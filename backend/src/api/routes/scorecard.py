"""Multi-platform scorecard API routes."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["scorecard"])

ROOT = Path(__file__).resolve().parents[4]
RESULTS_DIR = ROOT / "results"


@router.get("/scorecard")
def get_scorecard() -> list[dict]:
    """Get the framework comparison scorecard."""
    # Look for scorecard in multi-platform-agent results
    scorecard_path = RESULTS_DIR / "multi-platform-agent" / "scorecard.json"
    if not scorecard_path.exists():
        raise HTTPException(status_code=404, detail="Scorecard not found")

    with open(scorecard_path) as f:
        return json.load(f)
