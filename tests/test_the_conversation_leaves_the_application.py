"""The conversation that survives leaving the app, and what it owes for that.

The console's walk-along strip carries a conversation across a screen change
and stops dead when the browser puts the page away. That is not a shortcoming
of the strip — a backgrounded web page has its recogniser ended by the
browser — and the strip says so on screen rather than pretending otherwise.

    asked     can the conversation survive a screen change
    mattered  can it survive leaving the application

On a phone the answer can be yes, and the price is a foreground service
holding a microphone while the person is somewhere else entirely. That
notification is not a platform tax to be minimised. It is the whole
difference between *the conversation you took with you* and *an app recording
you after you left it*, and the two are the same code with different honesty.

So this file holds the declarations, which is what an environment with no
Android toolchain can actually check — and which is also, conveniently, the
half whose absence is a microphone with no indicator:

  * the permissions are asked for, including the one for the notification;
  * the service is declared, not exported, and typed as a microphone service;
  * the foreground start is made with that type;
  * the notification is ongoing and its first action ends the conversation;
  * nothing restarts the service by itself.

## What this cannot check

Whether it works. There is no compiler here, so the loop — the recogniser,
the turn, the voice — has been reasoned about and not run. The guard says
what it is checking so nobody reads a green suite as a working feature; the
CHANGELOG says the same thing in the reader's direction.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo()
MANIFEST = REPO / "native/android/app/src/main/AndroidManifest.xml"
SERVICE = REPO / ("native/android/app/src/main/java/app/qrme/studio/"
                  "Walk.kt")


def test_the_service_exists_at_all():
    assert SERVICE.exists(), "the walking service is gone"


def test_the_permissions_the_platform_will_ask_for_are_declared():
    """A foreground microphone service refused at start is a button that
    does nothing, and from Android 14 the typed permission is what the
    system checks the start against."""
    xml = MANIFEST.read_text(encoding="utf-8")
    for perm in ("android.permission.RECORD_AUDIO",
                 "android.permission.FOREGROUND_SERVICE",
                 "android.permission.FOREGROUND_SERVICE_MICROPHONE",
                 # The indicator is itself a permission from Android 13. A
                 # service whose notification can be silently withheld is
                 # exactly the thing this file is careful about.
                 "android.permission.POST_NOTIFICATIONS"):
        assert perm in xml, f"the manifest does not ask for {perm}"


def test_the_service_is_declared_typed_and_not_exported():
    xml = MANIFEST.read_text(encoding="utf-8")
    m = re.search(r"<service\b(.*?)/>", xml, re.S)
    assert m, "no service is declared in the manifest"
    block = m.group(1)
    assert 'android:name=".WalkService"' in block
    assert 'android:foregroundServiceType="microphone"' in block, (
        "the service is not typed as a microphone service; from Android 14 "
        "the start is refused, and before that the person is not told what "
        "kind of service is running")
    assert 'android:exported="false"' in block, (
        "the service is exported — anything on the phone could start this "
        "app's microphone")


def test_the_foreground_start_carries_the_microphone_type():
    src = SERVICE.read_text(encoding="utf-8")
    assert "startForeground(" in src, (
        "the service never goes to the foreground, so the system kills it "
        "and the notification the person is owed never appears")
    assert "FOREGROUND_SERVICE_TYPE_MICROPHONE" in src, (
        "the foreground start does not declare the microphone type")


def test_the_notification_says_it_and_can_end_it():
    """The whole justification for the feature is on this notification."""
    src = SERVICE.read_text(encoding="utf-8")
    assert "setOngoing(true)" in src, (
        "the notification can be swiped away, leaving a microphone open "
        "with nothing on screen saying so")
    assert "addAction(" in src, "the notification offers no way to stop it"
    # The action is the stop, not something else that happens to be an
    # action: it carries `walk.end` and it fires ACTION_STOP.
    # `nc.end` rather than a `walk.end` of its own: this shell already says
    # *End*, and a second row for one word gave a Hindi reader two spellings
    # of the same button.
    m = re.search(r"addAction\((.{0,300}?)\.build\(\)\)", src, re.S)
    assert m and 'L10n.t("nc.end"' in m.group(1), (
        "the notification's action is not the one that ends the "
        "conversation")
    assert 'setAction(ACTION_STOP)' in src, (
        "nothing builds the intent that stops the service")
    assert 'walk.note.body' in src, (
        "the notification never says the microphone is open")


def test_nothing_restarts_it_by_itself():
    """A service the system brings back after killing it is a microphone
    that reopens with nobody pressing anything — the one thing this must
    never be, and a one-word difference in the code."""
    src = SERVICE.read_text(encoding="utf-8")
    assert "START_NOT_STICKY" in src
    assert "START_STICKY" not in src, (
        "the service asks the system to restart it; nothing may reopen this "
        "microphone but a press")
    assert "START_REDELIVER_INTENT" not in src, (
        "the service asks the system to restart it with its arguments, "
        "which is the sticky problem carrying a token with it")


def test_a_superseded_turn_cannot_close_the_one_that_replaced_it():
    """The console's own defect, which cost a release: one shared flag meant
    a late callback from a stale recogniser closed the ear that had replaced
    it, and the microphone died a fifth of a second after it opened."""
    src = SERVICE.read_text(encoding="utf-8")
    assert re.search(r"val mine\s*=\s*\+\+turn", src), (
        "the listener takes no turn number, so a late callback from a "
        "superseded recogniser will act on the one that replaced it")
    assert re.search(r"fun live\(\)\s*=\s*mine == turn", src)
    for handler in ("onResults", "onError"):
        m = re.search(handler + r"\([^)]*\)\s*\{(.{0,120})", src, re.S)
        assert m and "live()" in m.group(1), (
            f"`{handler}` does not check that its session is still the live "
            "one")


def test_quiet_reopens_and_a_refusal_does_not():
    """A standing conversation treats quiet as a pause. Treating a refused
    microphone the same way is a loop that reopens forever with nothing to
    hear, and says nothing about why."""
    src = SERVICE.read_text(encoding="utf-8")
    m = re.search(r"override fun onError\(code: Int\)\s*\{(.*?)\n            \}",
                  src, re.S)
    assert m, "the service has no error handler"
    body = m.group(1)
    assert "ERROR_NO_MATCH" in body and "ERROR_SPEECH_TIMEOUT" in body, (
        "quiet is not separated from failure")
    assert "ERROR_INSUFFICIENT_PERMISSIONS" in body, (
        "a refused microphone is not distinguished, so it reads as quiet "
        "and the loop reopens into nothing")
    assert body.count("close(reason =") >= 3, (
        "the service has one way of failing; the console has already been "
        "caught by exactly that, where a refusal, an unreachable service "
        "and a defect all read the same")


def test_the_button_starts_it_and_the_same_button_ends_it():
    """A control that only starts something sends a person hunting through
    a notification shade for the way back out."""
    ui = (REPO / "native/android/app/src/main/java/app/qrme/studio/ui/"
          "Screens.kt").read_text(encoding="utf-8")
    assert "Walking.start(" in ui, "nothing on any screen starts a walk"
    assert "Walking.stop(" in ui, "the screen offers no way to end one"
    assert 'L10n.t("walk.take"' in ui and 'L10n.t("nc.end"' in ui, (
        "the control is unlabelled or labelled in one language")


def test_the_designation_rides_the_notification():
    """A person glancing at a notification from inside another app has the
    least context they will ever have, and it is the last place to leave
    *is this a person* to a guess. The estate's rule — the reader always
    knows it is an AI — does not stop at the edge of the app."""
    src = SERVICE.read_text(encoding="utf-8")
    assert 'L10n.t("walk.note.ai"' in src, (
        "the notification never says the profile is an AI")
    # The whole `val who =` expression, so the check survives the condition
    # growing a second clause (the agent) without the assertion loosening
    # into "the words appear somewhere in the file".
    block = src.split("val who =")[1].split("\n        val note")[0]
    assert 'shownName.lowercase().contains("ai")' in block, (
        "the designation is prepended unconditionally, so a name that "
        "already carries one reads as `AI · AI · Dana`")
    assert "else" in block and 'L10n.t("walk.note.ai"' in block, (
        "nothing prepends the designation to a name that lacks one, so a "
        "bare display name goes out undesignated")
    m = re.search(r"setContentTitle\((.{0,160}?)\)\n", src, re.S)
    assert m and "who" in m.group(1), (
        "the notification title does not carry the designated name")


def test_the_screen_says_why_it_stopped():
    """The same rule as the console's strip: silence and deafness look
    identical and are opposite facts."""
    ui = (REPO / "native/android/app/src/main/java/app/qrme/studio/ui/"
          "Screens.kt").read_text(encoding="utf-8")
    # The condition AND the render. The first draft asserted the name
    # `Walking.trouble` appeared anywhere in the file, and a sabotage that
    # replaced the condition with `if (false)` — leaving the now-unreachable
    # Text below it — passed happily. A branch that can never be taken is
    # exactly the shape of "shipped and never shown".
    assert re.search(
        r"if \(Walking\.trouble\.isNotEmpty\(\)\)\s*\{\s*\n?\s*"
        r"Text\(Walking\.trouble", ui), (
        "the screen never shows why the conversation stopped, so a refused "
        "microphone and a person pressing End look the same afterwards")


# ---------------------------------------------------------------------------
# Two conversations, one service.
#
# A synthetic profile answers through `POST /profiles/{id}/chat`; the console's
# agent answers through the authoring turn and keeps no memory of its own. The
# console met the same fork and answered it by handing the strip a callback —
# the screen knows its own wire, the strip stays ignorant. A Service cannot be
# handed a lambda across a start intent, so this one is told which kind it is
# carrying instead.
#
#     asked     can the service carry this conversation
#     mattered  how many wires does it have to know
#
# The agent's half brings a question the profile's half does not have: a row
# that cannot be taken back is answered by a press on a screen, and out here
# there is no screen.


def test_the_service_knows_which_conversation_it_is_carrying():
    src = SERVICE.read_text(encoding="utf-8")
    assert "KIND_PROFILE" in src and "KIND_AGENT" in src, (
        "the service carries only one kind of conversation; the console has "
        "two, and the agent is not the synthetic profile")
    assert "ApiClient.authoringTurn(" in src, (
        "nothing in the service takes an authoring turn, so the agent "
        "cannot be carried at all")
    assert "ApiClient.chat(" in src, "the profile's own wire is gone"


def test_the_agent_needs_no_interactor_and_the_profile_does():
    """The authoring turn is the owner's own door, reached with the owner's
    own token. Demanding an interactor for it would refuse every agent walk;
    not demanding one for a profile would start a chat with nobody."""
    src = SERVICE.read_text(encoding="utf-8")
    m = re.search(r"if \(profileId\.isEmpty\(\)(.{0,200}?)\{", src, re.S)
    assert m, "the service does not check what it was handed"
    assert "kind == KIND_PROFILE && interactorId.isEmpty()" in m.group(1), (
        "the interactor check does not distinguish the two kinds")


def test_the_agents_thread_is_carried_and_then_let_go():
    """The agent keeps no memory of its own — the cheaper design, and the one
    where *forget this* is something a person can actually do. Out here the
    transcript is the service's, and it must not outlive the walk."""
    src = SERVICE.read_text(encoding="utf-8")
    assert "thread.toList()" in src, (
        "the authoring turn is sent with no history, so the agent forgets "
        "between one sentence and the next")
    assert re.search(r"thread\.add\(\"user\"", src) and \
        re.search(r"thread\.add\(\"assistant\"", src), (
            "nothing accumulates the thread")
    assert "thread.clear()" in src, (
        "the transcript outlives the walk — a conversation somebody ended "
        "is still in memory afterwards")


