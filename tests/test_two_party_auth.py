"""Who the two-party surfaces think you are.

An exchange, a lent skill and a watch party all identify the acting party by an
id in the request body. An id in a body is a *claim*, and until this was
checked it was accepted as a fact — so an anonymous caller could forge both
signatures on somebody else's agreement, open its channel, and accept delivery
of an executable on their behalf. Every consent property those three modules
describe rested on a check that did not exist.

Two things are asserted for each surface, and the second is the one that
matters: **a valid token belonging to the wrong person is refused.** A test
that only tries an anonymous caller passes against a system that accepts any
logged-in user as anybody.
"""

import pytest

from qrme import db, exchange, sharing
from tests.test_capabilities import auth_header, make_profile


def _two(client):
    """Two real accounts, each with its own owner token."""
    a = make_profile(client, owner_id="owner-a", display_name="Ada")
    b = make_profile(client, owner_id="owner-b", display_name="Bo")
    return a, b


def _tok(profile):
    return auth_header(profile)


def _owner(profile):
    """The id a party is known by on these surfaces.

    An owner token's subject is the **profile id**, not the `owner_id` string
    the profile was created with — so that is what `require_self` compares
    against and what the body must carry. Getting this wrong is how the first
    draft of these tests failed against correct code.
    """
    return profile["id"]


def _anon(client):
    """A caller with no token at all.

    `make_profile` leaves the owner's token on the client so later owner-only
    calls authorize, which means "send no headers" is not anonymous — it is
    "whoever was created last". Without this the anonymous cases below assert
    403 where they mean 401, and would pass against a system with no
    authentication at the door.
    """
    return {"authorization": ""}


# -- an exchange --------------------------------------------------------------

def test_a_stranger_cannot_propose_an_exchange_between_two_people(client):
    """An agreement invented by a third party, naming two people who never
    spoke, is a phishing primitive with the platform's name on it."""
    a, b = _two(client)
    r = client.post("/exchanges", json={
        "host_id": _owner(a), "guest_id": _owner(b),
        "work": "Build it", "industry": "software"}, headers=_anon(client))
    assert r.status_code == 401


def test_a_logged_in_bystander_cannot_propose_for_two_others(client):
    """The check that a valid-token test would miss."""
    a, b = _two(client)
    c3 = make_profile(client, owner_id="owner-c", display_name="Cy")
    r = client.post("/exchanges", json={
        "host_id": _owner(a), "guest_id": _owner(b),
        "work": "Build it", "industry": "software"}, headers=_tok(c3))
    assert r.status_code == 403


def test_you_cannot_sign_as_the_other_party(client):
    """The one forgery that would make the whole module theatre."""
    a, b = _two(client)
    x = client.post("/exchanges", json={
        "host_id": _owner(a), "guest_id": _owner(b),
        "work": "Build it", "industry": "software"},
        headers=_tok(a)).json()
    client.post(f"/exchanges/{x['id']}/items",
                json={"direction": "host_to_guest", "name": "payload.exe",
                      "kind": "build", "bytes": 9}, headers=_tok(a))

    # Ada signs for herself: fine.
    assert client.post(f"/exchanges/{x['id']}/sign",
                       json={"actor_id": _owner(a)},
                       headers=_tok(a)).status_code == 200
    # Ada signs for Bo: refused, so the channel stays shut.
    r = client.post(f"/exchanges/{x['id']}/sign",
                    json={"actor_id": _owner(b)}, headers=_tok(a))
    assert r.status_code == 403
    assert client.get(f"/exchanges/{x['id']}/channel",
                      headers=_tok(a)).json()["open"] is False


def test_you_cannot_accept_delivery_on_somebody_elses_behalf(client):
    """How a `build` lands on a machine whose owner never agreed to it."""
    a, b = _two(client)
    x = client.post("/exchanges", json={
        "host_id": _owner(a), "guest_id": _owner(b),
        "work": "Build it", "industry": "software"},
        headers=_tok(a)).json()
    client.post(f"/exchanges/{x['id']}/items",
                json={"direction": "host_to_guest", "name": "payload.exe",
                      "kind": "build", "bytes": 9}, headers=_tok(a))
    client.post(f"/exchanges/{x['id']}/sign", json={"actor_id": _owner(a)},
                headers=_tok(a))
    client.post(f"/exchanges/{x['id']}/sign", json={"actor_id": _owner(b)},
                headers=_tok(b))
    item = client.get(f"/exchanges/{x['id']}", headers=_tok(a)).json()["items"][0]

    r = client.post(f"/exchanges/{x['id']}/items/{item['id']}/accept",
                    json={"actor_id": _owner(b)}, headers=_tok(a))
    assert r.status_code == 403


