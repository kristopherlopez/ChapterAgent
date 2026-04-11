"""Deployment gate — automated pass/fail decision for AI solutions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.platform.evaluation.harness import EvaluationReport
from src.platform.guardrails.base import GuardrailResult


class GateDecision(BaseModel):
    """Result of the deployment gate evaluation."""
    gate: str = "Deployment Gate"
    result: Literal["pass", "warn", "fail"]
    reason: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    )
    guardrails_passed: int = 0
    guardrails_total: int = 0
    metrics_passed: int = 0
    metrics_total: int = 0


class DeploymentGate:
    """Automated deployment gate — decides if a solution can go to production.

    Checks:
        1. All guardrails passed
        2. All evaluation metrics above threshold
        3. Evidence report can be generated

    Usage:
        gate = DeploymentGate()
        decision = gate.evaluate(guardrail_results, eval_report)
    """

    def evaluate(
        self,
        guardrail_results: list[GuardrailResult],
        eval_report: EvaluationReport,
    ) -> GateDecision:
        """Make the deployment decision."""
        guardrails_passed = sum(1 for r in guardrail_results if r.result == "pass")
        guardrails_total = len(guardrail_results)
        guardrails_ok = guardrails_passed == guardrails_total

        metrics_passed = eval_report.passing_metrics
        metrics_total = len(eval_report.metrics)
        eval_ok = eval_report.passed

        reasons = []

        if guardrails_ok:
            reasons.append(f"All {guardrails_total} guardrails passed.")
        else:
            failed = [r.name for r in guardrail_results if r.result != "pass"]
            reasons.append(f"Guardrail failures: {', '.join(failed)}.")

        if eval_ok:
            tier = eval_report.risk_tier
            reasons.append(
                f"All {metrics_total} evaluation metrics above"
                f" {tier} thresholds."
            )
        else:
            failed_metrics = [m.metric for m in eval_report.failing_metrics]
            reasons.append(f"Metrics below threshold: {', '.join(failed_metrics)}.")

        if guardrails_ok and eval_ok:
            reasons.append("Evidence report generated.")

        overall = "pass" if (guardrails_ok and eval_ok) else "fail"

        return GateDecision(
            result=overall,
            reason=" ".join(reasons),
            guardrails_passed=guardrails_passed,
            guardrails_total=guardrails_total,
            metrics_passed=metrics_passed,
            metrics_total=metrics_total,
        )
