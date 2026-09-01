"""Watching together, with synthetic profiles in the room.

The test that matters most is the one about what a profile is told: it has not
seen the video, and it is told so rather than merely starved of the footage.
A model handed only chat lines will fill the gap with a plausible opinion about
something nobody showed it, and that is the most ordinary-looking lie this
product could tell.
"""

import pytest

from qrme import db, embeds, seed, wall, watchparty
from tests.test_capabilities import auth_header, make_profile


def _video_post(client):
    me = make_profile(client, display_name="Poster")
    post = client.post(f"/profiles/{me['id']}/wall",
                       json={"body": "Worth eight minutes.",
                             "video_url": "https://youtu.be/dQw4w9WgXcQ",
                             "video_title": "the compounding talk"},
                       headers=auth_header(me)).json()
    return me, post


# -- what the room is ---------------------------------------------------------

def test_a_party_hangs_off_a_post_not_a_url(client):
    """So it inherits everything the post already carries — its author's
    rating, its moderation verdict, and the fact that the link was checked
    against the allowlist when it was posted."""
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    assert party["post_id"] == post["id"]
    assert party["video"]["platform_name"] == "YouTube"


def test_a_post_with_no_video_cannot_be_watched(client):
    me = make_profile(client, display_name="Poster")
    post = client.post(f"/profiles/{me['id']}/wall", json={"body": "Just words."},
                       headers=auth_header(me)).json()
    with pytest.raises(watchparty.PartyError):
        watchparty.start(post["id"], "person_1")


def test_a_blocked_post_cannot_be_watched_together(client):
    """A party would otherwise be a way to put a post in front of people that
    the wall refuses to show them."""
    me = make_profile(client, display_name="Loud")
    post = client.post(f"/profiles/{me['id']}/wall",
                       json={"body": "kill yourself",
                             "video_url": "https://youtu.be/dQw4w9WgXcQ"},
                       headers=auth_header(me)).json()
    assert post["status"] == "blocked"
    with pytest.raises(watchparty.PartyError):
        watchparty.start(post["id"], "person_1")


# -- synthetic profiles in the room ------------------------------------------

def test_profiles_can_be_in_the_party(client):
    """The whole point of this version of the feature."""
    seed.seed()
    marcus = db.connect().execute(
        "SELECT profile_id FROM handles WHERE handle='marcus_bell'").fetchone()[0]
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    watchparty.join(party["id"], marcus, kind="profile")
    after = watchparty.get(party["id"])
    assert after["profiles"] == 1 and after["people"] == 1


def test_every_member_says_whether_it_is_synthetic(client):
    """A room where you cannot tell which of the names is a person is the room
    this platform exists not to build."""
    seed.seed()
    marcus = db.connect().execute(
        "SELECT profile_id FROM handles WHERE handle='marcus_bell'").fetchone()[0]
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    watchparty.join(party["id"], marcus, kind="profile")
    kinds = {m["member_id"]: m["synthetic"]
             for m in watchparty.members(party["id"])}
    assert kinds[marcus] is True
    assert kinds["person_1"] is False


def test_a_profile_that_does_not_exist_cannot_join(client):
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    with pytest.raises(watchparty.PartyError):
        watchparty.join(party["id"], "nope_1", kind="profile")


# -- the honesty rule ---------------------------------------------------------

def test_the_profile_is_told_it_has_not_seen_the_video(client):
    """Not merely starved of it. Starving a model of context and hoping is not
    a safeguard; telling it the truth about its own position is."""
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    ctx = watchparty.prompt_context(party["id"])
    assert ctx["you_have_not_seen_it"] is True
    assert "cannot see it" in ctx["instruction"]
    assert "say you have not seen it" in ctx["instruction"]


def test_the_context_contains_no_description_or_transcript(client):
    """Because there is none on this side. Nothing fetches the video and
    nothing transcribes it, so there is nothing an opinion could be built on
    except the title somebody typed and what the room said."""
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    ctx = watchparty.prompt_context(party["id"])
    assert ctx["watching"]["description_available"] is False
    assert ctx["watching"]["transcript_available"] is False
    assert ctx["watching"]["title"] == "the compounding talk"
    assert set(ctx) == {"watching", "position_s", "playing", "recent",
                        "you_have_not_seen_it", "instruction"}


def test_the_context_carries_what_people_said_and_where(client):
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    watchparty.seek(party["id"], "person_1", 240)
    watchparty.say(party["id"], "person_1", "this bit is the good one")
    ctx = watchparty.prompt_context(party["id"])
    assert ctx["recent"][-1]["said"] == "this bit is the good one"
    assert ctx["recent"][-1]["at"] == 240


# -- the position is a number, not a player -----------------------------------

