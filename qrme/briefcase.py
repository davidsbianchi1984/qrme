"""What you hand a profile, read once and kept.

## The finding

A person in a conversation could already hand a profile a link, and the
profile would read it: ``interaction._handed_link_block`` pulls the first
URL out of the turn, fetches the page, and stuffs the visible text into that
turn's system prompt. It worked, and it evaporated. Nothing was stored, so
the *next* turn — the one where you actually discuss the thing — carried no
page at all. To keep talking about a document you had to keep pasting it,
and every paste re-fetched the whole of it and re-sent it to the model.

    asked     can the profile read what you hand it
    mattered  can it still remember it on the next turn

And a link was the only thing you could hand it. A photograph, a filing, a
spreadsheet, a video — the material a conversation is actually *about* — had
no way in at all. Ask a profile about your patents and the only route was to
retype them.

## What this module is

A briefcase, scoped to one conversation: the pair (profile, interactor).
Material is read **at import**, distilled **once**, and the distillation is
what every later turn carries. The raw text is kept beside it for a person
to read back, but it is never what goes to the model — a forty-page filing
enters the prompt as a few hundred characters that were paid for a single
time.

That is the whole economy of the thing. Re-pasting a document costs its full
length on every turn; importing it costs its full length once, and a digest
thereafter.

## Whose material it is

Deliberately **not** a ``source_items`` row. Source material is what the
profile recalls *as its own* — its life, its trade, the packs its owner
installed — and it is the same for everybody who talks to it. A briefcase
item is what *one visitor* brought to *one conversation*, and it stays there:
the person next in line does not inherit your medical records, and the
profile's owner does not acquire them either. The clinical-notes block in
``persona.build_system_prompt`` already draws exactly this line, and for the
same reason; this follows it.

The import runs against the profile the person is talking to, whichever that
is — a starter, a hybrid, a rated profile, somebody's own likeness. There is
no allow-list, because "the profile you are talking to" is the only answer
that is ever right.

## What it refuses to pretend

The honest failure is the point of the ``read`` flag. This deployment cannot
see a photograph and cannot watch a video; a PDF that carries only scanned
pixels has no text in it to find. In every one of those cases the item is
still imported — with whatever the person said it was — and the prompt block
says plainly that the profile has *not* seen it and must not describe it.
A profile that invents the contents of a picture it was handed is worse than
one that says "tell me what's in it".

Offline deployments do not fetch links, the same switch every other outbound
path honours, and the item records that it could not be read rather than
timing out mid-conversation.
"""

from __future__ import annotations

import re
import zipfile
import zlib
from io import BytesIO

from . import db, llm, media, offline, scrape

#: Kinds a person can hand over. ``photo`` and ``video`` are stored for what
#: the person says about them; the rest carry text this deployment can read.
KINDS = ("link", "photo", "video", "document", "recording")

#: How much extracted text is kept per item. Generous for a filing, small
#: enough that a briefcase is not an archive.
MAX_TEXT = 20_000

#: How much of the digest is carried into the prompt on every turn. This is
#: the number the credit argument rests on: the digest is what recurs.
MAX_DIGEST = 700

#: How many items one conversation may carry into the prompt, newest first.
PROMPT_ITEMS = 6

#: Hard cap on a single briefcase, so an import loop cannot grow a
#: conversation without bound.
MAX_ITEMS = 40


