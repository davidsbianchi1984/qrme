"""Friendships between profiles, and the one that comes as standard.

QRME already had a table called ``relationships``, and this is not it. That one
records how a profile treats an **interactor** — the person typing at it:
family, friend, stranger, and the tone and boundaries that follow from it. This
module is the other axis, profile ↔ profile, which is the graph the community
surfaces are actually drawn from. Naming them apart matters, because a bug
where one is read as the other would look like working code.

Three decisions worth keeping in view:

* **A list is directed, not mutual.** ``befriend`` writes one row. A friends
  list is a claim its owner makes about who they stand with, and a mutual
  edge would mean somebody else's action edits your list. Two rows make it
  mutual, and :func:`friends_of` reports ``mutual`` per entry so a surface can
  show the difference without inventing it.

* **The founder comes standard, and can be shown the door.** Every new profile
  is created with the founder's profile pinned at position one. This is the
  MySpace pattern and it is doing the same job: a brand-new account with an
  empty friends list looks broken, and the platform's owner standing there is
  both a welcome and a face to put to the thing. But it is a real row, it
  counts, and it can be removed — a friend you cannot remove is furniture.

* **Removal is durable.** Removing sets ``state='removed'`` rather than
  deleting, because the founder install runs on profile creation and a deleted
  row would simply be recreated. Somebody who removed the founder once should
  not find him back tomorrow; that is the difference between a default and an
  imposition.
"""

from __future__ import annotations

from . import db

# The founder profile's handle. One constant, because "who is pinned" is a
# product decision and should be greppable rather than spelled out at each
# call site.
FOUNDER_HANDLE = "david_bianchi"

# Where the founder sits, and why the rest of the list cannot reach it.
FOUNDER_POSITION = 1


class FriendError(ValueError):
    """A friendship that cannot exist — unknown profile, or a self-edge."""


def _profile_exists(profile_id: str) -> bool:
    return db.connect().execute(
        "SELECT 1 FROM profiles WHERE id=?", (profile_id,)).fetchone() is not None


def founder_id() -> str | None:
    """The founder profile's id, or ``None`` on a deployment without one.

    Looked up by handle rather than pinned to a fixed id, because the id is
    minted at seed time and differs per deployment. ``None`` is a normal
    answer: an unseeded database has no founder, and installing one is not
    something profile creation should be inventing on the fly.
    """
    row = db.connect().execute(
        "SELECT profile_id FROM handles WHERE handle=?",
        (FOUNDER_HANDLE,)).fetchone()
    return row["profile_id"] if row else None


def install_founder(profile_id: str) -> dict:
    """Give a newly created profile its standing first friend.

    Idempotent, and deliberately silent when there is nothing to do: no
    founder on this deployment, the profile *is* the founder, or the row
    already exists in either state. Creation calls this on every profile, so
    raising here would turn a cosmetic default into a reason profile creation
    fails.
    """
    fid = founder_id()
    if fid is None or fid == profile_id:
        return {"installed": False, "reason": "no founder to install"}

    conn = db.connect()
    existing = conn.execute(
        "SELECT state FROM friendships WHERE profile_id=? AND friend_id=?",
        (profile_id, fid)).fetchone()
    if existing is not None:
        # Includes the removed case, which is the point: somebody who removed
        # the founder does not get him back the next time this runs.
        return {"installed": False, "reason": f"already {existing['state']}"}

    conn.execute(
        "INSERT INTO friendships (id, profile_id, friend_id, origin, state,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("frn"), profile_id, fid, "founder", "active", db.utcnow()))
    conn.commit()
    return {"installed": True, "friend_id": fid}


def befriend(profile_id: str, friend_id: str) -> dict:
    """Add ``friend_id`` to ``profile_id``'s list.

    Re-adding somebody previously removed revives the existing row rather than
    failing on the UNIQUE constraint — including the founder, who can be
    invited back by the profile that showed him out.
    """
    if profile_id == friend_id:
        raise FriendError("a profile cannot be its own friend")
    for pid in (profile_id, friend_id):
        if not _profile_exists(pid):
            raise FriendError(f"no such profile: {pid}")

    conn = db.connect()
    row = conn.execute(
        "SELECT id, state FROM friendships WHERE profile_id=? AND friend_id=?",
        (profile_id, friend_id)).fetchone()
    if row is not None:
        if row["state"] == "active":
            return {"profile_id": profile_id, "friend_id": friend_id,
                    "added": False, "reason": "already a friend"}
        conn.execute(
            "UPDATE friendships SET state='active', removed_at=NULL WHERE id=?",
            (row["id"],))
        conn.commit()
        return {"profile_id": profile_id, "friend_id": friend_id,
                "added": True, "revived": True}

    conn.execute(
        "INSERT INTO friendships (id, profile_id, friend_id, origin, state,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("frn"), profile_id, friend_id, "chosen", "active",
         db.utcnow()))
    conn.commit()
    return {"profile_id": profile_id, "friend_id": friend_id, "added": True}


