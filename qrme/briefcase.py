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

And it says **which** kind of failure, because three of them wore one
sentence: a scan needs somebody's eyes, a locked file needs its password, and
a font this reader cannot follow is a gap in this code rather than a limit of
the format. Told only "could not open it", nobody could tell a limit from a
bug without opening the file by hand — which is a large part of why the same
report arrived four times.

The reason is stored as a **key**, never as a sentence. The prompt block is
written in English and the console is written in ten languages, and there is
no way back from a sentence to the fact it states.

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

from . import common, db, i18n, llm, media, offline, scrape

#: Kinds a person can hand over. ``photo`` and ``video`` are stored for what
#: the person says about them; the rest carry text this deployment can read.
KINDS = ("link", "photo", "video", "document", "recording")

#: How much extracted text is kept per item.
#:
#: This said *generous for a filing*, and it was not. A US patent application
#: runs to forty thousand characters and often past a hundred thousand; at
#: 20,000 the product read the first third of the documents it was mostly
#: being handed, and the round that made the truncation visible is what made
#: that legible rather than arguable — "the first 20,000 of 70,000" is a
#: sentence about a number that was chosen when nobody had measured one.
#:
#: 120,000 holds a long filing whole. What it costs is stated rather than
#: hidden: `distill` sends the stored text to the model once per import, so
#: a document six times longer is six times the reading — ONCE, and never
#: again, because the digest is what every later turn carries and that is
#: still capped at `MAX_DIGEST`. That is the module's whole economy working
#: as described rather than an exception to it.
#:
#: Still a cap, and the notice still fires past it: a briefcase is not an
#: archive, and something longer than this exists.
MAX_TEXT = 120_000

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


#: Control characters that are not whitespace. A glyph map can hand back a
#: NUL for an unmapped slot and a broken decode can hand back worse; neither
#: is writing, and both count toward length in the readability gate below
#: while reading as nothing at all on screen.
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _clean(text: str) -> str:
    """Tidy and CAP — two different things happening on one line.

    The cap is real and wanted: a briefcase is not an archive. What it was
    not was visible. A 70,000-character filing became 20,000 characters, the
    item said `read`, and the count shown beside it was the KEPT length
    rather than the document's — so nothing anywhere said that two thirds of
    it had gone. Asked about claim 14, a profile holding the first third
    answers from material it never saw.

        asked     did the document read
        mattered  how much of it did

    `full_length` is what a caller uses to say so, kept separate rather than
    returned alongside because `_clean` has nine callers and only the
    document ones have anywhere to put the number.
    """
    return _WS.sub(" ", _CONTROL.sub(" ", text)).strip()


def capped(text: str) -> str:
    """The tidied text, cut to what a briefcase keeps.

    The cap lives HERE and not inside `_clean` because the two callers that
    store a document are the only ones that can record what the cut cost.
    Capping inside the cleaner meant every reader had already thrown the
    number away before anybody could ask for it — which is why the loss was
    silent for as long as it was.
    """
    return text[:MAX_TEXT]


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


# --------------------------------------------------------------------------- #
# The font's own map
# --------------------------------------------------------------------------- #
#
# A fourth field report, with two USPTO filings held and unread. The gate
# below was doing its job — it refused to serve wreckage as a document — but
# refusing honestly is not reading, and `_string_text` already named the
# reason in its own docstring: *a subset font writing raw glyph ids does not
# read at all, in any encoding, without the font's own map*.
#
#     asked     can these bytes be decoded as characters
#     mattered  whose characters are they
#
# They are the font's. A composite font with `/Encoding /Identity-H` — which
# is what every generator reaches for the moment a document is not plain
# ASCII, and what a filing full of section signs and accented inventor names
# always is — writes GLYPH NUMBERS in its own subset, not Unicode. Glyph 3 is
# whatever the third glyph of that particular subset happens to be. There is
# no encoding under which those bytes are language, and the reader was right
# that they were not; it was simply reading the wrong thing.
#
# `/ToUnicode` is the map back, and PDFs that use these fonts carry it,
# because it is what makes them searchable and copy-pasteable. Following it is
# the difference between a filing that arrives as words and one that arrives
# as a filename.

