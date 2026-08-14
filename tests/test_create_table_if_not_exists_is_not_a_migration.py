"""The schema said the column was there; the database on disk disagreed.

`_SCHEMA` is entirely `CREATE TABLE IF NOT EXISTS`, which on a database that
already has the table does *nothing at all*. So a column added to the
declaration appears on fresh installs and on no existing one — including
every live deployment, and the developer's own `qrme.db`.

Nothing had ever depended on that until `interactors.account_id`, which is
indexed. The index named a column the old table did not have, so
`executescript` raised, and `connect()` raised with it: not one broken
feature but the backend refusing to open its database at all.

    asked     is the column in the schema
    mattered  is it in the database this deployment already has

It passed three thousand five hundred and eleven tests, because every
fixture builds a fresh file. The two that caught it were the two that did
not.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

from qrme import db

REPO = Path(__file__).resolve().parents[1]


def _tables(script: str) -> dict[str, str]:
    """{table: its column block} from the declared schema."""
    out = {}
    for m in re.finditer(
            r"CREATE TABLE IF NOT EXISTS (\w+) \((.*?)\n\);", script, re.S):
        out[m.group(1)] = m.group(2)
    return out


def _declared_columns(block: str) -> set[str]:
    names = set()
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        m = re.match(r"(\w+)\s", line)
        if m and m.group(1).upper() not in {
                "PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT"}:
            names.add(m.group(1))
    return names


def test_an_old_database_opens(tmp_path, monkeypatch):
    """The defect, directly: a database built before the column existed, then
    opened by today's code. This is what every deployment does on deploy."""
    old = tmp_path / "old.db"
    conn = sqlite3.connect(old)
    # The `interactors` table exactly as it shipped, without `account_id`.
    conn.executescript("""
        CREATE TABLE accounts (id TEXT PRIMARY KEY, email TEXT);
        CREATE TABLE interactors (
            id TEXT PRIMARY KEY, display_name TEXT NOT NULL,
            birthdate TEXT, quiet_start INTEGER, quiet_end INTEGER,
            created_at TEXT NOT NULL);
    """)
    conn.execute("INSERT INTO interactors (id, display_name, created_at)"
                 " VALUES ('usr_old', 'Sam', '2020-01-01T00:00:00Z')")
    conn.commit()
    conn.close()

    monkeypatch.setenv("QRME_DB", str(old))
    db.reset()
    try:
        live = db.connect()          # this raised OperationalError
        cols = {r[1] for r in live.execute("PRAGMA table_info(interactors)")}
        assert "account_id" in cols
        # And the row that was already there survived, unattached.
        row = live.execute("SELECT account_id FROM interactors WHERE id=?",
                           ("usr_old",)).fetchone()
        assert row["account_id"] is None
    finally:
        db.reset()


def test_every_added_column_is_actually_in_the_schema():
    """A record that has drifted from the declaration is worse than none: it
    would add a column the schema no longer wants, on every existing
    database, forever."""
    tables = _tables(db._SCHEMA)
    for table, column, _decl in db._ADDED_COLUMNS:
        assert table in tables, f"{table} is not declared"
        assert column in _declared_columns(tables[table]), (
            f"{table}.{column} is recorded as an addition but the schema does "
            "not declare it")


def test_the_migration_is_additive_only():
    """`ADD COLUMN` is the one alteration SQLite does cheaply and safely.
    Anything that rewrites or drops belongs in a considered migration with a
    backup, not in a path that runs on every connection."""
    source = (REPO / "qrme" / "db.py").read_text()
    body = source[source.index("def _add_missing_columns"):
                  source.index("def connect(")]
    lowered = body.lower()
    for forbidden in ("drop column", "drop table", "rename to", "delete from"):
        assert forbidden not in lowered, f"{forbidden!r} in the startup path"


def test_it_runs_before_the_schema_script():
    """Order is the whole fix. The script's own indexes may name these
    columns — which is exactly how this was found — so the column has to
    exist before `executescript` runs, not after."""
    source = (REPO / "qrme" / "db.py").read_text()
    connect = source[source.index("def connect("):]
    add = connect.index("_add_missing_columns(conn)")
    script = connect.index("conn.executescript(_SCHEMA)")
    assert add < script


def test_a_fresh_database_needs_no_migration(tmp_path, monkeypatch):
    """The loop must be a no-op on a file that does not exist yet: the tables
    are absent, and the script creates them with their columns in place."""
    monkeypatch.setenv("QRME_DB", str(tmp_path / "fresh.db"))
    db.reset()
    try:
        live = db.connect()
        cols = {r[1] for r in live.execute("PRAGMA table_info(interactors)")}
        assert "account_id" in cols
    finally:
        db.reset()


@pytest.mark.parametrize("table,column,_decl", db._ADDED_COLUMNS)
def test_each_addition_survives_a_second_open(tmp_path, monkeypatch,
                                              table, column, _decl):
    """Idempotent. `connect()` runs on every thread that has not connected
    yet, and a second `ADD COLUMN` for the same name is an error."""
    monkeypatch.setenv("QRME_DB", str(tmp_path / "twice.db"))
    db.reset()
    try:
        db.connect()
        db.reset()
        live = db.connect()
        cols = {r[1] for r in live.execute(f"PRAGMA table_info({table})")}
        assert column in cols
    finally:
        db.reset()
