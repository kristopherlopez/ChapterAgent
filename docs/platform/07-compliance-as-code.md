# Component #5: Compliance-as-Code Pipeline

This is the centrepiece. Alex called out the pain: manual effort to usher AI solutions through governance. This component turns that process into automated gates — demonstrated across three layers that cover the full governance lifecycle.

## The Problem It Solves

Today at PetSure Australia, getting an AI solution through governance means manual checklists, review meetings, Word documents, and email chains. Teams spend weeks on paperwork instead of building. The Governance Portal's job is to encode those policies into automated checks that run at every stage: before deployment, during production, and on demand for audit.

## Three Layers of Compliance-as-Code

```
LAYER 1: DEPLOYMENT GATE (CI/CD)
"Is this AI solution approved to go to production?"
Runs once, before deployment. The quality gate.

LAYER 2: PRODUCTION MONITORING (Real-Time)
"Is this AI solution still meeting policy right now?"
Runs on every response. Continuous compliance.

LAYER 3: EVIDENCE EXPORT (Audit)
"Can we prove this to a regulator?"
On-demand or scheduled. The audit trail.
```

Each layer maps to a different stakeholder:
- Layer 1 → the team (can I ship this?)
- Layer 2 → the Head of (are solutions behaving?)
- Layer 3 → 2nd/3rd line and APRA (show me the evidence)

---

## LAYER 1: Deployment Gate (CI/CD Pipeline)

Before the agent is deployed, it passes through an automated deployment gate in GitHub Actions. This is the same gate the Governance Portal would require for every team's AI solution. No manual review meeting. No governance form. The pipeline checks, and either promotes or blocks.

### What the pipeline checks

```yaml
# .github/workflows/compliance-gate.yml
name: Compliance Gate

on:
  push:
    branches: [main]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:

      # CHECK 1: Solution Registration
      # Policy: Every AI solution must be registered with metadata
      - name: Verify solution registration
        run: |
          python -m compliance.checks.registration \
            --solution-id chapter-agent \
            --check model-registry-entry \
            --check metadata-complete \
            --check risk-tier-assigned \
            --check owner-assigned

      # CHECK 2: Evaluation Harness (DeepEval)
      # Policy: Solution must pass quality thresholds for its risk tier
      - name: Run evaluation harness
        run: |
          deepeval test run tests/test_evaluation.py \
            --golden-dataset data/golden_dataset.json \
            --threshold-config config/thresholds_production_internal.yaml
        # Fails the pipeline if any metric is below threshold

      # CHECK 3: PII Validation
      # Policy: No PII leakage in outputs
      - name: Run PII leakage tests
        run: |
          python -m compliance.checks.pii \
            --test-suite data/pii_test_cases.json \
            --detector presidio \
            --threshold 0.0  # zero tolerance

      # CHECK 4: Guardrail Validation
      # Policy: All guardrails functional and tested
      - name: Run guardrail tests
        run: |
          python -m compliance.checks.guardrails \
            --test-suite data/guardrail_test_cases.json \
            --checks scope-adherence,prompt-injection,content-safety \
            --pass-rate 0.95

      # CHECK 5: Bias & Toxicity Sweep
      # Policy: Solution must not exhibit demographic bias
      - name: Run bias and toxicity evaluation
        run: |
          python -m compliance.checks.bias_toxicity \
            --golden-dataset data/golden_dataset.json \
            --bias-threshold 0.1 \
            --toxicity-threshold 0.05

      # CHECK 6: Audit Trail Completeness
      # Policy: Every interaction must be fully traced
      - name: Verify audit trail coverage
        run: |
          python -m compliance.checks.audit_trail \
            --sample-interactions 50 \
            --required-fields query,retrieval,generation,guardrails,response \
            --completeness-threshold 1.0  # 100% of fields present

      # CHECK 7: Golden Dataset Sign-Off
      # Policy: Human must have reviewed and approved the golden dataset
      - name: Verify golden dataset sign-off
        run: |
          python -m compliance.checks.human_signoff \
            --dataset data/golden_dataset.json \
            --signoff-file data/golden_dataset_signoff.json \
            --require-reviewer \
            --require-date

      # CHECK 8: Prompt Version Approval
      # Policy: System prompts must be version-controlled and approved
      - name: Verify prompt governance
        run: |
          python -m compliance.checks.prompt_governance \
            --prompt-dir prompts/ \
            --require-version \
            --require-approval-comment

      # GENERATE: Deployment Compliance Report
      - name: Generate compliance report
        if: success()
        run: |
          python -m compliance.report.generate \
            --output reports/deployment_compliance_$(date +%Y%m%d).json \
            --format json \
            --include-all-check-results

      # BLOCK or PROMOTE
      - name: Deployment decision
        if: success()
        run: echo "ALL GATES PASSED — approved for deployment"
```

