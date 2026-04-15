# Solution Lifecycle

How an AI solution moves through the chapter's platform — from a squad's first conversation to continuous production monitoring.

This is the chapter's operating model. Every AI solution in Risk Management follows this lifecycle, regardless of framework, LLM provider, or team. The platform automates the governance; the squad builds the solution.

---

## The Actors

| Actor | Role | What They Care About |
|---|---|---|
| **Squad** | Builds the AI solution. Owns the code, the deployment, the domain expertise. | "Can I ship this? What do I need to pass?" |
| **Chapter** | Builds and operates the governance platform. Provides reusable components, tracing SDK, evaluation harness. | "Is this solution safe, compliant, and monitored?" |
| **2nd/3rd Line** | Reviews evidence. Validates controls are working. | "Can we prove this to a regulator?" |
| **Platform** | The automated system. Discovers solutions, runs checks, produces evidence. | (No opinions — executes policy as code) |

---

## Phase 1: Intake & Instrumentation

*Before anything touches the platform.*

The squad comes to the chapter with an AI solution — built or in development. The chapter doesn't need their repo. What they need is a manifest, instrumentation, and test data.

### Step 1: Register the Solution

The squad registers their solution via the **Onboard Solution** wizard in the platform UI (`/onboard`), or by creating a `solution.yaml` manifest directly. The wizard walks through five steps — basics, type-specific configuration, guardrails, evaluation metrics, and a final review — then scaffolds the solution directory, manifest, and golden dataset automatically.

Alternatively, the squad fills out a `solution.yaml` manifest manually. This is the intake form — except it's a config file, not a Word doc.

```yaml
# solution.yaml — the squad's registration
name: "Claims Fraud Detection Agent"
id: "claims-fraud-agent"
description: >
  LLM agent that analyses claims data and flags potentially 
  fraudulent patterns for human investigation.
version: "1.0.0"
owner: "Claims Intelligence Squad"
contact: "claims-intel@petsure.com.au"
type: endpoint
endpoint:
  url: "https://claims-fraud-agent.internal.petsure.com.au/analyse"
  method: POST
  timeout_ms: 30000
```

No meeting. No governance form. A pull request with a YAML file.

### Step 2: Assign Risk Tier

The chapter assigns a risk tier based on the solution's description. Risk tier determines which guardrails fire and what thresholds apply.

```yaml
# Added by the chapter after review
risk_tier: production_customer_facing    # highest bar

# Risk tier determines:
# - Which guardrails are mandatory
# - What evaluation thresholds must be met
# - How frequently production monitoring runs
# - What evidence is required for audit
```

| Risk Tier | Description | Guardrail Bar | Eval Thresholds |
|---|---|---|---|
| `experimental` | Internal prototype, no real decisions | Logged only, no gates | No gate — scores logged |
| `production_internal` | Internal tool, supports human decisions | Standard gates | Moderate thresholds |
| `production_customer_facing` | Affects customers directly | All gates, strictest thresholds | Highest thresholds |

The risk tier conversation is the one human judgment call in the process. Everything after this is automated.

### Step 3: Instrument with Tracing SDK

The chapter provides a lightweight SDK. The squad adds it to their solution — a few decorators and context managers. This is the only code change the squad makes to interact with the platform.

```python
from chapter_platform import trace

@trace.solution("claims-fraud-agent")
async def analyse_claim(request: ClaimRequest) -> AnalysisResult:
    
    with trace.llm_call(model="gpt-4o"):
        initial_analysis = await llm.analyse(request.claim_data)
    
    with trace.tool_call("check_patterns"):
        patterns = check_fraud_patterns(request.claim_data)
    
    trace.reasoning_step(
        decision="Three pattern matches found — escalating to detailed analysis",
        action="run_detailed_analysis"
    )
    
    with trace.llm_call(model="gpt-4o"):
        detailed = await llm.detailed_analysis(initial_analysis, patterns)
    
    return AnalysisResult(
        risk_score=detailed.risk_score,
        findings=detailed.findings,
        recommendation=detailed.recommendation,
    )
```

The SDK emits structured spans that the platform reads. Without it, the platform can only see inputs and outputs. With it, the platform sees every LLM call, every tool invocation, every reasoning step.

