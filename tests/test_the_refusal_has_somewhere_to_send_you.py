"""A refusal that names a plan must be able to reach one.

The previous round taught the console to render a plan gate properly: the
capability that was wanted, the plan that has it, the price, and the note that
the billing is simulated. Drawing it well turned up the next thing — there was
no plans surface. The console could refuse you for not having Pro and had no
way to sell you Pro, because `GET /plans` and the three `/memberships` routes
were on the doorless list too.

That is a worse failure than the one it replaced. A flat "not on your plan" is
merely unhelpful; an upsell naming a plan in a product with no way to join one
advertises something that appears not to exist.

So this file guards the join rather than either half of it:

* the catalogue keeps the fields a picker is built from, including the two the
  running server revealed and a route signature would not have — `period` is
  null on the unpaid tiers, and `visitor` and `free` are **different plans that
  both cost nothing**;
* `capabilities` stays keyed by the same names the gate refuses with, which is
  the whole reason a refusal can be explained rather than just displayed;
* the console's side: a plans screen exists, `Refusal` can be given somewhere
  to go, and the shell actually gives it one — a prop that is optional and
  never passed is the same defect in a new place.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _account(client):
    """An owner token, and the account id it is an owner on."""
    p = client.post("/profiles", json={
        "owner_id": "acct_join", "kind": "fictional",
        "display_name": "Joiner", "purpose": "companion_coach",
        "persona": "p", "verification": {"birthdate": "1990-01-01"},
    }).json()
    return "acct_join", p["owner_token"]


def test_the_price_list_needs_no_account(client):
    """`tiers.py`: a paywall nobody can read the terms of before signing in is
    one people bounce off. The screen renders everything above the membership
    card with no session, and that is only honest while this holds."""
    r = client.get("/plans")
    assert r.status_code == 200, r.text


@pytest.mark.parametrize("field", ["plan", "title", "price_usd", "period",
                                   "means", "includes", "locked", "storage"])
def test_each_plan_carries_what_a_picker_draws(field, client):
    for plan in client.get("/plans").json()["plans"]:
        assert field in plan, f"{plan.get('plan')!r} has no {field!r}"


def test_free_and_visitor_are_kept_apart(client):
    """Both cost nothing and they are not the same thing.

    A visitor has no account and can read a public page. Free has an account
    whose work sits in the platform's database in the clear. A picker written
    from the price alone would collapse them into one $0 row and hide the
    entire difference — which is the difference the product is arguing about.
    """
    plans = {p["plan"]: p for p in client.get("/plans").json()["plans"]}
    assert "visitor" in plans and "free" in plans
    assert plans["visitor"]["price_usd"] == plans["free"]["price_usd"] == 0
    assert plans["visitor"]["includes"] != plans["free"]["includes"], (
        "visitor and free now offer the same thing, so the console has no "
        "reason to draw them as two plans")


def test_the_unpaid_tiers_have_no_billing_period(client):
    """Driven, not assumed. `period` is null rather than "month" at $0, and a
    screen that printed "$0 a month" would be inventing a subscription."""
    plans = {p["plan"]: p for p in client.get("/plans").json()["plans"]}
    for free in ("visitor", "free"):
        assert plans[free]["period"] is None
    assert plans["pro"]["period"], "a paid plan with no period to bill on"


def test_capabilities_are_keyed_the_way_the_gate_refuses(client):
    """The join between the refusal and the page.

    A plan gate refuses with `capability: "builders"`. The catalogue explains
    capabilities under the same key, so a console can say what was actually
    wanted instead of echoing an identifier. If these drift apart, the refusal
    still renders and quietly stops explaining anything.
    """
    cat = client.get("/plans").json()
    caps = cat["capabilities"]
    named = {c for p in cat["plans"] for c in p["includes"] + p["locked"]}
    assert named, "no plan names any capability"
    missing = sorted(named - set(caps))
    assert not missing, (
        f"these capabilities are gated but not explained: {missing} — a "
        "refusal naming one has nothing to show but the identifier")
    for key, entry in caps.items():
        assert entry.get("is"), f"{key} has no sentence"
        assert entry.get("from"), f"{key} does not say which plan it starts on"


def test_a_price_is_never_published_without_the_billing_note(client):
    """The same rule the refusal follows, on the page the refusal points at."""
    cat = client.get("/plans").json()
    assert "simulat" in cat["billing"].lower()
    _, token = _account(client)
    mine = client.get("/memberships/acct_join",
                      headers={"authorization": f"Bearer {token}"}).json()
    assert "simulat" in mine["billing"].lower()


def test_joining_and_leaving_both_answer_with_the_membership(client):
    """The screen renders the response rather than re-fetching, so all three
    routes have to answer in the same shape."""
    account, token = _account(client)
    head = {"authorization": f"Bearer {token}"}
    before = client.get(f"/memberships/{account}", headers=head).json()
    joined = client.post(f"/memberships/{account}", json={"plan": "pro"},
                         headers=head).json()
    left = client.request("DELETE", f"/memberships/{account}", headers=head)
    assert joined["plan"] == "pro"
    assert set(before) == set(joined) == set(left.json()), (
        "the three membership routes no longer answer in one shape")


def test_cancelling_keeps_the_profiles(client):
    """Said on the screen every time somebody presses it, so it had better be
    true: a lapsed plan is not a reason to delete anybody's work."""
    account, token = _account(client)
    head = {"authorization": f"Bearer {token}"}
    mine = client.get("/profiles").json()
    client.post(f"/memberships/{account}", json={"plan": "basic"}, headers=head)
    client.request("DELETE", f"/memberships/{account}", headers=head)
    after = client.get("/profiles").json()
    assert len(after) >= len(mine)


