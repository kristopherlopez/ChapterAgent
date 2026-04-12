# Portal

The portal is the primary artefact — the thing Alex sees and clicks. Everything else (guardrails, eval, compliance gates, observability) exists to populate what appears here. The first impression should scream "governance on autopilot."

## Screens

### 1. Compliance Health Dashboard (Landing Page)

The hero view. Alex opens this and immediately sees the health of every AI solution in the portfolio.

```
+------------------------------------------------------------------+
|  CHAPTER AI PLATFORM — Compliance Health                         |
+------------------------------------------------------------------+
|                                                                  |
|  Portfolio Overview                              [Export All]    |
|                                                                  |
|  +------------------------------------------------------------+ |
|  | Solution              | Guardrails | Eval   | Gate  | Health| |
|  |------------------------------------------------------------| |
|  | Q&A Agent        | 6/6 PASS   | 0.91   | PASS  |  🟢  | |
|  | Validation Agent      | 4/4 PASS   | 0.88   | PASS  |  🟢  | |
|  | Classification Agent  | 5/6 FAIL   | 0.72   | BLOCK |  🔴  | |
|  +------------------------------------------------------------+ |
|                                                                  |
|  Last compliance run: 2026-04-10 14:32 AEST                     |
|                                                                  |
|  Summary:                                                        |
|  - 2 of 3 solutions deployment-ready                             |
|  - 1 solution blocked — PII guardrail failure                    |
|  - Next scheduled run: 2026-04-11 09:00 AEST                    |
|                                                                  |
+------------------------------------------------------------------+
```

**What Alex sees:** A portfolio of AI solutions with clear pass/fail status across three dimensions — guardrails, evaluation score, and deployment gate. One solution is red. He can see why without clicking in.

**Health rollup logic:**
- 🟢 Green — all guardrails pass, eval score above threshold, deployment gate approved
- 🟡 Amber — eval score below threshold but above minimum, or non-critical guardrail warning
- 🔴 Red — any guardrail failure, eval below minimum, or deployment gate blocked

### 2. Solution Detail Page

Click into any solution from the dashboard. Shows the full picture for that solution.

```
+------------------------------------------------------------------+
|  Q&A Agent                                    [Export Evidence] |
+------------------------------------------------------------------+
|                                                                  |
|  Status: 🟢 DEPLOYMENT-READY                                     |
|  Risk Tier: High                                                 |
|  Last Run: 2026-04-10 14:32 AEST                                |
|                                                                  |
|  GUARDRAIL RESULTS                                               |
|  +------------------------------------------------------------+ |
|  | Guardrail            | Result | Detail                      | |
|  |------------------------------------------------------------| |
|  | Scope Containment    | PASS   | 0 out-of-scope responses    | |
|  | PII Detection        | PASS   | 0 PII instances found       | |
|  | Faithfulness Check   | PASS   | Score: 0.94                 | |
|  | Bias Scan            | PASS   | Score: 0.02                 | |
|  | Toxicity Scan        | PASS   | Score: 0.00                 | |
|  | Citation Presence    | PASS   | 100% responses cited        | |
|  +------------------------------------------------------------+ |
|                                                                  |
|  EVALUATION SCORES                                               |
|  +------------------------------------------------------------+ |
|  | Metric               | Score  | Threshold | Status          | |
|  |------------------------------------------------------------| |
|  | Context Precision    | 0.85   | 0.75      | PASS            | |
|  | Context Recall       | 0.79   | 0.70      | PASS            | |
|  | Faithfulness         | 0.93   | 0.85      | PASS            | |
|  | Answer Relevancy     | 0.91   | 0.80      | PASS            | |
|  | Overall              | 0.91   | 0.80      | PASS            | |
|  +------------------------------------------------------------+ |
|                                                                  |
|  COMPLIANCE GATE                                                 |
|  +------------------------------------------------------------+ |
|  | Gate                 | Result | Reason                      | |
|  |------------------------------------------------------------| |
|  | Deployment Gate      | PASS   | All checks passed           | |
|  | Approved at          |        | 2026-04-10 14:32 AEST       | |
|  +------------------------------------------------------------+ |
|                                                                  |
+------------------------------------------------------------------+
```

**What Alex sees:** Full transparency into why a solution is green (or red). Every guardrail result, every eval metric against its threshold, and the gate decision with reasoning. One click from the dashboard.

### 3. Evidence Export

A button on both the dashboard ("Export All") and solution detail page ("Export Evidence"). Produces a structured report — a populated template, not a dynamically generated document.

**Contents:**
- Solution name, risk tier, and description
- Guardrail results with pass/fail and detail
- Evaluation scores against thresholds
- Compliance gate decision and timestamp
- Summary of any failures or warnings

**Format:** JSON and/or PDF. The point is that an auditor gets a structured, reviewable artefact without a meeting.

### 4. Solution Registry

Dedicated page at `/registry` showing all registered solutions discovered from their `solution.yaml` manifests. Each row displays:

