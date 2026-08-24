"""The owner's workshop, on the phones.

Six more blocks off the per-shell doorless record — workflows, the
delegation envelope, the assistant's verbs, autonomous tasks under a
revocable grant, rated placements, and domain specialists — and what
they share is that every one is *work the profile does when the owner
is not watching*. That is exactly the work an owner checks from the
device in their pocket: what ran, where it paused, who was allowed to
start it, and how to pull the plug.

The rules these screens render rather than invent:

* **A workflow pauses where the world has to answer.** Advance runs
  phases until one waits; resume carries the confirmation back in.
  They are different buttons because they are different acts.
* **Delegation is off until the owner declares it,** the offer is
  readable without a token and never names the grant, and delegating
  `research` without a grant is refused while the owner is looking.
* **A task's grant can die mid-run.** Mint, run, revoke — and a run
  under a revoked grant is a refusal, not a quiet no-op.
* **A rated placement takes an adult-mode profile only,** every ref it
  mints resolves through the age wall, and withdrawing it stops the
  beacon.
* **The specialists a profile consults are the owner's to attach.**
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402

from qrme import delegation
from tests.test_capabilities import auth_header, make_profile
from . import ratchets, shelltables

REPO = Path(__file__).resolve().parent.parent

ADULT = {"birthdate": "1984-06-01"}


def _seed(client, p):
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "life_event", "title": "the 1998 road trip",
        "content": "We drove the coast road and camped under the redwoods."},
        headers=auth_header(p))


def _person(client, name="Sam"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code == 201, r.text
    return r.json()


# -- the workflow -----------------------------------------------------------

def test_a_workflow_pauses_where_the_world_answers(client):
    p = make_profile(client)
    _seed(client, p)
    # Two yeses, and only one of them is the grant — see qrme/privileges.py.
    client.post(f"/profiles/{p['id']}/privileges/run_jobs", json={"on": True},
                headers=auth_header(p))
    grant = client.post(f"/profiles/{p['id']}/grants", json={},
                        headers=auth_header(p)).json()
    wf = client.post(f"/profiles/{p['id']}/workflows", json={
        "goal": "write a short travel note",
        "grant_token": grant["token"]}, headers=auth_header(p)).json()
    wid = wf["id"]
    assert wf["next_phase"] == "research"
    for _ in range(5):
        wf = client.post(f"/profiles/{p['id']}/workflows/{wid}/advance",
                         headers=auth_header(p)).json()
    # The confirm phase waits on the world; resume carries the answer in.
    assert wf["status"] == "awaiting_input"
    wf = client.post(f"/profiles/{p['id']}/workflows/{wid}/resume",
                     json={"input": "confirmed, send it"},
                     headers=auth_header(p)).json()
    assert wf["status"] == "completed"
    # The list is the owner's alone: a perfectly valid other-owner token
    # is the wrong account.
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/workflows",
                      headers=auth_header(q)).status_code == 403
    assert client.get(f"/profiles/{p['id']}/workflows",
                      headers=auth_header(p)).status_code == 200


# -- the delegation envelope ------------------------------------------------

def test_delegation_is_an_envelope_not_a_door(client):
    p = make_profile(client)
    # Off until declared, and the offer answers a bare GET.
    offer = client.get(f"/profiles/{p['id']}/delegation",
                       headers={"authorization": ""}).json()
    assert offer == {"delegation": False, "phases": [],
                     "delegable": list(delegation.DELEGABLE)}
    # Delegating research without a grant would hand a caller the whole
    # vault, so it is refused at write — where the owner can read why.
    r = client.put(f"/profiles/{p['id']}/delegation",
                   json={"phases": ["research", "draft"]},
                   headers=auth_header(p))
    assert r.status_code == 422 and "requires a grant" in r.json()["detail"]
    ok = client.put(f"/profiles/{p['id']}/delegation",
                    json={"phases": ["draft", "review"]},
                    headers=auth_header(p))
    assert ok.status_code == 200
    # A stranger holding the id is not "in conversation".
    sam = _person(client)
    r = client.post(f"/profiles/{p['id']}/delegated-workflows",
                    json={"goal": "a note", "interactor_id": sam["id"]},
                    headers={"authorization": f"Bearer {sam['token']}"})
    assert r.status_code == 403
    # One chat turn is what "in conversation" means.
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": sam["id"], "message": "hello"})
    wf = client.post(f"/profiles/{p['id']}/delegated-workflows",
                     json={"goal": "a note", "interactor_id": sam["id"]},
                     headers={"authorization": f"Bearer {sam['token']}"})
    assert wf.status_code == 201, wf.text
    wid = wf.json()["id"]
    seen = client.get(
        f"/profiles/{p['id']}/delegated-workflows/{wid}",
        headers={"authorization": f"Bearer {sam['token']}"}).json()
    assert seen["delegated_to"] == sam["id"]


# -- the assistant ----------------------------------------------------------

def test_the_assistants_verbs_answer_the_owner(client):
    p = make_profile(client)
    made = client.post(f"/profiles/{p['id']}/assist/compose",
                       json={"kind": "note", "moment": "the first snow"},
                       headers=auth_header(p))
    assert made.status_code == 201, made.text
    assert made.json()["content"]
    # A composed work is kept, and every render carries the mark.
    assert made.json()["watermark"]["watermark_id"]
    works = client.get(f"/profiles/{p['id']}/assist/works",
                       headers=auth_header(p)).json()
    assert any(w["moment"] == "the first snow" for w in works)
    out = client.post(f"/profiles/{p['id']}/assist/proofread",
                      json={"text": "i went  to the store"},
                      headers=auth_header(p)).json()
    assert "capitalize the pronoun 'I'" in out["suggestions"]
    ranked = client.post(f"/profiles/{p['id']}/assist/triage", json={
        "items": [{"id": "a", "text": "the roof is leaking badly"},
                  {"id": "b", "text": "newsletter"}],
        "keep": 1, "criteria": "the roof is leaking"},
        headers=auth_header(p)).json()
    assert [k["id"] for k in ranked["kept"]] == ["a"]
    assert ranked["discarded_ids"] == ["b"]


# -- the task and its grant -------------------------------------------------

def test_a_task_grant_dies_mid_air(client):
    p = make_profile(client)
    _seed(client, p)
    # Two yeses, and only one of them is the grant — see qrme/privileges.py.
    client.post(f"/profiles/{p['id']}/privileges/run_jobs", json={"on": True},
                headers=auth_header(p))
    grant = client.post(f"/profiles/{p['id']}/grants", json={},
                        headers=auth_header(p)).json()
    ran = client.post(f"/profiles/{p['id']}/tasks",
                      json={"topic": "the road trip",
                            "grant_token": grant["token"]},
                      headers=auth_header(p))
    assert ran.status_code == 201, ran.text
    # Revoked is refused, not quietly skipped.
    assert client.delete(f"/grants/{grant['id']}",
                         headers=auth_header(p)).status_code == 200
    refused = client.post(f"/profiles/{p['id']}/tasks",
                          json={"topic": "another",
                                "grant_token": grant["token"]},
                          headers=auth_header(p))
    assert refused.status_code == 403
    rows = client.get(f"/profiles/{p['id']}/tasks",
                      headers=auth_header(p)).json()
    assert len(rows) >= 1


# -- the placement ----------------------------------------------------------

def test_a_placement_is_adult_mode_only_and_withdrawable(client):
    venues = client.get("/venues", headers={"authorization": ""}).json()
    assert all(v["age_wall"] for v in venues)
    # A wholesome profile is not placed at an adult venue.
    plain = make_profile(client)
    r = client.post(f"/profiles/{plain['id']}/placements",
                    json={"venue": venues[0]["key"]},
                    headers=auth_header(plain))
    assert r.status_code == 422
    rated = client.post("/profiles", json={
        "plan": "pro", "owner_id": "owner-1", "kind": "fictional",
        "display_name": "Velvet Ivy", "adult_mode": True,
        "persona": "A cabaret hostess persona for adult audiences.",
        "maturity": "open", "verification": ADULT}).json()
    head = {"authorization": f"Bearer {rated['owner_token']}"}
    made = client.post(f"/profiles/{rated['id']}/placements",
                       json={"venue": "onlyfans", "label": "bio link"},
                       headers=head)
    assert made.status_code == 201, made.text
    assert made.json()["rated"] is True
    listed = client.get(f"/profiles/{rated['id']}/placements",
                        headers=head).json()
    assert listed and listed[0]["active"] is True
    funnel = client.get(f"/profiles/{rated['id']}/placements/analytics",
                        headers=head).json()["funnel"]
    assert funnel["resolutions"] == 0
    # Withdrawing stops the beacon; somebody else cannot.
    pid = made.json()["placement_id"]
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.delete(f"/placements/{pid}",
                         headers=auth_header(q)).status_code == 403
    gone = client.delete(f"/placements/{pid}", headers=head).json()
    assert gone["removed"] is True and gone["beacon_active"] is False


# -- the specialist ---------------------------------------------------------

def test_a_specialist_is_the_owners_to_attach(client):
    p = make_profile(client)
    doc = make_profile(client, owner_id="owner-1",
                       display_name="Dr. Rivera")
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.put(f"/profiles/{p['id']}/specialists",
                      json={"domain": "finance",
                            "specialist_profile_id": doc["id"]},
                      headers=auth_header(q)).status_code == 403
    ok = client.put(f"/profiles/{p['id']}/specialists",
                    json={"domain": "finance",
                          "specialist_profile_id": doc["id"]},
                    headers=auth_header(p))
    assert ok.status_code == 200, ok.text
    rows = client.get(f"/profiles/{p['id']}/specialists",
                      headers=auth_header(p)).json()
    assert rows == [{"domain": "finance",
                     "specialist_profile_id": doc["id"]}]


# -- the doors and their languages ------------------------------------------

def test_every_shell_has_doors_on_all_six_blocks(client):
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("GET", "/profiles/x/workflows") in made, \
            f"{lang.name}: the workflows are unreadable"
        assert ("PUT", "/profiles/x/delegation") in made, \
            f"{lang.name}: the envelope cannot be declared"
        assert ("POST", "/profiles/x/assist/compose") in made, \
            f"{lang.name}: the assistant is mute"
        assert ("POST", "/profiles/x/tasks") in made, \
            f"{lang.name}: no task door"
        assert ("GET", "/venues") in made, \
            f"{lang.name}: the venues are unreadable"
        assert ("PUT", "/profiles/x/specialists") in made, \
            f"{lang.name}: no specialist door"


def test_the_six_blocks_speak_ten_languages_on_every_shell(client):
    """Every work/dele/asst/task/plc/spec key the iOS table carries,
    complete on all three shells — the full-list rule, never a sample."""
    keys = shelltables.ios_keys("workshop")
    assert len(keys) >= ratchets.floor("l10n.block.workshop"), \
        f"the iOS table lost rows: {len(keys)}"
    problems = shelltables.missing_rows(keys)
    assert not problems, (
        f"{len(problems)} gap(s) in the shell tables:\n    "
        + "\n    ".join(problems[:12]))
