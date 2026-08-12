"""Rehearsal mode: practice the hard conversation, nothing remembered.

The research ask under this round: people use personas to find their
words before a real conversation — and stop the moment the practice
starts counting against the relationship. The room holds its transcript
only while it is open; nothing said inside ever reaches messages,
engagement or the remembrance; closing the room wipes it.
"""

from qrme import db


def test_the_rehearsal_replies_and_the_relationship_never_hears_it(
        client, profile_id, interactor_id):
    r = client.post(f"/profiles/{profile_id}/rehearsal", json={
        "interactor_id": interactor_id,
        "scenario": "asking my manager for a raise"})
    assert r.status_code == 201, r.text
    room = r.json()
    assert room["remembered"] is False

    r = client.post(
        f"/profiles/{profile_id}/rehearsal/{room['id']}/say",
        json={"message": "I wanted to talk about my compensation."})
    assert r.status_code == 200, r.text
    turn = r.json()
    assert turn["reply"]
    assert turn["turns"] == 1
    assert turn["remembered"] is False

    # Nothing reached the places the relationship remembers from.
    conn = db.connect()
    for table in ("messages", "engagement", "remembrances"):
        n = conn.execute(
            f"SELECT COUNT(*) AS n FROM {table} WHERE profile_id=?"
            " AND interactor_id=?", (profile_id, interactor_id)).fetchone()
        assert n["n"] == 0, f"the rehearsal leaked into {table}"

    # Closing the room wipes the transcript with it.
    r = client.request(
        "DELETE", f"/profiles/{profile_id}/rehearsal/{room['id']}")
    assert r.status_code == 200
    assert r.json() == {"id": room["id"], "turns": 1, "erased": True}
    n = conn.execute("SELECT COUNT(*) AS n FROM rehearsals").fetchone()["n"]
    assert n == 0
    # The closed room is gone, not archived.
    r = client.post(
        f"/profiles/{profile_id}/rehearsal/{room['id']}/say",
        json={"message": "hello?"})
    assert r.status_code == 404


def test_an_empty_scenario_and_an_empty_line_are_refused(
        client, profile_id, interactor_id):
    r = client.post(f"/profiles/{profile_id}/rehearsal", json={
        "interactor_id": interactor_id, "scenario": "   "})
    assert r.status_code == 422
    assert "empty scenario" in r.json()["detail"]

    r = client.post(f"/profiles/{profile_id}/rehearsal", json={
        "interactor_id": interactor_id, "scenario": "a hard goodbye"})
    room = r.json()
    r = client.post(
        f"/profiles/{profile_id}/rehearsal/{room['id']}/say",
        json={"message": ""})
    assert r.status_code == 422
    assert "rehearses nothing" in r.json()["detail"]
