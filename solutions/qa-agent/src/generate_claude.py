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
    """Agentic Q&A using Claude with full page access.

    Gives Claude three tools:
        - list_pages: table of contents of the Annual Report
        - read_page: read a full markdown page
        - cite_source: record a citation for a claim

    Claude decides which pages to read, reads them in full (not
    truncated chunks), and answers with precise citations.
    """

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.1,
        max_tokens: int = 2048,
        pages_dir: Path | None = None,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._pages_dir = pages_dir
        self._page_index: list[dict] | None = None

    def _get_pages_dir(self, chunks: list[RetrievedChunk] | None = None) -> Path:
        """Resolve the pages directory."""
        if self._pages_dir:
            return self._pages_dir
        # Default: infer from project structure
        return (
            Path(__file__).parent.parent / "knowledge_base" / "markdown"
        )

    def _get_page_index(self) -> list[dict]:
        """Lazy-load the page index."""
        if self._page_index is None:
            self._page_index = _build_page_index(self._get_pages_dir())
        return self._page_index

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        *,
        scope_level: int = 1,
        query_id: str = "",
    ) -> QAResponse:
        """Generate answer using Claude with full page access.

        The chunks parameter is accepted for interface compatibility but
        the agent reads full pages instead of using pre-retrieved chunks.
        """
        pages_dir = self._get_pages_dir()

        if not pages_dir.exists() or not any(pages_dir.glob("*.md")):
            return QAResponse(
                query_id=query_id,
                question=question,
                answer=AnswerPayload(
                    text="Knowledge base pages not found.",
                    scope_level_used=scope_level,
                    grounding="none",
                ),
            )

        tools = self._build_tools()

        try:
            import anthropic

            client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )

            answer_text, citations, token_usage, pages_read = (
                self._run_agent_loop(
                    client, question, tools, pages_dir,
                )
            )

        except Exception as e:
            # Fallback to chunk-based answer
            answer_text = self._fallback_answer(chunks)
            citations = self._extract_citations(chunks)
            token_usage = {"error": str(e)}
            pages_read = 0

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
                "pages_read": pages_read,
                "chunks_retrieved": len(chunks),
                "token_usage": token_usage,
            },
        )

    def _build_tools(self) -> list[dict]:
        """Build tool definitions for Claude."""
        return [
            {
                "name": "list_pages",
                "description": (
                    "List all pages in the CBA Annual Report with page "
                    "numbers and section titles. Use this first to find "
                    "which pages are relevant to the question."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "read_page",
                "description": (
                    "Read a full page from the CBA Annual Report. "
                    "Returns the complete markdown content of that page. "
                    "Use the filename from list_pages."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": (
                                "The filename of the page to read "
                                "(e.g. '13-delivering-financial-performance.md')"
                            ),
                        },
                    },
                    "required": ["filename"],
                },
            },
            {
                "name": "cite_source",
                "description": (
                    "Record a citation for a factual claim in your "
                    "answer. Call this for every fact you cite."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "Page number in the report",
                        },
                        "section": {
                            "type": "string",
                            "description": "Section title",
                        },
                        "quote": {
                            "type": "string",
                            "description": (
                                "The relevant quote or fact being cited"
                            ),
                        },
                    },
                    "required": ["page", "section", "quote"],
                },
            },
        ]

    def _run_agent_loop(
        self,
        client,
        question: str,
        tools: list[dict],
        pages_dir: Path,
    ) -> tuple[str, list[Citation], dict, int]:
        """Run the Claude agent loop with tool use."""
        messages = [{"role": "user", "content": question}]
        citations: list[Citation] = []
        total_input = 0
        total_output = 0
        pages_read = 0
        max_iterations = 10

        for iteration in range(max_iterations):
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=AGENT_SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )

            if response.usage:
                total_input += response.usage.input_tokens
                total_output += response.usage.output_tokens

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result, did_read = self._handle_tool_call(
                            block.name,
                            block.input,
                            pages_dir,
                            citations,
                        )
                        if did_read:
                            pages_read += 1
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                messages.append({
                    "role": "assistant",
                    "content": response.content,
                })
                messages.append({
                    "role": "user",
                    "content": tool_results,
                })
            else:
                # Claude is done — extract final answer
                answer_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        answer_text += block.text
                break
        else:
            answer_text = (
                "I was unable to complete the search within the "
                "iteration limit."
            )

        token_usage = {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "agent_iterations": iteration + 1,
            "pages_read": pages_read,
        }

        return answer_text, citations, token_usage, pages_read

    def _handle_tool_call(
        self,
        tool_name: str,
        tool_input: dict,
        pages_dir: Path,
        citations: list[Citation],
    ) -> tuple[str, bool]:
        """Handle a tool call from Claude. Returns (result, did_read_page)."""
        if tool_name == "list_pages":
            index = self._get_page_index()
            # Format as a concise table of contents
            toc_lines = [
                f"p.{entry['page']:>3}  {entry['title']:<60}  [{entry['file']}]"
                for entry in index
            ]
            return "\n".join(toc_lines), False

        elif tool_name == "read_page":
            filename = tool_input.get("filename", "")
            page_path = pages_dir / filename
            if not page_path.exists():
                return json.dumps({
                    "error": f"Page not found: {filename}",
                }), False
            try:
                content = page_path.read_text(
                    encoding="utf-8", errors="replace",
                )
                # Truncate very large pages to stay within context
                if len(content) > 15000:
                    content = content[:15000] + "\n\n[... page truncated]"
                return content, True
            except Exception as e:
                return json.dumps({"error": str(e)}), False

        elif tool_name == "cite_source":
            citation = Citation(
                page=tool_input.get("page", 0),
                section=tool_input.get("section", ""),
                quote=tool_input.get("quote", ""),
            )
            citations.append(citation)
            return json.dumps({"status": "citation recorded"}), False

        return json.dumps({"error": f"Unknown tool: {tool_name}"}), False

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


