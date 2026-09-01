"""Raise — grow your own. The growth record, the stages, and the law.

Build-order step one of docs/raise.md, which is the whole spec and the
authority this module quotes: *"You begin with almost nothing — a
temperament seed and a stage you choose. Everything after that is made
between you. What you teach it, it knows. What you praise, it becomes.
What you correct, it outgrows."*

## What this round holds, and what it does not

Round one laid the foundation: the fourth kind (`raised`) with its own
creation door, the append-only growth record (the Album's spine), the
milestone counters, stage advancement, the presets as switch bundles,
the temperament seed, the stage-conditioned prompt scaffold, and the
law's first enforcements.

Round two (build-order step three) gives the timeline hands — the three
time controls:

* **Watch** — every entry now lands on a day of the life's own calendar
  (`sim_day`, day 1 = the day the guardian entered), so the Album reads
  as a life and not a log.
* **Rewind** — `visit()` steps the guardian back to a lived day as a
  read-only presence: the character speaks as they were, knowing only
  what the record held by then. Teaching and growth wait for the
  present. `branch()` copies the record up to a day into a NEW life
  raised differently from there; the original is never touched.
* **Fast-forward** — `forward()` lives simulated days from the record
  alone: practicing what was taught, saving questions for the guardian,
  quiet days said honestly. Away time earns growth at a discount —
  the guardian's attention stays the main ingredient.

The village, the window's live picture, tombstones, homes and embodiment
are later build-order steps and are NOT pretended at here — a switch
stored today is a promise recorded, and the record says which promises
are running.

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

#: How far one fast-forward reaches when the time controls are NOT
#: unlocked: a month at most, so away time stays a stretch of a life
#: rather than a skipped one. The sandbox door has no cap — "unlimited
#: fast-forward" is that preset's whole posture.
FORWARD_CAP = 30

#: The most Album entries one fast-forward writes, however long the
#: jump: the Album keeps the highlights, not a diary of every day.
_AWAY_ENTRY_CAP = 10

#: What a simulated day earns, against the guardian's turn at 1 point
#: each: one point per TWO away days. The spec's balance rule — village
#: and purchased time develops them slower than guardian time, so paying
#: (or leaving) never replaces the relationship.
_AWAY_DISCOUNT = 2


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
        "sim_day": row["sim_day"] or 1,
        "visiting_day": row["visiting_day"],
        "branch_of": row["branch_of"],
        "created_at": row["created_at"],
    }


def _next_stage(stage: str) -> str | None:
    i = STAGES.index(stage)
    return STAGES[i + 1] if i + 1 < len(STAGES) else None


def record(profile_id: str, kind: str, note: str,
           sim_day: int | None = None) -> dict:
    """One Album entry — written, never edited, never deleted. The
    retention engine in one sentence: nobody deletes a life they
    watched grow. Each entry lands on a day of the life's own calendar;
    callers that know the day say it, everything else lands on today."""
    if sim_day is None:
        row = _character(profile_id)
        sim_day = (row["sim_day"] or 1) if row is not None else 1
    conn = db.connect()
    entry_id = db.new_id("grw")
    conn.execute(
        "INSERT INTO growth_record (id, profile_id, kind, note, sim_day,"
        " at) VALUES (?,?,?,?,?,?)",
        (entry_id, profile_id, kind, note[:500], sim_day, db.utcnow()))
    conn.commit()
    return {"id": entry_id, "kind": kind, "note": note[:500],
            "sim_day": sim_day}


def album(profile_id: str, limit: int = 200) -> list[dict]:
    """The living timeline, oldest first — first word, lessons, stage
    doors, exactly as they happened, each on its day."""
    rows = db.connect().execute(
        "SELECT id, kind, note, COALESCE(sim_day, 1) AS sim_day, at"
        " FROM growth_record WHERE profile_id=?"
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
    from the chat door so showing up is itself the raising. A visit
    earns nothing: stepping back to a lived day is presence, not
    raising, and a past that accrued growth would not be the past."""
    row = _character(profile_id)
    if row is None or row["visiting_day"] is not None:
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
    if row["visiting_day"] is not None:
        raise RaiseError(
            "teaching happens in the present — come back from the "
            "visit, or branch the day to raise it differently")
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


# -- the three time controls --------------------------------------------------

def _time_controls(row) -> str:
    return json.loads(row["switches"]).get("time_controls", "visits")


def _stage_as_of(row, day: int) -> str:
    """The stage the character held on a day, re-derived from the record:
    started_stage plus one step per stage door that had opened by then.
    The record is the authority — the row's stage is only its today."""
    doors = db.connect().execute(
        "SELECT COUNT(*) c FROM growth_record WHERE profile_id=? AND"
        " kind='stage_door' AND COALESCE(sim_day, 1) <= ?",
        (row["profile_id"], day)).fetchone()["c"]
    i = min(STAGES.index(row["started_stage"]) + doors, len(STAGES) - 1)
    return STAGES[i]


