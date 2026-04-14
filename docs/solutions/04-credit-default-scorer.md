# Demo Solution #4: Credit Card Default Scorer

## What This Is

An ML scoring model that predicts whether a credit card holder will default on their payment next month. Takes customer features (credit limit, payment history, bill amounts) and outputs a probability score with feature contributions explaining the prediction.

This is the first ML demo solution. It passes through the same platform components (guardrails, evaluation, compliance gates) as the GenAI solutions, proving the reusable components work across the GenAI/ML boundary. It's the solution type where **discrimination, calibration, and explainability are the primary governance concerns** — every score must be fair, well-calibrated, and explainable.

## Why Credit Default Scoring

Credit risk is the backbone of any bank's risk management:

- Probability of default (PD) models underpin capital adequacy
- Credit decisions directly affect customers — a biased model is a regulatory event
- APRA, ASIC, and anti-discrimination law all have opinions about how these models behave
- Every squad in Risk Management either builds, validates, or monitors a scoring model

If the platform can govern a credit scorer — with discrimination testing, calibration monitoring, and explainability evidence — it can govern any ML solution.

## The Dataset

**Taiwan Credit Card Default Dataset** (UCI Machine Learning Repository)

| Attribute | Detail |
|---|---|
| Source | UCI ML Repository |
| Records | 30,000 |
| Features | 23 |
| Target | Default on payment next month (binary: 1 = default, 0 = no default) |
| Default rate | ~22% |

### Feature Summary

| Feature Group | Features | Count |
|---|---|---|
| Demographics | Gender, education, marital status, age | 4 |
| Credit | Credit limit (LIMIT_BAL) | 1 |
| Payment history | Repayment status for past 6 months (PAY_0 to PAY_6) | 6 |
| Bill amounts | Bill statement for past 6 months (BILL_AMT1 to BILL_AMT6) | 6 |
| Payment amounts | Previous payment for past 6 months (PAY_AMT1 to PAY_AMT6) | 6 |
| **Engineered** | Unpaid balance, utilisation ratio, payment ratio, balance trend, avg utilisation | **20** |

### Protected Attributes

This is what makes this dataset ideal for governance demos — four protected attributes:

| Attribute | Values | Governance Concern |
|---|---|---|
| Gender | Male (1), Female (2) | Scores must not systematically differ by gender after controlling for credit behaviour |
| Education | Graduate school (1), University (2), High school (3), Other (4-6) | Education level should not be a proxy for discrimination |
| Marital status | Married (1), Single (2), Other (3) | Marital status must not influence default prediction |
| Age | Continuous (21-79) | Age-based discrimination is prohibited; age bands must be tested |

## The Scenario

A squad in Retail Banking builds a credit card default prediction model. The model scores existing cardholders monthly, flagging those likely to default so the collections team can intervene early. The model is internal-facing — collections staff see the scores and act on them.

### Risk Tier

**`production_internal`** — the model supports human decisions (collections agents review flagged accounts), but doesn't make autonomous decisions. Standard guardrail bar, moderate thresholds.

### Why Not `production_customer_facing`?

The score isn't shown to customers. Collections agents use it as one input among many. If the model were used for automated credit limit adjustments or direct customer communications, it would be `production_customer_facing`.

## The Model

**Approach:** Logistic regression or gradient boosting (scikit-learn). The model is intentionally simple — the governance demo doesn't require a sophisticated model. It requires a model that produces outputs the platform can govern.

**Training:** 70/30 train/test split on the 30,000 records. Trains in under 1 second.

**Why sklearn:** No GPU, no infrastructure, no deployment complexity. A `.fit()` and `.predict_proba()` call. The model artifacts (coefficients, feature importance, SHAP values) are immediately available for the platform to evaluate.

### Model Output Schema

