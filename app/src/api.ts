// Thin typed client for the QRME FastAPI backend.
// Base URL is configurable (Settings); defaults to the local dev server.

const DEFAULT_BASE = "http://127.0.0.1:8000";

export function getBase(): string {
  return localStorage.getItem("qrme.base") || DEFAULT_BASE;
}
export function setBase(url: string) {
  localStorage.setItem("qrme.base", url.replace(/\/+$/, ""));
}

async function req<T>(
  path: string,
  opts: { method?: string; body?: unknown; token?: string } = {},
): Promise<T> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (opts.token) headers["authorization"] = `Bearer ${opts.token}`;
  const res = await fetch(getBase() + path, {
    method: opts.method || "GET",
    headers,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = (data && (data.detail || data.message)) || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as T;
}

// ---- types (only the fields the app reads) ----
export interface Profile {
  id: string;
  display_name: string;
  persona: string;
  kind: string;
  purpose?: string;
  status?: string;
  owner_token?: string;
}
export interface Stats {
  sessions: number;
  memory_entries: number;
  moderation_pass_rate: number;
  relationship_graph: number;
  engagement_average: number;
  sources: number;
  posts: number;
  surfaces: number;
}
export interface ChatMessage {
  id: string;
  role: string;
  content: string;
  status: string;        // "approved" | "held" | "rejected"
  flag_reason?: string | null;
}
export interface ChatReply {
  interactor_message: ChatMessage;
  profile_message: ChatMessage;
  handoff?: { state: string; specialist?: string } | null;
  persona_signature?: string;
}
export interface Interactor { id: string; display_name: string; token: string }
export interface MemoryEntry { role: string; content: string; at?: string }

// ---- endpoints ----
export const api = {
  health: () => req<{ status?: string }>("/health").then(() => true).catch(() => false),

  offlineStatus: () => req<Record<string, unknown>>("/offline/status"),

  createProfile: (body: {
    owner_id: string; kind: string; display_name: string; persona: string;
    verification: { birthdate: string }; purpose?: string;
  }) => req<Profile>("/profiles", { method: "POST", body }),

  getProfile: (id: string) => req<Profile>(`/profiles/${id}`),

  stats: (id: string, token: string) =>
    req<Stats>(`/profiles/${id}/stats`, { token }),

  createInteractor: (body: { display_name: string; birthdate?: string }) =>
    req<Interactor>("/interactors", { method: "POST", body }),

  setRelationship: (
    profileId: string, interactorId: string,
    body: { relationship_type: string; nickname?: string; tone?: string; boundaries?: string[] },
    token: string,
  ) => req<unknown>(`/profiles/${profileId}/relationships/${interactorId}`, {
    method: "PUT", body, token,
  }),

  chat: (profileId: string, body: { interactor_id: string; message: string }) =>
    req<ChatReply>(`/profiles/${profileId}/chat`, { method: "POST", body }),

  transparency: (id: string) =>
    req<{ active_relationships: number; relationships?: unknown[] }>(
      `/profiles/${id}/transparency`),

  memory: (profileId: string, interactorId: string, token: string) =>
    req<{ history: MemoryEntry[] } | MemoryEntry[]>(
      `/profiles/${profileId}/memory/${interactorId}`, { token }),

  clearMemory: (profileId: string, interactorId: string, token: string) =>
    req<unknown>(`/profiles/${profileId}/memory/${interactorId}`, {
      method: "DELETE", token,
    }),
};
