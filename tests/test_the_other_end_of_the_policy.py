"""An owner could publish a delegation policy that nobody could take up.

`Delegate` built the owner's half: mint a revocable grant, say which phases
may run unattended, start a workflow, advance it, answer it, cancel it. All of
it about *my profile working for me*.

Delegation is not for that. It exists for the person on the **other** end of a
conversation — somebody already talking to a profile hands it a job, inside
the limits its owner set. That half had four bindings in `api.ts` and no screen
calling any of them, so the policy was publishable and unusable from here.

Nothing was wrong with the backend. Driven end to end, every refusal is right
and every one of them is the feature working rather than failing:

* the **offer** is public and lists phases only — never the grant id, because
  which source items the owner scoped is the owner's business;
* enabling a phase that would read every source item on the profile is
  refused unless a grant scopes it;
* starting one **requires an existing conversation** — delegated work is not
  for a stranger holding a profile id;
* reading or advancing one is 403 to an outsider, 401 to nobody at all, and
  200 to the delegate *and* to the owner, who are the two people entitled to
  it for different reasons.

So this file pins the shape rather than reporting a fix. It is the first round
in a while with no defect in it, and that is worth recording plainly: the
feature was finished and unreachable, which is the failure the door audit
exists to name.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _profile(client, account="acct_del"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Rook",
        "purpose": "enterprise_agent", "persona": "an operator",
        "verification": {"birthdate": "1988-03-03"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p["id"], head


def _person(client, name="Client"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": "1990-01-01"}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


def _open(client, pid, head, phases=("draft",)):
    r = client.put(f"/profiles/{pid}/delegation", headers=head,
                   json={"enabled": True, "phases": list(phases)})
    assert r.status_code == 200, r.text
    return r


def _talking(client, pid, uid, head):
    client.post(f"/profiles/{pid}/chat", headers=head,
                json={"interactor_id": uid, "message": "hello"})


# --- the offer --------------------------------------------------------------

def test_the_offer_is_public_and_shows_only_phases(client):
    pid, head = _profile(client, "acct_offer")
    before = client.get(f"/profiles/{pid}/delegation").json()
    assert before["delegation"] is False and before["phases"] == []

    _open(client, pid, head)
    after = client.get(f"/profiles/{pid}/delegation").json()
    assert after["delegation"] is True and after["phases"] == ["draft"]
    assert "grant_id" not in after, (
        "which sources the owner scoped is the owner's business; the caller "
        "needs the shape of the request, not the scope behind it")


def test_a_phase_that_reads_everything_needs_a_grant(client):
    """The refusal names what it is protecting rather than the rule."""
    pid, head = _profile(client, "acct_grantless")
    r = client.put(f"/profiles/{pid}/delegation", headers=head,
                   json={"enabled": True, "phases": ["research", "draft"]})
    assert r.status_code == 422
    assert "requires a grant" in r.json()["detail"]
    assert "every source item" in r.json()["detail"]


# --- who may hand work over -------------------------------------------------

def test_you_have_to_be_talking_to_it_first(client):
    pid, head = _profile(client, "acct_cold")
    uid, mine = _person(client)
    _open(client, pid, head)
    r = client.post(f"/profiles/{pid}/delegated-workflows", headers=mine,
                    json={"interactor_id": uid, "goal": "summarise the lease"})
    assert r.status_code == 403
    assert "already talking to it" in r.json()["detail"]


def test_a_profile_that_did_not_offer_refuses(client):
    pid, _head = _profile(client, "acct_closed")
    uid, mine = _person(client)
    _talking(client, pid, uid, mine)
    r = client.post(f"/profiles/{pid}/delegated-workflows", headers=mine,
                    json={"interactor_id": uid, "goal": "do a thing"})
    assert r.status_code == 403
    assert "does not accept delegated workflows" in r.json()["detail"]


def test_somebody_in_conversation_can_hand_it_over(client):
    pid, head = _profile(client, "acct_hand")
    uid, mine = _person(client)
    _open(client, pid, head)
    _talking(client, pid, uid, mine)
    r = client.post(f"/profiles/{pid}/delegated-workflows", headers=mine,
                    json={"interactor_id": uid, "goal": "summarise the lease"})
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "running"


# --- who may read and run it ------------------------------------------------

def _handed(client, account="acct_run"):
    pid, head = _profile(client, account)
    uid, mine = _person(client)
    _open(client, pid, head)
    _talking(client, pid, uid, mine)
    wf = client.post(f"/profiles/{pid}/delegated-workflows", headers=mine,
                     json={"interactor_id": uid, "goal": "draft it"}).json()
    return pid, head, mine, wf["id"]


def test_an_outsider_can_neither_read_nor_run_it(client):
    pid, _head, _mine, wid = _handed(client, "acct_outsider")
    _oid, theirs = _person(client, "Outsider")
    assert client.get(f"/profiles/{pid}/delegated-workflows/{wid}",
                      headers=theirs).status_code == 403
    assert client.post(f"/profiles/{pid}/delegated-workflows/{wid}/advance",
                       headers=theirs).status_code == 403


def test_nobody_at_all_is_refused(client):
    pid, _head, _mine, wid = _handed(client, "acct_anon")
    assert client.get(
        f"/profiles/{pid}/delegated-workflows/{wid}").status_code == 401


def test_the_delegate_reads_and_advances_it(client):
    pid, _head, mine, wid = _handed(client, "acct_delegate")
    got = client.get(f"/profiles/{pid}/delegated-workflows/{wid}",
                     headers=mine)
    assert got.status_code == 200
    assert got.json()["delegated_to"]
    ran = client.post(f"/profiles/{pid}/delegated-workflows/{wid}/advance",
                      headers=mine)
    assert ran.status_code == 200, ran.text


def test_the_owner_reads_it_too(client):
    """Both, for different reasons: it is their profile doing the work, and
    somebody else's job being done. Neither is a guest."""
    pid, head, _mine, wid = _handed(client, "acct_ownerread")
    assert client.get(f"/profiles/{pid}/delegated-workflows/{wid}",
                      headers=head).status_code == 200


