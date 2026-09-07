"""The founder's description of a job is consulted beside its title.

The first real hire on the beta was an AI Specialist whose charter said
"Commercial content pictures and video for QRME". The title is an
imported row under Business, people & operations with no group, so the
seat took the family block: meeting minutes, process documentation,
stakeholder updating, diary and deadline management, record retention.
The description finds Video creator — a written row, with the phrases a
content job actually has — and the seat never asked it.

    asked     does the seat have skills
    mattered  are they this job's, or the family's

Three rules here. A written row found by the description leads a bare
title's skills and connections, and the seat says what it was read as. A
written title is left alone. And a row for adult work never outranks a
general one on a general question, because "pictures and video" was
answering with Adult content videographer first.
"""

import sys
from pathlib import Path

from qrme import company, occupations

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from occupation_groups import group_of  # noqa: E402

DESCRIBED = "Commercial content pictures and video for QRME"


def test_the_description_leads_a_bare_title():
    row = occupations.for_seat("AI Specialist", DESCRIBED)
    assert row["read_as"] == "Video creator"
    own = occupations.find("Video creator")["own_skills"]
    assert row["skills"][:len(own)] == own
    assert "meeting minutes" not in row["skills"][:6]
    assert row["family"] == "Business, people & operations", "the title is not re-filed"


def test_a_written_title_is_left_alone():
    plain = occupations.find("Video creator")
    row = occupations.for_seat("Video creator", "meeting minutes and diaries")
    assert row["skills"] == plain["skills"] and "read_as" not in row


def test_no_description_changes_nothing():
    a = occupations.for_seat("AI Specialist")
    b = occupations.find("AI Specialist")
    assert a["skills"] == b["skills"] and "read_as" not in a


def test_a_title_the_pool_never_heard_of_takes_the_description():
    assert not occupations.search("Zzyzx Quaggle", limit=1)
    row = occupations.for_seat("Zzyzx Quaggle", DESCRIBED)
    assert row and row["read_as"] == row["title"] == "Video creator"


def test_adult_work_never_leads_a_general_question():
    first = occupations.search("pictures and video", limit=1)[0]["title"]
    assert not first.lower().startswith("adult "), first
    asked = occupations.search("adult content videographer", limit=1)[0]["title"]
    assert asked == "Adult content videographer"


def test_the_charter_is_what_is_read():
    seat = {"charter": (
        '[{"question": "Full name of this employee:", "answer": "David Bianchi"},'
        ' {"question": "Describe the AI Specialist position in your own words:",'
        '  "answer": "Commercial content pictures and video for QRME"},'
        ' {"question": "Primary daily responsibilities and how often:",'
        '  "answer": "think study compose create draft"},'
        ' {"question": "Its handoff when unavailable:", "answer": "me"}]'),
            "interview": "[]"}
    said = company._described(seat)
    assert said == ["Commercial content pictures and video for QRME",
                    "think study compose create draft"]
    assert occupations.for_seat("AI Specialist", said)["read_as"] == "Video creator"


def test_ai_is_a_shape_of_work_and_air_cargo_is_not():
    assert group_of("AI Specialist") == "AI and machine learning"
    assert group_of("Data Scientist") == "AI and machine learning"
    assert group_of("Machine Learning Engineer") == "AI and machine learning"
    assert group_of("Air Cargo Specialist Supervisor") == "Supervision and management"
    assert group_of("AI Security Specialist") == "Security and policing"


def test_the_hire_route_reads_the_charter(client):
    """End to end, the way the beta did it: a seat called AI Specialist,
    an interview answered with what the job is for, Download knowledge
    with no model reachable — and the seat's skills are the content
    job's, not the family block's."""
    from tests.test_capabilities import auth_header, make_profile
    from tests.test_a_company_is_hired_one_interview_at_a_time import _found, _seat
    me = make_profile(client)
    co = _found(client, me, name="QRME", industry="ai synthetic profiles")
    seat = _seat(client, me, co, title="AI Specialist",
                 department="Business, people & operations")
    answers = [
        {"question": "Full name of this employee:", "answer": "David Bianchi"},
        {"question": "Describe the AI Specialist position in your own words:",
         "answer": DESCRIBED},
        {"question": "Primary daily responsibilities and how often:",
         "answer": "think study compose create draft"},
        {"question": "Preferred manner: voice, text, or both:", "answer": "both"},
    ]
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/hire",
                    json={"answers": answers}, headers=auth_header(me))
    assert r.status_code == 201, r.text
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/study",
                    json={}, headers=auth_header(me))
    assert r.status_code in (200, 201), r.text
    card = r.json()
    own = occupations.find("Video creator")["own_skills"]
    assert card["skills"][:len(own)] == own, card["skills"][:6]
    assert "meeting minutes" not in card["skills"][:6]
    assert card["known_as"] == "Video creator"
