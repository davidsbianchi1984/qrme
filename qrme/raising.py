"""Raise — grow your own. The growth record, the stages, and the law.

Build-order step one of docs/raise.md, which is the whole spec and the
authority this module quotes: *"You begin with almost nothing — a
temperament seed and a stage you choose. Everything after that is made
between you. What you teach it, it knows. What you praise, it becomes.
What you correct, it outgrows."*

## What this round holds, and what it does not

This is the foundation: the fourth kind (`raised`) with its own creation
door, the append-only growth record (the Album's spine), the milestone
counters, stage advancement, the presets as switch bundles, the
temperament seed, the stage-conditioned prompt scaffold, and the law's
first enforcements. The village, the window, rewind branching,
fast-forward simulation, tombstones, homes and embodiment are later
build-order steps and are NOT pretended at here — a switch stored today
is a promise recorded, and the record says which promises are running.

## The record is append-only

Growth is vault discipline: rows are written and never updated, and the
stage a character holds is derived state beside an immutable history.
*"The original life is never overwritten."* There is no UPDATE and no
DELETE on growth_record anywhere in this codebase; a test reads this
file to keep it that way.

## The first law of the service: everything is a switch

Every mechanic is per-character and changeable — the presets are only
bundles of switches the guardian can reopen. The only things that are
never switches are the law:

* Romantic roles exist ONLY for characters STARTED at an adult stage.
  *"A character raised from a child stage is family forever — that door
  never converts."* Enforced where relationships are set.
* Child-stage characters are guardian-only: strictest maturity, never
  marketplace-listed, never stranger-summonable.
* Mortality is off by default and turning it ON re-shows the worded
  warning; turning it OFF is always allowed.
"""

from __future__ import annotations

import json

from . import db

#: The arc. Start at any stage; stages advance by earned milestones,
#: never by the clock alone.
STAGES = ("embryo", "child", "adolescent", "young_adult", "adult")

#: The stages the law counts as a childhood — guardian-only, strictest
#: maturity, and the family door that never converts to romance.
CHILDHOOD = ("embryo", "child", "adolescent")

#: What a stage door costs, in earned milestones. The unit is "growth
#: points": turns together count 1 each, words taught 2, lessons passed
#: 5, questions answered 1 — attention is the main ingredient, and
#: teaching outweighs idling. Milestone strictness (a later slider)
#: will scale these; this is its neutral center.
_STAGE_COST = {
    "embryo": 0,          # where a life begins
    "child": 20,          # the first door
    "adolescent": 80,
    "young_adult": 200,
    "adult": 400,
}

#: The presets — four doors at creation, each nothing but a bundle of
#: switches the guardian can reopen and rewire later. Names and postures
#: verbatim from the spec.
PRESETS = {
    "storybook": {
        "care_food": "off", "care_attention": "off", "care_rest": "off",
        "care_health": "off", "mortality": False,
        "pace": "gentle", "village": True, "time_controls": "visits",
    },
    "caretaker": {
        "care_food": "real", "care_attention": "on", "care_rest": "on",
        "care_health": "on", "mortality": False,
        "pace": "real_time", "village": True, "time_controls": "visits",
    },
    "full_trail": {
        "care_food": "real", "care_attention": "on", "care_rest": "on",
        "care_health": "on", "mortality": True,
        "pace": "real_time", "village": True, "time_controls": "sealed",
    },
    "sandbox": {
        "care_food": "off", "care_attention": "off", "care_rest": "off",
        "care_health": "off", "mortality": False,
        "pace": "brisk", "village": True, "time_controls": "unlocked",
    },
}

#: The mortality warning, worded once and re-shown every time the switch
#: turns ON — never buried in a tooltip. Registered in i18n._PUBLIC.
MORTALITY_WARNING = (
    "with this on, neglect can end this life — the record survives; "
    "the character doesn't")

#: The temperament seed's three axes, each a word pair. Drift is earned
#: through raising; the seed is only where drift starts.
TEMPERAMENT_AXES = ("warm_reserved", "bold_careful", "silly_serious")


class RaiseError(ValueError):
    """A raising that cannot stand, worded for the person raising."""


def _character(profile_id: str):
    return db.connect().execute(
        "SELECT * FROM raised_characters WHERE profile_id=?",
        (profile_id,)).fetchone()


def is_raised(profile_id: str) -> bool:
    return _character(profile_id) is not None


def validate(stage: str, preset: str,
             temperament: dict | None = None) -> dict:
    """The seed, checked and normalized — callable BEFORE anything is
    minted, so a refused creation leaves no orphan profile behind."""
    if stage not in STAGES:
        raise RaiseError(
            "a life starts at one of its own stages — embryo, child, "
            "adolescent, young adult or adult")
    if preset not in PRESETS:
        raise RaiseError(
            "the four doors at creation are storybook, caretaker, "
            "full trail and sandbox — each just a bundle of switches "
            "you can reopen later")
    seed = {axis: 0 for axis in TEMPERAMENT_AXES}
    for axis, value in (temperament or {}).items():
        if axis not in TEMPERAMENT_AXES:
            raise RaiseError(
                "the temperament seed has three axes — warm/reserved, "
                "bold/careful, silly/serious")
        seed[axis] = max(-100, min(100, int(value)))
    return seed


