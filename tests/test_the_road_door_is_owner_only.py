"""Setting a profile's video road spends its owner's money — so its owner
is the only one who may set it, or read what it costs.

`POST /video/road/{id}` puts a profile on the video road, sets the daily
seconds ceiling that caps its spend, and points it at a render provider.
It shipped taking neither a token nor a Request: it authorized nobody.
A profile id is not a secret — it rides on printed stickers and in
beacons, the same argument the room doors were hardened on — so anyone
holding one could put somebody else's profile on the video road, raise
its ceiling to the hour, or repoint its provider, and start spending
that owner's budget.

The GET is guarded for the mirror reason: it hands back the ceiling, the
seconds already spent, and the service name — a profile's money posture,
which is its owner's to read and no one else's.
"""

from tests.test_capabilities import auth_header, make_profile


def test_a_stranger_cannot_put_a_profile_on_the_video_road(client):
    mine = make_profile(client)
    other = make_profile(client, display_name="Someone Else")
    # `other` is now the client default. A call for `mine` carrying no
    # owner token of mine must not set my road.
    r = client.post(f"/video/road/{mine['id']}",
                    json={"road": "video", "daily_seconds": 3600},
                    headers={})
    assert r.status_code in (401, 403), r.text
    # And with a DIFFERENT owner's token — a real credential, wrong profile.
    r = client.post(f"/video/road/{mine['id']}",
                    json={"road": "video", "daily_seconds": 3600},
                    headers=auth_header(other))
    assert r.status_code in (401, 403), r.text


def test_a_stranger_cannot_read_what_a_profile_spends(client):
    mine = make_profile(client)
    other = make_profile(client, display_name="Someone Else")
    r = client.get(f"/video/road/{mine['id']}", headers=auth_header(other))
    assert r.status_code in (401, 403), r.text


def test_the_owner_sets_and_reads_their_own_road(client):
    mine = make_profile(client)
    r = client.post(f"/video/road/{mine['id']}",
                    json={"road": "video", "daily_seconds": 120},
                    headers=auth_header(mine))
    assert r.status_code == 200, r.text
    assert r.json()["road"] == "video"
    assert r.json()["daily_seconds"] == 120

    got = client.get(f"/video/road/{mine['id']}", headers=auth_header(mine))
    assert got.status_code == 200, got.text
    assert got.json()["road"] == "video"
