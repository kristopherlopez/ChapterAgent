# APRA CPS 230 — Operational Risk Management (AI Governance Interpretation)

**Document ID:** REG-AI-001
**Version:** 1.2
**Status:** Active
**Effective Date:** 1 July 2025
**Next Review Date:** 1 July 2026
**Owner:** APRA (interpreted by Group Risk)
**Approval Authority:** Group Chief Risk Officer
**Classification:** Internal — Restricted

---

## 1. Purpose

This document provides PetSure Australia's interpretation of APRA Prudential Standard CPS 230 (Operational Risk Management) as it applies to artificial intelligence systems. It is not a reproduction of CPS 230 itself, but an internal mapping that translates CPS 230 obligations into concrete requirements for AI governance within the PetSure Australia Group.

CPS 230 came into effect on 1 July 2025 and fundamentally changed how APRA-regulated entities must manage operational risk. It replaced the previous CPS 231 (Outsourcing), CPS 232 (Business Continuity), and CPG 235 (Managing Data Risk) with a single, integrated standard that covers operational risk identification, control effectiveness, business continuity, and third-party risk management.

AI systems represent a new and material category of operational risk. Their outputs can be unpredictable, their failure modes are unlike traditional software, and their reliance on third-party large language model (LLM) providers creates vendor concentration risk that CPS 230 explicitly requires institutions to manage. This document ensures PetSure Australia's AI governance platform satisfies the operational risk requirements of CPS 230 in a demonstrable and auditable manner.

## 2. Scope

This interpretation applies to:

- All AI solutions registered on the PetSure Australia AI governance platform, regardless of risk tier.
- Third-party AI services procured or consumed by PetSure Australia business units, including LLM API providers, AI SaaS tools, and AI components embedded in vendor platforms.
- AI-related operational processes including model deployment, monitoring, incident response, and change management.

This interpretation does not replace PetSure Australia's broader CPS 230 compliance framework. It supplements the Group-wide operational risk management framework with AI-specific guidance and requirements.

## 3. Definitions

| Term | Definition |
|------|-----------|
| **Operational Risk** | The risk of loss resulting from inadequate or failed internal processes, people, and systems, or from external events. Under CPS 230, this includes legal risk but excludes strategic and reputational risk (though AI incidents frequently create reputational consequences). |
| **Material Service Provider** | A third party whose disruption could materially affect PetSure Australia's ability to meet its obligations. LLM providers powering customer-facing AI solutions are likely material service providers under CPS 230. |
| **Critical Operation** | A process, activity, or service that, if disrupted, would have a material adverse impact on PetSure Australia's depositors, policyholders, beneficiaries, or the financial system. AI systems that automate customer decisions may constitute critical operations. |
| **Tolerance Level** | The maximum acceptable level of disruption to a critical operation, expressed in terms of duration and impact. AI systems must have defined tolerance levels in their solution manifest. |
| **Control Effectiveness** | A measure of how well a control mitigates the risk it is designed to address. CPS 230 requires regular testing of control effectiveness — the platform's compliance gates serve this function for AI-specific controls. |

## 4. CPS 230 Requirements Relevant to AI Systems

### 4.1 Operational Risk Identification (CPS 230 Paragraphs 14-18)

CPS 230 requires institutions to identify and assess operational risks across all business activities. For AI systems, this means:

**AI-specific operational risks that must be identified and documented:**

| Risk Category | Description | AI-Specific Manifestation |
|---------------|-------------|---------------------------|
| **Output unpredictability** | AI systems can produce incorrect, misleading, or harmful outputs that are not deterministic | A Q&A agent fabricating policy information. A credit model producing unexplainable scores. |
| **Model drift** | AI model performance degrades over time as the relationship between inputs and outputs changes | An LLM provider updates their model, changing the behaviour of PetSure Australia solutions without PetSure Australia's direct control. |
| **Data quality** | Errors in training, reference, or input data propagate through AI systems in non-obvious ways | A RAG system retrieving outdated policy documents. Poisoned training data producing biased outputs. |
| **Prompt fragility** | Small changes to system prompts or user inputs can cause dramatic changes in AI behaviour | A guardrail-bypassing prompt injection. A system prompt edit that inadvertently removes safety constraints. |
| **Vendor dependency** | Reliance on external LLM providers for core AI capabilities creates single points of failure | OpenAI API outage rendering customer-facing Q&A agent unavailable. Anthropic changing API terms. |
| **Cascading failure** | Agentic AI workflows can propagate errors across multiple systems through tool calls and chain-of-thought reasoning | An agent making an incorrect tool call that triggers a downstream system action. |

PetSure Australia's AI governance platform addresses this requirement through mandatory solution registration (AI-GOV-001), which requires every solution to document its risk profile, dependencies, and potential failure modes in the solution manifest.

