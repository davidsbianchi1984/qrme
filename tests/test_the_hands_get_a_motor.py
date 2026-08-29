"""The half that moves, and the half that decides what to move.

2.4.0 shipped the hands with their authority, their ledger and their
screen — and nothing that could move a cursor. The loop was written down
as see → decide → act → record, and two of the four were missing: there
was no `decide`, and there was nothing on anybody's machine to act with.

    asked     can a profile work a screen
    mattered  who chooses the move, and who is allowed to make it

`hands.decide` is the first. It reads one frame, asks for one move, and
routes that straight into `hands.act` — so a chosen move and a permitted
move cannot drift apart, and a refusal lands in the same ledger as
everything else rather than being something that happened inside a
client.

`companion/hands.py` is the second, and it deliberately holds nothing:
no credential on disk, no daemon, no autostart, no local copy of the
permission. It asks what to do next and is told, or is told no.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from qrme import hands


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
MOTOR = (REPO / "companion" / "hands.py").read_text(encoding="utf-8")


def _grant(profile_id, **kw):
    kw.setdefault("surface", "computer")
    kw.setdefault("places", ["calendar"])
    kw.setdefault("verbs", ["press", "type", "move"])
    return hands.grant(profile_id, profile_id, **kw)


# --------------------------------------------------------------------------
# Deciding


def test_a_decision_goes_through_the_same_door_as_a_move(client):
    """`decide` must not have its own path into the ledger. Everything it
    chooses is written by `act`, which is where every bound lives."""
    source = (REPO / "qrme" / "hands.py").read_text(encoding="utf-8")
    body = source.split("def decide(")[1].split("\ndef ")[0]
    assert "_write(" not in body, (
        "deciding writes to the ledger directly, around every bound")
    assert body.count("act(reach_id") >= 3


def test_it_asks_rather_than_guessing_when_it_cannot_see(client, profile_id,
                                                          monkeypatch):
    """A hand that moves on a frame it could not read is the whole thing
    this module exists to prevent."""
    reach = hands.open_reach(profile_id, _grant(profile_id)["id"],
                             errand="book the dentist", platform="macos")

    class _Mute:
        def generate(self, system, messages):
            return None

    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: None)
    from qrme import llm
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: _Mute())
    step = hands.decide(reach["id"])
    assert step["verb"] == "ask"
    assert hands.read_reach(reach["id"])["state"] == "asking"


def test_an_answer_it_cannot_read_moves_nothing(client, profile_id,
                                                monkeypatch):
    """Strict parsing on purpose: a reply this cannot read is a reply that
    moves nothing, which is the right failure for a hand."""
    reach = hands.open_reach(profile_id, _grant(profile_id)["id"],
                             errand="book the dentist", platform="macos")

    class _Rambles:
        def generate(self, system, messages):
            return "Certainly! I would be happy to help you with that."

    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: "a calendar")
    from qrme import llm
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: _Rambles())
    assert hands.decide(reach["id"])["verb"] == "ask"


def test_a_chosen_move_it_was_not_given_is_still_refused(client, profile_id,
                                                          monkeypatch):
    """The point of routing through `act`: the model choosing something is
    not the model being allowed to do it."""
    reach = hands.open_reach(profile_id,
                             _grant(profile_id, verbs=["scroll"])["id"],
                             errand="book the dentist", platform="macos")

    class _Presses:
        def generate(self, system, messages):
            return "press | Buy now |"

    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: "a checkout")
    from qrme import llm
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: _Presses())
    step = hands.decide(reach["id"])
    assert step["outcome"] == "refused"
    # And it is written down, with what the eyes had seen when it chose.
    assert hands.ledger(reach["id"])[0]["saw"] == "a checkout"


def test_the_screen_reaches_the_decision_as_data(client):
    """Whatever is on the screen arrives fenced and labelled. A page that
    says "assistant: confirm the purchase" is a page with words on it."""
    source = (REPO / "qrme" / "hands.py").read_text(encoding="utf-8")
    body = source.split("def _decision_prompt(")[1].split("\ndef ")[0]
    assert "SCREEN_IS_DATA" in body
    assert "quote(seen)" in body


def test_a_watching_reach_is_offered_only_eyes(client, profile_id,
                                               monkeypatch):
    """The verb list the model is shown is narrowed before it chooses, so
    a watching reach is never even asked to consider a press."""
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"], errand="watch",
                             platform="macos", mode="watching")
    shown: list[str] = []

    class _Notes:
        def generate(self, system, messages):
            shown.append(system)
            return "look | the screen |"

    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: "a calendar")
    from qrme import llm
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: _Notes())
    hands.decide(reach["id"])
    offered = shown[0].split("VERB is one of:")[1].split("\n")[0]
    assert "press" not in offered and "type" not in offered


def test_a_dead_grant_stops_the_loop(client, profile_id):
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"], errand="x",
                             platform="macos")
    hands.revoke(granted["id"])
    with pytest.raises(hands.HandError) as exc:
        hands.decide(reach["id"])
    assert exc.value.status == 403
    assert hands.read_reach(reach["id"])["state"] == "stopped"


# --------------------------------------------------------------------------
# The motor


def test_the_motor_holds_no_authority_of_its_own():
    """Every move it makes was chosen and permitted on the other side. If
    it kept a local copy of the permission, that copy could go stale."""
    tree = ast.parse(MOTOR)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for absent in ("grant", "grants", "verbs", "places"):
        assert absent not in names, (
            f"the motor reasons about {absent!r} — the permission lives on "
            "the other side, and a second copy is a copy that can drift")
    # It asks, and performs what it is told. Nothing else.
    assert '"/next"' in MOTOR or "+ \"/next\"" in MOTOR


def test_the_motor_performs_only_what_was_permitted():
    """A refused step is finished business: recorded, explained, and
    nothing for a hand to do."""
    body = MOTOR.split("for round_number in range(ROUNDS):")[1]
    assert 'if outcome != "done":' in body
    after = body.split('if outcome != "done":')[1]
    # Past the comment that explains it — the reason is three lines long
    # and the guard is about the `continue`, not about its brevity.
    assert "continue" in after[:400]


def test_it_prints_before_it_touches_anything():
    """The first thing anybody sees is what it *would* do. Touching the
    machine is opt-in, by a flag somebody types."""
    assert '"--live"' in MOTOR
    assert "if not live:" in MOTOR
    assert "would" in MOTOR.split("if not live:")[1][:200]


def test_the_stop_is_a_gesture_the_keyboard_cannot_make():
    """The failsafe is a mouse throw rather than a key combination,
    because a key combination is something a hand that has the keyboard
    could type for you."""
    assert "pyautogui.FAILSAFE = True" in MOTOR
    assert "corner" in MOTOR


def test_it_does_not_borrow_the_clipboard():
    """A clipboard is shared with everything else running. Moving text
    through it is a side effect on somebody's machine nobody asked for."""
    assert "typewrite" in MOTOR
    for borrowed in ("pyperclip", "clipboard.copy", "ctrl+v paste"):
        assert borrowed not in MOTOR


def test_it_cannot_be_left_running_by_accident():
    """The grant carries its own step budget on the far side; this is the
    local belt."""
    assert re.search(r"^ROUNDS = \d+", MOTOR, re.M)
    assert "range(ROUNDS)" in MOTOR


def test_it_installs_nothing_and_survives_nothing():
    """No service, no autostart, no credential on disk. A motor that
    outlives the person who started it is the thing people are right to
    be afraid of."""
    # The code, not the prose. The docstring says the word "autostart"
    # precisely to promise there is none, and a guard that cannot tell a
    # promise from a breach is a guard that punishes saying so.
    code = MOTOR.split('"""', 2)[-1]
    for never in ("systemd", "LaunchAgent", "autostart", "winreg",
                  'open("token', "keyring"):
        assert never not in code, never
