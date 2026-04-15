# AI Acceptable Use Standard

| Name | Policy Owner | Reviewed by | Review Date | Approved by | Approval Date |
|------|-------------|-------------|-------------|-------------|---------------|
| AI Acceptable Use Standard | Chief Insurance Officer | Chief Risk Officer | February 2026 | Chief Insurance Officer | February 2026 |

| | |
|---|---|
| **Policy adopted by** | PetSure Holdings Pty Ltd and PetSure (Australia) Pty Ltd |
| **Review Period** | 3 Yearly (unless otherwise required) |
| **Next Review Date** | February 2029 |

### Policy Revision Authority

| Chief Insurance Officer approval required for | Head of Artificial Intelligence approval required for |
|---|---|
| Material Changes to Policy | Non-Material Changes to Policy |

### Policy Context

| | |
|---|---|
| **Legislative/Prudential framework** | APRA Prudential Standard CPS230 Operational Risk Management |
| **Related policies** | Code of Conduct, Delegated Authorities Policy, Information Security, Privacy and Model Governance, Incident Management Policy. Guidelines set out in this document are applicable to all Charters, Frameworks and Policies. |

---

## About the Document

This AI Acceptable Use Standard applies to PetSure Holdings Pty Ltd (PetSure Holdings) and PetSure (Australia) Pty Ltd (PetSure) (collectively, "the Group" and/or "the Boards" as the context requires). PetSure Holdings is authorised by APRA as a Non-Operating Holding Company (NOHC) and is the parent entity of the Level 2 Insurance Group. PetSure is the APRA-authorised Level 1 general insurance entity. PetSure is wholly owned by PetSure Holdings.

This Standard sets the operational rules, tool access matrices, approval workflows, and reporting channels that govern the acceptable use of artificial intelligence across PetSure. It applies to all employees, contractors, and third parties who use or interact with AI tools and systems in the course of PetSure business.

### Relationship to Policy

This Standard implements the principles established in the Responsible Use of AI Policy and the AI Governance Policy. Those policies set out board-approved principles, governance structure, prohibited activities, and the accountability framework. This Standard translates those principles into specific, actionable requirements.

Where this Standard and a parent policy conflict, the parent policy takes precedence.

### Maintenance

This Standard is maintained on an annual review cycle by the Standard Owner (Chief Insurance Officer). Out-of-cycle updates may be made in response to material changes in regulatory requirements, AI tool availability, or risk profile.

## Definitions

| Term | Definition |
|------|-----------|
| **General Enquiries** | Questions or prompts that do not include company-sensitive or personal data. |
| **Sensitive Data** | Any information relating to internal strategies, financial data, operations, intellectual property, or confidential business information not publicly available. |
| **Personally Identifiable Information (PII)** | Any data that could identify an individual, including names, contact details, addresses, account numbers, or other unique identifiers. |
| **Access status** | Indicates whether the use of a tool or feature is permitted, prohibited, or requires conditional approval/oversight. |

### AI Solution Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **Custom ML Model** | Model trained or fine-tuned by PetSure on internal data | Fraud models, Sophia Jnr / GP model, Pricing support models |
| **Custom AI Application** | AI application built by the AI team using platforms/SDKs | LangStack agents, document processing agents |
| **Configured AI Solution** | AI solution built using vendor-provided builder tools within a licensed platform | Copilot Studio agents, custom GPTs, Claude Projects |
| **AI Productivity Tool** | Licensed AI tool used as-is for general productivity | ChatGPT, Claude, M365 Copilot (core chat) |
| **Embedded AI Feature** | AI capability within a non-AI platform, often activated without separate procurement | GitHub Copilot, Claude Code, Atlassian's Rovo |

## Approvals and Data Access

### Approval Process for New AI Applications

The full intake process (steps 1-5 below) applies to Custom ML Models, Custom AI Applications, and Configured AI Solutions (see AI Solution Categories). AI Productivity Tools are approved at the tool level via AI Tools Access (Section 6); individual use does not require separate intake unless the use case involves sensitive data or customer-facing deployment.

Embedded AI Features require identification and registration by the relevant department head; where an Embedded AI Feature processes PetSure data or is used in a business-critical workflow, it must be assessed via the standard intake process.

