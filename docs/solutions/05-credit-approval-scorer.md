# Demo Solution #5: Credit Approval Scorer (Australian)

## What This Is

An ML scoring model that predicts whether a credit application should be approved or denied. Uses anonymised features from real Australian credit data to output an approval probability with feature contributions.

This solution uses the **Australian Credit Approval** dataset from the UCI ML Repository — the only publicly available Australian credit dataset. It's small (690 records) but symbolically significant: "we started with Australian data."

## Why This Solution

Two reasons:

1. **Australian data** — in a CBA interview, using Australian credit data signals awareness of the local regulatory and market context. APRA, ASIC, Privacy Act, anti-discrimination law — these all apply differently in Australia than elsewhere.
2. **Anonymised features** — the dataset's attributes are anonymised (A1-A14), which is itself a governance practice. It demonstrates data minimisation: the model works without knowing what the features represent, and the platform governs it the same way.

## The Dataset

**Australian Credit Approval Dataset** (UCI Machine Learning Repository — Statlog)

| Attribute | Detail |
|---|---|
| Source | UCI ML Repository (Statlog project) |
| Records | 690 |
| Features | 14 (6 continuous, 8 categorical — all anonymised) |
| Target | Approved (+) or denied (-) (binary) |
| Approval rate | ~44% |
| Origin | Australian financial institution |

### Feature Summary

All attribute names are anonymised to protect confidentiality. This is the dataset as published:

| Feature | Type | Values |
|---|---|---|
| A1 | Categorical | b, a |
| A2 | Continuous | Numeric |
| A3 | Continuous | Numeric |
| A4 | Categorical | u, y, l, t |
| A5 | Categorical | g, p, gg |
| A6 | Categorical | c, d, cc, i, j, k, m, r, q, w, x, e, aa, ff |
| A7 | Continuous | Numeric |
| A8 | Categorical | t, f |
| A9 | Categorical | t, f |
| A10 | Continuous | Numeric |
| A11 | Categorical | t, f |
| A12 | Categorical | s, g, p |
| A13 | Continuous | Numeric |
| A14 | Continuous | Numeric |

### Protected Attributes

The anonymisation creates a governance challenge: **we don't know which features are protected attributes**. This is realistic — in production, proxy discrimination occurs through features that correlate with demographics even when demographic data isn't directly used.

| Governance Approach | Method |
|---|---|
| Proxy detection | Statistical testing for features that correlate with approval/denial patterns in ways that suggest demographic proxies |
| Cluster fairness | Check whether approval rates differ significantly across natural clusters in the feature space |
| Anonymisation as governance | The dataset itself demonstrates data minimisation — a model that works without demographic data has a stronger compliance posture |

## The Scenario

A squad in Consumer Lending builds a credit approval model for personal loan applications. The model scores incoming applications and recommends approve/deny. A human credit officer makes the final decision, but the model's recommendation strongly influences the outcome.

### Risk Tier

**`production_internal`** — supports human decisions. The credit officer sees the recommendation and acts on it. If the model were making autonomous approval decisions, it would be `production_customer_facing`.

## The Model

**Approach:** Logistic regression (scikit-learn). With only 690 records and 14 features, a simple linear model is the appropriate choice. Gradient boosting would overfit.

**Training:** Stratified 70/30 split. 483 train, 207 test. Trains in milliseconds.

**Why this is still useful for the demo:** The small dataset makes every governance concept fast to demonstrate — discrimination probes run instantly, calibration curves compute in milliseconds, SHAP values are immediate. The governance story doesn't require a large dataset.

### Model Output Schema

```json
{
  "scoring_id": "SCR-AU-2026-0001",
  "application_id": "APP-001",
  "input_features": {
    "A1": "b",
    "A2": 30.83,
    "A3": 0.0,
    "A4": "u",
    "A5": "g",
    "A6": "w",
    "A7": 1.25,
    "A8": "t",
    "A9": "t",
    "A10": 1,
    "A11": "f",
    "A12": "g",
    "A13": 202,
    "A14": 0
  },
  "output": {
    "approval_probability": 0.73,
    "recommendation": "APPROVE",
    "confidence_band": "HIGH"
  },
  "explainability": {
    "method": "SHAP",
    "top_contributors": [
      { "feature": "A9", "direction": "supports_approval", "shap_value": 0.18 },
      { "feature": "A10", "direction": "supports_approval", "shap_value": 0.09 },
      { "feature": "A14", "direction": "supports_denial", "shap_value": -0.06 },
      { "feature": "A7", "direction": "supports_approval", "shap_value": 0.04 }
    ],
    "baseline_probability": 0.44
  },
  "guardrail_results": {
    "proxy_discrimination_check": "pass",
    "calibration_check": "pass",
    "explainability_check": "pass"
  },
  "metadata": {
    "model_version": "1.0.0",
    "model_type": "LogisticRegression",
    "dataset_origin": "Australian (UCI Statlog)",
    "training_date": "2026-04-01",
    "inference_latency_ms": 2
  }
}
```

