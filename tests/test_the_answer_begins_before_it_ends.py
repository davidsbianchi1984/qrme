"""The answer begins before it ends.

Field report, and the twin product's the same week: "still a long delay
while waiting for a response." The synthesis leg of that wait was being
paid in full — the whole reply became one utterance before a word of it
played.

    asked     when does the answer start being heard
    mattered  does the wait grow with the length of the answer

`speakInPieces` (app/src/spoken.ts) cuts a reply at sentence ends and
pipelines: the first sentence is synthesised alone — small, so it comes
back fast — and every later piece is fetched while the one before it
plays. Every screen that speaks a profile's bound voice goes through it,
so none of them can drift back to the one-big-utterance wait. The
splitter itself is executed through node, not pinned by regex.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import ratchets

REPO = Path(__file__).resolve().parents[1]
SPOKEN = (REPO / "app/src/spoken.ts").read_text(encoding="utf-8")

_RUNNER = """
const ts = require("typescript");
const fs = require("fs");
const src = fs.readFileSync("src/pieces.ts", "utf8");
const js = ts.transpileModule(src, {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText;
const mod = { exports: {} };
new Function("exports", "module", js)(mod.exports, mod);
const texts = JSON.parse(fs.readFileSync(0, "utf8"));
console.log(JSON.stringify(texts.map((t) => mod.exports.spokenPieces(t))));
"""


def _pieces(*texts: str) -> list[list[str]]:
    proc = subprocess.run(
        ["node", "-e", _RUNNER], cwd=REPO / "app", input=json.dumps(texts),
        capture_output=True, text=True)
    assert proc.returncode == 0, f"the splitter will not run:\n{proc.stderr}"
    return json.loads(proc.stdout)


# -- the splitter, run for real ----------------------------------------------

def test_a_short_reply_is_one_piece_unchanged():
    [pieces] = _pieces("It went well today.")
    assert pieces == ["It went well today."]


#: A long answer, as one. Held here rather than built inside the test so the
#: floor under the split counts the split rather than the sentence.
LONG_ANSWER = "The interview went fine. " + " ".join(
    f"Then question {i} came and I answered it." for i in range(1, 9))


def test_the_first_sentence_rides_alone_and_nothing_is_lost():
    text = LONG_ANSWER
    [pieces] = _pieces(text)
    assert pieces[0] == "The interview went fine.", (
        "the first piece must be the first sentence alone — it is the one "
        "somebody is waiting on")
    assert len(pieces) >= ratchets.floor("speech.pieces_from_a_long_answer")
    assert " ".join(pieces) == text, "no word may be lost or invented"


def test_a_decimal_and_a_title_are_not_sentence_ends():
    [a, b] = _pieces("It cost 2.5 times as much. Worth it.",
                     "Dr. Petrova disagreed. Politely.")
    assert a[0] == "It cost 2.5 times as much."
    assert b[0] == "Dr. Petrova disagreed."


def test_a_long_answer_is_a_few_requests_not_thirty():
    text = " ".join(f"Sentence number {i} of this answer." for i in range(30))
    [pieces] = _pieces(text)
    assert 1 < len(pieces) <= 8, (
        "grouping is the point: thirty sentences must not become thirty "
        "round trips to the synthesis engine")


# -- the pipeline ------------------------------------------------------------

def test_the_pipeline_prefetches_and_the_first_piece_gates():
    assert "api.sayInProfileVoice(profileId, pieces[i + 1], token)" in SPOKEN, (
        "the next piece must be fetched while the current one plays — "
        "without the prefetch the pauses between sentences are the same "
        "wait, paid in instalments")
    assert "await api.sayInProfileVoice(profileId, pieces[0], token)" in SPOKEN, (
        "the first piece must be awaited before the handle exists, so a "
        "caller with no binding or engine still takes its device fallback")


def test_every_speaking_screen_goes_through_the_pieces():
    # Voice.tsx keeps its direct call: its one utterance is the fixed,
    # one-sentence binding test line, which is a single piece by
    # definition. Every conversational screen speaks through the pipeline.
    for screen in ("Agent", "Chat", "Inside"):
        src = (REPO / f"app/src/screens/{screen}.tsx").read_text("utf-8")
        assert "speakInPieces(" in src, (
            f"{screen}.tsx no longer speaks piece by piece")
        assert "sayInProfileVoice" not in src, (
            f"{screen}.tsx calls the synthesis door directly — the whole "
            "reply is one utterance again, and the wait grows with it")


def test_closing_the_orb_stops_the_whole_reply_not_one_piece():
    agent = (REPO / "app/src/screens/Agent.tsx").read_text("utf-8")
    assert "playing.current?.stop()" in agent, (
        "pausing only the playing audio lets the next piece start — the "
        "handle's stop() is what drops the remainder")


def test_the_runbook_names_the_standing_door():
    doc = (REPO / "docs/beta-deploy.md").read_text("utf-8")
    assert "local_model_standing" in doc, (
        "§8d's 'prove it end to end' should point at the vault's own "
        "posture door instead of leaving the proof to a conversation")
