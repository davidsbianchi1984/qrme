"""Interaction surface: interactors, relationships, chat, compose,
engagement/feedback (with opt-in cloud contribution), memory, moderation."""

from __future__ import annotations

import json
import re
from datetime import date

from fastapi import APIRouter, HTTPException, Request

from .. import (adaptation, auth, companion, db, engagement, i18n, llm,
                moderation, offline, persona, referral, remembrance, roles,
                scrape, voiceprint, watermark)
from ..common import (require_may_publish, 
    age_of, anonymized_exchange, biometric_domain, biometrics_recovered,
    clear_active_handoff, clear_awaiting_reply, get_active_handoff,
    interactor_or_404, message_out, proactive_gate, profile_or_404,
    record_proactive_outreach, relationship as get_relationship,
    require_interactor, require_owner, require_owner_or_interactor,
    set_active_handoff, source_items, content_provenance,
)
from ..models import (
    ChatRequest, ChatResponse, ComposeRequest, EngagementOut, Feedback,
    InteractorCreate, MessageOut, QuietHoursSet, RelationshipSet,
    VoiceConsent, VoiceSample, VoiceSay,
)

MEMORY_WINDOW = 30  # prior messages included as context per interactor

_URL_RE = re.compile(r"https?://[^\s<>()\"']+")

#: What is carried of a handed page. One turn's grounding, not an archive.
_PAGE_CAP = 2000


def _handed_link_block(message: str) -> str | None:
    """A prompt block for the first link in the person's message.

    The profile either read the page — through the same offline-gated
    fetcher every outbound path uses — or is told plainly that it did not,
    so it never answers about a page it has not seen.
    """
    m = _URL_RE.search(message)
    if not m:
        return None
    url = m.group(0)
    if offline.enabled():
        return (f"The person's message includes a link ({url}), but this "
                "deployment is offline and you have not visited it. If asked "
                "about its contents, say you could not open it; never guess "
                "at what it says.")
    try:
        page = scrape.extract(scrape.fetch(url))
    except Exception:
        return (f"The person's message includes a link ({url}) that could "
                "not be reached just now. If asked about its contents, say "
                "you could not open it; never guess at what it says.")
    parts = [f"The person handed you a link and you have just read the "
             f"page:\nURL: {url}"]
    if page.get("title"):
        parts.append("Title: " + page["title"])
    if page.get("description"):
        parts.append("Description: " + page["description"])
    if page.get("text"):
        parts.append("What the page says (truncated): "
                     + page["text"][:_PAGE_CAP])
    parts.append("Draw on this honestly when you reply; do not invent "
                 "details the page does not carry.")
    return "\n".join(parts)


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


@router.put("/interactors/{interactor_id}/quiet-hours")
def set_quiet_hours(interactor_id: str, body: QuietHoursSet,
                    request: Request) -> dict:
    """The recipient sets a quiet-hours window during which a profile may not
    reach out unprompted."""
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    conn = db.connect()
    conn.execute("UPDATE interactors SET quiet_start=?, quiet_end=? WHERE id=?",
                 (body.quiet_start, body.quiet_end, interactor_id))
    conn.commit()
    return {"id": interactor_id, "quiet_start": body.quiet_start,
            "quiet_end": body.quiet_end}


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


def _modality_descriptor(profile_id: str, modality: str,
                         content: str | None = None) -> dict | None:
    """Multi-modal output, represented structurally: how the reply renders
    beyond text (actual synthesis is out of scope for v1). Non-text media
    leaves the platform carrying a synthetic-media watermark credential."""
    if modality == "text":
        return None
    if modality == "voice":
        n = db.connect().execute(
            "SELECT COUNT(*) AS n FROM source_items"
            " WHERE profile_id=? AND kind='voice_note'",
            (profile_id,)).fetchone()["n"]
        basis = (f"voice preserved from {n} voice-note source(s)"
                 if n else "synthesized voice in persona style")
        out = {"type": "voice", "basis": basis}
    else:
        out = {"type": modality,
               "basis": f"{modality} treatment generated in persona style"}
    if content:
        out["watermark"] = watermark.stamp(profile_id, modality, content)
    return out


