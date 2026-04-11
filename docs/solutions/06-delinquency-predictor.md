# Demo Solution #6: Delinquency Predictor

## What This Is

An ML scoring model that predicts whether a borrower will experience serious delinquency (90+ days past due) within the next two years. Takes financial behaviour features — revolving utilisation, debt ratio, income, past-due counts — and outputs a delinquency probability with feature contributions.

This solution uses the **Give Me Some Credit** dataset from Kaggle. It's the cleanest of the three ML datasets — 10 features, 150,000 records, intuitive feature names — making it the best candidate for a demo where explainability needs to be immediately understandable.

## Why This Solution

1. **Intuitive features** — unlike the Australian dataset (anonymised) or the Taiwan dataset (encoded), this dataset has human-readable feature names: "MonthlyIncome", "DebtRatio", "NumberOfTimes90DaysLate". When SHAP values say "DebtRatio was the biggest contributor", the demo audience understands immediately.
2. **Right size** — 150,000 records is large enough for reliable metrics and meaningful drift simulation, but small enough to train in seconds.
3. **Real missing data** — MonthlyIncome is missing for ~20% of records. This creates a natural data quality governance story: how the model handles missingness is itself a governance concern.
4. **Age available** — enables direct age-based discrimination testing (not just proxy detection).

## The Dataset

**Give Me Some Credit** (Kaggle Competition)

| Attribute | Detail |
|---|---|
| Source | Kaggle |
| Records | 150,000 |
| Features | 10 |
| Target | SeriousDlqin2yrs — experienced 90+ days past due (binary: 1 = yes, 0 = no) |
| Delinquency rate | ~6.7% |

### Feature Summary

| Feature | Description | Type | Governance Relevance |
|---|---|---|---|
| RevolvingUtilizationOfUnsecuredLines | Total balance / credit limit | Continuous | Key risk indicator |
| age | Age of borrower | Continuous | **Protected attribute** — age discrimination |
| NumberOfTime30-59DaysPastDueNotWorse | Past-due count (30-59 days) | Integer | Payment behaviour |
| DebtRatio | Monthly debt payments / monthly income | Continuous | Key risk indicator |
| MonthlyIncome | Monthly income | Continuous | **20% missing** — data quality concern |
| NumberOfOpenCreditLinesAndLoans | Open accounts count | Integer | Credit behaviour |
| NumberOfTimes90DaysLate | Past-due count (90+ days) | Integer | Strong predictor, but historically correlated with age |
| NumberRealEstateLoansOrLines | Mortgage/real estate count | Integer | Wealth proxy |
| NumberOfTime60-89DaysPastDueNotWorse | Past-due count (60-89 days) | Integer | Payment behaviour |
| NumberOfDependents | Dependents count | Integer | **Missing for ~2.5%** — potential proxy for family status |

### Protected Attributes

| Attribute | Available | Governance Concern |
|---|---|---|
| Age | Yes (continuous, 21-109) | Direct age discrimination testing. Age bands: 21-30, 31-40, 41-50, 51-60, 61+ |
| NumberOfDependents | Yes (0-20) | Proxy for family status — must not influence scoring after controlling for financial behaviour |
| MonthlyIncome | Yes (with missingness) | Income itself isn't protected, but missingness patterns may correlate with demographics |

## The Scenario

A squad in Consumer Lending builds an early warning system for borrowers at risk of serious delinquency. The model scores the existing portfolio monthly. Accounts above a risk threshold enter a proactive engagement workflow — the bank reaches out before the customer falls behind.

### Risk Tier

**`production_internal`** — scores inform proactive outreach by relationship managers. The model doesn't block credit or change terms automatically.

## The Model

**Approach:** Gradient boosting (scikit-learn GradientBoostingClassifier or XGBoost). With 150K records and 10 features, gradient boosting will produce a strong model with immediate SHAP interpretability via TreeExplainer.

**Training:** Stratified 70/30 split. ~105,000 train, ~45,000 test. Trains in seconds.

