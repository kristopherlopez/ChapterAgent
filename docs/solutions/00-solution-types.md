# Solution Types

## What This Is

A taxonomy of AI solution types — both GenAI and traditional ML — that squads across Risk Management commonly build. Each type has a different output shape, different primary governance concerns, and exercises the platform's reusable components differently.

The Chapter doesn't prescribe what squads build. It governs what they ship. This taxonomy defines the patterns the platform expects to see — so guardrails, evaluation metrics, and compliance gates can be configured appropriately for each.

**Two categories:**
- **GenAI solutions** — LLM-powered: Q&A, classification, validation, summarisation, extraction, generation
- **ML solutions** — Traditional/statistical ML: scoring, anomaly detection, forecasting, segmentation, ranking

The platform governs both. The reusable components are the same. The metrics, thresholds, and monitoring patterns shift based on category and type.

## Why Solution Types Matter

Not all AI solutions are the same. A Q&A agent that hallucinates a financial figure is a different kind of failure than a classifier that exhibits demographic bias. The platform's reusable components are generic — but the **metric emphasis, guardrail configuration, and evaluation strategy** shift based on solution type.

The solution manifest (`solution.yaml`) declares the type. The platform uses it to:

- Select the right evaluation metrics and thresholds
- Configure guardrails appropriate to the output shape
- Display the right views in the portal
- Generate the right compliance evidence

## Taxonomy

### Q&A

**Category:** GenAI

**What it does:** Answers questions from a document corpus. Retrieves context, generates a response, cites sources.

**Output shape:** Free text with citations.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Faithfulness | Every claim must be grounded in the source documents — a hallucinated answer is the primary failure mode |
| Citation coverage | Every factual claim must be traceable to a specific source, page, and section |
| Scope containment | The agent must stay within the boundaries of its document corpus (configurable via scope dial) |
| Temporal accuracy | Figures and statements must be attributed to the correct reporting period |

**Example use cases:**
- Investor relations Q&A over annual reports
- Policy lookup over internal documentation
- Regulatory research over published guidance

**Demo solution:** `01-qa-agent.md`

---

### Classification

**Category:** GenAI

**What it does:** Categorises incoming items into predefined categories. Assigns a primary classification, optional secondary classification, confidence score, and reasoning.

**Output shape:** Structured output — category, confidence, reasoning.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Accuracy | The classification must be correct — the primary failure mode is miscategorisation |
| Bias | The classifier must produce identical output regardless of demographic attributes in the input |
| Consistency | Same input must produce same output every time — non-determinism is a governance risk |
| Calibration | Confidence scores must reflect actual accuracy — a classifier that says 95% but is right 60% of the time is dangerous |

**Example use cases:**
- Operational risk event classification (Basel II categories)
- Customer complaint triage and routing
- Regulatory mapping (which regulation applies to a control gap)
- Risk tiering (high/medium/low)

**Demo solution:** `03-classification-agent.md`

---

### Validation

**Category:** GenAI

**What it does:** Reviews documentation or artefacts against a checklist or standard. Identifies gaps, assesses risk, produces structured findings with severity ratings.

**Output shape:** Structured findings — description, severity, recommendation.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Completeness | The agent must identify all gaps — a missed finding is the primary failure mode |
| Calibration | Severity ratings must be appropriate — over-rating creates noise, under-rating creates risk |
| Faithfulness | Findings must be grounded in the documentation provided, not fabricated |
| Scope adherence | The agent must stay within its validation domain |

**Example use cases:**
- AI model documentation review
- Control effectiveness assessment
- Regulatory compliance gap analysis
- Audit finding validation

**Demo solution:** `02-agentic-model-validation.md`

---

### Summarisation

**Category:** GenAI

**What it does:** Condenses long documents or collections of documents into concise summaries. May be extractive (pulling key sentences) or abstractive (generating new text that captures the essence).

**Output shape:** Free text — condensed narrative, optionally with key points or bullet summaries.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Faithfulness | The summary must not introduce claims absent from the source material |
| Coverage | The summary must capture the material points — omitting a critical finding is a failure |
| Bias | The summary must not selectively emphasise or downplay information |
| Attribution | Claims should be traceable to source sections, especially for multi-document summarisation |

**Example use cases:**
- Board paper summarisation
- Incident report condensation
- Regulatory change impact summaries
- Meeting minutes generation

**Demo solution:** None yet

---

### Extraction

**Category:** GenAI

**What it does:** Pulls structured data from unstructured documents. Identifies entities, relationships, figures, dates, or other specified fields and outputs them in a structured format.

**Output shape:** Structured output — extracted fields, values, source locations.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Accuracy | Extracted values must exactly match what's in the source document |
| Completeness | All instances of the target data must be found — missed extractions are the primary failure mode |
| Schema conformance | Output must match the expected schema — wrong field types or missing required fields break downstream systems |
| Source traceability | Every extracted value must link to its location in the source document |

**Example use cases:**
- Contract clause extraction
- Financial figure extraction from reports
- Regulatory obligation identification
- Risk event detail extraction from incident reports

