# AI Governance Policy

| Name | Policy Owner | Reviewed by | Review Date | Approved by | Approval Date |
|------|-------------|-------------|-------------|-------------|---------------|
| AI Governance Policy | Chief Insurance Officer | Chief Risk Officer | February 2026 | Chief Insurance Officer | February 2026 |

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

This AI Governance (Policy) applies to PetSure Holdings Pty Ltd (PetSure Holdings) and PetSure (Australia) Pty Ltd (PetSure) (collectively, "the Group" and/or "the Boards" as the context requires). PetSure Holdings is authorised by APRA as a Non-Operating Holding Company (NOHC) and is the parent entity of the Level 2 Insurance Group. PetSure is the APRA-authorised Level 1 general insurance entity. PetSure is wholly owned by PetSure Holdings.

The use of AI systems across the Group's activities may result in the potential for adverse financial and non-financial impacts, where strategic and business decisions are based on incorrect, biased, or unreliable AI system outputs, results, and reports. AI system risk may arise from multiple sources throughout the lifecycle of an AI system — including hallucination, algorithmic bias, scope creep beyond intended use, autonomous action without appropriate human oversight, and degradation of system performance over time — rather than being limited to when the system is initially deployed. These risks can lead to financial loss, adverse customer outcomes, poor business and strategic decision-making, damage to PetSure's reputation, or regulatory fines.

The AI Governance Policy (AIGP) is a key element of the Group's Risk Management Framework (RMF). The AIGP sets out PetSure's definition of AI systems and the approach for managing AI system risk across the full system lifecycle — from development through deployment, monitoring, and retirement. This includes consideration of governance requirements, roles and responsibilities, and non-compliance in relation to this policy.

Where an AI system incorporates one or more models that fall within the scope of the Model Governance Policy (MGP), both the AIGP and the MGP apply concurrently. The MGP governs model-specific risk (data, validation, drift); the AIGP governs the full AI system lifecycle including governance, controls, and human oversight.

A copy of the AIGP is made available on the intranet and changes communicated to relevant stakeholders following policy updates.

## Scope

The Policy applies to all AI Systems and AI System Groups as defined below. The scope of this policy extends to AI systems that are developed or provided by external vendors (External AI Systems). It applies to all AI systems and must be considered when:

- A new AI system is created or procured
- An AI system undergoes re-development or change of scope
- An AI system is in use

The AIGP also applies to the use of general-purpose AI tools (such as generative AI assistants) by all employees, contractors, and third parties acting on behalf of PetSure. While the operational rules for day-to-day AI tool use are set out in the AI Acceptable Use Standard, this Policy establishes the governance framework, accountability structures, and oversight mechanisms under which all AI use operates.

## Definitions

| Term | Definition |
|------|-----------|
| **AI System** | A software system. Systems which perform only basic data retrieval, simple deterministic calculations, or static rules-based processing without learning, adaptation, or generative capability are not considered AI Systems for the purpose of this policy. |
| **AI System Group** | A group of AI systems which share common infrastructure, or are used in conjunction with each other to deliver a combined output (for example, a claims processing AI System Group might consist of a document extraction system, a fraud detection model, and a decision-support agent that together support end-to-end claims assessment). |
| **AI System Developer** | The person or group that developed the AI System. This can be an employee of PetSure or an external party. |
| **AI Owner** | The person accountable for the AI system's registration, governance, compliance with this policy, and ongoing performance. This is an employee of PetSure. |
| **Generative AI (GenAI)** | AI systems capable of creating new content — such as text, images, code, or audio — typically based on large pre-trained foundation models. GenAI systems are AI Systems for the purpose of this policy. |
| **AI Agent** | An AI system that can autonomously plan and execute multi-step tasks, use tools, and take actions on behalf of users or processes. AI agents are AI Systems for the purpose of this policy and are subject to additional controls commensurate with their level of autonomy. |
| **Machine Learning (ML) Model** | A quantitative model trained on data to make predictions, classifications, or recommendations. ML models that meet the definition of a Model under the Model Governance Policy are subject to both the MGP and this policy. |

## Roles and Responsibilities

