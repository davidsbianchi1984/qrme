"""Shared request helpers used across the API routers."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, Request

from . import auth, db, persona
from .models import MessageOut, ProfileOut


def age_of(birthdate: date) -> int:
    today = datetime.now().date()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )


# `refusals_in` stood here for five releases: a context manager the four
# accountless routes wrapped themselves in, translating whatever refused
# inside. Its docstring said why the owner routes were left out —
#
#     `profile_or_404` and its siblings are shared with every owner route and
#     say "profile not found" in English, which is right there — the owner
#     picked that language
#
# — and the owner had not picked that language. They had picked one; it was in
# `language_prefs`; the persona had been speaking it for eleven releases.
#
#     asked     did the caller state a language
#     mattered  did the profile
#
# `create_app`'s exception handler now translates every refusal in the product
# for whoever is reading it, so this helper's whole job is done in one place
# that no route has to opt into. Keeping it as well would have left two paths
# translating one sentence, free to drift, with nothing to say which reader got
# which — the same argument `i18n.tr_refusal` makes for consulting one table
# rather than two.


def profile_or_404(profile_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "profile not found")
    return dict(row)


def require_owner(profile_id: str, request: Request) -> None:
    """Gate an owner-control endpoint: the caller must hold the profile's
    owner token."""
    auth.require(request, "owner", profile_id)


def require_interactor(interactor_id: str, request: Request) -> None:
    """Gate a per-interactor private endpoint: the caller must hold that
    interactor's token."""
    auth.require(request, "interactor", interactor_id)


#: A profile that has departed or been terminated produces no new words at
#: all. Kept as one map rather than a chain of `if`s at each site, because the
#: whole finding was that each site decided separately and most did not decide.
_SILENT = {
    "departed": "this profile has departed; its memory remains viewable",
    "terminated": "this profile has been terminated",
}

#: A contested profile does not publish while the objection is open. Distinct
#: from the sentence `chat` raises — that one is about *new interactors*, and
#: it is right for a conversation and wrong for a public post. Answering the
#: narrower question is how the wider one went unasked.
RESTRICTED_WHILE_CONTESTED = (
    "this profile is restricted pending an objection review; it is not "
    "publishing new work while the objection is open")


def require_may_speak(profile: dict) -> None:
    """The profile is not departed and not terminated.

    `chat` had these two branches inline and correct; nothing else had them at
    all. They live here now so the two cannot drift apart, and so a route that
    forgets is a route that never called this.
    """
    said = _SILENT.get(profile.get("status"))
    if said:
        raise HTTPException(410, said)


def require_may_publish(profile: dict) -> None:
    """The profile may produce new content for somebody else to read.

    `require_may_speak`, plus the contested case.

    ## The finding this exists for

    Nine routes make a profile produce new words. Two checked its status:
    `chat` and `proactive_checkin` — the two whose subject is the person on the
    *other* side. `compose`, which writes a public post and publishes it, did
    not. So a profile that had **departed** — a memorial, "frozen rather than
    orphaned" in succession's own words — went on writing and publishing, and a
    profile **restricted pending an objection review** went on publishing in
    the voice of the person contesting it, throughout the review.

        asked     can somebody still talk to a departed profile
        mattered  can a departed profile still be made to speak

    `chat` answered 410 for the dead while `compose` answered 201. Nobody could
    talk to them; they could still talk to everybody.
    """
    require_may_speak(profile)
    if profile.get("status") == "restricted":
        raise HTTPException(403, RESTRICTED_WHILE_CONTESTED)


def require_owner_or_interactor(profile_id: str, interactor_id: str,
                                request: Request) -> None:
    """Gate a shared per-interactor surface (a conversation's memory): either
    the profile's owner or that interactor may access it."""
    who = auth.principal(request)
    if who == {"role": "owner", "subject_id": profile_id}:
        return
    if who == {"role": "interactor", "subject_id": interactor_id}:
        return
    if who is None:
        raise HTTPException(401, "authentication required")
    raise HTTPException(403, "not authorized for this resource")


