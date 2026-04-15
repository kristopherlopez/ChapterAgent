"""Compliance event logger — Layer 2 production monitoring.

Logs every per-response compliance event to a JSONL file for audit trail
and production monitoring dashboards.

Usage:
    from src.platform.compliance.logger import ComplianceLogger

    logger = ComplianceLogger(solution_id="petsure-policy-qa")
    logger.log_response(
        query="What was net profit?",
        guardrail_results=results,
        latency_ms=187,
        blocked=False,
    )
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.platform.guardrails.base import GuardrailResult


class ComplianceEvent(BaseModel):
    """A single compliance event from a production response."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    solution_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    query_hash: str = ""  # SHA256 of query (privacy: don't log raw query)
    passed: bool
    blocked: bool
    guardrails: list[dict[str, Any]] = Field(default_factory=list)
    guardrails_passed: int = 0
    guardrails_total: int = 0
    latency_ms: int = 0
    regenerated: bool = False
    regeneration_passed: bool | None = None


class ComplianceLogger:
    """Logs compliance events to JSONL files.

    Each solution gets its own log file at:
        logs/compliance/{solution_id}/events.jsonl

    Events are appended — the log grows over the solution's lifetime.
    """

    def __init__(
        self,
        solution_id: str,
        log_dir: Path | None = None,
    ):
        self.solution_id = solution_id
        if log_dir is None:
            log_dir = (
                Path(__file__).resolve().parents[3]
                / "logs"
                / "compliance"
                / solution_id
            )
        self._log_dir = log_dir
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._events_path = self._log_dir / "events.jsonl"

    def log_response(
        self,
        *,
        query: str,
        guardrail_results: list[GuardrailResult],
        latency_ms: int = 0,
        blocked: bool = False,
        regenerated: bool = False,
        regeneration_passed: bool | None = None,
    ) -> ComplianceEvent:
        """Log a compliance event for a production response.

        Args:
            query: The user's query (hashed for privacy).
            guardrail_results: Results from the guardrail runner.
            latency_ms: Total response latency in milliseconds.
            blocked: Whether the response was blocked.
            regenerated: Whether the response was regenerated after failure.
            regeneration_passed: Whether the regenerated response passed.

        Returns:
            The compliance event that was logged.
        """
        import hashlib

        passed = all(g.result == "pass" for g in guardrail_results)
        guardrails_passed = sum(1 for g in guardrail_results if g.result == "pass")

        event = ComplianceEvent(
            solution_id=self.solution_id,
            query_hash=hashlib.sha256(query.encode()).hexdigest()[:16],
            passed=passed,
            blocked=blocked,
            guardrails=[
                {
                    "name": g.name,
                    "result": g.result,
                    "detail": g.detail,
                    "elapsed_ms": round(g.elapsed_ms, 1),
                    "score": g.score,
                }
                for g in guardrail_results
            ],
            guardrails_passed=guardrails_passed,
            guardrails_total=len(guardrail_results),
            latency_ms=latency_ms,
            regenerated=regenerated,
            regeneration_passed=regeneration_passed,
        )

        self._append(event)
        return event

    def _append(self, event: ComplianceEvent) -> None:
        """Append an event to the JSONL log."""
        with open(self._events_path, "a") as f:
            f.write(event.model_dump_json() + "\n")

    def get_health_summary(self, last_n: int = 100) -> dict[str, Any]:
        """Compute compliance health from the last N events.

        Returns a summary suitable for the production monitoring dashboard.
        """
        events = self._read_recent(last_n)
        if not events:
            return {
                "total_interactions": 0,
                "pass_rate": 0.0,
                "status": "unknown",
            }

        total = len(events)
        passed = sum(1 for e in events if e.get("passed"))
        blocked = sum(1 for e in events if e.get("blocked"))
        regenerated = sum(1 for e in events if e.get("regenerated"))

        pass_rate = passed / total if total else 0

        # Aggregate per-guardrail pass rates
        guardrail_stats: dict[str, dict] = {}
        for event in events:
            for g in event.get("guardrails", []):
                name = g.get("name", "")
                if name not in guardrail_stats:
                    guardrail_stats[name] = {"passed": 0, "total": 0}
                guardrail_stats[name]["total"] += 1
                if g.get("result") == "pass":
                    guardrail_stats[name]["passed"] += 1

        # Health status
        if pass_rate >= 0.98:
            status = "green"
        elif pass_rate >= 0.90:
            status = "amber"
        else:
            status = "red"

        return {
            "total_interactions": total,
            "pass_rate": round(pass_rate, 4),
            "passed": passed,
            "blocked": blocked,
            "regenerated": regenerated,
            "status": status,
            "guardrail_breakdown": {
                name: {
                    "pass_rate": round(
                        stats["passed"] / stats["total"], 4
                    ) if stats["total"] else 0,
                    **stats,
                }
                for name, stats in guardrail_stats.items()
            },
        }

    def _read_recent(self, n: int) -> list[dict]:
        """Read the last N events from the JSONL log."""
        if not self._events_path.exists():
            return []

        events = []
        with open(self._events_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))

        return events[-n:]
