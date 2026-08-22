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

**One pair's memories, kept on the person's side.** One profile talks to
many people, and what Alice told it must never surface in its reply to
Bob. That rule has not changed; where the memory *lives* has.

It used to be `qrme/{profile}/memory/{who}/` — the profile at the root,
gated on the profile owner's plan. So whether your conversation was
remembered depended on whether somebody else was paying for it, and the
record sat in their account, under their key, where you could not read it,
could not take it, and would lose it the day they stopped paying. A memory
of a conversation is worth keeping because the person comes back; it
belongs on the side of the person who might. It is
`qrme/{who}/memory/{profile}/` now, gated on theirs.

**And nothing reads that shape.** The `recollections` ledger records every
key as its seal is cut, so it is already a complete index of which key
belongs to which pair — recall filters against it and both erasures walk
it. An index that says so outright beats one inferred from how a string
was spelled, and it is what lets the shape change without stranding a
single conversation this product has already had.

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
    """Where a new moment is sealed. The **person** is the root.

    It used to be the profile — `qrme/{profile}/memory/{who}/{ref}` — which
    put a record of your conversation inside somebody else's account. Nothing
    reads this shape any more (see `_pair_keys`), so old keys minted the old
    way keep working exactly as they did; only new ones land under the person
    who said the words.
    """
    return f"qrme/{interactor_id}/memory/{profile_id}/{ref}"


