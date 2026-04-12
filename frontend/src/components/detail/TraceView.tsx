import type { TraceStep } from "@/lib/types";

export default function TraceView({ steps }: { steps: TraceStep[] }) {
  return (
    <div>
      <h2 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-3">
        Execution Trace
      </h2>
      <div className="bg-white border border-zinc-200 rounded-lg">
        <div className="grid grid-cols-[48px_1fr_100px_1fr] items-center gap-4 px-6 py-4 border-b border-zinc-100">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Step</p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Label</p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Duration</p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Detail</p>
        </div>
        {steps.map((step) => (
          <div
            key={step.step}
            className="grid grid-cols-[48px_1fr_100px_1fr] items-center gap-4 px-6 py-3 border-b border-zinc-100 last:border-b-0"
          >
            <p className="text-sm font-mono text-zinc-400">{step.step}</p>
            <p className="text-sm text-zinc-700">{step.label}</p>
            <p className="text-sm font-mono text-zinc-600">
              {step.durationMs > 0 ? `${step.durationMs}ms` : "—"}
            </p>
            <p className="text-sm text-zinc-500">{step.detail || "—"}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
