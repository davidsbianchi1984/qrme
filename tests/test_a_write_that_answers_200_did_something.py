"""A successful write must have written something.

Two routes in the owner's workshop were **silently permissive**, and it is the
same shape twice — a Pydantic model with a default, so an unknown key is
accepted, discarded, and answered `200`:

* ``PUT /profiles/{id}/steering`` takes ``values``. ``dials`` is the obvious
  guess, because that is what the *read* calls its catalogue;
* ``PUT /profiles/{id}/experience`` takes ``period``. ``years`` is the obvious
  guess, because that is what anybody writing a CV form reaches for.

Neither produced an error. The row saved with no dates, the dials did not move,
and both requests looked exactly like successes — same status, same shape,
plausible body. Nothing in the response distinguished "I applied your change"
from "I ignored it". A typecheck cannot see it, a status check cannot see it,
and a client that fired the request and moved on would never find out.

Both models are strict now, so a wrong key gets a 422 naming the field. But the
strictness is the *fix*, not the guard: the guard has to be the thing that
would have caught it in the first place, which is **writing and reading back**.
So each test here sets a value through the route and then asks the route what
it holds, and the strictness gets its own tests underneath.

The general lesson, worth stating because it will recur: a request model with
defaults for every field can never fail on a body it does not understand. Where
that model is the target of an owner's edit, "accepted" and "applied" have to be
checked separately.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _owner(client, account="acct_write"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Maker",
        "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1990-01-01"},
    }).json()
    token = p["owner_token"]
    client.post(f"/memberships/{account}", json={"plan": "pro"},
                headers={"authorization": f"Bearer {token}"})
    return p, {"authorization": f"Bearer {token}"}


# --- the two writes, checked by reading back --------------------------------

def test_steering_moves_the_dial_it_was_told_to(client):
    p, head = _owner(client, "acct_dial")
    r = client.put(f"/profiles/{p['id']}/steering",
                   json={"values": {"warmth": 80, "humor": 20}}, headers=head)
    assert r.status_code == 200, r.text
    assert r.json()["values"]["warmth"] == 80
    back = client.get(f"/profiles/{p['id']}/steering", headers=head).json()
    assert back["values"]["warmth"] == 80 and back["values"]["humor"] == 20, (
        "the steering write answered 200 and the dials did not move")


def test_an_experience_line_keeps_its_dates(client):
    p, head = _owner(client, "acct_cv")
    r = client.put(f"/profiles/{p['id']}/experience", headers=head, json={
        "entries": [{"title": "Head plumber", "org": "Bath Water Co",
                     "period": "2011-2019", "detail": "domestic heating"}]})
    assert r.status_code == 200, r.text
    entry = r.json()["experience"][0]
    assert entry["period"] == "2011-2019", (
        "the line saved without its dates and the request still succeeded")
    assert entry["org"] == "Bath Water Co"


# --- and the strictness that now makes the wrong key visible ----------------

def test_the_steering_write_refuses_a_key_it_would_have_dropped(client):
    """`dials` is what the read calls the catalogue, so it is the guess
    somebody makes. It used to be accepted and ignored."""
    p, head = _owner(client, "acct_dropped")
    r = client.put(f"/profiles/{p['id']}/steering",
                   json={"dials": {"warmth": 80}}, headers=head)
    assert r.status_code == 422, (
        "a body the route does not understand is being accepted again — it "
        "will answer 200 and change nothing")
    assert "dials" in r.text


def test_the_experience_write_refuses_a_key_it_would_have_dropped(client):
    p, head = _owner(client, "acct_years")
    r = client.put(f"/profiles/{p['id']}/experience", headers=head, json={
        "entries": [{"title": "Head plumber", "years": "2011-2019"}]})
    assert r.status_code == 422
    assert "years" in r.text


def test_a_robot_body_is_covered_by_the_same_strictness(client):
    """`SteeringSet` is shared with the robot route, which is where this was
    first found. One model, so one fix — asserted rather than assumed."""
    p, head = _owner(client, "acct_robotstrict")
    robot = client.post(f"/profiles/{p['id']}/robots",
                        json={"name": "Helper", "model": "u1_ultra"},
                        headers=head).json()
    assert client.put(f"/robots/{robot['id']}/steering",
                      json={"dials": {"pace": 10}},
                      headers=head).status_code == 422


# --- the rest of the workshop, driven ---------------------------------------

def test_source_material_says_whether_it_was_vaulted(client):
    """The create answers `vaulted`, the list answers `pdi_key`, and they are
    the same fact from two ends. The screen shows the material itself when it
    is not vaulted, because *not vaulted* means readable — by this platform,
    by whoever runs it, and by a lawful request."""
    p, head = _owner(client, "acct_src")
    made = client.post(f"/profiles/{p['id']}/sources", headers=head, json={
        "kind": "writing", "title": "How I answer the phone",
        "content": "Always name the shop first."}).json()
    assert "vaulted" in made
    row = client.get(f"/profiles/{p['id']}/sources", headers=head).json()[0]
    assert (row["pdi_key"] is not None) == made["vaulted"], (
        "the two ends disagree about whether this went into a vault")
    if not made["vaulted"]:
        assert row["content"], (
            "nothing is vaulted and nothing is readable either — then the "
            "screen cannot show the owner what is actually being held")


def test_a_source_kind_outside_the_vocabulary_is_refused(client):
    """The enum is the picker. A free-text kind would make the dropdown a
    guess."""
    p, head = _owner(client, "acct_srckind")
    r = client.post(f"/profiles/{p['id']}/sources",
                    json={"kind": "note", "content": "x"}, headers=head)
    assert r.status_code == 422
    assert "writing" in r.text


def test_the_specialist_route_is_plural_and_takes_one(client):
    """Named `specialists`, takes `{domain, specialist_profile_id}`. Reading
    the route name as "set the list" sends an array and gets a 422 for two
    missing fields — so the console binds one pair per call."""
    p, head = _owner(client, "acct_spec")
    expert = client.post("/profiles", json={
        "owner_id": "acct_spec", "kind": "fictional", "display_name": "Expert",
        "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1990-01-01"}}).json()
    assert client.put(f"/profiles/{p['id']}/specialists",
                      json={"specialists": []}, headers=head).status_code == 422
    r = client.put(f"/profiles/{p['id']}/specialists", headers=head,
                   json={"domain": "plumbing",
                         "specialist_profile_id": expert["id"]})
    assert r.status_code == 200, r.text
    rows = client.get(f"/profiles/{p['id']}/specialists", headers=head).json()
    assert rows[0]["domain"] == "plumbing"
    # No name comes back, which is why the screen shows an id as an id.
    assert "display_name" not in rows[0]


@pytest.mark.parametrize("field", ["external_transmission", "computed",
                                   "offline_mode", "sealed_in_vault"])
def test_the_finetune_answers_with_what_did_not_happen(field, client):
    """Most of this response is claims about what the run did *not* do —
    nothing transmitted, computed on this host. That is the reason the
    feature reads the way it does, so the screen renders those fields rather
    than asserting them itself, and they have to keep arriving."""
    p, head = _owner(client, f"acct_ft_{field}")
    run = client.post(f"/profiles/{p['id']}/finetune", json={},
                      headers=head).json()
    assert field in run, (
        f"the fine-tune no longer reports {field!r}, so a console claiming "
        "nothing left this machine would be claiming it on its own authority")


def test_nothing_leaves_the_host_on_a_finetune(client):
    p, head = _owner(client, "acct_ftlocal")
    run = client.post(f"/profiles/{p['id']}/finetune", json={},
                      headers=head).json()
    assert run["external_transmission"] is False
    assert "local" in run["computed"].lower()


def test_the_consistency_check_needs_no_account(client):
    """The one route on this screen a stranger can read.

    Somebody who has met the profile through a speaker and then meets it in a
    room can verify the signature is the same. Requiring a token would make
    that check available only to the person who never needed it.
    """
    p, head = _owner(client, "acct_sig")
    client.post(f"/profiles/{p['id']}/embodiments", headers=head,
                json={"name": "kitchen speaker", "kind": "speaker",
                      "has_llm": False})
    r = client.get(f"/profiles/{p['id']}/embodiment-consistency")
    assert r.status_code == 200, "the public verification check now needs auth"
    body = r.json()
    assert body["signature"] and body["guarantee"]
    assert body["embodiments"][0]["name"] == "kitchen speaker"


def test_an_embodiment_says_whether_it_can_answer_for_itself(client):
    """A speaker that relays and a robot that converses are different things
    to have in a room, and `has_llm` is the whole difference."""
    p, head = _owner(client, "acct_emb")
    client.post(f"/profiles/{p['id']}/embodiments", headers=head,
                json={"name": "hall earpiece", "kind": "earpiece",
                      "has_llm": False})
    rows = client.get(f"/profiles/{p['id']}/embodiments", headers=head).json()
    assert rows[0]["has_llm"] is False


def test_guidance_from_a_scene_carries_its_mark(client):
    """Everything generated here is watermarked, and the screen draws the mark
    beside the words rather than under a link."""
    p, head = _owner(client, "acct_see")
    r = client.post(f"/profiles/{p['id']}/perceive", headers=head,
                    json={"objects": ["radiator", "bleed key"],
                          "goal": "bleed the radiator"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["recognized_count"] == 2
    assert body["watermark"]["display"]["line"]
    assert "AI" in body["watermark"]["disclosure"]


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_the_workshop_screen_exists():
    assert (REPO / "app/src/screens/Workshop.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.profileSteering(", "api.setProfileSteering(", "api.sources(",
    "api.addSource(", "api.specialists(", "api.attachSpecialist(",
    "api.setExperience(", "api.finetune(", "api.embodiments(",
    "api.addEmbodiment(", "api.embodimentConsistency(", "api.perceive(",
])
def test_the_workshop_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Workshop.tsx")


def test_the_console_sends_the_field_names_the_models_declare():
    """The console half of both silent drops. A regression here would be
    accepted by neither model now, but the assertion is cheap and it names
    the two words that were wrong."""
    api = _src("app/src/api.ts")
    assert "body: { values }" in api, "steering is not sending `values`"
    workshop = _src("app/src/screens/Workshop.tsx")
    assert "period:" in workshop and "years:" not in workshop, (
        "the experience form is back to `years`, which is not the field")


def test_every_option_in_the_body_picker_is_a_kind_the_server_takes():
    """Written after the picker shipped with three words that were not.

    `screen`, `wearable` and `vehicle` are the words that come naturally for
    a thing a profile speaks through, and none of them is in the enum. Each
    would have sat in the dropdown looking ordinary and 422'd on submit —
    a wrong option is indistinguishable from a right one until pressed.
    """
    import re

    from qrme import models

    field = models.EmbodimentAdd.model_fields["kind"]
    allowed = set(getattr(field.annotation, "__args__", ()))
    assert allowed, "EmbodimentAdd.kind is no longer a closed vocabulary"

    src = _src("app/src/screens/Workshop.tsx")
    m = re.search(r'\{\[((?:"[a-z_]+",?\s*)+)\]\.map\(\(k\) => <option',
                  src)
    assert m, "the embodiment picker is no longer a literal list of kinds"
    offered = set(re.findall(r'"([a-z_]+)"', m.group(1)))
    assert offered <= allowed, (
        f"the picker offers kinds the server refuses: "
        f"{sorted(offered - allowed)}")


def test_the_public_check_is_bound_without_a_token():
    """Binding it with a token would work and would quietly make a public
    verification surface private to the one person who does not need it."""
    api = _src("app/src/api.ts")
    i = api.index("embodimentConsistency:")
    stanza = api[i:i + 220]
    assert "token" not in stanza, (
        "embodimentConsistency now takes a token — it is the one route here "
        "a stranger is meant to be able to read")
