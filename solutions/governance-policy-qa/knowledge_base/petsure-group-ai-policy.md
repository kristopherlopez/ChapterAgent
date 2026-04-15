# PetSure Australia Group AI Policy

**Document ID:** GOV-AI-001
**Version:** 2.1
**Status:** Active
**Effective Date:** 1 July 2025
**Next Review Date:** 1 July 2026
**Owner:** Group Risk
**Approval Authority:** Group Chief Risk Officer
**Classification:** Internal — Restricted

---

## 1. Purpose

This policy establishes mandatory requirements for the safe, ethical, and compliant development, deployment, and operation of artificial intelligence systems across the PetSure Australia Group. It provides the overarching governance framework that all subordinate standards, frameworks, and guidelines must align to.

This policy exists because AI systems introduce risks that are qualitatively different from traditional software: they can produce outputs that are unpredictable, difficult to explain, and harmful in ways that may not be immediately apparent. The Group requires a governance approach proportionate to these risks while enabling the responsible use of AI to serve customers and improve operations.

## 2. Scope

This policy applies to:

- All AI and machine learning systems developed, procured, or operated by any PetSure Australia business unit, subsidiary, or third-party vendor acting on PetSure Australia's behalf.
- Both generative AI (large language models, retrieval-augmented generation, agentic workflows, conversational AI) and traditional machine learning (scoring models, classifiers, anomaly detectors, forecasting models).
- Systems in all lifecycle stages: development, testing, staging, production, and retirement.
- AI components embedded within larger systems, even where AI is not the primary function.

This policy does **not** apply to:
- Pure analytics and business intelligence reporting that does not use predictive or generative models.
- Robotic process automation (RPA) that follows deterministic rules without AI/ML components.
- Research prototypes that are not connected to production systems or real customer data, unless they are being prepared for production deployment.

## 3. Definitions

| Term | Definition |
|------|-----------|
| **AI Solution** | Any system that uses machine learning, deep learning, or generative AI to produce outputs, predictions, classifications, or decisions. Includes both standalone AI systems and AI components within larger applications. |
| **Risk Tier** | A classification assigned during intake that determines the level of governance applied to a solution. Three tiers: `experimental` (lowest), `production_internal` (medium), `production_customer_facing` (highest). |
| **Solution Manifest** | A structured YAML file (`solution.yaml`) that declares a solution's identity, type, owner, risk tier, guardrail configuration, evaluation criteria, and compliance requirements. The manifest is the solution's contract with the platform. |
| **Guardrail** | An automated check that runs on AI inputs or outputs to enforce safety, scope, and quality boundaries. Guardrails may block, flag, or log depending on configuration. |
| **Golden Dataset** | A curated, human-reviewed set of test cases used to evaluate an AI solution's quality, safety, and compliance. Golden datasets must be representative of production scenarios including edge cases and adversarial inputs. |
| **Deployment Gate** | An automated compliance check that must pass before a solution can enter or remain in production. Eight gates are defined in this policy (see Section 6). |
| **Governance Portal Team** | The Risk Management AI capability team responsible for maintaining the AI governance platform, reviewing solution intakes, and providing governance tooling to teams. |
| **Team** | A cross-functional delivery team that builds and operates an AI solution. Teams are accountable for their solution's behaviour; the Governance Portal team provides the governance infrastructure. |

## 4. Principles

All AI governance at PetSure Australia is grounded in five principles. These principles inform every standard, framework, and guideline referenced by this policy.

### 4.1 Proportionate Governance

Governance intensity must match risk. An experimental prototype used by three internal analysts does not require the same rigour as a customer-facing credit scoring model. The risk tier system (Section 5) exists to codify this proportionality.

However, proportionality is not an excuse for avoidance. Every AI solution, regardless of tier, must be registered, have an owner, and have a minimum set of guardrails active. The floor is non-negotiable; the ceiling scales with risk.

### 4.2 Transparency and Explainability

AI systems must be explainable to the degree required by their impact. For customer-facing decisions, this means affected individuals must be able to understand why an AI-assisted decision was made. For internal systems, this means operators and risk managers must be able to inspect the system's reasoning.

