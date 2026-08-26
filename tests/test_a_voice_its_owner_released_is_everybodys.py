"""A voice its owner released is everybody's — on the record, until reclaimed.

The claim (`test_the_voice_binds_to_the_account_that_brought_it`) holds that
a cloned voice belongs to the account that brought it. The first cloned
voice this deployment ever carried was its owner's own, made to be handed
around — *anybody can use it, I am waiving my rights to it* — and the claim,
doing its job, refused every account but one.

    asked     may this voice be everybody's
    mattered  did the person it is made of say so, on the record

## What these guards hold

* a release is the **owner's** act: it needs the owner token, a bound
  voice, and a voice that was anybody's to waive at all — a premade is
  refused, because that waiver would be nobody's to make;
* while released, any account binds it, and the watermark path is exactly
  the one every other voice takes;
* reclaiming is personal — only the account that released may — and it
  takes every other account's binding with it: the release was the only
  thing that made those legitimate;
* and the history stays. Who released, when, and when it came back is a
  row, not a flag.
"""

from __future__ import annotations

from qrme import db, spoken

from .test_the_voice_binds_to_the_account_that_brought_it import (
    _bind, a_profile, head)

DB = "v-david-bianchi"


def _release(client, pid, tok):
    return client.post(f"/profiles/{pid}/voice/release", headers=head(tok))


def _reclaim(client, pid, tok):
    return client.delete(f"/profiles/{pid}/voice/release", headers=head(tok))


def test_a_released_voice_is_anybodys_to_bind(client):
    pid_a, tok_a = a_profile(client, "owner-l", "Lea")
    pid_b, tok_b = a_profile(client, "owner-m", "Max")
    assert _bind(client, pid_a, tok_a, voice=DB).status_code == 200
    assert _bind(client, pid_b, tok_b, voice=DB).status_code == 422
    r = _release(client, pid_a, tok_a)
    assert r.status_code == 200, r.text
    assert r.json()["released"] is True
    assert _bind(client, pid_b, tok_b, voice=DB).status_code == 200
    # And a third account too — "everybody" is not a whitelist of two.
    pid_c, tok_c = a_profile(client, "owner-n", "Nia")
    assert _bind(client, pid_c, tok_c, voice=DB).status_code == 200


def test_the_release_is_the_owners_act(client):
    """No token, no release; no binding, nothing to release; a premade,
    nobody's waiver to make."""
    pid_a, tok_a = a_profile(client, "owner-o", "Oak")
    assert client.post(f"/profiles/{pid_a}/voice/release").status_code in (
        401, 403)
    r = _release(client, pid_a, tok_a)
    assert r.status_code == 422
    assert "bind the voice" in r.text
    daniel = spoken.FALLBACK_VOICES[0]["id"]
    assert _bind(client, pid_a, tok_a, voice=daniel).status_code == 200
    r = _release(client, pid_a, tok_a)
    assert r.status_code == 422
    assert "already everybody" in r.text


def test_reclaiming_takes_the_other_bindings_with_it(client):
    pid_a, tok_a = a_profile(client, "owner-p", "Pia")
    pid_b, tok_b = a_profile(client, "owner-q", "Quinn")
    assert _bind(client, pid_a, tok_a, voice=DB).status_code == 200
    assert _release(client, pid_a, tok_a).status_code == 200
    assert _bind(client, pid_b, tok_b, voice=DB).status_code == 200
    assert _reclaim(client, pid_a, tok_a).status_code == 200
    # B's profile fell silent — the release was the only thing that made
    # that binding legitimate — and the claim stands again.
    assert client.get(f"/profiles/{pid_b}/voice").json()["speaks"] is False
    assert _bind(client, pid_b, tok_b, voice=DB).status_code == 422
    # The owner's own binding survived the reclaim.
    assert client.get(f"/profiles/{pid_a}/voice").json()["speaks"] is True


def test_only_the_releasing_account_may_reclaim(client):
    pid_a, tok_a = a_profile(client, "owner-r", "Rex")
    pid_b, tok_b = a_profile(client, "owner-s", "Sol")
    assert _bind(client, pid_a, tok_a, voice=DB).status_code == 200
    assert _release(client, pid_a, tok_a).status_code == 200
    assert _bind(client, pid_b, tok_b, voice=DB).status_code == 200
    r = _reclaim(client, pid_b, tok_b)
    assert r.status_code == 422
    assert "take it back" in r.text


def test_the_history_is_a_row_and_not_a_flag(client):
    """Who released, when, and when it came back — the decision outlives
    the state, the way a switched-off monitor's row outlives the switch."""
    pid_a, tok_a = a_profile(client, "owner-t", "Tam")
    assert _bind(client, pid_a, tok_a, voice=DB).status_code == 200
    _release(client, pid_a, tok_a)
    _reclaim(client, pid_a, tok_a)
    rows = db.connect().execute(
        "SELECT * FROM voice_releases WHERE voice_id=? AND released_by=?",
        (DB, "owner-t")).fetchall()
    assert len(rows) == 1
    assert rows[0]["released_at"] and rows[0]["reclaimed_at"]


def test_the_binding_read_says_released_so_a_screen_can(client):
    pid_a, tok_a = a_profile(client, "owner-u", "Uma")
    assert _bind(client, pid_a, tok_a, voice=DB).status_code == 200
    assert client.get(f"/profiles/{pid_a}/voice").json()["released"] is False
    _release(client, pid_a, tok_a)
    assert client.get(f"/profiles/{pid_a}/voice").json()["released"] is True