1. **Submit request:** Complete AI use case intake form via AI Use Case Repository
2. **Initial screening:** AI Governance Team screens against prohibited activities checklist
3. **Risk assessment:** Complete AI Risk Assessment per Initiative 5 methodology
4. **Approval:** Route to appropriate approver based on risk level:
   - Low risk: Team lead
   - Medium risk: Department head + AI Governance Team
5. **Registration:** Record in AI Use Case Repository with approval documentation

### Data Access Conditions

The following conditions apply to all AI solution categories where PetSure data is accessed by an AI system, whether through a custom data pipeline, a configured platform connection, or user-provided prompts containing sensitive data.

AI systems may access company data when:

- Data classification has been reviewed and approved for AI use
- Appropriate access controls are in place (per CPS 234 requirements)
- Data quality has been verified for the intended AI purpose (per CPG 235 requirements)
- Offshore data transfer requirements are met where applicable
- Personal or sensitive data access has been authorised by the relevant data owner

## Data Quality and Validation Procedures

This section defines the operational data quality and validation requirements that implement the data governance principles in the Responsible Use of AI Policy. Requirements for comprehensive data risk management are set out in the Data Risk Management Framework (aligned to APRA CPG 235).

The following table shows which subsections apply to each AI solution category:

| Subsection | Custom ML Model | Custom AI Application | Configured AI Solution | AI Productivity Tool | Embedded AI Feature |
|-----------|----------------|----------------------|----------------------|---------------------|-------------------|
| Data Quality Thresholds | Required | Required | Required (where data sources are connected) | N/A | N/A |
| Training and Input Data Validation | Required | Required | Required (where data sources are connected) | N/A | N/A |
| Data Lineage Documentation | Required | Required | Recommended | N/A | N/A |
| Data Validation Timing | Required | Required | Recommended | N/A | N/A |

### Data Quality Thresholds

- Each AI solution must have documented data quality thresholds appropriate to its use case and risk classification
- Thresholds must cover dimensions relevant to the solution, which may include accuracy, completeness, currency, consistency, and validity
- Quality thresholds must be reviewed when the AI solution's scope, risk classification, or data sources change

### Training and Input Data Validation

- Training data must be validated for accuracy, completeness, and currency before use in model development or retraining
- For AI applications that consume reference data (including knowledge bases, retrieval-augmented generation sources, and connected data repositories), input data must be validated for accuracy, completeness, and currency before deployment and at each scheduled review
- Validation must be documented, including the scope of checks performed, the data assessed, and the outcome
- Where validation identifies material deficiencies, the data must not be used until remediated

### Data Lineage Documentation

- Data lineage must be documented from source through to AI model input, consistent with APRA CPG 235 Clause 27
- Lineage documentation must include source systems, transformations applied, and any enrichment or aggregation steps
- Lineage records must be maintained and updated when data pipelines or sources change

### Data Validation Timing

- Data validation must occur as close to the point of capture as possible to minimise the propagation of quality issues
- Where validation at the point of capture is not feasible, compensating validation controls must be applied before the data is consumed by an AI system

## Prohibited and Restricted Uses

### Prohibited Uses

The following uses of AI are prohibited under all circumstances. These prohibitions supplement the prohibited activities defined in the Responsible Use of AI Policy and the AI Governance Policy:

| # | Prohibited Use |
|---|---------------|
| P1 | Entering customer PII into public AI tools (including public versions of Claude, ChatGPT, and Gemini) |
| P2 | Using AI tools that are classified as prohibited in the AI Tools Access Matrix (Section 6) |
| P3 | Using AI as the sole decision-maker for claims outcomes, underwriting decisions, or customer eligibility determinations |
| P4 | Using AI to circumvent compliance, regulatory, or internal control processes |
| P5 | Training or fine-tuning AI models on PetSure data without AI Governance Team authorisation |
| P6 | Using AI to generate or distribute misleading information about PetSure products, services, or coverage |
| P7 | Using AI to profile or score individual customers in ways that may result in unlawful discrimination |
| P8 | Sharing AI tool login credentials or using personal AI accounts for PetSure business purposes |
| P9 | Using AI to create synthetic customer records, fabricated evidence, or falsified documentation |
| P10 | Deploying AI models into production environments without completing the approval process |

### Restricted Uses

The following activities are not prohibited but require explicit approval before proceeding. Proceeding without the required approval is a policy violation.

