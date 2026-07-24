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

from .. import db, robotics
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
            "audience": row["audience"],
            "title": row["title"], "blurb": row["blurb"],
            "publisher": row["publisher"], "price": row["price"],
            "currency": row["currency"], "free": row["price"] == 0,
            "items": items, "installs": installs}


@router.get("/packs")
def list_packs(industry: str | None = None,
               audience: str | None = None) -> list[dict]:
    """Public catalog of knowledge packs, optionally narrowed by industry
    and/or audience (profile knowledge vs. robot task packs)."""
    clauses, params = [], []
    if industry:
        clauses.append("industry=?")
        params.append(industry)
    if audience:
        clauses.append("audience=?")
        params.append(audience)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = db.connect().execute(
        f"SELECT * FROM knowledge_packs{where} ORDER BY audience, industry,"
        " price", params).fetchall()
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
    if body.audience == "robot" and not all(i.task for i in body.items):
        raise HTTPException(
            422, "every item in a robot pack needs a task (the command verb)")
    conn = db.connect()
    pack_id = db.new_id("pak")
    conn.execute(
        "INSERT INTO knowledge_packs (id, industry, audience, title, blurb,"
        " publisher, price, currency, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (pack_id, body.industry, body.audience, body.title, body.blurb,
         body.publisher, body.price, body.currency, db.utcnow()))
    for item in body.items:
        conn.execute(
            "INSERT INTO pack_items (id, pack_id, title, content, task,"
            " requires, created_at) VALUES (?,?,?,?,?,?,?)",
            (db.new_id("pki"), pack_id, item.title, item.content, item.task,
             json.dumps(item.requires), db.utcnow()))
    conn.commit()
    return _summary(_pack_or_404(pack_id))


@router.post("/packs/seed", status_code=201)
def seed_packs() -> dict:
    """Populate the starter packs: one free Field Pack per industry."""
    from .. import packs
    return packs.seed()


def _price_gate(pack: dict, body: PackInstall) -> None:
    if pack["price"] > 0 and not body.accept_price:
        raise HTTPException(
            402, f"this pack costs {pack['price']:.2f} {pack['currency']} — "
                 "set accept_price to buy it")


@router.post("/packs/{pack_id}/install", status_code=201)
def install_pack(pack_id: str, body: PackInstall, request: Request) -> dict:
    """Buy/download a pack. Profile packs become the profile's source
    material (vaulted in PDI when configured), growing the persona's
    knowledge base. Robot packs install onto a bound body (pass robot_id):
    each task becomes a commandable verb for that robot — capability-checked
    against the robotics catalog, refused for bodies that can't do the work.
    A priced pack requires explicit accept_price consent (payment simulated,
    like licensing)."""
    pack = _pack_or_404(pack_id)
    profile_or_404(body.profile_id)
    require_owner(body.profile_id, request)
    conn = db.connect()

    if pack["audience"] == "robot":
        if not body.robot_id:
            raise HTTPException(
                422, "robot packs install onto a bound robot — pass robot_id")
        robot = conn.execute("SELECT * FROM robots WHERE id=?",
                             (body.robot_id,)).fetchone()
        if robot is None or robot["profile_id"] != body.profile_id:
            raise HTTPException(404, "robot not found on this profile")
        if conn.execute("SELECT 1 FROM pack_installs WHERE pack_id=? AND"
                        " robot_id=?", (pack_id, body.robot_id)).fetchone():
            raise HTTPException(409, "pack already installed on this robot")
        _price_gate(pack, body)
        spec = robotics.get(robot["model"])
        caps = set(spec["capabilities"])
        builtins = set(robotics.allowed_commands(robot["model"]))
        items = conn.execute(
            "SELECT * FROM pack_items WHERE pack_id=? ORDER BY rowid",
            (pack_id,)).fetchall()
        for item in items:
            missing = [c for c in json.loads(item["requires"])
                       if c not in caps]
            if missing:
                raise HTTPException(
                    422, f"this {spec['kind']} lacks "
                         f"{', '.join(missing)} — '{item['title']}' cannot "
                         "run on it")
            if item["task"] in builtins:
                raise HTTPException(
                    409, f"task '{item['task']}' shadows a built-in command")
            if conn.execute("SELECT 1 FROM robot_skills WHERE robot_id=? AND"
                            " task=?", (body.robot_id,
                                        item["task"])).fetchone():
                raise HTTPException(
                    409, f"task '{item['task']}' is already installed from "
                         "another pack")
        for item in items:
            conn.execute(
                "INSERT INTO robot_skills (robot_id, pack_id, task, title,"
                " procedure, created_at) VALUES (?,?,?,?,?,?)",
                (body.robot_id, pack_id, item["task"], item["title"],
                 item["content"], db.utcnow()))
        conn.execute(
            "INSERT INTO pack_installs (pack_id, profile_id, robot_id,"
            " price_paid, installed_at) VALUES (?,?,?,?,?)",
            (pack_id, body.profile_id, body.robot_id, pack["price"],
             db.utcnow()))
        conn.commit()
        return {"pack_id": pack_id, "profile_id": body.profile_id,
                "robot_id": body.robot_id,
                "installed_tasks": [i["task"] for i in items],
                "price_paid": pack["price"], "currency": pack["currency"],
                "note": "the body can now be commanded with these tasks"}

    if body.robot_id:
        raise HTTPException(
            422, "profile knowledge packs install onto the profile — omit "
                 "robot_id")
    if conn.execute("SELECT 1 FROM pack_installs WHERE pack_id=? AND"
                    " profile_id=? AND robot_id=''",
                    (pack_id, body.profile_id)).fetchone():
        raise HTTPException(409, "pack already installed on this profile")
    _price_gate(pack, body)
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
        "INSERT INTO pack_installs (pack_id, profile_id, robot_id,"
        " price_paid, installed_at) VALUES (?,?,'',?,?)",
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
        "SELECT p.id, p.industry, p.audience, p.title, p.publisher,"
        " i.robot_id, i.price_paid, i.installed_at FROM pack_installs i"
        " JOIN knowledge_packs p ON p.id = i.pack_id WHERE i.profile_id=?"
        " ORDER BY i.installed_at", (profile_id,)).fetchall()
    return [dict(r) for r in rows]


