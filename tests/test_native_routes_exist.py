"""The iOS, Android and Windows shells call real routes too.

`native.yml` compiles all three, which is the only reason a missing symbol or a
changed SwiftUI signature gets caught before somebody opens Xcode. But a path is
a string in every one of these languages: `"/post/\\(id)/like"` compiles
perfectly, ships, and 404s in the field. That is exactly the Wall bug, and the
shells had no guard against it at all while the console had one.

Roughly two hundred path literals live in `native/`, in three languages, and
until now not one of them had ever been compared with the route table.
"""

from __future__ import annotations

import re

from qrme.api import app

from . import clientpaths
from .clientpaths import NATIVE, paths

# The clients keep their paths in one file per platform, but the scan covers
# every source under `native/` so an inline call in a view is caught too.
_MIN_PATHS = 40


def test_every_native_path_reaches_a_route():
    """One assertion per platform would hide which platform drifted.

    Reported together instead, because a path added to two shells and mistyped
    in the third is the likely shape of this failure and the diff should say so.
    """
    missing: list[str] = []
    for lang in NATIVE:
        for line in clientpaths.unresolved(app, lang):
            missing.append(f"[{lang.name}] {line}")
    assert not missing, (
        "the native shells build these paths and no route accepts them:\n  "
        + "\n  ".join(missing)
    )


def test_each_shell_is_actually_being_scanned():
    """A guard on the guard.

    An extraction regex that silently matches nothing turns this whole file into
    a test that always passes — the worst kind, because the coverage it claims
    reads the same as the coverage it has. If a shell is deliberately dropped
    this fails and the number is changed on purpose.
    """
    counted = {lang.name: len(paths(lang)) for lang in NATIVE}
    thin = {k: v for k, v in counted.items() if v < _MIN_PATHS}
    assert not thin, (
        f"suspiciously few paths extracted: {thin} (expected at least "
        f"{_MIN_PATHS} per shell) — the literal or interpolation pattern for "
        f"that language has probably stopped matching. All counts: {counted}"
    )


def test_no_shell_uses_a_singular_mapped_segment():
    """The Wall bug's own shape, banned on the phones before it can happen.

    The console is already held to this. The shells reach the same
    kind-dispatching routes, so the same spelling rule applies: `/posts/`
    resolves and is accepted, `/post/` resolves and is then refused inside the
    handler. Only the second one looks like a working button.
    """
    from qrme.routers.audience import _KIND_BY_PATH

    offenders: list[str] = []
    for lang in NATIVE:
        for path, (source, literal) in sorted(paths(lang).items()):
            head = path.lstrip("/").split("/", 1)[0]
            if head in _KIND_BY_PATH.values() and head not in _KIND_BY_PATH:
                plural = next(p for p, s in _KIND_BY_PATH.items() if s == head)
                offenders.append(
                    f"[{lang.name}] {source}: {literal!r} uses /{head}/ "
                    f"(should be /{plural}/)"
                )
    assert not offenders, (
        "native sources use singular segments the kind lookup will refuse:\n  "
        + "\n  ".join(offenders)
    )


def test_the_shells_and_the_console_agree_on_the_wall():
    """Whatever the console learned in 0.17.0, the shells must not unlearn.

    The fix that round was a five-line change in one TypeScript file. Nothing
    stopped the same five paths being written the old way in Swift, Kotlin or
    C#, where no test was looking.
    """
    for lang in NATIVE:
        text = "\n".join(
            f.read_text(encoding="utf-8")
            for f in sorted(lang.root.rglob("*"))
            if f.suffix in lang.suffixes and f.is_file()
        )
        for verb in ("like", "comments", "share"):
            assert not re.search(rf"[\"/]post/[^\"\n]*/{verb}", text), (
                f"{lang.name} reaches for the singular /post/…/{verb}"
            )
