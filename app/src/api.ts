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

/** A refusal the backend structured on purpose.
 *
 *  Several gates here answer with an *object* rather than a sentence — the
 *  plan gate is the clearest: `{reason, capability, needs, have, price_usd,
 *  period, message, billing}`. That shape exists so a screen can say "this
 *  needs Pro, $130 a month, and the billing is simulated" with a button, and
 *  it was being flattened with `JSON.stringify` and thrown as the message. The
 *  user saw the raw object.
 *
 *  Worth naming as a shape rather than fixing in one place: the backend did
 *  the work of making a refusal actionable, and the transport threw the
 *  structure away at the last step. Every screen that catches an error and
 *  renders `.message` — which is all of them — showed a blob.
 *
 *  So `message` is now the human sentence the object already carried, and the
 *  structure rides along on `detail` for anything that wants to render it
 *  properly. Existing `catch (e) { (e as Error).message }` keeps working and
 *  simply gets better. */
export class RequestError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown) {
    super(RequestError.sentence(detail));
    this.name = "RequestError";
    this.status = status;
    this.detail = detail;
  }

  /** The most human thing in the payload. A structured refusal that carries
   *  its own `message` is quoted; anything else falls back to the JSON, which
   *  is at least honest about being unhandled. */
  private static sentence(detail: unknown): string {
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object") {
      const m = (detail as { message?: unknown }).message;
      if (typeof m === "string" && m) return m;
    }
    return JSON.stringify(detail);
  }
}

/** The plan gate, when that is what refused. Null for anything else, so a
 *  screen can render the upsell properly and otherwise show the sentence. */
export function planGate(err: unknown): PlanGate | null {
  const d = err instanceof RequestError ? err.detail : null;
  if (!d || typeof d !== "object") return null;
  const g = d as Partial<PlanGate>;
  return g.reason === "plan" && typeof g.needs === "string"
    ? (g as PlanGate) : null;
}

export type PlanGate = {
  reason: "plan";
  capability: string;
  needs: string; have: string;
  price_usd: number; period: string;
  message: string;
  /** "simulated — no real funds move". Carried on the refusal itself, so an
   *  upsell cannot show a price without it. */
  billing: string;
};

// ---------------------------------------------------------------------
// What the gate is gating.
//
// Driven, not read off the route signatures. Two things were only
// visible from the running server: `period` is null on the unpaid tiers
// rather than absent or "month", and `visitor` and `free` are separate
// plans that both cost nothing — the first is somebody with no account
// reading a public page, the second is somebody with an account whose
// work sits in the clear. A picker that collapsed them would be offering
// a downgrade nobody asked for.
// ---------------------------------------------------------------------

/** Where an account's work actually lives on this plan. The sentences are
 *  the backend's and are rendered verbatim: `disclosure` is a paragraph
 *  somebody argued carefully about what free means here, and a paraphrase
 *  would be a weaker version of it. Null once there is a vault, because
 *  there is then nothing to disclose. */
export type StoragePosture = {
  plan: string;
  posture: string;
  private: boolean; not_private: boolean;
  title: string; means: string;
  who_can_read: string[];
  encrypted_at_rest: boolean;
  audit_chain: boolean;
  you_hold_a_key: boolean;
  disclosure: string | null;
  /** What this posture will not hold at all, whatever the plan. Each is a
   *  case where the person exposed did not pick the plan. */
  refused_here: string[];
  custody: {
    who: string; held_by: string; means: string;
    transport: string;
    user_holds_a_key: boolean;
    returning_access: boolean;
    goes_through_a_vault: boolean;
    access_record: string;
    erasure: string;
  };
};

export type PlanEntry = {
  plan: string;
  title: string;
  price_usd: number;
  /** Null on visitor and free — they are not billed, rather than billed
   *  monthly at zero. */
  period: string | null;
  means: string;
  includes: string[];
  locked: string[];
  storage: StoragePosture;
};

export type PlanCatalogue = {
  plans: PlanEntry[];
  /** Keyed by the same capability name the plan gate refuses with, so a
   *  refusal naming `builders` can be explained without the console
   *  writing its own glossary. */
  capabilities: Record<string, { from: string; is: string }>;
  the_difference: string;
  billing: string;
};

export type Membership = {
  account_id: string;
  plan: string; title: string;
  price_usd: number; period: string | null;
  includes: string[]; locked: string[];
  billing: string;
  storage: StoragePosture;
};

// ---------------------------------------------------------------------
// Robot bodies.
// ---------------------------------------------------------------------

export type RobotModel = {
  model: string; label: string; maker: string; kind: string;
  capabilities: string[];
  llm_capable: boolean;
};

/** What binding a body answers with. Note it is **not** what the list
 *  returns — the two shapes differ, and the extra fields here are the ones
 *  worth showing once, at the moment of binding. */
export type BoundRobot = {
  id: string; profile_id: string;
  model: string; label: string; maker: string; kind: string;
  name: string;
  llm_provider: string;
  /** What this *model* of body accepts. Not a history, and not what it has
   *  learned — see the block above `robotCatalogue`. */
  commands: string[];
  /** The claim the whole embodiment rests on: the same personality, the
   *  same memory, the same voice, whatever it is speaking through. */
  identity: {
    signature: string; name: string;
    invariant_across: string; guarantee: string;
  };
  note: string;
};

/** The list shape. Carries `status` and `created_at`, which the bind
 *  response does not, and drops the catalogue detail, which it does. */
export type RobotRow = {
  id: string; profile_id: string;
  model: string; name: string;
  llm_provider: string;
  status: string;
  created_at: string;
  commands: string[];
};

/** A task module installed from a pack. `procedure` is rendered verbatim:
 *  every one of them names what the body will *not* do — "reminders only:
 *  never dispense", "companionship, not care" — and that is the sentence
 *  somebody pointing a robot at a relative needs to read. */
export type RobotSkill = {
  task: string; title: string; procedure: string;
  pack_id: string; pack_title: string;
};

export type RobotCommandResult = {
  robot_id: string; command: string;
  status: string; action: string;
  arg: string | null;
  said?: string;
};

export type RobotCommandEntry = {
  id: string; robot_id: string;
  command: string; arg: string | null;
  result: Record<string, unknown>;
  created_at: string;
};

export type SteeringDial = {
  name: string; group: string; label: string;
  low: string; high: string;
  default: number; min: number; max: number;
  adult_only: boolean;
};

export type RobotSteering = {
  subject: string; subject_id: string;
  dials: SteeringDial[];
  values: Record<string, number>;
  /** What the dials actually do to a body, derived rather than stored:
   *  pace becomes motion_eagerness, autonomy becomes initiative,
   *  assertiveness becomes firmness. Showing it is the difference between
   *  a slider and an explanation. */
  behavior_profile: Record<string, number>;
};

/** The PUT answers without `dials` — values and the derived profile only. */
export type RobotSteeringSet = {
  subject: string; subject_id: string;
  values: Record<string, number>;
  behavior_profile: Record<string, number>;
};

