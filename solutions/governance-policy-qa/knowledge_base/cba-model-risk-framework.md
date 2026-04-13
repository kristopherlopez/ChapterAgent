# CBA Model Risk Management Framework

**Document ID:** GOV-AI-003
**Version:** 1.2
**Status:** Active
**Effective Date:** 1 April 2025
**Next Review Date:** 1 October 2025
**Owner:** Model Risk
**Approval Authority:** Head of Model Risk
**Classification:** Internal — Restricted

---

## 1. Purpose

This framework establishes the requirements for managing risk arising from the use of models across the Commonwealth Bank Group, with particular emphasis on models that incorporate artificial intelligence and machine learning techniques. It provides a structured approach to model development, validation, deployment, monitoring, and retirement that is proportionate to the risk each model presents.

Models are used extensively across the Group for credit decisioning, pricing, fraud detection, customer engagement, and operational optimisation. The increasing adoption of AI and machine learning introduces additional complexity: models may be less interpretable, more sensitive to data drift, and more difficult to validate using traditional techniques. This framework addresses those challenges while maintaining alignment with the Group's established model risk management practices.

This framework is subordinate to the CBA Group AI Policy (GOV-AI-001) and implements model-specific governance requirements referenced in that policy. Where this framework imposes requirements beyond those in GOV-AI-001, the stricter requirement applies.

## 2. Scope

This framework applies to:

- All models that use machine learning, deep learning, or generative AI techniques, regardless of whether they are developed in-house, procured from vendors, or provided by third parties.
- Traditional statistical models (logistic regression, generalised linear models, time series) that are registered on the AI governance platform.
- Ensemble and hybrid systems that combine traditional statistical methods with AI/ML components.
- Models in all lifecycle stages from initial development through to retirement.

This framework does **not** apply to:

- Deterministic rule-based systems that contain no learned parameters.
- Pure retrieval-augmented generation (RAG) systems that do not contain a fine-tuned or trained model component — these are governed as AI solutions under GOV-AI-001 but are not subject to the model-specific requirements in this framework unless they incorporate a scoring or classification model.
- Spreadsheet-based calculations that do not contain embedded model logic.

## 3. Definitions

| Term | Definition |
|------|-----------|
| **Model** | A quantitative method, system, or approach that applies statistical, economic, financial, or mathematical theories, techniques, and assumptions to process input data into quantitative estimates. For the purposes of this framework, this includes AI/ML models that learn from data to produce predictions, classifications, scores, or generated outputs. |
| **Model Risk** | The potential for adverse consequences from decisions based on incorrect or misused model outputs. Model risk arises from fundamental errors in the model, incorrect or inappropriate use of model outputs, or the use of models in contexts for which they were not designed or validated. |
| **Model Owner** | The individual accountable for the model's performance, compliance, and business outcomes. The model owner is typically the squad lead or product owner responsible for the AI solution that contains the model. |
| **Model Validator** | An individual or team independent of the model development team who assesses the model's conceptual soundness, implementation correctness, and ongoing performance. |
| **Model Card** | A structured document that records a model's purpose, architecture, training data, performance characteristics, limitations, and governance metadata. Model cards are mandatory for all models above experimental tier. |
| **Challenger Model** | An alternative model maintained alongside the production model to provide an independent benchmark for performance comparison and to facilitate model replacement when necessary. |
| **Model Risk Tier** | A classification that determines the intensity of model risk governance applied. Model risk tiers align with the AI solution risk tiers defined in GOV-AI-001. |

## 4. Model Risk Classification

### 4.1 Risk Tier Alignment

Model risk tiers are aligned with the AI solution risk tiers defined in GOV-AI-001 Section 5. The mapping is as follows:

