"""Membership: Basic, Pro, and the visitor below both.

The tests that matter are the ones binding the three things that can disagree:
the price list, the gate, and the routes. A pricing page that promises a
capability the gate does not grant is a refund request; a gate that blocks
something the page says is included is the same bug from the other side.

Everything money-shaped in this repository is simulated, and the last test here
holds this surface to that — the one place a tier system would be tempted to
look like a working payment processor is exactly where somebody would be
misled.
"""

import pytest

from qrme import tiers
from tests.test_capabilities import auth_header, make_profile


# -- the price list and the gate are one table --------------------------------

def test_what_a_plan_includes_is_computed_not_typed(client):
    """A feature list written by hand is one that goes stale the first time a
    capability moves between plans."""
    page = client.get("/plans").json()
    for row in page["plans"]:
        assert row["includes"] == tiers.includes(row["plan"])
        assert set(row["includes"]) | set(row["locked"]) == set(tiers.CAPABILITIES)
        assert not set(row["includes"]) & set(row["locked"])


def test_the_plans_are_the_prices_that_were_agreed(client):
    """The agreement changed on 2026-08-10: every plan is $0 while the beta
    runs. The tiers keep their gates — the plan a tester chooses is still
    recorded and enforced — and each paid plan's own copy names the price
    that returns when the beta ends ($20 Basic, $130 Pro), so the zero is
    a disclosed decision rather than a forgotten number."""
    assert tiers.PLANS["basic"]["price_usd"] == 0
    assert tiers.PLANS["basic"]["period"] == "month"
    assert "beta" in tiers.PLANS["basic"]["means"]
    assert "$20" in tiers.PLANS["basic"]["means"]
    assert tiers.PLANS["pro"]["price_usd"] == 0
    assert tiers.PLANS["pro"]["period"] == "month"
    assert "beta" in tiers.PLANS["pro"]["means"]
    assert "$130" in tiers.PLANS["pro"]["means"]
    assert tiers.PLANS["visitor"]["price_usd"] == 0


def test_basic_makes_things_and_pro_reaches_outside(client):
    """The line the two plans are drawn on: Basic is for making your own
    things, Pro is for anything that leaves your own account."""
    assert tiers.entitles("basic", "profiles")
    assert tiers.entitles("basic", "own_agent")
    for capability in ("marketplace", "connectors", "skills", "downloads",
                       "connections", "builders"):
        assert not tiers.entitles("basic", capability), capability
        assert tiers.entitles("pro", capability), capability


def test_a_visitor_may_read_and_make_nothing(client):
    """Not an oversight. The whole beacon story is a stranger scanning a
    printed code and landing somewhere useful — a wall asking them to
    subscribe before they can read the page would break the feature."""
    for capability in tiers.CAPABILITIES:
        assert not tiers.entitles("visitor", capability), capability
    assert client.get("/plans", headers={"authorization": ""}).status_code == 200


def test_every_gated_pattern_names_a_real_capability(client):
    """A pattern mapped to a capability that does not exist would raise inside
    the gate on a live request, turning a paywall into a 500."""
    for _pattern, capability in tiers.GATED:
        assert capability in tiers.CAPABILITIES


def _sample_paths(client) -> list[str]:
    """Every served route as a concrete path, with `{id}` filled in."""
    import re

    return [re.sub(r"\{[^}]+\}", "x", p) for p in client.app.openapi()["paths"]]


def test_every_gated_pattern_is_a_route_that_exists(client):
    """The test that caught the first version of this table.

    It named `/steering`, `/governance` and `/licensing` as prefixes. None is a
    route on this application — steering lives at `/profiles/{id}/steering` —
    so all three were paywalls in front of a wall: they read as protection,
    protected nothing, and would have survived indefinitely because nothing
    fails when a pattern matches no traffic.
    """
    import re

    samples = _sample_paths(client)
    for pattern, _ in tiers.GATED:
        assert any(re.search(pattern, p) for p in samples), (
            f"{pattern} gates nothing — no served route matches it")


def test_the_named_exceptions_are_routes_that_exist(client):
    spec = client.app.openapi()
    for method, path in tiers.OPEN:
        assert path in spec["paths"], f"{path} is listed OPEN but is not a route"
        assert method.lower() in spec["paths"][path], (
            f"{method} {path} is listed OPEN but that method is not served")


# -- the gate actually refuses -------------------------------------------------

def test_a_basic_account_is_turned_away_from_pro_features(client):
    """The reason the whole module exists, exercised over HTTP rather than
    against the entitlement function."""
    me = make_profile(client, plan="basic")
    r = client.post("/marketplace/listings",
                    json={"profile_id": me["id"], "title": "x", "price": 1},
                    headers=auth_header(me))
    assert r.status_code == 402, r.text
    detail = r.json()["detail"]
    assert detail["reason"] == "plan"
    assert detail["needs"] == "pro" and detail["have"] == "basic"
    assert detail["price_usd"] == 0  # free during the beta


