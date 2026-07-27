"""Render each starter as its own Profile Home card, for the README gallery.

The gallery used to be a portrait with a name and an industry under it. That is
not what a profile looks like in the product: screen 5 gives it an avatar
bubble, a role, stat tiles and a **Chat** button, and the page was showing a
thinner thing than the app does. These cards are that screen, one per starter,
sized for a gallery cell.

The card follows **screen 80**, the profile front page a visitor lands on: the
bubble, the name, the role, the rating other people gave it, the skill chips,
and the call to action — plus screen 5's Memory, Relationships and Engagement
tiles beneath them.

**The figures are the product's own sample values, and they are identical on
every card.** A freshly seeded starter has nothing: no reviews, no
relationships, no messages, no engagement, because nobody has talked to it yet.
Reporting those zeros would render 34 dead cards; inventing a different number
per profile would be fabricating activity. The compromise is the app's existing
mock figures, repeated unchanged — thirty-four cards all reading *4.0 · 37
reviews* is self-evidently a template rather than a measurement, and the README
says so in a line under the gallery.

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
from starter_gallery import CAREERS, REVIEWS, ROLES, starters  # noqa: E402


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


# The app's own sample figures (screens 5 and 80), used verbatim and identically
# on every card. See the module docstring for why these are not per-profile.
SAMPLE = {"rating": 4.0, "reviews": 37, "memory": "247", "relationships": "12",
          "engagement": "92%"}


def tiles() -> list[tuple]:
    """(label, value, unit, colour) — the three the profile screen leads with."""
    return [("Memory", SAMPLE["memory"], "entries", C["brandA"]),
            ("Relationships", SAMPLE["relationships"], "connections", C["amber"]),
            ("Engagement", SAMPLE["engagement"], "High", C["green"])]


def stars(x: float, y: float, rating: float) -> str:
    """Five glyphs, filled to the rating. Drawn rather than typed so the
    half-filled case cannot render as a missing-glyph box on a phone."""
    out = []
    for i in range(5):
        cx, filled = x + i * 15, i < int(round(rating))
        pts = []
        for k in range(10):
            r = 6.2 if k % 2 == 0 else 2.7
            import math
            a = -math.pi / 2 + k * math.pi / 5
            pts.append(f"{cx + r * math.cos(a):.1f},{y + r * math.sin(a):.1f}")
        out.append(f'<polygon points="{" ".join(pts)}" '
                   f'fill="{C["gold"] if filled else "none"}" '
                   f'stroke="{C["gold"]}" stroke-width="1" opacity="'
                   f'{1 if filled else 0.45}"/>')
    return "".join(out)


def card(handle: str, industry: str, display: str, tags: list[str]) -> str:
    role = ROLES[handle].replace("&amp;", "&")
    png = base64.b64encode((BUBBLES / f"{handle}.webp").read_bytes()).decode()
    role_lines = wrap(role, 30)
    chips = [t for t in tags if t != industry.replace("_", "-")][:3]

    # Height is derived, not guessed. The first cut used a constant plus a
    # nudge per role line and left every card with a strip of dead space under
    # the button — and would have clipped the moment a chip row wrapped.
    chip_rows, row_w = 1, 0.0
    for label in chips:
        w = 16 + len(label) * 6.4
        if row_w + w > W - PAD * 2:
            chip_rows, row_w = chip_rows + 1, 0.0
        row_w += w + 6
    quote_lines = wrap(REVIEWS[handle][2], 44)
    H = int(574 + 16 * len(role_lines) + 26 * (chip_rows - 1)
            + 14 * len(quote_lines) + PAD)

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

    # Rating other people gave it — screen 80 leads with this, above the
    # skills, because "what did people who talked to it think" outranks any
    # claim the profile makes about itself.
    ry += 6
    o.append(stars(cx - 70, ry, SAMPLE["rating"]))
    o.append(f'<text x="{cx+14}" y="{ry+5}" font-family="{FONT}" '
             f'font-size="13" font-weight="700" fill="{C["txt"]}">'
             f'{SAMPLE["rating"]:.1f} · {SAMPLE["reviews"]} reviews</text>')
    ry += 26

    o.append(f'<text x="{PAD}" y="{ry}" font-family="{FONT}" font-size="10" '
             f'font-weight="700" letter-spacing="0.8" fill="{C["t3"]}">'
             f'SKILLS</text>')
    ry += 14
    sx = PAD
    for label in chips:
        w = 16 + len(label) * 6.4
        if sx + w > W - PAD:
            sx, ry = PAD, ry + 26
        o.append(f'<rect x="{sx}" y="{ry}" width="{w:.1f}" height="22" rx="11" '
                 f'fill="{S.A(C["brandA"], 0.14)}" stroke="{C["brandA"]}"/>')
        o.append(f'<text x="{sx + w/2:.1f}" y="{ry+15}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="10.5" font-weight="600" '
                 f'fill="{C["brandA"]}">{esc(label)}</text>')
        sx += w + 6
    ry += 34

    # Memory · Relationships · Engagement, the three the profile screen puts
    # under the fold. Three across rather than two-up, so the card stays short
    # enough that two fit a phone row.
    tw = (W - PAD * 2 - 12) / 3
    for i, (label, value, unit, col) in enumerate(tiles()):
        tx = PAD + i * (tw + 6)
        o.append(f'<rect x="{tx:.1f}" y="{ry}" width="{tw:.1f}" height="58" '
                 f'rx="13" fill="url(#tile)" stroke="{C["line"]}"/>')
        o.append(f'<text x="{tx + tw/2:.1f}" y="{ry+17}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="9" fill="{C["t2"]}">'
                 f'{esc(label)}</text>')
        o.append(f'<text x="{tx + tw/2:.1f}" y="{ry+38}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="17" font-weight="800" '
                 f'fill="{col}">{esc(value)}</text>')
        o.append(f'<text x="{tx + tw/2:.1f}" y="{ry+50}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="8.5" fill="{C["t2"]}">'
                 f'{esc(unit)}</text>')
    ry += 72

    # Experience, then a review. Screen 80's order, and the order matters:
    # what the profile did comes before what somebody thought of it, because
    # the second only means something once you know the first.
    o.append(f'<text x="{PAD}" y="{ry}" font-family="{FONT}" font-size="10" '
             f'font-weight="700" letter-spacing="0.8" fill="{C["t3"]}">'
             f'EXPERIENCE</text>')
    ry += 12
    for title_, org in CAREERS[handle]:
        o.append(f'<rect x="{PAD}" y="{ry}" width="{W-PAD*2}" height="40" '
                 f'rx="12" fill="url(#tile)" stroke="{C["line"]}"/>')
        o.append(f'<text x="{PAD+12}" y="{ry+17}" font-family="{FONT}" '
                 f'font-size="11.5" font-weight="650" fill="{C["txt"]}">'
                 f'{esc(title_)}</text>')
        o.append(f'<text x="{PAD+12}" y="{ry+31}" font-family="{FONT}" '
                 f'font-size="9.5" fill="{C["t2"]}">{esc(org)}</text>')
        ry += 46

    stars_n, who, quote = REVIEWS[handle]
    # The experience boxes leave a 6px gap and this label's cap-height eats 8,
    # so without the nudge REVIEWS sits inside the box above it.
    ry += 12
    o.append(f'<text x="{PAD}" y="{ry}" font-family="{FONT}" font-size="10" '
             f'font-weight="700" letter-spacing="0.8" fill="{C["t3"]}">'
             f'REVIEWS</text>')
    o.append(f'<text x="{W-PAD}" y="{ry}" text-anchor="end" '
             f'font-family="{FONT}" font-size="8.5" fill="{C["t3"]}">'
             f'from people who talked to it</text>')
    ry += 12
    qlines = quote_lines
    rh = 34 + 14 * len(qlines)
    o.append(f'<rect x="{PAD}" y="{ry}" width="{W-PAD*2}" height="{rh}" '
             f'rx="12" fill="url(#tile)" stroke="{C["line"]}"/>')
    o.append(stars(PAD + 14, ry + 16, stars_n))
    o.append(f'<text x="{PAD+92}" y="{ry+20}" font-family="{FONT}" '
             f'font-size="9.5" font-weight="600" fill="{C["t2"]}">'
             f'{esc(who)}</text>')
    qy = ry + 36
    for line in qlines:
        o.append(f'<text x="{PAD+14}" y="{qy}" font-family="{FONT}" '
                 f'font-size="10.5" fill="{C["txt"]}">{esc(line)}</text>')
        qy += 14
    by = ry + rh + 14


    # How the button addresses them. A plain given name for most; an honorific
    # plus surname for the ones who carry one, because "Talk to Osei" reads as
    # a stranger being curt and "Talk to Dr. Osei" reads as the product.
    parts = display.split()
    first = (f"{parts[0]} {parts[-1]}"
             if parts[0] in ("Dr.", "Chef", "Coach") else parts[0])
    o.append(f'<rect x="{PAD}" y="{by}" width="{W-PAD*2}" height="44" rx="14" '
             f'fill="url(#brand)"/>')
    o.append(f'<text x="{cx}" y="{by+28}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="15" font-weight="700" '
             f'fill="#fff">Talk to {esc(first)}</text>')

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
