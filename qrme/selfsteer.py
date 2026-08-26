"""The profile turns its own dials, when the person asks it to.

The dials existed and the rail put them beside the face — but the rail is
the owner's hand. The person actually talking had to hope the owner was
around: "be funnier" was a wish about a slider three screens and one
credential away.

    asked     make the adjustments when I tell you to
    mattered  the one being asked could not reach its own dials

So the profile can. Asked to come across differently, it writes the move
into its reply the way it hands over a document (qrme/composing.py): a
marker the person never reads, taken out of the spoken text and applied
to the same steering store the owner's sliders write. The reply says in
ordinary words what changed; the marker carries the mechanics.

## The step, and why it is fixed

One step is 25, always. The owner's ask was "steady intervals, maybe
like +25 or -25" — and a fixed step is also the safety shape: a model
cannot leap a dial from 0 to 100 on one enthusiastic reading of a
request. Ask again, it steps again. `steering.set_dials` clamps to
0–100 and hard-clamps intimacy on a non-adult profile, exactly as it
does for the sliders.

## The owner's veto

`steering.lock` predates this feature and its own docstring anticipated
it: while the lock stands, *any future automation* is refused. This is
that automation. A locked profile's turn still lands; the dials do not
move; the reply carries a sentence saying so — never a change that
quietly failed, never a failure that quietly changed nothing.
"""

from __future__ import annotations

import re

from . import steering

#: Any marker-shaped block comes OUT of the spoken text, valid or not — a
#: person should never read one (the composing lesson). Only the strict
#: shape below is also a move. Four ops, the owner's own list — "+/- 25
#: intervals or max or none" — and `all` where a dial name would stand,
#: for the person who asks for everything at once.
_ANY = re.compile(r"\[\[\s*dial:[^\]]*\]\]")
_MOVE = re.compile(r"\[\[\s*dial:\s*([a-z_]+)\s*([+-]25|max|none)\s*\]\]")

#: One step, the owner's own number.
STEP = 25


def split(reply: str) -> tuple[str, dict[str, str]]:
    """Separate the words from the moves.

    Returns ``(spoken, moves)`` where moves maps a dial name — or
    ``all`` — to one of ``+25``, ``-25``, ``max``, ``none``. A malformed
    marker (wrong step, unknown shape) is stripped and moves nothing; an
    unknown dial name survives to `apply`, where set_dials ignores it —
    same forgiveness, one place each.
    """
    if not reply or "[[" not in reply:
        return reply, {}
    moves: dict[str, str] = {}
    for name, op in _MOVE.findall(reply):
        # The same dial twice in one turn is still one move — "steady
        # intervals" means a turn moves a dial once, not as many times
        # as the model repeats itself. The last word wins.
        moves[name] = op
    spoken = _ANY.sub("", reply)
    spoken = re.sub(r"[ \t]+\n", "\n", spoken)
    spoken = re.sub(r"\n{3,}", "\n\n", spoken).strip()
    return spoken, moves


def _target(op: str, current: int) -> int:
    if op == "max":
        return 100
    if op == "none":
        return 0
    return current + (STEP if op == "+25" else -STEP)


def apply(profile_id: str, moves: dict[str, str], adult: bool) -> bool:
    """Move the dials. True when they moved, False when the lock held.

    ``all`` fans one op out to every dial. Built on `steering.set_dials`,
    so the clamps, the intimacy rule and the lock are the same ones the
    owner's sliders live under — a second write path with its own rules
    is how doors drift apart.
    """
    if not moves:
        return True
    current = steering.get(profile_id)
    want: dict[str, int] = {}
    if "all" in moves:
        op = moves["all"]
        want = {name: _target(op, current[name]) for name in steering.DIALS}
    for name, op in moves.items():
        if name in steering.DIALS:
            want[name] = _target(op, current[name])
    if not want:
        return True
    try:
        steering.set_dials(profile_id, want, adult)
    except steering.SteeringLocked:
        return False
    return True


#: The sentence a locked profile's reply carries. Translated through
#: i18n._PUBLIC, beside "Here it is."
LOCKED_SENTENCE = "My dials are locked, so nothing moved."


def guidance(adult: bool) -> str:
    """What the profile is told, beside the composing fence.

    A permission with a fixed step: the profile may move its own dials
    when asked, one step of 25 at a time, and never unprompted — a
    profile that re-tunes itself on a hunch is the drift the persona
    prompt already forbids.
    """
    # Every dial with both of its ends — the names alone taught only the
    # obvious mappings, and the field caught it: "it was supposed to be
    # for all of the modifications, not just humor." A model that reads
    # "agreeableness (contrarian, pushes back <-> accommodating, goes
    # along)" can map "push back more" to -25 on the right dial; a model
    # that reads the bare word cannot.
    dials = "\n".join(
        f"- {n}: 0 is {spec[2]}; 100 is {spec[3]}"
        for n, spec in steering.DIALS.items() if adult or not spec[4])
    return (
        "If the person you are talking with asks you to change how you "
        "come across in ANY of these ways — funnier, warmer, blunter, "
        "quicker, wordier, more upbeat, more formal, more independent, "
        "anything a dial below covers — you can turn your own dials. "
        "Put each move on its own line, exactly like this:\n"
        "[[dial: humor +25]]\n"
        "[[dial: agreeableness -25]]\n"
        "\"More\" of an end is a step toward it; \"less\" steps away; "
        "\"as much as you can\" is max; \"drop it entirely\" is none. "
        "Those are the only four moves — one step is always 25, dials "
        "run 0-100, and max and none are the ends. Asked to change "
        "everything at once, use all as the name: [[dial: all none]]. "
        "Your dials, each with what its two ends mean:\n"
        f"{dials}\n"
        "The bracket line is taken out of what they read, so say in "
        "ordinary words what you changed. If they later ask for the "
        "opposite, step it back. Only ever do this when asked — never "
        "re-tune yourself unprompted."
    )
