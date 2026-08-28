"""The stack's ears — and, since the watching, its eyes on a recording.

POST /transcribe {"url"} answers the words said in a recording,
transcribed by a local speech-to-text model. POST /watch {"url"} answers
the whole viewing: the same words, plus a handful of frames pulled evenly
across the recording, small JPEGs in base64 — what the video *shows*, for
a describer upstream to look at. Each door has a ``-file`` twin for bytes
already in hand.

The vault's ``fetch.listen`` tool (pdi/ears.py) asks here, named by
``PDI_EARS_URL``. The model and ffmpeg live in this container so the
vault's own image stays lean, and the transcription happens on the
deployment's own hardware — a recording fetched on someone's behalf never
leaves the facility to become words.

    asked     what was said in this recording
    mattered  the words, made at home — never the bytes shipped out

**The ears listen outward only.** The same rule as the eyes: private,
loopback, link-local and stack-internal addresses are refused, so a task
on the open web cannot use these ears against the stack behind them. And
they are ears, not an archive: the recording is downloaded to a temp file,
transcribed, and deleted — only the words and the frames leave this
container.
"""

import base64
import ipaddress
import os
import socket
import subprocess
import tempfile
import urllib.request
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()

# The stack's own names, and the ways a container reaches its host — the
# renderer's list plus this container's own name.
BLOCKED_NAMES = {"pdi", "qrme", "jim", "cloudgw", "bootstrap", "renderer",
                 "ears", "backup", "caddy", "localhost",
                 "host.docker.internal"}
MAX_TEXT = 800_000
#: A recording bigger than this is an archive job, not a lookout's errand.
MAX_MEDIA_BYTES = 200_000_000

_MODEL = None


def _model():
    """The Whisper model, loaded once per process. faster-whisper's int8
    CPU path — no GPU assumed; the weights were baked in at image build so
    a running stack never reaches out for them."""
    global _MODEL
    if _MODEL is None:
        from faster_whisper import WhisperModel
        _MODEL = WhisperModel(os.environ.get("EARS_MODEL", "base"),
                              device="cpu", compute_type="int8")
    return _MODEL


class ListenAsk(BaseModel):
    url: str


def _looks_inward(host: str | None) -> bool:
    h = (host or "").strip().lower().rstrip(".")
    if not h or h in BLOCKED_NAMES or "." not in h:
        return True
    try:
        return any(
            ipaddress.ip_address(info[4][0]).is_private
            or ipaddress.ip_address(info[4][0]).is_loopback
            or ipaddress.ip_address(info[4][0]).is_link_local
            for info in socket.getaddrinfo(h, None))
    except OSError:
        # A name that does not resolve plays nothing anyway; refusing it
        # here gives the caller one honest reason instead of a timeout.
        return True


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "ears": True}


def _words_from(box: str, media: str) -> dict:
    """The shared back half of both doors: ffmpeg makes one mono 16k wav
    out of whatever arrived — video or audio, any container — which is
    the one shape the model reads."""
    wav = os.path.join(box, "sound.wav")
    pulled = subprocess.run(
        ["ffmpeg", "-nostdin", "-y", "-i", media, "-vn", "-ac", "1",
         "-ar", "16000", wav],
        capture_output=True, timeout=300)
    if pulled.returncode != 0 or not os.path.exists(wav):
        raise HTTPException(
            422, "the recording carries no sound ffmpeg can read")
    segments, info = _model().transcribe(wav)
    text = " ".join(s.text.strip() for s in segments).strip()
    if not text:
        raise HTTPException(422, "the recording carries no speech")
    return {"text": text[:MAX_TEXT],
            "duration_seconds": round(getattr(info, "duration", 0.0), 1),
            "language": getattr(info, "language", None)}


#: How many frames a viewing keeps, and how wide each is scaled. Eight
#: evenly spaced stills tell a describer what a video shows without
#: shipping the video; 480 pixels is a look, not a copy.
WATCH_FRAMES = 8
FRAME_WIDTH = 480


