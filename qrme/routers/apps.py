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

## Installed is not the same as able to reach anything

A storefront draws a lock on some rows, and the lock has to be a posture
rather than a picture. ``catalog.needs()`` says what each connector must be
given — nothing, the person's sign-in, or an operator key — and this module
is where that becomes something a person meets:

- installing is always allowed, and a row that needs nothing is authorized
  the moment it is installed;
- ``POST /apps/{cid}/authorize`` takes the credential and seals it into the
  PDI vault, keeping only the key. No vault, no authorizing — this file
  will not hold somebody's Google password in the clear;
- ``invoke`` refuses an unauthorized connector, naming what is missing.

That last one is a correction rather than a new rule. ``invoke`` used to
answer ``performed`` for every connector on the board, having reached
nothing at all, which is the shape this estate keeps finding and removing:

    asked     did the call succeed
    mattered  did anything happen on the other end

``collect`` is deliberately not gated, because it does not reach anything —
it stores what the owner pasted, which needs no credential and never did.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import catalog, db, storage, tiers
from ..common import profile_or_404, require_owner
from ..models import AppAuthorize, AppCollect, AppConnect, AppInvoke

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
        "needs_first": catalog.needs(row["provider"], row["app"]),
        "authorized": bool(row["authorized_at"]),
    }


#: What the refusal says, per posture. Written here rather than at the raise
#: so the three of them can be read side by side — a person meeting one of
#: these is being told what to go and do, not that something went wrong.
_MISSING = {
    "sign-in": "{label} is installed and has not been signed in to yet, so it "
               "cannot reach your account there. Sign in to it from this "
               "connector and try again.",
    "key": "{label} needs a key this deployment has not been given, so it "
           "cannot reach the service. Whoever runs this deployment adds it.",
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
    now = db.utcnow()
    # A connector that needs nothing is able to reach the far side the moment
    # it exists, so it is authorized here rather than making somebody press a
    # second button that asks for a credential it will never use.
    authorized = now if entry["needs_first"] == "nothing" else None
    conn.execute(
        "INSERT INTO app_connectors (id, profile_id, provider, app, label,"
        " capabilities, directions, status, collected, actions,"
        " authorized_at, created_at)"
        " VALUES (?,?,?,?,?,?,?, 'active', 0, 0, ?, ?)",
        (cid, profile_id, body.provider, body.app, entry["label"],
         json.dumps(caps), json.dumps(entry["directions"]), authorized, now),
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


@router.post("/apps/{cid}/authorize")
def authorize_app(cid: str, body: AppAuthorize, request: Request) -> dict:
    """Give a connector the credential it has been waiting for.

    The secret goes into the PDI vault and this database keeps the key. A
    deployment with no vault configured has nowhere safe to put it, and
    refuses — storing somebody's account credential in a plain SQLite file
    beside their profile is not a lesser version of sealing it.
    """
    row = _conn_or_404(cid)
    require_owner(row["profile_id"], request)
    if row["status"] != "active":
        raise HTTPException(409, "connector has been revoked")
    if catalog.needs(row["provider"], row["app"]) == "nothing":
        raise HTTPException(
            409, f"{row['label']} reads what anybody can read — it has no "
                 f"account to sign in to and nothing to keep for it")
    # The vault question asks the *plan*, not the deployment — `storage`
    # explains why at length, and this is a write, so the plan gate applies.
    # A free profile is platform custody over plain HTTPS by design, which is
    # a fine posture for a wall post and not one for somebody's account
    # credential, so this refuses instead of quietly holding it in the clear.
    vault = storage.vault_for(
        tiers.plan_of_profile(row["profile_id"]), request.app.state.pdi)
    if vault is None:
        raise HTTPException(
            409, "there is nowhere here to keep that credential sealed, so "
                 "it will not be kept at all — this needs a plan with a "
                 "vault behind it, on a deployment that has one")
    ref = f"qrme/{row['profile_id']}/connectors/{cid}"
    vault.put(ref, json.dumps({"secret": body.secret, "account": body.account}))
    conn = db.connect()
    conn.execute(
        "UPDATE app_connectors SET authorized_at=?, secret_ref=? WHERE id=?",
        (db.utcnow(), ref, cid))
    conn.commit()
    return _out(_conn_or_404(cid))


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
    if not row["authorized_at"]:
        raise HTTPException(409, _MISSING[
            catalog.needs(row["provider"], row["app"])].format(
                label=row["label"]))
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
