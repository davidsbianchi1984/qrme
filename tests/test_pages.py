"""The homepage a person builds for themselves.

The MySpace idea, minus the part of MySpace that made it a security lesson.
The tests that matter are the ones holding that line: themes are a closed set,
colours are validated, a partial edit does not blank what it did not mention,
and the Top 8 cannot say something the friends graph does not.
"""

import pytest

from qrme import db, friends, pages, seed
from tests.test_capabilities import auth_header, make_profile


def _profile_with_friends(client, n=3):
    seed.seed()
    me = make_profile(client, display_name="Decorator")
    for i in range(n):
        other = make_profile(client, display_name=f"Pal {i}")
        client.post(f"/profiles/{me['id']}/friends",
                    json={"friend_id": other["id"]}, headers=auth_header(me))
    return me


# -- a page you did not make -------------------------------------------------

def test_an_untouched_profile_still_has_a_page(client):
    """A default rather than a blank. Somebody who never opens the editor
    still has a coherent page, and `customised` says which it is."""
    me = make_profile(client, display_name="Plain")
    page = client.get(f"/profiles/{me['id']}/page").json()
    assert page["customised"] is False
    assert page["theme"]["id"] == pages.DEFAULT_THEME
    assert page["layout"] == pages.DEFAULT_LAYOUT
    assert page["top_friends"] == []


def test_the_theme_catalog_is_offered_to_clients(client):
    r = client.get("/pages/themes").json()
    assert {t["id"] for t in r["themes"]} == set(pages.THEMES)
    assert r["top_friends"] == pages.TOP_FRIENDS


# -- the closed set ----------------------------------------------------------

def test_a_theme_outside_the_set_is_refused(client):
    """The whole point of a preset list. Raw markup is what made MySpace
    profiles a script-injection surface."""
    me = make_profile(client, display_name="Ambitious")
    r = client.put(f"/profiles/{me['id']}/page", json={"theme": "geocities"},
                   headers=auth_header(me))
    assert r.status_code == 422
    assert "unknown theme" in r.json()["detail"]


def test_an_accent_must_be_a_colour(client):
    me = make_profile(client, display_name="Creative")
    bad = client.put(f"/profiles/{me['id']}/page",
                     json={"accent": "javascript:alert(1)"},
                     headers=auth_header(me))
    assert bad.status_code == 422
    ok = client.put(f"/profiles/{me['id']}/page", json={"accent": "#d4a83a"},
                    headers=auth_header(me))
    assert ok.status_code == 200 and ok.json()["accent"] == "#d4a83a"


def test_only_the_owner_edits_the_page(client):
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    r = client.put(f"/profiles/{a['id']}/page", json={"tagline": "hi"},
                   headers=auth_header(b))
    assert r.status_code in (401, 403)


# -- an edit is an edit, not a reset ----------------------------------------

def test_a_partial_edit_leaves_the_other_fields_alone(client):
    """The mistake that turns an edit form into a delete button, and clients
    make it in exactly one direction."""
    me = make_profile(client, display_name="Careful")
    client.put(f"/profiles/{me['id']}/page",
               json={"theme": "sunset", "tagline": "Money jokes.",
                     "about": "Thirty years of it."},
               headers=auth_header(me))
    client.put(f"/profiles/{me['id']}/page", json={"theme": "chrome"},
               headers=auth_header(me))

    page = client.get(f"/profiles/{me['id']}/page").json()
    assert page["theme"]["id"] == "chrome"
    assert page["tagline"] == "Money jokes."
    assert page["about"] == "Thirty years of it."


# -- the Top 8 ---------------------------------------------------------------

def test_the_top_eight_keeps_the_owners_order(client):
    """The order is the whole point — it is what the owner thought was worth
    putting first, which is the thing a generated page cannot tell you."""
    me = _profile_with_friends(client)
    ids = [f["profile_id"] for f in friends.friends_of(me["id"])]
    chosen = list(reversed(ids[:3]))
    r = client.put(f"/profiles/{me['id']}/page", json={"top_friends": chosen},
                   headers=auth_header(me))
    assert r.status_code == 200, r.text
    assert [f["profile_id"] for f in r.json()["top_friends"]] == chosen


