# Tech Stack

The tech stack is organised by function, not by vendor. Every layer has a primary choice and alternatives — because the chapter's job is to evaluate options and make defensible recommendations, not pick favourites.

## 1. Model Gateway & LLM Providers

| Component | Technology | Why |
|---|---|---|
| **Model Gateway** | Custom gateway (thin abstraction over provider SDKs) | Unified interface across LLM providers. One call signature, provider resolved by config. Handles retries, fallbacks, spend tracking. No third-party proxy — direct SDK calls with a shared wrapper. |
| OpenAI | GPT-4o, GPT-4o-mini | Primary generation model (4o) and real-time compliance judge (4o-mini) |
| Azure OpenAI | GPT-4o (Azure-hosted) | Same models, Australian data residency option. CBA-relevant for data sovereignty. Semantic Kernel adapter uses this. |
| Anthropic | Claude Sonnet 4.6 | Claude adapter. Extended thinking for complex reasoning. Strong safety alignment for risk management. |
| **Embeddings** | OpenAI `text-embedding-3-small` | Primary embedding model. Cost-effective, good quality. |
| Embeddings (alternative) | Cohere `embed-v4` | Alternative for evaluation. Shows the chapter doesn't default to one provider. |
| Embeddings (local) | `sentence-transformers` (all-MiniLM-L6-v2) | Local embedding option for data sovereignty scenarios — nothing leaves the network. Demonstrates awareness of regulated environment constraints. |

**Why a custom gateway over third-party proxies:**

Third-party model gateways (e.g., LiteLLM) introduce supply chain risk — LiteLLM was recently compromised in a security incident. In a regulated environment like CBA, every dependency in the LLM call chain is an attack surface. The chapter builds a thin abstraction instead: direct SDK calls to each provider, wrapped in a shared interface for consistency.

```python
from chapter_gateway import completion

# Same interface, direct SDK calls — no third-party proxy
response = completion(provider="openai", model="gpt-4o", messages=[...])
response = completion(provider="azure", model="gpt-4o", messages=[...])
response = completion(provider="anthropic", model="claude-sonnet-4-6", messages=[...])

# Spend tracking via LangFuse callback, not a proxy layer
# Retries and fallbacks handled in the gateway, auditable in code
```

This is a chapter design decision worth discussing in the interview: convenience vs supply chain security. In banking, direct SDK calls with a thin wrapper beat a third-party proxy every time. The gateway is simple Python — auditable, no external dependencies in the critical path.

## 2. Context Retrieval Layer

| Component | Technology | Why |
|---|---|---|
| **Vector Store** | ChromaDB (local dev) / Qdrant (hosted demo) | ChromaDB for fast local iteration. Qdrant for production — filtering, payload storage, hybrid search built in. |
| Vector Store (alternative) | pgvector (PostgreSQL) | For squads already on PostgreSQL. No new infrastructure. Shows the chapter supports "meet squads where they are." |
| **Reranking** | Cohere Rerank 3.5 (`cohere.rerank`) | Cross-encoder reranking after initial retrieval. Dramatically improves precision — re-scores chunks by semantic relevance, not just embedding similarity. The difference between "found 10 chunks" and "found the right 3." |
| **Hybrid Search** | BM25 (rank-bm25) + vector, reciprocal rank fusion | Keyword search catches exact terms embeddings miss. Fused with vector results via RRF. LangChain's `EnsembleRetriever` wraps this natively. |
| **Knowledge Graph** | Neo4j (hosted) or NetworkX (local) | Entity-relationship graph for GraphRAG. Traversal for "how does X connect to Y" queries. Neo4j for production scale, NetworkX for the demo. |
| **Document Processing** | Unstructured.io (`unstructured`) | Parses PDFs, Word docs, HTML, slides into clean text with metadata. The chapter would use this to ingest policy documents, APRA standards, model documentation. In the demo, it processes the blueprint documents. |
| **Chunking** | Semantic chunking (`langchain.text_splitter.SemanticChunker`) + contextual enrichment | Chunks split at semantic boundaries (not fixed token counts). Each chunk enriched with document-level context preamble before embedding — Anthropic's contextual retrieval pattern. |
| **Query Transformation** | Multi-query generation, HyDE (Hypothetical Document Embeddings) | For complex queries: generate multiple search queries from different angles, or generate a hypothetical answer and search for chunks similar to it. Improves recall on ambiguous questions. |
| **Caching** | Redis + semantic similarity cache | Cache embeddings and LLM responses. Exact match cache for repeated queries. Semantic similarity cache for paraphrased queries (same question asked differently → cached answer). Reduces cost and latency at scale. |

