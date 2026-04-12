import { Plus, X } from "lucide-react";
import type { OnboardFormData, MetricEntry } from "@/app/onboard/page";

interface Props {
  data: OnboardFormData;
  onChange: (patch: Partial<OnboardFormData>) => void;
}

const inputClass =
  "w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent";

const ALL_GATES = [
  "registration",
  "evaluation_harness",
  "pii_validation",
  "guardrail_validation",
  "bias_toxicity",
  "audit_trail",
  "golden_dataset_signoff",
  "prompt_governance",
];

const PRESET_METRICS: Record<string, MetricEntry[]> = {
  qa: [
    { name: "faithfulness", threshold: 0.9, direction: "" },
    { name: "answer_relevancy", threshold: 0.85, direction: "" },
    { name: "contextual_precision", threshold: 0.8, direction: "" },
    { name: "contextual_recall", threshold: 0.75, direction: "" },
    { name: "hallucination", threshold: 0.1, direction: "lower_is_better" },
    { name: "citation_coverage", threshold: 0.95, direction: "" },
    { name: "bias", threshold: 0.05, direction: "lower_is_better" },
    { name: "toxicity", threshold: 0.05, direction: "lower_is_better" },
  ],
  scoring: [
    { name: "auc_roc", threshold: 0.7, direction: "" },
    { name: "gini", threshold: 0.4, direction: "" },
    { name: "brier_score", threshold: 0.25, direction: "lower_is_better" },
    { name: "shap_coverage", threshold: 1.0, direction: "" },
  ],
  endpoint: [
    { name: "accuracy", threshold: 0.85, direction: "" },
    { name: "bias", threshold: 0.05, direction: "lower_is_better" },
    { name: "consistency", threshold: 0.9, direction: "" },
  ],
};

export default function EvaluationStep({ data, onChange }: Props) {
  const addMetric = () => {
    onChange({
      evaluation_metrics: [
        ...data.evaluation_metrics,
        { name: "", threshold: 0.8, direction: "" },
      ],
    });
  };

  const removeMetric = (i: number) => {
    onChange({
      evaluation_metrics: data.evaluation_metrics.filter((_, idx) => idx !== i),
    });
  };

  const updateMetric = (i: number, patch: Partial<MetricEntry>) => {
    const updated = data.evaluation_metrics.map((m, idx) =>
      idx === i ? { ...m, ...patch } : m,
    );
    onChange({ evaluation_metrics: updated });
  };

  const loadPreset = () => {
    const preset = PRESET_METRICS[data.type] || [];
    onChange({ evaluation_metrics: [...preset] });
  };

  const toggleGate = (gate: string) => {
    const set = new Set(data.compliance_gates);
    if (set.has(gate)) set.delete(gate);
    else set.add(gate);
    onChange({ compliance_gates: Array.from(set) });
  };

  return (
    <div className="space-y-8">
      {/* Metrics */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Evaluation Metrics
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={loadPreset}
              className="text-xs text-zinc-500 hover:text-zinc-900 border border-zinc-200 px-2 py-1 rounded"
            >
              Load defaults for {data.type}
            </button>
            <button
              type="button"
              onClick={addMetric}
              className="inline-flex items-center gap-1 text-xs text-zinc-600 hover:text-zinc-900"
            >
              <Plus className="w-3 h-3" /> Add
            </button>
          </div>
        </div>

        {data.evaluation_metrics.length === 0 ? (
          <p className="text-sm text-zinc-400 py-4 text-center border border-dashed border-zinc-200 rounded-lg">
            No metrics configured. Click &quot;Load defaults&quot; or add manually.
          </p>
        ) : (
          <div className="space-y-2">
            <div className="grid grid-cols-[1fr_100px_140px_32px] gap-2 text-xs text-zinc-400 font-medium px-1">
              <span>Metric</span>
              <span>Threshold</span>
              <span>Direction</span>
              <span />
            </div>
            {data.evaluation_metrics.map((m, i) => (
              <div key={i} className="grid grid-cols-[1fr_100px_140px_32px] gap-2 items-center">
                <input
                  type="text"
                  value={m.name}
                  onChange={(e) => updateMetric(i, { name: e.target.value })}
                  placeholder="metric_name"
                  className={inputClass}
                />
                <input
                  type="number"
                  step="0.01"
                  value={m.threshold}
                  onChange={(e) => updateMetric(i, { threshold: parseFloat(e.target.value) || 0 })}
                  className={inputClass}
                />
                <select
                  value={m.direction}
                  onChange={(e) => updateMetric(i, { direction: e.target.value })}
                  className={inputClass}
                >
                  <option value="">Higher is better</option>
                  <option value="lower_is_better">Lower is better</option>
                </select>
                <button
                  type="button"
                  onClick={() => removeMetric(i)}
                  className="text-zinc-400 hover:text-red-500"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compliance gates */}
      <div>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-4">
          Compliance Gates
        </p>
        <div className="grid grid-cols-2 gap-2">
          {ALL_GATES.map((gate) => (
            <label key={gate} className="flex items-center gap-3 py-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={data.compliance_gates.includes(gate)}
                onChange={() => toggleGate(gate)}
                className="w-4 h-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900"
              />
              <span className="text-sm text-zinc-700">
                {gate.replace(/_/g, " ")}
              </span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
