# PetSure Australia Governance Portal — Overview

## What We're Building

A working platform that shows Alex what "governance on autopilot" looks like — reusable components, compliance-as-code, and a portal that makes it all visible. One demo solution runs through the platform end-to-end to prove it works.

The platform is the product. The portal is the entry point. The demo solution is the proof.

---

## Platform-First, Governance-Led

The platform provides **reusable components** that any team's AI solution plugs into — guardrails, evaluation, compliance gates, observability. The portal surfaces the results. Alex's first impression should be: "manual governance is gone."

### Portal Screens

1. **Compliance health dashboard** (landing page) — green/amber/red across all solutions
2. **Solution detail page** — guardrail results, eval scores, gate pass/fail, execution trace for a given solution
3. **Evidence export** — button that produces a structured report (populated template)
4. **Solution registry** — dedicated page showing all registered solutions with category (AI/ML), risk tier, owner
5. **Multi-platform scorecard** — framework comparison table

Sidebar navigation groups solutions into **AI Solutions** (GenAI/agentic) and **ML Solutions** (traditional ML) with health indicator dots. A **Platform** section links to the Solution Registry.

---

## Demo Solution

One solution, exercised thoroughly, proving the platform works end-to-end:

| Demo Solution | Solution Type | What It Proves |
|---|---|---|
| **Q&A Agent** — answers questions about PetSure Australia's governance policies, retrieves context, cites sources. Implemented in three frameworks (Claude Agent SDK, OpenAI SDK, LangChain/LangGraph) with multiple retrieval strategies. | Q&A | Guardrails catching bad answers, eval harness in action, compliance gates firing, multi-framework governance, scope enforcement, citation coverage — all visible in the portal |

The Q&A agent is the most common solution type teams build. If the platform can govern it well — across multiple frameworks, retrieval strategies, and failure modes — it can govern anything. See `../solutions/01-qa-agent.md` for the full solution spec.

---

## Platform Components (Reusable)

These are the components the team builds once. Every team's solution plugs into them.

| Component | Real Code | What It Does | Portal Representation |
|---|---|---|---|
| Guardrail framework | Yes | Catches bad answers, PII, scope violations, prompt injection | Results shown in solution detail |
| Evaluation harness | Yes | Golden dataset scoring, pass/fail thresholds, DeepEval metrics | Scores shown in solution detail |
| Compliance-as-code gates | Yes | 8 automated deployment gates that actually fire | Gate pass/fail shown in dashboard |
| Solution manifest schema | Yes | Self-registration via `solution.yaml` — teams declare, platform discovers | Solution registry in portal |
| Observability layer | Pre-recorded | Step-level traces from instrumented solutions | Traces shown in observability view |
| Unified portal | Yes | Real, functional UI surfacing all of the above | — |

---

## Demo Approach

- **Live query + pre-recorded scenarios** — ask the Q&A agent a question live, then walk through six pre-recorded governance scenarios (happy path, scope refusal, faithfulness catch, temporal accuracy failure, prompt injection, citation gap)
- **Real PetSure Australia governance policies** as the document corpus — publicly available, no sensitive data
- **Three framework implementations** compared on the multi-platform scorecard — same corpus, same golden dataset, same governance, different frameworks
- **Impressive but scoped** — things visibly work, governance visibly catches problems, but not production-grade

---

## Build Priority (cut from the bottom if time runs out)

1. Platform reusable components (guardrails, eval harness, compliance gates)
2. Portal (the entry point — makes the platform visible)
3. Q&A Agent — Claude Agent SDK implementation
4. Q&A Agent — OpenAI SDK implementation
5. Q&A Agent — LangChain/LangGraph implementation
6. Multi-platform scorecard in portal
7. Observability traces in portal
