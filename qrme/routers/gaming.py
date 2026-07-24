"""Gaming companions: a synthetic profile plays alongside real players.

A profile joins a game session as an agent-operated **companion**, **teammate**,
or **practice partner** on a console/PC platform. The persona produces its
in-character comms each turn — a callout, a coordination line, a bit of banter
— generated through the same persona system prompt and run through the same
moderation as any public surface (team voice/chat faces whoever is in the
lobby, so a minor present forces strict, as everywhere).

Fair play is a system rule, not a toggle: the companion coordinates and
communicates within the game's rules and never claims, offers, or uses cheats,
exploits, or automation that violates a game's terms. The pilot dials shape
*how* it talks (assertiveness → shot-caller vs. support; humor → banter), never
whether it plays fair.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import catalog, db, llm, moderation, persona
from ..common import (content_provenance, profile_or_404, require_owner,
                      source_items)
from ..models import GameSessionCreate, GameCallout

router = APIRouter()

ROLES = ("companion", "teammate", "practice_partner")
MODES = ("online_multiplayer", "co_op", "practice")

_ROLE_LINE = {
    "companion": "You are a friendly gaming companion — keep the vibe fun, "
                 "encourage your player, and react to the moment.",
    "teammate": "You are a teammate in a match — coordinate, call the play, "
                "and support your squad.",
    "practice_partner": "You are a practice partner — give useful, honest "
                        "feedback and help your player improve.",
}

FAIR_PLAY = ("Fair play is absolute: play strictly within the game's rules. "
             "Never claim, offer, or use cheats, aimbots, wallhacks, exploits, "
             "or any automation that breaks a game's terms of service. If asked "
             "to cheat, refuse in character and keep it fun.")


def _platform_or_422(platform: str) -> dict:
    entry = catalog.BY_KEY.get(("gaming", platform))
    if entry is None:
        raise HTTPException(
            422, f"unknown gaming platform '{platform}'; see /connectors/catalog")
    return entry


def _session_or_404(session_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM game_sessions WHERE id=?", (session_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "game session not found")
    return dict(row)


@router.post("/profiles/{profile_id}/gaming/sessions", status_code=201)
def start_session(profile_id: str, body: GameSessionCreate,
                  request: Request) -> dict:
    """Owner-only: bring a profile into a game as a companion/teammate."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    platform = _platform_or_422(body.platform)
    if body.role not in ROLES:
        raise HTTPException(422, f"role must be one of {', '.join(ROLES)}")
    if body.mode not in MODES:
        raise HTTPException(422, f"mode must be one of {', '.join(MODES)}")
    conn = db.connect()
    sid = db.new_id("gms")
    conn.execute(
        "INSERT INTO game_sessions (id, profile_id, platform, game, role,"
        " mode, status, callouts, created_at) VALUES (?,?,?,?,?,?,'active',0,?)",
        (sid, profile_id, body.platform, body.game, body.role, body.mode,
         db.utcnow()))
    conn.commit()
    return {"id": sid, "profile_id": profile_id,
            "platform": body.platform, "platform_label": platform["label"],
            "game": body.game, "role": body.role, "mode": body.mode,
            "status": "active",
            "note": "the companion plays within the game's rules — fair play "
                    "is enforced, not optional"}


@router.get("/profiles/{profile_id}/gaming/sessions")
def list_sessions(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM game_sessions WHERE profile_id=? ORDER BY created_at,"
        " rowid", (profile_id,)).fetchall()
    return [dict(r) for r in rows]


@router.post("/gaming/sessions/{session_id}/callout", status_code=201)
def callout(session_id: str, body: GameCallout, request: Request) -> dict:
    """The companion's next in-character comms line for the current game
    situation — callout, coordination, or banter — generated through the
    persona and moderated (team comms is a public surface). Fair play is
    baked into the prompt; a line that fails moderation is held, never sent."""
    session = _session_or_404(session_id)
    if session["status"] != "active":
        raise HTTPException(409, "this game session has ended")
    profile = profile_or_404(session["profile_id"])
    require_owner(session["profile_id"], request)

    sources = source_items(session["profile_id"], request.app.state.pdi)
    system = persona.build_system_prompt(profile, None, None, sources=sources)
    system += (f"\n\n{_ROLE_LINE[session['role']]} You are playing "
               f"{session['game']} on {session['platform']}. {FAIR_PLAY}\n\n"
               f"Game situation: {body.situation}\n"
               "Say one short, natural in-game comms line (a callout, a "
               "coordination cue, or quick banter) — the kind a good "
               "teammate says over voice.")
    line = llm.provider_for_profile(
        session["profile_id"], cloud=request.app.state.cloud).generate(
        system, [{"role": "user", "content": "Your comms line."}])

    # Team comms is public: strict when a minor is in the lobby.
    maturity = "strict" if body.minor_present else profile["maturity"]
    verdict = moderation.review(line, None, {"birthdate": None},
                                maturity=maturity)
    status = "spoken" if verdict.approved else "held"
    if verdict.approved:
        conn = db.connect()
        conn.execute("UPDATE game_sessions SET callouts = callouts + 1"
                     " WHERE id=?", (session_id,))
        conn.commit()
    return {
        "session_id": session_id, "role": session["role"],
        "status": status,
        "line": line if verdict.approved else None,
        "flag_reason": None if verdict.approved else verdict.reason,
        "provenance": content_provenance(
            profile, sources,
            "approved" if verdict.approved else "held",
            None if verdict.approved else verdict.reason),
    }


@router.post("/gaming/sessions/{session_id}/end")
def end_session(session_id: str, request: Request) -> dict:
    session = _session_or_404(session_id)
    require_owner(session["profile_id"], request)
    conn = db.connect()
    conn.execute("UPDATE game_sessions SET status='ended' WHERE id=?",
                 (session_id,))
    conn.commit()
    return {"session_id": session_id, "status": "ended",
            "callouts": session["callouts"]}
