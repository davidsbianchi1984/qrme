"""Community layer: rooms, marketplace listings, providers, and handoffs.

- **Rooms** — multiparty conversations over any channel (chat, voice, video,
  AR, VR) whose participants may be any mix of real users and synthetic
  profiles: user↔user, profile↔profile, or combinations. Every profile turn
  passes moderation; a room with a minor present always runs strict.
- **Listings** — the marketplace, generalized: users and businesses can
  share and market synthetic profiles, content, business expertise, or
  services, browsable by kind, tag, and area.
- **Providers & handoffs** — a directory of real local businesses
  (healthcare, medical, mental health, finance, relationships, career, …)
  and a *consented* handoff: the AI specialist's session summary is packaged,
  sealed in the PDI vault when configured, and released to the provider only
  through a revocable access token.
"""

from __future__ import annotations

import json
import secrets
from datetime import date

from fastapi import APIRouter, HTTPException, Request

from .. import db, engagement, llm, moderation, persona
from ..common import age_of, interactor_or_404, profile_or_404, source_items
from ..models import (
    HandoffCreate, ListingCreate, ProviderCreate, RoomCreate, RoomMessage,
)

router = APIRouter()

_CHANNEL_NOTES = {
    "chat": "text thread",
    "voice": "live voice; replies rendered in each speaker's voice style",
    "video": "live video call; profiles present as animated avatars",
    "ar": "shared augmented-reality space anchored to the room's location",
    "vr": "shared virtual-reality space; participants meet as avatars",
}


# --------------------------------------------------------------------------- #
# rooms
# --------------------------------------------------------------------------- #

def _room_or_404(room_id: str) -> dict:
    row = db.connect().execute("SELECT * FROM rooms WHERE id=?",
                               (room_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "room not found")
    return dict(row)


def _participants(room_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT kind, ref_id FROM room_participants WHERE room_id=?",
        (room_id,)).fetchall()
    return [dict(r) for r in rows]


def _room_maturity(participants: list[dict]) -> str:
    """A room with a minor present always runs strict."""
    for p in participants:
        if p["kind"] != "user":
            continue
        user = interactor_or_404(p["ref_id"])
        if not user["birthdate"] or age_of(
                date.fromisoformat(user["birthdate"])) < 18:
            return "strict"
    return "balanced"


def _display(kind: str, ref_id: str) -> str:
    if kind == "profile":
        profile = profile_or_404(ref_id)
        return ("anonymous persona" if profile["anonymous"]
                else profile["display_name"])
    return interactor_or_404(ref_id)["display_name"]


def _store_room_message(room_id, sender_kind, sender_id, content,
                        approved, reason) -> dict:
    conn = db.connect()
    message_id = db.new_id("rmg")
    conn.execute(
        "INSERT INTO room_messages (id, room_id, sender_kind, sender_id,"
        " content, status, flag_reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (message_id, room_id, sender_kind, sender_id, content,
         "approved" if approved else "blocked", reason, db.utcnow()),
    )
    conn.commit()
    return {"id": message_id, "sender_kind": sender_kind,
            "from": _display(sender_kind, sender_id),
            "content": content if approved else None,
            "status": "approved" if approved else "blocked"}


def _profile_turns(room: dict, participants: list[dict], pdi, cloud) -> list[dict]:
    """Every profile participant takes one moderated turn."""
    maturity = _room_maturity(participants)
    conn = db.connect()
    produced = []
    for participant in participants:
        if participant["kind"] != "profile":
            continue
        profile = profile_or_404(participant["ref_id"])
        if profile["status"] == "departed":
            continue
        history = conn.execute(
            "SELECT sender_kind, sender_id, content FROM room_messages"
            " WHERE room_id=? AND status='approved'"
            " ORDER BY created_at DESC, rowid DESC LIMIT 12",
            (room["id"],)).fetchall()
        turns = [
            {"role": ("assistant" if (r["sender_kind"] == "profile"
                                      and r["sender_id"] == profile["id"])
                      else "user"),
             "content": r["content"]}
            for r in reversed(history)
        ] or [{"role": "user", "content": f"Let's talk about {room['topic']}."}]
        system = persona.build_system_prompt(
            profile, None, None, sources=source_items(profile["id"], pdi))
        system += (f"\n\nYou are in a group {room['channel']} room about: "
                   f"{room['topic']} ({_CHANNEL_NOTES[room['channel']]}). "
                   "Reply with one short, in-character turn.")
        content = llm.get_provider(cloud=cloud).generate(system, turns)
        verdict = moderation.review(content, None, {"birthdate": None},
                                    maturity=maturity)
        produced.append(_store_room_message(
            room["id"], "profile", profile["id"], content,
            verdict.approved, verdict.reason))
    return produced


