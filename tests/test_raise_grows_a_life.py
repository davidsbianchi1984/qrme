"""Raise — grow your own. Round one: the record, the stages, the law.

docs/raise.md is the spec and these tests hold its foundation: *"You
begin with almost nothing — a temperament seed and a stage you choose.
Everything after that is made between you."* The fourth kind has its own
creation door; the Album is append-only; stage doors are earned, never
aged into; the presets are only switch bundles; mortality says its
warning out loud; and the law — a childhood is family forever — is
enforced where relationships are set, not merely written down.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from qrme import raising
from tests.test_community import as_interactor, make_interactor

REPO = Path(__file__).resolve().parents[1]
ENGINE = (REPO / "qrme" / "raising.py").read_text()
RAISE_TSX = (REPO / "app" / "src" / "screens" / "Raise.tsx").read_text()
APP_TSX = (REPO / "app" / "src" / "App.tsx").read_text()


def _begin(client, name="Pip", stage="child", preset="storybook",
           temperament=None):
    r = client.post("/raise", json={
        "owner_id": "acct_guardian", "display_name": name,
        "stage": stage, "preset": preset,
        "temperament": temperament or {"warm_reserved": -40},
        "verification": {"birthdate": "1984-05-01"},
        "terms_consent": True})
    assert r.status_code == 201, r.text
    out = r.json()
    return out["profile_id"], {"authorization":
                               f"Bearer {out['owner_token']}"}, out


# -- the creation door --------------------------------------------------------

def test_a_life_begins_with_a_stage_a_door_and_a_seed(client):
    pid, head, out = _begin(client)
    assert out["kind"] == "raised"
    who = out["character"]
    assert who["stage"] == "child"
    assert who["started_stage"] == "child"
    assert who["preset"] == "storybook"
    assert who["temperament"]["warm_reserved"] == -40
    # The Album opened with the life.
    album = client.get(f"/raise/{pid}/album", headers=head).json()
    assert album["entries"][0]["kind"] == "began"
    assert "storybook door" in album["entries"][0]["note"]


def test_the_ordinary_door_refuses_the_fourth_kind(client):
    r = client.post("/profiles", json={
        "owner_id": "acct_x", "display_name": "Nope", "kind": "raised",
        "persona": "typed", "verification": {"birthdate": "1984-05-01"},
        "terms_consent": True})
    assert r.status_code == 422
    assert "POST /raise" in r.json()["detail"]


def test_a_refused_creation_leaves_no_orphan_profile(client):
    from qrme import db
    before = db.connect().execute(
        "SELECT COUNT(*) c FROM profiles").fetchone()["c"]
    r = client.post("/raise", json={
        "owner_id": "acct_g", "display_name": "Nix", "stage": "larva",
        "preset": "storybook", "temperament": {},
        "verification": {"birthdate": "1984-05-01"},
        "terms_consent": True})
    assert r.status_code == 422
    after = db.connect().execute(
        "SELECT COUNT(*) c FROM profiles").fetchone()["c"]
    assert after == before, "a refused life left a profile row behind"


def test_the_presets_are_the_specs_four_doors():
    assert set(raising.PRESETS) == {"storybook", "caretaker",
                                    "full_trail", "sandbox"}
    # Storybook: no needs, no mortality. Full trail: everything on,
    # mortality on. Sandbox: time controls unlocked. Verbatim postures.
    assert raising.PRESETS["storybook"]["mortality"] is False
    assert raising.PRESETS["full_trail"]["mortality"] is True
    assert raising.PRESETS["full_trail"]["time_controls"] == "sealed"
    assert raising.PRESETS["sandbox"]["time_controls"] == "unlocked"
    # Mortality is off by default on every door but the one that names it.
    assert sum(1 for p in raising.PRESETS.values()
               if p["mortality"]) == 1


# -- the record is append-only ------------------------------------------------

def test_the_growth_record_is_written_and_never_edited():
    """Vault discipline, held by reading the engine: no UPDATE and no
    DELETE ever touches growth_record — the stage lives on the character
    row; the history is immutable."""
    assert "INSERT INTO growth_record" in ENGINE
    assert "UPDATE growth_record" not in ENGINE
    assert "DELETE FROM growth_record" not in ENGINE
    import subprocess
    grep = subprocess.run(
        ["grep", "-rl", "-e", "UPDATE growth_record",
         "-e", "DELETE FROM growth_record", str(REPO / "qrme")],
        capture_output=True, text=True)
    assert grep.stdout.strip() == "", (
        "something edits the append-only record: " + grep.stdout)


# -- doors are earned ---------------------------------------------------------

def test_the_stage_door_opens_on_earned_milestones(client):
    pid, head, _ = _begin(client, stage="embryo")
    # The child door costs 20 growth points; lessons weigh 5.
    for i in range(3):
        r = client.post(f"/raise/{pid}/teach", headers=head,
                        json={"teaching": "lesson", "what": f"lesson {i}"})
        assert r.json()["stage_door"] is None
    r = client.post(f"/raise/{pid}/teach", headers=head,
                    json={"teaching": "lesson", "what": "the fourth"})
    door = r.json()["stage_door"]
    assert door is not None and "child door" in door["note"]
    assert r.json()["character"]["stage"] == "child"
    # The door is an Album entry like everything else.
    album = client.get(f"/raise/{pid}/album", headers=head).json()
    assert any(e["kind"] == "stage_door" for e in album["entries"])


def test_the_first_word_is_marked_as_the_first(client):
    pid, head, _ = _begin(client)
    r = client.post(f"/raise/{pid}/teach", headers=head,
                    json={"teaching": "word", "what": "butterfly"})
    assert r.json()["taught"]["note"] == "first word: butterfly"
    r = client.post(f"/raise/{pid}/teach", headers=head,
                    json={"teaching": "word", "what": "river"})
    assert r.json()["taught"]["note"] == "word: river"


def test_chat_turns_count_toward_the_raising(client):
    """Showing up is itself the raising: the chat door counts a turn
    together for a raised profile and leaves the other kinds alone."""
    pid, head, _ = _begin(client)
    raising.turn_taken(pid)
    raising.turn_taken(pid)
    who = client.get(f"/raise/{pid}", headers=head).json()
    assert who["milestones"]["turns_together"] == 2
    # And a profile that is not raised is a no-op, not an error.
    raising.turn_taken("prf_nobody")


# -- the switches -------------------------------------------------------------

def test_mortality_says_its_warning_every_time_it_turns_on(client):
    pid, head, _ = _begin(client)
    r = client.patch(f"/raise/{pid}/switches", headers=head,
                     json={"changes": {"mortality": True}})
    assert "neglect can end this life" in r.json()["warning"]
    # Off is always allowed, and quiet.
    r = client.patch(f"/raise/{pid}/switches", headers=head,
                     json={"changes": {"mortality": False}})
    assert r.json()["warning"] is None
    # And on AGAIN warns AGAIN — never assumed remembered.
    r = client.patch(f"/raise/{pid}/switches", headers=head,
                     json={"changes": {"mortality": True}})
    assert r.json()["warning"] is not None


def test_an_unknown_switch_is_refused_by_name(client):
    pid, head, _ = _begin(client)
    r = client.patch(f"/raise/{pid}/switches", headers=head,
                     json={"changes": {"jetpack": True}})
    assert r.status_code == 422
    assert "not one of this character's switches" in r.json()["detail"]


# -- the law ------------------------------------------------------------------

def test_a_childhood_is_family_forever(client):
    """The one-way door, enforced where relationships are set: a
    character raised from a child stage refuses the romantic role even
    after it grows up — started_stage decides, not today's stage."""
    pid, head, _ = _begin(client, stage="child")
    person = make_interactor(client, "Dana", "1990-01-01")
    r = client.put(f"/profiles/{pid}/relationships/{person}",
                   headers=head,
                   json={"relationship_type": "romantic_partner"})
    assert r.status_code == 403
    assert "family forever" in r.json()["detail"]
    # Family is exactly what the door is FOR.
    r = client.put(f"/profiles/{pid}/relationships/{person}",
                   headers=head, json={"relationship_type": "family"})
    assert r.status_code == 200, r.text


