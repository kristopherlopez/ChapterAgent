export type HealthStatus = "pass" | "warn" | "fail";

export interface GuardrailResult {
  name: string;
  result: HealthStatus;
  detail: string;
}

export interface EvaluationScore {
  metric: string;
  score: number;
  threshold: number;
  status: HealthStatus;
}

export interface ComplianceGate {
  gate: string;
  result: HealthStatus;
  reason: string;
  timestamp: string;
}

export interface TraceStep {
  step: number;
  label: string;
  durationMs: number;
  detail?: string;
}

export interface SolutionSummary {
  id: string;
  name: string;
  description: string;
  riskTier: string;
  guardrailsSummary: string;
  evalScore: number;
  gateResult: HealthStatus;
  health: HealthStatus;
  lastRun: string;
}

export interface SolutionDetail extends SolutionSummary {
  guardrails: GuardrailResult[];
  evaluation: EvaluationScore[];
  complianceGate: ComplianceGate;
}

export interface FrameworkScore {
  framework: string;
  evalScore: number;
  guardrailsPass: string;
  latencyAvgMs: number;
  tokenUsageAvg: number;
  costPerRun: number;
  gateResult: HealthStatus;
}
