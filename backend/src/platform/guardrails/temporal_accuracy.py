"""Temporal accuracy guardrail — checks period attribution in output."""

from __future__ import annotations

import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

_PERIOD_PATTERNS = [
    re.compile(r"FY\s*20\d{2}", re.IGNORECASE),
    re.compile(r"20\d{2}\s*(?:financial|fiscal)\s*year", re.IGNORECASE),
    re.compile(r"(?:half|full)[\s-]*year\s*20\d{2}", re.IGNORECASE),
    re.compile(r"(?:H1|H2|1H|2H)\s*20\d{2}", re.IGNORECASE),
    re.compile(r"(?:Q[1-4])\s*20\d{2}", re.IGNORECASE),
]


class TemporalAccuracyGuardrail(Guardrail):
    """Checks that period references in the output match the source context.

    Extracts temporal references (FY2024, FY2023, etc.) from both the output
    and the retrieved context, checking for misattribution.
    """

    name = "Temporal Accuracy"
    description = "Verifies figures are attributed to the correct reporting period"

    def __init__(self, *, prerecorded_score: float | None = None):
        self._prerecorded_score = prerecorded_score

    def _extract_periods(self, text: str) -> set[str]:
        """Extract all period references from text."""
        periods = set()
        for pattern in _PERIOD_PATTERNS:
            for match in pattern.finditer(text):
                periods.add(match.group().upper().replace(" ", ""))
        return periods

    async def _check(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> GuardrailResult:
        if self._prerecorded_score is not None:
            score = self._prerecorded_score
            passed = score >= 0.90
            return GuardrailResult(
                name=self.name,
                result="pass" if passed else "fail",
                detail=f"Score: {score:.2f}",
                score=score,
            )

        output_periods = self._extract_periods(output)
        if not output_periods:
            return GuardrailResult(
                name=self.name,
                result="pass",
                detail="No temporal references in output — check not applicable",
                score=1.0,
            )

        if not context:
            return GuardrailResult(
                name=self.name,
                result="warn",
                detail="No context provided — cannot verify temporal accuracy",
                score=None,
            )

        context_periods = set()
        for chunk in context:
            context_periods.update(self._extract_periods(chunk))

        if not context_periods:
            return GuardrailResult(
                name=self.name,
                result="pass",
                detail="No temporal references in context — check not applicable",
                score=1.0,
            )

        # Check if output periods are present in context
        valid_periods = output_periods & context_periods
        score = len(valid_periods) / len(output_periods) if output_periods else 1.0
        passed = score >= 0.90

        return GuardrailResult(
            name=self.name,
            result="pass" if passed else "fail",
            detail=(
                f"Score: {score:.2f} — "
                f"{len(valid_periods)}/{len(output_periods)} "
                "periods verified in context"
            ),
            score=score,
        )
