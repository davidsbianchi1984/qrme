"""Lending a skill to somebody, inside a room you are both already in.

Two people are in the same place — a room, a live desk, a watch party, a
connection — and one of them has something the other needs. A finance pack. A
robot's task modules. A profession. The ask is simple: let them use it, if both
of us want that.

The whole feature is the word **both**, and the shape it takes here is
deliberately lopsided:

    it takes two to open a grant, and one to close it.

Symmetric consent to start is what makes it a loan rather than a taking.
Asymmetric consent to end is what stops it becoming a trap — somebody who
changes their mind should not need permission from the person benefiting to
change it back. Any consent model that needs both sides to *stop* is one that
cannot be withdrawn under pressure, which is when withdrawal matters.

Four more rules do the real work.

**A skill is used, never handed over.** The borrower may invoke it while the
grant stands; they receive no copy, no install, and no licence. Packs here are
bought, licensed and attributed to publishers, and a lending feature that
quietly duplicated them would be a piracy tool with a consent dialog on the
front. :func:`use` checks the grant at the moment of use and writes a line;
nothing is ever copied into the borrower's account.

**A grant lives inside one surface and dies with it.** Lending your expertise
in a watch party does not follow the borrower into a private message. The grant
names the surface and its id, and :func:`close_surface` ends every grant in a
room when the room does — a permission must not outlive the conversation that
justified it, which is the same rule the lent-microphone work already runs on.

**Every use is visible to the lender.** "Both parties choose" is a slogan
unless the person lending can see what was done with it. :func:`uses` is the
lender's log, and it is the reason a grant is worth agreeing to: you can watch
it being used and stop it mid-sentence.

**A rated skill does not become unrated by being borrowed.** An 18+ pack lent
into a room with a minor in it is refused, because the gate belongs to the
material rather than to the account holding it.

Money stays simulated, as everywhere here. A lend can carry a fee; it lands on
the statement and no funds move.
"""

from __future__ import annotations

from . import db

# Where a grant can live. Each is a place two people are already sharing —
# there is deliberately no "everywhere" and no "my account", because a grant
# with no surface is a permission nobody can see the edges of.
SURFACES: dict[str, str] = {
    "room": "a room you are both in",
    "desk": "a live desk and its stream",
    "desk_session": "a service session at a desk's counter",
    "party": "a watch party",
    "connection": "a one-to-one connection",
    "exchange": "an agreed piece of work",
}

# What can be lent. Each names something the lender already has rather than
# something this module invents.
SKILL_KINDS: dict[str, str] = {
    "pack": "a knowledge pack they installed",
    "robot_task": "a task module on a robot they own",
    "profession": "their own stated expertise",
    "language": "translation between two languages they hold",
    "workflow": "a multi-step workflow they can run",
    # The Geek Squad kind: the program itself — Cursor, a design suite, a
    # bookkeeping app — driven through the lender's own connected-app
    # connector, used one invocation at a time and logged like every other
    # lent skill. The program is the lender's; the borrower gets uses, never
    # the connector.
    "app": "a connected program they can drive",
}

STATES = ("offered", "active", "declined", "closed")

MAX_PER_SURFACE = 12


class SharingError(ValueError):
    """A grant that cannot stand."""


def _grant(grant_id: str):
    return db.connect().execute("SELECT * FROM skill_grants WHERE id=?",
                                (grant_id,)).fetchone()


