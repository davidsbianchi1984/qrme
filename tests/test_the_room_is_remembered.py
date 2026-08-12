"""The room is remembered, not just heard — spec clause 1's environmental
adaptation, finished.

Environment context sent with a turn was already stored and rendered into
the prompt; but the stored rows were never read back, so a turn without
fresh data forgot the room the table remembered. Now a turn without
environment reads the latest stored context — recent only — and the echo
marks it `remembered`, so a client can tell fresh data from recalled data.
"""

from datetime import datetime, timedelta, timezone

from qrme import db
from tests.test_capabilities import make_profile


def _chat(client, p, who, message, **extra):
    r = client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": who, "message": message, **extra})
    assert r.status_code == 200, r.text
    return r.json()


def test_a_turn_without_environment_reads_the_last_room(client):
    p = make_profile(client)
    who = client.post("/interactors", json={"display_name": "Ana"}).json()["id"]

    first = _chat(client, p, who, "hello from the garden",
                  environment={"location": "garden", "conditions": "sunny"})
    assert first["environment"] == {"location": "garden",
                                    "conditions": "sunny"}

    second = _chat(client, p, who, "and now just chatting")
    assert second["environment"]["location"] == "garden"
    assert second["environment"]["remembered"] is True


def test_fresh_environment_beats_the_remembered_one(client):
    p = make_profile(client)
    who = client.post("/interactors", json={"display_name": "Ben"}).json()["id"]
    _chat(client, p, who, "at home", environment={"location": "home"})
    moved = _chat(client, p, who, "on the move",
                  environment={"location": "train"})
    assert moved["environment"] == {"location": "train"}
    assert "remembered" not in moved["environment"]


def test_yesterdays_cafe_is_not_remembered(client):
    p = make_profile(client)
    who = client.post("/interactors", json={"display_name": "Cara"}).json()["id"]
    _chat(client, p, who, "at the café", environment={"location": "café"})
    # Age the stored context past the six-hour window.
    conn = db.connect()
    old = (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat()
    conn.execute("UPDATE environment_context SET created_at=?", (old,))
    conn.commit()
    later = _chat(client, p, who, "good morning")
    assert later["environment"] is None
