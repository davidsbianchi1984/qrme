"""A handoff that was clinical-only, and carried the conversation alone.

`referral.prepare` packages a session for a clinician and does it well: the
signature is over the exact bytes, bound to that referral, redeemable once.
Two things were wrong with what it carried rather than how.

**It was clinical only.** A cook profile handing a matter to a butcher, a
money profile to a broker, a coach to a physiotherapist — every synthetic
profile that can bring somebody real into it needs the same thing, and only
one area of life had it.

**It carried the conversation and nothing else.** A provider stepping into
somebody's matter is not caught up by six messages; they are caught up by the
photographs, the statements, the history. A briefing without them makes the
provider ask, which is the person telling their story twice — once to the
profile and once to the professional — which is the thing a handoff exists to
prevent.

    asked     can a session be handed to a professional
    mattered  does the professional arrive already knowing

## What the guards here hold

The dangerous half is the second one. A briefing that can carry files is a
briefing that can carry the wrong files, to somebody nobody chose, at a
profile's discretion. So three things are checked from the outside:

* everything in a briefing comes through the **one** function that reads a
  revocable grant, and revoking it empties the briefing;
* a briefing cannot be prepared for a provider the person has not attached;
* the specialist is named as synthetic **inside the document**, because a
  document travels away from the screen that framed it.

And one from the inside: `mypeople.attach` takes no area, so nobody can be
filed under an expertise they do not have.
"""

import inspect

import pytest

from qrme import briefing, mypeople, tasks


