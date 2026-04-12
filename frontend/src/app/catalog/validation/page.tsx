"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import Header from "@/components/layout/Header";
import { solutions, sampleValidationDataset } from "@/lib/data";
import type { ReviewStatus, ValidationTestCase } from "@/lib/types";
import {
  CheckCircle2,
  XCircle,
  Pencil,
  ChevronDown,
  ChevronRight,
  FileText,
  ShieldCheck,
  Clock,
  AlertTriangle,
} from "lucide-react";

function ReviewBadge({ status }: { status: ReviewStatus }) {
  switch (status) {
    case "approved":
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          <CheckCircle2 className="w-3 h-3" />
          Approved
        </span>
      );
    case "rejected":
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">
          <XCircle className="w-3 h-3" />
          Rejected
        </span>
      );
    case "edited":
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
          <Pencil className="w-3 h-3" />
          Edited
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-zinc-100 text-zinc-500 border border-zinc-200">
          <Clock className="w-3 h-3" />
          Pending
        </span>
      );
  }
}

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

export default function ValidationPage() {
  const searchParams = useSearchParams();
  const solutionParam = searchParams.get("solution") || "cba-annual-report-qa";

  const [selectedSolution, setSelectedSolution] = useState(solutionParam);
  const [testCases, setTestCases] = useState<ValidationTestCase[]>(
    sampleValidationDataset.testCases,
  );
  const [expandedCase, setExpandedCase] = useState<string | null>(null);
  const [signedOff, setSignedOff] = useState(false);

  const totalCases = testCases.length;
  const reviewed = testCases.filter((c) => c.reviewStatus !== "pending").length;
  const approved = testCases.filter((c) => c.reviewStatus === "approved" || c.reviewStatus === "edited").length;
  const rejected = testCases.filter((c) => c.reviewStatus === "rejected").length;
  const pending = testCases.filter((c) => c.reviewStatus === "pending").length;
  const progressPct = totalCases > 0 ? Math.round((reviewed / totalCases) * 100) : 0;
  const allReviewed = pending === 0;

  function updateCase(caseId: string, status: ReviewStatus, notes?: string) {
    setTestCases((prev) =>
      prev.map((tc) =>
        tc.caseId === caseId
          ? {
              ...tc,
              reviewStatus: status,
              reviewedBy: "Kristopher Lopez",
              reviewedAt: new Date().toISOString(),
              reviewNotes: notes || tc.reviewNotes,
            }
          : tc,
      ),
    );
  }

  function handleSignOff() {
    setSignedOff(true);
  }

  return (
    <div>
      <Header
        title="Golden Dataset Validation"
        subtitle="SME review and sign-off for golden dataset test cases"
      />
      <div className="px-8 py-6 space-y-6">
        {/* Solution selector */}
        <div className="flex items-center gap-4">
          <label className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
            Solution
          </label>
          <select
            value={selectedSolution}
            onChange={(e) => setSelectedSolution(e.target.value)}
            className="px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent"
          >
            {solutions.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        {/* Progress section */}
        <div className="bg-white border border-zinc-200 rounded-lg p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-zinc-900">
                Review Progress
              </h3>
              <p className="text-xs text-zinc-500 mt-0.5">
                {sampleValidationDataset.solutionName} &mdash; v{sampleValidationDataset.version}
              </p>
            </div>
            {signedOff ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md text-sm font-medium">
                <ShieldCheck className="w-4 h-4" />
                Signed Off
              </span>
            ) : (
              <button
                onClick={handleSignOff}
                disabled={!allReviewed}
                className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-md text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title={
                  allReviewed
                    ? "Sign off this golden dataset"
                    : `${pending} cases still pending review`
                }
              >
                <ShieldCheck className="w-4 h-4" />
                Sign Off Dataset
              </button>
            )}
          </div>

          {/* Progress bar */}
          <div>
            <div className="flex items-center justify-between text-xs text-zinc-500 mb-1.5">
              <span>
                {reviewed} of {totalCases} reviewed ({progressPct}%)
              </span>
              <span>
                {approved} approved &middot; {rejected} rejected &middot;{" "}
                {pending} pending
              </span>
            </div>
            <div className="h-2 bg-zinc-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-300"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>

          {/* Stat cards */}
          <div className="grid grid-cols-4 gap-3">
            <div className="text-center p-3 bg-zinc-50 rounded-lg">
              <p className="text-lg font-semibold text-zinc-900">{totalCases}</p>
              <p className="text-xs text-zinc-500">Total</p>
            </div>
            <div className="text-center p-3 bg-emerald-50 rounded-lg">
              <p className="text-lg font-semibold text-emerald-700">{approved}</p>
              <p className="text-xs text-emerald-600">Approved</p>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <p className="text-lg font-semibold text-red-700">{rejected}</p>
              <p className="text-xs text-red-600">Rejected</p>
            </div>
            <div className="text-center p-3 bg-zinc-100 rounded-lg">
              <p className="text-lg font-semibold text-zinc-600">{pending}</p>
              <p className="text-xs text-zinc-500">Pending</p>
            </div>
          </div>
        </div>

        {/* Test cases table */}
        <div className="bg-white border border-zinc-200 rounded-lg">
          <div className="grid grid-cols-[80px_100px_1fr_200px_100px_32px] items-center gap-4 px-6 py-4 border-b border-zinc-100">
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
              Expected Answer
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
              Status
            </p>
            <span />
          </div>

          {testCases.map((tc) => {
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
                  className="w-full grid grid-cols-[80px_100px_1fr_200px_100px_32px] items-center gap-4 px-6 py-4 hover:bg-zinc-50 transition-colors text-left"
                >
                  <p className="text-xs font-mono text-zinc-500">
                    {tc.caseId}
                  </p>
                  <QueryTypeBadge type={tc.queryType} />
                  <p className="text-sm text-zinc-900 truncate">
                    {tc.question}
                  </p>
                  <p className="text-xs text-zinc-500 truncate">
                    {tc.expectedAnswer}
                  </p>
                  <ReviewBadge status={tc.reviewStatus} />
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-zinc-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-zinc-400" />
                  )}
                </button>

                {isExpanded && (
                  <div className="px-6 pb-4">
                    <div className="bg-zinc-50 rounded-lg p-4 space-y-4">
                      {/* Question */}
                      <div>
                        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                          Question
                        </p>
                        <p className="text-sm text-zinc-900">{tc.question}</p>
                      </div>

                      {/* Expected answer */}
                      <div>
                        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                          Expected Answer
                        </p>
                        <p className="text-sm text-zinc-700">
                          {tc.expectedAnswer}
                        </p>
                      </div>

                      {/* Metadata */}
                      <div className="grid grid-cols-4 gap-4">
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
                        <div>
                          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                            Key Metrics
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {tc.keyMetrics.map((m) => (
                              <span
                                key={m}
                                className="text-[10px] px-1.5 py-0.5 bg-white rounded border border-zinc-200 text-zinc-500 font-mono"
                              >
                                {m}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Citations */}
                      {tc.expectedCitations.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                            Expected Citations
                          </p>
                          <div className="space-y-1">
                            {tc.expectedCitations.map((c, i) => (
                              <div
                                key={i}
                                className="flex items-center gap-2 text-xs text-zinc-600"
                              >
                                <FileText className="w-3 h-3 text-zinc-400" />
                                {c.document}, p.{c.page} &mdash; {c.section}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Review notes */}
                      {tc.reviewNotes && (
                        <div className="pt-2 border-t border-zinc-200">
                          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                            Review Notes
                          </p>
                          <div className="flex items-start gap-2">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
                            <p className="text-xs text-zinc-600">
                              {tc.reviewNotes}
                            </p>
                          </div>
                          {tc.reviewedBy && (
                            <p className="text-[10px] text-zinc-400 mt-1">
                              &mdash; {tc.reviewedBy},{" "}
                              {tc.reviewedAt
                                ? new Date(tc.reviewedAt).toLocaleDateString()
                                : ""}
                            </p>
                          )}
                        </div>
                      )}

                      {/* Action buttons */}
                      {!signedOff && (
                        <div className="flex items-center gap-2 pt-2 border-t border-zinc-200">
                          <button
                            onClick={() => updateCase(tc.caseId, "approved")}
                            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                              tc.reviewStatus === "approved"
                                ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                                : "bg-white text-emerald-700 border border-zinc-200 hover:bg-emerald-50 hover:border-emerald-200"
                            }`}
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Approve
                          </button>
                          <button
                            onClick={() => updateCase(tc.caseId, "rejected")}
                            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                              tc.reviewStatus === "rejected"
                                ? "bg-red-100 text-red-800 border border-red-300"
                                : "bg-white text-red-700 border border-zinc-200 hover:bg-red-50 hover:border-red-200"
                            }`}
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            Reject
                          </button>
                          <button
                            onClick={() => updateCase(tc.caseId, "edited")}
                            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                              tc.reviewStatus === "edited"
                                ? "bg-amber-100 text-amber-800 border border-amber-300"
                                : "bg-white text-amber-700 border border-zinc-200 hover:bg-amber-50 hover:border-amber-200"
                            }`}
                          >
                            <Pencil className="w-3.5 h-3.5" />
                            Edit
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Explainer */}
        <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-2">
            How Validation Works
          </h3>
          <p className="text-sm text-zinc-600">
            The Chapter provides this validation UI; squads bring their SMEs. Each test case must be
            reviewed and either approved, rejected, or edited before the dataset can be signed off.
            Sign-off produces a compliance artifact (AI-GOV-009) that the deployment gate checks
            before allowing production promotion. Rejected cases are sent back to the generator for
            revision. The goal is a curated, domain-expert-approved golden dataset that the
            evaluation harness can run against.
          </p>
        </div>
      </div>
    </div>
  );
}
