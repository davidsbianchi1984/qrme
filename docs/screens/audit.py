#!/usr/bin/env python3
"""Measure every line of text on every generated screen against its bounds.

    python3 docs/screens/audit.py

The screens are hand-laid SVG. Nothing wraps, nothing ellipsises, and a string
that is too long simply runs off the side of the phone and stays there — where
it is invisible to anyone who is not looking at that one screen out of a
hundred and ten. That defect has now shipped four separate times: three cards
on the gaming screen, a title under its own status pill on fine-tune, two of
the four Genesis questions, and a privacy line on the live-video screen.

The builder already refuses over-long *card* text, but a card is one of a dozen
things that draw a string. This walks the finished files instead, so it does not
care which helper produced the text — every `<text>` element in every screen,
both platforms, plus the desktop views and the watch faces.

Widths come from ``textwidth.py``, which is a measured advance-width table
rather than a character count. The renderer it was measured against substitutes
DejaVu Sans, which is wider than the SF Pro / Segoe UI / Roboto a browser will
actually find — so this over-estimates slightly, which is the direction an
overflow check should err in.

Exits non-zero when anything is out of bounds, so it can gate a build.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textwidth as tw

SVG = "{http://www.w3.org/2000/svg}"

# A phone screen's usable width. The screen itself is SX..SX+SW = 20..300; a
# glyph reaching the very edge of the glass is already wrong, but the margin
# here is the *breakage* line rather than the design's, for the same reason
# `card_room` uses a smaller inset than the layout does.
PHONE = (20.0, 300.0)
WATCH = (18.0, 214.0)

def bounds(path: str, kind: str) -> tuple[float, float]:
    """Where the usable area of this particular file starts and ends.

    A full-screen frame runs to the edge of the file, so its bounds are the
    canvas. That is read out of the drawing rather than guessed from the
    filename — a name-matching rule silently classified every `*-audio-room`
    and `*-vr-room` screen as an ordinary phone and then reported their own
    correct layout as broken.
    """
    src = open(path).read()
    canvas = float(re.search(r'width="(\d+)"', src).group(1))
    if kind == "watch":
        return WATCH
    if kind == "desktop":
        return 0.0, canvas
    # render_full lays its screen rect on the origin at full canvas size;
    # every other screen insets a phone body first.
    if re.search(r'<rect x="0(\.0)?" y="0(\.0)?" width="%g(\.0)?"' % canvas, src):
        return 0.0, canvas
    return PHONE


def offenders(path: str, left: float, right: float) -> list[tuple[float, float, str]]:
    out = []
    for el in ET.parse(path).getroot().iter(f"{SVG}text"):
        s = "".join(el.itertext())
        if not s.strip():
            continue
        x = float(el.get("x", 0))
        size = float(el.get("font-size", 12))
        weight = int(el.get("font-weight", 400))
        anchor = el.get("text-anchor", "start")
        width = tw.width(s, size, weight)
        x0 = {"start": x, "middle": x - width / 2}.get(anchor, x - width)
        if x0 < left - 0.5 or x0 + width > right + 0.5:
            out.append((x0, x0 + width, s))
    return out


def main() -> int:
    groups = (("mobile", "docs/screens/*.svg"),
              ("mobile", "docs/screens/android/*.svg"),
              ("desktop", "docs/desktop/*.svg"),
              ("watch", "docs/watch/*.svg"))
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    bad = 0
    seen: set[str] = set()
    for kind, pattern in groups:
        for path in sorted(glob.glob(os.path.join(root, pattern))):
            left, right = bounds(path, kind)
            for x0, x1, s in offenders(path, left, right):
                bad += 1
                if s in seen:
                    continue
                seen.add(s)
                print(f"{os.path.relpath(path, root):48} "
                      f"[{x0:6.0f},{x1:6.0f}] vs [{left:.0f},{right:.0f}]  {s!r}")
    if bad:
        print(f"\n{bad} text runs outside its bounds "
              f"({len(seen)} distinct strings)")
        return 1
    print("every line of text is inside its screen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
