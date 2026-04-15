# PetSure Australia AI Testing & Evaluation Framework

**Document ID:** GOV-AI-006
**Version:** 1.2
**Status:** Active
**Effective Date:** 1 April 2025
**Next Review Date:** 1 October 2025
**Owner:** Risk Management AI
**Approval Authority:** Head of Risk Management AI
**Classification:** Internal — Restricted

---

## 1. Purpose

This framework establishes the mandatory testing and evaluation requirements for all AI solutions governed by the PetSure Australia Group AI Policy (GOV-AI-001). It defines the composition, quality, and coverage standards for golden datasets; the evaluation metrics applicable to each solution type; the metric thresholds that vary by risk tier; the re-evaluation cadence for production solutions; and the technical architecture of the evaluation harness.

This framework exists because AI systems degrade silently. Unlike traditional software, where a defect produces an observable error, an AI system can drift in quality, develop bias, or produce subtly incorrect outputs without triggering any conventional alarm. Structured, repeatable evaluation is the primary defence against this failure mode. The framework ensures that every AI solution is measured against a defined quality bar before deployment and continuously thereafter.

This document is subordinate to GOV-AI-001 and implements the evaluation requirements described in Sections 5.2, 6.1 (Evaluation Harness gate, AI-GOV-003), and 8 of that policy.

## 2. Scope

This framework applies to all AI solutions registered on the PetSure Australia AI governance platform, including:

- Generative AI solutions (Q&A agents, conversational AI, document generation, summarisation)
- Classification solutions (intent detection, sentiment analysis, document classification, complaint routing)
- Scoring solutions (credit risk, fraud probability, propensity models, pricing models)
- Validation solutions (document verification, data quality assessment, compliance checking)

The framework applies from the point of solution registration through to retirement. Experimental-tier solutions are encouraged but not required to follow the full framework; production-tier solutions must comply fully.

## 3. Definitions

| Term | Definition |
|------|-----------|
| **Golden Dataset** | A curated, human-reviewed collection of test cases used to evaluate an AI solution's quality, safety, and compliance. Each case includes an input, expected behaviour or reference output, and metadata describing the case type and intent. |
| **Test Case** | A single entry in a golden dataset, consisting of an input (query, document, data record), an expected output or acceptable output range, case type tags, and guardrail expectations. |
| **Evaluation Harness** | The automated system that executes test cases against a solution, collects outputs, computes metrics, and produces a structured evaluation report. Built on DeepEval with PetSure Australia-specific extensions. |
| **Metric Threshold** | The minimum (or maximum, for inverse metrics) score a solution must achieve to pass a given metric at its assigned risk tier. |
| **Re-evaluation** | A scheduled or triggered repeat of the full evaluation harness run against the current golden dataset. Required at defined intervals for production solutions. |
| **Coverage** | The proportion of a solution's functional scope that is exercised by the golden dataset. Coverage is measured across scenario types, guardrail configurations, and input categories. |
| **Adversarial Test Case** | A test case specifically designed to probe failure modes: prompt injection, scope violations, hallucination triggers, bias-eliciting inputs, or edge-case formatting. |
| **DeepEval** | The open-source evaluation framework used as the foundation for the PetSure Australia evaluation harness. Provides metric implementations for faithfulness, answer relevancy, contextual precision, contextual recall, hallucination, bias, and toxicity. |

## 4. Golden Dataset Requirements

### 4.1 Minimum Case Counts by Risk Tier

Golden datasets must meet the following minimum size requirements, as mandated by GOV-AI-001 Section 5.2:

| Risk Tier | Minimum Cases | Sign-off Required | Notes |
|-----------|--------------|-------------------|-------|
| `experimental` | Recommended: 10+ | No | Golden datasets are encouraged for experimental solutions to establish evaluation baselines early. Not enforced by compliance gates. |
| `production_internal` | **30 cases minimum** | Yes — by a qualified reviewer independent of the development squad | Must include all case types defined in Section 4.3. |
| `production_customer_facing` | **50 cases minimum** | Yes — by a qualified reviewer independent of the development squad, plus Chapter Lead acknowledgement | Must include all case types defined in Section 4.3 with expanded adversarial coverage. |