**Missing data handling:** MonthlyIncome imputed with median. Missingness indicator added as a feature (`MonthlyIncome_missing`: 0/1). This is a governance-relevant decision — the platform records how missing data was handled and includes it in the evidence package.

### Model Output Schema

```json
{
  "scoring_id": "SCR-DLQ-2026-0001",
  "borrower_id": "SYNTH-001",
  "input_features": {
    "RevolvingUtilizationOfUnsecuredLines": 0.45,
    "age": 52,
    "NumberOfTime30-59DaysPastDueNotWorse": 0,
    "DebtRatio": 0.35,
    "MonthlyIncome": 7200,
    "MonthlyIncome_missing": 0,
    "NumberOfOpenCreditLinesAndLoans": 8,
    "NumberOfTimes90DaysLate": 0,
    "NumberRealEstateLoansOrLines": 1,
    "NumberOfTime60-89DaysPastDueNotWorse": 0,
    "NumberOfDependents": 2
  },
  "output": {
    "delinquency_probability": 0.04,
    "risk_band": "LOW",
    "recommendation": "NO_ACTION"
  },
  "explainability": {
    "method": "SHAP",
    "top_contributors": [
      { "feature": "NumberOfTimes90DaysLate", "direction": "decreases_risk", "shap_value": -0.09, "display": "No prior 90-day delinquencies" },
      { "feature": "RevolvingUtilizationOfUnsecuredLines", "direction": "decreases_risk", "shap_value": -0.05, "display": "Moderate credit utilisation (45%)" },
      { "feature": "DebtRatio", "direction": "decreases_risk", "shap_value": -0.03, "display": "Healthy debt-to-income ratio (35%)" }
    ],
    "baseline_probability": 0.067
  },
  "data_quality": {
    "missing_features": [],
    "imputed_features": [],
    "quality_flag": "clean"
  },
  "guardrail_results": {
    "age_discrimination_check": "pass",
    "calibration_check": "pass",
    "data_quality_check": "pass",
    "explainability_check": "pass"
  }
}
```

### Risk Banding

| Probability Range | Risk Band | Recommendation |
|---|---|---|
| 0.00 - 0.05 | LOW | No action |
| 0.05 - 0.15 | MEDIUM | Monitor — include in monthly review |
| 0.15 - 0.30 | HIGH | Proactive outreach — relationship manager engagement |
| 0.30 - 1.00 | VERY HIGH | Immediate review — potential hardship assessment |

## Guardrails

### 1. Age Discrimination

With age as a direct feature, discrimination testing is straightforward and mandatory.

- **Check:** Score distributions across age bands must not show systematic disadvantage to older or younger borrowers after controlling for financial behaviour
- **Method:** Demographic parity and equalised odds across age bands (21-30, 31-40, 41-50, 51-60, 61+)
- **Failure mode:** Model scores borrowers aged 61+ as 3x higher risk than 31-40 year-olds with identical financial profiles. Age is correlated with retirement income patterns — the model may be penalising a life stage, not credit risk.
- **Enforcement:** Age-stratified discrimination probes. Threshold breach → deployment gate blocks.

#### Age Discrimination Probe

```json
{
  "probe_id": "AGE-001",
  "probe_type": "age_band",
  "base_profile": {
    "RevolvingUtilizationOfUnsecuredLines": 0.40,
    "NumberOfTime30-59DaysPastDueNotWorse": 0,
    "DebtRatio": 0.30,
    "MonthlyIncome": 6000,
    "NumberOfOpenCreditLinesAndLoans": 6,
    "NumberOfTimes90DaysLate": 0,
    "NumberRealEstateLoansOrLines": 1,
    "NumberOfTime60-89DaysPastDueNotWorse": 0,
    "NumberOfDependents": 1
  },
  "variants": [
    { "age": 25, "label": "21-30" },
    { "age": 35, "label": "31-40" },
    { "age": 45, "label": "41-50" },
    { "age": 55, "label": "51-60" },
    { "age": 65, "label": "61+" }
  ],
  "tolerance": 0.03,
  "metric": "max_score_difference_across_bands"
}
```