| Restricted Use | Approval Required |
|---------------|------------------|
| Using AI for customer-facing communications | Communication review process + department head approval |
| Deploying AI models that inform or influence pricing, underwriting, or claims decisions | AI Governance Team + AI Steering Committee |
| Integrating new third-party AI services or APIs | IT/AI review and approval |
| Using AI with sensitive health information or detailed financial data | Data owner + AI Governance Team |
| Automated decision-making that affects customer eligibility or benefits | AI Governance Team + AI Steering Committee |
| AI applications that generate content published externally (website, marketing materials) | Marketing lead + communication review process |

## AI Tools Access

The following matrices outline permitted and prohibited uses of Generative AI tools depending on the type of enquiry and the sensitivity of data involved.

### AI Tools Access Matrix

Legend: Permitted | Prohibited | Conditional access

Note: PII is permitted only when using MS Copilot Chat and MS 365 Copilot, as these tools are organisation-approved and configured for secure handling of personal data.

For Generative AI tools that are not on this list, please contact the Head of Artificial Intelligence.

| Tool | General Enquiries | Company Sensitive Data | PII | Access Status |
|------|------------------|----------------------|-----|---------------|
| **Public AI Tools** | | | | |
| Claude (public) | Permitted | Prohibited | Prohibited | Permitted |
| ChatGPT (public) | Permitted | Prohibited | Prohibited | Permitted |
| Gemini (public) | Permitted | Prohibited | Prohibited | Permitted |
| DeepSeek | Prohibited | Prohibited | Prohibited | Prohibited |
| **Approved AI Tools** | | | | |
| Claude for Teams | Permitted | Permitted | Prohibited | Conditional |
| ChatGPT Team | Permitted | Permitted | Prohibited | Conditional |
| MS Copilot Chat | Permitted | Permitted | Permitted | Permitted |
| MS 365 Copilot | Permitted | Permitted | Permitted | Conditional |

### Approved AI Tool Features

| Tool / Feature | Approval Status | Notes |
|---------------|----------------|-------|
| **MS 365 Copilot** | | |
| Core Chat Functions & Research | Permitted | General use including PII handling as permitted. |
| Custom Assistants (Agent Builder) | Permitted | |
| Copilot Studio | Conditional | Approved for developer use only, with IT/AI team oversight. |
| Third-Party Integrations | Conditional | Require IT/AI review and approval before use. |
| **ChatGPT Team** | | |
| Core Chat Functions & Research | Permitted | General use excluding PII as indicated earlier. |
| Custom Assistants (GPTs & Projects) | Permitted | |
| Third-Party Integration | Conditional | Require IT/AI review and approval before use. |
| Codex & Agent Mode | Conditional | Require IT/AI review and approval before use. |
| Media Generation | Permitted | |
| **Claude for Teams** | | |
| Core Chat Functions & Research | Permitted | |
| Custom Assistants (Projects) | Permitted | |
| Third-Party Integrations | Conditional | Require IT/AI review and approval before use. |
| Claude Code | Conditional | Require IT/AI review and approval before use. |

## Customer-Facing AI Guardrails

This section establishes specific controls for the use of AI in customer-facing contexts. These guardrails are referenced from the AI Governance Policy (Section 11 — AI Incident Management) and apply in addition to the prohibited and restricted uses in Section 5. These guardrails apply to all AI solution categories when used in a customer-facing context.

### General Customer Communication Requirements

- AI-generated content must not be sent to customers without human review and approval by a person with authority to issue that type of communication
- All customer communications must use approved templates where templates exist for that communication type. AI must not be used to draft customer communications that bypass or modify approved templates
- Where AI is used to draft or assist with a customer communication, the person sending the communication remains fully accountable for its content, accuracy, and compliance with regulatory requirements
- AI-generated customer communications must be reviewed for accuracy, tone, regulatory compliance, and consistency with PetSure's brand and values before sending

### Customer Service Team Specific Controls

The Customer Service Team handles direct customer interactions and is subject to heightened controls due to the regulatory and conduct obligations attached to customer-facing communications:

- CST staff must not use AI to independently draft customer-facing emails, letters, or chat responses outside of approved templates and workflows
- Where AI-assisted response drafting is available through approved tools (e.g. agent assist), all AI-suggested responses must be reviewed and edited as needed by the CST staff member before sending
- CST staff must not copy AI-generated text directly into customer communications without review and appropriate modification
- AI tools that are not approved for customer-facing use must not be accessed from CST workstations or used in customer interaction workflows

These controls apply primarily to AI Productivity Tools and Configured AI Solutions used by CST staff.

