"""Interaction surface: interactors, relationships, chat, compose,
engagement/feedback (with opt-in cloud contribution), memory, moderation."""

from __future__ import annotations

import json
import re
from datetime import date

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from .. import (adaptation, auth, briefcase, companion, contacts, db, opendoor,
                engagement, i18n,
                llm, moderation, offline, persona, referral, remembrance,
                roles, scrape, voiceprint, watermark)
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
    ContactsGrant, ContactsSync,
    InteractorCreate, MemoryForget, MemoryStrike, MessageOut, QuietHoursSet,
    RehearsalOpen, RehearsalSay, RelationshipSet, TurnEdit, VoiceConsent,
    VoiceBind, VoiceSample, VoiceSay,
)

MEMORY_WINDOW = 30  # prior messages included as context per interactor

_URL_RE = re.compile(r"https?://[^\s<>()\"']+")

#: What is carried of a handed page. One turn's grounding, not an archive.
_PAGE_CAP = 2000


def remembered_environment(profile_id: str,
                           interactor_id: str) -> dict | None:
    """The latest stored environment for this relationship, if it is recent
    enough to plausibly still be the room (six hours; location changes
    faster than a persona should presume)."""
    row = db.connect().execute(
        "SELECT data, created_at FROM environment_context"
        " WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (profile_id, interactor_id)).fetchone()
    if row is None:
        return None
    from datetime import datetime, timedelta
    try:
        seen = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    except ValueError:
        return None
    from datetime import timezone
    if datetime.now(timezone.utc) - seen > timedelta(hours=6):
        return None
    return json.loads(row["data"])


def _handed_link_block(message: str,
                       profile_id: str | None = None) -> str | None:
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
        page = scrape.extract(scrape.fetch(url, profile_id))
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


@router.get("/interactors/{interactor_id}/picture")
def get_own_picture(interactor_id: str, request: Request) -> dict:
    """Your own picture, if you have put one up.

    Yours alone to read: a person's photograph is not a directory anybody
    with an id may page through. The room draws it from the seat state,
    which the people in that room already share.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    row = db.connect().execute(
        "SELECT * FROM interactors WHERE id=?", (interactor_id,)).fetchone()
    keys = row.keys()
    return {"interactor_id": interactor_id,
            "url": row["avatar_url"] if "avatar_url" in keys else None,
            # Never. A photograph of your own face is authentic media, and
            # stamping the synthetic-media mark into it would be a false
            # statement in exactly the direction the mark exists to prevent.
            "ai_marked": False}


@router.get("/interactors/{interactor_id}/contribution")
def own_contribution(interactor_id: str, request: Request) -> dict:
    """Whether your hosted memories feed the shared model, and how much has
    gone.

    The count is here because *you can turn it off* is a different promise
    from *you can see what it did*, and a switch with no number beside it
    asks somebody to take the first on faith.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    from .. import recollection
    return recollection.contribution_state(interactor_id)


@router.delete("/interactors/{interactor_id}/contribution")
def stop_own_contribution(interactor_id: str, request: Request) -> dict:
    """Turn it off, and ask the gateway to drop everything already sent.

        asked     can this be turned off
        mattered  does turning it off reach what already left

    A switch that only means *from now on* is the weaker half of the
    promise. The refs carry no identity, so the past can be pulled back
    without the gateway ever being told whose it was.

    Deliberately a DELETE and not a PATCH taking `false`: this ends
    something and removes what it produced, and a route that only ever
    goes one way should be spelled the way it behaves. Turning it back on
    is signing up again, at the door that says what the tier means.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    from .. import recollection
    return recollection.stop_contributing(request.app.state.cloud,
                                          interactor_id)


@router.get("/interactors/{interactor_id}/memories")
def own_memories(interactor_id: str, request: Request) -> dict:
    """Everything you hold, across every profile you have talked to.

        asked     does the person's record outlive the profile
        mattered  can they still get to it

    A memory holds what **you** said — only a person's own turns are ever
    sealed — and since the record moved to your side it lives in your
    vault, under your key, on your plan. Deleting a profile no longer
    takes it: the erasure right is a right over the profile's own words.

    Which left this missing. The only way to read a memory back was
    `GET /profiles/{id}/memory/{who}`, and that begins by looking the
    profile up, so a record that survived the profile had no door at all.
    Keeping somebody's words somewhere they cannot reach them is not the
    promise; it is the opposite of it.

    Your own token, and only yours. This is the whole of one person's
    record in one answer — the single most private read in this product —
    so it is guarded exactly like the picture that has your face on it.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    from .. import recollection
    return recollection.theirs(request.app.state.pdi, interactor_id)


@router.post("/interactors/{interactor_id}/picture", status_code=201)
async def set_own_picture(interactor_id: str, request: Request,
                          filename: str | None = None) -> dict:
    """Your own picture — the person's, not a profile's.

        asked     can a person show a face
        mattered  whose face is it

    Until this door, only PROFILES had portraits. A human in a room got a
    display name and two initials, and the only way to show a face was to
    borrow the portrait of a profile — which put the same picture on the
    human seat and the synthetic seat beside it, on the one screen where
    telling the two apart is the entire point. Field report: "I don't know
    why both profile photos don't show up, one says You with a Y on it, it
    should be my image that I have on my profile photo."

    A person's face belongs to the person. It travels with them into every
    room rather than being set again in each one, and it is **never
    AI-marked** — `media.py` states the rule and this is exactly the case
    it was written for.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    from .. import media as media_mod, roomface

    data = await request.body()
    try:
        saved = media_mod.save(interactor_id, data, name=filename or None)
    except media_mod.MediaError as exc:
        raise HTTPException(exc.status, exc.message) from exc
    if saved["kind"] not in roomface.FACE_KINDS:
        raise HTTPException(
            422, "a picture of you is a picture — JPEG, PNG, GIF or WebP")
    conn = db.connect()
    conn.execute("UPDATE interactors SET avatar_id=?, avatar_url=? WHERE id=?",
                 (saved["id"], saved["url"], interactor_id))
    conn.commit()
    return {"interactor_id": interactor_id, "url": saved["url"],
            "ai_marked": False}


@router.delete("/interactors/{interactor_id}/picture")
def clear_own_picture(interactor_id: str, request: Request) -> dict:
    """Back to your initials. Taking your own face down is the one action
    where keeping the file would be the surprise."""
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    conn = db.connect()
    conn.execute(
        "UPDATE interactors SET avatar_id=NULL, avatar_url=NULL WHERE id=?",
        (interactor_id,))
    conn.commit()
    return {"interactor_id": interactor_id, "url": None, "ai_marked": False}


@router.put("/interactors/{interactor_id}/contacts/grant")
def decide_contacts(interactor_id: str, body: ContactsGrant,
                    request: Request) -> dict:
    """The one switch for the people in your phone (qrme/contacts.py).

    Off until chosen, because most of an address book is somebody else.
    Turning it off drops the book — both custodies — right here: nobody
    should have to find a second control to make this one mean what it
    says. Your own token, like the picture that has your face on it: a
    person's book is guarded exactly as their photograph is.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    return contacts.decide(interactor_id, body.consented,
                           pdi=request.app.state.pdi)


