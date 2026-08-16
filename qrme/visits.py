"""The far end that sees you twice.

Offline mode answers *did anything leave this host*. Nothing answered *who
has watched us leave, and how often*.

:func:`qrme.offline.allow` sits on every outbound path in the package — a
structural guard in ``test_nothing_leaves_the_host.py`` walks the AST and
holds every socket site to consulting it — and it was a pure yes-or-no. It saw
the host, decided, and forgot. So a deployment could say with certainty that a
given excursion was sanitized, and could not say that the same far host had
now watched this household leave fourteen times.

    asked     did anything leave the host
    mattered  who has watched us leave, and how often

That is the case a scrubber does not cover. Strip every field from a single
request and it tells the far end nothing. Send the stripped request every
Tuesday for a year from the same address and the far end has a subject: not a
name, but a rhythm, a set of interests, and a count — and the fifteenth visit
is read against the previous fourteen rather than on its own.

## What is recorded, and what deliberately is not

**The host, never the path.** ``example.com``, not
``example.com/@grandpa-joe``. In the scrape case the path *is* the subject's
handle, and a ledger holding it would be a second copy of the private thing,
sitting in a table nobody thinks of as private. A host is enough to answer the
question this module exists to answer.

**Local is not far.** Loopback, the LAN, the on-prem vault, the Ollama daemon
— :func:`qrme.offline.is_local` already draws that line for the refusal, and
the ledger uses the same one. A machine on this side of the wire is not
watching anybody.

**On whose behalf, when that is knowable.** A profile-page fetch is a
profile's. The mail server, the vault and the cloud gateway are the
deployment's own plumbing and belong to nobody in particular; they record
``NULL`` and say so, and :data:`UNATTRIBUTED` is the written-down list of
which ones those are.

## Two readers, two shapes

The **owner** sees the hosts their own profiles reached. That is theirs.

The **operator** sees the deployment's totals per host, and no profile at all
— because the deployment-wide view is precisely the one that would tell owner
A that owner B's agent reads a particular forum, and a tool built to measure
correlation exposure must not be a way to correlate people.

## The lever

A ledger with no lever is a report. :func:`stand_down` marks a host as one
this profile no longer visits, and the refusal happens *at the socket* rather
than at the route above it — the same argument ``scrape.fetch`` makes for
putting its offline check where the connection opens: a second caller added
tomorrow inherits it instead of remembering it.
"""

from __future__ import annotations

import time
import urllib.parse
from datetime import datetime, timedelta, timezone

from . import db

#: How many visits make a far host a *persistent* one rather than a one-off.
#: Not a magic number about risk — a threshold for when the surface starts
#: saying so out loud, chosen low because the interesting moment is early.
PERSISTENT_AFTER = 5

#: Detail older than this stops existing. What remains is a per-host count and
#: the first and last time, which is what the question needs; the individual
#: timestamps are a movement log, and keeping one forever to warn people about
#: being tracked would be its own joke.
HORIZON_DAYS = 90

#: Outbound paths that legitimately cannot name a profile, and why. This is
#: the recorded half of the guard in
#: ``test_the_far_end_that_sees_you_twice.py``: a new socket either attributes
#: its visit to a profile or is written down here with a reason somebody read.
UNATTRIBUTED = {
    "the PDI vault": "the deployment's own storage, reached for every profile "
                     "and on behalf of none in particular",
    "sending mail": "one SMTP relay serves the whole deployment; a per-message "
                    "attribution would be a per-recipient one",
    "the cloud gateway": "the gateway is the deployment's account, not a "
                         "profile's",
    "the model provider": "inference is asked for by the deployment's "
                          "configured provider; the excursion above it records "
                          "its own brief and redaction count",
    "the local model daemon": "loopback — never recorded at all, see is_local",
    "the sign-in provider": "reached before anybody is a profile yet",
}


def host_of(url: str | None) -> str | None:
    """Just the host. The path is the caller's business and never ours."""
    return urllib.parse.urlsplit(url or "").hostname


#: When the horizon was last enforced in this process. Folding on *write*
#: rather than on read, because a horizon that only holds when somebody looks
#: is not a horizon — the detail would sit there indefinitely on a deployment
#: nobody audits, which is precisely the deployment it matters on.
_last_fold = 0.0
_FOLD_EVERY = 3600.0