def require_self(subject_id: str, request: Request) -> None:
    """The caller must **be** this party, whatever kind of subject they are.

    The two-party surfaces — an agreed exchange, a lent skill, a watch party —
    identify who is acting by an id in the request body, and an id in a body is
    a claim rather than a fact. Without this, `{"actor_id": "<somebody else>"}`
    is a complete impersonation: an anonymous caller could forge *both*
    signatures on an agreement, open its channel, and accept delivery of an
    executable on the victim's behalf. Every consent property those modules
    describe rests on this check existing.

    Deliberately not `auth.require`, which also pins the role: a party here may
    be a profile owner or an interactor, and which of the two they are is not
    what is being asserted. What is being asserted is that the token belongs to
    the person the body names.
    """
    who = auth.principal(request)
    if who is None:
        raise HTTPException(
            401, "authentication required — this acts on somebody's behalf, "
                 "so it has to know it is them")
    if who["subject_id"] != subject_id:
        raise HTTPException(
            403, "that is not you — an id in a request body is a claim, and "
                 "this one does not match the token presented")


def require_one_of(subject_ids: list[str], request: Request) -> str:
    """The caller must be one of these parties. Returns which one they are.

    For the endpoints where either side may act — reopening an agreement,
    closing a grant — and where the answer is also needed, so the handler does
    not have to ask twice.
    """
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["subject_id"] not in subject_ids:
        raise HTTPException(
            403, "only the people involved in this can act on it")
    return who["subject_id"]


def interactor_or_404(interactor_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM interactors WHERE id=?", (interactor_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "interactor not found")
    return dict(row)


def get_active_handoff(profile_id: str, interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM active_handoffs WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id)).fetchone()
    return dict(row) if row else None


def set_active_handoff(profile_id: str, interactor_id: str, domain: str,
                       specialist_profile_id: str) -> None:
    conn = db.connect()
    conn.execute(
        "INSERT INTO active_handoffs (profile_id, interactor_id, domain,"
        " specialist_profile_id, since) VALUES (?,?,?,?,?)"
        " ON CONFLICT (profile_id, interactor_id) DO UPDATE SET"
        " domain=excluded.domain,"
        " specialist_profile_id=excluded.specialist_profile_id,"
        " since=excluded.since",
        (profile_id, interactor_id, domain, specialist_profile_id, db.utcnow()),
    )
    conn.commit()


