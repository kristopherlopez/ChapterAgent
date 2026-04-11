"""Evidence export API routes."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(tags=["evidence"])

ROOT = Path(__file__).resolve().parents[4]
RESULTS_DIR = ROOT / "results"


@router.get("/evidence/{solution_id}")
def get_evidence(solution_id: str) -> dict:
    """Get the full evidence package for a solution."""
    evidence_path = RESULTS_DIR / solution_id / "evidence.json"
    if not evidence_path.exists():
        raise HTTPException(status_code=404, detail=f"Evidence not found for: {solution_id}")

    with open(evidence_path) as f:
        return json.load(f)


@router.get("/evidence/{solution_id}/download")
def download_evidence(solution_id: str) -> JSONResponse:
    """Download the evidence package as a JSON file."""
    evidence_path = RESULTS_DIR / solution_id / "evidence.json"
    if not evidence_path.exists():
        raise HTTPException(status_code=404, detail=f"Evidence not found for: {solution_id}")

    with open(evidence_path) as f:
        data = json.load(f)

    return JSONResponse(
        content=data,
        headers={
            "Content-Disposition": f"attachment; filename=evidence-{solution_id}.json",
        },
    )
