# Component #1: Context Retrieval Framework

RAG is one retrieval strategy — and already the least sophisticated. The agent demonstrates a **Context Retrieval Framework** that supports multiple strategies, with the agent choosing the best approach per query. The framework is the reusable component; the strategies are pluggable. This is what "building for the future" looks like in practice.

## The Problem with RAG-Only Thinking

RAG (embed → search → retrieve → stuff into prompt) assumes:
- All knowledge is in documents that can be chunked
- Similarity search is the best way to find relevant context
- The retrieval step is a single, static operation
- The query as-stated is sufficient to find what's needed

These assumptions break down quickly. A question like "How does the team build plan connect to the compliance-as-code strategy?" requires reasoning across multiple documents, not just finding the most similar chunk. An agent that can only do vector search will retrieve fragments; an agent with richer retrieval strategies will synthesise.

## Retrieval Strategy Spectrum

The framework supports a spectrum from simple to sophisticated. The agent selects the strategy (or combination) based on query complexity, and the trace panel shows which strategy was used and why.

```
RETRIEVAL STRATEGIES (simple → sophisticated)

1. Vector Search (Classic RAG)
   Query → Embed → Similarity Search → Top-K Chunks
   Best for: Direct factual questions ("What's the team size target?")

2. Contextual Retrieval
   Chunks pre-enriched with document-level context before embedding.
   Each chunk carries a preamble: "This chunk is from [document] about
   [topic] in the context of [broader section]."
   Better semantic matching — reduces the "lost in the middle" problem.
   Best for: Questions where chunk-level text is ambiguous without context

3. Hybrid Search (Vector + Keyword)
   Combines semantic similarity with BM25 keyword matching.
   Catches exact terms that embedding models may miss.
   Best for: Questions referencing specific terminology ("ContextualPrecisionMetric")

4. Knowledge Graph Traversal
   Entities and relationships extracted from documents into a graph.
   Retrieval follows edges: "team build" → "hiring sequence" → "roles" → "skills"
   Best for: Relationship questions ("How does X connect to Y?")

5. Agentic Retrieval (Multi-Step)
   Agent reasons about what information it needs, retrieves, evaluates
   sufficiency, retrieves more if needed. May reformulate the query,
   decompose into sub-queries, or follow chains of reasoning.
   Best for: Complex questions requiring synthesis across multiple topics

6. Tool-Based Retrieval (MCP / Function Calling)
   Context sources exposed as tools the agent can call. Each tool has
   a description — the agent decides which tools to invoke based on
   the query. Not searching a vector store; calling a structured interface.
   Best for: Structured data, APIs, live systems, multi-source queries

7. Harness-Native Retrieval (Claude Code Pattern)
   The agent has direct filesystem access — Read, Glob, Grep. No
   embedding, no vector store. The agent navigates the knowledge base
   like a developer navigates a codebase: search for files by name,
   grep for keywords, read specific sections.
   Best for: When the knowledge base is structured (like a codebase)
   and the agent is sophisticated enough to navigate it
```

## How the Agent Uses Multiple Strategies

The agent doesn't pick one strategy statically. It evaluates the query and selects the best approach — or chains strategies together. The trace panel makes this visible.

```
CONTEXT RETRIEVAL (this response)
  Query: "How does the team build plan connect to compliance-as-code?"

  Strategy selected: Agentic Retrieval (multi-step)
  Reasoning: "Query requires synthesis across two topics"

  Step 1: Vector search → "team build plan" → 3 chunks retrieved
  Step 2: Vector search → "compliance-as-code" → 3 chunks retrieved
  Step 3: Knowledge graph → traversed "team build" → "ML engineer role"
          → "CI/CD pipeline" → "compliance gates" (2 relationship edges)
  Step 4: Sufficiency check → PASS (both topics covered with connection path)

  Total chunks: 6 + 2 graph edges
  Retrieval time: 340ms
  Strategy: multi-step with graph augmentation
```

Compared to a simple factual query:

```
CONTEXT RETRIEVAL (this response)
  Query: "How many people in the initial team?"

  Strategy selected: Vector Search (classic RAG)
  Reasoning: "Direct factual question, single topic"

  Step 1: Vector search → "team build" → 2 chunks retrieved
  Sufficiency check → PASS

  Total chunks: 2
  Retrieval time: 85ms
  Strategy: single-step vector search
```

## Implementation (Progressive Build)

The framework is built incrementally. Each strategy adds capability without replacing the previous ones.

