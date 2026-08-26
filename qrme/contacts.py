"""The people in a person's phone — QRME's half of the estate's address book.

The ask, in its owner's words: *there's no address book when users create
connections — allowing JIM or the agent or synthetic profiles access to
Contacts and messages and phone... some people might not have JIM-mini and
only have QRME.* JIM grew its half first (`jim/contacts.py`); this is the
other one, because plenty of people hold one product and not the other, and
a grant that only exists in the product somebody does not have is a grant
they cannot give.

Two corrections from that round are load-bearing here as much as there:

* the book is a **synced source, never something people type** — it arrives
  from the device under a grant, and a replace is the only write;
* the grant belongs to the **person** (the interactor), never to a profile.
  Most of what is in an address book is somebody else, which is why the
  grant is off until chosen and withdrawal drops the book rather than
  stopping the sync.

The design is JIM's, deliberately, so the estate holds one shape:

* :func:`allowed` is the chokepoint — one function, so the book cannot be
  read by a path that forgot to ask;
* :func:`sync` replaces; a merge would quietly keep people the person
  deleted from their phone months ago;
* the number's recognisable **tail** is all that is kept, and nothing here
  ever returns it — the phone already has the numbers;
* the book is sealed into PDI where the person's plan has a vault and held
  in platform custody otherwise — `storage.vault_for`, asked about the
  plan, in the shape every seal point in this codebase asks it. One book
  and one withdrawal either way, and **never both**: a plan change between
  two syncs must not leave two books with two ideas of who somebody knows;
* a sealed book with no vault to hand **raises** — *you know nobody* and
  *I could not open your book* are different sentences and only one of
  them is true.

What is deliberately NOT here: a reader for the agent or a profile. A
synthetic profile that can leaf through its owner's contacts is an act that
reaches people who never chose it (`privileges.Privilege.touches_others`
names the cost), and it becomes a roster row the day something actually
consumes it — a promise on the roster with no act behind it is the defect
the roster exists to prevent. :func:`whose` is the one reader, takes a
number, answers with a name or nothing, and writes nothing down.
"""

from __future__ import annotations

import json
import re

from . import db, i18n, storage, tiers

#: How much of a number is enough to recognise somebody by. The same nine
#: digits JIM settled on: two numbers in different countries can share a
#: tail, and the consequence is a wrong NAME, never a wrong grant — nothing
#: in this module opens anything on the strength of a match.
TAIL = 9


def digits(number: str | None) -> str:
    """The recognisable tail, from however the device formatted it."""
    only = re.sub(r"\D", "", number or "")
    return only[-TAIL:]


class NotGranted(RuntimeError):
    """Refused: this person has not let anything see their contacts."""


#: The refusal, naming what it would reach rather than a config word —
#: *the people in your phone* is the thing somebody is deciding about.
NOT_GRANTED = ("nothing here can see the people in your phone: turn on "
               "contacts in what may be seen of you. It is off until you "
               "do, because most of what is in there is somebody else")


class VaultUnreachable(RuntimeError):
    """The book is sealed and the vault it is sealed into was not supplied."""


class NoSuchContact(RuntimeError):
    """Asked for a contact this book does not hold."""


def granted(interactor_id: str) -> bool:
    row = db.connect().execute(
        "SELECT consented FROM contact_grants WHERE interactor_id=?",
        (interactor_id,)).fetchone()
    return bool(row and row["consented"])


def allowed(interactor_id: str) -> None:
    """The chokepoint. Refuse unless this person granted the source."""
    if not granted(interactor_id):
        raise NotGranted(NOT_GRANTED)


