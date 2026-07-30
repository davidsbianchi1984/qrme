"""Voice cloning, in the order FIG. 800 draws it.

The figure is a permission gate first and a recorder second:

    802  operator permission to collect and use call information?  — no → end
    804  initialize collection for this user equipment
    806  active call?
    808  collect call information for the active call
    810  analyze it to determine characteristics of the communication
    812  record the voice of the operator from the call, for voice cloning

Read as a specification that is what it is: **nothing is collected before
permission, and the permission is for a named purpose.** So this module makes
the gate load-bearing rather than decorative. Every function that touches
audio checks it, revocation destroys what was gathered, and the readiness of
a clone is a stated number rather than a vibe.

Three rules the product already lives by, applied here:

- **Your own voice.** QRME's premise is a profile built from your own
  likeness; a voiceprint is the same promise in another medium. Enrollment is
  owner-only and requires an explicit attestation that the voice belongs to
  the person consenting. There is no path here for enrolling a stranger, a
  celebrity, or a recording of somebody who never agreed.
- **The mark is not optional.** Synthesized speech leaves carrying a
  watermark credential and a spoken-word disclosure, exactly like every other
  generated medium (qrme/watermark.py). A cloned voice that does not say it is
  one is the thing this whole codebase refuses to build.
- **Revocable, and it means it.** Withdrawing consent deletes the samples and
  retires the print. A tombstone stays so the record of the withdrawal
  survives, which is the opposite of pretending nothing happened.

``analyze`` is step 810 and is deliberately interpretable: sample count,
total seconds, mean turn length, the sources they came from. Enough to say
whether a clone is viable and why, with no opaque score in the middle.
"""

from __future__ import annotations

import json

from . import db, watermark

# How much of somebody's voice it takes before a clone is worth calling one.
# Not a model constraint — a floor so a thin enrollment cannot quietly
# produce a bad impersonation of the person and be labelled ready.
READY_SECONDS = 120.0
READY_SAMPLES = 3

# Where a sample may come from. `call` is FIG. 800's own case; the others are
# the paths QRME already has for a person recording themselves.
SOURCES = ("call", "voice_note", "direct")

DISCLOSURE = ("This voice is synthesized by QRME from a voiceprint its owner "
              "enrolled and can revoke. It is not a recording of them "
              "speaking these words.")


class VoiceError(ValueError):
    """A refusal a caller should read, not a crash."""


# --------------------------------------------------------------------------- #
# 802 / 804 — permission, and only then collection
# --------------------------------------------------------------------------- #

def consent(profile_id: str, *, own_voice: bool, sources: list[str] | None,
            note: str | None = None) -> dict:
    """Step 802: the permission, recorded before anything is collected.

    ``own_voice`` is an attestation, not a checkbox for decoration: without
    it there is no enrollment, because the only voice this system will learn
    is the voice of the person asking it to.
    """
    if not own_voice:
        raise VoiceError(
            "voiceprint enrollment requires attesting the voice is your own — "
            "QRME will not clone a voice on somebody else's behalf")
    picked = sorted(set(sources or ["voice_note"]))
    unknown = [s for s in picked if s not in SOURCES]
    if unknown:
        raise VoiceError(f"unknown voice source(s): {', '.join(unknown)}")

    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "INSERT INTO voice_consents (profile_id, own_voice, sources, note,"
        " granted_at, revoked_at) VALUES (?,1,?,?,?,NULL)"
        " ON CONFLICT(profile_id) DO UPDATE SET own_voice=1, sources=excluded.sources,"
        " note=excluded.note, granted_at=excluded.granted_at, revoked_at=NULL",
        (profile_id, json.dumps(picked), note, now))
    conn.commit()
    return status(profile_id)


def _live_consent(profile_id: str):
    row = db.connect().execute(
        "SELECT * FROM voice_consents WHERE profile_id=? AND revoked_at IS NULL",
        (profile_id,)).fetchone()
    return row


def require_consent(profile_id: str, source: str):
    """The gate every audio path passes through — FIG. 800's 802 → 804 edge."""
    row = _live_consent(profile_id)
    if row is None:
        raise VoiceError(
            "no voice consent on record for this profile — grant it first "
            "(PUT /profiles/{id}/voiceprint/consent)")
    allowed = json.loads(row["sources"])
    if source not in allowed:
        raise VoiceError(
            f"consent covers {', '.join(allowed)} — not {source}. Widen the "
            "consent if that is what you meant")
    return row


# --------------------------------------------------------------------------- #
# 806 / 808 — a sample arrives
# --------------------------------------------------------------------------- #

def collect(profile_id: str, *, source: str, seconds: float,
            turns: int = 1, transcript_chars: int = 0,
            reference: str | None = None) -> dict:
    """Step 808: record that a sample was gathered, and what it contained.

    Deliberately metadata, not audio bytes: QRME stores the *fact and shape*
    of the enrollment locally, and the audio itself belongs wherever the
    deployment's media policy puts it (``reference`` names it). That keeps a
    voice corpus out of the profile database by construction.
    """
    require_consent(profile_id, source)
    if seconds <= 0:
        raise VoiceError("a sample needs a positive duration")
    conn = db.connect()
    sample_id = db.new_id("vsm")
    conn.execute(
        "INSERT INTO voice_samples (id, profile_id, source, seconds, turns,"
        " transcript_chars, reference, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (sample_id, profile_id, source, float(seconds), int(turns),
         int(transcript_chars), reference, db.utcnow()))
    conn.commit()
    return {"id": sample_id, "source": source, "seconds": float(seconds),
            **analyze(profile_id)}


