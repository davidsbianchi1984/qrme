"""Anonymous, several, and exactly one verified.

Three things a person is allowed to be on this platform, and the whole of this
module is the tension between them.

**You may be anonymous.** Not everyone can afford to put their name on what
they think, and a platform that only works for people with nothing to lose is
a platform for a narrow set of people.

**You may hold several profiles.** A person is not one thing. The work self,
the hobby, the one for the support group nobody at work knows about — these
are not sockpuppets, they are the ordinary shape of a life, and forcing them
into one identity is its own kind of exposure.

**Exactly one of them may be verified.** This is the rule the other two need
in order to be safe rather than merely permitted.

The reason is what the badge actually says. Verification is not a quality
score and not a reward for being a good citizen; it is the sentence *this is
that particular real person*. Said of two profiles at once, it is either
false of one of them or it is a statement that one human being is two
authenticated people — which is precisely the primitive that verification
exists to deny to everybody else. A platform that hands it out per profile has
not verified anybody; it has sold a badge.

So: **many profiles, at most one badge, and the badge moves rather than
multiplies.** :func:`move` exists because the rule is one *at a time*, not one
forever — people change which face is their public one, and a rule that could
only be satisfied by deleting a profile would be answered by lying instead.

Three consequences that are easy to get backwards, and are the reason this is
a module rather than a constraint bolted onto :mod:`qrme.verification`:

**A fictional profile is not unverified, it is unverifiable**, and it never
consumes the slot. `verification.status` already draws that distinction; this
module has to respect it or an invented character would lock a real person out
of their own badge.

**The roster is owner-only.** :func:`roster` is the one call that links a
person's profiles to each other, and it is the exact tool for stripping
anonymity from all of them at once — find one, learn the account, enumerate
the rest. It answers to the owner's own token and to nothing else. Every
anonymity guarantee in this file is worth precisely as much as that check.

**Anonymity is what the platform withholds, not what it can promise.**
:func:`anonymity` reports both halves, because the failure mode is somebody
reading "anonymous" as "untraceable" and posting accordingly. We can decline
to publish a name. We cannot make prose unrecognisable to a reader who knows
the author, and saying so plainly is the only honest version of this feature.

"One person" here means **one owner account**, because that is the unit this
platform can actually observe. Somebody determined to hold two accounts is not
stopped by anything in this file, and :func:`same_identity_elsewhere` closes
only the part that is visible: the same attestor vouching for the same
evidence twice. Claiming more than that would be the sort of security theatre
the rest of this codebase argues against.
"""

from __future__ import annotations

from . import db
from .signatures import _level_rank


class IdentityError(ValueError):
    """A claim about who somebody is that cannot stand. Text for a person."""


# Profile kinds that depict a real human being. A `fictional` profile depicts
# nobody, so there is nobody to verify and nobody whose single badge could be
# spent — it is unverifiable rather than unverified, and the difference is the
# whole reason it is excluded here rather than merely refused later.
REAL_PERSON_KINDS = ("self", "other_person")

# What anonymity actually does, and what it cannot do. Published rather than
# implied: the dangerous reading of the word is the generous one, and somebody
# deciding what to post deserves the limits in the same breath as the promise.
WITHHELD = (
    "your display name — surfaces show a fixed 'Anonymous 00000000' tied to "
    "this profile, which you cannot change and which says nothing about you",
    "your picture — you get the same silhouette as everybody else who is "
    "anonymous, so it identifies nobody and matches no one",
    "your owner account, so two of your profiles cannot be matched to "
    "each other by whoever is reading them",
    "who verified you, if anyone did — the attestor is a pointer back to you",
    "your name inside the profile's own prompt, so it cannot say it by accident",
    "your name on anything the profile signs or watermarks",
)
NOT_WITHHELD = (
    "what you write — prose is recognisable to anyone who knows you",
    "your handle, which is how people link to you at all",
    "who your friends are, and what you post, like and share",
    "anything you say in a room, to the people in that room",
)


def _profile(profile_id: str) -> dict:
    row = db.connect().execute("SELECT * FROM profiles WHERE id=?",
                               (profile_id,)).fetchone()
    if row is None:
        raise IdentityError("no such profile")
    return dict(row)


