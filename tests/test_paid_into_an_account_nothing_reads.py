"""A sale credited to a key nothing queries.

`GET /profiles/{id}/earnings` resolves the profile to its ``owner_id`` and
reads the ledger by that. `PUT /marketplace/listings/{id}/offer` recorded the
seller as ``auth.principal(request)["subject_id"]`` — and an **owner token's
subject is a profile, not an account**.

So a seller who priced a listing while signed in as their profile's owner got:

* `200` on the offer, with `seller_id` set to a profile id;
* `201` on the buyer's purchase, carrying a real `ledger_entry` and the
  sentence *the sale is recorded on the seller's statement*;
* an empty statement.

The money was written. It was written under a key nothing reads, and every
response along the way said it had gone through.

## Why it survived

Nobody could do it. The console had no way to price a listing — `api.setOffer`
existed in `api.ts` and no screen called it, which is precisely the class of
gap `test_a_binding_is_not_a_door.py` was written to find, and this defect is
what came out of paying the first one of them down. On the phone the Market
tab prices listings as an *interactor*, whose subject id already is the
account, so the one surface that could reach the route took the path that
happens to work.

## The rule, which already existed

`commerce.beneficiary_of` has resolved a profile to its ``owner_id`` since
gifts existed, for the same reason and in the same file. It was applied to
money coming in and not to money going out. `_earner` is that rule on the
other half.
"""

from __future__ import annotations

LISTING = {"kind": "service", "title": "Roof work", "blurb": "b",
           "tags": ["trade"], "provider_name": "Ash", "area": "trades"}


def _owner(client, account="acct_sell"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Ash",
        "purpose": "enterprise_agent", "persona": "a tradesperson",
        "verification": {"birthdate": "1988-03-03"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p, head


def _buyer(client, name="Buyer"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": "1985-01-01"}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


# --- the defect -------------------------------------------------------------

def test_a_sale_priced_with_an_owner_token_reaches_the_statement(client):
    """The one this file exists for. Sold for 200, and the statement said
    nothing had ever been earned."""
    p, head = _owner(client, "acct_owner_sale")
    lid = client.post("/marketplace/listings", json=LISTING,
                      headers=head).json()["id"]
    r = client.put(f"/marketplace/listings/{lid}/offer", headers=head,
                   json={"price": 200, "currency": "USD"})
    assert r.status_code == 200, r.text

    _bid, buyer = _buyer(client)
    bought = client.post(f"/marketplace/listings/{lid}/purchase",
                         headers=buyer, json={"accept_price": 200})
    assert bought.status_code == 201, bought.text
    assert bought.json()["ledger_entry"], "no ledger entry was written at all"

    s = client.get(f"/profiles/{p['id']}/earnings", headers=head).json()
    assert s["totals"]["accrued"] == 200.0, (
        "the sale is not on the seller's statement, which is what every "
        "response in this flow said it would be")
    assert s["entries"][0]["beneficiary"] == "acct_owner_sale"


def test_the_offer_records_the_account_not_the_profile(client):
    """Visible in the offer itself, which is where it would have been caught
    by anybody reading the response."""
    p, head = _owner(client, "acct_recorded")
    lid = client.post("/marketplace/listings", json=LISTING,
                      headers=head).json()["id"]
    offer = client.put(f"/marketplace/listings/{lid}/offer", headers=head,
                       json={"price": 10, "currency": "USD"}).json()
    assert offer["seller_id"] == "acct_recorded"
    assert offer["seller_id"] != p["id"]


def test_an_interactor_seller_is_unchanged(client):
    """The path that already worked, pinned so the fix cannot break it. An
    interactor's subject id *is* the account, so nothing about this flow
    should have moved."""
    sid, seller = _buyer(client, "Seller")
    lid = client.post("/marketplace/listings", json=LISTING,
                      headers=seller).json()["id"]
    offer = client.put(f"/marketplace/listings/{lid}/offer", headers=seller,
                       json={"price": 30, "currency": "USD"}).json()
    assert offer["seller_id"] == sid


# --- the neighbouring routes that read the same key -------------------------

def test_withdrawing_is_still_the_sellers_alone(client):
    """`withdraw` compares the caller against the stored `seller_id`, so
    moving what is stored had to move what is compared. Both halves, or the
    seller locks themselves out of their own offer."""
    p, head = _owner(client, "acct_withdraw")
    lid = client.post("/marketplace/listings", json=LISTING,
                      headers=head).json()["id"]
    client.put(f"/marketplace/listings/{lid}/offer", headers=head,
               json={"price": 15, "currency": "USD"})
    _sid, stranger = _buyer(client, "Stranger")
    assert client.delete(f"/marketplace/listings/{lid}/offer",
                         headers=stranger).status_code == 403
    assert client.delete(f"/marketplace/listings/{lid}/offer",
                         headers=head).status_code == 200


def test_the_sales_list_finds_the_same_sales(client):
    """`GET /marketplace/sales` reads orders by seller id. It has to be
    resolved the same way or a seller sees an empty list beside a statement
    that is not empty — which is the original defect wearing a different
    coat."""
    p, head = _owner(client, "acct_sales")
    lid = client.post("/marketplace/listings", json=LISTING,
                      headers=head).json()["id"]
    client.put(f"/marketplace/listings/{lid}/offer", headers=head,
               json={"price": 40, "currency": "USD"})
    _bid, buyer = _buyer(client)
    client.post(f"/marketplace/listings/{lid}/purchase", headers=buyer,
                json={"accept_price": 40})
    sales = client.get("/marketplace/sales", headers=head).json()["sales"]
    assert len(sales) == 1 and sales[0]["price"] == 40.0


def test_two_profiles_on_one_account_share_the_statement(client):
    """The consequence worth stating: the ledger is per account, so a seller
    prices from whichever profile is to hand and is paid once. Before the fix
    they would have had one silent balance per profile."""
    a, ahead = _owner(client, "acct_shared")
    b = client.post("/profiles", json={
        "owner_id": "acct_shared", "kind": "fictional", "display_name": "Two",
        "purpose": "enterprise_agent", "persona": "a tradesperson",
        "verification": {"birthdate": "1988-03-03"}}).json()
    bhead = {"authorization": f"Bearer {b['owner_token']}"}

    for head in (ahead, bhead):
        lid = client.post("/marketplace/listings", json=LISTING,
                          headers=head).json()["id"]
        client.put(f"/marketplace/listings/{lid}/offer", headers=head,
                   json={"price": 50, "currency": "USD"})
        _bid, buyer = _buyer(client, f"B{lid[-4:]}")
        client.post(f"/marketplace/listings/{lid}/purchase", headers=buyer,
                    json={"accept_price": 50})

    s = client.get(f"/profiles/{a['id']}/earnings", headers=ahead).json()
    assert s["totals"]["accrued"] == 100.0
    assert len(s["entries"]) == 2


def test_a_gift_still_lands_where_it_always_did(client):
    """The half of the money that was already right, checked because the fix
    was written by reading it."""
    p, head = _owner(client, "acct_gift")
    _gid, giver = _buyer(client, "Giver")
    r = client.post(f"/profiles/{p['id']}/gift", headers=giver,
                    json={"amount": 5, "currency": "USD"})
    assert r.status_code == 201, r.text
    s = client.get(f"/profiles/{p['id']}/earnings", headers=head).json()
    assert s["totals"]["accrued"] == 5.0
