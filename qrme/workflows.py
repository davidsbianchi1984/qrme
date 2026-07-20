"""Autonomous multi-step workflows (claim 25, extended).

A single-shot task (``qrme/tasks.py``) reads scoped data, composes once, and
moderates. A **workflow** chains several such phases into a plan the profile
works through one step at a time — e.g. `research → draft → review → send →
confirm` — while:

- **carrying memory forward**: every phase sees the outputs of the phases
  before it (its "working memory"), so the profile builds on its own prior
  work instead of starting cold each step;
- **staying in character**: each phase is generated through the profile's
  persona prompt;
- **surviving across sessions**: the workflow is persisted between calls, so a
  phase that waits on external confirmation (`confirm`) pauses and resumes in a
  later session, exactly where it left off;
- **honoring revocable access**: vault reads run under the same revocable grant
  as single-shot tasks — revoke it mid-workflow and the next read-bearing phase
  fails.

Only phase *summaries/outputs* are kept as working memory; the raw vaulted
source content is used in-memory during the research phase and not retained.
"""

from __future__ import annotations

import json

from . import db, llm, moderation, persona

# The phases a plan may use. `confirm` is the one pausing phase: it waits for
# external input and resumes later.
PHASES = ("research", "draft", "review", "send", "confirm")
DEFAULT_PLAN = ["research", "draft", "review", "send", "confirm"]


def create(profile_id: str, goal: str, plan: list[str] | None,
           grant_id: str | None) -> dict:
    plan = plan or DEFAULT_PLAN
    unknown = [p for p in plan if p not in PHASES]
    if unknown:
        raise ValueError(f"unknown phase(s): {', '.join(unknown)}")
    if not plan:
        raise ValueError("a workflow needs at least one phase")
    conn = db.connect()
    wf_id = db.new_id("wfl")
    now = db.utcnow()
    conn.execute(
        "INSERT INTO workflows (id, profile_id, goal, plan, cursor, memory,"
        " status, grant_id, created_at, updated_at)"
        " VALUES (?,?,?,?,0,'{}','running',?,?,?)",
        (wf_id, profile_id, goal, json.dumps(plan), grant_id, now, now),
    )
    conn.commit()
    return get(profile_id, wf_id)


def get(profile_id: str, wf_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM workflows WHERE id=? AND profile_id=?",
        (wf_id, profile_id)).fetchone()
    return _hydrate(row) if row else None


def list_for(profile_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM workflows WHERE profile_id=? ORDER BY created_at, rowid",
        (profile_id,)).fetchall()
    return [_hydrate(r) for r in rows]


def _hydrate(row) -> dict:
    wf = dict(row)
    wf["plan"] = json.loads(wf["plan"])
    wf["memory"] = json.loads(wf["memory"])
    wf["next_phase"] = (wf["plan"][wf["cursor"]]
                        if wf["cursor"] < len(wf["plan"]) else None)
    return wf


def _save(wf_id: str, *, cursor: int, memory: dict, status: str,
          awaiting: str | None) -> None:
    conn = db.connect()
    conn.execute(
        "UPDATE workflows SET cursor=?, memory=?, status=?, awaiting=?,"
        " updated_at=? WHERE id=?",
        (cursor, json.dumps(memory), status, awaiting, db.utcnow(), wf_id),
    )
    conn.commit()


def _memory_block(memory: dict) -> str:
    if not memory:
        return ""
    parts = [f"[{phase}]\n{text}" for phase, text in memory.items()]
    return ("\n\nYour work on this so far (build on it and stay consistent):\n"
            + "\n\n".join(parts))


def _scoped_items(profile_id: str, grant_id: str | None, pdi) -> tuple[list, bool]:
    """Source items the workflow's grant permits, content resolved from the
    vault. Returns (items, grant_ok); grant_ok is False if a grant is set but
    revoked/unknown."""
    conn = db.connect()
    scope = ["*"]
    if grant_id is not None:
        grant = conn.execute("SELECT * FROM grants WHERE id=?",
                             (grant_id,)).fetchone()
        if grant is None or grant["revoked"]:
            return [], False
        scope = json.loads(grant["scope"])
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
    return items, True


