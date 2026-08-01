"""The accountless screen, in the three shells that are not a browser.

## The finding

Two rounds localized the browser's half of this. `Public.tsx` reads
`navigator.languages`, its frame is in ten languages, and the four public
routes now answer in the reader's language too.

The three native shells each carry the same screen — `WithoutAnAccountView`,
`WithoutAnAccountScreen`, `WithoutAnAccountPage` — built in an earlier round
for exactly the same person: somebody who has found a synthetic profile of
themselves, or is holding a screenshot and wants to know whether a person
wrote it. On all three, that screen is English and can only be English:

* Not one of them references its shell's `L10n` table at all. iOS's has ten
  languages in it and `WithoutAnAccountView.swift` contains zero `L10n.`
  calls.
* More to the point, **there was no language to pass**. Every shell's
  `language` is read from the profile's stored setting and is `"en"` until a
  profile exists. The one screen whose reader has no profile is the one
  screen where that value is guaranteed to be the default.

The same shape as the browser had, on three more clients — and the union
would have hidden it, which is the mistake this audit is named for: *some*
client localizes the accountless surface, and the three that a person is
most likely to be holding do not.

## What this round did, and what it did not

It supplied the missing input. `L10n.deviceLanguage` (iOS),
`L10n.deviceLanguage()` (Android) and `L10n.DeviceLanguage()` (Windows) read
the language the device has been carrying all along — `Locale.
preferredLanguages`, the system configuration's locale list,
`CurrentUICulture` — drop the region, and fall back to English rather than
guessing. Nothing can be translated on those screens until that exists.

It did **not** move the strings. Twenty-odd sentences on each of three
screens is its own round, and half-porting them across shells would be the
per-client mistake in miniature — one phone localized, two not. They are
recorded in `native_untranslated.txt`, which only shrinks, so the remainder
is a decision somebody wrote down rather than something nobody noticed.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SNAPSHOT = Path(__file__).resolve().parent / "native_untranslated.txt"

#: (label, the shell's L10n file, the symbol that resolves a device language,
#:  the accountless screen)
SHELLS = (
    ("ios",
     "native/ios/Sources/L10n.swift", "deviceLanguage",
     "native/ios/Sources/Views/WithoutAnAccountView.swift"),
    ("android",
     "native/android/app/src/main/java/app/qrme/studio/L10n.kt",
     "deviceLanguage",
     "native/android/app/src/main/java/app/qrme/studio/ui/Screens.kt"),
    ("windows",
     "native/windows/L10n.cs", "DeviceLanguage",
     "native/windows/Views/WithoutAnAccountPage.xaml.cs"),
)

#: How each shell asks its platform. Named so that deleting the *body* of a
#: resolver while leaving its name behind fails here rather than passing.
PLATFORM_SOURCE = {
    "ios": "Locale.preferredLanguages",
    "android": "Resources.getSystem().configuration.locales",
    "windows": "CurrentUICulture",
}


def _code(path: Path) -> str:
    """Source with comments and doc comments stripped.

    Every one of these resolvers is *described* in the comment above it, so a
    check that searched the whole file would be satisfied by the prose
    explaining the thing rather than the thing. That has happened eight times
    in this audit and three of those were inside guards written to prevent it.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*(///|//|\*)[^\n]*$", "", text, flags=re.M)
    return text


def test_every_shell_can_resolve_a_language_without_a_profile():
    """The input that was missing.

    Not "does the shell have an L10n table" — all three did, in ten
    languages, while the accountless screen could only ever be English
    because the only language variable in the app came from a profile.
    """
    missing = []
    for name, l10n, symbol, _ in SHELLS:
        path = REPO / l10n
        if not path.exists():
            continue
        code = _code(path)
        if symbol not in code:
            missing.append(f"{name}: {l10n} has no {symbol}")
        elif PLATFORM_SOURCE[name] not in code:
            missing.append(
                f"{name}: {symbol} exists but never reads "
                f"{PLATFORM_SOURCE[name]} — it is not asking the device")
    assert not missing, (
        "these shells cannot work out what language their reader speaks "
        "without a profile:\n    " + "\n    ".join(missing)
        + "\n  The one screen in each of them built for somebody with no "
          "profile is the one screen where the profile's setting is "
          "guaranteed to be the default.")


def test_no_shell_takes_the_accountless_screens_language_from_a_profile():
    """The specific wrong answer, named.

    A shell that resolves `deviceLanguage` and then passes `state.language`
    to the accountless screen has done the work and thrown it away. The
    check that would miss this is the one that only asks whether the resolver
    exists.
    """
    for name, _, symbol, screen in SHELLS:
        path = REPO / screen
        if not path.exists():
            continue
        code = _code(path)
        # Android's whole console is one file, so the search is narrowed to
        # the accountless composable rather than the whole of Screens.kt.
        if name == "android":
            start = code.find("fun WithoutAnAccountScreen")
            if start == -1:
                continue
            end = code.find("\nfun ", start + 1)
            code = code[start:end if end != -1 else len(code)]
        for wrong in ("state.language", "vm.language", "AppState.Language",
                      "State.Language"):
            assert wrong not in code, (
                f"{name}'s accountless screen reads {wrong}, which is the "
                "profile's setting — and its reader has no profile, so that "
                f"value is always the default. Use {symbol}.")


def _recorded() -> set[str]:
    return {line.strip() for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_native_backlog_is_written_down_and_only_shrinks():
    """What this round deliberately left.

    The strings themselves — twenty-odd sentences on each of three screens —
    are their own round. Recording them is the difference between a decision
    and an oversight, and it is the same ratchet
    `public_untranslated.txt` uses for the browser's half.
    """
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            SNAPSHOT.read_text(encoding="utf-8")).group(1))
    recorded = _recorded()
    assert recorded, "the snapshot is empty but the round is not finished"
    assert len(recorded) <= ceiling, (
        f"{len(recorded)} entries, above the {ceiling} this guard started at")

    # Each line names a shell that really exists, so the file cannot rot into
    # a list of screens somebody renamed two releases ago.
    shells = {name for name, _, _, _ in SHELLS}
    unknown = sorted(line for line in recorded
                     if line.split(":")[0].strip() not in shells)
    assert not unknown, (
        "these entries name a shell this repo does not have:\n    "
        + "\n    ".join(unknown))


def test_the_screens_the_backlog_names_are_still_there():
    """A guard on the guard: a recorded screen that has been deleted makes
    the backlog look smaller without anything having been translated."""
    for name, _, _, screen in SHELLS:
        assert (REPO / screen).exists(), (
            f"{name}'s accountless screen is gone from {screen} — the "
            "backlog below is measuring nothing")
