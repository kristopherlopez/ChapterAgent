"""Answer generation — Claude Agent SDK.

Uses the Anthropic SDK with tool use: Claude reads full markdown pages
from the Annual Report corpus, deciding what to read and how to cite.

Two modes:
    - **agentic**: Claude with tools (list_pages, read_page, cite_source)
    - **direct**: Anthropic SDK direct call (context in system prompt)

The agentic mode gives Claude access to the full document corpus as
individual pages. Claude reads the table of contents, decides which
pages are relevant, reads them in full, and answers with citations.
No pre-retrieval or chunking — Claude controls the search loop.

Usage:
    generator = ClaudeAgentGenerator(pages_dir=Path("knowledge_base/markdown"))
    response = generator.generate("What was CBA's NIM?", chunks)
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel

try:
    from solutions.qa_agent.src.generate import (
        SYSTEM_PROMPT,
        AnswerPayload,
        Citation,
        QAResponse,
    )
    from solutions.qa_agent.src.retrieve import RetrievedChunk
except ImportError:
    from generate import (  # type: ignore[no-redef]
        SYSTEM_PROMPT,
        AnswerPayload,
        Citation,
        QAResponse,
    )
    from retrieve import RetrievedChunk  # type: ignore[no-redef]


def _build_page_index(pages_dir: Path) -> list[dict[str, Any]]:
    """Build a table of contents from the markdown pages directory.

    Returns a list of {file, page_number, title} sorted by page number.
    """
    index = []
    for md_file in sorted(pages_dir.glob("*.md")):
        name = md_file.stem

        # Extract page number from filename (e.g. "13-delivering-financial-performance")
        match = re.match(r"(\d+)", name)
        page_num = int(match.group(1)) if match else 0

        # Extract title: use the rest of the filename, cleaned up
        title_part = re.sub(r"^\d+-?", "", name).replace("-", " ").strip()
        if not title_part:
            # Read the first heading from the file
            try:
                text = md_file.read_text(encoding="utf-8", errors="replace")
                heading = next(
                    (line.lstrip("#").strip() for line in text.split("\n")
                     if line.startswith("#")),
                    name,
                )
                title_part = heading[:80]
            except Exception:
                title_part = name

        index.append({
            "file": md_file.name,
            "page": page_num,
            "title": title_part.title() if title_part else name,
        })

    return index


# ---------------------------------------------------------------------------
# Claude Agent SDK — agentic tool-use implementation
# ---------------------------------------------------------------------------

AGENT_SYSTEM_PROMPT = """You are a Q&A agent for CBA's 2025 Annual Report. You answer questions by reading the actual report pages.

You have access to tools:
- **list_pages**: shows the table of contents — page numbers and section titles.
- **read_page**: reads a full page from the report by its filename.
- **cite_source**: records a citation for a factual claim in your answer.

WORKFLOW:
1. Call list_pages to see what's available.
2. Based on the question, decide which pages are likely relevant.
3. Call read_page to read those pages in full.
4. If you need more context, read additional pages.
5. Answer the question based on what you've read.
6. Call cite_source for EVERY factual claim.

