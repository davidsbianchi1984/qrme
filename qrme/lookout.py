"""The lookout: a page the vault keeps fresh, and the profile speaks from.

JIM's lookout watches a page for a person; this is QRME's twin with the
payoff turned toward conversation. An owner plants "keep an eye on this
page" as one standing plan in the vault (PDI 0.88's appointments), whose
single `fetch.render` step re-seals the current capture every cycle — the page as a person meets it, not the shell the server sends — and
the profile *answers from* that capture: the freshest reading of the
watched pages rides the chat prompt, so a persona whose restaurant menu
changed this morning speaks this morning's menu, not its sources'
snapshot.

    asked     can a profile stay current on a page
    mattered  who does the watching, and where the page lives

The resident does the watching, from inside the facility; QRME never
does, and what leaves QRME is the URL once, at planting.

## The rules, inherited from the JIM round and the study errands

**Consent before the web.** Planting requires the profile's standing
`study_the_web` privilege — the same consent the excursions ask for,
because the resident leaves its host on this profile's behalf.

**Writes are plan-gated; reads and deletes keep the real vault.**
Planting seals things and takes the write vault; the list, the capture
read-back, the prompt block and the drop take `app.state.pdi`, because
an owner who moved to Free still has lookouts to see, read and stop —
and a profile whose plan lapsed keeps speaking from what was captured.

**The ledger lets go only after the vault did.** A drop cancels the
standing task first, then unseals the capture, then deletes the local
row. Erasure walks the same path for every lookout the profile has.

**Honesty at every edge.** No vault, an older tandem, an unreached
tandem: each answers in words, never a pretend success — and the prompt
block simply contributes nothing when nothing can be read, because a
turn that lands without the pages beats a turn refused for them.
"""

from __future__ import annotations

import json

from . import db, privileges

#: The vault key a lookout's capture lives under: position 01 of the one-step
#: plan, re-sealed by the resident every cycle (pdi/resident.py `_tool_fetch`).
_CAPTURE = "resident/{task_id}/01-fetch"

#: The interval window mirrors PDI's own, so the refusal is local,
#: translatable, and identical to what the tandem would say.
MIN_HOURS, MAX_HOURS = 0.25, 744

#: How much of a capture one read returns — a reading, not an archive.
PAGE_CAP = 20000

#: How the captures ride the prompt: the latest few pages, each at a
#: digest's length. A prompt full of pages is a profile that stops
#: noticing the person in front of it.
PROMPT_PAGES = 3
PROMPT_CAP = 700


def capture_key(task_id: str) -> str:
    return _CAPTURE.format(task_id=task_id)


