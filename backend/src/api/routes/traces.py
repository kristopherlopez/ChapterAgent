"""Observability trace API routes."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["traces"])

ROOT = Path(__file__).resolve().parents[4]
TRACES_DIR = ROOT / "traces"


@router.get("/traces/{solution_id}")
def get_traces(solution_id: str) -> list[dict]:
    """Get the default trace (run_001) for a solution."""
    trace_dir = TRACES_DIR / solution_id
    if not trace_dir.exists():
        raise HTTPException(status_code=404, detail=f"Traces not found for: {solution_id}")

    # Return the first/default trace
    default_trace = trace_dir / "run_001.json"
    if not default_trace.exists():
        # Try to find any trace file
        traces = sorted(trace_dir.glob("*.json"))
        if not traces:
            raise HTTPException(status_code=404, detail="No trace files found")
        default_trace = traces[0]

    with open(default_trace) as f:
        return json.load(f)


@router.get("/traces/{solution_id}/scenarios")
def list_trace_scenarios(solution_id: str) -> list[dict]:
    """List all available trace scenarios for a solution."""
    trace_dir = TRACES_DIR / solution_id
    if not trace_dir.exists():
        raise HTTPException(status_code=404, detail=f"Traces not found for: {solution_id}")

    scenarios = []
    for trace_file in sorted(trace_dir.glob("*.json")):
        scenarios.append({
            "run_id": trace_file.stem,
            "filename": trace_file.name,
        })

    return scenarios


@router.get("/traces/{solution_id}/{run_id}")
def get_trace_by_run(solution_id: str, run_id: str) -> list[dict]:
    """Get a specific trace run for a solution."""
    trace_file = TRACES_DIR / solution_id / f"{run_id}.json"
    if not trace_file.exists():
        raise HTTPException(status_code=404, detail=f"Trace not found: {run_id}")

    with open(trace_file) as f:
        return json.load(f)
