# Australia's Voluntary AI Safety Standard — PetSure Australia Platform Alignment Guide

**Document ID:** REG-AI-003
**Version:** 1.1
**Status:** Active
**Effective Date:** September 2024 (DISR standard); PetSure Australia alignment guide effective 1 January 2025
**Next Review Date:** 1 January 2026
**Owner:** Department of Industry, Science and Resources (interpreted by Risk Management AI)
**Approval Authority:** Group Chief Risk Officer
**Classification:** Internal — Restricted

---

## 1. Purpose

This document maps the Australian Government's Voluntary AI Safety Standard to PetSure Australia's AI governance platform. The Voluntary AI Safety Standard was published by the Department of Industry, Science and Resources (DISR) in September 2024 and establishes 10 guardrails for the safe and responsible use of AI in Australia.

While the standard is voluntary, PetSure Australia has made the strategic decision to treat compliance as mandatory for all production AI solutions. This decision reflects three considerations:

1. **Regulatory trajectory**: The Australian Government has signalled that mandatory AI regulation is forthcoming. The voluntary standard is widely understood as the precursor to binding legislation. By complying now, PetSure Australia avoids a disruptive retrospective compliance programme.
2. **Prudential expectation**: APRA has indicated through supervisory engagement that it expects regulated entities to demonstrate alignment with industry AI safety standards, even where those standards are not legally binding. Non-compliance may be raised in supervisory reviews.
3. **Reputational risk**: As one of Australia's largest financial institutions, PetSure Australia is held to a higher standard by customers, regulators, and the public. Demonstrating voluntary compliance signals maturity and builds trust.

This guide provides, for each of the 10 DISR guardrails: the requirement, PetSure Australia's platform implementation, the mapped AI-GOV control, and any identified gaps.

## 2. Scope

This alignment guide applies to:

- All AI solutions registered on the PetSure Australia AI governance platform at production_internal and production_customer_facing risk tiers.
- Experimental solutions are encouraged but not required to align with the voluntary standard.
- Third-party AI solutions procured by PetSure Australia, where PetSure Australia should seek evidence of the vendor's alignment with the standard.

## 3. Definitions

| Term | Definition |
|------|-----------|
| **DISR** | Department of Industry, Science and Resources — the Australian Government department responsible for AI policy. |
| **Voluntary AI Safety Standard** | A set of 10 guardrails published by DISR in September 2024 that provide a framework for the safe and responsible deployment of AI systems in Australia. Not currently legally binding. |
| **Guardrail (DISR context)** | One of the 10 high-level principles in the voluntary standard. Distinct from the platform's technical guardrails (e.g., prompt injection detection), though the platform's technical guardrails help implement DISR guardrails. |
| **Conformity Assessment** | The process of evaluating whether an AI system meets the requirements of a standard. DISR Guardrail 10 requires organisations to conduct conformity assessments. |

## 4. The 10 DISR Guardrails — Platform Alignment

### Guardrail 1: Establish Organisational Accountability

**DISR Requirement:** Organisations deploying AI systems should have clear governance structures, defined roles and responsibilities, and accountability for AI outcomes at the appropriate senior level.

**PetSure Australia Platform Implementation:**

- The PetSure Australia Group AI Policy (GOV-AI-001) establishes a governance hierarchy from the Board Risk Committee through the Group Chief Risk Officer to the Team Lead and individual Solution Owners.
- Every AI solution must have a named owner documented in the solution manifest. The Registration gate (AI-GOV-001) blocks deployment if no owner is specified.
- The Team Lead is accountable for the AI governance platform itself. Solution Owners are accountable for their solution's behaviour.
- The AI Ethics Board provides independent oversight for fairness and ethical considerations on customer-facing solutions.

**AI-GOV Control:** AI-GOV-001 (Registration)

**Gap Assessment:** No gap. PetSure Australia's governance structure fully satisfies this guardrail. Accountability is enforced at registration and cannot be bypassed.

---

### Guardrail 2: Manage AI Risks

