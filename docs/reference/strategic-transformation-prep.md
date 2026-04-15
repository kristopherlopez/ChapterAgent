# Strategic Transformation — Interview Prep

The JD lists four points under "Drive strategic transformation." This covers the first three.

---

## 1. Pioneer advancements in AI-powered risk management by delivering state-of-the-art AI capabilities

### What they're really asking
"Can you push the boundary on how AI gets validated, governed, and made reusable in risk management?" This is a 2nd-line role — your team doesn't build the fraud model or the credit scorer. The teams (1st-line) do that. Your team builds the tooling, platforms, and governance frameworks that make those models safe to deploy and fast to validate.

### What "state-of-the-art" looks like in risk management AI (2026)

**What you need to understand deeply enough to validate (1st-line builds these):**
- Graph neural networks for fraud detection — catching fraud rings, not just individual transactions
- Causal inference for intervention design — not just "who's risky" but "what action changes the outcome"
- Online learning — models that adapt to distribution shift without full retraining cycles
- Survival analysis / time-to-event models for collections — when will a customer default, not just will they
- Real-time credit decisioning with explainable models (not batch scoring overnight)

Your team needs the technical depth to assess whether these models are sound, fair, and production-ready. You don't build them — you validate them.

**What your team actually builds (2nd-line — tooling, platforms, governance):**
- Agentic model validation workflows — LLM agents that read model documentation, run validation tests, draft findings, and flag gaps. Turns a 6-week manual review into days.
- RAG over APRA prudential standards — mapping regulatory changes to affected models and controls automatically
- Automated evaluation harnesses — standard pipelines for fairness, performance, and robustness testing across all team-built models
- Synthetic data generation for stress testing — generating realistic but privacy-safe scenarios for model robustness testing
- Natural language querying of risk dashboards — stakeholders ask questions in plain English, get answers from model monitoring data
- LLM-powered anomaly explanation — when a model flags unusual behaviour, an LLM generates a human-readable explanation of what's driving it

### How to talk about it

> "My team doesn't build the fraud model — we build the validation tooling, governance framework, and reusable components that make it safe to deploy. That's where 'pioneering' lives in a 2nd-line role: pushing the boundary on how AI gets validated, governed, and scaled.
>
> The teams are building graph neural networks for fraud, causal models for intervention design, online learning systems that adapt in real time. My team needs the technical depth to validate all of that — but what we actually ship is different. We build agentic validation workflows that compress a 6-week manual review into days. RAG over APRA standards so regulatory changes map automatically to affected models. Automated evaluation harnesses for fairness and robustness. Synthetic data pipelines for stress testing.
>
> At PetSure I built the GenAI operating model — governance, evaluation, guardrails — that let us move from experimentation to production. The principle is the same here at larger scale: make the right thing the easy thing, and make compliance a byproduct of following the paved road, not a manual burden."

### Proof points from your experience
- Built GenAI operating model at PetSure from scratch — governance, evaluation, production deployment
- Moved team from 0 to multiple production AI systems in under 2 years
- Hands-on with agentic architectures, RAG, LLM evaluation frameworks

---

## 2. Develop and implement a unified portal encompassing all AI-driven risk management tools, insights, and guidance

### What they're really asking
"We have fragmented AI tools and dashboards across risk management. Can you bring it together into one place?" This is a platform product management challenge as much as a technical one.

### What a unified portal would look like

**Layer 1 — Model Registry & Inventory**
- Every model in production with its risk tier, owner, team, status, last validation date
- Lifecycle tracking: development → validation → production → monitoring → retirement
- APRA-ready: auditors can pull up any model and see its full lineage

**Layer 2 — Monitoring & Health**
- Central dashboard: drift scores, performance metrics, fairness metrics, alert status — all filterable by risk tier, business unit, model type
- Traffic light system: green/amber/red per model, rolling up to portfolio-level health
- Drill-down: click any model to see its specific monitoring detail

**Layer 3 — GenAI Quality & Agent Activity**
- LLM system quality scores: hallucination rates, faithfulness, safety violations
- Agent audit trails: who ran what, what tools were accessed, what actions were taken
- Cost attribution: token spend by team, system, model

**Layer 4 — Guidance & Standards**
- Living documentation: how to deploy a model, how to set up monitoring, how to request retraining
- Templates: model cards, validation reports, fairness assessments — pre-populated, version-controlled
- Community of practice content: past workshops, post-mortems, decision records

**Layer 5 — Workflow & Governance**
- Retraining requests with automated approval routing based on risk tier
- Model promotion gates: submit for validation, track progress, view sign-off status
- Regulatory submission tracking: which models are due for periodic review

### How to talk about it

> "A unified portal isn't a dashboard project — it's the operating system for AI in risk management. The goal is that a data scientist, a team lead, a model risk analyst, or an APRA auditor can all come to one place and get what they need.
>
> I'd approach it in layers. First, get the model registry right — every model inventoried with its risk tier, owner, lifecycle status, and validation history. That's table stakes for APRA. Second, monitoring — a central view of model health across the portfolio, filterable by tier and business unit, with drill-down into individual models. Third, GenAI-specific views — quality scores, agent activity, cost attribution. Fourth, guidance — living documentation, templates, community of practice content. And fifth, workflow — retraining requests, promotion gates, regulatory review tracking.
>
> The critical design principle is that it's not optional. If you deploy a model through the standard pipeline, you appear in the portal automatically. It's not a reporting burden — it's a byproduct of following the paved road."