def test_reading_a_membership_still_needs_more_than_the_account_id(client):
    """An account id is not a credential — it is whatever string the owner
    typed at profile creation. Without this, reading somebody's plan and
    cancelling it would take only a guess."""
    account, _ = _account(client)
    assert client.get(f"/memberships/{account}").status_code == 401


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_the_console_has_a_plans_screen():
    assert (REPO / "app/src/screens/Plans.tsx").exists(), (
        "the refusal names a plan and the console has no page for one")


def test_the_plans_screen_calls_all_four_routes():
    src = _src("app/src/screens/Plans.tsx")
    for binding in ("api.plans(", "api.membership(", "api.subscribe(",
                    "api.cancelMembership("):
        assert binding in src, f"{binding}) is bound and never called"


def test_the_shell_actually_gives_the_refusal_somewhere_to_go():
    """The defect this whole round is about, in its newest possible form.

    `Refusal` takes an optional `onPlans`. An optional prop that nothing ever
    passes is a button that never appears — the upsell would go back to being
    a card with no way out, and nothing would fail.
    """
    app = _src("app/src/App.tsx")
    assert 'setTab("plans")' in app, "no way to reach the plans screen"
    assert app.count("onPlans={toPlans}") >= 20, (
        "the shell stopped threading onPlans into the screens; a plan gate "
        "there would render an offer with no button")


def test_the_sidebar_reserves_room_for_the_widget_parked_on_it():
    """Found by clicking, not reading.

    Adding the Plans tab put it under the always-on agent-lights widget, which
    is fixed to the bottom-left corner — on top of the sidebar. A real click
    landed on the lights. Two more tabs were already under there.

    This is the same fault the 760px block in `styles.css` was written for,
    when the widget covered Home and Chat on a phone and the tabs were
    reported as broken screens. On desktop the sidebar simply had not grown
    long enough to reach it yet, so the fix was made once and the second half
    of the problem shipped anyway.

    Asserting the arithmetic rather than the number: the column has to reserve
    the widget's footprint, whatever the widget's size becomes.
    """
    css = _src("app/src/styles.css")

    def px(pattern: str) -> int:
        m = re.search(pattern, css)
        assert m, f"styles.css no longer matches {pattern!r}"
        return int(m.group(1))

    height = px(r"\.watch-lights\s*\{[^}]*?height:\s*(\d+)px")
    bottom = px(r"\.watch-lights\s*\{[^}]*?bottom:\s*(\d+)px")
    reserved = px(r"\.sidebar\s*\{[^}]*?padding:\s*\d+px\s+\d+px\s+(\d+)px")
    assert reserved >= height + bottom, (
        f"the sidebar reserves {reserved}px at the bottom and the agent-lights "
        f"widget occupies {height + bottom}px of it — the last tabs are under "
        "the widget and a click lands on the lights")


def test_the_screens_keep_the_error_rather_than_its_sentence():
    """`req()` was fixed to carry the structure, and every screen then threw
    it away one layer up with `setError((e as Error).message)`. Fixing the
    transport alone changed nothing anybody could see."""
    offenders = []
    for path in sorted((REPO / "app" / "src").rglob("*.tsx")):
        text = path.read_text(encoding="utf-8")
        if re.search(r"setError\(\(e as Error\)\.message\)", text):
            offenders.append(str(path.relative_to(REPO)))
    assert not offenders, (
        f"these screens flatten the refusal before rendering it: {offenders}")