def test_the_refusal_is_structured_because_402_is_already_spoken(client):
    """`POST /packs/{id}/install` answers 402 for *this pack costs money*.
    Both are genuinely payment-required, so a client has to tell them apart —
    and matching on prose breaks the first time somebody rewords a message."""
    me = make_profile(client, plan="basic")
    r = client.put(f"/profiles/{me['id']}/steering", json={"warmth": 0.5},
                   headers=auth_header(me))
    assert r.status_code == 402, r.text
    assert isinstance(r.json()["detail"], dict)
    assert r.json()["detail"]["reason"] == "plan"


def test_upgrading_opens_the_same_call(client):
    me = make_profile(client, plan="basic")
    body = {"profile_id": me["id"], "title": "A listing", "price": 1}
    assert client.post("/marketplace/listings", json=body,
                       headers=auth_header(me)).status_code == 402

    client.post("/memberships/owner-1", json={"plan": "pro"},
                headers=auth_header(me))
    assert client.post("/marketplace/listings", json=body,
                       headers=auth_header(me)).status_code != 402


def test_browsing_stays_open_to_a_basic_member(client):
    """A paywall that hides the shop from the person you are trying to sell to
    is a paywall arguing against itself — and the catalogue is public to
    strangers anyway."""
    me = make_profile(client, plan="basic")
    assert client.get("/marketplace/listings",
                      headers=auth_header(me)).status_code == 200


def test_reading_is_open_wherever_writing_is_gated(client):
    """The decision recorded in tiers.READ_ALSO_GATED being empty."""
    import re

    for pattern, capability in tiers.GATED:
        sample = next(p for p in _sample_paths(client) if re.search(pattern, p))
        assert tiers.capability_for("GET", sample) is None, sample
        assert tiers.capability_for("POST", sample) == capability, sample


def test_a_named_exception_is_not_gated(client):
    assert tiers.capability_for("POST", "/packs/seed") is None
    assert tiers.capability_for("POST", "/marketplace/seed") is None
    assert tiers.capability_for("POST", "/marketplace/assist") is None
    assert tiers.capability_for("POST", "/packs/anything/install") == "downloads"


def test_an_ungated_path_needs_nothing(client):
    for path in ("/health", "/profiles", "/tutorial", "/dock/faces", "/plans"):
        assert tiers.capability_for("POST", path) is None, path


# -- who the membership belongs to --------------------------------------------

def test_a_membership_belongs_to_the_account_not_the_profile(client):
    """A per-profile membership would mean paying twice to hold two profiles,
    which is exactly what identity.py exists to let people do for free."""
    first = make_profile(client, plan="pro", owner_id="acct-1")
    second = make_profile(client, owner_id="acct-1", display_name="Second")
    assert tiers.plan_of("acct-1") == "pro"
    assert second["membership"]["plan"] == "pro"
    del first


def test_making_a_second_profile_does_not_downgrade_you(client):
    """The bug `_enrol` exists to prevent: a Pro member makes another profile
    and quietly lands back on Basic."""
    make_profile(client, plan="pro", owner_id="acct-2")
    # plan=None is the case that matters: the client did not name a plan, so
    # `_enrol` has to look up what this account already holds. Letting the
    # helper's Pro default ride through would test nothing.
    make_profile(client, plan=None, owner_id="acct-2", display_name="Another")
    assert tiers.plan_of("acct-2") == "pro"


def test_creating_a_profile_enrols_a_new_account_on_free(client):
    """Making something is what a membership is for, so creation is where an
    account joins one — and the default is Free.

    Putting somebody on a paid plan they did not ask for is the wrong default
    even at a fair price. Free is honest about what it is rather than quiet,
    which is what makes it safe to land people on.
    """
    me = make_profile(client, plan=None, owner_id="acct-3")
    assert me["membership"]["plan"] == tiers.DEFAULT_PLAN == "free"
    assert me["membership"]["storage"]["private"] is False
    assert "in the clear" in me["membership"]["storage"]["disclosure"]


def test_genesis_enrols_on_the_same_terms_as_the_form(client):
    """Two creation paths that enrolled differently is exactly the divergence
    `_enrol` was written once to prevent."""
    r = client.post("/profiles/genesis", json={
        "owner_id": "acct-4",
        "verification": {"birthdate": "1984-06-01"},
        "answers": {"social_style": "warm but quiet in the evenings",
                    "humor": "dry, gentle teasing",
                    "what_matters": "ferns, honesty, the garden",
                    "comfort": "sits with you and says little"}})
    assert r.status_code == 201, r.text
    assert r.json()["membership"]["plan"] == "free"


