"""Friends lists between profiles, and the founder who comes as standard.

The tests that matter here are the ones that stop the default from becoming an
imposition. A friend installed on every new profile is a fine welcome; a friend
who cannot be removed, or who quietly reappears after being removed, is
furniture wearing a person's face. Both of those are pinned below.

The other half is keeping this apart from `relationships`, which is a different
table answering a different question. A bug that read one as the other would
look exactly like working code.
"""

import pytest

from qrme import db, friends, seed
from tests.test_capabilities import auth_header, make_profile


def _seeded(client):
    """Seed the collection, and hand back the founder's profile id."""
    out = seed.seed()
    return out["founder"]


# -- the founder comes standard ---------------------------------------------

def test_a_new_profile_gets_the_founder_at_position_one(client):
    founder = _seeded(client)
    profile = make_profile(client, display_name="Newcomer")

    listed = client.get(f"/profiles/{profile['id']}/friends").json()
    assert listed["count"] == 1
    first = listed["friends"][0]
    assert first["position"] == 1
    assert first["profile_id"] == founder
    assert first["founder"] is True
    assert first["handle"] == friends.FOUNDER_HANDLE


def test_the_founder_stays_first_however_many_friends_arrive(client):
    """Position is computed from `origin`, not stored. A stored column would be
    the thing that is wrong on the day the founder turns up third."""
    founder = _seeded(client)
    profile = make_profile(client, display_name="Popular")
    others = [make_profile(client, display_name=f"Friend {i}")
              for i in range(3)]
    for other in others:
        r = client.post(f"/profiles/{profile['id']}/friends",
                        json={"friend_id": other["id"]},
                        headers=auth_header(profile))
        assert r.status_code == 200, r.text

    listed = client.get(f"/profiles/{profile['id']}/friends").json()
    assert listed["count"] == 4
    assert listed["friends"][0]["profile_id"] == founder
    assert [f["founder"] for f in listed["friends"]] == [True, False, False,
                                                         False]


def test_the_founder_is_first_even_when_he_arrives_last(client):
    """The real ordering test. Everywhere else the founder is installed at
    creation, so he is also the *oldest* row and plain `created_at` ordering
    would look correct while testing nothing. Here he is seeded onto a
    deployment that already had profiles and friends, so his row is the
    newest — and he must still stand first."""
    a = make_profile(client, display_name="Early Adopter")
    b = make_profile(client, display_name="Their Friend")
    client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                headers=auth_header(a))
    assert client.get(f"/profiles/{a['id']}/friends").json()["count"] == 1

    founder = _seeded(client)          # the founder appears only now

    listed = client.get(f"/profiles/{a['id']}/friends").json()
    assert listed["count"] == 2
    assert listed["friends"][0]["profile_id"] == founder
    assert listed["friends"][0]["position"] == 1
    assert listed["friends"][1]["profile_id"] == b["id"]


def test_the_backfill_does_not_undo_a_removal(client):
    """A repair that reverses somebody's decision is not a repair."""
    founder = _seeded(client)
    a = make_profile(client, display_name="Decided")
    client.delete(f"/profiles/{a['id']}/friends/{founder}",
                  headers=auth_header(a))

    assert friends.backfill_founder() == []
    assert client.get(f"/profiles/{a['id']}/friends").json()["count"] == 0


def test_the_founders_own_profile_does_not_befriend_itself(client):
    founder = _seeded(client)
    listed = client.get(f"/profiles/{founder}/friends").json()
    assert listed["count"] == 0


def test_install_is_silent_when_there_is_no_founder(client):
    """An unseeded deployment has none. Creating a profile must still work —
    a cosmetic default is not a reason for profile creation to fail."""
    assert friends.founder_id() is None
    profile = make_profile(client, display_name="Early")
    assert client.get(f"/profiles/{profile['id']}/friends").json()["count"] == 0


# -- and can be shown the door ----------------------------------------------

def test_the_founder_can_be_removed(client):
    founder = _seeded(client)
    profile = make_profile(client, display_name="Independent")

    r = client.delete(f"/profiles/{profile['id']}/friends/{founder}",
                      headers=auth_header(profile))
    assert r.status_code == 200, r.text
    assert r.json() == {"profile_id": profile["id"], "friend_id": founder,
                        "removed": True, "was_founder": True}
    assert client.get(f"/profiles/{profile['id']}/friends").json()["count"] == 0


def test_removing_the_founder_sticks(client):
    """The install runs on profile creation. If removal deleted the row, the
    next install would put him straight back — which is the difference between
    a default and something you cannot get rid of."""
    founder = _seeded(client)
    profile = make_profile(client, display_name="Firm")
    client.delete(f"/profiles/{profile['id']}/friends/{founder}",
                  headers=auth_header(profile))

    again = friends.install_founder(profile["id"])
    assert again["installed"] is False
    assert again["reason"] == "already removed"
    assert client.get(f"/profiles/{profile['id']}/friends").json()["count"] == 0