### 4.2 Data Requirements

All golden dataset test cases must comply with the following:

1. **No real customer data.** All inputs, reference outputs, and context documents must use synthetic or appropriately anonymised data. This is enforced by compliance gate AI-GOV-005 (PII Validation).
2. **Representative of production.** Test cases must reflect the actual distribution and variety of inputs the solution receives in production. A dataset consisting entirely of happy-path queries is insufficient.
3. **Version-controlled.** Golden datasets must be stored in the solution's repository and versioned alongside the solution code. Changes to the golden dataset must be tracked and attributable.
4. **Timestamped.** Each test case must include a `created_date` field. Cases older than 12 months must be reviewed for continued relevance.
5. **Tagged by type.** Each test case must carry one or more type tags from the taxonomy defined in Section 4.3.

### 4.3 Test Case Types

Every golden dataset must include cases from the following categories. The minimum counts per category vary by risk tier.

| Case Type | Description | Min Cases (Internal) | Min Cases (Customer-Facing) |
|-----------|-------------|---------------------|---------------------------|
| **happy_path** | Standard, well-formed inputs that exercise the solution's primary function. Expected to produce correct, high-quality outputs. | 10 | 15 |
| **edge_case** | Unusual but valid inputs: ambiguous queries, partial information, uncommon formatting, multilingual input, long-form or very short inputs. | 5 | 10 |
| **adversarial** | Inputs designed to probe failure modes: prompt injection attempts, jailbreak patterns, out-of-scope requests disguised as in-scope, leading or manipulative phrasing. | 5 | 10 |
| **guardrail_specific** | Cases that specifically exercise each configured guardrail: scope refusal (out-of-scope query that should be refused), PII handling (input containing PII that should be detected), injection blocking (input with injection payload). Minimum one case per active guardrail. | 5 (1 per guardrail) | 10 (2 per guardrail) |
| **bias_probing** | Cases designed to detect differential treatment across demographic groups, protected attributes, or sensitive categories. See GOV-AI-002 for fairness definitions by solution type. | 5 | 5 |

### 4.4 Coverage Requirements

Golden datasets must demonstrate adequate coverage across the solution's functional scope:

| Coverage Dimension | Internal Requirement | Customer-Facing Requirement |
|--------------------|---------------------|-----------------------------|
| **Topic coverage** | At least 80% of the solution's declared knowledge domains must be exercised | At least 90% of declared knowledge domains |
| **Guardrail coverage** | At least 1 test case per active guardrail | At least 2 test cases per active guardrail |
| **Input format coverage** | Cases should include the primary input format | Cases must include all supported input formats |
| **Output format coverage** | At least 1 case per output format (e.g., short answer, detailed response, refusal) | At least 2 cases per output format |
| **Temporal coverage** | Where applicable, cases should include time-sensitive queries | Where applicable, cases must include time-sensitive queries with known correct answers at the time of dataset creation |

## 5. Evaluation Metrics

### 5.1 Metrics by Solution Type

The evaluation harness computes different metrics depending on the solution type declared in the solution manifest.

#### 5.1.1 Q&A Solutions

Q&A solutions (including RAG-based agents, policy Q&A, document Q&A, conversational assistants) are evaluated on:

| Metric | Source | Description |
|--------|--------|-------------|
| **faithfulness** | DeepEval | Measures whether the generated answer is factually consistent with the retrieved context. Penalises claims not supported by the source material. |
| **answer_relevancy** | DeepEval | Measures whether the generated answer addresses the user's question directly and completely. |
| **contextual_precision** | DeepEval | Measures whether the retrieval step ranks relevant documents higher than irrelevant ones. |
| **contextual_recall** | DeepEval | Measures whether all relevant documents for a query are successfully retrieved. |
| **hallucination** | DeepEval | Measures the proportion of generated claims that are fabricated (not present in any retrieved context). Inverse metric: lower is better. |
| **citation_coverage** | PetSure Australia Custom | Measures whether the generated answer provides citations for factual claims, and whether those citations are correct and traceable to source documents. |
| **boundary_adherence** | PetSure Australia Custom | Measures whether the solution correctly refuses out-of-scope queries, responds with appropriate disclaimers, and does not speculate beyond its knowledge base. |
| **temporal_accuracy** | PetSure Australia Custom | Measures whether time-sensitive information (effective dates, version numbers, review dates) is correctly represented in the output. |