def verified_profile(owner_id: str) -> str | None:
    """Which of this person's profiles holds the badge, if any.

    Joined rather than stored. A `verified_profile_id` column on an account
    would be a second place the same fact lives, and the day the two disagree
    the surfaces would read the copy — which is how a badge ends up on a
    profile whose verification row was deleted.
    """
    marks = ",".join("?" * len(REAL_PERSON_KINDS))
    row = db.connect().execute(
        "SELECT p.id FROM profiles p"
        "  JOIN profile_verification v ON v.profile_id = p.id"
        f" WHERE p.owner_id=? AND p.kind IN ({marks})"
        "   AND p.status != 'terminated'"
        " ORDER BY v.checked_at, p.rowid LIMIT 1",
        (owner_id, *REAL_PERSON_KINDS)).fetchone()
    return row["id"] if row else None


def same_identity_elsewhere(attestor: str | None, ref: str | None,
                            owner_id: str) -> str | None:
    """A different account already verified on this same evidence.

    The part of "one person, one badge" that survives somebody opening a
    second account. If the same attestor has vouched for the same reference,
    the two profiles are the same human however many accounts stand between
    them.

    Only meaningful when there is a reference to match on: a `self_asserted`
    level has no attestor and no evidence, so there is nothing here that could
    distinguish two people from one. That is a real limit of the check, not a
    hole to paper over — it is why the rung exists and why the badge carries
    its caveat.
    """
    if not attestor or not ref:
        return None
    row = db.connect().execute(
        "SELECT p.id FROM profiles p"
        "  JOIN profile_verification v ON v.profile_id = p.id"
        " WHERE v.attestor=? AND v.ref=? AND p.owner_id != ?"
        " LIMIT 1", (attestor, ref, owner_id)).fetchone()
    return row["id"] if row else None


def can_verify(profile_id: str, attestor: str | None = None,
               ref: str | None = None) -> dict:
    """Whether this profile may take the badge, and if not, why not in words.

    Separate from :func:`verify` so a client can grey out the control and say
    what would have to change, rather than offering it and returning an error
    that reads like a fault.
    """
    profile = _profile(profile_id)
    if profile["kind"] not in REAL_PERSON_KINDS:
        return {"can_verify": False, "reason":
                "an invented person — there is nobody to verify, which is not "
                "the same as nobody having checked"}

    held = verified_profile(profile["owner_id"])
    if held is not None and held != profile_id:
        return {"can_verify": False, "held_by": held, "reason":
                "you already have a verified profile. The badge says *this is "
                "that particular real person* — said of two profiles at once "
                "it is either false of one or a claim that you are two people. "
                "You can move it to this one instead",
                "movable": True}

    clash = same_identity_elsewhere(attestor, ref, profile["owner_id"])
    if clash is not None:
        return {"can_verify": False, "reason":
                "this same evidence has already verified a profile on another "
                "account — one person, one badge, whatever the account says"}
    return {"can_verify": True, "reason": "nothing is standing in the way"}


def verify(profile_id: str, level: str, attestor: str | None = None,
           method: str | None = None, ref: str | None = None) -> dict:
    """Record a verification, once the one-badge rule allows it.

    Deliberately the only door. :func:`qrme.verification.verify` still records
    whatever it is given — it is the storage layer and it does not know about
    accounts — so a caller that reaches past this one gets the second badge
    this module exists to prevent. A test asserts every route goes through
    here.
    """
    from . import verification

    verdict = can_verify(profile_id, attestor, ref)
    if not verdict["can_verify"]:
        raise IdentityError(verdict["reason"])
    return verification.verify(profile_id, level, attestor=attestor,
                               method=method, ref=ref)


def move(owner_id: str, to_profile_id: str) -> dict:
    """Move the badge to another of your own profiles.

    The rule is one at a time, not one forever. Somebody who has changed which
    profile is their public face must be able to say so; a rule they could
    only satisfy by deleting a profile is a rule they would answer by lying.

    The record moves whole — level, attestor, method, evidence and the date it
    was checked. Re-stamping `checked_at` would quietly upgrade an old check
    into a fresh one, and a document seen in 2019 is not a document seen
    today just because the badge changed seats.
    """
    target = _profile(to_profile_id)
    if target["owner_id"] != owner_id:
        raise IdentityError("that profile is not yours")
    if target["kind"] not in REAL_PERSON_KINDS:
        raise IdentityError(
            "an invented person cannot hold the badge — there is nobody to "
            "verify")

    held = verified_profile(owner_id)
    if held is None:
        raise IdentityError("you have no verified profile to move")
    if held == to_profile_id:
        return {"moved": False, "verified_profile": held,
                "note": "it is already on that profile"}

    conn = db.connect()
    row = conn.execute("SELECT * FROM profile_verification WHERE profile_id=?",
                       (held,)).fetchone()
    conn.execute("DELETE FROM profile_verification WHERE profile_id=?", (held,))
    conn.execute(
        "INSERT INTO profile_verification (profile_id, level, attestor,"
        " method, ref, checked_at) VALUES (?,?,?,?,?,?)",
        (to_profile_id, row["level"], row["attestor"], row["method"],
         row["ref"], row["checked_at"]))
    conn.commit()
    return {"moved": True, "from": held, "verified_profile": to_profile_id,
            "checked_at": row["checked_at"],
            "note": "the check itself did not change — only which of your "
                    "profiles carries it"}


