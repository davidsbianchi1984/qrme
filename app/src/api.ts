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
// The deployment invite key: a published deployment sets QRME_SIGNUP_KEY and
// refuses account creation without it. Stored on this device once typed,
// sent as x-signup-key on every request — the backend reads it only on the
// routes it gates, so carrying it everywhere costs nothing and means the
// mail-settings screen works on a gated deployment too.
export function getSignupKey(): string { return localStorage.getItem("qrme.signupKey") || ""; }
export function setSignupKey(key: string) {
  if (key.trim()) localStorage.setItem("qrme.signupKey", key.trim());
  else localStorage.removeItem("qrme.signupKey");
}
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
 *  simply gets better.
 *
 *  ## The shape that walked past all of it
 *
 *  A 422 answers with a *list*, not an object: pydantic's rows, one per field.
 *  `sentence` below handled a string and an object carrying `message`, and a
 *  list is an object with no `message`, so it fell through to the
 *  `JSON.stringify` written for the unhandled case — and a mistyped form
 *  showed `[{"type":"missing","loc":["body","display_name"],...}]`.
 *
 *      asked     does a structured refusal reach the reader as a sentence
 *      mattered  does every structured refusal
 *
 *  The backend composes that sentence now (`qrme/i18n.py:validation_message`),
 *  in the reader's language, and `req` passes it in beside the rows. */
