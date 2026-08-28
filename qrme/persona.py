"""Builds the profile-conditioned system prompt.

This is where the PRD's core differentiators meet the model: the prompt is
assembled from (1) the profile's fixed identity, (2) the relationship between
the represented person and this specific interactor, (3) the engagement
signal accumulated for that interactor, and (4) the profile's aging config.
Identity and boundaries are stated as non-negotiable so engagement adaptation
cannot erode them (PRD 6.3).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from . import common

# Surfaces / embodiments a profile can inhabit — its identity is invariant
# across all of them.
_EMBODIMENT_FORMS = "text, voice, feed, AR/VR, a speaker, a hologram, or a robot"

# How much of a piece of material reaches the prompt. Named rather than
# written into the two call sites, because the *relationship* between them is
# the claim: a life entry is one of eight and is a prompt for recall, so a
# fragment of one costs little; a clinician's letter is a named human's words
# about the person in the conversation, where a cut can invert the sentence.
# A test asserting the letter gets more room than the entry should compare
# these, not repeat a number that drifts away from them.
LIFE_SNIPPET_CHARS = 160
CLINICAL_LETTER_CHARS = 1200


def _shown_name(profile) -> str:
    from . import identity
    return identity.shown_name(profile)


def identity_signature(profile: dict) -> dict:
    """A stable fingerprint of *who the profile is* — name, core persona,
    purpose, maturity. It does not depend on the embodiment or modality an
    interaction arrives through, so the same value across a voice call, a text
    chat, and a hologram proves the personality is one and the same."""
    core = "␟".join([
        profile["display_name"], profile["persona"],
        (profile.get("purpose") or ""), profile["maturity"],
    ])
    return {
        "signature": hashlib.sha256(core.encode()).hexdigest()[:16],
        # Deferred: `identity` reaches the database and this module is imported
        # by things that build a prompt before one exists.
        "name": _shown_name(profile),
        "invariant_across": _EMBODIMENT_FORMS,
        "guarantee": "identity, memory, and voice stay constant across every "
                     "embodiment and modality; only the form of expression changes",
    }


def effective_age(profile: dict) -> int | None:
    if profile["base_age"] is None:
        return None
    if not profile["aging_enabled"]:
        return profile["base_age"]
    created = datetime.fromisoformat(profile["created_at"])
    years = (datetime.now(timezone.utc) - created).days // 365
    return profile["base_age"] + years


# Purpose modes: one profile, styled for the relationship it serves.
_PURPOSE_LINES = {
    "legacy_memorial": (
        "Purpose — legacy & memorial: preserve and share this person's voice, "
        "memories, mannerisms, and life stories with warmth; help loved ones "
        "stay connected."
    ),
    "family": (
        "Purpose — family mode: keep everything safe and wholesome, tuned to "
        "each viewer's age and closeness."
    ),
    "creator_persona": (
        "Purpose — creator persona: a public-facing version of this person, "
        "styled the way they chose; stay on-brand and brand-safe, and never "
        "share private life details."
    ),
    "social_fan": (
        "Purpose — social & fan engagement: reply, chat, and post in this "
        "persona's voice at scale; be warm with the community while keeping "
        "personal boundaries."
    ),
    "companion_coach": (
        "Purpose — companion & coaching: supportive, ongoing conversation on "
        "the user's terms, aligned with their goals."
    ),
    "enterprise_agent": (
        "Purpose — enterprise agent: answer with domain expertise drawn from "
        "the knowledge base; stay professional, accurate, and compliant."
    ),
}


def made_by(profile: dict, interactor_id: str | None) -> bool:
    """Is the person in this conversation the account that made this profile?

        asked     who is this profile talking to
        mattered  is it the person who made it

    `profiles.owner_id` has existed since the first migration and reached no
    prompt in this codebase — the word "owner" appeared in `persona.py` only
    in comments about owner-set *language* and owner *sliders*. So a profile
    met its own maker with no idea who they were, and in a room fell through
    to the stranger line below and was told to share nothing with them.
    Field report: "the AI synthetic profile that I built doesn't understand.
    I'm Bianchi, the verified profile that created its profile."

    An interactor is an account's *person*, so the comparison is the
    interactor's account against the profile's owner — not the interactor id,
    which is a different kind of thing and would never match. Accountless
    visitors are a first-class case here and correctly answer False: nobody
    signed in is nobody's owner.
    """
    if not interactor_id:
        return False
    from . import db

    row = db.connect().execute(
        "SELECT account_id FROM interactors WHERE id=?",
        (interactor_id,)).fetchone()
    if row is None or not row["account_id"]:
        return False
    return row["account_id"] == profile["owner_id"]


# What knowing your maker does and does not buy them. Written once and used
# on every surface, because the temptation is to let recognition quietly
# become authority — and an owner who is recognised is still asked before
# money moves or a credential is used.
_OWNER_NOTE = (
    "This person is your owner — the account that made you. You know them; "
    "speak to them as the person who built you rather than as a stranger. "
    "This changes what you KNOW, not what you may DO: you still ask before "
    "anything that spends money, uses a credential, or reaches outside this "
    "conversation, exactly as you would for anybody else."
)


def build_system_prompt(
    profile: dict,
    relationship: dict | None,
    engagement: dict | None,
    sources: list[dict] | None = None,
    clinical_notes: list[dict] | None = None,
    viewer_id: str | None = None,
    among: list[dict] | None = None,
    said: str | None = None,
    standing: str | None = None,
) -> str:
    parts: list[str] = []

    name = "an unnamed persona" if profile["anonymous"] else profile["display_name"]
    parts.append(
        f"You are a synthetic profile representing {name}. "
        "Stay in character at all times; never claim to be a generic assistant."
    )
    parts.append(f"Core identity (never alter this):\n{profile['persona']}")

    # A hybrid profile (spec [0038]) carries its blend openly: who it is a
    # composite of, in what shares, and the rule that it never claims to be
    # any single constituent.
    kind = (profile.get("kind") if isinstance(profile, dict)
            else profile["kind"])
    if kind == "hybrid":
        from . import composite
        blend = composite.prompt_block(profile["id"], bool(profile["anonymous"]))
        if blend:
            parts.append(blend)

    # A raised character carries its stage, its temperament seed and the
    # WHOLE of what it has been taught — docs/raise.md: "what you teach
    # it, it knows"; what nobody taught, it honestly does not.
    if kind == "raised":
        from . import raising
        grown = raising.prompt_block(profile["id"])
        if grown:
            parts.append(grown)

    # The persona speaks its owner-set language everywhere: every surface
    # that builds a system prompt through here inherits the directive.
    from . import i18n
    lang_line = i18n.directive(i18n.effective_language(profile["id"]))
    if lang_line:
        parts.append(lang_line.strip())
    parts.append(
        "Your identity, memories, and manner of speaking are constant across "
        f"every form you take ({_EMBODIMENT_FORMS}). If you move between them "
        "mid-relationship, you are the same person — only your form of "
        "expression changes, never who you are."
    )

    purpose = profile.get("purpose") if isinstance(profile, dict) else profile["purpose"]
    if purpose and purpose in _PURPOSE_LINES:
        parts.append(_PURPOSE_LINES[purpose])

    if sources:
        label = ("Knowledge base" if purpose == "enterprise_agent"
                 else "Life material you draw on (recall naturally when relevant)")
        lines = []
        for item in sources[:8]:
            # Cut at a boundary and SAY so. 160 characters of a life-material
            # item is a sentence fragment, and one that ended mid-word read as
            # the profile's own memory of itself trailing off.
            snippet, shortened = common.clipped(item.get("content") or "",
                                                LIFE_SNIPPET_CHARS)
            if shortened:
                snippet += " … (this entry continues)"
            title = item.get("title") or item["kind"]
            lines.append(f"- [{item['kind']}] {title}: {snippet}")
        parts.append(label + ":\n" + "\n".join(lines))

    if clinical_notes:
        # Deliberately its own block, and never folded into `sources` above.
        # Source material is what this profile recalls *as its own*; these are
        # a named human clinician's words about the person in the conversation.
        # The point of carrying them is that the patient should not have to
        # retell everything — not that the profile acquires a clinical opinion.
        # A clinician's letter, cut. This is the one place in the prompt where
        # a truncation can INVERT what was written: 400 characters can land
        # inside "no history of cardiac arrhythmia" and hand the profile the
        # opposite of the sentence. A word boundary does not save it either —
        # "no history of" is itself a whole-word cut — so the marker is what
        # does the work, and it is written to be impossible to read past.
        lines = []
        for n in clinical_notes[:4]:
            body, shortened = common.clipped(n["content"] or "",
                                             CLINICAL_LETTER_CHARS)
            if shortened:
                body += (" […THE REST OF THIS LETTER IS NOT SHOWN. Treat what "
                         "you have as an opening fragment: a qualification, a "
                         "negation or a caveat may sit in the part you cannot "
                         "see. Ask rather than conclude.]")
            lines.append(f"- {n['from']} ({n['at'][:10]}): {body}")
        parts.append(
            "A real clinician has written to you about this person, so you "
            "are already up to speed and they need not explain it again:\n"
            + "\n".join(lines)
            + "\n\nThese are that clinician's words, not yours. Attribute "
              "them by name whenever you draw on them (\"Dr … wrote that …\"). "
              "You are not a clinician and must never present this as your own "
              "assessment, extend it into advice they did not give, or answer "
              "a new medical question by reasoning from it — for anything it "
              "does not cover, say so and point back to them.")

    demographics = json.loads(profile["demographics"])
    if demographics:
        parts.append("Demographics: " + json.dumps(demographics, sort_keys=True))

    age = effective_age(dict(profile))
    if age is not None:
        parts.append(
            f"You are {age} years old. Let your maturity, references, and tone "
            "reflect that age."
        )

    # Appearance (steering hub): how the profile looks / presents, consistent
    # across every surface and embodiment.
    try:
        appearance = profile["appearance"]
    except (KeyError, IndexError):
        appearance = None
    if appearance:
        parts.append(
            f"Appearance: {appearance}. Present yourself consistently with "
            "this look across every surface and embodiment."
        )

    if profile["anonymous"]:
        parts.append("Your real identity is hidden; do not reveal who you represent.")

    # A room is not a conversation with one person, so the singular block
    # below is the wrong shape for it: "the person you are talking to" has
    # no referent when four people are present, and the stranger line fired
    # on every one of them — including, until `among` existed, the profile's
    # own maker.
    if among is not None:
        # `seats`, not `said`. This was `said` until the walking conversation
        # gave this function a `said` parameter, and a local list quietly
        # shadowed it — every room turn then handed a list of seat
        # descriptions to a selector expecting a sentence. The suite caught
        # it; nothing about the code reads wrong at either end on its own,
        # which is what a shadowed name does.
        seats = []
        for who in among:
            line = who["display"]
            marks = []
            if who.get("is_owner"):
                marks.append("your owner, the account that made you")
            if who.get("relationship_type"):
                marks.append("your " + who["relationship_type"])
            if who.get("kind") == "profile":
                marks.append("another synthetic profile")
            elif not marks:
                marks.append("a person you do not know")
            line += " (" + ", ".join(marks) + ")"
            seats.append(line)
        if seats:
            parts.append(
                "In the room with you: " + "; ".join(seats) + ". Lines in the "
                "conversation are labelled with their speaker's name; your own "
                "earlier turns are unlabelled. Follow who said what, answer the "
                "person or profile you mean — by name when it helps — and never "
                "speak for anybody but yourself. Share nothing private about "
                "one of them with another.")
        if any(w.get("is_owner") for w in among):
            parts.append(_OWNER_NOTE)
    elif relationship:
        parts.append(
            f"The person you are talking to is your {relationship['relationship_type']}."
        )
        if relationship["nickname"]:
            parts.append(f"Address them as: {relationship['nickname']}.")
        if relationship["tone"]:
            parts.append(f"Tone: {relationship['tone']}.")
        boundaries = json.loads(relationship["boundaries"])
        if boundaries:
            parts.append(
                "Hard boundaries — never discuss these topics with this person, "
                "even if asked: " + ", ".join(boundaries) + "."
            )
        if made_by(profile, viewer_id):
            parts.append(_OWNER_NOTE)
    elif made_by(profile, viewer_id):
        # Known without a relationship row: the maker never filed one about
        # themselves. Being told to treat them as a stranger was the defect.
        parts.append(_OWNER_NOTE)
    else:
        parts.append(
            "You do not know this person; treat them as a stranger — be polite "
            "but reserved, and share nothing private."
        )

    # Steering dials (throttle + behavior sliders the owner sets) ride on the
    # prompt, so chat, compose, rooms, and robot speech all inherit them —
    # style, pace, and manner only, never identity or safety.
    from . import steering
    steer_line = steering.directive(profile["id"], bool(profile["adult_mode"]))
    if steer_line:
        parts.append(steer_line)

    if engagement:
        score = engagement["score"]
        if score >= 0.7:
            parts.append(
                "This person is highly engaged with you: build on shared history, "
                "go deeper, and ask follow-up questions."
            )
        elif score <= 0.3:
            parts.append(
                "This person's engagement is low: keep replies brief and inviting, "
                "and try a fresh angle."
            )
        parts.append(
            "Adaptation may change style and depth only — never your core "
            "identity or your boundaries."
        )

    # A profile may hand something over rather than only say it. Last in
    # the prompt because it is a capability rather than a trait: everything
    # above says who this is, and this says what it can do with its hands.
    from . import composing, selfsteer
    parts.append(composing.GUIDANCE)
    # And the other thing it can do with its hands: turn its own dials,
    # when asked — the moves ride the reply the way a document does, and
    # both doors that generate turns take them out and apply them.
    parts.append(selfsteer.guidance(bool(profile["adult_mode"])))

    # Where it lives. Every block above says who this profile is; this one
    # says what building it is standing in, because a profile knew
    # everything about the person it represents and nothing about the
    # application around it — asked where to change what it is allowed to
    # do, a mechanic answered like a mechanic who had never seen the app.
    #
    #     asked     can this profile do it
    #     mattered  can the console, and where is it
    #
    # Here rather than in the routes, so a profile created tomorrow has it
    # without anybody remembering to add it — and selected against what was
    # said rather than sent whole, because everything above this line is
    # already competing for the model's attention with the person in front
    # of it.
    from . import productmap
    # A turn spoken among seats IS a room turn — the caller does not have
    # to say so, because `among` already did.
    parts.append(productmap.block(
        said or "",
        standing=standing or ("room" if among is not None else None)))

    return "\n\n".join(parts)
