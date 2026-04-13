import { notFound } from "next/navigation";
import Link from "next/link";
import Header from "@/components/layout/Header";
import { documentDetails, governanceDocuments, aiGovPolicies } from "@/lib/data";
import type { DocumentType, DocumentStatus, DocumentSection } from "@/lib/types";

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

        {/* Document Sections */}
        {doc.sections && doc.sections.length > 0 && doc.sections.map((section: DocumentSection, idx: number) => (
          <div key={idx} className="bg-white border border-zinc-200 rounded-lg p-6 space-y-4">
            <h3 className="text-sm font-semibold text-zinc-900">{section.title}</h3>

            {section.content && (
              <p className="text-sm text-zinc-600 leading-relaxed">{section.content}</p>
            )}

            {section.bullets && (
              <ul className="space-y-2">
                {section.bullets.map((bullet, i) => (
                  <li key={i} className="flex gap-2 text-sm text-zinc-600">
                    <span className="text-zinc-400 mt-1 shrink-0">-</span>
                    <span className="leading-relaxed">{bullet}</span>
                  </li>
                ))}
              </ul>
            )}

            {section.subsections && (
              <div className="space-y-4">
                {section.subsections.map((sub, i) => (
                  <div key={i}>
                    <h4 className="text-sm font-medium text-zinc-800 mb-1">{sub.title}</h4>
                    <p className="text-sm text-zinc-600 leading-relaxed">{sub.content}</p>
                  </div>
                ))}
              </div>
            )}

            {section.table && (
              <div className="overflow-x-auto -mx-6 px-6">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-zinc-200">
                      {section.table.headers.map((header, i) => (
                        <th key={i} className="text-left py-2 pr-4 font-medium text-zinc-700 text-xs uppercase tracking-wider">
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100">
                    {section.table.rows.map((row, i) => (
                      <tr key={i} className="hover:bg-zinc-50">
                        {row.map((cell, j) => (
                          <td key={j} className={`py-2.5 pr-4 text-zinc-600 leading-relaxed ${j === 0 ? "font-medium text-zinc-800" : ""}`}>
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}

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