**Retrieval pipeline in practice:**
```
Query → Query Transformation (multi-query / HyDE)
      → Hybrid Search (vector + BM25 via RRF)
      → Reranking (Cohere Rerank 3.5)
      → Contextual chunks with citations
      → (if insufficient) Agentic re-retrieval via LangGraph cycle
```

## 3. Structured Outputs & Type Safety

| Component | Technology | Why |
|---|---|---|
| **Structured Outputs** | Pydantic + Instructor (`instructor`) | Forces LLM responses into typed Python objects. No parsing, no regex, no "hope it returns JSON." Every response is a validated data structure. |
| **Response Models** | Pydantic models per response type | `ChapterAnswer(content, citations, confidence, retrieval_strategy)`. Type-safe from LLM output to UI rendering. |

```python
import instructor
from pydantic import BaseModel

class ChapterAnswer(BaseModel):
    content: str
    citations: list[Citation]
    confidence: float
    retrieval_strategy: str
    components_used: list[str]

# Every LLM response is a validated, typed object
# No string parsing, no hope-based JSON extraction
client = instructor.from_openai(openai_client)
answer = client.chat.completions.create(
    model="gpt-4o",
    response_model=ChapterAnswer,
    messages=[...]
)
```

**Why this matters for the chapter:** Every squad's agent returns structured, typed outputs. The evaluation harness can assert on fields (`assert answer.confidence > 0.7`). The compliance pipeline can check specific fields. The UI renders typed data, not parsed strings. This is the difference between "AI that returns text" and "AI that returns auditable, structured decisions."

## 4. Guardrails & Safety

| Component | Technology | Why |
|---|---|---|
| **Guardrail Framework** | NVIDIA NeMo Guardrails (`nemoguardrails`) | Enterprise-grade guardrail orchestration. Defines rails in Colang (a conversation modelling language). Input rails, output rails, and topical rails as first-class concepts. |
| **Guardrail Alternative** | Guardrails AI (`guardrails-ai`) | Pydantic-based validation for LLM outputs. Validators as reusable components. Good for structured output validation. |
| **Prompt Injection Detection** | Rebuff + custom classifier | Dedicated prompt injection detection layer. Rebuff uses a multi-layered approach (heuristics, LLM-based, vector similarity to known attacks). Critical for any agent exposed to user input. |
| **PII Detection** | Microsoft Presidio (`presidio-analyzer`, `presidio-anonymizer`) | Entity recognition for PII (names, emails, phone numbers, ABN/TFN for Australia). Detects AND anonymises. Open-source, runs locally — no data sent externally. |
| **Content Safety** | OpenAI Moderation API + custom filters | Fast content classification (toxicity, hate, self-harm, violence). Free tier from OpenAI. Custom filters for domain-specific boundaries. |
| **Custom Rails** | Python library (shared component) | Domain-specific guardrails: scope containment, citation enforcement, confidence thresholds. These are the chapter's custom rails that sit alongside NeMo/Guardrails AI. |

**Layered guardrail architecture:**
```
Input → Prompt Injection Detection (Rebuff)
      → PII Detection & Masking (Presidio)
      → Topic Classification (NeMo Rails)
      → [LLM Generation]
      → Output Validation (Guardrails AI / Pydantic)
      → Faithfulness Check (DeepEval)
      → Bias & Toxicity Scan (DeepEval + OpenAI Moderation)
      → PII Output Scan (Presidio)
      → Citation Verification (custom)
      → Response delivered
```

**Why multiple guardrail tools:** No single tool covers everything. NeMo excels at conversational rails. Guardrails AI excels at structured output validation. Presidio excels at PII. Rebuff excels at injection detection. The chapter's job is to compose these into a unified pipeline that squads consume as one component — they call `compliance_check(response)`, the framework runs all layers internally.

