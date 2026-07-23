"""Objection, takedown, revocation & restricted state.

A real person — or their estate — can contest a profile that represents them.
Opening an objection immediately moves the profile to **restricted** (public
surfaces off, no new interactors) pending review, remembering the status it
held so a dismissal restores it. The owner re-attests their rights basis within
the review window; a reviewer then either **upholds** the objection (the
profile is **terminated** — its content erased, a tombstone left) or
**dismisses** it (the profile returns to whatever it was — active, or a
departed memorial).

Two consent-basis shortcuts bypass review because the standing party's rights
override preservation:

* a ``subject_consent`` subject may **withdraw** consent at any time; and
* an ``estate_authorization`` authorizer (or the subject) may **revoke**
  authorization at any time.

Both force termination immediately, even mid-review.

Interactions with the lifecycle states:

* **Memorial (departed).** A memorial can still be contested — an estate may
  need to take down a memorial that misrepresents the deceased. Opening an
  objection suspends the memorial (restricted); a dismissal restores it, an
  uphold/withdraw/revoke tears it down (terminated, anchors removed).
* **Succession.** A profile with an open objection cannot be succeeded — you
  cannot hand a contested identity to a new owner until it is resolved
  (enforced in ``profiles.succeed_profile``). Termination also clears any named
  successor so a torn-down profile can never be revived.

**Auditability.** Every lifecycle transition is written to ``objection_events``
and, when a PDI vault is configured, sealed into it. PDI hash-chains every
write, so the sealed copy is independently tamper-evident. ``GET
/objections/{id}/audit`` returns the timeline.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, Request

from .. import auth, db
from ..common import profile_or_404, require_owner
from ..models import ObjectionOpen, ObjectionResolve

router = APIRouter()
logger = logging.getLogger("qrme.governance")

# Bases whose standing party can force termination without review.
_REVOCABLE = {"subject_consent", "estate_authorization"}


def _objection_or_404(objection_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM objections WHERE id=?", (objection_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "objection not found")
    return dict(row)


def _audit(request: Request, objection_id: str, profile_id: str, event: str,
           actor: str, detail: dict | None = None) -> dict:
    """Record one lifecycle event locally and seal a copy into the PDI vault
    (when configured). The vault write is itself hash-chained by PDI, so the
    sealed record is independently verifiable."""
    conn = db.connect()
    event_id = db.new_id("obe")
    now = db.utcnow()
    payload = {"event": event, "actor": actor, "objection_id": objection_id,
               "profile_id": profile_id, "detail": detail or {}, "at": now}

    pdi_key = None
    pdi = request.app.state.pdi
    if pdi is not None:
        pdi_key = f"qrme/governance/{profile_id}/{objection_id}/{event_id}"
        try:
            pdi.put(pdi_key, json.dumps(payload, sort_keys=True))
        except Exception as exc:  # noqa: BLE001 — audit must not block the action
            logger.warning("PDI seal failed for %s/%s: %s",
                           objection_id, event, exc)
            pdi_key = None

    conn.execute(
        "INSERT INTO objection_events (id, objection_id, profile_id, event,"
        " actor, detail, pdi_key, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (event_id, objection_id, profile_id, event, actor,
         json.dumps(detail or {}), pdi_key, now),
    )
    conn.commit()
    logger.info("objection %s: %s by %s (sealed=%s)",
                objection_id, event, actor, pdi_key is not None)
    return {"id": event_id, "event": event, "actor": actor,
            "sealed": pdi_key is not None, "at": now}


def _terminate(profile_id: str, request: Request) -> None:
    """Erase a profile's content and leave a `terminated` tombstone. Distinct
    from a full owner delete (which removes the row entirely): the profile row
    survives so the objection record stays anchored and the handle/beacon
    cannot be re-summoned. Clears any named successor so a torn-down profile
    can never be revived through succession."""
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
    conn.execute(
        "UPDATE profiles SET status='terminated', successor_owner=NULL"
        " WHERE id=?", (profile_id,))
    conn.commit()


def has_open_objection(profile_id: str) -> bool:
    """True when a profile has an unresolved objection. Used by succession to
    refuse handing over a contested identity."""
    row = db.connect().execute(
        "SELECT 1 FROM objections WHERE profile_id=? AND status='open' LIMIT 1",
        (profile_id,)).fetchone()
    return row is not None


@router.post("/objections", status_code=201)
def open_objection(body: ObjectionOpen, request: Request) -> dict:
    """Open an objection (public: the objecting party need not own an account).
    Suspends the profile pending review — including a departed memorial, which
    an estate may contest. A terminated profile is already gone."""
    profile = profile_or_404(body.profile_id)
    if profile["status"] == "terminated":
        raise HTTPException(
            409, "profile is terminated; there is nothing left to object to")
    conn = db.connect()
    objection_id = db.new_id("obj")
    prior_status = profile["status"]        # active or departed (memorial)
    conn.execute(
        "INSERT INTO objections (id, profile_id, objector_ref, reason, status,"
        " prior_status, created_at) VALUES (?,?,?,?,'open',?,?)",
        (objection_id, body.profile_id, body.objector_ref, body.reason,
         prior_status, db.utcnow()),
    )
    conn.execute("UPDATE profiles SET status='restricted' WHERE id=?",
                 (body.profile_id,))
    conn.commit()
    _audit(request, objection_id, body.profile_id, "opened", "objector",
           {"reason": body.reason, "prior_status": prior_status})
    return {"id": objection_id, "profile_id": body.profile_id,
            "status": "open", "profile_status": "restricted",
            "prior_status": prior_status,
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


@router.get("/objections/{objection_id}/audit")
def objection_audit(objection_id: str, request: Request) -> dict:
    """The tamper-evident lifecycle timeline. Owner- or reviewer-gated (it can
    quote the objector's reason). Each event notes whether it was sealed into
    the PDI vault."""
    obj = _objection_or_404(objection_id)
    _require_owner_or_reviewer(obj["profile_id"], request)
    rows = db.connect().execute(
        "SELECT id, event, actor, detail, pdi_key, created_at"
        " FROM objection_events WHERE objection_id=? ORDER BY created_at, id",
        (objection_id,)).fetchall()
    events = [
        {"id": r["id"], "event": r["event"], "actor": r["actor"],
         "detail": json.loads(r["detail"] or "{}"),
         "sealed": r["pdi_key"] is not None, "pdi_key": r["pdi_key"],
         "at": r["created_at"]}
        for r in rows
    ]
    return {
        "objection_id": objection_id,
        "profile_id": obj["profile_id"],
        "status": obj["status"],
        "vault_backed": request.app.state.pdi is not None,
        "events": events,
    }


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
    _audit(request, objection_id, profile_id, "reattested", "owner")
    return {"id": objection_id, "reattested": True,
            "note": "basis re-attested; awaiting reviewer resolution"}


@router.post("/objections/{objection_id}/resolve")
def resolve_objection(objection_id: str, body: ObjectionResolve,
                      request: Request) -> dict:
    """Reviewer decision. Guarded by the reviewer role (QRME_ADMIN_TOKEN) so an
    owner cannot adjudicate an objection against their own profile. A dismissal
    restores the profile to whatever it was before the objection — active, or a
    departed memorial."""
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
        _audit(request, objection_id, obj["profile_id"], "upheld", "reviewer")
        _audit(request, objection_id, obj["profile_id"], "terminated", "system")
    else:
        # Restore the pre-objection status (active or a departed memorial).
        restored = obj["prior_status"] or "active"
        conn.execute("UPDATE profiles SET status=? WHERE id=?",
                     (restored, obj["profile_id"]))
        new_status, profile_status = "dismissed", restored
        _audit(request, objection_id, obj["profile_id"], "dismissed",
               "reviewer", {"restored_to": restored})
    conn.execute("UPDATE objections SET status=?, resolved_at=? WHERE id=?",
                 (new_status, db.utcnow(), objection_id))
    conn.commit()
    return {"id": objection_id, "status": new_status,
            "profile_status": profile_status}


@router.post("/objections/{objection_id}/withdraw")
def withdraw_consent(objection_id: str, request: Request) -> dict:
    """A ``subject_consent`` subject withdraws consent — honored immediately,
    even mid-review, forcing termination. Public: the subject acts through
    their objection. (For ``estate_authorization``, use ``/revoke``.)"""
    return _force_terminate(objection_id, request, basis="subject_consent",
                            status="withdrawn", actor="subject",
                            event="withdrawn")


@router.post("/objections/{objection_id}/revoke")
def revoke_authorization(objection_id: str, request: Request) -> dict:
    """Revoke the rights basis and force termination immediately. Works for
    ``subject_consent`` (the subject) and ``estate_authorization`` (the
    authorizing estate). ``public_figure_commentary`` has no consent to revoke
    — it must go through the review path."""
    obj = _objection_or_404(objection_id)
    if obj["status"] != "open":
        raise HTTPException(409, f"objection is already {obj['status']}")
    profile = profile_or_404(obj["profile_id"])
    basis = profile["consent_basis"]
    if basis not in _REVOCABLE:
        raise HTTPException(
            409, f"basis '{basis}' cannot be revoked; use the review path")
    actor = "subject" if basis == "subject_consent" else "estate"
    return _force_terminate(objection_id, request, basis=basis,
                            status="revoked", actor=actor, event="revoked")


def _force_terminate(objection_id: str, request: Request, *, basis: str,
                     status: str, actor: str, event: str) -> dict:
    """Shared teardown for withdrawal/revocation: verify the basis, terminate,
    revoke tokens, close the objection, and audit both the decision and the
    termination."""
    obj = _objection_or_404(objection_id)
    if obj["status"] != "open":
        raise HTTPException(409, f"objection is already {obj['status']}")
    profile = profile_or_404(obj["profile_id"])
    if profile["consent_basis"] != basis:
        raise HTTPException(
            409, f"this action applies only to {basis} profiles; this "
                 f"profile's basis is '{profile['consent_basis']}'")
    _terminate(obj["profile_id"], request)
    auth.revoke_subject(obj["profile_id"])
    conn = db.connect()
    conn.execute("UPDATE objections SET status=?, resolved_at=? WHERE id=?",
                 (status, db.utcnow(), objection_id))
    conn.commit()
    _audit(request, objection_id, obj["profile_id"], event, actor)
    _audit(request, objection_id, obj["profile_id"], "terminated", "system")
    return {"id": objection_id, "status": status,
            "profile_status": "terminated"}


def _require_owner_or_reviewer(profile_id: str, request: Request) -> None:
    """Allow either the profile owner or a platform reviewer. Reviewers need to
    read the audit trail to adjudicate; owners to see their own case."""
    try:
        auth.require_reviewer(request)
        return
    except HTTPException:
        pass
    require_owner(profile_id, request)
