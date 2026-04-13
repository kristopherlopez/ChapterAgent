import { EvaluationScore } from "@/lib/types";
import HealthBadge from "@/components/dashboard/HealthBadge";

export default function EvaluationScores({ scores }: { scores: EvaluationScore[] }) {
  return (
    <div className="bg-white border border-zinc-200 rounded-lg">
      <div className="px-6 py-4 border-b border-zinc-100">
        <h3 className="text-sm font-semibold text-zinc-900">Evaluation Scores</h3>
      </div>
      <div className="divide-y divide-zinc-100">
        {scores.map((s) => (
          <div key={s.metric} className="grid grid-cols-[1fr_80px_80px_80px] items-center gap-4 px-6 py-3">
            <p className="text-sm text-zinc-700">{s.metric}</p>
            <p className="text-sm font-mono text-zinc-900">
              {s.score === 0 && s.status === "warn" ? "—" : s.score.toFixed(2)}
            </p>
            <p className="text-xs text-zinc-400">min {s.threshold.toFixed(2)}</p>
            <HealthBadge status={s.status} />
          </div>
        ))}
      </div>
    </div>
  );
}
