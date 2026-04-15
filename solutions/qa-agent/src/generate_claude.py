"""Answer generation — Claude Agent SDK with agentic tool use."""

from __future__ import annotations

import json
import os
from pathlib import Path

import anthropic
import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    query,
    tool,
)
from pydantic import BaseModel

from retrieve import RetrievedChunk
from schema import (
    AGENT_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    AnswerPayload,
    BaseGenerator,
    Citation,
    QAResponse,
)


class ClaudeGenerator(BaseGenerator):
    """Agentic Q&A using the Claude Agent SDK.

    Gives the agent three tools via @tool decorator:
        - list_pages: table of contents of the governance policies
        - read_page: read a full markdown page
        - cite_source: record a citation for a claim

    Falls back to a direct Anthropic SDK call with chunk context
    when markdown pages are unavailable.

    Usage:
        generator = ClaudeGenerator()
        response = generator.generate("What is the PII handling policy?", chunks)
    """

    framework = "claude-agent-sdk"

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-20250514",
        max_turns: int = 10,
        pages_dir: Path | None = None,
    ):
        self.model = model
        self.max_turns = max_turns
        self._pages_dir = pages_dir
        self._page_index: list[dict] | None = None

    def _get_pages_dir(self) -> Path:
        if self._pages_dir:
            return self._pages_dir
        return Path(__file__).parent.parent / "knowledge_base" / "markdown"

    def _get_page_index(self) -> list[dict]:
        if self._page_index is None:
            self._page_index = self.build_page_index(self._get_pages_dir())
        return self._page_index

    def _build_tools(self, citations: list[Citation], pages_read: list[str]) -> list:
        """Build SDK tools with closures over pages_dir, citations, and pages_read."""
        pages_dir = self._get_pages_dir()
        page_index = self._get_page_index()

        class EmptyInput(BaseModel):
            pass

        @tool(
            name="list_pages",
            description="List all pages in the PetSure governance policies with page numbers and section titles.",
            input_schema=EmptyInput,
        )
        async def list_pages(input: EmptyInput) -> dict:
            toc_lines = [
                f"p.{entry['page']:>3}  {entry['title']:<60}  [{entry['file']}]"
                for entry in page_index
            ]
            return {"content": "\n".join(toc_lines)}

        class ReadPageInput(BaseModel):
            filename: str

        @tool(
            name="read_page",
            description="Read a full page from the PetSure governance policies by filename.",
            input_schema=ReadPageInput,
        )
        async def read_page(input: ReadPageInput) -> dict:
            page_path = pages_dir / input.filename
            if not page_path.exists():
                return {"error": f"Page not found: {input.filename}"}
            try:
                content = page_path.read_text(encoding="utf-8", errors="replace")
                if len(content) > 15000:
                    content = content[:15000] + "\n\n[... page truncated]"
                pages_read.append(content)
                return {"content": content}
            except Exception as e:
                return {"error": str(e)}

        class CiteSourceInput(BaseModel):
            page: int
            section: str
            quote: str

        @tool(
            name="cite_source",
            description="Record a citation for a factual claim in your answer.",
            input_schema=CiteSourceInput,
        )
        async def cite_source(input: CiteSourceInput) -> dict:
            citations.append(Citation(page=input.page, section=input.section, quote=input.quote))
            return {"status": "citation recorded"}

        return [list_pages, read_page, cite_source]

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        *,
        scope_level: int = 1,
        query_id: str = "",
    ) -> QAResponse:
        if not chunks:
            return self.empty_response(question, scope_level, query_id)

        pages_dir = self._get_pages_dir()
        has_pages = pages_dir.exists() and any(pages_dir.glob("*.md"))

        if not has_pages:
            return self._direct_fallback(question, chunks, scope_level, query_id)

        citations: list[Citation] = []
        thinking: list[str] = []
        pages_read: list[str] = []

        try:
            answer_text, token_usage, thinking = self._run_agent_direct(
                question, citations, pages_read,
            )
            if not answer_text or not answer_text.strip():
                answer_text = self.fallback_answer(chunks)
                citations = self.extract_citations(chunks)
        except Exception as e:
            answer_text = self.fallback_answer(chunks)
            citations = self.extract_citations(chunks)
            token_usage = {"error": str(e)}

        return QAResponse(
            query_id=query_id,
            question=question,
            answer=AnswerPayload(
                text=answer_text,
                scope_level_used=scope_level,
                grounding="corpus",
            ),
            citations=citations,
            thinking=thinking,
            metadata=self.build_metadata(
                chunks=chunks,
                citations=citations,
                token_usage=token_usage,
                retrieval_strategy="agentic_full_page",
                pages_available=len(self._get_page_index()),
                pages_read=pages_read,
            ),
        )

    def _run_agent_direct(
        self,
        question: str,
        citations: list[Citation],
        pages_read: list[str],
    ) -> tuple[str, dict, list[str]]:
        """Run agentic tool-use loop via the Anthropic API directly.

        This avoids the Claude Agent SDK CLI subprocess, which has issues
        with SDK MCP tool discovery on some platforms.
        """
        pages_dir = self._get_pages_dir()
        page_index = self._get_page_index()
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Define tools as Anthropic API tool schemas
        tools = [
            {
                "name": "list_pages",
                "description": "List all pages in the PetSure governance policies with page numbers and section titles.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "read_page",
                "description": "Read a full page from the PetSure governance policies by filename.",
                "input_schema": {
                    "type": "object",
                    "properties": {"filename": {"type": "string"}},
                    "required": ["filename"],
                },
            },
            {
                "name": "cite_source",
                "description": "Record a citation for a factual claim in your answer.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "page": {"type": "integer"},
                        "section": {"type": "string"},
                        "quote": {"type": "string"},
                    },
                    "required": ["page", "section", "quote"],
                },
            },
        ]

        def _handle_tool(name: str, args: dict) -> str:
            if name == "list_pages":
                return "\n".join(
                    f"p.{e['page']:>3}  {e['title']:<60}  [{e['file']}]"
                    for e in page_index
                )
            elif name == "read_page":
                page_path = pages_dir / args["filename"]
                if not page_path.exists():
                    return json.dumps({"error": f"Not found: {args['filename']}"})
                content = page_path.read_text(encoding="utf-8", errors="replace")
                content = content[:15000] if len(content) > 15000 else content
                pages_read.append(content)
                return content
            elif name == "cite_source":
                citations.append(Citation(
                    page=args["page"], section=args["section"], quote=args["quote"],
                ))
                return f"Citation recorded: p.{args['page']}"
            return json.dumps({"error": f"Unknown tool: {name}"})

        messages = [{"role": "user", "content": question}]
        thinking: list[str] = []
        token_usage: dict = {"input_tokens": 0, "output_tokens": 0}

        for _turn in range(self.max_turns):
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.1,
                system=AGENT_SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )
            token_usage["input_tokens"] += response.usage.input_tokens
            token_usage["output_tokens"] += response.usage.output_tokens

            # Collect thinking and text
            tool_uses = []
            answer_text = ""
            for block in response.content:
                if block.type == "text":
                    answer_text = block.text
                elif block.type == "tool_use":
                    tool_uses.append(block)
                elif block.type == "thinking" and hasattr(block, "thinking"):
                    thinking.append(block.thinking)

            # If no tool calls, we have the final answer
            if not tool_uses:
                return answer_text, token_usage, thinking

            # Process tool calls and continue
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for tu in tool_uses:
                result = _handle_tool(tu.name, tu.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": result,
                })
            messages.append({"role": "user", "content": tool_results})

        return answer_text, token_usage, thinking

    def _direct_fallback(
        self, question: str, chunks: list[RetrievedChunk],
        scope_level: int, query_id: str,
    ) -> QAResponse:
        """Fall back to direct Anthropic SDK call when pages aren't available."""
        context = self.build_context(chunks)
        system_message = SYSTEM_PROMPT.format(context=context)

        try:
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.1,
                system=system_message,
                messages=[{"role": "user", "content": question}],
            )
            answer_text = response.content[0].text
            token_usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        except Exception as e:
            answer_text = self.fallback_answer(chunks)
            token_usage = {"error": str(e)}

        citations = self.extract_citations(chunks)
        return QAResponse(
            query_id=query_id,
            question=question,
            answer=AnswerPayload(
                text=answer_text,
                scope_level_used=scope_level,
                grounding="corpus",
            ),
            citations=citations,
            metadata=self.build_metadata(
                chunks=chunks, citations=citations, token_usage=token_usage,
            ),
        )
