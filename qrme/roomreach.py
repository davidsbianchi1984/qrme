"""What the people in a room let the synthetic people in it reach.

## The two keys

A profile's *owner* decides what that profile can ever do: which apps it
is connected to (``app_connectors``) and which hands it has been granted
(``hand_grants``). That is one key, and it is the only one this product
had.

It is not enough on its own, because a profile in a room is very often
somebody else's. A starter is outsourced from the account that made it;
a specialist is invited into a room by a person who does not own it. The
owner's grant says *this profile may drive a browser* — it does not say
*this profile may drive it for you, now, in here*.

So the room holds the second key. Every synthetic seat's connections and
skills are listed to the people in the room with a box beside each one,
and nothing opens unless both keys are turned:

    the owner granted it   AND   this room allowed it

Either side can be withdrawn alone. Unticking a box in a room does not
touch the owner's grant, and an owner revoking a grant does not need the
room's permission to take effect — a reach checks both every time it is
opened, rather than trusting a decision made earlier.

## Why the room rather than the person

The tick is the room's, not one viewer's. Everybody in a room sees the
same conversation and the same seats, and a profile that may read one
person's screen while invisible to the person sitting beside them is a
room where nobody can say what is permitted. The ledger records *who*
decided, so the answer to "who let it do that" is a name.

## What a box is

Two kinds, because a profile reaches the world two ways:

``app``    a connector — one of the catalog's 103, across 9 providers.
           Keyed by the connector's id, so revoking and reconnecting the
           same app does not silently inherit the old room's yes.
``cap``    one capability of one connection — "read the mail" as opposed
           to "send it". 180 distinct ones across the catalog. Keyed
           ``<connector id>:<capability>``, so it dies with the
           connection it belongs to.
``skill``  a live hand grant — eyes on a screen, a cursor, a keyboard, a
           body. Keyed by the grant id, for the same reason: a grant is a
           specific set of places, verbs, minutes and steps, and a yes
           given to one is not a yes to its replacement.

## Why the whole catalog is listed

The panel shows every connector the platform has, per profile, not only
the ones a profile happens to hold. "What could this synthetic person
reach?" and "what has its owner actually wired up?" are different
questions, and a list that only ever shows the second cannot answer the
first — somebody deciding whether to trust a profile in their room wants
to see the shape of what is possible, and see that most of it is dark.

A row its owner has not connected is shown and cannot be ticked. The
room's key does not conjure the owner's: allowing an app that nobody has
connected would be a permission for something that cannot happen, which
is the kind of yes that later reads as consent to something real.

Absent means no. A box nobody has ticked is a row that does not exist,
which is the honest default for a permission and means a new connector
appearing in a profile arrives switched off.
"""

from __future__ import annotations

import json

from . import db


def _rows(room_id: str) -> dict[tuple[str, str, str], dict]:
    got = db.connect().execute(
        "SELECT * FROM room_allowances WHERE room_id=?", (room_id,)).fetchall()
    return {(r["profile_id"], r["kind"], r["key"]): dict(r) for r in got}


def allows(room_id: str, profile_id: str, kind: str, key: str) -> bool:
    """Whether this room has said yes to this one thing.

    One half of the check. The caller is responsible for the other half —
    that the owner granted it — because the two live in different tables
    and a helper that pretended to answer both would be the place
    somebody later forgot one.
    """
    row = _rows(room_id).get((profile_id, kind, key))
    return bool(row and row["allowed"])


def allow(room_id: str, profile_id: str, kind: str, key: str,
          allowed: bool, by: str) -> dict:
    """Tick or untick one box, and record who did it."""
    if kind not in ("app", "cap", "skill"):
        raise ValueError(
            "a room allows an app, one of its capabilities, or a skill — "
            "nothing else")
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "INSERT INTO room_allowances (id, room_id, profile_id, kind, key,"
        " allowed, decided_by, decided_at) VALUES (?,?,?,?,?,?,?,?)"
        " ON CONFLICT(room_id, profile_id, kind, key) DO UPDATE SET"
        " allowed=excluded.allowed, decided_by=excluded.decided_by,"
        " decided_at=excluded.decided_at",
        (db.new_id("allow"), room_id, profile_id, kind, key,
         1 if allowed else 0, by, now))
    conn.commit()
    return {"profile_id": profile_id, "kind": kind, "key": key,
            "allowed": bool(allowed), "decided_by": by, "decided_at": now}


