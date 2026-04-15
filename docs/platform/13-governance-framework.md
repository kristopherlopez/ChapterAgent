# Governance, Responsible AI & Risk Management Framework

This document defines the policy layer that sits above the platform's operational controls. The compliance-as-code pipeline (doc 07) automates enforcement. This document explains **what** is being enforced, **why**, and **which external frameworks** the platform's controls satisfy.

The chapter doesn't invent governance from scratch — it operationalises PetSure Australia's existing policies and Australia's regulatory expectations into automated, auditable controls.

---

## Responsible AI Principles

These principles govern every AI solution that passes through the platform. They are not aspirational — each maps directly to a platform control that enforces it.

| # | Principle | What It Means in Practice | Platform Control |
|---|-----------|---------------------------|------------------|
| 1 | **Fairness** | AI solutions must not produce systematically biased outputs across demographic groups. Fairness definitions are configured per solution type (equal opportunity, demographic parity, etc.) | DeepEval BiasMetric (deployment gate + real-time monitoring) |
| 2 | **Transparency** | Every AI decision must be explainable and traceable. Users and reviewers can see why an output was produced. | Citation coverage guardrail, tracing SDK, evidence export |
| 3 | **Accountability** | Every solution has a named owner, a risk tier, and a human sign-off on test data. Failures are logged, attributed, and escalated. | Solution manifest (owner field), golden dataset sign-off, compliance event log |
| 4 | **Privacy** | No personal information appears in AI outputs. Detection runs on every response, not just at deployment. | Presidio PII detection (zero-tolerance gate + real-time scan) |
| 5 | **Safety** | AI solutions must not produce harmful, toxic, or dangerous content. Content safety guardrails are mandatory for all risk tiers above experimental. | DeepEval ToxicityMetric, content safety guardrail, scope adherence |
| 6 | **Reliability** | AI solutions must perform consistently within defined quality thresholds. Degradation is detected and acted on automatically. | Evaluation harness thresholds, drift monitoring, automatic re-evaluation |
| 7 | **Human Oversight** | Humans remain in the loop for risk tier assignment, golden dataset approval, and escalation from automated alerts. The platform automates enforcement, not judgment. | Risk tier conversation, golden dataset sign-off, alert escalation to chapter lead |

### How Principles Flow to Controls

```
Responsible AI Principle
  → Platform Policy (AI-GOV-XXX)
    → Automated Control (guardrail, gate, or monitor)
      → Evidence (logged, exportable, auditable)
```

Every principle traces through this chain. If a principle cannot be traced to a working control with evidence, the platform has a gap.

---

## AI Risk Register

The platform manages risk through a structured register. Each risk is identified, assessed, and mapped to the control that mitigates it.

### Risk Assessment Methodology

Risks are assessed on two dimensions:
- **Likelihood** — how probable is the risk given current controls? (Rare / Unlikely / Possible / Likely / Almost Certain)
- **Impact** — what is the consequence if the risk materialises? (Insignificant / Minor / Moderate / Major / Severe)

The combination determines inherent risk (before controls) and residual risk (after platform controls are applied).

### Register

