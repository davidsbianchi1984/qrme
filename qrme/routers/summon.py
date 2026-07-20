"""Summoning: @handles, #tags, and QR beacons.

A synthetic profile can be reached three ways:

- ``@handle`` — a claimed, unique handle for direct summoning;
- ``#tag``    — topical summoning through marketplace tags;
- **beacon**  — a profile *left behind* somewhere physical: a placed QR
  anchor (bench, storefront, memorial plaque) whose code resolves to the
  profile. Scans are counted, beacons can be picked back up, and a beacon
  for a departed profile resolves as a memorial rather than a chat.

All summon responses are public discovery cards — display info only, never
persona internals; anonymous profiles stay anonymous.
"""

from __future__ import annotations

import io
import json
import os

from fastapi import APIRouter, HTTPException, Response

from .. import db
from ..common import profile_or_404
from ..models import BeaconCreate, HandleSet

router = APIRouter()


def _public_base() -> str:
    return os.environ.get("QRME_PUBLIC_URL", "https://qrme.app").rstrip("/")


_STATUS_NOTE = {
    "departed": "this profile has departed; its memory remains with those "
                "who knew it",
    "restricted": "this profile is restricted pending an objection review",
    "terminated": "this profile has been terminated",
}


def _card(profile: dict, handle: str | None = None) -> dict:
    """Public summon card — never persona internals."""
    # Only an active profile is chat-reachable from a public summon; a
    # restricted profile's public surfaces are off, and departed/terminated
    # profiles never chat.
    reachable = profile["status"] == "active"
    return {
        "profile_id": profile["id"],
        "display_name": ("anonymous persona" if profile["anonymous"]
                         else profile["display_name"]),
        "handle": f"@{handle}" if handle else _handle_of(profile["id"]),
        "purpose": profile["purpose"],
        "status": profile["status"],
        "chat": (f"/profiles/{profile['id']}/chat" if reachable else None),
        "note": _STATUS_NOTE.get(profile["status"]),
    }


def _handle_of(profile_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT handle FROM handles WHERE profile_id=?", (profile_id,)
    ).fetchone()
    return f"@{row['handle']}" if row else None


# -- @handles ----------------------------------------------------------------

@router.put("/profiles/{profile_id}/handle")
def claim_handle(profile_id: str, body: HandleSet) -> dict:
    profile_or_404(profile_id)
    handle = body.handle.lstrip("@").lower()
    conn = db.connect()
    taken = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                         (handle,)).fetchone()
    if taken and taken["profile_id"] != profile_id:
        raise HTTPException(409, f"@{handle} is already claimed")
    conn.execute("DELETE FROM handles WHERE profile_id=?", (profile_id,))
    conn.execute(
        "INSERT INTO handles (handle, profile_id, created_at) VALUES (?,?,?)",
        (handle, profile_id, db.utcnow()),
    )
    conn.commit()
    return {"profile_id": profile_id, "handle": f"@{handle}",
            "summon": f"/summon?ref=@{handle}"}


# -- beacons: leave a profile behind -----------------------------------------

@router.post("/profiles/{profile_id}/beacons", status_code=201)
def place_beacon(profile_id: str, body: BeaconCreate) -> dict:
    profile_or_404(profile_id)
    conn = db.connect()
    beacon_id = db.new_id("bcn")
    conn.execute(
        "INSERT INTO beacons (id, profile_id, label, location, scans, active,"
        " created_at) VALUES (?,?,?,?,0,1,?)",
        (beacon_id, profile_id, body.label, body.location, db.utcnow()),
    )
    conn.commit()
    return {
        "id": beacon_id, "label": body.label, "location": body.location,
        "summon_url": f"{_public_base()}/summon?ref={beacon_id}",
        "qr_svg": f"/beacons/{beacon_id}/qr.svg",
    }


@router.get("/profiles/{profile_id}/beacons")
def list_beacons(profile_id: str) -> list[dict]:
    profile_or_404(profile_id)
    rows = db.connect().execute(
        "SELECT * FROM beacons WHERE profile_id=? ORDER BY created_at, rowid",
        (profile_id,)).fetchall()
    return [{**dict(r), "active": bool(r["active"])} for r in rows]


@router.delete("/beacons/{beacon_id}")
def pick_up_beacon(beacon_id: str) -> dict:
    """Pick a beacon back up: the placed QR stops summoning."""
    conn = db.connect()
    if not conn.execute("UPDATE beacons SET active=0 WHERE id=?",
                        (beacon_id,)).rowcount:
        raise HTTPException(404, "beacon not found")
    conn.commit()
    return {"id": beacon_id, "active": False}


@router.get("/beacons/{beacon_id}/qr.svg")
def beacon_qr(beacon_id: str) -> Response:
    """The printable QR code for a placed beacon."""
    row = db.connect().execute("SELECT id FROM beacons WHERE id=?",
                               (beacon_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "beacon not found")
    import segno

    buf = io.BytesIO()
    segno.make(f"{_public_base()}/summon?ref={beacon_id}",
               error="q").save(buf, kind="svg", scale=8, border=2,
                               dark="#161840", light="#F4E3C8")
    return Response(content=buf.getvalue(), media_type="image/svg+xml")


# -- the summon endpoint -----------------------------------------------------

@router.get("/summon")
def summon(ref: str) -> dict:
    """Resolve @handle, #tag, or a beacon token to summonable profiles."""
    conn = db.connect()

    if ref.startswith("@"):
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (ref[1:].lower(),)).fetchone()
        if row is None:
            raise HTTPException(404, f"no profile answers to {ref}")
        return {"type": "handle", "ref": ref,
                "profile": _card(profile_or_404(row["profile_id"]))}

    if ref.startswith("#"):
        tag = ref[1:].lower()
        rows = conn.execute(
            "SELECT m.profile_id, m.tags FROM marketplace m"
            " JOIN profiles p ON p.id = m.profile_id"
            " ORDER BY m.listed_at DESC").fetchall()
        cards = [
            _card(profile_or_404(r["profile_id"]))
            for r in rows
            if tag in [t.lower() for t in json.loads(r["tags"])]
        ]
        return {"type": "tag", "ref": ref, "profiles": cards}

    beacon = conn.execute("SELECT * FROM beacons WHERE id=?", (ref,)).fetchone()
    if beacon is None:
        raise HTTPException(404, "nothing answers to that reference")
    if not beacon["active"]:
        raise HTTPException(410, "this beacon has been picked up")
    conn.execute("UPDATE beacons SET scans = scans + 1 WHERE id=?", (ref,))
    conn.commit()
    return {"type": "beacon", "ref": ref,
            "label": beacon["label"], "location": beacon["location"],
            "scans": beacon["scans"] + 1,
            "profile": _card(profile_or_404(beacon["profile_id"]))}