def test_only_the_host_moves_the_position(client):
    """Otherwise the last person to scrub decides what everyone is looking at,
    which is a fight rather than a feature."""
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    watchparty.join(party["id"], "person_2")
    with pytest.raises(watchparty.PartyError):
        watchparty.seek(party["id"], "person_2", 90)
    assert watchparty.seek(party["id"], "person_1", 90)["position_s"] == 90


def test_the_party_does_not_press_play_for_anybody(client):
    """A party that pre-loaded the video for twenty people would have made
    twenty requests to YouTube that nobody agreed to."""
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    assert party["loads_on_press"] is True
    assert "loads only when you press play" in party["note"]
    assert party["video"]["thumbnail"] is None


# -- chat ---------------------------------------------------------------------

def test_a_line_is_stamped_with_where_the_room_was(client):
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    watchparty.seek(party["id"], "person_1", 617)
    watchparty.say(party["id"], "person_1", "here it comes")
    assert watchparty.chat(party["id"])[0]["position_s"] == 617


def test_you_cannot_talk_in_a_party_you_are_not_in(client):
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    with pytest.raises(watchparty.PartyError):
        watchparty.say(party["id"], "stranger_1", "hello")


def test_party_chat_is_moderated_like_anything_else(client):
    """A watch party does not get to be the surface where that relaxes."""
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    said = watchparty.say(party["id"], "person_1", "kill yourself")
    assert said["status"] == "blocked"
    assert watchparty.chat(party["id"]) == []


def test_a_profiles_line_is_marked_as_a_profiles(client):
    seed.seed()
    marcus = db.connect().execute(
        "SELECT profile_id FROM handles WHERE handle='marcus_bell'").fetchone()[0]
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    watchparty.join(party["id"], marcus, kind="profile")
    watchparty.say(party["id"], marcus, "what are people making of it?")
    line = watchparty.chat(party["id"])[0]
    assert line["synthetic"] is True


def test_the_route_publishes_the_blindness_to_members_only(client):
    """Two properties in one place, because they were added at different times
    and the second broke this test.

    The context is what a synthetic profile in the room is told, and it says it
    has not watched. It is also the room's private state, so it is readable by
    the people in the room and nobody else — this test used to call it with no
    token at all and pass, which is exactly the gap `require_self` closed.
    """
    me, post = _video_post(client)
    party = watchparty.start(post["id"], me["id"])

    r = client.get(f"/watch-parties/{party['id']}/context",
                   headers=auth_header(me))
    assert r.status_code == 200
    assert r.json()["you_have_not_seen_it"] is True

    assert client.get(f"/watch-parties/{party['id']}/context",
                      headers={"authorization": ""}).status_code == 401


# -- a pasted link is met, not refused ----------------------------------------
#
# The field report that forced this was a screenshot: a YouTube link pasted
# into the screen's one field, answered with "that post has no video to
# watch" — technically true and humanly useless. A pasted link is the most
# natural input that field gets.

def test_a_pasted_link_starts_a_party(client):
    me = make_profile(client, display_name="Host")
    r = client.post("/watch-parties",
                    json={"video_url": "https://youtu.be/dQw4w9WgXcQ",
                          "host_id": me["id"], "title": "movie night"},
                    headers=auth_header(me))
    assert r.status_code == 201
    party = r.json()
    assert party["video"]["platform_name"] == "YouTube"
    assert party["video"]["video_id"] == "dQw4w9WgXcQ"
    assert party["title"] == "movie night"


def test_a_link_pasted_into_the_post_id_field_is_recognised(client):
    """Every client's one input box sends `post_id`, so a URL arriving under
    that name is what the deployed field actually produces."""
    me = make_profile(client, display_name="Host")
    r = client.post("/watch-parties",
                    json={"post_id": "https://youtu.be/dQw4w9WgXcQ",
                          "host_id": me["id"]},
                    headers=auth_header(me))
    assert r.status_code == 201
    assert r.json()["video"]["platform_name"] == "YouTube"


def test_a_link_party_faces_the_same_allowlist_a_post_does(client):
    """Nothing plays in a party that could not have been posted."""
    me = make_profile(client, display_name="Host")
    r = client.post("/watch-parties",
                    json={"video_url": "https://example.com/watch?v=abc",
                          "host_id": me["id"]},
                    headers=auth_header(me))
    assert r.status_code == 422
    assert "not one of them" in r.json()["detail"]


def test_a_link_party_fabricates_no_post_on_anybodys_wall(client):
    """The video hangs off the party's own id — no posts row exists for it,
    so it can never surface on a wall or in a feed."""
    me = make_profile(client, display_name="Host")
    party = watchparty.start_from_url("https://youtu.be/dQw4w9WgXcQ",
                                      me["id"])
    assert party["post_id"] == party["id"]
    assert db.connect().execute("SELECT 1 FROM posts WHERE id=?",
                                (party["id"],)).fetchone() is None


