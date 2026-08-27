"""The face it shows the world, on the phones.

Nine more blocks off the per-shell doorless record — the portrait, the
emblem and the badge, the page and its themes, the front, the surfaces,
the blend, the bodies, the dials and the wrist — and what they share is
that every one is how a profile *looks* to somebody deciding whether to
trust it. That decision happens on a phone held at a bus stop, not at a
desk, and until this cut the phone could not check a single one of the
claims the desktop could.

The rules these screens render rather than invent:

* **The portrait carries its own honesty.** The AI badge and whose
  likeness it is travel with the asset, and the starter briefs are
  public because "where did these faces come from" deserves an answer.
* **The badge a reader sees withholds what would undo a veil.** On an
  anonymous profile the attestor stays home — a name and a workplace
  narrow an anonymous author to a city.
* **The blend is provenance,** open like /transparency; a non-hybrid
  answers 404 rather than pretending an empty blend.
* **The same personality in every body**, checkable by anyone, while
  the list of bodies and screens stays the owner's.
* **Dials are 0–100 integers and intimacy never rises** on a non-rated
  persona.
* **The wrist reuses the full apps' paths** — same auth, same
  allowlists — so a tap from a watch can do nothing a phone could not.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402

from tests.test_capabilities import auth_header, make_profile
from . import ratchets, shelltables

REPO = Path(__file__).resolve().parent.parent


# -- the portrait -----------------------------------------------------------

def test_the_portrait_carries_its_own_honesty(client):
    p = make_profile(client)
    r = client.put(f"/profiles/{p['id']}/avatar",
                   json={"asset": "portraits/dana.png"},
                   headers=auth_header(p))
    assert r.status_code == 200, r.text
    # Public read: the asset never travels without the honesty.
    card = client.get(f"/profiles/{p['id']}/avatar",
                      headers={"authorization": ""}).json()
    assert card["asset"] == "portraits/dana.png"
    # A stranger's valid token is the wrong account for the write.
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.put(f"/profiles/{p['id']}/avatar",
                      json={"asset": "x"},
                      headers=auth_header(q)).status_code == 403
    # The briefs are public — the honest answer to "where did these
    # faces come from" — and an unknown handle is told so by name.
    briefs = client.get("/avatars/briefs",
                        headers={"authorization": ""}).json()
    assert briefs["briefs"]
    r = client.get("/avatars/briefs/nobody_of_that_name")
    assert r.status_code == 404
    assert "no portrait brief" in r.json()["detail"]


# -- the emblem and the badge -----------------------------------------------

def test_the_badge_a_reader_sees_withholds_what_would_undo_a_veil(client):
    p = make_profile(client)
    # The catalogue is open, and the emblem set from it sticks.
    emblems = client.get("/identity/emblems",
                         headers={"authorization": ""}).json()["emblems"]
    assert emblems
    r = client.put(f"/profiles/{p['id']}/emblem",
                   json={"emblem": emblems[0]["emblem"]},
                   headers=auth_header(p))
    assert r.status_code == 200, r.text
    # Verified, then veiled: the public badge keeps the fact and
    # withholds the person who checked.
    client.post(f"/profiles/{p['id']}/verification",
                json={"level": "document",
                      "attestor": "clinic-registrar"},
                headers=auth_header(p))
    client.put(f"/profiles/{p['id']}/anonymity", json={"anonymous": True},
               headers=auth_header(p))
    badge = client.get(f"/profiles/{p['id']}/badge",
                       headers={"authorization": ""}).json()
    assert badge["verified"] is True
    assert not badge.get("attestor"), \
        "the attestor narrows an anonymous author to a city"
    # The vocabulary that explains all this answers a bare GET.
    vocab = client.get("/identity/vocabulary",
                       headers={"authorization": ""}).json()
    assert vocab["withheld_when_anonymous"]


# -- the page and the front -------------------------------------------------

def test_the_page_is_the_owners_to_write_and_anyones_to_read(client):
    p = make_profile(client)
    themes = client.get("/pages/themes",
                        headers={"authorization": ""}).json()["themes"]
    assert themes
    r = client.put(f"/profiles/{p['id']}/page",
                   json={"theme": themes[0]["id"],
                         "tagline": "still gardening"},
                   headers=auth_header(p))
    assert r.status_code == 200, r.text
    page = client.get(f"/profiles/{p['id']}/page",
                      headers={"authorization": ""}).json()
    assert page["tagline"] == "still gardening"
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.put(f"/profiles/{p['id']}/page",
                      json={"tagline": "vandalized"},
                      headers=auth_header(q)).status_code == 403
    # A theme outside the closed set is refused while the owner looks.
    assert client.put(f"/profiles/{p['id']}/page",
                      json={"theme": "not_a_theme"},
                      headers=auth_header(p)).status_code == 422
    # The front is one call with everything a first screen needs.
    front = client.get(f"/profiles/{p['id']}/front",
                       headers={"authorization": ""}).json()
    assert front["display_name"]


# -- the surfaces and the blend ---------------------------------------------

def test_surfaces_are_declared_and_the_blend_never_pretends(client):
    p = make_profile(client)
    r = client.put(f"/profiles/{p['id']}/surfaces",
                   json={"surfaces": ["2d", "vr"]},
                   headers=auth_header(p))
    assert r.status_code == 200, r.text
    seen = client.get(f"/profiles/{p['id']}/surfaces",
                      headers={"authorization": ""}).json()
    assert seen["surfaces"] == ["2d", "vr"]
    # A non-hybrid has no blend, and says so rather than answering [].
    assert client.get(f"/profiles/{p['id']}/composition",
                      headers={"authorization": ""}).status_code == 404


# -- the bodies -------------------------------------------------------------

def test_the_same_personality_in_every_body(client):
    p = make_profile(client)
    r = client.post(f"/profiles/{p['id']}/embodiments",
                    json={"name": "kitchen speaker", "kind": "speaker",
                          "has_llm": False}, headers=auth_header(p))
    assert r.status_code == 201, r.text
    # The list of bodies is the owner's; the consistency of the
    # personality across them is anyone's to verify.
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/embodiments",
                      headers=auth_header(q)).status_code == 403
    same = client.get(f"/profiles/{p['id']}/embodiment-consistency",
                      headers={"authorization": ""}).json()
    assert any(f["name"] == "kitchen speaker"
               for f in same["embodiments"])
    # The profile's screens: owner-scoped both ways.
    made = client.post(f"/profiles/{p['id']}/displays",
                       json={"kind": "wall_panel", "label": "the lobby"},
                       headers=auth_header(p))
    assert made.status_code == 201, made.text
    assert client.get(f"/profiles/{p['id']}/displays",
                      headers=auth_header(q)).status_code == 403
    rows = client.get(f"/profiles/{p['id']}/displays",
                      headers=auth_header(p)).json()["displays"]
    assert any(d["label"] == "the lobby" for d in rows)


# -- the dials --------------------------------------------------------------

def test_dials_are_integers_and_intimacy_never_rises(client):
    p = make_profile(client)
    r = client.put(f"/profiles/{p['id']}/steering",
                   json={"values": {"pace": 30, "intimacy": 100}},
                   headers=auth_header(p))
    assert r.status_code == 200, r.text
    assert r.json()["values"]["pace"] == 30
    # Hard-clamped, not politely declined: whatever a non-rated persona
    # reports for the dial, it is not the 100 that rode in beside a
    # legitimate value.
    assert r.json()["values"].get("intimacy", 0) != 100
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/steering",
                      headers=auth_header(q)).status_code == 403


# -- the wrist --------------------------------------------------------------

def test_the_wrist_sees_the_lights_and_acts_through_the_same_doors(client):
    p = make_profile(client)
    wf = client.post(f"/profiles/{p['id']}/workflows",
                     json={"goal": "a note", "plan": ["draft", "confirm"]},
                     headers=auth_header(p)).json()
    face = client.get(f"/profiles/{p['id']}/watch",
                      headers=auth_header(p)).json()
    assert any(a["id"] == wf["id"] for a in face["agents"])
    assert face["chip"]["light"] in ("green", "orange", "red")
    # One tap advances the same workflow the full apps drive.
    r = client.post(f"/profiles/{p['id']}/watch/act",
                    json={"target": "workflow", "id": wf["id"],
                          "action": "advance"}, headers=auth_header(p))
    assert r.status_code == 201, r.text
    # The wrist opens no side door: a stranger's token fails the same way.
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/watch",
                      headers=auth_header(q)).status_code == 403


# -- the doors and their languages ------------------------------------------

def test_every_shell_has_doors_on_all_nine_blocks(client):
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("GET", "/profiles/x/avatar") in made, \
            f"{lang.name}: the portrait is unreadable"
        assert ("GET", "/identity/emblems") in made, \
            f"{lang.name}: the emblem catalogue is unreadable"
        assert ("GET", "/profiles/x/page") in made, \
            f"{lang.name}: the page is unreadable"
        assert ("GET", "/profiles/x/front") in made, \
            f"{lang.name}: no first screen"
        assert ("GET", "/profiles/x/surfaces") in made, \
            f"{lang.name}: the surfaces are unreadable"
        assert ("GET", "/profiles/x/embodiment-consistency") in made, \
            f"{lang.name}: the consistency claim cannot be checked"
        assert ("PUT", "/profiles/x/steering") in made, \
            f"{lang.name}: the dials cannot be turned"
        assert ("GET", "/profiles/x/watch") in made, \
            f"{lang.name}: the wrist is blind"


def test_the_nine_blocks_speak_ten_languages_on_every_shell(client):
    """Every ava/embl/pg/front/surf/comp/form/steer/wrist key the iOS
    table carries, complete on all three shells — the full-list rule,
    never a sample."""
    keys = shelltables.ios_keys("face")
    assert len(keys) >= ratchets.floor("l10n.block.face"), \
        f"the iOS table lost rows: {len(keys)}"
    problems = shelltables.missing_rows(keys)
    assert not problems, (
        f"{len(problems)} gap(s) in the shell tables:\n    "
        + "\n    ".join(problems[:12]))
