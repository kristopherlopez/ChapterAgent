# Controls Register

This is the single-page index of every automated control in the platform. It exists for one audience: anyone who needs to answer "what controls exist, where do they run, what risks do they cover, and which regulations do they satisfy?"

This document is a lookup table, not a narrative. For implementation detail, follow the links to the source docs.

---

## Control Index

| Control ID | Control Name | What It Enforces | Enforcement Layer | Control Type | Risk(s) Mitigated | Regulatory Alignment | Source Doc |
|------------|-------------|------------------|-------------------|-------------|-------------------|---------------------|------------|
| AI-GOV-001 | Solution Registration | Every AI solution must be registered with complete metadata, risk tier, and named owner | Layer 1 (Deployment Gate) | Preventive | AIR-012 | CPS 230 (risk identification), DISR #1 (accountability) | [07](07-compliance-as-code.md) |
| AI-GOV-002 | Risk Tier Assignment | Every solution must be assigned a risk tier that determines threshold strictness, guardrail scope, and re-evaluation frequency | Layer 1 (Deployment Gate) | Preventive | AIR-012 | CPS 230 (risk assessment), CPS 234 (asset classification), DISR #2 (risk management) | [04](04-solution-lifecycle.md), [13](13-governance-framework.md) |
| AI-GOV-003 | Quality Thresholds | Solutions must pass evaluation metrics (faithfulness, relevancy, precision, recall, hallucination) at or above their risk tier's thresholds | Layer 1 (Deployment Gate) + Layer 2 (Production) | Preventive + Detective | AIR-001, AIR-007 | CPS 234 (control effectiveness testing), DISR #4 (testing) | [07](07-compliance-as-code.md), [08](08-evaluation-harness.md) |
| AI-GOV-004 | Content Safety | Solutions must not produce toxic, harmful, or dangerous content; toxicity score must be within risk-tier threshold | Layer 1 (Deployment Gate) + Layer 2 (Production) | Preventive + Detective | AIR-005 | DISR #3 (data governance), DISR #4 (testing) | [06](06-guardrails.md), [08](08-evaluation-harness.md) |
| AI-GOV-005 | PII Protection | Zero PII in AI solution outputs; Presidio NER detection on every response | Layer 1 (Deployment Gate) + Layer 2 (Production) | Preventive + Detective | AIR-003 | CPS 234 (information security), DISR #3 (data governance) | [06](06-guardrails.md), [07](07-compliance-as-code.md) |
| AI-GOV-006 | Guardrail Validation | All guardrails (scope, injection, content safety) must pass their test suite before deployment | Layer 1 (Deployment Gate) | Preventive | AIR-004, AIR-005, AIR-006 | CPS 234 (control effectiveness testing), DISR #4 (testing) | [06](06-guardrails.md), [07](07-compliance-as-code.md) |
| AI-GOV-007 | Bias & Fairness | Solutions must not exhibit systematic demographic bias; bias score must be within risk-tier threshold | Layer 1 (Deployment Gate) + Layer 2 (Production) | Preventive + Detective | AIR-002 | DISR #4 (testing), CBA Group AI Policy (fairness) | [06](06-guardrails.md), [08](08-evaluation-harness.md) |
| AI-GOV-008 | Audit Trail Completeness | 100% of interactions must have complete trace fields (query, retrieval, generation, guardrails, response) | Layer 1 (Deployment Gate) + Layer 2 (Production) | Detective | AIR-008 | CPS 230 (monitoring & reporting), DISR #9 (records) | [07](07-compliance-as-code.md), [10](10-observability.md) |
| AI-GOV-009 | Golden Dataset Sign-Off | Human reviewer must approve the golden dataset with identity and date recorded | Layer 1 (Deployment Gate) | Preventive | AIR-011 | DISR #5 (human control), DISR #10 (conformity assessment) | [07](07-compliance-as-code.md) |
| AI-GOV-010 | Prompt Governance | System prompts must be version-controlled with linked approval commits; prompt hash change triggers re-evaluation | Layer 1 (Deployment Gate) | Preventive | AIR-009 | CPS 230 (operational risk controls), DISR #9 (records) | [07](07-compliance-as-code.md) |

---

## Runtime Guardrails (Layer 2 Detail)

These controls run on every production response. They are the real-time enforcement of the policies above.

| Guardrail | AI-GOV Control | Implementation | Latency Target | On Failure |
|-----------|---------------|----------------|---------------|------------|
| Scope Adherence | AI-GOV-006 | Custom classifier (query classification before retrieval) | 12ms | Block; serve refusal |
| Prompt Injection Detection | AI-GOV-006 | Pattern matching + classifier (input validation before LLM call) | ~10ms | Block |
| PII Scan | AI-GOV-005 | Presidio NER (PERSON, EMAIL, PHONE, AU_ABN, AU_TFN, AU_MEDICARE) | 15ms | Block; alert immediately |
| Citation Coverage | AI-GOV-003 | Custom metric (all claims traceable to source documents) | 8ms | Block if below threshold |
| Faithfulness | AI-GOV-003 | DeepEval FaithfulnessMetric, judge: gpt-4o-mini | 145ms | Regenerate with stricter grounding |
| Bias | AI-GOV-007 | DeepEval BiasMetric | 130ms | Block |
| Toxicity | AI-GOV-004 | DeepEval ToxicityMetric | 125ms | Block; alert immediately |
| Audit Trail | AI-GOV-008 | Custom logging (structured spans to immutable store) | 5ms | Serve but flag |

