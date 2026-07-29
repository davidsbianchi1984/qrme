"""Owner-side profile management: CRUD, sources, surfaces, stats,
marketplace, export, and erasure."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request

from .. import (auth, companion, composite, db, identity, persona, storage,
                terms, tiers)
from ..common import (
    age_of, profile_or_404, profile_out, require_owner, source_items,
)
from ..models import (
    CompositeCreate, EmbodimentAdd, GenesisCreate, MarketplaceList,
    ProfileCreate, ProfileOut, ProfileUpdate, SourceAdd, SucceedRequest,
    SurfacesSet,
)

router = APIRouter()


def _enrol(account_id: str, plan: str | None) -> None:
    """Put a new account on a plan; leave an existing member's alone.

    Called from both creation paths. Written once rather than inline twice,
    because "genesis quietly enrolled people on a different plan from the
    ordinary form" is exactly the kind of divergence two copies produce.
    """
    if plan is None and tiers.plan_of(account_id) != "visitor":
        return                       # already a member — do not downgrade them
    tiers.subscribe(account_id, plan or tiers.DEFAULT_PLAN)


# The signup key is a gate on the *HTTP* surface — who may create a profile
# on this deployment — so it rides as a route dependency. In-process callers
# (seeding a starter collection) are the operator already and don't pass
# through it.
@router.post("/profiles", status_code=201,
             dependencies=[Depends(auth.require_signup_key)])
def create_profile(body: ProfileCreate) -> dict:
    if not body.terms_consent:
        raise HTTPException(
            403, "acceptance of the Terms of Service is required to create "
                 "a profile (GET /terms)")
    if body.kind == "hybrid":
        # A hybrid is born from its constituents, not typed free-hand — the
        # composite route validates every source and records the blend.
        raise HTTPException(
            422, "hybrid profiles are created via POST /profiles/composite, "
                 "from at least two source profiles")
    owner_age = age_of(body.verification.birthdate)
    if owner_age < 18 and not body.verification.guardian_consent:
        raise HTTPException(403, "owners under 18 require parent/guardian consent")
    if body.adult_mode and owner_age < 18:
        raise HTTPException(403, "adult mode requires a verified adult owner")
    if body.adult_mode and body.kind == "other_person":
        # Hard line: never a rated persona of another real person — only
        # the verified adult owner themself, or a fictional character.
        #
        # **Checked before the storage question, and the order is the point.**
        # The first version asked "can your plan hold rated content" first, so
        # this request came back 402 *pay $20* when the true answer is 403
        # *never, at any price*. A payment response in front of a hard line
        # tells somebody the line is a price, which is the one impression this
        # particular refusal must never give. The suite caught it in
        # `test_a_real_likeness_can_never_be_rated`.
        raise HTTPException(
            403, "adult mode is never available for a profile of another "
                 "real person")
    if body.adult_mode:
        # A rated profile's content is not something to hold in the clear.
        #
        # Checked against the plan this request lands on rather than the one
        # the account holds *now*: creation is also enrolment, so a brand-new
        # account is still "visitor" at this line, and reading the current plan
        # refused every rated profile ever created.
        landing = getattr(body, "plan", None) or tiers.plan_of(body.owner_id)
        if landing == "visitor":
            landing = tiers.DEFAULT_PLAN
        try:
            storage.require(landing, "rated_content")
        except storage.StorageError as exc:
            raise HTTPException(402, str(exc)) from None
    if body.kind == "other_person" and body.consent is None:
        raise HTTPException(
            422, "profiles of another real person require a consent/rights record")

    profile_id = db.new_id("prf")
    conn = db.connect()
    conn.execute(
        "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
        " demographics, sources, anonymous, adult_mode, interaction_scope,"
        " moderation_mode, aging_enabled, base_age, consent_basis,"
        " consent_attestor, successor_owner, purpose, maturity,"
        " cloud_contribution, terms_version, terms_accepted_at, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            profile_id, body.owner_id, body.kind, body.display_name,
            body.persona, json.dumps(body.demographics),
            json.dumps(body.sources), int(body.anonymous),
            int(body.adult_mode), body.interaction_scope, body.moderation_mode,
            int(body.aging_enabled), body.base_age,
            body.consent.basis if body.consent else None,
            body.consent.attestor if body.consent else None,
            body.successor_owner, body.purpose, body.maturity,
            int(body.cloud_contribution), terms.TERMS_VERSION, db.utcnow(),
            db.utcnow(),
        ),
    )
    conn.commit()
    # Language chosen at the setup gateway: the profile speaks it from its
    # very first reply.
    if body.language:
        from .. import i18n
        if body.language not in i18n.SUPPORTED:
            raise HTTPException(
                422, f"language must be one of {', '.join(i18n.SUPPORTED)}")
        i18n.set_language(profile_id, body.language)
    # The standing first friend. Silent when there is nothing to install —
    # an unseeded deployment has no founder, and a cosmetic default must not
    # be a reason profile creation fails.
    from .. import friends
    friends.install_founder(profile_id)
    # Making something is what a membership is *for*, so creating a profile is
    # where an account joins one. Free unless a plan is named: putting somebody
    # on a paid plan they did not ask for is the wrong default even at a fair
    # price, and the free tier is honest about what it is rather than quiet.
    # An existing member keeps the plan they have rather than being downgraded
    # by making a second profile.
    _enrol(body.owner_id, getattr(body, "plan", None))
    token = auth.issue("owner", profile_id)
    out = {**profile_out(profile_or_404(profile_id), owner=True).model_dump(),
           "owner_token": token}
    out["membership"] = tiers.membership(body.owner_id)
    if body.language:
        out["language"] = body.language
    return out


@router.post("/profiles/composite", status_code=201,
             dependencies=[Depends(auth.require_signup_key)])
def create_composite(body: CompositeCreate) -> dict:
    """A hybrid profile blended from several existing ones (spec [0038]).

    Sources must be the caller's own profiles or marketplace-listed; departed
    profiles are allowed (blending grandparents who are gone is the spec's own
    example), rated ones never. The blend is recorded per-constituent and
    published at GET /profiles/{id}/composition.
    """
    if not body.terms_consent:
        raise HTTPException(
            403, "acceptance of the Terms of Service is required to create "
                 "a profile (GET /terms)")
    owner_age = age_of(body.verification.birthdate)
    if owner_age < 18 and not body.verification.guardian_consent:
        raise HTTPException(403, "owners under 18 require parent/guardian consent")
    try:
        resolved = composite.resolve_sources(body)
    except composite.CompositeError as e:
        raise HTTPException(403, str(e))
    persona_text, demographics = composite.blend_persona(resolved)

    profile_id = db.new_id("prf")
    conn = db.connect()
    conn.execute(
        "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
        " demographics, sources, anonymous, adult_mode, interaction_scope,"
        " moderation_mode, aging_enabled, base_age, purpose, maturity,"
        " cloud_contribution, terms_version, terms_accepted_at, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,0,'reactive','auto',0,NULL,?,?,0,?,?,?)",
        (profile_id, body.owner_id, "hybrid", body.display_name, persona_text,
         json.dumps(demographics), json.dumps([]), int(body.anonymous),
         body.purpose, body.maturity, terms.TERMS_VERSION, db.utcnow(),
         db.utcnow()),
    )
    conn.commit()
    composite.record(profile_id, resolved)
    if body.language:
        from .. import i18n
        if body.language not in i18n.SUPPORTED:
            raise HTTPException(
                422, f"language must be one of {', '.join(i18n.SUPPORTED)}")
        i18n.set_language(profile_id, body.language)
    from .. import friends
    friends.install_founder(profile_id)
    _enrol(body.owner_id, body.plan)
    token = auth.issue("owner", profile_id)
    out = {**profile_out(profile_or_404(profile_id), owner=True).model_dump(),
           "owner_token": token,
           "composition": composite.composition(profile_id)}
    out["membership"] = tiers.membership(body.owner_id)
    return out


@router.get("/profiles/{profile_id}/composition")
def get_composition(profile_id: str) -> dict:
    """What a hybrid is blended from — readable by anyone, the same open
    stance as /transparency: the blend is the profile's provenance."""
    profile = profile_or_404(profile_id)
    if profile["kind"] != "hybrid":
        raise HTTPException(404, "this profile is not a hybrid")
    return {"profile_id": profile_id,
            "sources": composite.composition(profile_id),
            "policy": "a hybrid acknowledges openly that it is a blend and "
                      "never claims to be any single constituent"}


