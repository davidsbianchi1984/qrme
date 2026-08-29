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


def test_the_always_on_moves_are_drawn_as_on(client, profile_id):
    """`look`, `ask` and `done` are in every grant whether or not they were
    ticked — `_verbs` forces them in. The screen drew them empty and
    disabled, which reads as "refused" rather than "always", and the first
    person to use it reported that it would not let him tick `look`.

    asked     why can the owner not grant the move that lets it see
    mattered  a box the owner cannot tick and cannot read is a lie either
              way; drawn on, it says what the backend already does
    """
    granted = hands.grant(
        profile_id, profile_id, surface="computer", places=["notepad"],
        verbs=["press", "type"])
    # Untouched by the owner, and in anyway.
    assert {"look", "ask", "done"} <= set(granted["verbs"])

    screen = (REPO / "app" / "src" / "screens" / "Hands.tsx").read_text(
        encoding="utf-8")
    block = screen.split('tr("hnd.moves"')[1].split("</div>")[0]
    assert "checked={verbs.includes(v) || always.includes(v)}" in block
    assert "disabled={always.includes(v)}" in block
    # And the reason is on the screen, not only in this file.
    assert 'tr("hnd.always"' in screen


def test_a_half_copied_command_line_says_so():
    """The command is copied off a screen, and the first person to run it
    copied the placeholders instead of the values. urllib answered with
    `unknown url type: '.../profiles/...'`, which names neither the flag
    that is wrong nor the screen the right one is on.

    asked     what does the motor say when --base is not a URL
    mattered  the person holding the terminal is the owner, not an
              operator; a traceback is not an answer to them
    """
    source = (REPO / "companion" / "hands.py").read_text(encoding="utf-8")
    body = source.split("def main(")[1]
    guard = body.split("where = ")[0]
    assert 'startswith(("http://", "https://"))' in guard
    assert "SystemExit" in guard
    # And it points at the place the real one is written out.
    assert "Hands screen" in guard


def test_the_grab_uses_the_name_mss_is_keeping():
    """`mss.mss` warns on release 10 and is going away. The motor prints
    that warning above its own first line, which reads like a fault in the
    thing the person just installed."""
    source = (REPO / "companion" / "hands.py").read_text(encoding="utf-8")
    assert 'getattr(mss, "MSS", None)' in source
    assert "with mss.mss()" not in source


def test_the_command_is_one_line_and_copyable():
    """The motor's command line was printed the way a shell script reads —
    four lines ending in backslashes. The first person to run it was on
    PowerShell, where a trailing backslash is an argument rather than a
    continuation, so the line could not be pasted at all.

    asked     can the reader get this command onto their own terminal
    mattered  it carries a token; a line you must retype off a screen is
              a line that gets retyped wrong, or photographed
    """
    screen = (REPO / "app" / "src" / "screens" / "Hands.tsx").read_text(
        encoding="utf-8")
    built = screen.split("function motorCommand(")[1].split("\n  }")[0]
    assert "\\\\\\n" not in built and "\\n" not in built
    for flag in ("--base", "--profile", "--reach"):
        assert flag in built
    # And there is a button, not just a box to select by hand.
    assert 'tr("hnd.motor.copy"' in screen
    assert "navigator.clipboard.writeText(motorCommand(" in screen


def test_the_platform_starts_at_the_machine_reading_the_screen():
    """The picker opened on macOS for everybody. A Windows reader opened a
    reach that told the deciding half it was working a Mac, so the errand
    was right and the menus it reasoned about were somebody else's."""
    screen = (REPO / "app" / "src" / "screens" / "Hands.tsx").read_text(
        encoding="utf-8")
    assert 'useState(_thisMachine())' in screen
    guess = screen.split("function _thisMachine(")[1].split("\n}")[0]
    for named in ("windows", "macos", "linux", "android", "ios"):
        assert named in guess
        assert named in hands.PLATFORMS


