"""The relationship could be set and could not be read.

`PUT /profiles/{id}/relationships/{interactor_id}` was the only door the
relationship ever had. There was no GET — `get_relationship` exists, but as
a helper the PUT handler calls on its way out, not as a route. So an owner
could declare that a profile calls somebody *kiddo* and speaks to them
*playfully*, and then had no way to ask what the standing currently was
short of writing again and reading what came back.

    asked     can the relationship be set
    mattered  can either of you read what it is

A form that opens blank over a value that already exists is the visible
half. The worse half is that the only way to look was to overwrite, so
checking cost you the thing you were checking.

It rides in `GET …/memory/{interactor_id}/account` rather than in a route
of its own. That payload is already the pair's own account of itself, under
the same `require_owner_or_interactor`, and a new route in this codebase is
four doorless rows across four clients before it is anything else.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _account(client, profile_id, interactor_id):
    r = client.get(f"/profiles/{profile_id}/memory/{interactor_id}/account")
    assert r.status_code == 200, r.text
    return r.json()


def test_a_pair_with_no_standing_says_so_rather_than_missing_the_key(
        client, profile_id, interactor_id):
    """`None`, not an absent field. A client reading `acc.relationship` has
    to be able to tell 'nobody set one' from 'this build is older than the
    fold', and a missing key answers both the same way."""
    acc = _account(client, profile_id, interactor_id)
    assert "relationship" in acc
    assert acc["relationship"] is None


def test_what_was_written_can_be_read_back(client, profile_id, interactor_id):
    """The defect, driven: set it, then read it without writing again."""
    client.put(f"/profiles/{profile_id}/relationships/{interactor_id}",
               json={"relationship_type": "grandchild", "nickname": "kiddo",
                     "tone": "playful", "boundaries": ["no money talk"]})

    rel = _account(client, profile_id, interactor_id)["relationship"]
    assert rel["relationship_type"] == "grandchild"
    assert rel["nickname"] == "kiddo"
    assert rel["tone"] == "playful"
    # Boundaries are stored as a JSON string and were the field most likely
    # to reach a client as one — a list that arrives as `'["no money talk"]'`
    # renders as its own punctuation.
    assert rel["boundaries"] == ["no money talk"]


def test_reading_it_does_not_change_it(client, profile_id, interactor_id):
    """The reason this matters more than convenience: before the fold, the
    only way to look was to PUT, so a client that wanted to *show* the
    standing had to overwrite it first."""
    client.put(f"/profiles/{profile_id}/relationships/{interactor_id}",
               json={"relationship_type": "neighbour", "nickname": "Sam"})
    first = _account(client, profile_id, interactor_id)["relationship"]
    for _ in range(3):
        again = _account(client, profile_id, interactor_id)["relationship"]
        assert again == first


def test_the_counts_it_used_to_carry_are_still_there(
        client, profile_id, interactor_id):
    """A fold is only free if it costs the payload nothing. This is the
    memory account first and the relationship second."""
    acc = _account(client, profile_id, interactor_id)
    for key in ("profile_name", "remembers", "folded_turns", "recent_turns",
                "first_at", "last_at"):
        assert key in acc, key


def test_it_did_not_become_a_route():
    """Structural, and the point of the whole approach: the fold exists so
    four clients do not each grow a fifth binding. If somebody adds the
    obvious GET later, the doorless manifests are what will notice — but by
    then the console will already be reading the wrong one of two shapes.
    """
    src = (REPO / "qrme" / "routers" / "interaction.py").read_text()
    tree = ast.parse(src)
    gets = [
        d.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        for d in node.decorator_list
        if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
        and d.func.attr == "get" and d.args
        and isinstance(d.args[0], ast.Constant)
    ]
    assert not [p for p in gets if "/relationships/" in p], (
        "the relationship grew a GET of its own — the account payload "
        "already carries it, and two shapes for one fact is the drift this "
        "codebase keeps finding")


def test_the_console_reads_it_from_the_account(client):
    """The binding is not a door unless something opens it. The rail's
    relationship panel is the only reader, and it reads through
    `memoryAccount` — which is what makes the fold a door rather than a
    field nobody fetches."""
    rail = (REPO / "app" / "src" / "TalkRail.tsx").read_text()
    assert "memoryAccount" in rail
    assert ".relationship" in rail
