// Typed client for the Board-Prep backend (FastAPI). One method per route in
// backend/app/main.py. Base URL from NEXT_PUBLIC_API_BASE (defaults to :8000).

import type {
  ChallengeSheet, DeepDive, Job, Lens, PackDetail, PackSummary,
  PreRead, RetentionMode, RunTrace, UserSettings,
} from "@/types/api";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch { /* non-JSON error body */ }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

function form(data: Record<string, string | Blob | undefined>): FormData {
  const fd = new FormData();
  for (const [k, v] of Object.entries(data)) {
    if (v !== undefined) fd.append(k, v);
  }
  return fd;
}

export const api = {
  // health
  health: () => req<{ status: string }>("/health"),

  // packs & jobs
  uploadPack: (file: File, opts: { title?: string; lens_id?: string; retention?: RetentionMode }) =>
    req<{ job_id: string; status: string }>("/packs", {
      method: "POST",
      body: form({
        file, title: opts.title, lens_id: opts.lens_id, retention: opts.retention,
      }),
    }),
  listJobs: () => req<Job[]>("/jobs"),
  getJob: (id: string) => req<Job>(`/jobs/${id}`),
  jobEventsUrl: (id: string) => `${BASE}/jobs/${id}/events`, // for EventSource

  listPacks: () => req<PackSummary[]>("/packs"),
  getPack: (id: string) => req<PackDetail>(`/packs/${id}`),
  deletePack: (id: string) => req<{ deleted: string }>(`/packs/${id}`, { method: "DELETE" }),
  regeneratePreread: (id: string, lens_id: string) =>
    req<PreRead>(`/packs/${id}/preread`, { method: "POST", body: form({ lens_id }) }),

  // challenge
  generateChallenge: (packId: string, lens_id: string) =>
    req<ChallengeSheet>(`/packs/${packId}/challenge`, { method: "POST", body: form({ lens_id }) }),
  getChallenge: (packId: string) => req<ChallengeSheet>(`/packs/${packId}/challenge`),

  // deep-dive
  createDeepDive: (packId: string, question: string, source_item_ref?: string) =>
    req<DeepDive>(`/packs/${packId}/deepdives`, {
      method: "POST", body: form({ question, source_item_ref }),
    }),
  listDeepDives: (packId: string) => req<DeepDive[]>(`/packs/${packId}/deepdives`),
  deleteDeepDive: (id: string) => req<{ deleted: string }>(`/deepdives/${id}`, { method: "DELETE" }),

  // lenses
  listLenses: () => req<Lens[]>("/lenses"),
  createLens: (lens: Omit<Lens, "id" | "builtin"> & { id?: string }) =>
    req<Lens>("/lenses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...lens, builtin: false }),
    }),
  updateLens: (id: string, lens: Omit<Lens, "builtin">) =>
    req<Lens>(`/lenses/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...lens, builtin: false }),
    }),
  deleteLens: (id: string) => req<{ deleted: string }>(`/lenses/${id}`, { method: "DELETE" }),

  // settings
  getSettings: () => req<UserSettings>("/settings"),
  updateSettings: (patch: Partial<UserSettings>) =>
    req<UserSettings>("/settings", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch),
    }),

  // activity / traces
  listTraces: (packId: string) => req<RunTrace[]>(`/packs/${packId}/traces`),
  listAllTraces: () => req<RunTrace[]>("/traces"),
};

export { ApiError };