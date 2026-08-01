# QRME v0.24.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.24.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

Nine rounds, one question: **when a stranger does reach the thing built for
them, can they read what it says?**

The last release opened the doors — the objector, the person asking whether
what they were sent is genuine, the person checking they met the same profile
twice. This one is what is written on the other side of them, and every
finding is the same shape a layer further in: a surface localized while the
sentence it answers with was not.

## The screen was in ten languages and the answers were in one

`qrme/i18n.py` takes a `profile_id`. The accountless screen's reader has
none, so that module could not have answered them even if something had
asked. A visitor in Osaka got a Japanese page, pasted in a piece of text,
pressed a Japanese button, and was told in English:

> no stamped work shares any wording with this text

which is the answer to the only question they came with. The restriction
notice after opening an objection, the consistency guarantee, the
synthetic-media disclosure, the recovery method and every refusal were the
same.

Thirteen sentences in ten languages, hand-translated rather than
machine-translated, in a table separate from the per-profile machinery above
it. Four public routes read `Accept-Language`; `refusals_in` translates what
they raise, narrowly, so an owner's refusal is untouched.

**The state words are deliberately not translated.** The first version of
this translated `status` too, and driving it caught the cost: `Contest.tsx`
branches on `status === "open"` to show the card a subject or an estate uses
to end a case immediately. A Japanese browser would have made that control
vanish from a signed-in screen. What a person reads is translated; what a
client compares is not.

## Twenty-five strings on the public screen, five in the ledger

The backlog file listed five sentence fragments and called them the hard
remainder. They were what a regex over TSX happened to be able to see:
`>([^<>{}]+)<` excludes braces, so every sentence wrapping an interpolated
value was skipped whole, and the five reported were their brace-free scraps.
TypeScript generics look like tags to that pattern, which is why it had grown
a rule dropping lines with `=`, `;` or `=>` — and that rule then swallowed
the mark pane's entire explanatory paragraph.

`app/scripts/jsx-text.mjs` asks TypeScript's own parser for `JsxText` nodes
instead. Twelve new keys in ten languages, and `fill()` so a sentence with
named holes stays one translatable unit rather than three fragments no
translator can reorder.

## The pre-session surface is two screens

That guard measured `Public.tsx` alone and reported the pre-session surface
clean. `App.tsx` renders two things before a profile exists, and the other is
the one everybody meets first. `Onboarding.tsx` carries thirty-seven English
strings while already calling `visitorLang()` three times — on the links
pointing at the accountless screen. The round that localized the door
localized the sign to the door and stopped.

Recorded and ratcheted rather than half-translated: a partly-translated
sign-up form reads as broken software at the moment somebody is deciding
whether to trust it with their email address.

## Three phones with no way to ask

Every native shell's `language` is read from the profile's stored setting, so
the one screen whose reader has no profile is the one screen where that value
is guaranteed to be the default. `WithoutAnAccountView.swift` contains no
`L10n.` calls beside a table with ten languages in it — and there was nothing
to pass it.

iOS, Android and Windows now resolve a device language from
`Locale.preferredLanguages`, the system locale list and `CurrentUICulture`,
region dropped, English as a fallback rather than a guess. The screens'
strings are recorded, all three shells or none.

## One header, three products

QRME, JIM-mini and PDI each grew a `negotiate()` in a different round.
Compared side by side for the first time, two rows disagreed — `ar;q=0` and
`de;q=abc`. `q=0` means *not acceptable*, so a browser sending `ar;q=0` is
refusing Arabic. A conformance table now lives byte-identically in all three
repositories.

## Also

- `test_the_promise_and_the_door_are_on_the_same_surface` could no longer see
  a claim made through a lookup key. Injecting a localized no-account claim
  into a gated screen passed against the shipped guard; both it and its
  positive control now resolve text through `l10n.ts`.

**2097 tests passing.**