### Proof points from your experience
- Built centralised AI capability at PetSure — went from fragmented initiatives to a governed, visible portfolio
- Experience designing operating models that create visibility for leadership without creating overhead for practitioners
- Understand the stakeholder lens: what a data scientist needs vs what a GM needs vs what an auditor needs

---

## 3. Provide standardised architecture, reusable AI solution components, and compliance-as-code frameworks

### What they're really asking
"Can you build the platform layer that makes 50+ data scientists productive and compliant without slowing them down?" This is the highest-leverage part of the role.

### Standardised architecture

**What this means in practice:**
- A reference architecture that every team follows — not prescriptive to the point of rigidity, but opinionated enough that models are consistent
- Standard patterns for: data ingestion → feature engineering → training → evaluation → deployment → monitoring
- Environment consistency: same tooling, same CI/CD patterns, same model registry, same monitoring stack
- Clear separation: what the platform provides vs what teams are responsible for

**Example components:**
| Component | What it provides |
|-----------|-----------------|
| **Model training template** | Cookiecutter/template repo with standard project structure, logging, experiment tracking, unit tests |
| **Feature Store integration** | Standard connectors to shared Feature Store, avoiding training-serving skew |
| **Deployment pipeline** | GitHub Actions / CI/CD templates for model packaging, container build, registry push, canary deployment |
| **Monitoring sidecar** | Every deployed model gets drift detection, performance tracking, alerting — zero team configuration |
| **LLM evaluation harness** | Standard evaluation pipeline for GenAI: golden test sets, LLM-as-a-Judge rubrics, regression testing |
| **RAG template** | Reference implementation for retrieval-augmented generation with chunking, embedding, retrieval, and evaluation built in |

### Reusable AI solution components

**The principle:** Build once, deploy many times. Teams shouldn't rebuild common capabilities from scratch.

- **Guardrails library** — PII detection, prompt injection scanning, topic filtering — importable as a package
- **Evaluation SDK** — standard metrics, assertion libraries, human review workflow integration
- **Agent framework** — approved MCP servers, permission policies, audit trail middleware, cost tracking
- **Prompt management service** — versioning, A/B testing, approval gates, rollback capability
- **Explainability toolkit** — SHAP/LIME wrappers, feature importance, natural language explanations — consistent across all models

### Compliance-as-code frameworks

**What it is:** Regulatory and policy requirements encoded as automated checks that run in the ML pipeline. Compliance becomes a CI/CD gate, not a manual review.

**Concrete implementation:**

| Pipeline stage | Automated check | What happens on failure |
|---------------|----------------|------------------------|
| **Pre-training** | Data lineage validated against approved sources catalogue | Block: can't train on unapproved data |
| **Post-training** | Fairness assertions (demographic parity, equalised odds) against protected attributes | Block: model can't proceed to validation |
| **Post-training** | Performance thresholds met (tier-specific — Tier 1 models have higher bars) | Block: must retrain or re-evaluate |
| **Pre-deployment** | Model card completeness check — all required fields populated | Block: can't deploy undocumented models |
| **Pre-deployment** | Approval chain complete in model registry (tier-specific sign-offs) | Block: waits for required approvals |
| **Production** | Drift exceeds threshold for N consecutive days | Alert → auto-trigger revalidation workflow |
| **Production** | Fairness metrics degrade beyond tolerance | Escalate to Model Risk Committee |
| **Retraining** | Champion-challenger validation passes | Block: retrained model can't replace current without proof it's better |

**Tools that enable this:**
- **Open Policy Agent (OPA)** — policy engine using Rego language, enforces rules across CI/CD and APIs
- **Great Expectations / Pandera** — data validation assertions as code
- **Custom Python assertion libraries** — fairness checks, performance checks, documentation checks
- **Model registry hooks** — MLflow / Weights & Biases with custom promotion gates

### How to talk about it

> "The way I think about this is: what does a data scientist's first day look like? If they join a team and have to figure out how to set up their environment, how to deploy a model, how to configure monitoring, how to meet APRA requirements — that's weeks of overhead and inconsistency across teams.
>
> What I'd build is the paved road. A model training template with standard structure, logging, and tests. A deployment pipeline that packages, deploys, and attaches monitoring automatically. A guardrails library they import, not build. An evaluation harness for GenAI systems. And compliance-as-code — fairness assertions, data lineage validation, documentation completeness checks, approval gates — all running as automated pipeline stages.
>
> The result: teams focus on the problem they're solving, not the infrastructure. Every model is consistent, governed, and auditable by default. And when APRA asks 'show me your controls,' you point at the pipeline, not a folder of Word documents.
>
> At PetSure I built this at a smaller scale — standardised our AI development lifecycle, governance framework, evaluation tooling. The principle is the same at PetSure Australia, the scale is different. The Head of's job is to make the right thing the easy thing."

### Proof points from your experience
- Built AI operating model and governance framework at PetSure
- Hands-on with CI/CD (GitHub Actions), containerisation (Docker/ECR), MLOps tooling
- Experience designing reusable components (JeromeLu.ai architecture demonstrates repeatable AI agent pattern)
- Understand the balance between standardisation and team autonomy — opinionated defaults, not rigid mandates
