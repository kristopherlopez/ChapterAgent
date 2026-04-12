# Compliance Health Dashboard

**Route:** `/` (Landing Page)
**Purpose:** Portfolio-level view of every registered AI/ML solution's compliance status.

---

## What It Shows

The hero view of the platform. When Alex opens the portal, this is what he sees — the health of every AI solution in the portfolio at a glance.

### Portfolio Table

Each row represents a registered solution with the following columns:

| Column | Description |
|--------|-------------|
| **Solution** | Name and short description |
| **Guardrails** | Pass/total summary (e.g. "8/8 PASS", "5/6 FAIL") |
| **Eval Score** | Overall evaluation score (0–1) |
| **Gate** | Deployment gate pass/fail |
| **Health** | Rolled-up health indicator |

Each row links to the [Solution Detail Page](02-solution-detail.md).

### Health Rollup Logic

| Status | Condition |
|--------|-----------|
| Green | All guardrails pass, eval score above threshold, deployment gate approved |
| Amber | Eval score below threshold but above minimum, or non-critical guardrail warning |
| Red | Any guardrail failure, eval below minimum, or deployment gate blocked |

### Compliance Summary Bar

Above the table, a summary section shows:
- Total solutions and how many are deployment-ready
- Count of blocked solutions with headline reason
- Timestamp of last compliance run
- Next scheduled run time

### Export All

A button in the header that produces a structured evidence report across all solutions. See [Evidence Export](03-evidence-export.md).

---

## Data Sources

- Solution summaries from `solutions` array in `lib/data.ts`
- Each solution's `health`, `guardrailsSummary`, `evalScore`, and `gateResult` fields drive the table

---

## Key Components

| Component | File | Role |
|-----------|------|------|
| `DashboardPage` | `app/page.tsx` | Page layout and table rendering |
| `ComplianceSummary` | `components/dashboard/ComplianceSummary.tsx` | Summary stats above the table |
| `SolutionRow` | `components/dashboard/SolutionRow.tsx` | Individual solution row with link to detail |
| `HealthBadge` | `components/dashboard/HealthBadge.tsx` | Green/amber/red status indicator |
| `ExportButton` | `components/evidence/ExportButton.tsx` | "Export All" action |

---

## Demo Narrative

Alex opens the portal and immediately sees three solutions green, one red. No clicking required to know something is wrong. The red solution's guardrail summary ("5/6 FAIL") tells him the category of failure. One click takes him to the detail.

**Key impression:** "I can see the health of my entire AI portfolio in one screen."
