"""An audience, and the decisions in how it pays.

**Nothing here renews on a timer.** A period is charged when somebody presses
renew, and `audience.py` says why: a deployment left running does not accrue
charges nobody authorised and nobody saw. So `periods` is a count of
deliberate acts rather than a duration, and a screen showing it as elapsed time
would be describing something that did not happen.

Two more decisions this file pins down:

* **agreeing to a price means sending the same number back.** `accept_price`
  is not a boolean — it has to equal `price` exactly, so the figure somebody
  agreed to is the figure being charged;
* **gifting needs a verified birthdate**, refused with the reason: *an
  unverified age is not evidence of an adult*.

And one asymmetry, recorded rather than corrected, because it is a design
question rather than a defect:

* a **gift** reads its beneficiary from the subject —
  `commerce.beneficiary_of` exists precisely so *a body-supplied beneficiary
  would let anyone direct a gift meant for a performer into their own
  balance*;
* a **subscription** takes one from the request body.

Both are asserted as they are. If the second should read from the subject too,
that is a change worth making on purpose, and a test that pretends they already
agree would hide the question.
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


def _pair(client, account="acct_aud"):
    """A profile, and somebody who might follow it."""
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Creator",
        "purpose": "creator_persona", "persona": "p",
        "verification": {"birthdate": "1990-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    fan = client.post("/interactors", json={"display_name": "Fan"}).json()
    return p, head, fan, {"authorization": f"Bearer {fan['token']}"}


# --- the tiers --------------------------------------------------------------

def test_there_are_two_tiers_and_a_wrong_one_names_both(client):
    p, _, fan, fhead = _pair(client, "acct_tier")
    r = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                    json={"tier": "supporter"})
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert "follow" in detail and "paid" in detail


def test_following_is_free_and_needs_no_price_consent(client):
    p, _, fan, fhead = _pair(client, "acct_free")
    r = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                    json={"tier": "follow"})
    assert r.status_code == 201, r.text
    sub = r.json()
    assert sub["price"] == 0.0 and sub["periods"] == 0


def test_a_paid_tier_wants_the_number_back_not_a_tick(client):
    """`accept_price` has to equal `price` exactly. A boolean would let a
    client agree to a figure it never showed anybody."""
    p, _, fan, fhead = _pair(client, "acct_accept")
    without = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                          json={"tier": "paid", "price": 5.0,
                                "beneficiary": "acct_accept"})
    assert without.status_code == 422
    assert "accept_price=5.00" in without.json()["detail"]

    mismatched = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                             json={"tier": "paid", "price": 5.0,
                                   "accept_price": 4.0,
                                   "beneficiary": "acct_accept"})
    assert mismatched.status_code == 422

    ok = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                     json={"tier": "paid", "price": 5.0, "accept_price": 5.0,
                           "beneficiary": "acct_accept"})
    assert ok.status_code == 201, ok.text


def test_a_paid_subscription_must_credit_somebody(client):
    p, _, fan, fhead = _pair(client, "acct_credit")
    r = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                    json={"tier": "paid", "price": 5.0, "accept_price": 5.0})
    assert r.status_code == 422
    assert "accrue to nobody" in r.json()["detail"]


# --- the thing this file is named for ---------------------------------------

def test_a_period_is_charged_only_when_somebody_presses(client):
    """The decision that shapes the whole screen. Nothing bills on a timer,
    so `periods` counts presses — and a console showing it as elapsed time
    would be describing something that never happened."""
    p, _, fan, fhead = _pair(client, "acct_press")
    sub = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                      json={"tier": "paid", "price": 5.0, "accept_price": 5.0,
                            "beneficiary": "acct_press"}).json()
    assert sub["periods"] == 1, "subscribing charges the first period"

    again = client.post(f"/subscriptions/{sub['id']}/renew", headers=fhead,
                        json={"beneficiary": "acct_press"}).json()
    assert again["periods"] == 2
    assert again["charged"]["amount"] == 5.0
    assert again["charged"]["ledger_entry"], (
        "a period was charged with nothing written to the ledger")


def test_renewing_needs_the_beneficiary_too(client):
    """Charging a period is the same act as the first charge, so it asks
    the same question rather than remembering an answer."""
    p, _, fan, fhead = _pair(client, "acct_renewben")
    sub = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                      json={"tier": "paid", "price": 5.0, "accept_price": 5.0,
                            "beneficiary": "acct_renewben"}).json()
    r = client.post(f"/subscriptions/{sub['id']}/renew", headers=fhead,
                    json={})
    assert r.status_code == 422
    assert "beneficiary" in r.json()["detail"]


def test_the_billing_note_travels_on_every_subscription(client):
    """Everywhere else in this repository a figure carries the fact that the
    money is simulated. A recurring one is the easiest place to forget."""
    p, _, fan, fhead = _pair(client, "acct_note")
    sub = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                      json={"tier": "follow"}).json()
    assert "simulat" in sub["billing"].lower()
    assert "never on a timer" in sub["billing"]


def test_cancelling_keeps_the_row_and_the_count(client):
    """A lapsed-then-returned subscriber keeps one history rather than
    accumulating rows, so cancel marks the row instead of deleting it."""
    p, _, fan, fhead = _pair(client, "acct_cancel")
    client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                json={"tier": "paid", "price": 5.0, "accept_price": 5.0,
                      "beneficiary": "acct_cancel"})
    gone = client.request("DELETE", f"/profiles/{p['id']}/subscribe",
                          headers=fhead, json={}).json()
    assert gone["status"] == "cancelled" and gone["cancelled_at"]
    assert gone["periods"] == 1, "the count of what was charged was erased"

    back = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                       json={"tier": "follow"}).json()
    assert back["id"] == gone["id"], "re-subscribing made a second row"


# --- gifts ------------------------------------------------------------------

def test_gifting_needs_a_verified_birthdate(client):
    p, _, fan, fhead = _pair(client, "acct_giftage")
    r = client.post(f"/profiles/{p['id']}/gift", headers=fhead,
                    json={"amount": 5.0})
    assert r.status_code == 403
    assert "not evidence of an adult" in r.json()["detail"]


def test_the_gift_cap_is_published_before_anybody_hits_it(client):
    """So a screen can say the limit rather than letting somebody find it
    by being refused."""
    p, head, _, _ = _pair(client, "acct_giftcap")
    view = client.get(f"/profiles/{p['id']}/gifts", headers=head).json()
    assert view["cap_per_gift"] > 0
    assert "total_amount" in view


def test_a_gift_reads_its_beneficiary_from_the_subject(client):
    """The asymmetry, half one.

    `commerce.beneficiary_of` exists so a giver cannot point money meant for
    a performer at their own balance — so the route takes no beneficiary at
    all, and a body carrying one changes nothing.
    """
    import inspect

    from qrme import commerce

    src = inspect.getsource(commerce.beneficiary_of)
    assert "owner_id" in src
    assert "body-supplied beneficiary" in commerce.beneficiary_of.__doc__


def test_a_subscription_takes_its_beneficiary_from_the_body(client):
    """The asymmetry, half two — recorded as it is.

    If this should read from the subject as well, that is a decision to make
    on purpose. A test asserting the two already agree would hide the
    question rather than answer it.
    """
    p, _, fan, fhead = _pair(client, "acct_asym")
    ok = client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                     json={"tier": "paid", "price": 3.0, "accept_price": 3.0,
                           "beneficiary": "somebody-else-entirely"})
    assert ok.status_code == 201, (
        "the subscription beneficiary is no longer taken from the body — if "
        "that was deliberate, this test should say so instead of failing")


# --- the counters -----------------------------------------------------------

def test_the_audience_view_counts_without_naming_anybody(client):
    p, head, fan, fhead = _pair(client, "acct_counts")
    client.post(f"/profiles/{p['id']}/subscribe", headers=fhead,
                json={"tier": "follow"})
    view = client.get(f"/profiles/{p['id']}/audience", headers=head).json()
    assert view["subscribers"] == 1
    for key in ("likes", "comments", "shares"):
        assert isinstance(view[key], int)
    assert "subscriber_names" not in view and "who" not in view


def test_the_buyer_and_the_seller_read_different_lists(client):
    """`/orders` is the buyer's side; `sales` next door is the seller's.
    Two questions, so two lists — and a console that showed one as the other
    would tell somebody they had bought their own listing."""
    p, head, fan, fhead = _pair(client, "acct_orders")
    assert "orders" in client.get("/orders", headers=fhead).json()


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_the_audience_screen_exists():
    assert (REPO / "app/src/screens/Audience.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.subscriptions(", "api.follow(", "api.unfollow(",
    "api.renewSubscription(", "api.subscribers(", "api.gifts(",
    "api.sendGift(", "api.audience(", "api.myOrders(",
])
def test_the_audience_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Audience.tsx")


def test_following_a_creator_is_not_named_like_joining_a_plan():
    """`subscribe` already means joining a membership plan. One verb for
    both is how somebody cancels the wrong thing."""
    api = _src("app/src/api.ts")
    assert "  follow: (kind: string" in api
    assert "  subscribe: (accountId: string" in api, (
        "the plan binding was renamed instead, which moves the collision "
        "rather than removing it")


def test_the_console_sends_the_price_it_showed():
    """`accept_price: price` and not a constant — the check only means
    something if the two are the same variable."""
    src = _src("app/src/screens/Audience.tsx")
    assert "accept_price: price" in src


def _markup(rel: str) -> str:
    """The file with its comments removed.

    Searching the whole file would pass on the docstring at the top, which
    explains this very decision at length — so the guard would be green
    whether or not anybody looking at the screen is ever told. What has to
    carry the sentence is the markup.
    """
    src = _src(rel)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"^\s*//.*$", "", src, flags=re.M)


def test_the_screen_says_a_period_is_a_press():
    """`periods` is a count of presses. Rendered bare it reads as elapsed
    time, and somebody would reasonably conclude they are being billed on a
    schedule — which is the one thing this feature does not do."""
    assert 'tr("aud.period' in _markup("app/src/screens/Audience.tsx"), (
        "periods are being shown without saying what they count, which "
        "reads as elapsed time")
    # The sentence moved into the l10n table when the screen was localized.
    # Both the singular and plural rows have to carry it: the plural is the
    # one somebody reads on a second press, and it is the press that this
    # sentence exists to name.
    l10n = _markup("app/src/l10n.ts")
    assert l10n.count("pressed a button") >= 2, (
        "one of the two period rows has stopped saying what they count")
