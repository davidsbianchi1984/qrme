"""Messaging, feature switches, and the homepage sandbox.

Three surfaces that share one idea: the person decides.

**Feature switches.** A small named set, per profile, default on. The point
is not the toggle — it is that everything downstream *refuses by naming the
switch*, so "why can't I message them" always has a real answer, and the
answer is theirs.

**Direct messages.** Between the people behind profiles, friends only —
the friendship graph is the consent record this platform already keeps,
and inventing a second one would be two things to revoke. The thread key
is the sorted pair, so a conversation has one identity from either side.
Unfriending closes the door without deleting what was said: words already
exchanged belong to both people.

**The homepage sandbox.** An editable page like the old MySpace — a
headline, an about, a theme, links, and top friends — stored as one
validated document. It is a sandbox in the strict sense: colors must be
hex, links must be http(s), everything else is plain text, and top friends
must be actual friends. There is nowhere to put a script, structurally,
which is what lets the page be shown to strangers at all.
"""

from __future__ import annotations

import json
import re

from . import db, inbox

#: The switches that exist. Adding one is a decision made here, where the
#: defaults live, rather than a string that quietly becomes load-bearing.
FEATURES = {
    "messaging": True,     # friends can DM the person behind this profile
    "homepage": True,      # the homepage is visible to others
}

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_MAX_LINKS = 8
_MAX_TOP_FRIENDS = 8


def are_friends(a: str, b: str) -> bool:
    """Mutual, deliberately: either side removing the edge closes the door
    for both. Consent that only one person can end is not consent.

    Public because a caller building a document for :func:`set_homepage` has
    to ask the same question this module will ask of it — a top friend who is
    not a friend refuses the *whole* page, so `seed` filters the list first.
    One definition of the question, asked by both sides of it."""
    conn = db.connect()
    one = conn.execute(
        "SELECT 1 FROM friendships WHERE profile_id=? AND friend_id=? AND"
        " state='active'", (a, b)).fetchone()
    other = conn.execute(
        "SELECT 1 FROM friendships WHERE profile_id=? AND friend_id=? AND"
        " state='active'", (b, a)).fetchone()
    return one is not None and other is not None


class SocialError(ValueError):
    pass


# -- feature switches ---------------------------------------------------------

def features_of(profile_id: str) -> dict:
    out = dict(FEATURES)
    for row in db.connect().execute(
            "SELECT feature, enabled FROM feature_flags WHERE profile_id=?",
            (profile_id,)).fetchall():
        if row["feature"] in out:
            out[row["feature"]] = bool(row["enabled"])
    return out


def set_feature(profile_id: str, feature: str, enabled: bool) -> dict:
    if feature not in FEATURES:
        raise SocialError(
            f"unknown feature {feature!r}; the switches are "
            f"{', '.join(sorted(FEATURES))}")
    conn = db.connect()
    conn.execute(
        "INSERT INTO feature_flags (profile_id, feature, enabled, updated_at)"
        " VALUES (?,?,?,?) ON CONFLICT (profile_id, feature) DO UPDATE SET"
        " enabled=excluded.enabled, updated_at=excluded.updated_at",
        (profile_id, feature, 1 if enabled else 0, db.utcnow()))
    conn.commit()
    return features_of(profile_id)


def enabled(profile_id: str, feature: str) -> bool:
    return features_of(profile_id).get(feature, False)


# -- direct messages ----------------------------------------------------------

