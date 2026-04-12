import type { OnboardFormData } from "@/app/onboard/page";

interface Props {
  data: OnboardFormData;
}

const TIER_LABELS: Record<string, string> = {
  experimental: "Experimental",
  production_internal: "Production (Internal)",
  production_customer_facing: "Production (Customer-Facing)",
};

const TYPE_LABELS: Record<string, string> = {
  endpoint: "Endpoint",
  scoring: "Scoring (ML)",
  qa: "Q&A (AI)",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-3">
        {title}
      </p>
      <div className="bg-zinc-50 rounded-lg border border-zinc-100 p-4 space-y-2">
        {children}
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  if (!value || (typeof value === "string" && !value.trim())) return null;
  return (
    <div className="flex justify-between text-sm">
      <span className="text-zinc-500">{label}</span>
      <span className="text-zinc-900 font-medium text-right max-w-[60%]">{value}</span>
    </div>
  );
}

export default function ReviewStep({ data }: Props) {
  return (
    <div className="space-y-6">
      <Section title="Basics">
        <Row label="Name" value={data.name} />
        <Row label="ID" value={<span className="font-mono">{data.id}</span>} />
        <Row label="Description" value={data.description} />
        <Row label="Version" value={data.version} />
        <Row label="Owner" value={data.owner} />
        <Row label="Risk Tier" value={TIER_LABELS[data.risk_tier] || data.risk_tier} />
        <Row label="Type" value={TYPE_LABELS[data.type] || data.type} />
      </Section>

      {data.type === "endpoint" && (
        <Section title="Endpoint Configuration">
          <Row label="URL" value={data.endpoint_url} />
          <Row label="Method" value={data.endpoint_method} />
          <Row label="Timeout" value={`${data.endpoint_timeout_ms}ms`} />
        </Section>
      )}

      {data.type === "scoring" && (
        <>
          <Section title="Model">
            <Row label="Type" value={data.model_type} />
            <Row label="Framework" value={data.model_framework} />
            <Row label="Explainability" value={data.model_explainability} />
            <Row label="Training Split" value={data.model_training_split} />
          </Section>
          <Section title="Dataset">
            <Row label="Source" value={data.dataset_source} />
            <Row label="Records" value={data.dataset_records} />
            <Row label="Features" value={data.dataset_features} />
            <Row label="Target" value={data.dataset_target} />
            <Row label="Protected Attributes" value={data.dataset_protected_attributes} />
          </Section>
        </>
      )}

      {data.type === "qa" && (
        <Section title="Corpus & Frameworks">
          <Row label="Source" value={data.corpus_source} />
          <Row
            label="Documents"
            value={
              data.corpus_documents.length > 0
                ? data.corpus_documents.map((d) => d.name).join(", ")
                : "None"
            }
          />
          <Row
            label="Frameworks"
            value={
              data.frameworks.length > 0
                ? data.frameworks.map((f) => f.name).join(", ")
                : "None"
            }
          />
        </Section>
      )}

      {data.type === "endpoint" && data.guardrail_names.length > 0 && (
        <Section title="Guardrails">
          <Row label="Enabled" value={data.guardrail_names.join(", ")} />
        </Section>
      )}

      {data.type === "qa" && (
        <Section title="Guardrails">
          <Row label="Scope Level" value={data.scope_level} />
          <Row label="Faithfulness" value={`>= ${data.faithfulness_threshold}`} />
          <Row label="Citation Coverage" value={`>= ${data.citation_coverage_threshold}`} />
          <Row label="PII Detection" value={data.pii_enabled ? "Enabled" : "Disabled"} />
          <Row label="Prompt Injection" value={data.prompt_injection_enabled ? "Enabled" : "Disabled"} />
          <Row label="Temporal Accuracy" value={data.temporal_accuracy_enabled ? "Enabled" : "Disabled"} />
        </Section>
      )}

      {data.type === "scoring" && (
        <Section title="Guardrails">
          <Row label="Discrimination Method" value={data.discrimination_method} />
          <Row label="Flag Threshold" value={data.discrimination_threshold} />
          <Row label="Brier Score" value={`<= ${data.brier_score_threshold}`} />
          <Row label="ECE" value={`<= ${data.ece_threshold}`} />
        </Section>
      )}

      {data.evaluation_metrics.length > 0 && (
        <Section title="Evaluation Metrics">
          {data.evaluation_metrics.map((m, i) => (
            <Row
              key={i}
              label={m.name}
              value={
                m.direction === "lower_is_better"
                  ? `<= ${m.threshold}`
                  : `>= ${m.threshold}`
              }
            />
          ))}
        </Section>
      )}

      <Section title="Compliance Gates">
        <Row
          label="Active gates"
          value={`${data.compliance_gates.length} of 8`}
        />
        <div className="flex flex-wrap gap-1.5 pt-1">
          {data.compliance_gates.map((g) => (
            <span
              key={g}
              className="px-2 py-0.5 bg-zinc-200 text-zinc-700 rounded text-xs"
            >
              {g.replace(/_/g, " ")}
            </span>
          ))}
        </div>
      </Section>
    </div>
  );
}
