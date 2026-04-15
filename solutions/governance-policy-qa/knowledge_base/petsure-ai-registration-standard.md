# PetSure Australia AI Solution Registration Standard

**Document ID:** GOV-AI-005
**Version:** 1.1
**Status:** Active
**Effective Date:** 1 April 2025
**Next Review Date:** 1 October 2025
**Owner:** Risk Management AI
**Approval Authority:** Head of Risk Management AI
**Classification:** Internal — Restricted

---

## 1. Purpose

This standard defines the mandatory registration process for all AI solutions governed by the PetSure Australia Group AI Policy (GOV-AI-001). It specifies the solution manifest schema, risk tier assignment criteria, registration workflow, validation rules, change management requirements, and de-registration procedures.

Registration is the foundation of AI governance at PetSure Australia. A solution that is not registered cannot be evaluated, monitored, or audited. The Registration compliance gate (AI-GOV-001) is the only gate that cannot be exempted under any circumstances, reflecting the principle that governance begins with visibility: you cannot govern what you cannot see.

This document is subordinate to GOV-AI-001 and implements the registration requirements described in Sections 5, 6.1 (Registration gate), and 10 of that policy.

## 2. Scope

This standard applies to every AI solution that falls within the scope of GOV-AI-001, specifically:

- All AI and machine learning systems developed, procured, or operated by any PetSure Australia business unit, subsidiary, or third-party vendor acting on PetSure Australia's behalf.
- Solutions at all lifecycle stages: development, testing, staging, production, and retirement.
- Both new solutions entering the platform and existing solutions that predate this standard (which must be registered under the transitional provisions in Section 10).

Registration is required regardless of risk tier. Experimental solutions have reduced manifest requirements but must still be registered.

## 3. Definitions

| Term | Definition |
|------|-----------|
| **Solution Manifest** | A structured YAML file (`solution.yaml`) stored in the solution's repository root that declares the solution's identity, type, owner, risk tier, guardrail configuration, evaluation criteria, and compliance requirements. The manifest is the solution's contract with the platform. |
| **Solution ID** | A globally unique identifier assigned to each solution during registration. Format: `{business-unit}-{solution-name}` using lowercase alphanumeric characters and hyphens. Example: `retail-policy-qa-agent`. |
| **Solution Type** | The functional category of the solution, determining which evaluation metrics apply. Valid types: `qa`, `classification`, `scoring`, `validation`, `conversational`, `agentic`. |
| **Intake** | The initial assessment process where a team presents a proposed AI solution to the Governance Portal team for review, tier assignment, and registration. |
| **Governance Review** | A structured review session where the Governance Portal team assesses a solution's risk profile, assigns a risk tier, and validates the proposed manifest configuration. |
| **Manifest Validation** | Automated checks that verify the solution manifest conforms to the required schema, contains all mandatory fields for the solution's type and tier, and passes structural integrity checks. |

## 4. Solution Manifest Schema

### 4.1 Manifest Structure

The solution manifest (`solution.yaml`) is a YAML file with the following top-level sections:

```yaml
# solution.yaml — top-level structure
id: string                  # Solution ID (mandatory)
name: string                # Human-readable solution name (mandatory)
description: string         # Brief description of the solution's purpose (mandatory)
version: string             # Semantic version of the solution (mandatory)
type: string                # Solution type (mandatory)
risk_tier: string           # Assigned risk tier (mandatory)
owner: object               # Solution owner details (mandatory)
data: object                # Data access and sensitivity (mandatory)
guardrails: object          # Guardrail configuration (mandatory)
evaluation: object          # Evaluation configuration (conditional)
knowledge_base: object      # Knowledge base configuration (conditional, Q&A only)
prompt: object              # Prompt governance (conditional)
compliance: object          # Compliance metadata (auto-populated by platform)
```

### 4.2 Mandatory Fields — All Solutions

The following fields are mandatory for every registered solution, regardless of type or risk tier:

