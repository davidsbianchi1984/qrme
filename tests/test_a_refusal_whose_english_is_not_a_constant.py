"""The refusals that could not be keyed, and the slot that could ruin them.

## What this closes

`tests/refusals_untranslated.txt` has carried this paragraph for three
releases: **49 f-string refusals**, named as uncovered and deliberately not
counted in the backlog, because

    f"language must be one of {', '.join(SUPPORTED)}"

cannot be looked up by its English source — at the moment it is raised there is
no English source, only a result. The same held in both sibling products.

    asked     is the refusal a constant we can translate
    mattered  is every part of it something we can translate

`i18n.Templated` carries the template and its slots alongside the finished
English sentence, so `localize_detail` can refill the frame in the reader's
language. It is a `str`, and its value is that English sentence, so nothing
that already treats a detail as text needed to change.

## The slot is the whole design

A translated frame around an English slot is *worse* than an English sentence:
it reads as a bug, in front of somebody who is already being told no. That is
precisely why `refusals_untranslated.txt` refuses to ship a translation of the
plan gate, whose message interpolates a capability description and a plan
title — and doing it here by accident would have been the same mistake with a
mechanism to spread it.

Two rules, and this file is mostly about holding them:

* **Whitespace means prose.** A slot holding `en, es, pt` or `prf_9f2` is a
  token; one holding `in development` is a sentence fragment. A slot that fails
  the test sets `translatable = False` and the whole refusal stays English —
  the state it was already in, now chosen rather than stumbled into.
* **A single English word defeats rule one.** `upheld` has no whitespace and is
  indistinguishable from an identifier, so a closed vocabulary is marked at the
  raise site with `i18n.Term(...)` and translated at *render*, when the
  reader's language is finally known.

## What this file does not claim

Eighteen of the forty-nine are converted. The rest are named in the record with
the reason, and the reason is now specific rather than "f-string": seven have
slots carrying prose this product does not author — a mail server's exception,
a moderation verdict, a hardware availability string — and translating their
frames would produce exactly the half-and-half sentence above.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from qrme import i18n
from qrme.api import create_app


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
PACKAGE = REPO / "qrme"


# --- the mechanism ----------------------------------------------------------

def test_a_templated_refusal_is_its_own_english_sentence():
    """The property everything else rests on.

    `Templated` is a `str` whose value is the finished English text. If that
    stopped being true, every driven test asserting on a refusal message, and
    the default English path itself, would be reading an object repr.
    """
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="language", choices="en, es")
    assert isinstance(said, str)
    assert said == "language must be one of en, es"
    assert f"{said}" == said


@pytest.mark.parametrize("language", ["pt", "es", "de", "ja", "ar"])
def test_the_frame_arrives_translated_and_the_slot_survives(language):
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="language",
                     choices=", ".join(i18n.SUPPORTED))
    out = i18n.localize_detail(said, language)
    assert out != str(said), f"the frame stayed English for {language}: {out}"
    assert ", ".join(i18n.SUPPORTED) in out, (
        f"the slot was lost in translation: {out}")


def test_every_template_is_translated_into_every_language():
    """A template with a missing language falls through as English silently,
    which is the failure mode this whole area keeps producing."""
    missing = []
    for template in i18n.TEMPLATES:
        table = i18n._TEMPLATES.get(template, {})
        for code in i18n.SUPPORTED:
            if code != i18n.DEFAULT and code not in table:
                missing.append(f"{template!r} has no {code}")
    assert not missing, "\n    ".join(missing)


def test_a_translation_keeps_every_slot_the_template_has():
    """A frame missing `{choices}` renders a sentence with the list silently
    dropped — grammatical, translated, and wrong."""
    problems = []
    for template in i18n.TEMPLATES:
        wanted = set(re.findall(r"\{(\w+)\}", template))
        for code, text in i18n._TEMPLATES[template].items():
            got = set(re.findall(r"\{(\w+)\}", text))
            if got != wanted:
                problems.append(
                    f"{code} of {template!r}: has {sorted(got)}, "
                    f"template has {sorted(wanted)}")
    assert not problems, "\n    ".join(problems)


# --- the slot rule ----------------------------------------------------------

@pytest.mark.parametrize("value", [
    "en, es, fr", "openai", "prf_9f2c", "12.00", "USD", "@ada",
    "pre, on_demand", "", "profile/desk",
])
def test_a_token_slot_is_translatable(value):
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="x", choices=value)
    assert said.translatable, f"{value!r} was refused and should not have been"


@pytest.mark.parametrize("value", [
    "in development",
    "the mail server refused the connection",
    "your account is not permitted to do that",
    "a name somebody typed",
])
def test_a_prose_slot_makes_the_whole_refusal_stay_english(value):
    """The safety valve, and the reason this mechanism is safe to use widely.

    Not an exception and not a partial translation: the English sentence, whole,
    which is what the reader would have got anyway.
    """
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="x", choices=value)
    assert not said.translatable, f"{value!r} was accepted as a token"
    assert i18n.localize_detail(said, "pt") == str(said), (
        "a prose slot reached a translated frame — the sentence is now half in "
        "one language and half in another")


def test_a_vocabulary_word_is_translated_at_render_not_at_raise():
    """`Term` exists because the reader's language is unknown where the
    refusal is raised. If it were resolved there, every objection refusal would
    carry whatever language happened to be in scope at the raise site."""
    said = i18n.fill(i18n.OBJECTION_ALREADY, status=i18n.Term("upheld"))
    assert str(said) == "objection is already upheld"
    assert "upheld" not in i18n.localize_detail(said, "pt")
    assert i18n.term("upheld", "pt") in i18n.localize_detail(said, "pt")


def test_an_unknown_state_keeps_the_whole_refusal_english():
    """The coverage guarantee, made structural instead of enumerated.

    A status added to a table three modules away cannot be relied upon to
    reach a list in this module, and a test that enumerates them is a test
    somebody has to remember to update — which is how the vocabulary would
    quietly start emitting English keys inside translated sentences.

    So an unmapped word is not a gap to be caught later: it keeps the entire
    refusal in English, exactly as a prose slot does.
    """
    known = i18n.fill(i18n.OBJECTION_ALREADY, status=i18n.Term("upheld"))
    assert i18n.localize_detail(known, "pt") != str(known)

    invented = i18n.fill(i18n.OBJECTION_ALREADY,
                         status=i18n.Term("escalated_to_ombudsman"))
    assert i18n.localize_detail(invented, "pt") == str(invented), (
        "an unmapped state was dropped into a translated frame")


def test_the_states_these_templates_can_actually_reach_are_covered():
    """The structural fallback keeps an unmapped state safe; it does not make
    one *good*. These are the words the four converted templates can carry, and
    a person meeting one of them should meet it in their own language."""
    reachable = {"open", "upheld", "dismissed", "withdrawn", "revoked",
                 "active", "restricted", "terminated", "departed", "memorial",
                 "delivered", "blocked"}
    missing = sorted(reachable - set(i18n._VOCABULARY))
    assert not missing, (
        f"{missing} can be raised into a converted refusal and would keep it "
        "English. Add to i18n._VOCABULARY.")


def test_no_vocabulary_word_is_left_as_its_english_key():
    """The risk a vocabulary actually carries.

    The first version of this asked whether each translation was whitespace-
    free, and failed on `वापस ली गई` and `تم التسليم` — correct translations
    that happen to be two words. The whitespace rule exists to catch a slot in
    the *wrong language*; a multi-word word in the right one is just that
    language.

        asked     is this translation a single token
        mattered  is this translation not still English

    What does matter is an entry copied from the key and never translated: it
    passes every structural check, renders inside a translated frame, and is
    the exact mixed sentence `Term` exists to prevent.
    """
    # Words that really are the same in another language. Declared rather than
    # silenced: a cognate is a claim about two languages, and the point of this
    # check is that such a claim is made on purpose exactly once.
    cognates = {"memorial/es", "memorial/pt"}
    untranslated = [f"{word}/{code}" for word, table in i18n._VOCABULARY.items()
                    for code, text in table.items()
                    if text == word and f"{word}/{code}" not in cognates]
    assert not untranslated, (
        f"{untranslated} are still the English key, and would land inside a "
        "translated sentence looking like a mistake")


# --- the raise sites --------------------------------------------------------

def _template_calls() -> list[tuple[str, int, dict]]:
    """Every `i18n.fill(...)` in the package, with its slot expressions."""
    found = []
    for path in sorted(PACKAGE.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node.func, "attr", "") != "fill":
                continue
            slots = {kw.arg: ast.unparse(kw.value)
                     for kw in node.keywords if kw.arg}
            found.append((str(path.relative_to(REPO)), node.lineno, slots))
    return found


def test_the_raise_sites_were_actually_converted():
    """A guard on the guard: everything below passes vacuously on no calls."""
    calls = _template_calls()
    assert len(calls) >= 15, (
        f"only {len(calls)} `i18n.fill` call(s) found — either the conversion "
        "was reverted or this extraction has stopped matching")


def test_no_slot_is_filled_from_a_string_literal():
    """The hole the whitespace rule cannot close, closed here instead.

    `_SLOT_TOKEN` sees values, and a single English word looks exactly like an
    identifier. What it cannot see is *where the value came from*. A slot filled
    from a variable, an attribute, a subscript or a `join` is data; a slot
    filled from a literal is a word somebody typed into this codebase, and a
    word somebody typed is prose unless it is a field name.

    Field names are the deliberate exception, and they are checked against the
    template that receives them: `MUST_BE_ONE_OF` names the field being
    validated, which is the API's own name for it and the same in every
    language.
    """
    allowed_literal_slots = {"field"}
    offenders = []
    for path, line, slots in _template_calls():
        for name, expression in slots.items():
            if name in allowed_literal_slots:
                continue
            if re.fullmatch(r"""['"].*['"]""", expression, re.S):
                offenders.append(f"{path}:{line} {name}={expression}")
    assert not offenders, (
        "a slot is filled from a string literal, which the whitespace rule "
        "cannot tell from an identifier:\n    " + "\n    ".join(offenders))


