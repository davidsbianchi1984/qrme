"""The steering lock: dials that hold still on purpose.

The research's steadiest fear about personas is drift — a personality that
moves under your hands, or under somebody else's. The lock answers it
literally: while it stands, no steering write lands (423, the refusal in
the reader's language), not the owner's own slip, not a compromised
session, not any future automation. The lock and the key are both the
owner's.
"""

from tests.test_steering import _profile


def test_locked_dials_hold_still_and_the_key_turns(client):
    pid = _profile(client)
    r = client.put(f"/profiles/{pid}/steering",
                   json={"values": {"warmth": 80}})
    assert r.status_code == 200

    r = client.post(f"/profiles/{pid}/steering/lock",
                    json={"reason": "she is finished"})
    assert r.status_code == 201, r.text
    assert r.json()["reason"] == "she is finished"

    # The lock shows at both read doors.
    assert client.get(f"/profiles/{pid}/steering").json()["lock"]
    assert client.get(f"/profiles/{pid}/steering/hub").json()["lock"]

    # No write lands — not through steering, not through the hub.
    r = client.put(f"/profiles/{pid}/steering",
                   json={"values": {"warmth": 10}})
    assert r.status_code == 423
    assert "locked" in r.json()["detail"]
    r = client.put(f"/profiles/{pid}/steering/hub",
                   json={"values": {"warmth": 10}})
    assert r.status_code == 423

    # The dials stand exactly where they were locked.
    values = client.get(f"/profiles/{pid}/steering").json()["values"]
    assert values["warmth"] == 80

    # The key turns, and the hands work again.
    r = client.request("DELETE", f"/profiles/{pid}/steering/lock")
    assert r.status_code == 200
    assert r.json()["lock"] is None
    r = client.put(f"/profiles/{pid}/steering",
                   json={"values": {"warmth": 10}})
    assert r.status_code == 200
    assert r.json()["values"]["warmth"] == 10
