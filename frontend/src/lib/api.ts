/**
 * API client for the Chapter Agent backend.
 * Falls back to hardcoded data if the backend is unavailable.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    next: { revalidate: 30 },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

import type {
  SolutionSummary,
  SolutionDetail,
  FrameworkScore,
  TraceStep,
} from "./types";

export async function fetchSolutions(): Promise<SolutionSummary[]> {
  return fetchJSON<SolutionSummary[]>("/api/solutions");
}

export async function fetchSolutionDetail(id: string): Promise<SolutionDetail> {
  return fetchJSON<SolutionDetail>(`/api/solutions/${id}`);
}

export async function fetchFrameworkScores(): Promise<FrameworkScore[]> {
  return fetchJSON<FrameworkScore[]>("/api/scorecard");
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
