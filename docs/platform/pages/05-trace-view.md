# Trace View

**Route:** `/traces/[id]`
**Purpose:** Step-level execution trace for a given solution run, demonstrating the platform's observability layer.

---

## What It Shows

A pre-recorded trace showing every step in a solution's execution pipeline. Proves that the platform provides full observability — every step, every cost, every check is traced and auditable.

### Trace Table

| Column | Description |
|--------|-------------|
| **Step** | Sequential step number |
| **Label** | What happened at this step (e.g. "Context retrieval", "LLM generation", "Guardrail pipeline") |
| **Duration** | Time in milliseconds |
| **Detail** | Specifics — chunks retrieved, tokens used, cost, scores, pass/fail counts |

### What Gets Traced

The trace captures the full request/response chain:

- **Query intake** — request received
- **Scope check** — topic classification and in-scope determination
- **Context retrieval** — chunks retrieved, relevance scores, search strategy
- **LLM generation** — model used, token count, cost, citations produced
- **Guardrail pipeline** — all checks run, individual results, aggregate pass/fail
- **Response delivery** — total end-to-end latency

For ML solutions, the trace covers:
- **Feature engineering** — features prepared, protected attributes flagged
- **Model inference** — prediction output
- **Explanation generation** — SHAP values, top contributing factors
- **Fairness guardrails** — all fairness checks and their results

### Trace Examples (Pre-recorded)

| Solution | Steps | Total Latency | Notable |
|----------|-------|---------------|---------|
| PetSure Policy Q&A | 6 | 1,659ms | Full RAG pipeline with 8/8 guardrails pass |
| Model Validation Agent | 7 | 3,945ms | Multi-step agentic workflow with findings |
| Multi-Platform Agent | 5 | 2,105ms | Response blocked at guardrail step (PII fail) |
| Credit Default Scorer | 6 | 100ms | ML inference with SHAP explanation and fairness checks |

---

## Data Sources

- Trace steps from `solutionTraces` record in `lib/data.ts` (keyed by solution ID)
- Also rendered inline on the [Solution Detail Page](02-solution-detail.md) via the `TraceView` component

---

## Key Components

| Component | File | Role |
|-----------|------|------|
| `TracePage` | `app/traces/[id]/page.tsx` | Full-page trace view with header and table |
| `TraceView` | `components/detail/TraceView.tsx` | Reusable trace rendering (used inline on solution detail) |

---

## Demo Narrative

Alex sees the trace for the Q&A Agent — query received, scope checked in 12ms, 4 chunks retrieved in 120ms, LLM generated in 1.3s at $0.0034, 8 guardrails passed in 187ms, response returned in 1.66s total. Every step is auditable.

For the blocked Multi-Platform Agent, the trace shows the PII failure at step 4 and the response being blocked at step 5. The failure is visible in the execution flow, not just in a summary.

**Key impression:** "Every interaction is fully traced — step-level observability, cost tracking, and an audit trail a regulator would accept."
