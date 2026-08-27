"""Scanning a beacon: what a stranger with a phone actually gets.

The viewer here is not a user. They pointed a camera at a sticker, they have
no token, and they may not know what QRME is. Most of these tests are about
what that person must be told — and about the two states that are easy to
get wrong because nobody scans them on purpose: a rated profile, and a
beacon that was picked up.
"""

from qrme import avatars, db


def _profile(client, **over):
    body = {"plan": "pro",
            "owner_id": "o1", "kind": "fictional", "display_name": "Marcus Bell",
            "persona": "A retired fee-only financial planner.",
            "verification": {"birthdate": "1980-01-01",
                             "id_document": "passport", "liveness_check": True}}
    body.update(over)
    created = client.post("/profiles", json=body).json()
    # Hold the owner capability, so the owner-only calls below (placing a
    # beacon, listing them, picking one up) authorize. Safe for the scan tests
    # that assert what a *stranger* sees: `rated.viewer_is_adult` requires an
    # **interactor** token, so an owner token still meets the age wall — which
    # is the correct answer anyway, since an owner is not a verified adult
    # viewer by virtue of owning something.
    client.headers["authorization"] = f"Bearer {created['owner_token']}"
    return created["id"], created["owner_token"]


def _beacon(client, pid, label="stall 3, second floor", token=None, **extra):
    """Place a beacon as its owner.

    Placing one is owner-only: where a profile is left is a decision about the
    profile, and it used to be anybody's. `_profile` leaves the owner token on
    the client, so these calls authorize without passing one — `token` is for
    the tests that juggle two owners.
    """
    body = {"label": label, "location": "cafe", **extra}
    headers = {"authorization": f"Bearer {token}"} if token else None
    return client.post(f"/profiles/{pid}/beacons", json=body,
                       headers=headers).json()


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


def test_a_profile_with_no_portrait_shows_no_stock_face(client):
    """A stranger's first impression of a person who does not exist should
    not be a stock photograph of someone who does.

    That is the property, and it still holds exactly. The assertion used to
    be `"<img" not in r.text` — a proxy that assumed initials were the only
    way to satisfy it, from when three surfaces each invented their own
    answer for a missing face. The page now shows the empty frame every
    surface shows: our own drawing, depicting nobody, and no more a
    photograph of a real person than a monogram was.
    """
    pid, _ = _profile(client)
    r = client.get(f"/b/{_beacon(client, pid)['id']}")
    assert avatars.ADD_PHOTO in r.text
    # Nothing from the burned portrait collection, and no outside photograph.
    assert avatars.ASSET_ROUTE not in r.text
    assert avatars.PHOTO_ROUTE not in r.text


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
    from qrme import identity
    assert identity.anonymous_name(pid) in r.text


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
    pid, token = _profile(client)
    b = _beacon(client, pid, label="Tuesday 7pm, church basement", token=token,
                mode="room", topic="open share")
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
    pid, token = _profile(client)
    b = _beacon(client, pid, label="studio wall", token=token, mode="room")
    seats = db.connect().execute(
        "SELECT kind, ref_id FROM room_participants WHERE room_id=?",
        (b["room_id"],)).fetchall()
    assert [(s["kind"], s["ref_id"]) for s in seats] == [("profile", pid)]


def test_chat_stays_the_default(client):
    """Placing a beacon without asking for a room keeps the private
    conversation every existing beacon has."""
    pid, token = _profile(client)
    b = _beacon(client, pid, label="bench", token=token)
    assert b["mode"] == "chat" and b["room_id"] is None
    assert "Talk to Marcus" in client.get(f"/b/{b['id']}").text


def test_the_room_topic_falls_back_to_the_label(client):
    pid, token = _profile(client)
    b = _beacon(client, pid, label="front counter", token=token, mode="room")
    topic = db.connect().execute("SELECT topic FROM rooms WHERE id=?",
                                 (b["room_id"],)).fetchone()["topic"]
    assert topic == "front counter"


def test_a_rated_beacon_cannot_be_a_shared_room_at_all(client):
    """This used to be allowed and then walled, and the wall was doing work it
    should never have been asked to do.

    `docs/beacons.md` has said since the feature shipped that rated placements
    stay one-to-one — a shared room behind an adult code in a public place is
    a different product with different moderation questions: strangers who
    scanned a sticker on a wall, in one room together, with rated material
    between them. Nothing enforced it, so the combination was reachable by
    setting a flag, and the only thing standing in front of it was an age gate
    on the landing page.

    Refused rather than quietly downgraded to `chat`: somebody who asked for a
    room and silently got private threads would not find out until the
    fortieth person was talking to themselves.
    """
    pid, token = _profile(client, adult_mode=True)
    r = client.post(f"/profiles/{pid}/beacons",
                    json={"label": "backstage", "mode": "room"},
                    headers={"authorization": f"Bearer {token}"})
    assert r.status_code == 422
    assert "one-to-one" in r.json()["detail"]

    # And the ordinary rated placement still walls, as it always did.
    b = _beacon(client, pid, label="backstage", token=token)
    assert "18+ only" in client.get(f"/b/{b['id']}").text


