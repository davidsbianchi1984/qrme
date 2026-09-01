"""The agent status light: green, amber, red.

One question, answered at a glance: **does this agent need me right now?**
Green no, amber yes, red it stopped. The tests that matter are the ones that
stop the light from lying — an unknown state must not render as a confident
green, and the light must not become a stored field that can disagree with the
status it claims to describe.
"""

import pytest

from qrme import agentlight, db
from tests.test_capabilities import make_profile


def _workflow(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/workflows",
                    json={"goal": "summarise the quarter", "plan": ["draft"]})
    assert r.status_code == 201, r.text
    return r.json()


# -- the mapping -------------------------------------------------------------

def test_every_status_the_workflow_writes_has_a_light():
    """The mapping is keyed on what `workflows.py` actually stores. If a status
    is added there and not here, this fails rather than the screen guessing."""
    import re
    # From the repo root by way of this file, not the invoker's cwd — a
    # battery launched from anywhere reads the same source.
    import pathlib
    src = (pathlib.Path(__file__).resolve().parents[1]
           / "qrme" / "workflows.py").read_text()
    written = set(re.findall(r'status="([a-z_]+)"', src))
    written |= {"running"}                     # the literal in the INSERT
    written |= set(re.findall(r'status = "([a-z_]+)"', src))
    missing = written - set(agentlight.LIGHTS)
    assert not missing, f"statuses with no light: {sorted(missing)}"


def test_an_unknown_status_raises_rather_than_defaulting():
    """The one failure this module must not have. A default would paint an
    unrecognised state green, and green is the colour that means 'ignore me'."""
    with pytest.raises(agentlight.UnknownStatus) as exc:
        agentlight.light("paused")
    assert "paused" in str(exc.value)


def test_only_amber_asks_for_a_person():
    """Red is stopped, not stopped-and-waiting. Conflating them would put a
    call to action on the one state where there is nothing to do."""
    assert agentlight.light("awaiting_input")["needs_you"] is True
    for status in ("running", "completed", "failed", "cancelled"):
        assert agentlight.light(status)["needs_you"] is False


def test_completed_is_green_but_says_done():
    """A finished workflow is not working, so the colour alone would mislead —
    which is why every reading carries a word as well."""
    d = agentlight.light("completed")
    assert d["light"] == "green" and d["label"] == "done"
    assert agentlight.light("running")["label"] == "working"


def test_there_are_exactly_three_colours():
    """Three is what a person reads without learning a key. Every scheme that
    grew a fourth grew a fifth."""
    assert set(agentlight.ORDER) == {"green", "amber", "red"}
    assert {c for c, _, _ in agentlight.LIGHTS.values()} == set(agentlight.ORDER)


# -- it is derived, not stored -----------------------------------------------

def test_the_light_is_not_a_column(client):
    """A stored light is a second field naming the same fact, and the one a
    screen reads would be the one nobody updates."""
    cols = [r["name"] for r in db.connect().execute("PRAGMA table_info(workflows)")]
    assert "light" not in cols and "agent" not in cols


def test_the_light_follows_the_status_wherever_it_goes(client):
    p = make_profile(client)
    wf = _workflow(client, p["id"])
    assert wf["agent"]["light"] == "green"
    assert wf["agent"]["label"] == "working"

    # Force the status the way the world would, and read it back through the
    # API rather than through the module — the point is that the surface
    # agrees, not that the function works.
    conn = db.connect()
    conn.execute("UPDATE workflows SET status='awaiting_input' WHERE id=?",
                 (wf["id"],))
    conn.commit()
    again = client.get(
        f"/profiles/{p['id']}/workflows/{wf['id']}").json()
    assert again["agent"]["light"] == "amber"
    assert again["agent"]["needs_you"] is True


def test_the_listing_carries_it_too(client):
    """Every workflow reaching a client goes through one hydrate, so a route
    cannot be the one that forgets."""
    p = make_profile(client)
    _workflow(client, p["id"])
    rows = client.get(f"/profiles/{p['id']}/workflows").json()
    assert rows and all("agent" in w and w["agent"]["light"] in agentlight.ORDER
                        for w in rows)


# -- the published legend ----------------------------------------------------

def test_the_legend_is_built_from_the_mapping(client):
    """A legend maintained separately eventually describes a mapping the code
    does not have, and it is the legend people trust."""
    out = client.get("/agent/lights").json()
    assert out["order"] == ["green", "amber", "red"]
    by = {row["light"]: row for row in out["legend"]}
    assert by["amber"]["statuses"] == ["awaiting_input"]
    assert by["red"]["statuses"] == ["cancelled", "failed"]
    assert set(by["green"]["statuses"]) == {"completed", "running"}