def decide(interactor_id: str, consented: bool, pdi=None) -> dict:
    """The grant's one switch — and withdrawal drops the book, both
    custodies, right here. Nobody should have to find a second control to
    make the first one mean what it says."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO contact_grants (interactor_id, consented, decided_at)"
        " VALUES (?,?,?) ON CONFLICT(interactor_id) DO UPDATE SET"
        " consented=excluded.consented, decided_at=excluded.decided_at",
        (interactor_id, 1 if consented else 0, db.utcnow()))
    conn.commit()
    if not consented:
        _clear(interactor_id, pdi)
    return {"consented": consented}


def _sealed(interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM contact_books WHERE interactor_id=?",
        (interactor_id,)).fetchone()
    return dict(row) if row else None


def _key(interactor_id: str) -> str:
    return f"qrme/{interactor_id}/contacts/book"


def _rows(interactor_id: str, pdi) -> list[dict]:
    """This person's book, from wherever it is — the one reader, so nothing
    above it branches on where the book happens to live."""
    book = _sealed(interactor_id)
    if book is None:
        return [dict(r) for r in db.connect().execute(
            "SELECT * FROM contacts WHERE interactor_id=? ORDER BY name"
            " COLLATE NOCASE", (interactor_id,)).fetchall()]
    if pdi is None:
        raise VaultUnreachable(
            "this book is sealed into the vault and no vault was supplied")
    raw = pdi.get(book["vault_key"])
    if raw is None:
        raise VaultUnreachable("the sealed book is not in the vault")
    rows = json.loads(raw)
    return sorted(rows, key=lambda r: (r.get("name") or "").casefold())


def _clear(interactor_id: str, pdi) -> None:
    """Drop the book from BOTH custodies, whatever the plan says today."""
    book = _sealed(interactor_id)
    conn = db.connect()
    conn.execute("DELETE FROM contacts WHERE interactor_id=?",
                 (interactor_id,))
    conn.execute("DELETE FROM contact_books WHERE interactor_id=?",
                 (interactor_id,))
    conn.commit()
    if book is not None and pdi is not None:
        try:
            pdi.delete(book["vault_key"])
        except Exception:
            # The index row is gone, so nothing will read it again; a vault
            # that refused the delete is not worth leaving it pointing at.
            pass


def sync(interactor_id: str, entries: list[dict], pdi=None) -> dict:
    """Replace the book with what the device has — the only write.

    Entries carry too little number to recognise anybody are skipped rather
    than refused: a real address book has half-rows in it. The plan question
    is asked here, of `tiers.plan_of_interactor`, because the old book has
    to be cleared from the side the PREVIOUS plan used before the new one
    is written to the side the current plan says.
    """
    allowed(interactor_id)
    seen: dict[str, dict] = {}
    skipped = 0
    for entry in entries:
        name = (entry.get("name") or "").strip()
        tail = digits(entry.get("number") or "")
        if not name or len(tail) < 7:
            skipped += 1
            continue
        seen[tail] = {"name": name, "peer_id": entry.get("peer_id")}

    now = db.utcnow()
    rows = [{"id": db.new_id("con"), "interactor_id": interactor_id,
             "name": row["name"], "digits": tail, "peer_id": row["peer_id"],
             "added_at": now}
            for tail, row in seen.items()]

    # Both sides first, then one side. Never both at once.
    _clear(interactor_id, pdi)

    vault = storage.vault_for(tiers.plan_of_interactor(interactor_id), pdi)
    conn = db.connect()
    if vault is None:
        conn.executemany(
            "INSERT INTO contacts (id, interactor_id, name, digits, peer_id,"
            " added_at) VALUES (?,?,?,?,?,?)",
            [(r["id"], interactor_id, r["name"], r["digits"], r["peer_id"],
              r["added_at"]) for r in rows])
    else:
        key = _key(interactor_id)
        vault.put(key, json.dumps(rows))
        conn.execute(
            "INSERT INTO contact_books (interactor_id, vault_key, held,"
            " sealed_at) VALUES (?,?,?,?)",
            (interactor_id, key, len(rows), now))
    conn.commit()
    return {"held": len(seen), "skipped": skipped,
            "sealed": vault is not None}


def withdrawn(interactor_id: str, pdi=None) -> dict:
    """The grant came off. Drop the book — not "stop syncing", drop it."""
    _clear(interactor_id, pdi)
    return {"held": 0}


def _seen(row) -> dict:
    """A contact as anybody reads it: a name, and whether a shell matched
    them to an account here. The digits do not come back out."""
    return {"id": row["id"], "name": row["name"],
            "holds_account": row["peer_id"] is not None,
            "added_at": row["added_at"]}


def book(interactor_id: str, pdi=None) -> list[dict]:
    """Everybody in the synced book, by name."""
    allowed(interactor_id)
    return [_seen(r) for r in _rows(interactor_id, pdi)]


def held(interactor_id: str) -> int:
    """How many, without opening anything sealed."""
    sealed = _sealed(interactor_id)
    if sealed is not None:
        return sealed["held"]
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM contacts WHERE interactor_id=?",
        (interactor_id,)).fetchone()["n"]


def whose(interactor_id: str, number: str | None, pdi=None) -> dict | None:
    """Which of this person's own contacts a number belongs to, if any.

    The recognition door, and the only one. It never writes, so a number
    that matches nobody leaves exactly as little behind as it did before
    this module existed. Refuses without the grant, like every reader.
    """
    allowed(interactor_id)
    tail = digits(number)
    if len(tail) < 7:
        return None
    row = next((r for r in _rows(interactor_id, pdi)
                if r["digits"] == tail), None)
    return _seen(row) if row else None
