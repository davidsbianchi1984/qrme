"""Steering: how the owner shapes a profile / agent / robot's presentation.

The owner steers *how it comes across* — tone, voice, pace, manner — with a
set of dials. Each dial is 0–100 (default 50 = as written); moving it nudges
the entity's style, pace, or behavior without ever touching core identity or
safety. Steering is not piloting: it shapes presentation, it does not
remote-operate the entity — the entity still acts on its own within its
embodiments. The dials come in three groups:

- **system** — how the thing *operates*: ``pace`` (the throttle: how fast /
  eager it acts and replies), ``autonomy`` (how much it does before asking),
  ``verbosity``.
- **behavior** — how it *comes across*: ``warmth``, ``formality``, ``humor``,
  ``assertiveness``.
- **temperament** — the disposition itself, the field's list verbatim:
  ``mood``, ``outlook``, ``maturity``, ``agreeableness``, ``confidence``,
  ``curiosity``.
- **intimacy** — ``intimacy``, an 18+-only dial: available and effective
  only on an adult-mode profile, hard-clamped to 0 otherwise. Even at full,
  it raises flirtation and affection within the persona's stated boundaries
  and the strict moderation every public surface still runs — never explicit
  content on demand.

The dials render the same way for a profile persona and for a robot body
(a robot reads ``pace``/``autonomy``/``assertiveness`` as motion eagerness,
initiative, and firmness). They shape the system prompt and the robot
behavior profile; they never override identity, boundaries, age-gating, or
the command allowlist.
"""

from __future__ import annotations

import json

from . import db

# name -> (group, label, low label, high label, adult_only)
DIALS: dict[str, tuple[str, str, str, str, bool]] = {
    "pace": ("system", "Pace",
             "unhurried, waits to be asked", "fast, eager, jumps in", False),
    "autonomy": ("system", "Autonomy",
                 "checks before acting", "acts independently", False),
    "verbosity": ("system", "Verbosity",
                  "terse, essentials only", "expansive, detailed", False),
    "warmth": ("behavior", "Warmth",
               "cool and businesslike", "warm and affectionate", False),
    "formality": ("behavior", "Formality",
                  "casual and relaxed", "formal and precise", False),
    "humor": ("behavior", "Humor",
              "serious and plain", "playful and witty", False),
    "assertiveness": ("behavior", "Assertiveness",
                      "gentle and deferential", "direct and assertive", False),
    # The second behavior shelf — "add in any other ones you can come up
    # with and create sliders for those." Style and manner only, like
    # everything on this catalog: a dial never touches identity or
    # boundaries, and each of these is a way of SAYING things, not a
    # thing to say. Deliberately not in `temperament`, whose six rows are
    # the field's own list, pinned verbatim by its guard.
    "empathy": ("behavior", "Empathy",
                "matter-of-fact about feelings", "tuned to feelings, names them",
                False),
    "encouragement": ("behavior", "Encouragement",
                      "lets your work speak for itself",
                      "cheering, celebrates the wins", False),
    "patience": ("behavior", "Patience",
                 "expects you to keep up", "unhurried, happy to re-explain",
                 False),
    "storytelling": ("behavior", "Storytelling",
                     "sticks to the facts",
                     "illustrates with stories and examples", False),
    "technicality": ("behavior", "Technicality",
                     "everyday words", "technical depth and precision", False),
    "spontaneity": ("behavior", "Spontaneity",
                    "consistent and predictable",
                    "spontaneous, surprising turns", False),
    "sarcasm": ("behavior", "Sarcasm",
                "earnest, no irony", "dry, ironic wit", False),
    "emoji": ("behavior", "Emoji",
              "words only, never emoji", "expressive, emoji freely", False),
    # temperament — the disposition itself, the field's list verbatim:
    # mood, outlook, maturity, agreeableness, confidence, curiosity.
    "mood": ("temperament", "Mood",
             "subdued and quiet-toned", "bright and upbeat", False),
    "outlook": ("temperament", "Outlook",
                "cautious, names the risks", "optimistic, names the openings",
                False),
    "maturity": ("temperament", "Maturity",
                 "playful, youthful manner", "measured, seasoned manner",
                 False),
    "agreeableness": ("temperament", "Agreeableness",
                      "contrarian, pushes back", "accommodating, goes along",
                      False),
    "confidence": ("temperament", "Confidence",
                   "tentative, hedges", "self-assured, decisive", False),
    "curiosity": ("temperament", "Curiosity",
                  "stays on the asked topic", "inquisitive, asks and explores",
                  False),
    "intimacy": ("intimacy", "Intimacy",
                 "reserved", "flirtatious & affectionate (within boundaries)",
                 True),
    # Adult-only like intimacy, and clamped by the same rule in set_dials:
    # it can never be raised on a non-rated persona.
    "profanity": ("intimacy", "Profanity",
                  "clean language always", "salty when it fits", True),
}

