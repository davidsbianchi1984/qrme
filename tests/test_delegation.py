"""Owner-authorized workflow delegation: somebody other than the owner starting
a workflow, inside an envelope the owner declared.

The interesting assertions here are the refusals. A workflow reads vaulted
source material unattended, so the question this surface has to answer is not
"can a caller start one" but "what stops a caller starting one that reads
everything".
"""

from tests.test_capabilities import make_profile, pdi_pair  # noqa: F401


def _interactor(client, name="Sam"):
    """An interactor and its capability token. Clears the client's default
    owner header so the caller really is the interactor."""
    r = client.post("/interactors",
                    json={"display_name": name, "birthdate": "2000-01-15"})
    assert r.status_code == 201, r.text
    return r.json()


def _as(token):
    return {"authorization": f"Bearer {token}"}


def _relate(client, p, interactor_id):
    """One chat turn — which is what "already in conversation" means here.
    Note this does *not* create a `relationships` row: those are owner-set,
    and gating delegation on one would need an owner action per caller."""
    r = client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": interactor_id, "message": "hello"})
    assert r.status_code == 200, r.text


def _seed(client, p):
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "life_event", "title": "the 1998 road trip",
        "content": "We drove the coast road and camped under the redwoods."})


# -- the envelope ------------------------------------------------------------

def test_delegation_is_off_until_the_owner_turns_it_on(client):
    p = make_profile(client)
    it = _interactor(client)
    _relate(client, p, it["id"])

    offer = client.get(f"/profiles/{p['id']}/delegation").json()
    assert offer == {"delegation": False, "phases": []}

    r = client.post(f"/profiles/{p['id']}/delegated-workflows",
                    json={"goal": "anything", "interactor_id": it["id"]},
                    headers=_as(it["token"]))
    assert r.status_code == 403
    assert "does not accept delegated workflows" in r.json()["detail"]


def test_delegating_research_without_a_grant_is_refused_at_write(client):
    """The load-bearing refusal. `workflows._scoped_items` reads *every*
    source item when the grant is absent, so a policy that delegates research
    without one would hand a caller the whole vault."""
    p = make_profile(client)
    r = client.put(f"/profiles/{p['id']}/delegation",
                   json={"phases": ["research", "draft"]})
    assert r.status_code == 422
    assert "requires a grant" in r.json()["detail"]

    # Same policy with a grant is fine.
    grant = client.post(f"/profiles/{p['id']}/grants", json={}).json()
    ok = client.put(f"/profiles/{p['id']}/delegation",
                    json={"phases": ["research", "draft"],
                          "grant_token": grant["token"]})
    assert ok.status_code == 200
    assert ok.json()["phases"] == ["research", "draft"]


def test_a_policy_without_research_needs_no_grant(client):
    p = make_profile(client)
    r = client.put(f"/profiles/{p['id']}/delegation",
                   json={"phases": ["draft", "review"]})
    assert r.status_code == 200
    assert r.json()["grant_id"] is None


def test_the_offer_never_leaks_the_grant(client):
    p = make_profile(client)
    grant = client.post(f"/profiles/{p['id']}/grants", json={}).json()
    client.put(f"/profiles/{p['id']}/delegation",
               json={"phases": ["research"], "grant_token": grant["token"]})

    offer = client.get(f"/profiles/{p['id']}/delegation").json()
    assert offer == {"delegation": True, "phases": ["research"]}
    assert "grant_id" not in offer


def test_a_caller_cannot_widen_the_envelope(client):
    p = make_profile(client)
    it = _interactor(client)
    _relate(client, p, it["id"])
    client.put(f"/profiles/{p['id']}/delegation", json={"phases": ["draft"]})

    r = client.post(f"/profiles/{p['id']}/delegated-workflows",
                    json={"goal": "go further", "plan": ["draft", "send"],
                          "interactor_id": it["id"]},
                    headers=_as(it["token"]))
    assert r.status_code == 403
    assert "does not permit: send" in r.json()["detail"]


def test_omitting_the_plan_gets_the_policy_not_the_product_default(client):
    """A delegated caller that names no plan must not fall through to
    workflows.DEFAULT_PLAN, which is every phase there is."""
    p = make_profile(client)
    it = _interactor(client)
    _relate(client, p, it["id"])
    client.put(f"/profiles/{p['id']}/delegation", json={"phases": ["draft"]})

    wf = client.post(f"/profiles/{p['id']}/delegated-workflows",
                     json={"goal": "a short note", "interactor_id": it["id"]},
                     headers=_as(it["token"])).json()
    assert wf["plan"] == ["draft"]


def test_disabling_the_policy_stops_new_delegation(client):
    p = make_profile(client)
    it = _interactor(client)
    _relate(client, p, it["id"])
    client.put(f"/profiles/{p['id']}/delegation", json={"phases": ["draft"]})
    client.put(f"/profiles/{p['id']}/delegation",
               json={"phases": ["draft"], "enabled": False})

    r = client.post(f"/profiles/{p['id']}/delegated-workflows",
                    json={"goal": "x", "interactor_id": it["id"]},
                    headers=_as(it["token"]))
    assert r.status_code == 403