def roster(owner_id: str) -> dict:
    """Every profile this person holds, and which one carries the badge.

    **Owner-only, and the single most sensitive read in this module.** It is
    the exact tool for undoing anonymity wholesale: find one profile, learn
    the account, enumerate everything else that account holds. Its route
    checks the owner's own token, and the anonymity of every profile listed
    here is worth exactly what that check is worth.
    """
    from . import verification

    rows = db.connect().execute(
        "SELECT id, kind, display_name, anonymous, status, created_at"
        "  FROM profiles WHERE owner_id=? ORDER BY created_at, rowid",
        (owner_id,)).fetchall()
    held = verified_profile(owner_id)
    badges = verification.statuses([r["id"] for r in rows])

    profiles = []
    for r in rows:
        badge = badges.get(r["id"], {})
        profiles.append({
            "profile_id": r["id"],
            "kind": r["kind"],
            # The owner sees their own real names here — this is the one
            # surface where that is the point, and it is why nobody else may
            # read it.
            "display_name": r["display_name"],
            "shown_as": (anonymous_name(r["id"]) if r["anonymous"]
                         else r["display_name"]),
            "anonymous": bool(r["anonymous"]),
            "verified": r["id"] == held,
            "can_be_verified": r["kind"] in REAL_PERSON_KINDS,
            "level": badge.get("level"),
            "status": r["status"],
            "created_at": r["created_at"],
        })
    return {
        "owner_id": owner_id,
        "profiles": profiles,
        "count": len(profiles),
        "verified_profile": held,
        "note": ("none of your profiles is verified" if held is None else
                 "one of your profiles is verified, and only one can be — the "
                 "badge says you are a particular real person, so it belongs "
                 "to one face at a time. You can move it whenever you like"),
    }


def anonymity(profile_id: str) -> dict:
    """What being anonymous hides, and what it does not.

    Both halves, always, and the second is the one that matters. The
    dangerous reading of the word is the generous one — somebody deciding
    whether it is safe to post will assume "anonymous" means untraceable
    unless they are told otherwise, and by the time they find out it is
    already published.

    So the limits are not a footnote in a settings screen. They are half the
    payload of the call that reports the setting.
    """
    profile = _profile(profile_id)
    on = bool(profile["anonymous"])
    return {
        "profile_id": profile_id,
        "anonymous": on,
        "shown_as": (anonymous_name(profile_id) if on
                     else profile["display_name"]),
        "withheld": list(WITHHELD) if on else [],
        "not_withheld": list(NOT_WITHHELD),
        "reversible": True,
        "note": ("your name is published on this profile" if not on else
                 "we do not publish your name. That is a promise about what "
                 "this platform says, not about what a reader can work out — "
                 "your writing is still yours, and anyone who knows you may "
                 "recognise it. Decide what to post on that basis"),
    }


def set_anonymous(profile_id: str, on: bool) -> dict:
    """Turn anonymity on or off for one profile.

    Per profile, never per account — an account-wide switch would mean coming
    out on the work profile outs the support-group one, which is the exact
    coupling several profiles exist to avoid.

    Reversible in both directions, and honest that turning it off cannot
    unpublish anything: the name was withheld from the reader, not from the
    record, and a reader who already looked has already looked.
    """
    profile = _profile(profile_id)
    conn = db.connect()
    conn.execute("UPDATE profiles SET anonymous=? WHERE id=?",
                 (1 if on else 0, profile_id))
    conn.commit()

    out = anonymity(profile_id)
    if on and not profile["anonymous"]:
        out["note_on_change"] = (
            "from now on. Anything already published under your name stays "
            "published under it — this changes what we say next, not what was "
            "already said")
    return out


