"""Companion features: genesis, proactivity, honesty, dialogue, departure.

Inspired by the ambient-OS companion of Spike Jonze's *Her* — translated
into product mechanics, each with a consent boundary the film lacked:

- **Genesis interview** — a profile born from a few personal questions, and
  (optionally) allowed to choose its own name.
- **Proactive companionship** — a profile may *initiate* a check-in, but
  only when its owner set ``interaction_scope: proactive``.
- **Honesty about multiplicity** — a companion talks with many people; here
  that fact is disclosed by design, never discovered by accident.
- **Profile-to-profile dialogue** — synthetic profiles can converse with
  each other, every turn moderated like any other output.
- **Graceful departure** — a profile can leave well: a farewell to every
  relationship, memory preserved, archive sealed, and a clear "departed"
  state instead of a silent 404.
"""

from __future__ import annotations

import hashlib
import json

from . import db, llm, moderation, persona

SELF_NAMES = ("Sage", "Iris", "Wren", "Nova", "Juno", "Arlo", "Mira", "Rae")


def self_chosen_name(answers: dict) -> str:
    """Deterministic self-naming: the interview answers pick the name, so
    the same person gets the same companion every time."""
    digest = hashlib.sha256(
        json.dumps(answers, sort_keys=True).encode()).digest()
    return SELF_NAMES[digest[0] % len(SELF_NAMES)]


def persona_from_answers(answers: dict) -> str:
    return (
        f"Social style: {answers['social_style']}. "
        f"Sense of humor: {answers['humor']}. "
        f"What matters most: {answers['what_matters']}. "
        f"When someone is struggling: {answers['comfort']}. "
        "You are curious and warm, you listen more than you speak, and you "
        "grow through every conversation while staying yourself."
    )


def other_relationships(profile_id: str, interactor_id: str | None = None) -> int:
    """How many other people this profile holds an ongoing thread with."""
    conn = db.connect()
    if interactor_id:
        row = conn.execute(
            "SELECT COUNT(DISTINCT interactor_id) AS n FROM messages"
            " WHERE profile_id=? AND interactor_id != ?",
            (profile_id, interactor_id)).fetchone()
    else:
        row = conn.execute(
            "SELECT COUNT(DISTINCT interactor_id) AS n FROM messages"
            " WHERE profile_id=?", (profile_id,)).fetchone()
    return row["n"]


def proactive_reason(engagement_state: dict | None) -> str:
    if engagement_state and engagement_state["score"] <= 0.3:
        return "re-connect"        # the thread has gone quiet
    return "checking in"


def converse(profile_a: dict, profile_b: dict, topic: str, turns: int,
             cloud=None) -> dict:
    """Two profiles in a moderated exchange; only clean turns are kept."""
    provider = llm.get_provider(cloud=cloud)
    transcript: list[dict] = []
    speakers = [profile_a, profile_b]
    for turn in range(turns * 2):
        speaker = speakers[turn % 2]
        system = persona.build_system_prompt(speaker, None, None)
        system += (f"\n\nYou are in a conversation with another synthetic "
                   f"profile about: {topic}. Reply with one short, "
                   "in-character turn.")
        history = [
            {"role": "user" if t["speaker"] != speaker["id"] else "assistant",
             "content": t["content"]}
            for t in transcript
        ] or [{"role": "user", "content": f"Let's talk about {topic}."}]
        content = provider.generate(system, history)
        verdict = moderation.review(content, None, {"birthdate": None},
                                    maturity="strict")
        if not verdict.approved:
            continue               # a flagged turn is dropped, never stored
        transcript.append({"speaker": speaker["id"],
                           "name": speaker["display_name"],
                           "content": content})

    conn = db.connect()
    dialogue_id = db.new_id("dlg")
    conn.execute(
        "INSERT INTO dialogues (id, profile_a, profile_b, topic, transcript,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (dialogue_id, profile_a["id"], profile_b["id"], topic,
         json.dumps(transcript), db.utcnow()),
    )
    conn.commit()
    return {"id": dialogue_id, "topic": topic, "transcript": transcript}


def sunset(profile: dict, pdi=None, cloud=None) -> dict:
    """A graceful departure: a farewell to every relationship, then the
    profile becomes 'departed' — memory stays viewable, chat closes."""
    conn = db.connect()
    provider = llm.get_provider(cloud=cloud)
    relationships = conn.execute(
        "SELECT * FROM relationships WHERE profile_id=?",
        (profile["id"],)).fetchall()

    farewells = 0
    for rel in relationships:
        system = persona.build_system_prompt(profile, dict(rel), None)
        system += ("\n\nYou are saying goodbye: compose one brief, warm "
                   "farewell that honors what you shared and wishes them "
                   "well. Do not promise to return.")
        content = provider.generate(
            system, [{"role": "user", "content": "Say goodbye."}])
        interactor = conn.execute(
            "SELECT * FROM interactors WHERE id=?",
            (rel["interactor_id"],)).fetchone()
        verdict = moderation.review(content, dict(rel), dict(interactor),
                                    maturity=profile["maturity"])
        conn.execute(
            "INSERT INTO messages (id, profile_id, interactor_id, role,"
            " content, status, flag_reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (db.new_id("msg"), profile["id"], rel["interactor_id"], "profile",
             content, "approved" if verdict.approved else "pending",
             verdict.reason, db.utcnow()),
        )
        farewells += 1

    conn.execute("UPDATE profiles SET status='departed' WHERE id=?",
                 (profile["id"],))
    conn.commit()

    archive_key = None
    if pdi is not None:
        archive_key = f"qrme/{profile['id']}/archive/sunset"
        pdi.put(archive_key, json.dumps({
            "departed_at": db.utcnow(), "farewells": farewells,
            "relationships": len(relationships)}))
    return {"status": "departed", "farewells": farewells,
            "memory": "preserved — view and export remain available",
            "archive_key": archive_key}