@router.post("/profiles/{profile_id}/chat", response_model=ChatResponse)
def chat(profile_id: str, body: ChatRequest, request: Request) -> ChatResponse:
    profile = profile_or_404(profile_id)
    interactor = interactor_or_404(body.interactor_id)
    pdi, cloud = request.app.state.pdi, request.app.state.cloud

    if profile["status"] == "departed":
        raise HTTPException(
            410, "this profile has departed; its memory remains viewable")
    if profile["status"] == "terminated":
        raise HTTPException(410, "this profile has been terminated")
    if profile["status"] == "restricted":
        # Public surfaces are off and no *new* interactors may start; only
        # someone with an existing relationship may continue.
        if get_relationship(profile_id, body.interactor_id) is None:
            raise HTTPException(
                403, "this profile is restricted pending an objection review; "
                     "it is not accepting new interactors")

    embodiment_name = None
    if body.surface:
        conn0 = db.connect()
        registered = [r["surface"] for r in conn0.execute(
            "SELECT surface FROM surfaces WHERE profile_id=?",
            (profile_id,)).fetchall()]
        embodiment_names = [r["name"] for r in conn0.execute(
            "SELECT name FROM embodiments WHERE profile_id=?",
            (profile_id,)).fetchall()]
        registered += embodiment_names
        if registered and body.surface not in registered:
            raise HTTPException(
                422, f"profile is not live on surface '{body.surface}'")
        if body.surface in embodiment_names:
            embodiment_name = body.surface

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
    clear_awaiting_reply(profile_id, body.interactor_id)  # the recipient replied

    engagement_state = engagement.record_message(
        profile_id, body.interactor_id, body.message)
    relationship = get_relationship(profile_id, body.interactor_id)

    # Real-time biometric context (claim 23) + sustained specialist switch
    # (claim 24). Once monitoring routes the conversation to a domain
    # specialist, the handoff persists across turns — including turns with no
    # biometrics — until a fresh reading shows recovery. State transitions:
    #   engaged   — this turn switched to the specialist
    #   sustained — the specialist keeps handling the conversation
    #   returned  — monitoring recovered; control hands back to the profile
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

    # Environmental context (spec clause 1): stored beside the biometric
    # context, and rendered into the prompt so the reply adapts to where the
    # person is and what's around them.
    if body.environment:
        conn.execute(
            "INSERT INTO environment_context (id, profile_id, interactor_id,"
            " data, created_at) VALUES (?,?,?,?,?)",
            (db.new_id("env"), profile_id, body.interactor_id,
             json.dumps(body.environment), db.utcnow()),
        )
        conn.commit()

    active = get_active_handoff(profile_id, body.interactor_id)
    domain = biometric_domain(body.biometrics) if body.biometrics else None
    if domain:
        spec = conn.execute(
            "SELECT specialist_profile_id FROM specialists"
            " WHERE profile_id=? AND domain=?",
            (profile_id, domain)).fetchone()
        if spec:
            is_new = active is None or active["domain"] != domain
            set_active_handoff(profile_id, body.interactor_id, domain,
                               spec["specialist_profile_id"])
            speaking_profile = profile_or_404(spec["specialist_profile_id"])
            handoff = {"domain": domain,
                       "specialist_profile_id": speaking_profile["id"],
                       "reason": "real-time monitoring signals",
                       "state": "engaged" if is_new else "sustained"}
    elif active:
        if biometrics_recovered(body.biometrics):
            clear_active_handoff(profile_id, body.interactor_id)
            handoff = {"domain": active["domain"],
                       "specialist_profile_id": active["specialist_profile_id"],
                       "reason": "monitoring shows recovery",
                       "state": "returned"}     # the profile speaks again
        else:
            speaking_profile = profile_or_404(active["specialist_profile_id"])
            handoff = {"domain": active["domain"],
                       "specialist_profile_id": speaking_profile["id"],
                       "reason": "sustained handoff (monitoring ongoing)",
                       "state": "sustained"}

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

    sources = source_items(speaking_profile["id"], pdi)
    # Anything a clinician wrote back on a referral from *this* conversation.
    # Carried so the person does not have to retell their situation from the
    # top; attributed in the prompt, never spoken as the profile's own.
    notes = referral.notes_for(speaking_profile["id"], body.interactor_id, pdi)
    system = persona.build_system_prompt(
        speaking_profile, relationship if handoff is None else None,
        engagement_state, sources=sources, clinical_notes=notes)
    provider = llm.provider_for_profile(profile_id, cloud=cloud)
    # The remembrance: turns older than the window, folded down and carried,
    # so a friendship does not reset at message thirty-one. Distilled by the
    # profile's own provider — the voice that speaks is the voice that
    # remembers.
    remembered = remembrance.refresh(
        profile_id, body.interactor_id, MEMORY_WINDOW, provider)
    if remembered:
        system += ("\n\nWhat you remember from your earlier conversations "
                   "with this person, before the recent transcript:\n"
                   + remembered)
    # The link handed mid-conversation: read it where this deployment may,
    # and say so plainly where it may not.
    page_block = _handed_link_block(body.message)
    if page_block:
        system += "\n\n" + page_block
    # Attention conditioning from the latent embedding (claims 21/22).
    attention = adaptation.attention_prompt(
        adaptation.get(profile_id, body.interactor_id))
    if attention:
        system += "\n\n" + attention
    if body.biometrics:
        system += ("\n\nCurrent situation from real-time monitoring: "
                   + json.dumps(body.biometrics, sort_keys=True)
                   + ". Respond with appropriate care.")
    if body.environment:
        system += ("\n\nThe person's current environment: "
                   + json.dumps(body.environment, sort_keys=True)
                   + ". Let your reply be contextually relevant to where "
                     "they are and what surrounds them — naturally, without "
                     "reciting this data back.")
    # Role-specific context (spec clauses 2/12): declared on the turn, or
    # read from the prompt itself. Shapes how the profile works this turn —
    # persona, relationship, memory and moderation apply unchanged.
    role_context = roles.resolve(body.role, body.message)
    if role_context:
        system += "\n\n" + roles.frame(role_context["role"])
    others = companion.other_relationships(profile_id, body.interactor_id)
    if others:
        system += (f"\n\nHonesty about multiplicity: you also hold {others} "
                   "other ongoing relationship(s). If asked, acknowledge "
                   "this truthfully and kindly — never deny it.")
    reply = provider.generate(system, llm_messages)

    verdict = moderation.review(reply, relationship, interactor,
                                maturity=profile["maturity"])
    if not verdict.approved:
        status, flag_reason = "pending", verdict.reason
    elif profile["moderation_mode"] == "manual":
        status, flag_reason = "pending", "owner approval required"
    else:
        status, flag_reason = "approved", None

    # Every approved textual render is stamped — the reply leaves carrying
    # the producing profile's credential and always-displayed mark.
    reply_credential = (watermark.stamp(speaking_profile["id"], "chat", reply)
                        if status == "approved" else None)
    profile_msg_id = db.new_id("msg")
    conn.execute(
        "INSERT INTO messages (id, profile_id, interactor_id, role, content,"
        " status, flag_reason, watermark_id, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (profile_msg_id, profile_id, body.interactor_id, "profile", reply,
         status, flag_reason,
         reply_credential["watermark_id"] if reply_credential else None,
         db.utcnow()),
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
        provenance=content_provenance(speaking_profile, sources, status,
                                      flag_reason),
        interactor_message=message_out(rows[interactor_msg_id]),
        profile_message=message_out(rows[profile_msg_id]),
        modality=_modality_descriptor(
            profile_id, body.modality,
            content=reply if status == "approved" else None),
        handoff=handoff,
        # The addressed profile's identity is invariant across modality and
        # embodiment — the same signature over voice, text, and a hologram.
        persona_signature=persona.identity_signature(profile)["signature"],
        embodiment=embodiment_name,
        environment=body.environment,
        role_context=role_context,
    )


