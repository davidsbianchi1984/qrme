"""The Company Builder: found, draft, interview, hire, oversee.

    asked     start a digital company and fill positions with synthetic
              profiles trained for each — any industry, any title,
              controlled individually under the company folder
    mattered  the interview IS the training, and the founder's account
              IS the oversight

These tests drive the doors in the order a founder walks them. The
model-drafted interview is exercised in its honest degraded form — the
test box configures no provider, so the role-blind core comes back,
which is itself the guarantee under test: a founder without a model
still hires, and nothing pretends otherwise.
"""

from __future__ import annotations

from qrme import company as companies
from tests.test_capabilities import auth_header, make_profile


def _found(client, me, name="Bianchi & Daughters", industry="bakery",
           headcount=3):
    r = client.post("/companies",
                    json={"name": name, "industry": industry,
                          "headcount": headcount},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    return r.json()


def _seat(client, me, co, title="Counter clerk", department="Front of house"):
    r = client.post(f"/companies/{co['id']}/seats",
                    json={"title": title, "department": department},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    return r.json()


def _hire(client, me, co, seat, name="June Okafor"):
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/hire",
                    json={"answers": [
                        {"question": "Full name:", "answer": name},
                        {"question": "Duties:",
                         "answer": "Take orders, box pastries, ring up "
                                   "sales, keep the case stocked."},
                        {"question": "Decides alone vs escalates:",
                         "answer": "Decides substitutions; escalates "
                                   "refunds to the manager."},
                    ]},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    return r.json()


def test_a_company_is_founded_with_a_size_and_no_list(client):
    """Industry is the founder's word — 'any industry' is a schema fact,
    not a menu."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me, industry="alpaca shearing")
    assert co["industry"] == "alpaca shearing"
    assert co["org_id"], "a company without an organization cannot coordinate"


def test_the_folder_is_the_account_boundary(client):
    """Somebody else's company answers 404 — knowing the id is not being
    here, the identity-router pattern this codebase already keeps."""
    me = make_profile(client, display_name="Founder")
    # A different ACCOUNT, not merely a different profile — the folder
    # boundary under test is the account's, and two profiles on one
    # account are the same founder wearing two faces.
    stranger = make_profile(client, owner_id="owner-2",
                            display_name="Stranger")
    co = _found(client, me)
    r = client.get(f"/companies/{co['id']}", headers=auth_header(stranger))
    assert r.status_code == 404


def test_the_interview_arrives_even_with_no_model(client):
    """The degraded interview admits what it is: the role-blind core,
    with the name first and the authority question present — a founder
    without a model still hires."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    seat = _seat(client, me, co)
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/interview",
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    qs = r.json()["questions"]
    assert len(qs) >= 3
    assert "name" in qs[0]["question"].lower()
    assert any("escalat" in q["question"].lower() for q in qs)


def test_the_signature_is_the_hire(client):
    """A signed interview becomes: a profile the founder's account owns,
    a persona carrying the charter, the charter filed as source
    material, and the seat marked filled."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    seat = _seat(client, me, co)
    hired = _hire(client, me, co, seat)
    assert hired["display_name"] == "June Okafor"

    roster = client.get(f"/companies/{co['id']}",
                        headers=auth_header(me)).json()
    filled = [s for s in roster["seats"] if s["id"] == seat["id"]][0]
    assert filled["status"] == "hired"
    assert filled["profile_id"] == hired["profile_id"]
    assert filled["charter"][0]["answer"] == "June Okafor"

    from qrme import db
    conn = db.connect()
    prof = conn.execute("SELECT * FROM profiles WHERE id=?",
                        (hired["profile_id"],)).fetchone()
    assert prof is not None and prof["owner_id"] == me["owner_id"], (
        "an employee outside the founder's account is outside the "
        "founder's oversight")
    assert "Counter clerk" in prof["persona"]
    src = conn.execute(
        "SELECT title FROM source_items WHERE profile_id=?",
        (hired["profile_id"],)).fetchall()
    assert any("The position:" in s["title"] for s in src), (
        "the charter is not filed where replies can ground on it")


def test_colleagues_know_each_other(client):
    """The second hire is connected to the first — a company whose
    employees are strangers to each other is an org chart, not a staff."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    first = _hire(client, me, co, _seat(client, me, co), name="June Okafor")
    second = _hire(client, me, co,
                   _seat(client, me, co, title="Baker", department="Kitchen"),
                   name="Sal Romero")
    from qrme import db
    conn = db.connect()
    linked = conn.execute(
        "SELECT COUNT(*) FROM friendships WHERE (profile_id=? AND"
        " friend_id=?) OR (profile_id=? AND friend_id=?)",
        (second["profile_id"], first["profile_id"],
         first["profile_id"], second["profile_id"])).fetchone()[0]
    assert linked >= 1


def test_the_headcount_is_a_wall_not_a_wish(client):
    me = make_profile(client, display_name="Founder")
    co = _found(client, me, headcount=1)
    _seat(client, me, co)
    r = client.post(f"/companies/{co['id']}/seats",
                    json={"title": "Second", "department": "Anything"},
                    headers=auth_header(me))
    assert r.status_code == 422
    assert "founded for 1" in r.json()["detail"]


def test_retiring_a_seat_keeps_the_person(client):
    """A staffing decision, not a deletion — the profile stays under
    every owner door that already exists."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    seat = _seat(client, me, co)
    hired = _hire(client, me, co, seat)
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/retire",
                    headers=auth_header(me))
    assert r.status_code == 200
    from qrme import db
    conn = db.connect()
    assert conn.execute("SELECT 1 FROM profiles WHERE id=?",
                        (hired["profile_id"],)).fetchone() is not None


def test_an_interview_too_thin_to_train_is_refused(client):
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    seat = _seat(client, me, co)
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/hire",
                    json={"answers": [
                        {"question": "Full name:", "answer": "June"},
                        {"question": "Duties:", "answer": "Stuff"},
                        {"question": "x", "answer": " "},
                    ]},
                    headers=auth_header(me))
    assert r.status_code == 422


def test_the_charter_says_what_may_not_be_performed(client):
    """The doctrine, written into every persona: licensed and physical
    duties are assisted, never performed — a fact about the product, in
    the employee's own job description."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    hired = _hire(client, me, co, _seat(client, me, co))
    from qrme import db
    conn = db.connect()
    persona = conn.execute("SELECT persona FROM profiles WHERE id=?",
                          (hired["profile_id"],)).fetchone()["persona"]
    assert "assisted, never performed" in persona
