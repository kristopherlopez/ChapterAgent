# Chapter Agent — Backend

FastAPI backend serving the AI governance platform. Provides API endpoints for the portal and houses the reusable platform core: guardrails, evaluation harness, compliance gates, and observability.

## Setup

```bash
cd backend
pip install -e ".[dev]"
```

## Run

```bash
uvicorn src.api.app:app --reload --port 8000
```

The frontend expects the backend at `http://localhost:8000`.

## Test

```bash
pytest tests/ -v
ruff check src/
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/solutions` | List all solutions with summary data |
| GET | `/api/solutions/{id}` | Solution detail (guardrails + eval + compliance) |
| GET | `/api/compliance/dashboard` | Aggregate compliance health |
| GET | `/api/evidence/{id}` | Full evidence package |
| GET | `/api/evidence/{id}/download` | Download evidence as JSON |
| GET | `/api/traces/{id}` | Default execution trace |
| GET | `/api/traces/{id}/scenarios` | List all trace scenarios |
| GET | `/api/traces/{id}/{run_id}` | Specific trace run |
| GET | `/api/scorecard` | Framework comparison scorecard |

## Platform Core

### Guardrails (`src/platform/guardrails/`)

8 guardrails with a Keras-style API:

- **PIIGuardrail** — regex-based Australian PII detection (TFN, ABN, Medicare, phone, email)
- **ScopeGuardrail** — topic graph + scope level enforcement (strict/contextual/open)
- **FaithfulnessGuardrail** — checks output is grounded in retrieved context
- **BiasGuardrail** — demographic bias pattern detection
- **ToxicityGuardrail** — harmful content detection
- **CitationCoverageGuardrail** — verifies factual claims have citations
- **TemporalAccuracyGuardrail** — checks period attribution
- **PromptInjectionGuardrail** — blocks injection attempts before retrieval

All share the same interface: `await guardrail.check(input=..., output=..., context=...)`.

### Evaluation Harness (`src/platform/evaluation/`)

DeepEval wrapper with risk-tier thresholds. Supports pre-recorded scoring for demos.

### Compliance Gates (`src/platform/compliance/`)

Deployment gate (pass/fail) + evidence report generator with policy-to-evidence mapping.
