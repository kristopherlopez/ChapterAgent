import type { OnboardFormData } from "@/app/onboard/page";

interface Props {
  data: OnboardFormData;
  onChange: (patch: Partial<OnboardFormData>) => void;
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

const RISK_TIERS = [
  { value: "experimental", label: "Experimental" },
  { value: "production_internal", label: "Production (Internal)" },
  { value: "production_customer_facing", label: "Production (Customer-Facing)" },
];

const TYPES = [
  { value: "endpoint", label: "Endpoint", desc: "External API endpoint (classification, validation)" },
  { value: "scoring", label: "Scoring (ML)", desc: "ML model with training data and fairness metrics" },
  { value: "qa", label: "Q&A (AI)", desc: "RAG agent with corpus, citations, and scope guardrails" },
];

export default function BasicInfoStep({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      {/* Name */}
      <div>
        <label className="block text-sm font-medium text-zinc-700 mb-1">
          Solution Name
        </label>
        <input
          type="text"
          value={data.name}
          onChange={(e) => {
            const name = e.target.value;
            const patch: Partial<OnboardFormData> = { name };
            if (!data.idManuallyEdited) {
              patch.id = slugify(name);
            }
            onChange(patch);
          }}
          placeholder="e.g. CBA Annual Report Q&A Agent"
          className="w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
        />
      </div>

      {/* ID */}
      <div>
        <label className="block text-sm font-medium text-zinc-700 mb-1">
          Solution ID
        </label>
        <input
          type="text"
          value={data.id}
          onChange={(e) =>
            onChange({ id: e.target.value, idManuallyEdited: true })
          }
          placeholder="e.g. cba-annual-report-qa"
          className="w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white font-mono focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
        />
        <p className="text-xs text-zinc-400 mt-1">
          Lowercase, hyphens only. Auto-generated from name.
        </p>
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-zinc-700 mb-1">
          Description
        </label>
        <textarea
          value={data.description}
          onChange={(e) => onChange({ description: e.target.value })}
          rows={3}
          placeholder="What does this solution do?"
          className="w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent resize-none"
        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Version */}
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">
            Version
          </label>
          <input
            type="text"
            value={data.version}
            onChange={(e) => onChange({ version: e.target.value })}
            className="w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
          />
        </div>

        {/* Owner */}
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">
            Owner
          </label>
          <input
            type="text"
            value={data.owner}
            onChange={(e) => onChange({ owner: e.target.value })}
            placeholder="e.g. Chapter Platform Team"
            className="w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
          />
        </div>
      </div>

      {/* Risk Tier */}
      <div>
        <label className="block text-sm font-medium text-zinc-700 mb-1">
          Risk Tier
        </label>
        <select
          value={data.risk_tier}
          onChange={(e) => onChange({ risk_tier: e.target.value })}
          className="w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
        >
          {RISK_TIERS.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {/* Type */}
      <div>
        <label className="block text-sm font-medium text-zinc-700 mb-2">
          Solution Type
        </label>
        <div className="grid grid-cols-3 gap-3">
          {TYPES.map((t) => (
            <button
              key={t.value}
              type="button"
              onClick={() => onChange({ type: t.value })}
              className={`text-left p-4 rounded-lg border-2 transition-colors ${
                data.type === t.value
                  ? "border-zinc-900 bg-zinc-50"
                  : "border-zinc-200 hover:border-zinc-300"
              }`}
            >
              <p className="text-sm font-medium text-zinc-900">{t.label}</p>
              <p className="text-xs text-zinc-500 mt-1">{t.desc}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
