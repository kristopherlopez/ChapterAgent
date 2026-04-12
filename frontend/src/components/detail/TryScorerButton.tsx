import Link from "next/link";
import { BarChart3 } from "lucide-react";

export default function TryScorerButton({ solutionId }: { solutionId: string }) {
  return (
    <Link
      href={`/solutions/${solutionId}/score`}
      className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
    >
      <BarChart3 className="w-4 h-4" />
      Try Scorer
    </Link>
  );
}
