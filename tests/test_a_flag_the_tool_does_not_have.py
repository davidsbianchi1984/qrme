"""The backup scripts call git with flags git actually accepts.

`git remote update` takes `--prune` and nothing else. A `--quiet` was added
to it while fixing an unrelated crash, and git answered every run with

    error: unknown option `quiet'
    exit=129

which the script's own repair logic read as "this mirror is broken" and
acted on: it deleted three healthy repositories and re-cloned them, on
every run, for ever. The output said `repository: unusable, cloning again`
where it should have said `updating`.

Nothing in the suite could have caught it, because no test ran the command
line the scripts actually build. This one does — it reads the invocations
out of both scripts and runs them against scratch repositories, so a flag
that does not exist fails here rather than on somebody's machine. It also
covers `git clone`, where a bad flag is not destructive but does leave the
repository half of the backup silently unmade.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess

import pytest

from . import ratchets

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ("tools/master-backup.ps1", "tools/master-backup.sh")

#: Everything up to the end of the command: a brace, a newline, a redirect
#: or a pipe. Whatever is left that starts with `-` is a flag git must know.
TAIL = r"([^}\n>|]*)"
INVOCATIONS = (
    ("remote update", re.compile(r"git\s+-C\s+\S+\s+remote\s+update" + TAIL)),
    ("clone",         re.compile(r"git\s+clone" + TAIL)),
)


def _calls() -> list[tuple[str, str, tuple[str, ...]]]:
    found = []
    for name in SCRIPTS:
        text = (REPO / name).read_text(encoding="utf-8")
        for sub, pattern in INVOCATIONS:
            for m in pattern.finditer(text):
                flags = tuple(w for w in m.group(1).split() if w.startswith("-"))
                found.append((name, sub, flags))
    return found


CALLS = _calls()


def test_there_are_invocations_to_check():
    subs = {sub for _, sub, _ in CALLS}
    assert {"remote update", "clone"} <= subs, (
        f"only {sorted(subs)} found across {SCRIPTS} — the check below "
        "would pass on less than it is written to cover")
    floor = ratchets.floor("backup.git_calls")
    assert len(CALLS) >= floor, (
        f"only {len(CALLS)} invocation(s) found, below the {floor} recorded")


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
@pytest.mark.parametrize(
    "script,sub,flags", CALLS,
    ids=[f"{s.split('/')[-1]}:{sub}:{'-'.join(f) or 'bare'}"
         for s, sub, f in CALLS])
def test_git_accepts_the_flags_the_script_passes(script, sub, flags, tmp_path):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)

    if sub == "clone":
        argv = ["git", "clone", *flags, str(origin), str(tmp_path / "out")]
    else:
        mirror = tmp_path / "mirror.git"
        subprocess.run(["git", "clone", "-q", "--mirror",
                        str(origin), str(mirror)], check=True)
        argv = ["git", "-C", str(mirror), "remote", "update", *flags]

    done = subprocess.run(argv, capture_output=True, text=True)
    assert done.returncode == 0, (
        f"{script} runs `git {sub} {' '.join(flags)}`, and git exits "
        f"{done.returncode}: {done.stderr.strip()}\n"
        "A non-zero exit from `remote update` is read as a broken mirror and "
        "re-clones the whole repository, so an unknown flag is not cosmetic.")
