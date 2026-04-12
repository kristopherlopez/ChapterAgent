"""Bias detection guardrail — checks for demographic and language bias."""

from __future__ import annotations

import logging
import os
import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

logger = logging.getLogger(__name__)

_BIAS_INDICATORS = [
    r"\b(always|never|every)\b.*\b(men|women|males?|females?)\b",
    r"\b(typical|obviously|naturally)\b.*\b(gender|race|age|religion)\b",
    r"\b(those people|these people|that kind)\b",
    r"\b(superior|inferior)\b.*\b(race|gender|group)\b",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _BIAS_INDICATORS]


class BiasGuardrail(Guardrail):
    """Detects demographic and language bias in agent output.

    Modes (in priority order):
        1. prerecorded_score — uses a pre-set score for demo/testing
        2. DeepEval BiasMetric — LLM-as-judge via gpt-4o-mini
        3. Pattern matching fallback — regex-based bias indicator detection
    """

    name = "Bias Scan"
    description = "Scans for demographic bias in output"

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
        """Run DeepEval BiasMetric, fall back to pattern matching."""
        if self._use_deepeval and os.environ.get("OPENAI_API_KEY"):
            try:
                return await self._deepeval_bias(output)
            except Exception as e:
                logger.warning("DeepEval bias failed, using heuristic: %s", e)

        return self._heuristic_bias(output)

    async def _deepeval_bias(self, output: str) -> float:
        """Use DeepEval BiasMetric (LLM-as-judge)."""
        from deepeval.metrics import BiasMetric
        from deepeval.test_case import LLMTestCase

        metric = BiasMetric(
            threshold=self.threshold,
            model=self._model,
            include_reason=True,
            async_mode=False,
        )
        test_case = LLMTestCase(
            input="Evaluate for bias",
            actual_output=output,
        )
        await metric.a_measure(test_case)
        return metric.score

    @staticmethod
    def _heuristic_bias(output: str) -> float:
        """Pattern matching fallback for bias detection."""
        matches = sum(1 for p in _COMPILED_PATTERNS if p.search(output))
        return min(matches * 0.2, 1.0)
