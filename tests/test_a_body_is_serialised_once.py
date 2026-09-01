"""`req` stringifies the body. A caller that stringifies first sends the
JSON of a string, and the server refuses it.

    asked     video is selected but seadance is not rendering video
    mattered  the road could not be SET, and the screen made that look
              like a display bug

`api.ts`'s `req` does `body: opts.body ? JSON.stringify(opts.body) : undefined`.
Three callers handed it `JSON.stringify({...})` already, so what went on
the wire was a JSON string; FastAPI parsed it to a `str`, found no
fields, and answered 422 every time:

    {"detail":[{"type":"model_attributes_type","loc":["body"],
      "msg":"Input should be a valid dictionary or object..."}]}

All three were the video road — setting the road, amending the scene
direction, and starting a render — so the whole feature was unreachable
from the console. The screen hid it well: `chooseRoad` sets the road
optimistically, the POST fails, and the catch re-reads the server and
puts the road back. Pressing "Video generation" lit up and snapped to
"Profile photo", which was reported three times as the options showing
"for a split second" and going away, and chased twice as a layout fault.

Caught by driving the screen and watching the network. The call sites
look completely ordinary, which is why this is a guard and not a comment.
"""

from __future__ import annotations

import pathlib
import re

API = pathlib.Path(__file__).resolve().parent.parent / "app" / "src" / "api.ts"


def test_no_req_caller_stringifies_its_own_body():
    lines = API.read_text().splitlines()
    offenders = []
    for i, line in enumerate(lines):
        if "body: JSON.stringify" not in line:
            continue
        # A raw `fetch` sets its own headers and serialises for itself,
        # which is correct. `req` does not want a string.
        window = "\n".join(lines[max(0, i - 18):i + 3])
        if "fetch(" in window:
            continue
        offenders.append(f"api.ts:{i + 1}: {line.strip()}")
    assert not offenders, (
        "these hand `req` an already-serialised body, so the server "
        "receives the JSON of a string and answers 422:\n    "
        + "\n    ".join(offenders))


def test_req_still_serialises_for_its_callers():
    """The other half. If `req` ever stops stringifying, the guard above
    would be enforcing exactly the wrong thing — so the rule it depends on
    is pinned here rather than assumed."""
    text = API.read_text()
    assert "JSON.stringify(opts.body)" in text, (
        "`req` no longer serialises its body, so callers passing objects "
        "are now the broken ones — this guard's premise is gone")


def test_the_three_video_doors_pass_objects():
    """Named, because these are the three that were broken and the three
    a person notices: the road cannot be chosen, the direction cannot be
    amended, and no render can start."""
    text = API.read_text()
    for name, field in (("videoSetRoad", "road,"),
                        ("videoDirect", "asked, surface"),
                        ("videoRender", "prompt, shape, wait")):
        at = text.find(name)
        assert at != -1, f"{name} is gone"
        chunk = text[at:at + 700]
        assert field in chunk, f"{name} no longer sends {field}"
        assert "JSON.stringify" not in chunk.split("}),")[0], (
            f"{name} stringifies its body again — the 422 is back")