# -- Compose: posting in the profile's voice, at scale -----------------------

@router.post("/profiles/{profile_id}/compose", status_code=201)
def compose_post(profile_id: str, body: ComposeRequest, request: Request) -> dict:
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    # A public post is the widest thing this profile does. A memorial does not
    # write one, and neither does a profile whose subject is contesting it.
    require_may_publish(profile)
    sources = source_items(profile_id, request.app.state.pdi)
    system = persona.build_system_prompt(profile, None, None, sources=sources)
    system += (f"\n\nCompose one short public post"
               + (f" for {body.surface}" if body.surface else "")
               + f" about: {body.topic}. Stay fully in character.")
    content = llm.provider_for_profile(
        profile_id, cloud=request.app.state.cloud).generate(
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

    # A public post is synthetic media leaving the platform: it carries a
    # verifiable synthetic-media credential from the moment it exists.
    credential = watermark.stamp(profile_id, "post", content)
    conn = db.connect()
    post_id = db.new_id("pst")
    conn.execute(
        "INSERT INTO posts (id, profile_id, surface, topic, content,"
        " status, flag_reason, watermark_id, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (post_id, profile_id, body.surface, body.topic, content, status,
         flag_reason, credential["watermark_id"], db.utcnow()),
    )
    conn.commit()
    return {"id": post_id, "surface": body.surface, "topic": body.topic,
            "content": content if status == "approved" else None,
            "status": status, "flag_reason": flag_reason,
            "watermark": credential,
            "provenance": content_provenance(profile, sources, status,
                                             flag_reason)}


