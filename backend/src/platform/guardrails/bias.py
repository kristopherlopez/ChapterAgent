"""Bias detection guardrail — checks for demographic and language bias."""

from __future__ import annotations

import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

_BIAS_INDICATORS = [
    r"\b(always|never|every)\b.*\b(men|women|males?|females?)\b",
    r"\b(typical|obviously|naturally)\b.*\b(gender|race|age|religion)\b",
    r"\b(those people|these people|that kind)\b",
    r"\b(superior|inferior)\b.*\b(race|gender|group)\b",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _BIAS_INDICATORS]


class BiasGuardrail(Guardrail):
    """Detects demographic and language bias in agent output.

    Uses pattern matching for common bias indicators.
    For production, would use DeepEval BiasMetric (LLM-as-judge).
    """

    name = "Bias Scan"
    description = "Scans for demographic bias in output"

    def __init__(self, *, threshold: float = 0.05, prerecorded_score: float | None = None):
        self.threshold = threshold
        self._prerecorded_score = prerecorded_score

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
            matches = sum(1 for p in _COMPILED_PATTERNS if p.search(output))
            # Normalize: each match adds 0.2 to the bias score (capped at 1.0)
            score = min(matches * 0.2, 1.0)

        passed = score <= self.threshold
        return GuardrailResult(
            name=self.name,
            result="pass" if passed else "fail",
            detail=f"Score: {score:.2f} (threshold: {self.threshold:.2f})",
            score=score,
        )
