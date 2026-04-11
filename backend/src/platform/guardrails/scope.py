"""Scope containment guardrail — topic graph and scope level enforcement."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.platform.guardrails.base import Guardrail, GuardrailResult


class ScopeGuardrail(Guardrail):
    """Enforces scope boundaries using a topic graph and scope level.

    Scope levels:
        1 (Strict): Only answers grounded in the document corpus.
        2 (Contextual): Corpus + general knowledge for interpretation.
        3 (Open): Corpus as primary source, general knowledge permitted.

    The topic graph maps known topics to keywords. Queries that don't match
    any topic are considered out-of-scope at levels 1 and 2.
    """

    name = "Scope Containment"
    description = "Checks if queries fall within the configured topic scope"

    def __init__(
        self,
        *,
        scope_level: int = 1,
        topic_graph: dict[str, Any] | None = None,
        topic_graph_path: Path | str | None = None,
        refusal_message: str = "I can only answer questions about the provided documents.",
    ):
        self.scope_level = scope_level
        self.refusal_message = refusal_message

        if topic_graph is not None:
            self._topics = topic_graph.get("topics", topic_graph)
        elif topic_graph_path is not None:
            with open(topic_graph_path) as f:
                data = json.load(f)
            self._topics = data.get("topics", data)
        else:
            self._topics = {}

        # Pre-build keyword index for fast lookup
        self._keyword_index: dict[str, str] = {}
        for topic_name, topic_data in self._topics.items():
            for kw in topic_data.get("keywords", []):
                self._keyword_index[kw.lower()] = topic_name

    def _classify_query(self, query: str) -> tuple[bool, str | None]:
        """Check if query maps to a known topic."""
        query_lower = query.lower()
        for keyword, topic in self._keyword_index.items():
            if keyword in query_lower:
                return True, topic
        return False, None

    def _is_financial_advice(self, query: str) -> bool:
        """Check if the query requests financial advice."""
        advice_patterns = [
            "should i buy", "should i sell", "should i invest",
            "is it a good investment", "recommend", "would you advise",
            "good time to buy", "worth investing",
        ]
        query_lower = query.lower()
        return any(p in query_lower for p in advice_patterns)

    def _is_opinion_request(self, query: str) -> bool:
        """Check if the query requests opinions or analysis."""
        opinion_patterns = [
            "what do you think", "in your opinion", "do you believe",
            "what's your view", "your assessment",
        ]
        query_lower = query.lower()
        return any(p in query_lower for p in opinion_patterns)

    async def _check(
        self,
        *,
        input: str,
        output: str,
        context: list[str] | None = None,
    ) -> GuardrailResult:
        # Financial advice and opinions are always refused
        if self._is_financial_advice(input):
            return GuardrailResult(
                name=self.name,
                result="fail",
                detail=f"Financial advice request — always out of scope. {self.refusal_message}",
                score=0.0,
            )

        if self._is_opinion_request(input):
            return GuardrailResult(
                name=self.name,
                result="fail",
                detail=f"Opinion request — always out of scope. {self.refusal_message}",
                score=0.0,
            )

        in_scope, matched_topic = self._classify_query(input)

        if in_scope:
            return GuardrailResult(
                name=self.name,
                result="pass",
                detail=f"Query mapped to topic: {matched_topic}",
                score=1.0,
            )

        # Out of scope behavior depends on scope level
        if self.scope_level == 1:
            return GuardrailResult(
                name=self.name,
                result="fail",
                detail=f"Query does not map to any known topic. {self.refusal_message}",
                score=0.0,
            )
        elif self.scope_level == 2:
            return GuardrailResult(
                name=self.name,
                result="warn",
                detail="Query outside corpus — general knowledge answer flagged",
                score=0.5,
            )
        else:  # Level 3 — open
            return GuardrailResult(
                name=self.name,
                result="pass",
                detail="Query outside corpus — open scope permits general knowledge",
                score=0.8,
            )
