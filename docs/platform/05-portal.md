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

### 4. Solution Registry (Nav-Level)

Not a dedicated page — this is the navigation. The sidebar or top-level nav lists all registered solutions, discovered from their `solution.yaml` manifests. Each links to its solution detail page.

### 5. Observability / Trace View

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

### 6. Solution Type Comparison

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

---

## Demo Flow

When Alex opens the portal:

1. **Landing page** — sees the compliance health dashboard. Two solutions green, one red. Immediate clarity.
2. **Clicks the red solution** — sees exactly which guardrail failed and why. No ambiguity.
3. **Clicks a green solution** — sees everything passing, eval scores above thresholds, gate approved.
4. **Clicks "Export Evidence"** — gets a structured report. No meeting, no form.
5. **Navigates to the scorecard** — sees the framework comparison. Strategic value beyond governance.
6. **Optionally views a trace** — sees step-level observability for a pre-recorded run.

The story in 60 seconds: "This is what governance on autopilot looks like. Every solution, every check, every decision — tracked, scored, and exportable."

---

## Design Principles

- **Governance-led, not solution-led** — the dashboard is about compliance health, not showcasing AI capabilities
- **One click to detail** — from dashboard to solution to evidence, never more than one click deep
- **No ambiguity** — pass/fail, green/amber/red, scores against thresholds. Everything has a clear status
- **Human-reviewable** — a non-engineer should understand what they're looking at
- **Pre-recorded but believable** — the data tells a coherent story with realistic scores and realistic failures