def _provider(client, name="Marsh & Sons", area="butchery",
              location="Camden"):
    r = client.post("/providers", json={"name": name, "area": area,
                                        "location": location,
                                        "contact": "01234 567890"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _grant(client, profile_id, scope=None):
    r = client.post(f"/profiles/{profile_id}/grants",
                    json={"scope": scope} if scope else {})
    assert r.status_code == 201, r.text
    return r.json()


def _source(client, profile_id, kind="photo", title="the cut in question"):
    r = client.post(f"/profiles/{profile_id}/sources",
                    json={"kind": kind, "title": title,
                          "content": "a photograph of what was delivered"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


# --------------------------------------------------------------------------
# Your own people, in every area of life.
# --------------------------------------------------------------------------

def test_the_area_comes_off_the_provider_not_off_the_caller():
    """A form that lets the caller say what somebody *is* is a form that
    eventually files a butcher under cardiology — and `referral.match` filters
    expertise before it ranks geography, so a wrong area defeats that ordering
    from inside the data."""
    sig = inspect.signature(mypeople.attach)
    assert "area" not in sig.parameters, (
        "`attach` grew an area argument; the provider row is the only place "
        "that may say what somebody does")


def test_somebody_you_kept_outranks_the_best_stranger(client, interactor_id, interactor_head):
    mine = _provider(client, "Marsh & Sons")
    _provider(client, "Aabbey Meats")          # sorts first alphabetically
    client.post(f"/interactors/{interactor_id}/people",
                json={"provider_id": mine, "preferred": True}, headers=interactor_head)

    rows = client.get(f"/interactors/{interactor_id}/people/for-area",
                      params={"area": "butchery"}, headers=interactor_head).json()
    assert rows[0]["name"] == "Marsh & Sons"
    assert rows[0]["yours"] is True
    # And the search still runs underneath, so an area with nobody in it is
    # not a dead end.
    assert any(r["yours"] is False for r in rows)


def test_every_row_says_whether_they_are_yours(client, interactor_id, interactor_head):
    """*Yours* and *found for you* are different claims, and somebody about to
    send their history is entitled to know which they are looking at."""
    _provider(client, "Aabbey Meats")
    rows = client.get(f"/interactors/{interactor_id}/people/for-area",
                      params={"area": "butchery"}, headers=interactor_head).json()
    assert rows and all("yours" in r for r in rows)
    assert all(r["yours"] is False for r in rows)


def test_preferring_one_keeps_the_others(client, interactor_id, interactor_head):
    """A second opinion is still somebody this person chose."""
    a, b = _provider(client, "Marsh & Sons"), _provider(client, "Aabbey Meats")
    for pid in (a, b):
        client.post(f"/interactors/{interactor_id}/people",
                    json={"provider_id": pid}, headers=interactor_head)
    client.post(f"/interactors/{interactor_id}/people/{b}/prefer", headers=interactor_head)
    mine = client.get(f"/interactors/{interactor_id}/people", headers=interactor_head).json()
    assert len(mine) == 2
    assert [r["preferred"] for r in mine] == [True, False]
    assert mine[0]["provider_id"] == b


def test_your_people_are_yours_and_not_the_profile_owners(client,
                                                          interactor_id,
                                                          interactor_head):
    pid = _provider(client)
    client.post(f"/interactors/{interactor_id}/people",
                json={"provider_id": pid}, headers=interactor_head)
    r = client.get(f"/interactors/{interactor_id}/people",
                   headers={"authorization": "Bearer not-this-person"})
    assert r.status_code in (401, 403), r.text


# --------------------------------------------------------------------------
# The briefing, and the grant that decides what is in it.
# --------------------------------------------------------------------------

def test_the_provider_arrives_knowing_what_was_granted(
        client, profile_id, interactor_id, interactor_head):
    """The whole point, end to end: attachments the person granted travel with
    the matter, and the display text counts them out loud."""
    pid = _provider(client)
    client.post(f"/interactors/{interactor_id}/people",
                json={"provider_id": pid, "preferred": True}, headers=interactor_head)
    _source(client, profile_id)
    grant = _grant(client, profile_id)

    r = client.post("/briefings/preview", json={
        "interactor_id": interactor_id, "profile_id": profile_id,
        "provider_id": pid, "matter": "the lamb that arrived grey",
        "grant_token": grant["token"]}, headers=interactor_head)
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["package"]["matter"] == "the lamb that arrived grey"
    assert out["package"]["attachments"], "granted material did not travel"
    assert "the lamb that arrived grey" in out["reads"]
    # Counted, not described. "Your history" is a phrase somebody agrees to
    # without knowing what it covers.
    assert "1 item" in out["reads"]


def test_revoking_the_grant_empties_the_briefing(
        client, profile_id, interactor_id, interactor_head):
    """The entire value of a revocable grant is that revoking it stops
    everything — including the path that was written after it."""
    pid = _provider(client)
    client.post(f"/interactors/{interactor_id}/people",
                json={"provider_id": pid}, headers=interactor_head)
    _source(client, profile_id)
    grant = _grant(client, profile_id)
    client.delete(f"/grants/{grant['id']}")

    r = client.post("/briefings/preview", json={
        "interactor_id": interactor_id, "profile_id": profile_id,
        "provider_id": pid, "matter": "the lamb that arrived grey",
        "grant_token": grant["token"]}, headers=interactor_head)
    assert r.status_code == 403, r.text


def test_a_narrow_grant_carries_only_what_it_names(
        client, profile_id, interactor_id, interactor_head):
    pid = _provider(client)
    client.post(f"/interactors/{interactor_id}/people",
                json={"provider_id": pid}, headers=interactor_head)
    kept = _source(client, profile_id, title="the cut in question")
    _source(client, profile_id, title="something else entirely")
    grant = _grant(client, profile_id, scope=[kept])

    out = client.post("/briefings/preview", json={
        "interactor_id": interactor_id, "profile_id": profile_id,
        "provider_id": pid, "matter": "the lamb",
        "grant_token": grant["token"]}, headers=interactor_head).json()
    titles = [a["title"] for a in out["package"]["attachments"]]
    assert titles == ["the cut in question"]


def test_a_briefing_cannot_reach_somebody_you_never_chose(
        client, profile_id, interactor_id, interactor_head):
    """A file does not travel to a professional nobody picked — not even one
    the search would happily have returned."""
    stranger = _provider(client, "Some Other Butcher")
    grant = _grant(client, profile_id)
    r = client.post("/briefings/preview", json={
        "interactor_id": interactor_id, "profile_id": profile_id,
        "provider_id": stranger, "matter": "the lamb",
        "grant_token": grant["token"]}, headers=interactor_head)
    assert r.status_code == 404, r.text


def test_the_specialist_is_named_synthetic_inside_the_document(
        client, profile_id, interactor_id, interactor_head):
    """A document travels away from the screen that framed it, so the
    disclosure rides in the bytes rather than around them."""
    pid = _provider(client)
    client.post(f"/interactors/{interactor_id}/people",
                json={"provider_id": pid}, headers=interactor_head)
    grant = _grant(client, profile_id)
    out = client.post("/briefings/preview", json={
        "interactor_id": interactor_id, "profile_id": profile_id,
        "provider_id": pid, "matter": "the lamb",
        "grant_token": grant["token"]}, headers=interactor_head).json()
    assert out["package"]["specialist"]["synthetic"] is True
    assert "synthetic" in briefing.document(out["package"])


def test_a_briefing_with_no_subject_is_refused(client, profile_id,
                                               interactor_id,
                                               interactor_head):
    pid = _provider(client)
    client.post(f"/interactors/{interactor_id}/people",
                json={"provider_id": pid}, headers=interactor_head)
    grant = _grant(client, profile_id)
    r = client.post("/briefings/preview", json={
        "interactor_id": interactor_id, "profile_id": profile_id,
        "provider_id": pid, "matter": "   ",
        "grant_token": grant["token"]}, headers=interactor_head)
    assert r.status_code == 422, r.text


def test_the_same_briefing_always_hashes_the_same_way():
    """Canonical, so the thing signed and the thing sent cannot diverge."""
    package = {"user": "Dana", "provider": "Marsh & Sons", "attachments": []}
    assert briefing.document(package) == briefing.document(dict(package))


# --------------------------------------------------------------------------
# And structurally, so it stays true after the next edit.
# --------------------------------------------------------------------------

def test_one_function_decides_what_a_grant_means():
    """Two readings of a scope is one reading too many: a second place
    interpreting it is a second place that can interpret it generously."""
    src = inspect.getsource(briefing)
    assert "scoped_items" in src
    assert "source_items" not in src, (
        "briefing.py queries the vault directly; everything must arrive "
        "already filtered by the grant")
    assert "grants" not in src, "briefing.py reads the grant table itself"
    assert "json.loads" not in src, (
        "briefing.py decodes a scope of its own — one function reads a "
        "grant, and it is tasks.scoped_items")


def test_the_task_runner_reads_the_grant_through_the_same_door():
    """The refactor that made this safe: both callers go through one
    function, so revoking a grant stops both."""
    assert "scoped_items" in inspect.getsource(tasks.run)


def test_nothing_granted_is_a_sentence_not_a_status():
    with pytest.raises(tasks.NothingGranted) as caught:
        tasks.scoped_items("prf_nobody", "grt_nothing")
    assert "revoked" in str(caught.value)
