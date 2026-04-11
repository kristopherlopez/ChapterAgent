import Link from "next/link";
import { SolutionSummary } from "@/lib/types";
import HealthBadge from "./HealthBadge";
import { ChevronRight } from "lucide-react";

export default function SolutionRow({ solution }: { solution: SolutionSummary }) {
  return (
    <Link
      href={`/solutions/${solution.id}`}
      className="grid grid-cols-[1fr_120px_100px_80px_80px_32px] items-center gap-4 px-6 py-4 hover:bg-zinc-50 transition-colors border-b border-zinc-100 last:border-b-0"
    >
      <div>
        <p className="text-sm font-medium text-zinc-900">{solution.name}</p>
        <p className="text-xs text-zinc-500 mt-0.5">{solution.description}</p>
      </div>
      <div className="text-sm text-zinc-600">{solution.guardrailsSummary}</div>
      <div className="text-sm font-mono text-zinc-700">
        {solution.evalScore.toFixed(2)}
      </div>
      <HealthBadge status={solution.gateResult} />
      <HealthBadge status={solution.health} />
      <ChevronRight className="w-4 h-4 text-zinc-400" />
    </Link>
  );
}
