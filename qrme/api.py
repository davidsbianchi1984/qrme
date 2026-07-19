"""HTTP API — the v1 surface for profile owners and interactors."""

from __future__ import annotations

import json
import os
from datetime import date, datetime

from fastapi import FastAPI, HTTPException

from . import adaptation, db, engagement, llm, moderation, persona, tasks
from .models import (
    ChatRequest,
    ChatResponse,
    ComposeRequest,
    EngagementOut,
    Feedback,
    GrantCreate,
    InteractorCreate,
    MessageOut,
    ProfileCreate,
    ProfileOut,
    ProfileUpdate,
    RelationshipSet,
    SourceAdd,
    SpecialistSet,
    SurfacesSet,
    TaskRun,
)
from .pdi_client import PDIClient

# Claim 24: map monitoring signals to the specialist domain they call for.
def _biometric_domain(biometrics: dict) -> str | None:
    condition = (biometrics.get("condition") or "").lower()
    if condition in ("anxiety", "depression", "stress", "phobia"):
        return "mental_health"
    if condition in ("physical_distress", "physical_injury"):
        return "medical"
    if condition == "financial_stress":
        return "finance"
    try:
        if float(biometrics.get("stress_level") or 0) >= 0.7:
            return "mental_health"
    except (TypeError, ValueError):
        pass
    return None

MEMORY_WINDOW = 30  # prior messages included as context per interactor


def _age(birthdate: date) -> int:
    today = datetime.now().date()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )


def _profile_or_404(profile_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "profile not found")
    return dict(row)


def _interactor_or_404(interactor_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM interactors WHERE id=?", (interactor_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "interactor not found")
    return dict(row)


def _relationship(profile_id: str, interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM relationships WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id),
    ).fetchone()
    return dict(row) if row else None


def _profile_out(row: dict) -> ProfileOut:
    return ProfileOut(
        id=row["id"],
        owner_id=row["owner_id"],
        kind=row["kind"],
        display_name=row["display_name"],
        persona=row["persona"],
        demographics=json.loads(row["demographics"]),
        sources=json.loads(row["sources"]),
        anonymous=bool(row["anonymous"]),
        adult_mode=bool(row["adult_mode"]),
        interaction_scope=row["interaction_scope"],
        moderation_mode=row["moderation_mode"],
        aging_enabled=bool(row["aging_enabled"]),
        base_age=row["base_age"],
        effective_age=persona.effective_age(row),
        successor_owner=row["successor_owner"],
        purpose=row["purpose"],
        maturity=row["maturity"],
        created_at=row["created_at"],
    )


def _message_out(row: dict) -> MessageOut:
    # Unapproved profile content is never shown to interactors (PRD 6.5).
    visible = row["status"] == "approved" or row["role"] == "interactor"
    return MessageOut(
        id=row["id"],
        role=row["role"],
        content=row["content"] if visible else None,
        status=row["status"],
        flag_reason=row["flag_reason"],
        created_at=row["created_at"],
    )


