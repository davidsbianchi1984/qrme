"""Everyone here, by default — the browse pool and its honest head count.

The field asked for it in head-count terms: every profile made on the
deployment goes on the browse page, the real people and the synthetic
ones side by side, so a person can see who is actually around. Listing
is the default; privacy is the door out — an owner who sets a profile
private leaves the pool and the name search both, until they come back.

    asked     who is here
    mattered  a deployment whose people cannot see each other is a
              hallway of closed doors
"""

from __future__ import annotations


def a_profile(client, owner: str, name: str, kind: str = "self"):
    body = {
        "owner_id": owner, "kind": kind, "display_name": name,
        "persona": "A retired teacher who likes gardening and dry humor.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"}
    if kind == "other_person":
        body["consent_basis"] = "self"
        body["consent_attestor"] = name
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"], r.json()["owner_token"]


def head(token):
    return {"authorization": f"Bearer {token}"}


def _pool(client):
    r = client.get("/people/browse")
    assert r.status_code == 200, r.text
    return r.json()


def test_a_new_profile_is_listed_without_being_asked(client):
    pid, _ = a_profile(client, "owner-p1", "Paula")
    pool = _pool(client)
    assert pid in [p["profile_id"] for p in pool["found"]]


def test_the_head_count_counts_real_and_synthetic_together(client):
    real, _ = a_profile(client, "owner-p2", "Rita", kind="self")
    synth, _ = a_profile(client, "owner-p2", "Sage", kind="fictional")
    pool = _pool(client)
    ids = [p["profile_id"] for p in pool["found"]]
    assert real in ids and synth in ids
    assert pool["head_count"] == len(ids) or pool["head_count"] >= len(ids)
    assert pool["kind_counts"].get("self", 0) >= 1
    assert pool["kind_counts"].get("fictional", 0) >= 1


def test_private_leaves_the_pool_and_the_search_and_can_come_back(client):
    pid, tok = a_profile(client, "owner-p3", "Quinn Uniquename")
    r = client.put(f"/profiles/{pid}/listing", json={"listed": False},
                   headers=head(tok))
    assert r.status_code == 200 and r.json()["listed"] is False
    assert pid not in [p["profile_id"] for p in _pool(client)["found"]]
    found = client.get("/people", params={"q": "Quinn Uniquename"}).json()
    assert pid not in [p["profile_id"] for p in found["found"]]
    # And back in — reversible both ways, like anonymity.
    client.put(f"/profiles/{pid}/listing", json={"listed": True},
               headers=head(tok))
    assert pid in [p["profile_id"] for p in _pool(client)["found"]]


def test_going_private_moves_the_head_count(client):
    pid, tok = a_profile(client, "owner-p4", "Tally")
    before = _pool(client)["head_count"]
    client.put(f"/profiles/{pid}/listing", json={"listed": False},
               headers=head(tok))
    assert _pool(client)["head_count"] == before - 1


def test_only_the_owner_throws_the_switch(client):
    pid, _ = a_profile(client, "owner-p5", "Uma")
    assert client.put(f"/profiles/{pid}/listing",
                      json={"listed": False}).status_code == 401


def test_an_anonymous_profile_never_browses(client):
    pid, tok = a_profile(client, "owner-p6", "Vera")
    client.put(f"/profiles/{pid}/anonymity", json={"anonymous": True},
               headers=head(tok))
    assert pid not in [p["profile_id"] for p in _pool(client)["found"]]
