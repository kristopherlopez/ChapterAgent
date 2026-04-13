"""Answer generation — LangChain / LangGraph."""

from __future__ import annotations

import os
from typing import Any

from retrieve import RetrievedChunk
from schema import (
    SYSTEM_PROMPT,
    AnswerPayload,
    Citation,
    QAResponse,
)


class LangChainQAGenerator:
    """Generates grounded answers with citations using LangChain.

    Uses ChatOpenAI (or any LangChain-compatible LLM) with the same
    system prompt and response format as the other generators.

    Usage:
        generator = LangChainQAGenerator()
        response = generator.generate("What was CBA's NIM?", chunks)
    """

    def __init__(
        self,
        *,
        model: str | None = None,
        temperature: float = 0.1,
        provider: str = "openrouter",
    ):
        self.model = model
        self.temperature = temperature
        self.provider = provider

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        blocks = []
        for i, chunk in enumerate(chunks, 1):
            blocks.append(
                f"[Context {i}] (p.{chunk.page}, {chunk.section})\n"
                f"{chunk.text}"
            )
        return "\n\n".join(blocks)

    def _extract_citations(
        self, chunks: list[RetrievedChunk],
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

    def _get_llm(self):
        """Create the LangChain LLM based on provider.

        Default provider is OpenRouter, which supports any model via
        the OpenAI-compatible API at openrouter.ai.
        """
        if self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=self.model or "claude-sonnet-4-20250514",
                temperature=self.temperature,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        elif self.provider == "openrouter":
            from langchain_openai import ChatOpenAI

            model = self.model or os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-preview")
            return ChatOpenAI(
                model=model,
                temperature=self.temperature,
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
        else:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=self.model or "gpt-4o",
                temperature=self.temperature,
                api_key=os.getenv("OPENAI_API_KEY"),
            )

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        *,
        scope_level: int = 1,
        query_id: str = "",
    ) -> QAResponse:
        """Generate a grounded answer using LangChain."""
        if not chunks:
            return QAResponse(
                query_id=query_id,
                question=question,
                answer=AnswerPayload(
                    text="I cannot find this information in the "
                    "Annual Report.",
                    scope_level_used=scope_level,
                    grounding="none",
                ),
            )

        context = self._build_context(chunks)
        system_message = SYSTEM_PROMPT.format(context=context)

        try:
            from langchain_core.messages import (
                HumanMessage,
                SystemMessage,
            )

            llm = self._get_llm()
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=question),
            ]
            response = llm.invoke(messages)
            answer_text = response.content
            token_usage = {}
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                token_usage = dict(response.usage_metadata)
            elif hasattr(response, "response_metadata"):
                meta = response.response_metadata or {}
                token_usage = meta.get("token_usage", {})
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
                "framework": "langchain-langgraph",
                "model": self.model or os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-preview"),
                "provider": self.provider,
                "retrieval_strategy": "hybrid",
                "chunks_retrieved": len(chunks),
                "chunks_used": len(citations),
                "token_usage": token_usage,
            },
        )

    @staticmethod
    def _fallback_answer(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "I cannot find this information in the Annual Report."
        top = chunks[0]
        return (
            f"{top.text}\n\n"
            f"*Source: CBA Annual Report 2025, "
            f"p.{top.page} — {top.section}*"
        )
