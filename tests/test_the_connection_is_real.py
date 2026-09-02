"""The pairing stops being a typed claim.

    asked     an actual connection to that watch, established and
              verifiable — not a picker that stores a string
    mattered  the difference between owning a device and having typed
              its name

The radio is in the person's hand, so what the server records is what
the browser's Bluetooth session reported and when. A row with a
``verified_at`` is a pairing something answered for.
"""

from __future__ import annotations

from tests.test_capabilities import auth_header, make_profile


def _paired(client, kind="watch", name="Series 9"):
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/wearables",
                    json={"name": name, "kind": kind},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    return me


def test_the_radio_answer_is_recorded(client):
    me = _paired(client)
    r = client.post(f"/profiles/{me['id']}/wearables/Series 9/verified",
                    json={"device_name": "Apple Watch von Owner",
                          "battery": 82},
                    headers=auth_header(me))
    assert r.status_code == 200, r.text
    row = r.json()
    assert row["verified_as"] == "Apple Watch von Owner"
    assert row["verified_at"]


def test_an_unverified_pairing_says_so(client):
    """No verified_at until something answers — the two states must be
    tellable apart, or 'verifiable' means nothing."""
    me = _paired(client)
    r = client.get(f"/profiles/{me['id']}/wearables",
                   headers=auth_header(me))
    rows = r.json()["wearables"] if isinstance(r.json(), dict) else r.json()
    assert all(w.get("verified_at") is None for w in rows)


def test_repairing_takes_the_verification_off(client):
    """A re-pair rewrites the claim; the answer that vouched for the old
    claim comes off with it."""
    me = _paired(client)
    client.post(f"/profiles/{me['id']}/wearables/Series 9/verified",
                json={"device_name": "Apple Watch"},
                headers=auth_header(me))
    r = client.post(f"/profiles/{me['id']}/wearables",
                    json={"name": "Series 9", "kind": "band"},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    assert r.json()["verified_at"] is None


def test_a_stranger_cannot_vouch(client):
    me = _paired(client)
    other = make_profile(client, owner_id="owner-2",
                         display_name="Somebody Else")
    r = client.post(f"/profiles/{me['id']}/wearables/Series 9/verified",
                    json={"device_name": "Their Watch"},
                    headers=auth_header(other))
    assert r.status_code == 403, r.text


def test_an_unpaired_name_is_a_translated_404(client):
    me = _paired(client)
    r = client.post(f"/profiles/{me['id']}/wearables/Nothing/verified",
                    json={"device_name": "Ghost"},
                    headers=auth_header(me))
    assert r.status_code == 404, r.text
    assert "pair it first" in r.text