def create_app(pdi_client: PDIClient | None = None) -> FastAPI:
    app = FastAPI(title="QRME", version="0.1.0")

    # PDI tandem: profile source material is sealed in the encrypted vault
    # when configured (QRME_PDI_URL + QRME_PDI_TOKEN, or an injected client).
    if pdi_client is None and os.environ.get("QRME_PDI_URL"):
        pdi_client = PDIClient(token=os.environ.get("QRME_PDI_TOKEN", ""),
                               base_url=os.environ["QRME_PDI_URL"])
    app.state.pdi = pdi_client

    def _source_items(profile_id: str) -> list[dict]:
        """Source items with content resolved from the PDI vault if sealed."""
        rows = db.connect().execute(
            "SELECT * FROM source_items WHERE profile_id=?"
            " ORDER BY created_at DESC, rowid DESC", (profile_id,),
        ).fetchall()
        out = []
        for row in rows:
            item = dict(row)
            if item["pdi_key"] and app.state.pdi is not None:
                raw = app.state.pdi.get(item["pdi_key"])
                item["content"] = json.loads(raw)["content"] if raw else None
            out.append(item)
        return out

    # -- Profile creation & onboarding (PRD 6.1) ----------------------------

    @app.post("/profiles", response_model=ProfileOut, status_code=201)
    def create_profile(body: ProfileCreate) -> ProfileOut:
        owner_age = _age(body.verification.birthdate)
        if owner_age < 18 and not body.verification.guardian_consent:
            raise HTTPException(
                403, "owners under 18 require parent/guardian consent"
            )
        if body.adult_mode and owner_age < 18:
            raise HTTPException(403, "adult mode requires a verified adult owner")
        if body.kind == "other_person" and body.consent is None:
            raise HTTPException(
                422,
                "profiles of another real person require a consent/rights record",
            )

        profile_id = db.new_id("prf")
        conn = db.connect()
        conn.execute(
            "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
            " demographics, sources, anonymous, adult_mode, interaction_scope,"
            " moderation_mode, aging_enabled, base_age, consent_basis,"
            " consent_attestor, successor_owner, purpose, maturity, created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                profile_id,
                body.owner_id,
                body.kind,
                body.display_name,
                body.persona,
                json.dumps(body.demographics),
                json.dumps(body.sources),
                int(body.anonymous),
                int(body.adult_mode),
                body.interaction_scope,
                body.moderation_mode,
                int(body.aging_enabled),
                body.base_age,
                body.consent.basis if body.consent else None,
                body.consent.attestor if body.consent else None,
                body.successor_owner,
                body.purpose,
                body.maturity,
                db.utcnow(),
            ),
        )
        conn.commit()
        return _profile_out(_profile_or_404(profile_id))

    @app.get("/profiles/{profile_id}", response_model=ProfileOut)
    def get_profile(profile_id: str) -> ProfileOut:
        return _profile_out(_profile_or_404(profile_id))

    # -- Owner control: edit, export, delete anytime ------------------------

    @app.patch("/profiles/{profile_id}", response_model=ProfileOut)
    def update_profile(profile_id: str, body: ProfileUpdate) -> ProfileOut:
        _profile_or_404(profile_id)
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
        return _profile_out(_profile_or_404(profile_id))

    @app.get("/profiles/{profile_id}/export")
    def export_profile(profile_id: str) -> dict:
        """Full data export — access everything, anytime (You Own It)."""
        profile = _profile_or_404(profile_id)
        conn = db.connect()
        grab = lambda q: [dict(r) for r in conn.execute(q, (profile_id,)).fetchall()]
        return {
            "profile": profile,
            "sources": _source_items(profile_id),
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

    @app.delete("/profiles/{profile_id}")
    def delete_profile(profile_id: str) -> dict:
        """Delete the profile and every trace of it — anytime."""
        _profile_or_404(profile_id)
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
                1 for key in vaulted
                if app.state.pdi is not None and app.state.pdi.delete(key))
        for table in ("source_items", "relationships", "messages", "engagement",
                      "posts", "surfaces", "persona_embeddings", "specialists",
                      "biometric_context", "grants", "tasks", "finetune_runs"):
            deleted[table] = conn.execute(
                f"DELETE FROM {table} WHERE profile_id=?", (profile_id,)
            ).rowcount
        deleted["profile"] = conn.execute(
            "DELETE FROM profiles WHERE id=?", (profile_id,)).rowcount
        conn.commit()
        return {"deleted": deleted}

    # -- Source material: the data the profile is built from ----------------

    @app.post("/profiles/{profile_id}/sources", status_code=201)
    def add_source(profile_id: str, body: SourceAdd) -> dict:
        _profile_or_404(profile_id)
        conn = db.connect()
        item_id = db.new_id("src")
        content, pdi_key = body.content, None
        if app.state.pdi is not None and body.content:
            pdi_key = f"qrme/{profile_id}/sources/{item_id}"
            app.state.pdi.put(pdi_key, json.dumps({"content": body.content}))
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

    @app.get("/profiles/{profile_id}/sources")
    def list_sources(profile_id: str) -> list[dict]:
        _profile_or_404(profile_id)
        return _source_items(profile_id)

    # -- Cross-platform surfaces --------------------------------------------

    @app.put("/profiles/{profile_id}/surfaces")
    def set_surfaces(profile_id: str, body: SurfacesSet) -> dict:
        _profile_or_404(profile_id)
        conn = db.connect()
        conn.execute("DELETE FROM surfaces WHERE profile_id=?", (profile_id,))
        for surface in body.surfaces:
            conn.execute(
                "INSERT INTO surfaces (profile_id, surface, created_at)"
                " VALUES (?,?,?)", (profile_id, surface, db.utcnow()))
        conn.commit()
        return {"profile_id": profile_id, "surfaces": body.surfaces}

    @app.get("/profiles/{profile_id}/surfaces")
    def get_surfaces(profile_id: str) -> dict:
        _profile_or_404(profile_id)
        rows = db.connect().execute(
            "SELECT surface FROM surfaces WHERE profile_id=?",
            (profile_id,)).fetchall()
        return {"profile_id": profile_id,
                "surfaces": [r["surface"] for r in rows]}

    @app.post("/interactors", status_code=201)
    def create_interactor(body: InteractorCreate) -> dict:
        interactor_id = db.new_id("usr")
        conn = db.connect()
        conn.execute(
            "INSERT INTO interactors (id, display_name, birthdate, created_at)"
            " VALUES (?,?,?,?)",
            (
                interactor_id,
                body.display_name,
                body.birthdate.isoformat() if body.birthdate else None,
                db.utcnow(),
            ),
        )
        conn.commit()
        return {"id": interactor_id, "display_name": body.display_name}

    # -- Relationship-aware modification (PRD 6.2) --------------------------

    @app.put("/profiles/{profile_id}/relationships/{interactor_id}")
    def set_relationship(
        profile_id: str, interactor_id: str, body: RelationshipSet
    ) -> dict:
        _profile_or_404(profile_id)
        _interactor_or_404(interactor_id)
        conn = db.connect()
        conn.execute(
            "INSERT INTO relationships (id, profile_id, interactor_id,"
            " relationship_type, nickname, tone, boundaries, created_at)"
            " VALUES (?,?,?,?,?,?,?,?)"
            " ON CONFLICT (profile_id, interactor_id) DO UPDATE SET"
            " relationship_type=excluded.relationship_type,"
            " nickname=excluded.nickname, tone=excluded.tone,"
            " boundaries=excluded.boundaries",
            (
                db.new_id("rel"),
                profile_id,
                interactor_id,
                body.relationship_type,
                body.nickname,
                body.tone,
                json.dumps(body.boundaries),
                db.utcnow(),
            ),
        )
        conn.commit()
        return _relationship(profile_id, interactor_id)

    # -- Chat surface (PRD 6.8) with moderation (6.5) and memory (6.4) ------

    @app.post("/profiles/{profile_id}/chat", response_model=ChatResponse)
    def chat(profile_id: str, body: ChatRequest) -> ChatResponse:
        profile = _profile_or_404(profile_id)
        interactor = _interactor_or_404(body.interactor_id)

        if body.surface:
            registered = [r["surface"] for r in db.connect().execute(
                "SELECT surface FROM surfaces WHERE profile_id=?",
                (profile_id,)).fetchall()]
            if registered and body.surface not in registered:
                raise HTTPException(
                    422, f"profile is not live on surface '{body.surface}'")

        if profile["adult_mode"]:
            if not interactor["birthdate"] or _age(
                date.fromisoformat(interactor["birthdate"])
            ) < 18:
                raise HTTPException(
                    403, "this profile is age-gated; verified 18+ required"
                )

        conn = db.connect()
        interactor_msg_id = db.new_id("msg")
        conn.execute(
            "INSERT INTO messages (id, profile_id, interactor_id, role, content,"
            " status, created_at) VALUES (?,?,?,?,?,'approved',?)",
            (
                interactor_msg_id,
                profile_id,
                body.interactor_id,
                "interactor",
                body.message,
                db.utcnow(),
            ),
        )
        conn.commit()

        engagement_state = engagement.record_message(
            profile_id, body.interactor_id, body.message
        )
        relationship = _relationship(profile_id, body.interactor_id)

        # Real-time biometric context (claim 23) + specialist switch (claim 24).
        handoff = None
        speaking_profile = profile
        if body.biometrics:
            conn.execute(
                "INSERT INTO biometric_context (id, profile_id, interactor_id,"
                " data, created_at) VALUES (?,?,?,?,?)",
                (db.new_id("bio"), profile_id, body.interactor_id,
                 json.dumps(body.biometrics), db.utcnow()),
            )
            conn.commit()
            domain = _biometric_domain(body.biometrics)
            if domain:
                spec = conn.execute(
                    "SELECT specialist_profile_id FROM specialists"
                    " WHERE profile_id=? AND domain=?",
                    (profile_id, domain)).fetchone()
                if spec:
                    speaking_profile = _profile_or_404(
                        spec["specialist_profile_id"])
                    handoff = {"domain": domain,
                               "specialist_profile_id": speaking_profile["id"],
                               "reason": "real-time monitoring signals"}

        # Persistent memory: prior turns with this interactor (PRD 6.4).
        history = conn.execute(
            "SELECT role, content FROM messages"
            " WHERE profile_id=? AND interactor_id=? AND status='approved'"
            " ORDER BY created_at DESC, rowid DESC LIMIT ?",
            (profile_id, body.interactor_id, MEMORY_WINDOW),
        ).fetchall()
        llm_messages = [
            {
                "role": "user" if row["role"] == "interactor" else "assistant",
                "content": row["content"],
            }
            for row in reversed(history)
        ]

        system = persona.build_system_prompt(
            speaking_profile, relationship if handoff is None else None,
            engagement_state, sources=_source_items(speaking_profile["id"]))
        # Attention conditioning from the latent embedding (claims 21/22).
        attention = adaptation.attention_prompt(
            adaptation.get(profile_id, body.interactor_id))
        if attention:
            system += "\n\n" + attention
        if body.biometrics:
            system += ("\n\nCurrent situation from real-time monitoring: "
                       + json.dumps(body.biometrics, sort_keys=True)
                       + ". Respond with appropriate care.")
        reply = llm.get_provider().generate(system, llm_messages)

        verdict = moderation.review(reply, relationship, interactor,
                                    maturity=profile["maturity"])
        if not verdict.approved:
            status, flag_reason = "pending", verdict.reason
        elif profile["moderation_mode"] == "manual":
            status, flag_reason = "pending", "owner approval required"
        else:
            status, flag_reason = "approved", None

        profile_msg_id = db.new_id("msg")
        conn.execute(
            "INSERT INTO messages (id, profile_id, interactor_id, role, content,"
            " status, flag_reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                profile_msg_id,
                profile_id,
                body.interactor_id,
                "profile",
                reply,
                status,
                flag_reason,
                db.utcnow(),
            ),
        )
        conn.commit()

        rows = {
            row["id"]: dict(row)
            for row in conn.execute(
                "SELECT * FROM messages WHERE id IN (?,?)",
                (interactor_msg_id, profile_msg_id),
            )
        }
        # Persist cross-session state: update the latent embedding (claim 21).
        adaptation.update(profile_id, body.interactor_id, body.message,
                          relationship, engagement.get(
                              profile_id, body.interactor_id),
                          biometrics=body.biometrics)

        return ChatResponse(
            interactor_message=_message_out(rows[interactor_msg_id]),
            profile_message=_message_out(rows[profile_msg_id]),
            modality=_modality_descriptor(profile_id, body.modality),
            handoff=handoff,
        )

    def _modality_descriptor(profile_id: str, modality: str) -> dict | None:
        """Multi-modal output, represented structurally: how the reply
        renders beyond text (actual synthesis is out of scope for v1)."""
        if modality == "text":
            return None
        if modality == "voice":
            n = db.connect().execute(
                "SELECT COUNT(*) AS n FROM source_items"
                " WHERE profile_id=? AND kind='voice_note'",
                (profile_id,)).fetchone()["n"]
            basis = (f"voice preserved from {n} voice-note source(s)"
                     if n else "synthesized voice in persona style")
            return {"type": "voice", "basis": basis}
        return {"type": modality,
                "basis": f"{modality} treatment generated in persona style"}

    # -- Latent persona embeddings (claims 21/22) ---------------------------

    @app.get("/profiles/{profile_id}/embedding/{interactor_id}")
    def get_embedding(profile_id: str, interactor_id: str) -> dict:
        _profile_or_404(profile_id)
        embedding = adaptation.get(profile_id, interactor_id)
        if embedding is None:
            raise HTTPException(404, "no embedding yet — interact first")
        return embedding

    # -- Domain specialists (claim 24) --------------------------------------

    @app.put("/profiles/{profile_id}/specialists")
    def set_specialist(profile_id: str, body: SpecialistSet) -> dict:
        _profile_or_404(profile_id)
        _profile_or_404(body.specialist_profile_id)
        conn = db.connect()
        conn.execute(
            "INSERT INTO specialists (profile_id, domain,"
            " specialist_profile_id, created_at) VALUES (?,?,?,?)"
            " ON CONFLICT (profile_id, domain) DO UPDATE SET"
            " specialist_profile_id=excluded.specialist_profile_id",
            (profile_id, body.domain, body.specialist_profile_id, db.utcnow()),
        )
        conn.commit()
        return {"profile_id": profile_id, "domain": body.domain,
                "specialist_profile_id": body.specialist_profile_id}

    @app.get("/profiles/{profile_id}/specialists")
    def get_specialists(profile_id: str) -> list[dict]:
        _profile_or_404(profile_id)
        rows = db.connect().execute(
            "SELECT domain, specialist_profile_id FROM specialists"
            " WHERE profile_id=?", (profile_id,)).fetchall()
        return [dict(r) for r in rows]

    # -- Revocable grants & autonomous tasks (claim 25) ---------------------

    @app.post("/profiles/{profile_id}/grants", status_code=201)
    def create_grant(profile_id: str, body: GrantCreate) -> dict:
        _profile_or_404(profile_id)
        return tasks.create_grant(profile_id, body.scope)

    @app.delete("/grants/{grant_id}")
    def revoke_grant(grant_id: str) -> dict:
        if not tasks.revoke_grant(grant_id):
            raise HTTPException(404, "grant not found")
        return {"id": grant_id, "revoked": True}

    @app.post("/profiles/{profile_id}/tasks", status_code=201)
    def run_task(profile_id: str, body: TaskRun) -> dict:
        profile = _profile_or_404(profile_id)
        result = tasks.run(profile, body.kind, body.topic, body.grant_token,
                           pdi=app.state.pdi)
        if result["status"] == "failed" and "grant" in result.get("reason", ""):
            raise HTTPException(403, result["reason"])
        return result

    @app.get("/profiles/{profile_id}/tasks")
    def list_tasks(profile_id: str) -> list[dict]:
        _profile_or_404(profile_id)
        return tasks.list_tasks(profile_id)

    # -- Offline fine-tuning (claim 26) -------------------------------------

    @app.post("/profiles/{profile_id}/finetune", status_code=201)
    def finetune(profile_id: str) -> dict:
        _profile_or_404(profile_id)
        return adaptation.finetune(profile_id, pdi=app.state.pdi)

    # -- Compose: posting in the profile's voice, at scale ------------------

    @app.post("/profiles/{profile_id}/compose", status_code=201)
    def compose_post(profile_id: str, body: ComposeRequest) -> dict:
        profile = _profile_or_404(profile_id)
        system = persona.build_system_prompt(
            profile, None, None, sources=_source_items(profile_id))
        system += (f"\n\nCompose one short public post"
                   + (f" for {body.surface}" if body.surface else "")
                   + f" about: {body.topic}. Stay fully in character.")
        content = llm.get_provider().generate(
            system, [{"role": "user", "content": "Write the post."}])

        # Public posts face the widest audience: always the strict filter.
        verdict = moderation.review(content, None, {"birthdate": None},
                                    maturity="strict")
        if not verdict.approved:
            status, flag_reason = "pending", verdict.reason
        elif profile["moderation_mode"] == "manual":
            status, flag_reason = "pending", "owner approval required"
        else:
            status, flag_reason = "approved", None

        conn = db.connect()
        post_id = db.new_id("pst")
        conn.execute(
            "INSERT INTO posts (id, profile_id, surface, topic, content,"
            " status, flag_reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (post_id, profile_id, body.surface, body.topic, content, status,
             flag_reason, db.utcnow()),
        )
        conn.commit()
        return {"id": post_id, "surface": body.surface, "topic": body.topic,
                "content": content if status == "approved" else None,
                "status": status, "flag_reason": flag_reason}

    @app.get("/profiles/{profile_id}/posts")
    def list_posts(profile_id: str) -> list[dict]:
        _profile_or_404(profile_id)
        rows = db.connect().execute(
            "SELECT * FROM posts WHERE profile_id=? ORDER BY created_at, rowid",
            (profile_id,)).fetchall()
        return [dict(r) for r in rows]

    # -- Profile health, at a glance ----------------------------------------

    @app.get("/profiles/{profile_id}/stats")
    def profile_stats(profile_id: str) -> dict:
        _profile_or_404(profile_id)
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

    # -- Engagement signals & feedback (PRD 6.3) ----------------------------

    @app.post("/profiles/{profile_id}/interactions/{interactor_id}/feedback")
    def give_feedback(profile_id: str, interactor_id: str, body: Feedback) -> dict:
        _profile_or_404(profile_id)
        _interactor_or_404(interactor_id)
        return engagement.record_feedback(profile_id, interactor_id, body.rating)

    @app.get(
        "/profiles/{profile_id}/engagement/{interactor_id}",
        response_model=EngagementOut,
    )
    def get_engagement(profile_id: str, interactor_id: str) -> EngagementOut:
        state = engagement.get(profile_id, interactor_id)
        if state is None:
            raise HTTPException(404, "no engagement recorded")
        return EngagementOut(**{k: state[k] for k in EngagementOut.model_fields})

    # -- Persistent memory management (PRD 6.4) -----------------------------

    @app.get("/profiles/{profile_id}/memory/{interactor_id}")
    def view_memory(profile_id: str, interactor_id: str) -> list[MessageOut]:
        _profile_or_404(profile_id)
        rows = db.connect().execute(
            "SELECT * FROM messages WHERE profile_id=? AND interactor_id=?"
            " ORDER BY created_at, rowid",
            (profile_id, interactor_id),
        ).fetchall()
        return [_message_out(dict(row)) for row in rows]

    @app.delete("/profiles/{profile_id}/memory/{interactor_id}", status_code=204)
    def clear_memory(profile_id: str, interactor_id: str) -> None:
        _profile_or_404(profile_id)
        conn = db.connect()
        conn.execute(
            "DELETE FROM messages WHERE profile_id=? AND interactor_id=?",
            (profile_id, interactor_id),
        )
        conn.execute(
            "DELETE FROM engagement WHERE profile_id=? AND interactor_id=?",
            (profile_id, interactor_id),
        )
        conn.commit()

    # -- Owner moderation queue (PRD 6.5) ------------------------------------

    @app.get("/profiles/{profile_id}/moderation/queue")
    def moderation_queue(profile_id: str) -> list[dict]:
        _profile_or_404(profile_id)
        rows = db.connect().execute(
            "SELECT * FROM messages WHERE profile_id=? AND status='pending'"
            " ORDER BY created_at",
            (profile_id,),
        ).fetchall()
        # Owners see full content, including held messages.
        return [dict(row) for row in rows]

    @app.post("/moderation/{message_id}/approve")
    def approve_message(message_id: str) -> dict:
        return _resolve_message(message_id, "approved")

    @app.post("/moderation/{message_id}/reject")
    def reject_message(message_id: str) -> dict:
        return _resolve_message(message_id, "rejected")

    def _resolve_message(message_id: str, status: str) -> dict:
        conn = db.connect()
        row = conn.execute(
            "SELECT * FROM messages WHERE id=?", (message_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(404, "message not found")
        if row["status"] != "pending":
            raise HTTPException(409, f"message is already {row['status']}")
        conn.execute(
            "UPDATE messages SET status=? WHERE id=?", (status, message_id)
        )
        conn.commit()
        return {"id": message_id, "status": status}

    return app


app = create_app()
