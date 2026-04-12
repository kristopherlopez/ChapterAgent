"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/layout/Header";
import { solutions, sampleGeneratedCases } from "@/lib/data";
import type { GeneratedTestCase } from "@/lib/types";
import {
  Sparkles,
  ChevronDown,
  ChevronRight,
  ArrowRight,
  FileText,
  CheckCircle2,
} from "lucide-react";

const QUERY_TYPES = [
  "direct_factual",
  "comparative",
  "temporal",
  "aggregation",
  "causal",
  "boundary",
  "multi_hop",
  "out_of_scope",
  "ambiguous",
  "adversarial",
];

function QueryTypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    direct_factual: "bg-blue-50 text-blue-700 border-blue-200",
    comparative: "bg-violet-50 text-violet-700 border-violet-200",
    temporal: "bg-amber-50 text-amber-700 border-amber-200",
    aggregation: "bg-teal-50 text-teal-700 border-teal-200",
    causal: "bg-rose-50 text-rose-700 border-rose-200",
    boundary: "bg-orange-50 text-orange-700 border-orange-200",
    multi_hop: "bg-indigo-50 text-indigo-700 border-indigo-200",
    out_of_scope: "bg-zinc-100 text-zinc-600 border-zinc-200",
    ambiguous: "bg-yellow-50 text-yellow-700 border-yellow-200",
    adversarial: "bg-red-50 text-red-700 border-red-200",
  };
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${colors[type] || "bg-zinc-50 text-zinc-600 border-zinc-200"}`}
    >
      {type.replace(/_/g, " ")}
    </span>
  );
}

export default function GeneratorPage() {
  const router = useRouter();
  const [selectedSolution, setSelectedSolution] = useState("cba-annual-report-qa");
  const [numCases, setNumCases] = useState(10);
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set(QUERY_TYPES));
  const [generated, setGenerated] = useState<GeneratedTestCase[] | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [expandedCase, setExpandedCase] = useState<string | null>(null);

  function toggleType(type: string) {
    const next = new Set(selectedTypes);
    if (next.has(type)) {
      next.delete(type);
    } else {
      next.add(type);
    }
    setSelectedTypes(next);
  }

  function handleGenerate() {
    setIsGenerating(true);
    // Simulate generation delay
    setTimeout(() => {
      const filtered = sampleGeneratedCases.filter((c) =>
        selectedTypes.has(c.queryType),
      );
      setGenerated(filtered.slice(0, numCases));
      setIsGenerating(false);
    }, 1200);
  }

  function handleSendToValidation() {
    router.push(`/catalog/validation?solution=${selectedSolution}`);
  }

  const typeDistribution = generated
    ? Object.entries(
        generated.reduce(
          (acc, c) => {
            acc[c.queryType] = (acc[c.queryType] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>,
        ),
      )
    : [];

  return (
    <div>
      <Header
        title="Golden Dataset Generator"
        subtitle="Generate draft test triples from a solution's corpus"
      />
      <div className="px-8 py-6 space-y-6">
        {/* Configuration form */}
        <div className="bg-white border border-zinc-200 rounded-lg p-6 space-y-5">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-5 h-5 text-amber-500" />
            <h3 className="text-sm font-semibold text-zinc-900">
              Generation Configuration
            </h3>
          </div>

          {/* Solution selector */}
          <div>
            <label className="block text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1.5">
              Solution
            </label>
            <select
              value={selectedSolution}
              onChange={(e) => setSelectedSolution(e.target.value)}
              className="w-full max-w-md px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
            >
              {solutions.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.riskTier})
                </option>
              ))}
            </select>
          </div>

          {/* Number of cases */}
          <div>
            <label className="block text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1.5">
              Number of Test Cases
            </label>
            <input
              type="number"
              min={1}
              max={50}
              value={numCases}
              onChange={(e) => setNumCases(Math.min(50, Math.max(1, parseInt(e.target.value) || 1)))}
              className="w-32 px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
            />
          </div>

          {/* Query types */}
          <div>
            <label className="block text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">
              Query Types
            </label>
            <div className="flex flex-wrap gap-2">
              {QUERY_TYPES.map((type) => (
                <button
                  key={type}
                  onClick={() => toggleType(type)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium border transition-colors ${
                    selectedTypes.has(type)
                      ? "bg-zinc-900 text-white border-zinc-900"
                      : "bg-white text-zinc-500 border-zinc-200 hover:border-zinc-300"
                  }`}
                >
                  {type.replace(/_/g, " ")}
                </button>
              ))}
            </div>
          </div>

          {/* Generate button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || selectedTypes.size === 0}
            className="inline-flex items-center gap-2 px-4 py-2 bg-zinc-900 text-white rounded-md text-sm font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Test Cases
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {generated && (
          <>
            {/* Stats row */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white border border-zinc-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-50 rounded-lg">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-semibold text-zinc-900">
                      {generated.length}
                    </p>
                    <p className="text-xs text-zinc-500">Cases Generated</p>
                  </div>
                </div>
              </div>
              <div className="bg-white border border-zinc-200 rounded-lg p-4">
                <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-2">
                  Type Distribution
                </p>
                <div className="flex flex-wrap gap-2">
                  {typeDistribution.map(([type, count]) => (
                    <span
                      key={type}
                      className="inline-flex items-center gap-1 text-xs text-zinc-600"
                    >
                      <QueryTypeBadge type={type} />
                      <span className="text-zinc-400">{count as number}</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Results table */}
            <div className="bg-white border border-zinc-200 rounded-lg">
              <div className="grid grid-cols-[80px_120px_1fr_200px_32px] items-center gap-4 px-6 py-4 border-b border-zinc-100">
                <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                  Case ID
                </p>
                <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                  Type
                </p>
                <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                  Question
                </p>
                <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                  Metrics
                </p>
                <span />
              </div>

              {generated.map((tc) => {
                const isExpanded = expandedCase === tc.caseId;
                return (
                  <div
                    key={tc.caseId}
                    className="border-b border-zinc-100 last:border-b-0"
                  >
                    <button
                      onClick={() =>
                        setExpandedCase(isExpanded ? null : tc.caseId)
                      }
                      className="w-full grid grid-cols-[80px_120px_1fr_200px_32px] items-center gap-4 px-6 py-4 hover:bg-zinc-50 transition-colors text-left"
                    >
                      <p className="text-xs font-mono text-zinc-500">
                        {tc.caseId}
                      </p>
                      <QueryTypeBadge type={tc.queryType} />
                      <p className="text-sm text-zinc-900 truncate">
                        {tc.question}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {tc.keyMetrics.slice(0, 2).map((m) => (
                          <span
                            key={m}
                            className="text-[10px] px-1.5 py-0.5 bg-zinc-100 rounded text-zinc-500 font-mono"
                          >
                            {m}
                          </span>
                        ))}
                        {tc.keyMetrics.length > 2 && (
                          <span className="text-[10px] text-zinc-400">
                            +{tc.keyMetrics.length - 2}
                          </span>
                        )}
                      </div>
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-zinc-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-zinc-400" />
                      )}
                    </button>

                    {isExpanded && (
                      <div className="px-6 pb-4">
                        <div className="bg-zinc-50 rounded-lg p-4 space-y-3">
                          <div>
                            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                              Question
                            </p>
                            <p className="text-sm text-zinc-900">
                              {tc.question}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                              Expected Answer
                            </p>
                            <p className="text-sm text-zinc-700">
                              {tc.expectedAnswer}
                            </p>
                          </div>
                          <div className="grid grid-cols-3 gap-4">
                            <div>
                              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                                Behaviour
                              </p>
                              <p className="text-xs text-zinc-600 font-mono">
                                {tc.expectedBehaviour}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                                Grounding
                              </p>
                              <p className="text-xs text-zinc-600 font-mono">
                                {tc.expectedGrounding}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                                Scope Level
                              </p>
                              <p className="text-xs text-zinc-600 font-mono">
                                {tc.scopeLevel}
                              </p>
                            </div>
                          </div>
                          {tc.expectedCitations.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                                Citations
                              </p>
                              <div className="space-y-1">
                                {tc.expectedCitations.map((c, i) => (
                                  <div
                                    key={i}
                                    className="flex items-center gap-2 text-xs text-zinc-600"
                                  >
                                    <FileText className="w-3 h-3 text-zinc-400" />
                                    {c.document}, p.{c.page} &mdash;{" "}
                                    {c.section}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Send to validation */}
            <div className="flex justify-end">
              <button
                onClick={handleSendToValidation}
                className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-md text-sm font-medium hover:bg-emerald-700 transition-colors"
              >
                Send to Validation
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </>
        )}

        {/* Explainer */}
        <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-2">
            How the Generator Works
          </h3>
          <p className="text-sm text-zinc-600">
            The generator ingests a squad&apos;s source documents, identifies key passages, and
            synthesises question-answer-context triples across configurable query types. The output
            is a draft golden dataset &mdash; not production-ready until SMEs review and approve
            each case through the{" "}
            <span className="font-medium text-zinc-900">Validation UI</span>. The Chapter provides
            the generator; squads bring their documents and their SMEs.
          </p>
        </div>
      </div>
    </div>
  );
}
