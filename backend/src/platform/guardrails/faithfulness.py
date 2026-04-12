"""Faithfulness guardrail — checks if output is grounded in retrieved context."""

from __future__ import annotations

import logging
import os
import re

from src.platform.guardrails.base import Guardrail, GuardrailResult

logger = logging.getLogger(__name__)


class FaithfulnessGuardrail(Guardrail):
    """Checks that every claim in the output is grounded in the retrieved context.

    Modes (in priority order):
        1. prerecorded_score — uses a pre-set score for demo/testing
        2. DeepEval FaithfulnessMetric — LLM-as-judge via gpt-4o-mini
        3. Heuristic fallback — word-overlap grounding check
    """

    name = "Faithfulness Check"
    description = "Verifies output claims are grounded in retrieved context"

    def __init__(
        self,
        *,
        threshold: float = 0.90,
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
        elif context:
            score = await self._evaluate(input, output, context)
        else:
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

    async def _evaluate(
        self, input: str, output: str, context: list[str]
    ) -> float:
        """Run DeepEval FaithfulnessMetric, fall back to heuristic."""
        if self._use_deepeval and os.environ.get("OPENAI_API_KEY"):
            try:
                return await self._deepeval_faithfulness(input, output, context)
            except Exception as e:
                logger.warning("DeepEval faithfulness failed, using heuristic: %s", e)

        return self._heuristic_faithfulness(output, context)

    async def _deepeval_faithfulness(
        self, input: str, output: str, context: list[str]
    ) -> float:
        """Use DeepEval FaithfulnessMetric (LLM-as-judge)."""
        from deepeval.metrics import FaithfulnessMetric
        from deepeval.test_case import LLMTestCase

        metric = FaithfulnessMetric(
            threshold=self.threshold,
            model=self._model,
            include_reason=True,
            async_mode=False,
        )
        test_case = LLMTestCase(
            input=input,
            actual_output=output,
            retrieval_context=context,
        )
        await metric.a_measure(test_case)
        return metric.score

    @staticmethod
    def _heuristic_faithfulness(output: str, context: list[str]) -> float:
        """Word-overlap heuristic — fast fallback for when DeepEval is unavailable."""
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
            words = [w for w in sentence.lower().split() if len(w) > 3]
            if not words:
                grounded += 1
                continue
            match_ratio = sum(1 for w in words if w in context_text) / len(words)
            if match_ratio >= 0.5:
                grounded += 1

        return grounded / len(sentences)