### What the deployment report looks like

```json
{
  "solution": "chapter-capability-agent",
  "version": "1.2.0",
  "risk_tier": "production_internal",
  "deployment_date": "2026-04-05T14:30:00Z",
  "gate_results": {
    "solution_registration": {
      "status": "PASS",
      "policy": "AI-GOV-001: All AI solutions must be registered",
      "evidence": {
        "registry_id": "PETSURE-AI-2026-0042",
        "risk_tier": "production_internal",
        "owner": "Kristopher Lopez",
        "registration_date": "2026-04-01"
      }
    },
    "evaluation_harness": {
      "status": "PASS",
      "policy": "AI-GOV-003: Solutions must pass quality thresholds",
      "evidence": {
        "faithfulness": 0.93,
        "answer_relevancy": 0.88,
        "contextual_precision": 0.85,
        "contextual_recall": 0.79,
        "hallucination": 0.07,
        "threshold_config": "production_internal",
        "golden_dataset_size": 48,
        "test_run_id": "eval-2026-04-05-001"
      }
    },
    "pii_validation": {
      "status": "PASS",
      "policy": "AI-GOV-005: No PII in outputs",
      "evidence": {
        "test_cases_run": 30,
        "pii_detected": 0,
        "detector": "presidio",
        "entities_scanned": ["PERSON", "EMAIL", "PHONE", "AU_ABN", "AU_TFN"]
      }
    },
    "guardrail_validation": {
      "status": "PASS",
      "policy": "AI-GOV-006: All guardrails functional",
      "evidence": {
        "scope_adherence_pass_rate": 1.0,
        "prompt_injection_pass_rate": 0.97,
        "content_safety_pass_rate": 1.0,
        "test_cases_run": 35
      }
    },
    "bias_toxicity": {
      "status": "PASS",
      "policy": "AI-GOV-007: No demographic bias",
      "evidence": {
        "bias_score": 0.03,
        "toxicity_score": 0.01,
        "threshold_bias": 0.1,
        "threshold_toxicity": 0.05
      }
    },
    "audit_trail": {
      "status": "PASS",
      "policy": "AI-GOV-008: Full interaction tracing",
      "evidence": {
        "interactions_sampled": 50,
        "completeness": 1.0,
        "fields_verified": ["query", "retrieval", "generation", "guardrails", "response"]
      }
    },
    "golden_dataset_signoff": {
      "status": "PASS",
      "policy": "AI-GOV-009: Human review of test data",
      "evidence": {
        "reviewer": "Kristopher Lopez",
        "review_date": "2026-04-03",
        "dataset_version": "1.1",
        "entries_reviewed": 48,
        "entries_approved": 48
      }
    },
    "prompt_governance": {
      "status": "PASS",
      "policy": "AI-GOV-010: Prompt version control",
      "evidence": {
        "prompt_version": "2.3",
        "last_change": "2026-04-04",
        "approval_commit": "a3f8c21"
      }
    }
  },
  "overall_result": "APPROVED",
  "next_review_date": "2026-07-05"
}
```

### How it's demonstrated in the interview

Open the GitHub Actions run in a browser tab. Show the pipeline — eight checks, all green. "Before I brought this agent to you, it passed through the same deployment gate I'd build for every team. Eight policy checks, fully automated. No meeting. No form. Here's the report."

The key framing: "This pipeline IS the governance process. Not a step before the governance process. Not documentation of what happened at a governance meeting. The pipeline checks are the controls. The report is the evidence. If a team can't pass the gate, they can't deploy — and the gate tells them exactly what to fix."

---

## LAYER 2: Production Monitoring (Real-Time Per-Response)

Once deployed, every response passes through a real-time compliance pipeline. This is continuous monitoring — proving the solution is still meeting policy in production, not just at deployment time.

### What the trace panel shows on every response

```
PRODUCTION COMPLIANCE (this response)
  [PASS] Scope adherence     -- response within permitted domain              [custom]      12ms
  [PASS] Citation coverage    -- all claims trace to source documents          [custom]      8ms
  [PASS] PII scan             -- no personal data in output                   [Presidio]    15ms
  [PASS] Faithfulness (0.94)  -- claims supported by retrieved context        [DeepEval]    145ms
  [PASS] Bias (0.02)          -- no demographic bias detected                 [DeepEval]    130ms
  [PASS] Toxicity (0.00)      -- no harmful content                           [DeepEval]    125ms
  [PASS] Audit trail          -- full chain logged to immutable store         [custom]      5ms

  Judge: gpt-4o-mini | Total: 187ms
  Result: AUTO-APPROVED
  Session evidence: appended to compliance log
```