```json
{
  "scoring_id": "SCR-2026-0001",
  "applicant_id": "SYNTH-001",
  "input_features": {
    "LIMIT_BAL": 200000,
    "AGE": 34,
    "EDUCATION": 2,
    "MARRIAGE": 1,
    "PAY_0": 0,
    "PAY_2": 0,
    "BILL_AMT1": 45000,
    "PAY_AMT1": 45000
  },
  "output": {
    "default_probability": 0.18,
    "risk_band": "MEDIUM",
    "decision_recommendation": "MONITOR"
  },
  "explainability": {
    "method": "SHAP",
    "top_contributors": [
      { "feature": "PAY_0", "direction": "increases_risk", "shap_value": 0.12 },
      { "feature": "LIMIT_BAL", "direction": "decreases_risk", "shap_value": -0.08 },
      { "feature": "PAY_AMT1", "direction": "decreases_risk", "shap_value": -0.06 },
      { "feature": "BILL_AMT1", "direction": "increases_risk", "shap_value": 0.04 }
    ],
    "baseline_probability": 0.22
  },
  "guardrail_results": {
    "discrimination_check": "pass",
    "calibration_check": "pass",
    "stability_check": "pass",
    "explainability_check": "pass"
  },
  "metadata": {
    "model_version": "1.0.0",
    "model_type": "GradientBoostingClassifier",
    "training_date": "2026-04-01",
    "inference_latency_ms": 12
  }
}
```

### Risk Banding

| Probability Range | Risk Band | Recommendation |
|---|---|---|
| 0.00 - 0.10 | LOW | No action |
| 0.10 - 0.30 | MEDIUM | Monitor — review at next cycle |
| 0.30 - 0.60 | HIGH | Proactive outreach — contact customer |
| 0.60 - 1.00 | VERY HIGH | Immediate intervention — collections escalation |

## Guardrails

Four guardrail concerns are primary for a credit scoring model.

### 1. Discrimination

The model must not produce systematically different scores for protected groups after controlling for legitimate credit behaviour features.

- **Check:** Same credit profile, different demographic → scores must be within tolerance
- **Method:** Demographic parity difference, equalised odds, and disparate impact ratio across gender, age bands, education, and marital status
- **Failure mode:** Model scores women 8% higher risk than men with identical payment histories. The model learned a proxy — credit limits correlate with gender in the training data.
- **Enforcement:** Discrimination probes run as part of the evaluation harness. Threshold breach → deployment gate blocks.

#### Discrimination Probe Structure

```json
{
  "probe_id": "DISC-001",
  "probe_type": "gender",
  "base_profile": {
    "LIMIT_BAL": 150000,
    "PAY_0": 0,
    "PAY_2": 0,
    "BILL_AMT1": 30000,
    "PAY_AMT1": 30000,
    "EDUCATION": 2,
    "MARRIAGE": 1,
    "AGE": 35
  },
  "variants": [
    { "SEX": 1, "label": "male" },
    { "SEX": 2, "label": "female" }
  ],
  "tolerance": 0.02,
  "metric": "absolute_score_difference"
}
```

### 2. Calibration

A model that outputs 0.30 probability should be correct ~30% of the time. Miscalibrated scores lead to bad decisions at scale.

- **Check:** Predicted probabilities align with observed default rates across deciles
- **Method:** Brier score, calibration curve (reliability diagram), expected calibration error (ECE)
- **Failure mode:** Model outputs 0.80 for accounts that default only 40% of the time. Collections team wastes resources on low-risk accounts.
- **Enforcement:** Calibration metrics computed on holdout set. ECE above threshold → deployment gate blocks.

### 3. Stability / Drift

Score distributions must remain stable over time. A shift signals data drift or population change.

- **Check:** Population Stability Index (PSI) on score distributions and key features between training and production populations
- **Method:** PSI, KS statistic, feature distribution comparison
- **Failure mode:** After a product change, the population's credit limit distribution shifts. Model's assumptions no longer hold, but scores look normal in aggregate. PSI catches the shift.
- **Enforcement:** Continuous monitoring compares production score distribution against baseline. PSI > 0.25 → alert. PSI > 0.5 → model flagged for re-evaluation.

### 4. Explainability

Every score must be accompanied by feature contributions. Regulators and customers have a right to understand why.