def test_a_link_party_still_tells_the_profile_it_has_not_seen_it(client):
    """The blindness instruction does not depend on how the party started."""
    me = make_profile(client, display_name="Host")
    party = watchparty.start_from_url("https://youtu.be/dQw4w9WgXcQ",
                                      me["id"])
    ctx = watchparty.prompt_context(party["id"])
    assert ctx["you_have_not_seen_it"] is True
    assert ctx["watching"]["platform"] == "YouTube"


def test_a_wrong_id_names_both_ways_in(client):
    """The refusal tells you what the field takes — an id or a link — instead
    of blaming a post nobody named."""
    me = make_profile(client, display_name="Host")
    r = client.post("/watch-parties",
                    json={"post_id": "not-a-real-post",
                          "host_id": me["id"]},
                    headers=auth_header(me))
    assert r.status_code == 422
    assert "paste the video's own link" in r.json()["detail"]


# -- public is a browse door; the id stays the private one --------------------
#
# "IDs should be for just jumping into specific rooms or private rooms" — the
# design in one sentence. A party is private by default and reachable only by
# its id; publishing is the host's deliberate act, and what it opens is a
# card a stranger can join from without ever seeing an id.

def _hosted_party(client, title="movie night"):
    me = make_profile(client, display_name="Host")
    r = client.post("/watch-parties",
                    json={"video_url": "https://youtu.be/dQw4w9WgXcQ",
                          "host_id": me["id"], "title": title},
                    headers=auth_header(me))
    return me, r.json()


def test_a_party_is_private_until_the_host_publishes_it(client):
    me, party = _hosted_party(client)
    assert party["public"] is False
    assert client.get("/watch-parties/public").json()["parties"] == []

    r = client.post(f"/watch-parties/{party['id']}/listing",
                    headers=auth_header(me))
    assert r.status_code == 201
    assert r.json()["public"] is True
    cards = client.get("/watch-parties/public").json()["parties"]
    assert [c["id"] for c in cards] == [party["id"]]


def test_only_the_host_moves_it_between_public_and_private(client):
    me, party = _hosted_party(client)
    other = make_profile(client, display_name="Guest")
    assert client.post(f"/watch-parties/{party['id']}/listing",
                       headers=auth_header(other)).status_code == 403
    client.post(f"/watch-parties/{party['id']}/listing",
                headers=auth_header(me))
    assert client.delete(f"/watch-parties/{party['id']}/listing",
                         headers=auth_header(other)).status_code == 403


def test_unpublishing_closes_the_browse_door_not_the_room(client):
    me, party = _hosted_party(client)
    client.post(f"/watch-parties/{party['id']}/listing",
                headers=auth_header(me))
    r = client.delete(f"/watch-parties/{party['id']}/listing",
                      headers=auth_header(me))
    assert r.json()["public"] is False
    assert client.get("/watch-parties/public").json()["parties"] == []
    # The id keeps working: the host still reads the room.
    assert client.get(f"/watch-parties/{party['id']}",
                      headers=auth_header(me)).status_code == 200


def test_the_public_card_carries_counts_and_a_facade_never_names(client):
    """Member names and chat stay members-only; a browse card that listed
    who is inside would publish presence nobody agreed to."""
    me, party = _hosted_party(client)
    client.post(f"/watch-parties/{party['id']}/listing",
                headers=auth_header(me))
    watchparty.say(party["id"], me["id"], "just us so far")
    card = client.get("/watch-parties/public").json()["parties"][0]
    assert card["people"] == 1 and card["video"]["platform_name"] == "YouTube"
    assert card["plays"] is False
    assert "joining" in card
    flat = str(card)
    assert "Host" not in flat and "just us so far" not in flat


def test_a_public_party_needs_a_findable_title(client):
    me, party = _hosted_party(client, title="")
    r = client.post(f"/watch-parties/{party['id']}/listing",
                    headers=auth_header(me))
    assert r.status_code == 422
    assert "needs a title" in r.json()["detail"]


def test_ending_a_party_takes_it_off_the_public_surfaces(client):
    me, party = _hosted_party(client)
    client.post(f"/watch-parties/{party['id']}/listing",
                headers=auth_header(me))
    client.post(f"/watch-parties/{party['id']}/end", headers=auth_header(me))
    assert client.get("/watch-parties/public").json()["parties"] == []


def test_a_public_party_rides_the_feed_beside_rooms_and_desks(client):
    from qrme import feed
    me, party = _hosted_party(client)
    client.post(f"/watch-parties/{party['id']}/listing",
                headers=auth_header(me))
    page = feed.stream()
    kinds = [i["kind"] for i in page["cards"]]
    assert "party" in kinds
    assert page["counts"]["party"] == 1
