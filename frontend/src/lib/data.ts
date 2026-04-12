import type {
  SolutionSummary,
  SolutionDetail,
  FrameworkScore,
  TraceStep,
  GovernanceDocument,
  GovernanceDocumentDetail,
  Control,
  RuntimeGuardrail,
  RiskControlMapping,
  ControlThreshold,
  IncidentResponse,
  RegulatoryRequirement,
} from "./types";

// --- Hardcoded fallback data (matches results/ JSON files) ---

export const solutions: SolutionSummary[] = [
  {
    id: "cba-annual-report-qa",
    name: "CBA Annual Report Q&A",
    description:
      "Answers questions about CBA's 2024 Annual Report with source citations",
    category: "ai",
    owner: "Chapter Platform Team",
    riskTier: "Customer-Facing",
    guardrailsSummary: "8/8 PASS",
    evalScore: 0.91,
    gateResult: "pass",
    health: "pass",
    lastRun: "2026-04-10 14:32 AEST",
    lastTested: "2026-04-12 08:15 AEST",
    healthHistory: [
      { date: "2026-03-29", status: "pass" },
      { date: "2026-03-30", status: "pass" },
      { date: "2026-03-31", status: "pass" },
      { date: "2026-04-01", status: "pass" },
      { date: "2026-04-02", status: "pass" },
      { date: "2026-04-03", status: "warn" },
      { date: "2026-04-04", status: "pass" },
      { date: "2026-04-05", status: "pass" },
      { date: "2026-04-06", status: "pass" },
      { date: "2026-04-07", status: "pass" },
      { date: "2026-04-08", status: "pass" },
      { date: "2026-04-09", status: "pass" },
      { date: "2026-04-10", status: "pass" },
      { date: "2026-04-11", status: "pass" },
      { date: "2026-04-12", status: "pass" },
    ],
  },
  {
    id: "agentic-model-validation",
    name: "Model Validation Agent",
    description:
      "LLM agent that reads model documentation, runs validation checks, and drafts findings",
    category: "ai",
    owner: "Risk Modelling Squad",
    riskTier: "High",
    guardrailsSummary: "4/4 PASS",
    evalScore: 0.88,
    gateResult: "pass",
    health: "pass",
    lastRun: "2026-04-10 14:35 AEST",
    lastTested: "2026-04-10 14:35 AEST",
    healthHistory: [
      { date: "2026-03-29", status: "pass" },
      { date: "2026-03-30", status: "pass" },
      { date: "2026-03-31", status: "fail" },
      { date: "2026-04-01", status: "fail" },
      { date: "2026-04-02", status: "pass" },
      { date: "2026-04-03", status: "pass" },
      { date: "2026-04-04", status: "pass" },
      { date: "2026-04-05", status: "pass" },
      { date: "2026-04-06", status: "warn" },
      { date: "2026-04-07", status: "pass" },
      { date: "2026-04-08", status: "pass" },
      { date: "2026-04-09", status: "pass" },
      { date: "2026-04-10", status: "pass" },
    ],
  },
  {
    id: "multi-platform-agent",
    name: "Multi-Platform Agent",
    description:
      "Same agent implemented across 3 frameworks for comparative evaluation",
    category: "ai",
    owner: "Chapter Platform Team",
    riskTier: "Medium",
    guardrailsSummary: "5/6 FAIL",
    evalScore: 0.72,
    gateResult: "fail",
    health: "fail",
    lastRun: "2026-04-10 14:38 AEST",
    lastTested: "2026-04-10 14:38 AEST",
    healthHistory: [
      { date: "2026-03-29", status: "pass" },
      { date: "2026-03-30", status: "pass" },
      { date: "2026-03-31", status: "warn" },
      { date: "2026-04-01", status: "warn" },
      { date: "2026-04-02", status: "fail" },
      { date: "2026-04-03", status: "fail" },
      { date: "2026-04-04", status: "fail" },
      { date: "2026-04-05", status: "fail" },
      { date: "2026-04-06", status: "fail" },
      { date: "2026-04-07", status: "fail" },
      { date: "2026-04-08", status: "fail" },
      { date: "2026-04-09", status: "fail" },
      { date: "2026-04-10", status: "fail" },
    ],
  },
  {
    id: "credit-default-scorer",
    name: "Credit Default Scorer",
    description:
      "Predicts credit card default probability using customer payment history and demographics",
    category: "ml",
    owner: "Chapter Platform Team",
    riskTier: "Internal",
    guardrailsSummary: "4/4 PASS",
    evalScore: 0.82,
    gateResult: "pass",
    health: "pass",
    lastRun: "2026-04-10 15:10 AEST",
    lastTested: "2026-03-28 09:00 AEST",
    healthHistory: [
      { date: "2026-03-14", status: "pass" },
      { date: "2026-03-15", status: "pass" },
      { date: "2026-03-16", status: "pass" },
      { date: "2026-03-17", status: "pass" },
      { date: "2026-03-18", status: "pass" },
      { date: "2026-03-19", status: "pass" },
      { date: "2026-03-20", status: "pass" },
      { date: "2026-03-21", status: "pass" },
      { date: "2026-03-22", status: "warn" },
      { date: "2026-03-23", status: "pass" },
      { date: "2026-03-24", status: "pass" },
      { date: "2026-03-25", status: "pass" },
      { date: "2026-03-26", status: "pass" },
      { date: "2026-03-27", status: "pass" },
      { date: "2026-03-28", status: "pass" },
    ],
  },
];