def record(host: str | None, what: str, profile_id: str | None = None) -> None:
    """One visit. Best-effort by construction: a ledger that could break an
    outbound call would be a worse thing than a gap in a ledger, so every
    failure here is swallowed rather than raised."""
    if not host:
        return
    try:
        conn = db.connect()
        conn.execute(
            "INSERT INTO outbound_visits (id, profile_id, host, what, at)"
            " VALUES (?,?,?,?,?)",
            (db.new_id("vst"), profile_id, host.lower(), what, db.utcnow()))
        conn.commit()
        global _last_fold
        now = time.monotonic()
        if now - _last_fold > _FOLD_EVERY:
            _last_fold = now
            fold_old()
    except Exception:                                        # noqa: BLE001
        # Recording is a courtesy to the person reading later. It is never
        # allowed to be the reason a fetch fails.
        pass


def stood_down(profile_id: str | None, host: str | None) -> bool:
    """Has this profile said it no longer visits this host?

    A visit with no profile behind it cannot be stood down by one — see
    :data:`UNATTRIBUTED`. Saying so here, rather than letting the lookup
    quietly match nothing, is what keeps the control from being a dead one.
    """
    if not profile_id or not host:
        return False
    return db.connect().execute(
        "SELECT 1 FROM visit_standdowns WHERE profile_id=? AND host=?",
        (profile_id, host.lower())).fetchone() is not None


def stand_down(profile_id: str, host: str) -> dict:
    conn = db.connect()
    conn.execute(
        "INSERT OR IGNORE INTO visit_standdowns (profile_id, host, at)"
        " VALUES (?,?,?)", (profile_id, host.lower(), db.utcnow()))
    conn.commit()
    return {"host": host.lower(), "stood_down": True}


def lift(profile_id: str, host: str) -> dict:
    conn = db.connect()
    conn.execute("DELETE FROM visit_standdowns WHERE profile_id=? AND host=?",
                 (profile_id, host.lower()))
    conn.commit()
    return {"host": host.lower(), "stood_down": False}


def _row(r, profile_id: str | None = None) -> dict:
    """One far host, folded. `persistent` is the sentence this module exists
    to be able to say: not *you visited this*, but *this one has seen you
    enough times to know you*."""
    times = int(r["times"])
    return {
        "host": r["host"],
        "times": times,
        "first_seen": r["first_seen"],
        "last_seen": r["last_seen"],
        "reasons": sorted(set((r["reasons"] or "").split("\x1f")) - {""}),
        "persistent": times >= PERSISTENT_AFTER,
        "stood_down": stood_down(profile_id, r["host"]),
    }


_FOLD = ("SELECT host, COUNT(*) AS times, MIN(at) AS first_seen,"
         " MAX(at) AS last_seen, GROUP_CONCAT(what, char(31)) AS reasons"
         " FROM outbound_visits")


def for_profile(profile_id: str) -> list[dict]:
    """Where this profile's agent has been. The owner's own, and only theirs."""
    rows = db.connect().execute(
        _FOLD + " WHERE profile_id=? GROUP BY host ORDER BY times DESC, host",
        (profile_id,)).fetchall()
    return [_row(r, profile_id) for r in rows]


def across_the_deployment() -> list[dict]:
    """Every far host this deployment has reached, and how often.

    **No profile appears in this answer, at any depth.** This is the view that
    shows real correlation exposure — one address, many households, one far
    host seeing all of it — and it is exactly the view that would otherwise
    tell one owner what another owner's agent reads. Counts, hosts, reasons.
    """
    rows = db.connect().execute(
        _FOLD + " GROUP BY host ORDER BY times DESC, host").fetchall()
    out = []
    for r in rows:
        seen = _row(r)
        seen.pop("stood_down")     # a stand-down is a profile's; there is none here
        out.append(seen)
    return out


def fold_old() -> int:
    """Drop visit detail past the horizon, keeping nothing but the fact that
    it happened. Returns how many rows went.

    The counts survive because the earliest visit is what makes the pattern
    legible; the individual timestamps do not, because a log of when a
    household's agent goes online is the thing this module warns about, and
    keeping one to write the warning would be indefensible.
    """
    cutoff = (datetime.now(timezone.utc)
              - timedelta(days=HORIZON_DAYS)).isoformat()
    conn = db.connect()
    # One survivor per (profile, host, reason) keeps the shape of the history
    # — first seen, and that it was persistent — without the beat of it.
    conn.execute(
        "DELETE FROM outbound_visits WHERE at < ? AND id NOT IN ("
        "  SELECT MIN(id) FROM outbound_visits WHERE at < ?"
        "  GROUP BY profile_id, host, what)", (cutoff, cutoff))
    gone = conn.total_changes
    conn.commit()
    return gone
