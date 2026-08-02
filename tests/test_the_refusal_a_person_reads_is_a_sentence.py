"""A 422 is a list, and no client could show a person a list.

## The finding

0.30.0 put every refusal this product raises into the reader's language.
0.30.1 caught the one it had missed — `RequestValidationError`, the 422 a
mistyped form produces, which went out past the handler carrying pydantic's
`input` key — and translated its `msg` too.

Nobody looked at what a client does with the result. `detail` on a 422 is a
*list* of rows, and every one of this product's four client families rendered
it by a path written for a string:

* the console called `JSON.stringify` on it, so the note under the form read
  `[{"type":"missing","loc":["body","display_name"],"msg":"Field required"}]`;
* Android's `JSONObject.optString("detail")` coerces a `JSONArray` through
  `toString()`, producing the same thing;
* iOS asked for `as? String`, got `nil`, and fell back to `HTTP 422`;
* Windows called `GetString()` on an array element, which throws, was caught,
  and fell back to `HTTP 422`.

        asked     is the refusal translated
        mattered  is the refusal a sentence

The `msg` translated in 0.30.1 was correct, arrived, and was never read by
anybody: it sat inside a JSON blob, or was discarded for a status code. Two of
the four families showed the person *less* than before their language was
considered at all.

## What this checks

The sentence is composed on the server (`i18n.validation_message`) rather than
in each client, for the reason the refusal handler is one handler: four
renderings of one thing are four chances to render it differently, and three of
these have no test runner in this repository.

So the driven half below holds the server to composing it, translating it, and
— the part that matters most — putting nothing in it that is not already in
the rows. The structural half holds each client to *reading* it, which is all a
source-level check can honestly claim; see
`test_native_shells_record_nothing_private.py` for the same limit stated the
same way.

## What is still not right

The field name in the sentence is the API's name — `display_name`, not the
label the form shows. It is joined with an em dash rather than declined into
the sentence, so nothing reads as half-translated, but a person looking at a
field captioned *"Nome de exibição"* is told about `display_name`. Mapping the
two needs a per-client table that does not exist. Written down here rather than
guessed at.
"""

from __future__ import annotations

import json
import pathlib
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


@pytest.fixture()
def client():
    return TestClient(create_app())


# --- driven: what the server sends ------------------------------------------

def test_a_mistyped_form_answers_with_a_sentence(client):
    """The defect, directly. Before this, `message` did not exist and the only
    human-readable thing in the body was buried in a list."""
    refused = client.post("/profiles", json={"kind": "self"})
    assert refused.status_code == 422
    said = refused.json().get("message")
    assert isinstance(said, str) and said.strip(), (
        "a 422 carries no `message`, so every client is back to rendering the "
        f"`detail` list: {refused.text[:200]}")
    assert not said.lstrip().startswith(("[", "{")), (
        f"the sentence is still a serialised structure: {said[:120]}")
    # `Profile name`, not `display_name`: 0.40.8 gave the sentence the label
    # the form shows. Matched on the word rather than the identifier, so this
    # asserts the shape — a field and a message, in prose — and leaves the
    # wording to the label table, where it is checked against the console.
    assert "name" in said.lower() and "Field required" in said


def test_the_rows_are_still_there(client):
    """`detail` keeps its shape.

    It is the FastAPI contract, a machine reading this API has every right to
    the rows, and the driven tests in this suite read them. A sentence that
    replaced them would fix one client family by breaking every other caller.
    """
    body = client.post("/profiles", json={"kind": "self"}).json()
    assert isinstance(body["detail"], list) and body["detail"]
    for row in body["detail"]:
        assert set(row) == {"type", "loc", "msg"}, (
            f"a row grew a key: {sorted(row)}")


