"""¥100 plus $100 is not 200.

The creator statement summed every ledger entry regardless of currency and
labelled the result with whichever sale happened to be newest. A creator
pricing one profile in dollars and another in yen — nothing stops them, and
nothing should — got back ``accrued: 200``, ``currency: "JPY"``, and a payout
receipt whose ``total`` covered both. All three native shells render that
figure with a currency symbol in front of it.

Nothing was wrong with the entries. Each row carried its own currency the
whole time. The arithmetic over them was wrong, in the one place where a
wrong number is indistinguishable from a right one, and it had never been
looked at because the console had no earnings screen: the only surface where
a person would have seen the figure was the phone.

So: totals per currency, a settlement currency chosen deterministically
rather than by recency, a ``mixed`` flag for the screen to read before it
draws anything, and a payout that settles one currency and says what is left.

## What is *not* changed

The headline is still one currency's figures rather than a refusal to answer.
A statement that returned nothing until you named a currency would break every
client that has one, and "your dollars" is a true answer where "your money"
was not.
"""

from __future__ import annotations

import re
from pathlib import Path

from qrme import ledger


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _owner(client, account="acct_ccy"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Kai",
        "purpose": "enterprise_agent", "persona": "a guide",
        "verification": {"birthdate": "1988-03-03"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    # Listing and licensing are Pro capabilities, so the fixture buys the
    # plan rather than every test discovering the 402 separately.
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p, head


def _sell(client, profile, head, price, currency):
    """Put an offer up in one currency and have somebody buy it."""
    client.put(f"/profiles/{profile['id']}/license", headers=head,
               json={"kind": "consult", "price": price, "currency": currency,
                     "terms": "t", "allow_derivatives": False})
    buyer = client.post("/interactors", json={
        "display_name": "B", "birthdate": "1990-01-01"}).json()
    r = client.post(f"/profiles/{profile['id']}/license/acquire",
                    headers={"authorization": f"Bearer {buyer['token']}"})
    assert r.status_code == 201, r.text


# --- the defect -------------------------------------------------------------

def test_two_currencies_are_not_added_together(client):
    """The one this file exists for. Both sales are 100; neither total is
    200."""
    a, head = _owner(client, "acct_two")
    b = client.post("/profiles", json={
        "owner_id": "acct_two", "kind": "fictional", "display_name": "Noor",
        "purpose": "enterprise_agent", "persona": "a guide",
        "verification": {"birthdate": "1988-03-03"}}).json()
    bhead = {"authorization": f"Bearer {b['owner_token']}"}

    _sell(client, a, head, 100, "USD")
    _sell(client, b, bhead, 100, "JPY")

    s = client.get(f"/profiles/{a['id']}/earnings", headers=head).json()
    assert sorted(s["currencies"]) == ["JPY", "USD"]
    assert s["totals"]["accrued"] == 100, "the two currencies were summed"
    assert s["by_currency"]["USD"]["accrued"] == 100
    assert s["by_currency"]["JPY"]["accrued"] == 100


def test_the_statement_says_when_it_is_leaving_something_out(client):
    """`mixed` is the whole point of keeping a headline at all — a figure
    that silently covers one of two balances is only honest if it says so."""
    a, head = _owner(client, "acct_mixed")
    b = client.post("/profiles", json={
        "owner_id": "acct_mixed", "kind": "fictional", "display_name": "N",
        "purpose": "enterprise_agent", "persona": "g",
        "verification": {"birthdate": "1988-03-03"}}).json()
    _sell(client, a, head, 100, "USD")
    s = client.get(f"/profiles/{a['id']}/earnings", headers=head).json()
    assert s["totals"]["mixed"] is False

    _sell(client, b, {"authorization": f"Bearer {b['owner_token']}"},
          100, "JPY")
    s = client.get(f"/profiles/{a['id']}/earnings", headers=head).json()
    assert s["totals"]["mixed"] is True


def test_one_currency_reads_exactly_as_it_did(client):
    """The ordinary case is untouched, which is what makes this safe to ship:
    almost every account has one currency, and its statement is the same
    shape and the same numbers as before."""
    a, head = _owner(client, "acct_one")
    _sell(client, a, head, 49.0, "USD")
    s = client.get(f"/profiles/{a['id']}/earnings", headers=head).json()
    assert s["currency"] == "USD"
    assert s["totals"]["accrued"] == 49.0
    assert s["totals"]["by_kind"] == {"license_fee": 49.0}
    assert s["totals"]["mixed"] is False


# --- which currency the headline is in --------------------------------------

def test_the_headline_currency_does_not_follow_the_newest_sale():
    """It used to be `rows[0]["currency"]` under a newest-first sort, so the
    headline changed currency as sales arrived without any figure under it
    changing. Now it is the most-earned-in one, computed the same way twice.
    """
    rows = [{"currency": "USD", "amount": 10.0},
            {"currency": "USD", "amount": 10.0},
            {"currency": "JPY", "amount": 5000.0}]
    assert ledger.settlement_currency(rows) == "USD"
    assert ledger.settlement_currency(list(reversed(rows))) == "USD"


def test_a_tie_is_broken_by_size_then_by_name():
    """Deterministic all the way down. Two currencies with one entry each
    would otherwise depend on row order, which is the bug this replaced."""
    rows = [{"currency": "EUR", "amount": 5.0},
            {"currency": "USD", "amount": 50.0}]
    assert ledger.settlement_currency(rows) == "USD"
    same = [{"currency": "EUR", "amount": 5.0},
            {"currency": "USD", "amount": 5.0}]
    assert ledger.settlement_currency(same) == "EUR"


def test_an_empty_ledger_still_names_a_currency():
    assert ledger.settlement_currency([]) == "USD"


# --- payouts ----------------------------------------------------------------

def test_a_payout_settles_one_currency_and_says_which(client):
    a, head = _owner(client, "acct_pay")
    b = client.post("/profiles", json={
        "owner_id": "acct_pay", "kind": "fictional", "display_name": "N",
        "purpose": "enterprise_agent", "persona": "g",
        "verification": {"birthdate": "1988-03-03"}}).json()
    _sell(client, a, head, 100, "USD")
    _sell(client, a, head, 100, "USD")
    _sell(client, b, {"authorization": f"Bearer {b['owner_token']}"},
          100, "JPY")

    r = client.post(f"/profiles/{a['id']}/earnings/payout", headers=head)
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["currency"] == "USD"
    assert out["total_amount"] == 200.0 and out["entries_count"] == 2
    assert out["remaining"] == ["JPY"], (
        "a receipt that does not say money is still owed reads as 'paid'")


def test_pressing_it_again_sweeps_what_is_left(client):
    """A client that has never heard of currencies — all three native shells
    post an empty body — still gets paid everything, one press per
    currency, rather than being told there is nothing there."""
    a, head = _owner(client, "acct_again")
    b = client.post("/profiles", json={
        "owner_id": "acct_again", "kind": "fictional", "display_name": "N",
        "purpose": "enterprise_agent", "persona": "g",
        "verification": {"birthdate": "1988-03-03"}}).json()
    _sell(client, a, head, 100, "USD")
    _sell(client, b, {"authorization": f"Bearer {b['owner_token']}"},
          100, "JPY")

    first = client.post(f"/profiles/{a['id']}/earnings/payout",
                        headers=head).json()
    second = client.post(f"/profiles/{a['id']}/earnings/payout",
                         headers=head).json()
    assert {first["currency"], second["currency"]} == {"USD", "JPY"}
    assert second["remaining"] == []
    assert client.post(f"/profiles/{a['id']}/earnings/payout",
                       headers=head).status_code == 409


def test_asking_for_a_currency_you_do_not_hold_says_what_you_do(client):
    a, head = _owner(client, "acct_named_ccy")
    _sell(client, a, head, 100, "USD")
    r = client.post(f"/profiles/{a['id']}/earnings/payout?currency=JPY",
                    headers=head)
    assert r.status_code == 409
    assert "USD" in r.json()["detail"]


def test_a_named_currency_is_swept_alone(client):
    a, head = _owner(client, "acct_pick")
    b = client.post("/profiles", json={
        "owner_id": "acct_pick", "kind": "fictional", "display_name": "N",
        "purpose": "enterprise_agent", "persona": "g",
        "verification": {"birthdate": "1988-03-03"}}).json()
    _sell(client, a, head, 100, "USD")
    _sell(client, b, {"authorization": f"Bearer {b['owner_token']}"},
          100, "JPY")
    out = client.post(f"/profiles/{a['id']}/earnings/payout?currency=JPY",
                      headers=head).json()
    assert out["currency"] == "JPY" and out["remaining"] == ["USD"]


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    """Comments stripped, so a phrase that only appears in the docstring
    above a component cannot satisfy an assertion about what it renders."""
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_reads_mixed_before_it_draws_a_figure():
    """The flag has to be the *condition*, not merely mentioned.

    The first version of this asserted `"statement.totals.mixed" in src`,
    which a deliberate break sailed straight through: the payout buttons
    further down read the same flag, so the substring survived the headline's
    guard being replaced with `false`. Two occurrences, one assertion, and it
    was satisfied by the wrong one.
    """
    src = _markup("app/src/screens/Selling.tsx")
    assert "{statement.totals.mixed && (" in src, (
        "the breakdown is no longer conditional on `mixed`, so the screen "
        "either hides a second balance or shouts about one that is not "
        "there — the defect one layer up, moved into the console")
    # The sentence moved into the l10n table when the screen was localized;
    # the screen must still look it up, and the table must still say it.
    assert 'tr("sell.earn.mixed", lang)' in src, (
        "the sentence that tells the owner why there are two figures is gone")
    l10n = _markup("app/src/l10n.ts")
    assert "and the two are not added together" in l10n, (
        "the sentence that tells the owner why there are two figures is gone")
    assert "statement.by_currency[c]" in src


def test_the_screen_offers_a_payout_per_currency():
    """One button pays the settlement currency; a mixed account gets one per
    remaining currency, because the server settles one at a time."""
    src = _markup("app/src/screens/Selling.tsx")
    assert "api.requestPayout(me, token, c)" in src


def test_the_receipt_says_when_there_is_more(client):
    assert "receipt.remaining.length > 0" in _markup(
        "app/src/screens/Selling.tsx")