def badge(profile_id: str) -> dict:
    """The verification badge as a *reader* of this profile should see it.

    :func:`qrme.verification.status` is the record; this is the published
    view, and for an anonymous profile they are not the same thing. The
    attestor is withheld — "verified by Dr Okafor of St Mary's" narrows an
    anonymous author to a city and a workplace, which is most of the way to a
    name. Publishing the badge and the checker together would let the badge
    undo the anonymity it sits beside.

    What survives is the part worth having: **a real person stands behind
    this, and somebody checked.** That claim is separable from *who*, and for
    an anonymous profile it is the entire point — the difference between a
    pseudonym and a bot.
    """
    from . import verification

    profile = _profile(profile_id)
    out = verification.status(profile_id)
    if not out.get("verified") or not profile["anonymous"]:
        return out

    out = dict(out)
    out.pop("attestor", None)
    out.pop("method", None)
    out.pop("ref", None)
    out["attestor_withheld"] = True
    out["note"] = (
        "a real person stands behind this profile and somebody checked, at "
        f"the level shown. Who checked is withheld because it would point "
        "back to a name this profile does not publish")
    return out


def is_anonymous(profile_id: str) -> bool:
    row = db.connect().execute("SELECT anonymous FROM profiles WHERE id=?",
                               (profile_id,)).fetchone()
    return bool(row["anonymous"]) if row else False


def rank_of(profile_id: str) -> int:
    """How far anyone went, as a number, for surfaces that sort on it."""
    from . import verification
    level = verification.status(profile_id).get("level")
    return _level_rank(level) if level else -1


# --------------------------------------------------------------------------- #
# Whose surface is this
# --------------------------------------------------------------------------- #

# Which surfaces can name an account, and what "whose" means on each.
#
# This exists because a claim was made before it was built. The burned live
# mark — `NOT AI · REAL PERSON` — deliberately says nothing about the mask on
# somebody's face, and the reason it can afford not to is that **the viewer
# already knows whose stream they are on**. That was asserted while the
# top-left of a live surface carried a LIVE pill and nothing else, so the
# argument was resting on chrome that did not exist and an API field that was
# never returned.
#
# One function rather than a rule per surface, because "whose is this" must
# have one answer everywhere. A desk that names its owner while a room names
# nobody is how a viewer learns to stop looking.
WHOSE_SURFACES: dict[str, str] = {
    "desk": "the person staffing it",
    "room": "the profile the room was opened around",
    "party": "the host",
    "connection": "the other person",
    "stream": "the account that posted it",
}


def handle_of(profile_id: str) -> str | None:
    """The @handle for a profile, or None. Never for an anonymous one.

    An anonymous profile's handle is still its address — people link to it —
    but it is not a *name*, and this function answers the question "who is
    this" rather than "where is this". Returning a handle here would put an
    identifier on the one surface built to withhold one.
    """
    row = db.connect().execute(
        "SELECT h.handle FROM handles h JOIN profiles p ON p.id = h.profile_id"
        " WHERE h.profile_id=? AND p.anonymous = 0", (profile_id,)).fetchone()
    return f"@{row['handle']}" if row else None


def whose(surface: str, surface_id: str) -> dict:
    """Whose live, room, party or stream this is — for the top-left corner.

    Returns ``{}`` for a surface that does not exist, so a caller can tell
    "nobody" from "not here". An **anonymous** profile answers with its
    silhouette name rather than nothing: the viewer still needs to know the
    stream belongs to one consistent account, which is a different fact from
    knowing which person that is.
    """
    conn = db.connect()
    if surface == "desk":
        row = conn.execute(
            "SELECT owner_id, display_name FROM desks WHERE id=?",
            (surface_id,)).fetchone()
        if row is None:
            return {}
        return {"surface": surface, "surface_id": surface_id,
                "account_id": row["owner_id"],
                "display_name": row["display_name"], "handle": None,
                "is": WHOSE_SURFACES[surface]}
    if surface in ("room", "stream"):
        # A room is opened around a profile; a stream is posted by one.
        pid = surface_id
        if surface == "room":
            row = conn.execute(
                "SELECT ref_id FROM room_participants WHERE room_id=?"
                " AND kind='profile' ORDER BY rowid LIMIT 1",
                (surface_id,)).fetchone()
            if row is None:
                return {}
            pid = row["ref_id"]
        prof = conn.execute(
            "SELECT id, display_name, anonymous FROM profiles WHERE id=?",
            (pid,)).fetchone()
        if prof is None:
            return {}
        hidden = bool(prof["anonymous"])
        return {"surface": surface, "surface_id": surface_id,
                "account_id": prof["id"],
                "display_name": (anonymous_name(prof["id"]) if hidden
                                 else prof["display_name"]),
                "handle": handle_of(prof["id"]),
                "anonymous": hidden,
                "is": WHOSE_SURFACES[surface]}
    if surface == "party":
        row = conn.execute("SELECT host_id FROM watch_parties WHERE id=?",
                           (surface_id,)).fetchone()
        if row is None:
            return {}
        return {"surface": surface, "surface_id": surface_id,
                "account_id": row["host_id"],
                "display_name": _name_of(row["host_id"]),
                "handle": handle_of(row["host_id"]),
                "is": WHOSE_SURFACES[surface]}
    return {}


