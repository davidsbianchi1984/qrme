"""Discover shows everyone who is here.

The screen rendered `GET /marketplace` — the opt-**in** listing a profile
enters only when somebody explicitly lists it. So a deployment holding 38
profiles showed 3 cards, and no privacy setting was involved: the other 35
had never been listed into a table the screen should not have been reading.

    asked     is this profile listed
    mattered  does this profile exist here

`GET /people/browse` is the pool, and it already carried the rule the product
means — every active, non-anonymous profile, with the owner's private switch
(`profiles.unlisted`, default 0) as the door out. Friends read it all along.
Nothing checked that Discover's surface agreed with it, which is how the two
could answer different questions about the same deployment for as long as
they did.

These hold the pool's own promise, at the door the screen actually calls:
a profile nobody listed is still here, and a profile whose owner went private
is not.
"""

from qrme import avatars, db, friends
from tests.test_capabilities import make_profile


def _pool_ids(client) -> set[str]:
    body = client.get("/people/browse").json()
    return {p["profile_id"] for p in body["found"]}


def _listed_ids(client) -> set[str]:
    return {c["profile_id"] for c in client.get("/marketplace").json()}


def test_a_profile_nobody_listed_is_still_here(client):
    """The whole of the reported defect, in one assertion: a profile that
    never entered the marketplace is in the pool the screen reads."""
    made = make_profile(client, display_name="Unlisted Newcomer")
    assert made["id"] not in _listed_ids(client), \
        "the fixture listed it — this test would prove nothing"
    assert made["id"] in _pool_ids(client)


def test_the_pool_is_not_the_marketplace(client):
    """They answer different questions, and the pool is the larger of the
    two. A screen that reads the smaller one shows a quiet deployment."""
    for n in range(3):
        make_profile(client, display_name=f"Person {n}")
    assert len(_pool_ids(client)) > len(_listed_ids(client))


def test_going_private_is_the_door_out(client):
    """`unlisted` is the only thing that removes somebody, which is what the
    product says and what the schema's default (0) means."""
    made = make_profile(client, display_name="Wants Privacy")
    assert made["id"] in _pool_ids(client)
    friends.set_listing(made["id"], False)
    assert made["id"] not in _pool_ids(client)
    friends.set_listing(made["id"], True)
    assert made["id"] in _pool_ids(client), "the door does not open again"


def test_the_head_count_counts_the_pool(client):
    """The number the screen prints is the pool's own, not the page length —
    three cards out of thirty-eight looked like a quiet deployment rather
    than a screen reading the wrong table."""
    before = client.get("/people/browse").json()["head_count"]
    make_profile(client, display_name="One More")
    after = client.get("/people/browse").json()
    assert after["head_count"] == before + 1
    assert after["head_count"] == len(after["found"])


def test_every_pool_row_says_which_kind_of_face_it_has(client):
    """The AI badge is not optional. A card built from a pool row has to be
    able to draw it, so the row carries the same server-decided answer the
    marketplace card does — no client re-derives it from an asset path."""
    make_profile(client, display_name="Has A Face")
    rows = client.get("/people/browse").json()["found"]
    assert rows
    for r in rows:
        assert "avatar_kind" in r
        assert r["avatar_kind"] in (None, "ai", "real_photo")
        # And it agrees with the picture the same row hands out. No badge
        # means the row is showing the empty frame, not a face — badging a
        # placeholder would be the same untruth as leaving a generated
        # portrait bare, in the other direction.
        if r["avatar_kind"] is None:
            assert r["avatar"] == avatars.ADD_PHOTO
        else:
            assert r["avatar"] != avatars.ADD_PHOTO
            if r["avatar_kind"] == "real_photo":
                assert r["avatar"].startswith(avatars.PHOTO_ROUTE)


def test_a_listed_profile_is_not_listed_twice(client):
    """Merging two sources must not double a profile that is in both."""
    ids = [p["profile_id"] for p in client.get("/people/browse").json()["found"]]
    assert len(ids) == len(set(ids))
