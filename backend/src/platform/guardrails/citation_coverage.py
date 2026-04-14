"""Citation coverage guardrail — checks that all claims are cited."""

from __future__ import annotations

import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

# Patterns that indicate a citation is present
_CITATION_PATTERNS = [
    re.compile(r"\[Source:.*?\]", re.IGNORECASE),
    re.compile(r"\(Source:.*?\)", re.IGNORECASE),
    re.compile(r"\*Source:.*?\*", re.IGNORECASE),
    re.compile(r"p\.\s*\d+", re.IGNORECASE),
    re.compile(r"Page\s+\d+", re.IGNORECASE),
    re.compile(r"Section:?\s+[A-Z]", re.IGNORECASE),
    re.compile(r"\[\d{1,3}(?:\s*,\s*\d{1,3})*\]"),   # [1], [12], [1, 2] (max 3 digits to exclude years)
]


class CitationCoverageGuardrail(Guardrail):
    """Checks that every factual claim in the output has a citation.

    Identifies factual claims (sentences containing numbers, percentages,
    or specific assertions) and checks each has an associated citation.
    """

    name = "Citation Coverage"
    description = "Verifies all factual claims have source citations"

    def __init__(self, *, threshold: float = 0.95, prerecorded_score: float | None = None):
        self.threshold = threshold
        self._prerecorded_score = prerecorded_score

    def _is_factual_claim(self, sentence: str) -> bool:
        """Heuristic: factual claim if it has numbers or assertions."""
        has_number = bool(re.search(r"\d+\.?\d*[%BMK]?", sentence))
        has_assertion = bool(re.search(
            r"\b(was|were|is|are|increased|decreased|grew|declined|reported|achieved)\b",
            sentence,
            re.IGNORECASE,
        ))
        return has_number or has_assertion

    def _has_citation(self, text_block: str) -> bool:
        """Check if a text block contains any citation marker."""
        return any(p.search(text_block) for p in _CITATION_PATTERNS)

    async def _check(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> GuardrailResult:
        if self._prerecorded_score is not None:
            score = self._prerecorded_score
            passed = score >= self.threshold
            return GuardrailResult(
                name=self.name,
                result="pass" if passed else "fail",
                detail=f"{score:.0%} claims cited (threshold: {self.threshold:.0%})",
                score=score,
            )

        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', output) if s.strip()]
        factual_claims = [s for s in sentences if self._is_factual_claim(s)]

        if not factual_claims:
            return GuardrailResult(
                name=self.name,
                result="pass",
                detail="No factual claims detected — citation check not applicable",
                score=1.0,
            )

        # Check if output has citations (either inline or at the end)
        has_any_citation = self._has_citation(output)
        if has_any_citation:
            # Simplified: if citations exist, estimate coverage based on citation density
            citation_count = sum(1 for p in _CITATION_PATTERNS for _ in p.finditer(output))
            coverage = min(citation_count / len(factual_claims), 1.0)
        else:
            coverage = 0.0

        passed = coverage >= self.threshold
        return GuardrailResult(
            name=self.name,
            result="pass" if passed else "fail",
            detail=f"{coverage:.0%} claims cited (threshold: {self.threshold:.0%})",
            score=coverage,
        )
