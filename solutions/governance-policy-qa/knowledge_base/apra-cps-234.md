# APRA CPS 234 — Information Security (AI Governance Interpretation)

**Document ID:** REG-AI-002
**Version:** 2.0
**Status:** Active
**Effective Date:** 1 July 2019 (original standard); AI interpretation updated 1 April 2025
**Next Review Date:** 1 April 2026
**Owner:** APRA (interpreted by CISO Office)
**Approval Authority:** Chief Information Security Officer
**Classification:** Internal — Restricted

---

## 1. Purpose

This document provides PetSure Australia's interpretation of APRA Prudential Standard CPS 234 (Information Security) as it applies to artificial intelligence systems. CPS 234 has been in force since 1 July 2019, but the rapid adoption of generative AI and large language models since 2023 has created information security challenges that the original standard did not explicitly anticipate.

This interpretation extends PetSure Australia's existing CPS 234 compliance framework to cover AI-specific information assets, threat vectors, security controls, and incident reporting obligations. It ensures that AI solutions registered on the PetSure Australia AI governance platform are secured in a manner consistent with CPS 234 and proportionate to the sensitivity of the information they process.

AI systems introduce security risks that are fundamentally different from traditional software. They can be manipulated through natural language (prompt injection), they may inadvertently memorise and reproduce sensitive training data, and they process unstructured information in ways that make data classification and access control more complex. This interpretation addresses those risks.

## 2. Scope

This interpretation applies to:

- All AI solutions registered on the PetSure Australia AI governance platform, including solutions in development, testing, and production.
- All information assets associated with AI solutions: models, prompts, training data, fine-tuning data, reference corpora, evaluation datasets, interaction logs, and trace data.
- Third-party AI services and LLM providers that process PetSure Australia information.
- AI-related infrastructure including GPU compute, vector databases, embedding stores, and model serving endpoints.

This interpretation supplements PetSure Australia's Group Information Security Policy. Where this document is silent, the Group policy applies. Where this document specifies stricter requirements for AI assets, the stricter requirement prevails.

## 3. Definitions

| Term | Definition |
|------|-----------|
| **Information Asset** | Any data, system, or component that has value to PetSure Australia and requires protection. Under this interpretation, AI models, system prompts, golden datasets, and interaction logs are all information assets. |
| **Threat Vector** | A method or pathway by which a threat actor can gain unauthorised access to or disrupt an information asset. AI systems have unique threat vectors including prompt injection, data poisoning, and model extraction. |
| **Security Classification** | A label assigned to an information asset that determines the security controls required. Classifications follow PetSure Australia's four-tier scheme: Public, Internal, Confidential, Restricted. |
| **Red Team** | A group that simulates adversarial attacks against a system to identify vulnerabilities. AI red-teaming specifically tests for prompt injection, jailbreaking, data leakage, and harmful output generation. |
| **Prompt Injection** | An attack where a malicious user crafts inputs designed to override, alter, or bypass the AI system's intended behaviour, including its system prompt, guardrails, or safety constraints. |

## 4. Information Security Classification for AI Assets

### 4.1 Classification Requirements

CPS 234 Paragraph 15 requires institutions to classify information assets by sensitivity and criticality. AI systems contain several categories of information assets that require explicit classification.

| AI Asset | Default Classification | Rationale | Risk if Compromised |
|----------|----------------------|-----------|---------------------|
| **System prompts** | Confidential | Contain business logic, safety constraints, and behavioural instructions. Exposure enables targeted attacks. | Attacker crafts inputs that bypass guardrails. Business logic reverse-engineered by competitors. |
| **Golden datasets** | Confidential | Contain expected Q&A pairs that reveal business knowledge and evaluation criteria. | Attacker learns what the system is tested against and crafts evasions. Evaluation integrity compromised. |
| **Training / fine-tuning data** | Confidential to Restricted | May contain proprietary business knowledge or derived customer insights. | Intellectual property loss. Potential privacy breach if data contains residual PII. |
| **Reference corpora (RAG)** | Varies by content | Classification matches the highest classification of any document in the corpus. | Unauthorised access to source documents. Policy or regulatory information leaked externally. |
| **Interaction logs** | Confidential | Contain user queries and AI responses. May contain sensitive business context or inadvertently disclosed information. | Privacy breach. Intellectual property exposure. Regulatory non-compliance. |
| **Trace data** | Internal | Contains system-level execution data (tool calls, reasoning chains, latency metrics). | Reveals internal architecture. Enables targeted performance attacks. |
| **Model weights (fine-tuned)** | Restricted | Represent significant investment and encode proprietary knowledge. | Model extraction. Competitive advantage lost. |
| **Embedding vectors** | Confidential | Mathematical representations of source documents. Partial reconstruction of source content possible. | Source document content inferred. Reference corpus compromised. |

