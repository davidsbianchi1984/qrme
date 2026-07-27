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

# The starter portraits, as thumbnails for the collection grid. 114px square
# is about 2x the ~46px each one gets in a five-column grid on the phone
# screen, so it stays crisp without carrying a megabyte into the file: the
# whole set of 34 costs roughly 140 KB of base64.
PORTRAIT_SRC = ROOT / "qrme" / "assets" / "portraits"
PORTRAIT_PX = 114
PORTRAIT_Q = 70


def encode(path: pathlib.Path) -> str:
    im = Image.open(path).convert("RGB")
    im = im.resize((WIDTH, round(WIDTH * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def encode_square(path: pathlib.Path, px: int, quality: int) -> str:
    im = Image.open(path).convert("RGB").resize((px, px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def portrait_entries() -> list[tuple[str, str]]:
    """Every starter portrait, in the order seed.py defines them.

    Read from seed.py rather than from a directory listing so the grid is the
    collection, in its own order, rather than whatever the filesystem hands
    back — and so a portrait added without a starter (or the reverse) shows up
    as a missing file here instead of a silently short grid.
    """
    import sys
    sys.path.insert(0, str(ROOT))
    from qrme.seed import RATED, STARTERS

    out = []
    for handle, _industry, name, *_ in list(STARTERS) + list(RATED):
        src = PORTRAIT_SRC / f"{handle}.webp"
        if not src.is_file():
            raise SystemExit(f"no portrait for starter {handle!r} at {src}")
        out.append((name, encode_square(src, PORTRAIT_PX, PORTRAIT_Q)))
    return out


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

    entries = portrait_entries()
    total = sum(len(b) for _, b in entries)
    parts.append(f"# The starter collection: {len(entries)} portraits at "
                 f"{PORTRAIT_PX}px ({total // 1024} KB base64 total).")
    parts.append("# (display_name, base64 jpeg), in seed.py's order.")
    parts.append("PORTRAITS = [")
    for name, b64 in entries:
        chunks = "\n".join(f'      "{c}"' for c in textwrap.wrap(b64, 96))
        parts.append(f'    ("{name}",\n{chunks}),')
    parts.append("]")
    parts.append("")
    print(f"portraits: {len(entries)} at {PORTRAIT_PX}px, "
          f"{total // 1024} KB base64")

    # The founder, kept out of PORTRAITS on purpose. That list documents itself
    # as the starter collection, and every starter is an invented person; this
    # one is a real person, so folding him in would make the comment above it
    # false. The friends screens want his face, so it gets its own name.
    import sys
    sys.path.insert(0, str(ROOT))
    from qrme.seed import (FOUNDER_HANDLE, FOUNDER_NAME, LIVE_HANDLE,
                           LIVE_NAME)
    PHOTO_SRC = ROOT / "qrme" / "assets" / "photos"
    for const, handle, name, src_dir, note in (
            ("FOUNDER", FOUNDER_HANDLE, FOUNDER_NAME, PORTRAIT_SRC,
             "the AI rendering, marked in its own pixels"),
            ("FOUNDER_LIVE", LIVE_HANDLE, LIVE_NAME, PHOTO_SRC,
             "the photograph — authentic, so deliberately unmarked")):
        fsrc = src_dir / f"{handle}.webp"
        if not fsrc.is_file():
            raise SystemExit(f"no founder image at {fsrc}")
        fb64 = encode_square(fsrc, PORTRAIT_PX, PORTRAIT_Q)
        fchunks = "\n".join(f'    "{c}"' for c in textwrap.wrap(fb64, 96))
        parts.append(f"# The founder, {note}. Kept out of the starter")
        parts.append("# collection above, which is invented people only.")
        parts.append(f'{const} = ("{name}",\n{fchunks})')
        parts.append("")
        print(f"{const}: {len(fb64) // 1024} KB base64")

    OUT.write_text("\n".join(parts))
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
