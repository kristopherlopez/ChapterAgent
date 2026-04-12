import Link from "next/link";
import Header from "@/components/layout/Header";
import { governanceDocuments, aiGovPolicies } from "@/lib/data";
import type { DocumentType, DocumentStatus } from "@/lib/types";

function TypeBadge({ type }: { type: DocumentType }) {
  const styles: Record<DocumentType, string> = {
    policy: "bg-zinc-900 text-white",
    standard: "bg-blue-100 text-blue-800 border border-blue-200",
    framework: "bg-purple-100 text-purple-800 border border-purple-200",
    guideline: "bg-amber-100 text-amber-800 border border-amber-200",
  };
  return (
    <span
      className={`inline-flex justify-center min-w-[80px] px-2 py-0.5 rounded-full text-xs font-medium capitalize ${styles[type]}`}
    >
      {type}
    </span>
  );
}

function StatusBadge({ status }: { status: DocumentStatus }) {
  const styles: Record<DocumentStatus, string> = {
    active: "bg-emerald-100 text-emerald-800 border border-emerald-200",
    draft: "bg-amber-100 text-amber-800 border border-amber-200",
    "under-review": "bg-blue-100 text-blue-800 border border-blue-200",
  };
  return (
    <span
      className={`inline-flex justify-center min-w-[80px] px-2 py-0.5 rounded-full text-xs font-medium capitalize ${styles[status]}`}
    >
      {status}
    </span>
  );
}

function ControlBadge({ id }: { id: string }) {
  const shortId = id.replace("AI-GOV-", "");
  const description = aiGovPolicies[id] ?? id;
  return (
    <span
      title={`${id}: ${description}`}
      className="inline-flex px-1.5 py-0.5 rounded text-[11px] font-mono font-medium bg-zinc-100 text-zinc-600 border border-zinc-200"
    >
      {shortId}
    </span>
  );
}

export default function DocumentsPage() {
  return (
    <div>
      <Header
        title="Governance Documents"
        subtitle="Policy documents, standards, and frameworks referenced by platform controls"
      />
      <div className="px-8 py-6 space-y-6">
        <div className="bg-white border border-zinc-200 rounded-lg">
          {/* Header row */}
          <div className="grid grid-cols-[1.25fr_100px_160px_80px_0.75fr_100px] items-center gap-4 px-6 py-4 border-b border-zinc-100">
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
              Document
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
              Type
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
              Owner
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider text-center">
              Status
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
              Linked Controls
            </p>
            <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
              Review
            </p>
          </div>

          {/* Rows */}
          {governanceDocuments.map((doc) => (
            <Link
              key={doc.id}
              href={`/documents/${doc.id}`}
              className="grid grid-cols-[1.25fr_100px_160px_80px_0.75fr_100px] items-center gap-4 px-6 py-4 border-b border-zinc-100 last:border-b-0 hover:bg-zinc-50 transition-colors"
            >
              <div>
                <p className="text-sm font-medium text-zinc-900">
                  {doc.title}
                </p>
                <p className="text-xs text-zinc-500 mt-0.5">
                  {doc.description}
                </p>
              </div>
              <div className="text-center"><TypeBadge type={doc.type} /></div>
              <p className="text-sm text-zinc-600">{doc.owner}</p>
              <div className="text-center"><StatusBadge status={doc.status} /></div>
              <div className="flex flex-wrap gap-1">
                {doc.aiGovControls.map((ctrl) => (
                  <ControlBadge key={ctrl} id={ctrl} />
                ))}
              </div>
              <p className="text-xs text-zinc-500">{doc.nextReviewDate}</p>
            </Link>
          ))}
        </div>

        {/* Explainer card */}
        <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-2">
            How Documents Connect to Controls
          </h3>
          <p className="text-sm text-zinc-600">
            Each document defines governance requirements that the platform
            enforces automatically through AI-GOV controls. Controls are checked
            at deployment (CI/CD gate) and monitored continuously in production.
            Hover over a control badge to see the specific policy it enforces.
            The platform traces every automated check back to the originating
            document, creating an auditable chain from policy to evidence.
          </p>
        </div>

        {/* Legend */}
        <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-4">
          <div className="flex items-center gap-6 text-xs text-zinc-500 flex-wrap">
            <span className="text-zinc-400 font-medium uppercase tracking-wider mr-2">
              Type
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium bg-zinc-900 text-white">
                policy
              </span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-100 text-blue-800 border border-blue-200">
                standard
              </span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium bg-purple-100 text-purple-800 border border-purple-200">
                framework
              </span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-100 text-amber-800 border border-amber-200">
                guideline
              </span>
            </span>
            <span className="text-zinc-300">|</span>
            <span className="text-zinc-400 font-medium uppercase tracking-wider mr-2">
              Status
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">
                active
              </span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-100 text-amber-800 border border-amber-200">
                draft
              </span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
