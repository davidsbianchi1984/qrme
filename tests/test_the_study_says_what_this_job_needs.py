"""The study's findings become the seat's own skills and connections.

    asked     skills and connections tailored to every profile, for what
              they need for their particular job
    mattered  516 of 45,153 rows carry skills of their own; the other
              44,637 inherit their family's, so a browse of the whole
              table read as sixteen jobs repeated

The carried pool is exhaustive in titles and coarse in detail — the
bargain that keeps it at 4.2 MB. The study is the opposite: it is about
one job, it is fetched, and until now it was stored as prose and thrown
away as data. `study_seat` took the structured half off the pool while
a paragraph naming this job's actual work sat in the same function.

`role_specifics` reads that paragraph. What it finds leads; the pool's
answer, true of the family, fills in behind. Four things have to hold:

1. **The specific leads.** A founder reading six generic skills learns
   nothing the word "health care" would not have told them.
2. **Nothing is said twice.** The study and the pool overlap by
   construction — they are describing the same job.
3. **A failure leaves the pool's answer standing.** No model, a refusal,
   a shape that will not parse: each of those is the screen as it was
   before this existed, not an error over a study that did arrive.
4. **No entry is an act.** The charter every hire signs ends "duties
   that are licensed or physical acts are assisted, never performed".
   The prompt says so; this asserts the plumbing that would carry a
   violation is at least bounded and readable.
"""

from __future__ import annotations

import json

from qrme import company as companies, llm


class _Says:
    """A provider that answers with whatever it was handed."""

    def __init__(self, text: str):
        self.text = text
        self.asked: list[str] = []

    def generate(self, system, messages):
        self.asked.append(messages[-1]["content"])
        return self.text


class _Refuses:
    def generate(self, system, messages):
        raise RuntimeError("no model answered this request")


SEAT = {"title": "Care home manager", "department": "Care"}
STUDY = ("A care home manager builds the staffing rota, prepares for "
         "inspection, keeps case notes, and reports to the regulator.")


def test_the_specifics_come_out_of_the_study(monkeypatch):
    answer = json.dumps({
        "skills": ["staffing rota building", "inspection preparation",
                   "incident report writing"],
        "connections": ["regulators", "families"]})
    said = _Says("Here you go:\n" + answer + "\nThat's all.")
    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: said)

    skills, connections = companies.role_specifics(SEAT, STUDY)
    assert skills == ["staffing rota building", "inspection preparation",
                      "incident report writing"]
    assert connections == ["regulators", "families"]
    # The study is what it read, not the title alone — a model asked only
    # for a job title is answering from memory, which is the thing the
    # study exists to replace.
    assert STUDY[:40] in said.asked[0]


def test_prose_around_the_json_does_not_lose_it(monkeypatch):
    """Models preface. The braces are found rather than assumed."""
    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: _Says(
        'Certainly. {"skills": ["visit log keeping"], '
        '"connections": ["district nurses"]} Let me know if…'))
    skills, connections = companies.role_specifics(SEAT, STUDY)
    assert skills == ["visit log keeping"]
    assert connections == ["district nurses"]


def test_a_refusal_leaves_the_pools_answer_standing(monkeypatch):
    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: _Refuses())
    assert companies.role_specifics(SEAT, STUDY) == ([], [])


def test_a_shape_that_will_not_parse_is_not_an_error(monkeypatch):
    for text in ("no json here at all", "{not json}", "[1, 2, 3]",
                 '{"skills": "not a list"}'):
        monkeypatch.setattr(llm, "get_provider",
                            lambda cloud=None, t=text: _Says(t))
        assert companies.role_specifics(SEAT, STUDY) == ([], [])


def test_an_empty_study_is_never_sent(monkeypatch):
    """Offline, `study_role` returns the local fallback and there is
    nothing in it to read. Asking anyway spends a call to be told so."""
    said = _Says("{}")
    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: said)
    assert companies.role_specifics(SEAT, "   ") == ([], [])
    assert not said.asked, "a blank study was sent to be parsed"


def test_the_list_is_read_carefully():
    """Sentences, duplicates and repeated spacing are read, not thrown."""
    got = companies._tidy(
        ["Visit log keeping.", "visit log keeping", "VISIT LOG KEEPING",
         "", "   ", "Medication  prompt   recording", "x" * 70,
         "consent capture"], 8)
    assert got == ["Visit log keeping", "Medication prompt recording",
                   "consent capture"]


def test_the_cap_holds():
    assert len(companies._tidy([f"skill {i}" for i in range(40)], 8)) == 8


def test_this_jobs_own_lead_and_nothing_is_said_twice():
    got = companies._lead_with(
        ["visit log keeping", "wellbeing check reporting"],
        ["Visit log keeping", "case note writing", "risk flagging"])
    assert got == ["visit log keeping", "wellbeing check reporting",
                   "case note writing", "risk flagging"]
    # Case-blind, because the study writes lowercase and the pool does
    # not, and the same skill under two capitalisations is one skill.
    assert "Visit log keeping" not in got


def test_the_seat_carries_what_the_study_found(client, monkeypatch):
    """End to end through the door the console presses."""
    from tests.test_capabilities import auth_header, make_profile
    from tests.test_a_company_is_hired_one_interview_at_a_time import (
        _found, _seat)

    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: _Says(
        '{"skills": ["staffing rota building", "inspection preparation"], '
        '"connections": ["regulators", "families"]}'))
    me = make_profile(client)
    co = _found(client, me, name="Bianchi Home Care", industry="home care")
    seat = _seat(client, me, co, title="Care home manager",
                 department="Care")

    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/study",
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["skills"][:2] == ["staffing rota building",
                                  "inspection preparation"]
    assert body["connections"][:2] == ["regulators", "families"]
    # And the count, so a card of generic skills can say which it is.
    assert body["tailored"] == 4
    # The family's are still behind them — the study narrows, it does
    # not replace what the pool knows about the trade.
    assert len(body["skills"]) > 2
