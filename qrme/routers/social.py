"""Social-platform connections.

A profile connects to an external platform (Instagram, X, TikTok, …) in one of
two directions:

- **collect** — pull the account's content *in* to build the profile. Each
  collected item is stored as a ``social_post`` source item (sealed in the PDI
  vault when configured), exactly like any other source the profile is trained
  on. This is how a synthetic profile is grown from someone's real footprint.
- **publish** — post / run the profile *on* the platform. Posts go through the
  same moderation pipeline as chat, the platform is registered as a live
  ``social:<name>`` surface, and a QR beacon lets people reach the profile's
  presence there.

Everything owner-gated; collecting and publishing are separate connections so a
read-only import can never also post.
"""

from __future__ import annotations

import io
import json
import os

from fastapi import APIRouter, HTTPException, Request, Response

from .. import db, moderation
from ..common import profile_or_404, require_owner, source_items
from ..models import SocialCollect, SocialConnect, SocialPublish

router = APIRouter()

_PLATFORM_URL = {
    "instagram": "https://instagram.com/{h}",
    "x": "https://x.com/{h}",
    "tiktok": "https://tiktok.com/@{h}",
    "facebook": "https://facebook.com/{h}",
    "linkedin": "https://linkedin.com/in/{h}",
    "youtube": "https://youtube.com/@{h}",
    "reddit": "https://reddit.com/user/{h}",
    "threads": "https://threads.net/@{h}",
}


def _public_base() -> str:
    return os.environ.get("QRME_PUBLIC_URL", "https://qrme.app").rstrip("/")


def _conn_or_404(cid: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM social_connections WHERE id=?", (cid,)).fetchone()
    if row is None:
        raise HTTPException(404, "social connection not found")
    return dict(row)


def _presence_url(row: dict) -> str:
    if row["handle"] and row["platform"] in _PLATFORM_URL:
        return _PLATFORM_URL[row["platform"]].format(h=row["handle"])
    return f"{_public_base()}/summon?ref=soc:{row['id']}"


def _out(row: dict) -> dict:
    return {
        "id": row["id"],
        "profile_id": row["profile_id"],
        "platform": row["platform"],
        "direction": row["direction"],
        "handle": f"@{row['handle']}" if row["handle"] else None,
        "scope": json.loads(row["scope"]),
        "status": row["status"],
        "collected": row["collected"],
        "published": row["published"],
        "beacon": f"/social/{row['id']}/beacon" if row["direction"] == "publish" else None,
    }


# -- connect / list / revoke -------------------------------------------------

@router.post("/profiles/{profile_id}/social", status_code=201)
def connect_platform(profile_id: str, body: SocialConnect, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    cid = db.new_id("soc")
    handle = (body.handle or "").lstrip("@") or None
    conn.execute(
        "INSERT INTO social_connections (id, profile_id, platform, direction,"
        " handle, scope, status, collected, published, created_at)"
        " VALUES (?,?,?,?,?,?, 'active', 0, 0, ?)",
        (cid, profile_id, body.platform, body.direction, handle,
         json.dumps(body.scope), db.utcnow()),
    )
    if body.direction == "publish":
        conn.execute(
            "INSERT OR IGNORE INTO surfaces (profile_id, surface, created_at)"
            " VALUES (?,?,?)",
            (profile_id, f"social:{body.platform}", db.utcnow()),
        )
    conn.commit()
    return _out(_conn_or_404(cid))


@router.get("/profiles/{profile_id}/social")
def list_connections(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM social_connections WHERE profile_id=?"
        " ORDER BY created_at, rowid", (profile_id,)).fetchall()
    return [_out(dict(r)) for r in rows]


@router.delete("/social/{cid}")
def revoke(cid: str, request: Request) -> dict:
    row = _conn_or_404(cid)
    require_owner(row["profile_id"], request)
    conn = db.connect()
    conn.execute("UPDATE social_connections SET status='revoked' WHERE id=?", (cid,))
    if row["direction"] == "publish":
        # Only drop the live surface if no other active publish connection uses it.
        others = conn.execute(
            "SELECT COUNT(*) AS c FROM social_connections WHERE profile_id=?"
            " AND platform=? AND direction='publish' AND status='active' AND id<>?",
            (row["profile_id"], row["platform"], cid)).fetchone()["c"]
        if not others:
            conn.execute("DELETE FROM surfaces WHERE profile_id=? AND surface=?",
                         (row["profile_id"], f"social:{row['platform']}"))
    conn.commit()
    return {"id": cid, "status": "revoked"}


# -- collect: build the profile from the account -----------------------------

@router.post("/social/{cid}/collect", status_code=201)
def collect(cid: str, body: SocialCollect, request: Request) -> dict:
    row = _conn_or_404(cid)
    require_owner(row["profile_id"], request)
    if row["direction"] != "collect":
        raise HTTPException(409, "this connection is for publishing, not collecting")
    if row["status"] != "active":
        raise HTTPException(409, "connection has been revoked")
    pdi = request.app.state.pdi
    conn = db.connect()
    ingested = 0
    for item in body.items:
        item_id = db.new_id("src")
        title = item.title or f"{row['platform']} post"
        content, pdi_key = item.content, None
        if pdi is not None and item.content:
            pdi_key = f"qrme/{row['profile_id']}/sources/{item_id}"
            pdi.put(pdi_key, json.dumps({"content": item.content}))
            content = None                 # only the reference stays local
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, created_at) VALUES (?,?,'social_post',?,?,?,?)",
            (item_id, row["profile_id"], title, content, pdi_key, db.utcnow()),
        )
        ingested += 1
    conn.execute("UPDATE social_connections SET collected = collected + ? WHERE id=?",
                 (ingested, cid))
    conn.commit()
    return {
        "connection": cid,
        "platform": row["platform"],
        "ingested": ingested,
        "total_sources": len(source_items(row["profile_id"], pdi)),
        "note": "collected content now feeds this profile's training",
    }


