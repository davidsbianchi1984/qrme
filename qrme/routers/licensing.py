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

**What a derivation carries.** The amended claims draw the line: what may
travel is parameter-level substance — "latent embeddings that maintain
cross-session state for consistent agent behavior **without storing raw user
data**". So a derive copies the profile's own substance (its knowledge items,
its characteristics, and — on a clone — an aggregate adaptation summary), and
never the raw material underneath: interactor messages and per-relationship
embeddings, the person's voice, vaulted content, and marketplace pack items
all stay behind. Every derivation writes a **manifest** recording exactly
what crossed and what was withheld, and why, readable by both parties.
"""

from __future__ import annotations

import json
import secrets
from datetime import date

from fastapi import APIRouter, HTTPException, Request

from .. import auth, db
from ..common import (age_of, interactor_or_404, profile_or_404,
                      require_may_publish, require_owner)
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


def _adaptation_summary(conn, profile_id: str) -> dict | None:
    """Aggregate the source's latent persona embeddings into one disposition
    vector — dimension means across every relationship, plus how many fed it.

    This is the artifact the amended claims let travel: cross-session state at
    the parameter level. No interactor ids, no per-relationship vectors, no
    message content — a buyer learns how the persona carries itself overall,
    never with whom."""
    rows = conn.execute(
        "SELECT vector FROM persona_embeddings WHERE profile_id=?",
        (profile_id,)).fetchall()
    if not rows:
        return None
    dims: dict[str, float] = {}
    for row in rows:
        for name, value in json.loads(row["vector"]).items():
            dims[name] = dims.get(name, 0.0) + value
    return {"disposition": {n: round(v / len(rows), 3)
                            for n, v in dims.items()},
            "relationships_aggregated": len(rows)}


def _transfer_substance(conn, source: dict, new_id: str, kind: str) -> dict:
    """Copy the licensed substance onto the derived profile and return the
    manifest (`carried` / `withheld`) describing what crossed the line."""
    carried: dict = {}
    withheld: list[dict] = []

    # The profile's own knowledge travels; anything whose custody is not the
    # owner's to hand over does not.
    items = conn.execute(
        "SELECT * FROM source_items WHERE profile_id=? ORDER BY created_at",
        (source["id"],)).fetchall()
    copied = vaulted = packed = 0
    for item in items:
        if item["pack_id"]:
            packed += 1
            continue
        if item["content"] is None or item["pdi_key"]:
            vaulted += 1
            continue
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,NULL,?)",
            (db.new_id("src"), new_id, item["kind"], item["title"],
             item["content"], db.utcnow()))
        copied += 1
    if copied:
        carried["knowledge_items"] = copied
    if vaulted:
        withheld.append({"item": f"{vaulted} vaulted source item(s)",
                         "reason": "sealed in the PDI vault; custody does "
                                   "not transfer with a license"})
    if packed:
        withheld.append({"item": f"{packed} knowledge-pack item(s)",
                         "reason": "marketplace pack content stays under "
                                   "its own license"})

    # Characteristics: the dials, appearance and demographics that make the
    # expertise speak the way it does.
    dials_row = conn.execute(
        "SELECT dials FROM steering_settings WHERE subject_id=?",
        (source["id"],)).fetchone()
    if dials_row and json.loads(dials_row["dials"]):
        conn.execute(
            "INSERT INTO steering_settings (subject_id, dials, updated_at)"
            " VALUES (?,?,?) ON CONFLICT (subject_id) DO UPDATE SET"
            " dials=excluded.dials, updated_at=excluded.updated_at",
            (new_id, dials_row["dials"], db.utcnow()))
        carried["steering_dials"] = len(json.loads(dials_row["dials"]))
    extras = {}
    if source["appearance"]:
        extras["appearance"] = source["appearance"]
    if source["demographics"] and json.loads(source["demographics"]):
        extras["demographics"] = source["demographics"]
    if extras:
        placeholders = ", ".join(f"{k}=?" for k in extras)
        conn.execute(f"UPDATE profiles SET {placeholders} WHERE id=?",
                     (*extras.values(), new_id))
        carried["characteristics"] = sorted(extras)

    # A clone also carries the adaptation artifact — aggregated, anonymous.
    if kind == "clone":
        summary = _adaptation_summary(conn, source["id"])
        if summary:
            conn.execute(
                "INSERT INTO source_items (id, profile_id, kind, title,"
                " content, pdi_key, pack_id, created_at)"
                " VALUES (?,?,?,?,?,NULL,NULL,?)",
                (db.new_id("src"), new_id, "knowledge",
                 "licensed adaptation summary",
                 json.dumps(summary), db.utcnow()))
            carried["adaptation_summary"] = summary
    else:
        withheld.append({"item": "adaptation summary",
                         "reason": "aggregate disposition travels on a "
                                   "clone license only"})

    # What never travels, whatever the kind.
    withheld.append({"item": "interactor messages and per-relationship "
                             "embeddings",
                     "reason": "raw interactor data never travels — the "
                               "relationships belong to the people in them"})
    if conn.execute("SELECT 1 FROM voice_consents WHERE profile_id=?"
                    " AND revoked_at IS NULL", (source["id"],)).fetchone():
        withheld.append({"item": "voice print",
                         "reason": "the voice is the person's biometric "
                                   "likeness; their consent does not "
                                   "transfer with a license"})
    return {"carried": carried, "withholdings": withheld}

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
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    # A memorial is not for sale. Sunset leaves the living owner their token,
    # so this route stayed open on a departed profile long after the person
    # whose expertise is being licensed could be asked about it.
    require_may_publish(profile)
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
def get_license(profile_id: str, request: Request) -> dict:
    """Public: prospective buyers see the offer terms. A rated profile's
    offer is itself age-gated — the shop window, not just the sale."""
    profile = profile_or_404(profile_id)
    if profile["adult_mode"]:
        from .. import rated
        if not rated.buyer_is_adult(request):
            raise HTTPException(
                403, "this profile's license is age-restricted (18+); "
                     "present a verified-18+ interactor token")
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
    profile = profile_or_404(profile_id)
    # Before the caller is identified, not after.
    #
    # Termination revokes the *owner's* token, so every owner-gated route on a
    # terminated profile answers 401 and the profile reads as closed. This
    # route is authorised by the **buyer's** interactor token, which
    # termination never touches — so a profile terminated on an upheld
    # objection went on selling licences to strangers.
    require_may_publish(profile)
    buyer_id = _buyer(request)
    buyer = interactor_or_404(buyer_id)
    if profile["adult_mode"]:
        # Rated commerce: acquiring a rated profile's license requires a
        # verified-adult buyer, not just a token.
        if not buyer["birthdate"] or age_of(
                date.fromisoformat(buyer["birthdate"])) < 18:
            raise HTTPException(
                403, "acquiring a license on a rated profile requires a "
                     "verified-18+ buyer")
    offer = _offer(profile_id)
    if offer is None:
        raise HTTPException(404, "this profile is not offered for license")
    if offer["allow_derivatives"] and (
            not buyer["birthdate"]
            or age_of(date.fromisoformat(buyer["birthdate"])) < 18):
        # The same bar `derive` applies, applied at the till instead.
        #
        # Without this a minor could buy a clone licence, be told
        # `can_derive: true`, have the fee credited to the seller at sale
        # time — and then be refused the only thing the licence is for. The
        # money moves here; refusing at delivery leaves somebody paid for
        # something they may not hand over.
        raise HTTPException(
            403, "a licence that permits deriving an agent requires a "
                 "verified-18+ buyer — the same bar deriving one does, "
                 "applied before the fee rather than after")
    conn = db.connect()
    grant_id = db.new_id("lic")
    token = f"lic_{secrets.token_urlsafe(24)}"
    conn.execute(
        "INSERT INTO license_grants (id, profile_id, buyer_id, kind, token,"
        " revoked, created_at) VALUES (?,?,?,?,?,0,?)",
        (grant_id, profile_id, buyer_id, offer["kind"], token, db.utcnow()),
    )
    conn.commit()
    # The fee accrues to the source profile's creator at sale time.
    from .. import ledger
    ledger.credit(profile["owner_id"], "license_fee", grant_id,
                  offer["price"], offer["currency"],
                  memo=f"{offer['kind']} license · {profile['display_name']}")
    return {"grant_id": grant_id, "profile_id": profile_id, "kind": offer["kind"],
            "token": token, "terms": offer["terms"],
            "can_derive": bool(offer["allow_derivatives"])}


@router.get("/profiles/{profile_id}/licenses")
def list_licenses(profile_id: str, request: Request) -> list[dict]:
    """Owner view: who holds a license on this profile."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    rows = conn.execute(
        "SELECT id, buyer_id, kind, derived_profile_id, revoked, created_at"
        " FROM license_grants WHERE profile_id=? ORDER BY created_at",
        (profile_id,)).fetchall()
    out = []
    for r in rows:
        manifest = conn.execute(
            "SELECT carried, withheld FROM license_manifests WHERE grant_id=?",
            (r["id"],)).fetchone()
        out.append({**dict(r), "revoked": bool(r["revoked"]),
                    "manifest": ({"carried": json.loads(manifest["carried"]),
                                  "withholdings": json.loads(manifest["withheld"])}
                                 if manifest else None)})
    # Leases ride the same list: an organization holding the profile as a
    # leased department is a licensee like any buyer, and the owner's view of
    # who uses their expertise should not depend on which table it sits in.
    for lease in conn.execute(
            "SELECT l.*, o.name AS org_name FROM license_leases l"
            " JOIN organizations o ON o.id=l.org_id WHERE l.profile_id=?"
            " ORDER BY l.created_at", (profile_id,)).fetchall():
        out.append({"id": lease["id"], "buyer_id": lease["org_name"],
                    "kind": "lease", "derived_profile_id": None,
                    "revoked": bool(lease["revoked"]),
                    "created_at": lease["created_at"], "manifest": None})
    return out


