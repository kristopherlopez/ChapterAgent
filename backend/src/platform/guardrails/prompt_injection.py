"""Prompt injection detection guardrail."""

from __future__ import annotations

import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(?:previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a?\s*(?:new|different|general)", re.IGNORECASE),
    re.compile(r"(?:system|initial)\s+prompt", re.IGNORECASE),
    re.compile(r"disregard\s+(?:all|your|the)\s+(?:previous|prior|instructions?)", re.IGNORECASE),
    re.compile(r"forget\s+(?:all|your|everything)\s+(?:previous|you\s+know)", re.IGNORECASE),
    re.compile(r"pretend\s+(?:you\s+are|to\s+be)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(?:if|though|a)", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"DAN\s+mode", re.IGNORECASE),
    re.compile(r"do\s+anything\s+now", re.IGNORECASE),
]


class PromptInjectionGuardrail(Guardrail):
    """Detects prompt injection attempts in user input.

    Fires before retrieval — blocks the query before it reaches the LLM.
    Uses pattern matching for common injection techniques.
    """

    name = "Prompt Injection"
    description = "Detects and blocks prompt injection attempts"

    async def _check(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> GuardrailResult:
        detected: list[str] = []

        for pattern in _INJECTION_PATTERNS:
            if pattern.search(input):
                detected.append(pattern.pattern[:50])

        if detected:
            return GuardrailResult(
                name=self.name,
                result="fail",
                detail=f"Injection attempt detected — {len(detected)} pattern(s) matched",
                score=0.0,
            )

        return GuardrailResult(
            name=self.name,
            result="pass",
            detail="0 injections detected",
            score=1.0,
        )