## 5. Evaluation & Testing

| Component | Technology | Why |
|---|---|---|
| **Primary Evaluation** | DeepEval (`deepeval`) | LLM-as-a-judge metrics, golden datasets, CI/CD integration. The evaluation engine. |
| **Alternative Evaluation** | RAGAS (`ragas`) | Alternative RAG evaluation framework. Includes context utilisation, noise robustness, and information integration metrics that DeepEval doesn't cover. Running both shows evaluation rigour. |
| **Production Monitoring** | Arize Phoenix (`phoenix`) | Real-time LLM observability in production. Drift detection, embedding visualisation, trace analysis. Complements LangFuse (tracing) with Phoenix (monitoring & analytics). |
| **Test Framework** | pytest + `deepeval` pytest plugin | DeepEval integrates as a pytest plugin: `deepeval test run test_evaluation.py`. Standard Python testing workflow — data scientists don't learn new tools. |
| **Load Testing** | Locust (`locust`) | Simulates realistic query load against the agent. Measures latency degradation under concurrency. Layer 3 (Production Quality) evaluation. |
| **Regression Testing** | Golden dataset + CI/CD gate | Every PR runs the golden dataset. If metrics regress, the PR is blocked. Same pattern the chapter would enforce for squad AI solutions. |

**Why both DeepEval AND RAGAS:**
- DeepEval: faithfulness, answer relevancy, contextual precision/recall, bias, toxicity
- RAGAS: context utilisation (did the LLM actually use what was retrieved?), noise robustness (does quality degrade with irrelevant chunks?), information integration (can it synthesise across chunks?)
- Together: the most comprehensive RAG evaluation coverage available. The comparative report shows the chapter evaluates thoroughly, not just conveniently.

## 6. Observability & Tracing

| Component | Technology | Why |
|---|---|---|
| **LLM Tracing** | LangFuse (`langfuse`) | Open-source LLM observability. Traces every LLM call with latency, tokens, cost. Native integrations with LangChain, LangGraph, OpenAI. The primary trace backend. |
| **Distributed Tracing** | OpenTelemetry (`opentelemetry-sdk`) | Industry-standard distributed tracing. Wraps the entire request lifecycle (API → retrieval → LLM → guardrails → response). Exportable to any OTEL backend. |
| **Production Monitoring** | Arize Phoenix | Embedding drift detection, trace analytics, LLM performance dashboards. The "Grafana for LLM systems." |
| **Cost Tracking** | LangFuse cost tracking + custom gateway logs | Token spend per query, per platform, per model. LangFuse tracks at the trace level. Gateway logs token counts per provider call. Both feed into the trace panel. |
| **Audit Trail** | Custom structured logging → JSON Lines | Every interaction logged as a structured JSON event. Immutable append-only log. Exportable for 2nd/3rd line audit. This is the "can we defend this to a regulator?" evidence. |

**Observability stack in practice:**
```
Request → OpenTelemetry span (distributed trace)
        → LangFuse trace (LLM-specific: tokens, cost, latency)
        → Gateway spend log (provider-level cost tracking)
        → Arize Phoenix (production monitoring, drift)
        → Audit trail (structured JSON, immutable)
        → Trace panel (real-time UI display)
```

## 7. Prompt Management

| Component | Technology | Why |
|---|---|---|
| **Prompt Versioning** | LangFuse Prompt Management or LangSmith Hub | Version-controlled prompts. A/B testing between prompt versions. Rollback capability. Prompts are not hardcoded strings — they're managed artifacts with lineage. |
| **Prompt Templates** | LangChain `PromptTemplate` + Jinja2 | Templated prompts with variable injection. Reusable across platforms. |
| **System Prompts** | Versioned in git + deployed via prompt management | The agent's system prompt (persona, scope, guardrails) is a managed artifact, not a hardcoded string. Changes go through review. |

**Why this matters:** In the demo, the agent's system prompt is versioned. You can show the panel: "This agent is running prompt v2.3. Last change: tightened scope boundaries. Approved by: [human reviewer]." That's prompt governance — the same pattern the chapter would enforce for every squad's prompts.

## 8. Tool & Interface Standards

