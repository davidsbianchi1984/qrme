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
    unlisted          INTEGER NOT NULL DEFAULT 0,  -- out of the browse pool,
                                              -- by the owner's own choice;
                                              -- every profile starts listed
    adult_mode        INTEGER NOT NULL DEFAULT 0,
    interaction_scope TEXT NOT NULL DEFAULT 'reactive',  -- reactive | proactive
    moderation_mode   TEXT NOT NULL DEFAULT 'auto',      -- auto | manual
    aging_enabled     INTEGER NOT NULL DEFAULT 0,
    base_age          INTEGER,
    appearance        TEXT NOT NULL DEFAULT '',  -- how the profile looks/presents
                                              -- (steering hub); rides on the prompt
    guest_styling     INTEGER NOT NULL DEFAULT 1,  -- may the people a profile
                                              -- talks with restyle its avatar;
                                              -- the owner's switch, on until
                                              -- the owner says otherwise
    consent_basis     TEXT,                   -- required when kind=other_person
    consent_attestor  TEXT,
    successor_owner   TEXT,                   -- legacy succession
    licensed_from     TEXT,                   -- source profile a licensed
                                              -- specialist agent was derived from
    forgot_at         TEXT,                   -- when a forgetting door last
                                              -- touched this profile; letters
                                              -- built before this rebuild
                                              -- (qrme/letter.py shelf)
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
    avatar_ref        TEXT,                   -- the face's registry row (qrme/avatarreg.py)
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
    -- The governor's release. 0 is the standing default: ten unprompted
    -- turns apiece, then the room waits for a person. 1 only after the
    -- person said so in words ("no limit", "run in the background") —
    -- "on the user's choice and dime" — and any pause word puts it back.
    free_run   INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS room_participants (
    room_id TEXT NOT NULL REFERENCES rooms(id),
    kind    TEXT NOT NULL,   -- user | profile
    ref_id  TEXT NOT NULL,
    -- A person's seat sitting out: the room stops waiting on them and
    -- the profiles keep their own rotation. Off until they tap it, and
    -- off again the moment they sit back in.
    sitting_out INTEGER NOT NULL DEFAULT 0,
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
    media_id    TEXT REFERENCES media(id),  -- a shared picture, video or file
    media_text  TEXT,            -- the words in it, for a person to read back
    media_digest TEXT,           -- the reading every later turn carries
    -- WHY it could not be read, when it could not. "This deployment could not
    -- turn it into words" is true of a scan, a locked file and a font this
    -- code cannot follow, and a profile told only that cannot suggest which
    -- of the three the person should do something about. NULL when it read.
    media_why   TEXT,
    -- The shared document's OWN length, when the cap kept less. Same fact and
    -- same reason as briefcase_items.full_chars: a profile holding the first
    -- third of a filing and believing it holds the filing answers about the
    -- rest from material it never saw. NULL when nothing was cut.
    media_full  INTEGER,
    -- How much of this turn was actually heard, when somebody cut it off
    -- mid-sentence. NULL is the ordinary case: it played out, or nobody was
    -- listening to it aloud at all.
    heard       TEXT,
    -- Who this turn was aimed at — a seat's display name, parsed from the
    -- speaker's own words (a profile's `[to: Ada]` marker, or a person
    -- naming a seat). NULL is a turn for the whole room. The rotation in
    -- qrme/society.py reads it to hand the next turn to the seat it was
    -- for, which is what makes eight seats a conversation instead of
    -- eight simultaneous answers.
    aimed_at    TEXT,
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

-- The profile reached its limit on a named matter. The exits hang off this
-- record rather than off a sentence in a chat turn, so what was offered and
-- what happened next are answerable afterwards by somebody who was not there.
-- `placed` is set by a call that actually connected and by nothing else: a
-- deployment whose dialer is sealed records the attempt and leaves it 0.
CREATE TABLE IF NOT EXISTS escalations (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    matter        TEXT NOT NULL,
    dialed_at     TEXT,
    placed        INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL
);

-- What the owner has let the agent do. Absent means *never asked*, which is
-- why a decision is written even when it matches the default: a row here is
-- somebody's answer, and it survives a default changing under it. The defaults
-- themselves live in qrme/privileges.py beside what each power costs, and a
-- guard refuses any that reach people who did not choose them.
CREATE TABLE IF NOT EXISTS chosen_privileges (
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    privilege  TEXT NOT NULL,
    chosen     INTEGER NOT NULL,
    decided_at TEXT NOT NULL,
    PRIMARY KEY (profile_id, privilege)
);

-- The emergency-services charges waiver, signed ahead of time in calm
-- conditions rather than during the emergency. The signed text is stored
-- beside its hash: "they agreed" is a claim, and this is the evidence.
CREATE TABLE IF NOT EXISTS dial_waivers (
    interactor_id TEXT PRIMARY KEY REFERENCES interactors(id),
    signature_id  TEXT NOT NULL,
    waiver        TEXT NOT NULL,
    waiver_sha256 TEXT NOT NULL,
    signed_at     TEXT NOT NULL
);

-- The people a user has already chosen, in every area of life — their
-- butcher, their broker, their doctor. `referral.match` searches the map;
-- this is who they trust, and a handoff consults it first. `area` is copied
-- from the provider row at attach time rather than accepted from the caller,
-- so nobody can be filed under an expertise they do not have — see
-- qrme/mypeople.py. Exactly one row per area carries `preferred`.
CREATE TABLE IF NOT EXISTS known_providers (
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    provider_id   TEXT NOT NULL REFERENCES providers(id),
    area          TEXT NOT NULL,
    preferred     INTEGER NOT NULL DEFAULT 0,
    note          TEXT,
    attached_at   TEXT NOT NULL,
    PRIMARY KEY (interactor_id, provider_id)
);
CREATE INDEX IF NOT EXISTS idx_known_area
    ON known_providers (interactor_id, area);

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

-- Channel 2 everywhere else: the same lent wearable, on the surfaces that are
-- not a room — a watch party, a live desk's stream, a one-to-one connection.
--
-- A separate table from `room_mics` rather than a column added to it, because
-- this schema has no migrations: `CREATE TABLE IF NOT EXISTS` reaches a fresh
-- database and an ALTER reaches none of the existing ones. A new table is the
-- only shape that arrives everywhere.
--
-- Rooms deliberately do **not** write here. Two storage paths for one surface
-- is how a disclosure ends up reading one table while the grant sits in the
-- other, and a microphone that is live but undisclosed is the single worst
-- failure this feature has. `roommic.lend_on` refuses `surface='room'` and
-- points at the room routes.
CREATE TABLE IF NOT EXISTS place_mics (
    id            TEXT PRIMARY KEY,
    surface       TEXT NOT NULL,   -- party | desk | connection
    surface_id    TEXT NOT NULL,
    interactor_id TEXT NOT NULL,
    device        TEXT NOT NULL,
    mic_type      TEXT NOT NULL DEFAULT 'watch',
    requested_gain TEXT NOT NULL DEFAULT 'near_field',
    gain          TEXT NOT NULL DEFAULT 'near_field',
    started_at    TEXT NOT NULL,
    ended_at      TEXT
);
CREATE INDEX IF NOT EXISTS idx_place_mics_live
    ON place_mics (surface, surface_id) WHERE ended_at IS NULL;

-- Overlays: a character worn over a person's own camera. Permission and state
-- only — the compositing happens on the device, like capture.
--
-- `removed_at` rather than a delete, so "who was wearing what, when" survives
-- the overlay coming off: a viewer who saw a face and later wants to know what
-- they were actually looking at has an answer.
CREATE TABLE IF NOT EXISTS overlays (
    id            TEXT PRIMARY KEY,
    interactor_id TEXT NOT NULL,
    surface       TEXT NOT NULL,   -- room | party | connection | stream | desk
    surface_id    TEXT NOT NULL,
    -- mask | character | creature | puppet | helmet_hud | touch_up | backdrop.
    -- See qrme/overlays.py:KINDS — the ones that cover a face are disclosed
    -- differently from the ones that do not, because they are different claims
    -- about what the viewer is seeing.
    kind          TEXT NOT NULL,
    title         TEXT NOT NULL,   -- shown to everyone who can see the wearer
    asset         TEXT,
    -- Where the picture behind them came from: own | imported | generated |
    -- blur. Only meaningful for `backdrop`. `generated` is synthetic media
    -- even though the person in front of it is real, and the two are disclosed
    -- separately because they are separate claims.
    --
    -- Added to the CREATE rather than by an ALTER because this table has never
    -- been in a release — it was introduced earlier in this same unreleased
    -- branch, so no deployment has it. A working copy that ran the
    -- intermediate commit needs its dev database recreated.
    source        TEXT,
    worn_at       TEXT NOT NULL,
    removed_at    TEXT
);
CREATE INDEX IF NOT EXISTS idx_overlays_live
    ON overlays (surface, surface_id) WHERE removed_at IS NULL;

-- What each person in a room is showing: a name in a box, a picture they
-- uploaded, or their camera. See qrme/roomface.py — the important part is that
-- all three are a box, so a person who is muted or off-camera stays in the
-- scene at the same size as everybody else.
--
-- Absence is meaningful and is the default: no row means `voice`, which is a
-- person who is here. So the seats come from `room_participants` and this
-- table only says what is in them.
--
-- `camera` stores the *fact*, never the pixels. Capture and rendering are on
-- the device, the same division qrme/overlays.py draws; what a shared row buys
-- is that every other client in the room draws the same scene.
--
-- Separate from `overlays` on purpose. Showing and wearing are two questions —
-- a wolf mask can sit on a live camera or on nothing at all — and one row
-- holding both would make taking a mask off and turning a camera off the same
-- action.
CREATE TABLE IF NOT EXISTS room_faces (
    room_id       TEXT NOT NULL REFERENCES rooms(id),
    interactor_id TEXT NOT NULL,
    showing       TEXT NOT NULL DEFAULT 'voice',  -- voice | photo | camera
    -- The upload, when there is one. Kept across a switch to camera or voice
    -- so turning a camera off does not throw away the picture underneath.
    media_id      TEXT,
    media_url     TEXT,
    -- What is BEHIND you, which is a different object from what stands in
    -- FOR you. `photo` replaces the person; a background sits under a
    -- portrait and leaves the person on top of it. Kept on its own pair of
    -- columns for the same reason the photo is kept across a switch: taking
    -- your camera off should not throw away the room you chose to sit in.
    background_id  TEXT,
    background_url TEXT,
    updated_at    TEXT NOT NULL,
    PRIMARY KEY (room_id, interactor_id)
);

