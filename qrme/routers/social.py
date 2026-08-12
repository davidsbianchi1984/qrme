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
import urllib.parse

from fastapi import APIRouter, HTTPException, Request, Response

from .. import catalog, db, moderation, offline, scrape, watermark
from ..common import profile_or_404, require_owner, source_items
from ..models import SocialCollect, SocialConnect, SocialPublish

router = APIRouter()


@router.get("/connectors/catalog")
def connector_catalog() -> dict:
    """The connected-apps catalog: the AI-integrated apps (Apple, Google,
    Microsoft, Canva) a profile and its agents can connect to."""
    return catalog.catalog()

_PLATFORM_URL = {
    "instagram": "https://instagram.com/{h}",
    "x": "https://x.com/{h}",
    "tiktok": "https://tiktok.com/@{h}",
    "facebook": "https://facebook.com/{h}",
    "linkedin": "https://linkedin.com/in/{h}",
    "youtube": "https://youtube.com/@{h}",
    "reddit": "https://reddit.com/user/{h}",
    "threads": "https://threads.net/@{h}",
    "whatsapp": "https://wa.me/{h}",
    "meta": "https://meta.com/{h}",
    "mastodon": "https://mastodon.social/@{h}",
    "twitch": "https://twitch.tv/{h}",
    "snapchat": "https://snapchat.com/add/{h}",
    "roblox": "https://roblox.com/users/{h}",
    "pinterest": "https://pinterest.com/{h}",
    "discord": "https://discord.com/users/{h}",
}

# The pasted link, read for what it already says. A person holds a URL far
# more often than a bare handle; the host names the platform and the path
# names the account, so the form must not ask anybody to transcribe either.
_HOST_PLATFORM = {
    "instagram.com": "instagram", "x.com": "x", "twitter.com": "x",
    "tiktok.com": "tiktok", "facebook.com": "facebook",
    "linkedin.com": "linkedin", "youtube.com": "youtube",
    "reddit.com": "reddit", "threads.net": "threads", "wa.me": "whatsapp",
    "meta.com": "meta", "mastodon.social": "mastodon", "twitch.tv": "twitch",
    "snapchat.com": "snapchat", "roblox.com": "roblox",
    "pinterest.com": "pinterest", "discord.com": "discord",
}

#: Path segments platforms put before the account name (linkedin.com/in/…,
#: reddit.com/user/…, discord.com/users/…, snapchat.com/add/…).
_LINK_PREFIXES = {"in", "user", "users", "add"}


