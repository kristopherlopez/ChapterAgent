"""Check 1: Solution Registration — AI-GOV-001.

Verifies the solution manifest is complete with all required fields.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.platform.compliance.checks import CheckResult


REQUIRED_FIELDS = ["name", "id", "type", "version", "description"]
REQUIRED_TOP_LEVEL = ["owner", "risk_tier"]
VALID_RISK_TIERS = [
    "experimental",
    "production_internal",
    "production_customer_facing",
]


def run(solution_dir: Path) -> CheckResult:
    """Verify solution registration is complete.

    Checks:
        - solution.yaml exists
        - All required solution fields present
        - Owner assigned
        - Risk tier assigned and valid
    """
    manifest_path = solution_dir / "solution.yaml"

    if not manifest_path.exists():
        return CheckResult(
            check="solution_registration",
            policy_id="AI-GOV-001",
            policy="All AI solutions must be registered",
            status="FAIL",
            evidence={"error": f"solution.yaml not found at {manifest_path}"},
        )

    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    errors: list[str] = []
    solution = manifest.get("solution", {})

    # Check required solution fields
    for field in REQUIRED_FIELDS:
        if not solution.get(field):
            errors.append(f"solution.{field} is missing")

    # Check top-level required fields
    for field in REQUIRED_TOP_LEVEL:
        if not manifest.get(field):
            errors.append(f"{field} is missing")

    # Validate risk tier
    risk_tier = manifest.get("risk_tier", "")
    if risk_tier and risk_tier not in VALID_RISK_TIERS:
        errors.append(
            f"risk_tier '{risk_tier}' is not valid. "
            f"Must be one of: {', '.join(VALID_RISK_TIERS)}"
        )

    evidence: dict[str, Any] = {
        "solution_id": solution.get("id", ""),
        "solution_name": solution.get("name", ""),
        "version": solution.get("version", ""),
        "risk_tier": risk_tier,
        "owner": manifest.get("owner", ""),
        "manifest_path": str(manifest_path),
    }

    if errors:
        evidence["errors"] = errors

    return CheckResult(
        check="solution_registration",
        policy_id="AI-GOV-001",
        policy="All AI solutions must be registered",
        status="FAIL" if errors else "PASS",
        evidence=evidence,
    )