### 4.2 Control Effectiveness (CPS 230 Paragraphs 19-25)

CPS 230 requires institutions to maintain effective controls for material operational risks and to test those controls regularly. For AI systems, the platform's compliance gates serve as the primary control testing mechanism.

**Control mapping:**

| CPS 230 Requirement | AI-GOV Control | Platform Implementation |
|----------------------|----------------|------------------------|
| Identify and document controls | AI-GOV-001 | Solution manifest documents all configured guardrails, evaluation metrics, and thresholds |
| Test control effectiveness regularly | AI-GOV-003 | Evaluation harness runs golden dataset against all metrics at configured cadence (30 or 90 days) |
| Maintain control assurance | AI-GOV-006 | Guardrail validation gate tests every configured guardrail against the golden dataset |
| Monitor controls on an ongoing basis | AI-GOV-008 | Audit trail records 100% of AI interactions with full trace data for production solutions |
| Escalate control failures | AI-GOV-001 to AI-GOV-010 | Any gate failure blocks deployment and generates an alert to the solution owner and Team Lead |

Control testing is not optional. The platform enforces testing through the compliance gate runner. Solutions that fail a gate cannot deploy — there is no manual override at the pipeline level. Gate exceptions require documented approval from the Team Lead and the relevant control owner (see PetSure Australia Group AI Policy, Section 6.3).

### 4.3 Incident Management (CPS 230 Paragraphs 36-41)

CPS 230 requires institutions to have processes to detect, manage, escalate, and report operational incidents. AI incidents have characteristics that make them different from traditional IT incidents:

- **Detection latency**: AI errors may not be immediately apparent. A subtly incorrect answer may be consumed and acted upon before anyone recognises it as wrong.
- **Blast radius uncertainty**: The impact of an AI error depends on who saw the output and what they did with it. This is harder to assess than a database outage.
- **Root cause complexity**: AI failures may stem from model behaviour, data quality, prompt design, or vendor changes — often a combination.

**AI incident detection mechanisms on the platform:**

1. **Guardrail alerts** — real-time detection of blocked or flagged outputs (injection attempts, PII leakage, scope violations).
2. **Evaluation drift** — periodic re-evaluation detects when solution quality drops below thresholds.
3. **Audit trail anomalies** — monitoring of trace data for unusual patterns (high refusal rates, sudden topic shifts, latency spikes).
4. **User reports** — structured feedback mechanism for internal users to flag incorrect or concerning AI outputs.

### 4.4 APRA Notification Requirements

CPS 230 requires notification to APRA of material operational incidents. The following AI incidents would likely trigger APRA notification:

| Incident Type | Notification Trigger | Timeframe |
|---------------|---------------------|-----------|
| Customer harm from AI output | AI output causes financial loss, privacy breach, or discriminatory outcome for customers | As soon as practicable, no later than 72 hours |
| Systemic AI failure | Multiple AI solutions fail simultaneously (e.g., due to shared LLM provider outage) | As soon as practicable, no later than 72 hours |
| AI security breach | Prompt injection or adversarial attack succeeds in extracting sensitive information | As soon as practicable, no later than 72 hours |
| Sustained quality degradation | Customer-facing AI solution operates below thresholds for more than 24 hours | Within 10 business days |

The Team Lead, in consultation with Group Risk and Legal, determines whether an AI incident meets the materiality threshold for APRA notification. When in doubt, the bias should be toward notification.

## 5. Third-Party Risk for LLM Providers

### 5.1 CPS 230 Third-Party Requirements (Paragraphs 46-58)

CPS 230 introduced comprehensive third-party risk management requirements, replacing the previous CPS 231. For AI governance, the most significant third-party relationships are with LLM providers.

**Current LLM provider landscape:**

| Provider | Models Used | PetSure Australia Solutions Dependent | Concentration Risk |
|----------|------------|------------------------|-------------------|
| OpenAI | GPT-4o, GPT-4.1 | Multiple production solutions | High — dominant provider for generative AI |
| Anthropic | Claude Sonnet 4, Claude Haiku | Growing adoption | Medium — secondary provider |
| Google | Gemini 2.5 Pro | Limited use | Low — minimal current dependency |

### 5.2 Vendor Concentration Risk

CPS 230 explicitly requires institutions to manage concentration risk in third-party arrangements. The global AI market is heavily concentrated among a small number of LLM providers, which creates systemic risk that PetSure Australia must actively manage.

**Mitigations required by PetSure Australia's interpretation:**

1. **Multi-provider capability**: All production AI solutions must be architecturally capable of switching between at least two LLM providers. The solution manifest must document primary and fallback providers.
2. **Provider monitoring**: The platform team maintains a quarterly assessment of each LLM provider's financial health, service reliability, compliance posture, and strategic direction.
3. **Contractual protections**: Agreements with LLM providers must include service level commitments, data handling requirements, change notification obligations, and exit provisions.
4. **No single-provider dependency for critical operations**: AI solutions that constitute critical operations under CPS 230 must not depend on a single LLM provider without a tested fallback.

