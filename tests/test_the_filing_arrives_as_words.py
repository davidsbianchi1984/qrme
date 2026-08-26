"""A filing written in embedded fonts arrives as words, not as a filename.

    asked     can these bytes be decoded as characters
    mattered  whose characters are they

The fourth report of the same thing, with two USPTO applications held and
unread and the profile saying so plainly: *"this setup couldn't turn either
PDF into text, so I genuinely haven't read a word of them."* It was telling
the truth. The gate that makes it tell the truth went in on the third report
and it worked — what it could not do was read.

`_string_text` had already named the reason in its own docstring: *a subset
font writing raw glyph ids does not read at all, in any encoding, without the
font's own map*. A composite font with `/Encoding /Identity-H` — which is
what a generator reaches for the moment a document is not plain ASCII, and
what a filing full of section signs and inventor names always is — writes
GLYPH NUMBERS in its own subset. Glyph 3 is the third glyph of that subset
and nothing else. There is no encoding under which those bytes are language.

`/ToUnicode` is the map back, and these files carry it, because it is what
makes them searchable in a reader. Following it is the whole difference.

Two structures, because a fix that handles one is a fix that handles half the
files: the map reachable by a scan of the file's own bytes, and the map
behind a compressed `/Type /ObjStm`, where every recent generator puts its
dictionaries and where a byte scan cannot see them at all.
"""

from __future__ import annotations

import re
import zlib
from pathlib import Path

import pytest

from qrme.briefcase import (_font_maps, _pdf_text, _why_unread, read_file,
                            why_unread)


def _obj(n: int, body: bytes) -> bytes:
    return f"{n} 0 obj\n".encode() + body + b"\nendobj\n"


def _stream(dic: bytes, body: bytes) -> bytes:
    packed = zlib.compress(body)
    return (dic[:-2] + f" /Filter /FlateDecode /Length {len(packed)} >>".encode()
            + b"\nstream\n" + packed + b"\nendstream")


SENTENCE = ("A method for regulating thermal transfer in a sealed enclosure, "
            "comprising a first conduit disposed along the interior wall and "
            "a second conduit in fluid communication therewith, wherein the "
            "controller varies flow responsive to a measured gradient.")


def _identity_pdf(text: str = SENTENCE, *, packed: bool = False) -> bytes:
    """A PDF written the way a filing is: glyph ids on the page, and a
    `/ToUnicode` CMap carrying them back to characters.

    With `packed`, the page and font dictionaries go inside a compressed
    object stream — the modern layout, and the one a scan of the file's
    bytes cannot see into.
    """
    order: dict[str, int] = {}
    for ch in text:
        order.setdefault(ch, len(order) + 3)
    glyphs = "".join(f"{order[c]:04X}" for c in text)
    content = f"BT /F1 12 Tf 72 720 Td <{glyphs}> Tj ET".encode()
    entries = "".join(f"<{g:04X}> <{ord(c):04X}>\n" for c, g in order.items())
    cmap = (b"begincmap\n1 begincodespacerange\n<0000> <FFFF>\n"
            b"endcodespacerange\n"
            + f"{len(order)} beginbfchar\n{entries}endbfchar\n".encode()
            + b"endcmap")
    page = (b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
            b" /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>")
    font = (b"<< /Type /Font /Subtype /Type0 /BaseFont /AAAAAA+Times"
            b" /Encoding /Identity-H /ToUnicode 6 0 R >>")
    parts = [_obj(1, b"<< /Type /Catalog /Pages 2 0 R >>"),
             _obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
             _obj(4, _stream(b"<< >>", content)),
             _obj(6, _stream(b"<< >>", cmap))]
    if packed:
        inner, head, bodies, off = [(3, page), (5, font)], [], [], 0
        for num, body in inner:
            head.append(f"{num} {off}".encode())
            bodies.append(body)
            off += len(body) + 1
        blob = b" ".join(head) + b"\n"
        first = len(blob)
        blob += b" ".join(bodies)
        parts.append(_obj(8, _stream(
            f"<< /Type /ObjStm /N {len(inner)} /First {first} >>".encode(),
            blob)))
    else:
        parts += [_obj(3, page), _obj(5, font)]
    return (b"%PDF-1.7\n" + b"".join(parts)
            + b"trailer\n<< /Root 1 0 R >>\n%%EOF\n")


