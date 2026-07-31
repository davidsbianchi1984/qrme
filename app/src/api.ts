// Thin typed client for the QRME FastAPI backend.
import { recordProblem } from "./errors";
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
export const oauthApi = {
  providers: () =>
    req<{ providers: { provider: string; name: string; configured: boolean;
                       setup?: string }[] }>(`/auth/oauth/providers`),
  start: (provider: string) =>
    req<{ url: string; state: string }>(
      `/auth/oauth/${provider}/start`, { method: "POST", body: {} }),
  claim: (state: string) =>
    req<{ ready: boolean; account_id?: string; email?: string;
          account_token?: string }>(
      `/auth/oauth/claim?state=${encodeURIComponent(state)}`),
};

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
    // Never reached a server. Recorded as status 0, which is a different
    // failure from anything the backend answered and worth telling apart.
    recordProblem(opts.method || "GET", path, 0);

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
    // The status and the operation, never the detail below: that string
    // carries whatever the user typed.
    recordProblem(opts.method || "GET", path, res.status);
    const body = data as { detail?: unknown; message?: unknown } | null;
    const detail = (body && (body.detail || body.message)) || text.trim() || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as T;
}

// ---- types (only the fields the app reads) ----
export interface VideoFacade {
  platform: string; platform_name: string; video_id: string; url: string;
  embed_url: string; title: string; thumbnail: null;
  loads_on_press: boolean; note: string;
}
export interface MediaUpload {
  id: string; kind: "image" | "video" | "file"; url: string;
  name?: string | null; ai_marked: false;
}
export interface WallPost {
  id: string; profile_id: string; display_name?: string;
  avatar?: string | null; body: string; created_at?: string;
  likes?: number; reason?: string; video?: VideoFacade | null;
  media?: MediaUpload[];
  status?: string; blocked_reason?: string | null;
}
export interface WallComment {
  id: string; body: string; author_id?: string; status?: string;
  created_at?: string;
}
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
  // Spec clauses 2/12: which role the profile worked in, and whether the
  // interactor declared it or the profile read it from the prompt.
  role_context?: { role: string; how: "declared" | "inferred" } | null;
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

// FIG. 800's voiceprint (qrme/voiceprint.py) — permission, enrollment,
// characteristics, print.
export interface VoiceEnrollment {
  samples: number; seconds: number; turns: number;
  mean_turn_seconds: number | null; mean_chars_per_turn: number | null;
  by_source: Record<string, number>;
  ready: boolean; needs: string[];
  threshold: { samples: number; seconds: number };
  method: string;
}
export interface VoiceprintStatus {
  consent: { granted: boolean; own_voice?: boolean; sources?: string[];
             granted_at?: string; note?: string };
  enrollment: VoiceEnrollment | null;
  voiceprint: { id: string; built_at: string; retired_at: string | null;
                active: boolean } | null;
  disclosure: string;
}
// Extract-and-reconstruct: who produced this text, from the text alone.
export interface WatermarkRecovery {
  recovered: boolean; reason?: string;
  profile_id?: string; watermark_id?: string; kind?: string;
  verbatim?: boolean; similarity?: number; best_similarity?: number;
  matched_windows?: number; stored_windows?: number; examined_windows?: number;
  state?: string; disclosure?: string; method?: string;
  display?: { mark: string; label: string } | null;
}

/** A revocable scope token. Phases that read the profile's own material need
 *  one; the backend refuses `research` without it. */
export type Grant = {
  id: string;
  token: string;
  scope: string[];
  revoked: boolean;
};

/** Which phases the owner has authorised the profile to run unattended. */
export type Delegation = {
  delegation: {
    phases?: string[];
    enabled?: boolean;
    grant_id?: string | null;
    [key: string]: unknown;
  } | null;
  phases: string[];
};

/** A run in progress. `awaiting` is what it is stopped on and waiting for a
 *  person to supply; `next_phase` is what it would do if advanced. */
export type Workflow = {
  id: string;
  profile_id: string;
  goal: string;
  plan: string[];
  status: string;
  cursor: number;
  next_phase?: string | null;
  awaiting?: string | null;
  agent?: string | null;
  grant_id?: string | null;
  memory?: unknown;
  created_at: string;
  updated_at: string;
};

export type TaskRunResult = {
  id: string;
  status: string;
  output?: string;
  steps?: unknown[];
  watermark?: unknown;
};

/** A staffed desk. `desk_id` and `desk_token`, not `id`/`owner_token` — the
 *  desk is its own thing, not a profile with a different name. */
// The marketplace. Every field below was read off a running server, not off
// a route signature — see the note on the bindings for the two that would
// have been wrong from reading alone.
export type MarketProfile = {
  profile_id: string; display_name: string; purpose: string;
  tags: string[]; blurb: string; avatar?: string; avatar_kind?: string;
};

export type Listing = {
  id: string; kind: string; title: string; blurb: string; tags: string[];
  area?: string; provider_name?: string; business?: boolean;
  profile_id?: string;
};

export type MarketSearch = {
  query: string; terms: string[]; scope: string;
  locality: string | null; region: string | null;
  results: Listing[]; total: number; hidden_by_place: number;
  /** The backend's own sentence about how it ranked. Shown, not paraphrased. */
  ranking: string;
};

export type MarketAssist = {
  need: string; suggestions: string[]; source: string; ai: boolean;
  /** False, always, so far — and the screen says so. */
  applied: boolean; note: string;
};

export type Locality = { locality: string; region: string | null; listings: number };

export type Place = {
  listing_id: string; locality: string; region: string | null; remote: boolean;
};

export type MarketPrefs = {
  interactor_id: string; locality: string | null; region: string | null;
  scope: string; include_remote: boolean; kinds: string[]; tags: string[];
  updated_at: string | null;
};

export type Offer = {
  listing_id: string; seller_id: string; price: number; currency: string;
  stock: number | null; status: string; created_at: string; sold: number;
  /** The backend states the money is simulated. So does the screen. */
  payment: string;
};

export type Order = {
  id: string; listing_id: string; title: string;
  buyer_id: string; seller_id: string;
  price: number; currency: string; status: string;
  ledger_entry: string; created_at: string; payment: string;
};