### 5.3 Fourth-Party Risk

LLM providers themselves depend on infrastructure providers (primarily cloud hyperscalers). PetSure Australia must understand and document these fourth-party dependencies. A disruption to a major cloud provider could simultaneously affect multiple LLM providers and, consequently, multiple PetSure Australia AI solutions.

## 6. Business Continuity for AI Systems

### 6.1 Tolerance Levels

CPS 230 requires tolerance levels for critical operations. AI solutions that constitute or support critical operations must define:

| Parameter | Definition | Example |
|-----------|-----------|---------|
| **Maximum tolerable downtime** | How long the AI solution can be unavailable before material impact occurs | Customer-facing Q&A: 4 hours. Internal decisioning support: 24 hours. |
| **Recovery time objective** | Target time to restore the AI solution to normal operation | Must be less than maximum tolerable downtime. |
| **Graceful degradation mode** | What the system does when the AI component is unavailable | Show static FAQ content. Route to human agent. Display "service temporarily unavailable" with estimated restoration. |
| **Fallback procedure** | Manual or alternative automated process to replace the AI function | Human review of applications. Manual policy lookup. Deterministic rule-based fallback. |

### 6.2 Business Continuity Testing

AI business continuity arrangements must be tested at least annually for production solutions. Testing must include:

- **Provider failover**: Switch from primary to fallback LLM provider and verify acceptable performance.
- **Graceful degradation**: Simulate provider outage and verify the solution degrades gracefully rather than failing completely.
- **Recovery**: Verify the solution can recover to normal operation after an outage without data loss or residual errors.
- **Concurrent failure**: Simulate simultaneous failure of multiple AI solutions to test the institution's response capacity.

## 7. PetSure Australia Platform Alignment

The following table maps CPS 230 requirements to the platform's AI-GOV controls and demonstrates how the platform provides automated evidence of compliance.

| CPS 230 Requirement | Paragraph | AI-GOV Control | Platform Evidence |
|----------------------|-----------|----------------|-------------------|
| Identify operational risks | 14-18 | AI-GOV-001 | Solution manifest documents risk tier, dependencies, failure modes, and guardrail configuration |
| Maintain effective controls | 19-25 | AI-GOV-003, AI-GOV-006 | Evaluation harness and guardrail validation gates test control effectiveness at defined cadence |
| Test controls regularly | 26-30 | AI-GOV-006 | Compliance gate runner produces timestamped, structured evidence of all control tests |
| Manage incidents | 36-41 | AI-GOV-008 | Audit trail provides complete interaction logs for incident investigation and root cause analysis |
| Manage third-party risk | 46-58 | AI-GOV-001 | Solution manifest documents primary and fallback LLM providers; provider assessments recorded quarterly |
| Business continuity | 59-68 | AI-GOV-001 | Solution manifest documents tolerance levels, degradation modes, and fallback procedures |
| Board oversight | 8-13 | AI-GOV-001 | Risk tier classification and compliance dashboard provide board-level visibility into AI risk posture |

The platform automates compliance evidence generation for all eight gates. Evidence packages are exportable in structured format for audit and regulatory review. This automated evidence trail directly addresses CPS 230's requirement that institutions be able to demonstrate the effectiveness of their operational risk management framework.

## 8. Related Documents

| Document | Relationship |
|----------|-------------|
| PetSure Australia Group AI Policy (GOV-AI-001) | Parent — this interpretation supports the Group AI Policy's compliance obligations |
| PetSure Australia Responsible AI Principles (GOV-AI-002) | Sibling — ethical principles inform operational risk identification |
| PetSure Australia Model Risk Management Framework (GOV-AI-003) | Sibling — model risk is a subset of operational risk under CPS 230 |
| APRA CPS 234 — Information Security (REG-AI-002) | Related — information security risks are a subset of operational risks |
| DISR Voluntary AI Safety Standard (REG-AI-003) | Related — the voluntary standard's risk management guardrail aligns with CPS 230 |
| APRA CPG 230 — Operational Risk Management (Guidance) | Regulatory — APRA's guidance on CPS 230 implementation |
| PetSure Australia Business Continuity Management Framework | Related — AI business continuity integrates with the Group BCM framework |

## 9. Review and Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 1 March 2025 | Group Risk | Initial AI interpretation developed ahead of CPS 230 effective date |
| 1.1 | 1 June 2025 | Group Risk | Incorporated APRA feedback from pre-implementation review. Added fourth-party risk section. |
| 1.2 | 1 July 2025 | Group Risk | Aligned to CPS 230 effective date. Finalised tolerance level requirements. Updated LLM provider landscape. |