- **Check:** SHAP values computed for every prediction. Top contributors surfaced.
- **Method:** SHAP (TreeExplainer for gradient boosting, LinearExplainer for logistic regression)
- **Failure mode:** Model produces a score of 0.85 (very high risk) with no explanation. Collections agent can't justify the intervention. Customer complains. Regulator asks why.
- **Enforcement:** Explainability completeness check — every scored record must have SHAP values. Compliance gate verifies.

## Evaluation Harness

For an ML scoring model, the evaluation harness uses statistical metrics rather than LLM-as-judge. The platform adapts — same harness interface, different metric implementations.

### Metrics

| Metric | Method | Role for Scoring | Threshold (production_internal) |
|---|---|---|---|
| AUC-ROC | sklearn | **Primary** — overall discrimination power | ≥ 0.70 |
| Gini Coefficient | 2 × AUC - 1 | **Primary** — industry-standard performance measure | ≥ 0.40 |
| Brier Score | sklearn | **Primary** — calibration quality | ≤ 0.20 |
| Expected Calibration Error | Custom | **Primary** — probability alignment | ≤ 0.05 |
| Demographic Parity Diff | Custom | **Critical** — fairness across gender | ≤ 0.05 |
| Equalised Odds Diff | Custom | **Critical** — fairness across gender | ≤ 0.05 |
| Disparate Impact Ratio | Custom | **Critical** — must be ≥ 0.80 (four-fifths rule) | ≥ 0.80 |
| PSI (vs training) | Custom | **Primary** — population stability | ≤ 0.25 |
| KS Statistic | scipy | Secondary — separation power | Report only |
| SHAP Coverage | Custom | Important — every prediction explained | 100% |

### GenAI vs ML Evaluation — Same Platform, Different Metrics

| Dimension | Q&A Agent (GenAI) | Credit Scorer (ML) |
|---|---|---|
| Evaluation method | LLM-as-judge (DeepEval) | Statistical metrics (sklearn, scipy) |
| Primary quality metric | Faithfulness (0.90) | AUC-ROC (0.70) |
| Fairness metric | Bias score (DeepEval) | Demographic parity, equalised odds, disparate impact |
| Calibration metric | N/A | Brier score, ECE |
| Drift metric | Faithfulness degradation | PSI, KS, feature drift |
| Explainability | Citation coverage | SHAP values |
| Judge model | gpt-4o / gpt-4o-mini | N/A — deterministic computation |
| Evaluation latency | Seconds (LLM calls) | Milliseconds (statistical computation) |

This comparison is the architectural point: the platform's evaluation harness is a **reusable interface** that accepts different metric implementations. The harness doesn't care whether the metric is an LLM call or a numpy computation — it runs the metric, checks the threshold, and produces a pass/fail result.

## Golden Dataset

The golden dataset for an ML model is the holdout test set — 9,000 records (30% of 30,000).

### Test Partitions

| Partition | Records | Purpose |
|---|---|---|
| Performance holdout | 6,000 | AUC, Gini, Brier score, calibration |
| Discrimination probes | 1,000 | Same profiles, varied demographics |
| Stability baseline | 1,000 | Reference distribution for PSI/KS |
| Edge cases | 500 | Boundary scores, extreme feature values |
| Adversarial | 500 | Profiles designed to expose model weaknesses |

### Discrimination Probe Coverage

| Protected Attribute | Probe Pairs | What It Tests |
|---|---|---|
| Gender | 200 pairs | Male vs female, identical credit behaviour |
| Age | 200 pairs | Age bands (21-30, 31-40, 41-50, 51+), identical credit behaviour |
| Education | 150 pairs | Graduate vs university vs high school, identical credit behaviour |
| Marital status | 100 pairs | Married vs single vs other, identical credit behaviour |
| Intersectional | 100 pairs | Gender × age, gender × education — compound discrimination |

## Demo Scenarios

### Pre-Recorded Scenarios

#### Scenario 1: Happy Path — Low-Risk Score

**Input:** Customer with high credit limit, clean payment history, moderate bills.

**What happens:** Model scores 0.08 (LOW risk). SHAP shows payment history as the strongest contributor. All guardrails pass. Portal shows green.

