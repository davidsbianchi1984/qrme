"""Interaction surface: interactors, relationships, chat, compose,
engagement/feedback (with opt-in cloud contribution), memory, moderation."""

from __future__ import annotations

import json
from datetime import date

from fastapi import APIRouter, HTTPException, Request

from .. import adaptation, auth, companion, db, engagement, llm, moderation, persona
from ..common import (
    age_of, biometric_domain, interactor_or_404, message_out, profile_or_404,
    relationship as get_relationship, require_owner,
    require_owner_or_interactor, source_items,
)
from ..models import (
    ChatRequest, ChatResponse, ComposeRequest, EngagementOut, Feedback,
    InteractorCreate, MessageOut, RelationshipSet,
)

MEMORY_WINDOW = 30  # prior messages included as context per interactor

router = APIRouter()


@router.post("/interactors", status_code=201)
def create_interactor(body: InteractorCreate) -> dict:
    interactor_id = db.new_id("usr")
    conn = db.connect()
    conn.execute(
        "INSERT INTO interactors (id, display_name, birthdate, created_at)"
        " VALUES (?,?,?,?)",
        (interactor_id, body.display_name,
         body.birthdate.isoformat() if body.birthdate else None, db.utcnow()),
    )
    conn.commit()
    token = auth.issue("interactor", interactor_id)
    return {"id": interactor_id, "display_name": body.display_name,
            "token": token}


@router.put("/profiles/{profile_id}/relationships/{interactor_id}")
def set_relationship(profile_id: str, interactor_id: str,
                     body: RelationshipSet, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    interactor_or_404(interactor_id)
    conn = db.connect()
    conn.execute(
        "INSERT INTO relationships (id, profile_id, interactor_id,"
        " relationship_type, nickname, tone, boundaries, created_at)"
        " VALUES (?,?,?,?,?,?,?,?)"
        " ON CONFLICT (profile_id, interactor_id) DO UPDATE SET"
        " relationship_type=excluded.relationship_type,"
        " nickname=excluded.nickname, tone=excluded.tone,"
        " boundaries=excluded.boundaries",
        (db.new_id("rel"), profile_id, interactor_id, body.relationship_type,
         body.nickname, body.tone, json.dumps(body.boundaries), db.utcnow()),
    )
    conn.commit()
    return get_relationship(profile_id, interactor_id)


def _modality_descriptor(profile_id: str, modality: str) -> dict | None:
    """Multi-modal output, represented structurally: how the reply renders
    beyond text (actual synthesis is out of scope for v1)."""
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


@router.post("/profiles/{profile_id}/chat", response_model=ChatResponse)
def chat(profile_id: str, body: ChatRequest, request: Request) -> ChatResponse:
    profile = profile_or_404(profile_id)
    interactor = interactor_or_404(body.interactor_id)
    pdi, cloud = request.app.state.pdi, request.app.state.cloud

    if profile["status"] == "departed":
        raise HTTPException(
            410, "this profile has departed; its memory remains viewable")

    if body.surface:
        conn0 = db.connect()
        registered = [r["surface"] for r in conn0.execute(
            "SELECT surface FROM surfaces WHERE profile_id=?",
            (profile_id,)).fetchall()]
        registered += [r["name"] for r in conn0.execute(
            "SELECT name FROM embodiments WHERE profile_id=?",
            (profile_id,)).fetchall()]
        if registered and body.surface not in registered:
            raise HTTPException(
                422, f"profile is not live on surface '{body.surface}'")

    if profile["adult_mode"]:
        if not interactor["birthdate"] or age_of(
            date.fromisoformat(interactor["birthdate"])
        ) < 18:
            raise HTTPException(
                403, "this profile is age-gated; verified 18+ required")

    conn = db.connect()
    interactor_msg_id = db.new_id("msg")
    conn.execute(
        "INSERT INTO messages (id, profile_id, interactor_id, role, content,"
        " status, created_at) VALUES (?,?,?,?,?,'approved',?)",
        (interactor_msg_id, profile_id, body.interactor_id, "interactor",
         body.message, db.utcnow()),
    )
    conn.commit()

    engagement_state = engagement.record_message(
        profile_id, body.interactor_id, body.message)
    relationship = get_relationship(profile_id, body.interactor_id)

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
        domain = biometric_domain(body.biometrics)
        if domain:
            spec = conn.execute(
                "SELECT specialist_profile_id FROM specialists"
                " WHERE profile_id=? AND domain=?",
                (profile_id, domain)).fetchone()
            if spec:
                speaking_profile = profile_or_404(spec["specialist_profile_id"])
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
        {"role": "user" if row["role"] == "interactor" else "assistant",
         "content": row["content"]}
        for row in reversed(history)
    ]

    system = persona.build_system_prompt(
        speaking_profile, relationship if handoff is None else None,
        engagement_state, sources=source_items(speaking_profile["id"], pdi))
    # Attention conditioning from the latent embedding (claims 21/22).
    attention = adaptation.attention_prompt(
        adaptation.get(profile_id, body.interactor_id))
    if attention:
        system += "\n\n" + attention
    if body.biometrics:
        system += ("\n\nCurrent situation from real-time monitoring: "
                   + json.dumps(body.biometrics, sort_keys=True)
                   + ". Respond with appropriate care.")
    others = companion.other_relationships(profile_id, body.interactor_id)
    if others:
        system += (f"\n\nHonesty about multiplicity: you also hold {others} "
                   "other ongoing relationship(s). If asked, acknowledge "
                   "this truthfully and kindly — never deny it.")
    reply = llm.get_provider(cloud=cloud).generate(system, llm_messages)

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
        (profile_msg_id, profile_id, body.interactor_id, "profile", reply,
         status, flag_reason, db.utcnow()),
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
                      relationship,
                      engagement.get(profile_id, body.interactor_id),
                      biometrics=body.biometrics)

    return ChatResponse(
        interactor_message=message_out(rows[interactor_msg_id]),
        profile_message=message_out(rows[profile_msg_id]),
        modality=_modality_descriptor(profile_id, body.modality),
        handoff=handoff,
    )