def _pair_keys(profile_id: str, interactor_id: str) -> dict[str, str]:
    """{pdi_key: ref} for every moment this pair holds, from the ledger.

    The `recollections` table records the key of every seal as it is cut, so
    it is already a complete index of which key belongs to which pair — and
    an index that says so outright beats one inferred from how a string was
    spelled. Reading it here is what lets the key shape change without
    stranding a single memory that was sealed under the old one: a filter
    that matched on the prefix would have quietly stopped finding every
    conversation this product has already had.

        asked     which of these keys are ours
        mattered  is that still true after the shape changed
    """
    rows = db.connect().execute(
        "SELECT id, pdi_key, posture FROM recollections"
        " WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id)).fetchall()
    return {(r["pdi_key"] or _hosted_ref(profile_id, interactor_id, r["id"])):
            r["id"] for r in rows}


def remember(pdi, profile_id: str, interactor_id: str, ref: str,
             text: str, posture: str = "vault") -> dict:
    """Keep one moment, index it, and write the ledger row erasure reads.

    Two arrangements, and the row records which one it landed under.

    **vault** — sealed in the tandem under a key the person can hold, and
    embedded. What a paid plan buys.

    **open_cloud** — the words in this deployment's own database, hosted by
    the operator, and contributed to the shared model as the tier's terms
    say. What the free plan is: somebody who is not paying for privacy
    still gets a profile that remembers them, because a memory is only
    worth keeping if the person comes back and a free plan that forgets
    everything is a product nobody returns to.

        asked     was this kept
        mattered  under which arrangement, and does the row still say so
                  after the plan changes

    The posture is written on the row rather than inferred later from the
    plan. Somebody on free this year and basic next year has rows that were
    genuinely hosted; reading their current plan would describe those
    retroactively as sealed and private, which upgrading does not make true.

    The index is the same either way where a tandem is reachable, and that
    costs nothing: the resident stores a hash of the text and never the
    text, so embedding a hosted memory hands over no more than embedding a
    sealed one. A deployment with no tandem still keeps hosted memories —
    they are in its own database — and simply recalls them by recency.
    """
    text = (text or "").strip()[:MAX_LINE]
    if not text:
        return {"remembered": False, "why": "nothing said"}
    if posture == "vault" and pdi is None:
        return {"remembered": False, "why": "no vault for this plan"}
    hosted = posture != "vault"
    key = "" if hosted else _key(profile_id, interactor_id, ref)
    try:
        if not hosted:
            pdi.put(key, json.dumps({"line": text, "at": db.utcnow()}))
        conn = db.connect()
        conn.execute(
            "INSERT OR REPLACE INTO recollections (id, profile_id,"
            " interactor_id, pdi_key, created_at, posture, line)"
            " VALUES (?,?,?,?,?,?,?)",
            (ref, profile_id, interactor_id, key, db.utcnow(), posture,
             text if hosted else None))
        conn.commit()
        # A hosted memory is already kept — it is in this database. The
        # index only decides whether it can be found by MEANING, so a
        # tandem that is absent or refuses costs recall-by-meaning and
        # never the memory itself.
        indexed = True
        if pdi is not None:
            indexed = bool(pdi.resident_embed(
                key or _hosted_ref(profile_id, interactor_id, ref), text))
    except Exception as exc:  # noqa: BLE001 — memory never breaks the doing
        return {"remembered": False,
                "why": f"{type(exc).__name__}: {exc}"[:200]}
    if not indexed and not hosted:
        return {"remembered": False, "why": "the vault has no memory index"}
    return {"remembered": True, "key": key, "posture": posture,
            "findable_by_meaning": indexed}


def contribute(cloud, profile_id: str, interactor_id: str, ref: str,
               text: str) -> bool:
    """Send one hosted moment to the shared model, carrying no identity.

    Only ever called for `open_cloud` rows. A sealed memory is never
    contributed whatever any switch says: a private plan is private, and
    the whole of what it buys is that this function does not run.

        asked     may this improve the shared model
        mattered  can anything in it point back at the person

    What leaves is the sentence and an opaque ref. No profile id, no
    interactor id, no display name, no account — the ref is meaningless at
    the gateway and meaningful only in `contribution_log` here, which is
    what lets a revocation delete the right item without ever telling the
    gateway whose it was.

    Non-fatal, like everything in this module: a conversation that lands
    and is not contributed beats a conversation refused because a gateway
    was down.
    """
    if cloud is None or not text:
        return False
    row = db.connect().execute(
        "SELECT contributes FROM interactors WHERE id=?",
        (interactor_id,)).fetchone()
    if row is None or not row["contributes"]:
        return False
    token = db.new_id("ctb")
    payload = {
        "ref": token,
        "source": "qrme",
        "kind": "held_moment",
        "quality": "hosted",
        "exchange": {"said": text},
    }
    try:
        if not cloud.contribute(payload):
            return False
        conn = db.connect()
        conn.execute(
            "INSERT INTO contribution_log (ref, profile_id, interactor_id,"
            " payload, contributed_at) VALUES (?,?,?,?,?)",
            (token, profile_id, interactor_id, json.dumps(payload),
             db.utcnow()))
        conn.commit()
    except Exception:  # noqa: BLE001
        return False
    return True


def stop_contributing(cloud, interactor_id: str) -> dict:
    """Turn it off, and pull back what already went.

    "You can turn it off" would be a thin promise if it only meant *from
    now on*. The refs carry no identity, so the gateway can be asked to
    drop each item without ever being told whose it was — the machinery
    the per-profile revocation already uses, pointed at a person.

    The flag goes down whatever the gateway says. A deployment that cannot
    reach the gateway must still stop contributing, and the answer says
    plainly whether the past was actually reached.
    """
    conn = db.connect()
    conn.execute("UPDATE interactors SET contributes=0 WHERE id=?",
                 (interactor_id,))
    refs = [r["ref"] for r in conn.execute(
        "SELECT ref FROM contribution_log WHERE interactor_id=? AND revoked=0",
        (interactor_id,)).fetchall()]
    if not refs:
        deleted = True                      # nothing ever left
    elif cloud is None:
        deleted = False                     # nothing to ask; the flag is down
    else:
        try:
            deleted = bool(cloud.revoke_contributions(refs))
        except Exception:  # noqa: BLE001
            deleted = False
    if deleted:
        conn.execute(
            "UPDATE contribution_log SET revoked=1 WHERE interactor_id=?",
            (interactor_id,))
    conn.commit()
    return {"contributes": False, "revoked_count": len(refs),
            "deleted_at_gateway": deleted}


def contribution_state(interactor_id: str) -> dict:
    """Whether this person contributes, and how much has gone."""
    conn = db.connect()
    row = conn.execute("SELECT contributes FROM interactors WHERE id=?",
                       (interactor_id,)).fetchone()
    sent = conn.execute(
        "SELECT COUNT(*) AS n FROM contribution_log"
        " WHERE interactor_id=? AND revoked=0", (interactor_id,)).fetchone()
    return {"contributes": bool(row and row["contributes"]),
            "contributed_count": sent["n"] if sent else 0}


def _hosted_ref(profile_id: str, interactor_id: str, ref: str) -> str:
    """The index handle for a hosted memory.

    Shaped like a vault key so one index holds both, and deliberately NOT a
    vault key: nothing is sealed under it and `pdi.get` would find nothing
    there. `posture` is what the reading paths branch on, never this.
    """
    return f"qrme/{interactor_id}/hosted/{profile_id}/{ref}"


def recall(pdi, profile_id: str, interactor_id: str, query: str,
           top_k: int = RECALLED) -> list[dict]:
    """The moments nearest this question — this pair's only."""
    query = (query or "").strip()
    if pdi is None or not query:
        return []
    ours = _pair_keys(profile_id, interactor_id)
    if not ours:
        return []
    try:
        matches = pdi.resident_search(query, top_k=top_k * 4)
    except Exception:  # noqa: BLE001
        return []
    out = []
    for m in matches:
        # The pair rule, unchanged and now enforced against the ledger
        # rather than a prefix string: what Alice told it must never
        # surface in its reply to Bob.
        if m.get("key") not in ours:
            continue
        line = _line_of(ours[m["key"]], pdi, m["key"])
        if not line:
            continue
        out.append({"line": line, "score": m.get("score")})
        if len(out) >= top_k:
            break
    return out


def _line_of(ref: str, pdi, key: str) -> str:
    """The words of one memory, from wherever that memory actually lives.

    A hosted row carries them in this database; a sealed row carries them in
    the tandem under `pdi_key`. The row's own `posture` decides, which is why
    it is a column: asking the plan would answer for today rather than for
    the moment the memory was made.
    """
    row = db.connect().execute(
        "SELECT posture, line FROM recollections WHERE id=?", (ref,)).fetchone()
    if row is None:
        return ""
    if row["posture"] != "vault":
        return row["line"] or ""
    if pdi is None:
        return ""
    try:
        raw = pdi.get(key)
    except Exception:  # noqa: BLE001
        return ""
    if not raw:
        return ""
    try:
        return json.loads(raw).get("line", "")
    except ValueError:
        return ""


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
        "SELECT id, pdi_key, created_at, posture, line FROM recollections"
        " WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at, rowid", (profile_id, interactor_id)).fetchall()
    moments, readable = [], True
    for r in rows:
        # A hosted moment is readable whatever the tandem is doing: its
        # words are in this database. Only a sealed one depends on the
        # vault answering, and `readable: false` has always meant "I hold
        # things I cannot show you right now" rather than "I hold nothing".
        if r["posture"] != "vault":
            moments.append({"ref": r["id"], "line": r["line"],
                            "at": r["created_at"]})
            continue
        entry = {}
        if pdi is None:
            readable = False
        else:
            try:
                raw = pdi.get(r["pdi_key"])
                entry = json.loads(raw) if raw else {}
            except Exception:  # noqa: BLE001
                readable = False
        moments.append({"ref": r["id"], "line": entry.get("line"),
                        "at": entry.get("at")})
    return {"memories": moments, "readable": readable}