**DISR Requirement:** Organisations should identify, assess, and manage AI risks throughout the AI system lifecycle, proportionate to the level of risk.

**PetSure Australia Platform Implementation:**

- The three-tier risk classification system (experimental, production_internal, production_customer_facing) provides proportionate governance. Higher tiers require stricter controls, more frequent evaluation, and additional oversight.
- Risk identification occurs during solution intake, where the Governance Portal team reviews the solution's audience, data sensitivity, decision impact, reversibility, and regulatory exposure.
- Ongoing risk management is automated through the platform's eight compliance gates, which run at defined cadences (30 days for customer-facing, 90 days for internal).
- The solution manifest documents identified risks and mitigations. Risk tier escalation is triggered automatically when scope changes.

**AI-GOV Control:** AI-GOV-001 (Registration), AI-GOV-003 (Evaluation Harness)

**Gap Assessment:** No gap. The platform's risk tier system directly implements proportionate risk management. The compliance gate cadence ensures risks are reassessed regularly.

---

### Guardrail 3: Protect AI Systems and Data

**DISR Requirement:** Organisations should protect AI systems and their data from cybersecurity threats, misuse, and unauthorised access.

**PetSure Australia Platform Implementation:**

- CPS 234 interpretation (REG-AI-002) provides comprehensive AI security controls including information asset classification, threat taxonomy, and mandatory security controls by risk tier.
- The platform enforces prompt injection detection, input validation, output filtering, and PII detection as mandatory guardrails.
- The PII Validation gate (AI-GOV-005) blocks deployment if PII is detected in any golden dataset response.
- Interaction logs and trace data are encrypted. Access to the platform is controlled through role-based access with audit logging.
- System prompts are classified as Confidential and stored encrypted at rest for production solutions.

**AI-GOV Control:** AI-GOV-005 (PII Validation), AI-GOV-006 (Guardrail Validation)

**Gap Assessment:** No gap. PetSure Australia's CPS 234 compliance framework, combined with the platform's automated security controls, provides comprehensive protection.

---

### Guardrail 4: Ensure AI Systems Are Tested and Fit for Purpose

**DISR Requirement:** Organisations should test AI systems to confirm they are fit for purpose, work as intended, and do not pose unacceptable risks before and during deployment.

**PetSure Australia Platform Implementation:**

- The golden dataset framework provides structured, human-reviewed test cases covering expected scenarios, edge cases, and adversarial inputs.
- The Evaluation Harness gate (AI-GOV-003) runs all golden dataset test cases against configured metrics and blocks deployment if any metric falls below threshold.
- Re-evaluation runs at defined cadences to detect drift: every 30 days for customer-facing, every 90 days for internal.
- Red-teaming is required quarterly for customer-facing solutions, testing for prompt injection, jailbreaking, data exfiltration, and output manipulation.
- Golden Dataset Sign-off gate (AI-GOV-009) requires independent human review and approval of the test suite before deployment.

**AI-GOV Control:** AI-GOV-003 (Evaluation Harness), AI-GOV-006 (Guardrail Validation), AI-GOV-009 (Golden Dataset Sign-off)

**Gap Assessment:** No gap. The platform's evaluation framework is comprehensive and exceeds DISR's testing requirements.

---

### Guardrail 5: Enable Human Oversight of AI Systems

**DISR Requirement:** Organisations should enable meaningful human oversight of AI systems, with the ability to intervene or override AI decisions where appropriate.

**PetSure Australia Platform Implementation:**

- The platform provides emergency kill switches to disable any AI solution immediately. This capability is available to the Solution Owner and Team Lead.
- For customer-facing solutions, the platform supports human-in-the-loop configurations where AI outputs are reviewed by a human before delivery.
- Guardrail confidence thresholds cause the AI to decline to answer and escalate to a human agent when confidence is low.
- The compliance dashboard provides real-time visibility into all active AI solutions, their compliance status, and guardrail alert rates, enabling proactive human oversight.
- Re-evaluation alerts notify Solution Owners when quality metrics decline, triggering human investigation.

