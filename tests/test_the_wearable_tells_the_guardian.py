"""The rings, straps and patches that report — tied into the guardian.

    asked     wearable sensor readings, sent where the rate-emergency
              guardian already watches
    mattered  QRME must never become the second place health data
              lives; the guardian product exists one door over, with a
              baseline and a ladder behind it — so what is stored here
              is an address, and a reading never touches this platform
"""

from __future__ import annotations

from qrme import wearables
from tests.test_capabilities import auth_header, make_profile


def _paired(client, kind="ring", name="Oura"):
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/wearables",
                    json={"name": name, "kind": kind},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    return me


def test_every_kind_has_decided_what_it_feels():
    """SENSES is a ledger, not a lookup: every kind appears, sensing or
    empty, because "not decided" and "senses nothing" are different
    claims and only one of them is the table's job."""
    assert set(wearables.SENSES) == set(wearables.KINDS)


def test_a_sensing_device_takes_the_guardian_road(client):
    me = _paired(client)
    r = client.put(f"/profiles/{me['id']}/wearables/Oura/guardian",
                   json={"drip_url": "https://jim.example/watch/drip/abc"},
                   headers=auth_header(me))
    assert r.status_code == 200, r.text
    row = r.json()
    assert row["guardian"] == "https://jim.example/watch/drip/abc"
    assert "heart_rate" in row["senses"]


def test_a_device_that_feels_nothing_is_refused(client):
    """A lapel mic has no reading to send; saying so beats storing an
    address that will never carry anything."""
    me = _paired(client, kind="lapel_mic", name="Collar")
    r = client.put(f"/profiles/{me['id']}/wearables/Collar/guardian",
                   json={"drip_url": "https://jim.example/watch/drip/abc"},
                   headers=auth_header(me))
    assert r.status_code == 422, r.text
    assert "senses nothing" in r.text


def test_the_address_is_a_web_address(client):
    me = _paired(client)
    r = client.put(f"/profiles/{me['id']}/wearables/Oura/guardian",
                   json={"drip_url": "not-an-address"},
                   headers=auth_header(me))
    assert r.status_code == 422, r.text


def test_blank_takes_the_road_back_down(client):
    me = _paired(client)
    client.put(f"/profiles/{me['id']}/wearables/Oura/guardian",
               json={"drip_url": "https://jim.example/watch/drip/abc"},
               headers=auth_header(me))
    r = client.put(f"/profiles/{me['id']}/wearables/Oura/guardian",
                   json={"drip_url": None}, headers=auth_header(me))
    assert r.status_code == 200, r.text
    assert r.json()["guardian"] is None


def test_a_stranger_cannot_point_the_readings(client):
    me = _paired(client)
    other = make_profile(client, owner_id="owner-2",
                         display_name="Somebody Else")
    r = client.put(f"/profiles/{me['id']}/wearables/Oura/guardian",
                   json={"drip_url": "https://theirs.example/drip/x"},
                   headers=auth_header(other))
    assert r.status_code == 403, r.text


def test_no_door_here_accepts_a_reading():
    """The claim that keeps this rail safe, held against the source: the
    wearables module stores an address and never a value — no route or
    function takes a heart rate, a step count, or any measured number."""
    import pathlib
    src = (pathlib.Path(wearables.__file__)).read_text(encoding="utf-8")
    for word in ("def drip", "reading:", "bpm", "heart_rate: float",
                 "value: float"):
        assert word not in src
