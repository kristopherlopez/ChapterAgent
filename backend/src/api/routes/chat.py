"""Chat API — interactive Q&A agent endpoint."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
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


def _get_guardrail_runner(citations_count: int | None = None) -> GuardrailRunner:
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
        citations_count=citations_count,
    )


_compliance_logger = ComplianceLogger(solution_id="cba-annual-report-qa")


def _get_context(agent, question, response):
    """Extract context texts for guardrail evaluation.

    Prefers the actual page content the agent read (stored in metadata by
    agentic generators) over re-retrieving chunks, which may not contain
    all the information the agent used to form its answer.
    """
    # Prefer pages the agent actually read (agentic generators store these)
    pages_read = response.metadata.get("pages_read")
    if pages_read:
        return pages_read
    # Fall back to retriever chunks
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
    runner = _get_guardrail_runner(citations_count=len(response.citations))
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

    # When blocked, replace answer with a friendly redirect
    display_text = response.answer.text
    if blocked:
        scope_failed = any(
            g.result == "fail" and "Scope" in g.name for g in guardrail_results
        )
        if scope_failed:
            display_text = (
                "That question is outside the scope of this tool. "
                "I can only answer questions about CBA's 2025 Annual Report — "
                "try asking about financial performance, dividends, sustainability, "
                "or other topics covered in the report."
            )
        else:
            display_text = (
                "I'm unable to answer that question. "
                "Please try rephrasing or ask something about CBA's 2025 Annual Report."
            )

    return ChatResponse(
        text=display_text,
        citations=[
            CitationOut(
                document=c.document,
                page=c.page,
                section=c.section,
                quote=c.quote,
            )
            for c in response.citations
        ] if not blocked else [],
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
    import sys
    import traceback

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    start = time.perf_counter()

    solution_dir = SOLUTIONS_DIR / "qa-agent"
    src_dir = solution_dir / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        agent = _get_agent(framework, model)
    except Exception as exc:
        yield sse("error", {"message": f"Failed to initialise agent: {exc}"})
        return

    yield sse("status", {"phase": "thinking"})

    # For OpenAI framework, use the real streaming path that emits
    # individual tool_call events as the agent reads pages
    streamed_context: list[str] | None = None

    if framework == "openai":
        try:
            collected_events: list[str] = []
            answer_text, citations, thinking, token_usage, pages_read = (
                await _run_openai_streamed(question, agent, collected_events)
            )
            if pages_read:
                streamed_context = pages_read
            # Flush collected SSE events to the client
            for ev in collected_events:
                yield ev
                await asyncio.sleep(0)
        except Exception as exc:
            tb = traceback.format_exc()
            yield sse("error", {"message": f"Generation failed: {exc}\n{tb}"})
            return
    else:
        try:
            def _run_sync():
                """Run the agent in a thread — answer() is async in signature
                but only performs sync work internally."""
                loop = asyncio.new_event_loop()
                try:
                    return loop.run_until_complete(agent.answer(question))
                finally:
                    loop.close()

            response = await asyncio.to_thread(_run_sync)
            answer_text = response.answer.text
            citations = response.citations
            thinking = response.thinking
            token_usage = response.metadata.get("token_usage", {})

            # Emit thinking steps
            for step in thinking:
                yield sse("thinking", {"text": step})
                await asyncio.sleep(0)

            # Emit individual source reads instead of a summary
            for c in citations:
                page_label = f"p.{c.page} — {c.section}" if hasattr(c, 'section') else f"p.{c.page}"
                yield sse("tool_call", {
                    "name": "read_page",
                    "description": f"Reading {page_label}",
                })
                await asyncio.sleep(0)
        except Exception as exc:
            tb = traceback.format_exc()
            yield sse("error", {"message": f"Generation failed: {exc}\n{tb}"})
            return

    # Run guardrails
    try:
        runner = _get_guardrail_runner(citations_count=len(citations) if citations else None)
        # Prefer page content the agent actually read; fall back to chunk retrieval
        context_texts = streamed_context
        if not context_texts and hasattr(agent, 'retriever'):
            chunks = agent.retriever.retrieve(question, top_k=5)
            context_texts = [c.text for c in chunks]

        guardrail_results = await runner.run_all(
            input=question, output=answer_text, context=context_texts,
        )
    except Exception as exc:
        yield sse("error", {"message": f"Guardrail evaluation failed: {exc}"})
        return

    total_ms = int((time.perf_counter() - start) * 1000)
    blocked = any(g.result == "fail" for g in guardrail_results)

    # When blocked, replace the answer with a friendly redirect
    display_text = answer_text
    if blocked:
        scope_failed = any(
            g.result == "fail" and "Scope" in g.name for g in guardrail_results
        )
        if scope_failed:
            display_text = (
                "That question is outside the scope of this tool. "
                "I can only answer questions about CBA's 2025 Annual Report — "
                "try asking about financial performance, dividends, sustainability, "
                "or other topics covered in the report."
            )
        else:
            display_text = (
                "I'm unable to answer that question. "
                "Please try rephrasing or ask something about CBA's 2025 Annual Report."
            )

    yield sse("complete", {
        "text": display_text,
        "citations": [
            {"document": c.document, "page": c.page, "section": c.section, "quote": c.quote}
            for c in citations
        ] if not blocked else [],
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
) -> tuple[str, list, list[str], dict, list[str]]:
    """Run OpenAI agent with streaming, collecting events.

    Returns (answer_text, citations, thinking, token_usage, pages_read)
    where pages_read contains the text of every page the agent read
    (used as guardrail context).
    """
    from agents import Agent, Runner, function_tool
    from agents.items import ReasoningItem
    from schema import AGENT_SYSTEM_PROMPT, Citation

    pages_dir = SOLUTIONS_DIR / "qa-agent" / "knowledge_base" / "markdown"

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    citations: list[Citation] = []
    thinking: list[str] = []
    pages_read: list[str] = []

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
            content = content[:15000] if len(content) > 15000 else content
            pages_read.append(content)
            return content

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
                # Build a human-readable description
                descriptions = {
                    "list_pages": "Browsing Annual Report table of contents",
                    "read_page": "Reading a page from the Annual Report",
                    "cite_source": "Recording a source citation",
                }
                desc = descriptions.get(tool_name, tool_name)
                # Extract args if available
                raw = item.raw_item if hasattr(item, "raw_item") else None
                if tool_name == "read_page" and raw and hasattr(raw, "arguments"):
                    try:
                        args = json.loads(raw.arguments) if isinstance(raw.arguments, str) else raw.arguments
                        fname = args.get("filename", "")
                        if fname:
                            desc = f"Reading {fname.replace('.md', '').replace('-', ' ')}"
                    except Exception:
                        pass
                events.append(sse("tool_call", {"name": tool_name, "description": desc}))
            elif hasattr(item, "type") and item.type == "tool_call_output_item":
                # Tool results — show page titles from list_pages
                raw = item.raw_item if hasattr(item, "raw_item") else None
                if raw and hasattr(raw, "output"):
                    output = raw.output if isinstance(raw.output, str) else str(raw.output)
                    # For list_pages, extract page titles as results
                    if "p." in output and "[" in output:
                        lines = [l.strip() for l in output.split("\n") if l.strip()][:6]
                        if lines:
                            events.append(sse("tool_call", {
                                "name": "list_pages",
                                "description": f"Annual Report — {len(lines)} sections",
                                "results": lines,
                            }))
            elif hasattr(item, "type") and item.type == "message_output_item":
                raw = item.raw_item if hasattr(item, "raw_item") else None
                if raw and hasattr(raw, "content"):
                    for c in raw.content:
                        if hasattr(c, "text") and c.text:
                            answer_text = c.text

    if not answer_text and result.is_complete:
        answer_text = result.final_output_as(str) or ""


    token_usage = {}

    return answer_text, citations, thinking, token_usage, pages_read


@router.post("/chat/{solution_id}/stream")
async def chat_stream(solution_id: str, req: ChatRequest):
    """Stream chat response with real-time thinking traces."""
    if solution_id != "cba-annual-report-qa":
        raise HTTPException(status_code=404, detail="Solution not found")

    return StreamingResponse(
        _stream_chat(solution_id, req.question, req.framework, req.model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
