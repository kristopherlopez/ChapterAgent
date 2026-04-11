import Header from "@/components/layout/Header";
import HealthBadge from "@/components/dashboard/HealthBadge";
import { frameworkScores } from "@/lib/data";

export default function ScorecardPage() {
  const best = frameworkScores.reduce((a, b) =>
    a.evalScore > b.evalScore ? a : b
  );

  return (
    <div>
      <Header
        title="Framework Scorecard"
        subtitle="Multi-Platform Agent — same task, three frameworks, same governance pipeline"
      />
      <div className="px-8 py-6 space-y-6">
        <div className="bg-white border border-zinc-200 rounded-lg">
          <div className="grid grid-cols-[1fr_80px_100px_100px_100px_100px_80px] items-center gap-4 px-6 py-4 border-b border-zinc-100">
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Framework</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Eval</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Guardrails</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Latency</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Tokens</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Cost/Run</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Gate</p>
          </div>
          {frameworkScores.map((fw) => (
            <div
              key={fw.framework}
              className="grid grid-cols-[1fr_80px_100px_100px_100px_100px_80px] items-center gap-4 px-6 py-4 border-b border-zinc-100 last:border-b-0"
            >
              <p className="text-sm font-medium text-zinc-900">{fw.framework}</p>
              <p className="text-sm font-mono text-zinc-700">{fw.evalScore.toFixed(2)}</p>
              <p className="text-sm text-zinc-600">{fw.guardrailsPass}</p>
              <p className="text-sm font-mono text-zinc-600">{fw.latencyAvgMs}ms</p>
              <p className="text-sm font-mono text-zinc-600">{fw.tokenUsageAvg.toLocaleString()}</p>
              <p className="text-sm font-mono text-zinc-600">${fw.costPerRun.toFixed(3)}</p>
              <HealthBadge status={fw.gateResult} />
            </div>
          ))}
        </div>

        <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-2">Recommendation</h3>
          <p className="text-sm text-zinc-600">
            <span className="font-medium text-zinc-900">{best.framework}</span> scores
            highest across eval ({best.evalScore.toFixed(2)}), latency ({best.latencyAvgMs}ms avg),
            and cost (${best.costPerRun.toFixed(3)}/run).
            {frameworkScores.some((fw) => fw.gateResult === "fail") && (
              <span>
                {" "}
                {frameworkScores
                  .filter((fw) => fw.gateResult === "fail")
                  .map((fw) => fw.framework)
                  .join(", ")}{" "}
                blocked at the compliance gate — requires config update before deployment.
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