def test_the_sentence_says_no_more_than_the_rows(client):
    """The whole reason 0.30.1 existed, applied to the thing it added.

    A sentence composed from the rows can only leak by composing from
    something else. Every word of it must be traceable to a `loc` part or a
    `msg`, and the value that failed must not appear — which is exactly what
    went wrong the first time, when pydantic's `input` key handed the entire
    submitted body back.
    """
    secret = "a-medication-name-nobody-should-see"
    refused = client.post("/profiles", json={
        "kind": "self", "display_name": {"nested": secret}})
    assert refused.status_code == 422
    body = refused.json()
    assert secret not in json.dumps(body), (
        "the submitted value came back — in the sentence, the rows, or both")

    accounted = set()
    for row in body["detail"]:
        accounted.update(str(p) for p in row["loc"])
        accounted.add(row["msg"])
    # ...and the field labels, which are constants in `i18n._FIELD_LABELS`.
    #
    # 0.40.8 gave the sentence a third source: the label the form shows, so a
    # person reads "Nome do perfil" where the API says `display_name`. That is
    # a real weakening of the rule this test enforces, and this test is what
    # caught it — the rule is mechanical on purpose, so that nothing has to
    # reason about whether a given source happens to be safe.
    #
    # Widened by *naming* the new source rather than by relaxing the match:
    # a constant table cannot carry a submitted value, and
    # `test_no_label_is_built_from_anything_but_a_constant` holds it to that.
    # The rule still forbids the thing it was written for — composing the
    # sentence from the body.
    accounted.update(v for row in i18n._FIELD_LABELS.values()
                     for v in row.values())
    for piece in re.split(r" — |; ", body["message"]):
        assert piece in accounted or piece.split(".")[-1] in accounted, (
            f"{piece!r} is in the sentence and in none of the rows, so the "
            "sentence is composed from something other than the rows")


@pytest.mark.parametrize("language", ["pt", "es", "ja"])
def test_the_sentence_arrives_in_the_readers_language(client, language):
    refused = client.post("/profiles", json={"kind": "self"},
                          headers={"accept-language": language})
    said = refused.json()["message"]
    assert "Field required" not in said, (
        f"the sentence is English for a {language} reader: {said}")
    assert i18n.tr_refusal("Field required", language) in said


def test_the_sentence_is_wholly_in_one_language(client):
    """Half in one language and half in another is the failure
    `refusals_untranslated.txt` refuses to ship for the plan gate.

    This used to be `test_the_field_name_is_not_translated_and_that_is_
    deliberate`, and it was right at the time: the field name was the API's
    identifier, the same string everywhere, joined with an em dash rather than
    declined into the sentence, so it read as an identifier rather than a word
    somebody forgot to translate.

    0.40.8 gave the fields a person types into a form the label the form shows,
    in all ten languages — so the Portuguese sentence is Portuguese on both
    sides of the dash, which is what the rule was protecting. The half of the
    decision that still stands is below: a field with **no** label keeps its
    identifier, on purpose.
    """
    said = client.post("/profiles", json={"kind": "self"},
                       headers={"accept-language": "pt"}).json()["message"]
    assert " — " in said, said
    assert "display_name" not in said, (
        f"the identifier is still in the sentence: {said!r}")


def test_an_unlabelled_field_still_keeps_its_identifier(client):
    """The half of the old decision that survives. An identifier a reader can
    match to the form beats a word invented for them."""
    said = i18n.validation_message(
        [{"loc": ["body", "aging_enabled"], "msg": "x"}], "pt")
    assert "aging_enabled" in said


def test_a_body_that_is_not_an_object_still_says_something(client):
    """`loc` is `["body"]` alone here — no field to name. The sentence must not
    come out as a bare em dash with nothing on either side of it."""
    refused = client.post("/profiles", content=b"not json",
                          headers={"content-type": "application/json"})
    assert refused.status_code == 422
    said = refused.json()["message"]
    assert said.strip() and not said.strip().startswith("—"), (
        f"a bodiless 422 composed {said!r}")


def test_an_unrecognised_field_name_is_readable_in_the_sentence():
    """`validation_detail` substitutes a placeholder where a caller's own key
    would be echoed. It is the one 'field name' that is prose, so it is the one
    that has to be translated when it lands in the sentence."""
    rows = i18n.validation_detail(
        [{"type": "extra_forbidden", "loc": ["body", "a key with spaces"],
          "msg": "Extra inputs are not permitted"}], "pt")
    said = i18n.validation_message(rows, "pt")
    assert i18n.UNRECOGNISED_FIELD not in said, (
        f"the placeholder stayed English inside a Portuguese sentence: {said}")
    assert "a key with spaces" not in said