# --------------------------------------------------------------------------- #
# 810 — the characteristics, stated plainly
# --------------------------------------------------------------------------- #

def analyze(profile_id: str) -> dict:
    """Step 810: what the collected material actually amounts to."""
    rows = db.connect().execute(
        "SELECT source, seconds, turns, transcript_chars FROM voice_samples"
        " WHERE profile_id=?", (profile_id,)).fetchall()
    samples = len(rows)
    seconds = round(sum(r["seconds"] for r in rows), 1)
    turns = sum(r["turns"] for r in rows)
    chars = sum(r["transcript_chars"] for r in rows)
    by_source: dict[str, int] = {}
    for r in rows:
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1

    ready = samples >= READY_SAMPLES and seconds >= READY_SECONDS
    missing = []
    if samples < READY_SAMPLES:
        missing.append(f"{READY_SAMPLES - samples} more sample(s)")
    if seconds < READY_SECONDS:
        missing.append(f"{round(READY_SECONDS - seconds, 1)}s more speech")
    return {
        "samples": samples,
        "seconds": seconds,
        "turns": turns,
        "mean_turn_seconds": round(seconds / turns, 2) if turns else None,
        "mean_chars_per_turn": round(chars / turns, 1) if turns and chars else None,
        "by_source": by_source,
        "ready": ready,
        "needs": missing,
        "threshold": {"samples": READY_SAMPLES, "seconds": READY_SECONDS},
        "method": ("counted from the enrolled samples — no opaque score; a "
                   "thin enrollment is called thin rather than labelled ready"),
    }


# --------------------------------------------------------------------------- #
# 812 — the voiceprint, and speaking with it
# --------------------------------------------------------------------------- #

def build(profile_id: str) -> dict:
    """Step 812: mint the voiceprint, once there is enough of the person in
    it to deserve the name."""
    if _live_consent(profile_id) is None:
        raise VoiceError("no voice consent on record for this profile")
    facts = analyze(profile_id)
    if not facts["ready"]:
        raise VoiceError(
            "not enough enrolled voice yet — needs " + ", ".join(facts["needs"]))
    conn = db.connect()
    print_id = db.new_id("vpr")
    conn.execute(
        "INSERT INTO voiceprints (id, profile_id, samples, seconds, built_at,"
        " retired_at) VALUES (?,?,?,?,?,NULL)"
        " ON CONFLICT(profile_id) DO UPDATE SET id=excluded.id,"
        " samples=excluded.samples, seconds=excluded.seconds,"
        " built_at=excluded.built_at, retired_at=NULL",
        (print_id, profile_id, facts["samples"], facts["seconds"], db.utcnow()))
    conn.commit()
    return status(profile_id)


def speak(profile_id: str, text: str) -> dict:
    """Render text in the enrolled voice — as a descriptor plus the mark.

    Synthesis itself belongs to whichever engine the deployment configures;
    what this function guarantees is that nothing leaves without the
    watermark credential and the spoken disclosure attached.
    """
    row = db.connect().execute(
        "SELECT * FROM voiceprints WHERE profile_id=? AND retired_at IS NULL",
        (profile_id,)).fetchone()
    if row is None:
        raise VoiceError("no voiceprint for this profile — build one first")
    if not (text or "").strip():
        raise VoiceError("nothing to say")
    return {
        "type": "voice",
        "voiceprint_id": row["id"],
        "basis": (f"cloned from {row['samples']} consented sample(s), "
                  f"{row['seconds']}s of the owner's own voice"),
        "disclosure": DISCLOSURE,
        "watermark": watermark.stamp(profile_id, "voice", text),
        "revocable": True,
    }


def revoke(profile_id: str, why: str = "withdrawn") -> dict:
    """Withdraw consent: the samples go, the print retires, the record of the
    withdrawal stays."""
    conn = db.connect()
    now = db.utcnow()
    deleted = conn.execute("DELETE FROM voice_samples WHERE profile_id=?",
                           (profile_id,)).rowcount
    conn.execute("UPDATE voiceprints SET retired_at=? WHERE profile_id=?"
                 " AND retired_at IS NULL", (now, profile_id))
    conn.execute("UPDATE voice_consents SET revoked_at=?, note=? WHERE"
                 " profile_id=?", (now, why, profile_id))
    conn.commit()
    return {"revoked": True, "samples_deleted": deleted,
            "voiceprint": "retired",
            "note": "consent withdrawn; the samples are gone and the print "
                    "will not speak again. The withdrawal itself is on record"}


def status(profile_id: str) -> dict:
    con = _live_consent(profile_id)
    row = db.connect().execute(
        "SELECT * FROM voiceprints WHERE profile_id=?", (profile_id,)).fetchone()
    return {
        "consent": ({"granted": True, "own_voice": True,
                     "sources": json.loads(con["sources"]),
                     "granted_at": con["granted_at"]} if con else
                    {"granted": False,
                     "note": "nothing is collected without this"}),
        "enrollment": analyze(profile_id) if con else None,
        "voiceprint": ({"id": row["id"], "built_at": row["built_at"],
                        "retired_at": row["retired_at"],
                        "active": row["retired_at"] is None}
                       if row else None),
        "disclosure": DISCLOSURE,
    }
