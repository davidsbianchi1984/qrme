"""The three shells' translation tables, read in one place.

Ten test files carried a byte-identical copy of the same twenty lines: build
the `shells` dict, list the nine languages, read the iOS table, pull the keys
matching this file's own prefix group, assert a floor on the count, then walk
every shell asserting each key is present in every language.

    asked     does this block of keys reach every shell in every language
    mattered  is that question asked once, or ten times in ten copies

Ten copies is how ten hand-set floors came to exist with nothing comparing
them to anything, which is what `unregistered_floors.txt` was counting. The
duplication was the cause and the floors were the symptom.

## What measuring them actually found

Not what the paydown so far would predict. Every one of these ten was in
band — ratios from 0.71 to 1.00, three of them at exactly 1.00 — while the
floors this estate has been correcting all round sat at a third, a sixth, and
in one case one per cent of what they measured.

    asked     is this floor unregistered
    mattered  is this floor wrong

They are not the same question. The backlog counts numbers nothing compares;
it does not count numbers that are wrong, and the two sets overlap far less
than the shrinking of one implies about the other. So these keep the floors
they already had rather than being recomputed to four-fifths: lowering a
guard that currently holds tight, in order to satisfy a convention about
where floors usually sit, would be following the rule off a cliff. What
registering buys here is the measurement attached and the audit every run —
not a different number.
"""
from __future__ import annotations

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this module")


REPO = _repo()

#: Where each shell keeps its table. The iOS one is the source of truth for
#: *which* keys exist; the other two are checked against it.
SHELLS = {
    "ios": REPO / "native/ios/Sources/L10n.swift",
    "android": (REPO / "native/android/app/src/main/java/app/qrme/"
                       "studio/L10n.kt"),
    "windows": REPO / "native/windows/L10n.cs",
}

#: The nine this estate translates into, beside English.
LANGS = ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")

#: Every prefix group a test file owns, by the name its ratchet uses. Held
#: here rather than in the ten files so that a group added to one shell and
#: forgotten in the record is visible as an edit to this list.
GROUPS = {
    "lobby": ("bot", "refer", "object", "lobby", "dock"),
    "crowd": ("crowd", "party", "lend"),
    "face": ("ava", "embl", "pg", "front", "surf", "comp", "form", "steer",
             "wrist"),
    "till": ("acct", "till", "life"),
    "lastdoors": ("born", "mind", "reach", "lic", "sens"),
    "place": ("place", "cam", "org", "tut"),
    "record": ("mem", "who", "src", "rec", "veil", "ver", "exit"),
    "seal": ("sig", "mail", "room", "disp", "member", "hand", "camp"),
    "sticker": ("bcn", "modq", "revw", "wm", "med", "wear"),
    "workshop": ("work", "dele", "asst", "task", "plc", "spec"),
}


def ios_keys(group: str) -> list[str]:
    """The keys the iOS table declares under this group's prefixes.

    Sorted and de-duplicated, because the comparison below is per key and a
    table that lists one twice would otherwise check it twice and report a
    larger surface than it has.
    """
    prefixes = "|".join(GROUPS[group])
    src = SHELLS["ios"].read_text(encoding="utf-8")
    return sorted(set(re.findall(rf'"((?:{prefixes})\.[a-z.]+)":', src)))


def missing_rows(keys: list[str]) -> list[str]:
    """Where a shell's table lacks a key, or lacks a language on one.

    Returns the problems rather than asserting, so a caller can name its own
    block in the failure and a future caller can count them instead. A helper
    that raises decides the sentence its caller reads, which is how ten copies
    of one check ended up with ten slightly different messages.
    """
    problems = []
    for shell, path in SHELLS.items():
        src = path.read_text(encoding="utf-8")
        for key in keys:
            row = re.search(rf'"{re.escape(key)}"[^\n]*', src)
            if row is None:
                problems.append(f"{shell}: missing {key}")
                continue
            for lang in LANGS:
                if f'"{lang}"' not in row.group(0):
                    problems.append(f"{shell}: {key} missing {lang}")
    return problems
