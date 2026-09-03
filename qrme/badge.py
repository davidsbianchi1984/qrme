"""The AI badge, burned into the bytes of anything rendered that leaves.

On screen the badge is the outermost layer: drawn by the console over
the player, over the full-screen takeover, over everything — never in
the pixels, so the footage plays clean and the badge cannot be scrolled,
covered or expanded away. That layer stops at the edge of the window.
A downloaded file has no console around it, so for a download the badge
is burned into the image itself, top-left, before the bytes go out.

    asked     the AI badge is the outermost overlay, and a download
              still carries it
    mattered  a badge drawn by the page is not in the file; a badge in
              the file cannot be the page's outermost layer — so there
              are two, one for each

`ai_marked` on a media row is the only thing that earns a burn: an
authentic upload is never stamped, because stamping it would be a false
statement in the direction the mark exists to prevent. A rendered scene
is stored with ``ai_marked=True`` and no argument turns that off
(`filming.save`).

Images are burned with Pillow. Video is burned with ffmpeg, an overlay
of the same badge picture; a deployment without ffmpeg refuses the
download rather than serving an unmarked copy.
"""

from __future__ import annotations

import io
import shutil
import subprocess
from pathlib import Path

from . import db, media

TEXT = "AI-GENERATED"
#: Where the badge sits, in pixels from the top-left corner.
MARGIN = 12


class NoBadge(LookupError):
    """No such media, or media that is not synthetic."""


class NoBurner(RuntimeError):
    """This deployment cannot burn a badge into that kind of file."""


def _badge_png(height: int) -> bytes:
    """The badge picture at a size that reads on a frame this tall."""
    from PIL import Image, ImageDraw, ImageFont
    size = max(14, height // 18)
    try:
        font = ImageFont.load_default(size=size)
    except TypeError:  # an older Pillow: one size only
        font = ImageFont.load_default()
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = probe.textbbox((0, 0), "✦ " + TEXT, font=font)
    w, h = box[2] - box[0] + size, box[3] - box[1] + size // 2
    img = Image.new("RGBA", (w, h), (8, 6, 16, 200))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 3,
                           outline=(159, 216, 232, 230), width=1)
    draw.text((size // 2 - box[0], size // 4 - box[1]), "✦ " + TEXT,
              font=font, fill=(159, 216, 232, 255))
    out = io.BytesIO()
    img.save(out, "PNG")
    return out.getvalue()


def _row(media_id: str):
    row = db.connect().execute(
        "SELECT id, kind, filename, ai_marked FROM media WHERE id=?",
        (media_id,)).fetchone()
    if row is None:
        raise NoBadge(f"no such media: {media_id}")
    if not row["ai_marked"]:
        raise NoBadge("this file is not synthetic media; nothing is burned "
                      "into an authentic upload")
    return row


def burned(media_id: str) -> Path:
    """The path of the burned copy, made on first ask and kept."""
    row = _row(media_id)
    source = media.media_dir() / row["filename"]
    if not source.exists():
        raise NoBadge(f"the file behind {media_id} is gone")
    target = source.with_name(source.stem + ".badged" + source.suffix)
    if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
        return target
    if row["kind"] == "image":
        _burn_image(source, target)
    elif row["kind"] == "video":
        _burn_video(source, target)
    else:
        raise NoBurner("only pictures and footage carry a burned badge")
    return target


def _burn_image(source: Path, target: Path) -> None:
    from PIL import Image
    with Image.open(source) as im:
        frame = im.convert("RGBA")
        badge = Image.open(io.BytesIO(_badge_png(frame.height))).convert("RGBA")
        frame.alpha_composite(badge, (MARGIN, MARGIN))
        if source.suffix.lower() in (".jpg", ".jpeg"):
            frame = frame.convert("RGB")
        frame.save(target)


def _burn_video(source: Path, target: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise NoBurner("this deployment has no ffmpeg, so the badge cannot "
                       "be burned into footage — the download is refused "
                       "rather than served unmarked")
    badge = source.with_name(source.stem + ".badge.png")
    # Sized for a 720-line frame; ffmpeg scales the overlay with the
    # frame so it reads the same at any height.
    badge.write_bytes(_badge_png(720))
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(source),
           "-i", str(badge),
           "-filter_complex",
           f"[1][0]scale2ref=w='iw*0.28':h='ow/mdar'[b][v];"
           f"[v][b]overlay={MARGIN}:{MARGIN}",
           "-c:a", "copy", "-movflags", "+faststart", str(target)]
    done = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if done.returncode != 0 or not target.exists():
        raise NoBurner("ffmpeg could not burn the badge: "
                       + done.stderr.strip()[-300:])
