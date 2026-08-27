"""Autonomous multi-step tasks over the private data vault (claim 25).

A profile can execute a multi-step task — read scoped source material,
compose an output in persona, pass moderation — using a **revocable access
grant** instead of standing access. The grant scopes which vaulted items the
task may read; revoking it kills future task runs instantly. The task log
records step summaries and counts only, never the raw vaulted data, so the
profile executes without retaining what it read.
"""

from __future__ import annotations

import json
import secrets

from . import db, llm, moderation, persona, privileges, watermark


def create_grant(profile_id: str, scope: list[str] | None) -> dict:
    conn = db.connect()
    grant_id = db.new_id("grt")
    token = f"grt_{secrets.token_urlsafe(24)}"
    conn.execute(
        "INSERT INTO grants (id, profile_id, scope, token, revoked, created_at)"
        " VALUES (?,?,?,?,0,?)",
        (grant_id, profile_id, json.dumps(scope or ["*"]), token, db.utcnow()),
    )
    conn.commit()
    return {"id": grant_id, "token": token, "scopes": scope or ["*"],
            "revoked": False}


def revoke_grant(grant_id: str) -> bool:
    conn = db.connect()
    changed = conn.execute(
        "UPDATE grants SET revoked=1 WHERE id=?", (grant_id,)).rowcount
    conn.commit()
    return changed > 0


def _grant_for(profile_id: str, token: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM grants WHERE profile_id=? AND token=?",
        (profile_id, token)).fetchone()
    return dict(row) if row else None


class NothingGranted(ValueError):
    """The grant does not exist, or has been revoked. Carries text for a
    person rather than a status for a caller."""


def scoped_items(profile_id: str, grant_token: str, pdi=None) -> list[dict]:
    """Exactly the vaulted material this grant lets a profile read.

    One function decides what a grant means, and both callers go through it —
    the autonomous task below, and the briefing a profile prepares for a real
    provider. Two readings of a scope is one reading too many: the whole value
    of a revocable grant is that revoking it stops *everything*, and a second
    place interpreting `scope` is a second place that can interpret it
    generously.
    """
    grant = _grant_for(profile_id, grant_token)
    if grant is None or grant["revoked"]:
        raise NothingGranted(
            "that grant is unknown or has been revoked — nothing can be read "
            "with it")
    scope = json.loads(grant["scope"])
    out = []
    for row in db.connect().execute(
            "SELECT * FROM source_items WHERE profile_id=?"
            " ORDER BY created_at DESC, rowid DESC", (profile_id,)).fetchall():
        item = dict(row)
        if scope != ["*"] and item["id"] not in scope:
            continue
        if item["pdi_key"] and pdi is not None:
            raw = pdi.get(item["pdi_key"])
            item["content"] = json.loads(raw)["content"] if raw else None
        out.append(item)
    return out


def run(profile: dict, kind: str, topic: str, grant_token: str,
        pdi=None, cloud=None) -> dict:
    """Execute a multi-step task under a revocable grant."""
    profile_id = profile["id"]
    # A grant says *what may be read*. The privilege says *whether this agent
    # works unattended at all* — two different yeses, and a revoked grant has
    # never been an answer to the second.
    privileges.require(profile_id, "run_jobs")
    steps: list[dict] = []

    # Step 1 — authorization: the grant must exist and not be revoked.
    grant = _grant_for(profile_id, grant_token)
    if grant is None or grant["revoked"]:
        return {"status": "failed", "reason": "grant revoked or unknown",
                "steps": [{"step": "grant_check", "ok": False}]}
    steps.append({"step": "grant_check", "ok": True, "grant_id": grant["id"]})

    # Step 2 — scoped vault read. Raw content is used in-memory only.
    items = scoped_items(profile_id, grant_token, pdi)
    steps.append({"step": "vault_read", "items": len(items),
                  "vaulted": sum(1 for i in items if i["pdi_key"])})

    # Step 3 — compose in persona, grounded in the scoped material.
    system = persona.build_system_prompt(profile, None, None, sources=items)
    system += (f"\n\nExecute this task autonomously: {kind} — {topic}. "
               "Produce the finished output only.")
    output = llm.get_provider(cloud=cloud).generate(
        system, [{"role": "user", "content": "Execute the task."}])
    steps.append({"step": "compose", "chars": len(output)})

    # Step 4 — moderation (widest audience → strict).
    verdict = moderation.review(output, None, {"birthdate": None},
                                maturity="strict")
    status = "completed" if verdict.approved else "failed"
    steps.append({"step": "moderation",
                  "result": "approved" if verdict.approved else verdict.reason})

    # An autonomous task's finished output is AI-composed work: stamped.
    credential = (watermark.stamp(profile_id, "task-output", output)
                  if verdict.approved else None)
    task_id = db.new_id("tsk")
    conn = db.connect()
    conn.execute(
        "INSERT INTO tasks (id, profile_id, kind, grant_id, status, steps,"
        " output, watermark_id, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (task_id, profile_id, kind, grant["id"], status, json.dumps(steps),
         output if verdict.approved else None,
         credential["watermark_id"] if credential else None, db.utcnow()),
    )
    conn.commit()
    return {"id": task_id, "status": status, "steps": steps,
            "output": output if verdict.approved else None,
            "watermark": credential}


def list_tasks(profile_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM tasks WHERE profile_id=? ORDER BY created_at, rowid",
        (profile_id,)).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["steps"] = json.loads(item["steps"])
        out.append(item)
    return out