def plant(profile_id: str, url: str, every_hours: float, pdi=None) -> dict:
    """One standing appointment in the vault, one ledger row here.

    `privileges.require` raises `NotChosen` for the router's 403 — the
    same chokepoint the excursions walk through, so a second caller
    cannot forget the consent.
    """
    privileges.require(profile_id, "study_the_web")
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        return {"planted": False, "why": "a lookout needs an http(s) url"}
    try:
        every_hours = float(every_hours)
    except (TypeError, ValueError):
        return {"planted": False,
                "why": "a lookout repeats on a number of hours"}
    if not MIN_HOURS <= every_hours <= MAX_HOURS:
        return {"planted": False,
                "why": "a lookout repeats between a quarter-hour and a month"}
    if pdi is None:
        return {"planted": False, "why": "no vault for this plan"}
    try:
        task = pdi.resident_stand(
            goal=f"lookout: {url}",
            steps=[{"tool": "fetch.render", "args": {"url": url}}],
            every_hours=every_hours)
    except Exception as exc:  # noqa: BLE001 — said, never crashed through
        return {"planted": False, "why": f"{type(exc).__name__}: {exc}"[:200]}
    if task is None:
        return {"planted": False,
                "why": "the vault has no standing tasks (older PDI)"}
    conn = db.connect()
    lookout_id = db.new_id("lkt")
    conn.execute(
        "INSERT INTO lookouts (id, profile_id, url, every_hours, task_id,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (lookout_id, profile_id, url, every_hours, task["id"], db.utcnow()))
    conn.commit()
    return {"planted": True, "id": lookout_id, "url": url,
            "every_hours": every_hours, "task_id": task["id"],
            "next_run_at": task.get("next_run_at")}


def watches(profile_id: str, pdi=None) -> dict:
    """This profile's lookouts, with what the vault says about each —
    `readable: false` when the tandem could not be asked, because a list
    that invents statuses is worse than one that says so."""
    rows = db.connect().execute(
        "SELECT * FROM lookouts WHERE profile_id=? ORDER BY created_at,"
        " rowid", (profile_id,)).fetchall()
    statuses, readable = {}, pdi is not None
    if pdi is not None and rows:
        try:
            statuses = {t["id"]: t for t in pdi.resident_tasks()}
        except Exception:  # noqa: BLE001
            readable = False
    out = []
    for r in rows:
        task = statuses.get(r["task_id"], {})
        # When the page last actually changed, from the capture's own
        # fingerprint history (PDI 0.89's fetch) — None when the tandem
        # cannot be read, nothing was fetched yet, or the capture
        # predates fingerprints. Absence stays absence, never a guess.
        sealed = _capture(pdi, r["task_id"]) if pdi is not None else None
        out.append({"id": r["id"], "url": r["url"],
                    "every_hours": r["every_hours"],
                    "status": task.get("status"),
                    "next_run_at": task.get("next_run_at"),
                    "changed_at": (sealed or {}).get("changed_at"),
                    "trouble": _trouble(pdi, r["task_id"]),
                    "created_at": r["created_at"]})
    return {"lookouts": out, "readable": readable}


def _trouble(pdi, task_id: str) -> str | None:
    """Why the watching last failed, from the vault's runs ledger
    (PDI 0.89) — the latest round's note when that round failed, else
    None. None also for an older PDI or an unreached one: absence stays
    absence, and a lookout in trouble should not make the list fail."""
    runs_door = getattr(pdi, "resident_runs", None)
    if runs_door is None:
        return None
    try:
        rounds = runs_door(task_id)
    except Exception:  # noqa: BLE001
        return None
    if not rounds:
        return None
    latest = rounds[0]
    if latest.get("status") != "failed":
        return None
    return latest.get("note")


def _row(profile_id: str, lookout_id: str):
    return db.connect().execute(
        "SELECT * FROM lookouts WHERE id=? AND profile_id=?",
        (lookout_id, profile_id)).fetchone()


def _capture(pdi, task_id: str) -> dict | None:
    try:
        raw = pdi.get(capture_key(task_id))
    except Exception:  # noqa: BLE001
        return None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


def page(profile_id: str, lookout_id: str, pdi=None) -> dict | None:
    """The current capture, read back from the seal. None: no such
    lookout. `readable: false`: the lookout stands but the tandem could
    not be reached, or the resident has not fetched yet."""
    row = _row(profile_id, lookout_id)
    if row is None:
        return None
    out = {"id": row["id"], "url": row["url"], "readable": False,
           "fetched_at": None, "changed_at": None, "chars": 0, "text": None}
    if pdi is None:
        return out
    sealed = _capture(pdi, row["task_id"])
    if sealed is None:
        return out
    text = sealed.get("text") or ""
    out.update({"readable": True, "fetched_at": sealed.get("fetched_at"),
                "changed_at": sealed.get("changed_at"),
                "chars": len(text), "text": text[:PAGE_CAP]})
    return out


def prompt_block(profile_id: str, pdi=None) -> str | None:
    """The watched pages as their current captures, worded for the prompt
    — context the model may draw on, never an instruction, and honest
    about its age. Contributes nothing rather than failing: a turn that
    lands without the pages beats a turn refused for them."""
    if pdi is None:
        return None
    rows = db.connect().execute(
        "SELECT * FROM lookouts WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (profile_id, PROMPT_PAGES)).fetchall()
    parts = []
    for r in rows:
        sealed = _capture(pdi, r["task_id"])
        if sealed is None:
            continue
        text = (sealed.get("text") or "").strip()
        if not text:
            continue
        when = f"captured {sealed.get('fetched_at')}"
        if sealed.get("changed_at"):
            when += f", last changed {sealed['changed_at']}"
        parts.append(f"{r['url']} ({when}):\n" + text[:PROMPT_CAP])
    if not parts:
        return None
    return ("Pages you keep an eye on for your owner, as their current "
            "captures — draw on them when they are relevant, say when a "
            "page did not carry an answer, and never present a capture as "
            "older or newer than its date:\n\n" + "\n\n".join(parts))


def drop(profile_id: str, lookout_id: str, pdi=None) -> dict | None:
    """Stop the watching the whole way: the appointment, the seal, the
    row — in that order, because a row whose appointment still stands
    belongs on the list, not orphaned. None: no such lookout."""
    row = _row(profile_id, lookout_id)
    if row is None:
        return None
    if pdi is None:
        return {"removed": False, "why": "no vault configured"}
    try:
        pdi.resident_cancel(row["task_id"])
        pdi.delete(capture_key(row["task_id"]))
    except Exception as exc:  # noqa: BLE001
        return {"removed": False,
                "why": f"{type(exc).__name__}: {exc}"[:200]}
    conn = db.connect()
    conn.execute("DELETE FROM lookouts WHERE id=? AND profile_id=?",
                 (lookout_id, profile_id))
    conn.commit()
    return {"removed": True, "id": lookout_id}


def drop_all(profile_id: str, pdi=None) -> int | None:
    """Erasure's call: every appointment cancelled, every capture
    unsealed. None when the tandem could not be reached — the erasure
    answer says so, and the rows die with the profile's tables either
    way."""
    rows = db.connect().execute(
        "SELECT task_id FROM lookouts WHERE profile_id=?",
        (profile_id,)).fetchall()
    if pdi is None:
        return None
    cancelled = 0
    try:
        for r in rows:
            if pdi.resident_cancel(r["task_id"]):
                cancelled += 1
            pdi.delete(capture_key(r["task_id"]))
    except Exception:  # noqa: BLE001
        return None
    return cancelled
