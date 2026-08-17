"""Asking the people, not the pages.

:mod:`qrme.research` sends a sanitized brief to a model and brings general
knowledge back. That covers what is already written down. It does not cover the
thing a person two streets over knows and nobody ever published — which shop
still repairs this, what the part is actually called, why the obvious answer is
wrong in an old house.

An **inquiry** is that question, put where people can answer it. Anyone on the
internet can answer one; nobody needs an account to. What comes back is folded
into the profile as a learned ``knowledge`` source, the same fold the excursion
findings get, so the offline model ends up knowing it and the people who
answered end up knowing nothing.

    asked     can the agent look it up
    mattered  can the agent ask somebody who knows

Three things are hardcoded rather than configured, because a privacy posture
with a switch on it is a privacy posture somebody will switch:

1. **The question is sanitized on the way out.** :func:`compose` is the only
   way to build one, it always runs :func:`qrme.research.sanitize`, and it
   takes no argument that skips it. There is no second scrubber to keep in
   step with the first.
2. **The public wire carries the sanitized brief and nothing else.**
   :func:`public` is the only shape the accountless routes return. The profile
   id, the owner's own words, the redaction count and whether it left the host
   are all owner-side fields — an outsider reading the board cannot tell whose
   question it is, or that two questions came from one person.
3. **An answer is a stranger's text.** It is moderated on arrival and it is
   never executed, never followed automatically, and never folded without the
   owner saying so. Being pointed in a direction is not the same as being
   steered, and the difference is a person choosing.
"""

from __future__ import annotations

from . import db, privileges, research

# What an outsider is allowed to see of an inquiry. Every other column on the
# table is the owner's side of it. Keeping this list here — rather than
# spelling the dict out at each route — is what lets one guard check that no
# route ever widens it.
PUBLIC_FIELDS = ("id", "brief", "asked_at", "answer_count", "closed")

# An answer is written by somebody with no account, so it is bounded on
# arrival rather than trusted: a stranger cannot post a novel into a profile's
# knowledge base, and an alias cannot be a paragraph pretending to be one.
MAX_ANSWER = 4000
MAX_ALIAS = 40
MAX_SOURCE = 500


def compose(profile_id: str, topic: str, question: str,
            private: list[str] | None = None) -> tuple[str, int]:
    """The outbound question, and how much was taken out of it.

    The only way to build the text of an inquiry. It always sanitizes: there is
    deliberately no parameter here that turns it off, no plan that exempts a
    profile from it, and no second path that reaches the board. A caller who
    wants to withhold *more* passes ``private``; nobody can withhold less.

    The privilege is asked for here for the same reason the sanitiser is: this
    is the only way to build one, so it is the only place either can be
    skipped.
    """
    privileges.require(profile_id, "ask_people")
    return research.sanitize(profile_id, f"{topic}\n{question}", private)


def public(row: dict, answer_count: int = 0) -> dict:
    """An inquiry as an outsider sees it: the sanitized brief, and the facts
    about the question itself. Whose it is, what they actually typed, and how
    much of it was taken out are all absent — a redaction count is a fact about
    a person, and two questions with the same count are a thread to pull."""
    out = {"id": row["id"], "brief": row["brief"], "asked_at": row["created_at"],
           "answer_count": answer_count, "closed": bool(row["closed_at"])}
    assert set(out) == set(PUBLIC_FIELDS), "the public shape changed"
    return out


def answer_out(row: dict) -> dict:
    """One answer. The alias is whatever the person typed, or nothing — an
    answer from nobody in particular is still an answer."""
    return {"id": row["id"], "inquiry_id": row["inquiry_id"],
            "alias": row["alias"] or "", "body": row["body"],
            "points_to": row["points_to"] or "",
            "answered_at": row["created_at"],
            "blocked": bool(row["blocked"]), "folded": bool(row["folded_src"])}


def count_answers(inquiry_id: str) -> int:
    """Answers a reader would actually be shown — a blocked one is kept for the
    record and counted to nobody."""
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM inquiry_answers"
        " WHERE inquiry_id=? AND blocked=0", (inquiry_id,)).fetchone()["n"]
