"""Error-report intake: what a crash report may say, and what is kept of it.

`app/src/errors.ts` in all three consoles records failed requests as an
operation and a status — never a message, never an id — and sends the batch at
launch. This module is the gateway's side of that wire.

It is written the same way `screening.py` is, and for the same reason: the
gateway accumulates reports from deployments it does not control, running
builds it did not ship. One regression in the client's redaction and the pile
has real paths in it, discovered late if at all. So the intake is a
**whitelist** — five keys at the top, five per problem, each with a fixed shape
— and anything outside it is refused with a 422 rather than dropped quietly. A
client whose redaction has stopped working needs to hear about it, and the
operator of that deployment is the only person who can fix it.

Refusing is cheap here in a way it is not for contributions: a rejected error
report costs one lost diagnostic. A rejected contribution costs a user's
donated work. The asymmetry is why this file is stricter than that one.

Two things it deliberately does *not* do:

**It does not sanitize an unredacted path into a redacted one.** It could —
the pattern is right here. But then a client that stopped redacting would keep
working, and the only signal would be a server-side counter nobody reads.

**It does not keep everything it accepts.** `language` is validated and then
discarded, and no report is stored as a report: they fold into counters keyed
by (source, version, platform, operation, status). The console shows the user
the exact object that leaves their machine, and what survives here is less
than that. Every extra dimension in that key narrows a row towards a single
install, and a row that identifies one person is the thing this whole design
is arranged to avoid — so the key holds what triage actually needs and stops.
"""

from __future__ import annotations

import json
import os
import re
import threading
from pathlib import Path

TOP_LEVEL = {"source", "app_version", "platform", "language", "problems"}
PROBLEM_FIELDS = {"op", "status", "count", "day", "fingerprint"}
SOURCES = {"qrme", "jim-mini", "pdi"}

MAX_PROBLEMS = 50          # the console's own LIMIT; a larger batch is a bug
MAX_SHORT = 64             # version, platform, language

# Every pattern here ends `\Z`, never `$`. Python's `$` also matches *before* a
# trailing newline, so `$` would have accepted "Win32\n" and "GET /health\n"
# while this file's own error messages promised it did not. `\Z` is the end of
# the string and nothing else.

# `POST /profiles/{id}/chat`. The verb list is the one the products serve.
_OP = re.compile(r"^(GET|POST|PUT|PATCH|DELETE) (/[A-Za-z0-9{}_\-./]*)\Z")

# A segment that survived redaction and should not have. Mirrors ID_LIKE in
# errors.ts — deliberately, so the two can be compared when either changes.
_ID_LIKE = (
    re.compile(r"^[a-z]{2,8}_[0-9a-z]+$", re.I),
    re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}"
               r"-[0-9a-f]{4}-[0-9a-f]{12}$", re.I),
    re.compile(r"^\d+$"),
    re.compile(r"^[A-Za-z0-9_-]{24,}$"),
)

# Free-text-ish fields the browser fills in. Restricted rather than trusted:
# `navigator.platform` is a string the client controls, and a long one is
# exactly where a message would be smuggled if somebody wired one in.
_SHORT = re.compile(r"^[A-Za-z0-9 ._\-()/;:+]{1,%d}\Z" % MAX_SHORT)
_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}\Z")
_FINGERPRINT = re.compile(r"^[0-9a-f]{8}\Z")


class Rejected(Exception):
    """The report was refused. The message names the offending field, so the
    deployment that sent it can find the bug."""


def _check_short(name: str, value: object) -> str:
    if not isinstance(value, str) or not _SHORT.match(value):
        raise Rejected(
            f"{name!r} must be a short plain string (≤{MAX_SHORT} chars, no "
            f"newlines or punctuation beyond ._-()/;:+) — got {value!r}")
    return value


def screen(payload: object) -> dict:
    """Raise :class:`Rejected` unless this is exactly an error report.

    Returns the payload so a caller can validate and use in one expression.
    """
    if not isinstance(payload, dict):
        raise Rejected("an error report is an object")

    extra = sorted(set(payload) - TOP_LEVEL)
    if extra:
        raise Rejected(
            f"unknown top-level keys {extra} — this intake accepts exactly "
            f"{sorted(TOP_LEVEL)}. A new key is refused rather than ignored: "
            "silently dropping it would let a client start sending content "
            "and never learn that nobody wanted it.")
    missing = sorted(TOP_LEVEL - set(payload))
    if missing:
        raise Rejected(f"missing keys {missing}")

    if payload["source"] not in SOURCES:
        raise Rejected(f"unknown source {payload['source']!r} — expected one "
                       f"of {sorted(SOURCES)}")
    for key in ("app_version", "platform", "language"):
        _check_short(key, payload[key])

    problems = payload["problems"]
    if not isinstance(problems, list):
        raise Rejected("'problems' must be a list")
    if len(problems) > MAX_PROBLEMS:
        raise Rejected(
            f"{len(problems)} problems in one report; the console caps its "
            f"buffer at {MAX_PROBLEMS}, so a larger batch means the sender is "
            "not the console this intake is for")

    for i, problem in enumerate(problems):
        _screen_problem(f"problems[{i}]", problem)
    return payload


