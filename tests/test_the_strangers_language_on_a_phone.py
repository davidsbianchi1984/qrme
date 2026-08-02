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


def _accountless(name: str, code: str) -> str:
    """Android's whole console is one file, so the search is narrowed to the
    accountless composable rather than the whole of Screens.kt."""
    if name != "android":
        return code
    start = code.find("fun WithoutAnAccountScreen")
    if start == -1:
        return ""
    end = code.find("\nfun ", start + 1)
    return code[start:end if end != -1 else len(code)]


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
        code = _accountless(name, _code(path))
        for wrong in ("state.language", "vm.language", "AppState.Language",
                      "State.Language"):
            assert wrong not in code, (
                f"{name}'s accountless screen reads {wrong}, which is the "
                "profile's setting — and its reader has no profile, so that "
                f"value is always the default. Use {symbol}.")


# --- the round after: the language nobody was sending -----------------------
#
# Supplying `deviceLanguage` fixed the words each shell owns. It did not fix
# the ones it does not. `governance.py` composes the sentence a person reads
# when they open an objection, when they end a profile, and on the timeline of
# their own case, and it picks the language from `Accept-Language`. No native
# shell was sending that header. The browser sends it without being asked,
# which is exactly why the three clients a contested person is most likely to
# be holding were the ones still answering in English after the routes learned
# to speak.
#
#     asked     can the shell say it in the reader's language
#     mattered  does the reader's language ever reach the server

#: (label, the shell's HTTP client, the resolver as written at the call site)
HTTP_CLIENTS = (
    ("ios", "native/ios/Sources/ApiClient.swift", "L10n.deviceLanguage"),
    ("android",
     "native/android/app/src/main/java/app/qrme/studio/ApiClient.kt",
     "L10n.deviceLanguage()"),
    ("windows", "native/windows/ApiClient.cs", "L10n.DeviceLanguage()"),
)

#: How each shell asks its own chrome table for a string.
TRANSLATOR = {"ios": "L10n.t(", "android": "L10n.t(", "windows": "L10n.T("}


def test_every_shell_tells_the_server_what_language_its_reader_speaks():
    """Both halves, because a header set to the wrong thing looks identical
    to a header set to the right thing from the outside: the shell must send
    `Accept-Language`, **and** what it sends must come from the device
    resolver rather than a constant or the profile's setting."""
    wrong = []
    for name, client, resolver in HTTP_CLIENTS:
        path = REPO / client
        if not path.exists():
            continue
        lines = [ln for ln in _code(path).splitlines()
                 if "accept-language" in ln.lower()]
        if not lines:
            wrong.append(f"{name}: {client} never sets an accept-language "
                         "header, so every sentence the backend composes for "
                         "a reader with no profile arrives in English")
        elif [ln for ln in lines if resolver not in ln]:
            # Every line, not any line. A client can build requests in more
            # than one place — PDI's iOS client has the shared helper and the
            # intake submit its accountless recipient uses — and an `any` here
            # passed an injection that hardcoded "en" on one of them, because
            # the other one was still right. The union hid a surface inside
            # the guard written to stop exactly that.
            #
            #     asked     does this client send the reader's language
            #     mattered  does every request this client makes send it
            bad = len([ln for ln in lines if resolver not in ln])
            wrong.append(f"{name}: {bad} of {len(lines)} accept-language "
                         f"header(s) set without {resolver} — the header is "
                         "there and the reader's language is not in it")
    assert not wrong, "\n    ".join([""] + wrong)