def theirs(pdi, interactor_id: str) -> dict:
    """Everything one **person** holds, across every profile they have
    talked to — including profiles that no longer exist.

    The door that makes "the user's record survives" true rather than
    merely accurate. Profile erasure stops taking these seals (see
    `ERASE_KEEPS`), and a record kept where its owner cannot reach it is
    not a record surviving, it is data being held. The only existing way
    in was `GET /profiles/{id}/memory/{who}`, which begins by looking the
    profile up — so the moment the profile went, so did the door.

        asked     does the person's record outlive the profile
        mattered  can they still get to it

    Grouped by profile, and each group says whether that profile is still
    there. `gone: true` is not an error state — it is a conversation whose
    other party has deleted themselves, which is exactly the case this
    exists for, and the person's own words are still their own words.

    The display name is read from the profile while there is one, and
    omitted rather than invented once there is not: a deleted profile's
    name is one of the profile's own words, and erasure took it.
    """
    conn = db.connect()
    rows = conn.execute(
        "SELECT r.id, r.profile_id, r.pdi_key, r.created_at, r.posture,"
        "       r.line, p.display_name AS name"
        "  FROM recollections r"
        "  LEFT JOIN profiles p ON p.id = r.profile_id"
        " WHERE r.interactor_id=?"
        " ORDER BY r.created_at, r.rowid", (interactor_id,)).fetchall()
    groups: dict[str, dict] = {}
    readable = True
    for r in rows:
        group = groups.setdefault(r["profile_id"], {
            "profile_id": r["profile_id"],
            "display_name": r["name"],
            "gone": r["name"] is None,
            "memories": [],
            # Said per conversation rather than per person, because a
            # person can hold both: what they said while on free is hosted
            # and contributed, and what they said after upgrading is
            # sealed. One badge over the lot would be false about half of
            # it, in whichever direction it leaned.
            "postures": [],
        })
        if r["posture"] not in group["postures"]:
            group["postures"].append(r["posture"])
        if r["posture"] != "vault":
            group["memories"].append({"ref": r["id"], "line": r["line"],
                                      "at": r["created_at"]})
            continue
        entry = {}
        if pdi is None:
            readable = False
        else:
            try:
                raw = pdi.get(r["pdi_key"])
                entry = json.loads(raw) if raw else {}
            except Exception:  # noqa: BLE001
                readable = False
        group["memories"].append({"ref": r["id"], "line": entry.get("line"),
                                  "at": entry.get("at")})
    return {"conversations": list(groups.values()), "readable": readable}