#### 5.1.2 Classification Solutions

| Metric | Source | Description |
|--------|--------|-------------|
| **accuracy** | Standard | Overall classification accuracy across all classes. |
| **consistency** | PetSure Australia Custom | Given semantically equivalent inputs, the classification should be identical. Measures output stability under paraphrase. |
| **calibration** | Standard | Confidence scores should be well-calibrated: a prediction made with 80% confidence should be correct approximately 80% of the time. |
| **bias** | DeepEval | Differential classification rates across demographic groups or protected attributes. |
| **fairness** | PetSure Australia Custom | Solution-specific fairness metric as defined in GOV-AI-002. Default: equalised odds across demographic groups. |

#### 5.1.3 Scoring Solutions

| Metric | Source | Description |
|--------|--------|-------------|
| **discrimination** | Standard | AUC-ROC or Gini coefficient measuring the model's ability to rank-order risk. |
| **calibration_brier** | Standard | Brier score measuring alignment between predicted probabilities and observed outcomes. |
| **calibration_ece** | Standard | Expected Calibration Error measuring miscalibration across confidence bins. |
| **demographic_parity** | Standard | Approval rates across demographic groups should not differ by more than the defined threshold. |
| **equalised_odds** | Standard | True positive and false positive rates across demographic groups should not differ by more than the defined threshold. |
| **stability_psi** | Standard | Population Stability Index measuring distribution shift between development and current populations. |

#### 5.1.4 Validation Solutions

| Metric | Source | Description |
|--------|--------|-------------|
| **completeness** | PetSure Australia Custom | Measures whether the validation solution identifies all relevant issues in the input. |
| **severity_calibration** | PetSure Australia Custom | Measures whether the severity assigned to findings is appropriate relative to ground-truth severity labels. |
| **faithfulness** | DeepEval | Measures whether validation findings are supported by the evidence cited. |

### 5.2 Metric Thresholds by Risk Tier

The following thresholds define the minimum (or maximum, for inverse metrics) scores required for a solution to pass the Evaluation Harness compliance gate (AI-GOV-003).

#### 5.2.1 Q&A Solution Thresholds

| Metric | Experimental | Production Internal | Production Customer-Facing |
|--------|-------------|--------------------|-----------------------------|
| faithfulness | N/A | >= 0.85 | >= 0.90 |
| answer_relevancy | N/A | >= 0.80 | >= 0.85 |
| contextual_precision | N/A | >= 0.75 | >= 0.85 |
| contextual_recall | N/A | >= 0.75 | >= 0.85 |
| hallucination | N/A | <= 0.15 | <= 0.08 |
| citation_coverage | N/A | >= 0.85 | >= 0.95 |
| boundary_adherence | N/A | >= 0.90 | >= 0.95 |
| temporal_accuracy | N/A | >= 0.85 (where applicable) | >= 0.95 (where applicable) |

#### 5.2.2 Classification Solution Thresholds

| Metric | Experimental | Production Internal | Production Customer-Facing |
|--------|-------------|--------------------|-----------------------------|
| accuracy | N/A | >= 0.85 | >= 0.90 |
| consistency | N/A | >= 0.90 | >= 0.95 |
| calibration | N/A | <= 0.15 (ECE) | <= 0.10 (ECE) |
| bias | N/A | <= 0.10 | <= 0.05 |
| fairness (equalised odds gap) | N/A | <= 0.10 | <= 0.05 |

#### 5.2.3 Scoring Solution Thresholds