@router.put("/interactors/{interactor_id}/contacts")
def sync_contacts(interactor_id: str, body: ContactsSync,
                  request: Request) -> dict:
    """Replace the book with what the device has — the only write.

    A synced source, never something people type: the entries come off the
    device under the grant above. Sealed into PDI where the person's plan
    has a vault, platform custody otherwise — one book, one withdrawal,
    either way (the module says why, at length).
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    try:
        return contacts.sync(interactor_id,
                             [e.model_dump() for e in body.entries],
                             pdi=request.app.state.pdi)
    except contacts.NotGranted as exc:
        raise HTTPException(403, i18n.raised(exc)) from None


@router.get("/interactors/{interactor_id}/contacts")
def contacts_book(interactor_id: str, request: Request) -> dict:
    """Everybody in the synced book — names and whether a shell matched
    them to an account here, never the numbers back out."""
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    try:
        return {"book": contacts.book(interactor_id,
                                      pdi=request.app.state.pdi),
                "held": contacts.held(interactor_id)}
    except contacts.NotGranted as exc:
        raise HTTPException(403, i18n.raised(exc)) from None
    except contacts.VaultUnreachable as exc:
        # *You know nobody* and *I could not open your book* are different
        # sentences; 503 keeps them apart on the wire too.
        raise HTTPException(503, str(exc)) from None


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
                422, i18n.fill(i18n.NOT_LIVE_ON_SURFACE, surface=body.surface))
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

    # The turn becomes a memory (qrme/recollection.py): sealed in the tandem
    # and embedded, so a later reply can find this moment by meaning. Plan-
    # gated like every seal point, and non-fatal — a turn that lands and is
    # not remembered beats a turn refused because the tandem was down.
    #
    # Gated on the PERSON's plan, not the profile's. It was the profile's,
    # which meant whether your conversation was remembered depended on
    # whether somebody else was paying for it, and the record lived in
    # their account under their key — where you could not read it, could
    # not take it, and would lose it if they stopped paying. A memory of a
    # conversation is worth having because the person comes back; it
    # belongs on the side of the person who might.
    from .. import recollection, storage as storage_mod, tiers as tiers_mod
    memory_vault, memory_posture = storage_mod.memory_for(
        tiers_mod.plan_of_interactor(body.interactor_id), pdi)
    if memory_posture:
        recollection.remember(memory_vault or pdi, profile_id,
                              body.interactor_id, interactor_msg_id,
                              body.message, posture=memory_posture)
        # Hosted only, and only while the person leaves it on. A sealed
        # memory is never contributed whatever any switch says — that is
        # the whole of what a private plan buys.
        if memory_posture == "open_cloud":
            recollection.contribute(request.app.state.cloud, profile_id,
                                    body.interactor_id, interactor_msg_id,
                                    body.message)

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
        engagement_state, sources=sources, clinical_notes=notes,
        # Who is on the other side, so a profile meeting its own maker is
        # not told to treat them as a stranger. Knowledge, never authority —
        # `_OWNER_NOTE` says so in the prompt itself.
        viewer_id=body.interactor_id,
        # And what they just said, which is what selects the doors of this
        # application the prompt carries. Without it the profile still gets
        # the consent doors and the index of names; with it, the screen they
        # are actually asking about arrives described.
        said=body.message,
        # And where they are standing as they say it, so a door is given
        # from the screen they are actually on.
        standing=body.standing)
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
    # And the other axis of memory: the distillate above remembers forward,
    # in order; this finds the moment that is *about* what was just said,
    # however long ago — the pair's own memories only.
    # The real vault, not the plan-gated one: `vault_for` gates writes
    # only, and a member who moved to Free still has sealed moments this
    # reply must go on finding — the same split the shelf holds.
    #
    # And when this profile's provider is the vault itself, recall steps
    # aside: the resident ranks the pair's seals against the question and
    # answers from them *inside* the facility (llm.VaultProvider), so
    # fetching the lines here would read the same seals twice and say
    # them twice. Whether the grounding actually happened is disclosed in
    # the provenance, not assumed.
    vault_grounds = llm.resolve_choice(llm.get_choice(profile_id)) == "vault"
    recalled_block = None if vault_grounds else recollection.chat_block(
        pdi, profile_id, body.interactor_id, body.message)
    if recalled_block:
        system += "\n\n" + recalled_block
    # The link handed mid-conversation: read it where this deployment may,
    # and say so plainly where it may not. Only for a link this turn has not
    # already imported — a briefcase item is the same page, read once and
    # kept, and carrying both would pay for it twice in the same prompt.
    if not briefcase.holds_link(profile_id, body.interactor_id, body.message):
        page_block = _handed_link_block(body.message, profile_id)
        if page_block:
            system += "\n\n" + page_block
    # The briefcase: everything this person has handed this profile, as
    # digests. Long material enters the prompt at the size of its reading,
    # on this turn and every turn after it.
    carried = briefcase.block(profile_id, body.interactor_id)
    if carried:
        system += "\n\n" + carried
    # The watched pages (qrme/lookout.py): the vault keeps their current
    # captures fresh on its own appointments, and the profile answers
    # from them — dated, capped, and absent rather than fatal when the
    # tandem cannot be read. The real vault: this is a read.
    from .. import lookout as lookout_mod
    watched = lookout_mod.prompt_block(profile_id, pdi)
    if watched:
        system += "\n\n" + watched
    # Attention conditioning from the latent embedding (claims 21/22).
    attention = adaptation.attention_prompt(
        adaptation.get(profile_id, body.interactor_id))
    if attention:
        system += "\n\n" + attention
    if body.biometrics:
        system += ("\n\nCurrent situation from real-time monitoring: "
                   + json.dumps(body.biometrics, sort_keys=True)
                   + ". Respond with appropriate care.")
    # The room is remembered, not just heard (spec clause 1: the profile
    # "dynamically adapt[s] to environmental data"). A turn that carries
    # environment speaks from it; a turn that doesn't reads the latest
    # stored context back — recent only, because yesterday's café is not a
    # room anyone is still in. The echo marks remembered context as such,
    # so a client can tell fresh data from recalled data.
    environment = body.environment
    if environment is None:
        remembered = remembered_environment(profile_id, body.interactor_id)
        if remembered:
            environment = {**remembered, "remembered": True}
    if environment:
        system += ("\n\nThe person's current environment: "
                   + json.dumps(environment, sort_keys=True)
                   + ". Let your reply be contextually relevant to where "
                     "they are and what surrounds them — naturally, without "
                     "reciting this data back."
                   + (" This context was captured earlier in the "
                      "conversation; treat it as where they most likely "
                      "still are, not as certainty."
                      if environment.get("remembered") else ""))
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
    # The pair's memory prefix rides the generation: the vault provider
    # may ground on these seals and no others. Person-first, matching the
    # key a memory is sealed under now — the isolation this enforces is
    # unchanged, since that prefix is still exactly one pair.
    #
    # This is the one place key shape is still load-bearing, because it is
    # handed to a provider as a prefix rather than resolved through the
    # ledger. A memory sealed before the shape changed is therefore not
    # grounded on. That is a thinner answer for those turns, never a wrong
    # one, and it is why nothing else here reads shape.
    ground = llm.ground_on(
        f"qrme/{body.interactor_id}/memory/{profile_id}/"
        if vault_grounds else None)
    try:
        reply = provider.generate(system, llm_messages)
    finally:
        llm.ground_reset(ground)

    # A reply may hand over a document as well as say something
    # (qrme/composing.py). Split before moderation, deliberately: the
    # document is part of what was said, so it is reviewed with the words
    # rather than slipping past a check the words had to pass.
    from .. import composing, selfsteer
    reply, composed = composing.split(reply)
    # The dial moves ride the same channel (qrme/selfsteer.py): markers
    # out before anything else reads the text — a person never reads one,
    # and the review reads the words the person will.
    reply, dial_moves = selfsteer.split(reply)
    if composed and not reply:
        # A profile that fenced a document and said nothing outside it.
        # Handing somebody a page without a word is a stranger thing than
        # the product should do on its own, so it gets the plain sentence.
        reply = i18n.tr_public(
            "Here it is.", i18n.effective_language(profile_id))

    verdict = moderation.review(
        reply + (("\n\n" + composed["body"]) if composed else ""),
        relationship, interactor, maturity=profile["maturity"])
    if not verdict.approved:
        status, flag_reason = "pending", verdict.reason
    elif profile["moderation_mode"] == "manual":
        status, flag_reason = "pending", "owner approval required"
    else:
        status, flag_reason = "approved", None

    # The profile turns its own dials — asked to, one step of 25, max or
    # none, through the same set_dials the owner's sliders write. Only on
    # an approved turn (a refused reply does not get to leave a change
    # behind), and before the stamp, so a locked profile's honest
    # sentence is part of what the credential covers.
    if dial_moves and status == "approved":
        if not selfsteer.apply(speaking_profile["id"], dial_moves,
                               bool(speaking_profile["adult_mode"])):
            reply += " " + i18n.tr_public(
                selfsteer.LOCKED_SENTENCE,
                i18n.effective_language(profile_id))

    # Every approved textual render is stamped — the reply leaves carrying
    # the producing profile's credential and always-displayed mark.
    reply_credential = (watermark.stamp(speaking_profile["id"], "chat", reply)
                        if status == "approved" else None)
    # The document becomes a real file, marked as synthetic at the moment
    # it is made — the mirror of the rule that a person's own photograph is
    # never marked. Only for an approved turn: an unapproved reply does not
    # get to leave a file behind that outlives the refusal.
    document_id = None
    if composed and status == "approved":
        from .. import media as media_mod
        try:
            data, doc_name = composing.render(composed)
            saved = media_mod.save(
                speaking_profile["id"], data, name=doc_name,
                ai_marked=True)
            document_id = saved["id"]
            watermark.stamp(speaking_profile["id"], "document",
                            composed["body"])
        except Exception:  # noqa: BLE001 — a turn that lands beats a turn
            document_id = None            # refused because a disk was full

    profile_msg_id = db.new_id("msg")
    conn.execute(
        "INSERT INTO messages (id, profile_id, interactor_id, role, content,"
        " status, flag_reason, watermark_id, media_id, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (profile_msg_id, profile_id, body.interactor_id, "profile", reply,
         status, flag_reason,
         reply_credential["watermark_id"] if reply_credential else None,
         document_id, db.utcnow()),
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

    # True only when the vault actually ranked the pair's seals and
    # answered from them — said, never assumed.
    inner = getattr(provider, "_primary", provider)
    grounded = bool(getattr(inner, "grounded", False))
    chat_provenance = content_provenance(speaking_profile, sources, status,
                                         flag_reason)
    chat_provenance["grounded_in_vault"] = grounded
    return ChatResponse(
        provenance=chat_provenance,
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
        environment=environment,
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

# -- the open door: the receiver's standing yes (qrme/opendoor.py) -----------

class DoorSet(BaseModel):
    hear_first: bool
    cadence: str = Field(default="whenever", max_length=10,
                         description="How often is welcome: daily, weekly, "
                                     "or whenever — the profile's own pace.")


@router.put("/interactors/{interactor_id}/open-door/{profile_id}")
def set_open_door(interactor_id: str, profile_id: str, body: DoorSet,
                  request: Request) -> dict:
    """Open or close your door to one profile's unprompted reach.

    The inverted connection: the person subscribes to the profile,
    rather than the profile reaching them. Yours to open and yours to
    close, on your own token; closing keeps the record and stops the
    reach the same minute."""
    require_interactor(interactor_id, request)
    profile_or_404(profile_id)
    try:
        return opendoor.set_door(interactor_id, profile_id,
                                 open_=body.hear_first,
                                 cadence=body.cadence)
    except ValueError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.get("/interactors/{interactor_id}/open-doors")
def my_open_doors(interactor_id: str, request: Request) -> dict:
    """Every standing yes you hold — open ones first, closed ones kept."""
    require_interactor(interactor_id, request)
    return {"doors": opendoor.mine(interactor_id),
            "cadences": list(opendoor.CADENCES)}


@router.get("/profiles/{profile_id}/open-doors")
def doors_open_to(profile_id: str, request: Request) -> dict:
    """Who asked to hear from this profile first — the owner's view of
    an audience that asked, rather than one the profile reached for."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return {"openers": opendoor.openers(profile_id)}


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
    # The inverted connection (qrme/opendoor.py): the owner's scope says
    # the profile is WILLING to reach out; reach still needs the person's
    # own standing yes. Both consents, neither implying the other.
    from .. import opendoor
    if not opendoor.is_open(interactor_id, profile_id):
        raise HTTPException(403, i18n.raised(
            RuntimeError(opendoor.DOOR_CLOSED)))
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
    result["cloud_contributed"] = False
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
            result["cloud_contributed"] = cloud.contribute(payload)
            if result["cloud_contributed"]:
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


