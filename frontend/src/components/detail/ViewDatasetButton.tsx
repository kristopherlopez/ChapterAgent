import { Database } from "lucide-react";

const DATASET_MAP: Record<string, string> = {
  "credit-default-scorer": "taiwan",
  "credit-approval-scorer": "australian",
};

export default function ViewDatasetButton({ solutionId }: { solutionId: string }) {
  const dataset = DATASET_MAP[solutionId];
  if (!dataset) return null;

  return (
    <a
      href={`/dataset-explorer.html#${dataset}`}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 px-4 py-2 border border-zinc-300 text-zinc-700 text-sm font-medium rounded-lg hover:bg-zinc-50 transition-colors"
    >
      <Database className="w-4 h-4" />
      View Dataset
    </a>
  );
}