def test_a_row_that_needs_a_press_is_said_and_not_done():
    """`asks` comes back instead of an act for the rows that cannot be taken
    back. A yes spoken into a phone in somebody's pocket is not the press
    that row is asking for."""
    src = SERVICE.read_text(encoding="utf-8")
    assert "turnTaken?.asks != null" in src, (
        "the walk does not check whether the turn came back as a proposal, "
        "so a confirming row's own sentence is never said and the person "
        "hears silence where a question was")
    assert 'L10n.fill("walk.agent.asks"' in src, (
        "the proposal is not put into words")
    # And it must not act on it out here. The one door that turns a proposal
    # into an act is `authoringAct`, and it has no business in a service with
    # no screen to press.
    assert "authoringAct" not in src, (
        "the service can complete a confirming row without a press — the "
        "press is the whole of the difference between *may this person do "
        "this* and *did this person mean this*")


def test_the_designation_is_for_the_profile_not_the_agent():
    """A synthetic profile stands in for a person and must say it is an AI.
    The agent is the console's own tool, named as itself — a designation
    prepended to it is noise, and noise is how a designation stops being read
    where it matters."""
    src = SERVICE.read_text(encoding="utf-8")
    assert "kind == KIND_AGENT" in src.split("val who =")[1][:200], (
        "the agent is given a synthetic profile's AI designation, or the "
        "profile is not given one — the two are not the same thing")


