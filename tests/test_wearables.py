"""Watches and wearables paired over Bluetooth.

The wrist is a control surface for the owner, not a place a persona lives —
that distinction is the one worth testing, because folding the two together
would mean pairing a watch could put somebody's synthetic profile on it.
"""

import pathlib
import re

import pytest

from qrme import wearables
from tests.test_capabilities import auth_header, make_profile


def test_pairing_a_watch(client):
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/wearables",
                    json={"name": "My Watch", "kind": "watch"},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    d = r.json()
    assert d["paired"] is True and d["transport"] == "bluetooth"
    assert d["faces"] == list(wearables.DEFAULT_FACES)


def test_only_the_owner_pairs_a_device(client):
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    r = client.post(f"/profiles/{a['id']}/wearables",
                    json={"name": "Sneaky", "kind": "watch"},
                    headers=auth_header(b))
    assert r.status_code in (401, 403)


def test_faces_are_a_permission_not_a_free_field(client):
    """A face added later must not arrive on every wrist by default."""
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/wearables",
                    json={"name": "W", "kind": "watch",
                          "faces": ["agents", "everything"]},
                    headers=auth_header(me))
    assert r.status_code == 422
    assert "unknown face" in r.json()["detail"]


def test_a_device_only_shows_the_faces_it_was_given(client):
    me = make_profile(client, display_name="Owner")
    client.post(f"/profiles/{me['id']}/wearables",
                json={"name": "W", "kind": "watch", "faces": ["agents"]},
                headers=auth_header(me))
    assert wearables.may_show(me["id"], "W", "agents") is True
    assert wearables.may_show(me["id"], "W", "control") is False


def test_unpairing_is_a_revocation_not_a_delete(client):
    """So a device sent away cannot come back by re-presenting the same name,
    and the owner can still see what was ever paired."""
    me = make_profile(client, display_name="Owner")
    client.post(f"/profiles/{me['id']}/wearables",
                json={"name": "Lost Watch", "kind": "watch"},
                headers=auth_header(me))
    r = client.delete(f"/profiles/{me['id']}/wearables/Lost Watch",
                      headers=auth_header(me))
    assert r.status_code == 200 and r.json()["paired"] is False
    assert wearables.may_show(me["id"], "Lost Watch", "agents") is False

    live = client.get(f"/profiles/{me['id']}/wearables",
                      headers=auth_header(me)).json()["wearables"]
    assert live == []
    history = client.get(f"/profiles/{me['id']}/wearables?include_revoked=true",
                         headers=auth_header(me)).json()["wearables"]
    assert [d["name"] for d in history] == ["Lost Watch"]


def test_a_wearable_is_not_an_embodiment(client):
    """`embodiments` is where a profile lives — a speaker, a hologram, a robot.
    Pairing a watch must not put a persona on it."""
    from qrme import db
    me = make_profile(client, display_name="Owner")
    client.post(f"/profiles/{me['id']}/wearables",
                json={"name": "W", "kind": "watch"}, headers=auth_header(me))
    n = db.connect().execute(
        "SELECT COUNT(*) AS n FROM embodiments WHERE profile_id=?",
        (me["id"],)).fetchone()["n"]
    assert n == 0


def test_there_is_a_watch_face_for_every_permission(client):
    """A face somebody can enable and never see would be a permission granting
    nothing; a face with no permission would be one nobody chose."""
    src = pathlib.Path("docs/watch/build.py").read_text()
    drawn = set(re.findall(r'dict\(num=\d+, title="(\w+)"', src))
    assert {f.lower() for f in drawn} == set(wearables.FACES), (
        f"watch faces {sorted(drawn)} vs permissions "
        f"{sorted(wearables.FACES)}")


def test_pairing_says_nothing_about_a_microphone(client):
    """Pairing and permission only. Anything that listens is a separate
    decision, and it has not been made here."""
    import inspect
    src = inspect.getsource(wearables).lower()
    body = src[src.index("kinds = "):]
    for word in ("microphone", "mic", "audio", "capture", "sample"):
        assert word not in body, f"{word!r} appears in the pairing model"