def _from_link(url: str) -> tuple[str, str]:
    """(platform, handle) read out of a pasted profile link."""
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower().removeprefix("www.")
    platform = _HOST_PLATFORM.get(host)
    if platform is None:
        raise HTTPException(
            422, "that link's site is not a platform this deployment "
                 "recognises — pick the platform and type the handle instead")
    segments = [s for s in parts.path.split("/")
                if s and s.lower() not in _LINK_PREFIXES]
    if not segments:
        raise HTTPException(
            400, "that link has no account in it — paste the profile's own "
                 "page, not the platform's front door")
    return platform, segments[0]


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
    handle = (body.handle or "").strip()
    platform = body.platform
    if handle.startswith("#"):
        raise HTTPException(
            422, "a hashtag names a topic, not an account — give the "
                 "account's handle or paste its link")
    if handle.startswith(("http://", "https://")):
        # A pasted link names its own platform and account; what it says
        # wins over the dropdown, because the link is the thing imported.
        platform, handle = _from_link(handle)
    handle = handle.lstrip("@") or None
    conn.execute(
        "INSERT INTO social_connections (id, profile_id, platform, direction,"
        " handle, scope, status, collected, published, created_at)"
        " VALUES (?,?,?,?,?,?, 'active', 0, 0, ?)",
        (cid, profile_id, platform, body.direction, handle,
         json.dumps(body.scope), db.utcnow()),
    )
    if body.direction == "publish":
        conn.execute(
            "INSERT OR IGNORE INTO surfaces (profile_id, surface, created_at)"
            " VALUES (?,?,?)",
            (profile_id, f"social:{platform}", db.utcnow()),
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


@router.post("/social/{cid}/scrape", status_code=201)
def scrape_page(cid: str, request: Request) -> dict:
    """Go to the imported link and take the words that are publicly there.

    The collect door stores what the owner pastes; this one visits the
    address the connection has carried since it was made — the platform's
    public page for the handle — and stores what a browser would show
    anybody: title, the bio line in the page's metadata, the visible text.
    One source item per visit, with the URL and the fetch time written into
    it, so the profile's material says where it came from.
    """
    row = _conn_or_404(cid)
    require_owner(row["profile_id"], request)
    if row["direction"] != "collect":
        raise HTTPException(409, "this connection is for publishing, not collecting")
    if row["status"] != "active":
        raise HTTPException(409, "connection has been revoked")
    if offline.enabled():
        raise HTTPException(
            409, "this deployment is offline — nothing leaves this machine, "
                 "so the page cannot be fetched. Paste the content into "
                 "collect instead.")
    if not row["handle"] or row["platform"] not in _PLATFORM_URL:
        raise HTTPException(
            400, "this connection has no public address to visit — reconnect "
                 "with the account's handle, or paste content into collect")
    url = _PLATFORM_URL[row["platform"]].format(h=row["handle"])
    try:
        page = scrape.extract(scrape.fetch(url))
    except Exception as e:                                     # noqa: BLE001
        raise HTTPException(
            502, f"could not fetch {url} — {e.__class__.__name__}: {e}")
    # A wall's words are the platform's, not the person's. Before this
    # check, a Facebook import "succeeded" by storing the login page as
    # source material — which the persona then quoted back in chat as
    # though it were the owner's own writing.
    if scrape.wall(page):
        raise HTTPException(
            422, "that platform shows a signed-out visitor only its login "
                 "wall, so there is nothing of the account to import — "
                 "copy the profile's text while signed in and paste it "
                 "into collect instead")
    parts = [p for p in (page["description"], page["text"]) if p]
    if not (page["title"] or parts):
        raise HTTPException(
            502, f"{url} answered with nothing readable — no title, no "
                 "description, no text")
    body_text = "\n\n".join(parts) + f"\n\nFetched from {url} at {db.utcnow()}"
    pdi = request.app.state.pdi
    conn = db.connect()
    item_id = db.new_id("src")
    title = f"{row['platform']} · {page['title'] or row['handle']}"
    content, pdi_key = body_text, None
    if pdi is not None:
        pdi_key = f"qrme/{row['profile_id']}/sources/{item_id}"
        pdi.put(pdi_key, json.dumps({"content": body_text}))
        content = None                     # only the reference stays local
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, created_at) VALUES (?,?,'social_post',?,?,?,?)",
        (item_id, row["profile_id"], title, content, pdi_key, db.utcnow()),
    )
    conn.execute("UPDATE social_connections SET collected = collected + 1 WHERE id=?",
                 (cid,))
    conn.commit()
    return {
        "connection": cid,
        "platform": row["platform"],
        "url": url,
        "title": page["title"],
        "ingested": 1,
        "total_sources": len(source_items(row["profile_id"], pdi)),
        "note": "the page's public words now feed this profile's training",
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
    profile_or_404(row["profile_id"])
    # Strict, not the profile's own maturity. `compose_post` states the rule
    # for an in-app post — *public posts face the widest audience: always the
    # strict filter* — and this is that same act aimed somewhere wider still:
    # a platform QRME does not run, in front of an audience it cannot see.
    # Reading `profile["maturity"]` here meant a profile set to `open` ran the
    # open filter on the way *out of the building*, while the same profile
    # posting in-app ran strict.
    verdict = moderation.review(body.content, None, {"birthdate": None},
                                maturity="strict")
    status = "approved" if verdict.approved else "rejected"
    conn = db.connect()
    post_id = db.new_id("post")
    surface = f"social:{row['platform']}"
    # Stamped, like every other public post. `compose_post` says why in one
    # sentence — *a public post is synthetic media leaving the platform: it
    # carries a verifiable synthetic-media credential from the moment it
    # exists* — and this route is the literal case that sentence describes.
    # It stored `watermark_id` as NULL, so the only posts going out with no
    # credential were the ones actually leaving.
    credential = watermark.stamp(row["profile_id"], "post", body.content)
    conn.execute(
        "INSERT INTO posts (id, profile_id, surface, topic, content, status,"
        " flag_reason, watermark_id, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (post_id, row["profile_id"], surface, body.topic, body.content, status,
         verdict.reason, credential["watermark_id"], db.utcnow()),
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
        # Handed back so whatever posts this to the platform can carry the
        # disclosure with it rather than having to look it up afterwards.
        "watermark": credential,
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
