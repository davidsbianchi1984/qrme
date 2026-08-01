"""The aggregate had a ceiling on every report and none on the pile.

## The finding

`cloudgw/problems.py` is careful about each report: at most fifty problems,
short strings bounded at sixty-four characters, a day and not a timestamp, a
route template and not a path, four classes of leak refused outright. Every
one of those is a check on the *message*.

Nothing checked the *accumulation*. `Aggregate._rows` is a plain dict keyed on
`(source, app_version, platform, op, status)`. `op` is bounded by the route
tables and `platform` by reality, but **`app_version` is any short string the
caller sends** — so the key space grows with every release forever, and with
every *claimed* release, from anyone holding a posting token. Nothing evicted,
nothing expired, and the file is rewritten in full on every accepted report.

    asked     is each report small and well-formed
    mattered  is the thing they accumulate into bounded

A collector that fills its own disk stops answering `/health`, which is the
one route an orchestrator uses to decide whether to restart it — and on a
gateway that also serves the greater model, it takes inference down with it.
The diagnostic becomes the outage.

## What this round chose

Evicting, not refusing. The counters are advisory: refusing new reports to
protect old ones would preserve precisely the rows least worth keeping. The
order is `last_day` then `count`, ascending, so a failure that is still
happening outlives one that stopped — which is the ordering somebody reading
this file actually wants, because they are looking for what to fix now.

What must not happen is evicting *quietly*. A number that silently stops
growing looks exactly like a product that stopped failing.
"""

from __future__ import annotations

import json

import pytest

from cloudgw.problems import MAX_KEYS, Aggregate


def _report(version: str, ops: int, day: str = "2026-08-01") -> dict:
    return {
        "source": "qrme", "app_version": version, "platform": "win32",
        "language": "en",
        "problems": [
            {"op": f"GET /route/{i}", "status": 500, "count": 1, "day": day,
             "fingerprint": "a1b2c3d4"}
            for i in range(ops)
        ],
    }


def test_the_pile_has_a_ceiling():
    """The defect, directly: distinct versions used to grow the file forever."""
    store = Aggregate()
    for release in range(140):
        store.add(_report(f"0.{release}.0", 50))
    facts = store.describe()
    assert facts["keys"] <= MAX_KEYS, (
        f"{facts['keys']} rows held against a ceiling of {MAX_KEYS} — the "
        "aggregate is unbounded again, and the collector will fill its own "
        "disk and stop answering /health")
    assert facts["evicted"] > 0
    assert facts["capacity"] == MAX_KEYS


def test_eviction_is_reported_rather_than_silent():
    """A count that stops growing looks like a product that stopped failing.

    So the number of dropped rows is on `describe()`, which is what the boot
    banner and the ops read. Without it, a gateway at its ceiling and a
    gateway with nothing to report are the same picture.
    """
    store = Aggregate()
    assert store.describe()["evicted"] == 0
    for release in range(140):
        store.add(_report(f"0.{release}.0", 50))
    assert store.describe()["evicted"] == 140 * 50 - MAX_KEYS


def test_what_is_still_happening_outlives_what_stopped():
    """The ordering is the whole value of evicting rather than refusing.

    A row nobody has seen since March is worth less than one from yesterday,
    however large it grew before it stopped. Checked with the loud-but-old row
    deliberately given a far higher count than the quiet-but-current one, so a
    naive `-count` ordering would keep the wrong one.
    """
    store = Aggregate()
    old = {"source": "qrme", "app_version": "0.1.0", "platform": "win32",
           "language": "en",
           "problems": [{"op": "GET /ancient", "status": 500, "count": 9999,
                         "day": "2026-01-01", "fingerprint": "a1b2c3d4"}]}
    fresh = {"source": "qrme", "app_version": "0.1.0", "platform": "win32",
             "language": "en",
             "problems": [{"op": "GET /current", "status": 500, "count": 1,
                           "day": "2026-08-01", "fingerprint": "b2c3d4e5"}]}
    store.add(old)
    store.add(fresh)
    for release in range(140):
        store.add(_report(f"0.{release}.9", 50, day="2026-07-15"))

    surviving = {row["op"] for row in store.rows()}
    assert "GET /current" in surviving, (
        "a failure that is still happening was evicted. The point of this "
        "file is what to fix now.")
    assert "GET /ancient" not in surviving, (
        "the loudest row from seven months ago outlived current ones — the "
        "eviction order is on count alone, which keeps history rather than "
        "news")


def test_the_ceiling_survives_a_reload(tmp_path):
    """A restart must not read back more rows than it will hold.

    The file is written under the cap, so this is really a check that nothing
    reintroduces the pile through the door marked `path`.
    """
    store = Aggregate(tmp_path / "problems.json")
    for release in range(140):
        store.add(_report(f"0.{release}.0", 50))
    written = json.loads((tmp_path / "problems.json").read_text())
    assert len(written) <= MAX_KEYS, (
        f"{len(written)} rows on disk against a ceiling of {MAX_KEYS}")
    assert len(Aggregate(tmp_path / "problems.json").rows()) <= MAX_KEYS


@pytest.mark.parametrize("held", [0, 1, MAX_KEYS - 1])
def test_nothing_is_evicted_below_the_ceiling(held):
    """A guard on the guard: an evictor that ran unconditionally would satisfy
    every check above and throw away a collector's entire first day."""
    store = Aggregate()
    if held:
        store.add(_report("0.1.0", held))
    assert store.describe()["keys"] == held
    assert store.describe()["evicted"] == 0
