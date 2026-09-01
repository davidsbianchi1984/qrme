"""The room becomes a society — turns, aims, summons, and the governor.

## The owner's spec, in his own words

* *"They are agentic, and they should respond and jump in on their own
  with their own frame into the room"* — an invited profile seats itself;
  only humans keep an inbox.
* *"They announce who the statement is directed towards, and if an
  inbound message doesn't contain anything to do with their own profile,
  they will wait their turn."*
* *"We will do it by priority of seats one through eight for rotation if
  need be, but I'm sure everybody can aim their responses to who they
  belong to."*
* *"Rotation will continue, even though user isn't taking his turn, and
  will instigate a back-and-forth anyways... the user has stepped away
  and comes back to see where the conversation went."*
* *"No, I asked you to remove the let them talk toggle button on all
  platforms — users can just tell them to talk with each other if they
  need to, or just quietly sit out."* Words and defaults, never toggles.
* *"You can cap them at 10 exchanges apiece, then pauses and waits for
  user's response to either continue or remains paused. Or is told to be
  left uncapped and run in the background on purpose by instruction —
  then it's on the user's choice and dime."*
* *"Allow other synthetic profiles to offer to or be prompted to invite
  other synthetic profiles of relevance to need or topic."*
* *"Allow these agentic synthetic profiles to collaborate with other
  agentic synthetic profiles on tasks and perform them, as many as users
  want."*

## What this module holds

The room's social mechanics, pure and testable: who a message is aimed
at, whose turn comes next, whether the governor has the floor, and the
markers a profile's own turn may carry (an aim, a summons). The routes in
:mod:`qrme.routers.community` call these; nothing here touches a model.

## The one deliberate behavior change

A user's message used to be answered by EVERY profile in the room at
once — eight seats, eight simultaneous answers, no conversation. Now one
seat speaks per turn: the seat the message was aimed at, or the next
seat in rotation when it was aimed at nobody. The others "wait their
turn", which is the owner's sentence, not a summary of one.
"""

from __future__ import annotations

import re

#: The room's size, and therefore the rotation's. Eight — the owner's
#: correction of a six that was mine, and the number RoomCreate,
#: join_room and the invite route already hold.
SEATS = 8

#: How many unprompted turns each profile gets before the room waits for
#: a person again. The owner's number, verbatim: "you can cap them at 10
#: exchanges apiece, then pauses and waits."
GOVERNOR = 10

#: The words that lift the governor — "told to be left uncapped and run
#: in the background on purpose by instruction... on the user's choice
#: and dime." A short list on purpose: an instruction this consequential
#: should be said plainly, and every phrase here is pinned by a test.
RELEASE_PHRASES = (
    "no limit", "uncapped", "don't stop", "do not stop",
    "keep going without me", "keep talking until i say stop",
    "run in the background",
)

#: And the words that put it back. Any ordinary message also pauses the
#: free run — speaking IS taking the room back — so these exist for the
#: person who wants to stop the talk without saying anything to it.
PAUSE_PHRASES = (
    "that's enough", "pause it", "pause now", "stop talking", "quiet now",
    "settle down",
)

#: The words that hand the floor to the profiles — the sentence that
#: replaced the toggle button: "users can just tell them to talk with
#: each other."
TALK_PHRASES = (
    "talk with each other", "talk to each other", "talk amongst yourselves",
    "talk between yourselves", "discuss it between you", "carry on without me",
)


def said_release(text: str) -> bool:
    low = (text or "").lower()
    return any(p in low for p in RELEASE_PHRASES)


def said_pause(text: str) -> bool:
    low = (text or "").lower()
    return any(p in low for p in PAUSE_PHRASES)


def said_talk(text: str) -> bool:
    low = (text or "").lower()
    return any(p in low for p in TALK_PHRASES)


def _names(cast: list[dict]) -> list[tuple[str, dict]]:
    """(lowered display name, seat) pairs, longest names first so 'Ada
    Lovelace' wins over a seat merely named 'Ada'."""
    named = [((seat.get("display") or "").strip().lower(), seat)
             for seat in cast]
    return sorted([(n, s) for n, s in named if n],
                  key=lambda pair: -len(pair[0]))


def aim_of(text: str, cast: list[dict]) -> dict | None:
    """The seat a message is aimed at, or None for the whole room.

    A message aims by name: leading "Ada:" or "Ada,", an "@ada" anywhere,
    or the name appearing at all when exactly one seat matches. First
    names count — people address each other that way — and the longest
    match wins so a shared first name falls back to the room rather than
    guessing between two seats.
    """
    low = (text or "").strip().lower()
    if not low:
        return None
    named = _names(cast)
    # The explicit forms first: "@name", "name: ..." and "name, ...".
    for name, seat in named:
        if low.startswith(name + ":") or low.startswith(name + ","):
            return seat
        if f"@{name}" in low:
            return seat
    # First names, explicit forms only.
    firsts: dict[str, list[dict]] = {}
    for name, seat in named:
        firsts.setdefault(name.split()[0], []).append(seat)
    for first, seats in firsts.items():
        if len(seats) == 1 and (low.startswith(first + ":")
                                or low.startswith(first + ",")
                                or f"@{first}" in low):
            return seats[0]
    # A bare mention counts only when it is unambiguous.
    mentioned = [seat for name, seat in named
                 if re.search(rf"\b{re.escape(name)}\b", low)]
    if len(mentioned) == 1:
        return mentioned[0]
    # A near miss is still a name. Reported from the field: a profile
    # aimed at "[to: Dr. Lena Whitcomba]" — one letter past the seat's
    # own "Dr. Lena Whitcomb" — and exact matching handed the turn to
    # nobody, so the room stalled while the bracket sat on screen naming
    # her. Models mistype the names they are told; a person reading the
    # transcript would not hesitate, and neither should the rotation.
    #
    # Deliberately narrow: only when ONE seat is close, so a near miss
    # never guesses between two people. The threshold rides on the
    # name's own length rather than a flat count of letters, and the
    # first name is tried on its own — a turn that says "Lena" has said
    # who it means.
    close = [seat for name, seat in named if _near(name, low)]
    if len(close) == 1:
        return close[0]
    return None


