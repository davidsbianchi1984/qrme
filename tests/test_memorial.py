"""Succession and the public memorial: ownership passes to a named successor
on a verified death signal (or the profile sunsets to memorial when none is
named), and a departed profile has a public memorial view."""

from tests.test_capabilities import make_interactor, make_profile


def test_succession_transfers_control_to_the_successor(client):
    p = make_profile(client, successor_owner="daughter-1")
    old_token_header = dict(client.headers)

    r = client.post(f"/profiles/{p['id']}/succeed",
                    json={"verification_ref": "death-cert-042"}).json()
    assert r["succeeded"] is True and r["memorial"] is False
    assert r["owner_id"] == "daughter-1"
    assert r["owner_token"]

    # The old owner token is dead; the successor's works.
    client.headers.update(old_token_header)
    assert client.get(f"/profiles/{p['id']}/export").status_code == 401
    ok = {"authorization": f"Bearer {r['owner_token']}"}
    assert client.get(f"/profiles/{p['id']}/export", headers=ok).status_code == 200
    # Ownership is reflected on the card, and the profile stays active.
    card = client.get(f"/profiles/{p['id']}", headers={}).json()
    assert card["owner_id"] == "daughter-1" and card["status"] == "active"


def test_succession_without_successor_becomes_memorial(client):
    p = make_profile(client)                   # no successor_owner named
    user = make_interactor(client)
    client.put(f"/profiles/{p['id']}/relationships/{user}",
               json={"relationship_type": "grandchild", "nickname": "kiddo"})

    r = client.post(f"/profiles/{p['id']}/succeed",
                    json={"verification_ref": "death-cert-043"}).json()
    assert r["succeeded"] is False and r["memorial"] is True
    assert r["farewells"] == 1                 # the farewell reached the grandchild
    assert client.get(f"/profiles/{p['id']}", headers={}).json()["status"] == "departed"

    # Succeeding again is a conflict — it is already a memorial.
    again = client.post(f"/profiles/{p['id']}/succeed",
                        json={"verification_ref": "x"})
    assert again.status_code == 409


def test_public_memorial_view(client):
    p = make_profile(client, purpose="legacy_memorial")
    client.put(f"/profiles/{p['id']}/handle", json={"handle": "rosa"})
    client.post(f"/profiles/{p['id']}/beacons",
                json={"label": "Rosa's garden bench", "location": "the park"})
    user = make_interactor(client)
    client.put(f"/profiles/{p['id']}/relationships/{user}",
               json={"relationship_type": "friend"})

    # Not a memorial while active.
    assert client.get(f"/profiles/{p['id']}/memorial",
                      headers={}).status_code == 409

    client.post(f"/profiles/{p['id']}/sunset")
    m = client.get(f"/profiles/{p['id']}/memorial", headers={}).json()
    assert m["display_name"] == "Dana" and m["handle"] == "@rosa"
    assert m["memorial_anchors"][0]["label"] == "Rosa's garden bench"
    assert m["relationships_touched"] == 1
    assert "memory remains" in m["note"]
    # The memorial never leaks persona internals.
    assert "persona" not in m
