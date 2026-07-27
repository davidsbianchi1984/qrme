"""The agent status light: green, amber, red.

A person watching an agent work needs one question answered at a glance, and it
is not *"what phase is it in"* — it is **"does this need me right now?"**

    green   working          it is running; nothing is wanted from you
    amber   needs assistance it has stopped and is waiting on a person
    red     stopped          it will not continue on its own

The light is **derived, never stored**. There is no `light` column anywhere,
and nothing sets one. It is computed from the status the workflow already
keeps, because a second field naming the same fact is a second field that can
disagree with the first — and the one a screen reads would be the one nobody
updates.

`completed` is the case worth explaining. A finished workflow is not working,
so "green means working" argues for something else; but the light answers
*does this need me*, and a finished one does not. It shows green with the word
**done**, which is why every reading carries a word as well as a colour. A
colour alone cannot tell a person whether the agent is mid-task or finished,
and on a watch face the word is doing most of the work anyway.

Deliberately **not** a fourth colour. Three is what a person can read without
learning a key, and every scheme that grew a fourth grew a fifth.
"""

from __future__ import annotations

# status -> (light, word, what the person should understand)
#
# Keyed on the vocabulary `qrme/workflows.py` already writes: running,
# awaiting_input, completed, failed, cancelled. Adding a status there without
# adding it here raises rather than defaulting — a silent default would render
# an unknown state as a confident green, which is the one failure this module
# must not have.
LIGHTS: dict[str, tuple[str, str, str]] = {
    "running": ("green", "working", "in progress — nothing needed from you"),
    "awaiting_input": ("amber", "needs you",
                       "stopped and waiting for a person to answer"),
    "completed": ("green", "done", "finished — nothing needed from you"),
    "failed": ("red", "stopped", "it hit an error and will not continue"),
    "cancelled": ("red", "stopped", "somebody stopped it"),
}

# The three colours, in the order a person reads them. Published so a client
# renders the same palette the screens do rather than picking its own greens.
ORDER = ("green", "amber", "red")


class UnknownStatus(KeyError):
    """A status with no light. Raised rather than defaulted — see LIGHTS."""


def light(status: str) -> dict:
    """The light for a workflow status.

    >>> light("awaiting_input")["light"]
    'amber'
    """
    try:
        colour, word, meaning = LIGHTS[status]
    except KeyError:
        raise UnknownStatus(
            f"no agent light for status {status!r} — add it to "
            f"qrme/agentlight.py:LIGHTS rather than letting it default") from None
    return {"light": colour, "label": word, "meaning": meaning,
            "status": status, "needs_you": colour == "amber"}


def legend() -> list[dict]:
    """What the three colours mean, for a screen that shows a key.

    Built from LIGHTS rather than written out again, so a legend cannot
    describe a mapping the code does not have.
    """
    out = []
    for colour in ORDER:
        words = sorted({w for c, w, _ in LIGHTS.values() if c == colour})
        statuses = sorted(s for s, (c, _, _) in LIGHTS.items() if c == colour)
        out.append({"light": colour, "labels": words, "statuses": statuses})
    return out