export const solutionDetails: Record<string, SolutionDetail> = {
  "cba-annual-report-qa": {
    ...solutions[0],
    guardrails: [
      { name: "Prompt Injection", result: "pass", detail: "0 injections detected" },
      { name: "Scope Containment", result: "pass", detail: "Query mapped to topic: financial_performance" },
      { name: "PII Detection", result: "pass", detail: "0 PII instances found" },
      { name: "Faithfulness Check", result: "pass", detail: "Score: 0.94 (threshold: 0.90)" },
      { name: "Bias Scan", result: "pass", detail: "Score: 0.02 (threshold: 0.05)" },
      { name: "Toxicity Scan", result: "pass", detail: "Score: 0.00 (threshold: 0.05)" },
      { name: "Citation Coverage", result: "pass", detail: "98% claims cited (threshold: 95%)" },
      { name: "Temporal Accuracy", result: "pass", detail: "Score: 0.96" },
    ],
    evaluation: [
      { metric: "Faithfulness", score: 0.94, threshold: 0.90, status: "pass" },
      { metric: "Answer Relevancy", score: 0.91, threshold: 0.85, status: "pass" },
      { metric: "Context Precision", score: 0.85, threshold: 0.80, status: "pass" },
      { metric: "Context Recall", score: 0.79, threshold: 0.75, status: "pass" },
      { metric: "Hallucination", score: 0.06, threshold: 0.10, status: "pass" },
      { metric: "Citation Coverage", score: 0.98, threshold: 0.95, status: "pass" },
      { metric: "Boundary Adherence", score: 0.98, threshold: 0.95, status: "pass" },
      { metric: "Temporal Accuracy", score: 0.92, threshold: 0.90, status: "pass" },
      { metric: "Bias", score: 0.02, threshold: 0.05, status: "pass" },
      { metric: "Toxicity", score: 0.01, threshold: 0.05, status: "pass" },
    ],
    complianceGate: {
      gate: "Deployment Gate",
      result: "pass",
      reason: "All 8 guardrails passed. All 10 evaluation metrics above production_customer_facing thresholds. Evidence report generated.",
      timestamp: "2026-04-10 14:32 AEST",
    },
  },
  "agentic-model-validation": {
    ...solutions[1],
    guardrails: [
      { name: "Scope Containment", result: "pass", detail: "0 out-of-scope responses" },
      { name: "PII Detection", result: "pass", detail: "0 PII instances found" },
      { name: "Faithfulness Check", result: "pass", detail: "Score: 0.91" },
      { name: "Bias Scan", result: "pass", detail: "Score: 0.01" },
    ],
    evaluation: [
      { metric: "Faithfulness", score: 0.90, threshold: 0.85, status: "pass" },
      { metric: "Answer Relevancy", score: 0.88, threshold: 0.80, status: "pass" },
    ],
    complianceGate: {
      gate: "Deployment Gate",
      result: "pass",
      reason: "All guardrails passed, evaluation scores above thresholds",
      timestamp: "2026-04-10 14:35 AEST",
    },
  },
  "multi-platform-agent": {
    ...solutions[2],
    guardrails: [
      { name: "Scope Containment", result: "pass", detail: "0 out-of-scope responses" },
      { name: "PII Detection", result: "fail", detail: "3 PII instances detected in responses" },
      { name: "Faithfulness Check", result: "pass", detail: "Score: 0.78" },
      { name: "Bias Scan", result: "pass", detail: "Score: 0.04" },
      { name: "Toxicity Scan", result: "pass", detail: "Score: 0.01" },
      { name: "Citation Presence", result: "warn", detail: "72% responses cited" },
    ],
    evaluation: [
      { metric: "Faithfulness", score: 0.72, threshold: 0.80, status: "fail" },
      { metric: "Answer Relevancy", score: 0.75, threshold: 0.75, status: "pass" },
    ],
    complianceGate: {
      gate: "Deployment Gate",
      result: "fail",
      reason: "PII guardrail failure — 3 instances detected. Faithfulness below threshold (0.72 < 0.80).",
      timestamp: "2026-04-10 14:38 AEST",
    },
  },
  "credit-default-scorer": {
    ...solutions[3],
    guardrails: [
      { name: "Discrimination Check", result: "pass", detail: "Demographic parity diff: 0.03 (threshold: 0.05)" },
      { name: "Calibration Check", result: "pass", detail: "Brier score: 0.17 (threshold: 0.20)" },
      { name: "Stability Check", result: "pass", detail: "PSI: 0.08 (threshold: 0.25)" },
      { name: "Explainability Check", result: "pass", detail: "SHAP coverage: 100%" },
    ],
    evaluation: [
      { metric: "AUC-ROC", score: 0.78, threshold: 0.70, status: "pass" },
      { metric: "Gini", score: 0.56, threshold: 0.40, status: "pass" },
      { metric: "Brier Score", score: 0.17, threshold: 0.20, status: "pass" },
      { metric: "ECE", score: 0.03, threshold: 0.05, status: "pass" },
      { metric: "Demographic Parity Diff", score: 0.03, threshold: 0.05, status: "pass" },
      { metric: "Equalised Odds Diff", score: 0.04, threshold: 0.05, status: "pass" },
      { metric: "Disparate Impact Ratio", score: 0.87, threshold: 0.80, status: "pass" },
      { metric: "PSI", score: 0.08, threshold: 0.25, status: "pass" },
      { metric: "SHAP Coverage", score: 1.0, threshold: 1.0, status: "pass" },
    ],
    complianceGate: {
      gate: "Deployment Gate",
      result: "pass",
      reason: "All 4 guardrails passed. All 9 evaluation metrics within thresholds. Fairness and calibration validated.",
      timestamp: "2026-04-10 15:10 AEST",
    },
  },
};

export const frameworkScores: FrameworkScore[] = [
  {
    framework: "Claude Agent SDK",
    evalScore: 0.89,
    guardrailsPass: "6/6",
    latencyAvgMs: 1200,
    tokenUsageAvg: 1650,
    costPerRun: 0.003,
    gateResult: "pass",
  },
  {
    framework: "OpenAI Agents SDK",
    evalScore: 0.85,
    guardrailsPass: "6/6",
    latencyAvgMs: 1400,
    tokenUsageAvg: 1920,
    costPerRun: 0.004,
    gateResult: "pass",
  },
  {
    framework: "LangChain / LangGraph",
    evalScore: 0.72,
    guardrailsPass: "5/6",
    latencyAvgMs: 1800,
    tokenUsageAvg: 2100,
    costPerRun: 0.005,
    gateResult: "fail",
  },
];

export const solutionTraces: Record<string, TraceStep[]> = {
  "cba-annual-report-qa": [
    { step: 1, label: "Query received", durationMs: 0 },
    { step: 2, label: "Scope check (topic graph)", durationMs: 12, detail: "Topic: financial_performance | Scope level: 1 | Result: in-scope" },
    { step: 3, label: "Context retrieval (hybrid search)", durationMs: 120, detail: "4 chunks retrieved from ChromaDB, top score: 0.94" },
    { step: 4, label: "LLM generation (OpenAI gpt-4o)", durationMs: 1340, detail: "Tokens: 1,847 | Cost: $0.0034 | Citations: 1" },
    { step: 5, label: "Guardrail pipeline", durationMs: 187, detail: "8/8 passed | Faithfulness: 0.94 | PII: clean | Scope: pass" },
    { step: 6, label: "Response returned", durationMs: 1659, detail: "Total end-to-end latency" },
  ],
  "agentic-model-validation": [
    { step: 1, label: "Workflow initiated", durationMs: 0 },
    { step: 2, label: "Document ingestion", durationMs: 230, detail: "Model doc parsed, 12 sections extracted" },
    { step: 3, label: "Validation check 1: completeness", durationMs: 890, detail: "Tokens: 2,100 | All required sections present" },
    { step: 4, label: "Validation check 2: methodology", durationMs: 1120, detail: "Tokens: 2,450 | 2 findings flagged" },
    { step: 5, label: "Findings draft generation", durationMs: 1560, detail: "Tokens: 3,200 | 2 findings drafted" },
    { step: 6, label: "Guardrail checks", durationMs: 145, detail: "4/4 passed" },
    { step: 7, label: "Workflow complete", durationMs: 3945, detail: "Total end-to-end" },
  ],
  "multi-platform-agent": [
    { step: 1, label: "Query received", durationMs: 0 },
    { step: 2, label: "Context retrieval", durationMs: 95, detail: "3 chunks retrieved" },
    { step: 3, label: "LLM generation (LangChain)", durationMs: 1800, detail: "Tokens: 2,100 | Cost: $0.005" },
    { step: 4, label: "Guardrail checks", durationMs: 210, detail: "5/6 — PII FAIL" },
    { step: 5, label: "Response blocked", durationMs: 2105, detail: "PII detected, response not delivered" },
  ],
  "credit-default-scorer": [
    { step: 1, label: "Scoring request received", durationMs: 0 },
    { step: 2, label: "Feature engineering", durationMs: 15, detail: "23 features prepared, 4 protected attributes flagged" },
    { step: 3, label: "Model inference (GradientBoosting)", durationMs: 8, detail: "Default probability: 0.23" },
    { step: 4, label: "SHAP explanation generated", durationMs: 45, detail: "Top factors: PAY_0, BILL_AMT1, PAY_AMT1" },
    { step: 5, label: "Fairness guardrails", durationMs: 32, detail: "4/4 passed | Demographic parity: 0.03 | Disparate impact: 0.87" },
    { step: 6, label: "Score returned", durationMs: 100, detail: "Total end-to-end latency" },
  ],
};