Explainability takes different forms depending on solution type: citation coverage for Q&A agents, feature importance (SHAP) for scoring models, decision traces for agentic workflows.

### 4.3 Fairness and Non-Discrimination

AI systems must not produce systematically biased outputs across demographic groups. Bias testing is mandatory for all solutions above experimental tier, with stricter thresholds for customer-facing systems.

The definition of fairness must be documented for each solution because fairness means different things in different contexts. Demographic parity may be appropriate for one use case while equalised odds is appropriate for another. The Governance Portal team reviews fairness definitions during intake.

### 4.4 Privacy by Design

AI systems must not collect, store, process, or expose personal information beyond what is explicitly required and authorised for the solution's function. PII detection guardrails are mandatory for all solutions that process text or unstructured data.

This principle extends to training and evaluation data. Golden datasets must use synthetic or appropriately anonymised data. Real customer data must not be used in test cases.

### 4.5 Accountability and Auditability

Every AI interaction must be traceable. The audit trail must be complete enough to reconstruct any AI-assisted decision after the fact. This is both a regulatory requirement (APRA CPS 230, CPS 234) and an operational necessity for incident response.

Accountability is personal: every solution has a named owner in the solution manifest. The Governance Portal team does not accept solutions without an identified accountable individual.

## 5. Risk Tier Classification

### 5.1 Tier Definitions

| Tier | Label | Criteria | Examples |
|------|-------|----------|----------|
| **Tier 1** | `experimental` | Not connected to production systems. No real customer data. Used for research, prototyping, or internal exploration. | Research prototypes, hackathon projects, internal tooling experiments |
| **Tier 2** | `production_internal` | Deployed in production but used only by internal PetSure Australia staff. Outputs inform decisions but do not directly reach customers. | Internal Q&A agents, risk assessment tools, model validation assistants, operational dashboards |
| **Tier 3** | `production_customer_facing` | Outputs are visible to or directly impact customers, investors, regulators, or the public. | Customer chatbots, public Q&A agents, credit scoring models, automated decisioning |

### 5.2 Governance by Tier

| Requirement | Experimental | Production Internal | Production Customer-Facing |
|-------------|-------------|--------------------|-----------------------------|
| Solution manifest | Required | Required | Required |
| Named owner | Required | Required | Required |
| Guardrails active | Minimum set (scope, injection) | Full set | Full set at strictest thresholds |
| Golden dataset | Recommended | Required (30+ cases) | Required (50+ cases) |
| Golden dataset sign-off | Not required | Required | Required |
| Evaluation harness | Recommended | Required | Required |
| Bias testing | Not required | Required | Required at strictest thresholds |
| Audit trail | Recommended | Required (sampling OK) | Required (100% coverage) |
| Prompt governance | Not required | Required | Required |
| Re-evaluation cadence | None | Every 90 days | Every 30 days |
| Compliance gates | Registration only | All 8 gates | All 8 gates |
| Independent review | Not required | Recommended | Required |

### 5.3 Tier Assignment

Risk tier is assigned by the Governance Portal team during the solution intake process based on:

1. **Audience** — who sees or is affected by the AI outputs?
2. **Decision impact** — what decisions do the outputs inform or automate?
3. **Data sensitivity** — what data does the solution access and what data appears in outputs?
4. **Reversibility** — how easily can an incorrect AI output be identified and corrected?
5. **Regulatory exposure** — does the use case fall under specific regulatory requirements?

Tier assignment is documented in the solution manifest and can be changed if the solution's scope, audience, or impact changes. Tier changes trigger re-assessment of all governance requirements.

### 5.4 Tier Escalation

A solution must be escalated to a higher tier if any of the following occur:

- The solution's outputs begin reaching customers or external parties
- The solution begins processing real customer data (not synthetic)
- A regulator enquires about the solution or its use case
- An incident occurs that reveals higher impact than originally assessed
- The solution's scope expands beyond its original registration

Tier escalation cannot be reversed without Governance Portal team approval and a documented justification.

## 6. Compliance Gates

Every AI solution above experimental tier must pass eight automated compliance gates before deployment. These gates are enforced by the platform — they are not advisory, they are blocking.

### 6.1 The Eight Gates