@router.post("/rooms", status_code=201)
def create_room(body: RoomCreate) -> dict:
    conn = db.connect()
    for participant in body.participants:
        if participant.kind == "profile":
            profile = profile_or_404(participant.id)
            if profile["status"] == "departed":
                raise HTTPException(410, f"profile {participant.id} has departed")
        else:
            interactor_or_404(participant.id)
    room_id = db.new_id("room")
    conn.execute(
        "INSERT INTO rooms (id, topic, channel, status, created_at)"
        " VALUES (?,?,?,'active',?)",
        (room_id, body.topic, body.channel, db.utcnow()),
    )
    for participant in body.participants:
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?,?,?)", (room_id, participant.kind, participant.id))
    conn.commit()
    return {
        "id": room_id, "topic": body.topic, "channel": body.channel,
        "presence": _CHANNEL_NOTES[body.channel],
        "participants": [
            {"kind": p.kind, "id": p.id, "display": _display(p.kind, p.id)}
            for p in body.participants
        ],
    }


@router.post("/rooms/{room_id}/messages", status_code=201)
def room_message(room_id: str, body: RoomMessage, request: Request) -> dict:
    """A user participant speaks; every profile participant answers."""
    room = _room_or_404(room_id)
    participants = _participants(room_id)
    if not any(p["kind"] == "user" and p["ref_id"] == body.sender_id
               for p in participants):
        raise HTTPException(403, "sender is not a user participant of this room")
    maturity = _room_maturity(participants)
    verdict = moderation.review(body.message, None, {"birthdate": None},
                                maturity=maturity)
    sent = _store_room_message(room_id, "user", body.sender_id, body.message,
                               verdict.approved, verdict.reason)
    replies = []
    if verdict.approved:
        replies = _profile_turns(room, participants,
                                 request.app.state.pdi,
                                 request.app.state.cloud)
    return {"message": sent, "replies": replies}


@router.post("/rooms/{room_id}/advance", status_code=201)
def room_advance(room_id: str, request: Request) -> dict:
    """Profiles take a turn unprompted — profile↔profile rooms run on this."""
    room = _room_or_404(room_id)
    participants = _participants(room_id)
    if not any(p["kind"] == "profile" for p in participants):
        raise HTTPException(422, "no synthetic profiles in this room")
    return {"replies": _profile_turns(room, participants,
                                      request.app.state.pdi,
                                      request.app.state.cloud)}


@router.get("/rooms/{room_id}/messages")
def room_transcript(room_id: str) -> list[dict]:
    _room_or_404(room_id)
    rows = db.connect().execute(
        "SELECT * FROM room_messages WHERE room_id=? AND status='approved'"
        " ORDER BY created_at, rowid", (room_id,)).fetchall()
    return [{"id": r["id"], "sender_kind": r["sender_kind"],
             "from": _display(r["sender_kind"], r["sender_id"]),
             "content": r["content"], "created_at": r["created_at"]}
            for r in rows]


# --------------------------------------------------------------------------- #
# marketplace listings
# --------------------------------------------------------------------------- #

@router.post("/marketplace/listings", status_code=201)
def create_listing(body: ListingCreate) -> dict:
    if body.kind == "profile":
        if not body.profile_id:
            raise HTTPException(422, "profile listings require profile_id")
        profile_or_404(body.profile_id)
    conn = db.connect()
    listing_id = db.new_id("lst")
    conn.execute(
        "INSERT INTO listings (id, kind, title, blurb, tags, area,"
        " provider_name, business, profile_id, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (listing_id, body.kind, body.title, body.blurb, json.dumps(body.tags),
         body.area, body.provider_name, int(body.business), body.profile_id,
         db.utcnow()),
    )
    conn.commit()
    return {"id": listing_id, "kind": body.kind, "title": body.title}


@router.post("/marketplace/seed", status_code=201)
def seed_marketplace() -> dict:
    """Populate the starter collection: one synthetic expert per industry,
    each with a claimed @handle and a marketplace listing, so a fresh
    deployment has profiles to immerse with before users publish their own.
    Idempotent — already-seeded profiles are skipped."""
    from .. import seed
    return seed.seed()


@router.get("/marketplace/listings")
def browse_listings(kind: str | None = None, tag: str | None = None,
                    area: str | None = None) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM listings ORDER BY created_at DESC, rowid DESC").fetchall()
    out = []
    for row in rows:
        tags = json.loads(row["tags"])
        if kind and row["kind"] != kind:
            continue
        if tag and tag.lower() not in [t.lower() for t in tags]:
            continue
        if area and (row["area"] or "").lower() != area.lower():
            continue
        out.append({"id": row["id"], "kind": row["kind"],
                    "title": row["title"], "blurb": row["blurb"],
                    "tags": tags, "area": row["area"],
                    "provider_name": row["provider_name"],
                    "business": bool(row["business"]),
                    "profile_id": row["profile_id"]})
    return out


