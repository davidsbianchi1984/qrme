"""An orb that says "listening" over a dead microphone is lying.

Field report, screenshot attached in the session: voice mode on, the orb
glowing "Listening — say it", and nothing ever heard. The recogniser had
no `onerror` at all, so a refused microphone, a missing input device, or
an unreachable speech service fell through to `onend` — whose job is to
relight after a quiet stretch. The failure loop: error → onend → relight
→ error, with the orb glowing through all of it.

    asked     does the orb say it is listening
    mattered  is anything actually able to hear

Three causes a person can act on are named now, each stopping the relight
loop; the quiet ends (`no-speech`) keep relighting, because leaving a
room empty is not an error.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENT = (REPO / "app/src/screens/Agent.tsx").read_text(encoding="utf-8")
L10N = (REPO / "app/src/l10n.ts").read_text(encoding="utf-8")

LANGS = ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")


def test_both_ears_have_an_onerror():
    """The voice orb's recogniser and the dictation mic's — the same API,
    the same silent death without one."""
    assert AGENT.count("r.onerror = (e: { error?: string })") == 2, (
        "a recogniser lost its onerror — its failures fall through to "
        "onend again, which relights the lie")


def test_the_three_actionable_causes_are_named():
    for code, key in (("not-allowed", "agent.ear.blocked"),
                      ("audio-capture", "agent.ear.nomic"),
                      ("network", "agent.ear.unreachable")):
        assert code in AGENT, f"the {code} cause is no longer distinguished"
        assert f'tr("{key}", lang)' in AGENT


def test_a_fatal_error_stops_the_relight_loop():
    m = re.search(r"r\.onend = \(\) => \{\n      recogniser\.current(.*?)\n    \};",
                  AGENT, re.S)
    assert m, "the voice orb's onend is gone"
    body = m.group(1)
    assert "if (fatal) return;" in body, (
        "onend relights after a fatal error — error, onend, relight, "
        "error, with the orb glowing through all of it")
    assert "startVoice(false)" in body, (
        "the quiet-stretch relight is gone — a silence would end voice "
        "mode entirely, which is the opposite over-correction")


def test_the_fault_outranks_listening_on_the_orb():
    assert re.search(r"earFault \?\? tr\(\"agent.orb.listening\"", AGENT), (
        "the orb label ignores the fault — it says \"listening\" over a "
        "microphone the browser refused")


def test_every_fault_sentence_speaks_ten_languages():
    for key in ("agent.ear.blocked", "agent.ear.nomic",
                "agent.ear.unreachable"):
        block = re.search(rf'"{re.escape(key)}":\s*\{{(.*?)\n  \}}', L10N, re.S)
        assert block, f"{key} is not on the console's table"
        for lang in LANGS:
            assert re.search(rf"\b{lang}:", block.group(1)), (
                f"{key} has no {lang} translation")
