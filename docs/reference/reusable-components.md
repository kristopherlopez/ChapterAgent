# Reusable Components — CBA Chapter Area Lead

## 1. What Makes a Component Genuinely Reusable

Shared code is "here's a repo, good luck." A reusable component is something squads actually adopt and rely on. The distinction:

| Shared Code | Reusable Component |
|---|---|
| Dumped in a repo | Versioned and released |
| Tribal knowledge to use | Documented with clear interface |
| Author moves on, it rots | Has an owner who maintains it |
| No idea if anyone uses it | Adoption tracked via telemetry |
| Squads need to understand internals | Squads consume it as a black box |
| Breaks silently when dependencies change | Breaking changes managed through semver |

### Four Criteria for Reusability

1. **Clear interface** — squads don't need to understand the internals to use it
2. **Distribution** — easy to consume (installable package, template repo, sparse clone)
3. **Ownership** — someone maintains it, answers questions, fixes bugs
4. **Adoption tracking** — telemetry proves it's actually used and surfaces where it's failing

If a component doesn't meet all four, it's shared code pretending to be reusable. The chapter's job is to build and maintain components that meet this bar.

---

## 2. Evaluation Framework (Four Layers)

The strategic framework that defines how AI solutions are assessed. Each layer answers a different question at a different stage of the lifecycle.

### Layer 1: Retrieval Quality — "Did we find the right context?"
- Precision, recall, ranking quality (NDCG/MRR)
- Measured against the golden dataset
- Answers: is the retriever doing its job?

### Layer 2: Generation Quality — "Is the answer faithful to what was found?"
- Faithfulness — no hallucinated claims
- Groundedness — every statement traces to a chunk
- Answer relevance — actually addresses the question
- Measured via LLM-as-a-judge (e.g., DeepEval)

### Layer 3: Production Quality — "Will it hold up in the real world?"
- Latency under load
- Cost per query at expected volume
- Consistency — same question, different phrasing, same answer?
- Fallback behaviour — what happens when retrieval returns nothing?

### Layer 4: Governance Quality — "Can we defend this to a regulator?"
- Citation traceability — output links back to source documents
- Boundary adherence — system stays in scope, refuses out-of-scope queries
- Bias and toxicity checks
- Audit trail — full chain from query → retrieval → generation → output logged

### When Each Layer Runs

| Layer | When | How |
|---|---|---|
| 1 & 2 | CI/CD pipeline before promotion | Automated gate via evaluation harness |
| 3 | Staging environment | Load testing under realistic conditions |
| 4 | Continuous in production | Observability layer (e.g., LangFuse) |

A squad can't promote without passing Layers 1-3. Layer 4 runs forever and feeds back into the golden dataset — real queries that fail in production become new test cases.

### Chapter Lead's Role Across All Four Layers
- Define the metrics and thresholds per layer
- Build the reusable tooling (harness, generator, validation UI)
- Review scorecards before production sign-off
- Evolve the framework as new patterns emerge (agentic, multi-step, etc.)

---

## 3. Guardrail Framework

Standardised guardrails that apply across all AI solutions, with additional controls specific to agentic architectures. The chapter defines the guardrail patterns and reusable components — squads implement them in their solutions.

### Foundation Guardrails (All AI Solutions)

**Data Protection**
- Data sovereignty enforcement — resources provisioned in approved regions, aligned to commitments made to customers
- PII masking — automated detection and masking before data is shared with LLMs, especially those processing in international data centres
- Data classification gates — what data can be sent to which models/services

**Bias & Fairness**
- Task-level monitoring for bias in requests and outputs — gender, ethnicity, age
- Aligned to principles in the Responsible Use of AI policy
- Automated checks integrated into evaluation pipelines

**Content Safety**
- Input/output filtering — toxicity, harmful content, prompt injection detection
- Boundary adherence — system refuses out-of-scope queries
- Jailbreak resistance testing as part of pre-production evaluation

### Agentic-Specific Guardrails