**Point:** The model works. The explanation is intuitive. The platform verified it.

#### Scenario 2: High-Risk Score with Explanation

**Input:** Customer with repeated late payments, maxed credit limit.

**What happens:** Model scores 0.72 (VERY HIGH). SHAP shows PAY_0 (most recent payment status) as the dominant contributor. Recommendation: immediate intervention. All guardrails pass.

**Point:** High-risk scores are legitimate when explained. The platform doesn't block high scores — it verifies they're justified.

#### Scenario 3: Discrimination Catch

**Input:** Two customers with identical credit behaviour but different genders.

**What happens:** Model scores the female customer 0.31 (HIGH) and the male customer 0.22 (MEDIUM). The discrimination guardrail catches the 0.09 absolute difference — above the 0.02 tolerance. Deployment gate blocks.

**Point:** The platform catches bias that humans would miss. Same credit profile, different score — the model learned a proxy.

#### Scenario 4: Calibration Failure

**Input:** Batch of 500 customers scored in the 0.70-0.80 probability range.

**What happens:** Actual default rate for this group is 45%, not the expected ~75%. ECE exceeds threshold. The model is overestimating risk for high-score customers.

**Point:** A model that says "80% chance of default" when it's really 45% wastes collections resources and may trigger unfair treatment.

#### Scenario 5: Drift Detection

**Input:** Production population compared to training baseline.

**What happens:** PSI on credit limit distribution is 0.31 (above 0.25 threshold). The production population has higher credit limits on average — possibly due to a product change. Model flagged for re-evaluation.

**Point:** The model was fine at deployment. The world changed. The platform caught the shift before it caused damage.

#### Scenario 6: Missing Explainability

**Input:** Score produced without SHAP values (simulated SDK misconfiguration).

**What happens:** SHAP coverage check fails — the prediction has no feature contributions. Compliance gate blocks. "Every score must be explainable" isn't a guideline, it's enforced.

**Point:** Explainability is a governance requirement, not an optional extra. The platform enforces it.

## Solution Manifest

```yaml
# solution.yaml
solution:
  name: "Credit Card Default Scorer"
  id: "credit-default-scorer"
  type: "scoring"
  category: "ml"
  version: "1.0.0"
  description: "Predicts credit card default probability using customer payment history and demographics"

risk_tier: "production_internal"

dataset:
  source: "UCI Machine Learning Repository — Taiwan Credit Card Default"
  records: 30000
  features: 23
  target: "default_payment_next_month"
  protected_attributes: ["SEX", "EDUCATION", "MARRIAGE", "AGE"]

model:
  type: "GradientBoostingClassifier"
  framework: "scikit-learn"
  explainability: "SHAP"
  training_split: 0.7

guardrails:
  discrimination:
    attributes: ["SEX", "EDUCATION", "MARRIAGE", "AGE"]
    demographic_parity_threshold: 0.05
    equalised_odds_threshold: 0.05
    disparate_impact_ratio: 0.80
    probe_tolerance: 0.02
  calibration:
    brier_score_threshold: 0.20
    ece_threshold: 0.05
  stability:
    psi_warning: 0.10
    psi_alert: 0.25
    psi_block: 0.50
  explainability:
    method: "SHAP"
    coverage: 1.0

evaluation:
  holdout_size: 0.3
  metrics:
    - name: "auc_roc"
      threshold: 0.70
    - name: "gini"
      threshold: 0.40
    - name: "brier_score"
      threshold: 0.20
      direction: "lower_is_better"
    - name: "ece"
      threshold: 0.05
      direction: "lower_is_better"
    - name: "demographic_parity_diff"
      threshold: 0.05
      direction: "lower_is_better"
    - name: "equalised_odds_diff"
      threshold: 0.05
      direction: "lower_is_better"
    - name: "disparate_impact_ratio"
      threshold: 0.80
    - name: "psi"
      threshold: 0.25
      direction: "lower_is_better"
    - name: "shap_coverage"
      threshold: 1.0

compliance:
  gates:
    - "registration"
    - "evaluation_harness"
    - "discrimination_validation"
    - "calibration_validation"
    - "stability_validation"
    - "explainability_validation"
    - "audit_trail"
    - "golden_dataset_signoff"

monitoring:
  frequency: "monthly"
  drift_check: "psi"
  recalibration_trigger: "ece > 0.10"
  discrimination_recheck: "quarterly"
```

