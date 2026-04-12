"""Check 3: PII Validation — AI-GOV-005.

Runs PII detection across all golden dataset outputs to verify zero leakage.
"""

from __future__ import annotations

from src.platform.compliance.checks import CheckResult
from src.platform.guardrails.base import GuardrailResult


# The PII entities the platform scans for (Australian-specific)
ENTITIES_SCANNED = [
    "TFN", "ABN", "MEDICARE", "PHONE", "EMAIL", "CREDIT_CARD", "BSB",
]


def run(guardrail_results: list[GuardrailResult]) -> CheckResult:
    """Verify zero PII in outputs using guardrail results.

    Uses the PII Detection guardrail results from the golden dataset sweep.
    Zero tolerance — any PII detection is a FAIL.

    Args:
        guardrail_results: Results from running all guardrails on the golden dataset.
    """
    pii_result = next(
        (r for r in guardrail_results if "PII" in r.name), None
    )

    if pii_result is None:
        return CheckResult(
            check="pii_validation",
            policy_id="AI-GOV-005",
            policy="No PII in AI solution outputs",
            status="FAIL",
            evidence={"error": "PII guardrail was not included in the run"},
        )

    pii_detected = pii_result.result != "pass"

    return CheckResult(
        check="pii_validation",
        policy_id="AI-GOV-005",
        policy="No PII in AI solution outputs",
        status="FAIL" if pii_detected else "PASS",
        evidence={
            "pii_detected": 1 if pii_detected else 0,
            "detector": "regex_australian_pii",
            "entities_scanned": ENTITIES_SCANNED,
            "detail": pii_result.detail,
            "elapsed_ms": pii_result.elapsed_ms,
        },
    )
