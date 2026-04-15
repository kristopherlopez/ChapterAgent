# Governance Portal

An AI governance platform that automates compliance, guardrails, and evaluation for AI solutions. Replaces manual governance processes with compliance-as-code — automated deployment gates, reusable safety components, and real-time monitoring through a unified portal.

**Core idea:** Teams build AI solutions using whatever framework they choose. The platform provides reusable governance components that every solution plugs into. The portal makes it all visible.

---

## Architecture

```
+------------------------------------------------------------------+
|                     Unified Portal (Next.js)                      |
|  Compliance dashboard | Solution detail | Evidence export        |
|  Solution registry    | Trace view      | Dataset explorer       |
|  Field catalogue      |                 |                        |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|                      API / Backend (FastAPI)                       |
|  Solution discovery | Result aggregation | Agent chat             |
+------------------------------------------------------------------+
         |
         +---------------------------+
         |                           |
         v                           v
+------------------+    +---------------------------+
| Platform Core    |    | Solutions                 |
|                  |    |                           |
| - Guardrails     |    | - Q&A Agent (RAG)         |
| - Evaluation     |    | - Validation Agent        |
| - Compliance     |    | - Classification Agent    |
|   Gates          |    | - Credit Approval Scorer  |
| - Observability  |    | - Credit Default Scorer   |
+------------------+    +---------------------------+
```

### Design Principles

- **Portal-first** — every component exists to populate the portal
- **Reusable components, not frameworks** — teams choose their orchestration; the platform provides guardrails, evaluation, and compliance
- **Config-driven** — guardrail rules, thresholds, and risk tiers defined in YAML
- **Solution self-registration** — add a solution by dropping a folder with a `solution.yaml` manifest
- **Human-reviewable** — all artifacts (config, results, evidence, traces) are readable without tooling

---

## Platform Components

### Guardrail Framework (8 guardrails)

| Guardrail | Purpose |
|-----------|---------|
| Scope Adherence | Enforces topic boundaries via topic graph |
| PII Detection | Scans for personally identifiable information |
| Faithfulness | Validates claims against retrieved context |
| Citation Coverage | Verifies proper source citations |
| Bias Detection | Monitors for demographic/language bias |
| Toxicity Filter | Screens for harmful content |
| Temporal Accuracy | Validates time-sensitive references |
| Prompt Injection | Detects jailbreak/injection attempts |

All guardrails share a unified async interface and return structured pass/warn/fail results.

### Evaluation Harness

Scores solutions against golden datasets using DeepEval metrics: faithfulness, answer relevancy, contextual precision/recall, hallucination, citation coverage, boundary adherence, bias, toxicity, and more. Thresholds scale by risk tier.

### Compliance-as-Code (8 automated gates)

| Gate | Policy | Check |
|------|--------|-------|
| AI-GOV-001 | Registration | Manifest completeness |
| AI-GOV-003 | Evaluation | All metrics pass for risk tier |
| AI-GOV-005 | PII | PII guardrail passes on golden dataset |
| AI-GOV-006 | Guardrails | All configured guardrails pass |
| AI-GOV-007 | Bias & Toxicity | Scores within bounds |
| AI-GOV-008 | Audit Trail | 100% trace coverage |
| AI-GOV-009 | Golden Dataset | Human-reviewed and signed off |
| AI-GOV-010 | Prompt Governance | Prompts version-controlled |

Run the gate: `cd backend && uv run python -m src.platform.compliance.runner --solution-dir ../solutions/qa-agent --verbose`

Exit code 0 = APPROVED, 1 = BLOCKED.

### Observability

Two integration modes:
- **Inline traces** — endpoint embeds trace in JSON response (demo mode)
- **OpenTelemetry** — solutions push spans to platform collector (production mode)

### Reusable Component Catalog

28 discoverable components across guardrails, evaluation, compliance, observability, and tooling — exposed via API at `/api/catalog`.

---

## Demo Solutions

