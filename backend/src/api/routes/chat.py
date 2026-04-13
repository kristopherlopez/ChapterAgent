"""Chat API — interactive Q&A agent endpoint."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.platform.compliance.logger import ComplianceLogger
from src.platform.guardrails.runner import GuardrailRunner

router = APIRouter()

SOLUTIONS_DIR = Path(__file__).resolve().parents[4] / "solutions"

# Cached agent instances (avoid re-embedding on every request)
_agent_cache: dict[str, object] = {}


class ChatRequest(BaseModel):
    question: str
    framework: str = "openai"
    model: str | None = None


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
    thinking: list[str] = []
    latencyMs: int
    blocked: bool
    regenerated: bool = False


def _get_agent(framework: str, model: str | None = None):
    """Lazily import and build the QA agent (cached by framework+model)."""
    cache_key = f"{framework}:{model or 'default'}"
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

    kwargs = {}
    if model:
        kwargs["model"] = model

    try:
        agent = QAAgent.from_solution_dir(solution_dir, framework=framework, **kwargs)
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


_compliance_logger = ComplianceLogger(solution_id="cba-annual-report-qa")


def _get_context(agent, question, response):
    """Extract context texts for guardrail evaluation."""
    if hasattr(agent, 'retriever'):
        chunks = agent.retriever.retrieve(question, top_k=5)
        return [c.text for c in chunks]
    if response.citations:
        return [c.quote for c in response.citations]
    return None


@router.post("/chat/{solution_id}", response_model=ChatResponse)
async def chat(solution_id: str, req: ChatRequest):
    if solution_id != "cba-annual-report-qa":
        raise HTTPException(status_code=404, detail="Solution not found")

    start = time.perf_counter()

    # Run the agent
    agent = _get_agent(req.framework, req.model)
    response = await agent.answer(req.question)
    context_texts = _get_context(agent, req.question, response)

    # Run guardrails
    runner = _get_guardrail_runner()
    guardrail_results = await runner.run_all(
        input=req.question,
        output=response.answer.text,
        context=context_texts,
    )

    blocked = any(g.result == "fail" for g in guardrail_results)
    regenerated = False

    # Regeneration: if only faithfulness failed, retry with stricter grounding
    if blocked:
        faithfulness_failed = any(
            g.result == "fail" and "Faithfulness" in g.name
            for g in guardrail_results
        )
        only_faithfulness = faithfulness_failed and sum(
            1 for g in guardrail_results if g.result == "fail"
        ) == 1

        if only_faithfulness:
            # Retry with stricter grounding prompt
            response = await agent.answer(
                req.question,
                strict_grounding=True,
            ) if hasattr(agent.answer, '__code__') and 'strict_grounding' in agent.answer.__code__.co_varnames else await agent.answer(req.question)

            context_texts = _get_context(agent, req.question, response)
            guardrail_results = await runner.run_all(
                input=req.question,
                output=response.answer.text,
                context=context_texts,
            )
            blocked = any(g.result == "fail" for g in guardrail_results)
            regenerated = True

    total_ms = int((time.perf_counter() - start) * 1000)

    # Log compliance event (Layer 2)
    _compliance_logger.log_response(
        query=req.question,
        guardrail_results=guardrail_results,
        latency_ms=total_ms,
        blocked=blocked,
        regenerated=regenerated,
        regeneration_passed=not blocked if regenerated else None,
    )

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
        thinking=response.thinking,
        latencyMs=total_ms,
        blocked=blocked,
        regenerated=regenerated,
    )


# ---------------------------------------------------------------------------
# Streaming chat endpoint — real-time thinking traces
# ---------------------------------------------------------------------------

async def _stream_chat(
    solution_id: str,
    question: str,
    framework: str,
    model: str | None,
) -> AsyncIterator[str]:
    """Stream chat response with real-time thinking traces via SSE."""
    import importlib.util
    import sys

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    start = time.perf_counter()

    solution_dir = SOLUTIONS_DIR / "qa-agent"
    src_dir = solution_dir / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Import what we need from the agents
    from retrieve import HybridRetriever
    from schema import Citation

    # Get retriever (cached via _get_agent's side effect of adding src to path)
    agent = _get_agent(framework, model)

    yield sse("status", {"phase": "thinking"})

    # Framework-specific streaming
    if framework == "openai":
        answer_text, citations, thinking, token_usage = await _stream_openai(
            question, agent, src_dir, sse_callback=lambda e, d: None,
            yield_events=[],
        )
        # Re-run with actual yielding
        events: list[str] = []
        answer_text, citations, thinking, token_usage = await _run_openai_streamed(
            question, agent, events,
        )
        for ev in events:
            yield ev
    else:
        # For Claude and LangChain, use the existing generate() and return thinking
        response = await agent.answer(question)
        answer_text = response.answer.text
        citations = response.citations
        thinking = response.thinking
        token_usage = response.metadata.get("token_usage", {})
        for step in thinking:
            yield sse("thinking", {"text": step})

    # Run guardrails
    runner = _get_guardrail_runner()
    context_texts = None
    if hasattr(agent, 'retriever'):
        chunks = agent.retriever.retrieve(question, top_k=5)
        context_texts = [c.text for c in chunks]

    guardrail_results = await runner.run_all(
        input=question, output=answer_text, context=context_texts,
    )

    total_ms = int((time.perf_counter() - start) * 1000)
    blocked = any(g.result == "fail" for g in guardrail_results)

    # Send final complete response
    yield sse("complete", {
        "text": answer_text,
        "citations": [
            {"document": c.document, "page": c.page, "section": c.section, "quote": c.quote}
            for c in citations
        ],
        "guardrails": [
            {"name": g.name, "status": g.result, "detail": g.detail}
            for g in guardrail_results
        ],
        "thinking": thinking if isinstance(thinking, list) else [],
        "latencyMs": total_ms,
        "blocked": blocked,
    })


async def _run_openai_streamed(
    question: str, agent, events: list[str],
) -> tuple[str, list, list[str], dict]:
    """Run OpenAI agent with streaming, collecting events."""
    from agents import Agent, Runner, function_tool
    from agents.items import ReasoningItem
    from schema import AGENT_SYSTEM_PROMPT, Citation

    pages_dir = SOLUTIONS_DIR / "qa-agent" / "knowledge_base" / "markdown"

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    citations: list[Citation] = []
    thinking: list[str] = []

    has_pages = pages_dir.exists() and any(pages_dir.glob("*.md"))

    if has_pages:
        # Build page index
        from schema import BaseGenerator
        page_index = BaseGenerator.build_page_index(pages_dir)

        @function_tool
        def list_pages() -> str:
            """List all pages in the CBA Annual Report."""
            return "\n".join(
                f"p.{e['page']:>3}  {e['title']:<60}  [{e['file']}]"
                for e in page_index
            )

        @function_tool
        def read_page(filename: str) -> str:
            """Read a full page from the CBA Annual Report by filename."""
            p = pages_dir / filename
            if not p.exists():
                return json.dumps({"error": f"Not found: {filename}"})
            content = p.read_text(encoding="utf-8", errors="replace")
            return content[:15000] if len(content) > 15000 else content

        @function_tool
        def cite_source(page: int, section: str, quote: str) -> str:
            """Record a citation for a factual claim."""
            citations.append(Citation(page=page, section=section, quote=quote))
            return f"Citation recorded: p.{page}"

        openai_agent = Agent(
            name="CBA Annual Report Q&A",
            instructions=AGENT_SYSTEM_PROMPT,
            model=agent.generator.model,
            tools=[list_pages, read_page, cite_source],
        )
    else:
        # Context fallback
        from schema import SYSTEM_PROMPT
        chunks = agent.retriever.retrieve(question, top_k=5)
        context = BaseGenerator.build_context(chunks)
        instructions = SYSTEM_PROMPT.format(context=context)
        citations = BaseGenerator.extract_citations(chunks)

        @function_tool
        def cite_source_ctx(page: int, section: str, quote: str) -> str:
            """Record a citation."""
            citations.append(Citation(page=page, section=section, quote=quote))
            return f"Citation recorded: p.{page}"

        openai_agent = Agent(
            name="CBA Annual Report Q&A",
            instructions=instructions,
            model=agent.generator.model,
            tools=[cite_source_ctx],
        )

    # Stream the run
    result = Runner.run_streamed(openai_agent, question, max_turns=10)
    answer_text = ""

    async for event in result.stream_events():
        if event.type == "run_item_stream_event":
            item = event.item
            if hasattr(item, "type") and item.type == "reasoning_item":
                # Extract reasoning summary
                raw = item.raw_item if hasattr(item, "raw_item") else None
                if raw and hasattr(raw, "summary"):
                    for s in raw.summary:
                        if hasattr(s, "text") and s.text:
                            thinking.append(s.text)
                            events.append(sse("thinking", {"text": s.text}))
                elif raw and hasattr(raw, "content"):
                    for c in (raw.content or []):
                        if hasattr(c, "text") and c.text:
                            thinking.append(c.text)
                            events.append(sse("thinking", {"text": c.text}))
            elif hasattr(item, "type") and item.type == "tool_call_item":
                tool_name = getattr(item, "name", "") or ""
                if not tool_name and hasattr(item, "raw_item"):
                    tool_name = getattr(item.raw_item, "name", "tool")
                events.append(sse("tool_call", {"name": tool_name}))
            elif hasattr(item, "type") and item.type == "message_output_item":
                raw = item.raw_item if hasattr(item, "raw_item") else None
                if raw and hasattr(raw, "content"):
                    for c in raw.content:
                        if hasattr(c, "text") and c.text:
                            answer_text = c.text

    if not answer_text and result.is_complete:
        answer_text = result.final_output_as(str) or ""

    token_usage = {}

    return answer_text, citations, thinking, token_usage


@router.post("/chat/{solution_id}/stream")
async def chat_stream(
    solution_id: str,
    framework: str = Query(default="openai"),
    question: str = Query(...),
    model: str | None = Query(default=None),
):
    """Stream chat response with real-time thinking traces."""
    if solution_id != "cba-annual-report-qa":
        raise HTTPException(status_code=404, detail="Solution not found")

    return StreamingResponse(
        _stream_chat(solution_id, question, framework, model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
