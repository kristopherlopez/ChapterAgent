"""Answer generation — OpenAI Agents SDK with agentic retrieval.

The agent has access to tools (list_pages, read_page, cite_source) and
decides which pages to read from the Annual Report. Same agentic pattern
as the Claude generator — no pre-supplied context.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents import Agent, Runner, function_tool  # pip install openai-agents
from agents.items import ReasoningItem
from retrieve import RetrievedChunk
from schema import (
    AGENT_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    AnswerPayload,
    BaseGenerator,
    Citation,
    QAResponse,
)


class OpenAIGenerator(BaseGenerator):
    """Agentic Q&A using the OpenAI Agents SDK.

    Gives the agent three tools via @function_tool:
        - list_pages: table of contents of the Annual Report
        - read_page: read a full markdown page
        - cite_source: record a citation for a claim

    The agent decides which pages to read, reads them in full,
    and answers with precise citations. Same agentic pattern as
    ClaudeGenerator — the platform governs both identically.

    Falls back to context-in-prompt when markdown pages are unavailable.

    Usage:
        generator = OpenAIGenerator()
        response = generator.generate("What was CBA's NIM?", chunks)
    """

    framework = "openai-agents-sdk"

    def __init__(
        self,
        *,
        model: str = "gpt-4o",
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
            return self._context_fallback(question, chunks, scope_level, query_id)

        return self._agentic_generate(question, chunks, scope_level, query_id)

    def _agentic_generate(
        self, question: str, chunks: list[RetrievedChunk],
        scope_level: int, query_id: str,
    ) -> QAResponse:
        """Run the agent with full page access tools."""
        pages_dir = self._get_pages_dir()
        page_index = self._get_page_index()
        citations: list[Citation] = []

        try:
            @function_tool
            def list_pages() -> str:
                """List all pages in the CBA Annual Report with page numbers and section titles."""
                toc_lines = [
                    f"p.{entry['page']:>3}  {entry['title']:<60}  [{entry['file']}]"
                    for entry in page_index
                ]
                return "\n".join(toc_lines)

            @function_tool
            def read_page(filename: str) -> str:
                """Read a full page from the CBA Annual Report by filename."""
                page_path = pages_dir / filename
                if not page_path.exists():
                    return json.dumps({"error": f"Page not found: {filename}"})
                try:
                    content = page_path.read_text(encoding="utf-8", errors="replace")
                    if len(content) > 15000:
                        content = content[:15000] + "\n\n[... page truncated]"
                    return content
                except Exception as e:
                    return json.dumps({"error": str(e)})

            @function_tool
            def cite_source(page: int, section: str, quote: str) -> str:
                """Record a citation for a factual claim in your answer."""
                citations.append(Citation(page=page, section=section, quote=quote))
                return f"Citation recorded: p.{page}, {section}"

            agent = Agent(
                name="CBA Annual Report Q&A",
                instructions=AGENT_SYSTEM_PROMPT,
                model=self.model,
                tools=[list_pages, read_page, cite_source],
            )

            result = Runner.run_sync(agent, question, max_turns=self.max_turns)
            answer_text = result.final_output or ""

            # Extract thinking from agent activity (tool calls + reasoning)
            thinking = []
            for item in result.to_input_list():
                if isinstance(item, dict):
                    item_type = item.get("type", "")
                    if item_type == "reasoning":
                        for s in item.get("summary", []):
                            if isinstance(s, dict) and s.get("text"):
                                thinking.append(s["text"])
                    elif item_type == "function_call":
                        name = item.get("name", "")
                        args = item.get("arguments", "")
                        if name == "list_pages":
                            thinking.append("Browsing Annual Report table of contents")
                        elif name == "read_page":
                            try:
                                import json as _json
                                a = _json.loads(args) if isinstance(args, str) else args
                                fname = a.get("filename", "")
                                thinking.append(f"Reading {fname.replace('.md', '').replace('-', ' ')}")
                            except Exception:
                                thinking.append("Reading a page from the Annual Report")
                        elif name == "cite_source":
                            try:
                                import json as _json
                                a = _json.loads(args) if isinstance(args, str) else args
                                thinking.append(f"Citing p.{a.get('page', '?')} — {a.get('section', '')}")
                            except Exception:
                                thinking.append("Recording a citation")

            token_usage = {}
            if hasattr(result, "raw_responses") and result.raw_responses:
                last = result.raw_responses[-1]
                if hasattr(last, "usage") and last.usage:
                    token_usage = {
                        "input_tokens": last.usage.input_tokens,
                        "output_tokens": last.usage.output_tokens,
                        "total_tokens": last.usage.total_tokens,
                    }

        except Exception as e:
            answer_text = self.fallback_answer(chunks)
            citations = self.extract_citations(chunks)
            thinking = []
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
            ),
        )

    def _context_fallback(
        self, question: str, chunks: list[RetrievedChunk],
        scope_level: int, query_id: str,
    ) -> QAResponse:
        """Fall back to context-in-prompt when pages aren't available."""
        context = self.build_context(chunks)
        instructions = SYSTEM_PROMPT.format(context=context)
        citations = self.extract_citations(chunks)

        try:
            collected_citations: list[dict] = []

            @function_tool
            def cite_source(page: int, section: str, quote: str) -> str:
                """Record a citation for a factual claim."""
                collected_citations.append({"page": page, "section": section, "quote": quote})
                return f"Citation recorded: p.{page}, {section}"

            agent = Agent(
                name="CBA Annual Report Q&A",
                instructions=instructions,
                model=self.model,
                tools=[cite_source],
            )

            result = Runner.run_sync(agent, question, max_turns=5)
            answer_text = result.final_output or ""

            if collected_citations:
                citations = [
                    Citation(page=c["page"], section=c["section"], quote=c["quote"])
                    for c in collected_citations
                ]

            token_usage = {}
            if hasattr(result, "raw_responses") and result.raw_responses:
                last = result.raw_responses[-1]
                if hasattr(last, "usage") and last.usage:
                    token_usage = {
                        "input_tokens": last.usage.input_tokens,
                        "output_tokens": last.usage.output_tokens,
                        "total_tokens": last.usage.total_tokens,
                    }

        except Exception as e:
            answer_text = self.fallback_answer(chunks)
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
                chunks=chunks, citations=citations, token_usage=token_usage,
            ),
        )