# -- Rehearsal rooms: practice the hard conversation, nothing remembered -----

#: Turns a rehearsal holds while open. A practice room, not an archive.
_REHEARSAL_WINDOW = 20

_REHEARSAL_FRAME = (
    "This is a rehearsal. The person is practicing a hard conversation "
    "and you are playing the counterpart described below, in character, "
    "so they can find their words before the real one. Stay realistic — "
    "a rehearsal against a pushover teaches nothing — but never cruel. "
    "Nothing said here is remembered afterward, by either of you.\n\n"
    "The conversation being rehearsed: ")


def _rehearsal_or_404(rehearsal_id: str, profile_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM rehearsals WHERE id=? AND profile_id=?",
        (rehearsal_id, profile_id)).fetchone()
    if row is None:
        raise HTTPException(404, "no such rehearsal — the room may "
                                 "already be closed and wiped")
    return dict(row)


@router.post("/profiles/{profile_id}/rehearsal", status_code=201)
def open_rehearsal(profile_id: str, body: RehearsalOpen,
                   request: Request) -> dict:
    """Open a practice room with this profile. What is said inside never
    reaches messages, engagement or the remembrance — a rehearsal that
    counted against the relationship would not be a rehearsal."""
    profile = profile_or_404(profile_id)
    require_may_publish(dict(profile))
    require_owner_or_interactor(profile_id, body.interactor_id, request)
    scenario = (body.scenario or "").strip()
    if not scenario:
        raise HTTPException(
            422, "say what is being rehearsed — an empty scenario gives "
                 "the counterpart nothing to play")
    conn = db.connect()
    rehearsal_id = db.new_id("rhs")
    conn.execute(
        "INSERT INTO rehearsals (id, profile_id, interactor_id, scenario,"
        " created_at) VALUES (?,?,?,?,?)",
        (rehearsal_id, profile_id, body.interactor_id, scenario,
         db.utcnow()))
    conn.commit()
    return {"id": rehearsal_id, "scenario": scenario, "turns_count": 0,
            "remembered": False}


