"""Training-data licensing & derivable specialist agents.

An owner can license their profile's expertise; a buyer acquires a license and,
when the terms permit, **derives their own specialist agent** from it — a new
profile the buyer owns, seeded from the source's persona under a recorded
license (provenance kept in `licensed_from`). Licenses are revocable, and every
derivation is traceable back to the source.

Kinds:
- ``consult``  — licensed use of the profile as-is (no derivative agent).
- ``finetune`` — the buyer may derive an agent specialized from this expertise.
- ``clone``    — the buyer may derive a full stand-alone copy.

`finetune`/`clone` set ``allow_derivatives``; ``consult`` does not.
"""

from __future__ import annotations

import secrets
from datetime import date

from fastapi import APIRouter, HTTPException, Request

from .. import auth, db
from ..common import age_of, interactor_or_404, profile_or_404, require_owner
from ..models import LicenseOffer


def _derived_persona(source: dict, kind: str) -> str:
    """Seed a derived agent's persona from the licensed source, keeping a clear
    licensed-expertise framing (and provenance line)."""
    base = source["persona"]
    if kind == "clone":
        return (f"{base}\n\n(Licensed clone of {source['display_name']}, "
                "operated under license by its buyer.)")
    return (f"A specialist agent whose expertise is licensed from "
            f"{source['display_name']}. Draw on that expertise:\n\n{base}\n\n"
            "(Licensed derivative — stay within the licensed domain.)")

router = APIRouter()


def _buyer(request: Request) -> str:
    """The authenticated buyer — identity comes from an interactor token, not a
    body field, so a buyer can only act as themselves."""
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["role"] != "interactor":
        raise HTTPException(403, "a buyer acts with an interactor token")
    return who["subject_id"]


def _offer(profile_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM license_offers WHERE profile_id=?",
        (profile_id,)).fetchone()
    return dict(row) if row else None


