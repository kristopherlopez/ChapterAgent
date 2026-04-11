import { ComplianceGate as ComplianceGateType } from "@/lib/types";
import HealthBadge from "@/components/dashboard/HealthBadge";

export default function ComplianceGate({ gate }: { gate: ComplianceGateType }) {
  return (
    <div className="bg-white border border-zinc-200 rounded-lg">
      <div className="px-6 py-4 border-b border-zinc-100">
        <h3 className="text-sm font-semibold text-zinc-900">Compliance Gate</h3>
      </div>
      <div className="px-6 py-4 space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-sm text-zinc-700">{gate.gate}</p>
          <HealthBadge status={gate.result} />
        </div>
        <p className="text-sm text-zinc-500">{gate.reason}</p>
        <p className="text-xs text-zinc-400">Evaluated at {gate.timestamp}</p>
      </div>
    </div>
  );
}