| Gate | Control ID | What It Checks | Failure Action |
|------|-----------|----------------|----------------|
| **Registration** | AI-GOV-001 | Solution manifest is complete, valid, and includes all mandatory fields | Deployment blocked |
| **Evaluation Harness** | AI-GOV-003 | All golden dataset metrics meet risk-tier-specific thresholds | Deployment blocked |
| **PII Validation** | AI-GOV-005 | No PII detected in any golden dataset response | Deployment blocked |
| **Guardrail Validation** | AI-GOV-006 | All configured guardrails pass at required rate on golden dataset | Deployment blocked |
| **Bias & Toxicity** | AI-GOV-007 | Bias and toxicity scores within risk-tier thresholds | Deployment blocked |
| **Audit Trail** | AI-GOV-008 | 100% trace coverage across all golden dataset interactions | Deployment blocked |
| **Golden Dataset Sign-off** | AI-GOV-009 | Human reviewer has approved the golden dataset with recorded identity and date | Deployment blocked |
| **Prompt Governance** | AI-GOV-010 | System prompts are version-controlled with approval commit hash linked | Deployment blocked |

### 6.2 Gate Behaviour

Gates are binary: pass or fail. There is no "pass with conditions" or "advisory pass." If a gate fails, the solution cannot deploy until the failure is remediated and the gate re-run.

Gates run automatically in the CI/CD pipeline. They can also be triggered manually from the platform portal for ad-hoc assessment.

Gate results are recorded as structured evidence and included in the compliance evidence package. This package is exportable for audit purposes.

### 6.3 Gate Exceptions

In exceptional circumstances, a gate can be temporarily exempted. Exceptions require:

1. Written justification from the solution owner
2. Approval from the Team Lead **and** the relevant control owner
3. A documented remediation plan with a deadline (maximum 30 days)
4. The exception recorded in the compliance evidence package

Exceptions are not renewable. If the remediation deadline passes without resolution, the solution must be taken out of production.

The Registration gate (AI-GOV-001) cannot be exempted under any circumstances.

## 7. Guardrail Requirements

### 7.1 Mandatory Guardrails by Tier

| Guardrail | Experimental | Production Internal | Production Customer-Facing |
|-----------|-------------|--------------------|-----------------------------|
| Prompt injection detection | Required | Required | Required |
| Scope containment | Required | Required | Required |
| PII detection | Recommended | Required | Required (zero tolerance) |
| Faithfulness | Not required | Required (>= 0.85) | Required (>= 0.90) |
| Bias detection | Not required | Required (<= 0.10) | Required (<= 0.05) |
| Toxicity detection | Not required | Required (<= 0.10) | Required (<= 0.05) |
| Citation coverage | Not required | Required (>= 0.85) | Required (>= 0.95) |
| Temporal accuracy | Not required | Where applicable | Where applicable |

### 7.2 Custom Guardrails

Teams may implement additional guardrails specific to their use case. Custom guardrails must:

- Be documented in the solution manifest
- Be included in the guardrail test suite
- Produce structured pass/fail results compatible with the platform's evidence format
- Be included in the audit trail

The Governance Portal team reviews custom guardrails during intake to ensure they are appropriate and correctly implemented.

## 8. Evaluation Requirements

### 8.1 Golden Dataset Standards

Golden datasets must:

- Contain a minimum number of test cases based on risk tier (see Section 5.2)
- Cover expected scenarios, edge cases, and adversarial inputs
- Include cases for every configured guardrail (scope refusal, injection blocking, PII handling)
- Use synthetic or appropriately anonymised data — real customer data is prohibited
- Be reviewed and approved by a qualified person independent of the development team
- Be versioned and stored alongside the solution in the platform

### 8.2 Evaluation Metrics by Solution Type

The platform supports multiple evaluation metrics. The relevant metrics depend on the solution type:

- **Q&A solutions:** Faithfulness, answer relevancy, contextual precision, contextual recall, hallucination rate, citation coverage, boundary adherence
- **Classification solutions:** Accuracy, consistency, calibration, bias, fairness across demographics
- **Scoring models:** AUC/Gini, calibration (Brier score, ECE), discrimination testing (demographic parity, equalised odds), stability (PSI)
- **Validation solutions:** Completeness, severity calibration, faithfulness

