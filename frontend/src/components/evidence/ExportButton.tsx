"use client";

import { Download } from "lucide-react";
import { getEvidenceDownloadUrl } from "@/lib/api";

export default function ExportButton({ solutionId }: { solutionId?: string }) {
  async function handleExport() {
    if (!solutionId) {
      alert("Full portfolio evidence export coming soon.");
      return;
    }

    try {
      const url = getEvidenceDownloadUrl(solutionId);
      const res = await fetch(url);
      if (!res.ok) throw new Error("Backend unavailable");

      const blob = await res.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `evidence-${solutionId}.json`;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch {
      alert(
        `Evidence report for "${solutionId}" — backend not running. Start the backend to enable download.`
      );
    }
  }

  return (
    <button
      onClick={handleExport}
      className="inline-flex items-center gap-2 px-4 py-2 bg-zinc-900 text-white text-sm font-medium rounded-lg hover:bg-zinc-800 transition-colors"
    >
      <Download className="w-4 h-4" />
      Export Evidence
    </button>
  );
}
