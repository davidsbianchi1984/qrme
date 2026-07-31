"""A route the backend made public, in a client that made it private.

## The finding

`governance.open_objection` says what it is in its own first line:

    Open an objection (**public: the objecting party need not own an
    account**). Suspends the profile pending review.

`Contest.tsx` said the same thing in the copy a person reads:

    You do not need an account. Objecting to a profile should not require
    joining the platform that is hosting it.

Both were true of the route and false of the app. `App.tsx` returned
`<Onboarding />` for the entire window while `session.profileId` was unset, so
all forty-six tabs — Contest among them — sat behind a sign-up. The three
native shells did the same: `RootView` renders `WelcomeView` unless
`state.isSignedIn`, and the objection form lives inside `ManageView`.

So the sentence promising no account was printed on a surface that required
one, and the person the route exists for is precisely the person who cannot
reach it. They have found a synthetic profile of themselves. They have no QRME
account. The product's answer was that they should make one — with the
platform depicting them — first.

## Why the guard that was supposed to catch this did not

`test_the_phone_is_a_client_too.py`, written one round earlier, has a check
named `test_every_shell_carries_the_publics_half` with `POST /objections` in
it. It passed. It asks whether a shell *contains a call site* for the route,
and a call site inside a signed-in tab is still a call site.

That is the seventh time in this audit that a checker has answered a question
slightly to the left of the one that matters:

    union doorless      → some client can reach it     (not: this one can)
    console doorless    → the console can reach it     (not: a phone can)
    binding count       → a function exists            (not: a screen calls it)
    native bindings     → same, three surfaces over
    the shell can end   → the name appears in the file (matched its own def)
    the public's half   → a shell calls the route      (not: without an account)

Every one of them was true. None was the question.

## What this file checks

That each public path is called from code reachable **before** the session
gate, in each client that has one. It is not a general authentication audit —
it names four paths and asks one question about them.

The paths are not a list of everything the backend leaves uncredentialed;
roughly two hundred routes take no token, most because the caller's identity
is a path parameter rather than because a stranger is meant to call them.
These four are the ones whose *user* has no account by construction: somebody
contesting a profile of themselves, and somebody holding a piece of content
asking whether a person made it.
"""

from __future__ import annotations

import re
from pathlib import Path

from qrme.api import app

from . import clientpaths


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SRC = REPO / "app" / "src"

#: Routes whose caller, by construction, has no account — with the binding
#: name each client uses for it. Not deferrable: there is no snapshot file
#: beside this one, because "we decided a stranger has to sign up to object to
#: a profile of themselves" is not a decision this product can record.
PUBLIC_PATHS = {
    "POST /objections": "openObjection",
    "GET /objections/{objection_id}": "objection",
    "POST /watermarks/recover": "recoverWatermark",
    # Found by this file's last check rather than by hand: the route says
    # "Public: anyone meeting the profile through any form can verify it is
    # the same personality", and the only screen calling it was the owner's
    # Workshop — which printed that sentence in a card only the owner sees.
    "GET /profiles/{profile_id}/embodiment-consistency": "embodimentConsistency",
}


def test_the_public_paths_are_real_routes():
    """A guard on the guard, first, because everything below is a search for
    a name: if a route is renamed, the checks stop checking and pass."""
    routed = {f"{m} {r.path}"
              for r in clientpaths.all_routes(app)
              for m in (r.methods or set()) - {"HEAD", "OPTIONS"}}
    unknown = sorted(p for p in PUBLIC_PATHS if p not in routed)
    assert not unknown, (
        "these are not routes in the app any more, so the checks below are "
        "vacuous:\n    " + "\n    ".join(unknown))