- **Solution** — name and description
- **Category** — AI or ML
- **Risk Tier** — Customer-Facing, High, Medium, Internal
- **Owner** — responsible squad
- **Gate** — deployment gate pass/fail badge
- **Health sparkline** — 14-day health trend rendered as a colour-coded sparkline (green = pass, amber = warn, red = fail), giving at-a-glance visibility into solution stability over time
- **Last Tested** — relative timestamp with a stale indicator (amber warning badge) when a solution has not been tested in 7+ days

Each row links to the solution detail page. Includes an explanation of the self-registration model via manifests and a legend for the sparkline and stale indicators.

### 5. Governance Documents

Dedicated page at `/documents` showing the governance policy documents, standards, and frameworks that the platform's automated controls reference. This is the policy layer made visible — connecting AI-GOV controls back to the documents they enforce.

Each row displays:

- **Document** — title and description
- **Type** — badge indicating policy, standard, framework, or guideline
- **Owner** — the team or body responsible (e.g. "Group Risk", "APRA", "DISR")
- **Status** — active, draft, or under-review
- **Linked Controls** — AI-GOV control badges showing which automated checks this document requires. Hover for the full policy description.
- **Review Date** — next scheduled review

The page includes 10 documents covering:
- CBA internal policies (Group AI Policy, Responsible AI Principles, Data Governance Standard)
- CBA frameworks (Model Risk Management, AI Testing & Evaluation)
- CBA standards (AI Solution Registration, Prompt Governance)
- External standards (APRA CPS 230, APRA CPS 234)
- Government guidelines (Australia's Voluntary AI Safety Standard)

An explainer card describes how documents connect to automated controls: each document defines requirements, each requirement maps to an AI-GOV control, and each control is enforced by the compliance-as-code pipeline. A legend card shows the colour coding for document types and statuses.

**What Alex sees:** "Every automated check traces back to a policy document. This isn't governance invented from scratch — it's CBA's existing policies, APRA standards, and the Australian AI Safety Standard, operationalised into automated controls."

### 6. Controls Register

Dedicated page at `/controls` showing every automated control in the platform — the auditor's cross-reference view. While the Documents page is document-centric ("this policy requires these controls"), the Controls Register is control-centric ("this control mitigates these risks and satisfies these regulations").

Four tabbed views:

- **Controls** — all 10 AI-GOV controls with enforcement layer (Gate / Runtime / Gate + Runtime), control type (Preventive / Detective), and risks mitigated. Each row is expandable to show runtime guardrails (with latency targets) and incident response actions for that control.
- **Risk Mapping** — all 12 risks from the AI Risk Register, each linked to mitigating controls with residual risk level. One view that answers "every risk has a control."
- **Regulatory** — CPS 230, CPS 234, and DISR AI Safety Standard requirements, each mapped to the platform controls and evidence that satisfy them. Gaps are flagged explicitly (e.g. DISR Guardrail 7: Challenge processes).
- **Thresholds** — per-metric threshold table showing how controls scale across Experimental, Production Internal, and Production Customer-Facing risk tiers.

Summary cards show: 10 automated controls, 8 runtime guardrails, < 200ms total runtime latency budget.

**What Alex sees:** "Here's every automated control in the platform. Pick any one — I can show you where it runs, what risk it covers, which regulation it maps to, and where the evidence lives. This is the page a 2nd-line reviewer or APRA auditor would use."

### 7. Observability / Trace View

Pre-recorded trace data showing step-level execution for a given solution run.

```
+------------------------------------------------------------------+
|  Q&A Agent — Trace: run_2026-04-10_001                     |
+------------------------------------------------------------------+
|                                                                  |
|  Step 1: Query received                          0ms             |
|  Step 2: Context retrieval (hybrid search)       120ms           |
|    → 3 chunks retrieved, top score: 0.92                         |
|  Step 3: LLM generation                          1,340ms         |
|    → Tokens: 1,847 | Cost: $0.0034                              |
|  Step 4: Guardrail checks                        187ms           |
|    → 6/6 passed                                                  |
|  Step 5: Response returned                        1,647ms total  |
|                                                                  |
+------------------------------------------------------------------+
```

**What Alex sees:** Even though this is pre-recorded, it shows the level of observability the platform provides. Every step, every cost, every check — traced and auditable.

### 8. Solution Type Comparison

Comparison table across all three demo solutions — showing how the same platform evaluates different solution types.

```
+------------------------------------------------------------------+
|  Solution Type Comparison                                        |
+------------------------------------------------------------------+
|                                                                  |
|  Metric              | Q&A Agent  | Validation | Classification |
|  ------------------------------------------------------------- |
|  Guardrails Pass     | 6/6        | 5/5        | 3/4            |
|  Faithfulness        | 0.93       | 0.88       | N/A            |
|  Accuracy            | N/A        | N/A        | 0.84           |
|  Bias                | 0.02       | 0.03       | 0.08           |
|  Consistency         | N/A        | N/A        | 0.91           |
|  Compliance Gate     | PASS       | PASS       | BLOCK          |
|  Solution Type       | Q&A        | Validation | Classification |
|  ------------------------------------------------------------- |
|                                                                  |
|  Note: Classification Agent blocked — bias score above           |
|  threshold for production_customer_facing tier.                  |
|                                                                  |
+------------------------------------------------------------------+
```

**What Alex sees:** Three different solution types, same governance platform. The metrics that matter shift by type — faithfulness for Q&A, accuracy and bias for classification. The platform adapts its evaluation to the solution, not the other way around.

### 10. Component Catalog

Dedicated page at `/catalog` listing every reusable platform component the Chapter ships to squads. This is the "menu" of Chapter-provided tooling.

Components are organised by type with filter pills:
- **Guardrail** (8) — scope adherence, PII, faithfulness, bias, toxicity, citation coverage, temporal accuracy, prompt injection
- **Evaluation** (1) — the evaluation harness with risk-tier thresholds
- **Compliance** (8) — the 8 AI-GOV compliance gate checks
- **Observability** (1) — trace logger
- **Tooling** (2) — golden dataset generator (beta) and validation UI (beta)

Each component row expands to show:
- **Interface contract** — what the squad provides vs what the component returns
- **Adoption** — which solutions currently consume this component (with links)
- **Open Tool** button for tooling components (links to generator or validation UI)

Summary cards show total components, active count, and solutions consuming. An explainer card describes the "Chapter builds, squads consume" model.

**What Alex sees:** "Here's every reusable component the Chapter ships. Squads don't build guardrails from scratch — they consume these. Adoption is tracked. Each component has a clear interface contract."

### 11. Golden Dataset Generator

Dedicated page at `/catalog/generator` providing the Chapter's tool for bootstrapping golden datasets. Squads bring their documents; the generator produces draft test triples.

Configuration form:
- **Solution selector** — pick from registered solutions
- **Number of cases** — how many test triples to generate
- **Query types** — checkboxes for 10 types (direct factual, comparative, temporal, aggregation, causal, boundary, multi-hop, out of scope, ambiguous, adversarial)

Results table shows generated cases with expandable detail (question, expected answer, citations, behaviour, grounding, scope level, key metrics). A "Send to Validation" button forwards generated cases to the validation UI.

**What Alex sees:** "The Chapter provides this tool so squads don't start from scratch. They bring their documents, the generator bootstraps draft test cases, and their SMEs review them in the validation UI."

### 12. Golden Dataset Validation UI

Dedicated page at `/catalog/validation` providing the SME review interface for golden dataset test cases.

Progress section:
- **Progress bar** — visual indicator of review completion
- **Stats** — total, approved, rejected, pending counts
- **Sign-off button** — disabled until all cases reviewed

Test cases table with expandable review panels showing:
- Full question and expected answer
- Citations, behaviour, grounding, scope level, key metrics
- Review notes from previous reviewers
- **Approve / Reject / Edit** action buttons

Sign-off produces the compliance artifact required by AI-GOV-009 (Golden Dataset Sign-off gate).

**What Alex sees:** "This closes the loop. The generator creates volume, domain experts validate quality, and sign-off feeds directly into the compliance gate. Squads get a reviewed, auditable golden dataset."

---

## Demo Flow

When Alex opens the portal:

1. **Landing page** — sees the compliance health dashboard. Three solutions green, one red. Immediate clarity.
2. **Sidebar** — solutions split into AI Solutions and ML Solutions with health dots. Platform governs both GenAI and traditional ML.
3. **Clicks the red solution** — sees exactly which guardrail failed and why. Execution trace visible on the same page. No ambiguity.
4. **Clicks the ML solution** — sees completely different guardrail profile (fairness, calibration, stability). Same platform, different governance.
5. **Clicks "Export Evidence"** — gets a structured report. No meeting, no form.
6. **Navigates to the scorecard** — sees the framework comparison. Strategic value beyond governance.
7. **Opens Solution Registry** — sees manifest-driven self-registration model. Squads onboard themselves.
8. **Opens Controls Register** — sees every automated control mapped to risks and regulations. The auditor's view. "Pick any control — I can show you where it runs and what regulation it satisfies."
9. **Opens Documents** — sees governance documents mapped to automated controls. Every AI-GOV check traces to a policy.
10. **Opens Component Catalog** — sees every reusable component the Chapter ships. Clicks into a guardrail to see the interface contract. Sees adoption across solutions. "This is the menu of what the Chapter provides."
11. **Opens Generator** — sees the tool that bootstraps golden datasets. Selects a solution, generates test cases, sends to validation. "Squads don't start from scratch."
12. **Opens Validation UI** — sees SME review interface. Approves/rejects cases, sees progress bar fill. Signs off. "This sign-off feeds directly into the compliance gate."

The story in 60 seconds: "This is what governance on autopilot looks like. Every solution, every check, every decision — tracked, scored, and exportable. The Chapter builds reusable components; squads consume them and bring their domain expertise."

---

## Design Principles

- **Governance-led, not solution-led** — the dashboard is about compliance health, not showcasing AI capabilities
- **One click to detail** — from dashboard to solution to evidence, never more than one click deep
- **No ambiguity** — pass/fail, green/amber/red, scores against thresholds. Everything has a clear status
- **Human-reviewable** — a non-engineer should understand what they're looking at
- **Pre-recorded but believable** — the data tells a coherent story with realistic scores and realistic failures
