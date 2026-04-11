import { solutions } from "@/lib/data";
import { CheckCircle2, XCircle, Clock } from "lucide-react";

export default function ComplianceSummary() {
  const passing = solutions.filter((s) => s.health === "pass").length;
  const failing = solutions.filter((s) => s.health === "fail").length;
  const total = solutions.length;

  return (
    <div className="grid grid-cols-3 gap-4 px-8 py-6">
      <div className="bg-white border border-zinc-200 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-50 rounded-lg">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p className="text-2xl font-semibold text-zinc-900">{passing}</p>
            <p className="text-xs text-zinc-500">Deployment-ready</p>
          </div>
        </div>
      </div>
      <div className="bg-white border border-zinc-200 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-50 rounded-lg">
            <XCircle className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <p className="text-2xl font-semibold text-zinc-900">{failing}</p>
            <p className="text-xs text-zinc-500">Blocked</p>
          </div>
        </div>
      </div>
      <div className="bg-white border border-zinc-200 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-zinc-100 rounded-lg">
            <Clock className="w-5 h-5 text-zinc-500" />
          </div>
          <div>
            <p className="text-2xl font-semibold text-zinc-900">{total}</p>
            <p className="text-xs text-zinc-500">Total solutions</p>
          </div>
        </div>
      </div>
    </div>
  );
}
