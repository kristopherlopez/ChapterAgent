"""Check 2: Evaluation Harness — AI-GOV-003.

Verifies the solution passes quality thresholds for its risk tier.
"""

from __future__ import annotations

from src.platform.compliance.checks import CheckResult
from src.platform.evaluation.harness import EvaluationReport


def run(eval_report: EvaluationReport) -> CheckResult:
    """Verify all evaluation metrics pass their risk-tier thresholds.

    Args:
        eval_report: The evaluation report from running the golden dataset.
    """
    evidence = {
        "risk_tier": eval_report.risk_tier,
        "total_test_cases": eval_report.total_test_cases,
        "overall_score": eval_report.overall_score,
        "metrics_passed": eval_report.passing_metrics,
        "metrics_total": len(eval_report.metrics),
        "metrics": {
            m.metric: {"score": m.score, "threshold": m.threshold, "status": m.status}
            for m in eval_report.metrics
        },
    }

    if not eval_report.passed:
        evidence["failing"] = [
            {"metric": m.metric, "score": m.score, "threshold": m.threshold}
            for m in eval_report.failing_metrics
        ]

    return CheckResult(
        check="evaluation_harness",
        policy_id="AI-GOV-003",
        policy="Solutions must pass quality thresholds",
        status="PASS" if eval_report.passed else "FAIL",
        evidence=evidence,
    )