def _scanned_pdf() -> bytes:
    """Pictures of pages: a content stream that draws one image and shows no
    text at all. There is nothing in here to read, and saying so is the
    right answer rather than a failure."""
    parts = [
        _obj(1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        _obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        _obj(3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
                b" /Resources << /XObject << /Im0 5 0 R >> >>"
                b" /Contents 4 0 R >>"),
        _obj(4, _stream(b"<< >>", b"q 612 0 0 792 0 0 cm /Im0 Do Q")),
        _obj(5, b"<< /Type /XObject /Subtype /Image /Width 2550"
                b" /Height 3300 /Filter /DCTDecode /Length 9 >>"
                b"\nstream\n\xff\xd8\xff\xe0JFIF\n\nendstream"),
    ]
    return (b"%PDF-1.5\n" + b"".join(parts)
            + b"trailer\n<< /Root 1 0 R >>\n%%EOF\n")


# -- the reading ----------------------------------------------------------

@pytest.mark.parametrize("packed", [False, True],
                         ids=["plain objects", "inside an object stream"])
def test_a_filing_written_in_glyph_ids_reads_as_its_sentence(packed):
    got = _pdf_text(_identity_pdf(packed=packed))
    assert "regulating thermal transfer" in got
    assert "measured gradient" in got


@pytest.mark.parametrize("packed", [False, True],
                         ids=["plain objects", "inside an object stream"])
def test_without_the_font_map_the_same_bytes_are_unreadable(packed,
                                                            monkeypatch):
    """The claim under the fix, stated as a difference rather than asserted:
    this is the same file, read without following `/ToUnicode`, and it is
    the empty answer the field report was looking at."""
    from qrme import briefcase

    monkeypatch.setattr(briefcase, "_font_maps", lambda data: {})
    assert briefcase._pdf_text(_identity_pdf(packed=packed)) == ""


def test_the_map_is_found_at_the_width_it_was_written():
    """A two-byte map applied a byte at a time yields twice as many wrong
    characters, which reads as wreckage exactly like the problem it was
    meant to fix — so the width is read from the CMap, not assumed."""
    maps = _font_maps(_identity_pdf())
    assert "F1" in maps
    assert maps["F1"].width == 2


def test_the_fonts_own_map_is_not_read_as_the_page():
    """A `/ToUnicode` CMap **is** a stream, full of `<0041>` tokens that
    look exactly like hex strings on a page. Scanning every stream in the
    file read the map as though it were the document and delivered every
    mapped letter twice — invisible while the letters were NULs, obvious
    the moment the fonts started working."""
    got = _pdf_text(_identity_pdf())
    assert got.rstrip().endswith("measured gradient."), (
        "something after the page's own last sentence came through — the "
        "font's map is being read as though it were the document"
    )


def test_nothing_unprintable_survives_into_the_text():
    """A glyph map hands back a NUL for an unmapped slot, and a partial map
    is the ordinary case — a subset font covers the glyphs its document
    uses and nothing else. A NUL counts toward length in the readability
    gate and reads as nothing at all on screen, which is a document that
    passes for read and shows blank.

    Read at `_clean`, where the rule lives, rather than only through a file
    that happens not to produce any: this test passed against a build with
    the stripping taken out, because scanning only the pages had already
    removed the source those NULs were coming from. A claim proven by a
    file that cannot exercise it is not proven.
    """
    from qrme.briefcase import _clean

    assert _clean("claim \x00 1 \x07 and\x1f 2") == "claim 1 and 2"
    # And the tab and newline it must NOT eat, since those are whitespace
    # and the collapse below them is what makes a page one paragraph.
    assert _clean("a\tb\nc") == "a b c"
    got = _pdf_text(_identity_pdf())
    assert got and not any(ord(c) < 32 for c in got)


# -- the other half of the same problem, and the dangerous half -----------
#
# A composite font writing glyph ids produces bytes that are obviously not
# language, so the gate catches them and the item is reported unread. A
# SIMPLE font with a re-arranged `/Differences` encoding produces bytes that
# ARE letters — the wrong ones. `[169 /section]` means byte 169 is a section
# sign; read as Latin-1 it is a copyright sign. That passes every readability
# test there is, and arrives as a document somebody believes.

def _differences_pdf() -> bytes:
    """A filing whose font re-points two bytes: a section sign and an
    accented letter, both of which a filing is full of."""
    content = (b"BT /F1 11 Tf 72 700 Td (See \xa9 2.14 of the specification, "
               b"and the caf\xa8 clause.) Tj ET")
    font = (b"<< /Type /Font /Subtype /TrueType /BaseFont /CCCCCC+Times"
            b" /Encoding << /Type /Encoding /Differences"
            b" [169 /section 168 /eacute] >> >>")
    parts = [_obj(1, b"<< /Type /Catalog /Pages 2 0 R >>"),
             _obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
             _obj(3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
                     b" /Resources << /Font << /F1 5 0 R >> >>"
                     b" /Contents 4 0 R >>"),
             _obj(4, _stream(b"<< >>", content)),
             _obj(5, font)]
    return (b"%PDF-1.4\n" + b"".join(parts)
            + b"trailer\n<< /Root 1 0 R >>\n%%EOF\n")


def test_a_rearranged_encoding_reads_as_the_characters_it_means():
    got = _pdf_text(_differences_pdf())
    assert "See \u00a7 2.14" in got
    assert "caf\u00e9 clause" in got


def test_without_it_the_same_page_is_wrong_rather_than_empty(monkeypatch):
    """The reason this one matters more than the composite case: the
    failure is not an empty answer somebody reports, it is a plausible
    answer somebody believes."""
    from qrme import briefcase

    monkeypatch.setattr(briefcase, "_font_maps", lambda data: {})
    got = briefcase._pdf_text(_differences_pdf())
    assert got, "the wrong-characters case comes back readable, not empty"
    assert "\u00a9 2.14" in got and "\u00a7" not in got


def test_unlisted_codes_keep_their_ordinary_character():
    """A `/Differences` array is a patch on the standard encoding and lists
    only what CHANGED. Read as though it were the whole map, a page becomes
    two mapped characters and fifty spaces — a map that then declines to be
    used, which is how this looked before the distinction existed."""
    from qrme.briefcase import _differences_map, _font_maps

    cmap = _font_maps(_differences_pdf())["F1"]
    assert cmap.over_base is True
    assert cmap.decode(b"abc") == "abc"
    # And a `/ToUnicode` map is the whole map, so it must NOT do this.
    assert _font_maps(_identity_pdf())["F1"].over_base is False
    assert _differences_map(b"<< /Type /Font >>") is None


def test_a_glyph_name_this_reader_does_not_know_is_left_alone():
    """Not replaced with a plausible letter. A document rendered in NEARLY
    the right characters is worse than one that comes back empty: the empty
    one gets reported and the nearly-right one gets believed."""
    from qrme.briefcase import _glyph_char

    assert _glyph_char("section") == "\u00a7"
    assert _glyph_char("eacute") == "\u00e9"
    assert _glyph_char("uni00A7") == "\u00a7"
    assert _glyph_char("gremlin") is None


def test_the_fonts_own_answer_wins_over_the_rendering_instruction():
    """`/ToUnicode` is the font's answer to exactly this question.
    `/Differences` is a rendering instruction that happens to imply one, so
    a font carrying both means the first."""
    from qrme.briefcase import _font_maps

    both = _identity_pdf().replace(
        b"/Encoding /Identity-H",
        b"/Encoding << /Differences [65 /section] >>")
    cmap = _font_maps(both)["F1"]
    assert cmap.width == 2 and cmap.over_base is False


# -- and when it genuinely cannot be read ---------------------------------

def test_a_scan_says_it_is_a_scan():
    data = _scanned_pdf()
    assert _pdf_text(data) == ""
    assert _why_unread(data) == "scanned"
    kind, text, read = read_file(data, "US 2025 0265659 A1.pdf")
    assert read is False
    # A key, never a sentence: the prompt block is written in English and the
    # console is written in ten languages, and they need different words for
    # the same fact. There is no way back from a sentence to what it states.
    assert why_unread(data, kind, read) == "scanned"
    from qrme.briefcase import _PDF_WHY

    assert "no text layer" in _PDF_WHY["scanned"]


def test_a_locked_file_says_it_is_locked():
    """Three failures wore one sentence. A person told only "could not open
    it" has no idea whether to try a different export, find the password, or
    stop trying."""
    data = _scanned_pdf().replace(b"trailer\n<<", b"trailer\n<< /Encrypt 9 0 R")
    assert _why_unread(data) == "locked"


def test_a_font_this_reader_cannot_follow_says_so():
    """The honest name for a gap in this code, kept distinct from a scan so
    the next report says which one it is."""
    data = _identity_pdf().replace(b"/ToUnicode 6 0 R", b"                ")
    assert _pdf_text(data) == ""
    assert _why_unread(data) == "unmapped"


def test_a_minified_map_is_the_whole_map():
    """A CMap written on one line is the same map.

    The first bfrange follower split the block on \\n and read one range
    per "line" — which on a minified map, or one written with \\r-only
    endings, meant the FIRST range and none after it: most of the alphabet
    lost silently and reported as this reader's own "unmapped". The
    grammar never needed the lines — two hex tokens then a destination,
    repeated — so the follower walks tokens now and the layout of the
    bytes stops mattering.
    """
    from qrme.briefcase import _parse_cmap

    one_line = (b"begincodespacerange <0000> <FFFF> endcodespacerange "
                b"beginbfrange <0003> <0005> <0041>"
                b" <0006> <0007> [<0058> <0059>] endbfrange")
    m = _parse_cmap(one_line)
    assert m is not None
    assert (m.table[3], m.table[4], m.table[5]) == ("A", "B", "C")
    assert (m.table[6], m.table[7]) == ("X", "Y")
    # The same map with carriage returns for line ends — a layout that
    # really ships — reads identically.
    cr = one_line.replace(b"> <", b">\r<")
    m2 = _parse_cmap(cr)
    assert m2 is not None and m2.table == m.table


def test_the_eyes_read_what_the_text_reader_refused(monkeypatch):
    """OCR is the route around BOTH honest refusals at once.

    The owner shared two filings in one afternoon and the profile refused
    both, correctly: one was pages-as-pictures ("scanned"), the other
    wrote its text in fonts whose map could not be followed ("unmapped").
    From the other side of the glass they are one problem — the words are
    DRAWN on the page either way, and drawn words can be read. The eyes
    run only after the text reader comes back empty, because a text layer
    is the exact text and OCR is the approximate way to almost get it.
    """
    import qrme.briefcase as bc

    monkeypatch.setattr(bc, "_ocr_text", lambda data: SENTENCE)
    for data in (_scanned_pdf(),
                 _identity_pdf().replace(b"/ToUnicode 6 0 R",
                                         b"                ")):
        kind, text, read = read_file(data, "filing.pdf")
        assert read is True and text == SENTENCE
        # Read is read: no diagnosis rides along with a document that
        # arrived as words.
        assert why_unread(data, kind, read) is None
    # And a PDF whose text layer works never pays for the eyes.
    monkeypatch.setattr(bc, "_ocr_text",
                        lambda data: pytest.fail("OCR ran on readable text"))
    _, text, read = read_file(_identity_pdf(), "filing.pdf")
    assert read is True and SENTENCE.split()[0] in text


def test_without_eyes_the_refusal_stands(monkeypatch):
    """A deployment without the tools keeps today's honest answer.

    `_ocr_text` feature-detects poppler and tesseract; both absent means
    "" — which IS the refusal, in the same words as before, with the same
    key for the console's ten languages. Nothing new to install for a dev
    checkout, nothing invented for a box the image was not built on.
    """
    import shutil

    monkeypatch.setattr(shutil, "which", lambda name: None)
    data = _scanned_pdf()
    kind, text, read = read_file(data, "filing.pdf")
    assert read is False and text == ""
    assert why_unread(data, kind, read) == "scanned"


def test_only_a_document_gets_a_reason():
    """A photograph is not a failure of this reader — this deployment has
    ears and no eyes, which the prompt block says in its own words. Dressing
    that up as a diagnosis would bury the one case where the reason tells
    somebody what to do next."""
    assert why_unread(b"\x89PNG\r\n\x1a\n", "photo", False) is None
    assert why_unread(_identity_pdf(), "document", True) is None


# -- and the room, which is the other half of the same door ----------------
#
# The pair's briefcase and a room share run through one reader,
# `briefcase.read_file`, and until now only the briefcase said which kind of
# unreadable it was. A fix that reaches one of two paths looks exactly like a
# fix — this session has already caught that shape twice — so the room is
# read here by taking a real share and reading the transcript the model gets.

def _share(client, room_id, interactor, data, name):
    from tests.test_capabilities import as_interactor

    return client.post(
        f"/rooms/{room_id}/share?interactor_id={interactor}"
        f"&filename={name}&caption=have a look",
        headers=as_interactor(interactor), content=data)


def test_a_room_share_says_which_kind_of_unread(client, monkeypatch):
    from tests.test_capabilities import (as_interactor, make_interactor,
                                         make_profile)
    from qrme.routers import community

    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": user},
        {"kind": "profile", "id": dana["id"]}]}).json()["id"]

    r = _share(client, room, user, _scanned_pdf(), "US 2025 0265659 A1.pdf")
    assert r.status_code in (200, 201), r.text

    seen: list = []

    class Provider:
        def generate(self, system, turns):
            seen.append(turns)
            return "Noted."

    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: Provider())
    advanced = client.post(f"/rooms/{room}/advance",
                           headers=as_interactor(user))
    assert advanced.status_code in (200, 201), advanced.text
    assert seen, "no profile turn was taken"
    handed = " ".join(t["content"] for t in seen[-1])
    assert "no text layer" in handed, (
        "a room share that could not be read still says only that it could "
        "not be read — the reason reaches the pair's briefcase and not here"
    )