_OBJ = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj", re.S)
_TOUNICODE = re.compile(rb"/ToUnicode\s+(\d+)\s+\d+\s+R")
_FONT_RES = re.compile(rb"/Font\s*<<(.*?)>>", re.S)
_FONT_REF = re.compile(rb"/([A-Za-z0-9#]+)\s+(\d+)\s+\d+\s+R")
_BFCHAR = re.compile(rb"beginbfchar(.*?)endbfchar", re.S)
_BFRANGE = re.compile(rb"beginbfrange(.*?)endbfrange", re.S)
_HEXTOK = re.compile(rb"<([0-9A-Fa-f\s]*)>")
_CODESPACE = re.compile(rb"begincodespacerange(.*?)endcodespacerange", re.S)
#: `/F1 12 Tf` — which font the strings after it are written in.
_TF = re.compile(rb"/([A-Za-z0-9#]+)\s+[-\d.]+\s+Tf")


#: Glyph names a `/Differences` array can hand back, to the character each
#: one is. Not the whole Adobe glyph list — that is four thousand entries and
#: most of a filing is ASCII — but every name a Western document actually
#: reaches for, which is the punctuation and the accents. Anything outside it
#: is handled by the `uniXXXX` and `gNN` conventions below, and anything
#: outside THOSE is left alone rather than guessed at.
_GLYPH_NAMES = {
    "space": " ", "exclam": "!", "quotedbl": '"', "numbersign": "#",
    "dollar": "$", "percent": "%", "ampersand": "&", "quotesingle": "'",
    "parenleft": "(", "parenright": ")", "asterisk": "*", "plus": "+",
    "comma": ",", "hyphen": "-", "period": ".", "slash": "/",
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "colon": ":", "semicolon": ";", "less": "<", "equal": "=",
    "greater": ">", "question": "?", "at": "@", "bracketleft": "[",
    "backslash": "\\", "bracketright": "]", "asciicircum": "^",
    "underscore": "_", "grave": "`", "braceleft": "{", "bar": "|",
    "braceright": "}", "asciitilde": "~",
    # The ones a filing is actually full of.
    "section": "\u00a7", "paragraph": "\u00b6", "degree": "\u00b0",
    "plusminus": "\u00b1", "copyright": "\u00a9", "registered": "\u00ae",
    "trademark": "\u2122", "bullet": "\u2022", "endash": "\u2013",
    "emdash": "\u2014", "quoteleft": "\u2018", "quoteright": "\u2019",
    "quotedblleft": "\u201c", "quotedblright": "\u201d",
    "ellipsis": "\u2026", "dagger": "\u2020", "daggerdbl": "\u2021",
    "fi": "fi", "fl": "fl", "ff": "ff", "ffi": "ffi", "ffl": "ffl",
    "minus": "\u2212", "multiply": "\u00d7", "divide": "\u00f7",
    "mu": "\u00b5", "sterling": "\u00a3", "yen": "\u00a5",
    "euro": "\u20ac", "cent": "\u00a2", "currency": "\u00a4",
    "onehalf": "\u00bd", "onequarter": "\u00bc", "threequarters": "\u00be",
    "guillemotleft": "\u00ab", "guillemotright": "\u00bb",
    "quotesinglbase": "\u201a", "quotedblbase": "\u201e",
    "fraction": "\u2044", "perthousand": "\u2030",
}
#: Accented letters, built rather than listed: the names are regular.
for _base, _ch in (("A", "A"), ("E", "E"), ("I", "I"), ("O", "O"),
                   ("U", "U"), ("a", "a"), ("e", "e"), ("i", "i"),
                   ("o", "o"), ("u", "u"), ("y", "y"), ("n", "n"),
                   ("N", "N"), ("c", "c"), ("C", "C")):
    for _mark, _combining in (("acute", "\u0301"), ("grave", "\u0300"),
                              ("circumflex", "\u0302"), ("tilde", "\u0303"),
                              ("dieresis", "\u0308"), ("cedilla", "\u0327"),
                              ("ring", "\u030a"), ("caron", "\u030c")):
        import unicodedata as _ud
        _GLYPH_NAMES.setdefault(
            _base + _mark, _ud.normalize("NFC", _ch + _combining))