def _arity(code: str, open_paren: int) -> int:
    """How many arguments the call whose `(` is at `open_paren` was given.

    String-aware, because every one of these calls takes a quoted key first
    and half of them build it by interpolation — a comma inside `"obj.event.
    \\(e.event)"` is not an argument separator, and a scanner that thought it
    was would find two arguments in a one-argument call and pass.
    """
    depth, args, quote, i, seen = 0, 1, "", open_paren, False
    while i < len(code):
        c = code[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = ""
        else:
            if depth == 1 and not c.isspace() and c not in ")]}":
                # Anything at all between the brackets — including the opening
                # quote of the key, which an earlier draft of this scanner
                # skipped straight past, so `T("k")` counted as no arguments.
                seen = True
            if c in "\"'":
                quote = c
            elif c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
                if depth == 0:
                    return args if seen else 0
            elif c == "," and depth == 1:
                args += 1
        i += 1
    raise AssertionError(f"unbalanced call at offset {open_paren}")


def test_the_accountless_screen_never_asks_for_a_string_without_a_language():
    """The Windows-shaped version of the same mistake.

    iOS and Android cannot make it: both `t` functions require the language as
    an argument, so a screen that forgets one does not compile. Windows'
    `T(key)` reads `AppState.Current.Language` — the profile's setting — and
    the accountless screen can reach it by writing nothing at all. The
    existing check greps this screen for the profile's name and would not see
    it, because the screen never names it; the overload does.
    """
    for name, _, symbol, screen in SHELLS:
        path = REPO / screen
        if not path.exists():
            continue
        code = _accountless(name, _code(path))
        call = TRANSLATOR[name]
        for m in re.finditer(re.escape(call), code):
            n = _arity(code, m.end() - 1)
            assert n >= 2, (
                f"{name}: {screen} calls {call.rstrip('(')} with {n} "
                "argument(s) at offset "
                f"{m.start()} — no language, so it falls back to whatever the "
                f"shell's default is. Pass {symbol}.")


def test_the_arity_scanner_can_count():
    """A guard on the guard: a scanner that returned 2 for everything would
    pass the check above on a screen with no languages in it at all."""
    def n(src: str) -> int:
        return _arity(src, src.index("("))

    assert n('L10n.T("k")') == 1
    assert n('L10n.T("k", lang)') == 2
    assert n('L10n.T("a, b")') == 1, "a comma inside a string"
    assert n('L10n.t("obj.event.\\(e.event)", lang)') == 2
    assert n('L10n.T(Fmt("a", "b"), lang)') == 2, "a nested call"
    assert n("L10n.T()") == 0


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
    # It used to say "the snapshot is empty but the round is not finished".
    # The round is finished, and an empty file is now the right answer — held
    # up by `test_no_accountless_screen_has_english_of_its_own` below rather
    # than by anybody's word.
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


# --- the round after that: the strings themselves ---------------------------
#
# `native_untranslated.txt` recorded three shells and only shrank, which made
# the remainder a decision rather than an oversight. It could also be driven to
# zero by deleting three lines: nothing here read the screens.
#
#     asked     is the backlog written down and shrinking
#     mattered  did anything get translated
#
# So the floor is now held up by the screens rather than by the file. The
# checks below borrow the *sibling guard's* extraction patterns rather than
# writing their own, because two definitions of "an English string on a screen"
# is two numbers that can disagree, and the disagreement would live in
# whichever one nobody was reading.

from tests.test_the_tabs_are_translated_and_the_screens_are_not import (  # noqa: E402
    SHELLS as _COUNTED, _HAS_LETTER, _HOLE, _code as _screen_code)

CONSOLE_TABLE = REPO / "app" / "src" / "l10n.ts"

#: Keys the shells carry that the console has no row for, each with the reason.
#: Everything else must be a port — a second translation of the same sentence
#: is a second thing to keep in step, and it drifts first in the language
#: nobody here reads.
SHELL_ONLY = {
    "pub.back.short": "a sheet's dismiss button; the console's `pub.back` says "
                      "'Back to sign in', which is a browser's whole-page nav",
    "pub.object.needid": "client-side validation; the console validates in the "
                         "form and never composes this sentence",
    "pub.mark.needtext": "the same, on the other pane",
    "pub.object.ref.ph": "a placeholder; the console's field has none",
}


#: Literals the extraction sees and no reader reads. One entry, and it is an
#: identifier prefix: `prf_…` is what a QRME profile id starts with, and it
#: starts with that in all ten languages. Declared rather than translated,
#: because a translated `prf_…` would be a wrong hint in nine of them — and
#: declared rather than skipped by a widened pattern, because "strings that
#: look like identifiers" is a rule that would quietly swallow real prose.
NOT_PROSE = {
    "prf_…": "the literal prefix of every profile id, in every language",
}


def _accountless_files(name: str) -> list[Path]:
    """The screen, as files. Windows is two — the markup and the code-behind —
    and the markup is where every one of its strings used to live, which is why
    that shell's count was the largest of the nine."""
    if name == "windows":
        return [REPO / "native/windows/Views/WithoutAnAccountPage.xaml",
                REPO / "native/windows/Views/WithoutAnAccountPage.xaml.cs"]
    return [REPO / dict((n, scr) for n, _, _, scr in SHELLS)[name]]


def _accountless_text(name: str) -> str:
    out = []
    for path in _accountless_files(name):
        if not path.exists():
            continue
        text = _screen_code(path)
        out.append(_accountless(name, text) if name == "android" else text)
    return "\n".join(out)


def test_no_accountless_screen_has_english_of_its_own():
    """The strings, not the record of the strings.

    Deleting three lines from `native_untranslated.txt` would have satisfied
    the ratchet above with all three screens still in English. This reads the
    screens.
    """
    left = []
    for name, _, _, _ in SHELLS:
        patterns = _COUNTED[name][2]
        text = _accountless_text(name)
        found = {s for pat in patterns for s in re.findall(pat, text)
                 if _HAS_LETTER.search(_HOLE.sub("", s))}
        left += [f"{name}: {s[:72]}" for s in sorted(found - set(NOT_PROSE))]
    assert not left, (
        f"{len(left)} English string(s) still on the one screen in each shell "
        "built for somebody with no profile — and therefore no profile "
        "language:\n    " + "\n    ".join(left))


def test_the_screen_scan_is_reading_the_screens():
    """A guard on the guard: a path that stopped resolving would report no
    English and pass the check above on an empty string."""
    for name, _, _, _ in SHELLS:
        text = _accountless_text(name)
        assert len(text) > 800, (
            f"{name}'s accountless screen read as {len(text)} characters — the "
            "check above is passing on nothing")


def _keys_used(name: str) -> set[str]:
    return set(re.findall(r'"(pub\.[\w.]+)"', _accountless_text(name)))


def test_the_shells_say_what_the_console_says():
    """Ported, not translated again.

    The console had these sixty-four rows in ten languages before this round.
    A shell that writes its own is a second wording of the same sentence, and
    the drift shows up first in the language nobody here reads.
    """
    console = set(re.findall(
        r'"(pub\.[\w.]+)":', CONSOLE_TABLE.read_text(encoding="utf-8")))
    invented = []
    for name, _, _, _ in SHELLS:
        for key in sorted(_keys_used(name)):
            if key.startswith("pub.state."):
                continue          # substituted into a sentence, never shown raw
            if key not in console and key not in SHELL_ONLY:
                invented.append(f"{name}: {key}")
    assert not invented, (
        "these keys exist on a shell and not in the console's table, and are "
        "not declared shell-only with a reason:\n    " + "\n    ".join(invented))


def test_every_shell_only_key_is_still_used_by_a_shell():
    """An exemption for a key nothing renders is a paragraph in front of
    nothing."""
    used = set().union(*(_keys_used(n) for n, _, _, _ in SHELLS))
    stale = sorted(k for k in SHELL_ONLY if k not in used)
    assert not stale, (
        "these shell-only keys are on no screen — strike them:\n    "
        + "\n    ".join(stale))


def test_every_ported_row_carries_every_language():
    """Ten languages, or the row is a promise the table does not keep.

    A key present with three languages passes a check that only asks whether
    the key is there, and answers the other seven readers in English.
    """
    langs = ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")
    thin = []
    for name, l10n, _, _ in SHELLS:
        path = REPO / l10n
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.search(r'"(pub\.[\w.]+)"', line)
            if not m:
                continue
            missing = [c for c in langs
                       if not re.search(rf'"{c}"\s*(?::|to|\])\s*=?\s*"', line)]
            if missing:
                thin.append(f"{name} {m.group(1)}: missing {', '.join(missing)}")
    assert not thin, (
        "these rows are not in every language:\n    " + "\n    ".join(thin))


def test_every_not_prose_literal_is_still_on_a_screen():
    """A guard on the exemption: a literal nothing renders any more is a hole
    with a paragraph in front of it, which is how the seven ungated tables in
    the release before this one looked."""
    text = "\n".join(_accountless_text(n) for n, _, _, _ in SHELLS)
    stale = sorted(k for k in NOT_PROSE if k not in text)
    assert not stale, (
        "these exempt literals are on no screen — strike them:\n    "
        + "\n    ".join(stale))