// --- AI-GOV Policy Descriptions (for tooltips) ---

export const aiGovPolicies: Record<string, string> = {
  "AI-GOV-001": "All AI solutions must be registered",
  "AI-GOV-002": "Every solution must be assigned a risk tier",
  "AI-GOV-003": "Solutions must pass quality thresholds",
  "AI-GOV-004": "No toxic or harmful content in outputs",
  "AI-GOV-005": "No PII in AI solution outputs",
  "AI-GOV-006": "All guardrails functional and tested",
  "AI-GOV-007": "No demographic bias in outputs",
  "AI-GOV-008": "All interactions fully traced for audit",
  "AI-GOV-009": "Golden datasets human-reviewed and approved",
  "AI-GOV-010": "System prompts version-controlled and approved",
};

// --- Controls Register ---

export const controls: Control[] = [
  {
    id: "AI-GOV-001",
    name: "Solution Registration",
    description:
      "Every AI solution must be registered with complete metadata, risk tier, and named owner",
    enforcementLayer: "deployment-gate",
    controlType: "preventive",
    risksMitigated: ["AIR-012"],
    regulatoryAlignment: ["CPS 230", "DISR #1"],
    sourceDoc: "07-compliance-as-code",
  },
  {
    id: "AI-GOV-002",
    name: "Risk Tier Assignment",
    description:
      "Every solution must be assigned a risk tier that determines threshold strictness, guardrail scope, and re-evaluation frequency",
    enforcementLayer: "deployment-gate",
    controlType: "preventive",
    risksMitigated: ["AIR-012"],
    regulatoryAlignment: ["CPS 230", "CPS 234", "DISR #2"],
    sourceDoc: "04-solution-lifecycle",
  },
  {
    id: "AI-GOV-003",
    name: "Quality Thresholds",
    description:
      "Solutions must pass evaluation metrics (faithfulness, relevancy, precision, recall, hallucination) at or above their risk tier's thresholds",
    enforcementLayer: "deployment-gate+production",
    controlType: "preventive+detective",
    risksMitigated: ["AIR-001", "AIR-007"],
    regulatoryAlignment: ["CPS 234", "DISR #4"],
    sourceDoc: "08-evaluation-harness",
  },
  {
    id: "AI-GOV-004",
    name: "Content Safety",
    description:
      "Solutions must not produce toxic, harmful, or dangerous content; toxicity score must be within risk-tier threshold",
    enforcementLayer: "deployment-gate+production",
    controlType: "preventive+detective",
    risksMitigated: ["AIR-005"],
    regulatoryAlignment: ["DISR #3", "DISR #4"],
    sourceDoc: "06-guardrails",
  },
  {
    id: "AI-GOV-005",
    name: "PII Protection",
    description:
      "Zero PII in AI solution outputs; Presidio NER detection on every response",
    enforcementLayer: "deployment-gate+production",
    controlType: "preventive+detective",
    risksMitigated: ["AIR-003"],
    regulatoryAlignment: ["CPS 234", "DISR #3"],
    sourceDoc: "06-guardrails",
  },
  {
    id: "AI-GOV-006",
    name: "Guardrail Validation",
    description:
      "All guardrails (scope, injection, content safety) must pass their test suite before deployment",
    enforcementLayer: "deployment-gate",
    controlType: "preventive",
    risksMitigated: ["AIR-004", "AIR-005", "AIR-006"],
    regulatoryAlignment: ["CPS 234", "DISR #4"],
    sourceDoc: "06-guardrails",
  },
  {
    id: "AI-GOV-007",
    name: "Bias & Fairness",
    description:
      "Solutions must not exhibit systematic demographic bias; bias score must be within risk-tier threshold",
    enforcementLayer: "deployment-gate+production",
    controlType: "preventive+detective",
    risksMitigated: ["AIR-002"],
    regulatoryAlignment: ["DISR #4", "CBA AI Policy"],
    sourceDoc: "08-evaluation-harness",
  },
  {
    id: "AI-GOV-008",
    name: "Audit Trail Completeness",
    description:
      "100% of interactions must have complete trace fields (query, retrieval, generation, guardrails, response)",
    enforcementLayer: "deployment-gate+production",
    controlType: "detective",
    risksMitigated: ["AIR-008"],
    regulatoryAlignment: ["CPS 230", "DISR #9"],
    sourceDoc: "10-observability",
  },
  {
    id: "AI-GOV-009",
    name: "Golden Dataset Sign-Off",
    description:
      "Human reviewer must approve the golden dataset with identity and date recorded",
    enforcementLayer: "deployment-gate",
    controlType: "preventive",
    risksMitigated: ["AIR-011"],
    regulatoryAlignment: ["DISR #5", "DISR #10"],
    sourceDoc: "07-compliance-as-code",
  },
  {
    id: "AI-GOV-010",
    name: "Prompt Governance",
    description:
      "System prompts must be version-controlled with linked approval commits; prompt hash change triggers re-evaluation",
    enforcementLayer: "deployment-gate",
    controlType: "preventive",
    risksMitigated: ["AIR-009"],
    regulatoryAlignment: ["CPS 230", "DISR #9"],
    sourceDoc: "07-compliance-as-code",
  },
];

