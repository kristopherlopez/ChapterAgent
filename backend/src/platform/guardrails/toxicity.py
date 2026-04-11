"""Toxicity detection guardrail — checks for harmful or toxic content."""

from __future__ import annotations

import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

_TOXICITY_PATTERNS = [
    r"\b(hate|hatred|despise)\b",
    r"\b(kill|murder|destroy)\b.*\b(you|them|people)\b",
    r"\b(stupid|idiot|moron|dumb)\b",
    r"\b(threat|threaten|threatening)\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _TOXICITY_PATTERNS]


class ToxicityGuardrail(Guardrail):
    """Detects harmful or toxic content in agent output.

    Uses pattern matching for common toxicity indicators.
    For production, would use DeepEval ToxicityMetric (LLM-as-judge).
    """

    name = "Toxicity Scan"
    description = "Scans for harmful or toxic content in output"

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
            matches = sum(1 for p in _COMPILED if p.search(output))
            score = min(matches * 0.25, 1.0)

        passed = score <= self.threshold
        return GuardrailResult(
            name=self.name,
            result="pass" if passed else "fail",
            detail=f"Score: {score:.2f} (threshold: {self.threshold:.2f})",
            score=score,
        )