def _screen_problem(where: str, problem: object) -> None:
    if not isinstance(problem, dict):
        raise Rejected(f"{where} must be an object")
    extra = sorted(set(problem) - PROBLEM_FIELDS)
    if extra:
        raise Rejected(
            f"{where} has unknown fields {extra} — a recorded failure carries "
            f"exactly {sorted(PROBLEM_FIELDS)}, and a field like 'message' or "
            "'detail' appearing here is the leak this intake exists to catch")

    match = _OP.match(problem.get("op") or "")
    if not match:
        raise Rejected(
            f"{where}.op must read like 'POST /profiles/{{id}}/chat' — got "
            f"{problem.get('op')!r}")

    for segment in match.group(2).split("/"):
        if segment and any(p.match(segment) for p in _ID_LIKE):
            raise Rejected(
                f"{where}.op contains {segment!r}, which looks like an "
                "identifier rather than a route name. The console redacts "
                "these before storing them, so this build's redaction is not "
                "working. Refused rather than redacted here, because "
                "redacting here would hide that from the only people who can "
                "fix it.")

    status = problem.get("status")
    if not isinstance(status, int) or isinstance(status, bool) \
            or not 0 <= status <= 599:
        raise Rejected(f"{where}.status must be an HTTP status, or 0 when the "
                       f"request never reached a server — got {status!r}")
    count = problem.get("count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise Rejected(f"{where}.count must be a positive integer — got "
                       f"{count!r}")
    if not _DAY.match(str(problem.get("day", ""))):
        raise Rejected(f"{where}.day must be an ISO date with no time of day; "
                       "a timestamp to the second is a movement record")
    if not _FINGERPRINT.match(str(problem.get("fingerprint", ""))):
        raise Rejected(f"{where}.fingerprint must be eight hex characters")


class Aggregate:
    """Counters, not reports.

    Keyed by (source, app_version, platform, op, status). No row records that
    a particular install sent anything, how often it launched, or when beyond
    the day — so the file this writes is one a person could read over your
    shoulder without learning anything about anybody.

    That is also why it is a plain JSON file rather than a PDI vault, which is
    the opposite of the choice `store.py` makes for contributions and worth
    saying out loud: contributions are people's own words and get sealed;
    these counters have no owner to protect. Encrypting them would look
    careful and mean nothing.
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._lock = threading.Lock()
        self._rows: dict[str, dict] = {}
        if path and path.exists():
            try:
                self._rows = json.loads(path.read_text("utf-8"))
            except (OSError, ValueError):
                self._rows = {}

    def describe(self) -> dict:
        return {"configured": self.path is not None,
                "keys": len(self._rows),
                "note": None if self.path else
                        "no CLOUDGW_PROBLEMS_PATH set — reports are validated "
                        "and counted in memory only, and go when this process "
                        "does"}

    def add(self, payload: dict) -> int:
        """Fold a screened report in. Returns how many failures it carried."""
        folded = 0
        with self._lock:
            for problem in payload["problems"]:
                key = "\t".join((payload["source"], payload["app_version"],
                                 payload["platform"], problem["op"],
                                 str(problem["status"])))
                row = self._rows.setdefault(key, {
                    "source": payload["source"],
                    "app_version": payload["app_version"],
                    "platform": payload["platform"],
                    "op": problem["op"],
                    "status": problem["status"],
                    "count": 0,
                    "first_day": problem["day"],
                    "last_day": problem["day"],
                })
                row["count"] += problem["count"]
                row["first_day"] = min(row["first_day"], problem["day"])
                row["last_day"] = max(row["last_day"], problem["day"])
                folded += problem["count"]
            self._flush()
        return folded

    def rows(self) -> list[dict]:
        """Worst first — the point of collecting this is to know what to fix."""
        return sorted(self._rows.values(), key=lambda r: -r["count"])

    def _flush(self) -> None:
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._rows, indent=1), "utf-8")
            tmp.replace(self.path)
        except OSError:
            # A gateway that cannot write its diagnostics is still a gateway.
            # Losing a counter must never cost somebody an inference call.
            pass


def aggregate_from_env() -> Aggregate:
    path = os.environ.get("CLOUDGW_PROBLEMS_PATH", "").strip()
    return Aggregate(Path(path) if path else None)