# --- structural: what each client does with it ------------------------------
#
# Per client, never unioned, and with a *different question per client*,
# because the four decode a refusal in four genuinely different ways.
#
# The first version of this section asked one question of all four — does the
# source mention `message` — and passed on all four while every one of them was
# still broken: `message` is a field on a chat model, a parameter name on an
# exception class, and a word in the comments directly above the bug.
#
# The second version anchored on the throw and asked whether the surrounding
# lines read `message`. That caught iOS, Android and Windows, and still passed
# on a broken console — because the console's fallback chain has always read
# `body.message` as an *alternative to* `detail`, so the words were present in
# a window where the sentence was being dropped on the floor.
#
#     asked     does the decode mention the sentence
#     mattered  does the decode pass the sentence on
#
# So the console is checked on the thing that actually carries it — the third
# argument to `RequestError` — and the three shells on the JSON key, which in
# those three files appears nowhere else.

CONSOLE = REPO / "app/src/api.ts"

SHELLS = {
    "ios": (REPO / "native/ios/Sources/ApiClient.swift",
            r"throw ApiError\.http\("),
    "android": (next((p for p in (REPO / "native/android").rglob("ApiClient.kt")),
                     None),
                r"throw ApiException\("),
    "windows": (REPO / "native/windows/ApiClient.cs",
                r"throw new HttpRequestException\("),
}

_READS_DETAIL = re.compile(r'"detail"')
_READS_SENTENCE = re.compile(r'"message"')

#: Lines before and after the throw that count as its decode. Wide enough for
#: the C# `try`/`catch` block, narrow enough that an unrelated key elsewhere in
#: the file cannot drift into range.
_BEFORE, _AFTER = 14, 3


