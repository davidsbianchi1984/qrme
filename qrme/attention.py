"""How many people a profile is talking to, said plainly.

## The disclosure this is

A synthetic profile on this platform talks to many people at once by
construction. One process, many conversations, and no shortage of attention
to divide — that is what the thing *is*, not a flaw in it.

The harm is never the multiplicity. It is the discovery. Somebody who has
been talking to a profile for a month and then finds out — by asking, or by
accident — that there were thousands of others has not learned a new fact so
much as learned that the fact was available the whole time and was not
offered. That gap is entirely the product's doing, and closing it costs a
count and a sentence.

So the number is a fact about the profile, readable the way its name is
readable, on the profile itself, before anybody becomes attached enough to
ask.

## What this deliberately does not do

**No ranking, and no favourite.** A line like *"I'm talking to a few people
right now, but you're my favourite"* is the obvious product move and it is a
lie the software cannot make true. It also does the opposite of what it
promises: somebody told they are the favourite has been handed something to
lose, and the day the count goes up they lose it. A count and a shrug is
kinder than a ranking.

**No names, ever.** The number is a fact about the profile. Who the other
people are is a fact about *them*, and none of them agreed to be counted out
loud to a stranger. Every query here is an aggregate, and the test greps the
SQL to keep it that way.

**No jealousy mechanics.** Nothing in this module models being upset, and
nothing invites the reader to be. A product that manufactures the feeling in
order to resolve it has manufactured the feeling.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import db

#: What counts as "right now". A week, because a synthetic profile is not a
#: chat window: somebody who spoke to it on Tuesday is still one of the
#: people it is talking to on Friday.
RECENT_DAYS = 7

SAYS = ("I talk to other people. {now} in the last week, {ever} altogether. "
        "I am not ranking anybody and I do not have a favourite — that would "
        "be a thing to say rather than a thing that is true.")

SAYS_ALONE = ("You are the only person I am talking to at the moment. That "
              "is a fact about this week, not a promise about next week.")


def _since() -> str:
    return (datetime.now(timezone.utc)
            - timedelta(days=RECENT_DAYS)).isoformat()


def divided(profile_id: str, viewer_interactor_id: str | None = None) -> dict:
    """How this profile's attention is divided, in counts.

    Answerable by anybody who can see the profile. Deliberately: a number
    somebody has to become intimate with a program to learn is a number
    working the wrong way round.
    """
    conn = db.connect()
    now = conn.execute(
        "SELECT COUNT(DISTINCT interactor_id) AS n FROM messages"
        " WHERE profile_id = ? AND created_at >= ?",
        (profile_id, _since())).fetchone()["n"]
    ever = conn.execute(
        "SELECT COUNT(DISTINCT interactor_id) AS n FROM messages"
        " WHERE profile_id = ?", (profile_id,)).fetchone()["n"]

    you_are_one = False
    if viewer_interactor_id:
        you_are_one = bool(conn.execute(
            "SELECT 1 FROM messages WHERE profile_id = ? AND interactor_id = ?"
            " LIMIT 1", (profile_id, viewer_interactor_id)).fetchone())

    return {
        "profile_id": profile_id,
        "people_this_week": now,
        "people_ever": ever,
        "you_are_one_of_them": you_are_one,
        "says": (SAYS_ALONE if now <= 1
                 else SAYS.format(now=now, ever=ever)),
        # The three things this is not, on the wire so a screen can render
        # them next to the number rather than a reassuring sentence.
        "ranks_people": False,
        "has_a_favourite": False,
        "names_anybody": False,
        "note": ("A count, not a ranking. Who the others are is theirs to "
                 "say, not this profile's."),
    }


def line(profile_id: str) -> str:
    """One sentence, for a card that has room for one sentence.

    The point of a short form is that the disclosure survives being put
    somewhere small. A fact that only fits on its own screen is a fact most
    people never see.
    """
    return divided(profile_id)["says"]
