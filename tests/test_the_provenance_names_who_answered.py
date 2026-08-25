"""The provenance named the model that was asked, not the one that answered.

## The finding

`content_provenance` is this product's central claim. Its own docstring says
what it is for:

    The verifiable basis of a piece of persona-generated content: which model
    produced it ... so nothing the platform emits is a black box.

It read the profile's **stored preference**:

    "generated_by": llm.resolve_choice(llm.get_choice(profile["id"])),

Meanwhile both network wrappers degrade rather than fail.
`llm.FallbackProvider` catches any exception from the primary and returns the
local stub's text, logging a warning. `cloud.CloudProvider` did the same and
did not even log.

So: an owner sets their profile to Anthropic and brings their own API key. The
key expires. The next post is written by the stub on their own machine, stamped
`generated_by: "anthropic"`, watermarked, and published — and the only trace is
a log line addressed to nobody.

    asked     which model was this profile set to
    mattered  which model actually wrote this

Degrading is the right behaviour and is not what changed here. A model outage
should not take the product down. What changed is what the platform then *says*
about the result.

## The rule was already written, in the other product

JIM-mini's `FallbackProvider` has carried this in its docstring for releases:

    The degrade is recorded on the instance (``answered_by``, ``failure``) so a
    caller can tell the user the truth about who actually answered — **a log
    line the user will never read is not disclosure.**

The product that had the rule was the health app. The product that needed it is
the one whose premise is that generated content carries a trustworthy account
of where it came from.

## Why a context variable and not an instance attribute

JIM records on the provider instance because its callers hold one. Every call
site here is `llm.provider_for_profile(profile_id).generate(...)` — built and
discarded inline, nothing left to interrogate. A request-scoped `ContextVar` is
the idiom this module already uses for the caller's API key, and it means
`content_provenance` reads the truth without a single call site changing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from qrme import cloud, common, llm

from . import ratchets


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


class _Dead:
    """A provider whose credential has expired, in the way they really do."""

    def __init__(self, message="Error code: 401 - invalid x-api-key"):
        self.message = message

    def generate(self, system, messages):
        raise RuntimeError(self.message)


class _Live:
    def __init__(self, text="a real answer"):
        self.text = text

    def generate(self, system, messages):
        return self.text


@pytest.fixture(autouse=True)
def _forget_between_tests():
    """The variable is request-scoped in the app; these tests drive the
    providers directly, so they clear it themselves."""
    llm.clear_answered_by()
    yield
    llm.clear_answered_by()


# --- the wrappers say who answered -----------------------------------------

def test_a_degrade_records_the_provider_that_actually_answered():
    out = llm.FallbackProvider("anthropic", _Dead(), _Live("stub text")).generate("s", [])
    assert out == "stub text"
    assert llm.answered_by() == (llm.LOCAL_FALLBACK, "anthropic"), (
        "the fallback ran and did not say so, which is the whole defect: the "
        "text came from the local stub and provenance would go on naming the "
        "model the owner chose")


def test_a_success_records_the_provider_too():
    """Both branches, because recording only the degrade leaves the variable
    holding a *previous* degrade when a later call succeeds — a false statement
    with a longer life than the one it replaced."""
    llm.FallbackProvider("anthropic", _Dead(), _Live()).generate("s", [])
    llm.FallbackProvider("anthropic", _Live("fresh"), _Live()).generate("s", [])
    assert llm.answered_by() == ("anthropic", None), (
        "a successful generation left the earlier degrade in place")


def test_the_cloud_gateway_records_its_degrade_as_well():
    """The path that did not even log. Two wrappers swallow provider failures
    in this codebase and a check that knew about one of them would pass while
    the other went on lying."""
    class DeadClient:
        def generate(self, system, messages):
            raise RuntimeError("gateway down")

    out = cloud.CloudProvider(DeadClient(), _Live("stub text")).generate("s", [])
    assert out == "stub text"
    actual, asked = llm.answered_by()
    assert actual == llm.LOCAL_FALLBACK and asked == cloud.CloudProvider.GREATER_MODEL


# --- the record does not carry the caller's credential ----------------------

def test_a_degrade_never_repeats_the_key_the_caller_sent():
    """The reason for a degrade comes from an exception this codebase did not
    raise, and some HTTP clients put the whole request — headers included —
    into the string form of their errors. On this path the interesting header
    is the caller's own API key."""
    token = llm.set_request_key("sk-THE-CALLERS-OWN-KEY")
    try:
        said = llm.scrub(RuntimeError(
            "401 from provider; sent x-api-key: sk-THE-CALLERS-OWN-KEY"))
    finally:
        llm.reset_request_key(token)
    assert "sk-THE-CALLERS-OWN-KEY" not in said, (
        "a provider's error was about to be shown to the person and written to "
        f"the log with their own credential still in it: {said!r}")


# --- and the provenance reports it ------------------------------------------