See [../solutions/02-agentic-model-validation.md](../solutions/02-agentic-model-validation.md) for the full tracing contract specification.

### Step 4: Provide a Golden Dataset

The squad provides test cases that cover their solution's expected behaviour. The chapter provides the template and reviews for coverage — but the squad owns the domain knowledge.

```json
[
  {
    "input": { "claim_id": "SYNTH-001", "claim_data": "..." },
    "expected_output": {
      "risk_score": "LOW",
      "findings": [],
      "recommendation": "AUTO_APPROVE"
    },
    "category": "legitimate_claim"
  },
  {
    "input": { "claim_id": "SYNTH-002", "claim_data": "..." },
    "expected_output": {
      "risk_score": "HIGH",
      "findings": ["Pattern: multiple claims within 30 days"],
      "recommendation": "HUMAN_REVIEW"
    },
    "category": "suspicious_pattern"
  }
]
```

The golden dataset uses synthetic data — no real claims, no real customers. The chapter reviews for:
- Coverage across expected scenarios (happy path, edge cases, adversarial)
- Balance (not all pass or all fail)
- Alignment with the risk tier's requirements

The squad signs off on the dataset. The sign-off is recorded and becomes part of the evidence package.

### What the Chapter Does NOT Do in Phase 1

- Clone the squad's repo
- Review their code line by line
- Tell them which framework or LLM provider to use
- Rewrite their solution
- Attend their stand-ups

The chapter provides components, not opinions about implementation.

---

## Phase 2: Pre-Deployment Assessment

*The squad wants to go to production. The deployment gate decides.*

### Step 5: Platform Runs the Evaluation Harness

Automated, no human in the loop. The platform calls the squad's endpoint with every golden dataset entry and runs the evaluation suite.

```
EVALUATION RUN — Claims Fraud Detection Agent v1.0.0
  Risk tier: production_customer_facing
  Golden dataset: 52 test cases
  Judge model: gpt-4o

  Results:
    Faithfulness:           0.91  (threshold: 0.90)  PASS
    Answer Relevancy:       0.87  (threshold: 0.85)  PASS
    Contextual Precision:   0.83  (threshold: 0.80)  PASS
    Contextual Recall:      0.78  (threshold: 0.75)  PASS
    Hallucination:          0.06  (threshold: 0.10)  PASS
    Bias:                   0.04  (threshold: 0.10)  PASS
    Toxicity:               0.01  (threshold: 0.05)  PASS
```

### Step 6: Platform Runs Compliance Gates

The same eight checks that every solution passes through. Automated. No meeting.

```
COMPLIANCE GATE — Claims Fraud Detection Agent v1.0.0

  [PASS] Solution registration     — manifest complete, risk tier assigned
  [PASS] Evaluation harness        — all metrics above threshold
  [PASS] PII validation            — no PII in outputs (30 test cases)
  [PASS] Guardrail validation      — scope, injection, content safety (35 test cases)
  [PASS] Bias & toxicity           — within thresholds
  [PASS] Audit trail               — 100% trace completeness
  [PASS] Golden dataset sign-off   — reviewed and approved
  [PASS] Prompt governance         — prompts versioned, approval commit linked

  RESULT: APPROVED FOR DEPLOYMENT
```

### Step 7: Platform Reads Traces

During the golden dataset run, the instrumented solution emitted spans. The platform now has step-level visibility:

- Which LLM was called, how many times, token usage, cost
- Which tools were invoked, in what order
- How many reasoning iterations the agent took
- Where time was spent (retrieval vs generation vs guardrails)

This data populates the trace view in the portal and feeds into the evidence package.

### Step 8: Gate Decision

**PASS** — the solution is approved for deployment. The platform generates a deployment compliance report automatically. The report becomes evidence. No one wrote it. No one reviewed it manually. The pipeline produced it.

**FAIL** — the platform tells the squad exactly what failed and why.

