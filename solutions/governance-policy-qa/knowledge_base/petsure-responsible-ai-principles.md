# PetSure Australia Responsible AI Principles

**Document ID:** GOV-AI-002
**Version:** 2.0
**Status:** Active
**Effective Date:** 1 April 2025
**Next Review Date:** 1 April 2026
**Owner:** Group AI Ethics Board
**Approval Authority:** Group AI Ethics Board
**Classification:** Internal — General

---

## 1. Purpose

This document defines the six Responsible AI Principles that govern the design, development, deployment, and operation of all AI systems across the PetSure Australia Group. These principles translate the values articulated in GOV-AI-001 Section 4 into practical requirements, platform enforcement mechanisms, and measurable outcomes.

Principles without enforcement are aspirational statements. This document goes beyond aspiration: for each principle, it defines what the principle means in practice, how the PetSure Australia AI governance platform enforces it, and how compliance is measured. The intent is to make responsible AI the path of least resistance, not an additional burden layered onto delivery teams.

This document is subordinate to the PetSure Australia Group AI Policy (GOV-AI-001) and is referenced by the PetSure Australia AI Testing & Evaluation Framework (GOV-AI-006), the PetSure Australia AI Solution Registration Standard (GOV-AI-005), and the PetSure Australia Prompt Governance Guideline (GOV-AI-007).

## 2. Scope

These principles apply to all AI solutions within the scope of GOV-AI-001, at all lifecycle stages and all risk tiers. While the intensity of enforcement varies by risk tier (proportionate governance, per GOV-AI-001 Section 4.1), the principles themselves are universal. An experimental prototype is not exempt from fairness or safety — it is simply held to a proportionate standard.

These principles also apply to the evaluation of third-party AI solutions procured by PetSure Australia. Vendors must demonstrate alignment with these principles as a condition of procurement.

## 3. Definitions

| Term | Definition |
|------|-----------|
| **Protected Attribute** | A characteristic that must not influence AI outputs in a discriminatory manner. Includes but is not limited to: age, gender, race, ethnicity, disability, sexual orientation, religion, marital status, and postcode (as a proxy for socio-economic status). |
| **Demographic Parity** | A fairness criterion requiring that the rate of a particular outcome (e.g., approval, classification, score band) is approximately equal across demographic groups. |
| **Equalised Odds** | A fairness criterion requiring that the true positive rate and false positive rate of a model are approximately equal across demographic groups. |
| **Output Consistency** | A fairness criterion for generative AI requiring that semantically equivalent inputs produce substantively equivalent outputs regardless of demographic references in the input. |
| **Explainability** | The degree to which an AI system's outputs can be understood and interpreted by its intended audience. Ranges from full model interpretability to post-hoc explanation of individual decisions. |
| **Human-in-the-Loop** | A design pattern where a human reviews and approves AI outputs before they are acted upon or delivered to end users. |
| **Human-on-the-Loop** | A design pattern where AI outputs are delivered directly but a human monitors aggregate performance and can intervene when anomalies are detected. |

## 4. The Six Principles

### 4.1 Fairness

#### Definition

AI systems must not produce systematically biased outputs that disadvantage individuals or groups based on protected attributes. Where differential treatment exists, it must be justified by legitimate, documented business reasons and must not serve as a proxy for discrimination.

#### What This Means in Practice

- Every AI solution must declare its fairness definition in the solution manifest. Fairness is context-dependent: what constitutes fair treatment in a credit scoring model differs from what constitutes fair treatment in a Q&A agent.
- Teams must consider fairness during design, not only during testing. Bias that is baked into training data or system prompts cannot be reliably detected by post-hoc testing alone.
- When a solution produces different outcomes for different groups, the team must be able to explain why and demonstrate that the differential is not attributable to protected attributes.

#### Fairness Definitions by Solution Type

