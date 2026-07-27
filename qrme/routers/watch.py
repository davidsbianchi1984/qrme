"""The watch: a wrist extension and remote for agents, profile, and robots.

One glanceable payload with a status light per running thing —
**green = working, orange = needing assistance, red = stopped** — and a
remote `act` endpoint so the owner can assist a paused agent, halt one,
approve a held reply, or command a robot body from the wrist. The watch is
the owner's *control* surface; it is distinct from the wearable *presence*
surface a persona can live on.

Everything the watch shows and does reuses the existing machinery:
workflows advance/resume/cancel, moderation approve/reject, and the robot
command allowlist (learned task-pack verbs included) — the wrist adds no
new powers, only reach.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal

from fastapi import APIRouter, HTTPException, Request

from .. import db, robotics, steering, wearables, workflows
from ..common import profile_or_404, require_owner
from .interaction import approve_message, reject_message
from .robots import RobotCommand, command_robot

router = APIRouter()


class WearablePair(BaseModel):
    name: str = Field(min_length=1, max_length=60,
                      description="What you will recognise it by.")
    kind: str = Field(description="See GET .../wearables for the list.")
    faces: list[str] | None = Field(
        None, description="Which faces this device may show. Defaults to "
                          "agents + activity.")


@router.get("/profiles/{profile_id}/wearables")
def list_wearables(profile_id: str, request: Request,
                   include_revoked: bool = False) -> dict:
    """Devices paired to this account, and which faces each may show."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return {"profile_id": profile_id,
            "wearables": wearables.paired(profile_id, include_revoked),
            "faces": wearables.FACES,
            "kinds": wearables.KINDS,
            # Said out loud, so a client can grey these out with the reason
            # rather than offering them and returning a 422.
            "refused": {k: wearables.REFUSAL.format(kind=k, what=v)
                        for k, v in wearables.REFUSED.items()}}


@router.post("/profiles/{profile_id}/wearables", status_code=201)
def pair_wearable(profile_id: str, body: WearablePair,
                  request: Request) -> dict:
    """Pair a watch or wearable over Bluetooth.

    Pairing and permission only — no sensor stream, no capture, nothing about
    a microphone. A paired device here is a screen and a set of buttons.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return wearables.pair(profile_id, body.name, body.kind, body.faces)
    except wearables.WearableError as exc:
        raise HTTPException(422, str(exc)) from None


@router.delete("/profiles/{profile_id}/wearables/{name}")
def unpair_wearable(profile_id: str, name: str, request: Request) -> dict:
    """Unpair. The record survives so a device sent away cannot come back by
    re-presenting the same name, and so the owner can see what was ever
    paired — the question people actually ask after losing a watch."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return wearables.unpair(profile_id, name)
    except wearables.WearableError as exc:
        raise HTTPException(404, str(exc)) from None


# agent status -> watch light
LIGHTS = {"running": "green", "awaiting_input": "orange",
          "failed": "red", "cancelled": "red", "completed": "done"}
ROBOT_LIGHTS = {"active": "green", "docked": "idle", "offline": "red"}

# The wrist's quick ring: short, glanceable robot commands.
QUICK_RING = ["come_here", "patrol", "dock", "stop"]


class WatchAct(BaseModel):
    target: Literal["workflow", "robot", "approval"]
    id: str
    action: str                        # workflow: advance|assist|cancel ·
    #                                    robot: any allowlisted/learned verb ·
    #                                    approval: approve|reject
    input: str | None = None           # assist text / robot command arg


@router.get("/profiles/{profile_id}/watch")
def watch_face(profile_id: str, request: Request) -> dict:
    """The glanceable face: every agent with its light, the profile chip,
    and each robot with its quick-command ring."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()

    agents = []
    for wf in workflows.list_for(profile_id):
        agents.append({
            "id": wf["id"], "goal": wf["goal"],
            "phase": wf["next_phase"], "status": wf["status"],
            "light": LIGHTS.get(wf["status"], "idle"),
            "awaiting": wf["awaiting"],
        })

    pending = conn.execute(
        "SELECT COUNT(*) AS n FROM messages WHERE profile_id=? AND"
        " status='pending'", (profile_id,)).fetchone()["n"]
    profile_light = ("red" if profile["status"] != "active"
                     else "orange" if pending else "green")

    robots = []
    for r in conn.execute(
            "SELECT * FROM robots WHERE profile_id=? ORDER BY created_at,"
            " rowid", (profile_id,)).fetchall():
        allowed = robotics.allowed_commands(r["model"])
        learned = [s["task"] for s in conn.execute(
            "SELECT task FROM robot_skills WHERE robot_id=? ORDER BY task",
            (r["id"],)).fetchall()]
        robots.append({
            "id": r["id"], "name": r["name"], "model": r["model"],
            "status": r["status"],
            "light": ROBOT_LIGHTS.get(r["status"], "idle"),
            "quick_commands": [c for c in QUICK_RING if c in allowed],
            "learned_tasks": learned,
        })

    working = (sum(1 for a in agents if a["light"] == "green")
               + sum(1 for r in robots if r["light"] == "green"))
    needing = (sum(1 for a in agents if a["light"] == "orange")
               + (1 if profile_light == "orange" else 0))
    stopped = (sum(1 for a in agents if a["light"] == "red")
               + sum(1 for r in robots if r["light"] == "red")
               + (1 if profile_light == "red" else 0))
    return {
        "profile": {"id": profile_id,
                    "display_name": profile["display_name"],
                    "status": profile["status"], "light": profile_light,
                    "pending_approvals": pending,
                    # The wrist's throttle read-out: pace + autonomy at a
                    # glance, set through PUT /profiles/{id}/steering.
                    "throttle": {k: steering.get(profile_id)[k]
                                 for k in ("pace", "autonomy")}},
        "agents": agents,
        "robots": robots,
        "summary": {"working": working, "needing_assistance": needing,
                    "stopped": stopped},
        # The wrist taps the owner when something needs them.
        "haptic": "alert" if (needing or stopped) else None,
    }


@router.post("/profiles/{profile_id}/watch/act", status_code=201)
def watch_act(profile_id: str, body: WatchAct, request: Request) -> dict:
    """One remote action from the wrist. Reuses the exact same paths the
    full apps use — same auth, same allowlists, same moderation."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)

    if body.target == "workflow":
        wf = workflows.get(profile_id, body.id)
        if wf is None:
            raise HTTPException(404, "workflow not found")
        if body.action == "advance":
            result = workflows.advance(profile, wf,
                                       pdi=request.app.state.pdi,
                                       cloud=request.app.state.cloud)
        elif body.action == "assist":
            if not body.input:
                raise HTTPException(
                    422, "assist needs input — what the paused phase asked "
                         "for")
            result = workflows.resume(profile_id, wf, body.input)
        elif body.action == "cancel":
            result = workflows.cancel(profile_id, wf)
        else:
            raise HTTPException(
                422, "workflow actions: advance, assist, cancel")

    elif body.target == "robot":
        result = command_robot(
            body.id, RobotCommand(command=body.action, arg=body.input),
            request)

    else:                              # approval
        if body.action == "approve":
            result = approve_message(body.id, request)
        elif body.action == "reject":
            result = reject_message(body.id, request)
        else:
            raise HTTPException(422, "approval actions: approve, reject")

    return {"target": body.target, "id": body.id, "action": body.action,
            "result": result}
