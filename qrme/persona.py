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

# Surfaces / embodiments a profile can inhabit — its identity is invariant
# across all of them.
_EMBODIMENT_FORMS = "text, voice, feed, AR/VR, a speaker, a hologram, or a robot"


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
        "name": ("anonymous persona" if profile["anonymous"]
                 else profile["display_name"]),
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


def build_system_prompt(
    profile: dict,
    relationship: dict | None,
    engagement: dict | None,
    sources: list[dict] | None = None,
) -> str:
    parts: list[str] = []

    name = "an unnamed persona" if profile["anonymous"] else profile["display_name"]
    parts.append(
        f"You are a synthetic profile representing {name}. "
        "Stay in character at all times; never claim to be a generic assistant."
    )
    parts.append(f"Core identity (never alter this):\n{profile['persona']}")

    # The persona speaks its owner-set language everywhere: every surface
    # that builds a system prompt through here inherits the directive.
    from . import i18n
    lang_line = i18n.directive(i18n.get_language(profile["id"]))
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
            snippet = (item.get("content") or "")[:160]
            title = item.get("title") or item["kind"]
            lines.append(f"- [{item['kind']}] {title}: {snippet}")
        parts.append(label + ":\n" + "\n".join(lines))

    demographics = json.loads(profile["demographics"])
    if demographics:
        parts.append("Demographics: " + json.dumps(demographics, sort_keys=True))

    age = effective_age(dict(profile))
    if age is not None:
        parts.append(
            f"You are {age} years old. Let your maturity, references, and tone "
            "reflect that age."
        )

    if profile["anonymous"]:
        parts.append("Your real identity is hidden; do not reveal who you represent.")

    if relationship:
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
    else:
        parts.append(
            "You do not know this person; treat them as a stranger — be polite "
            "but reserved, and share nothing private."
        )

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

    return "\n\n".join(parts)
