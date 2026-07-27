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
    # Read the permission each face declares, rather than lower-casing its
    # title and hoping. The title is prose — "On Camera" reads better on a
    # wrist than "Camera" — and a binding that breaks when somebody writes a
    # two-word title is a binding people loosen instead of satisfying.
    drawn = set(re.findall(r'face="([a-z_]+)"', src))
    assert drawn == set(wearables.FACES), (
        f"watch faces {sorted(drawn)} vs permissions "
        f"{sorted(wearables.FACES)}")


def test_pairing_opens_no_capture_path(client):
    """This test used to assert the module never said "microphone" at all.
    That stopped being the right check the moment room-facing mics had to be
    refused *by name* — so it now asserts the thing that actually matters:
    nothing here records, streams, or reads a sample.
    """
    import inspect
    src = inspect.getsource(wearables).lower()
    for verb in ("record(", "capture(", "stream(", "listen(", "sample(",
                 "transcribe", "audio_", "def capture", "def listen"):
        assert verb not in src, f"{verb!r} appears in the pairing model"


# -- what may be worn, and what may not --------------------------------------

def test_the_wearable_kinds_are_the_ones_worn_on_a_person(client):
    me = make_profile(client, display_name="Owner")
    for kind in ("watch", "earbuds", "lapel_mic", "clip_on_mic", "glasses",
                 "ring", "pendant", "headset", "band"):
        r = client.post(f"/profiles/{me['id']}/wearables",
                        json={"name": f"dev-{kind}", "kind": kind},
                        headers=auth_header(me))
        assert r.status_code == 201, f"{kind}: {r.text}"


@pytest.mark.parametrize("kind", ["smart_speaker", "conference_puck",
                                  "room_array", "tabletop_mic", "desk_mic"])
def test_a_room_facing_microphone_is_refused(client, kind):
    """The rule the platform's owner has restated every time this came up: a
    device that hears whoever walks in cannot be paired, because that person
    did not pair it, was not asked, and may have a right not to be recorded.
    Refused rather than allowed-and-restricted — a restriction is a setting
    somebody can change."""
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/wearables",
                    json={"name": "Kitchen", "kind": kind},
                    headers=auth_header(me))
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert "walks into the room" in detail
    assert "right not to be recorded" in detail


def test_the_refusals_are_published_with_their_reason(client):
    """So a client greys them out with the reason rather than offering one and
    returning a 422."""
    me = make_profile(client, display_name="Owner")
    r = client.get(f"/profiles/{me['id']}/wearables",
                   headers=auth_header(me)).json()
    assert set(r["refused"]) == set(wearables.REFUSED)
    assert all("walks into the room" in v for v in r["refused"].values())
    assert not set(r["kinds"]) & set(r["refused"])


def test_pairing_a_microphone_kind_opens_no_channel(client):
    """A lapel mic can be *paired* — the registry is what a later feature will
    need — but nothing here starts listening. If a capture path ever grows out
    of this module, this fails."""
    from qrme import db
    me = make_profile(client, display_name="Owner")
    client.post(f"/profiles/{me['id']}/wearables",
                json={"name": "Lapel", "kind": "lapel_mic"},
                headers=auth_header(me))
    row = db.connect().execute(
        "SELECT * FROM wearables WHERE profile_id=? AND name='Lapel'",
        (me["id"],)).fetchone()
    # The row records what it is and what it may show. Nothing else.
    assert set(row.keys()) == {
        "id", "profile_id", "name", "kind", "transport", "faces",
        "paired_at", "last_seen_at", "revoked_at"}
    assert wearables.may_show(me["id"], "Lapel", "agents") is True
