"""Answer generation — Claude Agent SDK with agentic tool use."""

from __future__ import annotations

import json
import os
from pathlib import Path

import anthropic
import anyio
from claude_agent_sdk import ClaudeAgentOptions, query, tool
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
        - list_pages: table of contents of the Annual Report
        - read_page: read a full markdown page
        - cite_source: record a citation for a claim

    Falls back to a direct Anthropic SDK call with chunk context
    when markdown pages are unavailable.

    Usage:
        generator = ClaudeGenerator()
        response = generator.generate("What was CBA's NIM?", chunks)
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

    def _build_tools(self, citations: list[Citation]) -> list:
        """Build SDK tools with closures over pages_dir and citations."""
        pages_dir = self._get_pages_dir()
        page_index = self._get_page_index()

        class EmptyInput(BaseModel):
            pass

        @tool(
            name="list_pages",
            description="List all pages in the CBA Annual Report with page numbers and section titles.",
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
            description="Read a full page from the CBA Annual Report by filename.",
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
        sdk_tools = self._build_tools(citations)

        try:
            answer_text, token_usage = anyio.from_thread.run(
                self._run_agent, question, sdk_tools,
            )
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
            metadata=self.build_metadata(
                chunks=chunks,
                citations=citations,
                token_usage=token_usage,
                retrieval_strategy="agentic_full_page",
                pages_available=len(self._get_page_index()),
            ),
        )

    async def _run_agent(self, question: str, sdk_tools: list) -> tuple[str, dict]:
        """Run the Claude Agent SDK query loop."""
        options = ClaudeAgentOptions(
            model=self.model,
            max_turns=self.max_turns,
            system_prompt=AGENT_SYSTEM_PROMPT,
            tools=sdk_tools,
            permission_mode="auto",
        )

        answer_text = ""
        token_usage: dict = {}

        async for message in query(prompt=question, options=options):
            if hasattr(message, "result") and message.result:
                answer_text = message.result
            if hasattr(message, "usage") and message.usage:
                token_usage = {
                    "input_tokens": getattr(message.usage, "input_tokens", 0),
                    "output_tokens": getattr(message.usage, "output_tokens", 0),
                }
            if hasattr(message, "total_cost_usd"):
                token_usage["cost_usd"] = message.total_cost_usd
            if hasattr(message, "num_turns"):
                token_usage["agent_turns"] = message.num_turns

        return answer_text, token_usage

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
