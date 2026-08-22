"""A button that did nothing and a button that did something look identical
when neither says so.

Field report: *"I just tried to bring in another synthetic profile in my
friends list by using the add friend button and it's not working."*

The server was never the problem. Driven end to end — two profiles, the name
search, the browse pool, ``POST /profiles/{id}/friends``, the list read back
— the row lands and reads back, and a second press correctly answers 200
with ``added: false, reason: "already a friend"``.

Every fault was in the console, and all three are the same one:

* ``Profile.tsx`` guarded with a bare ``return``. No request, no error, no
  note. Pressed without a profile of your own — a visitor, or anybody signed
  in as a person rather than as one of their profiles — it did nothing and
  said nothing. ``Discover.tsx``'s identical guard has always named the
  reason, which is how you can tell this was an oversight rather than a
  decision.
* ``Friends.tsx`` asserted the owner token with ``!`` instead of checking it,
  so a session holding a profile id without a token sent an unauthenticated
  request — and rendered the refusal at the very bottom of a screen carrying
  the search results, the whole browse pool, the list and the suggestions.
  An answer below the fold is an answer nobody reads.
* ``addFriend`` was typed ``req<unknown>`` and all three call sites dropped
  the reply, so the one verdict the server takes care to distinguish arrived
  as silence.

    asked     did the friendship get added
    mattered  does anyone find out either way

The third is the one with previous form. ``FriendRemoval`` exists, and its
own comment says it: *a screen reporting success from the status code alone
tells somebody it removed a friendship that never existed.* That lesson was
written down for the remove and never carried across to the add.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SRC = REPO / "app" / "src"
API = SRC / "api.ts"

#: Every screen that offers to add a friend, and the function that does it.
ADDERS = {
    "Profile.tsx": "befriend",
    "Discover.tsx": "befriend",
    "Friends.tsx": "add",
}


def _stripped(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def _body(path: Path, fn: str) -> str:
    code = _stripped(path)
    m = re.search(r"async function %s\(.*?\n  \}" % re.escape(fn), code, re.S)
    assert m, f"{path.name} has no `{fn}` any more — read the shape again"
    return m.group(0)


def test_the_wire_says_what_befriending_answers() -> None:
    """`req<unknown>` is a promise not to look.

    The mirror of `FriendRemoval`, which has existed all along with a comment
    explaining exactly why the flag matters.
    """
    code = _stripped(API)
    assert "FriendAddition" in code, (
        "addFriend has no answer type, so no screen can read the verdict")
    call = re.search(r"addFriend:.*?\}\),", code, re.S)
    assert call, "addFriend moved — this guard reads it by name"
    assert "req<FriendAddition>" in call.group(0), (
        "addFriend still throws its answer away")


@pytest.mark.parametrize("screen", sorted(ADDERS))
def test_the_verdict_is_read_rather_than_assumed(screen: str) -> None:
    """A 200 is not a yes. Adding somebody already on the list succeeds and
    changes nothing, and a screen that reports that as "Added" is telling a
    person something it was told was untrue."""
    body = _body(SRC / "screens" / screen, ADDERS[screen])
    # The answer has to be bound to a name and that name's `added` read. An
    # earlier version of this guard searched the body for `.added` and passed
    # against a screen that had dropped the verdict entirely — because the
    # l10n key it printed regardless was called `dsc.added`. A guard that
    # matches the string it is meant to catch you printing is not a guard.
    held = re.search(r"(?:const|let)\s+(\w+)\s*=\s*await api\.addFriend\(",
                     body)
    assert held, (
        f"{screen} does not keep what addFriend answered, so it cannot read "
        "the verdict — the press reports the same thing either way")
    assert re.search(r"\b%s\.added\b" % re.escape(held.group(1)), body), (
        f"{screen} holds the answer as `{held.group(1)}` and never reads "
        "`.added` from it — adding somebody already on the list changes "
        "nothing and would still be reported as a fresh friendship")


@pytest.mark.parametrize("screen", sorted(ADDERS))
def test_no_press_returns_in_silence(screen: str) -> None:
    """The guard that fires before the request.

    Whatever a screen does about a missing profile or owner token, it may not
    do it quietly: a bare `return` is the press disappearing.
    """
    body = _body(SRC / "screens" / screen, ADDERS[screen])
    for guard in re.finditer(
            r"if \([^)]*(?:profileId|ownerToken)[^)]*\)\s*(\{[^}]*\}|[^\n]*)",
            body):
        said = guard.group(1)
        assert re.search(r"setNote|setError", said), (
            f"{screen} turns the press away without a word: `{said.strip()}` "
            "— nothing is sent and nothing is shown, which is exactly what "
            "the field report described")


@pytest.mark.parametrize("screen", sorted(ADDERS))
def test_the_token_is_checked_rather_than_asserted(screen: str) -> None:
    """`ownerToken!` is the type system being told to look away.

    It does not produce a token; it produces an unauthenticated request and a
    refusal from the far end, for a condition the screen could have named.
    """
    body = _body(SRC / "screens" / screen, ADDERS[screen])
    assert "ownerToken!" not in body and "profileId!" not in body, (
        f"{screen} asserts the session instead of checking it, so a session "
        "without an owner token sends the request anyway")


def test_the_friends_screen_answers_where_the_press_was() -> None:
    """Above the fold, or it may as well be nowhere.

    The note and the refusal sat last in the file — under the search results,
    the browse pool, the list and the suggestions. On the pool card, which is
    the surface a person actually adds from, that is hundreds of pixels below
    the button they pressed.
    """
    code = _stripped(SRC / "screens" / "Friends.tsx")
    verdict = code.index("<Refusal")
    # The cards the verdict has to come before. `frn.pool` is the browse pool
    # and `frn.suggested` is the tail of the screen.
    for card, why in (("frn.pool", "the browse pool"),
                      ("frn.suggested", "the suggestions")):
        assert verdict < code.index(card), (
            f"the verdict renders after {why}, so an Add pressed above it "
            "answers off-screen and the button reads as dead")
