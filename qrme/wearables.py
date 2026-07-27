"""Watches and wearables paired over Bluetooth.

QRME already had a watch *API* — `qrme/routers/watch.py` serves one glanceable
payload and a remote `act` endpoint — and no way to say **which watch**. This
is the pairing: a named device, what kind it is, and which faces it may show.

Kept deliberately apart from :data:`embodiments`, which records where a
*profile* lives — a speaker, a hologram, a robot body. A wearable here belongs
to the **owner** and reaches their own account. Folding them together would
mean pairing a watch could put somebody's synthetic persona on their wrist,
which is a different feature with a different consent question.

**Pairing and permission only.** There is no sensor stream here, no capture,
and nothing about a microphone. A paired watch in this module is a screen and a
set of buttons; anything that listens is a separate decision that has not been
made here.

**Unpairing is a revocation, not a delete.** The row stays with `revoked_at`
set, so a device that has been sent away cannot quietly come back by
re-presenting the same name — and the owner can see what was ever paired, which
is the question people actually ask after losing a watch.
"""

from __future__ import annotations

import json

from . import db

KINDS = ("watch", "band", "ring", "earbuds", "glasses")

# The faces a wrist can be given, and what each is for. A closed set, because
# "which faces" is a permission and a permission with open-ended values is one
# nobody can audit.
FACES: dict[str, str] = {
    "agents": "the status lights and their counts — no names",
    "activity": "how many new posts, friends and replies are waiting",
    "profile": "the profile's own headline figures",
    "control": "assist, halt, approve — the remote",
}
DEFAULT_FACES = ("agents", "activity")

MAX_WEARABLES = 8


class WearableError(ValueError):
    """A pairing that cannot stand."""


def pair(profile_id: str, name: str, kind: str,
         faces: list[str] | None = None) -> dict:
    """Pair a device, or re-pair one that was revoked.

    Re-pairing an existing name updates it rather than failing, because a watch
    that was unpaired and is being paired again is the same watch, and making
    somebody invent ``watch-2`` to do it is the kind of friction that teaches
    people to leave devices paired.
    """
    name = (name or "").strip()
    if not name:
        raise WearableError("a device needs a name you will recognise")
    if len(name) > 60:
        raise WearableError("a device name is at most 60 characters")
    if kind not in KINDS:
        raise WearableError(
            f"unknown wearable {kind!r}; expected one of {', '.join(KINDS)}")
    chosen = list(faces) if faces is not None else list(DEFAULT_FACES)
    for face in chosen:
        if face not in FACES:
            raise WearableError(
                f"unknown face {face!r}; expected one of {', '.join(FACES)}")

    conn = db.connect()
    existing = conn.execute(
        "SELECT id FROM wearables WHERE profile_id=? AND name=?",
        (profile_id, name)).fetchone()
    if existing is None:
        live = conn.execute(
            "SELECT COUNT(*) AS n FROM wearables WHERE profile_id=? AND"
            " revoked_at IS NULL", (profile_id,)).fetchone()["n"]
        if live >= MAX_WEARABLES:
            raise WearableError(
                f"{MAX_WEARABLES} paired devices is the limit — unpair one")
        conn.execute(
            "INSERT INTO wearables (id, profile_id, name, kind, transport,"
            " faces, paired_at) VALUES (?,?,?,?,'bluetooth',?,?)",
            (db.new_id("wbl"), profile_id, name, kind, json.dumps(chosen),
             db.utcnow()))
    else:
        conn.execute(
            "UPDATE wearables SET kind=?, faces=?, paired_at=?,"
            " revoked_at=NULL WHERE id=?",
            (kind, json.dumps(chosen), db.utcnow(), existing["id"]))
    conn.commit()
    return device(profile_id, name)


def unpair(profile_id: str, name: str) -> dict:
    """Revoke a pairing. The row survives — see the module note."""
    conn = db.connect()
    row = conn.execute(
        "SELECT id FROM wearables WHERE profile_id=? AND name=?",
        (profile_id, name)).fetchone()
    if row is None:
        raise WearableError("no such device")
    conn.execute("UPDATE wearables SET revoked_at=? WHERE id=?",
                 (db.utcnow(), row["id"]))
    conn.commit()
    return device(profile_id, name)


def device(profile_id: str, name: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM wearables WHERE profile_id=? AND name=?",
        (profile_id, name)).fetchone()
    if row is None:
        return {}
    return {"id": row["id"], "name": row["name"], "kind": row["kind"],
            "transport": row["transport"],
            "faces": json.loads(row["faces"]),
            "paired_at": row["paired_at"], "revoked_at": row["revoked_at"],
            "paired": row["revoked_at"] is None}


def paired(profile_id: str, include_revoked: bool = False) -> list[dict]:
    sql = "SELECT name FROM wearables WHERE profile_id=?"
    if not include_revoked:
        sql += " AND revoked_at IS NULL"
    rows = db.connect().execute(sql + " ORDER BY paired_at",
                                (profile_id,)).fetchall()
    return [device(profile_id, r["name"]) for r in rows]


def may_show(profile_id: str, name: str, face: str) -> bool:
    """Whether this device is allowed this face.

    Checked here rather than at each surface, so a face added later cannot
    arrive on every wrist by default.
    """
    d = device(profile_id, name)
    return bool(d) and d["paired"] and face in d["faces"]