def _windows(path: Path, throws: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return ["\n".join(lines[max(0, i - _BEFORE):i + 1 + _AFTER])
            for i, line in enumerate(lines) if re.search(throws, line)]


def _constructions(source: str, call: str) -> list[list[str]]:
    """Every `new RequestError(...)` argument list, split at top-level commas.

    Paren-matched rather than line-matched: these calls wrap, and a regex that
    stopped at the newline would read a two-argument call as complete.
    """
    out = []
    for start in (m.end() for m in re.finditer(re.escape(call), source)):
        depth, args, current = 1, [], ""
        for ch in source[start:]:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
                if depth == 0:
                    break
            if depth == 1 and ch == ",":
                args.append(current.strip())
                current = ""
            else:
                current += ch
        args.append(current.strip())
        out.append([a for a in args if a])
    return out


def test_the_console_hands_the_sentence_to_the_error_it_throws():
    """`RequestError`'s third argument is the sentence, and a call that omits
    it falls back to `JSON.stringify` on the row list — which is what a person
    read before this round."""
    calls = _constructions(CONSOLE.read_text(encoding="utf-8"),
                           "new RequestError(")
    assert calls, "no `new RequestError(` call found — the pattern has stopped matching"
    short = [c for c in calls if len(c) < 3]
    assert not short, (
        f"{len(short)} of the console's {len(calls)} refusal throws pass no "
        "sentence, so a 422 renders as a serialised list:\n    "
        + "\n    ".join(", ".join(c) for c in short))


def test_the_console_prefers_the_sentence_over_the_structure():
    """Order matters and is easy to get backwards.

    `sentence()` returns the first thing it can use. With `detail` checked
    first a 422 never reaches the sentence, because a list is truthy and
    `typeof detail === "object"` is true for it.
    """
    source = CONSOLE.read_text(encoding="utf-8")
    body = source[source.index("private static sentence("):]
    # After the opening brace: the signature names its parameters in the other
    # order and is not a statement about which one is consulted first.
    body = body[body.index("{") + 1:]
    body = body[:body.index("\n  }")]
    assert body.index("message") < body.index("detail"), (
        "`sentence()` consults `detail` before the sentence, so the 422 list "
        "reaches the fallback again:\n" + body)


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_every_shell_refusal_decode_reads_the_sentence(shell):
    """A decode that reads `"detail"` and never `"message"` shows the reader a
    serialised list or a bare status code.

    Structural, and that is the honest limit: this reads the source, it does
    not run the shell — there is no Swift, Kotlin or C# runner in this
    repository. What it rules out is the state all three were actually in.
    """
    path, throws = SHELLS[shell]
    assert path is not None and path.exists(), f"no client source for {shell}"
    blind = [w for w in _windows(path, throws)
             if _READS_DETAIL.search(w) and not _READS_SENTENCE.search(w)]
    assert not blind, (
        f"{shell} has {len(blind)} refusal site(s) that read `detail` and "
        "never look for the sentence beside it:\n\n"
        + "\n\n---\n\n".join(blind[:2]))


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_windows_were_actually_found(shell):
    """A guard on the guard. A renamed exception type makes the pattern match
    nothing, and a check over no windows passes."""
    path, throws = SHELLS[shell]
    found = _windows(path, throws)
    assert found, (
        f"no refusal-throwing site found in {shell} — the pattern "
        f"{throws!r} has stopped matching")
    assert any(_READS_DETAIL.search(w) for w in found), (
        f"none of {shell}'s {len(found)} refusal site(s) reads `detail`, "
        "which means the extraction is pointed at the wrong lines")


def test_the_client_list_is_the_whole_set():
    """A fifth client added to this product and not to the tables above would
    be audited by nothing, and this file would keep passing."""
    assert CONSOLE.exists()
    shells = {p.name for p in (REPO / "native").iterdir() if p.is_dir()}
    assert shells == set(SHELLS), (
        f"native/ holds {sorted(shells)}; SHELLS above covers {sorted(SHELLS)}")


# --- every shape, not just the one that was broken last time ----------------
#
# The round above gave the 422 a top-level `message` and taught all four
# clients to read it. `detail` has three shapes in this product — a string for
# most refusals, a **dict** for the plan gate, a **list** for a 422 — and only
# the list was fixed. The plan gate's `message` stayed nested inside its dict,
# where it had always been.
#
#     asked     does the sentence ride beside the structure
#     mattered  does every structured refusal put it in the same place
#
# So the plan gate reached iOS, Android and Windows as `HTTP 402`: no price, no
# plan name, no reason, on the one refusal in this product that stands between
# somebody and a decision to pay. iOS and Windows had always done that. Android
# had been coercing the dict through `toString()` and showing its raw JSON —
# ugly, but it contained the price — and teaching it to read the top-level key
# first is what regressed it to the status code.
#
# The checks below are per *shape* rather than per route, because that is the
# axis the defect lives on and the axis nothing was testing.

def _probe_app():
    """An app with one route per detail shape.

    Driven through the real handler rather than by calling `sentence_of`:
    being right about the shapes and never being reached is exactly what
    happened to the 422 handler when its branch sat below the string branch.
    """
    from fastapi import HTTPException as _HTTPException

    from qrme import tiers
    app = create_app()

    @app.get("/_shape/string")
    def _string():
        raise _HTTPException(403, "you are not the owner of this profile")

    @app.get("/_shape/dict")
    def _dict():
        raise _HTTPException(402, {
            "reason": "plan", "capability": "marketplace",
            "needs": "pro", "have": "free",
            "price_usd": tiers.PLANS["pro"]["price_usd"],
            "period": tiers.PLANS["pro"]["period"],
            "message": tiers.refusal("free", "marketplace"),
            "billing": "simulated — no real funds move"})

    @app.get("/_shape/bare")
    def _bare():
        raise _HTTPException(404)

    return TestClient(app)


@pytest.mark.parametrize("shape,path", [
    ("string", "/_shape/string"),
    ("dict (the plan gate)", "/_shape/dict"),
])
def test_every_refusal_shape_carries_a_top_level_sentence(shape, path):
    """The defect, per shape. A client should never have to know which one it
    is looking at to find the sentence."""
    body = _probe_app().get(path).json()
    said = body.get("message")
    assert isinstance(said, str) and said.strip(), (
        f"a {shape} refusal carries no top-level `message`, so the three "
        f"shells fall back to the status code: {body}")
    assert not said.lstrip().startswith(("{", "[")), (
        f"the sentence is a serialised structure: {said[:120]}")


def test_the_422_shape_is_covered_by_the_same_rule(client):
    """The list, checked here too rather than only above, so all three shapes
    are asserted in one place and adding a fourth has an obvious home."""
    body = client.post("/profiles", json={"kind": "self"}).json()
    assert isinstance(body.get("message"), str) and body["message"].strip()


def test_the_plan_gate_keeps_the_structure_the_console_renders():
    """The sentence rides *beside* the structure, never instead of it.

    `planGate()` and `Refusal.tsx` read `reason`, `needs`, `price_usd`,
    `period` and `billing` to draw the upgrade card with its price and button.
    A fix that flattened the refusal to a sentence would have replaced that
    card with a line of text.
    """
    body = _probe_app().get("/_shape/dict").json()
    detail = body["detail"]
    assert isinstance(detail, dict)
    for key in ("reason", "capability", "needs", "have", "price_usd",
                "period", "billing"):
        assert key in detail, f"the console's upgrade card lost {key}"
    assert detail["reason"] == "plan"


def test_a_refusal_with_nothing_readable_is_not_given_an_invented_sentence():
    """`HTTPException(404)` has no message of its own.

    Answered exactly as before rather than handed a sentence this codebase made
    up — a fabricated explanation is worse than a bare status, and it would be
    indistinguishable from a real one.
    """
    body = _probe_app().get("/_shape/bare").json()
    assert "message" not in body or body.get("message"), (
        "a refusal with nothing to say grew an empty `message`, which a client "
        "would render as a blank line where an explanation belongs")


@pytest.mark.parametrize("language", ["pt", "ja"])
def test_the_lifted_sentence_is_the_translated_one(language):
    """Order inside the handler, and a test that can actually fail on it.

    The first version of this compared the top-level sentence with the nested
    one on the plan gate — and could not fail, because the plan gate's message
    is deliberately untranslated (`refusals_untranslated.txt` says why), so
    both sides were the same English string no matter which order the handler
    used. An injection that lifted the sentence *before* localizing passed.

        asked     do the two copies agree
        mattered  is the lifted one the translated one

    So this drives a structured refusal whose message is in `_REFUSALS`, where
    lifting before localizing produces a visible difference.
    """
    from fastapi import HTTPException as _HTTPException
    english = "authentication required"
    assert english in i18n._REFUSALS, (
        "the sentence this test relies on is no longer translated — pick "
        "another from i18n._REFUSALS, or this check goes vacuous again")

    app = create_app()

    @app.get("/_shape/translated_dict")
    def _translated():
        raise _HTTPException(401, {"reason": "auth", "message": english})

    body = TestClient(app).get(
        "/_shape/translated_dict",
        headers={"accept-language": language}).json()
    expected = i18n.tr_refusal(english, language)
    assert expected != english, f"no {language} translation to distinguish"
    assert body["message"] == expected, (
        f"the top-level sentence is {body['message']!r}, not the {language} "
        "one — it was lifted off the detail before the detail was localized")
    assert body["detail"]["message"] == expected


def test_sentence_of_reads_each_shape_and_invents_nothing():
    """The unit behind it, including the case that must return nothing."""
    assert i18n.sentence_of("plain") == "plain"
    assert i18n.sentence_of({"message": "structured", "needs": "pro"}) == "structured"
    assert i18n.sentence_of({"needs": "pro"}) is None
    assert i18n.sentence_of(None) is None
    assert i18n.sentence_of("") is None
    assert i18n.sentence_of([{"msg": "row"}]) is None, (
        "the 422 list is validation_message's job — it needs the reader's "
        "language and the field-name rules this function does not have")


def test_no_label_is_built_from_anything_but_a_constant():
    """What makes widening the rule above safe.

    `test_the_sentence_says_no_more_than_the_rows` now accepts pieces that came
    from `_FIELD_LABELS`. That is only sound while every value in it is a
    literal — a table that interpolated anything could put a submitted value
    into the sentence through the one door the leak check was just told to
    trust.

        asked     is the sentence composed only from the rows
        mattered  is every source of it incapable of carrying the body
    """
    import ast as _ast
    src = pathlib.Path(i18n.__file__).read_text(encoding="utf-8")
    table = next(
        (n for n in _ast.walk(_ast.parse(src))
         if isinstance(n, _ast.AnnAssign)
         and getattr(n.target, "id", "") == "_FIELD_LABELS"), None)
    assert table is not None, "the label table is no longer a module constant"
    bad = [_ast.dump(v)[:60] for v in _ast.walk(table.value)
           if isinstance(v, (_ast.JoinedStr, _ast.Call, _ast.Name,
                             _ast.Attribute, _ast.BinOp))]
    assert not bad, (
        "the label table is not all literals, so a value could reach the "
        "sentence through it:\n    " + "\n    ".join(bad))
