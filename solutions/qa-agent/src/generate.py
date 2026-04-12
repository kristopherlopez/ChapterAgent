"""Answer generation — grounded answers with citations using OpenAI SDK."""

from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel, Field

try:
    from solutions.qa_agent.src.retrieve import RetrievedChunk
except ImportError:
    from retrieve import RetrievedChunk  # type: ignore[no-redef]

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


class QAGenerator:
    """Generates grounded answers with citations using OpenAI SDK.

    Usage:
        generator = QAGenerator()
        response = generator.generate("What was CBA's NIM?", chunks)
    """

    def __init__(self, *, model: str = "gpt-4o", temperature: float = 0.1):
        self.model = model
        self.temperature = temperature

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks as numbered context blocks."""
        blocks = []
        for i, chunk in enumerate(chunks, 1):
            blocks.append(
                f"[Context {i}] (p.{chunk.page}, {chunk.section})\n{chunk.text}"
            )
        return "\n\n".join(blocks)

    def _extract_citations(self, chunks: list[RetrievedChunk]) -> list[Citation]:
        """Build citations from the chunks used."""
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

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        *,
        scope_level: int = 1,
        query_id: str = "",
    ) -> QAResponse:
        """Generate a grounded answer with citations.

        Calls OpenAI with the retrieved context and returns a structured response.
        Falls back to a refusal if no context is available.
        """
        if not chunks:
            return QAResponse(
                query_id=query_id,
                question=question,
                answer=AnswerPayload(
                    text="I cannot find this information in the Annual Report.",
                    scope_level_used=scope_level,
                    grounding="none",
                ),
            )

        context = self._build_context(chunks)
        system_message = SYSTEM_PROMPT.format(context=context)

        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
                ],
            )
            answer_text = response.choices[0].message.content or ""
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            }
        except Exception as e:
            # Fallback: generate answer from context without LLM
            answer_text = self._fallback_answer(question, chunks)
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
                "framework": "openai-sdk",
                "model": self.model,
                "retrieval_strategy": "hybrid",
                "chunks_retrieved": len(chunks),
                "chunks_used": len(citations),
                "token_usage": token_usage,
            },
        )

    @staticmethod
    def _fallback_answer(question: str, chunks: list[RetrievedChunk]) -> str:
        """Simple fallback: return the most relevant chunk text with citation."""
        if not chunks:
            return "I cannot find this information in the Annual Report."
        top = chunks[0]
        return (
            f"{top.text}\n\n"
            f"*Source: CBA Annual Report 2025, p.{top.page} — {top.section}*"
        )