| Solution Type | Primary Fairness Metric | Definition | Threshold (Internal) | Threshold (Customer-Facing) |
|---------------|------------------------|------------|---------------------|-----------------------------|
| **Scoring** | Demographic parity | Approval or score band rates must not differ across demographic groups by more than the threshold | Gap <= 0.10 | Gap <= 0.05 |
| **Scoring** | Equalised odds | True positive and false positive rates must not differ across demographic groups by more than the threshold | Gap <= 0.10 | Gap <= 0.05 |
| **Classification** | Output consistency | Given semantically equivalent inputs that differ only in demographic references, classification must be identical | Consistency >= 0.90 | Consistency >= 0.95 |
| **Q&A** | Output consistency | Given semantically equivalent queries that differ only in demographic references, response quality and completeness must be equivalent | Consistency >= 0.90 | Consistency >= 0.95 |
| **Validation** | Severity consistency | Validation findings and severity ratings must not differ based on demographic characteristics of the subject | Consistency >= 0.90 | Consistency >= 0.95 |
| **Conversational / Agentic** | Output consistency | Tone, helpfulness, and response quality must not vary based on inferred or stated demographic characteristics | Consistency >= 0.90 | Consistency >= 0.95 |

#### Platform Enforcement

- The DeepEval `bias` metric is mandatory for all solutions at `production_internal` tier and above. Thresholds: bias score <= 0.10 for internal, <= 0.05 for customer-facing (per GOV-AI-001 Section 7.1).
- Golden datasets must include bias-probing test cases (minimum 5 cases per GOV-AI-006 Section 4.3).
- The Bias & Toxicity compliance gate (AI-GOV-007) blocks deployment if bias thresholds are exceeded.

#### Measurement

Fairness is measured through:
1. **Bias metric scores** computed by the evaluation harness on every evaluation run
2. **Bias-probing test case results** examining differential treatment across demographic groups
3. **Production monitoring** of output distributions, flagging drift in demographic group outcomes (customer-facing solutions only)

### 4.2 Transparency

#### Definition

AI systems must be explainable to the degree required by their impact. Affected individuals must be able to understand that AI was involved in a decision, what role the AI played, and why the AI produced the output it did.

#### What This Means in Practice

- Customer-facing solutions must disclose AI involvement. Users must know they are interacting with or being assessed by an AI system.
- Q&A agents must provide citations for factual claims, traceable to specific source documents. This is measured by the `citation_coverage` metric.
- Scoring models must provide feature importance explanations (SHAP values or equivalent) for individual decisions.
- Classification solutions must provide the basis for each classification, at a minimum the top contributing factors.
- Agentic workflows must produce decision traces that allow after-the-fact reconstruction of the reasoning chain.

#### Platform Enforcement

- The `citation_coverage` metric is mandatory for Q&A solutions at production tier (>= 0.85 internal, >= 0.95 customer-facing, per GOV-AI-006).
- The Audit Trail compliance gate (AI-GOV-008) requires 100% trace coverage for production solutions, ensuring every AI interaction is reconstructable.
- Solution manifests must declare the explainability approach appropriate to the solution type.

#### Measurement

Transparency is measured through:
1. **Citation coverage scores** for Q&A and generative solutions
2. **Trace completeness** as verified by the Audit Trail gate
3. **Disclosure compliance** audited through periodic review of customer-facing interfaces

### 4.3 Accountability

#### Definition

Every AI system must have a named, accountable individual. Accountability cannot be delegated to the AI system itself. When an AI system produces a harmful, incorrect, or inappropriate output, a human is responsible.

#### What This Means in Practice

- Every solution manifest must include a named owner with a valid PetSure Australia email address. The platform does not accept solutions without an identified accountable individual (per GOV-AI-001 Section 4.5).
- The solution owner is responsible for the solution's compliance, including maintaining the golden dataset, responding to evaluation failures, and managing incidents.
- Accountability extends to third-party solutions: if PetSure Australia procures an AI system from a vendor, a PetSure Australia employee must still be the accountable owner.
- When a solution owner leaves the organisation or changes roles, ownership must be transferred within 10 business days.

#### Platform Enforcement

- The Registration gate (AI-GOV-001) validates the presence of a named owner in the solution manifest.
- The platform tracks ownership and flags solutions where the owner's PetSure Australia account becomes inactive.
- All compliance evidence, evaluation results, and incident records are attributed to the solution owner at the time of the event.

#### Measurement

Accountability is measured through:
1. **Registration completeness** — percentage of AI solutions with a valid, active owner
2. **Incident response times** — whether the accountable owner responds within the timeframes defined in GOV-AI-001 Section 9.1
3. **Ownership currency** — number of solutions with stale or inactive owners

### 4.4 Privacy

#### Definition

AI systems must not collect, store, process, or expose personal information beyond what is explicitly required and authorised for the solution's function. Privacy is not an afterthought; it must be designed into the solution from inception.

#### What This Means in Practice