# -- publish: run the profile on the platform --------------------------------

@router.post("/social/{cid}/publish", status_code=201)
def publish(cid: str, body: SocialPublish, request: Request) -> dict:
    row = _conn_or_404(cid)
    require_owner(row["profile_id"], request)
    if row["direction"] != "publish":
        raise HTTPException(409, "this connection is for collecting, not publishing")
    if row["status"] != "active":
        raise HTTPException(409, "connection has been revoked")
    profile = profile_or_404(row["profile_id"])
    verdict = moderation.review(body.content, None, {"birthdate": None},
                                profile["maturity"])
    status = "approved" if verdict.approved else "rejected"
    conn = db.connect()
    post_id = db.new_id("post")
    surface = f"social:{row['platform']}"
    conn.execute(
        "INSERT INTO posts (id, profile_id, surface, topic, content, status,"
        " flag_reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (post_id, row["profile_id"], surface, body.topic, body.content, status,
         verdict.reason, db.utcnow()),
    )
    if verdict.approved:
        conn.execute("UPDATE social_connections SET published = published + 1 WHERE id=?",
                     (cid,))
    conn.commit()
    return {
        "post_id": post_id,
        "platform": row["platform"],
        "surface": surface,
        "status": status,
        "flag_reason": verdict.reason,
        "content": body.content if verdict.approved else None,
    }


# -- beacon / QR: reach the profile's presence -------------------------------

@router.get("/social/{cid}/beacon")
def beacon(cid: str) -> dict:
    row = _conn_or_404(cid)
    if row["direction"] != "publish":
        raise HTTPException(409, "beacons are for publish connections")
    return {
        "connection": cid,
        "platform": row["platform"],
        "handle": f"@{row['handle']}" if row["handle"] else None,
        "presence_url": _presence_url(row),
        "qr_svg": f"/social/{cid}/qr.svg",
    }


@router.get("/social/{cid}/qr.svg")
def qr(cid: str) -> Response:
    row = _conn_or_404(cid)
    if row["direction"] != "publish":
        raise HTTPException(409, "beacons are for publish connections")
    import segno

    buf = io.BytesIO()
    segno.make(_presence_url(row), error="q").save(
        buf, kind="svg", scale=8, border=2, dark="#161840", light="#F4E3C8")
    return Response(content=buf.getvalue(), media_type="image/svg+xml")
