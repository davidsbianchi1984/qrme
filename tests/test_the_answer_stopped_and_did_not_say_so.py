"""A long answer hit the wall mid-sentence and simply stopped.

## The finding

`llm.py` capped every reply at 1024 tokens, with the comment *"chat replies are
deliberately short"*. Short is right for a chat turn — and the same door
answers *write me the migration* and *explain both patents*. Those replies ran
out of room, and what a person got was a sentence that ended in the middle of
itself with nothing to say it had.

    asked     is the reply short enough to read
    mattered  can a person tell a truncation from a model losing the thread

Those two call for opposite responses — ask it to continue, or start over — and
the reader had no way to choose.

## Both halves, because a bigger wall is still a wall

The room went up tenfold. That fixes the common case and cannot fix the case
that matters, so the second half is the one under test here: when a provider
stops because it ran out of room rather than because it finished, the reply
says so. Every provider reports that differently — `stop_reason`,
`finish_reason`, `finishReason` — which is exactly the kind of detail one
adapter gets right and the next one quietly does not.

## The platform's sentence, not the persona's

The marker is the platform speaking, so it is registered in `i18n._PUBLIC` and
travels through `tr_public` like every other sentence this platform says to a
person. A model asked to write in Hindi does not also get to decide how the
platform announces its own truncation.
"""

from __future__ import annotations

import pytest

from qrme import i18n, llm


# --- the budget ------------------------------------------------------------

def test_the_budget_is_one_room():
    """The field call, kept as a number this test can name.

    A staircase, every step of it a field report. 1024 was the old wall.
    It went to ten times that for a while; the field called it back to
    five; the same reviewer sent five back too — "still a long delay
    while waiting for a response — drop it to 2.5" — and then, having
    lived with 2.5, sent that back as well: "can we reduce the ceiling
    2.5X, it's still a little long-winded".

    So: back to 1024, which is where it started. The whole staircase was
    somebody reading real replies and saying they were too long, and the
    truncation notice below is what made every step safe — hitting the
    wall is said out loud, so a shorter wall costs a sentence and never
    costs the reader the knowledge that there was more.
    """
    assert llm.MAX_REPLY_TOKENS == 1024


def test_every_provider_asks_for_the_same_room():
    """A per-provider literal is how one model keeps the old ceiling while the
    release notes say otherwise.

    Reading the *code* lines only. The first draft of this scanned the whole
    module for "1024" and failed on the paragraph above `MAX_REPLY_TOKENS`
    explaining what 1024 used to be — a checker that cannot tell a number from
    a sentence about a number.
    """
    import inspect
    import re

    # Only the forms that *set* a budget. A looser pattern also matched
    # `stop_reason == "max_tokens"`, which is the code reading the answer to
    # this question rather than asking it — a checker that cannot tell the
    # two apart would fail on the fix.
    sets = re.compile(r'max_tokens\s*=|"max_tokens"\s*:|"maxOutputTokens"\s*:')
    asks = [line.strip() for line in inspect.getsource(llm).splitlines()
            if sets.search(line) and not line.lstrip().startswith("#")]
    assert asks, "nothing in llm.py asks for a token budget any more"
    stray = [a for a in asks if "MAX_REPLY_TOKENS" not in a]
    assert not stray, (
        "a provider carries its own number, which is a provider with its own "
        "wall:\n    " + "\n    ".join(stray))


# --- the marker ------------------------------------------------------------

def test_a_finished_answer_says_nothing_extra():
    """The marker must be rare enough to mean something. A sentence appended
    to every reply is a sentence people stop reading."""
    assert llm._capped("all done.", False) == "all done."
    assert llm.CONTINUES not in llm._capped("all done.", False)


def test_an_answer_that_ran_out_says_so():
    said = llm._capped("def migrate():\n    pass\n\ndef next_step(", True)
    assert said.endswith(llm.CONTINUES), said
    assert "def migrate()" in said, "the partial answer is kept, not replaced"


def test_an_empty_answer_that_ran_out_is_still_explained():
    """Thinking can consume the whole budget and leave no text at all. An empty
    reply with no explanation is the worst version of this bug, not the
    harmless one."""
    assert llm._capped("", True) == llm.CONTINUES