def test_a_model_that_failed_is_not_reported_as_a_screen(client, profile_id,
                                                         monkeypatch):
    """`decide` caught every exception from the deciding model, threw the
    reason away, and asked with "it could not read the screen". The eyes
    had worked — the first person to run the motor watched it describe his
    taskbar, then his Notepad window, and then tell him twice that it
    could not read the screen. He went looking at his monitor.

    asked     which half failed
    mattered  a refusal that names the wrong half sends the reader to the
              wrong place, and this one is read by the owner of the screen
    """
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"], errand="type yellow",
                             platform="windows")

    class _Broken:
        def generate(self, system, messages):
            raise RuntimeError("nope")

    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: "a notepad")
    from qrme import llm
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: _Broken())
    step = hands.decide(reach["id"])
    assert step["verb"] == "ask"
    assert "could not read the screen" not in step["target"]
    assert "RuntimeError" in step["target"]
    # The eyes' own failure keeps the sentence that belongs to it.
    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: None)
    reach2 = hands.open_reach(profile_id, granted["id"],
                              errand="type yellow", platform="windows")
    blind = hands.decide(reach2["id"])
    assert blind["target"] == "it could not read the screen"


def test_the_machine_is_in_the_question(profile_id):
    """The platform is picked on the screen that opens a reach and was then
    used only to decide whether the machine could be driven at all. The
    deciding half was never told which machine it was working, so it
    reasoned about generic furniture — a Mac menu bar on a Windows laptop.
    """
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"],
                             errand="type yellow", platform="windows")
    _, question = hands._decision_prompt(
        hands.read_reach(reach["id"]), ["press", "type"], "a notepad", [])
    assert "windows" in question


def test_looking_is_not_offered_as_a_free_first_move(profile_id):
    """The screen is read afresh before every decision, so `look` returns
    what the question already carries. The first person to run the motor
    spent step 1 on `look`, learnt nothing, and asked on step 2.

    asked     why does it burn a move seeing what it was just shown
    mattered  a step budget is the owner's, and the first one bought air
    """
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"],
                             errand="type yellow", platform="windows")
    system, _ = hands._decision_prompt(
        hands.read_reach(reach["id"]), ["look", "press", "type"], "x", [])
    assert "tells you nothing you are not already" in system
    # And `ask` is for what a person knows, not for being unsure.
    assert "not because you are unsure" in system


def test_an_empty_answer_is_asked_for_twice(client, profile_id, monkeypatch):
    """`ask` closes a reach. One blank answer therefore ended an errand and
    cost its owner a new grant, a new reach and a new command line — for a
    hiccup that was nobody's question."""
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"], errand="type yellow",
                             platform="windows")

    class _Hiccups:
        def __init__(self):
            self.asked = 0

        def generate(self, system, messages):
            self.asked += 1
            return "" if self.asked == 1 else "type | the page | yellow"

    twice = _Hiccups()
    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: "a notepad")
    from qrme import llm
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: twice)
    step = hands.decide(reach["id"])
    assert twice.asked == 2
    assert step["verb"] == "type"
    assert hands.read_reach(reach["id"])["state"] == "open"


def test_the_prompt_says_whose_screen_it_is(profile_id):
    """Every claim in the opening of the system prompt is one this module
    enforces elsewhere, and it is there because leaving it out changed the
    answers: the model chose `look`, then said nothing at all once looking
    was discouraged and pressing was the only thing left.

    asked     whose machine is this and who is standing at it
    mattered  a hand asked to drive nobody's computer should decline; the
              refusal was right and the question was wrong
    """
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"],
                             errand="type yellow", platform="windows")
    system, _ = hands._decision_prompt(
        hands.read_reach(reach["id"]), ["press", "type"], "a notepad", [])
    assert "owner's own" in system
    assert "ledger" in system
    assert "corner" in system
    # And each claim is true of the code, not decoration.
    assert hands.read_grant(granted["id"])["places"]        # named apps
    assert hands.read_grant(granted["id"])["steps"]         # a step budget
    assert hands.ledger(reach["id"]) == []                  # a real ledger