**AI-GOV Control:** AI-GOV-008 (Audit Trail)

**Gap Assessment:** Minor gap. The platform supports human oversight through monitoring, alerting, and kill switches, but does not enforce mandatory human-in-the-loop review for all customer-facing decisions. This is by design — some customer-facing use cases (e.g., FAQ retrieval) do not warrant full human review of every response. However, the platform should provide clearer guidance on which use cases require mandatory human review versus monitoring-based oversight. **Remediation planned for Q3 2025.**

---

### Guardrail 6: Be Transparent About the Use of AI

**DISR Requirement:** Organisations should inform people when they are interacting with an AI system and be transparent about how the AI system works, its limitations, and how decisions are made.

**PetSure Australia Platform Implementation:**

- The PetSure Australia Group AI Policy requires that customer-facing AI solutions clearly disclose their AI nature. Users must know they are interacting with an AI system, not a human.
- RAG solutions are required to provide citations to source documents, enabling users to verify the AI's reasoning.
- The solution manifest documents the solution's intended scope, limitations, and known failure modes. This information must be reflected in user-facing disclosures.
- Explainability requirements scale with risk tier: citation coverage for Q&A agents, feature importance for scoring models, decision traces for agentic workflows.

**AI-GOV Control:** AI-GOV-001 (Registration), AI-GOV-003 (Evaluation Harness — citation coverage metric)

**Gap Assessment:** Minor gap. The platform tracks citation coverage and scope containment, but does not currently enforce specific user-facing disclosure language or verify that the disclosure is presented prominently. Teams are responsible for implementing appropriate disclosures, but there is no automated check. **Remediation under consideration — disclosure template library planned for Q4 2025.**

---

### Guardrail 7: Respect the Right to Contest AI Decisions

**DISR Requirement:** Organisations should provide mechanisms for individuals to contest AI-assisted decisions and have them reviewed by a human.

**PetSure Australia Platform Implementation:**

- PetSure Australia's existing complaints and disputes framework applies to AI-assisted decisions. Customers can contest any decision through established channels.
- The audit trail (AI-GOV-008) ensures that every AI interaction can be reconstructed after the fact, providing the evidence base for reviewing contested decisions.
- Trace data captures the full chain of reasoning (retrieval, guardrail checks, model reasoning, tool calls) so that a human reviewer can understand exactly how the AI reached its output.
- For credit decisions and other regulated outcomes, existing regulatory frameworks (responsible lending, hardship provisions) already provide contestability mechanisms.

**AI-GOV Control:** AI-GOV-008 (Audit Trail)

**Gap Assessment:** Minor gap. The platform provides the technical infrastructure for contestability (audit trail, trace reconstruction) but does not enforce that customer-facing solutions implement an explicit AI-decision contestability process. This relies on the existing complaints framework, which may not be specifically adapted for AI decision challenges. **Remediation: AI-specific contestability process guidance to be developed in partnership with Customer Advocacy, planned for Q3 2025.**

---

### Guardrail 8: Ensure Appropriate Record Keeping

**DISR Requirement:** Organisations should maintain adequate records of AI systems and their outcomes to support accountability, auditability, and continuous improvement.

**PetSure Australia Platform Implementation:**

- The Audit Trail gate (AI-GOV-008) requires 100% trace coverage for production solutions. Every AI interaction is logged with full context: user input, retrieved documents, guardrail results, model output, latency, and token usage.
- Compliance evidence packages are generated automatically by the platform and include gate results, guardrail test outcomes, evaluation metrics, and audit trail exports.
- Evidence packages are exportable in structured format for internal audit, regulatory review, and APRA examination.
- Solution manifests, golden datasets, and system prompts are version-controlled. The Prompt Governance gate (AI-GOV-010) requires approval commit hashes linking prompt changes to reviewed versions.
- Record retention follows PetSure Australia's existing data retention policy (minimum 7 years for regulatory records).