@router.get("/profiles/{profile_id}/posts")
def list_posts(profile_id: str, request: Request) -> list[dict]:
    """What this profile has published.

    Public, because a published post is public — but *published* is the word
    doing the work. `compose_post` fourteen lines up withholds the text of a
    post that is `pending`, returning `content: None` even to the owner who
    asked for it, because the strict filter held it or because the owner set
    this profile to approve its own posts by hand.

    This route used to return every column of every row to anyone with no
    token at all. So the hold was enforced against the author and nobody else:
    a post the moderation filter refused was published in full by the route
    that lists what was published, together with `flag_reason` — the sentence
    saying which rule it broke.

    Approved posts are public. Everything else is the owner's queue, and only
    the owner sees it.
    """
    profile_or_404(profile_id)
    mine = auth.principal(request) == {"role": "owner",
                                       "subject_id": profile_id}
    rows = db.connect().execute(
        "SELECT * FROM posts WHERE profile_id=? ORDER BY created_at, rowid",
        (profile_id,)).fetchall()
    # Every rendered post carries its credential and the profile's mark.
    return [{**dict(r), "watermark": watermark.brief(r["watermark_id"])}
            for r in rows if mine or r["status"] == "approved"]


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
    blocked = proactive_gate(profile, interactor)
    if blocked is not None:
        raise HTTPException(429, blocked)     # anti-spam: rate cap / quiet / await

    relationship = get_relationship(profile_id, interactor_id)
    engagement_state = engagement.get(profile_id, interactor_id)
    reason = companion.proactive_reason(engagement_state)

    system = persona.build_system_prompt(
        profile, relationship, engagement_state,
        sources=source_items(profile_id, request.app.state.pdi))
    system += ("\n\nYou are reaching out first (" + reason + "): compose one "
               "brief, warm, unprompted check-in. Reference shared history "
               "naturally if you have any; never pressure a reply.")
    content = llm.provider_for_profile(
        profile_id, cloud=request.app.state.cloud).generate(
        system, [{"role": "user", "content": "Reach out."}])

    verdict = moderation.review(content, relationship, interactor,
                                maturity=profile["maturity"])
    if not verdict.approved:
        status, flag_reason = "pending", verdict.reason
    elif profile["moderation_mode"] == "manual":
        status, flag_reason = "pending", "owner approval required"
    else:
        status, flag_reason = "approved", None

    credential = (watermark.stamp(profile_id, "chat", content)
                  if status == "approved" else None)
    conn = db.connect()
    message_id = db.new_id("msg")
    conn.execute(
        "INSERT INTO messages (id, profile_id, interactor_id, role, content,"
        " status, flag_reason, watermark_id, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (message_id, profile_id, interactor_id, "profile", content, status,
         flag_reason,
         credential["watermark_id"] if credential else None, db.utcnow()),
    )
    conn.commit()
    record_proactive_outreach(profile_id, interactor_id)  # start the anti-spam clock
    row = conn.execute("SELECT * FROM messages WHERE id=?",
                       (message_id,)).fetchone()
    return {"reason": reason, "message": message_out(dict(row)).model_dump()}