def test_a_silent_answer_names_its_stop_reason():
    """The Anthropic response keeps only text blocks. When there are none,
    `stop_reason` is the only thing that says whether the model declined or
    spent its budget thinking — and it was dropped, so every caller saw an
    empty string and reported it as having nothing to say."""
    source = (REPO / "qrme" / "llm.py").read_text(encoding="utf-8")
    body = source.split("class AnthropicProvider")[1].split("\nclass ")[0]
    assert "stop_reason=%s blocks=%s" in body


def test_the_decision_follows_the_owners_chosen_model(client, profile_id,
                                                      monkeypatch):
    """Deciding a move on somebody's screen is the one call here a provider
    may decline as a class, and one did — `stop_reason=refusal`, no content
    at all. The remedy is the owner's, and they already have the screen for
    it, so `decide` asks the provider that profile chose rather than the
    house default.

    asked     which model is being asked to move somebody's cursor
    mattered  the owner picked one; a refusal they cannot route around is
              a dead end, and this one is theirs to route
    """
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"], errand="type yellow",
                             platform="windows")
    asked_for = {}

    class _Says:
        def generate(self, system, messages):
            return "type | the page | yellow"

    from qrme import llm

    def _for_profile(pid, cloud=None):
        asked_for["profile"] = pid
        return _Says()

    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: "a notepad")
    monkeypatch.setattr(llm, "provider_for_profile", _for_profile)
    step = hands.decide(reach["id"])
    assert asked_for["profile"] == profile_id
    assert step["verb"] == "type"


def test_a_model_that_will_not_answer_points_at_the_remedy(client, profile_id,
                                                           monkeypatch):
    """"answered with nothing" is true and useless. The owner can change
    which model decides, on a screen that already exists."""
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"], errand="type yellow",
                             platform="windows")

    class _Mute:
        def generate(self, system, messages):
            return ""

    from qrme import llm
    monkeypatch.setattr(hands, "read_screen", lambda *a, **k: "a notepad")
    monkeypatch.setattr(llm, "provider_for_profile", lambda *a, **k: _Mute())
    step = hands.decide(reach["id"])
    assert step["verb"] == "ask"
    assert "Settings" in step["target"]


def test_the_probe_asks_what_the_hands_ask():
    """Finding out which provider will work a screen used to cost a grant,
    a reach, a hand-edited command line and a rebuild — per candidate, and
    the answer is each vendor's policy rather than anything predictable.

    asked     which model will choose a move, before anyone buys a key
    mattered  a probe that asks an easier question answers a different one
    """
    from qrme import will_it_decide

    # It builds the real prompt, not a convenient one.
    source = (REPO / "qrme" / "will_it_decide.py").read_text(encoding="utf-8")
    assert "hands._decision_prompt(" in source
    assert "hands._CHOICE.match" in source
    # And it ships: `tools/` is not copied into the image, and this has to
    # run where the keys are.
    assert (REPO / "qrme" / "will_it_decide.py").exists()
    assert "COPY qrme/" in (REPO / "Dockerfile").read_text(encoding="utf-8")

    verdict, detail = will_it_decide._one("stub")
    # The stub is not a deciding model and the probe says so rather than
    # flattering it.
    assert verdict in ("UNPARSED", "SILENT", "HEDGED", "ERROR")
    assert detail


