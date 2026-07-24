"""Pilot controls: live throttles and sliders for agents, profiles, robots.

An owner *pilots* what they run. Each dial is 0–100 (default 50 = as
written); moving it nudges style, pace, or behavior without ever touching
core identity or safety. Dials come in three groups:

- **system** — how the thing *operates*: ``pace`` (the throttle: how fast /
  eager it acts and replies), ``autonomy`` (how much it does before asking),
  ``verbosity``.
- **behavior** — how it *comes across*: ``warmth``, ``formality``, ``humor``,
  ``assertiveness``.
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
    "intimacy": ("intimacy", "Intimacy",
                 "reserved", "flirtatious & affectionate (within boundaries)",
                 True),
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
        "SELECT dials FROM pilot_controls WHERE subject_id=?",
        (subject_id,)).fetchone()
    stored = json.loads(row["dials"]) if row else {}
    return {name: int(stored.get(name, DEFAULT)) for name in DIALS}


def set_dials(subject_id: str, values: dict, adult: bool) -> dict[str, int]:
    """Persist dial changes. Unknown dials are ignored; each is clamped to
    0–100; the intimacy dial is hard-clamped to 0 unless the subject is
    adult-mode, so it can never be raised on a non-rated profile."""
    current = get(subject_id)
    for name, raw in values.items():
        if name not in DIALS:
            continue
        val = max(0, min(100, int(raw)))
        if DIALS[name][4] and not adult:
            val = 0
        current[name] = val
    if not adult:
        current["intimacy"] = 0
    conn = db.connect()
    conn.execute(
        "INSERT INTO pilot_controls (subject_id, dials, updated_at)"
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
    head = ("Pilot settings from your owner — adjust style, pace, and manner "
            "accordingly, but never your core identity, your boundaries, or "
            "the safety rules:")
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
