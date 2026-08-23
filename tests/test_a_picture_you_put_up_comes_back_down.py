"""Whatever you put up in a room, you can take back down.

    asked     is the picture on screen
    mattered  can the person who put it there get it off the server

`DELETE /rooms/{room_id}/face` is the only route that removes an uploaded
room picture or background — `PUT .../face` changes what is DISPLAYED and
leaves the file exactly where it is. So the delete route is the erasure
door, and a room face is a photograph of a person: it is the kind of thing
somebody changes their mind about.

That door was lost once, quietly. A chip labelled "Just my name" was taken
out on request — it was a display toggle nobody wanted in a crowded strip —
and it happened to be the only caller of the delete binding. The display
behaviour it offered survived in the camera control, so nothing looked
broken; what left with it was the way to take a background down. The
binding guard caught the orphan and this test is the reason it stays
caught, because a guard that only counts callers is happy the moment any
caller exists, including a wrong one.

Two claims, both about the client, because the route itself was never in
question:

* something is offered when something is up, and
* what it calls is the route that deletes rather than the one that hides.
"""

from __future__ import annotations

import re
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1]
       / "app" / "src" / "screens" / "Inside.tsx").read_text(encoding="utf-8")
API = (Path(__file__).resolve().parents[1]
       / "app" / "src" / "api.ts").read_text(encoding="utf-8")


def _binding(name: str) -> str:
    """The body of one `api.<name>` binding, as written."""
    start = API.index(f"\n  {name}: (")
    rest = API[start + 1:]
    nxt = re.search(r"\n  [A-Za-z_]\w*: ", rest)
    return rest[:nxt.start()] if nxt else rest


def test_the_take_down_control_reaches_the_deleting_route():
    """Not "a control exists" — that a control reaches the route that
    removes the file. Hiding a picture and deleting it are one keystroke
    apart in this API and a world apart for the person in the photograph."""
    assert "api.clearRoomFace(" in SRC, (
        "nothing in the room calls the route that takes a picture down"
    )
    body = _binding("clearRoomFace")
    assert '"DELETE"' in body, (
        "the take-down control is wired to a binding that does not delete"
    )
    assert "/face" in body


def test_it_is_offered_only_when_there_is_something_to_take_down():
    """A chip that is always there, on a strip that was cropping, is the
    clutter the removal was about. It earns its place by appearing when
    there is a file to remove and staying out of the way otherwise."""
    call = SRC.index("api.clearRoomFace(")
    guard = SRC[max(0, call - 700):call]
    assert "media_url" in guard and "background_url" in guard, (
        "the take-down control is not conditioned on there being an "
        "uploaded picture or background — either it shows when there is "
        "nothing to take down, or it hides when there is"
    )


def test_taking_it_down_reloads_the_room():
    """The file is gone server-side either way; a seat still showing the
    picture is a control that looks like it failed."""
    after = SRC[SRC.index("api.clearRoomFace("):][:300]
    assert "load()" in after, (
        "the room is not re-read after the picture is deleted"
    )