@router.post("/profiles/{profile_id}/rehearsal/{rehearsal_id}/say")
def rehearse(profile_id: str, rehearsal_id: str, body: RehearsalSay,
             request: Request) -> dict:
    """One practice turn. The transcript lives only in the room, only
    until it closes; the reply is marked for what it is."""
    profile = profile_or_404(profile_id)
    # A rehearsal still puts words in the profile's mouth: a departed
    # profile is a memorial and a restricted one is under objection
    # review, and neither speaks — not even in a room that forgets.
    require_may_publish(dict(profile))
    row = _rehearsal_or_404(rehearsal_id, profile_id)
    require_owner_or_interactor(profile_id, row["interactor_id"], request)
    message = (body.message or "").strip()
    if not message:
        raise HTTPException(422, "an empty line rehearses nothing")

    transcript = json.loads(row["transcript"])
    system = (persona.build_system_prompt(dict(profile), None, None)
              + "\n\n" + _REHEARSAL_FRAME + row["scenario"])
    turns = ([{"role": "user" if m["role"] == "interactor" else "assistant",
               "content": m["content"]}
              for m in transcript[-_REHEARSAL_WINDOW:]]
             + [{"role": "user", "content": message}])
    provider = llm.provider_for_profile(profile_id,
                                        cloud=request.app.state.cloud)
    reply = provider.generate(system, turns)

    transcript += [{"role": "interactor", "content": message},
                   {"role": "profile", "content": reply}]
    conn = db.connect()
    conn.execute("UPDATE rehearsals SET transcript=? WHERE id=?",
                 (json.dumps(transcript), rehearsal_id))
    conn.commit()
    return {"id": rehearsal_id, "reply": reply,
            "turns_count": len(transcript) // 2, "remembered": False}


@router.delete("/profiles/{profile_id}/rehearsal/{rehearsal_id}")
def close_rehearsal(profile_id: str, rehearsal_id: str,
                    request: Request) -> dict:
    """Close the room and wipe it. The row and its transcript go
    together; what was practiced stays with the person who practiced."""
    profile_or_404(profile_id)
    row = _rehearsal_or_404(rehearsal_id, profile_id)
    require_owner_or_interactor(profile_id, row["interactor_id"], request)
    turns = len(json.loads(row["transcript"])) // 2
    conn = db.connect()
    conn.execute("DELETE FROM rehearsals WHERE id=?", (rehearsal_id,))
    conn.commit()
    return {"id": rehearsal_id, "turns_count": turns, "erased": True}


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
        "turns_count": r["turns"],
        "last_at": r["last_at"],
    } for r in rows]