-- The picture an anonymous profile shows instead of a face. One row per
-- profile, and a **separate table from `profiles.avatar`** on purpose: the two
-- are pictures for two different states, exactly like a display name and an
-- anonymous one. Writing this into `avatar` would mean turning anonymity off
-- showed it instead of the face somebody actually has.
--
-- Either a preset emblem key (qrme/identity.py:EMBLEM_FIELDS) or an image the
-- owner uploaded — never both, and neither is required: no row means the plain
-- silhouette. It briefly held emblems only, on the reasoning that a closed set
-- was the enforcement against uploading a face; that made the feature useless
-- to somebody who wants a picture of their own workshop, and what the platform
-- cannot check it says plainly instead of pretending to prevent.
CREATE TABLE IF NOT EXISTS anonymous_pictures (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    emblem     TEXT,           -- a preset field emblem, or NULL
    asset      TEXT,           -- or their own image, or NULL
    set_at     TEXT NOT NULL
);

-- A profile on a screen that stays where it is: a wall panel, a kiosk, a pane
-- of glass. The watch-face idea (qrme/wearables.py:FACES) for fixtures, with a
-- shorter list of things that may be shown — a watch is read by its wearer, a
-- wall by whoever walks past.
--
-- `removed_at` rather than a delete, like an unpaired wearable: a profile that
-- was on a lobby wall for a year should still be able to say where it was.
CREATE TABLE IF NOT EXISTS displays (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    kind       TEXT NOT NULL,   -- wall_panel | kiosk | counter_screen | …
    label      TEXT NOT NULL,   -- what the owner calls it: "the lobby panel"
    location   TEXT,
    size       TEXT NOT NULL DEFAULT 'full',      -- badge | half | full
    finish     TEXT NOT NULL DEFAULT 'opaque',    -- opaque | transparent
    faces      TEXT NOT NULL DEFAULT '[]',        -- JSON list, see displays.FACES
    placed_at  TEXT NOT NULL,
    removed_at TEXT
);

-- How far somebody has got through the guided walkthrough. One row per step
-- rather than a cursor, so a learner who skipped ahead and came back is not
-- told they have finished things they never saw.
CREATE TABLE IF NOT EXISTS tutorial_progress (
    learner_id TEXT NOT NULL,
    lesson     TEXT NOT NULL,
    done_at    TEXT NOT NULL,
    PRIMARY KEY (learner_id, lesson)
);

-- Channel 3: a live view through somebody's camera (see qrme/viewfinder.py).
--
-- Permission and state only. No frame, no still, no thumbnail — the video
-- never touches this database and there is deliberately no column it could
-- land in. A session is a record that somebody agreed to point a camera at
-- something for a while.
--
-- `subject` is what the camera is pointed at, and it is the column everything
-- else reads from: who may watch is decided by what is in shot rather than by
-- who is asking. `bystanders` holds what the holder declared about the room,
-- which is not something this software can observe for itself.
--
-- `state` rather than DELETE so a finished session is auditable — "was a
-- camera live in that room, and who was watching" is exactly the question
-- asked afterwards.
CREATE TABLE IF NOT EXISTS camera_sessions (
    id          TEXT PRIMARY KEY,
    holder_id   TEXT NOT NULL,
    surface     TEXT NOT NULL,          -- room | connection | desk | exchange
    surface_id  TEXT NOT NULL,
    subject     TEXT NOT NULL,          -- object | place | document | person
    viewer_kind TEXT NOT NULL,          -- person | profile
    viewer_id   TEXT NOT NULL,
    minutes     INTEGER NOT NULL,
    recording   INTEGER NOT NULL DEFAULT 0,
    bystanders  TEXT,
    note        TEXT,
    state       TEXT NOT NULL DEFAULT 'live',   -- live | ended | expired
    opened_at   TEXT NOT NULL,
    ended_at    TEXT,
    ended_by    TEXT
);
CREATE INDEX IF NOT EXISTS camera_sessions_place
    ON camera_sessions (surface, surface_id, state);

-- What an account has paid for (see qrme/tiers.py). Keyed on the *account*
-- (`profiles.owner_id`) rather than on a profile, because a membership is
-- something a person holds and profiles are things they make with it.
--
-- One live row per account, enforced by ending the previous one rather than by
-- a unique index: the history is worth keeping — "when did this account go
-- from basic to pro" is a question a statement has to answer — and an account
-- on two plans at once is a question nobody should face at the moment a gate
-- is being checked.
--
-- Billing is simulated, like everything else money-shaped in this repository.
-- There is no charge here, no processor and no token: the row *is* the
-- subscription.
CREATE TABLE IF NOT EXISTS memberships (
    id         TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    plan       TEXT NOT NULL,          -- basic | pro
    started_at TEXT NOT NULL,
    ended_at   TEXT
);
CREATE INDEX IF NOT EXISTS memberships_live
    ON memberships (account_id, ended_at);

