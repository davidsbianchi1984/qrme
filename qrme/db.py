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
    purpose           TEXT,                   -- legacy_memorial | family | creator_persona
                                              -- | social_fan | companion_coach | enterprise_agent
    maturity          TEXT NOT NULL DEFAULT 'balanced',  -- strict | balanced | open
    cloud_contribution INTEGER NOT NULL DEFAULT 0,  -- opt-in: share rated,
                                                    -- anonymized exchanges to
                                                    -- improve the cloud model
    status            TEXT NOT NULL DEFAULT 'active',  -- active | departed
    created_at        TEXT NOT NULL
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

-- AI Profile Marketplace: owner-listed profiles discoverable by others.
CREATE TABLE IF NOT EXISTS marketplace (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    tags       TEXT NOT NULL DEFAULT '[]',
    blurb      TEXT,
    listed_at  TEXT NOT NULL
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
    created_at   TEXT NOT NULL
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