export class RequestError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown, message?: unknown) {
    super(RequestError.sentence(detail, message));
    this.name = "RequestError";
    this.status = status;
    this.detail = detail;
  }

  /** The most human thing in the payload. A sentence the body carried
   *  alongside the structure wins; then a structured refusal quoting its own
   *  `message`; and only then the JSON, which is at least honest about being
   *  unhandled.
   *
   *  `message` is checked first and not last because the case it exists for —
   *  the 422 list — reaches the fallback otherwise, which is how it got out. */
  private static sentence(detail: unknown, message?: unknown): string {
    if (typeof message === "string" && message) return message;
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

/** One body on the market. `availability` is the whole reason this
 *  catalogue is worth reading: it lists machines nobody can buy yet, and
 *  `bindable` says which of them a profile can actually be attached to —
 *  binding an `announced` one is a 409 that names the status rather than a
 *  404, because the machine is real and its maker has shown it. */
export type RobotModel = {
  model: string; label: string; maker: string; kind: string;
  capabilities: string[];
  llm_capable: boolean;
  availability: string;      // shipping | preorder | announced
  bindable: boolean;
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
export type SteeringLock = {
  subject_id: string; reason: string | null; locked_at: string;
};
export type ProfileSteering = {
  subject: string; subject_id: string;
  dials: SteeringDial[];
  values: Record<string, number>;
  adult_mode: boolean;
  lock?: SteeringLock | null;
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
  kinds_worn: Record<string, string>;
  /** Room-facing microphones, each with the paragraph saying why it cannot
   *  be paired. Rendered verbatim: the argument is that the people who walk
   *  into the room did not agree to anything. */
  refusal_reasons: Record<string, string>;
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
  /** What the upload shows, in the uploader's words — the image's alt. */
  alt?: string | null;
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

/** What each tier demands, and — the part that matters — what the scheme
 *  does **not** prove. `limits` is prose written to be shown, not summarised:
 *  every line is a claim somebody might otherwise make about a signature and
 *  be wrong. The screen renders them verbatim for that reason. */
export type SigningPolicy = {
  tiers: Record<string, { min_proofing: string; device_bound: boolean;
                          hybrid_required_in_xr: boolean;
                          trusted_timestamp: boolean }>;
  proofing_levels: string[];
  xr_platform_authenticators: string[];
  xr_hybrid_required: string[];
  standard: string;
  limits: string[];
};

/** Straight out of `navigator.credentials.create()`'s vocabulary — the
 *  ceremony page consumes it as-is, which is why the field names are
 *  WebAuthn's camelCase rather than this API's snake_case. */
export type EnrollOptions = {
  challenge: string;
  rp: { id: string; name: string };
  user: { id: string; name: string; displayName: string };
  pubKeyCredParams: { type: string; alg: number }[];
  timeout: number;
  authenticatorSelection: { userVerification: string; residentKey: string };
  attestation: string;
  extensions: Record<string, unknown>;
};

/** The envelope. `challenge` **is** the hash of `payload`, and `payload`
 *  carries the document's hash — so signing the challenge signs this
 *  document and no other. `allowed_credentials` is why an envelope minted
 *  by one account cannot be signed by another's key. */
export type SignatureEnvelope = {
  envelope_id: string;
  challenge: string;
  payload: Record<string, unknown>;
  display_text: string;
  display_sha256: string;
  document_sha256: string;
  meaning: string;
  tier: string;
  expires_at: string;
  allowed_credentials: string[];
  user_verification: string;
};

export type SignatureResult = {
  signature_id: string;
  envelope_id: string;
  signer: { account_id: string; name: string; proofing_level: string };
  meaning: string;
  document_sha256: string;
  display_text: string;
  display_sha256: string;
  tier: string;
  user_verified: boolean;
};

/** `checks` is the whole answer and `valid` is only its conjunction, so the
 *  screen shows the checks rather than a green tick.
 *
 *  A check that is **absent** did not run. That distinction is load-bearing:
 *  a package missing a field used to come back `signature: false`, which
 *  said the cryptography was broken when it had verified perfectly well.
 *  Absent now means absent, `valid` is false whenever anything is missing,
 *  and `notes` says which. */
export type VerifyVerdict = {
  valid: boolean;
  checks: Partial<Record<
    "signature" | "challenge_matches" | "ceremony_is_signing"
    | "challenge_binds_payload" | "payload_binds_document"
    | "payload_binds_display" | "display_text_matches" | "user_verified",
    boolean>>;
  notes: string[];
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

// ---------------------------------------------------------------------
// The lobby.
// ---------------------------------------------------------------------

export type LobbyVocabulary = {
  kinds: { kind: string; is: string }[];
  seats: { role: string; does: string }[];
  max_synthetic: number;
  /** Twelve entries, each closing a route somebody would otherwise argue
   *  for — its own console, a second controller, a Bluetooth pad, a
   *  capture card. Rendered verbatim: every one is a decision with a
   *  reason, and "no cheating" is not the same statement. */
  never: { thing: string; means: string }[];
  fair_play: string;
  rules: string[];
};

export type Seat = {
  seat_id: string | null;
  member_kind: string;
  member_id: string;
  role: string;
  does: string;
  callsign: string | null;
  synthetic: boolean;
  is: string;
  host?: boolean;
  since: string;
  seated?: boolean;
};

export type Lobby = {
  session_id: string; game: string; platform: string;
  members: Seat[];
  people: number; profiles: number; agents: number;
  synthetic_seats_left: number;
  maturity: string;
  fair_play: string;
};

/** What a synthetic member is told about its own position. The instruction
 *  says openly that some of the others are synthetic too — a model that
 *  believes every callsign is a person will address them as people. */
export type LobbyContext = {
  game: string;
  members: { callsign: string | null; role: string; synthetic: boolean }[];
  people: number;
  synthetic_here: number;
  maturity: string;
  instruction: string;
};

export type HandoffPackage = {
  user: string;
  provider_area: string;
  sessions: number | null;
  specialist?: string;
  specialist_purpose?: string;
  recent_exchange?: { role: string; content: string }[];
};

export type HandoffMade = {
  id: string; provider: string; area: string;
  token: string;
  /** True where a vault holds the package. False means it is sitting in
   *  this deployment's database until somebody revokes it. */
  sealed: boolean;
};

// ---------------------------------------------------------------------
// The audience.
// ---------------------------------------------------------------------

export type Subscription = {
  id: string;
  subject_kind: string; subject_id: string;
  subscriber: string;
  /** `follow` or `paid` — there is no middle tier, and a name that is not
   *  one of those is refused with both spelled out. */
  tier: string;
  price: number; currency: string;
  status: string;
  started_at: string; renewed_at: string;
  /** Counts up only when somebody presses renew. Nothing here bills on a
   *  timer, so a deployment left running charges nobody. */
  periods: number;
  /** Set on cancel; the row survives, so a lapsed-then-returned subscriber
   *  keeps one history rather than accumulating rows. */
  cancelled_at: string | null;
  billing: string;
  charged?: { period: number; amount: number; ledger_entry: string };
};

export type Gift = {
  id?: string;
  amount: number; currency: string;
  note?: string | null;
  created_at?: string;
};

export type GiftsView = {
  gifts: Gift[];
  total_amount: number;
  /** Published so a screen can say the limit before somebody hits it. */
  cap_per_gift: number;
};

export type AudienceView = {
  likes: number; comments: number; shares: number;
  subscribers: number;
  you_liked: boolean;
  your_subscription: Subscription | null;
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

export interface DmMessage {
  id: string; low_id: string; high_id: string; sender_id: string;
  body: string; sent_at: string;
}
export interface DmThread {
  other_id: string; other_name?: string | null; messages: number;
  last_at: string;
}
export interface Homepage {
  profile_id: string; display_name?: string | null; headline: string;
  about: string; theme: { bg: string; accent: string };
  links: { label: string; url: string }[];
  top_friends: { profile_id: string; display_name: string }[];
  editable: boolean;
}

export interface ShopCard {
  id: string; profile_id: string; name: string; blurb?: string | null;
  tag?: string | null; seller: string; offerings: number;
}
export interface ShopOffering {
  id: string; shop_id: string; kind: string; title: string;
  blurb?: string | null; price: number; currency: string;
  availability: string; retired: number;
}
export interface ShopDetail extends Omit<ShopCard, "offerings"> {
  offerings: ShopOffering[];
}
export interface ShopOrder {
  id: string; shop_id: string; offering_id: string; buyer_id: string;
  quantity: number; amount: number; currency: string; note?: string | null;
  status: string; placed_at: string; settled_at?: string | null;
  title: string; kind: string;
}

async function req<T>(
  path: string,
  opts: { method?: string; body?: unknown; token?: string } = {},
): Promise<T> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (opts.token) headers["authorization"] = `Bearer ${opts.token}`;
  const llmKey = getLlmKey();
  if (llmKey) headers["x-llm-api-key"] = llmKey;
  const signupKey = getSignupKey();
  if (signupKey) headers["x-signup-key"] = signupKey;
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
    // The sentence rides beside the structure rather than replacing it: a
    // screen that renders the plan gate's buttons still gets `detail`, and a
    // screen that only shows `e.message` stops showing a serialised list.
    throw new RequestError(res.status, detail, body?.message);
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
  name?: string | null; alt?: string | null; ai_marked: false;
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
  engagement_avg: number;
  interactors: number;
  sources: number;
  posts: number;
  surfaces: string[];
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
  /** Who actually wrote this, and what was asked for when they differ.
   *
   *  `generated_by` used to be the profile's stored *choice*, so an owner
   *  whose own API key had expired read stub-written text labelled with the
   *  model they had chosen. `degraded_from` is what makes the amber banner
   *  possible: without it a record that suddenly says "local fallback" looks
   *  like somebody changed a setting rather than a credential going dead. */
  provenance?: {
    generated_by?: string;
    degraded_from?: string | null;
  } | null;
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
                 profile_id: string; agent: string; scoped: boolean;
                 leased: boolean; lease_revoked: boolean }[];
}
/** AI for lease: a stranger's licensed specialist, seated as a department
 *  under a revocable lease. */
export interface LeaseOut {
  lease_id: string;
  department_id: string;
  org: OrgOut;
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
  /** The sentence that travels with every figure in this repository. A
   *  fundraising page is the last place it should be dropped. */
  payment?: string;
  created_at?: string;
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
export interface MemoryEntry {
  id?: string; role: string; content: string; at?: string;
  // A rewritten turn says so — the fact of the edit is part of the record.
  edited?: boolean;
}
export interface Remembrance {
  content: string | null; covers: number; updated_at: string | null;
}
export interface MemoryAccount {
  profile_name: string;
  remembers: string | null;
  folded_turns: number;
  recent_turns: number;
  first_at: string | null;
  last_at: string | null;
}

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
  ready_when: { samples: number; seconds: number };
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
export interface ObjectionTimeline {
  objection_id: string; profile_id: string; status: string;
  reattested: boolean; vault_backed: boolean; note: string;
  events: { id: string; event: string; actor: string;
            sealed: boolean; at: string }[];
}

export interface InboxEvent {
  id: string;
  /** One of the closed set in qrme/inbox.py — message | comment | friend |
   *  exchange_signed | guest_accepted. The sentence is the client's to
   *  compose; the backend names the deed, never the words. */
  kind: string;
  actor_id: string; actor_name: string | null;
  ref: string | null; created_at: string; seen: boolean;
}

export interface ProfileAttention {
  profile_id: string;
  people_this_week: number;
  people_ever: number;
  you_are_one_of_them: boolean;
  says: string;
  ranks_people: boolean;
  has_a_favourite: boolean;
  names_anybody: boolean;
  note: string;
}

export interface SolitudeOffer {
  state: "available" | "accepted" | "declined";
  at?: string;
  what?: string;
  why?: string;
  carries?: string[];
  does_not_carry?: string[];
  accept_at?: string;
}

export interface Solitude {
  interactor_id: string;
  window_days: number;
  turns: { to_profiles: number; to_people: number };
  total_turns: number;
  /** null until there is any conversation at all to take a ratio of. */
  share_synthetic: number | null;
  enough_to_say: boolean;
  note: string;
  offer?: SolitudeOffer;
}

export interface SolitudeReferral {
  ref: string;
  window_days: number;
  turns: { to_profiles: number; to_people: number };
  issued_at: string;
  product: string;
}

export interface SolitudeDecision {
  interactor_id: string;
  state: "accepted" | "declined";
  referral: SolitudeReferral | null;
}

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
// `delegation` is a boolean and `phases` sits beside it — not nested under
// it. The nested shape below was never what /profiles/{id}/delegation sends,
// and TypeScript erased the difference at build time: `false?.enabled` is
// `undefined`, so the screen read every profile as un-delegated and offered
// no way to change that.
export type Delegation = {
  delegation: boolean;
  phases: string[];
  delegable: string[];
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
  scope: string; include_remote: boolean; kinds_wanted: string[];
  tags: string[];
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
  /** Whether the host put it on the public surfaces. The id stays the
   *  private door either way. */
  public: boolean;
  video: PartyVideo;
  position_s: number; playing: boolean;
  members: PartyMember[];
  people: number; profiles: number;
  created_at: string;
  loads_on_press: boolean;
  /** "the room shares a position, not a player" — the server's sentence. */
  note: string;
};

/** A public browse card: counts and the facade, never member names and
 *  never a line of chat — those stay members-only. */
export type PublicParty = {
  kind: "party"; id: string; title: string | null;
  video: PartyVideo | null;
  people: number; profiles: number; playing: boolean;
  plays: boolean;
  /** What pressing Join does, said before it is pressed. */
  joining: string;
  join: string; reason: string; at: string;
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
  /** The upper-torso form — the figure that stands in a live feed or an
   *  AR scene at 1:1; the circular bubble is only the avatar-less form. */
  torso?: string | null;
  /** Always displayed, by the product's own rule. */
  watermark: { mark: string; label: string; line: string; custom: boolean;
               always_displayed: boolean; disclosure: string };
  likeness: { real_person: boolean; note: string;
              basis?: string | null; attestor?: string | null;
              revocable?: boolean };
  placeholder: boolean;
  /** The moving image: animation parameters derived from the interaction
   *  history. `tempo_ms` is the idle-breath period; 0 means pinned still. */
  motion: { style: string; energy: number; warmth: number; tempo_ms: number;
            states: { idle: string; speaking: string; listening: string };
            updated_with: number };
};

export type AvatarBrief = {
  handle: string; portrait: string; style: string; prompt?: string;
  asset?: string | null;
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
  refusals: { kind: string; why: string }[];
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

/** One turn in a room. A profile's turn always carries a watermark; a
 *  person's never does, which is the difference the screen renders. */
export type RoomMsg = {
  id: string;
  sender_kind: string;          // user | profile
  from: string;
  content: string | null;
  watermark: { display?: { line?: string } } | null;
  created_at?: string;
};

export type RobotCatalogue = {
  robots: RobotModel[];
  by_maker: Record<string, RobotModel[]>;
  by_kind: Record<string, RobotModel[]>;
  by_availability: Record<string, RobotModel[]>;
  commands: Record<string, string[]>;
  reviewed: string;
  buyable: string[];
  note: string;
};

export type ConnectorCatalogue = {
  providers: { provider: string; label: string;
               apps: { app: string; label: string; capabilities: string[];
                       directions: string[] }[] }[];
  app_count: number; provider_count: number;
};

export type PackRow = {
  id: string; industry: string; audience: string; title: string;
  publisher: string; price?: number; rated?: boolean;
};

export type InstalledPack = {
  id: string; industry: string; audience: string; title: string;
  publisher: string; robot_id: string | null;
  price_paid: number | null; installed_at: string;
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
  refusal_reasons: Record<string, string>;
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

/** The frame a visitor sees, and the sentence that keeps it honest.
 *  `live` is false wherever no camera is attached, and `note` says so in
 *  words — a sample view is never allowed to pass for a live one. */
export type DeskFeed = {
  url: string;
  live: boolean;
  note: string;
  ai: boolean;
  watermark: string | null;
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
  /** Typed rather than `unknown` because the console renders it: the note is
   *  the whole reason the block exists, and a picture served without it
   *  reads as a live camera on a deployment that has none. */
  feed?: DeskFeed;
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

/** One connected thing across the counter. `token` only ever appears in the
 *  caller's own view of an active link — it is their machine the link opens,
 *  so the secret is theirs and the desk's view never carries it. */
export type DeskConnection = {
  id: string;
  session_id: string;
  kind: string;
  target: string;
  scope?: string | null;
  status: string;          // offered | active | declined | ended
  means?: string;          // what agreeing to this kind means, in words
  token?: string;          // caller's view of an active link only
  offered_at?: string;
  answered_at?: string | null;
  ended_at?: string | null;
  ended_by?: string | null;
};

export type DeskSession = {
  id: string;
  desk_id: string;
  caller_id: string;
  ring_id?: string | null;
  status: string;          // open | closed
  desk_name?: string | null;
  trade?: string | null;
  opened_at?: string;
  closed_at?: string | null;
  closed_by?: string | null;
  connections: DeskConnection[];
};

/** What a visitor sees standing in front of somebody's desk.
 *
 *  `designation` is the sentence the whole feature rests on — *Live person —
 *  not AI* — and it is the inversion of the mark every synthetic profile
 *  carries. `attestation.signed` is the honest qualifier: recorded is not
 *  proven, and the screen has to say which this is. */
export type DeskCard = {
  desk_id: string;
  display_name: string;
  trade: string;
  location: string | null;
  blurb: string | null;
  rated: boolean;
  age_wall: boolean;
  presence: string;
  last_seen: string | null;
  human: boolean;
  ai: boolean;
  designation: string;
  attestation: {
    attestor: string; basis: string; attested_at: string;
    signed: boolean; signature_id: string | null; note: string;
  };
  portrait: string | null;
  feed: { url: string; live: boolean; note: string;
          watermark: string | null; ai: boolean };
};

export type BellRung = {
  ring_id: string;
  desk_id: string;
  /** How many are already waiting — including this one. */
  waiting: number;
  presence: string;
  note: string;
};

/** Both join modes land in the same room; `on_stream` is the difference, and
 *  it is reported rather than inferred so a client draws the right thing
 *  instead of guessing from the absence of something. */
export type DeskJoined = {
  desk_id: string;
  room_id: string;
  channel: string;
  presence: string;
  rated: boolean;
  /** Always false. There is a real person on the other end of this stream. */
  ai: boolean;
  mode: string;
  on_stream: boolean;
  overlay: DeskOverlay;
  note: string;
  /** Present only for `mode: "guest"`, and only once the request is made. */
  guest_request?: DeskGuest;
};

/** A profile left somewhere — a QR sticker on a bench, at a meeting, on a
 *  counter. `mode: "room"` mints one shared room every scanner joins, so the
 *  people who found the same sticker talk to the profile together. */
export type ProfileBeacon = {
  id: string;
  label: string;
  location: string | null;
  summon_url: string;
  /** What the printed QR actually encodes — this is the one to print. */
  scan_url: string;
  mode: string;
  room_id: string | null;
  qr_svg: string;
};

export type PlacedBeacon = {
  id: string; profile_id: string; label: string; location: string | null;
  scans: number; active: boolean; room_id: string | null; created_at: string;
};

/** The smallest thing an in-camera overlay needs: who it is, one line of
 *  portrait, and the mark. The mark travels *with* the card so an overlay
 *  cannot draw the face without also holding the disclosure to draw with it. */
export type BeaconScanCard = {
  profile_id?: string;
  display_name?: string;
  watermark?: string;
  portrait?: string | null;
  /** Whether the disclosure is already burned into the image. A surface QRME
   *  does not control needs to know if compositing is mandatory. */
  portrait_marked?: boolean;
  initials?: string;
  label?: string;
  shared_room?: string | null;
  open_url?: string;
  age_wall: boolean;
  rated?: boolean;
  note?: string;
};

/** A raised hand. The field is `status`, not `state` — the index signature
 *  below meant the wrong name typechecked and read `undefined` forever. */
export type DeskGuest = {
  id: string;
  desk_id: string;
  guest_id: string;
  display_name: string | null;
  note: string | null;
  status: string;
  requested_at: string;
  decided_at: string | null;
  on_stream: boolean;
};

/** What a viewer sees layered over the stream.
 *
 *  Three of these were written from the route's name rather than from its
 *  answer, and `Desk` rendered all three wrong. `style` is a layout object,
 *  not a word, so *laid out as a ${style}* printed `[object Object]`.
 *  `comments` and `waiting` were **exactly swapped**: `waiting.length` on a
 *  number printed `undefined waiting`, and `{comments}` on an array of
 *  objects renders as nothing while empty and throws the moment somebody
 *  comments on the stream.
 *
 *  Driven against a running desk, which is the rule the marketplace block
 *  further down states for itself and this one skipped. */
export type DeskOverlay = {
  /** Semi-transparent by design: the picture stays readable underneath, which
   *  is the whole reason these sit over the video rather than beside it. */
  style: { opacity: number; over_video: boolean; anchor: string };
  on_stream: unknown[];
  /** A count of raised hands, not the hands. */
  waiting: number;
  likes: number;
  /** The last six approved room messages, oldest first. */
  comments: { who: string; said: string }[];
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
  /** Absolute. It describes what the printed code encodes, and a code on a
   *  shop door has no origin to be relative to. It was a bare path until the
   *  beacons screen went to link it and found the link resolving against the
   *  console's own origin. */
  scan_url: string;
  /** A path on this API — `<img src>` it against `getBase()`. Unlike the
   *  scan surfaces, fetching this does **not** count as a scan. */
  qr_svg: string;
  created_at: string;
};

/** What succession did. Either control passed to a named person, or the
 *  profile sunset to memorial — frozen rather than orphaned. */
export type Succession = {
  profile_id: string;
  status: string;
  successor_owner?: string | null;
  /** Minted only where there is somebody to hand it to, and shown once. */
  owner_token?: string | null;
  note?: string;
};

export type PackSummary = {
  id: string; industry: string; audience: string; title: string;
  blurb: string | null; publisher: string; price: number; currency: string;
  free: boolean; origin: string; origin_url: string | null; rated: boolean;
  items: number; installs: number;
};

/** Seeding is idempotent, and says so by counting both sides. A press that
 *  reported only `created` would look like it had done nothing the second
 *  time instead of like there was nothing left to do. */
export type PackSeed = {
  created: number;
  skipped: number;
  industries: number;
  packs: unknown[];
};

/** The three lights, and which statuses drive each.
 *
 *  Built from the mapping rather than written beside it — the backend says
 *  why: a legend maintained separately eventually describes a mapping the
 *  code does not have, and it is the legend people trust. */
export type LightLegend = {
  order: string[];
  legend: { light: string; labels: string[]; statuses: string[] }[];
  question: string;
};

/** One trip out to look something up.
 *
 *  `redactions` is the count of private terms stripped from the brief before
 *  it went, and `left_host` says whether anything actually left this machine
 *  at all. Both are the point: a research feature that could not tell you
 *  either would be asking for trust it had not earned. */
export type Excursion = {
  id: string;
  profile_id: string;
  topic: string;
  brief: string;
  redactions: number;
  left_host: boolean;
  findings: string | null;
  learned: boolean;
};

export type PersonGrants = {
  lending?: unknown[];
  borrowing?: unknown[];
  [key: string]: unknown;
};

export type PlaceGrants = {
  surface: string;
  surface_id: string;
  grants: unknown[];
  /** Rendered verbatim. It says the list is yours alone and why a room-wide
   *  view does not exist yet, which is the sort of thing a screen quietly
   *  presenting a short list would otherwise misrepresent as "nothing here". */
  note: string;
};

/** What unfriending answers.
 *
 *  A 200 here does **not** mean a row went away: removing somebody who was
 *  never a friend succeeds with `removed: false` and a reason. Unlike the
 *  comment and listing deletes next door, which 404. A screen reporting
 *  success from the status code alone tells somebody it removed a friendship
 *  that never existed. */
export type FriendRemoval = {
  profile_id: string;
  friend_id: string;
  removed: boolean;
  reason?: string;
};

export type CloudStatus = {
  cloud: boolean;
  model: unknown;
  fallback: string;
  contribution: string;
};

/** The contribution loop, as the owner can see it.
 *
 *  `preview_next` is a **dry run** and is computed whether or not
 *  `opted_in` is true — it is what would leave, not what is leaving. A
 *  screen that renders it under one heading regardless tells an opted-out
 *  owner their next conversation is on its way out. */
export type ContributionView = {
  opted_in: boolean;
  policy: string;
  preview_next: {
    source: string; kind: string; quality: string; purpose: string;
    exchange: { role: string; content: string }[];
  } | null;
  contributed: {
    ref: string; at: string; revoked: boolean;
    payload: Record<string, unknown>;
  }[];
};

export type RevokeResult = {
  opted_in: boolean;
  revoked_count: number;
  /** True vacuously when `revoked` is 0 — nothing ever left, so nothing
   *  needed deleting. Not the same claim as "the gateway confirmed", and a
   *  tick shown for both would be the wrong reassurance. */
  deleted_at_gateway: boolean;
  note: string;
};

export type LicenseGrant = {
  grant_id: string;
  profile_id: string;
  kind: string;
  token: string;
  terms: string | null;
  can_derive: boolean;
};

/** What a derivation actually handed over, and what stayed behind (with the
 *  reason), written at derive time and readable by both parties. */
export type LicenseManifest = {
  carried: Record<string, unknown>;
  withholdings: { item: string; reason: string }[];
};

export type DerivedAgent = {
  derived_profile_id: string;
  owner_id: string;
  licensed_from: string;
  kind: string;
  owner_token: string;
  manifest: LicenseManifest;
};

/** The offer an owner has posted — what their profile is licensed for and
 *  at what price. 404 when there is none, which is a real answer and not an
 *  error: most profiles are not for sale. */
export type LicenseOfferView = {
  profile_id: string;
  kind: string;
  price: number;
  currency: string;
  terms: string | null;
  allow_derivatives: boolean;
};

/** One licence somebody holds on this profile. The owner's view of the sale,
 *  which is a different list from the grants a buyer holds. */
export type LicenseHolder = {
  id: string;
  buyer_id: string;
  kind: string;
  derived_profile_id: string | null;
  revoked: boolean;
  created_at: string;
  manifest: LicenseManifest | null;   // null until an agent is derived
};

export type LedgerEntry = {
  id: string; beneficiary: string; kind: string; ref: string;
  memo: string | null; amount: number; currency: string;
  status: string;            // accrued | paid
  payout_id: string | null;
  created_at: string;
};

export type MoneyTotals = {
  accrued: number; paid: number; lifetime: number;
  by_kind: Record<string, number>;
};

/** The creator statement.
 *
 *  `totals` is **one currency's** figures — the settlement currency named in
 *  `currency` — and `by_currency` holds every currency including that one.
 *  They were a single set of numbers summed across currencies until this
 *  round: ¥100 and $100 came back as `accrued: 200` under whichever currency
 *  had sold most recently. `mixed` is the flag a screen needs before it draws
 *  a figure, because a headline that silently omits a second balance is only
 *  honest if it says so. */
export type EarningsStatement = {
  owner_id: string;
  entries: LedgerEntry[];
  totals: MoneyTotals & { mixed: boolean };
  by_currency: Record<string, MoneyTotals>;
  currencies: string[];
  currency: string;
};

/** One payout, of one currency. `remaining` names the currencies still
 *  holding a balance, so "you have been paid" and "you have been paid some
 *  of it" are distinguishable without a second request. */
export type PayoutReceipt = {
  payout_id: string; owner_id: string; total_amount: number; currency: string;
  entries: number; at: string; remaining: string[]; note: string;
};

/** How this profile and one person are going.
 *
 *  Deliberately narrower than what a rating hands back: `last_seen` and
 *  `contributed` come out of the write and are **not** in the read. The two
 *  answer different questions and a screen that assumed they matched would
 *  render blanks. */
export type Engagement = {
  profile_id: string;
  interactor_id: string;
  score: number;
  interactions: number;
  sessions: number;
  feedback_pos: number;
  feedback_neg: number;
};

/** What a rating answers with — the engagement record plus the two fields
 *  only the write knows. `contributed` is the honest one: it says whether
 *  this thumbs-up actually sent an anonymised exchange to the cloud, which
 *  happens only on `up`, only with the profile opted in, and only where a
 *  gateway is configured. */
export type FeedbackResult = Engagement & {
  last_seen: string | null;
  contributed: boolean;
};

/** The latent picture of one relationship. Owner-only: it is a model of a
 *  named person, and the six dimensions are what the profile behaves from. */
export type PersonaEmbedding = {
  profile_id: string;
  interactor_id: string;
  vector: Record<string, number>;
  version: number;
  updated_at: string;
};

/** An unprompted message that got past all three gates, with the reason the
 *  profile gave itself for sending it. */
export type ProactiveOutreach = {
  reason: string;
  message: {
    id: string; role: string; content: string; status: string;
    flag_reason: string | null; created_at: string;
    watermark?: unknown;
  };
};

/** The window during which no profile may reach out unprompted. Hours in
 *  UTC, 0–23; null on both means no window at all. Set by the person, and
 *  refused to their profile's owner. */
export type QuietHours = {
  id: string;
  quiet_start: number | null;
  quiet_end: number | null;
};

/** What a scanning app receives, as opposed to the page a browser gets.
 *  The same scan either way — including the count, which goes up for both. */
export type DeskScanCard = {
  desk_id: string;
  display_name: string;
  trade: string;
  location: string | null;
  presence: string;
  /** "Live person — not AI", or its opposite. The first thing a scanner is
   *  told, and the sentence the whole desk feature rests on. */
  designation: string;
  human: boolean;
  ai: boolean;
  age_wall: boolean;
  rated: boolean;
  attestation: {
    attestor: string; basis: string; attested_at: string;
    signed: boolean; signature_id: string | null; note: string;
  };
  feed: DeskFeed;
  beacon: { id: string; label: string; location: string | null };
};

/** One direction of one platform. `collect` pulls content in, `publish`
 *  runs the profile out; they are separate rows so an import can never post.
 *  `beacon` is null on a `collect` row, which is how a screen knows not to
 *  offer a QR that would be refused. */
/** Resolving a reference somebody arrived with: `@handle`, `#tag`, or a
 *  beacon id off a printed sticker. A rated profile answers through the age
 *  wall on the direct refs and is omitted entirely from `#tag` browse. */
export type SummonCard = {
  profile_id: string;
  display_name: string;
  handle: string | null;
  purpose: string;
  status: string;
  rated: boolean;
  chat: string;
  note: string | null;
};

export type Summoned = {
  type: "handle" | "tag" | "beacon";
  ref: string;
  profile?: SummonCard;
  profiles?: SummonCard[];
  label?: string;
  location?: string | null;
  scans?: number;
};

/** Anonymous matchmaking between two people — no profile involved. Either
 *  you are matched at once, or you wait. `matched_with` is the other side's
 *  chosen alias and never their name or id: anonymity is the feature. */
export type ConnJoined = {
  status: "matched" | "waiting" | "idle";
  connection_id?: string;
  tier?: string;
  matched_with?: string;
};

/** `from` is `"you"` or the other side's alias — never an id.
 *
 *  A `blocked` message is returned only to the person who sent it, so they
 *  can see what was held back. That rule is only worth anything now that the
 *  route knows who is asking; it used to take the id on trust. */
export type ConnMessage = {
  id: string;
  from: string;
  content: string;
  status: string;
  created_at: string;
};

export type ConnSent = {
  id: string;
  status: string;
  flag_reason: string | null;
};

/** The mark a profile's generated work carries.
 *
 *  `label` comes back with `AI ·` in front of whatever the owner typed, and
 *  that is the point: the designation cannot be designed away. Ask for
 *  "Rosa" and the line is "✦ AI · Rosa". */
export type WatermarkDesign = {
  mark: string;
  label: string;
  line: string;
  /** Whether the owner has set one, or this is the default. */
  custom: boolean;
  always_displayed: boolean;
  disclosure: string;
};

/** One composed post. `content` is present only when the post is approved —
 *  or when the caller is the owner reading their own hold queue. */
export type ProfilePost = {
  id: string;
  profile_id: string;
  surface: string | null;
  topic: string;
  content: string;
  status: string;
  /** Why it was held. Never public: it names the rule the text broke. */
  flag_reason: string | null;
  watermark_id: string;
  created_at: string;
  watermark: { watermark_id: string; kind: string; disclosure: string };
};

/** Somebody contesting that this profile should exist. Opening one restricts
 *  the profile immediately and pending review — `prior_status` is what it
 *  goes back to if the objection is dismissed. */
export type ObjectionRow = {
  id: string;
  profile_id: string;
  /** An out-of-band proof-of-identity reference, not the objector's name. */
  objector_ref: string;
  reason: string | null;
  status: string;
  reattested: number;
  prior_status: string;
  created_at: string;
  resolved_at: string | null;
};

export type Reattested = {
  id: string;
  reattested: boolean;
  note: string;
};

/** Languages a profile can speak. The persona generates *natively* in the
 *  chosen one on every surface — chat, posts, rooms, robot speech — rather
 *  than writing English and translating it afterwards. */
export type LanguageCatalogue = {
  languages: { code: string; label: string }[];
  default: string;
};

/** `mode` is `pre` (already in that language everywhere) or `on_demand`
 *  (translated when asked). Not a display setting: it changes what the model
 *  is asked to produce. */
export type LanguagePref = {
  profile_id: string;
  language: string;
  label: string;
  mode: string;
};

/** `engine: "none"` is the honest answer, not a failure — the offline stub
 *  says it cannot translate rather than handing back the input as though it
 *  had. `note` carries the reason. */
export type Translated = {
  text: string;
  translation: string;
  language: string;
  engine: string;
  note?: string;
};

/** The name a profile answers to. Claiming replaces whatever it had, which
 *  is why this is owner-only: the old handle stops resolving. */
export type HandleClaimed = {
  profile_id: string;
  handle: string;
  summon: string;
};

/** Feedback on the app itself. `mine` is only ever the caller's own words;
 *  `tally` is the public count by category, which is the most a submission
 *  ever contributes to anybody else's view. */
export type FeedbackBoard = {
  mine: { id: string; category: string; message: string; rating: number | null;
          status: string; created_at: string }[];
  tally: Record<string, number>;
  total: number;
  categories: string[];
};

/** Accessibility reports, for the deployment's reviewer. Three answers in
 *  the writer's own words and language — never a name, never a diagnosis:
 *  the table they come from has no submitter column to select. */
export type AccessReports = {
  reports: { id: string; lang: string; doing: string; wall: string;
             help: string | null; status: string; pdi_key: string | null;
             created_at: string }[];
  total: number;
};

/** A third-party catalogue of task or knowledge mods. `audience` says which
 *  kind of thing it stocks — a robot body or a profile. */
export type RegistrySynced = {
  registry: string; name: string; url: string;
  created: number; skipped: number;
  packs: { pack_id: string; title: string; price: number }[];
};

export type PackDetail = {
  id: string; industry: string; audience: string; title: string;
  blurb: string; publisher: string; price: number; currency: string;
  free: boolean; origin: string; origin_url: string; rated: boolean;
  items: number; installs: number; item_titles: string[];
};

export type PackRegistry = {
  key: string; name: string; url: string; audience: string;
  tagline: string; available_packs: number; synced: number;
};

/** An app this profile is connected to. `directions` is what the connection
 *  is *for*: `collect` reads into the profile, `act` lets it do something. */
export type AppConnector = {
  id: string; profile_id: string; provider: string; app: string;
  label: string; capabilities: string[]; directions: string[];
  status: string; collected: number; actions: number;
};

export type ExcursionLearned = {
  source_id: string; already_learned: boolean; note: string;
};

/** The whole steering surface for a profile: the dials on offer, the values
 *  set, and the age/appearance sections that ride on the persona prompt.
 *  `adult_only` dials are reported rather than hidden, so the refusal on a
 *  profile that is not rated has something to point at. */
export type SteeringHub = {
  subject_id: string;
  adult_mode: boolean;
  dials: SteeringDial[];
  values?: Record<string, number>;
  age?: Record<string, unknown>;
  appearance?: Record<string, unknown>;
};

export type GameSession = {
  id: string; profile_id: string; platform: string; platform_label: string;
  game: string; role: string; mode: string; status: string; note?: string;
};

export type GameCallout = {
  session_id: string; role: string; status: string; line: string;
};

export type GameEnded = {
  session_id: string; status: string; callouts: number;
  lobby_emptied: number;
};

/** What `publish` hands back. `watermark` is new: this route stored a post
 *  with no credential at all, which meant the only synthetic media going out
 *  unmarked was the media actually leaving the platform. */
export type SocialPublished = {
  post_id: string; platform: string; surface: string; status: string;
  flag_reason: string | null; content: string | null;
  watermark: { watermark_id: string; kind: string; disclosure: string };
};

export type SocialCollected = {
  connection: string; platform: string; ingested: number;
  total_sources: number; note: string;
};

export type SocialScraped = {
  connection: string; platform: string; url: string; title: string | null;
  ingested: number; total_sources: number; note: string;
};

export type SocialConnection = {
  id: string;
  profile_id: string;
  platform: string;
  direction: string;
  handle: string | null;
  scope: string[];
  status: string;
  collected: number;
  published: number;
  beacon: string | null;
};

export type SocialBeacon = {
  connection: string;
  platform: string;
  handle: string | null;
  /** Where the code actually sends somebody: the account's page on the
   *  platform, or — with no handle to build one from — a QRME summon link.
   *  Worth showing, because the two are very different destinations and the
   *  picture looks identical. */
  presence_url: string;
  qr_svg: string;
};

export interface FeedItem {
  kind: "video" | "offsite" | "room" | "desk" | "party";
  id: string;
  reason: string;
  at: string;
  /** Decided by the server. The client renders it and never overrides it. */
  plays: boolean;
  loop?: boolean;
  note?: string;
  /** video */
  src?: string;
  profile?: { profile_id: string; name: string };
  title?: string;
  said?: string;
  /** offsite */
  facade?: { platform: string; platform_name: string; video_id: string;
             url: string };
  /** room */
  topic?: string;
  channel?: string;
  people?: number;
  entering?: string;
  enter?: string;
  /** desk */
  display_name?: string;
  trade?: string;
  location?: string | null;
  blurb?: string | null;
  presence?: string;
  rated?: boolean;
  portrait?: string | null;
  live?: boolean;
  human?: boolean;
  ai?: boolean;
  ringing?: string;
  ring?: string;
  shop?: {
    shop_id: string; name: string; blurb?: string | null; tag?: string | null;
    offerings: { id: string; kind: string; title: string; price: number;
                 currency: string; availability: string }[];
    open: string;
  } | null;
  /** party — a watch party whose host chose to be found. Counts and a
   *  facade only; joining is each viewer's own press. */
  video?: PartyVideo | null;
  profiles?: number;
  playing?: boolean;
  joining?: string;
  join?: string;
}

/** One page of the public stream. `rules` is the server saying, in words a
 *  screen can show, what it will and will not play without being asked. */
export interface FeedPage {
  items: FeedItem[];
  cursor: string | null;
  counts: { video: number; offsite: number; room: number; desk: number;
            party: number };
  rules: { plays: string; facade: string; public: string };
}

/** Both parameters are optional and neither is sent empty: `viewer=` would be
 *  an account id the server then has to decide is not one. */
const feedQuery = (cursor?: string, viewer?: string) =>
  new URLSearchParams({
    ...(cursor ? { cursor } : {}), ...(viewer ? { viewer } : {}),
  }).toString();

export const api = {
  // `health` used to sit here: the same route, the body thrown away, a
  // boolean returned. Nothing called it — `healthInfo` below returns the
  // version the guard actually needs — and a binding that discards the
  // answer is worse than none, because the next person to want a health
  // check would have found it and lost the version with it. Deleted
  // rather than wired: not every unused binding wants a screen.

  healthInfo: () => req<{ status?: string; version?: string;
                          signup_key?: boolean;
                          footsteps?: number }>("/health"),

  // How to open this studio on a phone: its URL on the local network.
  pair: () => req<PairInfo>("/pair"),

  offlineStatus: () => req<Record<string, unknown>>("/offline/status"),
  // The failure aggregate this backend keeps (qrme/routers/problems.py).
  // Reading is the operator's: QRME_PROBLEMS_KEY as the token, or nothing
  // when asking from the machine the backend runs on.
  problemRows: (key?: string) =>
    req<{ rows: { source: string; app_version: string; platform: string;
                  op: string; status_code: number; day: string; count: number;
                  last_seen: string }[] }>(
      "/v1/problems", key ? { token: key } : {}),
  // The sending half of the same wire, for the screen's own button — the
  // launch-time auto-sender lives in errors.ts and may point at an external
  // collector; this one posts to the backend this console already talks to.
  reportProblems: (body: Record<string, unknown>) =>
    req<{ accepted: boolean; problems: number; failures: number }>(
      "/v1/problems", { method: "POST", body }),

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

  // A character card as a profile seed; what is refused is named.
  importCard: (body: {
    owner_id: string; verification: { birthdate: string };
    card?: Record<string, unknown>; content?: string; plan?: string;
  }) =>
    req<Profile & { owner_token: string; carried: Record<string, unknown>;
                    withholdings: { item: string; reason: string }[] }>(
      "/profiles/import/card", { method: "POST", body }),

  // Rehearsal rooms: practice the hard conversation, nothing remembered.
  openRehearsal: (profileId: string, interactorId: string, scenario: string) =>
    req<{ id: string; scenario: string; turns: number; remembered: boolean }>(
      `/profiles/${profileId}/rehearsal`,
      { method: "POST", body: { interactor_id: interactorId, scenario } }),
  rehearse: (profileId: string, rehearsalId: string, message: string) =>
    req<{ id: string; reply: string; turns: number; remembered: boolean }>(
      `/profiles/${profileId}/rehearsal/${rehearsalId}/say`,
      { method: "POST", body: { message } }),
  closeRehearsal: (profileId: string, rehearsalId: string) =>
    req<{ id: string; turns: number; erased: boolean }>(
      `/profiles/${profileId}/rehearsal/${rehearsalId}`,
      { method: "DELETE" }),

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
                     handle?: string | null; avatar?: string | null;
                     founder?: boolean }[]; founder_handles: string[] }>(
      `/profiles/${profileId}/friends`),
  suggestedFriends: (profileId: string) =>
    // The key is `suggested`. Declaring `suggestions` — in both arms of a
    // union, so neither could match — meant the reader's `?? []` fired every
    // time and the list was permanently empty.
    req<{ profile_id: string; suggested: { profile_id: string;
          display_name: string }[]; ranked_on: string[];
          never_ranked_on: string[]; excluded: string }>(
      `/profiles/${profileId}/friends/suggested`),
  addFriend: (profileId: string, friendId: string, token: string) =>
    req<unknown>(`/profiles/${profileId}/friends`,
      { method: "POST", body: { friend_id: friendId }, token }),
  inbox: (profileId: string, token: string) =>
    req<{ events: InboxEvent[]; unseen: number }>(
      `/profiles/${profileId}/inbox`, { token }),
  inboxSeen: (profileId: string, token: string) =>
    req<{ marked_seen: number }>(`/profiles/${profileId}/inbox/seen`,
      { method: "POST", token }),
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
  uploadMedia: async (profileId: string, file: File, token: string,
                      alt = "") => {
    // Raw bytes, not multipart — the backend reads the kind from the bytes;
    // the filename is a display hint only. `alt` is the uploader's own words
    // for what the file shows, served to people who cannot see it.
    const res = await fetch(getBase() +
      `/profiles/${profileId}/media?filename=${encodeURIComponent(file.name)}` +
      (alt ? `&alt=${encodeURIComponent(alt)}` : ""), {
      method: "POST", body: file,
      headers: { authorization: `Bearer ${token}` },
    });
    const data = await res.json().catch(() => ({}));
    // `detail` here can be the 422 list, which stringifies to "[object
    // Object]" through Error. The sentence beside it is what a person reads.
    if (!res.ok) {
      const body = data as { detail?: unknown; message?: unknown };
      throw new RequestError(res.status, body.detail ?? `upload failed (${res.status})`,
                             body.message);
    }
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
  // -- shops: standalone storefronts (qrme/shops.py). Not desks: no
  // sessions, no connections — offerings, orders, and a ledger entry on
  // fulfilment. Shapes read off a running server.
  // The person's own surfaces: switches, DMs, and the homepage sandbox.
  getFeatures: (profileId: string, token: string) =>
    req<Record<string, boolean>>(`/profiles/${profileId}/features`, { token }),
  setFeature: (profileId: string, feature: string, enabled: boolean,
               token: string) =>
    req<Record<string, boolean>>(`/profiles/${profileId}/features`,
      { method: "PUT", body: { feature, enabled }, token }),
  sendDm: (profileId: string, to: string, body: string, token: string) =>
    req<DmMessage>(`/profiles/${profileId}/messages`,
      { method: "POST", body: { to, body }, token }),
  dmThreads: (profileId: string, token: string) =>
    req<{ threads: DmThread[] }>(`/profiles/${profileId}/messages`, { token }),
  dmThread: (profileId: string, withId: string, token: string) =>
    req<{ with: string; messages: DmMessage[] }>(
      `/profiles/${profileId}/messages?with_id=${encodeURIComponent(withId)}`,
      { token }),
  homepage: (profileId: string, token?: string) =>
    req<Homepage>(`/profiles/${profileId}/homepage`, { token }),
  editHomepage: (profileId: string, body: {
    headline?: string; about?: string; theme?: { bg: string; accent: string };
    links?: { label: string; url: string }[]; top_friends?: string[];
  }, token: string) =>
    req<Homepage>(`/profiles/${profileId}/homepage`,
      { method: "PUT", body, token }),
  listShops: (tag?: string) =>
    req<ShopCard[]>(`/shops${tag ? `?tag=${encodeURIComponent(tag)}` : ""}`),
  shopCard: (shopId: string) => req<ShopDetail>(`/shops/${shopId}`),
  openShop: (body: { profile_id: string; name: string; blurb?: string;
                     tag?: string }, token: string) =>
    req<ShopDetail>(`/shops`, { method: "POST", body, token }),
  addOffering: (shopId: string,
                body: { kind: string; title: string; blurb?: string;
                        price: number; currency?: string;
                        availability?: string }, token: string) =>
    req<ShopOffering>(`/shops/${shopId}/offerings`,
      { method: "POST", body, token }),
  retireOffering: (shopId: string, offeringId: string, token: string) =>
    req<ShopOffering>(`/shops/${shopId}/offerings/${offeringId}`,
      { method: "DELETE", token }),
  placeShopOrder: (shopId: string,
                   body: { offering_id: string; buyer_id: string;
                           quantity?: number; note?: string },
                   token: string) =>
    req<ShopOrder>(`/shops/${shopId}/orders`, { method: "POST", body, token }),
  shopOrderBook: (shopId: string, token: string) =>
    req<ShopOrder[]>(`/shops/${shopId}/orders`, { token }),
  myShopOrders: (buyerId: string, token: string) =>
    req<ShopOrder[]>(`/shops/orders/of/${buyerId}`, { token }),
  advanceShopOrder: (shopId: string, orderId: string,
                     body: { party: string; to: string }, token: string) =>
    req<ShopOrder>(`/shops/${shopId}/orders/${orderId}/advance`,
      { method: "POST", body, token }),
  seedStarters: () =>
    req<{ created: string[]; skipped: string[]; repaired?: string[] }>(
      `/marketplace/seed`, { method: "POST" }),
  listRooms: () =>
    req<{ id: string; topic?: string | null; channel: string;
          participants: number; created_at: string }[]>(`/rooms`),
  // The standing rooms: blueprints shown when the live list is empty,
  // each one press away from being a real room through createRoom.
  roomTemplates: () =>
    req<{ key: string; topic: string; channel: string; pitch: string;
          presence: string }[]>(`/rooms/templates`),
  createRoom: (body: { topic?: string; channel: string;
                       participants: { kind: string; id: string }[] }) =>
    req<{ id: string }>(`/rooms`, { method: "POST", body }),
  // Step into a live room: the token names the joiner, joining twice is
  // being there once, and the table seats eight.
  joinRoom: (roomId: string, token: string) =>
    req<{ id: string; topic?: string | null; channel: string;
          participants: { kind: string; id: string; display: string }[] }>(
      `/rooms/${roomId}/join`, { method: "POST", token }),
  // Step into a standing room — the room, not a copy of it: joins the
  // live one with a seat left, opens it fresh only when nobody is there.
  openStandingRoom: (key: string, profileId: string, token: string) =>
    req<{ id: string; topic?: string | null; channel: string;
          opened: string;
          participants: { kind: string; id: string; display: string }[] }>(
      `/rooms/templates/${key}/open?profile_id=${encodeURIComponent(profileId)}`,
      { method: "POST", token }),
  // Inside a room: read it, speak in it, let the profiles take a turn. All
  // three carry the interactor token, and the speaker is read from it rather
  // than from `sender_id` in the body — which is what let anybody holding a
  // room id post under a named participant's name. The transcript took no
  // token at all, so a room id, which rides on printed stickers, was enough
  // to read everything said in it.
  roomMessages: (roomId: string, token: string) =>
    req<RoomMsg[]>(`/rooms/${roomId}/messages`, { token }),
  sayInRoom: (roomId: string, interactorId: string, message: string,
              token: string) =>
    req<{ message: RoomMsg; replies: RoomMsg[] }>(`/rooms/${roomId}/messages`,
      { method: "POST", body: { sender_id: interactorId, message }, token }),
  advanceRoom: (roomId: string, token: string) =>
    req<{ replies: RoomMsg[] }>(`/rooms/${roomId}/advance`,
      { method: "POST", token }),
  listDesks: () =>
    req<{ id: string; display_name: string; trade: string; location?: string;
          blurb?: string; presence: string; rated: number }[]>(`/desks`),

  // -- the feed (qrme/feed.py): one public stream, three kinds of card.
  //
  // `plays` is the server's, not ours. Footage this deployment holds comes
  // back true; anything on somebody else's platform comes back false and
  // stays a facade until a person presses it, so that scrolling past fifty
  // cards does not announce the viewer to fifty other companies. The client
  // reads that flag and never decides it — see the note in qrme/feed.py.
  // The query is built above rather than inline, and that is not style.
  // `tests/clientpaths.py` reads these literals to decide which routes have a
  // door, and its template-literal pattern follows one level of nested braces.
  // A first draft wrote the `URLSearchParams({ ...(cursor ? { cursor } : {}) })`
  // straight into the template — three levels deep — and `GET /feed` came back
  // doorless while the screen calling it was on screen.
  publicFeed: (cursor?: string, viewer?: string) =>
    req<FeedPage>(`/feed?${feedQuery(cursor, viewer)}`),
  publicFeedItem: (id: string) =>
    req<FeedItem>(`/feed/${encodeURIComponent(id)}`),

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
  // AI for lease: seat somebody else's licensed specialist as a department.
  // The fee accrues to the specialist's owner; the lease is revocable from
  // the owner's side (their licenses list, the same revoke door as grants).
  leaseSpecialist: (orgId: string, body: {
    profile_id: string; name: string; role: string;
  }, token: string) =>
    req<LeaseOut>(`/organizations/${orgId}/lease`,
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

  // The distilled long memory of one person — what survived the window.
  remembrance: (profileId: string, interactorId: string, token: string) =>
    req<Remembrance>(
      `/profiles/${profileId}/memory/${interactorId}/remembrance`, { token }),

  clearMemory: (profileId: string, interactorId: string, token: string) =>
    req<unknown>(`/profiles/${profileId}/memory/${interactorId}`, {
      method: "DELETE", token,
    }),

  // What do you remember about me — answered from the records.
  memoryAccount: (profileId: string, interactorId: string, token: string) =>
    req<MemoryAccount>(
      `/profiles/${profileId}/memory/${interactorId}/account`, { token }),

  // Forget that one thing: the turns that carry the words are deleted and
  // the kept memory is re-folded from what remains.
  forgetMemory: (profileId: string, interactorId: string, about: string,
                 token: string) =>
    req<{ forgotten_turns: number; remembrance_reset: boolean }>(
      `/profiles/${profileId}/memory/${interactorId}/forget`,
      { method: "POST", body: { about }, token }),
  // Strike the turns selected by checkbox — the delete-selected door.
  strikeTurns: (profileId: string, interactorId: string,
                messageIds: string[], token: string) =>
    req<{ struck_turns: number; remembrance_reset: boolean }>(
      `/profiles/${profileId}/memory/${interactorId}/strike`,
      { method: "POST", body: { message_ids: messageIds }, token }),
  // Rewrite one remembered turn in place. A profile turn loses its
  // synthetic-media credential — it must not vouch for rewritten words.
  editTurn: (profileId: string, interactorId: string, messageId: string,
             content: string, token: string) =>
    req<{ turn: MemoryEntry; remembrance_reset: boolean }>(
      `/profiles/${profileId}/memory/${interactorId}/turns/${messageId}`,
      { method: "PUT", body: { content }, token }),
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
  // How many people this profile is talking to. Public on purpose: the count
  // is a fact about the profile, not a secret earned by intimacy, and making
  // somebody get close before they may learn it is what turns an ordinary
  // property of the software into a betrayal.
  profileAttention: (pid: string, interactor?: string) =>
    req<ProfileAttention>(`/profiles/${pid}/attention`
      + (interactor ? `?interactor=${encodeURIComponent(interactor)}` : "")),
  // The same honesty as `profileAttention`, pointed the other way. How much
  // of *your* talking here went to a profile rather than to a person — counts
  // from your own logs, readable by you and by nobody else. There is no owner
  // view of this and there must never be one: the moment a second party can
  // read it, a disclosure becomes a way to find the visitors who have nobody
  // else to talk to.
  solitude: (who: string) =>
    req<Solitude>(`/interactors/${encodeURIComponent(who)}/solitude`),
  // Take the door or close it. Declining is recorded so the offer does not
  // come back — a second asking overrides an answer already given.
  solitudeHandoff: (who: string, accept: boolean) =>
    req<SolitudeDecision>(
      `/interactors/${encodeURIComponent(who)}/solitude/handoff`,
      { method: "POST", body: { accept } }),
  // What would travel, before it travels. Counts and a window, never a word.
  solitudeReferral: (who: string) =>
    req<SolitudeReferral>(
      `/interactors/${encodeURIComponent(who)}/solitude/referral`),
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

  // Connections across the counter — the service the desk exists to give.
  // The desk offers (screen, machine, program, files); only the caller's
  // accept mints the link token, and it comes back to the caller alone.
  openDeskSession: (deskId: string, body: { caller_id: string;
    ring_id?: string }, token: string) =>
    req<DeskSession>(`/desks/${deskId}/sessions`,
      { method: "POST", body, token }),
  deskSessions: (deskId: string, token: string) =>
    req<DeskSession[]>(`/desks/${deskId}/sessions`, { token }),
  deskSession: (sessionId: string, token: string) =>
    req<DeskSession>(`/desk-sessions/${sessionId}`, { token }),
  offerDeskConnection: (sessionId: string, body: { kind: string;
    target: string; scope?: string }, token: string) =>
    req<DeskConnection>(`/desk-sessions/${sessionId}/connections`,
      { method: "POST", body, token }),
  answerDeskConnection: (sessionId: string, connectionId: string,
    accept: boolean, token: string) =>
    req<DeskConnection>(
      `/desk-sessions/${sessionId}/connections/${connectionId}/answer`,
      { method: "POST", body: { accept }, token }),
  endDeskConnection: (sessionId: string, connectionId: string,
    token: string) =>
    req<DeskConnection>(
      `/desk-sessions/${sessionId}/connections/${connectionId}/end`,
      { method: "POST", token }),
  closeDeskSession: (sessionId: string, token: string) =>
    req<DeskSession>(`/desk-sessions/${sessionId}/close`,
      { method: "POST", token }),
  myDeskSessions: (interactorId: string, token: string) =>
    req<DeskSession[]>(`/interactors/${interactorId}/desk-sessions`,
      { token }),

  // ---------------------------------------------------------------------
  // The other side of a desk.
  //
  // Everything above is the host's: open one, set your presence, read who
  // rang, accept a guest. None of it is the visitor's, and the visitor is the
  // person the feature is *for* — somebody standing in front of an empty
  // chair with a sign on it saying to ring the bell.
  //
  // Two of these take no token and it is deliberate both times. The card is
  // public because a desk is a shopfront. The bell is public because the
  // visitor at an empty chair is exactly the person who has no account yet —
  // an 18+ stream is the one exception, since an anonymous ping channel to an
  // adult performer is not something to hand out.
  // ---------------------------------------------------------------------

  visitDesk: (deskId: string) => req<DeskCard>(`/desks/${deskId}`),
  ringBell: (deskId: string, body: { caller_id?: string; note?: string }) =>
    req<BellRung>(`/desks/${deskId}/bell`, { method: "POST", body }),
  // `guest` needs an account and this binding does not carry one, because a
  // guest request is `askToComeUp` below — the route answers 401 to an
  // anonymous `mode: "guest"` rather than quietly seating them in the
  // audience, which is the honest refusal.
  joinDesk: (deskId: string, mode: "audience" | "guest" = "audience",
             token?: string) =>
    req<DeskJoined>(`/desks/${deskId}/join`,
      { method: "POST", body: { mode }, ...(token ? { token } : {}) }),

  deskOverlay: (deskId: string, token: string) =>
    req<DeskOverlay>(`/desks/${deskId}/overlay`, { token }),
  deskLivePerson: (deskId: string) =>
    req<LivePerson>(`/desks/${deskId}/live-person`),

  deskBeacons: (deskId: string, token: string) =>
    req<{ beacons: DeskBeacon[] }>(`/desks/${deskId}/beacons`, { token }),
  placeDeskBeacon: (deskId: string, body: { label: string; location?: string },
    token: string) =>
    req<DeskBeacon>(`/desks/${deskId}/beacons`, { method: "POST", body, token }),
  // No token: a scan is a stranger with a camera, and this is that same
  // scan shaped for an app rather than a browser. It increments the count
  // like any other — there is no read of a beacon that doesn't.
  deskScanCard: (beaconId: string) =>
    req<DeskScanCard>(`/d/${beaconId}/card`),
  pickUpDeskBeacon: (beaconId: string, token: string) =>
    req<{ picked_up: boolean }>(`/desk-beacons/${beaconId}`,
      { method: "DELETE", token }),

  // ---------------------------------------------------------------------
  // Leaving a *profile* somewhere. A different family from the desk beacons
  // above, and easy to confuse with them: `/desk-beacons/…` points at a live
  // person, `/beacons/…` points at a profile. Both print as a QR sticker.
  //
  // All three owner routes are owner-only, and each of those checks was put
  // there because the route had shipped without it: placing was anybody's,
  // so a stranger could print stickers pointing at somebody else's profile;
  // the list carries `label` and `location` as free text — "the back table at
  // the Tuesday meeting" — which is a list of physical places a person
  // frequents, and it was readable from the profile id alone; and picking one
  // up was a way to switch off somebody else's printed stickers, with the
  // paper still on the wall and nothing to see wrong with it.
  // ---------------------------------------------------------------------

  profileBeacons: (profileId: string, token: string) =>
    req<PlacedBeacon[]>(`/profiles/${profileId}/beacons`, { token }),
  // `mode: "room"` is refused outright on a rated profile rather than
  // downgraded — somebody who asked for a shared room and silently got
  // private threads would not find out until the fortieth scanner was
  // talking to themselves.
  placeBeacon: (profileId: string,
                body: { label: string; location?: string; mode?: string;
                        topic?: string }, token: string) =>
    req<ProfileBeacon>(`/profiles/${profileId}/beacons`,
      { method: "POST", body, token }),
  // Deactivated, not deleted: the printed paper still exists, so the code has
  // to keep answering — with nothing.
  pickUpBeacon: (beaconId: string, token: string) =>
    req<{ id: string; active: boolean }>(`/beacons/${beaconId}`,
      { method: "DELETE", token }),
  // No token: this is a stranger with a camera pointed at a sticker, which is
  // the whole point of leaving one. On a rated profile it returns the age
  // wall and *nothing else* — not the name, not the portrait — so an overlay
  // can draw the refusal without ever having held what it refuses.
  beaconCard: (beaconId: string) =>
    req<BeaconScanCard>(`/b/${beaconId}/card`),

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
  // Both take a token now. These routes stopped being open when listings
  // gained claimants: moving somebody's listing to another city is a quieter
  // version of taking it down, so it is gated the same way. The bindings had
  // no token parameter at all, which was harmless only because no screen
  // called them — a tokenless call would now be a 401 the moment one did.
  placeListing: (listingId: string,
                 body: { locality: string; region?: string; remote?: boolean },
                 token: string) =>
    req<Place>(`/marketplace/listings/${listingId}/place`,
      { method: "PUT", body, token }),
  unplaceListing: (listingId: string, token: string) =>
    req<{ listing_id: string; place: null }>(
      `/marketplace/listings/${listingId}/place`,
      { method: "DELETE", token }),

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

  // One anchor, two names: the id of a posted video, or `video_url` — a
  // pasted link that faces the same platform allowlist a wall post's does.
  startWatchParty: (body: { post_id?: string; video_url?: string;
                            host_id: string; title?: string },
                    token: string) =>
    req<WatchParty>("/watch-parties", { method: "POST", body, token }),

  // The browse door. Public means public: no token. The id on each card is
  // a join door, not a key — chat and member names stay members-only.
  publicWatchParties: () =>
    req<{ parties: PublicParty[] }>("/watch-parties/public", {}),

  // Host only, both directions. Publishing is a deliberate act; taking it
  // back closes the browse door and the id keeps working.
  publishWatchParty: (partyId: string, token: string) =>
    req<WatchParty>(`/watch-parties/${partyId}/listing`,
                    { method: "POST", token }),
  unpublishWatchParty: (partyId: string, token: string) =>
    req<WatchParty>(`/watch-parties/${partyId}/listing`,
                    { method: "DELETE", token }),

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
  setAvatar: (profileId: string, asset: string, token: string,
              motionStyle?: string) =>
    req<Avatar>(`/profiles/${profileId}/avatar`,
      { method: "PUT",
        body: motionStyle ? { asset, motion_style: motionStyle } : { asset },
        token }),

  avatarMarket: () =>
    req<{ sources: { key: string; name: string; how: string }[]; note: string }>(
      "/avatars/market"),
  importAvatar: (profileId: string, body: { source: string; asset: string;
                                            extra?: string[];
                                            torso?: string },
                 token: string) =>
    req<Avatar>(`/profiles/${profileId}/avatar/import`,
      { method: "POST", body, token }),

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
  // A one-time, minutes-long handoff of the export to another device: the
  // QR carries the ticket URL, never the owner token.
  exportTicket: (profileId: string, token: string) =>
    req<{ ticket: string; url: string; qr_svg: string; expires_at: string;
          single_use: boolean; note: string }>(
      `/profiles/${profileId}/export/ticket`, { method: "POST", token }),
  // The redeeming side, on the device the QR was scanned into. Tokenless:
  // the single-use ticket is the whole authority.
  exportHandoff: (profileId: string, ticket: string) =>
    req<Record<string, unknown>>(
      `/profiles/${profileId}/export/handoff/${ticket}`),

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
  // The objector's own view: what happened, who did it, when. Public,
  // because the party who raised the case has no account by design — and
  // carrying no free text, which is what keeps `objectionAudit` gated.
  objectionTimeline: (objectionId: string) =>
    req<ObjectionTimeline>(`/objections/${objectionId}/timeline`),
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

  // The whole market, including what nobody can buy yet. `announced` rows
  // are listed so an owner can see a body coming and are refused at bind
  // with a 409 that names the status — a 404 would be a lie about a machine
  // its maker has publicly shown.
  robotCatalogue: () => req<RobotCatalogue>("/robotics/catalog"),

  // The connections bracket: what a body is taught, and what it is plugged
  // into. A task pack installed on a robot turns each of its tasks into a
  // commandable verb, capability-checked against the catalogue — a vacuum
  // cannot be taught to fetch. The connected-apps catalogue is the other
  // half: the services an agent can collect from, act on, or produce into.
  connectorCatalogue: () => req<ConnectorCatalogue>("/connectors/catalog"),
  packs: (audience?: string) =>
    req<PackRow[]>(`/packs${audience ? `?audience=${audience}` : ""}`),
  installedPacks: (profileId: string, token: string) =>
    req<InstalledPack[]>(`/profiles/${profileId}/packs`, { token }),
  installPack: (packId: string,
                body: { profile_id: string; robot_id?: string;
                        accept_price?: boolean },
                token: string) =>
    req<{ pack_id: string; installed: boolean; tasks?: string[] }>(
      `/packs/${packId}/install`, { method: "POST", body, token }),
  uninstallPack: (profileId: string, packId: string, token: string) =>
    req<{ removed: number }>(`/profiles/${profileId}/packs/${packId}`,
      { method: "DELETE", token }),
  uninstallRobotPack: (robotId: string, packId: string, token: string) =>
    req<{ removed: number }>(`/robots/${robotId}/packs/${packId}`,
      { method: "DELETE", token }),
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

  // The personality nobody can move: while the lock stands, no steering
  // write lands — the owner's own slip included. The key is the owner's.
  lockSteering: (profileId: string, reason: string | null, token: string) =>
    req<SteeringLock>(`/profiles/${profileId}/steering/lock`,
      { method: "POST", body: reason ? { reason } : {}, token }),
  unlockSteering: (profileId: string, token: string) =>
    req<{ subject_id: string; lock: null }>(
      `/profiles/${profileId}/steering/lock`, { method: "DELETE", token }),

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

  // The console could *list* credentials and reproof them, and could do
  // nothing else — not enrol one, not revoke one, not read the rules, not
  // mint an envelope, not sign it, not check a package somebody handed over.
  // `Referrals` said so out loud and had no button behind the sentence:
  // "None enrolled. The ceremony can enrol one."
  //
  // Two of these take no token on purpose, and the reason is different each
  // time. `signingPolicy` is public because a counterparty deciding whether
  // to accept a signature must be able to read the rules without an account
  // here. `verifyPackage` is public because the whole claim of the scheme is
  // that the evidence stands on its own arithmetic — a verification that
  // needed our blessing would be us vouching, which is the opposite.
  signingPolicy: () => req<SigningPolicy>("/signatures/policy"),
  enrollOptions: (displayName: string, token: string) =>
    req<EnrollOptions>("/signatures/enroll/options",
      { method: "POST", body: { display_name: displayName }, token }),
  // `challenge` is echoed back from the options above rather than re-derived:
  // the server is checking that this registration answers the challenge it
  // just issued, which is what stops one being replayed.
  enrollCredential: (body: { credential_id: string;
                             attestation_object: string;
                             client_data_json: string; challenge: string;
                             proofing_level?: string; display_name?: string;
                             proofing_method?: string; proofing_ref?: string;
                             proofing_attestor?: string }, token: string) =>
    req<SigningCredential>("/signatures/enroll",
      { method: "POST", body, token }),
  // Going forward only. Signatures already made stay verifiable, because
  // their public key lives in the evidence rather than in this table — which
  // is also why revoking cannot be used to disown something already signed.
  revokeCredential: (rowId: string, token: string) =>
    req<SigningCredential>(`/signatures/credentials/${rowId}`,
      { method: "DELETE", token }),
  requestSignature: (body: { document: string; meaning: string;
                             display_text: string; tier?: string;
                             binding_kind?: string; binding_ref?: string },
                     token: string) =>
    req<SignatureEnvelope>("/signatures/request",
      { method: "POST", body, token }),
  signEnvelope: (body: { envelope_id: string; credential_id: string;
                         signature: string; authenticator_data: string;
                         client_data_json: string; transport?: string;
                         platform?: string }, token: string) =>
    req<SignatureResult>("/signatures/sign",
      { method: "POST", body, token }),
  verifyPackage: (pkg: Record<string, unknown>) =>
    req<VerifyVerdict>("/signatures/verify",
      { method: "POST", body: { package: pkg } }),
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

  // ---------------------------------------------------------------------
  // A lobby, and the handoff.
  //
  // The lobby's whole design is in one sentence it publishes: *everything
  // in this lobby observes and talks; nothing in it plays*. The `never`
  // list spells that out twelve ways, each one closing a route somebody
  // would otherwise argue for — a console of its own, a second controller,
  // a Bluetooth pad, a capture card. The console renders those rather than
  // paraphrasing, because each is an argument somebody made.
  //
  // The handoff is the *lighter* sibling of a referral: consented rather
  // than signed, revocable rather than one-time, and purged on revoke. Two
  // ways to hand a conversation on, and the difference is the point.
  // ---------------------------------------------------------------------

  lobbyVocabulary: () => req<LobbyVocabulary>("/gaming/lobby/vocabulary"),
  lobby: (sessionId: string, token: string) =>
    req<Lobby>(`/gaming/sessions/${sessionId}/lobby`, { token }),
  // `member_kind`, not `kind`. A player seats only themselves — an id in a
  // body is a claim, and the route checks it against the token.
  takeSeat: (sessionId: string,
             body: { member_kind: string; member_id: string; role: string;
                     callsign?: string }, token: string) =>
    req<Seat>(`/gaming/sessions/${sessionId}/lobby`,
      { method: "POST", body, token }),
  // A DELETE with a body, like retracting a message: the route has to know
  // which member is leaving.
  leaveLobby: (sessionId: string, memberId: string, token: string) =>
    req<{ id: string; seated: boolean }>(
      `/gaming/sessions/${sessionId}/lobby`,
      { method: "DELETE", body: { member_id: memberId }, token }),
  // What a synthetic member is *told* about its own position — including
  // that some of the others are synthetic too. Shown to the owner because
  // a lobby that reads as five friends when it is one player and four
  // generated voices is the impression this product must not create.
  lobbyContext: (sessionId: string, token: string) =>
    req<LobbyContext>(`/gaming/sessions/${sessionId}/lobby/context`,
      { token }),

  handoff: (body: { interactor_id: string; provider_id: string;
                    profile_id?: string; consent: boolean }, token: string) =>
    req<HandoffMade>("/handoffs", { method: "POST", body, token }),
  openHandoff: (handoffId: string, token: string) =>
    req<{ id: string; package: HandoffPackage | null }>(
      `/handoffs/${handoffId}?token=${encodeURIComponent(token)}`),
  // Revoking purges the package, not just the access. The response says
  // `revoked`, and a later read 403s.
  revokeHandoff: (handoffId: string, token: string) =>
    req<{ id: string; revoked: boolean }>(`/handoffs/${handoffId}`,
      { method: "DELETE", token }),

  // ---------------------------------------------------------------------
  // An audience, and what it pays.
  //
  // Two tiers only — `follow` (free) and `paid` — and paid asks for two
  // things a careless client would skip: `accept_price` matching the price
  // exactly, and a `beneficiary`. **Nothing renews on a timer.** A period
  // is charged when somebody presses renew, which is why the console has a
  // button for it rather than a schedule: a deployment left running does
  // not accrue charges nobody authorised and nobody saw.
  //
  // Worth knowing, because the two differ: a **gift** reads its
  // beneficiary from the subject (`commerce.beneficiary_of`, so a giver
  // cannot redirect money meant for a performer), while a **subscription**
  // takes one from the body. The console sends the profile's own account
  // and says so.
  // ---------------------------------------------------------------------

  subscriptions: (token: string) =>
    req<{ subscriptions: Subscription[] }>("/subscriptions", { token }),
  // Named apart from `subscribe`, which joins a **plan**. Following a
  // creator and paying for the product are different things, and one verb
  // for both is how somebody ends up cancelling the wrong one.
  follow: (kind: string, subjectId: string,
           body: { tier: string; price?: number; accept_price?: number;
                   beneficiary?: string }, token: string) =>
    req<Subscription>(`/${kind}/${subjectId}/subscribe`,
      { method: "POST", body, token }),
  unfollow: (kind: string, subjectId: string, token: string) =>
    req<Subscription>(`/${kind}/${subjectId}/subscribe`,
      { method: "DELETE", body: {}, token }),
  // Explicit, and the only way a period is ever charged.
  renewSubscription: (subId: string, beneficiary: string, token: string) =>
    req<Subscription>(`/subscriptions/${subId}/renew`,
      { method: "POST", body: { beneficiary }, token }),
  subscribers: (kind: string, subjectId: string, token: string) =>
    req<{ subscribers: Subscription[] }>(`/${kind}/${subjectId}/subscribers`,
      { token }),

  gifts: (kind: string, subjectId: string, token: string) =>
    req<GiftsView>(`/${kind}/${subjectId}/gifts`, { token }),
  // No beneficiary field: it is read from the subject, so a giver cannot
  // point somebody else's gift at their own balance.
  sendGift: (kind: string, subjectId: string,
             body: { amount: number; note?: string }, token: string) =>
    req<Gift>(`/${kind}/${subjectId}/gift`,
      { method: "POST", body, token }),

  audience: (kind: string, targetId: string, token?: string) =>
    req<AudienceView>(`/${kind}/${targetId}/audience`, { token }),
  // `sales(token)` next door reads the seller's side of the same ledger;
  // this is the buyer's. Two names because they are two questions.
  myOrders: (token: string) => req<{ orders: Order[] }>("/orders", { token }),

  // ---------------------------------------------------------------------
  // Connections to the world: a platform connection, and the code that
  // points at it.
  //
  // A connection has a **direction**, and the two never overlap: `collect`
  // pulls an account's content in to grow the profile, `publish` runs the
  // profile out on the platform. Separate rows on purpose, so a read-only
  // import can never also post. Only a `publish` connection has a beacon —
  // asking a `collect` one for its QR is a 409, and the list says which is
  // which by giving `beacon: null`, so a screen never has to find out by
  // being refused.
  //
  // The QR here points at the **platform**, not at QRME: `presence_url` is
  // the account's own page. Only when there is no handle does it fall back
  // to a QRME summon link. That is the opposite of a placed beacon, whose
  // code always lands on QRME — the same picture, two different
  // destinations, which is worth saying on the screen rather than leaving
  // somebody to scan it and find out.
  // ---------------------------------------------------------------------

  // ---------------------------------------------------------------------
  // Arriving, and talking to a stranger.
  //
  // `summon` is public and has to be: it is what a scanned sticker or a
  // shared @handle resolves through, and the person following one has no
  // account. A rated profile answers it through the age wall.
  //
  // The connection routes are the opposite — every one of them carries the
  // interactor's own token. They took none at all until this round: the
  // `interactor_id` in the body was read as *who is asking*, when all it ever
  // said was *whose turn this is meant to be*. Two public ids were enough to
  // speak as either party, read the pair's whole conversation including the
  // blocked messages kept back for their sender, and end it — and `end` did
  // not even need that, because its check was skipped entirely when no id was
  // supplied.
  //
  // The ids still ride in the body and the query string: three shipped native
  // clients send them, and a 422 on upgrade is a worse answer than not
  // believing them. They are ignored.
  // ---------------------------------------------------------------------

  // ---------------------------------------------------------------------
  // The mark, and contesting it.
  //
  // `watermarkDesign` is public because every render of this profile's work
  // carries the line, so anyone looking at one can check what it should say.
  // Setting it is the owner's, and whatever they set, the answer comes back
  // with the AI designation in front — it is not a field they can empty.
  //
  // `profilePosts` is public too, and *published* is the word doing the work
  // there: a post the strict filter held, or one the owner set to approve by
  // hand, is the owner's queue and not a publication. It used to return every
  // row to anybody, `flag_reason` included.
  //
  // The objection routes are the owner's side of somebody contesting that
  // their profile should exist at all. Opening one is public and elsewhere;
  // these two are what the owner does about it, and re-attesting is the only
  // move they have — resolving is the reviewer's, deliberately, so an owner
  // cannot adjudicate an objection against their own profile.
  // ---------------------------------------------------------------------

  // ---------------------------------------------------------------------
  // The words it uses, and the name it answers to.
  //
  // `languages` is a static registry and public. The rest are the owner's.
  //
  // `claimHandle` in particular: it took **no credential at all**, and the
  // damage was not that a stranger could give a profile a second name — it is
  // that claiming one deletes whatever the profile had. So `@rosa` stopped
  // resolving, `@notrosa` resolved to Rosa, and every printed reference and
  // shared link that named her went dead at once. The three beacon routes
  // just below it in the same file were given this check in an earlier pass;
  // this one was missed.
  // ---------------------------------------------------------------------

  // ---------------------------------------------------------------------
  // The last of the backlog: feedback, mod registries, connected apps,
  // excursions, the steering hub, playing alongside somebody, and the two
  // halves of a social connection.
  //
  // `publish` is the one worth reading twice. It writes a post to a platform
  // QRME does not run, and it used to store that post with **no watermark
  // id** while the in-app `compose` stamped one — so the only synthetic media
  // leaving the building was the media with no credential on it. It also ran
  // the profile's own maturity filter where `compose` forces `strict`, so a
  // profile set to `open` was held to the loosest rule on the way out.
  // ---------------------------------------------------------------------

  feedback: (token?: string) =>
    req<FeedbackBoard>("/feedback", token ? { token } : {}),
  sendFeedback: (body: { category: string; message: string; rating?: number },
                 token?: string) =>
    req<{ id: string; category: string; status: string; note: string }>(
      "/feedback", { method: "POST", body, ...(token ? { token } : {}) }),

  // The accessibility door. The POST is deliberately tokenless — the person
  // it exists for may be the person the signup shut out — and the GET takes
  // the *reviewer* token, never an owner's: reports are read by whoever
  // stands for the deployment, same role that adjudicates objections.
  sendAccessReport: (body: { doing: string; wall: string; help?: string;
                             lang?: string }) =>
    req<{ id: string; status: string; note: string }>(
      "/access/reports", { method: "POST", body }),
  accessReports: (reviewerToken: string) =>
    req<AccessReports>("/access/reports", { token: reviewerToken }),

  packRegistries: (token: string) =>
    req<PackRegistry[]>("/packs/registries", { token }),
  // `created` and `skipped`, not a single count: syncing is idempotent, and
  // the difference between "two new" and "two already had" is the whole
  // reason to press it twice.
  syncRegistry: (key: string, token: string) =>
    req<RegistrySynced>(`/packs/registries/${key}/sync`,
      { method: "POST", token }),
  // The shop window: metadata plus item *titles*. The contents are the
  // product and arrive by installing. A rated pack needs an age-verified
  // caller even for the window.
  pack: (packId: string, token?: string) =>
    req<PackDetail>(`/packs/${packId}`, token ? { token } : {}),

  profileApps: (profileId: string, token: string) =>
    req<AppConnector[]>(`/profiles/${profileId}/apps`, { token }),
  connectApp: (profileId: string,
               body: { provider: string; app: string;
                       capabilities?: string[] }, token: string) =>
    req<AppConnector>(`/profiles/${profileId}/apps`,
      { method: "POST", body, token }),

  excursions: (profileId: string, token: string) =>
    req<Excursion[]>(`/profiles/${profileId}/excursions`, { token }),
  // `redactions` and `left_host` on the answer are the point of the feature:
  // what was stripped before the question went out, and whether it went out.
  startExcursion: (profileId: string,
                   body: { topic: string; question: string;
                           private?: string[] }, token: string) =>
    req<Excursion>(`/profiles/${profileId}/excursions`,
      { method: "POST", body, token }),
  learnFromExcursion: (excursionId: string, token: string) =>
    req<ExcursionLearned>(`/excursions/${excursionId}/learn`,
      { method: "POST", token }),

  steeringHub: (profileId: string, token: string) =>
    req<SteeringHub>(`/profiles/${profileId}/steering/hub`, { token }),
  setSteeringHub: (profileId: string, body: Record<string, unknown>,
                   token: string) =>
    req<SteeringHub>(`/profiles/${profileId}/steering/hub`,
      { method: "PUT", body, token }),

  gameSessions: (profileId: string, token: string) =>
    req<GameSession[]>(`/profiles/${profileId}/gaming/sessions`, { token }),
  startGameSession: (profileId: string,
                     body: { platform: string; game: string; role?: string;
                             mode?: string }, token: string) =>
    req<GameSession>(`/profiles/${profileId}/gaming/sessions`,
      { method: "POST", body, token }),
  gameCallout: (sessionId: string, situation: string, token: string) =>
    req<GameCallout>(`/gaming/sessions/${sessionId}/callout`,
      { method: "POST", body: { situation }, token }),
  endGameSession: (sessionId: string, token: string) =>
    req<GameEnded>(`/gaming/sessions/${sessionId}/end`,
      { method: "POST", token }),

  collectSocial: (cid: string, items: { title?: string; content: string }[],
                  token: string) =>
    req<SocialCollected>(`/social/${cid}/collect`,
      { method: "POST", body: { items }, token }),
  scrapeSocial: (cid: string, token: string) =>
    req<SocialScraped>(`/social/${cid}/scrape`, { method: "POST", token }),
  publishSocial: (cid: string, body: { topic: string; content: string },
                  token: string) =>
    req<SocialPublished>(`/social/${cid}/publish`,
      { method: "POST", body, token }),

  languages: () => req<LanguageCatalogue>("/languages"),
  profileLanguage: (profileId: string) =>
    req<LanguagePref>(`/profiles/${profileId}/language`),
  setProfileLanguage: (profileId: string,
                       body: { language: string; mode: string },
                       token: string) =>
    req<LanguagePref>(`/profiles/${profileId}/language`,
      { method: "PUT", body, token }),
  // Anything the owner ran across — an interactor's message, a room turn, a
  // listing — into the profile's language, using the profile's own model.
  translate: (profileId: string, text: string, to: string | undefined,
              token: string) =>
    req<Translated>(`/profiles/${profileId}/translate`,
      { method: "POST", body: { text, ...(to ? { to } : {}) }, token }),
  claimHandle: (profileId: string, handle: string, token: string) =>
    req<HandleClaimed>(`/profiles/${profileId}/handle`,
      { method: "PUT", body: { handle }, token }),
  composePost: (profileId: string,
                body: { topic: string; surface?: string }, token: string) =>
    req<ProfilePost & { content: string | null }>(
      `/profiles/${profileId}/compose`, { method: "POST", body, token }),

  watermarkDesign: (profileId: string) =>
    req<WatermarkDesign>(`/profiles/${profileId}/watermark`),
  setWatermarkDesign: (profileId: string,
                       body: { mark?: string; label?: string },
                       token: string) =>
    req<WatermarkDesign>(`/profiles/${profileId}/watermark`,
      { method: "PUT", body, token }),
  // With the owner's token this includes the hold queue; without it, only
  // what is actually published.
  profilePosts: (profileId: string, token?: string) =>
    req<ProfilePost[]>(`/profiles/${profileId}/posts`,
      token ? { token } : {}),
  profileObjections: (profileId: string, token: string) =>
    req<ObjectionRow[]>(`/profiles/${profileId}/objections`, { token }),
  reattestBasis: (profileId: string, objectionId: string, token: string) =>
    req<Reattested>(
      `/profiles/${profileId}/objections/${objectionId}/attest`,
      { method: "POST", token }),

  summon: (ref: string) =>
    req<Summoned>(`/summon?ref=${encodeURIComponent(ref)}`),
  joinQueue: (body: { interactor_id: string; tier: string; alias?: string },
              token: string) =>
    req<ConnJoined>("/connections/join", { method: "POST", body, token }),
  // What happened to my wait. The match is made by whichever side arrives
  // second, so the waiter polls this — never join again, which would
  // re-queue them.
  myConnection: (token: string) =>
    req<ConnJoined>("/connections/mine", { token }),
  connectionMessages: (connectionId: string, interactorId: string,
                       token: string) =>
    req<ConnMessage[]>(
      `/connections/${connectionId}/messages`
      + `?interactor_id=${encodeURIComponent(interactorId)}`, { token }),
  sendToConnection: (connectionId: string,
                     body: { interactor_id: string; message: string },
                     token: string) =>
    req<ConnSent>(`/connections/${connectionId}/messages`,
      { method: "POST", body, token }),
  // Either side may end it — either side, not anybody.
  endConnection: (connectionId: string, interactorId: string, token: string) =>
    req<{ id: string; status: string; microphones_returned: number }>(
      `/connections/${connectionId}/end`
      + `?interactor_id=${encodeURIComponent(interactorId)}`,
      { method: "POST", token }),

  socialConnections: (profileId: string, token: string) =>
    req<SocialConnection[]>(`/profiles/${profileId}/social`, { token }),
  connectSocial: (profileId: string,
                  body: { platform: string; direction: string;
                          handle?: string; scope?: string[] },
                  token: string) =>
    req<SocialConnection>(`/profiles/${profileId}/social`,
      { method: "POST", body, token }),
  disconnectSocial: (cid: string, token: string) =>
    req<{ disconnected: boolean }>(`/social/${cid}`,
      { method: "DELETE", token }),
  socialBeacon: (cid: string) =>
    req<SocialBeacon>(`/social/${cid}/beacon`),

  // ---------------------------------------------------------------------
  // One person, and what reaching out to them costs.
  //
  // Three separate gates stand between a profile and an unprompted message,
  // and they refuse in three different words because they are three
  // different facts:
  //
  //   403  the owner never turned proactive outreach on at all
  //   429  "awaiting a reply" — it already reached out and heard nothing
  //   429  "rate cap" — it reached out recently and may not again yet
  //   429  "quiet hours" — the recipient's window, set by the recipient
  //
  // The last one is the one worth knowing: **the owner cannot set it.**
  // Sending it with an owner token is a 403. The person being reached out
  // to holds their own window, which is the only arrangement in which it
  // means anything.
  //
  // Two surfaces here took no token at all until this round. Both do now:
  // a rating is gated on the rater's own token, because a rating in
  // somebody else's name is a lie about what they thought *and* the trigger
  // for contributing their exchange to the cloud; and the engagement record
  // is gated on the owner or that person, because it is a record of how
  // often somebody talks to a profile.
  // ---------------------------------------------------------------------

  engagement: (profileId: string, interactorId: string, token: string) =>
    req<Engagement>(`/profiles/${profileId}/engagement/${interactorId}`,
      { token }),
  // The rater's token, not the owner's.
  rateExchange: (profileId: string, interactorId: string,
                 rating: "up" | "down", token: string) =>
    req<FeedbackResult>(
      `/profiles/${profileId}/interactions/${interactorId}/feedback`,
      { method: "POST", body: { rating }, token }),
  personaEmbedding: (profileId: string, interactorId: string, token: string) =>
    req<PersonaEmbedding>(`/profiles/${profileId}/embedding/${interactorId}`,
      { token }),
  reachOut: (profileId: string, interactorId: string, token: string) =>
    req<ProactiveOutreach>(`/profiles/${profileId}/proactive/${interactorId}`,
      { method: "POST", token }),
  // The recipient's own token. An owner sending this is refused, and that
  // refusal is the feature.
  setQuietHours: (interactorId: string,
                  body: { quiet_start: number | null;
                          quiet_end: number | null }, token: string) =>
    req<QuietHours>(`/interactors/${interactorId}/quiet-hours`,
      { method: "PUT", body, token }),

  // ---------------------------------------------------------------------
  // What leaves this deployment, and on what terms.
  //
  // Two different kinds of leaving, and the difference is worth keeping
  // straight. A **contribution** sends an anonymised exchange to the shared
  // model: no ids, the persona name replaced, and a random ref so the item
  // can be deleted at the gateway without identifying anybody. A **licence**
  // sends the profile itself — somebody else acquires the right to consult
  // it, or to derive a whole new agent seeded from its persona.
  //
  // The contribution view is a **dry run**: `preview_next` is computed
  // whether or not the profile is opted in, so it says what *would* leave
  // rather than what is about to. Rendering it without that distinction
  // tells an opted-out owner their next conversation is going out.
  // ---------------------------------------------------------------------

  cloudStatus: () => req<CloudStatus>("/cloud/status"),
  contributionView: (profileId: string, token: string) =>
    req<ContributionView>(`/profiles/${profileId}/cloud-contribution`,
      { token }),
  // Stops future contributions *and* asks the gateway to delete past ones by
  // their refs. `deleted_at_gateway` is true vacuously when nothing ever
  // left, which is worth saying apart from "the gateway confirmed".
  revokeContributions: (profileId: string, token: string) =>
    req<RevokeResult>(`/profiles/${profileId}/cloud-contribution/revoke`,
      { method: "POST", token }),

  // The buyer's token, not the owner's. A licence permitting derivatives is
  // refused to a buyer under 18 **here**, at the till — the fee moves at
  // sale time, so refusing at delivery would leave somebody paid for
  // something the server will not hand over.
  acquireLicense: (profileId: string, token: string) =>
    req<LicenseGrant>(`/profiles/${profileId}/license/acquire`,
      { method: "POST", token }),
  deriveAgent: (profileId: string, grantId: string, token: string) =>
    req<DerivedAgent>(`/profiles/${profileId}/license/${grantId}/derive`,
      { method: "POST", token }),

  // ---------------------------------------------------------------------
  // The other side of the counter.
  //
  // Everything above is what a buyer does. The console could buy a licence
  // and derive an agent from it, and could not post an offer, see who had
  // bought one, revoke one, read a penny of what any of it earned, or ask
  // to be paid. Nine routes, all of them owner-side, all of them reachable
  // from the iOS, Android and Windows shells — which is how the route audit
  // came back clean: it asked whether *some* client had a door, and a phone
  // counts. The console is the surface with the screens; a capability only
  // the phone can reach is not a capability a desktop owner has.
  //
  // Read `mixed` before drawing a total. See EarningsStatement.
  // ---------------------------------------------------------------------

  licenseOffer: (profileId: string) =>
    req<LicenseOfferView>(`/profiles/${profileId}/license`),
  setLicenseOffer: (profileId: string,
                    body: { kind: string; price: number; currency?: string;
                            terms?: string; allow_derivatives?: boolean },
                    token: string) =>
    req<LicenseOfferView>(`/profiles/${profileId}/license`,
      { method: "PUT", body, token }),
  withdrawLicenseOffer: (profileId: string, token: string) =>
    req<void>(`/profiles/${profileId}/license`,
      { method: "DELETE", token }),
  licenseHolders: (profileId: string, token: string) =>
    req<LicenseHolder[]>(`/profiles/${profileId}/licenses`, { token }),
  // The grant id, not the profile's. Revoking stops a buyer deriving from
  // it; it does not unmake an agent already derived, and it does not undo
  // the fee — the statement keeps the entry, which is what a revoked sale
  // looks like in an honest ledger.
  revokeLicense: (grantId: string, token: string) =>
    req<{ grant_id: string; revoked: boolean }>(`/licenses/${grantId}`,
      { method: "DELETE", token }),

  earnings: (profileId: string, token: string) =>
    req<EarningsStatement>(`/profiles/${profileId}/earnings`, { token }),
  // One currency per sweep, because a transfer is a movement of money and
  // there is no money that is partly yen. Omitting it means the settlement
  // currency — the figure the statement puts at the top.
  requestPayout: (profileId: string, token: string, currency?: string) =>
    req<PayoutReceipt>(
      `/profiles/${profileId}/earnings/payout${
        currency ? `?currency=${encodeURIComponent(currency)}` : ""}`,
      { method: "POST", token }),

  // A listing still needs no token to create — that has always been the
  // design, and the seller is established when a price is attached. What it
  // now does is *record* an authenticated creator as the listing's claimant,
  // which is what makes it theirs to move or take down. Removal used to ask
  // for nothing at all.
  createListing: (body: { kind: string; title: string; blurb?: string;
                          tags?: string[]; area?: string;
                          provider_name: string; business?: boolean;
                          profile_id?: string },
                  token: string) =>
    req<{ id: string; kind: string; title: string;
          claimed_by: string | null }>(`/marketplace/listings`,
      { method: "POST", body, token }),
  removeListing: (listingId: string, token: string) =>
    req<void>(`/marketplace/listings/${listingId}`,
      { method: "DELETE", token }),

  // ---------------------------------------------------------------------
  // Taking something back, and the three different answers to "there was
  // nothing there".
  //
  //   comment    404 "no such comment"     — and 403 if it is not yours
  //   listing    404 "profile is not listed"
  //   friend     **200**, `removed: false`, `reason: "not a friend"`
  //
  // The third is the one that bites. A caller reading only the status code
  // reports "Removed." for a row that was never there, so `removeFriend`
  // hands back the flag and the screen reads it. The founder's two profiles
  // are pinned and answer 409 instead — the list marks them, so the control
  // is not offered rather than offered and refused.
  // ---------------------------------------------------------------------

  removeFriend: (profileId: string, friendId: string, token: string) =>
    req<FriendRemoval>(`/profiles/${profileId}/friends/${friendId}`,
      { method: "DELETE", token }),
  deleteComment: (commentId: string, token: string) =>
    req<{ id: string; deleted: boolean }>(`/comments/${commentId}`,
      { method: "DELETE", token }),
  listOnMarketplace: (profileId: string,
                      body: { tags: string[]; blurb?: string },
                      token: string) =>
    req<{ profile_id: string; listed: boolean; tags: string[] }>(
      `/profiles/${profileId}/marketplace`, { method: "POST", body, token }),
  unlistFromMarketplace: (profileId: string, token: string) =>
    req<void>(`/profiles/${profileId}/marketplace`,
      { method: "DELETE", token }),

  // ---------------------------------------------------------------------
  // One named thing, and who may ask about it.
  //
  // Six reads, six different answers, each for a reason worth stating:
  //
  //   the light legend   anybody, and it takes no id at all
  //   a campaign         **anybody** — deliberately the most public read in
  //                      the product, because it carries `proceeds_to` and
  //                      the person about to give money is the one entitled
  //                      to see where it goes
  //   an organization    signed in
  //   an excursion       the profile's owner only — it holds the brief that
  //                      was sanitised before it left, and the count of
  //                      what was taken out
  //   somebody's grants  themselves only
  //   a place's grants   filtered to your own, because there is no
  //                      room-membership check to hang "what the room can
  //                      see" on, and without one it listed who is lending
  //                      what to whom to anybody who guessed the id
  // ---------------------------------------------------------------------

  agentLights: () => req<LightLegend>("/agent/lights"),
  campaign: (campaignId: string) =>
    req<CampaignOut>(`/campaigns/${campaignId}`),
  organization: (orgId: string, token: string) =>
    req<OrgOut>(`/organizations/${orgId}`, { token }),
  excursion: (cid: string, token: string) =>
    req<Excursion>(`/excursions/${cid}`, { token }),
  grantsForPerson: (personId: string, token: string) =>
    req<PersonGrants>(`/people/${personId}/skill-grants`, { token }),
  grantsInPlace: (surface: string, surfaceId: string, token: string) =>
    req<PlaceGrants>(`/surfaces/${surface}/${surfaceId}/skill-grants`,
      { token }),

  // ---------------------------------------------------------------------
  // A beginning, an ending, what it is taught, and a press from the wrist.
  //
  // The one worth reading twice is succession. **The owner token cannot be
  // the gate**, because the signal it responds to is that the owner has died
  // or cannot act — so it is held by a reviewer, outside profile ownership,
  // against an out-of-band `verification_ref`. With a named successor,
  // control passes and a fresh owner token is minted; with none, the profile
  // sunsets to memorial: frozen rather than orphaned.
  //
  // Publishing a pack now needs an owner token too, and the account sales
  // accrue to is read from it rather than from the body. It used to take
  // neither — anybody could publish under any publisher name and name any
  // account as the one the money went to.
  // ---------------------------------------------------------------------

  genesis: (body: {
    owner_id: string;
    verification: { birthdate: string; guardian_consent?: boolean };
    answers: { social_style: string; humor: string; what_matters: string;
               comfort: string };
    display_name?: string;
    purpose?: string;
    plan?: string;
  }) => req<Profile>("/profiles/genesis", { method: "POST", body }),

  // A reviewer's token, never the owner's.
  succeed: (profileId: string, verificationRef: string, token: string) =>
    req<Succession>(`/profiles/${profileId}/succeed`,
      { method: "POST", body: { verification_ref: verificationRef }, token }),

  publishPack: (body: {
    industry: string; title: string; blurb?: string; price?: number;
    currency?: string; publisher?: string; rated?: boolean;
    audience?: "profile" | "robot";
    items: { title: string; content: string; task?: string }[];
  }, token: string) =>
    req<PackSummary>("/packs", { method: "POST", body, token }),
  seedPacks: () => req<PackSeed>("/packs/seed", { method: "POST" }),

  // One press from the wrist, down the same paths the full apps use — same
  // auth, same allowlists, same moderation. A shortcut that skipped any of
  // those would be a second, weaker way in.
  watchAct: (profileId: string,
             body: { target: "workflow" | "robot" | "approval"; id: string;
                     action: string; input?: string },
             token: string) =>
    req<Record<string, unknown>>(`/profiles/${profileId}/watch/act`,
      { method: "POST", body, token }),
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
  return window.open(ceremonyOrigin() + `/signatures/ceremony?${q}`,
                     "qrme-ceremony", "width=460,height=620");
}

/** The base, with a loopback IP swapped for `localhost`.
 *
 *  A relying party id must be a **domain**, and `127.0.0.1` is not one — so
 *  a ceremony served from the desktop app's default base was refused by the
 *  browser before any authenticator was reached, with a message that reads
 *  like the credential failed rather than the address. `localhost` is a
 *  domain, reaches the same backend, and is a secure context without a
 *  certificate. Only the ceremony window needs this; every other call is
 *  plain HTTP and does not care. */
export function ceremonyOrigin(base: string = getBase()): string {
  return base.replace(/^(https?:\/\/)(127\.0\.0\.1|\[::1\])(?=[:/]|$)/,
                      "$1localhost");
}

/** Raw bytes, not JSON and not multipart — the route reads the request body
 *  and works the kind out from the bytes. `filename` is a display hint that
 *  never chooses the kind, so it rides as a query parameter. Written by hand
 *  rather than through `req()` because `req()` serialises JSON. */
export async function uploadMedia(profileId: string, file: File,
                                  token: string,
                                  alt = ""): Promise<UploadedMedia> {
  const parts = [];
  if (file.name) parts.push(`filename=${encodeURIComponent(file.name)}`);
  if (alt) parts.push(`alt=${encodeURIComponent(alt)}`);
  const q = parts.length ? `?${parts.join("&")}` : "";
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
    const body = data as { detail?: unknown; message?: unknown } | null;
    throw new RequestError(res.status, (body && body.detail) ?? text,
                           body?.message);
  }
  return data as UploadedMedia;
}
