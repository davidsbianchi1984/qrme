"""A roster of what the agent may do, and nobody said yes by arriving.

The product grew powers faster than it grew a place to see them. A profile
could go and study the open web, put a question to strangers, package a history
for a professional, run a job over vaulted material and reach emergency
services, and the only way to find out was to read a changelog or to meet one
mid-conversation.

    asked     can the agent do this
    mattered  did the person decide it could, knowing what it costs

## What these guards hold

* every row is off until somebody turns it on, unless a written reason says
  otherwise — and nothing that reaches people who did not choose it may carry
  one;
* the refusal names the *thing*, translated, rather than the row's identifier;
* the check sits at each power's own last hop, not in the route above it, so a
  second caller cannot walk past it;
* a visitor can read the roster — what an agent may do on somebody's behalf is
  not a secret kept from the person it would be done to;
* every row names a power this product actually has, wired to the code that
  exercises it. A row for something unbuilt is a person saying yes to nothing.
"""

import inspect

import pytest

from qrme import privileges


def _roster(client, profile_id, **kwargs):
    r = client.get(f"/profiles/{profile_id}/privileges", **kwargs)
    assert r.status_code == 200, r.text
    return {row["name"]: row for row in r.json()}


def _turn_on(client, profile_id, name, on=True):
    r = client.post(f"/profiles/{profile_id}/privileges/{name}",
                    json={"on": on})
    assert r.status_code == 200, r.text
    return r.json()


# --------------------------------------------------------------------------
# The rule that is enforced rather than intended.
# --------------------------------------------------------------------------

def test_nothing_that_reaches_other_people_is_on_by_default():
    """The one guard this module exists for.

    Convenience defaults are how a product ends up briefing a stranger, or
    dialling one, on behalf of somebody who never said it could. The argument
    for one always sounds reasonable at the time, so it is refused here rather
    than argued about there.
    """
    assert privileges._defaults_are_honest() == []


def test_a_row_that_keeps_something_says_why_it_may_default_on():
    """`study_the_web` is on, and is allowed to be — the sanitiser strips the
    owner's terms and the visits ledger records where it went. What makes that
    acceptable is that the reason is written down and travels with the row."""
    for row in privileges.PRIVILEGES.values():
        if row.default:
            assert row.why, f"{row.name} defaults on and says nothing about it"
            assert not row.touches_others


def test_every_row_names_a_power_this_product_actually_has():
    """A roster row with nothing behind it is a dead control: the person says
    yes, and yes does nothing. Structural, because the temptation is to add the
    row in the round that plans the feature rather than the one that builds
    it."""
    from qrme import briefing, escalation, inquiries, research, tasks
    wired = "".join(inspect.getsource(m) for m in
                    (research, inquiries, briefing, tasks, escalation))
    for name in privileges.PRIVILEGES:
        assert f'"{name}"' in wired, (
            f"{name} is on the roster and no code asks for it — a person can "
            "turn it on and nothing changes")


# --------------------------------------------------------------------------
# The roster itself.
# --------------------------------------------------------------------------

def test_the_roster_shows_what_is_off_and_what_each_one_keeps(client,
                                                              profile_id):
    """A roster that hides what has not been chosen is a roster nobody can
    choose from, and *what it keeps* is the half these lists usually omit."""
    rows = _roster(client, profile_id)
    assert set(rows) == set(privileges.PRIVILEGES)
    assert rows["reach_emergency_services"]["chosen"] is False
    assert rows["study_the_web"]["chosen"] is True
    assert rows["run_jobs"]["holds"], "a row that keeps something says so"
    assert rows["brief_a_professional"]["touches_others"] is True


def test_a_visitor_can_read_what_this_profile_is_able_to_do(client,
                                                            profile_id):
    """The half of the round that is not a settings screen: somebody deciding
    whether to bring a matter here can look, instead of finding out when the
    profile happens to offer it."""
    del client.headers["authorization"]
    rows = _roster(client, profile_id)
    assert rows["brief_a_professional"]["may_do"]


def test_only_the_owner_may_change_one(client, profile_id):
    del client.headers["authorization"]
    r = client.post(f"/profiles/{profile_id}/privileges/run_jobs",
                    json={"on": True})
    assert r.status_code in (401, 403), r.text


def test_choosing_returns_the_whole_roster(client, profile_id):
    """Not the row. A client that re-reads one row shows a screen that agrees
    with itself about that row and nothing else."""
    out = _turn_on(client, profile_id, "run_jobs")
    assert {row["name"] for row in out} == set(privileges.PRIVILEGES)
    assert [r for r in out if r["name"] == "run_jobs"][0]["chosen"] is True


def test_a_decision_that_agrees_with_the_default_is_still_written_down(
        client, profile_id):
    """*Never asked* and *considered and left alone* are different states, and
    the second is the one that survives a default changing under it."""
    from qrme import db
    _turn_on(client, profile_id, "study_the_web", on=True)
    row = db.connect().execute(
        "SELECT chosen FROM chosen_privileges WHERE profile_id=?"
        " AND privilege='study_the_web'", (profile_id,)).fetchone()
    assert row is not None and row["chosen"] == 1