Metric thresholds are configured per risk tier in the solution manifest. Customer-facing thresholds are strictly higher than internal thresholds.

### 8.3 Re-evaluation

Production solutions must be re-evaluated on a regular cadence:

- `production_internal`: every 90 days
- `production_customer_facing`: every 30 days
- After any model update, prompt change, or scope modification: immediately

Re-evaluation runs the full evaluation harness against the current golden dataset. If a re-evaluation fails, the solution remains in production but is flagged as non-compliant and the team has 14 days (customer-facing) or 30 days (internal) to remediate.

## 9. Incident Response

### 9.1 AI Incident Classification

| Severity | Criteria | Response Time | Escalation |
|----------|----------|---------------|------------|
| **Critical** | AI output causes customer harm, regulatory breach, or financial loss | Immediate | GCRO, Board Risk Committee |
| **High** | AI output is systematically incorrect, biased, or leaking PII | 4 hours | Team Lead, Solution Owner, relevant control owner |
| **Medium** | AI output quality degrades below thresholds but no immediate harm | 24 hours | Team Lead, Solution Owner |
| **Low** | Isolated incorrect output, caught by guardrails | 5 business days | Solution Owner |

### 9.2 Incident Procedures

When an AI incident is identified:

1. **Contain** — if the solution is causing ongoing harm, it must be taken out of production immediately. The platform supports emergency kill switches.
2. **Assess** — determine the scope, impact, and root cause. Use the audit trail to reconstruct the chain of events.
3. **Remediate** — fix the root cause. This may involve model retraining, prompt updates, guardrail reconfiguration, or data corrections.
4. **Re-evaluate** — run the full evaluation harness to confirm the fix. All gates must pass.
5. **Report** — document the incident, root cause, and remediation in the platform. Material incidents must be reported to APRA per CPS 230 requirements.

## 10. Roles and Responsibilities

| Role | Responsibilities |
|------|-----------------|
| **Group Chief Risk Officer** | Approval authority for this policy. Accountable for the Group's AI risk posture. |
| **Team Lead** | Maintains the AI governance platform. Reviews solution intakes. Approves tier assignments and gate exceptions. |
| **Solution Owner** | Accountable for their solution's compliance. Maintains the solution manifest. Responds to incidents. |
| **Team** | Builds and operates the AI solution. Implements guardrails. Maintains the golden dataset. |
| **AI Ethics Board** | Sets fairness principles. Reviews bias testing results for customer-facing solutions. |
| **Model Risk** | Reviews scoring models and classifiers. Provides independent validation. |
| **Internal Audit** | Audits compliance evidence packages. Validates gate enforcement. |

## 11. Related Documents

| Document | Relationship |
|----------|-------------|
| PetSure Australia Responsible AI Principles (GOV-AI-002) | Subordinate — defines the fairness and ethics principles this policy mandates |
| PetSure Australia Model Risk Management Framework (GOV-AI-003) | Subordinate — extends model governance requirements for AI/ML models |
| PetSure Australia Data Governance Standard (GOV-AI-004) | Subordinate — defines data quality and privacy requirements for AI data |
| PetSure Australia AI Solution Registration Standard (GOV-AI-005) | Subordinate — details the solution manifest schema and registration process |
| PetSure Australia AI Testing & Evaluation Framework (GOV-AI-006) | Subordinate — details evaluation metrics, thresholds, and golden dataset requirements |
| PetSure Australia Prompt Governance Guideline (GOV-AI-007) | Subordinate — details prompt version control and approval workflows |
| APRA CPS 230 — Operational Risk Management | Regulatory — this policy implements CPS 230 requirements for AI operational risk |
| APRA CPS 234 — Information Security | Regulatory — this policy implements CPS 234 requirements for AI information security |
| DISR Voluntary AI Safety Standard | Regulatory — this policy aligns to the 10 voluntary guardrails |

## 12. Review and Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 1 January 2025 | Group Risk | Initial release |
| 2.0 | 1 April 2025 | Group Risk | Added risk tier system, compliance gates, guardrail requirements |
| 2.1 | 1 July 2025 | Group Risk | Aligned to APRA CPS 230 effective date. Added incident response section. Updated gate exception process. |
