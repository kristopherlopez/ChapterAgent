# Solution Registry

**Route:** `/registry`
**Purpose:** Catalogue of all registered solutions discovered from `solution.yaml` manifests, showing the self-registration model.

---

## What It Shows

A dedicated page listing every solution the platform has discovered, with richer metadata than the dashboard. Demonstrates the manifest-driven onboarding model — teams register themselves, the platform discovers and governs automatically.

### Registry Table

| Column | Description |
|--------|-------------|
| **Solution** | Name and description |
| **Category** | AI or ML |
| **Risk Tier** | Customer-Facing, High, Medium, Internal |
| **Owner** | Responsible team |
| **Guardrails** | Summary count (e.g. `8/8 PASS`, `5/6 FAIL`) |
| **Gate** | Deployment gate — minimal icon (check or cross) |
| **Health** | 14-day health trend sparkline (green/amber/red lines) |
| **Last Tested** | Relative timestamp with stale indicator |

Each row links to the [Solution Detail Page](02-solution-detail.md).

### Health Sparkline

A colour-coded line sparkline showing the last 14 days of health status, rendered against three background bands:
- Green band / line = pass
- Amber band / line = warn
- Red band / line = fail

Gives at-a-glance visibility into solution stability over time — a solution that's green today but was red for the last week tells a different story than one that's been green all month.

### Stale Indicator

Solutions not tested in 7+ days show an amber warning badge next to the "Last Tested" timestamp. This surfaces solutions that may have drifted out of compliance without anyone noticing.

### Onboard Solution

An **Onboard Solution** link in the sidebar (and discoverable from the registry page) opens a five-step wizard at `/onboard`:

1. **Basics** — name, ID, description, version, owner, risk tier, solution type
2. **Configuration** — type-specific fields (endpoint URL, model/dataset config, or corpus/frameworks)
3. **Guardrails** — type-specific thresholds and toggles
4. **Evaluation & Compliance** — metric rows with thresholds, compliance gate selection
5. **Review & Submit** — read-only summary, then submit

On submit the platform creates the `solutions/{id}/` directory, writes `solution.yaml`, scaffolds the golden dataset, and registers initial results. The new solution appears in the registry immediately with a "pending" health status.

### How Registration Works

The self-registration model supports two paths:
- **UI wizard** — use the Onboard Solution flow described above
- **File-based** — solutions declare themselves via a `solution.yaml` manifest; the platform discovers manifests automatically

In both cases, guardrail profiles are applied based on solution type and risk tier.

### Legend

A legend bar at the bottom explains the sparkline colours and stale indicator.

---

## Data Sources

- Solution summaries from `solutions` array in `lib/data.ts`
- `healthHistory` array on each solution drives the sparkline
- `lastTested` field drives the stale calculation (threshold: 7 days)

---

## Key Components

| Component | File | Role |
|-----------|------|------|
| `RegistryPage` | `app/registry/page.tsx` | Page layout, table rendering, stale logic |
| `HealthBadge` | `components/dashboard/HealthBadge.tsx` | Gate pass/fail badge |
| `Sparkline` | `components/dashboard/Sparkline.tsx` | 14-day health trend visualisation |

---

## Demo Narrative

Alex navigates to the Solution Registry. He sees all four solutions — three AI, one ML — with their categories, risk tiers, and owners. The Credit Default Scorer shows a stale warning (last tested 15 days ago). The Multi-Platform Agent's sparkline is almost entirely red. He understands which solutions need attention without clicking into any of them.

**Key impression:** "Teams onboard themselves. The platform discovers, governs, and surfaces problems automatically."
