"""PII detection guardrail — regex-based Australian PII patterns."""

from __future__ import annotations

import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

# Australian PII patterns
_PATTERNS: dict[str, re.Pattern[str]] = {
    "TFN (Tax File Number)": re.compile(r"\b\d{3}\s?\d{3}\s?\d{3}\b"),
    "ABN (Australian Business Number)": re.compile(r"\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b"),
    "Medicare Number": re.compile(r"\b\d{4}\s?\d{5}\s?\d{1}\b"),
    "Phone Number": re.compile(r"\b(?:\+61|0)\d[\s-]?\d{4}[\s-]?\d{4}\b"),
    "Email Address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "Credit Card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    "BSB Number": re.compile(r"\b\d{3}[\s-]?\d{3}\b"),
}


class PIIGuardrail(Guardrail):
    """Detects personally identifiable information in agent output.

    Scans output text for Australian PII patterns including TFN, ABN,
    Medicare, phone numbers, email addresses, and credit card numbers.
    Zero tolerance — any PII detection is a failure.
    """

    name = "PII Detection"
    description = "Scans for personally identifiable information in output"

    async def _check(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> GuardrailResult:
        found: list[str] = []

        for pattern_name, pattern in _PATTERNS.items():
            matches = pattern.findall(output)
            if matches:
                found.append(f"{pattern_name}: {len(matches)} instance(s)")

        if found:
            return GuardrailResult(
                name=self.name,
                result="fail",
                detail=f"PII detected — {'; '.join(found)}",
                score=0.0,
            )

        return GuardrailResult(
            name=self.name,
            result="pass",
            detail="0 PII instances found",
            score=1.0,
        )
