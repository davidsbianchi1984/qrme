"""A room id is not a secret, and it was the only thing a room asked for.

`GET /rooms/{id}/mic` says this out loud. Its docstring explains that a room
id "rides in beacons and on printed QR stickers, which is the point of them",
and that answering anybody who holds one "made a privacy feature into the
opposite one". That reasoning was applied to the microphone disclosure and to
nothing else in the room.

So, until this round:

* **`POST /rooms/{id}/messages` let anybody speak as anybody.** The speaker
  came from ``sender_id`` in the body, and the check was only that the id
  named a participant — never that the *caller* was that person. A stranger's
  token plus a named participant's id produced a `201`, a message stored under
  her name, a transcript reading `from: Ada`, and every profile in the room
  answering as though she had spoken.
* **`GET /rooms/{id}/messages` asked for nothing at all.** Not a wrong token —
  no token. The entire conversation was public to anyone with the id.
* **`POST /rooms/{id}/advance` asked for nothing either**, so a stranger could
  run somebody else's room forward indefinitely against their model key.

All three now go through `_require_in_room`, which already existed in the same
file, written for the narrower fact.

## The body field stays

``sender_id`` is still on `RoomMessage` and still ignored. Three shipped
native clients send it, and removing it would 422 them all on upgrade; reading
it is what was wrong, not receiving it. The same shape as `publish_pack`,
which keeps ``publisher_owner_id`` and takes the account from the token.
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


def _person(client, name="P", birthdate="1990-01-01"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


def _profile(client, account="acct_room"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Iris",
        "purpose": "enterprise_agent", "persona": "a calm host",
        "verification": {"birthdate": "1988-03-03"}}).json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


def _room(client, uid, head, pid, channel="chat"):
    r = client.post("/rooms", headers=head, json={
        "topic": "the roof", "channel": channel,
        "participants": [{"kind": "user", "id": uid},
                         {"kind": "profile", "id": pid}]})
    assert r.status_code == 201, r.text
    return r.json()["id"]


# --- who may speak ----------------------------------------------------------

def test_a_stranger_cannot_speak_as_a_participant(client):
    """The one this file exists for. Ada's id, a stranger's token."""
    uid, ada = _person(client, "Ada")
    pid, _own = _profile(client)
    rid = _room(client, uid, ada, pid)
    _sid, stranger = _person(client, "Stranger")

    r = client.post(f"/rooms/{rid}/messages", headers=stranger,
                    json={"sender_id": uid, "message": "sell the house"})
    assert r.status_code == 403
    assert "not in this room" in r.json()["detail"]


def test_nobody_at_all_cannot_speak(client):
    uid, ada = _person(client, "Ada")
    pid, _own = _profile(client, "acct_anon")
    rid = _room(client, uid, ada, pid)
    assert client.post(f"/rooms/{rid}/messages",
                       json={"sender_id": uid, "message": "hi"}
                       ).status_code == 401


def test_a_participant_still_speaks(client):
    uid, ada = _person(client, "Ada")
    pid, _own = _profile(client, "acct_speak")
    rid = _room(client, uid, ada, pid)
    r = client.post(f"/rooms/{rid}/messages", headers=ada,
                    json={"sender_id": uid, "message": "Can it be fixed?"})
    assert r.status_code == 201, r.text
    assert r.json()["message"]["from"] == "Ada"
    assert r.json()["replies"], "the profiles did not answer"


def test_the_speaker_is_the_token_not_the_body(client):
    """A participant sending somebody else's id is recorded as themselves.

    The field is ignored rather than refused, because three shipped native
    clients send it and a 422 on upgrade would be a worse answer than simply
    not believing it.
    """
    uid, ada = _person(client, "Ada")
    other, _oh = _person(client, "Someone Else")
    pid, _own = _profile(client, "acct_body")
    rid = _room(client, uid, ada, pid)
    client.post("/rooms", headers=ada, json={"topic": "t", "channel": "chat",
                "participants": [{"kind": "user", "id": uid},
                                 {"kind": "profile", "id": pid}]})
    r = client.post(f"/rooms/{rid}/messages", headers=ada,
                    json={"sender_id": other, "message": "mine"})
    assert r.status_code == 201, r.text
    assert r.json()["message"]["from"] == "Ada", (
        "the body's sender_id was believed over the token")


def test_an_owner_token_is_refused_by_name(client):
    """A room turn is spoken by a person. The profile's owner is in the room
    for the disclosure, not to talk in it, and the refusal says so."""
    uid, ada = _person(client, "Ada")
    pid, own = _profile(client, "acct_ownertok")
    rid = _room(client, uid, ada, pid)
    r = client.post(f"/rooms/{rid}/messages", headers=own,
                    json={"sender_id": uid, "message": "hi"})
    assert r.status_code == 403
    assert "spoken by a person" in r.json()["detail"]


# --- who may read -----------------------------------------------------------

def test_the_transcript_is_for_the_people_in_the_room(client):
    uid, ada = _person(client, "Ada")
    pid, _own = _profile(client, "acct_read")
    rid = _room(client, uid, ada, pid)
    client.post(f"/rooms/{rid}/messages", headers=ada,
                json={"sender_id": uid, "message": "something private"})

    _sid, stranger = _person(client, "Stranger")
    assert client.get(f"/rooms/{rid}/messages",
                      headers=stranger).status_code == 403
    assert client.get(f"/rooms/{rid}/messages").status_code == 401
    mine = client.get(f"/rooms/{rid}/messages", headers=ada)
    assert mine.status_code == 200 and mine.json()


def test_the_profiles_owner_may_read_it(client):
    """Their profile is in the room and is answering; the transcript is what
    it said. `_require_in_room` accepts an owner token for exactly this."""
    uid, ada = _person(client, "Ada")
    pid, own = _profile(client, "acct_ownerread")
    rid = _room(client, uid, ada, pid)
    assert client.get(f"/rooms/{rid}/messages", headers=own).status_code == 200


# --- who may advance it -----------------------------------------------------

def test_a_stranger_cannot_run_the_room_forward(client):
    """Every advance is model work billed to somebody. A room id is not
    authority to spend it."""
    uid, ada = _person(client, "Ada")
    pid, _own = _profile(client, "acct_adv")
    rid = _room(client, uid, ada, pid)
    _sid, stranger = _person(client, "Stranger")
    assert client.post(f"/rooms/{rid}/advance",
                       headers=stranger).status_code == 403
    assert client.post(f"/rooms/{rid}/advance").status_code == 401
    assert client.post(f"/rooms/{rid}/advance",
                       headers=ada).status_code == 201


def test_an_owner_may_advance_it(client):
    """A profile↔profile room has no user participant to press the button,
    so an owner token has to be enough here even though it is not enough to
    speak."""
    uid, ada = _person(client, "Ada")
    pid, own = _profile(client, "acct_advown")
    rid = _room(client, uid, ada, pid)
    assert client.post(f"/rooms/{rid}/advance", headers=own).status_code == 201


# --- the microphone, which was right all along ------------------------------

def test_the_microphone_disclosure_is_unchanged(client):
    """The route the reasoning was borrowed from. Pinned so the borrowing
    cannot drift away from the original."""
    uid, ada = _person(client, "Ada")
    pid, _own = _profile(client, "acct_mic")
    rid = _room(client, uid, ada, pid, channel="voice")
    _sid, stranger = _person(client, "Stranger")
    assert client.get(f"/rooms/{rid}/mic", headers=stranger).status_code == 403
    lent = client.post(f"/rooms/{rid}/mic", headers=ada,
                       json={"interactor_id": uid, "device": "watch"})
    assert lent.status_code == 201, lent.text
    seen = client.get(f"/rooms/{rid}/mic", headers=ada).json()
    assert len(seen["microphones_lent"]) == 1


def test_somebody_else_cannot_take_your_microphone_back(client):
    uid, ada = _person(client, "Ada")
    pid, _own = _profile(client, "acct_mic2")
    rid = _room(client, uid, ada, pid, channel="voice")
    client.post(f"/rooms/{rid}/mic", headers=ada,
                json={"interactor_id": uid, "device": "watch"})
    _sid, stranger = _person(client, "Stranger")
    assert client.delete(f"/rooms/{rid}/mic/{uid}",
                         headers=stranger).status_code == 403
    assert client.delete(f"/rooms/{rid}/mic/{uid}",
                         headers=ada).status_code == 200


# --- the console half -------------------------------------------------------

def _markup(rel: str) -> str:
    s = (REPO / rel).read_text(encoding="utf-8")
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_exists_and_calls_all_six():
    src = (REPO / "app/src/screens/Inside.tsx").read_text(encoding="utf-8")
    for binding in ("api.roomMessages(", "api.sayInRoom(", "api.advanceRoom(",
                    "api.micsInRoom(", "api.lendMicInRoom(",
                    "api.takeBackMicInRoom("):
        assert binding in src, f"{binding} is not called by the screen"


def test_the_screen_sends_the_interactor_token_not_the_owners():
    """A room turn is spoken by a person, and the screen holds both tokens."""
    src = _markup("app/src/screens/Inside.tsx")
    assert "session.interactorToken" in src
    assert "ownerToken" not in src


def test_the_screen_says_the_microphone_is_seen_by_everyone():
    """The disclosure, in both halves.

    The paragraph moved into the l10n table, so the screen is asked for the
    lookup and the table is asked for the sentence. Either half alone would
    pass while the other was gone: a screen that looks up a key the table
    has dropped renders `ins.micpitch`, and a table that keeps the sentence
    no screen reads is a translation nobody sees.
    """
    assert 'tr("ins.micpitch", lang)' in _markup("app/src/screens/Inside.tsx")
    l10n = _markup("app/src/l10n.ts")
    assert "a microphone the others cannot see" in l10n
    assert "Everybody here is shown that you lent it" in l10n


# --- the native shells, which all had to learn to send it -------------------

def _native(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_every_native_shell_sends_a_token_on_the_room_routes():
    """Gating the routes broke three shipped clients until they carried one.
    None of them sent a credential on any room route before this round.
    """
    ios = _native("native/ios/Sources/ApiClient.swift")
    assert 'func roomTranscript(roomId: String, token: String)' in ios
    assert 'func roomAdvance(roomId: String, token: String)' in ios

    kt = _native("native/android/app/src/main/java/app/qrme/studio/ApiClient.kt")
    assert "suspend fun roomAdvance(roomId: String, token: String)" in kt
    assert "suspend fun roomTranscript(roomId: String, token: String)" in kt

    cs = _native("native/windows/ApiClient.cs")
    assert "public async Task RoomAdvance(string roomId, string token)" in cs
    assert "public Task<RoomMsg[]> RoomTranscript(string roomId, string token)" in cs


def test_windows_keeps_the_interactor_token_at_all():
    """It never had one. The shell could hold an identity and not act as it,
    which is why these routes had to be open for its Community page to work.
    """
    st = _native("native/windows/AppState.cs")
    assert "public string? InteractorToken { get; set; }" in st
    api = _native("native/windows/ApiClient.cs")
    assert '[property: JsonPropertyName("token")] string? Token = null' in api