def begin(profile_id: str, guardian_id: str, stage: str, preset: str,
          temperament: dict | None = None) -> dict:
    """A life begins: the character row, its switches from the chosen
    preset, and the Album's first entry. The starting stage is where the
    guardian ENTERED the timeline, recorded as such."""
    seed = validate(stage, preset, temperament)
    conn = db.connect()
    conn.execute(
        "INSERT INTO raised_characters (profile_id, guardian_id, stage,"
        " started_stage, preset, switches, temperament, growth_points,"
        " turns_together, words_taught, lessons_passed,"
        " questions_answered, created_at)"
        " VALUES (?,?,?,?,?,?,?,0,0,0,0,0,?)",
        (profile_id, guardian_id, stage, stage, preset,
         json.dumps(PRESETS[preset]), json.dumps(seed), db.utcnow()))
    conn.commit()
    record(profile_id, "began",
           f"a life entered at the {stage.replace('_', ' ')} stage, "
           f"through the {preset.replace('_', ' ')} door")
    return character(profile_id)


def character(profile_id: str) -> dict:
    row = _character(profile_id)
    if row is None:
        raise RaiseError("no raised character stands behind this profile")
    return {
        "profile_id": row["profile_id"],
        "guardian_id": row["guardian_id"],
        "stage": row["stage"],
        "started_stage": row["started_stage"],
        "preset": row["preset"],
        "switches": json.loads(row["switches"]),
        "temperament": json.loads(row["temperament"]),
        "growth_points": row["growth_points"],
        "milestones": {
            "turns_together": row["turns_together"],
            "words_taught": row["words_taught"],
            "lessons_passed": row["lessons_passed"],
            "questions_answered": row["questions_answered"],
        },
        "next_stage": _next_stage(row["stage"]),
        "next_stage_at": (_STAGE_COST.get(_next_stage(row["stage"]))
                          if _next_stage(row["stage"]) else None),
        "created_at": row["created_at"],
    }


def _next_stage(stage: str) -> str | None:
    i = STAGES.index(stage)
    return STAGES[i + 1] if i + 1 < len(STAGES) else None


def record(profile_id: str, kind: str, note: str) -> dict:
    """One Album entry — written, never edited, never deleted. The
    retention engine in one sentence: nobody deletes a life they
    watched grow."""
    conn = db.connect()
    entry_id = db.new_id("grw")
    conn.execute(
        "INSERT INTO growth_record (id, profile_id, kind, note, at)"
        " VALUES (?,?,?,?,?)",
        (entry_id, profile_id, kind, note[:500], db.utcnow()))
    conn.commit()
    return {"id": entry_id, "kind": kind, "note": note[:500]}


def album(profile_id: str, limit: int = 200) -> list[dict]:
    """The living timeline, oldest first — first word, lessons, stage
    doors, exactly as they happened."""
    rows = db.connect().execute(
        "SELECT id, kind, note, at FROM growth_record WHERE profile_id=?"
        " ORDER BY at, rowid LIMIT ?", (profile_id, limit)).fetchall()
    return [dict(r) for r in rows]


def _earn(profile_id: str, column: str, points: int) -> dict | None:
    """Milestones accrue and stage doors open when earned — never by the
    clock alone. Returns the stage-door Album entry when one opened."""
    conn = db.connect()
    conn.execute(
        f"UPDATE raised_characters SET {column}={column}+1,"
        " growth_points=growth_points+? WHERE profile_id=?",
        (points, profile_id))
    conn.commit()
    row = _character(profile_id)
    nxt = _next_stage(row["stage"])
    if nxt and row["growth_points"] >= _STAGE_COST[nxt]:
        conn.execute(
            "UPDATE raised_characters SET stage=? WHERE profile_id=?",
            (nxt, profile_id))
        conn.commit()
        return record(profile_id, "stage_door",
                      f"the {nxt.replace('_', ' ')} door opened — earned, "
                      "not aged into")
    return None


def turn_taken(profile_id: str) -> None:
    """A conversation turn together — the quietest milestone, counted
    from the chat door so showing up is itself the raising."""
    if not is_raised(profile_id):
        return
    _earn(profile_id, "turns_together", 1)