def test_the_top_eight_only_features_actual_friends(client):
    me = _profile_with_friends(client)
    stranger = make_profile(client, display_name="Stranger")
    r = client.put(f"/profiles/{me['id']}/page",
                   json={"top_friends": [stranger["id"]]},
                   headers=auth_header(me))
    assert r.status_code == 422
    assert "does not create them" in r.json()["detail"]


def test_the_top_eight_has_a_ceiling(client):
    me = _profile_with_friends(client, n=10)
    ids = [f["profile_id"] for f in friends.friends_of(me["id"])]
    r = client.put(f"/profiles/{me['id']}/page",
                   json={"top_friends": ids[:pages.TOP_FRIENDS + 1]},
                   headers=auth_header(me))
    assert r.status_code == 422


def test_the_same_friend_twice_is_refused(client):
    me = _profile_with_friends(client)
    fid = friends.friends_of(me["id"])[0]["profile_id"]
    r = client.put(f"/profiles/{me['id']}/page",
                   json={"top_friends": [fid, fid]}, headers=auth_header(me))
    assert r.status_code == 422


def test_a_top_friend_who_is_no_longer_a_friend_thins_out(client):
    """Rather than 404-ing the page it sits on."""
    me = _profile_with_friends(client)
    ids = [f["profile_id"] for f in friends.friends_of(me["id"])]
    ordinary = [i for i in ids if not friends.is_pinned(me["id"], i)]
    client.put(f"/profiles/{me['id']}/page", json={"top_friends": ordinary[:2]},
               headers=auth_header(me))
    client.delete(f"/profiles/{me['id']}/friends/{ordinary[0]}",
                  headers=auth_header(me))

    page = client.get(f"/profiles/{me['id']}/page").json()
    assert [f["profile_id"] for f in page["top_friends"]] == [ordinary[1]]


def test_the_top_eight_does_not_reorder_the_friends_list(client):
    """A showcase, not a second source of truth for the same fact. The founder
    pins stay where they are however the Top 8 is arranged."""
    me = _profile_with_friends(client)
    ids = [f["profile_id"] for f in friends.friends_of(me["id"])]
    ordinary = [i for i in ids if not friends.is_pinned(me["id"], i)]
    client.put(f"/profiles/{me['id']}/page", json={"top_friends": ordinary[:2]},
               headers=auth_header(me))

    after = client.get(f"/profiles/{me['id']}/friends").json()["friends"]
    assert after[0]["pinned"] is True and after[1]["pinned"] is True


# -- text other people read --------------------------------------------------

def test_about_text_is_moderated_like_anything_else_written_for_others(client):
    """A profile page is a surface other people read, so it goes through the
    same filter as a chat turn."""
    me = make_profile(client, display_name="Loud")
    r = client.put(f"/profiles/{me['id']}/page",
                   json={"about": "kill yourself"},
                   headers=auth_header(me))
    assert r.status_code == 200
    owner_view = r.json()
    assert owner_view["about_blocked"]

    # A visitor sees the page without it, rather than seeing it or seeing a
    # hole where a moderation notice would be.
    visitor = client.get(f"/profiles/{me['id']}/page").json()
    assert visitor["about"] is None
    assert visitor["about_blocked"] is None


def test_a_tagline_has_a_length(client):
    me = make_profile(client, display_name="Verbose")
    r = client.put(f"/profiles/{me['id']}/page",
                   json={"tagline": "x" * (pages.MAX_TAGLINE + 1)},
                   headers=auth_header(me))
    assert r.status_code == 422


def test_no_page_field_stores_markup_as_markup(client):
    """There is no field that takes HTML, and this is the test that says so.
    If somebody adds one, this fails and they have to argue with the module
    docstring rather than with nobody."""
    me = make_profile(client, display_name="Injector")
    payload = "<script>alert(1)</script>"
    client.put(f"/profiles/{me['id']}/page",
               json={"tagline": payload, "about": payload},
               headers=auth_header(me))
    row = db.connect().execute(
        "SELECT * FROM profile_pages WHERE profile_id=?",
        (me["id"],)).fetchone()
    # Stored verbatim as *text* — never interpreted, and the columns are a
    # fixed set rather than a markup blob. The guarantee is that no rendering
    # path treats any of them as markup.
    assert set(row.keys()) == {
        "profile_id", "theme", "accent", "layout", "tagline", "about",
        "about_status", "about_flag", "top_friends", "updated_at"}