| Component | Technology | Why |
|---|---|---|
| **Tool Protocol** | MCP (Model Context Protocol) | Anthropic's open standard for tool interfaces. Defines how agents discover and call tools. The chapter would standardise on MCP for tool interoperability across frameworks. |
| **API Interface** | FastAPI (`fastapi`) + Pydantic | Typed API layer routing requests to platform adapters. Auto-generated OpenAPI docs. Request/response validation via Pydantic. |
| **Async** | asyncio + httpx | Non-blocking I/O for concurrent retrieval, guardrail checks, and LLM calls. Critical for the real-time compliance pipeline (multiple checks in parallel). |
| **Task Queue** | Celery or arq (if needed) | For async evaluation jobs (batch golden dataset runs). Not needed for the real-time path. |

## 9. Platform-Specific SDKs

| Platform | LLM Provider | SDK(s) | Retrieval Strategy |
|---|---|---|---|
| LangChain | OpenAI (via gateway) | `langchain`, `langchain-openai`, `langchain-community` | Hybrid search via `EnsembleRetriever`, multi-query via `MultiQueryRetriever` |
| LangGraph | OpenAI (via gateway) | `langgraph`, `langgraph-checkpoint-sqlite` | Agentic retrieval as graph cycles, checkpointed state |
| CrewAI | OpenAI (via gateway) | `crewai`, `crewai-tools` | Task-based decomposition, role-based retrieval agents |
| Semantic Kernel | Azure OpenAI | `semantic-kernel` | Plugin-based tool retrieval, SK planner |
| OpenAI Agents SDK | OpenAI | `openai-agents` | Function calling, structured outputs |
| Claude Agent SDK | Anthropic | `claude-agent-sdk` | MCP tools, harness-native file access, extended thinking |

## 10. Infrastructure & Deployment

| Component | Technology | Why |
|---|---|---|
| **Container Orchestration** | Docker Compose (dev) / ECS Fargate (prod) | Each platform adapter is a container. Compose for local dev. Fargate for the hosted demo — no server management. |
| **CI/CD** | GitHub Actions | Mirrors what the chapter would use. Evaluation harness runs as a CI step — PR blocked if metrics regress. |
| **IaC** | Terraform or AWS CDK | Infrastructure as code for the hosted deployment. Shows the chapter ships infrastructure the same way it ships code — versioned, reviewed, automated. |
| **Secrets** | AWS Secrets Manager | API keys for LLM providers. Rotatable. Auditable access logs. |
| **Monitoring** | CloudWatch + Arize Phoenix | Infrastructure monitoring (CloudWatch) + LLM-specific monitoring (Phoenix). |
| **Domain** | Custom domain via Route53 | e.g., `chapter-agent.kristopherlopez.com` — shareable, professional URL for the demo |

## 11. Data Sovereignty & Security (CBA-Relevant)

| Component | Technology | Why |
|---|---|---|
| **Data Residency** | Azure OpenAI (Australia East region) | LLM inference in Australia. For the Semantic Kernel adapter, all data stays onshore. Demonstrates awareness of CBA's data sovereignty obligations. |
| **Local Embeddings** | `sentence-transformers` | Embedding option where nothing leaves the network. For sensitive document scenarios. |
| **PII Protection** | Presidio (detection) + masking before LLM calls | PII detected and masked BEFORE sending to any LLM. Especially important for models hosted outside Australia. |
| **Prompt Injection** | Rebuff (multi-layer detection) | Protects against adversarial inputs. Critical for any agent exposed to user queries. |
| **Audit Logging** | Immutable JSON Lines + S3 archival | Every interaction logged. Immutable. Archived to S3 with lifecycle policies. APRA-ready evidence trail. |
| **Auth** | NextAuth.js or Streamlit auth | Demo-level authentication. Shows awareness that production agents need access control. |

## Technology Map (Visual)

