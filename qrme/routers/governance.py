"""Objection, takedown & restricted state.

A real person — or their estate — can contest a profile that represents them.
Opening an objection immediately moves the profile to **restricted** (public
surfaces off, no new interactors) pending review. The owner is expected to
re-attest their rights basis within the review window; a reviewer then either
**upholds** the objection (the profile is **terminated** — its content erased,
a tombstone left) or **dismisses** it (the profile returns to active with the
objection recorded). A `subject_consent` subject may **withdraw** consent at
any time, which forces termination regardless of review.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import auth, db
from ..common import profile_or_404, require_owner
from ..models import ObjectionOpen, ObjectionResolve

router = APIRouter()


def _objection_or_404(objection_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM objections WHERE id=?", (objection_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "objection not found")
    return dict(row)


def _terminate(profile_id: str, request: Request) -> None:
    """Erase a profile's content and leave a `terminated` tombstone. Distinct
    from a full owner delete (which removes the row entirely): the profile row
    survives so the objection record stays anchored and the handle/beacon
    cannot be re-summoned."""
    conn = db.connect()
    pdi = request.app.state.pdi
    if pdi is not None:
        for key in conn.execute(
                "SELECT pdi_key FROM source_items WHERE profile_id=?"
                " AND pdi_key IS NOT NULL", (profile_id,)).fetchall():
            pdi.delete(key["pdi_key"])
    for table in ("source_items", "messages", "engagement", "posts",
                  "relationships", "surfaces", "marketplace", "handles",
                  "beacons", "creative_works", "perceptions", "active_handoffs",
                  "persona_embeddings", "biometric_context"):
        conn.execute(f"DELETE FROM {table} WHERE profile_id=?", (profile_id,))
    conn.execute("UPDATE profiles SET status='terminated' WHERE id=?",
                 (profile_id,))
    conn.commit()


@router.post("/objections", status_code=201)
def open_objection(body: ObjectionOpen, request: Request) -> dict:
    """Open an objection (public: the objecting party need not own an account).
    Moves the profile to restricted pending review."""
    profile = profile_or_404(body.profile_id)
    if profile["status"] in ("terminated", "departed"):
        raise HTTPException(
            409, f"profile is {profile['status']}; cannot be objected to")
    conn = db.connect()
    objection_id = db.new_id("obj")
    conn.execute(
        "INSERT INTO objections (id, profile_id, objector_ref, reason, status,"
        " created_at) VALUES (?,?,?,?,'open',?)",
        (objection_id, body.profile_id, body.objector_ref, body.reason,
         db.utcnow()),
    )
    conn.execute("UPDATE profiles SET status='restricted' WHERE id=?",
                 (body.profile_id,))
    conn.commit()
    return {"id": objection_id, "profile_id": body.profile_id,
            "status": "open", "profile_status": "restricted",
            "note": "profile restricted pending review; the owner must "
                    "re-attest their rights basis"}


@router.get("/objections/{objection_id}")
def get_objection(objection_id: str) -> dict:
    """Public status check for the objecting party (their proof reference is
    returned so they can confirm it's their case)."""
    obj = _objection_or_404(objection_id)
    return {"id": obj["id"], "profile_id": obj["profile_id"],
            "status": obj["status"], "reattested": bool(obj["reattested"]),
            "objector_ref": obj["objector_ref"]}


@router.get("/profiles/{profile_id}/objections")
def list_objections(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM objections WHERE profile_id=? ORDER BY created_at",
        (profile_id,)).fetchall()
    return [dict(r) for r in rows]


@router.post("/profiles/{profile_id}/objections/{objection_id}/attest")
def reattest_basis(profile_id: str, objection_id: str,
                   request: Request) -> dict:
    """The owner re-attests their rights basis within the review window."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    obj = _objection_or_404(objection_id)
    if obj["profile_id"] != profile_id:
        raise HTTPException(404, "objection not found for this profile")
    if obj["status"] != "open":
        raise HTTPException(409, f"objection is already {obj['status']}")
    conn = db.connect()
    conn.execute("UPDATE objections SET reattested=1 WHERE id=?",
                 (objection_id,))
    conn.commit()
    return {"id": objection_id, "reattested": True,
            "note": "basis re-attested; awaiting reviewer resolution"}


@router.post("/objections/{objection_id}/resolve")
def resolve_objection(objection_id: str, body: ObjectionResolve,
                      request: Request) -> dict:
    """Reviewer decision. Guarded by the reviewer role (QRME_ADMIN_TOKEN) so an
    owner cannot adjudicate an objection against their own profile."""
    auth.require_reviewer(request)
    obj = _objection_or_404(objection_id)
    if obj["status"] != "open":
        raise HTTPException(409, f"objection is already {obj['status']}")
    if body.outcome not in ("uphold", "dismiss"):
        raise HTTPException(422, "outcome must be 'uphold' or 'dismiss'")
    conn = db.connect()
    if body.outcome == "uphold":
        _terminate(obj["profile_id"], request)
        auth.revoke_subject(obj["profile_id"])
        new_status, profile_status = "upheld", "terminated"
    else:
        conn.execute("UPDATE profiles SET status='active' WHERE id=?",
                     (obj["profile_id"],))
        new_status, profile_status = "dismissed", "active"
    conn.execute("UPDATE objections SET status=?, resolved_at=? WHERE id=?",
                 (new_status, db.utcnow(), objection_id))
    conn.commit()
    return {"id": objection_id, "status": new_status,
            "profile_status": profile_status}


@router.post("/objections/{objection_id}/withdraw")
def withdraw_consent(objection_id: str, request: Request) -> dict:
    """A `subject_consent` subject withdraws consent — honored immediately,
    even mid-review, and forces termination (the subject's rights override
    preservation). Public: the subject acts through their objection."""
    obj = _objection_or_404(objection_id)
    if obj["status"] != "open":
        raise HTTPException(409, f"objection is already {obj['status']}")
    profile = profile_or_404(obj["profile_id"])
    if profile["consent_basis"] != "subject_consent":
        raise HTTPException(
            409, "withdrawal applies only to subject-consent profiles; this "
                 "profile's basis is different — use the review path")
    _terminate(obj["profile_id"], request)
    auth.revoke_subject(obj["profile_id"])
    conn = db.connect()
    conn.execute("UPDATE objections SET status='withdrawn', resolved_at=?"
                 " WHERE id=?", (db.utcnow(), objection_id))
    conn.commit()
    return {"id": objection_id, "status": "withdrawn",
            "profile_status": "terminated"}