**Demo solution:** None yet

---

### Generation

**Category:** GenAI

**What it does:** Creates new content based on inputs, templates, or instructions. May generate reports, correspondence, documentation, or other artefacts.

**Output shape:** Free text or structured document — varies by use case.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Hallucination | Generated content must not fabricate facts, figures, or references |
| Tone and compliance | Content must meet organisational standards for language, tone, and regulatory appropriateness |
| Template adherence | If generating from a template, all required sections must be present and correctly populated |
| PII | Generated content must not inadvertently include personal information from training data |

**Example use cases:**
- Draft regulatory responses
- Model documentation generation
- Risk assessment report drafting
- Customer communication templates

**Demo solution:** None yet

---

### Scoring

**Category:** ML

**What it does:** Assigns a numeric risk score or probability to an entity (customer, transaction, claim, counterparty) based on features. The score drives downstream decisions — approve, refer, decline, investigate.

**Output shape:** Numeric score (0–1 probability or banded score), feature contributions, decision recommendation.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Discrimination | Scores must not systematically disadvantage protected groups — this is the primary regulatory concern for any scoring model |
| Calibration | A model that outputs 0.8 probability should be correct ~80% of the time — miscalibrated scores lead to bad decisions at scale |
| Stability | Score distributions must remain stable over time — sudden shifts indicate data drift or population change |
| Explainability | Every score must be accompanied by top feature contributions — regulators and customers have a right to understand why |
| Performance degradation | Accuracy (AUC, Gini, precision/recall) must be monitored continuously — a model that was accurate at deployment can degrade silently |

**Example use cases:**
- Credit risk scoring (PD models)
- Fraud probability scoring
- Claims risk scoring
- Counterparty risk assessment
- Customer churn probability

**Demo solution:** None yet

---

### Anomaly Detection

**Category:** ML

**What it does:** Monitors a data stream and flags observations that deviate from expected patterns. May operate in real-time (per-transaction) or batch (periodic sweep).

**Output shape:** Binary flag (anomaly/normal) or anomaly score, with contributing factors and contextual data.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| False positive rate | Too many false alerts cause alert fatigue — investigators stop trusting the model |
| False negative rate | Missed anomalies are the primary risk — an undetected fraud or compliance breach |
| Timeliness | Detection must happen within the operational window — a fraud flag 24 hours late has limited value |
| Threshold stability | Detection thresholds must be justified and reviewed — too tight creates noise, too loose creates gaps |
| Population drift | Normal behaviour evolves — the model must distinguish genuine anomalies from shifted baselines |

**Example use cases:**
- Transaction monitoring (AML/CTF)
- Unusual trading pattern detection
- Operational risk event early warning
- IT security anomaly detection
- Claims fraud pattern identification

**Demo solution:** None yet

---

### Forecasting

**Category:** ML

**What it does:** Predicts future values of a time-dependent variable based on historical patterns, trends, and external factors. Outputs are typically point estimates with confidence intervals over a forecast horizon.

**Output shape:** Predicted values over time horizon, confidence intervals, trend decomposition.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Accuracy | Forecast error directly impacts capital reserves, provisioning, and business planning |
| Uncertainty quantification | Point estimates without confidence intervals are dangerous — decision-makers need to understand the range of outcomes |
| Regime sensitivity | Models trained on stable periods may fail during market stress — backtesting must include stress scenarios |
| Stale model detection | Forecasting models degrade as the data-generating process changes — monitoring forecast error over time is critical |
| Assumption transparency | Key assumptions (stationarity, seasonality, external factors) must be documented and reviewable |

**Example use cases:**
- Credit loss provisioning (IFRS 9 / AASB 9)
- Capital adequacy forecasting
- Claims volume forecasting
- Operational loss forecasting
- Liquidity stress testing

**Demo solution:** None yet

---

### Segmentation

**Category:** ML

**What it does:** Groups entities into distinct clusters based on shared characteristics. Segments may be used for differentiated treatment, targeted strategies, or population analysis.

**Output shape:** Segment assignment, segment profile/description, distance to cluster centre.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Discrimination | Segments must not act as proxies for protected attributes — a "high-risk" segment that correlates with ethnicity is a regulatory failure |
| Stability | Segment definitions must be stable enough for business processes to operate on them — unstable clusters create operational chaos |
| Interpretability | Each segment must have a human-understandable profile — "Cluster 3" is not a useful business concept |
| Coverage | Every entity must be assigned to a segment — unassigned entities fall through operational cracks |
| Granularity | Too few segments lose nuance, too many are unmanageable — the right number is a governance decision |

**Example use cases:**
- Customer risk segmentation
- Portfolio stratification
- Behavioural cohort analysis
- Peer group construction for benchmarking
- Claims population analysis

**Demo solution:** None yet

---

### Ranking

**Category:** ML

**What it does:** Orders a set of items by priority, relevance, or risk. Used to direct limited human attention to the highest-value or highest-risk items first.

**Output shape:** Ordered list with rank scores, ranking rationale, and optional tier assignment.

**Primary governance concerns:**

