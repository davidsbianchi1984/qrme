"""The package the wheel promises and the build context never had.

## The failure this exists for

`pyproject.toml` builds a wheel from two packages — `qrme*` and `cloudgw*` —
and the Dockerfile copied one of them. `setuptools` finds packages on disk,
so it found `qrme` and, seeing no `cloudgw/` directory in the build context,
shipped a wheel without it and said nothing. `qrme/routers/problems.py`
imports `cloudgw.problems` at module load, so the container could not import
the app at all: uvicorn exited on `ModuleNotFoundError`, and the proxy in
front of it answered `502` with an empty body.

    asked     do the tests pass
    mattered  does the thing that gets built start

Every test in this suite runs from the repository root, where `cloudgw/` is
sitting right there on the import path. Nothing any of them could assert
would have caught this, because the defect is not in the code — it is in
what the image is made of.

## Why this checks the build context and not the image

Building the image here would need a daemon, several minutes and a network,
and a guard that heavy is a guard somebody skips. The whole defect is a
mismatch between two files that both live in this repository, and it is
readable from them: the wheel says which packages it contains, the Dockerfile
says which directories the builder can see, and the first must be a subset of
the second.
"""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

from . import ratchets

REPO = Path(__file__).resolve().parent.parent


def _declared() -> list[str]:
    """The top-level packages the wheel is built from, as directories.

    `include` holds glob patterns (`qrme*`), and what matters for the build
    context is the directory each one actually matches here.
    """
    data = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    patterns = data["tool"]["setuptools"]["packages"]["find"]["include"]
    found = set()
    for pattern in patterns:
        top = pattern.split(".")[0]
        for path in REPO.glob(top):
            if path.is_dir() and (path / "__init__.py").exists():
                found.add(path.name)
    return sorted(found)


def _runtime_copies() -> set[str]:
    """Directories the runtime stage copies from the build context.

    Stage-scoped on purpose: `COPY app/ ./app/` in the console builder says
    nothing about what the service image holds, and reading the file as one
    flat list is how a guard concludes the opposite.
    """
    text = (REPO / "Dockerfile").read_text(encoding="utf-8")
    stages = re.split(r"^FROM ", text, flags=re.M)
    runtime = next(s for s in stages if s.startswith("python"))
    copied = set()
    for source, _dest in re.findall(r"^COPY\s+(?!--from)(\S+)\s+(\S+)",
                                    runtime, re.M):
        copied.add(source.rstrip("/").split("/")[0])
    return copied


def test_every_package_the_wheel_declares_is_in_the_build_context():
    """The guard.

    A package `pip install .` is asked to build and cannot see is not a
    build error — setuptools finds what is there and ships it. The absence
    arrives much later, as an import error inside a container, behind a
    proxy answering 502 with an empty body.
    """
    declared, copied = _declared(), _runtime_copies()
    missing = [p for p in declared if p not in copied]
    assert not missing, (
        f"the wheel is built from {declared} and the runtime stage copies "
        f"{sorted(copied)} — {missing} would be silently left out of the "
        "image, and the app cannot import without it. Add a `COPY` for each.")


def test_the_guard_can_still_see_both_halves():
    """A guard on the guard.

    Either half returning nothing would make the check above pass on any
    Dockerfile at all — an empty `declared` asserts nothing, and an empty
    `copied` would fail so loudly nobody could miss it, which is the
    harmless direction. This pins the silent one.
    """
    assert len(_declared()) >= ratchets.floor("wheel.declared"), (
        "fewer than two packages found for the wheel — the reader has "
        "drifted off pyproject's shape and this file is checking nothing")
    assert "qrme" in _runtime_copies(), (
        "the Dockerfile reader found no `qrme` in the runtime stage, which "
        "cannot be true of a working image — the parser has drifted")
