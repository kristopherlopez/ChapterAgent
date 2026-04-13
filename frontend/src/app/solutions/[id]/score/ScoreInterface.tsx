"use client";

import { useState } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  Clock,
  Loader2,
  TrendingUp,
  TrendingDown,
  Users,
  BarChart3,
} from "lucide-react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SHAPContributor {
  feature: string;
  direction: string;
  shap_value: number;
}

interface GuardrailResult {
  name: string;
  status: string;
  detail?: string;
}

interface ScoreResult {
  scoring_id: string;
  applicant_id: string;
  default_probability: number;
  risk_band: string;
  recommendation: string;
  shap_contributors: SHAPContributor[];
  baseline_probability: number;
  guardrails: GuardrailResult[];
  latency_ms: number;
  blocked: boolean;
}

interface ProbeResult {
  results: ScoreResult[];
  score_difference: number;
  tolerance: number;
  discrimination_pass: boolean;
}

// ---------------------------------------------------------------------------
// Sample profiles (pre-loaded for one-click scoring)
// ---------------------------------------------------------------------------

const SAMPLE_PROFILES: Record<string, { label: string; desc: string; features: Record<string, number> }> = {
  low_risk: {
    label: "Low Risk",
    desc: "High credit limit, clean payment history, bills paid in full",
    features: {
      LIMIT_BAL: 300000, PAY_0: 0, PAY_2: 0, PAY_3: 0, PAY_4: 0, PAY_5: 0, PAY_6: 0,
      BILL_AMT1: 50000, BILL_AMT2: 48000, BILL_AMT3: 45000,
      BILL_AMT4: 42000, BILL_AMT5: 40000, BILL_AMT6: 38000,
    },
  },
  high_risk: {
    label: "High Risk",
    desc: "Low credit limit, repeated late payments, near-maxed utilisation",
    features: {
      LIMIT_BAL: 50000, PAY_0: 3, PAY_2: 2, PAY_3: 2, PAY_4: 2, PAY_5: 2, PAY_6: 2,
      BILL_AMT1: 49000, BILL_AMT2: 48000, BILL_AMT3: 47000,
      BILL_AMT4: 46000, BILL_AMT5: 45000, BILL_AMT6: 44000,
    },
  },
  deteriorating: {
    label: "Deteriorating",
    desc: "Was current, now 3 months late. Bills rising, payments shrinking",
    features: {
      LIMIT_BAL: 100000, PAY_0: 3, PAY_2: 2, PAY_3: 1, PAY_4: 0, PAY_5: 0, PAY_6: -1,
      BILL_AMT1: 95000, BILL_AMT2: 85000, BILL_AMT3: 70000,
      BILL_AMT4: 55000, BILL_AMT5: 40000, BILL_AMT6: 30000,
    },
  },
};

const PROBE_TYPES: Record<string, { label: string; variants: Record<string, number>[] }> = {
  gender: {
    label: "Gender",
    variants: [
      { SEX: 1, label: "Male" } as any,
      { SEX: 2, label: "Female" } as any,
    ],
  },
  age: {
    label: "Age Band",
    variants: [
      { AGE: 25, label: "25 (Young)" } as any,
      { AGE: 55, label: "55 (Older)" } as any,
    ],
  },
  education: {
    label: "Education",
    variants: [
      { EDUCATION: 1, label: "Graduate" } as any,
      { EDUCATION: 3, label: "High School" } as any,
    ],
  },
  marital: {
    label: "Marital Status",
    variants: [
      { MARRIAGE: 1, label: "Married" } as any,
      { MARRIAGE: 2, label: "Single" } as any,
    ],
  },
};

// ---------------------------------------------------------------------------
// Demo fallback responses
// ---------------------------------------------------------------------------