def test_only_the_owner_decides_where_a_profile_is_left(client):
    """It was anybody's. A stranger could print stickers pointing at somebody
    else's profile, in places its owner never chose and could not see — and
    where a profile is left is a decision about the profile. A recovery
    sponsor's code belongs at a meeting and not on a billboard."""
    pid, _ = _profile(client)
    r = client.post(f"/profiles/{pid}/beacons", json={"label": "anywhere"},
                    headers={"authorization": ""})
    assert r.status_code == 401

    other, other_token = _profile(client, owner_id="o2",
                                  display_name="Someone Else")
    r = client.post(f"/profiles/{pid}/beacons", json={"label": "anywhere"},
                    headers={"authorization": f"Bearer {other_token}"})
    assert r.status_code == 403


def test_where_a_profile_has_been_left_is_not_public(client):
    """`label` and `location` are free text like "the back table at the
    Tuesday meeting" — a list of physical places associated with a person,
    readable by anybody holding the profile id. Scanning one code told you
    where all the others were."""
    pid, _ = _profile(client)
    _beacon(client, pid, label="the back table, Tuesday meeting")
    assert client.get(f"/profiles/{pid}/beacons",
                      headers={"authorization": ""}).status_code == 401
    mine = client.get(f"/profiles/{pid}/beacons")
    assert mine.status_code == 200
    assert mine.json()[0]["label"] == "the back table, Tuesday meeting"


def test_a_stranger_cannot_switch_off_your_stickers(client):
    """Unauthenticated, picking one up was a way to kill somebody else's
    printed codes — every one going dead at once, with the paper still on the
    wall and nothing to see wrong with it."""
    pid, _ = _profile(client)
    bid = _beacon(client, pid)["id"]
    assert client.delete(f"/beacons/{bid}",
                         headers={"authorization": ""}).status_code == 401
    assert client.get(f"/b/{bid}").status_code == 200      # still live
    assert client.delete(f"/beacons/{bid}").status_code == 200


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
    # Absolute, not the stored path. The consumer is a native client building
    # a URL from this string; a root-relative path is a valid href only in a
    # browser already on the origin, and the overlay is never that.
    assert card["portrait"] == "https://qrme.app/a/m.png"
    assert card["age_wall"] is False
    # `initials` used to ride along so an overlay could draw a monogram when
    # the portrait was absent. The portrait is never absent now — a profile
    # with no face is sent the frame — so the field was a second answer to a
    # question that has one, and on a hidden profile it was a monogram of the
    # name being hidden.
    assert set(card) == {"profile_id", "display_name", "watermark_line", "portrait",
                         "portrait_marked", "label", "shared_room",
                         "open_url", "age_wall"}


def test_the_mark_travels_with_the_face(client):
    """An overlay cannot be handed a portrait without also being handed the
    disclosure to draw beside it."""
    pid, _ = _profile(client)
    card = client.get(f"/b/{_beacon(client, pid)['id']}/card").json()
    assert card["watermark_line"] == "✦ AI · Marcus Bell"


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
    from qrme import identity
    assert card["display_name"] == identity.anonymous_name(pid)
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


def test_the_card_says_whether_the_portrait_already_carries_the_mark(client):
    """A shipped starter's portrait has the AI mark burned into its pixels; an
    owner-attached asset is somebody else's file and cannot be vouched for.
    A surface QRME does not control has to be able to tell the two apart."""
    from qrme import seed
    seed.seed()
    pid = client.get("/summon?ref=@otis_marsh").json()["profile"]["profile_id"]
    # A seeded starter's owner token is never handed out, so mint one — this
    # test is about what the card reports, not about who may place a beacon.
    from qrme import auth
    b = _beacon(client, pid, label="the shop counter",
                token=auth.issue("owner", pid))
    card = client.get(f"/b/{b['id']}/card").json()
    assert card["portrait"].endswith("/portraits/otis_marsh.webp")
    assert card["portrait_marked"] is True


def test_an_owner_attached_portrait_is_never_claimed_to_be_marked(client):
    pid, token = _profile(client)
    client.put(f"/profiles/{pid}/avatar",
               json={"asset": "https://example.test/face.png"},
               headers={"authorization": f"Bearer {token}"})
    b = _beacon(client, pid)
    card = client.get(f"/b/{b['id']}/card").json()
    assert card["portrait_marked"] is False
