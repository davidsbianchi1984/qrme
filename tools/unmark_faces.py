"""Lift the burned-in marks back off the shipped faces.

## What changed, and why

Two marks were painted into the pixels of the shipped images: ``AI`` on
every portrait, top-right (``mark_portraits.py``), and ``VERIFIED`` on the
one photograph of a real person, bottom-right (``mark_verified.py``). Both
were burned rather than composited so the mark would survive the file being
hotlinked, scraped, saved or screenshotted — surfaces QRME does not control.

Every place the product actually draws a face draws it as a **circle**. A
mark painted into the corner of a square is cut in half by that circle, and
a disclosure sliced through the middle is worse than one drawn honestly on
top: it reads as a rendering fault, which is the opposite of the thing a
disclosure has to be.

    asked     take the AI and VERIFIED marks off the image itself
    mattered  the circle was eating them

So the marks move out of the pixels and onto the surface, drawn on the
outermost layer around the profile sphere where nothing can crop them.
``avatars.asset_is_marked`` reports False for the whole collection now,
which is the flag every surface already reads to decide whether to draw its
own badge — so they all start drawing one.

**The cost, stated plainly:** a portrait file fetched directly from
``/portraits/{handle}.webp`` no longer carries the disclosure in its bytes.
That is the gap the burn existed to close, and it is open again by
instruction. The checksum manifest stays — it still stops a shipped face
being swapped for a different one without the suite noticing.

## How the marks come off

Not by guessing where they were. Both marking tools are deterministic
functions of the image width, so this reproduces each shape exactly —
the same rounded rectangle, at the same coordinates — as a mask, grows it
a few pixels to catch the antialiased edge, and lets OpenCV reconstruct
what was underneath from the surrounding pixels.

That reconstruction is honest about what it is: an inpaint over a plain
backdrop is invisible, and over hair or a shoulder it is soft. It is run
once, offline, and the result is committed and looked at.

    python3 tools/unmark_faces.py            # lift, and rewrite the manifest
    python3 tools/unmark_faces.py --check    # verify against the manifest
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PORTRAITS = ROOT / "qrme" / "assets" / "portraits"
PHOTOS = ROOT / "qrme" / "assets" / "photos"
MANIFEST = PORTRAITS / "MANIFEST.json"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# How far past the drawn shape to reconstruct. The pill was composited with
# alpha, so its outermost ring of pixels is a blend of mark and photograph;
# repainting exactly the drawn shape leaves that ring behind as a faint
# outline of the thing that was removed.
GROW = 5


def _font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:                                  # pragma: no cover
        return ImageFont.load_default()


def ai_mask(size: tuple[int, int]) -> Image.Image:
    """The exact footprint of ``mark_portraits.mark`` at this size."""
    w, _ = size
    pad = round(w * 0.035)
    px = round(w * 0.115)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    text_w = draw.textlength("AI", font=_font(px))
    box_h = round(px * 1.65)
    box_w = round(text_w + px * 2.35)
    x1, y1 = w - pad, pad + box_h
    x0, y0 = x1 - box_w, pad
    draw.rounded_rectangle((x0 - GROW, y0 - GROW, x1 + GROW, y1 + GROW),
                           radius=box_h // 2 + GROW, fill=255)
    return mask


def verified_mask(size: tuple[int, int]) -> Image.Image:
    """The exact footprint of ``mark_verified.mark`` at this size."""
    w, h = size
    pad = round(w * 0.035)
    px = round(w * 0.085)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    text_w = draw.textlength("VERIFIED", font=_font(px))
    box_h = round(px * 1.75)
    box_w = round(text_w + px * 2.6)
    x1, y1 = w - pad, h - pad
    x0, y0 = x1 - box_w, y1 - box_h
    # Out to the corner, not merely around the plate. This one is drawn
    # with a two-pixel gold outline and sits a hair off the edge, so a
    # snug mask left the outline's far end behind as a stray gold curve —
    # visible in the seat as half a letter. There is nothing in the strip
    # between the plate and the corner worth keeping, so it goes too.
    draw.rounded_rectangle((x0 - GROW * 2, y0 - GROW * 2, w, h),
                           radius=box_h // 2 + GROW, fill=255)
    return mask


def lift(path: Path, mask: Image.Image) -> None:
    """Reconstruct what the mark was covering, in place.

    Mirrored, not diffused. A straight inpaint of a region this size
    reconstructs by spreading colour inward from the boundary, which is
    right over a plain studio backdrop and wrong over anything with
    texture — run across these portraits it left a legible smeared
    rectangle in the hair of everyone whose hair reached the corner.
    Looked at on a contact sheet, which is the only way to catch it.

    A face is roughly symmetric, and the same corner mirrored across the
    image carries the same KIND of thing: hair against hair, backdrop
    against backdrop, shoulder against shoulder. So the patch is the
    image's own mirror, feathered in over the mark's footprint, and the
    diffusing inpaint is left to do the one job it is good at — settling
    the thin seam where the patch meets the original.
    """
    import cv2

    image = Image.open(path).convert("RGB")
    src = np.asarray(image).astype(np.float32)
    feather = (np.asarray(mask.filter(ImageFilter.GaussianBlur(6)))
               .astype(np.float32) / 255.0)[..., None]
    blended = src * (1 - feather) + src[:, ::-1, :] * feather

    # Where the mirror would copy the mark onto itself.
    #
    # The AI pill is a narrow tab in one corner, so its reflection lands
    # on clean pixels. The VERIFIED plate is wide and nearly centred —
    # 151 to 494 across a 512px photograph — so its own reflection, 18 to
    # 361, overlaps it by two hundred pixels. Mirroring painted the left
    # half of the word back into the right half, and the seat came out
    # wearing "VERI" spelled backwards in gold. Caught in the shot, not
    # in the code.
    #
    # So the overlap is not mirrored at all: it is handed to the
    # diffusing inpaint, which has no source to get wrong.
    flipped = np.asarray(mask)[:, ::-1]
    solid = np.asarray(mask)
    both = ((solid > 8) & (flipped > 8)).astype(np.uint8) * 255

    seam = np.asarray(mask.filter(ImageFilter.GaussianBlur(3)))
    edge = ((seam > 20) & (seam < 235)).astype(np.uint8) * 255
    bgr = blended.astype(np.uint8)[:, :, ::-1].copy()
    healed = cv2.inpaint(bgr, np.maximum(edge, both), 4, cv2.INPAINT_TELEA)
    Image.fromarray(healed[:, :, ::-1]).save(path, "WEBP", quality=92)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    files = sorted(PORTRAITS.glob("*.webp"))
    if not files:
        print("no portraits found", file=sys.stderr)
        return 1

    if "--check" in argv:
        manifest = json.loads(MANIFEST.read_text())
        bad = [p.name for p in files if manifest.get(p.name) != digest(p)]
        missing = sorted(set(manifest) - {p.name for p in files})
        for name in bad:
            print(f"  ! {name} does not match the manifest")
        for name in missing:
            print(f"  ! {name} is in the manifest and not on disk")
        return 1 if (bad or missing) else 0

    for path in files:
        with Image.open(path) as im:
            size = im.size
        lift(path, ai_mask(size))
        print(f"  ✓ {path.name}")

    photo = PHOTOS / "david_bianchi.webp"
    if photo.exists():
        with Image.open(photo) as im:
            size = im.size
        lift(photo, verified_mask(size))
        print(f"  ✓ {photo.name}")

    MANIFEST.write_text(json.dumps(
        {p.name: digest(p) for p in sorted(PORTRAITS.glob("*.webp"))},
        indent=2, sort_keys=True) + "\n")
    print(f"  ✓ {MANIFEST.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