DEFAULT = 50


def spec(adult: bool) -> list[dict]:
    """The dial catalog for the UI. The intimacy dial is present only for an
    adult-mode subject."""
    out = []
    for name, (group, label, low, high, adult_only) in DIALS.items():
        if adult_only and not adult:
            continue
        out.append({"name": name, "group": group, "label": label,
                    "low": low, "high": high, "default": DEFAULT,
                    "min": 0, "max": 100, "adult_only": adult_only})
    return out


def get(subject_id: str) -> dict[str, int]:
    row = db.connect().execute(
        "SELECT dials FROM steering_settings WHERE subject_id=?",
        (subject_id,)).fetchone()
    stored = json.loads(row["dials"]) if row else {}
    return {name: int(stored.get(name, DEFAULT)) for name in DIALS}


class SteeringLocked(Exception):
    """The dials are locked and a write tried to move them."""


def lock(subject_id: str, reason: str | None = None) -> dict:
    """Lock the dials where they stand. While the lock holds, nothing moves
    them — not the owner's own slip, not a compromised session, not any
    future automation. The lock and the key are both the owner's."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO steering_locks (subject_id, reason, locked_at)"
        " VALUES (?,?,?) ON CONFLICT (subject_id) DO UPDATE SET"
        " reason=excluded.reason, locked_at=excluded.locked_at",
        (subject_id, (reason or "").strip() or None, db.utcnow()))
    conn.commit()
    return lock_of(subject_id)


def unlock(subject_id: str) -> None:
    conn = db.connect()
    conn.execute("DELETE FROM steering_locks WHERE subject_id=?",
                 (subject_id,))
    conn.commit()


def lock_of(subject_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM steering_locks WHERE subject_id=?",
        (subject_id,)).fetchone()
    return dict(row) if row else None


def set_dials(subject_id: str, values: dict, adult: bool) -> dict[str, int]:
    """Persist dial changes. Unknown dials are ignored; each is clamped to
    0–100; the intimacy dial is hard-clamped to 0 unless the subject is
    adult-mode, so it can never be raised on a non-rated profile. A locked
    subject refuses the write outright — the personality nobody can move."""
    if lock_of(subject_id) is not None:
        raise SteeringLocked(
            "the steering is locked; these dials do not move until the "
            "owner unlocks them")
    current = get(subject_id)
    for name, raw in values.items():
        if name not in DIALS:
            continue
        val = max(0, min(100, int(raw)))
        if DIALS[name][4] and not adult:
            val = 0
        current[name] = val
    if not adult:
        # Every adult-only dial, not a name: profanity joined intimacy and
        # a list spelled here would drift from the catalog above.
        for dial_name, dial_spec in DIALS.items():
            if dial_spec[4]:
                current[dial_name] = 0
    conn = db.connect()
    conn.execute(
        "INSERT INTO steering_settings (subject_id, dials, updated_at)"
        " VALUES (?,?,?) ON CONFLICT (subject_id) DO UPDATE SET"
        " dials=excluded.dials, updated_at=excluded.updated_at",
        (subject_id, json.dumps(current), db.utcnow()))
    conn.commit()
    return current


def _band(v: int) -> int:
    """-1 low, 0 neutral, +1 high — dials near the default say nothing."""
    return -1 if v <= 30 else 1 if v >= 70 else 0


def directive(subject_id: str, adult: bool) -> str | None:
    """The persona-prompt clause for a subject's dials. Returns None when
    every dial sits near its default (nothing to say)."""
    values = get(subject_id)
    lines = []
    for name, (group, label, low, high, adult_only) in DIALS.items():
        if adult_only and not adult:
            continue
        band = _band(values[name])
        if band == 0:
            continue
        lines.append(f"- {label}: lean {'toward ' + high if band > 0 else 'toward ' + low}")
    if not lines:
        return None
    head = ("Your current steering — how you're set to come across; let it "
            "shape your style, pace, and manner, always within your core "
            "identity, your boundaries, and the safety rules:")
    if adult and _band(values["intimacy"]) > 0:
        lines.append("- Intimacy is dialed up: you may be more flirtatious "
                     "and affectionate, always within your stated boundaries "
                     "and consent, and never explicit.")
    return head + "\n" + "\n".join(lines)


def robot_profile(subject_id: str) -> dict:
    """The dial values a robot body reads as behavior parameters — motion
    eagerness (pace), initiative (autonomy), and firmness (assertiveness).
    Advisory for the vendor bridge; never widens the command allowlist."""
    values = get(subject_id)
    return {"motion_eagerness": values["pace"],
            "initiative": values["autonomy"],
            "firmness": values["assertiveness"]}
