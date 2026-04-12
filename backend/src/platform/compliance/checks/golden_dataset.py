"""Check 7: Golden Dataset Sign-Off — AI-GOV-009.

Verifies the golden dataset has been human-reviewed and approved.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.platform.compliance.checks import CheckResult


def run(solution_dir: Path) -> CheckResult:
    """Verify golden dataset has human sign-off.

    Checks:
        - Golden dataset file exists
        - Sign-off record exists (golden_dataset_signoff.json)
        - Reviewer identity and date are recorded
        - All entries are approved

    Args:
        solution_dir: Path to the solution directory.
    """
    # Find golden dataset
    dataset_path = solution_dir / "golden_dataset" / "dataset.json"
    signoff_path = solution_dir / "golden_dataset" / "signoff.json"

    if not dataset_path.exists():
        return CheckResult(
            check="golden_dataset_signoff",
            policy_id="AI-GOV-009",
            policy="Golden datasets human-reviewed and approved",
            status="FAIL",
            evidence={"error": f"Golden dataset not found at {dataset_path}"},
        )

    # Load dataset to count entries
    with open(dataset_path) as f:
        dataset = json.load(f)

    test_cases = dataset.get("test_cases", [])
    total_entries = len(test_cases)
    dataset_version = dataset.get("version", "unknown")

    # Check for sign-off record
    if signoff_path.exists():
        with open(signoff_path) as f:
            signoff = json.load(f)

        reviewer = signoff.get("reviewer", "")
        review_date = signoff.get("review_date", "")
        entries_approved = signoff.get("entries_approved", 0)

        if not reviewer or not review_date:
            return CheckResult(
                check="golden_dataset_signoff",
                policy_id="AI-GOV-009",
                policy="Golden datasets human-reviewed and approved",
                status="FAIL",
                evidence={
                    "error": "Sign-off record incomplete — missing reviewer or date",
                    "signoff_path": str(signoff_path),
                },
            )

        return CheckResult(
            check="golden_dataset_signoff",
            policy_id="AI-GOV-009",
            policy="Golden datasets human-reviewed and approved",
            status="PASS" if entries_approved >= total_entries else "FAIL",
            evidence={
                "reviewer": reviewer,
                "review_date": review_date,
                "dataset_version": dataset_version,
                "entries_reviewed": total_entries,
                "entries_approved": entries_approved,
            },
        )

    # No sign-off file — generate a stub for the reviewer to complete
    return CheckResult(
        check="golden_dataset_signoff",
        policy_id="AI-GOV-009",
        policy="Golden datasets human-reviewed and approved",
        status="FAIL",
        evidence={
            "error": "No sign-off record found. Create golden_dataset/signoff.json",
            "expected_format": {
                "reviewer": "<name>",
                "review_date": "<YYYY-MM-DD>",
                "entries_approved": total_entries,
                "dataset_version": dataset_version,
            },
            "total_entries": total_entries,
        },
    )
