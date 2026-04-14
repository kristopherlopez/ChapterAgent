# Tech Stack & Project Structure

One choice per slot. No alternatives, no hedging. This is what we're building with.

---

## Tech Stack

### Frontend

| Technology | Purpose |
|---|---|
| Next.js 16 (React 19) | App framework |
| TypeScript | Type safety |
| Tailwind CSS 4 | Styling |
| Lucide React | Icons |
| react-markdown + remark-gfm | Markdown rendering |
| ESLint | Linting |

### Backend

| Technology | Purpose |
|---|---|
| FastAPI + Uvicorn | API framework |
| Pydantic 2 | Data validation, settings, solution manifests |
| Temporal (temporalio) | Workflow orchestration (eval runs, compliance gates) |
| python-dotenv | Environment config |
| Ruff | Python linting and formatting |

### LLM

| Technology | Purpose |
|---|---|
| OpenAI SDK | Default for all demo solutions and platform components |

### RAG

| Technology | Purpose |
|---|---|
| ChromaDB | Vector store |
| OpenAI text-embedding-3-small | Embeddings model |

### Platform Components

| Technology | Purpose |
|---|---|
| DeepEval | Evaluation harness (LLM-as-judge, golden datasets, pytest plugin) |
| Custom Python functions | Guardrail framework (PII, scope, bias, toxicity, citation coverage, temporal accuracy, prompt injection) |
| Structured JSON log files | Observability / trace data |
| JSON / YAML files | All data storage (scenarios, results, manifests, evidence) |

### CI/CD & Infrastructure

| Technology | Purpose |
|---|---|
| GitHub Actions | CI/CD pipeline (Level 1: platform tests, Level 2: solution eval) |
| Docker Compose | Local development, containerised services |

---

## Project Structure

