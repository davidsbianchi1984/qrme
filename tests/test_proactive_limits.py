"""Proactive-outreach anti-spam: per-relationship rate cap, recipient
quiet-hours, and suppression until the recipient replies."""

from datetime import datetime, timedelta, timezone

from qrme import db
from tests.test_capabilities import as_owner, make_interactor, make_profile


def _proactive_profile(client):
    return make_profile(client, interaction_scope="proactive")


def test_rate_cap_blocks_a_second_outreach_within_the_window(client):
    p = _proactive_profile(client)
    user = make_interactor(client)
    assert client.post(f"/profiles/{p['id']}/proactive/{user}").status_code == 200
    # A second immediate outreach is rate-capped.
    second = client.post(f"/profiles/{p['id']}/proactive/{user}")
    assert second.status_code == 429


def test_reply_lifts_suppression_but_rate_cap_still_applies(client):
    # interval 0h isolates the awaiting-reply rule from the rate cap.
    p = _proactive_profile(client)
    as_owner(client, p)
    client.patch(f"/profiles/{p['id']}", json={"proactive_min_interval_hours": 0})
    user = make_interactor(client)

    assert client.post(f"/profiles/{p['id']}/proactive/{user}").status_code == 200
    # Still awaiting a reply → suppressed even with a 0h rate cap.
    assert client.post(f"/profiles/{p['id']}/proactive/{user}").status_code == 429
    # The recipient replies…
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": "hi back"})
    # …now outreach is allowed again.
    assert client.post(f"/profiles/{p['id']}/proactive/{user}").status_code == 200


def test_rate_cap_allows_again_after_the_interval(client):
    p = _proactive_profile(client)
    user = make_interactor(client)
    client.post(f"/profiles/{p['id']}/proactive/{user}")
    # Simulate 25h passing and a prior reply (clear the awaiting flag).
    past = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
    conn = db.connect()
    conn.execute("UPDATE proactive_state SET last_outreach_at=?, awaiting_reply=0"
                 " WHERE profile_id=? AND interactor_id=?", (past, p["id"], user))
    conn.commit()
    assert client.post(f"/profiles/{p['id']}/proactive/{user}").status_code == 200


def test_quiet_hours_suppress_outreach(client):
    p = _proactive_profile(client)
    user = make_interactor(client)
    who = client.post("/interactors",
                      json={"display_name": "Q"}).json()
    quiet_user, tok = who["id"], who["token"]

    # Set a quiet window covering the current UTC hour.
    now_h = datetime.now(timezone.utc).hour
    client.put(f"/interactors/{quiet_user}/quiet-hours",
               json={"quiet_start": now_h, "quiet_end": (now_h + 1) % 24},
               headers={"authorization": f"Bearer {tok}"})
    as_owner(client, p)
    blocked = client.post(f"/profiles/{p['id']}/proactive/{quiet_user}")
    assert blocked.status_code == 429

    # A window that does not cover now allows outreach.
    client.put(f"/interactors/{quiet_user}/quiet-hours",
               json={"quiet_start": (now_h + 2) % 24, "quiet_end": (now_h + 3) % 24},
               headers={"authorization": f"Bearer {tok}"})
    as_owner(client, p)
    assert client.post(
        f"/profiles/{p['id']}/proactive/{quiet_user}").status_code == 200


def test_quiet_hours_require_the_interactors_own_token(client):
    make_profile(client)                       # sets an owner token as default
    user = make_interactor(client)
    # The owner token is not the interactor's — quiet hours are the recipient's.
    r = client.put(f"/interactors/{user}/quiet-hours",
                   json={"quiet_start": 0, "quiet_end": 6})
    assert r.status_code == 403
