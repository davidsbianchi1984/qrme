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


# -- shared mode: one sticker, one conversation ----------------------------

def test_a_room_beacon_puts_everyone_in_the_same_conversation(client):
    """A sticker at a meeting, a class, a workshop: the people who found the
    same code should be talking to the profile together, not each in their
    own private thread."""
    pid, _ = _profile(client)
    b = client.post(f"/profiles/{pid}/beacons",
                    json={"label": "Tuesday 7pm, church basement",
                          "mode": "room", "topic": "open share"}).json()
    assert b["mode"] == "room"
    assert b["room_id"]

    r = client.get(f"/b/{b['id']}")
    assert "Join the conversation" in r.text
    assert b["room_id"] in r.text
    assert "you may not be the only one here" in r.text
    # Not the private 1:1 path.
    assert "Talk to Marcus" not in r.text


def test_the_profile_is_already_in_the_room(client):
    """Nobody should scan a sticker and arrive somewhere empty."""
    pid, _ = _profile(client)
    b = client.post(f"/profiles/{pid}/beacons",
                    json={"label": "studio wall", "mode": "room"}).json()
    seats = db.connect().execute(
        "SELECT kind, ref_id FROM room_participants WHERE room_id=?",
        (b["room_id"],)).fetchall()
    assert [(s["kind"], s["ref_id"]) for s in seats] == [("profile", pid)]


def test_chat_stays_the_default(client):
    """Placing a beacon without asking for a room keeps the private
    conversation every existing beacon has."""
    pid, _ = _profile(client)
    b = client.post(f"/profiles/{pid}/beacons", json={"label": "bench"}).json()
    assert b["mode"] == "chat" and b["room_id"] is None
    assert "Talk to Marcus" in client.get(f"/b/{b['id']}").text


def test_the_room_topic_falls_back_to_the_label(client):
    pid, _ = _profile(client)
    b = client.post(f"/profiles/{pid}/beacons",
                    json={"label": "front counter", "mode": "room"}).json()
    topic = db.connect().execute("SELECT topic FROM rooms WHERE id=?",
                                 (b["room_id"],)).fetchone()["topic"]
    assert topic == "front counter"


def test_a_rated_room_beacon_still_walls(client):
    """Shared mode does not open a side door around the age gate."""
    pid, _ = _profile(client, adult_mode=True)
    b = client.post(f"/profiles/{pid}/beacons",
                    json={"label": "backstage", "mode": "room"}).json()
    r = client.get(f"/b/{b['id']}")
    assert "18+ only" in r.text
    assert b["room_id"] not in r.text


def test_the_call_to_action_survives_an_honorific(client):
    """"Talk to Dr." is what the naive first-word split produced."""
    pid, _ = _profile(client, display_name="Dr. Sana Iqbal")
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    assert "Talk to Sana" in r.text
    assert "Talk to Dr." not in r.text


# -- the in-camera card ----------------------------------------------------

def test_the_card_is_small_enough_to_fetch_while_the_camera_runs(client):
    """The overlay draws this over the sticker in a live viewfinder, so it
    carries what a face needs and nothing else — no chat URLs, no status
    notes, none of the full summon card."""
    pid, token = _profile(client)
    client.put(f"/profiles/{pid}/avatar", json={"asset": "/a/m.png"},
               headers={"authorization": f"Bearer {token}"})
    b = _beacon(client, pid)

    card = client.get(f"/b/{b['id']}/card").json()
    assert card["display_name"] == "Marcus Bell"
    assert card["portrait"] == "/a/m.png"
    assert card["initials"] == "MB"
    assert card["age_wall"] is False
    assert set(card) == {"profile_id", "display_name", "watermark", "portrait",
                         "initials", "label", "shared_room", "open_url",
                         "age_wall"}


def test_the_mark_travels_with_the_face(client):
    """An overlay cannot be handed a portrait without also being handed the
    disclosure to draw beside it."""
    pid, _ = _profile(client)
    card = client.get(f"/b/{_beacon(client, pid)['id']}/card").json()
    assert card["watermark"] == "✦ AI · Marcus Bell"


def test_the_rated_card_carries_nothing_to_leak(client):
    """The overlay must be able to render the wall without ever holding the
    name or the portrait — so neither is sent."""
    pid, _ = _profile(client, adult_mode=True)
    card = client.get(f"/b/{_beacon(client, pid)['id']}/card").json()
    assert card["age_wall"] is True
    assert "display_name" not in card
    assert "portrait" not in card
    assert "Marcus Bell" not in str(card)


def test_an_anonymous_profile_stays_anonymous_in_the_camera(client):
    pid, _ = _profile(client, anonymous=True)
    card = client.get(f"/b/{_beacon(client, pid)['id']}/card").json()
    assert card["display_name"] == "anonymous persona"
    assert "Marcus Bell" not in str(card)


def test_a_shared_beacon_says_so_on_the_card(client):
    """Someone about to walk into a room deserves to know before they tap."""
    pid, _ = _profile(client)
    b = client.post(f"/profiles/{pid}/beacons",
                    json={"label": "back table", "mode": "room"}).json()
    assert client.get(f"/b/{b['id']}/card").json()["shared_room"] == b["room_id"]


def test_scanning_through_the_camera_counts(client):
    """Same person, same sticker — the only difference is they never left the
    camera, so it counts the same."""
    pid, _ = _profile(client)
    bid = _beacon(client, pid)["id"]
    client.get(f"/b/{bid}/card")
    client.get(f"/b/{bid}")
    assert client.get(f"/profiles/{pid}/beacons").json()[0]["scans"] == 2


def test_a_picked_up_beacon_has_no_card(client):
    pid, _ = _profile(client)
    bid = _beacon(client, pid)["id"]
    client.delete(f"/beacons/{bid}")
    assert client.get(f"/b/{bid}/card").status_code == 404
