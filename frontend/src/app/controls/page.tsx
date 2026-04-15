"use client";

import { useState } from "react";
import Header from "@/components/layout/Header";
import {
  controls,
  runtimeGuardrails,
  riskControlMappings,
  controlThresholds,
  incidentResponses,
  regulatoryRequirements,
  aiGovPolicies,
} from "@/lib/data";
import type { EnforcementLayer, ControlType, ResidualRisk } from "@/lib/types";

const tabs = [
  { id: "controls", label: "Controls" },
  { id: "risks", label: "Risk Mapping" },
  { id: "regulatory", label: "Regulatory" },
  { id: "thresholds", label: "Thresholds" },
] as const;

type TabId = (typeof tabs)[number]["id"];

function LayerBadge({ layer }: { layer: EnforcementLayer }) {
  const styles: Record<EnforcementLayer, string> = {
    "deployment-gate": "bg-blue-100 text-blue-800 border border-blue-200",
    production: "bg-purple-100 text-purple-800 border border-purple-200",
    "deployment-gate+production":
      "bg-indigo-100 text-indigo-800 border border-indigo-200",
  };
  const labels: Record<EnforcementLayer, string> = {
    "deployment-gate": "Gate",
    production: "Runtime",
    "deployment-gate+production": "Gate + Runtime",
  };
  return (
    <span
      className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${styles[layer]}`}
    >
      {labels[layer]}
    </span>
  );
}

function TypeBadge({ type }: { type: ControlType }) {
  const styles: Record<ControlType, string> = {
    preventive: "bg-emerald-100 text-emerald-800 border border-emerald-200",
    detective: "bg-amber-100 text-amber-800 border border-amber-200",
    "preventive+detective":
      "bg-teal-100 text-teal-800 border border-teal-200",
  };
  const labels: Record<ControlType, string> = {
    preventive: "Preventive",
    detective: "Detective",
    "preventive+detective": "Prev + Det",
  };
  return (
    <span
      className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${styles[type]}`}
    >
      {labels[type]}
    </span>
  );
}