## Ablation Study

### Experiment Tracking

The solution uses **MLflow** (local SQLite backend) to track experiments. Each training run logs parameters, metrics, model artifacts, feature importance plots, and SHAP summaries.

```bash
cd solutions/credit-default-scorer
python src/ablation.py                    # runs all 9 steps, logs to mlflow.db
python -u run_mlflow_ui.py               # browse at http://127.0.0.1:5000
```

### Incremental Feature Group Ablation

Features are added incrementally to isolate the contribution of each group. Same hyperparameters (GBM: 100 trees, depth 5, lr 0.1) and same train/test split (70/30, seed 42) across all steps.

#### Raw Feature Groups (Steps 1-5)

| Step | Features Added | AUC | Gini | Brier | DemParity | DI Ratio |
|------|---------------|-----|------|-------|-----------|----------|
| 1. Payment history | PAY_0..PAY_6 (6) | 0.738 | 0.476 | 0.140 | 0.007 | 0.976 |
| 2. + Credit limit | LIMIT_BAL (7) | 0.754 | 0.508 | 0.139 | 0.012 | 0.944 |
| 3. + Bill amounts | BILL_AMT1..6 (13) | 0.773 | 0.546 | 0.137 | 0.013 | 0.952 |
| 4. + Payment amounts | PAY_AMT1..6 (19) | 0.772 | 0.544 | 0.138 | 0.014 | 0.942 |
| 5. + Demographics | SEX, EDU, MARRIAGE, AGE (23) | 0.775 | 0.551 | 0.137 | 0.021 | 0.892 |

#### Engineered Feature Groups (Steps 6-9)

Engineered features are derived from raw bill and payment data to test whether domain-informed transformations capture signal that raw features miss.

| Feature | Formula | Intuition |
|---------|---------|-----------|
| UNPAID_BAL{1-6} | BILL_AMT - PAY_AMT | Outstanding debt each month |
| UTIL_RATIO{1-6} | BILL_AMT / LIMIT_BAL | Credit utilisation per month |
| PAY_RATIO{1-6} | PAY_AMT / BILL_AMT | Fraction of bill paid (capped at 1.0) |
| BAL_TREND | Linear slope of UNPAID_BAL over 6 months | Debt trajectory (positive = growing) |
| AVG_UTIL | Mean of UTIL_RATIO across 6 months | Overall credit utilisation |

| Step | Features | Count | AUC | Gini | Brier | DemParity | DI Ratio |
|------|----------|-------|-----|------|-------|-----------|----------|
| 6. All V1 engineered on best raw | PAY + LIMIT + BILL + all V1 engineered | 33 | 0.779 | 0.557 | 0.137 | 0.014 | 0.947 |
| 7. Unpaid balance only | PAY + LIMIT + BILL + UNPAID_BAL | 19 | 0.773 | 0.545 | 0.138 | 0.013 | 0.962 |
| 8. Ratio-based only | PAY + LIMIT + BILL + UTIL + PAY_RATIO + trend | 27 | 0.779 | 0.558 | 0.136 | 0.014 | 0.908 |
| 9. All raw + V1 engineered | PAY + LIMIT + BILL + PAY_AMT + all V1 engineered | 39 | 0.777 | 0.554 | 0.137 | 0.013 | 0.937 |

#### V2 Engineered Features (Steps 10-16)

Deeper domain features: delinquency patterns from payment status codes, spending volatility, credit headroom, behavioral signals, and interaction terms.

