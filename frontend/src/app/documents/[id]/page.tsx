import { notFound } from "next/navigation";
import Link from "next/link";
import Header from "@/components/layout/Header";
import { documentDetails, governanceDocuments, aiGovPolicies } from "@/lib/data";
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

export default async function DocumentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const doc = documentDetails[id];

  if (!doc) {
    notFound();
  }

  return (
    <div>
      <Header title={doc.title} subtitle={doc.description} />
      <div className="px-8 py-6 space-y-6">
        {/* Metadata bar */}
        <div className="flex items-center gap-4 flex-wrap">
          <TypeBadge type={doc.type} />
          <StatusBadge status={doc.status} />
          <span className="text-sm text-zinc-500">
            Owner: <span className="font-medium text-zinc-700">{doc.owner}</span>
          </span>
          <span className="text-sm text-zinc-500">
            Effective: <span className="font-medium text-zinc-700">{doc.effectiveDate}</span>
          </span>
          <span className="text-sm text-zinc-500">
            Next Review: <span className="font-medium text-zinc-700">{doc.nextReviewDate}</span>
          </span>
          <span className="text-sm text-zinc-500">
            Approval: <span className="font-medium text-zinc-700">{doc.approvalAuthority}</span>
          </span>
        </div>

        {/* Purpose & Scope */}
        <div className="bg-white border border-zinc-200 rounded-lg p-6 space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 mb-2">Purpose</h3>
            <p className="text-sm text-zinc-600 leading-relaxed">{doc.purpose}</p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-900 mb-2">Scope</h3>
            <p className="text-sm text-zinc-600 leading-relaxed">{doc.scope}</p>
          </div>
        </div>

        {/* Key Requirements */}
        <div className="bg-white border border-zinc-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-4">Key Requirements</h3>
          <ul className="space-y-3">
            {doc.keyRequirements.map((req, i) => (
              <li key={i} className="flex gap-3 text-sm text-zinc-600">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-zinc-100 text-zinc-500 text-xs font-medium flex items-center justify-center mt-0.5">
                  {i + 1}
                </span>
                <span className="leading-relaxed">{req}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Control Mapping */}
        <div className="bg-white border border-zinc-200 rounded-lg overflow-hidden">
          <div className="p-6 border-b border-zinc-100">
            <h3 className="text-sm font-semibold text-zinc-900">Platform Control Mapping</h3>
            <p className="text-xs text-zinc-500 mt-1">
              How the platform&apos;s automated controls enforce this document&apos;s requirements
            </p>
          </div>
          <div className="divide-y divide-zinc-100">
            {doc.controlMappings.map((mapping) => (
              <div key={mapping.controlId} className="p-6 hover:bg-zinc-50 transition-colors">
                <div className="flex items-start gap-4">
                  <span
                    title={aiGovPolicies[mapping.controlId] ?? mapping.controlId}
                    className="flex-shrink-0 inline-flex px-2 py-0.5 rounded text-xs font-mono font-medium bg-zinc-900 text-white"
                  >
                    {mapping.controlId}
                  </span>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-zinc-900">{mapping.requirement}</p>
                    <p className="text-sm text-zinc-500 leading-relaxed">{mapping.platformEnforcement}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Related Documents */}
        {doc.relatedDocuments.length > 0 && (
          <div className="bg-white border border-zinc-200 rounded-lg p-6">
            <h3 className="text-sm font-semibold text-zinc-900 mb-3">Related Documents</h3>
            <div className="flex flex-wrap gap-2">
              {doc.relatedDocuments.map((relId) => {
                const related = governanceDocuments.find((d) => d.id === relId);
                if (!related) return null;
                return (
                  <Link
                    key={relId}
                    href={`/documents/${relId}`}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-zinc-600 bg-zinc-50 border border-zinc-200 hover:bg-zinc-100 hover:text-zinc-900 transition-colors"
                  >
                    {related.title}
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
