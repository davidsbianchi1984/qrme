"""An export is measured against the schema too — and drops the credentials.

0.59.9 derived the **erase** from the schema in all three products, because
the lists that stood in for it had gone stale: an operation advertised as
*every trace* reached a third of the tables. The export is the same question
turned round, and here it was worse.

## What it was

`GET /profiles/{id}/export` says *full data export — access everything,
anytime (You Own It)*. The README's capability table points at it under **You
own it / total control**. The suite gateway's GDPR Article 20 bundle is built
on it — the tandem's whole answer to *give me my data*.

It returned **six tables of sixty-six**: the profile, its sources,
relationships, messages, engagement, posts and surfaces. Everything else this
deployment holds about a profile — its clinical notes and the media behind
them, its watermarks, its homepage, its friendships, its inbox — was not in
the file a person downloaded to see what we have.

    asked     can a person delete everything we hold
    mattered  can a person see everything we hold

## Two properties, and the second is not the first

An export must be **complete** and must **not hand back a live credential**.
Those pull in opposite directions, and the honest resolution is per column
rather than per table: a row is the person's own history, and a token inside
it is a credential in whatever they do with the file.

The redaction is a **rule** rather than a list, and that is not tidiness. The
first cut was a list of exact column names and the guard below caught it on
its first run — three credential columns in tables the export now reaches,
none of them in the list. A list of columns goes stale exactly the way the
cascade's list of tables did.

## How this checks it

The same way the erase guard does — plant a row in every scoped table, ask
for the export, and look. A completeness check that only visits tables some
feature happens to fill has the same blind spot as the list it replaced.
"""

from __future__ import annotations

import ast
import inspect
import textwrap

import pytest

from qrme import common, db

from . import ratchets
from .conftest import ADULT_VERIFICATION
from .test_an_erase_is_measured_against_the_schema import (
    SUBJECT, _plant, _scoped_from_the_schema)


def test_the_export_reaches_every_table_the_schema_scopes(client, profile_id):
    """The completeness half."""
    conn = db.connect()
    planted = [t for t in _scoped_from_the_schema(conn)
               if t != "profiles" and _plant(conn, t, profile_id)]
    conn.commit()
    assert len(planted) >= ratchets.floor("erase.tables_planted"), (
        f"only planted rows in {len(planted)} tables — the planter is failing "
        "and the check below would pass on almost nothing")

    bundle = client.get(f"/profiles/{profile_id}/export")
    assert bundle.status_code == 200, bundle.text
    tables = bundle.json()["tables"]
    missing = sorted(t for t in planted if t not in tables)
    assert not missing, (
        f"{len(missing)} table(s) hold rows for this profile and are not in "
        "its export:\n    " + "\n    ".join(missing)
        + "\n  *Access everything* is a claim about the schema. Derive the "
          "export from it, as the erase cascade does.")


def test_the_export_carries_no_live_credential(client, profile_id):
    """The half that is not completeness.

    Checked against the rows that come back rather than against the redaction
    marks: the marks are a rule somebody wrote, and this file exists because
    rules somebody wrote stop matching what the schema grew.
    """
    conn = db.connect()
    for table in _scoped_from_the_schema(conn):
        if table != "profiles":
            _plant(conn, table, profile_id)
    conn.commit()

    leaked = []
    tables = client.get(f"/profiles/{profile_id}/export").json()["tables"]
    for table, rows in tables.items():
        for row in rows:
            for column in row:
                if any(mark in column.lower() for mark in
                       ("token", "secret", "password", "api_key",
                        "private_key", "grant_hash")):
                    leaked.append(f"{table}.{column}")
    assert not leaked, (
        "the export hands back live credentials:\n    "
        + "\n    ".join(sorted(set(leaked)))
        + "\n  A bundle is downloaded, mailed and copied. Carry the row and "
          "drop the column.")


def test_the_export_is_not_a_hand_written_list():
    """The structural half, which survives the next migration."""
    source = inspect.getsource(common.export_rows)
    tree = ast.parse(textwrap.dedent(source))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Tuple, ast.List)):
            continue
        words = [e.value for e in node.elts
                 if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        assert len(words) < 5, (
            f"the export carries a list of {len(words)} table names "
            f"({words[:4]}…). Read the schema instead.")
    assert "profile_scoped_tables" in source, (
        "export_rows no longer asks the schema what this profile has")


def test_the_export_and_the_erase_reach_the_same_tables(client, profile_id):
    """The symmetry, asserted rather than assumed.

    A table the erase clears and the export omits is a person who can delete
    something they were never shown. A table the export carries and the erase
    misses is the defect 0.59.9 was about. Both are one comparison.
    """
    conn = db.connect()
    planted = {t for t in _scoped_from_the_schema(conn)
               if t != "profiles" and _plant(conn, t, profile_id)}
    conn.commit()
    shown = set(client.get(f"/profiles/{profile_id}/export")
                .json()["tables"]) & planted
    assert client.delete(f"/profiles/{profile_id}").status_code == 200
    left = {t for t in planted
            if conn.execute(f"SELECT COUNT(*) FROM {t} WHERE {SUBJECT}=?",
                            (profile_id,)).fetchone()[0]}
    cleared = planted - left
    assert shown == cleared, (
        "the export and the erase disagree about this profile's data:\n"
        f"    shown but not cleared: {sorted(shown - cleared)}\n"
        f"    cleared but not shown: {sorted(cleared - shown)}")


def test_the_named_keys_survive_for_the_clients_that_read_them(client,
                                                               profile_id):
    """The four a person opening their own bundle should not have to hunt
    for, and which the suite gateway and the console both read by name."""
    body = client.get(f"/profiles/{profile_id}/export").json()
    for key in ("profile", "sources", "relationships", "messages",
                "engagement", "posts", "surfaces", "tables"):
        assert key in body, f"the export no longer carries {key!r}"


def test_the_route_is_reachable_and_owner_only(client, profile_id):
    """A person's own bundle, and nobody else's.

    The completeness work above makes this route carry sixty-six tables where
    it used to carry six, which raises the cost of the door being wrong by
    the same factor.
    """
    assert client.get(f"/profiles/{profile_id}/export").status_code == 200
    # An empty credential rather than `headers={}`: the fixture puts the
    # owner token on the client itself, and a per-request mapping is merged
    # with those rather than replacing them, so `{}` sends the token anyway.
    assert client.get(f"/profiles/{profile_id}/export",
                      headers={"authorization": ""}).status_code == 401
    other = client.post("/profiles", json={
        "owner_id": "owner-2", "kind": "self", "display_name": "Bo",
        "persona": "Another person entirely.",
        "verification": ADULT_VERIFICATION,
    })
    assert other.status_code == 201, other.text
    # The first profile's owner token is on the client; it must not open the
    # second profile's bundle.
    assert client.get(
        f"/profiles/{other.json()['id']}/export").status_code == 403
