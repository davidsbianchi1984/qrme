"""Burn the gold **verified real** mark into an authenticated person's photo.

The counterpart to ``tools/mark_portraits.py``, and the mirror image of what it
says. That one burns *AI* into a synthetic face so a picture circulating
outside QRME still says what it is. This burns *VERIFIED REAL* into an
authentic photograph, for the same reason and with the same physics: a
composited badge does not survive a screenshot, a hotlink, or a right-click
save, and those are the journeys a profile picture actually takes.

**Gold, and nothing else.** Blue is Twitter/X and Facebook, grey is the
downgraded one everybody learned to distrust, green reads as the agent status
light two screens away, and red already means *stopped* in this product. Gold
is unclaimed in this space and reads as a distinction rather than a warning.

**It is gated, and the gate is the whole point.**

A burned mark is the strongest claim an image can carry: it cannot be
qualified, it outlives every surface, and by design it travels to places where
nobody can check it. That is safe for *AI* — an AI rendering is AI-generated
wherever it ends up, forever, so burning it in can never become false.

*Verified real* is not that kind of fact. At ``self_asserted`` the only thing
established is that somebody typed their own name, and a gold checkmark on that
photograph would be a credential the platform minted for itself — which is the
exact failure the AI mark exists to prevent, pointed the other way.

So this refuses to burn anything below ``document``. Somebody has to have
checked an identity document, and a named attestor has to be on the record for
it. When that happens, run this. Until it does, the surfaces composite the
badge live from ``verification.status`` where the level rides along with it and
the caveat can be read.

    python3 tools/mark_verified.py --preview        # render, do not install
    python3 tools/mark_verified.py <handle>         # burn, once authenticated
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "qrme" / "assets" / "photos"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

LABEL = "VERIFIED REAL"

# The one colour left. See the module note for why each of the others is out.
GOLD = (212, 168, 58)
GOLD_LIGHT = (247, 216, 122)

# The rung this mark requires. Below it the claim is not established enough to
# burn into pixels that will outlive every place they can be checked.
REQUIRED_LEVEL = "document"


def mark(image: Image.Image) -> Image.Image:
    """Draw the gold mark into a copy of ``image``.

    Bottom-left. ``mark_portraits`` puts the AI mark top-right and every
    composited badge in the product is bottom-left; this is neither, so it can
    never land on top of the other one — a photograph should never carry both,
    but a layout that makes the collision impossible is better than a rule
    saying it must not happen.
    """
    out = image.convert("RGB")
    w, h = out.size
    pad = round(w * 0.035)
    size = round(w * 0.052)
    try:
        font = ImageFont.truetype(FONT, size)
    except OSError:                                  # pragma: no cover
        font = ImageFont.load_default()

    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    text_w = draw.textlength(LABEL, font=font)
    box_h = round(size * 1.75)
    box_w = round(text_w + size * 2.6)
    x0, y1 = pad, h - pad
    x1, y0 = x0 + box_w, y1 - box_h

    draw.rounded_rectangle((x0, y0, x1, y1), radius=box_h // 2,
                           fill=(24, 18, 4, 214), outline=GOLD, width=2)

    # The tick, drawn rather than typed: an emoji would depend on a font the
    # renderer may not have, and this mark has to look the same everywhere it
    # is scraped to.
    cx, cy = x0 + size * 1.05, (y0 + y1) / 2
    r = size * 0.44
    draw.line([(cx - r * 0.62, cy + r * 0.05),
               (cx - r * 0.16, cy + r * 0.52),
               (cx + r * 0.66, cy - r * 0.52)],
              fill=GOLD_LIGHT, width=max(2, round(size * 0.16)),
              joint="curve")
    draw.text((x0 + size * 1.85, cy), LABEL, font=font, anchor="lm",
              fill=GOLD_LIGHT)

    out.paste(Image.alpha_composite(out.convert("RGBA"), layer).convert("RGB"))
    return out


def _level_of(handle: str) -> str | None:
    """The recorded proofing level for the profile owning ``handle``."""
    sys.path.insert(0, str(ROOT))
    from qrme import db, verification
    row = db.connect().execute(
        "SELECT profile_id FROM handles WHERE handle=?", (handle,)).fetchone()
    if row is None:
        return None
    return verification.status(row["profile_id"]).get("level")


def main(argv: list[str]) -> int:
    if "--preview" in argv:
        src = next(iter(sorted(PHOTOS.glob("*.webp"))), None)
        if src is None:
            print("no photographs to preview", file=sys.stderr)
            return 1
        out = ROOT / "verified-preview.png"
        with Image.open(src) as im:
            mark(im).save(out)
        print(f"preview written to {out} (not installed)")
        return 0

    handles = [a for a in argv if not a.startswith("-")]
    if not handles:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2

    from qrme.signatures import PROOFING_LEVELS
    need = PROOFING_LEVELS.index(REQUIRED_LEVEL)
    for handle in handles:
        path = PHOTOS / f"{handle}.webp"
        if not path.is_file():
            print(f"no photograph at {path}", file=sys.stderr)
            return 1
        level = _level_of(handle)
        if level is None or PROOFING_LEVELS.index(level) < need:
            print(f"refusing to burn {handle}: proofing level is "
                  f"{level or 'unrecorded'}, and this mark requires "
                  f"{REQUIRED_LEVEL} or better. A gold checkmark cannot be "
                  f"qualified once it is in the pixels.", file=sys.stderr)
            return 1
        with Image.open(path) as im:
            mark(im).save(path, "WEBP", quality=90, method=6)
        print(f"burned the verified mark into {handle}.webp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