- PII detection guardrails are mandatory for all solutions at production tier. Customer-facing solutions operate under a zero-tolerance policy: no PII may appear in AI outputs unless explicitly authorised and documented.
- Golden datasets must use synthetic or appropriately anonymised data. Real customer data is prohibited in test cases (per GOV-AI-001 Section 4.4).
- Training data and fine-tuning datasets must undergo PII review before use.
- Solutions that access customer data must declare data sources and PII exposure level in the solution manifest (`data.pii_exposure` field).
- Data retention for AI interaction logs must comply with PetSure Australia data retention policies and the Privacy Act 1988 (Cth).

#### Platform Enforcement

- The PII Validation compliance gate (AI-GOV-005) scans all golden dataset responses for PII and blocks deployment if any is detected.
- PII detection guardrails run in real-time on production solutions, flagging or blocking responses that contain detected PII.
- The solution manifest requires declaration of data sensitivity (`data.classification`) and PII exposure level, validated during registration per GOV-AI-005.

#### Measurement

Privacy is measured through:
1. **PII Validation gate results** — pass/fail on every evaluation run
2. **Real-time PII detection rates** — count of PII detections in production (target: zero for customer-facing)
3. **Data classification accuracy** — periodic audit of declared vs actual data sensitivity levels

### 4.5 Safety

#### Definition

AI systems must not produce outputs that could cause harm to individuals, the organisation, or the public. Safety encompasses physical safety, financial safety, reputational safety, and psychological safety.

#### What This Means in Practice

- Toxicity detection is mandatory for all solutions at production tier. Thresholds: toxicity score <= 0.10 for internal, <= 0.05 for customer-facing (per GOV-AI-001 Section 7.1).
- Solutions must implement scope containment guardrails that prevent the AI from operating outside its designated domain. A policy Q&A agent must refuse requests for medical advice, legal counsel, or financial planning, for example.
- Prompt injection detection is mandatory at all tiers, including experimental. Injection attacks can cause an AI system to bypass its safety controls.
- Customer-facing solutions must include appropriate disclaimers where outputs could be mistaken for professional advice (financial, legal, medical).
- The platform supports emergency kill switches that can take a solution out of production immediately if it is causing ongoing harm (per GOV-AI-001 Section 9.2).

#### Platform Enforcement

- The DeepEval `toxicity` metric is mandatory for production-tier solutions. The Bias & Toxicity compliance gate (AI-GOV-007) blocks deployment if thresholds are exceeded.
- Scope containment and prompt injection guardrails are mandatory at all tiers, enforced by the Guardrail Validation gate (AI-GOV-006).
- The `boundary_adherence` metric measures whether solutions correctly refuse out-of-scope requests (>= 0.90 internal, >= 0.95 customer-facing, per GOV-AI-006).

#### Measurement

Safety is measured through:
1. **Toxicity scores** computed by the evaluation harness
2. **Boundary adherence scores** measuring scope containment effectiveness
3. **Guardrail pass rates** across the golden dataset
4. **Production incident rates** classified by severity (per GOV-AI-001 Section 9.1)

### 4.6 Human Oversight

#### Definition

AI systems must operate under appropriate human oversight. The level of oversight must be proportionate to the risk and impact of the system's outputs. No AI system at PetSure Australia is fully autonomous — there is always a human in or on the loop.

#### What This Means in Practice

The required level of human oversight varies by risk tier and decision impact:

| Risk Tier | Oversight Model | Description |
|-----------|----------------|-------------|
| `experimental` | **Developer oversight** | The development team monitors outputs during experimentation. No formal oversight structure required. |
| `production_internal` | **Human-on-the-loop** | AI outputs are delivered to internal users directly, but aggregate quality is monitored. The solution owner reviews evaluation results and production metrics at least monthly. |
| `production_customer_facing` | **Human-in-the-loop or human-on-the-loop** | Determined by decision impact. High-impact decisions (credit, claims, complaints) require human-in-the-loop. Lower-impact interactions (general Q&A, navigation assistance) may use human-on-the-loop with robust monitoring. |

For customer-facing solutions, the oversight model must be documented in the solution manifest and reviewed during intake. The Governance Portal team assesses whether the proposed oversight model is appropriate for the solution's risk profile.

#### Escalation and Override

All customer-facing AI solutions must provide a mechanism for human escalation. Customers must be able to request that a human review an AI-assisted decision. This requirement is non-negotiable and applies regardless of the solution's risk tier assessment.

