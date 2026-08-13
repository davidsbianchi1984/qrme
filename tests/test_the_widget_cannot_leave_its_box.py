"""A person's own code runs here, and it reaches nothing that is not theirs.

## What this file is for

The Studio lets somebody write a widget — a function of their own, stored
against their profile, run against their own data. That is the feature. This
file is the reason it can exist on a host that also holds JIM-mini's clinical
captures, PDI's tenant vaults and every profile's remembrance.

    asked     can a person run their own code here
    mattered  can a person run their own code without reaching anybody else's

Every test below is an escape attempt written the way somebody would actually
write it, run through the real runner. None of them assert on the *source* of
`qrme/widgets.py` — a guard that reads the sandbox's own configuration and
agrees with it proves only that the file is self-consistent. These run the
code and read what came back.

## Why the walls are tested one at a time

A single "can it escape" test passes for the wrong reason the moment one wall
holds and another is gone: the escape fails, the test is green, and the
missing wall is invisible until an attempt arrives that needed only that one.
So the network, the filesystem, the process table, the clock and the
allocator are each asked separately, and each failure message names which
wall fell.
"""
from __future__ import annotations

import shutil
import subprocess

import pytest

from qrme import widgets


def _ran(source: str, inputs: dict | None = None) -> dict:
    """Run a widget and fail loudly if the sandbox refused to build at all —
    a refusal renders as `status: refused` and would otherwise read as a
    successful block."""
    answer = widgets.run_source(source, inputs)
    assert answer["status"] != "refused", (
        "the sandbox could not be built here, so nothing below proves "
        f"anything: {answer['detail']}")
    return answer


def test_the_sandbox_is_available_in_this_environment():
    """The guard on the guard. If the walls cannot be built, every escape
    test below 'passes' because nothing ran."""
    ready, why = widgets.sandbox_available()
    assert ready, (
        f"the widget sandbox cannot be built here ({why}) — on a host where "
        "this is true the feature must refuse rather than degrade, and these "
        "tests cannot tell you whether it does")


def test_a_widget_returns_what_it_computed():
    """The feature itself, first: a box nothing can run in is not a sandbox,
    it is a wall."""
    answer = _ran("module.exports = ({a, b}) => a + b;", {"a": 2, "b": 3})
    assert answer["status"] == "ok", answer
    assert answer["value"] == 5


def test_a_widget_cannot_reach_the_network():
    """The wall that matters most. A widget that can reach the network can
    send out whatever it can read, and can be told what to do by somebody who
    is not its author."""
    answer = _ran("""
      module.exports = async () => {
        const r = await fetch("https://example.com");
        return "REACHED " + r.status;
      };
    """)
    assert answer["status"] == "error", (
        f"a widget reached the network: {answer}")
    assert "REACHED" not in str(answer.get("message", ""))


def test_a_widget_cannot_read_the_host_filesystem():
    """`/etc/passwd` stands in for every file on the machine that is not the
    widget's own: the database, the key material, another person's export."""
    answer = _ran("""
      module.exports = () =>
        require("node:fs").readFileSync("/etc/passwd", "utf8").slice(0, 20);
    """)
    assert answer["status"] == "error", (
        f"a widget read a file outside its own directory: {answer}")


def test_a_widget_cannot_read_the_database():
    """The specific file this whole estate exists to protect, asked for by
    name and by the path the deployment actually uses."""
    answer = _ran("""
      module.exports = () => {
        const fs = require("node:fs");
        for (const p of ["qrme.db", "/app/qrme.db", "../../qrme.db"]) {
          try { return "READ " + fs.readFileSync(p).length; } catch (e) {}
        }
        return "no";
      };
    """)
    assert answer["status"] == "error" or answer["value"] == "no", (
        f"a widget read a database file: {answer}")


def test_a_widget_cannot_start_a_process():
    """The escape that would make every other wall irrelevant, because the
    child would carry none of them."""
    answer = _ran("""
      module.exports = () =>
        require("node:child_process").execSync("id").toString();
    """)
    assert answer["status"] == "error", (
        f"a widget started a process: {answer}")


