"""Two people agreeing, in writing, on work about to be exchanged.

Somebody comes up as a guest on a desk and it turns into business: they will
build something, review something, hand over a file. The moment that happens,
two strangers are about to send each other things — and the interesting part is
not the sending, it is the **agreeing**, because that is where every dispute
comes from and where the platform can actually help.

So an exchange is a document before it is a transfer. One side proposes; the
document names, item by item:

* **what is going across, in each direction** — every artifact listed with its
  kind and its size, so *what am I about to receive* is a list rather than an
  assurance;
* **what the work is** — one plain sentence, and the industry it belongs to;
* **what is included when it is finished** — the deliverables, which is the
  clause people actually argue about afterwards;
* **what is not included** — stated, because an absent exclusion reads as an
  inclusion to whoever paid.

Then both sides sign, and only then does anything move.

Four rules make that more than a form.

**Neither side's signature alone opens anything.** :func:`channel` returns
nothing until both have signed. A one-sided agreement is not an agreement.

**Any change to the manifest voids both signatures.** This is the rule the
whole design turns on: without it, you agree to a two-item manifest and the
other side appends to it afterwards, and your signature is on a document you
never read. Adding, removing or editing an item drops the exchange back to
``draft`` and both parties sign again. It is meant to be annoying.

**Nothing downloads by itself.** A signed exchange makes each item *available*;
the receiving side accepts them one at a time (:func:`accept_item`). Consent to
an agreement is not consent to a file landing on your disk.

**This is not remote access to anybody's device**, and that limit is in the
code rather than in a warning. An exchange moves named artifacts that somebody
attached; it opens no session, runs nothing, and reaches nothing that was not
listed. "Hook my machine up to theirs" is a different feature with a different
threat model, and quietly shipping it inside a file-sharing agreement would be
the wrong way to arrive at it.

Money stays simulated, as everywhere else here: a fee is recorded on the
statement and no funds move.
"""

from __future__ import annotations

import hashlib
import json

from . import db

MAX_ITEMS = 40
MAX_TEXT = 400
MAX_NAME = 160

# The industries an exchange can belong to. Open enough to cover the work
# people actually bring to a desk, closed enough that "industry" stays a field
# somebody can group and audit by rather than free text.
INDUSTRIES: tuple[str, ...] = (
    "software", "design", "writing", "audio", "video", "photography",
    "engineering", "trades", "finance", "legal", "healthcare", "education",
    "marketing", "research", "manufacturing", "other",
)

# What an item *is*. The kind is not decoration: `source` and `build` are
# things that run on the receiving machine if anybody double-clicks them, and
# a surface should be able to say so without inspecting a filename.
KINDS: dict[str, str] = {
    "document": "a document — read it",
    "image": "an image",
    "audio": "an audio file",
    "video": "a video file",
    "archive": "an archive — a bundle of files",
    "source": "source code — it is text, and it is meant to be run",
    "build": "a compiled build — it runs, and you cannot read it first",
    "data": "a data file",
    "model": "a trained model or weights",
    "link": "a link to something hosted elsewhere",
}

# States, in order. `draft` is the only one you can edit in.
STATES = ("draft", "proposed", "signed", "delivered", "closed", "withdrawn")

# The sentence a receiving side reads before accepting anything that executes.
RUNS_WARNING = ("this item runs on your machine — a signature on an agreement "
                "is not a review of what the code does")


class ExchangeError(ValueError):
    """An exchange that cannot stand."""


def _row(exchange_id: str):
    return db.connect().execute("SELECT * FROM exchanges WHERE id=?",
                                (exchange_id,)).fetchone()


def _items(exchange_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM exchange_items WHERE exchange_id=? ORDER BY rowid",
        (exchange_id,)).fetchall()
    return [{"id": r["id"], "direction": r["direction"], "name": r["name"],
             "kind": r["kind"], "bytes": r["bytes"], "note": r["note"],
             "accepted_at": r["accepted_at"],
             "runs": r["kind"] in ("source", "build")} for r in rows]


def fingerprint(exchange_id: str) -> str:
    """A hash of exactly what the parties are agreeing to.

    Signatures are stored against this rather than against the exchange's id,
    which is what makes "any change voids the signatures" a fact about the data
    instead of a promise about the code: after an edit the fingerprint differs,
    so the old signatures no longer match anything.
    """
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    body = {
        "work": row["work"], "industry": row["industry"],
        "includes": json.loads(row["includes"] or "[]"),
        "excludes": json.loads(row["excludes"] or "[]"),
        "fee": row["fee"],
        "items": [{k: it[k] for k in ("direction", "name", "kind", "bytes")}
                  for it in _items(exchange_id)],
    }
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def propose(host_id: str, guest_id: str, work: str, industry: str,
            includes: list[str] | None = None,
            excludes: list[str] | None = None,
            fee: float = 0.0, desk_id: str | None = None) -> dict:
    """Start the document. Nothing is exchangeable yet."""
    work = (work or "").strip()
    if not work:
        raise ExchangeError("say what the work is, in one sentence")
    if len(work) > MAX_TEXT:
        raise ExchangeError(f"the work description is at most {MAX_TEXT} characters")
    if industry not in INDUSTRIES:
        raise ExchangeError(
            f"unknown industry {industry!r}; expected one of "
            f"{', '.join(INDUSTRIES)}")
    if host_id == guest_id:
        raise ExchangeError("an exchange needs two parties")
    if fee < 0:
        raise ExchangeError("a fee cannot be negative")

    xid = db.new_id("xch")
    db.connect().execute(
        "INSERT INTO exchanges (id, desk_id, host_id, guest_id, work,"
        " industry, includes, excludes, fee, state, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,'draft',?)",
        (xid, desk_id, host_id, guest_id, work, industry,
         json.dumps(list(includes or [])), json.dumps(list(excludes or [])),
         float(fee), db.utcnow()))
    db.connect().commit()
    return get(xid)


