"""And so is each phone. The console guard's question, one surface over.

`test_the_console_is_a_client_too.py` exists because the union guard answered
*some client can reach this*, which was true, in place of *this client can
reach this*, which was not. It fixed that for the console, and the console
backlog is now zero.

It fixed it for **one** client. There are four.

                      at the start of this round
    union doorless                         0
    console                                0
    ios                                  309
    android                              311
    windows                              309

Three quarters of QRME's routes are unreachable from a phone. That is not a
list of things to build — an owner's workshop has no business on a handset —
it is a list of things **nobody has decided about**. This file makes the split
deliberate: one ratcheted snapshot per shell, so deferring a route takes an
edit and shows in a diff.

## What it found on its first run

The phones carry the profile owner's side of accountability and not the
public's. iOS, Android and Windows all call:

    GET  /profiles/{id}/objections               — see objections against mine
    POST /profiles/{id}/objections/{oid}/attest  — answer one
    POST /watermarks/recover                     — whose text is this?

and none of them calls:

    POST /objections          — raise one
    POST /watermarks/verify   — is this the content it was issued for?
    GET  /watermarks/{id}     — read a credential

`governance.open_objection` says who the missing one belongs to, in its own
docstring: *"Open an objection (**public: the objecting party need not own an
account**). Suspends the profile pending review."* It is the route for a
person who has found a synthetic profile of themselves — someone who by
construction has no QRME account, and therefore no console. The surface they
would reach for is a phone, and it is the surface that cannot do it.

This is the audit's recurring shape in a new place. Not a checker asking a
question to the left of the one that matters — a **surface** carrying the half
of a feature that belongs to the person with power, and not the half that
belongs to the person without it.

## What is *not* wrong, and nearly got "fixed"

The watermark pair looks like the same story and is not. A first draft of this
file demanded `POST /watermarks/verify` and `GET /watermarks/{id}` on every
shell, on the reasoning that encountering synthetic media happens on a phone.

All three shells decline those on purpose, and say why in a comment above the
card that replaces them:

    `/watermarks/verify` needs a credential id up front and fails on one
    edited character. This asks "whose work is this" with no id, and keeps
    answering after the text has been rewritten.

Somebody holding a screenshot has no credential id, and the text they were
sent has usually been reworded. `recover` is the right tool for that person
and `verify` is the wrong one — the shells picked correctly and wrote down the
reason. The console keeps `verify` because a console user is checking a
credential they already hold.

The draft also grew a test asserting that any shell verifying a mark must
render `content_match` as well as `valid`. It fired on all three — by matching
the **comment above**, not a call. That is the same mistake four extractors
have made in this audit, made this time by the guard written to catch its
cousin. It has been removed rather than patched: the door test below already
says whether a shell can verify at all, and
`test_two_questions_a_mark_answers.py` covers the surface that does.

## What this file is not

It is not a demand that every route reach every client. It is the ratchet that
makes the split a decision. The difference between a decision and an oversight
is whether anybody made it.
"""

from __future__ import annotations

from pathlib import Path

from qrme.api import app

from . import clientpaths

HERE = Path(__file__).resolve().parent

#: One snapshot per shell. Separate files rather than one, because the shells
#: diverge for real reasons — a camera roll, a Health store, a desktop-only
#: signing ceremony — and a single list would hide which shell a line is for.
SNAPSHOTS = {
    "ios": HERE / "ios_doorless.txt",
    "android": HERE / "android_doorless.txt",
    "windows": HERE / "windows_doorless.txt",
}

#: Where each stood when this guard was written, so the direction of travel is
#: a fact in the file rather than a claim in a commit message.
STARTED_AT = {"ios": 309, "android": 311, "windows": 309}


def _surface(name: str):
    for lang in clientpaths.NATIVE:
        if lang.name == name:
            return lang
    raise AssertionError(f"no native surface named {name!r}")


