# Platform Implementations

## Why Six Platforms

This isn't about picking a winner. It's about proving three things:
1. **The reusable components are genuinely framework-agnostic** -- same context retrieval, guardrails, evaluation, observability across all six
2. **Framework evaluation is a real skill** -- the comparative scorecard IS the framework evaluation template filled out with real data
3. **Building for the future** -- today's best framework might not be tomorrow's. The chapter's job is to make squads productive regardless of which framework they choose

The six platforms span three categories -- this is deliberate:

| Category | Platforms | What it proves |
|---|---|---|
| **Provider SDKs** | OpenAI Agents SDK, Claude Agent SDK | LLM providers ship their own agent frameworks -- the chapter can support either without lock-in |
| **Orchestration Frameworks** | LangChain, LangGraph, CrewAI | The open-source ecosystem offers different paradigms (chains, graphs, crews) -- the chapter evaluates them on real data |
| **Enterprise Frameworks** | Semantic Kernel | Microsoft's play for enterprise AI -- CBA is an Azure shop, this is the expected choice. Including it alongside five alternatives shows rigour, not default |

## Platform 1: LangChain (Python)

**Why included:** The most widely adopted LLM framework. Massive ecosystem of integrations, connectors, and community knowledge. Listed in the JD (LangChain/LangGraph). Represents the "ecosystem breadth" approach.

**Implementation:**
- `ChatModel` + `RunnableSequence` chain: retrieval → guardrails → generation → compliance
- LangChain's native retriever interface wrapping the shared Context Retrieval Framework
- `Tool` definitions mapped to shared components
- LangChain's callback system feeding into the shared observability layer (LangFuse has native LangChain integration)

**Retrieval strategy:** LangChain's retriever abstraction — `EnsembleRetriever` for hybrid search (vector + BM25), `MultiQueryRetriever` for query expansion, `SelfQueryRetriever` for metadata filtering. Maps naturally to strategies 1-3 in the Context Retrieval Framework.

**Demonstrates:** The "lingua franca" of LLM development. Most data scientists know LangChain. If a squad only knows one framework, it's probably this one. Shows the chapter can support the most common choice.

## Platform 2: LangGraph (Python)

**Why included:** LangChain's graph-based orchestration layer for stateful, multi-step agent workflows. Listed in the JD. Represents the "agent-as-a-graph" paradigm — explicitly modelling decision points, cycles, and conditional logic as nodes and edges.

**Implementation:**
- `StateGraph` with explicit nodes: `retrieve`, `evaluate_sufficiency`, `generate`, `compliance_check`, `respond`
- Conditional edges: if retrieval is insufficient → re-retrieve with reformulated query (agentic retrieval as a graph cycle)
- Human-in-the-loop as a graph interrupt: `interrupt_before=["high_risk_action"]`
- Checkpointing for conversation state persistence
- Subgraphs for the compliance pipeline (each gate is a node, the pipeline is a subgraph)

```
                    +----------+
                    |  START   |
                    +----+-----+
                         |
                         v
                  +------+------+
                  |  Retrieve   |
                  +------+------+
                         |
                         v
              +----------+----------+
              | Evaluate Sufficiency|
              +----------+----------+
                    |           |
              sufficient   insufficient
                    |           |
                    v           v
              +-----+--+  +---+--------+
              |Generate |  | Reformulate|
              +-----+---+  | & Re-fetch |
                    |       +---+--------+
                    |           |
                    |     (cycles back to Retrieve)
                    v
           +-------+--------+
           |Compliance Gates |
           | (subgraph)      |
           +-------+---------+
                   |
              pass | fail
                   |     |
                   v     v
             +-----++ +--+------+
             |Respond| |Regenerate|
             +------++ +---------+
```

**Retrieval strategy:** Agentic retrieval implemented as graph cycles. The agent retrieves, evaluates whether it has enough context, and either proceeds or loops back with a refined query. This is strategy #5 (Agentic Retrieval) expressed as a visual, debuggable graph — every decision point is a node you can inspect.

**Demonstrates:** The most sophisticated orchestration pattern. Graph-based workflows make complex agent logic explicit, debuggable, and auditable — critical for risk management. The compliance pipeline as a subgraph shows how governance integrates into the workflow, not bolted on after. LangGraph's `interrupt` feature is a natural fit for human-in-the-loop gates.