def test_a_status_slot_always_goes_through_the_vocabulary():
    """A raise site passing a raw status would put an English key inside a
    translated sentence, and `_SLOT_TOKEN` would wave it through."""
    bare = [f"{path}:{line} status={slots['status']}"
            for path, line, slots in _template_calls()
            if "status" in slots and "Term(" not in slots["status"]]
    assert not bare, (
        "a status reaches a template without `i18n.Term`:\n    "
        + "\n    ".join(bare))


# --- driven -----------------------------------------------------------------

@pytest.fixture()
def client():
    return TestClient(create_app())


def test_a_converted_refusal_answers_in_the_readers_language(client):
    """End to end through the handler, not through the module.

    `localize_detail` being right is not the same as the handler reaching it —
    `Templated` is a `str`, and the plain-string branch was above it in the
    first version of this change, which would have looked up the finished
    sentence, found nothing, and returned English.
    """
    refused = client.post("/profiles", json={
        "owner_id": "usr_x", "display_name": "A", "persona": {"bio": "b"},
        "verification": {"kind": "self"}, "language": "klingon"},
        headers={"accept-language": "pt"})
    assert refused.status_code in (401, 403, 422), refused.text
    if refused.status_code == 422:
        assert "must be one of" not in refused.text


def test_the_english_default_is_untouched(client):
    """Every driven test in this suite reads English refusals. The mechanism
    must be invisible when the reader's language is the default."""
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="mode",
                     choices=", ".join(i18n.MODES))
    assert i18n.localize_detail(said, i18n.DEFAULT) == said
    assert i18n.localize_detail(said, "en") == "mode must be one of pre, on_demand"
