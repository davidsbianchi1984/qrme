"""SQLite persistence layer.

A single-file database keeps v1 dependency-free; every table maps to a PRD
concept (profiles, interactors, relationships, messages, engagement).
"""

from __future__ import annotations

import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone

_SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id                TEXT PRIMARY KEY,
    owner_id          TEXT NOT NULL,
    kind              TEXT NOT NULL,          -- self | other_person | fictional
    display_name      TEXT NOT NULL,
    persona           TEXT NOT NULL,          -- core identity description
    demographics      TEXT NOT NULL DEFAULT '{}',
    sources           TEXT NOT NULL DEFAULT '[]',  -- imported content sources
    anonymous         INTEGER NOT NULL DEFAULT 0,
    adult_mode        INTEGER NOT NULL DEFAULT 0,
    interaction_scope TEXT NOT NULL DEFAULT 'reactive',  -- reactive | proactive
    moderation_mode   TEXT NOT NULL DEFAULT 'auto',      -- auto | manual
    aging_enabled     INTEGER NOT NULL DEFAULT 0,
    base_age          INTEGER,
    appearance        TEXT NOT NULL DEFAULT '',  -- how the profile looks/presents
                                              -- (steering hub); rides on the prompt
    consent_basis     TEXT,                   -- required when kind=other_person
    consent_attestor  TEXT,
    successor_owner   TEXT,                   -- legacy succession
    licensed_from     TEXT,                   -- source profile a licensed
                                              -- specialist agent was derived from
    purpose           TEXT,                   -- legacy_memorial | family | creator_persona
                                              -- | social_fan | companion_coach | enterprise_agent
    maturity          TEXT NOT NULL DEFAULT 'balanced',  -- strict | balanced | open
    cloud_contribution INTEGER NOT NULL DEFAULT 0,  -- opt-in: share rated,
                                                    -- anonymized exchanges to
                                                    -- improve the cloud model
    status            TEXT NOT NULL DEFAULT 'active',  -- active | restricted | departed | terminated
    proactive_min_interval_hours INTEGER NOT NULL DEFAULT 24,  -- anti-spam rate cap
    terms_version     TEXT,                   -- ToS version accepted at creation
    terms_accepted_at TEXT,
    watermark_design  TEXT,                   -- JSON {mark, label}: owner-designed
                                              -- display watermark; the AI
                                              -- designation itself is invariant
    avatar            TEXT,                   -- rendered portrait (asset ref or
                                              -- URL); served only through
                                              -- avatars.render(), which attaches
                                              -- the AI badge
    created_at        TEXT NOT NULL
);

-- Anti-spam state for unprompted (proactive) outreach, per (profile,
-- interactor): the last outreach time enforces the rate cap, and awaiting_reply
-- suppresses further outreach until the person has replied at least once.
CREATE TABLE IF NOT EXISTS proactive_state (
    profile_id       TEXT NOT NULL REFERENCES profiles(id),
    interactor_id    TEXT NOT NULL REFERENCES interactors(id),
    last_outreach_at TEXT,
    awaiting_reply   INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (profile_id, interactor_id)
);