| Feature | Formula | Intuition |
|---------|---------|-----------|
| MONTHS_DELINQUENT | count(PAY > 0) | How many months late in 6-month window |
| MAX_DELAY | max(PAY_0..PAY_6) | Worst delinquency severity |
| DELINQUENCY_TREND | slope of PAY values | Improving vs deteriorating payment behaviour |
| CONSECUTIVE_LATE | longest streak of PAY > 0 | Sustained vs sporadic delinquency |
| REVOLVING_COUNT | count(PAY = 0) | Months using revolving credit (minimum payment) |
| FULL_PAY_COUNT | count(PAY = -1) | Months paid in full |
| BILL_VOLATILITY | std(BILL_AMT1..6) | Erratic spending signals instability |
| PAY_VOLATILITY | std(PAY_AMT1..6) | Erratic payments = inconsistent cash flow |
| BILL_RANGE | max - min of bills | Spending spikes |
| AVAILABLE_CREDIT | LIMIT_BAL - BILL_AMT1 | Remaining credit headroom |
| AVAILABLE_CREDIT_RATIO | (LIMIT - BILL) / LIMIT | Normalised headroom |
| HEADROOM_TREND | slope of available credit | Shrinking headroom = growing risk |
| MIN_PAY_FLAG | count(PAY_AMT/BILL_AMT < 5%) | Minimum-payment-only behaviour |
| OVERPAY_COUNT | count(PAY_AMT > BILL_AMT) | Paying ahead = low risk |
| UTIL_X_MAX_DELAY | AVG_UTIL * MAX_DELAY | High utilisation + late = multiplicative risk |
| HEADROOM_X_DELINQUENT | (1 - headroom ratio) * months delinquent | Low headroom + late = compounding risk |

| Step | Features | Count | AUC | Gini | Brier | DemParity | DI Ratio |
|------|----------|-------|-----|------|-------|-----------|----------|
| 10. Delinquency patterns | Base + delinquency patterns | 19 | 0.772 | 0.544 | 0.137 | 0.014 | 0.931 |
| 11. + Volatility | + bill/payment volatility | 22 | 0.773 | 0.546 | 0.137 | 0.013 | 0.916 |
| 12. + Capacity | + available credit, headroom | 25 | 0.776 | 0.552 | 0.137 | 0.016 | 0.933 |
| 13. + Behavioral | + min pay, overpay counts | 27 | 0.777 | 0.554 | 0.137 | 0.014 | 0.929 |
| 14. + Interactions | + util×delay, headroom×delinquent | 29 | 0.775 | 0.550 | 0.137 | 0.015 | 0.912 |
| 15. Best V1 + all V2 | Ratio features + all V2 | 43 | 0.776 | 0.553 | 0.136 | 0.015 | 0.918 |
| 16. Kitchen sink | All raw + V1 + V2 | 55 | 0.777 | 0.555 | 0.137 | 0.014 | 0.914 |

### Key Findings

1. **Payment history is the dominant signal** — Step 1 alone achieves AUC 0.738 with just 6 features. This confirms the hypothesis that delinquency history is the primary default predictor.

2. **Credit limit adds meaningful lift** — Step 2 adds +0.016 AUC from a single feature. Capacity constraints matter.

3. **Bill amounts improve the model further** — Step 3 adds +0.019 AUC. Utilisation context helps.

4. **Payment amounts add noise, not signal** — Step 4 actually decreases AUC by 0.001. The 6 additional payment amount features don't help — the model already captured repayment behaviour through the payment history flags.

5. **Demographics: the governance tradeoff** — Step 5 adds +0.003 AUC (marginal) but increases demographic parity difference from 0.014 to 0.021 and drops the disparate impact ratio from 0.942 to 0.892. The model is closer to the four-fifths rule threshold (0.80). **The AUC gain is not worth the fairness cost** — this is the governance insight the ablation is designed to surface.

6. **V1 engineered features beat raw payment amounts** — Step 8 (ratio features, AUC 0.7789) and step 6 (all V1, AUC 0.7787) both outperform the best raw config (step 3, AUC 0.7732) by +0.006 — a meaningful lift. Unpaid balance alone (step 7, AUC 0.7726) matches raw payment amounts (step 4, AUC 0.7721), confirming `BILL - PAY` captures the same signal as 6 raw features in one.