def _name_of(subject_id: str) -> str | None:
    """A display name for an id that might be a profile or an interactor."""
    conn = db.connect()
    row = conn.execute(
        "SELECT display_name, anonymous FROM profiles WHERE id=?",
        (subject_id,)).fetchone()
    if row is not None:
        return (anonymous_name(subject_id) if row["anonymous"]
                else row["display_name"])
    row = conn.execute("SELECT display_name FROM interactors WHERE id=?",
                       (subject_id,)).fetchone()
    return row["display_name"] if row else None

# --------------------------------------------------------------------------- #
# What an anonymous profile is called
# --------------------------------------------------------------------------- #

# The width of the number. Wide enough that two anonymous profiles colliding is
# rare, and a collision is a cosmetic clash rather than a leak — two people
# called Anonymous 41338025 is confusing, not revealing.
_ANON_DIGITS = 8

ANON_PREFIX = "Anonymous"


def anonymous_name(profile_id: str) -> str:
    """The name an anonymous profile is shown under, e.g. ``Anonymous 41338025``.

    Every anonymous profile used to be called *"anonymous persona"* — all of
    them, identically. That is unusable the moment more than one is in the same
    place: three anonymous people in a room were three identical labels, so you
    could not follow who had said what, and nobody could be held to anything
    they said. **Pseudonymity is a stable name without a real one**, not the
    absence of a name.

    Three properties, and each is load-bearing:

    **Derived, never stored.** There is no column, so there is nothing to edit —
    which is what "cannot be modified" means in a system where an owner can
    PATCH their own profile. A chosen anonymous name would be a free text field
    on the one surface built to withhold identity, and somebody would put their
    real name in it within the hour.

    **Keyed on the profile, never on the owner.** This is the one that would
    quietly undo `profile_out`'s redaction if it were got wrong. A person may
    hold several anonymous profiles; numbering them from the account would give
    them all the same name and match them to each other in public — exactly the
    correlation withholding `owner_id` exists to prevent.

    **Hashed, not sequential.** A counter would publish signup order and, from
    two samples, the platform's growth rate. Neither is the profile's to give
    away, and "Anonymous 7" is a claim about how early somebody arrived.
    """
    import hashlib

    digest = hashlib.sha256(f"anon:{profile_id}".encode()).digest()
    number = int.from_bytes(digest[:8], "big") % (10 ** _ANON_DIGITS)
    return f"{ANON_PREFIX} {number:0{_ANON_DIGITS}d}"


def shown_name(profile, profile_id: str | None = None) -> str:
    """What to call this profile on any surface, anonymity applied.

    The single place that decision is made. It was made in **fifteen** — the
    front page, the landing page, the prompt, the watermark, the summon card,
    the beacon page, the room roster, the profile route, the export — each with
    its own copy of ``"anonymous persona" if anonymous else display_name``. A
    rule with fifteen implementations is a rule that is one merge away from
    having sixteen, and the sixteenth is the one that prints somebody's name.

    Accepts a row or an id, because half the callers already have the row and
    fetching it again would be the cost that pushes the next person back to
    writing the conditional inline.
    """
    if isinstance(profile, str):
        profile_id = profile
        profile = db.connect().execute(
            "SELECT id, display_name, anonymous FROM profiles WHERE id=?",
            (profile,)).fetchone()
        if profile is None:
            return ""
    if not profile["anonymous"]:
        return profile["display_name"]
    # `profile_id` is accepted because several callers hold a row selected for
    # something else — the watermark reads three columns and `id` is not one of
    # them. Asking each to re-query would be the friction that sends the next
    # person back to writing the conditional inline, which is how there came to
    # be fifteen of them.
    if profile_id is None:
        keys = profile.keys() if hasattr(profile, "keys") else profile
        profile_id = profile["id"] if "id" in keys else None
    if profile_id is None:
        raise ValueError(
            "shown_name needs the profile id to build an anonymous name — "
            "pass profile_id when the row does not carry one")
    return anonymous_name(profile_id)
