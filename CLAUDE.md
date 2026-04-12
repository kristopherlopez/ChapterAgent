## Git Workflow

After every change (feature, fix, refactor, docs update), **commit and push to `main`** immediately. Do not batch changes or wait to be asked.

---

You are extremely disciplined about keeping documentation in perfect sync with the code. For **every single task, feature, refactor, or plan** you create or suggest:

1. **Discovery Phase** (always do this first)
   - Explore and read all existing documentation:
     - README.md
     - docs/ folder (and any \*.md files)
     - Relevant inline docstrings / comments
     - This CLAUDE.md file itself
   - Identify what is relevant, outdated, or missing for the proposed changes.

2. **Planning Requirement**
   - Every plan you propose MUST contain a dedicated section called "**Documentation Updates**".
   - In that section explicitly list:
     - Which existing documents are impacted
     - What will be updated or newly created
     - Specific changes (e.g. "Add new endpoint X to API reference in docs/api.md", "Update architecture overview in README.md with new diagram description", "Create new migration guide for breaking change Y")

3. **Execution**
   - After code changes are complete, immediately update/create all affected documentation.
   - Documentation changes must be part of the same changeset when possible.
   - Never mark a task as "done" or propose final code until docs are current and consistent.

Stale or missing documentation is not acceptable. Treat docs as production code.

---

## Development

### Prerequisites

- Python 3.12+ with `uv` (package manager)
- Node.js 22+ with `npm`
- API keys configured in `.env` at project root (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`)

### Backend (FastAPI — port 8000)

```bash
# From project root
cd backend
uv run uvicorn src.api.app:app --reload --port 8000
```

The backend serves the REST API at `http://localhost:8000`. Key routes:
- `GET  /api/solutions` — solution list
- `GET  /api/solutions/{id}` — solution detail
- `POST /api/chat/{solution_id}` — interactive agent chat (body: `{ "question": "...", "framework": "openai" | "claude" | "langchain" }`)
- `GET  /api/compliance/dashboard` — compliance summary
- `GET  /api/evidence/{id}/download` — evidence export
- `GET  /api/traces/{id}` — trace steps
- `GET  /api/controls` — controls register (AI-GOV controls, risk mappings)
- `GET  /api/compliance/health/{id}` — real-time compliance health from event log
- `GET  /api/scorecard` — framework scorecard

### Frontend (Next.js 16 — port 3000)

```bash
cd frontend
npm install   # first time only
npm run dev
```

The frontend runs at `http://localhost:3000`. It calls the backend API when available and falls back to hardcoded data when the backend is not running.

### Running both together

Open two terminals:

```bash
# Terminal 1 — backend
cd backend && uv run uvicorn src.api.app:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev
```

### Compliance Gate

```bash
# Run the full 8-check compliance gate for the QA agent
cd backend
uv run python -m src.platform.compliance.runner \
  --solution-dir ../solutions/qa-agent --verbose
```

The runner loads `solution.yaml`, runs all 8 AI-GOV checks (registration, evaluation, PII, guardrails, bias/toxicity, audit trail, golden dataset sign-off, prompt governance), and outputs APPROVED or BLOCKED. Exit code 1 on BLOCKED.

### Tests

```bash
# Backend tests (from project root)
uv run pytest backend/tests

# Frontend lint
cd frontend && npm run lint
```
