"""The feed, and the line it draws between playing and pointing.

## What this round built

One public stream a person swipes: a video that loops, a swipe, another video
— and mixed into it the two things this product has that a video app does not.
**A live room you can walk into**, and **a desk with a real person behind it**,
with the shop behind the desk reachable without leaving the stream.

## The line the feed had to not cross

`post_videos` in `qrme/db.py` carries a comment written long before this
surface existed:

    The link and the id, never the file and never a thumbnail: re-hosting
    somebody's video is a copyright problem and a cached thumbnail is a copy
    of an image nobody granted.

That is why a QRME wall renders without making a single request to YouTube.
An endless autoplaying feed is the one surface where that promise is expensive
to keep and easy to lose: a viewer flicking past fifty cards would announce
their address, and their taste, to fifty other companies for footage they
never chose to watch.

    asked     does the feed play the next thing
    mattered  does swiping past something tell a stranger you were here

So the rule is drawn on **who holds the file**, and it is drawn in the server
rather than left to each of the four clients to remember:

* footage this deployment holds (`media`, `kind='video'`) comes back with
  `plays: true` and loops;
* everything else comes back `plays: false` with a facade — platform name,
  the poster's own title, a link — and makes its first request when somebody
  presses it.

`test_an_offsite_video_never_plays_by_itself` is the one that matters. It is
easy to satisfy today and easy to lose the day a client decides autoplay is a
nicer default, which is exactly why the assertion lives on the wire.

## A room and a desk are people

The two best things in this stream are the two that can embarrass somebody,
because entering a room and ringing a desk **reach a human being**. Every room
carries `entering` and every desk carries `ringing`: a plain sentence saying
what the press does, before it is pressed.

That is not decoration. A person who swipes into a live room is *in it*, and a
bell is somebody's attention rather than a message they can read later.

## What is public is what somebody made public

Nothing is in the feed by default. A post reaches it only if it is on the wall
and approved; a desk only if it is not closed; a room only while it is active
**and** attached to a desk that chose to be found — a room with no desk behind
it is somebody's private conversation and is not in this stream at any ranking.

The last test asserts the feed's read surface never names `memories` or
`source_items`, the same line `qrme/wall.py` draws for the ranked wall feed:
a feed is a new use of somebody's data, and this one is only ever built from
what they published.
"""

import re
from pathlib import Path

ADULT = {"birthdate": "1984-06-01"}
OFFSITE = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

#: A tiny well-formed MP4 header — enough for media.py to read `video` off the
#: bytes, which is where the kind comes from rather than from the filename.
MP4 = (b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"
       + b"\x00\x00\x00\x08free" + b"\x00" * 64)


def _profile(client, name):
    r = client.post("/profiles", json={
        "owner_id": f"owner-{name}", "kind": "self", "display_name": name,
        "persona": "A person who shows up on time and stays to the end.",
        "verification": ADULT, "plan": "pro"})
    assert r.status_code == 201, r.text
    body = r.json()
    return body["id"], {"authorization": f"Bearer {body['owner_token']}"}


def _hosted_post(client, pid, head, words="Here is the bench, finished."):
    up = client.post(f"/profiles/{pid}/media?filename=bench.mp4",
                     content=MP4, headers=head)
    assert up.status_code == 201, up.text
    assert up.json()["kind"] == "video", up.json()
    r = client.post(f"/profiles/{pid}/wall", headers=head,
                    json={"body": words, "media_ids": [up.json()["id"]]})
    assert r.status_code == 201, r.text
    return r.json()


def _offsite_post(client, pid, head):
    r = client.post(f"/profiles/{pid}/wall", headers=head,
                    json={"body": "Worth watching.", "video_url": OFFSITE,
                          "video_title": "A song"})
    assert r.status_code == 201, r.text
    return r.json()


def _desk(client, pid, head, name="Otis Marsh", trade="Carpentry"):
    r = client.post("/desks", json={
        "owner_id": pid, "display_name": name, "trade": trade,
        "attestor": "Vault Operations LLC",
        "basis": "met in person, photo ID checked",
        "location": "Leeds", "blurb": "Benches, tables, repairs."})
    assert r.status_code == 201, r.text
    return r.json()


def test_the_feed_answers_without_an_account(client):
    """A person who followed a link from a shop window has no token. The
    public half of this product stays public."""
    r = client.get("/feed")
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body) >= {"items", "cursor", "counts", "rules"}
    assert "posted publicly" in body["rules"]["public"] \
        or "publicly" in body["rules"]["public"]


def test_footage_this_deployment_holds_plays_and_loops(client):
    pid, head = _profile(client, "Rosa")
    _hosted_post(client, pid, head)
    items = client.get("/feed").json()["items"]
    videos = [i for i in items if i["kind"] == "video"]
    assert videos, f"the hosted post is not in the feed: {items}"
    one = videos[0]
    assert one["plays"] is True and one["loop"] is True
    assert one["src"].startswith("/media/")
    assert "Nothing is requested from anybody else" in one["note"]