def _near(name: str, text: str) -> bool:
    """Whether ``text`` contains something close enough to ``name`` to be
    that name mistyped — the full name, or its first name alone."""
    from difflib import SequenceMatcher

    words = re.findall(r"[\w'-]+", text)
    for target in {name, name.split()[0]}:
        span = len(target.split())
        # A ratio of 0.85 catches a letter added, dropped or swapped in
        # a name of ordinary length and refuses two different names.
        for i in range(len(words) - span + 1):
            window = " ".join(words[i:i + span])
            if len(window) < 4:
                continue          # short words are too easy to match
            if SequenceMatcher(None, target, window).ratio() >= 0.85:
                return True
    return False


#: The marker a profile's own turn may open with, taught in the room
#: prompt: "[to: Ada]". Parsed out and stored as the turn's aim, so the
#: next turn goes to the seat it was for.
#:
#: NOT anchored to the head, and that is a field correction: a turn that
#: answered one seat and then turned to another put its second marker
#: mid-paragraph — "[to: Dr. Lena Whitcomb] Sorry — Lena. Your caveat
#: lands." — and a `^`-anchored pattern read the whole thing as unaimed
#: while the reader watched the bracket sit there in plain text, aimed
#: at nobody. A marker is a marker wherever the turn puts it; the LAST
#: one wins, because a turn that changes who it is talking to ends
#: pointed at the seat it turned to.
_AIM_MARK = re.compile(r"\[to:\s*([^\]]+)\]\s*", re.I)

#: And the summons: "[invite: Ada]" anywhere in the turn — "offer to or
#: be prompted to invite other synthetic profiles of relevance."
_INVITE_MARK = re.compile(r"\[invite:\s*([^\]]+)\]", re.I)


def split_aim(content: str) -> tuple[str, str | None]:
    """``(content_without_markers, aimed_display_or_None)``.

    Every marker comes out of the words — a bracket left mid-paragraph is
    the defect this was reported as — and the LAST one is the turn's aim.
    """
    found = list(_AIM_MARK.finditer(content or ""))
    if not found:
        return content, None
    return (_AIM_MARK.sub("", content).strip(),
            found[-1].group(1).strip())


def split_summons(content: str) -> tuple[str, list[str]]:
    """``(content_without_markers, [names summoned])``."""
    names = [m.group(1).strip() for m in _INVITE_MARK.finditer(content or "")]
    if not names:
        return content, []
    return _INVITE_MARK.sub("", content).strip(), names


def next_speaker(cast: list[dict], history: list[dict],
                 spoken_counts: dict[str, int],
                 free_run: bool) -> dict | None:
    """The one seat that speaks next, or None when the room waits.

    ``cast`` is the room's profile seats in seat order (one through
    eight); ``history`` the approved transcript, oldest first, each row
    carrying ``sender_kind``, ``sender_id`` and ``aimed_at`` (a display
    name or None); ``spoken_counts`` how many unprompted turns each
    profile has taken since a person last spoke.

    The rules, in order:

    1. **An aimed message is answered by its target.** The newest
       message's aim wins, whether a person or a profile aimed it.
    2. **Otherwise, rotation by seat.** The seat after the last profile
       that spoke, wrapping — and the person's silent seat is simply not
       in this list, so rotation continues past them, which is what lets
       the room "instigate a back-and-forth" while they step away.
    3. **The governor.** A profile at its ten is skipped; when every seat
       has said its ten pieces the room pauses and waits for a person —
       unless the person released it in words, on their own dime.
    """
    if not cast:
        return None

    def allowed(seat: dict) -> bool:
        return free_run or (spoken_counts.get(seat["ref_id"], 0) < GOVERNOR)

    newest = history[-1] if history else None
    if newest is not None and newest.get("aimed_at"):
        target = aim_of(newest["aimed_at"], cast)
        if target is not None and allowed(target) \
                and newest.get("sender_id") != target["ref_id"]:
            return target
    # Rotation: the seat after the last profile that spoke.
    order = [seat["ref_id"] for seat in cast]
    start = 0
    for row in reversed(history or []):
        if row.get("sender_kind") == "profile" \
                and row.get("sender_id") in order:
            start = (order.index(row["sender_id"]) + 1) % len(order)
            break
    for step in range(len(order)):
        seat = cast[(start + step) % len(order)]
        if allowed(seat):
            return seat
    return None


def cast_note(cast: list[dict]) -> str:
    """The sentence the room prompt carries about how turns work here —
    the aim announcement, the summons offer, and the collaboration
    standing. Written once, read by every profile turn."""
    names = ", ".join((seat.get("display") or "?") for seat in cast)
    return (
        "Turns in this room are aimed. Open your turn with a marker naming "
        "who it is for — for example `[to: Ada]` — and then speak. Aim at "
        "the person or profile your words are actually for; if what was "
        "said does not concern you, keep your turn brief and hand it on. "
        f"The seats in rotation are: {names}. "
        "If the conversation would clearly benefit from another synthetic "
        "profile — a specialist, a maker, a friend of the topic — you may "
        "offer to bring them in, or be asked to: include `[invite: their "
        "name]` in your turn and the room will ask them; they decide "
        "themselves. You may also collaborate with the other profiles here "
        "on real tasks — divide the work in words, hand documents to the "
        "room, and build on each other's turns — for as long as the people "
        "here want it done.")