def offered(room_id: str, profile_ids: list[str]) -> list[dict]:
    """Every synthetic seat, the whole catalog, and what this room allows.

    The catalog is the frame and the owner's connectors fill it in, so a
    profile that has wired up two apps comes back with 103 rows of which
    two are live. That is the point: the dark rows are the answer to
    "what could this reach", and they are the reason the lit ones mean
    something.
    """
    from . import catalog, hands

    ticks = _rows(room_id)
    conn = db.connect()
    out: list[dict] = []
    for pid in profile_ids:
        held = {
            (r["provider"], r["app"]): dict(r)
            for r in conn.execute(
                "SELECT id, provider, app, capabilities, authorized_at"
                " FROM app_connectors WHERE profile_id=? AND status='active'",
                (pid,)).fetchall()
        }
        groups: list[dict] = []
        by_provider: dict[str, dict] = {}
        for entry in catalog.CONNECTORS:
            key = (entry["provider"], entry["app"])
            row = held.get(key)
            cid = row["id"] if row else None
            granted = set(json.loads(row["capabilities"])) if row else set()
            tick = ticks.get((pid, "app", cid)) if cid else None
            group = by_provider.get(entry["provider"])
            if group is None:
                group = by_provider[entry["provider"]] = {
                    "provider": entry["provider"],
                    "label": catalog._PROVIDER_LABEL[entry["provider"]],
                    "apps": [],
                }
                groups.append(group)
            group["apps"].append({
                "key": cid, "provider": entry["provider"],
                "app": entry["app"], "label": entry["label"],
                # The owner's side, in three separate facts rather than
                # one blurred one: has it been connected at all, has it
                # been given its credential, and has this room said yes.
                "connected": cid is not None,
                "ready": bool(row and row["authorized_at"]),
                "allowed": bool(tick and tick["allowed"]),
                "capabilities": [
                    {"name": cap,
                     "granted": cap in granted,
                     "allowed": bool(
                         cid and (ticks.get((pid, "cap", f"{cid}:{cap}"))
                                  or {}).get("allowed"))}
                    for cap in entry["capabilities"]
                ],
            })
        skills = []
        for grant in hands.grants(pid, live_only=True):
            tick = ticks.get((pid, "skill", grant["id"]))
            skills.append({
                "key": grant["id"], "surface": grant["surface"],
                "places": grant["places"], "verbs": grant["verbs"],
                "steps": grant["steps"], "watched": grant["watched"],
                "expires_at": grant["expires_at"],
                # Eyes and nothing else. Worth saying on the box rather
                # than making somebody read four verbs to work out that
                # this one only looks.
                "eyes_only": all(v in hands.EYES_ONLY
                                 for v in grant["verbs"]),
                "allowed": bool(tick and tick["allowed"]),
            })
        out.append({"profile_id": pid, "providers": groups,
                    "skills": skills,
                    # Counted here rather than in the client, so the row a
                    # person reads before opening anything is the truth and
                    # not an estimate: how much of what is possible is
                    # actually wired up, and how much of that is allowed.
                    # The bar beside the name, counted here rather than
                    # in the client so the number somebody reads before
                    # opening anything is the truth and not an estimate.
                    #
                    # Split by kind on purpose: "2 allowed" said nothing
                    # about WHAT was allowed, and skills and connections
                    # are the two things this panel is about. Each gets
                    # its own "n of m".
                    "connected_count": len(held),
                    "app_count": len(catalog.CONNECTORS),
                    "apps_allowed": sum(
                        1 for k, v in ticks.items()
                        if k[0] == pid and k[1] == "app" and v["allowed"]),
                    # Every capability the catalog offers, counted once.
                    "skill_count": len({
                        cap for e in catalog.CONNECTORS
                        for cap in e["capabilities"]}),
                    "skills_allowed": sum(
                        1 for k, v in ticks.items()
                        if k[0] == pid and k[1] == "cap" and v["allowed"]),
                    # The hand grants are a third thing and are counted
                    # as themselves — a room that has allowed a cursor
                    # has allowed something no connector count shows.
                    "hands_allowed": sum(
                        1 for k, v in ticks.items()
                        if k[0] == pid and k[1] == "skill" and v["allowed"]),
                    "hands_count": len(skills)})
    return out
