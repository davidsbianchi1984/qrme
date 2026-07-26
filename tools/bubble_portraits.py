"""Bake the avatar bubble into a portrait, for surfaces that cannot draw it.

Inside the product, a portrait is never shown raw. ``docs/screens/build.py``'s
:func:`face` puts it in a rounded box over a soft brand glow with a hairline
border — the "avatar bubble" — and every screen that shows a face does that at
render time.

The README cannot. It embeds the shipped ``.webp`` directly, and those files
are square RGB with a near-black backdrop, so the gallery renders 34 hard-edged
**black boxes** where the app shows bubbles. The obvious fix — a `style`
attribute on the `<img>` — does not survive: GitHub's markdown sanitiser strips
it, so the bubble has to be *in the pixels* or it does not happen at all.

That is the same reasoning as ``tools/mark_portraits.py``: a surface QRME does
not control cannot be asked to composite anything. Run once, offline, commit
the result.

**Derived, never in place.** These are written to a separate directory and the
originals are untouched. ``qrme/assets/portraits/`` is what the API serves at
``/portraits/{handle}.webp`` and what ``frames.PORTRAITS`` feeds to the screens
— and the screens draw their *own* bubble. Baking one into the source would
show every app screen a bubble inside a bubble.

**Alpha, not a background colour.** The corners and the glow margin are
transparent, so the gallery sits on whatever GitHub is using — the reader's
theme, not a guess at it. A baked-in dark backdrop would be the black box again
by another route, and would be visibly wrong in light mode.

    python3 tools/bubble_portraits.py            # write docs/portraits/bubbles/
    python3 tools/bubble_portraits.py --check    # verify they are current
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "qrme" / "assets" / "portraits"
OUT = ROOT / "docs" / "portraits" / "bubbles"

# Matched to docs/screens/build.py:face() so the README and the app agree.
RADIUS = 0.28                    # of the portrait's side
GLOW_MARGIN = 0.18               # canvas padding, as a fraction of the side
GLOW = (123, 92, 255)            # C["brandA"] — the neon purple
GLOW_ALPHA = 0.5                 # face() draws url(#glow) at 0.5 in the centre
BORDER = (255, 255, 255, 56)     # rgba(255,255,255,0.22)


def bubble(image: Image.Image) -> Image.Image:
    """A portrait in its avatar bubble, on transparency."""
    im = image.convert("RGBA")
    w, _ = im.size
    pad = round(w * GLOW_MARGIN)
    side = w + pad * 2
    rad = round(w * RADIUS)

    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))

    # The glow: face() lays a radial gradient circle of r*1.45 behind the box.
    # Approximated by a blurred rounded rect, which reads the same at gallery
    # size and does not need a gradient per file.
    halo = Image.new("L", (side, side), 0)
    ImageDraw.Draw(halo).rounded_rectangle(
        (pad * 0.45, pad * 0.45, side - pad * 0.45, side - pad * 0.45),
        radius=rad + pad // 2, fill=round(255 * GLOW_ALPHA))
    halo = halo.filter(ImageFilter.GaussianBlur(pad * 0.62))
    canvas.paste(Image.new("RGBA", (side, side), GLOW + (255,)), (0, 0), halo)

    # The portrait, clipped to the rounded box.
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, w - 1), radius=rad,
                                           fill=255)
    canvas.paste(im, (pad, pad), mask)

    # The hairline border, drawn on the same rounded path.
    edge = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle(
        (pad, pad, pad + w - 1, pad + w - 1), radius=rad, outline=BORDER,
        width=max(2, round(w * 0.006)))
    return Image.alpha_composite(canvas, edge)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    files = sorted(SRC.glob("*.webp"))
    if not files:
        print(f"no portraits in {SRC}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    missing = []
    for path in files:
        target = OUT / path.name
        if check:
            if not target.exists():
                missing.append(path.name)
            continue
        bubble(Image.open(path)).save(target, "WEBP", quality=90, method=6,
                                      lossless=False)

    if check:
        if missing:
            print(f"missing bubbles: {', '.join(missing)}", file=sys.stderr)
            return 1
        print(f"all {len(files)} bubbles present")
        return 0
    print(f"wrote {len(files)} bubbles to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