def test_an_interactor_is_not_an_account(client):
    """Returning an interactor's id from `account_of` would silently give
    every person who ever talked to a profile a membership under their own
    name."""
    import types

    fake = types.SimpleNamespace(
        method="POST", url=types.SimpleNamespace(path="/marketplace/listings"),
        headers={})
    assert tiers.account_of(fake) is None


# -- joining, moving and leaving ----------------------------------------------

def test_moving_plan_replaces_rather_than_stacks(client):
    """An account on two plans at once is a question nobody should have to
    answer at the moment a gate is being checked."""
    me = make_profile(client, plan="basic", owner_id="acct-5")
    client.post("/memberships/acct-5", json={"plan": "pro"},
                headers=auth_header(me))
    from qrme import db

    live = db.connect().execute(
        "SELECT COUNT(*) AS n FROM memberships WHERE account_id=? AND"
        " ended_at IS NULL", ("acct-5",)).fetchone()["n"]
    assert live == 1
    assert tiers.plan_of("acct-5") == "pro"


def test_cancelling_keeps_the_profiles(client):
    """A lapsed subscription is not a reason to delete somebody's work, and a
    product that deleted it is one nobody could safely try."""
    me = make_profile(client, plan="pro", owner_id="acct-6")
    client.delete("/memberships/acct-6", headers=auth_header(me))
    assert tiers.plan_of("acct-6") == "visitor"
    assert client.get(f"/profiles/{me['id']}").status_code == 200


def test_the_history_survives_a_change_of_plan(client):
    """"When did this account go from Basic to Pro" is a question a statement
    has to answer."""
    me = make_profile(client, plan="basic", owner_id="acct-7")
    client.post("/memberships/acct-7", json={"plan": "pro"},
                headers=auth_header(me))
    from qrme import db

    rows = db.connect().execute(
        "SELECT plan, ended_at FROM memberships WHERE account_id=?"
        " ORDER BY started_at", ("acct-7",)).fetchall()
    assert [r["plan"] for r in rows] == ["basic", "pro"]
    assert rows[0]["ended_at"] is not None and rows[1]["ended_at"] is None


def test_an_unknown_plan_is_refused(client):
    me = make_profile(client, owner_id="acct-8")
    r = client.post("/memberships/acct-8", json={"plan": "platinum"},
                    headers=auth_header(me))
    assert r.status_code == 422
    with pytest.raises(tiers.TierError):
        tiers.subscribe("acct-8", "visitor")     # not something you buy


# -- somebody else's membership ------------------------------------------------

def test_a_membership_is_not_readable_by_its_account_id_alone(client):
    """An account id is not a credential — it is whatever string the owner
    typed at signup. Without a check, reading somebody's plan and cancelling
    it would take only a guess."""
    make_profile(client, plan="pro", owner_id="acct-9")
    other = make_profile(client, owner_id="acct-10", display_name="Rae")
    theirs = auth_header(other)

    assert client.get("/memberships/acct-9", headers=theirs).status_code == 403
    assert client.post("/memberships/acct-9", json={"plan": "basic"},
                       headers=theirs).status_code == 403
    assert client.delete("/memberships/acct-9",
                         headers=theirs).status_code == 403
    assert client.get("/memberships/acct-9",
                      headers={"authorization": ""}).status_code == 401
    assert tiers.plan_of("acct-9") == "pro"      # untouched throughout


# -- the money is simulated, and says so --------------------------------------

def test_every_money_bearing_response_discloses_the_simulation(client):
    """The convention `commerce.py` set. A tier system that quietly looked
    like a working payment processor would be the one surface here where the
    simulation was not disclosed — precisely where somebody would be misled."""
    me = make_profile(client, plan="basic", owner_id="acct-11")
    assert "simulated" in client.get("/plans").json()["billing"]
    assert "simulated" in client.get(
        "/memberships/acct-11", headers=auth_header(me)).json()["billing"]
    assert "simulated" in client.post(
        "/memberships/acct-11", json={"plan": "pro"},
        headers=auth_header(me)).json()["billing"]

    # A separate account, still on Basic — the one above was just upgraded, so
    # asking it for a refusal would test nothing.
    still_basic = make_profile(client, plan="basic", owner_id="acct-12",
                               display_name="Rae")
    refused = client.put(f"/profiles/{still_basic['id']}/steering",
                         json={"warmth": 0.5}, headers=auth_header(still_basic))
    assert refused.status_code == 402, refused.text
    assert "simulated" in refused.json()["detail"]["billing"]


def test_nothing_here_reaches_a_payment_processor(client):
    """Asserted against the source: the row *is* the subscription."""
    import inspect

    src = inspect.getsource(tiers)
    for real in ("stripe", "paypal", "braintree", "charge(", "card",
                 "http://", "https://"):
        assert real not in src.lower(), f"{real!r} appears in tiers.py"