### 2. Data Quality Governance

20% missing MonthlyIncome is a governance concern, not just a modelling concern.

- **Check:** How was missingness handled? Does the imputation strategy introduce bias? Do customers with missing income get systematically different scores?
- **Method:** Compare score distributions for records with vs without missing MonthlyIncome. Check whether missingness correlates with age or dependents.
- **Failure mode:** Customers with missing MonthlyIncome are scored 40% higher risk because median imputation understates their actual income. The imputation strategy creates systematic disadvantage.
- **Enforcement:** Data quality report as part of evidence package. Missingness impact analysis included in compliance gate.

#### Data Quality Report

```json
{
  "feature": "MonthlyIncome",
  "missing_rate": 0.197,
  "imputation_method": "median",
  "imputed_value": 5400,
  "impact_analysis": {
    "mean_score_missing": 0.089,
    "mean_score_present": 0.062,
    "score_difference": 0.027,
    "assessment": "Customers with imputed income score 2.7% higher risk on average. Within tolerance but flagged for monitoring."
  },
  "correlation_with_protected": {
    "age": "no significant correlation (p=0.34)",
    "dependents": "weak correlation (p=0.08) — monitor"
  }
}
```

### 3. Calibration

With 150K records, calibration can be measured with high precision.

- **Check:** Predicted probabilities align with observed delinquency rates across deciles
- **Method:** Brier score, calibration curve, ECE
- **Failure mode:** The 6.7% base rate means most customers are low-risk. The model must be well-calibrated in the 0-15% range where most decisions happen.
- **Enforcement:** Calibration metrics on holdout set. ECE above threshold → deployment gate blocks.

### 4. Stability / Drift

150K records provides a strong baseline for drift detection.

- **Check:** PSI on score distributions and all 10 features
- **Method:** PSI with monthly production snapshots against training baseline
- **Failure mode:** Post-COVID, income distributions shifted. Debt ratios changed. The model's baseline assumptions no longer hold.
- **Enforcement:** Monthly PSI computation. Warning at 0.10, alert at 0.25.

### 5. Explainability

Human-readable feature names make SHAP explanations immediately interpretable.

- **Check:** SHAP values for every prediction, with human-readable display strings
- **Method:** SHAP TreeExplainer
- **Key advantage:** Unlike the Australian dataset where SHAP says "A9 contributed +0.18", this model says "No prior 90-day delinquencies reduced risk by 9%." The relationship manager reading this can understand and explain it to the customer.

## Evaluation Harness

### Metrics

| Metric | Method | Threshold (production_internal) | Note |
|---|---|---|---|
| AUC-ROC | sklearn | ≥ 0.75 | Higher bar — 150K records supports it |
| Gini Coefficient | 2 × AUC - 1 | ≥ 0.50 | Higher bar — 150K records supports it |
| Brier Score | sklearn | ≤ 0.10 | Tighter — enough data for precision |
| Expected Calibration Error | Custom | ≤ 0.03 | Tighter — enough data for precision |
| Age Band Parity Diff | Custom | ≤ 0.05 | Across 5 age bands |
| Age Band Equalised Odds | Custom | ≤ 0.05 | TPR/FPR parity across age bands |
| PSI (vs training) | Custom | ≤ 0.25 | Population stability |
| Feature PSI (per feature) | Custom | ≤ 0.25 per feature | Individual feature drift |
| Missingness Impact | Custom | ≤ 0.05 score diff | Missing vs present income |
| SHAP Coverage | Custom | 100% | Every prediction explained |
| Precision @ 15% threshold | Custom | ≥ 0.30 | Of those flagged, ≥30% would actually default |
| Recall @ 15% threshold | Custom | ≥ 0.60 | Catch ≥60% of actual defaults |

## Golden Dataset

45,000 records (30% holdout).

### Test Partitions

