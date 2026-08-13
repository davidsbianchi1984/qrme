"""The export handoff: a QR that carries a ticket, never a token.

A field report pointed at the "Take it with you" card and asked for a QR
door. The owner token must never ride in a QR — a code on a screen is
legible to any camera in the room — so the code carries a single-use,
minutes-long ticket that unlocks exactly one read of exactly this
profile's export. These tests hold the ticket to each of those words.
"""

from tests.test_capabilities import auth_header, make_profile


def _ticket(client, me):
    r = client.post(f"/profiles/{me['id']}/export/ticket",
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    return r.json()


def test_the_ticket_serves_the_export_without_a_token(client):
    me = make_profile(client, display_name="Porter")
    t = _ticket(client, me)
    out = client.get(t["url"], headers={})
    assert out.status_code == 200, out.text
    assert out.json()["profile"]["id"] == me["id"]
    assert "tables" in out.json()


def test_one_use_is_the_whole_life(client):
    me = make_profile(client, display_name="Once")
    t = _ticket(client, me)
    assert client.get(t["url"], headers={}).status_code == 200
    again = client.get(t["url"], headers={})
    assert again.status_code == 410
    assert "already been used" in again.json()["detail"]


def test_minting_is_the_owners_act(client):
    me = make_profile(client, display_name="Mine")
    other = make_profile(client, display_name="Other",
                         owner_id="owner-2")
    r = client.post(f"/profiles/{me['id']}/export/ticket",
                    headers=auth_header(other))
    assert r.status_code in (401, 403)


def test_a_ticket_opens_only_its_own_profile(client):
    """A ticket minted for one profile read against another's path is a
    404, not a cross-profile read."""
    me = make_profile(client, display_name="A")
    other = make_profile(client, display_name="B", owner_id="owner-2")
    t = _ticket(client, me)
    r = client.get(f"/profiles/{other['id']}/export/handoff/{t['ticket']}",
                   headers={})
    assert r.status_code == 404


def test_an_expired_ticket_is_refused(client, monkeypatch):
    from qrme import db
    me = make_profile(client, display_name="Late")
    t = _ticket(client, me)
    conn = db.connect()
    conn.execute("UPDATE export_tickets SET expires_at=? WHERE ticket=?",
                 ("2000-01-01T00:00:00+00:00", t["ticket"]))
    conn.commit()
    r = client.get(t["url"], headers={})
    assert r.status_code == 410


def test_the_qr_renders_and_does_not_consume(client):
    """Reading the code is not using the handoff — a phone camera may
    fetch the image any number of times before the scan."""
    me = make_profile(client, display_name="Scan")
    t = _ticket(client, me)
    for _ in range(2):
        qr = client.get(t["qr_svg"], headers={})
        assert qr.status_code == 200
        assert qr.headers["content-type"].startswith("image/svg")
    assert client.get(t["url"], headers={}).status_code == 200


def test_the_owner_token_is_not_in_the_code(client):
    """The whole point: the QR carries the ticket URL and nothing else —
    no bearer token, no owner id beyond the path."""
    me = make_profile(client, display_name="Quiet")
    t = _ticket(client, me)
    svg = client.get(t["qr_svg"], headers={}).text
    assert me["owner_token"] not in svg
    assert me["owner_token"] not in t["url"]