## Guardrails

### 1. Proxy Discrimination

Without knowing which features are demographic, the platform must detect discrimination through proxies.

- **Check:** For each binary/categorical feature, compute approval rate difference between groups. Flag features where approval rates diverge beyond tolerance after controlling for other features.
- **Method:** Conditional independence testing, mutual information between features and outcome, subgroup analysis
- **Failure mode:** Feature A1 (binary: a/b) has an approval rate of 62% for "b" and 31% for "a". If A1 is a gender proxy, this is discrimination. If A1 is a legitimate risk factor, it's not — but the model can't prove which.
- **Enforcement:** Flag features with high conditional dependence on outcome. Require human review of flagged features before deployment.

### 2. Calibration

With only 690 records, calibration is harder to measure precisely — but still critical.

- **Check:** Predicted probabilities align with observed approval rates
- **Method:** Brier score, Hosmer-Lemeshow test (better for small samples), calibration curve
- **Failure mode:** Model outputs 0.90 approval probability for a segment that's actually approved 55% of the time.
- **Enforcement:** Calibration metrics on holdout set. Poor calibration → warning (not block, given sample size constraints).

### 3. Small Sample Governance

The dataset is small. The platform must account for this — metrics are less reliable, confidence intervals are wider.

- **Check:** Bootstrap confidence intervals on all metrics. Report metric ± uncertainty, not just point estimates.
- **Method:** 1000 bootstrap iterations on test set. 95% confidence intervals.
- **Failure mode:** AUC is 0.78 but the 95% CI is [0.65, 0.91]. The point estimate looks good; the uncertainty is too wide for production.
- **Enforcement:** Report uncertainty alongside every metric. Wide confidence intervals trigger a warning: "performance is within threshold but sample size limits confidence."

### 4. Explainability

Same as Solution #4 — every score must be accompanied by SHAP values.

- **Check:** SHAP values computed for every prediction
- **Method:** SHAP LinearExplainer (logistic regression)
- **Additional concern:** With anonymised features, SHAP values say "A9 was the biggest contributor" — but the credit officer doesn't know what A9 is. The platform flags this: "explainability is present but may not be interpretable to end users."

## Evaluation Harness

### Metrics

| Metric | Method | Threshold (production_internal) | Note |
|---|---|---|---|
| AUC-ROC | sklearn | ≥ 0.70 | Report with 95% CI |
| Gini Coefficient | 2 × AUC - 1 | ≥ 0.40 | Report with 95% CI |
| Brier Score | sklearn | ≤ 0.25 | Relaxed vs Solution #4 due to sample size |
| Hosmer-Lemeshow | statsmodels | p > 0.05 | Better calibration test for small samples |
| Subgroup Approval Rate Variance | Custom | Flag if > 0.15 | Proxy discrimination indicator |
| SHAP Coverage | Custom | 100% | Every prediction explained |
| Bootstrap CI Width (AUC) | Custom | Report only | Flags if CI > 0.20 |

## Golden Dataset

207 records (30% holdout). Small, but structured for governance testing.

### Test Partitions

| Partition | Records | Purpose |
|---|---|---|
| Performance holdout | 150 | AUC, Gini, calibration |
| Proxy probes | 30 | Subgroup analysis across categorical features |
| Edge cases | 15 | Boundary scores (0.45-0.55 probability range) |
| Bootstrap sample | 207 (full) | Confidence interval computation |

## Demo Scenarios

### Scenario 1: Happy Path — Clear Approval

**Input:** Application with strong indicators across features.

**What happens:** Model scores 0.82 (APPROVE with high confidence). SHAP shows A9 and A10 as primary contributors. Guardrails pass.