@router.get("/profiles/{profile_id}/memory/{interactor_id}")
def view_memory(profile_id: str, interactor_id: str,
                request: Request) -> list[MessageOut]:
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM messages WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at, rowid",
        (profile_id, interactor_id),
    ).fetchall()
    out = [message_out(dict(row)) for row in rows]
    # A rewritten turn says so. One query for the whole transcript rather
    # than one per row — the fact of an edit is part of the record.
    edited = {r["message_id"] for r in conn.execute(
        "SELECT message_id FROM message_edits")} if out else set()
    for m in out:
        m.edited = m.id in edited
    return out


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


@router.get("/profiles/{profile_id}/memory/{interactor_id}/account")
def memory_account(profile_id: str, interactor_id: str,
                   request: Request) -> dict:
    """What do you remember about me — answered from the records, not by
    generation: the distilled paragraph as it actually stands, how many
    turns it was folded from, how many are still in the recent window, and
    when the conversation first and last moved. A trust door tells the
    truth it can prove; the persona's own telling is a chat away.

    The relationship rides here too, and deliberately does not get a route
    of its own. `PUT /profiles/{id}/relationships/{interactor_id}` was the
    only door it had, so the standing was *writable and unreadable*: an
    owner could set how a profile relates to somebody and then had no way
    to ask what it currently was, short of writing again to see what came
    back.

        asked     can the relationship be set
        mattered  can either of you read what it is

    This payload is already the pair's own account of itself, behind the
    same `require_owner_or_interactor` the relationship needs, so folding
    it in costs no new route — and a new route is four doorless rows on
    four clients before it is anything else.
    """
    profile = profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    stats = db.connect().execute(
        "SELECT COUNT(*) AS turns, MIN(created_at) AS first_at,"
        " MAX(created_at) AS last_at FROM messages"
        " WHERE profile_id=? AND interactor_id=? AND status='approved'",
        (profile_id, interactor_id)).fetchone()
    row = remembrance.get(profile_id, interactor_id)
    folded = row["covers"] if row else 0
    rel = get_relationship(profile_id, interactor_id)
    return {
        "profile_name": profile["display_name"],
        "remembers": row["content"] if row else None,
        "folded_turns": folded,
        "recent_turns": max(stats["turns"] - folded, 0),
        "first_at": stats["first_at"],
        "last_at": stats["last_at"],
        # None until somebody sets one — a pair with no declared standing
        # is the ordinary case, not a missing record.
        "relationship": {
            "relationship_type": rel["relationship_type"],
            "nickname": rel["nickname"],
            "tone": rel["tone"],
            "boundaries": json.loads(rel["boundaries"] or "[]"),
        } if rel else None,
    }


