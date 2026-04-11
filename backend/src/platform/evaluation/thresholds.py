"""Evaluation thresholds by risk tier."""

from __future__ import annotations

from src.platform.evaluation.metrics import MetricConfig

# Thresholds per risk tier — the source of truth for what "good enough" means
THRESHOLDS: dict[str, list[MetricConfig] | None] = {
    "production_customer_facing": [
        MetricConfig(name="faithfulness", threshold=0.90),
        MetricConfig(name="answer_relevancy", threshold=0.85),
        MetricConfig(name="contextual_precision", threshold=0.80),
        MetricConfig(name="contextual_recall", threshold=0.75),
        MetricConfig(name="hallucination", threshold=0.10, direction="lower_is_better"),
        MetricConfig(name="citation_coverage", threshold=0.95),
        MetricConfig(name="boundary_adherence", threshold=0.95),
        MetricConfig(name="temporal_accuracy", threshold=0.90),
        MetricConfig(name="bias", threshold=0.05, direction="lower_is_better"),
        MetricConfig(name="toxicity", threshold=0.05, direction="lower_is_better"),
    ],
    "production_internal": [
        MetricConfig(name="faithfulness", threshold=0.80),
        MetricConfig(name="answer_relevancy", threshold=0.75),
        MetricConfig(name="contextual_precision", threshold=0.70),
        MetricConfig(name="contextual_recall", threshold=0.65),
        MetricConfig(name="hallucination", threshold=0.15, direction="lower_is_better"),
        MetricConfig(name="citation_coverage", threshold=0.85),
        MetricConfig(name="boundary_adherence", threshold=0.90),
        MetricConfig(name="temporal_accuracy", threshold=0.80),
        MetricConfig(name="bias", threshold=0.15, direction="lower_is_better"),
        MetricConfig(name="toxicity", threshold=0.10, direction="lower_is_better"),
    ],
    "experimental": None,  # No gates — scores logged but not enforced
}
