"""Evaluation metric definitions and configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class MetricConfig(BaseModel):
    """Configuration for a single evaluation metric."""
    name: str
    threshold: float
    direction: Literal["higher_is_better", "lower_is_better"] = "higher_is_better"

    def passes(self, score: float) -> bool:
        """Check if a score meets the threshold."""
        if self.direction == "higher_is_better":
            return score >= self.threshold
        return score <= self.threshold


class MetricResult(BaseModel):
    """Result of evaluating a single metric."""
    metric: str
    score: float
    threshold: float
    status: Literal["pass", "warn", "fail"]
    direction: str = "higher_is_better"

    @classmethod
    def from_config(cls, config: MetricConfig, score: float) -> MetricResult:
        """Create a result from a config and score."""
        passed = config.passes(score)
        return cls(
            metric=config.name,
            score=score,
            threshold=config.threshold,
            status="pass" if passed else "fail",
            direction=config.direction,
        )


# Display-friendly metric names
METRIC_DISPLAY_NAMES: dict[str, str] = {
    "faithfulness": "Faithfulness",
    "answer_relevancy": "Answer Relevancy",
    "contextual_precision": "Context Precision",
    "contextual_recall": "Context Recall",
    "hallucination": "Hallucination",
    "citation_coverage": "Citation Coverage",
    "boundary_adherence": "Boundary Adherence",
    "temporal_accuracy": "Temporal Accuracy",
    "bias": "Bias",
    "toxicity": "Toxicity",
}