# -- and on screen, where the person who uploaded it is looking ------------

CONSOLE = (Path(__file__).resolve().parents[1] / "app" / "src")
BRIEFCASE_TSX = (CONSOLE / "Briefcase.tsx").read_text(encoding="utf-8")
L10N = (CONSOLE / "l10n.ts").read_text(encoding="utf-8")

#: The file with its comments taken out. A guard that forbids a pattern has
#: to read past the note explaining why the pattern is not used, or it trips
#: on its own reasoning — which is a guard that punishes writing the reason
#: down, and this session has done it three times.
CODE_ONLY = re.sub(r"/\*.*?\*/|//[^\n]*", "", BRIEFCASE_TSX, flags=re.S)


def _looked_up(source: str, prefix: str) -> set[str]:
    """The keys under `prefix` this file actually hands to `tr`.

    Matched at the `tr` call, which is the only shape the console's own
    lookup scanner can see — and therefore the only shape that proves a
    translated string is being read rather than sitting unread while the
    English shows. Pinning where the key is *stored* instead is what these
    guards did first, and they broke the moment the storage got better.
    """
    return set(re.findall(rf'tr\("({re.escape(prefix)}[a-z]+)"', source))


def test_every_reason_the_reader_gives_has_a_line_on_screen():
    """The two halves cannot drift. A reader that learns a fourth kind of
    unreadable and a console that knows three would put a filing under a
    blank line — which is where this started."""
    from qrme.briefcase import _PDF_WHY

    # `empty` is the catch-all; it has no advice to give, so no line.
    named = {k for k in _PDF_WHY if k != "empty"}
    for source, prefix in ((BRIEFCASE_TSX, "prf.bc.why."),
                           (INSIDE_TSX, "ins.file.why.")):
        shown = {k.rsplit(".", 1)[-1] for k in _looked_up(source, prefix)}
        assert named <= shown, (
            f"{prefix}: the reader gives {sorted(named - shown)} and this "
            "screen says nothing for them"
        )
        for key in named:
            assert f'"{prefix}{key}"' in L10N, prefix + key


