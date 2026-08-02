"""The cross-product smoke check: boots QRME + JIM-mini + PDI in-process,
seeds all three, wires the tandems, and drives one live exchange with
sealed, provable custody. Skips cleanly when the sibling packages are not
installed (the same requirement as the suite gateway).

## The finding

Every part of the multi-phase handoff had a test. `qrme/workflows.py` names
three properties a delegated goal has to keep — memory carried forward between
phases, every phase generated through the profile's persona, and `confirm`
pausing for a human rather than running off the end — and each had unit
coverage on its own side of the wire. The one thing nothing did was walk the
whole arc: the smoke check seeded all three products, wired the tandems, drove
one exchange and proved its custody, and then stopped. `start_workflow`,
`advance`, and `specialist_tasks` were never called across the boundary.

    asked     does the workflow round-trip
    mattered  does anything walk the whole arc

Driving it found two behaviours nothing had exercised end to end, both of which
are now steps rather than surprises: delegated work is Pro-gated
(`synthetic_agents`, a 402 naming the tier), and delegation is *off* until the
specialist's owner opts in, with `research` refused unless a grant scopes what
it may read. A one-exchange smoke check meets neither.
"""

import pytest

pytest.importorskip("jim", reason="jim-mini not installed alongside qrme")
pytest.importorskip("pdi", reason="pdi not installed alongside qrme")


@pytest.fixture(scope="module")
def report(tmp_path_factory):
    """One run, read by several checks. The boot is ~all of the cost."""
    from suite import smoke

    return smoke.run(workdir=str(tmp_path_factory.mktemp("smoke")))


def _green(report):
    """Fail naming the step that died, not by printing the whole report.

    The first draft asserted `report["ok"], report` and let pytest render it.
    A run that aborted in the arc printed a truncated dict of the *seeded*
    steps with `...` where the failure was — every check erroring with the same
    unreadable blob, and none of them saying which leg broke.
    """
    if report["ok"]:
        return
    dead = [s for s in report["steps"] if not s["ok"]]
    reached = [s["name"] for s in report["steps"] if s["ok"]]
    pytest.fail(
        "the smoke run died at "
        + (f"{dead[0]['name']}: {dead[0]['detail']}" if dead else "no step")
        + "\n  got as far as: " + ", ".join(reached))


@pytest.fixture(scope="module")
def steps(report):
    _green(report)
    return {s["name"]: s for s in report["steps"]}


def test_suite_smoke_is_green(report):
    _green(report)


def test_the_exchange_reached_the_specialist(steps):
    assert steps["end_to_end_tandem"]["detail"]["condition"] == \
        "financial_stress"
    assert "Marcus Bell" in steps["end_to_end_tandem"]["detail"]["specialist"]


def test_the_custody_chain_held(steps):
    assert steps["custody_provenance"]["detail"]["chain_intact"] is True


# --- the arc ----------------------------------------------------------------

def test_delegated_work_names_the_tier_that_buys_it(steps):
    """The 402 is a step, not a thing stepped past: somebody deciding whether
    to pay needs the gate named, and a smoke check that quietly ran as Pro
    would never show it."""
    assert steps["workflow_needs_pro"]["detail"]["gate"] == "synthetic_agents"


def test_the_specialists_owner_had_to_opt_in(steps):
    """Delegation is off by default and `research` needs a grant. A run that
    started a task without either would prove a stranger can put a synthetic
    profile to work uninvited.

    Driven by opening the gate and watching this fail. Worth recording what it
    took: flipping `delegation.offer` alone — the advertised answer to "do you
    accept work" — did *not* get a task started, because `delegation.start`
    checks the policy again on its own. Both had to be opened before anything
    ran. The advertisement is not the gate.
    """
    detail = steps["specialist_opted_in"]["detail"]
    assert detail["refused_before_opt_in"] is True, detail
    assert "research" in detail["phases"], detail
    assert detail["scoped_by_grant"] is True, detail


def test_the_arc_carried_memory_across_more_than_one_phase(steps):
    """The property `workflows.py` puts first. One phase proves a route exists;
    two prove the second one was handed what the first produced."""
    done = steps["workflow_arc"]["detail"]["goal_phases"]
    assert len(done) >= 2, f"only {done} ran — nothing was carried forward"


def test_confirm_paused_instead_of_running_off_the_end(steps):
    """`confirm` waits for a human. An arc that walked straight through it
    would have sent something on a person's behalf that they never saw, and a
    check that only counted phases would have called that a fuller pass."""
    detail = steps["workflow_arc"]["detail"]
    assert detail["status"] == "awaiting_input", detail
    assert detail["awaiting"], f"paused with nothing named: {detail}"


def test_jim_knows_which_profile_did_the_work(steps):
    """The arc ran in QRME; the row that survives it is JIM's. If it came back
    without the profile id, the audit trail stops at the boundary."""
    assert steps["workflow_arc"]["detail"]["qrme_profile_id"], \
        steps["workflow_arc"]