export const runtimeGuardrails: RuntimeGuardrail[] = [
  {
    name: "Scope Adherence",
    controlId: "AI-GOV-006",
    implementation: "Custom classifier — query classification before retrieval",
    latencyMs: 12,
    onFailure: "Block; serve refusal",
  },
  {
    name: "Prompt Injection Detection",
    controlId: "AI-GOV-006",
    implementation: "Pattern matching + classifier — input validation before LLM call",
    latencyMs: 10,
    onFailure: "Block",
  },
  {
    name: "PII Scan",
    controlId: "AI-GOV-005",
    implementation: "Presidio NER (PERSON, EMAIL, PHONE, AU_ABN, AU_TFN, AU_MEDICARE)",
    latencyMs: 15,
    onFailure: "Block; alert immediately",
  },
  {
    name: "Citation Coverage",
    controlId: "AI-GOV-003",
    implementation: "Custom metric — all claims traceable to source documents",
    latencyMs: 8,
    onFailure: "Block if below threshold",
  },
  {
    name: "Faithfulness",
    controlId: "AI-GOV-003",
    implementation: "DeepEval FaithfulnessMetric, judge: gpt-4o-mini",
    latencyMs: 145,
    onFailure: "Regenerate with stricter grounding",
  },
  {
    name: "Bias",
    controlId: "AI-GOV-007",
    implementation: "DeepEval BiasMetric",
    latencyMs: 130,
    onFailure: "Block",
  },
  {
    name: "Toxicity",
    controlId: "AI-GOV-004",
    implementation: "DeepEval ToxicityMetric",
    latencyMs: 125,
    onFailure: "Block; alert immediately",
  },
  {
    name: "Audit Trail",
    controlId: "AI-GOV-008",
    implementation: "Custom logging — structured spans to immutable store",
    latencyMs: 5,
    onFailure: "Serve but flag",
  },
];

export const riskControlMappings: RiskControlMapping[] = [
  { riskId: "AIR-001", risk: "Hallucination", controls: ["AI-GOV-003"], residualRisk: "low" },
  { riskId: "AIR-002", risk: "Bias & Discrimination", controls: ["AI-GOV-007"], residualRisk: "low" },
  { riskId: "AIR-003", risk: "PII Leakage", controls: ["AI-GOV-005"], residualRisk: "very-low" },
  { riskId: "AIR-004", risk: "Prompt Injection", controls: ["AI-GOV-006"], residualRisk: "low" },
  { riskId: "AIR-005", risk: "Toxic Content", controls: ["AI-GOV-004", "AI-GOV-006"], residualRisk: "very-low" },
  { riskId: "AIR-006", risk: "Scope Creep", controls: ["AI-GOV-006"], residualRisk: "very-low" },
  { riskId: "AIR-007", risk: "Model Drift", controls: ["AI-GOV-003"], residualRisk: "low" },
  { riskId: "AIR-008", risk: "Audit Trail Gaps", controls: ["AI-GOV-008"], residualRisk: "very-low" },
  { riskId: "AIR-009", risk: "Uncontrolled Prompt Changes", controls: ["AI-GOV-010"], residualRisk: "low" },
  { riskId: "AIR-010", risk: "Third-Party Model Changes", controls: ["AI-GOV-003"], residualRisk: "medium" },
  { riskId: "AIR-011", risk: "Insufficient Test Coverage", controls: ["AI-GOV-009"], residualRisk: "low" },
  { riskId: "AIR-012", risk: "Unauthorised Deployment", controls: ["AI-GOV-001", "AI-GOV-002"], residualRisk: "very-low" },
];

export const controlThresholds: ControlThreshold[] = [
  { controlId: "AI-GOV-003", metric: "Faithfulness", experimental: null, productionInternal: "\u2265 0.80", productionCustomerFacing: "\u2265 0.90" },
  { controlId: "AI-GOV-003", metric: "Answer Relevancy", experimental: null, productionInternal: "\u2265 0.75", productionCustomerFacing: "\u2265 0.85" },
  { controlId: "AI-GOV-003", metric: "Hallucination", experimental: null, productionInternal: "\u2264 0.15", productionCustomerFacing: "\u2264 0.10" },
  { controlId: "AI-GOV-004", metric: "Toxicity", experimental: null, productionInternal: "\u2264 0.05", productionCustomerFacing: "\u2264 0.02" },
  { controlId: "AI-GOV-005", metric: "PII", experimental: null, productionInternal: "Zero tolerance", productionCustomerFacing: "Zero tolerance" },
  { controlId: "AI-GOV-007", metric: "Bias", experimental: null, productionInternal: "\u2264 0.10", productionCustomerFacing: "\u2264 0.05" },
  { controlId: "AI-GOV-008", metric: "Audit Completeness", experimental: null, productionInternal: "100%", productionCustomerFacing: "100%" },
  { controlId: "AI-GOV-003", metric: "Re-evaluation", experimental: null, productionInternal: "90 days", productionCustomerFacing: "30 days" },
];

export const incidentResponses: IncidentResponse[] = [
  { controlId: "AI-GOV-005", event: "PII detected in output", automatedResponse: "Response blocked, PII redacted", escalation: "Immediate alert to owner + chapter lead" },
  { controlId: "AI-GOV-004", event: "Toxicity detected", automatedResponse: "Response blocked", escalation: "Immediate alert to owner + chapter lead" },
  { controlId: "AI-GOV-007", event: "Bias threshold exceeded", automatedResponse: "Response blocked", escalation: "Alert to owner + chapter lead" },
  { controlId: "AI-GOV-003", event: "Faithfulness below threshold", automatedResponse: "Response regenerated (stricter grounding)", escalation: "Escalated if retry also fails" },
  { controlId: "AI-GOV-006", event: "Scope violation", automatedResponse: "Response blocked, refusal served", escalation: "Escalated if > 5 in 1 hour" },
  { controlId: "AI-GOV-006", event: "Prompt injection detected", automatedResponse: "Response blocked", escalation: "Logged as security event" },
  { controlId: "AI-GOV-008", event: "Audit trail incomplete", automatedResponse: "Response served but flagged", escalation: "Alert to chapter lead" },
  { controlId: "AI-GOV-003", event: "7-day faithfulness declining", automatedResponse: "Dashboard moves to AMBER", escalation: "Alert to squad + chapter lead" },
];

