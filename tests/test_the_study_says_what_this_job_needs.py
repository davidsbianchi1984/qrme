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
        "connections": ["regulators", "families"],
        "tools": ["Google Calendar", "QuickBooks"]})
    said = _Says("Here you go:\n" + answer + "\nThat's all.")
    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: said)

    skills, connections, tools = companies.role_specifics(SEAT, STUDY)
    assert skills == ["staffing rota building", "inspection preparation",
                      "incident report writing"]
    assert connections == ["regulators", "families"]
    assert tools == ["Google Calendar", "QuickBooks"]
    # The study is what it read, not the title alone — a model asked only
    # for a job title is answering from memory, which is the thing the
    # study exists to replace.
    assert STUDY[:40] in said.asked[0]


def test_prose_around_the_json_does_not_lose_it(monkeypatch):
    """Models preface. The braces are found rather than assumed."""
    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: _Says(
        'Certainly. {"skills": ["visit log keeping"], '
        '"connections": ["district nurses"]} Let me know if…'))
    skills, connections, tools = companies.role_specifics(SEAT, STUDY)
    assert skills == ["visit log keeping"]
    assert connections == ["district nurses"]
    assert tools == []


def test_a_refusal_leaves_the_pools_answer_standing(monkeypatch):
    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: _Refuses())
    assert companies.role_specifics(SEAT, STUDY) == ([], [], [])


def test_a_shape_that_will_not_parse_is_not_an_error(monkeypatch):
    for text in ("no json here at all", "{not json}", "[1, 2, 3]",
                 '{"skills": "not a list"}'):
        monkeypatch.setattr(llm, "get_provider",
                            lambda cloud=None, t=text: _Says(t))
        assert companies.role_specifics(SEAT, STUDY) == ([], [], [])


def test_an_empty_study_is_never_sent(monkeypatch):
    """Offline, `study_role` returns the local fallback and there is
    nothing in it to read. Asking anyway spends a call to be told so."""
    said = _Says("{}")
    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: said)
    assert companies.role_specifics(SEAT, "   ") == ([], [], [])
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


# --- what the signature carries ---------------------------------------------

def _hire(client, me, co, seat, name):
    from tests.test_capabilities import auth_header
    return client.post(
        f"/companies/{co['id']}/seats/{seat['id']}/hire",
        json={"answers": [{"question": "Full name:", "answer": name},
                          {"question": "Duties:", "answer": "Does the job."},
                          {"question": "Authority:", "answer": "Escalates."}]},
        headers=auth_header(me))


def test_the_signature_carries_the_study_onto_the_person(client, monkeypatch):
    """The list was fetched, stored on the seat, and read by nobody.

    `hire` never touched `seat["connections"]`, and there was nowhere for
    it to go if it had: `routers/connections.py` is anonymous
    person-to-person chat and a referrer is not a profile. It lands three
    ways now, and all three are asserted here because each answers a
    different question — what the employee knows, who it is linked to,
    and what a screen can say about it.
    """
    from qrme import db, exchange
    from tests.test_capabilities import auth_header, make_profile
    from tests.test_a_company_is_hired_one_interview_at_a_time import (
        _found, _seat)

    monkeypatch.setattr(llm, "get_provider", lambda cloud=None: _Says(
        '{"skills": ["image report dictation"], "connections": '
        '["imaging technologists", "referrers", "Counter clerk"], '
        '"tools": ["Google Calendar", "the practice management system"]}'))
    me = make_profile(client)
    co = _found(client, me, name="Bianchi Imaging", industry="imaging")
    mate = _seat(client, me, co, title="Counter clerk", department="Front")
    _hire(client, me, co, mate, "June Okafor")

    seat = _seat(client, me, co, title="Radiologist", department="Imaging")
    body = client.post(f"/companies/{co['id']}/seats/{seat['id']}/study",
                       headers=auth_header(me)).json()
    # The trade's programs, split by whether this platform has a door.
    assert [t["label"] for t in body["tools"]] == ["Google Calendar"]
    assert body["tools_named"] == ["the practice management system"]

    pid = _hire(client, me, co, seat, "Amara Osei").json()["profile_id"]

    # 1. Stated, on the person it is about.
    prof = client.get(f"/profiles/{pid}").json()
    assert prof["works_with"][:3] == ["imaging technologists", "referrers",
                                      "Counter clerk"]
    # 2. Grounding: filed as source material, so replies know it.
    titles = [r["title"] for r in db.connect().execute(
        "SELECT title FROM source_items WHERE profile_id=?", (pid,))]
    assert "Who this job reaches: Radiologist" in titles
    # 3. The roster: a named connection that is also a colleague.
    assert "Colleagues the study named" in titles

    # And the trade it was hired into, which is what stops every
    # synthetic professional proposing work under "software".
    assert prof["trade_family"] == "Health care"
    assert prof["trade_domain"] == "healthcare"
    assert prof["trade_domain"] in exchange.INDUSTRIES


def test_a_hire_with_no_study_still_gets_its_trade(client, monkeypatch):
    """`hire` is reachable without a study — the console gates the
    signature on one, the route does not — and the pool still knows what
    a radiologist is."""
    from tests.test_capabilities import make_profile
    from tests.test_a_company_is_hired_one_interview_at_a_time import (
        _found, _seat)
    me = make_profile(client)
    co = _found(client, me, name="Bianchi Imaging", industry="imaging")
    seat = _seat(client, me, co, title="Radiologist", department="Imaging")
    pid = _hire(client, me, co, seat, "Amara Osei").json()["profile_id"]
    prof = client.get(f"/profiles/{pid}").json()
    assert prof["trade_domain"] == "healthcare"
    assert prof["works_with"] == []


def test_every_family_maps_to_a_real_industry():
    """The two vocabularies were written apart. A family that fell
    through the map would default to the first of the menu, which is the
    bug this map exists to end."""
    from qrme import exchange, occupations
    assert not set(occupations.families()) - set(exchange.FAMILY_INDUSTRY)
    assert not set(exchange.FAMILY_INDUSTRY.values()) - set(
        exchange.INDUSTRIES)
    assert exchange.industry_for(None) == "other"
    assert exchange.industry_for("Nonesuch") == "other"


def test_the_tool_matcher_scores_rather_than_guesses():
    """Both bugs the first version shipped with."""
    matched, missing = companies.match_tools(
        ["Google Calendar", "a computer", "the system", "QuickBooks",
         "the practice management system"])
    by = {m["because"]: f"{m['provider']}/{m['app']}" for m in matched}
    # Not Apple's Calendar: overlap is counted, not merely detected.
    assert by["Google Calendar"] == "google/calendar"
    assert by["QuickBooks"] == "work/quickbooks"
    # Category-only tools name nothing a founder could act on, either
    # way — neither offered nor reported as missing.
    assert "a computer" not in by and "a computer" not in missing
    assert "the system" not in by and "the system" not in missing
    # A real system with no connector is named rather than dropped.
    assert missing == ["the practice management system"]