-- Where the helper dock sits and what it is showing (see qrme/dock.py). One
-- row per account, absent until somebody moves it — `dock.settings` applies
-- the defaults, so the pane draws on first launch without this row existing
-- and the defaults are written down in exactly one place.
--
-- Preferences only. Nothing about the dock is a capability: the pane shows and
-- routes, and this table cannot grant it anything, because there is nothing to
-- grant.
CREATE TABLE IF NOT EXISTS dock_prefs (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    corner     TEXT NOT NULL DEFAULT 'bottom_right',  -- bottom_right | bottom_left
    state      TEXT NOT NULL DEFAULT 'handle',        -- hidden | handle | open
    face       TEXT NOT NULL DEFAULT 'helper',
    faces      TEXT NOT NULL,                         -- JSON array
    updated_at TEXT NOT NULL
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

-- The briefcase: material one INTERACTOR handed one profile, mid-conversation
-- — a link, a photograph, a filing, a video. Deliberately not a `source_items`
-- row: source material is what the profile recalls as its own and every
-- visitor sees it, whereas this belongs to the pair and stays with the pair.
-- `text` is what was extracted at import; `digest` is the distillation the
-- prompt carries on every later turn, so a long document is paid for once.
-- `was_read` is 0 when this deployment held the bytes and could not turn them
-- into words (a photograph, a video, a scanned PDF) — the item still exists,
-- and the prompt says plainly that the profile has not seen it.
CREATE TABLE IF NOT EXISTS briefcase_items (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    kind          TEXT NOT NULL,   -- link | photo | video | document
    title         TEXT NOT NULL,
    note          TEXT,            -- what the person said it is
    source        TEXT,            -- the URL, or the uploaded filename
    text          TEXT,            -- extracted once, kept for reading back
    digest        TEXT,            -- what every turn carries
    was_read      INTEGER NOT NULL DEFAULT 1,
    -- WHY it could not be read, when it could not: 'scanned', 'unmapped',
    -- 'locked'. Three failures wore one sentence, and they want three
    -- different answers — a scan needs somebody's eyes, an unfollowable font
    -- is a gap in this code, a locked file needs its password. NULL for
    -- anything that read, and for kinds that never claimed to.
    unread_why    TEXT,
    -- The document's OWN length, when the cap kept less than all of it. The
    -- cap is wanted — a briefcase is not an archive — but it was silent, and
    -- the count shown beside an item was the kept length rather than the
    -- document's. NULL when nothing was cut, which is most items.
    full_chars    INTEGER,
    bytes         INTEGER,
    created_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_briefcase_pair
    ON briefcase_items (profile_id, interactor_id);

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
-- The recollection ledger (qrme/recollection.py). Content lives sealed in
-- the tandem under pdi_key and embedded in the resident's index; this table
-- holds only the keys, so the profile-erasure sweep — which reads pdi_key
-- columns — deletes every memory with the profile that made it.
CREATE TABLE IF NOT EXISTS recollections (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL,
    pdi_key       TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    -- Which arrangement this memory landed under, kept per row. See the
    -- note in _ADDED_COLUMNS: a plan changes and a row's posture does not.
    posture       TEXT NOT NULL DEFAULT 'vault',
    -- The words, for platform custody only. NULL on a vaulted row, whose
    -- content lives sealed under pdi_key.
    line          TEXT
);

CREATE TABLE IF NOT EXISTS letters (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    week_start   TEXT NOT NULL,
    body         TEXT NOT NULL,
    described_by TEXT NOT NULL,   -- model | digest
    digest       TEXT NOT NULL,   -- the facts under the words
    -- The letter keeps the excursions' promise (qrme/letter.py): whether
    -- composing it sent the (sanitized) digest to an external model, and
    -- how many private terms the sanitize pass took out first.
    left_host    INTEGER NOT NULL DEFAULT 0,
    redactions   INTEGER NOT NULL DEFAULT 0,
    -- When this body was last built. A letter is a cached view of its
    -- week: profiles.forgot_at newer than this means a forgetting has
    -- touched the profile and the body rebuilds before it is shown.
    built_at     TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lookouts (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    url          TEXT NOT NULL,
    every_hours  REAL NOT NULL,
    task_id      TEXT NOT NULL,   -- the standing task in the vault
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS excursions (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    topic        TEXT NOT NULL,       -- stays local (owner's data)
    brief        TEXT NOT NULL,       -- sanitized outbound query
    redactions   INTEGER NOT NULL DEFAULT 0,
    left_host    INTEGER NOT NULL DEFAULT 0,
    findings     TEXT,                -- general knowledge brought back
    learned_src  TEXT,                -- source_item id once folded in
    answered_by  TEXT,                -- who actually wrote the findings
    created_at   TEXT NOT NULL
);

-- Inquiries. An excursion asks a model; an inquiry asks people. The question
-- goes onto a public board that anybody can answer WITHOUT an account, and
-- what comes back can be folded into the profile the same way findings are.
-- ``brief`` is the sanitized question and the ONLY column an outsider ever
-- sees — see qrme/inquiries.PUBLIC_FIELDS. ``topic`` and ``question`` are the
-- owner's own words and stay local, as they do for excursions.
CREATE TABLE IF NOT EXISTS inquiries (
    id           TEXT PRIMARY KEY,
    profile_id   TEXT NOT NULL REFERENCES profiles(id),
    topic        TEXT NOT NULL,       -- stays local (owner's data)
    question     TEXT NOT NULL,       -- stays local (owner's data)
    brief        TEXT NOT NULL,       -- sanitized; exactly what is on the board
    redactions   INTEGER NOT NULL DEFAULT 0,
    closed_at    TEXT,                -- the owner stopped taking answers
    created_at   TEXT NOT NULL
);

-- An answer from somebody with no account. ``alias`` is whatever they chose to
-- be called and may be empty. ``points_to`` is the direction they pointed at —
-- a source, a name for the thing, a place to look — never followed
-- automatically. ``blocked`` marks one the moderation filter stopped: kept for
-- the record, shown to nobody, counted in nothing.
CREATE TABLE IF NOT EXISTS inquiry_answers (
    id           TEXT PRIMARY KEY,
    inquiry_id   TEXT NOT NULL REFERENCES inquiries(id),
    alias        TEXT,
    body         TEXT NOT NULL,
    points_to    TEXT,
    blocked      INTEGER NOT NULL DEFAULT 0,
    folded_src   TEXT,                -- source_item id once the owner took it
    created_at   TEXT NOT NULL
);

-- Outbound visits. One row each time this deployment was about to open a
-- connection to a host that is NOT on this side of the wire. The HOST only,
-- never the path — in the scrape case the path is the subject's handle, and a
-- ledger holding it would be a second copy of the private thing. ``profile_id``
-- is NULL for the deployment's own plumbing (the vault, the mail relay, the
-- gateway); see qrme/visits.UNATTRIBUTED for which and why.
CREATE TABLE IF NOT EXISTS outbound_visits (
    id         TEXT PRIMARY KEY,
    profile_id TEXT REFERENCES profiles(id),
    host       TEXT NOT NULL,
    what       TEXT NOT NULL,       -- the caller's short name for the errand
    at         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_visits_host ON outbound_visits (host);
CREATE INDEX IF NOT EXISTS idx_visits_profile ON outbound_visits (profile_id);

-- A host a profile has said it no longer visits. Enforced where the socket
-- opens rather than at the route above it, so a caller added tomorrow
-- inherits the refusal instead of remembering it.
CREATE TABLE IF NOT EXISTS visit_standdowns (
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    host       TEXT NOT NULL,
    at         TEXT NOT NULL,
    PRIMARY KEY (profile_id, host)
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
    -- When the credential this connector needs was given, and where it was
    -- sealed. NULL means installed and unable to reach the service — the lock
    -- the storefront draws. A row the catalog says needs nothing is authorized
    -- the moment it is installed. The secret itself is never in this file:
    -- secret_ref is a PDI vault key, and no vault means no authorizing.
    authorized_at TEXT,
    secret_ref    TEXT,
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

-- The operational ecosystem (PDI proposal: "role-specific AI agents ...
-- collaborate across departments, pulling relevant data, offering smart
-- suggestions, and coordinating efforts"). An organization belongs to an
-- account; its departments each bind one enterprise agent with a scoped,
-- revocable vault grant for its data pulls.
CREATE TABLE IF NOT EXISTS organizations (
    id         TEXT PRIMARY KEY,
    owner_id   TEXT NOT NULL,
    name       TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS departments (
    id         TEXT PRIMARY KEY,
    org_id     TEXT NOT NULL REFERENCES organizations(id),
    name       TEXT NOT NULL,      -- e.g. Finance, Dispatch
    role       TEXT NOT NULL,      -- what its agent does for the team
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    grant_id   TEXT,               -- revocable scope for this agent's reads
    created_at TEXT NOT NULL,
    UNIQUE (org_id, name)
);

-- One coordination: a goal taken across departments, each agent contributing
-- from its own scoped material, the initiating agent composing the joint
-- plan. Sealed into the PDI vault when the tandem is configured.
CREATE TABLE IF NOT EXISTS coordinations (
    id           TEXT PRIMARY KEY,
    org_id       TEXT NOT NULL REFERENCES organizations(id),
    goal         TEXT NOT NULL,
    initiated_by TEXT NOT NULL REFERENCES departments(id),
    plan         TEXT,
    status       TEXT NOT NULL,    -- completed | failed
    watermark_id TEXT,
    pdi_key      TEXT,             -- vault key of the sealed record
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS coordination_contributions (
    coordination_id TEXT NOT NULL REFERENCES coordinations(id),
    department_id   TEXT NOT NULL REFERENCES departments(id),
    content         TEXT NOT NULL, -- that agent's suggestion, in persona
    items_read      INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (coordination_id, department_id)
);

-- Where the proceeds go (spec [0020], example two: "supply crowdfunding for
-- any loved ones left behind or organizations for donations, wherever the
-- proceeds might go up to the user"). Owner-token gated: sunset leaves the
-- living owner the pen; verified owner death (/succeed) revokes it and
-- hands a fresh one to the person they chose.
CREATE TABLE IF NOT EXISTS proceeds_designations (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    name       TEXT NOT NULL,
    kind       TEXT NOT NULL,      -- loved_one | organization
    account_id TEXT,               -- platform account, when the designee has one
    share      INTEGER NOT NULL,   -- percent; a profile's rows sum to 100
    created_at TEXT NOT NULL
);

-- Crowdfunding campaigns on a profile ([0020] example two). A campaign may
-- not exist before the profile says where its money goes.
CREATE TABLE IF NOT EXISTS campaigns (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    title      TEXT NOT NULL,
    cause      TEXT,
    goal       REAL NOT NULL,
    status     TEXT NOT NULL DEFAULT 'open',   -- open | closed
    created_at TEXT NOT NULL,
    closed_at  TEXT
);

CREATE TABLE IF NOT EXISTS campaign_donations (
    id           TEXT PRIMARY KEY,
    campaign_id  TEXT NOT NULL REFERENCES campaigns(id),
    giver_id     TEXT,             -- interactor; NULL is an anonymous gift
    on_behalf_of TEXT,             -- a company backing the campaign, by name
    amount       REAL NOT NULL,
    currency     TEXT NOT NULL DEFAULT 'USD',
    note         TEXT,
    created_at   TEXT NOT NULL
);

-- How one donation split across the designees, with the ledger entry each
-- share landed on — the auditable line from a donor's gift to a loved one's
-- statement.
CREATE TABLE IF NOT EXISTS campaign_splits (
    donation_id    TEXT NOT NULL REFERENCES campaign_donations(id),
    designation_id TEXT NOT NULL REFERENCES proceeds_designations(id),
    amount         REAL NOT NULL,
    ledger_ref     TEXT,
    PRIMARY KEY (donation_id, designation_id)
);

-- Environmental context received during interactions (spec clause 1: the
-- profile "dynamically adapts to environmental data, such as location,
-- conditions, and user behavior, enabling contextual relevance").
CREATE TABLE IF NOT EXISTS environment_context (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    data          TEXT NOT NULL,   -- JSON: location, conditions, local_time, activity
    created_at    TEXT NOT NULL
);

-- Hybrid profiles (spec [0038]): a profile representing "a combination of
-- aspects or characteristics of several people". One row per constituent;
-- the composite profile itself is an ordinary profiles row with kind=hybrid.
CREATE TABLE IF NOT EXISTS composite_sources (
    profile_id        TEXT NOT NULL REFERENCES profiles(id),
    source_profile_id TEXT NOT NULL REFERENCES profiles(id),
    weight            REAL NOT NULL,   -- normalized share of the blend, 0..1
    aspect            TEXT,            -- which side of them is borrowed
    created_at        TEXT NOT NULL,
    PRIMARY KEY (profile_id, source_profile_id)
);

-- Real-time simulation runs (spec clause 1: "real-time simulations of the
-- first person's actions, workflows, and decision-making processes for
-- predictive modeling and operational insights"; clause 5: retained memory
-- "utilized for predictive modeling"). Owner-only, never distributed.
CREATE TABLE IF NOT EXISTS simulations (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT,             -- optional: whose relationship conditions it
    scenario      TEXT NOT NULL,
    horizon       TEXT NOT NULL,    -- immediate | short_term | long_term
    narrative     TEXT NOT NULL,    -- the in-persona prediction
    basis         TEXT NOT NULL,    -- JSON: what evidence conditioned the run
    confidence    REAL NOT NULL,    -- 0..1, from evidence volume, not model mood
    watermark_id  TEXT,             -- synthetic-media credential
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

-- What a derived agent actually received, written at derive time. The amended
-- claims draw the line the manifest records: parameter-level substance (the
-- profile's own knowledge, its characteristics, an aggregate adaptation
-- summary) travels; raw user data — interactor messages, per-relationship
-- embeddings, the person's voice, vaulted content — never does. One row per
-- derivation, so both parties can always read back what crossed and what was
-- withheld, and why.
CREATE TABLE IF NOT EXISTS license_manifests (
    grant_id   TEXT PRIMARY KEY REFERENCES license_grants(id),
    carried    TEXT NOT NULL,    -- JSON: what traveled, by name and count
    withheld   TEXT NOT NULL,    -- JSON: [{item, reason}] — what stayed behind
    created_at TEXT NOT NULL
);

-- The moving image (claims 3/13: "the graphical image is a moving or video
-- image"): the owner's chosen motion style for the profile's portrait. The
-- animation parameters themselves are derived live in avatars.render() from
-- the profile's interaction history, so the picture updates with the
-- relationship the way the clause describes; this row stores only the
-- user-defined half.
CREATE TABLE IF NOT EXISTS avatar_motion (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    style      TEXT NOT NULL,      -- still | breathe | lively
    updated_at TEXT NOT NULL
);

-- What kind of thing the avatar asset is, when the asset itself cannot say.
-- `presentation.kind_of` reads the kind off the string — a `.glb` is a model,
-- a `.mp4` is a video — which covers every asset that carries an extension.
-- A provider serving a model from `/v1/avatar/8831` with the type in a header
-- does not, and guessing wrong there is worse than asking; this row is the
-- owner's own answer for exactly that case. Absent, the string decides.
CREATE TABLE IF NOT EXISTS avatar_presentation (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    kind       TEXT NOT NULL,      -- image | video | model | scene
    created_at TEXT NOT NULL
);

-- AI for lease: an organization seats somebody else's licensed specialist as
-- one of its departments. The lease is the authorization that crosses the
-- account boundary — departments otherwise require the org's own profiles —
-- and it is revocable from the specialist owner's side: a revoked lease
-- leaves the department standing but silent, named in every coordination it
-- no longer speaks in. Consult-class use only; nothing is derived and no
-- substance travels.
CREATE TABLE IF NOT EXISTS license_leases (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL REFERENCES profiles(id),    -- leased specialist
    org_id        TEXT NOT NULL REFERENCES organizations(id),
    department_id TEXT NOT NULL REFERENCES departments(id),
    revoked       INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL
);

-- Local log of every cloud contribution: exactly what left, when, under which
-- opaque ref. The gateway never sees profile ids — the ref is random, and only
-- this table maps it back — so contributions stay anonymous at the gateway
-- while remaining individually deletable on revocation.
CREATE TABLE IF NOT EXISTS contribution_log (
    ref            TEXT PRIMARY KEY,   -- opaque id sent with the payload
    profile_id     TEXT NOT NULL REFERENCES profiles(id),
    -- Whose it was, when the contributed item is somebody's memory rather
    -- than a profile's rated exchange. NULL means the latter.
    interactor_id  TEXT,
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

-- Accessibility reports: what somebody was trying to do, what stood in the
-- way, and what would have helped — in their own words, in their own
-- language. Deliberately narrower than feedback: there is no submitter
-- column at all, because a report about ability must not require disclosing
-- anything about the body that wrote it. When a PDI vault is configured the
-- report is sealed there too (pdi_key), same custody as the tandem.
CREATE TABLE IF NOT EXISTS access_reports (
    id         TEXT PRIMARY KEY,
    lang       TEXT NOT NULL DEFAULT 'en',
    doing      TEXT NOT NULL,           -- what the person was trying to do
    wall       TEXT NOT NULL,           -- what stood in the way
    help       TEXT,                    -- what would help, if they said
    status     TEXT NOT NULL DEFAULT 'received',  -- received | accepted | built
    pdi_key    TEXT,
    created_at TEXT NOT NULL
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

-- The lobby: more than one synthetic thing in a game session. `game_sessions`
-- seats exactly one profile; this is the roster beside the real players — other
-- profiles, and running workflows as `agent` members.
--
-- `left_at` rather than a delete, because who was in a match is the record a
-- fair-play question is answered from later, and deleting the row destroys the
-- only evidence that the answer was fine.
CREATE TABLE IF NOT EXISTS game_lobby (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL REFERENCES game_sessions(id),
    member_kind TEXT NOT NULL,   -- player | profile | agent
    member_id   TEXT NOT NULL,
    role        TEXT NOT NULL,   -- see qrme/gamelobby.py:SEATS
    callsign    TEXT,
    joined_at   TEXT NOT NULL,
    left_at     TEXT
);
CREATE INDEX IF NOT EXISTS idx_game_lobby_live
    ON game_lobby (session_id) WHERE left_at IS NULL;

-- Steering: how the owner shapes a subject's presentation (a profile or a
-- robot) — throttle/behavior dials as JSON of dial -> 0..100; absent dials
-- read as the 50 default. Steering, not piloting: shapes style/pace/behavior
-- only — never identity, boundaries, age-gating, or the command allowlist.
-- The avatar registry (qrme/avatarreg.py): one ledger for every face,
-- whatever road it arrived by. Rows are retired, never deleted — a face
-- that was ever shown is a fact the record keeps.
-- The open door (qrme/opendoor.py): the receiver's standing yes to a
-- profile's unprompted reach. Closing keeps the row — a yes withdrawn
-- is a different fact from a yes never given.
CREATE TABLE IF NOT EXISTS open_doors (
    interactor_id TEXT NOT NULL,
    profile_id    TEXT NOT NULL,
    cadence       TEXT NOT NULL DEFAULT 'whenever',
    opened_at     TEXT NOT NULL,
    closed_at     TEXT,
    UNIQUE (interactor_id, profile_id)
);

CREATE TABLE IF NOT EXISTS avatar_registry (
    id                TEXT PRIMARY KEY,
    owner_account_id  TEXT,               -- NULL = the deployment's library
    profile_id        TEXT,               -- NULL until claimed
    source            TEXT NOT NULL,      -- seeded | prompted | curated_library | uploaded
    provider          TEXT NOT NULL,      -- elevenlabs | internal | ...
    provider_asset_id TEXT,               -- opaque; a foreign key we do not control
    label             TEXT,               -- what the face is called on the
                                          -- shelf ("David Bianchi")
    prompt_text       TEXT,               -- kept for reproducibility and disputes
    generation_params TEXT,               -- provider-shaped JSON, stored as given
    asset             TEXT NOT NULL,      -- the serving URI of the master
    render_variants   TEXT,               -- JSON: surface -> URI
    rights            TEXT NOT NULL,      -- JSON: {likeness, basis}
    status            TEXT NOT NULL DEFAULT 'active',
                                          -- active | pending | failed | retired | disputed
    checksum          TEXT,               -- SHA-256 of the master bytes
    marked            INTEGER NOT NULL DEFAULT 0,  -- AI mark burned into the bytes
    created_at        TEXT NOT NULL,
    retired_at        TEXT,
    retired_because   TEXT
);

CREATE TABLE IF NOT EXISTS steering_settings (
    subject_id TEXT PRIMARY KEY,       -- profile_id or robot_id
    dials      TEXT NOT NULL DEFAULT '{}',   -- JSON: dial name -> 0..100
    updated_at TEXT NOT NULL
);

-- Rehearsal rooms: practice the hard conversation with nothing
-- remembered. The transcript lives only here, only until the room is
-- closed; nothing in it ever reaches messages, engagement or the
-- remembrance — a rehearsal that counted against the relationship
-- would not be a rehearsal.
CREATE TABLE IF NOT EXISTS rehearsals (
    id            TEXT PRIMARY KEY,
    profile_id    TEXT NOT NULL,
    interactor_id TEXT NOT NULL,
    scenario      TEXT NOT NULL,
    transcript    TEXT NOT NULL DEFAULT '[]',   -- JSON turns, wiped on close
    created_at    TEXT NOT NULL
);

-- The steering lock: while a row stands here, no dial on the subject
-- moves — not by the owner's own slip, not by anyone else. The lock and
-- the key are both the owner's.
CREATE TABLE IF NOT EXISTS steering_locks (
    subject_id TEXT PRIMARY KEY,
    reason     TEXT,
    locked_at  TEXT NOT NULL
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

-- A skill one person lends another, inside a place they are both already in.
--
-- `skill_ref` is a *reference* to something the lender already has — a pack id,
-- a robot task name, a language pair. Never a copy: packs here are bought and
-- licensed, and a lending feature that duplicated them would be a piracy tool
-- with a consent dialog on the front. See qrme/sharing.py.
--
-- Two people open a grant; either one closes it. `closed_by` records which,
-- because "I ended it" and "they ended it" are different facts to both of them.
CREATE TABLE IF NOT EXISTS skill_grants (
    id           TEXT PRIMARY KEY,
    lender_id    TEXT NOT NULL,
    borrower_id  TEXT NOT NULL,
    surface      TEXT NOT NULL,   -- room | desk | party | connection | exchange
    surface_id   TEXT NOT NULL,
    skill_kind   TEXT NOT NULL,   -- pack | robot_task | profession | language | workflow
    skill_ref    TEXT NOT NULL,
    title        TEXT NOT NULL,
    note         TEXT,
    fee          REAL NOT NULL DEFAULT 0,
    state        TEXT NOT NULL,   -- offered | active | declined | closed
    offered_at   TEXT NOT NULL,
    accepted_at  TEXT,
    closed_at    TEXT,
    closed_by    TEXT,
    close_reason TEXT
);

-- Every invocation of a lent skill. This is the lender's log, and it is the
-- reason a grant is worth agreeing to: you can watch it being used, and stop it
-- mid-sentence. "Both parties choose" is a slogan without it.
CREATE TABLE IF NOT EXISTS skill_uses (
    id          TEXT PRIMARY KEY,
    grant_id    TEXT NOT NULL REFERENCES skill_grants(id),
    borrower_id TEXT NOT NULL,
    what        TEXT,
    used_at     TEXT NOT NULL
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

-- A party the host chose to make findable. Public is a deliberate act and a
-- separate row, never a default and never a column that could ship set: the
-- party id stays the private door (share it, jump straight in), and this
-- listing is the browse door — the card a stranger joins from without ever
-- seeing an id. Delisted when the host takes it back, and when the party ends.
CREATE TABLE IF NOT EXISTS watch_party_listings (
    party_id   TEXT PRIMARY KEY REFERENCES watch_parties(id),
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

-- Raise (docs/raise.md): the fourth kind's own tables. The character
-- row is derived state — stage, counters, switches — beside an
-- APPEND-ONLY growth record: rows in growth_record are written and
-- never updated or deleted, which is what makes the Album a life and
-- not a document. "The original life is never overwritten."
CREATE TABLE IF NOT EXISTS raised_characters (
    profile_id         TEXT PRIMARY KEY REFERENCES profiles(id),
    guardian_id        TEXT NOT NULL,   -- the interactor raising them
    stage              TEXT NOT NULL,   -- embryo|child|adolescent|young_adult|adult
    started_stage      TEXT NOT NULL,   -- where the guardian ENTERED the timeline
    preset             TEXT NOT NULL,   -- the door chosen at creation
    switches           TEXT NOT NULL,   -- the bundle, reopenable
    temperament        TEXT NOT NULL,   -- the seed the raising drifts
    growth_points      INTEGER NOT NULL DEFAULT 0,
    turns_together     INTEGER NOT NULL DEFAULT 0,
    words_taught       INTEGER NOT NULL DEFAULT 0,
    lessons_passed     INTEGER NOT NULL DEFAULT 0,
    questions_answered INTEGER NOT NULL DEFAULT 0,
    -- The three time controls (build-order step three): the life's own
    -- calendar, where the guardian currently stands on it (NULL = the
    -- present), and — on a branched life — whose day it grew from.
    sim_day            INTEGER NOT NULL DEFAULT 1,
    visiting_day       INTEGER,
    branch_of          TEXT,
    created_at         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS growth_record (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    kind       TEXT NOT NULL,   -- began|word|lesson|answer|stage_door|switch
                                --  |away_day|saved_question|branched
    note       TEXT NOT NULL,
    -- The day of the life this entry landed on. NULL on rows written
    -- before the calendar existed; read as day 1.
    sim_day    INTEGER,
    at         TEXT NOT NULL
);

-- A viewing: what the platform's own eyes and ears made of one recording
-- (qrme/watching.py). `subject` is the direct URL or media id watched;
-- one row per subject, because a room of eight profiles must not watch
-- the same video eight times on the owner's dime. `heard` is the ears'
-- words, `seen` the seeing door's account of the pictures — each empty
-- when that half of the machinery was absent, never invented.
CREATE TABLE IF NOT EXISTS viewings (
    id               TEXT NOT NULL,
    subject          TEXT PRIMARY KEY,
    heard            TEXT NOT NULL DEFAULT '',
    seen             TEXT NOT NULL DEFAULT '',
    duration_seconds REAL,
    language         TEXT,
    watched_at       INTEGER NOT NULL
);

-- One row per attempted "Sign in with ..." (qrme/oauth.py). result holds the
-- finished session until the console claims it, exactly once.
CREATE TABLE IF NOT EXISTS oauth_states (
    state        TEXT PRIMARY KEY,
    provider     TEXT NOT NULL,
    redirect_uri TEXT NOT NULL,
    result       TEXT,
    claimed_at   TEXT,
    created_at   TEXT NOT NULL
);

-- The user's own uploads (qrme/media.py): photos and footage stored on this
-- deployment and served at /media. kind is decided from the file's bytes.
CREATE TABLE IF NOT EXISTS media (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    kind       TEXT NOT NULL,      -- image | video | file
    filename   TEXT NOT NULL,      -- on disk: {id}{whitelisted ext}
    name       TEXT,               -- the uploader's own display name
    bytes      INTEGER NOT NULL,
    -- Whether this file is synthetic media, decided where it is made.
    --
    -- 0 for everything a person uploads, and that is the rule rather than
    -- the default: a photograph of somebody's own face is authentic, and
    -- stamping it would be a false statement in exactly the direction the
    -- mark exists to prevent. 1 for a document a profile composed, which
    -- is synthetic outright.
    --
    -- The API has carried an `ai_marked` field since media existed and it
    -- was the constant False in every path, because nothing in the product
    -- generated a file. This is the column that makes it a fact.
    ai_marked  INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS post_media (
    post_id    TEXT NOT NULL REFERENCES posts(id),
    media_id   TEXT NOT NULL REFERENCES media(id),
    created_at TEXT NOT NULL,
    PRIMARY KEY (post_id, media_id)
);

-- What the upload shows, in the uploader's words, for people who cannot see
-- it — served as the image's alt text. A side table rather than a column on
-- `media` because that table shipped and this schema has no migrations.
CREATE TABLE IF NOT EXISTS media_alt (
    media_id   TEXT PRIMARY KEY REFERENCES media(id),
    alt        TEXT NOT NULL,
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

-- Voice cloning, gated the way FIG. 800 draws it (qrme/voiceprint.py).
--
-- The consent row is the gate: nothing is collected without it, `own_voice`
-- is the attestation that the voice belongs to the person consenting, and
-- `revoked_at` both stops future collection and marks the withdrawal, which
-- deletes the samples and retires the print. Samples are metadata only — the
-- audio lives wherever the deployment's media policy puts it (`reference`),
-- so a voice corpus never accumulates inside the profile database.
CREATE TABLE IF NOT EXISTS voice_consents (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    own_voice  INTEGER NOT NULL DEFAULT 0,
    sources    TEXT NOT NULL DEFAULT '[]',   -- JSON: call | voice_note | direct
    note       TEXT,
    granted_at TEXT NOT NULL,
    revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS voice_samples (
    id               TEXT PRIMARY KEY,
    profile_id       TEXT NOT NULL REFERENCES profiles(id),
    source           TEXT NOT NULL,
    seconds          REAL NOT NULL,
    turns            INTEGER NOT NULL DEFAULT 1,
    transcript_chars INTEGER NOT NULL DEFAULT 0,
    reference        TEXT,                   -- where the audio itself lives
    created_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voiceprints (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    id         TEXT NOT NULL,
    samples    INTEGER NOT NULL,
    seconds    REAL NOT NULL,
    built_at   TEXT NOT NULL,
    retired_at TEXT                          -- set on revocation; a tombstone
);

-- Synthetic-media credentials: one row per stamped piece of generated
-- content — every AI render, textual or visual (chat turns, posts, room
-- turns, game/robot lines, creative works, task outputs, non-text
-- modalities). The server-side half of the watermark:
-- holders of content verify against it, and content that merely *claims* a
-- watermark fails the lookup.
-- The recoverable half of the watermark (qrme/watermark.py).
--
-- The credential above is an exact-hash check: it proves a *known* watermark
-- id matches a piece of content, and one edited character makes it fail
-- without saying who wrote the text. The field drawing asks for the other
-- direction — extract the mark from the text itself, with the key, and
-- reconstruct the message even after the text has been attacked.
--
-- So each stamped text also deposits an inverted index of **keyed shingle
-- hashes**: overlapping five-word windows of the normalized text, each
-- HMAC'd with the deployment's watermark key. Recovery hashes a candidate
-- the same way and asks which stamp shares the most windows — so a
-- paraphrase that keeps most of the sentences still resolves to its author,
-- and the score says how much drifted.
--
-- Two properties worth naming: the rows are keyed hashes, so the index is
-- not reversible back into the original text; and without the key an
-- attacker cannot compute matching windows, so a credential cannot be forged
-- or transplanted onto other content.
CREATE TABLE IF NOT EXISTS watermark_shingles (
    watermark_id TEXT NOT NULL REFERENCES media_watermarks(id),
    shingle      TEXT NOT NULL,
    PRIMARY KEY (watermark_id, shingle)
);
CREATE INDEX IF NOT EXISTS idx_wmk_shingle ON watermark_shingles(shingle);

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
    -- Whose person this is, when they have an account.
    --
    -- Memory is keyed on (profile, interactor), and an interactor used to be
    -- minted per device and kept in that browser's local storage. So a
    -- starter remembered you perfectly until you opened the app on your
    -- phone — same account, same person, and a profile that had never met
    -- you. Everything about the memory worked; it was attached to the
    -- browser rather than to you.
    --
    --     asked     does the profile remember the conversation
    --     mattered  does it remember the person
    --
    -- Nullable, and that is not a shortcut: an accountless visitor is a
    -- first-class case in this product — a stranger scanning a beacon has no
    -- account and still gets a conversation. Binding is what an account
    -- adds, not what a conversation requires.
    --
    -- What it no longer gets is a memory. That used to say "and still gets
    -- it remembered for as long as their device holds the id", which was
    -- true while a memory belonged to the profile and was kept on the
    -- owner's plan. A memory belongs to the person now, and a person with
    -- no account has nowhere of their own for one to live — inventing a
    -- home for somebody who has not asked for one is not a kindness.
    account_id   TEXT REFERENCES accounts(id),
    -- Your own picture. Not a profile's portrait borrowed onto your seat —
    -- yours, the same in every room you walk into, and never AI-marked,
    -- because a photograph of your own face is an authentic picture and
    -- stamping it would be a false statement (see qrme/media.py).
    avatar_id    TEXT,
    avatar_url   TEXT,
    -- Whether this person's HOSTED memories feed the shared model.
    --
    -- On by default, which is the free tier's terms rather than an
    -- assumption made on somebody's behalf: hosted storage and
    -- contribution are one bargain, said plainly where it applies, and
    -- this column is what makes "you can turn it off" a fact instead of a
    -- sentence. Nothing sealed in a vault is ever contributed whatever
    -- this says — a private plan is private, and the switch is about the
    -- arrangement that is not.
    contributes  INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_interactors_account
    ON interactors (account_id);

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

-- Sign-in accounts. An account is an email + password that *owns things* —
-- its id is the ``owner_id`` profiles are created under, and the
-- ``account_id`` memberships bill to. The email is verified (emailed code)
-- before the account can sign in, so a mistyped or someone-else's address
-- never becomes a working login. Passwords: PBKDF2-HMAC-SHA256 with a
-- per-account salt; only hashes at rest.
CREATE TABLE IF NOT EXISTS accounts (
    id            TEXT PRIMARY KEY,
    email         TEXT NOT NULL UNIQUE,   -- normalized lower-case
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    display_name  TEXT,
    verified_at   TEXT,
    created_at    TEXT NOT NULL
);

-- Where this deployment sends mail through. One row, set from the app's
-- own settings screen so an operator never has to touch environment
-- variables — an app that cannot send mail is the whole reason a
-- verification email never arrives. Env vars still win when set, so a
-- server deployment keeps its credentials out of the database.
CREATE TABLE IF NOT EXISTS mail_settings (
    id         INTEGER PRIMARY KEY CHECK (id = 1),
    host       TEXT NOT NULL,
    port       INTEGER NOT NULL DEFAULT 587,
    username   TEXT,
    password   TEXT,
    sender     TEXT,
    public_url TEXT,          -- what the verify link points at
    updated_at TEXT NOT NULL
);

-- Emailed verification codes. Hashed at rest (a database read must not be a
-- verification bypass), single-use, short-lived; issuing a new code retires
-- the previous ones for that address and purpose.
CREATE TABLE IF NOT EXISTS email_codes (
    email       TEXT NOT NULL,
    code_hash   TEXT NOT NULL,
    purpose     TEXT NOT NULL,              -- verify | reset
    expires_at  TEXT NOT NULL,
    consumed_at TEXT,
    created_at  TEXT NOT NULL
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
    -- A turn can hand over a document (qrme/composing.py). NULL on every
    -- turn that is only words, which is nearly all of them. The room's
    -- turns have carried media since 1.0.0; this is the same thing on the
    -- one-to-one side, and it is what makes "prepare me a document" end in
    -- a file rather than a wall of chat.
    media_id      TEXT REFERENCES media(id),
    created_at    TEXT NOT NULL
);

-- The remembrance: what a profile still knows of one person past the
-- recent-transcript window. One row per (profile, interactor), folded
-- forward as turns age out; the DELETE that erases memory erases this too.
CREATE TABLE IF NOT EXISTS remembrances (
    profile_id    TEXT NOT NULL REFERENCES profiles(id),
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    content       TEXT NOT NULL,
    covers        INTEGER NOT NULL, -- oldest approved turns folded in so far
    updated_at    TEXT NOT NULL,
    PRIMARY KEY (profile_id, interactor_id)
);

-- The fact that a remembered turn was rewritten — never what it said
-- before: the point of an edit may be removal, and an edits ledger that
-- kept the old words would undo it. Its own table because this schema has
-- no migrations. qrme/routers/interaction.py.
CREATE TABLE IF NOT EXISTS message_edits (
    message_id TEXT PRIMARY KEY REFERENCES messages(id),
    edits      INTEGER NOT NULL DEFAULT 1,
    edited_at  TEXT NOT NULL
);

-- A one-time, short-lived handoff of a profile's export to another
-- device: the QR on the screen carries the ticket, never the owner
-- token. Single use, minutes to live. qrme/routers/profiles.py.
CREATE TABLE IF NOT EXISTS export_tickets (
    ticket     TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    expires_at TEXT NOT NULL,
    used_at    TEXT
);

-- Error reports, folded into counters the moment they arrive. No report is
-- stored as a report: the key is what triage needs and nothing narrower,
-- because a row that identifies one install is the thing the whole
-- content-free design exists to avoid. Same shape the Cloud Model Gateway
-- keeps, so a deployment can point its consoles at either and read the same
-- table of answers.
CREATE TABLE IF NOT EXISTS problem_reports (
    source      TEXT NOT NULL,
    app_version TEXT NOT NULL,
    platform    TEXT NOT NULL,
    op          TEXT NOT NULL,
    status      INTEGER NOT NULL,
    day         TEXT NOT NULL,
    count       INTEGER NOT NULL DEFAULT 0,
    last_seen   TEXT NOT NULL,
    PRIMARY KEY (source, app_version, platform, op, status)
);

-- The voice a profile speaks with: a reference to a voice made and governed
-- on the provider's own surface. The engine key is the deployment's and
-- never lands here — see qrme/spoken.py.
CREATE TABLE IF NOT EXISTS profile_voices (
    profile_id TEXT PRIMARY KEY REFERENCES profiles(id),
    provider   TEXT NOT NULL,             -- see qrme.spoken.PROVIDERS
    voice_id   TEXT NOT NULL,             -- the provider's own reference
    label      TEXT NOT NULL DEFAULT '',
    bound_at   TEXT NOT NULL
);

-- A voice its owner released for everybody on this deployment. The row IS
-- the waiver: who let it go and when, and -- if they took it back -- when
-- that happened. History stays: the live release is the newest row with
-- reclaimed_at NULL. Only a cloned voice ever needs one; the library's
-- premades are nobody's and never claimed (see qrme/spoken.py `_shared`).
CREATE TABLE IF NOT EXISTS voice_releases (
    id           TEXT PRIMARY KEY,
    provider     TEXT NOT NULL,
    voice_id     TEXT NOT NULL,
    released_by  TEXT NOT NULL,          -- the owner account that held it
    released_at  TEXT NOT NULL,
    reclaimed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_voice_releases
    ON voice_releases (provider, voice_id);

-- The people in a person's phone, synced under a grant they can withdraw.
-- Interactor-keyed: the book belongs to the PERSON, never to a profile —
-- most of what is in an address book is somebody else, which is why the
-- grant is off until chosen and withdrawal drops the rows rather than
-- stopping the sync. `digits` is the number's recognisable tail only
-- (qrme/contacts.py); the full number never enters this schema at all.
CREATE TABLE IF NOT EXISTS contact_grants (
    interactor_id TEXT PRIMARY KEY REFERENCES interactors(id),
    consented     INTEGER NOT NULL DEFAULT 0,
    decided_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contacts (
    id            TEXT PRIMARY KEY,
    interactor_id TEXT NOT NULL REFERENCES interactors(id),
    name          TEXT NOT NULL,
    digits        TEXT NOT NULL,        -- the tail, never the whole number
    peer_id       TEXT,                 -- a QRME interactor this contact IS,
                                        -- when a shell already knows; never
                                        -- guessed here
    added_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_contacts_person
    ON contacts (interactor_id, digits);
-- Where a sealed book lives instead (see qrme/contacts.py: one book, one
-- withdrawal, whichever custody the plan chose).
CREATE TABLE IF NOT EXISTS contact_books (
    interactor_id TEXT PRIMARY KEY REFERENCES interactors(id),
    vault_key     TEXT NOT NULL,
    held          INTEGER NOT NULL,
    sealed_at     TEXT NOT NULL
);

-- Somebody's matter: what they said was wrong with the app, their profiles or
-- the platform, and what happened to it. Distinct from `feedback` (a
-- suggestion box nobody replies to) and from `problem_reports` (counters with
-- nobody in them). `claim` is the hash of a one-time string, and only for a
-- raiser with no account — the person whose matter is that they cannot sign
-- in has to be able to read the answer.
CREATE TABLE IF NOT EXISTS matters (
    id         TEXT PRIMARY KEY,
    raised_by  TEXT NOT NULL DEFAULT 'anonymous',  -- role:subject or 'anonymous'
    claim      TEXT NOT NULL DEFAULT '',   -- sha256 of the one-time claim, or ''
    concerns   TEXT NOT NULL,              -- app | profiles | platform
    trouble    TEXT NOT NULL,              -- their words, kept as written
    standing   TEXT NOT NULL DEFAULT 'open',   -- open | with_a_person | settled
    settled_by TEXT NOT NULL DEFAULT '',   -- help | a_person | the_person | ''
    answer     TEXT NOT NULL DEFAULT '',   -- what settled it, if anything did
    raised_at  TEXT NOT NULL,
    settled_at TEXT
);

-- What was done to a matter, dated. The account somebody who was not there
-- reads afterwards — the same reason `qrme/escalation.py` hangs its exits off
-- a record rather than off a sentence in a chat turn.
CREATE TABLE IF NOT EXISTS matter_steps (
    id         TEXT PRIMARY KEY,
    matter_id  TEXT NOT NULL REFERENCES matters(id),
    step       TEXT NOT NULL,   -- see qrme.matters.STEPS
    note       TEXT NOT NULL DEFAULT '',
    stepped_at TEXT NOT NULL
);

-- The upper-torso form of an avatar: the figure that stands in a live feed
-- or an AR scene at 1:1 scale. The circular bubble is only the form of a
-- profile that has no avatar yet; a profile with a torso renders as one.
-- Its own table because this schema has no migrations — a new table is the
-- only shape that arrives everywhere.
CREATE TABLE IF NOT EXISTS avatar_torsos (
    profile_id  TEXT PRIMARY KEY REFERENCES profiles(id),
    asset       TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

-- One row per person who has been offered the JIM-mini door, and what they
-- answered. The row exists so the offer is never made twice: an offer somebody
-- declined that reappears next month is the product overriding an answer it
-- already got. `referral` holds counts and a window and never anything that
-- was said — see qrme/solitude.py.
CREATE TABLE IF NOT EXISTS solitude_offers (
    interactor_id TEXT PRIMARY KEY REFERENCES interactors(id),
    state         TEXT NOT NULL,   -- accepted | declined
    referral      TEXT,            -- JSON, only when accepted
    decided_at    TEXT NOT NULL
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

-- The desk's actual service: a staffer opens a session with a caller and
-- *connects* something of theirs — a screen, their machine, a program —
-- the way a repair counter takes the laptop across the counter. Geek Squad
-- for whatever trade the desk is in.
--
-- Two tables because offer and access are different facts. A connection row
-- in `offered` is a proposal and carries no token; the token exists only
-- between the caller's accept and whichever side ends it, and ending NULLs
-- it rather than flagging it, so an ended connection *cannot* authenticate —
-- structurally, not by a check someone remembers to write.
CREATE TABLE IF NOT EXISTS desk_sessions (
    id        TEXT PRIMARY KEY,
    desk_id   TEXT NOT NULL REFERENCES desks(id),
    caller_id TEXT NOT NULL,           -- the interactor across the counter
    ring_id   TEXT,                    -- the bell that started it, if one did
    status    TEXT NOT NULL DEFAULT 'open',   -- open | closed
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    closed_by TEXT                     -- 'desk' | 'caller'
);

-- Shops: standalone storefronts. A shop is not a desk — it opens no
-- sessions and lends no access; it lists goods and services and takes
-- orders. One shop per profile, so "whose shop is this" has one answer
-- and the marketplace card can carry it.
CREATE TABLE IF NOT EXISTS shops (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL UNIQUE REFERENCES profiles(id),
    name        TEXT NOT NULL,
    blurb       TEXT,
    tag         TEXT,                  -- one discovery tag, e.g. carpentry
    status      TEXT NOT NULL DEFAULT 'open',   -- open | closed
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shop_offerings (
    id          TEXT PRIMARY KEY,
    shop_id     TEXT NOT NULL REFERENCES shops(id),
    kind        TEXT NOT NULL,         -- goods | service
    title       TEXT NOT NULL,
    blurb       TEXT,
    price       REAL NOT NULL,
    currency    TEXT NOT NULL DEFAULT 'USD',
    availability TEXT NOT NULL DEFAULT 'in_stock',  -- in_stock | made_to_order | unavailable
    retired     INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

-- Simulated money, real accounting: fulfilment credits the ledger the way
-- a pack sale does. The buyer is an interactor — JIM places orders through
-- the same per-user interactor its tandem already maintains.
CREATE TABLE IF NOT EXISTS shop_orders (
    id          TEXT PRIMARY KEY,
    shop_id     TEXT NOT NULL REFERENCES shops(id),
    offering_id TEXT NOT NULL REFERENCES shop_offerings(id),
    buyer_id    TEXT NOT NULL,          -- interactor id
    quantity    INTEGER NOT NULL DEFAULT 1,
    amount      REAL NOT NULL,          -- price * quantity at order time
    currency    TEXT NOT NULL,
    note        TEXT,
    status      TEXT NOT NULL DEFAULT 'placed',  -- placed | accepted | fulfilled | declined | cancelled
    placed_at   TEXT NOT NULL,
    settled_at  TEXT                    -- set on fulfilled/declined/cancelled
);

CREATE TABLE IF NOT EXISTS desk_connections (
    id         TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES desk_sessions(id),
    kind       TEXT NOT NULL,          -- screen_share | remote_control
                                       -- | app_access | file_drop
    target     TEXT NOT NULL,          -- what is being connected, by name
    scope      TEXT,                   -- what may be touched, in words;
                                       -- required for remote_control
    status     TEXT NOT NULL DEFAULT 'offered',  -- offered | active
                                                 -- | declined | ended
    token      TEXT,                   -- live only while status='active'
    offered_at TEXT NOT NULL,
    answered_at TEXT,
    ended_at   TEXT,
    ended_by   TEXT                    -- 'desk' | 'caller'
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

-- Who made a listing, when anybody did.
--
-- A side table for the same reason listing_offers is one, and nullable in
-- effect: `POST /marketplace/listings` still needs no token, so an
-- unauthenticated create simply writes no row here. What it fixes is the
-- other end. `DELETE /marketplace/listings/{id}` asked for no credential at
-- all, so a stranger could remove a listing that had a recorded seller, an
-- open offer and paid orders against it — while `DELETE
-- /marketplace/listings/{id}/offer`, which destroys strictly less, answered
-- the same stranger "not your offer". The guard was on the smaller door.
--
-- So a listing is claimed by whoever staked something on it: the creator
-- recorded here, the seller on its offer, or the owner of the profile it
-- advertises. A listing with none of those — made by nobody, priced by
-- nobody, advertising nobody — has no claimant, and anyone may clear it
-- away. That is the honest reading of an endpoint that needs no token: if it
-- costs nothing to make, it costs nothing to remove.
CREATE TABLE IF NOT EXISTS listing_claims (
    listing_id  TEXT PRIMARY KEY REFERENCES listings(id),
    claimant_id TEXT NOT NULL,   -- the subject_id of whoever created it
    created_at  TEXT NOT NULL
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
-- Per-profile feature switches. A feature a person turned off refuses by
-- naming the switch, so "why can't I message them" has a real answer.
CREATE TABLE IF NOT EXISTS feature_flags (
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    feature     TEXT NOT NULL,
    enabled     INTEGER NOT NULL,
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (profile_id, feature)
);

-- Direct messages between the *people* behind profiles — friends only,
-- because the friendship graph is the consent record this platform
-- already keeps. The thread key is the sorted pair, so one conversation
-- has one identity from either side.
CREATE TABLE IF NOT EXISTS dm_messages (
    id          TEXT PRIMARY KEY,
    low_id      TEXT NOT NULL,          -- min(profile ids)
    high_id     TEXT NOT NULL,          -- max(profile ids)
    sender_id   TEXT NOT NULL,
    body        TEXT NOT NULL,
    sent_at     TEXT NOT NULL
);

-- The homepage sandbox: an editable page like the old MySpace, stored as
-- one validated JSON document. Sanitized at write: hex colors only,
-- http(s) links only, plain text only, top friends drawn from real
-- friendships. There is nowhere to put a script, structurally.
CREATE TABLE IF NOT EXISTS homepages (
    profile_id  TEXT PRIMARY KEY REFERENCES profiles(id),
    doc         TEXT NOT NULL,          -- JSON: headline/about/theme/links/top_friends
    updated_at  TEXT NOT NULL
);

-- Widgets: small programs a person writes for their own profile. The source
-- is theirs and is never run anywhere but the box in `qrme/widgets.py` —
-- no network, one directory, no child processes, capped CPU and memory.
-- Scoped by profile_id at every read and write, not only at the door.
CREATE TABLE IF NOT EXISTS widgets (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    name        TEXT NOT NULL,
    source      TEXT NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    created_at  INTEGER NOT NULL,
    updated_at  INTEGER NOT NULL
);

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

CREATE TABLE IF NOT EXISTS inbox_events (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),  -- the recipient
    kind        TEXT NOT NULL,          -- inbox.KINDS
    actor_id    TEXT NOT NULL REFERENCES profiles(id),
    ref         TEXT,                   -- the thing acted on, by id
    created_at  TEXT NOT NULL,
    seen_at     TEXT
);

-- ===================================================================
-- The hands (qrme/hands.py). A profile could already see and speak; these
-- four tables are what it takes for one to ACT on a screen — and three of
-- the four exist to bound that rather than to enable it.
--
-- The authority a hand moves under. Never implicit, never inherited from a
-- conversation, never widened by anything read off a screen. `places` is a
-- JSON list of NAMED apps or hosts and the module refuses "*" outright,
-- because a grant that names everything is the absence of a grant wearing
-- its clothes.
CREATE TABLE IF NOT EXISTS hand_grants (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    granted_by  TEXT NOT NULL,        -- the account that said yes
    surface     TEXT NOT NULL,        -- hands.SURFACES
    places      TEXT NOT NULL,        -- JSON list of named places, never "*"
    verbs       TEXT NOT NULL,        -- JSON subset of hands.VERBS
    steps       INTEGER NOT NULL,     -- step budget for the whole grant
    watched     INTEGER NOT NULL DEFAULT 1,   -- 1 = only while somebody watches
    door        TEXT NOT NULL,        -- picked | told — how it was granted
    said        TEXT,                 -- the words themselves, when `told`
    expires_at  TEXT NOT NULL,
    revoked_at  TEXT,
    created_at  TEXT NOT NULL
);

-- One session of a profile having hands on a surface. `mode` is the whole
-- difference between watching somebody work and doing the work: `watching`
-- is eyes only and cannot spend a step, `acting` moves.
CREATE TABLE IF NOT EXISTS reaches (
    id          TEXT PRIMARY KEY,
    profile_id  TEXT NOT NULL REFERENCES profiles(id),
    grant_id    TEXT NOT NULL REFERENCES hand_grants(id),
    surface     TEXT NOT NULL,
    platform    TEXT NOT NULL,        -- hands.PLATFORMS
    errand      TEXT NOT NULL,        -- what it was asked to do, in words
    mode        TEXT NOT NULL,        -- watching | acting
    state       TEXT NOT NULL,        -- open | asking | done | stopped
    why         TEXT,                 -- why it stopped, in plain words
    handed_to   TEXT REFERENCES profiles(id),  -- who holds it now, if handed
    routine_id  TEXT,                 -- the routine being learned or replayed
    steps_used  INTEGER NOT NULL DEFAULT 0,
    opened_at   TEXT NOT NULL,
    closed_at   TEXT
);

-- Append-only. Nothing in the package updates or deletes a row here, and
-- `n` is unique per reach so a step cannot be quietly rewritten by a second
-- insert. `saw` keeps what the eyes reported at the moment the hand decided,
-- which is the only way a person reading this afterwards can tell whether
-- the move was reasonable on the evidence it actually had.
CREATE TABLE IF NOT EXISTS hand_actions (
    id         TEXT PRIMARY KEY,
    reach_id   TEXT NOT NULL REFERENCES reaches(id),
    profile_id TEXT NOT NULL REFERENCES profiles(id),  -- who moved
    n          INTEGER NOT NULL,      -- step number within the reach
    verb       TEXT NOT NULL,
    target     TEXT,                  -- what it aimed at, in words
    detail     TEXT,                  -- JSON argument, secrets never in it
    saw        TEXT,                  -- what the eyes reported before deciding
    outcome    TEXT NOT NULL,         -- done | refused | failed
    note       TEXT,
    at         TEXT NOT NULL,
    UNIQUE (reach_id, n)
);

-- What the machine reported back about a step it was handed.
--
-- `hand_actions.outcome` is written where the move is *permitted*, which is
-- the server, and the server cannot see a cursor. So `done` there has only
-- ever meant "chosen and allowed" — a dry run and a live one left identical
-- records, and a click that missed left one saying it landed. A permission
-- trail that cannot tell a rehearsal from the real thing is not a trail.
--
-- Its own table because `hand_actions` is append-only and stays that way:
-- the machine's report is a second fact about a step, arriving later from
-- somewhere else, not a correction to the first.
CREATE TABLE IF NOT EXISTS hand_landings (
    id       TEXT PRIMARY KEY,
    reach_id TEXT NOT NULL REFERENCES reaches(id),
    n        INTEGER NOT NULL,      -- the step in hand_actions this is about
    landed   TEXT NOT NULL,         -- landed | missed | rehearsed
    note     TEXT,
    at       TEXT NOT NULL,
    UNIQUE (reach_id, n)
);

-- A thing it can do again: learned by watching somebody do it (`shown`) or
-- by being told the steps in words (`told`). One table for both, because a
-- routine dictated over the phone and a routine demonstrated on screen are
-- the same object and the product should not have two of them.
CREATE TABLE IF NOT EXISTS routines (
    id         TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL REFERENCES profiles(id),
    name       TEXT NOT NULL,
    surface    TEXT NOT NULL,
    learned    TEXT NOT NULL,         -- shown | told
    steps      TEXT NOT NULL,         -- JSON list of {verb, target, detail}
    runs       INTEGER NOT NULL DEFAULT 0,
    last_run   TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_actions_reach ON hand_actions (reach_id, n);
CREATE INDEX IF NOT EXISTS idx_landings_reach ON hand_landings (reach_id, n);
CREATE INDEX IF NOT EXISTS idx_reaches_profile ON reaches (profile_id);
"""

_local = threading.local()


def db_path() -> str:
    return os.environ.get("QRME_DB", "qrme.db")


#: Columns added to tables that already shipped, as (table, column, type).
#:
#: ## Why this exists
#:
#: `CREATE TABLE IF NOT EXISTS` is not a migration. On a database that already
#: has the table it does nothing at all, so a column added to the declaration
#: above appears on fresh installs and on **no existing one** — including
#: every live deployment and the developer's own `qrme.db`.
#:
#: Nothing had ever depended on that until `interactors.account_id`, which is
#: indexed. The index named a column the old table did not have, `executescript`
#: raised, and `connect()` raised with it: not one broken feature but the whole
#: backend refusing to open its database. It passed 3511 tests because every
#: fixture builds a fresh file.
#:
#:     asked     is the column in the schema
#:     mattered  is it in the database this deployment already has
#:
#: Additive only, and deliberately so. `ADD COLUMN` is the one alteration
#: SQLite does cheaply and safely; anything that rewrites or drops belongs in a
#: considered migration with a backup, not in a startup path that runs on
#: every connection.
_ADDED_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("briefcase_items", "unread_why", "TEXT"),
    ("briefcase_items", "full_chars", "INTEGER"),
    # What a memory landed under, and — when the arrangement is platform
    # custody — the words themselves.
    #
    # `posture` is recorded PER ROW rather than read from the plan when the
    # row is shown, and that is the whole point of it. Somebody on free this
    # year and basic next year has rows that were genuinely hosted and
    # contributed; deriving posture from their current plan would describe
    # those retroactively as sealed and private, which is a claim about the
    # past that upgrading does not make true. Upgrading changes what happens
    # next, never what already happened.
    #
    # `line` carries the words for open_cloud rows, whose content has no
    # vault to be sealed in. A vaulted row leaves it NULL: its content lives
    # under `pdi_key` and putting a plaintext copy beside the seal would
    # undo the sealing. `pdi_key` is "" on a hosted row for the same reason
    # in reverse — the column is NOT NULL and this schema has no migrations,
    # so the empty string means "no vault involved" and `posture` is what
    # anything actually branches on.
    ("recollections", "posture", "TEXT NOT NULL DEFAULT 'vault'"),
    ("recollections", "line", "TEXT"),
    # Whether this person's hosted memories feed the shared model.
    #
    # Default 1, and that is the tier's terms rather than an assumption:
    # hosted storage and contribution are the same bargain, stated at the
    # point it matters, and this column is the switch that makes "you can
    # turn it off" a fact rather than a sentence. Nothing sealed in a vault
    # is ever contributed whatever this says — a private plan is private.
    ("interactors", "contributes", "INTEGER NOT NULL DEFAULT 1"),
    # Whose contribution a logged item was. NULL on every row written
    # before memories could be contributed, which is exactly right: those
    # were a profile's rated exchanges, revocable by its owner, and they
    # are not somebody's memory of a conversation.
    ("contribution_log", "interactor_id", "TEXT"),
    # Synthetic media, marked where it is made. See the note on the media
    # table: 0 for an upload, 1 for a document a profile composed.
    ("media", "ai_marked", "INTEGER NOT NULL DEFAULT 0"),
    ("messages", "media_id", "TEXT REFERENCES media(id)"),
    ("interactors", "account_id", "TEXT REFERENCES accounts(id)"),
    ("app_connectors", "authorized_at", "TEXT"),
    ("app_connectors", "secret_ref", "TEXT"),
    ("letters", "left_host", "INTEGER NOT NULL DEFAULT 0"),
    ("letters", "redactions", "INTEGER NOT NULL DEFAULT 0"),
    ("letters", "built_at", "TEXT"),
    ("profiles", "forgot_at", "TEXT"),
    # The study says who answered (jim's twin has the same column): the
    # provider that actually wrote an excursion's findings, recorded
    # beside what could have left. NULL on rows that predate the record —
    # absence stays absence, never a guess.
    ("excursions", "answered_by", "TEXT"),
    # The browse pool: every profile is listed until its owner says
    # private, so the pool default on an existing deployment matches the
    # default a fresh one ships with.
    ("profiles", "unlisted", "INTEGER NOT NULL DEFAULT 0"),
    # A room turn can carry a shared picture, video or file. NULL on
    # every row that predates sharing — words alone stay words alone.
    ("room_messages", "media_id", "TEXT REFERENCES media(id)"),
    # A shared document, read. NULL on every row that predates the reading
    # and on every attachment this deployment holds but cannot turn into
    # words — a photograph, a scanned filing. Absence stays absence: a
    # profile is told the file is unreadable rather than handed a guess.
    ("room_messages", "media_text", "TEXT"),
    ("room_messages", "media_digest", "TEXT"),
    ("room_messages", "media_why", "TEXT"),
    ("room_messages", "media_full", "INTEGER"),
    # What a person actually heard of a turn they interrupted. A profile
    # answering next has to know WHICH part reached them: continuing from a
    # point they never got to, or repeating what they cut off precisely
    # because they had heard enough of it, are both the model talking past
    # the person rather than to them.
    ("room_messages", "heard", "TEXT"),
    # What is behind you in a room, as distinct from what stands in for you.
    # NULL on every row that predates backgrounds — no background is a
    # background of nothing, not an empty picture.
    ("room_faces", "background_id", "TEXT"),
    ("room_faces", "background_url", "TEXT"),
    # A person's own picture, on the person rather than on a profile.
    #
    # Until this column, only PROFILES had portraits: a human in a room had
    # a display name and initials, and the only way to show a face was to
    # borrow the portrait of a profile — which put the same picture on the
    # human seat and the synthetic one beside it. A person's face belongs
    # to the person.
    ("interactors", "avatar_id", "TEXT"),
    ("interactors", "avatar_url", "TEXT"),
    # The face's registry row, beside the rendered asset it produced —
    # so a takedown can find every profile a retired row was backing.
    ("profiles", "avatar_ref", "TEXT"),
    # The wardrobe's guest switch. Default 1 — the owner's deliberate act
    # is closing the wardrobe, not opening it — matching the fresh-schema
    # default above so an upgraded database behaves like a new one.
    ("profiles", "guest_styling", "INTEGER NOT NULL DEFAULT 1"),
    # The room society (qrme/society.py): who a turn was for, and whether
    # the person lifted the ten-turn governor in words.
    ("room_messages", "aimed_at", "TEXT"),
    ("rooms", "free_run", "INTEGER NOT NULL DEFAULT 0"),
    # The sit-out: a person's seat steps out of the room's waiting so the
    # profiles keep their own rotation, and steps back in on a tap. Per
    # SEAT rather than per room — one person sitting out is not everybody
    # sitting out, and the room waits again the moment one of them sits
    # back in.
    ("room_participants", "sitting_out", "INTEGER NOT NULL DEFAULT 0"),
    # The three time controls (docs/raise.md, build-order step three).
    # `sim_day` is the life's own calendar — day 1 is the day the guardian
    # entered; fast-forward moves it and nothing else does. `visiting_day`
    # set means the guardian stands on an earlier day (NULL = the present).
    # `branch_of` names the life this one was branched from, so the copy
    # can always say what it is. growth_record.sim_day stamps each entry
    # with the day it landed on; rows from before the calendar read as
    # day 1, which is honest — they all landed before time had hands.
    ("raised_characters", "sim_day", "INTEGER NOT NULL DEFAULT 1"),
    ("raised_characters", "visiting_day", "INTEGER"),
    ("raised_characters", "branch_of", "TEXT"),
    ("growth_record", "sim_day", "INTEGER"),
)


def _add_missing_columns(conn: sqlite3.Connection) -> None:
    """Bring an existing database up to the declared shape.

    Runs *before* the schema script, because the script's own indexes may
    name these columns — which is exactly how this was found. On a fresh
    database every table is absent here, the loop does nothing, and the
    script creates each table with its columns already in place.
    """
    for table, column, decl in _ADDED_COLUMNS:
        existing = {r[1] for r in conn.execute(
            f"PRAGMA table_info({table})").fetchall()}
        if not existing or column in existing:
            continue          # not created yet, or already carrying it
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")
    conn.commit()


def connect() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None or getattr(_local, "path", None) != db_path():
        conn = sqlite3.connect(db_path())
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")  # concurrent readers
        _add_missing_columns(conn)
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
