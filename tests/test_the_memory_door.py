"""The memory door: what do you remember about me, and forget that one thing.

The account answers from the records, not by generation — the distilled
paragraph as it stands, and the honest counts around it. The forget is the
scalpel the erase-all door never was: the turns that said the thing are
deleted and the distilled remembrance is re-folded from what remains,
never from what was struck.
"""

from qrme import db, remembrance


def _say(profile_id, interactor_id, i, text):
    db.connect().execute(
        "INSERT INTO messages (id, profile_id, interactor_id, role,"
        " content, status, created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("msg"), profile_id, interactor_id,
         "interactor" if i % 2 == 0 else "profile",
         text, "approved", f"2026-02-01T00:{i:02d}:00Z"))
    db.connect().commit()


def test_the_account_tells_what_the_records_hold(client, profile_id,
                                                 interactor_id):
    _say(profile_id, interactor_id, 0, "I planted tomatoes this spring")
    _say(profile_id, interactor_id, 1, "May they outrun the frost")
    db.connect().execute(
        "INSERT INTO remembrances (profile_id, interactor_id, content,"
        " covers, updated_at) VALUES (?,?,?,?,?)",
        (profile_id, interactor_id,
         "They garden; tomatoes went in this spring.", 2, db.utcnow()))
    db.connect().commit()

    r = client.get(f"/profiles/{profile_id}/memory/{interactor_id}/account")
    assert r.status_code == 200, r.text
    account = r.json()
    assert "tomatoes" in account["remembers"]
    assert account["folded_turns"] == 2
    assert account["first_at"] and account["last_at"]


def test_forget_that_one_thing_and_only_that_thing(client, profile_id,
                                                   interactor_id):
    _say(profile_id, interactor_id, 0, "my ex used to say that")
    _say(profile_id, interactor_id, 1, "I hear you")
    _say(profile_id, interactor_id, 2, "the garden is doing well")
    db.connect().execute(
        "INSERT INTO remembrances (profile_id, interactor_id, content,"
        " covers, updated_at) VALUES (?,?,?,?,?)",
        (profile_id, interactor_id,
         "They mentioned their ex once; they keep a garden.", 3,
         db.utcnow()))
    db.connect().commit()

    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/forget",
                    json={"about": "my ex"})
    assert r.status_code == 200, r.text
    assert r.json() == {"forgotten_turns": 1, "remembrance_reset": True,
                        "sealed_forgotten": 0}

    # The turn that said it is gone; the garden stays.
    left = [row["content"] for row in db.connect().execute(
        "SELECT content FROM messages WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id))]
    assert "my ex used to say that" not in left
    assert "the garden is doing well" in left
    # The paragraph is dropped, to re-fold from what remains.
    assert remembrance.get(profile_id, interactor_id) is None


def test_the_forget_refuses_empty_and_unremembered_words(client, profile_id,
                                                         interactor_id):
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/forget",
                    json={"about": "   "})
    assert r.status_code == 422
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/forget",
                    json={"about": "a thing never said"})
    assert r.status_code == 404