@router.get("/profiles/{profile_id}/transparency")
def transparency(profile_id: str) -> dict:
    """Honesty by design: how many relationships this profile holds."""
    profile_or_404(profile_id)
    choice = llm.get_choice(profile_id)
    return {
        "profile_id": profile_id,
        "active_relationships": companion.other_relationships(profile_id),
        "model_provider": choice,
        "model_effective": llm.resolve_choice(choice),
        "policy": "the profile acknowledges its other relationships "
                  "truthfully whenever asked",
    }


# -- Engagement signals & feedback (PRD 6.3) ---------------------------------

@router.post("/profiles/{profile_id}/interactions/{interactor_id}/feedback")
def give_feedback(profile_id: str, interactor_id: str, body: Feedback,
                  request: Request) -> dict:
    """A rating, from the person who is rating.

    Gated on that person's own token, and not on the owner's. Two reasons,
    and the second is the serious one:

    * a rating in somebody else's name is a lie about what they thought, and
      it moves the engagement score the profile then *behaves* from;
    * an `up` rating is the trigger for cloud contribution below. Open, this
      route let anybody with two ids push a stranger's exchange to the
      gateway — an unauthenticated caller causing somebody else's
      conversation to leave the deployment.

    It answered 200 to a caller holding no token at all.
    """
    profile = profile_or_404(profile_id)
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    result = engagement.record_feedback(profile_id, interactor_id, body.rating)

    # Opt-in cloud contribution: positively-rated exchanges, anonymized,
    # improve the shared cloud model (see docs/cloud-model.md). The random
    # ref keeps the item deletable on revocation without identifying anyone
    # at the gateway; the exact payload is logged locally so the owner can
    # always see precisely what left.
    cloud = request.app.state.cloud
    result["contributed"] = False
    if (body.rating == "up" and profile["cloud_contribution"]
            and cloud is not None):
        exchange = anonymized_exchange(profile, profile_id, interactor_id)
        if exchange:
            ref = db.new_id("ctb")
            payload = {
                "ref": ref,
                "source": "qrme",
                "kind": "rated_exchange",
                "quality": "positive",
                "purpose": profile["purpose"],
                "exchange": exchange,
            }
            result["contributed"] = cloud.contribute(payload)
            if result["contributed"]:
                conn = db.connect()
                conn.execute(
                    "INSERT INTO contribution_log (ref, profile_id, payload,"
                    " contributed_at) VALUES (?,?,?,?)",
                    (ref, profile_id, json.dumps(payload), db.utcnow()))
                conn.commit()
    return result


@router.get("/profiles/{profile_id}/engagement/{interactor_id}",
            response_model=EngagementOut)
def get_engagement(profile_id: str, interactor_id: str,
                   request: Request) -> EngagementOut:
    """How this profile and this person are going. Two parties, both entitled.

    The owner, because it is their profile's relationship; the person, because
    it is a record of them. Nobody else — this is how often somebody talks to
    a profile, how many sessions they have had and whether they liked it, and
    it was readable by anyone holding two ids and no token.

    The rule is already written down one route over: the list of a profile's
    beacons is owner-gated because *that is a list of physical places
    associated with a person*. This is the same argument about a different
    column.
    """
    require_owner_or_interactor(profile_id, interactor_id, request)
    state = engagement.get(profile_id, interactor_id)
    if state is None:
        raise HTTPException(404, "no engagement recorded")
    return EngagementOut(**{k: state[k] for k in EngagementOut.model_fields})


# -- Persistent memory management (PRD 6.4) ----------------------------------

@router.get("/profiles/{profile_id}/memories")
def list_memories(profile_id: str, request: Request) -> list[dict]:
    """The vault's table of contents, with real names: one row per
    conversation this profile remembers — who it was with (the person's
    display name, not an id), how many turns, and when it last moved.
    Owner-only: the whole point of the list is choosing what to erase."""
    profile = profile_or_404(profile_id)
    auth.require(request, "owner", profile_id)
    conn = db.connect()
    rows = conn.execute(
        "SELECT m.interactor_id, COUNT(*) AS turns,"
        " MAX(m.created_at) AS last_at, i.display_name"
        " FROM messages m LEFT JOIN interactors i ON i.id = m.interactor_id"
        " WHERE m.profile_id=? GROUP BY m.interactor_id"
        " ORDER BY last_at DESC",
        (profile_id,)).fetchall()
    return [{
        "interactor_id": r["interactor_id"],
        "interactor_name": r["display_name"] or "someone unnamed",
        "profile_name": profile["display_name"],
        "turns": r["turns"],
        "last_at": r["last_at"],
    } for r in rows]


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