def _recorded(name: str) -> list[str]:
    return [line.strip() for line in
            SNAPSHOTS[name].read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def _actual(name: str) -> list[str]:
    return clientpaths.doorless(app, surfaces=(_surface(name),))


def test_each_shell_backlog_matches_its_record():
    """Both directions, per shell. A route that has *gained* a door on a phone
    is as much a change to report as one that has lost it — a file only
    checked for growth becomes a list of things that were true once."""
    problems = []
    for name in SNAPSHOTS:
        actual, recorded = set(_actual(name)), set(_recorded(name))
        appeared, resolved = sorted(actual - recorded), sorted(recorded - actual)
        if appeared:
            problems.append(
                f"{name}: {len(appeared)} route(s) the shell cannot reach:\n    "
                + "\n    ".join(appeared)
                + "\n  (build the door, or record it here with the reason)")
        if resolved:
            problems.append(
                f"{name}: {len(resolved)} route(s) now have a door — strike "
                f"them from {SNAPSHOTS[name].name}:\n    "
                + "\n    ".join(resolved))
    assert not problems, "\n\n".join(problems)


def test_each_backlog_only_shrinks():
    """A ratchet per shell. None is zero and none has to be — what they must
    not do is grow."""
    for name, started in STARTED_AT.items():
        assert len(_recorded(name)) <= started, (
            f"the {name} backlog is {len(_recorded(name))}, above the "
            f"{started} it started at — routes are being added faster than "
            "doors")


def test_the_union_is_never_worse_than_any_single_shell():
    """Arithmetic, not policy: every shell is one of the union's own surfaces,
    so the union cannot be missing something a shell reaches."""
    union = set(clientpaths.doorless(app))
    for name in SNAPSHOTS:
        assert union <= set(_actual(name)), (
            f"a route is doorless everywhere but reachable from {name}, which "
            "means the two are computed over different route tables")


# --- the public's half ------------------------------------------------------

#: Routes that belong to somebody who is **not** a profile owner: a person
#: contesting a synthetic profile of themselves, and anybody asking whether
#: what they are looking at is genuine. Unlike the snapshots above, these are
#: not deferrable — there is no line to add.
#:
#: The test on them is deliberately narrow. It does not say a phone must carry
#: every governance route; it says a phone must carry the ones whose user has
#: no other surface. A profile owner has a console. The person objecting to
#: their profile does not.
#: Narrowed from a first draft that also listed the two watermark routes —
#: see the note in the module docstring. They are absent from the shells by a
#: decision that is better than the one this guard would have forced.
PUBLIC_PATHS = (
    "POST /objections",
)


def test_every_shell_carries_the_publics_half():
    """The half that belongs to the person without an account.

    `open_objection` is explicit that its caller need not own one, and a
    watermark check is the question QRME exists to answer. Both were reachable
    only from a console — which is to say, only by people who already have a
    profile.
    """
    missing = []
    for name in SNAPSHOTS:
        cannot = set(_actual(name))
        missing += [f"{name}: {p}" for p in PUBLIC_PATHS if p in cannot]
    assert not missing, (
        "a shell cannot reach the public's half of accountability:\n    "
        + "\n    ".join(missing)
        + "\n  These belong to somebody with no console — the person "
          "objecting to a synthetic profile of themselves, and anybody "
          "asking whether what they are holding is genuine.")


def test_the_public_paths_are_real_routes():
    """A guard on the guard. If one of these is renamed, the check above would
    silently stop checking anything — the list would simply never match and
    every shell would 'pass'."""
    routed = {f"{m} {r.path}"
              for r in clientpaths.all_routes(app)
              for m in (r.methods or set()) - {"HEAD", "OPTIONS"}}
    unknown = [p for p in PUBLIC_PATHS if p not in routed]
    assert not unknown, (
        "these are not routes in the app any more, so the check above is "
        "vacuous:\n    " + "\n    ".join(unknown))