# -- Compose: posting in the profile's voice, at scale -----------------------

@router.post("/profiles/{profile_id}/compose", status_code=201)
def compose_post(profile_id: str, body: ComposeRequest, request: Request) -> dict:
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    system = persona.build_system_prompt(
        profile, None, None,
        sources=source_items(profile_id, request.app.state.pdi))
    system += (f"\n\nCompose one short public post"
               + (f" for {body.surface}" if body.surface else "")
               + f" about: {body.topic}. Stay fully in character.")
    content = llm.get_provider(cloud=request.app.state.cloud).generate(
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


@router.get("/profiles/{profile_id}/posts")
def list_posts(profile_id: str) -> list[dict]:
    profile_or_404(profile_id)
    rows = db.connect().execute(
        "SELECT * FROM posts WHERE profile_id=? ORDER BY created_at, rowid",
        (profile_id,)).fetchall()
    return [dict(r) for r in rows]


# -- Companion features: proactive check-ins and transparency ----------------

@router.post("/profiles/{profile_id}/proactive/{interactor_id}")
def proactive_checkin(profile_id: str, interactor_id: str,
                      request: Request) -> dict:
    """The profile initiates — allowed only when its owner opted in with
    interaction_scope='proactive'."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    interactor = interactor_or_404(interactor_id)
    if profile["status"] == "departed":
        raise HTTPException(410, "this profile has departed")
    if profile["interaction_scope"] != "proactive":
        raise HTTPException(
            403, "this profile is reactive-only; its owner has not enabled "
                 "proactive outreach")

    relationship = get_relationship(profile_id, interactor_id)
    engagement_state = engagement.get(profile_id, interactor_id)
    reason = companion.proactive_reason(engagement_state)

    system = persona.build_system_prompt(
        profile, relationship, engagement_state,
        sources=source_items(profile_id, request.app.state.pdi))
    system += ("\n\nYou are reaching out first (" + reason + "): compose one "
               "brief, warm, unprompted check-in. Reference shared history "
               "naturally if you have any; never pressure a reply.")
    content = llm.get_provider(cloud=request.app.state.cloud).generate(
        system, [{"role": "user", "content": "Reach out."}])

    verdict = moderation.review(content, relationship, interactor,
                                maturity=profile["maturity"])
    if not verdict.approved:
        status, flag_reason = "pending", verdict.reason
    elif profile["moderation_mode"] == "manual":
        status, flag_reason = "pending", "owner approval required"
    else:
        status, flag_reason = "approved", None

    conn = db.connect()
    message_id = db.new_id("msg")
    conn.execute(
        "INSERT INTO messages (id, profile_id, interactor_id, role, content,"
        " status, flag_reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (message_id, profile_id, interactor_id, "profile", content, status,
         flag_reason, db.utcnow()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM messages WHERE id=?",
                       (message_id,)).fetchone()
    return {"reason": reason, "message": message_out(dict(row)).model_dump()}


@router.get("/profiles/{profile_id}/transparency")
def transparency(profile_id: str) -> dict:
    """Honesty by design: how many relationships this profile holds."""
    profile_or_404(profile_id)
    return {
        "profile_id": profile_id,
        "active_relationships": companion.other_relationships(profile_id),
        "policy": "the profile acknowledges its other relationships "
                  "truthfully whenever asked",
    }


# -- Engagement signals & feedback (PRD 6.3) ---------------------------------

def _anonymized_exchange(profile: dict, profile_id: str,
                         interactor_id: str) -> list[dict] | None:
    """The last approved exchange with all identifying strings stripped —
    ids never included; the persona's display name replaced throughout."""
    rows = db.connect().execute(
        "SELECT role, content FROM messages WHERE profile_id=?"
        " AND interactor_id=? AND status='approved'"
        " ORDER BY created_at DESC, rowid DESC LIMIT 2",
        (profile_id, interactor_id)).fetchall()
    if len(rows) < 2:
        return None
    exchange = []
    for row in reversed(rows):
        content = row["content"].replace(profile["display_name"], "PERSONA")
        exchange.append({"role": row["role"], "content": content})
    return exchange


@router.post("/profiles/{profile_id}/interactions/{interactor_id}/feedback")
def give_feedback(profile_id: str, interactor_id: str, body: Feedback,
                  request: Request) -> dict:
    profile = profile_or_404(profile_id)
    interactor_or_404(interactor_id)
    result = engagement.record_feedback(profile_id, interactor_id, body.rating)

    # Opt-in cloud contribution: positively-rated exchanges, anonymized,
    # improve the shared cloud model (see docs/cloud-model.md).
    cloud = request.app.state.cloud
    result["contributed"] = False
    if (body.rating == "up" and profile["cloud_contribution"]
            and cloud is not None):
        exchange = _anonymized_exchange(profile, profile_id, interactor_id)
        if exchange:
            result["contributed"] = cloud.contribute({
                "source": "qrme",
                "kind": "rated_exchange",
                "quality": "positive",
                "purpose": profile["purpose"],
                "exchange": exchange,
            })
    return result


@router.get("/profiles/{profile_id}/engagement/{interactor_id}",
            response_model=EngagementOut)
def get_engagement(profile_id: str, interactor_id: str) -> EngagementOut:
    state = engagement.get(profile_id, interactor_id)
    if state is None:
        raise HTTPException(404, "no engagement recorded")
    return EngagementOut(**{k: state[k] for k in EngagementOut.model_fields})


# -- Persistent memory management (PRD 6.4) ----------------------------------

@router.get("/profiles/{profile_id}/memory/{interactor_id}")
def view_memory(profile_id: str, interactor_id: str,
                request: Request) -> list[MessageOut]:
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    rows = db.connect().execute(
        "SELECT * FROM messages WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at, rowid",
        (profile_id, interactor_id),
    ).fetchall()
    return [message_out(dict(row)) for row in rows]


@router.delete("/profiles/{profile_id}/memory/{interactor_id}", status_code=204)
def clear_memory(profile_id: str, interactor_id: str,
                 request: Request) -> None:
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    conn = db.connect()
    conn.execute("DELETE FROM messages WHERE profile_id=? AND interactor_id=?",
                 (profile_id, interactor_id))
    conn.execute("DELETE FROM engagement WHERE profile_id=? AND interactor_id=?",
                 (profile_id, interactor_id))
    conn.commit()


# -- Owner moderation queue (PRD 6.5) ----------------------------------------

@router.get("/profiles/{profile_id}/moderation/queue")
def moderation_queue(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM messages WHERE profile_id=? AND status='pending'"
        " ORDER BY created_at", (profile_id,),
    ).fetchall()
    # Owners see full content, including held messages.
    return [dict(row) for row in rows]


def _resolve_message(message_id: str, status: str, request: Request) -> dict:
    conn = db.connect()
    row = conn.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "message not found")
    require_owner(row["profile_id"], request)   # only the owner moderates
    if row["status"] != "pending":
        raise HTTPException(409, f"message is already {row['status']}")
    conn.execute("UPDATE messages SET status=? WHERE id=?", (status, message_id))
    conn.commit()
    return {"id": message_id, "status": status}


@router.post("/moderation/{message_id}/approve")
def approve_message(message_id: str, request: Request) -> dict:
    return _resolve_message(message_id, "approved", request)


@router.post("/moderation/{message_id}/reject")
def reject_message(message_id: str, request: Request) -> dict:
    return _resolve_message(message_id, "rejected", request)