def test_an_offsite_video_never_plays_by_itself(client):
    """The assertion this whole file exists for.

    Easy to satisfy today, easy to lose the day a client decides autoplay is a
    nicer default — so it is asserted on the wire, where all four clients read
    it, rather than in any one of them.
    """
    pid, head = _profile(client, "Marcus")
    _offsite_post(client, pid, head)
    items = client.get("/feed").json()["items"]
    offsite = [i for i in items if i["kind"] == "offsite"]
    assert offsite, f"the off-site post is not in the feed: {items}"
    one = offsite[0]
    assert one["plays"] is False, (
        "an off-site video came back playable — scrolling past it would "
        "announce the viewer to a company they never chose")
    assert one["loop"] is False
    assert "src" not in one, "the feed is serving a file it does not hold"
    assert one["facade"]["url"] == OFFSITE
    assert "thumbnail" not in str(one), (
        "a thumbnail is a copy of an image nobody granted")
    assert "until you press" in one["note"]


def test_every_item_says_why_it_is_there(client):
    pid, head = _profile(client, "Priya")
    _hosted_post(client, pid, head)
    _offsite_post(client, pid, head)
    _desk(client, pid, head)
    items = client.get("/feed").json()["items"]
    assert items
    missing = [i for i in items if not i.get("reason")]
    assert not missing, (
        "a card with no reason: a feed that cannot explain itself is one "
        f"nobody can audit — {missing}")


def test_a_desk_says_what_ringing_does_before_it_is_rung(client):
    pid, head = _profile(client, "Amara")
    _desk(client, pid, head)
    items = client.get("/feed").json()["items"]
    desks = [i for i in items if i["kind"] == "desk"]
    assert desks, items
    one = desks[0]
    assert "Ringing reaches a person" in one["ringing"]
    assert one["ring"].endswith("/bell"), (
        "the card points at a route that does not exist — the bell is "
        "/desks/{id}/bell")
    # The desk's own claim, and never an AI watermark: a desk that carried one
    # would be telling a visitor this person does not exist.
    assert one["human"] is True and one["ai"] is False
    assert one["plays"] is False


def test_the_shop_behind_a_desk_is_reachable_from_the_stream(client):
    pid, head = _profile(client, "Lena")
    _desk(client, pid, head)
    r = client.post("/shops", headers=head, json={
        "profile_id": pid, "name": "Marsh & Daughter",
        "blurb": "Benches and repairs.", "tag": "carpentry"})
    assert r.status_code in (200, 201), r.text
    shop_id = r.json()["id"] if "id" in r.json() else r.json()["shop_id"]
    client.post(f"/shops/{shop_id}/offerings", headers=head, json={
        "kind": "goods", "title": "Oak bench", "blurb": "Two metres.",
        "price": 240.0})
    desks = [i for i in client.get("/feed").json()["items"]
             if i["kind"] == "desk"]
    assert desks and desks[0]["shop"], "the shop is not reachable from the feed"
    assert desks[0]["shop"]["offerings"], desks[0]["shop"]


def test_a_rated_desk_is_absent_rather_than_blurred(client):
    """A gate, not a tease. The reader who is not verified does not learn that
    the rated desk exists."""
    pid, head = _profile(client, "Vivienne")
    # A rated desk can only be opened by the person on it — `qrme/desks.py`
    # refuses a third party attesting in somebody else's name — so the
    # attestor here is the owner, attesting for themselves.
    r = client.post("/desks", json={
        "owner_id": pid, "display_name": "Vivienne", "trade": "Performance",
        "attestor": pid, "basis": "attesting for myself",
        "rated": True})
    assert r.status_code == 201, r.text
    desk_id = r.json()["desk_id"] if "desk_id" in r.json() else r.json()["id"]
    items = client.get("/feed").json()["items"]
    assert not [i for i in items if i["kind"] == "desk" and i["id"] == desk_id]
    assert client.get(f"/feed/{desk_id}").status_code == 404, (
        "404 rather than 403: a 403 announces that the item exists")


def test_a_shared_link_opens_one_card_by_the_same_rules(client):
    pid, head = _profile(client, "Otis")
    post = _offsite_post(client, pid, head)
    r = client.get(f"/feed/{post['id']}")
    assert r.status_code == 200, r.text
    assert r.json()["plays"] is False, (
        "the deep link took a second path and disagreed with the stream "
        "about what plays")


def test_a_stale_cursor_opens_the_feed_rather_than_failing(client):
    assert client.get("/feed?cursor=not-a-cursor").status_code == 200


def test_a_page_is_capped_however_much_is_asked_for(client):
    assert client.get("/feed?limit=5000").status_code == 200


def test_the_feed_never_reads_a_private_table():
    """The same line `qrme/wall.py` draws for the ranked wall feed. A feed is
    a new use of somebody's data, and this one is built only from what they
    published."""
    src = (Path(__file__).resolve().parent.parent
           / "qrme" / "feed.py").read_text(encoding="utf-8")
    queries = " ".join(re.findall(r'"(SELECT[^"]*)"', src))
    for private in ("memories", "source_items", "messages", "vault"):
        assert private not in queries, (
            f"the feed's queries name `{private}` — the feed reads what was "
            "published and nothing else")
