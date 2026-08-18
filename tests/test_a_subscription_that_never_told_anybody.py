"""Somebody subscribing to the agent, rather than the agent reaching them.

The estate's connections all run one way. A profile posts, a desk goes live,
an escalation fires — the thing acts and the people hear about it because it
reached them. `audience.subscribe` was supposed to be the other direction, and
it half was: there is a `subscriptions` table, two tiers, a charge per period,
`subscribers()` and `subscriptions_of()`.

    asked     can somebody subscribe to this
    mattered  does subscribing ever reach them

It did not. `subscribers()` was read in exactly two places — a route that
lists them, and the `counts` payload — so what a person bought was a row, a
charge, and a number on somebody else's page. `subscribe`'s own docstring says
subscribing means *"tell me when there is more from them"*, and nothing ever
told anybody.

## Where the telling goes

`qrme/inbox.py`, whose docstring already made this argument for every other
capability: *a capability nobody is told about is reachable the way a doorless
route is — technically*. It is the one place this platform keeps that kind of
promise, so a second delivery surface beside it would be the drift the module
was written to prevent.

`published` is the one exception to the inbox's *somebody did this to you*
framing, and it is deliberate: it is the thing you asked to hear.

## What these hold

**A reference, never the words.** The inbox's own first rule, and it earns a
second reason here: the thing published has its own gates — a rated desk runs
the deployment's verified-adult check, a blocked post is visible only to its
author — and a notice carrying the content would be a path around every one of
them.

**A blocked post tells nobody.** An inbox row about something the reader can
never see is the filter advertising its own catch, which is why
`audience.comment` sends no event for a blocked comment either.

**Cancelling stops the telling.** Otherwise cancelling is a pause on the
billing with the delivery left running.
"""

from __future__ import annotations

import inspect

from qrme import audience, db, inbox, wall


def a_profile(client, **kw):
    body = {"owner_id": kw.get("owner", "owner-x"), "kind": "self",
            "display_name": kw.get("name", "Dana"),
            "persona": "A retired teacher who likes gardening and dry humor.",
            "verification": {"birthdate": "1984-06-01"}, "plan": "pro"}
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def kinds_in(profile_id):
    return [e["kind"] for e in inbox.events(profile_id)["events"]]


# --- the half that was missing ----------------------------------------------

def test_a_post_reaches_the_people_who_subscribed(client):
    author = a_profile(client, owner="o1", name="Dana")
    reader = a_profile(client, owner="o2", name="Sam")
    audience.subscribe("profile", author, reader, tier="follow")

    wall.publish(author, "the tomatoes came in")

    assert "published" in kinds_in(reader), (
        "a subscription is still a row, a charge and a number on a page")


def test_the_notice_carries_a_reference_and_not_the_words(client):
    author = a_profile(client, owner="o1", name="Dana")
    reader = a_profile(client, owner="o2", name="Sam")
    audience.subscribe("profile", author, reader, tier="follow")

    post = wall.publish(author, "the tomatoes came in")

    row = next(e for e in inbox.events(reader)["events"]
               if e["kind"] == "published")
    assert post["id"] in repr(row)
    assert "tomatoes" not in repr(row), (
        "the post's words are in the inbox row, so the notice is a second "
        "copy of content that has its own gates")


def test_nobody_is_told_about_a_blocked_post(client, monkeypatch):
    author = a_profile(client, owner="o1", name="Dana")
    reader = a_profile(client, owner="o2", name="Sam")
    audience.subscribe("profile", author, reader, tier="follow")

    class Blocked:
        approved = False
        reason = "no"

    monkeypatch.setattr(wall.moderation, "review", lambda *a, **k: Blocked())
    out = wall.publish(author, "something the filter stops")

    assert out["status"] == "blocked"
    assert "published" not in kinds_in(reader), (
        "the inbox advertised a post the reader can never see")


def test_cancelling_stops_the_telling(client):
    author = a_profile(client, owner="o1", name="Dana")
    reader = a_profile(client, owner="o2", name="Sam")
    audience.subscribe("profile", author, reader, tier="follow")
    audience.cancel("profile", author, reader)

    wall.publish(author, "the tomatoes came in")

    assert "published" not in kinds_in(reader)


def test_a_profile_is_not_told_about_its_own_post(client):
    author = a_profile(client, owner="o1", name="Dana")
    audience.subscribe("profile", author, author, tier="follow")

    wall.publish(author, "the tomatoes came in")

    assert "published" not in kinds_in(author), (
        "telling somebody what they just did is noise wearing the coat of news")


def test_every_active_subscriber_is_told_and_only_them(client):
    author = a_profile(client, owner="o1", name="Dana")
    one = a_profile(client, owner="o2", name="Sam")
    two = a_profile(client, owner="o3", name="Ada")
    bystander = a_profile(client, owner="o4", name="Kit")
    audience.subscribe("profile", author, one, tier="follow")
    audience.subscribe("profile", author, two, tier="follow")

    out = audience.published("profile", author, "pst-made-up")

    assert out["told"] == 2
    assert "published" in kinds_in(one) and "published" in kinds_in(two)
    assert "published" not in kinds_in(bystander)


# --- the door is called, not merely written ---------------------------------

def test_the_delivery_door_is_reached_from_the_thing_that_publishes():
    """A delivery function nothing calls is the defect one layer along.

    Read from the source as well as exercised above, because the behavioural
    test would still pass if some future round routed around `published` and
    noted the inbox itself — which is how a second delivery surface starts.
    """
    body = inspect.getsource(wall.publish)
    assert "audience.published(" in body
    assert "inbox.note(" not in body, (
        "wall.publish notes the inbox directly, so there are two ways a "
        "subscriber gets told and only one of them is `published`")


def test_the_inbox_knows_the_word():
    """Clients render an inbox row from their own vocabulary, so a kind the
    inbox does not name is a row nothing can draw."""
    assert "published" in inbox.KINDS


def test_only_a_subject_can_be_published_about():
    """A message and a listing cannot be subscribed to — neither produces
    more — so neither can publish."""
    try:
        audience.published("message", "msg-1", "ref")
    except audience.AudienceError:
        return
    raise AssertionError("published accepted a kind nobody can subscribe to")