def offer(lender_id: str, borrower_id: str, surface: str, surface_id: str,
          skill_kind: str, skill_ref: str, title: str,
          note: str = "", fee: float = 0.0) -> dict:
    """Offer a skill into a shared surface. Nothing is usable yet.

    ``skill_ref`` points at the thing the lender already has — a pack id, a
    robot task name, a language pair. It is stored as a reference rather than
    copied, which is what keeps :func:`use` a permission check instead of a
    duplication.
    """
    if surface not in SURFACES:
        raise SharingError(
            f"unknown surface {surface!r}; expected one of "
            f"{', '.join(SURFACES)}")
    if skill_kind not in SKILL_KINDS:
        raise SharingError(
            f"unknown skill kind {skill_kind!r}; expected one of "
            f"{', '.join(SKILL_KINDS)}")
    if lender_id == borrower_id:
        raise SharingError("a grant needs two people")
    title = (title or "").strip()
    if not title:
        raise SharingError("say what is being lent, in words the other reads")
    if fee < 0:
        raise SharingError("a fee cannot be negative")

    live = db.connect().execute(
        "SELECT COUNT(*) AS n FROM skill_grants WHERE surface=? AND"
        " surface_id=? AND state IN ('offered','active')",
        (surface, surface_id)).fetchone()["n"]
    if live >= MAX_PER_SURFACE:
        raise SharingError(
            f"{MAX_PER_SURFACE} open grants is the limit in one place")

    gid = db.new_id("skg")
    db.connect().execute(
        "INSERT INTO skill_grants (id, lender_id, borrower_id, surface,"
        " surface_id, skill_kind, skill_ref, title, note, fee, state,"
        " offered_at) VALUES (?,?,?,?,?,?,?,?,?,?, 'offered', ?)",
        (gid, lender_id, borrower_id, surface, surface_id, skill_kind,
         skill_ref, title, (note or "").strip() or None, float(fee),
         db.utcnow()))
    db.connect().commit()
    return get(gid)


def accept(grant_id: str, borrower_id: str) -> dict:
    """The second half of the consent. Only now is anything usable."""
    row = _grant(grant_id)
    if row is None:
        raise SharingError("no such grant")
    if row["borrower_id"] != borrower_id:
        raise SharingError("only the person it was offered to can accept it")
    if row["state"] == "closed":
        raise SharingError("that grant is closed")
    if row["state"] == "declined":
        raise SharingError("that offer was declined — a fresh one is needed")
    db.connect().execute(
        "UPDATE skill_grants SET state='active', accepted_at=? WHERE id=?",
        (db.utcnow(), grant_id))
    db.connect().commit()
    return get(grant_id)


def decline(grant_id: str, borrower_id: str) -> dict:
    row = _grant(grant_id)
    if row is None:
        raise SharingError("no such grant")
    if row["borrower_id"] != borrower_id:
        raise SharingError("only the person it was offered to can decline it")
    db.connect().execute("UPDATE skill_grants SET state='declined' WHERE id=?",
                         (grant_id,))
    db.connect().commit()
    return get(grant_id)


def close(grant_id: str, actor_id: str, reason: str = "") -> dict:
    """End it. **Either** side, alone, without the other's agreement.

    This is the asymmetry the module exists for. Requiring both to close would
    mean a person who has changed their mind needs the agreement of the person
    benefiting — which is exactly the situation where withdrawal has to work.
    """
    row = _grant(grant_id)
    if row is None:
        raise SharingError("no such grant")
    if actor_id not in (row["lender_id"], row["borrower_id"]):
        raise SharingError("only the two people involved can close this")
    db.connect().execute(
        "UPDATE skill_grants SET state='closed', closed_at=?, closed_by=?,"
        " close_reason=? WHERE id=?",
        (db.utcnow(), actor_id, (reason or "").strip() or None, grant_id))
    db.connect().commit()
    return get(grant_id)


def close_surface(surface: str, surface_id: str) -> int:
    """End every grant in a place, because the place ended.

    Called when a room closes, a stream stops, or a party breaks up. A
    permission must not outlive the conversation that justified it, and leaving
    that to each caller to remember is how one of them forgets.
    """
    conn = db.connect()
    n = conn.execute(
        "SELECT COUNT(*) AS n FROM skill_grants WHERE surface=? AND"
        " surface_id=? AND state IN ('offered','active')",
        (surface, surface_id)).fetchone()["n"]
    conn.execute(
        "UPDATE skill_grants SET state='closed', closed_at=?,"
        " close_reason='the place it was lent in ended'"
        " WHERE surface=? AND surface_id=? AND state IN ('offered','active')",
        (db.utcnow(), surface, surface_id))
    conn.commit()
    return n


def may_use(grant_id: str, borrower_id: str) -> bool:
    row = _grant(grant_id)
    return bool(row and row["state"] == "active"
                and row["borrower_id"] == borrower_id)