# --- each provider reads its own signal ------------------------------------

class _Fake:
    """Enough of a provider response to answer the one question."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_anthropic_reads_stop_reason(monkeypatch):
    block = _Fake(type="text", text="half a thought")
    provider = llm.AnthropicProvider.__new__(llm.AnthropicProvider)
    provider._client = _Fake(messages=_Fake(create=lambda **kw: _Fake(
        content=[block], stop_reason="max_tokens")))
    assert provider.generate("s", []).endswith(llm.CONTINUES)


def test_anthropic_says_nothing_when_it_finished():
    block = _Fake(type="text", text="a whole thought")
    provider = llm.AnthropicProvider.__new__(llm.AnthropicProvider)
    provider._client = _Fake(messages=_Fake(create=lambda **kw: _Fake(
        content=[block], stop_reason="end_turn")))
    assert provider.generate("s", []) == "a whole thought"


def test_anthropic_asks_for_the_budget():
    """The number actually leaving the process, not the constant beside it."""
    seen = {}

    def create(**kw):
        seen.update(kw)
        return _Fake(content=[], stop_reason="end_turn")

    provider = llm.AnthropicProvider.__new__(llm.AnthropicProvider)
    provider._client = _Fake(messages=_Fake(create=create))
    provider.generate("s", [])
    assert seen["max_tokens"] == llm.MAX_REPLY_TOKENS


@pytest.mark.parametrize("reason,marked", [("length", True),
                                           ("stop", False)])
def test_openai_shaped_providers_read_finish_reason(monkeypatch, reason, marked):
    body = {"choices": [{"message": {"content": "half a thought"},
                         "finish_reason": reason}]}
    monkeypatch.setattr(llm, "_post_json", lambda *a, **k: body)
    provider = llm.OpenAICompatibleProvider("x", "https://e", "k", "m")
    assert provider.generate("s", []).endswith(llm.CONTINUES) is marked


def test_openai_shaped_providers_ask_for_the_budget(monkeypatch):
    sent = {}

    def post(url, payload, headers):
        sent.update(payload)
        return {"choices": [{"message": {"content": "hi"},
                             "finish_reason": "stop"}]}

    monkeypatch.setattr(llm, "_post_json", post)
    llm.OpenAICompatibleProvider("x", "https://e", "k", "m").generate("s", [])
    assert sent["max_tokens"] == llm.MAX_REPLY_TOKENS


@pytest.mark.parametrize("reason,marked", [("MAX_TOKENS", True),
                                           ("STOP", False)])
def test_gemini_reads_its_own_spelling(monkeypatch, reason, marked):
    """`finishReason`, camel-cased and shouting. Its own adapter, its own
    chance to miss this."""
    body = {"candidates": [{"content": {"parts": [{"text": "half"}]},
                            "finishReason": reason}]}
    monkeypatch.setattr(llm, "_post_json", lambda *a, **k: body)
    provider = llm.GeminiProvider("k", "m")
    assert provider.generate("s", []).endswith(llm.CONTINUES) is marked


def test_gemini_asks_for_the_budget(monkeypatch):
    sent = {}

    def post(url, payload, headers):
        sent.update(payload)
        return {"candidates": [{"content": {"parts": [{"text": "hi"}]},
                                "finishReason": "STOP"}]}

    monkeypatch.setattr(llm, "_post_json", post)
    llm.GeminiProvider("k", "m").generate("s", [])
    assert sent["generationConfig"]["maxOutputTokens"] == llm.MAX_REPLY_TOKENS


# --- the sentence is the platform's ----------------------------------------

def test_the_marker_is_translated_everywhere_the_platform_speaks():
    missing = [lang for lang in i18n.SUPPORTED
               if lang != i18n.DEFAULT
               and i18n.tr_public(llm.CONTINUES, lang) == llm.CONTINUES]
    assert not missing, (
        "the truncation marker is English-only in: " + ", ".join(missing)
        + " — it is the platform speaking, and this platform speaks ten")
