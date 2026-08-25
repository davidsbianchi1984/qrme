"""The header that protects a stranger, and the player it silently broke.

## What happened

`pagehead.HEADERS` sends `referrer-policy: no-referrer` on every HTML
response. That is right, and the reason is written where it is set: a page
reached from a QR sticker must not tell the next host which sticker somebody
knelt over — the referrer *is* the beacon.

It applies to the console too, and the console embeds other platforms'
players. A player handed no referrer cannot check whether it is allowed to
embed on the site it finds itself in, so it does not play. YouTube renders
its own grey panel reading **Error 153, video player configuration error**,
which names nothing a reader could act on and appears identical to a broken
link.

    asked     does the page carry the header
    mattered  does the thing inside the page still work

Nothing in this suite could see it. The header is correct, the embed markup
was correct, and the two were only wrong together — in a browser, which no
test here is.

## The fix, and its shape

`referrerPolicy` on the iframe element overrides the document's policy for
that one subresource. So the beacon pages keep `no-referrer` and the players
get `strict-origin-when-cross-origin`: the host and never the path. The
platform learns the origin of an embed it is already serving, which the
request itself told it, and learns it only when somebody presses play,
because until then there is no request at all.

## Why this reads the source

The failure is a browser behaviour and this is not a browser. What is
checkable here is the thing that was actually missing: an iframe pointed at
somebody else's player, on a document that sends no referrer, with nothing
on the element to say otherwise.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import ratchets

SRC = Path(__file__).resolve().parent.parent / "app" / "src"

#: The attributes that mark an iframe as somebody else's player rather than
#: our own markup: it is handed a URL from the API, and it is allowed the
#: capabilities a player asks for.
_PLAYER = re.compile(r"<iframe\b[^>]*?allow=\"[^\"]*encrypted-media[^\"]*\"[^>]*?>",
                     re.S)


def _players() -> list[tuple[str, str]]:
    found = []
    for path in sorted(SRC.rglob("*.tsx")):
        for tag in _PLAYER.findall(path.read_text(encoding="utf-8")):
            found.append((path.name, tag))
    return found


def test_every_embedded_player_is_handed_an_origin():
    """The guard.

    An embed with no `referrerPolicy` inherits the document's `no-referrer`
    and the player refuses to start. The failure is silent in every sense
    that matters: the request succeeds, the frame renders, and what a person
    reads is the other platform's error code.
    """
    mute = [f"{name}: {tag.split('src=')[1][:60]}"
            for name, tag in _players() if "referrerPolicy" not in tag]
    assert not mute, (
        "these players are embedded on a document that sends no referrer, "
        "with nothing on the element to override it — they will render and "
        "refuse to play:\n    " + "\n    ".join(mute)
        + '\n  Add referrerPolicy="strict-origin-when-cross-origin".')


def test_the_origin_is_all_a_player_is_given():
    """The other direction, and the reason the policy is not simply removed.

    `no-referrer-when-downgrade` or `unsafe-url` would also make the player
    work, and would hand the platform the whole path — which profile, which
    screen. The host is enough for it to check its own embedding, and the
    host is all it gets.
    """
    loose = [f"{name}: {tag[:80]}" for name, tag in _players()
             if "referrerPolicy" in tag
             and "strict-origin-when-cross-origin" not in tag]
    assert not loose, (
        "these players are given more than their embedding check needs:\n    "
        + "\n    ".join(loose)
        + "\n  The origin answers it; the path is nobody else's.")


def test_the_reader_can_still_find_a_player():
    """A guard on the guard. If the pattern stopped matching, both checks
    above would pass on a console with every embed broken."""
    assert len(_players()) >= ratchets.floor("console.players"), (
        f"found {len(_players())} embedded players, which cannot be right — "
        "the Feed and the Wall each carry one, so the reader has drifted "
        "off the markup and these checks are vacuous")