RULES:
1. Answer ONLY from the pages you've read. Do not use prior knowledge.
2. Cite EVERY factual claim with cite_source.
3. If you can't find the information after reading relevant pages, say so.
4. Never provide financial advice, opinions, or recommendations.
5. Be precise with numbers — do not round or approximate.
6. Include the reporting period (e.g., "FY2025") when referencing figures.
"""


class ClaudeAgentGenerator:
    """Agentic Q&A using the Claude Agent SDK.

    Gives the agent three tools via @tool decorator:
        - list_pages: table of contents of the Annual Report
        - read_page: read a full markdown page
        - cite_source: record a citation for a claim

    The agent decides which pages to read, reads them in full (not
    truncated chunks), and answers with precise citations.

    Usage:
        from claude_agent_sdk import query, ClaudeAgentOptions
        generator = ClaudeAgentGenerator(pages_dir=Path("knowledge_base/markdown"))
        response = generator.generate("What was CBA's NIM?", chunks)
    """

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
        """Resolve the pages directory."""
        if self._pages_dir:
            return self._pages_dir
        return (
            Path(__file__).parent.parent / "knowledge_base" / "markdown"
        )

    def _get_page_index(self) -> list[dict]:
        """Lazy-load the page index."""
        if self._page_index is None:
            self._page_index = _build_page_index(self._get_pages_dir())
        return self._page_index

    def _build_tools(self, citations: list[Citation]) -> list:
        """Build SDK tools with closures over pages_dir and citations."""
        from claude_agent_sdk import tool
        from pydantic import BaseModel as PydanticBaseModel

        pages_dir = self._get_pages_dir()
        page_index = self._get_page_index()

        class EmptyInput(PydanticBaseModel):
            pass

        @tool(
            name="list_pages",
            description=(
                "List all pages in the CBA Annual Report with page "
                "numbers and section titles. Use this first to find "
                "which pages are relevant to the question."
            ),
            input_schema=EmptyInput,
        )
        async def list_pages(input: EmptyInput) -> dict:
            toc_lines = [
                f"p.{entry['page']:>3}  {entry['title']:<60}  [{entry['file']}]"
                for entry in page_index
            ]
            return {"content": "\n".join(toc_lines)}

        class ReadPageInput(PydanticBaseModel):
            filename: str

        @tool(
            name="read_page",
            description=(
                "Read a full page from the CBA Annual Report. "
                "Returns the complete markdown content of that page. "
                "Use the filename from list_pages."
            ),
            input_schema=ReadPageInput,
        )
        async def read_page(input: ReadPageInput) -> dict:
            page_path = pages_dir / input.filename
            if not page_path.exists():
                return {"error": f"Page not found: {input.filename}"}
            try:
                content = page_path.read_text(
                    encoding="utf-8", errors="replace",
                )
                if len(content) > 15000:
                    content = content[:15000] + "\n\n[... page truncated]"
                return {"content": content}
            except Exception as e:
                return {"error": str(e)}

        class CiteSourceInput(PydanticBaseModel):
            page: int
            section: str
            quote: str

        @tool(
            name="cite_source",
            description=(
                "Record a citation for a factual claim in your "
                "answer. Call this for every fact you cite."
            ),
            input_schema=CiteSourceInput,
        )
        async def cite_source(input: CiteSourceInput) -> dict:
            citations.append(
                Citation(
                    page=input.page,
                    section=input.section,
                    quote=input.quote,
                )
            )
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
        """Generate answer using the Claude Agent SDK.

        The chunks parameter is accepted for interface compatibility but
        the agent reads full pages instead of using pre-retrieved chunks.
        """
        import anyio

        pages_dir = self._get_pages_dir()

        if not pages_dir.exists() or not any(pages_dir.glob("*.md")):
            # Fall back to chunk-based answer if no pages available
            return self._chunk_fallback(question, chunks, scope_level, query_id)

        citations: list[Citation] = []
        sdk_tools = self._build_tools(citations)

        try:
            answer_text, token_usage = anyio.from_thread.run(
                self._run_agent, question, sdk_tools,
            )
        except Exception as e:
            # Fallback to chunk-based answer
            answer_text = self._fallback_answer(chunks)
            citations = self._extract_citations(chunks)
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
            metadata={
                "framework": "claude-agent-sdk",
                "model": self.model,
                "retrieval_strategy": "agentic_full_page",
                "pages_available": len(self._get_page_index()),
                "chunks_retrieved": len(chunks),
                "token_usage": token_usage,
            },
        )

    async def _run_agent(
        self, question: str, sdk_tools: list,
    ) -> tuple[str, dict]:
        """Run the Claude Agent SDK query loop."""
        from claude_agent_sdk import query, ClaudeAgentOptions

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

    def _chunk_fallback(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        scope_level: int,
        query_id: str,
    ) -> QAResponse:
        """Fall back to chunk-based direct call when pages aren't available."""
        if not chunks:
            return QAResponse(
                query_id=query_id,
                question=question,
                answer=AnswerPayload(
                    text="Knowledge base pages not found.",
                    scope_level_used=scope_level,
                    grounding="none",
                ),
            )

        context = "\n\n".join(
            f"[Context {i}] (p.{c.page}, {c.section})\n{c.text}"
            for i, c in enumerate(chunks, 1)
        )
        system_message = SYSTEM_PROMPT.format(context=context)

        try:
            import anthropic

            client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.1,
                system=system_message,
                messages=[{"role": "user", "content": question}],
            )
            answer_text = response.content[0].text
        except Exception:
            answer_text = self._fallback_answer(chunks)

        return QAResponse(
            query_id=query_id,
            question=question,
            answer=AnswerPayload(
                text=answer_text,
                scope_level_used=scope_level,
                grounding="corpus",
            ),
            citations=self._extract_citations(chunks),
            metadata={"framework": "claude-agent-sdk", "model": self.model},
        )

    @staticmethod
    def _extract_citations(
        chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        seen = set()
        citations = []
        for chunk in chunks[:3]:
            key = (chunk.page, chunk.section)
            if key not in seen:
                seen.add(key)
                citations.append(
                    Citation(
                        page=chunk.page,
                        section=chunk.section,
                        quote=chunk.text[:200],
                    )
                )
        return citations

    @staticmethod
    def _fallback_answer(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return (
                "I cannot find this information "
                "in the Annual Report."
            )
        top = chunks[0]
        return (
            f"{top.text}\n\n"
            f"*Source: CBA Annual Report 2025, "
            f"p.{top.page} — {top.section}*"
        )


# Default export — agentic version
ClaudeQAGenerator = ClaudeAgentGenerator
