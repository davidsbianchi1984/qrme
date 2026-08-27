"""The community wall, and the feed that decides what you see of it.

The tests that matter are about the feed rather than the posting. Publishing is
easy to get right; a ranked feed is where a platform quietly starts using data
it was not given for that, and where content first reaches somebody who did not
ask for it.
"""

import pytest

from qrme import audience, db, friends, seed, wall
from tests.test_capabilities import auth_header, make_profile


def _handles(client):
    seed.seed()
    conn = db.connect()
    def pid(h):
        return conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                            (h,)).fetchone()["profile_id"]
    return pid


# -- publishing --------------------------------------------------------------

def test_a_post_lands_on_the_wall(client):
    me = make_profile(client, display_name="Poster")
    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "First one."}, headers=auth_header(me))
    assert r.status_code == 201, r.text
    posts = client.get(f"/profiles/{me['id']}/wall").json()["posts"]
    assert [p["body"] for p in posts] == ["First one."]


def test_only_the_owner_posts_to_their_wall(client):
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    r = client.post(f"/profiles/{a['id']}/wall", json={"body": "hi"},
                    headers=auth_header(b))
    assert r.status_code in (401, 403)


def test_a_blocked_post_is_kept_for_its_author_and_hidden_from_everyone(client):
    """The shape the audience layer already uses for a comment. Dropping it
    silently teaches the author nothing; showing it teaches everyone else the
    filter does not work."""
    me = make_profile(client, display_name="Loud")
    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "kill yourself"}, headers=auth_header(me))
    assert r.status_code == 201
    assert r.json()["status"] == "blocked"
    assert r.json()["blocked_reason"]

    assert client.get(f"/profiles/{me['id']}/wall").json()["posts"] == []
    owner_view = wall.wall(me["id"], owner=True)
    assert owner_view[0]["status"] == "blocked"
    assert owner_view[0]["blocked_reason"]


def test_an_empty_post_is_refused(client):
    me = make_profile(client, display_name="Blank")
    r = client.post(f"/profiles/{me['id']}/wall", json={"body": "   "},
                    headers=auth_header(me))
    assert r.status_code == 422


# -- the audience layer already had the verbs --------------------------------

def test_a_post_is_an_audience_target_rather_than_a_new_system(client):
    """Like, comment, share and subscribe already work against a (kind, id)
    pair. A parallel set of tables for posts would have drifted from them
    inside a round."""
    assert "post" in audience.TARGETS
    me = make_profile(client, display_name="Author")
    them = make_profile(client, display_name="Reader")
    post = client.post(f"/profiles/{me['id']}/wall", json={"body": "Hello."},
                       headers=auth_header(me)).json()

    r = client.post(f"/posts/{post['id']}/like",
                    json={"actor_id": them["id"]})
    assert r.status_code in (200, 201), r.text
    assert client.get(f"/profiles/{me['id']}/wall").json()["posts"][0]["likes"] == 1


def test_a_like_on_a_post_is_idempotent(client):
    """Inherited from the audience layer's UNIQUE (target, actor) — which is
    the whole reason to reuse it rather than write a counter."""
    me = make_profile(client, display_name="Author")
    them = make_profile(client, display_name="Reader")
    post = client.post(f"/profiles/{me['id']}/wall", json={"body": "Twice."},
                       headers=auth_header(me)).json()
    for _ in range(3):
        client.post(f"/posts/{post['id']}/like", json={"actor_id": them["id"]})
    assert client.get(f"/profiles/{me['id']}/wall").json()["posts"][0]["likes"] == 1


# -- what the feed is allowed to know ---------------------------------------

def test_the_feed_never_reads_source_material_or_memories(client):
    """The line the data promise turns on, asserted rather than described.

    A For You feed is a new use of a person's data. This one ranks on public
    actions — friendships, engagement, tags, likes — and if somebody later
    reaches for the private material, this fails."""
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(wall))
    # Only the SQL the ranking actually runs — docstrings describe the rule and
    # would match it, which would make this test pass on its own prose.
    sql = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("_signals",
                                                               "for_you"):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    if "SELECT" in sub.value or "FROM" in sub.value:
                        sql.append(sub.value)
    joined = " ".join(sql)
    assert joined, "found no queries to check"
    for forbidden in ("source_items", "memories", "pdi_key"):
        assert forbidden not in joined, (
            f"the ranking queries {forbidden!r} — the feed ranks on public "
            f"actions only")