def test_an_adult_started_character_may_hold_the_role(client):
    pid, head, _ = _begin(client, name="Rowan", stage="adult")
    person = make_interactor(client, "Sam", "1990-01-01")
    r = client.put(f"/profiles/{pid}/relationships/{person}",
                   headers=head,
                   json={"relationship_type": "romantic_partner"})
    assert r.status_code == 200, r.text


def test_a_childhood_is_pinned_to_the_strictest_maturity(client):
    from qrme import db
    pid, head, _ = _begin(client, stage="child")
    row = db.connect().execute("SELECT maturity FROM profiles WHERE id=?",
                               (pid,)).fetchone()
    assert row["maturity"] == "strict"
    assert raising.maturity_floor(pid) == "strict"
    pid2, _, _ = _begin(client, name="Rowan", stage="adult")
    assert raising.maturity_floor(pid2) is None


# -- the raising speaks -------------------------------------------------------

def test_the_prompt_carries_the_stage_and_only_what_was_taught(client):
    pid, head, _ = _begin(client, temperament={"warm_reserved": -60,
                                               "silly_serious": 80})
    client.post(f"/raise/{pid}/teach", headers=head,
                json={"teaching": "word", "what": "butterfly"})
    block = raising.prompt_block(pid)
    assert "You are a child" in block
    assert "warm" in block and "serious" in block
    assert "butterfly" in block
    assert "WHOLE of your learned knowledge" in block


def test_an_untaught_life_says_it_knows_almost_nothing(client):
    pid, head, _ = _begin(client)
    block = raising.prompt_block(pid)
    assert "not been taught anything yet" in block


def test_the_persona_layer_carries_the_raising(client):
    from qrme import persona
    from qrme.common import profile_or_404
    pid, head, _ = _begin(client)
    system = persona.build_system_prompt(profile_or_404(pid), None, None)
    assert "RAISED character" in system


# -- the screen ---------------------------------------------------------------

def test_the_raise_tab_stands_in_the_shell():
    assert '"raise"' in APP_TSX
    assert "<Raise onPlans" in APP_TSX
    for needle in ("raise.begin", "raise.teach", "raise.album",
                   "raise.switches", "raiseBegin", "raiseTeach",
                   "raise.door."):
        # The door captions are looked up through a template head
        # (`raise.door.${p}`) over the server's own preset list — the
        # dead-key guard's sanctioned shape for a table-driven lookup.
        assert needle in RAISE_TSX, f"the Raise screen lost {needle}"
    # The mortality warning renders when the server sends one — the
    # law's worded half reaching the person.
    assert "r.warning" in RAISE_TSX
