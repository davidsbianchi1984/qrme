"""Open for business: the company enters the marketplace inside the app.

    asked     users can enter their business into the digital
              marketplace QRME offers
    mattered  the storefront is the shop rail that already exists — one
              set of rules about listings, orders and money — so a
              company in the marketplace is a shop like every other,
              with a staff behind it
"""

from __future__ import annotations

from tests.test_a_company_is_hired_one_interview_at_a_time import (
    _found, _hire, _seat)
from tests.test_capabilities import auth_header, make_profile


def _publish(client, me, co, tagline=None):
    return client.post(f"/companies/{co['id']}/publish",
                       json={"tagline": tagline},
                       headers=auth_header(me))


def test_nobody_hired_means_no_storefront(client):
    """A storefront with nobody behind the counter is a sign, not a
    business."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    _seat(client, me, co)
    r = _publish(client, me, co)
    assert r.status_code == 422
    assert "nobody hired" in r.json()["detail"]


def test_the_storefront_is_a_shop_like_every_other(client):
    """Published, the company appears on the same rail every shop uses —
    named for the company, tagged with its industry, one service
    offering per staffed department saying who answers."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    _hire(client, me, co, _seat(client, me, co), name="June Okafor")
    _hire(client, me, co,
          _seat(client, me, co, title="Baker", department="Kitchen"),
          name="Sal Romero")
    r = _publish(client, me, co, tagline="Bread the old way")
    assert r.status_code == 201, r.text
    shop = r.json()
    assert shop["name"] == co["name"]
    titles = {o["title"] for o in shop["offerings"]}
    assert titles == {"Front of house", "Kitchen"}
    blurbs = " ".join(o["blurb"] or "" for o in shop["offerings"])
    assert "June Okafor" in blurbs and "Sal Romero" in blurbs

    listed = client.get("/shops").json()
    assert any(s["id"] == shop["id"] for s in listed), (
        "the storefront is not on the rail people browse")


def test_unpublishing_takes_the_sign_down_not_the_company(client):
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    _hire(client, me, co, _seat(client, me, co))
    shop = _publish(client, me, co).json()
    r = client.post(f"/companies/{co['id']}/unpublish",
                    headers=auth_header(me))
    assert r.status_code == 200
    listed = client.get("/shops").json()
    assert not any(s["id"] == shop["id"] for s in listed), (
        "a closed storefront is still on the rail")
    roster = client.get(f"/companies/{co['id']}",
                        headers=auth_header(me)).json()
    assert any(s["status"] == "hired" for s in roster["seats"]), (
        "unpublishing dissolved the staff")


def test_publishing_twice_is_an_edit(client):
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    _hire(client, me, co, _seat(client, me, co))
    first = _publish(client, me, co).json()
    again = _publish(client, me, co, tagline="Under new light").json()
    assert again["id"] == first["id"], (
        "republishing minted a second storefront")


def test_a_strangers_publish_is_a_404(client):
    me = make_profile(client, display_name="Founder")
    stranger = make_profile(client, owner_id="owner-2",
                            display_name="Stranger")
    co = _found(client, me)
    r = client.post(f"/companies/{co['id']}/publish", json={},
                    headers=auth_header(stranger))
    assert r.status_code == 404
