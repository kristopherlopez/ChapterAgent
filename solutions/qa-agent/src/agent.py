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
        refusal_message: str = "I can only answer questions about CBA's 2024 Annual Report.",
    ):
        self.retriever = retriever
        self.generator = generator or QAGenerator()
        self.topic_graph = topic_graph
        self.scope_level = scope_level
        self.refusal_message = refusal_message
        self._query_counter = 0

    @classmethod
    def from_solution_dir(cls, solution_dir: Path) -> QAAgent:
        """Create agent from the solution directory structure."""
        kb_dir = solution_dir / "knowledge_base"
        topic_graph_path = solution_dir / "topic_graph.json"

        retriever = HybridRetriever.from_knowledge_base(kb_dir)

        topic_graph = None
        if topic_graph_path.exists():
            with open(topic_graph_path) as f:
                topic_graph = json.load(f)

        return cls(
            retriever=retriever,
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


async def main():
    """Run the Q&A agent interactively."""
    solution_dir = Path(__file__).parent.parent
    agent = QAAgent.from_solution_dir(solution_dir)

    print("CBA Annual Report Q&A Agent")
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
