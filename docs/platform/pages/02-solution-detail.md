# Solution Detail Page

**Route:** `/solutions/[id]`
**Purpose:** Full transparency into a single solution's compliance status — guardrails, evaluation metrics, gate decision, and execution trace.

---

## What It Shows

Click into any solution from the dashboard or sidebar. This page answers: "Why is this solution green (or red)?"

### Header

- Solution name and description
- Health badge (green/amber/red)
- Risk tier (Customer-Facing, High, Medium, Internal)
- Last run timestamp
- "Export Evidence" button for this specific solution

### Guardrail Results

A table of every guardrail check run against this solution:

| Column | Description |
|--------|-------------|
| **Guardrail** | Name of the check (e.g. Prompt Injection, PII Detection, Faithfulness) |
| **Result** | PASS, FAIL, or WARN |
| **Detail** | Specifics — score, count, or reason |

Guardrail profiles differ by solution type:
- **AI solutions** — Prompt Injection, Scope Containment, PII Detection, Faithfulness, Bias, Toxicity, Citation Coverage, Temporal Accuracy
- **ML solutions** — Discrimination Check, Calibration Check, Stability Check, Explainability Check

### Evaluation Scores

A table of evaluation metrics with scores tested against thresholds:

| Column | Description |
|--------|-------------|
| **Metric** | Evaluation metric name |
| **Score** | Measured value |
| **Threshold** | Required minimum (or maximum for inverse metrics) |
| **Status** | PASS or FAIL based on threshold comparison |

Metrics also differ by solution type:
- **AI solutions** — Faithfulness, Answer Relevancy, Context Precision, Context Recall, Hallucination, Citation Coverage, Boundary Adherence, Temporal Accuracy, Bias, Toxicity
- **ML solutions** — AUC-ROC, Gini, Brier Score, ECE, Demographic Parity Diff, Equalised Odds Diff, Disparate Impact Ratio, PSI, SHAP Coverage

### Compliance Gate

Shows the final deployment gate decision:
- Gate name ("Deployment Gate")
- Result — PASS or FAIL
- Reason — human-readable explanation
- Timestamp of decision

### Execution Trace

Pre-recorded trace showing step-level execution (rendered inline via the `TraceView` component). Each step shows:
- Step number
- Label (what happened)
- Duration in milliseconds
- Detail (metrics, counts, costs)

Links to the full [Trace View](05-trace-view.md) page.

---

## Data Sources

- Solution detail from `solutionDetails` record in `lib/data.ts` (keyed by solution ID)
- Trace data from `solutionTraces` record in `lib/data.ts`

---

## Key Components

| Component | File | Role |
|-----------|------|------|
| `SolutionDetailPage` | `app/solutions/[id]/page.tsx` | Page layout, data lookup, 404 handling |
| `GuardrailResults` | `components/detail/GuardrailResults.tsx` | Guardrail results table |
| `EvaluationScores` | `components/detail/EvaluationScores.tsx` | Eval metrics table with threshold comparison |
| `ComplianceGate` | `components/detail/ComplianceGate.tsx` | Gate decision display |
| `TraceView` | `components/detail/TraceView.tsx` | Inline execution trace |
| `HealthBadge` | `components/dashboard/HealthBadge.tsx` | Status indicator |
| `ExportButton` | `components/evidence/ExportButton.tsx` | Solution-specific evidence export |

---

## Demo Narrative

Alex clicks the red solution. He sees exactly which guardrail failed (PII Detection — 3 instances detected) and which eval metric is below threshold (Faithfulness 0.72 < 0.80). The gate decision confirms: blocked, with a clear reason. The trace shows the execution steps including where the failure occurred.

**Key impression:** "I can see exactly what went wrong, why, and when — without asking anyone."
