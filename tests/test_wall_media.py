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