// ---------------------------------------------------------------------
// Three two-party surfaces: an agreed exchange, a lent skill, a watch
// party. Every shape below was read off a running server. Four would have
// been wrong from the route signatures alone, and they are the four a
// screen would have crashed on:
//
//   * POST /exchanges/{id}/items returns the whole *exchange*, not the
//     item it created — so the new item's id has to be read out of the
//     returned manifest;
//   * the same is true of POST /watch-parties/{id}/members;
//   * `channel` has two different shapes depending on `open`, which is why
//     ExchangeChannel is a union rather than one type with optionals;
//   * POST /watch-parties/{id}/end returns a little summary of what it
//     shut down, and nothing else that looks like a party.
// ---------------------------------------------------------------------

export type ExchangeItem = {
  id: string; direction: "host_to_guest" | "guest_to_host";
  name: string; kind: string; bytes: number; note: string | null;
  accepted_at: string | null;
  /** The server's own judgement, not a filename guess. */
  runs: boolean;
};

export type Exchange = {
  id: string; desk_id: string | null;
  host_id: string; guest_id: string;
  work: string; industry: string;
  includes: string[]; excludes: string[];
  fee: number; fee_note: string;
  state: "draft" | "proposed" | "signed" | "delivered" | "closed" | "withdrawn";
  created_at: string;
  items: ExchangeItem[];
  /** Names only — the screen lists these before anybody signs. */
  runs_on_your_machine: string[];
  runs_warning: string | null;
  /** What the signatures are actually against. Changes when the manifest does. */
  fingerprint: string;
  /** `matches_current` is the server's own answer to "does this signature
   *  still apply", computed by comparing the stored fingerprint against the
   *  live one. It is not `fingerprint` — that field was written here from the
   *  route signature and does not exist on the wire.
   *
   *  In every state reachable today it is `true`: the manifest cannot be
   *  edited except from `draft`, and `reopen` deletes the signatures on the
   *  way. So it is the backend checking its own invariant rather than
   *  assuming it, and the screen shows it for the same reason — a signature
   *  that had gone stale would be exactly the thing worth seeing. */
  signatures: { party_id: string; signed_at: string;
                matches_current: boolean }[];
  unsigned: string[];
  channel: ExchangeChannel;
  grants: string; does_not_grant: string;
};

/** Two shapes, not one. A closed channel says why; an open one says what. */
export type ExchangeChannel =
  | { open: false; reason: string; unsigned: string[] }
  | { open: true; items: ExchangeItem[]; fingerprint: string;
      auto_download: boolean; note: string };

export type ExchangeVocabulary = {
  industries: string[];
  kinds: { key: string; means: string; runs: boolean }[];
  states: string[];
  directions: string[];
  max_items: number;
  /** The backend's own five sentences. Shown, not paraphrased. */
  rules: string[];
};

export type SkillGrant = {
  id: string; lender_id: string; borrower_id: string;
  surface: string; surface_id: string;
  /** The server's plain-English gloss of `surface`. */
  where: string;
  skill_kind: string; skill_ref: string;
  /** Likewise for `skill_kind`. */
  means: string;
  title: string; note: string;
  fee: number; fee_note: string;
  state: "offered" | "active" | "declined" | "closed";
  active: boolean;
  offered_at: string; accepted_at: string | null;
  closed_at: string | null; closed_by: string | null;
  close_reason: string | null;
  used_count: number;
  recent_uses: SkillGrantUse[];
  /** Both are constants the server states about itself. The screen quotes them. */
  transfers_anything: boolean; either_can_end_it: boolean;
};

export type SkillGrantUse = { what: string; used_at: string; borrower_id: string };

/** What `use` returns — a receipt, not the grant. */
export type SkillGrantReceipt = {
  grant_id: string; skill_kind: string; skill_ref: string; title: string;
  surface: string; surface_id: string;
  copied: boolean; note: string; used: string;
};

export type SkillGrantVocabulary = {
  surfaces: { key: string; means: string }[];
  skill_kinds: { key: string; means: string }[];
  states: string[];
  terms: string[];
};

export type PartyVideo = {
  platform: string; platform_name: string; video_id: string;
  url: string; embed_url: string; title: string;
  thumbnail: string | null; loads_on_press: boolean; note: string;
};

export type PartyMember = {
  member_id: string; kind: "person" | "profile"; role: string;
  display_name: string | null; avatar: string | null;
  /** Travels with every member, so a room can always say who is not a person. */
  synthetic: boolean;
  joined_at: string;
};

export type WatchParty = {
  id: string; post_id: string; host_id: string; title: string | null;
  video: PartyVideo;
  position_s: number; playing: boolean;
  members: PartyMember[];
  people: number; profiles: number;
  created_at: string;
  loads_on_press: boolean;
  /** "the room shares a position, not a player" — the server's sentence. */
  note: string;
};

export type PartyLine = {
  id: string; member_id: string; display_name: string | null;
  kind: string; synthetic: boolean;
  body: string; position_s: number | null; created_at: string;
};

/** What POST /chat returns: the line, plus a moderation verdict on it. */
export type PostedLine = {
  id: string; party_id: string; member_id: string; body: string;
  status: string; blocked_reason: string | null;
};

/** Everything a synthetic profile in the party is allowed to know. The
 *  absences are the point, so they are typed rather than left out. */
export type PartyContext = {
  watching: { title: string; platform: string;
              description_available: boolean;
              transcript_available: boolean };
  position_s: number; playing: boolean;
  recent: { who: string; said: string; at: number | null }[];
  you_have_not_seen_it: boolean;
  /** The literal text that goes into the prompt. Shown so a person can read
   *  what their profile was told, rather than trusting that it was told it. */
  instruction: string;
};

export type PartyEnded = {
  party_id: string; ended: boolean;
  grants_closed: number; microphones_returned: number;
};

// ---------------------------------------------------------------------
// Who a profile is, who may know, and how it ends.
//
// Three of the shapes below are unions rather than one type with optional
// fields, and that is not tidiness — each pair is a genuinely different
// answer, and flattening them would let a screen read a field that is only
// meaningful in the other case.
// ---------------------------------------------------------------------

/** Whether somebody checked, and how well. Two answers, not one shape.
 *
 *  The unverified reply says *why* — an invented person is **unverifiable**
 *  rather than unverified, and the note distinguishes those, because "nobody
 *  checked" said of a fictional character is a category error rather than a
 *  gap.
 *
 *  The verified reply is also what `GET /badge` returns to the public, with
 *  one difference: on an anonymous profile the attestor is dropped and
 *  `attestor_withheld` appears. "Checked by Dr Okafor of St Mary's" narrows an
 *  anonymous author to a city and a workplace. */
