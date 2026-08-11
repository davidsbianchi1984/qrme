"""User-uploaded media for wall posts — the user's own photos and videos.

The wall could already carry a *link* (qrme/embeds.py, the facade contract);
this is the other half the field asked for: the user's own pixels, uploaded
and served from this deployment. Three rules:

* **A whitelist read from the bytes, not the filename.** The kind is decided
  by magic numbers — a renamed executable is refused no matter what its
  extension claims. Images: JPEG, PNG, WebP, GIF. Video: MP4, WebM. Files:
  PDF, the zip-family office documents (docx/xlsx/pptx/zip — PK magic, with
  the extension taken from a whitelist rather than trusted), and plain text
  (txt/csv/md). Nothing that a browser executes: no HTML, no SVG, no
  scripts — a text file that *contains* markup is stored and served as
  ``text/plain``, where markup is just characters.
* **Caps stated up front.** 8 MB for a picture, 60 MB for a video, 20 MB
  for a file — a wall is a feed, not a locker. The limits ride
  ``GET /media/limits`` so a client can say so before the upload fails
  instead of after.
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
FILE_MAX = 20 * 1024 * 1024

_MAX = {"image": IMAGE_MAX, "video": VIDEO_MAX, "file": FILE_MAX}

# Extensions a PK-magic (zip family) or text upload may keep. The magic
# proves the container; the whitelisted extension only picks which safe
# label it is served under — anything else becomes .zip or .txt.
_PK_EXTS = {".docx", ".xlsx", ".pptx", ".zip"}
_TEXT_EXTS = {".txt", ".csv", ".md"}

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
        "file": {"max_bytes": FILE_MAX,
                 "types": ["PDF", "DOCX", "XLSX", "PPTX", "ZIP",
                           "TXT", "CSV", "MD"]},
        "detected_from": "the file's own bytes, never its name",
        "ai_marked": False,
        "note": "your own photos and footage — authentic media is never "
                "stamped with the AI mark",
    }


def _named_ext(name: str | None) -> str:
    if not name or "." not in name:
        return ""
    return "." + name.rsplit(".", 1)[1].lower()


def _sniff(data: bytes, name: str | None = None) -> tuple[str, str]:
    for kind, ext, test in _SNIFF:
        try:
            if test(data):
                return kind, ext
        except IndexError:                              # pragma: no cover
            continue
    # Documents. The magic proves the container; the extension only picks
    # which safe label it is served under — never trusted beyond the list.
    if data[:4] == b"%PDF":
        return "file", ".pdf"
    if data[:4] == b"PK\x03\x04":
        ext = _named_ext(name)
        return "file", ext if ext in _PK_EXTS else ".zip"
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        raise MediaError(
            422, "unrecognized file — pictures (JPEG, PNG, GIF, WebP), "
                 "video (MP4, WebM) or documents (PDF, docx/xlsx/pptx/zip, "
                 "plain text), detected from the bytes themselves") from None
    # Plain text serves as text/plain, where any markup is just characters —
    # which is why .html and .svg are deliberately not in the list.
    ext = _named_ext(name)
    return "file", ext if ext in _TEXT_EXTS else ".txt"


def save(profile_id: str, data: bytes, name: str | None = None,
         alt: str | None = None) -> dict:
    """Store one upload for this profile and return its serving facts."""
    if not data:
        raise MediaError(422, "the upload arrived empty")
    kind, ext = _sniff(data, name)
    cap = _MAX[kind]
    if len(data) > cap:
        raise MediaError(413, f"{kind} uploads top out at "
                              f"{cap // (1024 * 1024)} MB")
    media_id = db.new_id("med")
    directory = media_dir()
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{media_id}{ext}"
    (directory / filename).write_bytes(data)
    # The display name is the uploader's own, kept for the card and nothing
    # else — the file on disk is named by its id and whitelisted extension.
    display = (name or "").strip()[:120] or None
    description = (alt or "").strip()[:300] or None
    conn = db.connect()
    conn.execute(
        "INSERT INTO media (id, profile_id, kind, filename, name, bytes,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (media_id, profile_id, kind, filename, display, len(data),
         db.utcnow()))
    if description:
        conn.execute(
            "INSERT INTO media_alt (media_id, alt, created_at)"
            " VALUES (?,?,?)", (media_id, description, db.utcnow()))
    conn.commit()
    return {"id": media_id, "kind": kind, "url": f"{ROUTE}/{filename}",
            "name": display, "bytes": len(data), "alt": description,
            "ai_marked": False}


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
        row = conn.execute(
            "SELECT m.*, a.alt AS alt FROM media m"
            " LEFT JOIN media_alt a ON a.media_id = m.id WHERE m.id=?",
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
            "url": f"{ROUTE}/{row['filename']}",
            "name": row["name"],
            "alt": row["alt"] if "alt" in row.keys() else None,
            "ai_marked": False}


def for_posts(post_ids: list[str]) -> dict[str, list[dict]]:
    """Hydration for a page of posts, one query — see qrme.wall._hydrate."""
    if not post_ids:
        return {}
    marks = ",".join("?" * len(post_ids))
    rows = db.connect().execute(
        f"SELECT pm.post_id, m.*, a.alt AS alt FROM post_media pm"
        f" JOIN media m ON m.id = pm.media_id"
        f" LEFT JOIN media_alt a ON a.media_id = m.id"
        f" WHERE pm.post_id IN ({marks}) ORDER BY pm.rowid", post_ids
    ).fetchall()
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r["post_id"], []).append(row_facade(r))
    return out
