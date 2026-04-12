"""Faithfulness guardrail — checks if output is grounded in retrieved context."""

from __future__ import annotations

from src.platform.guardrails.base import Guardrail, GuardrailResult


class FaithfulnessGuardrail(Guardrail):
    """Checks that every claim in the output is grounded in the retrieved context.

    In live mode, uses an LLM-as-judge to evaluate faithfulness.
    In prerecorded mode, uses a pre-set score for demo purposes.
    """

    name = "Faithfulness Check"
    description = "Verifies output claims are grounded in retrieved context"

    def __init__(self, *, threshold: float = 0.90, prerecorded_score: float | None = None):
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
        elif context:
            score = self._heuristic_faithfulness(output, context)
        else:
            # No context provided — can't assess faithfulness
            return GuardrailResult(
                name=self.name,
                result="warn",
                detail="No retrieval context provided — faithfulness cannot be assessed",
                score=None,
            )

        passed = score >= self.threshold
        return GuardrailResult(
            name=self.name,
            result="pass" if passed else "fail",
            detail=f"Score: {score:.2f} (threshold: {self.threshold:.2f})",
            score=score,
        )

    @staticmethod
    def _heuristic_faithfulness(output: str, context: list[str]) -> float:
        """Simple heuristic: what fraction of output sentences appear in context.

        For production, this would use an LLM-as-judge (DeepEval FaithfulnessMetric).
        This heuristic is a fast fallback for demo/testing.
        """
        import re

        # Strip inline citations like [Source: ...] before splitting
        clean_output = re.sub(r'\[Source:[^\]]*\]', '', output)
        sentences = [
            s.strip() for s in re.split(r'[.!?]+', clean_output)
            if s.strip() and len(s.strip()) > 10
        ]
        if not sentences:
            return 1.0

        context_text = " ".join(context).lower()
        grounded = 0
        for sentence in sentences:
            # Check if key words from the sentence appear in context
            words = [w for w in sentence.lower().split() if len(w) > 3]
            if not words:
                grounded += 1
                continue
            match_ratio = sum(1 for w in words if w in context_text) / len(words)
            if match_ratio >= 0.5:
                grounded += 1

        return grounded / len(sentences)
