# Component #4: Evaluation Harness (DeepEval)

The agent ships with its own evaluation suite powered by DeepEval — the same pattern the chapter would require for any AI solution. DeepEval is the engine; the harness is the reusable wrapper that standardises how squads consume it.

## How DeepEval Fits

DeepEval provides LLM-as-a-judge metrics out of the box. The chapter wraps these into a standardised harness that squads consume without needing to understand DeepEval internals. This is the reusable component pattern in action: DeepEval is the dependency, the harness is the interface.

```
+-------------------------------------------------------+
|  Chapter Evaluation Harness (reusable component)       |
|                                                        |
|  Squad provides:        Harness provides:              |
|  - Golden dataset        - DeepEval metric configs     |
|  - Retriever endpoint    - Threshold enforcement       |
|  - Generator endpoint    - Scorecard generation        |
|                          - CI/CD gate (pass/fail)      |
|                                                        |
|  +---------------------------------------------------+ |
|  |  DeepEval Engine                                   | |
|  |                                                    | |
|  |  Batch Metrics (golden dataset sweep):             | |
|  |  - FaithfulnessMetric                              | |
|  |  - AnswerRelevancyMetric                           | |
|  |  - ContextualPrecisionMetric                       | |
|  |  - ContextualRecallMetric                          | |
|  |  - HallucinationMetric                             | |
|  |  - BiasMetric                                      | |
|  |  - ToxicityMetric                                  | |
|  |                                                    | |
|  |  Custom Metrics (chapter-defined):                 | |
|  |  - CitationCoverageMetric                          | |
|  |  - BoundaryAdherenceMetric                         | |
|  |  - CrossPlatformConsistencyMetric                  | |
|  +---------------------------------------------------+ |
|                                                        |
|  Output: Standardised scorecard per evaluation layer   |
+-------------------------------------------------------+
```

## DeepEval Integration — Batch Evaluation (CI/CD Gate)

This runs the full golden dataset through the agent and produces a scorecard. It's the quality gate before any AI solution goes to production.

```python
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    HallucinationMetric,
    BiasMetric,
    ToxicityMetric,
)
from deepeval.dataset import EvaluationDataset

# Chapter-defined thresholds (configurable by risk tier)
THRESHOLDS = {
    "production_customer_facing": {
        "faithfulness": 0.9,
        "answer_relevancy": 0.85,
        "contextual_precision": 0.8,
        "contextual_recall": 0.75,
        "hallucination": 0.1,  # max allowed
        "bias": 0.1,
        "toxicity": 0.05,
    },
    "production_internal": {
        "faithfulness": 0.8,
        "answer_relevancy": 0.75,
        "contextual_precision": 0.7,
        "contextual_recall": 0.65,
        "hallucination": 0.15,
        "bias": 0.15,
        "toxicity": 0.1,
    },
    "experimental": None,  # no gate, but scores logged
}

# Metrics the chapter ships as part of the harness
metrics = [
    FaithfulnessMetric(threshold=0.9, model="gpt-4o"),
    AnswerRelevancyMetric(threshold=0.85, model="gpt-4o"),
    ContextualPrecisionMetric(threshold=0.8, model="gpt-4o"),
    ContextualRecallMetric(threshold=0.75, model="gpt-4o"),
    HallucinationMetric(threshold=0.1, model="gpt-4o"),
    BiasMetric(threshold=0.1),
    ToxicityMetric(threshold=0.05),
]

# Squad provides: golden dataset + their retriever/generator endpoints
# Harness provides: metrics, thresholds, scorecard, CI/CD gate
def build_test_cases(golden_dataset, retriever, generator):
    test_cases = []
    for entry in golden_dataset:
        retrieved_contexts = retriever.retrieve(entry["question"])
        generated_output = generator.generate(
            entry["question"], retrieved_contexts
        )
        test_cases.append(
            LLMTestCase(
                input=entry["question"],
                actual_output=generated_output,
                expected_output=entry.get("expected_answer"),
                retrieval_context=retrieved_contexts,
                context=entry.get("expected_chunks"),
            )
        )
    return test_cases

# Run evaluation — this is the CI/CD gate
dataset = EvaluationDataset(test_cases=build_test_cases(...))
results = evaluate(dataset, metrics)
```