export type Verification =
  | { verified: false; real_person: boolean; note: string }
  | { verified: true; real_person: boolean; level: string; rank: number;
      means: string; method: string | null; checked_at: string;
      caveat: string | null;
      /** Present to the owner and on a named profile. */
      attestor?: string;
      /** Present instead, on an anonymous profile, to the public. */
      attestor_withheld?: boolean; note?: string };

/** Whether this profile *could* take the badge. Two answers again: the
 *  blocked one names the sibling that holds it and whether it can be moved,
 *  and the plain one has no `held_by` to read. */
export type Verifiable =
  | { can_verify: true; reason: string }
  | { can_verify: false; reason: string; held_by?: string; movable?: boolean };

export type BadgeMoved = {
  moved: boolean; from: string; verified_profile: string;
  checked_at: string;
  /** "the check itself did not change — only which of your profiles carries
   *  it". The distinction the whole feature turns on. */
  note: string;
};

export type Anonymity = {
  profile_id: string; anonymous: boolean;
  /** The fixed `Anonymous 00000000` when on, the real name when off. */
  shown_as: string;
  withheld: string[];
  /** The half that matters more. Shown with equal weight on the screen. */
  not_withheld: string[];
  reversible: boolean;
  note: string;
  /** Only on a change: what the switch does and does not do retroactively. */
  note_on_change?: string;
};

export type IdentityVocabulary = {
  withheld_when_anonymous: string[];
  never_withheld: string[];
  real_person_kinds: string[];
  /** Weakest first — a ladder, not a menu of alternatives. */
  proofing_levels: { level: string; means: string; needs_attestor: boolean }[];
  rules: string[];
};

export type Sibling = {
  profile_id: string; kind: string; display_name: string;
  shown_as: string; anonymous: boolean;
  verified: boolean;
  /** False for an invented person — which is why the roster can say
   *  "unverifiable" rather than leaving a blank that reads as "not yet". */
  can_be_verified: boolean;
  level: string | null; status: string; created_at: string;
};

export type Emblem = { emblem: string; asset: string; means: string };

export type EmblemSet = {
  profile_id: string; emblem: string; asset: string;
  own_image: boolean; shown: boolean; note: string;
};

export type Avatar = {
  profile_id: string; asset: string | null; silhouette: boolean;
  asset_marked: boolean;
  /** Always displayed, by the product's own rule. */
  watermark: { mark: string; label: string; line: string; custom: boolean;
               always_displayed: boolean; disclosure: string };
  likeness: { real_person: boolean; note: string;
              basis?: string | null; attestor?: string | null;
              revocable?: boolean };
  placeholder: boolean;
};

export type AvatarBrief = {
  handle: string; portrait: string; style: string; prompt?: string;
};

/** What sunsetting did. `archive_key` is non-null only where a vault holds it. */
export type Sunset = {
  status: string; farewells: number; memory: string;
  archive_key: string | null;
};

export type Memorial = {
  profile_id: string; display_name: string; handle: string | null;
  purpose: string; status: string;
  memorial_anchors: unknown[]; relationships_touched: number; note: string;
};

/** The itemised receipt for a deletion — one count per table it emptied.
 *  Typed as an open record because the table list is the backend's business
 *  and will grow; the screen renders whatever came back rather than a fixed
 *  list that would silently stop mentioning a new one. */
export type Deleted = { deleted: Record<string, number> };

// ---------------------------------------------------------------------
// How a profile presents itself, everywhere it is seen: the page it builds,
// the front page a stranger lands on, the physical screens it is shown on,
// and which surfaces it is allowed on at all.
// ---------------------------------------------------------------------

export type Theme = {
  id: string; label: string; bg: string; ink: string; note: string;
};

export type PageCatalog = {
  themes: Theme[]; layouts: string[]; top_friends: number;
  /** Published so an editor can grey out what it knows will be stripped
   *  rather than letting somebody write it and lose it — the backend says so
   *  in its own comment. Nothing was reading them until now. */
  html_tags: string[]; css_properties: string[];
};

export type PageLink = { label: string; url: string };

export type ProfilePage = {
  profile_id: string;
  theme: Theme;
  accent: string | null; layout: string;
  tagline: string | null;
  about: string | null;
  /** Set when moderation held the about text, with the reason, so it can be
   *  fixed rather than silently dropped. Owner's view only. */
  about_blocked: string | null;
  top_friends: unknown[];
  html: string | null;
  /** Tag names the sanitiser removed. The edit still succeeds — so without
   *  showing this, somebody's `<script>` vanishes and the page just quietly
   *  does less than they wrote. */
  html_removed: string[];
  links: PageLink[];
  offers: unknown[];
  feed: unknown[];
};

/** What a stranger lands on. Public, and the AI disclosure is part of it
 *  rather than chrome around it. */
export type Front = {
  profile_id: string; display_name: string; handle: string | null;
  headline: string | null; portrait: string | null;
  ai_disclosure: string;
  verification: Verification;
  skills: unknown[]; experience: unknown[];
  rating: { average: number | null; count: number; note?: string };
  reviews: unknown[];
  talked_with: number; interactions: number; adult: boolean;
};

export type DisplayCatalog = {
  /** `passers_by` is the field that matters: a corridor panel and a screen on
   *  your own desk are not the same risk, and the vocabulary says which is
   *  which rather than leaving a client to guess from the name. */
  kinds: { kind: string; passers_by: boolean; means: string }[];
  sizes: { size: string; means: string }[];
  finishes: { finish: string; means: string }[];
  faces: { face: string; private: boolean; shows: string }[];
  default_faces: string[];
  /** What a fixed screen may never show, each with the reason. Shown on the
   *  screen verbatim — these are the sentences that explain the product's
   *  posture, and a paraphrase would be a worse version of an argument
   *  somebody already made carefully. */
  never: { thing: string; why: string }[];
};

export type Display = {
  id: string; profile_id: string;
  kind: string; label: string; location: string | null;
  size: string; finish: string;
  faces: string[];
  passers_by: boolean;
  /** False after it is taken down — retired, not erased. */
  live: boolean;
  mark: { backing_plate: boolean; why: string; min_contrast: number;
          note: string };
  placed_at: string;
};

export type Desk = {
  desk_id: string;
  desk_token?: string;
  display_name: string;
  trade: string;
  presence: string;
  location?: string | null;
  blurb?: string | null;
  portrait?: string | null;
  rated: boolean;
  designation?: string | null;
  attestation?: unknown;
  human?: unknown;
  ai?: unknown;
  age_wall?: unknown;
  bell?: unknown;
  feed?: unknown;
  join?: unknown;
  room_id?: string | null;
  last_seen?: string | null;
};

