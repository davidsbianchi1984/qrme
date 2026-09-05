"""Browse the positions, download what the job needs, then sign.

    asked     does the platform know the trade
    mattered  does the *founder* get to see what it knows, before
              signing somebody into the job

`study_role` has gone online and stored a study of the trade since the
Builder shipped — and it ran inside `draft_interview`, silently. So the
knowledge existed, grounded the questions, and was never once shown to
the person doing the hiring. A founder pressed one button, got an
interview, and signed against an understanding they had no way to read.

Two doors close that. `/occupations` is the pool made browsable, so a
founder can go and look at what the app carries instead of typing into
the dark. `/study` is the download made a step: press it, read what came
back, change what is wrong, and only then sign.
"""

from __future__ import annotations

from qrme import company as companies, occupations
from tests.test_capabilities import auth_header, make_profile
from tests.test_a_company_is_hired_one_interview_at_a_time import (
    _found, _seat)


def test_the_pool_is_browsable_from_a_door(client):
    me = make_profile(client)
    r = client.get("/occupations", params={"q": "bakes bread"},
                   headers=auth_header(me))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["positions"], "the search bar answers nothing"
    assert body["positions"][0]["title"] == "Baker"
    assert body["positions"][0]["skills"], (
        "a browsed position arrives with no skills, so a founder is "
        "picking a title and being told nothing about the work")
    assert body["total"] > 40000


def test_an_empty_query_is_a_browse_not_an_error(client):
    """The list must never be blank while somebody is deciding what to
    type — that is the moment the old three canned seats filled."""
    me = make_profile(client)
    r = client.get("/occupations", headers=auth_header(me))
    assert r.status_code == 200
    assert r.json()["positions"]


def test_a_family_narrows_the_walk(client):
    me = make_profile(client)
    fams = client.get("/occupations/families",
                      headers=auth_header(me)).json()["families"]
    assert len(fams) == 16
    r = client.get("/occupations",
                   params={"family": "Health care", "limit": 20},
                   headers=auth_header(me))
    assert r.status_code == 200
    got = r.json()["positions"]
    assert got and all(p["family"] == "Health care" for p in got)


def test_browsing_needs_an_owner(client):
    """The pool is a founder's tool and sits behind the same door the
    rest of the Builder does."""
    assert client.get("/occupations").status_code == 401


def test_the_study_hands_back_what_the_seat_must_know(client):
    me = make_profile(client)
    co = _found(client, me)
    seat = _seat(client, me, co, title="Baker", department="Kitchen")
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/study",
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["found"] is True
    assert body["skills"], "the download returned no skills"
    assert body["connections"], "the download returned no connections"
    assert body["knowledge"], "the download returned no working knowledge"


def test_a_title_the_pool_never_heard_of_still_studies(client):
    """Typing your own is exactly as good as picking one. An unknown
    title is not an error and not a lesser seat — it starts from an
    empty list rather than a filled one."""
    me = make_profile(client)
    co = _found(client, me)
    seat = _seat(client, me, co, title="Chief vibes officer",
                 department="Whatever")
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/study",
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    assert r.json()["knowledge"], "an unknown title got no study at all"


def test_what_the_study_found_is_kept_on_the_seat(client):
    """Stored, not just returned: that is what makes the hire offline
    from then on."""
    me = make_profile(client)
    co = _found(client, me)
    seat = _seat(client, me, co, title="Baker", department="Kitchen")
    client.post(f"/companies/{co['id']}/seats/{seat['id']}/study",
                headers=auth_header(me))
    kept = [s for s in companies.seats(co["id"]) if s["id"] == seat["id"]][0]
    assert kept["skills"], "the seat forgot what the study downloaded"
    assert kept["connections"]
    assert kept["study"], "the working knowledge did not reach the seat"


def test_the_founder_can_change_what_the_study_found(client):
    """Review means being able to edit it. A skill this business does
    not want comes off; one the pool never thought of goes on."""
    me = make_profile(client)
    co = _found(client, me)
    seat = _seat(client, me, co, title="Baker", department="Kitchen")
    client.post(f"/companies/{co['id']}/seats/{seat['id']}/study",
                headers=auth_header(me))
    r = client.post(
        f"/companies/{co['id']}/seats/{seat['id']}/study/keep",
        json={"skills": ["dough scheduling", "allergen labelling"],
              "connections": ["the mill", "environmental health"]},
        headers=auth_header(me))
    assert r.status_code == 200, r.text
    kept = [s for s in companies.seats(co["id"]) if s["id"] == seat["id"]][0]
    assert kept["skills"] == ["dough scheduling", "allergen labelling"]
    assert kept["connections"] == ["the mill", "environmental health"]


def test_another_account_cannot_study_your_seat(client):
    """The company's folder boundary is an account boundary, and these
    two doors are inside it like every other."""
    me = make_profile(client)
    co = _found(client, me)
    seat = _seat(client, me, co)
    # A different *account*, not just a different profile: a company's
    # folder boundary is an account boundary, and `make_profile` puts
    # everything under owner-1 unless told otherwise.
    stranger = make_profile(client, owner_id="owner-2",
                            display_name="Someone else")
    for path in ("study", "study/keep"):
        r = client.post(
            f"/companies/{co['id']}/seats/{seat['id']}/{path}",
            json={"skills": [], "connections": []},
            headers=auth_header(stranger))
        assert r.status_code == 404, (path, r.status_code)


def test_the_signature_waits_for_the_study():
    """Structural, on the console's own source: the sign button is
    disabled until the study for that seat is on screen.

    A behavioural test would need a JavaScript runtime the console CI
    job does not have, and the shape is what matters here — a seat
    signed before anybody read what the job needs is the whole thing
    this step exists to stop.
    """
    from pathlib import Path
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            root = parent
            break
    screen = (root / "app/src/screens/Companies.tsx").read_text(
        encoding="utf-8")
    assert 'disabled={busy || study?.seatId !== s.id}' in screen, (
        "the sign button no longer waits for the study")
    assert "api.studySeat(" in screen, "no door presses the download"
    assert "api.browseOccupations(" in screen, "no door opens the pool"