| Field | Type | Validation Rule | Description |
|-------|------|----------------|-------------|
| `id` | string | Must match pattern `^[a-z0-9]+(-[a-z0-9]+)*$`. Must be globally unique across the platform. Maximum 64 characters. | The solution's unique identifier. Assigned during registration and immutable thereafter. |
| `name` | string | Non-empty. Maximum 128 characters. | Human-readable display name for the solution. |
| `description` | string | Non-empty. Maximum 500 characters. | A concise description of the solution's purpose, audience, and key capabilities. |
| `version` | string | Must match semantic versioning pattern `^\\d+\\.\\d+\\.\\d+$`. | The current version of the solution. Must be incremented on material changes. |
| `type` | string | Must be one of: `qa`, `classification`, `scoring`, `validation`, `conversational`, `agentic`. | Determines which evaluation metrics apply (see GOV-AI-006). |
| `risk_tier` | string | Must be one of: `experimental`, `production_internal`, `production_customer_facing`. | Assigned by the Governance Portal team during intake. Determines governance intensity. |
| `owner.name` | string | Non-empty. Must be a valid PetSure Australia employee name. | The accountable individual for this solution. |
| `owner.email` | string | Must be a valid `@petsure.com.au` email address. | Contact email for the solution owner. |
| `owner.team` | string | Non-empty. Must match a registered team name. | The team responsible for building and operating the solution. |
| `owner.team_group` | string | Non-empty. | The team group the solution reports into for governance purposes. |
| `data.sources` | list | At least one entry. | List of data sources the solution accesses. |
| `data.pii_exposure` | string | Must be one of: `none`, `indirect`, `direct`. | Level of PII exposure in the solution's inputs and outputs. |
| `data.classification` | string | Must be one of: `public`, `internal`, `confidential`, `restricted`. | Data classification level, per PetSure Australia Data Governance Standard (GOV-AI-004). |
| `guardrails.enabled` | list | Must include at least `scope_containment` and `prompt_injection` for all tiers. | List of active guardrails. |

### 4.3 Conditional Fields — By Type and Tier

Additional fields become mandatory depending on the solution type and risk tier:

| Field | Required When | Validation Rule | Description |
|-------|--------------|----------------|-------------|
| `evaluation.golden_dataset` | `production_internal` or `production_customer_facing` | Must reference a valid file path within the solution repository | Path to the golden dataset file |
| `evaluation.metrics` | `production_internal` or `production_customer_facing` | Must list applicable metrics for the solution type | Metrics to evaluate (see GOV-AI-006 Section 5.1) |
| `evaluation.thresholds` | `production_internal` or `production_customer_facing` | Each metric must have a numeric threshold | Per-metric pass/fail thresholds |
| `evaluation.threshold_overrides` | Optional | Must include justification and approval reference for each override | Custom thresholds that differ from defaults |
| `knowledge_base.path` | Type is `qa` | Must reference a valid directory | Path to the knowledge base documents |
| `knowledge_base.document_count` | Type is `qa` | Positive integer | Number of documents in the knowledge base |
| `prompt.system_prompt_path` | `production_internal` or `production_customer_facing` | Must reference a valid file path | Path to the system prompt file |
| `prompt.approval_commit` | `production_internal` or `production_customer_facing` | Must be a valid git commit hash | Git commit hash of the approved prompt version |
| `guardrails.pii_detection` | `production_internal` or `production_customer_facing` | Must be `true` | PII detection guardrail must be active |
| `guardrails.bias_detection` | `production_internal` or `production_customer_facing` | Must be `true` | Bias detection guardrail must be active |
| `guardrails.toxicity_detection` | `production_internal` or `production_customer_facing` | Must be `true` | Toxicity detection guardrail must be active |

### 4.4 Auto-Populated Fields

The platform automatically populates the following fields. Teams must not set these manually:

