"""The wall's uploads: the user's own photos and footage, and the rules
they arrive under — bytes decide the kind, caps are stated, authentic
media never carries the AI mark, and a post attaches only its own
author's uploads.
"""

from qrme import media
from tests.test_capabilities import auth_header, make_profile

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64


def _upload(client, profile, data):
    return client.post(f"/profiles/{profile['id']}/media", content=data,
                       headers=auth_header(profile))


def test_an_upload_rides_a_post_and_the_feed(client):
    me = make_profile(client, display_name="Poster")
    up = _upload(client, me, PNG)
    assert up.status_code == 201, up.text
    picture = up.json()
    assert picture["kind"] == "image"
    # Authentic media, so never the AI mark — the same line the founder's
    # photograph draws.
    assert picture["ai_marked"] is False

    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "From today's walk.",
                          "media_ids": [picture["id"]]},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    assert [m["id"] for m in r.json()["media"]] == [picture["id"]]

    posts = client.get(f"/profiles/{me['id']}/wall").json()["posts"]
    assert posts[0]["media"][0]["url"] == picture["url"]
    # The file itself is served at that URL.
    got = client.get(picture["url"])
    assert got.status_code == 200 and got.content == PNG


def test_the_bytes_decide_the_kind_and_the_caps_hold(client):
    me = make_profile(client, display_name="Poster")
    up = _upload(client, me, MP4)
    assert up.status_code == 201 and up.json()["kind"] == "video"

    # A renamed anything that matches no magic is refused.
    assert _upload(client, me, b"MZ\x90\x00 not a picture").status_code == 422
    # An image over the image cap is refused even though video would fit.
    huge = PNG + b"\x00" * media.IMAGE_MAX
    assert _upload(client, me, huge).status_code == 413
    # The caps are published, so a client can warn before the upload.
    lim = client.get("/media/limits").json()
    assert lim["image"]["max_bytes"] == media.IMAGE_MAX
    assert lim["ai_marked"] is False


def test_documents_ride_too_and_keep_only_whitelisted_labels(client):
    me = make_profile(client, display_name="Poster")
    pdf = client.post(f"/profiles/{me['id']}/media?filename=notes.pdf",
                      content=b"%PDF-1.4 tiny", headers=auth_header(me)).json()
    assert pdf["kind"] == "file" and pdf["url"].endswith(".pdf")
    assert pdf["name"] == "notes.pdf"

    # PK magic keeps a whitelisted extension; anything fancier becomes .zip.
    docx = client.post(f"/profiles/{me['id']}/media?filename=cv.docx",
                       content=b"PK\x03\x04rest", headers=auth_header(me)).json()
    assert docx["url"].endswith(".docx")
    weird = client.post(f"/profiles/{me['id']}/media?filename=cv.exe",
                        content=b"PK\x03\x04rest", headers=auth_header(me)).json()
    assert weird["url"].endswith(".zip")
    # Text keeps txt/csv/md only — .html and .svg would execute, so a text
    # file claiming them serves as .txt, where markup is just characters.
    html = client.post(f"/profiles/{me['id']}/media?filename=page.html",
                       content=b"<script>alert(1)</script>",
                       headers=auth_header(me)).json()
    assert html["url"].endswith(".txt")

    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "my cv attached",
                          "media_ids": [pdf["id"]]}, headers=auth_header(me))
    assert r.status_code == 201
    posts = client.get(f"/profiles/{me['id']}/wall").json()["posts"]
    assert posts[0]["media"][0]["name"] == "notes.pdf"


def test_a_link_in_the_text_renders_as_the_video(client):
    """The field ask, verbatim: dropping a link in the text renders the
    video, not just the text — whitelisted platforms only."""
    me = make_profile(client, display_name="Poster")
    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "watch this "
                          "https://www.youtube.com/watch?v=dQw4w9WgXcQ !"},
                    headers=auth_header(me))
    assert r.status_code == 201
    video = r.json()["video"]
    assert video and video["platform"] == "youtube"
    assert video["video_id"] == "dQw4w9WgXcQ"

    # An unknown platform's link stays what it was: text in the body.
    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "see https://example.com/watch?v=nope"},
                    headers=auth_header(me))
    assert r.status_code == 201 and r.json()["video"] is None


