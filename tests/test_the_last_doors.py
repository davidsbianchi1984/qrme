"""The last doors, and the record they close.

The per-shell doorless records run to **zero**: with this round every
route in the table has a door on iOS, Android and Windows. What was
left was the deepest machinery — the interview a profile is born from,
the hybrid blend, the knowledge packs, the owner's simulations and
fine-tuning, the cloud-contribution ledger, the profile's reach into a
person's day, the license a stranger buys, and the senses (perceive,
the lending vocabulary, the overlays, the experience list).

The rules these screens render rather than invent:

* **A profile is born from an interview,** not a form of toggles — and
  the hybrid records its constituents where anyone can read them.
* **A simulation is the owner's operational insight** — a stranger's
  token opens none of it.
* **The contribution ledger shows what would leave before it leaves,**
  and revoke answers honestly when nothing ever did.
* **The profile initiates only when its owner opted in** — a
  reactive-only profile refuses by name.
* **A rating comes from the person who is rating.** Unauthenticated,
  it moved the engagement score a profile behaves from.
* **A license is bought against an offer,** and a profile not offered
  says so rather than minting a grant.
* **The experience form refuses the field people actually type**
  (`years`) by name, instead of saving a row with no dates.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402

from tests.test_capabilities import (
    as_interactor, auth_header, make_interactor, make_profile,
)

REPO = Path(__file__).resolve().parent.parent


# -- the birth --------------------------------------------------------------

def test_a_profile_is_born_from_an_interview(client):
    r = client.post("/profiles/genesis", json={
        "owner_id": "owner-genesis",
        "verification": {"birthdate": "1990-01-01"},
        "answers": {"social_style": "warm but needs quiet evenings",
                    "humor": "dry, gentle teasing",
                    "what_matters": "family, honesty, the garden",
                    "comfort": "sits with you and listens"}})
    assert r.status_code == 201, r.text
    assert r.json()["display_name"]


def test_the_hybrid_records_its_constituents_in_the_open(client):
    a = make_profile(client, display_name="Grandma Rose")
    b = make_profile(client, display_name="Grandpa Lou")
    r = client.post("/profiles/composite", json={
        "owner_id": "owner-1", "display_name": "The Grandparents",
        "terms_consent": True,
        "verification": {"birthdate": "1990-01-01"},
        "sources": [{"profile_id": a["id"]}, {"profile_id": b["id"]}]})
    assert r.status_code == 201, r.text
    hybrid = r.json()
    blend = client.get(f"/profiles/{hybrid['id']}/composition",
                       headers={"authorization": ""}).json()
    assert blend
    # One constituent is not enough to call it a blend.
    assert client.post("/profiles/composite", json={
        "owner_id": "owner-1", "display_name": "Solo",
        "terms_consent": True,
        "verification": {"birthdate": "1990-01-01"},
        "sources": [{"profile_id": a["id"]}]}).status_code == 422


def test_the_packs_seed_and_publish(client):
    p = make_profile(client)
    seeded = client.post("/packs/seed", json={})
    assert seeded.status_code == 201, seeded.text
    r = client.post("/packs", json={
        "industry": "carpentry", "title": "Joinery basics",
        "items": [{"title": "Mortise and tenon",
                   "content": "Cut the mortise first."}]},
                    headers=auth_header(p))
    assert r.status_code == 201, r.text
    rows = client.get("/packs", headers={"authorization": ""}).json()
    assert any(row["title"] == "Joinery basics" for row in rows)


# -- the mind at work -------------------------------------------------------

def test_a_simulation_is_the_owners_operational_insight(client):
    p = make_profile(client)
    r = client.post(f"/profiles/{p['id']}/simulate",
                    json={"scenario": "a difficult monday"},
                    headers=auth_header(p))
    assert r.status_code == 201, r.text
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.post(f"/profiles/{p['id']}/simulate",
                       json={"scenario": "x"},
                       headers=auth_header(q)).status_code == 403
    runs = client.get(f"/profiles/{p['id']}/simulations",
                      headers=auth_header(p)).json()
    assert len(runs) == 1
    assert client.get(f"/profiles/{p['id']}/simulations",
                      headers=auth_header(q)).status_code == 403


def test_the_ledger_is_honest_when_nothing_ever_left(client):
    p = make_profile(client)
    view = client.get(f"/profiles/{p['id']}/cloud-contribution",
                      headers=auth_header(p)).json()
    assert view["opted_in"] is False
    r = client.post(f"/profiles/{p['id']}/cloud-contribution/revoke",
                    json={}, headers=auth_header(p))
    assert r.status_code == 200, r.text
    assert r.json()["deleted_at_gateway"] is True, \
        "nothing ever left, and the revoke should say so plainly"


# -- the reach --------------------------------------------------------------

def test_a_reactive_profile_refuses_to_initiate_by_name(client):
    p = make_profile(client)
    who = make_interactor(client)
    r = client.post(f"/profiles/{p['id']}/proactive/{who}",
                    headers=auth_header(p))
    assert r.status_code == 403
    assert "reactive-only" in r.json()["detail"]


def test_a_rating_comes_from_the_person_who_is_rating(client):
    p = make_profile(client)
    who = make_interactor(client)
    # No token at all: refused — open, this pushed a stranger's
    # exchange toward the gateway.
    assert client.post(
        f"/profiles/{p['id']}/interactions/{who}/feedback",
        json={"rating": "up"},
        headers={"authorization": ""}).status_code in (401, 403)
    r = client.post(f"/profiles/{p['id']}/interactions/{who}/feedback",
                    json={"rating": "up"}, headers=as_interactor(who))
    assert r.status_code == 200, r.text
    # Quiet hours are the recipient's own to set…
    r = client.put(f"/interactors/{who}/quiet-hours",
                   json={"quiet_start": 22, "quiet_end": 6},
                   headers=as_interactor(who))
    assert r.status_code == 200, r.text
    assert (r.json()["quiet_start"], r.json()["quiet_end"]) == (22, 6)
    # …and nobody else's.
    other = make_interactor(client, name="Ines")
    assert client.put(f"/interactors/{who}/quiet-hours",
                      json={"quiet_start": 0, "quiet_end": 23},
                      headers=as_interactor(other)).status_code == 403
    # The referral history is likewise the person's own.
    assert client.get(f"/interactors/{who}/referrals",
                      headers=as_interactor(who)).status_code == 200
    assert client.get(f"/interactors/{who}/referrals",
                      headers=as_interactor(other)).status_code == 403


# -- the license ------------------------------------------------------------

def test_a_license_is_bought_against_an_offer(client):
    p = make_profile(client)
    who = make_interactor(client)
    r = client.post(f"/profiles/{p['id']}/license/acquire",
                    headers=as_interactor(who))
    assert r.status_code == 404
    assert "not offered" in r.json()["detail"]


# -- the senses -------------------------------------------------------------

def test_the_senses_answer_and_the_cv_form_refuses_by_name(client):
    for path, key in (("/microphones/places", "places"),
                      ("/microphones/vocabulary", None),
                      ("/overlays/catalogue", None)):
        r = client.get(path, headers={"authorization": ""})
        assert r.status_code == 200, path
        assert r.json(), path
    p = make_profile(client, kind="fictional")
    r = client.post(f"/profiles/{p['id']}/perceive",
                    json={"objects": ["a kettle", "a window"],
                          "goal": "make tea"},
                    headers=auth_header(p))
    assert r.status_code == 200, r.text
    assert r.json()["guidance"]
    # The CV: owner-gated, and `years` is refused by name rather than
    # silently dropped.
    r = client.put(f"/profiles/{p['id']}/experience",
                   json={"entries": [{"title": "Carpenter",
                                      "period": "1990–2005"}]},
                   headers=auth_header(p))
    assert r.status_code == 200, r.text
    assert client.put(f"/profiles/{p['id']}/experience",
                      json={"entries": [{"title": "Carpenter",
                                         "years": "1990"}]},
                      headers=auth_header(p)).status_code == 422
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.put(f"/profiles/{p['id']}/experience",
                      json={"entries": []},
                      headers=auth_header(q)).status_code == 403


# -- the doors and their languages ------------------------------------------

def test_no_route_in_the_table_lacks_a_door_anywhere(client):
    """No route is unreachable from EVERY surface, and every shell's
    deferral is a real route with a reason.

    This asserted the three per-shell files were empty, which is what they
    were when the round that wrote it finished. It stopped being true the
    day a route was legitimately deferred — `POST /rooms/{room_id}/heard`,
    which takes recorded audio and answers with words, and which none of
    the shells has a caller for. The web console does.

        asked     is every per-shell record empty
        mattered  is any route unreachable from everywhere

    Two guards already contradicted each other here.
    `test_every_route_has_a_door.py` states in its own words that adding a
    line to a doorless file **is allowed** — "a backlog is not an approval,
    and there are legitimate reasons to defer" — and
    `test_the_phone_is_a_client_too.py` holds the ratchet that stops one
    growing (309/311/309, currently one row each). Between them, deferring
    is already a deliberate edit that shows in a diff and cannot widen. An
    assertion of emptiness on top of that is not a third protection; it is
    a claim about a finished state, and the day it stops being true it
    reports a decision as a defect.

    So this keeps the part that is still a promise and drops the part that
    was a snapshot. The union is what matters — a route no client anywhere
    can reach is a capability that shipped and cannot be used — and a
    deferral has to be a real route, named exactly, with the reason written
    above it. A typo'd row defers nothing and hides the gap it claims to
    record, which is the failure mode of a backlog nobody parses.
    """
    # `clientpaths.all_routes`, not `app.routes`: FastAPI wraps each
    # `include_router` in a delegating object that carries no path of its
    # own, so the top level alone sees eight of QRME's routes against more
    # than two hundred real ones. That module documents the trap; this is
    # not the place to fall into it again.
    from qrme.api import app as served_app

    served = {f"{method} {route.path}"
              for route in clientpaths.all_routes(served_app)
              for method in (route.methods - {"HEAD", "OPTIONS"})}
    for shell in ("ios", "android", "windows"):
        text = (REPO / f"tests/{shell}_doorless.txt").read_text(
            encoding="utf-8")
        rows = [l.strip() for l in text.splitlines()
                if l.strip() and not l.startswith("#")]
        for row in rows:
            assert row in served, (
                f"{shell}: {row!r} is recorded as doorless and is not a "
                "route this backend serves — a row nothing matches defers "
                "nothing and hides the gap it claims to record"
            )
            assert row.split(" ", 1)[1] in text.replace("#", ""), row
            # The reason, which is the whole point of the file over a count.
            assert text.index("#") < text.index(row), (
                f"{shell}: {row!r} is recorded with no reason above it"
            )
    # The promise that never stopped being one: nothing is doorless
    # everywhere. The console holds the door for anything the shells defer.
    assert clientpaths.doorless(served_app) == [], (
        "a route is reachable from no client at all"
    )
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("POST", "/profiles/genesis") in made, \
            f"{lang.name}: nothing can be born here"
        assert ("POST", "/profiles/x/simulate") in made, \
            f"{lang.name}: the mind cannot be exercised"
        assert ("GET", "/profiles/x/cloud-contribution") in made, \
            f"{lang.name}: the ledger is unreadable"
        assert ("POST", "/profiles/x/proactive/x") in made, \
            f"{lang.name}: the reach has no door"
        assert ("POST", "/profiles/x/license/acquire") in made, \
            f"{lang.name}: no license can be bought"
        assert ("POST", "/profiles/x/perceive") in made, \
            f"{lang.name}: the senses are dark"


def test_the_five_blocks_speak_ten_languages_on_every_shell(client):
    """Every born/mind/reach/lic/sens key the iOS table carries,
    complete on all three shells — the full-list rule, never a sample."""
    shells = {
        "ios": REPO / "native/ios/Sources/L10n.swift",
        "android": (REPO / "native/android/app/src/main/java/app/qrme/"
                           "studio/L10n.kt"),
        "windows": REPO / "native/windows/L10n.cs",
    }
    langs = ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")
    ios_src = shells["ios"].read_text(encoding="utf-8")
    keys = sorted(set(re.findall(
        r'"((?:born|mind|reach|lic|sens)\.[a-z.]+)":', ios_src)))
    assert len(keys) >= 42, f"the iOS table lost rows: {len(keys)}"
    for shell, path in shells.items():
        src = path.read_text(encoding="utf-8")
        for key in keys:
            row = re.search(rf'"{re.escape(key)}"[^\n]*', src)
            assert row, f"{shell}: missing {key}"
            for lang in langs:
                assert f'"{lang}"' in row.group(0), \
                    f"{shell}: {key} missing {lang}"
