#!/usr/bin/env python3
"""Generate the QRME *watch* faces — what a paired wearable is allowed to show.

The case, crown and frame are lifted from JIM's watch builder deliberately: two
products drawing the same hardware differently would be a bug wearing the
clothes of a style choice. The palette comes from QRME's own phone generator,
so the faces belong to this product while the watch belongs to the wrist.

There is one face per entry in ``qrme/wearables.FACES``, and a test holds them
in step — a face somebody can enable and never see would be a permission
granting nothing.

Run: python3 docs/watch/build.py  ->  docs/watch/NN-name.svg
"""

from __future__ import annotations

import importlib.util
import os
import random

OUT = os.path.dirname(os.path.abspath(__file__))

# reuse the phone builder's primitives (icons, palette, text/rrect helpers)
_spec = importlib.util.spec_from_file_location(
    "phonebuild", os.path.join(OUT, "..", "screens", "build.py"))
pb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pb)
icon, C, ACCENT, esc, rrect, text = pb.icon, pb.C, pb.ACCENT, pb.esc, pb.rrect, pb.text
A = pb.A

W, H = 236, 300
# Case and screen are the same rectangle: the display runs edge to edge, the
# way a modern watch does. A separate inset screen leaves a bezel band that
# reads as a frame drawn around a picture rather than as glass filling a case.
CAX, CAY, CAW, CAH = 18, 20, 196, 260
SXX, SYY, SWW, SHH = CAX, CAY, CAW, CAH
PADX = 38          # content left inside screen
CW = SWW - 2 * (PADX - SXX)   # content width


def orb(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#orb)"/>'
            f'<ellipse cx="{cx-r*0.28}" cy="{cy-r*0.32}" rx="{r*0.28}" ry="{r*0.18}" fill="rgba(255,255,255,0.33)"/>')


def head(num, title, accent="brand"):
    ac = ACCENT.get(accent, C["brandA"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)} watch screen">']
    o.append(f'''<defs>
      <linearGradient id="gScr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C['scrA']}"/><stop offset="1" stop-color="{C['scrB']}"/></linearGradient>
      <!-- The case gets its own gradient rather than the phone's. QRME's
           frameA (#2a2352) is *lighter* than the screen, which on a phone
           reads as the metal band catching the light and on a watch reads as
           a purple glow behind the whole device. A case is darker than the
           display it surrounds. -->
      <linearGradient id="gFrame" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#141029"/><stop offset="1" stop-color="#07050f"/></linearGradient>
      <linearGradient id="gCard" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C['card']}"/><stop offset="1" stop-color="{C['card2']}"/></linearGradient>
      <linearGradient id="gBrand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="mV" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="mO" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f7b731"/><stop offset="1" stop-color="#ff7a45"/></linearGradient>
      <linearGradient id="mG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2fd27a"/><stop offset="1" stop-color="#43e08a"/></linearGradient>
      <radialGradient id="orb" cx="34%" cy="30%" r="75%"><stop offset="0" stop-color="#c3b0ff"/><stop offset="42%" stop-color="{C['brandA']}"/><stop offset="80%" stop-color="#2f6cf0"/><stop offset="100%" stop-color="#14204a"/></radialGradient>
    </defs>''')
    # crown + side button on the right
    o.append(rrect(CAX + CAW - 2, 118, 7, 34, 3, "#333c52"))
    o.append(rrect(CAX + CAW - 1, 160, 5, 26, 2, "#2a3145"))
    # The screen is the whole face. The case survives only as the hairline
    # around it — enough to say where the glass ends, not enough to be a bezel.
    o.append(rrect(SXX, SYY, SWW, SHH, 60, "url(#gScr)",
                   "rgba(255,255,255,0.13)", 1.2))
    o.append(text(SXX + SWW - 26, SYY + 30, "10:09", 11, ac, 700, "end"))
    o.append(text(PADX, SYY + 30, title, 13, C["txt"], 700, spacing=-0.2))
    return o


