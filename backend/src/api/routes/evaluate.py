"""Evaluation API — run guardrails and DeepEval metrics with SSE streaming."""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.platform.guardrails.runner import GuardrailRunner

router = APIRouter(tags=["evaluate"])

ROOT = Path(__file__).resolve().parents[4]
SOLUTIONS_DIR = ROOT / "solutions"
RESULTS_DIR = ROOT / "results"


class EvaluateRequest(BaseModel):
    framework: str = "openai"
    limit: int = 3
    judge: str = "gpt-4o-mini"


def _get_agent(framework: str):
    """Import and build the QA agent."""
    import importlib.util
    import sys

    solution_dir = SOLUTIONS_DIR / "qa-agent"
    src_dir = solution_dir / "src"

    if "qa_agent_module_eval" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "qa_agent_module_eval", src_dir / "agent.py",
            submodule_search_locations=[str(src_dir)],
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["qa_agent_module_eval"] = mod
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        spec.loader.exec_module(mod)

    mod = sys.modules["qa_agent_module_eval"]

    try:
        agent = mod.QAAgent.from_solution_dir(solution_dir, framework=framework)
    except Exception:
        agent = mod.DemoQAAgent.from_solution_dir(solution_dir)

    return agent


def _get_guardrail_runner() -> GuardrailRunner:
    """Build guardrail runner."""
    topic_graph_path = SOLUTIONS_DIR / "qa-agent" / "topic_graph.json"
    topic_graph = None
    if topic_graph_path.exists():
        with open(topic_graph_path) as f:
            topic_graph = json.load(f)
    return GuardrailRunner.for_qa_agent(scope_level=1, topic_graph=topic_graph)


def _load_golden_dataset(limit: int) -> list[dict]:
    """Load test cases from the golden dataset."""
    dataset_path = SOLUTIONS_DIR / "qa-agent" / "golden_dataset" / "dataset.json"
    with open(dataset_path, encoding="utf-8") as f:
        data = json.load(f)
    cases = data.get("test_cases", data if isinstance(data, list) else [])
    return cases[:limit]


def _save_results(
    guardrail_results: list[dict],
    eval_results: list[dict],
    framework: str,
    agent_results: list[dict] | None = None,
):
    """Persist results to the results directory — both per-framework and top-level."""
    result_dir = RESULTS_DIR / "petsure-annual-report-qa"
    result_dir.mkdir(parents=True, exist_ok=True)

    # Save per-framework results
    fw_dir = result_dir / "frameworks" / framework
    fw_dir.mkdir(parents=True, exist_ok=True)

    with open(fw_dir / "guardrails.json", "w") as f:
        json.dump(guardrail_results, f, indent=2)
    with open(fw_dir / "evaluation.json", "w") as f:
        json.dump(eval_results, f, indent=2)

    # Compute per-framework scorecard entry
    pass_count = sum(1 for g in guardrail_results if g["result"] == "pass")
    total = len(guardrail_results)
    eval_scores = [e["score"] for e in eval_results if e.get("score") is not None]
    avg_score = sum(eval_scores) / len(eval_scores) if eval_scores else 0

    latency_avg = 0
    token_avg = 0
    cost_avg = 0.0
    if agent_results:
        latencies = [r["elapsed_ms"] for r in agent_results]
        latency_avg = int(sum(latencies) / len(latencies))

    fw_summary = {
        "framework": framework,
        "evalScore": round(avg_score, 4),
        "guardrailsPass": f"{pass_count}/{total}",
        "latencyAvgMs": latency_avg,
        "gateResult": "pass" if pass_count == total else "fail",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M AEST"),
    }
    with open(fw_dir / "scorecard.json", "w") as f:
        json.dump(fw_summary, f, indent=2)

    # Also update top-level files (most recent framework wins)
    with open(result_dir / "guardrails.json", "w") as f:
        json.dump(guardrail_results, f, indent=2)
    with open(result_dir / "evaluation.json", "w") as f:
        json.dump(eval_results, f, indent=2)

    # Update summary
    summary_path = result_dir / "summary.json"
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
    else:
        summary = {
            "id": "petsure-annual-report-qa",
            "name": "PetSure Australia Annual Report Q&A",
        }

    summary["guardrailsSummary"] = f"{pass_count}/{total} PASS"
    summary["evalScore"] = round(avg_score, 2)
    summary["health"] = "pass" if pass_count == total else "fail"
    summary["gateResult"] = "pass" if pass_count == total else "fail"
    summary["lastRun"] = datetime.now().strftime("%Y-%m-%d %H:%M AEST")

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Update compliance gate
    compliance = {
        "gate": "Deployment Gate",
        "result": "pass" if pass_count == total else "fail",
        "reason": f"{pass_count}/{total} guardrails passed. "
                  f"Overall eval score: {avg_score:.2%}.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M AEST"),
    }
    with open(result_dir / "compliance.json", "w") as f:
        json.dump(compliance, f, indent=2)