def test_a_removed_founder_can_be_invited_back(client):
    founder = _seeded(client)
    profile = make_profile(client, display_name="Forgiving")
    client.delete(f"/profiles/{profile['id']}/friends/{founder}",
                  headers=auth_header(profile))

    r = client.post(f"/profiles/{profile['id']}/friends",
                    json={"friend_id": founder}, headers=auth_header(profile))
    assert r.status_code == 200, r.text
    assert r.json()["revived"] is True
    back = client.get(f"/profiles/{profile['id']}/friends").json()
    assert back["friends"][0]["founder"] is True


# -- the ordinary verbs ------------------------------------------------------

def test_a_list_is_directed_not_mutual(client):
    """Befriending writes one row. A mutual edge would mean somebody else's
    action edits your list."""
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")

    client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                headers=auth_header(a))

    a_list = client.get(f"/profiles/{a['id']}/friends").json()["friends"]
    b_list = client.get(f"/profiles/{b['id']}/friends").json()["friends"]
    assert b["id"] in [f["profile_id"] for f in a_list]
    assert a["id"] not in [f["profile_id"] for f in b_list]
    assert [f for f in a_list if f["profile_id"] == b["id"]][0]["mutual"] is False


def test_mutual_is_reported_once_both_rows_exist(client):
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                headers=auth_header(a))
    client.post(f"/profiles/{b['id']}/friends", json={"friend_id": a["id"]},
                headers=auth_header(b))

    a_list = client.get(f"/profiles/{a['id']}/friends").json()["friends"]
    assert [f for f in a_list if f["profile_id"] == b["id"]][0]["mutual"] is True


def test_befriending_twice_is_idempotent(client):
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    for _ in range(2):
        client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                    headers=auth_header(a))
    listed = client.get(f"/profiles/{a['id']}/friends").json()
    assert [f["profile_id"] for f in listed["friends"]].count(b["id"]) == 1


def test_a_profile_cannot_befriend_itself(client):
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    r = client.post(f"/profiles/{a['id']}/friends", json={"friend_id": a["id"]},
                    headers=auth_header(a))
    assert r.status_code == 422
    assert "own friend" in r.json()["detail"]


def test_only_the_owner_edits_the_list(client):
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    # b's owner token, aimed at a's list.
    r = client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                    headers=auth_header(b))
    assert r.status_code in (401, 403)


# -- the friends list is not the relationships table -------------------------

def test_friendships_and_relationships_are_separate_tables(client):
    """`relationships` records how a profile treats an *interactor*. Reading
    one as the other would look like working code."""
    founder = _seeded(client)
    profile = make_profile(client, display_name="Distinct")
    conn = db.connect()
    assert conn.execute(
        "SELECT COUNT(*) AS n FROM relationships WHERE profile_id=?",
        (profile["id"],)).fetchone()["n"] == 0
    assert conn.execute(
        "SELECT COUNT(*) AS n FROM friendships WHERE profile_id=?",
        (profile["id"],)).fetchone()["n"] == 1


# -- the founder profile itself ---------------------------------------------

def test_the_founder_is_a_real_person_with_a_marked_portrait(client):
    """He is `self` kind, not `fictional`, so the likeness record says a real
    person is depicted and the grant is revocable. And the portrait carries the
    AI mark in its own pixels, because it is an AI rendering of a real face —
    which is the exact case the mark exists for."""
    founder = _seeded(client)
    avatar = client.get(f"/profiles/{founder}/avatar").json()
    assert avatar["asset"] == f"/portraits/{friends.FOUNDER_HANDLE}.webp"
    assert avatar["asset_marked"] is True
    assert avatar["likeness"]["real_person"] is True
    assert avatar["likeness"]["revocable"] is True


def test_the_founder_is_not_in_the_fictional_starter_collection(client):
    """`seed.py`'s docstring promises every starter is fictional, and
    `avatars.BRIEFS` promises every brief describes an invented person. A real
    person in either list would quietly make a documented claim false."""
    from qrme import avatars
    handles = [h for h, *_ in seed.STARTERS + seed.RATED]
    assert friends.FOUNDER_HANDLE not in handles
    assert friends.FOUNDER_HANDLE not in avatars.BRIEFS


def test_the_founder_is_grounded_like_everybody_else(client):
    """0.3.1 established that a profile with no source material answers from
    tone alone, and fixed it for all 34 starters. The profile every new account
    meets first must not reintroduce it."""
    founder = _seeded(client)
    rows = db.connect().execute(
        "SELECT title FROM source_items WHERE profile_id=?",
        (founder,)).fetchall()
    assert len(rows) == len(seed.FOUNDER_SOURCES)
    # Written material, not a Field Pack — the packs are paired one-per-industry
    # with the Starter Collection and a founder pack would break that pairing.
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM source_items WHERE profile_id=? AND"
        " pack_id IS NOT NULL", (founder,)).fetchone()["n"] == 0


def test_the_founder_handle_agrees_with_the_seed(client):
    """Two modules name the same person. If they drift, every new profile gets
    an empty list and nothing else complains."""
    assert friends.FOUNDER_HANDLE == seed.FOUNDER_HANDLE
