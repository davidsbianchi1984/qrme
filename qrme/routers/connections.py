"""User-to-user connections: anonymous chat between interactors.

Two tiers, both consent-first:

- ``friendly`` — open matchmaking for platonic conversation; minors are
  always held to the strict moderation filter.
- ``rated`` — adult chat; **both** parties must be age-verified 18+ to even
  join the queue, and the pair's messages run under the ``open`` filter.

Matching is anonymous by design: participants see each other's chosen alias
(or a neutral "Stranger"), never a display name or id. Either side can end
the connection at any time, and a flagged message is blocked — stored for
the sender's record but never shown to the other person.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Request

from .. import auth, db, moderation
from ..common import age_of, interactor_or_404, require_interactor
from ..models import ConnectionJoin, ConnectionMessage

router = APIRouter()


def _is_adult(interactor: dict) -> bool:
    return bool(interactor["birthdate"]) and age_of(
        date.fromisoformat(interactor["birthdate"])) >= 18


def _connection_or_404(connection_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM connections WHERE id=?", (connection_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "connection not found")
    return dict(row)


def _participant(connection: dict, interactor_id: str) -> None:
    if interactor_id not in (connection["interactor_a"],
                             connection["interactor_b"]):
        raise HTTPException(403, "not a participant in this connection")


def _speaker(connection_id: str, request: Request) -> tuple[dict, str]:
    """Who is calling, and the connection they are in.

    The id in the request body says *whose turn this is meant to be*. It never
    said who was asking, and nothing here checked — so a stranger holding two
    public ids could speak as either party, read the whole conversation as
    them (including the blocked messages kept back for their eyes only), and
    end it.

    This is the room defect over again. `community._require_in_room` already
    settles it for rooms in the same words: an id is a claim, and the token is
    the answer.
    """
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["role"] != "interactor":
        raise HTTPException(
            403, "a connection is between two people, so this needs the token "
                 "of one of them rather than a profile's owner token")
    connection = _connection_or_404(connection_id)
    _participant(connection, who["subject_id"])
    return connection, who["subject_id"]


@router.post("/connections/join")
def join_queue(body: ConnectionJoin, request: Request) -> dict:
    # You may queue as yourself. Anyone could queue as anybody, which meant a
    # stranger could put a real person into matchmaking and be paired with
    # somebody under that person's name — and, on the rated tier, borrow an
    # adult's id to get past the age check below.
    require_interactor(body.interactor_id, request)
    interactor = interactor_or_404(body.interactor_id)
    if body.tier == "rated" and not _is_adult(interactor):
        raise HTTPException(
            403, "the rated tier requires verified 18+ participants")

    conn = db.connect()
    alias = body.alias or "Stranger"
    # A waiting partner in the same tier? Match immediately.
    partner = conn.execute(
        "SELECT * FROM connection_queue WHERE tier=? AND interactor_id != ?"
        " ORDER BY created_at, rowid LIMIT 1",
        (body.tier, body.interactor_id)).fetchone()
    if partner:
        connection_id = db.new_id("con")
        conn.execute("DELETE FROM connection_queue WHERE interactor_id=?",
                     (partner["interactor_id"],))
        conn.execute(
            "INSERT INTO connections (id, interactor_a, interactor_b, tier,"
            " alias_a, alias_b, status, created_at)"
            " VALUES (?,?,?,?,?,?,'active',?)",
            (connection_id, partner["interactor_id"], body.interactor_id,
             body.tier, partner["alias"] or "Stranger", alias, db.utcnow()),
        )
        conn.commit()
        return {"status": "matched", "connection_id": connection_id,
                "tier": body.tier,
                "matched_with": partner["alias"] or "Stranger"}

    conn.execute(
        "INSERT OR REPLACE INTO connection_queue (interactor_id, tier, alias,"
        " created_at) VALUES (?,?,?,?)",
        (body.interactor_id, body.tier, alias, db.utcnow()),
    )
    conn.commit()
    return {"status": "waiting", "tier": body.tier}


@router.get("/connections/mine")
def my_connection(request: Request) -> dict:
    """What happened to my wait — the half of matchmaking join can't say.

    A match is made by whichever side arrives *second*: their join deletes
    the waiter's queue row and creates the connection, and the waiter is
    never told. The consoles read "waiting for a partner" forever while the
    partner was already in the room talking to nobody. A field report asked
    for roulette — "just drop you with the next available person that's
    already in" — and the drop needs this: something a waiting client can
    poll that answers matched, still waiting, or neither.

    Re-calling join would be the wrong poll. It re-queues the caller, so two
    people both polling that way can be paired with each other twice.

    Token only, no id in the path or query — "mine" is whoever the token
    says, which is the one question a stranger can't answer.
    """
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["role"] != "interactor":
        raise HTTPException(
            403, "a connection is between two people, so this needs the token "
                 "of one of them rather than a profile's owner token")
    me = who["subject_id"]
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM connections WHERE status='active'"
        " AND (interactor_a=? OR interactor_b=?)"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1", (me, me)).fetchone()
    if row:
        other_alias = (row["alias_b"] if me == row["interactor_a"]
                       else row["alias_a"])
        return {"status": "matched", "connection_id": row["id"],
                "tier": row["tier"],
                "matched_with": other_alias or "Stranger"}
    queued = conn.execute(
        "SELECT tier FROM connection_queue WHERE interactor_id=?",
        (me,)).fetchone()
    if queued:
        return {"status": "waiting", "tier": queued["tier"]}
    return {"status": "idle"}


@router.post("/connections/{connection_id}/messages", status_code=201)
def send_message(connection_id: str, body: ConnectionMessage,
                 request: Request) -> dict:
    # `body.interactor_id` stays on the model and is ignored: three shipped
    # native clients send it, and a 422 on upgrade is a worse answer than not
    # believing it. The speaker is the token.
    connection, speaker = _speaker(connection_id, request)
    if connection["status"] != "active":
        raise HTTPException(410, "this connection has ended")

    other_id = (connection["interactor_b"]
                if speaker == connection["interactor_a"]
                else connection["interactor_a"])
    recipient = interactor_or_404(other_id)
    # Rated pairs are both verified adults → open filter; friendly pairs run
    # balanced, and a minor recipient is always held to strict.
    maturity = "open" if connection["tier"] == "rated" else "balanced"
    verdict = moderation.review(body.message, None, recipient,
                                maturity=maturity)

    conn = db.connect()
    message_id = db.new_id("cmg")
    conn.execute(
        "INSERT INTO connection_messages (id, connection_id, sender_id,"
        " content, status, flag_reason, created_at) VALUES (?,?,?,?,?,?,?)",
        (message_id, connection_id, speaker, body.message,
         "approved" if verdict.approved else "blocked", verdict.reason,
         db.utcnow()),
    )
    conn.commit()
    return {"id": message_id,
            "status": "approved" if verdict.approved else "blocked",
            "flag_reason": verdict.reason}


@router.get("/connections/{connection_id}/messages")
def read_messages(connection_id: str, request: Request,
                  interactor_id: str | None = None) -> list[dict]:
    """The conversation, as one of the two people in it.

    `interactor_id` rides in the query string and is ignored — three shipped
    clients send it. Reading it was how a stranger got the whole thing,
    including the blocked messages this route keeps back for their sender's
    eyes alone, which is a rule that means nothing if anyone can claim to be
    the sender.
    """
    connection, interactor_id = _speaker(connection_id, request)
    aliases = {connection["interactor_a"]: connection["alias_a"],
               connection["interactor_b"]: connection["alias_b"]}
    rows = db.connect().execute(
        "SELECT * FROM connection_messages WHERE connection_id=?"
        " ORDER BY created_at, rowid", (connection_id,)).fetchall()
    out = []
    for row in rows:
        mine = row["sender_id"] == interactor_id
        # Blocked messages are visible only to their sender.
        if row["status"] == "blocked" and not mine:
            continue
        out.append({"id": row["id"],
                    "from": "you" if mine else aliases[row["sender_id"]],
                    "content": row["content"], "status": row["status"],
                    "created_at": row["created_at"]})
    return out


@router.post("/connections/{connection_id}/end")
def end_connection(connection_id: str, request: Request,
                   body: ConnectionMessage | None = None,
                   interactor_id: str | None = None) -> dict:
    """Either side may end it. *Either side* — not anybody.

    The check was `if ender: _participant(...)`, and `ender` came from an
    optional body and an optional query parameter. So sending neither skipped
    the check entirely: a bare POST with no id and no token ended a stranger's
    conversation, and the wearable lent inside it came back with it.
    """
    _connection, _ender = _speaker(connection_id, request)
    conn = db.connect()
    conn.execute("UPDATE connections SET status='ended' WHERE id=?",
                 (connection_id,))
    conn.commit()
    # Ending the connection returns any wearable lent inside it. The
    # permission was scoped to this conversation and must not survive it.
    from .. import roommic
    returned = roommic.close_place("connection", connection_id)
    return {"id": connection_id, "status": "ended",
            "microphones_returned": returned}
