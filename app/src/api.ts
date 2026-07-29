// Thin typed client for the QRME FastAPI backend.
// Base URL is configurable (Settings).
//
// Default base: when the studio is served *by* the API (the phone case —
// http://<machine>:8000/app/), the backend is the origin we came from, so
// the phone needs no configuration at all. Only the Electron desktop shell
// (file://) and the Vite dev server fall back to the local backend.
const LOOPBACK = "http://127.0.0.1:8000";
function defaultBase(): string {
  if (typeof window === "undefined") return LOOPBACK;
  const { protocol, origin, pathname } = window.location;
  if (protocol !== "http:" && protocol !== "https:") return LOOPBACK;  // file://
  if (pathname.startsWith("/app")) return origin;   // served by the API itself
  return LOOPBACK;                                   // vite dev on :5173
}

// The desktop shell starts its own backend and tells us where it is. That
// address wins over any stored loopback one: a saved "127.0.0.1:8000" from an
// earlier install would otherwise point at a leftover backend of an older
// version — which is exactly how an upgraded app kept meeting an old signup.
function desktopBackendUrl(): string | null {
  if (typeof window === "undefined") return null;
  const bridge = (window as { qrmeDesktop?: { backendUrl?: string | null } }).qrmeDesktop;
  return bridge?.backendUrl || null;
}

export function getBase(): string {
  const stored = localStorage.getItem("qrme.base");
  const desktop = desktopBackendUrl();
  if (desktop) {
    // Only a remote address survives on the desktop; a loopback one is this
    // app's own business and must match the backend it started.
    if (stored && !/^https?:\/\/(127\.0\.0\.1|localhost|\[::1\])(:|\/|$)/.test(stored)) {
      return stored;
    }
    return desktop;
  }
  return stored || defaultBase();
}
export function setBase(url: string) {
  localStorage.setItem("qrme.base", url.replace(/\/+$/, ""));
}
export function clearBase() { localStorage.removeItem("qrme.base"); }

// The console's own version, injected at build time (vite.config.ts) and
// compared against /health's — see VersionGuard.tsx.
declare const __APP_VERSION__: string;
export const CONSOLE_VERSION: string =
  typeof __APP_VERSION__ !== "undefined" ? __APP_VERSION__ : "dev";

// Bring-your-own model key: stored on this device only, sent per-request as
// x-llm-api-key so generations run on the user's own credential. The backend
// never persists it; without one, the deployment's key (if any) answers.
export function getLlmKey(): string { return localStorage.getItem("qrme.llmKey") || ""; }
export function setLlmKey(key: string) {
  if (key.trim()) localStorage.setItem("qrme.llmKey", key.trim());
  else localStorage.removeItem("qrme.llmKey");
}