For automated decisioning (solutions that make or materially influence decisions about individual customers), the following additional requirements apply:

- Decisions must be logged with full trace data sufficient for after-the-fact human review
- A sample of automated decisions must be reviewed by a qualified human on a regular cadence (minimum monthly for customer-facing solutions)
- Customers must be informed that the decision involved AI and told how to request a human review
- Human reviewers must have the authority and the tooling to override AI decisions

#### Platform Enforcement

- The Audit Trail compliance gate (AI-GOV-008) ensures 100% trace coverage, enabling after-the-fact human review.
- The evaluation harness includes guardrail-specific test cases to verify that escalation and refusal mechanisms function correctly.
- Golden dataset sign-off (AI-GOV-009) requires a human reviewer, ensuring that at minimum the evaluation itself involves human judgement.

#### Measurement

Human oversight is measured through:
1. **Trace coverage** — 100% required for production solutions (verified by AI-GOV-008)
2. **Human review rates** — proportion of automated decisions reviewed by humans (target: 100% sample coverage on defined cadence)
3. **Escalation availability** — verified during intake and periodic review
4. **Override rates** — frequency of human overrides of AI decisions, tracked as a signal of AI quality

## 5. Bias Testing Requirements

### 5.1 When Bias Testing Is Required

Bias testing is mandatory for all AI solutions at `production_internal` tier and above, as mandated by GOV-AI-001 Section 5.2. The requirements are stricter for customer-facing solutions.

| Risk Tier | Bias Testing Requirement | Threshold |
|-----------|-------------------------|-----------|
| `experimental` | Not required (recommended) | N/A |
| `production_internal` | Required | Bias score <= 0.10, fairness gap <= 0.10 |
| `production_customer_facing` | Required at strictest thresholds | Bias score <= 0.05, fairness gap <= 0.05 |

### 5.2 Bias Testing Methodology

Bias testing is conducted through two complementary approaches:

**Approach 1: Metric-based evaluation.** The DeepEval `bias` metric is computed across the full golden dataset. This provides a solution-level bias score reflecting the overall tendency of the solution to produce biased outputs.

**Approach 2: Bias-probing test cases.** Dedicated test cases in the golden dataset probe for differential treatment. These cases use matched pairs: semantically equivalent inputs that differ only in demographic references. For example:

- "What is the claims process for a 25-year-old male?" vs "What is the claims process for a 65-year-old female?"
- "Assess the risk profile of a business in Mosman" vs "Assess the risk profile of a business in Mount Druitt"

The solution must produce substantively equivalent outputs for each pair. Material differences are flagged and investigated.

### 5.3 Protected Attributes for Testing

The following protected attributes must be considered in bias testing, where applicable to the solution:

| Attribute | Applicable Solution Types | Testing Approach |
|-----------|--------------------------|------------------|
| Age | All | Matched pairs with different age references |
| Gender | All | Matched pairs with different gender references |
| Ethnicity / Cultural background | All | Matched pairs with names or references associated with different ethnic groups |
| Location / Postcode | Scoring, Classification | Matched pairs with different postcodes (testing for socio-economic proxy discrimination) |
| Disability | Conversational, Q&A | Matched pairs referencing different ability levels |
| Marital status | Scoring | Matched pairs with different marital statuses |
| Religion | Conversational, Q&A | Matched pairs with different religious references |

## 6. Ethics Review Triggers

### 6.1 When Ethics Board Review Is Required

Certain AI solutions or changes require review by the Group AI Ethics Board before proceeding. The following triggers mandate Ethics Board review:

| Trigger | Description | Review Scope |
|---------|-------------|-------------|
| **Customer-facing automated decisioning** | Any solution that makes or materially influences decisions about individual customers without human-in-the-loop review of each decision | Full ethics review: fairness, transparency, human oversight, complaint mechanisms |
| **Sensitive use cases** | Solutions involving credit decisions, insurance underwriting, claims assessment, complaint handling, vulnerability detection, or collections | Full ethics review |
| **Novel AI capabilities** | First deployment of a new AI capability type within PetSure Australia (e.g., first agentic workflow, first voice AI) | Capability assessment: risks, safeguards, oversight model |
| **Bias threshold exceedance** | A production solution exceeds bias or fairness thresholds during evaluation | Targeted review: root cause, remediation plan, threshold adequacy |
| **Customer complaint** | A customer lodges a formal complaint alleging unfair or discriminatory treatment by an AI system | Targeted review: complaint investigation, systemic assessment |
| **Regulatory enquiry** | A regulator enquires about a specific AI solution or PetSure Australia's AI practices generally | Full review: compliance posture, documentation adequacy |
| **Significant scope expansion** | A registered solution materially expands its scope, audience, or decision authority | Re-assessment of original ethics review (if one existed) or new review |

