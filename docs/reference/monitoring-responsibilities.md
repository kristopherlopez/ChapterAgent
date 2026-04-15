---
topic: ML & AI Monitoring — Role Responsibilities
related:
  - [[learning/topics/ml-ops/]]
  - [[learning/topics/ai-ops/]]
purpose: Interview prep — maps monitoring knowledge to what the Head of and teams actually do
---

# Monitoring Responsibilities — Head of vs Teams

## The Org Structure at PetSure Australia

- **Head of (you)** — sets standards, builds platforms, governs quality, upskills the team. You don't build individual models — you make it possible for 50+ data scientists to build and operate them well.
- **Teams (data scientists / ML engineers)** — build, deploy, and operate specific models within their business domain (credit risk, fraud, collections, marketing, etc.)

---

## What the Head of Does

### Standards & Templates (the "paved road")

You build the thing that teams deploy *with*, not the thing they deploy.

| What you build | Reference |
|---------------|-----------|
| **Monitoring template** — every model deploys with data drift, prediction drift, data quality, and alerting pre-configured | `ml-ops/03`, `ml-ops/04`, `ml-ops/05` |
| **Evaluation framework** — standardised LLM-as-a-Judge rubrics, assertion libraries, human review workflows | `ai-ops/02` |
| **Agent governance framework** — hooks, permission policies, audit trail aggregation, cost limits | `ai-ops/04`, `ai-ops/05` |
| **Prompt management standard** — versioning, testing, rollback, approval gates | `ai-ops/06` |
| **Security baseline** — input/output guardrails, PII scanning, injection detection as a shared service | `ai-ops/08` |
| **Cost governance model** — attribution tagging, budget allocation, model routing guidelines | `ai-ops/07` |
| **Vendor monitoring capability** — golden test sets, output distribution tracking, contractual templates | `ai-ops/09` |
| **Fairness monitoring toolkit** — standard metrics, segmentation requirements, regulatory reporting templates | `ml-ops/09` |

The key principle: **teams shouldn't have to think about monitoring architecture.** They deploy a model, it comes with monitoring. Like deploying a microservice comes with logging and health checks.

### Central Dashboards & Visibility

| Dashboard | Audience | What it shows |
|-----------|----------|---------------|
| **Model Health** — risk-tiered view of all models | Head of, Model Risk Committee | Drift scores, performance metrics, alert status by model tier |
| **GenAI Quality** — quality scores across all LLM-powered systems | Head of, Product owners | Hallucination rates, faithfulness, safety violations |
| **Agent Activity** — sessions, costs, blast radius across all agent usage | Head of, Security | Who's running what, what did it touch, what did it cost |
| **Cost** — token spend by team, system, model | Head of, Finance | Budget burn, attribution, optimisation opportunities |
| **Regulatory** — APRA-ready model risk reporting | Model Risk Committee, Compliance | Performance by model tier, fairness metrics, drift status |

### Governance & Escalation

You define the rules, not just the tools:

- **Risk tiering** — which models are Tier 1 (customer-facing, regulatory-critical) vs Tier 3 (internal tools)? Tier determines monitoring rigour.
- **Retraining governance** — who can trigger retraining? What validation gates exist? How does a retrained model get promoted through the registry?
- **Alert escalation paths** — drift alert on a Tier 3 model → team handles it. Drift alert on a Tier 1 credit risk model → team + Team Lead + Model Risk Committee.
- **Agent approval tiers** — which MCP servers can agents access? Who approves new tool access? What's the incident playbook when an agent makes a destructive change?
- **Vendor change management** — what happens when Azure OpenAI updates a model? Who validates? Who approves the switch?

### Upskilling the Team

This is the part most people miss. The Head of's job is to raise the floor:

- Run workshops on monitoring best practices
- Pair senior data scientists with juniors on monitoring implementation
- Share post-mortems when monitoring catches (or misses) a problem
- Build a community of practice around MLOps and AI Ops

---

## What the Data Scientists / Teams Do

### For Traditional ML Models

| Activity | Cadence | Reference |
|----------|---------|-----------|
| **Deploy model with monitoring template** — configure thresholds for their specific model | At deployment | `ml-ops/03`, `ml-ops/04` |
| **Review drift alerts** — investigate when their model flags drift | As alerts fire | `ml-ops/04`, `ml-ops/05` |
| **Cohort performance analysis** — track model accuracy by origination cohort as labels arrive | Weekly/monthly | `ml-ops/07` |
| **Segmented performance review** — check for segment-level degradation | Monthly | `ml-ops/07` |
| **Fairness reporting** — run fairness metrics for their model, flag issues | Monthly / pre-regulatory-review | `ml-ops/09` |
| **Retraining** — when drift/degradation is confirmed, retrain and promote through registry | As needed | `ml-ops/06`, `ml-ops/01` |
| **Feature Store maintenance** — keep feature definitions current, fix training-serving skew | Ongoing | `ml-ops/03` |

### For GenAI / LLM Systems

| Activity | Cadence | Reference |
|----------|---------|-----------|
| **Configure evaluation pipeline** — set up LLM-as-a-Judge rubrics for their specific system | At deployment | `ai-ops/02` |
| **Review quality scores** — investigate when hallucination or faithfulness scores degrade | Daily (Tier 1), weekly (Tier 2) | `ai-ops/02` |
| **RAG tuning** — fix retrieval issues (chunking, embedding, index freshness) | As quality monitoring surfaces issues | `ai-ops/03` |
| **Prompt iteration** — version, test, and deploy prompt changes through the standard pipeline | As needed | `ai-ops/06` |
| **Human review** — sample and review outputs for their system | Daily/weekly by tier | `ai-ops/02` |
| **Cost optimisation** — right-size model selection, tune retrieval, optimise prompts | Monthly | `ai-ops/07` |
| **Security review** — review injection attempts and abuse patterns for their system | Weekly | `ai-ops/08` |

---

## Summary — Who Owns What

| Responsibility | Head of | Data Scientists / Teams |
|---------------|-------------------|------------------------|
| **Monitoring platform** | Builds and maintains it | Uses it |
| **Standards & templates** | Defines them | Implements them |
| **Risk tiering** | Sets the tiers and requirements | Operates within their tier |
| **Dashboards** | Central dashboards across all models | System-specific dashboards |
| **Alert response** | Escalation for Tier 1, trend analysis | First responder for their models |
| **Retraining governance** | Defines the process and gates | Executes retraining within the process |
| **Fairness & regulatory** | Reporting framework, APRA interface | Run metrics, flag issues |
| **Upskilling** | Workshops, pairing, community of practice | Learn, adopt, give feedback |
| **Vendor management** | Contractual, change management process | Golden test set execution, quality validation |
| **Agent governance** | Policy, hooks, audit aggregation | Operate within the guardrails |

---

## Interview Framing

> "As Head of, my job isn't to build individual models — it's to build the platform and standards that let 50+ data scientists build and operate models well. For monitoring, that means a standardised template every team deploys with — drift detection, performance tracking, alerting, fairness metrics — so they don't have to reinvent monitoring for every model. A central dashboard that gives the Model Risk Committee a risk-tiered view across all models. Governance for retraining — who can trigger it, what gates exist, how models promote through the registry. And for GenAI specifically, evaluation frameworks, prompt management standards, agent governance with audit trails, and vendor monitoring capability. The teams own their models and respond to alerts. I own the system that makes all of that consistent, visible, and governable."
