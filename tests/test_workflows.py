"""Autonomous multi-step workflows (claim 25, extended): a plan of phases run
one at a time, carrying working memory forward, pausing for external
confirmation, and honoring a revocable grant."""

from tests.test_capabilities import make_profile, pdi_pair  # noqa: F401


def _seed(client, p):
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "life_event", "title": "the 1998 road trip",
        "content": "We drove the coast road and camped under the redwoods."})


def test_full_workflow_runs_to_completion_with_carryover(client):
    p = make_profile(client)
    _seed(client, p)
    grant = client.post(f"/profiles/{p['id']}/grants", json={}).json()

    wf = client.post(f"/profiles/{p['id']}/workflows", json={
        "goal": "write a short travel note about the road trip",
        "grant_token": grant["token"]}).json()
    assert wf["status"] == "running"
    assert wf["plan"] == ["research", "draft", "review", "send", "confirm"]
    assert wf["next_phase"] == "research"
    wid = wf["id"]

    # research → draft → review → send: four advances, memory accumulates.
    for expected_next in ("draft", "review", "send", "confirm"):
        wf = client.post(
            f"/profiles/{p['id']}/workflows/{wid}/advance").json()
        assert wf["next_phase"] == expected_next
    # Working memory carried every completed phase forward.
    assert set(wf["memory"]) == {"research", "draft", "review", "send"}
    assert all(wf["memory"].values())

    # The confirm phase pauses for the outside world.
    wf = client.post(f"/profiles/{p['id']}/workflows/{wid}/advance").json()
    assert wf["status"] == "awaiting_input"
    assert "confirmation" in wf["awaiting"]

    # Advancing again while paused does nothing (must resume).
    still = client.post(f"/profiles/{p['id']}/workflows/{wid}/advance").json()
    assert still["status"] == "awaiting_input"


def test_confirm_resumes_and_completes(client):
    p = make_profile(client)
    wf = client.post(f"/profiles/{p['id']}/workflows", json={
        "goal": "draft a thank-you", "plan": ["draft", "confirm"]}).json()
    wid = wf["id"]
    client.post(f"/profiles/{p['id']}/workflows/{wid}/advance")   # draft
    paused = client.post(
        f"/profiles/{p['id']}/workflows/{wid}/advance").json()    # confirm
    assert paused["status"] == "awaiting_input"

    # Resume — as if in a later session — supplies the confirmation.
    done = client.post(f"/profiles/{p['id']}/workflows/{wid}/resume",
                       json={"input": "recipient replied: thank you!"}).json()
    assert done["status"] == "completed"
    assert done["next_phase"] is None
    assert "confirmed" in done["memory"]["confirm"]

    # Resuming a completed workflow is a conflict.
    assert client.post(f"/profiles/{p['id']}/workflows/{wid}/resume",
                       json={"input": "again"}).status_code == 409


def test_revoking_the_grant_halts_the_next_read_phase(pdi_pair):
    client, _ = pdi_pair
    p = make_profile(client)
    _seed(client, p)
    grant = client.post(f"/profiles/{p['id']}/grants", json={}).json()
    wf = client.post(f"/profiles/{p['id']}/workflows", json={
        "goal": "summarize the trip", "grant_token": grant["token"]}).json()
    wid = wf["id"]

    # Revoke before the research phase runs.
    assert client.delete(f"/grants/{grant['id']}").status_code == 200
    halted = client.post(
        f"/profiles/{p['id']}/workflows/{wid}/advance").json()
    assert halted["status"] == "failed"


def test_unknown_phase_is_rejected(client):
    p = make_profile(client)
    r = client.post(f"/profiles/{p['id']}/workflows", json={
        "goal": "x", "plan": ["research", "teleport"]})
    assert r.status_code == 422
    assert "teleport" in r.json()["detail"]


def test_cancel_stops_a_running_workflow(client):
    p = make_profile(client)
    wf = client.post(f"/profiles/{p['id']}/workflows", json={
        "goal": "x", "plan": ["draft", "send", "confirm"]}).json()
    wid = wf["id"]
    client.post(f"/profiles/{p['id']}/workflows/{wid}/advance")   # draft
    cancelled = client.post(
        f"/profiles/{p['id']}/workflows/{wid}/cancel").json()
    assert cancelled["status"] == "cancelled"
    # A cancelled workflow will not advance.
    after = client.post(
        f"/profiles/{p['id']}/workflows/{wid}/advance").json()
    assert after["status"] == "cancelled"
