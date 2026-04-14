/**
 * API client for the Chapter Agent backend.
 * Falls back to hardcoded data if the backend is unavailable.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 3000);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      next: { revalidate: 30 },
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`);
    }
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

import type {
  SolutionSummary,
  SolutionDetail,
  TraceStep,
  CatalogComponent,
  GenerationResult,
  ValidationDataset,
} from "./types";

export async function fetchSolutions(): Promise<SolutionSummary[]> {
  return fetchJSON<SolutionSummary[]>("/api/solutions");
}

export async function fetchSolutionDetail(id: string): Promise<SolutionDetail> {
  return fetchJSON<SolutionDetail>(`/api/solutions/${id}`);
}

export async function fetchTraceSteps(id: string): Promise<TraceStep[]> {
  return fetchJSON<TraceStep[]>(`/api/traces/${id}`);
}

export async function fetchEvidence(id: string): Promise<Record<string, unknown>> {
  return fetchJSON<Record<string, unknown>>(`/api/evidence/${id}`);
}

export function getEvidenceDownloadUrl(id: string): string {
  return `${API_BASE}/api/evidence/${id}/download`;
}

export async function fetchCatalog(): Promise<CatalogComponent[]> {
  return fetchJSON<CatalogComponent[]>("/api/catalog");
}

export async function generateTestCases(
  solutionId: string,
  numCases: number,
  queryTypes: string[],
): Promise<GenerationResult> {
  const res = await fetch(`${API_BASE}/api/catalog/generator/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      solution_id: solutionId,
      num_cases: numCases,
      query_types: queryTypes,
    }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchValidationDataset(
  solutionId: string,
): Promise<ValidationDataset> {
  return fetchJSON<ValidationDataset>(
    `/api/catalog/validation/${solutionId}`,
  );
}

export async function updateReviewStatus(
  solutionId: string,
  caseId: string,
  status: string,
  reviewedBy: string,
  notes?: string,
): Promise<void> {
  const res = await fetch(
    `${API_BASE}/api/catalog/validation/${solutionId}/${caseId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        review_status: status,
        reviewed_by: reviewedBy,
        review_notes: notes,
      }),
    },
  );
  if (!res.ok) throw new Error(`API error: ${res.status}`);
}

export async function signOffDataset(
  solutionId: string,
  reviewer: string,
): Promise<void> {
  const res = await fetch(
    `${API_BASE}/api/catalog/validation/${solutionId}/sign-off`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewer }),
    },
  );
  if (!res.ok) throw new Error(`API error: ${res.status}`);
}

export async function onboardSolution(
  data: Record<string, unknown>,
): Promise<{ id: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/solutions/onboard`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: `API error: ${res.status}` }));
    throw new Error(err.detail || `API error: ${res.status}`);
  }
  return res.json();
}
