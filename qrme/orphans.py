"""What the old delete left behind, for deployments that ran it.

0.59.9 derived the profile delete from the schema. Before that it ran off a
list of twenty-four table names while the schema had grown to sixty-six, so
every profile deleted on a pre-0.59.9 build left **forty-two tables
standing** — `clinical_notes` and the `media` behind them,
`media_watermarks`, `anonymous_pictures`, `homepages`, `friendships`, and the
`inbox_events` that record what the platform did to somebody.

Fixing the delete fixes the next one. It does not reach back. A deployment
that has been running since March holds rows for profiles somebody ended, and
nothing in the running product will ever look at them again: the `profiles`
row is gone, so the API answers 404, so no code path visits those rows.

    asked     does the delete work now
    mattered  what did it leave the last time it did not

This module is that reach-back, and it is deliberately a **separate command**
rather than something the app runs at startup. A sweep that deletes rows is
not a thing to do silently on somebody else's data on boot.

## What it will and will not touch

The scope is exactly what the profile delete would have cleared had the
profile still existed — `common.profile_scoped_tables()` minus
`common.ERASE_KEEPS`. It shares that reader with the handler on purpose: this
is the same cascade applied retroactively, and a second opinion about which
tables are in scope would be a second thing to keep in step.

A row is an orphan only when its `profile_id` names a profile that is **not
in `profiles`**. Rows with a NULL or empty subject are left alone: they are
not the residue of a deleted profile, they are something else, and this
command does not get to decide what.

## Dry by default

`survey()` reads. `sweep(apply=True)` writes, and nothing calls it without
that argument. The command line mirrors it::

    python -m qrme.orphans              # count them, change nothing
    python -m qrme.orphans --apply      # clear them
    python -m qrme.orphans --json       # the same survey, machine-readable
"""

from __future__ import annotations

import json
import sys

from . import common, db

#: The identity table. A `profile_id` naming no row here belongs to nobody.
LIVING = "profiles"


def _living(conn) -> set[str]:
    return {r[0] for r in conn.execute(f"SELECT id FROM {LIVING}").fetchall()}


def _in_scope() -> list[str]:
    """The tables the cascade reaches."""
    return [t for t in common.profile_scoped_tables()
            if t not in common.ERASE_KEEPS and t != LIVING]


def survey() -> dict:
    """Count rows belonging to profiles this deployment no longer has.

    Returns ``{"rows": int, "tables": {name: count}, "subjects": [id, ...]}``.
    ``tables`` carries only the tables that hold something, so an empty
    mapping is the answer a healthy deployment gives.
    """
    conn = db.connect()
    living = _living(conn)
    tables: dict[str, int] = {}
    subjects: set[str] = set()

    for table in _in_scope():
        rows = conn.execute(
            f"SELECT profile_id, COUNT(*) FROM {table} "
            "WHERE profile_id IS NOT NULL AND profile_id != '' "
            "GROUP BY profile_id").fetchall()
        stranded = [(pid, n) for pid, n in rows if pid not in living]
        if stranded:
            tables[table] = sum(n for _, n in stranded)
            subjects.update(pid for pid, _ in stranded)

    return {"rows": sum(tables.values()), "tables": tables,
            "subjects": sorted(subjects)}


def sweep(apply: bool = False) -> dict:
    """Survey, and — only when asked — delete what the survey found.

    The deletion repeats the survey's own predicate rather than working from
    the ids it collected: between the two, a row could have been written for
    a profile that has since been created, and `NOT IN (SELECT id FROM
    profiles)` is true of exactly the rows that are still stranded at the
    moment the statement runs.
    """
    found = survey()
    found["applied"] = bool(apply)
    if not apply or not found["rows"]:
        return found

    conn = db.connect()
    for table in _in_scope():
        conn.execute(
            f"DELETE FROM {table} WHERE profile_id IS NOT NULL "
            f"AND profile_id != '' AND profile_id NOT IN "
            f"(SELECT id FROM {LIVING})")
    conn.commit()
    return found


def _report(found: dict) -> str:
    if not found["rows"]:
        return ("Nothing stranded: every profile-scoped row belongs to a "
                "profile this deployment still has.")
    verb = "Cleared" if found.get("applied") else "Found"
    lines = [f"{verb} {found['rows']} row(s) across {len(found['tables'])} "
             f"table(s), belonging to {len(found['subjects'])} profile(s) "
             "that no longer exist:"]
    for table, n in sorted(found["tables"].items(), key=lambda kv: -kv[1]):
        lines.append(f"    {n:>7}  {table}")
    if not found.get("applied"):
        lines.append("")
        lines.append("Nothing was changed. Re-run with --apply to clear them.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    unknown = [a for a in argv if a not in ("--apply", "--json")]
    if unknown:
        print(f"unknown argument(s): {' '.join(unknown)}\n"
              "usage: python -m qrme.orphans [--apply] [--json]",
              file=sys.stderr)
        return 2
    found = sweep(apply="--apply" in argv)
    print(json.dumps(found, indent=2) if "--json" in argv else _report(found))
    return 0


if __name__ == "__main__":                                   # pragma: no cover
    raise SystemExit(main())
