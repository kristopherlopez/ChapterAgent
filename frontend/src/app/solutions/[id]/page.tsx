import { notFound } from "next/navigation";
import Header from "@/components/layout/Header";
import GuardrailResults from "@/components/detail/GuardrailResults";
import EvaluationScores from "@/components/detail/EvaluationScores";
import ComplianceGateComponent from "@/components/detail/ComplianceGate";
import TraceView from "@/components/detail/TraceView";
import ExportButton from "@/components/evidence/ExportButton";
import TryAgentButton from "@/components/detail/TryAgentButton";
import TryScorerButton from "@/components/detail/TryScorerButton";
import ViewDatasetButton from "@/components/detail/ViewDatasetButton";
import RunEvaluation from "@/components/detail/RunEvaluation";
import HealthBadge from "@/components/dashboard/HealthBadge";
import { solutionDetails, solutionTraces } from "@/lib/data";
import { fetchSolutionDetail } from "@/lib/api";
import type { GuardrailResult, EvaluationScore } from "@/lib/types";

const PLANNED_GUARDRAILS: GuardrailResult[] = [
  { name: "Prompt Injection", result: "warn", detail: "Not yet evaluated" },
  { name: "Scope Containment", result: "warn", detail: "Not yet evaluated" },
  { name: "PII Detection", result: "warn", detail: "Not yet evaluated" },
  { name: "Faithfulness Check", result: "warn", detail: "Not yet evaluated" },
  { name: "Bias Scan", result: "warn", detail: "Not yet evaluated" },
  { name: "Toxicity Scan", result: "warn", detail: "Not yet evaluated" },
  { name: "Citation Coverage", result: "warn", detail: "Not yet evaluated" },
  { name: "Temporal Accuracy", result: "warn", detail: "Not yet evaluated" },
];

const PLANNED_METRICS: EvaluationScore[] = [
  { metric: "Faithfulness", score: 0, threshold: 0.90, status: "warn" },
  { metric: "Answer Relevancy", score: 0, threshold: 0.85, status: "warn" },
  { metric: "Context Precision", score: 0, threshold: 0.80, status: "warn" },
  { metric: "Context Recall", score: 0, threshold: 0.75, status: "warn" },
  { metric: "Hallucination", score: 0, threshold: 0.10, status: "warn" },
  { metric: "Citation Coverage", score: 0, threshold: 0.95, status: "warn" },
  { metric: "Boundary Adherence", score: 0, threshold: 0.95, status: "warn" },
  { metric: "Temporal Accuracy", score: 0, threshold: 0.90, status: "warn" },
  { metric: "Bias", score: 0, threshold: 0.05, status: "warn" },
  { metric: "Toxicity", score: 0, threshold: 0.05, status: "warn" },
];

export default async function SolutionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Try backend first for real data, fall back to hardcoded
  let solution;
  try {
    solution = await fetchSolutionDetail(id);
  } catch {
    solution = solutionDetails[id];
  }

  const trace = solutionTraces[id];

  if (!solution) {
    notFound();
  }

  const hasGuardrails = solution.guardrails && solution.guardrails.length > 0;
  const hasEvaluation = solution.evaluation && solution.evaluation.length > 0;

  return (
    <div>
      <Header
        title={solution.name}
        subtitle={solution.description}
      />
      <div className="px-8 py-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <HealthBadge status={solution.health} />
            <span className="text-sm text-zinc-500">
              Risk Tier: <span className="font-medium text-zinc-700">{solution.riskTier}</span>
            </span>
            {solution.lastRun && (
              <span className="text-sm text-zinc-500">
                Last Run: <span className="font-medium text-zinc-700">{solution.lastRun}</span>
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            {solution.category === "ml" ? (
              <>
                <TryScorerButton solutionId={solution.id} />
                <ViewDatasetButton solutionId={solution.id} />
              </>
            ) : (
              <TryAgentButton solutionId={solution.id} />
            )}
            <RunEvaluation solutionId={solution.id} />
            <ExportButton solutionId={solution.id} />
          </div>
        </div>

        {hasGuardrails ? (
          <GuardrailResults guardrails={solution.guardrails} />
        ) : (
          <GuardrailResults guardrails={PLANNED_GUARDRAILS} />
        )}

        {hasEvaluation ? (
          <EvaluationScores scores={solution.evaluation} />
        ) : (
          <EvaluationScores scores={PLANNED_METRICS} />
        )}

        <ComplianceGateComponent gate={solution.complianceGate} />
        {trace && <TraceView steps={trace} />}
      </div>
    </div>
  );
}
