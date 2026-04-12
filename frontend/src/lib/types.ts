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

export type SolutionCategory = "ai" | "ml";

export interface HealthSnapshot {
  date: string;
  status: HealthStatus;
}

export interface SolutionSummary {
  id: string;
  name: string;
  description: string;
  category: SolutionCategory;
  owner: string;
  riskTier: string;
  guardrailsSummary: string;
  evalScore: number;
  gateResult: HealthStatus;
  health: HealthStatus;
  lastRun: string;
  lastTested: string;
  healthHistory: HealthSnapshot[];
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

export type DocumentType = "policy" | "standard" | "framework" | "guideline";
export type DocumentStatus = "active" | "draft" | "under-review";

export interface GovernanceDocument {
  id: string;
  title: string;
  type: DocumentType;
  owner: string;
  status: DocumentStatus;
  effectiveDate: string;
  nextReviewDate: string;
  description: string;
  aiGovControls: string[];
}

export interface ControlMapping {
  controlId: string;
  requirement: string;
  platformEnforcement: string;
}

// --- Controls Register ---

export type ControlType = "preventive" | "detective" | "preventive+detective";
export type EnforcementLayer =
  | "deployment-gate"
  | "production"
  | "deployment-gate+production";
export type ResidualRisk = "very-low" | "low" | "medium";

export interface Control {
  id: string;
  name: string;
  description: string;
  enforcementLayer: EnforcementLayer;
  controlType: ControlType;
  risksMitigated: string[];
  regulatoryAlignment: string[];
  sourceDoc: string;
}

export interface RuntimeGuardrail {
  name: string;
  controlId: string;
  implementation: string;
  latencyMs: number;
  onFailure: string;
}

export interface RiskControlMapping {
  riskId: string;
  risk: string;
  controls: string[];
  residualRisk: ResidualRisk;
}

export interface ControlThreshold {
  controlId: string;
  metric: string;
  experimental: string | null;
  productionInternal: string;
  productionCustomerFacing: string;
}

export interface IncidentResponse {
  controlId: string;
  event: string;
  automatedResponse: string;
  escalation: string;
}

export interface RegulatoryRequirement {
  framework: string;
  requirement: string;
  controls: string[];
  evidence: string;
}

export interface GovernanceDocumentDetail extends GovernanceDocument {
  purpose: string;
  scope: string;
  keyRequirements: string[];
  controlMappings: ControlMapping[];
  approvalAuthority: string;
  relatedDocuments: string[];
}
