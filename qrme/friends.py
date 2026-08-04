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

* **The founder comes standard, and stays.** Every new profile is created with
  both of the founder's profiles pinned at the top of its list — the rendered
  one and the photographed one, which are two different profiles of the same
  man. This is the MySpace pattern: a brand-new account with an empty friends
  list looks broken, and the platform's owner standing there is both a welcome
  and a face to put to the thing.

  These two are **fixed**. They cannot be removed and cannot be reordered
  below a chosen friend — a product decision by the platform's owner, made
  explicitly and after the removable version had been built. Everything else in
  the list is entirely the owner's to add and drop.

* **Removal is durable for everyone it applies to.** Removing sets
  ``state='removed'`` rather than deleting, because the founder install runs on
  profile creation and a deleted row would simply be recreated. That machinery
  stays: it is what makes an ordinary un-friending stick.
"""

from __future__ import annotations

from . import db, inbox, verification

# The founder's two profiles, in the order they stand. One constant, because
# "who is pinned" is a product decision and should be greppable rather than
# spelled out at each call site.
#
# Two profiles for one person is the point rather than an accident: the
# rendered likeness is marked AI in its own pixels, the photograph is not, and
# a platform whose whole argument is that synthetic things must say so cannot
# have its owner running a single profile that is ambiguously both.
FOUNDER_HANDLES: tuple[str, ...] = ("david_bianchi", "david_bianchi_ai")

# Kept as a name because the rest of the module and its tests read better for
# it, and because a single-founder deployment is still a coherent thing.
FOUNDER_HANDLE = FOUNDER_HANDLES[0]


class FriendError(ValueError):
    """A friendship that cannot exist — unknown profile, or a self-edge."""


class PinnedFriend(FriendError):
    """A pinned founder row cannot be removed."""


def _profile_exists(profile_id: str) -> bool:
    return db.connect().execute(
        "SELECT 1 FROM profiles WHERE id=?", (profile_id,)).fetchone() is not None


def founder_ids() -> list[str]:
    """The founder profiles' ids, in pinned order.

    Looked up by handle rather than pinned to fixed ids, because ids are minted
    at seed time and differ per deployment. An empty list is a normal answer:
    an unseeded database has no founder, and installing one is not something
    profile creation should be inventing on the fly.
    """
    out = []
    conn = db.connect()
    for handle in FOUNDER_HANDLES:
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()
        if row:
            out.append(row["profile_id"])
    return out


def founder_id() -> str | None:
    """The first founder profile's id, or ``None``."""
    ids = founder_ids()
    return ids[0] if ids else None


def is_pinned(profile_id: str, friend_id: str) -> bool:
    """Whether this row is one of the fixed founder pins."""
    return friend_id in founder_ids() and profile_id != friend_id


def install_founder(profile_id: str) -> dict:
    """Give a newly created profile its standing friends.

    Idempotent, and deliberately silent when there is nothing to do: no founder
    on this deployment, or the profile *is* one of them. Creation calls this on
    every profile, so raising here would turn a default into a reason profile
    creation fails.

    Unlike an ordinary friendship, a pin that was somehow cleared is restored —
    these two are fixed, so "already removed" is not a state they are allowed
    to stay in.
    """
    ids = [fid for fid in founder_ids() if fid != profile_id]
    if not ids:
        return {"installed": False, "reason": "no founder to install"}

    conn = db.connect()
    installed = []
    for order, fid in enumerate(ids):
        existing = conn.execute(
            "SELECT id, state FROM friendships WHERE profile_id=? AND"
            " friend_id=?", (profile_id, fid)).fetchone()
        if existing is None:
            conn.execute(
                "INSERT INTO friendships (id, profile_id, friend_id, origin,"
                " state, created_at) VALUES (?,?,?,?,?,?)",
                (db.new_id("frn"), profile_id, fid, f"founder:{order}",
                 "active", db.utcnow()))
            installed.append(fid)
        elif existing["state"] != "active":
            conn.execute("UPDATE friendships SET state='active',"
                         " removed_at=NULL WHERE id=?", (existing["id"],))
            installed.append(fid)
    conn.commit()
    return {"installed": bool(installed), "friend_ids": installed}


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
        inbox.note(friend_id, "friend", profile_id)
        return {"profile_id": profile_id, "friend_id": friend_id,
                "added": True, "revived": True}

    conn.execute(
        "INSERT INTO friendships (id, profile_id, friend_id, origin, state,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("frn"), profile_id, friend_id, "chosen", "active",
         db.utcnow()))
    conn.commit()
    # The person on the other end hears about it — a friendship extended
    # in silence is indistinguishable from one that never was.
    inbox.note(friend_id, "friend", profile_id)
    return {"profile_id": profile_id, "friend_id": friend_id, "added": True}