### 4.2 Classification Review

AI asset classifications must be reviewed when:

- The solution's risk tier changes (e.g., escalation from experimental to production_customer_facing).
- New data sources are added to the reference corpus.
- The solution's scope expands to cover new topics or audiences.
- A security incident reveals that the current classification is inadequate.

## 5. AI-Specific Security Threats

### 5.1 Threat Taxonomy

CPS 234 Paragraph 17 requires institutions to identify and assess information security threats. The following threat taxonomy is specific to AI systems and supplements PetSure Australia's general information security threat register.

| Threat | Description | Likelihood | Impact | Primary Targets |
|--------|-------------|------------|--------|-----------------|
| **Prompt injection (direct)** | User crafts input that instructs the AI to ignore its system prompt or safety constraints | High | High | System prompts, guardrails, output integrity |
| **Prompt injection (indirect)** | Malicious content embedded in retrieved documents or tool outputs manipulates AI behaviour | Medium | High | RAG corpora, tool integrations, agentic workflows |
| **Data poisoning** | Attacker corrupts training data, reference documents, or golden datasets to influence AI behaviour | Low | Critical | Training data, reference corpora, evaluation integrity |
| **Model extraction** | Attacker systematically queries the AI to reconstruct its behaviour, fine-tuning, or system prompt | Medium | Medium | Fine-tuned models, system prompts, business logic |
| **Data exfiltration via AI** | Attacker uses the AI as a channel to extract information the AI has access to but the user should not | Medium | High | Reference corpora, connected databases, internal systems |
| **Adversarial inputs** | Carefully crafted inputs that cause the AI to produce incorrect but plausible-seeming outputs | Medium | Medium | Output integrity, decision quality |
| **Denial of service** | Attacker floods the AI system with complex or malicious queries to exhaust resources or budgets | Medium | Medium | System availability, API cost budgets |
| **Training data memorisation** | AI model inadvertently memorises and reproduces specific training examples, potentially including sensitive data | Low | High | PII, proprietary information, confidential documents |

### 5.2 Threat Assessment Cadence

AI threat assessments must be conducted:

- At solution registration (during intake).
- At every risk tier change.
- Quarterly for production_customer_facing solutions.
- Annually for production_internal solutions.
- Immediately following a security incident or the publication of a new AI attack technique.

## 6. Security Controls for AI Systems

### 6.1 Mandatory Controls by Risk Tier

CPS 234 Paragraph 20 requires that security controls be commensurate with the size and extent of threats to information assets. The following controls are mandatory based on risk tier.

| Security Control | Experimental | Production Internal | Production Customer-Facing |
|------------------|-------------|--------------------|-----------------------------|
| Prompt injection detection guardrail | Required | Required | Required (strict mode) |
| Input validation and sanitisation | Recommended | Required | Required |
| Output filtering (PII, toxicity) | Recommended | Required | Required (zero tolerance for PII) |
| Rate limiting per user/session | Not required | Required | Required |
| Authentication and authorisation | Basic (SSO) | Role-based access | Role-based + MFA for admin |
| System prompt protection | Store in config | Encrypted at rest | Encrypted at rest + access audited |
| Interaction log encryption | Not required | Encrypted at rest | Encrypted at rest and in transit |
| Network segmentation | Shared dev environment | Dedicated namespace | Dedicated namespace + WAF |
| API key rotation | Manual | Automated quarterly | Automated monthly |
| Model access controls | Team-level | Team + approval | Individual + approval + audit |

