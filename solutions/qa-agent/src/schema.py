"""Shared types and constants for Q&A agent generators."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from retrieve import RetrievedChunk

SYSTEM_PROMPT = """You are a Q&A agent for CBA's 2025 Annual Report. You answer questions based ONLY on the provided document context.

RULES:
1. Answer ONLY from the provided context. Do not use prior knowledge.
2. Cite EVERY factual claim with [Source: CBA Annual Report 2025, p.X, Section Name].
3. If the context does not contain enough information, say: "I cannot find this information in the Annual Report."
4. Never provide financial advice, opinions, or recommendations.
5. When referencing figures, include the reporting period (e.g., "FY2024").
6. Be precise with numbers — do not round or approximate.

CONTEXT:
{context}
"""


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
    guardrail_results: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