export type DeskRing = {
  id?: string;
  caller_id?: string | null;
  note?: string | null;
  acked?: boolean;
  at?: string;
  [key: string]: unknown;
};

export type DeskGuest = {
  id?: string;
  display_name?: string | null;
  note?: string | null;
  state?: string;
  [key: string]: unknown;
};

/** What a viewer sees layered over the stream. `style` is the desk's own
 *  view style, so the overlay matches the room rather than guessing. */
export type DeskOverlay = {
  style: string;
  on_stream: unknown[];
  waiting: unknown[];
  likes: number;
  comments: number;
  shares: number;
  gifts: unknown[];
  gift_total: number;
};

/** The attestation behind "a real person staffs this desk" — who says so, on
 *  what basis, and whether the claim has been burned. */
export type LivePerson = {
  desk_id: string;
  real_person: boolean;
  whose?: string | null;
  owner_id?: string | null;
  designation?: string | null;
  attestor?: string | null;
  attestation_basis?: string | null;
  attested_at?: string | null;
  means?: string | null;
  line?: string | null;
  note?: string | null;
  burned?: boolean;
};

export type DeskBeacon = {
  id: string;
  desk_id: string;
  label: string;
  location?: string | null;
  active: boolean;
  scans: number;
  scan_url: string;
  qr_svg: string;
  created_at: string;
};

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
    // Role-specific context (spec clauses 2/12): advisor | collaborator |
    // operator. Omitted, the profile reads the prompt itself.
    role?: string;
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
  feed: (profileId: string, adult = false) =>
    req<{ posts: WallPost[]; ranked_on: string[] }>(
      `/profiles/${profileId}/feed${adult ? "?adult=true" : ""}`),
  myWall: (profileId: string) =>
    req<{ posts: WallPost[] }>(`/profiles/${profileId}/wall`),
  publishPost: (profileId: string,
                body: { body: string; video_url?: string; video_title?: string;
                        media_ids?: string[] },
                token: string) =>
    req<WallPost>(`/profiles/${profileId}/wall`,
      { method: "POST", body, token }),
  uploadMedia: async (profileId: string, file: File, token: string) => {
    // Raw bytes, not multipart — the backend reads the kind from the bytes;
    // the filename is a display hint only.
    const res = await fetch(getBase() +
      `/profiles/${profileId}/media?filename=${encodeURIComponent(file.name)}`, {
      method: "POST", body: file,
      headers: { authorization: `Bearer ${token}` },
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error((data as { detail?: string }).detail || `upload failed (${res.status})`);
    return data as MediaUpload;
  },
  mediaLimits: () =>
    req<{ image: { max_bytes: number }; video: { max_bytes: number } }>(
      `/media/limits`),
  videoPlatforms: () =>
    req<{ platforms: { key: string; name: string; hosts: string[] }[];
          note: string }>(`/videos/platforms`),
  // `/posts/…`, plural. The audience routes take the *path* segment and map it
  // to a kind (`posts` → `post`), so the singular these used to send reached
  // no route at all and every like, comment and share came back 404.
  likePost: (postId: string, token: string) =>
    req<{ likes?: number }>(`/posts/${postId}/like`, { method: "POST", token }),
  unlikePost: (postId: string, token: string) =>
    req<{ likes?: number }>(`/posts/${postId}/like`, { method: "DELETE", token }),
  postComments: (postId: string) =>
    req<{ comments: WallComment[] } | WallComment[]>(`/posts/${postId}/comments`),
  addComment: (postId: string, body: string, token: string) =>
    req<WallComment>(`/posts/${postId}/comments`,
      { method: "POST", body: { body }, token }),
  sharePost: (postId: string, token: string) =>
    req<unknown>(`/posts/${postId}/share`, { method: "POST", token }),
  marketplace: (tag?: string) =>
    req<{ profile_id: string; display_name: string; purpose?: string;
          blurb?: string; tags: string[]; avatar?: string | null;
          avatar_kind?: "ai" | "real_photo" | null }[]>(
      `/marketplace${tag ? `?tag=${encodeURIComponent(tag)}` : ""}`),
  // Typed off a running server rather than left as `unknown[]`: it answers a
  // bare array of listings, which the marketplace screen renders directly.
  marketplaceListings: () => req<Listing[]>(`/marketplace/listings`),
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
  // The voiceprint, in FIG. 800's order (qrme/voiceprint.py).
  voiceprint: (pid: string) =>
    req<VoiceprintStatus>(`/profiles/${pid}/voiceprint`),
  grantVoiceConsent: (pid: string, body: { own_voice: boolean; sources?: string[]; note?: string }) =>
    req<VoiceprintStatus>(`/profiles/${pid}/voiceprint/consent`, { method: "PUT", body }),
  addVoiceSample: (pid: string, body: { source: string; seconds: number; turns?: number }) =>
    req<{ id: string } & VoiceEnrollment>(`/profiles/${pid}/voiceprint/samples`, { method: "POST", body }),
  buildVoiceprint: (pid: string) =>
    req<VoiceprintStatus>(`/profiles/${pid}/voiceprint`, { method: "POST", body: {} }),
  speakInVoice: (pid: string, text: string) =>
    req<{ basis: string; disclosure: string; watermark: { watermark_id: string } }>(
      `/profiles/${pid}/voiceprint/speak`, { method: "POST", body: { text } }),
  revokeVoiceprint: (pid: string) =>
    req<{ revoked: boolean; samples_deleted: number }>(
      `/profiles/${pid}/voiceprint`, { method: "DELETE" }),
  // Who wrote this? — from the text alone, surviving edits.
  recoverWatermark: (content: string) =>
    req<WatermarkRecovery>("/watermarks/recover", { method: "POST", body: { content } }),
  // ---------------------------------------------------------------------
  // What this profile may do on the owner's behalf, and what it has done.
  // The whole chain — mint a grant, authorise phases, run and steer a
  // workflow — existed in the backend with no caller anywhere.
  // ---------------------------------------------------------------------

  // A grant is the revocable scope a phase reads through. Minting one is the
  // first step of delegation, not a separate feature.
  createGrant: (profileId: string, scope: string[], token: string) =>
    req<Grant>(`/profiles/${profileId}/grants`,
      { method: "POST", body: { scope }, token }),
  revokeGrant: (grantId: string, token: string) =>
    req<{ revoked: boolean }>(`/grants/${grantId}`,
      { method: "DELETE", token }),

  delegation: (profileId: string) =>
    req<Delegation>(`/profiles/${profileId}/delegation`),
  setDelegation: (profileId: string, body: { phases: string[];
    grant_token?: string; enabled?: boolean }, token: string) =>
    req<Delegation>(`/profiles/${profileId}/delegation`,
      { method: "PUT", body, token }),

  workflows: (profileId: string, token: string) =>
    req<Workflow[]>(`/profiles/${profileId}/workflows`, { token }),
  workflow: (profileId: string, workflowId: string, token: string) =>
    req<Workflow>(`/profiles/${profileId}/workflows/${workflowId}`, { token }),
  createWorkflow: (profileId: string, body: { goal: string; plan?: string[];
    grant_token?: string }, token: string) =>
    req<Workflow>(`/profiles/${profileId}/workflows`,
      { method: "POST", body, token }),
  advanceWorkflow: (profileId: string, workflowId: string, token: string) =>
    req<Workflow>(`/profiles/${profileId}/workflows/${workflowId}/advance`,
      { method: "POST", token }),
  resumeWorkflow: (profileId: string, workflowId: string, input: string,
    token: string) =>
    req<Workflow>(`/profiles/${profileId}/workflows/${workflowId}/resume`,
      { method: "POST", body: { input }, token }),
  cancelWorkflow: (profileId: string, workflowId: string, token: string) =>
    req<Workflow>(`/profiles/${profileId}/workflows/${workflowId}/cancel`,
      { method: "POST", token }),

  // The same machinery run by somebody who is not the owner, under the
  // policy the owner set. Kept separate on purpose: these are the runs a
  // person other than the owner started.
  startDelegatedWorkflow: (profileId: string, body: { goal: string;
    interactor_id: string; plan?: string[] }, token: string) =>
    req<Workflow>(`/profiles/${profileId}/delegated-workflows`,
      { method: "POST", body, token }),
  delegatedWorkflow: (profileId: string, workflowId: string, token: string) =>
    req<Workflow>(
      `/profiles/${profileId}/delegated-workflows/${workflowId}`, { token }),
  advanceDelegatedWorkflow: (profileId: string, workflowId: string,
    token: string) =>
    req<Workflow>(
      `/profiles/${profileId}/delegated-workflows/${workflowId}/advance`,
      { method: "POST", token }),
  resumeDelegatedWorkflow: (profileId: string, workflowId: string,
    input: string, token: string) =>
    req<Workflow>(
      `/profiles/${profileId}/delegated-workflows/${workflowId}/resume`,
      { method: "POST", body: { input }, token }),

  tasks: (profileId: string, token: string) =>
    req<TaskRunResult[]>(`/profiles/${profileId}/tasks`, { token }),
  runTask: (profileId: string, body: { kind?: string; topic: string;
    grant_token: string }, token: string) =>
    req<TaskRunResult>(`/profiles/${profileId}/tasks`,
      { method: "POST", body, token }),
  // ---------------------------------------------------------------------
  // Desks: a staffed counter somebody can walk up to. Opening one, saying
  // whether anybody is there, answering the bell, and letting a visitor come
  // up on stream all existed in the backend with no caller.
  // ---------------------------------------------------------------------

  openDesk: (body: { owner_id: string; display_name: string; trade: string;
    attestor: string; basis: string; location?: string; blurb?: string;
    rated?: boolean; view_style?: string }) =>
    req<Desk>("/desks", { method: "POST", body }),

  // Presence is the whole point of a desk: whether a person is actually
  // there. `closed` is not `away` — one says come back later, the other says
  // the counter is shut.
  setDeskPresence: (deskId: string, presence: string, token: string) =>
    req<Desk>(`/desks/${deskId}/presence`,
      { method: "PUT", body: { presence }, token }),
  setDeskPortrait: (deskId: string, asset: string | null, token: string) =>
    req<Desk>(`/desks/${deskId}/portrait`,
      { method: "PUT", body: { asset }, token }),
  setDeskCamera: (deskId: string, url: string | null, token: string) =>
    req<Desk>(`/desks/${deskId}/camera`,
      { method: "PUT", body: { url }, token }),

  // The bell, and the queue of people who rang it.
  deskRings: (deskId: string, token: string, pending = false) =>
    req<{ rings: DeskRing[] }>(`/desks/${deskId}/rings`
      + (pending ? "?pending=true" : ""), { token }),
  ackRing: (deskId: string, ringId: string, token: string) =>
    req<DeskRing>(`/desks/${deskId}/rings/${ringId}/ack`,
      { method: "POST", token }),

  // Asking to come up, and the desk deciding. `guests/me` is the visitor's
  // own way back down, which is theirs to press rather than the desk's.
  deskGuests: (deskId: string, token: string, pending = false) =>
    req<{ guests: DeskGuest[]; on_stream: unknown[] }>(
      `/desks/${deskId}/guests` + (pending ? "?pending=true" : ""), { token }),
  askToComeUp: (deskId: string, body: { display_name?: string; note?: string },
    token: string) =>
    req<DeskGuest>(`/desks/${deskId}/guests`, { method: "POST", body, token }),
  acceptGuest: (deskId: string, reqId: string, token: string) =>
    req<DeskGuest>(`/desks/${deskId}/guests/${reqId}/accept`,
      { method: "POST", token }),
  declineGuest: (deskId: string, reqId: string, token: string) =>
    req<DeskGuest>(`/desks/${deskId}/guests/${reqId}/decline`,
      { method: "POST", token }),
  stepDown: (deskId: string, token: string) =>
    req<{ stepped_down: boolean }>(`/desks/${deskId}/guests/me`,
      { method: "DELETE", token }),

  deskOverlay: (deskId: string, token: string) =>
    req<DeskOverlay>(`/desks/${deskId}/overlay`, { token }),
  deskLivePerson: (deskId: string) =>
    req<LivePerson>(`/desks/${deskId}/live-person`),

  deskBeacons: (deskId: string, token: string) =>
    req<{ beacons: DeskBeacon[] }>(`/desks/${deskId}/beacons`, { token }),
  placeDeskBeacon: (deskId: string, body: { label: string; location?: string },
    token: string) =>
    req<DeskBeacon>(`/desks/${deskId}/beacons`, { method: "POST", body, token }),
  pickUpDeskBeacon: (beaconId: string, token: string) =>
    req<{ picked_up: boolean }>(`/desk-beacons/${beaconId}`,
      { method: "DELETE", token }),

  // ---------------------------------------------------------------------
  // The marketplace. A whole commercial surface — browsing, searching,
  // placing a listing in a town, pricing it, buying it, and the seller's
  // own statement — existed in the backend with no caller at all.
  //
  // Every shape below was read off a running server rather than off the
  // route signatures. Two would have been wrong from reading alone: the
  // offer takes `price`, not `price_cents`, and `settings/{id}` wants an
  // *interactor* id, not a profile's.
  // ---------------------------------------------------------------------

  // Deterministic on purpose: the backend states, in the response, that no
  // model reorders the results. The screen quotes that rather than paraphrasing it.
  marketSearch: (q: string, interactorId?: string) =>
    req<MarketSearch>("/marketplace/search?q=" + encodeURIComponent(q)
      + (interactorId ? `&interactor_id=${interactorId}` : "")),

  // Suggestions for the search box, and nothing else. The reply says so
  // itself — `applied: false` — and the screen shows that, because a
  // suggestion that had quietly filtered would be a different product.
  marketAssist: (need: string) =>
    req<MarketAssist>("/marketplace/assist", { method: "POST", body: { need } }),

  marketLocalities: () => req<Locality[]>("/marketplace/localities"),

  // Where a listing is, if anywhere. Placement is what makes "near me" mean
  // something; without it a listing is everywhere and therefore nowhere.
  placeListing: (listingId: string,
                 body: { locality: string; region?: string; remote?: boolean }) =>
    req<Place>(`/marketplace/listings/${listingId}/place`,
      { method: "PUT", body }),
  unplaceListing: (listingId: string) =>
    req<{ listing_id: string; place: null }>(
      `/marketplace/listings/${listingId}/place`, { method: "DELETE" }),

  // What this buyer wants shown: their town, how far out to look, and
  // whether remote counts. Their own setting, behind their own token.
  marketSettings: (interactorId: string, token: string) =>
    req<MarketPrefs>(`/marketplace/settings/${interactorId}`, { token }),
  setMarketSettings: (interactorId: string, body: Partial<MarketPrefs>,
                      token: string) =>
    req<MarketPrefs>(`/marketplace/settings/${interactorId}`,
      { method: "PUT", body, token }),

  // Pricing establishes the seller — the listing endpoint never needed a
  // token, so the seller is whoever puts the price on, where money starts.
  offer: (listingId: string) =>
    req<Offer>(`/marketplace/listings/${listingId}/offer`),
  setOffer: (listingId: string,
             body: { price: number; currency?: string; stock?: number },
             token: string) =>
    req<Offer>(`/marketplace/listings/${listingId}/offer`,
      { method: "PUT", body, token }),
  withdrawOffer: (listingId: string, token: string) =>
    req<Offer>(`/marketplace/listings/${listingId}/offer`,
      { method: "DELETE", token }),

  // `accept_price` confirms *the* price rather than setting one: a mismatch
  // is refused with the real figure, so a stale screen cannot undercharge.
  purchase: (listingId: string, acceptPrice: number, token: string) =>
    req<Order>(`/marketplace/listings/${listingId}/purchase`,
      { method: "POST", body: { accept_price: acceptPrice }, token }),
  sales: (token: string) => req<{ sales: Order[] }>("/marketplace/sales", { token }),

  // ---------------------------------------------------------------------
  // The agreement two people sign before work changes hands.
  //
  // Every one of these needs the acting party's own token, and that is not
  // ceremony: the router rejects an `actor_id` that does not match the
  // caller, because without that check an anonymous stranger could forge
  // both signatures and accept delivery of an executable on somebody's
  // behalf. The bindings therefore take the token explicitly rather than
  // leaning on an ambient one — a caller that has to pass it cannot
  // accidentally act as the wrong person.
  // ---------------------------------------------------------------------

  exchangeVocabulary: () => req<ExchangeVocabulary>("/exchanges/vocabulary"),

  myExchanges: (partyId: string, token: string) =>
    req<{ party_id: string; exchanges: Exchange[] }>(
      `/parties/${partyId}/exchanges`, { token }),

  exchange: (exchangeId: string, token: string) =>
    req<Exchange>(`/exchanges/${exchangeId}`, { token }),

  proposeExchange: (body: {
    host_id: string; guest_id: string; work: string; industry: string;
    includes?: string[]; excludes?: string[]; fee?: number; desk_id?: string;
  }, token: string) =>
    req<Exchange>("/exchanges", { method: "POST", body, token }),

  // Returns the whole exchange, not the item — read the new item off
  // `.items`. Adding one also drops a signed exchange back to draft, which
  // is why the screen re-renders the whole manifest from this reply rather
  // than appending a row to what it already had.
  addExchangeItem: (exchangeId: string, body: {
    direction: string; name: string; kind: string; bytes?: number; note?: string;
  }, token: string) =>
    req<Exchange>(`/exchanges/${exchangeId}/items`,
      { method: "POST", body, token }),

  removeExchangeItem: (exchangeId: string, itemId: string, token: string) =>
    req<Exchange>(`/exchanges/${exchangeId}/items/${itemId}`,
      { method: "DELETE", token }),

  signExchange: (exchangeId: string, actorId: string, token: string) =>
    req<Exchange>(`/exchanges/${exchangeId}/sign`,
      { method: "POST", body: { actor_id: actorId }, token }),

  reopenExchange: (exchangeId: string, actorId: string, token: string) =>
    req<Exchange>(`/exchanges/${exchangeId}/reopen`,
      { method: "POST", body: { actor_id: actorId }, token }),

  // The one call a transport makes. Kept separate from `exchange()` even
  // though the manifest embeds it, because "may anything move" is the
  // question worth asking on its own.
  exchangeChannel: (exchangeId: string, token: string) =>
    req<ExchangeChannel>(`/exchanges/${exchangeId}/channel`, { token }),

  // One item at a time, by the side receiving it. The server refuses a
  // sender accepting their own item, which is what keeps a signature on an
  // agreement from being a signature on a download.
  acceptExchangeItem: (exchangeId: string, itemId: string, actorId: string,
                       token: string) =>
    req<Exchange>(`/exchanges/${exchangeId}/items/${itemId}/accept`,
      { method: "POST", body: { actor_id: actorId }, token }),

  withdrawExchange: (exchangeId: string, actorId: string, token: string) =>
    req<Exchange>(`/exchanges/${exchangeId}/withdraw`,
      { method: "POST", body: { actor_id: actorId }, token }),

  // ---------------------------------------------------------------------
  // Lending a skill inside a place two people already share.
  //
  // The asymmetry is the feature and the screen shows it: two people to
  // open a grant, either one alone to close it.
  // ---------------------------------------------------------------------

  skillGrantVocabulary: () => req<SkillGrantVocabulary>("/skill-grants/vocabulary"),

  skillGrant: (grantId: string, token: string) =>
    req<SkillGrant>(`/skill-grants/${grantId}`, { token }),

  offerSkill: (body: {
    lender_id: string; borrower_id: string; surface: string;
    surface_id: string; skill_kind: string; skill_ref: string;
    title: string; note?: string; fee?: number;
  }, token: string) =>
    req<SkillGrant>("/skill-grants", { method: "POST", body, token }),

  acceptSkillGrant: (grantId: string, actorId: string, token: string) =>
    req<SkillGrant>(`/skill-grants/${grantId}/accept`,
      { method: "POST", body: { actor_id: actorId }, token }),

  declineSkillGrant: (grantId: string, actorId: string, token: string) =>
    req<SkillGrant>(`/skill-grants/${grantId}/decline`,
      { method: "POST", body: { actor_id: actorId }, token }),

  closeSkillGrant: (grantId: string, actorId: string, reason: string,
               token: string) =>
    req<SkillGrant>(`/skill-grants/${grantId}/close`,
      { method: "POST", body: { actor_id: actorId, reason }, token }),

  // Returns a receipt, not the grant: what was used, where, and the
  // server's own line that nothing was installed. Checked at use rather
  // than at grant time, so closing a grant stops the very next call.
  useSkill: (grantId: string, borrowerId: string, what: string,
             token: string) =>
    req<SkillGrantReceipt>(`/skill-grants/${grantId}/use`,
      { method: "POST", body: { borrower_id: borrowerId, what }, token }),

  skillGrantUses: (grantId: string, token: string) =>
    req<{ grant_id: string; uses: SkillGrantUse[] }>(
      `/skill-grants/${grantId}/uses`, { token }),

  // ---------------------------------------------------------------------
  // Watching a posted video together, with synthetic profiles in the room.
  // ---------------------------------------------------------------------

  watchParty: (partyId: string, token: string) =>
    req<WatchParty>(`/watch-parties/${partyId}`, { token }),

  startWatchParty: (body: { post_id: string; host_id: string; title?: string },
                    token: string) =>
    req<WatchParty>("/watch-parties", { method: "POST", body, token }),

  // Returns the whole party. `kind: "profile"` needs that profile's own
  // owner token — bringing a synthetic profile into a room speaks in its
  // voice, so it is its owner's call and nobody else's.
  joinWatchParty: (partyId: string,
                   body: { member_id: string; kind?: string; role?: string },
                   token: string) =>
    req<WatchParty>(`/watch-parties/${partyId}/members`,
      { method: "POST", body, token }),

  leaveWatchParty: (partyId: string, memberId: string, token: string) =>
    req<WatchParty>(`/watch-parties/${partyId}/members/${memberId}`,
      { method: "DELETE", token }),

  // Moves the room's number. It presses play on nobody's device — which is
  // what keeps the embed promise from being broken twenty times at once.
  seekWatchParty: (partyId: string,
                   body: { host_id: string; position_s: number; playing?: boolean },
                   token: string) =>
    req<WatchParty>(`/watch-parties/${partyId}/seek`,
      { method: "POST", body, token }),

  // The reply carries a moderation `status`, so a line can come back
  // blocked. The screen shows that rather than optimistically appending.
  sayInWatchParty: (partyId: string,
                    body: { member_id: string; body: string;
                            at_position_s?: number },
                    token: string) =>
    req<PostedLine>(`/watch-parties/${partyId}/chat`,
      { method: "POST", body, token }),

  watchPartyChat: (partyId: string, token: string) =>
    req<{ party_id: string; lines: PartyLine[] }>(
      `/watch-parties/${partyId}/chat`, { token }),

  // What a synthetic profile in this party is allowed to know — and, more
  // to the point, what it is not. Worth a door of its own: a person can
  // read the exact instruction their profile was given about the video it
  // has not seen, instead of taking on trust that it was given one.
  watchPartyContext: (partyId: string, token: string) =>
    req<PartyContext>(`/watch-parties/${partyId}/context`, { token }),

  endWatchParty: (partyId: string, hostId: string, token: string) =>
    req<PartyEnded>(`/watch-parties/${partyId}/end`,
      { method: "POST", body: { host_id: hostId, position_s: 0 }, token }),

  // ---------------------------------------------------------------------
  // Who a profile is, who may know, and how it ends.
  //
  // Nineteen routes with no caller — including `DELETE /profiles/{id}`, so
  // the console could make a profile and never remove one.
  //
  // Two routes are deliberately still without a door and stay in the
  // doorless backlog rather than getting a button that lies:
  //
  //   * `POST /profiles/{id}/succeed` requires a *reviewer* token, not the
  //     owner's, and on purpose — succession runs when the owner cannot
  //     authorise anything. A button on the owner's own screen would 403
  //     every time it was pressed;
  //   * `POST /profiles/genesis` is a second creation path (a profile born
  //     from a short interview, which names itself). It belongs in
  //     onboarding, next to the first one, not on a screen about a profile
  //     that already exists.
  // ---------------------------------------------------------------------

  identityVocabulary: () => req<IdentityVocabulary>("/identity/vocabulary"),

  // The roster: every profile this account holds, which one carries the
  // badge, and which of them could. Owner-only — it is the linkage between
  // somebody's separate personas, which is the thing anonymity protects.
  siblings: (profileId: string, token: string) =>
    req<{ owner_id: string; profiles: Sibling[] }>(
      `/profiles/${profileId}/siblings`, { token }),

  verification: (profileId: string, token: string) =>
    req<Verification>(`/profiles/${profileId}/verification`, { token }),

  // Public, and not the same call: on an anonymous profile this drops the
  // attestor. What survives is the part worth having — a real person stands
  // behind this and somebody checked.
  badge: (profileId: string) =>
    req<Verification>(`/profiles/${profileId}/badge`),

  verifiable: (profileId: string, token: string) =>
    req<Verifiable>(`/profiles/${profileId}/verifiable`, { token }),

  // 422 when the claim is malformed, 409 when the one-badge rule refuses.
  // Both carry a sentence worth showing; the screen shows whichever arrives
  // rather than replacing it with one of its own.
  claimVerification: (profileId: string, body: {
    level: string; attestor?: string; method?: string; ref?: string;
  }, token: string) =>
    req<Verification>(`/profiles/${profileId}/verification`,
      { method: "POST", body, token }),

  // Moving is the whole design: at most one of your profiles may be
  // verified, and which one is a decision you can revisit. The check itself
  // is not redone — only where it points.
  moveBadge: (toProfileId: string, token: string) =>
    req<BadgeMoved>(`/profiles/${toProfileId}/verification/move`,
      { method: "POST", body: {}, token }),

  anonymity: (profileId: string, token: string) =>
    req<Anonymity>(`/profiles/${profileId}/anonymity`, { token }),
  setAnonymity: (profileId: string, anonymous: boolean, token: string) =>
    req<Anonymity>(`/profiles/${profileId}/anonymity`,
      { method: "PUT", body: { anonymous }, token }),

  emblems: () => req<{ emblems: Emblem[] }>("/identity/emblems"),
  setEmblem: (profileId: string, emblem: string, token: string) =>
    req<EmblemSet>(`/profiles/${profileId}/emblem`,
      { method: "PUT", body: { emblem }, token }),

  // The bubble, and everything the product says about it: the watermark that
  // is always displayed, and whether a real person's likeness stands behind
  // it under a grant that can be withdrawn.
  avatar: (profileId: string, token: string) =>
    req<Avatar>(`/profiles/${profileId}/avatar`, { token }),
  // Takes `asset`, not a brief — the brief is the prompt you would hand a
  // generator, and generating is not this endpoint's job.
  setAvatar: (profileId: string, asset: string, token: string) =>
    req<Avatar>(`/profiles/${profileId}/avatar`,
      { method: "PUT", body: { asset }, token }),

  avatarBriefs: () =>
    req<{ style: string; briefs: AvatarBrief[] }>("/avatars/briefs"),
  avatarBrief: (handle: string) =>
    req<AvatarBrief>(`/avatars/briefs/${handle}`),

  editProfile: (profileId: string, body: Record<string, unknown>,
                token: string) =>
    req<Profile>(`/profiles/${profileId}`, { method: "PATCH", body, token }),

  // Everything held about this profile, as rows. The point of a door for it
  // is that leaving before you can take your things is not leaving.
  exportProfile: (profileId: string, token: string) =>
    req<Record<string, unknown>>(`/profiles/${profileId}/export`, { token }),

  // Retire it rather than erase it: the profile departs, and what it meant
  // to the people who knew it stays readable.
  sunsetProfile: (profileId: string, token: string) =>
    req<Sunset>(`/profiles/${profileId}/sunset`,
      { method: "POST", body: {}, token }),
  memorial: (profileId: string) =>
    req<Memorial>(`/profiles/${profileId}/memorial`),

  // The other ending. Returns a count per table it emptied — twenty-five of
  // them — which the screen shows rather than summarising, because "deleted"
  // is a claim and an itemised receipt is evidence.
  deleteProfile: (profileId: string, token: string) =>
    req<Deleted>(`/profiles/${profileId}`, { method: "DELETE", token }),

  // ---------------------------------------------------------------------
  // How a profile presents itself, everywhere it is seen.
  //
  // Twelve routes with no caller. `/pages/themes` is the one that stings:
  // it publishes the allowed HTML tags and CSS properties specifically so
  // an editor can grey out what would be stripped — the backend says so in
  // its own comment — and nothing was reading them.
  // ---------------------------------------------------------------------

  pageCatalog: () => req<PageCatalog>("/pages/themes"),

  // Public: the page as a visitor sees it.
  page: (profileId: string) =>
    req<ProfilePage>(`/profiles/${profileId}/page`),

  // The owner's view comes back from the edit, and it carries two things
  // the visitor's does not: `about_blocked` with moderation's reason, and
  // `html_removed`. The edit succeeds either way, so a screen that ignored
  // those would let somebody's markup disappear without a word.
  setPage: (profileId: string, body: {
    theme?: string; accent?: string | null; layout?: string;
    tagline?: string | null; about?: string | null;
    top_friends?: string[]; html?: string | null;
    links?: PageLink[]; show_offers?: boolean;
  }, token: string) =>
    req<ProfilePage>(`/profiles/${profileId}/page`,
      { method: "PUT", body, token }),

  front: (profileId: string) => req<Front>(`/profiles/${profileId}/front`),

  displayCatalog: () => req<DisplayCatalog>("/displays/vocabulary"),

  // Placing one is owner-only, for the same reason placing a beacon is:
  // where a profile is shown is a decision about the profile, and a screen
  // bolted to a wall is a beacon with a plug in it.
  placeDisplay: (profileId: string, body: {
    kind: string; label: string; location?: string | null;
    size?: string; finish?: string; faces?: string[];
  }, token: string) =>
    req<Display>(`/profiles/${profileId}/displays`,
      { method: "POST", body, token }),

  // Owner-only, and the asymmetry with `display()` below is deliberate: the
  // list of somebody's screens is a list of physical places.
  myDisplays: (profileId: string, token: string) =>
    req<{ profile_id: string; displays: Display[] }>(
      `/profiles/${profileId}/displays`, { token }),

  // Public on purpose rather than by oversight — a fixture in a corridor
  // displays to whoever walks past, so what it shows cannot be a secret
  // from them.
  display: (displayId: string) => req<Display>(`/displays/${displayId}`),

  // 422 naming the reason, not the rule: "a conversation on a wall is a
  // conversation with an audience the other person did not agree to".
  setDisplayFaces: (displayId: string, faces: string[], token: string) =>
    req<Display>(`/displays/${displayId}/faces`,
      { method: "PUT", body: { faces }, token }),

  // Returns the display with `live: false` — taken down, not erased.
  removeDisplay: (displayId: string, token: string) =>
    req<Display>(`/displays/${displayId}`, { method: "DELETE", token }),

  surfaces: (profileId: string) =>
    req<{ profile_id: string; surfaces: string[] }>(
      `/profiles/${profileId}/surfaces`),
  setSurfaces: (profileId: string, surfaces: string[], token: string) =>
    req<{ profile_id: string; surfaces: string[] }>(
      `/profiles/${profileId}/surfaces`,
      { method: "PUT", body: { surfaces }, token }),
};
