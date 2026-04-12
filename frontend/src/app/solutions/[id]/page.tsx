import { notFound } from "next/navigation";
import Header from "@/components/layout/Header";
import GuardrailResults from "@/components/detail/GuardrailResults";
import EvaluationScores from "@/components/detail/EvaluationScores";
import ComplianceGateComponent from "@/components/detail/ComplianceGate";
import TraceView from "@/components/detail/TraceView";
import ExportButton from "@/components/evidence/ExportButton";
import TryAgentButton from "@/components/detail/TryAgentButton";
import TryScorerButton from "@/components/detail/TryScorerButton";
import HealthBadge from "@/components/dashboard/HealthBadge";
import { solutionDetails, solutionTraces } from "@/lib/data";

export default async function SolutionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const solution = solutionDetails[id];
  const trace = solutionTraces[id];

  if (!solution) {
    notFound();
  }

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
            <span className="text-sm text-zinc-500">
              Last Run: <span className="font-medium text-zinc-700">{solution.lastRun}</span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            {solution.category === "ml" ? (
              <TryScorerButton solutionId={solution.id} />
            ) : (
              <TryAgentButton solutionId={solution.id} />
            )}
            <ExportButton solutionId={solution.id} />
          </div>
        </div>

        <GuardrailResults guardrails={solution.guardrails} />
        <EvaluationScores scores={solution.evaluation} />
        <ComplianceGateComponent gate={solution.complianceGate} />
        {trace && <TraceView steps={trace} />}
      </div>
    </div>
  );
}