def _pair(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a < b else (b, a)


def send_message(sender_id: str, recipient_id: str, body: str) -> dict:
    if sender_id == recipient_id:
        raise SocialError("that would be a note to yourself; the journal "
                          "is better at those")
    if not (body or "").strip():
        raise SocialError("a message needs words")
    if not are_friends(sender_id, recipient_id):
        raise SocialError("messages travel between friends; befriend them "
                          "first")
    if not enabled(recipient_id, "messaging"):
        raise SocialError("that person has messaging turned off")
    if not enabled(sender_id, "messaging"):
        raise SocialError("your messaging is turned off; turn the switch "
                          "back on to send")
    low, high = _pair(sender_id, recipient_id)
    conn = db.connect()
    message_id = db.new_id("dm")
    conn.execute(
        "INSERT INTO dm_messages (id, low_id, high_id, sender_id, body,"
        " sent_at) VALUES (?,?,?,?,?,?)",
        (message_id, low, high, sender_id, body.strip(), db.utcnow()))
    conn.commit()
    # The recipient hears *that*, not *what*: the words wait behind their
    # own door, where they already are.
    inbox.note(recipient_id, "message", sender_id, message_id)
    return _message(message_id)


def _message(message_id: str) -> dict:
    return dict(db.connect().execute(
        "SELECT * FROM dm_messages WHERE id=?", (message_id,)).fetchone())


def thread(profile_id: str, other_id: str) -> list[dict]:
    """One conversation, read by either side. Readable even after an
    unfriending: the words already exchanged belong to both people — only
    *new* words need the friendship."""
    low, high = _pair(profile_id, other_id)
    return [dict(r) for r in db.connect().execute(
        "SELECT * FROM dm_messages WHERE low_id=? AND high_id=?"
        " ORDER BY sent_at", (low, high)).fetchall()]


def threads(profile_id: str) -> list[dict]:
    """Every conversation this profile is part of, newest words first —
    with the other side's name, so a list is a list without n lookups."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT low_id, high_id, MAX(sent_at) AS last_at, COUNT(*) AS n"
        " FROM dm_messages WHERE low_id=? OR high_id=?"
        " GROUP BY low_id, high_id ORDER BY last_at DESC",
        (profile_id, profile_id)).fetchall()
    out = []
    for r in rows:
        other = r["high_id"] if r["low_id"] == profile_id else r["low_id"]
        name = conn.execute("SELECT display_name FROM profiles WHERE id=?",
                            (other,)).fetchone()
        out.append({"other_id": other,
                    "other_name": name["display_name"] if name else None,
                    "messages_count": r["n"], "last_at": r["last_at"]})
    return out


# -- the homepage sandbox -----------------------------------------------------

_DEFAULT_DOC = {
    "headline": "",
    "about": "",
    "theme": {"bg": "#1a1333", "accent": "#7b5cff"},
    "links": [],
    "top_friends": [],
}


def _validate_doc(profile_id: str, doc: dict) -> dict:
    """The sandbox's walls. Everything that comes back is safe to show a
    stranger; anything that is not text, a hex color, an http(s) link or a
    real friend's id is refused with the wall's own sentence."""
    out = dict(_DEFAULT_DOC)
    out["headline"] = str(doc.get("headline") or "")[:120]
    out["about"] = str(doc.get("about") or "")[:2000]

    theme = doc.get("theme") or {}
    for slot in ("bg", "accent"):
        value = theme.get(slot) or _DEFAULT_DOC["theme"][slot]
        if not _HEX.match(str(value)):
            raise SocialError("a theme color is a hex code like #1a1333")
    out["theme"] = {"bg": theme.get("bg") or _DEFAULT_DOC["theme"]["bg"],
                    "accent": theme.get("accent")
                    or _DEFAULT_DOC["theme"]["accent"]}

    links = doc.get("links") or []
    if len(links) > _MAX_LINKS:
        raise SocialError(f"up to {_MAX_LINKS} links; a homepage is a page, "
                          "not a directory")
    clean_links = []
    for link in links:
        url = str((link or {}).get("url") or "")
        label = str((link or {}).get("label") or "")[:80]
        if not url.startswith(("http://", "https://")):
            raise SocialError("links start with http:// or https://")
        clean_links.append({"label": label or url, "url": url[:500]})
    out["links"] = clean_links

    tops = list(doc.get("top_friends") or [])[: _MAX_TOP_FRIENDS + 1]
    if len(tops) > _MAX_TOP_FRIENDS:
        raise SocialError(f"top friends is at most {_MAX_TOP_FRIENDS} — "
                          "that is what makes it a ranking")
    for friend_id in tops:
        if not are_friends(profile_id, str(friend_id)):
            raise SocialError("top friends are chosen from your actual "
                              "friends")
    out["top_friends"] = [str(f) for f in tops]
    return out


def set_homepage(profile_id: str, doc: dict) -> dict:
    clean = _validate_doc(profile_id, doc)
    conn = db.connect()
    conn.execute(
        "INSERT INTO homepages (profile_id, doc, updated_at) VALUES (?,?,?)"
        " ON CONFLICT (profile_id) DO UPDATE SET doc=excluded.doc,"
        " updated_at=excluded.updated_at",
        (profile_id, json.dumps(clean), db.utcnow()))
    conn.commit()
    return homepage(profile_id, viewer_is_owner=True)


def homepage(profile_id: str, viewer_is_owner: bool = False) -> dict:
    """The page, for whoever may see it. The owner always sees their own
    sandbox; anybody else needs the homepage switch on."""
    if not viewer_is_owner and not enabled(profile_id, "homepage"):
        raise SocialError("this homepage is not public")
    conn = db.connect()
    row = conn.execute("SELECT * FROM homepages WHERE profile_id=?",
                       (profile_id,)).fetchone()
    doc = json.loads(row["doc"]) if row else dict(_DEFAULT_DOC)
    name = conn.execute("SELECT display_name FROM profiles WHERE id=?",
                        (profile_id,)).fetchone()
    tops = []
    for friend_id in doc.get("top_friends", []):
        friend = conn.execute(
            "SELECT display_name FROM profiles WHERE id=?",
            (friend_id,)).fetchone()
        if friend is not None:
            tops.append({"profile_id": friend_id,
                         "display_name": friend["display_name"]})
    return {"profile_id": profile_id,
            "display_name": name["display_name"] if name else None,
            "headline": doc["headline"], "about": doc["about"],
            "theme": doc["theme"], "links": doc["links"],
            "top_friends": tops,
            "editable": viewer_is_owner}