| Metric | Experimental | Production Internal | Production Customer-Facing |
|--------|-------------|--------------------|-----------------------------|
| discrimination (AUC) | N/A | >= 0.70 | >= 0.75 |
| calibration_brier | N/A | <= 0.25 | <= 0.20 |
| calibration_ece | N/A | <= 0.10 | <= 0.05 |
| demographic_parity (gap) | N/A | <= 0.10 | <= 0.05 |
| equalised_odds (gap) | N/A | <= 0.10 | <= 0.05 |
| stability_psi | N/A | <= 0.20 | <= 0.10 |

#### 5.2.4 Validation Solution Thresholds

| Metric | Experimental | Production Internal | Production Customer-Facing |
|--------|-------------|--------------------|-----------------------------|
| completeness | N/A | >= 0.85 | >= 0.90 |
| severity_calibration | N/A | >= 0.80 | >= 0.90 |
| faithfulness | N/A | >= 0.85 | >= 0.90 |

### 5.3 Threshold Override

Squads may request adjusted thresholds for specific metrics if they can demonstrate that the default thresholds are inappropriate for their use case. Threshold overrides require:

1. A written justification documenting why the default threshold does not apply
2. A proposed alternative threshold with evidence supporting its appropriateness
3. Approval from the Chapter Lead and the Head of Risk Management AI
4. The override documented in the solution manifest under the `evaluation.threshold_overrides` section

Threshold overrides are reviewed at each re-evaluation. They do not carry over automatically when a solution changes risk tier.

## 6. Re-evaluation Cadence

### 6.1 Scheduled Re-evaluation

Production solutions must be re-evaluated on a regular schedule, as mandated by GOV-AI-001 Section 8.3:

| Risk Tier | Cadence | Grace Period After Due Date |
|-----------|---------|----------------------------|
| `experimental` | No scheduled re-evaluation required | N/A |
| `production_internal` | Every 90 calendar days | 14 days |
| `production_customer_facing` | Every 30 calendar days | 7 days |

The platform tracks re-evaluation due dates and sends automated reminders at 14 days, 7 days, and 1 day before the due date. If the grace period expires without a passing re-evaluation, the solution is flagged as non-compliant and the squad has the remediation window defined in GOV-AI-001 Section 8.3 (14 days for customer-facing, 30 days for internal).

### 6.2 Triggered Re-evaluation

In addition to scheduled re-evaluation, a full evaluation harness run must be triggered immediately when any of the following occur:

| Trigger Event | Rationale |
|---------------|-----------|
| Model update or swap | A new model version may produce different outputs across the entire test surface |
| System prompt change | Prompt modifications can materially alter output quality, tone, and boundary adherence |
| Knowledge base update | New or modified source documents change the ground truth that the solution operates against |
| Guardrail configuration change | Modified guardrails may alter the solution's behaviour on previously passing cases |
| Risk tier change | A tier change introduces new thresholds; the solution must be verified against them |
| Post-incident remediation | After an AI incident, the fix must be validated against the full golden dataset |
| Golden dataset update | If the golden dataset itself is modified (cases added, removed, or changed), the evaluation must be re-run to establish a new baseline |

### 6.3 Re-evaluation Scope

All re-evaluations run the complete evaluation harness. Partial re-evaluation (running only a subset of test cases or metrics) is not supported. This prevents the introduction of gaps where degradation in one area is masked by selective testing.

## 7. Evaluation Harness Architecture

### 7.1 Technology Stack

The evaluation harness is built on the following components:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Metric Engine** | DeepEval (Python) | Provides implementations for faithfulness, answer_relevancy, contextual_precision, contextual_recall, hallucination, bias, and toxicity metrics |
| **Custom Metrics** | PetSure Australia Platform Extensions | Provides implementations for citation_coverage, boundary_adherence, temporal_accuracy, consistency, completeness, severity_calibration, and fairness metrics |
| **Test Runner** | Platform Compliance Runner | Orchestrates test case execution, collects outputs, dispatches to metric calculators, aggregates results |
| **Evidence Store** | Platform Evidence API | Stores structured evaluation results for audit and compliance gate enforcement |
| **LLM Judge** | Configurable (GPT-4o / Claude Sonnet) | Used by DeepEval metrics that require LLM-as-judge evaluation (faithfulness, answer_relevancy, hallucination) |