@router.post("/profiles/genesis", status_code=201)
def genesis_profile(body: GenesisCreate) -> dict:
    """A profile born from a short interview. Omit ``display_name`` and the
    profile chooses its own name from the answers."""
    owner_age = age_of(body.verification.birthdate)
    if owner_age < 18 and not body.verification.guardian_consent:
        raise HTTPException(403, "owners under 18 require parent/guardian consent")
    answers = body.answers.model_dump()
    name = body.display_name or companion.self_chosen_name(answers)
    profile_id = db.new_id("prf")
    conn = db.connect()
    conn.execute(
        "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
        " demographics, sources, anonymous, adult_mode, interaction_scope,"
        " moderation_mode, aging_enabled, base_age, purpose, maturity,"
        " cloud_contribution, created_at)"
        " VALUES (?,?,?,?,?,'{}','[]',0,0,?,'auto',0,NULL,?,?,0,?)",
        (profile_id, body.owner_id, body.kind, name,
         companion.persona_from_answers(answers), body.interaction_scope,
         body.purpose, body.maturity, db.utcnow()),
    )
    conn.commit()
    _enrol(body.owner_id, getattr(body, "plan", None))
    token = auth.issue("owner", profile_id)
    return {**profile_out(profile_or_404(profile_id), owner=True).model_dump(),
            "owner_token": token,
            "membership": tiers.membership(body.owner_id)}