def test_the_backend_still_means_them_to_be_public():
    """The premise, checked rather than assumed.

    This whole file rests on `open_objection` being public **on purpose**. If
    somebody adds a credential check to it, that is a legitimate decision — and
    this test should fail loudly and be deleted along with the screen, rather
    than the screen quietly becoming a form that always 401s.
    """
    text = (REPO / "qrme" / "routers" / "governance.py").read_text(
        encoding="utf-8")
    body = text[text.index("def open_objection"):]
    body = body[:body.index("\n@router")] if "\n@router" in body else body
    assert "need not own an account" in body, (
        "open_objection no longer documents itself as public — if that is "
        "deliberate, the public screen is now a form nobody can submit")
    for guard in ("require_owner", "require_self", "require_interactor",
                  "require_reviewer"):
        assert guard not in body, (
            f"open_objection now calls {guard}: the route is no longer public, "
            "so the accountless screen in front of it is misleading")


# --- the console ------------------------------------------------------------
#
# One gate, and it is a single early return in App.tsx:
#
#     if (!session.profileId) { ... return <Onboarding/> or <Public/> ... }
#
# So "reachable without an account" has an exact meaning here: rendered by a
# component the early return can reach. Below, that set is computed from the
# source rather than assumed — the first draft of this file hardcoded
# `Public.tsx`, which would have passed for as long as the file existed and
# said nothing about whether App still rendered it.


def _pre_session_components() -> set[str]:
    """The components App renders while `session.profileId` is unset."""
    app_tsx = (SRC / "App.tsx").read_text(encoding="utf-8")
    start = app_tsx.index("if (!session.profileId)")
    # To the end of the early return — the next line at function indent that
    # begins a new statement. The `return (` block is what we want and the
    # signed-in `return (` below it is what we must not swallow.
    tail = app_tsx[start:]
    end = tail.index("\n  return (")
    return set(re.findall(r"<(\w+)[\s/>]", tail[:end]))


def _calls_in(component: str, seen: set[str] | None = None) -> set[str]:
    """`api.x(` names reachable from a component, following its imports."""
    seen = seen if seen is not None else set()
    if component in seen:
        return set()
    seen.add(component)
    for path in (SRC / f"{component}.tsx", SRC / "screens" / f"{component}.tsx"):
        if path.exists():
            break
    else:
        return set()
    text = path.read_text(encoding="utf-8")
    calls = set(re.findall(r"\bapi\.(\w+)\s*\(", text))
    for child in re.findall(r'from "\.{1,2}/(?:screens/)?(\w+)"', text):
        calls |= _calls_in(child, seen)
    return calls


def test_the_console_opens_the_public_doors_without_an_account():
    """The check that would have failed before this round, and did."""
    reachable: set[str] = set()
    for component in _pre_session_components():
        reachable |= _calls_in(component)

    missing = sorted(f"{path}  ({binding})"
                     for path, binding in PUBLIC_PATHS.items()
                     if binding not in reachable)
    assert not missing, (
        "the console reaches these only after a profile exists:\n    "
        + "\n    ".join(missing)
        + "\n  Their callers are, by construction, people without an account: "
          "somebody contesting a synthetic profile of themselves, and somebody "
          "asking whether what they are holding was written by a person. "
          "Reaching them must not require signing up to the platform they are "
          "asking about.")


def test_the_pre_session_branch_is_actually_being_read():
    """A guard on the guard.

    `_pre_session_components` finds components by slicing App.tsx between two
    string literals. If either moves, the slice silently becomes empty or
    becomes the whole file — one of which passes everything and the other of
    which passes nothing for the wrong reason. Five false positives in this
    audit came from a pattern that quietly stopped matching.
    """
    found = _pre_session_components()
    assert "Onboarding" in found, (
        "the pre-session branch of App.tsx no longer renders Onboarding — the "
        "slice above has stopped finding what it was reading")
    assert "Home" not in found, (
        "the slice has run past the early return into the signed-in tabs, so "
        "it would report the whole console as reachable without an account")


# --- the three shells -------------------------------------------------------
#
# Each has one gate and it is a single conditional in the root view:
#
#     iOS      if state.isSignedIn { TabView { … } } else { WelcomeView() }
#     Android  if (!vm.isSignedIn) { WelcomeScreen(vm) } else { … }
#     Windows  RootFrame.Navigate(IsSignedIn ? ShellPage : WelcomePage)
#
# So the pre-session surface is the welcome screen and whatever it opens.
# Rather than model three languages' control flow, the check below asks the
# narrower question that is still the one that matters: does the file the
# gate falls through to reach the public binding, directly or through a view
# it names.

