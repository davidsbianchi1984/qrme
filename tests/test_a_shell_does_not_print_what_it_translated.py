"""English on a screen that the same shell already translates.

The shape 0.47.9 found in the iPhone's voiceprint consent block, and 0.54.0
found again in the Windows beacon list:

    Detail = $"{b.Location ?? "—"} · {b.Scans} scan(s)"
             + (b.Active ? "" : " · picked up"),

while `nmg.beacon.scans` — *"{n} scan(s)"* — and `nmg.beacon.pickedup` —
*"picked up"* — sat in that same shell's table, translated into ten languages,
asked for by nothing. An owner reading the app in German was shown

    Garten · 3 scan(s) · picked up

which is the worst version of a localized product: translated chrome around
the two words that carry the meaning, so the screen looks finished and reads
as broken.

## Why the dead-key guard did not catch it

`test_a_shell_asks_for_a_key_it_has` sees a row nothing asks for and records
it. That is the right measurement and it is one step short: it cannot tell a
row **waiting for a screen that does not exist** from a row whose screen
exists and is printing the English by hand. Both look like silence from the
table's side. The 335-row backlog held both kinds, and only reading the
screens told them apart.

So this asks the other question: is any string a shell **shows** identical to
the English of a row that shell **holds**?

## What it deliberately does not flag

A literal in a display position is a bug. A literal anywhere else is usually a
protocol value — a JSON field name, a default a form posts back, a `kind` the
API matches on — and translating one of those breaks the request rather than
the reader. `DockStateBox.Text = "handle"` reads like a label and is a value
this page sends; it stays English on purpose.

That is why this greps **assignment into a display property**, not the whole
source. The first version of this check greped everything, reported 88 hits
across three shells, and 86 of them were protocol values. A guard that cries
wolf 86 times out of 88 is one nobody reads.
"""

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent

#: Per shell: its table, the screens it draws, and how a row looks in it.
#:
#: The root is the **view** directory, not the whole shell. `ApiClient` names
#: routes and JSON fields that read like English sentences, and scanning it
#: produced hundreds of matches on words like "Password" that were never on a
#: screen.
SHELLS = {
    "ios": {
        "table": "native/ios/Sources/L10n.swift",
        "views": "native/ios/Sources/Views",
        "exts": (".swift",),
        "row": r'"([\w.]+)":\s*\[\s*"en":\s*"((?:[^"\\]|\\.)*)"',
    },
    "android": {
        "table": "native/android/app/src/main/java/app/qrme/studio/L10n.kt",
        "views": "native/android/app/src/main/java/app/qrme/studio/ui",
        "exts": (".kt",),
        "row": r'"([\w.]+)"\s+to\s+mapOf\(\s*"en"\s+to\s+"((?:[^"\\]|\\.)*)"',
    },
    "windows": {
        "table": "native/windows/L10n.cs",
        "views": "native/windows/Views",
        "exts": (".cs", ".xaml"),
        "row": r'\["([\w.]+)"\]\s*=\s*new\(\)\s*\{\s*\["en"\]\s*=\s*"((?:[^"\\]|\\.)*)"',
    },
}

#: The record. Each row is a literal a shell shows that its own table already
#: translates, kept with the reason it is still there. Ratcheted: the list may
#: shrink and never grow.
#:
#: 0.54.1 read all twenty-four call sites, and the split was clean: **twelve
#: were labels and are now keys**; the rest are below, and every one of them
#: is a **value** — a string this shell posts back to a route that compares
#: against English. Translating one turns a working form into a 422.
#:
#:   * `stranger`, `professional`, `grandchild` — relationship kinds in the
#:     `types` list the steering API matches on;
#:   * `standard` — a SwiftUI `.tag()` on a signature-level Picker. Its label
#:     was localized all along; the guard was seeing the tag beside it;
#:   * `restricted` — the fallback when the server does not name a profile
#:     status, so it must be the word the server would have sent.
#:
#: Every remaining row is here because it was read, not because it was
#: skipped.
RECORDED = {
    ('android', 'grandchild'),
    ('android', 'professional'),
    ('android', 'stranger'),
    ('ios', 'grandchild'),
    ('ios', 'professional'),
    ('ios', 'restricted'),
    ('ios', 'standard'),
    ('ios', 'stranger'),
    ('windows', 'basis re-attested'),
    ('windows', 'grandchild'),
    ('windows', 'professional'),
    ('windows', 'stranger'),
}


