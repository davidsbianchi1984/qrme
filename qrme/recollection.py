"""What a profile remembers by meaning, sealed in the vault.

`remembrance.py` already keeps a friendship from resetting at message
thirty-one: turns older than the window are distilled into a running
summary, one per profile-and-interactor pair. A distillate is a timeline,
though — it remembers *forward*. Ask about the thing mentioned once in
March and the summary may have folded it into a clause or out of
existence.

This is the other axis. PDI's resident intelligence (0.86.0) gave the
vault an embedding index that stores a hash of the text and never the
text; here, each thing a person says to a profile is **sealed** into the
tandem AES-256-GCM and **embedded** under the same key, so the reply that
matters can find the moment that is *about* it — by meaning, however long
ago it was said.

    asked     does the profile remember this conversation
    mattered  can it find the earlier moment this question is about

## The rules, inherited from the JIM round and one stricter

**Memory never breaks the doing.** Every function returns rather than
raises: a chat turn that lands and is not remembered beats a turn refused
because the tandem was down. What happened is said in the return.

**No vault, no memory, no pretending.** The gate is the *plan*, through
`storage.vault_for` — free is platform custody over plain HTTPS, and a
free account's turns are not sealed into a vault it holds no key to.
Unconfigured, unpaid, offline, or an older PDI without the resident: the
profile answers exactly as before, and the reason is written down.

**One pair's memories.** JIM filtered by user; here the prefix carries
both the profile *and the interactor* — `qrme/{profile}/memory/{who}/` —
because one profile talks to many people, and what Alice told it must
never surface in its reply to Bob. Recall drops any match outside the
pair's prefix before it fetches a word.

**Erasure knows every key.** Each seal writes a `recollections` ledger
row beside it; the profile-erasure sweep reads `pdi_key` columns, and
this table carries one — the lesson the JIM round learned mid-flight,
applied here before the first key was ever cut.
"""

from __future__ import annotations

import json

from . import db

#: A memory is a line, not a transcript — recall folds these into a prompt,
#: and a prompt full of pages is a profile that stops noticing what is in
#: front of it.
MAX_LINE = 400

#: How many remembered lines one reply may carry.
RECALLED = 3


def _key(profile_id: str, interactor_id: str, ref: str) -> str:
    return f"qrme/{profile_id}/memory/{interactor_id}/{ref}"


def remember(pdi, profile_id: str, interactor_id: str, ref: str,
             text: str) -> dict:
    """Seal one moment, index it, and write the ledger row erasure reads."""
    text = (text or "").strip()[:MAX_LINE]
    if pdi is None or not text:
        return {"remembered": False,
                "why": "no vault for this plan" if pdi is None
                else "nothing said"}
    key = _key(profile_id, interactor_id, ref)
    try:
        pdi.put(key, json.dumps({"line": text, "at": db.utcnow()}))
        conn = db.connect()
        conn.execute(
            "INSERT OR REPLACE INTO recollections (id, profile_id,"
            " interactor_id, pdi_key, created_at) VALUES (?,?,?,?,?)",
            (ref, profile_id, interactor_id, key, db.utcnow()))
        conn.commit()
        indexed = pdi.resident_embed(key, text)
    except Exception as exc:  # noqa: BLE001 — memory never breaks the doing
        return {"remembered": False,
                "why": f"{type(exc).__name__}: {exc}"[:200]}
    if not indexed:
        return {"remembered": False, "why": "the vault has no memory index"}
    return {"remembered": True, "key": key}


def recall(pdi, profile_id: str, interactor_id: str, query: str,
           top_k: int = RECALLED) -> list[dict]:
    """The moments nearest this question — this pair's only."""
    query = (query or "").strip()
    if pdi is None or not query:
        return []
    prefix = f"qrme/{profile_id}/memory/{interactor_id}/"
    try:
        matches = pdi.resident_search(query, top_k=top_k * 4)
    except Exception:  # noqa: BLE001
        return []
    out = []
    for m in matches:
        if not m.get("key", "").startswith(prefix):
            continue
        try:
            raw = pdi.get(m["key"])
        except Exception:  # noqa: BLE001
            continue
        if not raw:
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        out.append({"line": entry.get("line", ""), "score": m.get("score")})
        if len(out) >= top_k:
            break
    return out


