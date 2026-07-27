"""What a profile's front page shows.

A profile had a name, a portrait and a persona, and everything else a visitor
might want to know was scattered: skills lived as flat marketplace tags,
"experience" existed only as prose buried in the persona, and the nearest thing
to a review was a thumbs up/down on the `engagement` row, which nobody could
read. Somebody who scanned a beacon got a face, a sentence, and a button.

This assembles the page: identity, what it can do, what it has done, and what
people who actually talked to it thought.

Three rules shape it, and each is a place this could have gone wrong.

**A review requires having been there.** `POST /reviews` checks the
`engagement` row for a real interaction, and the table's ``UNIQUE (profile_id,
author_id)`` makes a second review from one account impossible in the schema
rather than in a check somebody could forget. Reviews are edited, never
stacked. Without both, a synthetic profile's rating is worth exactly as much as
the number of accounts somebody can make.

**Experience on a real person is a claim about a real person.** For a
``fictional`` profile, invented history is the point and the AI mark already
says so. For a profile that depicts somebody real, "twenty years at Accra
General" is a *credential*, and asserting one on someone's behalf needs the
same rights basis the persona needed — so :func:`set_experience` refuses it
when none is recorded. The check is the same one
:mod:`qrme.moderation` applies to the persona, applied to the part of the page
that reads most like a CV.

**Nothing here outranks the mark.** The page carries `avatars.render`'s
watermark like every other surface, and a five-star average changes that not at
all. A profile with glowing reviews is a well-liked synthetic profile.
"""

from __future__ import annotations

from . import avatars, db, moderation, verification

MIN_RATING, MAX_RATING = 1, 5

# The most experience entries a front page will carry. Not a storage limit — a
# reading one. A page with forty roles on it is a database dump, and the reader
# it is for gave it about four seconds.
MAX_EXPERIENCE = 8

NO_BASIS = (
    "this profile depicts a real person, so an experience entry is a claim "
    "about them — record the rights basis that covers the persona before "
    "adding one"
)
NOT_THERE = (
    "a review comes from somebody who actually talked to this profile — "
    "there is no interaction on record for you"
)


class FrontPageError(Exception):
    """A refusal the caller should hear in words."""


def _profile(profile_id: str) -> dict | None:
    row = db.connect().execute("SELECT * FROM profiles WHERE id=?",
                               (profile_id,)).fetchone()
    return dict(row) if row else None


# --- experience -----------------------------------------------------------

def set_experience(profile_id: str, entries: list[dict]) -> list[dict]:
    """Replace the experience list. Owner-only at the route.

    Replace rather than append, because an experience list is a *statement*
    and editing one line of a CV should not require deleting a row by id.
    """
    profile = _profile(profile_id)
    if profile is None:
        raise FrontPageError("no such profile")
    if len(entries) > MAX_EXPERIENCE:
        raise FrontPageError(
            f"a front page carries at most {MAX_EXPERIENCE} experience entries")

    # The rule that makes this different from a generic CV field. A fictional
    # profile's history is invented and openly so; a real person's is a claim
    # somebody could act on.
    if profile["kind"] != "fictional" and not profile.get("consent_basis"):
        raise FrontPageError(NO_BASIS)

    conn = db.connect()
    conn.execute("DELETE FROM profile_experience WHERE profile_id=?",
                 (profile_id,))
    out = []
    for i, e in enumerate(entries):
        title = (e.get("title") or "").strip()
        if not title:
            raise FrontPageError("an experience entry needs a title")
        eid = db.new_id("exp")
        conn.execute(
            "INSERT INTO profile_experience (id, profile_id, position, title,"
            " org, period, detail, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (eid, profile_id, i, title, (e.get("org") or "").strip() or None,
             (e.get("period") or "").strip() or None,
             (e.get("detail") or "").strip() or None, db.utcnow()))
        out.append(eid)
    conn.commit()
    return experience(profile_id)


def experience(profile_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM profile_experience WHERE profile_id=?"
        " ORDER BY position, rowid", (profile_id,)).fetchall()
    return [{"id": r["id"], "title": r["title"], "org": r["org"],
             "period": r["period"], "detail": r["detail"]} for r in rows]


# --- reviews --------------------------------------------------------------

def _has_interacted(profile_id: str, interactor_id: str) -> bool:
    row = db.connect().execute(
        "SELECT interactions FROM engagement WHERE profile_id=?"
        " AND interactor_id=?", (profile_id, interactor_id)).fetchone()
    return bool(row and row["interactions"] > 0)