// ---------------------------------------------------------------------
// Rated placement: marketing an adult-mode profile at an adult venue.
// ---------------------------------------------------------------------

export type Venue = {
  key: string; name: string;
  url: string | null;
  kind: string;
  /** `profile`, `beacon`, or both — what this venue will actually carry. */
  hosts: string[];
  blurb: string;
  age_wall: boolean;
  /** Rendered verbatim on the screen. The same sentence on every venue,
   *  and the point of the feature: the wall does not move to the venue. */
  note: string;
};

export type PlacementMade = {
  placement_id: string;
  venue: { key: string; name: string; url: string | null; hosts: string[] };
  beacon_id: string;
  /** The JSON surface existing clients read. */
  summon_url: string;
  /** What the printed QR encodes and where a phone camera lands. This is
   *  the one to publish; they are easy to mix up. */
  scan_url: string;
  /** A path on this API, not the markup — `<img src>` it. */
  qr_svg: string;
  /** Null until the profile has claimed one. */
  handle: string | null;
  rated: boolean;
  note: string;
};

/** The list shape, which carries the counts and **not** the urls or the QR
 *  path. Those are derivable from `beacon_id`, and a screen that assumed
 *  the create shape came back here would render blanks. */
export type PlacementRow = {
  id: string; venue: string; venue_name: string;
  beacon_id: string;
  label: string;
  created_at: string;
  scans: number;
  active: boolean;
};

export type PlacementAnalytics = {
  profile_id: string;
  venues: {
    placement_id: string; venue: string; venue_name: string;
    label: string; active: boolean;
    scans: number;
    /** The split that matters: `walled` reached the age wall, `verified`
     *  got through it. */
    walled: number; verified: number;
    by_day: { day: string; scans: number }[];
  }[];
  /** Scans that arrived at the profile without going through a placement. */
  direct: { walled: number; verified: number };
  funnel: {
    resolutions: number; verified_views: number; unique_chatters: number;
    verified_rate: number;
    /** **Null**, not zero, when nothing has got through the wall yet —
     *  there is no rate to state. A screen calling `.toFixed()` on it
     *  without checking prints nonsense. */
    chat_rate: number | null;
  };
};

export type PlacementCustody = Record<string, unknown>;

// ---------------------------------------------------------------------
// The owner's workshop.
// ---------------------------------------------------------------------

/** A profile's dials. Same catalogue as a robot's, plus one difference the
 *  read carries and the robot's does not: `adult_mode`, which is what
 *  decides whether the intimacy dial exists at all. */
export type ProfileSteering = {
  subject: string; subject_id: string;
  dials: SteeringDial[];
  values: Record<string, number>;
  adult_mode: boolean;
};

/** The write answers without the catalogue, and without a body's derived
 *  `behavior_profile` — a fourth shape across the two steering surfaces. */
export type ProfileSteeringSet = {
  subject: string; subject_id: string;
  values: Record<string, number>;
  adult_mode: boolean;
};

export type SourceItem = {
  id: string; profile_id: string;
  kind: string;
  title: string | null;
  /** Null once a vault holds it — the content left and only the reference
   *  stayed. Present and readable means it is sitting in the clear, which
   *  is the free tier's posture and worth showing rather than implying. */
  content: string | null;
  pdi_key: string | null;
  pack_id: string | null;
  created_at: string;
};

export type SourceAdded = {
  id: string; kind: string;
  title: string | null;
  /** The same fact as `pdi_key`, said from the other end. */
  vaulted: boolean;
};

/** What comes back: the domain and an id, with no name. Showing who the
 *  specialist *is* means fetching that profile — the join is the console's
 *  job, not the route's. */
export type Specialist = {
  domain: string;
  specialist_profile_id: string;
};

export type SpecialistSet = Specialist & { profile_id: string };

/** `period`, not `years`. Sending the latter used to save a row with no
 *  dates and answer 200; the model is strict now. */
export type ExperienceEntry = {
  id?: string;
  title: string;
  org?: string | null;
  period?: string | null;
  detail?: string | null;
};

/** A local fine-tune. Every field after the counts is a claim about what
 *  did *not* happen, which is the reason this feature reads the way it
 *  does — rendered rather than summarised. */
export type FinetuneRun = {
  id: string;
  interactors: number;
  messages_processed: number;
  engagement_avg: number | null;
  external_transmission: boolean;
  computed: string;
  offline_mode: boolean;
  sealed_in_vault: boolean;
  vault_key: string | null;
};

export type Embodiment = {
  name: string; kind: string;
  /** False for a speaker or a screen that only relays. The distinction
   *  matters: one of them can hold a conversation and one cannot. */
  has_llm: boolean;
};

/** The public verification surface. Anybody who meets this profile in any
 *  form can fetch this and check the signature is the same one. */
export type EmbodimentConsistency = {
  profile_id: string;
  signature: string;
  name: string;
  invariant_across: string;
  guarantee: string;
  embodiments: Embodiment[];
  surfaces: string[];
};

export type Perception = {
  id: string;
  recognized: Record<string, string[]>;
  recognized_count: number;
  goal: string | null;
  guidance: string;
  /** Every piece of generated guidance is marked, with a path to check it
   *  against. Drawn beside the words rather than under a disclosure link. */
  watermark: {
    watermark_id: string; kind: string; profile_id: string;
    content_sha256: string; issued_at: string; disclosure: string;
    display: { mark: string; label: string; line: string;
               custom: boolean; always_displayed: boolean;
               disclosure: string };
    verify: string;
  };
  status: string;
};

// ---------------------------------------------------------------------
// The profile working for its owner.
// ---------------------------------------------------------------------

/** Triage answers with the *reason* each item survived, and the score it
 *  scored. The ranking is deliberately transparent — a pile sorted by a
 *  number nobody can see is a pile somebody has to re-check by hand. */
export type TriageResult = {
  reviewed: number;
  kept: { id: string; reason: string; preview: string }[];
  discarded_ids: string[];
  criteria: string | null;
};

export type MarkDisplay = {
  mark: string; label: string; line: string;
  custom: boolean; always_displayed: boolean; disclosure: string;
};

export type Mark = {
  watermark_id: string; kind: string; profile_id: string;
  content_sha256: string; issued_at: string; disclosure: string;
  display: MarkDisplay;
  verify: string;
};

export type Proofread = {
  original: string;
  edited: string;
  watermark: Mark;
  /** Concrete and mechanical — "add end punctuation" — beside the rewrite
   *  rather than instead of it. */
  suggestions: string[];
  status: string;
};

export type CreativeWork = {
  id: string; kind: string; moment: string; content: string;
  watermark: Partial<Mark> & { watermark_id: string; display: MarkDisplay };
  /** Present on the list, absent on the create. */
  profile_id?: string;
  created_at?: string;
};