// Accounts: the email is verified (emailed code) before sign-in works. The
// account is what owns — its id is the owner_id profiles are created under.
export const accountApi = {
  signup: (body: { email: string; password: string; display_name?: string }) =>
    req<{ account_id: string; email: string; verified: boolean; code_delivery?: string;
          verification: "local" | "email";
          // Present when verification is "local" (no mail transport — the
          // machine owner is trusted and the account activates directly).
          display_name?: string; account_token?: string }>(
      "/signup", { method: "POST", body }),
  verifyEmail: (body: { email: string; code: string }) =>
    req<{ account_id: string; email: string; display_name?: string; account_token: string }>(
      "/verify-email", { method: "POST", body }),
  resendCode: (email: string) =>
    req<{ email: string; code_delivery: string }>(
      "/verify-email/resend", { method: "POST", body: { email } }),
  signin: (body: { email: string; password: string }) =>
    req<{ account_id: string; email: string; display_name?: string; account_token: string }>(
      "/signin", { method: "POST", body }),
  // Which model answers, as a picker rather than a config file.
  listModels: () =>
    req<{ providers: { name: string; label: string; configured: boolean;
                       model: string; network: boolean }[]; default: string }>("/models"),
  getProfileModel: (pid: string) =>
    req<{ provider: string; effective: string }>(`/profiles/${pid}/model`),
  setProfileModel: (pid: string, provider: string, token: string) =>
    req<{ provider: string; effective: string }>(
      `/profiles/${pid}/model`, { method: "PUT", body: { provider }, token }),

  // Mail settings: what makes verification emails real instead of a line in
  // a log file. The password goes up; it never comes back down.
  getMailSettings: () =>
    req<{ transport: "smtp" | "console"; source: string; host: string | null;
          port: number; username: string | null; sender: string | null;
          public_url: string; password_set: boolean }>("/settings/mail"),
  saveMailSettings: (body: { host: string; port: number; username?: string;
                             password?: string; sender?: string; public_url?: string }) =>
    req<{ transport: string }>("/settings/mail", { method: "PUT", body }),
  clearMailSettings: () =>
    req<{ transport: string }>("/settings/mail", { method: "DELETE" }),
  testMailSettings: (to: string) =>
    req<{ sent: boolean; to: string }>("/settings/mail/test",
      { method: "POST", body: { to } }),
  requestReset: (email: string) =>
    req<{ email: string; code_delivery: string }>(
      "/password/reset/request", { method: "POST", body: { email } }),
  resetPassword: (body: { email: string; code: string; new_password: string }) =>
    req<{ email: string; reset: boolean }>(
      "/password/reset", { method: "POST", body }),
};