### 6.2 Input Validation Controls

All AI solutions must implement input validation to detect and block malicious inputs before they reach the model. The platform provides built-in guardrails for:

1. **Prompt injection detection**: Pattern-based and ML-based detection of injection attempts. Must be active for all risk tiers. Customer-facing solutions must use strict mode (lower false negative tolerance).
2. **Input length limits**: Maximum input length configured per solution to prevent resource exhaustion.
3. **Character encoding validation**: Reject inputs with unusual Unicode characters commonly used in injection techniques (zero-width characters, homoglyph substitutions, right-to-left override characters).
4. **Topic boundary enforcement**: Scope containment guardrail restricts the AI to its configured domain, preventing users from repurposing the system.

### 6.3 Output Filtering Controls

AI outputs must be filtered before delivery to users:

1. **PII detection and redaction**: All outputs scanned for personal information. Customer-facing solutions must operate at zero tolerance — any detected PII blocks the response.
2. **Toxicity filtering**: Outputs scanned for harmful, offensive, or inappropriate content.
3. **Citation verification**: For RAG solutions, outputs must include citations to source documents. Unsupported claims are flagged.
4. **Confidence thresholds**: Solutions must be configured to decline to answer rather than provide low-confidence responses.

## 7. Security Testing Requirements

### 7.1 Testing Cadence

CPS 234 Paragraph 28 requires systematic testing of security controls. For AI systems, the testing programme must include:

| Test Type | Frequency | Applies To | Description |
|-----------|-----------|-----------|-------------|
| **Guardrail unit testing** | Every deployment | All tiers | Automated tests confirming each guardrail correctly detects and blocks known attack patterns |
| **Golden dataset evaluation** | Per cadence (30/90 days) | Production tiers | Full evaluation harness run including adversarial test cases |
| **Penetration testing** | Annually | Production tiers | Professional security assessment of the AI solution's attack surface |
| **AI red-teaming** | Quarterly | Customer-facing | Dedicated red team attempts prompt injection, data exfiltration, jailbreaking, and output manipulation |
| **Vulnerability scanning** | Continuous | All tiers | Automated scanning of AI infrastructure, dependencies, and API endpoints |
| **Third-party security review** | Annually | All using third-party LLMs | Security assessment of LLM provider's data handling, access controls, and incident response |

### 7.2 Red-Teaming Requirements

AI red-teaming is distinct from traditional penetration testing and requires specialised skills. Red-team exercises for AI systems must:

- Include prompt injection attempts (both direct and indirect).
- Attempt to extract the system prompt through conversational manipulation.
- Attempt to make the AI reveal information from its reference corpus that should be restricted.
- Test guardrail bypass techniques including multi-turn attacks, encoding tricks, and role-playing scenarios.
- Document all successful and unsuccessful attack vectors with full reproduction steps.
- Feed findings back into the golden dataset as adversarial test cases.

Red-team findings classified as Critical or High must be remediated before the next production deployment. Medium findings must be remediated within 30 days. Low findings are tracked and prioritised by the team.

## 8. Incident Notification to APRA

### 8.1 CPS 234 Notification Requirements

CPS 234 Paragraph 36 requires APRA notification of material information security incidents. An AI security incident must be reported to APRA if it meets any of the following criteria:

| Criterion | AI-Specific Example | Notification Timeframe |
|-----------|--------------------|-----------------------|
| Information security incident that materially affected or could have affected the entity | Successful prompt injection attack on customer-facing AI that extracted restricted data | Within 72 hours of becoming aware |
| Material information security control weakness | Discovery that prompt injection guardrail has been ineffective for an extended period | Within 10 business days |
| Material information security control weakness at a service provider | LLM provider suffers a data breach affecting PetSure Australia's interaction logs or prompts | Within 72 hours of becoming aware |

### 8.2 Notification Process