| Role | Responsibilities |
|------|-----------------|
| **The Board** | Oversight of the management of AI system risk. Approve the AIGP and any material changes to the policy, ensuring its objectives are compatible with strategy. Ensure sufficient and appropriate resources are available for key functions, including management of AI risk. |
| **Board Risk Committee** | Review and recommend the AIGP to the Board for approval. Monitor compliance with the Policy and report risks and issues to the Board as applicable. Oversight of risks associated with AI systems and the adequacy of the control environment and its impact on the risk profile. |
| **PetSure Audit Risk & Compliance Committee** | Reviews management and implementation of the AI Governance Policy, for its effectiveness in identifying and controlling AI system risk in relation to appetite. Oversight of risks associated with material AI systems and the adequacy of the control environment. |
| **Chief Insurance Officer** | Develop, maintain and update the AIGP as required. Monitor and report on the effective implementation of this Policy to the ELT, PetSure Risk and Audit Risk Committee, Board Risk Committee, and Board. Manage and oversee the communication of the AIGP. Approval of high-risk AI use cases and AI systems. |
| **PetSure Executive Leadership Team (ELT)** | Manage AI system risk as part of its overall corporate governance role and within delegated authorities. Ensure the effective operation of the AIGP and its implementation. Ensure there are available resources to develop, operate and validate material AI systems and the appropriate skills and training are in place for each functional area. Ensure that relevant employees are aware of the procedures for the discharge of their responsibilities around AI systems to manage AI system risk. |
| **Chief Risk Officer and 2nd Line Risk & Compliance leads** | Review of the AIGP. Monitor the Group AI System Register for appropriate AI system registration and assessment. Provide objective advice and challenge over AI system controls with AI owners and the appropriateness of AI system ratings. Identify improvements and updates to the AIGP where required. |
| **AI Owner** | Register and maintain the AI system details in the Group AI System Register. Assess the AI system materiality rating and ensure that any AI system with a Material rating meets the minimum governance requirements. Establish appropriate AI system controls, including human oversight mechanisms. Arrange for the AI system to be validated according to the guidelines set out in the AIGP and approve and appoint a suitable steward as required. Review and sign off the AI system validation documentation. Reviews the AIGP as required. Communicates any changes to the AIGP to key stakeholders. |
| **AI Steward(s)** | Responsible for verifying controls, reviewing documentation, configuration, and assumptions, as well as reviewing system behaviour, outputs, and underlying code or models. Documenting the validation performed according to the requirements of the AIGP. Ensuring the AI system validation process is followed. |
| **Legal & Compliance (L&C)** | Interpret regulatory requirements as they apply to AI. Review high-risk AI use cases for compliance with applicable legislation and prudential standards. Advise on incident reporting obligations. |
| **Internal Audit** | Independent assurance over the effectiveness of AI governance controls, including AI System Register completeness, incident management process effectiveness, and training compliance. |

## Policy Framework

The AIGP sits at the top of PetSure's AI governance document hierarchy. It establishes the governance structures, oversight mechanisms, and accountability framework within which all other AI-related policies and standards operate. The document hierarchy is as follows:

| Document | Purpose |
|----------|---------|
| **AI Governance Policy** | How we govern AI — structures, roles, oversight, incident management, reporting |
| **Model Governance Policy** | How we govern models — registration, validation, ownership, materiality assessment |
| **Responsible Use of AI Policy** | What principles guide AI use — ethics, fairness, transparency, accountability |
| **AI Acceptable Use Standard** | What people can and cannot do — tools, use cases, data rules, customer-facing guardrails |

### Relationship Between Documents

- The **AI Governance Policy** is the parent governance document. It defines the governance machinery — who oversees AI, how decisions are made, how incidents are managed, what gets reported to the Board.
- The **Model Governance Policy** addresses the specific governance requirements for quantitative models, including registration, validation, and attestation. Where an AI system incorporates models, both the AIGP and MGP apply concurrently.
- The **Responsible Use of AI Policy** establishes the principles and values that guide AI use at PetSure — transparency, fairness, accountability, privacy, human-centricity, and safety. It is the "why" and "what we stand for" document.
- The **AI Acceptable Use Standard** translates the policies into operational rules — approved tools, data handling requirements, training obligations, and reporting channels. It enables the organisation to respond to changes in the AI landscape (new tools, new risks) without delay.

