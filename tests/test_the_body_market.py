"""The catalogue of bodies, including the ones nobody can buy yet.

An owner choosing a body is shopping. A catalogue listing only what is already
on sale answers a narrower question than the one being asked — *what exists* —
and leaves somebody to find out elsewhere that the machine they wanted ships
next year.

So every row carries ``availability``:

``shipping``  buyable now by somebody, developer- and enterprise-only included;
``preorder``  announced with a price and an order book open;
``announced`` publicly shown by its maker, with no order book.

## The interesting decision

**An announced body cannot be bound**, and the refusal is a `409` that names
the status rather than a `404`. A 404 would say *unknown robot model* about a
machine its maker has stood on a stage with, which is false; and binding one
would leave every command afterwards going nowhere. Listing it and refusing it
are the two halves of the same honesty.

## Why the date matters

`REVIEWED` is checked against the changelog rather than left as a comment. A
catalogue whose `announced` rows shipped eighteen months ago is worse than no
catalogue, because it reads as current — the same failure as an exemption list
that stopped being looked at, which this repository has now found twice.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest

from qrme import robotics


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _owner(client, account="acct_body"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Vela",
        "purpose": "enterprise_agent", "persona": "a steady hand",
        "verification": {"birthdate": "1988-03-03"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p["id"], head


# --- the shape of the catalogue ---------------------------------------------

def test_the_catalogue_covers_the_market(client):
    c = client.get("/robotics/catalog").json()
    assert len(c["robots"]) >= 30, (
        "the point of this round was breadth; a short list is the old one")
    assert len(c["by_maker"]) >= 15
    assert set(c["by_kind"]) >= {"humanoid", "home_robot", "vacuum",
                                 "quadruped"}


def test_every_row_says_whether_you_can_get_one(client):
    c = client.get("/robotics/catalog").json()
    for row in c["robots"]:
        assert row["availability"] in ("shipping", "preorder", "announced"), \
            f"{row['model']} has no usable availability"
        assert row["bindable"] is (row["availability"] in c["buyable"])


def test_it_lists_things_nobody_can_buy(client):
    """If this ever goes empty the catalogue has quietly become a shop
    again, which is the thing it was widened not to be."""
    c = client.get("/robotics/catalog").json()
    assert c["by_availability"].get("announced"), (
        "nothing is listed as announced — either the market stopped "
        "announcing anything, or the list stopped looking forward")


def test_the_grouping_is_done_once_on_the_server(client):
    """Three clients would otherwise group three ways."""
    c = client.get("/robotics/catalog").json()
    total = sum(len(v) for v in c["by_kind"].values())
    assert total == len(c["robots"])
    assert sum(len(v) for v in c["by_availability"].values()) == total


def test_every_kind_has_a_command_allowlist(client):
    """A body whose kind is missing from COMMANDS accepts nothing, which is
    a quiet way for a new row to be useless."""
    c = client.get("/robotics/catalog").json()
    for kind in c["by_kind"]:
        assert c["commands"].get(kind), f"{kind} has no allowlist"
        assert kind in robotics.EMBODIMENT_KIND, \
            f"{kind} maps onto no embodiment kind"


# --- what you can and cannot bind -------------------------------------------

def test_a_shipping_body_binds(client):
    pid, head = _owner(client, "acct_ship")
    shipping = next(r for r in robotics.BY_KEY.values()
                    if r["availability"] == "shipping" and r["llm_capable"])
    r = client.post(f"/profiles/{pid}/robots", headers=head,
                    json={"name": "Vela's body", "model": shipping["model"]})
    assert r.status_code == 201, r.text


def test_an_announced_body_is_refused_by_name(client):
    """The decision this file exists for. Not "unknown model" — the machine
    is real, and saying otherwise is the lie."""
    pid, head = _owner(client, "acct_soon")
    soon = next(r for r in robotics.BY_KEY.values()
                if r["availability"] == "announced")
    r = client.post(f"/profiles/{pid}/robots", headers=head,
                    json={"name": "too early", "model": soon["model"]})
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert soon["label"] in detail
    assert "announced" in detail
    assert "see it coming" in detail


def test_a_model_that_does_not_exist_is_still_a_404(client):
    """The two refusals stay distinguishable: one says *not yet*, the other
    says *no such thing*."""
    pid, head = _owner(client, "acct_nomodel")
    r = client.post(f"/profiles/{pid}/robots", headers=head,
                    json={"name": "x", "model": "no_such_body"})
    assert r.status_code == 404


def test_a_preorder_body_binds(client):
    """Pre-order is a body somebody has taken money for, so it is bindable;
    the constraint is delivery, not existence."""
    pid, head = _owner(client, "acct_pre")
    pre = next((r for r in robotics.BY_KEY.values()
                if r["availability"] == "preorder"), None)
    if pre is None:
        pytest.skip("nothing is on pre-order in this snapshot")
    r = client.post(f"/profiles/{pid}/robots", headers=head,
                    json={"name": "ordered", "model": pre["model"]})
    assert r.status_code == 201, r.text


def test_bindable_agrees_with_the_route(client):
    """The helper and the route have to say the same thing, or the console
    disables the wrong options."""
    pid, head = _owner(client, "acct_agree")
    for spec in robotics.BY_KEY.values():
        expected = 201 if robotics.bindable(spec["model"]) else 409
        r = client.post(f"/profiles/{pid}/robots", headers=head,
                        json={"name": spec["model"], "model": spec["model"]})
        assert r.status_code == expected, \
            f"{spec['model']} ({spec['availability']}) answered {r.status_code}"


# --- the snapshot has to stay a snapshot ------------------------------------

def test_the_review_date_is_not_stale():
    """`announced` is a claim about the future, and it ages.

    Checked against the newest changelog heading rather than against today,
    so the test is about *maintenance* — did anybody look at this while the
    product was moving — rather than about wall-clock time in CI.
    """
    reviewed = date.fromisoformat(robotics.REVIEWED)
    text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    dates = [date.fromisoformat(m) for m in
             re.findall(r"^## \[[^\]]+\] — (\d{4}-\d{2}-\d{2})", text, re.M)]
    assert dates, "no dated release heading found in the changelog"
    newest = max(dates)
    assert (newest - reviewed).days <= 365, (
        f"the robot catalogue was last reviewed {robotics.REVIEWED} and the "
        f"newest release is {newest} — an `announced` row that shipped a year "
        "ago reads as current, which is worse than not listing it")


# --- the console half -------------------------------------------------------

def _markup(rel: str) -> str:
    s = (REPO / rel).read_text(encoding="utf-8")
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_picker_groups_by_availability():
    src = _markup("app/src/screens/Robots.tsx")
    assert "optgroup" in src, "the model picker is one flat list again"
    assert "Announced — not yet buyable" in src


def test_the_picker_disables_what_cannot_be_bound():
    """An option that only ever produces a 409 is worse than a disabled
    one — the refusal is correct and the click was still wasted."""
    assert "disabled={!m.bindable}" in _markup("app/src/screens/Robots.tsx")


def test_the_screen_shows_when_the_list_was_checked():
    assert "market.reviewed" in _markup("app/src/screens/Robots.tsx")


def test_the_connections_bracket_calls_all_four():
    src = (REPO / "app/src/screens/Robots.tsx").read_text(encoding="utf-8")
    for binding in ("api.packs(", "api.installedPacks(", "api.installPack(",
                    "api.uninstallRobotPack(", "api.connectorCatalogue("):
        assert binding in src, f"{binding} is not called by the screen"


def test_the_screen_says_a_pack_is_fitted_to_a_body_not_a_profile():
    """The distinction that decides whether the install goes where the owner
    meant. A profile pack teaches a persona; a robot pack teaches a machine."""
    # The sentence moved into the l10n table when the screen was localized;
    # the screen must still look it up, and the table must still say it.
    src = _markup("app/src/screens/Robots.tsx")
    assert 'tr("rbt.conn.openfirst", lang)' in src
    table = _markup("app/src/l10n.ts").replace("\n", " ").replace("  ", " ")
    assert "fitted to a" in table