**LangChain vs LangGraph — why both:**
- LangChain = chains (linear, sequential). Good for straightforward RAG pipelines.
- LangGraph = graphs (stateful, cyclical, conditional). Good for complex agent workflows with decision points.
- A squad building a simple Q&A tool uses LangChain. A squad building a multi-step validation agent uses LangGraph. The chapter supports both — same reusable components, different orchestration complexity.

## Platform 3: CrewAI (Python)

**Why included:** Popular open-source multi-agent framework. Strong community. Represents the "role-based multi-agent" approach — agents defined by role, goal, and backstory.

**Implementation:**
- Single agent with tools: `retrieve_knowledge`, `check_guardrails`, `format_citation`, `log_trace`
- CrewAI's built-in memory for conversation context
- Task-based execution model

**Retrieval strategy:** Task-based agentic retrieval. CrewAI's task model naturally decomposes complex queries into subtasks, each with its own retrieval step.

**Demonstrates:** How a squad might build with a high-level framework -- fast to prototype, opinionated structure. Also previews multi-agent patterns (e.g., a "retrieval agent" and a "compliance agent" working together).

## Platform 4: Semantic Kernel (.NET/Python)

**Why included:** Microsoft's framework. CBA is an Azure shop. This is the enterprise-aligned choice. Supports both .NET and Python. Listed in the JD.

**Implementation:**
- Kernel with plugins: KnowledgeBasePlugin, GuardrailPlugin, ObservabilityPlugin
- Semantic Kernel's native planner for multi-step reasoning
- Azure OpenAI as the LLM backend

**Retrieval strategy:** Plugin-based tool retrieval. Each knowledge domain is a plugin the kernel can invoke. Maps to strategy #6 (Tool-Based Retrieval).

**Demonstrates:** Enterprise integration path. How the chapter would support squads on the Microsoft stack. Shows CBA-relevant technology choices without defaulting to them.

## Platform 5: OpenAI Agents SDK (Python)

**Why included:** OpenAI's official agent framework. Listed in the JD. Represents the "platform provider" approach.

**Implementation:**
- Agent with function tools mapped to shared components
- OpenAI's built-in tool calling and structured outputs
- Guardrails implemented as OpenAI's native guardrail features + shared guardrail layer

**Retrieval strategy:** Function calling for tool-based retrieval. Structured outputs for consistent response formatting.

**Demonstrates:** How to work within a provider's ecosystem while keeping components portable

## Platform 6: Claude Agent SDK (Python)

**Why included:** Anthropic's agent framework. Demonstrates awareness of the competitive landscape and willingness to evaluate alternatives. Claude's strong reasoning and safety focus aligns with risk management.

**Implementation:**
- Agent with MCP tools mapped to shared components
- Claude's extended thinking for complex reasoning traces
- Native safety features complementing the shared guardrail layer

**Retrieval strategy:** Harness-native retrieval (strategy #7). The Claude adapter can use direct file access (Read, Glob, Grep) alongside MCP tools — the most sophisticated pattern, mirroring how Claude Code actually works. No embedding layer required for structured knowledge bases.

**Demonstrates:** Multi-provider strategy. The chapter shouldn't be locked to one LLM provider. The harness-native retrieval pattern shows where agent-based context retrieval is heading.

## Cross-Platform Comparison

The evaluation harness runs the same golden dataset against all six implementations and produces a comparative scorecard:

| Metric | LangChain | LangGraph | CrewAI | Semantic Kernel | OpenAI SDK | Claude SDK |
|---|---|---|---|---|---|---|
| Ctx Precision | | | | | | |
| Ctx Recall | | | | | | |
| Faithfulness | | | | | | |
| Answer Relevancy | | | | | | |
| Boundary Adherence | | | | | | |
| Avg Latency (ms) | | | | | | |
| Avg Cost per Query | | | | | | |
| Compliance Pass Rate | | | | | | |
| Retrieval Strategy Used | Hybrid | Agentic (graph) | Task-based | Plugin-based | Tool calling | Harness-native |

This scorecard IS the framework evaluation template (Section 5 of reusable components) filled out with real data. It turns a theoretical framework into a practical tool.

**The narrative this enables:**
"Six platforms. Same reusable components. Same evaluation harness. Same compliance pipeline. The scorecard tells you which framework fits which use case — not based on a vendor pitch, but based on measured performance against the same golden dataset. That's how the chapter would evaluate any framework a squad proposes."