def test_the_eyes_do_not_write_down_what_they_should_not_read():
    """The description the eyes write is not a passing thought: it goes
    into the ledger's `saw` column and out to the deciding model on every
    turn after. A terminal left open with an owner token in it therefore
    put that token in the database and in a provider's inbox — and the
    deciding model refused the errand rather than work a screen with a
    credential written across it, which was the right call.

    asked     what did the eyes see
    mattered  what did they write down, and where did that go
    """
    seen = ("PowerShell is open behind Notepad. It shows: python hands.py "
            "--token _-emviLdIVDYeyhz2YGM3dW_5QutpovSwIVbcQJHTXs --reach "
            "rch_1d5b30d5af28")
    kept = hands.without_secrets(seen)
    assert "_5QutpovSwIVbcQJHTXs" not in kept
    assert hands.UNSAID in kept
    # The parts a person needs are still there.
    assert "Notepad" in kept and "hands.py" in kept
    # Ordinary prose is left alone.
    plain = "A blank Notepad window with the cursor at Ln 1, Col 1."
    assert hands.without_secrets(plain) == plain
    # A card on the glass goes too, and the sentence still reads.
    carded = hands.without_secrets("the card 4111 1111 1111 1111 is shown")
    assert "4111" not in carded and "is shown" in carded
    # And it is the eyes that call it, not something a caller may forget.
    source = (REPO / "qrme" / "hands.py").read_text(encoding="utf-8")
    eyes = source.split("def read_screen(")[1].split("\ndef ")[0]
    assert "without_secrets(llm.look(" in eyes
    assert "never what it says" in eyes


def test_the_token_is_not_on_the_screen_the_eyes_photograph():
    """`--token` put a live credential in four places at once: the shell's
    history, the process list, the terminal's scrollback, and — because
    this program photographs the screen it is running on — every frame it
    sends. Clearing the window did not help: the line you type is echoed,
    so the token is back in the first row of the next picture.

    asked     how does the motor learn the token
    mattered  who else learns it, and the eyes were one of them

    The deciding model refused an errand over exactly this, which was the
    right reading of a screen with a token written across it.
    """
    motor = (REPO / "companion" / "hands.py").read_text(encoding="utf-8")
    assert 'ask.add_argument("--token", default=None' in motor
    assert "getpass.getpass(" in motor
    assert "QRME_OWNER_TOKEN" in motor
    # `--token` still exists for a script with nowhere to type, and says
    # what it costs rather than passing silently.
    resolve = motor.split("def _token(")[1].split("\ndef ")[0]
    assert "every picture" in resolve

    # And the console stops printing it.
    screen = (REPO / "app" / "src" / "screens" / "Hands.tsx").read_text(
        encoding="utf-8")
    built = screen.split("function motorCommand(")[1].split("\n  }")[0]
    assert "token" not in built.replace("// ", "").split("return")[1]


def test_the_owner_can_still_get_at_their_own_token():
    """Taking the token out of the printed command was right and left
    nowhere to get it from — the console showed it in exactly one place
    and that place was the command. The first person to try typed
    something else and the stack said "authentication required", which
    was true and no help at all.

    asked     where does the owner get their token now
    mattered  a secret nobody can reach is not safer, it is broken
    """
    screen = (REPO / "app" / "src" / "screens" / "Hands.tsx").read_text(
        encoding="utf-8")
    # Copied, never drawn.
    assert "navigator.clipboard.writeText(token)" in screen
    assert 'tr("hnd.motor.token"' in screen
    # And a fold for a browser that cannot reach the clipboard, which
    # costs a deliberate press and says what it costs.
    assert 'tr("hnd.motor.token.show"' in screen
    assert 'tr("hnd.motor.token.warn"' in screen
    fold = screen.split('<details className="hnd-token">')[1].split(
        "</details>")[0]
    assert "{token}" in fold
    # The command itself still carries no token.
    built = screen.split("function motorCommand(")[1].split("\n  }")[0]
    assert "${token}" not in built


def test_there_is_time_to_bring_the_app_forward():
    """The motor is started from a terminal, so a terminal is the first
    thing it photographs: a shell filling the display, and an errand about
    an app that is not in the picture. The first person to run it watched
    it look, look again, and give up — every one of those a correct
    reading of the screen it was actually shown.

    asked     what is on the screen when the first picture is taken
    mattered  whatever the person was starting this from, not what they
              meant it to work
    """
    motor = (REPO / "companion" / "hands.py").read_text(encoding="utf-8")
    assert '"--start-in"' in motor
    body = motor.split("def main(")[1]
    setup = body.split("for round_number")[0]
    assert "start_in" in setup and "time.sleep(1)" in setup
    # It counts down out loud rather than appearing to hang.
    assert "first picture in" in setup