### When a gate fails — scope violation

```
PRODUCTION COMPLIANCE (this response)
  [FAIL] Scope adherence     -- query outside permitted domain                [custom]      10ms

  Result: BLOCKED
  Action: response replaced with scope refusal message
  Evidence: failure logged with query, classification, and refusal
```

### When a gate fails — faithfulness drift

```
PRODUCTION COMPLIANCE (this response)
  [PASS] Scope adherence     -- response within permitted domain              [custom]      12ms
  [PASS] Citation coverage    -- all claims trace to source documents          [custom]      8ms
  [PASS] PII scan             -- no personal data in output                   [Presidio]    14ms
  [FAIL] Faithfulness (0.61)  -- claims not supported by retrieved context    [DeepEval]    148ms
         Reason: "Statement about team size not grounded in any retrieved chunk"

  Result: BLOCKED
  Action: response regenerated with stricter grounding prompt
  Retry: regenerated response passed (faithfulness 0.91)
  Evidence: original failure + regeneration + retry result all logged
```

### The difference from Layer 1

| | Layer 1 (Deployment Gate) | Layer 2 (Production Monitoring) |
|---|---|---|
| **When** | Once, before deployment | Every response, continuously |
| **What it checks** | Full evaluation suite on golden dataset | Subset of checks on live traffic |
| **Judge model** | gpt-4o (accuracy over speed) | gpt-4o-mini (speed over accuracy) |
| **On failure** | Block deployment | Block or regenerate the response |
| **Evidence** | Deployment compliance report | Appended to session compliance log |
| **Latency budget** | Minutes (CI/CD pipeline) | < 200ms (real-time) |

### Production monitoring dashboard (visible in UI)

The agent tracks compliance metrics over time. The UI has a dashboard tab showing:

```
COMPLIANCE HEALTH (last 24 hours)

  Total interactions:     142
  Compliance pass rate:   98.6% (140/142)
  Failures:
    - Scope violation:    1 (blocked)
    - Faithfulness drift: 1 (regenerated, retry passed)

  Gate breakdown:
    Scope adherence:      100% pass (1 blocked correctly)
    Citation coverage:    100% pass
    PII scan:             100% pass
    Faithfulness:         99.3% pass (1 retry needed)
    Bias:                 100% pass
    Toxicity:             100% pass

  Avg compliance latency: 178ms
  Evidence log entries:   142 (complete)
```

This dashboard pattern is what every team's solution would have. The Governance Portal builds it once, every team gets it automatically.

### How it's demonstrated in the interview

Ask the agent a few questions. Point at the trace panel. "Every response just passed seven compliance checks in under 200 milliseconds. This is continuous monitoring — not a quarterly audit, not a manual review. The solution is proving it meets policy on every single interaction."

Then deliberately trigger a failure. Ask an out-of-scope question. "Watch the trace panel. Scope adherence failed. The response was blocked. The failure was logged with the query, the classification, and the refusal. That's a compliance event — captured automatically, with evidence."

Then show the dashboard. "Over the last [N] interactions, here's the compliance health of this solution. 98.6% pass rate. Two failures — both handled correctly. An auditor can see this at any time without asking anyone for a report."

---

## LAYER 3: Evidence Export (Audit & Regulatory)

On-demand or scheduled generation of compliance evidence packages. This is what 2nd line, 3rd line, and APRA actually need — structured proof that controls exist and are working.

### Evidence package structure

```
compliance-evidence/
  chapter-agent-v1.2.0/
    README.md                         # Summary and navigation guide

    1-solution-metadata/
      registration.json               # Solution registration record
      risk-tier-assignment.json        # Risk tier and justification
      ownership.json                   # Owner, team, escalation contacts

    2-deployment-evidence/
      deployment-gate-report.json      # Layer 1 report (all 8 checks)
      github-actions-run.url           # Link to the CI/CD run
      evaluation-scorecard.json        # DeepEval results on golden dataset
      evaluation-scorecard-ragas.json  # RAGAS complementary results

    3-golden-dataset/
      golden-dataset-v1.1.json         # The test data
      signoff-record.json              # Who reviewed, when, approval status
      coverage-analysis.json           # Which question categories, edge cases

    4-guardrail-evidence/
      guardrail-test-results.json      # Scope, injection, content safety tests
      pii-test-results.json            # PII leakage test results (Presidio)
      bias-toxicity-report.json        # Bias and toxicity sweep results

    5-production-monitoring/
      compliance-health-summary.json   # Aggregated pass rates, failure counts
      compliance-events.jsonl          # Every compliance event (pass and fail)
      failure-log.json                 # Detailed failure records with remediation
      drift-analysis.json              # Metric trends over time (improving/degrading?)

    6-audit-trail/
      interaction-sample.jsonl         # Full traces of sampled interactions
      audit-completeness.json          # % of interactions with complete traces
      retention-policy.json            # How long evidence is kept, where archived

    7-prompt-governance/
      prompt-versions.json             # Version history of all system prompts
      current-prompt.md                # Current active prompt
      change-log.json                  # What changed, when, approval commit

    8-framework-evaluation/
      cross-platform-scorecard.json    # Six-platform comparative evaluation
      framework-selection-rationale.md # Why this framework for this use case
```

