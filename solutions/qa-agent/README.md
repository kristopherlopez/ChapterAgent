# Q&A Agent — CBA Annual Report

Demo Solution #1: Answers questions about CBA's 2025 Annual Report with source citations.

## What It Does

Given a question, the agent:
1. Checks scope against the topic graph (7 topics, 3 scope levels)
2. Retrieves relevant context via hybrid search (ChromaDB)
3. Generates a grounded answer with citations (OpenAI SDK)
4. Returns structured JSON with citations, guardrail results, and metadata

## Structure

```
qa-agent/
  solution.yaml         # Solution manifest (id: cba-annual-report-qa)
  topic_graph.json      # 7 topic clusters with keywords
  knowledge_base/       # 7 synthetic markdown files (~400 words each)
  golden_dataset/       # 50 test cases across 10 query types
  scenarios/            # Pre-recorded pass/fail scenarios
  src/
    ingest.py           # Chunk and embed documents into ChromaDB
    retrieve.py         # Hybrid retrieval (vector + keyword)
    generate_openai.py  # Answer generation — OpenAI Agent SDK
    agent.py            # Full pipeline orchestrator
```

## Run Standalone

Requires `OPENAI_API_KEY` environment variable.

```bash
cd solutions/qa-agent
python -m src.agent
```

## Risk Tier

`production_customer_facing` — strictest guardrails, highest thresholds.

## Guardrails

7 guardrails: prompt injection, scope containment, PII, bias, toxicity, citation coverage (>= 0.95), temporal accuracy. Faithfulness is assessed via the DeepEval evaluation metric, not as a real-time guardrail.

## Golden Dataset

50 test cases: 15 direct factual, 8 multi-fact, 5 temporal, 5 tabular, 5 interpretive, 4 scope refusal, 3 scope boundary, 2 financial advice, 2 prompt injection, 1 PII probe.