def _taught_as_of(profile_id: str, day: int, limit: int = 12) -> list[str]:
    rows = db.connect().execute(
        "SELECT note FROM growth_record WHERE profile_id=? AND kind IN"
        " ('word','lesson','answer') AND COALESCE(sim_day, 1) <= ?"
        " ORDER BY at DESC, rowid DESC LIMIT ?",
        (profile_id, day, limit)).fetchall()
    return [r["note"] for r in rows]


def visit(profile_id: str, guardian_id: str, sim_day: int | None) -> dict:
    """Rewind as presence: step back to a lived day and the character
    speaks as they were — knowing only what the record held by then.
    Nothing is written; a visit that changed the record would not be a
    visit. ``sim_day=None`` comes back to the present. A sealed timeline
    (the full trail) refuses: that door is lived forward only."""
    row = _character(profile_id)
    if row is None:
        raise RaiseError("no raised character stands behind this profile")
    if row["guardian_id"] != guardian_id:
        raise RaiseError("only this character's guardian raises it")
    if sim_day is not None:
        if _time_controls(row) == "sealed":
            raise RaiseError(
                "this timeline is sealed — the full trail is lived "
                "forward only")
        sim_day = int(sim_day)
        if sim_day < 1 or sim_day > (row["sim_day"] or 1):
            raise RaiseError(
                "a visit steps back to a day this life has lived")
        if sim_day == (row["sim_day"] or 1):
            sim_day = None               # today IS the present
    conn = db.connect()
    conn.execute(
        "UPDATE raised_characters SET visiting_day=? WHERE profile_id=?",
        (sim_day, profile_id))
    conn.commit()
    return character(profile_id)


