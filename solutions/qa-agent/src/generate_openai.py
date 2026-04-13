"""Answer generation — OpenAI Agents SDK with function tools."""

from __future__ import annotations

from agents import Agent, Runner, function_tool  # pip install openai-agents
from retrieve import RetrievedChunk
from schema import (
    SYSTEM_PROMPT,
    AnswerPayload,
    BaseGenerator,
    Citation,
    QAResponse,
)


class OpenAIGenerator(BaseGenerator):
    """Generates grounded answers using the OpenAI Agents SDK.

    Uses Agent with function_tool decorators for structured tool use.
    The agent receives retrieved context and can cite sources via tools.

    Usage:
        generator = OpenAIGenerator()
        response = generator.generate("What was CBA's NIM?", chunks)
    """

    framework = "openai-agents-sdk"

    def __init__(self, *, model: str = "gpt-4o", temperature: float = 0.1):
        self.model = model
        self.temperature = temperature

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
        instructions = SYSTEM_PROMPT.format(context=context)
        citations = self.extract_citations(chunks)

        try:
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