| Partition | Records | Purpose |
|---|---|---|
| Performance holdout | 30,000 | AUC, Gini, Brier, calibration, precision/recall |
| Age discrimination probes | 5,000 | Score parity across age bands |
| Missingness impact | 5,000 | Imputed vs non-imputed score comparison |
| Stability baseline | 3,000 | Reference distributions for PSI |
| Edge cases | 2,000 | Boundary scores, extreme feature values, outliers |

## Demo Scenarios

### Scenario 1: Happy Path — Low-Risk Borrower

**Input:** Borrower aged 42, low utilisation, no past-due history, stable income.

**What happens:** Model scores 0.03 (LOW). SHAP shows clean payment history as the dominant contributor. Portal displays human-readable explanation: "Clean payment history and moderate credit utilisation indicate low delinquency risk."

**Point:** The explanation is immediately understandable — to the relationship manager, to the compliance reviewer, to the customer.

### Scenario 2: High-Risk with Clear Explanation

**Input:** Borrower with high revolving utilisation (0.95), two prior 90-day delinquencies, high debt ratio.

**What happens:** Model scores 0.38 (VERY HIGH). SHAP clearly attributes risk to prior delinquencies and high utilisation. Recommendation: immediate review for potential hardship assessment.

**Point:** High scores are justified and explainable. The platform doesn't suppress risk — it ensures risk assessments are transparent.

### Scenario 3: Age Discrimination Catch

**Input:** Five borrowers with identical financial profiles, ages 25, 35, 45, 55, 65.

**What happens:** Model scores the 65-year-old 0.14 (HIGH) vs 0.06 (MEDIUM) for the 35-year-old. Max score difference is 0.08 — above the 0.03 tolerance. Discrimination guardrail fails. Deployment gate blocks.

**Point:** Age is a real feature in the model. The platform verifies it isn't driving unfair outcomes.

### Scenario 4: Missing Income — Data Quality Flag

**Input:** Two identical borrowers — one with MonthlyIncome = 6000, one with MonthlyIncome missing (imputed to median 5400).

**What happens:** The borrower with imputed income scores slightly higher risk. Platform reports the data quality impact analysis: "Imputation shifts this prediction by +0.02. Within tolerance but logged."

**Point:** Data quality is a governance concern. The platform tracks how missing data affects outcomes.

### Scenario 5: Drift Detection — Income Distribution Shift

**Input:** Simulated production population where average MonthlyIncome has increased 15% vs training baseline.

**What happens:** PSI on MonthlyIncome is 0.18 (above 0.10 warning threshold). Feature drift detected. Platform flags: "MonthlyIncome distribution has shifted. Model may be underestimating risk for the current population. Review recommended."

**Point:** The world changed since the model was trained. The platform caught it.

### Scenario 6: Calibration Deep-Dive

**Input:** Full holdout set, grouped into deciles by predicted probability.

**What happens:** Deciles 1-7 are well calibrated (predicted ≈ observed). Decile 9 shows 22% predicted delinquency but only 15% observed. The model overestimates risk for this segment.

**Point:** Overall metrics can mask segment-level problems. The platform checks calibration at the decile level, not just in aggregate.

## Solution Manifest

