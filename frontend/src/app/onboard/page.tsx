"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Loader2, Rocket } from "lucide-react";
import Header from "@/components/layout/Header";
import StepIndicator from "@/components/onboard/StepIndicator";
import BasicInfoStep from "@/components/onboard/steps/BasicInfoStep";
import ConfigurationStep from "@/components/onboard/steps/ConfigurationStep";
import GuardrailsStep from "@/components/onboard/steps/GuardrailsStep";
import EvaluationStep from "@/components/onboard/steps/EvaluationStep";
import ReviewStep from "@/components/onboard/steps/ReviewStep";
import { onboardSolution } from "@/lib/api";

// ── Types ────────────────────────────────────────────────────────────────

export interface CorpusDocument {
  name: string;
  format: string;
  pages: number;
}

export interface FrameworkEntry {
  name: string;
  retrieval_strategies: string[];
}

export interface MetricEntry {
  name: string;
  threshold: number;
  direction: string;
}

export interface OnboardFormData {
  // Step 1 — Basics
  name: string;
  id: string;
  idManuallyEdited: boolean;
  description: string;
  version: string;
  owner: string;
  risk_tier: string;
  type: string;

  // Step 2 — Endpoint
  endpoint_url: string;
  endpoint_method: string;
  endpoint_timeout_ms: number;

  // Step 2 — Scoring
  model_type: string;
  model_framework: string;
  model_explainability: string;
  model_training_split: number;
  dataset_source: string;
  dataset_records: number;
  dataset_features: number;
  dataset_target: string;
  dataset_protected_attributes: string;

  // Step 2 — QA
  corpus_source: string;
  corpus_documents: CorpusDocument[];
  frameworks: FrameworkEntry[];

  // Step 3 — Guardrails (Endpoint)
  guardrail_names: string[];

  // Step 3 — Guardrails (Scoring)
  discrimination_method: string;
  discrimination_threshold: number;
  brier_score_threshold: number;
  ece_threshold: number;
  psi_warning: number;
  psi_alert: number;
  psi_block: number;

  // Step 3 — Guardrails (QA)
  scope_level: number;
  scope_refusal_message: string;
  citation_coverage_threshold: number;
  temporal_accuracy_enabled: boolean;
  pii_enabled: boolean;
  prompt_injection_enabled: boolean;

  // Step 4 — Evaluation & Compliance
  evaluation_metrics: MetricEntry[];
  compliance_gates: string[];
}

const DEFAULTS: OnboardFormData = {
  name: "",
  id: "",
  idManuallyEdited: false,
  description: "",
  version: "1.0.0",
  owner: "",
  risk_tier: "production_internal",
  type: "qa",

  endpoint_url: "",
  endpoint_method: "POST",
  endpoint_timeout_ms: 30000,

  model_type: "",
  model_framework: "",
  model_explainability: "SHAP",
  model_training_split: 0.7,
  dataset_source: "",
  dataset_records: 0,
  dataset_features: 0,
  dataset_target: "",
  dataset_protected_attributes: "",

  corpus_source: "",
  corpus_documents: [],
  frameworks: [],

  guardrail_names: ["scope_adherence", "pii_scan", "bias", "toxicity"],

  discrimination_method: "subgroup_approval_rate_analysis",
  discrimination_threshold: 0.15,
  brier_score_threshold: 0.25,
  ece_threshold: 0.05,
  psi_warning: 0.10,
  psi_alert: 0.20,
  psi_block: 0.25,

  scope_level: 1,
  scope_refusal_message: "",
  citation_coverage_threshold: 0.95,
  temporal_accuracy_enabled: true,
  pii_enabled: true,
  prompt_injection_enabled: true,

  evaluation_metrics: [],
  compliance_gates: [
    "registration",
    "evaluation_harness",
    "pii_validation",
    "guardrail_validation",
    "bias_toxicity",
    "audit_trail",
    "golden_dataset_signoff",
    "prompt_governance",
  ],
};

// ── Helpers ──────────────────────────────────────────────────────────────