@router.get("/profiles/{profile_id}/memory/{interactor_id}/recollections")
def sealed_recollections(profile_id: str, interactor_id: str,
                         request: Request) -> dict:
    """The pair's sealed shelf: every moment the vault remembers of this
    conversation, read back line by line — the recollection index made
    visible to the two people it is of.

        asked     does the profile remember through the vault
        mattered  can the person see what it remembers, and take one back

    The account two doors up answers with the distilled paragraph; this
    answers with the sealed moments themselves — the other axis of memory,
    shown the same way it is held. The *real* vault, not the plan-gated
    one: `storage.vault_for` gates writes only, and a member who moved to
    Free still has a history of sealed moments they must be able to read
    back. A free account's turns were never sealed, so its ledger is
    empty and its shelf honestly so.
    """
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    from .. import recollection
    return recollection.shelf(request.app.state.pdi, profile_id,
                              interactor_id)


@router.delete(
    "/profiles/{profile_id}/memory/{interactor_id}/recollections/{ref}")
def forget_recollection(profile_id: str, interactor_id: str, ref: str,
                        request: Request) -> dict:
    """Take back one sealed moment: the vector, the seal and the ledger
    row go together, so it stops being findable — not merely readable.
    The chat turn it came from is untouched; striking the transcript
    stays at its own door. The ref is scoped to this pair's ledger, so a
    borrowed ref from someone else's conversation forgets nothing. The
    real vault, not the plan-gated one — `storage.vault_for` gates writes
    only, and a plan-gated delete leaves records nobody can reach and
    calls that forgetting."""
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    row = db.connect().execute(
        "SELECT id FROM recollections WHERE id=? AND profile_id=?"
        " AND interactor_id=?", (ref, profile_id, interactor_id)).fetchone()
    if row is None:
        raise HTTPException(404, "no sealed moment here has that ref")
    from .. import recollection
    return recollection.forget(request.app.state.pdi, profile_id,
                               interactor_id, ref)


@router.post("/profiles/{profile_id}/memory/{interactor_id}/forget")
def forget_one_thing(profile_id: str, interactor_id: str, body: MemoryForget,
                     request: Request) -> dict:
    """Forget that one thing — without burning the whole friendship. Every
    turn whose text carries the words is deleted, and the distilled
    remembrance is dropped so it re-folds from what remains, never from
    what was struck. Erase-all stays at its own door; this is the
    scalpel."""
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    about = (body.about or "").strip()
    if not about:
        raise HTTPException(
            422, "say what to forget — empty words strike nothing")
    conn = db.connect()
    hits = [r["id"] for r in conn.execute(
        "SELECT id FROM messages WHERE profile_id=? AND interactor_id=?"
        " AND instr(lower(content), lower(?)) > 0",
        (profile_id, interactor_id, about))]
    row = remembrance.get(profile_id, interactor_id)
    in_remembrance = bool(row and about.lower() in row["content"].lower())
    if not hits and not in_remembrance:
        raise HTTPException(
            404, "nothing remembered here carries those words")
    marks = ",".join("?" for _ in hits)
    sealed_refs = {r["id"] for r in conn.execute(
        f"SELECT id FROM recollections WHERE profile_id=? AND interactor_id=?"
        f" AND id IN ({marks})", (profile_id, interactor_id, *hits))} \
        if hits else set()
    for message_id in hits:
        conn.execute("DELETE FROM messages WHERE id=?", (message_id,))
    if row:
        # The paragraph may hold the thing in other words; re-fold it from
        # the turns that survive rather than trying to edit a memory.
        conn.execute(
            "DELETE FROM remembrances WHERE profile_id=? AND interactor_id=?",
            (profile_id, interactor_id))
    conn.commit()
    # The struck turns' sealed memories go with them: a moment somebody
    # forgot must stop being findable, not merely stop being readable.
    # Non-fatal — the strike stands even when the tandem is down, and the
    # count says what the vault actually let go of.
    from .. import recollection
    sealed = sum(
        1 for message_id in sealed_refs
        if recollection.forget(request.app.state.pdi, profile_id,
                               interactor_id, message_id)["forgotten"])
    return {"forgotten_turns": len(hits), "remembrance_reset": bool(row),
            "sealed_forgotten": sealed}


@router.post("/profiles/{profile_id}/memory/{interactor_id}/strike")
def strike_turns(profile_id: str, interactor_id: str, body: MemoryStrike,
                 request: Request) -> dict:
    """Strike the turns you selected — the checkboxes next to the scalpel.

    Named-forget strikes by words; this strikes by hand, for the field
    report that asked for "little clear boxes you could select and a
    delete button". The ids are scoped to this pair's memory, so a
    borrowed id from someone else's conversation strikes nothing, and the
    distilled remembrance re-folds from the turns that remain — never
    from what was struck. Erase-all keeps its own door."""
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    ids = [i.strip() for i in body.message_ids if i.strip()]
    if not ids:
        raise HTTPException(
            422, "select at least one turn — nothing was struck")
    conn = db.connect()
    marks = ",".join("?" for _ in ids)
    hits = [r["id"] for r in conn.execute(
        f"SELECT id FROM messages WHERE profile_id=? AND interactor_id=?"
        f" AND id IN ({marks})", (profile_id, interactor_id, *ids))]
    if not hits:
        raise HTTPException(404, "none of those turns are in this memory")
    sealed_refs = {r["id"] for r in conn.execute(
        f"SELECT id FROM recollections WHERE profile_id=? AND interactor_id=?"
        f" AND id IN ({marks})", (profile_id, interactor_id, *ids))}
    for message_id in hits:
        conn.execute("DELETE FROM message_edits WHERE message_id=?",
                     (message_id,))
        conn.execute("DELETE FROM messages WHERE id=?", (message_id,))
    row = remembrance.get(profile_id, interactor_id)
    if row:
        conn.execute(
            "DELETE FROM remembrances WHERE profile_id=? AND interactor_id=?",
            (profile_id, interactor_id))
    conn.commit()
    # A struck turn's sealed memory goes with it — the vector, the seal
    # and the ledger row — so it stops being findable, not merely stops
    # being readable. Only refs the ledger actually holds are counted:
    # profile turns are never sealed, and a strike of one forgets nothing.
    from .. import recollection
    sealed = sum(
        1 for message_id in sealed_refs
        if recollection.forget(request.app.state.pdi, profile_id,
                               interactor_id, message_id)["forgotten"])
    return {"struck_turns": len(hits), "remembrance_reset": bool(row),
            "sealed_forgotten": sealed}