### 7.2 Execution Flow

1. **Load** — The harness loads the golden dataset from the solution's repository, validates its structure, and checks minimum case counts against the solution's risk tier.
2. **Execute** — Each test case is sent to the solution under evaluation. The solution's response, any retrieved context, trace data, and guardrail results are captured.
3. **Evaluate** — Captured outputs are passed to the metric engine. DeepEval metrics and custom metrics are computed in parallel where possible. LLM-as-judge metrics are batched to manage cost and latency.
4. **Aggregate** — Per-case metric scores are aggregated to produce solution-level scores. Aggregation uses the arithmetic mean by default. Weighted aggregation may be configured in the solution manifest.
5. **Gate** — Aggregated scores are compared against risk-tier thresholds. Each metric produces a pass/fail result. The overall gate passes only if all applicable metrics pass.
6. **Report** — A structured evaluation report is generated and stored in the evidence store. The report includes per-case results, aggregated scores, pass/fail status, and metadata (timestamp, harness version, LLM judge model, golden dataset version).

### 7.3 LLM-as-Judge Configuration

Several DeepEval metrics rely on an LLM to act as a judge (evaluating whether a response is faithful, relevant, or hallucinatory). The judge model is configured at the platform level and must meet the following requirements:

- The judge model must not be the same model used by the solution under evaluation, to avoid self-evaluation bias.
- The judge model must be from the platform's approved model list.
- Judge model changes are versioned and recorded in evaluation reports to ensure reproducibility.
- If the judge model is unavailable, the evaluation harness must fail rather than skip LLM-judged metrics.

## 8. Evaluation Report Format

Every evaluation harness run produces a structured report with the following sections:

| Section | Contents |
|---------|----------|
| **Summary** | Solution ID, risk tier, golden dataset version, overall pass/fail, timestamp, harness version |
| **Metric Results** | Per-metric: score, threshold, pass/fail, number of cases evaluated, confidence interval |
| **Per-Case Results** | Per test case: input, expected output, actual output, per-metric scores, guardrail results, pass/fail |
| **Failures** | Filtered view of all failing cases with failure reasons and metric breakdowns |
| **Configuration** | Evaluation parameters: judge model, aggregation method, threshold overrides, custom metric configuration |
| **Comparison** | If a previous evaluation exists, a delta comparison showing metric movements and any regressions |

Reports are stored as JSON in the platform evidence store and are included in the compliance evidence package exportable via the `GET /api/evidence/{id}/download` endpoint.

## 9. Related Documents

| Document | Relationship |
|----------|-------------|
| PetSure Australia Group AI Policy (GOV-AI-001) | Parent — this framework implements evaluation requirements from Sections 5.2, 6.1, and 8 |
| PetSure Australia Responsible AI Principles (GOV-AI-002) | Peer — defines fairness metrics and bias testing requirements referenced by this framework |
| PetSure Australia AI Solution Registration Standard (GOV-AI-005) | Peer — defines the solution manifest schema including evaluation configuration fields |
| PetSure Australia Prompt Governance Guideline (GOV-AI-007) | Peer — prompt changes trigger re-evaluation as defined in Section 6.2 of this framework |
| DeepEval Documentation | Reference — technical documentation for the evaluation metric library |
| APRA CPS 230 — Operational Risk Management | Regulatory — evaluation cadence supports continuous risk monitoring obligations |

## 10. Review and Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 1 April 2025 | Risk Management AI | Initial release aligned to GOV-AI-001 v2.0 |
| 1.1 | 15 May 2025 | Risk Management AI | Added scoring solution metrics (PSI, demographic parity, equalised odds). Clarified LLM-as-judge requirements. |
| 1.2 | 1 July 2025 | Risk Management AI | Updated customer-facing hallucination threshold from <= 0.10 to <= 0.08. Added triggered re-evaluation for golden dataset updates. Aligned to GOV-AI-001 v2.1 incident response requirements. |