def unfriend(profile_id: str, friend_id: str) -> dict:
    """Remove a friend.

    Marks the row removed rather than deleting it — see the module note.

    The founder pins are refused. That is a product decision by the platform's
    owner rather than a technical constraint, and it is enforced here, in the
    one function every removal path goes through, so a future caller cannot
    route around it by not knowing about it.
    """
    if is_pinned(profile_id, friend_id):
        raise PinnedFriend(
            "the founder is a fixed friend on every profile and cannot be "
            "removed")
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
    return {"profile_id": profile_id, "friend_id": friend_id, "removed": True}


def friends_of(profile_id: str) -> list[dict]:
    """The list: the founder pins in their fixed order, then everyone else
    oldest-first.

    The ordering is computed here rather than stored, so it cannot drift out of
    step with what ``origin`` says. A stored position column would have to be
    rewritten on every insert and would be the thing that is wrong when the
    founder turns up third.

    ``origin`` is ``founder:0``, ``founder:1``, … for the pins, so their order
    among themselves is fixed too and does not depend on which row happened to
    be written first.
    """
    rows = db.connect().execute(
        "SELECT f.friend_id, f.origin, f.created_at, p.display_name, p.avatar,"
        "       p.kind, h.handle"
        "  FROM friendships f"
        "  JOIN profiles p ON p.id = f.friend_id"
        "  LEFT JOIN handles h ON h.profile_id = f.friend_id"
        " WHERE f.profile_id=? AND f.state='active'"
        " ORDER BY (f.origin LIKE 'founder:%') DESC, f.origin ASC,"
        "          f.created_at ASC",
        (profile_id,)).fetchall()

    # Both of the per-row lookups below are answered up front. Reading a
    # verification record and a reciprocal friendship one row at a time made a
    # list of fifty friends into a hundred and one queries, all of which fit in
    # two.
    ids = [r["friend_id"] for r in rows]
    badges = verification.statuses(ids)
    mutual = _mutual_with(profile_id, ids)

    out = []
    for i, r in enumerate(rows, start=1):
        founder = r["origin"].startswith("founder")
        out.append({
            "position": i,
            "profile_id": r["friend_id"],
            "display_name": r["display_name"],
            "handle": r["handle"],
            "avatar": r["avatar"],
            "kind": r["kind"],
            "founder": founder,
            # Said out loud so a client renders the row without a remove
            # control, rather than offering one that will 409.
            "pinned": founder,
            # The identity badge, as the whole record. A friends list is
            # exactly where somebody decides whether a face is a real person,
            # so the level travels with the word rather than being a second
            # call the surface might not make.
            "verification": badges.get(r["friend_id"], {}),
            "since": r["created_at"],
            "mutual": r["friend_id"] in mutual,
        })
    return out


def _is_mutual(profile_id: str, friend_id: str) -> bool:
    return db.connect().execute(
        "SELECT 1 FROM friendships WHERE profile_id=? AND friend_id=? AND"
        " state='active'", (friend_id, profile_id)).fetchone() is not None


def _mutual_with(profile_id: str, friend_ids: list[str]) -> set[str]:
    """Which of these list `profile_id` back, in one query."""
    if not friend_ids:
        return set()
    marks = ",".join("?" * len(friend_ids))
    return {r["profile_id"] for r in db.connect().execute(
        f"SELECT profile_id FROM friendships WHERE friend_id=? AND"
        f" state='active' AND profile_id IN ({marks})",
        [profile_id] + list(friend_ids)).fetchall()}


def backfill_founder() -> list[str]:
    """Install the founder pins on profiles that predate them.

    :func:`install_founder` runs at profile creation, which does nothing for a
    deployment that was already running before the founder was seeded — those
    profiles would be the only ones on the platform without the standing
    friends, and nothing else would ever notice. The seed is the repair,
    exactly as it is for the starters' portraits.

    Also repairs a pin that was cleared before the pins became fixed: unlike an
    ordinary un-friending, "removed" is not a state these two are allowed to
    stay in.
    """
    ids = founder_ids()
    if not ids:
        return []
    rows = db.connect().execute("SELECT id FROM profiles").fetchall()
    return [r["id"] for r in rows if install_founder(r["id"])["installed"]]