When an AI security incident occurs:

1. **Immediate containment**: Disable the affected AI solution if the incident is ongoing.
2. **Impact assessment**: Determine what information was compromised, how many users were affected, and whether customer data was involved. Use the audit trail to reconstruct the incident timeline.
3. **CISO notification**: Inform the CISO Office within 4 hours of confirmed AI security incidents.
4. **APRA notification**: The CISO Office determines whether APRA notification is required and prepares the notification within the required timeframe.
5. **Remediation**: Fix the vulnerability, update guardrails, add the attack vector to the golden dataset, and re-run all compliance gates before restoring the solution.

## 9. PetSure Australia Platform Alignment

The following table maps CPS 234 requirements to the platform's AI-GOV controls and demonstrates how the platform provides automated evidence of compliance.

| CPS 234 Requirement | Paragraph | AI-GOV Control | Platform Evidence |
|----------------------|-----------|----------------|-------------------|
| Classify information assets | 15 | AI-GOV-005 | Solution manifest documents all information assets and their classifications. PII validation gate confirms no unclassified personal data in outputs. |
| Maintain security controls commensurate with threats | 20-23 | AI-GOV-006 | Guardrail validation gate tests all security controls (injection detection, PII filtering, scope containment) against the golden dataset. |
| Test security control effectiveness | 28-30 | AI-GOV-006 | Compliance gate runner produces timestamped evidence of all security control tests. Red-team findings integrated into golden dataset. |
| Detect and respond to security incidents | 31-35 | AI-GOV-008 | Audit trail provides 100% interaction logging with real-time guardrail alerts for blocked attacks. Anomaly detection flags unusual patterns. |
| Notify APRA of material incidents | 36 | AI-GOV-008 | Incident reports generated from audit trail data with full timeline reconstruction for regulatory submission. |
| Manage service provider security | 37-40 | AI-GOV-010 | Change management gate ensures third-party provider changes are reviewed. Provider security assessments recorded and tracked. |
| Internal audit review | 41 | AI-GOV-008, AI-GOV-009 | Compliance evidence packages exportable for internal audit. Golden dataset sign-off provides independent review evidence. |

The platform's automated compliance evidence generation directly supports CPS 234's requirement that institutions be able to demonstrate the effectiveness of their information security framework to APRA. Evidence packages include timestamped gate results, guardrail test outcomes, and audit trail exports — all in structured format suitable for regulatory review.

## 10. Related Documents

| Document | Relationship |
|----------|-------------|
| PetSure Australia Group AI Policy (GOV-AI-001) | Parent — this interpretation supports the Group AI Policy's security obligations |
| PetSure Australia Group Information Security Policy | Parent — this interpretation supplements the Group-wide CPS 234 compliance framework |
| APRA CPS 230 — Operational Risk Management (REG-AI-001) | Related — operational risk and information security are complementary frameworks |
| DISR Voluntary AI Safety Standard (REG-AI-003) | Related — Guardrail 3 (data protection) and Guardrail 4 (testing) align with CPS 234 |
| PetSure Australia AI Testing & Evaluation Framework (GOV-AI-006) | Subordinate — details red-teaming methodology and adversarial test case requirements |
| PetSure Australia Data Governance Standard (GOV-AI-004) | Sibling — defines data classification requirements that inform AI asset classification |
| APRA CPG 234 — Information Security (Guidance) | Regulatory — APRA's non-binding guidance on CPS 234 implementation |
| OWASP Top 10 for LLM Applications | Reference — industry standard taxonomy of AI security risks |

## 11. Review and Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 1 July 2019 | CISO Office | Original CPS 234 compliance framework (not AI-specific) |
| 1.1 | 1 March 2023 | CISO Office | Added initial generative AI security considerations |
| 1.5 | 1 September 2024 | CISO Office | Major update for LLM-specific threats. Added prompt injection, data poisoning, model extraction. |
| 2.0 | 1 April 2025 | CISO Office | Full AI governance platform alignment. Mapped to AI-GOV controls. Added red-teaming requirements. Updated classification for AI assets. |