def test_an_exchange_is_readable_only_by_its_two_parties(client):
    """A manifest names somebody's files, their sizes, and what the work is
    worth. It is the private part."""
    a, b = _two(client)
    c3 = make_profile(client, owner_id="owner-c", display_name="Cy")
    x = client.post("/exchanges", json={
        "host_id": _owner(a), "guest_id": _owner(b),
        "work": "Build it", "industry": "software"},
        headers=_tok(a)).json()
    assert client.get(f"/exchanges/{x['id']}", headers=_tok(a)).status_code == 200
    assert client.get(f"/exchanges/{x['id']}", headers=_tok(b)).status_code == 200
    assert client.get(f"/exchanges/{x['id']}", headers=_tok(c3)).status_code == 403
    assert client.get(f"/exchanges/{x['id']}",
                      headers=_anon(client)).status_code == 401


def test_the_vocabulary_stays_open(client):
    """It describes the feature, not anybody's agreement — a client needs it
    before there is anything to be a party to."""
    assert client.get("/exchanges/vocabulary").status_code == 200


# -- a lent skill -------------------------------------------------------------

def test_you_cannot_offer_somebody_elses_skill(client):
    """Not a loan — a forgery with their name on it."""
    a, b = _two(client)
    r = client.post("/skill-grants", json={
        "lender_id": _owner(a), "borrower_id": _owner(b), "surface": "room",
        "surface_id": "rm_1", "skill_kind": "pack", "skill_ref": "pk_x",
        "title": "Her pack"}, headers=_tok(b))
    assert r.status_code == 403


def test_you_cannot_accept_a_loan_for_the_borrower(client):
    """An acceptance somebody else can send is not a second consent, it is the
    first one typed twice."""
    a, b = _two(client)
    g = client.post("/skill-grants", json={
        "lender_id": _owner(a), "borrower_id": _owner(b), "surface": "room",
        "surface_id": "rm_1", "skill_kind": "pack", "skill_ref": "pk_x",
        "title": "Her pack"}, headers=_tok(a)).json()
    r = client.post(f"/skill-grants/{g['id']}/accept",
                    json={"actor_id": _owner(b)}, headers=_tok(a))
    assert r.status_code == 403
    assert sharing.get(g["id"])["active"] is False


def test_you_cannot_use_a_grant_that_is_not_yours(client):
    a, b = _two(client)
    c3 = make_profile(client, owner_id="owner-c", display_name="Cy")
    g = client.post("/skill-grants", json={
        "lender_id": _owner(a), "borrower_id": _owner(b), "surface": "room",
        "surface_id": "rm_1", "skill_kind": "pack", "skill_ref": "pk_x",
        "title": "Her pack"}, headers=_tok(a)).json()
    client.post(f"/skill-grants/{g['id']}/accept",
                json={"actor_id": _owner(b)}, headers=_tok(b))
    r = client.post(f"/skill-grants/{g['id']}/use",
                    json={"borrower_id": _owner(b), "what": "anything"},
                    headers=_tok(c3))
    assert r.status_code == 403


def test_a_surface_listing_shows_only_your_own_grants(client):
    """It used to list every grant in any surface to anybody who guessed the
    id — who is lending what to whom."""
    a, b = _two(client)
    c3 = make_profile(client, owner_id="owner-c", display_name="Cy")
    client.post("/skill-grants", json={
        "lender_id": _owner(a), "borrower_id": _owner(b), "surface": "room",
        "surface_id": "rm_9", "skill_kind": "pack", "skill_ref": "pk_x",
        "title": "Her pack"}, headers=_tok(a))
    seen = client.get("/surfaces/room/rm_9/skill-grants",
                      headers=_tok(c3)).json()["grants"]
    assert seen == []
    assert len(client.get("/surfaces/room/rm_9/skill-grants",
                          headers=_tok(a)).json()["grants"]) == 1