def dots(active, count):
    o = []
    cx0 = W / 2 - (count - 1) * 5
    for i in range(count):
        c = C["txt"] if i == active else C["t3"]
        o.append(f'<circle cx="{cx0+i*10}" cy="{SYY+SHH-14}" r="{2.6 if i==active else 2}" fill="{c}"/>')
    return o


def close():
    return ["</svg>"]


def tile(x, y, w, h, ic, col, val, lbl):
    c = ACCENT[col]
    return (rrect(x, y, w, h, 13, "url(#gCard)", C["line"], 1)
            + rrect(x + 9, y + 9, 22, 22, 7, A(c, 0.16))
            + icon(ic, x + 20, y + 20, c, 0.62)
            + text(x + 9, y + h - 20, val, 15, C["txt"], 750)
            + text(x + 9, y + h - 7, lbl, 8.5, C["t2"], 500))


def row(x, y, w, ic, col, k, s):
    c = ACCENT[col]
    return (rrect(x, y, w, 40, 12, "url(#gCard)", C["line"], 1)
            + rrect(x + 8, y + 9, 22, 22, 7, A(c, 0.16)) + icon(ic, x + 19, y + 20, c, 0.6)
            + text(x + 38, y + 17, k, 11, C["txt"], 650)
            + text(x + 38, y + 30, s, 9, C["t2"]))


def agent_light(x, y, colour, label):
    """The agent status light on a watch — green working, amber needs you,
    red stopped.

    A wrist is the surface this matters most on: it is glanced at, not read.
    The dot carries the answer and the word confirms it, because a colour
    alone cannot separate "still going" from "finished" — and a watch is
    exactly where somebody would guess wrong and walk away.
    """
    col = {"green": C["green"], "amber": C["amber"], "red": C["red"]}[colour]
    return (f'<circle cx="{x}" cy="{y}" r="9" fill="{A(col, 0.18)}"/>'
            + f'<circle cx="{x}" cy="{y}" r="4.2" fill="{col}"/>'
            + text(x + 14, y + 4, label, 10, col, 700))


def light_board(cx, y, counts):
    """The ambient agent board: three lights, three counts, no names.

    This face exists for the moment the phone is busy and the wrist is the
    only surface free. Naming the agents here was the first cut and was wrong
    — a name is something you *read*, and reading is the thing a glance cannot
    do. What a person needs off the wrist is whether anything has gone amber
    or red; which agent it was is a question for the app, where there is room
    to answer it.

    It is also the reason this face carries no tap targets. A wrist showing
    three numbers can be understood without being touched, and a control that
    invites a tap invites looking away from whatever the phone was for.
    """
    out = []
    rows = (("green", "running", counts[0]),
            ("amber", "need help", counts[1]),
            ("red", "stopped", counts[2]))
    yy = y
    for colour, label, n in rows:
        col = {"green": C["green"], "amber": C["amber"], "red": C["red"]}[colour]
        dim = n == 0
        a = 0.22 if not dim else 0.07
        out.append(f'<circle cx="{cx-52}" cy="{yy}" r="17" fill="{A(col, a)}"/>')
        op = ' opacity="0.28"' if dim else ""
        out.append(f'<circle cx="{cx-52}" cy="{yy}" r="8.5" fill="{col}"{op}/>')
        out.append(text(cx - 22, yy + 9, str(n), 26, col if not dim else C["t3"],
                        800))
        out.append(text(cx + 6, yy + 8, label, 11,
                        C["t2"] if not dim else C["t3"], 600))
        yy += 48
    return out



def big_counts(rows):
    """Three numbers and nothing else. The ambient shape, borrowed from the
    agent light board for the same reason it worked there: a wrist is glanced
    at, and a glance reads a number but not a sentence."""
    o, y = [], SYY + 56
    for col, label, n in rows:
        c = ACCENT[col]
        dim = n == 0
        op = ' opacity="0.3"' if dim else ""
        o.append(f'<circle cx="{PADX + 14}" cy="{y}" r="13" fill="{A(c, 0.18)}"{op}/>')
        o.append(f'<circle cx="{PADX + 14}" cy="{y}" r="6" fill="{c}"{op}/>')
        o.append(text(PADX + 36, y + 8, str(n), 22,
                      c if not dim else C["t3"], 800))
        # Offset by the number's own width: "12" is wider than "3", and a
        # fixed label position crowds the two-digit case.
        o.append(text(PADX + 46 + len(str(n)) * 14, y + 7, label, 10.5,
                      C["t2"] if not dim else C["t3"], 600))
        y += 46
    return o