| Phase | Strategy Added | Implementation |
|---|---|---|
| Phase 1 | Vector Search + Contextual Retrieval | ChromaDB, OpenAI embeddings, Anthropic-style chunk preambles |
| Phase 1 | Hybrid Search | ChromaDB vector + BM25 keyword, reciprocal rank fusion |
| Phase 2 | Agentic Retrieval | Agent evaluates query complexity, decomposes multi-topic queries, iterates until sufficient |
| Phase 3 | Knowledge Graph | Extract entities/relationships from blueprint docs into NetworkX or Neo4j. Graph traversal for relationship queries |
| Phase 3 | Tool-Based Retrieval (MCP) | Blueprint sections exposed as MCP tools. Agent calls `get_team_plan()`, `get_compliance_framework()` etc. |
| Phase 3 | Harness-Native | Direct file access for the Claude SDK adapter — demonstrate the Claude Code pattern |

## The Router (Strategy Selection)

A lightweight classifier (or the LLM itself) categorises the query and selects the strategy:

```python
class RetrievalRouter:
    """Selects retrieval strategy based on query characteristics."""

    def route(self, query: str) -> RetrievalStrategy:
        analysis = self.analyse_query(query)

        if analysis.is_factual and analysis.single_topic:
            return VectorSearchStrategy()  # fast, simple

        if analysis.has_specific_terms:
            return HybridSearchStrategy()  # vector + keyword

        if analysis.asks_about_relationships:
            return KnowledgeGraphStrategy()  # graph traversal

        if analysis.requires_synthesis:
            return AgenticRetrievalStrategy()  # multi-step

        # Default: hybrid (good enough for most queries)
        return HybridSearchStrategy()

    def analyse_query(self, query: str) -> QueryAnalysis:
        """Fast classification — LLM call or trained classifier."""
        ...
```

## What Each Platform Demonstrates

Different platforms handle retrieval differently — the framework adapts:

| Platform | Primary Strategy | Why |
|---|---|---|
| LangChain | Hybrid Search (EnsembleRetriever) | Native retriever abstractions, vector + BM25 fusion, broadest connector ecosystem |
| LangGraph | Agentic Retrieval (graph cycles) | Retrieve → evaluate sufficiency → re-retrieve loop as explicit graph nodes. Most debuggable agentic pattern. |
| CrewAI | Agentic Retrieval (task-based) | CrewAI's task model naturally decomposes complex queries into subtasks with independent retrieval |
| Semantic Kernel | Tool-Based (plugins) | SK's plugin architecture maps to tool-based retrieval — each knowledge domain is a plugin |
| OpenAI Agents SDK | Function Calling | Tools as retrieval sources, structured outputs for consistent response formatting |
| Claude Agent SDK | Harness-Native + MCP | Direct file access (Read/Glob/Grep) + MCP tools — the most sophisticated pattern, mirrors how Claude Code actually works |

This means the cross-platform comparison isn't just "same agent, different framework" — it's "same knowledge, different retrieval strategies, comparable outcomes." That's the real insight: the evaluation harness measures retrieval quality regardless of HOW the context was retrieved.

## Source Documents (the team blueprint)

- Team vision and strategy
- Team build plan (5 -> 10, hiring sequence, onshore/offshore)
- Reusable component definitions (evaluation harness, guardrails, CI/CD, compliance-as-code)
- Unified portal design (5 layers)
- 90/180/365 day roadmap
- Stakeholder engagement model
- Framework evaluation template
- Kris's background and proof points (PetSure, Chubb, greenfield builds)

## Evaluation — Strategy-Aware

The evaluation harness (Component #4) evaluates retrieval quality regardless of strategy. DeepEval's ContextualPrecision and ContextualRecall work the same whether the chunks came from vector search, graph traversal, or tool calls. The scorecard adds a strategy breakdown:

| Metric | Vector | Hybrid | Agentic | Graph | Overall |
|---|---|---|---|---|---|
| Contextual Precision | 0.82 | 0.86 | 0.91 | 0.88 | 0.85 |
| Contextual Recall | 0.71 | 0.78 | 0.89 | 0.83 | 0.79 |
| Avg Retrieval Time | 85ms | 120ms | 340ms | 190ms | 165ms |

This shows the tradeoffs: agentic retrieval is more accurate but slower. The Governance Portal defines when each strategy is appropriate — teams configure the router for their use case.

## What it demonstrates

- Context retrieval is bigger than RAG — the Governance Portal builds for where this is going
- Strategy selection as a reusable pattern — the router is a component teams consume
- Same evaluation framework works regardless of retrieval method
- Each platform naturally gravitates toward different strategies — proving framework agnosticism
- The Claude Code pattern (harness-native retrieval) as the most advanced approach — agents that navigate knowledge like developers navigate code
- Citation traceability works across all strategies — governance doesn't break when retrieval evolves