def forget(pdi, profile_id: str, interactor_id: str, ref: str) -> dict:
    """Unmake one sealed moment: the vector, the seal, and the ledger row
    — so a forgotten memory stops being findable, not merely stops being
    readable. The chat turn itself is not touched; striking the
    transcript stays at its own door. Non-fatal like everything here."""
    from . import letter
    letter.mark_forgotten(profile_id)
    if pdi is None:
        return {"forgotten": False, "why": "no vault for this plan"}
    # Read the key, never recompute it. `_key` mints where a NEW moment
    # goes; a moment sealed before the key changed shape lives where the
    # ledger says it lives. Recomputing here would have deleted a key that
    # does not exist, reported `forgotten: True`, and left the real seal
    # and its vector exactly where they were — a forgetting that forgets
    # nothing and says it worked.
    row = db.connect().execute(
        "SELECT pdi_key, posture FROM recollections WHERE id=? AND profile_id=?"
        " AND interactor_id=?", (ref, profile_id, interactor_id)).fetchone()
    if row is None:
        return {"forgotten": False, "why": "no such memory"}
    hosted = row["posture"] != "vault"
    key = row["pdi_key"] or _hosted_ref(profile_id, interactor_id, ref)
    try:
        removed = pdi.resident_forget(key)
        # Nothing is sealed under a hosted memory's handle, so there is no
        # record to delete — the words go with the ledger row below, which
        # is where they live.
        if not hosted:
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
    from . import letter
    letter.mark_forgotten(profile_id)
    if pdi is None:
        return None
    try:
        conn = db.connect()
        removed = 0
        for key, ref in _pair_keys(profile_id, interactor_id).items():
            removed += pdi.resident_forget(key) or 0
            # A hosted handle seals nothing; the words go with the row.
            if "/hosted/" not in key:
                pdi.delete(key)
            conn.execute(
                "DELETE FROM recollections WHERE id=? AND profile_id=?"
                " AND interactor_id=?", (ref, profile_id, interactor_id))
        conn.commit()
        return removed
    except Exception:  # noqa: BLE001
        return None


def forget_profile(pdi, profile_id: str) -> int | None:
    """Erasure's call: every vector this profile ever put in the index.

    None when the tandem could not be reached — the erasure answer says so
    rather than counting what it cannot see. The sealed texts and the
    `recollections` ledger rows are taken by the erasure sweep itself; this
    is the half only the resident can do.

    ## Why this walks keys instead of sweeping a prefix

    It used to be one trip: `resident_forget("qrme/{profile}/memory/",
    prefix=True)`. That was correct for exactly as long as the profile was
    the root of the key, and the moment a memory moved under the person who
    said it — which is the whole point of the change this arrived with —
    that prefix would have matched nothing at all.

    The failure would have been silent and would have looked like success.
    `resident_forget` returns a count, zero is a perfectly ordinary count,
    and erasure would have reported a clean sweep having deleted nothing.
    An erasure that quietly erases nothing is worse than one that fails
    loudly, because the second gets fixed.

        asked     did the vectors go
        mattered  would we know if they had not

    So the ledger says which keys exist and each one is forgotten by name.
    That also makes this correct across the change rather than after it:
    keys minted under the old shape are in the ledger too, and go with the
    rest.
    """
    if pdi is None:
        return None
    try:
        rows = db.connect().execute(
            "SELECT id, interactor_id, pdi_key FROM recollections"
            " WHERE profile_id=?", (profile_id,)).fetchall()
        removed = 0
        for r in rows:
            removed += pdi.resident_forget(
                r["pdi_key"]
                or _hosted_ref(profile_id, r["interactor_id"], r["id"])) or 0
        return removed
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