**AI-GOV Control:** AI-GOV-008 (Audit Trail), AI-GOV-009 (Golden Dataset Sign-off), AI-GOV-010 (Prompt Governance)

**Gap Assessment:** No gap. The platform's automated evidence generation and 100% trace coverage exceed DISR's record keeping requirements. This is one of the platform's strongest compliance areas.

---

### Guardrail 9: Ensure AI Systems Are Fair and Do Not Create or Exacerbate Unjust Discrimination

**DISR Requirement:** Organisations should identify and mitigate risks of AI systems producing unfair or discriminatory outcomes, particularly for vulnerable or disadvantaged groups.

**PetSure Australia Platform Implementation:**

- The Bias & Toxicity gate (AI-GOV-007) tests all production solutions for bias and toxicity. Thresholds are stricter for customer-facing solutions (bias <= 0.05, toxicity <= 0.05) than internal solutions (bias <= 0.10, toxicity <= 0.10).
- The PetSure Australia Group AI Policy requires that the definition of fairness be documented for each solution, recognising that fairness means different things in different contexts.
- The AI Ethics Board reviews bias testing results for customer-facing solutions and provides independent oversight.
- Golden datasets must include test cases specifically designed to probe for demographic bias, covering protected characteristics under Australian anti-discrimination law.
- For scoring models, discrimination testing includes demographic parity, equalised odds, and other statistical fairness measures.

**AI-GOV Control:** AI-GOV-007 (Bias & Toxicity)

**Gap Assessment:** No gap. The platform's bias testing framework, combined with the AI Ethics Board's oversight, satisfies this guardrail. The documented-fairness-definition requirement ensures that fairness is contextualised rather than applied as a generic metric.

---

### Guardrail 10: Assess AI Systems Against This Standard

**DISR Requirement:** Organisations should regularly assess their AI systems against this standard and maintain a process for continuous improvement.

**PetSure Australia Platform Implementation:**

- This document itself constitutes PetSure Australia's initial conformity assessment against the voluntary standard.
- The compliance gate runner automates assessment against AI-GOV controls, which are mapped to DISR guardrails throughout this document.
- Re-evaluation cadences (30 days for customer-facing, 90 days for internal) ensure ongoing assessment rather than point-in-time compliance.
- The compliance dashboard provides real-time visibility into the compliance posture of all registered solutions, enabling continuous monitoring.
- This alignment guide is reviewed annually and updated when the platform evolves or DISR updates the standard.

**AI-GOV Control:** All AI-GOV controls (AI-GOV-001 through AI-GOV-010)

**Gap Assessment:** No gap. The platform's automated compliance framework provides continuous assessment that exceeds the periodic review DISR contemplates.

## 5. Summary — DISR Guardrail to AI-GOV Control Mapping

| DISR Guardrail | AI-GOV Control(s) | Compliance Status | Notes |
|----------------|-------------------|-------------------|-------|
| 1. Organisational Accountability | AI-GOV-001 | Fully aligned | Named ownership enforced at registration |
| 2. Risk Management | AI-GOV-001, AI-GOV-003 | Fully aligned | Three-tier risk system with proportionate governance |
| 3. Data Protection | AI-GOV-005, AI-GOV-006 | Fully aligned | PII detection, encryption, access controls |
| 4. Testing | AI-GOV-003, AI-GOV-006, AI-GOV-009 | Fully aligned | Golden dataset framework with independent sign-off |
| 5. Human Oversight | AI-GOV-008 | Partially aligned | Kill switches and monitoring in place; human-in-the-loop guidance needed |
| 6. Transparency | AI-GOV-001, AI-GOV-003 | Partially aligned | Citation coverage tracked; disclosure enforcement gap |
| 7. Contestability | AI-GOV-008 | Partially aligned | Audit trail supports review; AI-specific contestability process needed |
| 8. Record Keeping | AI-GOV-008, AI-GOV-009, AI-GOV-010 | Fully aligned | 100% trace coverage, automated evidence generation |
| 9. Fairness | AI-GOV-007 | Fully aligned | Bias testing with contextualised fairness definitions |
| 10. Conformity Assessment | All | Fully aligned | Automated continuous assessment via compliance gates |

