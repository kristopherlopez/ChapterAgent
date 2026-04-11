"""Structured JSON trace logger."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    """A single step in an execution trace."""
    step: int
    label: str
    durationMs: int | float
    detail: str | None = None


class Trace(BaseModel):
    """Complete execution trace for a solution run."""
    solution_id: str
    scenario: str = "live"
    question: str = ""
    steps: list[TraceStep] = Field(default_factory=list)


class TraceLogger:
    """Builds structured execution traces.

    Usage:
        logger = TraceLogger(solution_id="rag-policy-qa")
        logger.log_step(1, "Query received", 0)
        logger.log_step(2, "Context retrieval", 120, detail="3 chunks retrieved")
        trace = logger.to_trace()
        logger.save(Path("traces/rag-policy-qa/run_001.json"))
    """

    def __init__(self, *, solution_id: str, scenario: str = "live", question: str = ""):
        self.solution_id = solution_id
        self.scenario = scenario
        self.question = question
        self._steps: list[TraceStep] = []

    def log_step(
        self,
        step: int,
        label: str,
        duration_ms: int | float,
        detail: str | None = None,
    ) -> None:
        """Add a step to the trace."""
        self._steps.append(
            TraceStep(step=step, label=label, durationMs=duration_ms, detail=detail)
        )

    def to_trace(self) -> Trace:
        """Build the trace object."""
        return Trace(
            solution_id=self.solution_id,
            scenario=self.scenario,
            question=self.question,
            steps=list(self._steps),
        )

    def save(self, path: Path) -> None:
        """Save the trace to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        trace = self.to_trace()
        with open(path, "w") as f:
            json.dump(trace.model_dump(), f, indent=2)
