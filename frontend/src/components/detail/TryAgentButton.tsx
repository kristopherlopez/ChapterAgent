import Link from "next/link";
import { MessageSquare } from "lucide-react";

export default function TryAgentButton({ solutionId }: { solutionId: string }) {
  return (
    <Link
      href={`/solutions/${solutionId}/chat`}
      className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 transition-colors"
    >
      <MessageSquare className="w-4 h-4" />
      Try Agent
    </Link>
  );
}
