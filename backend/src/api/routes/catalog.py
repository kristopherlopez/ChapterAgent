"""Component catalog, golden dataset generator, and validation API routes."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.platform.discovery import discover_solutions
from src.platform.evaluation.datasets import GoldenDatasetLoader

router = APIRouter(tags=["catalog"])

ROOT = Path(__file__).resolve().parents[4]
SOLUTIONS_DIR = ROOT / "solutions"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ComponentInterface(BaseModel):
    squad_provides: str
    component_returns: str


class CatalogComponent(BaseModel):
    id: str
    name: str
    type: str
    description: str
    interface: ComponentInterface
    adoption: list[str]
    status: str


class GenerationRequest(BaseModel):
    solution_id: str
    num_cases: int = Field(default=10, ge=1, le=100)
    query_types: list[str] = []


class ReviewUpdate(BaseModel):
    review_status: str
    reviewed_by: str = "SME Reviewer"
    review_notes: str | None = None
    edited_answer: str | None = None


class SignOffRequest(BaseModel):
    reviewer: str


# ---------------------------------------------------------------------------
# Component definitions
# ---------------------------------------------------------------------------

GUARDRAIL_COMPONENTS: list[dict[str, Any]] = [
    {"id": "guardrail-scope-adherence", "name": "Scope Adherence", "description": "Enforces topic boundaries using a configurable topic graph with 3 strictness levels", "interface": {"squad_provides": "Topic graph JSON, scope level (1-3), refusal message", "component_returns": "pass/warn/fail with boundary violation detail"}},
    {"id": "guardrail-pii-scan", "name": "PII Detection", "description": "Scans agent output for personally identifiable information using NER-based detection", "interface": {"squad_provides": "Agent output text", "component_returns": "pass/fail with detected PII entities and types"}},
    {"id": "guardrail-bias", "name": "Bias Detection", "description": "Monitors for demographic and language bias in agent outputs", "interface": {"squad_provides": "Agent output text", "component_returns": "pass/warn/fail with bias score and flagged phrases"}},
    {"id": "guardrail-toxicity", "name": "Toxicity Filter", "description": "Screens agent output for harmful, offensive, or toxic content", "interface": {"squad_provides": "Agent output text", "component_returns": "pass/fail with toxicity score"}},
    {"id": "guardrail-citation-coverage", "name": "Citation Coverage", "description": "Verifies response includes proper source citations for factual claims", "interface": {"squad_provides": "Agent output with citation markers, threshold", "component_returns": "pass/fail with coverage ratio"}},
    {"id": "guardrail-temporal-accuracy", "name": "Temporal Accuracy", "description": "Validates time-sensitive references are consistent with source documents", "interface": {"squad_provides": "Agent output, context with dates", "component_returns": "pass/warn/fail with temporal inconsistencies"}},
    {"id": "guardrail-prompt-injection", "name": "Prompt Injection Detection", "description": "Detects prompt injection and jailbreak attempts in user input", "interface": {"squad_provides": "User input text", "component_returns": "pass/fail with injection type and confidence"}},
]

EVALUATION_COMPONENTS: list[dict[str, Any]] = [
    {"id": "evaluation-harness", "name": "Evaluation Harness", "description": "Standardised test runner scoring AI solutions against risk-tier thresholds with 10+ metrics", "interface": {"squad_provides": "Golden dataset, risk tier, metric overrides (optional)", "component_returns": "EvaluationReport with per-metric scores and pass/fail"}},
]

COMPLIANCE_COMPONENTS: list[dict[str, Any]] = [
    {"id": "compliance-registration", "name": "Registration Check (AI-GOV-001)", "description": "Verifies solution.yaml manifest is complete with all required fields", "interface": {"squad_provides": "solution.yaml in solution directory", "component_returns": "PASS/FAIL with field-level evidence"}},
    {"id": "compliance-evaluation", "name": "Evaluation Gate (AI-GOV-003)", "description": "Confirms solution passed evaluation harness for its risk tier", "interface": {"squad_provides": "EvaluationReport from the harness", "component_returns": "PASS/FAIL with per-metric evidence"}},
    {"id": "compliance-pii", "name": "PII Validation (AI-GOV-005)", "description": "Validates PII guardrail passes on golden dataset sample", "interface": {"squad_provides": "Guardrail results from sample", "component_returns": "PASS/FAIL with PII detection evidence"}},
    {"id": "compliance-guardrails", "name": "Guardrail Validation (AI-GOV-006)", "description": "Confirms all configured guardrails pass on golden dataset sample", "interface": {"squad_provides": "Full guardrail results from sample", "component_returns": "PASS/FAIL with per-guardrail breakdown"}},
    {"id": "compliance-bias-toxicity", "name": "Bias & Toxicity Gate (AI-GOV-007)", "description": "Verifies bias and toxicity scores within acceptable bounds", "interface": {"squad_provides": "Guardrail results + evaluation report", "component_returns": "PASS/FAIL with scores and thresholds"}},
    {"id": "compliance-audit-trail", "name": "Audit Trail Check (AI-GOV-008)", "description": "Validates execution traces exist for 100% of golden dataset cases. Supports disk-based traces (embedded solutions) and inline traces from endpoint responses", "interface": {"squad_provides": "Trace files on disk OR inline traces in endpoint response body", "component_returns": "PASS/FAIL with trace coverage, sources breakdown (disk vs inline)"}},
    {"id": "compliance-golden-dataset", "name": "Golden Dataset Sign-off (AI-GOV-009)", "description": "Confirms golden dataset reviewed and signed off by qualified reviewer", "interface": {"squad_provides": "sign-off.json in golden dataset directory", "component_returns": "PASS/FAIL with sign-off evidence"}},
    {"id": "compliance-prompt-governance", "name": "Prompt Governance (AI-GOV-010)", "description": "Validates system prompts are version-controlled and registered", "interface": {"squad_provides": "Prompt templates in solution directory", "component_returns": "PASS/FAIL with registered/unregistered prompts"}},
]

OBSERVABILITY_COMPONENTS: list[dict[str, Any]] = [
    {"id": "observability-trace-logger", "name": "Trace Logger", "description": "Structured execution tracing capturing every step with timestamps and durations", "interface": {"squad_provides": "Instrument pipeline with trace_step() calls", "component_returns": "Structured JSON trace file"}},
    {"id": "observability-trace-contract", "name": "Trace Contract Validator", "description": "Validates that endpoint responses include compliant traces. Supports inline traces (endpoint returns trace in response body) and OpenTelemetry sidecar (production pattern for orgs where the Chapter doesn't control endpoint schemas)", "interface": {"squad_provides": "Inline: trace field in JSON response. OTel: spans pushed to platform collector with solution.id tag", "component_returns": "Validation result with matched/missing trace labels and completeness score"}},
]

TOOLING_COMPONENTS: list[dict[str, Any]] = [
    {"id": "tooling-golden-dataset-generator", "name": "Golden Dataset Generator", "description": "Generates draft test triples from a squad's document corpus", "interface": {"squad_provides": "Solution ID, corpus documents, query types", "component_returns": "Generated test cases matching golden dataset schema"}, "status": "beta"},
    {"id": "tooling-golden-dataset-validation", "name": "Golden Dataset Validation UI", "description": "SME review interface for approving, rejecting, or editing test cases", "interface": {"squad_provides": "Golden dataset, SME reviewers", "component_returns": "Validated dataset with review statuses and sign-off"}, "status": "beta"},
]


def _build_catalog() -> list[dict[str, Any]]:
    """Build the full component catalog with dynamic adoption data."""
    # Discover solutions for adoption mapping
    adoption_map: dict[str, list[str]] = {}
    try:
        manifests = discover_solutions(SOLUTIONS_DIR)
        for m in manifests:
            sid = m.id
            # All solutions use evaluation, compliance, observability
            for comp_id in ["evaluation-harness", "observability-trace-logger"]:
                adoption_map.setdefault(comp_id, []).append(sid)
            # Map guardrail names to component IDs
            for gname in m.guardrail_names:
                comp_id = f"guardrail-{gname.replace('_', '-')}"
                adoption_map.setdefault(comp_id, []).append(sid)
            # All solutions use all compliance gates
            for comp in COMPLIANCE_COMPONENTS:
                adoption_map.setdefault(comp["id"], []).append(sid)
    except Exception:
        pass  # Fall back to empty adoption if discovery fails

    components = []
    all_defs = [
        ("guardrail", GUARDRAIL_COMPONENTS),
        ("evaluation", EVALUATION_COMPONENTS),
        ("compliance", COMPLIANCE_COMPONENTS),
        ("observability", OBSERVABILITY_COMPONENTS),
        ("tooling", TOOLING_COMPONENTS),
    ]
    for comp_type, defs in all_defs:
        for d in defs:
            components.append({
                "id": d["id"],
                "name": d["name"],
                "type": comp_type,
                "description": d["description"],
                "interface": d["interface"],
                "adoption": adoption_map.get(d["id"], []),
                "status": d.get("status", "active"),
            })
    return components


# ---------------------------------------------------------------------------
# In-memory validation state
# ---------------------------------------------------------------------------

_validation_state: dict[str, dict[str, Any]] = {}


def _get_validation_state(solution_id: str) -> dict[str, Any]:
    """Get or initialise validation state for a solution."""
    if solution_id in _validation_state:
        return _validation_state[solution_id]

    # Try to load from golden dataset
    solution_dir = SOLUTIONS_DIR / solution_id.replace("-", "_").replace("petsure-annual-report-qa", "qa-agent")
    # Handle ID-to-directory mapping
    dir_map = {
        "petsure-annual-report-qa": "qa-agent",
        "governance-policy-qa": "governance-policy-qa",
    }
    dir_name = dir_map.get(solution_id, solution_id)
    solution_dir = SOLUTIONS_DIR / dir_name
    dataset_path = solution_dir / "golden_dataset" / "dataset.json"

    test_cases = []
    if dataset_path.exists():
        ds = GoldenDatasetLoader.load(dataset_path)
        for tc in ds.test_cases[:20]:  # Cap at 20 for demo
            test_cases.append({
                "case_id": tc.case_id,
                "query_type": tc.query_type,
                "question": tc.question,
                "expected_answer": tc.expected_answer or "",
                "expected_behaviour": tc.expected_behaviour,
                "expected_grounding": tc.expected_grounding,
                "expected_citations": [c if isinstance(c, dict) else {} for c in tc.expected_citations],
                "scope_level": tc.scope_level,
                "key_metrics": tc.key_metrics,
                "review_status": "pending",
                "reviewed_by": None,
                "reviewed_at": None,
                "review_notes": None,
            })

    state = {
        "solution_id": solution_id,
        "solution_name": dir_name.replace("-", " ").title(),
        "version": "1.0",
        "test_cases": test_cases,
        "signed_off": False,
        "signed_off_by": None,
        "signed_off_at": None,
    }
    _validation_state[solution_id] = state
    return state


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/catalog")
def list_catalog() -> list[dict[str, Any]]:
    """List all reusable platform components with adoption data."""
    return _build_catalog()


@router.get("/catalog/{component_id}")
def get_component(component_id: str) -> dict[str, Any]:
    """Get a single platform component by ID."""
    for comp in _build_catalog():
        if comp["id"] == component_id:
            return comp
    raise HTTPException(status_code=404, detail=f"Component not found: {component_id}")


@router.post("/catalog/generator/generate")
def generate_test_cases(req: GenerationRequest) -> dict[str, Any]:
    """Generate draft golden dataset test cases for a solution.

    For demo, returns pre-generated cases based on existing golden dataset.
    In production, this would use LLMs to synthesise from the corpus.
    """
    dir_map = {
        "petsure-annual-report-qa": "qa-agent",
        "governance-policy-qa": "governance-policy-qa",
    }
    dir_name = dir_map.get(req.solution_id)
    if not dir_name:
        raise HTTPException(status_code=404, detail=f"Unknown solution: {req.solution_id}")

    dataset_path = SOLUTIONS_DIR / dir_name / "golden_dataset" / "dataset.json"
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail="No golden dataset found for this solution")

    ds = GoldenDatasetLoader.load(dataset_path)
    cases = ds.test_cases[:req.num_cases]

    # Filter by query types if specified
    if req.query_types:
        filtered = [tc for tc in ds.test_cases if tc.query_type in req.query_types]
        cases = filtered[:req.num_cases]

    generated = []
    for i, tc in enumerate(cases):
        generated.append({
            "case_id": f"GEN-{i + 1:03d}",
            "query_type": tc.query_type,
            "question": tc.question,
            "expected_answer": tc.expected_answer or "",
            "expected_behaviour": tc.expected_behaviour,
            "expected_grounding": tc.expected_grounding,
            "expected_citations": [c if isinstance(c, dict) else {} for c in tc.expected_citations],
            "scope_level": tc.scope_level,
            "key_metrics": tc.key_metrics,
        })

    return {
        "solution_id": req.solution_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "test_cases": generated,
    }


@router.get("/catalog/validation/{solution_id}")
def get_validation_dataset(solution_id: str) -> dict[str, Any]:
    """Get golden dataset with review statuses for validation UI."""
    state = _get_validation_state(solution_id)
    cases = state["test_cases"]
    reviewed = sum(1 for c in cases if c["review_status"] != "pending")
    approved = sum(1 for c in cases if c["review_status"] == "approved")
    rejected = sum(1 for c in cases if c["review_status"] == "rejected")
    pending = sum(1 for c in cases if c["review_status"] == "pending")

    return {
        "solutionId": state["solution_id"],
        "solutionName": state["solution_name"],
        "version": state["version"],
        "totalCases": len(cases),
        "reviewed": reviewed,
        "approved": approved,
        "rejected": rejected,
        "pending": pending,
        "signedOff": state["signed_off"],
        "signedOffBy": state["signed_off_by"],
        "signedOffAt": state["signed_off_at"],
        "testCases": [
            {
                "caseId": c["case_id"],
                "queryType": c["query_type"],
                "question": c["question"],
                "expectedAnswer": c["expected_answer"],
                "expectedBehaviour": c["expected_behaviour"],
                "expectedGrounding": c["expected_grounding"],
                "expectedCitations": c["expected_citations"],
                "scopeLevel": c["scope_level"],
                "keyMetrics": c["key_metrics"],
                "reviewStatus": c["review_status"],
                "reviewedBy": c["reviewed_by"],
                "reviewedAt": c["reviewed_at"],
                "reviewNotes": c["review_notes"],
            }
            for c in cases
        ],
    }


@router.put("/catalog/validation/{solution_id}/{case_id}")
def update_review(solution_id: str, case_id: str, update: ReviewUpdate) -> dict[str, str]:
    """Update review status for a single test case."""
    state = _get_validation_state(solution_id)
    for case in state["test_cases"]:
        if case["case_id"] == case_id:
            case["review_status"] = update.review_status
            case["reviewed_by"] = update.reviewed_by
            case["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            case["review_notes"] = update.review_notes
            if update.edited_answer:
                case["expected_answer"] = update.edited_answer
            return {"status": "updated"}
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")


@router.post("/catalog/validation/{solution_id}/sign-off")
def sign_off_dataset(solution_id: str, req: SignOffRequest) -> dict[str, str]:
    """Sign off a validated golden dataset."""
    state = _get_validation_state(solution_id)
    pending = sum(1 for c in state["test_cases"] if c["review_status"] == "pending")
    if pending > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot sign off: {pending} cases still pending review",
        )
    state["signed_off"] = True
    state["signed_off_by"] = req.reviewer
    state["signed_off_at"] = datetime.now(timezone.utc).isoformat()
    return {"status": "signed_off"}