const DEMO_SCORES: Record<string, ScoreResult> = {
  low_risk: {
    scoring_id: "SCR-DEMO-001", applicant_id: "DEMO-001",
    default_probability: 0.08, risk_band: "LOW", recommendation: "No action",
    shap_contributors: [
      { feature: "PAY_0", direction: "decreases_risk", shap_value: -0.09 },
      { feature: "LIMIT_BAL", direction: "decreases_risk", shap_value: -0.06 },
      { feature: "BILL_AMT1", direction: "increases_risk", shap_value: 0.02 },
      { feature: "PAY_2", direction: "decreases_risk", shap_value: -0.01 },
    ],
    baseline_probability: 0.22,
    guardrails: [
      { name: "Discrimination Check", status: "pass", detail: "DI ratio: 0.93" },
      { name: "Calibration Check", status: "pass", detail: "Brier: 0.14" },
      { name: "Stability Check", status: "pass", detail: "PSI: 0.08" },
      { name: "Explainability Check", status: "pass", detail: "SHAP coverage: 100%" },
    ],
    latency_ms: 45, blocked: false,
  },
  high_risk: {
    scoring_id: "SCR-DEMO-002", applicant_id: "DEMO-002",
    default_probability: 0.72, risk_band: "VERY_HIGH", recommendation: "Immediate intervention",
    shap_contributors: [
      { feature: "PAY_0", direction: "increases_risk", shap_value: 0.22 },
      { feature: "PAY_2", direction: "increases_risk", shap_value: 0.14 },
      { feature: "LIMIT_BAL", direction: "increases_risk", shap_value: 0.08 },
      { feature: "BILL_AMT1", direction: "increases_risk", shap_value: 0.06 },
    ],
    baseline_probability: 0.22,
    guardrails: [
      { name: "Discrimination Check", status: "pass", detail: "DI ratio: 0.91" },
      { name: "Calibration Check", status: "pass", detail: "Brier: 0.14" },
      { name: "Stability Check", status: "pass", detail: "PSI: 0.08" },
      { name: "Explainability Check", status: "pass", detail: "SHAP coverage: 100%" },
    ],
    latency_ms: 48, blocked: false,
  },
  deteriorating: {
    scoring_id: "SCR-DEMO-003", applicant_id: "DEMO-003",
    default_probability: 0.45, risk_band: "HIGH", recommendation: "Proactive outreach",
    shap_contributors: [
      { feature: "PAY_0", direction: "increases_risk", shap_value: 0.18 },
      { feature: "PAY_2", direction: "increases_risk", shap_value: 0.10 },
      { feature: "LIMIT_BAL", direction: "decreases_risk", shap_value: -0.04 },
      { feature: "BILL_AMT1", direction: "increases_risk", shap_value: 0.08 },
    ],
    baseline_probability: 0.22,
    guardrails: [
      { name: "Discrimination Check", status: "pass", detail: "DI ratio: 0.89" },
      { name: "Calibration Check", status: "pass", detail: "Brier: 0.14" },
      { name: "Stability Check", status: "pass", detail: "PSI: 0.08" },
      { name: "Explainability Check", status: "pass", detail: "SHAP coverage: 100%" },
    ],
    latency_ms: 42, blocked: false,
  },
};

const DEMO_PROBE: ProbeResult = {
  results: [
    { ...DEMO_SCORES.low_risk, applicant_id: "Male", default_probability: 0.22 },
    { ...DEMO_SCORES.low_risk, applicant_id: "Female", default_probability: 0.31 },
  ],
  score_difference: 0.09,
  tolerance: 0.02,
  discrimination_pass: false,
};

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