| Risk ID | Risk | Category | Inherent Risk | Platform Control | Residual Risk |
|---------|------|----------|---------------|------------------|---------------|
| AIR-001 | **Hallucination** — AI produces factually incorrect output not grounded in source data | Output Quality | High | Faithfulness metric (deployment gate threshold + real-time check), citation coverage guardrail, regeneration on failure | Low |
| AIR-002 | **Bias & Discrimination** — AI produces systematically unfair outputs across demographic groups | Fairness | High | BiasMetric in evaluation harness + real-time monitoring, bias threshold gate | Low |
| AIR-003 | **PII Leakage** — AI exposes personal information in outputs | Privacy | High | Presidio PII detection (zero-tolerance deployment gate + per-response scan), response blocking on detection | Very Low |
| AIR-004 | **Prompt Injection** — Adversarial inputs manipulate AI behaviour | Security | Medium | Prompt injection detection guardrail, scope adherence check, input validation | Low |
| AIR-005 | **Toxic Content** — AI produces harmful, offensive, or dangerous outputs | Safety | Medium | ToxicityMetric (deployment gate + real-time), content safety guardrail | Very Low |
| AIR-006 | **Scope Creep** — AI responds to queries outside its permitted domain | Operational | Medium | Scope adherence guardrail (real-time, blocks and serves refusal) | Very Low |
| AIR-007 | **Model Drift** — AI performance degrades over time as data or environment changes | Reliability | High | Drift monitoring (7-day rolling average), automatic re-evaluation triggers, scheduled 90-day re-evaluation | Low |
| AIR-008 | **Audit Trail Gaps** — Inability to reconstruct what happened and why | Compliance | Medium | Tracing SDK (100% completeness requirement), audit trail completeness gate | Very Low |
| AIR-009 | **Uncontrolled Prompt Changes** — System prompt modifications without review introduce regressions | Operational | Medium | Prompt version control, approval commit requirement, automatic re-evaluation on prompt hash change | Low |
| AIR-010 | **Third-Party Model Changes** — LLM provider updates model behaviour without notice | Vendor | High | Model change detection triggers mandatory re-evaluation, golden dataset regression testing | Medium |
| AIR-011 | **Insufficient Test Coverage** — Golden dataset doesn't cover critical scenarios | Quality Assurance | Medium | Chapter review of golden dataset coverage, human sign-off requirement, coverage analysis in evidence package | Low |
| AIR-012 | **Unauthorised Deployment** — Solution deployed without passing governance gates | Compliance | Medium | CI/CD deployment gate (8 automated checks), pipeline blocks deployment on any failure | Very Low |

### Risk Appetite by Tier

Risk appetite is encoded in the platform's threshold configuration. Higher-risk solutions face stricter thresholds.

| Dimension | Experimental | Production Internal | Production Customer-Facing |
|-----------|-------------|--------------------|-----------------------------|
| Hallucination tolerance | Logged only | ≤ 10% hallucination score | ≤ 5% hallucination score |
| Bias tolerance | Logged only | ≤ 0.10 bias score | ≤ 0.05 bias score |
| PII tolerance | Logged only | Zero tolerance | Zero tolerance |
| Toxicity tolerance | Logged only | ≤ 0.05 toxicity score | ≤ 0.02 toxicity score |
| Audit completeness | Best effort | 100% | 100% |
| Re-evaluation frequency | None | 90 days | 30 days |

---

## Regulatory & Standards Alignment

The platform's controls map to external regulatory expectations and standards. This section provides the traceability an auditor or regulator needs.

### APRA CPS 230 — Operational Risk Management

CPS 230 requires ADIs to manage operational risks, including those from technology and third-party arrangements. AI solutions introduce operational risk through model behaviour, vendor dependencies, and process automation.

| CPS 230 Requirement | Platform Control | Evidence |
|----------------------|------------------|----------|
| Identify and assess operational risks | AI Risk Register (above), risk tier assignment per solution | Risk tier in solution manifest, register maintained by chapter |
| Maintain effective controls | 8 automated deployment gates, 7 real-time production checks | Deployment gate reports, production compliance logs |
| Monitor and report on operational risk | Portfolio dashboard, drift monitoring, compliance health metrics | Dashboard data, drift alerts, compliance health summary |
| Manage third-party risks | Model change detection triggers re-evaluation, vendor field in solution manifest | Re-evaluation reports after model changes, vendor tracking |
| Business continuity | Response blocking/regeneration on compliance failure (graceful degradation, not silent failure) | Failure logs with remediation actions taken |

### APRA CPS 234 — Information Security

CPS 234 requires ADIs to maintain information security capability commensurate with information asset threats.

| CPS 234 Requirement | Platform Control | Evidence |
|----------------------|------------------|----------|
| Classify information assets | Solutions classified by risk tier; data sensitivity considered in tier assignment | Solution manifest with risk tier |
| Implement controls commensurate with risk | Threshold configuration scales with risk tier — stricter controls for higher-risk solutions | Threshold config files, per-tier gate results |
| Detect and respond to security incidents | Prompt injection detection, scope violation blocking, PII scan on every response | Compliance event log (filter by security events) |
| Notify APRA of material incidents | Compliance event log provides the data; escalation to incident management is a chapter operational procedure | Failure logs, escalation records |
| Test control effectiveness | Evaluation harness runs on golden dataset, guardrail test suites, scheduled re-evaluation | Evaluation scorecards, guardrail test results |

