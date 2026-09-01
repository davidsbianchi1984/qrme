"""The study, the staffing plan, and bring-your-own: 2.9.11's three doors.

    asked     the platform researches the occupation, its skills, the
              connections and the knowledge of its profession; predicts
              what a fully functioning storefront needs; and takes the
              founder's own or blended profiles into seats
    mattered  an interview written from model memory is a guess about a
              job, a founder should not need to already know what
              fully-functioning means, and a seat is not only for the
              newly minted

On the test box no cloud is configured, so `research.gather` answers
through the local deterministic provider — which is itself the guarantee
under test: the study never silently fails, it degrades on the record.
"""

from __future__ import annotations

from tests.test_a_company_is_hired_one_interview_at_a_time import (
    _found, _hire, _seat)
from tests.test_capabilities import auth_header, make_profile


def test_the_trade_rides_the_hire(client):
    """The study is filed beside the job description, so the employee
    arrives knowing its profession and every reply can ground on it."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    seat = _seat(client, me, co)
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/interview",
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    hired = _hire(client, me, co, seat)

    from qrme import db
    conn = db.connect()
    titles = [s["title"] for s in conn.execute(
        "SELECT title FROM source_items WHERE profile_id=?",
        (hired["profile_id"],))]
    assert any(t.startswith("The trade:") for t in titles), (
        "the profession's knowledge did not ride the hire")


def test_the_plan_predicts_a_fully_functioning_roster(client):
    """Suggestions with a title, a department and a why — at most the
    headcount, and never zero: the honest floor stands when the model's
    answer does not parse."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me, headcount=3)
    r = client.post(f"/companies/{co['id']}/plan",
                    json={"description": "a neighborhood bakery with a "
                                         "counter and morning rush"},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    rows = r.json()["suggestions"]
    assert 1 <= len(rows) <= 3
    for row in rows:
        assert row["title"] and row["department"] and "why" in row


def test_the_plan_opens_no_seat_by_itself(client):
    """Suggestions, never walls — and never deeds. Nothing is staffed
    without the founder's own press."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    client.post(f"/companies/{co['id']}/plan", json={},
                headers=auth_header(me))
    roster = client.get(f"/companies/{co['id']}",
                        headers=auth_header(me)).json()
    assert roster["seats"] == []


def test_a_brought_profile_takes_the_seat(client):
    """Bring your own hire: the founder's existing profile fills the
    seat, colleagues connect, and the record says brought."""
    me = make_profile(client, display_name="Founder")
    mine = make_profile(client, display_name="My Specialist")
    co = _found(client, me)
    first = _hire(client, me, co, _seat(client, me, co))
    seat = _seat(client, me, co, title="Consultant", department="Advisory")
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/assign",
                    json={"profile_id": mine["id"]},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    assert r.json()["brought"] is True

    from qrme import db
    conn = db.connect()
    linked = conn.execute(
        "SELECT COUNT(*) FROM friendships WHERE (profile_id=? AND"
        " friend_id=?) OR (profile_id=? AND friend_id=?)",
        (mine["id"], first["profile_id"],
         first["profile_id"], mine["id"])).fetchone()[0]
    assert linked >= 1, "a brought colleague is still a stranger"


def test_a_strangers_profile_cannot_be_seated(client):
    """The organization's own staffing rule, kept at this door too."""
    me = make_profile(client, display_name="Founder")
    theirs = make_profile(client, owner_id="owner-2",
                          display_name="Not Yours")
    co = _found(client, me)
    seat = _seat(client, me, co)
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/assign",
                    json={"profile_id": theirs["id"]},
                    headers=auth_header(me))
    assert r.status_code == 422
    assert "founder holds" in r.json()["detail"]
