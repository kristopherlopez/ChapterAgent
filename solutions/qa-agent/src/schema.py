"""Shared types, constants, and base class for Q&A agent generators."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from retrieve import RetrievedChunk


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a Q&A agent for CBA's 2025 Annual Report. You answer questions based ONLY on the provided document context.

RULES:
1. Answer ONLY from the provided context. Do not use prior knowledge.
2. Write your own synthesis — never copy-paste context verbatim.
3. If the context does not contain enough information, say: "I cannot find this information in the Annual Report."
4. Never provide financial advice, opinions, or recommendations.
5. When referencing figures, include the reporting period (e.g., "FY2024").
6. Be precise with numbers — do not round or approximate.

CITATION FORMAT (you MUST follow this exactly):
- Place a superscript footnote marker [^1^], [^2^], etc. after each factual claim.
- At the end of your answer, list ALL sources on separate lines.
- Do NOT use any other citation format.

Example:
CBA's net interest margin was 2.08% in FY2025[^1^]. The dividend payout ratio was 79%[^2^].

[^1^]: CBA Annual Report 2025, p.3 — 2025 Highlights
[^2^]: CBA Annual Report 2025, p.12 — Delivering Financial Performance

CONTEXT:
{context}
"""

AGENT_SYSTEM_PROMPT = """You are a Q&A agent for CBA's 2025 Annual Report. You answer questions by reading the actual report pages.

You have access to tools:
- **list_pages**: shows the table of contents — page numbers and section titles.
- **read_page**: reads a full page from the report by its filename.
- **cite_source**: records a citation for a factual claim in your answer.

WORKFLOW:
1. Call list_pages to see what's available.
2. Based on the question, decide which pages are likely relevant. If multiple pages share a similar title, read the earliest one first — summary/highlights pages appear early and contain the key figures.
3. Call read_page to read those pages in full.
4. If the page you read doesn't contain the specific figure or fact asked about, read additional pages.
5. Call cite_source for EVERY source page you reference.
6. Write your answer in your own words, synthesizing across the pages you've read.

RULES:
1. Answer ONLY from the pages you've read. Do not use prior knowledge.
2. Write your own synthesis — NEVER copy-paste page content verbatim. Extract the key facts and present them clearly.
3. Your answer MUST include the specific numbers, percentages, and figures from the report. Do not just describe trends — state the actual values. Lead with the direct answer before adding context.
4. Call cite_source for EVERY source page BEFORE writing your final answer.
5. If you can't find the information after reading relevant pages, say so.
6. Never provide financial advice, opinions, or recommendations.
7. Be precise with numbers — do not round or approximate.
8. Include the reporting period (e.g., "FY2025") when referencing figures.

CITATION FORMAT (you MUST follow this exactly):
- Place a superscript footnote marker [^1^], [^2^], etc. after each factual claim in your answer.
- At the end of your answer, list ALL sources on separate lines.
- Do NOT use any other citation format. No "*Source:...*", no "[Source:...]", no inline citations.

Example answer:
CBA's net interest margin was 2.08% in FY2025[^1^], with operating income of $28,465 million[^1^]. The dividend payout ratio was 79%[^2^].

[^1^]: CBA Annual Report 2025, p.3 — 2025 Highlights
[^2^]: CBA Annual Report 2025, p.12 — Delivering Financial Performance
"""


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class Citation(BaseModel):
    """A source citation for a claim in the answer."""
    document: str = "CBA Annual Report 2025"
    page: int
    section: str
    quote: str = ""


class AnswerPayload(BaseModel):
    """The generated answer with grounding information."""
    text: str
    scope_level_used: int = 1
    grounding: str = "corpus"


class QAResponse(BaseModel):
    """Full structured response from the Q&A agent."""
    query_id: str = ""
    question: str
    answer: AnswerPayload
    citations: list[Citation] = Field(default_factory=list)
    thinking: list[str] = Field(default_factory=list)
    guardrail_results: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Base generator
# ---------------------------------------------------------------------------

