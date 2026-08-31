"""Telling a synthetic seat, out loud in a room, to go and do something.

## What this adds

`roomreach` decides what a profile in a room *may* reach. This is the
other half: turning a person's words in that room into a profile actually
putting its hands on a surface.

    asked     the profiles with connections should be verbally commanded
              or prompted to take action — cursor, screen, eyes, ears,
              hands, body
    mattered  a permission nobody can spend is a permission that does
              nothing

The machinery to act already existed and was reachable only by an owner:
`hands.grant_from_words` writes an authority from a sentence, `open_reach`
begins a session, `decide` sees and moves. None of it could be reached
from a room, which is where the person and the profile are actually
talking — so a room could agree that a seat may drive a browser and had
no way to ask it to.

## Both keys, spent rather than merely held

Nothing here writes a permission. That is the whole design:

* the **owner's** key is a live `hand_grant` on that profile, written by
  its owner, naming its places, verbs, minutes and steps;
* the **room's** key is that grant ticked in this room;
* and this function spends them — it can only pick among grants that
  already pass both, and it narrows further by what the words name.

So a person in a room can ask a profile they do not own to do something
for them, which is the point ("they all can become agents for the user,
even if they're being outsourced from other users") — and cannot thereby
obtain anything its owner did not already write down.

## Why a refusal names which key is missing

"It won't do it" is the answer that makes somebody try the same sentence
five times. The two keys fail for opposite reasons and have opposite
remedies: an owner has to grant, or somebody in this room has to tick a
box that is already on their screen. The refusal says which.
"""

from __future__ import annotations

from . import hands, roomreach


class ErrandError(ValueError):
    """An errand that cannot be sent. Text meant for a person."""


def _usable(profile_id: str, room_id: str) -> list[dict]:
    """The grants this room may spend on this profile — both keys turned.

    Read fresh every time rather than trusted from a moment ago: an owner
    can revoke while a room is talking, and a tick outlives nothing.
    """
    return [g for g in hands.grants(profile_id, live_only=True)
            if roomreach.allows(room_id, profile_id, "skill", g["id"])]


def _fits(grant: dict, said: str) -> bool:
    """Whether the words stay inside what this grant already permits.

    A grant names its places. Words that name a place outside them are not
    a narrower version of that grant — they are a different one — so they
    are refused rather than quietly run against whatever the grant did
    allow. Words that name no place at all fit any grant: "read this
    screen and tell me what it says" is an errand about the surface in
    front of it, not about an app somewhere else.

    Checked in the GRANT's vocabulary, not the grant-writer's.
    `hands.places_in` exists to turn a sentence into places worth
    granting, and it speaks two languages at once — catalog app ids and
    host fragments — so `mail.google.com` comes back as `['mail',
    'mail.google']`, neither of which equals the place an owner actually
    wrote. Comparing those two lists refused every errand, including the
    ones the grant plainly covered. The right question is the other way
    round: does this sentence mention somewhere this grant already
    allows.

    Worth having at all because `act` does not check places. It holds the
    grant's life, its verbs, its step budget and the refusal to type a
    secret — places are enforced where a grant is written and where one
    is narrowed, so for a reach opened from a room this is the only place
    they are checked.
    """
    low = (said or "").lower()
    if any(str(p).lower() in low for p in grant["places"]):
        return True
    return not hands.places_in(said)


def send(room_id: str, profile_id: str, said: str, by: str,
         platform: str = "web") -> dict:
    """Open a reach from what somebody said in a room.

    The mode is decided by the grant rather than by the sentence. A grant
    written for eyes only opens a `watching` reach whatever the words ask
    for, because the alternative is a sentence widening a permission — and
    the whole shape of this is that words can only narrow.
    """
    said = (said or "").strip()
    if not said:
        raise ErrandError("nothing was said")

    live = hands.grants(profile_id, live_only=True)
    if not live:
        raise ErrandError(
            "its owner has not given this profile hands — nobody in this "
            "room can grant that, and until they do there is nothing here "
            "to allow")

    usable = _usable(profile_id, room_id)
    if not usable:
        raise ErrandError(
            "this room has not allowed any of what its owner granted — "
            "tick a skill on this seat first, and the box is on this "
            "screen")

    fitting = [g for g in usable if _fits(g, said)]
    if not fitting:
        places = sorted({p for g in usable for p in g["places"]})
        raise ErrandError(
            "that names somewhere this profile is not allowed in here — "
            "what it may reach is " + ", ".join(places))

    # The narrowest first: a grant that only looks is a smaller thing to
    # spend than one that can type, so an errand a watching grant can
    # carry is carried by that one.
    grant = sorted(
        fitting,
        key=lambda g: (0 if all(v in hands.EYES_ONLY for v in g["verbs"])
                       else 1, len(g["verbs"])))[0]
    watching = all(v in hands.EYES_ONLY for v in grant["verbs"])

    reach = hands.open_reach(profile_id, grant["id"], errand=said,
                             platform=platform,
                             mode="watching" if watching else "acting")
    return {**reach, "room_id": room_id, "asked_by": by,
            "grant_id": grant["id"], "eyes_only": watching}