Total latency budget: < 200ms per response.

---

## Risk-to-Control Mapping

Every risk in the [AI Risk Register](13-governance-framework.md) maps to at least one automated control.

| Risk ID | Risk | Controls | Residual Risk |
|---------|------|----------|---------------|
| AIR-001 | Hallucination | AI-GOV-003 (faithfulness threshold + citation coverage) | Low |
| AIR-002 | Bias & Discrimination | AI-GOV-007 (BiasMetric gate + real-time monitoring) | Low |
| AIR-003 | PII Leakage | AI-GOV-005 (Presidio zero-tolerance gate + per-response scan) | Very Low |
| AIR-004 | Prompt Injection | AI-GOV-006 (injection detection guardrail + input validation) | Low |
| AIR-005 | Toxic Content | AI-GOV-004 (ToxicityMetric gate + real-time), AI-GOV-006 (content safety guardrail) | Very Low |
| AIR-006 | Scope Creep | AI-GOV-006 (scope adherence guardrail, blocks + serves refusal) | Very Low |
| AIR-007 | Model Drift | AI-GOV-003 (drift monitoring, 7-day rolling avg, 90-day re-eval) | Low |
| AIR-008 | Audit Trail Gaps | AI-GOV-008 (tracing SDK, 100% completeness requirement) | Very Low |
| AIR-009 | Uncontrolled Prompt Changes | AI-GOV-010 (prompt version control + approval + re-eval trigger) | Low |
| AIR-010 | Third-Party Model Changes | AI-GOV-003 (model change detection triggers mandatory re-eval) | Medium |
| AIR-011 | Insufficient Test Coverage | AI-GOV-009 (chapter review + human sign-off + coverage analysis) | Low |
| AIR-012 | Unauthorised Deployment | AI-GOV-001 + AI-GOV-002 (8-check deployment gate blocks on any failure) | Very Low |

---

## Regulatory Alignment Summary

How the platform's controls satisfy each external framework requirement.

### APRA CPS 230 (Operational Risk Management)

| CPS 230 Requirement | Controls | Evidence |
|----------------------|----------|----------|
| Identify and assess operational risks | AI-GOV-001, AI-GOV-002 | Risk register, risk tier in solution manifest |
| Maintain effective controls | AI-GOV-003 through AI-GOV-010 | Deployment gate reports, production compliance logs |
| Monitor and report on operational risk | AI-GOV-003, AI-GOV-007, AI-GOV-008 | Portfolio dashboard, drift alerts, compliance health summary |
| Manage third-party risks | AI-GOV-003 (re-eval on model change) | Re-evaluation reports, vendor tracking in manifest |
| Business continuity | AI-GOV-004, AI-GOV-005, AI-GOV-006 | Response blocking/regeneration on failure (graceful degradation) |

### APRA CPS 234 (Information Security)

| CPS 234 Requirement | Controls | Evidence |
|----------------------|----------|----------|
| Classify information assets | AI-GOV-002 | Risk tier assignment in solution manifest |
| Controls commensurate with risk | AI-GOV-002 (thresholds scale with tier) | Per-tier threshold config, gate results |
| Detect and respond to security incidents | AI-GOV-005, AI-GOV-006 | Compliance event log (security events filter) |
| Test control effectiveness | AI-GOV-003, AI-GOV-006 | Evaluation scorecards, guardrail test results |

### DISR AI Safety Standard (10 Guardrails)

| # | DISR Guardrail | Controls | Status |
|---|----------------|----------|--------|
| 1 | Accountability | AI-GOV-001 (named owner, risk tier, chapter oversight) | Addressed |
| 2 | Risk management | AI-GOV-002 (risk register, tier framework, risk-proportionate controls) | Addressed |
| 3 | Data governance & protection | AI-GOV-005 (PII detection), AI-GOV-006 (scope, injection) | Partially addressed |
| 4 | Testing | AI-GOV-003 (eval harness), AI-GOV-006 (guardrail tests), AI-GOV-004 (toxicity) | Addressed |
| 5 | Human control | AI-GOV-002 (risk tier conversation), AI-GOV-009 (golden dataset sign-off) | Addressed |
| 6 | Inform end users | AI-GOV-003 (citation coverage guardrail enables transparency) | Partially addressed |
| 7 | Challenge processes | No platform control; requires organisational process | Gap |
| 8 | Transparency | AI-GOV-001 (solution registry), AI-GOV-008 (evidence export) | Partially addressed |
| 9 | Record keeping | AI-GOV-008 (audit trail), AI-GOV-010 (prompt versioning) | Addressed |
| 10 | Conformity assessments | AI-GOV-003 (deployment gate), AI-GOV-003 (scheduled re-eval) | Addressed |

