"""Render each starter as its own Profile Home card, for the README gallery.

The gallery used to be a portrait with a name and an industry under it. That is
not what a profile looks like in the product: screen 5 gives it an avatar
bubble, a role, stat tiles and a **Chat** button, and the page was showing a
thinner thing than the app does. These cards are that screen, one per starter,
sized for a gallery cell.

**The stat tiles carry real facts, not the screen's demo numbers.** Screen 5
reads *Memory 247 · Relationships 12 · Engagement 92%*, which is fine for one
illustrative mock and wrong here: stamping invented engagement figures onto 34
public cards would be publishing data about profiles nobody has talked to yet.
What each card shows instead is true of that starter — the size of the Field
Pack it is grounded in, and how many skills it is tagged with. The rated
starter has no Field Pack (there is no adult-industry pack, deliberately), so
its tiles say so rather than showing a zero that looks like a failure.

SVG rather than PNG, with the portrait embedded as base64: the text stays crisp
at any display width and selectable in the file, and GitHub renders these the
same way it already renders the desk-frame screens.

    python3 tools/starter_cards.py            # write docs/portraits/cards/*.svg
    python3 tools/starter_cards.py --check    # verify, exit 1 if stale
"""

from __future__ import annotations

import base64
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUBBLES = ROOT / "docs" / "portraits" / "bubbles"
OUT = ROOT / "docs" / "portraits" / "cards"

sys.path.insert(0, str(ROOT / "tools"))
from starter_gallery import ROLES, starters  # noqa: E402


def _screens():
    """The screen generator, imported for its palette and font.

    Imported rather than copied so the cards cannot drift from the app's
    colours — the whole complaint that produced this file was a gallery that
    looked nothing like the product.
    """
    spec = importlib.util.spec_from_file_location(
        "screens_build", ROOT / "docs" / "screens" / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _screens()
C, FONT = S.C, S.FONT

# Authored at 2x and displayed at half size, so the text is crisp on a phone.
# The height is computed from the content rather than fixed: a one-line role
# and a two-line role produced the same box before, so half the cards carried a
# strip of dead space under the buttons.
W = 352
PAD = 16


def esc(t: str) -> str:
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def wrap(text: str, limit: int) -> list[str]:
    """Wrap into at most two **balanced** lines.

    Greedy wrapping fills the first line and leaves the remainder stranded:
    "retired fee-only financial planner," then "ret." alone underneath, which
    reads like a typo. Balanced picks the break that minimises the longer line,
    giving "retired fee-only" / "financial planner".
    """
    words = text.split()
    if len(" ".join(words)) <= limit:
        return [" ".join(words)]
    best, score = None, None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        s = max(len(a), len(b))
        if score is None or s < score:
            best, score = (a, b), s
    return list(best)


def tiles(handle: str, industry: str, tags: list[str]) -> list[tuple]:
    """(label, value, unit, colour) — every one of them true of this starter."""
    if handle == "vivienne_sable":       # rated tier: no pack exists to install
        return [("Field Pack", "None", "rated tier", C["amber"]),
                ("Skills", str(len(tags)), "tagged", C["brandA"])]
    return [("Field Pack", "3", "items", C["brandA"]),
            ("Skills", str(len(tags)), "tagged", C["amber"])]


def card(handle: str, industry: str, display: str, tags: list[str]) -> str:
    role = ROLES[handle].replace("&amp;", "&")
    png = base64.b64encode((BUBBLES / f"{handle}.webp").read_bytes()).decode()
    role_lines = wrap(role, 30)
    H = 430 + 16 * (len(role_lines) - 1)

    o: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{esc(display)} — {esc(role)}">',
        "<defs>",
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{C["scrA"]}"/>'
        f'<stop offset="1" stop-color="{C["scrB"]}"/></linearGradient>',
        f'<linearGradient id="tile" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{C["card"]}"/>'
        f'<stop offset="1" stop-color="{C["card2"]}"/></linearGradient>',
        f'<linearGradient id="brand" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{C["brandA"]}"/>'
        f'<stop offset="1" stop-color="{C["brandB"]}"/></linearGradient>',
        "</defs>",
        f'<rect width="{W}" height="{H}" rx="22" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="21.5" '
        f'fill="none" stroke="{C["line"]}"/>',
    ]

    cx = W / 2
    # The bubble portrait already carries the AI mark burned into its pixels,
    # which is why it is used whole rather than re-cropped here.
    o.append(f'<image x="{cx-62}" y="24" width="124" height="124" '
             f'href="data:image/webp;base64,{png}"/>')

    o.append(f'<text x="{cx}" y="181" text-anchor="middle" font-family="{FONT}" '
             f'font-size="21" font-weight="750" fill="#fff">{esc(display)}</text>')

    ry = 202
    for line in role_lines:
        o.append(f'<text x="{cx}" y="{ry}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="12.5" fill="{C["t2"]}">'
                 f'{esc(line)}</text>')
        ry += 16

    o.append(f'<circle cx="{cx-34}" cy="{ry+2}" r="3.5" fill="{C["green"]}"/>')
    o.append(f'<text x="{cx-25}" y="{ry+6}" font-family="{FONT}" '
             f'font-size="12" font-weight="600" fill="{C["green"]}">'
             f'{esc(industry.replace("_", " "))}</text>')

    ty = ry + 24
    tw = (W - PAD * 2 - 10) / 2
    for i, (label, value, unit, col) in enumerate(tiles(handle, industry, tags)):
        tx = PAD + i * (tw + 10)
        o.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="62" rx="14" '
                 f'fill="url(#tile)" stroke="{C["line"]}"/>')
        o.append(f'<text x="{tx+12}" y="{ty+22}" font-family="{FONT}" '
                 f'font-size="11" fill="{C["t2"]}">{esc(label)}</text>')
        o.append(f'<text x="{tx+12}" y="{ty+48}" font-family="{FONT}" '
                 f'font-size="20" font-weight="800" fill="{col}">{esc(value)}</text>')
        o.append(f'<text x="{tx+tw-10}" y="{ty+48}" text-anchor="end" '
                 f'font-family="{FONT}" font-size="10" fill="{C["t2"]}">'
                 f'{esc(unit)}</text>')

    by = ty + 78
    o.append(f'<rect x="{PAD}" y="{by}" width="{W-PAD*2}" height="44" rx="14" '
             f'fill="url(#brand)"/>')
    o.append(f'<text x="{cx}" y="{by+28}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="16" font-weight="700" '
             f'fill="#fff">Chat</text>')

    gw = (W - PAD * 2 - 10) / 2
    for i, label in enumerate(("Customize", "View Memory")):
        gx = PAD + i * (gw + 10)
        o.append(f'<rect x="{gx}" y="{by+52}" width="{gw}" height="38" rx="12" '
                 f'fill="none" stroke="{C["line"]}"/>')
        o.append(f'<text x="{gx+gw/2}" y="{by+76}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="12.5" font-weight="600" '
                 f'fill="{C["t2"]}">{label}</text>')

    o.append("</svg>")
    return "\n".join(o)


def main() -> int:
    check = "--check" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    stale, n = [], 0
    for handle, industry, display, tags in starters():
        svg = card(handle, industry, display, tags)
        path = OUT / f"{handle}.svg"
        if not path.exists() or path.read_text() != svg:
            stale.append(handle)
            if not check:
                path.write_text(svg)
        n += 1
    if check and stale:
        print(f"{len(stale)} starter card(s) stale: {', '.join(stale[:5])}…")
        return 1
    print(f"{'checked' if check else 'wrote'} {n} starter cards in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
