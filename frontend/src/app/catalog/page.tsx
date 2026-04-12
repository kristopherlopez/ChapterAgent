"use client";

import { useState } from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";
import { catalogComponents } from "@/lib/data";
import type { ComponentType } from "@/lib/types";
import {
  Shield,
  BarChart3,
  ShieldCheck,
  Activity,
  Wrench,
  ChevronDown,
  ChevronRight,
  ArrowRight,
  Package,
} from "lucide-react";

const TYPE_FILTERS: { label: string; value: ComponentType | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Guardrail", value: "guardrail" },
  { label: "Evaluation", value: "evaluation" },
  { label: "Compliance", value: "compliance" },
  { label: "Observability", value: "observability" },
  { label: "Tooling", value: "tooling" },
];

const TYPE_ICONS: Record<ComponentType, typeof Shield> = {
  guardrail: Shield,
  evaluation: BarChart3,
  compliance: ShieldCheck,
  observability: Activity,
  tooling: Wrench,
};

const TYPE_COLORS: Record<ComponentType, string> = {
  guardrail: "bg-violet-50 text-violet-700 border-violet-200",
  evaluation: "bg-blue-50 text-blue-700 border-blue-200",
  compliance: "bg-emerald-50 text-emerald-700 border-emerald-200",
  observability: "bg-amber-50 text-amber-700 border-amber-200",
  tooling: "bg-rose-50 text-rose-700 border-rose-200",
};

function TypeBadge({ type }: { type: ComponentType }) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${TYPE_COLORS[type]}`}
    >
      {type}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  if (status === "beta") {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
        Beta
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
      Active
    </span>
  );
}

export default function CatalogPage() {
  const [activeFilter, setActiveFilter] = useState<ComponentType | "all">("all");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered =
    activeFilter === "all"
      ? catalogComponents
      : catalogComponents.filter((c) => c.type === activeFilter);

  const totalComponents = catalogComponents.length;
  const activeCount = catalogComponents.filter((c) => c.status === "active").length;
  const solutionsUsing = new Set(catalogComponents.flatMap((c) => c.adoption)).size;

  return (
    <div>
      <Header
        title="Component Catalog"
        subtitle="Reusable platform components the Chapter ships to squads"
      />
      <div className="px-8 py-6 space-y-6">
        {/* Summary stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white border border-zinc-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-zinc-100 rounded-lg">
                <Package className="w-5 h-5 text-zinc-600" />
              </div>
              <div>
                <p className="text-2xl font-semibold text-zinc-900">{totalComponents}</p>
                <p className="text-xs text-zinc-500">Total Components</p>
              </div>
            </div>
          </div>
          <div className="bg-white border border-zinc-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-2xl font-semibold text-zinc-900">{activeCount}</p>
                <p className="text-xs text-zinc-500">Active Components</p>
              </div>
            </div>
          </div>
          <div className="bg-white border border-zinc-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Activity className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-semibold text-zinc-900">{solutionsUsing}</p>
                <p className="text-xs text-zinc-500">Solutions Consuming</p>
              </div>
            </div>
          </div>
        </div>

        {/* Type filter pills */}
        <div className="flex gap-1 bg-zinc-100 p-1 rounded-lg w-fit">
          {TYPE_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setActiveFilter(f.value)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeFilter === f.value
                  ? "bg-white text-zinc-900 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-700"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Component table */}
        <div className="bg-white border border-zinc-200 rounded-lg">
          <div className="grid grid-cols-[1fr_120px_200px_80px_32px] items-center gap-4 px-6 py-4 border-b border-zinc-100">
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
              Component
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
              Type
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
              Adoption
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
              Status
            </p>
            <span />
          </div>

          {filtered.map((component) => {
            const isExpanded = expandedId === component.id;
            const Icon = TYPE_ICONS[component.type];
            const isTooling = component.id === "tooling-golden-dataset-generator" || component.id === "tooling-golden-dataset-validation";
            const toolLink = component.id === "tooling-golden-dataset-generator" ? "/catalog/generator" : "/catalog/validation";

            return (
              <div key={component.id} className="border-b border-zinc-100 last:border-b-0">
                <button
                  onClick={() => setExpandedId(isExpanded ? null : component.id)}
                  className="w-full grid grid-cols-[1fr_120px_200px_80px_32px] items-center gap-4 px-6 py-4 hover:bg-zinc-50 transition-colors text-left"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-1.5 rounded-md ${TYPE_COLORS[component.type].split(" ")[0]}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-zinc-900">
                        {component.name}
                      </p>
                      <p className="text-xs text-zinc-500 mt-0.5 line-clamp-1">
                        {component.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex justify-center">
                    <TypeBadge type={component.type} />
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-sm text-zinc-600">
                      {component.adoption.length} solution{component.adoption.length !== 1 ? "s" : ""}
                    </span>
                    {component.adoption.length > 0 && (
                      <div className="flex -space-x-1 ml-2">
                        {component.adoption.slice(0, 4).map((_, i) => (
                          <div
                            key={i}
                            className="w-5 h-5 rounded-full bg-zinc-200 border-2 border-white flex items-center justify-center"
                          >
                            <span className="text-[8px] font-medium text-zinc-600">
                              {i + 1}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex justify-center">
                    <StatusBadge status={component.status} />
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-zinc-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-zinc-400" />
                  )}
                </button>

                {isExpanded && (
                  <div className="px-6 pb-4 space-y-3">
                    <div className="bg-zinc-50 rounded-lg p-4 space-y-3">
                      <p className="text-sm text-zinc-700">{component.description}</p>

                      <div className="grid grid-cols-2 gap-4 pt-2">
                        <div>
                          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                            Squad Provides
                          </p>
                          <p className="text-sm text-zinc-700">
                            {component.interface.squadProvides}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                            Component Returns
                          </p>
                          <p className="text-sm text-zinc-700">
                            {component.interface.componentReturns}
                          </p>
                        </div>
                      </div>

                      {component.adoption.length > 0 && (
                        <div className="pt-2">
                          <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider mb-1">
                            Adopted By
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {component.adoption.map((sid) => (
                              <Link
                                key={sid}
                                href={`/solutions/${sid}`}
                                className="inline-flex items-center gap-1 px-2 py-1 bg-white border border-zinc-200 rounded-md text-xs text-zinc-600 hover:border-zinc-300 hover:text-zinc-900 transition-colors"
                              >
                                {sid}
                              </Link>
                            ))}
                          </div>
                        </div>
                      )}

                      {isTooling && (
                        <div className="pt-2">
                          <Link
                            href={toolLink}
                            className="inline-flex items-center gap-2 px-3 py-1.5 bg-zinc-900 text-white rounded-md text-sm font-medium hover:bg-zinc-800 transition-colors"
                          >
                            Open Tool
                            <ArrowRight className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Ownership model explainer */}
        <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-2">
            Chapter Builds, Squads Consume
          </h3>
          <p className="text-sm text-zinc-600">
            The Chapter owns and maintains every component listed here. Squads consume them by declaring
            configuration in their{" "}
            <code className="px-1.5 py-0.5 bg-zinc-200 rounded text-xs font-mono">
              solution.yaml
            </code>{" "}
            manifest. The platform discovers manifests automatically, wires up the appropriate
            guardrails, evaluation metrics, and compliance gates based on solution type and risk tier.
            Adoption is tracked via telemetry &mdash; the numbers above reflect live usage across all
            registered solutions.
          </p>
        </div>
      </div>
    </div>
  );
}
