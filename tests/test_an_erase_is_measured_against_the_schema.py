"""An erase is measured against the schema, not against a list somebody wrote.

## What it was

`DELETE /profiles/{id}` says *delete the profile and every trace of it —
anytime*. It named twenty-four tables in a tuple. This schema has
**sixty-six** with a `profile_id` column, so the delete left forty-two
standing:

    anonymous_pictures   clinical_notes   media          media_watermarks
    homepages            friendships      inbox_events   displays
    embodiments          excursions       campaigns      game_sessions
    departments          delegated_workflows             environment_context
    …and twenty-eight more

`clinical_notes` and `media` are the sharp ones: a clinical note and the
photographs behind it, belonging to a profile the API answers 404 for.
`media_watermarks` is the identifier that ties a rendered likeness back to
the person it was made from.

The sibling vault had already found and fixed the same shape, and its fix did
not travel. Its docstring says why in one line: *a migration that adds a table
is covered by writing it, not by remembering this function.*

    asked     did we delete what the handler names
    mattered  did we delete what the schema holds

## How this checks it

By writing a row into **every** scoped table, deleting, and looking. Not by
exercising features until rows appear: the tables a test can reach through the
API are the tables somebody thought to wire, which is the same blind spot as
the list. The rows are synthetic and go in through SQL — the question here is
whether the cascade reaches a table, and a row is a row.

## The test does not borrow the reader it is checking

The first cut planted rows in `profile_scoped_tables()` — the function under
test. Narrowing the cascade narrowed the planting with it, so an injected
hand-written list produced *a blind reader* rather than *forty-two surviving
tables*. It reads the schema itself now.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from pathlib import Path

import pytest

from . import ratchets

from qrme import common, db
from qrme.routers import profiles as handler

#: The column that names the subject, per table shape.
SUBJECT = "profile_id"


def _columns(conn, table: str) -> list[tuple]:
    return list(conn.execute(f"PRAGMA table_info({table})"))


def _filler(kind: str):
    kind = (kind or "").upper()
    if "INT" in kind:
        return 0
    if any(k in kind for k in ("REAL", "FLOA", "DOUB", "NUM", "DEC")):
        return 0.0
    if "BLOB" in kind:
        return b""
    return ""


def _plant(conn, table: str, subject: str) -> bool:
    """Put one row naming `subject` into `table`. False if it will not take."""
    names, values = [], []
    for cid, name, kind, notnull, default, pk in _columns(conn, table):
        if name == SUBJECT:
            names.append(name)
            values.append(subject)
        elif name == "id":
            names.append(name)
            values.append(f"erase-probe-{table}")
        elif notnull and default is None and not pk:
            names.append(name)
            values.append(_filler(kind))
    marks = ",".join("?" for _ in names)
    try:
        conn.execute(f"INSERT INTO {table} ({','.join(names)}) VALUES ({marks})",
                     values)
        return True
    except Exception:
        return False


def plantable() -> int:
    """How many scoped tables will take a probe row.

    Registered as a floor of its own: the planter is the half of this file
    that can go quiet without the sweep noticing — every insert failing looks
    exactly like a schema with nothing in it.
    """
    conn = db.connect()
    return sum(1 for t in _scoped_from_the_schema(conn)
               if _plant(conn, t, "erase-probe-count"))


def scoped_tables() -> list[str]:
    """The registry's reader: this file's own view of the schema."""
    return _scoped_from_the_schema(db.connect())


def _scoped_from_the_schema(conn) -> list[str]:
    """The tables this test will plant in — read here, not borrowed.

    Deliberately not `common.profile_scoped_tables()`. A test that asks the code
    under test which tables to check plants rows only where that code already
    looks, so narrowing the cascade narrows the test with it and the run stays
    green. Found by injecting the old hand-written list: the check reported a
    blind *reader* rather than forty-three surviving tables.
    """
    out = []
    for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'").fetchall():
        if SUBJECT in {c[1] for c in _columns(conn, row[0])}:
            out.append(row[0])
    return sorted(out)


def test_the_erase_reaches_every_table_the_schema_scopes(client, profile_id):
    """The whole check, and it needs no feature to be wired to find a gap.

    Driven over HTTP rather than by calling the handler: the delete is a
    route with an owner check in front of it, and the thing being audited is
    what a person pressing *delete everything* actually gets.
    """
    conn = db.connect()
    subject = profile_id
    planted = [t for t in _scoped_from_the_schema(conn)
               if t != "profiles" and _plant(conn, t, subject)]
    conn.commit()
    assert len(planted) >= ratchets.floor("erase.tables_planted"), (
        f"only planted rows in {len(planted)} tables — the planter is failing "
        "on this schema and the check below would pass on almost nothing")

    gone = client.delete(f"/profiles/{subject}")
    assert gone.status_code == 200, gone.text

    left = []
    for table in planted:
        n = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {SUBJECT}=?", (subject,)
        ).fetchone()[0]
        if n and table not in common.ERASE_KEEPS:
            left.append(table)
    assert not left, (
        f"{len(left)} table(s) still hold rows for a user who asked to be "
        "forgotten:\n    " + "\n    ".join(sorted(left))
        + "\n  The handler says *every trace*. Derive the cascade from the "
          "schema, or put the table in ERASE_KEEPS with the reason.")


def test_the_cascade_is_not_a_hand_written_list():
    """The structural half.

    A behavioural check passes the moment the list is long enough *today*,
    and says nothing about the table added next week. This is the part that
    survives the next migration.
    """
    source = inspect.getsource(handler.delete_profile)
    # `cleandoc` normalises a docstring, not a function body — it strips the
    # `def` line's indentation and leaves the rest, which does not parse.
    tree = ast.parse(textwrap.dedent(source))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Tuple, ast.List)):
            continue
        words = [e.value for e in node.elts
                 if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        assert len(words) < 5, (
            f"the cascade carries a list of {len(words)} table names "
            f"({words[:4]}…). Every list of this shape in the estate has gone "
            "stale; read the schema instead.")
    assert "profile_scoped_tables" in source, (
        "delete_profile no longer asks the schema which tables to clear")


def test_the_scoped_reader_sees_the_whole_schema(client):
    """A reader that goes blind reports an erase with nothing left to do."""
    conn = db.connect()
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%'").fetchall()]
    scoped = common.profile_scoped_tables()
    assert len(scoped) >= ratchets.floor("erase.scoped_tables"), (
        f"{len(scoped)} scoped tables out of {len(tables)} — the schema "
        "reader has stopped matching, and an empty cascade deletes nothing "
        "while reporting success")
    assert set(scoped) <= set(tables)


def test_what_is_kept_is_named_and_reasoned():
    """`ERASE_KEEPS` is the only way a table survives, so it is the only place
    a promise is broken. Empty today; a row in it is a deliberate edit that a
    reader can see and argue with."""
    assert isinstance(common.ERASE_KEEPS, frozenset)
    for table in common.ERASE_KEEPS:
        assert table in common.profile_scoped_tables(), (
            f"{table!r} is kept from an erase and is not in the schema")
