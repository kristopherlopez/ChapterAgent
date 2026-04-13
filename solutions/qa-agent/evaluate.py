"""Evaluate the CBA Annual Report Q&A Agent using DeepEval.

Runs golden dataset questions through the agent, then scores the
responses with DeepEval's LLM-as-judge metrics (faithfulness,
answer relevancy, hallucination, bias, toxicity).

Usage:
    # Full evaluation (all 50 test cases)
    python evaluate.py

    # Quick smoke test (first 5 cases)
    python evaluate.py --limit 5

    # Specific framework
    python evaluate.py --framework claude --limit 3

    # Use a different judge model
    python evaluate.py --judge gpt-4o-mini --limit 5
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# Ensure imports resolve
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from src.agent import QAAgent
from src.platform.evaluation.harness import EvaluationHarness
from src.platform.evaluation.datasets import GoldenDatasetLoader


def run_agent_on_dataset(
    agent: QAAgent,
    dataset_path: Path,
    *,
    limit: int | None = None,
) -> list[dict]:
    """Run the agent on each golden dataset question, return DeepEval test cases."""
    dataset = GoldenDatasetLoader.load(dataset_path)
    cases = dataset.test_cases[:limit] if limit else dataset.test_cases

    print(f"Running {len(cases)} test cases through the agent...")
    print()

    test_cases = []
    for i, tc in enumerate(cases, 1):
        print(f"  [{i}/{len(cases)}] {tc.question[:70]}...", end=" ", flush=True)
        start = time.time()

        response = asyncio.run(agent.answer(tc.question))
        elapsed = time.time() - start

        # Build retrieval context from citations
        retrieval_context = [
            f"p.{c.page}, {c.section}: {c.quote}"
            for c in response.citations
        ] or None

        test_cases.append({
            "input": tc.question,
            "actual_output": response.answer.text,
            "expected_output": tc.expected_answer,
            "retrieval_context": retrieval_context,
            "context": [tc.expected_answer] if tc.expected_answer else None,
        })

        status = "BLOCKED" if response.metadata.get("blocked") else "OK"
        print(f"({elapsed:.1f}s)")

    print()
    return test_cases


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate CBA Annual Report Q&A Agent with DeepEval",
    )
    parser.add_argument(
        "--framework",
        choices=["openai", "claude", "langchain"],
        default="openai",
        help="Agent framework (default: openai)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of test cases (default: all)",
    )
    parser.add_argument(
        "--judge",
        default="gpt-4o-mini",
        help="Judge model for DeepEval metrics (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use DemoQAAgent (pre-recorded answers, no API key needed)",
    )
    args = parser.parse_args()

    solution_dir = Path(__file__).parent
    dataset_path = solution_dir / "golden_dataset" / "dataset.json"

    if not dataset_path.exists():
        print(f"Golden dataset not found: {dataset_path}")
        sys.exit(1)

    # Build agent
    if args.demo:
        from src.agent import DemoQAAgent
        agent = DemoQAAgent.from_solution_dir(solution_dir)
        print(f"Agent: DemoQAAgent (pre-recorded)")
    else:
        agent = QAAgent.from_solution_dir(solution_dir, framework=args.framework)
        print(f"Agent: QAAgent ({args.framework})")

    print(f"Judge: {args.judge}")
    print(f"Dataset: {dataset_path}")
    print()

    # Step 1: Run agent on golden dataset
    test_cases = run_agent_on_dataset(
        agent, dataset_path, limit=args.limit,
    )

    # Step 2: Run DeepEval evaluation
    print("Running DeepEval evaluation...")
    print()

    harness = EvaluationHarness(
        risk_tier="production_customer_facing",
        golden_dataset_path=dataset_path,
    )

    report = harness.run_live(
        test_cases,
        solution_id="cba-annual-report-qa",
        model=args.judge,
    )

    # Step 3: Print results
    print("=" * 60)
    print(f"  EVALUATION REPORT — {args.framework.upper()}")
    print("=" * 60)
    print()
    print(f"  Solution:    cba-annual-report-qa")
    print(f"  Framework:   {args.framework}")
    print(f"  Risk Tier:   {report.risk_tier}")
    print(f"  Test Cases:  {report.total_test_cases}")
    print(f"  Overall:     {report.overall_score:.2%}")
    print(f"  Result:      {'PASS' if report.passed else 'FAIL'}")
    print()
    print("  Metrics:")
    for m in report.metrics:
        icon = "PASS" if m.status == "pass" else "FAIL"
        direction = "<=" if m.direction == "lower_is_better" else ">="
        print(
            f"    [{icon}] {m.metric:<25} "
            f"{m.score:.2%}  ({direction} {m.threshold:.2%})"
        )
    print()
    print(f"  {report.summary}")
    print()

    # Save report
    report_path = solution_dir / "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(report.model_dump(), f, indent=2)
    print(f"  Report saved to: {report_path}")


if __name__ == "__main__":
    main()