def clear_active_handoff(profile_id: str, interactor_id: str) -> None:
    conn = db.connect()
    conn.execute(
        "DELETE FROM active_handoffs WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id))
    conn.commit()


def _in_quiet_hours(interactor: dict, now: datetime) -> bool:
    """Whether the recipient's quiet-hours window covers the current UTC hour.
    A window that wraps midnight (start > end) is handled."""
    start, end = interactor.get("quiet_start"), interactor.get("quiet_end")
    if start is None or end is None:
        return False
    hour = now.hour
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end        # overnight window


def proactive_gate(profile: dict, interactor: dict) -> str | None:
    """Anti-spam gate for unprompted outreach. Returns a rejection reason, or
    None when outreach is allowed. Three rules (see lifecycle-and-consent.md):
    a per-relationship rate cap, the recipient's quiet hours, and suppression
    until the recipient has replied at least once."""
    now = datetime.now(timezone.utc)
    if _in_quiet_hours(interactor, now):
        return "the recipient's quiet hours are in effect"
    row = db.connect().execute(
        "SELECT last_outreach_at, awaiting_reply FROM proactive_state"
        " WHERE profile_id=? AND interactor_id=?",
        (profile["id"], interactor["id"])).fetchone()
    if row is None:
        return None
    if row["awaiting_reply"]:
        return "awaiting a reply since the last outreach — not sending again"
    if row["last_outreach_at"]:
        # The door's own pace binds alongside the owner's cap — the
        # looser of the two, made binding on both (qrme/opendoor.py): a
        # weekly door slows a daily profile; nothing speeds one up.
        from . import opendoor
        hours = max(profile["proactive_min_interval_hours"],
                    opendoor.cadence_hours(interactor["id"], profile["id"]))
        interval = timedelta(hours=hours)
        last = datetime.fromisoformat(row["last_outreach_at"])
        if now - last < interval:
            return (f"rate cap: at most one unprompted outreach per "
                    f"{hours}h")
    return None


def record_proactive_outreach(profile_id: str, interactor_id: str) -> None:
    conn = db.connect()
    conn.execute(
        "INSERT INTO proactive_state (profile_id, interactor_id,"
        " last_outreach_at, awaiting_reply) VALUES (?,?,?,1)"
        " ON CONFLICT (profile_id, interactor_id) DO UPDATE SET"
        " last_outreach_at=excluded.last_outreach_at, awaiting_reply=1",
        (profile_id, interactor_id, db.utcnow()))
    conn.commit()


def clear_awaiting_reply(profile_id: str, interactor_id: str) -> None:
    """The recipient replied — lift the suppression so future outreach may
    resume (subject to the rate cap)."""
    conn = db.connect()
    conn.execute(
        "UPDATE proactive_state SET awaiting_reply=0"
        " WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id))
    conn.commit()


def anonymized_exchange(profile: dict, profile_id: str,
                        interactor_id: str) -> list[dict] | None:
    """The last approved exchange with all identifying strings stripped —
    ids never included; the persona's display name replaced throughout. This is
    exactly (and only) what a cloud contribution contains."""
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


def relationship(profile_id: str, interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM relationships WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id),
    ).fetchone()
    return dict(row) if row else None


def profile_out(row: dict, request: Request | None = None, *,
                owner: bool = False) -> ProfileOut:
    """One profile, redacted for whoever is asking.

    `GET /profiles/{id}` is public, and for a long time this function handed
    every caller the raw row — including `display_name` and `owner_id` on a
    profile flagged `anonymous`. The flag was real everywhere it was
    *rendered*: the front-page card, the landing page, the prompt and the
    watermark all substituted "anonymous persona". The route that returns the
    profile itself did not, so anonymity was a property of four presentation
    surfaces rather than of the profile, and the shortest way past it was to
    ask for the profile.

    `owner_id` is the worse of the two, because it does not just undo one
    profile's anonymity — it undoes all of them at once. Two anonymous
    profiles sharing an owner are the same person, and anybody could read that
    field off both and match them. The same field on a *named* profile then
    names the anonymous ones beside it. Withheld from everyone but the owner
    for that reason, along with `successor_owner`, which is somebody else's
    account id and was never a visitor's business either.

    The owner still sees their own profile whole: they are the one person for
    whom none of this is a disclosure.

    ``owner=True`` says so directly, for the one case a token cannot: the
    response to profile *creation*, which carries the owner token it is being
    authorized by. The incoming request there holds the signup key, so asking
    it who is calling would redact the creator's own new profile from them.
    """
    from . import auth, exchange, identity

    who = auth.principal(request) if request is not None else None
    is_owner = owner or who == {"role": "owner", "subject_id": row["id"]}
    hidden = bool(row["anonymous"]) and not is_owner

    return ProfileOut(
        id=row["id"],
        owner_id=row["owner_id"] if is_owner else None,
        kind=row["kind"],
        display_name=(identity.anonymous_name(row["id"]) if hidden
                      else row["display_name"]),
        persona=row["persona"],
        # Not redacted with the name. A trade is not an identifier — the
        # anonymous emblems are chosen BY field, so the platform already
        # shows an anonymous profile's line of work on its picture.
        industry=row["industry"],
        job_title=row["job_title"],
        # Same posture as the trade above: who somebody works with is
        # part of what they are, not an identifier, so it travels with
        # the job title rather than being redacted with the name.
        # `.get` with a default, like `guest_styling` below: these
        # columns postdate several creation paths that build a dict by
        # hand and never learned about them.
        works_with=json.loads(
            (row.get("works_with") if hasattr(row, "get")
             else row["works_with"]) or "[]"),
        trade_family=(row.get("trade_family") if hasattr(row, "get")
                      else row["trade_family"]),
        trade_domain=exchange.industry_for(
            row.get("trade_family") if hasattr(row, "get")
            else row["trade_family"]),
        demographics=json.loads(row["demographics"]),
        sources=json.loads(row["sources"]),
        anonymous=bool(row["anonymous"]),
        adult_mode=bool(row["adult_mode"]),
        interaction_scope=row["interaction_scope"],
        moderation_mode=row["moderation_mode"],
        aging_enabled=bool(row["aging_enabled"]),
        base_age=row["base_age"],
        effective_age=persona.effective_age(row),
        successor_owner=row["successor_owner"] if is_owner else None,
        purpose=row["purpose"],
        maturity=row["maturity"],
        cloud_contribution=bool(row["cloud_contribution"]),
        # `.get` with the schema's own default: rows arrive here both as
        # sqlite rows (always carrying the column) and as dicts built in
        # creation paths that predate the wardrobe switch.
        guest_styling=bool(row.get("guest_styling", 1)
                           if hasattr(row, "get") else row["guest_styling"]),
        status=row["status"],
        licensed_from=row["licensed_from"],
        created_at=row["created_at"],
    )


def message_out(row: dict) -> MessageOut:
    from . import watermark
    # Unapproved profile content is never shown to interactors (PRD 6.5).
    visible = row["status"] == "approved" or row["role"] == "interactor"
    keys = row.keys() if hasattr(row, "keys") else row
    return MessageOut(
        id=row["id"],
        role=row["role"],
        content=row["content"] if visible else None,
        status=row["status"],
        flag_reason=row["flag_reason"],
        created_at=row["created_at"],
        # Every rendered profile turn carries its mark (AI-designated,
        # owner-designable) alongside the verifiable credential.
        watermark=(watermark.brief(row["watermark_id"])
                   if visible and "watermark_id" in keys else None),
        # What the turn handed over, if it handed anything over. Hidden
        # with the words when a turn is not visible: a document made by an
        # unapproved turn is that turn, in a file.
        document=(_document_brief(row["media_id"])
                  if visible and "media_id" in keys and row["media_id"]
                  else None),
    )


def _document_brief(media_id: str) -> dict | None:
    """The card a composed document renders as — never its whole body.

    A chat turn's answer carries the handle, not the file. The body can be
    a hundred thousand characters and the transcript is polled; putting it
    in the turn would send the document again on every poll.
    """
    from . import media as media_mod

    row = db.connect().execute(
        "SELECT * FROM media WHERE id=?", (media_id,)).fetchone()
    return media_mod.row_facade(row) if row is not None else None


def source_items(profile_id: str, pdi=None) -> list[dict]:
    """Source items with content resolved from the PDI vault if sealed.

    A sealed item whose readback fails resolves to ``content: None`` — the
    profile simply cannot recall that item this turn. The alternative was
    the field report: one erroring vault record inside the chat route, and
    every conversation with the profile answered 500 from the moment its
    first page was fetched and sealed.
    """
    rows = db.connect().execute(
        "SELECT * FROM source_items WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC", (profile_id,),
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        if item["pdi_key"] and pdi is not None:
            try:
                raw = pdi.get(item["pdi_key"])
                item["content"] = json.loads(raw)["content"] if raw else None
            except Exception:                              # noqa: BLE001
                item["content"] = None
        out.append(item)
    return out


def biometric_domain(biometrics: dict) -> str | None:
    """Claim 24: map monitoring signals to the specialist domain they call for."""
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


def biometrics_recovered(biometrics: dict | None) -> bool:
    """Whether a fresh biometric reading indicates the episode has passed —
    the signal to hand a conversation back from a specialist to the primary
    profile. Recovery requires *positive* evidence: a reading that carries no
    concerning domain and a low stress level. Absent biometrics are not
    recovery (the specialist stays engaged until monitoring says otherwise)."""
    if not biometrics:
        return False
    if biometric_domain(biometrics) is not None:
        return False
    try:
        return float(biometrics.get("stress_level") or 0) < 0.4
    except (TypeError, ValueError):
        return False


def _who_generated(profile_id: str) -> dict:
    """The `generated_by` half of a provenance record, and the degrade beside
    it when the model that answered is not the one that was asked.

    Two keys rather than one, because they answer different questions and a
    reader needs both: `generated_by` is the honest origin of the text, and
    `degraded_from` is what the owner had configured — without it, a record
    that suddenly says "local fallback" looks like a settings change rather
    than an outage or a dead credential.
    """
    from . import llm
    answered = llm.answered_by()
    if answered is None:
        return {"generated_by": llm.resolve_choice(llm.get_choice(profile_id)),
                "degraded_from": None}
    actual, asked = answered
    return {"generated_by": actual, "degraded_from": asked if asked != actual
            else None}


def content_provenance(profile: dict, sources: list[dict],
                       status: str, flag_reason: str | None) -> dict:
    """The verifiable basis of a piece of persona-generated content: which
    model produced it, what it was grounded in (the profile's core identity
    plus its consented source material), any licensed lineage, and the
    moderation verdict it passed through — so nothing the platform emits is
    a black box."""
    from . import i18n, llm
    kinds: dict[str, int] = {}
    for item in sources:
        kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1
    return {
        "method": "generated in persona — grounded in the profile's core "
                  "identity and its consented source material, then "
                  "moderated before delivery",
        # Who actually wrote it, not who was asked to.
        #
        # This read `resolve_choice(get_choice(...))` — the profile's stored
        # preference — while `llm.FallbackProvider` and `cloud.CloudProvider`
        # both degrade to the local stub whenever the network provider fails.
        # An owner whose own API key had expired therefore got stub-written
        # text stamped with the model they had chosen, watermarked, and
        # published, and the only trace was a log line addressed to nobody.
        #
        #     asked     which model was this profile set to
        #     mattered  which model actually wrote this
        #
        # `answered_by()` is None when nothing on this request went through a
        # degrading wrapper, and the stored choice is then the honest answer —
        # it is what `_build` resolved and what actually ran.
        **_who_generated(profile["id"]),
        "language": i18n.effective_language(profile["id"]),
        "grounded_in": {"persona": True, "source_items": len(sources),
                        "by_kind": kinds},
        "licensed_from": profile.get("licensed_from"),
        "moderation": {"maturity": profile["maturity"], "status": status,
                       "flag_reason": flag_reason},
        "disclaimer": "Synthetic-persona content. The grounding and lineage "
                      "above are the derivation trail — this is a character "
                      "speaking, not a verified factual source.",
    }

#: Tables a profile erase must **not** clear, and why.
#:
#: Empty on purpose. A row here is a promise broken deliberately, so it needs
#: a sentence beside it naming whose promise and why — the sibling vault keeps
#: its hash-chained audit log for exactly that reason and nothing here has the
#: same standing.
#: Tables that are not the profile's — walked past by BOTH the erasure
#: sweep and the owner's export, because those are the same question asked
#: twice: *is this the profile's to take, and is it the profile's to be
#: handed?*
#:
#: One entry, and it is a decision rather than an oversight. `recollections`
#: holds what a **person** said — only their own turns are ever sealed, never
#: the profile's replies — and since 1.2.0 those live in their vault, under
#: their key, gated on their plan. Deleting a profile must not reach into
#: somebody else's account and take their record of a conversation they had.
#:
#: David, ruling on it directly: *the user's record survives, profile erasure
#: redacts its own words.* Both halves are here. The redaction needs no pass
#: of its own — none of the profile's words are in this table — and what IS
#: the profile's goes with the sweep: its replies in `messages`, its distilled
#: view of the conversation in `remembrances`, its persona, its sources.
#:
#:     asked     did we delete every trace of the profile
#:     mattered  did we delete somebody else's record while we were in there
#:
#: The erasure right is not weakened by this. It is a right over the
#: profile's own words, and it still takes every one of them.
#:
#: The export side was found by the guard that holds those two in step
#: (`test_the_export_and_the_erase_reach_the_same_tables`), and it was the
#: sharper of the two: a profile's owner downloading their bundle was being
#: handed every interactor's memories — other people's words, in a file that
#: gets mailed and copied. Exempting one side and not the other would have
#: left that standing.
ERASE_KEEPS: frozenset[str] = frozenset({"recollections"})


def profile_scoped_tables() -> list[str]:
    """Every table in this schema with a `profile_id` column.

    Read from the schema rather than written down. The list this replaced
    named twenty-four tables while the schema had grown to sixty-six, so a
    delete advertised as *the profile and every trace of it* left forty-two
    tables standing — among them `clinical_notes`, `media` and
    `media_watermarks`, `anonymous_pictures`, `homepages` and `friendships`.

    A migration that adds a table is covered by writing it, not by remembering
    the delete handler.
    """
    conn = db.connect()
    found = []
    for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'").fetchall():
        name = row[0]
        columns = {c[1] for c in conn.execute(f"PRAGMA table_info({name})")}
        if "profile_id" in columns:
            found.append(name)
    return sorted(found)

#: What an export must never hand back, matched as **marks inside a column
#: name** rather than as a list of exact names.
#:
#: The first cut of this was a list, and the guard next door caught it on its
#: first run: `owner_token`, `qrme_interactor_token` and a third all sat in
#: tables the export now reaches and none of them were in the list. A list of
#: credential columns goes stale exactly the way the erase cascade's list of
#: tables did, and for the same reason — somebody adds a column.
#:
#: Deliberately not the bare word `hash`: an audit chain's hash is a record,
#: not a credential, and a person auditing their own export should be able to
#: verify it.
EXPORT_REDACTS = ("token", "secret", "password", "api_key", "private_key",
                  "grant_hash", "check_value", "credential")


def _public(row) -> dict:
    """A row with every credential-bearing column dropped."""
    return {k: v for k, v in dict(row).items()
            if not any(mark in k.lower() for mark in EXPORT_REDACTS)}


def export_rows(profile_id: str) -> dict[str, list[dict]]:
    """Every row in this schema that names this profile, by table.

    Derived from the schema for the same reason the erase cascade is: the
    handler this replaced named six tables — `relationships`, `messages`,
    `engagement`, `posts`, `surfaces` and the profile itself — under a
    docstring reading *full data export — access everything, anytime (You Own
    It)*, and a README row promising the same. Sixty-six tables carry a
    `profile_id`.

    Redaction is per column, not per table: a row is the person's history and
    a token inside it is a live credential in whatever they do with the file.
    """
    conn = db.connect()
    out: dict[str, list[dict]] = {}
    for table in profile_scoped_tables():
        if table in ERASE_KEEPS:
            continue          # not the profile's to be handed — see above
        rows = conn.execute(f"SELECT * FROM {table} WHERE profile_id=?",
                            (profile_id,)).fetchall()
        if not rows:
            continue
        out[table] = [_public(r) for r in rows]
    return out


# --------------------------------------------------------------------------- #
# Cutting text without cutting a word in half
# --------------------------------------------------------------------------- #

#: The boundaries to prefer when text has to be shortened, largest first.
#: The same ladder `wall.parts` walks, and for the same finding: a cut inside
#: a word is what got reported, and a cut inside a sentence is merely unlovely.
_CLIP_BREAKS = ("\n\n", "\n", ". ", " ")


def clipped(text: str, cap: int) -> tuple[str, bool]:
    """`(text, was_cut)` — shortened at a boundary, never inside a word.

    `wall.parts` learned this for posts somebody writes. Everything that
    assembles a PROMPT went on slicing with a bare `[:n]`, which is the same
    defect facing the model instead of a reader — and worse there, because a
    reader sees a word end mid-air and distrusts it while a model reads on.

        asked     does the text fit
        mattered  what does the part that fits say

    A clinician's note cut at 400 characters can land inside *no history of*
    and hand a profile the opposite of what was written. That is the reason
    this refuses a mid-word cut rather than tidying one up afterwards.

    The flag is the other half. Something has to SAY it was shortened, and
    only the caller knows how to word that for where it is going — a source
    item and a clinician's letter want different sentences.
    """
    text = (text or "").strip()
    if len(text) <= cap:
        return text, False
    window = text[:cap]
    # Two passes. The first prefers a boundary in the second half, so what
    # comes back is not a stub. The second accepts a boundary ANYWHERE,
    # because a short honest clip beats a broken word — this is a clip, not
    # a split into parts, and nothing downstream needs the piece to be a
    # certain size. Written as two passes after a sweep across every cap
    # caught the single-pass version cutting "The patien" out of "The
    # patient": with no space past the halfway mark it fell straight through
    # to the raw cut, so the guarantee this function is named for was false
    # exactly where the text was shortest.
    for floor in (cap // 2, -1):
        for mark in _CLIP_BREAKS:
            cut = window.rfind(mark)
            if cut > floor:
                return window[:cut].rstrip(), True
    # One unbroken run longer than the cap — a URL, a chemical name, an
    # identifier. Cutting at the ceiling is the only option left, and the
    # caller's marker is what keeps it honest.
    return window.rstrip(), True
