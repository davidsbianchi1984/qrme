"""A badge placed a fixed distance down the tile needs the tile pinned.

## The defect

The room draws the AI mark and the VERIFIED mark twice: once burned into
the portrait's own pixels, and once again on the outermost layer, in the
same box and the same colours, so that the circle the face is drawn in
cannot slice a disclosure in half. That only reads as one mark if the
drawn one lands on the burned one exactly.

The drawn one is positioned from the tile: `top` is
`var(--face-top) + var(--face) * 0.035156`, where `--face-top` is meant
to be the distance from the tile's padding box down to the top of the
face. One number, for every seat.

It is only one number if every seat's face starts at the same height —
and it did not. The seats are grid items, a grid stretches every item in
a row to the tallest of them, and the tiles were centring their contents
inside that. So a seat whose field wrapped to two lines had less leftover
space above it than a seat whose did not, and its face rode up. Measured
on a phone, four seats in one room: two faces at 9px down the tile and
two at 16.1, against a mark drawn at a single fixed offset. Up to seven
pixels of daylight, which is a doubled badge in a 56px circle — reported
as "the glyphs are missing" and "the AI badge doubles".

    asked     does the drawn mark cover the burned one
    mattered  does the face start where the mark says it does

## What this checks

That no rule lays the room's seats out from their middle. Packed from
the top, a face begins at the tile's own padding on every seat, in every
row, lit or not — which is a number the marks can be written against,
and the number they are written against now.

It does not check the offsets themselves. Those are measured off a live
page rather than reasoned about, because the last three times they were
reasoned about they were wrong; this guards the property that makes a
measurement good for more than one seat.
"""

from __future__ import annotations

import pathlib
import re

CSS = pathlib.Path(__file__).resolve().parent.parent / "app" / "src" / "styles.css"

_COMMENTS = re.compile(r"/\*.*?\*/", re.S)

#: The seat itself, not something sitting inside it. The last compound in
#: the selector has to BE the tile — `... > .rs-tile > .rs-side` centres a
#: row of glyphs inside a seat, which is its own business and not this.
_SEAT = re.compile(r"\.room-scene\s*>?\s*[^,]*\.rs-(tile|empty)"
                   r"[\w.:()-]*\s*$")


def _targets_a_seat(selector: str) -> bool:
    return any(_SEAT.search(part.strip()) for part in selector.split(","))

#: What packing from the top is called, in the two spellings CSS allows.
_PINNED = {"flex-start", "start", "normal"}


def _rules(text: str) -> list[tuple[str, str]]:
    """(selector, body) for every rule in the sheet, at-rules unwrapped."""
    text = _COMMENTS.sub("", text)
    out, buf, stack = [], [], []
    for ch in text:
        if ch == "{":
            stack.append("".join(buf).strip())
            buf = []
        elif ch == "}":
            head = stack.pop() if stack else ""
            body = "".join(buf)
            buf = []
            if head and not head.startswith("@"):
                out.append((" ".join(head.split()), body))
        else:
            buf.append(ch)
    return out


def _declared(body: str, prop: str) -> list[str]:
    """Every value this body gives that property, in order."""
    found = []
    for piece in body.split(";"):
        if ":" not in piece:
            continue
        name, value = piece.split(":", 1)
        if name.strip().lower() == prop:
            found.append(value.replace("!important", "").strip().lower())
    return found


def test_the_rooms_seats_pack_from_the_top() -> None:
    loose = []
    for selector, body in _rules(CSS.read_text(encoding="utf-8")):
        if not _targets_a_seat(selector):
            continue
        for value in _declared(body, "justify-content"):
            if value not in _PINNED:
                loose.append(f"{selector} {{ justify-content: {value} }}")
    assert not loose, (
        "a seat that centres its contents moves its own face, and the "
        "marks are drawn a fixed distance down the tile:\n  "
        + "\n  ".join(loose))


def test_the_offset_is_declared_where_the_seats_are() -> None:
    """`--face-top` belongs on the seat, beside `--face`."""
    homes = [selector for selector, body in
             _rules(CSS.read_text(encoding="utf-8"))
             if _declared(body, "--face-top")]
    assert homes, "nothing declares --face-top any more"
    stray = [s for s in homes if not _targets_a_seat(s)]
    assert not stray, (
        "--face-top is the distance down a SEAT to its face, and these "
        "rules declare it somewhere else:\n  " + "\n  ".join(stray))