@router.get("/profiles/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: str, request: Request) -> ProfileOut:
    """Public, so it is redacted for everyone but the owner.

    The request is here to answer one question — *is this the owner asking?* —
    because an anonymous profile returns its real name to them and to nobody
    else. Public and unredacted was the previous combination, and it made
    `anonymous` a property of the four surfaces that render a profile rather
    than of the profile itself.
    """
    return profile_out(profile_or_404(profile_id), request)


# -- Embodiments: the profile in a physical body -----------------------------

@router.post("/profiles/{profile_id}/embodiments", status_code=201)
def add_embodiment(profile_id: str, body: EmbodimentAdd, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    conn.execute(
        "INSERT OR REPLACE INTO embodiments (profile_id, name, kind, has_llm,"
        " created_at) VALUES (?,?,?,?,?)",
        (profile_id, body.name, body.kind, int(body.has_llm), db.utcnow()),
    )
    conn.commit()
    return {"profile_id": profile_id, "name": body.name, "kind": body.kind,
            "has_llm": body.has_llm}


@router.get("/profiles/{profile_id}/embodiment-consistency")
def embodiment_consistency(profile_id: str) -> dict:
    """The profile's invariant identity signature and the embodiments it stays
    consistent across. Public: anyone meeting the profile through any form can
    verify it is the same personality."""
    profile = profile_or_404(profile_id)
    sig = persona.identity_signature(profile)
    forms = [{**dict(r), "has_llm": bool(r["has_llm"])} for r in
             db.connect().execute(
                 "SELECT name, kind, has_llm FROM embodiments WHERE profile_id=?",
                 (profile_id,)).fetchall()]
    surfaces = [r["surface"] for r in db.connect().execute(
        "SELECT surface FROM surfaces WHERE profile_id=?",
        (profile_id,)).fetchall()]
    return {"profile_id": profile_id, **sig,
            "embodiments": forms, "surfaces": surfaces}


@router.get("/profiles/{profile_id}/embodiments")
def list_embodiments(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT name, kind, has_llm FROM embodiments WHERE profile_id=?",
        (profile_id,)).fetchall()
    return [{**dict(r), "has_llm": bool(r["has_llm"])} for r in rows]


# -- Graceful departure ------------------------------------------------------

@router.post("/profiles/{profile_id}/sunset")
def sunset_profile(profile_id: str, request: Request) -> dict:
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    if profile["status"] == "departed":
        raise HTTPException(409, "profile has already departed")
    return companion.sunset(profile, pdi=request.app.state.pdi,
                            cloud=request.app.state.cloud)


@router.post("/profiles/{profile_id}/succeed")
def succeed_profile(profile_id: str, body: SucceedRequest,
                    request: Request) -> dict:
    """Ownership succession on a confirmed owner-death / incapacity signal.
    Verified by a reviewer (the original owner may be unable to authorize, so
    the owner token cannot be the gate): with a named ``successor_owner``,
    control passes to them and a fresh owner token is minted; with none, the
    profile sunsets to memorial — frozen rather than orphaned."""
    profile = profile_or_404(profile_id)
    auth.require_reviewer(request)
    if profile["status"] in ("departed", "terminated"):
        raise HTTPException(409, f"profile is already {profile['status']}")
    # A contested identity cannot be handed to a new owner until the objection
    # is resolved (governance.py owns the objection lifecycle).
    contested = db.connect().execute(
        "SELECT 1 FROM objections WHERE profile_id=? AND status='open' LIMIT 1",
        (profile_id,)).fetchone()
    if contested:
        raise HTTPException(
            409, "profile has an open objection; resolve it before succession")

    conn = db.connect()
    if not profile["successor_owner"]:
        result = companion.sunset(profile, pdi=request.app.state.pdi,
                                  cloud=request.app.state.cloud)
        return {"succeeded": False, "memorial": True,
                "verification_ref": body.verification_ref, **result}

    conn.execute(
        "UPDATE profiles SET owner_id=?, successor_owner=NULL WHERE id=?",
        (profile["successor_owner"], profile_id))
    conn.commit()
    auth.revoke_subject(profile_id)            # the old owner token dies here
    token = auth.issue("owner", profile_id)
    return {"succeeded": True, "memorial": False,
            "owner_id": profile["successor_owner"],
            "verification_ref": body.verification_ref,
            "owner_token": token}              # shown once, to the successor


@router.get("/profiles/{profile_id}/memorial")
def memorial_view(profile_id: str) -> dict:
    """Public memorial for a departed profile — what the world may see: the
    name, the purpose it served, its physical memorial anchors. Never persona
    internals; memory stays with those who knew it."""
    profile = profile_or_404(profile_id)
    if profile["status"] != "departed":
        raise HTTPException(
            409, f"this profile is {profile['status']}, not a memorial")
    conn = db.connect()
    beacons = [{"label": r["label"], "location": r["location"],
                "scans": r["scans"]}
               for r in conn.execute(
                   "SELECT label, location, scans FROM beacons"
                   " WHERE profile_id=? AND active=1", (profile_id,)).fetchall()]
    handle = conn.execute("SELECT handle FROM handles WHERE profile_id=?",
                          (profile_id,)).fetchone()
    farewells = conn.execute(
        "SELECT COUNT(DISTINCT interactor_id) AS n FROM messages"
        " WHERE profile_id=? AND role='profile'", (profile_id,)).fetchone()["n"]
    return {
        "profile_id": profile_id,
        "display_name": identity.shown_name(profile),
        "handle": f"@{handle['handle']}" if handle else None,
        "purpose": profile["purpose"],
        "status": "departed",
        "memorial_anchors": beacons,
        "relationships_touched": farewells,
        "note": "this profile has departed; its memory remains with those "
                "who knew it — viewing and export stay open to them",
    }


@router.patch("/profiles/{profile_id}", response_model=ProfileOut)
def update_profile(profile_id: str, body: ProfileUpdate,
                   request: Request) -> ProfileOut:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        conn = db.connect()
        assignments = ", ".join(f"{k}=?" for k in updates)
        conn.execute(
            f"UPDATE profiles SET {assignments} WHERE id=?",
            (*[int(v) if isinstance(v, bool) else v for v in updates.values()],
             profile_id),
        )
        conn.commit()
    return profile_out(profile_or_404(profile_id), request)


@router.get("/profiles/{profile_id}/export")
def export_profile(profile_id: str, request: Request) -> dict:
    """Full data export — access everything, anytime (You Own It)."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    grab = lambda q: [dict(r) for r in conn.execute(q, (profile_id,)).fetchall()]
    return {
        "profile": profile,
        "sources": source_items(profile_id, request.app.state.pdi),
        "relationships": grab("SELECT * FROM relationships WHERE profile_id=?"),
        "messages": grab("SELECT * FROM messages WHERE profile_id=?"
                         " ORDER BY created_at, rowid"),
        "engagement": grab("SELECT * FROM engagement WHERE profile_id=?"),
        "posts": grab("SELECT * FROM posts WHERE profile_id=?"
                      " ORDER BY created_at, rowid"),
        "surfaces": [r["surface"] for r in conn.execute(
            "SELECT surface FROM surfaces WHERE profile_id=?",
            (profile_id,)).fetchall()],
    }


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str, request: Request) -> dict:
    """Delete the profile and every trace of it — anytime."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    pdi = request.app.state.pdi
    conn = db.connect()
    deleted = {}
    vaulted = [r["pdi_key"] for r in conn.execute(
        "SELECT pdi_key FROM source_items WHERE profile_id=?"
        " AND pdi_key IS NOT NULL", (profile_id,)).fetchall()]
    vaulted += [r["vault_key"] for r in conn.execute(
        "SELECT vault_key FROM finetune_runs WHERE profile_id=?"
        " AND vault_key IS NOT NULL", (profile_id,)).fetchall()]
    if vaulted:
        deleted["pdi_records"] = sum(
            1 for key in vaulted if pdi is not None and pdi.delete(key))
    for table in ("source_items", "relationships", "messages", "engagement",
                  "posts", "surfaces", "persona_embeddings", "specialists",
                  "biometric_context", "grants", "tasks", "finetune_runs",
                  "marketplace", "handles", "beacons", "creative_works",
                  "perceptions", "active_handoffs", "workflows", "objections",
                  "proactive_state", "license_offers", "license_grants",
                  "contribution_log"):
        deleted[table] = conn.execute(
            f"DELETE FROM {table} WHERE profile_id=?", (profile_id,)).rowcount
    # Also drop any conversation that had handed off *to* this profile.
    conn.execute("DELETE FROM active_handoffs WHERE specialist_profile_id=?",
                 (profile_id,))
    deleted["profile"] = conn.execute(
        "DELETE FROM profiles WHERE id=?", (profile_id,)).rowcount
    conn.commit()
    auth.revoke_subject(profile_id)   # the owner token dies with the profile
    return {"deleted": deleted}


# -- Source material: the data the profile is built from ---------------------

@router.post("/profiles/{profile_id}/sources", status_code=201)
def add_source(profile_id: str, body: SourceAdd, request: Request) -> dict:
    row = profile_or_404(profile_id)
    require_owner(profile_id, request)
    # Source material about somebody who is not the account holder does not go
    # into the open store. The person exposed did not choose the plan — see
    # qrme/storage.py:SENSITIVE.
    if row["kind"] == "other_person":
        try:
            storage.require(tiers.plan_of(row["owner_id"]),
                            "third_party_source")
        except storage.StorageError as exc:
            raise HTTPException(402, str(exc)) from None
    pdi = request.app.state.pdi
    conn = db.connect()
    item_id = db.new_id("src")
    content, pdi_key = body.content, None
    if pdi is not None and body.content:
        pdi_key = f"qrme/{profile_id}/sources/{item_id}"
        pdi.put(pdi_key, json.dumps({"content": body.content}))
        content = None                # only the reference stays local
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, created_at) VALUES (?,?,?,?,?,?,?)",
        (item_id, profile_id, body.kind, body.title, content, pdi_key,
         db.utcnow()),
    )
    conn.commit()
    return {"id": item_id, "kind": body.kind, "title": body.title,
            "vaulted": pdi_key is not None}