```
COMPLIANCE GATE — FAILED

  [FAIL] Evaluation harness
         Faithfulness: 0.68 (threshold: 0.90)
         3 test cases failed:
           - SYNTH-017: Finding not grounded in claim data
           - SYNTH-031: Hallucinated a pattern that doesn't exist in the data
           - SYNTH-044: Recommendation contradicts findings

  Action required: Improve grounding in claim data. 
  Re-submit when ready — no meeting needed, just re-run the gate.
```

The squad fixes, re-submits. The gate runs again. This cycle repeats until the solution passes or the squad decides it's not ready. No governance committee sits in between — the gate is the committee.

---

## Phase 3: Production Monitoring

*The solution is deployed. The platform watches.*

### Step 9: Continuous Compliance Checks

Every response passes through the real-time compliance layer. The squad routes production traffic through the platform's proxy, or the platform polls the solution's trace output.

```
PRODUCTION COMPLIANCE (per response)
  [PASS] Scope adherence      12ms
  [PASS] PII scan              15ms
  [PASS] Faithfulness (0.93)  145ms
  [PASS] Bias (0.02)          130ms
  [PASS] Toxicity (0.00)      125ms
  [PASS] Audit trail             5ms

  Total: 187ms
  Result: AUTO-APPROVED
```

When a check fails:
- **Scope violation** → response blocked, refusal served
- **Faithfulness drift** → response regenerated with stricter grounding
- **PII detected** → response blocked, PII redacted, alert raised
- Every failure is logged with full context

### Step 10: Portfolio Dashboard

The chapter lead opens the portal. Every governed solution is visible.

```
COMPLIANCE HEALTH — All Solutions

  Claims Fraud Agent         v1.0.0  [GREEN]   99.2% pass rate   142 interactions/24h
  Policy Q&A                 v2.1.0  [GREEN]   98.8% pass rate   89 interactions/24h
  Model Validation Agent     v1.0.0  [GREEN]   100% pass rate    12 interactions/24h
  Credit Risk Explainer      v0.9.0  [AMBER]   94.1% pass rate   203 interactions/24h
                                               ↑ faithfulness degrading — review triggered
```

One view. All solutions. No asking squads for status updates.

### Step 11: Evidence Export

2nd line, 3rd line, or APRA asks "show me the controls for the Claims Fraud Agent."

One click. The platform generates a structured evidence package:
- Solution metadata and registration
- Deployment gate report (all 8 checks)
- Golden dataset with sign-off record
- Guardrail and PII test results
- Production monitoring summary (pass rates, failure counts, trends)
- Sampled interaction traces
- Prompt version history
- Policy-to-control-to-evidence mapping

Nobody wrote this report. Nobody compiled evidence from emails and spreadsheets. The platform produced it as a byproduct of operating.

### Step 12: Drift and Re-Evaluation

The platform monitors for degradation over time.

| Signal | Trigger | Action |
|---|---|---|
| Faithfulness declining | 7-day rolling average drops below threshold | Alert to squad + chapter lead |
| Bias score rising | Score exceeds 80% of threshold | Warning — not blocking yet |
| New prompt version deployed | Prompt hash changes | Automatic re-evaluation against golden dataset |
| Scheduled re-evaluation | Every 90 days (configurable by risk tier) | Full evaluation suite re-run |
| Model change | Squad updates LLM provider or model version | Mandatory re-evaluation before traffic resumes |

When drift is detected, the solution's portal status moves from GREEN to AMBER. If it crosses a hard threshold, it moves to RED and the chapter lead is notified. The squad is told exactly what degraded and by how much.

---

## The Full Lifecycle — One View

```
PHASE 1: INTAKE                    PHASE 2: ASSESSMENT              PHASE 3: PRODUCTION
─────────────────                  ────────────────────              ───────────────────

Squad registers                    Platform runs eval               Continuous compliance
  solution.yaml ──────────────────→  harness on golden  ──────────→  checks on every
                                     dataset                         response
Chapter assigns                    
  risk tier                        Platform runs 8                  Portfolio dashboard
                                     compliance gates                 updated continuously
Squad instruments                  
  with tracing SDK                 PASS → deploy                    Evidence export
                                   FAIL → fix + re-submit             on demand
Squad provides                     
  golden dataset                   Traces analysed                  Drift monitoring
                                                                      + re-evaluation

Human effort:                      Human effort:                    Human effort:
  - Write solution.yaml              - Fix failures (if any)          - None (automated)
  - Add tracing decorators            - That's it                     - Review alerts (if any)
  - Provide golden dataset
  - One risk tier conversation
```