```
+------------------------------------------------------------------+
|                         WEB UI (Next.js)                          |
|  Platform selector | Chat | Trace panel | Scorecard | Evidence   |
+------------------------------------------------------------------+
         |
+------------------------------------------------------------------+
|                    API LAYER (FastAPI + Pydantic)                  |
|  Request routing | Auth | Rate limiting | OpenTelemetry spans     |
+------------------------------------------------------------------+
         |
+------------------------------------------------------------------+
|              MODEL GATEWAY (Custom — Direct SDK Calls)            |
|  Unified interface | Provider routing | Spend tracking | Fallbacks|
|  OpenAI | Azure OpenAI | Anthropic (no third-party proxy)        |
+------------------------------------------------------------------+
         |
+--------+---------+---------+---------+---------+---------+
|LangChain|LangGraph| CrewAI  |Sem.Kernel|OpenAI  |Claude  |
|Adapter  |Adapter  |Adapter  |Adapter  |Adapter |Adapter |
+---------+---------+---------+---------+--------+--------+
         |
+------------------------------------------------------------------+
|              SHARED REUSABLE COMPONENTS                           |
+------------------------------------------------------------------+
|                                                                    |
| CONTEXT RETRIEVAL          | GUARDRAILS & SAFETY                  |
| - Vector (ChromaDB/Qdrant) | - NeMo Guardrails (conversational)   |
| - Hybrid (BM25 + vector)  | - Guardrails AI (output validation)  |
| - Reranking (Cohere)       | - Presidio (PII detect/mask)         |
| - Knowledge Graph (Neo4j)  | - Rebuff (prompt injection)          |
| - Agentic (multi-step)    | - OpenAI Moderation (content safety) |
| - Tool-based (MCP)        | - DeepEval (faithfulness/bias/tox)   |
| - Harness-native (files)  | - Custom rails (scope/citations)     |
| - Semantic cache (Redis)   |                                      |
| - Query transform (HyDE)  |                                      |
| - Doc processing (Unstruct)|                                      |
|                            |                                      |
| EVALUATION & TESTING       | OBSERVABILITY & AUDIT                |
| - DeepEval (primary)       | - LangFuse (LLM tracing)             |
| - RAGAS (complementary)    | - OpenTelemetry (distributed trace)  |
| - Locust (load testing)    | - Arize Phoenix (monitoring)         |
| - pytest (test framework)  | - Gateway logs (cost tracking)       |
| - Golden dataset (curated) | - Audit trail (JSON Lines → S3)      |
|                            |                                      |
| PROMPT MANAGEMENT          | STRUCTURED OUTPUTS                   |
| - LangFuse/LangSmith      | - Pydantic (type safety)             |
| - Version control          | - Instructor (LLM → typed objects)   |
| - A/B testing              | - Response models per type            |
+------------------------------------------------------------------+
|                                                                    |
| INFRASTRUCTURE                                                     |
| Docker Compose | ECS Fargate | GitHub Actions | Terraform          |
| CloudWatch | Secrets Manager | Route53 | S3 (audit archive)       |
+------------------------------------------------------------------+
```

## Technology Count

| Category | Count | Technologies |
|---|---|---|
| LLM Providers | 3 | OpenAI, Azure OpenAI, Anthropic |
| Agent Frameworks | 6 | LangChain, LangGraph, CrewAI, Semantic Kernel, OpenAI Agents SDK, Claude Agent SDK |
| Retrieval & Search | 8 | ChromaDB, Qdrant, pgvector, Cohere Rerank, BM25, Neo4j, Unstructured, Redis |
| Guardrails & Safety | 6 | NeMo Guardrails, Guardrails AI, Presidio, Rebuff, OpenAI Moderation, custom |
| Evaluation | 4 | DeepEval, RAGAS, Locust, pytest |
| Observability | 3 | LangFuse, OpenTelemetry, Arize Phoenix |
| Structured Outputs | 2 | Pydantic, Instructor |
| Prompt Management | 2 | LangFuse PM, LangSmith Hub |
| Infrastructure | 7 | Docker, ECS Fargate, GitHub Actions, Terraform, CloudWatch, Secrets Manager, S3 |
| Standards | 2 | MCP, OpenTelemetry |
| **Total** | **43** | |

This isn't about using 43 technologies. It's about knowing the landscape well enough to pick the right tool for each problem, evaluate alternatives, and make defensible recommendations — including knowing when NOT to use a popular tool because the supply chain risk outweighs the convenience. That's what a Chapter Area Lead does.
