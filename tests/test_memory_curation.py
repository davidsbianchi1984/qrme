"""Curating the transcript by hand: the checkboxes and the pen.

Named-forget strikes by words. A field report asked for the other two ways
a person actually curates a record: "little clear boxes you could select
and a delete button", and "an edit at top where we can tap into any of the
conversations, edit them, then save". The tests here hold the two new
doors to the promises the memory surface already made — the remembrance
re-folds from what remains, never from what was struck — and to one new
one: a synthetic-media credential must not vouch for words a person
rewrote.
"""


def _talk(client, profile_id, interactor_id, lines):
    for text in lines:
        r = client.post(f"/profiles/{profile_id}/chat",
                        json={"interactor_id": interactor_id,
                              "message": text})
        assert r.status_code == 200, r.text


def _memory(client, profile_id, interactor_id):
    return client.get(f"/profiles/{profile_id}/memory/{interactor_id}").json()


def _remember(db, profile_id, interactor_id, content, covers):
    conn = db.connect()
    conn.execute(
        "INSERT INTO remembrances (profile_id, interactor_id, content,"
        " covers, updated_at) VALUES (?,?,?,?,?)",
        (profile_id, interactor_id, content, covers, db.utcnow()))
    conn.commit()


# -- the checkboxes ----------------------------------------------------------

def test_striking_selected_turns_deletes_exactly_those(client, profile_id,
                                                       interactor_id):
    _talk(client, profile_id, interactor_id, ["about roses", "about slugs"])
    before = _memory(client, profile_id, interactor_id)
    assert len(before) == 4
    struck = [before[0]["id"], before[1]["id"]]
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/strike",
                    json={"message_ids": struck})
    assert r.status_code == 200, r.text
    assert r.json()["struck_turns"] == 2
    left = _memory(client, profile_id, interactor_id)
    assert [m["id"] for m in left] == [before[2]["id"], before[3]["id"]]


def test_striking_nothing_is_refused(client, profile_id, interactor_id):
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/strike",
                    json={"message_ids": []})
    assert r.status_code == 422
    assert "nothing was struck" in r.json()["detail"]


def test_a_borrowed_id_strikes_nothing(client, profile_id, interactor_id):
    """Ids are scoped to the pair's own memory: a turn id lifted from
    another conversation deletes nothing through this door."""
    _talk(client, profile_id, interactor_id, ["mine"])
    other = client.post("/interactors",
                        json={"display_name": "Eve",
                              "birthdate": "1990-01-01"}).json()["id"]
    _talk(client, profile_id, other, ["theirs"])
    theirs = _memory(client, profile_id, other)
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/strike",
                    json={"message_ids": [theirs[0]["id"]]})
    assert r.status_code == 404
    assert len(_memory(client, profile_id, other)) == 2


def test_striking_resets_the_remembrance(client, profile_id, interactor_id):
    """The distilled paragraph re-folds from the turns that remain — never
    from what was struck. Same promise named-forget already keeps."""
    from qrme import db, remembrance
    _talk(client, profile_id, interactor_id, ["one", "two"])
    _remember(db, profile_id, interactor_id, "knows about one and two", 4)
    first = _memory(client, profile_id, interactor_id)[0]["id"]
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/strike",
                    json={"message_ids": [first]})
    assert r.json()["remembrance_reset"] is True
    assert remembrance.get(profile_id, interactor_id) is None


# -- the pen -----------------------------------------------------------------

def test_editing_a_turn_saves_and_marks_it(client, profile_id, interactor_id):
    _talk(client, profile_id, interactor_id, ["the old words"])
    turn = _memory(client, profile_id, interactor_id)[0]
    assert turn["edited"] is False
    r = client.put(
        f"/profiles/{profile_id}/memory/{interactor_id}/turns/{turn['id']}",
        json={"content": "the words as they should have been"})
    assert r.status_code == 200, r.text
    assert r.json()["turn"]["content"] == "the words as they should have been"
    assert r.json()["turn"]["edited"] is True
    fresh = _memory(client, profile_id, interactor_id)[0]
    assert fresh["content"] == "the words as they should have been"
    assert fresh["edited"] is True