## DeepEval Integration — Real-Time Compliance Checks (Component #5)

The same DeepEval metrics also power the per-response compliance pipeline. The difference: batch evaluation runs the full golden dataset pre-deployment; real-time checks run on every live response.

```python
from deepeval.metrics import FaithfulnessMetric, BiasMetric, ToxicityMetric
from deepeval.test_case import LLMTestCase

async def compliance_pipeline(query, retrieved_chunks, response):
    """Runs on every response before it reaches the user."""
    test_case = LLMTestCase(
        input=query,
        actual_output=response,
        retrieval_context=retrieved_chunks,
    )

    # These run in parallel — target < 200ms total
    checks = {
        "scope_adherence": check_scope(query),           # custom: fast classifier
        "citation_coverage": check_citations(response, retrieved_chunks),  # custom
        "pii_scan": check_pii(response),                 # custom: regex + NER
        "faithfulness": FaithfulnessMetric(threshold=0.9, model="gpt-4o-mini"),
        "bias": BiasMetric(threshold=0.1),
        "toxicity": ToxicityMetric(threshold=0.05),
    }

    # Fast checks run synchronously, LLM-as-a-judge checks run async
    # For real-time: use gpt-4o-mini as the judge (faster, cheaper)
    # For batch eval: use gpt-4o as the judge (more accurate)

    results = await run_all_checks(checks, test_case)

    return ComplianceResult(
        passed=all(r.passed for r in results),
        gates=results,
        elapsed_ms=total_time,
        evidence=generate_evidence_report(results),
    )
```

## Two Modes, Same Engine

| | Batch Evaluation (CI/CD) | Real-Time Compliance |
|---|---|---|
| **When** | Pre-deployment, on golden dataset | Every live response |
| **Judge model** | gpt-4o (accuracy) | gpt-4o-mini (speed) |
| **Metrics** | Full suite (7+ metrics) | Subset (faithfulness, bias, toxicity) |
| **Threshold source** | Risk tier config | Same risk tier config |
| **Output** | Scorecard + pass/fail gate | Trace panel + evidence log |
| **Latency budget** | Minutes (batch) | < 500ms (real-time) |
| **DeepEval integration** | `evaluate()` on `EvaluationDataset` | Individual `Metric.measure()` calls |

This is the key architectural insight: the same evaluation framework (DeepEval) serves two purposes through the same reusable component. Squads don't need to build separate systems for pre-deployment testing and production monitoring.

## Golden Dataset

- Curated set of expected interview questions and ideal answers
- Graded relevance scores per source chunk (Grade 0-3)
- Covers: leadership questions, technical questions, governance questions, team build questions, strategy questions
- Format compatible with DeepEval's `EvaluationDataset` class

## Cross-Platform Evaluation

- Same golden dataset, same metrics, six platforms
- DeepEval's `evaluate()` runs against each platform adapter
- Comparative scorecard shows where each platform excels/fails
- This IS the framework evaluation template filled with real data

## Scorecard Output

- Standardised scorecard per platform (DeepEval's built-in reporting)
- Comparative scorecard across platforms
- Maps directly to the evaluation framework's four layers
- Exportable as JSON for the compliance dashboard

## What it demonstrates

- The RAG evaluation harness in action — not theoretical, running on real data
- DeepEval as the engine, chapter harness as the reusable interface
- Same framework powering both CI/CD gates and real-time compliance
- Golden dataset methodology with graded relevance
- Configurable thresholds by risk tier
- The chapter's evaluation framework applied to a real system