| Field | Populated By | Description |
|-------|-------------|-------------|
| `compliance.registration_date` | Platform | ISO 8601 timestamp of initial registration |
| `compliance.last_evaluation_date` | Evaluation Harness | Timestamp of the most recent evaluation run |
| `compliance.next_evaluation_due` | Platform | Calculated based on risk tier cadence |
| `compliance.gate_results` | Compliance Runner | Latest pass/fail results for all 8 compliance gates |
| `compliance.evidence_package_id` | Evidence Store | Reference to the latest compliance evidence package |

## 5. Risk Tier Assignment Criteria

### 5.1 Assessment Dimensions

Risk tier is assigned by the Governance Portal team during intake based on five dimensions, as defined in GOV-AI-001 Section 5.3:

| Dimension | Weight | Experimental | Production Internal | Production Customer-Facing |
|-----------|--------|-------------|--------------------|-----------------------------|
| **Audience** | High | Internal team only, limited users | All internal PetSure Australia staff, or a specific business unit | External customers, investors, regulators, or public |
| **Decision Impact** | High | No operational decisions depend on outputs | Outputs inform internal decisions but human review is standard | Outputs directly influence customer outcomes, financial decisions, or regulatory reporting |
| **Data Sensitivity** | Medium | Synthetic or public data only | Internal data, no direct customer PII | Customer data, PII, financial records |
| **Reversibility** | Medium | All outputs are easily discarded | Outputs can be corrected with moderate effort | Outputs are difficult or impossible to retract once delivered |
| **Regulatory Exposure** | High | No regulatory obligations | General operational risk obligations (CPS 230) | Specific regulatory requirements (credit reporting, consumer protection, anti-discrimination) |

### 5.2 Tier Assignment Rules

The highest-risk dimension determines the floor for tier assignment:

1. If **any** dimension is assessed at the customer-facing level, the solution must be assigned `production_customer_facing`.
2. If no dimension is at the customer-facing level but **any** dimension is at the internal level, the solution must be assigned `production_internal`.
3. A solution may only be assigned `experimental` if **all** dimensions are at the experimental level.

The Governance Portal team may assign a higher tier than the floor if professional judgement warrants it. The Governance Portal team may not assign a lower tier than the floor without documented justification approved by the Head of Risk Management AI.

### 5.3 Tier Assignment Documentation

The tier assignment rationale must be recorded in the intake record and include:

- Assessment of each of the five dimensions with supporting evidence
- The resulting tier determination and the rationale
- Any dissenting views from the team or Governance Portal team members
- The name and role of the person who made the final tier determination
- Date of the assessment

## 6. Registration Process

### 6.1 Registration Workflow

The registration process consists of five stages:

| Stage | Actor | Activities | Outputs |
|-------|-------|-----------|---------|
| **1. Intake** | Team | Team submits an intake request via the platform portal or API (`POST /api/solutions/onboard`). Provides solution name, description, type, intended audience, data sources, and proposed guardrail configuration. | Intake record created in the platform |
| **2. Governance Review** | Governance Portal team | Governance Portal team reviews the intake, assesses risk dimensions, assigns risk tier, validates proposed guardrails against tier requirements, and identifies any gaps. May request additional information from the team. | Tier assignment, review notes, conditions (if any) |
| **3. Manifest Creation** | Team | Team creates the `solution.yaml` file incorporating the assigned tier and any conditions from governance review. Team populates all mandatory and conditional fields. | Draft solution manifest |
| **4. Manifest Validation** | Platform | Automated validation checks the manifest against the schema, verifies all mandatory fields are present and correctly formatted, confirms the solution ID is unique, and validates field values against allowed enumerations. | Validation report (pass/fail with specific errors) |
| **5. Platform Registration** | Platform | Once the manifest passes validation, the solution is registered on the platform. The Registration compliance gate (AI-GOV-001) is marked as passed. Compliance tracking begins. | Registered solution, compliance tracking active |

### 6.2 Registration Timeline