def _strip_comments(text: str) -> str:
    """Comments are prose about the code, and prose quotes the strings it
    discusses. Reading them was what produced most of the first draft's noise.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith(("//", "///", "*")))


def _rows(spec) -> dict[str, str]:
    """English → key, for rows worth checking.

    Skips anything with a slot in it, and anything both short and single-word:
    `kind`, `handle`, `basic` and their kin are almost always protocol values,
    and a guard that reports eighty of those is one nobody reads.
    """
    text = (REPO / spec["table"]).read_text(encoding="utf-8")
    out = {}
    for key, english in re.findall(spec["row"], text):
        if "{" in english:
            continue
        if " " in english or len(english) >= 8:
            out[english] = key
    return out


def _shown(spec) -> set[tuple[str, str]]:
    """Every string literal these screens contain, with its file.

    Extracted as literals rather than searched for as substrings, and taken
    from anywhere in the literal — including the pieces of an interpolation.
    The first version of this guard only looked at assignments into display
    properties, and so could not see

        Detail = $"{b.Location} · {b.Scans} scan(s)"

    which is the exact line it was written for. It reported the shells clean
    and the injection pass caught it.
    """
    found = set()
    for path in (REPO / spec["views"]).rglob("*"):
        if path.suffix not in spec["exts"]:
            continue
        src = _strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
        for literal in re.findall(r'"((?:[^"\\\n]|\\.)*)"', src):
            found.add((literal.strip(" \u00b7\u2014-"), path.name))
    return found


def _live() -> set[tuple[str, str, str]]:
    out = set()
    for shell, spec in SHELLS.items():
        rows = _rows(spec)
        for literal, filename in _shown(spec):
            if literal in rows:
                out.add((shell, literal, filename))
    return out


def test_no_new_screen_prints_english_it_already_holds_translated():
    """The ratchet. A row translated ten ways and then typed out in English on
    the screen beside it is a translation nobody will ever read."""
    appeared = sorted((s, lit, fn) for s, lit, fn in _live()
                      if (s, lit) not in RECORDED)
    assert not appeared, "\n    ".join(
        [""] + [f"{s}: {fn} shows {lit!r}, which {s}'s own table translates"
                for s, lit, fn in appeared]) + (
        "\n  Use the key, or record it — but recording is ratcheted.")


def test_the_record_has_not_gone_stale():
    """A recorded row that is no longer shown is a note about a line somebody
    already fixed, and it makes the next reader trust the list less."""
    live = {(s, lit) for s, lit, _ in _live()}
    stale = sorted(RECORDED - live)
    assert not stale, "\n    ".join(
        [""] + [f"{s}: {lit!r} is recorded and no longer shown" for s, lit in stale]
    ) + "\n  Strike it from RECORDED."


def test_the_scan_can_still_see_a_screen():
    """A guard nobody has watched fail is a guard nobody should trust.

    Every shell puts a great many strings on screens, so a scan reporting a
    handful is far more likely to be broken than to be good news — which is
    what a rewrite of one of these regexes would produce.
    """
    for shell, spec in SHELLS.items():
        assert len(_shown(spec)) > 100, (
            f"{shell}: the scan found only {len(_shown(spec))} literal(s) on "
            f"any screen — the extractor has stopped matching")
        assert _rows(spec), f"{shell}: no rows parsed out of its table"