def test_a_friends_post_outranks_a_strangers(client):
    pid = _handles(client)
    me, friend, stranger = pid("david_bianchi"), pid("marcus_bell"), pid("dr_amara_osei")
    wall.publish(stranger, "A stranger writes something.")
    wall.publish(friend, "A friend writes something.")
    friends.befriend(me, friend)

    feed = wall.for_you(me)
    assert feed[0]["profile_id"] == friend
    assert feed[0]["reason"] == "a friend posted this"


def test_every_entry_says_why_it_is_there(client):
    """A ranked feed that cannot explain itself is one nobody can audit,
    including whoever built it."""
    pid = _handles(client)
    me, other = pid("david_bianchi"), pid("dr_amara_osei")
    wall.publish(other, "Something.")
    for entry in wall.for_you(me):
        assert entry["reason"]


def test_the_feed_route_publishes_its_own_weights(client):
    """So the ranking can be argued with rather than merely accepted."""
    pid = _handles(client)
    me = pid("david_bianchi")
    r = client.get(f"/profiles/{me}/feed").json()
    assert r["weights"]["friend"] == wall.W_FRIEND
    assert "memories" in " ".join(r["never_ranked_on"])


def test_your_own_posts_are_not_in_your_feed(client):
    pid = _handles(client)
    me = pid("david_bianchi")
    wall.publish(me, "Talking to myself.")
    assert [p["profile_id"] for p in wall.for_you(me)] == []


def test_popularity_contributes_but_does_not_decide(client):
    """A capped signal. Uncapped, one heavily-liked stranger's post outranks
    every friend you have, which is the failure mode people complain about."""
    pid = _handles(client)
    me, friend, stranger = pid("david_bianchi"), pid("marcus_bell"), pid("dr_amara_osei")
    friends.befriend(me, friend)
    wall.publish(friend, "Quiet but yours.")
    loud = wall.publish(stranger, "Very popular.")
    for i in range(50):
        other = make_profile(client, display_name=f"Fan {i}")
        audience.like("post", loud["id"], other["id"])

    feed = wall.for_you(me)
    assert feed[0]["profile_id"] == friend


# -- content reaching people who did not ask for it -------------------------

def test_an_adult_profiles_post_is_walled_out_of_an_ordinary_feed(client):
    """A feed is the first surface where content arrives unrequested, so the
    gate is on the way out as well as the way in. Inherited from the author
    rather than judged per post — otherwise an adult profile publishes past its
    own wall by writing something innocuous."""
    pid = _handles(client)
    me = pid("david_bianchi")
    rated = pid("vivienne_sable")
    post = wall.publish(rated, "Backstage, before the curtain.")
    assert post["status"] == "approved"

    assert [p["id"] for p in wall.for_you(me)] == []
    assert post["id"] in [p["id"] for p in wall.for_you(me, adult_ok=True)]
    assert audience.is_rated("post", post["id"]) is True


# -- the three verbs, on a post ---------------------------------------------

def test_like_comment_and_share_all_work_on_a_post(client):
    """The whole reason `post` became an audience target rather than growing
    its own tables. Sharing was the one that did not: `share_url` had no
    pattern for a post and raised KeyError at the moment somebody shared it."""
    me = make_profile(client, display_name="Author")
    them = make_profile(client, display_name="Reader")
    post = client.post(f"/profiles/{me['id']}/wall", json={"body": "Look."},
                       headers=auth_header(me)).json()

    assert client.post(f"/posts/{post['id']}/like",
                       json={"actor_id": them["id"]}).status_code == 201
    assert client.post(f"/posts/{post['id']}/comments",
                       json={"actor_id": them["id"],
                             "body": "Nice one."}).status_code == 201
    r = client.post(f"/posts/{post['id']}/share",
                    json={"actor_id": them["id"], "channel": "link"})
    assert r.status_code == 201, r.text
    assert r.json()["url"] == f"/posts/{post['id']}"

    counts = client.get(f"/posts/{post['id']}/audience").json()
    assert counts["likes"] == 1 and counts["comments_count"] == 1
    assert counts["shares"] == 1


def test_every_target_kind_can_be_shared(client):
    """The guard for the bug above: a kind in TARGETS with no share URL is a
    KeyError waiting for the first person to press share."""
    for kind in audience.TARGETS:
        assert audience.share_url(kind, "x_1")
