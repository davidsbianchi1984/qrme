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
CREATE TABLE IF NOT EXISTS marketplace (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    tags       TEXT NOT NULL DEFAULT '[]',
    blurb      TEXT,
    listed_at  TEXT NOT NULL
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
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    surface     TEXT,
    topic       TEXT,
    content     TEXT NOT NULL,
    status      TEXT NOT NULL,  -- approved | pending | rejected
    flag_reason TEXT,
    created_at  TEXT NOT NULL
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
