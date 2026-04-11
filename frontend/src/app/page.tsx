import Header from "@/components/layout/Header";
import ComplianceSummary from "@/components/dashboard/ComplianceSummary";
import SolutionRow from "@/components/dashboard/SolutionRow";
import ExportButton from "@/components/evidence/ExportButton";
import { solutions } from "@/lib/data";

export default function DashboardPage() {
  return (
    <div>
      <Header
        title="Compliance Health"
        subtitle="Portfolio overview — all registered AI solutions"
      />
      <ComplianceSummary />
      <div className="px-8 pb-6">
        <div className="bg-white border border-zinc-200 rounded-lg">
          <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-100">
            <div className="grid grid-cols-[1fr_120px_100px_80px_80px_32px] items-center gap-4 w-full">
              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Solution</p>
              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Guardrails</p>
              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Eval Score</p>
              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Gate</p>
              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Health</p>
              <div />
            </div>
          </div>
          {solutions.map((solution) => (
            <SolutionRow key={solution.id} solution={solution} />
          ))}
        </div>
        <div className="flex items-center justify-between mt-6">
          <p className="text-xs text-zinc-400">
            Last compliance run: 2026-04-10 14:32 AEST
          </p>
          <ExportButton />
        </div>
      </div>
    </div>
  );
}