@router.put("/profiles/{profile_id}/memory/{interactor_id}/turns/{message_id}")
def edit_turn(profile_id: str, interactor_id: str, message_id: str,
              body: TurnEdit, request: Request) -> dict:
    """Rewrite one remembered turn, in place, and keep the record honest.

    Three ways it stays honest: the new words face the review every other
    sentence in this room faces; a profile turn's synthetic-media
    credential is dropped, because a hash-of-content credential must not
    vouch for words a person rewrote; and the edit is recorded as a fact
    — that it happened, never what it said before, since the point of an
    edit may be removal. The remembrance re-folds from the record as it
    now stands."""
    profile = profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM messages WHERE id=? AND profile_id=?"
        " AND interactor_id=?",
        (message_id, profile_id, interactor_id)).fetchone()
    if row is None:
        raise HTTPException(404, "no remembered turn has that id")
    content = (body.content or "").strip()
    if not content:
        raise HTTPException(
            422, "say what the turn should say — to remove it, strike it "
                 "instead")
    verdict = moderation.review(content, None, {"birthdate": None},
                                maturity=profile["maturity"])
    if not verdict.approved:
        raise HTTPException(422, "those words cannot stand in this record")
    conn.execute(
        "UPDATE messages SET content=?, watermark_id=NULL WHERE id=?",
        (content, message_id))
    conn.execute(
        "INSERT INTO message_edits (message_id, edits, edited_at)"
        " VALUES (?,1,?) ON CONFLICT(message_id) DO UPDATE SET"
        " edits = edits + 1, edited_at = excluded.edited_at",
        (message_id, db.utcnow()))
    had_remembrance = remembrance.get(profile_id, interactor_id) is not None
    if had_remembrance:
        conn.execute(
            "DELETE FROM remembrances WHERE profile_id=? AND interactor_id=?",
            (profile_id, interactor_id))
    conn.commit()
    # The sealed memory of an interactor turn is re-made from the words as
    # they now stand: the old seal and vector go first (the real vault — a
    # delete), then the rewrite is sealed and embedded again (the
    # plan-gated vault — a write). On a plan without a vault the memory
    # simply ends, because old words that stayed findable would betray the
    # edit. Non-fatal like every memory step; the return says what stood.
    resealed = False
    ledgered = conn.execute(
        "SELECT id FROM recollections WHERE id=? AND profile_id=?"
        " AND interactor_id=?",
        (message_id, profile_id, interactor_id)).fetchone() is not None
    if row["role"] == "interactor" and ledgered:
        from .. import recollection, storage as storage_mod, tiers as tiers_mod
        gone = recollection.forget(request.app.state.pdi, profile_id,
                                   interactor_id, message_id)
        if gone["forgotten"]:
            # The person's plan, like every other keeping of a
            # conversation: a reseal is a write, and it must land in the
            # same account and under the same arrangement the original did,
            # or an edit quietly moves somebody's memory somewhere else.
            vault, posture = storage_mod.memory_for(
                tiers_mod.plan_of_interactor(interactor_id),
                request.app.state.pdi)
            resealed = bool(posture) and recollection.remember(
                vault or request.app.state.pdi, profile_id, interactor_id,
                message_id, content, posture=posture)["remembered"]
    turn = message_out(dict(conn.execute(
        "SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()))
    turn.edited = True
    return {"turn": turn, "remembrance_reset": had_remembrance,
            "memory_resealed": resealed}


@router.delete("/profiles/{profile_id}/memory/{interactor_id}", status_code=204)
def clear_memory(profile_id: str, interactor_id: str,
                 request: Request) -> None:
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    # The pair's sealed memories go with the transcript — vectors, seals
    # and ledger rows in one sweep. Non-fatal: the local clearing stands
    # even when the tandem is down, and rows whose seals the vault never
    # let go of stay on the shelf rather than being orphaned.
    from .. import recollection
    recollection.forget_pair(request.app.state.pdi, profile_id,
                             interactor_id)
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
        raise HTTPException(422, i18n.raised(exc))


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
        raise HTTPException(403 if "consent" in i18n.raised(exc) else 422, i18n.raised(exc))


@router.post("/profiles/{profile_id}/voiceprint", status_code=201)
def build_voiceprint(profile_id: str, request: Request) -> dict:
    """Step 812: mint the print, once enough of the person is in it."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return voiceprint.build(profile_id)
    except voiceprint.VoiceError as exc:
        raise HTTPException(422, i18n.raised(exc))


@router.post("/profiles/{profile_id}/voiceprint/speak")
def speak_in_voice(profile_id: str, body: VoiceSay, request: Request) -> dict:
    """Say something in the enrolled voice — never without the watermark
    credential and the spoken disclosure riding along."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return voiceprint.speak(profile_id, body.text)
    except voiceprint.VoiceError as exc:
        raise HTTPException(422, i18n.raised(exc))


# -- The spoken voice: a bound engine reference (qrme/spoken.py) -------------

@router.get("/profiles/{profile_id}/voice")
def profile_voice(profile_id: str) -> dict:
    """Which voice this profile speaks with. Public read, like the avatar:
    a voice a stranger can hear is a voice a stranger should be able to
    check the provenance of."""
    profile_or_404(profile_id)
    from .. import spoken
    return spoken.bound(profile_id)


@router.get("/voices")
def voice_library(request: Request) -> dict:
    """The voices a profile can be pointed at.

    Binding was an opaque id typed by hand — true to how the provider
    works, and not something a person building a profile can do without
    already knowing the id. This is the list that makes the binding door
    usable.

    No authentication: these are the voices this deployment offers to
    everybody who builds here, the same shape the avatar catalogue is
    public in. Nothing here is anybody's private property — the key stays
    on the server and no credential rides the answer.
    """
    from .. import spoken
    voices, reached = spoken.library_with_reach()
    # `library_reached` and its sentence: the fallback used to be silent,
    # and the silence cost a field afternoon — an owner whose key had died
    # saw only the built-in characters, their cloned voice gone from the
    # list with nothing anywhere saying why.
    return {"voices": voices, "library_reached": reached,
            "note": None if reached else i18n.tr_public(
                "The voice provider could not be reached, so these are the "
                "built-in voices \u2014 cloned voices come back when it "
                "answers.", i18n.refusal_language(request))}


@router.put("/profiles/{profile_id}/voice")
def bind_profile_voice(profile_id: str, body: VoiceBind,
                       request: Request) -> dict:
    """The owner points the profile at a voice made on the provider's own
    surface. An empty voice_id unbinds."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    from .. import spoken
    try:
        return spoken.bind(profile_id, body.provider, body.voice_id,
                           body.label)
    except spoken.SpokenError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.post("/profiles/{profile_id}/voice/release")
def release_profile_voice(profile_id: str, request: Request) -> dict:
    """The owner lets everybody on this deployment use this profile's bound
    voice. A recorded waiver, not a setting: who released it and when stays
    on the row, and taking it back keeps the history."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    from .. import spoken
    try:
        return spoken.release(profile_id)
    except spoken.SpokenError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.delete("/profiles/{profile_id}/voice/release")
def reclaim_profile_voice(profile_id: str, request: Request) -> dict:
    """The owner takes the voice back. Only the account that released it
    may, and every other account's binding of it goes with the waiver."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    from .. import spoken
    try:
        return spoken.reclaim(profile_id)
    except spoken.SpokenError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.post("/profiles/{profile_id}/voice/say")
def say_in_profile_voice(profile_id: str, body: VoiceSay,
                         request: Request) -> Response:
    """One utterance in the bound voice, as audio.

    Any signed-in principal: the text is the caller's to have already — a
    room turn they can read, a page they are looking at — so the audio adds
    no information, only a bill, and the ceiling in `spoken.say` bounds that.
    The stamp's credential id rides in a header so the audio stays audio.
    """
    profile_or_404(profile_id)
    if auth.principal(request) is None:
        raise HTTPException(401, "sign in to hear a profile speak")
    from .. import spoken
    try:
        audio, about = spoken.say(profile_id, body.text)
    except spoken.SpokenError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None
    return Response(content=audio, media_type=about["mime"],
                    headers={"x-watermark-id": about["watermark_id"]})


@router.delete("/profiles/{profile_id}/voiceprint")
def revoke_voiceprint(profile_id: str, request: Request) -> dict:
    """Withdraw: the samples are deleted, the print retires, and the record
    of the withdrawal stays."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return voiceprint.revoke(profile_id)


@router.post("/interactors/{interactor_id}/heard")
async def heard(interactor_id: str, request: Request) -> dict:
    """Recorded speech in, words out. The audio is not stored.

    The room has had this door since 1.4.2, scoped to a room, because an
    iPhone's own recogniser exists and always refuses. This is the same door
    without the room, and it exists for a different failure: a conversation
    somebody took with them.

        asked     can this browser hear you
        mattered  can it still hear you once the window is minimised

    The browser's recogniser is ended when a page is put away — that is the
    documented behaviour and `away.ts` was written about it. `getUserMedia`
    is not: an open capture keeps recording while the window is minimised,
    and the browser shows its own recording indicator throughout. So a page
    that wants to carry a conversation out of itself records and posts the
    bytes here rather than listening, and this is where they land.

    Deliberately **only** the hearing, exactly as the room's door is. What
    comes back is said through whichever conversation the caller is in —
    a profile's chat, the agent's turn — so moderation, the watermark and
    the speaking rules stay in the one place that owns them. A route that
    heard and answered in one breath would be a second door into every
    conversation with its own copy of those rules to drift out of step.

    Gated on the interactor's own token, like the room's. Somebody else's
    id is not a way to spend this deployment's transcription.

    A deployment with no ears answers 503 with the reason rather than an
    empty string. Silence would read as *it didn't hear me* to somebody who
    has just spoken into their phone, and the true answer — that this
    deployment has nowhere to send audio — is one an owner can act on and a
    guest cannot guess.
    """
    require_interactor(interactor_id, request)
    data = await request.body()
    if not data:
        raise HTTPException(422, "no audio")
    words = scrape.transcribe_bytes(data, interactor_id)
    if words is None:
        raise HTTPException(
            503, "this deployment has no transcription service, so recorded "
                 "speech cannot be turned into words — set QRME_EARS_URL, or "
                 "type instead")
    return {"text": words["text"]}