#: (label, welcome file, files it may open, bindings as that shell spells them)
SHELLS = (
    ("ios",
     "native/ios/Sources/Views/WelcomeView.swift",
     ("native/ios/Sources/Views/WithoutAnAccountView.swift",),
     ("openObjection", "recoverWatermark")),
    ("android",
     "native/android/app/src/main/java/app/qrme/studio/ui/Screens.kt",
     (),   # the welcome screen and its public door are in the same file
     ("openObjection", "recoverWatermark")),
    ("windows",
     "native/windows/Views/WelcomePage.xaml.cs",
     ("native/windows/Views/WithoutAnAccountPage.xaml.cs",),
     ("OpenObjection", "RecoverWatermark")),
)


def _shell_text(welcome: str, opens: tuple[str, ...]) -> str:
    paths = [REPO / welcome] + [REPO / p for p in opens]
    return "\n".join(p.read_text(encoding="utf-8") for p in paths if p.exists())


def test_every_shell_opens_the_public_doors_before_sign_in():
    """Android's whole console is one file, so this is a weaker check there
    than for iOS and Windows — it cannot distinguish the welcome screen's
    reach from the signed-in screens'. `test_each_shell_names_its_public_door`
    below is what carries Android: the welcome composable must name the public
    one, which is the edge the gate actually falls through."""
    missing = []
    for name, welcome, opens, bindings in SHELLS:
        if not (REPO / welcome).exists():
            continue
        text = _shell_text(welcome, opens)
        missing += [f"{name}: {b}" for b in bindings
                    if not re.search(rf"\b{b}\s*\(", text)]
    assert not missing, (
        "these shells reach the public routes only from a signed-in screen:\n"
        "    " + "\n    ".join(missing)
        + "\n  The person the objection route was written for has no account "
          "by construction — a call site inside the tab bar is not a door "
          "they can open.")


def test_each_shell_names_its_public_door():
    """The edge, not the destination.

    A view that exists and is never presented is the binding problem one level
    up, and this audit has now made that mistake twice. Each welcome screen
    must name the thing it opens.
    """
    edges = {
        "ios": ("native/ios/Sources/Views/WelcomeView.swift",
                "WithoutAnAccountView()"),
        "android": ("native/android/app/src/main/java/app/qrme/studio/ui/Screens.kt",
                    "WithoutAnAccountScreen(vm)"),
        "windows": ("native/windows/Views/WelcomePage.xaml.cs",
                    "typeof(WithoutAnAccountPage)"),
    }
    broken = []
    for name, (path, edge) in edges.items():
        p = REPO / path
        if not p.exists():
            continue
        # Comments stripped: a doc comment naming the view is exactly the
        # match that produced the sixth false positive in this audit.
        text = p.read_text(encoding="utf-8")
        code = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
        if edge not in code:
            broken.append(f"{name}: {path} never presents {edge}")
    assert not broken, (
        "the public screen exists and nothing opens it:\n    "
        + "\n    ".join(broken))


def test_the_promise_and_the_door_are_on_the_same_surface():
    """The specific thing that made this worth a round.

    A screen may say 'you do not need an account' only if somebody without one
    can be looking at it. The sentence was true of the route and false of the
    page it was printed on, and a sentence like that is worse than silence: it
    tells the person who most needs the door that the door is already open.
    """
    pre = _pre_session_components()
    claims = []
    for path in sorted(SRC.rglob("*.tsx")):
        text = path.read_text(encoding="utf-8")
        # Prose, not comments — a doc comment explaining the history is
        # exactly the kind of match that made the sixth false positive.
        prose = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
        if re.search(r"do not need an account|need no account|without an account",
                     prose, re.I):
            claims.append(path.stem)

    stranded = sorted(c for c in claims if c not in pre)
    assert not stranded, (
        "these surfaces tell the reader they do not need an account, and are "
        f"reachable only after signing up: {stranded}\n  Either move the door "
        "to a surface a stranger can reach, or stop making the promise.")