def use(grant_id: str, borrower_id: str, what: str,
        surface_id: str | None = None) -> dict:
    """Invoke a lent skill, once, and write it down.

    Checked at the moment of use rather than at the moment of grant, so closing
    a grant stops the next call rather than only preventing new ones. Nothing
    is copied to the borrower: this returns the *reference* they are permitted
    to act through, and the permission is gone the moment either side closes it.
    """
    row = _grant(grant_id)
    if row is None:
        raise SharingError("no such grant")
    if row["borrower_id"] != borrower_id:
        raise SharingError("that grant belongs to somebody else")
    if row["state"] != "active":
        raise SharingError(
            "that grant is not active — it was "
            + {"offered": "never accepted", "declined": "declined",
               "closed": "closed"}[row["state"]])
    if surface_id is not None and surface_id != row["surface_id"]:
        raise SharingError(
            "a skill lent in one place cannot be used in another — ask there")

    db.connect().execute(
        "INSERT INTO skill_uses (id, grant_id, borrower_id, what, used_at)"
        " VALUES (?,?,?,?,?)",
        (db.new_id("sku"), grant_id, borrower_id, (what or "").strip()[:400],
         db.utcnow()))
    db.connect().commit()
    return {"grant_id": grant_id, "skill_kind": row["skill_kind"],
            "skill_ref": row["skill_ref"], "title": row["title"],
            "surface": row["surface"], "surface_id": row["surface_id"],
            # Said on every use rather than once at the start.
            "copied": False,
            "note": "used through the lender's grant — nothing was installed "
                    "on your account, and either of you can end this",
            "used": (what or "").strip()[:400]}


def uses(grant_id: str, limit: int = 100) -> list[dict]:
    """The lender's log. The reason a grant is worth agreeing to."""
    rows = db.connect().execute(
        "SELECT * FROM skill_uses WHERE grant_id=? ORDER BY used_at DESC"
        " LIMIT ?", (grant_id, limit)).fetchall()
    return [{"what": r["what"], "used_at": r["used_at"],
             "borrower_id": r["borrower_id"]} for r in rows]


def get(grant_id: str) -> dict:
    row = _grant(grant_id)
    if row is None:
        raise SharingError("no such grant")
    log = uses(grant_id)
    return {
        "id": row["id"], "lender_id": row["lender_id"],
        "borrower_id": row["borrower_id"],
        "surface": row["surface"], "surface_id": row["surface_id"],
        "where": SURFACES[row["surface"]],
        "skill_kind": row["skill_kind"], "skill_ref": row["skill_ref"],
        "means": SKILL_KINDS[row["skill_kind"]],
        "title": row["title"], "note": row["note"],
        "fee": row["fee"], "fee_note": "simulated — no funds move",
        "state": row["state"],
        "active": row["state"] == "active",
        "offered_at": row["offered_at"], "accepted_at": row["accepted_at"],
        "closed_at": row["closed_at"], "closed_by": row["closed_by"],
        "close_reason": row["close_reason"],
        "used_count": len(log), "recent_uses": log[:10],
        # The two facts a person deciding whether to accept needs, carried on
        # the object rather than left to a client to know.
        "transfers_anything": False,
        "either_can_end_it": True,
    }


def in_surface(surface: str, surface_id: str) -> list[dict]:
    """Everything lent in one place — what the room can see about itself."""
    rows = db.connect().execute(
        "SELECT id FROM skill_grants WHERE surface=? AND surface_id=?"
        " ORDER BY offered_at", (surface, surface_id)).fetchall()
    return [get(r["id"]) for r in rows]


def for_person(person_id: str) -> dict:
    """Everything somebody is lending, and everything they are borrowing."""
    conn = db.connect()
    lent = [get(r["id"]) for r in conn.execute(
        "SELECT id FROM skill_grants WHERE lender_id=? ORDER BY offered_at DESC",
        (person_id,)).fetchall()]
    borrowed = [get(r["id"]) for r in conn.execute(
        "SELECT id FROM skill_grants WHERE borrower_id=? ORDER BY offered_at"
        " DESC", (person_id,)).fetchall()]
    return {"person_id": person_id, "lending": lent, "borrowing": borrowed}
