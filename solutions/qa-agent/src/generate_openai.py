"""Answer generation — OpenAI Agents SDK with function tools."""

from __future__ import annotations

import os
from pathlib import Path

from retrieve import RetrievedChunk
from schema import (
    SYSTEM_PROMPT,
    AnswerPayload,
    Citation,
    QAResponse,
)


class QAGenerator:
    """Generates grounded answers using the OpenAI Agents SDK.

    Uses Agent with function_tool decorators for structured tool use.
    The agent receives retrieved context and can cite sources via tools.

    Usage:
        from agents import Agent, Runner, function_tool
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
        """Generate a grounded answer using the OpenAI Agents SDK.

        Creates an Agent with context-aware instructions and runs it
        synchronously via Runner.run_sync.
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
        instructions = SYSTEM_PROMPT.format(context=context)
        citations = self._extract_citations(chunks)

        try:
            from agents import Agent, Runner, function_tool

            # Define a citation tool the agent can call
            collected_citations: list[dict] = []

            @function_tool
            def cite_source(page: int, section: str, quote: str) -> str:
                """Record a citation for a factual claim. Call this for every fact you reference."""
                collected_citations.append({
                    "page": page,
                    "section": section,
                    "quote": quote,
                })
                return f"Citation recorded: p.{page}, {section}"

            agent = Agent(
                name="CBA Annual Report Q&A",
                instructions=instructions,
                model=self.model,
                tools=[cite_source],
            )

            result = Runner.run_sync(
                agent,
                question,
                max_turns=5,
            )

            answer_text = result.final_output or ""

            # Merge any agent-collected citations with chunk-based ones
            if collected_citations:
                citations = [
                    Citation(
                        page=c["page"],
                        section=c["section"],
                        quote=c["quote"],
                    )
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
            # Fallback: generate answer from context without LLM
            answer_text = self._fallback_answer(question, chunks)
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
                "framework": "openai-agents-sdk",
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