## Governance Structure

This section sets out the oversight mechanisms, escalation paths, and reporting cadence through which the Board and management exercise oversight of AI risk. Accountability for each role is defined in Roles and Responsibilities and is not repeated here.

### Committee Oversight Flow

Oversight of AI risk flows upward through the following committee chain.

### Decision Authority Matrix

The following matrix defines who approves what within the AI governance framework:

| Decision | Authority |
|----------|-----------|
| Approve or materially change the AIGP | Board (on recommendation from BRC) |
| Approve or materially change the Responsible Use of AI Policy | Board (on recommendation from BRC) |
| Approve or change the AI Acceptable Use Standard | CInsO |
| Classify an AI system as Material | AI Owner (may be overridden by CRO, CEO, Internal Audit, or Board) |
| Approve a Material AI system for production deployment | ELT member to whom the AI Owner reports |
| Approve a Material AI use case | AI Steering Committee |
| Grant an exemption from the AIGP | CInsO (as Policy Owner) |
| Escalate an AI incident to the Board | CInsO or CRO (based on severity) |

### Reporting

| Report | Audience | Frequency | Content |
|--------|----------|-----------|---------|
| AI Operational Report | AI Committee (ELT) | Bi-Monthly | New AI use cases. Incident log. Tool usage trends. Upcoming regulatory changes. |
| AI Risk Report | Board Risk Committee | Monthly | AI risk profile against risk appetite. AI incident trends. Control environment updates. Emerging AI risks. Material changes to AI risk appetite alignment. The BRC reports AI risk matters to the Board as part of its standing reporting obligations. |

## AI System Materiality Assessment

For the purpose of this policy, AI Systems (or AI System Groups) are assessed with reference to the Impact Matrix as defined in the current Risk Management Strategy (RMS):

- A **Material AI System** (or AI System Group) is one where failure, misuse, or incorrect operation could be expected to lead to an inherent Extreme or Major impact based on the Impact Matrix in the RMS.
- Extreme or Major impacts are not limited to financial risks. Customer, people, operational, partners, regulatory impacts, and relevant scenarios are also considered in the assessment.
- AI systems can also be deemed material by the AI owner, or the Chief Executive Officer (CEO), Chief Risk Officer (CRO), Internal Audit, or Board.

In addition to the standard RMS Impact Matrix criteria, the following AI-specific triggers must be considered when assessing materiality. An AI system that meets any of the following criteria is presumed Material unless the AI owner documents a justified rationale otherwise:

- The AI system makes or materially influences decisions affecting customers (e.g. pricing, underwriting, claims eligibility, policy servicing)
- The AI system processes sensitive personal data
- The AI system can produce consequential outputs — such as decisions, actions, or communications — without a human reviewing each output before it takes effect
- The AI system is subject to heightened regulatory exposure (APRA prudential requirements, ASIC conduct scrutiny, Privacy Act implications for automated decision-making)
- The AI system interacts directly with customers without human intermediation (e.g. a chatbot or automated outbound communication, as distinct from an AI tool used by an employee to draft content that is then reviewed before sending)

A **Non-Material AI System** is any AI system that does not meet the definition of a Material AI System.

## Requirements under the AIGP

Requirements for Material AI systems and Non-Material AI systems are summarised below:

| Section | Requirements | Material AI Systems | Non-Material AI Systems |
|---------|-------------|--------------------|-----------------------|
| 8.1 | AI system registration | Yes | Yes |
| 8.2 | AI ownership | Yes | Yes |
| 8.3 | AI system documentation | Yes | Recommended |
| 8.4 | AI system approval | Yes | Recommended |
| 8.5 | Independent peer review and validation | Yes | Recommended |
| 8.6 | General AI system review and attestation | Yes | Recommended |

Note that external AI systems are not part of an AI System Group and need to be listed independently and follow the below requirements.

### AI System Registration