function RiskBadge({ level }: { level: ResidualRisk }) {
  const styles: Record<ResidualRisk, string> = {
    "very-low": "bg-emerald-100 text-emerald-800 border border-emerald-200",
    low: "bg-blue-100 text-blue-800 border border-blue-200",
    medium: "bg-amber-100 text-amber-800 border border-amber-200",
  };
  const labels: Record<ResidualRisk, string> = {
    "very-low": "Very Low",
    low: "Low",
    medium: "Medium",
  };
  return (
    <span
      className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${styles[level]}`}
    >
      {labels[level]}
    </span>
  );
}

function ControlIdBadge({ id }: { id: string }) {
  return (
    <span
      title={aiGovPolicies[id] ?? id}
      className="inline-flex px-1.5 py-0.5 rounded text-[11px] font-mono font-medium bg-zinc-100 text-zinc-600 border border-zinc-200"
    >
      {id}
    </span>
  );
}

function RegBadge({ reg }: { reg: string }) {
  return (
    <span className="inline-flex px-1.5 py-0.5 rounded text-[11px] font-medium bg-zinc-100 text-zinc-500 border border-zinc-200">
      {reg}
    </span>
  );
}

// --- Tab: Controls Index ---

function ControlsTab() {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      <div className="bg-white border border-zinc-200 rounded-lg">
        {/* Header */}
        <div className="grid grid-cols-[100px_140px_1fr_120px_100px_0.6fr] items-center gap-4 px-6 py-3 border-b border-zinc-100">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Control
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Name
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Description
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
            Layer
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
            Type
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Risks
          </p>
        </div>

        {/* Rows */}
        {controls.map((ctrl) => {
          const isExpanded = expandedId === ctrl.id;
          const guardrails = runtimeGuardrails.filter(
            (g) => g.controlId === ctrl.id
          );
          const incidents = incidentResponses.filter(
            (i) => i.controlId === ctrl.id
          );

          return (
            <div key={ctrl.id} className="border-b border-zinc-100 last:border-b-0">
              <button
                onClick={() =>
                  setExpandedId(isExpanded ? null : ctrl.id)
                }
                className="w-full grid grid-cols-[100px_140px_1fr_120px_100px_0.6fr] items-center gap-4 px-6 py-4 text-left hover:bg-zinc-50 transition-colors"
              >
                <span className="text-sm font-mono font-semibold text-zinc-900">
                  {ctrl.id.replace("AI-GOV-", "GOV-")}
                </span>
                <span className="text-sm font-medium text-zinc-900">
                  {ctrl.name}
                </span>
                <span className="text-sm text-zinc-600 truncate">
                  {ctrl.description}
                </span>
                <span className="flex justify-center">
                  <LayerBadge layer={ctrl.enforcementLayer} />
                </span>
                <span className="flex justify-center">
                  <TypeBadge type={ctrl.controlType} />
                </span>
                <span className="flex flex-wrap gap-1">
                  {ctrl.risksMitigated.map((r) => (
                    <span
                      key={r}
                      className="text-[11px] font-mono text-zinc-500"
                    >
                      {r}
                    </span>
                  ))}
                </span>
              </button>

              {/* Expanded detail */}
              {isExpanded && (
                <div className="px-6 pb-5 pt-1 bg-zinc-50 space-y-4">
                  <p className="text-sm text-zinc-700">
                    {ctrl.description}
                  </p>

                  <div className="flex flex-wrap gap-1.5">
                    <span className="text-xs text-zinc-400 font-medium mr-1">
                      Regulatory:
                    </span>
                    {ctrl.regulatoryAlignment.map((r) => (
                      <RegBadge key={r} reg={r} />
                    ))}
                  </div>

                  {/* Runtime guardrails for this control */}
                  {guardrails.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-2">
                        Runtime Guardrails
                      </p>
                      <div className="bg-white border border-zinc-200 rounded-md overflow-hidden">
                        <div className="grid grid-cols-[1fr_1fr_80px_1fr] gap-4 px-4 py-2 border-b border-zinc-100">
                          <span className="text-[11px] font-medium text-zinc-400 uppercase">
                            Guardrail
                          </span>
                          <span className="text-[11px] font-medium text-zinc-400 uppercase">
                            Implementation
                          </span>
                          <span className="text-[11px] font-medium text-zinc-400 uppercase text-right">
                            Latency
                          </span>
                          <span className="text-[11px] font-medium text-zinc-400 uppercase">
                            On Failure
                          </span>
                        </div>
                        {guardrails.map((g) => (
                          <div
                            key={g.name}
                            className="grid grid-cols-[1fr_1fr_80px_1fr] gap-4 px-4 py-2 border-b border-zinc-100 last:border-b-0"
                          >
                            <span className="text-sm text-zinc-900">
                              {g.name}
                            </span>
                            <span className="text-sm text-zinc-600">
                              {g.implementation}
                            </span>
                            <span className="text-sm text-zinc-500 text-right font-mono">
                              {g.latencyMs}ms
                            </span>
                            <span className="text-sm text-zinc-600">
                              {g.onFailure}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Incident response for this control */}
                  {incidents.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-2">
                        Incident Response
                      </p>
                      <div className="bg-white border border-zinc-200 rounded-md overflow-hidden">
                        <div className="grid grid-cols-[1fr_1fr_1fr] gap-4 px-4 py-2 border-b border-zinc-100">
                          <span className="text-[11px] font-medium text-zinc-400 uppercase">
                            Event
                          </span>
                          <span className="text-[11px] font-medium text-zinc-400 uppercase">
                            Response
                          </span>
                          <span className="text-[11px] font-medium text-zinc-400 uppercase">
                            Escalation
                          </span>
                        </div>
                        {incidents.map((inc) => (
                          <div
                            key={inc.event}
                            className="grid grid-cols-[1fr_1fr_1fr] gap-4 px-4 py-2 border-b border-zinc-100 last:border-b-0"
                          >
                            <span className="text-sm text-zinc-900">
                              {inc.event}
                            </span>
                            <span className="text-sm text-zinc-600">
                              {inc.automatedResponse}
                            </span>
                            <span className="text-sm text-zinc-600">
                              {inc.escalation}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-zinc-200 rounded-lg p-4">
          <p className="text-2xl font-semibold text-zinc-900">
            {controls.length}
          </p>
          <p className="text-xs text-zinc-500 mt-1">Automated Controls</p>
        </div>
        <div className="bg-white border border-zinc-200 rounded-lg p-4">
          <p className="text-2xl font-semibold text-zinc-900">
            {runtimeGuardrails.length}
          </p>
          <p className="text-xs text-zinc-500 mt-1">Runtime Guardrails</p>
        </div>
        <div className="bg-white border border-zinc-200 rounded-lg p-4">
          <p className="text-2xl font-semibold text-zinc-900">
            &lt; 200ms
          </p>
          <p className="text-xs text-zinc-500 mt-1">
            Total Runtime Latency Budget
          </p>
        </div>
      </div>
    </div>
  );
}

// --- Tab: Risk Mapping ---

function RisksTab() {
  return (
    <div className="bg-white border border-zinc-200 rounded-lg">
      <div className="grid grid-cols-[80px_1fr_0.75fr_100px] items-center gap-4 px-6 py-3 border-b border-zinc-100">
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
          Risk ID
        </p>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
          Risk
        </p>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
          Mitigating Controls
        </p>
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
          Residual
        </p>
      </div>

      {riskControlMappings.map((rm) => (
        <div
          key={rm.riskId}
          className="grid grid-cols-[80px_1fr_0.75fr_100px] items-center gap-4 px-6 py-3 border-b border-zinc-100 last:border-b-0"
        >
          <span className="text-sm font-mono font-medium text-zinc-900">
            {rm.riskId}
          </span>
          <span className="text-sm text-zinc-700">{rm.risk}</span>
          <div className="flex flex-wrap gap-1.5">
            {rm.controls.map((c) => (
              <ControlIdBadge key={c} id={c} />
            ))}
          </div>
          <span className="flex justify-center">
            <RiskBadge level={rm.residualRisk} />
          </span>
        </div>
      ))}
    </div>
  );
}

// --- Tab: Regulatory ---

function RegulatoryTab() {
  const frameworks = [
    ...new Set(regulatoryRequirements.map((r) => r.framework)),
  ];

  return (
    <div className="space-y-6">
      {frameworks.map((fw) => {
        const reqs = regulatoryRequirements.filter(
          (r) => r.framework === fw
        );
        return (
          <div key={fw}>
            <h3 className="text-sm font-semibold text-zinc-900 mb-3">
              {fw}
            </h3>
            <div className="bg-white border border-zinc-200 rounded-lg">
              <div className="grid grid-cols-[1fr_0.75fr_1fr] items-center gap-4 px-6 py-3 border-b border-zinc-100">
                <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                  Requirement
                </p>
                <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                  Controls
                </p>
                <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                  Evidence
                </p>
              </div>

              {reqs.map((req) => (
                <div
                  key={req.requirement}
                  className="grid grid-cols-[1fr_0.75fr_1fr] items-center gap-4 px-6 py-3 border-b border-zinc-100 last:border-b-0"
                >
                  <span className="text-sm text-zinc-700">
                    {req.requirement}
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {req.controls.length > 0 ? (
                      req.controls.map((c) => (
                        <ControlIdBadge key={c} id={c} />
                      ))
                    ) : (
                      <span className="text-[11px] text-amber-600 font-medium">
                        Gap
                      </span>
                    )}
                  </div>
                  <span className="text-sm text-zinc-600">
                    {req.evidence}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// --- Tab: Thresholds ---

function ThresholdsTab() {
  return (
    <div className="space-y-4">
      <div className="bg-white border border-zinc-200 rounded-lg">
        <div className="grid grid-cols-[100px_1fr_120px_120px_120px] items-center gap-4 px-6 py-3 border-b border-zinc-100">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Control
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Metric
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
            Experimental
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
            Prod Internal
          </p>
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
            Prod Customer
          </p>
        </div>

        {controlThresholds.map((ct) => (
          <div
            key={`${ct.controlId}-${ct.metric}`}
            className="grid grid-cols-[100px_1fr_120px_120px_120px] items-center gap-4 px-6 py-3 border-b border-zinc-100 last:border-b-0"
          >
            <span className="text-[11px] font-mono font-medium text-zinc-500">
              {ct.controlId.replace("AI-GOV-", "GOV-")}
            </span>
            <span className="text-sm text-zinc-700">{ct.metric}</span>
            <span className="text-sm text-zinc-400 text-center">
              {ct.experimental ?? "Logged only"}
            </span>
            <span className="text-sm text-zinc-700 text-center font-medium">
              {ct.productionInternal}
            </span>
            <span className="text-sm text-zinc-900 text-center font-semibold">
              {ct.productionCustomerFacing}
            </span>
          </div>
        ))}
      </div>

      {/* Explainer */}
      <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-zinc-900 mb-2">
          How Thresholds Scale with Risk
        </h3>
        <p className="text-sm text-zinc-600">
          Thresholds are encoded in the platform&apos;s configuration and
          enforced automatically. Higher-risk solutions (customer-facing) face
          stricter thresholds. Experimental solutions log metrics without
          gating, allowing teams to iterate before committing to production
          standards. The team reviews and calibrates thresholds quarterly.
        </p>
      </div>
    </div>
  );
}

// --- Main Page ---

export default function ControlsPage() {
  const [activeTab, setActiveTab] = useState<TabId>("controls");

  return (
    <div>
      <Header
        title="Controls Register"
        subtitle="Automated controls mapped to risks, regulations, and evidence"
      />
      <div className="px-8 py-6 space-y-6">
        {/* Tabs */}
        <div className="flex gap-1 bg-zinc-100 p-1 rounded-lg w-fit">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "bg-white text-zinc-900 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {activeTab === "controls" && <ControlsTab />}
        {activeTab === "risks" && <RisksTab />}
        {activeTab === "regulatory" && <RegulatoryTab />}
        {activeTab === "thresholds" && <ThresholdsTab />}
      </div>
    </div>
  );
}