| # | Solution | Type | Risk Tier | Description |
|---|----------|------|-----------|-------------|
| 1 | Q&A Agent | RAG | `production_customer_facing` | Answers questions about PetSure Australia's governance policies with citations. Implemented in Claude SDK, OpenAI SDK, and LangChain. |
| 2 | Validation Agent | Agentic | `production_internal` | Endpoint-based model validator |
| 3 | Classification Agent | Endpoint | `production_internal` | Risk category classification |
| 4 | Credit Approval Scorer | ML | `production_internal` | Logistic regression on UCI Australian Credit dataset |
| 5 | Credit Default Scorer | ML | `production_internal` | Credit card default prediction |

Each solution is self-contained with a `solution.yaml` manifest, golden dataset, evaluation config, and pre-recorded scenarios.

---

## Tech Stack

**Backend:** Python 3.12+, FastAPI, DeepEval, ChromaDB, scikit-learn, pandas, SHAP, MLflow

**Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS 4

**Tooling:** `uv` (Python packages), `npm` (frontend), GitHub Actions (CI), ruff (linting), pytest (tests)

---

## Getting Started

### Prerequisites

- Python 3.12+ with [`uv`](https://docs.astral.sh/uv/)
- Node.js 22+ with `npm`
- API keys in `.env` at project root: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`

### Run the platform

```bash
# Terminal 1 — backend (port 8000)
cd backend
uv run uvicorn src.api.app:app --reload --port 8000

# Terminal 2 — frontend (port 3000)
cd frontend
npm install   # first time only
npm run dev
```

Open `http://localhost:3000` to access the portal. The frontend falls back to hardcoded data when the backend is not running.

### Run the compliance gate

```bash
cd backend
uv run python -m src.platform.compliance.runner \
  --solution-dir ../solutions/qa-agent --verbose
```

### Run tests

```bash
# Backend
uv run pytest backend/tests

# Frontend lint
cd frontend && npm run lint
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/solutions` | List all solutions |
| `GET` | `/api/solutions/{id}` | Solution detail |
| `POST` | `/api/chat/{solution_id}` | Interactive agent chat |
| `GET` | `/api/compliance/dashboard` | Compliance summary |
| `GET` | `/api/compliance/health/{id}` | Real-time compliance health |
| `GET` | `/api/evidence/{id}/download` | Evidence export |
| `GET` | `/api/traces/{id}` | Execution trace steps |
| `GET` | `/api/controls` | Controls register |
| `GET` | `/api/catalog` | Reusable component catalog |
| `POST` | `/api/catalog/generator/generate` | Generate golden dataset test cases |
| `POST` | `/api/solutions/onboard` | Onboard a new solution |

---

## Project Structure

```
GovernancePortal/
  backend/
    src/
      api/           # FastAPI routes
      platform/       # Reusable components (guardrails, evaluation, compliance, observability)
      solutions/      # Solution-specific backends
  frontend/
    src/
      app/            # Next.js pages
      components/     # UI components
      lib/            # Data fetching and utilities
  solutions/
    qa-agent/             # Q&A Agent (RAG with citations)
    governance-policy-qa/ # Governance Policy Agent
  docs/
    platform/         # Platform architecture and component docs
    solutions/        # Solution specifications
    reference/        # Background and research
```

---

## Documentation

Detailed documentation lives in `docs/`:

- **Platform docs** (`docs/platform/`) — architecture, guardrails, compliance gates, evaluation harness, observability, portal pages
- **Solution docs** (`docs/solutions/`) — specifications for each demo solution
- **Reference docs** (`docs/reference/`) — background research and context

---

## Adding a New Solution

1. Create a directory under `solutions/` with a `solution.yaml` manifest
2. Define guardrails, evaluation metrics, and risk tier in the manifest
3. Add a golden dataset (`golden_dataset/dataset.json`)
4. Run the compliance gate to validate
5. The portal auto-discovers the solution via manifest

Or use the onboarding API: `POST /api/solutions/onboard`