### Australia's Voluntary AI Safety Standard (10 Guardrails)

Published by the Department of Industry, Science and Resources (DISR). While voluntary, these represent the Australian Government's expectations for responsible AI and are likely to inform future regulation.

| # | DISR Guardrail | Platform Alignment | Status |
|---|----------------|-------------------|--------|
| 1 | Establish, implement, and publish an accountability process | Solution manifest with named owner, risk tier, chapter oversight model | **Addressed** — accountability encoded in manifest and lifecycle |
| 2 | Establish and implement a risk management process | AI Risk Register, risk tier framework, automated risk-proportionate controls | **Addressed** — risk management is the platform's core function |
| 3 | Protect AI systems and implement data governance | PII detection, scope containment, prompt injection defence, audit logging | **Partially addressed** — data governance for training data requires supplementary policy (see below) |
| 4 | Test AI models and systems to ensure they work as intended | Evaluation harness (DeepEval), golden dataset testing, scheduled re-evaluation | **Addressed** — testing is automated and continuous |
| 5 | Enable human control or intervention | Human-in-the-loop for risk tier assignment, golden dataset sign-off, low-confidence flagging, chapter lead alerts | **Addressed** — humans decide risk appetite; platform enforces it |
| 6 | Inform end users regarding AI-enabled decisions | Transparency is solution-level (the squad's UX responsibility); platform provides citation coverage guardrail and tracing for auditability | **Partially addressed** — platform enables transparency; squads implement user-facing disclosure |
| 7 | Establish processes for people impacted by AI to challenge outcomes | Not a platform control — requires organisational process (complaints handling, human review pathway) | **Gap** — chapter should define escalation pathway template for squads |
| 8 | Be transparent about the use of AI | Solution registry provides portfolio visibility; evidence export provides regulatory transparency | **Partially addressed** — internal transparency strong; external disclosure is squad/business responsibility |
| 9 | Keep and maintain records | Audit trail (100% completeness), evidence export, compliance event logs, prompt version history | **Addressed** — record-keeping is automated and complete |
| 10 | Undertake conformity assessments | Deployment gate (pre-production assessment), scheduled re-evaluation, evidence export for external review | **Addressed** — conformity assessment is the deployment gate |

### PetSure Australia Group AI Policy (Internal)

The platform is designed to operationalise PetSure Australia's internal AI policy. The specific policy document is internal to PetSure Australia, but the platform's architecture assumes the following typical enterprise AI policy requirements:

| Expected Policy Requirement | Platform Control |
|-----------------------------|------------------|
| AI solutions must be registered and inventoried | Solution registry, `solution.yaml` manifest |
| AI solutions must be risk-assessed | Risk tier framework with three tiers |
| AI outputs must be monitored for quality and safety | Real-time compliance pipeline (7 checks per response) |
| AI solutions must have audit trails | Tracing SDK, 100% audit completeness requirement |
| AI solutions must be tested before deployment | Evaluation harness, 8-check deployment gate |
| Evidence must be available for assurance review | Evidence export (structured JSON + HTML report) |
| AI solutions must have human oversight | Risk tier assignment, golden dataset sign-off, alert escalation |

---

## Incident Response & Escalation

When an automated control catches a problem, the platform's response depends on the layer and severity.

### Real-Time Response (Layer 2 — Production Monitoring)

| Event | Automated Response | Escalation |
|-------|--------------------|------------|
| Scope violation | Response blocked, refusal served | Logged — no escalation unless repeated (>5 in 1 hour) |
| PII detected in output | Response blocked, PII redacted | **Immediate alert** to solution owner + chapter lead |
| Faithfulness below threshold | Response regenerated with stricter grounding | Logged — escalated if retry also fails |
| Bias score above threshold | Response blocked | Alert to solution owner + chapter lead |
| Toxicity detected | Response blocked | **Immediate alert** to solution owner + chapter lead |
| Audit trail incomplete | Response served but flagged | Alert to chapter lead — indicates instrumentation issue |

### Drift Response (Layer 2 — Continuous Monitoring)

| Signal | Severity | Action |
|--------|----------|--------|
| 7-day rolling average faithfulness declining | Warning | Alert to squad, dashboard moves to AMBER |
| Bias score at 80% of threshold | Warning | Alert to squad + chapter lead |
| Any metric crosses hard threshold | Critical | Dashboard moves to RED, chapter lead notified, solution flagged for re-evaluation |
| Sustained RED status (>48 hours without remediation) | Escalation | Chapter lead escalates to 2nd line |

### Escalation Path

```
Automated Control (detects issue)
  → Solution Owner (first responder — fix or acknowledge)
    → Chapter Lead (if unresolved within SLA or severity warrants)
      → 2nd Line Risk (if sustained non-compliance or material incident)
        → APRA Notification (if material information security incident per CPS 234)
```

### SLAs by Severity

| Severity | Response Time | Resolution Time | Escalation If Unresolved |
|----------|---------------|-----------------|--------------------------|
| Critical (PII, toxicity, sustained RED) | 1 hour | 24 hours | Chapter lead → 2nd line |
| High (bias, faithfulness failure after retry) | 4 hours | 48 hours | Squad → chapter lead |
| Medium (drift warning, scope violations) | 24 hours | 5 business days | Logged, reviewed in weekly chapter standup |
| Low (minor threshold approach) | Next review cycle | Next scheduled re-evaluation | No escalation |

---

## Model Lifecycle Governance

AI solutions don't stay static. Models change, prompts evolve, data drifts. The platform governs the full lifecycle, not just the initial deployment.

### Change Events and Required Actions

| Change Event | Detection Method | Required Action | Gate Required? |
|--------------|------------------|-----------------|----------------|
| Prompt modification | Prompt hash change detected in version control | Automatic re-evaluation against golden dataset | Yes — must pass evaluation thresholds |
| LLM provider model update | Squad declares in solution manifest; platform detects version change | Mandatory re-evaluation before production traffic resumes | Yes — full deployment gate |
| Golden dataset update | Dataset version change in manifest | Re-evaluation with new dataset; chapter reviews coverage | Yes — sign-off + evaluation |
| Risk tier change | Chapter reassigns based on scope change | Re-evaluation with new tier's thresholds | Yes — full deployment gate at new tier |
| Guardrail config change | Config file diff in version control | Guardrail test suite re-run | Yes — guardrail validation gate |
| Scheduled re-evaluation | Timer (90 days for internal, 30 days for customer-facing) | Full evaluation suite on current golden dataset | Yes — pass thresholds or move to AMBER |

### Version Tracking

The platform tracks versions of every moving part:

```yaml
# Tracked in solution evidence
solution_version: "1.2.0"          # Squad's solution code
prompt_version: "2.3"              # System prompt version
model_version: "gpt-4o-2024-08"   # LLM model version
golden_dataset_version: "1.1"      # Test data version
guardrail_config_version: "1.0"    # Guardrail thresholds
platform_version: "0.9.0"          # Chapter platform version
```

Any version change triggers the appropriate re-evaluation pathway. The evidence package records which versions were active at every evaluation point.

---

## Data Governance

AI solutions consume, process, and produce data. The platform enforces data governance at the boundaries it controls.

### Platform-Enforced Data Controls

| Control | Scope | Implementation |
|---------|-------|----------------|
| **No PII in outputs** | Every response from every governed solution | Presidio entity detection (PERSON, EMAIL, PHONE, AU_ABN, AU_TFN, AU_MEDICARE) |
| **Synthetic test data** | Golden datasets must not contain real customer data | Chapter review during intake; sign-off confirms synthetic data |
| **Audit data retention** | Compliance event logs and traces retained per policy | Configurable retention period in solution manifest; default 12 months |
| **Data minimisation in traces** | Tracing SDK emits prompt hashes, not prompt content; logs structure, not payloads | SDK design — the platform sees what happened, not what was said |

### Squad Responsibilities (Not Platform-Enforced)

The platform governs AI outputs and governance artefacts. The squad retains responsibility for:

| Responsibility | Why It's the Squad's |
|----------------|----------------------|
| Training data quality and provenance | The squad owns their data pipeline; the platform doesn't access training data |
| Consent and legal basis for data use | Legal/compliance decision, not a technical control |
| Data classification of inputs | The squad knows their domain; the platform classifies risk tier, not data sensitivity |
| Data storage and access controls | Infrastructure-level controls outside the platform's scope |

The chapter provides guidance and templates for these responsibilities during intake (Phase 1), but enforcement is organisational, not automated.

---

## Governance Operating Model

How the chapter, squads, and assurance lines interact through the platform.

### Three Lines of Defence

| Line | Actor | Role | Platform Interaction |
|------|-------|------|----------------------|
| **1st Line** | Squad | Builds and operates the AI solution. Owns risk within their domain. | Registers solution, provides golden dataset, fixes failures, responds to alerts |
| **2nd Line** | Chapter (AI Governance) | Builds and operates the governance platform. Sets policy thresholds. Reviews risk tiers. | Maintains platform, reviews risk tiers, monitors portfolio dashboard, escalates sustained non-compliance |
| **3rd Line** | Internal Audit / External Audit | Independent assurance that controls are effective | Consumes evidence export, reviews policy-to-evidence mapping, validates control design |
| **Regulator** | APRA / ASIC | Prudential oversight | Receives evidence packages on request; platform designed for regulatory-ready evidence |

### Chapter Governance Cadence

| Activity | Frequency | Purpose |
|----------|-----------|---------|
| Portfolio dashboard review | Daily | Spot RED/AMBER solutions, triage drift alerts |
| Risk tier review for new solutions | On intake | Assign appropriate governance bar |
| Golden dataset coverage review | On intake + on update | Ensure test coverage matches risk profile |
| Threshold calibration | Quarterly | Review whether thresholds are too tight (false positives) or too loose (missed issues) |
| Risk register review | Quarterly | Update risk assessments, add new risks, retire mitigated risks |
| Framework alignment review | Annually (or on regulatory change) | Verify platform controls still satisfy regulatory expectations |
| Evidence export for 2nd/3rd line | On request | Generate compliance evidence package |

---

## Gaps and Roadmap

Honest accounting of what the platform addresses today and what requires further development.

| Area | Current State | Next Step |
|------|---------------|-----------|
| Responsible AI principles | Embedded in controls; not published as a standalone policy | Draft standalone RAI policy document for PetSure Australia Risk Management AI solutions |
| Challenge/appeal mechanism (DISR Guardrail 7) | No platform support | Define escalation pathway template for squads to implement |
| External transparency (DISR Guardrail 8) | Internal transparency strong via portal | Develop guidance for squads on user-facing AI disclosure |
| Data governance for training data | Out of platform scope; guidance provided at intake | Publish data governance checklist for squads |
| Third-party model governance | Re-evaluation trigger exists; no vendor risk register | Integrate vendor risk tracking into solution manifest |
| Regulatory change monitoring | Manual review | Establish process to monitor APRA/ASIC/DISR publications for AI-relevant updates |

---

## How This Document Relates to Other Platform Docs

| Doc | Relationship |
|-----|-------------|
| [07-compliance-as-code.md](07-compliance-as-code.md) | Defines the **operational controls** this framework requires. The compliance pipeline is the enforcement mechanism; this document is the policy layer above it. |
| [04-solution-lifecycle.md](04-solution-lifecycle.md) | Defines **when** governance applies (intake, assessment, production). This document defines **what** governance requires and **why**. |
| [06-guardrails.md](06-guardrails.md) | Defines the **guardrail implementations**. This document explains which risks and principles each guardrail satisfies. |
| [08-evaluation-harness.md](08-evaluation-harness.md) | Defines the **testing methodology**. This document explains the quality and fairness standards the testing must verify. |
| [10-observability.md](10-observability.md) | Defines the **tracing and logging infrastructure**. This document explains the audit and accountability requirements that infrastructure satisfies. |
| [14-controls-register.md](14-controls-register.md) | **Single-page index** of every AI-GOV control, mapping each to its enforcement layer, mitigated risks, regulatory alignment, and evidence location. The lookup table for auditors. |