def test_a_widget_cannot_see_this_process_environment():
    """Model keys, admin tokens and the collector's bearer live in this
    process's environment. The child is given a PATH and nothing else."""
    answer = _ran("""
      module.exports = () => Object.keys(process.env).sort().join(",");
    """)
    assert answer["status"] == "ok", answer
    seen = set(filter(None, answer["value"].split(",")))
    assert seen <= {"PATH", "NODE_OPTIONS", "HOME"}, (
        f"the child can read more of the environment than it should: {seen}")


def test_a_spinning_widget_is_killed():
    """The loop with no exit. RLIMIT_CPU arrives as a signal the child cannot
    ignore; the wall clock catches what the CPU cap does not."""
    answer = _ran("module.exports = () => { for (;;) {} };")
    assert answer["status"] in ("timeout", "killed"), answer
    assert answer["ms"] <= widgets.LIMITS["wall_seconds"] * 1000 + 1500, (
        f"the runner waited {answer['ms']}ms on a widget that never returns")


def test_a_sleeping_widget_is_killed():
    """The CPU cap does not fire on a widget that spends its time waiting, so
    the wall clock has to.

    The waiting has to be real waiting — a timer the runtime is holding open
    — which is what a widget polling for something it will never get looks
    like from outside.
    """
    answer = _ran("""
      module.exports = () => new Promise((resolve) => {
        setTimeout(resolve, 60 * 1000);
      });
    """)
    assert answer["status"] == "timeout", answer
    assert answer["ms"] <= widgets.LIMITS["wall_seconds"] * 1000 + 1500


def test_a_widget_that_never_answers_is_not_waited_on():
    """The distinction this file nearly lost.

    `new Promise(() => {})` never resolves, but it also holds nothing open,
    so the event loop empties and node exits — in forty milliseconds, with
    no answer written. Reading that as a timeout would have taught the
    runner to wait five seconds for a child that had already gone, and
    reading it as success would have handed the console an empty value as
    though the widget had returned one.

        asked     did the widget take too long
        mattered  did the widget answer at all

    Both are failures, and they are not the same failure: this one is
    somebody's forgotten `resolve`, and the reader deserves to be told that
    rather than told about a clock.
    """
    answer = _ran("module.exports = () => new Promise(() => {});")
    assert answer["status"] == "killed"
    assert answer["detail"] == "widgets.no_answer"
    assert answer["ms"] < widgets.LIMITS["wall_seconds"] * 1000


def test_a_greedy_widget_is_killed():
    """Address space is capped before node starts, so the allocation fails
    inside the child rather than on the host."""
    answer = _ran("""
      module.exports = () => {
        const held = [];
        for (;;) held.push(new Uint8Array(8 * 1024 * 1024));
      };
    """)
    assert answer["status"] in ("error", "killed", "timeout"), answer


def test_a_loud_widget_is_truncated_rather_than_rendered():
    """A widget that returns a hundred megabytes is a denial of service
    against the screen that draws it."""
    answer = _ran("""
      module.exports = () => "x".repeat(2 * 1024 * 1024);
    """)
    assert answer["status"] in ("ok", "killed", "error"), answer
    if answer["status"] == "ok":
        assert answer["truncated"] and answer["value"] is None, (
            "a widget's answer larger than the cap was rendered whole")


def test_a_widget_that_throws_is_reported_rather_than_hidden():
    """The ordinary case: somebody's code has a bug in it, and they need to
    read the message rather than a shrug."""
    answer = _ran("module.exports = () => { throw new Error('my mistake'); };")
    assert answer["status"] == "error"
    assert "my mistake" in answer["message"]


def test_source_longer_than_the_cap_is_refused_before_it_runs(tmp_path):
    """A limit that is enforced by the box rather than at the door is a
    limit somebody has already spent the machine's time reaching."""
    with pytest.raises(widgets.WidgetError) as caught:
        widgets.save("prof_nobody", "big",
                     "x" * (widgets.LIMITS["source_bytes"] + 1))
    assert "widgets.too_long" in str(caught.value)