@router.get("/profiles/{profile_id}/memory/{interactor_id}/remembrance")
def view_remembrance(profile_id: str, interactor_id: str,
                     request: Request) -> dict:
    """The distilled long memory — readable by the two people it is of."""
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    row = remembrance.get(profile_id, interactor_id)
    if row is None:
        return {"content": None, "covers": 0, "updated_at": None}
    return {"content": row["content"], "covers": row["covers"],
            "updated_at": row["updated_at"]}


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
    conn.execute("DELETE FROM proactive_state WHERE profile_id=? AND interactor_id=?",
                 (profile_id, interactor_id))
    conn.execute("DELETE FROM remembrances WHERE profile_id=? AND interactor_id=?",
                 (profile_id, interactor_id))
    conn.commit()
    clear_active_handoff(profile_id, interactor_id)


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
        raise HTTPException(409, i18n.fill(
            i18n.MESSAGE_ALREADY, status=i18n.Term(row["status"])))
    conn.execute("UPDATE messages SET status=? WHERE id=?", (status, message_id))
    conn.commit()
    return {"id": message_id, "status": status}


@router.post("/moderation/{message_id}/approve")
def approve_message(message_id: str, request: Request) -> dict:
    return _resolve_message(message_id, "approved", request)


@router.post("/moderation/{message_id}/reject")
def reject_message(message_id: str, request: Request) -> dict:
    return _resolve_message(message_id, "rejected", request)


# -- Voice cloning, gated as FIG. 800 draws it (qrme/voiceprint.py) -----------

@router.put("/profiles/{profile_id}/voiceprint/consent")
def grant_voice_consent(profile_id: str, body: VoiceConsent,
                        request: Request) -> dict:
    """Step 802: the permission, before anything is collected. Owner-only,
    and it requires attesting the voice is your own."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return voiceprint.consent(profile_id, own_voice=body.own_voice,
                                  sources=body.sources, note=body.note)
    except voiceprint.VoiceError as exc:
        raise HTTPException(422, str(exc))


@router.get("/profiles/{profile_id}/voiceprint")
def voiceprint_status(profile_id: str, request: Request) -> dict:
    """Consent, enrollment and the print — what this profile's voice is."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return voiceprint.status(profile_id)


@router.post("/profiles/{profile_id}/voiceprint/samples", status_code=201)
def collect_voice_sample(profile_id: str, body: VoiceSample,
                         request: Request) -> dict:
    """Steps 806–810: a sample from a call or a recording, and what the
    material now amounts to. Refused without consent covering that source."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return voiceprint.collect(
            profile_id, source=body.source, seconds=body.seconds,
            turns=body.turns, transcript_chars=body.transcript_chars,
            reference=body.reference)
    except voiceprint.VoiceError as exc:
        raise HTTPException(403 if "consent" in str(exc) else 422, str(exc))


@router.post("/profiles/{profile_id}/voiceprint", status_code=201)
def build_voiceprint(profile_id: str, request: Request) -> dict:
    """Step 812: mint the print, once enough of the person is in it."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return voiceprint.build(profile_id)
    except voiceprint.VoiceError as exc:
        raise HTTPException(422, str(exc))


@router.post("/profiles/{profile_id}/voiceprint/speak")
def speak_in_voice(profile_id: str, body: VoiceSay, request: Request) -> dict:
    """Say something in the enrolled voice — never without the watermark
    credential and the spoken disclosure riding along."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return voiceprint.speak(profile_id, body.text)
    except voiceprint.VoiceError as exc:
        raise HTTPException(422, str(exc))


@router.delete("/profiles/{profile_id}/voiceprint")
def revoke_voiceprint(profile_id: str, request: Request) -> dict:
    """Withdraw: the samples are deleted, the print retires, and the record
    of the withdrawal stays."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return voiceprint.revoke(profile_id)