| AI Solution Risk Tier | Model Risk Tier | Model Risk Label | Governance Intensity |
|----------------------|----------------|-----------------|---------------------|
| `experimental` | Tier 1 | Low | Basic documentation and monitoring |
| `production_internal` | Tier 2 | Medium | Full documentation, periodic validation, active monitoring |
| `production_customer_facing` | Tier 3 | High | Full documentation, independent validation, continuous monitoring, challenger model |

### 4.2 Additional Risk Factors

Beyond the base tier alignment, model risk may be elevated based on:

- **Materiality of decisions** — models that directly determine credit limits, pricing, or claim outcomes are inherently higher risk regardless of their AI solution tier.
- **Model complexity** — deep learning models, large language models, and ensemble methods carry higher inherent model risk than linear models due to reduced interpretability.
- **Data sensitivity** — models trained on or processing sensitive personal data (health, financial hardship, indigenous status) carry elevated risk.
- **Regulatory significance** — models subject to specific regulatory requirements (e.g., APRA's requirements for internal ratings-based credit models) are automatically classified as Tier 3.
- **Concentration risk** — models that are the sole basis for a high-volume automated decision process without human review.

The Head of Model Risk may override the default tier alignment where these additional factors warrant a higher classification. Downgrading from the default alignment requires documented justification and approval from the Head of Model Risk.

## 5. Model Lifecycle

### 5.1 Lifecycle Stages

Every model progresses through five lifecycle stages. Each stage has defined entry criteria, activities, and exit criteria.

| Stage | Entry Criteria | Key Activities | Exit Criteria |
|-------|---------------|----------------|---------------|
| **Development** | Approved use case, registered AI solution (AI-GOV-001) | Data preparation, feature engineering, model training, initial testing, model card creation | Model card complete, initial performance metrics documented |
| **Validation** | Development complete, model card available | Independent review (scope depends on tier), conceptual soundness assessment, implementation testing, performance benchmarking | Validation report issued, findings addressed |
| **Deployment** | Validation passed, all compliance gates passed (AI-GOV-001 Section 6) | Integration into production environment, A/B testing where applicable, monitoring activation | Model live in production, monitoring dashboards active |
| **Monitoring** | Model deployed to production | Performance tracking, drift detection, periodic re-validation, incident response | Ongoing — exits only to Retirement |
| **Retirement** | Replacement model deployed, or business decision to decommission | Output archival, audit trail preservation, model registry update, dependent system notification | Model removed from production, registry updated to "retired" |

### 5.2 Stage Transitions

Transitions between lifecycle stages require documented approval. The approval authority depends on the model risk tier:

| Transition | Tier 1 (Low) | Tier 2 (Medium) | Tier 3 (High) |
|-----------|-------------|-----------------|---------------|
| Development to Validation | Model Owner | Model Owner | Model Owner + Model Risk |
| Validation to Deployment | Model Owner | Model Risk | Model Risk + Head of Model Risk |
| Deployment to Monitoring | Automatic on deployment | Automatic on deployment | Model Risk sign-off |
| Monitoring to Retirement | Model Owner | Model Owner + Model Risk | Head of Model Risk |

## 6. Model Validation

### 6.1 Validation Independence

Model validation must be performed by individuals who are independent of the model development process. The degree of independence required varies by tier:

| Model Risk Tier | Validation Independence Requirement |
|----------------|--------------------------------------|
| Tier 1 (Low) | Peer review by a team member not directly involved in model development is sufficient. |
| Tier 2 (Medium) | Validation by the Model Risk team or an independent internal team with relevant expertise. The validator must not report to the same line manager as the model developer. |
| Tier 3 (High) | Validation by the Model Risk team is mandatory. For models with material financial impact (e.g., credit scoring, pricing), external independent validation may also be required at the discretion of the Head of Model Risk. |

### 6.2 Validation Scope

Model validation covers three domains:

**Conceptual Soundness**
- Is the modelling approach appropriate for the business problem?
- Are the assumptions reasonable and documented?
- Are the model's limitations understood and documented in the model card?
- For AI/ML models: is the choice of algorithm, architecture, and hyperparameters justified?

**Implementation Correctness**
- Has the model been implemented correctly?
- Are the data pipelines feeding the model accurate and complete?
- Does the model produce consistent outputs across environments (development, staging, production)?
- For AI/ML models: are the training, inference, and serving pipelines reproducible?

**Performance Assessment**
- Does the model meet the performance thresholds defined in the solution manifest?
- How does the model perform on out-of-sample data, edge cases, and adversarial inputs?
- For scoring models: AUC/Gini coefficient, calibration (Brier score, expected calibration error), discrimination metrics.
- For classification models: precision, recall, F1 score, confusion matrix analysis across demographic groups.
- For generative AI models: evaluation harness results as defined in GOV-AI-006.

### 6.3 Validation Reports

Every validation produces a structured validation report that includes:

1. Executive summary and overall recommendation (approve, approve with conditions, reject)
2. Scope of validation and limitations
3. Findings categorised by severity (critical, high, medium, low)
4. Benchmarking against alternative approaches or challenger models
5. Conditions or recommendations for ongoing monitoring
6. Sign-off by the lead validator

Validation reports are stored in the platform's evidence repository and linked to the solution's compliance evidence package.

### 6.4 Validation Triggers

Beyond the initial pre-deployment validation, re-validation is required when:

- The model is retrained on new data.
- The model's architecture or feature set changes materially.
- Performance monitoring detects drift beyond defined thresholds (see Section 7).
- The model's use case or scope changes.
- A material incident occurs involving the model.
- The periodic re-validation schedule is reached (Tier 2: annually, Tier 3: semi-annually).

## 7. Performance Monitoring

### 7.1 Monitoring Requirements by Tier

| Monitoring Requirement | Tier 1 (Low) | Tier 2 (Medium) | Tier 3 (High) |
|-----------------------|-------------|-----------------|---------------|
| Performance dashboards | Recommended | Required | Required |
| Automated alerting | Not required | Required (daily checks) | Required (real-time) |
| Population Stability Index (PSI) | Not required | Required (monthly) | Required (weekly) |
| Discrimination metric tracking | Not required | Required (monthly) | Required (weekly) |
| Calibration monitoring | Not required | Required (quarterly) | Required (monthly) |
| Drift detection | Recommended | Required | Required |
| Challenger model comparison | Not required | Recommended | Required |

### 7.2 Key Monitoring Metrics

**Scoring Models (Credit, Pricing, Risk)**

| Metric | Description | Alert Threshold (Tier 2) | Alert Threshold (Tier 3) |
|--------|-------------|--------------------------|--------------------------|
| AUC/Gini decay | Change in discriminatory power from validation baseline | > 5% relative decline | > 3% relative decline |
| PSI (Population Stability Index) | Shift in score distribution | > 0.20 | > 0.10 |
| Characteristic Stability Index (CSI) | Shift in individual feature distributions | > 0.25 | > 0.15 |
| Calibration drift | Difference between predicted and observed rates | > 10% relative deviation | > 5% relative deviation |
| Approval rate shift | Change in population-level approval rate | > 5 percentage points | > 3 percentage points |

**Classification Models**

| Metric | Description | Alert Threshold (Tier 2) | Alert Threshold (Tier 3) |
|--------|-------------|--------------------------|--------------------------|
| Accuracy decay | Drop in classification accuracy from baseline | > 5% absolute decline | > 3% absolute decline |
| Demographic parity gap | Difference in positive classification rates across groups | > 0.10 | > 0.05 |
| Equalised odds gap | Difference in true/false positive rates across groups | > 0.10 | > 0.05 |
| Confidence distribution shift | Change in model confidence score distribution | PSI > 0.20 | PSI > 0.10 |

**Generative AI Models**

Generative AI models are monitored through the platform's evaluation harness (GOV-AI-006) rather than traditional statistical monitoring. The re-evaluation cadences defined in GOV-AI-001 Section 8.3 apply: every 90 days for `production_internal`, every 30 days for `production_customer_facing`.

Additional monitoring for generative AI:
- Guardrail trigger rates tracked weekly; sustained increases trigger investigation.
- User feedback and escalation rates tracked where available.
- Citation coverage and faithfulness scores tracked per evaluation run.

### 7.3 Monitoring Escalation

When monitoring detects a breach of alert thresholds:

1. **Tier 2 models** — the model owner is notified and must investigate within 5 business days. If the investigation confirms material degradation, re-validation is triggered.
2. **Tier 3 models** — the model owner and Model Risk are notified immediately. Investigation must commence within 24 hours. The model owner must determine within 48 hours whether the model should remain in production, be constrained (e.g., reduced to shadow mode), or be replaced by the challenger model.

## 8. Challenger Model Requirements

### 8.1 When Challengers Are Required

Challenger models are required for all Tier 3 (High) models and recommended for Tier 2 (Medium) models. A challenger model provides:

- An independent benchmark for performance comparison.
- A ready replacement if the production model degrades or fails.
- Evidence that the chosen model is the best available approach.

### 8.2 Challenger Model Standards

Challenger models must:

- Be developed independently from the production model (different algorithm, different feature selection, or different training approach).
- Be maintained alongside the production model with regular performance comparisons.
- Be validated to the same standard as the production model before being designated as a challenger.
- Be deployable to production within 48 hours if the production model is taken offline.
- Have their performance comparison results documented in each periodic validation report.

### 8.3 Champion-Challenger Switching

The decision to switch from the current champion model to a challenger model requires:

- Documented evidence that the challenger outperforms the champion on the primary business metric.
- Validation report for the challenger model.
- Approval from Model Risk (Tier 2) or the Head of Model Risk (Tier 3).
- A parallel running period of at least 14 days (Tier 2) or 30 days (Tier 3) before the challenger becomes the new champion.

## 9. Model Inventory and Registration

### 9.1 Relationship to AI Solution Registration

All AI solutions must be registered per GOV-AI-001 and the AI Solution Registration Standard (GOV-AI-005). For solutions that contain models, the solution registration is extended with model-specific fields. This framework does not replace the AI solution registration — it augments it.

### 9.2 Model Inventory Fields

In addition to the standard solution manifest fields, model-containing solutions must include:

| Field | Description | Required From |
|-------|-------------|--------------|
| `model.type` | Model category: `scoring`, `classification`, `regression`, `generative`, `embedding`, `ensemble` | All tiers |
| `model.algorithm` | Primary algorithm or architecture (e.g., XGBoost, logistic regression, GPT-4, BERT) | All tiers |
| `model.framework` | Training/inference framework (e.g., scikit-learn, PyTorch, LangChain) | All tiers |
| `model.training_data_source` | Reference to training data lineage record | Tier 2+ |
| `model.training_date` | Date of most recent training or fine-tuning | Tier 2+ |
| `model.feature_count` | Number of input features | Tier 2+ (traditional ML) |
| `model.parameter_count` | Number of learned parameters | Tier 2+ (deep learning/LLM) |
| `model.baseline_metrics` | Performance metrics at time of validation | Tier 2+ |
| `model.challenger_model_id` | Reference to the challenger model, if applicable | Tier 3 |
| `model.validation_report_id` | Reference to most recent validation report | Tier 2+ |
| `model.next_validation_date` | Scheduled date for next periodic validation | Tier 2+ |
| `model.model_card_url` | Link to the model card document | Tier 2+ |

### 9.3 Model Card Requirements

Model cards must contain, at minimum:

1. **Model overview** — purpose, intended use, out-of-scope uses.
2. **Architecture description** — model type, key hyperparameters, training approach.
3. **Training data summary** — source, size, date range, known limitations, bias assessment.
4. **Performance summary** — key metrics, benchmark comparisons, performance across demographic groups.
5. **Limitations and risks** — known failure modes, scenarios where the model should not be used.
6. **Ethical considerations** — fairness assessment, potential for harm, mitigation measures.
7. **Governance metadata** — owner, validator, validation date, risk tier, next review date.

Model cards must be updated whenever the model is retrained, re-validated, or its use case changes.

## 10. Documentation Standards

### 10.1 Required Documentation by Tier

| Document | Tier 1 | Tier 2 | Tier 3 |
|----------|--------|--------|--------|
| Model card | Recommended | Required | Required |
| Validation report | Not required | Required | Required |
| Training data lineage | Recommended | Required | Required |
| Feature documentation | Recommended | Required | Required |
| Monitoring specification | Not required | Required | Required |
| Challenger model comparison | Not required | Recommended | Required |
| Incident response plan | Not required | Recommended | Required |

### 10.2 Documentation Retention

All model documentation must be retained for the lifetime of the model plus five years after retirement, in accordance with the CBA Data Governance Standard (GOV-AI-004) and APRA record-keeping requirements.

## 11. APRA Alignment

### 11.1 CPS 230 — Operational Risk Management

APRA's Prudential Standard CPS 230 requires authorised deposit-taking institutions to effectively manage operational risks, including risks arising from the use of models. This framework implements CPS 230 requirements as follows:

| CPS 230 Requirement | Framework Implementation |
|---------------------|--------------------------|
| Identify and assess operational risks | Model risk classification (Section 4), model inventory (Section 9) |
| Maintain effective controls | Compliance gates (GOV-AI-001 Section 6), validation requirements (Section 6), monitoring (Section 7) |
| Manage change effectively | Lifecycle stage transitions (Section 5.2), validation triggers (Section 6.4) |
| Business continuity | Challenger model requirements (Section 8), incident response per GOV-AI-001 Section 9 |
| Third-party risk management | Scope includes vendor and third-party models (Section 2) |

### 11.2 CPS 234 — Information Security

Models that process sensitive data must comply with APRA CPS 234 information security requirements. This is addressed through the CBA Data Governance Standard (GOV-AI-004) and the platform's PII validation gate (AI-GOV-005).

## 12. Related Documents

| Document | Relationship |
|----------|-------------|
| CBA Group AI Policy (GOV-AI-001) | Parent — this framework implements the model risk requirements of GOV-AI-001 |
| CBA Responsible AI Principles (GOV-AI-002) | Sibling — provides the fairness and ethics principles applied during model validation |
| CBA Data Governance Standard (GOV-AI-004) | Sibling — governs data used in model training, evaluation, and monitoring |
| CBA AI Solution Registration Standard (GOV-AI-005) | Sibling — defines the base solution registration that this framework extends |
| CBA AI Testing & Evaluation Framework (GOV-AI-006) | Sibling — defines the evaluation harness used for generative AI model monitoring |
| CBA Prompt Governance Guideline (GOV-AI-007) | Sibling — governs prompt management for generative AI models |
| APRA CPS 230 — Operational Risk Management | Regulatory — this framework implements CPS 230 model risk requirements |
| APRA CPS 234 — Information Security | Regulatory — referenced for data security requirements |
| APRA CPG 235 — Managing Data Risk (Draft) | Regulatory — anticipated guidance on data risk management for models |

## 13. Review and Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 1 January 2025 | Model Risk | Initial release aligned to GOV-AI-001 v1.0 |
| 1.1 | 1 April 2025 | Model Risk | Updated to align with GOV-AI-001 v2.0 risk tier system. Added challenger model requirements. Added APRA CPS 230 alignment section. |
| 1.2 | 1 April 2025 | Model Risk | Refined monitoring thresholds based on six months of operational experience. Added CSI metric. Clarified validation independence requirements for Tier 2 models. |
