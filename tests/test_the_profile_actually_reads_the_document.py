"""A PDF comes back as words, or it comes back as nothing.

Asked three times, and the third time with the transcript attached — *"the
synthetic profile can't read documents still"*, under a room where the
profile had just said the filings *"came through as garbage on my end —
scanned PDFs, no text layer, so what I'm seeing is byte soup rather than
claims. I can make out the publication numbers from the filenames and
nothing else."*

The profile was reporting honestly. It had been handed 1,818 characters of
mojibake and told that was the document. Run against a real, ordinary,
text-bearing PDF, the shipped reader produced exactly that and declared it
read.

    asked     did any text come out of the PDF
    mattered  is it text

Three faults, and the third is why the first two survived three rounds of
being reported:

* Only zlib streams were decoded. A stream in **ASCII85** — which is what
  the real file used — raised `zlib.error`, and the handler appended the
  stream *still encoded*. The scanner then matched parentheses inside
  compressed bytes.
* **Hex strings were not matched at all.** `_PDF_STR` knew `(...)` and not
  `<...>`, so every generator that prefers hex produced an empty read.
* `len(text) >= 40` stood in for *is this text*. Forty characters is a
  length, and garbage is long. So the module header's own promise — *a PDF
  that carries only scanned pixels has no text in it to find* — was the one
  case never reached: unreadable bytes never came back empty, they came back
  as a paragraph.

The last one is the guard that matters. Everything upstream of it is
best-effort — filters this module implements, encodings it guesses at — and
best-effort is fine as long as the failures come back as failures. A profile
told plainly *this was held but could not be read* asks what is in it. A
profile handed mojibake describes the mojibake.

The fixtures are built here rather than committed, so what is being tested
is the reader against the filters real generators emit, not one file
somebody happened to keep.
"""

from __future__ import annotations

import base64
import zlib

import pytest

from qrme.briefcase import _pdf_text, _reads_like_language, read_file

#: Deliberately shaped like the thing that was handed over: prose, claim
#: language, and publication numbers, so a reader that returns only the
#: numbers is visibly not enough.
WORDS = ("Claim 1. A method for operating a distributed sensor array, "
         "comprising: receiving, at a controller, a plurality of measurement "
         "frames from sensors disposed about a monitored volume; determining "
         "a confidence interval for each frame; and suppressing frames whose "
         "interval exceeds a threshold. The abstract describes error bars "
         "rather than a slogan.")


def _literal(words: str) -> bytes:
    out = [b"BT /F1 12 Tf 72 720 Td"]
    for part in [words[i:i + 80] for i in range(0, len(words), 80)]:
        esc = part.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        out.append(b"(" + esc.encode("latin-1") + b") Tj 0 -14 Td")
    return b"\n".join(out + [b"ET"])


def _hexed(words: str) -> bytes:
    out = [b"BT /F1 12 Tf 72 720 Td"]
    for part in [words[i:i + 80] for i in range(0, len(words), 80)]:
        out.append(b"<" + part.encode("latin-1").hex().encode() + b"> Tj 0 -14 Td")
    return b"\n".join(out + [b"ET"])


def _pdf(stream: bytes, filt: bytes | None) -> bytes:
    body = b"<< /Length " + str(len(stream)).encode()
    if filt:
        body += b" /Filter " + filt
    body += b" >>\nstream\n" + stream + b"\nendstream"
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
        b" /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        body,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    for i, obj in enumerate(objs, 1):
        out += str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    return bytes(out + b"trailer\n<< /Size 6 /Root 1 0 R >>\n%%EOF\n")


def _a85(raw: bytes) -> bytes:
    return base64.a85encode(raw, adobe=True)


#: One per filter arrangement a real generator emits. `ascii85` and
#: `ascii85+flate` are the two that produced David's byte soup; the two hex
#: rows are the ones that came back empty.
ARRANGEMENTS = {
    "uncompressed": _pdf(_literal(WORDS), None),
    "flate": _pdf(zlib.compress(_literal(WORDS)), b"/FlateDecode"),
    "ascii85": _pdf(_a85(_literal(WORDS)), b"/ASCII85Decode"),
    "ascii85+flate": _pdf(_a85(zlib.compress(_literal(WORDS))),
                          b"[/ASCII85Decode /FlateDecode]"),
    "hex strings": _pdf(_hexed(WORDS), None),
    "hex strings+flate": _pdf(zlib.compress(_hexed(WORDS)), b"/FlateDecode"),
}


@pytest.mark.parametrize("arrangement", sorted(ARRANGEMENTS))
def test_the_words_come_out_whatever_the_stream_was_wrapped_in(
        arrangement: str) -> None:
    """The claim text, not the filename and not the wrapper.

    Two of these six read before this was written. The four that did not are
    the ones a person actually hands over.
    """
    text = _pdf_text(ARRANGEMENTS[arrangement])
    assert "Claim 1" in text, (
        f"a {arrangement} PDF gave up no claim text — got {text[:120]!r}")
    assert "threshold" in text, (
        f"a {arrangement} PDF was read only in part — got {text[-120:]!r}")


