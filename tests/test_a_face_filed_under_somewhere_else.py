"""Eight systems on the shelf, and three clients filing every face as "other".

`GET /avatars/market` has named eight places a person may already have a face
— Ready Player Me, Bitmoji, Meta, Memoji, Xbox, Zepeto, Mii, and the catch-all
— since the avatar deck was written. Each row carries the provider's own export
route in that provider's words, which is the half somebody actually needs.

The console grew a picker for it. The three shells fetched the shelf, counted
it, put the number on screen, and then posted `source: "other"`.

    asked     did the import go through
    mattered  does the record say where it came from

`import_avatar` takes a source for exactly one reason, stated in its own
docstring: *the import is written onto the profile's own record as a source
item — which provider or path it came from, when* … *so the face's provenance
survives next to the face.* Filing all of it under the value that means
"somewhere else" is that provenance thrown away at the last step, by the code
that had just been handed it.

Android's binding was the clearest form of it: `avatarMarket()` decoded the
eight rows and returned `arr.length()`. The shell could say "8" and had no way
to name one — a binding that reads the answer, throws it away, and returns a
count of what it discarded.

## What this file checks, and what it deliberately does not

Not that a particular provider is offered: the shelf is a deployment's own
list and this suite has no business pinning its contents. What it checks is
that no client hard-codes the fallback source at a call site — which is the
shape the defect took on all three at once, and the shape it would take again.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

#: One file per shell — the one that actually posts the import.
CALLERS = {
    "ios": REPO / "native/ios/Sources/Views/FaceView.swift",
    "android": REPO / "native/android/app/src/main/java/app/qrme/studio/ui/Screens.kt",
    "windows": REPO / "native/windows/Views/PeoplePage.xaml.cs",
}

#: And the console, which had it right and is here so the check reads the same
#: question of all four clients rather than treating the phones as a special
#: case. The odd-client-out is a thing this estate has been bitten by.
#: The deck lives on the Identity screen now — SkinPicker.tsx was the
#: orphan component a whole deploy night was lost to (finished features
#: nothing mounted), and it is gone so no guard can assert on an
#: unmounted file again.
CONSOLE = REPO / "app/src/screens/Identity.tsx"


def test_the_shelf_still_names_more_than_one_system():
    """A guard on the guard. If the shelf collapsed to a single row, a picker
    would be a formality and every check below would pass on nothing."""
    from qrme import avatars

    from .ratchets import floor
    assert len(avatars.MARKET) >= floor("avatars.skin_shelf"), (
        f"the skin shelf is down to {len(avatars.MARKET)} row(s) — a picker "
        "over that is a label, and this file is asserting nothing")


def test_other_is_a_row_on_the_shelf_and_not_a_default():
    """`other` is a legitimate choice — somebody exporting from a system this
    deployment has never heard of picks it deliberately. What it must not be
    is what a client reaches for when it has the real answer in hand."""
    from qrme import avatars
    keys = [m["key"] for m in avatars.MARKET]
    assert "other" in keys
    assert keys[-1] == "other", (
        "`other` is no longer last on the shelf — it is the catch-all and "
        "reads as one only at the end of the list")


def test_no_client_hard_codes_the_source_it_imports_under():
    """The defect, directly, in all four clients at once.

    A literal source beside the import call is a client that decided where
    somebody's face came from on their behalf.
    """
    guilty = {}
    for name, path in {**CALLERS, "console": CONSOLE}.items():
        text = path.read_text(encoding="utf-8")
        # A quoted shelf key sitting in an argument list — `"other",` — rather
        # than a variable. Deliberately narrow: the *declaration* of a default
        # in state is fine and every client has one, because a picker has to
        # open on something.
        for hit in re.finditer(r'["\'](other|ready_player_me|bitmoji)["\']\s*,',
                               text):
            line = text[:hit.start()].count("\n") + 1
            guilty.setdefault(name, []).append(f"{path.name}:{line}")
    assert not guilty, (
        "these clients pass a hard-coded source to the import:\n    "
        + "\n    ".join(f"{k}: {', '.join(v)}" for k, v in sorted(guilty.items()))
        + "\n  The shelf is on the wire and the person is looking at it — "
          "the provenance should be what they picked.")


def test_every_shell_reads_the_shelf_into_something_it_can_name():
    """Android's binding returned `arr.length()`.

    A count is not a shelf. This asserts each shell carries the *rows* far
    enough to put a name on screen, which is the difference between offering
    eight systems and reporting that eight exist.
    """
    missing = []
    for name, path in CALLERS.items():
        text = path.read_text(encoding="utf-8")
        if not re.search(r"\bshelf\b|_skinShelf", text):
            missing.append(name)
    assert not missing, (
        f"{', '.join(missing)} import without holding the shelf, so nothing "
        "on screen can name where a face came from")


def test_each_shell_shows_the_providers_own_export_route():
    """The `how` field, which is the useful half and which no shell carried.

    "Export a .glb from your avatar page" is the sentence that turns a URL box
    into something somebody can complete. It has been on the wire the whole
    time and only the console ever rendered it.
    """
    missing = [name for name, path in CALLERS.items()
               if not re.search(r"\bhow\b|\.How\b", path.read_text("utf-8"))]
    assert not missing, (
        f"{', '.join(missing)} show a source picker with no export "
        "instructions — the shelf's `how` is on the wire and unread")
