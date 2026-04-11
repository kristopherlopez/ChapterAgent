"""Guardrail framework — base interface and result model."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field


class GuardrailResult(BaseModel):
    """Result of a single guardrail check."""
    name: str
    result: Literal["pass", "warn", "fail"]
    detail: str
    elapsed_ms: float = Field(default=0.0, ge=0.0)
    score: float | None = None


class Guardrail(ABC):
    """Base guardrail — all guardrails implement this interface.

    Usage:
        guardrail = PIIGuardrail()
        result = await guardrail.check(input="...", output="...", context=[...])
    """

    name: str = "base"
    description: str = ""

    async def check(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> GuardrailResult:
        """Run the guardrail check with timing."""
        start = time.perf_counter()
        result = await self._check(input=input, output=output, context=context)
        result.elapsed_ms = (time.perf_counter() - start) * 1000
        return result

    @abstractmethod
    async def _check(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> GuardrailResult:
        """Implement the guardrail logic. Override this."""
        ...