# ---------------------------------------------------------------------------
# Direct Anthropic SDK — simple call, no tool use
# ---------------------------------------------------------------------------

class ClaudeDirectGenerator:
    """Simple Claude generation without tool use.

    Same as the OpenAI generator pattern — sends context in the
    system prompt and gets back an answer. No agent loop.
    """

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        *,
        scope_level: int = 1,
        query_id: str = "",
    ) -> QAResponse:
        """Generate answer with a direct Claude call."""
        if not chunks:
            return QAResponse(
                query_id=query_id,
                question=question,
                answer=AnswerPayload(
                    text="I cannot find this information "
                    "in the Annual Report.",
                    scope_level_used=scope_level,
                    grounding="none",
                ),
            )

        context = self._build_context(chunks)
        system_message = SYSTEM_PROMPT.format(context=context)

        try:
            import anthropic

            client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_message,
                messages=[
                    {"role": "user", "content": question},
                ],
            )
            answer_text = response.content[0].text
            token_usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        except Exception as e:
            answer_text = self._fallback_answer(chunks)
            token_usage = {"error": str(e)}

        citations = self._extract_citations(chunks)

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
                "framework": "claude-direct",
                "model": self.model,
                "retrieval_strategy": "hybrid",
                "chunks_retrieved": len(chunks),
                "chunks_used": len(citations),
                "token_usage": token_usage,
            },
        )

    @staticmethod
    def _build_context(chunks: list[RetrievedChunk]) -> str:
        blocks = []
        for i, chunk in enumerate(chunks, 1):
            blocks.append(
                f"[Context {i}] (p.{chunk.page}, {chunk.section})\n"
                f"{chunk.text}"
            )
        return "\n\n".join(blocks)

    @staticmethod
    def _extract_citations(
        chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        seen = set()
        citations = []
        for chunk in chunks:
            key = (chunk.page, chunk.section)
            if key not in seen:
                seen.add(key)
                citations.append(
                    Citation(
                        page=chunk.page,
                        section=chunk.section,
                        quote=chunk.text[:200] + (
                            "..." if len(chunk.text) > 200 else ""
                        ),
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