# -- who may ask -------------------------------------------------------------

def test_a_stranger_with_the_profile_id_is_refused(client):
    """Delegated work is for somebody already talking to the profile. Holding
    a valid interactor token and the profile's id is not enough."""
    p = make_profile(client)
    stranger = _interactor(client, "Stranger")
    client.put(f"/profiles/{p['id']}/delegation", json={"phases": ["draft"]})

    r = client.post(f"/profiles/{p['id']}/delegated-workflows",
                    json={"goal": "x", "interactor_id": stranger["id"]},
                    headers=_as(stranger["token"]))
    assert r.status_code == 403
    assert "not in conversation" in r.json()["detail"]


def test_one_interactor_cannot_start_work_as_another(client):
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    _relate(client, p, sam["id"])
    client.put(f"/profiles/{p['id']}/delegation", json={"phases": ["draft"]})

    # Mal presents their own token but names Sam as the interactor.
    r = client.post(f"/profiles/{p['id']}/delegated-workflows",
                    json={"goal": "x", "interactor_id": sam["id"]},
                    headers=_as(mal["token"]))
    assert r.status_code == 403


# -- the two surfaces never merge --------------------------------------------

def test_an_owners_workflow_is_invisible_to_the_delegated_routes(client):
    """The owner's own workflow has no delegated_workflows row, and that
    absence is the whole guard — it 404s here however the caller authenticates.
    """
    p = make_profile(client)
    owned = client.post(f"/profiles/{p['id']}/workflows",
                        json={"goal": "mine", "plan": ["draft"]}).json()

    # Even as the owner, it is not reachable through the delegated surface.
    r = client.get(f"/profiles/{p['id']}/delegated-workflows/{owned['id']}")
    assert r.status_code == 404


def test_another_interactor_cannot_read_a_delegated_workflow(client):
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    _relate(client, p, sam["id"])
    _relate(client, p, mal["id"])
    client.put(f"/profiles/{p['id']}/delegation", json={"phases": ["draft"]})

    wf = client.post(f"/profiles/{p['id']}/delegated-workflows",
                     json={"goal": "sam's work", "interactor_id": sam["id"]},
                     headers=_as(sam["token"])).json()

    r = client.get(f"/profiles/{p['id']}/delegated-workflows/{wf['id']}",
                   headers=_as(mal["token"]))
    assert r.status_code == 403


def test_the_owner_can_still_see_what_was_delegated(client):
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    _relate(client, p, sam["id"])
    client.put(f"/profiles/{p['id']}/delegation", json={"phases": ["draft"]})
    wf = client.post(f"/profiles/{p['id']}/delegated-workflows",
                     json={"goal": "sam's work", "interactor_id": sam["id"]},
                     headers=_as(sam["token"])).json()

    seen = client.get(f"/profiles/{p['id']}/delegated-workflows/{wf['id']}")
    assert seen.status_code == 200
    assert seen.json()["delegated_to"] == sam["id"]


# -- it actually runs --------------------------------------------------------

def test_a_delegated_workflow_advances_and_completes(client):
    p = make_profile(client)
    it = _interactor(client)
    _relate(client, p, it["id"])
    client.put(f"/profiles/{p['id']}/delegation",
               json={"phases": ["draft", "confirm"]})

    wf = client.post(f"/profiles/{p['id']}/delegated-workflows",
                     json={"goal": "draft a thank-you note",
                           "interactor_id": it["id"]},
                     headers=_as(it["token"])).json()
    wid = wf["id"]

    drafted = client.post(
        f"/profiles/{p['id']}/delegated-workflows/{wid}/advance",
        headers=_as(it["token"])).json()
    assert drafted["memory"]["draft"]
    assert drafted["next_phase"] == "confirm"

    paused = client.post(
        f"/profiles/{p['id']}/delegated-workflows/{wid}/advance",
        headers=_as(it["token"])).json()
    assert paused["status"] == "awaiting_input"

    done = client.post(
        f"/profiles/{p['id']}/delegated-workflows/{wid}/resume",
        json={"input": "recipient replied: thank you!"},
        headers=_as(it["token"])).json()
    assert done["status"] == "completed"


def test_delegated_research_reads_only_the_granted_scope(pdi_pair):
    """The grant the owner named scopes the delegated read — and revoking it
    halts the workflow, exactly as it does for the owner's own."""
    client, _ = pdi_pair
    p = make_profile(client)
    _seed(client, p)
    it = _interactor(client)
    _relate(client, p, it["id"])
    grant = client.post(f"/profiles/{p['id']}/grants", json={}).json()
    client.put(f"/profiles/{p['id']}/delegation",
               json={"phases": ["research"], "grant_token": grant["token"]})

    wf = client.post(f"/profiles/{p['id']}/delegated-workflows",
                     json={"goal": "summarize the trip",
                           "interactor_id": it["id"]},
                     headers=_as(it["token"])).json()
    assert client.delete(f"/grants/{grant['id']}").status_code == 200

    halted = client.post(
        f"/profiles/{p['id']}/delegated-workflows/{wf['id']}/advance",
        headers=_as(it["token"])).json()
    assert halted["status"] == "failed"
    assert "grant revoked" in halted["note"]
