"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function DatasetExplorer() {
  const searchParams = useSearchParams();
  const ds = searchParams.get("ds") || "australian";
  const src = `/dataset-explorer.html#${ds}`;

  return (
    <iframe
      src={src}
      className="w-full h-full border-0"
      title="Dataset Explorer"
    />
  );
}

export default function DatasetsPage() {
  return (
    <div className="h-full">
      <Suspense fallback={<div className="p-8 text-zinc-500">Loading explorer...</div>}>
        <DatasetExplorer />
      </Suspense>
    </div>
  );
}
