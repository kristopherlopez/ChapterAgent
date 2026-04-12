"""Evaluation harness — runs golden datasets through solutions and scores them."""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic import BaseModel, Field

from src.platform.evaluation.datasets import GoldenDataset, GoldenDatasetLoader
from src.platform.evaluation.metrics import (
    METRIC_DISPLAY_NAMES,
    MetricConfig,
    MetricResult,
)
from src.platform.evaluation.thresholds import THRESHOLDS

logger = logging.getLogger(__name__)


class EvaluationReport(BaseModel):
    """Complete evaluation report for a solution."""
    solution_id: str
    risk_tier: str
    total_test_cases: int
    metrics: list[MetricResult] = Field(default_factory=list)
    overall_score: float = 0.0
    passed: bool = False
    summary: str = ""

    @property
    def passing_metrics(self) -> int:
        return sum(1 for m in self.metrics if m.status == "pass")

    @property
    def failing_metrics(self) -> list[MetricResult]:
        return [m for m in self.metrics if m.status == "fail"]


class EvaluationHarness:
    """Evaluation harness — wraps DeepEval for standardised solution evaluation.

    The harness loads a golden dataset, runs each test case through the solution,
    and scores the results against configured thresholds.

    Usage:
        harness = EvaluationHarness(
            risk_tier="production_customer_facing",
            golden_dataset_path=Path("golden_dataset/dataset.json"),
        )
        report = harness.run_prerecorded(prerecorded_scores)
    """

    def __init__(
        self,
        *,
        risk_tier: str = "production_internal",
        golden_dataset_path: Path | None = None,
        metric_overrides: list[MetricConfig] | None = None,
    ):
        self.risk_tier = risk_tier
        self._golden_dataset: GoldenDataset | None = None

        if golden_dataset_path and golden_dataset_path.exists():
            self._golden_dataset = GoldenDatasetLoader.load(golden_dataset_path)

        # Use overrides if provided, otherwise load from risk tier defaults
        if metric_overrides:
            self._metrics = metric_overrides
        else:
            self._metrics = THRESHOLDS.get(risk_tier) or []

    @property
    def golden_dataset(self) -> GoldenDataset | None:
        return self._golden_dataset

    @property
    def metric_configs(self) -> list[MetricConfig]:
        return list(self._metrics)

    def run_prerecorded(
        self,
        scores: dict[str, float],
        *,
        solution_id: str = "",
        total_test_cases: int = 50,
    ) -> EvaluationReport:
        """Run evaluation using pre-recorded scores (for demo).

        Args:
            scores: Metric name -> score mapping (e.g., {"faithfulness": 0.94})
            solution_id: ID of the solution being evaluated
            total_test_cases: Number of test cases in the golden dataset
        """
        results = []
        for config in self._metrics:
            score = scores.get(config.name)
            if score is not None:
                result = MetricResult.from_config(config, score)
                # Use display name
                result.metric = METRIC_DISPLAY_NAMES.get(config.name, config.name)
                results.append(result)

        all_passed = all(r.status == "pass" for r in results)
        overall = sum(r.score for r in results) / len(results) if results else 0.0

        return EvaluationReport(
            solution_id=solution_id,
            risk_tier=self.risk_tier,
            total_test_cases=total_test_cases,
            metrics=results,
            overall_score=round(overall, 4),
            passed=all_passed,
            summary=self._build_summary(results, all_passed),
        )

    def run_live(
        self,
        test_cases: list[dict],
        *,
        solution_id: str = "",
        model: str = "gpt-4o",
    ) -> EvaluationReport:
        """Run evaluation using real DeepEval metrics (LLM-as-judge).

        Args:
            test_cases: List of dicts with keys: input, actual_output,
                expected_output (optional), retrieval_context (optional).
            solution_id: ID of the solution being evaluated.
            model: Judge model for LLM-as-judge metrics.

        Returns:
            EvaluationReport with real DeepEval scores.
        """
        from deepeval import evaluate
        from deepeval.metrics import (
            FaithfulnessMetric,
            AnswerRelevancyMetric,
            ContextualPrecisionMetric,
            ContextualRecallMetric,
            HallucinationMetric,
            BiasMetric,
            ToxicityMetric,
        )
        from deepeval.test_case import LLMTestCase

        # Build DeepEval test cases
        deepeval_cases = []
        for tc in test_cases:
            deepeval_cases.append(
                LLMTestCase(
                    input=tc["input"],
                    actual_output=tc["actual_output"],
                    expected_output=tc.get("expected_output"),
                    retrieval_context=tc.get("retrieval_context"),
                    context=tc.get("context"),
                )
            )

        # Map metric names to DeepEval metric classes
        metric_map = {
            "faithfulness": lambda t: FaithfulnessMetric(threshold=t, model=model, include_reason=True),
            "answer_relevancy": lambda t: AnswerRelevancyMetric(threshold=t, model=model, include_reason=True),
            "contextual_precision": lambda t: ContextualPrecisionMetric(threshold=t, model=model, include_reason=True),
            "contextual_recall": lambda t: ContextualRecallMetric(threshold=t, model=model, include_reason=True),
            "hallucination": lambda t: HallucinationMetric(threshold=t, model=model, include_reason=True),
            "bias": lambda t: BiasMetric(threshold=t, model=model, include_reason=True),
            "toxicity": lambda t: ToxicityMetric(threshold=t, model=model, include_reason=True),
        }

        # Build metrics from config
        deepeval_metrics = []
        for config in self._metrics:
            factory = metric_map.get(config.name)
            if factory:
                deepeval_metrics.append(factory(config.threshold))

        if not deepeval_metrics:
            logger.warning("No DeepEval metrics configured for live evaluation")
            return self.run_prerecorded({}, solution_id=solution_id)

        # Run evaluation
        logger.info(
            "Running DeepEval evaluation: %d cases, %d metrics, judge=%s",
            len(deepeval_cases), len(deepeval_metrics), model,
        )
        eval_results = evaluate(
            test_cases=deepeval_cases,
            metrics=deepeval_metrics,
            print_results=False,
        )

        # Extract scores per metric (average across test cases)
        metric_scores: dict[str, list[float]] = {}
        for result in eval_results.test_results:
            for metric_data in result.metrics_data:
                name = metric_data.name.lower().replace(" ", "_")
                if name not in metric_scores:
                    metric_scores[name] = []
                if metric_data.score is not None:
                    metric_scores[name].append(metric_data.score)

        # Build results using existing threshold configs
        results = []
        for config in self._metrics:
            scores = metric_scores.get(config.name, [])
            if scores:
                avg_score = sum(scores) / len(scores)
                result = MetricResult.from_config(config, avg_score)
                result.metric = METRIC_DISPLAY_NAMES.get(config.name, config.name)
                results.append(result)

        all_passed = all(r.status == "pass" for r in results)
        overall = sum(r.score for r in results) / len(results) if results else 0.0

        return EvaluationReport(
            solution_id=solution_id,
            risk_tier=self.risk_tier,
            total_test_cases=len(test_cases),
            metrics=results,
            overall_score=round(overall, 4),
            passed=all_passed,
            summary=self._build_summary(results, all_passed),
        )

    @staticmethod
    def _build_summary(results: list[MetricResult], passed: bool) -> str:
        """Build a human-readable summary."""
        passing = sum(1 for r in results if r.status == "pass")
        total = len(results)
        status = "PASSED" if passed else "FAILED"
        failing = [r.metric for r in results if r.status == "fail"]
        summary = f"Evaluation {status}: {passing}/{total} metrics above threshold."
        if failing:
            summary += f" Failing: {', '.join(failing)}."
        return summary