def test_the_runner_refuses_rather_than_degrades_when_a_wall_is_missing(
        monkeypatch):
    """The failure this module was written around.

    A sandbox that quietly runs with three walls when it cannot build four
    still looks like a working feature, and nobody learns otherwise until the
    day it matters. When the network cut is unavailable, nothing runs.
    """
    monkeypatch.setattr(widgets.shutil, "which",
                        lambda name: None if name == "unshare"
                        else shutil.which(name))
    answer = widgets.run_source("module.exports = () => 1;")
    assert answer["status"] == "refused"
    assert answer["detail"] == "widgets.no_unshare"


def test_an_interpreter_too_old_to_build_the_wall_is_a_missing_wall(
        monkeypatch):
    """Found on a live host, not in review.

    The filesystem wall is node's own permission model, which arrives in Node
    20. `sandbox_available` asked whether *an* interpreter existed and nothing
    more, so a machine carrying Ubuntu's own Node 18 answered **available**:
    the editor opened, the run button lit, and every widget came back failed
    on a flag its author never typed.

        asked     is there an interpreter here
        mattered  is there one that can hold a widget

    A binary that cannot build the wall is the missing-wall case wearing
    different clothes, and this module's whole promise is that it refuses
    rather than running with three walls instead of four.
    """
    real = subprocess.run

    def old(argv, *a, **kw):
        if argv[1:] == ["--version"]:
            return subprocess.CompletedProcess(argv, 0, "v18.19.1\n", "")
        return real(argv, *a, **kw)                          # pragma: no cover
    monkeypatch.setattr(widgets.subprocess, "run", old)
    answer = widgets.run_source("module.exports = () => 1;")
    assert answer["status"] == "refused"
    assert answer["detail"] == "widgets.node_too_old"


def test_an_interpreter_that_will_not_say_its_version_is_too_old(monkeypatch):
    """Unreadable counts as too old. Every other reading — assume it is fine,
    raise, guess from the path — ends with a run button lit on a host where
    nothing runs, which is the whole defect."""
    real = subprocess.run

    def mute(argv, *a, **kw):
        if argv[1:] == ["--version"]:
            raise OSError("cannot execute")
        return real(argv, *a, **kw)                          # pragma: no cover
    monkeypatch.setattr(widgets.subprocess, "run", mute)
    answer = widgets.run_source("module.exports = () => 1;")
    assert answer["status"] == "refused"
    assert answer["detail"] == "widgets.node_too_old"


def test_the_floor_is_the_version_the_flag_actually_needs(monkeypatch):
    """A guard on the guard. A floor quietly lowered to 18 would let the
    defect back in with every test above still passing, because they assert
    on the refusal rather than on the number that produces it."""
    assert widgets.MIN_NODE >= 20, (
        "--experimental-permission arrives in Node 20; a floor below that "
        "admits an interpreter that cannot build the filesystem wall")
    for said, major in (("v20.0.0", 20), ("v22.22.2", 22), ("v18.19.1", 18),
                        ("not a version", 0), ("", 0)):
        monkeypatch.setattr(
            widgets.subprocess, "run",
            lambda argv, *a, **kw: subprocess.CompletedProcess(
                argv, 0, said, ""))
        assert widgets._node_major("/nowhere/node") == major, said


def test_the_refusal_is_also_checked_when_the_namespace_is_denied(monkeypatch):
    """`unshare` present and refused is a different failure from `unshare`
    absent — a container without user namespaces reaches this one, and it
    must refuse just as hard."""
    real = subprocess.run

    def denied(argv, *a, **kw):
        if argv[:2] == ["unshare", "-rn"]:
            return subprocess.CompletedProcess(argv, 1, b"", b"denied")
        return real(argv, *a, **kw)
    monkeypatch.setattr(widgets.subprocess, "run", denied)
    answer = widgets.run_source("module.exports = () => 1;")
    assert answer["status"] == "refused"
    assert answer["detail"] == "widgets.no_netns"
