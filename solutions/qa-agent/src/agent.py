"""Q&A Agent — full pipeline: scope check, retrieve, generate, guardrails."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

try:
    from solutions.qa_agent.src.generate import QAGenerator, QAResponse
    from solutions.qa_agent.src.retrieve import HybridRetriever, RetrievedChunk
except ImportError:
    from generate import QAGenerator, QAResponse  # type: ignore[no-redef]
    from retrieve import HybridRetriever, RetrievedChunk  # type: ignore[no-redef]


def _create_generator(framework: str = "openai") -> QAGenerator:
    """Factory: create the right generator for the chosen framework.

    Frameworks:
        openai:        OpenAI SDK (gpt-4o)
        claude:        Claude Agent SDK with tool use (agentic)
        claude-direct: Anthropic SDK direct call (no tool use)
        langchain:     LangChain/LangGraph
    """
    if framework == "openai":
        return QAGenerator()
    elif framework == "claude":
        try:
            from solutions.qa_agent.src.generate_claude import (
                ClaudeAgentGenerator,
            )
        except ImportError:
            from generate_claude import ClaudeAgentGenerator  # type: ignore[no-redef]
        return ClaudeAgentGenerator()
    elif framework == "claude-direct":
        try:
            from solutions.qa_agent.src.generate_claude import (
                ClaudeDirectGenerator,
            )
        except ImportError:
            from generate_claude import ClaudeDirectGenerator  # type: ignore[no-redef]
        return ClaudeDirectGenerator()
    elif framework == "langchain":
        try:
            from solutions.qa_agent.src.generate_langchain import (
                LangChainQAGenerator,
            )
        except ImportError:
            from generate_langchain import LangChainQAGenerator  # type: ignore[no-redef]
        return LangChainQAGenerator()
    else:
        raise ValueError(
            f"Unknown framework: {framework!r}. "
            "Use 'openai', 'claude', 'claude-direct', "
            "or 'langchain'."
        )


class QAAgent:
    """CBA Annual Report Q&A Agent.

    Full pipeline: scope check -> retrieve -> generate -> guardrails.
    Can run with or without the guardrail runner (for standalone use).

    Usage:
        agent = QAAgent.from_solution_dir(Path("solutions/qa-agent"))
        response = await agent.answer("What was CBA's net interest margin?")
    """

    def __init__(
        self,
        *,
        retriever: HybridRetriever,
        generator: QAGenerator | None = None,
        topic_graph: dict[str, Any] | None = None,
        scope_level: int = 1,
        refusal_message: str = "I can only answer questions about CBA's 2025 Annual Report.",
    ):
        self.retriever = retriever
        self.generator = generator or QAGenerator()
        self.topic_graph = topic_graph
        self.scope_level = scope_level
        self.refusal_message = refusal_message
        self._query_counter = 0

    @classmethod
    def from_solution_dir(
        cls,
        solution_dir: Path,
        *,
        framework: str = "openai",
    ) -> QAAgent:
        """Create agent from the solution directory structure.

        Args:
            solution_dir: Path to solutions/qa-agent.
            framework: LLM framework — "openai" (default),
                "claude", or "langchain".
        """
        kb_dir = solution_dir / "knowledge_base"
        topic_graph_path = solution_dir / "topic_graph.json"

        retriever = HybridRetriever.from_knowledge_base(kb_dir)

        topic_graph = None
        if topic_graph_path.exists():
            with open(topic_graph_path) as f:
                topic_graph = json.load(f)

        generator = _create_generator(framework)

        return cls(
            retriever=retriever,
            generator=generator,
            topic_graph=topic_graph,
        )

    def _next_query_id(self) -> str:
        self._query_counter += 1
        return f"QRY-2026-{self._query_counter:04d}"

    async def answer(
        self,
        question: str,
        *,
        scope_level: int | None = None,
        top_k: int = 5,
    ) -> QAResponse:
        """Answer a question with the full pipeline.

        Steps:
            1. Retrieve relevant context from the document corpus
            2. Generate grounded answer with citations
            3. Return structured response

        Guardrails are run separately by the platform (GuardrailRunner).
        The agent focuses on retrieval + generation.
        """
        level = scope_level or self.scope_level
        query_id = self._next_query_id()

        start = time.perf_counter()

        # Step 1: Retrieve context
        chunks = self.retriever.retrieve(question, top_k=top_k)

        retrieval_ms = (time.perf_counter() - start) * 1000

        # Step 2: Generate answer
        gen_start = time.perf_counter()
        response = self.generator.generate(
            question,
            chunks,
            scope_level=level,
            query_id=query_id,
        )
        generation_ms = (time.perf_counter() - gen_start) * 1000

        # Add timing metadata
        response.metadata["retrieval_ms"] = round(retrieval_ms, 1)
        response.metadata["generation_ms"] = round(generation_ms, 1)
        response.metadata["total_ms"] = round(retrieval_ms + generation_ms, 1)

        return response


class DemoQAAgent:
    """Demo agent that returns pre-recorded answers without LLM or ChromaDB.

    Loads scenarios from solutions/qa-agent/scenarios/ and matches questions
    by keyword similarity. Falls back to the pass scenario for unknown questions.

    Usage:
        agent = DemoQAAgent.from_solution_dir(Path("solutions/qa-agent"))
        response = await agent.answer("What was CBA's net interest margin?")
    """

    def __init__(self, scenarios: dict[str, dict]):
        self._scenarios = scenarios
        self._query_counter = 0

    @classmethod
    def from_solution_dir(cls, solution_dir: Path) -> DemoQAAgent:
        """Load all pre-recorded scenarios."""
        scenarios_dir = solution_dir / "scenarios"
        scenarios: dict[str, dict] = {}

        for scenario_dir in sorted(scenarios_dir.iterdir()):
            if not scenario_dir.is_dir():
                continue
            input_path = scenario_dir / "input.json"
            output_path = scenario_dir / "output.json"
            if input_path.exists() and output_path.exists():
                with open(input_path) as f:
                    inp = json.load(f)
                with open(output_path) as f:
                    out = json.load(f)
                scenarios[scenario_dir.name] = {
                    "input": inp,
                    "output": out,
                }

        return cls(scenarios)

    def _match_scenario(self, question: str) -> dict:
        """Find the best matching scenario for a question."""
        q_lower = question.lower()

        # Check for injection patterns
        injection_words = [
            "ignore", "pretend", "system prompt",
            "jailbreak", "dan mode",
        ]
        if any(w in q_lower for w in injection_words):
            if "fail-injection" in self._scenarios:
                return self._scenarios["fail-injection"]["output"]

        # Check for out-of-scope (comparative) patterns
        scope_words = ["compare", "westpac", "anz", "nab"]
        if any(w in q_lower for w in scope_words):
            if "fail-scope" in self._scenarios:
                return self._scenarios["fail-scope"]["output"]

        # Check for financial advice
        advice_words = [
            "should i buy", "should i invest", "recommend",
        ]
        if any(w in q_lower for w in advice_words):
            if "fail-scope" in self._scenarios:
                return self._scenarios["fail-scope"]["output"]

        # Default to pass scenario
        if "pass" in self._scenarios:
            return self._scenarios["pass"]["output"]

        # Last resort
        return {
            "answer": {
                "text": "I can only answer questions about "
                "CBA's 2025 Annual Report.",
            },
            "citations": [],
        }

    async def answer(
        self,
        question: str,
        **kwargs: Any,
    ) -> QAResponse:
        """Return a pre-recorded answer."""
        self._query_counter += 1
        matched = self._match_scenario(question)

        # Build response from scenario, overriding IDs
        fields = {
            k: v for k, v in matched.items()
            if k in QAResponse.model_fields
        }
        fields["query_id"] = f"DEMO-{self._query_counter:04d}"
        fields["question"] = question
        return QAResponse(**fields)


async def main():
    """Run the Q&A agent interactively."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CBA Annual Report Q&A Agent",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Demo mode — pre-recorded answers, no API key needed",
    )
    parser.add_argument(
        "--framework",
        choices=["openai", "claude", "claude-direct", "langchain"],
        default="openai",
        help="LLM framework (default: openai)",
    )
    args = parser.parse_args()

    solution_dir = Path(__file__).parent.parent

    if args.demo:
        agent = DemoQAAgent.from_solution_dir(solution_dir)
        print("CBA Annual Report Q&A Agent (DEMO MODE)")
        print("Answers are pre-recorded. No API key needed.")
    else:
        agent = QAAgent.from_solution_dir(
            solution_dir, framework=args.framework,
        )
        print(f"CBA Annual Report Q&A Agent ({args.framework})")

    print("Type 'quit' to exit.\n")

    while True:
        question = input("Question: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break

        response = await agent.answer(question)
        print(f"\n{response.answer.text}")
        if response.citations:
            print("\nSources:")
            for c in response.citations:
                print(f"  - {c.document}, p.{c.page} — {c.section}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