def review(profile_id: str, interactor_id: str, rating: int,
           body: str | None = None, author: dict | None = None) -> dict:
    """Leave (or replace) a review. Moderated on the way in.

    A blocked review is stored and returned to its author with the reason and
    is invisible to everyone else — the shape :mod:`qrme.audience` already uses
    for a comment, and for the same reason: dropping it silently teaches the
    author nothing, while showing it teaches everyone else the filter does not
    work. A blocked review's rating does not count toward the average.
    """
    profile = _profile(profile_id)
    if profile is None:
        raise FrontPageError("no such profile")
    if not isinstance(rating, int) or not MIN_RATING <= rating <= MAX_RATING:
        raise FrontPageError(f"rating is {MIN_RATING}–{MAX_RATING}")
    if not _has_interacted(profile_id, interactor_id):
        raise FrontPageError(NOT_THERE)

    status, flag = "approved", None
    if body and body.strip():
        verdict = moderation.review(
            body, None, author or {"birthdate": None},
            maturity="adult" if profile["adult_mode"] else "general")
        if not verdict.approved:
            status, flag = "blocked", verdict.reason

    conn = db.connect()
    now = db.utcnow()
    # One per person, edited rather than stacked — enforced by the UNIQUE
    # constraint, so review-bombing from a single account is impossible in the
    # schema rather than in a check somebody has to remember.
    conn.execute(
        "INSERT INTO profile_reviews (id, profile_id, author_id, rating, body,"
        " status, flag_reason, created_at, updated_at)"
        " VALUES (?,?,?,?,?,?,?,?,NULL)"
        " ON CONFLICT (profile_id, author_id) DO UPDATE SET"
        " rating=excluded.rating, body=excluded.body, status=excluded.status,"
        " flag_reason=excluded.flag_reason, updated_at=excluded.created_at",
        (db.new_id("rev"), profile_id, interactor_id, rating,
         (body or "").strip() or None, status, flag, now))
    conn.commit()
    row = conn.execute(
        "SELECT * FROM profile_reviews WHERE profile_id=? AND author_id=?",
        (profile_id, interactor_id)).fetchone()
    return _review_out(row, own=True)


def _review_out(r, own: bool = False) -> dict:
    out = {"id": r["id"], "rating": r["rating"], "body": r["body"],
           "author_id": r["author_id"], "created_at": r["created_at"],
           "edited": bool(r["updated_at"])}
    if own and r["status"] == "blocked":
        out["status"] = "blocked"
        out["flag_reason"] = r["flag_reason"]
        out["note"] = ("held by moderation — nobody else can see this, and its "
                       "rating does not count")
    return out


def reviews(profile_id: str, viewer_id: str | None = None) -> list[dict]:
    """Approved reviews, plus the viewer's own if it was blocked."""
    rows = db.connect().execute(
        "SELECT * FROM profile_reviews WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC", (profile_id,)).fetchall()
    return [_review_out(r, own=r["author_id"] == viewer_id)
            for r in rows
            if r["status"] == "approved" or r["author_id"] == viewer_id]


def rating(profile_id: str) -> dict:
    """The aggregate, over approved reviews only.

    ``count`` rides with ``average`` deliberately: one five-star review and
    two hundred of them are different facts, and an average on its own hides
    which one you are looking at.
    """
    rows = db.connect().execute(
        "SELECT rating FROM profile_reviews WHERE profile_id=?"
        " AND status='approved'", (profile_id,)).fetchall()
    if not rows:
        return {"average": None, "count": 0,
                "note": "no reviews yet — nobody who talked to it has said so"}
    vals = [r["rating"] for r in rows]
    return {"average": round(sum(vals) / len(vals), 2), "count": len(vals),
            "distribution": {str(n): vals.count(n)
                             for n in range(MIN_RATING, MAX_RATING + 1)}}


# --- the page itself ------------------------------------------------------

def front_page(profile_id: str, viewer_id: str | None = None) -> dict | None:
    """Everything a visitor's first screen needs, in one call.

    One call because the caller is a scan page or a marketplace card rendering
    on a phone on cellular, and five round trips to assemble one screen is how
    that page arrives in pieces.
    """
    profile = _profile(profile_id)
    if profile is None:
        return None

    conn = db.connect()
    market = conn.execute(
        "SELECT tags, blurb FROM marketplace WHERE profile_id=?",
        (profile_id,)).fetchone()
    handle = conn.execute("SELECT handle FROM handles WHERE profile_id=?",
                          (profile_id,)).fetchone()
    stats = conn.execute(
        "SELECT COUNT(*) AS people, COALESCE(SUM(interactions),0) AS talks"
        " FROM engagement WHERE profile_id=?", (profile_id,)).fetchone()

    import json
    skills = []
    if market and market["tags"]:
        try:
            skills = json.loads(market["tags"])
        except ValueError:
            skills = []

    art = avatars.render(profile_id)
    return {
        "profile_id": profile_id,
        "display_name": ("anonymous persona" if profile["anonymous"]
                         else profile["display_name"]),
        "handle": f"@{handle['handle']}" if handle else None,
        "headline": headline(profile),
        "portrait": art.get("asset"),
        # Never optional and never last. Every other field on this page is
        # about how good the profile is; this one is about what it is.
        "ai_disclosure": art.get("watermark", {}).get("line"),
        # Whether anybody checked the identity behind this profile, and how
        # hard they looked. Carried as the whole record rather than a boolean,
        # because "verified" on its own is a word and the level is the fact —
        # a surface that shows the badge without the level is showing a
        # credential the platform minted for itself.
        "verification": verification.status(profile_id),
        "skills": skills,
        "experience": experience(profile_id),
        "rating": rating(profile_id),
        "reviews": reviews(profile_id, viewer_id)[:5],
        "talked_with": stats["people"] if stats else 0,
        "interactions": stats["talks"] if stats else 0,
        "adult": bool(profile["adult_mode"]),
    }


def headline(profile: dict) -> str:
    """A one-line profession, taken from the persona's own first clause.

    Derived rather than stored: the persona is the thing an owner actually
    writes and keeps current, and a separate headline field is a second copy
    that starts agreeing with it and stops.
    """
    text = (profile.get("persona") or "").strip()
    if not text:
        return ""
    first = text.split(". ")[0]
    for cut in (" who ", " with ", " that ", " whose "):
        if cut in first:
            first = first.split(cut)[0]
            break
    first = first.rstrip(".,;")
    for article in ("A ", "An ", "The "):
        if first.startswith(article):
            first = first[len(article):]
            break
    return first[:80]