@router.get("/profiles/{profile_id}/sources")
def list_sources(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return source_items(profile_id, request.app.state.pdi)


# -- Cross-platform surfaces -------------------------------------------------

@router.put("/profiles/{profile_id}/surfaces")
def set_surfaces(profile_id: str, body: SurfacesSet, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    conn.execute("DELETE FROM surfaces WHERE profile_id=?", (profile_id,))
    for surface in body.surfaces:
        conn.execute(
            "INSERT INTO surfaces (profile_id, surface, created_at)"
            " VALUES (?,?,?)", (profile_id, surface, db.utcnow()))
    conn.commit()
    return {"profile_id": profile_id, "surfaces": body.surfaces}


@router.get("/profiles/{profile_id}/surfaces")
def get_surfaces(profile_id: str) -> dict:
    profile_or_404(profile_id)
    rows = db.connect().execute(
        "SELECT surface FROM surfaces WHERE profile_id=?",
        (profile_id,)).fetchall()
    return {"profile_id": profile_id, "surfaces": [r["surface"] for r in rows]}


# -- AI Profile Marketplace --------------------------------------------------

@router.post("/profiles/{profile_id}/marketplace", status_code=201)
def list_on_marketplace(profile_id: str, body: MarketplaceList,
                        request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    conn.execute(
        "INSERT INTO marketplace (profile_id, tags, blurb, listed_at)"
        " VALUES (?,?,?,?) ON CONFLICT (profile_id) DO UPDATE SET"
        " tags=excluded.tags, blurb=excluded.blurb",
        (profile_id, json.dumps(body.tags), body.blurb, db.utcnow()),
    )
    conn.commit()
    return {"profile_id": profile_id, "listed": True, "tags": body.tags}


@router.delete("/profiles/{profile_id}/marketplace", status_code=204)
def unlist_from_marketplace(profile_id: str, request: Request) -> None:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    if not conn.execute("DELETE FROM marketplace WHERE profile_id=?",
                        (profile_id,)).rowcount:
        raise HTTPException(404, "profile is not listed")
    conn.commit()


@router.get("/marketplace")
def browse_marketplace(tag: str | None = None) -> list[dict]:
    """Public discovery cards — display info only, never persona internals."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT m.profile_id, m.tags, m.blurb, p.display_name, p.purpose,"
        " p.anonymous FROM marketplace m JOIN profiles p ON p.id=m.profile_id"
        " WHERE p.status='active'"        # restricted/terminated stay hidden
        " ORDER BY m.listed_at DESC").fetchall()
    cards = []
    for row in rows:
        tags = json.loads(row["tags"])
        if tag and tag not in tags:
            continue
        cards.append({
            "profile_id": row["profile_id"],
            "display_name": (identity.anonymous_name(row["profile_id"])
                             if row["anonymous"]
                             else row["display_name"]),
            "purpose": row["purpose"], "tags": tags, "blurb": row["blurb"],
        })
    return cards


# -- Profile health, at a glance ---------------------------------------------

@router.get("/profiles/{profile_id}/stats")
def profile_stats(profile_id: str, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    one = lambda q: conn.execute(q, (profile_id,)).fetchone()
    eng = one("SELECT COALESCE(SUM(sessions),0) AS sessions,"
              " COALESCE(AVG(score),0) AS avg_score,"
              " COUNT(*) AS interactors FROM engagement WHERE profile_id=?")
    msgs = one("SELECT COUNT(*) AS total FROM messages WHERE profile_id=?")
    prof_msgs = one(
        "SELECT COUNT(*) AS total,"
        " SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) AS approved"
        " FROM messages WHERE profile_id=? AND role='profile'")
    pass_rate = (round(prof_msgs["approved"] / prof_msgs["total"], 4)
                 if prof_msgs["total"] else None)
    return {
        "sessions": eng["sessions"],
        "memory_entries": msgs["total"],
        "moderation_pass_rate": pass_rate,
        "relationship_graph": one(
            "SELECT COUNT(*) AS n FROM relationships WHERE profile_id=?")["n"],
        "engagement_avg": round(eng["avg_score"], 3),
        "interactors": eng["interactors"],
        "sources": one(
            "SELECT COUNT(*) AS n FROM source_items WHERE profile_id=?")["n"],
        "posts": one(
            "SELECT COUNT(*) AS n FROM posts WHERE profile_id=?")["n"],
        "surfaces": [r["surface"] for r in conn.execute(
            "SELECT surface FROM surfaces WHERE profile_id=?",
            (profile_id,)).fetchall()],
    }
