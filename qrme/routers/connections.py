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

from fastapi import APIRouter, HTTPException

from .. import db, moderation
from ..common import age_of, interactor_or_404
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


@router.post("/connections/join")
def join_queue(body: ConnectionJoin) -> dict:
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


@router.post("/connections/{connection_id}/messages", status_code=201)
def send_message(connection_id: str, body: ConnectionMessage) -> dict:
    connection = _connection_or_404(connection_id)
    _participant(connection, body.interactor_id)
    if connection["status"] != "active":
        raise HTTPException(410, "this connection has ended")

    other_id = (connection["interactor_b"]
                if body.interactor_id == connection["interactor_a"]
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
        (message_id, connection_id, body.interactor_id, body.message,
         "approved" if verdict.approved else "blocked", verdict.reason,
         db.utcnow()),
    )
    conn.commit()
    return {"id": message_id,
            "status": "approved" if verdict.approved else "blocked",
            "flag_reason": verdict.reason}


@router.get("/connections/{connection_id}/messages")
def read_messages(connection_id: str, interactor_id: str) -> list[dict]:
    connection = _connection_or_404(connection_id)
    _participant(connection, interactor_id)
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
def end_connection(connection_id: str, body: ConnectionMessage | None = None,
                   interactor_id: str | None = None) -> dict:
    connection = _connection_or_404(connection_id)
    ender = interactor_id or (body.interactor_id if body else None)
    if ender:
        _participant(connection, ender)
    conn = db.connect()
    conn.execute("UPDATE connections SET status='ended' WHERE id=?",
                 (connection_id,))
    conn.commit()
    return {"id": connection_id, "status": "ended"}
