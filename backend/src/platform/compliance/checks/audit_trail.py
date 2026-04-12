"""Check 6: Audit Trail Completeness — AI-GOV-008.

Verifies all interactions have complete trace fields.

Supports two tracing patterns:
- **Embedded solutions**: Traces stored as JSON files on disk (traces/ directory).
- **Endpoint solutions (inline)**: Traces embedded in endpoint response body,
  validated against the platform's trace contract.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.platform.compliance.checks import CheckResult
from src.platform.observability.trace_contract import (
    REQUIRED_TRACE_LABELS,
    validate_inline_trace,
)


REQUIRED_TRACE_FIELDS = REQUIRED_TRACE_LABELS


def _validate_trace_file(trace_file: Path) -> tuple[bool, list[str]]:
    """Validate a single trace file against the contract."""
    try:
        with open(trace_file) as f:
            trace = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False, ["invalid_file"]

    return validate_inline_trace(trace)


def run(
    solution_dir: Path,
    total_test_cases: int = 0,
    *,
    inline_traces: list[dict] | None = None,
) -> CheckResult:
    """Verify audit trail completeness.

    Checks:
        - Trace files exist for the solution (disk-based), OR
        - Inline traces from endpoint responses are contract-compliant
        - All required fields present in each trace
        - Completeness >= 100%

    Args:
        solution_dir: Path to the solution directory.
        total_test_cases: Expected number of traced interactions.
        inline_traces: Optional list of trace dicts from endpoint responses.
            When provided, these are validated instead of (or in addition to)
            disk-based traces.
    """
    project_root = Path(__file__).resolve().parents[5]
    solution_id = solution_dir.name

    # --- Collect traces from all sources ---
    trace_results: list[tuple[str, bool, list[str]]] = []

    # Source 1: Disk-based trace files
    candidates = [
        solution_dir / "traces",
        project_root / "traces" / solution_id,
        project_root / "traces" / "rag-policy-qa",
        project_root / "results" / solution_id,
        project_root / "results" / "rag-policy-qa",
    ]
    trace_dir = next((d for d in candidates if d.exists()), candidates[0])
    trace_files = list(trace_dir.glob("*.json")) if trace_dir.exists() else []

    for trace_file in trace_files:
        is_valid, missing = _validate_trace_file(trace_file)
        trace_results.append((trace_file.name, is_valid, missing))

    # Source 2: Inline traces from endpoint responses
    if inline_traces:
        for i, trace_data in enumerate(inline_traces):
            source = f"inline_response_{i + 1:03d}"
            # Extract the trace field if it's a full endpoint response
            trace_payload = trace_data.get("trace", trace_data) if isinstance(trace_data, dict) else trace_data
            is_valid, missing = validate_inline_trace(trace_payload)
            trace_results.append((source, is_valid, missing))

    interactions_sampled = len(trace_results)

    if interactions_sampled == 0:
        return CheckResult(
            check="audit_trail",
            policy_id="AI-GOV-008",
            policy="Full interaction tracing",
            status="FAIL",
            evidence={
                "error": f"No traces found (checked {trace_dir} and inline responses)",
                "interactions_sampled": 0,
                "completeness": 0.0,
                "trace_contract": "inline",
            },
        )

    complete_count = sum(1 for _, is_valid, _ in trace_results if is_valid)
    missing_fields = [
        {"source": source, "missing": missing}
        for source, is_valid, missing in trace_results
        if not is_valid
    ]

    completeness = complete_count / interactions_sampled

    return CheckResult(
        check="audit_trail",
        policy_id="AI-GOV-008",
        policy="Full interaction tracing",
        status="PASS" if completeness >= 1.0 else "FAIL",
        evidence={
            "interactions_sampled": interactions_sampled,
            "complete": complete_count,
            "completeness": round(completeness, 4),
            "fields_verified": REQUIRED_TRACE_FIELDS,
            "missing_fields": missing_fields[:5],
            "trace_contract": "inline",
            "trace_sources": {
                "disk": len(trace_files),
                "inline": len(inline_traces) if inline_traces else 0,
            },
        },
    )
