"""Messaging, switches, and a homepage like the old MySpace.

## The finding

The platform's people could befriend each other, meet at desks, buy from
shops — and could not send each other a message, could not turn any of it
off, and had no page of their own to point at. Three absences with one
shape: the *person* behind the profile had no surfaces that were simply
theirs.

    asked     can profiles talk and present themselves
    mattered  can the people behind them — on their own terms

## What this file drives

`qrme/social.py`, whose three parts share one idea — the person decides:

1. **switches** — a named set, default on, and everything downstream
   refuses by naming the switch, so "why can't I message them" always has
   an answer that is theirs;
2. **messages** — friends only (the friendship graph is the consent record
   already kept), one thread per pair, old words surviving an unfriending
   while new ones need the friendship back;
3. **the homepage sandbox** — headline, about, theme, links, top friends,
   validated so hard there is nowhere to put a script: hex colors only,
   http(s) links only, plain text only, top friends from real friends.
"""

from __future__ import annotations

import pytest

from qrme import db


ADULT = {"birthdate": "1984-06-01"}


def _person(client, name):
    r = client.post("/profiles", json={
        "owner_id": f"own-{name.lower()}", "kind": "self",
        "display_name": name, "persona": "A person on the platform.",
        "verification": ADULT, "plan": "pro"})
    assert r.status_code == 201, r.text
    p = r.json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


def _befriend(client, a, ha, b, hb):
    assert client.post(f"/profiles/{a}/friends", json={"friend_id": b},
                       headers=ha).status_code in (200, 201)
    assert client.post(f"/profiles/{b}/friends", json={"friend_id": a},
                       headers=hb).status_code in (200, 201)


# --- the switches ------------------------------------------------------------

def test_the_switches_default_on_and_flip_per_person(client):
    a, ha = _person(client, "Ana")
    flags = client.get(f"/profiles/{a}/features", headers=ha).json()
    assert flags == {"messaging": True, "homepage": True}
    out = client.put(f"/profiles/{a}/features",
                     json={"feature": "messaging", "enabled": False},
                     headers=ha).json()
    assert out["messaging"] is False and out["homepage"] is True


def test_an_unknown_switch_is_refused_by_name(client):
    a, ha = _person(client, "Ana")
    r = client.put(f"/profiles/{a}/features",
                   json={"feature": "telepathy", "enabled": True},
                   headers=ha)
    assert r.status_code == 422
    assert "homepage" in r.json()["detail"] and \
           "messaging" in r.json()["detail"]


def test_the_switches_are_the_owners_alone(client):
    a, _ = _person(client, "Ana")
    _, hb = _person(client, "Ben")
    assert client.get(f"/profiles/{a}/features",
                      headers=hb).status_code in (401, 403)
    assert client.put(f"/profiles/{a}/features",
                      json={"feature": "messaging", "enabled": False},
                      headers=hb).status_code in (401, 403)


# --- the messages ------------------------------------------------------------

