"""A profile's front page: skills, experience, reviews, and the rating.

Three claims carry it, and each is a way the page could have become a lie:

* **A review comes from somebody who was actually there.** A rating anyone can
  post is worth exactly the number of accounts somebody can make.
* **Experience on a real person is a credential**, so it needs the same rights
  basis the persona needed. On a fictional profile the invented history is the
  point.
* **Nothing on the page outranks the AI mark.** Five stars does not make a
  synthetic profile a person.
"""

import pytest

from qrme import db, frontpage


def _profile(client, **over):
    body = {"owner_id": "owner-1", "kind": "fictional",
            "display_name": "Marcus Bell",
            "persona": "A retired fee-only financial planner who spent thirty "
                       "years helping ordinary families budget and retire.",
            "purpose": "enterprise_agent",
            "verification": {"birthdate": "1980-01-01"}}
    body.update(over)
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _interactor(client, name="Visitor"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code == 201, r.text
    return r.json()


def _auth(tok):
    return {"authorization": f"Bearer {tok}"}


def _talk(profile_id, interactor_id, n=1):
    """Put a real interaction on the engagement row."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO engagement (profile_id, interactor_id, interactions)"
        " VALUES (?,?,?) ON CONFLICT (profile_id, interactor_id)"
        " DO UPDATE SET interactions=excluded.interactions",
        (profile_id, interactor_id, n))
    conn.commit()


# --- the page -------------------------------------------------------------

def test_the_front_page_carries_the_ai_mark_with_everything_else(client):
    p = _profile(client)
    page = client.get(f"/profiles/{p['id']}/front").json()

    assert page["display_name"] == "Marcus Bell"
    assert page["ai_disclosure"]                # never optional
    assert page["headline"] == "retired fee-only financial planner"
    assert page["rating_summary"]["count"] == 0
    assert "no reviews yet" in page["rating_summary"]["note"]


def test_the_headline_comes_from_the_persona_not_a_second_field(client):
    """A separate headline field is a second copy that starts agreeing with
    the persona and stops."""
    p = _profile(client, persona="A climate scientist who translates "
                                 "atmospheric physics for a town.")
    page = client.get(f"/profiles/{p['id']}/front").json()
    assert page["headline"] == "climate scientist"


# --- reviews --------------------------------------------------------------

def test_a_review_needs_having_actually_talked_to_it(client):
    p, v = _profile(client), _interactor(client)
    r = client.post(f"/profiles/{p['id']}/reviews",
                    json={"interactor_id": v["id"], "rating": 5,
                          "body": "great"}, headers=_auth(v["token"]))
    assert r.status_code == 422
    assert "actually talked to" in r.json()["detail"]

    _talk(p["id"], v["id"])
    ok = client.post(f"/profiles/{p['id']}/reviews",
                     json={"interactor_id": v["id"], "rating": 5,
                           "body": "great"}, headers=_auth(v["token"]))
    assert ok.status_code == 201


def test_one_review_per_person_edited_rather_than_stacked(client):
    """Enforced by the schema, not by a check somebody could forget."""
    p, v = _profile(client), _interactor(client)
    _talk(p["id"], v["id"])
    for score in (5, 5, 1):
        client.post(f"/profiles/{p['id']}/reviews",
                    json={"interactor_id": v["id"], "rating": score},
                    headers=_auth(v["token"]))

    agg = frontpage.rating(p["id"])
    assert agg["count"] == 1                    # not three
    assert agg["average"] == 1.0                # the latest one
    assert frontpage.reviews(p["id"])[0]["edited"] is True


def test_the_average_reports_how_many_it_is_an_average_of(client):
    """One five-star review and two hundred are different facts."""
    p = _profile(client)
    for i, score in enumerate((5, 4, 3)):
        v = _interactor(client, f"V{i}")
        _talk(p["id"], v["id"])
        client.post(f"/profiles/{p['id']}/reviews",
                    json={"interactor_id": v["id"], "rating": score},
                    headers=_auth(v["token"]))

    agg = client.get(f"/profiles/{p['id']}/reviews").json()["rating_summary"]
    assert agg["count"] == 3
    assert agg["average"] == 4.0
    assert agg["distribution"]["5"] == 1


def test_a_rating_outside_the_scale_is_refused(client):
    p, v = _profile(client), _interactor(client)
    _talk(p["id"], v["id"])
    for bad in (0, 6, 99):
        r = client.post(f"/profiles/{p['id']}/reviews",
                        json={"interactor_id": v["id"], "rating": bad},
                        headers=_auth(v["token"]))
        assert r.status_code == 422


def test_another_account_cannot_post_a_review_as_you(client):
    p = _profile(client)
    mine, theirs = _interactor(client, "Mine"), _interactor(client, "Theirs")
    _talk(p["id"], mine["id"])
    r = client.post(f"/profiles/{p['id']}/reviews",
                    json={"interactor_id": mine["id"], "rating": 1},
                    headers=_auth(theirs["token"]))
    assert r.status_code in (401, 403)


# --- experience -----------------------------------------------------------

def test_a_fictional_profile_may_invent_its_history(client):
    p = _profile(client)
    r = client.put(f"/profiles/{p['id']}/experience", json={"entries": [
        {"title": "Fee-only financial planner", "org": "Bell & Co",
         "period": "1994–2024"}]}, headers=_auth(p["owner_token"]))
    assert r.status_code == 200
    assert r.json()["experience"][0]["org"] == "Bell & Co"


def test_experience_about_a_real_person_needs_a_rights_basis(client):
    """On a fictional profile invented history is the point. On one that
    depicts somebody real it is a credential asserted on their behalf."""
    p = _profile(client, kind="self", display_name="A Real Person")
    r = client.put(f"/profiles/{p['id']}/experience", json={"entries": [
        {"title": "Chief Surgeon", "org": "Mass General"}]},
        headers=_auth(p["owner_token"]))
    assert r.status_code == 422
    assert "rights basis" in r.json()["detail"]
    assert frontpage.experience(p["id"]) == []


def test_experience_is_replaced_not_appended(client):
    p = _profile(client)
    put = lambda e: client.put(f"/profiles/{p['id']}/experience",
                               json={"entries": e},
                               headers=_auth(p["owner_token"]))
    put([{"title": "One"}, {"title": "Two"}])
    out = put([{"title": "Only"}]).json()["experience"]
    assert [e["title"] for e in out] == ["Only"]


def test_a_front_page_will_not_carry_a_database_dump(client):
    p = _profile(client)
    r = client.put(f"/profiles/{p['id']}/experience",
                   json={"entries": [{"title": f"Role {i}"} for i in range(20)]},
                   headers=_auth(p["owner_token"]))
    assert r.status_code == 422
    assert "at most" in r.json()["detail"]


def test_a_stranger_cannot_write_the_experience(client):
    p, v = _profile(client), _interactor(client)
    r = client.put(f"/profiles/{p['id']}/experience",
                   json={"entries": [{"title": "Hacked"}]},
                   headers=_auth(v["token"]))
    assert r.status_code in (401, 403)
    assert frontpage.experience(p["id"]) == []
