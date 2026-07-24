"""Knowledge packs on the marketplace: browse, buy/download, install.

A pack's item titles are public (the shop window); the contents are the
product — they are delivered only by installing, which copies them into the
profile's source material. From there the existing pipeline does the rest:
the persona's system prompt gains a knowledge base, and every reply's
provenance counts the ``pack`` grounding honestly.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import db
from ..common import profile_or_404, require_owner
from ..models import PackInstall, PackPublish

router = APIRouter()


def _pack_or_404(pack_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM knowledge_packs WHERE id=?", (pack_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "pack not found")
    return dict(row)


def _summary(row: dict) -> dict:
    conn = db.connect()
    items = conn.execute("SELECT COUNT(*) AS n FROM pack_items WHERE pack_id=?",
                         (row["id"],)).fetchone()["n"]
    installs = conn.execute(
        "SELECT COUNT(*) AS n FROM pack_installs WHERE pack_id=?",
        (row["id"],)).fetchone()["n"]
    return {"id": row["id"], "industry": row["industry"],
            "title": row["title"], "blurb": row["blurb"],
            "publisher": row["publisher"], "price": row["price"],
            "currency": row["currency"], "free": row["price"] == 0,
            "items": items, "installs": installs}


@router.get("/packs")
def list_packs(industry: str | None = None) -> list[dict]:
    """Public catalog of knowledge packs, optionally narrowed by industry."""
    conn = db.connect()
    if industry:
        rows = conn.execute(
            "SELECT * FROM knowledge_packs WHERE industry=?"
            " ORDER BY price, title", (industry,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM knowledge_packs ORDER BY industry, price").fetchall()
    return [_summary(dict(r)) for r in rows]


@router.get("/packs/{pack_id}")
def pack_detail(pack_id: str) -> dict:
    """Public detail: metadata plus item *titles* — the shop window. The
    contents are the product; they are delivered by installing."""
    pack = _pack_or_404(pack_id)
    titles = [r["title"] for r in db.connect().execute(
        "SELECT title FROM pack_items WHERE pack_id=? ORDER BY rowid",
        (pack_id,)).fetchall()]
    return {**_summary(pack), "item_titles": titles}


@router.post("/packs", status_code=201)
def publish_pack(body: PackPublish) -> dict:
    """Publish a pack to the marketplace. Priced packs are bought; price 0
    is a free download."""
    if not body.items:
        raise HTTPException(422, "a pack needs at least one knowledge item")
    if body.price < 0:
        raise HTTPException(422, "price cannot be negative")
    conn = db.connect()
    pack_id = db.new_id("pak")
    conn.execute(
        "INSERT INTO knowledge_packs (id, industry, title, blurb, publisher,"
        " price, currency, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (pack_id, body.industry, body.title, body.blurb, body.publisher,
         body.price, body.currency, db.utcnow()))
    for item in body.items:
        conn.execute(
            "INSERT INTO pack_items (id, pack_id, title, content, created_at)"
            " VALUES (?,?,?,?,?)",
            (db.new_id("pki"), pack_id, item.title, item.content, db.utcnow()))
    conn.commit()
    return _summary(_pack_or_404(pack_id))


@router.post("/packs/seed", status_code=201)
def seed_packs() -> dict:
    """Populate the starter packs: one free Field Pack per industry."""
    from .. import packs
    return packs.seed()


@router.post("/packs/{pack_id}/install", status_code=201)
def install_pack(pack_id: str, body: PackInstall, request: Request) -> dict:
    """Buy/download a pack onto a profile: its items become the profile's
    source material (vaulted in PDI when configured), growing the persona's
    knowledge base. A priced pack requires explicit accept_price consent
    (payment simulated, like licensing)."""
    pack = _pack_or_404(pack_id)
    profile_or_404(body.profile_id)
    require_owner(body.profile_id, request)
    conn = db.connect()
    if conn.execute("SELECT 1 FROM pack_installs WHERE pack_id=? AND"
                    " profile_id=?", (pack_id, body.profile_id)).fetchone():
        raise HTTPException(409, "pack already installed on this profile")
    if pack["price"] > 0 and not body.accept_price:
        raise HTTPException(
            402, f"this pack costs {pack['price']:.2f} {pack['currency']} — "
                 "set accept_price to buy it")
    items = conn.execute(
        "SELECT * FROM pack_items WHERE pack_id=? ORDER BY rowid",
        (pack_id,)).fetchall()
    pdi = request.app.state.pdi
    for item in items:
        item_id = db.new_id("src")
        content, pdi_key = item["content"], None
        if pdi is not None:
            pdi_key = f"qrme/{body.profile_id}/sources/{item_id}"
            pdi.put(pdi_key, json.dumps({"content": item["content"]}))
            content = None            # only the reference stays local
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (item_id, body.profile_id, "pack",
             f"{pack['title']} — {item['title']}", content, pdi_key, pack_id,
             db.utcnow()))
    conn.execute(
        "INSERT INTO pack_installs (pack_id, profile_id, price_paid,"
        " installed_at) VALUES (?,?,?,?)",
        (pack_id, body.profile_id, pack["price"], db.utcnow()))
    conn.commit()
    return {"pack_id": pack_id, "profile_id": body.profile_id,
            "installed_items": len(items), "price_paid": pack["price"],
            "currency": pack["currency"],
            "note": "the pack now grounds this profile's knowledge base"}


@router.get("/profiles/{profile_id}/packs")
def installed_packs(profile_id: str, request: Request) -> list[dict]:
    """Owner view: which packs this profile has installed."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT p.id, p.industry, p.title, p.publisher, i.price_paid,"
        " i.installed_at FROM pack_installs i JOIN knowledge_packs p"
        " ON p.id = i.pack_id WHERE i.profile_id=? ORDER BY i.installed_at",
        (profile_id,)).fetchall()
    return [dict(r) for r in rows]


@router.delete("/profiles/{profile_id}/packs/{pack_id}")
def uninstall_pack(profile_id: str, pack_id: str, request: Request) -> dict:
    """Uninstall: removes the pack's grounding items from the profile (and
    their vaulted copies), so the knowledge base shrinks back honestly."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    if not conn.execute("SELECT 1 FROM pack_installs WHERE pack_id=? AND"
                        " profile_id=?", (pack_id, profile_id)).fetchone():
        raise HTTPException(404, "pack not installed on this profile")
    pdi = request.app.state.pdi
    if pdi is not None:
        for row in conn.execute(
                "SELECT pdi_key FROM source_items WHERE profile_id=? AND"
                " pack_id=? AND pdi_key IS NOT NULL",
                (profile_id, pack_id)).fetchall():
            try:
                pdi.delete(row["pdi_key"])
            except Exception:
                pass                  # local removal still proceeds
    removed = conn.execute(
        "DELETE FROM source_items WHERE profile_id=? AND pack_id=?",
        (profile_id, pack_id)).rowcount
    conn.execute("DELETE FROM pack_installs WHERE pack_id=? AND profile_id=?",
                 (pack_id, profile_id))
    conn.commit()
    return {"pack_id": pack_id, "profile_id": profile_id,
            "removed_items": removed}