def test_the_agent_screen_offers_it_too():
    ui = (REPO / "native/android/app/src/main/java/app/qrme/studio/ui/"
          "Screens.kt").read_text(encoding="utf-8")
    assert "Walking.startAgent(" in ui, (
        "the agent screen offers no way to take the conversation out of the "
        "app, though the shell has had the authoring turn all along")


# ---------------------------------------------------------------------------
# Who answered, out where there is no screen.
#
# A deployment with no model key still answers — the offline stack does, from
# stored knowledge — and that has been true for releases. On the phone the
# person is in another application entirely, so the notification is the only
# surface they have and the only place this can be said.
#
#     asked     did the turn come back
#     mattered  who wrote it


def test_the_service_reads_who_answered():
    src = SERVICE.read_text(encoding="utf-8")
    assert "generatedBy" in src, (
        "the service never reads who wrote the turn, so a fallback answer "
        "is spoken as though the chosen model wrote it")
    assert 'generatedBy == "stub"' in src


def test_the_notification_says_it_and_stops_saying_it():
    src = SERVICE.read_text(encoding="utf-8")
    assert 'L10n.t("walk.offline"' in src, (
        "the notification never says the answer came from stored knowledge")
    # One notification, not one per turn: rewritten under the same id, and
    # only when the answer actually changed hands.
    assert "if (fromStore != Walking.offline)" in src, (
        "the notification is rebuilt on every turn rather than when the "
        "answerer changes, which is a notification that flickers all day")
    assert "Walking.offline = false" in src, (
        "the flag outlives the walk, so the next one starts by claiming a "
        "fallback answered a turn that has not happened yet")