def test_a_workflow_id_from_another_profile_is_a_404(client):
    pid, _head, mine, _wid = _handed(client, "acct_crossed")
    other, ohead = _profile(client, "acct_crossed2")
    assert client.get(f"/profiles/{other}/delegated-workflows/{_wid}",
                      headers=mine).status_code == 404


# --- the console half -------------------------------------------------------

def _markup(rel: str) -> str:
    s = (REPO / rel).read_text(encoding="utf-8")
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_calls_all_four_delegated_bindings():
    src = (REPO / "app/src/screens/Delegate.tsx").read_text(encoding="utf-8")
    for binding in ("api.startDelegatedWorkflow(", "api.delegatedWorkflow(",
                    "api.advanceDelegatedWorkflow(",
                    "api.resumeDelegatedWorkflow("):
        assert binding in src, f"{binding} is still called by nothing"


def test_the_delegate_half_uses_the_interactor_token():
    """Here you are the person asking somebody else's profile to work. The
    owner token above is for the other half of the same screen."""
    src = _markup("app/src/screens/Delegate.tsx")
    assert "session.interactorToken" in src


def test_the_screen_says_you_must_be_talking_to_it():
    src = _markup("app/src/screens/Delegate.tsx")
    flat = " ".join(src.split())
    assert 'tr("dlg.talking", lang)' in flat, (
        "the screen has stopped rendering the paragraph that says so")
    l10n = " ".join(
        (REPO / "app/src/l10n.ts").read_text(encoding="utf-8").split())
    assert "not a stranger holding a profile id" in l10n, (
        "the sentence left the l10n table, so the screen looks up nothing")


def test_the_screen_does_not_promise_to_show_the_scope():
    """The offer omits the grant id deliberately, and a screen that implied
    otherwise would be describing a different endpoint."""
    flat = " ".join(_markup("app/src/screens/Delegate.tsx").split())
    assert 'tr("dlg.noscope.shown", lang)' in flat
    l10n = " ".join(
        (REPO / "app/src/l10n.ts").read_text(encoding="utf-8").split())
    assert "is not shown, and is not yours to know" in l10n


# --- and one binding that wanted deleting rather than wiring ----------------

def test_the_duplicate_health_binding_is_gone():
    """`api.health` hit the same route as `healthInfo`, threw the body away
    and returned a boolean. Nothing called it, and a binding that discards
    the answer is worse than none: the next person wanting a health check
    would have found it and lost the version with it.

    Not every unused binding wants a screen — some want deleting, and the
    guard's backlog should shrink both ways.
    """
    src = (REPO / "app/src/api.ts").read_text(encoding="utf-8")
    assert "\n  health: () =>" not in src
    assert "healthInfo:" in src, "the one that is actually used went instead"