class BaseGenerator(ABC):
    """Abstract base for all Q&A generators.

    Provides shared helpers for context formatting, citation extraction,
    and fallback answers. Subclasses implement `generate()` with their
    framework-specific logic.
    """

    framework: str = ""
    model: str = ""

    @abstractmethod
    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        *,
        scope_level: int = 1,
        query_id: str = "",
    ) -> QAResponse:
        """Generate a grounded answer with citations."""
        ...

    @staticmethod
    def build_context(chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks as numbered context blocks."""
        blocks = []
        for i, chunk in enumerate(chunks, 1):
            blocks.append(
                f"[Context {i}] (p.{chunk.page}, {chunk.section})\n{chunk.text}"
            )
        return "\n\n".join(blocks)

    @staticmethod
    def extract_citations(chunks: list[RetrievedChunk]) -> list[Citation]:
        """Build deduplicated citations from retrieved chunks."""
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
                        quote=chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""),
                    )
                )
        return citations

    @staticmethod
    def fallback_answer(chunks: list[RetrievedChunk]) -> str:
        """Simple fallback: return the most relevant chunk text with citation."""
        if not chunks:
            return "I cannot find this information in the Annual Report."
        top = chunks[0]
        return (
            f"{top.text}\n\n"
            f"*Source: CBA Annual Report 2025, p.{top.page} — {top.section}*"
        )

    @staticmethod
    def format_answer_with_footnotes(text: str, citations: list[Citation]) -> str:
        """Normalize answer text to use footnote citations.

        If the model already used [^1^] footnotes, return as-is.
        Otherwise, strip inline *Source:...* markers and append a
        footnote block built from the structured citations list.
        """
        if not citations:
            return text
        # Already has footnotes — leave alone
        if "[^" in text:
            return text
        # Strip inline *Source:...* or [Source:...] markers
        clean = re.sub(r'\n*\*Source:.*?\*\s*$', '', text, flags=re.DOTALL).strip()
        clean = re.sub(r'\[Source:[^\]]*\]', '', clean).strip()
        # Strip leading markdown headings (## **Title**) — these are raw page dumps
        clean = re.sub(r'^#{1,3}\s+\*{0,2}[^*\n]+\*{0,2}\s*\n?', '', clean).strip()
        # Build footnote block from structured citations
        # Deduplicate by (page, section)
        seen: set[tuple[int, str]] = set()
        unique: list[Citation] = []
        for c in citations:
            key = (c.page, c.section)
            if key not in seen:
                seen.add(key)
                unique.append(c)
        footnotes = "\n".join(
            f"[^{i}^]: {c.document}, p.{c.page} — {c.section}"
            for i, c in enumerate(unique, 1)
        )
        return f"{clean}\n\n{footnotes}"

    def empty_response(
        self, question: str, scope_level: int, query_id: str,
    ) -> QAResponse:
        """Return a standard empty response when no chunks are available."""
        return QAResponse(
            query_id=query_id,
            question=question,
            answer=AnswerPayload(
                text="I cannot find this information in the Annual Report.",
                scope_level_used=scope_level,
                grounding="none",
            ),
        )

    def build_metadata(
        self,
        *,
        chunks: list[RetrievedChunk],
        citations: list[Citation],
        token_usage: dict,
        **extra: Any,
    ) -> dict[str, Any]:
        """Build a standardised metadata dict."""
        meta: dict[str, Any] = {
            "framework": self.framework,
            "model": self.model,
            "retrieval_strategy": extra.get("retrieval_strategy", "hybrid"),
            "chunks_retrieved": len(chunks),
            "chunks_used": len(citations),
            "token_usage": token_usage,
        }
        meta.update({k: v for k, v in extra.items() if k != "retrieval_strategy"})
        return meta

    @staticmethod
    def build_page_index(pages_dir: Path) -> list[dict[str, Any]]:
        """Build a table of contents from the markdown pages directory.

        Returns a list of {file, page, title} sorted by page number.
        Used by agentic generators that give the LLM full page access.
        """
        index = []
        for md_file in sorted(pages_dir.glob("*.md")):
            name = md_file.stem
            match = re.match(r"(\d+)", name)
            page_num = int(match.group(1)) if match else 0
            title_part = re.sub(r"^\d+-?", "", name).replace("-", " ").strip()
            if not title_part:
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