def test_turning_one_off_that_was_on_by_default_holds(client, profile_id):
    _turn_on(client, profile_id, "study_the_web", on=False)
    assert privileges.chosen(profile_id, "study_the_web") is False


def test_an_invented_privilege_is_refused_by_name(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/privileges/watch_my_screen",
                    json={"on": True})
    assert r.status_code == 422, r.text
    assert "run_jobs" in r.text, "the refusal says what there is instead"


# --------------------------------------------------------------------------
# The chokepoint.
# --------------------------------------------------------------------------

def test_the_press_is_refused_when_the_owner_never_allowed_it(
        client, profile_id, interactor_id, interactor_head):
    """Two people have to have agreed: the owner, who put the power on the
    roster, and the person pressing, who signed the waiver. Neither yes stands
    in for the other."""
    from qrme import db, escalation, signatures
    conn = db.connect()
    conn.execute(
        "INSERT OR REPLACE INTO dial_waivers (interactor_id, signature_id,"
        " waiver, waiver_sha256, signed_at) VALUES (?,?,?,?,?)",
        (interactor_id, "sig_test", escalation.WAIVER,
         signatures.sha256_hex(escalation.WAIVER), db.utcnow()))
    conn.commit()

    raised = client.post(f"/profiles/{profile_id}/unresolved",
                         json={"interactor_id": interactor_id,
                               "matter": "the boiler is leaking gas"},
                         headers=interactor_head)
    assert raised.status_code == 201, raised.text
    r = client.post(f"/escalations/{raised.json()['id']}/dial",
                    params={"interactor_id": interactor_id},
                    headers=interactor_head)
    assert r.status_code == 403, r.text
    assert "emergency services" in r.text


def test_a_job_needs_the_privilege_as_well_as_the_grant(client, profile_id):
    """A grant says *what may be read*. The privilege says *whether this agent
    works unattended at all* — and a revoked grant was never an answer to the
    second."""
    grant = client.post(f"/profiles/{profile_id}/grants",
                        json={"scope": ["*"], "purpose": "a test"})
    assert grant.status_code == 201, grant.text
    token = grant.json()["token"]

    refused = client.post(f"/profiles/{profile_id}/tasks",
                          json={"kind": "summarize", "topic": "the garden",
                                "grant_token": token})
    assert refused.status_code == 403, refused.text

    _turn_on(client, profile_id, "run_jobs")
    allowed = client.post(f"/profiles/{profile_id}/tasks",
                          json={"kind": "summarize", "topic": "the garden",
                                "grant_token": token})
    assert allowed.status_code == 201, allowed.text


def test_asking_strangers_needs_the_privilege(client, profile_id):
    body = {"topic": "old plumbing", "question": "who still repairs these"}
    refused = client.post(f"/profiles/{profile_id}/inquiries", json=body)
    assert refused.status_code == 403, refused.text

    _turn_on(client, profile_id, "ask_people")
    assert client.post(f"/profiles/{profile_id}/inquiries",
                       json=body).status_code == 201


def test_the_check_is_at_the_last_hop_not_in_the_route(client, profile_id):
    """A refusal that lived in the router is a refusal a second caller walks
    past. The excursion's check moved out of `routers/research.py` and into
    `research.excursion` for exactly that reason."""
    from qrme import research
    from qrme.routers import research as routes
    assert "privileges.require" in inspect.getsource(research.excursion)
    assert "privileges.require" not in inspect.getsource(routes)


def test_turning_it_off_stops_a_power_that_had_been_used(client, profile_id):
    """The direction that matters more than granting. A person who changes
    their mind gets the power back off, not a setting that only reads."""
    body = {"topic": "old plumbing", "question": "who still repairs these"}
    _turn_on(client, profile_id, "ask_people")
    assert client.post(f"/profiles/{profile_id}/inquiries",
                       json=body).status_code == 201
    _turn_on(client, profile_id, "ask_people", on=False)
    assert client.post(f"/profiles/{profile_id}/inquiries",
                       json=body).status_code == 403


def test_the_refusal_arrives_in_the_readers_language(client, profile_id):
    """`str(exc)` on a `Templated` returns a plain `str`, which forgets the
    template — the refusal then reads as English in every language, silently.
    The escalation router did that to the sealed-dialer sentence, which is the
    one a person reads while something is going wrong."""
    from qrme import i18n
    # The owner's stored preference, not the header: an owner who chose
    # Portuguese gets Portuguese even from a client that sent nothing.
    i18n.set_language(profile_id, "pt")
    r = client.post(f"/profiles/{profile_id}/inquiries",
                    json={"topic": "t", "question": "q"})
    assert r.status_code == 403, r.text
    said = r.json()["message"]
    assert "permission" not in said, said
    assert "desconhecidos" in said, "the thing itself is translated too"


def test_the_refusal_names_the_thing_rather_than_the_row(client, profile_id):
    """`run_jobs` is an identifier. *Turn it on* is only actionable if the
    person can tell which power the sentence is about."""
    with pytest.raises(privileges.NotChosen) as caught:
        privileges.require(profile_id, "run_jobs")
    said = str(caught.value)
    assert "run_jobs" not in said
    assert "multi-step job" in said