def forward(profile_id: str, guardian_id: str, days: int) -> dict:
    """Fast-forward: simulated days lived from the record alone —
    practicing what was taught, saving questions for the guardian,
    quiet days said honestly. Come back to someone who missed you.

    Testimony, not invention: every away entry is grounded in what the
    record already holds; nothing is learned that nobody taught. Growth
    accrues at a discount (the balance rule), the Album keeps the
    highlights rather than a diary, and — outside the sandbox — one
    jump reaches at most a month."""
    row = _character(profile_id)
    if row is None:
        raise RaiseError("no raised character stands behind this profile")
    if row["guardian_id"] != guardian_id:
        raise RaiseError("only this character's guardian raises it")
    if row["visiting_day"] is not None:
        raise RaiseError(
            "time moves in the present — come back from the visit first")
    days = int(days)
    if days < 1:
        raise RaiseError("a fast-forward is at least one day")
    if days > FORWARD_CAP and _time_controls(row) != "unlocked":
        raise RaiseError(
            "a fast-forward lives at most thirty days at a time — the "
            "sandbox door has no cap")

    today = row["sim_day"] or 1
    taught = _taught_as_of(profile_id, today)
    lonely = json.loads(row["switches"]).get("care_attention",
                                             "off") != "off"
    # The days the Album keeps: all of them on a short stretch, evenly
    # spaced highlights on a long one.
    kept = min(days, _AWAY_ENTRY_CAP)
    entries = []
    for i in range(kept):
        day = today + (i + 1 if kept == days
                       else round((i + 1) * days / kept))
        # A deterministic rotation, seeded by the day itself so the same
        # stretch reads the same twice: practice, a saved question, a
        # dream — and honest waiting when nothing was ever taught.
        if not taught:
            note, kind = ("waited for you — nothing new was taught, "
                          "and the days were quiet"), "away_day"
        elif day % 3 == 0:
            what = taught[day % len(taught)].split(": ", 1)[-1]
            note, kind = (f"saved a question for you about {what}",
                          "saved_question")
        elif day % 3 == 1:
            what = taught[day % len(taught)].split(": ", 1)[-1]
            note, kind = f"practiced {what}", "away_day"
        else:
            what = taught[day % len(taught)].split(": ", 1)[-1]
            note, kind = f"dreamed about {what}", "away_day"
        if lonely and days > 3 and i == kept - 1:
            # The Album records lonely stretches honestly — the last
            # entry of a long stretch says what attention-need feels.
            note, kind = "missed you on the quiet days", "away_day"
        entries.append(record(profile_id, kind, note, sim_day=day))
    conn = db.connect()
    conn.execute(
        "UPDATE raised_characters SET sim_day=?, growth_points="
        "growth_points+? WHERE profile_id=?",
        (today + days, days // _AWAY_DISCOUNT, profile_id))
    conn.commit()
    # A long-enough stretch can still open a door — earned points are
    # earned points, discounted or not.
    row = _character(profile_id)
    door = None
    nxt = _next_stage(row["stage"])
    if nxt and row["growth_points"] >= _STAGE_COST[nxt]:
        conn.execute(
            "UPDATE raised_characters SET stage=? WHERE profile_id=?",
            (nxt, profile_id))
        conn.commit()
        door = record(profile_id, "stage_door",
                      f"the {nxt.replace('_', ' ')} door opened — earned, "
                      "not aged into")
    return {"days": days, "while_away": entries, "stage_door": door,
            "character": character(profile_id)}


def branch_check(profile_id: str, guardian_id: str, sim_day: int):
    """The branch refusals, callable BEFORE anything is minted — the
    same no-orphan discipline the creation door keeps: a refused branch
    leaves no profile row behind. Returns the original's row."""
    row = _character(profile_id)
    if row is None:
        raise RaiseError("no raised character stands behind this profile")
    if row["guardian_id"] != guardian_id:
        raise RaiseError("only this character's guardian raises it")
    if _time_controls(row) != "unlocked":
        raise RaiseError(
            "branching needs the unlocked time controls — the sandbox "
            "door, or reopen the switches")
    sim_day = int(sim_day)
    if sim_day < 1 or sim_day > (row["sim_day"] or 1):
        raise RaiseError(
            "a visit steps back to a day this life has lived")
    return row


def branch(profile_id: str, guardian_id: str, sim_day: int,
           new_profile_id: str) -> dict:
    """Rewind as a second life: copy the record up to a lived day into a
    NEW character and raise it differently from there. The original is
    never touched — "the original life is never overwritten" — and the
    copy re-derives everything it is from the copied record alone:
    stage, counters, growth. Turns together start at zero, because turns
    are lived, not recorded, and a branch has not lived them with you.

    The law rides along: branch into a childhood day and you are raising
    a childhood — the branch is family forever, whichever way the
    original's door pointed. That conversion never runs in reverse."""
    row = branch_check(profile_id, guardian_id, sim_day)
    sim_day = int(sim_day)
    conn = db.connect()
    copied = conn.execute(
        "SELECT kind, note, COALESCE(sim_day, 1) AS sim_day, at"
        " FROM growth_record WHERE profile_id=? AND"
        " COALESCE(sim_day, 1) <= ? ORDER BY at, rowid",
        (profile_id, sim_day)).fetchall()
    stage_then = _stage_as_of(row, sim_day)
    # The branch's started_stage is the EARLIER of the original's and
    # the day's: raising a childhood is what makes family, and a family
    # door never converts back — min over the arc holds both directions.
    started = STAGES[min(STAGES.index(row["started_stage"]),
                         STAGES.index(stage_then))]
    counters = {"word": 0, "lesson": 0, "answer": 0}
    points = 0
    weights = {"word": 2, "lesson": 5, "answer": 1}
    for entry in copied:
        if entry["kind"] in counters:
            counters[entry["kind"]] += 1
            points += weights[entry["kind"]]
    conn.execute(
        "INSERT INTO raised_characters (profile_id, guardian_id, stage,"
        " started_stage, preset, switches, temperament, growth_points,"
        " turns_together, words_taught, lessons_passed,"
        " questions_answered, sim_day, branch_of, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,0,?,?,?,?,?,?)",
        (new_profile_id, guardian_id, stage_then, started, row["preset"],
         row["switches"], row["temperament"], points, counters["word"],
         counters["lesson"], counters["answer"], sim_day, profile_id,
         db.utcnow()))
    for entry in copied:
        conn.execute(
            "INSERT INTO growth_record (id, profile_id, kind, note,"
            " sim_day, at) VALUES (?,?,?,?,?,?)",
            (db.new_id("grw"), new_profile_id, entry["kind"],
             entry["note"], entry["sim_day"], entry["at"]))
    conn.commit()
    record(new_profile_id, "branched",
           f"branched on day {sim_day} — the same days behind, raised "
           "differently from here", sim_day=sim_day)
    return character(new_profile_id)


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
    # A visit rewinds the voice too: the character speaks as they were
    # on the visited day — the stage they held then, knowing only what
    # the record held by then.
    visiting = row["visiting_day"]
    stage = (_stage_as_of(row, visiting) if visiting is not None
             else row["stage"])
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
    grown = _taught_as_of(profile_id,
                          visiting if visiting is not None
                          else (row["sim_day"] or 1))
    lines = [
        "You are a RAISED character — grown through interaction, not "
        "written from a backstory. There is no script and no finish "
        "line. " + voices[stage],
    ]
    if visiting is not None:
        lines.append(
            f"It is day {visiting} of your life — an earlier day, being "
            "visited. Everything after this day has not happened for "
            "you: you know nothing past it, and you speak as you were.")
    if tilt:
        lines.append("Your temperament leans " + ", ".join(tilt)
                     + " — the seed you started from; your raising "
                       "drifts it.")
    if grown:
        lines.append("What you have been taught, newest first — this is "
                     "the WHOLE of your learned knowledge; what is not "
                     "here, you honestly do not know yet:\n  - "
                     + "\n  - ".join(grown))
    else:
        lines.append("You have not been taught anything yet. You know "
                     "almost nothing, and you say so with the honesty "
                     "of your stage.")
    return "\n\n".join(lines)