### Policy-to-evidence mapping (the core of the export)

The evidence package includes a mapping that connects every governance policy to the specific automated check and its result. This is what an auditor actually needs — "show me the control and show me it's working."

```json
{
  "policy_evidence_map": [
    {
      "policy_id": "AI-GOV-001",
      "policy": "All AI solutions must be registered in the model registry",
      "control": "Automated registration check in CI/CD pipeline",
      "control_type": "preventive",
      "evidence_location": "2-deployment-evidence/deployment-gate-report.json#solution_registration",
      "last_verified": "2026-04-05T14:30:00Z",
      "status": "PASS",
      "frequency": "every deployment"
    },
    {
      "policy_id": "AI-GOV-003",
      "policy": "Solutions must pass quality thresholds for their risk tier",
      "control": "DeepEval evaluation harness as CI/CD gate",
      "control_type": "preventive",
      "evidence_location": "2-deployment-evidence/evaluation-scorecard.json",
      "last_verified": "2026-04-05T14:30:00Z",
      "status": "PASS",
      "frequency": "every deployment + continuous monitoring"
    },
    {
      "policy_id": "AI-GOV-005",
      "policy": "No PII in AI solution outputs",
      "control": "Presidio PII detection on every response + batch test suite",
      "control_type": "preventive + detective",
      "evidence_location": [
        "4-guardrail-evidence/pii-test-results.json",
        "5-production-monitoring/compliance-events.jsonl (filter: pii_scan)"
      ],
      "last_verified": "2026-04-05T16:45:00Z",
      "status": "PASS",
      "frequency": "every response (real-time) + every deployment (batch)"
    },
    {
      "policy_id": "AI-GOV-007",
      "policy": "AI solutions must not exhibit demographic bias",
      "control": "DeepEval BiasMetric in CI/CD + real-time monitoring",
      "control_type": "preventive + detective",
      "evidence_location": [
        "4-guardrail-evidence/bias-toxicity-report.json",
        "5-production-monitoring/compliance-events.jsonl (filter: bias)"
      ],
      "last_verified": "2026-04-05T16:45:00Z",
      "status": "PASS",
      "frequency": "every response (real-time) + every deployment (batch)"
    },
    {
      "policy_id": "AI-GOV-008",
      "policy": "All AI interactions must be fully traced for audit",
      "control": "Structured audit logging with completeness verification",
      "control_type": "detective",
      "evidence_location": "6-audit-trail/audit-completeness.json",
      "last_verified": "2026-04-05T16:45:00Z",
      "status": "PASS (100% completeness)",
      "frequency": "continuous"
    },
    {
      "policy_id": "AI-GOV-009",
      "policy": "Golden datasets must be human-reviewed and approved",
      "control": "Sign-off record with reviewer identity and date",
      "control_type": "preventive",
      "evidence_location": "3-golden-dataset/signoff-record.json",
      "last_verified": "2026-04-03T10:00:00Z",
      "status": "PASS",
      "frequency": "every golden dataset update"
    },
    {
      "policy_id": "AI-GOV-010",
      "policy": "System prompts must be version-controlled and approved",
      "control": "Prompt versioning with git-based approval tracking",
      "control_type": "preventive",
      "evidence_location": "7-prompt-governance/prompt-versions.json",
      "last_verified": "2026-04-04T09:00:00Z",
      "status": "PASS",
      "frequency": "every prompt change"
    }
  ]
}
```

### Evidence export in the UI

The "Export Compliance Evidence" button in the UI generates this entire package. Two formats:

1. **Structured (JSON)** — machine-readable, integrates with GRC tooling, queryable
2. **Human-readable (HTML report)** — formatted summary with navigation, suitable for emailing to a reviewer or presenting in a governance forum