```
chapter-agent/
│
├── docs/                              # Documentation (you're reading it)
│   ├── platform/                      # Platform docs (architecture, components, delivery)
│   │   ├── 00-background.md
│   │   ├── 01-overview.md
│   │   └── ...
│   └── solutions/                     # Solution type taxonomy and demo solution specs
│       ├── 00-solution-types.md
│       ├── 01-qa-agent.md
│       └── ...
│
├── frontend/                          # Next.js portal
│   ├── src/
│   │   ├── app/                       # App router pages
│   │   │   ├── page.tsx               # Landing — compliance health dashboard
│   │   │   ├── solutions/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx       # Solution detail page
│   │   │   ├── scorecard/
│   │   │   │   └── page.tsx           # Multi-platform scorecard
│   │   │   └── traces/
│   │   │       └── [id]/
│   │   │           └── page.tsx       # Observability trace view
│   │   ├── components/                # Shared UI components
│   │   │   ├── dashboard/
│   │   │   │   ├── HealthBadge.tsx
│   │   │   │   ├── SolutionRow.tsx
│   │   │   │   └── ComplianceSummary.tsx
│   │   │   ├── detail/
│   │   │   │   ├── GuardrailResults.tsx
│   │   │   │   ├── EvaluationScores.tsx
│   │   │   │   └── ComplianceGate.tsx
│   │   │   ├── evidence/
│   │   │   │   └── ExportButton.tsx
│   │   │   └── layout/
│   │   │       ├── Sidebar.tsx        # Solution registry nav
│   │   │       └── Header.tsx
│   │   └── lib/                       # API client, types, utils
│   │       ├── api.ts
│   │       └── types.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── eslint.config.js
│
├── backend/                           # FastAPI backend
│   ├── src/
│   │   ├── api/                       # API routes
│   │   │   ├── routes/
│   │   │   │   ├── solutions.py       # Solution registry, detail
│   │   │   │   ├── compliance.py      # Dashboard data, gate results
│   │   │   │   ├── evidence.py        # Evidence export
│   │   │   │   ├── traces.py          # Observability trace data
│   │   │   │   └── scorecard.py       # Multi-platform comparison
│   │   │   └── app.py                 # FastAPI app, router setup
│   │   │
│   │   ├── platform/                  # Platform core — shared components
│   │   │   ├── guardrails/            # Custom guardrail framework
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py            # Base guardrail interface
│   │   │   │   ├── pii.py             # PII detection guardrail
│   │   │   │   ├── scope.py           # Scope containment guardrail
│   │   │   │   ├── bias.py            # Bias detection guardrail
│   │   │   │   ├── toxicity.py        # Toxicity detection guardrail
│   │   │   │   └── runner.py          # Runs all guardrails for a solution
│   │   │   │
│   │   │   ├── evaluation/            # DeepEval evaluation harness
│   │   │   │   ├── __init__.py
│   │   │   │   ├── harness.py         # Evaluation runner
│   │   │   │   ├── metrics.py         # Metric definitions and thresholds
│   │   │   │   └── datasets.py        # Golden dataset loader
│   │   │   │
│   │   │   ├── compliance/            # Compliance-as-code gates
│   │   │   │   ├── __init__.py
│   │   │   │   ├── gate.py            # Deployment gate logic
│   │   │   │   └── evidence.py        # Evidence report generator
│   │   │   │
│   │   │   ├── observability/         # Structured JSON logging
│   │   │   │   ├── __init__.py
│   │   │   │   └── logger.py          # Step-level trace logger
│   │   │   │
│   │   │   └── discovery.py           # Reads solution.yaml manifests
│   │   │
│   │   └── workflows/                 # Temporal workflows
│   │       ├── evaluate_solution.py   # Orchestrates eval + guardrails + gate
│   │       └── activities.py          # Temporal activities
│   │
│   ├── tests/                         # Platform tests (CI/CD Level 1)
│   │   ├── unit/
│   │   │   ├── test_guardrails.py
│   │   │   ├── test_evaluation.py
│   │   │   ├── test_compliance.py
│   │   │   └── test_discovery.py
│   │   └── integration/
│   │       └── test_workflow.py
│   │
│   ├── pyproject.toml
│   └── Dockerfile
│
├── solutions/                         # Demo solutions — each self-contained
│   │
│   ├── qa-agent/                      # Solution #1: Q&A Agent
│   │   ├── solution.yaml              # Manifest (name, risk tier, guardrails, eval config)
│   │   ├── scenarios/
│   │   │   ├── pass/
│   │   │   │   ├── input.json         # Test query
│   │   │   │   └── output.json        # Solution response
│   │   │   └── fail/
│   │   │       ├── input.json
│   │   │       └── output.json
│   │   ├── golden_dataset/
│   │   │   └── dataset.json           # DeepEval golden dataset
│   │   ├── knowledge_base/            # Document corpus
│   │   │   └── *.md
│   │   └── src/                       # Solution code (embedded, OpenAI SDK)
│   │       └── ...
│   │
│   ├── validation-agent/              # Solution #2: Model Validation Agent
│   │   ├── solution.yaml              # type: endpoint
│   │   ├── scenarios/
│   │   │   ├── pass/
│   │   │   └── fail/
│   │   ├── golden_dataset/
│   │   └── src/                       # Standalone FastAPI endpoint
│   │       └── ...
│   │
│   └── classification-agent/          # Solution #3: Risk Classification Agent
│       ├── solution.yaml              # type: endpoint
│       ├── scenarios/
│       │   ├── pass/
│       │   ├── fail/
│       │   └── bias/                  # Demographic variant probes
│       ├── golden_dataset/
│       └── src/                       # Standalone FastAPI endpoint
│           └── ...
│
├── results/                           # Platform output — generated by eval/compliance runs
│   ├── qa-agent/
│   │   ├── pass/
│   │   │   ├── guardrails.json
│   │   │   ├── evaluation.json
│   │   │   └── compliance.json
│   │   └── fail/
│   │       ├── guardrails.json
│   │       ├── evaluation.json
│   │       └── compliance.json
│   ├── validation-agent/
│   │   └── ...
│   └── classification-agent/
│       └── ...
│
├── traces/                            # Pre-recorded observability traces
│   ├── qa-agent/
│   │   └── run_001.json
│   ├── validation-agent/
│   │   └── run_001.json
│   └── classification-agent/
│       └── run_001.json
│
├── .github/
│   └── workflows/
│       ├── ci.yml                     # Level 1: platform unit/integration tests
│       └── eval.yml                   # Level 2: solution eval + compliance gates
│
├── docker-compose.yml
├── .env.example
├── README.md
└── CLAUDE.md
```

---

## Key Structural Decisions

### Solutions are self-contained
Each solution is a folder with a manifest, scenarios, golden dataset, and source code. Drop in a new folder with a `solution.yaml` and the platform discovers it. Remove a folder and it's gone. No central registry to edit.

### Results are separate from solutions
The `results/` directory is generated output — what the platform produces when it analyses solutions. This separation means:
- Solutions are inputs, results are outputs
- Results can be regenerated at any time
- The portal reads from `results/`, not from `solutions/`

### Traces are pre-recorded
The `traces/` directory contains static JSON files representing step-level execution traces. The portal renders these directly. No tracing infrastructure needed.

### Platform core lives in the backend
The guardrails, evaluation, compliance, and observability code lives in `backend/src/platform/`. This is the reusable component library — the thing the chapter builds once and every squad consumes.

### Two CI/CD pipelines
- `ci.yml` — runs on every PR. Tests the platform code itself (pytest, ruff).
- `eval.yml` — runs on demand or on merge. Runs DeepEval against solution golden datasets and compliance gates. This is the "governance on autopilot" pipeline.