def test_the_keys_are_written_out_rather_than_assembled():
    """A key built inside the call — `prf.bc.why.${...}` — is invisible to
    the lookup scanner, so the guard that proves every key has ten
    languages behind it cannot see it. This console has shipped that
    mistake in both of its shapes: a template, and a table of key strings
    the scanner reads as data rather than as a lookup."""
    for source, prefix in ((CODE_ONLY, "prf.bc.why."),
                           (INSIDE_CODE, "ins.file.why.")):
        assert prefix + "${" not in source, (
            f"{prefix}: the key is assembled at run time, so nothing "
            "checks it has translations"
        )
        assert _looked_up(source, prefix), (
            f"{prefix}: no key reaches `tr` as a literal, so the lookup "
            "scanner cannot see these strings being read at all"
        )


def test_the_reason_is_shown_only_where_there_is_one():
    """An item that read has no reason, and an unknown key renders nothing
    rather than a missing-translation placeholder under somebody's
    filing."""
    assert "!item.read && whySays(item.unread_why" in CODE_ONLY
    assert "return null;" in CODE_ONLY, (
        "an unrecognised reason has no way to render nothing"
    )


# -- and in the room, on the attachment itself -----------------------------
#
# The field report was a photograph of exactly this line: "US 2025 0265659
# A1.pdf  held, not read — nobody here can see inside it". True, and it is
# the sentence that sent the same report back four times, because it is the
# same sentence for a scan, a locked file and a font this reader could not
# follow — and only one of those is worth trying a different export for.