---

## What the Squad Provides vs What the Chapter Provides

| Squad Provides | Chapter Provides |
|---|---|
| The AI solution (their code, their repo, their deployment) | Governance platform (portal, gates, monitoring) |
| `solution.yaml` manifest | Manifest schema and validation |
| Endpoint URL | Endpoint integration layer |
| Tracing instrumentation (using chapter's SDK) | Tracing SDK (lightweight package) |
| Golden dataset (domain knowledge) | Golden dataset template + coverage review |
| Domain expertise for risk tier discussion | Risk tier framework and threshold definitions |
| Fixes when gates fail | Clear failure messages with remediation guidance |

## What the Chapter Does NOT Need

- **The squad's repo** — the platform governs via endpoint + traces, not code review. Code quality and architecture are the squad's responsibility. The chapter may offer advisory reviews, but the platform doesn't require repo access to function.
- **The squad's prompts** — the tracing SDK emits a prompt hash for version tracking, not the prompt content. The chapter tracks that prompts are versioned and approved, not what they say.
- **Control over framework choice** — the tracing contract is framework-agnostic. LangChain, Claude SDK, raw API calls, custom framework — all emit the same spans.
- **Ongoing manual intervention** — once a solution passes the deployment gate and is instrumented, production monitoring is fully automated.

---

## Solution Types

The platform handles different types of AI solutions. Each type exercises the platform's components differently — different metrics matter, different guardrails are critical, different output shapes need evaluation.

| Type | What It Does | Platform Challenge | Key Metrics |
|---|---|---|---|
| **Q&A** | Answers questions from a knowledge base | Faithfulness, hallucination, citation | Faithfulness, answer relevancy, citation coverage |
| **Validation** | Reviews documents against a checklist, produces findings | Completeness, calibration of severity ratings | Faithfulness, completeness, calibration |
| **Classification** | Categorises inputs into defined buckets | Bias across categories, consistency | Accuracy, bias, consistency, calibration |
| **Extraction** | Pulls structured data from unstructured documents | Precision, recall, schema adherence | Extraction accuracy, schema compliance |
| **Summarisation** | Condenses long documents into shorter outputs | Nothing added (faithfulness), nothing critical lost (coverage) | Faithfulness, coverage, conciseness |
| **Generation** | Produces draft documents or content | Accuracy, tone, template compliance | Faithfulness, relevancy, format adherence |
| **Monitoring** | Watches a data stream and flags anomalies | False positive rate, alert fatigue, timeliness | Precision, recall, latency |
| **Orchestration** | Coordinates multi-step workflows across systems | Action boundaries, scope containment, audit trail | Scope adherence, action safety, trace completeness |
| **Recommendation** | Suggests actions or decisions for human review | Calibration, bias, human-in-the-loop design | Accuracy, bias, confidence calibration |

### Demo Coverage

The three demo solutions cover three different types, proving the platform adapts:

| Demo Solution | Type | Output Shape | Primary Governance Concern |
|---|---|---|---|
| Q&A Agent | Q&A | Free text with citations | Is the answer grounded in sources? |
| Validation Agent | Validation | Structured findings with severity | Are findings complete and calibrated? |
| Classification Agent | Classification | Category + confidence + reasoning | Is the classifier biased? Is it consistent? |

The same guardrail runner, evaluation harness, and compliance gates handle all three — but the metrics that matter shift based on type. The platform handles this through the solution manifest: the squad declares what type of solution it is, the chapter's thresholds and metric selection adjust accordingly.

---

## The Insight for Alex

"This lifecycle is the chapter's product. Not the guardrails themselves — the guardrails are a component. Not the eval harness — that's a component too. The product is this end-to-end lifecycle: a squad registers a solution, the platform assesses it, monitors it continuously, and produces evidence on demand. The chapter builds it once. Every squad in Risk Management uses it. That's what 'governance on autopilot' means in practice."
