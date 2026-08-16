"""Your own people, in every area of life.

``referral.match`` finds providers by area of expertise, ranks geography
*within* it, and never invents one to fill a gap. That is the right search and
it is not the right answer, because a person who has a butcher does not want a
butcher — they want **theirs**.

    asked     who could help with this
    mattered  who does this person already trust with it

The gap is not clinical. A cook profile reaching for a butcher, a money
profile reaching for a broker, a coach reaching for a physiotherapist: every
synthetic profile that can hand a matter to somebody real hits the same
question, and the search answers it from scratch every time. So this is a
register of the people a user has already chosen, per area, and the handoff
consults it before it consults the map.

## The area is the provider's, never the caller's

:func:`attach` takes an id and reads the area off the provider row. It does
not accept an area from whoever is attaching, because a form that lets the
caller say what somebody *is* is a form that will eventually file a butcher
under cardiology — and the whole point of ``referral.match``'s ordering is
that expertise filters before geography ranks. A wrong area here would defeat
that ordering from inside the data.

## One preferred, and the rest still yours

A person can have several people in an area — two doctors, an accountant and
a tax lawyer — and exactly one of them is who the profile should reach for
first. Preferring one demotes the others rather than deleting them: the
second opinion is still somebody they chose.
"""

from __future__ import annotations

from . import db, referral


class NotYourPerson(ValueError):
    """A person cannot be attached, preferred or reached. Carries text for a
    reader, in the estate's usual way."""


def _provider(provider_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM providers WHERE id=?", (provider_id,)).fetchone()
    if row is None:
        raise NotYourPerson("no such provider")
    return dict(row)


def attach(interactor_id: str, provider_id: str, note: str | None = None,
           preferred: bool = False) -> dict:
    """Keep somebody as yours in their own area.

    The area is read from the provider rather than taken as an argument —
    see the module docstring for why that is not a convenience.
    """
    provider = _provider(provider_id)
    conn = db.connect()
    conn.execute(
        "INSERT OR REPLACE INTO known_providers"
        " (interactor_id, provider_id, area, preferred, note, attached_at)"
        " VALUES (?,?,?,?,?,?)",
        (interactor_id, provider_id, provider["area"], 0, note, db.utcnow()))
    conn.commit()
    if preferred:
        return prefer(interactor_id, provider_id)
    return _mine_row(interactor_id, provider_id)


def prefer(interactor_id: str, provider_id: str) -> dict:
    """Make this the one a profile reaches for first in their area.

    Demotes the others in that area rather than dropping them: a second
    opinion is still somebody this person chose.
    """
    row = _mine_row(interactor_id, provider_id)
    conn = db.connect()
    conn.execute(
        "UPDATE known_providers SET preferred=0"
        " WHERE interactor_id=? AND area=?", (interactor_id, row["area"]))
    conn.execute(
        "UPDATE known_providers SET preferred=1"
        " WHERE interactor_id=? AND provider_id=?",
        (interactor_id, provider_id))
    conn.commit()
    return _mine_row(interactor_id, provider_id)


def detach(interactor_id: str, provider_id: str) -> dict:
    conn = db.connect()
    changed = conn.execute(
        "DELETE FROM known_providers WHERE interactor_id=? AND provider_id=?",
        (interactor_id, provider_id)).rowcount
    conn.commit()
    if not changed:
        raise NotYourPerson("that person is not one of yours")
    return {"provider_id": provider_id, "attached": False}


def _out(r) -> dict:
    return {"provider_id": r["provider_id"], "name": r["name"],
            "area": r["area"], "location": r["location"],
            "contact": r["contact"], "business": bool(r["business"]),
            "preferred": bool(r["preferred"]), "note": r["note"],
            "yours": True, "attached_at": r["attached_at"]}


_JOIN = ("SELECT k.*, p.name, p.location, p.contact, p.business"
         " FROM known_providers k JOIN providers p ON p.id = k.provider_id"
         " WHERE k.interactor_id=?")


def _mine_row(interactor_id: str, provider_id: str) -> dict:
    row = db.connect().execute(
        _JOIN + " AND k.provider_id=?", (interactor_id, provider_id)).fetchone()
    if row is None:
        raise NotYourPerson("that person is not one of yours")
    return _out(row)


def mine(interactor_id: str, area: str | None = None) -> list[dict]:
    """Everybody this person has kept, preferred first inside each area."""
    sql = _JOIN + (" AND k.area=?" if area else "")
    args = (interactor_id, area) if area else (interactor_id,)
    rows = db.connect().execute(
        sql + " ORDER BY k.area, k.preferred DESC, p.name", args).fetchall()
    return [_out(r) for r in rows]


def preferred(interactor_id: str, area: str) -> dict | None:
    """The one to reach for first in this area, or nothing."""
    for row in mine(interactor_id, area):
        if row["preferred"]:
            return row
    return None


def for_area(interactor_id: str, area: str, location: str | None = None,
             limit: int = 5) -> list[dict]:
    """Who a profile should offer for this area: yours first, then the search.

    Not a merge of two rankings — an ordering with a reason. Somebody this
    person already chose outranks the best stranger the map can produce, and
    the search still runs underneath so an area they have nobody in is not a
    dead end. Every row says which it is, because *yours* and *found for you*
    are different claims and a reader deciding who to send their history to
    is entitled to know which one they are looking at.
    """
    ours = mine(interactor_id, area)
    seen = {r["provider_id"] for r in ours}
    found = [dict(r, yours=False) for r in referral.match(area, location, limit)
             if r["id"] not in seen]
    for r in found:
        r["provider_id"] = r.pop("id")
    return (ours + found)[:max(limit, len(ours))]