def test_provenance_names_the_fallback_after_a_degrade(client, profile_id):
    llm.FallbackProvider("anthropic", _Dead(), _Live()).generate("s", [])
    prov = common.content_provenance(
        {"id": profile_id, "maturity": "balanced", "licensed_from": None},
        [], "ok", None)
    assert prov["generated_by"] == llm.LOCAL_FALLBACK, (
        f"provenance says {prov['generated_by']!r} wrote this; the local "
        "fallback did")
    assert prov["degraded_from"] == "anthropic", (
        "the record does not say what was asked for, so a reader cannot tell "
        "an outage from somebody changing the setting")


def test_provenance_falls_back_to_the_stored_choice_when_nothing_degraded(
        client, profile_id):
    """The honest default. `answered_by()` is None when no wrapper ran, and
    the stored choice is then exactly what generated — this must not report a
    degrade that did not happen."""
    prov = common.content_provenance(
        {"id": profile_id, "maturity": "balanced", "licensed_from": None},
        [], "ok", None)
    assert prov["generated_by"] == llm.resolve_choice(llm.get_choice(profile_id))
    assert prov["degraded_from"] is None


def test_one_requests_degrade_does_not_describe_the_next_ones_content(client,
                                                                      profile_id):
    """Driven through the app, because the clearing lives in middleware and a
    unit test of the context variable would pass without it.

    A degrade left behind by an earlier request would label the next request's
    perfectly good content as a fallback — the same false statement as the
    original defect, pointing the other way.
    """
    llm.note_answered_by(llm.LOCAL_FALLBACK, degraded_from="anthropic")
    body = client.post(f"/profiles/{profile_id}/compose",
                       json={"topic": "a walk"})
    assert body.status_code in (200, 201), body.text
    prov = body.json().get("provenance") or {}
    assert prov.get("degraded_from") is None, (
        "this request generated normally and its provenance reports a degrade "
        "left over from before it — the middleware is not clearing the record")


# --- the generalisation -----------------------------------------------------

def _degrading_wrappers() -> list[tuple[str, str, ast.FunctionDef]]:
    """Every `generate` that answers a provider failure with somebody else's
    text.

    Found structurally rather than by name. Two such wrappers exist today and
    the defect was that one of them said nothing; a third added later without
    recording who answered would put the false claim straight back, and naming
    the two known classes would not notice.
    """
    out = []
    for rel in ("qrme/llm.py", "qrme/cloud.py"):
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        for cls in ast.walk(tree):
            if not isinstance(cls, ast.ClassDef):
                continue
            for fn in cls.body:
                if not isinstance(fn, ast.FunctionDef) or fn.name != "generate":
                    continue
                for handler in [n for n in ast.walk(fn)
                                if isinstance(n, ast.ExceptHandler)]:
                    calls = [n for n in ast.walk(handler)
                             if isinstance(n, ast.Call)
                             and getattr(n.func, "attr", "") == "generate"]
                    if calls:
                        out.append((rel, cls.name, handler))
    return out


def _calls(node) -> set[str]:
    """Names called inside `node`, dotted or bare.

    Both forms, because both are here: `cloud.py` imports the module and calls
    `llm.note_answered_by(...)`, while `llm.py` calls its own
    `note_answered_by(...)` unqualified. The first draft of this check read
    only `.attr`, so it saw the cloud wrapper recording and reported the one in
    `llm.py` — the one that had just been fixed — as silent.

        asked     does the handler call llm.note_answered_by
        mattered  does the handler record who answered
    """
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            out.add(getattr(n.func, "attr", None) or getattr(n.func, "id", ""))
    return out


def test_every_wrapper_that_swallows_a_failure_records_who_answered():
    silent = []
    for rel, name, handler in _degrading_wrappers():
        if "note_answered_by" not in _calls(handler):
            silent.append(f"{rel}: {name}.generate (line {handler.lineno})")
    assert not silent, (
        f"{len(silent)} wrapper(s) answer a provider failure with the local "
        "fallback's text and do not record it, so provenance goes on naming "
        "the provider that was asked:\n    " + "\n    ".join(silent))


def test_the_wrapper_scan_is_finding_wrappers():
    """A guard on the guard. A structural walk that stopped matching would
    report no silent wrappers and pass on nothing at all."""
    found = _degrading_wrappers()
    assert len(found) >= ratchets.floor("degrading.wrappers"), (
        f"only {len(found)} degrading wrapper(s) parsed — this codebase has "
        "two, in llm.FallbackProvider and cloud.CloudProvider, and the check "
        "above is passing on an empty set")


def test_the_provenance_docstring_still_claims_what_this_file_holds_it_to():
    """The claim and the check, kept beside each other. If the docstring stops
    promising the model that *produced* the content, this whole file is
    enforcing something the product no longer says."""
    # Whitespace-normalised: the phrase wraps across two source lines, and a
    # plain substring search read `"which\n    model produced it"` and
    # reported the promise gone while it sat there intact.
    doc = " ".join((common.content_provenance.__doc__ or "").split())
    assert "which model produced it" in doc, (
        "content_provenance no longer claims to name the model that produced "
        "the content — either the promise moved or it was dropped, and this "
        "file should follow it rather than outlive it")