7. **Delinquency patterns don't help GBM (Step 10)** — Adding explicit delinquency features (months late, max delay, streaks) to the base yields AUC 0.7721, identical to step 3. The tree model already learns these patterns from raw PAY codes through splits — making them explicit adds no lift.

8. **Capacity features provide the real V2 lift (Step 12)** — Available credit and headroom trend push AUC from 0.7728 (step 11) to 0.7762, a +0.003 jump. Knowing how much credit remains — and whether it's shrinking — adds signal the model can't easily derive from bill amounts alone.

9. **Behavioral signals add marginal lift (Step 13)** — Min-payment flags and overpay counts push AUC to 0.7771, but the gain is small (+0.001). The model already captures payment adequacy through utilisation and payment ratios.

10. **Interaction features hurt (Step 14)** — Adding `UTIL × MAX_DELAY` and `HEADROOM × DELINQUENT` drops AUC from 0.7771 to 0.7752. GBM already captures interactions through tree depth — explicit interaction terms add noise.

11. **Kitchen sink confirms: more features ≠ better model** — Step 16 (55 features, AUC 0.7772) doesn't beat step 8 (27 features, AUC 0.7789). The best model remains **step 8: ratio-based V1 features** — highest AUC, lowest Brier (0.1364), strong fairness (DI 0.908), no demographics.

## Model Selection Analysis

Eight studies were conducted to systematically arrive at the optimal production model. All experiments are tracked in MLflow with full artifacts.

### Study Summary

| # | Study | MLflow Experiment | Key Finding |
|---|-------|-------------------|-------------|
| 1 | Feature group ablation | `credit-default-ablation` | Payment history + credit + bills = sweet spot. Payment amounts add noise. |
| 1b | Engineered feature ablation | `credit-default-ablation` (steps 6-9) | Derived features (unpaid balance, utilisation, payment ratios, trend) tested against and alongside raw features. |
| 2 | Skip payment amounts | `credit-default-ablation` (step 6) | 17 features (no PAY_AMT) achieves best single-split AUC (0.7765). |
| 3 | Model comparison | `credit-default-model-comparison` | GBM wins on AUC. Logistic regression fails four-fifths rule. |
| 4 | Threshold tuning | `credit-default-threshold-tuning` | Best F1 at threshold 0.25. Default 0.50 too conservative. |
| 5 | Hyperparameter sweep | `credit-default-hyperparam-sweep` | `lr=0.05` beats `lr=0.10`. Deeper trees and higher lr both hurt. |
| 6 | Cross-validation stability | `credit-default-cv-stability` | AUC stable (0.783 +/- 0.007). DI with all demographics fails every fold. |
| 7 | Individual demographics | `credit-default-demographic-interaction` | SEX is the problem feature. EDUCATION adds AUC. MARRIAGE improves fairness. |

### The Three Candidate Models

Based on the studies, three candidate configurations were evaluated under 5-fold cross-validation:

| Candidate | Features | AUC | Brier | DemParity | DI Ratio | DI Pass Rate |
|-----------|----------|-----|-------|-----------|----------|-------------|
| **A: No demographics** | 13 (PAY + LIMIT + BILL) | 0.7812 +/- 0.008 | 0.1345 | 0.0193 | 0.826 +/- 0.020 | **5/5 folds** |
| B: + EDUCATION, MARRIAGE | 15 | 0.7823 +/- 0.007 | 0.1340 | 0.0186 | 0.819 +/- 0.017 | 4/5 folds |
| C: All demographics | 17 | 0.7829 +/- 0.007 | 0.1340 | 0.0286 | 0.762 +/- 0.022 | **0/5 folds** |

### Decision: Candidate A — 13 Features, No Demographics

**Selected configuration:**
- **Model:** GradientBoostingClassifier
- **Hyperparameters:** `n_estimators=100, max_depth=5, learning_rate=0.05, subsample=0.8`
- **Features (13):** PAY_0, PAY_2..PAY_6, LIMIT_BAL, BILL_AMT1..BILL_AMT6
- **Threshold:** 0.25 (optimised for F1)

**Why this model:**

