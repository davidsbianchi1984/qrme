"""The open door: the receiver's standing yes to unprompted reach.

The oldest still-open ask, in its own words: *somebody subscribing to
the agent, rather than the agent reaching them.* The direction of
consent flips.

What stood before this: the OWNER opted a profile into proactive reach
(``interaction_scope: proactive``), and the person being reached had
only throttles — quiet hours, a rate cap, awaiting-reply suppression.
Real protections, all of them, and none of them a *yes*. The receiver
never said they wanted to hear from it first; they could only be
reached politely.

Now reach requires the door to be open at the receiving end. A person
opens their door to one profile at a time — "hear from them first" —
and closes it the same way. Closing keeps the row (a record, not an
erasure: when the door was open is a fact about the relationship), and
outreach to a closed or never-opened door refuses in a sentence.

Both consents stand, and neither implies the other. The owner's
``proactive`` scope says the profile is *willing* to reach out; the
open door says this person is *willing to be reached*. An open door
cannot make a reactive-only profile speak first — a subscription is not
a lever on somebody else's profile — and a proactive profile cannot
step through a door nobody opened.

## Cadence tightens, never loosens

The subscriber picks how often is welcome — ``daily``, ``weekly``, or
``whenever`` (the profile's own pace). The effective interval is the
LOOSER bound of the two made binding on both: ``max(profile's rate cap,
the door's cadence)``. A door can slow a profile down; it can never
speed one up past the owner's cap.
"""

from __future__ import annotations

from . import db, i18n

#: How often is welcome, in hours. `whenever` defers to the profile's own
#: rate cap alone.
CADENCES = {"daily": 24, "weekly": 168, "whenever": 0}

#: The refusal the outreach door gives when no door is open. Translated
#: in i18n._REFUSALS.
DOOR_CLOSED = ("they have not asked to hear from this profile first — "
               "unprompted reach goes only to people whose door is open")


def set_door(interactor_id: str, profile_id: str, *, open_: bool,
             cadence: str = "whenever") -> dict:
    """Open or close one person's door to one profile.

    Closing keeps the row with when and that it closed — the record of a
    standing yes that was withdrawn is not the same fact as a yes never
    given, and the profile's side of the relationship may honestly say
    "they used to want this".
    """
    if cadence not in CADENCES:
        raise ValueError(i18n.fill(i18n.MUST_BE_ONE_OF, field="cadence",
                                   choices=", ".join(CADENCES)))
    conn = db.connect()
    if open_:
        conn.execute(
            "INSERT INTO open_doors (interactor_id, profile_id, cadence,"
            " opened_at, closed_at) VALUES (?,?,?,?,NULL)"
            " ON CONFLICT (interactor_id, profile_id) DO UPDATE SET"
            " cadence=excluded.cadence, opened_at=excluded.opened_at,"
            " closed_at=NULL",
            (interactor_id, profile_id, cadence, db.utcnow()))
    else:
        conn.execute(
            "UPDATE open_doors SET closed_at=? WHERE interactor_id=?"
            " AND profile_id=? AND closed_at IS NULL",
            (db.utcnow(), interactor_id, profile_id))
    conn.commit()
    return standing(interactor_id, profile_id)


def standing(interactor_id: str, profile_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM open_doors WHERE interactor_id=? AND profile_id=?",
        (interactor_id, profile_id)).fetchone()
    if row is None:
        return {"open": False, "cadence": None, "ever_opened": False}
    return {"open": row["closed_at"] is None,
            "cadence": row["cadence"],
            "ever_opened": True,
            "opened_at": row["opened_at"],
            "closed_at": row["closed_at"]}


def is_open(interactor_id: str, profile_id: str) -> bool:
    return standing(interactor_id, profile_id)["open"]


def cadence_hours(interactor_id: str, profile_id: str) -> int:
    """The door's own pace, as hours between reaches — 0 for `whenever`,
    which leaves the profile's rate cap as the only bound."""
    got = standing(interactor_id, profile_id)
    if not got["open"]:
        return 0
    return CADENCES.get(got["cadence"] or "whenever", 0)


def mine(interactor_id: str) -> list[dict]:
    """Every door this person holds, open ones first — the standing yeses
    they can walk down and close."""
    rows = db.connect().execute(
        "SELECT * FROM open_doors WHERE interactor_id=?"
        " ORDER BY closed_at IS NOT NULL, opened_at DESC",
        (interactor_id,)).fetchall()
    return [{"profile_id": r["profile_id"],
             "open": r["closed_at"] is None,
             "cadence": r["cadence"],
             "opened_at": r["opened_at"], "closed_at": r["closed_at"]}
            for r in rows]


def openers(profile_id: str) -> list[dict]:
    """Who opened their door to this profile — the owner's view of the
    inverted connection: an audience that asked, rather than one the
    profile reached for."""
    rows = db.connect().execute(
        "SELECT * FROM open_doors WHERE profile_id=? AND closed_at IS NULL"
        " ORDER BY opened_at DESC", (profile_id,)).fetchall()
    return [{"interactor_id": r["interactor_id"], "cadence": r["cadence"],
             "opened_at": r["opened_at"]} for r in rows]
