# Framework Scorecard

**Route:** `/scorecard`
**Purpose:** Compare the same agent implemented across multiple frameworks — same task, same governance, different implementations.

---

## What It Shows

A comparison table showing how the platform evaluates the same solution built with different frameworks. Demonstrates that the governance platform is framework-agnostic — it applies the same guardrails, evaluation, and compliance gates regardless of implementation.

### Comparison Table

| Column | Description |
|--------|-------------|
| **Framework** | Implementation framework name |
| **Eval** | Overall evaluation score |
| **Guardrails** | Pass/total summary |
| **Latency** | Average latency in milliseconds |
| **Tokens** | Average token usage per run |
| **Cost/Run** | Average cost per execution |
| **Gate** | Deployment gate pass/fail |

### Frameworks Compared

| Framework | Eval | Guardrails | Latency | Tokens | Cost | Gate |
|-----------|------|------------|---------|--------|------|------|
| Claude Agent SDK | 0.89 | 6/6 | 1,200ms | 1,650 | $0.003 | PASS |
| OpenAI Agents SDK | 0.85 | 6/6 | 1,400ms | 1,920 | $0.004 | PASS |
| LangChain / LangGraph | 0.72 | 5/6 | 1,800ms | 2,100 | $0.005 | FAIL |

### Recommendation Panel

Below the table, an automated recommendation highlights:
- Which framework scored highest across eval, latency, and cost
- Which frameworks are blocked at the compliance gate and why
- Actionable next step (e.g. "requires config update before deployment")

---

## Data Sources

- Framework scores from `frameworkScores` array in `lib/data.ts`
- Best framework calculated dynamically by highest `evalScore`

---

## Key Components

| Component | File | Role |
|-----------|------|------|
| `ScorecardPage` | `app/scorecard/page.tsx` | Page layout, comparison table, recommendation logic |
| `HealthBadge` | `components/dashboard/HealthBadge.tsx` | Gate pass/fail badge per framework |

---

## Demo Narrative

Alex opens the scorecard. Three implementations of the same agent, governed by the same platform. Claude Agent SDK leads on eval (0.89), latency (1.2s), and cost ($0.003). LangChain is blocked — guardrail failure and lowest eval score. The recommendation makes it clear: same governance pipeline, different outcomes by framework.

**Key impression:** "The platform governs any framework. And the data tells you which one to use."
