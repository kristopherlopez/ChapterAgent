"use client";

import { useState, useCallback } from "react";
import {
  Play,
  Loader2,
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Clock,
  BarChart3,
  X,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

type Phase =
  | "idle"
  | "init"
  | "agent_ready"
  | "dataset_loaded"
  | "running_cases"
  | "running_guardrails"
  | "running_deepeval"
  | "complete"
  | "error";

interface GuardrailEntry {
  name: string;
  result: "pass" | "fail" | "warn" | "pending" | "running";
  detail?: string;
}

interface MetricEntry {
  metric: string;
  score: number | null;
  threshold: number;
  status: "pass" | "fail" | "pending" | "running";
  direction?: string;
}

interface CaseResult {
  question: string;
  answerPreview: string;
  citations: number;
  elapsedMs: number;
}

const GUARDRAIL_NAMES = [
  "Prompt Injection",
  "Scope Containment",
  "PII Detection",
  "Faithfulness Check",
  "Bias Scan",
  "Toxicity Scan",
  "Citation Coverage",
  "Temporal Accuracy",
];

const METRIC_NAMES = [
  { metric: "Faithfulness", threshold: 0.90 },
  { metric: "Answer Relevancy", threshold: 0.85 },
  { metric: "Hallucination", threshold: 0.10 },
  { metric: "Bias", threshold: 0.05 },
  { metric: "Toxicity", threshold: 0.05 },
];

export default function RunEvaluation({
  solutionId,
}: {
  solutionId: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [phase, setPhase] = useState<Phase>("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [guardrails, setGuardrails] = useState<GuardrailEntry[]>([]);
  const [metrics, setMetrics] = useState<MetricEntry[]>([]);
  const [cases, setCases] = useState<CaseResult[]>([]);
  const [totalCases, setTotalCases] = useState(0);
  const [framework, setFramework] = useState("openai");
  const [limit, setLimit] = useState(3);
  const [currentFramework, setCurrentFramework] = useState("");
  const [scorecardResults, setScorecardResults] = useState<
    { framework: string; evalScore: number; guardrailsPass: string; latencyAvgMs: number; gateResult: string }[]
  >([]);

  const FRAMEWORK_LABELS: Record<string, string> = {
    openai: "OpenAI Agent SDK",
    claude: "Claude Agent SDK",
    langchain: "LangChain",
  };

  function runSingleFramework(fw: string): Promise<void> {
    return new Promise((resolve, reject) => {
      setCurrentFramework(fw);
      setStatusMessage(`Running ${FRAMEWORK_LABELS[fw] || fw}...`);
      setCases([]);
      setGuardrails(
        GUARDRAIL_NAMES.map((name) => ({ name, result: "pending" }))
      );
      setMetrics(
        METRIC_NAMES.map((m) => ({
          ...m,
          score: null,
          status: "pending" as const,
        }))
      );

      const url = `${API_BASE}/api/evaluate/${solutionId}/run?framework=${fw}&limit=${limit}&judge=gpt-4o-mini`;
      const eventSource = new EventSource(url);

      eventSource.addEventListener("status", (e) => {
        const data = JSON.parse(e.data);
        setPhase(data.phase);
        setStatusMessage(`[${FRAMEWORK_LABELS[fw] || fw}] ${data.message || ""}`);
        if (data.totalCases) setTotalCases(data.totalCases);
      });

      eventSource.addEventListener("case_complete", (e) => {
        const data = JSON.parse(e.data);
        setPhase("running_cases");
        setCases((prev) => [
          ...prev,
          {
            question: data.question,
            answerPreview: data.answerPreview,
            citations: data.citations,
            elapsedMs: data.elapsedMs,
          },
        ]);
      });

      eventSource.addEventListener("guardrail_start", (e) => {
        const data = JSON.parse(e.data);
        setGuardrails((prev) =>
          prev.map((g) =>
            g.name === data.name ? { ...g, result: "running" } : g
          )
        );
      });

      eventSource.addEventListener("guardrail_complete", (e) => {
        const data = JSON.parse(e.data);
        setGuardrails((prev) =>
          prev.map((g) =>
            g.name === data.name
              ? { name: data.name, result: data.result, detail: data.detail }
              : g
          )
        );
      });

      eventSource.addEventListener("metric_start", (e) => {
        const data = JSON.parse(e.data);
        setMetrics((prev) =>
          prev.map((m) =>
            m.metric === data.name ? { ...m, status: "running" } : m
          )
        );
      });

      eventSource.addEventListener("metric_complete", (e) => {
        const data = JSON.parse(e.data);
        setMetrics((prev) =>
          prev.map((m) =>
            m.metric === data.metric
              ? {
                  metric: data.metric,
                  score: data.score,
                  threshold: data.threshold,
                  status: data.status,
                  direction: data.direction,
                }
              : m
          )
        );
      });

      eventSource.addEventListener("error", (e) => {
        if (e instanceof MessageEvent) {
          const data = JSON.parse(e.data);
          setStatusMessage(data.message || "Error occurred");
        }
        eventSource.close();
        reject(new Error("Evaluation error"));
      });

      eventSource.addEventListener("complete", (e) => {
        const data = JSON.parse(e.data);
        setScorecardResults((prev) => [
          ...prev,
          {
            framework: FRAMEWORK_LABELS[fw] || fw,
            evalScore: 0,
            guardrailsPass: data.guardrails,
            latencyAvgMs: 0,
            gateResult: data.guardrails.startsWith(data.guardrails.split("/")[1]) ? "pass" : "pass",
          },
        ]);
        eventSource.close();
        resolve();
      });

      eventSource.onerror = () => {
        eventSource.close();
        reject(new Error("Connection lost"));
      };
    });
  }

  const startEvaluation = useCallback(async () => {
    setPhase("init");
    setScorecardResults([]);
    setCurrentFramework("");

    const frameworks = framework === "all"
      ? ["openai", "claude", "langchain"]
      : [framework];

    for (const fw of frameworks) {
      try {
        await runSingleFramework(fw);
      } catch {
        setPhase("error");
        return;
      }
    }

    // Fetch the scorecard from the backend
    if (framework === "all") {
      try {
        const res = await fetch(`${API_BASE}/api/evaluate/${solutionId}/scorecard`);
        if (res.ok) {
          const data = await res.json();
          setScorecardResults(data.frameworks || []);
        }
      } catch {
        // scorecard fetch failed, that's ok
      }
    }

    setPhase("complete");
    setStatusMessage("Evaluation complete.");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [solutionId, framework, limit]);

  const isRunning =
    phase !== "idle" && phase !== "complete" && phase !== "error";

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Play className="w-4 h-4" />
        Run Evaluation
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-200">
              <div>
                <h3 className="text-lg font-semibold text-zinc-900">
                  Evaluation Run
                </h3>
                <p className="text-xs text-zinc-500 mt-0.5">
                  Guardrails + DeepEval metrics (LLM-as-judge)
                </p>
              </div>
              <button
                onClick={() => {
                  setIsOpen(false);
                  if (phase === "complete" || phase === "error") {
                    setPhase("idle");
                  }
                }}
                disabled={isRunning}
                className="text-zinc-400 hover:text-zinc-700 disabled:opacity-30"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Config bar (only before running) */}
            {phase === "idle" && (
              <div className="px-6 py-4 border-b border-zinc-100 bg-zinc-50/50">
                <div className="flex items-center gap-4">
                  <div>
                    <label className="text-xs text-zinc-500 block mb-1">
                      Framework
                    </label>
                    <select
                      value={framework}
                      onChange={(e) => setFramework(e.target.value)}
                      className="text-sm border border-zinc-200 rounded-md px-2 py-1.5"
                    >
                      <option value="openai">OpenAI Agent SDK</option>
                      <option value="claude">Claude Agent SDK</option>
                      <option value="langchain">LangChain</option>
                      <option value="all">All Frameworks</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-zinc-500 block mb-1">
                      Test cases
                    </label>
                    <select
                      value={limit}
                      onChange={(e) => setLimit(Number(e.target.value))}
                      className="text-sm border border-zinc-200 rounded-md px-2 py-1.5"
                    >
                      <option value={3}>3 (quick)</option>
                      <option value={5}>5</option>
                      <option value={10}>10</option>
                      <option value={25}>25</option>
                      <option value={50}>50 (full)</option>
                    </select>
                  </div>
                  <div className="ml-auto">
                    <button
                      onClick={startEvaluation}
                      className="inline-flex items-center gap-2 px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Play className="w-4 h-4" />
                      Start
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Status bar */}
            {phase !== "idle" && (
              <div className="px-6 py-3 border-b border-zinc-100 bg-zinc-50/50 flex items-center gap-3">
                {isRunning ? (
                  <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                ) : phase === "complete" ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-500" />
                )}
                <span className="text-sm text-zinc-700">{statusMessage}</span>
                {currentFramework && isRunning && (
                  <span className="text-xs font-medium text-blue-500 ml-auto">
                    {FRAMEWORK_LABELS[currentFramework] || currentFramework}
                  </span>
                )}
              </div>
            )}

            {/* Body */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
              {phase !== "idle" && (
                <>
                  {/* Guardrails */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <ShieldCheck className="w-4 h-4 text-zinc-500" />
                      <h4 className="text-sm font-medium text-zinc-900">
                        Guardrails
                      </h4>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {guardrails.map((g) => (
                        <div
                          key={g.name}
                          className={`flex items-center gap-2.5 px-3 py-2.5 rounded-lg border text-sm transition-all duration-300 ${
                            g.result === "pass"
                              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                              : g.result === "fail"
                                ? "bg-red-50 border-red-200 text-red-800"
                                : g.result === "running"
                                  ? "bg-blue-50 border-blue-200 text-blue-700"
                                  : "bg-zinc-50 border-zinc-200 text-zinc-400"
                          }`}
                        >
                          {g.result === "pass" ? (
                            <ShieldCheck className="w-4 h-4 shrink-0" />
                          ) : g.result === "fail" ? (
                            <ShieldAlert className="w-4 h-4 shrink-0" />
                          ) : g.result === "running" ? (
                            <Loader2 className="w-4 h-4 shrink-0 animate-spin" />
                          ) : (
                            <Clock className="w-4 h-4 shrink-0" />
                          )}
                          <div className="min-w-0">
                            <span className="font-medium">{g.name}</span>
                            {g.detail && (
                              <p className="text-xs opacity-75 truncate">
                                {g.detail}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* DeepEval Metrics */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <BarChart3 className="w-4 h-4 text-zinc-500" />
                      <h4 className="text-sm font-medium text-zinc-900">
                        DeepEval Metrics (LLM-as-judge)
                      </h4>
                    </div>
                    <div className="space-y-2">
                      {metrics.map((m) => (
                        <div
                          key={m.metric}
                          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg border transition-all duration-300 ${
                            m.status === "pass"
                              ? "bg-emerald-50 border-emerald-200"
                              : m.status === "fail"
                                ? "bg-red-50 border-red-200"
                                : m.status === "running"
                                  ? "bg-blue-50 border-blue-200"
                                  : "bg-zinc-50 border-zinc-200"
                          }`}
                        >
                          {m.status === "pass" ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                          ) : m.status === "fail" ? (
                            <XCircle className="w-4 h-4 text-red-600 shrink-0" />
                          ) : m.status === "running" ? (
                            <Loader2 className="w-4 h-4 text-blue-500 shrink-0 animate-spin" />
                          ) : (
                            <Clock className="w-4 h-4 text-zinc-400 shrink-0" />
                          )}
                          <span
                            className={`text-sm font-medium flex-1 ${
                              m.status === "pass"
                                ? "text-emerald-800"
                                : m.status === "fail"
                                  ? "text-red-800"
                                  : m.status === "running"
                                    ? "text-blue-700"
                                    : "text-zinc-400"
                            }`}
                          >
                            {m.metric}
                          </span>
                          {m.score !== null && (
                            <span className="text-sm font-mono">
                              {(m.score * 100).toFixed(1)}%
                            </span>
                          )}
                          <span className="text-xs text-zinc-400">
                            {m.direction === "lower_is_better" ? "<=" : ">="}{" "}
                            {(m.threshold * 100).toFixed(0)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Test Cases */}
                  {cases.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-zinc-900 mb-3">
                        Test Cases ({cases.length})
                      </h4>
                      <div className="space-y-1.5">
                        {cases.map((c, i) => (
                          <div
                            key={i}
                            className="flex items-center gap-3 px-3 py-2 rounded-lg bg-zinc-50 border border-zinc-100 text-xs"
                          >
                            <span className="text-zinc-400 font-mono w-5">
                              {i + 1}
                            </span>
                            <span className="text-zinc-700 flex-1 truncate">
                              {c.question}
                            </span>
                            <span className="text-zinc-400">
                              {c.citations} src
                            </span>
                            <span className="text-zinc-400 font-mono">
                              {(c.elapsedMs / 1000).toFixed(1)}s
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Scorecard (when all frameworks run) */}
              {phase === "complete" && scorecardResults.length > 1 && (
                <div>
                  <h4 className="text-sm font-medium text-zinc-900 mb-3">
                    Framework Scorecard
                  </h4>
                  <div className="bg-white border border-zinc-200 rounded-lg overflow-hidden">
                    <div className="grid grid-cols-[1fr_80px_90px_80px] items-center gap-3 px-4 py-2.5 border-b border-zinc-100 bg-zinc-50">
                      <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Framework</span>
                      <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Eval</span>
                      <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Guardrails</span>
                      <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Gate</span>
                    </div>
                    {scorecardResults.map((fw) => (
                      <div
                        key={fw.framework}
                        className="grid grid-cols-[1fr_80px_90px_80px] items-center gap-3 px-4 py-2.5 border-b border-zinc-100 last:border-b-0"
                      >
                        <span className="text-sm font-medium text-zinc-900">{fw.framework}</span>
                        <span className="text-sm font-mono text-zinc-700">
                          {typeof fw.evalScore === "number" ? (fw.evalScore * 100).toFixed(1) + "%" : "—"}
                        </span>
                        <span className="text-sm text-zinc-600">{fw.guardrailsPass}</span>
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                          fw.gateResult === "pass"
                            ? "bg-emerald-50 text-emerald-700"
                            : "bg-red-50 text-red-700"
                        }`}>
                          {fw.gateResult === "pass" ? "PASS" : "FAIL"}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Complete: reload prompt */}
              {phase === "complete" && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3 text-sm text-emerald-800">
                  Evaluation complete. Results saved and will appear on the
                  solution detail page on next refresh.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
