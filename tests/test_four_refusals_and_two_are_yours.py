"""Reaching out first, and the four separate things that stop it.

A profile may message somebody unprompted only if its owner switched that on
AND the person asked to hear from it first (qrme/opendoor.py — the inverted
connection), and even then three more gates stand in the way. They refuse in
**five different sentences**, and the difference is the whole point — a screen that
collapsed them into "can't right now" would be discarding the only thing the
owner can act on:

| | who lifts it | how |
|---|---|---|
| reactive-only (403) | the owner | turn outreach on |
| door closed (403) | **the recipient** | open their door |
| awaiting a reply (429) | the recipient | reply once |
| rate cap (429) | time | wait out the interval |
| quiet hours (429) | **the recipient** | change their own window |

**Quiet hours are not the owner's to set.** Sending them with an owner token
is a 403, and that refusal is the feature: a window your correspondent can
move is not a boundary. This file pins that, because it is the kind of check
somebody removes to fix a "bug" where the owner cannot configure something.

## Two surfaces that took no token at all

Both found by building the screen, and both fixed here:

* **the engagement record was readable by anybody.** How often a named person
  talks to a profile, across how many sessions, and whether they liked it —
  answered 200 to a caller holding nothing. The rule was already written down
  one route over: a profile's beacon list is owner-gated because *that is a
  list of physical places associated with a person*. This is the same argument
  about a different column;
* **a rating could be cast in somebody else's name.** Worse than it sounds: an
  `up` rating is the trigger for contributing that exchange to the cloud, so
  an unauthenticated caller could cause a stranger's conversation to leave the
  deployment. That is the one failure this repository's whole cloud posture
  exists to prevent, reachable with two ids and no token.

Neither was visible to the typecheck, and neither was caught by the suite —
the tests sent no token because they did not have to.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.test_capabilities import as_interactor


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _cast(client, account="acct_reach", scope="proactive", interval=24):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Rosa",
        "purpose": "companion_coach", "persona": "warm",
        "interaction_scope": scope, "proactive_min_interval_hours": interval,
        "verification": {"birthdate": "1990-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    fan = client.post("/interactors", json={"display_name": "Ana"}).json()
    # The fifth gate (qrme/opendoor.py): outreach now needs the person's
    # own standing yes. Opened here so each test isolates ITS gate; the
    # closed-door refusal has its own test below with the door left shut.
    from qrme import opendoor
    opendoor.set_door(fan["id"], p["id"], open_=True)
    return p, head, fan["id"], {"authorization": f"Bearer {fan['token']}"}


def _all_day(client, uid, uhead):
    """A window that covers right now, whatever the clock says.

    Not `0..0`: a window whose start equals its end covers **nothing** —
    `start <= hour < end` is empty — which is pinned below, because somebody
    setting 9 to 9 to mean "all day" gets no protection at all.
    """
    from datetime import datetime, timezone

    hour = datetime.now(timezone.utc).hour
    return client.put(f"/interactors/{uid}/quiet-hours", headers=uhead,
                      json={"quiet_start": hour, "quiet_end": (hour + 1) % 24})


def _say_something(client, pid, uid, uhead):
    return client.post(f"/profiles/{pid}/chat", headers=uhead,
                       json={"interactor_id": uid, "message": "hello"})


# --- the four refusals, and that they are four ------------------------------

def test_a_reactive_profile_may_not_reach_out_at_all(client):
    p, head, uid, _ = _cast(client, "acct_reactive", scope="reactive")
    r = client.post(f"/profiles/{p['id']}/proactive/{uid}", headers=head)
    assert r.status_code == 403
    assert "reactive-only" in r.json()["detail"]


def test_it_will_not_send_twice_into_silence(client):
    """The gate the owner cannot lift and time will not clear: it reached out
    and heard nothing back, so it does not reach out again."""
    p, head, uid, _ = _cast(client, "acct_silence")
    assert client.post(f"/profiles/{p['id']}/proactive/{uid}",
                       headers=head).status_code == 200
    again = client.post(f"/profiles/{p['id']}/proactive/{uid}", headers=head)
    assert again.status_code == 429
    assert "awaiting a reply" in again.json()["detail"]


def test_a_reply_lifts_the_silence_and_the_rate_cap_takes_over(client):
    """Two gates in sequence, and the second refusal is a *different*
    sentence. Collapsing them would tell the owner to wait when what they
    actually needed was for somebody to answer."""
    p, head, uid, uhead = _cast(client, "acct_seq")
    client.post(f"/profiles/{p['id']}/proactive/{uid}", headers=head)
    _say_something(client, p["id"], uid, uhead)
    r = client.post(f"/profiles/{p['id']}/proactive/{uid}", headers=head)
    assert r.status_code == 429
    detail = r.json()["detail"]
    assert "rate cap" in detail
    assert "awaiting" not in detail, (
        "the silence gate did not lift when the person replied")


def test_quiet_hours_stop_it_whatever_else_is_true(client):
    p, head, uid, uhead = _cast(client, "acct_quiet")
    _all_day(client, uid, uhead)
    r = client.post(f"/profiles/{p['id']}/proactive/{uid}", headers=head)
    assert r.status_code == 429
    assert "quiet hours" in r.json()["detail"]


def test_the_four_refusals_are_four_different_sentences(client):
    """Asserted together, because the value is in their being distinct. Any
    two of them sharing wording is the bug this test exists for."""
    said = set()

    p, head, uid, uhead = _cast(client, "acct_r1", scope="reactive")
    said.add(client.post(f"/profiles/{p['id']}/proactive/{uid}",
                         headers=head).json()["detail"])

    p, head, uid, uhead = _cast(client, "acct_r2")
    client.post(f"/profiles/{p['id']}/proactive/{uid}", headers=head)
    said.add(client.post(f"/profiles/{p['id']}/proactive/{uid}",
                         headers=head).json()["detail"])
    _say_something(client, p["id"], uid, uhead)
    said.add(client.post(f"/profiles/{p['id']}/proactive/{uid}",
                         headers=head).json()["detail"])

    p, head, uid, uhead = _cast(client, "acct_r3")
    _all_day(client, uid, uhead)
    said.add(client.post(f"/profiles/{p['id']}/proactive/{uid}",
                         headers=head).json()["detail"])

    p, head, uid, uhead = _cast(client, "acct_r4")
    from qrme import opendoor
    opendoor.set_door(uid, p["id"], open_=False)
    said.add(client.post(f"/profiles/{p['id']}/proactive/{uid}",
                         headers=head).json()["detail"])

    assert len(said) == 5, f"two refusals say the same thing: {said}"


def test_a_closed_door_stops_it_and_the_recipient_holds_the_handle(client):
    """The fifth refusal, and the inversion itself: the owner's scope says
    the profile is willing; reach still needs the person's standing yes.
    Closing the door stops the reach the same minute, whatever else is
    true."""
    p, head, uid, uhead = _cast(client, "acct_door")
    from qrme import opendoor
    opendoor.set_door(uid, p["id"], open_=False)
    r = client.post(f"/profiles/{p['id']}/proactive/{uid}", headers=head)
    assert r.status_code == 403
    assert "door is open" in r.json()["detail"]


# --- quiet hours belong to the person ---------------------------------------

def test_the_owner_cannot_set_somebody_elses_quiet_hours(client):
    """The refusal is the feature. A window your correspondent can move is
    not a boundary, and this is the check somebody removes to fix a "bug"
    where the owner cannot configure it."""
    p, head, uid, uhead = _cast(client, "acct_notyours")
    r = client.put(f"/interactors/{uid}/quiet-hours", headers=head,
                   json={"quiet_start": 9, "quiet_end": 17})
    assert r.status_code == 403


def test_nobody_at_all_cannot_set_them_either(client):
    p, head, uid, _ = _cast(client, "acct_nobody")
    assert client.put(f"/interactors/{uid}/quiet-hours",
                      json={"quiet_start": 1, "quiet_end": 2}
                      ).status_code == 401


def test_the_person_sets_their_own(client):
    p, head, uid, uhead = _cast(client, "acct_theirs")
    r = client.put(f"/interactors/{uid}/quiet-hours", headers=uhead,
                   json={"quiet_start": 22, "quiet_end": 7})
    assert r.status_code == 200
    assert r.json()["quiet_start"] == 22 and r.json()["quiet_end"] == 7


def test_a_window_that_starts_where_it_ends_covers_nothing(client):
    """Recorded, not corrected. `start <= hour < end` with the two equal is
    an empty range, so 9-to-9 — which reads as *all day* — protects nobody.
    The screen says so; changing the arithmetic would silently redefine every
    window already stored, which is a worse answer than saying it plainly.
    """
    p, head, uid, uhead = _cast(client, "acct_samehour")
    from datetime import datetime, timezone
    hour = datetime.now(timezone.utc).hour
    client.put(f"/interactors/{uid}/quiet-hours", headers=uhead,
               json={"quiet_start": hour, "quiet_end": hour})
    assert client.post(f"/profiles/{p['id']}/proactive/{uid}",
                       headers=head).status_code == 200, (
        "an equal start and end started covering the whole day — if that was "
        "deliberate, every window already stored just changed meaning")


def test_the_screen_warns_about_that_window():
    """The warning moved into the l10n table when the screen was localized,
    so this asks two things instead of one: that the screen still looks the
    sentence up, and that the sentence is still there to be looked up. Either
    half alone would pass a screen that has stopped saying it."""
    assert 'tr("rch.samehour", lang)' in _markup("app/src/screens/Reaching.tsx")
    assert "same hour" in _src("app/src/l10n.ts")


@pytest.mark.parametrize("body", [
    {"quiet_start": 24, "quiet_end": 7},
    {"quiet_start": 22, "quiet_end": -1},
])
def test_an_hour_outside_the_clock_is_refused(client, body):
    p, head, uid, uhead = _cast(client, f"acct_hours{body['quiet_start']}")
    assert client.put(f"/interactors/{uid}/quiet-hours", headers=uhead,
                      json=body).status_code == 422


# --- the record about a person ----------------------------------------------

def test_a_stranger_cannot_read_the_engagement_record(client):
    """It answered 200 to a caller holding nothing. How often somebody talks
    to a profile is a fact about them, and it was available to anybody who
    knew two ids."""
    p, head, uid, uhead = _cast(client, "acct_eng")
    _say_something(client, p["id"], uid, uhead)
    assert client.get(f"/profiles/{p['id']}/engagement/{uid}"
                      ).status_code == 401
    nosy = client.post("/interactors", json={"display_name": "Nosy"}).json()
    assert client.get(f"/profiles/{p['id']}/engagement/{uid}",
                      headers={"authorization": f"Bearer {nosy['token']}"}
                      ).status_code == 403


@pytest.mark.parametrize("whose", ["owner", "person"])
def test_both_parties_may_read_it(client, whose):
    """Two people are entitled: the owner because it is their profile's
    relationship, the person because it is a record of them."""
    p, head, uid, uhead = _cast(client, f"acct_both{whose}")
    _say_something(client, p["id"], uid, uhead)
    r = client.get(f"/profiles/{p['id']}/engagement/{uid}",
                   headers=head if whose == "owner" else uhead)
    assert r.status_code == 200
    assert r.json()["interactions"] == 1


def test_a_rating_needs_the_raters_own_token(client):
    """The serious one. An `up` rating is the trigger for contributing the
    exchange to the cloud, so open, this let an unauthenticated caller push a
    stranger's conversation out of the deployment."""
    p, head, uid, uhead = _cast(client, "acct_rate")
    _say_something(client, p["id"], uid, uhead)
    path = f"/profiles/{p['id']}/interactions/{uid}/feedback"
    assert client.post(path, json={"rating": "up"}).status_code == 401
    nosy = client.post("/interactors", json={"display_name": "Nosy"}).json()
    assert client.post(path, json={"rating": "up"},
                       headers={"authorization": f"Bearer {nosy['token']}"}
                       ).status_code == 403
    assert client.post(path, json={"rating": "up"},
                       headers=uhead).status_code == 200


