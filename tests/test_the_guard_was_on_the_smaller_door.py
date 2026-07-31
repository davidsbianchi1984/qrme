"""Anyone could delete anyone's listing.

`DELETE /marketplace/listings/{id}/offer` asks who you are and answers *not
your offer*. `DELETE /marketplace/listings/{id}` — which destroys strictly
more — asked nothing at all. A stranger could remove a listing that had a
recorded seller, an open offer and paid orders against it, and the offer,
the orders and the seller's ledger all survived: the shop window was simply
gone, the title free for somebody else to put up.

The argument against it was already written down, one file over, in the
docstring of the endpoint that *does* check:

    Anyone can create a listing — that endpoint has never needed a token —
    so the seller is established here, where money starts, rather than back
    there where it did not exist.

That reasoning is right about creation and says nothing about removal, which
is how the gap survived being read.

## The rule

A listing is claimed by whoever staked something on it:

* the **creator**, when they were signed in — recorded in `listing_claims`,
  a side table for the same reason `listing_offers` is one;
* the **seller** on its offer, the account a purchase pays;
* the **owner** of the profile it advertises.

An empty claimant set is a real answer, not a missing one. A listing made by
an anonymous caller, never priced, advertising nobody, has nothing staked on
it and anyone may clear it away — which is the honest reading of an endpoint
that needs no token: if it costs nothing to make, it costs nothing to remove.
The seeded starter collection is exactly that case, deliberately.

Moving a listing is gated the same way. Sending somebody's listing to another
city is a quieter version of taking it down: it stops being found by the
people it was put up for, and nothing about it looks wrong.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

LISTING = {"kind": "service", "title": "Roof repair", "blurb": "b",
           "tags": ["trade"], "provider_name": "Sam", "area": "trades"}


def _person(client, name="P", birthdate="1985-01-01"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


def _listing(client, head=None, **over):
    body = {**LISTING, **over}
    r = client.post("/marketplace/listings", json=body,
                    headers=head or {})
    assert r.status_code == 201, r.text
    return r.json()


# --- the defect -------------------------------------------------------------

def test_a_stranger_cannot_delete_a_listing_with_a_seller(client):
    """The one this file exists for. Everything about this listing said it
    belonged to somebody, and the delete route did not ask."""
    _, seller = _person(client, "Seller")
    _, stranger = _person(client, "Stranger")
    _, buyer = _person(client, "Buyer")
    row = _listing(client, seller)

    client.put(f"/marketplace/listings/{row['id']}/offer", headers=seller,
               json={"price": 120, "currency": "USD", "stock": 3})
    client.post(f"/marketplace/listings/{row['id']}/purchase", headers=buyer,
                json={"accept_price": 120})

    # The rule already existed on the neighbouring route.
    assert client.delete(f"/marketplace/listings/{row['id']}/offer",
                         headers=stranger).status_code == 403
    r = client.delete(f"/marketplace/listings/{row['id']}", headers=stranger)
    assert r.status_code == 403
    assert "not your listing" in r.json()["detail"]


def test_the_seller_can(client):
    """The point is the credential, not the friction. Whoever is owed the
    money on it may take it down."""
    _, seller = _person(client, "Seller")
    row = _listing(client, seller)
    client.put(f"/marketplace/listings/{row['id']}/offer", headers=seller,
               json={"price": 10, "currency": "USD"})
    assert client.delete(f"/marketplace/listings/{row['id']}",
                         headers=seller).status_code == 204


def test_the_creator_can_even_with_no_offer_on_it(client):
    """A listing with no price still belongs to whoever put it up, provided
    they were signed in when they did."""
    _, mine = _person(client, "Mine")
    _, other = _person(client, "Other")
    row = _listing(client, mine)
    assert row["claimed_by"] is not None
    assert client.delete(f"/marketplace/listings/{row['id']}",
                         headers=other).status_code == 403
    assert client.delete(f"/marketplace/listings/{row['id']}",
                         headers=mine).status_code == 204


def test_the_owner_of_the_profile_it_advertises_can(client, profile_id):
    """A profile listing advertises somebody. They did not necessarily
    create it — the third claimant exists for exactly that.

    `profile_id` leaves the owner's token on the client, so the delete below
    goes out as the owner while the create went out as the stranger.
    """
    _, stranger = _person(client, "Stranger")
    row = _listing(client, stranger, kind="profile", profile_id=profile_id,
                   title="Somebody else's profile")
    assert client.delete(f"/marketplace/listings/{row['id']}"
                         ).status_code == 204


# --- what is deliberately still open ----------------------------------------

def test_creating_one_still_needs_no_token(client):
    """Unchanged, and on purpose. The seller is established when a price is
    attached; tightening creation would be a different decision than the one
    this fixes, and the schema comment says so."""
    r = client.post("/marketplace/listings", json=LISTING)
    assert r.status_code == 201
    assert r.json()["claimed_by"] is None


def test_a_listing_nobody_staked_anything_on_is_anybodys_to_clear(client):
    """The honest end of "anyone can create one". No creator, no offer, no
    profile — nothing is taken from anybody by removing it, and requiring a
    credential would leave anonymous litter permanently unclearable."""
    row = _listing(client)          # no token at all
    _, anybody = _person(client, "Anybody")
    assert client.delete(f"/marketplace/listings/{row['id']}",
                         headers=anybody).status_code == 204


def test_seeding_claims_the_profile_listings_and_not_the_pack_ones(client):
    """The seeders pass no claimant, and the rule still tells the two kinds
    of starter listing apart — which is the check that showed this test's
    first premise was wrong.

    A seeded **profile** listing advertises a real starter profile, and that
    profile's owner claims it through the third route: nobody created it and
    nothing is priced on it, and it is still not a stranger's to remove. A
    seeded **expertise** listing is a knowledge pack in the window, naming no
    profile at all, and it is exactly the litter case — anybody may clear it.
    """
    client.post("/marketplace/seed")
    client.post("/packs/seed")
    listings = client.get("/marketplace/listings").json()
    profiles = [l for l in listings if l.get("profile_id")]
    packs = [l for l in listings if not l.get("profile_id")]
    assert profiles and packs, "seeding produced only one kind to check"

    _, anybody = _person(client, "Anybody")
    assert client.delete(f"/marketplace/listings/{profiles[0]['id']}",
                         headers=anybody).status_code == 403
    assert client.delete(f"/marketplace/listings/{packs[0]['id']}",
                         headers=anybody).status_code == 204


def test_a_missing_listing_is_a_404_not_a_403(client):
    """Order matters: existence is checked first, so a caller is not told
    'not yours' about something that is not there."""
    _, anybody = _person(client, "Anybody")
    assert client.delete("/marketplace/listings/lst_nope",
                         headers=anybody).status_code == 404


# --- moving one -------------------------------------------------------------

def test_a_stranger_cannot_move_somebody_elses_listing(client):
    _, mine = _person(client, "Mine")
    _, other = _person(client, "Other")
    row = _listing(client, mine)
    r = client.put(f"/marketplace/listings/{row['id']}/place", headers=other,
                   json={"locality": "Leeds", "region": "UK",
                         "remote": False})
    assert r.status_code == 403
    assert client.put(f"/marketplace/listings/{row['id']}/place",
                      headers=mine,
                      json={"locality": "Leeds", "region": "UK",
                            "remote": False}).status_code == 200


def test_a_stranger_cannot_clear_where_it_is(client):
    _, mine = _person(client, "Mine")
    _, other = _person(client, "Other")
    row = _listing(client, mine)
    client.put(f"/marketplace/listings/{row['id']}/place", headers=mine,
               json={"locality": "Leeds", "region": "UK", "remote": False})
    assert client.delete(f"/marketplace/listings/{row['id']}/place",
                         headers=other).status_code == 403


# --- the console half -------------------------------------------------------

def _markup(rel: str) -> str:
    s = (REPO / rel).read_text(encoding="utf-8")
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_says_who_may_take_one_down():
    src = _markup("app/src/screens/Selling.tsx")
    assert "Only a claimant may take a listing down" in src


def test_the_screen_calls_both_ends():
    src = (REPO / "app/src/screens/Selling.tsx").read_text(encoding="utf-8")
    assert "api.createListing(" in src and "api.removeListing(" in src
