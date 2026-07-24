"""Robotic embodiment: a profile inhabiting a physical body.

Binds a robot from the shared catalog (``qrme.robotics``) to a profile. The
binding creates a normal ``embodiments`` row, so everything that already holds
for embodiments — identity consistency, chat routing through a registered
surface — holds for the robot too: it is the *same personality* in a body, not
a second persona.

The platforms in the catalog can run an onboard LLM; the binding records which
provider (from the ``qrme.llm`` registry) the robot is loaded with, defaulting
to the profile's own model preference so the persona speaks through the same
model everywhere.

Safety model:

* commands are validated against the catalog's **per-kind allowlist** — a
  vacuum cannot be told to ``fetch``, and unknown commands are refused;
* ``say`` generates the line **in character** through the profile's provider
  and then runs the strict moderation filter (a robot speaking into a room is
  a public surface); a rejected line is never sent to the body;
* every command lands in ``robot_commands`` for the audit trail.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .. import db, llm, moderation, persona, robotics
from ..common import profile_or_404, require_owner, source_items

router = APIRouter()
logger = logging.getLogger("qrme.robots")


class RobotBind(BaseModel):
    model: str                     # robotics catalog key, e.g. "neo"
    name: str | None = None        # household name; defaults to the label
    llm_provider: str | None = None  # qrme.llm registry name; None → profile's


class RobotCommand(BaseModel):
    command: str
    arg: str | None = None         # e.g. the topic for "say", a room for "clean"


def _robot_or_404(robot_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM robots WHERE id=?", (robot_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "robot not found")
    return dict(row)


@router.get("/robotics/catalog")
def robotics_catalog() -> dict:
    """Every supported robot platform, grouped by maker, with the per-kind
    command allowlists. Public — it is a static registry."""
    return robotics.catalog()


@router.post("/profiles/{profile_id}/robots", status_code=201)
def bind_robot(profile_id: str, body: RobotBind, request: Request) -> dict:
    """Owner-only. Bind a catalog robot to this profile as an embodiment."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    spec = robotics.get(body.model)
    if spec is None:
        raise HTTPException(404, f"unknown robot model '{body.model}'")

    # Which LLM rides along: an explicit choice, else the profile's own
    # preference. Only validated (and stored) for llm-capable platforms.
    provider = None
    if spec["llm_capable"]:
        provider = body.llm_provider or llm.get_choice(profile_id)
        if provider not in llm.CHOICES:
            raise HTTPException(
                422, f"llm_provider must be one of {', '.join(llm.CHOICES)}")
    elif body.llm_provider:
        raise HTTPException(
            422, f"{spec['label']} cannot run an onboard LLM")

    name = body.name or spec["label"]
    conn = db.connect()
    robot_id = db.new_id("rob")
    conn.execute(
        "INSERT INTO robots (id, profile_id, model, name, llm_provider,"
        " status, created_at) VALUES (?,?,?,?,?,'docked',?)",
        (robot_id, profile_id, body.model, name, provider, db.utcnow()))
    # The robot is an embodiment like any other — same identity, new body.
    conn.execute(
        "INSERT OR REPLACE INTO embodiments (profile_id, name, kind, has_llm,"
        " created_at) VALUES (?,?,?,?,?)",
        (profile_id, name, robotics.EMBODIMENT_KIND[spec["kind"]],
         int(spec["llm_capable"]), db.utcnow()))
    conn.commit()
    logger.info("profile %s bound robot %s (%s, llm=%s)",
                profile_id, robot_id, body.model, provider)
    return {"id": robot_id, "profile_id": profile_id, "model": body.model,
            "label": spec["label"], "maker": spec["maker"],
            "kind": spec["kind"], "name": name, "llm_provider": provider,
            "commands": robotics.allowed_commands(body.model),
            "identity": persona.identity_signature(profile),
            "note": "the same personality now speaks through this body; "
                    "identity stays invariant across embodiments"}


@router.get("/profiles/{profile_id}/robots")
def list_robots(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM robots WHERE profile_id=? ORDER BY created_at",
        (profile_id,)).fetchall()
    return [{**dict(r),
             "commands": robotics.allowed_commands(r["model"])} for r in rows]


