"""Assistant & perception: the profile as a capable personal assistant.

Inspired by Samantha's assistant/creative/perceptual roles in *Her*:

- **Triage** — sort through a large pile of items and curate the best few
  (the "keep the 86 best emails" scene). Ranking is transparent and
  deterministic, not a black box.
- **Proofread** — edit and improve a piece of writing, with concrete
  suggestions.
- **Perceive** — "see" a real-time scene (objects, people, gestures) through
  a camera and give hands-free guidance toward a goal (navigating a crowd).
- **Compose** — create an original creative work (music, poem, note) that
  captures a shared moment, kept as an artifact.

All generated text passes the profile's moderation before it is returned.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import db, llm, moderation, persona
from ..common import profile_or_404, source_items
from ..models import (
    ComposeCreative, PerceiveRequest, ProofreadRequest, TriageRequest,
)

router = APIRouter()


def _provider(request: Request):
    return llm.get_provider(cloud=request.app.state.cloud)


# --------------------------------------------------------------------------- #
# triage — curate the best N from a large pile
# --------------------------------------------------------------------------- #

def _score(text: str, criteria: str | None) -> float:
    """Transparent relevance score: substance (length, sentence structure),
    signal words, and criteria-keyword matches — auditable, not opaque."""
    words = text.split()
    score = min(len(words) / 40, 1.0) * 2                 # substance
    strong = ("achieved", "led", "delivered", "launched", "grew", "award",
              "promoted", "solved", "built", "shipped", "results")
    score += sum(1 for w in strong if w in text.lower()) * 0.5
    if criteria:
        keys = [k.strip().lower() for k in criteria.split() if len(k) > 3]
        score += sum(1 for k in keys if k in text.lower()) * 0.8
    return round(score, 3)


@router.post("/profiles/{profile_id}/assist/triage")
def triage(profile_id: str, body: TriageRequest) -> dict:
    profile_or_404(profile_id)
    keep = min(body.keep, len(body.items))
    ranked = sorted(
        ({"id": it.id, "score": _score(it.text, body.criteria),
          "preview": it.text[:80]} for it in body.items),
        key=lambda r: r["score"], reverse=True)
    return {
        "reviewed": len(body.items),
        "kept": [{"id": r["id"], "reason": f"strongest match (score {r['score']})",
                  "preview": r["preview"]} for r in ranked[:keep]],
        "discarded_ids": [r["id"] for r in ranked[keep:]],
        "criteria": body.criteria or "overall strength",
    }


# --------------------------------------------------------------------------- #
# proofread — edit and suggest
# --------------------------------------------------------------------------- #

def _suggestions(text: str) -> list[str]:
    out = []
    if "  " in text:
        out.append("collapse double spaces")
    if text != text.strip():
        out.append("trim leading/trailing whitespace")
    if text and text[-1] not in ".!?\"'":
        out.append("add end punctuation")
    if " i " in f" {text} ":
        out.append("capitalize the pronoun 'I'")
    return out


@router.post("/profiles/{profile_id}/assist/proofread")
def proofread(profile_id: str, body: ProofreadRequest, request: Request) -> dict:
    profile = profile_or_404(profile_id)
    system = persona.build_system_prompt(profile, None, None)
    system += ("\n\nYou are proofreading the user's writing. Return an "
               "improved version that keeps their voice: fix grammar, "
               "clarity, and flow without changing the meaning.")
    edited = _provider(request).generate(
        system, [{"role": "user", "content": body.text}])
    verdict = moderation.review(edited, None, {"birthdate": None},
                                maturity=profile["maturity"])
    return {
        "original": body.text,
        "edited": edited if verdict.approved else None,
        "suggestions": _suggestions(body.text),
        "status": "approved" if verdict.approved else "blocked",
    }


# --------------------------------------------------------------------------- #
# perceive — see a scene and guide hands-free
# --------------------------------------------------------------------------- #

@router.post("/profiles/{profile_id}/perceive")
def perceive(profile_id: str, body: PerceiveRequest, request: Request) -> dict:
    profile = profile_or_404(profile_id)
    if profile["status"] == "departed":
        raise HTTPException(410, "this profile has departed")

    recognized = {"objects": body.objects, "people": body.people,
                  "gestures": body.gestures, "place": body.place}
    scene_desc = json.dumps({k: v for k, v in recognized.items() if v})
    system = persona.build_system_prompt(profile, None, None)
    system += ("\n\nYou can see the user's surroundings in real time through "
               f"their camera. Current scene: {scene_desc}. "
               + (f"Their goal: {body.goal}. Give calm, hands-free, "
                  "step-by-step guidance." if body.goal
                  else "Describe warmly what you see and share the moment."))
    guidance = _provider(request).generate(
        system, [{"role": "user", "content": "What do you see? Guide me."}])
    verdict = moderation.review(guidance, None, {"birthdate": None},
                                maturity=profile["maturity"])

    conn = db.connect()
    perception_id = db.new_id("prc")
    conn.execute(
        "INSERT INTO perceptions (id, profile_id, scene, goal, guidance,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (perception_id, profile_id, json.dumps(recognized), body.goal,
         guidance if verdict.approved else "", db.utcnow()),
    )
    conn.commit()
    return {
        "id": perception_id,
        "recognized": {k: v for k, v in recognized.items() if v},
        "recognized_count": sum(len(v) for v in
                                (body.objects, body.people, body.gestures)),
        "goal": body.goal,
        "guidance": guidance if verdict.approved else None,
        "status": "approved" if verdict.approved else "blocked",
    }


# --------------------------------------------------------------------------- #
# compose — an original creative work capturing a moment
# --------------------------------------------------------------------------- #

_CREATIVE_BRIEF = {
    "music": "Compose a short original piano piece — describe its melody, "
             "tempo, and feeling — that captures this moment.",
    "poem": "Write a short original poem that captures this moment.",
    "note": "Write a short, heartfelt original note about this moment.",
    "lyric": "Write short original song lyrics that capture this moment.",
}


@router.post("/profiles/{profile_id}/assist/compose", status_code=201)
def compose_creative(profile_id: str, body: ComposeCreative,
                     request: Request) -> dict:
    profile = profile_or_404(profile_id)
    system = persona.build_system_prompt(profile, None, None)
    system += (f"\n\n{_CREATIVE_BRIEF[body.kind]} The moment: {body.moment}. "
               "Make it personal and original.")
    content = _provider(request).generate(
        system, [{"role": "user", "content": f"Create it about: {body.moment}"}])
    verdict = moderation.review(content, None, {"birthdate": None},
                                maturity=profile["maturity"])
    if not verdict.approved:
        raise HTTPException(422, f"creative work blocked: {verdict.reason}")

    conn = db.connect()
    work_id = db.new_id("wrk")
    conn.execute(
        "INSERT INTO creative_works (id, profile_id, kind, moment, content,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (work_id, profile_id, body.kind, body.moment, content, db.utcnow()),
    )
    conn.commit()
    return {"id": work_id, "kind": body.kind, "moment": body.moment,
            "content": content}


@router.get("/profiles/{profile_id}/assist/works")
def list_works(profile_id: str) -> list[dict]:
    profile_or_404(profile_id)
    rows = db.connect().execute(
        "SELECT * FROM creative_works WHERE profile_id=?"
        " ORDER BY created_at, rowid", (profile_id,)).fetchall()
    return [dict(r) for r in rows]
