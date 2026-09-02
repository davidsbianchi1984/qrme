"""The room's turns become footage, and its rotation waits out an outage.

Two field reports from the same phone, ten minutes apart.

The first was a black frame. The room's video format promised "this
turn, as footage" and delivered "no footage for this turn yet" forever,
because `filming.auto_render` — the thing that turns an approved reply
into a render — was called from exactly one place, and that place was
the one-on-one chat door. The room stored its turns and never ordered a
frame. `SeatFilm.tsx` even says so in its own header: "Nothing here
starts a render." Now the room does, on the same ceremony as chat:
after the reply is settled, never waited for, approved turns only, with
`auto_render` holding the road, ceiling and configured gates itself.

The second was a transcript reading backwards: an apology — "still
without a model, no model answered this request either" — quoting a
question from minutes earlier, landing ABOVE the line the person had
just typed, followed by a good answer. The rotation had taken an
unprompted turn during a one-request model outage, and the fallback's
apology went into the record like a real turn. A person who asked is
owed an answer even when every model is down; the rotation is not owed
a turn. So an advance whose generation DEGRADED to the local fallback
is skipped — while a deployment whose only voice is the stub keeps
advancing, because a profile-only room runs on that and the stub is
that install's honest voice.
"""

import json

import pytest

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)


class _Answer:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _speaks(script):
    calls = []

    def urlopen(request, timeout=None):
        body = None
        if request.data:
            body = json.loads(request.data.decode())
        calls.append((request.full_url, body))
        return _Answer(json.dumps(script(request.full_url, body)).encode())

    urlopen.calls = calls
    return urlopen


@pytest.fixture()
def filmable(monkeypatch):
    """A deployment with somewhere to send a scene."""
    monkeypatch.setenv("QRME_FILM_PROVIDER", "seedance")
    monkeypatch.setenv("QRME_FILM_URL", "https://render.test/v1")
    monkeypatch.setenv("QRME_FILM_KEY", "secret-value")


def test_a_room_turn_on_the_video_road_orders_a_render(client, monkeypatch,
                                                       filmable):
    """The reply lands, and a pending render row lands with it."""
    from qrme import filming

    user = make_interactor(client, "Vera", "1990-01-01")
    pal = make_profile(client)
    filming.set_road(pal["id"], "video", 120)

    speaks = _speaks(lambda url, body: {"id": "job-room-1"})
    monkeypatch.setattr("urllib.request.urlopen", speaks)

    room = client.post("/rooms", json={
        "topic": "the footage", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": pal["id"]}]}).json()
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"sender_id": user,
                          "message": "tell me about the bakery"})
    assert r.status_code == 201
    assert len(r.json()["replies"]) == 1

    row = filming.latest(pal["id"])
    assert row is not None, "the room turn ordered no footage"
    assert row["status"] in ("pending", "done")
    # The scene that went out is the reply that was stored, not the
    # person's message — the footage is of the profile's turn.
    assert speaks.calls, "nothing reached the render service"


def test_a_room_turn_off_the_video_road_orders_nothing(client, monkeypatch,
                                                       filmable):
    """auto_render's own gate, exercised through the room door: a seat
    that never chose video stays footage-free."""
    from qrme import filming

    user = make_interactor(client, "Wes", "1990-01-01")
    pal = make_profile(client)

    speaks = _speaks(lambda url, body: {"id": "job-never"})
    monkeypatch.setattr("urllib.request.urlopen", speaks)

    room = client.post("/rooms", json={
        "topic": "words only", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": pal["id"]}]}).json()
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"sender_id": user, "message": "hello there"})
    assert r.status_code == 201
    assert filming.latest(pal["id"]) is None


def test_a_degraded_rotation_turn_is_waited_out_not_posted(client,
                                                           monkeypatch):
    """The outage case: a real provider was asked, the fallback answered,
    and the rotation stores nothing rather than the apology."""
    from qrme import llm

    class Degraded:
        def generate(self, system, messages):
            llm.note_answered_by(llm.LOCAL_FALLBACK,
                                 degraded_from="anthropic")
            return "Still here, still without a model."

    monkeypatch.setattr("qrme.llm.get_provider",
                        lambda cloud=None, choice=None: Degraded())

    dana = make_profile(client)
    echo = make_profile(client, display_name="Echo", kind="fictional",
                        persona="A thoughtful fictional conversationalist.")
    own = {"Authorization": f"Bearer {dana['owner_token']}"}
    room = client.post("/rooms", json={
        "topic": "gardens", "channel": "voice",
        "participants": [{"kind": "profile", "id": dana["id"]},
                         {"kind": "profile", "id": echo["id"]}]}).json()
    r = client.post(f"/rooms/{room['id']}/advance", headers=own)
    assert r.status_code == 201
    assert r.json()["replies"] == [], (
        "an outage's apology went into the transcript as a turn")
    transcript = client.get(f"/rooms/{room['id']}/messages",
                            headers=own).json()
    assert transcript == []


def test_a_person_still_gets_the_honest_apology_when_every_model_is_down(
        client, monkeypatch):
    """The other half of the rule: a DIRECT answer keeps the degraded
    reply, because a person who asked is owed an answer."""
    from qrme import llm

    class Degraded:
        def generate(self, system, messages):
            llm.note_answered_by(llm.LOCAL_FALLBACK,
                                 degraded_from="anthropic")
            return "I heard you, and no model answered this request."

    monkeypatch.setattr("qrme.llm.get_provider",
                        lambda cloud=None, choice=None: Degraded())

    user = make_interactor(client, "Ada", "1990-01-01")
    pal = make_profile(client)
    room = client.post("/rooms", json={
        "topic": "outage hour", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": pal["id"]}]}).json()
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"sender_id": user, "message": "anyone there?"})
    assert r.status_code == 201
    assert len(r.json()["replies"]) == 1, (
        "a person's question went unanswered during the outage")


def test_a_stub_only_deployment_keeps_its_rotation(client):
    """A profile-only room in a deployment whose only voice is the stub
    still advances — the stub is that install's honest voice, and this
    is the line that keeps the outage rule from widening into it."""
    dana = make_profile(client)
    echo = make_profile(client, display_name="Echo", kind="fictional",
                        persona="A thoughtful fictional conversationalist.")
    own = {"Authorization": f"Bearer {dana['owner_token']}"}
    room = client.post("/rooms", json={
        "topic": "gardens", "channel": "voice",
        "participants": [{"kind": "profile", "id": dana["id"]},
                         {"kind": "profile", "id": echo["id"]}]}).json()
    r = client.post(f"/rooms/{room['id']}/advance", headers=own)
    assert r.status_code == 201
    assert len(r.json()["replies"]) == 1