# -- a watch party ------------------------------------------------------------

def _party(client, host):
    post = client.post(f"/profiles/{host['id']}/wall",
                       json={"body": "Look.",
                             "video_url": "https://youtu.be/dQw4w9WgXcQ"},
                       headers=_tok(host)).json()
    return client.post("/watch-parties",
                       json={"post_id": post["id"], "host_id": _owner(host)},
                       headers=_tok(host)).json()


def test_only_the_host_moves_the_position_and_it_is_checked(client):
    """The module refused a non-host id; nothing checked that the caller *was*
    the host, so anyone could pass the host's id and seize the scrubber."""
    a, b = _two(client)
    p = _party(client, a)
    r = client.post(f"/watch-parties/{p['id']}/seek",
                    json={"host_id": _owner(a), "position_s": 90},
                    headers=_tok(b))
    assert r.status_code == 403


def test_you_cannot_speak_as_another_member(client):
    """Putting words in a third party's mouth is the one thing a chat endpoint
    must refuse."""
    a, b = _two(client)
    p = _party(client, a)
    client.post(f"/watch-parties/{p['id']}/members",
                json={"member_id": _owner(b)}, headers=_tok(b))
    r = client.post(f"/watch-parties/{p['id']}/chat",
                    json={"member_id": _owner(b), "body": "I agree with Ada"},
                    headers=_tok(a))
    assert r.status_code == 403


def test_party_chat_is_not_readable_by_outsiders(client):
    """A conversation between the people watching, not a public timeline
    attached to a guessable id."""
    a, b = _two(client)
    c3 = make_profile(client, owner_id="owner-c", display_name="Cy")
    p = _party(client, a)
    assert client.get(f"/watch-parties/{p['id']}/chat",
                      headers=_tok(a)).status_code == 200
    assert client.get(f"/watch-parties/{p['id']}/chat",
                      headers=_tok(c3)).status_code == 403
    assert client.get(f"/watch-parties/{p['id']}/chat",
                      headers=_anon(client)).status_code == 401


def test_only_a_profiles_owner_can_bring_it_into_a_room(client):
    """Bringing a synthetic profile into a room speaks in its voice."""
    a, b = _two(client)
    p = _party(client, a)
    r = client.post(f"/watch-parties/{p['id']}/members",
                    json={"member_id": b["id"], "kind": "profile"},
                    headers=_tok(a))
    assert r.status_code == 403
    assert client.post(f"/watch-parties/{p['id']}/members",
                       json={"member_id": b["id"], "kind": "profile"},
                       headers=_tok(b)).status_code == 201


# -- the sweep ----------------------------------------------------------------

def test_no_two_party_route_accepts_an_anonymous_caller(client):
    """The regression net. Every mutating route on these three surfaces must
    refuse a caller it cannot identify — a new one added without a check is
    the way this comes back."""
    from qrme.api import create_app
    from fastapi.routing import APIRoute
    app = create_app()

    def walk(routes):
        for r in routes:
            if isinstance(r, APIRoute):
                yield r
            inner = getattr(r, "original_router", None)
            if inner is not None:
                yield from walk(inner.routes)

    # The vocabularies, and the party browse list: deliberately public reads.
    # The browse card carries counts and a facade, never member names or a
    # line of chat — everything a member token protects still requires one.
    OPEN = {"/exchanges/vocabulary", "/skill-grants/vocabulary",
            "/watch-parties/public"}
    unguarded = []
    for route in walk(app.routes):
        if not any(route.path.startswith(p) for p in
                   ("/exchanges", "/skill-grants", "/watch-parties",
                    "/parties/", "/people/", "/surfaces/")):
            continue
        if route.path in OPEN:
            continue
        src = route.endpoint.__code__.co_varnames
        if "request" not in src:
            unguarded.append(f"{sorted(route.methods)} {route.path}")
    assert not unguarded, ("routes with no way to identify the caller:\n  "
                           + "\n  ".join(unguarded))
