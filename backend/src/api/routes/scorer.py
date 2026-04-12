"""Scorer API — interactive credit default scoring endpoint."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

SOLUTIONS_DIR = Path(__file__).resolve().parents[4] / "solutions"

# Cached scorer instance (trained once on first request)
_scorer_cache: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ScoreRequest(BaseModel):
    features: dict[str, Any]
    applicant_id: str = ""


class ProbeRequest(BaseModel):
    base_profile: dict[str, Any]
    variants: list[dict[str, Any]]
    tolerance: float = 0.02


class GuardrailOut(BaseModel):
    name: str
    status: str
    detail: str | None = None


class SHAPContributorOut(BaseModel):
    feature: str
    direction: str
    shap_value: float


class ScoreResult(BaseModel):
    scoring_id: str
    applicant_id: str
    default_probability: float
    risk_band: str
    recommendation: str
    shap_contributors: list[SHAPContributorOut]
    baseline_probability: float
    guardrails: list[GuardrailOut]
    latency_ms: int
    blocked: bool


class ProbeResult(BaseModel):
    results: list[ScoreResult]
    score_difference: float
    tolerance: float
    discrimination_pass: bool


# ---------------------------------------------------------------------------
# Demo fallback responses (used when scorer/dataset unavailable)
# ---------------------------------------------------------------------------

DEMO_PROFILES: dict[str, dict[str, Any]] = {
    "low_risk": {
        "LIMIT_BAL": 300000, "PAY_0": 0, "PAY_2": 0, "PAY_3": 0,
        "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
        "BILL_AMT1": 50000, "BILL_AMT2": 48000, "BILL_AMT3": 45000,
        "BILL_AMT4": 42000, "BILL_AMT5": 40000, "BILL_AMT6": 38000,
    },
    "high_risk": {
        "LIMIT_BAL": 50000, "PAY_0": 3, "PAY_2": 2, "PAY_3": 2,
        "PAY_4": 2, "PAY_5": 2, "PAY_6": 2,
        "BILL_AMT1": 49000, "BILL_AMT2": 48000, "BILL_AMT3": 47000,
        "BILL_AMT4": 46000, "BILL_AMT5": 45000, "BILL_AMT6": 44000,
    },
    "deteriorating": {
        "LIMIT_BAL": 100000, "PAY_0": 3, "PAY_2": 2, "PAY_3": 1,
        "PAY_4": 0, "PAY_5": 0, "PAY_6": -1,
        "BILL_AMT1": 95000, "BILL_AMT2": 85000, "BILL_AMT3": 70000,
        "BILL_AMT4": 55000, "BILL_AMT5": 40000, "BILL_AMT6": 30000,
    },
}

DEMO_RESPONSES: dict[str, ScoreResult] = {
    "low_risk": ScoreResult(
        scoring_id="SCR-DEMO-001", applicant_id="DEMO-001",
        default_probability=0.08, risk_band="LOW",
        recommendation="No action",
        shap_contributors=[
            SHAPContributorOut(feature="PAY_0", direction="decreases_risk", shap_value=-0.09),
            SHAPContributorOut(feature="LIMIT_BAL", direction="decreases_risk", shap_value=-0.06),
            SHAPContributorOut(feature="BILL_AMT1", direction="increases_risk", shap_value=0.02),
            SHAPContributorOut(feature="PAY_2", direction="decreases_risk", shap_value=-0.01),
        ],
        baseline_probability=0.22,
        guardrails=[
            GuardrailOut(name="Discrimination Check", status="pass", detail="DI ratio: 0.93"),
            GuardrailOut(name="Calibration Check", status="pass", detail="Brier: 0.14"),
            GuardrailOut(name="Stability Check", status="pass", detail="PSI: 0.08"),
            GuardrailOut(name="Explainability Check", status="pass", detail="SHAP coverage: 100%"),
        ],
        latency_ms=45, blocked=False,
    ),
    "high_risk": ScoreResult(
        scoring_id="SCR-DEMO-002", applicant_id="DEMO-002",
        default_probability=0.72, risk_band="VERY_HIGH",
        recommendation="Immediate intervention",
        shap_contributors=[
            SHAPContributorOut(feature="PAY_0", direction="increases_risk", shap_value=0.22),
            SHAPContributorOut(feature="PAY_2", direction="increases_risk", shap_value=0.14),
            SHAPContributorOut(feature="LIMIT_BAL", direction="increases_risk", shap_value=0.08),
            SHAPContributorOut(feature="BILL_AMT1", direction="increases_risk", shap_value=0.06),
        ],
        baseline_probability=0.22,
        guardrails=[
            GuardrailOut(name="Discrimination Check", status="pass", detail="DI ratio: 0.91"),
            GuardrailOut(name="Calibration Check", status="pass", detail="Brier: 0.14"),
            GuardrailOut(name="Stability Check", status="pass", detail="PSI: 0.08"),
            GuardrailOut(name="Explainability Check", status="pass", detail="SHAP coverage: 100%"),
        ],
        latency_ms=48, blocked=False,
    ),
    "deteriorating": ScoreResult(
        scoring_id="SCR-DEMO-003", applicant_id="DEMO-003",
        default_probability=0.45, risk_band="HIGH",
        recommendation="Proactive outreach",
        shap_contributors=[
            SHAPContributorOut(feature="PAY_0", direction="increases_risk", shap_value=0.18),
            SHAPContributorOut(feature="PAY_2", direction="increases_risk", shap_value=0.10),
            SHAPContributorOut(feature="LIMIT_BAL", direction="decreases_risk", shap_value=-0.04),
            SHAPContributorOut(feature="BILL_AMT1", direction="increases_risk", shap_value=0.08),
        ],
        baseline_probability=0.22,
        guardrails=[
            GuardrailOut(name="Discrimination Check", status="pass", detail="DI ratio: 0.89"),
            GuardrailOut(name="Calibration Check", status="pass", detail="Brier: 0.14"),
            GuardrailOut(name="Stability Check", status="pass", detail="PSI: 0.08"),
            GuardrailOut(name="Explainability Check", status="pass", detail="SHAP coverage: 100%"),
        ],
        latency_ms=42, blocked=False,
    ),
}


# ---------------------------------------------------------------------------
# Scorer loader
# ---------------------------------------------------------------------------


def _get_scorer():
    """Lazily import and train the credit default scorer."""
    if "scorer" in _scorer_cache:
        return _scorer_cache["scorer"]

    solution_dir = SOLUTIONS_DIR / "credit-default-scorer"
    src_dir = solution_dir / "src"

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from scorer import CreditDefaultScorer

        dataset_path = solution_dir / "data" / "UCI_Credit_Card.csv"
        if not dataset_path.exists():
            return None

        instance = CreditDefaultScorer()
        instance.train(str(dataset_path))
        _scorer_cache["scorer"] = instance
        return instance
    except Exception:
        return None


def _scoring_response_to_result(response, latency_ms: int) -> ScoreResult:
    """Convert a ScoringResponse to a ScoreResult for the API."""
    return ScoreResult(
        scoring_id=response.scoring_id,
        applicant_id=response.applicant_id,
        default_probability=response.output.default_probability,
        risk_band=response.output.risk_band,
        recommendation=response.output.decision_recommendation,
        shap_contributors=[
            SHAPContributorOut(
                feature=c.feature,
                direction=c.direction,
                shap_value=c.shap_value,
            )
            for c in response.explainability.top_contributors
        ],
        baseline_probability=response.explainability.baseline_probability,
        guardrails=[
            GuardrailOut(name="Discrimination Check", status=response.guardrail_results.discrimination_check),
            GuardrailOut(name="Calibration Check", status=response.guardrail_results.calibration_check),
            GuardrailOut(name="Stability Check", status=response.guardrail_results.stability_check),
            GuardrailOut(name="Explainability Check", status=response.guardrail_results.explainability_check),
        ],
        latency_ms=latency_ms,
        blocked=any(
            g in ("FAIL", "fail")
            for g in [
                response.guardrail_results.discrimination_check,
                response.guardrail_results.calibration_check,
                response.guardrail_results.stability_check,
                response.guardrail_results.explainability_check,
            ]
        ),
    )


def _demo_score(features: dict[str, Any]) -> ScoreResult:
    """Return a demo response based on feature patterns."""
    pay_0 = features.get("PAY_0", 0)
    limit = features.get("LIMIT_BAL", 100000)

    if pay_0 >= 3:
        base = DEMO_RESPONSES["high_risk"].model_copy()
    elif pay_0 >= 1 or limit < 80000:
        base = DEMO_RESPONSES["deteriorating"].model_copy()
    else:
        base = DEMO_RESPONSES["low_risk"].model_copy()

    return base


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/score/{solution_id}", response_model=ScoreResult)
async def score(solution_id: str, req: ScoreRequest):
    if solution_id != "credit-default-scorer":
        raise HTTPException(status_code=404, detail="Solution not found")

    start = time.perf_counter()
    scorer = _get_scorer()

    if scorer is None:
        # Demo fallback
        await _simulate_latency()
        result = _demo_score(req.features)
        result.applicant_id = req.applicant_id or result.applicant_id
        return result

    response = scorer.score(req.features, applicant_id=req.applicant_id)
    latency_ms = int((time.perf_counter() - start) * 1000)
    return _scoring_response_to_result(response, latency_ms)


@router.post("/score/{solution_id}/probe", response_model=ProbeResult)
async def probe(solution_id: str, req: ProbeRequest):
    if solution_id != "credit-default-scorer":
        raise HTTPException(status_code=404, detail="Solution not found")

    start = time.perf_counter()
    scorer = _get_scorer()

    results: list[ScoreResult] = []

    for i, variant in enumerate(req.variants):
        profile = {**req.base_profile, **variant}

        if scorer is None:
            result = _demo_score(profile)
            result.applicant_id = variant.get("label", f"PROBE-{i+1}")
            # Simulate slight score difference for demo
            if i == 1:
                result.default_probability = round(result.default_probability + 0.09, 4)
        else:
            response = scorer.score(profile, applicant_id=variant.get("label", f"PROBE-{i+1}"))
            latency_ms = int((time.perf_counter() - start) * 1000)
            result = _scoring_response_to_result(response, latency_ms)

        results.append(result)

    probabilities = [r.default_probability for r in results]
    score_diff = round(max(probabilities) - min(probabilities), 4)

    return ProbeResult(
        results=results,
        score_difference=score_diff,
        tolerance=req.tolerance,
        discrimination_pass=score_diff <= req.tolerance,
    )


async def _simulate_latency():
    """Simulate realistic latency for demo mode."""
    import asyncio
    await asyncio.sleep(0.5)