export const regulatoryRequirements: RegulatoryRequirement[] = [
  // CPS 230
  { framework: "APRA CPS 230", requirement: "Identify and assess operational risks", controls: ["AI-GOV-001", "AI-GOV-002"], evidence: "Risk register, risk tier in solution manifest" },
  { framework: "APRA CPS 230", requirement: "Maintain effective controls", controls: ["AI-GOV-003", "AI-GOV-004", "AI-GOV-005", "AI-GOV-006", "AI-GOV-007", "AI-GOV-008", "AI-GOV-009", "AI-GOV-010"], evidence: "Deployment gate reports, production compliance logs" },
  { framework: "APRA CPS 230", requirement: "Monitor and report on operational risk", controls: ["AI-GOV-003", "AI-GOV-007", "AI-GOV-008"], evidence: "Portfolio dashboard, drift alerts, compliance health summary" },
  { framework: "APRA CPS 230", requirement: "Manage third-party risks", controls: ["AI-GOV-003"], evidence: "Re-evaluation reports, vendor tracking in manifest" },
  { framework: "APRA CPS 230", requirement: "Business continuity", controls: ["AI-GOV-004", "AI-GOV-005", "AI-GOV-006"], evidence: "Response blocking/regeneration on failure" },
  // CPS 234
  { framework: "APRA CPS 234", requirement: "Classify information assets", controls: ["AI-GOV-002"], evidence: "Risk tier assignment in solution manifest" },
  { framework: "APRA CPS 234", requirement: "Controls commensurate with risk", controls: ["AI-GOV-002"], evidence: "Per-tier threshold config, gate results" },
  { framework: "APRA CPS 234", requirement: "Detect and respond to security incidents", controls: ["AI-GOV-005", "AI-GOV-006"], evidence: "Compliance event log (security events filter)" },
  { framework: "APRA CPS 234", requirement: "Test control effectiveness", controls: ["AI-GOV-003", "AI-GOV-006"], evidence: "Evaluation scorecards, guardrail test results" },
  // DISR
  { framework: "DISR AI Safety Standard", requirement: "Guardrail 1: Accountability", controls: ["AI-GOV-001"], evidence: "Named owner, risk tier, chapter oversight" },
  { framework: "DISR AI Safety Standard", requirement: "Guardrail 2: Risk management", controls: ["AI-GOV-002", "AI-GOV-007"], evidence: "Risk register, tier framework, bias metrics" },
  { framework: "DISR AI Safety Standard", requirement: "Guardrail 3: Data governance", controls: ["AI-GOV-005"], evidence: "PII detection, scope containment" },
  { framework: "DISR AI Safety Standard", requirement: "Guardrail 4: Testing", controls: ["AI-GOV-003", "AI-GOV-004", "AI-GOV-006"], evidence: "Evaluation harness, guardrail test suites" },
  { framework: "DISR AI Safety Standard", requirement: "Guardrail 5: Human control", controls: ["AI-GOV-002", "AI-GOV-009"], evidence: "Risk tier conversation, golden dataset sign-off" },
  { framework: "DISR AI Safety Standard", requirement: "Guardrail 7: Challenge processes", controls: [], evidence: "Gap — requires organisational process" },
  { framework: "DISR AI Safety Standard", requirement: "Guardrail 9: Record keeping", controls: ["AI-GOV-008", "AI-GOV-010"], evidence: "Audit trail, prompt versioning" },
  { framework: "DISR AI Safety Standard", requirement: "Guardrail 10: Conformity assessments", controls: ["AI-GOV-003"], evidence: "Deployment gate, scheduled re-evaluation" },
];

// --- Governance Documents ---

export const governanceDocuments: GovernanceDocument[] = [
  {
    id: "cba-group-ai-policy",
    title: "CBA Group AI Policy",
    type: "policy",
    owner: "Group Risk",
    status: "active",
    effectiveDate: "2025-07-01",
    nextReviewDate: "2026-07-01",
    description:
      "Enterprise-wide policy governing the development, deployment, and operation of AI systems across CBA. Establishes mandatory requirements for all business units.",
    aiGovControls: [
      "AI-GOV-001",
      "AI-GOV-003",
      "AI-GOV-005",
      "AI-GOV-006",
      "AI-GOV-007",
      "AI-GOV-008",
      "AI-GOV-009",
      "AI-GOV-010",
    ],
  },
  {
    id: "cba-responsible-ai-principles",
    title: "CBA Responsible AI Principles",
    type: "policy",
    owner: "Group AI Ethics Board",
    status: "active",
    effectiveDate: "2025-09-01",
    nextReviewDate: "2026-09-01",
    description:
      "Defines CBA's commitment to fairness, transparency, accountability, privacy, and safety in AI systems. Applies to all AI and ML solutions across the Group.",
    aiGovControls: ["AI-GOV-005", "AI-GOV-007"],
  },
  {
    id: "cba-model-risk-framework",
    title: "CBA Model Risk Management Framework",
    type: "framework",
    owner: "Model Risk",
    status: "active",
    effectiveDate: "2025-01-15",
    nextReviewDate: "2026-01-15",
    description:
      "Framework for identifying, assessing, and mitigating risks arising from the use of models — including AI/ML models — in business decision-making. Covers model lifecycle from development through retirement.",
    aiGovControls: ["AI-GOV-001", "AI-GOV-003", "AI-GOV-007", "AI-GOV-009"],
  },
  {
    id: "cba-data-governance-standard",
    title: "CBA Data Governance Standard",
    type: "standard",
    owner: "Chief Data Office",
    status: "active",
    effectiveDate: "2025-04-01",
    nextReviewDate: "2026-04-01",
    description:
      "Standards for data quality, lineage, classification, retention, and privacy across all data assets. Includes specific provisions for AI training data and evaluation datasets.",
    aiGovControls: ["AI-GOV-005", "AI-GOV-008", "AI-GOV-009"],
  },
  {
    id: "cba-ai-registration-standard",
    title: "CBA AI Solution Registration Standard",
    type: "standard",
    owner: "Risk Management AI",
    status: "active",
    effectiveDate: "2025-11-01",
    nextReviewDate: "2026-11-01",
    description:
      "Mandatory registration requirements for all AI solutions. Defines the solution manifest schema, risk tier classification criteria, and inventory maintenance procedures.",
    aiGovControls: ["AI-GOV-001"],
  },
  {
    id: "cba-ai-testing-framework",
    title: "CBA AI Testing & Evaluation Framework",
    type: "framework",
    owner: "Risk Management AI",
    status: "active",
    effectiveDate: "2025-11-01",
    nextReviewDate: "2026-11-01",
    description:
      "Framework for evaluating AI solution quality, safety, and fairness. Defines golden dataset requirements, evaluation metrics by solution type, and pass/fail thresholds by risk tier.",
    aiGovControls: ["AI-GOV-003", "AI-GOV-006", "AI-GOV-007", "AI-GOV-009"],
  },
  {
    id: "cba-prompt-governance-guideline",
    title: "CBA Prompt Governance Guideline",
    type: "guideline",
    owner: "Risk Management AI",
    status: "draft",
    effectiveDate: "2026-06-01",
    nextReviewDate: "2027-06-01",
    description:
      "Guideline for version control, review, and approval of system prompts in GenAI solutions. Covers prompt change management, regression testing, and audit trail requirements.",
    aiGovControls: ["AI-GOV-010"],
  },
  {
    id: "apra-cps-230",
    title: "APRA CPS 230 — Operational Risk Management",
    type: "standard",
    owner: "APRA",
    status: "active",
    effectiveDate: "2025-07-01",
    nextReviewDate: "2026-07-01",
    description:
      "Prudential standard requiring ADIs to effectively manage operational risks, including those arising from technology, third-party arrangements, and business disruptions.",
    aiGovControls: ["AI-GOV-001", "AI-GOV-003", "AI-GOV-006", "AI-GOV-008"],
  },
  {
    id: "apra-cps-234",
    title: "APRA CPS 234 — Information Security",
    type: "standard",
    owner: "APRA",
    status: "active",
    effectiveDate: "2019-07-01",
    nextReviewDate: "2026-07-01",
    description:
      "Prudential standard requiring ADIs to maintain information security capability commensurate with the size and extent of threats to their information assets, including AI systems.",
    aiGovControls: ["AI-GOV-005", "AI-GOV-006", "AI-GOV-008", "AI-GOV-010"],
  },
  {
    id: "disr-ai-safety-standard",
    title: "Australia's Voluntary AI Safety Standard",
    type: "guideline",
    owner: "DISR",
    status: "active",
    effectiveDate: "2024-09-01",
    nextReviewDate: "2026-09-01",
    description:
      "Ten guardrails for safe and responsible AI published by the Department of Industry, Science and Resources. Covers accountability, risk management, testing, human oversight, and transparency.",
    aiGovControls: [
      "AI-GOV-001",
      "AI-GOV-003",
      "AI-GOV-005",
      "AI-GOV-007",
      "AI-GOV-008",
    ],
  },
];