@router.delete("/marketplace/listings/{listing_id}", status_code=204)
def remove_listing(listing_id: str) -> None:
    conn = db.connect()
    if not conn.execute("DELETE FROM listings WHERE id=?",
                        (listing_id,)).rowcount:
        raise HTTPException(404, "listing not found")
    conn.commit()


# --------------------------------------------------------------------------- #
# providers & consented handoffs
# --------------------------------------------------------------------------- #

@router.post("/providers", status_code=201)
def register_provider(body: ProviderCreate) -> dict:
    conn = db.connect()
    provider_id = db.new_id("prv")
    conn.execute(
        "INSERT INTO providers (id, name, area, location, contact, business,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (provider_id, body.name, body.area, body.location, body.contact,
         int(body.business), db.utcnow()),
    )
    conn.commit()
    return {"id": provider_id, "name": body.name, "area": body.area}


@router.get("/providers")
def list_providers(area: str | None = None) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM providers ORDER BY created_at, rowid").fetchall()
    return [{**dict(r), "business": bool(r["business"])}
            for r in rows if not area or r["area"].lower() == area.lower()]


@router.post("/handoffs", status_code=201)
def create_handoff(body: HandoffCreate, request: Request) -> dict:
    """Hand a session from the AI specialist to a real local provider —
    only with the user's explicit consent, behind a revocable token."""
    if not body.consent:
        raise HTTPException(
            403, "a handoff requires the user's explicit consent")
    interactor = interactor_or_404(body.interactor_id)
    provider = db.connect().execute(
        "SELECT * FROM providers WHERE id=?", (body.provider_id,)).fetchone()
    if provider is None:
        raise HTTPException(404, "provider not found")

    package: dict = {"user": interactor["display_name"],
                     "provider_area": provider["area"], "sessions": None}
    if body.profile_id:
        profile = profile_or_404(body.profile_id)
        conn = db.connect()
        recent = conn.execute(
            "SELECT role, content FROM messages WHERE profile_id=?"
            " AND interactor_id=? AND status='approved'"
            " ORDER BY created_at DESC, rowid DESC LIMIT 6",
            (body.profile_id, body.interactor_id)).fetchall()
        state = engagement.get(body.profile_id, body.interactor_id)
        package.update({
            "specialist": profile["display_name"],
            "specialist_purpose": profile["purpose"],
            "sessions": state["sessions"] if state else 0,
            "recent_exchange": [
                {"role": r["role"], "content": r["content"]}
                for r in reversed(recent)
            ],
        })

    conn = db.connect()
    handoff_id = db.new_id("hnd")
    token = f"hnd_{secrets.token_urlsafe(24)}"
    pdi = request.app.state.pdi
    stored, pdi_key = json.dumps(package), None
    if pdi is not None:
        pdi_key = f"qrme/handoffs/{handoff_id}"
        pdi.put(pdi_key, stored)
        stored = None                 # sealed — only the key stays local
    conn.execute(
        "INSERT INTO handoffs (id, interactor_id, profile_id, provider_id,"
        " package, pdi_key, token, revoked, created_at)"
        " VALUES (?,?,?,?,?,?,?,0,?)",
        (handoff_id, body.interactor_id, body.profile_id, body.provider_id,
         stored, pdi_key, token, db.utcnow()),
    )
    conn.commit()
    return {"id": handoff_id, "provider": provider["name"],
            "area": provider["area"], "token": token,
            "sealed": pdi_key is not None}


@router.get("/handoffs/{handoff_id}")
def read_handoff(handoff_id: str, token: str, request: Request) -> dict:
    """The provider redeems the token to receive the session package."""
    row = db.connect().execute("SELECT * FROM handoffs WHERE id=?",
                               (handoff_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "handoff not found")
    if row["revoked"] or token != row["token"]:
        raise HTTPException(403, "token invalid or revoked")
    if row["pdi_key"] and request.app.state.pdi is not None:
        raw = request.app.state.pdi.get(row["pdi_key"])
        package = json.loads(raw) if raw else None
    else:
        package = json.loads(row["package"]) if row["package"] else None
    return {"id": handoff_id, "package": package}


@router.delete("/handoffs/{handoff_id}")
def revoke_handoff(handoff_id: str, request: Request) -> dict:
    """The user changes their mind: revoke access and purge the package."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM handoffs WHERE id=?",
                       (handoff_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "handoff not found")
    conn.execute("UPDATE handoffs SET revoked=1, package=NULL WHERE id=?",
                 (handoff_id,))
    conn.commit()
    if row["pdi_key"] and request.app.state.pdi is not None:
        request.app.state.pdi.delete(row["pdi_key"])
    return {"id": handoff_id, "revoked": True}