-- User-to-user connections: interactors matched for anonymous chat, in a
-- friendly tier or an 18+-verified rated tier.
CREATE TABLE IF NOT EXISTS connection_queue (
    interactor_id TEXT PRIMARY KEY REFERENCES interactors(id),
    tier          TEXT NOT NULL,   -- friendly | rated
    alias         TEXT,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS connections (
    id           TEXT PRIMARY KEY,
    interactor_a TEXT NOT NULL REFERENCES interactors(id),
    interactor_b TEXT NOT NULL REFERENCES interactors(id),
    tier         TEXT NOT NULL,
    alias_a      TEXT,
    alias_b      TEXT,
    status       TEXT NOT NULL DEFAULT 'active',  -- active | ended
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS connection_messages (
    id            TEXT PRIMARY KEY,
    connection_id TEXT NOT NULL REFERENCES connections(id),
    sender_id     TEXT NOT NULL REFERENCES interactors(id),
    content       TEXT NOT NULL,
    status        TEXT NOT NULL,   -- approved | blocked
    flag_reason   TEXT,
    created_at    TEXT NOT NULL
);

-- Rooms: multiparty conversations across channels (chat/voice/video/AR/VR)
-- whose participants may be any mix of real users and synthetic profiles.
CREATE TABLE IF NOT EXISTS rooms (
    id         TEXT PRIMARY KEY,
    topic      TEXT,
    channel    TEXT NOT NULL DEFAULT 'chat',  -- chat | voice | video | ar | vr
    status     TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS room_participants (
    room_id TEXT NOT NULL REFERENCES rooms(id),
    kind    TEXT NOT NULL,   -- user | profile
    ref_id  TEXT NOT NULL,
    PRIMARY KEY (room_id, ref_id)
);

CREATE TABLE IF NOT EXISTS room_messages (
    id          TEXT PRIMARY KEY,
    room_id     TEXT NOT NULL REFERENCES rooms(id),
    sender_kind TEXT NOT NULL,   -- user | profile
    sender_id   TEXT NOT NULL,
    content     TEXT NOT NULL,
    status      TEXT NOT NULL,   -- approved | blocked
    flag_reason TEXT,
    watermark_id TEXT,           -- synthetic-media credential for profile turns
    created_at  TEXT NOT NULL
);

-- General marketplace listings: profiles, content, business expertise, and
-- services — offered by users or businesses.
CREATE TABLE IF NOT EXISTS listings (
    id            TEXT PRIMARY KEY,
    kind          TEXT NOT NULL,   -- profile | content | expertise | service
    title         TEXT NOT NULL,
    blurb         TEXT,
    tags          TEXT NOT NULL DEFAULT '[]',
    area          TEXT,            -- e.g. healthcare | finance | relationships
    provider_name TEXT NOT NULL,
    business      INTEGER NOT NULL DEFAULT 0,
    profile_id    TEXT REFERENCES profiles(id),  -- when kind = profile
    created_at    TEXT NOT NULL
);

-- Local provider directory: real businesses and practitioners users can be
-- handed to when AI guidance reaches its limits.
CREATE TABLE IF NOT EXISTS providers (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    area       TEXT NOT NULL,      -- healthcare | medical | mental_health |
                                   -- finance | relationships | career | …
    location   TEXT,
    contact    TEXT,
    business   INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

-- Consented session handoffs: an AI specialist's session summary packaged
-- for a local provider, sealed (PDI when configured) behind a revocable token.
CREATE TABLE IF NOT EXISTS handoffs (
    id            TEXT PRIMARY KEY,
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    profile_id    TEXT REFERENCES profiles(id),
    provider_id   TEXT NOT NULL REFERENCES providers(id),
    package       TEXT,            -- JSON summary; NULL when sealed in PDI
    pdi_key       TEXT,
    token         TEXT NOT NULL,   -- provider's revocable access token
    revoked       INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL
);

-- Wearable microphones lent to a room's profiles (see qrme/roommic.py). In a
-- voice or video room the participant's own microphone is carrying their voice
-- to the other people; a watch on the wrist has one nothing else is using.
--
-- Per participant, never per room: somebody can lend their own microphone, and
-- cannot consent on behalf of the people they can hear. `disclosure()` is
-- readable by everyone in the room rather than by the lender alone — in a room
-- the others *can* be told, and telling them is the price of the feature.
--
-- Rows are closed, not deleted, and every grant is closed when the room closes,
-- so a permission cannot outlive the conversation that justified it.
CREATE TABLE IF NOT EXISTS room_mics (
    id            TEXT PRIMARY KEY,
    room_id       TEXT NOT NULL REFERENCES rooms(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    device        TEXT NOT NULL,   -- the device, e.g. smart_watch, earbuds
    -- watch | earbuds | lapel | clip_on | … see qrme/roommic.py:MIC_TYPES.
    -- Only microphones pointed at a person qualify: a room-facing one would
    -- pick up the other participants, whose voices are not the lender's to give.
    mic_type      TEXT NOT NULL DEFAULT 'watch',
    -- What the lender asked for, and what the grant actually runs at. In a
    -- room these differ whenever the request was anything but near-field: a
    -- room has other people in it by definition, so a channel wide enough to
    -- hear them is a channel lending their voices. Both are stored because the
    -- request is the lender's setting and `gain` is what the room was told —
    -- reporting the request would overstate what the profiles could hear.
    requested_gain TEXT NOT NULL DEFAULT 'near_field',
    gain          TEXT NOT NULL DEFAULT 'near_field',
    started_at    TEXT NOT NULL,
    ended_at      TEXT
);

-- Medical referrals: a handoff whose release is authorised by a verified
-- WebAuthn assertion instead of a `consent: true` boolean (see
-- qrme/referral.py). A separate table rather than columns on `handoffs`
-- because the two are different promises — a handoff token stays live for an
-- ongoing provider relationship, a referral link opens once.
--
-- `document_sha256` records the hash at signing time and is **not** what the
-- release checks against — it was written in the same breath as `package` and
-- would agree with itself however the row was edited afterwards. `release()`
-- re-hashes `package` as it stands and compares *that* to the signature. The
-- column is kept as a record of what was signed, not as the guarantee.
-- What the clinician wrote back, so the synthetic profile is caught up without
-- the patient retelling everything (see qrme/referral.py).
--
-- Sealed in the PDI vault exactly like source material — `content` is NULL when
-- `pdi_key` is set — but deliberately **not** a `source_items` row. Source
-- material is life material the profile recalls *as its own*, and it is what
-- `workflows._scoped_items` feeds to a `research` phase. A clinician's note is
-- neither: it is somebody else's words, and it reaches the prompt through its
-- own attributed block that says so. Filing it as a source would let the
-- profile recite a clinical opinion as its own knowledge, which is the one
-- thing this must never do.
--
-- Scoped to (profile, interactor): it is that person's medical information and
-- belongs in no other conversation.
CREATE TABLE IF NOT EXISTS clinical_notes (
    id            TEXT PRIMARY KEY,
    referral_id   TEXT NOT NULL REFERENCES referrals(id),
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    provider_id   TEXT NOT NULL REFERENCES providers(id),
    provider_name TEXT NOT NULL,   -- denormalised: the attribution must survive
                                   -- a provider row being edited or removed
    content       TEXT,            -- NULL when sealed in the PDI vault
    pdi_key       TEXT,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS referrals (
    id              TEXT PRIMARY KEY,
    interactor_id   TEXT NOT NULL REFERENCES interactors(id),
    profile_id      TEXT NOT NULL REFERENCES profiles(id),
    provider_id     TEXT NOT NULL REFERENCES providers(id),
    package         TEXT NOT NULL,   -- JSON, exactly what was signed
    document_sha256 TEXT NOT NULL,   -- of `package`, checked again at release
    envelope_id     TEXT NOT NULL,   -- the signature envelope raised for this
    signature_id    TEXT,            -- set once released
    token           TEXT,            -- one-time; NULL until released
    redeemed_at     TEXT,            -- set on the single opening
    -- Issued *at* that opening, so the clinician can write back once without
    -- the summary link being reusable. Open once, reply once.
    reply_token     TEXT,
    replied_at      TEXT,
    created_at      TEXT NOT NULL
);

-- Creative works a profile composes (music description, poem, note) that
-- capture a shared moment — kept as artifacts.
CREATE TABLE IF NOT EXISTS creative_works (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    kind       TEXT NOT NULL,   -- music | poem | note | lyric
    moment     TEXT,            -- the moment it captures
    content    TEXT NOT NULL,
    watermark_id TEXT,          -- synthetic-media credential (watermark.py)
    created_at TEXT NOT NULL
);

-- Real-time perception events: what a profile "sees" through a camera and
-- the guidance it gives back (hands-free navigation, shared experiences).
CREATE TABLE IF NOT EXISTS perceptions (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    scene      TEXT NOT NULL,   -- JSON: objects, people, gestures, place
    goal       TEXT,            -- e.g. "guide me to the exit"
    guidance   TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- @handles: one claimable, unique handle per profile for direct summoning.
CREATE TABLE IF NOT EXISTS handles (
    handle     TEXT PRIMARY KEY,   -- lowercase, no leading @
    profile_id TEXT NOT NULL UNIQUE REFERENCES profiles(id),
    created_at TEXT NOT NULL
);

-- Beacons: a profile left behind somewhere in the world. Each beacon is a
-- placed QR anchor (a bench, a storefront, a memorial) whose code summons
-- the profile; scans are counted and beacons can be picked back up.
CREATE TABLE IF NOT EXISTS beacons (
    id         TEXT PRIMARY KEY,   -- bcn_… — also the QR token
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    label      TEXT NOT NULL,      -- e.g. "Rosa's garden bench"
    location   TEXT,               -- free-text place
    scans      INTEGER NOT NULL DEFAULT 0,
    active     INTEGER NOT NULL DEFAULT 1,
    room_id    TEXT REFERENCES rooms(id),  -- set = everyone who scans this
                                           -- code joins one shared room
                                           -- instead of a private 1:1 chat
    created_at TEXT NOT NULL
);

-- Physical embodiments a profile can inhabit: speaker, earpiece, hologram,
-- robot. Chat may arrive from (and route back to) an embodiment.
CREATE TABLE IF NOT EXISTS embodiments (
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    name       TEXT NOT NULL,
    kind       TEXT NOT NULL,   -- speaker | earpiece | hologram | robot | humanoid | other
    has_llm    INTEGER NOT NULL DEFAULT 0,  -- embodiment runs its own model
    created_at TEXT NOT NULL,
    PRIMARY KEY (profile_id, name)
);

-- Source material the profile is built from ("AI builds & trains the
-- profile"): photos, conversations, writings, voice notes, life events,
-- knowledge-base entries. Content may live in the PDI vault (pdi_key set).
CREATE TABLE IF NOT EXISTS source_items (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    kind       TEXT NOT NULL,   -- photo | conversation | social_post | writing
                                -- | voice_note | life_event | knowledge | linked_account
    title      TEXT,
    content    TEXT,            -- NULL when sealed in the PDI vault
    pdi_key    TEXT,
    pack_id    TEXT,            -- set when the item came from a knowledge pack
    created_at TEXT NOT NULL
);

-- Cross-platform presence: the surfaces this profile is live on.
CREATE TABLE IF NOT EXISTS surfaces (
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    surface    TEXT NOT NULL,   -- chat | feed | web | ar_vr | wearable | social:<name>
    created_at TEXT NOT NULL,
    PRIMARY KEY (profile_id, surface)
);

-- Safe knowledge excursions. When a profile's model needs to study an
-- unfamiliar topic, it gathers general knowledge from a SANITIZED brief (the
-- owner's private terms redacted). ``brief`` is exactly what could leave;
-- ``left_host`` records whether anything actually did (offline: never). Findings
-- come back as general knowledge and can be folded into a knowledge source.
CREATE TABLE IF NOT EXISTS excursions (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    topic        TEXT NOT NULL,       -- stays local (owner's data)
    brief        TEXT NOT NULL,       -- sanitized outbound query
    redactions   INTEGER NOT NULL DEFAULT 0,
    left_host    INTEGER NOT NULL DEFAULT 0,
    findings     TEXT,                -- general knowledge brought back
    learned_src  TEXT,                -- source_item id once folded in
    created_at   TEXT NOT NULL
);

-- Connected-app connectors. Each links a profile to an AI-integrated app from
-- the catalog (Apple Photos, Google Calendar, Microsoft 365, Canva, …). Its
-- agents then use it: collect context in, act on the app, or produce media.
CREATE TABLE IF NOT EXISTS app_connectors (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    provider     TEXT NOT NULL,   -- apple | google | microsoft | canva
    app          TEXT NOT NULL,   -- photos | calendar | mail | ...
    label        TEXT NOT NULL,
    capabilities TEXT NOT NULL DEFAULT '[]',  -- granted subset of the app's catalog capabilities
    directions   TEXT NOT NULL DEFAULT '[]',  -- collect | act | produce (from the catalog)
    status       TEXT NOT NULL DEFAULT 'active',  -- active | revoked
    collected    INTEGER NOT NULL DEFAULT 0,   -- context items pulled in
    actions      INTEGER NOT NULL DEFAULT 0,   -- capabilities invoked
    created_at   TEXT NOT NULL
);

-- Social-platform connections. Each links a profile to an external platform in
-- one of two directions:
--   collect  — pull the account's content in as source material that BUILDS the
--              profile (each item lands in source_items as a social_post);
--   publish  — post / run the profile ON the platform, registering a
--              social:<platform> surface and a QR beacon that reaches it.
CREATE TABLE IF NOT EXISTS social_connections (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    platform    TEXT NOT NULL,   -- instagram | x | tiktok | facebook | linkedin | youtube | reddit | threads
    direction   TEXT NOT NULL,   -- collect | publish
    handle      TEXT,            -- the account handle on that platform
    scope       TEXT NOT NULL DEFAULT '[]',   -- JSON list: posts, photos, bio, ...
    status      TEXT NOT NULL DEFAULT 'active',  -- active | revoked
    collected   INTEGER NOT NULL DEFAULT 0,   -- items ingested (collect)
    published   INTEGER NOT NULL DEFAULT 0,   -- items posted (publish)
    created_at  TEXT NOT NULL
);

-- Latent persona embeddings (claim 21): a persistent, per-(profile,
-- interactor) state vector updated after every interaction to carry
-- cross-session state into inference conditioning.
CREATE TABLE IF NOT EXISTS persona_embeddings (
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    vector        TEXT NOT NULL,   -- JSON list of named latent dimensions
    version       INTEGER NOT NULL DEFAULT 1,
    updated_at    TEXT NOT NULL,
    PRIMARY KEY (profile_id, interactor_id)
);

-- Domain-specialized synthetic agents (claim 24): the profile can hand a
-- conversation to a specialist profile when monitoring signals call for it.
CREATE TABLE IF NOT EXISTS specialists (
    profile_id            TEXT NOT NULL REFERENCES profiles(id),
    domain                TEXT NOT NULL,   -- mental_health | medical | finance | …
    specialist_profile_id TEXT NOT NULL REFERENCES profiles(id),
    created_at            TEXT NOT NULL,
    PRIMARY KEY (profile_id, domain)
);

-- Active in-conversation specialist handoff (claim 24, sustained): once
-- real-time monitoring routes a conversation to a domain specialist, the
-- handoff persists across turns — even turns that carry no biometrics — until
-- monitoring shows recovery, so the switch is a real hand-to-hand within one
-- conversation rather than a single-message detour.
CREATE TABLE IF NOT EXISTS active_handoffs (
    profile_id            TEXT NOT NULL REFERENCES profiles(id),
    interactor_id         TEXT NOT NULL REFERENCES interactors(id),
    domain                TEXT NOT NULL,
    specialist_profile_id TEXT NOT NULL REFERENCES profiles(id),
    since                 TEXT NOT NULL,
    PRIMARY KEY (profile_id, interactor_id)
);

-- Real-time biometric context received during interactions (claim 23).
CREATE TABLE IF NOT EXISTS biometric_context (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    data          TEXT NOT NULL,   -- JSON signal payload
    created_at    TEXT NOT NULL
);

-- Revocable access grants (claim 25): scoped tokens a profile uses to read
-- vaulted data during a task, without retaining the raw data.
CREATE TABLE IF NOT EXISTS grants (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    scope      TEXT NOT NULL,      -- JSON list of source-item ids ("*" = all)
    token      TEXT NOT NULL,
    revoked    INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Autonomous multi-step tasks (claim 25). Step log keeps summaries and
-- references only — never the raw vaulted data.
CREATE TABLE IF NOT EXISTS tasks (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    kind        TEXT NOT NULL,
    grant_id    TEXT,
    status      TEXT NOT NULL,     -- completed | failed
    steps       TEXT NOT NULL,     -- JSON step log (summaries only)
    output      TEXT,
    watermark_id TEXT,             -- synthetic-media credential (watermark.py)
    created_at  TEXT NOT NULL
);

-- Training-data licensing: an owner offers their profile's expertise for
-- license (consult / fine-tune / clone), optionally allowing buyers to derive
-- their own specialist agent from it. One active offer per profile.
CREATE TABLE IF NOT EXISTS license_offers (
    profile_id        TEXT PRIMARY KEY REFERENCES profiles(id),
    kind              TEXT NOT NULL,          -- consult | finetune | clone
    price             REAL NOT NULL DEFAULT 0,
    currency          TEXT NOT NULL DEFAULT 'USD',
    terms             TEXT,
    allow_derivatives INTEGER NOT NULL DEFAULT 0,  -- buyer may derive an agent
    created_at        TEXT NOT NULL
);

-- A license a buyer holds against a source profile. The token authorizes
-- licensed use; deriving a specialist agent records the child profile here.
CREATE TABLE IF NOT EXISTS license_grants (
    id                 TEXT PRIMARY KEY,
    profile_id         TEXT NOT NULL REFERENCES profiles(id),   -- licensed source
    buyer_id           TEXT NOT NULL REFERENCES interactors(id),
    kind               TEXT NOT NULL,
    token              TEXT NOT NULL,
    derived_profile_id TEXT,                  -- set when an agent is derived
    revoked            INTEGER NOT NULL DEFAULT 0,
    created_at         TEXT NOT NULL
);

-- Local log of every cloud contribution: exactly what left, when, under which
-- opaque ref. The gateway never sees profile ids — the ref is random, and only
-- this table maps it back — so contributions stay anonymous at the gateway
-- while remaining individually deletable on revocation.
CREATE TABLE IF NOT EXISTS contribution_log (
    ref            TEXT PRIMARY KEY,   -- opaque id sent with the payload
    profile_id     TEXT NOT NULL REFERENCES profiles(id),
    payload        TEXT NOT NULL,      -- the exact JSON that was sent
    revoked        INTEGER NOT NULL DEFAULT 0,
    contributed_at TEXT NOT NULL
);

-- AI Profile Marketplace: owner-listed profiles discoverable by others.
-- Product feedback: "help us improve" — anyone using the app can send an
-- idea, improvement, bug, or praise. The submitter's role/subject is kept
-- when they're authenticated (so they can see their own), anonymous
-- otherwise. Never surfaced to other users; only aggregate tallies are.
CREATE TABLE IF NOT EXISTS feedback (
    id         TEXT PRIMARY KEY,
    submitter  TEXT NOT NULL DEFAULT 'anonymous',  -- role:subject or 'anonymous'
    category   TEXT NOT NULL,          -- idea | improvement | bug | praise | other
    message    TEXT NOT NULL,
    rating     INTEGER,                -- optional 1..5 satisfaction
    status     TEXT NOT NULL DEFAULT 'received',   -- received | reviewed | planned | shipped
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS marketplace (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    tags       TEXT NOT NULL DEFAULT '[]',
    blurb      TEXT,
    listed_at  TEXT NOT NULL
);

-- Rated (18+) placements: where an adult-mode profile is marketed. Each
-- placement mints a beacon whose scans resolve through the age wall.
CREATE TABLE IF NOT EXISTS rated_placements (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    venue      TEXT NOT NULL,
    beacon_id  TEXT NOT NULL REFERENCES beacons(id),
    label      TEXT,
    created_at TEXT NOT NULL
);

-- Every resolution of a rated profile on a discovery surface: walled or
-- verified, and through which beacon (NULL = a direct @handle/ref summon).
-- The raw material for placement analytics — counts and rates only ever
-- shown to the profile's owner.
CREATE TABLE IF NOT EXISTS rated_events (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    beacon_id  TEXT,
    kind       TEXT NOT NULL,          -- wall | verified_view
    at         TEXT NOT NULL,
    pdi_key    TEXT                    -- set when sealed in the PDI vault
);

-- Knowledge packs: downloadable clusters of curated expertise sold (or given
-- away) on the marketplace. Installing a pack copies its items into the
-- profile's source material, so the persona's knowledge base — and its
-- provenance trail — genuinely grows.
CREATE TABLE IF NOT EXISTS knowledge_packs (
    id         TEXT PRIMARY KEY,
    industry   TEXT NOT NULL,
    audience   TEXT NOT NULL DEFAULT 'profile',  -- profile | robot
    title      TEXT NOT NULL,
    blurb      TEXT,
    publisher  TEXT NOT NULL,
    price      REAL NOT NULL DEFAULT 0,   -- 0 = free download
    currency   TEXT NOT NULL DEFAULT 'USD',
    origin     TEXT NOT NULL DEFAULT 'local',  -- local | a registry key
    origin_url TEXT,                     -- the registry storefront, when federated
    rated      INTEGER NOT NULL DEFAULT 0,  -- 18+ commerce: age-gated to buy AND see
    publisher_owner_id TEXT,           -- who the sale accrues to in the ledger
    created_at TEXT NOT NULL
);

-- Gaming: a synthetic profile joins a game as an agent-operated companion
-- or teammate. Each session is owner-created for a platform + title + role;
-- the persona produces in-character comms (callouts, coordination, banter)
-- each turn, moderated like any public surface. Fair play is a system rule,
-- not a toggle: the companion plays within the game's rules and never claims
-- or uses cheats.
CREATE TABLE IF NOT EXISTS game_sessions (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    platform   TEXT NOT NULL,          -- a catalog gaming app key
    game       TEXT NOT NULL,          -- free-text title
    role       TEXT NOT NULL,          -- companion | teammate | practice_partner
    mode       TEXT NOT NULL DEFAULT 'online_multiplayer',
    status     TEXT NOT NULL DEFAULT 'active',  -- active | ended
    callouts   INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Steering: how the owner shapes a subject's presentation (a profile or a
-- robot) — throttle/behavior dials as JSON of dial -> 0..100; absent dials
-- read as the 50 default. Steering, not piloting: shapes style/pace/behavior
-- only — never identity, boundaries, age-gating, or the command allowlist.
CREATE TABLE IF NOT EXISTS steering_settings (
    subject_id TEXT PRIMARY KEY,       -- profile_id or robot_id
    dials      TEXT NOT NULL DEFAULT '{}',   -- JSON: dial name -> 0..100
    updated_at TEXT NOT NULL
);

-- The creator ledger: one row per money event, written at sale time so a
-- creator's statement is a record, not a reconstruction. Simulated money,
-- like every payment on the platform — but the accounting is real.
CREATE TABLE IF NOT EXISTS ledger (
    id          TEXT PRIMARY KEY,
    beneficiary TEXT NOT NULL,         -- the earning creator's owner_id
    kind        TEXT NOT NULL,         -- pack_sale | license_fee
    ref         TEXT NOT NULL,         -- pack_id / grant_id
    memo        TEXT,
    amount      REAL NOT NULL,
    currency    TEXT NOT NULL DEFAULT 'USD',
    status      TEXT NOT NULL DEFAULT 'accrued',  -- accrued | paid
    payout_id   TEXT,                  -- set when swept into a payout
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pack_items (
    id         TEXT PRIMARY KEY,
    pack_id    TEXT NOT NULL REFERENCES knowledge_packs(id),
    title      TEXT NOT NULL,
    content    TEXT NOT NULL,
    task       TEXT,                      -- robot packs: the command verb added
    requires   TEXT NOT NULL DEFAULT '[]', -- robot packs: capabilities needed
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pack_installs (
    pack_id      TEXT NOT NULL REFERENCES knowledge_packs(id),
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    robot_id     TEXT NOT NULL DEFAULT '',  -- set for robot-audience installs
    price_paid   REAL NOT NULL DEFAULT 0,
    installed_at TEXT NOT NULL,
    PRIMARY KEY (pack_id, profile_id, robot_id)
);

-- Task modules a robot pack installed onto a bound body. Each task becomes a
-- commandable verb for that robot, alongside its kind's built-in allowlist —
-- capability-checked at install, audited like every other command.
CREATE TABLE IF NOT EXISTS robot_skills (
    robot_id   TEXT NOT NULL REFERENCES robots(id),
    pack_id    TEXT NOT NULL REFERENCES knowledge_packs(id),
    task       TEXT NOT NULL,
    title      TEXT NOT NULL,
    procedure  TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (robot_id, task)
);

-- Autonomous multi-step workflows (claim 25, extended): a named plan of
-- phases (research → draft → review → send → confirm) executed one at a time.
-- Each phase's output is carried forward as working memory into the next, so
-- the profile builds on its own prior work and stays in character; the
-- workflow persists between calls, so a phase that waits on external
-- confirmation can resume in a later session. Vault reads run under the same
-- revocable grant as single-shot tasks.
CREATE TABLE IF NOT EXISTS workflows (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    goal        TEXT NOT NULL,
    plan        TEXT NOT NULL,                   -- JSON list of phase names
    cursor      INTEGER NOT NULL DEFAULT 0,      -- index of the next phase
    memory      TEXT NOT NULL DEFAULT '{}',      -- JSON: phase -> output so far
    status      TEXT NOT NULL DEFAULT 'running', -- running | awaiting_input
                                                 -- | completed | failed | cancelled
    awaiting    TEXT,                            -- what a paused phase needs
    grant_id    TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- Owner-authorized workflow delegation: who else may start a workflow on this
-- profile, and what they may ask for. The workflow routes are owner-only, and
-- correctly so — a workflow reads vaulted source material unattended, which is
-- not the same decision as allowing a chat turn. So delegation is off until an
-- owner writes a row here.
--
-- `grant_id` is not optional in practice: `set_policy` refuses a policy that
-- delegates `research` without one, because `workflows._scoped_items` reads
-- *every* source item when the grant is absent. The column is nullable only so
-- a policy that delegates, say, `draft` alone need not invent a grant.
CREATE TABLE IF NOT EXISTS delegation_policies (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    phases     TEXT NOT NULL,      -- JSON list: the phases a caller may ask for
    grant_id   TEXT,               -- scopes every delegated vault read
    enabled    INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Which workflows were started by somebody other than the owner, and by whom.
-- A separate table rather than a column on `workflows` so an owner's own
-- workflow has no row here at all — that absence is what keeps it unreachable
-- from the delegated routes.
CREATE TABLE IF NOT EXISTS delegated_workflows (
    workflow_id   TEXT PRIMARY KEY REFERENCES workflows(id),
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    created_at    TEXT NOT NULL
);

-- Offline fine-tuning runs (claim 26): local-only adaptation passes whose
-- artifacts are sealed (PDI vault when configured); nothing leaves the host.
CREATE TABLE IF NOT EXISTS finetune_runs (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    metrics     TEXT NOT NULL,     -- JSON: messages processed, engagement stats
    vault_key   TEXT,              -- adaptation artifact location when sealed
    created_at  TEXT NOT NULL
);

-- Posts composed in the profile's voice (social & fan engagement), each
-- through the same moderation pipeline as chat replies.
-- A wearable paired over Bluetooth: a watch, a band, a ring, earbuds.
--
-- Distinct from `embodiments`, which is where a *profile* lives — a speaker, a
-- hologram, a robot. This is hardware belonging to the **owner**, paired to
-- reach their own account: the wrist is a control surface, not a place a
-- persona is embodied. Running them together would mean pairing a watch could
-- put somebody's synthetic profile on it.
--
-- Only the pairing and what it is allowed to show. No sensor stream, no
-- capture, nothing about a microphone — a paired watch here is a screen and a
-- set of buttons.
CREATE TABLE IF NOT EXISTS wearables (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    name         TEXT NOT NULL,
    kind         TEXT NOT NULL,   -- watch | band | ring | earbuds | glasses
    transport    TEXT NOT NULL DEFAULT 'bluetooth',
    faces        TEXT NOT NULL DEFAULT '[]',  -- JSON: which faces are enabled
    paired_at    TEXT NOT NULL,
    last_seen_at TEXT,
    revoked_at   TEXT,
    UNIQUE (profile_id, name)
);

-- What a post is promoting, when it is promoting something. A separate table
-- because `posts` shipped before this and the schema has no migrations, so a
-- new column would reach a fresh database and miss every existing one.
CREATE TABLE IF NOT EXISTS post_attachments (
    post_id    TEXT PRIMARY KEY REFERENCES posts(id),
    listing_id TEXT NOT NULL REFERENCES listings(id),
    created_at TEXT NOT NULL
);

-- Two people agreeing, in writing, on work about to change hands.
--
-- `state` is the whole safety story: only `draft` is editable, and any edit
-- deletes the signature rows, so a signature can never be attached to a
-- manifest its signer did not read. See qrme/exchange.py.
CREATE TABLE IF NOT EXISTS exchanges (
    id         TEXT PRIMARY KEY,
    desk_id    TEXT,                -- the desk it came out of, when it did
    host_id    TEXT NOT NULL,
    guest_id   TEXT NOT NULL,
    work       TEXT NOT NULL,       -- one sentence: what is being done
    industry   TEXT NOT NULL,
    includes   TEXT,                -- JSON list: what is delivered at the end
    excludes   TEXT,                -- JSON list: what is not, said out loud
    fee        REAL NOT NULL DEFAULT 0,
    state      TEXT NOT NULL,       -- draft|proposed|signed|delivered|closed|withdrawn
    created_at TEXT NOT NULL
);

-- Every artifact named on a manifest, in both directions. `accepted_at` is the
-- second consent: a signed agreement makes an item available, and this is the
-- receiving side actually taking it.
CREATE TABLE IF NOT EXISTS exchange_items (
    id          TEXT PRIMARY KEY,
    exchange_id TEXT NOT NULL REFERENCES exchanges(id),
    direction   TEXT NOT NULL,      -- host_to_guest | guest_to_host
    name        TEXT NOT NULL,
    kind        TEXT NOT NULL,
    bytes       INTEGER NOT NULL DEFAULT 0,
    note        TEXT,
    accepted_at TEXT,
    created_at  TEXT NOT NULL
);

-- A signature against a *fingerprint*, never against an exchange id. That is
-- what lets `channel()` tell a current signature from a stale one without
-- anything having to remember to clear it.
CREATE TABLE IF NOT EXISTS exchange_signatures (
    exchange_id TEXT NOT NULL REFERENCES exchanges(id),
    party_id    TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    signed_at   TEXT NOT NULL,
    PRIMARY KEY (exchange_id, party_id)
);

-- Watching something together. The party holds a *position*, not a player:
-- each viewer's own video still loads only when they press play, which is the
-- promise post_videos above is built on. See qrme/watchparty.py.
CREATE TABLE IF NOT EXISTS watch_parties (
    id         TEXT PRIMARY KEY,
    post_id    TEXT NOT NULL REFERENCES posts(id),
    host_id    TEXT NOT NULL,
    title      TEXT,
    position_s INTEGER NOT NULL DEFAULT 0,
    playing    INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Who is in the room. `kind` separates a real account from a synthetic
-- profile, because nearly every rule differs between them — and because a room
-- where you cannot tell which of the names is a person is the room this
-- platform exists not to build.
CREATE TABLE IF NOT EXISTS watch_party_members (
    id        TEXT PRIMARY KEY,
    party_id  TEXT NOT NULL REFERENCES watch_parties(id),
    member_id TEXT NOT NULL,
    kind      TEXT NOT NULL,        -- person | profile
    role      TEXT NOT NULL,        -- host | guest
    joined_at TEXT NOT NULL,
    left_at   TEXT,
    UNIQUE (party_id, member_id)
);

-- The party chat, each line stamped with the position it was said at so a
-- comment about a moment stays attached to that moment. Moderated like every
-- other utterance; a blocked line is kept rather than dropped.
CREATE TABLE IF NOT EXISTS watch_party_lines (
    id          TEXT PRIMARY KEY,
    party_id    TEXT NOT NULL REFERENCES watch_parties(id),
    member_id   TEXT NOT NULL,
    kind        TEXT NOT NULL,
    body        TEXT NOT NULL,
    position_s  INTEGER NOT NULL DEFAULT 0,
    status      TEXT NOT NULL,
    flag_reason TEXT,
    created_at  TEXT NOT NULL
);

-- A video a post is pointing at, on somebody else's platform.
--
-- The link and the id, never the file and never a thumbnail: re-hosting
-- somebody's video is a copyright problem and a cached thumbnail is a copy of
-- an image nobody granted. `title` is what the poster typed, not what was
-- scraped from the other site — which is both the honest attribution and the
-- reason nothing here has to make a request to render.
--
-- Separate table for the same reason as post_attachments above: no migrations.
CREATE TABLE IF NOT EXISTS post_videos (
    post_id    TEXT PRIMARY KEY REFERENCES posts(id),
    platform   TEXT NOT NULL,
    video_id   TEXT NOT NULL,
    url        TEXT NOT NULL,
    title      TEXT,
    created_at TEXT NOT NULL
);

-- Edits to a message already sent. One row per revision, so the trail is the
-- history rather than only the latest text.
--
-- A separate table on purpose: this schema is CREATE TABLE IF NOT EXISTS with
-- no migrations, so adding columns to `messages` would reach a fresh database
-- and silently miss every existing one. Retraction needs no new column at all —
-- it writes `retracted` into the status the history query already filters on.
CREATE TABLE IF NOT EXISTS message_revisions (
    id          TEXT PRIMARY KEY,
    message_id  TEXT NOT NULL REFERENCES messages(id),
    was         TEXT NOT NULL,        -- the text this revision replaced
    became      TEXT,                 -- NULL when the edit was a retraction
    reason      TEXT,                 -- moderation flag, when one applied
    edited_at   TEXT NOT NULL
);

-- Posts a profile publishes. `surface` says where: a social platform via
-- social.py, or 'wall' for the community wall (qrme/wall.py).
--
-- The wall reuses this rather than adding a second posts table. It already had
-- a surface column, an author, content and a moderation verdict, which is the
-- whole of what a wall post is — and likes, comments and shares are not here
-- at all, because `post` is a target kind in the audience layer.
CREATE TABLE IF NOT EXISTS posts (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    surface      TEXT,            -- external platform name, or 'wall'
    topic        TEXT,
    content      TEXT NOT NULL,
    status       TEXT NOT NULL,  -- approved | pending | rejected
    flag_reason  TEXT,
    watermark_id TEXT,           -- synthetic-media credential (watermark.py)
    created_at   TEXT NOT NULL
);

-- Synthetic-media credentials: one row per stamped piece of generated
-- content — every AI render, textual or visual (chat turns, posts, room
-- turns, game/robot lines, creative works, task outputs, non-text
-- modalities). The server-side half of the watermark:
-- holders of content verify against it, and content that merely *claims* a
-- watermark fails the lookup.
CREATE TABLE IF NOT EXISTS media_watermarks (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    kind         TEXT NOT NULL,     -- post | voice | image | video | …
    content_hash TEXT NOT NULL,     -- sha256 of the content at issue time
    issued_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interactors (
    id           TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    birthdate    TEXT,
    quiet_start  INTEGER,             -- quiet-hours window (UTC hour, inclusive)
    quiet_end    INTEGER,             -- quiet-hours window (UTC hour, exclusive)
    created_at   TEXT NOT NULL
);

-- Objections: a real person (or their estate) contesting a profile that
-- represents them. Opening one moves the profile to 'restricted' (public
-- surfaces off, no new interactors) pending review; resolution either
-- terminates the profile or returns it to active. A subject_consent subject
-- can withdraw consent at any time, which forces termination.
CREATE TABLE IF NOT EXISTS objections (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    objector_ref  TEXT NOT NULL,   -- out-of-band proof-of-identity reference
    reason        TEXT,
    status        TEXT NOT NULL DEFAULT 'open',  -- open | upheld | dismissed | withdrawn | revoked
    reattested    INTEGER NOT NULL DEFAULT 0,    -- owner re-attested their basis
    prior_status  TEXT,            -- profile status before restriction (active | departed)
    created_at    TEXT NOT NULL,
    resolved_at   TEXT
);

-- Tamper-evident audit trail for the objection / revocation lifecycle. Each
-- row is also sealed into the PDI vault when configured (pdi_key holds the
-- vault key); PDI hash-chains every write, so the sealed copy is independently
-- verifiable and cannot be silently altered.
CREATE TABLE IF NOT EXISTS objection_events (
    id            TEXT PRIMARY KEY,
    objection_id  TEXT NOT NULL,
    profile_id    TEXT NOT NULL,
    event         TEXT NOT NULL,   -- opened|reattested|upheld|dismissed|withdrawn|revoked|terminated
    actor         TEXT NOT NULL,   -- objector|owner|reviewer|subject|estate|system
    detail        TEXT,            -- JSON
    pdi_key       TEXT,            -- vault key of the sealed copy, if PDI configured
    created_at    TEXT NOT NULL
);

-- Capability tokens. Owner control of a profile is proven by holding the
-- profile's owner token (minted once at creation); interactor identity is
-- proven by the interactor's own token. Only the SHA-256 hash is stored, so
-- a database leak never yields a usable credential.
CREATE TABLE IF NOT EXISTS api_tokens (
    token_hash TEXT PRIMARY KEY,
    role       TEXT NOT NULL,   -- owner | interactor
    subject_id TEXT NOT NULL,   -- profile_id for owner, interactor_id for interactor
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS relationships (
    id                TEXT PRIMARY KEY,
    profile_id        TEXT NOT NULL REFERENCES profiles(id),
    interactor_id     TEXT NOT NULL REFERENCES interactors(id),
    relationship_type TEXT NOT NULL DEFAULT 'stranger',
    nickname          TEXT,
    tone              TEXT,
    boundaries        TEXT NOT NULL DEFAULT '[]',  -- restricted topics
    created_at        TEXT NOT NULL,
    UNIQUE (profile_id, interactor_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    role          TEXT NOT NULL,   -- interactor | profile
    content       TEXT NOT NULL,
    status        TEXT NOT NULL,   -- approved | pending | rejected
    flag_reason   TEXT,
    watermark_id  TEXT,            -- synthetic-media credential for profile turns
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS engagement (
    profile_id    TEXT NOT NULL,
    interactor_id TEXT NOT NULL,
    score         REAL NOT NULL DEFAULT 0.5,   -- 0..1 engagement estimate
    interactions  INTEGER NOT NULL DEFAULT 0,
    sessions      INTEGER NOT NULL DEFAULT 0,
    feedback_pos  INTEGER NOT NULL DEFAULT 0,
    feedback_neg  INTEGER NOT NULL DEFAULT 0,
    last_seen     TEXT,
    PRIMARY KEY (profile_id, interactor_id)
);

-- Per-profile LLM provider preference. 'auto' (or a missing row) defers to the
-- platform default; any other value is a qrme.llm registry name the owner
-- picked (anthropic | openai | grok | perplexity | gemini | stub).
CREATE TABLE IF NOT EXISTS model_prefs (
    profile_id  TEXT PRIMARY KEY REFERENCES profiles(id),
    provider    TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS language_prefs (
    profile_id  TEXT PRIMARY KEY REFERENCES profiles(id),
    language    TEXT NOT NULL,   -- qrme.i18n.SUPPORTED code, e.g. "es"
    mode        TEXT NOT NULL DEFAULT 'pre',  -- pre | on_demand
    updated_at  TEXT NOT NULL
);

-- Robot bodies bound to a profile (see qrme/robotics.py for the catalog).
-- Each binding also creates an embodiments row, so identity consistency and
-- chat routing treat the robot like any other embodiment.
CREATE TABLE IF NOT EXISTS robots (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    model        TEXT NOT NULL,   -- robotics.BY_KEY key, e.g. neo, saros_20
    name         TEXT NOT NULL,   -- the household name, e.g. "kitchen NEO"
    llm_provider TEXT,            -- qrme.llm registry name loaded onboard
    status       TEXT NOT NULL DEFAULT 'docked',  -- docked | active | offline
    created_at   TEXT NOT NULL
);

-- Every command sent to a robot, for the audit trail (commands are validated
-- against the per-kind allowlist before they are ever queued).
CREATE TABLE IF NOT EXISTS robot_commands (
    id         TEXT PRIMARY KEY,
    robot_id   TEXT NOT NULL REFERENCES robots(id),
    command    TEXT NOT NULL,
    arg        TEXT,
    result     TEXT,             -- JSON summary of what was queued/said
    created_at TEXT NOT NULL
);

-- A live desk: a real person offering services, not a synthetic profile.
-- Kept in its own table rather than as a profile flag, because everything
-- that touches `profiles` attaches the AI watermark, and a human must never
-- pick it up by inheriting machinery built for synthetic renders.
CREATE TABLE IF NOT EXISTS desks (
    id                TEXT PRIMARY KEY,
    owner_id          TEXT NOT NULL,
    display_name      TEXT NOT NULL,
    trade             TEXT NOT NULL,
    location          TEXT,
    blurb             TEXT,
    presence          TEXT NOT NULL DEFAULT 'away',  -- attended | away | closed
    rated             INTEGER NOT NULL DEFAULT 0,     -- 18+ stream: the existing
                                       -- verified-adult gate applies to the
                                       -- card, the view, the bell and joining
    view_style        TEXT NOT NULL DEFAULT 'desk',   -- desk | stage: which
                                       -- sample frame stands in until a real
                                       -- camera is configured
    room_id           TEXT,            -- the live stream people join
    portrait          TEXT,            -- only ever set by the desk's owner
    camera_url        TEXT,            -- the desk's own camera, when it has one;
                                       -- NULL means the sample frame is served
                                       -- and the card says live:false
    attestor          TEXT NOT NULL,   -- who vouches a real person staffs this
    attestation_basis TEXT NOT NULL,
    attested_at       TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    last_seen         TEXT NOT NULL
);

-- Ring the bell at an unattended desk. caller_id is NULL for a stranger who
-- arrived from a beacon and has no identity to rate-limit against.
CREATE TABLE IF NOT EXISTS desk_rings (
    id        TEXT PRIMARY KEY,
    desk_id   TEXT NOT NULL REFERENCES desks(id),
    caller_id TEXT,
    note      TEXT,
    rung_at   TEXT NOT NULL,
    acked_at  TEXT
);

-- Coming up on stream. Joining a live room has two shapes and they are not
-- the same act: the audience watches and comments, a guest appears *on* the
-- stream. The second needs the host's yes, because it puts someone into a
-- broadcast the host is answerable for — and on a rated desk it also needs a
-- verified adult, since a guest there is a person going live on an 18+ stream
-- rather than merely watching one.
CREATE TABLE IF NOT EXISTS desk_guests (
    id           TEXT PRIMARY KEY,
    desk_id      TEXT NOT NULL REFERENCES desks(id),
    guest_id     TEXT NOT NULL,
    display_name TEXT,
    note         TEXT,
    status       TEXT NOT NULL DEFAULT 'requested',  -- requested | accepted
                                                     -- | declined | left
    requested_at TEXT NOT NULL,
    decided_at   TEXT
);

-- A desk left behind as a printed code — the sticker on the shop door that
-- says "I'm out back, ring the bell". Deliberately its own table rather than
-- a nullable desk_id on `beacons`: that column is NOT NULL on every database
-- already out there, and this schema is applied with CREATE TABLE IF NOT
-- EXISTS, so widening an existing table would only take effect on a fresh
-- one. Additive works everywhere.
-- Commerce: gifts, and the offer that turns a listing into something buyable.

-- A listing is a shop window. An *offer* is what makes it a shop.
--
-- Deliberately a side table rather than columns on `listings`. Partly because
-- this schema is applied with CREATE TABLE IF NOT EXISTS, so new columns on an
-- existing table would only ever appear on a fresh database — but mostly
-- because it makes the safety property structural instead of a check someone
-- can forget: a listing with no offer row has no seller and no price, and
-- therefore cannot be bought. `POST /marketplace/listings` needs no token and
-- never has, so anyone can create a listing; nobody can attach money to one
-- without holding a token and becoming its recorded seller.
-- Where a listing is offered. A side table for the same reason listing_offers
-- is one — and because `listings.area` is a *subject* area (healthcare,
-- finance, relationships), not a place. Folding geography into that column
-- would make "near me" quietly mean "in healthcare".
--
-- Deliberately coarse: a named locality a seller typed, never coordinates and
-- never anything sniffed from an address or an IP. And a rated listing can
-- never get a row here at all (see marketplace.set_place), which makes "you
-- cannot filter your way to where a performer physically is" structural rather
-- than a check somebody has to remember.
CREATE TABLE IF NOT EXISTS listing_places (
    listing_id TEXT PRIMARY KEY REFERENCES listings(id),
    locality   TEXT NOT NULL,   -- as typed, e.g. "Oakland, CA"
    region     TEXT,            -- broader bucket, e.g. "California"
    remote     INTEGER NOT NULL DEFAULT 0,  -- also served from anywhere
    created_at TEXT NOT NULL
);

-- One interactor's saved marketplace settings: where they consider "here",
-- how far out they want to look, and the kinds and tags they keep choosing.
-- Typed by them — nothing here is inferred from a device.
CREATE TABLE IF NOT EXISTS marketplace_prefs (
    interactor_id  TEXT PRIMARY KEY REFERENCES interactors(id),
    locality       TEXT,
    region         TEXT,
    scope          TEXT NOT NULL DEFAULT 'anywhere',  -- locality | region | anywhere
    include_remote INTEGER NOT NULL DEFAULT 1,
    kinds          TEXT NOT NULL DEFAULT '[]',
    tags           TEXT NOT NULL DEFAULT '[]',
    updated_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS listing_offers (
    listing_id TEXT PRIMARY KEY REFERENCES listings(id),
    seller_id  TEXT NOT NULL,   -- who the sale accrues to
    price      REAL NOT NULL,
    currency   TEXT NOT NULL DEFAULT 'USD',
    stock      INTEGER,         -- NULL = unlimited
    status     TEXT NOT NULL DEFAULT 'open',   -- open | closed
    created_at TEXT NOT NULL
);

-- One purchase. Kept even when the listing is later withdrawn, because a
-- receipt that disappears with the shop window is not a receipt.
CREATE TABLE IF NOT EXISTS orders (
    id         TEXT PRIMARY KEY,
    listing_id TEXT NOT NULL REFERENCES listings(id),
    title      TEXT NOT NULL,   -- copied at purchase: what they actually bought
    buyer_id   TEXT NOT NULL,
    seller_id  TEXT NOT NULL,
    price      REAL NOT NULL,
    currency   TEXT NOT NULL DEFAULT 'USD',
    ledger_ref TEXT,            -- the seller's ledger entry
    status     TEXT NOT NULL DEFAULT 'paid',
    created_at TEXT NOT NULL
);

-- A gift: value sent to a person with nothing delivered back. That asymmetry
-- is why gifts carry rules purchases do not — see qrme/commerce.py.
CREATE TABLE IF NOT EXISTS gifts (
    id           TEXT PRIMARY KEY,
    subject_kind TEXT NOT NULL,  -- profile | desk
    subject_id   TEXT NOT NULL,
    giver_id     TEXT NOT NULL,
    beneficiary  TEXT NOT NULL,  -- whose ledger it lands on
    amount       REAL NOT NULL,
    currency     TEXT NOT NULL DEFAULT 'USD',
    note         TEXT,
    ledger_ref   TEXT,
    created_at   TEXT NOT NULL
);

-- The audience layer: what a viewer does other than talk. Likes, comments,
-- shares and subscriptions all point at a (kind, id) pair rather than at a
-- profile column, because the same four verbs have to work on a synthetic
-- profile, a live desk, a room message and a marketplace listing without four
-- copies of each table.

-- A like. UNIQUE on (target, actor) rather than a counter column: a like is a
-- fact about one person, not a number that can be pumped by calling twice.
CREATE TABLE IF NOT EXISTS reactions (
    id          TEXT PRIMARY KEY,
    target_kind TEXT NOT NULL,   -- profile | desk | message | listing
    target_id   TEXT NOT NULL,
    actor_id    TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    UNIQUE (target_kind, target_id, actor_id)
);

-- A comment. Moderated on the way in exactly like a chat turn: a blocked one
-- is kept so its author can see what happened to it, and shown to nobody else.
-- What a profile has done, shown on its front page. Owner-written, replaced
-- wholesale rather than edited row by row, because a CV is a statement.
--
-- On a profile that depicts a REAL person this is a credential, so
-- frontpage.set_experience refuses it without the same rights basis the
-- persona needed. On a fictional profile the invented history is the point.
CREATE TABLE IF NOT EXISTS profile_experience (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    position   INTEGER NOT NULL DEFAULT 0,
    title      TEXT NOT NULL,
    org        TEXT,
    period     TEXT,
    detail     TEXT,
    created_at TEXT NOT NULL
);

-- A review, by somebody who actually talked to the profile.
--
-- UNIQUE (profile_id, author_id) is the load-bearing line: one review per
-- person, edited rather than stacked, so review-bombing from a single account
-- is impossible in the schema rather than in a check somebody could forget.
-- A blocked review is kept and shown to its author alone, and its rating does
-- not count toward the average.
CREATE TABLE IF NOT EXISTS profile_reviews (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    author_id   TEXT NOT NULL REFERENCES interactors(id),
    rating      INTEGER NOT NULL,          -- 1..5
    body        TEXT,
    status      TEXT NOT NULL,             -- approved | blocked
    flag_reason TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT,
    UNIQUE (profile_id, author_id)
);

CREATE TABLE IF NOT EXISTS comments (
    id          TEXT PRIMARY KEY,
    target_kind TEXT NOT NULL,
    target_id   TEXT NOT NULL,
    author_id   TEXT NOT NULL,
    body        TEXT NOT NULL,
    status      TEXT NOT NULL,   -- approved | blocked
    flag_reason TEXT,
    created_at  TEXT NOT NULL
);

-- A share. Recorded rather than merely counted, because "shared 40 times"
-- and "shared 40 times by one account" are different facts and only one of
-- them is worth anything.
CREATE TABLE IF NOT EXISTS shares (
    id          TEXT PRIMARY KEY,
    target_kind TEXT NOT NULL,
    target_id   TEXT NOT NULL,
    actor_id    TEXT,            -- NULL: shared from a beacon page, no account
    channel     TEXT NOT NULL DEFAULT 'link',
    created_at  TEXT NOT NULL
);

-- A subscription. Two tiers on one row: `follow` is free and means "tell me
-- when they are live", `paid` additionally credits the creator's ledger every
-- period. Cancelling sets status and keeps the row, so a lapsed subscriber is
-- distinguishable from someone who was never there.
CREATE TABLE IF NOT EXISTS subscriptions (
    id           TEXT PRIMARY KEY,
    subject_kind TEXT NOT NULL,  -- profile | desk
    subject_id   TEXT NOT NULL,
    subscriber   TEXT NOT NULL,
    tier         TEXT NOT NULL DEFAULT 'follow',  -- follow | paid
    price        REAL NOT NULL DEFAULT 0,
    currency     TEXT NOT NULL DEFAULT 'USD',
    status       TEXT NOT NULL DEFAULT 'active',  -- active | cancelled
    started_at   TEXT NOT NULL,
    renewed_at   TEXT,
    periods      INTEGER NOT NULL DEFAULT 0,      -- how many have been charged
    cancelled_at TEXT,
    UNIQUE (subject_kind, subject_id, subscriber)
);

CREATE TABLE IF NOT EXISTS desk_beacons (
    id         TEXT PRIMARY KEY,   -- dbn_… — also the QR token
    desk_id    TEXT NOT NULL REFERENCES desks(id),
    label      TEXT NOT NULL,      -- e.g. "on the shop door"
    location   TEXT,               -- free-text place
    scans      INTEGER NOT NULL DEFAULT 0,
    active     INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

-- A signing credential is a WebAuthn/passkey public key bound to an account
-- whose identity was proofed at enrollment. The proofing level is stored
-- here, not inferred, because it decides what this credential may sign.
CREATE TABLE IF NOT EXISTS signing_credentials (
    id              TEXT PRIMARY KEY,
    account_id      TEXT NOT NULL,
    credential_id   TEXT NOT NULL UNIQUE,   -- base64url, as the client sends it
    public_key      TEXT NOT NULL,          -- COSE key as JSON (see webauthn.py)
    aaguid          TEXT,                   -- which authenticator model
    alg             INTEGER NOT NULL,
    sign_count      INTEGER NOT NULL DEFAULT 0,
    backup_eligible INTEGER NOT NULL DEFAULT 0,   -- may this key sync?
    backed_up       INTEGER NOT NULL DEFAULT 0,   -- does it currently?
    proofing_level  TEXT NOT NULL,
    proofing_method TEXT,
    proofing_ref    TEXT,                   -- evidence reference, never the ID image
    proofing_attestor TEXT,
    display_name    TEXT,                   -- the signer's name, for manifestations
    created_at      TEXT NOT NULL,
    revoked_at      TEXT
);

-- One row per signing request. The challenge IS the document hash, so an
-- envelope is the binding between a person's gesture and a specific record.
CREATE TABLE IF NOT EXISTS signature_envelopes (
    id            TEXT PRIMARY KEY,
    account_id    TEXT NOT NULL,
    tier          TEXT NOT NULL,
    meaning       TEXT NOT NULL,
    document_sha256 TEXT NOT NULL,
    display_text  TEXT NOT NULL,
    display_sha256 TEXT NOT NULL,
    payload       TEXT NOT NULL,            -- the canonical bytes that were hashed
    challenge     TEXT NOT NULL,            -- base64url of SHA-256(payload)
    binding_kind  TEXT,                     -- what record this signs
    binding_ref   TEXT,
    issued_at     TEXT NOT NULL,
    expires_at    TEXT NOT NULL,
    consumed_at   TEXT                      -- single use, enforced server-side
);

-- The evidence package. Written once, never regenerated: this is the
-- artifact a dispute is fought over. The public key is COPIED here so that
-- revoking the credential cannot take past signatures down with it.
CREATE TABLE IF NOT EXISTS signatures (
    id                 TEXT PRIMARY KEY,
    envelope_id        TEXT NOT NULL,
    account_id         TEXT NOT NULL,
    credential_id      TEXT NOT NULL,
    public_key         TEXT NOT NULL,
    aaguid             TEXT,
    alg                INTEGER NOT NULL,
    signature          TEXT NOT NULL,       -- base64url, raw as received
    authenticator_data TEXT NOT NULL,       -- base64url
    client_data_json   TEXT NOT NULL,       -- base64url
    user_verified      INTEGER NOT NULL,
    backup_eligible    INTEGER NOT NULL,
    backed_up          INTEGER NOT NULL,
    sign_count         INTEGER NOT NULL,
    sign_count_regressed INTEGER NOT NULL DEFAULT 0,
    transport          TEXT,                -- internal | hybrid
    platform           TEXT,                -- ios | visionos | android | quest | web
    proofing_level     TEXT NOT NULL,
    tier               TEXT NOT NULL,
    signer_name        TEXT,
    binding_kind       TEXT,
    binding_ref        TEXT,
    sealed_ref         TEXT,                -- PDI record, when a vault is configured
    signed_at          TEXT NOT NULL
);

-- The homepage a person builds for themselves, as opposed to the front page
-- the platform assembles. Theme, colour, a tagline, a paragraph, and a Top 8.
--
-- Deliberately a fixed set of columns and a closed theme list rather than a
-- blob of markup. MySpace let people paste raw HTML and CSS, which is why it
-- was also the golden age of drive-by script injection; the nostalgia worth
-- keeping is the feeling of a place you decorated, not the implementation.
--
-- `about` carries a moderation status like any other text a person writes for
-- other people to read, and a blocked one is kept so its author can be told
-- why rather than having it vanish.
CREATE TABLE IF NOT EXISTS profile_pages (
    profile_id   TEXT PRIMARY KEY REFERENCES profiles(id),
    theme        TEXT NOT NULL DEFAULT 'midnight',
    accent       TEXT,                       -- #rrggbb, validated
    layout       TEXT NOT NULL DEFAULT 'classic',
    tagline      TEXT,
    about        TEXT,
    about_status TEXT NOT NULL DEFAULT 'approved',  -- approved | blocked
    about_flag   TEXT,
    top_friends  TEXT NOT NULL DEFAULT '[]',  -- JSON, owner's order
    html         TEXT,                       -- sanitised: see qrme/markup.py
    html_removed TEXT NOT NULL DEFAULT '[]',  -- JSON: what the filter stripped
    links        TEXT NOT NULL DEFAULT '[]',  -- JSON [{label, url}]
    show_offers  INTEGER NOT NULL DEFAULT 0,  -- surface this profile's listings
    updated_at   TEXT NOT NULL
);

-- How well a profile's identity has been established. Distinct from `kind`,
-- which says whether there is a real person at all: this says whether anybody
-- checked they are who they claim. The ladder is signatures.PROOFING_LEVELS,
-- reused so the platform has one meaning for it rather than two that drift,
-- and `attestor` is required above self_asserted for the same reason it is
-- there — who checked belongs in the record, not in a footnote.
CREATE TABLE IF NOT EXISTS profile_verification (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    level      TEXT NOT NULL,   -- self_asserted | federated | document | in_person
    attestor   TEXT,            -- who checked; required above self_asserted
    method     TEXT,
    ref        TEXT,            -- evidence held elsewhere, never the document
    checked_at TEXT NOT NULL
);

-- Friendships between profiles. Distinct from `relationships`, which records
-- how one profile treats one *interactor* — the person typing at it. This is
-- the other axis: profile ↔ profile, the social graph the community surfaces
-- are drawn from.
--
-- Directed on purpose. A friends list is a claim its owner makes about who
-- they stand with, and making it mutual would mean one profile's list could be
-- edited by somebody else. Two rows make a mutual friendship, and `mutual` on
-- the read side reports whether the other row exists.
--
-- `state` rather than DELETE, so a removal is durable. The founder row is
-- installed on every new profile, and if it were deleted outright the next
-- install would put it straight back — a friend you cannot get rid of, which
-- is furniture rather than a friendship.
CREATE TABLE IF NOT EXISTS friendships (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    friend_id    TEXT NOT NULL REFERENCES profiles(id),
    origin       TEXT NOT NULL DEFAULT 'chosen',  -- chosen | founder
    state        TEXT NOT NULL DEFAULT 'active',  -- active | removed
    created_at   TEXT NOT NULL,
    removed_at   TEXT,
    UNIQUE (profile_id, friend_id)
);
"""

_local = threading.local()


def db_path() -> str:
    return os.environ.get("QRME_DB", "qrme.db")


def connect() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None or getattr(_local, "path", None) != db_path():
        conn = sqlite3.connect(db_path())
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")  # concurrent readers
        conn.executescript(_SCHEMA)
        _local.conn = conn
        _local.path = db_path()
    return conn


def reset() -> None:
    """Close the thread-local connection (used by tests when QRME_DB changes)."""
    conn = getattr(_local, "conn", None)
    if conn is not None:
        conn.close()
        _local.conn = None
        _local.path = None


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