INSIDE_TSX = (CONSOLE / "screens" / "Inside.tsx").read_text(encoding="utf-8")
INSIDE_CODE = re.sub(r"/\*.*?\*/|//[^\n]*", "", INSIDE_TSX, flags=re.S)


def test_the_room_puts_the_reason_on_the_wire(client):
    """Taken off a real share and a real transcript read, because
    `_media_brief` is what every room surface goes through — the store, the
    transcript and the share reply — and a fact added to one of them is a
    fact the other two do not have."""
    from tests.test_capabilities import (as_interactor, make_interactor,
                                         make_profile)

    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": user},
        {"kind": "profile", "id": dana["id"]}]}).json()["id"]

    posted = _share(client, room, user, _scanned_pdf(),
                    "US 2025 0265659 A1.pdf")
    assert posted.status_code in (200, 201), posted.text
    assert posted.json()["shared"]["media"]["unread_why"] == "scanned"

    seen = client.get(f"/rooms/{room}/messages",
                      headers=as_interactor(user)).json()
    attached = [m["media"] for m in seen if m.get("media")]
    assert attached and attached[-1]["unread_why"] == "scanned", (
        "the share reply says why and a reload does not — the person who "
        "comes back to the room sees the sentence that sent this report "
        "back four times"
    )


def test_a_read_file_carries_no_reason(client):
    """There is nothing to explain about a file that read, and a leftover
    key under one would be a diagnosis nobody made."""
    from tests.test_capabilities import make_interactor, make_profile

    user = make_interactor(client, "Sam", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": user},
        {"kind": "profile", "id": dana["id"]}]}).json()["id"]

    posted = _share(client, room, user,
                    b"Claim 1. A method of regulating thermal transfer in a "
                    b"sealed enclosure, comprising a first conduit disposed "
                    b"along the interior wall of the enclosure.",
                    "claims.txt")
    media = posted.json()["shared"]["media"]
    assert media["read"] is True
    assert media["unread_why"] is None


def test_the_room_line_says_which_kind():
    """The attachment line the field report was a photograph of."""
    assert _looked_up(INSIDE_CODE, "ins.file.why.") == {
        "ins.file.why.scanned", "ins.file.why.locked",
        "ins.file.why.unmapped"}
    assert "fileWhy(m.media.unread_why" in INSIDE_CODE, (
        "the room still shows one sentence for all three failures"
    )


def test_an_unknown_reason_falls_back_rather_than_showing_a_placeholder():
    """A reader that learns a fourth kind must not put a missing-translation
    key in the middle of somebody's conversation."""
    assert ': tr("ins.file.unread", lang))' in INSIDE_CODE, (
        "there is no plain fallback for a reason this console does not know"
    )
