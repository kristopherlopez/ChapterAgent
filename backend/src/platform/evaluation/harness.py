"""Evaluation harness — runs golden datasets through solutions and scores them."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from src.platform.evaluation.datasets import GoldenDataset, GoldenDatasetLoader
from src.platform.evaluation.metrics import (
    METRIC_DISPLAY_NAMES,
    MetricConfig,
    MetricResult,
)
from src.platform.evaluation.thresholds import THRESHOLDS


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