The HTML report looks like:

```
COMPLIANCE EVIDENCE REPORT
Chapter Capability Agent v1.2.0
Generated: 2026-04-05T17:00:00Z

EXECUTIVE SUMMARY
  Solution:       Chapter Capability Agent
  Risk Tier:      Production Internal
  Owner:          Kristopher Lopez
  Status:         COMPLIANT
  Policies:       7/7 passing
  Next Review:    2026-07-05

DEPLOYMENT GATE
  Last deployment: 2026-04-05
  Pipeline: github.com/.../actions/runs/12345
  Result: 8/8 checks passed
  [View full deployment report →]

PRODUCTION MONITORING (last 30 days)
  Interactions:   3,847
  Pass rate:      99.1%
  Failures:       34 (31 scope blocks, 2 faithfulness retries, 1 PII catch)
  All failures handled automatically.
  [View compliance dashboard →]

POLICY COMPLIANCE
  AI-GOV-001  Solution Registration     PASS  [View evidence →]
  AI-GOV-003  Quality Thresholds        PASS  [View scorecard →]
  AI-GOV-005  PII Protection            PASS  [View test results →]
  AI-GOV-006  Guardrail Validation      PASS  [View test results →]
  AI-GOV-007  Bias & Fairness           PASS  [View report →]
  AI-GOV-008  Audit Trail               PASS  [View completeness →]
  AI-GOV-009  Golden Dataset Sign-Off   PASS  [View sign-off →]

AUDIT TRAIL SAMPLE
  [10 sampled interactions with full traces →]
```

### How it's demonstrated in the interview

After showing Layers 1 and 2, click "Export Compliance Evidence." Show the HTML report. "This was generated automatically. Nobody filled out a form. Nobody wrote a document. The evidence is a byproduct of the system running."

Then the key line: "Imagine this for every AI solution in Risk Management. A 2nd-line reviewer opens the compliance dashboard, sees the health of every solution across the portfolio. Clicks into one, gets this report. No request needed. No waiting. The evidence is already there."

"APRA asks 'show me your controls for AI model XYZ.' You don't convene a meeting. You don't pull together a slide deck. You export the evidence package. Every policy maps to a control. Every control maps to evidence. Every piece of evidence was generated automatically."

---

## Three Layers Working Together

```
BEFORE DEPLOYMENT          IN PRODUCTION              ON DEMAND

Layer 1:                   Layer 2:                   Layer 3:
Deployment Gate            Production Monitoring       Evidence Export

CI/CD pipeline runs        Every response passes      "Export Compliance
8 policy checks.           through 7 real-time        Evidence" generates
Pass → deploy.             compliance gates.          a structured report
Fail → block with          Pass → serve response.     with policy-to-evidence
specific remediation.      Fail → block/regenerate.   mapping.

Produces:                  Produces:                  Produces:
Deployment report          Compliance event log       Evidence package
Evaluation scorecard       Health dashboard           HTML/JSON report
                           Failure records            Audit trail sample

Stakeholder:               Stakeholder:               Stakeholder:
Team ("can I ship?")       Head of ("healthy?")       2nd/3rd line & APRA
```

## The reusable component pattern

The Governance Portal builds all three layers as reusable components:

| Governance Portal builds (reusable) | Team configures (specific) |
|---|---|
| Deployment gate framework (GitHub Actions template) | Their policy checks and thresholds for their risk tier |
| Real-time compliance pipeline (Python library) | Their guardrail thresholds and scope definitions |
| Evidence export generator | Their solution metadata and ownership |
| Policy-to-evidence mapping template | Their specific policy IDs and control descriptions |
| Compliance dashboard | Appears automatically when a team uses the pipeline |
| DeepEval metric configuration | Their golden dataset and evaluation thresholds |

A team adopts the compliance-as-code framework by:
1. Adding the deployment gate template to their GitHub Actions
2. Importing the compliance pipeline library into their agent
3. Writing their golden dataset and configuring their thresholds
4. Registering their solution in the model registry

From that point: deployment gates, production monitoring, and evidence export all work automatically. The team writes no compliance code. They configure the Governance Portal's components.

## What it demonstrates (all three layers)

- The full governance lifecycle automated — not just one layer
- Direct solution to the pain point Alex raised (manual governance effort)
- Policy-to-code-to-evidence mapping in action
- Compliance evidence as a byproduct, not a burden
- The gate library pattern teams would consume
- How 2nd and 3rd line get their evidence without requesting it
- APRA-ready evidence generation
- The difference between "guardrails" (Layer 2) and "compliance-as-code" (all three layers)
