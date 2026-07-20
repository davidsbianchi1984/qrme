"""Owner-side profile management: CRUD, sources, surfaces, stats,
marketplace, export, and erasure."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import auth, companion, db
from ..common import (
    age_of, profile_or_404, profile_out, require_owner, source_items,
)
from ..models import (
    EmbodimentAdd, GenesisCreate, MarketplaceList, ProfileCreate, ProfileOut,
    ProfileUpdate, SourceAdd, SurfacesSet,
)

router = APIRouter()


@router.post("/profiles", status_code=201)
def create_profile(body: ProfileCreate) -> dict:
    owner_age = age_of(body.verification.birthdate)
    if owner_age < 18 and not body.verification.guardian_consent:
        raise HTTPException(403, "owners under 18 require parent/guardian consent")
    if body.adult_mode and owner_age < 18:
        raise HTTPException(403, "adult mode requires a verified adult owner")
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
        " cloud_contribution, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            profile_id, body.owner_id, body.kind, body.display_name,
            body.persona, json.dumps(body.demographics),
            json.dumps(body.sources), int(body.anonymous),
            int(body.adult_mode), body.interaction_scope, body.moderation_mode,
            int(body.aging_enabled), body.base_age,
            body.consent.basis if body.consent else None,
            body.consent.attestor if body.consent else None,
            body.successor_owner, body.purpose, body.maturity,
            int(body.cloud_contribution), db.utcnow(),
        ),
    )
    conn.commit()
    token = auth.issue("owner", profile_id)
    return {**profile_out(profile_or_404(profile_id)).model_dump(),
            "owner_token": token}


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
    token = auth.issue("owner", profile_id)
    return {**profile_out(profile_or_404(profile_id)).model_dump(),
            "owner_token": token}


@router.get("/profiles/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: str) -> ProfileOut:
    return profile_out(profile_or_404(profile_id))


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
    return profile_out(profile_or_404(profile_id))


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
                  "perceptions", "active_handoffs", "workflows"):
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
    profile_or_404(profile_id)
    require_owner(profile_id, request)
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
        " ORDER BY m.listed_at DESC").fetchall()
    cards = []
    for row in rows:
        tags = json.loads(row["tags"])
        if tag and tag not in tags:
            continue
        cards.append({
            "profile_id": row["profile_id"],
            "display_name": ("anonymous persona" if row["anonymous"]
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