1. **Passes the four-fifths rule in every fold.** Candidate A is the only configuration that passes the disparate impact test (DI >= 0.80) in all 5 CV folds. Candidate B fails 1/5 folds. Candidate C fails every fold. A model that fails the four-fifths rule is a regulatory event — this is non-negotiable.

2. **AUC is within noise of the best.** The gap between Candidate A (0.7812) and Candidate C (0.7829) is 0.0017 — well within the standard deviation of 0.008. There is no statistically meaningful performance difference between the three candidates. Paying a fairness cost for noise is not justified.

3. **No protected attributes as inputs.** Even though EDUCATION and MARRIAGE are technically less harmful than SEX and AGE, excluding all demographics eliminates the risk of proxy discrimination through feature interactions. The model cannot be accused of using demographic information, directly or indirectly.

4. **Simpler model governance.** A model with no demographic inputs requires less ongoing monitoring for discrimination, fewer compliance reviews, and simpler documentation for regulators. The governance overhead of including any demographic feature outweighs the 0.001 AUC it might buy.

5. **Threshold 0.25 recovers recall.** At the default 0.50 threshold, the model is too conservative (36% recall). At 0.25, F1 peaks at 0.540 with 59% recall and 50% precision, flagging 26% of customers — a more actionable workload for the collections team.

### What Was Ruled Out and Why

| Option | Ruled Out Because |
|--------|-------------------|
| Adding payment amounts (PAY_AMT1..6) | Decreased AUC by 0.001 (noise, not signal). 6 extra features for no benefit. |
| Adding SEX | +0.0006 AUC, -0.057 DI. Biggest fairness cost, negligible performance gain. |
| Adding AGE | +0.0010 AUC, -0.020 DI. Moderate fairness cost for near-zero gain. |
| Logistic regression | DI ratio 0.751 — fails four-fifths rule outright. Also worst AUC (0.707). |
| Random forest | AUC 0.769 (worse than GBM), DI 0.882 (borderline). No advantage. |
| AdaBoost | Fairest model (DI 0.980) but poorly calibrated (ECE 0.036) and lower AUC. |
| Higher learning rate (0.2) | Overfits — lower AUC, worse calibration, worse fairness. |
| Deeper trees (depth 7) | Overfits — lower AUC and worse DI than depth 5. |
| Threshold 0.50 | Only catches 36% of defaults. Precision is high (66%) but too many defaults slip through. |

### Production Metrics (CV-Validated)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AUC-ROC | 0.781 +/- 0.008 | >= 0.70 | PASS |
| Gini | 0.563 +/- 0.016 | >= 0.40 | PASS |
| Brier Score | 0.135 +/- 0.002 | <= 0.20 | PASS |
| ECE | 0.013 +/- 0.003 | <= 0.05 | PASS |
| Demographic Parity Diff | 0.019 +/- 0.002 | <= 0.05 | PASS |
| Disparate Impact Ratio | 0.826 +/- 0.020 | >= 0.80 | PASS (5/5) |
| SHAP Coverage | 100% | 100% | PASS |

## What It Demonstrates

### To Alex

"This is the other half of the chapter's scope. GenAI solutions hallucinate — ML solutions discriminate. Different failure modes, same governance platform. This credit scorer runs through the same compliance gates as the Q&A agent — but the metrics that matter are completely different. Discrimination testing instead of faithfulness checking. Calibration instead of citation coverage. SHAP values instead of source citations."

"Watch — I'll show you two customers with identical credit behaviour but different genders. The model scores them differently. The platform caught it. That's what 'governance on autopilot' looks like for ML."

### Architectural Points

| Point | How This Demo Proves It |
|---|---|
| Platform governs ML, not just GenAI | Same portal, same gates, different metrics |
| Discrimination testing is automated | Probe pairs catch bias humans would miss |
| Calibration is enforced | Overconfident models are blocked, not just flagged |
| Explainability is mandatory | No SHAP values → no deployment |
| Drift monitoring works | PSI catches population shifts before they cause damage |
| Same evaluation harness interface | Statistical metrics plug into the same harness as LLM-as-judge metrics |
| Risk tier drives thresholds | `production_internal` has different bars than `production_customer_facing` |
