"""Golden dataset loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """A single test case from the golden dataset."""
    case_id: str
    query_type: str
    question: str
    expected_answer: str | None = None
    expected_behaviour: str = "answer_with_citation"
    expected_grounding: str = "corpus"
    expected_citations: list[dict[str, Any]] = Field(default_factory=list)
    scope_level: int = 1
    key_metrics: list[str] = Field(default_factory=list)


class GoldenDataset(BaseModel):
    """A golden dataset for evaluation."""
    solution_id: str = ""
    version: str = "1.0"
    test_cases: list[TestCase] = Field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.test_cases)

    def by_type(self, query_type: str) -> list[TestCase]:
        """Filter test cases by query type."""
        return [tc for tc in self.test_cases if tc.query_type == query_type]


class GoldenDatasetLoader:
    """Loads golden datasets from JSON files.

    Usage:
        loader = GoldenDatasetLoader()
        dataset = loader.load(Path("solutions/qa-agent/golden_dataset/dataset.json"))
    """

    @staticmethod
    def load(path: Path) -> GoldenDataset:
        """Load a golden dataset from a JSON file."""
        with open(path) as f:
            raw = json.load(f)

        if isinstance(raw, list):
            return GoldenDataset(test_cases=[TestCase.model_validate(tc) for tc in raw])

        return GoldenDataset.model_validate(raw)
