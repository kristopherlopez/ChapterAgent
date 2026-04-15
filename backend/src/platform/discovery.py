"""Solution manifest discovery — reads solution.yaml files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ScopeConfig(BaseModel):
    """Scope enforcement configuration."""
    level: int = Field(
        default=1, ge=1, le=3,
        description="Scope level: 1=strict, 2=contextual, 3=open",
    )
    topic_graph: str | None = None
    refusal_message: str = "I can only answer questions about the provided documents."


class GuardrailConfig(BaseModel):
    """Guardrail-specific configuration."""
    scope: ScopeConfig = Field(default_factory=ScopeConfig)
    faithfulness_threshold: float = Field(default=0.90, ge=0.0, le=1.0)
    citation_coverage_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    temporal_accuracy_enabled: bool = True
    pii_enabled: bool = True
    prompt_injection_enabled: bool = True


class EvaluationMetric(BaseModel):
    """Single evaluation metric configuration."""
    name: str
    threshold: float
    direction: str = "higher_is_better"


class EvaluationConfig(BaseModel):
    """Evaluation harness configuration."""
    golden_dataset: str = "golden_dataset/dataset.json"
    test_cases: int = 50
    metrics: list[EvaluationMetric] = Field(default_factory=list)


class ComplianceConfig(BaseModel):
    """Compliance gate configuration."""
    deployment_gate: bool = True
    evidence_export: bool = True
    gates: list[str] = Field(default_factory=list)


class CorpusDocument(BaseModel):
    """Document in the solution corpus."""
    name: str
    format: str = "pdf"
    pages: int | None = None


class CorpusConfig(BaseModel):
    """Document corpus configuration."""
    source: str = ""
    documents: list[CorpusDocument] = Field(default_factory=list)
    topic_graph: str | None = None


class FrameworkConfig(BaseModel):
    """Framework implementation configuration."""
    name: str
    retrieval_strategies: list[str] = Field(default_factory=list)


class EndpointConfig(BaseModel):
    """External endpoint configuration for endpoint-type solutions."""
    url: str = ""
    method: str = "POST"
    timeout_ms: int = 30000


class TracingConfig(BaseModel):
    """Tracing contract configuration.

    Defines how a solution exposes execution traces. Two modes:

    - **inline** (demo): The endpoint includes a ``trace`` field in its JSON
      response body conforming to the platform trace schema.  The compliance
      runner can validate traces without extra infrastructure.
    - **opentelemetry** (production): The solution pushes spans to a
      platform-provided OTel collector (e.g. LangFuse).  More realistic at
      PetSure Australia scale where the Governance Portal may not control endpoint response schemas.
    """
    contract_version: str = "1.0"
    format: str = "inline"  # "inline" | "opentelemetry"
    emits: list[str] = Field(default_factory=list)
    required_fields: list[str] = Field(
        default_factory=lambda: ["query", "retrieval", "generation", "guardrails", "response"],
    )


class SolutionManifest(BaseModel):
    """Complete solution manifest — parsed from solution.yaml."""
    name: str
    id: str
    description: str = ""
    version: str = "1.0.0"
    owner: str = "Governance Portal Team"
    type: str = "embedded"
    risk_tier: str = "production_internal"
    endpoint: EndpointConfig | None = None
    tracing: TracingConfig = Field(default_factory=TracingConfig)
    guardrails: GuardrailConfig | list[str] = Field(default_factory=list)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)
    corpus: CorpusConfig | None = None
    frameworks: list[FrameworkConfig] = Field(default_factory=list)

    @property
    def guardrail_names(self) -> list[str]:
        """Get guardrail names regardless of config format."""
        if isinstance(self.guardrails, list):
            return self.guardrails
        return [
            "scope_adherence",
            "pii_scan",
            "faithfulness",
            "bias",
            "toxicity",
            "citation_coverage",
            "temporal_accuracy",
            "prompt_injection",
        ]


def load_solution_manifest(solution_dir: Path) -> SolutionManifest:
    """Load a single solution manifest from a directory."""
    manifest_path = solution_dir / "solution.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No solution.yaml found in {solution_dir}")

    with open(manifest_path) as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    # Handle nested 'solution' key (some manifests wrap fields under 'solution:')
    if "solution" in raw and isinstance(raw["solution"], dict):
        solution_data = raw.pop("solution")
        raw = {**solution_data, **raw}

    return SolutionManifest.model_validate(raw)


def discover_solutions(solutions_dir: Path) -> list[SolutionManifest]:
    """Discover all solutions by reading their manifests."""
    manifests = []
    if not solutions_dir.exists():
        return manifests

    for child in sorted(solutions_dir.iterdir()):
        if child.is_dir() and (child / "solution.yaml").exists():
            try:
                manifests.append(load_solution_manifest(child))
            except Exception:
                continue

    return manifests