// --- Governance Document Details ---

export const documentDetails: Record<string, GovernanceDocumentDetail> = {
  "cba-group-ai-policy": {
    ...governanceDocuments[0],
    purpose:
      "Establish mandatory requirements for the safe, ethical, and compliant development, deployment, and operation of AI systems across the Commonwealth Bank Group.",
    scope:
      "All AI and ML systems developed, procured, or operated by any CBA business unit, subsidiary, or third-party vendor acting on CBA's behalf. Applies to both generative AI and traditional machine learning.",
    keyRequirements: [
      "All AI solutions must be registered in the Group AI inventory before deployment",
      "AI solutions must be assigned a risk tier based on impact assessment and undergo governance proportionate to that tier",
      "Automated quality and safety evaluations must be passed before any AI solution enters production",
      "All AI outputs must be monitored for PII leakage, bias, toxicity, and factual accuracy on an ongoing basis",
      "Guardrails must be implemented and tested for every AI solution, covering scope containment, content safety, and input validation",
      "Complete audit trails must be maintained for all AI interactions, enabling reconstruction of any decision",
      "Human-reviewed golden datasets must be used for evaluation, with sign-off recorded and traceable",
      "System prompts must be version-controlled with approval workflows before deployment",
    ],
    controlMappings: [
      { controlId: "AI-GOV-001", requirement: "AI inventory registration", platformEnforcement: "Automated registration check in CI/CD pipeline verifies solution manifest is complete, risk tier assigned, and owner designated" },
      { controlId: "AI-GOV-003", requirement: "Quality threshold compliance", platformEnforcement: "DeepEval evaluation harness runs against golden dataset with risk-tier-specific thresholds; deployment blocked if any metric fails" },
      { controlId: "AI-GOV-005", requirement: "PII protection", platformEnforcement: "Presidio PII detection scans every AI output at deployment (batch test suite) and in production (per-response); zero tolerance policy" },
      { controlId: "AI-GOV-006", requirement: "Guardrail validation", platformEnforcement: "Guardrail test suite validates scope adherence, prompt injection defence, and content safety with 95% minimum pass rate" },
      { controlId: "AI-GOV-007", requirement: "Bias and fairness", platformEnforcement: "DeepEval BiasMetric evaluated at deployment gate and monitored per-response; threshold varies by risk tier" },
      { controlId: "AI-GOV-008", requirement: "Audit trail completeness", platformEnforcement: "Tracing SDK enforces structured logging; audit completeness gate requires 100% of fields present across sampled interactions" },
      { controlId: "AI-GOV-009", requirement: "Golden dataset governance", platformEnforcement: "Sign-off record verified in CI/CD pipeline; requires reviewer identity, date, and approval status before deployment proceeds" },
      { controlId: "AI-GOV-010", requirement: "Prompt version control", platformEnforcement: "Prompt governance check verifies version tracking and approval commit linkage; prompt hash changes trigger automatic re-evaluation" },
    ],
    approvalAuthority: "Group Chief Risk Officer",
    relatedDocuments: ["cba-responsible-ai-principles", "cba-model-risk-framework", "cba-data-governance-standard"],
  },
  "cba-responsible-ai-principles": {
    ...governanceDocuments[1],
    purpose:
      "Articulate CBA's commitment to developing and deploying AI systems that are fair, transparent, accountable, and safe, ensuring trust with customers, regulators, and the community.",
    scope:
      "All AI and ML systems across the CBA Group. Principles apply regardless of whether systems are developed internally, procured from vendors, or operated by third parties.",
    keyRequirements: [
      "AI systems must not produce systematically biased outputs across demographic groups including age, gender, ethnicity, or location",
      "Fairness definitions must be documented for each AI solution, appropriate to its use case and impact",
      "AI outputs must not contain or expose personal information beyond what is explicitly required for the solution's function",
      "Privacy-by-design principles must be embedded in AI solution architecture from inception",
      "Regular bias audits must be conducted on production AI systems, with results reported to the AI Ethics Board",
      "Mechanisms must exist for affected individuals to seek review of AI-assisted decisions",
    ],
    controlMappings: [
      { controlId: "AI-GOV-005", requirement: "Privacy and PII protection", platformEnforcement: "Presidio entity detection (PERSON, EMAIL, PHONE, AU_ABN, AU_TFN, AU_MEDICARE) on every response; zero-tolerance blocking" },
      { controlId: "AI-GOV-007", requirement: "Fairness and non-discrimination", platformEnforcement: "DeepEval BiasMetric runs at deployment and per-response; bias score thresholds enforced by risk tier (0.10 internal, 0.05 customer-facing)" },
    ],
    approvalAuthority: "Group AI Ethics Board",
    relatedDocuments: ["cba-group-ai-policy", "cba-data-governance-standard"],
  },
  "cba-model-risk-framework": {
    ...governanceDocuments[2],
    purpose:
      "Provide a structured approach to identifying, assessing, and mitigating risks arising from the use of models — including AI and ML models — in business decision-making across CBA.",
    scope:
      "All models used for decision-making, risk measurement, financial reporting, or customer-facing interactions. Includes traditional statistical models, machine learning models, and generative AI systems.",
    keyRequirements: [
      "All models must be registered in the Group model inventory with complete metadata including purpose, owner, and risk classification",
      "Models must undergo independent validation before production deployment, with validation scope proportionate to model risk tier",
      "Model performance must be evaluated against documented quality thresholds using representative test data",
      "Models must be re-validated on a regular schedule and when material changes occur (data drift, model updates, scope changes)",
      "Golden datasets used for validation must be reviewed and approved by qualified personnel independent of the development team",
      "Bias and fairness assessments are mandatory for models that impact customers or make decisions about individuals",
    ],
    controlMappings: [
      { controlId: "AI-GOV-001", requirement: "Model inventory registration", platformEnforcement: "Solution manifest schema enforces registration with metadata completeness check; deployment blocked without valid registration" },
      { controlId: "AI-GOV-003", requirement: "Pre-deployment validation", platformEnforcement: "Evaluation harness runs full metric suite against golden dataset; thresholds configured per risk tier in YAML" },
      { controlId: "AI-GOV-007", requirement: "Bias and fairness assessment", platformEnforcement: "BiasMetric included in evaluation suite; demographic parity and equalised odds tracked for ML models" },
      { controlId: "AI-GOV-009", requirement: "Independent test data review", platformEnforcement: "Golden dataset sign-off gate requires documented reviewer, review date, and explicit approval before deployment" },
    ],
    approvalAuthority: "Head of Model Risk",
    relatedDocuments: ["cba-group-ai-policy", "cba-ai-testing-framework"],
  },
  "cba-data-governance-standard": {
    ...governanceDocuments[3],
    purpose:
      "Establish standards for data quality, lineage, classification, retention, and privacy across all CBA data assets, with specific provisions for data used in AI and ML systems.",
    scope:
      "All data assets across CBA, with enhanced requirements for data used in AI training, evaluation, and production inference. Covers both structured and unstructured data.",
    keyRequirements: [
      "Data used in AI systems must be classified according to CBA's data classification scheme and handled according to its sensitivity level",
      "AI solution outputs must not contain personal information unless explicitly required and authorised for the solution's purpose",
      "Evaluation datasets must use synthetic or appropriately anonymised data — real customer data must not be used in golden datasets",
      "Complete audit trails must be maintained for data access, transformation, and usage in AI systems",
      "Data retention periods must be defined and enforced for all AI-related data assets including training data, evaluation results, and interaction logs",
      "Data lineage must be documented for AI training data, enabling traceability from source to model",
    ],
    controlMappings: [
      { controlId: "AI-GOV-005", requirement: "PII protection in outputs", platformEnforcement: "Presidio scans every AI response for PII entities; detected PII triggers response blocking and alert to solution owner" },
      { controlId: "AI-GOV-008", requirement: "Audit trail for data access", platformEnforcement: "Tracing SDK logs all data retrieval and transformation steps; 100% completeness enforced at deployment gate" },
      { controlId: "AI-GOV-009", requirement: "Synthetic data in evaluation", platformEnforcement: "Golden dataset sign-off process includes confirmation that test data is synthetic; chapter reviews during intake" },
    ],
    approvalAuthority: "Chief Data Officer",
    relatedDocuments: ["cba-group-ai-policy", "cba-responsible-ai-principles", "apra-cps-234"],
  },
  "cba-ai-registration-standard": {
    ...governanceDocuments[4],
    purpose:
      "Define the mandatory registration requirements for all AI solutions, ensuring every AI system in CBA is inventoried, classified, and assigned appropriate governance.",
    scope:
      "All AI and ML solutions deployed or in development across CBA, regardless of framework, hosting environment, or development team.",
    keyRequirements: [
      "Every AI solution must have a solution.yaml manifest file containing name, description, version, owner, contact, and endpoint details",
      "Solutions must be assigned a risk tier (experimental, production_internal, production_customer_facing) by the chapter during intake",
      "Risk tier determines which guardrails are mandatory, what evaluation thresholds apply, and how frequently production monitoring runs",
      "Solution registration must be completed before any evaluation, testing, or deployment activities begin",
      "Changes to solution scope, ownership, or risk tier must be reflected in the manifest and trigger re-assessment",
    ],
    controlMappings: [
      { controlId: "AI-GOV-001", requirement: "Solution registration and inventory", platformEnforcement: "CI/CD pipeline verifies manifest completeness: model registry entry, metadata, risk tier assignment, and owner — deployment blocked on any gap" },
    ],
    approvalAuthority: "Head of Risk Management AI",
    relatedDocuments: ["cba-group-ai-policy", "cba-model-risk-framework"],
  },
  "cba-ai-testing-framework": {
    ...governanceDocuments[5],
    purpose:
      "Define how AI solutions are evaluated for quality, safety, and fairness before deployment and throughout their production lifecycle.",
    scope:
      "All AI and ML solutions subject to the CBA Group AI Policy. Covers pre-deployment evaluation, production monitoring, and scheduled re-evaluation.",
    keyRequirements: [
      "Every AI solution must have a golden dataset covering expected scenarios, edge cases, and adversarial inputs, reviewed for coverage by the chapter",
      "Evaluation metrics must be appropriate to the solution type: faithfulness for Q&A, accuracy and calibration for classification, completeness for validation",
      "Pass/fail thresholds must be configured by risk tier — customer-facing solutions face the strictest thresholds",
      "All guardrails must be tested with dedicated test suites covering scope adherence, prompt injection, content safety, and PII detection",
      "Bias and toxicity evaluations are mandatory for all solutions above experimental tier",
      "Solutions must be re-evaluated every 90 days (internal) or 30 days (customer-facing), and immediately after model or prompt changes",
    ],
    controlMappings: [
      { controlId: "AI-GOV-003", requirement: "Quality threshold compliance", platformEnforcement: "DeepEval harness runs full metric suite in CI/CD pipeline; results compared against risk-tier YAML thresholds" },
      { controlId: "AI-GOV-006", requirement: "Guardrail functional testing", platformEnforcement: "Guardrail test suite runs scope, injection, and content safety tests with 95% minimum pass rate gate" },
      { controlId: "AI-GOV-007", requirement: "Bias and toxicity evaluation", platformEnforcement: "BiasMetric and ToxicityMetric included in evaluation suite; separate thresholds per risk tier" },
      { controlId: "AI-GOV-009", requirement: "Golden dataset governance", platformEnforcement: "Sign-off record with reviewer identity and date required; coverage analysis included in evidence package" },
    ],
    approvalAuthority: "Head of Risk Management AI",
    relatedDocuments: ["cba-group-ai-policy", "cba-model-risk-framework", "cba-ai-registration-standard"],
  },
  "cba-prompt-governance-guideline": {
    ...governanceDocuments[6],
    purpose:
      "Provide guidance on the version control, review, and approval of system prompts in generative AI solutions, ensuring prompt changes are governed with the same rigour as code changes.",
    scope:
      "All generative AI solutions that use system prompts, including RAG pipelines, agentic workflows, and conversational AI. Does not apply to traditional ML models.",
    keyRequirements: [
      "System prompts must be stored in version control with a clear change history",
      "Prompt changes must be reviewed and approved before deployment, with the approval commit linked in the solution manifest",
      "Any prompt modification must trigger automatic re-evaluation against the solution's golden dataset to detect regressions",
      "Prompt versions must be tracked in the evidence package, with the current active prompt and full change log available for audit",
      "Emergency prompt changes must follow the same approval workflow but may use an expedited review process",
    ],
    controlMappings: [
      { controlId: "AI-GOV-010", requirement: "Prompt version control and approval", platformEnforcement: "CI/CD gate verifies prompt directory has version tags and approval commits; prompt hash changes trigger automatic re-evaluation" },
    ],
    approvalAuthority: "Head of Risk Management AI",
    relatedDocuments: ["cba-group-ai-policy", "cba-ai-testing-framework"],
  },
  "apra-cps-230": {
    ...governanceDocuments[7],
    purpose:
      "Strengthen the management of operational risks by authorised deposit-taking institutions (ADIs), including risks from technology, third-party service providers, and business disruptions.",
    scope:
      "All APRA-regulated ADIs, including CBA. Applies to operational risk management frameworks, including risks introduced by AI and ML systems used in banking operations.",
    keyRequirements: [
      "ADIs must identify, assess, manage, and monitor operational risks, including those arising from the use of AI and technology",
      "Effective controls must be maintained that are proportionate to the operational risk profile, with regular testing of control effectiveness",
      "Material operational risks must be reported to the Board and APRA, including incidents involving AI system failures",
      "Third-party arrangements (including AI/LLM vendor dependencies) must be managed with appropriate due diligence and ongoing monitoring",
      "Business continuity arrangements must account for AI system failures, including graceful degradation and fallback procedures",
      "ADIs must maintain an operational risk profile that is regularly updated to reflect changes in the operating environment",
    ],
    controlMappings: [
      { controlId: "AI-GOV-001", requirement: "Operational risk identification", platformEnforcement: "Solution registry provides a complete inventory of AI operational risks; risk tier assignment classifies each solution's risk profile" },
      { controlId: "AI-GOV-003", requirement: "Effective controls proportionate to risk", platformEnforcement: "Evaluation thresholds scale by risk tier — higher-risk solutions face stricter quality gates, ensuring controls match risk" },
      { controlId: "AI-GOV-006", requirement: "Control testing and effectiveness", platformEnforcement: "Guardrail test suites verify control effectiveness at deployment; scheduled re-evaluation tests controls on an ongoing basis" },
      { controlId: "AI-GOV-008", requirement: "Operational risk monitoring and reporting", platformEnforcement: "Compliance event logs capture all control outcomes; portfolio dashboard provides continuous operational risk visibility" },
    ],
    approvalAuthority: "APRA (Australian Prudential Regulation Authority)",
    relatedDocuments: ["apra-cps-234", "cba-group-ai-policy", "cba-model-risk-framework"],
  },
  "apra-cps-234": {
    ...governanceDocuments[8],
    purpose:
      "Ensure ADIs maintain information security capability commensurate with the size and extent of threats to their information assets, including threats introduced by AI systems.",
    scope:
      "All APRA-regulated ADIs. Covers information security governance, controls, incident management, and testing obligations relevant to AI system security.",
    keyRequirements: [
      "Information assets (including AI systems and their data) must be classified and managed according to their sensitivity and criticality",
      "Security controls must be implemented commensurate with the threats to information assets, including AI-specific threats like prompt injection",
      "Information security incidents (including AI security failures) must be detected, reported, and escalated in a timely manner",
      "APRA must be notified of material information security incidents, including significant AI system compromises",
      "Control effectiveness must be tested regularly through systematic testing programs",
      "Third-party and vendor risks to information security must be actively managed",
    ],
    controlMappings: [
      { controlId: "AI-GOV-005", requirement: "Information asset protection", platformEnforcement: "PII detection prevents AI systems from exposing sensitive information; zero-tolerance policy with per-response scanning" },
      { controlId: "AI-GOV-006", requirement: "Security controls for AI threats", platformEnforcement: "Prompt injection detection, scope containment, and content safety guardrails defend against AI-specific security threats" },
      { controlId: "AI-GOV-008", requirement: "Incident detection and audit trail", platformEnforcement: "Complete interaction tracing enables incident reconstruction; compliance event logs capture all security-relevant events" },
      { controlId: "AI-GOV-010", requirement: "Change management for AI systems", platformEnforcement: "Prompt version control ensures changes to AI behaviour are tracked, approved, and auditable — preventing unauthorised modifications" },
    ],
    approvalAuthority: "APRA (Australian Prudential Regulation Authority)",
    relatedDocuments: ["apra-cps-230", "cba-group-ai-policy", "cba-data-governance-standard"],
  },
  "disr-ai-safety-standard": {
    ...governanceDocuments[9],
    purpose:
      "Provide ten voluntary guardrails for the safe and responsible design, development, deployment, and use of AI systems in Australia, reflecting community expectations and international best practice.",
    scope:
      "All organisations developing or deploying AI systems in Australia. Voluntary but represents the Australian Government's expectations and is likely to inform future mandatory regulation.",
    keyRequirements: [
      "Organisations must establish, implement, and publish accountability processes for AI systems, including clear ownership and escalation paths",
      "A risk management process must be established, with risks identified, assessed, and managed proportionate to the AI system's potential impact",
      "AI systems must be tested to ensure they work as intended, with testing covering functionality, safety, fairness, and edge cases",
      "AI systems must be protected, with data governance measures ensuring data quality, privacy, and security",
      "Human control or intervention mechanisms must be available, ensuring humans can override or shut down AI systems when necessary",
      "Records must be kept and maintained to support accountability, audit, and regulatory compliance",
    ],
    controlMappings: [
      { controlId: "AI-GOV-001", requirement: "Accountability and ownership (Guardrail 1)", platformEnforcement: "Solution manifest requires named owner and contact; solution registry provides portfolio-wide accountability visibility" },
      { controlId: "AI-GOV-003", requirement: "Testing AI systems (Guardrail 4)", platformEnforcement: "Evaluation harness provides automated, repeatable testing against golden datasets with documented pass/fail criteria" },
      { controlId: "AI-GOV-005", requirement: "Data governance and protection (Guardrail 3)", platformEnforcement: "PII detection enforces data protection at the output layer; synthetic data requirements protect privacy in testing" },
      { controlId: "AI-GOV-007", requirement: "Risk management and fairness (Guardrail 2)", platformEnforcement: "Bias and toxicity metrics quantify fairness risk; risk tier framework ensures governance proportionate to impact" },
      { controlId: "AI-GOV-008", requirement: "Record keeping (Guardrail 9)", platformEnforcement: "Complete audit trails maintained automatically; evidence export generates structured compliance packages on demand" },
    ],
    approvalAuthority: "Department of Industry, Science and Resources (DISR)",
    relatedDocuments: ["cba-group-ai-policy", "cba-responsible-ai-principles", "apra-cps-230"],
  },
};