def add_item(exchange_id: str, direction: str, name: str, kind: str,
             size_bytes: int = 0, note: str = "") -> dict:
    """List one thing that will cross. Only while the document is editable.

    ``direction`` is ``host_to_guest`` or ``guest_to_host`` — an exchange is
    two-way, and a manifest that could not say which way an item goes would be
    unable to describe the ordinary case of somebody sending files in and
    getting work back.
    """
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    if row["state"] != "draft":
        raise ExchangeError(
            "this exchange is not editable — reopen it to change the manifest, "
            "which clears both signatures")
    if direction not in ("host_to_guest", "guest_to_host"):
        raise ExchangeError("direction is host_to_guest or guest_to_host")
    if kind not in KINDS:
        raise ExchangeError(
            f"unknown kind {kind!r}; expected one of {', '.join(KINDS)}")
    name = (name or "").strip()
    if not name:
        raise ExchangeError("every item needs a name the other side will read")
    if len(name) > MAX_NAME:
        raise ExchangeError(f"an item name is at most {MAX_NAME} characters")
    if size_bytes < 0:
        raise ExchangeError("a size cannot be negative")
    n = db.connect().execute(
        "SELECT COUNT(*) AS n FROM exchange_items WHERE exchange_id=?",
        (exchange_id,)).fetchone()["n"]
    if n >= MAX_ITEMS:
        raise ExchangeError(
            f"{MAX_ITEMS} items is the limit — a manifest nobody reads is not "
            f"consent")

    db.connect().execute(
        "INSERT INTO exchange_items (id, exchange_id, direction, name, kind,"
        " bytes, note, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (db.new_id("xit"), exchange_id, direction, name, kind,
         int(size_bytes), (note or "").strip() or None, db.utcnow()))
    db.connect().commit()
    return get(exchange_id)


def remove_item(exchange_id: str, item_id: str) -> dict:
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    if row["state"] != "draft":
        raise ExchangeError("reopen the exchange to change the manifest")
    db.connect().execute("DELETE FROM exchange_items WHERE id=? AND"
                         " exchange_id=?", (item_id, exchange_id))
    db.connect().commit()
    return get(exchange_id)


def reopen(exchange_id: str, actor_id: str) -> dict:
    """Put a signed exchange back into draft, clearing both signatures.

    Deliberately the only way to change an agreed manifest. Either party can do
    it — being able to edit unilaterally would be the hole, and *not* being able
    to reopen would mean a typo needs a whole new exchange.
    """
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    if actor_id not in (row["host_id"], row["guest_id"]):
        raise ExchangeError("only the two parties can reopen this")
    if row["state"] in ("closed", "withdrawn"):
        raise ExchangeError("this exchange is finished")
    conn = db.connect()
    conn.execute("DELETE FROM exchange_signatures WHERE exchange_id=?",
                 (exchange_id,))
    conn.execute("UPDATE exchanges SET state='draft' WHERE id=?",
                 (exchange_id,))
    conn.commit()
    return get(exchange_id)


def sign(exchange_id: str, actor_id: str) -> dict:
    """Agree to exactly this manifest.

    The signature records the fingerprint it was made against, so a signature
    can be checked rather than trusted — and an edit leaves both of them
    pointing at a document that no longer exists.
    """
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    if actor_id not in (row["host_id"], row["guest_id"]):
        raise ExchangeError("only the two parties can sign this")
    if row["state"] in ("closed", "withdrawn"):
        raise ExchangeError("this exchange is finished")
    if not _items(exchange_id):
        raise ExchangeError(
            "there is nothing on the manifest — an empty agreement agrees to "
            "nothing in particular, which is the state people sign by accident")

    fp = fingerprint(exchange_id)
    conn = db.connect()
    conn.execute(
        "INSERT INTO exchange_signatures (exchange_id, party_id, fingerprint,"
        " signed_at) VALUES (?,?,?,?)"
        " ON CONFLICT(exchange_id, party_id) DO UPDATE SET fingerprint=excluded"
        ".fingerprint, signed_at=excluded.signed_at",
        (exchange_id, actor_id, fp, db.utcnow()))
    conn.commit()
    state = "signed" if _both_signed(exchange_id) else "proposed"
    conn.execute("UPDATE exchanges SET state=? WHERE id=?", (state, exchange_id))
    conn.commit()
    return get(exchange_id)


