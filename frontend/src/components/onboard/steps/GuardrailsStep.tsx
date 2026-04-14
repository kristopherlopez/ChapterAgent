import type { OnboardFormData } from "@/app/onboard/page";

interface Props {
  data: OnboardFormData;
  onChange: (patch: Partial<OnboardFormData>) => void;
}

const inputClass =
  "w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent";

const ENDPOINT_GUARDRAILS = [
  "scope_adherence",
  "pii_scan",
  "bias",
  "toxicity",
  "prompt_injection",
];

function Toggle({
  label,
  checked,
  onToggle,
}: {
  label: string;
  checked: boolean;
  onToggle: () => void;
}) {
  return (
    <label className="flex items-center gap-3 py-2 cursor-pointer">
      <div
        className={`w-9 h-5 rounded-full transition-colors relative ${
          checked ? "bg-zinc-900" : "bg-zinc-200"
        }`}
        onClick={onToggle}
      >
        <div
          className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-transform ${
            checked ? "translate-x-4" : "translate-x-0.5"
          }`}
        />
      </div>
      <span className="text-sm text-zinc-700">{label}</span>
    </label>
  );
}

function EndpointGuardrails({ data, onChange }: Props) {
  const selected = new Set(data.guardrail_names);
  const toggle = (name: string) => {
    const next = new Set(selected);
    if (next.has(name)) next.delete(name);
    else next.add(name);
    onChange({ guardrail_names: Array.from(next) });
  };

  return (
    <div className="space-y-2">
      <p className="text-sm text-zinc-500 mb-4">
        Select which guardrails to enable for this endpoint.
      </p>
      {ENDPOINT_GUARDRAILS.map((g) => (
        <label key={g} className="flex items-center gap-3 py-1.5 cursor-pointer">
          <input
            type="checkbox"
            checked={selected.has(g)}
            onChange={() => toggle(g)}
            className="w-4 h-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900"
          />
          <span className="text-sm text-zinc-700">{g.replace(/_/g, " ")}</span>
        </label>
      ))}
    </div>
  );
}

function ScoringGuardrails({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-3">
          Proxy Discrimination
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Method</label>
            <select
              value={data.discrimination_method}
              onChange={(e) => onChange({ discrimination_method: e.target.value })}
              className={inputClass}
            >
              <option value="subgroup_approval_rate_analysis">Subgroup Approval Rate Analysis</option>
              <option value="demographic_parity">Demographic Parity</option>
              <option value="equalised_odds">Equalised Odds</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Flag Threshold</label>
            <input
              type="number"
              step="0.01"
              value={data.discrimination_threshold}
              onChange={(e) => onChange({ discrimination_threshold: parseFloat(e.target.value) || 0.15 })}
              className={inputClass}
            />
          </div>
        </div>
      </div>

      <div>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-3">
          Calibration
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Brier Score Threshold</label>
            <input
              type="number"
              step="0.01"
              value={data.brier_score_threshold}
              onChange={(e) => onChange({ brier_score_threshold: parseFloat(e.target.value) || 0.25 })}
              className={inputClass}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">ECE Threshold</label>
            <input
              type="number"
              step="0.01"
              value={data.ece_threshold}
              onChange={(e) => onChange({ ece_threshold: parseFloat(e.target.value) || 0.05 })}
              className={inputClass}
            />
          </div>
        </div>
      </div>

      <div>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-3">
          Stability (PSI)
        </p>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Warning</label>
            <input
              type="number"
              step="0.01"
              value={data.psi_warning}
              onChange={(e) => onChange({ psi_warning: parseFloat(e.target.value) || 0.10 })}
              className={inputClass}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Alert</label>
            <input
              type="number"
              step="0.01"
              value={data.psi_alert}
              onChange={(e) => onChange({ psi_alert: parseFloat(e.target.value) || 0.20 })}
              className={inputClass}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Block</label>
            <input
              type="number"
              step="0.01"
              value={data.psi_block}
              onChange={(e) => onChange({ psi_block: parseFloat(e.target.value) || 0.25 })}
              className={inputClass}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function QAGuardrails({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-3">
          Scope Adherence
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Scope Level</label>
            <select
              value={data.scope_level}
              onChange={(e) => onChange({ scope_level: parseInt(e.target.value) })}
              className={inputClass}
            >
              <option value={1}>Level 1 (Strict)</option>
              <option value={2}>Level 2 (Moderate)</option>
              <option value={3}>Level 3 (Permissive)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Refusal Message</label>
            <input
              type="text"
              value={data.scope_refusal_message}
              onChange={(e) => onChange({ scope_refusal_message: e.target.value })}
              placeholder="I can only answer questions about..."
              className={inputClass}
            />
          </div>
        </div>
      </div>

      <div>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-3">
          Thresholds
        </p>
        <div className="grid grid-cols-2 gap-4">
<div>
            <label className="block text-sm font-medium text-zinc-700 mb-1">Citation Coverage</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={data.citation_coverage_threshold}
              onChange={(e) => onChange({ citation_coverage_threshold: parseFloat(e.target.value) || 0.95 })}
              className={inputClass}
            />
          </div>
        </div>
      </div>

      <div>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-3">
          Additional Guardrails
        </p>
        <Toggle
          label="Temporal Accuracy"
          checked={data.temporal_accuracy_enabled}
          onToggle={() => onChange({ temporal_accuracy_enabled: !data.temporal_accuracy_enabled })}
        />
        <Toggle
          label="PII Detection"
          checked={data.pii_enabled}
          onToggle={() => onChange({ pii_enabled: !data.pii_enabled })}
        />
        <Toggle
          label="Prompt Injection Detection"
          checked={data.prompt_injection_enabled}
          onToggle={() => onChange({ prompt_injection_enabled: !data.prompt_injection_enabled })}
        />
      </div>
    </div>
  );
}

export default function GuardrailsStep({ data, onChange }: Props) {
  return (
    <div>
      {data.type === "endpoint" && <EndpointGuardrails data={data} onChange={onChange} />}
      {data.type === "scoring" && <ScoringGuardrails data={data} onChange={onChange} />}
      {data.type === "qa" && <QAGuardrails data={data} onChange={onChange} />}
    </div>
  );
}