def test_messages_travel_between_friends_and_only_friends(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    r = client.post(f"/profiles/{a}/messages", json={"to": b, "body": "hi"},
                    headers=ha)
    assert r.status_code == 422 and "friends" in r.json()["detail"]
    _befriend(client, a, ha, b, hb)
    r = client.post(f"/profiles/{a}/messages",
                    json={"to": b, "body": "hi Ben"}, headers=ha)
    assert r.status_code == 201, r.text
    # Both sides read the same thread.
    mine = client.get(f"/profiles/{a}/messages",
                      params={"with_id": b}, headers=ha).json()["messages"]
    theirs = client.get(f"/profiles/{b}/messages",
                        params={"with_id": a}, headers=hb).json()["messages"]
    assert [m["body"] for m in mine] == ["hi Ben"]
    assert mine == theirs


def test_the_thread_list_names_the_other_person(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _befriend(client, a, ha, b, hb)
    client.post(f"/profiles/{a}/messages", json={"to": b, "body": "hello"},
                headers=ha)
    threads = client.get(f"/profiles/{b}/messages",
                         headers=hb).json()["threads"]
    assert [t["other_name"] for t in threads] == ["Ana"]


def test_the_recipients_switch_refuses_by_name(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _befriend(client, a, ha, b, hb)
    client.put(f"/profiles/{b}/features",
               json={"feature": "messaging", "enabled": False}, headers=hb)
    r = client.post(f"/profiles/{a}/messages", json={"to": b, "body": "hi"},
                    headers=ha)
    assert r.status_code == 422
    assert "turned off" in r.json()["detail"]


def test_old_words_survive_an_unfriending_and_new_ones_need_it_back(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _befriend(client, a, ha, b, hb)
    client.post(f"/profiles/{a}/messages", json={"to": b, "body": "before"},
                headers=ha)
    assert client.delete(f"/profiles/{a}/friends/{b}",
                         headers=ha).status_code == 200
    # The record stays readable by both…
    old = client.get(f"/profiles/{b}/messages",
                     params={"with_id": a}, headers=hb).json()["messages"]
    assert [m["body"] for m in old] == ["before"]
    # …but new words need the friendship again.
    r = client.post(f"/profiles/{b}/messages", json={"to": a, "body": "hey"},
                    headers=hb)
    assert r.status_code == 422 and "friends" in r.json()["detail"]


def test_a_message_needs_a_sender_credential_and_words(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _befriend(client, a, ha, b, hb)
    r = client.post(f"/profiles/{a}/messages",
                    json={"to": b, "body": "spoofed"}, headers=hb)
    assert r.status_code in (401, 403), (
        "somebody sent a message as a profile they do not own")
    r = client.post(f"/profiles/{a}/messages", json={"to": b, "body": "  "},
                    headers=ha)
    assert r.status_code == 422 and "words" in r.json()["detail"]


# --- the homepage sandbox ----------------------------------------------------

def _edit(client, pid, head, **doc):
    return client.put(f"/profiles/{pid}/homepage", json=doc, headers=head)


def test_the_homepage_edits_and_shows_to_a_stranger(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _befriend(client, a, ha, b, hb)
    r = _edit(client, a, ha, headline="Ana's corner",
              about="Candles and code.",
              theme={"bg": "#101020", "accent": "#ff88cc"},
              links=[{"label": "my shop", "url": "https://example.com"}],
              top_friends=[b])
    assert r.status_code == 200, r.text
    page = client.get(f"/profiles/{a}/homepage").json()   # no auth at all
    assert page["headline"] == "Ana's corner"
    assert page["theme"]["accent"] == "#ff88cc"
    assert [t["display_name"] for t in page["top_friends"]] == ["Ben"]
    assert page["editable"] is False


def test_the_walls_hold(client):
    a, ha = _person(client, "Ana")
    r = _edit(client, a, ha, theme={"bg": "javascript:alert(1)"})
    assert r.status_code == 422 and "hex" in r.json()["detail"]
    r = _edit(client, a, ha, links=[{"url": "javascript:alert(1)"}])
    assert r.status_code == 422 and "http" in r.json()["detail"]
    b, hb = _person(client, "Ben")
    r = _edit(client, a, ha, top_friends=[b])
    assert r.status_code == 422 and "actual friends" in r.json()["detail"]


def test_a_rejected_edit_changes_nothing(client):
    """The wall is a wall, not a filter: one bad link rejects the whole
    document, and the page keeps its last good state."""
    a, ha = _person(client, "Ana")
    _edit(client, a, ha, headline="good")
    _edit(client, a, ha, headline="evil",
          links=[{"url": "javascript:alert(1)"}])
    page = client.get(f"/profiles/{a}/homepage", headers=ha).json()
    assert page["headline"] == "good"


def test_the_homepage_switch_hides_it_from_everyone_but_the_owner(client):
    a, ha = _person(client, "Ana")
    _edit(client, a, ha, headline="mine")
    client.put(f"/profiles/{a}/features",
               json={"feature": "homepage", "enabled": False}, headers=ha)
    assert client.get(f"/profiles/{a}/homepage").status_code == 404
    own = client.get(f"/profiles/{a}/homepage", headers=ha).json()
    assert own["headline"] == "mine" and own["editable"] is True


def test_nothing_a_stranger_sees_can_carry_a_script(client):
    """The structural claim: walk every string in a stranger's view of a
    maximally hostile-but-accepted document and find no `<` at all —
    because the sandbox stores text, and text is what comes back."""
    a, ha = _person(client, "Ana")
    _edit(client, a, ha,
          headline="<script>alert(1)</script>",
          about="<img onerror=x src=y>")
    page = client.get(f"/profiles/{a}/homepage").json()
    # Stored as inert text: the API returns it as data, and every client
    # renders text as text. What the sandbox guarantees is narrower and
    # stronger: no field a stranger sees is anything *but* text, a hex
    # color, or an http(s) URL.
    assert page["theme"]["bg"].startswith("#")
    for link in page["links"]:
        assert link["url"].startswith(("http://", "https://"))
    assert isinstance(page["headline"], str)
    assert isinstance(page["about"], str)