@router.delete("/profiles/{profile_id}/packs/{pack_id}")
def uninstall_pack(profile_id: str, pack_id: str, request: Request) -> dict:
    """Uninstall: removes the pack's grounding items from the profile (and
    their vaulted copies), so the knowledge base shrinks back honestly."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    if not conn.execute("SELECT 1 FROM pack_installs WHERE pack_id=? AND"
                        " profile_id=? AND robot_id=''",
                        (pack_id, profile_id)).fetchone():
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
    conn.execute("DELETE FROM pack_installs WHERE pack_id=? AND profile_id=?"
                 " AND robot_id=''", (pack_id, profile_id))
    conn.commit()
    return {"pack_id": pack_id, "profile_id": profile_id,
            "removed_items": removed}


# -- robot task packs: the skills a bound body has learned -------------------

def _owned_robot_or_404(robot_id: str, request: Request) -> dict:
    row = db.connect().execute("SELECT * FROM robots WHERE id=?",
                               (robot_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "robot not found")
    require_owner(row["profile_id"], request)
    return dict(row)


@router.get("/robots/{robot_id}/skills")
def robot_skills(robot_id: str, request: Request) -> list[dict]:
    """Owner view: every task module installed on this body, and the pack
    it came from."""
    _owned_robot_or_404(robot_id, request)
    rows = db.connect().execute(
        "SELECT s.task, s.title, s.procedure, s.pack_id, p.title AS pack_title"
        " FROM robot_skills s JOIN knowledge_packs p ON p.id = s.pack_id"
        " WHERE s.robot_id=? ORDER BY s.created_at, s.task",
        (robot_id,)).fetchall()
    return [dict(r) for r in rows]


@router.delete("/robots/{robot_id}/packs/{pack_id}")
def uninstall_robot_pack(robot_id: str, pack_id: str,
                         request: Request) -> dict:
    """Uninstall a task pack from a body: its tasks stop being commandable
    immediately."""
    robot = _owned_robot_or_404(robot_id, request)
    conn = db.connect()
    if not conn.execute("SELECT 1 FROM pack_installs WHERE pack_id=? AND"
                        " robot_id=?", (pack_id, robot_id)).fetchone():
        raise HTTPException(404, "pack not installed on this robot")
    removed = conn.execute(
        "DELETE FROM robot_skills WHERE robot_id=? AND pack_id=?",
        (robot_id, pack_id)).rowcount
    conn.execute("DELETE FROM pack_installs WHERE pack_id=? AND robot_id=?",
                 (pack_id, robot_id))
    conn.commit()
    return {"pack_id": pack_id, "robot_id": robot_id,
            "profile_id": robot["profile_id"], "removed_tasks": removed}