| Risk Tier | Expected Intake-to-Registration Time | Maximum Allowed |
|-----------|-------------------------------------|-----------------|
| `experimental` | 1-2 business days | 5 business days |
| `production_internal` | 3-5 business days | 10 business days |
| `production_customer_facing` | 5-10 business days | 15 business days |

Customer-facing solutions require additional time for a more thorough governance review, including consultation with the AI Ethics Board where the solution involves sensitive use cases (see GOV-AI-002 Section 7 for ethics review triggers).

### 6.3 Fast-Track Registration

Experimental solutions may use a fast-track registration process that bypasses the formal governance review session. Fast-track registration requires:

- The solution type is declared as `experimental`
- The solution does not process any real customer data
- The solution is not connected to any production system
- The team self-certifies compliance with the experimental-tier requirements

Fast-track registered solutions are reviewed by the Governance Portal team within 10 business days of registration. If the Governance Portal team determines the tier is inappropriate, it will be escalated per GOV-AI-001 Section 5.4.

## 7. Manifest Validation Rules

### 7.1 Structural Validation

The platform performs the following structural checks on every manifest submission:

| Check | Rule | Failure Behaviour |
|-------|------|-------------------|
| YAML syntax | Manifest must be valid YAML | Registration blocked |
| Schema conformance | All fields must match expected types and structures | Registration blocked |
| Required fields | All mandatory fields for the solution's type and tier must be present | Registration blocked |
| ID format | Solution ID must match `^[a-z0-9]+(-[a-z0-9]+)*$` and be <= 64 characters | Registration blocked |
| ID uniqueness | Solution ID must not already exist on the platform | Registration blocked |
| Type validity | Solution type must be in the allowed enumeration | Registration blocked |
| Tier validity | Risk tier must be in the allowed enumeration | Registration blocked |
| Email format | Owner email must match PetSure Australia domain patterns | Registration blocked |
| Version format | Version must be valid semantic version | Registration blocked |
| Guardrail minimum | `scope_containment` and `prompt_injection` must be in the enabled guardrails list | Registration blocked |

### 7.2 Semantic Validation

Beyond structural checks, the platform performs semantic validations:

| Check | Rule | Failure Behaviour |
|-------|------|-------------------|
| Tier-guardrail alignment | If tier is `production_internal` or higher, PII, bias, and toxicity guardrails must be enabled | Registration blocked |
| Tier-evaluation alignment | If tier is `production_internal` or higher, evaluation section must be present and complete | Registration blocked |
| Metric-type alignment | Declared evaluation metrics must be valid for the declared solution type (see GOV-AI-006 Section 5.1) | Registration blocked |
| Threshold reasonableness | Declared thresholds must not be lower than the tier's minimum thresholds (see GOV-AI-006 Section 5.2) unless a threshold override is documented | Warning issued |
| File path validity | All referenced file paths (golden dataset, knowledge base, system prompt) must exist in the repository | Registration blocked |
| Data classification consistency | If data classification is `restricted` or `confidential`, risk tier must be at least `production_internal` | Registration blocked |

## 8. Change Management

### 8.1 Changes Requiring Re-registration

The following changes to a registered solution require the manifest to be updated and the Registration gate to be re-validated:

| Change Type | Required Action | Approval |
|-------------|----------------|----------|
| **Solution scope change** | Update description, data sources, and guardrail configuration. Governance review if scope expansion is material. | Team + platform team (if material) |
| **Risk tier change** | Update risk tier. Triggers re-assessment of all conditional requirements. All compliance gates must be re-run at the new tier. | Team Lead approval mandatory |
| **Owner change** | Update owner fields. New owner must acknowledge accountability. | Outgoing and incoming owner, Team Lead |
| **Type change** | Update solution type. Triggers change in applicable evaluation metrics (see GOV-AI-006). Golden dataset may need restructuring. | Governance review mandatory |
| **Guardrail change** | Update guardrail configuration. Must continue to meet tier minimums. | Team (if adding), platform team (if removing) |
| **Data source change** | Update data sources. If new sources introduce higher data sensitivity, tier re-assessment may be required. | Team + platform team (if sensitivity changes) |