del _base, _ch, _mark, _combining

_DIFFERENCES = re.compile(rb"/Differences\s*\[(.*?)\]", re.S)
_DIFF_TOKEN = re.compile(rb"(\d+)|/([A-Za-z0-9._]+)")
_UNI_NAME = re.compile(r"^uni([0-9A-Fa-f]{4,6})$")


def _glyph_char(name: str) -> str | None:
    """One glyph name as the character it stands for, or `None`.

    `None` matters: a name this does not know is left for the readability
    gate to judge rather than replaced with a plausible letter. A document
    rendered in *nearly* the right characters is worse than one that comes
    back empty — the empty one gets reported, and the nearly-right one gets
    believed.
    """
    got = _GLYPH_NAMES.get(name)
    if got is not None:
        return got
    if len(name) == 1:
        return name
    hexed = _UNI_NAME.match(name)
    if hexed:
        try:
            return chr(int(hexed.group(1), 16))
        except (ValueError, OverflowError):
            return None
    return None


def _differences_map(font: bytes) -> _Cmap | None:
    """A simple font's `/Differences` array as a one-byte map.

    The other half of the same problem `/ToUnicode` solves, and the more
    dangerous half. A composite font writing glyph ids produces bytes that
    are obviously not language, so the gate catches them and the item is
    reported unread. A simple font with a re-arranged encoding produces
    bytes that ARE letters — the wrong ones. `[169 /section]` means byte 169
    is a section sign; read as Latin-1 it is `©`. That passes every
    readability test there is and arrives as a document somebody trusts.
    """
    array = _DIFFERENCES.search(font)
    if array is None:
        return None
    table: dict[int, str] = {}
    code = 0
    for number, name in _DIFF_TOKEN.findall(array.group(1)):
        if number:
            code = int(number)
            continue
        char = _glyph_char(name.decode("latin-1"))
        if char is not None:
            table[code] = char
        code += 1
    return _Cmap(1, table, over_base=True) if table else None


class _Cmap:
    """One font's `/ToUnicode`: glyph code in, characters out.

    `width` is how many bytes make one code, taken from the CMap's own
    codespace range and falling back to the width the mappings are written
    at. It has to be read rather than assumed: a two-byte map applied a byte
    at a time turns a document into twice as many wrong characters, which
    reads as wreckage exactly like the problem it was meant to fix.
    """

    __slots__ = ("width", "table", "over_base")

    def __init__(self, width: int, table: dict[int, str],
                 over_base: bool = False):
        self.width = width
        self.table = table
        #: Whether unlisted codes mean their ordinary character or mean
        #: nothing. A `/ToUnicode` CMap is the WHOLE map — a code it does not
        #: carry is a code this reader cannot read. A `/Differences` array is
        #: a patch on the standard encoding and lists only what CHANGED, so
        #: its unlisted codes are ordinary Latin-1 and always were. Reading
        #: the second like the first turns a page into two mapped characters
        #: and fifty spaces, which is a map that then declines to be used.
        self.over_base = over_base

    def decode(self, raw: bytes) -> str | None:
        """The string as characters, or `None` when this map does not cover
        it — an unmapped run is not something to paper over with a
        replacement character, because a page of those still passes for
        length and never for language."""
        out: list[str] = []
        hit = 0
        for i in range(0, len(raw) - self.width + 1, self.width):
            chunk = raw[i:i + self.width]
            code = int.from_bytes(chunk, "big")
            got = self.table.get(code)
            if got is not None:
                out.append(got)
                hit += 1
            elif self.over_base:
                out.append(chunk.decode("latin-1", "replace"))
                hit += 1
            else:
                out.append(" ")
        if not out or hit < len(out) * 0.6:
            return None
        return "".join(out)