@router.delete("/robots/{robot_id}")
def unbind_robot(robot_id: str, request: Request) -> dict:
    """Owner-only. Unbind the body; the persona is untouched."""
    robot = _robot_or_404(robot_id)
    require_owner(robot["profile_id"], request)
    conn = db.connect()
    conn.execute("DELETE FROM robots WHERE id=?", (robot_id,))
    conn.execute("DELETE FROM embodiments WHERE profile_id=? AND name=?",
                 (robot["profile_id"], robot["name"]))
    conn.commit()
    return {"id": robot_id, "unbound": True}


@router.post("/robots/{robot_id}/command", status_code=201)
def command_robot(robot_id: str, body: RobotCommand, request: Request) -> dict:
    """Owner-only. Send one allowlisted command to the body. ``say`` speaks in
    character (generated by the robot's LLM provider, strictly moderated);
    motion commands are queued for the platform bridge."""
    robot = _robot_or_404(robot_id)
    profile = profile_or_404(robot["profile_id"])
    require_owner(robot["profile_id"], request)

    allowed = robotics.allowed_commands(robot["model"])
    # Installed task packs extend the allowlist: a task module is a new
    # commandable verb for exactly this body, capability-checked at install
    # and audited like every built-in command.
    skill = db.connect().execute(
        "SELECT s.task, s.title, s.procedure, p.title AS pack_title"
        " FROM robot_skills s JOIN knowledge_packs p ON p.id = s.pack_id"
        " WHERE s.robot_id=? AND s.task=?",
        (robot_id, body.command)).fetchone()
    if body.command not in allowed and skill is None:
        raise HTTPException(
            422, f"'{body.command}' is not permitted for a "
                 f"{robotics.get(robot['model'])['kind']}; "
                 f"allowed: {', '.join(allowed)} — plus any installed "
                 "task-pack modules")

    result: dict
    if body.command == "say":
        if not body.arg:
            raise HTTPException(422, "say requires an arg (what to speak about)")
        system = persona.build_system_prompt(
            profile, None, None,
            sources=source_items(robot["profile_id"], request.app.state.pdi))
        system += (f"\n\nYou are speaking aloud through your {robot['name']} "
                   f"body. Say one short, natural line about: {body.arg}.")
        learned = [r["title"] for r in db.connect().execute(
            "SELECT title FROM robot_skills WHERE robot_id=? ORDER BY task",
            (robot_id,)).fetchall()]
        if learned:
            # The embodied agent knows what its body has learned.
            system += (" Task modules your body has learned: "
                       + ", ".join(learned) + ".")
        provider = llm.get_provider(cloud=request.app.state.cloud,
                                    choice=robot["llm_provider"])
        line = provider.generate(
            system, [{"role": "user", "content": "Speak the line."}])
        # A robot speaking into a room faces whoever is present: strict filter.
        verdict = moderation.review(line, None, {"birthdate": None},
                                    maturity="strict")
        if not verdict.approved:
            result = {"status": "held", "reason": verdict.reason,
                      "spoken": None}
        else:
            result = {"status": "spoken", "spoken": line}
    elif skill is not None and body.command not in allowed:
        # A learned task: queued for the bridge with its pack procedure, so
        # the body (and the audit trail) knows exactly what was licensed.
        db.connect().execute(
            "UPDATE robots SET status='active' WHERE id=?", (robot_id,))
        result = {"status": "queued", "action": body.command,
                  "arg": body.arg, "skill": skill["title"],
                  "pack": skill["pack_title"],
                  "procedure": skill["procedure"]}
    else:
        # Motion/utility commands are queued for the vendor bridge; the status
        # flips so the UI can show the body doing something.
        active = body.command not in ("dock", "stop")
        db.connect().execute(
            "UPDATE robots SET status=? WHERE id=?",
            ("active" if active else "docked", robot_id))
        result = {"status": "queued", "action": body.command,
                  "arg": body.arg}

    conn = db.connect()
    conn.execute(
        "INSERT INTO robot_commands (id, robot_id, command, arg, result,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("cmd"), robot_id, body.command, body.arg,
         json.dumps(result), db.utcnow()))
    conn.commit()
    return {"robot_id": robot_id, "command": body.command, **result}


@router.get("/robots/{robot_id}/commands")
def robot_command_log(robot_id: str, request: Request) -> list[dict]:
    """Owner-only audit: everything this body has been told to do."""
    robot = _robot_or_404(robot_id)
    require_owner(robot["profile_id"], request)
    rows = db.connect().execute(
        "SELECT * FROM robot_commands WHERE robot_id=? ORDER BY created_at",
        (robot_id,)).fetchall()
    return [{**dict(r), "result": json.loads(r["result"] or "{}")}
            for r in rows]
