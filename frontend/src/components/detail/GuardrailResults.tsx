import { GuardrailResult } from "@/lib/types";
import HealthBadge from "@/components/dashboard/HealthBadge";

export default function GuardrailResults({ guardrails }: { guardrails: GuardrailResult[] }) {
  return (
    <div className="bg-white border border-zinc-200 rounded-lg">
      <div className="px-6 py-4 border-b border-zinc-100">
        <h3 className="text-sm font-semibold text-zinc-900">Guardrail Results</h3>
      </div>
      <div className="divide-y divide-zinc-100">
        {guardrails.map((g) => (
          <div key={g.name} className="grid grid-cols-[1fr_80px_80px_80px] items-center gap-4 px-6 py-3">
            <p className="text-sm text-zinc-700">{g.name}</p>
            <p className="text-sm text-zinc-500 col-span-2">{g.detail}</p>
            <HealthBadge status={g.result} />
          </div>
        ))}
      </div>
    </div>
  );
}
