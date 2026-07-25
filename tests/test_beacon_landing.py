"""Scanning a beacon: what a stranger with a phone actually gets.

The viewer here is not a user. They pointed a camera at a sticker, they have
no token, and they may not know what QRME is. Most of these tests are about
what that person must be told — and about the two states that are easy to
get wrong because nobody scans them on purpose: a rated profile, and a
beacon that was picked up.
"""

from qrme import db


def _profile(client, **over):
    body = {"owner_id": "o1", "kind": "fictional", "display_name": "Marcus Bell",
            "persona": "A retired fee-only financial planner.",
            "verification": {"birthdate": "1980-01-01",
                             "id_document": "passport", "liveness_check": True}}
    body.update(over)
    created = client.post("/profiles", json=body).json()
    return created["id"], created["owner_token"]


def _beacon(client, pid, label="stall 3, second floor"):
    return client.post(f"/profiles/{pid}/beacons",
                       json={"label": label, "location": "cafe"}).json()


def test_the_printed_qr_points_at_the_page_not_the_json(client):
    """A camera app can only open a URL. If that URL answers JSON, the person
    who scanned the sticker gets a wall of braces."""
    pid, _ = _profile(client)
    b = _beacon(client, pid)
    assert b["scan_url"].endswith(f"/b/{b['id']}")
    qr = client.get(f"/beacons/{b['id']}/qr.svg")
    assert qr.status_code == 200
    # The JSON surface stays, for clients that want data rather than a page.
    assert b["summon_url"].endswith(f"/summon?ref={b['id']}")


def test_a_scan_reveals_the_portrait_and_the_ai_mark(client):
    pid, token = _profile(client)
    client.put(f"/profiles/{pid}/avatar", json={"asset": "/assets/m.png"},
               headers={"authorization": f"Bearer {token}"})
    b = _beacon(client, pid)

    r = client.get(f"/b/{b['id']}")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "/assets/m.png" in r.text
    assert "✦ AI · Marcus Bell" in r.text
    assert "Marcus Bell" in r.text


def test_the_disclosure_is_unavoidable(client):
    """This is the viewer the AI mark exists for: someone in the studio knows
    they are looking at a synthetic profile, someone who scanned a sticker in
    a bathroom does not."""
    pid, _ = _profile(client)
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    assert "not a real person" in r.text
    assert "AI-generated synthetic media" in r.text


def test_a_profile_with_no_portrait_shows_initials_not_a_stock_face(client):
    """A stranger's first impression of a person who does not exist should
    not be a stock photograph of someone who does."""
    pid, _ = _profile(client)
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    assert "<img" not in r.text
    assert ">MB<" in r.text


def test_the_page_is_self_contained(client):
    """It opens in a camera app's in-app browser, on cellular, cold. The
    portrait is the only fetch after the document itself."""
    pid, _ = _profile(client)
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    for offender in ("<script", "https://fonts.", "cdn.", "<link"):
        assert offender not in r.text, offender


def test_the_beacon_label_tells_them_where_they_are(client):
    pid, _ = _profile(client)
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    assert "stall 3, second floor" in r.text


def test_a_scan_is_counted(client):
    pid, _ = _profile(client)
    bid = _beacon(client, pid)["id"]
    client.get(f"/b/{bid}")
    client.get(f"/b/{bid}")
    assert client.get(f"/profiles/{pid}/beacons").json()[0]["scans"] == 2


# -- the states nobody scans on purpose ------------------------------------

def test_a_rated_profile_shows_the_age_wall_to_a_stranger(client):
    """A sticker in a public place is scanned by whoever walks past, and a
    stranger never has a token — so the wall is the ordinary path here, not
    an edge case."""
    pid, _ = _profile(client, adult_mode=True)
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    assert r.status_code == 200
    assert "18+ only" in r.text
    # Nothing about the profile leaks past the wall.
    assert "Marcus Bell" not in r.text
    assert "<img" not in r.text


def test_the_age_wall_says_where_the_check_happens(client):
    """The venue that hosts the code is not the thing enforcing the gate."""
    pid, _ = _profile(client, adult_mode=True)
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    assert "not at whoever placed this code" in r.text


def test_a_picked_up_beacon_says_so_rather_than_erroring(client):
    """Stickers outlive the profiles behind them. Someone scanning a stale
    one should get a sentence, not a stack trace."""
    pid, _ = _profile(client)
    bid = _beacon(client, pid)["id"]
    client.delete(f"/beacons/{bid}")

    r = client.get(f"/b/{bid}")
    assert r.status_code == 410
    assert r.headers["content-type"].startswith("text/html")
    assert "picked up" in r.text


def test_an_unknown_beacon_is_a_page_too(client):
    r = client.get("/b/bcn_nothing")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("text/html")
    assert "Nothing here" in r.text


def test_a_departed_profile_stops_summoning(client):
    """The beacon outliving the profile is the same problem as the sticker
    outliving the beacon."""
    pid, _ = _profile(client)
    bid = _beacon(client, pid)["id"]
    db.connect().execute("UPDATE profiles SET status='departed' WHERE id=?",
                         (pid,))
    db.connect().commit()
    assert client.get(f"/b/{bid}").status_code == 410


def test_an_anonymous_profile_stays_anonymous_on_a_sticker(client):
    pid, _ = _profile(client, anonymous=True)
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    assert "Marcus Bell" not in r.text
    assert "anonymous persona" in r.text


def test_the_page_escapes_what_the_owner_typed(client):
    """Beacon labels and display names are owner-supplied and land in HTML."""
    pid, _ = _profile(client, display_name='Ada <script>alert(1)</script>')
    r = client.get(f"/b/{_beacon(client, pid, label='<b>x</b>')['id']}")
    assert "<script>alert(1)</script>" not in r.text
    assert "&lt;script&gt;" in r.text
    assert "<b>x</b>" not in r.text
