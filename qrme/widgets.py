"""Small programs a person writes for their own profile, and the box they run in.

## What this is

The Studio's second half. The first is authoring — an agent that edits the
artifacts this platform already renders, through the doors that already
require owner authorization. This is the half where somebody writes *code*:
a widget is a function they wrote, stored against their profile, run on
demand against their own data.

    "For removing or creating tools things as you wish without affecting
     anybody else's app"

That sentence is the whole specification, and the load-bearing half of it is
the second clause.

## Why this is not a shell

The obvious way to give somebody coding access is a shell. This deployment
cannot offer one, and the reason is not caution in general — it is what is
on the machine. The same host holds JIM-mini's clinical captures and money
guardian statement files, PDI's tenant vaults, and every profile's
remembrance of every conversation. A shell handed to whoever signs up is a
read of all of it, arriving through a door the estate's tenant-isolation
guards were written to make impossible.

    asked     can a person run their own code here
    mattered  can a person run their own code without reaching anybody else's

So a widget runs in a box that is built to hold nothing but the widget, and
this module's job is that box.

## The four walls, and how each is actually held

Every one of these is a mechanism rather than a policy, because a policy is
a sentence and a mechanism is a failure.

**The network is cut.** `unshare -rn` puts the child in a new network
namespace with no interfaces. It needs no privilege and it is not advisory:
a `fetch` inside resolves nothing. This is the wall that matters most — a
widget that can reach the network can exfiltrate whatever it can read, and
can be told what to do by somebody who is not its author.

**The filesystem is a single directory.** Node's permission model
(`--experimental-permission --allow-fs-read`) admits exactly the widget's
own scratch directory and refuses everything else, including the read of
`/etc/passwd` that the guard for this file performs.

**There are no child processes.** The same permission model refuses
`child_process` outright, which is what stops a widget from escaping through
a program that has none of these limits.

**Time and memory are finite.** `setrlimit` caps CPU seconds and address
space in the child before it execs; a wall-clock kill catches the widget
that sleeps rather than spins. Output is truncated at a byte count, because
a widget that returns a gigabyte is a denial of service against the console
that renders it.

## The refusal that matters

If the network cut is unavailable — an unusual kernel, a container without
user namespaces — this module **refuses to run anything at all**. It does
not fall back to running the widget with three walls instead of four. A
sandbox that quietly degrades is worse than no sandbox, because the feature
still appears to work and nobody learns otherwise until it matters.

    asked     did the widget run
    mattered  did it run inside all four walls
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid

# `resource` is POSIX-only, and this module is imported by qrme.api through
# routers/studio — so a bare `import resource` at the top of the file is not
# "the sandbox is unavailable on Windows", it is *the whole API fails to
# import on Windows*. The frozen desktop backend died here on first run,
# which took the Windows installer job down, which skipped the release job,
# which is why 0.70.0 and 0.70.1 published with no installers attached at
# all — not even the macOS and Linux ones that had built.
#
#     asked     does the module import
#     mattered  does it import on every platform we ship
#
# Absent, it is the missing-wall case wearing different clothes: this module
# refuses to run anything rather than running a widget with three walls
# instead of four. So the import is allowed to fail and `sandbox_available`
# says so in a sentence, exactly like a host with no `unshare`.
try:
    import resource
except ImportError:                                 # pragma: no cover - POSIX
    resource = None

from . import db

#: Every limit the box holds a widget to, in one place so a guard can read
#: them rather than restating them. Deliberately small: a widget draws a
#: number on somebody's own page, and nothing here is a batch job.
LIMITS: dict[str, int] = {
    "wall_seconds": 5,          # the sleeping widget
    "cpu_seconds": 2,           # the spinning one
    "heap_mb": 64,              # the greedy one
    "address_space_mb": 4096,   # the backstop under the heap cap
    "output_bytes": 16 * 1024,  # the loud one
    "source_bytes": 64 * 1024,  # what a person may store as one widget
    "widgets_per_profile": 50,  # what a person may store in total
}

#: Memory is held two ways, and the reason is a failure this file already
#: had. `RLIMIT_AS` at 256MB killed node before it ran a line: V8 *reserves*
#: gigabytes of virtual address space at startup and touches almost none of
#: it, so an address-space cap sized like a memory budget is not a small
#: budget — it is a refusal to start, arriving as `killed` on every widget
#: including the ones that add two numbers.
#:
#:     asked     how much memory may a widget use
#:     mattered  which number does the kernel think it is capping
#:
#: So the real cap is V8's own heap (`--max-old-space-size`), which fails
#: *inside* the child as an ordinary out-of-memory error its author can
#: read, and `RLIMIT_AS` stays as a backstop far above the reservation.


class WidgetError(ValueError):
    """A widget that cannot be stored, or a box that cannot be built."""


# -- the box -------------------------------------------------------------------

#: The command that cuts the network. Checked for rather than assumed: the
#: absence of this binary is the one condition under which this module will
#: not run a widget at all.
_UNSHARE = "unshare"

#: The interpreter's floor, and the reason there has to be one.
#:
#: The filesystem wall is node's own permission model, reached through
#: `--experimental-permission`, which arrives in **Node 20**. On Node 18 that
#: flag is not merely ignored — it is unknown, and node exits before it runs a
#: line.
#:
#: This is a floor because of what the absence of it looked like on a real
#: host. `sandbox_available` asked `shutil.which("node")` and nothing else, so
#: a machine carrying Ubuntu's own Node 18 answered **available** — the editor
#: opened, the run button lit, and every widget came back failed on a flag its
#: author never typed.
#:
#:     asked     is there an interpreter here
#:     mattered  is there one that can hold a widget
#:
#: A missing binary and a binary that cannot build the wall are the same
#: condition wearing different clothes, and this module already says what it
#: does about that: it refuses to run rather than running with three walls
#: instead of four. The version was the one way that promise could be broken
#: without anybody being told.
MIN_NODE = 20

#: What the child is allowed to know about the machine it runs on, which is
#: nothing. Everything in this process's environment — model keys, admin
#: tokens, database paths, the collector's bearer — stays here.
#:
#: There is no `PATH`, deliberately: the interpreter is resolved to an
#: absolute path in the parent and exec'd by that path, so the child cannot
#: be steered into a different binary by a search order it can read. The
#: first draft passed `PATH=/usr/bin:/bin` and every widget failed with
#: "failed to execute node" on a machine whose node lives in /opt — which
#: was the right failure for the wrong reason, and would have become a
#: silent dependency on wherever node happened to sit.
_CHILD_ENV = {"NODE_OPTIONS": "", "HOME": "/nonexistent"}

#: The harness the child actually runs. It reads the call on stdin, hands it
#: to the widget's own exported function, and writes one JSON line back.
#: Written here rather than shipped as a file so that a guard reading this
#: module reads the whole contract.
_HARNESS = """
const fs = require("node:fs");
let call = {};
try { call = JSON.parse(fs.readFileSync(0, "utf8") || "{}"); } catch (e) {}
(async () => {
  let out;
  try {
    const widget = require("./widget.js");
    const fn = typeof widget === "function" ? widget : widget.run;
    if (typeof fn !== "function") {
      throw new Error("a widget exports a function, or an object with run()");
    }
    out = { ok: true, value: await fn(call.inputs === undefined ? {} : call.inputs) };
  } catch (e) {
    out = { ok: false, error: String((e && e.message) || e) };
  }
  process.stdout.write(JSON.stringify(out));
})();
"""


def sandbox_available() -> tuple[bool, str]:
    """Whether all four walls can be built here, and the sentence to say when
    they cannot.

    Returned rather than raised so the console can show the honest reason on
    a screen instead of a stack trace, and so the guard for the refusal can
    read the same sentence the person reads.
    """
    if resource is None:
        return False, "widgets.no_rlimits"
    if shutil.which(_UNSHARE) is None:
        return False, "widgets.no_unshare"
    node = shutil.which("node")
    if node is None:
        return False, "widgets.no_node"
    if _node_major(node) < MIN_NODE:
        return False, "widgets.node_too_old"
    probe = subprocess.run([_UNSHARE, "-rn", "true"], capture_output=True)
    if probe.returncode != 0:
        return False, "widgets.no_netns"
    return True, ""


def _node_major(node: str) -> int:
    """The interpreter's major version, or 0 when it cannot be read.

    Unreadable counts as too old on purpose. Every other answer this function
    could give — assume it is fine, raise, guess from the path — ends with a
    run button that lights on a host where nothing runs, which is the defect
    `MIN_NODE` exists for.
    """
    try:
        said = subprocess.run([node, "--version"], capture_output=True,
                              text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return 0
    found = re.match(r"v(\d+)\.", (said.stdout or "").strip())
    return int(found.group(1)) if found else 0


def _limits() -> None:                              # pragma: no cover - child
    """Set in the child between fork and exec, so the caps are already in
    force when node starts rather than argued about afterwards."""
    cpu = LIMITS["cpu_seconds"]
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
    space = LIMITS["address_space_mb"] * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (space, space))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run_source(source: str, inputs: dict | None = None) -> dict:
    """Run one widget's source in the box and answer what it said.

    The return is always a dict a screen can render: `status` is one of
    `ok`, `error`, `timeout`, `killed` or `refused`, and the sentence key
    beside it is a refusal row rather than a message built here, so that
    every way this can fail reaches a reader in their own language.
    """
    ready, why = sandbox_available()
    if not ready:
        return {"status": "refused", "detail": why, "ms": 0}

    box = tempfile.mkdtemp(prefix="qrme-widget-")
    try:
        with open(os.path.join(box, "widget.js"), "w", encoding="utf-8") as fh:
            fh.write(source)
        with open(os.path.join(box, "harness.js"), "w", encoding="utf-8") as fh:
            fh.write(_HARNESS)
        argv = [
            shutil.which(_UNSHARE), "-rn",
            shutil.which("node"),
            "--experimental-permission", f"--allow-fs-read={box}",
            f"--max-old-space-size={LIMITS['heap_mb']}",
            os.path.join(box, "harness.js"),
        ]
        started = time.monotonic()
        try:
            done = subprocess.run(
                argv, cwd=box, env=_CHILD_ENV,
                input=json.dumps({"inputs": inputs or {}}),
                capture_output=True, text=True,
                timeout=LIMITS["wall_seconds"],
                preexec_fn=_limits)
        except subprocess.TimeoutExpired:
            ms = int((time.monotonic() - started) * 1000)
            return {"status": "timeout", "detail": "widgets.timeout", "ms": ms}
        ms = int((time.monotonic() - started) * 1000)

        if done.returncode != 0 and not done.stdout.strip():
            # Killed by a limit rather than finishing: RLIMIT_CPU arrives as
            # SIGXCPU, RLIMIT_AS as an allocation failure node cannot survive.
            return {"status": "killed", "detail": "widgets.killed", "ms": ms,
                    "signal": -done.returncode if done.returncode < 0 else None}
        try:
            answer = json.loads(done.stdout[:LIMITS["output_bytes"]])
        except ValueError:
            return {"status": "killed", "detail": "widgets.no_answer", "ms": ms}
        if not answer.get("ok"):
            return {"status": "error", "detail": "widgets.threw", "ms": ms,
                    "message": str(answer.get("error", ""))[:500]}
        rendered = json.dumps(answer.get("value"))
        truncated = len(rendered) > LIMITS["output_bytes"]
        return {"status": "ok", "ms": ms, "truncated": truncated,
                "value": json.loads(rendered) if not truncated else None}
    finally:
        shutil.rmtree(box, ignore_errors=True)


# -- what a person keeps -------------------------------------------------------

def _row(row) -> dict:
    return {"id": row["id"], "name": row["name"], "source": row["source"],
            "version": row["version"], "created_at": row["created_at"],
            "updated_at": row["updated_at"]}


def save(profile_id: str, name: str, source: str,
         widget_id: str | None = None) -> dict:
    """Store a widget, or a new version of one that exists.

    Scoped to the profile at the write, not only at the door: a widget id
    from somebody else's profile is not found here rather than updated.
    """
    name = (name or "").strip()
    if not name:
        raise WidgetError("widgets.unnamed")
    if len(source or "") > LIMITS["source_bytes"]:
        raise WidgetError("widgets.too_long")
    conn = db.connect()
    now = int(time.time())
    if widget_id:
        row = conn.execute(
            "SELECT * FROM widgets WHERE id=? AND profile_id=?",
            (widget_id, profile_id)).fetchone()
        if row is None:
            raise WidgetError("widgets.no_such")
        conn.execute(
            "UPDATE widgets SET name=?, source=?, version=version+1, "
            "updated_at=? WHERE id=? AND profile_id=?",
            (name, source, now, widget_id, profile_id))
        conn.commit()
        return read(profile_id, widget_id)
    held = conn.execute("SELECT COUNT(*) c FROM widgets WHERE profile_id=?",
                        (profile_id,)).fetchone()["c"]
    if held >= LIMITS["widgets_per_profile"]:
        raise WidgetError("widgets.too_many")
    wid = f"wdg_{uuid.uuid4().hex[:12]}"
    conn.execute(
        "INSERT INTO widgets (id, profile_id, name, source, version, "
        "created_at, updated_at) VALUES (?,?,?,?,1,?,?)",
        (wid, profile_id, name, source, now, now))
    conn.commit()
    return read(profile_id, wid)


def read(profile_id: str, widget_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM widgets WHERE id=? AND profile_id=?",
        (widget_id, profile_id)).fetchone()
    if row is None:
        raise WidgetError("widgets.no_such")
    return _row(row)


def listing(profile_id: str) -> list[dict]:
    return [_row(r) for r in db.connect().execute(
        "SELECT * FROM widgets WHERE profile_id=? ORDER BY updated_at DESC",
        (profile_id,)).fetchall()]


def remove(profile_id: str, widget_id: str) -> dict:
    conn = db.connect()
    row = conn.execute("SELECT id FROM widgets WHERE id=? AND profile_id=?",
                       (widget_id, profile_id)).fetchone()
    if row is None:
        raise WidgetError("widgets.no_such")
    conn.execute("DELETE FROM widgets WHERE id=? AND profile_id=?",
                 (widget_id, profile_id))
    conn.commit()
    # `removed` is a yes/no everywhere else on this wire; the id
    # travels beside it rather than inside it.
    return {"removed": True, "widget_id": widget_id}


def run(profile_id: str, widget_id: str, inputs: dict | None = None) -> dict:
    """Run a stored widget. The record of the run is the answer itself —
    nothing about a person's own widget is kept beyond what they can see."""
    widget = read(profile_id, widget_id)
    answer = run_source(widget["source"], inputs)
    answer["widget_id"] = widget_id
    answer["version"] = widget["version"]
    return answer