| Concern | Why |
|---|---|
| Bias | Ranking criteria must not systematically deprioritise items associated with protected groups |
| Calibration | Items ranked highly must genuinely be higher priority — a ranking model that puts low-risk items at the top wastes investigator time |
| Coverage | Important items must not be systematically ranked low — a missed high-risk item at the bottom of a queue is a governance failure |
| Transparency | The ranking criteria and their weights must be explainable — "the model ranked it #47" is not sufficient for audit |
| Threshold sensitivity | If ranks are converted to tiers (investigate/monitor/ignore), the thresholds must be justified and monitored |

**Example use cases:**
- Alert prioritisation (AML, fraud, compliance)
- Audit finding severity ranking
- Risk assessment prioritisation
- Claims investigation queue ordering
- Remediation action prioritisation

**Demo solution:** None yet

---

## How Types Map to Platform Components

The platform's reusable components work across all solution types. The difference is **emphasis** — which metrics are primary, which guardrails are critical, which failure modes the platform prioritises.

| | | GenAI | GenAI | GenAI | GenAI | GenAI | GenAI | ML | ML | ML | ML | ML |
| Component | Category → | Q&A | Classification | Validation | Summarisation | Extraction | Generation | Scoring | Anomaly Detection | Forecasting | Segmentation | Ranking |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Faithfulness guardrail** | | Primary | Secondary | Primary | Primary | N/A | Primary | N/A | N/A | N/A | N/A | N/A |
| **Bias / discrimination** | | Standard | Critical | Standard | Important | Standard | Standard | Critical | Standard | Standard | Critical | Critical |
| **Scope guardrail** | | Primary | Primary | Primary | Standard | Standard | Standard | Standard | Standard | Standard | Standard | Standard |
| **PII guardrail** | | Standard | Standard | Standard | Standard | Standard | Important | Important | Standard | Standard | Important | Standard |
| **Citation metric** | | Primary | N/A | N/A | Important | Primary | N/A | N/A | N/A | N/A | N/A | N/A |
| **Accuracy metric** | | Secondary | Primary | Secondary | N/A | Primary | N/A | Primary | Important | Primary | N/A | Important |
| **Calibration metric** | | N/A | Primary | Primary | N/A | N/A | N/A | Critical | N/A | Important | N/A | Important |
| **Consistency metric** | | N/A | Primary | N/A | N/A | Important | N/A | Important | N/A | N/A | Primary | N/A |
| **Stability / drift** | | N/A | N/A | N/A | N/A | N/A | N/A | Primary | Primary | Primary | Primary | Primary |
| **Explainability** | | N/A | N/A | N/A | N/A | N/A | N/A | Critical | Important | Important | Primary | Important |
| **False positive rate** | | N/A | N/A | N/A | N/A | N/A | N/A | Important | Critical | N/A | N/A | Important |
| **False negative rate** | | N/A | N/A | N/A | N/A | N/A | N/A | Important | Critical | N/A | N/A | Important |
| **Uncertainty quantification** | | N/A | N/A | N/A | N/A | N/A | N/A | Important | N/A | Critical | N/A | N/A |

**Standard** = checked at baseline thresholds. **Primary** = the main thing the platform measures for this solution type. **Critical** = elevated thresholds and additional test cases (e.g. bias probes for classifiers, discrimination testing for scoring models). **Important** = meaningful but not the primary governance concern. **N/A** = not applicable to this solution type.

### GenAI vs ML — What Changes in the Platform

The platform's reusable components work for both GenAI and ML solutions. The key differences are in **what gets measured and how**:

| Dimension | GenAI Solutions | ML Solutions |
|---|---|---|
| **Primary failure mode** | Hallucination, unfaithfulness, scope violation | Discrimination, drift, miscalibration |
| **Evaluation method** | LLM-as-judge (DeepEval) on golden dataset | Statistical metrics (AUC, Gini, PSI, KS) on holdout/production data |
| **Real-time monitoring** | Per-response compliance checks | Population-level monitoring (score distributions, feature drift, performance decay) |
| **Guardrail emphasis** | Content safety (faithfulness, PII, scope) | Fairness (discrimination, proxy detection, disparate impact) |
| **Evidence emphasis** | Interaction traces, response-level audit trail | Model cards, validation reports, ongoing performance reports |
| **Drift signal** | Faithfulness score degradation, retrieval quality decline | PSI/KS on features and scores, accuracy decay, population shift |
| **Explainability** | Citation coverage, retrieval transparency | Feature importance (SHAP/LIME), decision rationale |
| **Regulatory focus** | Responsible AI principles, content governance | CPS 230, SPS 220, Basel requirements, anti-discrimination law |

## Adding New Solution Types

The taxonomy is not closed. When a squad builds something that doesn't fit these patterns, the Chapter:

1. Identifies the output shape and primary governance concerns
2. Defines which metrics and guardrails apply
3. Sets thresholds appropriate to the risk tier
4. Adds the type to this taxonomy
5. Updates the platform's metric selection logic

The platform's reusable components don't change — only the configuration does. That's the point of building components, not solutions.
