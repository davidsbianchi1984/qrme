"""Hybrid profiles — one persona blended from several people.

Spec [0038]: "the AI profile may represent a combination of aspects or
characteristics of several people, such as a combination of several past
presidents or business leaders, a combination of trusted relatives such as
grandparents who are gone, or other such hybrid profiles."

The composite is an ordinary profile (kind=hybrid) so everything built for
profiles — chat, memory, moderation, watermarking, steering — works on it
unchanged. What makes it a hybrid lives in `composite_sources`: one row per
constituent with its normalized share of the blend and, optionally, which
aspect of that person is borrowed. The rows are the provenance, and the
persona prompt is honest about them: a hybrid says openly that it is a blend
and never claims to be any single one of its constituents.

Who may be blended: a profile the same owner holds, or one listed publicly on
the marketplace. Departed profiles are allowed on purpose — "grandparents who
are gone" is the spec's own example. Rated (adult-mode) profiles are refused
outright: a blend dilutes exactly the consent that made the rated persona
permissible.
"""

from __future__ import annotations

import json

from . import db


class CompositeError(Exception):
    """Refusal with a reason the caller can read."""


def _source_or_refuse(source, owner_id: str) -> dict:
    conn = db.connect()
    row = conn.execute("SELECT * FROM profiles WHERE id=?",
                       (source.profile_id,)).fetchone()
    if row is None:
        raise CompositeError(f"source profile {source.profile_id} not found")
    profile = dict(row)
    if profile["adult_mode"]:
        raise CompositeError(
            "a rated profile can never be blended into a hybrid")
    if profile["status"] in ("terminated", "restricted"):
        raise CompositeError(
            f"source profile {profile['display_name']} is "
            f"{profile['status']} and cannot be blended")
    if profile["owner_id"] != owner_id:
        listed = conn.execute(
            "SELECT 1 FROM marketplace WHERE profile_id=?",
            (source.profile_id,)).fetchone()
        if listed is None:
            raise CompositeError(
                "sources must be your own profiles or listed on the "
                f"marketplace; {profile['display_name']} is neither")
    return profile


def resolve_sources(body) -> list[tuple[dict, float, str | None]]:
    """Validate every constituent and normalize the weights to shares."""
    seen: set[str] = set()
    resolved = []
    for source in body.sources:
        if source.profile_id in seen:
            raise CompositeError(
                f"source profile {source.profile_id} appears twice")
        seen.add(source.profile_id)
        resolved.append((_source_or_refuse(source, body.owner_id),
                         source.weight, source.aspect))
    total = sum(w for _, w, _ in resolved)
    return [(p, round(w / total, 4), a) for p, w, a in resolved]


def blend_persona(resolved) -> tuple[str, dict]:
    """The composite's core identity text and merged demographics.

    Demographics merge highest-weight-first so the dominant constituent's
    facts win where they collide.
    """
    lines = ["A composite persona, deliberately blended from several people:"]
    for profile, share, aspect in resolved:
        pct = int(round(share * 100))
        borrowed = f" — drawing on their {aspect}" if aspect else ""
        lines.append(f"- {profile['display_name']} ({pct}%){borrowed}: "
                     f"{profile['persona']}")
    demographics: dict = {}
    for profile, _, _ in sorted(resolved, key=lambda r: -r[1]):
        for key, value in json.loads(profile["demographics"]).items():
            demographics.setdefault(key, value)
    return "\n".join(lines), demographics


def record(profile_id: str, resolved) -> None:
    conn = db.connect()
    for profile, share, aspect in resolved:
        conn.execute(
            "INSERT INTO composite_sources (profile_id, source_profile_id,"
            " weight, aspect, created_at) VALUES (?,?,?,?,?)",
            (profile_id, profile["id"], share, aspect, db.utcnow()))
    conn.commit()


def composition(profile_id: str) -> list[dict]:
    """The blend, readable by anyone — a hybrid's constituents are its
    transparency, the same stance as /transparency and the watermark."""
    rows = db.connect().execute(
        "SELECT c.source_profile_id, c.weight, c.aspect, p.display_name"
        " FROM composite_sources c JOIN profiles p ON p.id=c.source_profile_id"
        " WHERE c.profile_id=? ORDER BY c.weight DESC, p.display_name",
        (profile_id,)).fetchall()
    return [dict(r) for r in rows]


def prompt_block(profile_id: str, anonymous: bool) -> str | None:
    """The honesty block a hybrid carries in every system prompt."""
    parts = composition(profile_id)
    if not parts:
        return None
    if anonymous:
        return ("You are a deliberate composite of several people whose "
                "identities are private. If asked, say openly that you are "
                "a blend — never claim to be one real person.")
    names = ", ".join(
        f"{p['display_name']} ({int(round(p['weight'] * 100))}%"
        + (f", their {p['aspect']}" if p["aspect"] else "") + ")"
        for p in parts)
    return ("You are a deliberate composite persona blending: " + names + ". "
            "Let each constituent's voice surface in proportion to their "
            "share. If asked who you are, say openly that you are a blend "
            "of these people — never claim to be any single one of them.")
