"""Connected-app connectors.

A profile connects to an AI-integrated app from the catalog (``catalog.py``) —
Apple Photos, Google Calendar, Microsoft 365, Canva Magic Studio, … — and its
agents then use it in the direction the app supports:

- **collect** — pull context in as source material that builds the profile
  (sealed in the PDI vault when configured);
- **act** — drive the app agentically (create an event, run a shortcut);
- **produce** — generate media (a memory movie, a Canva design).

Connecting grants a subset of the app's catalog capabilities; invoking a
capability the connector wasn't granted is refused. All owner-gated.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import catalog, db
from ..common import profile_or_404, require_owner
from ..models import AppCollect, AppConnect, AppInvoke

router = APIRouter()


def _entry(provider: str, app: str) -> dict:
    entry = catalog.BY_KEY.get((provider, app))
    if entry is None:
        raise HTTPException(404, f"unknown connector: {provider}/{app}")
    return entry


def _conn_or_404(cid: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM app_connectors WHERE id=?", (cid,)).fetchone()
    if row is None:
        raise HTTPException(404, "app connector not found")
    return dict(row)


def _out(row: dict) -> dict:
    return {
        "id": row["id"],
        "profile_id": row["profile_id"],
        "provider": row["provider"],
        "app": row["app"],
        "label": row["label"],
        "capabilities": json.loads(row["capabilities"]),
        "directions": json.loads(row["directions"]),
        "status": row["status"],
        "collected": row["collected"],
        "actions": row["actions"],
    }


@router.post("/profiles/{profile_id}/apps", status_code=201)
def connect_app(profile_id: str, body: AppConnect, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    entry = _entry(body.provider, body.app)
    caps = body.capabilities or list(entry["capabilities"])
    unknown = set(caps) - set(entry["capabilities"])
    if unknown:
        raise HTTPException(422, f"{body.app} does not offer: {sorted(unknown)}")
    conn = db.connect()
    cid = db.new_id("app")
    conn.execute(
        "INSERT INTO app_connectors (id, profile_id, provider, app, label,"
        " capabilities, directions, status, collected, actions, created_at)"
        " VALUES (?,?,?,?,?,?,?, 'active', 0, 0, ?)",
        (cid, profile_id, body.provider, body.app, entry["label"],
         json.dumps(caps), json.dumps(entry["directions"]), db.utcnow()),
    )
    conn.commit()
    return _out(_conn_or_404(cid))


@router.get("/profiles/{profile_id}/apps")
def list_apps(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM app_connectors WHERE profile_id=?"
        " ORDER BY created_at, rowid", (profile_id,)).fetchall()
    return [_out(dict(r)) for r in rows]


@router.delete("/apps/{cid}")
def revoke_app(cid: str, request: Request) -> dict:
    row = _conn_or_404(cid)
    require_owner(row["profile_id"], request)
    conn = db.connect()
    conn.execute("UPDATE app_connectors SET status='revoked' WHERE id=?", (cid,))
    conn.commit()
    return {"id": cid, "status": "revoked"}


@router.post("/apps/{cid}/collect", status_code=201)
def collect_app(cid: str, body: AppCollect, request: Request) -> dict:
    row = _conn_or_404(cid)
    require_owner(row["profile_id"], request)
    if "collect" not in json.loads(row["directions"]):
        raise HTTPException(409, f"{row['app']} does not support collecting context")
    if row["status"] != "active":
        raise HTTPException(409, "connector has been revoked")
    pdi = request.app.state.pdi
    conn = db.connect()
    ingested = 0
    for item in body.items:
        item_id = db.new_id("src")
        title = item.title or row["label"]
        content, pdi_key = item.content, None
        if pdi is not None and item.content:
            pdi_key = f"qrme/{row['profile_id']}/sources/{item_id}"
            pdi.put(pdi_key, json.dumps({"content": item.content}))
            content = None
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, created_at) VALUES (?,?,'linked_account',?,?,?,?)",
            (item_id, row["profile_id"], title, content, pdi_key, db.utcnow()),
        )
        ingested += 1
    conn.execute("UPDATE app_connectors SET collected = collected + ? WHERE id=?",
                 (ingested, cid))
    conn.commit()
    return {"connector": cid, "app": row["app"], "ingested": ingested,
            "note": f"context from {row['label']} now feeds this profile's training"}


@router.post("/apps/{cid}/invoke", status_code=201)
def invoke_app(cid: str, body: AppInvoke, request: Request) -> dict:
    """An agent uses one of the connector's capabilities (act / produce)."""
    row = _conn_or_404(cid)
    require_owner(row["profile_id"], request)
    if row["status"] != "active":
        raise HTTPException(409, "connector has been revoked")
    if body.capability not in json.loads(row["capabilities"]):
        raise HTTPException(422,
                            f"this {row['app']} connector was not granted "
                            f"'{body.capability}'")
    conn = db.connect()
    conn.execute("UPDATE app_connectors SET actions = actions + 1 WHERE id=?", (cid,))
    conn.commit()
    return {
        "connector": cid,
        "provider": row["provider"],
        "app": row["app"],
        "capability": body.capability,
        "directions": json.loads(row["directions"]),
        "status": "performed",
        "input": body.input,
        "result": f"{row['label']} · {body.capability} performed",
    }
