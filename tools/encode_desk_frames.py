#!/usr/bin/env python3
"""Encode the desk camera frames into `docs/screens/frames.py`.

The screen generators are deliberately dependency-free — `build.py` imports
nothing outside the standard library, so anyone can regenerate the galleries
without installing Pillow. But the desk screens need the *actual* photographs
in them, and an SVG loaded through an ``<img>`` tag (which is how GitHub
renders one in a README) cannot fetch an external file: a relative path to the
`.webp` would render as an empty box.

So the pixels have to travel inside the SVG as a data URI, and that encoding is
done here, once, and committed. Run this only when the source frames change:

    python3 tools/encode_desk_frames.py

JPEG rather than WebP because ``<image>`` inside SVG is rendered by more things
than support WebP, and these need to survive a README, a raw file view, and
whatever converter someone points at them.
"""

from __future__ import annotations

import base64
import io
import pathlib
import textwrap

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "qrme" / "assets" / "desks"
OUT = ROOT / "docs" / "screens" / "frames.py"

# 560px wide: the mobile screens show the frame about 300px across and the
# desktop views about 430px, so this stays crisp on a 2x display without
# carrying a megabyte of base64 into every file that embeds it.
WIDTH = 560
QUALITY = 71

FRAMES = {"DESK": "desk_view.webp", "STAGE": "stage_view.webp"}


def encode(path: pathlib.Path) -> str:
    im = Image.open(path).convert("RGB")
    im = im.resize((WIDTH, round(WIDTH * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def main() -> None:
    parts = [
        '"""The desk camera frames, base64 JPEG — GENERATED, do not edit.',
        "",
        "Written by tools/encode_desk_frames.py from qrme/assets/desks/*.webp.",
        "Lives here so docs/screens/build.py can stay dependency-free while the",
        "desk screens still show the real photograph rather than a placeholder.",
        '"""',
        "",
    ]
    for name, filename in FRAMES.items():
        src = SRC / filename
        b64 = encode(src)
        wrapped = "\n".join(f'    "{c}"'
                            for c in textwrap.wrap(b64, 96))
        parts.append(f"# {filename}  ({len(b64) // 1024} KB base64)")
        parts.append(f"{name} = (\n{wrapped}\n)")
        parts.append("")
        print(f"{filename}: {len(b64) // 1024} KB base64")
    OUT.write_text("\n".join(parts))
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
