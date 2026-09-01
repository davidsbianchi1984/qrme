"""The employee file: a hire is a full citizen of the world's rails.

    asked     embodiment straight from the company builder — the robot
              shelf of American models, screens to stand on, pairing —
              and a hand-out per profile: a code to input, a QR code,
              links, a file to download
    mattered  a synthetic employee reachable only inside one menu is an
              org chart, not a workforce; and the founder's key must
              never ride in anything that leaves the screen

No new doors were cut for any of this. The rails — embodiments, the
robotics catalogue, fixed displays, the export handoff — already stood,
and what these tests pin is the composition: a profile minted by an
interview is exactly as embodiable and exactly as portable as one minted
any other way.
"""

from __future__ import annotations

import json

from qrme import auth
from tests.test_a_company_is_hired_one_interview_at_a_time import (
    _found, _hire, _seat)
from tests.test_capabilities import auth_header, make_profile


def _hired_employee(client):
    """A founded company with one signed hire, and the employee's own
    owner key — the same capability the console mints through the
    account door when the founder opens the file."""
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    seat = _seat(client, me, co)
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/interview",
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    hired = _hire(client, me, co, seat)
    pid = hired["profile_id"]
    key = {"authorization": f"Bearer {auth.issue('owner', pid)}"}
    return co, pid, key


def test_the_hire_takes_a_body_from_the_shelf(client):
    """The catalogue's American models bind to a hired employee exactly
    as they bind to any profile: the binding lands as an embodiment, so
    identity consistency holds in the new body too."""
    co, pid, key = _hired_employee(client)
    shelf = client.get("/robotics/catalog").json()
    model = next(r for r in shelf["robots"] if r["bindable"])
    r = client.post(f"/profiles/{pid}/robots",
                    json={"model": model["model"]}, headers=key)
    assert r.status_code == 201, r.text
    forms = client.get(f"/profiles/{pid}/embodiments", headers=key).json()
    assert any(f["name"] == model["label"] for f in forms), (
        "the bound body did not land as an embodiment")


def test_an_announced_body_is_refused_by_name(client):
    """A machine its maker has shown but not shipped stays on the shelf
    un-bindable — named with its status rather than 404'd, because the
    catalogue lists it on purpose and every command to it would go
    nowhere."""
    co, pid, key = _hired_employee(client)
    shelf = client.get("/robotics/catalog").json()
    waiting = next((r for r in shelf["robots"] if not r["bindable"]), None)
    assert waiting is not None, "the catalogue no longer lists any announced model"
    r = client.post(f"/profiles/{pid}/robots",
                    json={"model": waiting["model"]}, headers=key)
    assert r.status_code == 409, r.text


def test_the_hire_stands_on_a_screen(client):
    """A fixed display placed from the builder is a real placement: the
    founder's listing shows it, and the public face answers — a fixture
    in a corridor displays to whoever walks past."""
    co, pid, key = _hired_employee(client)
    kind = client.get("/displays/vocabulary").json()["kinds"][0]["kind"]
    r = client.post(f"/profiles/{pid}/displays",
                    json={"kind": kind, "label": "Front counter panel"},
                    headers=key)
    assert r.status_code == 201, r.text
    display_id = r.json()["id"]
    mine = client.get(f"/profiles/{pid}/displays", headers=key).json()
    assert any(d["id"] == display_id for d in mine["displays"])
    shown = client.get(f"/displays/{display_id}")
    assert shown.status_code == 200, shown.text


def test_the_handoff_is_a_ticket_and_never_the_key(client):
    """The hand-out per profile: the minted ticket carries a QR path, a
    URL and a code to type — none of which contain the owner key — the
    handoff read delivers the position the employee was hired into, and
    the second read finds the ticket already dead."""
    co, pid, key = _hired_employee(client)
    r = client.post(f"/profiles/{pid}/export/ticket", headers=key)
    assert r.status_code == 201, r.text
    ticket = r.json()
    assert ticket["single_use"] is True
    assert ticket["qr_svg"].endswith("/qr.svg")
    owner_key = key["authorization"].split()[-1]
    assert owner_key not in json.dumps(ticket), (
        "the founder's key rode in the handoff")

    handed = client.get(ticket["url"])
    assert handed.status_code == 200, handed.text
    titles = [row["title"] for row in handed.json()["source_rows"]]
    assert any(t.startswith("The position:") for t in titles), (
        "the handoff arrived without the job the employee was hired into")

    again = client.get(ticket["url"])
    assert again.status_code == 410, (
        "a single-use handoff answered twice")


def test_a_stranger_holds_none_of_the_employees_doors(client):
    """Somebody else's owner key opens neither the embodiment list nor
    the hand-out — holding *an* owner key is not holding *this*
    employee's."""
    co, pid, key = _hired_employee(client)
    other = make_profile(client, owner_id="owner-2",
                         display_name="Somebody Else")
    stranger = auth_header(other)
    assert client.get(f"/profiles/{pid}/embodiments",
                      headers=stranger).status_code == 403
    assert client.post(f"/profiles/{pid}/export/ticket",
                       headers=stranger).status_code == 403
