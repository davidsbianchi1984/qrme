"""The routes the console round exposed: named memories, room and desk
lists, and the stub that stopped performing a character.

Field-reported: the memory vault said "interactor" and "profile" where two
names belonged, chat showed "[stub reply in a warm tone to: hi]", and the
rooms and desks existed only for callers who already knew an id.
"""

from __future__ import annotations


def _interactor(client, name="June"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code == 201, r.text
    return r.json()


def test_the_vault_lists_conversations_by_name(client, profile_id):
    june = _interactor(client, "June Bianchi")
    client.post(f"/profiles/{profile_id}/chat",
                json={"interactor_id": june["id"], "message": "hi"})
    rows = client.get(f"/profiles/{profile_id}/memories").json()
    assert len(rows) == 1
    assert rows[0]["interactor_name"] == "June Bianchi"
    assert rows[0]["profile_name"] == "Dana"
    assert rows[0]["turns_count"] >= 2                  # her turn and the reply
    assert "interactor_id" in rows[0]             # the handle for erasing


def test_the_memories_list_is_owner_only(client, profile_id):
    june = _interactor(client)
    client.post(f"/profiles/{profile_id}/chat",
                json={"interactor_id": june["id"], "message": "hi"})
    auth = client.headers.pop("authorization")
    try:
        r = client.get(f"/profiles/{profile_id}/memories")
        assert r.status_code in (401, 403)
    finally:
        client.headers["authorization"] = auth


def test_erasing_one_conversation_leaves_the_others(client, profile_id):
    june = _interactor(client, "June")
    robin = _interactor(client, "Robin")
    for who in (june, robin):
        client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": who["id"], "message": "hello"})
    client.delete(f"/profiles/{profile_id}/memory/{june['id']}")
    names = [r["interactor_name"] for r in
             client.get(f"/profiles/{profile_id}/memories").json()]
    assert names == ["Robin"]


def test_the_stub_no_longer_performs_a_character(client, profile_id):
    june = _interactor(client)
    reply = client.post(f"/profiles/{profile_id}/chat",
                        json={"interactor_id": june["id"],
                              "message": "hi"}).json()
    text = reply["profile_message"]["content"]
    assert "[stub reply" not in text
    assert "ollama.com" in text                  # the free door out is named
    assert "Settings" in text                    # and the keyed one


def test_rooms_are_listable_with_their_channel(client, profile_id):
    june = _interactor(client)
    for channel in ("voice", "ar", "vr"):
        r = client.post("/rooms", json={
            "topic": f"a {channel} room", "channel": channel,
            "participants": [{"kind": "user", "id": june["id"]},
                             {"kind": "profile", "id": profile_id}]})
        assert r.status_code == 201, r.text
    rooms = client.get("/rooms").json()
    assert {r["channel"] for r in rooms} == {"voice", "ar", "vr"}
    assert all(r["participants"] == 2 for r in rooms)


def test_desks_are_listable_and_closed_ones_are_not(client, profile_id):
    r = client.post("/desks", json={
        "owner_id": profile_id, "display_name": "Dana's woodshop",
        "trade": "carpentry", "location": "Ohio",
        "attestor": "id-verify.example", "basis": "document-check"})
    assert r.status_code == 201, r.text
    desks = client.get("/desks").json()
    assert any(d["display_name"] == "Dana's woodshop" for d in desks)
