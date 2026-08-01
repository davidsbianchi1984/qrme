"""The persona speaks it everywhere. The platform spoke English.

## The finding

`qrme/i18n.py` opens with a claim and keeps it:

    Per-profile language: the persona speaks it everywhere ... the directive
    rides on the persona system prompt, so every generation site inherits it
    without per-endpoint plumbing.

Every *generation* site. The product's own sentences were another matter. An
owner who set Portuguese got a Portuguese sidebar from `l10n.ts`, Portuguese
answers from the model, and English on every single refusal — 153 distinct
ones, from "authentication required" to the plan gate that stands between them
and a decision to pay.

`common.refusals_in` was added in 0.24.0 for the four accountless routes, and
its docstring wrote the reason the owner routes were left out:

    `profile_or_404` and its siblings are shared with every owner route and
    say "profile not found" in English, which is right there — the owner
    picked that language

The owner did not pick that language. They picked one; it is in
`language_prefs`; English is what they get when they picked English. The
justification for the scope *was* the defect, written down and reviewed.

    asked     did the caller state a language
    mattered  did the profile

## The two ways the fix could have been wrong and still passed

**Whose language.** Reading the `profile_id` in the path would answer a
stranger on `GET /profiles/{id}/consistency` in the language of the person
they are asking *about* — a new wrong answer wearing the shape of a fix.
Reading `Accept-Language` would take `en-US` from a console owner's browser
whatever they had set in the app, making the whole round a no-op that passed
its own tests. The credential names the reader, and nothing else does.

**Which stored value.** `effective_language` returns English whenever the mode
is `on_demand` — a statement about the *persona's voice*, not about what the
owner reads. Using it would have looked right, passed a test written with a
`pre`-mode profile, and served English to every owner who had asked their
persona to stay in character. Both are checked below, with a profile in
`on_demand` mode specifically.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from qrme import i18n


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SNAPSHOT = Path(__file__).resolve().parent / "refusals_untranslated.txt"


def _details(root: Path) -> tuple[set[str], int]:
    """Every literal `HTTPException` detail in the package, and how many are
    built by interpolation instead.

    From Python's own parser. A regex over the source is how the language
    audit in this repository missed real text three separate times — the long
    version is in `test_the_stranger_has_a_language_too.py` — and refusals are
    worse than most: they wrap across source lines by construction, because
    they are long sentences inside an indented `raise`.
    """
    literals: set[str] = set()
    interpolated = 0
    for path in sorted(root.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = getattr(fn, "id", "") or getattr(fn, "attr", "")
            if name != "HTTPException":
                continue
            detail = node.args[1] if len(node.args) >= 2 else None
            for kw in node.keywords:
                if kw.arg == "detail":
                    detail = kw.value
            if isinstance(detail, ast.Constant) and isinstance(detail.value, str):
                literals.add(detail.value)
            elif isinstance(detail, ast.JoinedStr):
                interpolated += 1
    return literals, interpolated


def _translated() -> set[str]:
    """Both tables. `profile_or_404` is shared between the accountless routes
    and every owner route, so its sentence lives in `_PUBLIC` and is not owed
    a second entry — see `tr_refusal`."""
    return set(i18n._REFUSALS) | set(i18n._PUBLIC)


def _recorded() -> set[str]:
    return {line.rstrip("\n") for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_every_refusal_is_translated_or_written_down():
    """Both directions. A refusal that is neither is a sentence somebody will
    read in a language they did not choose, that nobody decided about."""
    literals, _ = _details(REPO / "qrme")
    undecided = sorted(literals - _translated() - _recorded())
    stale = sorted(_recorded() - literals)
    problems = []
    if undecided:
        problems.append(
            f"{len(undecided)} refusal(s) that are neither translated nor "
            "recorded:\n    " + "\n    ".join(s[:90] for s in undecided[:30])
            + "\n  Add it to i18n._REFUSALS, or to "
              f"{SNAPSHOT.name} — but adding there is ratcheted.")
    if stale:
        problems.append(
            f"{len(stale)} recorded refusal(s) are no longer raised anywhere "
            f"— strike them from {SNAPSHOT.name}:\n    "
            + "\n    ".join(s[:90] for s in stale[:30]))
    assert not problems, "\n\n".join(problems)


def test_the_backlog_only_shrinks():
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            SNAPSHOT.read_text(encoding="utf-8")).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} untranslated refusals, above the {ceiling} this "
        "guard started at")


def test_the_extractor_can_still_see(tmp_path):
    """A guard on the guard, against a fixture whose answer is known.

    Everything above trusts an AST walk. If the walk stops recognising a call
    shape, `_details` returns a small set, the backlog looks solved and the
    record fills with strings nobody raises — which the staleness half would
    report as *progress*. The fixture carries one of each shape this codebase
    actually uses.
    """
    fixture = tmp_path / "shapes.py"
    fixture.write_text(
        'from fastapi import HTTPException\n'
        'def a(): raise HTTPException(404, "positional")\n'
        'def b(): raise HTTPException(403, detail="by keyword")\n'
        'def c(): raise HTTPException(422, "wrapped across "\n'
        '                                  "two source lines")\n'
        'def d(x): raise HTTPException(400, f"built from {x}")\n'
        'def e(): raise fastapi.HTTPException(409, "dotted call")\n'
        'def f(): raise HTTPException(402, {"message": "a dict detail"})\n',
        encoding="utf-8")
    literals, interpolated = _details(tmp_path)
    assert literals == {"positional", "by keyword",
                        "wrapped across two source lines", "dotted call"}, (
        f"the extractor no longer reads the shapes it documents:\n{literals}")
    assert interpolated == 1, (
        "the extractor stopped counting interpolated refusals, which is how "
        "49 of them would quietly leave the record's header")


def test_every_translated_refusal_has_every_language():
    """No partial rows. A row missing four languages serves English to four
    readers while the table says the sentence is handled."""
    langs = [c for c in i18n.SUPPORTED if c != i18n.DEFAULT]
    gaps = {k: [c for c in langs if c not in v]
            for k, v in i18n._REFUSALS.items()}
    gaps = {k: v for k, v in gaps.items() if v}
    assert not gaps, (
        "these refusals are missing languages:\n    "
        + "\n    ".join(f"{k[:60]}: {', '.join(v)}"
                        for k, v in sorted(gaps.items())))
    assert len(i18n._REFUSALS) >= 9, (
        f"only {len(i18n._REFUSALS)} refusals in the table — this check would "
        "be passing on almost nothing")


# --- driven, not read ------------------------------------------------------
#
# `client` comes from tests/conftest.py. Profiles are made here rather than
# through the `profile_id` fixture because that fixture pins an owner token
# onto the client's default headers, and half of what follows is about a
# reader who holds no such token.

def _a_profile(client, name: str, language: str, mode: str = "pre"):
    made = client.post("/profiles", json={
        "owner_id": f"owner-{name}", "kind": "self", "display_name": name,
        "persona": "A profile that exists to be refused.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert made.status_code == 201, made.text
    body = made.json()
    owner = body["owner_token"]
    set_language = client.put(
        f"/profiles/{body['id']}/language",
        json={"language": language, "mode": mode},
        headers={"authorization": f"Bearer {owner}"})
    assert set_language.status_code == 200, set_language.text
    return body["id"], owner


def test_an_owner_is_refused_in_their_own_language(client):
    """The defect, driven end to end.

    The browser header says `en-US` throughout, because that is what a console
    owner's browser actually sends whatever they chose in the app. If this
    passes while the header decides, the fix is a no-op.

    Asserted against the table's own entry rather than a fixed Spanish string,
    so rewording the English fails the row that went stale rather than this
    test.
    """
    profile_id, owner = _a_profile(client, "Refusal", "es")
    intruder, _ = _a_profile(client, "Intruder", "en")

    refused = client.put(
        f"/profiles/{intruder}/language", json={"language": "de"},
        headers={"authorization": f"Bearer {owner}",
                 "accept-language": "en-US,en;q=0.9"})
    assert refused.status_code == 403, refused.text
    assert refused.json()["detail"] == (
        i18n._REFUSALS["not authorized for this resource"]["es"]), (
        "the owner set Spanish and was refused in "
        f"{refused.json()['detail']!r}. The browser header said en-US, which "
        "is exactly why the header cannot be what decides this.")


def test_a_stranger_is_not_answered_in_the_owners_language(client):
    """The wrong fix, checked directly.

    Resolving the language from the `profile_id` in the path would answer a
    stranger asking *about* a profile in the language of the person they are
    asking about. The reader here holds no owner token, so their own header is
    all there is.
    """
    profile_id, _ = _a_profile(client, "Watched", "ja")

    refused = client.put(f"/profiles/{profile_id}/language",
                         json={"language": "de"},
                         headers={"accept-language": "fr-FR,fr;q=0.9"})
    assert refused.status_code == 401, refused.text
    detail = refused.json()["detail"]
    assert detail == i18n._REFUSALS["authentication required"]["fr"], (
        "a stranger asking about a Japanese-speaking owner's profile got "
        f"{detail!r}. The path names whose profile it is, never who is "
        "reading the answer.")


def test_on_demand_mode_is_not_a_statement_about_what_the_owner_reads(client):
    """`effective_language` returns English in `on_demand` mode.

    That mode means "persona, keep your own voice; I will translate what I
    choose" — a decision about generated speech. Reading it here would serve
    English refusals to an owner who had set Spanish, and would have passed
    every test written with a default-mode profile.
    """
    profile_id, owner = _a_profile(client, "OnDemand", "es", mode="on_demand")
    intruder, _ = _a_profile(client, "Bystander", "en")

    assert i18n.effective_language(profile_id) == "en"
    assert i18n.get_language(profile_id) == "es"

    refused = client.put(
        f"/profiles/{intruder}/language", json={"language": "de"},
        headers={"authorization": f"Bearer {owner}",
                 "accept-language": "en-US,en;q=0.9"})
    assert refused.status_code == 403, refused.text
    assert refused.json()["detail"] == (
        i18n._REFUSALS["not authorized for this resource"]["es"]), (
        "an owner in on_demand mode was refused in "
        f"{refused.json()['detail']!r}. That mode is about the persona's "
        "voice; it says nothing about what the owner reads.")


def test_a_dict_detail_keeps_its_vocabulary_and_translates_its_sentence():
    """`tiers.gate` refuses with a dict, not a sentence.

    A handler that translated only `str` would leave the plan gate — the one
    refusal standing between somebody and a decision to pay — in English while
    every sentence around it changed language. And a handler that translated
    the whole dict would translate `reason` and `capability`, which the
    console branches on: the same rule as `_PUBLIC`, one layer in.
    """
    detail = {"reason": "plan", "capability": "marketplace",
              "have": "free", "message": "authentication required"}
    out = i18n.localize_detail(detail, "de")
    assert out["message"] == i18n._REFUSALS["authentication required"]["de"]
    assert out["reason"] == "plan" and out["capability"] == "marketplace", (
        "the API's own vocabulary was translated. A console comparing "
        'reason === "plan" stops recognising its own upgrade card.')


def test_an_unknown_sentence_falls_through_as_english():
    """The 142 in the record, and anything added tomorrow.

    English is a visible gap. A guessed translation is a confident error, and
    a refusal is exactly the sentence where being confidently wrong costs
    somebody the most.
    """
    assert i18n.tr_refusal("a sentence nobody has translated", "es") == (
        "a sentence nobody has translated")
    assert i18n.localize_detail({"message": "likewise"}, "ja") == {
        "message": "likewise"}


def test_resolving_a_language_never_raises():
    """The diagnostic must not become the outage.

    This runs inside the exception handler. If it can throw, a refusal turns
    into a 500 and the person is told the server broke when it was really
    telling them no.
    """
    class _Broken:
        @property
        def headers(self):
            raise RuntimeError("no headers here")

    with pytest.raises(RuntimeError):
        _Broken().headers          # the fixture really is broken
    for bad in ({}, None):
        class _Odd:
            headers = {"authorization": "Bearer nope"} if bad is None else {}
        assert i18n.refusal_language(_Odd()) == "en"
