export type HealthStatus = "pass" | "warn" | "fail" | "pending";

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

// --- Component Catalog ---

export type ComponentType =
  | "guardrail"
  | "evaluation"
  | "compliance"
  | "observability"
  | "tooling";
export type ComponentStatus = "active" | "beta";

export interface ComponentInterface {
  squadProvides: string;
  componentReturns: string;
}

export interface CatalogComponent {
  id: string;
  name: string;
  type: ComponentType;
  description: string;
  interface: ComponentInterface;
  adoption: string[];
  status: ComponentStatus;
}

// --- Golden Dataset Generator ---

export type QueryType =
  | "direct_factual"
  | "comparative"
  | "temporal"
  | "aggregation"
  | "causal"
  | "boundary"
  | "multi_hop"
  | "out_of_scope"
  | "ambiguous"
  | "adversarial";

export interface GeneratedTestCase {
  caseId: string;
  queryType: string;
  question: string;
  expectedAnswer: string;
  expectedBehaviour: string;
  expectedGrounding: string;
  expectedCitations: { document: string; page: number; section: string }[];
  scopeLevel: number;
  keyMetrics: string[];
}

export interface GenerationResult {
  solutionId: string;
  generatedAt: string;
  testCases: GeneratedTestCase[];
}

// --- Golden Dataset Validation ---

export type ReviewStatus = "pending" | "approved" | "rejected" | "edited";

export interface ValidationTestCase extends GeneratedTestCase {
  reviewStatus: ReviewStatus;
  reviewedBy: string | null;
  reviewedAt: string | null;
  reviewNotes: string | null;
}

export interface ValidationDataset {
  solutionId: string;
  solutionName: string;
  version: string;
  totalCases: number;
  reviewed: number;
  approved: number;
  rejected: number;
  pending: number;
  signedOff: boolean;
  signedOffBy: string | null;
  signedOffAt: string | null;
  testCases: ValidationTestCase[];
}

export interface DocumentSection {
  title: string;
  content?: string;
  bullets?: string[];
  table?: { headers: string[]; rows: string[][] };
  subsections?: { title: string; content: string }[];
}

export interface GovernanceDocumentDetail extends GovernanceDocument {
  purpose: string;
  scope: string;
  keyRequirements: string[];
  sections?: DocumentSection[];
  controlMappings: ControlMapping[];
  approvalAuthority: string;
  relatedDocuments: string[];
}
