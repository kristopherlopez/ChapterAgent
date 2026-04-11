"""Solution registry and detail API routes."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["solutions"])

# Project root — results are at {ROOT}/results/{solution_id}/
ROOT = Path(__file__).resolve().parents[4]  # backend/src/api/routes -> project root
RESULTS_DIR = ROOT / "results"


def _load_json(path: Path) -> dict | list:
    """Load a JSON file, raising 404 if not found."""
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path.name}")
    with open(path) as f:
        return json.load(f)


@router.get("/solutions")
def list_solutions() -> list[dict]:
    """List all registered solutions with summary data."""
    summaries = []
    if not RESULTS_DIR.exists():
        return summaries

    for child in sorted(RESULTS_DIR.iterdir()):
        summary_path = child / "summary.json"
        if child.is_dir() and summary_path.exists():
            summaries.append(_load_json(summary_path))

    return summaries


@router.get("/solutions/{solution_id}")
def get_solution_detail(solution_id: str) -> dict:
    """Get full detail for a solution: summary + guardrails + evaluation + compliance."""
    solution_dir = RESULTS_DIR / solution_id
    if not solution_dir.exists():
        raise HTTPException(status_code=404, detail=f"Solution not found: {solution_id}")

    summary = _load_json(solution_dir / "summary.json")

    gr_path = solution_dir / "guardrails.json"
    ev_path = solution_dir / "evaluation.json"
    co_path = solution_dir / "compliance.json"

    guardrails = _load_json(gr_path) if gr_path.exists() else []
    evaluation = _load_json(ev_path) if ev_path.exists() else []
    compliance = _load_json(co_path) if co_path.exists() else {}

    return {
        **summary,
        "guardrails": guardrails,
        "evaluation": evaluation,
        "complianceGate": compliance,
    }