def _both_signed(exchange_id: str) -> bool:
    row = _row(exchange_id)
    fp = fingerprint(exchange_id)
    signed = {r["party_id"] for r in db.connect().execute(
        "SELECT party_id FROM exchange_signatures WHERE exchange_id=? AND"
        " fingerprint=?", (exchange_id, fp)).fetchall()}
    return {row["host_id"], row["guest_id"]} <= signed


def channel(exchange_id: str) -> dict:
    """Whether anything may move, and what.

    The one function a transport layer should ask. It reports ``open`` only
    when both parties have signed *the current* manifest — so a stale signature
    is the same as no signature, without anything having to remember to clear
    it.
    """
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    if row["state"] == "withdrawn":
        return {"open": False, "reason": "withdrawn"}
    if not _both_signed(exchange_id):
        missing = _unsigned(exchange_id)
        return {"open": False,
                "reason": "waiting on a signature for this exact manifest",
                "unsigned": missing}
    return {
        "open": True,
        "items": _items(exchange_id),
        "fingerprint": fingerprint(exchange_id),
        # Said here rather than left to a client to infer: an open channel is
        # permission to offer these items, not permission to place them.
        "auto_download": False,
        "note": "each item is accepted separately — nothing arrives on its own",
    }


def _unsigned(exchange_id: str) -> list[str]:
    row = _row(exchange_id)
    fp = fingerprint(exchange_id)
    signed = {r["party_id"] for r in db.connect().execute(
        "SELECT party_id FROM exchange_signatures WHERE exchange_id=? AND"
        " fingerprint=?", (exchange_id, fp)).fetchall()}
    return [p for p in (row["host_id"], row["guest_id"]) if p not in signed]


def accept_item(exchange_id: str, item_id: str, actor_id: str) -> dict:
    """Take delivery of one listed item.

    Per item, and only by the side receiving it. This is the step that makes
    "nothing downloads by itself" true of the system rather than of the client:
    a signed agreement leaves every item still waiting.
    """
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    if not _both_signed(exchange_id):
        raise ExchangeError(
            "nothing can be accepted until both parties have signed this "
            "manifest")
    item = db.connect().execute(
        "SELECT * FROM exchange_items WHERE id=? AND exchange_id=?",
        (item_id, exchange_id)).fetchone()
    if item is None:
        raise ExchangeError("no such item on this manifest")
    receiver = (row["guest_id"] if item["direction"] == "host_to_guest"
                else row["host_id"])
    if actor_id != receiver:
        raise ExchangeError(
            "only the side receiving an item can accept it — the sender "
            "cannot accept on their behalf")
    db.connect().execute(
        "UPDATE exchange_items SET accepted_at=? WHERE id=?",
        (db.utcnow(), item_id))
    db.connect().commit()
    if all(i["accepted_at"] for i in _items(exchange_id)):
        db.connect().execute("UPDATE exchanges SET state='delivered' WHERE id=?",
                             (exchange_id,))
        db.connect().commit()
    return get(exchange_id)


def withdraw(exchange_id: str, actor_id: str) -> dict:
    """Either side can walk away. Nothing further moves."""
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    if actor_id not in (row["host_id"], row["guest_id"]):
        raise ExchangeError("only the two parties can withdraw this")
    db.connect().execute("UPDATE exchanges SET state='withdrawn' WHERE id=?",
                         (exchange_id,))
    db.connect().commit()
    return get(exchange_id)


def get(exchange_id: str) -> dict:
    row = _row(exchange_id)
    if row is None:
        raise ExchangeError("no such exchange")
    items = _items(exchange_id)
    sigs = [{"party_id": r["party_id"], "signed_at": r["signed_at"],
             "matches_current": r["fingerprint"] == fingerprint(exchange_id)}
            for r in db.connect().execute(
                "SELECT * FROM exchange_signatures WHERE exchange_id=?",
                (exchange_id,)).fetchall()]
    return {
        "id": row["id"], "desk_id": row["desk_id"],
        "host_id": row["host_id"], "guest_id": row["guest_id"],
        "work": row["work"], "industry": row["industry"],
        "includes": json.loads(row["includes"] or "[]"),
        "excludes": json.loads(row["excludes"] or "[]"),
        "fee": row["fee"], "fee_note": "simulated — no funds move",
        "state": row["state"], "created_at": row["created_at"],
        "items": items,
        "runs_on_your_machine": [i["name"] for i in items if i["runs"]],
        "runs_warning": RUNS_WARNING if any(i["runs"] for i in items) else None,
        "fingerprint": fingerprint(exchange_id),
        "signatures": sigs,
        "unsigned": _unsigned(exchange_id),
        "channel": channel(exchange_id),
        # The boundary, carried with the object rather than left in the docs.
        "grants": "the listed items, once accepted",
        "does_not_grant": "access to either device, or anything not listed",
    }


def for_party(party_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM exchanges WHERE host_id=? OR guest_id=?"
        " ORDER BY created_at DESC", (party_id, party_id)).fetchall()
    return [get(r["id"]) for r in rows]
