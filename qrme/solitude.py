"""How much of somebody's talking here has been with software, and a door.

`attention.py` closed one half of the honesty problem: a profile talks to many
people, and the count is offered rather than discovered. This is the other
half, pointed the other way. A person can spend a great deal of time on this
platform in conversation that is entirely synthetic, and the platform is the
only party that can see that. Nothing was looking, and nothing offered a door.

## What this refuses to be

**Not a diagnosis.** This module does not decide anybody is lonely, and the
word does not appear in anything it returns. It cannot know: somebody with a
full life may talk to a profile every day for reasons of their own, and
somebody in real trouble may have a busy-looking week. What the software can
honestly see is a **ratio in its own logs** — how many of your turns here went
to a profile, and how many went to a person — and reporting a count is the
only claim it is entitled to make. The reader draws the conclusion; the
product does not draw it for them.

**Not a notification.** Nothing here is pushed, and no beat fires. A product
that watched somebody's conversations and then messaged them about it would be
doing the surveillance the count exists to disclose. :func:`shape` is a **pull
** — it answers when the person asks, and is silent every other minute of the
day.

**Not visible to anybody else.** A profile's owner cannot read this about the
people who talk to it, the platform has no aggregate view of it, and it is not
in any moderation queue. It is a fact about one person's own account, readable
by them.

**Never carries what was said.** The handoff below is a referral, and it is
built out of counts and a window. No message, no title, no profile name, no
topic. JIM-mini is a health guardian; a bridge from here that carried
conversation content would be handing a medical product the transcript of
somebody's private evenings, which is the exact trade this ecosystem exists to
refuse.

## What it does offer

JIM-mini is a different kind of thing from a profile — it does not perform a
personality, it is not a marketplace, and its whole surface is built around
somebody's own life rather than around holding attention. Handing that door to
somebody whose weeks here have been entirely synthetic is worth doing. Handing
it *unasked*, or handing it with the evening's messages attached, is not.

So `handoff()` requires an explicit `accept` from the person, mints a
referral carrying counts only, and records that it happened so the offer is
never made twice at somebody who already said no.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

from . import db

#: The window the shape is read over. Four weeks rather than a week: a quiet
#: fortnight is a fortnight, and the shorter the window the more this reads
#: like a mood ring rather than a pattern.
WINDOW_DAYS = 28

#: How much conversation there has to be before the ratio means anything. Two
#: turns that happen to both be with a profile is not a shape, and offering a
#: door on that evidence is the software being presumptuous about somebody it
#: has barely met.
MIN_TURNS = 20

#: The share of turns that has to be synthetic before the door is offered at
#: all. Not a cliff a person falls off — above it the offer appears in the
#: response, below it the same counts come back with no offer attached.
OFFER_AT = 0.95


def _since() -> str:
    return (datetime.now(timezone.utc)
            - timedelta(days=WINDOW_DAYS)).isoformat()


def _counts(interactor_id: str) -> dict:
    """Turns this person sent, split by who was on the other end.

    Only rows where **they** are the sender. A profile's replies are the
    profile's activity, and counting them would let a chatty profile move a
    number that is supposed to describe a person.
    """
    conn = db.connect()
    since = _since()
    to_profiles = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE interactor_id=? AND role='interactor'"
        " AND created_at >= ?", (interactor_id, since)).fetchone()[0]
    # The two places a turn on this platform reaches a human being: a matched
    # one-to-one connection, and a room.
    to_people = conn.execute(
        "SELECT COUNT(*) FROM connection_messages WHERE sender_id=?"
        " AND created_at >= ?", (interactor_id, since)).fetchone()[0]
    # `sender_kind` matters here: a room holds profiles and people side by
    # side, and counting a profile's turns in a room as this person's would
    # make the ratio describe the room instead of them.
    to_people += conn.execute(
        "SELECT COUNT(*) FROM room_messages WHERE sender_id=?"
        " AND sender_kind='user' AND created_at >= ?",
        (interactor_id, since)).fetchone()[0]
    return {"to_profiles": to_profiles, "to_people": to_people}


def _offer_row(interactor_id: str):
    return db.connect().execute(
        "SELECT * FROM solitude_offers WHERE interactor_id=?",
        (interactor_id,)).fetchone()


def shape(interactor_id: str) -> dict:
    """The counts, and — above the threshold — a door.

    Reads as a sentence about the software's own logs, which is the only thing
    it is entitled to say. `share_synthetic` is a ratio and is not called a
    score, because a score implies a scale somebody is being placed on.
    """
    counts = _counts(interactor_id)
    total = counts["to_profiles"] + counts["to_people"]
    share = round(counts["to_profiles"] / total, 4) if total else None

    body = {
        "interactor_id": interactor_id,
        "window_days": WINDOW_DAYS,
        "turns": counts,
        "total_turns": total,
        "share_synthetic": share,
        "enough_to_say": total >= MIN_TURNS,
        # Said in the response rather than left to a reader's assumption: the
        # absence of a `notice` field is not the absence of an opinion.
        "note": ("These are counts from this account's own logs over the last "
                 f"{WINDOW_DAYS} days. They are not an assessment of you, and "
                 "nobody else can read them."),
    }

    row = _offer_row(interactor_id)
    if row is not None:
        body["offer"] = {"state": row["state"], "at": row["decided_at"]}
        return body

    if body["enough_to_say"] and share is not None and share >= OFFER_AT:
        body["offer"] = {
            "state": "available",
            "what": "jim-mini",
            "why": ("Everything you have said here in this window went to a "
                    "profile. JIM-mini is a different kind of program — it is "
                    "built around your own week rather than around keeping "
                    "you here."),
            "carries": ["the two counts above", "the window in days"],
            "does_not_carry": ["anything you wrote", "which profiles",
                               "your name"],
            "accept_at": f"/interactors/{interactor_id}/solitude/handoff",
        }
    return body


class SolitudeError(Exception):
    def __init__(self, status: int, message: str):
        self.status, self.message = status, message
        super().__init__(message)


def handoff(interactor_id: str, accept: bool) -> dict:
    """Take the door, or close it. Both are recorded; neither is reversible
    by anybody but this person.

    `accept=False` is not a no-op and is the more important half. An offer a
    person declined that reappears next month is the product overriding an
    answer it already got, and the second asking is worse than the first.
    """
    counts = _counts(interactor_id)
    total = counts["to_profiles"] + counts["to_people"]
    if accept and total < MIN_TURNS:
        raise SolitudeError(
            409, "there is not enough conversation here to hand anything over")

    conn = db.connect()
    now = db.utcnow()
    state = "accepted" if accept else "declined"
    referral = None
    if accept:
        referral = {
            "ref": "sol_" + uuid.uuid4().hex[:16],
            # Counts and a window. Nothing else crosses, and
            # `test_the_referral_carries_no_word_anybody_wrote` is what holds
            # this to it rather than this comment.
            "window_days": WINDOW_DAYS,
            "turns": counts,
            "issued_at": now,
            "product": "jim-mini",
        }
    conn.execute(
        "INSERT INTO solitude_offers (interactor_id, state, referral,"
        " decided_at) VALUES (?, ?, ?, ?)"
        " ON CONFLICT (interactor_id) DO UPDATE SET state=excluded.state,"
        " referral=excluded.referral, decided_at=excluded.decided_at",
        (interactor_id, state, json.dumps(referral) if referral else None, now))
    conn.commit()
    return {"interactor_id": interactor_id, "state": state,
            "referral": referral}


def referral(interactor_id: str) -> dict | None:
    """What JIM-mini would be handed, readable by the person first.

    A referral somebody cannot look at before it travels is a referral they
    did not really consent to.
    """
    row = _offer_row(interactor_id)
    if row is None or not row["referral"]:
        return None
    return json.loads(row["referral"])
