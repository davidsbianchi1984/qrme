"""Posting a video that lives on somebody else's platform.

The tests worth having are not about YouTube URL shapes. They are about the two
promises this feature makes and could quietly stop keeping: that nothing is
copied, and that nothing is requested from the other platform until a viewer
asks for it.
"""

import pytest

from qrme import db, embeds
from tests.test_capabilities import auth_header, make_profile


# -- recognising a link ------------------------------------------------------

@pytest.mark.parametrize("url,vid", [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://m.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ"),
])
def test_the_shapes_a_youtube_link_actually_arrives_in(url, vid):
    got = embeds.parse(url)
    assert got["platform"] == "youtube"
    assert got["video_id"] == vid


def test_the_canonical_url_is_rebuilt_rather_than_kept(client):
    """The pasted string is thrown away. A tracking query, a redirect
    parameter or a lookalike path cannot ride along into what gets stored and
    later opened, because what gets stored is built from the id."""
    got = embeds.parse(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&si=TRACKINGTOKEN")
    assert got["url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert "TRACKINGTOKEN" not in got["url"]
    assert "TRACKINGTOKEN" not in got["embed_url"]


def test_a_platform_nobody_listed_is_refused_by_name():
    """An allowlist, not a pattern. "Looks like a video URL" is how an open
    redirect becomes a feature, and a refusal nobody can read is one people
    work around instead of understanding."""
    with pytest.raises(embeds.EmbedError) as err:
        embeds.parse("https://videos.example.com/watch/12345")
    assert "videos.example.com" in str(err.value)
    assert "YouTube" in str(err.value)


def test_a_javascript_link_is_not_a_video():
    with pytest.raises(embeds.EmbedError):
        embeds.parse("javascript:alert(1)")


def test_a_channel_link_is_not_a_video(client):
    """A Twitch channel points at whatever happens to be live, which is not the
    thing somebody chose to post."""
    with pytest.raises(embeds.EmbedError):
        embeds.parse("https://www.twitch.tv/somestreamer")
    assert embeds.parse("https://www.twitch.tv/videos/123456789")["video_id"] \
        == "123456789"


def test_a_link_on_the_right_host_with_no_video_in_it_says_so():
    with pytest.raises(embeds.EmbedError) as err:
        embeds.parse("https://www.youtube.com/feed/subscriptions")
    assert "no video in it" in str(err.value)


# -- what is and is not stored ----------------------------------------------

def test_nothing_of_the_video_itself_is_copied(client):
    """The promise the copyright question turns on. What is kept is a pointer
    and the poster's own words — no file, no scraped title, no thumbnail."""
    me = make_profile(client, display_name="Poster")
    post = client.post(
        f"/profiles/{me['id']}/wall",
        json={"body": "Worth eight minutes.",
              "video_url": "https://youtu.be/dQw4w9WgXcQ",
              "video_title": "the compounding talk"},
        headers=auth_header(me)).json()

    row = dict(db.connect().execute(
        "SELECT * FROM post_videos WHERE post_id=?", (post["id"],)).fetchone())
    assert set(row) == {"post_id", "platform", "video_id", "url", "title",
                        "created_at"}
    # The title is what the poster typed. Nothing fetched it from YouTube.
    assert row["title"] == "the compounding talk"


def test_the_facade_carries_no_thumbnail(client):
    """Its absence is the feature. Fetching a thumbnail at render time is
    exactly the request this design exists to not make, and caching one is a
    copy of an image nobody granted."""
    me = make_profile(client, display_name="Poster")
    post = client.post(f"/profiles/{me['id']}/wall",
                       json={"body": "Look.",
                             "video_url": "https://youtu.be/dQw4w9WgXcQ"},
                       headers=auth_header(me)).json()
    assert post["video"]["thumbnail"] is None
    assert post["video"]["loads_on_press"] is True


def test_the_viewer_is_told_before_anything_is_requested(client):
    """A privacy promise that holds only until an embed loads is not one. The
    note is what makes pressing play a decision rather than a side effect."""
    me = make_profile(client, display_name="Poster")
    client.post(f"/profiles/{me['id']}/wall",
                json={"body": "Look.",
                      "video_url": "https://youtu.be/dQw4w9WgXcQ"},
                headers=auth_header(me))
    entry = client.get(f"/profiles/{me['id']}/wall").json()["posts"][0]
    assert "until you press play" in entry["video"]["note"]
    assert "YouTube" in entry["video"]["note"]


def test_the_platform_list_is_published(client):
    r = client.get("/videos/platforms").json()
    assert {p["key"] for p in r["platforms"]} == set(embeds.PLATFORMS)
    assert "a cached thumbnail" in r["never_stored"]


# -- posting through the wall ------------------------------------------------

def test_a_bad_link_does_not_leave_an_orphan_post(client):
    """Validated before the row is written. Attaching afterwards would leave a
    post somebody has to go and delete to fix a typo."""
    me = make_profile(client, display_name="Poster")
    before = len(client.get(f"/profiles/{me['id']}/wall").json()["posts"])
    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "Look at this.",
                          "video_url": "https://videos.example.com/x"},
                    headers=auth_header(me))
    assert r.status_code == 422
    after = len(client.get(f"/profiles/{me['id']}/wall").json()["posts"])
    assert after == before


def test_a_video_post_is_still_a_post(client):
    """It inherits everything: moderation on the words, the audience layer's
    like and share, and its author's rating. A video is an attachment, not a
    parallel kind of thing with its own rules."""
    me = make_profile(client, display_name="Poster")
    them = make_profile(client, display_name="Reader")
    post = client.post(f"/profiles/{me['id']}/wall",
                       json={"body": "Worth watching.",
                             "video_url": "https://vimeo.com/123456789"},
                       headers=auth_header(me)).json()
    assert post["status"] == "approved"
    assert client.post(f"/posts/{post['id']}/like",
                       json={"actor_id": them["id"]}).status_code == 201
    assert client.post(f"/posts/{post['id']}/share",
                       json={"actor_id": them["id"],
                             "channel": "link"}).status_code == 201


def test_the_words_around_a_video_are_moderated_like_any_post(client):
    """The link being fine says nothing about what was written next to it."""
    me = make_profile(client, display_name="Poster")
    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "kill yourself",
                          "video_url": "https://youtu.be/dQw4w9WgXcQ"},
                    headers=auth_header(me))
    assert r.json()["status"] == "blocked"
    assert client.get(f"/profiles/{me['id']}/wall").json()["posts"] == []


def test_one_video_per_post(client):
    me = make_profile(client, display_name="Poster")
    post = client.post(f"/profiles/{me['id']}/wall",
                       json={"body": "One.",
                             "video_url": "https://youtu.be/dQw4w9WgXcQ"},
                       headers=auth_header(me)).json()
    with pytest.raises(embeds.EmbedError):
        embeds.attach(post["id"], "https://vimeo.com/123456789")