---

## Thresholds by Risk Tier

Controls enforce different thresholds depending on the solution's risk tier.

| Control | Metric | Experimental | Production Internal | Production Customer-Facing |
|---------|--------|-------------|--------------------|-----------------------------|
| AI-GOV-003 | Faithfulness | Logged only | >= 0.80 | >= 0.90 |
| AI-GOV-003 | Answer Relevancy | Logged only | >= 0.75 | >= 0.85 |
| AI-GOV-003 | Hallucination | Logged only | <= 0.15 | <= 0.10 |
| AI-GOV-004 | Toxicity | Logged only | <= 0.05 | <= 0.02 |
| AI-GOV-005 | PII | Logged only | Zero tolerance | Zero tolerance |
| AI-GOV-007 | Bias | Logged only | <= 0.10 | <= 0.05 |
| AI-GOV-008 | Audit completeness | Best effort | 100% | 100% |
| AI-GOV-003 | Re-evaluation frequency | None | 90 days | 30 days |

---

## Incident Response by Control

When a control detects a violation, the response depends on the control and severity.

| Control | Event | Automated Response | Escalation |
|---------|-------|--------------------|------------|
| AI-GOV-005 | PII detected in output | Response blocked, PII redacted | Immediate alert to owner + chapter lead |
| AI-GOV-004 | Toxicity detected | Response blocked | Immediate alert to owner + chapter lead |
| AI-GOV-007 | Bias threshold exceeded | Response blocked | Alert to owner + chapter lead |
| AI-GOV-003 | Faithfulness below threshold | Response regenerated (stricter grounding) | Escalated if retry also fails |
| AI-GOV-006 | Scope violation | Response blocked, refusal served | Escalated if > 5 in 1 hour |
| AI-GOV-006 | Prompt injection detected | Response blocked | Logged as security event |
| AI-GOV-008 | Audit trail incomplete | Response served but flagged | Alert to chapter lead |
| AI-GOV-003 | 7-day faithfulness declining | Dashboard moves to AMBER | Alert to squad + chapter lead |
| AI-GOV-003 | Any metric crosses hard threshold | Dashboard moves to RED | Chapter lead notified; solution flagged for re-eval |

### Escalation SLAs

| Severity | Examples | Response Time | Resolution Time |
|----------|---------|---------------|-----------------|
| Critical | PII leakage, toxicity, sustained RED | 1 hour | 24 hours |
| High | Bias failure, faithfulness retry failure | 4 hours | 48 hours |
| Medium | Drift warning, scope violations | 24 hours | 5 business days |
| Low | Minor threshold approach | Next review cycle | Next scheduled re-evaluation |

---

## Evidence Locations

Where to find evidence for each control in the [evidence export package](07-compliance-as-code.md).

| Control | Evidence Location in Export |
|---------|---------------------------|
| AI-GOV-001 | `1-solution-metadata/registration.json` |
| AI-GOV-002 | `1-solution-metadata/risk-tier-assignment.json` |
| AI-GOV-003 | `2-deployment-evidence/evaluation-scorecard.json`, `5-production-monitoring/compliance-health-summary.json` |
| AI-GOV-004 | `4-guardrail-evidence/bias-toxicity-report.json`, `5-production-monitoring/compliance-events.jsonl` |
| AI-GOV-005 | `4-guardrail-evidence/pii-test-results.json`, `5-production-monitoring/compliance-events.jsonl` |
| AI-GOV-006 | `4-guardrail-evidence/guardrail-test-results.json` |
| AI-GOV-007 | `4-guardrail-evidence/bias-toxicity-report.json`, `5-production-monitoring/compliance-events.jsonl` |
| AI-GOV-008 | `6-audit-trail/audit-completeness.json`, `6-audit-trail/interaction-sample.jsonl` |
| AI-GOV-009 | `3-golden-dataset/signoff-record.json`, `3-golden-dataset/coverage-analysis.json` |
| AI-GOV-010 | `7-prompt-governance/prompt-versions.json`, `7-prompt-governance/change-log.json` |

---

## How This Document Relates to Other Platform Docs

This register is a cross-reference, not a source of truth. The source docs are:

| Doc | What it defines |
|-----|----------------|
| [04-solution-lifecycle.md](04-solution-lifecycle.md) | When controls apply (intake, assessment, production) |
| [06-guardrails.md](06-guardrails.md) | Guardrail implementations (scope, injection, PII, action boundaries) |
| [07-compliance-as-code.md](07-compliance-as-code.md) | Three-layer enforcement pipeline (gates, monitoring, evidence) |
| [08-evaluation-harness.md](08-evaluation-harness.md) | Metric definitions, DeepEval integration, threshold configuration |
| [10-observability.md](10-observability.md) | Tracing infrastructure and audit logging |
| [13-governance-framework.md](13-governance-framework.md) | Policy layer, risk register, responsible AI principles, regulatory alignment |
