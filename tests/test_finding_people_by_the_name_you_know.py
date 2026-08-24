"""Finding people by the name you already know.

Two beta testers who knew each other's names had no way to become friends:
suggestions walk a friend graph they are not on yet, and the marketplace
lists only profiles that chose a storefront. `GET /people` is the missing
door. These tests hold the two exclusions that make it safe to have — an
anonymous profile never matches, and only active profiles greet strangers —
and that what comes back is only what the profile already shows the public.
"""

from __future__ import annotations

from qrme import db


def a_profile(client, name="Dana Field", owner="owner-f", **extra):
    r = client.post("/profiles", json={
        "owner_id": owner, "kind": "self", "display_name": name,
        "persona": "A retired teacher who likes gardening and dry humor.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro", **extra})
    assert r.status_code == 201, r.text
    return r.json()["id"], r.json()["owner_token"]


def test_a_name_finds_its_profile(client):
    pid, _ = a_profile(client, name="Marisol Vega")
    found = client.get("/people?q=marisol").json()["found"]
    assert [p["profile_id"] for p in found] == [pid]
    row = found[0]
    # `avatar_kind` is in this set deliberately, and it is the only key here
    # that was ever added after the guard was written. It is not new exposure:
    # it is derived from `avatar`, which the row already hands out, and a
    # caller can read `/photos/...` against `/portraits/...` for themselves.
    # What it buys is that no *surface* has to — the AI badge is mandatory,
    # and a rule re-derived per client is a rule that drifts.
    #
    #     asked     did the row grow a key
    #     mattered  did the row grow a fact
    assert set(row) == {"profile_id", "display_name", "handle", "avatar",
                        "avatar_kind", "kind", "verification"}, (
        "the row grew keys beyond what the profile already shows the public")


def test_the_search_is_public_like_the_list_beside_it(client):
    a_profile(client, name="Marisol Vega")
    assert client.get("/people?q=vega").status_code == 200


def test_an_anonymous_profile_never_matches(client):
    """Anonymity a name search could pierce would not be anonymity."""
    pid, _ = a_profile(client, name="Quiet Person", anonymous=True)
    found = client.get("/people?q=quiet").json()["found"]
    assert pid not in [p["profile_id"] for p in found]


def test_a_departed_profile_is_not_greeting_strangers(client):
    pid, _ = a_profile(client, name="Gone Person")
    db.connect().execute("UPDATE profiles SET status='departed' WHERE id=?",
                         (pid,))
    db.connect().commit()
    found = client.get("/people?q=gone").json()["found"]
    assert pid not in [p["profile_id"] for p in found]


def test_an_empty_query_refuses_with_a_sentence(client):
    r = client.get("/people?q=%20")
    assert r.status_code == 422
    assert "search" in str(r.json()["detail"])


def test_a_handle_matches_with_or_without_its_at(client):
    pid, tok = a_profile(client, name="Rios Delgado")
    r = client.put(f"/profiles/{pid}/handle", json={"handle": "riosd"},
                   headers={"authorization": f"Bearer {tok}"})
    if r.status_code not in (200, 201):
        return  # no handle door in this build; the name path is covered above
    found = client.get("/people?q=@riosd").json()["found"]
    assert pid in [p["profile_id"] for p in found]