Each AI owner is responsible for entering and maintaining the details of their AI system(s) in the Group AI System Register and for determining a materiality rating using the AI system materiality assessment process outlined above. Details entered in the Group AI System Register are commensurate with the complexity and materiality of the AI system under consideration.

At a minimum, the details required to be registered for each AI system are documented in Appendix A.

Any material changes to AI systems and/or new AI system developments must be considered and added to the information in the Group AI System Register to maintain an up-to-date register and materiality assessment.

AI owners are responsible for updating and reviewing the registration of their AI systems on at least an annual basis and on any material changes to the AI system.

### AI Ownership

For each AI system that is assessed as "material," an AI owner is assigned. The AI owner must be a member of the Executive Leadership Team (ELT) or at a minimum a "Head of" level. The AI owner is responsible for the use, governance, and validation of that AI system, including where the AI system is used by a team, and for demonstrating adherence with the requirements under the AIGP. Where there are multiple users of an AI system, for example across teams, a primary owner is determined, who is responsible for ensuring that the AI system complies with the AIGP on an ongoing basis.

### AI System Documentation

All Material AI systems are supported by documentation. The degree of documentation will depend on the materiality, size, and complexity of the AI system, but must be adequate to support the review and independent validation process.

Key limitations, assumptions, and governance controls are clearly documented to ensure they are understood by AI system users. Any changes to the AI system must be recorded in the system's change log. This change log may be managed by the AI owner or delegated as appropriate.

Documentation must be of a standard to support compliance with relevant regulatory requirements.

In addition to standard documentation practices, Material AI systems must also document:

- **Controls:** Preventive, detective, and corrective controls in place, including input validation, output filtering, monitoring arrangements
- **Prompts and configuration:** For generative AI and agent-based systems, the system prompts, configuration settings, tool permissions, and guardrails that govern system behaviour
- **Limitations and known risks:** Known limitations of the AI system, including scenarios where the system may produce unreliable outputs, and any residual risks accepted by the AI owner

All Material rated AI systems are appropriately documented to the level that an appropriately skilled person(s) would be able to independently validate the AI system.

### AI System Approval

Material AI systems must be approved by the ELT member to whom the AI owner reports (or their delegate) before deployment into production use.

Approval for Material AI systems requires the following supporting evidence:

- **Risk assessment:** A completed AI risk assessment in accordance with the Group's risk assessment methodology, documenting inherent risks, ongoing monitoring controls, and residual risk
- **Regulatory review:** Confirmation that applicable regulatory requirements have been identified and addressed, including privacy, prudential, and conduct obligations
- **Security assessment:** Confirmation that the AI system has been assessed against applicable information security requirements (per CPS 234) and that identified risks have been mitigated
- **Pilot evidence:** Where practicable, evidence from a controlled pilot or staging deployment demonstrating that the AI system performs as intended and controls operate effectively

### Independent Peer Review and Validation

AI owners must ensure that their AI systems undergo an appropriate peer-review/validation process when new AI systems are developed, or existing AI systems are changed (re-developed or change of scope) to ensure that the AI system is correct, working as intended, and changes made are appropriate. The maximum period of validation and independent review for any AI system is one year (if there are no changes made to the AI system for more than one year, it still needs to be reviewed/validated every year) to ensure that AI systems are still appropriate for the purpose intended.

The extent of the peer review/validation will depend on the materiality of the AI system, and the extent of changes in the system. For example, for a new Material AI system, the validation process might consider (but not necessarily) the appropriateness of the design, assessment of the system's components and integration points, configuration review, and output quality assessment. However, a minor change in a Material AI system might involve a peer review process to ensure that changes made are appropriate and system outcomes are aligned to expectations.

Peer review/validation for Material AI systems is performed by an appropriately qualified and competent individual who is independent of the AI system development process and ideally is operationally independent of the AI owner (not a direct report of the AI owner).

The AI system validation process includes the following steps:

