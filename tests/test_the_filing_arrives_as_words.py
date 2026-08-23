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

import zlib

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


# -- and when it genuinely cannot be read ---------------------------------

def test_a_scan_says_it_is_a_scan():
    data = _scanned_pdf()
    assert _pdf_text(data) == ""
    assert _why_unread(data) == "scanned"
    kind, text, read = read_file(data, "US 2025 0265659 A1.pdf")
    assert read is False
    assert "no text layer" in (why_unread(data, kind, read) or "")


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


def test_only_a_document_gets_a_reason():
    """A photograph is not a failure of this reader — this deployment has
    ears and no eyes, which the prompt block says in its own words. Dressing
    that up as a diagnosis would bury the one case where the reason tells
    somebody what to do next."""
    assert why_unread(b"\x89PNG\r\n\x1a\n", "photo", False) is None
    assert why_unread(_identity_pdf(), "document", True) is None
