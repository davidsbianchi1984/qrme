"""The agent screen's "Search the Internet" opener stands on a real door.

The opener existed as a sentence before it existed as a capability, on a
deployment with no model and no key configured. So the door is keyless — the
engine is DuckDuckGo's instant-answer API — and these tests hold the three
things that make it safe to offer: the query is the whole of what leaves,
the answer has one shape including when it is empty, and every trip off the
host is gated and attributed like the rest of them.
"""

from __future__ import annotations

import pytest

from qrme import websearch


def a_profile(client, owner="owner-s"):
    r = client.post("/profiles", json={
        "owner_id": owner, "kind": "self", "display_name": "Dana",
        "persona": "A retired teacher who likes gardening and dry humor.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert r.status_code == 201, r.text
    return r.json()["id"], r.json()["owner_token"]


def head(token):
    return {"authorization": f"Bearer {token}"}


# --- the door ---------------------------------------------------------------

def test_a_search_is_the_owners_errand(client, monkeypatch):
    """Signed out is 401 and somebody else is 403 — the trip is witnessed
    under this profile's name, so only its owner gets to make it."""
    pid, tok = a_profile(client)
    monkeypatch.setattr(websearch, "_fetch", lambda url, who: {})
    assert client.get(f"/profiles/{pid}/search?q=x").status_code == 401
    _, other = a_profile(client, owner="owner-else")
    assert client.get(f"/profiles/{pid}/search?q=x",
                      headers=head(other)).status_code == 403
    assert client.get(f"/profiles/{pid}/search?q=x",
                      headers=head(tok)).status_code == 200


def test_an_empty_query_refuses_before_the_engine_is_reached(client,
                                                             monkeypatch):
    pid, tok = a_profile(client)
    called = []
    monkeypatch.setattr(websearch, "_fetch",
                        lambda url, who: called.append(1) or {})
    r = client.get(f"/profiles/{pid}/search?q=%20%20", headers=head(tok))
    assert r.status_code == 422
    assert not called, "the engine was reached with nothing to ask it"


def test_only_the_query_leaves_and_the_errand_is_named(client, monkeypatch):
    """What crosses the wire is the query — never who asked — and the
    fetch is told whose errand it is, for the visits ledger."""
    pid, tok = a_profile(client)
    asked = {}
    monkeypatch.setattr(
        websearch, "_fetch",
        lambda url, who: asked.update(url=url, who=who) or {})
    r = client.get(f"/profiles/{pid}/search?q=weather+in+lisbon",
                   headers=head(tok))
    assert r.status_code == 200
    assert asked["who"] == pid
    assert "weather+in+lisbon" in asked["url"].replace("%20", "+")
    assert pid not in asked["url"], "the asker leaked into the query string"


# --- the shape --------------------------------------------------------------

def test_the_answer_has_one_shape_even_empty(client, monkeypatch):
    """An instant-answer engine finding nothing is not the web having
    nothing: the empty answer still carries `more_url`, so a screen always
    has somewhere honest to send the person."""
    pid, tok = a_profile(client)
    monkeypatch.setattr(websearch, "_fetch", lambda url, who: {})
    r = client.get(f"/profiles/{pid}/search?q=xyzzy", headers=head(tok))
    body = r.json()
    assert set(body) == {"q", "engine", "pages", "more_url"}
    assert body["pages"] == []
    assert "duckduckgo.com" in body["more_url"]
    assert "xyzzy" in body["more_url"]


def test_the_engines_nesting_is_flattened_to_rows(client, monkeypatch):
    """Abstract plus nested related topics in, one row shape out — every
    row carries all three keys, empty strings where the engine had
    nothing."""
    pid, tok = a_profile(client)
    monkeypatch.setattr(websearch, "_fetch", lambda url, who: {
        "Heading": "Lisbon",
        "AbstractText": "The capital of Portugal.",
        "AbstractURL": "https://en.wikipedia.org/wiki/Lisbon",
        "RelatedTopics": [
            {"FirstURL": "https://a.example", "Text": "A - first thing"},
            {"Topics": [
                {"FirstURL": "https://b.example", "Text": "B - nested thing"},
            ]},
        ],
    })
    rows = client.get(f"/profiles/{pid}/search?q=lisbon",
                      headers=head(tok)).json()["pages"]
    assert rows[0] == {"title": "Lisbon",
                       "url": "https://en.wikipedia.org/wiki/Lisbon",
                       "note": "The capital of Portugal."}
    assert {r["url"] for r in rows[1:]} == {"https://a.example",
                                            "https://b.example"}
    for row in rows:
        assert set(row) == {"title", "url", "note"}


def test_the_row_count_has_a_ceiling(client, monkeypatch):
    pid, tok = a_profile(client)
    monkeypatch.setattr(websearch, "_fetch", lambda url, who: {
        "RelatedTopics": [{"FirstURL": f"https://x.example/{i}",
                           "Text": f"thing {i}"} for i in range(40)],
    })
    rows = client.get(f"/profiles/{pid}/search?q=things",
                      headers=head(tok)).json()["pages"]
    assert len(rows) == websearch.MAX_RESULTS


# --- the failures, in sentences ---------------------------------------------

def test_an_unreachable_engine_is_a_sentence_not_a_stack(client, monkeypatch):
    import urllib.error

    def down(req, timeout=0):
        raise urllib.error.URLError("nope")

    # The seam sits below `_fetch`, so the real `_fetch` translates.
    pid, tok = a_profile(client)
    monkeypatch.setattr(websearch.urllib.request, "urlopen", down)
    r = client.get(f"/profiles/{pid}/search?q=x", headers=head(tok))
    assert r.status_code == 422
    assert "could not be reached" in str(r.json()["detail"])


def test_a_long_query_is_trimmed_not_refused(client, monkeypatch):
    """A search engine trimming a query is ordinary behaviour; the one
    button that needs no setup must not be the one that argues."""
    pid, tok = a_profile(client)
    seen = {}
    monkeypatch.setattr(websearch, "_fetch",
                        lambda url, who: seen.update(url=url) or {})
    q = "a" * (websearch.MAX_QUERY * 2)
    r = client.get(f"/profiles/{pid}/search?q={q}", headers=head(tok))
    assert r.status_code == 200
    assert r.json()["q"] == "a" * websearch.MAX_QUERY
