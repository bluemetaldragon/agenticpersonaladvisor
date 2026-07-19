// Mirrors the backend domain models (backend/app/domain.py). Keep in sync with
// the API contract. All ids are backend-generated strings.

export type RetentionMode = "persist" | "ephemeral";

export interface Lens {
  id: string;
  name: string;
  keywords: string[];
  builtin: boolean;
}

export interface PackSection {
  section_ref: string;
  title: string;
  text: string;
}

export interface BoardPack {
  id: string;
  title: string;
  uploaded_at: string;
  sections: PackSection[];
  retention_mode: RetentionMode;
}

export interface PreReadItem {
  item_ref: string;
  heading: string;
  body: string;
  source_section_ref: string;
}

export interface PreRead {
  id: string;
  pack_id: string;
  profile_id: string;
  items: PreReadItem[];
  generated_at: string;
}

export interface ChallengeItem {
  item_ref: string;
  question: string;
  source_item_ref: string;
}

export interface ChallengeSheet {
  id: string;
  pack_id: string;
  profile_id: string;
  items: ChallengeItem[];
  generated_at: string;
}

export interface Source {
  url: string;
  snippet: string;
  retrieved_at: string;
}

export interface DeepDive {
  id: string;
  pack_id: string;
  question: string;
  source_item_ref: string | null;
  analysis: string;
  sources: Source[];
  created_at: string;
  sanitised_query?: string;
}

export type JobStatus =
  | "queued" | "parsing" | "indexing"
  | "drafting_preread" | "drafting_challenge"
  | "ready" | "failed";

export type StepState = "pending" | "active" | "done";

export interface JobStep { name: string; state: StepState; }
export interface JobLogEntry { ts: string; message: string; }

export interface Job {
  id: string;
  pack_id: string | null;
  title: string;
  source_filename: string | null;
  status: JobStatus;
  percent: number;
  steps: JobStep[];
  log: JobLogEntry[];
  error: string | null;
  created_at: string;
}

export type RunType = "ingest" | "preread" | "challenge" | "deepdive";

export interface RunTrace {
  id: string;
  pack_id: string;
  run_type: RunType;
  firewall_query: string | null;
  trace_ref: string | null;
  created_at: string;
}

export interface UserSettings {
  id: string;
  default_lens: string;
  focus_areas: string[];
  depth: string;
  accent: string;
  favicon_ref: string | null;
  app_name: string;
  logo_ref: string | null;
  onboarding_seen_version: string | null;
}

export interface PackDetail {
  pack: BoardPack;
  pre_read: PreRead | null;
  challenge: ChallengeSheet | null;
  deepdives: DeepDive[];
}

export interface PackSummary {
  pack_id: string;
  title: string;
  uploaded_at: string;
  retention_mode: RetentionMode;
}