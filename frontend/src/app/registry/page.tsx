import Link from "next/link";
import Header from "@/components/layout/Header";
import Sparkline from "@/components/dashboard/Sparkline";
import { solutions } from "@/lib/data";
import { Clock, AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

const STALE_THRESHOLD_DAYS = 7;

function getDaysAgo(dateStr: string): number {
  const tested = new Date(dateStr.replace(" AEST", ""));
  const now = new Date("2026-04-12T12:00:00");
  return Math.floor((now.getTime() - tested.getTime()) / (1000 * 60 * 60 * 24));
}

function formatLastTested(dateStr: string): string {
  const days = getDaysAgo(dateStr);
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  return `${days}d ago`;
}

export default function RegistryPage() {
  return (
    <div>
      <Header
        title="Solution Registry"
        subtitle="All registered solutions discovered from solution.yaml manifests"
      />
      <div className="px-8 py-6 space-y-6">
        <div className="bg-white border border-zinc-200 rounded-lg">
          <div className="grid grid-cols-[1fr_80px_110px_140px_100px_40px_130px_100px] items-center gap-4 px-6 py-4 border-b border-zinc-100">
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Solution</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Category</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Risk Tier</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Owner</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Guardrails</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Gate</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Health</p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Last Tested</p>
          </div>
          {solutions.map((solution) => {
            const daysAgo = getDaysAgo(solution.lastTested);
            const isStale = daysAgo >= STALE_THRESHOLD_DAYS;

            return (
              <Link
                key={solution.id}
                href={`/solutions/${solution.id}`}
                className="grid grid-cols-[1fr_80px_110px_140px_100px_40px_130px_100px] items-center gap-4 px-6 py-4 border-b border-zinc-100 last:border-b-0 hover:bg-zinc-50 transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-zinc-900">{solution.name}</p>
                  <p className="text-xs text-zinc-500 mt-0.5">{solution.description}</p>
                </div>
                <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                  {solution.category === "ai" ? "AI" : "ML"}
                </p>
                <p className="text-sm text-zinc-600">{solution.riskTier}</p>
                <p className="text-sm text-zinc-600">{solution.owner}</p>
                <p className="text-sm text-zinc-600">{solution.guardrailsSummary}</p>
                {solution.gateResult === "pass" ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
                <Sparkline history={solution.healthHistory} />
                <div className="flex items-center gap-1.5">
                  {isStale ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border text-amber-700 bg-amber-50 border-amber-200">
                      <AlertTriangle className="w-3 h-3" />
                      {formatLastTested(solution.lastTested)}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs text-zinc-500">
                      <Clock className="w-3 h-3" />
                      {formatLastTested(solution.lastTested)}
                    </span>
                  )}
                </div>
              </Link>
            );
          })}
        </div>

        <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-2">How Registration Works</h3>
          <p className="text-sm text-zinc-600">
            Solutions self-register by providing a <code className="px-1.5 py-0.5 bg-zinc-200 rounded text-xs font-mono">solution.yaml</code> manifest.
            The platform discovers manifests automatically, applies the appropriate guardrail profile based on solution type and risk tier,
            and surfaces compliance status here. No manual onboarding required.
          </p>
        </div>

        <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-4">
          <div className="flex items-center gap-6 text-xs text-zinc-500">
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500" /> Pass
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-2 h-2 rounded-full bg-amber-500" /> Warn
            </span>
            <span className="flex items-center gap-1.5">
              <span className="inline-block w-2 h-2 rounded-full bg-red-500" /> Fail
            </span>
            <span className="text-zinc-300">|</span>
            <span className="flex items-center gap-1.5">
              <AlertTriangle className="w-3 h-3 text-amber-600" />
              Stale — not tested in {STALE_THRESHOLD_DAYS}+ days
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
