"""HTTP API — the v1 surface for profile owners and interactors."""

from __future__ import annotations

import json
from datetime import date, datetime

from fastapi import FastAPI, HTTPException

from . import db, engagement, llm, moderation, persona
from .models import (
    ChatRequest,
    ChatResponse,
    EngagementOut,
    Feedback,
    InteractorCreate,
    MessageOut,
    ProfileCreate,
    ProfileOut,
    RelationshipSet,
)

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


def create_app() -> FastAPI:
    app = FastAPI(title="QRME", version="0.1.0")

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
            " consent_attestor, successor_owner, created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
                db.utcnow(),
            ),
        )
        conn.commit()
        return _profile_out(_profile_or_404(profile_id))

    @app.get("/profiles/{profile_id}", response_model=ProfileOut)
    def get_profile(profile_id: str) -> ProfileOut:
        return _profile_out(_profile_or_404(profile_id))

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

        system = persona.build_system_prompt(profile, relationship, engagement_state)
        reply = llm.get_provider().generate(system, llm_messages)

        verdict = moderation.review(reply, relationship, interactor)
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
        return ChatResponse(
            interactor_message=_message_out(rows[interactor_msg_id]),
            profile_message=_message_out(rows[profile_msg_id]),
        )

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
