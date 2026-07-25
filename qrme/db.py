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
CREATE TABLE IF NOT EXISTS posts (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    surface      TEXT,
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