async def _stream_evaluation(
    framework: str,
    limit: int,
    judge: str,
) -> AsyncIterator[str]:
    """Run evaluation and yield SSE events as each step completes."""

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    yield sse("status", {"phase": "init", "message": "Loading agent..."})

    # Load agent
    agent = _get_agent(framework)
    agent_type = type(agent).__name__
    yield sse("status", {
        "phase": "agent_ready",
        "message": f"Agent ready ({agent_type})",
    })

    # Load golden dataset
    test_cases = _load_golden_dataset(limit)
    yield sse("status", {
        "phase": "dataset_loaded",
        "message": f"Loaded {len(test_cases)} test cases",
        "totalCases": len(test_cases),
    })

    # Run agent on each test case
    agent_results = []
    for i, tc in enumerate(test_cases):
        question = tc["question"]
        yield sse("status", {
            "phase": "running_case",
            "caseIndex": i,
            "question": question[:80],
        })

        start = time.perf_counter()
        response = await agent.answer(question)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        agent_results.append({
            "question": question,
            "answer": response.answer.text,
            "citations": [c.model_dump() for c in response.citations],
            "expected": tc.get("expected_answer"),
            "elapsed_ms": elapsed_ms,
        })

        yield sse("case_complete", {
            "caseIndex": i,
            "question": question[:80],
            "answerPreview": response.answer.text[:100],
            "citations": len(response.citations),
            "elapsedMs": elapsed_ms,
        })

    # Run guardrails on each result
    yield sse("status", {
        "phase": "running_guardrails",
        "message": "Running guardrails...",
    })

    runner = _get_guardrail_runner()
    all_guardrail_results: list[dict] = []

    # Run guardrails on first result as representative sample
    if agent_results:
        sample = agent_results[0]
        context_texts = [
            c.get("quote", "") for c in sample["citations"]
        ] or None

        # Run each guardrail individually for streaming progress
        for guardrail in runner.guardrails:
            yield sse("guardrail_start", {"name": guardrail.name})

            result = await guardrail.check(
                input=sample["question"],
                output=sample["answer"],
                context=context_texts,
            )

            entry = {
                "name": result.name,
                "result": result.result,
                "detail": result.detail,
            }
            all_guardrail_results.append(entry)

            yield sse("guardrail_complete", entry)

            # Small delay so the UI can animate
            await asyncio.sleep(0.3)

    # Run DeepEval metrics
    yield sse("status", {
        "phase": "running_deepeval",
        "message": "Running DeepEval metrics (LLM-as-judge)...",
    })

    eval_results: list[dict] = []
    try:
        from deepeval.metrics import (
            FaithfulnessMetric,
            AnswerRelevancyMetric,
            HallucinationMetric,
            BiasMetric,
            ToxicityMetric,
        )
        from deepeval.test_case import LLMTestCase

        metrics_to_run = [
            ("Faithfulness", FaithfulnessMetric(threshold=0.90, model=judge)),
            ("Answer Relevancy", AnswerRelevancyMetric(threshold=0.85, model=judge)),
            ("Hallucination", HallucinationMetric(threshold=0.10, model=judge)),
            ("Bias", BiasMetric(threshold=0.05, model=judge)),
            ("Toxicity", ToxicityMetric(threshold=0.05, model=judge)),
        ]

        # Build test cases
        deepeval_cases = []
        for ar in agent_results:
            retrieval_context = [
                c.get("quote", "") for c in ar["citations"]
            ] if ar["citations"] else None
            deepeval_cases.append(
                LLMTestCase(
                    input=ar["question"],
                    actual_output=ar["answer"],
                    expected_output=ar.get("expected"),
                    retrieval_context=retrieval_context,
                    context=[ar["expected"]] if ar.get("expected") else None,
                )
            )

        # Run each metric and stream results
        for metric_name, metric in metrics_to_run:
            yield sse("metric_start", {"name": metric_name})

            scores = []
            for tc in deepeval_cases:
                try:
                    await metric.a_measure(tc)
                    if metric.score is not None:
                        scores.append(metric.score)
                except Exception:
                    pass

            avg_score = sum(scores) / len(scores) if scores else 0.0
            threshold = metric.threshold
            direction = "lower_is_better" if metric_name in ("Hallucination", "Bias", "Toxicity") else "higher_is_better"

            if direction == "lower_is_better":
                status = "pass" if avg_score <= threshold else "fail"
            else:
                status = "pass" if avg_score >= threshold else "fail"

            entry = {
                "metric": metric_name,
                "score": round(avg_score, 4),
                "threshold": threshold,
                "status": status,
                "direction": direction,
            }
            eval_results.append(entry)

            yield sse("metric_complete", entry)
            await asyncio.sleep(0.1)

    except Exception as e:
        yield sse("error", {
            "phase": "deepeval",
            "message": f"DeepEval error: {str(e)}",
        })

    # Save results (per-framework + top-level)
    _save_results(all_guardrail_results, eval_results, framework, agent_results)

    # Final summary
    guardrail_pass = sum(1 for g in all_guardrail_results if g["result"] == "pass")
    eval_pass = sum(1 for e in eval_results if e["status"] == "pass")

    yield sse("complete", {
        "guardrails": f"{guardrail_pass}/{len(all_guardrail_results)}",
        "metrics": f"{eval_pass}/{len(eval_results)}",
        "totalCases": len(test_cases),
    })