```yaml
# solution.yaml
solution:
  name: "Delinquency Predictor"
  id: "delinquency-predictor"
  type: "scoring"
  category: "ml"
  version: "1.0.0"
  description: "Predicts probability of serious delinquency (90+ days past due) within 2 years using borrower financial behaviour"

risk_tier: "production_internal"

dataset:
  source: "Kaggle — Give Me Some Credit"
  records: 150000
  features: 10
  target: "SeriousDlqin2yrs"
  protected_attributes: ["age"]
  proxy_attributes: ["NumberOfDependents"]
  missing_data:
    MonthlyIncome: 0.197
    NumberOfDependents: 0.025
  imputation:
    MonthlyIncome: "median"
    NumberOfDependents: "median"

model:
  type: "GradientBoostingClassifier"
  framework: "scikit-learn"
  explainability: "SHAP (TreeExplainer)"
  training_split: 0.7

guardrails:
  age_discrimination:
    bands: [21, 31, 41, 51, 61]
    demographic_parity_threshold: 0.05
    equalised_odds_threshold: 0.05
    probe_tolerance: 0.03
  data_quality:
    missingness_impact_threshold: 0.05
    missingness_correlation_check: true
  calibration:
    brier_score_threshold: 0.10
    ece_threshold: 0.03
  stability:
    psi_warning: 0.10
    psi_alert: 0.25
    feature_psi: true
  explainability:
    method: "SHAP"
    coverage: 1.0
    human_readable: true

evaluation:
  holdout_size: 0.3
  metrics:
    - name: "auc_roc"
      threshold: 0.75
    - name: "gini"
      threshold: 0.50
    - name: "brier_score"
      threshold: 0.10
      direction: "lower_is_better"
    - name: "ece"
      threshold: 0.03
      direction: "lower_is_better"
    - name: "age_band_parity_diff"
      threshold: 0.05
      direction: "lower_is_better"
    - name: "age_band_equalised_odds"
      threshold: 0.05
      direction: "lower_is_better"
    - name: "psi"
      threshold: 0.25
      direction: "lower_is_better"
    - name: "feature_psi_max"
      threshold: 0.25
      direction: "lower_is_better"
    - name: "missingness_impact"
      threshold: 0.05
      direction: "lower_is_better"
    - name: "shap_coverage"
      threshold: 1.0
    - name: "precision_at_threshold"
      threshold: 0.30
      at: 0.15
    - name: "recall_at_threshold"
      threshold: 0.60
      at: 0.15

compliance:
  gates:
    - "registration"
    - "evaluation_harness"
    - "age_discrimination_validation"
    - "data_quality_validation"
    - "calibration_validation"
    - "stability_validation"
    - "explainability_validation"
    - "audit_trail"
    - "golden_dataset_signoff"

monitoring:
  frequency: "monthly"
  drift_check: "psi (score + all features)"
  recalibration_trigger: "ece > 0.05"
  discrimination_recheck: "quarterly"
  data_quality_recheck: "monthly (missingness rate trends)"
```

## What It Demonstrates

### To Alex

"This model predicts which borrowers will become seriously delinquent. Watch the explanation: 'Clean payment history and moderate credit utilisation indicate low risk.' A relationship manager can read that. A customer can understand it. A regulator can review it."

"Now watch this — same financial profile, five different ages. The model scores the 65-year-old twice as high. The platform caught it. That's age discrimination, and it would have gone to production without this governance layer."

"And here's the data quality story — 20% of income data is missing. The platform tracks how imputation affects scores. It doesn't just impute and forget. It measures and reports."

### Architectural Points

| Point | How This Demo Proves It |
|---|---|
| Human-readable explainability | SHAP + intuitive feature names = immediately understandable explanations |
| Age discrimination testing | Direct protected attribute testing with probes |
| Data quality as governance | Missing data impact is measured, tracked, and reported |
| Drift monitoring at feature level | Individual feature PSI catches shifts that aggregate PSI misses |
| Calibration at segment level | Decile-level calibration reveals problems aggregate metrics hide |
| Right-sized governance | 150K records enables tighter thresholds than the 690-record Australian dataset |

### Comparison Across ML Solutions

| Dimension | Solution #4 (Taiwan) | Solution #5 (Australian) | Solution #6 (Delinquency) |
|---|---|---|---|
| Dataset size | 30,000 | 690 | 150,000 |
| Protected attributes | Gender, age, education, marital | Unknown (anonymised) | Age, dependents (proxy) |
| Discrimination method | Direct probes | Proxy detection | Direct age probes |
| Unique governance story | Multi-attribute discrimination | Anonymisation + small sample | Data quality + human-readable SHAP |
| Calibration approach | Standard ECE | Hosmer-Lemeshow (small sample) | Decile-level calibration |
| Model complexity | Moderate | Simple (logistic) | Moderate |
| Best demo strength | Richest fairness testing | Australian context + uncertainty | Most interpretable explanations |