Agents introduce unique risks — they take actions, make multi-step decisions, and call tools autonomously. These require additional controls beyond standard LLM guardrails.

**Action Boundaries**
- Explicit whitelist of permitted tools and actions per agent
- What the agent can read vs write vs execute — defined and enforced
- Scope containment — agent cannot access data or systems beyond its intended domain

**Human-in-the-Loop Gates**
- Defined thresholds where the agent must stop and request human approval before proceeding
- Risk-tiered: low-risk actions proceed autonomously, high-risk actions require sign-off
- Configurable per use case — the chapter provides the gate framework, squads define their thresholds

**Step-Level Observability**
- Full trace of every decision the agent made, every tool it called, and why
- Integrated with observability layer (e.g., LangFuse) for audit trail
- Each step logged with: input, reasoning, action taken, output, time elapsed

**Circuit Breakers**
- Automatic termination if the agent enters a loop, exceeds step limits, or takes an unexpected path
- Cost ceiling — kill the agent if token/API spend exceeds a threshold
- Anomaly detection — flag if agent behaviour diverges significantly from expected patterns

**Escalation Paths**
- Defined fallback when an agent fails or is terminated — graceful degradation to human review or previous non-agentic process
- Incident playbooks for common agent failure modes

### Guardrail Ownership

| Chapter builds (reusable) | Squad owns (specific) |
|---|---|
| PII masking library | Which data fields to mask for their domain |
| Bias detection pipeline | Fairness thresholds for their use case |
| Action boundary enforcement framework | Their agent's permitted tool whitelist |
| Human-in-the-loop gate framework | Their risk thresholds for when gates trigger |
| Circuit breaker library | Their step limits and cost ceilings |
| Step-level tracing integration | Instrumenting their agent with the tracer |

---

## 4. RAG Evaluation Harness

The primary reusable component — a standardised test runner that any squad can plug their RAG pipeline into to measure retrieval and generation quality against chapter-defined thresholds.

### Components

