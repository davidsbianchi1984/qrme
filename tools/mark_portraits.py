"""Burn the AI mark into the shipped portraits.

The AI disclosure already rides *alongside* every portrait: ``GET
/profiles/{id}/avatar`` returns the watermark with the asset, and the beacon
page and camera overlays composite it. That covers every surface QRME
controls — and none of the ones it does not.

The portraits are served as ordinary files at ``/portraits/{handle}.webp``.
That URL can be hotlinked, embedded, scraped, screenshotted, or saved, and in
every one of those cases a composited badge is simply absent. A synthetic face
would then be circulating with nothing saying so, which is the exact failure
the watermark exists to prevent.

So the mark goes into the pixels. Run once, offline, and commit the result:
burning at request time would mean an imaging library in the runtime
dependencies and a redraw on every fetch, to reach a mark that never changes.

The mark sits **top-right**. Every composited badge in the product is
bottom-left (`landing.py`, `BeaconScannerView`, `BeaconScanner.kt`), so the two
never collide and a surface that draws its own live badge still shows the
profile's designed label underneath.

    python3 tools/mark_portraits.py            # mark, and rewrite the manifest
    python3 tools/mark_portraits.py --check    # verify against the manifest
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PORTRAITS = ROOT / "qrme" / "assets" / "portraits"
MANIFEST = PORTRAITS / "MANIFEST.json"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

LABEL = "AI"


def mark(image: Image.Image) -> Image.Image:
    """Draw the mark into a copy of ``image``."""
    out = image.convert("RGB")
    w, _ = out.size
    pad = round(w * 0.035)
    size = round(w * 0.062)
    try:
        font = ImageFont.truetype(FONT, size)
    except OSError:                                  # pragma: no cover
        font = ImageFont.load_default()

    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    text_w = draw.textlength(LABEL, font=font)
    box_h = round(size * 1.65)
    box_w = round(text_w + size * 2.35)
    x1, y1 = w - pad, pad + box_h
    x0, y0 = x1 - box_w, pad

    # A dark pill so the mark stays legible over a light shoulder or a dark
    # background alike — a portrait collection cannot assume either.
    draw.rounded_rectangle((x0, y0, x1, y1), radius=box_h // 2,
                           fill=(9, 7, 24, 205))
    # The glyph that heads the watermark line everywhere else in the product.
    cx, cy = x0 + size * 0.85, (y0 + y1) / 2
    r = size * 0.42
    draw.polygon([(cx, cy - r), (cx + r * 0.42, cy - r * 0.42),
                  (cx + r, cy), (cx + r * 0.42, cy + r * 0.42),
                  (cx, cy + r), (cx - r * 0.42, cy + r * 0.42),
                  (cx - r, cy), (cx - r * 0.42, cy - r * 0.42)],
                 fill=(255, 255, 255, 235))
    draw.text((x0 + size * 1.5, cy), LABEL, font=font, anchor="lm",
              fill=(255, 255, 255, 240))

    out.paste(Image.alpha_composite(out.convert("RGBA"), layer).convert("RGB"))
    return out


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    files = sorted(PORTRAITS.glob("*.webp"))
    if not files:
        print("no portraits found", file=sys.stderr)
        return 1

    if "--check" in argv:
        expected = json.loads(MANIFEST.read_text())
        bad = [p.name for p in files if expected.get(p.name) != digest(p)]
        missing = sorted(set(expected) - {p.name for p in files})
        if bad or missing:
            print("manifest mismatch:", bad + missing, file=sys.stderr)
            return 1
        print(f"{len(files)} portraits match the manifest")
        return 0

    for path in files:
        with Image.open(path) as im:
            mark(im).save(path, "WEBP", quality=88, method=6)
    MANIFEST.write_text(json.dumps(
        {p.name: digest(p) for p in files}, indent=2, sort_keys=True) + "\n")
    print(f"marked {len(files)} portraits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