- Conduct a data review and reconciliation (including review of training data, input data sources, and data quality)
- Review the assumption(s), input(s), and configuration of the AI system (including prompts, parameters, and tool permissions for agent-based systems)
- Review the set-up, architecture, and process(es) of the AI system
- Review the output(s) of the AI system, including testing for bias and hallucination where applicable
- Review the controls of the AI system, including human oversight mechanisms and escalation paths
- Review the ongoing monitoring arrangements, including performance metrics, drift detection, and alerting thresholds

### General AI System Review

Annually, AI owners are required to undertake a general AI system review which is a holistic review to assess the AI system's health. The extent of the review includes evidence of effective AI system usage, adequacy of documentation, review of the AI system's materiality, and summary of changes made since the last review.

In addition, the annual review must consider:

- **Performance monitoring:** Evidence that the AI system continues to perform within acceptable thresholds, including accuracy, reliability, and latency metrics
- **Control effectiveness:** Assessment of whether preventive, detective, and corrective controls remain effective and fit for purpose
- **Usage patterns:** Review of how the AI system is being used in practice, including any usage outside the originally intended scope, and whether human oversight levels remain appropriate

This format of this review includes a written statement of the items considered in the review.

## Incident Management

All employees are expected to report AI-related incidents through the established incident management process. AI incidents include but are not limited to: AI system outputs that cause or could cause customer harm, systematic errors or biases identified in AI outputs, unauthorised use of AI systems, data breaches involving AI systems, and failures of AI system controls.

## Compliance

All employees are required to comply with the AIGP. A breach of this Policy by an employee may result in disciplinary action, which may include termination of employment in cases of a serious breach of this Policy. Any instances of non-compliance should be treated in accordance with the Incident Management Policy.

## Exemptions

Any instance where a business area or employee is unable to comply with the requirements of this Policy, an exemption request must be sought in writing from the Policy owner. Exemptions will be considered on a case-by-case basis and will only be granted based on the circumstances and potential risk.

## Appendix A: AI System Register Details

### Core Fields (All AI Systems)

The following fields are required for every registered AI system, including Non-Material systems.

| Item | Details |
|------|---------|
| AI System / AI System Group name | Name of AI system or name of AI system group |
| AI System type | Classification of the AI system (e.g. ML Model, GenAI Application, AI Agent, AI-enabled Automation, Decision Support System) |
| AI Owner | Person responsible for the AI system |
| Is the AI system an external system? | Yes/No — If Yes, external vendor details documented |
| AI system platform/infrastructure | The name of the platform, infrastructure, or hosting environment (e.g. Azure OpenAI, AWS SageMaker, on-premises, M365 Copilot) |
| AI system description and purpose | A brief description of the purpose of the AI system / group of AI systems and other component parts |
| Data classification | Classification of data processed by the AI system (e.g. Public, Internal, Confidential, Restricted) |
| PII flag | Whether the AI system processes personally identifiable information (Yes/No). If Yes, specify categories of PII processed |
| Customer-facing flag | Whether the AI system directly interacts with or is visible to customers (Yes/No) |
| Status | In Production, Development/Validation, Retired |
| AI System Materiality Assessment and justification | Result of materiality assessment and rationale, including consideration of AI-specific materiality triggers |

### Additional Fields (Material AI Systems)

The following fields are required for AI systems assessed as Material. They are recommended but not mandatory for Non-Material systems.

| Item | Details |
|------|---------|
| Use Case ID | Reference to the associated use case in the AI Use Case Register |
| Model ID(s) | Reference(s) to any underlying model(s) registered in the Group Model Register under the MGP. Where an AI system incorporates one or more models, list all applicable Model IDs |
| Version Number | Used for version tracking |
| Human oversight level | Level of human oversight applied (e.g. Human-in-the-Loop, Human-on-the-Loop, Human-out-of-the-Loop) |
| Risk Assessment ID | Reference to the completed AI risk assessment document |
| Links to AI system documentation | Link to written documentation (e.g. system design document, configuration record, validation report) |
| AI system approver | Person responsible for approving the AI system |
| AI system approval date | Date of approval |
| AI steward | Person responsible for performing AI system validation |
| AI system validation date | Date of validation |
| AI System General Review Date (and Last Review) | Date of last review |
| AI System Attestation Evidence | Link to written documentation (e.g. email, pdf, word document) |