### 8.2 Changes Not Requiring Re-registration

The following changes can be made without re-running the Registration gate, though they may trigger other gates:

- Model version updates (triggers re-evaluation, not re-registration)
- System prompt updates (triggers Prompt Governance gate, not re-registration)
- Golden dataset updates (triggers re-evaluation, not re-registration)
- Knowledge base updates (triggers re-evaluation, not re-registration)
- Version number increment (routine update)

### 8.3 Change Audit Trail

All manifest changes are tracked by the platform. The change audit trail records:

- Previous and new values for every changed field
- Timestamp of the change
- Identity of the person who made the change
- Approval references where required
- Whether the change triggered re-validation of any compliance gates

## 9. De-registration and Retirement

### 9.1 When De-registration Is Required

A solution must be de-registered when:

- The solution is permanently decommissioned and will no longer operate
- The solution is replaced by a successor solution (the successor must be separately registered)
- The solution's registration was made in error

### 9.2 De-registration Process

| Step | Actor | Activities |
|------|-------|-----------|
| **1. Retirement Request** | Solution Owner | Owner submits a de-registration request via the platform, providing a reason and confirming that the solution has been or will be shut down. |
| **2. Dependency Check** | Platform | Platform checks whether any other registered solutions depend on the solution being retired. If dependencies exist, they must be resolved first. |
| **3. Data Retention** | Solution Owner + platform team | All compliance evidence, evaluation reports, audit trails, and the final solution manifest are archived per PetSure Australia data retention requirements. Minimum retention: 7 years for customer-facing solutions, 5 years for internal solutions. |
| **4. De-registration** | Platform | Solution status is changed to `retired`. Compliance tracking ceases. The solution ID is permanently reserved and cannot be reused. |
| **5. Confirmation** | Platform team | Platform team confirms the de-registration and updates the AI solution register. |

### 9.3 Dormant Solutions

If a registered solution has had no evaluation runs, no manifest updates, and no audit trail entries for more than 180 days, the platform flags it as dormant. The solution owner is notified and must either:

- Confirm the solution is still active and schedule an evaluation, or
- Initiate de-registration

If no response is received within 30 days, the platform team escalates to the owner's line management.

## 10. Transitional Provisions

AI solutions that were operational before the effective date of this standard must be registered within the following timeframes:

| Risk Tier | Registration Deadline |
|-----------|----------------------|
| `production_customer_facing` | 1 July 2025 |
| `production_internal` | 1 October 2025 |
| `experimental` | 31 December 2025 |

Solutions that are not registered by their deadline will be flagged as non-compliant and escalated to the Team Lead and the relevant business unit head.

## 11. Related Documents

| Document | Relationship |
|----------|-------------|
| PetSure Australia Group AI Policy (GOV-AI-001) | Parent — this standard implements registration requirements from Sections 5, 6.1, and 10 |
| PetSure Australia Responsible AI Principles (GOV-AI-002) | Peer — ethics review triggers referenced during intake for sensitive use cases |
| PetSure Australia Data Governance Standard (GOV-AI-004) | Peer — data classification and PII exposure levels referenced in the manifest schema |
| PetSure Australia AI Testing & Evaluation Framework (GOV-AI-006) | Peer — evaluation configuration in the manifest must align with metric and threshold requirements |
| PetSure Australia Prompt Governance Guideline (GOV-AI-007) | Peer — prompt governance fields in the manifest must align with prompt version control requirements |
| APRA CPS 230 — Operational Risk Management | Regulatory — registration supports the identification and management of AI operational risk |

## 12. Review and Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 1 April 2025 | Risk Management AI | Initial release aligned to GOV-AI-001 v2.0 |
| 1.1 | 1 July 2025 | Risk Management AI | Added fast-track registration for experimental solutions. Clarified dormant solution handling. Added transitional provisions for pre-existing solutions. Aligned to GOV-AI-001 v2.1. |