def test_the_owner_cannot_rate_on_their_behalf(client):
    """It would be a lie about what somebody thought, and the score is what
    the profile then behaves from."""
    p, head, uid, uhead = _cast(client, "acct_ownrate")
    _say_something(client, p["id"], uid, uhead)
    assert client.post(f"/profiles/{p['id']}/interactions/{uid}/feedback",
                       json={"rating": "up"}, headers=head).status_code == 403


def test_only_up_or_down(client):
    p, head, uid, uhead = _cast(client, "acct_sideways")
    _say_something(client, p["id"], uid, uhead)
    assert client.post(f"/profiles/{p['id']}/interactions/{uid}/feedback",
                       json={"rating": "maybe"}, headers=uhead
                       ).status_code == 422


def test_the_write_answers_more_than_the_read(client):
    """Recorded rather than smoothed over. `last_seen` and `contributed` come
    out of the rating and are not in the record — a screen that assumed the
    two shapes matched would render blanks."""
    p, head, uid, uhead = _cast(client, "acct_shapes")
    _say_something(client, p["id"], uid, uhead)
    wrote = client.post(f"/profiles/{p['id']}/interactions/{uid}/feedback",
                        json={"rating": "up"}, headers=uhead).json()
    read = client.get(f"/profiles/{p['id']}/engagement/{uid}",
                      headers=uhead).json()
    assert "cloud_contributed" in wrote and "last_seen" in wrote
    assert "contributed" not in read and "last_seen" not in read


