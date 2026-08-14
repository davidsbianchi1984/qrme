"""Nothing this API imports may be missing on a platform we ship to.

## What this file is for

The desktop app ships a frozen copy of this backend on macOS, Windows and
Linux. The suite runs on Linux only, so a module that exists on one and not
the others is invisible here: every test passes, the installer builds, and
the first thing a person on Windows sees is a backend that will not start.

That is not hypothetical. `qrme/widgets.py` imported `resource` — POSIX-only
— at module scope. `qrme/api.py` imports `routers/studio`, which imports
`widgets`, so the whole API failed to import on Windows. The frozen backend
died on first run, which failed the Windows installer job, which skipped the
release job, which is why 0.70.0 and 0.70.1 published with no installers
attached at all — including the macOS and Linux ones that had built fine.

    asked     does the module import
    mattered  does it import on every platform we ship

## Why this reads the source rather than importing

The obvious test is `import qrme.api` and see whether it raises. On Linux it
never will, whatever is in the file — the modules below are all present here.
The defect only exists on a platform the suite cannot run on, so the guard
has to be a property of the *text*: no module-scope import of a name that
some target platform does not have.

## Why the try/except form passes

A POSIX-only module is not banned — being unable to build the sandbox is a
real state this product already knows how to say out loud. What is banned is
importing one in a way that takes the process down with it. Wrapped in a
`try` that catches `ImportError`, the module is absent, the feature reports
itself unavailable in the reader's own language, and everything else on the
API still answers. That is the same shape as every other missing wall here.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

#: Standard-library modules that do not exist on at least one platform the
#: desktop app is built for. Not an exhaustive list of POSIX-only names —
#: an exhaustive list would be a second thing to maintain. These are the
#: ones plausibly reachable from a web backend, which is where the risk is.
ABSENT_SOMEWHERE = {
    "resource",     # no Windows — the one that actually shipped broken
    "fcntl",        # no Windows
    "pwd",          # no Windows
    "grp",          # no Windows
    "termios",      # no Windows
    "tty",          # no Windows
    "syslog",       # no Windows
    "posix",        # no Windows
}

PACKAGE = pathlib.Path(__file__).resolve().parent.parent / "qrme"


def _guarded(handlers: list[ast.ExceptHandler]) -> bool:
    """Whether these `except` clauses would catch a missing module.

    A bare `except:` counts. So does `except (ImportError, OSError)`.
    `ModuleNotFoundError` is a subclass of `ImportError` and is accepted by
    name for the person who writes the narrower one.
    """
    caught = {"ImportError", "ModuleNotFoundError"}
    for handler in handlers:
        if handler.type is None:
            return True
        names = (handler.type.elts if isinstance(handler.type, ast.Tuple)
                 else [handler.type])
        for name in names:
            if isinstance(name, ast.Name) and name.id in caught:
                return True
    return False


def _bare_imports(path: pathlib.Path) -> list[tuple[int, str]]:
    """Every module-scope import of an absent-somewhere module that is not
    wrapped in a handler for its absence.

    Only `tree.body` is walked, deliberately. An import inside a function
    runs when that function is called, and a function nobody calls on
    Windows cannot stop the process from starting — the defect this guard
    exists for is specifically the one that fires at import time.
    """
    found: list[tuple[int, str]] = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Try) and _guarded(node.handlers):
            continue
        statements = node.body if isinstance(node, ast.Try) else [node]
        for statement in statements:
            if isinstance(statement, ast.Import):
                for alias in statement.names:
                    root = alias.name.split(".")[0]
                    if root in ABSENT_SOMEWHERE:
                        found.append((statement.lineno, root))
            elif isinstance(statement, ast.ImportFrom):
                root = (statement.module or "").split(".")[0]
                if root in ABSENT_SOMEWHERE:
                    found.append((statement.lineno, root))
    return found


def test_no_module_imports_a_platform_specific_module_at_import_time():
    offences = []
    for path in sorted(PACKAGE.rglob("*.py")):
        for line, module in _bare_imports(path):
            offences.append(
                f"{path.relative_to(PACKAGE.parent)}:{line} imports "
                f"{module!r} at module scope")
    assert not offences, (
        "these imports run when the API is imported, and the module is not "
        "present on every platform the desktop app ships to — so the frozen "
        "backend will not start there at all. Wrap the import in "
        "`try: ... except ImportError:` and have the feature report itself "
        "unavailable instead:\n  " + "\n  ".join(offences))


def test_the_guard_would_notice_the_import_that_shipped(tmp_path):
    """The guard's own failure mode is silence, so it is shown a copy of the
    line that actually shipped and required to object to it."""
    was = tmp_path / "widgets.py"
    was.write_text("import json\nimport resource\nimport shutil\n")
    assert _bare_imports(was) == [(2, "resource")]


def test_an_import_wrapped_for_its_absence_is_allowed(tmp_path):
    """And required *not* to object to the fix, in both the narrow and the
    broad spelling — otherwise the only way to pass is to delete the
    feature."""
    narrow = tmp_path / "narrow.py"
    narrow.write_text("try:\n    import resource\n"
                      "except ModuleNotFoundError:\n    resource = None\n")
    broad = tmp_path / "broad.py"
    broad.write_text("try:\n    import resource\n"
                     "except ImportError:\n    resource = None\n")
    assert _bare_imports(narrow) == []
    assert _bare_imports(broad) == []


def test_an_import_wrapped_in_the_wrong_handler_is_still_an_offence(tmp_path):
    """A `try` is not the point — catching the absence is. Wrapping the
    import in a handler for something else leaves the process dying exactly
    as before, and would be the easiest way to silence this guard without
    fixing anything."""
    wrong = tmp_path / "wrong.py"
    wrong.write_text("try:\n    import resource\n"
                     "except ValueError:\n    resource = None\n")
    assert _bare_imports(wrong) == [(2, "resource")]


@pytest.mark.parametrize("module", sorted(ABSENT_SOMEWHERE))
def test_every_named_module_is_one_this_platform_actually_has(module):
    """The list is only useful if its entries are real module names. A typo
    would sit in it forever, guarding nothing — and reading as though it
    did."""
    __import__(module)