**Point:** The model works on Australian data, with Australian-origin features.

### Scenario 2: Proxy Discrimination Flag

**Input:** Subgroup analysis across feature A1 (binary categorical).

**What happens:** Approval rate for A1="b" is 62%, for A1="a" is 31%. Platform flags: "Feature A1 shows significant approval rate disparity. Human review required — is this a legitimate risk factor or a demographic proxy?"

**Point:** When features are anonymised, the platform can't definitively say "this is gender discrimination" — but it can say "this feature behaves like a proxy." That flag is the governance control.

### Scenario 3: Uncertainty Warning

**Input:** Full holdout set performance evaluation.

**What happens:** AUC is 0.78 but bootstrap 95% CI is [0.67, 0.89]. Platform reports: "Performance meets threshold (0.78 ≥ 0.70) but confidence interval width is 0.22 — sample size limits precision. Consider expanded validation before production deployment."

**Point:** The platform adapts governance to data constraints. Small datasets get uncertainty-aware evaluation.

### Scenario 4: Anonymisation as Governance

**Demo talking point:** "Notice the features are A1 through A14 — no names, no descriptions. This dataset was anonymised at source. The model works without knowing what the features represent. That's data minimisation in action. The platform governs the model's behaviour — fairness, calibration, explainability — without needing to know the underlying data semantics."

## Solution Manifest

```yaml
# solution.yaml
solution:
  name: "Australian Credit Approval Scorer"
  id: "credit-approval-au"
  type: "scoring"
  category: "ml"
  version: "1.0.0"
  description: "Predicts credit approval probability using anonymised Australian credit data"

risk_tier: "production_internal"

dataset:
  source: "UCI Machine Learning Repository — Statlog (Australian Credit Approval)"
  origin: "Australia"
  records: 690
  features: 14
  target: "class"
  protected_attributes: "unknown (anonymised)"
  small_sample: true

model:
  type: "LogisticRegression"
  framework: "scikit-learn"
  explainability: "SHAP"
  training_split: 0.7

guardrails:
  proxy_discrimination:
    method: "subgroup_approval_rate_analysis"
    flag_threshold: 0.15
    human_review_required: true
  calibration:
    brier_score_threshold: 0.25
    hosmer_lemeshow_p: 0.05
  explainability:
    method: "SHAP"
    coverage: 1.0
    interpretability_warning: true
  small_sample:
    bootstrap_iterations: 1000
    ci_level: 0.95
    ci_width_warning: 0.20

evaluation:
  holdout_size: 0.3
  metrics:
    - name: "auc_roc"
      threshold: 0.70
      report_ci: true
    - name: "gini"
      threshold: 0.40
      report_ci: true
    - name: "brier_score"
      threshold: 0.25
      direction: "lower_is_better"
    - name: "hosmer_lemeshow_p"
      threshold: 0.05
    - name: "subgroup_approval_variance"
      threshold: 0.15
      direction: "lower_is_better"
    - name: "shap_coverage"
      threshold: 1.0
    - name: "ci_width_auc"
      report_only: true

compliance:
  gates:
    - "registration"
    - "evaluation_harness"
    - "proxy_discrimination_review"
    - "calibration_validation"
    - "explainability_validation"
    - "small_sample_uncertainty"
    - "audit_trail"
    - "golden_dataset_signoff"

monitoring:
  frequency: "monthly"
  note: "Small dataset limits production drift monitoring — PSI unreliable below 1000 records"
```

## What It Demonstrates

### To Alex

"Australian data. Anonymised features. 690 records. Three governance challenges the platform handles: proxy discrimination when you don't know which features are demographic, calibration with small samples, and explainability when the features themselves are opaque. The platform adapts — uncertainty-aware metrics, proxy detection instead of direct discrimination testing, and flags where human review is needed."

### Architectural Points

| Point | How This Demo Proves It |
|---|---|
| Platform works with Australian data | Symbolically important for CBA |
| Anonymisation is a governance practice | Data minimisation demonstrated in action |
| Proxy discrimination detection | Platform catches bias even without labelled demographics |
| Small sample awareness | Metrics include uncertainty; platform warns when confidence is low |
| Human-in-the-loop where appropriate | Platform flags, doesn't block, when judgement is needed |
| Same platform, different constraints | Same evaluation harness adapts to dataset limitations |
