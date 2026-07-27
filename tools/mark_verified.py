"""Burn the gold **verified real** mark into an authenticated person's photo.

The counterpart to ``tools/mark_portraits.py``, and the mirror image of what it
says. That one burns *AI* into a synthetic face so a picture circulating
outside QRME still says what it is. This burns *VERIFIED* into an
authentic photograph, for the same reason and with the same physics: a
composited badge does not survive a screenshot, a hotlink, or a right-click
save, and those are the journeys a profile picture actually takes.

**Gold, and nothing else.** Blue is Twitter/X and Facebook, grey is the
downgraded one everybody learned to distrust, green reads as the agent status
light two screens away, and red already means *stopped* in this product. Gold
is unclaimed in this space and reads as a distinction rather than a warning.

**It is gated, and the gate is a named attestor.**

A burned mark is the strongest claim an image can carry: it cannot be
qualified, it outlives every surface, and by design it travels to places where
nobody can check it. That is safe for *AI* — an AI rendering is AI-generated
wherever it ends up, forever, so burning it in can never become false.

*Verified* is not that kind of fact, so the gate is that somebody is **on the
record** as having attested to the identity. :func:`qrme.verification.verify`
stores who, by what method, and at what level, and this refuses to burn a photo
with no such record.

What the gate deliberately does **not** require is a particular rung. It first
required ``document``, and the platform's owner asked for the mark on his own
photograph at ``self_asserted`` — a decision he is entitled to make about his
own face on his own product, taken after the stricter version had been built
and the trade explained. So the burned word carries exactly the weight of
whoever attested, and the honest reading lives one call away:
``verification.status`` still reports ``self_asserted`` and still returns its
caveat. **Nothing in the code claims a document was checked, because none was.**

    python3 tools/mark_verified.py --preview
    python3 tools/mark_verified.py --preview        # render, do not install
    python3 tools/mark_verified.py <handle>         # burn, once attested
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "qrme" / "assets" / "photos"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

LABEL = "VERIFIED"

# The one colour left. See the module note for why each of the others is out.
GOLD = (212, 168, 58)
GOLD_LIGHT = (247, 216, 122)

# What the mark requires: a verification record with a named attestor. Not a
# particular rung — see the module note for whose decision that was and why the
# API still reports the real level either way.
REQUIRE_ATTESTOR = True


def mark(image: Image.Image) -> Image.Image:
    """Draw the gold mark into a copy of ``image``.

    Bottom-right. ``mark_portraits`` puts the AI mark top-right, diagonally
    opposite, so the two can never land on each other — a photograph should
    never carry both, but a layout that makes the collision impossible beats a
    rule saying it must not happen.
    """
    out = image.convert("RGB")
    w, h = out.size
    pad = round(w * 0.035)
    size = round(w * 0.085)
    try:
        font = ImageFont.truetype(FONT, size)
    except OSError:                                  # pragma: no cover
        font = ImageFont.load_default()

    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    text_w = draw.textlength(LABEL, font=font)
    box_h = round(size * 1.75)
    box_w = round(text_w + size * 2.6)
    x1, y1 = w - pad, h - pad
    x0, y0 = x1 - box_w, y1 - box_h

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


def _record_of(handle: str) -> dict:
    """The verification record for the profile owning ``handle``."""
    sys.path.insert(0, str(ROOT))
    from qrme import db, verification
    row = db.connect().execute(
        "SELECT profile_id FROM handles WHERE handle=?", (handle,)).fetchone()
    if row is None:
        return {}
    return verification.status(row["profile_id"])


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

    for handle in handles:
        path = PHOTOS / f"{handle}.webp"
        if not path.is_file():
            print(f"no photograph at {path}", file=sys.stderr)
            return 1
        record = _record_of(handle)
        if not record.get("verified") or not record.get("attestor"):
            print(f"refusing to burn {handle}: no verification record with a "
                  f"named attestor. A gold checkmark cannot be qualified once "
                  f"it is in the pixels, so somebody has to be on the record "
                  f"for it.", file=sys.stderr)
            return 1
        with Image.open(path) as im:
            mark(im).save(path, "WEBP", quality=90, method=6)
        print(f"burned the verified mark into {handle}.webp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
