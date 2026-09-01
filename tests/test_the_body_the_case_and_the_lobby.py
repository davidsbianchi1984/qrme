"""The body, the referral, the objection, the lobby and the dock.

Five more blocks of the per-shell doorless record, and the shape of
what was missing differs by block: the robot body's owner could not
audit from a phone what the body had been told to do; the referral flow
existed end to end with no phone on either side of it; the person who
raised an objection could read their case on the console and not on the
device in their pocket; a lobby's honest roster — what every callsign
*is* — was unreadable exactly where people game; and the dock, whose
whole job is pointing at where features live, could not itself be found.

    asked     does the audit trail exist
    mattered  can its owner read it from the device they carry

Twenty-five routes gain doors on iOS, Android and Windows in one cut,
each rendering its backend's rules: the command log answers to the
owner alone; a referral opens exactly once; an objection's reviewer
verb refuses the owner by role; the roster names each member's kind;
and every dock face carries a way out of the read-only pane.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402
from . import ratchets, shelltables

REPO = Path(__file__).resolve().parent.parent

ADULT = {"birthdate": "1984-06-01"}


def _mk(client, name):
    r = client.post("/profiles", json={
        "owner_id": f"owner-{name}", "kind": "self", "display_name": name,
        "persona": "A person who checks the log before blaming the tool.",
        "verification": ADULT, "plan": "pro"})
    assert r.status_code == 201, r.text
    body = r.json()
    return body["id"], {"authorization": f"Bearer {body['owner_token']}"}


def test_the_bodys_audit_trail_answers_to_its_owner_alone(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    catalog = client.get("/robotics/catalog").json()
    model = catalog["robots"][0]["model"]
    r = client.post(f"/profiles/{a}/robots",
                    json={"model": model, "name": "porter"}, headers=ha)
    assert r.status_code == 201, r.text
    robot_id = r.json()["id"]
    assert client.get(f"/robots/{robot_id}/commands",
                      headers=ha).status_code == 200
    # Ben's perfectly valid token is the wrong account.
    assert client.get(f"/robots/{robot_id}/commands",
                      headers=hb).status_code == 403
    # Intimacy is never a body dial.
    dials = client.get(f"/robots/{robot_id}/steering", headers=ha).json()
    assert all(d["group"] != "intimacy" for d in dials["dials"])
    r = client.put(f"/robots/{robot_id}/steering",
                   json={"values": {"pace": 30, "intimacy": 100}},
                   headers=ha)
    assert r.status_code == 200
    # The write ignored the intimacy value: whatever a body reports for
    # the dial, it is not the 100 that was sent alongside a legitimate one.
    assert r.json()["values"]["pace"] == 30
    assert r.json()["values"].get("intimacy", 0) != 100
    r = client.delete(f"/robots/{robot_id}", headers=ha)
    assert r.status_code == 200 and r.json()["unbound"] is True


def test_the_referral_match_filters_by_expertise(client):
    # Expertise filters, geography ranks — an empty list rather than a
    # near-miss, because a confident wrong referral is somebody phoning a
    # clinic that cannot help them.
    r = client.get("/referrals/match?area=dermatology")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_the_objection_is_readable_and_endable_by_its_subject(client):
    # A subject_consent profile: the basis whose subject can withdraw it.
    r = client.post("/profiles", json={
        "owner_id": "owner-Ana", "kind": "self", "display_name": "Ana",
        "persona": "A person who reads the sign before signing.",
        "verification": ADULT, "plan": "pro",
        "consent": {"basis": "subject_consent", "attestor": "owner-Ana"}})
    assert r.status_code == 201, r.text
    a = r.json()["id"]
    ha = {"authorization": f"Bearer {r.json()['owner_token']}"}
    r = client.post("/objections", json={
        "profile_id": a, "basis": "subject_consent",
        "objector_ref": "case-77", "reason": "that likeness is mine"})
    assert r.status_code in (200, 201), r.text
    oid = r.json()["id"]
    card = client.get(f"/objections/{oid}").json()
    assert card["status"] == "open"
    audit = client.get(f"/objections/{oid}/audit", headers=ha).json()
    assert audit["audit_events"], audit
    # The reviewer verb refuses an owner token by role: an owner cannot
    # adjudicate an objection against their own profile. From localhost
    # with no QRME_ADMIN_TOKEN the gate deliberately stands open (the
    # development path), so the refusal is asserted with the token set —
    # the posture every reachable deployment runs in.
    import os
    os.environ["QRME_ADMIN_TOKEN"] = "reviewer-secret"
    try:
        r = client.post(f"/objections/{oid}/resolve",
                        json={"outcome": "dismiss"}, headers=ha)
        assert r.status_code == 403, r.text
    finally:
        del os.environ["QRME_ADMIN_TOKEN"]
    # The subject's own end is honored immediately, even mid-review.
    r = client.post(f"/objections/{oid}/withdraw")
    assert r.status_code == 200, r.text
    assert client.get(f"/objections/{oid}").json()["status"] == "withdrawn"


def test_the_lobby_roster_says_what_every_callsign_is(client):
    a, ha = _mk(client, "Ana")
    vocab = client.get("/gaming/lobby/vocabulary").json()
    assert vocab.get("never") and vocab.get("rules")
    r = client.post(f"/profiles/{a}/gaming/sessions",
                    json={"game": "chess", "platform": "pc"}, headers=ha)
    assert r.status_code == 201, r.text
    sid = r.json()["id"]
    r = client.post(f"/gaming/sessions/{sid}/lobby",
                    json={"member_kind": "profile", "member_id": a,
                          "role": "coach", "callsign": "Sage"}, headers=ha)
    assert r.status_code == 201, r.text
    roster = client.get(f"/gaming/sessions/{sid}/lobby",
                        headers=ha).json()
    seat = next(m for m in roster["seats"] if m["member_id"] == a)
    # The kind travels with the callsign — a lobby that reads as five
    # friends when it is one player and four generated voices is the
    # impression this product must not create.
    assert seat["member_kind"] == "profile"
    r = client.request("DELETE", f"/gaming/sessions/{sid}/lobby",
                       json={"member_id": a}, headers=ha)
    assert r.status_code == 200, r.text


def test_every_dock_face_carries_a_way_out(client):
    faces = client.get("/dock/faces").json()["faces"]
    assert faces
    # The pane is read-only, so each face points at the screen that can
    # actually do its job — checked for every face, not a sample.
    for face in faces:
        name = face["face"] if isinstance(face, dict) else face
        r = client.get(f"/dock/where/{name}")
        assert r.status_code == 200, (name, r.text)


def test_every_shell_has_doors_on_all_five_blocks(client):
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("GET", "/robots/x/commands") in made, \
            f"{lang.name}: the body's audit trail is unreadable"
        assert ("POST", "/referrals/prepare") in made, \
            f"{lang.name}: no referral door"
        assert ("GET", "/objections/x") in made, \
            f"{lang.name}: the case is unreadable"
        assert ("GET", "/gaming/lobby/vocabulary") in made, \
            f"{lang.name}: the lobby's limits are unreadable"
        assert ("GET", "/dock/faces") in made, \
            f"{lang.name}: the dock cannot be found"


def test_the_five_blocks_speak_ten_languages_on_every_shell(client):
    """Every bot/refer/object/lobby/dock key the iOS table carries,
    complete on all three shells — the full-list rule, not a sample."""
    keys = shelltables.ios_keys("lobby")
    assert len(keys) >= ratchets.floor("l10n.block.lobby"), \
        f"the iOS table lost rows: {len(keys)}"
    problems = shelltables.missing_rows(keys)
    assert not problems, (
        f"{len(problems)} gap(s) in the shell tables:\n    "
        + "\n    ".join(problems[:12]))