@router.post("/profiles/{profile_id}/license/{grant_id}/derive",
             status_code=201)
def derive_agent(profile_id: str, grant_id: str, request: Request) -> dict:
    """Fine-tune / clone: the buyer derives their own specialist agent from the
    licensed expertise. The new profile is owned by the buyer, its persona
    seeded from the source, and its origin recorded in `licensed_from`."""
    source = profile_or_404(profile_id)
    # The largest thing anyone can do with somebody else's profile: mint a new
    # one from its persona, owned by the buyer, with its own owner token. It
    # asked whether the *licence* was still good and never whether the
    # *profile* was.
    require_may_publish(source)
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
    # The buyer paid for expertise; hand the expertise over, not a paragraph
    # about it. Substance crosses under the manifest's rules — the profile's
    # own knowledge and characteristics travel, raw interactor data, voice,
    # vaulted and pack content never do — and the manifest is written in the
    # same transaction as the derivation it describes.
    manifest = _transfer_substance(conn, source, new_id, offer["kind"])
    conn.execute(
        "INSERT INTO license_manifests (grant_id, carried, withheld,"
        " created_at) VALUES (?,?,?,?)",
        (grant_id, json.dumps(manifest["carried"]),
         json.dumps(manifest["withholdings"]), db.utcnow()))
    conn.execute("UPDATE license_grants SET derived_profile_id=? WHERE id=?",
                 (new_id, grant_id))
    conn.commit()
    token = auth.issue("owner", new_id)
    return {"derived_profile_id": new_id, "owner_id": buyer_id,
            "licensed_from": profile_id, "kind": offer["kind"],
            "owner_token": token, "manifest": manifest}


@router.delete("/licenses/{grant_id}")
def revoke_license(grant_id: str, request: Request) -> dict:
    """The source owner revokes a license — a buyer's grant or an
    organization's lease; both live on the owner's licenses list and both
    revoke through this one door."""
    conn = db.connect()
    grant = conn.execute("SELECT * FROM license_grants WHERE id=?",
                         (grant_id,)).fetchone()
    if grant is not None:
        require_owner(grant["profile_id"], request)
        conn.execute("UPDATE license_grants SET revoked=1 WHERE id=?",
                     (grant_id,))
        conn.commit()
        return {"grant_id": grant_id, "revoked": True}
    lease = conn.execute("SELECT * FROM license_leases WHERE id=?",
                         (grant_id,)).fetchone()
    if lease is None:
        raise HTTPException(404, "license not found")
    require_owner(lease["profile_id"], request)
    # The department stands but is silent from the next coordination on —
    # revocation is the owner's hand on the switch, not a renegotiation.
    conn.execute("UPDATE license_leases SET revoked=1 WHERE id=?",
                 (grant_id,))
    conn.commit()
    return {"grant_id": grant_id, "revoked": True}