FACES = [
    # agents — the light board, matching JIM's face 36 so one wrist shows the
    # same shape whichever product paired it.
    dict(num=1, title="Agents", accent="green", kind="counts", rows=[
        ("green", "running", 3), ("amber", "need help", 1),
        ("red", "stopped", 1)], foot="open on your phone"),
    # activity — the community layer, as counts. Not the content: a feed on a
    # wrist is a reading surface, and reading is the thing a glance cannot do.
    dict(num=2, title="Activity", accent="cyan", kind="counts", rows=[
        ("cyan", "new posts", 12), ("brand", "friend picks", 3),
        ("amber", "replies", 2)], foot="tap to open the feed"),
    dict(num=3, title="Profile", accent="brand", kind="tiles", tiles=[
        ("chat", "brand", "247", "memories"),
        ("people", "cyan", "12", "relationships"),
        ("chart", "green", "92%", "engagement"),
        ("star", "gold", "4.0", "rating")]),
    dict(num=4, title="Control", accent="amber", kind="rows", rows=[
        ("check", "green", "Approve reply", "held for you"),
        ("play", "amber", "Assist agent", "one is waiting"),
        ("stop", "red", "Halt", "stops the run")], foot="the wrist adds reach, not powers"),
    # microphone — channel 2, on the device that is doing the listening.
    #
    # The other four faces report; this one is the only place the wrist can
    # end something, and that is deliberate rather than an exception to "the
    # wrist adds reach, not powers". A lent microphone is this watch. Making
    # somebody find a phone to stop their own device listening would be the
    # one permission on the platform you cannot revoke from the thing it runs
    # on, and "yours to end, alone and at any moment" would be false.
    dict(num=5, title="Microphone", accent="cyan", kind="rows", rows=[
        ("mic", "cyan", "Lent to a room", "the quarterly numbers"),
        ("shield", "green", "Near-field only", "you, not the room"),
        ("stop", "red", "Take it back", "ends it here")],
        foot="everyone in the room can see it is lent"),
]


def render(spec):
    o = head(f"{spec['num']:02d}", spec["title"], spec.get("accent", "brand"))
    if spec["kind"] == "counts":
        o += big_counts(spec["rows"])
    elif spec["kind"] == "tiles":
        tw = (CW - 10) / 2
        for i, (ic, col, val, lbl) in enumerate(spec["tiles"]):
            x = PADX + (i % 2) * (tw + 10)
            y = SYY + 44 + (i // 2) * 66
            o.append(tile(x, y, tw, 58, ic, col, val, lbl))
    else:
        y = SYY + 46
        for ic, col, k, s in spec["rows"]:
            o.append(row(PADX, y, CW, ic, col, k, s))
            y += 48
    if spec.get("foot"):
        o.append(text(W / 2, SYY + SHH - 28, spec["foot"], 8.5, C["t3"], 500,
                      "middle"))
    o += dots(spec["num"] - 1, len(FACES))
    o += close()
    return "".join(o)


def main():
    import re
    for spec in FACES:
        slug = re.sub(r"[^a-z0-9]+", "-", spec["title"].lower()).strip("-")
        path = os.path.join(OUT, f"{spec['num']:02d}-{slug}.svg")
        # Rendered first — see the note in docs/screens/build.py. Opening for
        # write truncates before the render runs, so a failure here would leave
        # an empty face behind rather than the previous good one.
        svg = render(spec)
        with open(path, "w") as fh:
            fh.write(svg)
    print(f"generated {len(FACES)} watch faces")


if __name__ == "__main__":
    main()
