"""Toxicity detection guardrail — checks for harmful or toxic content."""

from __future__ import annotations

import logging
import os
import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

logger = logging.getLogger(__name__)

_TOXICITY_PATTERNS = [
    r"\b(hate|hatred|despise)\b",
    r"\b(kill|murder|destroy)\b.*\b(you|them|people)\b",
    r"\b(stupid|idiot|moron|dumb)\b",
    r"\b(threat|threaten|threatening)\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _TOXICITY_PATTERNS]


class ToxicityGuardrail(Guardrail):
    """Detects harmful or toxic content in agent output.

    Modes (in priority order):
        1. prerecorded_score — uses a pre-set score for demo/testing
        2. DeepEval ToxicityMetric — LLM-as-judge via gpt-4o-mini
        3. Pattern matching fallback — regex-based toxicity detection
    """

    name = "Toxicity Scan"
    description = "Scans for harmful or toxic content in output"

    def __init__(
        self,
        *,
        threshold: float = 0.05,
        prerecorded_score: float | None = None,
        use_deepeval: bool = True,
        model: str = "gpt-4o-mini",
    ):
        self.threshold = threshold
        self._prerecorded_score = prerecorded_score
        self._use_deepeval = use_deepeval
        self._model = model

    async def _check(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> GuardrailResult:
        if self._prerecorded_score is not None:
            score = self._prerecorded_score
        else:
            score = await self._evaluate(output)

        passed = score <= self.threshold
        return GuardrailResult(
            name=self.name,
            result="pass" if passed else "fail",
            detail=f"Score: {score:.2f} (threshold: {self.threshold:.2f})",
            score=score,
        )

    async def _evaluate(self, output: str) -> float:
        """Run DeepEval ToxicityMetric, fall back to pattern matching."""
        if self._use_deepeval and os.environ.get("OPENAI_API_KEY"):
            try:
                return await self._deepeval_toxicity(output)
            except Exception as e:
                logger.warning("DeepEval toxicity failed, using heuristic: %s", e)

        return self._heuristic_toxicity(output)

    async def _deepeval_toxicity(self, output: str) -> float:
        """Use DeepEval ToxicityMetric (LLM-as-judge)."""
        from deepeval.metrics import ToxicityMetric
        from deepeval.test_case import LLMTestCase

        metric = ToxicityMetric(
            threshold=self.threshold,
            model=self._model,
            include_reason=True,
            async_mode=False,
        )
        test_case = LLMTestCase(
            input="Evaluate for toxicity",
            actual_output=output,
        )
        await metric.a_measure(test_case)
        return metric.score

    @staticmethod
    def _heuristic_toxicity(output: str) -> float:
        """Pattern matching fallback for toxicity detection."""
        matches = sum(1 for p in _COMPILED if p.search(output))
        return min(matches * 0.25, 1.0)
