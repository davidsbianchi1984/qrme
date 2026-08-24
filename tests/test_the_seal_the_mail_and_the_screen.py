"""The seal, the mail server, the room's ear, the wall screen, the plan,
the handoff and the campaign — on the phones.

Seven more blocks off the per-shell doorless record, and what they share
is an audience that is not the owner sitting at the console: the person
*accepting* a signature, the admin proving mail can actually leave the
box, whoever walks into a room or past a wall panel, the account holder
reading what their plan reaches, the provider on the far end of a
handoff, and a donor arriving from a beacon scan with no account at all.
Every one of those people is holding a phone, and until this cut the
phone had no door.

The rules these screens render rather than invent:

* **A verification asks nothing of this deployment.** No token, no
  lookup; an empty package gets a verdict, not an error, and the
  verdict's notes name the field it was missing.
* **The mail read is public and the write is the deployment's.** Anyone
  may see where mail would go; only the signup key changes it, and the
  password never comes back out.
* **The disclosure is readable exactly where the microphone is.** In
  the room — not by strangers who merely know the id.
* **What a screen shows is public on purpose; what it may never show is
  published too.** And only the owner changes or removes it.
* **A lapsed plan keeps its profiles.** Cancelling is becoming a
  visitor, not being erased.
* **A handoff exists only by consent, opens only by its token, and dies
  when revoked.**
* **A donation needs no token; closing the campaign needs the owner.**
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402

from tests.test_capabilities import (as_interactor, auth_header,  # noqa: F401,E501
                                     make_profile, pdi_pair)
from tests.test_signatures import _enroll, _sign, _token
from . import ratchets, shelltables

REPO = Path(__file__).resolve().parent.parent


def _person(client, name="Sam"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code == 201, r.text
    body = r.json()
    return body["id"], {"authorization": f"Bearer {body['token']}"}


# -- the seal ---------------------------------------------------------------

def test_the_certificate_is_public_and_the_refusal_teaches(client):
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth)
    sig_id = res.json()["signature_id"]
    # The person accepting a signature has no account here — the
    # certificate answers a bare GET, in words a person can read.
    cert = client.get(f"/signatures/{sig_id}/certificate",
                      headers={"authorization": ""})
    assert cert.status_code == 200, cert.text
    assert cert.json()["printed_name"] == "Dana Reyes"
    # The phone's verify button posts whatever was pasted. A package
    # with nothing in it is answered, not erred: invalid, with a note
    # that names the missing field — the verdict is the screen's
    # documentation of what belongs in the box.
    r = client.post("/signatures/verify", json={"package": {}})
    assert r.status_code == 200
    verdict = r.json()
    assert verdict["valid"] is False
    assert any("`assertion`" in n for n in verdict["notes"])


# -- the mail server --------------------------------------------------------

def test_the_mail_read_is_public_and_the_write_is_the_deployments(client):
    body = client.get("/settings/mail",
                      headers={"authorization": ""}).json()
    assert body["transport"] == "console"
    assert "password" not in body
    os.environ["QRME_SIGNUP_KEY"] = "deployment-secret"
    try:
        refused = client.put("/settings/mail",
                             json={"host": "smtp.example.test"})
        assert refused.status_code == 403
        assert client.post("/settings/mail/test",
                           json={"to": "a@b.test"}).status_code == 403
        r = client.put("/settings/mail",
                       json={"host": "smtp.example.test", "port": 587,
                             "sender": "me@example.test",
                             "password": "app-password"},
                       headers={"x-signup-key": "deployment-secret"})
        assert r.status_code == 200, r.text
        # The password went in and never comes back out.
        seen = client.get("/settings/mail").json()
        assert seen["password_set"] is True
        assert "app-password" not in str(seen)
        assert client.delete(
            "/settings/mail",
            headers={"x-signup-key": "deployment-secret"}).status_code == 200
    finally:
        del os.environ["QRME_SIGNUP_KEY"]
        client.delete("/settings/mail")


# -- the room's ear ---------------------------------------------------------

def test_the_disclosure_is_readable_exactly_where_the_mic_is(client):
    p = make_profile(client)
    uid, mine = _person(client, "Sam")
    room = client.post("/rooms", json={
        "topic": "the quarterly numbers", "channel": "voice",
        "participants": [{"kind": "profile", "id": p["id"]},
                         {"kind": "user", "id": uid}]}).json()
    # The list of doors is public; where the microphones are is not.
    listed = client.get("/rooms", headers={"authorization": ""}).json()
    assert any(r["id"] == room["id"] for r in listed)
    _sid, stranger = _person(client, "Stranger")
    assert client.get(f"/rooms/{room['id']}/mic",
                      headers=stranger).status_code == 403
    lent = client.post(f"/rooms/{room['id']}/mic",
                       json={"interactor_id": uid}, headers=mine)
    assert lent.status_code == 201, lent.text
    seen = client.get(f"/rooms/{room['id']}/mic", headers=mine).json()
    assert len(seen["microphones_lent"]) == 1
    # Somebody else cannot hand your microphone back either.
    assert client.delete(f"/rooms/{room['id']}/mic/{uid}",
                         headers=stranger).status_code == 403
    assert client.delete(f"/rooms/{room['id']}/mic/{uid}",
                         headers=mine).status_code == 200


# -- the wall screen --------------------------------------------------------

def test_the_screen_reads_public_and_answers_to_its_owner(client):
    vocab = client.get("/displays/vocabulary",
                       headers={"authorization": ""}).json()
    assert vocab["never"] and vocab["rules"]
    p = make_profile(client)
    made = client.post(f"/profiles/{p['id']}/displays",
                       json={"kind": "wall_panel", "label": "the lobby"},
                       headers=auth_header(p))
    assert made.status_code == 201, made.text
    did = made.json()["id"]
    # What it shows is public on purpose — whoever walks past can ask.
    assert client.get(f"/displays/{did}",
                      headers={"authorization": ""}).status_code == 200
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.put(f"/displays/{did}/faces",
                      json={"faces": ["presence"]},
                      headers=auth_header(q)).status_code == 403
    assert client.put(f"/displays/{did}/faces",
                      json={"faces": ["presence"]},
                      headers=auth_header(p)).status_code == 200
    assert client.delete(f"/displays/{did}",
                         headers=auth_header(q)).status_code == 403
    assert client.delete(f"/displays/{did}",
                         headers=auth_header(p)).status_code == 200


# -- the plan ---------------------------------------------------------------

def test_cancelling_a_membership_keeps_the_profiles(client):
    p = make_profile(client, plan="basic")
    account = "owner-1"
    head = auth_header(p)
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    # The statement is the account holder's, not anyone with a token.
    assert client.get(f"/memberships/{account}",
                      headers=auth_header(q)).status_code == 403
    r = client.post(f"/memberships/{account}", json={"plan": "pro"},
                    headers=head)
    assert r.status_code == 200, r.text
    assert client.get(f"/memberships/{account}",
                      headers=head).json()["plan"] == "pro"
    out = client.delete(f"/memberships/{account}", headers=head)
    assert out.status_code == 200, out.text
    # The account became a visitor — and the work is still there.
    assert client.get(f"/memberships/{account}",
                      headers=head).json()["plan"] == "visitor"
    assert client.get(f"/profiles/{p['id']}").status_code == 200


# -- the handoff ------------------------------------------------------------

def test_a_handoff_needs_consent_and_a_token_and_dies_revoked(pdi_pair):
    client, _fake = pdi_pair
    uid, _mine = _person(client, "Theo")
    doc = make_profile(client, display_name="Dr. Rivera",
                       persona="A calm mental-health specialist.",
                       purpose="companion_coach")
    client.post(f"/profiles/{doc['id']}/chat",
                json={"interactor_id": uid, "message": "the panic is back"})
    provider = client.post("/providers", json={
        "name": "Riverside Behavioral Health", "area": "mental_health",
        "location": "12 Main St", "contact": "+1 555 0100"}).json()
    assert client.post("/handoffs", json={
        "interactor_id": uid, "provider_id": provider["id"],
        "profile_id": doc["id"]}).status_code == 403
    handoff = client.post("/handoffs", json={
        "interactor_id": uid, "provider_id": provider["id"],
        "profile_id": doc["id"], "consent": True}).json()
    assert client.get(f"/handoffs/{handoff['id']}",
                      params={"token": "wrong"}).status_code == 403
    opened = client.get(f"/handoffs/{handoff['id']}",
                        params={"token": handoff["token"]})
    assert opened.status_code == 200, opened.text
    client.delete(f"/handoffs/{handoff['id']}")
    assert client.get(f"/handoffs/{handoff['id']}",
                      params={"token": handoff["token"]}).status_code == 403


# -- the campaign -----------------------------------------------------------

def test_a_donation_needs_no_token_and_close_is_the_owners(client):
    p = make_profile(client)
    client.put(f"/profiles/{p['id']}/proceeds", json={
        "designees": [{"name": "June", "kind": "loved_one", "share": 100}]},
        headers=auth_header(p))
    made = client.post(f"/profiles/{p['id']}/campaigns",
                       json={"title": "Keep the garden going",
                             "goal": 1000.0, "cause": "the garden"},
                       headers=auth_header(p))
    assert made.status_code == 201, made.text
    cid = made.json()["id"]
    # A donor arriving from a beacon scan has no account. Requiring one
    # gates generosity behind signup, so the door takes a bare POST.
    give = client.post(f"/campaigns/{cid}/donate",
                       json={"amount": 25.0, "on_behalf_of": "a passerby"},
                       headers={"authorization": ""})
    assert give.status_code == 201, give.text
    card = client.get(f"/campaigns/{cid}",
                      headers={"authorization": ""}).json()
    assert card["raised"] == 25.0
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.post(f"/campaigns/{cid}/close",
                       headers=auth_header(q)).status_code == 403
    assert client.post(f"/campaigns/{cid}/close",
                       headers=auth_header(p)).status_code == 200


# -- the doors and their languages ------------------------------------------

def test_every_shell_has_doors_on_all_seven_blocks(client):
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("GET", "/signatures/x/certificate") in made, \
            f"{lang.name}: the certificate is unreadable"
        assert ("GET", "/settings/mail") in made, \
            f"{lang.name}: nobody can see where mail goes"
        assert ("GET", "/rooms") in made, \
            f"{lang.name}: the rooms have no list"
        assert ("GET", "/displays/vocabulary") in made, \
            f"{lang.name}: the wall's limits are unreadable"
        assert ("GET", "/memberships/x") in made, \
            f"{lang.name}: the plan is unreadable"
        assert ("POST", "/handoffs") in made, \
            f"{lang.name}: no handoff door"
        assert ("POST", "/campaigns/x/donate") in made, \
            f"{lang.name}: the donor has no door"


def test_the_seven_blocks_speak_ten_languages_on_every_shell(client):
    """Every sig/mail/room/disp/member/hand/camp key the iOS table
    carries, complete on all three shells — the full-list rule, never a
    sample."""
    keys = shelltables.ios_keys("seal")
    assert len(keys) >= ratchets.floor("l10n.block.seal"), \
        f"the iOS table lost rows: {len(keys)}"
    problems = shelltables.missing_rows(keys)
    assert not problems, (
        f"{len(problems)} gap(s) in the shell tables:\n    "
        + "\n    ".join(problems[:12]))