**4.1 Golden Dataset**
Curated set of question-answer-context triples (ground truth). Each entry has:
- A question
- The expected relevant chunks with **graded relevance scores** (not just relevant/irrelevant):
  - **Grade 3** — directly answers the question (must appear in top results)
  - **Grade 2** — supporting context (useful but not essential)
  - **Grade 1** — tangentially related (acceptable but shouldn't outrank Grade 3)
  - **Grade 0** — irrelevant
- The expected answer (or acceptable answer range)

Graded relevance enables ranking metrics (NDCG, MRR) — without it, you can only measure whether the right chunks were retrieved, not whether they were retrieved *in the right order*.

**4.2 Golden Dataset Generator**
Uses LLMs to synthesise question-answer-context triples from a squad's document corpus. Bootstraps evaluation quickly rather than waiting for manual curation. Process:
- Ingest the squad's source documents
- Generate candidate questions per chunk
- Generate expected answers grounded in the chunk
- Output draft triples for human review

**4.3 Golden Dataset Validation UI**
Lightweight web app for SMEs (not data scientists) to review and approve synthetic triples. Features:
- Shows the question, expected answer, and source chunks side by side
- SME marks each triple as: approved, edited, or rejected
- SME assigns or adjusts graded relevance scores (Grade 0-3) per chunk — drag-and-drop ranking or grade selection
- Tracks inter-rater agreement if multiple SMEs review
- Exports validated dataset in the format the evaluation harness expects

This closes the loop: the generator creates volume, the UI brings in domain expertise, and the harness runs the evaluation. The chapter builds all three — squads bring their documents and their SMEs.

**4.4 Retrieval Evaluator**
Runs each question through the squad's retriever and scores:
- **Precision** — of the chunks retrieved, what proportion were in the expected set?
- **Recall** — of the expected chunks, how many were actually retrieved?
- **Ranking quality (MRR / NDCG)** — were the best chunks ranked highest?

**4.5 Generation Evaluator**
Scores the generated output against the retrieved context:
- **Faithfulness** — is every claim supported by the retrieved context? (no hallucinated facts — the answer doesn't contradict what was retrieved)
- **Groundedness** — can each statement trace back to a *specific* chunk? (attribution, not just consistency — the audit trail for *why* the system said what it said). An answer can be faithful but not grounded: nothing wrong, but you can't point to where it came from. In regulated environments, groundedness is what lets you show evidence.
- **Answer relevance** — does the answer address the question asked?

**4.6 Production Readiness Checks**
- **Latency** — end-to-end response time under realistic load
- **Cost per query** — token usage, embedding calls, retrieval API costs
- **Fallback behaviour** — what happens when retrieval returns nothing relevant?
- **Consistency** — same question asked multiple ways, same answer?

**4.7 Governance Checks**
- **Citation traceability** — can the answer point back to source documents for audit?
- **Boundary adherence** — does the system stay within permitted scope?
- **Toxicity / bias checks** — relevant for customer-facing or decision-support systems

**4.8 Configurable Thresholds**
Chapter sets minimum bars per risk tier:
- Production customer-facing: retrieval precision > 0.8, faithfulness > 0.9
- Production internal: retrieval precision > 0.7, faithfulness > 0.8
- Experimental / sandbox: no gate, but scores logged

**4.9 Report Output**
Standardised scorecard written to the model registry. Same format across every squad and every RAG implementation.

### Harness Ownership

| Chapter builds (reusable) | Squad owns (specific) |
|---|---|
| Evaluation harness / test runner | Their golden dataset (domain-specific) |
| Golden dataset generator | Their source document corpus |
| Validation UI for SME review | Their SMEs to review and approve |
| Scoring functions | Their retrieval pipeline config |
| Threshold standards by risk tier | Their chunking strategy |
| Report template | Their embedding model choice |
| CI/CD integration (pass/fail gate) | Running the eval before promotion |

### How It Works in Practice

The harness is a Python package or internal library. A squad imports it, points it at their retriever and their golden dataset, runs it, gets a scorecard. If it passes the chapter's thresholds, they can promote to production. If not, they know exactly where it's failing.

---

## 5. Framework Evaluation Template

Standardised criteria for squads evaluating agentic orchestration frameworks (or any significant technology adoption). The chapter defines the template — squads fill it out, the chapter reviews, and the decision is documented and auditable.

### Evaluation Criteria

**Technical Fit**
- Does it support the patterns we need? (tool calling, multi-agent, human-in-the-loop, stateful workflows)
- Language/runtime compatibility — Python, .NET, both?
- How does it handle memory and state management across conversation turns?

**Ecosystem Integration**
- How well does it integrate with our existing stack? (Azure, CI/CD, observability tooling)
- Native connectors vs community-maintained vs build-your-own
- LLM provider flexibility — locked to one provider or model-agnostic?

**Maturity & Support**
- How active is the maintainer? Release cadence, issue resolution time
- Community size — can we hire people who know this?
- Documentation quality — can a mid-level data scientist pick it up without hand-holding?

**Governance & Observability**
- Can we instrument it for tracing? (integrates with LangFuse, OpenTelemetry, etc.)
- Can we enforce guardrails at the framework level? (input/output validation, content filtering)
- Logging granularity — can we trace a decision back through every agent step for audit?

**Vendor & Lock-in Risk**
- Open source vs proprietary — what happens if the maintainer pivots or sunsets?
- How coupled is the framework to a specific LLM provider?
- Portability — how hard is it to migrate away if we need to?

**Roadmap Alignment**
- Where is the framework heading in 3-6 months?
- Does the roadmap align with where our patterns are heading? (e.g., multi-agent, computer use)
- Is the maintainer investing in regulated/enterprise use cases or consumer?

**Cost**
- Licensing model — free, per-seat, per-call?
- Overhead — does the framework add latency or token cost?
- Build cost — how much custom code do we need to write around it?

### How It Works

A squad considering a new framework fills out the template, scoring each criterion. The chapter reviews the evaluation, challenges assumptions, and signs off. Even if three squads pick different frameworks, they all made the decision the same way and the rationale is documented.

---

## 6. CI/CD Consistency Strategy

The chapter can't control every squad's CI/CD pipeline — and shouldn't try. The lever is standardising what runs *inside* the pipeline, not the pipeline itself.

### The Principle

You don't need to own the pipeline to enforce consistency through it. Shared components plug into any CI/CD setup regardless of whether the squad uses GitHub Actions, Azure DevOps, or Jenkins.

### Pipeline-Agnostic Components the Chapter Ships

| Component | What it does | How squads consume it |
|---|---|---|
| **Evaluation gate** | Runs the RAG evaluation harness, fails the build if thresholds aren't met | CLI command or Docker container — callable from any pipeline |
| **Model registry push** | Standardised registration of models with metadata, version, lineage | API call or SDK — same format regardless of pipeline |
| **Notebook linting config** | Shared code quality and style standards for data science notebooks | Config file imported into squad's linting step |
| **Guardrail validation step** | Tests guardrails (PII masking, boundary adherence, bias checks) pre-deployment | CLI command — runs in any pipeline as a step |
| **Scorecard generator** | Produces the standardised evaluation report after all checks pass | Triggered by evaluation gate — outputs to model registry |

### How It Works

1. Chapter publishes components as versioned packages (pip install, Docker images, or CLI tools)
2. Squads add them as steps in their own pipelines — one line of config each
3. Components report results to a central dashboard — chapter has visibility across all squads
4. If a squad skips a required step, it shows up as a gap in the dashboard — visibility, not enforcement

### Why This Works

- Squads keep autonomy over their pipeline tooling
- Chapter gets consistency through shared components, not mandated infrastructure
- Adoption is tracked via telemetry — you can see who's using what and where gaps are
- New squads get a starter template but aren't locked into it

---

## 7. Compliance-as-Code

Encoding governance rules into automated checks that run in the pipeline, rather than relying on manual review, checklists, or quarterly audits. Compliance evidence is generated as a byproduct of how the team works, not a separate reporting exercise.

### The Principle

Every governance policy should have a corresponding automated check. If a rule can be expressed as "did X happen before Y?" — it can be a pipeline gate.

### Example: RAG Solution Promotion

A squad wants to promote a RAG solution to production. Instead of a governance review meeting, the pipeline automatically checks:

| Check | Policy it encodes | Pass/Fail |
|---|---|---|
| Is the model registered in the model registry? | Inventory compliance | Block if unregistered |
| Has it passed the evaluation harness for its risk tier? | Quality compliance | Block if below threshold |
| Has PII masking been validated? | Privacy compliance | Block if untested |
| Is the audit trail complete — every step traced? | Observability compliance | Block if gaps |
| Has a human signed off on the golden dataset? | Human oversight compliance | Block if unsigned |

All pass → auto-promoted. Any fail → blocked with a specific reason and remediation guidance.

### What the Chapter Builds

- **Policy-to-code mapping** — each governance policy translated into one or more automated checks
- **Gate library** — reusable check functions squads add to their pipelines
- **Compliance dashboard** — real-time view of which solutions meet which policies, across all squads
- **Evidence generator** — automated compliance reporting for 2nd line validation and 3rd line audit, produced as a byproduct of the pipeline running

### Why It Matters at CBA

- Manual governance doesn't scale across dozens of squads and hundreds of models
- Regulators (APRA) want evidence of controls, not just policies — automated checks produce that evidence continuously
- Reduces governance overhead for squads — they don't fill out forms, they pass gates
- 2nd and 3rd line get their evidence without requesting it — it's already in the system

---

## Interview Framing

> "The chapter builds the evaluation harness and sets the standards. The squads consume it and own their domain-specific test data. That's the reusable component model — we build it once, every squad benefits, and quality is consistent across the organisation."
>
> "At PetSure I'm building Layers 1 and 2 right now with DeepEval and LangFuse. At CBA scale, I'd extend this to a full four-layer framework with automated gates across the CI/CD pipeline, staging, and production."