@pytest.mark.parametrize("arrangement", sorted(ARRANGEMENTS))
def test_the_document_is_marked_read_when_it_was(arrangement: str) -> None:
    """The flag the prompt block is built from. Text nobody is told about is
    text the profile will not use."""
    kind, text, read = read_file(ARRANGEMENTS[arrangement],
                                 "US 2025_0265659 A1.pdf")
    assert kind == "document"
    assert read is True, f"a readable {arrangement} PDF was reported unread"
    assert "Claim 1" in text


#: The exact opening of what the shipped reader handed to a profile, kept
#: verbatim. If a future reader ever produces this again, it must produce it
#: as *nothing* — the item held, and said so.
BYTE_SOUP = (
    "@oB<8Z7!%Ta0erK*G>ILZH]_[]^AId2IHKeir3&<<pLS?C%<HA;?2^+Qa/kl;7Ga "
    "<US>%7rHp=0HUr>%NHF9<.o=2oS,p tQ[B4H1_*F$Y9c_KI8n;Vj YD:grl%@@f6$~> "
    "Gat= Re?f3hH7;5 3draJY#FZJ[f4D,H#oZJ?+]1n; S!*=/f!`oY&7;kad8Itf#LP+"
    "1nBUcoj]7@&%S$?\"KA`hFL3t4X^>H+2*2gI"
)

WRECKAGE = {
    "the byte soup that shipped": BYTE_SOUP,
    "base64 of a photograph":
        "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS"
        "Ew8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/",
    "a hex dump":
        "89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52 00 00 01 f4 00 00"
        " 01 90 08 06 00 00 00",
}

WRITING = {
    "english prose":
        "Claim 1. A method for operating a distributed sensor array, "
        "comprising: receiving a plurality of measurement frames.",
    "a filing, heavy with numbers":
        "US 2025/0265659 A1 discloses, at paragraph [0042], a controller 120 "
        "coupled to sensors 130a-130n via bus 140.",
    "japanese, which has no spaces":
        "これは日本語の文書です。センサー配列の制御について説明します。"
        "信頼区間を決定し、閾値を超えるフレームを抑制します。",
    "arabic":
        "هذه وثيقة باللغة العربية تصف مصفوفة أجهزة الاستشعار وكيفية تحديد "
        "فترات الثقة لكل إطار قياس.",
    "german, which runs its words together":
        "Die Rechtsschutzversicherungsgesellschaft prüft die "
        "Geschwindigkeitsbegrenzung und die Datenschutzgrundverordnung "
        "sorgfältig.",
}


@pytest.mark.parametrize("what", sorted(WRECKAGE))
def test_wreckage_is_not_a_read(what: str) -> None:
    """The gate, from the failing side.

    This is the guard the reader never had, and the only reason the other
    two faults could survive being reported three times: they failed
    loudly enough for the profile to complain about and quietly enough for
    the flag to say everything was fine.
    """
    assert _reads_like_language(WRECKAGE[what]) is False, (
        f"{what} passed as writing — a profile handed this describes it")


@pytest.mark.parametrize("what", sorted(WRITING))
def test_writing_is_a_read(what: str) -> None:
    """And from the passing side, because a gate that refuses everything is
    the same defect pointed the other way: a document nobody can hand over.
    Scripts without spaces and languages that run words together are the two
    ways a naive gate gets this wrong."""
    assert _reads_like_language(WRITING[what]) is True, (
        f"{what} was refused as unreadable — that document cannot be handed "
        "to a profile at all")


def test_a_pdf_that_cannot_be_read_comes_back_empty_not_garbled() -> None:
    """What a scan has always been promised: held, and said so.

    A PDF whose content stream is an image codec has no text in it. The old
    reader appended the raw JPEG bytes and scanned them for parentheses.
    """
    scan = _pdf(b"\xff\xd8\xff\xe0" + bytes(range(256)) * 6, b"/DCTDecode")
    kind, text, read = read_file(scan, "scanned filing.pdf")
    assert kind == "document"
    assert text == "", f"a scan gave up {text[:120]!r} instead of nothing"
    assert read is False, "a scan was reported as read"


def test_a_short_note_is_still_a_read() -> None:
    """The gate has a floor, and the floor must not swallow a real one-liner.

    Applying a language test to a note too short to judge would be the new
    bug wearing the fix's clothes.
    """
    _, text, read = read_file(b"Meet me at 4pm.", "note.txt")
    assert read is True and text == "Meet me at 4pm."
