"""Trace contract validator for endpoint-type solutions.

Defines the response contract that endpoint solutions must conform to in
order to pass the AI-GOV-008 audit trail check.  The platform provides two
integration patterns:

**Option 1 — Inline traces (demo / lightweight):**
    The endpoint returns traces embedded in its JSON response body.  The
    compliance runner validates the trace at test time.  Simple to implement
    but requires the team to change their response schema.

**Option 2 — Sidecar export via OpenTelemetry (production / PetSure Australia-realistic):**
    The endpoint pushes spans to a platform-provided OTel collector (e.g.
    LangFuse, Jaeger).  The platform doesn't own the endpoint response schema
    — it owns the collector.  More realistic at PetSure Australia scale where the
    Head of may not have the influence to mandate response format changes.

This module implements Option 1 for the demo and documents the Option 2
contract for production readiness.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Inline trace response contract (Option 1)
# ---------------------------------------------------------------------------

class TraceStepContract(BaseModel):
    """Schema for a single step in an inline trace."""
    step: int
    label: str
    durationMs: int | float
    detail: str | None = None


class InlineTraceContract(BaseModel):
    """Schema an endpoint must include in its response for inline tracing.

    Example conforming response from an endpoint::

        {
            "answer": "PetSure Australia's NPAT was $10,133M...",
            "citations": [...],
            "trace": {
                "steps": [
                    {"step": 1, "label": "Query received", "durationMs": 0},
                    {"step": 2, "label": "Context retrieval", "durationMs": 120, "detail": "3 chunks"},
                    {"step": 3, "label": "LLM generation", "durationMs": 1340},
                    {"step": 4, "label": "Guardrail checks", "durationMs": 187, "detail": "8/8 pass"},
                    {"step": 5, "label": "Response returned", "durationMs": 1647}
                ]
            }
        }
    """
    steps: list[TraceStepContract] = Field(default_factory=list)


# Required trace step labels that must appear for a trace to be complete.
# Step labels are matched case-insensitively using substring containment,
# so "Context retrieval (hybrid search)" matches "retrieval".
REQUIRED_TRACE_LABELS = [
    "query",
    "retrieval",
    "generation",
    "guardrail",
    "response",
]

# Labels that indicate the trace was short-circuited (blocked, refused,
# injection detected).  Blocked traces are exempt from the full label
# requirement — they only need "query" + a terminal label.
BLOCKED_INDICATORS = ["block", "refus", "inject", "out_of_scope"]


def validate_inline_trace(trace_data: dict | list) -> tuple[bool, list[str]]:
    """Validate an inline trace against the contract.

    Args:
        trace_data: The ``trace`` field from an endpoint response, or a
            raw list of step dicts.

    Returns:
        Tuple of (is_valid, missing_labels).
    """
    if isinstance(trace_data, dict):
        steps = trace_data.get("steps", [])
    elif isinstance(trace_data, list):
        steps = trace_data
    else:
        return False, REQUIRED_TRACE_LABELS[:]

    # Collect matched labels from steps
    matched: set[str] = set()
    is_blocked = False

    for step in steps:
        if not isinstance(step, dict):
            continue
        label = step.get("label", "").lower()

        for required in REQUIRED_TRACE_LABELS:
            if required in label:
                matched.add(required)

        if any(indicator in label for indicator in BLOCKED_INDICATORS):
            is_blocked = True

    # Blocked traces only need query + terminal
    if is_blocked:
        has_query = "query" in matched
        has_terminal = "response" in matched or "guardrail" in matched
        if has_query and has_terminal:
            return True, []

    missing = [r for r in REQUIRED_TRACE_LABELS if r not in matched]

    # Allow one missing field (flexibility for different solution types)
    is_valid = len(missing) <= 1
    return is_valid, missing


# ---------------------------------------------------------------------------
# OpenTelemetry sidecar contract (Option 2 — documented, not enforced)
# ---------------------------------------------------------------------------

OTEL_CONTRACT_DOCS = """
## OpenTelemetry Sidecar Contract (Production Pattern)

For production deployments where the platform does not control the endpoint
response schema, solutions export traces via OpenTelemetry:

### Team responsibilities:
1. Instrument their pipeline with OTel SDK (Python: opentelemetry-sdk)
2. Export spans to the platform's OTel collector endpoint
3. Tag spans with the solution ID and trace contract version
4. Emit the required span types declared in solution.yaml `tracing.emits`

### Platform responsibilities:
1. Provide the OTel collector endpoint (e.g. LangFuse, Jaeger)
2. Validate span completeness asynchronously (not at request time)
3. Surface gaps in the Compliance Health dashboard
4. AI-GOV-008 check queries the collector for trace coverage

### Required span attributes:
- `solution.id` — matches solution.yaml ID
- `trace.contract_version` — matches solution.yaml tracing.contract_version
- `step.type` — one of: query, retrieval, generation, guardrail, response, tool_call, reasoning_step

### Why this pattern at PetSure Australia:
The Head of typically doesn't have the authority to mandate response
schema changes across all teams.  OTel is an industry standard that teams
may already use.  The platform provides the collector; teams instrument at
their own pace.  Adoption is tracked via the dashboard — visibility, not
enforcement.
"""