def count(profile_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM friendships WHERE profile_id=? AND"
        " state='active'", (profile_id,)).fetchone()["n"]


# -- who you might know ------------------------------------------------------

# What a suggestion is worth, and why. Same posture as the feed's weights:
# small readable integers, because a recommendation nobody can explain is one
# nobody can argue with — and a friend suggestion is a claim about a person.
S_MUTUAL = 40           # per friend in common, capped below
S_MUTUAL_CAP = 120
S_TAG = 20              # per shared subject
S_TAG_CAP = 60
S_FRIEND_OF_PIN = 5     # the founder is everybody's friend, so this is faint


def suggestions(profile_id: str, limit: int = 10) -> list[dict]:
    """Profiles this one might want to know, most likely first, and why.

    Ranked on the same public signals the feed uses — the friend graph and the
    subjects a profile works in. Never source material, never memories: a
    friend suggestion built from somebody's private writing would be the
    platform reading a diary to make an introduction.

    Two exclusions that matter more than the ranking:

    * **Anyone already on the list**, in either state. Somebody who removed a
      friend should not be handed them back as a suggestion the next day —
      that is the same imposition the founder pins were careful to avoid,
      wearing a recommendation badge.
    * **The founder pins**, which are already on every list by construction and
      would otherwise top every suggestion set on the platform.
    """
    import json

    conn = db.connect()
    mine = {f["profile_id"] for f in friends_of(profile_id)}
    # Every row, not only the active ones: a removal is a decision.
    known = {r["friend_id"] for r in conn.execute(
        "SELECT friend_id FROM friendships WHERE profile_id=?",
        (profile_id,)).fetchall()}
    excluded = known | {profile_id} | set(founder_ids())

    my_tags: set[str] = set()
    row = conn.execute("SELECT tags FROM marketplace WHERE profile_id=?",
                       (profile_id,)).fetchone()
    if row and row["tags"]:
        try:
            my_tags = set(json.loads(row["tags"]))
        except ValueError:
            my_tags = set()

    # Friends of friends, with how many paths lead to each.
    mutual_counts: dict[str, int] = {}
    for friend in mine:
        for r in conn.execute(
                "SELECT friend_id FROM friendships WHERE profile_id=? AND"
                " state='active'", (friend,)).fetchall():
            fid = r["friend_id"]
            if fid not in excluded:
                mutual_counts[fid] = mutual_counts.get(fid, 0) + 1

    candidates = dict.fromkeys(mutual_counts)
    if my_tags:
        for r in conn.execute("SELECT profile_id, tags FROM marketplace"
                              ).fetchall():
            if r["profile_id"] in excluded:
                continue
            try:
                if my_tags & set(json.loads(r["tags"] or "[]")):
                    candidates.setdefault(r["profile_id"])
            except ValueError:
                pass

    out = []
    for pid in candidates:
        info = conn.execute(
            "SELECT p.display_name, p.avatar, p.kind, m.tags, h.handle"
            "  FROM profiles p"
            "  LEFT JOIN marketplace m ON m.profile_id = p.id"
            "  LEFT JOIN handles h ON h.profile_id = p.id"
            " WHERE p.id=?", (pid,)).fetchone()
        if info is None:
            continue
        score, reason = 0, None
        n = mutual_counts.get(pid, 0)
        if n:
            score += min(n * S_MUTUAL, S_MUTUAL_CAP)
            reason = (f"{n} friend{'s' if n > 1 else ''} in common")
        shared: set[str] = set()
        try:
            shared = my_tags & set(json.loads(info["tags"] or "[]"))
        except ValueError:
            pass
        if shared:
            score += min(len(shared) * S_TAG, S_TAG_CAP)
            if reason is None:
                reason = f"also works in {sorted(shared)[0]}"
        if score == 0:
            continue
        out.append({
            "profile_id": pid, "display_name": info["display_name"],
            "handle": info["handle"], "avatar": info["avatar"],
            "kind": info["kind"], "score": score,
            "mutual_friends": n, "shared_subjects": sorted(shared),
            "reason": reason,
        })
    out.sort(key=lambda s: (-s["score"], s["display_name"]))
    return out[:limit]