def unfriend(profile_id: str, friend_id: str) -> dict:
    """Remove a friend, founder included.

    Marks the row removed rather than deleting it — see the module note. The
    founder is not special-cased here on purpose: the whole point of him being
    a real row is that the ordinary verb works on him.
    """
    conn = db.connect()
    row = conn.execute(
        "SELECT id, state, origin FROM friendships WHERE profile_id=? AND"
        " friend_id=?", (profile_id, friend_id)).fetchone()
    if row is None or row["state"] == "removed":
        return {"profile_id": profile_id, "friend_id": friend_id,
                "removed": False, "reason": "not a friend"}
    conn.execute("UPDATE friendships SET state='removed', removed_at=? WHERE"
                 " id=?", (db.utcnow(), row["id"]))
    conn.commit()
    return {"profile_id": profile_id, "friend_id": friend_id, "removed": True,
            "was_founder": row["origin"] == "founder"}


def friends_of(profile_id: str) -> list[dict]:
    """The list, founder first, then everyone else oldest-first.

    The ordering is computed here rather than stored, so it cannot drift out of
    step with what ``origin`` says. A stored position column would have to be
    rewritten on every insert and would be the thing that is wrong when the
    founder turns up third.
    """
    rows = db.connect().execute(
        "SELECT f.friend_id, f.origin, f.created_at, p.display_name, p.avatar,"
        "       p.kind, h.handle"
        "  FROM friendships f"
        "  JOIN profiles p ON p.id = f.friend_id"
        "  LEFT JOIN handles h ON h.profile_id = f.friend_id"
        " WHERE f.profile_id=? AND f.state='active'"
        " ORDER BY (f.origin='founder') DESC, f.created_at ASC",
        (profile_id,)).fetchall()

    out = []
    for i, r in enumerate(rows, start=1):
        out.append({
            "position": i,
            "profile_id": r["friend_id"],
            "display_name": r["display_name"],
            "handle": r["handle"],
            "avatar": r["avatar"],
            "kind": r["kind"],
            "founder": r["origin"] == "founder",
            "since": r["created_at"],
            "mutual": _is_mutual(profile_id, r["friend_id"]),
        })
    return out


def _is_mutual(profile_id: str, friend_id: str) -> bool:
    return db.connect().execute(
        "SELECT 1 FROM friendships WHERE profile_id=? AND friend_id=? AND"
        " state='active'", (friend_id, profile_id)).fetchone() is not None


def backfill_founder() -> list[str]:
    """Install the founder on profiles that predate him.

    :func:`install_founder` runs at profile creation, which does nothing for a
    deployment that was already running before the founder was seeded — those
    profiles would be the only ones on the platform without the standing first
    friend, and nothing else would ever notice. The seed is the repair, exactly
    as it is for the starters' portraits.

    Skips anybody who has removed him, because a repair that undoes a person's
    decision is not a repair.
    """
    fid = founder_id()
    if fid is None:
        return []
    rows = db.connect().execute(
        "SELECT p.id FROM profiles p"
        "  LEFT JOIN friendships f"
        "         ON f.profile_id = p.id AND f.friend_id = ?"
        " WHERE p.id != ? AND f.id IS NULL", (fid, fid)).fetchall()
    return [r["id"] for r in rows if install_founder(r["id"])["installed"]]


def count(profile_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM friendships WHERE profile_id=? AND"
        " state='active'", (profile_id,)).fetchone()["n"]