async function req<T>(
  path: string,
  opts: { method?: string; body?: unknown; token?: string } = {},
): Promise<T> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (opts.token) headers["authorization"] = `Bearer ${opts.token}`;
  const llmKey = getLlmKey();
  if (llmKey) headers["x-llm-api-key"] = llmKey;
  let res: Response;
  try {
    res = await fetch(getBase() + path, {
      method: opts.method || "GET",
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
  } catch {
    // A network-level failure surfaces as "Failed to fetch", which tells the
    // user nothing. Name the actual problem: no QRME backend answering.
    throw new Error(
      `Can't reach the QRME backend at ${getBase()}. ` +
      `Start it with "python -m qrme serve", or set the backend URL in Settings.`,
    );
  }
  const text = await res.text();
  // A body is not guaranteed to be JSON — a crashed server answers plain
  // text ("Internal Server Error"), and surfacing a JSON.parse exception
  // instead of those words is how one error hides another.
  let data: unknown = null;
  try { data = text ? JSON.parse(text) : null; }
  catch { data = null; }
  if (!res.ok) {
    const body = data as { detail?: unknown; message?: unknown } | null;
    const detail = (body && (body.detail || body.message)) || text.trim() || res.statusText;
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
  environment?: Record<string, string> | null;
}
export interface CompositionRow {
  source_profile_id: string;
  display_name: string;
  weight: number;
  aspect?: string | null;
}
export interface OrgOut {
  id: string;
  name: string;
  departments: { id: string; name: string; role: string;
                 profile_id: string; agent: string; scoped: boolean }[];
}
export interface CoordinationOut {
  id: string;
  goal: string;
  plan?: string | null;
  status: string;
  sealed?: boolean;
  initiated_by?: string;
  contributions?: { department: string; content: string; items_read: number }[];
  departments?: { name: string; items_read: number }[];
}
export interface DesigneeOut {
  id: string;
  name: string;
  kind: string;
  share: number;
  has_account: boolean;
}
export interface CampaignOut {
  id: string;
  profile_id: string;
  title: string;
  cause?: string | null;
  goal: number;
  raised: number;
  donors: number;
  status: string;
  proceeds_to: DesigneeOut[];
}
export interface SimulationOut {
  id: string;
  scenario: string;
  horizon: string;
  narrative: string;
  confidence: number;
  basis: { source_items: number; remembered_turns: number; note?: string };
  disclaimer?: string;
  created_at?: string;
}
export interface Interactor { id: string; display_name: string; token: string }
export interface MemoryEntry { role: string; content: string; at?: string }

// ---- endpoints ----
export interface PairInfo {
  console_url: string; api_url: string; console_built: boolean;
  reachable: boolean; qr_svg: string; how: string[]; note: string;
}

// The wrist's glanceable payload (GET /profiles/{id}/watch), reused by the
// always-on lights widget: counts and the profile chip are all it reads.
export interface WatchFace {
  profile: {
    id: string; display_name: string; status: string;
    light: "green" | "orange" | "red"; pending_approvals: number;
  };
  summary: { working: number; needing_assistance: number; stopped: number };
  haptic: string | null;
}

export const api = {
  health: () => req<{ status?: string }>("/health").then(() => true).catch(() => false),

  healthInfo: () => req<{ status?: string; version?: string }>("/health"),

  // How to open this studio on a phone: its URL on the local network.
  pair: () => req<PairInfo>("/pair"),

  offlineStatus: () => req<Record<string, unknown>>("/offline/status"),

  // The help box. No token: a beacon scan lands a stranger on a page, and
  // requiring an account to ask "what is this?" gates the one question that
  // arrives before one exists.
  help: (question: string) =>
    req<{ answer: string; disclosure: string; ai: boolean; refused: boolean;
          topics: string[] }>("/help", { method: "POST", body: { question } }),

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

  chat: (profileId: string, body: {
    interactor_id: string; message: string;
    // Environmental context (spec clause 1): the reply adapts to where the
    // person actually is. Optional; echoed back on the response.
    environment?: { location?: string; conditions?: string;
                    local_time?: string; activity?: string };
  }) =>
    req<ChatReply>(`/profiles/${profileId}/chat`, { method: "POST", body }),

  // Hybrid profiles (spec [0038]): several people blended into one persona.
  createComposite: (body: {
    owner_id: string; display_name: string;
    verification: { birthdate: string };
    sources: { profile_id: string; weight?: number; aspect?: string }[];
    purpose?: string;
  }) =>
    req<Profile & { owner_token: string; composition: CompositionRow[] }>(
      "/profiles/composite", { method: "POST", body }),
  composition: (profileId: string) =>
    req<{ profile_id: string; sources: CompositionRow[]; policy: string }>(
      `/profiles/${profileId}/composition`),

  // Real-time simulation (spec clauses 1 & 5): predictive modeling, owner-only.
  simulate: (profileId: string, body: {
    scenario: string; horizon?: "immediate" | "short_term" | "long_term";
    interactor_id?: string;
  }, token: string) =>
    req<SimulationOut>(`/profiles/${profileId}/simulate`,
      { method: "POST", body, token }),
  simulations: (profileId: string, token: string) =>
    req<SimulationOut[]>(`/profiles/${profileId}/simulations`, { token }),

  transparency: (id: string) =>
    req<{ active_relationships: number; relationships?: unknown[] }>(
      `/profiles/${id}/transparency`),

  // The vault's table of contents, with real names — one row per remembered
  // conversation, so the owner chooses what to erase by name, not by id.
  memories: (profileId: string, token: string) =>
    req<{ interactor_id: string; interactor_name: string; profile_name: string;
          turns: number; last_at: string }[]>(
      `/profiles/${profileId}/memories`, { token }),

  // The surfaces the console finally shows: friends (founder first), the
  // marketplace, the starter collection, and the rooms.
  friends: (profileId: string) =>
    req<{ friends: { profile_id: string; display_name: string; pinned?: boolean;
                     handle?: string | null }[]; founder_handles: string[] }>(
      `/profiles/${profileId}/friends`),
  suggestedFriends: (profileId: string) =>
    req<{ suggestions: { profile_id: string; display_name: string }[] } |
        { profile_id: string; display_name: string }[]>(
      `/profiles/${profileId}/friends/suggested`),
  addFriend: (profileId: string, friendId: string, token: string) =>
    req<unknown>(`/profiles/${profileId}/friends`,
      { method: "POST", body: { friend_id: friendId }, token }),
  marketplace: (tag?: string) =>
    req<{ profile_id: string; display_name: string; purpose?: string;
          blurb?: string; tags: string[] }[]>(
      `/marketplace${tag ? `?tag=${encodeURIComponent(tag)}` : ""}`),
  marketplaceListings: () =>
    req<{ listings?: unknown[] } | unknown[]>(`/marketplace/listings`),
  seedStarters: () =>
    req<{ created: string[]; skipped: string[]; repaired?: string[] }>(
      `/marketplace/seed`, { method: "POST" }),
  listRooms: () =>
    req<{ id: string; topic?: string | null; channel: string;
          participants: number; created_at: string }[]>(`/rooms`),
  createRoom: (body: { topic?: string; channel: string;
                       participants: { kind: string; id: string }[] }) =>
    req<{ id: string }>(`/rooms`, { method: "POST", body }),
  roomMessages: (roomId: string) =>
    req<unknown[]>(`/rooms/${roomId}/messages`),
  listDesks: () =>
    req<{ id: string; display_name: string; trade: string; location?: string;
          blurb?: string; presence: string; rated: number }[]>(`/desks`),

  // The profile's language: the console chrome follows it (l10n.ts).
  getLanguage: (profileId: string) =>
    req<{ language: string }>(`/profiles/${profileId}/language`),

  // The wrist's glanceable face, reused by the always-on lights widget.
  watchFace: (profileId: string, token: string) =>
    req<WatchFace>(`/profiles/${profileId}/watch`, { token }),

  // Crowdfunding with proceeds routed where the user said (spec [0020]).
  getProceeds: (profileId: string) =>
    req<{ proceeds_to: DesigneeOut[] }>(`/profiles/${profileId}/proceeds`),
  setProceeds: (profileId: string, designees: {
    name: string; kind: "loved_one" | "organization"; share: number;
    account_id?: string;
  }[], token: string) =>
    req<{ proceeds_to: DesigneeOut[] }>(`/profiles/${profileId}/proceeds`,
      { method: "PUT", body: { designees }, token }),
  listCampaigns: (profileId: string) =>
    req<CampaignOut[]>(`/profiles/${profileId}/campaigns`),
  createCampaign: (profileId: string, body: {
    title: string; goal: number; cause?: string;
  }, token: string) =>
    req<CampaignOut>(`/profiles/${profileId}/campaigns`,
      { method: "POST", body, token }),
  donate: (campaignId: string, body: {
    amount: number; giver_id?: string; note?: string; on_behalf_of?: string;
  }) =>
    req<{ split: { name: string; amount: number }[]; note_to_giver: string }>(
      `/campaigns/${campaignId}/donate`, { method: "POST", body }),
  closeCampaign: (campaignId: string, token: string) =>
    req<CampaignOut>(`/campaigns/${campaignId}/close`,
      { method: "POST", token }),

  // The operational ecosystem: departments staffed by role agents.
  listOrgs: (token: string) =>
    req<OrgOut[]>("/organizations", { token }),
  createOrg: (name: string, token: string) =>
    req<OrgOut>("/organizations", { method: "POST", body: { name }, token }),
  seedDemoOrg: (token: string) =>
    req<OrgOut & { note?: string }>("/organizations/demo",
      { method: "POST", token }),
  addDepartment: (orgId: string, body: {
    name: string; role: string; profile_id: string; grant_token?: string;
  }, token: string) =>
    req<OrgOut>(`/organizations/${orgId}/departments`,
      { method: "POST", body, token }),
  coordinate: (orgId: string, body: { goal: string; from_department: string },
               token: string) =>
    req<CoordinationOut>(`/organizations/${orgId}/coordinate`,
      { method: "POST", body, token }),
  listCoordinations: (orgId: string, token: string) =>
    req<CoordinationOut[]>(`/organizations/${orgId}/coordinations`, { token }),

  memory: (profileId: string, interactorId: string, token: string) =>
    req<{ history: MemoryEntry[] } | MemoryEntry[]>(
      `/profiles/${profileId}/memory/${interactorId}`, { token }),

  clearMemory: (profileId: string, interactorId: string, token: string) =>
    req<unknown>(`/profiles/${profileId}/memory/${interactorId}`, {
      method: "DELETE", token,
    }),
};
