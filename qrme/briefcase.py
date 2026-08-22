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

import base64
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

_PK_PARTS = {
    ".docx": ("word/document.xml",),
    ".pptx": ("ppt/slides/",),
    ".xlsx": ("xl/sharedStrings.xml",),
}


def _clean(text: str) -> str:
    return _WS.sub(" ", text).strip()[:MAX_TEXT]


#: Stream filters this reader knows how to undo. Anything outside this set —
#: an image codec, or a filter nobody has written here yet — leaves the stream
#: where it is, and :func:`_reads_like_language` below is what stops the
#: leftovers being served to a profile as though they were the document.
_TEXT_FILTERS = {
    b"FlateDecode", b"Fl", b"ASCII85Decode", b"A85", b"ASCIIHexDecode",
    b"AHx", b"LZWDecode", b"LZW", b"RunLengthDecode", b"RL",
}

#: A stream and, ahead of it, the dictionary that says how it is encoded.
_PDF_STREAM = re.compile(rb"stream\r?\n(.*?)endstream", re.S)
_FILTER = re.compile(rb"/Filter\s*(\[[^\]]*\]|/[A-Za-z0-9]+)")
_FILTER_NAME = re.compile(rb"/([A-Za-z0-9]+)")

#: PDF text-showing strings. ``(...)`` is a literal string; ``<...>`` is the
#: same thing written in hex, which the previous reader did not match at all —
#: so every generator that prefers hex (most of them, for anything but plain
#: ASCII) produced a document that came back empty.
_PDF_STR = re.compile(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>", re.S)


def _unfilter(body: bytes, spec: bytes | None) -> bytes | None:
    """Undo a stream's filter chain, or ``None`` if this reader cannot.

    ``None`` is a real answer and the important one. The previous version had
    no concept of it: a stream it could not inflate was appended **still
    encoded**, and the text scanner then matched parentheses inside compressed
    bytes. That is where the byte soup came from.
    """
    if spec is None:
        return body
    for name in _FILTER_NAME.findall(spec):
        if name not in _TEXT_FILTERS:
            return None                     # an image, or a filter we lack
        try:
            if name in (b"FlateDecode", b"Fl"):
                body = zlib.decompress(body)
            elif name in (b"ASCII85Decode", b"A85"):
                body = _a85(body)
            elif name in (b"ASCIIHexDecode", b"AHx"):
                body = _ahx(body)
            elif name in (b"LZWDecode", b"LZW"):
                body = _lzw(body)
            else:
                body = _runlength(body)
        except Exception:
            return None
    return body


def _a85(body: bytes) -> bytes:
    """ASCII85, with Adobe's framing optional — real files vary on whether the
    leading ``<~`` is written, and every one of them ends with ``~>``."""
    text = b"".join(body.split())
    if text.startswith(b"<~"):
        text = text[2:]
    end = text.find(b"~>")
    if end >= 0:
        text = text[:end]
    return base64.a85decode(text, adobe=False)


def _ahx(body: bytes) -> bytes:
    text = b"".join(body.split())
    end = text.find(b">")
    if end >= 0:
        text = text[:end]
    if len(text) % 2:
        text += b"0"                        # the spec pads an odd tail
    return bytes.fromhex(text.decode("ascii"))


def _runlength(body: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i < len(body):
        n = body[i]
        if n == 128:
            break
        if n < 128:
            out += body[i + 1:i + 2 + n]
            i += 2 + n
        else:
            out += body[i + 1:i + 2] * (257 - n)
            i += 2
    return bytes(out)


def _lzw(body: bytes) -> bytes:
    """LZW as PDF writes it: 8-bit input, codes 9..12 bits, early change."""
    out = bytearray()
    table: list[bytes] = [bytes([i]) for i in range(256)] + [b"", b""]
    width, prev = 9, None
    buf = bits = 0
    for byte in body:
        buf = (buf << 8) | byte
        bits += 8
        while bits >= width:
            code = (buf >> (bits - width)) & ((1 << width) - 1)
            bits -= width
            if code == 256:                 # clear
                table = [bytes([i]) for i in range(256)] + [b"", b""]
                width, prev = 9, None
                continue
            if code == 257:                 # end of data
                return bytes(out)
            if prev is None:
                entry = table[code]
            elif code < len(table):
                entry = table[code]
                table.append(prev + entry[:1])
            else:
                entry = prev + prev[:1]
                table.append(entry)
            out += entry
            prev = entry
            if len(table) + 1 >= (1 << width) and width < 12:
                width += 1                  # early change
    return bytes(out)


def _string_text(raw: bytes) -> str:
    """One text-showing string's bytes as characters.

    Two-byte encodings are tried first where the bytes look like one. A
    composite font writing UTF-16 reads correctly this way; a subset font
    writing raw glyph ids does not read at all, in any encoding, without the
    font's own map — and that is what the readability gate is for.
    """
    if len(raw) >= 4 and not len(raw) % 2:
        zeros = sum(1 for i in range(0, len(raw), 2) if raw[i] == 0)
        if zeros >= len(raw) // 4:
            try:
                return raw.decode("utf-16-be")
            except UnicodeDecodeError:
                pass
    return raw.decode("latin-1", "replace")


def _pdf_text(data: bytes) -> str:
    """Whatever words a PDF carries as text, ignoring what it carries as
    pixels, and **nothing at all** when what came out is not language.

    A field report, three times: *"the synthetic profile can't read documents
    still"*, with a transcript of the profile saying the filings *"came
    through as garbage on my end — byte soup rather than claims"*. The profile
    was right and was reporting honestly. It had been handed 1,818 characters
    of mojibake and told that was the document.

        asked     did any text come out of the PDF
        mattered  is it text

    The old reader inflated what it could, appended what it could not **still
    encoded**, scanned for parentheses across both, and declared the result
    read if it ran past forty characters. Forty characters is a length, and
    garbage is long. So the one case the module's own header promises to
    handle honestly — *a PDF that carries only scanned pixels has no text in
    it to find* — was the one case it did not reach, because unreadable bytes
    never came back empty. They came back as a paragraph.
    """
    chunks: list[bytes] = []
    for match in _PDF_STREAM.finditer(data):
        head = data[max(0, match.start() - 800):match.start()]
        spec = _FILTER.findall(head)
        body = _unfilter(match.group(1), spec[-1] if spec else None)
        if body is not None:
            chunks.append(body)
    if not chunks:
        chunks = [data]
    out: list[str] = []
    for chunk in b"\n".join(chunks).split(b"BT")[1:] or [b"".join(chunks)]:
        for match in _PDF_STR.findall(chunk):
            if match[:1] == b"<":
                try:
                    body = _ahx(match[1:])
                except ValueError:
                    continue
            else:
                body = match[1:-1]
                body = re.sub(rb"\\([()\\])", rb"\1", body)
                body = re.sub(rb"\\[0-9]{1,3}", b" ", body)
            out.append(_string_text(body))
    text = _clean(" ".join(out))
    return text if _reads_like_language(text) else ""


#: How much of an extraction has to look like writing before it counts as
#: having been read. Deliberately generous: a filing is full of numbers,
#: citations and reference signs, and this is a floor against byte soup, not a
#: taste test.
_WORDISH = re.compile(r"[^\W\d_]{2,}")


def _reads_like_language(text: str) -> bool:
    """Whether an extraction is writing or wreckage.

    The gate the reader never had. Everything upstream of it is best-effort —
    filters this module implements, encodings it guesses at — and best-effort
    is fine as long as the failures come back as failures. A profile that is
    told plainly *this was held but could not be read* asks what is in it. A
    profile handed mojibake describes the mojibake.
    """
    if len(text) < 40:
        return False
    letters = [ch for ch in text if ch.isalpha()]
    if len(letters) < len(text) * 0.5:
        return False
    # Scripts written without spaces (Chinese, Japanese) have no words to
    # count, so the letter share is the whole test for them.
    if sum(1 for ch in letters if ch.isascii()) < len(letters) * 0.5:
        return True
    # Writing is spaced. Prose of any language that uses spaces breaks every
    # few characters; an encoding runs on. A base64 blob is all letters and
    # would pass every other test here on its way to a profile.
    tokens = text.split()
    if not tokens or len(text) / len(tokens) > 18:
        return False
    # The share of the text standing inside ordinary word-shaped runs. Byte
    # soup has letters everywhere and words almost nowhere: its runs are one
    # or two characters long, broken up by punctuation that means nothing.
    return sum(len(w) for w in _WORDISH.findall(text)) >= len(text) * 0.45


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
        # Empty is the honest answer for a scan, and now also for a PDF this
        # reader could open but not turn into words — see `_pdf_text`.
        text = _pdf_text(data)
        return "document", text, bool(text)
    if data[:4] == b"PK\x03\x04":
        text = _zip_text(data, ext)
        return "document", text, bool(text)
    # Whatever is left is treated as plain text, and most of the time it is.
    # But `errors="replace"` never fails, so a format nobody sniffed — an old
    # binary .doc, an .rtf, a database file somebody dragged in — decoded into
    # replacement characters and was handed over as though it were writing.
    # The same gate the PDF reader uses answers it here: held, and said so.
    text = _clean(data.decode("utf-8", "replace"))
    # Short enough and there is nothing to judge — "Meet me at 4" is a note,
    # not wreckage, and a gate that called it unread would be the new bug.
    return "document", text, bool(text) and (len(text) < 40
                                             or _reads_like_language(text))


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