def _hex_chars(token: bytes) -> str:
    """A `<...>` destination, which is UTF-16BE and may be several
    characters — a ligature maps one glyph onto `fi`."""
    text = b"".join(token.split())
    if len(text) % 2:
        text += b"0"
    try:
        return bytes.fromhex(text.decode("ascii")).decode("utf-16-be", "ignore")
    except ValueError:
        return ""


def _parse_cmap(body: bytes) -> _Cmap | None:
    """A `/ToUnicode` CMap, as far as this reader follows it.

    `bfchar` maps one code; `bfrange` maps a run, either onto a run of
    characters or onto an explicit array of them. Both forms appear in
    ordinary files, and a reader that handles only the first loses most of
    the alphabet from the second.
    """
    table: dict[int, str] = {}
    width = 0
    space = _CODESPACE.search(body)
    if space:
        first = _HEXTOK.search(space.group(1))
        if first:
            width = max(1, len(b"".join(first.group(1).split())) // 2)
    for block in _BFCHAR.findall(body):
        tokens = _HEXTOK.findall(block)
        for i in range(0, len(tokens) - 1, 2):
            src = b"".join(tokens[i].split())
            if not width:
                width = max(1, len(src) // 2)
            try:
                code = int(src, 16)
            except ValueError:
                continue
            char = _hex_chars(tokens[i + 1])
            if char:
                table[code] = char
    for block in _BFRANGE.findall(body):
        # In token order, not by line. CMaps are written by machines and
        # machines disagree about lines: \r-only endings, several ranges to
        # a line, a whole minified map on one. The first version split on
        # \n and read one range per "line" — which on a one-line map meant
        # the first range and none after it, an alphabet lost silently and
        # reported as this reader's own "unmapped". The grammar itself is
        # unambiguous without the lines: two hex tokens then a destination
        # (a third hex token, or an array), repeated.
        items: list[tuple[bytes, bytes]] = [
            (b"arr", m.group(2)) if m.group(2) is not None
            else (b"hex", m.group(1))
            for m in re.finditer(rb"<([0-9A-Fa-f\s]*)>|\[(.*?)\]", block, re.S)
        ]
        i = 0
        while i + 2 < len(items):
            src_lo, src_hi, dest = items[i], items[i + 1], items[i + 2]
            if src_lo[0] != b"hex" or src_hi[0] != b"hex":
                i += 1
                continue
            try:
                lo = int(b"".join(src_lo[1].split()), 16)
                hi = int(b"".join(src_hi[1].split()), 16)
            except ValueError:
                i += 1
                continue
            if not width:
                width = max(1, len(b"".join(src_lo[1].split())) // 2)
            if hi < lo or hi - lo > 65535:
                i += 3
                continue
            if dest[0] == b"arr":
                for offset, token in enumerate(_HEXTOK.findall(dest[1])):
                    char = _hex_chars(token)
                    if char:
                        table[lo + offset] = char
            else:
                start = _hex_chars(dest[1])
                if start:
                    base = ord(start[-1])
                    head = start[:-1]
                    for offset in range(hi - lo + 1):
                        if base + offset > 0x10FFFF:
                            break
                        table[lo + offset] = head + chr(base + offset)
            i += 3
    if not table:
        return None
    return _Cmap(width or 2, table)


def _objects(data: bytes) -> dict[int, bytes]:
    """Every indirect object's body, including the ones packed inside object
    streams.

    A PDF written to any recent version keeps most of its dictionaries — font
    dictionaries among them — inside a compressed `/Type /ObjStm`, where a
    scan of the file's own bytes cannot see them. Skipping that step finds the
    content streams and none of the fonts, which is a reader that knows there
    is a map and cannot reach it.
    """
    found: dict[int, bytes] = {}
    for num, _gen, body in _OBJ.findall(data):
        try:
            found.setdefault(int(num), body)
        except ValueError:
            continue
    for body in list(found.values()):
        if b"/ObjStm" not in body:
            continue
        stream = _PDF_STREAM.search(body)
        if stream is None:
            continue
        spec = _FILTER.findall(body[:stream.start()])
        plain = _unfilter(stream.group(1), spec[-1] if spec else None)
        if plain is None:
            continue
        first = re.search(rb"/First\s+(\d+)", body)
        count = re.search(rb"/N\s+(\d+)", body)
        if not (first and count):
            continue
        start = int(first.group(1))
        pairs = plain[:start].split()
        for i in range(0, min(len(pairs) - 1, int(count.group(1)) * 2), 2):
            try:
                num, offset = int(pairs[i]), int(pairs[i + 1])
            except ValueError:
                continue
            found.setdefault(num, plain[start + offset:start + offset + 4096])
    return found


def _font_maps(data: bytes) -> dict[str, _Cmap]:
    """Resource name — `/F1`, `/TT2` — to the map its font carries.

    Keyed on the name rather than on the page, because a content stream names
    its font and nothing else, and following the name back through each
    page's own resource dictionary buys accuracy this reader has no use for:
    the fonts in one document are one document's fonts.
    """
    objects = _objects(data)
    maps: dict[str, _Cmap] = {}
    for body in objects.values():
        for res in _FONT_RES.findall(body):
            for name, ref in _FONT_REF.findall(res):
                font = objects.get(int(ref))
                if font is None:
                    continue
                cmap = None
                to_unicode = _TOUNICODE.search(font)
                if to_unicode is not None:
                    holder = objects.get(int(to_unicode.group(1)))
                    stream = (_PDF_STREAM.search(holder)
                              if holder is not None else None)
                    if stream is not None:
                        spec = _FILTER.findall(holder[:stream.start()])
                        plain = _unfilter(stream.group(1),
                                          spec[-1] if spec else None)
                        if plain is not None:
                            cmap = _parse_cmap(plain)
                if cmap is None:
                    # `/ToUnicode` first, because it is the font's own answer
                    # to this exact question. `/Differences` is a rendering
                    # instruction that happens to imply one, and a font that
                    # carries both means the first.
                    cmap = _differences_map(font)
                if cmap is not None:
                    maps.setdefault(name.decode("latin-1"), cmap)
    return maps


_PAGE = re.compile(rb"/Type\s*/Page\b")
_CONTENTS = re.compile(rb"/Contents\s*(\[[^\]]*\]|\d+\s+\d+\s+R)")
_REF = re.compile(rb"(\d+)\s+\d+\s+R")
#: A stream that is a font's map rather than a page's words.
_IS_CMAP = re.compile(rb"begincmap|beginbfchar|beginbfrange|/CIDInit")


def _page_streams(data: bytes) -> list[bytes] | None:
    """The decoded content streams of the document's pages, in page order,
    or `None` when the structure could not be followed.

    Scanning every stream in the file instead is what the reader did, and it
    is wrong in a way that only showed once the glyph maps started working:
    a `/ToUnicode` CMap **is** a stream, full of `<0041>` tokens that look
    exactly like hex strings, so the map got read as though it were the page
    and every mapped letter arrived twice. It was there before and passed as
    NULs; decoding the fonts is what turned it into visible nonsense.

        asked     which streams have text in them
        mattered  which streams are the PAGE

    `None` rather than an empty list when there are no pages to follow, so
    the caller falls back to the old sweep — a file this cannot parse is
    better read loosely than not at all.
    """
    objects = _objects(data)
    refs: list[int] = []
    for body in objects.values():
        if not _PAGE.search(body) or b"/Pages" in body[:40]:
            continue
        found = _CONTENTS.search(body)
        if found:
            refs.extend(int(n) for n in _REF.findall(found.group(1)))
    if not refs:
        return None
    out: list[bytes] = []
    for ref in refs:
        holder = objects.get(ref)
        if holder is None:
            continue
        stream = _PDF_STREAM.search(holder)
        if stream is None:
            continue
        spec = _FILTER.findall(holder[:stream.start()])
        plain = _unfilter(stream.group(1), spec[-1] if spec else None)
        if plain is not None:
            out.append(plain)
    return out or None


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


#: Why a PDF came back with nothing, in words a person can act on.
#:
#: Three failures wear the same face — "held, not read" — and want three
#: different answers. A scan needs somebody's eyes or an OCR pass; a font this
#: reader cannot follow is a gap in this code; a locked file needs the
#: password. Reporting them as one sentence is what made the same field report
#: arrive four times: nothing in the answer distinguished "there is no text in
#: this file" from "there is text and I failed at it", so there was no way to
#: tell a limit from a bug without opening the file by hand.
_PDF_WHY = {
    "locked": "it is password-protected, so nothing inside it can be opened",
    "scanned": "it is a scan — pictures of pages, with no text layer in it "
               "at all, so there are no words in the file to read",
    "unmapped": "its text is written in embedded fonts whose character map "
                "this reader could not follow",
    "empty": "no text came out of it",
}


def _why_unread(data: bytes) -> str:
    """Which kind of unreadable a PDF is.

    Read off the file's own structure rather than guessed from the emptiness:
    a locked file says so in its trailer, a scan has pages and no text-showing
    operators in them, and a file with `Tj` operators that still yields
    nothing had text this reader could not decode.
    """
    if re.search(rb"/Encrypt\b", data):
        return "locked"
    chunks = _page_streams(data) or []
    if not chunks:
        return "empty"
    joined = b"\n".join(chunks)
    if not re.search(rb"\bT[Jj]\b|\bBT\b", joined):
        return "scanned"
    return "unmapped"


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
    chunks = _page_streams(data)
    if chunks is None:
        chunks = []
        for match in _PDF_STREAM.finditer(data):
            head = data[max(0, match.start() - 800):match.start()]
            spec = _FILTER.findall(head)
            body = _unfilter(match.group(1), spec[-1] if spec else None)
            # A font's map is not a page. Cheap to spot by its own opening
            # words, and the loose sweep is exactly where that mistake used
            # to be made, so the guard belongs here too.
            if body is not None and not _IS_CMAP.search(body[:4096]):
                chunks.append(body)
        if not chunks:
            chunks = [data]
    fonts = _font_maps(data)
    out: list[str] = []
    for chunk in b"\n".join(chunks).split(b"BT")[1:] or [b"".join(chunks)]:
        # The font in force, carried across the pieces of one text object.
        # A `Tf` inside the block switches it; the block inherits whatever
        # the page set before `BT`, which is why the search runs from the
        # start of the chunk rather than only over what follows.
        cmap = None
        for token in re.finditer(
                rb"/[A-Za-z0-9#]+\s+[-\d.]+\s+Tf|\((?:\\.|[^\\()])*\)"
                rb"|<[0-9A-Fa-f\s]*>", chunk, re.S):
            match = token.group(0)
            if match.endswith(b"Tf"):
                named = _TF.match(match)
                if named:
                    cmap = fonts.get(named.group(1).decode("latin-1"))
                continue
            if match[:1] == b"<":
                try:
                    body = _ahx(match[1:])
                except ValueError:
                    continue
            else:
                body = match[1:-1]
                body = re.sub(rb"\\([()\\])", rb"\1", body)
                body = re.sub(rb"\\[0-9]{1,3}", b" ", body)
            # The font's own map first, and only where it actually covers the
            # bytes. A map that misses most of a string is a different font's
            # map, or a code width read wrong, and guessing there would trade
            # honest wreckage for confident nonsense.
            mapped = cmap.decode(body) if cmap is not None else None
            out.append(mapped if mapped is not None else _string_text(body))
    text = _clean(" ".join(out))
    return text if _reads_like_language(text) else ""


#: How many pages the eyes look at. A cap because OCR is the expensive way
#: to read and a scan can be four hundred pages; what a profile needs to
#: DISCUSS a document lives overwhelmingly in its front matter, and the
#: prompt block caps what it hands over anyway.
_OCR_PAGES = 12


def _ocr_text(data: bytes) -> str:
    """The words drawn on a PDF's pages, read with actual eyes.

    The route around both refusals the text reader gives honestly. A scan
    has no text layer; a subset font without a followable map hides its
    text behind glyph ids. In both files the words are nonetheless DRAWN
    on the page, where an OCR pass reads them the way a person would —
    the owner's two filings, refused as "scanned" and "unmapped" in the
    same afternoon, are one problem from this side of the glass.

    System tools, feature-detected: poppler's `pdftoppm` rasterises and
    `tesseract` reads, both reached as subprocesses so this stays a
    stack with no new Python dependencies — the same bargain the ears
    struck. A deployment without them keeps today's honest refusal
    (this function answering "" IS that refusal); the docker image
    installs both, so the beta has eyes even where a dev checkout does
    not.

    Gated by the same language gate as everything upstream of it. OCR of
    a blurry page is noise, and the gate is what keeps best-effort
    honest: a failure must come back as a failure, never as a paragraph.
    """
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    if not (shutil.which("pdftoppm") and shutil.which("tesseract")):
        return ""
    with tempfile.TemporaryDirectory(prefix="qrme-eyes-") as work:
        held = Path(work) / "held.pdf"
        held.write_bytes(data)
        try:
            subprocess.run(
                # 150 dpi, down from 200: print-size glyphs OCR fine at
                # 150, and half the pixels is roughly half the time per
                # page — the field report on the first live pass was "why
                # are they taking so long?", from a person sharing four
                # scans in a row. The language gate keeps the honesty
                # whatever the resolution.
                ["pdftoppm", "-r", "150", "-gray", "-png",
                 "-f", "1", "-l", str(_OCR_PAGES),
                 str(held), str(Path(work) / "page")],
                capture_output=True, timeout=120, check=True)
        except Exception:
            return ""            # not a PDF poppler can open; nothing read
        seen: list[str] = []
        for page in sorted(Path(work).glob("page*.png")):
            try:
                got = subprocess.run(
                    ["tesseract", str(page), "stdout"],
                    capture_output=True, timeout=60, check=True)
            except Exception:
                continue         # one bad page does not unread the rest
            seen.append(got.stdout.decode("utf-8", "replace"))
    text = _clean(" ".join(seen))
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


def why_unread(data: bytes, kind: str, was_read: bool) -> str | None:
    """Which kind of unreadable an item is, as a KEY — 'scanned', 'locked',
    'unmapped' — never as a sentence.

    A key because the two readers of this want different words for the same
    fact. The prompt block is written in English and hands the model
    `_PDF_WHY`; the console is written in ten languages and looks the same
    fact up in its own. Storing the English sentence would have given a
    Japanese-speaking person an English diagnosis under a Japanese heading,
    and there is no way back from a sentence to the fact it states.

    Only PDFs get one. A photograph and a video are not failures of this
    reader — this deployment has ears and no eyes, which the prompt block
    already says in its own words — and dressing them up as diagnoses would
    bury the one case where the reason is actionable.
    """
    if was_read or kind != "document" or data[:4] != b"%PDF":
        return None
    why = _why_unread(data)
    return why if why in _PDF_WHY else None


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
        if not text:
            # The eyes. Both honest refusals — the scan with no text layer
            # and the font whose map cannot be followed — leave the words
            # drawn on the page, and drawn words can be read (_ocr_text).
            # Tried only after the text reader comes back empty: where a
            # text layer exists it is the exact text, and OCR is the
            # approximate, expensive way to almost get it.
            text = _ocr_text(data)
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
        provider=None, unread_why: str | None = None,
        full_chars: int | None = None) -> dict:
    if kind not in KINDS:
        raise BriefcaseError(422, i18n.fill(i18n.FIELD_IS_ONE_OF, field="kind", choices=', '.join(KINDS)))
    if _count(profile_id, interactor_id) >= MAX_ITEMS:
        raise BriefcaseError(
            422, f"this conversation already carries {MAX_ITEMS} imported "
                 "items — remove one before adding another")
    title = (title or "").strip()[:160] or "Untitled"
    # The person's OWN words about what they handed over, and they reach the
    # prompt as "They said: …". Cut bare at 400 they ended mid-word, which
    # reads to the model as somebody trailing off rather than as a sentence
    # that was shortened by us.
    note, note_cut = common.clipped(note or "", 400)
    if note_cut:
        note += " … (they wrote more than is kept here)"
    note = note or None
    # The cut happens here, where its cost can be written down beside it.
    # Tidied first so the two numbers are comparable: `read_file` hands over
    # tidied text already and this is a no-op for it, but a direct caller
    # passing raw text would otherwise be told "20,000 of 70,000" where the
    # 70,000 counts whitespace the kept 20,000 no longer has.
    text = _clean(text or "")
    whole = len(text)
    text = capped(text)
    if full_chars is None:
        full_chars = whole
    digest = distill(text, title, provider) if read else ""
    item_id = db.new_id("brf")
    conn = db.connect()
    conn.execute(
        "INSERT INTO briefcase_items (id, profile_id, interactor_id, kind,"
        " title, note, source, text, digest, was_read, unread_why,"
        " full_chars, bytes, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (item_id, profile_id, interactor_id, kind, title, note, source,
         text or None, digest or None, 1 if read else 0,
         None if read else (unread_why or None),
         # NULL unless something was actually cut. A number equal to the kept
         # length would be a truncation notice on every whole document.
         full_chars if (full_chars or 0) > len(text or "") else None,
         size, db.utcnow()))
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
            # Shown to the person too, not only to the profile. Somebody who
            # uploads a filing and is told "held, not read" wants to know
            # whether to try a different export or stop trying.
            "unread_why": (row["unread_why"]
                           if "unread_why" in row.keys() else None),
            # And how much of it is actually here. `chars` is the kept
            # length; this is the document's, when the two differ. Absent
            # when nothing was cut, which is most items.
            "full_chars": (row["full_chars"]
                           if "full_chars" in row.keys() else None),
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
            # How much of it is here. A profile holding the first third of a
            # filing and believing it holds the filing answers about claim 14
            # from material it never saw — confidently, because nothing told
            # it otherwise. Said as a fact about the item, so it can offer
            # the part it has rather than invent the part it does not.
            whole = (row["full_chars"]
                     if "full_chars" in row.keys() else None)
            kept = len(row["text"] or "")
            if whole and kept and whole > kept:
                body += (f" [only the first {kept:,} characters of a "
                         f"{whole:,}-character document were kept — you have "
                         "not seen the rest, and must not answer as though "
                         "you had]")
            lines.append(f"{head}\n  {body}")
        else:
            said = f" They said it is: {row['note']}." if row["note"] else ""
            # And WHY, where the reader knows. "You could not open it" is
            # true of a scan, a locked file and a font this code cannot
            # follow, and a person told only that has no idea whether to
            # export it differently or give up. The profile that can say
            # which one it was is the profile that can suggest the next move.
            why = _PDF_WHY.get(row["unread_why"]
                               if "unread_why" in row.keys() else None)
            because = f" You could not read it because {why}." if why else ""
            unread.append(
                f"{head} — you have NOT seen its contents.{because}{said}")
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