# --------------------------------------------------------------------------- #
# phase handlers — each returns the text output stored as working memory
# --------------------------------------------------------------------------- #

def _generate(profile: dict, memory: dict, instruction: str, provider,
              sources=None) -> str:
    system = persona.build_system_prompt(profile, None, None, sources=sources)
    system += _memory_block(memory)
    system += "\n\n" + instruction
    return provider.generate(system, [{"role": "user", "content": "Continue."}])


def advance(profile: dict, wf: dict, pdi=None, cloud=None) -> dict:
    """Run the next phase of a workflow. Pausing phases set the workflow to
    ``awaiting_input``; call :func:`resume` to supply what they need."""
    profile_id = profile["id"]
    if wf["status"] not in ("running",):
        return {**wf, "note": f"workflow is {wf['status']}, not advancing"}

    phase = wf["plan"][wf["cursor"]]
    memory = dict(wf["memory"])
    provider = llm.get_provider(cloud=cloud)

    # `confirm` waits for the outside world before the workflow can finish.
    if phase == "confirm":
        _save(wf["id"], cursor=wf["cursor"], memory=memory,
              status="awaiting_input",
              awaiting="external confirmation that the deliverable was accepted")
        return get(profile_id, wf["id"])

    if phase == "research":
        items, grant_ok = _scoped_items(profile_id, wf["grant_id"], pdi)
        if not grant_ok:
            _save(wf["id"], cursor=wf["cursor"], memory=memory,
                  status="failed", awaiting=None)
            out = get(profile_id, wf["id"])
            out["note"] = "grant revoked or unknown; workflow halted"
            return out
        output = _generate(
            profile, memory,
            f"Task goal: {wf['goal']}. Phase — research: review your source "
            "material and write a concise briefing of the facts relevant to "
            "the goal.", provider, sources=items)

    elif phase == "draft":
        output = _generate(
            profile, memory,
            f"Task goal: {wf['goal']}. Phase — draft: using your research, "
            "write the deliverable in full.", provider)

    elif phase == "review":
        draft = memory.get("draft", "")
        verdict = moderation.review(draft, None, {"birthdate": None},
                                    maturity="strict")
        if not verdict.approved:
            memory["review"] = f"blocked: {verdict.reason}"
            _save(wf["id"], cursor=len(wf["plan"]), memory=memory,
                  status="failed", awaiting=None)
            return get(profile_id, wf["id"])
        output = _generate(
            profile, memory,
            f"Task goal: {wf['goal']}. Phase — review: critique your draft in "
            "one short paragraph and note it is ready to send.", provider)

    elif phase == "send":
        output = _generate(
            profile, memory,
            f"Task goal: {wf['goal']}. Phase — send: produce the final, "
            "polished deliverable exactly as it should go out.", provider)

    else:                                   # pragma: no cover - guarded at create
        raise ValueError(f"unknown phase {phase}")

    memory[phase] = output
    cursor = wf["cursor"] + 1
    status = "completed" if cursor >= len(wf["plan"]) else "running"
    _save(wf["id"], cursor=cursor, memory=memory, status=status, awaiting=None)
    return get(profile_id, wf["id"])


def resume(profile_id: str, wf: dict, supplied: str) -> dict:
    """Supply the input a paused (`awaiting_input`) workflow was waiting on —
    typically in a later session — and move past the pausing phase."""
    if wf["status"] != "awaiting_input":
        raise ValueError("workflow is not awaiting input")
    phase = wf["plan"][wf["cursor"]]
    memory = dict(wf["memory"])
    memory[phase] = f"confirmed: {supplied}"
    cursor = wf["cursor"] + 1
    status = "completed" if cursor >= len(wf["plan"]) else "running"
    _save(wf["id"], cursor=cursor, memory=memory, status=status, awaiting=None)
    return get(profile_id, wf["id"])


def cancel(profile_id: str, wf: dict) -> dict:
    _save(wf["id"], cursor=wf["cursor"], memory=wf["memory"],
          status="cancelled", awaiting=None)
    return get(profile_id, wf["id"])