export type Wearable = {
  id: string; name: string; kind: string;
  transport: string;
  faces: string[];
  paired_at: string;
  /** Set once unpaired. The row survives — a device that was on somebody's
   *  wrist is a fact about the past, not a row to delete. */
  revoked_at: string | null;
  paired: boolean;
};

export type WearableView = {
  profile_id: string;
  wearables: Wearable[];
  /** What each watch face shows, in the backend's words. */
  faces: Record<string, string>;
  kinds: Record<string, string>;
  /** Room-facing microphones, each with the paragraph saying why it cannot
   *  be paired. Rendered verbatim: the argument is that the people who walk
   *  into the room did not agree to anything. */
  refused: Record<string, string>;
};

export type Review = {
  id: string; rating: number;
  body: string | null;
  author_id: string;
  created_at: string;
  edited: boolean;
};

export type ReviewsView = {
  profile_id: string;
  /** `average` and `distribution` are absent until somebody has reviewed —
   *  the empty case carries a `note` instead, and the screen shows it. */
  rating: {
    average: number | null; count: number;
    note?: string;
    distribution?: Record<string, number>;
  };
  reviews: Review[];
};

export type ThreadMessage = {
  id: string; role: string; content: string; status: string;
  created_at: string;
  edited: boolean;
  edit_count: number;
  /** The interesting one: a reply written before the message above it was
   *  changed. Marked rather than hidden, because a conversation that
   *  silently rewrote itself would be worse than one that admits the
   *  answer is to an older question. */
  answers_stale_text: boolean;
};

export type ThreadView = {
  profile_id: string; interactor_id: string;
  messages: ThreadMessage[];
};

export type MessageRevision = Record<string, unknown>;

export type UploadedMedia = {
  id: string; kind: string; url: string;
  name: string | null;
  bytes: number;
  /** False for a photograph somebody took. Authentic media is never
   *  AI-marked, which is the whole point of the mark meaning something. */
  ai_marked: boolean;
};

/** What the credential says about itself. */
export type WatermarkRecord = {
  watermark_id: string;
  valid: boolean;
  kind: string; profile_id: string;
  content_sha256: string; issued_at: string; disclosure: string;
  display: MarkDisplay;
};

/** And what it says about a piece of content you hand it.
 *
 *  `valid` and `content_match` answer different questions and **can
 *  disagree**: a real credential whose content has since been altered comes
 *  back `valid: true, content_match: false`, with `note` saying so. A screen
 *  reporting `valid` alone would tell somebody the thing in front of them is
 *  genuine at the exact moment the server said it had been changed. */
export type WatermarkVerdict = WatermarkRecord & {
  content_match: boolean;
  note?: string;
};

// ---------------------------------------------------------------------
// Referrals.
// ---------------------------------------------------------------------

export type Provider = {
  id: string; name: string; area: string;
  location: string | null; contact: string | null;
  business: boolean;
  created_at?: string;
};

/** A match. `match` says in words how it matched rather than scoring it —
 *  a number would imply a precision the data does not have, and expertise
 *  filters while geography only ranks. A cardiologist two streets away is
 *  not a substitute for a psychiatrist. */
export type Clinician = Provider & {
  in_your_area: boolean;
  match: string;
};

export type ReferralPackage = {
  user: string; clinician: string; area: string;
  /** Rendered verbatim, and the most important line in the package: the
   *  thing that had the conversation is an AI profile, not a clinician,
   *  and nothing in it is a diagnosis. */
  specialist: { name: string; synthetic: boolean; note: string };
  recent_exchange: { role: string; content: string }[];
};

export type ReferralPrepared = {
  referral_id: string;
  clinician: string; area: string;
  /** What would go. Shown before anything is signed — the point of a
   *  separate prepare step is that somebody reads this first. */
  package: ReferralPackage;
  display_text: string;
  sign: {
    envelope_id: string;
    challenge: string;
    payload: Record<string, unknown>;
    display_text: string;
  };
};

export type ReferralReleased = {
  id: string;
  /** Opens it, once. Not the same string as the reply token, which does
   *  not exist yet. */
  token: string;
  one_time: boolean;
  signature_id: string;
  signed_by: { account_id: string; name: string; proofing_level: string };
  meaning: string;
};

export type ReferralOpened = {
  id: string;
  package: ReferralPackage;
  signature_id: string;
  /** Arrives only here, when the link is spent. The clinician answers with
   *  this, not with the token they opened it with. */
  reply_token: string;
  reply_note: string;
  note: string;
};

export type ReferralReplied = {
  id: string; referral_id: string;
  sealed: boolean;
  note: string;
};

export type ReferralHistory = {
  id: string; provider_id: string;
  released: boolean;
  opened_at: string | null;
  signature_id: string | null;
  created_at: string;
};

export type ClinicalNote = {
  id: string;
  from: string;
  at: string;
  content: string;
};

export type SigningCredential = {
  id: string; account_id: string;
  credential_id: string; aaguid: string; alg: number;
  proofing_level: string;
  proofing_method: string | null;
  proofing_attestor: string | null;
  display_name: string;
  backup_eligible: boolean; backed_up: boolean;
  /** False for a passkey that syncs between devices, which is why it
   *  cannot reach the high tier — the tier wants a key that stayed put. */
  device_bound: boolean;
  created_at: string;
  revoked_at: string | null;
  /** The visible consequence of the proofing level, and what the screen
   *  shows instead of explaining the tiers. */
  can_sign: string[];
};

export type Certificate = {
  signature_id: string;
  printed_name: string;
  signed_at: string;
  meaning: string;
  document_sha256: string;
  /** The bytes the signer actually read, kept beside the hash of them —
   *  a signature over a document nobody saw is a signature over nothing. */
  what_was_shown: string;
  identity_verified_as: string;
  tier: string;
  valid: boolean;
  verify_at: string;
  standard: string;
};