@router.get("/evaluate/{solution_id}/run")
async def run_evaluation(
    solution_id: str,
    framework: str = Query(default="openai"),
    limit: int = Query(default=3, ge=1, le=50),
    judge: str = Query(default="gpt-5.4"),
):
    """Run evaluation with SSE streaming progress."""
    if solution_id != "petsure-annual-report-qa":
        raise HTTPException(status_code=404, detail="Solution not found")

    return StreamingResponse(
        _stream_evaluation(framework, limit, judge),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/evaluate/{solution_id}/results")
def get_evaluation_results(solution_id: str):
    """Get the latest evaluation results."""
    result_dir = RESULTS_DIR / solution_id
    if not result_dir.exists():
        raise HTTPException(status_code=404, detail="No evaluation results")

    guardrails = []
    evaluation = []

    gr_path = result_dir / "guardrails.json"
    ev_path = result_dir / "evaluation.json"

    if gr_path.exists():
        with open(gr_path) as f:
            guardrails = json.load(f)
    if ev_path.exists():
        with open(ev_path) as f:
            evaluation = json.load(f)

    return {
        "guardrails": guardrails,
        "evaluation": evaluation,
    }


@router.get("/evaluate/{solution_id}/results/{framework}")
def get_framework_results(solution_id: str, framework: str):
    """Get evaluation results for a specific framework."""
    fw_dir = RESULTS_DIR / solution_id / "frameworks" / framework
    if not fw_dir.exists():
        raise HTTPException(status_code=404, detail=f"No results for framework: {framework}")

    guardrails = []
    evaluation = []
    scorecard = {}

    gr_path = fw_dir / "guardrails.json"
    ev_path = fw_dir / "evaluation.json"
    sc_path = fw_dir / "scorecard.json"

    if gr_path.exists():
        with open(gr_path) as f:
            guardrails = json.load(f)
    if ev_path.exists():
        with open(ev_path) as f:
            evaluation = json.load(f)
    if sc_path.exists():
        with open(sc_path) as f:
            scorecard = json.load(f)

    return {
        "framework": framework,
        "guardrails": guardrails,
        "evaluation": evaluation,
        "scorecard": scorecard,
    }


@router.get("/evaluate/{solution_id}/scorecard")
def get_scorecard(solution_id: str):
    """Get scorecard comparing all frameworks that have been evaluated."""
    fw_root = RESULTS_DIR / solution_id / "frameworks"
    if not fw_root.exists():
        return {"frameworks": []}

    frameworks = []
    for fw_dir in sorted(fw_root.iterdir()):
        if not fw_dir.is_dir():
            continue
        sc_path = fw_dir / "scorecard.json"
        if sc_path.exists():
            with open(sc_path) as f:
                frameworks.append(json.load(f))

    return {"frameworks": frameworks}
