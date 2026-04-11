# Build Phases

**Timeline:** ~1 week
**Approach:** Portal-first, cut from the bottom if time runs out

---

## Phase 1: Foundation + Portal Shell (Day 1)

**Goal:** Repo structure, tooling, and a portal that renders static data.

- Initialise monorepo (frontend/, backend/, solutions/, results/, traces/)
- Set up Next.js 16 with TypeScript, Tailwind CSS 4, ESLint
- Set up FastAPI with Pydantic 2, Ruff
- Docker Compose for local dev
- GitHub Actions CI pipeline (Ruff + pytest on PR)
- Build portal shell:
  - Compliance health dashboard (landing page) — hardcoded data
  - Solution detail page — hardcoded data
  - Sidebar nav with solution registry
  - Evidence export button (placeholder)
- Create solution manifests (`solution.yaml`) for all three demo solutions
- Backend: solution discovery (reads manifests), serves portal data from JSON files

**Exit criteria:** Portal renders a dashboard with three solutions, you can click into detail pages. Data is hardcoded but the structure is real.

---

## Phase 2: Q&A Agent + Custom Guardrails (Days 2-3)

**Goal:** First real solution passing through real guardrails. The "governance on autopilot" moment.

- Build Q&A Agent solution:
  - Knowledge base documents (markdown corpus)
  - Chunk, embed with OpenAI text-embedding-3-small, store in ChromaDB
  - Query → retrieve → generate pipeline using OpenAI SDK
- Build custom guardrail framework (Keras-style API):
  - Base guardrail interface (`base.py`)
  - PII detection (`pii.py`)
  - Scope containment (`scope.py`)
  - Faithfulness check (`faithfulness.py`)
  - Bias detection (`bias.py`)
  - Toxicity detection (`toxicity.py`)
  - Guardrail runner — runs all guardrails for a solution (`runner.py`)
- Create pre-recorded scenarios for Q&A Agent:
  - Pass scenario: clean query, good response, all guardrails green
  - Fail scenario: PII in response, guardrails catch it
- Run guardrails against scenarios, write results to `results/`
- Portal reads real results — dashboard shows green/red for Q&A Agent
- Unit tests for all guardrails

**Exit criteria:** Q&A Agent has real guardrail results. Portal shows pass/fail from real data. Guardrail code is clean, tested, and human-reviewable.

---

## Phase 3: Compliance Gates + Evaluation Harness (Days 3-4)

**Goal:** Deployment gates that actually fire, eval scores with thresholds.

- Build compliance-as-code gates:
  - Deployment gate logic — reads guardrail + eval results, makes pass/block decision
  - Gate config in YAML (thresholds per risk tier)
  - Evidence report generator (populated JSON template)
- Build evaluation harness:
  - Golden dataset for Q&A Agent (20-30 question-answer pairs)
  - DeepEval integration — faithfulness, answer relevancy, contextual precision/recall
  - Metric thresholds in YAML config
  - pytest plugin integration for CI
- Wire up Temporal workflow: orchestrates eval → guardrails → gate for a solution
- GitHub Actions eval pipeline (`eval.yml`) — runs DeepEval + compliance gates
- Portal updates:
  - Solution detail shows real eval scores against thresholds
  - Compliance gate shows real pass/block with reasoning
  - Evidence export produces real structured report
- Create pass/fail scenarios for compliance gates (one solution passes, one blocked)

**Exit criteria:** Compliance gates fire based on real guardrail + eval results. Evidence export works. Two CI pipelines running (platform tests + solution eval). Portal shows the full governance story for Q&A Agent.

---

## Phase 4: Validation Agent (Day 5)

**Goal:** Second solution through the platform — endpoint-based, proving the platform works on solutions it doesn't own.

- Build Validation Agent as a standalone FastAPI endpoint:
  - Synthetic model documentation to validate against (pass + fail model cards)
  - LLM agent: reads docs, runs validation checks, drafts structured findings
  - Tool definitions (document reader, completeness checker, risk assessor, findings drafter)
  - Instrumented with chapter tracing SDK
- Create solution manifest (`type: endpoint`), scenarios (pass/fail), golden dataset
- Run through same platform (guardrails, eval, compliance gates) via endpoint
- Write results, portal renders second solution on dashboard
- Verify: same guardrail runner, same eval harness, same gate logic — different solution type and integration pattern

**Exit criteria:** Two solutions on the dashboard — one embedded, one endpoint-based. Reusable components proven across solution types and integration patterns.

---

## Phase 5: Classification Agent (Day 6)

**Goal:** Third solution type through the platform — different metrics emphasis, bias detection with real teeth.

- Build Classification Agent as a standalone FastAPI endpoint:
  - Basel II operational risk event classification
  - Structured output: category, confidence, reasoning, recommended action
  - Bias probe test cases (same event, different demographics — must produce identical output)
  - Instrumented with chapter tracing SDK
- Create solution manifest (`type: endpoint`), scenarios (pass/fail/bias), golden dataset
- Run through same platform with classification-specific metrics (accuracy, bias, consistency)
- Build solution type comparison view in portal:
  - Metrics shift by type — faithfulness for Q&A, accuracy and bias for classification
- Third solution on the dashboard

**Exit criteria:** Three solution types on the dashboard. Bias detection demonstrated with demographic variant probes. Platform adapts evaluation to solution type.

---

## Phase 6: Polish + Observability (Day 7)

**Goal:** Pre-recorded traces, demo polish, interview prep.

- Create pre-recorded trace files for each solution (step-level JSON)
- Build trace view page in portal
- Portal polish:
  - Consistent styling, loading states, responsive layout
  - Demo flow works smoothly (dashboard → detail → evidence → scorecard → traces)
- Docker Compose — everything starts with one command
- README — setup instructions, architecture overview
- Dry-run the demo walkthrough
- Record backup demo video (in case of live demo issues)

**Exit criteria:** Portal tells the full governance story. Repo is clean and reviewable. Demo is rehearsed.

---

## Cut Line

If time runs out, cut from the bottom. Each phase delivers a demoable state:

| After Phase | What You Can Demo |
|---|---|
| 1 | Portal with structure — shows the vision |
| 2 | Q&A Agent + guardrails catching bad answers — shows governance works |
| 3 | Compliance gates + eval + evidence export — shows the full platform |
| 4 | Two solution types (embedded + endpoint) — shows reusable components |
| 5 | Three solution types + bias detection — shows platform versatility |
| 6 | Full polish — shows production thinking |

**Minimum viable demo:** Phases 1-3 (portal + Q&A Agent + guardrails + compliance gates + eval). This covers Alex's pain point and the core platform story.
