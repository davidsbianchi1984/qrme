"""Builds the profile-conditioned system prompt.

This is where the PRD's core differentiators meet the model: the prompt is
assembled from (1) the profile's fixed identity, (2) the relationship between
the represented person and this specific interactor, (3) the engagement
signal accumulated for that interactor, and (4) the profile's aging config.
Identity and boundaries are stated as non-negotiable so engagement adaptation
cannot erode them (PRD 6.3).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone


def effective_age(profile: dict) -> int | None:
    if profile["base_age"] is None:
        return None
    if not profile["aging_enabled"]:
        return profile["base_age"]
    created = datetime.fromisoformat(profile["created_at"])
    years = (datetime.now(timezone.utc) - created).days // 365
    return profile["base_age"] + years


def build_system_prompt(
    profile: dict,
    relationship: dict | None,
    engagement: dict | None,
    situation: str | None = None,
) -> str:
    parts: list[str] = []

    name = "an unnamed persona" if profile["anonymous"] else profile["display_name"]
    parts.append(
        f"You are a synthetic profile representing {name}. "
        "Stay in character at all times; never claim to be a generic assistant."
    )
    parts.append(f"Core identity (never alter this):\n{profile['persona']}")

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

    if situation:
        # Guardian passes a real-time condition note here; the specialist agent
        # responds to the monitored state (claim 6: biometric/context data
        # conditions the interaction).
        parts.append(
            "Current situation from real-time monitoring: " + situation + " "
            "Respond supportively and specifically to this. Keep the person safe; "
            "if they may be in danger, urge them to seek immediate help."
        )

    return "\n\n".join(parts)
