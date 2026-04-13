"""Answer generation — LangChain via OpenRouter."""

from __future__ import annotations

import os
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from retrieve import RetrievedChunk
from schema import (
    SYSTEM_PROMPT,
    AnswerPayload,
    BaseGenerator,
    Citation,
    QAResponse,
)


class LangChainGenerator(BaseGenerator):
    """Generates grounded answers using LangChain via OpenRouter.

    Uses ChatOpenAI pointed at the OpenRouter API, which supports
    any model (Gemini, Llama, Mistral, etc.) via a single endpoint.

    Usage:
        generator = LangChainGenerator()
        response = generator.generate("What was CBA's NIM?", chunks)
    """

    framework = "langchain-openrouter"

    def __init__(self, *, model: str | None = None, temperature: float = 0.1):
        self.model = model or os.getenv("OPENROUTER_MODEL", "anthropic/claude-opus-4.6")
        self.temperature = temperature

    def _get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

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

        context = self.build_context(chunks)
        system_message = SYSTEM_PROMPT.format(context=context)

        try:
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

            # Extract thinking from <think> tags (DeepSeek, Qwen, etc.)
            thinking = re.findall(r"<think>(.*?)</think>", answer_text, re.DOTALL)
            if thinking:
                answer_text = re.sub(r"<think>.*?</think>", "", answer_text, flags=re.DOTALL).strip()

            # Also check additional_kwargs for reasoning_content (some models)
            if not thinking and hasattr(response, "additional_kwargs"):
                reasoning = response.additional_kwargs.get("reasoning_content")
                if reasoning:
                    thinking = [reasoning]

        except Exception as e:
            answer_text = self.fallback_answer(chunks)
            thinking = []
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
            thinking=thinking,
            metadata=self.build_metadata(
                chunks=chunks, citations=citations, token_usage=token_usage,
            ),
        )