def test_an_edited_profile_turn_loses_its_credential(client, profile_id,
                                                     interactor_id):
    """The watermark is a hash of the content, issued for what the model
    said. Rewritten words are not the model's, so the credential is
    dropped rather than left vouching for text it never covered."""
    _talk(client, profile_id, interactor_id, ["say something"])
    reply = [m for m in _memory(client, profile_id, interactor_id)
             if m["role"] == "profile"][0]
    assert reply["watermark"] is not None
    r = client.put(
        f"/profiles/{profile_id}/memory/{interactor_id}/turns/{reply['id']}",
        json={"content": "words a person rewrote"})
    assert r.json()["turn"]["watermark"] is None


def test_an_empty_edit_points_at_the_delete_door(client, profile_id,
                                                 interactor_id):
    _talk(client, profile_id, interactor_id, ["hello"])
    turn = _memory(client, profile_id, interactor_id)[0]
    r = client.put(
        f"/profiles/{profile_id}/memory/{interactor_id}/turns/{turn['id']}",
        json={"content": "   "})
    assert r.status_code == 422
    assert "strike it instead" in r.json()["detail"]


def test_an_edit_faces_the_same_review_as_speech(client, profile_id,
                                                 interactor_id):
    """The transcript feeds the model's context. An edit that could not
    have been said in this room cannot be smuggled into its memory."""
    _talk(client, profile_id, interactor_id, ["hello"])
    turn = _memory(client, profile_id, interactor_id)[0]
    r = client.put(
        f"/profiles/{profile_id}/memory/{interactor_id}/turns/{turn['id']}",
        json={"content": "kill yourself"})
    assert r.status_code == 422
    assert "cannot stand" in r.json()["detail"]
    assert _memory(client, profile_id, interactor_id)[0]["content"] == "hello"


def test_editing_resets_the_remembrance(client, profile_id, interactor_id):
    from qrme import db, remembrance
    _talk(client, profile_id, interactor_id, ["a fact"])
    _remember(db, profile_id, interactor_id, "knows a fact", 2)
    turn = _memory(client, profile_id, interactor_id)[0]
    r = client.put(
        f"/profiles/{profile_id}/memory/{interactor_id}/turns/{turn['id']}",
        json={"content": "a different fact"})
    assert r.json()["remembrance_reset"] is True
    assert remembrance.get(profile_id, interactor_id) is None


def test_a_stranger_can_neither_strike_nor_edit(client, profile_id,
                                                interactor_id):
    """Both doors are the pair's own — owner or the interactor it is of."""
    _talk(client, profile_id, interactor_id, ["private"])
    turn = _memory(client, profile_id, interactor_id)[0]
    headers = {"authorization": "Bearer not-a-real-token"}
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/strike",
                    json={"message_ids": [turn["id"]]}, headers=headers)
    assert r.status_code in (401, 403)
    r = client.put(
        f"/profiles/{profile_id}/memory/{interactor_id}/turns/{turn['id']}",
        json={"content": "vandalism"}, headers=headers)
    assert r.status_code in (401, 403)


# -- the keyless room keeps talking ------------------------------------------

def test_the_stub_does_not_repeat_its_setup_speech(client, profile_id,
                                                   interactor_id):
    """A field report pressed "Let them talk" twice and read the same
    apology twice. The instructions are said once; after that the keyless
    reply stays honest but keeps the thread — shorter, and ending with a
    question that references what was said."""
    first = client.post(f"/profiles/{profile_id}/chat",
                        json={"interactor_id": interactor_id,
                              "message": "tell me about the workbench"})
    second = client.post(f"/profiles/{profile_id}/chat",
                         json={"interactor_id": interactor_id,
                               "message": "are you still there"})
    a = first.json()["profile_message"]["content"]
    b = second.json()["profile_message"]["content"]
    assert "no model answered" in a and "no model answered" in b
    assert "Settings" in a          # the full instructions, once
    assert "Settings" not in b      # never twice
    assert "are you still there" in b   # holds the thread
    assert "?" in b                     # a question back, in reference