class BriefcaseError(ValueError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status, self.message = status, message


# --------------------------------------------------------------------------- #
# Reading what was handed over
# --------------------------------------------------------------------------- #

_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")

#: PDF text-showing operators. ``(...) Tj`` draws one string; ``[...] TJ``
#: draws a run of them with kerning numbers interleaved.
_PDF_STR = re.compile(rb"\((?:\\.|[^\\()])*\)", re.S)
_PDF_STREAM = re.compile(rb"stream\r?\n(.*?)endstream", re.S)

_PK_PARTS = {
    ".docx": ("word/document.xml",),
    ".pptx": ("ppt/slides/",),
    ".xlsx": ("xl/sharedStrings.xml",),
}


def _clean(text: str) -> str:
    return _WS.sub(" ", text).strip()[:MAX_TEXT]


def _pdf_text(data: bytes) -> str:
    """Whatever words a PDF carries as text, ignoring what it carries as
    pixels. A scan comes back empty on purpose — see ``read`` below."""
    chunks: list[bytes] = []
    for raw in _PDF_STREAM.findall(data):
        try:
            chunks.append(zlib.decompress(raw))
        except zlib.error:
            chunks.append(raw)          # uncompressed content stream
    if not chunks:
        chunks = [data]
    out: list[str] = []
    for chunk in b"\n".join(chunks).split(b"BT")[1:] or [b"".join(chunks)]:
        for match in _PDF_STR.findall(chunk):
            body = match[1:-1]
            body = re.sub(rb"\\([()\\])", rb"\1", body)
            body = re.sub(rb"\\[0-9]{1,3}", b" ", body)
            out.append(body.decode("latin-1", "replace"))
    return _clean(" ".join(out))


def _zip_text(data: bytes, ext: str) -> str:
    """The words inside an Office container, or — for a plain archive — the
    list of what is in it, which is the honest most we can say without
    unpacking somebody's zip."""
    try:
        archive = zipfile.ZipFile(BytesIO(data))
    except (zipfile.BadZipFile, OSError):
        return ""
    wanted = _PK_PARTS.get(ext)
    if wanted is None:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        listing = ", ".join(names[:60])
        return _clean(f"An archive of {len(names)} file(s): {listing}")
    parts: list[str] = []
    for name in archive.namelist():
        if not any(name.startswith(w) or name == w for w in wanted):
            continue
        try:
            xml = archive.read(name).decode("utf-8", "replace")
        except (KeyError, OSError):                      # pragma: no cover
            continue
        # Paragraph and cell boundaries are the only structure worth keeping;
        # everything else is markup between the words.
        xml = re.sub(r"</(w:p|a:p|si)>", " \n", xml)
        parts.append(_TAGS.sub(" ", xml))
    return _clean(" ".join(parts))


#: Audio containers, by their leading bytes — an MP3 (ID3-tagged or a bare
#: frame-sync), WAV, Ogg, FLAC. The `.m4a` voice memo is absent on purpose:
#: it opens with the same `ftyp` box an .mp4 does, sniffs as video, and the
#: video branch already hears it.
_AUDIO_MAGIC = (
    lambda b: b[:3] == b"ID3",
    lambda b: b[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"),
    lambda b: b[:4] == b"RIFF" and b[8:12] == b"WAVE",
    lambda b: b[:4] == b"OggS",
    lambda b: b[:4] == b"fLaC",
)


def _sounds_like_audio(data: bytes) -> bool:
    return any(test(data) for test in _AUDIO_MAGIC)


def read_file(data: bytes, name: str | None,
              on_behalf_of: str | None = None) -> tuple[str, str, bool]:
    """``(kind, text, read)`` for one upload.

    ``read`` is false when this deployment holds the bytes and cannot turn
    them into words — a photograph, a scanned PDF, a recording on a stack
    without ears. The item is still worth importing; the prompt block
    simply says so. With ears deployed a video reads as the words said in
    it, the same account a watched recording gets.
    """
    # A voice memo, by its own magic bytes — checked before `media._sniff`
    # because that reader refuses audio outright ("unrecognized file"),
    # and deliberately NOT added to the media store's own kinds: the wall
    # serves images and video a profile wears; a recording handed to a
    # pair belongs to the conversation, read here and never stored as a
    # file. RIFF is shared ground — WAVE is a recording, WEBP stays a
    # photograph — which is why the container's second name is checked.
    if _sounds_like_audio(data):
        heard = scrape.transcribe_bytes(data, on_behalf_of)
        if heard is not None:
            return "recording", _clean(heard["text"]), True
        return "recording", "", False
    kind, ext = media._sniff(data, name)
    if kind == "image":
        return "photo", "", False
    if kind == "video":
        # The ears turn a handed-over recording into the words said in it
        # (a voice memo's .m4a sniffs as video too — same ftyp box). No
        # ears keeps the old posture: held, said so, never invented. The
        # picture in the frames stays undescribed either way — these are
        # ears, not eyes.
        heard = scrape.transcribe_bytes(data, on_behalf_of)
        if heard is not None:
            return "video", _clean(heard["text"]), True
        return "video", "", False
    if data[:4] == b"%PDF":
        text = _pdf_text(data)
        return "document", text, len(text) >= 40
    if data[:4] == b"PK\x03\x04":
        text = _zip_text(data, ext)
        return "document", text, bool(text)
    text = _clean(data.decode("utf-8", "replace"))
    return "document", text, bool(text)


def read_link(url: str, on_behalf_of: str | None = None) -> tuple[str, bool, str | None]:
    """``(text, read, title)`` for a page, through the same offline gate and
    the same fetcher the collect connections use."""
    if offline.enabled():
        return "", False, None
    try:
        # A link that *is* a recording goes to the ears (qrme/scrape.py):
        # what comes back is the words said in it. Without ears the item
        # is held, not read — the same posture an uploaded video takes —
        # because the plain fetch below would decode compressed media as
        # mojibake and mark it read, which is worse than saying nothing.
        if scrape.is_recording(url):
            heard = scrape.fetch_transcribed(url, on_behalf_of)
            if heard is not None:
                return _clean(heard["text"]), True, None
            return "", False, None
        # The rendered reading first (qrme/scrape.py): the page as a person
        # meets it, so a JavaScript application stops carrying as a title
        # and a dozen characters. A deployment without eyes answers None
        # and the plain fetch stands in — the character count on the item's
        # state line is the honest witness to which reading this was.
        rendered = scrape.fetch_rendered(url, on_behalf_of)
        if rendered is not None:
            return _clean(rendered["text"]), True, rendered.get("title")
        page = scrape.extract(scrape.fetch(url, on_behalf_of))
    except offline.StoodDown:
        # Not a failure to reach the page — a decision not to. Reported the
        # same way here because this caller has no channel for the
        # difference; the route that owns the decision says so in words.
        return "", False, None
    except Exception:
        return "", False, None
    parts = [p for p in (page.get("description"), page.get("text")) if p]
    return _clean(" ".join(parts)), bool(parts), page.get("title") or None


# --------------------------------------------------------------------------- #
# Distilling it, once
# --------------------------------------------------------------------------- #

_DISTILL_SYSTEM = (
    "You are reducing a document someone handed to a synthetic profile they "
    "are talking to, so the profile can discuss it later without re-reading "
    "it. Write a compact briefing in plain prose: what this is, and the "
    "specific facts, names, numbers and claims a conversation about it would "
    "turn on. No preamble, no bullet characters, no commentary about the "
    "document's quality. Never invent anything the text does not say. Stay "
    f"under {MAX_DIGEST} characters."
)


def distill(text: str, title: str, provider=None) -> str:
    """The reading that every later turn carries.

    Paid for once. When there is nothing that can actually read it — no
    provider, the local fallback, a provider that errors — the head of the
    text stands in, which is the same shape of thing and costs nothing.

    The fallback is checked *after* the call as well as before it, because
    ``FallbackProvider`` degrades silently and the stub does not perform a
    character: it explains itself. Storing that explanation as a digest would
    put a sentence about the stub into the prompt under this document's
    title, and show the person "read once — 12,000 characters, carried as
    240" where the 240 are about our software rather than about their file.
    A truncation is a worse reading and an honest one.
    """
    text = (text or "").strip()
    if not text:
        return ""
    if len(text) <= MAX_DIGEST:
        return text
    head = text[:MAX_DIGEST].rstrip() + "…"
    if provider is None or isinstance(provider, llm.StubProvider):
        return head
    token = llm.clear_answered_by()
    try:
        out = provider.generate(
            _DISTILL_SYSTEM,
            [{"role": "user", "content": f"Title: {title}\n\n{text}"}])
        answered = llm.answered_by()
    except Exception:
        return head
    finally:
        llm.clear_answered_by(token)
    if answered and answered[0] == llm.LOCAL_FALLBACK:
        return head
    out = (out or "").strip()
    return out[:MAX_DIGEST] if out else head


# --------------------------------------------------------------------------- #
# The briefcase itself
# --------------------------------------------------------------------------- #

def _count(profile_id: str, interactor_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM briefcase_items"
        " WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id)).fetchone()["n"]


def add(profile_id: str, interactor_id: str, *, kind: str, title: str,
        text: str, read: bool, note: str | None = None,
        source: str | None = None, size: int | None = None,
        provider=None) -> dict:
    if kind not in KINDS:
        raise BriefcaseError(422, f"kind is one of {', '.join(KINDS)}")
    if _count(profile_id, interactor_id) >= MAX_ITEMS:
        raise BriefcaseError(
            422, f"this conversation already carries {MAX_ITEMS} imported "
                 "items — remove one before adding another")
    title = (title or "").strip()[:160] or "Untitled"
    note = (note or "").strip()[:400] or None
    digest = distill(text, title, provider) if read else ""
    item_id = db.new_id("brf")
    conn = db.connect()
    conn.execute(
        "INSERT INTO briefcase_items (id, profile_id, interactor_id, kind,"
        " title, note, source, text, digest, was_read, bytes, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (item_id, profile_id, interactor_id, kind, title, note, source,
         text or None, digest or None, 1 if read else 0, size, db.utcnow()))
    conn.commit()
    return facade(conn.execute("SELECT * FROM briefcase_items WHERE id=?",
                               (item_id,)).fetchone())


def facade(row) -> dict:
    """What a client sees. ``chars`` and ``digest_chars`` are shown on
    purpose: they are the person's own evidence that the long thing was read
    once and the short thing is what recurs."""
    text = row["text"] or ""
    digest = row["digest"] or ""
    return {"id": row["id"], "kind": row["kind"], "title": row["title"],
            "note": row["note"], "source": row["source"],
            "read": bool(row["was_read"]), "digest": digest,
            "chars": len(text), "digest_chars": len(digest),
            "bytes": row["bytes"], "created_at": row["created_at"]}


def items(profile_id: str, interactor_id: str, limit: int = 50) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM briefcase_items WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (profile_id, interactor_id, max(1, min(limit, MAX_ITEMS)))).fetchall()
    return [facade(r) for r in rows]


def get(profile_id: str, interactor_id: str, item_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM briefcase_items"
        " WHERE id=? AND profile_id=? AND interactor_id=?",
        (item_id, profile_id, interactor_id)).fetchone()
    return dict(row) if row else None


def remove(profile_id: str, interactor_id: str, item_id: str) -> bool:
    conn = db.connect()
    cur = conn.execute(
        "DELETE FROM briefcase_items"
        " WHERE id=? AND profile_id=? AND interactor_id=?",
        (item_id, profile_id, interactor_id))
    conn.commit()
    return cur.rowcount > 0


_URL_IN_TEXT = re.compile(r"https?://[^\s<>\"')]+")


def holds_link(profile_id: str, interactor_id: str, message: str) -> bool:
    """Whether a URL in this turn is already imported here.

    The chat route reads a pasted link inline; a link that was imported is
    the same page, already read and already carried as a digest. Without this
    the turn where you paste the link you have imported pays for the page
    twice — once inline at full length, once as its digest.
    """
    found = {u.rstrip("/.,") for u in _URL_IN_TEXT.findall(message or "")}
    if not found:
        return False
    rows = db.connect().execute(
        "SELECT source FROM briefcase_items"
        " WHERE profile_id=? AND interactor_id=? AND kind='link'",
        (profile_id, interactor_id)).fetchall()
    held = {(r["source"] or "").rstrip("/.,") for r in rows}
    return bool(found & held)


_LABELS = {"link": "a link", "photo": "a photograph", "video": "a video",
           "document": "a document", "recording": "a recording"}


def block(profile_id: str, interactor_id: str) -> str | None:
    """The prompt block, carried on every turn of this conversation.

    Digests only. The full text stays in the database for the person to read
    back; sending it to the model on every turn is exactly the cost this
    module exists to remove.
    """
    rows = db.connect().execute(
        "SELECT * FROM briefcase_items WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (profile_id, interactor_id, PROMPT_ITEMS)).fetchall()
    if not rows:
        return None
    lines: list[str] = []
    unread: list[str] = []
    for row in rows:
        label = _LABELS.get(row["kind"], row["kind"])
        head = f"- {row['title']} ({label})"
        if row["source"]:
            head += f" — {row['source']}"
        if row["was_read"] and row["digest"]:
            body = row["digest"]
            if row["note"]:
                body = f"They said: {row['note']}. {body}"
            lines.append(f"{head}\n  {body}")
        else:
            said = f" They said it is: {row['note']}." if row["note"] else ""
            unread.append(f"{head} — you have NOT seen its contents.{said}")
    parts = ["This person has handed you material to read, and you have read "
             "it. Draw on it naturally when it is relevant; never invent "
             "details it does not carry, and say plainly when it does not "
             "answer what they asked."]
    if lines:
        parts.append("\n".join(lines))
    if unread:
        parts.append(
            "They also handed you these, which you could not open:\n"
            + "\n".join(unread)
            + "\nDo not describe or summarise anything in this second list. "
              "You may ask them what it contains, or ask them to paste the "
              "part that matters.")
    return "\n\n".join(parts)