### 6.2 Ethics Review Process

Ethics Board reviews follow a structured process:

1. **Referral** — The platform team, solution owner, or compliance function refers the matter to the Ethics Board with supporting documentation.
2. **Assessment** — The Ethics Board assesses the matter against the six principles in this document. The Board may request additional information, testing, or expert input.
3. **Determination** — The Board issues one of three determinations:
   - **Approved** — the solution may proceed as proposed
   - **Approved with conditions** — the solution may proceed subject to specified conditions (additional guardrails, monitoring, human oversight, etc.)
   - **Referred back** — the solution requires material changes before re-submission
4. **Documentation** — The determination, rationale, and any conditions are recorded and linked to the solution's compliance evidence package.

Ethics Board determinations are advisory to the Head of Risk Management AI, who makes the final governance decision. In practice, Ethics Board recommendations are followed in all but exceptional circumstances.

## 7. Complaint and Review Mechanisms

### 7.1 Customer Complaints About AI-Assisted Decisions

Customers who believe they have been unfairly treated by an AI-assisted decision have the right to:

1. **Be informed** that AI was involved in the decision
2. **Request an explanation** of how the AI contributed to the decision
3. **Request a human review** of the decision by a qualified person not involved in the original decision
4. **Lodge a complaint** through PetSure Australia's existing complaint resolution process, with the complaint flagged as AI-related for tracking and escalation

### 7.2 Internal Escalation

PetSure Australia staff who identify potential fairness, safety, or ethical concerns with an AI solution may escalate through:

- Their line management
- The Team Lead
- The AI Ethics Board directly (for concerns about systemic issues or concerns that have not been addressed through other channels)

Escalations are treated confidentially and without adverse consequence to the person raising the concern.

### 7.3 Tracking and Reporting

All AI-related complaints and escalations are tracked in the platform and reported to the AI Ethics Board quarterly. Trends in complaints inform:

- Updates to bias testing requirements and thresholds
- Identification of systemic issues across solutions
- Amendments to these principles or subordinate standards

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| PetSure Australia Group AI Policy (GOV-AI-001) | Parent — this document implements the principles defined in Section 4 of the Group policy |
| PetSure Australia Data Governance Standard (GOV-AI-004) | Peer — privacy requirements are jointly governed with the Data Governance Standard |
| PetSure Australia AI Solution Registration Standard (GOV-AI-005) | Peer — fairness definitions and ethics review outcomes are recorded in the solution manifest |
| PetSure Australia AI Testing & Evaluation Framework (GOV-AI-006) | Peer — bias testing methodology and thresholds are implemented through the evaluation harness |
| PetSure Australia Prompt Governance Guideline (GOV-AI-007) | Peer — prompt design must reflect these principles, particularly fairness and safety |
| Privacy Act 1988 (Cth) | Regulatory — privacy principle aligns to Australian privacy legislation |
| APRA CPS 230 — Operational Risk Management | Regulatory — accountability and safety principles support operational risk management obligations |
| DISR Voluntary AI Safety Standard | Regulatory — these principles align to the 10 voluntary guardrails published by the Department of Industry, Science and Resources |
| Anti-Discrimination Act 1977 (NSW) | Regulatory — fairness principle aligns to anti-discrimination obligations |

## 9. Review and Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 1 January 2025 | Group AI Ethics Board | Initial release with five principles (Fairness, Transparency, Accountability, Privacy, Safety) |
| 1.1 | 1 April 2025 | Group AI Ethics Board | Added Human Oversight as sixth principle. Added fairness definitions by solution type. Added ethics review triggers. Aligned to GOV-AI-001 v2.0. |
| 2.0 | 1 July 2025 | Group AI Ethics Board | Major revision: added platform enforcement mechanisms for each principle. Added bias testing methodology detail. Added complaint and review mechanisms section. Added protected attributes table. Aligned to GOV-AI-001 v2.1 and DISR Voluntary AI Safety Standard. |
