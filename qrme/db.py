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
