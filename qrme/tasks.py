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

from . import db, llm, moderation, persona


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
    return {"id": grant_id, "token": token, "scope": scope or ["*"],
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


def run(profile: dict, kind: str, topic: str, grant_token: str,
        pdi=None) -> dict:
    """Execute a multi-step task under a revocable grant."""
    profile_id = profile["id"]
    steps: list[dict] = []

    # Step 1 — authorization: the grant must exist and not be revoked.
    grant = _grant_for(profile_id, grant_token)
    if grant is None or grant["revoked"]:
        return {"status": "failed", "reason": "grant revoked or unknown",
                "steps": [{"step": "grant_check", "ok": False}]}
    scope = json.loads(grant["scope"])
    steps.append({"step": "grant_check", "ok": True, "grant_id": grant["id"]})

    # Step 2 — scoped vault read. Raw content is used in-memory only.
    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM source_items WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC", (profile_id,)).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        if scope != ["*"] and item["id"] not in scope:
            continue
        if item["pdi_key"] and pdi is not None:
            raw = pdi.get(item["pdi_key"])
            item["content"] = json.loads(raw)["content"] if raw else None
        items.append(item)
    steps.append({"step": "vault_read", "items": len(items),
                  "vaulted": sum(1 for i in items if i["pdi_key"])})

    # Step 3 — compose in persona, grounded in the scoped material.
    system = persona.build_system_prompt(profile, None, None, sources=items)
    system += (f"\n\nExecute this task autonomously: {kind} — {topic}. "
               "Produce the finished output only.")
    output = llm.get_provider().generate(
        system, [{"role": "user", "content": "Execute the task."}])
    steps.append({"step": "compose", "chars": len(output)})

    # Step 4 — moderation (widest audience → strict).
    verdict = moderation.review(output, None, {"birthdate": None},
                                maturity="strict")
    status = "completed" if verdict.approved else "failed"
    steps.append({"step": "moderation",
                  "result": "approved" if verdict.approved else verdict.reason})

    task_id = db.new_id("tsk")
    conn.execute(
        "INSERT INTO tasks (id, profile_id, kind, grant_id, status, steps,"
        " output, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (task_id, profile_id, kind, grant["id"], status, json.dumps(steps),
         output if verdict.approved else None, db.utcnow()),
    )
    conn.commit()
    return {"id": task_id, "status": status, "steps": steps,
            "output": output if verdict.approved else None}


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
