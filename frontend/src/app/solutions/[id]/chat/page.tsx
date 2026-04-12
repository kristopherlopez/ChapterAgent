import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { solutionDetails } from "@/lib/data";
import ChatInterface from "./ChatInterface";

export default async function ChatPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const solution = solutionDetails[id];

  if (!solution) {
    notFound();
  }

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-zinc-200 bg-white px-8 py-4 flex items-center gap-4">
        <Link
          href={`/solutions/${id}`}
          className="text-zinc-400 hover:text-zinc-700 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h2 className="text-lg font-semibold text-zinc-900">
            {solution.name}
          </h2>
          <p className="text-xs text-zinc-500">
            Interactive agent &middot; {solution.riskTier} &middot; Guardrails active
          </p>
        </div>
      </div>
      <ChatInterface solutionId={id} />
    </div>
  );
}
