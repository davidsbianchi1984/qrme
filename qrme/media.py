"""User-uploaded media for wall posts — the user's own photos and videos.

The wall could already carry a *link* (qrme/embeds.py, the facade contract);
this is the other half the field asked for: the user's own pixels, uploaded
and served from this deployment. Three rules:

* **A whitelist read from the bytes, not the filename.** The kind is decided
  by magic numbers — a renamed executable is refused no matter what its
  extension claims. Images: JPEG, PNG, WebP, GIF. Video: MP4, WebM.
* **Caps stated up front.** 8 MB for a picture, 60 MB for a video — a wall
  is a feed, not a locker. The limits ride ``GET /media/limits`` so a client
  can say so before the upload fails instead of after.
* **Never the AI mark.** These are the user's own photographs and footage.
  Burning the synthetic-media mark into an authentic picture is a false
  statement in exactly the direction the mark exists to prevent — the same
  line ``avatars.PHOTO_ROUTE`` draws for the verified founder photo.

Files live in a ``media`` directory beside the database (or wherever
``QRME_MEDIA_DIR`` points), served read-only at ``/media``. The row keeps the
uploader, so a post can only ever attach media its own author brought.
"""

from __future__ import annotations

import os
from pathlib import Path

from . import db

ROUTE = "/media"

# kind -> (max bytes, {extension: magic check})
IMAGE_MAX = 8 * 1024 * 1024
VIDEO_MAX = 60 * 1024 * 1024

_SNIFF = [
    # (kind, extension, test on the leading bytes)
    ("image", ".jpg",  lambda b: b[:3] == b"\xff\xd8\xff"),
    ("image", ".png",  lambda b: b[:8] == b"\x89PNG\r\n\x1a\n"),
    ("image", ".gif",  lambda b: b[:6] in (b"GIF87a", b"GIF89a")),
    ("image", ".webp", lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP"),
    ("video", ".mp4",  lambda b: b[4:8] == b"ftyp"),
    ("video", ".webm", lambda b: b[:4] == b"\x1a\x45\xdf\xa3"),
]


class MediaError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def media_dir() -> Path:
    configured = os.environ.get("QRME_MEDIA_DIR")
    if configured:
        return Path(configured)
    return Path(db.db_path()).resolve().parent / "qrme_media"


def limits() -> dict:
    return {
        "image": {"max_bytes": IMAGE_MAX,
                  "types": ["JPEG", "PNG", "GIF", "WebP"]},
        "video": {"max_bytes": VIDEO_MAX, "types": ["MP4", "WebM"]},
        "detected_from": "the file's own bytes, never its name",
        "ai_marked": False,
        "note": "your own photos and footage — authentic media is never "
                "stamped with the AI mark",
    }


def _sniff(data: bytes) -> tuple[str, str]:
    for kind, ext, test in _SNIFF:
        try:
            if test(data):
                return kind, ext
        except IndexError:                              # pragma: no cover
            continue
    raise MediaError(422, "unrecognized file — JPEG, PNG, GIF, WebP, MP4 "
                          "or WebM, detected from the bytes themselves")


def save(profile_id: str, data: bytes) -> dict:
    """Store one upload for this profile and return its serving facts."""
    if not data:
        raise MediaError(422, "the upload arrived empty")
    kind, ext = _sniff(data)
    cap = IMAGE_MAX if kind == "image" else VIDEO_MAX
    if len(data) > cap:
        raise MediaError(413, f"{kind} uploads top out at "
                              f"{cap // (1024 * 1024)} MB")
    media_id = db.new_id("med")
    directory = media_dir()
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{media_id}{ext}"
    (directory / filename).write_bytes(data)
    conn = db.connect()
    conn.execute(
        "INSERT INTO media (id, profile_id, kind, filename, bytes,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (media_id, profile_id, kind, filename, len(data), db.utcnow()))
    conn.commit()
    return {"id": media_id, "kind": kind, "url": f"{ROUTE}/{filename}",
            "bytes": len(data), "ai_marked": False}


def check_owned(profile_id: str, media_ids: list[str]) -> None:
    """Refuse anybody else's upload — called by wall.publish *before* the
    post row is written, so a refusal leaves no orphan post behind."""
    conn = db.connect()
    for media_id in media_ids:
        row = conn.execute("SELECT profile_id FROM media WHERE id=?",
                           (media_id,)).fetchone()
        if row is None or row["profile_id"] != profile_id:
            raise MediaError(422, f"no upload {media_id!r} on this profile")


def attach(post_id: str, profile_id: str, media_ids: list[str]) -> list[dict]:
    """Tie uploads to a post. Only the author's own uploads qualify —
    attaching somebody else's media id is refused, not borrowed."""
    conn = db.connect()
    out = []
    for media_id in media_ids:
        row = conn.execute("SELECT * FROM media WHERE id=?",
                           (media_id,)).fetchone()
        if row is None or row["profile_id"] != profile_id:
            raise MediaError(422, f"no upload {media_id!r} on this profile")
        conn.execute(
            "INSERT INTO post_media (post_id, media_id, created_at)"
            " VALUES (?,?,?)", (post_id, media_id, db.utcnow()))
        out.append(row_facade(row))
    conn.commit()
    return out


def row_facade(row) -> dict:
    return {"id": row["id"], "kind": row["kind"],
            "url": f"{ROUTE}/{row['filename']}", "ai_marked": False}


def for_posts(post_ids: list[str]) -> dict[str, list[dict]]:
    """Hydration for a page of posts, one query — see qrme.wall._hydrate."""
    if not post_ids:
        return {}
    marks = ",".join("?" * len(post_ids))
    rows = db.connect().execute(
        f"SELECT pm.post_id, m.* FROM post_media pm"
        f" JOIN media m ON m.id = pm.media_id"
        f" WHERE pm.post_id IN ({marks}) ORDER BY pm.rowid", post_ids
    ).fetchall()
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r["post_id"], []).append(row_facade(r))
    return out