def chat_block(pdi, profile_id: str, interactor_id: str,
               message: str) -> str | None:
    """Recall, worded for the prompt — beside the remembrance's distillate,
    attributed as memory the profile may draw on, never an instruction."""
    found = recall(pdi, profile_id, interactor_id, message)
    lines = [m["line"] for m in found if m["line"]]
    if not lines:
        return None
    return ("Moments you remember this person telling you, from further "
            "back, found because they are close to what was just said:\n- "
            + "\n- ".join(lines))


def shelf(pdi, profile_id: str, interactor_id: str) -> dict:
    """Every sealed moment this pair holds, read back.

    The refs come from the `recollections` ledger — the same rows the
    erasure sweep walks — and the lines from the vault, so the answer is
    exactly what recall can actually surface, not a claim about it. A
    tandem that cannot be reached answers `readable: false` with whatever
    refs exist, because "I hold twelve moments I cannot show you right
    now" and "I hold nothing" are different answers. The pair scoping is
    in the SQL: Bob's shelf never lists what Alice said.
    """
    rows = db.connect().execute(
        "SELECT id, pdi_key, created_at FROM recollections"
        " WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at, rowid", (profile_id, interactor_id)).fetchall()
    moments, readable = [], pdi is not None
    for r in rows:
        entry = {}
        if pdi is not None:
            try:
                raw = pdi.get(r["pdi_key"])
                entry = json.loads(raw) if raw else {}
            except Exception:  # noqa: BLE001
                readable = False
        moments.append({"ref": r["id"], "line": entry.get("line"),
                        "at": entry.get("at")})
    return {"memories": moments, "readable": readable}


def forget(pdi, profile_id: str, interactor_id: str, ref: str) -> dict:
    """Unmake one sealed moment: the vector, the seal, and the ledger row
    — so a forgotten memory stops being findable, not merely stops being
    readable. The chat turn itself is not touched; striking the
    transcript stays at its own door. Non-fatal like everything here."""
    if pdi is None:
        return {"forgotten": False, "why": "no vault for this plan"}
    key = _key(profile_id, interactor_id, ref)
    try:
        removed = pdi.resident_forget(key)
        pdi.delete(key)
        conn = db.connect()
        conn.execute(
            "DELETE FROM recollections WHERE id=? AND profile_id=?"
            " AND interactor_id=?", (ref, profile_id, interactor_id))
        conn.commit()
    except Exception as exc:  # noqa: BLE001
        return {"forgotten": False,
                "why": f"{type(exc).__name__}: {exc}"[:200]}
    return {"forgotten": True, "vectors_removed": removed}


def forget_pair(pdi, profile_id: str, interactor_id: str) -> int | None:
    """The pair's erase-all: every vector, seal and ledger row under this
    conversation's memory prefix, in one sweep — called beside the local
    deletes when somebody clears a whole memory. None when the tandem
    could not be reached; the ledger rows are then left standing, because
    a row whose seal the vault never let go of belongs on the shelf, not
    orphaned. Each row goes only after its seal did."""
    if pdi is None:
        return None
    try:
        removed = pdi.resident_forget(
            f"qrme/{profile_id}/memory/{interactor_id}/", prefix=True)
        conn = db.connect()
        rows = conn.execute(
            "SELECT id, pdi_key FROM recollections WHERE profile_id=?"
            " AND interactor_id=?", (profile_id, interactor_id)).fetchall()
        for r in rows:
            pdi.delete(r["pdi_key"])
            conn.execute(
                "DELETE FROM recollections WHERE id=? AND profile_id=?"
                " AND interactor_id=?", (r["id"], profile_id, interactor_id))
        conn.commit()
        return removed
    except Exception:  # noqa: BLE001
        return None


def forget_profile(pdi, profile_id: str) -> int | None:
    """Erasure's call: every vector under this profile's memory prefix, in
    one trip. None when the tandem could not be reached — the erasure
    answer says so rather than counting what it cannot see. The sealed
    texts and the `recollections` ledger rows are taken by the erasure
    sweep itself; this is the half only the resident can do."""
    if pdi is None:
        return None
    try:
        return pdi.resident_forget(f"qrme/{profile_id}/memory/", prefix=True)
    except Exception:  # noqa: BLE001
        return None


def tabulate(pdi, dataset: str, rows: list[dict],
             source_ref: str | None = None) -> bool:
    """Structured results into a vault table the PDI console can query —
    the study ledger writing itself into the tenant's own shelf."""
    if pdi is None or not rows:
        return False
    try:
        return pdi.resident_tabulate(dataset, rows, source_ref=source_ref)
    except Exception:  # noqa: BLE001
        return False