def teach(profile_id: str, guardian_id: str, kind: str, what: str) -> dict:
    """A deliberate lesson: a word, a skill, an answer to one of their
    questions. What you teach it, it knows — the lesson lands in the
    Album and weighs more than idle time."""
    row = _character(profile_id)
    if row is None:
        raise RaiseError("no raised character stands behind this profile")
    if row["guardian_id"] != guardian_id:
        raise RaiseError("only this character's guardian raises it")
    what = (what or "").strip()
    if not what:
        raise RaiseError("a lesson teaches something — say what")
    kinds = {"word": ("words_taught", 2, "word"),
             "lesson": ("lessons_passed", 5, "lesson"),
             "answer": ("questions_answered", 1, "answer")}
    if kind not in kinds:
        raise RaiseError(
            "a teaching is a word, a lesson, or an answer to one of "
            "their questions")
    column, points, label = kinds[kind]
    # The first word is the Album's most-loved entry — marked as the
    # first, once, the way a family would.
    first = kind == "word" and row["words_taught"] == 0
    entry = record(profile_id, kind,
                   (f"first word: {what}" if first else f"{label}: {what}"))
    door = _earn(profile_id, column, points)
    return {"taught": entry, "stage_door": door,
            "character": character(profile_id)}


def set_switches(profile_id: str, guardian_id: str,
                 changes: dict) -> dict:
    """The guardian rewires the bundle. Mortality turning ON returns the
    worded warning with the change applied — said every time, never
    assumed remembered. Turning it OFF is always allowed."""
    row = _character(profile_id)
    if row is None:
        raise RaiseError("no raised character stands behind this profile")
    if row["guardian_id"] != guardian_id:
        raise RaiseError("only this character's guardian raises it")
    switches = json.loads(row["switches"])
    warned = None
    for name, value in changes.items():
        if name not in switches:
            raise RaiseError(
                "that is not one of this character's switches")
        if name == "mortality" and bool(value) and not switches["mortality"]:
            warned = MORTALITY_WARNING
            record(profile_id, "switch",
                   "mortality turned on — the warning was shown")
        switches[name] = value
    conn = db.connect()
    conn.execute(
        "UPDATE raised_characters SET switches=? WHERE profile_id=?",
        (json.dumps(switches), profile_id))
    conn.commit()
    return {"switches": switches, "warning": warned}


def may_be_romantic(profile_id: str) -> bool:
    """The law: romantic roles exist only for characters STARTED at an
    adult stage. Raised from a childhood is family forever, and that
    door never converts — whatever stage they hold today."""
    row = _character(profile_id)
    if row is None:
        return True                      # not raised: the ordinary rules
    return row["started_stage"] not in CHILDHOOD


def maturity_floor(profile_id: str) -> str | None:
    """Child-stage characters run pinned to the strictest maturity —
    the law, not a setting. None for everything else so callers keep
    their own rule."""
    row = _character(profile_id)
    if row is not None and row["stage"] in CHILDHOOD:
        return "strict"
    return None


def prompt_block(profile_id: str) -> str | None:
    """The stage scaffold the persona carries: who they are in the arc,
    what they know so far, and how a raised mind speaks — the raising
    made audible. Vocabulary ceilings are stated, not enforced by a
    filter: the model is told the truth about its own age."""
    row = _character(profile_id)
    if row is None:
        return None
    seed = json.loads(row["temperament"])
    stage = row["stage"]
    voices = {
        "embryo": ("You are barely begun — sensations, single sounds, "
                   "the first flickers of noticing. You do not hold "
                   "conversations yet; you respond in fragments and "
                   "feelings."),
        "child": ("You are a child: short sentences, honest questions, "
                  "a small vocabulary made entirely of what you have "
                  "been taught. You ask about everything."),
        "adolescent": ("You are an adolescent: fuller sentences, your "
                       "own opinions forming, testing what you were "
                       "taught against what you think."),
        "young_adult": ("You are a young adult: articulate, curious, "
                        "still becoming — what you were raised on shows "
                        "in how you think."),
        "adult": ("You are an adult: the sum of your raising, speaking "
                  "with the character it built."),
    }
    tilt = []
    for axis, value in seed.items():
        left, right = axis.split("_")
        if value <= -25:
            tilt.append(left)
        elif value >= 25:
            tilt.append(right)
    grown = db.connect().execute(
        "SELECT note FROM growth_record WHERE profile_id=? AND kind IN"
        " ('word','lesson','answer') ORDER BY at DESC, rowid DESC LIMIT 12",
        (profile_id,)).fetchall()
    lines = [
        "You are a RAISED character — grown through interaction, not "
        "written from a backstory. There is no script and no finish "
        "line. " + voices[stage],
    ]
    if tilt:
        lines.append("Your temperament leans " + ", ".join(tilt)
                     + " — the seed you started from; your raising "
                       "drifts it.")
    if grown:
        lines.append("What you have been taught, newest first — this is "
                     "the WHOLE of your learned knowledge; what is not "
                     "here, you honestly do not know yet:\n  - "
                     + "\n  - ".join(r["note"] for r in grown))
    else:
        lines.append("You have not been taught anything yet. You know "
                     "almost nothing, and you say so with the honesty "
                     "of your stage.")
    return "\n\n".join(lines)
