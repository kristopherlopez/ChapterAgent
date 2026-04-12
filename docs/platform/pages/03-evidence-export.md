# Evidence Export

**Trigger:** "Export All" button on dashboard, "Export Evidence" button on solution detail
**Purpose:** Produce a structured, auditor-ready compliance report without a meeting.

---

## What It Does

Generates a structured evidence report — a populated template, not a dynamically generated document. The report contains everything an auditor, risk committee, or governance lead needs to review a solution's compliance posture.

### Export Scopes

| Trigger | Scope |
|---------|-------|
| "Export All" on dashboard | All registered solutions in one report |
| "Export Evidence" on solution detail | Single solution report |

### Report Contents

Each solution section includes:

1. **Solution metadata** — name, description, risk tier, owner, category (AI/ML)
2. **Guardrail results** — every guardrail check with pass/fail and detail
3. **Evaluation scores** — every metric against its threshold with status
4. **Compliance gate decision** — result, reason, and timestamp
5. **Summary** — count of failures/warnings, overall health status

### Format

JSON and/or PDF. The goal is a structured, reviewable artefact that can be attached to a governance record, shared with an auditor, or filed as evidence — without requiring a walkthrough or meeting.

---

## Key Components

| Component | File | Role |
|-----------|------|------|
| `ExportButton` | `components/evidence/ExportButton.tsx` | Triggers export (dashboard or solution scope) |

---

## Demo Narrative

Alex clicks "Export Evidence" on the Q&A Agent detail page. A structured report downloads containing the full guardrail results, evaluation scores, and gate decision. He could hand this to an auditor today.

**Key impression:** "Compliance evidence is a button click, not a meeting."