def test_the_agent_branch_makes_no_claim_about_who_answered():
    """The authoring turn reports no provenance. A `false` there would be a
    claim nothing checked."""
    src = SERVICE.read_text(encoding="utf-8")
    agent = src.split("if (kind == KIND_AGENT) {")[1].split("} else {")[0]
    assert "fromStore" not in agent, (
        "the agent's branch decides who answered, and its wire does not "
        "report that")


# ---------------------------------------------------------------------------
# iOS: the other bargain.
#
# Android suspends an app when it leaves the screen and charges a foreground
# service with a notification that cannot be dismissed. iOS charges the
# `audio` background mode and draws the indicator itself — better, because a
# person learns one orange dot for every app rather than one notification per
# app.
#
#     asked     can the conversation survive a screen change
#     mattered  what does this platform charge for it

IOS_SPEC = REPO / "native/ios/project.yml"


def test_ios_declares_the_background_mode_and_both_permissions():
    spec = IOS_SPEC.read_text(encoding="utf-8")
    assert "UIBackgroundModes" in spec and "- audio" in spec, (
        "iOS is not declared as a background audio app, so the session is "
        "torn down the moment the app leaves the screen and the walk ends "
        "without saying why")
    assert "NSSpeechRecognitionUsageDescription" in spec, (
        "speech recognition is its own permission on iOS, and an app that "
        "asks for it without a string is killed on the spot")
    # The microphone string has to describe the walking case too. It is what
    # somebody reads in Settings months later, and describing only voice
    # enrollment would be true of one feature and false of the product.
    i = spec.index("NSMicrophoneUsageDescription:")
    said = spec[i:spec.index("NSSpeechRecognitionUsageDescription:", i)]
    assert "other apps" in said, (
        "the microphone permission string describes only voice enrollment; "
        "the app also listens while the person is elsewhere, and this string "
        "is where they find that out")
