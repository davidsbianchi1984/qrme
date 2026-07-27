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


def test_the_route_publishes_the_blindness(client):
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    r = client.get(f"/watch-parties/{party['id']}/context").json()
    assert r["you_have_not_seen_it"] is True