@router.put("/profiles/{profile_id}/license")
def set_license(profile_id: str, body: LicenseOffer, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    if body.kind not in ("consult", "finetune", "clone"):
        raise HTTPException(422, "kind must be consult, finetune, or clone")
    allow = body.allow_derivatives or body.kind in ("finetune", "clone")
    conn = db.connect()
    conn.execute(
        "INSERT INTO license_offers (profile_id, kind, price, currency, terms,"
        " allow_derivatives, created_at) VALUES (?,?,?,?,?,?,?)"
        " ON CONFLICT (profile_id) DO UPDATE SET kind=excluded.kind,"
        " price=excluded.price, currency=excluded.currency,"
        " terms=excluded.terms, allow_derivatives=excluded.allow_derivatives",
        (profile_id, body.kind, body.price, body.currency, body.terms,
         int(allow), db.utcnow()),
    )
    conn.commit()
    return {"profile_id": profile_id, "kind": body.kind, "price": body.price,
            "currency": body.currency, "allow_derivatives": bool(allow)}


@router.get("/profiles/{profile_id}/license")
def get_license(profile_id: str) -> dict:
    """Public: prospective buyers see the offer terms."""
    profile_or_404(profile_id)
    offer = _offer(profile_id)
    if offer is None:
        raise HTTPException(404, "this profile is not offered for license")
    return {"profile_id": profile_id, "kind": offer["kind"],
            "price": offer["price"], "currency": offer["currency"],
            "terms": offer["terms"],
            "allow_derivatives": bool(offer["allow_derivatives"])}


@router.delete("/profiles/{profile_id}/license", status_code=204)
def unlist_license(profile_id: str, request: Request) -> None:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    if not conn.execute("DELETE FROM license_offers WHERE profile_id=?",
                        (profile_id,)).rowcount:
        raise HTTPException(404, "this profile is not offered for license")
    conn.commit()


@router.post("/profiles/{profile_id}/license/acquire", status_code=201)
def acquire_license(profile_id: str, request: Request) -> dict:
    """A buyer acquires a license against the source profile."""
    profile_or_404(profile_id)
    buyer_id = _buyer(request)
    interactor_or_404(buyer_id)
    offer = _offer(profile_id)
    if offer is None:
        raise HTTPException(404, "this profile is not offered for license")
    conn = db.connect()
    grant_id = db.new_id("lic")
    token = f"lic_{secrets.token_urlsafe(24)}"
    conn.execute(
        "INSERT INTO license_grants (id, profile_id, buyer_id, kind, token,"
        " revoked, created_at) VALUES (?,?,?,?,?,0,?)",
        (grant_id, profile_id, buyer_id, offer["kind"], token, db.utcnow()),
    )
    conn.commit()
    return {"grant_id": grant_id, "profile_id": profile_id, "kind": offer["kind"],
            "token": token, "terms": offer["terms"],
            "can_derive": bool(offer["allow_derivatives"])}


@router.get("/profiles/{profile_id}/licenses")
def list_licenses(profile_id: str, request: Request) -> list[dict]:
    """Owner view: who holds a license on this profile."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT id, buyer_id, kind, derived_profile_id, revoked, created_at"
        " FROM license_grants WHERE profile_id=? ORDER BY created_at",
        (profile_id,)).fetchall()
    return [{**dict(r), "revoked": bool(r["revoked"])} for r in rows]


@router.post("/profiles/{profile_id}/license/{grant_id}/derive",
             status_code=201)
def derive_agent(profile_id: str, grant_id: str, request: Request) -> dict:
    """Fine-tune / clone: the buyer derives their own specialist agent from the
    licensed expertise. The new profile is owned by the buyer, its persona
    seeded from the source, and its origin recorded in `licensed_from`."""
    source = profile_or_404(profile_id)
    buyer_id = _buyer(request)
    buyer = interactor_or_404(buyer_id)
    conn = db.connect()
    grant = conn.execute(
        "SELECT * FROM license_grants WHERE id=? AND profile_id=?",
        (grant_id, profile_id)).fetchone()
    if grant is None:
        raise HTTPException(404, "license not found")
    if grant["buyer_id"] != buyer_id:
        raise HTTPException(403, "this license belongs to another buyer")
    if grant["revoked"]:
        raise HTTPException(403, "this license has been revoked")
    offer = _offer(profile_id)
    if offer is None or not offer["allow_derivatives"]:
        raise HTTPException(
            403, "this license does not permit deriving an agent (consult only)")
    if grant["derived_profile_id"]:
        raise HTTPException(409, "an agent has already been derived here")
    # The buyer becomes an owner of a real profile — hold them to the same
    # adult bar as any owner deriving a persona.
    if not buyer["birthdate"] or age_of(
            date.fromisoformat(buyer["birthdate"])) < 18:
        raise HTTPException(403, "deriving an agent requires a verified-adult buyer")

    new_id = db.new_id("prf")
    derived_persona = _derived_persona(source, offer["kind"])
    conn.execute(
        "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
        " demographics, sources, anonymous, adult_mode, interaction_scope,"
        " moderation_mode, aging_enabled, base_age, purpose, maturity,"
        " cloud_contribution, licensed_from, created_at)"
        " VALUES (?,?,?,?,?,'{}','[]',0,0,'reactive','auto',0,NULL,?,?,0,?,?)",
        (new_id, buyer_id, "fictional",
         f"{source['display_name']} — licensed {offer['kind']}",
         derived_persona, "enterprise_agent", source["maturity"], profile_id,
         db.utcnow()),
    )
    conn.execute("UPDATE license_grants SET derived_profile_id=? WHERE id=?",
                 (new_id, grant_id))
    conn.commit()
    token = auth.issue("owner", new_id)
    return {"derived_profile_id": new_id, "owner_id": buyer_id,
            "licensed_from": profile_id, "kind": offer["kind"],
            "owner_token": token}


@router.delete("/licenses/{grant_id}")
def revoke_license(grant_id: str, request: Request) -> dict:
    """The source owner revokes a license."""
    conn = db.connect()
    grant = conn.execute("SELECT * FROM license_grants WHERE id=?",
                         (grant_id,)).fetchone()
    if grant is None:
        raise HTTPException(404, "license not found")
    require_owner(grant["profile_id"], request)
    conn.execute("UPDATE license_grants SET revoked=1 WHERE id=?", (grant_id,))
    conn.commit()
    return {"grant_id": grant_id, "revoked": True}
