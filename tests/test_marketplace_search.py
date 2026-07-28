"""Marketplace search: words, place, settings, and a hand with the words.

Three claims carry this, and most of what follows tries to break one:

* **Ranking is deterministic.** No model reorders results, so the same
  arguments give the same order and the response can say why each hit landed.
* **A rated listing can never carry a place**, so no place filter can ever
  surface one — the structural version of "where a performer physically is has
  nothing to do with browsing them".
* **The assistant returns suggestions, never results.** There is no code path
  from it into the search, so a model can change what is in your search box
  and nothing else.
"""

import json

import pytest

from qrme import marketplace

ADULT = {"birthdate": "1984-06-01"}


def _listing(client, **over):
    body = {"kind": "service", "title": "Lease review and tenant rights",
            "blurb": "Read your lease before you sign", "tags": ["legal", "housing"],
            "area": "legal", "provider_name": "Ashe Legal"}
    body.update(over)
    r = client.post("/marketplace/listings", json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _rated_listing(client):
    r = client.post("/profiles", json={
        "plan": "pro", "owner_id": "owner-1", "kind": "fictional", "display_name": "Velvet Ivy",
        "adult_mode": True, "maturity": "open",
        "persona": "A cabaret hostess persona for adult audiences.",
        "verification": ADULT})
    assert r.status_code == 201, r.text
    pid = r.json()["id"]
    return pid, _listing(client, kind="profile", profile_id=pid,
                         title="Velvet Ivy — cabaret", tags=["cabaret"],
                         area="entertainment", provider_name="Velvet")


def _interactor(client, name="Sam"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-03-03"})
    body = r.json()
    return body["id"], {"authorization": f"Bearer {body['token']}"}


class _FakeProvider:
    """A model that says exactly what the test tells it to."""

    def __init__(self, reply="lease review\ntenant rights\nhousing lawyer",
                 boom=False):
        self.reply, self.boom, self.saw = reply, boom, []

    def generate(self, system, messages):
        if self.boom:
            raise RuntimeError("provider down")
        self.saw.append(messages[-1]["content"])
        return self.reply


# --- words -----------------------------------------------------------------

def test_plain_words_find_a_listing_without_knowing_its_tag(client):
    """The point of text search: "help me read a lease" should find the legal
    listing without the searcher knowing the tag is `legal`."""
    _listing(client)
    _listing(client, title="Nutrition coaching", blurb="Meal plans",
             tags=["nutrition"], area="healthcare", provider_name="Sana")

    body = client.get("/marketplace/search",
                      params={"q": "someone who can help me read a lease"}).json()
    assert [r["title"] for r in body["results"]] == ["Lease review and tenant rights"]
    assert "title" in body["results"][0]["matched_on"]


def test_a_title_hit_outranks_a_blurb_hit(client):
    _listing(client, title="Contract lawyer", blurb="Small business contracts",
             tags=["legal"], provider_name="Remote Legal Co")
    _listing(client, title="Bookkeeping", blurb="We also review a contract",
             tags=["finance"], provider_name="Ledger Co")

    body = client.get("/marketplace/search", params={"q": "contract"}).json()
    assert body["results"][0]["title"] == "Contract lawyer"
    assert body["results"][0]["score"] > body["results"][1]["score"]


def test_ranking_is_deterministic_and_says_why(client):
    for i in range(4):
        _listing(client, title=f"Legal help {i}", provider_name=f"P{i}")
    first = client.get("/marketplace/search", params={"q": "legal"}).json()
    second = client.get("/marketplace/search", params={"q": "legal"}).json()
    assert [r["id"] for r in first["results"]] == [r["id"] for r in second["results"]]
    assert "No model reorders this" in first["ranking"]
    assert first["terms"] == ["legal"]


def test_a_query_that_matches_nothing_returns_nothing(client):
    _listing(client)
    body = client.get("/marketplace/search", params={"q": "astrophysics"}).json()
    assert body["results"] == [] and body["total"] == 0


# --- place -----------------------------------------------------------------

def test_a_place_is_not_the_subject_area(client):
    """`listings.area` is healthcare/finance/legal. Geography is its own
    table, or "near me" quietly means "in healthcare"."""
    lid = _listing(client, area="legal")
    client.put(f"/marketplace/listings/{lid}/place",
               json={"locality": "Oakland, CA", "region": "California"})

    body = client.get("/marketplace/search",
                      params={"scope": "locality", "locality": "Oakland, CA"}).json()
    assert body["results"][0]["area"] == "legal"
    assert body["results"][0]["place"]["locality"] == "Oakland, CA"


def test_narrowing_to_a_place_hides_the_placeless_and_counts_them(client):
    near = _listing(client, title="Local lawyer")
    _listing(client, title="Lawyer with no place given")
    client.put(f"/marketplace/listings/{near}/place", json={"locality": "Oakland, CA"})

    body = client.get("/marketplace/search",
                      params={"scope": "locality", "locality": "Oakland, CA"}).json()
    assert [r["title"] for r in body["results"]] == ["Local lawyer"]
    # Said out loud, so an empty-looking marketplace is explicable.
    assert body["hidden_by_place"] == 1


def test_a_remote_listing_reaches_past_its_own_locality(client):
    far = _listing(client, title="Contract lawyer", provider_name="Remote Legal Co")
    client.put(f"/marketplace/listings/{far}/place",
               json={"locality": "Austin, TX", "region": "Texas", "remote": True})

    near = client.get("/marketplace/search",
                      params={"scope": "locality", "locality": "Oakland, CA"}).json()
    assert [r["title"] for r in near["results"]] == ["Contract lawyer"]

    excluded = client.get("/marketplace/search",
                          params={"scope": "locality", "locality": "Oakland, CA",
                                  "include_remote": "false"}).json()
    assert excluded["results"] == []


def test_localities_lists_what_actually_exists(client):
    a, b = _listing(client, title="One"), _listing(client, title="Two")
    client.put(f"/marketplace/listings/{a}/place", json={"locality": "Oakland, CA"})
    client.put(f"/marketplace/listings/{b}/place", json={"locality": "Oakland, CA"})
    body = client.get("/marketplace/localities").json()
    assert body == [{"locality": "Oakland, CA", "region": None, "listings": 2}]


def test_a_place_needs_a_locality(client):
    lid = _listing(client)
    r = client.put(f"/marketplace/listings/{lid}/place", json={"locality": "  "})
    assert r.status_code == 422


def test_clearing_a_place_returns_the_listing_to_anywhere(client):
    lid = _listing(client)
    client.put(f"/marketplace/listings/{lid}/place", json={"locality": "Oakland, CA"})
    client.delete(f"/marketplace/listings/{lid}/place")
    body = client.get("/marketplace/search",
                      params={"scope": "locality", "locality": "Oakland, CA"}).json()
    assert body["results"] == [] and body["hidden_by_place"] == 1


# --- the line that does not move -------------------------------------------

def test_a_rated_listing_cannot_carry_a_location(client):
    """Where a performer physically is has nothing to do with browsing them,
    and a place filter is a way of asking. Refused, not silently ignored."""
    _pid, lid = _rated_listing(client)
    r = client.put(f"/marketplace/listings/{lid}/place",
                   json={"locality": "Oakland, CA"})
    assert r.status_code == 422
    assert "physically is" in r.text


def test_no_place_filter_can_surface_a_rated_listing(client):
    """Structural rather than checked: the refusal above means no row exists,
    so there is nothing for a place filter to match — even for an adult."""
    _pid, _lid = _rated_listing(client)
    _hdr = _interactor(client, "Adult")[1]
    r = client.post("/interactors", json={"display_name": "Adult",
                                          "birthdate": "1984-06-01"})
    adult = {"authorization": f"Bearer {r.json()['token']}"}

    body = client.get("/marketplace/search",
                      params={"scope": "locality", "locality": "Oakland, CA"},
                      headers=adult).json()
    assert body["results"] == []
    assert marketplace.place_of(_lid) is None


def test_a_rated_listing_still_never_surfaces_unverified(client):
    """The pre-existing rule, unchanged by any of this."""
    _pid, _lid = _rated_listing(client)
    body = client.get("/marketplace/search", params={"q": "cabaret"}).json()
    assert body["results"] == []


# --- settings ---------------------------------------------------------------

def test_settings_are_saved_and_are_the_owners_alone(client):
    mine, my_hdr = _interactor(client, "Mine")
    _theirs, their_hdr = _interactor(client, "Theirs")

    r = client.put(f"/marketplace/settings/{mine}",
                   json={"locality": "Oakland, CA", "scope": "locality"},
                   headers=my_hdr)
    assert r.status_code == 200 and r.json()["scope"] == "locality"
    assert client.get(f"/marketplace/settings/{mine}",
                      headers=their_hdr).status_code == 403


def test_settings_are_defaults_not_a_cage(client):
    mine, hdr = _interactor(client)
    near = _listing(client, title="Oakland lawyer")
    far = _listing(client, title="Austin lawyer")
    client.put(f"/marketplace/listings/{near}/place", json={"locality": "Oakland, CA"})
    client.put(f"/marketplace/listings/{far}/place", json={"locality": "Austin, TX"})
    client.put(f"/marketplace/settings/{mine}",
               json={"locality": "Oakland, CA", "scope": "locality"}, headers=hdr)

    default = client.get("/marketplace/search", params={"q": "lawyer"},
                         headers=hdr).json()
    assert [r["title"] for r in default["results"]] == ["Oakland lawyer"]

    # An explicitly typed locality wins over the saved one.
    typed = client.get("/marketplace/search",
                       params={"q": "lawyer", "scope": "locality",
                               "locality": "Austin, TX"}, headers=hdr).json()
    assert [r["title"] for r in typed["results"]] == ["Austin lawyer"]


def test_narrowing_to_a_place_you_have_not_named_is_refused(client):
    mine, hdr = _interactor(client)
    r = client.put(f"/marketplace/settings/{mine}", json={"scope": "locality"},
                   headers=hdr)
    # Silently returning nothing would look like an empty marketplace.
    assert r.status_code == 422 and "needs a locality" in r.text


def test_an_unknown_listing_kind_is_refused(client):
    mine, hdr = _interactor(client)
    r = client.put(f"/marketplace/settings/{mine}",
                   json={"kinds": ["spaceship"]}, headers=hdr)
    assert r.status_code == 422


# --- a hand with the words --------------------------------------------------

def test_the_assistant_returns_suggestions_and_never_results(client):
    _listing(client)
    body = client.post("/marketplace/assist",
                       json={"need": "I need help understanding a rental agreement"}).json()
    assert body["suggestions"]
    assert body["applied"] is False
    assert "results" not in body
    assert "nothing has been searched" in body["note"]


def test_a_model_writes_the_box_and_nothing_else(client):
    """The model's output reaches a suggestion list. There is no code path
    from here into the search, so it cannot reorder or filter anything."""
    fake = _FakeProvider()
    out = marketplace.assist("help me with my lease", provider=fake)
    assert out["source"] == "model" and out["ai"] is True
    assert out["suggestions"] == ["lease review", "tenant rights", "housing lawyer"]
    assert out["applied"] is False


def test_the_assistant_degrades_rather_than_failing(client):
    """A provider outage must not leave somebody stuck at an empty box."""
    out = marketplace.assist("help me with my lease",
                             provider=_FakeProvider(boom=True))
    assert out["source"] == "local" and out["ai"] is False
    assert out["suggestions"]


def test_the_assistant_caps_what_it_offers(client):
    fake = _FakeProvider(reply="\n".join(f"idea {i}" for i in range(9)))
    out = marketplace.assist("anything", provider=fake)
    assert len(out["suggestions"]) == marketplace.MAX_SUGGESTIONS


def test_the_assistant_needs_something_to_work_from(client):
    r = client.post("/marketplace/assist", json={"need": "   "})
    assert r.status_code == 422


def test_the_assistant_shows_the_settings_it_would_be_searched_under(client):
    mine, hdr = _interactor(client)
    client.put(f"/marketplace/settings/{mine}",
               json={"locality": "Oakland, CA", "scope": "locality"}, headers=hdr)
    body = client.post("/marketplace/assist", json={"need": "a lawyer"},
                       headers=hdr).json()
    assert body["your_settings"]["locality"] == "Oakland, CA"
