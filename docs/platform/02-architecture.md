# Architecture

## Architectural Principles

### 1. Portal-First

The portal is the primary artefact. Every component, solution, and pipeline exists to populate what appears in the portal. Design decisions flow from "what does this look like in the portal?" backwards to implementation.

### 2. Reusable Components, Not Reusable Frameworks

The platform is built on a **shared core** of framework-agnostic components (guardrails, evaluation, compliance gates, observability). Solutions choose their own orchestration framework. The shared components work identically regardless of whether the solution is a RAG pipeline, an agentic workflow, or a multi-framework comparison.

This mirrors how the team would operate: build the components once, let teams choose their orchestration.

### 3. Config-Driven Where It Matters

Things that change — guardrail rules, evaluation thresholds, compliance gates, risk tiers — are defined in human-readable YAML/JSON config files. Things that don't change — the plumbing that executes those rules — are clean, well-structured code.

The test: a team developer or a governance reviewer should be able to open a PR that changes a guardrail rule and understand the change from the diff alone, without reading the underlying framework code.

### 4. Keras-Style Developer Experience

Components follow a consistent, predictable API pattern inspired by Keras:

- **Verbose, descriptive function and parameter names** — clarity over brevity. A developer reading a solution should understand what's happening without diving into source.
- **Progressive disclosure** — simple to use at the surface (`evaluate(solution)`, `check_compliance(solution)`), with full control available when you drill in.
- **Consistent patterns across components** — guardrails, eval, compliance, and observability all follow the same structural conventions. Learn one, know them all.
- **No magic** — explicit over implicit. If a guardrail runs, you can see it was invoked and why.

### 5. Human-Reviewable by Default

Every artefact the platform produces — config, results, evidence, traces — should be readable by a human without tooling. Changes to rules, thresholds, and gates show up clearly in PR diffs. Evaluation results and compliance reports are structured but not opaque.

This principle exists because the team sits in 2nd-line Risk Management. The people reviewing this work are not always engineers.

### 6. Tested at Two Levels

**Level 1 — Platform tests itself:** Unit tests, integration tests, and linting run in a CI/CD pipeline. This demonstrates engineering discipline and how the team operates.

**Level 2 — Platform tests solutions:** The evaluation harness and compliance gates test the AI solutions that pass through the platform. This is the product — governance on autopilot.

Both levels are visible: Level 1 in the repo's CI pipeline, Level 2 in the portal.

### 7. Solution Self-Registration via Manifest

Each solution declares itself through a manifest file (e.g., `solution.yaml`) that specifies:

- Solution name and description
- Risk tier
- Which guardrails apply
- Evaluation dataset path
- Compliance gate configuration

The platform discovers solutions by reading their manifests. Solutions are self-contained and portable — add a new solution by dropping in a folder with a manifest, not by editing a central config.

### 8. Monorepo

Portal, platform components, and all demo solutions live in a single repository. Given the tight timeline and high interdependency between components, this minimises friction and keeps everything in sync.

---

## Shared vs Solution-Specific

| Shared (platform core) | Solution-Specific |
|---|---|
| Guardrail framework | Orchestration logic |
| Evaluation harness | Prompts and prompt chains |
| Compliance-as-code gates | Tools and tool definitions |
| Observability layer | Retrieval strategy (if applicable) |
| Portal integration | Solution manifest |
| Solution discovery via manifest | Domain-specific config |

---

## System Diagram

```
+------------------------------------------------------------------+
|                     Unified Portal (Web UI)                       |
|  - Compliance health dashboard (landing)                         |
|  - Solution detail pages                                         |
|  - Evidence export                                               |
|  - Observability / trace view                                    |
|  - Multi-platform scorecard                                      |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|                      API / Backend                                |
|  - Solution discovery (reads solution.yaml manifests)            |
|  - Aggregates results from platform components                   |
|  - Serves portal data                                            |
+------------------------------------------------------------------+
         |
         +---------------------------+
         |                           |
         v                           v
+------------------+    +---------------------------+
| Platform Core    |    | Demo Solutions            |
|                           |
|                  |    |                           |
| - Guardrails     |    | 1. Q&A Agent             |
| - Evaluation     |    | 2. Validation Agent      |
| - Compliance     |    | 3. Classification Agent  |
|   Gates          |    |                           |
| - Observability  |    |                           |
+------------------+    +---------------------------+
         |                           |
         +---------------------------+
         |
         v
+------------------------------------------------------------------+
|                     CI/CD Pipeline                                |
|  - Platform unit/integration tests (Level 1)                     |
|  - Solution eval + compliance checks (Level 2)                   |
+------------------------------------------------------------------+
```

## Document Index

### Platform (`docs/platform/`)

| # | Doc | Topic |
|---|---|---|
| 00 | [00-background.md](00-background.md) | Background & Context |
| 01 | [01-overview.md](01-overview.md) | Overview |
| 02 | [02-architecture.md](02-architecture.md) | Architecture (this doc) |
| 03 | [03-tech-stack.md](03-tech-stack.md) | Tech Stack & Project Structure |
| 04 | [04-solution-lifecycle.md](04-solution-lifecycle.md) | Solution Lifecycle (Intake → Assessment → Production) |
| 05 | [05-portal.md](05-portal.md) | Portal / Web UI |
| 06 | [06-guardrails.md](06-guardrails.md) | Guardrail Framework |
| 07 | [07-compliance-as-code.md](07-compliance-as-code.md) | Compliance-as-Code Gates |
| 08 | [08-evaluation-harness.md](08-evaluation-harness.md) | Evaluation Harness (DeepEval) |
| 09 | [09-context-retrieval.md](09-context-retrieval.md) | Context Retrieval Framework |
| 10 | [10-observability.md](10-observability.md) | Observability Layer |
| 11 | [11-build-phases.md](11-build-phases.md) | Build Phases |
| 12 | [12-interview-delivery.md](12-interview-delivery.md) | Interview Delivery |
| 13 | [13-governance-framework.md](13-governance-framework.md) | Governance, Responsible AI & Risk Management Framework |
| 14 | [14-controls-register.md](14-controls-register.md) | Controls Register (cross-reference index) |

### Solutions (`docs/solutions/`)

| # | Doc | Topic |
|---|---|---|
| 00 | [../solutions/00-solution-types.md](../solutions/00-solution-types.md) | Solution Type Taxonomy (GenAI & ML) |
| 01 | [../solutions/01-qa-agent.md](../solutions/01-qa-agent.md) | Demo Solution #1: Q&A Agent |
| 07 | [../solutions/07-governance-policy-agent.md](../solutions/07-governance-policy-agent.md) | Demo Solution #2: Governance Policy Agent |
