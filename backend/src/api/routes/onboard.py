"""Solution onboarding — create solution directory, manifest, and scaffolding."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Literal

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

router = APIRouter(tags=["onboard"])

ROOT = Path(__file__).resolve().parents[4]
SOLUTIONS_DIR = ROOT / "solutions"
RESULTS_DIR = ROOT / "results"

AEST = timezone(timedelta(hours=10))

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class EndpointConfig(BaseModel):
    url: str
    method: str = "POST"
    timeout_ms: int = 30000


class DatasetConfig(BaseModel):
    source: str
    records: int
    features: int
    target: str
    protected_attributes: list[str] = []


class ModelConfig(BaseModel):
    type: str
    framework: str
    explainability: str = "SHAP"
    training_split: float = 0.7


class CorpusDocument(BaseModel):
    name: str
    format: str = "pdf"
    pages: int = 0


class CorpusConfig(BaseModel):
    source: str
    documents: list[CorpusDocument] = []


class FrameworkConfig(BaseModel):
    name: str
    retrieval_strategies: list[str] = []


class MetricConfig(BaseModel):
    name: str
    threshold: float
    direction: str | None = None
    report_ci: bool | None = None
    report_only: bool | None = None


class GuardrailsConfig(BaseModel):
    # Endpoint type
    names: list[str] | None = None
    # QA type
    scope: dict[str, Any] | None = None
    faithfulness_threshold: float | None = None
    citation_coverage_threshold: float | None = None
    temporal_accuracy_enabled: bool | None = None
    pii_enabled: bool | None = None
    prompt_injection_enabled: bool | None = None
    # Scoring type
    proxy_discrimination: dict[str, Any] | None = None
    calibration: dict[str, Any] | None = None
    stability: dict[str, Any] | None = None
    explainability: dict[str, Any] | None = None
    small_sample: dict[str, Any] | None = None


class OnboardRequest(BaseModel):
    name: str
    id: str
    description: str
    version: str = "1.0.0"
    owner: str
    risk_tier: Literal["experimental", "production_internal", "production_customer_facing"]
    type: Literal["endpoint", "scoring", "qa"]

    # Type-specific (optional)
    endpoint: EndpointConfig | None = None
    model: ModelConfig | None = None
    dataset: DatasetConfig | None = None
    corpus: CorpusConfig | None = None
    frameworks: list[FrameworkConfig] | None = None

    # Common
    guardrails: GuardrailsConfig | None = None
    evaluation_metrics: list[MetricConfig] = []
    compliance_gates: list[str] = Field(default_factory=lambda: [
        "registration",
        "evaluation_harness",
        "pii_validation",
        "guardrail_validation",
        "bias_toxicity",
        "audit_trail",
        "golden_dataset_signoff",
        "prompt_governance",
    ])
    monitoring: dict[str, Any] | None = None

    @field_validator("id")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not SLUG_RE.match(v):
            raise ValueError(
                "id must be lowercase alphanumeric with hyphens (e.g. 'my-solution')"
            )
        return v


class OnboardResponse(BaseModel):
    id: str
    message: str


# ---------------------------------------------------------------------------
# YAML builder
# ---------------------------------------------------------------------------


def _build_manifest(req: OnboardRequest) -> dict[str, Any]:
    """Build the solution.yaml dict from the onboard request."""

    if req.type == "endpoint":
        # Endpoint solutions use flat top-level keys
        manifest: dict[str, Any] = {
            "name": req.name,
            "id": req.id,
            "description": req.description,
            "version": req.version,
            "owner": req.owner,
            "type": "endpoint",
            "risk_tier": req.risk_tier,
        }
        if req.endpoint:
            manifest["endpoint"] = {
                "url": req.endpoint.url,
                "method": req.endpoint.method,
                "timeout_ms": req.endpoint.timeout_ms,
            }
        if req.guardrails and req.guardrails.names:
            manifest["guardrails"] = req.guardrails.names
        else:
            manifest["guardrails"] = ["scope_adherence", "pii_scan", "bias", "toxicity"]
        manifest["tracing"] = {
            "contract_version": "1.0",
            "emits": ["llm_call", "reasoning_step"],
            "format": "opentelemetry",
        }
    else:
        # Scoring and QA use nested solution: key
        category = "ml" if req.type == "scoring" else "ai"
        manifest = {
            "solution": {
                "name": req.name,
                "id": req.id,
                "type": req.type,
                "category": category,
                "version": req.version,
                "description": req.description,
            },
            "owner": req.owner,
            "risk_tier": req.risk_tier,
        }

        if req.type == "scoring":
            if req.dataset:
                manifest["dataset"] = {
                    "source": req.dataset.source,
                    "records": req.dataset.records,
                    "features": req.dataset.features,
                    "target": req.dataset.target,
                    "protected_attributes": (
                        ", ".join(req.dataset.protected_attributes)
                        if req.dataset.protected_attributes
                        else "unknown"
                    ),
                }
            if req.model:
                manifest["model"] = {
                    "type": req.model.type,
                    "framework": req.model.framework,
                    "explainability": req.model.explainability,
                    "training_split": req.model.training_split,
                }
            # Guardrails
            guardrails: dict[str, Any] = {}
            if req.guardrails:
                if req.guardrails.proxy_discrimination:
                    guardrails["proxy_discrimination"] = req.guardrails.proxy_discrimination
                if req.guardrails.calibration:
                    guardrails["calibration"] = req.guardrails.calibration
                if req.guardrails.stability:
                    guardrails["stability"] = req.guardrails.stability
                if req.guardrails.explainability:
                    guardrails["explainability"] = req.guardrails.explainability
                if req.guardrails.small_sample:
                    guardrails["small_sample"] = req.guardrails.small_sample
            if guardrails:
                manifest["guardrails"] = guardrails

        elif req.type == "qa":
            if req.corpus:
                corpus_dict: dict[str, Any] = {"source": req.corpus.source}
                if req.corpus.documents:
                    corpus_dict["documents"] = [
                        {"name": d.name, "format": d.format, "pages": d.pages}
                        for d in req.corpus.documents
                    ]
                manifest["corpus"] = corpus_dict
            # Guardrails
            guardrails_qa: dict[str, Any] = {}
            if req.guardrails:
                if req.guardrails.scope:
                    guardrails_qa["scope"] = req.guardrails.scope
                if req.guardrails.faithfulness_threshold is not None:
                    guardrails_qa["faithfulness_threshold"] = req.guardrails.faithfulness_threshold
                if req.guardrails.citation_coverage_threshold is not None:
                    guardrails_qa["citation_coverage_threshold"] = req.guardrails.citation_coverage_threshold
                if req.guardrails.temporal_accuracy_enabled is not None:
                    guardrails_qa["temporal_accuracy_enabled"] = req.guardrails.temporal_accuracy_enabled
                if req.guardrails.pii_enabled is not None:
                    guardrails_qa["pii_enabled"] = req.guardrails.pii_enabled
                if req.guardrails.prompt_injection_enabled is not None:
                    guardrails_qa["prompt_injection_enabled"] = req.guardrails.prompt_injection_enabled
            if guardrails_qa:
                manifest["guardrails"] = guardrails_qa
            if req.frameworks:
                manifest["frameworks"] = [
                    {"name": f.name, "retrieval_strategies": f.retrieval_strategies}
                    for f in req.frameworks
                ]

    # Evaluation (common)
    if req.evaluation_metrics:
        eval_section: dict[str, Any] = {
            "golden_dataset": "golden_dataset/dataset.json",
            "metrics": [],
        }
        for m in req.evaluation_metrics:
            entry: dict[str, Any] = {"name": m.name, "threshold": m.threshold}
            if m.direction:
                entry["direction"] = m.direction
            if m.report_ci:
                entry["report_ci"] = m.report_ci
            if m.report_only:
                entry["report_only"] = m.report_only
            eval_section["metrics"].append(entry)
        if req.type == "scoring":
            eval_section["holdout_size"] = 0.3
        else:
            eval_section["test_cases"] = len(req.evaluation_metrics) * 5 or 50
        manifest["evaluation"] = eval_section

    # Compliance (common)
    manifest["compliance"] = {
        "deployment_gate": True,
        "evidence_export": True,
        "gates": req.compliance_gates,
    }

    # Monitoring
    if req.monitoring:
        manifest["monitoring"] = req.monitoring

    return manifest


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/solutions/onboard", response_model=OnboardResponse)
def onboard_solution(req: OnboardRequest) -> OnboardResponse:
    """Create a new solution directory with manifest and scaffolding."""

    # Check for duplicates
    solution_dir = SOLUTIONS_DIR / req.id
    if solution_dir.exists():
        raise HTTPException(status_code=409, detail=f"Solution '{req.id}' already exists")

    results_dir = RESULTS_DIR / req.id
    if results_dir.exists():
        raise HTTPException(status_code=409, detail=f"Results for '{req.id}' already exist")

    # Type-specific validation
    if req.type == "endpoint" and not req.endpoint:
        raise HTTPException(status_code=422, detail="Endpoint config required for type 'endpoint'")
    if req.type == "scoring" and (not req.dataset or not req.model):
        raise HTTPException(status_code=422, detail="Dataset and model config required for type 'scoring'")
    if req.type == "qa" and not req.corpus:
        raise HTTPException(status_code=422, detail="Corpus config required for type 'qa'")

    # Build manifest
    manifest = _build_manifest(req)

    # Create directories
    solution_dir.mkdir(parents=True)
    golden_dir = solution_dir / "golden_dataset"
    golden_dir.mkdir()
    results_dir.mkdir(parents=True)

    # Write solution.yaml
    with open(solution_dir / "solution.yaml", "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Write golden dataset scaffold
    golden_dataset = {
        "solution_id": req.id,
        "version": "1.0",
        "description": f"Golden dataset for {req.name}",
        "test_cases": [],
    }
    with open(golden_dir / "dataset.json", "w") as f:
        json.dump(golden_dataset, f, indent=2)

    # Risk tier display mapping
    tier_display = {
        "production_customer_facing": "Customer-Facing",
        "production_internal": "Internal",
        "experimental": "Experimental",
    }
    category = "ml" if req.type == "scoring" else "ai"
    now = datetime.now(AEST).strftime("%Y-%m-%d %H:%M AEST")

    # Write results/summary.json
    summary = {
        "id": req.id,
        "name": req.name,
        "description": req.description,
        "category": category,
        "owner": req.owner,
        "riskTier": tier_display.get(req.risk_tier, req.risk_tier),
        "guardrailsSummary": "Not evaluated",
        "evalScore": None,
        "gateResult": "pending",
        "health": "pending",
        "lastRun": now,
        "lastTested": None,
    }
    with open(results_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return OnboardResponse(
        id=req.id,
        message=f"Solution '{req.name}' onboarded successfully. Run the compliance gate to activate.",
    )
