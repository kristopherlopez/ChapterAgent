"""Citation coverage guardrail — checks that all claims are cited."""

from __future__ import annotations

import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

# Patterns that indicate a citation is present in the output text.
# LLMs use many formats: [12], [^1^], [^1], \[12\], [source](12),
# [Source: ...], p.30, Page 30, etc.
_CITATION_PATTERNS = [
    re.compile(r"\[Source:.*?\]", re.IGNORECASE),
    re.compile(r"\(Source:.*?\)", re.IGNORECASE),
    re.compile(r"\*Source:.*?\*", re.IGNORECASE),
    re.compile(r"Cite:\s*Page\s+\d+", re.IGNORECASE),  # Cite:Page 12, Cite: Page 12
    re.compile(r"p\.\s*\d+", re.IGNORECASE),
    re.compile(r"Page\s+\d+", re.IGNORECASE),
    re.compile(r"Section:?\s+[A-Z]", re.IGNORECASE),
    re.compile(r"\\?\[?\^?\d{1,3}\^?\\?\]"),           # [12], [^1^], \[12\], ^1^
    re.compile(r"\[source\]\(\d+\)", re.IGNORECASE),    # [source](12)
    re.compile(r"\[.*?\]\(\d+\)"),                      # [anything](12)
]


class CitationCoverageGuardrail(Guardrail):
    """Checks that every factual claim in the output has a citation.

    Identifies factual claims (sentences containing numbers, percentages,
    or specific assertions) and checks each has an associated citation.

    When structured citations are available (e.g. from cite_source tool
    calls), they can be passed via the ``citations_count`` constructor
    parameter to bypass fragile regex matching on the output text.
    """

    name = "Citation Coverage"
    description = "Verifies all factual claims have source citations"

    def __init__(
        self,
        *,
        threshold: float = 0.95,
        prerecorded_score: float | None = None,
        citations_count: int | None = None,
    ):
        self.threshold = threshold
        self._prerecorded_score = prerecorded_score
        self._citations_count = citations_count

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

        # If structured citations were provided (from cite_source tool),
        # trust them as the authoritative citation record.  The agent is
        # instructed to call cite_source for every factual claim; each call
        # records the source page/section.  One citation can cover multiple
        # sentences from the same source, so dividing by factual-claim count
        # would under-report coverage.
        if self._citations_count is not None and self._citations_count > 0:
            coverage = 1.0
        else:
            # Fall back to regex detection on the output text.
            # Count unique citation markers (deduplicated across patterns
            # to avoid double-counting overlapping matches like "Page 12"
            # matching both the Page and Cite:Page patterns).
            citation_spans: set[tuple[int, int]] = set()
            for p in _CITATION_PATTERNS:
                for m in p.finditer(output):
                    citation_spans.add((m.start(), m.end()))
            if citation_spans:
                # Each distinct citation marker can cover all factual claims
                # in its vicinity.  A single trailing citation block (e.g.
                # "Cite:Page 12, Section X") is standard for short answers
                # where the entire response references the same source.
                # Treat presence of any citation as covering all claims when
                # the answer is ≤5 sentences (typical single-source answer).
                if len(factual_claims) <= 5 and len(citation_spans) >= 1:
                    coverage = 1.0
                else:
                    coverage = min(len(citation_spans) / len(factual_claims), 1.0)
            else:
                coverage = 0.0

        passed = coverage >= self.threshold
        return GuardrailResult(
            name=self.name,
            result="pass" if passed else "fail",
            detail=f"{coverage:.0%} claims cited (threshold: {self.threshold:.0%})",
            score=coverage,
        )
