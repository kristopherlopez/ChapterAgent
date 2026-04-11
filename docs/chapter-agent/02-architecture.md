# Architecture

## Core Principle: Reusable Components, Not Reusable Frameworks

The agent is built on a **shared core** with **platform-specific adapters**. The reusable components (knowledge base, guardrails, evaluation, observability) are framework-agnostic. The orchestration layer swaps out. This mirrors exactly how the chapter would operate: build the components once, let squads choose their orchestration framework.

## System Diagram

```
+------------------------------------------------------------------+
|                        Web UI (Shared)                            |
|  - Chat interface                                                 |
|  - Platform selector (CrewAI | Semantic Kernel | OpenAI | Claude) |
|  - Component trace panel (shows which components were invoked)    |
|  - Evaluation scorecard display                                   |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|                    API Gateway / Router                            |
|  - Routes to selected platform adapter                            |
|  - Request/response logging                                       |
|  - Cost tracking per platform                                     |
+------------------------------------------------------------------+
         |
         +--------+---------+---------+---------+
         |        |         |         |         |
         v        v         v         v         v
+--------+  +---------+ +-------+ +-------+ +----------+
| CrewAI |  |Semantic | |OpenAI | |Claude | | Shared   |
| Adapter|  |Kernel   | |Agents | |Agent  | | Core     |
|        |  |Adapter  | |SDK    | |SDK    | |          |
+--------+  +---------+ +-------+ +-------+ +----------+
         |        |         |         |         |
         +--------+---------+---------+---------+
                            |
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
+-------------------+ +----------------+ +------------------+
| Context Retrieval | | Guardrail      | | Observability    |
| Framework         | | Framework      | | Layer            |
|                   | |                | |                  |
| - Router (selects | | - Boundary     | | - Step tracing   |
|   strategy)       | |   adherence    | | - Token counting |
| - Vector Search   | | - PII masking  | | - Latency logs   |
| - Hybrid Search   | | - Scope        | | - Component      |
| - Knowledge Graph | |   containment  | |   attribution    |
| - Agentic (multi- | | - Input/output | | - Audit trail    |
|   step retrieval) | |   filtering    | | - Retrieval      |
| - Tool-Based /MCP | |                | |   strategy log   |
| - Harness-Native  | |                | |                  |
| - Citations       | |                | |                  |
+-------------------+ +----------------+ +------------------+
         |                  |                  |
         +------------------+------------------+
         |                                     |
         v                                     v
+-------------------+               +-------------------+
| Evaluation        |               | Compliance-as-Code|
| Harness (DeepEval)|               | Pipeline          |
|                   |               |                   |
| - Golden dataset  |               | - Policy gates    |
| - Retrieval eval  |               | - DeepEval checks |
|   (strategy-aware)|               | - Evidence gen    |
| - Generation eval |               | - Real-time trace |
| - Cross-platform  |               |                   |
| - Scorecard       |               |                   |
+-------------------+               +-------------------+
```

## Component Breakdown

| # | Component | Doc |
|---|---|---|
| 1 | Context Retrieval Framework | [03-context-retrieval.md](03-context-retrieval.md) |
| 2 | Guardrail Framework | [04-guardrails.md](04-guardrails.md) |
| 3 | Observability Layer | [05-observability.md](05-observability.md) |
| 4 | Evaluation Harness (DeepEval) | [06-evaluation-harness.md](06-evaluation-harness.md) |
| 5 | Compliance-as-Code Pipeline | [07-compliance-as-code.md](07-compliance-as-code.md) |