async function fetchScore(solutionId: string, features: Record<string, number>): Promise<ScoreResult | null> {
  try {
    const res = await fetch(`${API_BASE}/api/score/${solutionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ features }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

async function fetchProbe(
  solutionId: string,
  baseProfile: Record<string, number>,
  variants: Record<string, any>[],
  tolerance: number,
): Promise<ProbeResult | null> {
  try {
    const res = await fetch(`${API_BASE}/api/score/${solutionId}/probe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ base_profile: baseProfile, variants, tolerance }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Colour helpers
// ---------------------------------------------------------------------------

function riskBandColour(band: string): string {
  switch (band) {
    case "LOW": return "bg-green-100 text-green-800 border-green-200";
    case "MEDIUM": return "bg-yellow-100 text-yellow-800 border-yellow-200";
    case "HIGH": return "bg-orange-100 text-orange-800 border-orange-200";
    case "VERY_HIGH": return "bg-red-100 text-red-800 border-red-200";
    default: return "bg-zinc-100 text-zinc-800 border-zinc-200";
  }
}

function probabilityColour(p: number): string {
  if (p < 0.1) return "text-green-600";
  if (p < 0.3) return "text-yellow-600";
  if (p < 0.6) return "text-orange-600";
  return "text-red-600";
}

function barColour(direction: string): string {
  return direction === "increases_risk" ? "bg-red-500" : "bg-green-500";
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ScoreResultCard({ result }: { result: ScoreResult }) {
  const maxShap = Math.max(...result.shap_contributors.map(c => Math.abs(c.shap_value)), 0.01);

  return (
    <div className="space-y-4">
      {/* Probability + Risk Band */}
      <div className="flex items-center gap-6">
        <div>
          <div className="text-xs text-zinc-500 uppercase tracking-wider mb-1">Default Probability</div>
          <div className={`text-4xl font-bold ${probabilityColour(result.default_probability)}`}>
            {(result.default_probability * 100).toFixed(1)}%
          </div>
        </div>
        <div>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border ${riskBandColour(result.risk_band)}`}>
            {result.risk_band.replace("_", " ")}
          </span>
          <div className="text-sm text-zinc-600 mt-1">{result.recommendation}</div>
        </div>
      </div>

      {/* SHAP Waterfall */}
      <div>
        <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Why this score (SHAP)</div>
        <div className="text-xs text-zinc-400 mb-2">Baseline default rate: {(result.baseline_probability * 100).toFixed(0)}%</div>
        <div className="space-y-1.5">
          {result.shap_contributors.map((c) => (
            <div key={c.feature} className="flex items-center gap-2">
              <div className="w-24 text-xs text-zinc-600 text-right font-mono">{c.feature}</div>
              <div className="flex-1 relative h-5">
                <div
                  className={`absolute top-0 h-full rounded ${barColour(c.direction)}`}
                  style={{ width: `${(Math.abs(c.shap_value) / maxShap) * 100}%` }}
                />
              </div>
              <div className="w-20 text-xs text-zinc-500 font-mono flex items-center gap-1">
                {c.direction === "increases_risk" ? (
                  <TrendingUp className="w-3 h-3 text-red-500" />
                ) : (
                  <TrendingDown className="w-3 h-3 text-green-500" />
                )}
                {c.shap_value > 0 ? "+" : ""}{c.shap_value.toFixed(4)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Guardrails */}
      <div>
        <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Guardrails</div>
        <div className="flex flex-wrap gap-2">
          {result.guardrails.map((g) => (
            <span
              key={g.name}
              className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                g.status === "pass"
                  ? "bg-green-50 text-green-700"
                  : "bg-red-50 text-red-700"
              }`}
            >
              {g.status === "pass" ? (
                <ShieldCheck className="w-3 h-3" />
              ) : (
                <ShieldAlert className="w-3 h-3" />
              )}
              {g.name}
              {g.detail && <span className="text-zinc-400 ml-1">({g.detail})</span>}
            </span>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-4 text-xs text-zinc-400">
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" /> {result.latency_ms}ms
        </span>
        <span>ID: {result.scoring_id}</span>
        {result.blocked && (
          <span className="text-red-600 font-semibold">BLOCKED</span>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function ScoreInterface({ solutionId }: { solutionId: string }) {
  const [tab, setTab] = useState<"score" | "probe">("score");
  const [loading, setLoading] = useState(false);
  const [scoreResult, setScoreResult] = useState<ScoreResult | null>(null);
  const [probeResult, setProbeResult] = useState<ProbeResult | null>(null);
  const [selectedProbe, setSelectedProbe] = useState("gender");

  // -- Score Tab --
  async function handleScore(profileKey: string) {
    setLoading(true);
    setScoreResult(null);

    const features = SAMPLE_PROFILES[profileKey].features;
    const result = await fetchScore(solutionId, features);

    if (result) {
      setScoreResult(result);
    } else {
      // Demo fallback
      await new Promise((r) => setTimeout(r, 800));
      setScoreResult(DEMO_SCORES[profileKey] || DEMO_SCORES.low_risk);
    }

    setLoading(false);
  }

  // -- Probe Tab --
  async function handleProbe() {
    setLoading(true);
    setProbeResult(null);

    const baseProfile = SAMPLE_PROFILES.low_risk.features;
    const probeType = PROBE_TYPES[selectedProbe];
    const result = await fetchProbe(solutionId, baseProfile, probeType.variants, 0.02);

    if (result) {
      setProbeResult(result);
    } else {
      // Demo fallback
      await new Promise((r) => setTimeout(r, 800));
      setProbeResult(DEMO_PROBE);
    }

    setLoading(false);
  }

  return (
    <div className="flex-1 overflow-y-auto bg-zinc-50 px-8 py-6">
      {/* Tabs */}
      <div className="flex gap-1 bg-zinc-200 rounded-lg p-1 w-fit mb-6">
        <button
          onClick={() => setTab("score")}
          className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
            tab === "score" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-600 hover:text-zinc-900"
          }`}
        >
          <BarChart3 className="w-4 h-4 inline mr-1.5" />
          Score a Profile
        </button>
        <button
          onClick={() => setTab("probe")}
          className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
            tab === "probe" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-600 hover:text-zinc-900"
          }`}
        >
          <Users className="w-4 h-4 inline mr-1.5" />
          Discrimination Probe
        </button>
      </div>

      {/* Score Tab */}
      {tab === "score" && (
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-zinc-700 mb-3">Select a customer profile</h3>
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(SAMPLE_PROFILES).map(([key, profile]) => (
                <button
                  key={key}
                  onClick={() => handleScore(key)}
                  disabled={loading}
                  className="text-left p-4 bg-white border border-zinc-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all disabled:opacity-50"
                >
                  <div className="font-medium text-sm text-zinc-900">{profile.label}</div>
                  <div className="text-xs text-zinc-500 mt-1">{profile.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {loading && (
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <Loader2 className="w-4 h-4 animate-spin" /> Scoring...
            </div>
          )}

          {scoreResult && !loading && (
            <div className="bg-white border border-zinc-200 rounded-lg p-6">
              <ScoreResultCard result={scoreResult} />
            </div>
          )}
        </div>
      )}

      {/* Probe Tab */}
      {tab === "probe" && (
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-zinc-700 mb-2">
              Same credit behaviour, different demographics
            </h3>
            <p className="text-xs text-zinc-500 mb-4">
              Two customers with identical payment history and credit profile. The only difference is a protected attribute. If the model scores them differently, it has learned a bias.
            </p>
            <div className="flex items-center gap-3">
              <label className="text-sm text-zinc-600">Compare by:</label>
              <select
                value={selectedProbe}
                onChange={(e) => setSelectedProbe(e.target.value)}
                className="border border-zinc-300 rounded-md px-3 py-1.5 text-sm bg-white"
              >
                {Object.entries(PROBE_TYPES).map(([key, pt]) => (
                  <option key={key} value={key}>{pt.label}</option>
                ))}
              </select>
              <button
                onClick={handleProbe}
                disabled={loading}
                className="px-4 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Run Probe"}
              </button>
            </div>
          </div>

          {loading && (
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <Loader2 className="w-4 h-4 animate-spin" /> Running discrimination probe...
            </div>
          )}

          {probeResult && !loading && (
            <div className="space-y-4">
              {/* Verdict banner */}
              <div className={`p-4 rounded-lg border ${
                probeResult.discrimination_pass
                  ? "bg-green-50 border-green-200"
                  : "bg-red-50 border-red-200"
              }`}>
                <div className="flex items-center gap-2">
                  {probeResult.discrimination_pass ? (
                    <ShieldCheck className="w-5 h-5 text-green-600" />
                  ) : (
                    <ShieldAlert className="w-5 h-5 text-red-600" />
                  )}
                  <span className={`font-semibold text-sm ${
                    probeResult.discrimination_pass ? "text-green-800" : "text-red-800"
                  }`}>
                    {probeResult.discrimination_pass
                      ? "PASS — Scores within tolerance"
                      : "FAIL — Discrimination detected"}
                  </span>
                </div>
                <div className="text-xs mt-1 text-zinc-600">
                  Score difference: <span className="font-mono font-semibold">{probeResult.score_difference.toFixed(4)}</span>
                  {" "}(tolerance: {probeResult.tolerance})
                </div>
              </div>

              {/* Side-by-side results */}
              <div className="grid grid-cols-2 gap-4">
                {probeResult.results.map((result, i) => (
                  <div key={i} className="bg-white border border-zinc-200 rounded-lg p-5">
                    <div className="text-sm font-semibold text-zinc-700 mb-3">
                      {result.applicant_id}
                    </div>
                    <ScoreResultCard result={result} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
