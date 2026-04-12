"""Compliance gate checks — 8 automated checks that run before deployment."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import UTC, datetime


class CheckResult(BaseModel):
    """Result of a single compliance gate check."""
    check: str
    policy_id: str
    policy: str
    status: Literal["PASS", "FAIL"]
    evidence: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    @property
    def passed(self) -> bool:
        return self.status == "PASS"