### Claims and Complaints Specific Controls

AI use in claims and complaints communications is subject to additional controls due to specific compliance requirements under the Insurance Contracts Act, ASIC RG 271 (Internal Dispute Resolution), and General Insurance Code of Practice:

- AI must not be used to draft claims decisions, denial letters, or complaints outcomes without human review by a person with delegated authority for that decision type
- AI-generated summaries or analysis used to support a claims decision must be disclosed to the decision-maker as AI-generated
- Complaints correspondence must be prepared using approved templates. AI may be used to gather information or summarise case history, but the response itself must be prepared by the complaints handler using the approved process
- Any AI system involved in claims or complaints workflows must be registered in the AI System Register and assessed for materiality under the AI Governance Policy

These controls apply to all solution categories involved in claims or complaints workflows, including Custom ML Models used for claims decisioning and AI Productivity Tools used for case summarisation.

### Non-Approved Tools

- Employees in customer-facing roles must not use non-approved AI tools (including public AI assistants) for any task related to customer interactions, customer data, or customer communications
- Department heads are responsible for ensuring their teams are aware of which AI tools are approved for customer-facing use (see AI Tools Access)
- Attempts to access non-approved AI tools in customer-facing workflows should be reported to the AI Governance Team

## User Responsibilities

### Required Training

All users must complete:

- AI Awareness training (before first use of any AI system)
- Role-specific AI training (as applicable to job function)
- Annual refresher training
- High-Risk AI training (for users of high-risk AI applications)

### Documentation Obligations

Users must:

- Record use of AI assistance in high-impact business decisions
- Retain AI-generated content that informs material business decisions
- Report AI use in work products where required by department guidelines
- Maintain audit trails for AI-assisted customer decisions

### Issue Reporting

Users must report:

- Potential bias, discrimination, or errors in AI outputs
- Security concerns or potential data breaches
- Policy violations (own or observed)
- AI system malfunctions or availability issues

## Monitoring and Review

### Monitoring and Auditing

| Activity | Frequency | Responsible Party | Primary Categories |
|----------|-----------|------------------|-------------------|
| AI usage monitoring (systems) | Continuous | AI Team + IT Security | Custom ML Model, Custom AI Application |
| Policy compliance spot-checks | Quarterly | AI Governance Team | All |
| AI model performance reviews | Annually (minimum) | AI Team + Risk | Custom ML Model |
| Third-party AI service security assessments | At renewal + annually | IT Security + Procurement | AI Productivity Tool, Embedded AI Feature, Configured AI Solution |
| AI use case registry audit | Semi-annually | AI Governance Team | All |
| Training completion verification | Quarterly | AI Governance Team + HR | All |

### Review Cycles

- Standard review: Annual (or upon material regulatory change)
- Compliance verification: Quarterly spot-checks
- Framework alignment review: Annual (against NIST AI RMF, APRA standards)
- Risk appetite review: Annual (aligned with enterprise risk review)
- Incident trend analysis: Quarterly

## Reporting Channels

To report concerns, raise issues, or seek clarification:

| Channel | Contact | Use For |
|---------|---------|---------|
| AI Governance Team | ai-governance@petsure.com.au | Policy questions, intake process, compliance queries, potential violations |
| IT Security | IT Security incident reporting process / hotline | Security concerns, data breaches, technical security incidents |
| Line Manager | Direct report | First point of contact for potential violations, urgent issues |
| AI Team Lead | Immediate escalation | Urgent AI-related issues requiring rapid response |
| L&C Team | Legal & Compliance | Regulatory concerns, legal interpretation |
| PetSure Whistleblower Hotline | Anonymous reporting | Serious concerns requiring anonymous reporting |

## Appendix A: Regulatory References

| Regulation | AI Implications |
|-----------|----------------|
| **APRA CPS 234** | All AI systems are information assets requiring appropriate security controls and incident notification |
| **APRA CPG 235** | AI data inputs must meet data quality, lineage, and governance requirements |
| **Privacy Act (APPs)** | AI processing of personal information must comply with Australian Privacy Principles |
| **ASIC RG 271** | AI in financial advice or product recommendations must meet conduct obligations |
| **Anti-discrimination laws** | AI in underwriting and pricing must not result in unlawful discrimination |
| **Insurance Contracts Act** | AI-generated disclosures and communications must meet statutory requirements |
| **APRA CPS 230** | AI systems supporting critical operations must meet operational resilience requirements |
