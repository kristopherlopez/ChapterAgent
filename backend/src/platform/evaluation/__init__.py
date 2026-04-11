"""Evaluation harness — DeepEval integration for AI solution governance."""

from src.platform.evaluation.datasets import GoldenDatasetLoader
from src.platform.evaluation.harness import EvaluationHarness, EvaluationReport
from src.platform.evaluation.metrics import MetricConfig
from src.platform.evaluation.thresholds import THRESHOLDS

__all__ = [
    "EvaluationHarness",
    "EvaluationReport",
    "GoldenDatasetLoader",
    "MetricConfig",
    "THRESHOLDS",
]