def _frames_from(box: str, media: str) -> list[str]:
    """The eyes' half: up to WATCH_FRAMES stills pulled evenly across the
    recording, scaled down, JPEG, base64. An audio file simply has none —
    the empty list is the honest answer, not an error."""
    probed = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", media],
        capture_output=True, timeout=60)
    try:
        length = float(probed.stdout.strip())
    except (ValueError, TypeError):
        length = 0.0
    if length <= 0:
        return []
    frames: list[str] = []
    for i in range(WATCH_FRAMES):
        # Centered sampling — 1/16, 3/16, … 15/16 of the way through — so
        # neither a title card at 0:00 nor a black closing frame stands
        # for the whole video.
        at = length * (2 * i + 1) / (2 * WATCH_FRAMES)
        still = os.path.join(box, f"frame-{i}.jpg")
        pulled = subprocess.run(
            ["ffmpeg", "-nostdin", "-y", "-ss", f"{at:.2f}", "-i", media,
             "-frames:v", "1", "-vf", f"scale={FRAME_WIDTH}:-2",
             "-q:v", "5", still],
            capture_output=True, timeout=120)
        if pulled.returncode != 0 or not os.path.exists(still):
            continue
        with open(still, "rb") as fh:
            frames.append(base64.b64encode(fh.read()).decode("ascii"))
    # A short clip can yield the same still eight times; the describer
    # gains nothing from copies, so exact duplicates collapse.
    seen: set[str] = set()
    kept = [f for f in frames if not (f in seen or seen.add(f))]
    return kept


def _fetched(box: str, url: str) -> str:
    """The shared front half of both url doors: gates, download, caps."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(422, "transcribe needs an http(s) url")
    if _looks_inward(parsed.hostname):
        raise HTTPException(403, "the ears do not listen inward: private "
                                 "and stack-internal addresses are refused")
    media = os.path.join(box, "media")
    req = urllib.request.Request(url, headers={"user-agent": "qrme-ears"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, \
                open(media, "wb") as out:
            got = 0
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                got += len(chunk)
                if got > MAX_MEDIA_BYTES:
                    raise HTTPException(
                        413, "the recording is larger than the ears "
                             "will hold (200MB)")
                out.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 — one honest reason
        raise HTTPException(502, f"could not fetch the recording: {exc}")
    return media


def _watched(box: str, media: str) -> dict:
    """The whole viewing: words when there is speech, frames when there
    are pictures. A silent film and a podcast are both watchable; only a
    file that yields neither is refused."""
    try:
        heard = _words_from(box, media)
    except HTTPException:
        heard = {"text": "", "duration_seconds": None, "language": None}
    frames = _frames_from(box, media)
    if not heard["text"] and not frames:
        raise HTTPException(
            422, "the recording carries nothing to watch — no sound "
                 "ffmpeg can read and no pictures either")
    return {**heard, "frames": frames}


@app.post("/transcribe")
def transcribe(ask: ListenAsk) -> dict:
    with tempfile.TemporaryDirectory() as box:
        media = _fetched(box, ask.url)
        heard = _words_from(box, media)
    return {"url": ask.url, **heard}


@app.post("/watch")
def watch(ask: ListenAsk) -> dict:
    """The viewing door: one download, then both halves — the words said
    and the frames shown. What the transcribe door is to a podcast, this
    is to a video."""
    with tempfile.TemporaryDirectory() as box:
        media = _fetched(box, ask.url)
        viewing = _watched(box, media)
    return {"url": ask.url, **viewing}


@app.post("/transcribe-file")
async def transcribe_file(request: Request) -> dict:
    """The same ears for bytes already in hand — an upload somebody made
    to the stack, forwarded here as the raw body. Nothing is fetched and
    nothing leaves; the inward gate is for outbound targets and has no
    business on this door. The recording still touches disk only inside
    a temp directory that dies with the request."""
    data = await request.body()
    if not data:
        raise HTTPException(422, "the upload arrived empty")
    if len(data) > MAX_MEDIA_BYTES:
        raise HTTPException(413, "the recording is larger than the ears "
                                 "will hold (200MB)")
    with tempfile.TemporaryDirectory() as box:
        media = os.path.join(box, "media")
        with open(media, "wb") as out:
            out.write(data)
        heard = _words_from(box, media)
    return heard


@app.post("/watch-file")
async def watch_file(request: Request) -> dict:
    """The viewing for bytes already in hand — an upload somebody made to
    the stack. Same posture as /transcribe-file: nothing fetched, nothing
    kept, the recording touches disk only inside a temp directory that
    dies with the request."""
    data = await request.body()
    if not data:
        raise HTTPException(422, "the upload arrived empty")
    if len(data) > MAX_MEDIA_BYTES:
        raise HTTPException(413, "the recording is larger than the ears "
                                 "will hold (200MB)")
    with tempfile.TemporaryDirectory() as box:
        media = os.path.join(box, "media")
        with open(media, "wb") as out:
            out.write(data)
        viewing = _watched(box, media)
    return viewing
