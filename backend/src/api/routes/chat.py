"""Chat API — interactive Q&A agent endpoint."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.platform.guardrails.runner import GuardrailRunner

router = APIRouter()

SOLUTIONS_DIR = Path(__file__).resolve().parents[4] / "solutions"

# Cached agent instances (avoid re-embedding on every request)
_agent_cache: dict[str, object] = {}


class ChatRequest(BaseModel):
    question: str
    framework: str = "openai"


class CitationOut(BaseModel):
    document: str
    page: int
    section: str
    quote: str


class GuardrailOut(BaseModel):
    name: str
    status: str
    detail: str | None = None


class ChatResponse(BaseModel):
    text: str
    citations: list[CitationOut]
    guardrails: list[GuardrailOut]
    latencyMs: int
    blocked: bool


def _get_agent(framework: str):
    """Lazily import and build the QA agent (cached after first call)."""
    cache_key = framework
    if cache_key in _agent_cache:
        return _agent_cache[cache_key]

    import importlib.util
    import sys

    solution_dir = SOLUTIONS_DIR / "qa-agent"
    src_dir = solution_dir / "src"

    # Import agent.py from the hyphenated directory via importlib
    if "qa_agent_module" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "qa_agent_module", src_dir / "agent.py",
            submodule_search_locations=[str(src_dir)],
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["qa_agent_module"] = mod
        # Ensure sibling imports (generate, retrieve) resolve from src_dir
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        spec.loader.exec_module(mod)

    mod = sys.modules["qa_agent_module"]
    DemoQAAgent = mod.DemoQAAgent
    QAAgent = mod.QAAgent

    try:
        agent = QAAgent.from_solution_dir(solution_dir, framework=framework)
    except Exception:
        # Fall back to demo agent if ChromaDB / deps unavailable
        agent = DemoQAAgent.from_solution_dir(solution_dir)

    _agent_cache[cache_key] = agent
    return agent


def _get_guardrail_runner() -> GuardrailRunner:
    """Build the guardrail runner for the QA agent."""
    import json

    topic_graph_path = SOLUTIONS_DIR / "qa-agent" / "topic_graph.json"
    topic_graph = None
    if topic_graph_path.exists():
        with open(topic_graph_path) as f:
            topic_graph = json.load(f)

    return GuardrailRunner.for_qa_agent(
        scope_level=1,
        topic_graph=topic_graph,
    )


@router.post("/chat/{solution_id}", response_model=ChatResponse)
async def chat(solution_id: str, req: ChatRequest):
    if solution_id != "cba-annual-report-qa":
        raise HTTPException(status_code=404, detail="Solution not found")

    start = time.perf_counter()

    # Run the agent
    agent = _get_agent(req.framework)
    response = await agent.answer(req.question)

    # Build context for guardrails from the full citation quotes
    # For QAAgent, also retrieve the raw chunks for better faithfulness scoring
    context_texts = None
    if hasattr(agent, 'retriever'):
        chunks = agent.retriever.retrieve(req.question, top_k=5)
        context_texts = [c.text for c in chunks]
    elif response.citations:
        context_texts = [c.quote for c in response.citations]

    # Run guardrails
    runner = _get_guardrail_runner()
    guardrail_results = await runner.run_all(
        input=req.question,
        output=response.answer.text,
        context=context_texts,
    )

    total_ms = int((time.perf_counter() - start) * 1000)

    blocked = any(g.result == "fail" for g in guardrail_results)

    return ChatResponse(
        text=response.answer.text,
        citations=[
            CitationOut(
                document=c.document,
                page=c.page,
                section=c.section,
                quote=c.quote,
            )
            for c in response.citations
        ],
        guardrails=[
            GuardrailOut(
                name=g.name,
                status=g.result,
                detail=g.detail if g.detail else None,
            )
            for g in guardrail_results
        ],
        latencyMs=total_ms,
        blocked=blocked,
    )