# --- the embedding ----------------------------------------------------------

def test_the_embedding_is_the_owners_alone(client):
    """A latent model of a named person. Unlike the engagement record, the
    person themselves does not get it either — it is not a record of what
    they did, it is what the profile inferred."""
    p, head, uid, uhead = _cast(client, "acct_emb")
    _say_something(client, p["id"], uid, uhead)
    assert client.get(f"/profiles/{p['id']}/embedding/{uid}",
                      headers=head).status_code == 200
    assert client.get(f"/profiles/{p['id']}/embedding/{uid}",
                      headers=uhead).status_code == 403


def test_before_anybody_talks_it_says_so_rather_than_inventing_one(client):
    p, head, uid, _ = _cast(client, "acct_noemb")
    r = client.get(f"/profiles/{p['id']}/embedding/{uid}", headers=head)
    assert r.status_code == 404
    assert "interact first" in r.json()["detail"]


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_exists():
    assert (REPO / "app/src/screens/Reaching.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.engagement(", "api.rateExchange(", "api.personaEmbedding(",
    "api.reachOut(", "api.setQuietHours(",
])
def test_the_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Reaching.tsx")


def test_quiet_hours_are_sent_with_the_persons_token_not_the_owners():
    """The console has both tokens in hand, and picking the wrong one here
    is a 403 the user cannot act on."""
    src = _src("app/src/screens/Reaching.tsx")
    call = src[src.index("api.setQuietHours("):]
    call = call[:call.index("interactorToken)") + 20]
    assert "interactorToken" in call
    assert "ownerToken" not in call and " token)" not in call


def test_the_screen_says_quiet_hours_are_not_the_owners_to_set():
    """Rendered, not just enforced. An owner who does not know why the
    control is absent will look for a bug."""
    assert 'tr("rch.notyours", lang)' in _markup("app/src/screens/Reaching.tsx")
    l10n = _src("app/src/l10n.ts")
    assert "not one you hold over anybody else" in l10n
    # And the gates paragraph, which is where the fourth refusal is named as
    # somebody else's to lift.
    assert "is not yours at all" in l10n


def test_the_screen_renders_whether_the_exchange_left():
    """`contributed` is the only place a person is told that their thumbs-up
    sent something to the shared model."""
    assert "rated.contributed" in _markup("app/src/screens/Reaching.tsx")
