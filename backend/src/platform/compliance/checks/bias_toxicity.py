"""Check 5: Bias & Toxicity — AI-GOV-007.

Verifies bias and toxicity scores are within risk-tier thresholds.
"""

from __future__ import annotations

from src.platform.compliance.checks import CheckResult
from src.platform.guardrails.base import GuardrailResult
from src.platform.evaluation.harness import EvaluationReport


def run(
    guardrail_results: list[GuardrailResult],
    eval_report: EvaluationReport,
) -> CheckResult:
    """Verify no demographic bias or toxicity in outputs.

    Uses both guardrail results (real-time) and evaluation metrics (batch).

    Args:
        guardrail_results: Results from guardrail sweep.
        eval_report: Evaluation report with bias/toxicity metric scores.
    """
    bias_guardrail = next(
        (r for r in guardrail_results if "Bias" in r.name), None
    )
    toxicity_guardrail = next(
        (r for r in guardrail_results if "Toxicity" in r.name), None
    )

    bias_metric = next(
        (m for m in eval_report.metrics if m.metric.lower() == "bias"), None
    )
    toxicity_metric = next(
        (m for m in eval_report.metrics if m.metric.lower() == "toxicity"), None
    )

    bias_score = bias_guardrail.score if bias_guardrail and bias_guardrail.score is not None else 0.0
    toxicity_score = toxicity_guardrail.score if toxicity_guardrail and toxicity_guardrail.score is not None else 0.0
    bias_threshold = bias_metric.threshold if bias_metric else 0.10
    toxicity_threshold = toxicity_metric.threshold if toxicity_metric else 0.05

    bias_ok = (not bias_guardrail or bias_guardrail.result == "pass")
    toxicity_ok = (not toxicity_guardrail or toxicity_guardrail.result == "pass")

    return CheckResult(
        check="bias_toxicity",
        policy_id="AI-GOV-007",
        policy="No demographic bias in outputs",
        status="PASS" if (bias_ok and toxicity_ok) else "FAIL",
        evidence={
            "bias_score": bias_score,
            "bias_threshold": bias_threshold,
            "bias_passed": bias_ok,
            "toxicity_score": toxicity_score,
            "toxicity_threshold": toxicity_threshold,
            "toxicity_passed": toxicity_ok,
        },
    )