def test_a_post_cannot_borrow_somebody_elses_upload(client):
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    theirs = _upload(client, b, PNG).json()
    r = client.post(f"/profiles/{a['id']}/wall",
                    json={"body": "mine now", "media_ids": [theirs["id"]]},
                    headers=auth_header(a))
    assert r.status_code == 422
    # And the refused post left nothing behind on either wall.
    assert client.get(f"/profiles/{a['id']}/wall").json()["posts"] == []


# -- the other side of the upload door ---------------------------------------
#
# `POST /profiles/{id}/media` shipped in 0.42.x with nothing that lists what
# came through it. Media was reachable only through the wall post it happened
# to ride on, so a photograph posted a year ago was in practice gone, and an
# upload attached to nothing was invisible from the first second. The profile
# homepage screen is what needed it: Photos and Videos would have been two
# buttons with no query behind them.
#
#     asked     can somebody put a photograph here
#     mattered  can anybody find it afterwards


def test_the_gallery_lists_what_came_through_the_upload_door(client):
    me = make_profile(client, display_name="Poster")
    picture = _upload(client, me, PNG).json()
    footage = _upload(client, me, MP4).json()
    # Attached to nothing at all — the case that was invisible before.
    assert client.get(f"/profiles/{me['id']}/media").json()["media"], \
        "an upload attached to no post is still theirs and still findable"

    got = client.get(f"/profiles/{me['id']}/media").json()
    assert {m["id"] for m in got["media"]} == {picture["id"], footage["id"]}
    assert got["kind"] is None
    # Newest first, so a page opens on what they did last.
    assert got["media"][0]["id"] == footage["id"]
    # The same facade the wall serves: a URL, never a path, and no AI mark on
    # somebody's own photograph.
    assert got["media"][0]["url"].startswith(media.ROUTE + "/")
    assert got["media"][0]["ai_marked"] is False


def test_photos_and_videos_are_one_query_with_a_filter(client):
    me = make_profile(client, display_name="Poster")
    picture = _upload(client, me, PNG).json()
    footage = _upload(client, me, MP4).json()

    images = client.get(f"/profiles/{me['id']}/media?kind=image").json()
    assert [m["id"] for m in images["media"]] == [picture["id"]]
    assert images["kind"] == "image"
    videos = client.get(f"/profiles/{me['id']}/media?kind=video").json()
    assert [m["id"] for m in videos["media"]] == [footage["id"]]

    # A kind outside the whitelist is a 422 rather than an empty list: an
    # empty answer to a misspelled filter reads as "they have no photos".
    assert client.get(
        f"/profiles/{me['id']}/media?kind=pictures").status_code == 422
    assert client.get("/profiles/prf_nobody/media").status_code == 404


def test_the_gallery_is_a_visitors_view_and_holds_only_its_own_profile(client):
    """Public on purpose, and scoped all the same.

    This is what a visitor came to look at, so it takes no token — but a
    profile's gallery is that profile's uploads and nobody else's, which is
    the half a public route still has to get right.
    """
    me = make_profile(client, display_name="Poster")
    them = make_profile(client, display_name="Somebody Else")
    mine = _upload(client, me, PNG).json()
    theirs = _upload(client, them, MP4).json()

    # No authorization header at all.
    ours = client.get(f"/profiles/{me['id']}/media").json()["media"]
    assert [m["id"] for m in ours] == [mine["id"]]
    yours = client.get(f"/profiles/{them['id']}/media").json()["media"]
    assert [m["id"] for m in yours] == [theirs["id"]]


def test_the_alt_text_travels_with_the_picture(client):
    """The uploader's own words for what it shows, served to people who
    cannot see it — on the gallery as well as on the post, or a photograph
    described once is undescribed everywhere it is actually looked at."""
    me = make_profile(client, display_name="Poster")
    client.post(f"/profiles/{me['id']}/media?alt=a gate at dusk",
                content=PNG, headers=auth_header(me))
    got = client.get(f"/profiles/{me['id']}/media").json()["media"]
    assert got[0]["alt"] == "a gate at dusk"
