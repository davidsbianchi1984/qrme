"""The place, the camera, the organization and the tour reach the phones.

Four more blocks of the per-shell doorless record. The phone could stand
in a room and not know whose corner it was, who had lent a microphone
into it, or who was wearing what over their face — the disclosures the
console has rendered since the live-place round, each addressed to
everyone present precisely because a disclosure only its subject can
see is not a disclosure. The camera existed with published refusals no
phone could read. The owner's organization could coordinate and the
phone could not found one. The guided tour could not be opened from the
device most likely to be in a new user's hand.

    asked     is the disclosure served
    mattered  can the person standing in the place read it

Twenty-seven routes gain doors on iOS, Android and Windows in one cut,
with the round's rules kept rather than invented: the camera opens with
its refusals shown verbatim; only the holder opens a session and either
party alone closes it; the organization answers only to its owner's
account; and the tour is anybody's, learner id or no account at all.
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
        "persona": "A person who reads the sign on the door before opening.",
        "verification": ADULT, "plan": "pro"})
    assert r.status_code == 201, r.text
    body = r.json()
    return body["id"], {"authorization": f"Bearer {body['owner_token']}"}


def test_whose_corner_answers_before_anything_else(client):
    a, ha = _mk(client, "Ana")
    desk = client.post("/desks", json={
        "owner_id": "owner-Ana", "display_name": "Ana's desk",
        "trade": "design", "attestor": "owner-Ana",
        "basis": "long acquaintance"}, headers=ha).json()
    r = client.get(f"/places/desk/{desk['desk_id']}/whose")
    assert r.status_code == 200, r.text
    assert r.json().get("display_name")
    # An invented surface is named in the refusal, choices included.
    r = client.get(f"/places/backstage/{desk['desk_id']}/whose")
    assert r.status_code == 422 and "backstage" in r.text


def test_the_camera_publishes_its_refusals_and_the_holder_holds_it(client):
    vocab = client.get("/camera/vocabulary").json()
    assert vocab.get("never"), vocab
    r = client.get("/camera/bystanders/place")
    assert r.status_code == 200, r.text
    # Only the holder opens a session: a camera opened *for* somebody by
    # somebody else is a camera turned on remotely.
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    r = client.post("/camera/sessions", json={
        "holder_id": b, "surface": "room", "surface_id": "rm-1",
        "subject": "object", "viewer_kind": "person", "viewer_id": a,
        "minutes": 5}, headers=ha)
    assert r.status_code == 403, r.text


def test_the_organization_answers_to_its_owner_alone(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    org = client.post("/organizations", json={"name": "Ana & Co"},
                      headers=ha).json()
    assert org.get("id"), org
    mine = client.get("/organizations", headers=ha).json()
    assert any(o["id"] == org["id"] for o in mine)
    # Ben holds a perfectly good token for the wrong account.
    r = client.get(f"/organizations/{org['id']}", headers=hb)
    assert r.status_code == 403, r.text
    log = client.get(f"/organizations/{org['id']}/coordinations",
                     headers=ha).json()
    assert log == []


def test_the_tour_opens_for_anybody_and_remembers_where_they_are(client):
    outline = client.get("/tutorial").json()
    chapters = outline.get("chapters") or outline.get("lessons")
    assert chapters, outline
    r = client.post("/tutorial/start", json={"learner_id": "walk-in",
                                             "lesson": ""})
    assert r.status_code == 200, r.text
    progress = client.get("/tutorial/progress/walk-in").json()
    assert progress, progress


def test_every_shell_has_doors_on_all_four_blocks(client):
    """One representative door per block per shell — the ratchet counts
    the rest."""
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("GET", "/places/x/x/whose") in made, \
            f"{lang.name}: whose corner is unreadable"
        assert ("GET", "/places/x/x/microphone") in made, \
            f"{lang.name}: the microphone disclosure is unreadable"
        assert ("POST", "/camera/sessions") in made, \
            f"{lang.name}: no camera door"
        assert ("GET", "/camera/vocabulary") in made, \
            f"{lang.name}: the camera's refusals are unreadable"
        assert ("POST", "/organizations") in made, \
            f"{lang.name}: no organization door"
        assert ("POST", "/tutorial/start") in made, \
            f"{lang.name}: the tour cannot begin"


def test_the_place_speaks_ten_languages_on_every_shell(client):
    """Every place/cam/org/tut key the iOS table carries, complete on all
    three shells — the full-list rule the 0.43.2 injection taught."""
    keys = shelltables.ios_keys("place")
    assert len(keys) >= ratchets.floor("l10n.block.place"), \
        f"the iOS table lost rows: {len(keys)}"
    problems = shelltables.missing_rows(keys)
    assert not problems, (
        f"{len(problems)} gap(s) in the shell tables:\n    "
        + "\n    ".join(problems[:12]))
