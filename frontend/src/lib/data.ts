import type {
  SolutionSummary,
  SolutionDetail,
  FrameworkScore,
  TraceStep,
} from "./types";

// --- Hardcoded fallback data (matches results/ JSON files) ---

export const solutions: SolutionSummary[] = [
  {
    id: "rag-policy-qa",
    name: "CBA Annual Report Q&A",
    description:
      "Answers questions about CBA's 2024 Annual Report with source citations",
    riskTier: "Customer-Facing",
    guardrailsSummary: "8/8 PASS",
    evalScore: 0.91,
    gateResult: "pass",
    health: "pass",
    lastRun: "2026-04-10 14:32 AEST",
  },
  {
    id: "agentic-model-validation",
    name: "Model Validation Agent",
    description:
      "LLM agent that reads model documentation, runs validation checks, and drafts findings",
    riskTier: "High",
    guardrailsSummary: "4/4 PASS",
    evalScore: 0.88,
    gateResult: "pass",
    health: "pass",
    lastRun: "2026-04-10 14:35 AEST",
  },
  {
    id: "multi-platform-agent",
    name: "Multi-Platform Agent",
    description:
      "Same agent implemented across 3 frameworks for comparative evaluation",
    riskTier: "Medium",
    guardrailsSummary: "5/6 FAIL",
    evalScore: 0.72,
    gateResult: "fail",
    health: "fail",
    lastRun: "2026-04-10 14:38 AEST",
  },
];

export const solutionDetails: Record<string, SolutionDetail> = {
  "rag-policy-qa": {
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
  "rag-policy-qa": [
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
};