function buildPayload(data: OnboardFormData): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    name: data.name,
    id: data.id,
    description: data.description,
    version: data.version,
    owner: data.owner,
    risk_tier: data.risk_tier,
    type: data.type,
    evaluation_metrics: data.evaluation_metrics
      .filter((m) => m.name.trim())
      .map((m) => ({
        name: m.name,
        threshold: m.threshold,
        ...(m.direction ? { direction: m.direction } : {}),
      })),
    compliance_gates: data.compliance_gates,
  };

  if (data.type === "endpoint") {
    payload.endpoint = {
      url: data.endpoint_url,
      method: data.endpoint_method,
      timeout_ms: data.endpoint_timeout_ms,
    };
    payload.guardrails = { names: data.guardrail_names };
  }

  if (data.type === "scoring") {
    payload.model = {
      type: data.model_type,
      framework: data.model_framework,
      explainability: data.model_explainability,
      training_split: data.model_training_split,
    };
    payload.dataset = {
      source: data.dataset_source,
      records: data.dataset_records,
      features: data.dataset_features,
      target: data.dataset_target,
      protected_attributes: data.dataset_protected_attributes
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    };
    payload.guardrails = {
      proxy_discrimination: {
        method: data.discrimination_method,
        flag_threshold: data.discrimination_threshold,
        human_review_required: true,
      },
      calibration: {
        brier_score_threshold: data.brier_score_threshold,
        ece_threshold: data.ece_threshold,
      },
      stability: {
        psi_warning: data.psi_warning,
        psi_alert: data.psi_alert,
        psi_block: data.psi_block,
      },
    };
  }

  if (data.type === "qa") {
    payload.corpus = {
      source: data.corpus_source,
      documents: data.corpus_documents.filter((d) => d.name.trim()),
    };
    if (data.frameworks.length > 0) {
      payload.frameworks = data.frameworks;
    }
    payload.guardrails = {
      scope: {
        level: data.scope_level,
        topic_graph: "topic_graph.json",
        refusal_message: data.scope_refusal_message || undefined,
      },
      citation_coverage_threshold: data.citation_coverage_threshold,
      temporal_accuracy_enabled: data.temporal_accuracy_enabled,
      pii_enabled: data.pii_enabled,
      prompt_injection_enabled: data.prompt_injection_enabled,
    };
  }

  return payload;
}

function validateStep(step: number, data: OnboardFormData): string | null {
  if (step === 0) {
    if (!data.name.trim()) return "Solution name is required";
    if (!data.id.trim()) return "Solution ID is required";
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(data.id))
      return "ID must be lowercase alphanumeric with hyphens";
    if (!data.owner.trim()) return "Owner is required";
  }
  if (step === 1) {
    if (data.type === "endpoint" && !data.endpoint_url.trim())
      return "Endpoint URL is required";
    if (data.type === "scoring" && !data.model_type.trim())
      return "Model type is required";
    if (data.type === "scoring" && !data.dataset_source.trim())
      return "Dataset source is required";
    if (data.type === "qa" && !data.corpus_source.trim())
      return "Corpus source is required";
  }
  return null;
}

// ── Component ────────────────────────────────────────────────────────────

const TOTAL_STEPS = 5;

export default function OnboardPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [data, setData] = useState<OnboardFormData>(DEFAULTS);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onChange = (patch: Partial<OnboardFormData>) => {
    setData((prev) => ({ ...prev, ...patch }));
    setError(null);
  };

  const next = () => {
    const err = validateStep(step, data);
    if (err) {
      setError(err);
      return;
    }
    setStep((s) => Math.min(s + 1, TOTAL_STEPS - 1));
    setError(null);
  };

  const back = () => {
    setStep((s) => Math.max(s - 1, 0));
    setError(null);
  };

  const submit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const payload = buildPayload(data);
      const res = await onboardSolution(payload);
      router.push(`/solutions/${res.id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to onboard solution");
    } finally {
      setSubmitting(false);
    }
  };

  const isLastStep = step === TOTAL_STEPS - 1;

  return (
    <div>
      <Header
        title="Onboard Solution"
        subtitle="Register a new AI or ML solution with the platform"
      />

      <div className="px-8 py-6 space-y-6">
        {/* Step indicator */}
        <StepIndicator current={step} />

        {/* Step content card */}
        <div className="bg-white border border-zinc-200 rounded-lg">
          <div className="px-6 py-4 border-b border-zinc-100">
            <h2 className="text-sm font-semibold text-zinc-900">
              {["Basic Information", "Configuration", "Guardrails", "Evaluation & Compliance", "Review & Submit"][step]}
            </h2>
          </div>
          <div className="px-6 py-6">
            {step === 0 && <BasicInfoStep data={data} onChange={onChange} />}
            {step === 1 && <ConfigurationStep data={data} onChange={onChange} />}
            {step === 2 && <GuardrailsStep data={data} onChange={onChange} />}
            {step === 3 && <EvaluationStep data={data} onChange={onChange} />}
            {step === 4 && <ReviewStep data={data} />}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={back}
            disabled={step === 0}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              step === 0
                ? "text-zinc-300 cursor-not-allowed"
                : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
            }`}
          >
            <ArrowLeft className="w-4 h-4" /> Back
          </button>

          {isLastStep ? (
            <button
              type="button"
              onClick={submit}
              disabled={submitting}
              className="inline-flex items-center gap-2 px-6 py-2 bg-zinc-900 text-white rounded-md text-sm font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Onboarding...
                </>
              ) : (
                <>
                  <Rocket className="w-4 h-4" /> Onboard Solution
                </>
              )}
            </button>
          ) : (
            <button
              type="button"
              onClick={next}
              className="inline-flex items-center gap-2 px-4 py-2 bg-zinc-900 text-white rounded-md text-sm font-medium hover:bg-zinc-800 transition-colors"
            >
              Next <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