export type PlacementRemoved = {
  placement_id: string;
  removed: boolean;
  beacon_id: string;
  /** False afterwards: the beacon is deactivated, not deleted, so a QR
   *  already printed at the venue stops resolving rather than pointing
   *  somewhere new. */
  beacon_active: boolean;
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
    const detail = (body && (body.detail ?? body.message)) ?? text.trim()
      ?? res.statusText;
    throw new RequestError(res.status, detail);
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

// ---------------------------------------------------------------------
// What is live in a shared place: a camera running, a lent microphone, a
// face drawn over one.
//
// One posture runs through all three, and the screen is built on it —
// whatever you put between yourself and the people around you, they are
// told. Every type below therefore carries the backend's own sentences
// rather than a flag the console would have to caption itself.
// ---------------------------------------------------------------------

/** The six things a viewer can never do. Rendered verbatim: this is the
 *  product's promise about a live camera, argued once, carefully. */
export type CameraNever = {
  camera_control: string; capture_trigger: string; other_cameras: string;
  location: string; background_start: string; silent_run: string;
};

/** Who is in shot, and whose problem that is. `why_it_is_yours` is the
 *  honest part: the platform cannot see the room, so it declines to promise
 *  anything about who walked into it. */
export type Bystanders = {
  subject: string; risk: string;
  we_cannot: string; you_can: string; why_it_is_yours: string;
};

export type CameraVocabulary = {
  subjects: Record<string, { means: string; bystander_risk: string }>;
  /** `may_watch[subject][viewer_kind]`. The one `false` is a profile
   *  watching a person, and `refusals.profile_on_person` says why at
   *  length. */
  may_watch: Record<string, Record<string, boolean>>;
  viewers: string[];
  surfaces: Record<string, string>;
  never: CameraNever;
  max_minutes: number; default_minutes: number;
  records_by_default: boolean;
  refusals: Record<string, string>;
  bystanders: Bystanders;
};

export type CameraSession = {
  id: string; holder_id: string;
  surface: string; surface_id: string;
  subject: string; subject_means: string;
  viewer_kind: string; viewer_id: string;
  minutes: number; recording: boolean;
  bystanders: string | null; note: string | null;
  state: string; live: boolean;
  opened_at: string; ended_at: string | null; ended_by: string | null;
  never: CameraNever;
  bystanders_note: Bystanders;
};

/** What the people in a place are told about cameras in it. */
export type CameraDisclosure = {
  surface: string; surface_id: string;
  live: unknown[]; any_live: boolean; any_recording: boolean;
  note: string;
};

export type MicVocabulary = {
  personal: string[];
  /** Room-pointed devices, each with the same reason: "it is pointed at the
   *  room, not at you — it would pick up the people around you, and their
   *  voices are not yours to lend." */
  refused: { kind: string; why: string }[];
  gain_levels: { level: string; describes: string; reaches_others: boolean }[];
  room_gain: string; voice_focus: boolean; rules: string[];
};

export type MicPlaces = {
  /** Which surfaces can take a lent microphone, and why each qualifies. */
  places: { surface: string; why: string }[];
  /** Rooms are excluded here and lend through their own route — the reply
   *  says so, and the refusal on a wrong surface repeats it. */
  room: string; test: string; rules: string[];
};

export type LentMic = {
  id: string; room_id?: string;
  device: string; mic_type: string;
  lending: boolean; gain: string; capped: boolean; voice_focus: boolean;
  /** Ends with "Everyone in the room is shown that you lent it." */
  note: string;
};

export type MicsHere = {
  room_id?: string; surface?: string; surface_id?: string;
  microphones_lent: { interactor_id: string; device: string;
                      mic_type: string; gain: string; hears: string;
                      since: string }[];
  gain: string; voice_focus: boolean; note: string;
};

export type OverlayCatalogue = {
  kinds: { kind: string; covers_face: boolean; means: string }[];
};

export type Overlay = {
  id: string; interactor_id: string;
  surface: string; surface_id: string;
  kind: string; title: string; asset: string | null;
  covers_face: boolean; source: string | null;
  background_generated: boolean;
  /** "not their face — Fox, drawn over the camera in real time. A real
   *  person is underneath." The sentence other people in the place see. */
  disclosure: string;
  since: string; wearing?: boolean;
};

export type OverlaysHere = {
  surface: string; surface_id: string;
  overlays: Overlay[];
  /** "…every one of them is named as wearing it." */
  note: string;
};

/** Whose place this is. Small, and the point is `is` — "the host". */
export type WhosePlace = {
  surface: string; surface_id: string; account_id: string;
  display_name: string | null; handle: string | null; is: string;
};

// ---------------------------------------------------------------------
// Contesting a profile that depicts you, and holding what one says.
//
// The most consequential surface in the product, and it had no door. A
// real person or their estate can object; opening one restricts the
// profile *immediately*, before any review, and the two consent-basis
// shortcuts terminate it outright.
// ---------------------------------------------------------------------

/** What opening an objection did. `prior_status` is the promise that a
 *  dismissal is reversible: the profile goes back to whatever it was,
 *  active or a departed memorial. */
export type ObjectionOpened = {
  id: string; profile_id: string;
  status: string;
  /** `restricted`, immediately — public surfaces off, no new interactors. */
  profile_status: string;
  prior_status: string;
  note: string;
};

/** The public status check, for the objecting party — who may have no
 *  account at all. `objector_ref` comes back so they can confirm it is
 *  their case without having to be logged in as anybody. */
export type ObjectionStatus = {
  id: string; profile_id: string; status: string;
  reattested: boolean; objector_ref: string;
};

export type ObjectionEvent = {
  id: string; event: string; actor: string;
  detail: Record<string, unknown>;
  /** Whether this event was sealed into the PDI vault. PDI hash-chains
   *  every write, so a sealed copy is independently tamper-evident. */
  sealed: boolean; pdi_key: string | null;
  at: string;
};

export type ObjectionAudit = {
  objection_id: string; profile_id: string; status: string;
  /** False when no vault is configured — and the screen says so, because
   *  "tamper-evident" is a claim that depends on it. */
  vault_backed: boolean;
  events: ObjectionEvent[];
};

/** What any of resolve / withdraw / revoke returns. */
export type ObjectionOutcome = {
  id: string; status: string; profile_status: string;
};

export type HeldMessage = {
  id: string; profile_id: string; interactor_id: string;
  role: string; content: string;
  status: string;
  /** Why it is waiting — "owner approval required", or a moderation flag. */
  flag_reason: string | null;
  watermark_id: string | null;
  created_at: string;
};

// ---------------------------------------------------------------------
// The guide itself: the walkthrough, the help index, and the pane the
// helper lives in.
//
// The walkthrough is written prose that works with no model configured,
// it names the screens each step is about, and a test asserts every screen
// in the gallery is claimed by some lesson — so it cannot quietly fall
// behind the app. All of it, and no way for anybody to take it.
// ---------------------------------------------------------------------

export type Lesson = {
  key: string; chapter: string; title: string;
  what: string; try_it: string;
  mode: string;
  /** The binding to the gallery. `/tutorial/for-screen/{n}` is the same
   *  relation read the other way. */
  screens: number[];
};

export type Walkthrough = {
  /** Why the guide has no name and no face — shown, because on a platform
   *  of synthetic people a guide with a persona would be the first thing
   *  you met that was not marked. */
  guide: string;
  chapters: { chapter: string; steps: Lesson[] }[];
};

export type Progress = {
  learner_id: string; guide: string;
  /** Where they are now. Null once finished. */
  step: Lesson | null;
  done: number; total: number; finished: boolean;
  note: string;
};

export type HelpTopics = { topics: string[]; disclosure: string };

export type DockFaces = {
  faces: Record<string, string>;
  /** What the dock will not carry, with the reason. `control` is refused
   *  because assist/halt/approve are *actions* and the dock does not act —
   *  it floats over the thing those buttons would stop. */
  refused: Record<string, string>;
  corners: Record<string, string>;
  states: Record<string, string>;
};

export type DockRoute = {
  face: string; screen: number; path: string; title: string;
  opens_dock_face: string;
};

export type DockSettings = {
  profile_id: string; corner: string; state: string;
  face: string; faces: string[];
  platform: string;
  /** False until the owner has chosen — so a screen can tell a default
   *  from a decision. */
  set: boolean;
  surface: string | null;
  wanted: string;
  /** Capped rather than overridden on a surface being transmitted. `why`
   *  carries the reason when it is. */
  tucked: boolean; why: string | null;
};

export type DockFace = {
  face: string; shows: string;
  profile_id: string; surface: string | null; surface_id: string | null;
  route: DockRoute;
  /** Always false. The dock shows and never acts. */
  acts: boolean;
  box: { width: number; height: number; handle: number; inset: number };
  /** The keys of what may never appear in the pane. */
  never: string[];
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

  // ---------------------------------------------------------------------
  // What is live in a shared place.
  //
  // Twenty routes with no caller: a camera being shared, a microphone lent
  // to the profiles in a room, a face drawn over a camera. Three features
  // with one posture — whatever you put between yourself and the people
  // around you, they are told — and none of them reachable.
  // ---------------------------------------------------------------------

  cameraVocabulary: () => req<CameraVocabulary>("/camera/vocabulary"),

  // Per subject kind, because the honest answer differs: a boiler has no
  // face, a room full of people does.
  bystanders: (subject: string) =>
    req<Bystanders>(`/camera/bystanders/${subject}`),

  // 422 with a paragraph when a profile is asked to watch a person. The
  // screen shows that paragraph rather than "not allowed" — it is the
  // reasoning, and it is the part worth reading.
  openCamera: (body: {
    holder_id: string; viewer_id: string; viewer_kind: string;
    subject: string; surface: string; surface_id: string; minutes?: number;
  }, token: string) =>
    req<CameraSession>("/camera/sessions", { method: "POST", body, token }),

  cameraSession: (sessionId: string, token: string) =>
    req<CameraSession>(`/camera/sessions/${sessionId}`, { token }),

  // Returns a bare array. The holder's own list, and the reason it exists
  // is `never.silent_run`: there is no state where a session is on and not
  // visible to the person holding the phone.
  liveCameras: (holderId: string, token: string) =>
    req<CameraSession[]>(`/camera/live/${holderId}`, { token }),

  closeCamera: (sessionId: string, actorId: string, token: string) =>
    req<CameraSession>(`/camera/sessions/${sessionId}/close`,
      { method: "POST", body: { actor_id: actorId }, token }),

  // What the people in a place are told. The other half of the promise —
  // a session the room cannot see would make the rest of it decoration.
  cameraDisclosure: (surface: string, surfaceId: string, token: string) =>
    req<CameraDisclosure>(`/camera/disclosure/${surface}/${surfaceId}`,
      { token }),

  micVocabulary: () => req<MicVocabulary>("/microphones/vocabulary"),

  // Which surfaces can take one, and why each qualifies: the other people
  // present must have a member list and somewhere to be shown the
  // disclosure. Rooms are excluded and lend through their own route.
  micPlaces: () => req<MicPlaces>("/microphones/places"),

  lendMicHere: (surface: string, surfaceId: string,
                interactorId: string, token: string) =>
    req<LentMic>(`/places/${surface}/${surfaceId}/microphone`,
      { method: "POST", body: { interactor_id: interactorId }, token }),
  micsHere: (surface: string, surfaceId: string, token: string) =>
    req<MicsHere>(`/places/${surface}/${surfaceId}/microphone`, { token }),
  takeBackMicHere: (surface: string, surfaceId: string,
                    interactorId: string, token: string) =>
    req<{ lending: boolean; id: string }>(
      `/places/${surface}/${surfaceId}/microphone`,
      { method: "DELETE", body: { interactor_id: interactorId }, token }),

  lendMicInRoom: (roomId: string, interactorId: string, token: string) =>
    req<LentMic>(`/rooms/${roomId}/mic`,
      { method: "POST", body: { interactor_id: interactorId }, token }),
  micsInRoom: (roomId: string, token: string) =>
    req<MicsHere>(`/rooms/${roomId}/mic`, { token }),
  takeBackMicInRoom: (roomId: string, interactorId: string, token: string) =>
    req<{ lending: boolean; id: string }>(
      `/rooms/${roomId}/mic/${interactorId}`, { method: "DELETE", token }),

  overlayCatalogue: () => req<OverlayCatalogue>("/overlays/catalogue"),

  wearOverlay: (surface: string, surfaceId: string, body: {
    interactor_id: string; kind: string; title: string;
  }, token: string) =>
    req<Overlay>(`/places/${surface}/${surfaceId}/overlay`,
      { method: "POST", body, token }),
  overlaysHere: (surface: string, surfaceId: string, token: string) =>
    req<OverlaysHere>(`/places/${surface}/${surfaceId}/overlay`, { token }),
  takeOffOverlay: (surface: string, surfaceId: string,
                   interactorId: string, token: string) =>
    req<{ wearing: boolean; id: string }>(
      `/places/${surface}/${surfaceId}/overlay`,
      { method: "DELETE", body: { interactor_id: interactorId }, token }),

  whosePlace: (surface: string, surfaceId: string, token: string) =>
    req<WhosePlace>(`/places/${surface}/${surfaceId}/whose`, { token }),

  // ---------------------------------------------------------------------
  // Contesting a profile, and holding what one says.
  //
  // Nine routes with no caller, including the takedown path for a product
  // whose whole subject is synthetic people who can be mistaken for real
  // ones. A person depicted by a profile had no way to say so from here.
  // ---------------------------------------------------------------------

  // Public, and deliberately so: the objecting party need not own an
  // account. Somebody who has just found a profile of themselves should
  // not have to sign up to the thing depicting them in order to object.
  //
  // `objector_ref` is an out-of-band proof-of-identity reference, not a
  // login — the identity check happens elsewhere and this points at it.
  openObjection: (body: {
    profile_id: string; objector_ref: string; reason?: string;
  }) => req<ObjectionOpened>("/objections", { method: "POST", body }),

  objection: (objectionId: string) =>
    req<ObjectionStatus>(`/objections/${objectionId}`),

  // Owner- or reviewer-gated, because it quotes the objector's reason.
  objectionAudit: (objectionId: string, token: string) =>
    req<ObjectionAudit>(`/objections/${objectionId}/audit`, { token }),

  // Reviewer-gated. `uphold` terminates the profile and erases its
  // content; `dismiss` restores whatever it was before.
  resolveObjection: (objectionId: string, outcome: "uphold" | "dismiss",
                     token: string) =>
    req<ObjectionOutcome>(`/objections/${objectionId}/resolve`,
      { method: "POST", body: { outcome }, token }),

  // The two shortcuts that bypass review entirely, because the standing
  // party's rights override preservation. Both terminate immediately, even
  // mid-review, and each applies to exactly one consent basis — the
  // refusal names the profile's actual basis when it does not match.
  withdrawConsent: (objectionId: string) =>
    req<ObjectionOutcome>(`/objections/${objectionId}/withdraw`,
      { method: "POST", body: {} }),
  revokeAuthorization: (objectionId: string) =>
    req<ObjectionOutcome>(`/objections/${objectionId}/revoke`,
      { method: "POST", body: {} }),

  // The owner's own queue: what this profile said that is waiting on them.
  // A bare array, not a wrapper.
  moderationQueue: (profileId: string, token: string) =>
    req<HeldMessage[]>(`/profiles/${profileId}/moderation/queue`, { token }),
  approveMessage: (messageId: string, token: string) =>
    req<{ id: string; status: string }>(`/moderation/${messageId}/approve`,
      { method: "POST", body: {}, token }),
  rejectMessage: (messageId: string, token: string) =>
    req<{ id: string; status: string }>(`/moderation/${messageId}/reject`,
      { method: "POST", body: {}, token }),

  // ---------------------------------------------------------------------
  // The guide itself.
  //
  // Twelve routes with no caller, and this is the set it is least
  // comfortable to have found: the walkthrough that teaches somebody where
  // everything in the product lives had no way to be taken. A written
  // lesson for every screen, a test asserting every drawing in the gallery
  // is claimed by one of them, and no door.
  //
  // The console already had `api.help(question)` — the box you type a
  // question into. What was missing is the other half, for the person who
  // does not yet know what to ask.
  // ---------------------------------------------------------------------

  walkthrough: () => req<Walkthrough>("/tutorial"),
  lesson: (key: string) => req<Lesson>(`/tutorial/steps/${key}`),

  // The gallery relation, read from the screen end: what explains this
  // drawing. It is what makes a "what am I looking at" button possible.
  lessonForScreen: (screen: number) =>
    req<Lesson>(`/tutorial/for-screen/${screen}`),

  // `lesson`, not `key` — the field is named for what it holds rather than
  // for its role in the record, and reading the route signature would have
  // got this wrong.
  startWalkthrough: (learnerId: string, lesson: string) =>
    req<Progress>("/tutorial/start",
      { method: "POST", body: { learner_id: learnerId, lesson } }),
  finishLesson: (learnerId: string, lesson: string) =>
    req<Progress>("/tutorial/done",
      { method: "POST", body: { learner_id: learnerId, lesson } }),
  progress: (learnerId: string) =>
    req<Progress>(`/tutorial/progress/${learnerId}`),

  // What the help box can answer without a model. Worth showing rather
  // than leaving people to guess at a blank input.
  helpTopics: () => req<HelpTopics>("/help/topics"),

  dockFaces: () => req<DockFaces>("/dock/faces"),
  dockRoute: (face: string) => req<DockRoute>(`/dock/where/${face}`),
  dockSettings: (profileId: string, token: string) =>
    req<DockSettings>(`/dock/${profileId}`, { token }),
  setDock: (profileId: string, body: { corner?: string; state?: string;
                                       face?: string }, token: string) =>
    req<DockSettings>(`/dock/${profileId}`,
      { method: "PUT", body, token }),
  dockFace: (profileId: string, name: string, token: string) =>
    req<DockFace>(`/dock/${profileId}/face/${name}`, { token }),

  // ---------------------------------------------------------------------
  // Plans and membership.
  //
  // Found by following the refusal. `Refusal.tsx` draws a plan gate as an
  // upsell — the capability, the plan that has it, the price — and then
  // had nowhere to send anybody, because the four routes behind the price
  // it was quoting had no caller either. A refusal that names a plan in a
  // product with no way to join one is worse than a flat no.
  //
  // `GET /plans` is public on purpose (`tiers.py`: "a paywall nobody can
  // read the terms of before signing in is one people bounce off"), and it
  // is generated from the same table the gate reads, so the page and the
  // refusal cannot disagree.
  // ---------------------------------------------------------------------

  plans: () => req<PlanCatalogue>("/plans"),
  membership: (accountId: string, token: string) =>
    req<Membership>(`/memberships/${accountId}`, { token }),
  subscribe: (accountId: string, plan: string, token: string) =>
    req<Membership>(`/memberships/${accountId}`,
      { method: "POST", body: { plan }, token }),
  // Ends the subscription; the account keeps its profiles. Named for what
  // it does rather than `delete`, because "cancel my plan" and "delete my
  // work" are the two things a person must never confuse here.
  cancelMembership: (accountId: string, token: string) =>
    req<Membership>(`/memberships/${accountId}`,
      { method: "DELETE", token }),

  // ---------------------------------------------------------------------
  // A body to speak through.
  //
  // The native shells already drive the catalogue, the binding and the
  // command button; the web console never had any of it, so the three
  // routes that say what a body has *become* — its steering, what it has
  // learned, and what it has been told to do — had no caller anywhere.
  //
  // Read the three list-shaped things carefully, because two of them are
  // named almost identically and mean different things:
  //
  //   robot.commands            what this model of body accepts at all
  //   GET /robots/{id}/commands the audit log of what it was told to do
  //   GET /robots/{id}/skills   installed task modules, which *extend* the
  //                             allowlist above with new verbs
  //
  // A screen built from the route names alone would show the log where the
  // buttons belong.
  // ---------------------------------------------------------------------

  robotCatalogue: () => req<{ robots: RobotModel[] }>("/robotics/catalog"),
  robots: (profileId: string, token: string) =>
    req<RobotRow[]>(`/profiles/${profileId}/robots`, { token }),
  bindRobot: (profileId: string, body: { name: string; model: string },
              token: string) =>
    req<BoundRobot>(`/profiles/${profileId}/robots`,
      { method: "POST", body, token }),
  // Unbinds the body from the profile. The name follows the response —
  // `{id, unbound: true}` — rather than the HTTP verb, because "delete my
  // robot" and "stop this profile speaking through it" are different
  // enough to be worth not confusing on a button.
  unbindRobot: (robotId: string, token: string) =>
    req<{ id: string; unbound: boolean }>(`/robots/${robotId}`,
      { method: "DELETE", token }),

  commandRobot: (robotId: string, body: { command: string; arg?: string },
                 token: string) =>
    req<RobotCommandResult>(`/robots/${robotId}/command`,
      { method: "POST", body, token }),
  robotCommandLog: (robotId: string, token: string) =>
    req<RobotCommandEntry[]>(`/robots/${robotId}/commands`, { token }),
  robotSkills: (robotId: string, token: string) =>
    req<RobotSkill[]>(`/robots/${robotId}/skills`, { token }),

  robotSteering: (robotId: string, token: string) =>
    req<RobotSteering>(`/robots/${robotId}/steering`, { token }),
  // `values`, not `dials` — driven, and worth saying: the request model
  // takes `values` with a default of `{}`, so a body keyed `dials` is
  // accepted, ignored, and answered 200 with nothing changed. There is no
  // error to notice.
  setRobotSteering: (robotId: string, values: Record<string, number>,
                     token: string) =>
    req<RobotSteeringSet>(`/robots/${robotId}/steering`,
      { method: "PUT", body: { values }, token }),

  // ---------------------------------------------------------------------
  // Where a rated profile is marketed.
  //
  // The venue catalogue is public and structural; the age wall never moves
  // to the venue. Every entry carries that sentence and the screen renders
  // it verbatim, because it is the whole argument for the feature existing:
  // a rated profile can be advertised anywhere and still only resolves
  // through QRME's own 18+ wall.
  // ---------------------------------------------------------------------

  venues: () => req<Venue[]>("/venues"),
  placements: (profileId: string, token: string) =>
    req<PlacementRow[]>(`/profiles/${profileId}/placements`, { token }),
  placeAtVenue: (profileId: string, body: { venue: string; label?: string },
                 token: string) =>
    req<PlacementMade>(`/profiles/${profileId}/placements`,
      { method: "POST", body, token }),
  placementAnalytics: (profileId: string, token: string) =>
    req<PlacementAnalytics>(`/profiles/${profileId}/placements/analytics`,
      { token }),
  // 409s with an operator sentence when the deployment has no vault. That
  // is a posture to report, not a failure to apologise for.
  placementCustody: (profileId: string, token: string) =>
    req<PlacementCustody>(`/profiles/${profileId}/placements/custody`,
      { token }),
  // Deactivates the beacon rather than deleting it: a QR already printed
  // at a venue stops resolving, and the response says so.
  removePlacement: (placementId: string, token: string) =>
    req<PlacementRemoved>(`/placements/${placementId}`,
      { method: "DELETE", token }),

  // ---------------------------------------------------------------------
  // What a profile is made of, and how the owner shapes it.
  //
  // Source material, the dials, a CV, the specialists it hands work to, the
  // bodies it speaks through, and the local fine-tune that folds all of it
  // back in. Twelve routes, none of them with a caller in the console.
  //
  // Two of these writes were **silently permissive** until this round:
  // `PUT .../steering` takes `values` and `PUT .../experience` takes
  // `period`, and a body keyed anything else was accepted, discarded, and
  // answered 200. `dials` and `years` are the obvious guesses — the first
  // is what the steering *read* calls its catalogue, the second is what
  // anybody writing a CV form reaches for. Both models are now strict, so
  // the next wrong guess gets a 422 naming the field.
  // ---------------------------------------------------------------------

  profileSteering: (profileId: string, token: string) =>
    req<ProfileSteering>(`/profiles/${profileId}/steering`, { token }),
  setProfileSteering: (profileId: string, values: Record<string, number>,
                       token: string) =>
    req<ProfileSteeringSet>(`/profiles/${profileId}/steering`,
      { method: "PUT", body: { values }, token }),

  sources: (profileId: string, token: string) =>
    req<SourceItem[]>(`/profiles/${profileId}/sources`, { token }),
  addSource: (profileId: string,
              body: { kind: string; title?: string; content?: string },
              token: string) =>
    req<SourceAdded>(`/profiles/${profileId}/sources`,
      { method: "POST", body, token }),

  // Plural route, singular body: one `{domain, specialist_profile_id}` pair
  // per call, replacing whatever held that domain. Reading the route name
  // as "set the list" sends an array and gets a 422 for two missing fields.
  specialists: (profileId: string, token: string) =>
    req<Specialist[]>(`/profiles/${profileId}/specialists`, { token }),
  attachSpecialist: (profileId: string, domain: string,
                     specialistProfileId: string, token: string) =>
    req<SpecialistSet>(`/profiles/${profileId}/specialists`,
      { method: "PUT", token,
        body: { domain, specialist_profile_id: specialistProfileId } }),

  // Replaced wholesale — a CV is a statement, not rows to patch.
  setExperience: (profileId: string, entries: ExperienceEntry[],
                  token: string) =>
    req<{ profile_id: string; experience: ExperienceEntry[] }>(
      `/profiles/${profileId}/experience`,
      { method: "PUT", body: { entries }, token }),

  // No body. The answer's own fields are the interesting part: nothing was
  // transmitted, it was computed on this host, and whether it was sealed.
  finetune: (profileId: string, token: string) =>
    req<FinetuneRun>(`/profiles/${profileId}/finetune`,
      { method: "POST", body: {}, token }),

  embodiments: (profileId: string, token: string) =>
    req<Embodiment[]>(`/profiles/${profileId}/embodiments`, { token }),
  addEmbodiment: (profileId: string,
                  body: { name: string; kind: string; has_llm: boolean },
                  token: string) =>
    req<Embodiment & { profile_id: string }>(
      `/profiles/${profileId}/embodiments`, { method: "POST", body, token }),
  // **Public**, and deliberately so: anybody who meets this profile through
  // any form can check it is the same personality. No token.
  embodimentConsistency: (profileId: string) =>
    req<EmbodimentConsistency>(`/profiles/${profileId}/embodiment-consistency`),

  perceive: (profileId: string,
             body: { objects?: string[]; people?: string[];
                     gestures?: string[]; place?: string; goal?: string },
             token: string) =>
    req<Perception>(`/profiles/${profileId}/perceive`,
      { method: "POST", body, token }),

  // ---------------------------------------------------------------------
  // The profile working for its owner, and what it leaves behind.
  //
  // Triage, proofreading, composing something to keep, the wearables the
  // watch faces run on, the reviews people who actually talked to it left,
  // and the mark every generated thing carries.
  // ---------------------------------------------------------------------

  triage: (profileId: string,
           body: { items: { id: string; text: string }[]; keep: number;
                   criteria?: string }, token: string) =>
    req<TriageResult>(`/profiles/${profileId}/assist/triage`,
      { method: "POST", body, token }),
  proofread: (profileId: string, text: string, token: string) =>
    req<Proofread>(`/profiles/${profileId}/assist/proofread`,
      { method: "POST", body: { text }, token }),
  compose: (profileId: string, body: { kind: string; moment: string },
            token: string) =>
    req<CreativeWork>(`/profiles/${profileId}/assist/compose`,
      { method: "POST", body, token }),
  works: (profileId: string, token: string) =>
    req<CreativeWork[]>(`/profiles/${profileId}/assist/works`, { token }),

  // `include_revoked` exists because unpairing is a revocation and not a
  // delete — the row stays, with the date. Without asking for them the
  // console can never show that, and a promise nobody can see is a promise
  // that may as well not have been kept.
  wearables: (profileId: string, token: string, includeRevoked = false) =>
    req<WearableView>(
      `/profiles/${profileId}/wearables`
      + (includeRevoked ? "?include_revoked=true" : ""), { token }),
  pairWearable: (profileId: string,
                 body: { name: string; kind: string; faces?: string[] },
                 token: string) =>
    req<Wearable>(`/profiles/${profileId}/wearables`,
      { method: "POST", body, token }),
  // Keyed by **name**, not id — the id is in the row and the route is not.
  unpairWearable: (profileId: string, name: string, token: string) =>
    req<Wearable>(
      `/profiles/${profileId}/wearables/${encodeURIComponent(name)}`,
      { method: "DELETE", token }),

  reviews: (profileId: string) =>
    req<ReviewsView>(`/profiles/${profileId}/reviews`),
  leaveReview: (profileId: string,
                body: { interactor_id: string; rating: number; body?: string },
                token: string) =>
    req<Review>(`/profiles/${profileId}/reviews`,
      { method: "POST", body, token }),

  thread: (profileId: string, interactorId: string, token: string) =>
    req<ThreadView>(`/profiles/${profileId}/thread/${interactorId}`, { token }),
  editMessage: (profileId: string, messageId: string, interactorId: string,
                content: string, token: string) =>
    req<MessageRevision>(`/profiles/${profileId}/messages/${messageId}`,
      { method: "PATCH", body: { interactor_id: interactorId, content },
        token }),
  // A DELETE **with a body** — the route needs to know who is retracting.
  // Worth stating: plenty of HTTP clients drop a body on DELETE, and this
  // one 422s without it rather than guessing.
  retractMessage: (profileId: string, messageId: string, interactorId: string,
                   token: string) =>
    req<MessageRevision>(`/profiles/${profileId}/messages/${messageId}`,
      { method: "DELETE", body: { interactor_id: interactorId }, token }),

  // ---------------------------------------------------------------------
  // The mark.
  //
  // `valid` and `content_match` are **different questions** and can
  // disagree: a genuine credential whose content has since been altered
  // answers `valid: true, content_match: false`. A screen that reported
  // `valid` alone would say the opposite of the truth about the thing in
  // front of somebody.
  // ---------------------------------------------------------------------

  watermark: (watermarkId: string) =>
    req<WatermarkRecord>(`/watermarks/${watermarkId}`),
  verifyWatermark: (watermarkId: string, content: string) =>
    req<WatermarkVerdict>("/watermarks/verify",
      { method: "POST", body: { watermark_id: watermarkId, content } }),

  // ---------------------------------------------------------------------
  // Handing a conversation to a clinician.
  //
  // Nothing is released until a signature covers the exact bytes. `prepare`
  // assembles the summary and raises a challenge whose value *is* the hash
  // of those bytes — so signing it signs this summary rather than a
  // checkbox, and a summary edited afterwards cannot ride the old
  // signature.
  //
  // Three pairs are easy to confuse and are named apart here:
  //
  //   the referral token  opens it, once
  //   the reply token     answers it, and arrives only when it is opened
  //   the signature id    is what release checks, not the envelope id
  // ---------------------------------------------------------------------

  clinicians: (area: string, location?: string) =>
    req<Clinician[]>(`/referrals/match?area=${encodeURIComponent(area)}`
      + (location ? `&location=${encodeURIComponent(location)}` : "")),
  providers: () => req<Provider[]>("/providers"),
  addProvider: (body: { name: string; area: string; location?: string;
                        contact?: string; business?: boolean }) =>
    req<{ id: string; name: string; area: string }>("/providers",
      { method: "POST", body }),

  prepareReferral: (body: { interactor_id: string; profile_id: string;
                            provider_id: string }, token: string) =>
    req<ReferralPrepared>("/referrals/prepare",
      { method: "POST", body, token }),
  releaseReferral: (referralId: string, signatureId: string, token: string) =>
    req<ReferralReleased>(`/referrals/${referralId}/release`,
      { method: "POST", body: { signature_id: signatureId }, token }),
  // The clinician's side. No account — the link is the credential, and it
  // works once.
  openReferral: (referralId: string, token: string) =>
    req<ReferralOpened>(
      `/referrals/${referralId}?token=${encodeURIComponent(token)}`),
  replyToReferral: (referralId: string, replyToken: string, content: string) =>
    req<ReferralReplied>(
      `/referrals/${referralId}/reply?token=${encodeURIComponent(replyToken)}`,
      { method: "POST", body: { content } }),
  myReferrals: (interactorId: string, token: string) =>
    req<ReferralHistory[]>(`/interactors/${interactorId}/referrals`, { token }),
  clinicalNotes: (profileId: string, interactorId: string, token: string) =>
    req<ClinicalNote[]>(
      `/profiles/${profileId}/clinical-notes/${interactorId}`, { token }),

  // ---------------------------------------------------------------------
  // The signature behind it.
  // ---------------------------------------------------------------------

  signingCredentials: (token: string) =>
    req<{ credentials: SigningCredential[] }>("/signatures/credentials",
      { token }),
  // Enrolment fixes a proofing level; this is how it moves. `can_sign` on
  // the answer is the visible consequence — a self-asserted credential
  // signs `basic` only, and a document check opens `high`.
  reproof: (rowId: string,
            body: { proofing_level: string; proofing_attestor: string;
                    proofing_method?: string; proofing_ref?: string },
            token: string) =>
    req<SigningCredential>(`/signatures/credentials/${rowId}/proofing`,
      { method: "POST", body, token }),
  certificate: (signatureId: string) =>
    req<Certificate>(`/signatures/${signatureId}/certificate`),
};

/** Open the WebAuthn ceremony.
 *
 *  A page rather than a request, and it has to be: WebAuthn refuses a
 *  mismatched `rpId`, and an opaque origin has none to match — so the
 *  ceremony is served from the relying party's own origin and the browser
 *  navigates to it. It takes no token on purpose; a bearer token in a query
 *  string ends up in logs and history. */
export function openCeremony(params: {
  mode: "sign" | "enroll"; challenge: string;
  display_text?: string; meaning?: string;
  user_id?: string; user_name?: string; display_name?: string;
}): Window | null {
  const q = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v) as [string, string][]);
  // The path is its own literal so the route audit can see it — a template
  // that opens with `${...}` is a string the extractor cannot resolve to a
  // path, and this door would go on counting as missing.
  return window.open(getBase() + `/signatures/ceremony?${q}`,
                     "qrme-ceremony", "width=460,height=620");
}

/** Raw bytes, not JSON and not multipart — the route reads the request body
 *  and works the kind out from the bytes. `filename` is a display hint that
 *  never chooses the kind, so it rides as a query parameter. Written by hand
 *  rather than through `req()` because `req()` serialises JSON. */
export async function uploadMedia(profileId: string, file: File,
                                  token: string): Promise<UploadedMedia> {
  const q = file.name ? `?filename=${encodeURIComponent(file.name)}` : "";
  const res = await fetch(`${getBase()}/profiles/${profileId}/media${q}`, {
    method: "POST",
    headers: { "content-type": "application/octet-stream",
               authorization: `Bearer ${token}` },
    body: file,
  });
  const text = await res.text();
  let data: unknown = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) {
    const body = data as { detail?: unknown } | null;
    throw new RequestError(res.status, (body && body.detail) ?? text);
  }
  return data as UploadedMedia;
}
