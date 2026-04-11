"""Compliance dashboard API routes."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(tags=["compliance"])

ROOT = Path(__file__).resolve().parents[4]
RESULTS_DIR = ROOT / "results"


@router.get("/compliance/dashboard")
def compliance_dashboard() -> dict:
    """Aggregate compliance health across all solutions."""
    solutions = []
    passing = 0
    failing = 0
    warning = 0

    if not RESULTS_DIR.exists():
        return {"passing": 0, "failing": 0, "warning": 0, "total": 0, "solutions": []}

    for child in sorted(RESULTS_DIR.iterdir()):
        summary_path = child / "summary.json"
        if child.is_dir() and summary_path.exists():
            with open(summary_path) as f:
                summary = json.load(f)
            health = summary.get("health", "pass")
            if health == "pass":
                passing += 1
            elif health == "fail":
                failing += 1
            else:
                warning += 1
            solutions.append({
                "id": summary.get("id"),
                "name": summary.get("name"),
                "health": health,
                "gateResult": summary.get("gateResult"),
            })

    return {
        "passing": passing,
        "failing": failing,
        "warning": warning,
        "total": passing + failing + warning,
        "solutions": solutions,
    }
