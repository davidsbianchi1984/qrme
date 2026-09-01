"""The watching — the platform's own eyes on a recording or a picture.

## Where this came from

A plugin was being sold on video feeds as "Claude can now watch videos".
There is no secret underneath a tool like that: pull frames, hear the
soundtrack, hand both to a model. The house already had the ears
(``docker/ears``, reached through :mod:`qrme.scrape`) and a briefcase
comment that named the missing half out loud — *"these are ears, not
eyes"*. The owner's word on it: **"Let's make our own then."** So this
module is the eyes, made at home, and every borrowed part of it is a part
this stack already ran.

## What a viewing is

Two halves, each honest about its absence:

* ``heard`` — the words said in the recording, from the ears sidecar.
  Empty for a silent film, absent entirely when the stack has no ears.
* ``seen`` — an account of what the pictures show, written by the seeing
  door (:func:`qrme.llm.look`) over frames the sidecar pulled. Absent when
  the deployment cannot see (no key, offline) — never invented.

A viewing with neither half does not exist; the caller keeps the
held-not-watched posture the briefcase has always had.

## Who watches

* **Shared files** — a video or a picture handed to a room or a pair goes
  through :func:`observe_bytes` on its way in, so the very first profile
  turn after the share already knows what is on screen. A screenshot IS a
  screen read: the phone that cannot hand a live screen to a web page
  hands a screenshot instead, and the eyes read it the same.
* **Watch parties** — :func:`watch_link` fetches and watches a direct
  video link once, stores the viewing, and the party's prompt context
  swaps its blindness sentence for the truth of what was actually seen
  and heard. A platform page that only hands over a player is refused by
  name — fetching youtube.com yields markup, not the recording, and a
  viewing built on markup would be the lie this whole module exists to
  avoid.

Viewings are stored by subject, watched once: a room of eight profiles
does not watch the same video eight times on the owner's dime.
"""

from __future__ import annotations

import time
import uuid

from . import db, llm, scrape

#: What the describer is asked over a video's frames. The transcript rides
#: along when there is one, so "the speaker points at the chart" can name
#: the chart being discussed.
_VIDEO_ASK = (
    "These pictures are frames pulled evenly from one video, in order. "
    "Describe what the video shows: the setting, who or what is on "
    "screen, any readable text, and how it changes across the frames.")

#: And over a single shared picture — a photo, a screenshot, a grabbed
#: screen. Readable text matters most here: a screenshot is usually shared
#: FOR its words.
_PICTURE_ASK = (
    "Describe what this picture shows, for someone who cannot see it. If "
    "it is a screenshot or a captured screen, read out the text on it and "
    "say what application or page it appears to be.")

#: Image kinds the seeing door accepts, by magic bytes. GIF is absent on
#: purpose: an animation's first frame is not the animation, and claiming
#: to have seen one from it would be a small lie with the same shape as
#: the big ones.
_IMAGE_MAGIC = (
    (b"\xff\xd8", "image/jpeg"),
    (b"\x89PNG", "image/png"),
    (b"RIFF", "image/webp"),
)


def image_kind(data: bytes) -> str | None:
    """The media type of an image the eyes can read, or None. RIFF is
    shared ground with WAVE; the container's second name settles it."""
    for magic, kind in _IMAGE_MAGIC:
        if data[:len(magic)] == magic:
            if kind == "image/webp" and data[8:12] != b"WEBP":
                continue
            return kind
    return None


def _stored(subject: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM viewings WHERE subject=?", (subject,)).fetchone()
    if row is None:
        return None
    return {"subject": row["subject"], "heard": row["heard"] or "",
            "seen": row["seen"] or "",
            "duration_seconds": row["duration_seconds"],
            "language": row["language"], "watched_at": row["watched_at"]}


def _store(subject: str, heard: str, seen: str,
           duration: float | None, language: str | None) -> dict:
    conn = db.connect()
    conn.execute(
        "INSERT INTO viewings (id, subject, heard, seen, duration_seconds,"
        " language, watched_at) VALUES (?,?,?,?,?,?,?)"
        " ON CONFLICT(subject) DO UPDATE SET heard=excluded.heard,"
        " seen=excluded.seen, duration_seconds=excluded.duration_seconds,"
        " language=excluded.language, watched_at=excluded.watched_at",
        (f"view_{uuid.uuid4().hex[:12]}", subject, heard, seen,
         duration, language, int(time.time())))
    conn.commit()
    return _stored(subject)  # type: ignore[return-value]


def viewing_of(subject: str) -> dict | None:
    """The stored viewing for a URL or a media id — watched once, read
    many times."""
    return _stored(subject)


class NothingToWatch(Exception):
    """Raised with the translated sentence when a watch cannot happen for
    a reason the person can act on."""


def watch_link(url: str, on_behalf_of: str | None = None) -> dict | None:
    """Watch a direct video or audio link, once. Returns the stored
    viewing, or None when the stack's machinery cannot answer (no ears
    sidecar, a timeout) — the caller says held, not watched.

    Raises :class:`NothingToWatch` for the case that is not machinery but
    geometry: a platform page (a YouTube link, a TikTok link) hands over
    a player, not the recording, and no honest viewing can be built from
    it. The sentence names the fix — a direct link to the file.
    """
    held = _stored(url)
    if held is not None:
        return held
    if not scrape.is_recording(url):
        raise NothingToWatch(
            "that platform hands over a player, not the recording — only "
            "a direct video or audio link can be watched")
    viewing = scrape.watch_url(url, on_behalf_of)
    if viewing is None:
        return None
    seen = llm.look(_ask_with(viewing["text"]), viewing["frames"]) or ""
    return _store(url, viewing["text"], seen,
                  viewing.get("duration_seconds"), viewing.get("language"))


def _ask_with(heard: str) -> str:
    if not heard:
        return _VIDEO_ASK
    return (_VIDEO_ASK + "\n\nThe words said in it, for reference:\n"
            + heard[:2000])


def observe_bytes(data: bytes, on_behalf_of: str | None = None
                  ) -> tuple[str, str]:
    """``(heard, seen)`` for an uploaded video's bytes — the ears' words
    and the eyes' account, each empty when its half of the machinery is
    absent. The briefcase's video branch calls this where it used to call
    the ears alone."""
    viewing = scrape.watch_bytes(data, on_behalf_of)
    if viewing is None:
        return "", ""
    seen = llm.look(_ask_with(viewing["text"]), viewing["frames"]) or ""
    return viewing["text"], seen


def see_picture(data: bytes) -> str:
    """What a shared picture shows, or "" — the eyes over one image. The
    briefcase's photo branch calls this where it used to answer *held,
    not read* unconditionally. A screenshot is the phone's way of handing
    over its screen, so the ask leans on readable text."""
    import base64
    kind = image_kind(data)
    if kind is None:
        return ""
    return llm.look(_PICTURE_ASK,
                    [base64.b64encode(data).decode("ascii")],
                    media_type=kind) or ""
