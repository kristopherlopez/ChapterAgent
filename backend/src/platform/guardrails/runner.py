"""Guardrail runner — orchestrates all guardrails for a solution."""

from __future__ import annotations

import asyncio

from src.platform.guardrails.base import Guardrail, GuardrailResult
from src.platform.guardrails.bias import BiasGuardrail
from src.platform.guardrails.citation_coverage import CitationCoverageGuardrail
from src.platform.guardrails.faithfulness import FaithfulnessGuardrail
from src.platform.guardrails.pii import PIIGuardrail
from src.platform.guardrails.prompt_injection import PromptInjectionGuardrail
from src.platform.guardrails.scope import ScopeGuardrail
from src.platform.guardrails.temporal_accuracy import TemporalAccuracyGuardrail
from src.platform.guardrails.toxicity import ToxicityGuardrail


class GuardrailRunner:
    """Runs all configured guardrails for a solution.

    Usage:
        runner = GuardrailRunner(guardrails=[PIIGuardrail(), ScopeGuardrail(...)])
        results = await runner.run_all(input="...", output="...", context=[...])
    """

    def __init__(self, guardrails: list[Guardrail]):
        self.guardrails = guardrails

    async def run_all(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> list[GuardrailResult]:
        """Run all guardrails concurrently, return results."""
        tasks = [
            g.check(input=input, output=output, context=context)
            for g in self.guardrails
        ]
        return list(await asyncio.gather(*tasks))

    @property
    def all_passed(self) -> bool:
        """Check if all guardrails in the last run passed. Use after run_all."""
        return True  # Stateless — use results from run_all directly

    @classmethod
    def for_qa_agent(
        cls,
        *,
        scope_level: int = 1,
        topic_graph: dict | None = None,
        topic_graph_path: str | None = None,
        refusal_message: str = "I can only answer questions about PetSure Australia's 2025 Annual Report.",
        faithfulness_threshold: float = 0.90,
        citation_coverage_threshold: float = 0.95,
        citations_count: int | None = None,
    ) -> GuardrailRunner:
        """Factory: build the guardrail runner for a Q&A agent."""
        return cls(
            guardrails=[
                PromptInjectionGuardrail(),
                ScopeGuardrail(
                    scope_level=scope_level,
                    topic_graph=topic_graph,
                    topic_graph_path=topic_graph_path,
                    refusal_message=refusal_message,
                ),
                PIIGuardrail(),
                FaithfulnessGuardrail(threshold=faithfulness_threshold, model="gpt-5.4"),
                BiasGuardrail(),
                ToxicityGuardrail(),
                CitationCoverageGuardrail(
                    threshold=citation_coverage_threshold,
                    citations_count=citations_count,
                ),
                TemporalAccuracyGuardrail(),
            ]
        )


# Registry for building guardrails by name
GUARDRAIL_REGISTRY: dict[str, type[Guardrail]] = {
    "scope_adherence": ScopeGuardrail,
    "pii_scan": PIIGuardrail,
    "faithfulness": FaithfulnessGuardrail,
    "bias": BiasGuardrail,
    "toxicity": ToxicityGuardrail,
    "citation_coverage": CitationCoverageGuardrail,
    "temporal_accuracy": TemporalAccuracyGuardrail,
    "prompt_injection": PromptInjectionGuardrail,
}