## 6. Gap Remediation Plan

| Gap | DISR Guardrail | Remediation | Target Date | Owner |
|-----|---------------|-------------|-------------|-------|
| Human-in-the-loop guidance for customer-facing solutions | Guardrail 5 | Develop decision framework for when mandatory human review is required vs. monitoring-based oversight | Q3 2025 | Team Lead |
| Disclosure enforcement for AI-powered interfaces | Guardrail 6 | Create disclosure template library and automated check for customer-facing solutions | Q4 2025 | Team Lead + Design |
| AI-specific contestability process | Guardrail 7 | Develop AI decision contestability guidance integrated with existing complaints framework | Q3 2025 | Team Lead + Customer Advocacy |

All gaps are classified as low severity. The platform provides the technical infrastructure to support these guardrails; the gaps relate to process guidance and policy documentation rather than technical capability. Remediation is planned and tracked.

## 7. Voluntary vs. Mandatory — Strategic Position

### 7.1 Current Regulatory Status

The Voluntary AI Safety Standard is not legally binding. There is no penalty for non-compliance and no formal enforcement mechanism. Organisations are encouraged but not required to adopt the 10 guardrails.

### 7.2 Anticipated Regulatory Trajectory

The Australian Government has signalled its intent to move toward mandatory AI regulation. Key indicators:

- The DISR consultation paper (January 2024) explicitly discussed mandatory obligations.
- The voluntary standard is framed as an interim measure while mandatory frameworks are developed.
- International peers (EU AI Act, Canada's AIDA) are moving toward binding regulation, creating pressure for Australia to follow.
- APRA has indicated through supervisory engagement that alignment with industry standards is expected, effectively making voluntary standards quasi-mandatory for regulated entities.

### 7.3 PetSure Australia's Position

PetSure Australia treats the voluntary standard as mandatory for all production AI solutions. This decision was approved by the Group Chief Risk Officer and is documented in the PetSure Australia Group AI Policy. The rationale:

1. **Compliance readiness**: When the standard becomes mandatory, PetSure Australia will already be compliant. This avoids a disruptive and costly retrospective compliance programme.
2. **Regulatory relationship**: Demonstrating voluntary compliance builds credibility with APRA and DISR. It positions PetSure Australia as a responsible leader in AI governance.
3. **Customer trust**: Customers increasingly expect transparency and accountability in AI. Voluntary compliance supports PetSure Australia's brand commitment to responsible banking.
4. **Risk management**: The 10 guardrails represent genuine good practice. Compliance reduces the risk of AI incidents regardless of regulatory status.

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| PetSure Australia Group AI Policy (GOV-AI-001) | Parent — the Group AI Policy mandates alignment with this standard |
| APRA CPS 230 — Operational Risk Management (REG-AI-001) | Related — CPS 230 risk management requirements align with Guardrail 2 |
| APRA CPS 234 — Information Security (REG-AI-002) | Related — CPS 234 security requirements align with Guardrail 3 |
| PetSure Australia Responsible AI Principles (GOV-AI-002) | Sibling — ethical principles inform Guardrails 1, 5, 6, 7, and 9 |
| PetSure Australia AI Testing & Evaluation Framework (GOV-AI-006) | Subordinate — details testing requirements for Guardrail 4 |
| DISR Voluntary AI Safety Standard (original document) | Source — this guide interprets and maps the original standard |
| DISR Safe and Responsible AI in Australia consultation paper (January 2024) | Context — provides background on Australia's regulatory trajectory |

## 9. Review and Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 1 January 2025 | Risk Management AI | Initial alignment guide mapping DISR guardrails to AI governance platform |
| 1.1 | 1 April 2025 | Risk Management AI | Updated gap analysis following Q1 platform enhancements. Added gap remediation plan with target dates. Updated regulatory trajectory section. |
