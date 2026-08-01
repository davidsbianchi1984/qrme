# Changelog

All notable changes to QRME are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.28.0] — 2026-08-01

Aligned with JIM-mini 0.28.0. The three products carry one version, so a
release that only moves in one of them still moves in all three.

Nothing in this product's own code changed this cut. JIM's console gained the
localization layer whose absence was measured last release, and two of its
guards broke on the way — both asking whether a sentence was in a screen's
*file* when what mattered was whether the screen *says* it. Neither surface
exists here in that form.

## [0.27.0] — 2026-08-01

### The screen everybody meets first

`public_untranslated.txt` recorded thirty-seven English strings on the
pre-session surface, thirty-six of them on `Onboarding.tsx` — the screen every
single person meets before any account exists anywhere. Two releases localized
the accountless *door* and the routes behind it; the sign-up form itself was
still English in ten languages' worth of browsers.

Twenty-two keys, hand-translated across all ten: the tagline, both mode
buttons, every field label and placeholder, the verification and reset codes,
the password rules and the mismatch warning, the profile name and persona. The
backlog is **37 → 20**, and what is left is explanatory prose rather than
anything with an action attached.

The completeness guard only looked at keys prefixed `pub.`, so twenty-two
`onb.` keys would have been invisible to it — a check reporting a complete
table while no longer reading all of it.

    asked     are the `pub.` keys complete
    mattered  are the keys a pre-session screen looks up complete

### Kotlin's other interpolation

`_spans` routes every `${`-carrying pattern to a brace counter, which is right
for the nested-template problem it was written for and blind to the *other*
form the same language uses. Kotlin interpolates `${expr}` **and** a bare
`$ident`, and only the first was ever substituted — so `"/users/$uid/meds"`
normalised to itself.

    asked     does this language interpolate with braces
    mattered  what are all the ways this language interpolates

It never produced a wrong verdict, which is why it lasted: Starlette's path
parameter matches any segment, so `$uid` resolved against `{uid}` by accident.
But the optional-parameter cut looks for a quoted `?` *inside an interpolation
span*, and a span never found cannot be looked inside — a Kotlin call written
with the `$flag` idiom would have carried its query into the path. The
divergence recorded last release is now closed rather than recorded.

### The collector fills its own disk

`cloudgw/problems.py` is careful about each report — fifty problems at most,
short strings bounded, a day and not a timestamp, four classes of leak refused
outright. Every one of those is a check on the message.

Nothing checked the accumulation. `Aggregate._rows` is a plain dict keyed on
`(source, app_version, platform, op, status)`, and `app_version` is any short
string the caller sends, so the key space grew with every release forever —
and with every *claimed* release, from anyone holding a posting token.

    asked     is each report small and well-formed
    mattered  is the thing they accumulate into bounded

A collector that fills its own disk stops answering `/health`, which is the
one route an orchestrator uses to decide whether to restart it; on a gateway
that also serves the greater model, the diagnostic becomes the outage.

Evicting rather than refusing, because the counters are advisory and refusing
new reports to protect old ones preserves exactly the rows least worth
keeping. Ordered by `last_day` then `count`, so a failure still happening
outlives one that stopped. The dropped count is reported: a number that
silently stops growing looks exactly like a product that stopped failing.

## [0.26.0] — 2026-08-01

### Three copies of one guard, three different blind spots

`clientpaths.py` says of itself, in its own docstring, that it is *byte-
identical in qrme, jim-mini and pdi*. It was not, and nothing checked.

JIM's had grown two capabilities the other two never received. So the same
audit, asked the same question in three repositories, gave three different
answers — and each repository believed it was running the same check.

    asked     does this repo's audit pass
    mattered  is this repo's audit the same audit

PDI's Android client submits an intake through exactly the form its extractor
could not see. `POST /intakes/{iid}/submit` had a working door and sat in
`android_doorless.txt` as missing — the guard could see neither the call nor
its own error.

Porting the missing capability produced a second finding one layer in: the
rule arrived carrying its author's premise. The direct-connection form was
declared `verb="GET"` on the reasoning that *every array route in this shell
is a GET* — true where it was written, false in PDI, which POSTs. The verb is
now read from the `.apply { }` block, which needed the extractor to look past
a call's own parentheses for the first time (`verb_after`).

`test_the_extractors_agree.py` runs each extractor over a fixture whose answer
is written down, so a capability lost in any one repository fails **there**
rather than reporting a clean sweep. It immediately found a third divergence:
iOS and Windows normalise an interpolated segment to a placeholder and Kotlin
leaves `$id` standing. Harmless today — Starlette matches either — and written
down rather than quietly encoded, because a difference nobody has looked at is
how the first three started.

### The notice that makes it real

Last round's sender answered `awaitingNotice` on every launch, because there
was no surface to answer it on. That is the safe direction to be wrong in and
it is still wrong: a mechanism nobody can reach is a mechanism nobody chose.

Nine shells now carry a reporting card — on the screen each product already
uses for data posture. Two rules it exists to keep:

* **Show the report, do not describe it.** The preview is built by
  `Problems.report`, the same call the sender posts, so what is on screen is
  the payload. A card that said "we collect anonymous diagnostics" would be
  asking somebody to take our word for it, and would drift the first time the
  payload changed — silently, in the direction of a promise nobody is keeping.
* **No pre-ticked answer.** Neither button is painted as the expected one. A
  notice with a bright Yes and a grey No has made the choice already, and that
  is not consent — it is a layout that looks like consent.

Answering yes sends immediately rather than waiting for the next launch, so
the person who just agreed watches the buffer drain instead of being told
something happened later. A build with no address compiled in says so plainly
rather than asking for permission it has no use for.

The guard grew two checks that both caught the guard itself first. The
emphasis check searched whole files and failed on a button three sections up
that belongs to a different card; scoped to the answers, it then read one line
at a time and missed its own injection, because Swift puts the style on a
wrapped modifier below the label.

    asked     does this file mention the brand colour anywhere
    mattered  do the two answers differ in emphasis

### The drawer nobody empties

Task #110 gave all three native shells content-free error capture, and it did
that part well: `record` templates the route, drops the message, keeps the day
and not the time, and redacts on the way *in* so the buffer never holds
something that would later have to be scrubbed.

Then nothing sent it anywhere.

Nine shells across three products recorded failures into a fifty-row buffer
that filled and rolled over. Only the desktop console ever had the second
half. The tell was in the model the whole time: every shell declares a `sent`
field documented as *"how much of `count` has already been reported"*, and
nothing in any of them ever read it, because nothing ever reported. The
comment described behaviour that was not in the file.

    asked     is the failure recorded without recording anything private
    mattered  does the failure reach anybody

Written per shell rather than as a union — the console having both halves is
exactly what made this invisible for four releases. "Error reporting works"
was true of one client in four, per product.

Each of the nine now has a report builder, a watermark that advances **by
amount and not by a flag** (a row goes on counting while the request is in
flight, and a flag drops every occurrence that happened during the send), a
collector address that is empty until a release stamps one, a notice gate, and
a call at launch. The address comes from the build — `Info.plist` on iOS, a
gradle `buildConfigField` on Android, `AssemblyMetadata` on Windows — for the
same reason the console's does: an install with no address has nowhere to
send, and there is no flag for a later mistake to switch on.

**Nothing sends yet, deliberately.** `send` answers `awaitingNotice` until
somebody has been told what a report contains and chosen. The notice and the
off-switch need a surface on each shell's settings screen, and that is the
next round; until it lands the mechanism is inert by its own gate rather than
by omission.

### Two things the round turned up on its way through

**A path that belongs to another service.** The existing route guard refused
the new call: `/v1/problems` is on the Cloud Model Gateway, not on this
product's API. `NOT_A_CLIENT_CALL` was the wrong home for it — that list is
for paths *nothing should ever call*, and its own comment says to exempt a
path only for that reason and never because the audit cannot see the call. So
`ANOTHER_SERVICE` is a separate list with a separate rule: a different
deployment owns this path.

**The same guard in three repos disagrees about what it can see.** JIM's
extractor found the Android literal; QRME's and PDI's did not, and none of the
three sees the iOS or Windows equivalents. Recorded rather than fixed here —
three copies of one guard with three different blind spots is its own round,
and it is the audit's shape applied to the audit.

## [0.25.0] — 2026-08-01

Two outstanding console tasks — Google/Apple credentials and the Windows Hello
field test — written down field by field. Writing them down found a defect in
each.

### A relying party id is a domain, and `127.0.0.1` is not one

`docs/signatures.md` is careful that the ceremony must run on the relying
party's own origin, and every client obeys it: the Windows shell embeds a
WebView2 pointed at `/signatures/ceremony`, the console opens the same page.
Both fetch it from `http://127.0.0.1:8000` — the default base address — and
`QRME_RP_ID` defaults to `qrme.app`.

Neither can host a ceremony. `rp.id` must be a **domain**, so an IP-address
origin has none it could use; and `qrme.app` is not a suffix of a loopback
host either. The Register and Sign buttons had never worked from a default
install and could not, and the browser's refusal arrives inside an embedded
WebView as a DOMException that reads like a declined credential rather than a
wrong address.

    asked     does the ceremony run on the relying party's own origin
    mattered  can that origin be a relying party at all

Both clients now rewrite a loopback IP to `localhost` — a domain, the same
backend, a secure context without a certificate — and the ceremony route
refuses a pairing that cannot work with a **page** naming the variable to
change, because a JSON error inside a WebView is a blank panel.

### The Apple client secret expires and nothing says so

`QRME_APPLE_CLIENT_SECRET` is not a string you copy once. It is an ES256 JWT
minted from a `.p8`, capped by Apple at six months, with no renewal notice
and no degraded mode — on the day it lapses every token exchange answers
`invalid_client`. `providers()` reports the door open the entire time,
because it asks whether the variable is *set*.

`scripts/mint_apple_secret.py` mints it and reads its expiry without needing
the key, exiting non-zero inside the last thirty days so a health check can
act. Two things it gets right that are easy to get wrong: JWS wants a raw
64-byte `r || s` signature where `cryptography` returns DER, and a lifetime
past Apple's ceiling is refused at minting rather than at the exchange. The
test verifies the signature with the public key instead of measuring it.

### Added

- `docs/sign-in.md` — every field of the Google Web-application client and
  the Apple Services ID, with the return addresses, the scopes that keep it
  out of verification review, and why a Desktop-app client cannot be used.
- `docs/windows-hello-field-test.md` — the checklist, including what the test
  cannot prove: Windows verifies rather than signs, the ceremony runs through
  Edge's WebAuthn, and `basic` is the only tier a self-asserted credential
  reaches.
- `scripts/mint_apple_secret.py`, with `mint` and `check`.
- `*.p8` in `.gitignore`, and a test that fails if one lands in the tree
  anyway.

## [0.24.0] — 2026-08-01

Nine rounds, one question: **when a stranger does reach the thing built for
them, can they read what it says?** The last release opened the doors. This
one is what is written on the other side of them, and every finding is the
same shape a layer further in — a surface localized while the sentence it
answers with was not.

### The answers were in one language while the screen was in ten

`qrme/i18n.py` takes a `profile_id`. The accountless screen's reader has
none, so it could not have answered them even if something had asked. A
visitor in Osaka got a Japanese page, pasted in a piece of text, pressed a
Japanese button, and was told in English `no stamped work shares any wording
with this text` — the answer to the only question they came with. The
restriction notice after opening an objection, the consistency guarantee, the
synthetic-media disclosure, the recovery method and every refusal were the
same.

`negotiate()` plus thirteen sentences in ten languages, in a table separate
from the per-profile machinery, hand-translated rather than machine-
translated. Four public routes read the header; `refusals_in` translates what
they raise, narrowly, so an owner's refusal is untouched.

**The state words are deliberately not translated.** The first version of
this round translated `status` too, and driving it caught the cost:
`Contest.tsx` branches on `status === "open"` to show the card a subject or
an estate uses to end a case immediately, so a Japanese browser would have
made that control vanish from a signed-in screen. What a person reads is
translated; what a client compares is not.

### Twenty-five strings on the public screen, five in the ledger

`public_untranslated.txt` listed five sentence fragments and called them the
hard remainder. They were what a regex over TSX happened to be able to see:
`>([^<>{}]+)<` excludes braces, so every sentence wrapping an interpolated
value was skipped whole and the five reported were their brace-free scraps.
TypeScript generics look like tags to that pattern, which is why it had grown
a rule dropping lines with `=`, `;` or `=>` — and that rule then swallowed the
mark pane's entire explanatory paragraph.

`app/scripts/jsx-text.mjs` asks TypeScript's own parser for `JsxText` nodes
instead. Twelve new keys in ten languages, and `fill()` so a sentence with
named holes stays one translatable unit rather than three fragments a
translator cannot reorder.

### The pre-session surface is two screens

That guard measured `Public.tsx` alone and reported the pre-session surface
clean. `App.tsx` renders two things before a profile exists, and the other is
the one everybody meets first: `Onboarding.tsx` carries thirty-seven English
strings while already calling `visitorLang()` three times, on the links
pointing at the accountless screen. The round that localized the door
localized the sign to the door and stopped. Recorded and ratcheted rather
than half-translated — a partly-translated sign-up form reads as broken
software at the moment somebody is deciding whether to trust it with their
email.

### Three phones with no way to ask

Every native shell's `language` is read from the profile's stored setting, so
the one screen whose reader has no profile is the one screen where that value
is guaranteed to be the default. `WithoutAnAccountView.swift` contains no
`L10n.` calls beside a table with ten languages in it, and there was nothing
to pass it. iOS, Android and Windows now resolve a device language —
`Locale.preferredLanguages`, the system locale list, `CurrentUICulture` —
region dropped, English as the fallback rather than a guess. The screens'
strings are recorded, all three or none.

### One header, three products

QRME, JIM and PDI each grew a `negotiate()` in a different round. Compared
side by side for the first time, two rows disagreed: `ar;q=0` and `de;q=abc`.
`q=0` means *not acceptable*, so a browser sending `ar;q=0` is refusing
Arabic. A conformance table now lives byte-identically in all three
repositories.

### Fixed

- `POST /objections` and `GET /objections/{id}` read `Accept-Language`; the
  409 for a terminated profile and the 404s a stranger can hit are translated.
- `POST /watermarks/recover` and `GET /profiles/{id}/embodiment-consistency`
  answer in the reader's language.
- `test_the_promise_and_the_door_are_on_the_same_surface` could no longer see
  a claim made through a lookup key. Injecting a localized no-account claim
  into a gated screen passed against the shipped guard; both it and its
  positive control now resolve text through `l10n.ts`.

## [0.23.0] — 2026-08-01

Ten rounds, and one question asked in three products: **can the person this
was built for actually reach it?** Every finding below is a route the backend
deliberately made public, or a capability a screen deliberately offered, that
the client then put behind something its intended user does not have.

### A public route behind a private door

`governance.open_objection` says what it is in its own first line — *"public:
the objecting party need not own an account"* — and `Contest.tsx` said it in
the copy a person reads: *"You do not need an account. Objecting to a profile
should not require joining the platform that is hosting it."*

That sentence was printed on a tab nobody without an account could open.
`App.tsx` returned `<Onboarding />` for the entire window while
`session.profileId` was unset, so all forty-six tabs sat behind a sign-up, and
the three native shells did the same. The person the route exists for is by
construction the one who cannot reach it: they have found a synthetic profile
of themselves, they have no QRME account, and the product's answer was that
they should make one with the platform depicting them first.

A **Without an account** surface now opens before the gate on all four
clients, carrying the objection form, the objection-status lookup, and the
mark check. The console answers `#object` and `#mark` in the URL, so a takedown
notice or a moderation reply can point at the form rather than at a sign-up
page. Nothing on it sends a credential; the audit trail, which quotes the
objector's reason, stays gated where it was.

The guard's own last check found a third route nobody had looked for.
`embodiment-consistency` is public in its own words — *"anyone meeting the
profile through any form can verify it is the same personality"* — and the only
screen calling it was the owner's Workshop, which printed that sentence in a
card only the owner can see. It is now the public surface's third pane.

### A binding is not a door — for the native shells too

`test_a_binding_is_not_a_door.py` existed because `clientpaths.doorless` counts
call sites: a function written in `api.ts` and wired to no screen takes its
route off the backlog whether or not anything calls it. It checked one client
of four. `ApiClient.swift`, `ApiClient.kt` and `ApiClient.cs` are files of the
same kind with the same property, and nothing had ever looked at them.

Eight unused bindings, three of them a capability with no door — and all three
the same shape, a shell carrying the act that **creates** a standing power and
not the act that **ends** it. `SignatureView` listed signing credentials and
could not revoke one; a credential that signs documents as you, on a device you
may no longer hold. Both are wired, with confirmations that say what the act
does and does not undo.

### The stranger's language

Every localization path in this product takes a profile id, which is exactly
what the reader of the public surface does not have. `navigator.languages` is
the only signal those visitors carry and nothing read it, so the screen built
for people with no account was also the screen with no language.

`visitorLang()` negotiates it — region dropped, anything unrecognised falling
back to English rather than guessing — and the action-carrying strings are
translated across all ten languages. The longer explanatory paragraphs are not,
yet: they are listed in `tests/public_untranslated.txt`, checked in both
directions and ratcheted, so what is left in English is a decision on the
record rather than an oversight.

### The audit's recurring shape, named

Seven times now a checker has answered a question slightly to the left of the
one that matters, and passed:

| asked | mattered |
|---|---|
| some client reaches this route | *this* client reaches it |
| the console reaches it | a phone reaches it |
| a binding exists | a screen calls it |
| the same, three surfaces over | |
| the name appears in the file | it was not the declaration itself |
| a shell calls the public route | somebody without an account can |
| the console reaches the recipient's route | the recipient can |

Every one was true. None was the question. Three of the seven were mistakes in
guards written to catch the previous one.

### Fixed

- `SignatureView` on iOS can revoke a signing credential it enrolled.
- The console's `Contest` and `Workshop` copy now points at the surface that
  keeps its promise instead of asserting something its own surface cannot
  deliver.
- Screen 184 joins the gallery with a lesson and dock keywords for somebody
  who types *"I don't have an account"*.

### Known gap

The six releases from 0.19.0 to 0.22.0 had shipped without rows in the README
release table. They are written in now, from the CHANGELOG sections that
already described them.

## [0.22.0] — 2026-07-31

### The only post that actually leaves was the one going out unmarked

`POST /social/{cid}/publish` writes a profile's words to a platform QRME does
not run. It is the single route in this product where synthetic media genuinely
**leaves the building** — and it stored that post with `watermark_id` NULL,
while `compose_post`, the in-app equivalent, stamped a credential every time.

`compose_post` even says why, in a sentence that describes the *other* route
more exactly than the one it is written above: *a public post is synthetic
media leaving the platform: it carries a verifiable synthetic-media credential
from the moment it exists.* So the only posts going out unmarked were the ones
actually going out.

The same function ran `profile["maturity"]` as its moderation filter, where
`compose_post` forces `strict` with the note *public posts face the widest
audience: always the strict filter*. A profile set to `open` was therefore held
to the loosest rule on the way to an audience QRME cannot see, and the
strictest one when posting where it can. Both now match the in-app path, and
`publish` hands the credential back so whatever posts it onward carries the
disclosure rather than looking it up.

### The audit reaches zero

**Screen 183** doors the last eighteen routes — feedback, mod registries,
connected apps, excursions, the steering hub, playing alongside somebody, and
both directions of a social connection — and wires the eleven remaining
`api.ts` bindings that nothing called. Nine of those were the same question
about different ids, so they are one lookup control rather than nine buttons
nobody would find.

| | at the start of this release | now |
|---|---|---|
| Console-doorless routes | 64 | **0** |
| `api.ts` bindings nothing calls | 25 | **0** |

Both record files are now **empty rather than short**, and the tests that read
them assert emptiness.

`test_the_union_is_still_wider_than_the_console` had to change with it. It
asserted the union backlog was *strictly* smaller than the console's, on the
reasoning that if the two ever agreed the likelier cause was a broken native
extractor than a console that had caught up. That was sound while catching up
was hypothetical. It now asserts the invariant that survives — the union can
never exceed the console's, since the console is one of its own surfaces — and
the liveness check it was doubling for lives in
`test_each_native_shell_is_still_being_read`, which counts call sites per shell
and would actually notice.


### Anybody could take away the name a profile answers to

`PUT /profiles/{id}/handle` took **no credential of any kind** — no `request`
parameter, no `require_owner`, nothing. And the damage is not that a stranger
could give a profile a second name to be found by. Claiming a handle runs

```sql
DELETE FROM handles WHERE profile_id=?
```

first, because that is how *changing* your handle works. So anybody could take
`@rosa` away from Rosa: the handle she had published stopped resolving, the one
the stranger chose resolved to her profile instead, and every printed
reference, shared link and beacon that named her went dead at once — with the
name she now answered to picked by whoever did it.

The three beacon routes sitting **immediately below this one in the same file**
were given exactly this check in an earlier pass, and `place_beacon` states the
reason in words that fit here without changing a syllable: *it was anybody's,
which meant a stranger could print stickers pointing at somebody else's
profile, in places its owner never chose and cannot see.* That pass hardened
placing, listing and picking up, and walked past the handle route above them.

iOS, Android and Windows all claimed handles with no credential, and all three
now send the owner's token.

**Screen 182** is the door the round built: which language a profile speaks —
not a display setting, since the persona *writes* in it natively on every
surface rather than translating afterwards — translating something it ran
across, claiming the handle, and composing a post.

Console-doorless routes **23 → 18**.


### A post the filter refused was published by the route that lists what was published

Public posts run through the **strict** moderation filter, because a public
post faces the widest audience there is. When it holds one — or when the owner
has set the profile to approve its own posts by hand — `compose_post` stores it
`pending` and is deliberate about what it hands back:

```python
"content": content if status == "approved" else None
```

`content: None`, **to the owner who just asked for it**.

Fourteen lines further down, `list_posts` returned `{**dict(r)}` — every column
of every row, whatever its status — to anybody, with no token at all. So the
hold was enforced against the author and against nobody else: a post the strict
filter refused was readable in full by a stranger, from the route whose entire
job is to list what a profile has *published*, carrying `flag_reason` with it —
the sentence naming the rule the text broke.

An approved post is public. A held one is a queue, and now only its owner sees
it. **Screen 181** shows the two apart.

The same screen opens two surfaces that were already right and are now pinned:
the **designation cannot be designed away** (ask for the label "Rosa" and the
line comes back "✦ AI · Rosa"), and an owner **cannot resolve an objection
against their own profile** — re-attesting the basis is the only move they
have, because an owner who could dismiss it would be deciding their own case.

Console-doorless routes **28 → 23**.


### An id was read as a credential, in the one feature built on consent

`/connections` is anonymous matchmaking between two people with no profile
involved: each sees the alias the other chose, never a name or an id.
Anonymity is the whole feature. It had no door in this console, and building
one — **screen 180** — found that it had no *authentication* either. Not weak
authentication: none.

Every route read `interactor_id` out of the request body or query string and
checked only that it named one of the two participants. Nothing checked that
the caller **was** that person, and no route asked for a token at all. Two
public ids were enough to:

- **join the queue as somebody else**, and be matched with a stranger under
  their name — and on the `rated` tier, borrow a verified adult's id straight
  past the age check, which is the one gate this feature cannot afford to lose;
- **send messages as either party**, stored under their id and shown to the
  other person as theirs;
- **read the pair's entire conversation as either party**, including the
  `blocked` messages the route deliberately withholds for their sender's eyes
  alone — a rule worth nothing while anyone may claim to be the sender;
- **end it.**

Ending was the worst, because it did not even need the ids. The check read
`if ender: _participant(connection, ender)` over an *optional* body and an
*optional* query parameter, so supplying neither skipped it entirely: a bare
`POST` with no id and no credential ended a stranger's conversation, and
returned any wearable microphone lent inside it.

This is the room defect from earlier in this same release, in the one feature
whose premise is consent — and `community._require_in_room` had already
settled the argument in the same words. An id is a claim; the token is the
answer.

The ids still ride in the body and the query string and are ignored: three
shipped native clients send them, and a 422 on upgrade is a worse answer than
not believing them. **iOS, Android and Windows all now carry the interactor's
token** on all four calls.

Console-doorless routes **33 → 28**.


### A refused request left a room behind

`Desk` is the host's console — open a desk, set your presence, point the
camera, read who rang, bring a guest up — and every route it calls is
owner-only. There was no **visitor's** side at all, and the visitor is the
person the feature is for: somebody standing in front of an empty chair with a
sign on it saying to ring the bell. Seven routes, plus `askToComeUp`, which had
sat in `api.ts` for months with no screen calling it. **Screen 179** is that
side, together with leaving a profile somewhere.

Building it found three defects, and the third was found by the compiler after
the first two were fixed.

- **A `401` that wrote anyway.** Joining as a `guest` needs an account — the
  host is deciding about a person, not an anonymous request — and the route
  said so. It also called `desks.join` *first*, which mints the stream's room
  on first arrival (a real row, committed), and asked who was calling
  afterwards. So a request we were turning away left a room behind it.
  `ask_to_come_up`, **the very next route in the same file**, already had the
  order right: gate, identify, then write.

- **Two fields exactly swapped, and a third stringified.** `DeskOverlay` was
  written from the route's name rather than its answer. `waiting` is a *count*
  and was typed as a list, so `waiting.length` printed **“undefined waiting”**.
  `comments` is a *list* and was typed as a count, so `{overlay.comments}`
  rendered nothing while empty and would have thrown *Objects are not valid as
  a React child* the moment anybody spoke on the stream. And `style` is a
  layout object, so *laid out as a `${style}`* printed `[object Object]`.
  `api.ts` states the rule for itself twenty lines below, over the marketplace
  block: *every shape below was read off a running server rather than off the
  route signatures.*

- **A field that was never on the wire.** With the types corrected, the
  compiler found `DeskGuest.state` — the real field is `status`, and an index
  signature had made the wrong name typecheck and read `undefined` forever. The
  status label never rendered, and the guard
  `g.state !== "accepted" && g.state !== "declined"` was **always true**: the
  host was offered *Let them up* for people already up, and *Not now* for
  people already turned away.

Console-doorless routes **40 → 33**; unused bindings **12 → 11**.

## [0.21.0] — 2026-07-31

Four door-audit rounds run back to back. Each built a console door for a
backend feature that had none, and in three of the four, building the door
found a defect in the thing it was a door to — with the argument against
the defect already written down elsewhere in the same repository.

### A missing field was reported as a broken signature

Seven signature routes had no console door: enrol a credential, revoke one,
read the policy, mint an envelope, sign it, and check a package handed over
from outside. The console could *list* credentials and reproof one and could
do nothing else — `Referrals` had already written the gap down as a sentence,
**“None enrolled. The ceremony can enrol one.”**, under a heading with no
button behind it. The ceremony page existed, `openCeremony` existed, and it
posts the raw assertion back to its host by `postMessage`. Nothing in the
console was listening, so the message went nowhere. **Screen 178** is that
listener and the two calls on the far side of it.

Building it found the defect, in the one place this feature cannot afford one.

- **`verify_package` blamed the cryptography for a missing field.** It runs
  eight checks in order, and *any* exception anywhere in that sequence ran
  `checks["signature"] = False` and appended `str(exc)`. So a package missing
  `display_text` — trimmed in transit, or a summary forwarded in place of the
  package — came back saying **the signature is invalid**, when the ECDSA
  verification several lines earlier had passed. That is the strongest and
  most damaging thing this endpoint can say, it was false, and the reason
  offered was `'display_text'`: a Python `KeyError` repr sitting beside two
  notes written as full sentences. A counterparty reading it would conclude
  they had been handed a forgery.

  The argument was **already written down in the same feature**. The router
  says of its own refusals: *the message is the reason, because a signature
  that is turned away without one is impossible to fix from the outside.* A
  counterparty is exactly the outside.

Two rules now hold. A check that already passed is never retroactively failed
by a later one breaking — only the check that actually broke is reported
broken. And a check that never *ran* is not a pass: `VERIFICATION_CHECKS`
names all eight, `valid` is false whenever any is absent, and the notes say
which and why in sentences. The screen renders unrun as unrun rather than as
a tick, because a fixed backend behind a screen that drew absent as passing
would put the same lie back on the glass.

Console-doorless routes: **47 → 40**.

### A policy you could publish and nobody could take up

`Delegate` built the owner's half of delegation — mint a revocable grant, say
which phases may run unattended, start and advance and cancel a workflow. All
of it about *my profile working for me*. But delegation is not for that. It
exists for the person on the **other** end of a conversation: somebody already
talking to a profile hands it a job, inside the limits its owner set. That half
had four bindings in `api.ts` and no screen calling any of them, so the policy
was publishable and unusable from the console that published it.

Driven end to end against a running backend, **every rule was already right** —
the offer is public and lists phases only, never the grant id, because which
source items the owner scoped is the owner's business; enabling `research` is
refused without a grant, and the refusal names what it protects rather than the
rule it enforces; starting one requires an existing conversation; reading or
advancing one is `403` to an outsider, `401` to nobody at all, and `200` to the
delegate *and* the owner, who are entitled to it for different reasons.

That is worth recording plainly. This is the first round in a while with no
defect in it, and the failure it did find is the one the door audit exists to
name: a feature finished and unreachable. `tests/test_the_other_end_of_the_policy.py`
pins the shape so it stays that way, and **screen 174's** second half now calls
all four bindings with the interactor's own token.

- **`api.health` deleted rather than doored.** It hit the same route as
  `healthInfo`, threw the body away and returned a boolean. Nothing called it,
  and a binding that discards the answer is worse than none — the next person
  wanting a health check would have found it and lost the version with it. Not
  every unused binding wants a screen; the backlog shrinks both ways.

Unused bindings: **17 → 12**.

### A room id was the only thing a room asked for

`Rooms` could open one and not enter it: the console had no way to read a
transcript, say anything, let the profiles take a turn, or lend them a
microphone. Six routes, four behind `api.ts` bindings that no screen called.
Building the way in — **screen 175, "Inside a room"** — found two defects
worth more than the screen.

- **Anybody could speak as anybody.** `POST /rooms/{id}/messages` read the
  speaker from `sender_id` **in the body** and checked only that the id named
  a participant, never that the caller *was* that person. A stranger's token
  plus a named participant's id gave a `201`, a message stored under her name,
  a transcript reading `from: Ada`, and every profile in the room answering as
  though she had spoken.
- **The transcript asked for nothing at all.** Not a wrong token — no token.
  The whole conversation was readable by anyone holding the room id.
- **`POST /rooms/{id}/advance` asked for nothing either**, so a stranger could
  run somebody else's room forward indefinitely against their model key.

A room id is not a secret; it rides in beacons and on printed QR stickers,
which is the point of them. That sentence was **already written down two
routes away**, on `GET /rooms/{id}/mic`, guarding the narrower fact of who is
wearing a live microphone. All three now go through the same
`_require_in_room`.

`sender_id` stays on the request model and is ignored — three shipped native
clients send it, and a 422 on upgrade is a worse answer than not believing it.

### The body market, and what you bolt onto a body

Choosing a body is shopping, and the catalogue listed nine models. It now
lists **36 from 25 makers** across humanoids, home robots, quadrupeds and
vacuums — including the ones nobody can buy yet, because *what exists* is the
question an owner is actually asking.

- Every row carries `availability`: `shipping`, `preorder` or `announced`.
- **An announced body is listed and refused.** Binding one answers `409`
  naming its status, not `404` — saying *unknown robot model* about a machine
  its maker has publicly shown would be false, and every command to a body
  nobody has would go nowhere. Listing it and refusing it are two halves of
  the same honesty.
- `catalog()` groups by maker, kind **and** availability, because three
  clients would otherwise group three ways.
- `REVIEWED` dates the snapshot and `test_the_body_market.py` fails when it
  falls a year behind the newest release. `announced` is a claim about the
  future; a stale one reads as current, which is the same failure as an
  exemption list nobody looks at.
- `quadruped` is a new kind, with its own command allowlist.

**The connections bracket** — screen 176 — is the other half: what a body is
taught and what it is plugged into. A **task pack** turns each of its tasks
into a commandable verb, capability-checked against the catalogue so a vacuum
is never taught to fetch; a **connector** is a service the profile's agents
can collect from, act on or produce into. A pack is fitted to a particular
machine rather than to the profile, which is the distinction that decides
where it lands.

Console backlog **53 → 47**.

### The native shells learned to send a credential

Gating the routes broke iOS, Android and Windows, none of which sent a token
on any room route. All three now do. **Windows had no interactor token at
all** — `AppState` kept the id and threw the token away, so the shell could
hold an identity and never act as it, which is part of why these routes had to
be open for its Community page to work.

Unused `api.ts` bindings **21 → 17**; console backlog **55 → 53**.

## [0.20.1] — 2026-07-31

Two rounds, and the second was found by the first. The audit round below built
a guard that names every `api.ts` binding no screen calls; paying down the
first of them turned up a marketplace sale that was credited to a key nothing
reads.

### A sale credited to a key nothing reads

Paying down the first of the 25 unused `api.ts` bindings found it. `PUT /marketplace/listings/{id}/offer`
recorded the seller as the token's subject — and an **owner token's subject is
a profile, not an account**, while `GET /profiles/{id}/earnings` resolves the
profile to its `owner_id` before querying the ledger.

So a seller who priced a listing while signed in as their profile's owner got
`200` on the offer, `201` on the buyer's purchase with a real `ledger_entry`
and the sentence *the sale is recorded on the seller's statement* — and an
empty statement. The money was written under a key nothing queries, and every
response along the way said it had gone through.

It survived because nobody could do it: `api.setOffer` existed and no screen
called it, and the phone prices listings as an *interactor*, whose subject id
already is the account. `commerce.beneficiary_of` has resolved a profile to
its owner for gifts since gifts existed — the same rule, never applied to the
other half of the money.

### Fixed

- `_earner()` resolves an owner token to its account for **every** seller-side
  route: pricing, withdrawing, and `GET /marketplace/sales`. Moving what is
  stored had to move what is compared, or a seller locks themselves out of
  their own offer.
- `api.placeListing` and `api.unplaceListing` took no token, which was
  harmless only while nothing called them — those routes gained claimant
  gating this round, so a tokenless call would now be a 401.

### Added

- **"What you are owed" gains the price and the place.** `setOffer`,
  `withdrawOffer`, `placeListing`, `unplaceListing` — four of the 25 unused
  bindings, wired to the screen that should have carried them. Unused
  bindings: **25 → 21**.


### The union hid a surface

The doorless backlog reached zero in 0.20.0, and it was measuring the wrong
thing. `clientpaths.doorless` unions the console
with the iOS, Android and Windows shells, so a route only the phone calls
counts as doored — the number went to zero while a desktop owner could not
reach **64 routes**. The guard was answering *some client can reach this*,
which was true, in place of *this client can reach this*, which was not.

That is the same shape as every defect this audit has produced: a checker
answering a question slightly to the left of the one that matters, and
passing.

### Added

- **`test_the_console_is_a_client_too.py`** — the console's own backlog, in
  `console_doorless.txt`, checked in both directions and ratcheted so it
  cannot grow past where it started. The union guard stays; a route no client
  anywhere calls is still worse. A phone-only capability is a legitimate
  design choice, which is what the snapshot is for: deferring one takes a
  deliberate edit and shows up in a diff.
- **`test_a_binding_is_not_a_door.py`** — a function in `api.ts` that no
  screen calls is not a door, and `doorless` counts it as one. The docstring
  on `doorless` had said this was "a discipline rather than something the
  test can enforce"; it turned out to be enforceable in about twenty lines,
  and found **25 bindings nothing calls**. *The test cannot check this* is a
  claim worth testing.
- **Screen 174, "What you are owed"** — the seller's side of the counter,
  which the console did not have. An owner could be bought from and could not
  post a licence offer, see who held one, revoke it, read what any of it
  earned, or ask to be paid. Nine routes, all owner-side, all present on the
  phone's Earn tab.

### Fixed

- **A statement added two currencies together.** A creator pricing one profile
  in dollars and another in yen got back `accrued: 200` for ¥100 and $100,
  labelled with whichever sale was newest — and all three native shells render
  that figure with a currency symbol in front of it. Totals are now kept per
  currency (`by_currency`, `currencies`, and a `mixed` flag on the headline),
  the settlement currency is chosen deterministically rather than by recency,
  and a payout settles **one** currency and reports what is `remaining`. An
  account with one currency reads exactly as it did.
- **Anyone could delete anyone's marketplace listing.** `DELETE
  /marketplace/listings/{id}` asked for no credential, while `DELETE
  /marketplace/listings/{id}/offer` — which destroys strictly less — answered
  the same stranger "not your offer". A listing is now claimed by whoever
  staked something on it: the creator recorded in `listing_claims`, the seller
  on its offer, or the owner of the profile it advertises. Creating one still
  needs no token, and a listing with no claimant at all is still anybody's to
  clear away. The place routes are gated the same way, because moving somebody
  else's listing to another city is a quieter version of taking it down.
- **`clientpaths.py` was not byte-identical across the three repositories**,
  though it says it is. JIM and PDI never received the `fetch`, `window.open`,
  `<img src>` and `<a href>` call forms from the previous round, so their
  backlogs counted doors that existed. Restored, and JIM's backlog dropped
  73 → 69 as a result.

## [0.20.0] — 2026-07-31

**The doorless backlog reached zero.** It began at 116 routes the backend
served that no client could reach, and this release closes the last 42. Every
one got a door in the console; six new screens (**168–173**) carry them.

A route with no door is the quieter of the two integration failures. A client
asking for a route that does not exist produces a 404 somebody eventually
reports; a route no client asks for produces nothing at all — the code is
present, its tests pass, the changelog says it shipped, and the capability is
simply unreachable.

**What the exercise produced was not doors. It was defects**, and almost none
of them were visible to the typecheck:

- **Three routes took no token at all.** `POST /packs` let anybody publish to
  the marketplace, name any string as the publisher, and name *any account* as
  the one sales accrue to. `POST /profiles/{id}/interactions/{id}/feedback` let
  anybody rate in somebody else's name — and since an `up` rating is the
  trigger for cloud contribution, an unauthenticated caller could push a
  stranger's conversation out of the deployment. `GET
  /profiles/{id}/engagement/{id}` exposed how often a named person talks to a
  profile, across how many sessions, and whether they liked it. In each case
  the argument against it was **already written down elsewhere in this
  repository** — `commerce.beneficiary_of` on gifts, the beacon list on
  physical places — and these three quietly went the other way.
- **A licence was sold to somebody who could not use it.** A licence permitting
  derivatives went to a buyer under 18: 201, `can_derive: true`, and the fee
  credited to the seller at sale time — then a 403 on the only thing the
  licence exists for. The adult check now runs at acquire, where the money
  moves, rather than at delivery.
- **A link that resolved against the wrong origin.** Desk beacons returned a
  relative `scan_url` while the profile beacons next door returned an absolute
  one, so the console's scan link resolved against the console's own origin —
  dead in every build where the console is not served by the API, which is
  every packaged build.
- **An honesty note served to nobody.** A desk's view frame — the picture
  carrying *a sample view; this deployment has no camera on this desk, so the
  frame is not live and is not claimed to be* — was never rendered anywhere in
  the console.

### The audit could not see two kinds of request

An `<img src>` is a fetch. An `<a href>` is a fetch. Neither passes through the
API client on the way, and the route extractor could see neither — so
`/b/{id}` and `/beacons/{id}/qr.svg` sat on the backlog while the placements
screen had been rendering both since it was written. That is the
false-positive failure the nested-template bug produced in 0.19.1, arriving
from a different direction: a guard that invents work fails more quietly than
one that misses some, because a miss is found by the bug it let through while
an invention is found only by somebody going to do the work and finding it
done.

Worse, **the exemption list had absorbed three of them**, each marked "rendered
in an `<img src>`, not fetched by the API client" — an exemption made out of a
blind spot, which is exactly the shape that stops anybody asking. One of the
three turned out to have no door at all. The list now holds to one rule:
exempt a path because nothing should ever call it, never because the audit
cannot see the call. Four entries survive, including the OAuth callbacks, whose
address is built by the API and handed to the provider — a `redirect_uri` a
client could choose is one an attacker could choose.

### Recorded rather than corrected

Five findings are pinned as observed behaviour instead of changed, because each
is a decision to make deliberately rather than while building a screen, and a
test asserting they already agree would hide the question:

- a **gift** reads its beneficiary from the subject while a **subscription**
  takes one from the request body;
- the contribution **preview is computed whether or not you are opted in**, so
  the console changes the heading rather than the content;
- the quiet-hours window is half-open, so a start equal to its end covers
  **nothing** — 9-to-9, read as *all day*, protects nobody. Changing the
  arithmetic would silently redefine every window already stored;
- three deletes give three different answers to *there was nothing there*: a
  missing comment 404s, an unlisted profile 404s, and unfriending a stranger
  answers **200** with `removed: false`;
- `deleted_at_gateway` is true *vacuously* when nothing ever left.

### The guard, now that the backlog is empty

`doorless_routes.txt` is empty and a new assertion says so directly, separate
from the record comparison so the message is plain when it goes: *the number is
no longer zero*, rather than *strike this line*. Deferring a route legitimately
means editing that test as well as the file, which is the right amount of
friction for a decision that used to be made by accident.

Its guard-on-guard changed with it. Asserting the snapshot was non-empty no
longer means anything, so the liveness check moved to where the meaning lives:
**the console must still be producing call sites.** If the extractor broke
entirely every route would read as doorless, loudly; if it were quietly
narrowed to a handful of forms, that count is what would notice.

Seven new test files, 154 tests, 23 injection-verified. Suite: **1807 passing**.

## [0.19.1] — 2026-07-30

**A feature can no longer ship with nothing drawn.** The gallery tests all
check screens against the README — a reference with no file, a file with no
reference, a gap in the numbering. Every one of them starts from the screens,
and none asks the opposite question: does this surface have a screen at all?
So a feature could ship with nothing drawn, nothing taught and nothing for the
in-app helper to point at, and the suite stayed green.

That had happened three times, most recently to 0.19.0's own error-reporting
card and its first-run notice — undrawn while the release notes described them
at length. It is the same shape of flaw found twice before in this suite: a
guard that only walks the relation in the direction where the answers already
exist, like the doorless audit before it counted call sites, or the redaction
check that read a shrinking snapshot and would have gone vacuous the day it
emptied.

`ui_screens.txt` is the missing direction. Every console surface now carries a
screen number, `undrawn`, or `unaudited`, so a surface nobody has classified
fails the suite in the round that introduces it. The mapping is declared rather
than inferred on purpose: matching component names against screen titles
resolved only ten of twenty-four, because titles are written for the person
using the app and component names for the person editing it, and guessing the
rest would have produced a mapping that looked complete and was not.

Both backlogs are ratcheted against a ceiling each repository declares for
itself — one hardcoded number would be the largest of the three and leave the
other two slack to grow into. A ceiling left high after the backlog falls fails
too, because a ratchet that stops ratcheting re-opens the ground it gained.
Verified by injecting five failures, including the one that gives the check its
teeth: silencing it by writing `undrawn` fails the ratchet.

**And the two surfaces it caught are drawn.** Screens **150 What Went Wrong** and **151 Before Anything Is Sent** join the gallery, each
with a lesson and with phrasings that reach it by asking the helper in the
words somebody actually types when something has broken — "it failed",
"something broke", "stop sending", "opt out". The card draws an operation and a
status and nothing else, because that is all the log holds; drawing a message
there would depict a product that does not exist.

## [0.19.0] — 2026-07-30

**The apps now record what fails, without recording anything private.** Every
failed request passes through one function in the console, so one call there
catches the lot — but the obvious version of this feature would have quietly
undone what every other screen promises.

The backends put user input straight into their error messages: *no device
called 'Pixel Buds' on this account*, *unknown site 'knee'*, *unknown language
'xx'*. Those are good messages for the person reading them and bad things to
keep. So the message is shown to the user, who owns it, and is **never
written to the log**. The same reasoning rules out the path:
`/profiles/prf_0de08e794ed0/chat` identifies a person, `POST /profiles/{id}/chat`
identifies a bug, and only the second is recorded.

What a report contains is the operation, the status, the app version, platform
and language, a count and a date — no ids, no messages, no bodies, no
timestamps finer than a day. The redaction happens on the way *in*, so there is
no moment at which the buffer holds something that would have to be scrubbed
later.

**Sent once at launch, if the build has anywhere to send.** A Settings card
shows the exact payload — the same object the copy button produces and the
sender posts, from one function, so the preview cannot drift from what leaves.
The address is compiled in at build time and unset by default, which is a
stronger "off" than a flag: with no address there is nothing for a later
mistake to switch on. Where one is set, the console posts alongside the update
check and swallows every failure, because a diagnostic that can delay a launch
has stopped being worth having. Anyone who would rather it did not happen can
turn it off on the same card.

Counts go as **deltas** — each row remembers how much of itself has been
reported, so reopening the app twenty times does not turn one broken screen
into twenty. A failed send moves nothing and the next launch tries again.

The gateway that receives them, `cloudgw`, accepts exactly five top-level keys
and five per problem and **422s on anything else**: an unknown field, a
`platform` string long enough to hide a sentence, a `day` carrying a time of
day, or a path with an unredacted id still in it. It could redact that path
itself — the pattern is right there — but then a build whose redaction had
broken would keep working and nobody would learn that every report from those
users had been arriving with a profile id in it. What survives is less than
what arrives: reports fold into counters keyed by product, version, platform,
operation and status, locale is validated and then dropped, and nothing records
that a particular install sent anything. Reading that aggregate needs a
narrower permission than writing to it, because the posting token ships inside
every installer and is public the moment somebody unzips one.

**Nothing goes before you have been asked.** Sending is opt-*out*, which only
means something if the opting-out can happen before the first report rather
than being discovered afterwards in a settings panel nobody opened. So the
sender refuses until a first-run notice has been answered — and that notice
shows the actual payload rather than describing it, from the same function
that posts it, so it cannot go stale while still looking honest. Both answers
are offered, the answer is remembered, and the switch on the Settings card is
that same answer, changeable whenever. It only appears where a build has a
collector at all: interrupting somebody to explain a thing that cannot happen
teaches them these notices are noise.

Thirty-nine tests hold the shape in place — that `recordProblem` has no
parameter a message could arrive through, that the stored record has no field
one could sit in, that the wire shape and the gateway's whitelist still agree,
that the redaction catches short ids as well as long ones, and that it never
eats a real route name. Four leaks were injected to prove they fail: a `detail`
parameter on the recorder, the redaction narrowed back to six-hex-character
ids, a `detail` field added to the outgoing report, and the send routed back
through the recording client so it would log its own delivery attempts. All
four were caught — and the third exposed a real gap while doing it, since that
check only ran in the repo shipping the gateway, which is the one repo where a
leak would matter least.

One more bug found by checking rather than reasoning: every pattern in the
gateway's validator was anchored with `$`, which in Python matches *before* a
trailing newline as well as at the end of a string. So `Win32\n` and
`GET /health\n` were accepted by a validator whose own error message said
newlines were not allowed. Harmless in itself — one invisible character — but a
validator that is wrong about its own rule is not one to keep trusting. All of
them now end `\Z`, with a test for the case, because the next person writing a
pattern here will reach for `$` too.

One more bug, and this one came from being careless rather than clever. While
driving the client against a live gateway, a scratch file of unrelated JSON
got reused as the counter path. The aggregate loaded it — it parsed, after all
— and `GET /v1/problems` then died with a 500 sorting values that had no
count. Unparseable JSON had been handled from the start; *parseable* JSON of
the wrong shape had not, which is the likelier accident: a half-written file
that happens to close its braces, an older format, an operator pointing
`CLOUDGW_PROBLEMS_PATH` at something already there. Rows are now checked
individually on load, so a bad one is dropped and the good ones beside it
survive. A test written from imagination would have reached for
`"{ this is not json"` again and stayed green.

And the one that would have made all of the above pointless: the gateway had
**no CORS at all**. The sender posts JSON with an `authorization` header, which
makes it a non-simple request — the browser sends `OPTIONS` first and refuses
the real call unless that is answered. Every preflight would have been 405'd,
every report would have failed, and because the sender swallows failures the
whole feature would have been dead in the field with nothing to show for it.
Found by asking what an Electron renderer's origin actually *is*: `null`, since
it loads the console from `file://` — which is also why no origin allowlist
could have been written. Answered from any origin with credentials off, which
costs nothing here because every endpoint needs a bearer presented explicitly
and there is no ambient authority for a hostile page to borrow. The preflight
test was checked by deleting the middleware and watching it fail.


**A desk you can actually staff.** The desk is the one surface in QRME whose
promise is a *person* — a real tradesperson, attested by somebody, reachable
now — and none of it was reachable from a client. You could not open a desk,
say whether anybody was behind it, answer the bell, or let a visitor come up.

The new **Desk** screen covers the counter end to end: opening one with the
attestation it rests on, setting presence, answering rings, accepting or
declining the people asking to come up, the stream overlay, and beacons — the
desk as a sticker somebody scans in the street.

Four things are stated the way the backend states them rather than the way a
console would guess. **A desk is not a profile**: the API answers `desk_id` and
`desk_token`, and holding a desk token is what makes you the desk rather than a
visitor to it — so the token lives in the screen rather than the shared session,
because signing in as an owner does not make you the counter. **Away and closed
are different promises**: one says come back, the other says the counter is
shut, and the desk gets to make either. **The attestation is shown to its own
keeper**, `burned` included, because a withdrawn claim is not something to
learn about from a visitor. And **picking up a beacon retires it** — the sticker
on the wall stops working, which is the point of picking it up.

The desk's view (`view.webp`) and a beacon's QR are now excluded as
browser-facing in `NOT_A_CLIENT_CALL`, alongside the pair and medical-ID codes:
they are rendered in an `<img src>`, not fetched by the API client, and counting
them as doorless would have meant building a door that cannot exist.

Eighteen routes came off the doorless list, 236 → 218.


**A profile that can act for you, and finally a way to say how far.** The
whole authorisation chain existed in the backend with no caller anywhere: mint
a revocable grant, authorise which phases may run unattended, start a workflow,
advance it, answer it when it stops, cancel it. Shipping the acting half
without the governing half is the wrong half to ship, and it is the half that
shipped.

The new **Delegation** screen is ordered the way the decision is. Grants first,
because a phase reads the profile's own material *through* one and it can be
withdrawn mid-run — the work stops seeing what the grant covered from that
moment rather than at the end. The policy second, because it is a choice about
scope rather than about work. The runs last, because they are what the first
two make possible.

Three things are the server's judgement rendered rather than the console's
invention. The delegable phases come from `GET /profiles/{id}/delegation`
instead of a list retyped in the client. **`research` cannot be delegated
without a grant** — the backend refuses it, because "without one the phase
reads every source item on the profile" — so the console sends the grant it
holds and lets the refusal reach anyone who has not minted one, message
intact, rather than pre-empting it with a guess. And a run that has stopped
shows **what it is waiting for**, because `awaiting` is the entire point of the
pause: the profile stopped because it needs a person, and it says what for.

Sixteen routes came off the doorless list, 252 → 236 — QRME's first pass, and
the largest backlog of the three.


**252 of QRME's 409 routes cannot be reached from any client.** The route
guards ask whether every call reaches a route. This asks the inverse — whether
every route is reachable from a door a user can open — and it is the quieter of
the two failures by far. A client calling a route that does not exist produces a
404 somebody eventually reports. A route no client calls produces nothing at
all: the code is present, its tests pass, the changelog says it shipped, and the
capability is simply unreachable.

Spot-checked rather than asserted. The console reads `/profiles/{id}/friends`
and shows the list, but `DELETE /profiles/{id}/friends/{fid}` is called by
nothing — you can gain a friend and never remove one. `/displays`, `/comments`,
`/agent/lights` and two hundred and fifty others are in the same position.

The count is recorded in `tests/doorless_routes.txt`, and the list is a backlog
rather than an approval. It cannot grow: a new route with no door fails the
test, so the gap stops widening on the day it appears. And it must shrink
deliberately: building a door also fails the test, telling you to strike the
line, because a backlog that quietly re-fills is how this got to 252.

**A correction to this cycle's earlier entry.** The first version of this audit
reported *zero* doorless routes and passed. That was wrong, and wrong in the
most dangerous way — vacuously. `app.routes` is not the flat list it appears to
be: FastAPI wraps each `include_router` in an `_IncludedRouter` that carries no
`path` or `methods` of its own, so walking the top level saw **8 routes out of
409**. Enumeration now recurses through those wrappers. Route *matching* was
never affected — the wrapper implements `matches` and delegates — so the guards
built in the last two rounds were sound; only counting was broken.

The guard-on-guard is what caught it, by asserting the route table is not
implausibly small. That test was written in the same round it went on to
falsify, which is the argument for writing them.

**Every option the backend offers, it now has to accept.** A catalog endpoint
is a menu — the console and the three shells render it directly, so whatever it
lists is what a user can pick. If the endpoint that *consumes* the choice
refuses one of those values, the user gets an error for doing exactly what they
were offered.

That is the Wall bug's shape a third time, and the one both route guards said
plainly they could not see: the request routes perfectly and the refusal happens
inside the handler, after dispatch. This check stops reading source and sends
the request. Eight of them, covering languages in both delivery modes, the same
languages as translation targets, the steering dials the server describes, the
providers on the model menu, the robots in the catalog, the connectors, and the
pack registries.

Two decisions worth stating. A 409 is not counted as a refusal — it means the
server understood the value and objected to the *state* (already bound, already
connected), which is a different thing from not recognising it. And an empty
catalog fails rather than passes, because a menu with nothing on it would
otherwise be a test that checks nothing and reports success.

**No field bug came out of this.** All 49 fixed-set refusals in the backend were
enumerated, every catalog was probed, and every advertised value is accepted.
The check was verified by making `/languages` offer Arabic while the writer
refused it, and watching both language tests fail.

One approach was tried and abandoned rather than shipped: matching client string
literals to backend vocabularies by field name. `role="dialog"`, `target="_blank"`
and `platform="xbox"` are ARIA and UI attributes, not API fields, and `kind`
alone means five different things across five modules. Nearly every hit was a
false positive, and a guard that cries wolf is worse than no guard — so it is
not in this release.

**The guard now checks the verb, not just the address.** Matching a path while
ignoring the method accepts a client that sends POST where only GET is mounted.
The answer is a 405 rather than a 404, and from the user's side that is the same
dead button — so the check was proving less than it appeared to. It now requires
a full router match, method included, and reads the verb the way each language
actually writes it: labelled in TypeScript and Swift (`method: "PUT"`),
positional in Kotlin, encoded in the helper's own name in C# (`Post(...)`,
`HttpMethod.Get`).

Scoping the check to the enclosing *call* rather than to loose path-shaped
strings is what made that possible, and it fixed the boundary in both
directions. Double-quoted paths — the ones written without interpolation — had
been skipped entirely on a guard that claimed to cover the console, leaving a
third of its call sites unchecked; 42 paths became 74 verb-and-path pairs. In
the other direction, `"/app"` stopped being counted as a request: it appears in
`defaultBase()`, where the console asks whether `window.location.pathname`
starts with it to work out where it is being served. Only something that knows
what encloses a literal can tell a request from a question about the page.

Each language's verb reader gets its own liveness test, because they are
separate code and they fail quietly. If one stops matching, every call from that
surface silently becomes a GET — and since most routes do serve a GET, the suite
would stay green while checking almost nothing. A surface reaching dozens of
routes and reporting a single verb is that failure, so it is now an assertion.

No new field bug came out of this either: all 340 verb-and-path pairs across the
four surfaces are accepted. Method-awareness was verified by injecting the
mistake it exists to catch — a console POST turned PUT, an iOS call stripped of
its `method:` label so it fell back to GET — and watching the check name the
verb the route actually accepts.

Earlier in this cycle, the same guard gained the coverage it was missing
altogether: **it had a hole in it, and six client surfaces had no guard at
all.** 0.17.0 fixed a 404 under every like, comment
and share, and added a test so it could not come back. That test cut a path
at its first interpolation whenever a query followed — correct for
`?tag=${tag}`, wrong for `/profiles/${id}/media?filename=${…}`, which it
checked as bare `/profiles`. A prefix that resolves is worse than one that
does not: the check passes and the tail it exists to verify is never looked
at. Two of QRME's console paths were being skipped that way, including the
media upload added in 0.16.0. Interpolations are now filled in before the
query is cut, with the optional-parameter idiom (`${adult ? "?adult=true" :
""}`) recognised as the one interpolation that really is a query.

The same check now covers the **iOS, Android and Windows shells**, which had
none. `native.yml` proves they compile; a path is a string in all three
languages, so `"/post/\(id)/like"` compiles, ships, and 404s in the field —
the Wall bug exactly. Around 220 path literals across the three shells had
never been compared with the route table. They are now, and the singular
mapped segments are banned in the native sources too, so the bug cannot
reappear on a phone after being fixed on the web.

Extraction is shared by both guards and byte-identical in all three repos,
since the question does not differ by product. Two tests guard the guard: one
pins the truncation bug against the live paths that were being skipped, and
one fails if a language's pattern stops matching — a scan that silently finds
nothing reads exactly like a scan that finds nothing wrong.

No new field bug came out of this. Every path all four surfaces build
resolves, and each check was verified by injecting the bug it claims to catch
and watching it fail.

## [0.18.0] — 2026-07-30

**Two versions of features finally get drawn, taught and findable.**
Everything shipped in 0.16.0 and 0.17.0 had code, a console door and a
native door — and no screen, no lesson, and no way for the in-app helper
to point at it. The convention this project has followed since the
walkthrough existed is screen SVG + gallery row + lesson + help
destination per feature, and it had quietly stopped being followed.

Three screens join the gallery: **147 Your Own Voice** (FIG. 800's order,
permission first), **148 Who Wrote This?** (the counts, and the threshold
below which nobody is named), and **149 How Should They Work?** (advisor,
collaborator, operator, or let it infer). Each gets a lesson in its own
chapter — voice and provenance under "You are in control", the role under
"Working" — and each is reachable by asking the helper in the words
somebody would actually use ("clone my voice", "who wrote this", "just do
it").

**The last two console-only features reach the native shells.** Voice
enrollment went native in 0.17.0 and the other two features that had
gained console doors did not — so iOS, Android and Windows could neither
ask *who wrote this* nor choose how the profile should work a turn. Both
now do.

**Who wrote this?** joins Manage → General on all three
(`POST /watermarks/recover`). It shows the counts — matched passages out
of stored, and the similarity — rather than a bare yes, and below the
0.25 threshold it names nobody at all, because ordinary phrases travel
between unrelated texts.

**The role picker** joins the chat composer on all three (spec clauses
2/12), with "read my prompt" as the default, and the reply reports which
role applied and whether it was declared or inferred — so an inference is
never presented as an instruction.

With this, every feature that has a door in the web console has one in the
native shells too. That parity was the thing two earlier rounds each
claimed and neither finished.

## [0.17.0] — 2026-07-30

**Voice enrollment reaches the device that has the microphone.** The
Voice screen shipped in the web console — which is the one surface where
the owner cannot actually record anything, so it asks them to *type* how
many seconds of speech they gathered. iOS, Android and Windows each gain
a **Voice** screen (`native/ios/Sources/Views/VoiceView.swift`,
`native/android/…/ui/VoiceScreen.kt`, `native/windows/Views/VoicePage.xaml`)
walking the same FIG. 800 order — permission, collection, the
characteristics, the print — but recording the sample and measuring it
instead of asking.

The privacy property survives the change, and survives it structurally
rather than by promise: the recording is written to the app's own
container (`temporaryDirectory`, `cacheDir`,
`LocalApplicationData\QrmeStudio\voice`) and only the *measurement*
crosses the wire, with `reference` naming the file. No audio is uploaded,
so no voice corpus can accumulate server-side. Turn counting is honest
about its method per platform: iOS and Android read the level meter and
count stretches of speech between silences; Windows does not meter its
input and so reports one turn per recording rather than inventing a count
from the duration.

**Fixed — every like, comment and share on the community wall returned
404, and always had.** The audience routes dispatch on a leading `{kind}`
and map the *plural* path segment to a singular kind (`posts` → `post`);
`app/src/api.ts` was asking for the singular. So `/post/{id}/like`,
`/post/{id}/comments` and `/post/{id}/share` reached the generic route and
were then refused by the kind lookup. Liking a post, unliking it, reading
its comments, writing one, sharing it — none of it worked in any release
that shipped the buttons.

Nothing caught it, and the reason is worth keeping: the backend tests
exercised the plural and passed, and the console compiled because a
template literal is only a string. Neither half was wrong on its own. So
the fix ships with `tests/test_console_routes_exist.py`, which checks them
against each other — every path the console builds must resolve, no
singular of a mapped segment may appear in `api.ts`, and the singular's
404 is observed against a live request so the rule is not merely a
spelling convention. A route-table comparison alone would *not* have
caught this: `/post/x/like` matches `/{kind}/{target_id}/like` perfectly
well at the routing layer, because the refusal happens after dispatch.

**Fixed** — the Windows navigation pane displayed the literal strings
`tab.desk` and `tab.signatures`. Chrome localization falls back to the
key when a key is missing, and those two were never added when the
screens were; all three (with `tab.voice`) are now in `L10n.cs` in every
supported language.

**Three features come out from behind the API.** An audit for what had
been skipped found the same failure this project keeps relearning: a
door nobody can open reads in the field as the feature not existing.
Voice cloning, the recoverable watermark and the advisor/collaborator/
operator role all shipped as routes with no way to reach them.

The console gains a **Voice** tab that walks FIG. 800's order rather
than offering one "clone me" button: the permission first (with the
attestation that it is your own voice), then enrollment showing the
readiness numbers so a thin enrollment looks thin, then the print, then
speaking — with the withdrawal that deletes the samples on the same
screen. The composer gains a **role picker** — advisor, collaborator,
operator, or "let it read my prompt", which is the honest default — and
the reply now reports which role applied and whether it was declared or
inferred. And Control gains **"Who wrote this?"**: paste any text and it
names the profile that produced it, from the text alone, saying how many
passages matched and whether the writing has been altered since.

**The watermark learns to survive being edited.** The field drawing asks
for a direction the credential could not go: message + sequence +
security key → watermark → **attack** → extract → reconstruct. Until now
`/watermarks/verify` could only confirm that a piece of content matched a
credential id you already had, and one changed character made it fail
while saying nothing about who wrote the text. `POST
/watermarks/recover` answers the other question — *whose work is this?* —
from the text alone, and keeps answering after the text has been
rewritten. Every stamped text now also deposits an inverted index of
**keyed five-word windows**, HMAC'd with the deployment's watermark key
(`QRME_WATERMARK_KEY`); recovery hashes a candidate the same way and asks
which stamp shares the most windows. A paraphrase that keeps most of its
sentences still resolves to its author, with the score stating how much
drifted: `matched_windows` out of `stored_windows`, a similarity, and
`unaltered` or `altered but traceable`. Below a 0.25 threshold it names
nobody, because ordinary phrases travel between unrelated texts and a
coincidence must not read as an accusation. Two properties make it a
watermark rather than a fingerprint: without the key nobody can compute
matching windows, so a credential cannot be forged onto text QRME never
wrote — and the stored rows are keyed hashes, so a provenance index can
never be read back as the writing it came from.

**Voice cloning, in the order FIG. 800 draws it.** The figure is a
permission gate first and a recorder second — 802 asks, 804 initializes,
808 collects, 810 analyzes the characteristics, 812 records the voice —
and `qrme/voiceprint.py` keeps that order load-bearing. Consent comes
first and `own_voice` is an attestation: QRME will not learn a voice on
somebody else's behalf, and consent is scoped to the sources it named
(a call, a voice note, a direct recording), so a sample from an
uncovered source is refused with the reason. Samples are **metadata
only** — seconds, turns, transcript size, and a reference naming where
the audio lives — so a voice corpus never accumulates inside the profile
database. Step 810's analysis is arithmetic anyone can check rather than
an opaque score, with a stated floor (three samples, two minutes) so a
thin enrollment is called thin instead of labelled ready. Synthesized
speech leaves carrying the watermark credential **and** a spoken
disclosure, because a cloned voice that does not say it is one is the
thing this codebase exists to refuse. And withdrawal means it: the
samples are deleted, the print retires, and the withdrawal stays on
record.

## [0.16.0] — 2026-07-30

**Your own pixels on the wall, and two new front doors.** Wall posts now
carry uploads — photos, videos and files, stored on the deployment and
served from it, kind decided by the file's bytes (JPEG, PNG, GIF, WebP;
MP4, WebM; PDF, docx/xlsx/pptx/zip, plain text — never anything a
browser executes), caps published at `GET /media/limits`, and never the
AI mark: authentic media stays authentic. A video link dropped straight
into the post text renders as the player, not as characters — the same
whitelist, the same nothing-loads-until-play facade — and other links
become links. And the account
gateway grows **Sign in with Google / Apple** — configuration decides
whether the buttons are live (`QRME_GOOGLE_CLIENT_ID` and friends), an
unconfigured door is grey with its setup note, the provider's word
verifies the inbox so the emailed-code dance is skipped, and a
passwordless account fails closed on any typed password.

**The faces come back on their own, and the phone layout stops fighting
your thumbs.** Field round. Deployments seeded before the portraits
shipped sat on initials with 34 faces in the package, because the repair
lived behind a seed button nobody knows is a repair — the API now runs a
blank-only portrait repair at startup (`seed.repair()`), including the
founder's two profiles, which the starter backfill never reached. On a
phone, the twelve tab labels forced the whole app wider than the screen
(the right half of every form hung off the viewport — tapping the Rooms
topic box opened the Kind dropdown instead), and the agent-lights window
and help button sat on top of the tab bar: the bar now scrolls, forms
stack one column, and the corner widgets ride above the tabs. Opening a
room without a profile picked now says what it needs instead of failing
with a validation dump.

**The Wall reaches the console.** The community layer — the For You
feed with its stated reasons, posts, likes, comments, shares, and
shared-video links — has lived in the backend since the community
round, but the desktop console never got the door, which read in the
field as the features not existing. New Wall tab: a composer that takes
a video link (YouTube, Vimeo, Twitch — the whitelist is shown up
front), and video cards that honor the facade contract — drawn from
stored fields only, nothing loads from the other platform until the
viewer presses play.

**Two more doors on the model menu: DeepSeek, and your own algorithm.**
DeepSeek joins the provider registry as a first-class tile
(`QRME_DEEPSEEK_API_KEY` or `DEEPSEEK_API_KEY`), and the plug the founder
asked for exists too: a **custom** provider pointing at any endpoint
speaking the OpenAI dialect (`QRME_CUSTOM_LLM_URL` + `QRME_CUSTOM_LLM_KEY`,
optional model and label overrides). The custom tile stays dark until its
URL is set — a key alone points at nothing — and both fall back like every
other unconfigured provider.

**Advisor, collaborator, operator — the role rides the turn.** Spec
clauses 2 and 12, made real: a chat turn can declare how the profile
should function (`role: "advisor" | "collaborator" | "operator"`), or
leave it unset and the profile reads the prompt itself — a transparent
keyword reading, never a hidden model call, silent on a tie. The reply's
`role_context` says which of the two happened (`declared` / `inferred`),
and the frames shape *how* the profile works — counsel with a clear
recommendation, co-creation with a next step, precise execution — never
*who* it is: persona, relationship, memory and moderation apply unchanged.

## [0.15.0] — 2026-07-29

**The temperament dials — the field's list, verbatim.** Steering gains
a fourth dial group: mood, outlook, maturity, agreeableness,
confidence, curiosity — each 0–100, defaulting to silence, rendered
into the persona prompt exactly like the existing dials and picked up
by every surface that reads the dial catalog. Together with language,
the aging lifecycle, and the freeform persona (the deliberate home of
culture and background), the video's "modify your profile's
characteristics" list is now covered dial for dial.

## [0.14.5] — 2026-07-29

**No functional changes here**: cut with the siblings. JIM-mini
gained the fall path through the watch drip, the crash watch on its
native shells, and the docs web for the field round.

## [0.14.4] — 2026-07-29

**Field feedback, applied.** Discovery cards now carry the portrait —
and say which kind of face it is: an **AI** badge on generated
portraits, **✓ real photo** only on an authentic photograph under
/photos (`/marketplace` gains `avatar` + `avatar_kind`; anonymous
profiles keep their silhouette). The Friends header drops the
"founder stands first" line. Room kinds read plainly: Text, Voice
chat only, Video, AR, VR. The Blend screen now explains itself —
blending creates a brand-new openly-hybrid profile; it is not a
follow, and the sources are untouched. And the Memory Vault gains
**Erase all** beside the per-conversation erase.

**Two versions answering is no longer a mystery.** Field report: a
fresh console over a stale backend answers "Not Found" on every newer
screen while looking otherwise alive — the shell refuses to adopt a
version-mismatched backend on its own port, but a stored base address
(for example the LAN address saved for the phone bridge) can still
steer the console to an old process. The console now performs the
version handshake itself: it compares its build version against
/health's on launch and, on mismatch, shows a banner naming both
versions and the address — with a one-click "use this app's own
backend" when a stored address is the culprit.

## [0.14.3] — 2026-07-29

**The lights are always on.** The packaged console gains a round,
watch-face-sized window pinned bottom-left on every screen — the
wrist's exact glanceable payload (three lights, three counts, the
approval line), polling `GET /profiles/{id}/watch`, with a minimize
control that folds it to a dot in the worst light's colour when it is
in the way. The choice sticks.

## [0.14.2] — 2026-07-29

**The launcher shows the joints.** The suite dashboard now renders the
two tandems the gateway wires (care team, vault sealing) as lights —
amber is degraded, not down — plus a one-press "Build my ecosystem"
(`POST /suite/ecosystem`) and the owner-scoped operations list
(`POST /suite/operations`), so the vault's record of your coordinations
is one press away from sign-on.

**Docs: suite mode enters the tandem contract.** `docs/tandem.md`
(byte-identical across the three repos) now describes how the suite
gateway wires both tandem joints itself — JIM's QRME client and QRME's
vault tenant (`suite:qrme-vault`) — and how the operations provenance
view re-draws PDI's per-tenant isolation by owner when every suite
identity's seals share the one tenant.

**The vault posture survives suite mode.** The gateway now wires QRME's
PDI tandem too: a dedicated vault tenant (`suite:qrme-vault`), found or
minted once by name, injected as QRME's own PDIClient over the
in-process bridge — so coordinations seal in suite mode instead of
quietly not. `GET /suite/health` reports both tandems, and
`POST /suite/operations` is the provenance view: the caller's
coordinations as the vault recorded them, authenticated with their own
QRME owner token and scoped by owner, because in suite mode every
identity's seals share the one tenant.

Fixed: `python -m suite.smoke` had been failing since the vault gate
moved from deployment to plan — its user enrolled as a visitor, whose
writes rightly stay out of the vault. The smoke now puts its user on a
private plan before asserting the exchange sealed. (CI's qrme-only
checkout skips the smoke, which is how it slipped.)

## [0.14.1] — 2026-07-29

**The suite wires its own tandem.** In suite mode the gateway bridges
JIM's QRME client to the mounted QRME app in-process — the care team
and specialist handoffs work with no second server — and
`POST /suite/ecosystem` builds the working ecosystem in one stateless
call: demo org seeded, care team linked.

## [0.14.0] — 2026-07-29

**The front page and the wrist.** Home gains a "New in this release"
card naming Blend, What If, Campaigns and Org; the wearables vocabulary
gains proceeds and coordination faces (counts only, never the thing
itself), drawn as watch faces 10 and 11 and routed from the pane.

## [0.13.1] — 2026-07-29

**The train after the cut.** The demo org (one press, a staffed
team on your own account, idempotent), the docs round (tandem contract
and invention disclosure caught up with the ecosystem), and hardening:
twelve departments at most (a coordination is one model call per desk),
a per-campaign daily donation count on the tokenless door, and caps
proven by tests.

## [0.13.0] — 2026-07-29

**The ecosystem round.** Crowdfunding with proceeds routed where the
user said (spec [0020] ex. two): designations that must sum to 100,
campaigns gated on them, donations split at the door onto the ledger,
succession moving the pen. The operational ecosystem (PDI proposal):
organizations, department agents on revocable grants, cross-department
coordination sealed into the vault. And the console chrome now follows
the profile's language (app/src/l10n.ts). Screens 145-146, Campaigns
and Org tabs. Proved end-to-end against live JIM and PDI processes:
the care team coordinated from JIM, the plan journaled in PDI, the
donation split exactly on the ledger.

## [0.12.0] — 2026-07-29

**The specification, mined.** The filed patent spec of App.
19/056,418 was read end to end and everything it describes that
the apps did not yet do was built in — backend and console.

### Added

- **Hybrid profiles** (spec [0038]) — `POST /profiles/composite` blends two
  or more source profiles into one `kind=hybrid` persona with normalized
  shares and borrowed aspects; the blend is public at
  `GET /profiles/{id}/composition`, departed profiles may be blended (the
  spec's "grandparents who are gone"), rated ones never, and the persona
  says openly that it is a blend. Console: the **Blend** tab; screen 142.
- **Real-time simulation** (spec clauses 1 & 5) — `POST /profiles/{id}/simulate`
  predicts the represented person's likely decision, workflow and rationale
  over a chosen horizon, with confidence **earned from evidence volume**
  (sources, remembered turns, embedding), watermarked synthetic, owner-only,
  never distributed. Console: the **What If** tab; screen 143.
- **Environmental adaptation** (spec clause 1) — `ChatRequest.environment`
  (location, conditions, local time, activity) rides beside the claim-23
  biometrics: stored, woven into the reply, echoed back. Console: the 📍
  toggle in Chat; screen 144.
- Tutorial lessons `blend` and `predict`, helper directions for all three,
  and screens 142-144 drawn for both platforms.

## [0.11.1] — 2026-07-29

**No functional changes here**: cut with the siblings. In PDI, the
desktop app finally carries its own vault — bundled backend, persistent
master key, and a release gate that proves the first run.

## [0.11.0] — 2026-07-29

### Added

- **The console catches up with its backend.** Friends, the marketplace,
  the starter collection, the rooms and the live desks all existed as API
  surfaces; the desktop console finally shows the doors:
  - **Discover** — the marketplace cards, tag search, and one press to
    install the 33-profile starter collection (idempotent server-side);
    every card is a real profile with an *Add friend* button.
  - **Friends** — the list with the founder pinned first (David Bianchi
    and his synthetic profile at positions one and two, by design —
    `qrme/friends.py` has always enforced it; now it is visible), plus
    suggestions.
  - **Rooms** — list and open rooms across every channel (2D text, 2D
    audio, 2D video, **AR**, **VR**) and see the live desks with their
    presence. AR/VR rooms carry an honest badge: join from a headset or
    phone; the desktop shows the room. New `GET /rooms` and `GET /desks`
    list routes back it.
- **The memory vault names names** (`GET /profiles/{id}/memories`,
  owner-only): one row per remembered conversation — *Dana with June
  Bianchi, 12 turns, last Tuesday* — never "profile" and "interactor",
  and each row individually erasable from the screen.

### Fixed

- **Chat's fallback stopped performing a character.** "[stub reply in a
  warm tone to: hi]" was a stage direction leaking into the play. The
  fallback now quotes what it heard plainly, says no model answered, and
  names both doors out (a provider key, or Ollama). The quoted echo stays
  on purpose — moderation must see user-influenced text ride into the
  reply, end to end.

### Changed

- Version aligned to 0.11.0 — cut together with jim-mini and pdi.

## [0.10.0] — 2026-07-29

### Added

- **A real offline model** (`qrme/llm.py`; the *Local (Ollama)* tile).
  Install Ollama (ollama.com), pull a model like `deepseek-r1:1.5b`, and
  QRME finds the daemon on its own — the tile lights up configured, no
  key, nothing leaves the machine. Automatic prefers it over the stub
  when no cloud key exists, and offline mode uses it too.
  `QRME_OLLAMA_MODEL` / `QRME_OLLAMA_URL` override the defaults.

## [0.9.1] — 2026-07-29

**There are no functional changes to QRME in this release**: cut with the
siblings. In JIM-mini, the watch panel's drip address became honest — it
says when a phone cannot reach it yet, and one switch opens Wi-Fi access.

## [0.9.0] — 2026-07-29

**There are no functional changes to QRME in this release**: the three
products are cut as one release, and the version moves so one number keeps
naming one combination of all three. In JIM-mini, the medicine cabinet
arrived — medications in the user's own words, a day board with humane
grace, and a coach that notices without ever alarming.

## [0.8.0] — 2026-07-29

**No new routes in QRME this release** — the round's new ground lives in
the siblings (JIM-mini's silence vigil, PDI's bequests), and QRME's part
was already built: reviewer-gated ownership succession and memorial
sunset. What changed here is the join: a JIM vigil event id now serves as
the succession `verification_ref`, so one attested absence carries
through all three products. Documented in docs/invention-disclosure.md.

## [0.7.0] — 2026-07-29

### Added

- **The app keeps itself current** (`app/electron/main.cjs`,
  electron-updater). On launch the desktop shell asks GitHub Releases
  whether a newer version exists. Windows and Linux download it in the
  background and offer one restart; macOS — which cannot swap an unsigned
  app under itself — says a new version exists and opens the download
  page. Every failure path is silent by design: an update check must
  never stand between the user and the app. Ships *in* 0.7.0, so this is
  the last version anyone has to fetch by hand.

## [0.6.1] — 2026-07-29

### Fixed

- **Settings says plainly when the built-in helper is what will answer**
  (Settings → *Which model answers*). The silent case was the bad one:
  *Automatic* quietly resolving to the offline stub under a screen full of
  provider logos. An amber notice now names the fallback and what to do
  about it; picking a provider with no key warns the same way. (In
  JIM-mini, the same round also fixed the coach performing distress it
  never detected — see its changelog.)

## [0.6.0] — 2026-07-29

**There are no functional changes to QRME in this release**: the three
products are cut as one release, and the version moves so one number keeps
naming one combination of all three. In JIM-mini, the Apple Watch found
its way in — an iPhone Shortcuts automation drips Health readings at a
tokened URL, and the Health app's export seeds the baseline from history
in one upload.

## [0.5.0] — 2026-07-29

### Added

- **A picker for which model answers** (`app/src/ProviderTiles.tsx`). The
  per-profile switchboard has been in the backend since 0.4.3 and nowhere in
  the app: Claude, ChatGPT, Grok, Perplexity, Gemini and the offline stub are
  now tiles you click, each marked in its own colour, each saying whether it
  is configured here and what it resolves to if not. The marks are drawn in
  the app rather than fetched — an installer that reaches out to six vendors'
  CDNs is one that leaks which product you opened.

## [0.4.8] — 2026-07-28

### Added

- **Email delivery is configurable from the app itself** (`mail_settings`,
  `GET/PUT/DELETE /settings/mail`, `POST /settings/mail/test`). Until now
  the only way to make a verification email real was an environment
  variable, so a desktop install could never send one — which is exactly
  why a user watched an inbox that was never going to receive anything. The
  Settings screen now takes a mail server, username, app password, from
  address and link address, says plainly which of the three sources is in
  force (environment > settings > none), and **sends a real test message on
  demand**, reporting what the server actually said rather than claiming
  success. The password goes up and never comes back down. Configuring one
  turns local signup back into genuine email verification, link and all.

## [0.4.7] — 2026-07-28

### Fixed

- **An upgraded app kept meeting the first version's signup.** The desktop
  shell adopted whatever backend answered its port — and on Windows, killing
  the frozen backend's bootloader left the real process alive, so a zombie
  from an early install held port 8000 across every later upgrade and served
  its old API to every new console. Three changes make it impossible:
  `/health` now reports the backend's **version**; the shell adopts a running
  backend **only when that version is its own**, otherwise it takes a free
  port and starts its own there and tells the window which address to use
  (a stored loopback address never overrides it); and quitting kills the
  backend's **whole process tree** (`taskkill /T` on Windows) rather than
  just the launcher. The release gate now also asserts the frozen backend
  reports the version being packaged.

## [0.4.6] — 2026-07-28

### Fixed

- **A stranded pending account can no longer resurrect the email screen on
  a desktop install.** Databases from older builds hold half-made accounts
  (0.4.3 crashed mid-signup) that nothing can ever verify where no mail can
  be sent. Retrying signup on a no-mail deployment now finishes the pending
  account on the spot, under the newly-typed password — the machine owner
  is the only person there. A **verified** account is never overwritten
  this way, on any deployment; SMTP deployments still require the emailed
  proof.

## [0.4.5] — 2026-07-28

### Changed

- **Verification matches the deployment, and the email got a link.** A
  desktop install has no mail service, so no email can ever arrive — yet
  0.4.4's code screen sat waiting for one: a locked door in an empty house.
  Now, with no mail transport configured, signup activates the account
  directly (the machine owner is trusted on a single-user local install —
  there is no inbox to prove and nothing to prove it to). A deployment
  **with** SMTP configured enforces the real proof, and its email now leads
  with a **clickable verification link** (`GET /verify-email/click`) — the
  shape every mainstream flow uses — with the 6-digit code as the fallback
  for a mail client on another device. The app finishes on its own after
  the click: it holds the email and password, so it polls sign-in until the
  address is proven.

### Fixed

- **A crashed signup no longer strands the retry.** 0.4.3's mid-flight crash
  left pending accounts; retrying signup answered 409 and parked the person
  on the form. A pending-account signup now routes straight to the
  verification screen and issues a fresh code; an already-verified address
  routes to sign-in.

- **The packaged app can show you its own log.** The "console" mail
  transport writes to the spawned backend's log file, which the window
  never named and could not open. An "Open the log" button (Electron
  bridge) does now — relevant to resends on deployments without mail.

## [0.4.4] — 2026-07-28

### Fixed

- **Signup answered 500 on the frozen Windows backend.** With no mail server
  configured, the verification code is printed to the server console — in a
  banner drawn with box characters that Windows' cp1252 stdout cannot
  encode. The print raised mid-request and every signup died on the one
  platform the console transport serves most. The banner is ASCII now, the
  frozen entry point reconfigures stdout/stderr to replace rather than
  raise, and a test encodes the console delivery to cp1252 forever
  (mutation-checked).

- **The console showed a JSON-parse crash instead of the server's words.**
  A crashed server answers plain text ("Internal Server Error"), and
  `req()` assumed every body was JSON — so the person saw
  *Unexpected token 'I' … is not valid JSON* instead of the actual error.
  Non-JSON bodies now surface as-is.

## [0.4.3] — 2026-07-28

### Added

- **Accounts: email + password, the address verified before sign-in works**
  (`qrme/accounts.py`, `qrme/mailer.py`, `qrme/routers/accounts.py`). The
  account is what *owns* — its id is the `owner_id` profiles are created
  under and the `account_id` memberships bill to — while every profile keeps
  its own owner capability token exactly as before. `POST /signup` creates
  an account that cannot sign in yet; a 6-digit code goes to the address
  (SMTP when `QRME_SMTP_HOST` is configured, printed to the server terminal
  otherwise) and only `POST /verify-email` proves the inbox and mints the
  first account token. `POST /signin` refuses unverified addresses and
  answers unknown-address and wrong-password identically;
  `POST /password/reset/request` + `POST /password/reset` change a forgotten
  password by the same emailed-code proof and revoke every account session.
  Passwords are PBKDF2 with per-account salts; codes hashed at rest,
  single-use, 15-minute expiry. The console onboarding is now the
  conventional two-stage flow: account gate (tabs, show/hide password
  toggles, a re-enter field checked live, Forgot password) then profile
  creation under the signed-in account.

- **Bring your own model key.** `x-llm-api-key` rides any request into a
  request-scoped context variable the provider layer reads — that request's
  generations run on the caller's credential, never persisted, never
  logged, gone when the request ends. An explicit provider choice plus a
  caller key counts as configured; a key on auto defaults to Claude rather
  than the stub; the deployment's env key remains the fallback (an operator
  lending theirs out). The Control Center stores the key device-side only.

- **The installer runs itself.** `packaging/backend_entry.py` freezes the
  whole backend with PyInstaller (CORS on, loopback only, data under the
  app's user-data directory); the release workflow builds it per-OS and
  ships it inside the installer; Electron probes `/health`, spawns the
  bundled backend when nothing answers, waits for it, and kills it on
  quit — double-click-and-done, no Python on the machine. A backend the
  user already runs is left alone.

## [0.4.2] — 2026-07-28

### Changed

- **The Anthropic provider defaults to `claude-opus-5`.** The default model
  string in `qrme/llm.py` (and the README rows quoting it) still named the
  previous Opus generation. `QRME_MODEL` still overrides, and every other
  provider default is untouched. Verified against the live API: with
  `QRME_LLM=anthropic` every chat produces a real round-trip to
  api.anthropic.com, and the per-profile switchboard
  (`PUT /profiles/{id}/model`) stores and honors provider choices.

- **`python -m qrme serve` answers the packaged console by default.** The
  installer ships only the console; the API it calls is started by hand — and
  a loopback `serve` never set `QRME_CORS_ORIGINS`, so every console request
  died as *"Failed to fetch"* against a backend that was running fine,
  including for a user following the app's own recovery instructions. A
  loopback serve now defaults CORS open (the posture the in-app hint has
  always instructed), announced on stdout, with `--no-cors` to keep it
  closed — and never when binding beyond loopback or when an explicit
  allowlist is set. Owner and interactor endpoints still require their
  bearer tokens. Four tests, mutation-checked.

### Fixed

- **The desktop installers were labelled 0.3.3.** `app/package.json` carries
  its own version and no cut ever bumped it, so the 0.4.0 and 0.4.1 releases
  both attached installers stamped with the stale number — built from the
  right tag, named for the wrong release, and invisible to the auto-updater,
  which compares package versions and saw nothing newer. Bumped, with a
  test asserting it always matches the API version, because a duplicated
  number with nothing to fail is how the last three of these happened. This
  release is the first whose installers come out named for it.

- **The desktop onboarding pre-filled a birthdate.** The age-verification
  field shipped with a sample date sitting in it — a wrong answer already
  submitted. It starts empty now, and Create My Profile waits for a real one.
  (The name field was already deliberately empty here; JIM Guardian's screen
  broke that rule and was fixed in the same pass.)

- **A network-level fetch failure surfaced as "Failed to fetch".** The
  console's error now names the backend URL it could not reach and the
  command that starts one — `python -m qrme serve`, which the old hint got
  wrong too: bare `python -m qrme` only prints the launcher menu.

## [0.4.1] — 2026-07-28

### Added

- **Platform custody, and a vault gate that asks about the plan** —
  `storage.CUSTODY`, `storage.vault_for`, `tiers.plan_of_profile`. The free
  plan is the familiar hosted-assistant arrangement: QRME holds the work and
  the person has access to it, over ordinary HTTPS, never through a vault.
  Named as **custody rather than ownership**, deliberately — a product decides
  who holds and operates a record, and does not get to decide away somebody's
  statutory rights over their own personal data.

### Fixed

- **The README's own arithmetic was wrong.** `qrme/storage.py` claimed 23
  tests against 38, `qrme/dock.py` claimed 30 against 34. A number in prose is
  a duplicate of something the repository already knows, and nothing fails when
  a file grows a test — so nothing did, in a document whose whole pitch is that
  its claims are checked. A guard now verifies every "`module.py`, N tests"
  claim against the files.

- **Stale copy behind a growing list.** `SENSITIVE` gained `clinical_note`
  and four pieces of user-facing copy went on saying **two things are
  refused**: screen 138's card, screen 140's subtitle, the walkthrough lesson
  and a README heading. Screen 140 also never drew the third refusal at all. A
  number written into prose is a duplicate of a list and drifts silently —
  nothing fails when a dict grows an entry. The copy no longer counts in prose,
  screen 140 names all three, and two guards hold it: one rejecting a hardcoded
  count that disagrees with `len(SENSITIVE)`, one asserting the screen names
  every kind on the list.

- **`docs/tandem.md` described sealing as unconditional.** It was written when
  a paid plan was the only kind. Now says which plans reach PDI at all —
  byte-identical in all three repositories, as that file always is.

- **A free account's work was being sealed into the vault.** Every seal point
  read `if pdi is not None` — whether the *deployment* has a vault, not
  whether the *account* is on a plan that uses one. On a PDI-backed
  deployment that put a free account's work in a vault it was not paying for
  and could not hold a key to. `storage.vault_for(plan, pdi)` is now the one
  place the question is asked. Guarded by counting vault writes rather than
  by reading call sites.

  Reads and deletions deliberately keep the real vault: a plan-gated vault on
  a read strands a downgraded account's history behind a billing change, and
  on a delete it leaves records nobody can reach and calls that erasure.
  Signing keeps it too — a signer is frequently an interactor with no
  membership, and gating `signatures._seal` by their plan would quietly stop
  writing the custody chain a referral depends on.

- **A clinician's note about a real person could land in the open store.**
  The referral flow writes through `referral.reply` rather than `add_source`,
  so the third-party-source rule — which is the same rule — never saw it.
  `clinical_note` joins `SENSITIVE`, refused at `POST /referrals/prepare`
  before any clinician is contacted, because refusing when the note comes back
  would strand a real person who has already been written to.

- **A refusal test that proved nothing.** `test_the_refusal_lands_before_any_clinician_is_contacted`
  passed with the guard removed, because it used a nonexistent provider and
  failed at "no such clinician" either way. A refusal test has to be reached
  by a request that would otherwise succeed; it now builds the whole flow.

- **A free plan, with nothing private about it** — `qrme/storage.py`, 23 tests,
  screens 138, 139 and 140. Two storage postures: **open cloud** (Free — the
  platform's own database, in the clear) and **encrypted vault** (Basic and
  Pro — sealed in PDI under a key you can hold, with a tamper-evident chain).
  `DEFAULT_PLAN` is now `free`, and the ladder runs visitor → free → basic →
  pro.

  **Free and Basic reach identical capabilities** — `includes("free") ==
  includes("basic")`, asserted by test. What $20 buys is privacy, not a
  feature. A free tier crippled into uselessness teaches nobody anything about
  the product; a free tier that is honestly *not private* teaches somebody
  exactly what they are choosing between.

  **The disclosure is structural.** `storage.describe()` rides on `GET /plans`,
  `GET /memberships/{id}` and the body returned when a profile is created, and
  `not_private` is a field rather than a footnote. The open posture names its
  readers — *you, anyone you share with, the people who operate this
  deployment, anyone with lawful access to it* — because "industry-standard
  security" is what a product says when it does not want to finish the
  sentence.

  **Two payloads are refused rather than quietly exposed**, and the test for
  the list is not *would the account holder mind* but **whose exposure is it**:
  source material about somebody else, and anything behind the age gate. Both
  are cases where the person harmed is frequently not the person who clicked.

### Fixed

- **A signing credential was on the sensitive list and should never have
  been.** It reads like the most sensitive thing in the product and is not a
  storage-at-rest risk at all — WebAuthn keeps the private key on the device,
  so an open store has nothing to expose. Gating it also broke signing
  outright: a signer is frequently an interactor with no membership, so
  `plan_of` returned "visitor", the posture came back open, and every
  enrolment was refused. The reasoning is recorded in the module so it cannot
  be re-added by intuition.

- **A hard line was being answered with a price.** A rated profile *of another
  real person* is refused at any amount, and the storage-posture check ran
  first — so the response was 402, telling somebody the line is a price. It is
  not. The check now runs after the hard line, and
  `test_a_hard_line_is_never_answered_with_a_price` holds the order.

- **The rated-content check ran before enrolment**, so a brand-new account was
  still "visitor" at that line and every rated profile was refused. It now
  reads the plan being asked for, falling back to `DEFAULT_PLAN`.

## [0.4.0] — 2026-07-27

The round where the products got a price, and a guide that walks you to
whatever you paid for.

### Added

- **Membership: Basic $20/month, Pro $130/month, and a visitor below both** —
  `qrme/tiers.py`, 4 routes, 26 tests, screens 130 and 131. Basic is the entry
  to *making* things: your own profiles, your own agent. Pro adds everything
  that leaves your account — the marketplace, connectors, skills, downloads,
  connections, and every modifier and builder.

  **Visitor is a real state**, not an oversight: the whole beacon story is a
  stranger scanning a printed code and landing somewhere useful, and a wall
  asking them to subscribe before reading the page would break the feature the
  beacons exist for.

  **Enforcement is one table and one chokepoint.** `tiers.gate` is installed
  once as an application-wide dependency, so no route opts in and none can be
  forgotten. The table is asserted against the served routes rather than
  proof-read — and the first version failed that assertion, naming `/steering`,
  `/governance` and `/licensing`, none of which is a route here. All three were
  paywalls in front of a wall: they read as protection, protected nothing, and
  would have survived indefinitely because nothing fails when a pattern matches
  no traffic.

  Browsing stays open by decision. The refusal is structured, because 402 is
  already spoken here by the pack price gate. A membership belongs to the
  account rather than the profile, and cancelling keeps the profiles. Money is
  simulated, as everywhere else in this repository.

- **The helper dock** — `qrme/dock.py`, 5 routes, 30 tests, screens 128 and
  129. The watch faces in a pane that tucks into the bottom corner, for the
  people who own neither a watch nor a wall panel. Same faces as the wrist,
  bound by test. **It shows and it routes; it never acts** — the inversion of
  the watch's one exception, because nothing here is the device and a control
  floating over live video is a mis-tap on somebody's broadcast. **It is inside
  every screenshot**, so it opens tucked on a surface being broadcast and
  carries no message bodies, memory, agent names or viewer names. On the
  desktop it replaced the pinned agent-lights panel rather than joining it.

- **The assistant gives directions** — *"where do I change my background"* now
  answers with the screen and the dock face, from the same table the pane
  reads, matched before `TOPICS` and before any model.

- **Three-way coverage** — watch faces 06–09 and desktop views 12–14, closing
  the hole an audit found in five more features after channel 2.

- **A guided walkthrough of the whole app** — `qrme/tutorial.py`, delivered by
  the help box in voice or text, with a test binding every lesson to the
  gallery in both directions.

### Fixed

- **A screen title's punctuation reached its filename.** `129-where-is-it?.svg`
  — the `?` starts a query string, so the README's `<img src>` drew a broken
  icon. A comma had done it once already; both came from the slug being written
  by hand in two places that disagreed. One `slug()` now, plus a test.

- **The desktop avatar was painted over the header pill on every view.**


### Added

- **A second ear: lending the profiles a wearable microphone** —
  `qrme/roommic.py`, 3 routes, 21 tests. In a voice or video room the
  participant's own microphone is carrying their voice to the other people.
  The profiles are reading text and have no ear of their own, so anything said
  aloud but not typed is invisible to them.

  This lends them any personal microphone already on the person — watch,
  earbuds, lapel, clip-on, glasses. A room-facing one (speakerphone,
  conference puck, room array) is refused, and in a room that is the sharpest
  version of the rule: it would pick up the other participants, and their
  voices are not the lender's to give. **Permission and state only**
  — capture is on the device; nothing here touches a sample.

  The counterpart is `jim/mic.py`, which lends the same wearable to the
  Guardian during a call — and the same hardware raises a *different* question
  here, because **a room has other people in it**. They are participants, so
  they can be told, and telling them is the price of the feature: the
  disclosure is readable by anyone in the room, not by the lender alone. The
  grant is per participant and never becomes the room's microphone, because
  nobody can consent for the people they can hear. Refused in a text room,
  where no primary is occupied at all, and every grant closes when the room
  does — a permission must not outlive the conversation that justified it.

  The profile's prompt states the limit rather than assuming it: *you hear
  them, not the other people in this room, who have not lent you anything and
  may not realise you could hear them.*

  Two bounds make that true of the capture rather than of a sentence in a note.
  A lent channel **keys on its wearer and drops the rest** — which in a room is
  the other participants — and it **runs near-field however the lender has
  their dial set**. Both, not just the filter, because a filter can fail and
  the people it would fail on did not choose to be in range. Every gain level
  describes the lender at a distance, never a level of company; a dial whose
  wide end meant "more voices" would be the whole objection to this feature
  wearing a different name.

  JIM caps channel 2 while a call is in progress; a room is that condition for
  its whole duration, so there is no state in which a wider one would be honest
  here. Capped, not rejected and not overwritten — the lender's setting is
  theirs and applies everywhere else. The row records both what was asked for
  and what it ran at, and the room's disclosure carries the **effective** gain
  only: what protects the other participants is how wide the channel actually
  is, and a rejected preference is the lender's business.

  **Screen 81, Lend a Microphone**, and the disclosure is the design, so the
  disclosure is the screen: it shows the other participants *by name* seeing
  the grant. A version showing the lender only their own row would be the exact
  mistake the module was written to avoid. Plus `GET /microphones/vocabulary`,
  open, so a client can draw the picker from the real sets — the refusals are
  published **by name with the reason**, because a client that knew only the
  allowed list would grey out a conference puck as though the feature were
  unfinished, when its absence is the whole argument.

- **Anonymous, several, and exactly one verified** — `qrme/identity.py`,
  8 routes, 21 tests, screens 118 and 119. Three things a person is allowed to
  be, and the module is the tension between them: you may be anonymous, you may
  hold as many profiles as you like, and **at most one of them may be
  verified**.

  The badge is not a quality score. It is the sentence *this is that particular
  real person* — said of two profiles at once it is either false of one of them
  or a claim that one human being is two authenticated people, which is exactly
  the primitive verification exists to deny everybody else. So the badge moves
  rather than multiplies: one at a time, not one forever, because a rule
  somebody could only satisfy by deleting a profile is a rule they would answer
  by lying. The record moves whole and `checked_at` is deliberately not
  re-stamped — a document seen in 2019 is not a document seen today because the
  badge changed seats.

  A `fictional` profile is **unverifiable rather than unverified** and never
  consumes the slot; getting that backwards would let an invented character
  lock a real person out of their own badge. "One person" means one owner
  account, which is the unit this platform can observe, and the cross-account
  check closes only the visible part — the same attestor vouching for the same
  evidence twice. A `self_asserted` level has no evidence to match on, and that
  limit is stated rather than papered over.

- **A live desk wears an overlay and keeps its badge.** This was refused in
  this same branch, and the refusal was wrong: it conflated *this face is
  unmodified* with *a real person is behind this*, and only the second is what
  `desks.DESIGNATION` ever claimed. A costume is not a synthesis. Refusing it
  protected nothing and cost the people who most need to work without showing
  their face.

  `GET /desks/{id}/live-person` returns **one burned mark — `NOT AI · REAL
  PERSON`** — and it does not change when somebody puts a face on. A first fix
  composed the badge with the costume (*"… · wearing The Wolf"*), which
  answered a question nobody had: a viewer is on a **named account's** live or
  room, with the handle at the top left, and they chose it to get there. The
  open question on that page is never *is that his real nose*, it is *is there
  a person here at all*.

  It also removed a quiet penalty — somebody covering their face because of
  dysmorphia, or because their work makes showing it unsafe, was handed a badge
  announcing the fact on every frame while the person beside them got a clean
  one. Same claim, same mark, whatever you wear. Read from the desk row and its
  attestation, never accepted from a client, so a stream that never earned it
  cannot paste it on.

- **An anonymous profile can wear a field emblem** — `identity.set_emblem()`,
  2 routes, 7 tests, 16 generated assets. The plain silhouette was the only
  face, on the argument that a distinct picture would be a stable mark
  following one person around. That argument died with the fixed name:
  `Anonymous 41338025` is already stable and already public, so an emblem adds
  no correlation the name does not — while a nurse answering health questions
  looking identical to a troll is a real cost paid for nothing.

  One per industry the platform already models, so the set is not a new
  vocabulary invented for pictures. Each keeps the **same silhouette** with the
  field glyph badged on, so "anonymous" reads first from across a roster before
  anybody parses which symbol it carries.

  **They are a shortcut, not a fence — an owner may upload their own image.**
  This was briefly a closed list, on the reasoning that a profile able to
  attach any image could attach its owner's face and nothing here can look at
  a file and tell. True, and the wrong conclusion: it made the feature useless
  to the locksmith who wants a photo of their own workbench, and bought no
  safety, since somebody set on publishing their face can put it in a post. A
  limit that stops the honest use and not the risky one is decoration.

  So what cannot be checked is **said**: a photograph of your own face is
  allowed, and the response tells you it undoes your anonymity to anyone who
  knows you — a line that is now in `NOT_WITHHELD` beside "your writing is
  still yours". Somebody else's likeness is refused, declared exactly as the
  overlay module asks it. Its own table, never `profiles.avatar` — two pictures
  for two states, and writing it into `avatar` would mean turning anonymity off
  showed it instead of the real face.

  An **empty bubble is an empty picture frame with a plus**, and it is the same
  picture for the owner and for visitors. Two defaults were tried first — a
  plain silhouette for strangers, the photo-and-plus for the owner — on the
  reasoning that the second reads as a control offered to somebody who cannot
  press it. The identifying work is done by the name, though: `Anonymous
  41338025` already says which account this is, so the picture is a placeholder
  rather than a claim about anybody. Two defaults were also two things that
  could disagree about one profile, so `editor_asset` and `silhouette.svg` are
  both gone.

- **Anonymous profiles get a fixed name they cannot change** —
  `identity.anonymous_name()`, 7 tests. Every one of them used to be called
  *"anonymous persona"*, identically, which is unusable the moment two are in
  the same place: three anonymous people in a room were three identical labels,
  so you could not follow who had said what and nobody could be held to
  anything they said. Pseudonymity is a stable name without a real one, not the
  absence of a name.

  `Anonymous 41338025`, and three properties carry it. **Derived, never
  stored**, so there is nothing to edit — which is what "cannot be modified"
  has to mean where an owner can `PATCH` their own profile, and a chosen
  anonymous name would be a free text field on the one surface built to
  withhold identity. **Keyed on the profile, never the account** — the one that
  would quietly undo the `owner_id` redaction, since numbering a person's
  several anonymous profiles from their account would match them to each other
  in public. **Hashed, not sequential**, because a counter publishes signup
  order and, from two samples, the growth rate.

  The decision was being made in **fifteen places**, each with its own copy of
  `"anonymous persona" if anonymous else display_name`. A rule with fifteen
  implementations is one merge away from sixteen, and the sixteenth is the one
  that prints somebody's name — so it is one function now, and a test parses
  every module to assert nobody has written another.

- **Whose live, room or stream this is now appears on it** —
  `identity.whose()`, 1 route, 5 tests. The simpler burned mark is justified by
  the viewer already knowing whose account they are on, and that was asserted
  while the top-left of a live surface carried a `LIVE` pill and nothing else,
  and while no route returned it. The argument was resting on chrome that did
  not exist.

  One function for every surface — desk, room, party, connection, stream —
  because "whose is this" must have one answer everywhere; a desk that names
  its owner while a room names nobody is how a viewer learns to stop looking.
  Drawn beside the `LIVE` pill on all nine surfaces with a picture, full screen
  and landscape included, since full screen is where it matters most: that is
  the state with the app's own header taken away. And returned **with** the
  mark by `GET /desks/{id}/live-person`, so a client cannot render one without
  having been handed the other.

  An anonymous account answers with its silhouette name rather than nothing — a
  viewer still needs to know the stream belongs to one consistent account,
  which is a different fact from knowing which person that is. Its `@handle` is
  withheld: this call answers *who is this*, not *where is this*, and the
  handle would put an identifier on the one surface built to withhold one.

- **Seventeen face overlays**, not one. Masks and half masks, characters,
  creatures, 2-D and 3-D avatars, helmets and visors, paint, makeup, hair,
  headwear, eyewear, prosthetics, rendered styles, and plain blur or silhouette
  for anybody who wants to be present without being seen. Named as a need
  rather than a nicety: somebody with dysmorphia has to be able to appear
  without appearing, and one mask and a shrug is not that.

- **Backgrounds: your own, imported, or AI-generated** — screen 124. `kind`
  says what happened to your face; the new `source` says what happened to the
  room, and a single "filter applied" would run the two together. **A generated
  background is synthetic media** even though the person in front of it is
  real, and the disclosure says both in that order — the viewer is deciding
  about the person, and the room is the part that was made. `source` is
  required on a backdrop and refused on anything covering a face, and an
  imported image has to be one the wearer holds the rights to — asked rather
  than guessed, like the face question.

- **No synthetic member ever occupies a player slot** — screen 125. `teammate`
  is the seat that means *in the match, taking a slot*, and nothing synthetic
  may hold one; checked in `gamelobby.seat` rather than left to a prompt,
  because the point of the rule is that it survives a model deciding otherwise.
  Five more entries close the plumbing, each refused **in the words somebody
  would use to ask for it**, because a single generic refusal loses that
  argument — "it's only a second controller" is true and not the point.
  `own_hardware` (a second machine moves where a bot runs), `second_controller`
  (the same bot with a shorter cable — a controller nobody is holding is not a
  player's), `bluetooth_input` (that again, wireless; the pairing is the tell),
  `capture_perception` (a capture card feeding it the picture is how it would
  learn where to aim — **watching the screen to play is playing**),
  `game_plugin` (an overlay, mod, injector or plug-in handing it state or
  controls, whatever it is called), and `own_character` (no member pilots one —
  not a second character beside yours, not a co-op partner, not a body in the
  world).

- **More than one synthetic thing in a game session** — `qrme/gamelobby.py`,
  5 routes, 19 tests, screen 122. `game_sessions` seats exactly one profile;
  this is the roster beside the real players — other profiles, and running
  workflows as `agent` members carrying the same green/amber/red light as
  everywhere else.

  **Adding a second one changes the question, and the question is fair play.**
  A companion calling shots is a teammate talking; five coordinating on one
  player's behalf is indistinguishable, from the publisher's side, from a bot
  squad. So synthetic members are **capped at four**, counting the session's
  own profile — a lobby where the synthetic side outnumbers the humans has
  stopped being people playing with help. And **nothing here can act in a
  game**: no input, aim, macro, automation or exploit, published by name in
  `NEVER`, with a test asserting no function in either module is named for any
  of them.

  Every member says what it is on every read, never inferred from a name — it
  matters more here than in a chat room, because the other people in a match
  did not opt into anything. The session's own profile is derived rather than
  stored, so a roster can never show a session hosted by a profile the session
  does not think it has. A minor anywhere in the lobby makes the whole lobby
  strict, keyed on the lobby rather than the owner.

- **Two more beacon placements walked end to end** — a pharmacy counter and a
  link posted to a neighbourhood site. The pharmacy is the one that carries the
  most obligation, and the neighbourhood one exists because **the scan is the
  only part that changes**: `scan_url` is an ordinary URL and the QR is one way
  of typing it, so the same page, mark, age wall and picked-up sentence all
  answer — but the camera path is gone and `label` has to mean something to a
  reader rather than to somebody standing in front of a wall.

- **Wearing a character over your own camera** — `qrme/overlays.py`, 4 routes,
  14 tests, screen 121. A mask, a creature driven by your own expressions, a
  puppet, a replaced background. Ordinary, and it lands directly on the
  argument everything else here is built from: an overlay is synthetic media
  composited onto a real human face in real time, and the fact that the person
  underneath consented does not change what the **viewer** is looking at. So
  the rule is neither allowed nor banned: it is disclosed to the people who can
  see it, always, and it can never be the thing that makes a truthful badge
  false.

  **A live desk can never wear one.** Its badge reads "Live person — not AI"
  and its whole premise is that a real human is behind it — the badge is
  *inverted* precisely because there is a person there. A character over that
  face makes the badge a false statement, on the one surface whose entire value
  is that it is true. Refused rather than the badge weakened, because a desk
  that cannot promise a real person is not a desk.

  **No overlay may depict a real, identifiable person** — refused by name with
  the reason, alongside public figures, another user's portrait, age shifts,
  and drawing a mark or badge into the picture. It is *asked* rather than
  guessed, because nothing here can look at a file and tell whether the face in
  it belongs to somebody; the declaration is recorded either way, so a false
  one has a name and a timestamp on it.

  The disclosure distinguishes what it discloses: a replaced face reads "not
  their face … a real person is underneath", a replaced background reads "their
  own face, unaltered". A disclosure that cries wolf is one people learn to
  skip.

- **Channel 2 off the room** — `roommic.lend_on` and friends, 4 routes, 18
  tests, screen 120. The same lent wearable on a **watch party**, a **live
  desk's stream** and a **one-to-one connection**. Rooms already covered voice,
  video, AR and VR by channel, so a 3-D or VR room lends exactly as a voice
  room does.

  One question decides whether a surface qualifies: **can the other people
  present be told?** That is what made a room different from a phone call —
  `jim/mic.py` refuses speakerphone because the other party is a stranger to
  this product, with no surface on which to show them a disclosure, so their
  voice could never be part of the bargain. Every place added here has a member
  list and somewhere to render one; a surface without both must never be added,
  whatever else is convenient about it, and `GET /microphones/places` publishes
  the test rather than only the list.

  Rooms deliberately do **not** write to the new table. Two storage paths for
  one surface is how a disclosure ends up reading one while the grant sits in
  the other, and a microphone that is live but undisclosed is the worst failure
  this feature has. A separate table rather than a column on `room_mics`
  because this schema has no migrations.

  Presence is checked rather than assumed: somebody who left a watch party is
  not present, an ended connection is not a place, and an unknown id answers
  404 rather than 403 so a stranger cannot tell a real place from an invented
  one by the status code. The place ending returns the microphones, wired into
  `watchparty.end`, `desks.set_presence(..., "closed")` and ending a connection
  rather than left as a function nobody calls.

- **Anonymous profiles wear one shared silhouette** — `avatars.SILHOUETTE`.
  Everybody who is anonymous gets the *same* figure, and the sameness is the
  feature: a per-profile silhouette, tinted or initialled or generated from the
  id, would be a stable mark following one person across every surface, which
  is what an anonymous profile is trying not to have.

  It closed two leaks the flag never touched. A profile that had set a portrait
  of its own face went on serving that face while its name was withheld — a
  picture is the strongest identifier on a page. And a profile with *no*
  portrait fell back to initials drawn from the display name, so hiding the
  name produced a monogram of it. Substituted in `avatars.render()` rather than
  at each surface, because 2-D, 3-D, VR, AR, the beacon page and every embed
  read that one shape, and a surface cannot opt out of a rule it never knew
  about.

- **Two cards on screen 119 said the rule instead of what it does.** "One
  badge, not three" only counts if you count the rows above it, and "it says
  you are one person" parses as the badge making a claim about your personhood.
  "One at a time, not one forever" is the argument in `qrme/identity.py`
  compressed into a riddle — fine in a docstring, where the reader came looking
  for reasoning; useless on a card, where they came to find a control.

- **`docs/beacons.md` walks two placements end to end** — a songwriter's
  sticker at a concert hall, and an 18+ creator's on a bathroom stall door.
  Both were chosen because the person scanning is a stranger standing somewhere
  the creator is not, which is the condition the whole feature has to survive.
  Writing the second one found three of the defects below.

- **A profile on a screen that stays where it is** — `qrme/displays.py`,
  6 routes, 17 tests, screen 126. A wall panel, a kiosk, a counter screen, a
  pane of glass with something behind it. Sizes `badge`/`half`/`full`,
  finishes `opaque`/`transparent`, and a closed set of faces — the watch-face
  idea applied to fixtures, for the same reason the watch's list is closed.

  **A stationary screen is not a small watch, and that is the whole module.** A
  watch is on one person's wrist; they chose it and they are the only one
  reading it. A wall panel is read by whoever walks past — a courier, a child,
  somebody visiting the person whose profile it shows. That is the
  room-microphone argument from the other direction: there a device that
  *hears* people who did not agree, here one that *shows* things to people who
  did not ask. So the list is **shorter** than the watch's, and every face on
  it is already public.

  **There is no `control` face.** Assist, halt and approve are safe on a wrist
  because the wrist belongs to the owner; a button on a wall is pressed by
  whoever reaches it. Messages, memory, friends, notifications and agent
  *names* are refused the same way, each by name with its reason — every one of
  them is allowed somewhere else in this product, so the absence is a decision
  rather than a gap.

  **The AI mark gets a backing plate on glass.** A transparent panel's
  background is a corridor, and a moving one, so contrast is not something the
  renderer controls — and a mark that vanishes against a bright wall is worse
  than no mark, because the rest of the card still reads as a person. A
  `beacon` face needs the full surface: a QR at strip height is one no camera
  resolves, and an unscannable code looks broken rather than absent.

  Placing one is the owner's decision, like a beacon. Where the screens *are*
  is owner-only; what a given screen is *showing* is public, because a fixture
  in a corridor cannot keep a secret from the corridor — which is also the
  check on the design: if that route could leak anything, the wrong thing is on
  the face list.

- **A guided walkthrough of the whole app** — `qrme/tutorial.py`, 6 routes,
  16 tests, screen 127. `help.py` answers a question somebody thought to ask;
  this is the other half of the same surface, for somebody who does not yet
  know what there is to ask about. Seven chapters, seventeen steps, in an order
  that introduces nothing before it exists.

  **The guide has no name and no face**, structurally rather than as a style
  choice: a tutorial guide with a persona would be the most convincing
  synthetic profile on this platform, met by every user in their first minute,
  at the exact moment they have the least idea what is synthetic here.

  **It never taps anything for you** — every lesson says what to tap, none of
  them taps it, and a test asserts the module writes to nothing but the
  learner's own progress. **It works with no model configured**, like
  `help.TOPICS`, because a walkthrough that needs an API key is missing on a
  self-hosted deployment.

  **Voice and text are one lesson rendered twice.** Spoken, a screen number is
  noise, so `?mode=voice` drops the numbers and keeps the sentence — two
  hand-written versions would drift and the spoken one would be the one nobody
  re-read.

  **And it cannot quietly fall behind the app.** Each lesson names the screens
  it covers and a test asserts every screen in the gallery is claimed by one,
  in both directions. Add a feature, draw its screen, and the walkthrough fails
  until somebody has said what it is for.

- **Channel 2 reaches the watch and the desktop** — watch face 05, desktop view
  11. The audit before tagging found the feature had screens on the phone only,
  which is the odd one out: **the watch is the device being lent.**

  Face 05 is the only watch face that can *end* something, and that is
  deliberate rather than an exception to "the wrist adds reach, not powers". A
  lent microphone **is** this watch — making somebody find a phone to stop
  their own device listening would be the one permission on the platform you
  cannot revoke from the thing it runs on, and "yours to end, alone and at any
  moment" would be false. `wearables.FACES` gained the permission in the same
  change, so the test binding faces to permissions held.

  Desktop view 11 is the one a wide window earns: a desk operator has a room, a
  watch party and a stream open at once, and the question a phone cannot answer
  is *where is my microphone live right now, all of it* — shown beside the
  room's own disclosure, because those two being the same thing is the design.

- **The rest of the round reaches the watch and the desktop too** — watch faces
  06–09, desktop views 12–14. Channel 2 got its watch face because the audit
  caught it; the same audit run against everything built since found the same
  hole five more times. Overlays, backgrounds, the game lobby, identity and
  fixed screens were all phone-only, and all five answer a question you ask
  *while you are away from the phone*.

  The wrist question is one question in five shapes: **what am I currently
  presenting as?** Face 06 is the name and picture a stranger sees right now —
  which for an anonymous profile is the fixed `Anonymous NNNNNNNN` nobody can
  change. Face 07 is what is over your face and behind you on camera. Face 08
  is who is in the lobby beside you, with the seat kinds spelled out. Face 09
  is which fixed screens are lit and what each one is showing. None of the four
  can change anything — the wrist adds reach, not powers, and face 05 stays the
  single deliberate exception because a lent microphone *is* the watch.

  `wearables.FACES` gained all four in the same change, and the binding test
  was tightened while it was open: it now reads an explicit `face="..."` key
  out of the builder rather than inferring the face from a title, so a face
  drawn under a name the regex happened not to match can no longer pass.

  Desktop views 12–14 are the ones a wide window earns rather than a phone
  screen made larger. **13 Camera & Screens** is the clearest case: overlays,
  backgrounds and fixed displays are three modules on the phone and one
  question at a desk — *what does everything of mine that is currently facing
  outward look like* — so they are one view.

- **The assistant delivers the walkthrough by voice or by text** —
  `help.ask(question, mode=...)`, `POST /help` gained `mode`. The tutorial
  already existed at `/tutorial`, which is fine if you know it is there. What
  somebody actually does is ask the help box *"show me around"* — a phrase that
  is not a question with an answer, and answering it with a paragraph **about**
  tours would be the most annoying possible reply.

  So the phrase table starts the tour instead, handing back the first step
  inline. Voice is a `mode` on the existing help box rather than a second
  endpoint: a spoken assistant and a written one answering differently is two
  products, and the spoken one would be the one nobody re-read. The refusal
  check still runs **first**, so asking the guide to pretend it is somebody is
  refused rather than answered with a tour.

### Fixed
- **The account avatar was painted over the header pill on every desktop view.**
  It sat at a hard-coded 96px from the pill's right edge while `status_dot`
  sizes itself from its label, so at this label's length the orb landed *inside*
  the pill and covered three characters of "Assistant". It read as a rendering
  glitch across all eleven views, which is how it survived: a mockup's header is
  the part nobody looks at twice. Derived from the same expression that sizes
  the pill, so a longer label moves the avatar instead of colliding with it.

- **An explicitly empty face list was silently answered with the defaults.**
  `faces or DEFAULT_FACES` collapsed "use the defaults" (`None`) and "show
  nothing" (`[]`) into one branch, so the guard against a blank screen could
  never fire and a caller asking for one got the opposite of what they asked
  for. Found by the test written for the guard.

- **Anonymity was a label on four surfaces, not a property of the profile.**
  `anonymous` was honoured by the front-page card, the landing page, the prompt
  and the watermark — every surface that *renders* a profile. `GET
  /profiles/{id}` is public and returned `display_name` in full, so the
  shortest way past anonymity was to ask for the profile.

  `owner_id` was the worse half, because it does not undo one profile's
  anonymity — it undoes all of them at once. Two anonymous profiles sharing an
  account are the same person, and anybody could read that field off both and
  match them, then read it off the named profile beside them and put a name to
  the pair. Now withheld from everyone but the owner on **every** profile,
  named ones included, along with `successor_owner` — somebody else's account
  id, never a visitor's business.

  An anonymous profile's badge also withholds **who checked**: "verified by Dr
  Okafor of St Mary's" narrows an anonymous author to a city and a workplace,
  and the badge would undo the anonymity it sits beside. What survives is the
  part worth having — a real person stands behind this and somebody checked —
  which is the difference between a pseudonym and a bot.

- **The seed verified both of the founder's profiles.** They are the same human
  being, so the platform was asserting that David Bianchi was two verified
  people, on the deployment that ships as the worked example of the rule. The
  badge now belongs to the photographed profile alone, because a real person
  whose picture is authentic is what the badge is a claim about; the rendered
  half carries the AI mark, which is the claim that is true of it.

- **The room-microphone disclosure was readable by anyone holding a room id.**
  The route's own docstring said "readable by anyone in the room"; the code
  checked nothing, so "in the room" meant "knows the id" — and a room id is not
  a secret. It rides in beacons and on printed QR stickers, which is the point
  of them. That turned a privacy feature into its opposite: who is wearing a
  live microphone, on what, and since when, published to whoever scanned the
  sticker. Being in the room now means holding a participant's token or the
  owner token of a profile in it. Two tests, and the one that matters is the
  signed-in stranger rather than the anonymous caller.

- **Pairing and lending were two vocabularies for the same hardware.**
  `qrme/wearables.py` registers a collar clip as `lapel_mic`; `qrme/roommic.py`
  is kept in step with `jim/mic.py` by hand and calls it `lapel`. Nothing
  joined them, so you could pair a lapel mic and be told `lapel_mic` was an
  unknown microphone type when you tried to lend it — from a registry whose own
  comment says it exists for this feature. `FROM_WEARABLE` translates rather
  than renames, because renaming either side breaks something real: the JIM
  table is maintained by hand precisely because the products do not import each
  other, and the registry names are already in paired rows. A test holds every
  kind in the registry against one side or the other, so adding a device forces
  the question *does this carry a microphone* when it is added rather than when
  somebody tries to lend it. A refused kind now gets its reason back instead of
  "unknown", which reads as a gap somebody files a bug about — or works around.

- **`docs/tandem.md` was 92 lines short in PDI.** The "Reaching a real
  clinician" section added in 0.3.0 and the channel 2 section never reached the
  third repo, so the file that is meant to be byte-identical in three places
  was identical in two. Resynced.

- **Placing a beacon was not owner-only.** Anybody could print stickers
  pointing at somebody else's profile, in places its owner never chose and
  could not see — and where a profile is left is a decision about the profile:
  a recovery sponsor's code belongs at a meeting and not on a billboard.
  Listing them was public too, and `label`/`location` are free text like "the
  back table at the Tuesday meeting" — a list of physical places tied to a
  person, so scanning one code told you where all the others were. And picking
  one up was unauthenticated, which made it a way to switch off a stranger's
  printed codes: every one dead at once, paper still on the wall, nothing to
  see wrong with it.

- **A rated profile could be placed as a shared room.** `docs/beacons.md` has
  said since the feature shipped that rated placements stay one-to-one — a
  shared room behind an adult code in a public place is a different product
  with different moderation questions, strangers who scanned a sticker on a
  wall in one room together. Nothing enforced it; the combination was reachable
  by setting a flag, and the only thing in front of it was the age gate on the
  landing page. Refused now rather than silently downgraded to `chat`, because
  somebody who asked for a room and quietly got private threads would not find
  out until the fortieth person was talking to themselves.

- **Nothing tied the README's gallery to the screens on disk** —
  `tests/test_docs_gallery.py`, 3 tests. Three separate defects had already
  shipped through that gap: six stale SVGs left rendering after a renumbering,
  a screen built and never shown, and — while restoring screen 81 in this very
  round — inserting a cell into a full three-wide row silently pushed **82**
  off the page. Every file existed and every link resolved; the gallery just
  read 79, 80, 81, 83. So the numeric run is asserted as well as both
  directions of existence, because a number that stops appearing is exactly
  what nobody re-reads an 1,800-line README to find.

## [0.3.3] — 2026-07-27

**The round where an agent working on its own stopped being something you had
to go and check.** One question — *does this need me right now?* — answered on
the wrist, in the app, and over whatever screen you happen to be on.

### Added

- **The agent status light** — `qrme/agentlight.py`, 1 route, 9 tests. Five
  workflow statuses collapse to three colours, and each colour carries a word:
  green *working* or *done*, amber *needs you*, red *stopped*. The word rides
  with the colour because green alone cannot separate an agent that is still
  going from one that has finished, and those call for opposite reactions.

  **Derived, never stored.** There is no `light` column and nothing sets one —
  it is computed in `_hydrate()`, the single function every workflow read
  passes through, so a row cannot be persisted with a light that disagrees with
  its own status. A second field naming the same fact is a second field that
  can disagree with the first, and the one a screen reads would be the one
  nobody remembers to update. A test asserts the column's absence.

  **An unrecognised status raises rather than defaulting.** A default would
  paint an unknown state green, and green is the colour that means *ignore me*
  — the one failure this must not have. `GET /agent/lights` returns the legend
  built from the mapping rather than restated beside it.

- **Three surfaces, doing three different jobs** — screens 82 and 83, and the
  desktop console. The watch face (in JIM) shows three lights and three counts
  and **no agent names**: naming them was the first cut and was wrong, because
  a name is something you read and reading is the thing a glance cannot do.
  Screen 82 folds every agent into one tappable group per light, so somebody
  opening it *because* amber appeared is not scanning a flat list for the one
  that changed. The overlay rides over an ordinary screen and over **every**
  desktop view — an agent that reports only on its own screen is one you have
  to remember to check, and amber and red are exactly the states nobody thinks
  to look for.

  Shaped like the watch face rather than as a bar across the screen: a small
  translucent box in the bottom-right, three stacked rows, each its own tap
  target. On mobile it sits above the help button, which was already parked in
  that corner on every screen — two things competing for one corner is worse
  than either of them being there.

### Fixed

- **Two of the three group subtitles ran under the chevron.** Visible in a
  render and invisible in the source, which is how it survived being written.
  `agent_groups()` now length-guards them, so the next one fails the build
  rather than arriving months later as a screenshot.

## [0.3.2] — 2026-07-27

**The round where the starter collection stopped looking like a directory.**
Each of the 34 is now shown as the profile card the app actually gives it, and
the one starter with no source material finally has some.

### Changed

- **The starter gallery shows each profile's own front page** —
  `tools/starter_cards.py`, `tools/starter_gallery.py`. It used to be a
  portrait with a name and an industry captioned under it, which is a directory
  listing rather than a profile: screen 80 gives a starter an avatar bubble, a
  role, the rating people who talked to it left, skill chips, Memory /
  Relationships / Engagement, a career, a review, and a **Talk to** button. The
  page was showing two of those.

  It was also **five columns wide** — roughly 590px of content on a phone that
  offers 390, so on mobile the fourth column was sliced mid-word and the fifth
  never appeared at all. Every starter past the third was unreachable to
  anybody reading on a phone. Two columns of whole cards fit, checked by
  rendering the real markup at 390px rather than by arithmetic.

  Generated from `qrme/seed.py` rather than hand-written, because the old
  gallery was a second copy of the starter list maintained by hand and could
  drift from it silently. Adding a starter without a role line is now a build
  error instead of a blank cell, and both tools have a `--check` mode.

  Careers and reviews are written, like the personas: these are invented
  experts, so a CV is characterisation of the kind the bio already is, and each
  is drawn from that starter's own bio so the two cannot contradict each other.
  The rating and the three tiles are the app's own sample values, identical on
  every card — a freshly seeded starter has zero of each, so 34 cards reading
  *4.0 · 37 reviews* is self-evidently a template, and the README says so.

### Fixed

- **The rated starter was the only profile with no source material at all.**
  0.3.1 grounded every starter in its industry's Field Pack and left Vivienne
  Sable out, because the rule read *"there is no adult-industry Field Pack, and
  inventing a substitute would be putting words in a profile the age wall
  exists to contain"* — which ran two things together. The wall governs **who
  may talk to her**; it was never a reason for her to know less about her own
  subject.

  The **Cabaret & Burlesque Field Pack** is theatre history and stagecraft: the
  Ziegfeld era, the Parisian revues, and why a tease is a rhythm problem. Free
  and unrated like the other 33, so it reaches her through the existing path
  with no change to `_ground()` — she was already in the same seed loop with
  nothing to match. Seeding now reports `grounded: 34`, where it reported 33.

  Deliberately **not** the same thing as `RATED_PACK`, which is the $6.99
  age-gated *After Dark Companion Pack* sold to owners of any adult-mode
  persona and never auto-installed. A test pins both so the two cannot be
  merged by accident.

- **`test_starter_packs_cover_every_industry` compared the pack list against
  `STARTERS` and not `STARTERS + RATED`** — so the test that existed to catch a
  missing pack had been asserting the gap into place, and would have gone on
  passing forever with her ungrounded.

## [0.3.1] — 2026-07-26

**The round where the starter profiles stopped answering from tone alone.**
Thirty-four of them shipped with no source material at all while the packs
that matched them sat unused in the marketplace. Plus the README finally says
which version you are looking at.

### Added

- **Starters arrive knowing something** — `qrme/seed.py`, 12 tests.
  `qrme/packs.py` has always described its starter packs as *"one free Field
  Pack per industry, **matching the Starter Collection**"*. The pairing was
  never wired. All 34 starters shipped with **zero source material** while 37
  packs sat in the marketplace — Dr. Sana Iqbal had an environment persona and
  no environmental knowledge, Diego Fuentes a construction persona and no
  construction material. Every one of them answered from tone alone.

  Seeding now installs each starter's own industry pack, and it is part of the
  **repair** path, so deployments seeded before this catch up by re-running
  rather than by hand across 34 profiles.

  Deliberately narrow, and each limit is a way of not overwriting somebody's
  decision:

  - **Only the starter's own industry.** Not "everything relevant" —
    `build_system_prompt` renders `sources[:8]`, so a profile that hoards
    material crowds out its own knowledge. One pack is three items, which
    leaves the budget room to grow.
  - **Only onto a profile with nothing.** An owner who added their own
    material, or removed the pack on purpose, is not topped up on the next
    seed — the same blank-only rule the portrait backfill follows.
  - **Free packs only, and no ledger credit.** A deployment grounding its own
    starters is not a purchase; a priced pack stays a decision for whoever owns
    the profile.
  - **The rated starter is left alone.** There is no adult-industry Field Pack,
    and substituting one would be putting words in the profile the age wall
    exists to contain.

### Fixed

- **The README's avatar bubbles had no visible glow.** The bubble shipped in
  0.3.0 got the rounded clip right and then blurred the halo across most of the
  margin, which spread the light so thin it vanished against a dark page — a
  glow that existed in the source and nowhere a reader would see it. Narrowed
  the blur and raised the strength so the gallery matches the Profile Home
  screen it is meant to mirror. Checked by rendering against the app's own
  background, which is the only way this is checkable at all.

## [0.3.0] — 2026-07-26

**The round where the tandem reaches a person.** A synthetic specialist could
answer a question; now it can be handed a multi-step task, and the person it
is talking to can be put in front of a real clinician with the release signed
for rather than ticked.

### Added

- **Owner-authorized workflow delegation** — `qrme/delegation.py`, 5 routes,
  14 tests. `qrme/workflows.py` has always run a plan of phases in character,
  carrying memory forward and surviving across sessions. Every route reaching
  it was `require_owner`, which is right for the owner's console and blocked
  the case the tandem needs: **JIM's Guardian handing work to a specialist it
  is already talking to.**

  The obvious fix — let an interactor call the workflow routes — is the wrong
  one. **A workflow is not a chat turn.** `POST /chat` composes one reply and
  moderates it; a workflow runs several phases unattended, and its `research`
  phase reads the profile's vaulted source material. Worse,
  `workflows._scoped_items` treats a missing grant as scope `["*"]` — *all of
  it*. Letting anyone who can reach the endpoint start that is not the same
  decision at a larger size; it is a different decision.

  So delegation is **off until an owner turns it on**, and turning it on means
  saying what may be delegated. **A grant is mandatory the moment `research`
  is delegable** — refused at write time (422), where the owner is present to
  read the error, rather than at 3am inside somebody else's workflow. A caller
  may only ask for a subset of the owner's phases, and omitting the plan gets
  the owner's set rather than `DEFAULT_PLAN`, which is every phase there is.

  The two surfaces never merge: an owner's own workflow has no
  `delegated_workflows` row, and that absence is the whole guard — it 404s on
  the delegated routes however the caller authenticates.

  `send` *is* delegable, deliberately. The phase produces the finished
  deliverable; there is no code path from a workflow phase to an outbound
  message.

- **Medical referral, signed for rather than consented to** — `qrme/referral.py`,
  5 routes, 14 tests. `POST /handoffs` could already package an AI specialist's
  session for a real provider. It releases on **`consent: true`, a boolean the
  client sets** — while `qrme/webauthn.py` opens by describing itself as *"the
  layer that turns 'the app says the user agreed' into something a third party
  can check"*. The whole signing stack — enrolment, proofing levels,
  device-bound credentials, verified evidence packages — sat one import away
  from the single endpoint that ships somebody's health conversation outside
  the product, and a checkbox was authorising it.

  A referral signs at the **`high` tier**: document proofing on a device-bound
  credential — the platform authenticator (Face ID / Touch ID / Optic ID)
  rather than a passkey that roams. An account without one is told so, never
  quietly dropped to a weaker tier: that would be the checkbox again wearing a
  signature's name.

  **The signature is over the package.** The envelope's challenge *is* the hash
  of the exact bytes, and `release()` **re-hashes the stored package** at
  release time — deliberately not the `document_sha256` column beside it, which
  was written in the same breath and would agree with itself however the row
  was edited afterwards. The first draft compared those two columns and a test
  caught it: the guarantee exists only because the check reads the real bytes.

  **Bound, and one-time.** `binding_kind="referral"` stops a valid assertion
  raised for something else being a skeleton key. The link opens once, and a
  second attempt says so rather than quietly working — a replayed link is
  something the patient should be able to discover.

  Matching filters on **expertise** and only *ranks* on geography (a
  cardiologist two streets away is not a substitute for a psychiatrist), and
  returns nothing rather than a near miss, because a confident wrong referral
  is somebody phoning a clinic that cannot help them. The package names the
  specialist as synthetic inside itself: a clinician reading a transcript
  should never have to work out which voice was a person.

- **The clinician writes back, and the profile is caught up** — 2 routes, 10
  tests. Opening the one-time link mints a **reply token** at that moment, so
  the summary link stays burnt while exactly one note can return. Open once,
  reply once. The note is sealed in the PDI vault under
  `qrme/{profile}/clinical/…` — the same treatment source material gets,
  content in the vault and only a key reference held locally.

  The point is the handover: somebody who has just seen a clinician should not
  have to retell the whole thing to the specialist, and the profile should
  already know where the matter stands.

  **It is deliberately not a `source_items` row**, which is the decision the
  rest hangs on. Source material is what a profile recalls *as its own*, and
  it is what `workflows._scoped_items` feeds to a `research` phase — a
  clinical opinion filed there could be recited as the profile's own knowledge,
  or drafted from into a letter. A test asserts it reaches neither.

  Instead it arrives in its own prompt block naming the clinician: *these are
  that clinician's words, not yours* — attribute them, never present them as
  your own assessment, never extend them into advice they did not give, and
  for anything they do not cover, say so and point back. Notes are scoped to
  (profile, interactor); another interactor talking to the same profile sees
  nothing, in the prompt or through the API.

## [0.2.2] — 2026-07-26

**A documentation release.** No code changed in any of the three products — no
new routes, no schema, no behaviour. Every entry below corrects something that
was *described* wrongly, which on this round turned out to be the thing costing
real time.

### Fixed

- **`POST /marketplace/seed` described itself as only skipping.** Its docstring
  — the text served in the OpenAPI docs, which is where anybody deciding
  whether it is safe to call actually reads it — said *"Idempotent —
  already-seeded profiles are skipped"*, and 0.2.1 made that only half true:
  the endpoint now also **repairs**, filling a missing portrait or appearance
  on a starter that already exists.

  The stale sentence had a cost. Someone looking at three starters rendering as
  bare initials would read that line and conclude the one call that fixes them
  could not possibly help, because re-seeding skips what is already there. No
  behaviour changes here — this corrects the description in all four places it
  was wrong: the endpoint, `qrme/seed.py`'s module and `seed()` docstrings, and
  the README's Starter Collection row.

- **Changelog release links stopped at 0.1.8.** `[0.1.9]`, `[0.2.0]` and
  `[0.2.1]` had headings but no link definitions, so three shipped versions
  rendered as literal `[0.2.1]` text, and `[Unreleased]` still diffed against
  `app-v0.1.8` — a three-release diff pretending to be an empty one.

- **The release checklist is why that kept happening.** `docs/releasing.md`
  step 1 said to move the `Unreleased` items and date the heading, and never
  mentioned the link definition at the bottom of the file — so the step was
  skipped three releases running by someone following the instructions
  correctly. Step 2 was wrong in the same direction: it named `pyproject.toml`
  and `app/package.json` when the version string actually lives in **five**
  places, the two extra ones being the `FastAPI(...)` call in `qrme/api.py` and
  the second root entry in `app/package-lock.json`. Both steps now say what
  they meant, in all three repositories.

## [0.2.1] — 2026-07-26

### Added

- **A help box on every screen** — `qrme/help.py`, 2 routes, 11 tests. Every
  screen here can be somebody's first: a beacon scan lands a stranger on a
  profile page, a shared link drops them into a room. Until now the only thing
  on any of those screens that could answer a question was **a synthetic
  profile** — the one thing that should never be answering questions about the
  product.

  So it is structurally **not a profile**. No name, no face, no memory. On a
  product whose whole subject is synthetic people who can be mistaken for real
  ones, a help assistant with a portrait would be a thirty-fifth character
  rather than the thing that explains the other thirty-four.

  **It never speaks as anybody.** *Are you real*, *pretend you are*, *what do
  you think of me* are caught **before any model sees them** and handed back to
  the profile on the page — the thing that actually has a persona, a
  relationship and a moderation pipeline. A test hands it a provider that
  raises if it is ever reached with one of those.

  **It writes nothing.** No path from this endpoint to a change — the same
  boundary as `marketplace.assist`, which suggests searches and never runs one.

  **It works with no model at all.** The answers are written prose, and that is
  the answer rather than an apology: a help system that stops helping during a
  provider outage is absent on exactly the day everything else is confusing
  too. The offline stub is explicitly *not* allowed to speak for it — "[stub
  reply in a warm tone]" is worse than the written sentence it would replace.

  Public, because requiring an account to ask *"what is this?"* gates the one
  question that arrives before an account exists. Drawn in the screen chrome
  and mounted outside the studio's tab switch, so "on all screens" is a
  property of the shell rather than something 79 screens each have to remember.

- **Screen 80 — the front page a visitor actually sees.** Screen 5 is the
  owner's view; this is the one a beacon scan lands on, so it leads with who
  this is: the real portrait with its burned-in mark, the name, the profession,
  the rating *beside its own count*, then skills, experience, and a review from
  somebody who talked to them. The help affordance is on it, like every other
  screen.

- **A profile has a front page** — `qrme/frontpage.py`, 3 routes, 12 tests. A
  profile had a name, a portrait and a persona; everything else a visitor might
  want was scattered. Skills lived as flat marketplace tags, "experience"
  existed only as prose buried in the persona, and the nearest thing to a
  review was a thumbs up/down on the `engagement` row that nobody could read.
  Somebody who scanned a beacon got a face, a sentence and a button.

  `GET /profiles/{id}/front` assembles it in **one call** — identity, headline,
  skills, experience, rating, reviews, and how many people have actually talked
  to it — because the caller is a scan page on cellular and five round trips is
  how a page arrives in pieces.

  **A review comes from somebody who was actually there.** It checks the
  `engagement` row for a real interaction, and `UNIQUE (profile_id, author_id)`
  makes a second review from one account impossible *in the schema* rather than
  in a check somebody could forget — reviews are edited, never stacked. Without
  both, a rating is worth exactly the number of accounts somebody can make. The
  average always reports its own `count`, because one five-star review and two
  hundred are different facts.

  **Experience about a real person is a credential.** On a `fictional` profile
  invented history is the point and the AI mark says so. On a profile depicting
  somebody real, *"twenty years at Accra General"* is a claim asserted on their
  behalf, so it is refused without the same rights basis the persona needed.

  **Nothing on the page outranks the mark.** It carries `avatars.render`'s
  watermark like every other surface; a five-star average is a well-liked
  synthetic profile and nothing more. Reviews are moderated on the way in, and
  a blocked one is kept, shown to its author with the reason, invisible to
  everyone else, and excluded from the average — the shape `qrme.audience`
  already uses for comments.

  The headline is **derived from the persona** rather than stored. A separate
  field is a second copy that starts agreeing with the persona and stops.

### Changed

- **The screens show real faces instead of a hologram.** Profile Home, Avatar
  Studio and Live Video drew `orb()` — a purple sphere with a generic person
  glyph — where the face belongs. The pixels were already in the repo: all 34
  starter portraits ride in `frames.PORTRAITS`, and exactly one screen used
  them, so the gallery showed a hologram of a profile whose photograph was one
  import away.

  **A rounded box rather than a circle, and not only for taste.**
  `tools/mark_portraits.py` burns the AI mark into the pixels at the
  *top-right*, so a circular clip of a square portrait cuts off the corner the
  disclosure lives in. The radius stays well inside it, so the mark survives
  into every screen that shows a face — which is the whole reason it was burned
  in rather than composited.

  Those screens name the character and their profession (`Marcus Bell` ·
  *retired fee-only financial planner*), both sourced from `seed.py` so the
  face and the name cannot drift apart. "AI assistant" stays where it belongs:
  the chrome that genuinely cannot know who is loaded.

### Fixed

- **Re-seeding repairs a starter that predates its portrait.** The seed is
  idempotent by @handle, and idempotent meant *do nothing* — so a deployment
  created before the portraits shipped was stuck showing **initials** on
  profiles whose faces are sitting in the package, and running the seed again,
  the obvious repair, did nothing at all. `POST /marketplace/seed` now fills a
  blank `avatar` or `appearance` on an existing starter and reports
  `repaired` alongside `created` and `skipped` — *"34 skipped"* on a
  deployment that just got 34 faces back is the kind of summary that hides the
  thing you wanted to know.

  Blank-only, so it is a repair rather than a reset: an owner who set their own
  portrait or wrote their own appearance keeps both.

### Changed

- **The assistant has no name any more.** "Ava" was a sample profile name that
  had quietly become the product's mascot: the studio's nav read *Chat with
  Ava*, the chat bubble's CSS class was `.ava`, the screen gallery said *People
  in Ava's life* and *Ava wants to reply*, the desktop frames said *Ava ·
  Online*, and the demo handle was `@ava.bianchi`.

  None of that is true of the product. A QRME profile is named by whoever
  creates it, so hardcoding one name in the chrome told every user their
  assistant was somebody else's. The chat screen was already right — it reads
  `session.profile.display_name` — so the name only ever lived in the parts
  that could not know it.

  Everything that cannot know the name now says **AI assistant**, and the
  message role is `assistant` rather than `ava`, which is what it always was.

  **Onboarding no longer pre-fills the name.** `useState("Ava")` put a name in
  the box, and a default in a box is the one most people never change — which
  is exactly how a sample name becomes a mascot. It is empty now, with
  *"Name your assistant"* as placeholder text.

  Screen 6 is `06-chat.svg` rather than `06-chat-with-ava.svg`.

### Fixed

- **The chat screen's online dot sat at a fixed x that assumed a three-letter
  name**, so "AI assistant" ran straight through it — found by rendering the
  screen rather than by reading the diff. The dot and its label are measured
  off the label now, so a longer name cannot overwrite the status.

## [0.2.0] — 2026-07-25

### Fixed

- **Two workflows were writing the release body, and only one of them was
  right.** `desktop-release.yml` published the release with
  `body_path: RELEASE_NOTES.md` — the file verbatim, *"Ready-to-paste body for
  the GitHub Release…"* preamble and all — while `sync-release-notes.yml`
  published the same file with that preamble stripped. Both fired on the same
  tag push. The sync finished in about six seconds; the installer build
  finished two to four minutes later and overwrote it.

  So the build always won, and every release since the sync workflow existed
  has shipped the maintainer preamble at the top of its notes until somebody
  re-ran the sync by hand. The de-duplication logic already in the sync
  workflow — *"several releases carry it twice from a body that was pasted over
  one that already had it"* — was scar tissue from this, treating the symptom.

  The build step no longer sets a body at all; it attaches installers and lets
  GitHub generate the changelog. `sync-release-notes` now triggers on
  `workflow_run` when that workflow **completes**, rather than on the tag push,
  so the curated notes are the last write by construction instead of by luck.
  It runs on a failed build too — a build that fails after creating the release
  is exactly when a wrong body is least likely to be noticed.

  [docs/releasing.md](docs/releasing.md) says to leave the release body empty
  and records who owns it, along with the other trap in this area: tag names
  are case-sensitive to `tags: ["app-v*"]`, so `App-v0.1.9` silently triggers
  nothing.

## [0.1.9] — 2026-07-25

### Added

- **The tandem doc describes the architecture that actually exists** —
  [docs/tandem.md](docs/tandem.md), and the same file byte-for-byte in all
  three repositories. It had drifted in three separate ways at once.

  **It was missing an arrow.** For most of this project's life one sentence
  covered the topology: every arrow points *into* PDI. PDI's gate agent broke
  that on purpose — it asks a QRME profile for the words it speaks at a door —
  and the document, the ASCII diagram and the section headings all still
  described the world before it. There is a `pdi ✕ qrme` section now, with the
  flow, the fallbacks, and why the model is the voice and not the decider.

  **Two of the three copies were stale.** JIM's and PDI's still described the
  suite gateway's erase, export, consent and metering as `[planned]` when
  `suite/gateway.py` had shipped them, and the docker-compose e2e harness as
  `[planned]` when it runs in CI. A reader in those repos was told cross-app
  deletion did not exist. The three copies are identical again.

  **The numbers were wrong.** *QRME 59, JIM 49, PDI 20 tests* against actual
  suites of 523, 293 and 177.

  Also new: a **beacon family** section, because three products now put a
  printed code on a physical thing and answer three different questions with
  it, and the shared rules (a scan is a page not JSON; a dead code and a code
  that never existed render identically; the page renders only what it was
  handed) were true in three places and written down in none.

- **The diagram is generated** — `tools/build_assets.py` now writes
  `docs/diagrams/tandem-flow.svg`, and the block that draws it is identical in
  all three repos so one picture cannot become three that disagree. It replaces
  a hand-drawn SVG that was cream-and-serif while every other asset in every
  repo is night-indigo, and that showed two arrows because it was drawn when
  there were two.

  The vault arrows name **what actually goes down them**. *"Medical payloads"*
  was true and incomplete: spending events, bank transactions, messages and
  location all ride the same wire, under the same consent gate, into the same
  `jim/{user}/context/…` namespace. A diagram — or a doc — naming only the
  medical half invites the reader to assume the rest is held somewhere else,
  and it is not. All four categories a person would be startled to find there
  now sit on the label's bold line together; putting two of them a row down in
  a smaller font would have re-made the same mistake more quietly. The QRME
  arrow got the same treatment, having been summarised to *"source material"*
  while also carrying rated placement earnings and adaptation runs.

- **Marketplace search: words, place, and a hand with the words** —
  `qrme/marketplace.py`, [docs/marketplace.md](docs/marketplace.md), 8 routes,
  23 tests. Browsing meant knowing the vocabulary: exact `kind`, exact `tag`,
  exact `area`. Fine if you know the tag is `legal`, useless if what you have
  is *"someone who can help me read a lease"*.

  **Place is not `area`.** `listings.area` was already taken and means a
  *subject* area — healthcare, finance, legal — so geography went into its own
  table. Folding them together would have made "near me" quietly mean "in
  healthcare", which looks like an empty marketplace and is very hard to see.

  **Nothing is sniffed.** No IP geolocation, no GPS, no address parsing. A
  seller types where they serve; a searcher types where they are. Location a
  user did not enter is location they did not agree to share. Localities are
  names, not points — there is no distance maths, which is a real limitation
  and also the reason there is nothing to leak.

  **A rated listing can never carry a place.** `set_place` refuses one, so no
  row exists, so no place filter can match it. That is
  [desks.md](docs/desks.md)'s line — where a performer physically is has
  nothing to do with browsing them, and a place filter is a way of asking —
  made structural instead of a check the next filter could forget.

  **Ranking is deterministic and says why.** Field-weighted, with `score` and
  `matched_on` on every result, so "why am I seeing this?" is answerable.
  `hidden_by_place` is reported rather than swallowed.

  **The assistant writes the search box and stops.** `POST /marketplace/assist`
  turns "I don't know what to search for" into two or three candidate
  searches, and returns **suggestions, never results** — there is deliberately
  no code path from it into `search()`. Same boundary as PDI's gate agent: a
  model can change what is in your box and nothing else, so everyone gets the
  same explainable ranking. It degrades to keywords when no model is reachable,
  so nobody is stuck behind a provider outage.

  Settings are **defaults, not a cage**: a typed locality always wins over a
  saved one. Three screens (77 Search & Place, 78 Marketplace Settings,
  79 Search Assistant).

### Changed

- The Starter Collection row said *33 fictional profiles* while the README, the
  avatars doc and the generated cover all said 34. Both were right —
  `@vivienne_sable` seeds the rated tier from `RATED` rather than `STARTERS` —
  and reading them together still looked like a contradiction. Named.

- **The README cover is generated now** (`tools/build_assets.py`) rather than
  hand-built. It had been drawn before live desks, beacons, the audience layer,
  the marketplace and the burned-in AI mark existed, and was still advertising
  the 0.1.0 product four releases later — in amber on navy, while every screen
  in `docs/screens/` is night-indigo with neon purple.

  It now reads its palette from the same constants the screens use, so it
  cannot drift away from what it is a picture of, and names what actually
  shipped: 34 starter profiles, live desks, desk beacons, the audience layer,
  the marketplace, gifts. Regenerate with `python3 tools/build_assets.py`.

  The other sixteen files in `assets/design/` are **deliberately untouched** —
  no README or doc references any of them, so they are an orphaned illustration
  library rather than something going stale in public.

### Fixed

- **An unknown button kind rendered as a faint outline and said nothing.**
  `docs/screens/build.py`'s `button()` fell through to `ghost` for anything it
  did not recognise, so a screen's primary action could silently lose its
  fill — valid SVG either way, which is exactly why only the generator can
  catch it. It now raises on an unknown kind. Found by rendering two new
  screens and looking at them.

## [0.1.8] — 2026-07-25

### Added

- **Two ways into a live room, and they are not the same act.** Watching and
  commenting is something a viewer does; appearing *on* the stream is something
  the host lets them do. `POST /desks/{id}/join` now takes `mode`:
  `audience` joins immediately, while `guest` **only asks** — it returns a
  pending request rather than a room, because a join that behaved as though the
  request had been granted would be the worst possible default.

  Coming up needs an **account**, since the host is deciding about a person
  rather than an anonymous request, and on a rated desk a **verified adult**,
  because a guest there is someone *going live* on an 18+ stream rather than
  merely watching one. One hand up at a time, so a host reading the queue sees
  people instead of repeats; a decision is made once; and a guest can always
  step back down without asking, because needing permission to *stop* being on
  camera would be the wrong way round. The queue is owner-only — who asked to
  appear on someone's stream is theirs to see.

- **`GET /desks/{id}/overlay` — what renders over the video.** Recent comments,
  likes, shares, gifts and whoever is currently up, defined in one place so
  every client draws the same layer instead of each inventing its own. A live
  stream's reactions belong on top of the picture because that is where the
  viewer is already looking, and on a stream whose entire premise is an empty
  chair with a bell, the reactions *are* the room. The plate behind each line is
  transparent so the room stays visible through it; the text on it is not faded,
  because chat you have to squint at is chat nobody reads.

### Changed

- **The screens show what they had been describing.** The galleries covered
  every capability through 0.1.5 and then stopped, so live desks, desk beacons,
  the audience layer, commerce and signatures had no screen at all. Eight new
  mobile screens (69–76) and three desktop views (07–09) close that, and the
  desktop sidebar gains **Desks** and **Signing**.

  Three of them carry the **real camera frames** — the photographs that ship as
  `qrme/assets/desks/*.webp`, embedded as base64 rather than linked, because an
  SVG rendered through an `<img>` tag cannot fetch external files and a relative
  path renders as an empty box. The signs in them are the feature: *ring bell
  for service, away from the desk*, and *be back soon or ring bell*.

- **The starter collection is visible instead of described.** All 34 portraits
  now appear in the README, in [docs/avatars.md](docs/avatars.md) beneath the
  briefs that specify them, and as a grid on the Starter Collection screen —
  which previously said "seeded with faces" and drew icon chips. None of those
  galleries carries a badge of its own: the AI mark is burned into each
  portrait's own pixels, so it survives a screenshot, a hotlink or a crop and
  travels into every page that shows one. That is the property that made
  burning it in worth doing rather than drawing it at render time.

### Fixed

- **`[0.1.5]` and `[0.1.6]` linked to releases that do not exist.** Both
  versions were cut — changelog, notes, version bumps — but their `app-v*` tags
  were never pushed, so those two entries pointed at 404s. They now point at
  their release-prep commits. Deliberately **not** fixed by backfilling the
  tags: pushing them now would fire the installer build and publish v0.1.5 and
  v0.1.6 releases *dated after* v0.1.7, putting superseded installers at the top
  of the page people download from. [docs/releasing.md](docs/releasing.md)
  records that reasoning, because an unexplained gap in a tag sequence is
  exactly what someone later "fixes" without knowing why it was left.

## [0.1.7] — 2026-07-25

### Added

- **Gifts, and buying things on the marketplace.** Round 2 of the audience
  work, and it starts by fixing something the first round turned up: `listings`
  had no price and no purchase endpoint at all, so a product could be listed
  and bought by nobody. Packs and licences had priced purchase; listings never
  got it.

  **A listing is a shop window; an offer is what makes it a shop.**
  `POST /marketplace/listings` needs no token and never has, so anyone can
  create one naming any provider — harmless while listings were discovery-only,
  and not harmless the moment a price could attach. So price and seller live in
  a separate `listing_offers` row that only a token-holder can write, and the
  seller comes from that token rather than a request body. A listing with no
  offer cannot be bought, not by a check that could be forgotten but because
  there is nowhere for a price to be. Buying confirms `accept_price` against
  the offer, an order copies the title it was bought under (a receipt that
  changes when the seller edits the listing is not a receipt), and withdrawing
  an offer keeps both the shop window and past receipts. Buying your own
  listing is refused — it would credit you with your own money and inflate the
  sales count at once.

  **A gift is not a small purchase.** It sends money to a person and receives
  nothing, which is exactly the shape livestream tipping keeps turning into a
  way to take money from people who should not be spending it. So the giver
  must be a **verified adult** whoever they are gifting — an account with no
  birthdate is refused, because an unverified age is not evidence of an adult —
  a single gift is **capped**, a rated desk runs its own 18+ gate on top (the
  two answer different questions), and the beneficiary is read from the subject
  rather than named by the giver, since a body-supplied one would let anyone
  route a performer's gift into their own balance. Every gift states
  `refundable: false` at the point of giving rather than in a policy page.

  Money remains **simulated**, as everywhere else here: real rows on the
  creator's statement under `listing_sale` and `gift`, settling through the
  same payout sweep as pack sales and licence fees, with no real funds moved —
  and every money-bearing response says so in its own body.
  [docs/commerce.md](docs/commerce.md) states plainly what this is *not*:
  running spend totals, cooling-off, parental controls, a real identity check
  behind "verified adult", chargebacks, and payout compliance are all absent.
  That list is written down rather than omitted because a half-built safety
  feature that looks whole is worse than an obviously missing one.

- **The audience layer — like, comment, share, subscribe.** What a viewer does
  *other* than talk, on a profile, a live desk, a room message or a marketplace
  listing. Targets are a `(kind, id)` pair rather than a column per thing,
  because the same four verbs on four surfaces would otherwise have become four
  near-identical tables that drifted apart within a round.

  **A like is a fact, not a counter** — `reactions` is UNIQUE on
  `(target, actor)`, so liking twice is idempotent and reports
  `was_already_liked` instead of erroring. A plain integer column would let one
  account manufacture popularity by calling an endpoint in a loop, which makes
  every number on the platform meaningless rather than just that one. That is
  also why a like needs a token: a like from nobody in particular is a number
  anyone can produce.

  **A comment is authored text, so it is filtered like authored text** — the
  same moderation pipeline as a chat turn, at *the target's* maturity setting
  rather than the commenter's, since a comment lands under someone else's name.
  A blocked comment is kept, returned to its author with the reason, and shown
  to nobody else; the endpoint answers 201 because the comment was accepted and
  recorded, and what happened to it is in `status`. Blocked comments are not
  counted.

  **Sharing is gated at the far end, not at the sharer** — no token needed,
  including for a rated target, because the link lands the recipient on the age
  wall regardless of who sent it. Refusing the sharer would be gate theatre.
  Shares record the actor when there is one: "shared 40 times" and "shared 40
  times by one account" are different facts.

  **Subscriptions are two tiers on one row** — a free `follow`, and a `paid`
  tier that credits the creator's ledger each period alongside pack sales and
  licence fees. Paid requires `accept_price` to match, the same explicit consent
  priced packs use and for a sharper reason: a recurring charge a viewer did not
  mean to start *keeps* costing them. **Nothing bills on a timer** — the first
  period is charged on subscribe and later ones by an explicit
  `POST /subscriptions/{id}/renew`, so a deployment left running accrues nothing
  unseen. Cancelling keeps the row so a lapsed subscriber stays distinguishable
  from someone who was never there, and re-subscribing reuses it. Money is
  simulated exactly as it is elsewhere here, and every subscription response
  says so in its own `billing` field rather than leaving it to a policy page.

  A rated target keeps its gate on **every** verb, running the deployment's
  existing verified-adult check rather than a second implementation of it. The
  test asserts across all five surfaces in one loop, because a gate remembered
  on four of five is exactly the kind that ships. `GET …/audience` is
  deliberately not called `engagement`: that word already means the
  per-relationship EMA score, and two different numbers under one word get read
  as one.

- **A live desk can be left behind as a printed code.** A profile beacon and a
  desk beacon are the same gesture aimed at opposite things: scanning the first
  reveals somebody who does not exist, and the page marks the portrait *AI*;
  scanning the second reveals somebody who does, and the page must not say
  otherwise. `POST /desks/{id}/beacons` prints one, `GET /d/{id}` is what a
  phone's camera app opens, and `GET /d/{id}/card` is the same scan as JSON for
  the native overlays. The sticker on the shop door is arguably the more
  natural of the two — it is there *because* nobody is behind the desk right
  now, which is exactly what the bell was built for, and the scan page carries
  a working one.

  The badge is inverted and deliberately unlike the AI mark at a glance —
  **Live person — not AI**, green and top-right against the mark's neutral
  bottom-left — because absence of the AI mark is not a disclosure on its own:
  an unmarked card could be a synthetic profile whose badge got dropped. The
  page states the claim positively and names who vouched for it.

  Two consequences of the scanner being a stranger with no account, neither of
  them a gap: their ring is **anonymous**, so it takes the 30-second per-desk
  cooldown rather than the 5-minute per-caller one, because a printed code is
  reachable by anyone walking past; and a **rated desk always shows them the
  age wall**, since there is no token on a sticker scan that could clear it.
  That wall withholds the name and, above all, the location — whereabouts on an
  adult listing is a safety matter and a sticker is by definition somewhere
  physical. Placing a beacon is owner-only, because anyone who could print a
  code for a desk they do not hold could put a stranger's name and whereabouts
  on a sticker and put it anywhere.

  Stored in its own `desk_beacons` table rather than as a nullable `desk_id` on
  `beacons`: that column is `NOT NULL` on every database already out there, and
  the schema is applied with `CREATE TABLE IF NOT EXISTS`, so widening an
  existing table would only ever take effect on a fresh one.

- **Windows signs now, through the browser engine rather than interop.** The
  blocker was `webauthn.dll`: several hundred lines of version-sensitive struct
  marshalling that a compile cannot meaningfully check and nothing here can
  execute. Edge already implements WebAuthn and already talks to Windows Hello,
  so the desktop app hosts a **WebView2** pointed at a new
  `GET /signatures/ceremony` page, served from the deployment's own origin —
  WebAuthn refuses a mismatched relying party, and an opaque origin has none to
  match, which is why it is a route and not a string inside the C#. The page
  runs `navigator.credentials`, posts the raw assertion back over the WebView2
  message channel, and the app makes the authenticated call; **the page never
  sees a token**, because a bearer token in a query string ends up in logs and
  history. It shows the document before the prompt for the same reason the
  native screens do.
- **`portrait_marked` on the beacon card.** `asset_marked` existed on the
  avatar response and nothing consumed it. The camera overlays are the surface
  that most needs it: a shipped starter's portrait carries the AI mark in its
  own pixels, an owner-attached asset is somebody else's file and cannot be
  vouched for, and a surface QRME does not control has to be able to tell those
  apart. QRME's own overlays still draw their badge either way — theirs carries
  the profile's designed label and is real text, not pixels.

### Changed

- **The three products are now cut as one release** — documented in
  [docs/releasing.md](docs/releasing.md), and in JIM-mini's and PDI's copies of
  the same file. Same number, same pass, even when a repository has nothing of
  its own to ship that round; an empty round says so in those words rather than
  being padded. Through v0.1.5 each repository cut whenever it happened to have
  work, so the numbers matched only by coincidence — which is how QRME reached
  0.1.6 alone. The doc also writes down the trap that follows: tag the
  release-prep commit rather than the tip of `main`, because work keeps landing
  while a release is cut and anything arriving after the changelog is sectioned
  belongs to `[Unreleased]`, not to the version being tagged.

## [0.1.6] — 2026-07-25

### Added

- **The starter collection has faces.** All 34 portraits ship as files in
  `qrme/assets/portraits/`, served at `/portraits/{handle}.webp` and attached
  to each starter by `seed.py`. Until now the briefs described portraits that
  did not exist, so every starter fell back to initials — including on the
  beacon page and in the camera overlay, which is the first thing a stranger
  ever sees. 512×512 WebP, declared as package data so they survive
  `pip install` rather than existing only in the repo. `avatars.STYLE` is
  rewritten to describe the treatment that actually shipped (a monochrome cyan
  hologram, not the warm-lit photographic look originally specified), because
  a shared style whose text disagrees with the assets cannot do the one job it
  exists for; the rated portrait carries its own `RATED_STYLE`, since it is
  age-walled off every surface the others appear on.
- **Live desks** (`qrme/desks.py`, `/desks/*`, [docs/desks.md](docs/desks.md))
  — a real person offering a service, behind the same surfaces as a synthetic
  profile and with the one difference that matters: **a desk never carries the
  AI watermark.** Marking a real human is not a cautious default, it is a false
  statement about them, and the test suite pins both directions of that rule in
  one file so neither can be relaxed quietly. Absence of a mark would be
  ambiguous on its own, so the claim is positive — *Live person — not AI* —
  with the attestor, the basis, and the word **recorded** rather than *proven*
  shipped next to it; a desk cannot be opened without saying who vouches, and a
  `high`-tier signature bound to the desk raises the claim to something a
  counterparty can check. What a visitor looks at is a camera view of the desk
  rather than a portrait, since we have no photograph of the person and do not
  go looking for one; with no camera configured the card reports
  `feed.live: false` and the clients say **SAMPLE VIEW**, because presenting a
  still frame as live would be the same class of lie. And the sign on the chair
  says to ring the bell, so **iOS, Android and Windows all carry the button** —
  no token, because the person in front of an empty chair is exactly the one
  without an account, and rate limited, because a bell anyone can ring from
  anywhere is a doorbell prank waiting to happen. An **18+ stream** is the same
  desk behind the deployment's existing verified-adult gate rather than a new
  tier or a second, weaker check: unverified callers get an age wall carrying
  existence and nothing else — no name, no view, and no location, which stays
  withheld even past the wall — and the view, the bell and joining all take the
  same token. Only the performer can open one, because the repo's standing rule
  that adult mode is never available for a profile of another real person lands
  here as *the attestor must be the owner, attesting for themselves*. The AI
  mark is off on both sides of the wall. `POST /desks/{id}/join` returns the
  room whoever is watching shares, minted on first arrival.
- **The AI mark is burned into every shipped portrait.** The disclosure
  already rode alongside a portrait — `GET /profiles/{id}/avatar` returns it,
  and the beacon page and both camera overlays composite it — which covers
  every surface QRME controls and none of the ones it does not.
  `/portraits/{handle}.webp` is an ordinary file URL: hotlink it, embed it,
  scrape it, screenshot it, and a composited badge survives none of that. The
  mark now sits in the pixels, top-right, where every composited badge is
  bottom-left so the two never collide. Burned offline by
  `tools/mark_portraits.py` rather than at request time — that would put an
  imaging library in the runtime dependencies and redraw a constant on every
  fetch — and pinned by a SHA-256 manifest the test suite checks, so a
  portrait swapped for an unmarked one fails CI instead of shipping quietly.
  `asset_marked` on the avatar response tells a surface QRME does not control
  whether compositing is mandatory; an owner-attached asset always reports
  `false`, since nothing here can vouch for someone else's file.
- **The native apps sign.** iOS/visionOS drive the ceremony through
  `ASAuthorizationPlatformPublicKeyCredentialProvider` (Face ID, Touch ID, or
  Optic ID) and Android through Credential Manager, so the private key stays in
  the Secure Enclave or StrongBox and the app never handles it. Both render the
  document immediately before the prompt and send that exact text to the
  server — the mitigation for WebAuthn having no trusted display, since the
  prompt itself can never say what is being signed. Both also need a verified
  domain (associated domains on iOS, Digital Asset Links on Android) before any
  prompt appears, which a LAN dev server cannot have; the screens say so rather
  than failing with a system error nobody can read. **Windows reads and
  verifies but does not sign**: reaching Windows Hello means `webauthn.dll`
  struct marshalling that a compile cannot meaningfully check, and a signing
  button that looks like it works and does not is worse than no button — so the
  desktop app carries the half that needs no authenticator, including a paste
  box for verifying a package a counterparty handed you.
- **Signatures that survive being disputed** (`qrme/signatures.py`,
  `qrme/webauthn.py`, `POST /signatures/*`). The gesture is the same Face ID
  prompt; what comes back is a WebAuthn assertion rather than a boolean —
  signed by a key in the Secure Enclave that the app never sees, over a
  challenge that **is** the SHA-256 of a canonical payload naming the document
  hash, the stated meaning, the signer, and an expiry. Change one byte of the
  document and verification fails. `userVerification: "required"` makes the
  biometric mandatory rather than a presence tap, an envelope signs once,
  and an assertion made for one document is refused for another. Proofing
  level is recorded at enrollment and enforced per tier, so a self-asserted
  credential cannot sign a care handoff; syncable credentials (`be`/`bs`) are
  reported and barred from the top tier, because a key present on every device
  in a cloud account is a weaker claim of exclusive possession. The evidence
  package copies the public key, so revoking a passkey never retroactively
  unmakes what it signed, and `POST /signatures/verify` checks a package with
  no token and no lookup — a counterparty should not have to trust this
  deployment. Every package ships its own limits attached, including that
  WebAuthn has no trusted display. Adds `cryptography` as a runtime
  dependency: a module that parsed assertions without verifying them would
  produce records that only *look* like evidence.
- **The in-camera beacon overlay on Android** (CameraX + ML Kit), matching the
  iOS scanner: point the phone at a sticker and the profile is drawn on the
  code in the live viewfinder, tracking it as the phone moves. ML Kit reports
  in the analysis image's coordinate space, which is rotated and differently
  sized from the view, so the box is mapped through the preview's
  `FILL_CENTER` transform before anything is drawn — without that the portrait
  lands where the sticker is not. Resolution is guarded by beacon id and an
  in-flight flag, since the camera delivers ~30 frames a second and every one
  sees the same sticker. The barcode model is bundled rather than downloaded
  on demand, so the first scan works without Play Services fetching anything.

### Fixed

- **The signing flow in both mobile apps could never succeed.** iOS and
  Android each enrol a passkey at `self_asserted` — all the screens can do —
  and then immediately requested the `standard` tier, which needs `federated`
  proofing or better. Every attempt died at the server with a 422. The tests
  missed it because they all enrol at `document` level, so none of them walked
  the sequence the clients actually perform; there are now tests that do. Both
  apps default to `basic`, and say plainly that the higher tiers need an
  identity check a passkey alone does not provide.
- **A credential's proofing level could never change.** `docs/signatures.md`
  said a user re-proofs and the new level applies from that moment forward, and
  nothing implemented it — so every credential was stuck at whatever it
  enrolled with, permanently. `POST /signatures/credentials/{id}/proofing`
  records a fresh check. It applies going forward only: a signature already
  made copied its level into the evidence at signing time, so raising the
  credential today cannot quietly upgrade what it signed yesterday.
- **The WebAuthn deployment variables were undocumented.** `QRME_RP_ID` and
  `QRME_RP_ORIGINS` shipped with the signature scheme and appeared in no table
  anywhere, so an operator had no way to learn that leaving `QRME_RP_ID` at its
  default makes every signature on a real deployment fail as *"made for a
  different site"* — a server-side refusal that reads like a client bug. Both
  are in the README's environment table now, with `QRME_CONSOLE_DIR` and
  `QRME_CORS_ORIGINS`, which were also read but never written down; and
  `docs/signatures.md` gains the deployment section that says what the domain
  itself has to serve.
- **A desk's camera could never be turned on.** `feed.live` was read from a
  column no endpoint could write, so the live branch was unreachable and every
  desk was a sample view for ever. `PUT /desks/{id}/camera` sets it, and only
  the desk's own token can — a camera on a person is not something a platform
  switches on for them.
- **The mug says nothing, as the brief asked.** `bev_lindqvist`'s portrait had
  the word "nothing" lettered onto it — a literal reading of "a mug that says
  nothing at all", and the one piece of baked-in text in the collection that
  was not deliberate. Painted out, with the mug's own shading preserved.
- **The portraits were sliced on the wrong boundaries.** The contact sheet was
  cut on a nominal 192px grid, but the subjects overrun their cells, so several
  tiles carried a sliver of the neighbouring portrait — most visibly Otis's arm
  in Bev's frame. Re-sliced on the quietest column near each seam, which is
  where the real gutter is. `dr_priya_nair` is also re-cropped: her source is a
  wide landscape scene, so a full-width cut padded her down to a thumbnail
  inside her own tile.
- **A beacon card's portrait is now an absolute URL.** `GET /b/{id}/card` was
  returning the stored asset path unchanged, which is a valid `href` only for
  a browser already on the origin — and the consumer of that field is a native
  overlay building a `URL` from the string. It worked while every portrait was
  an absolute test URL and would have broken the moment real assets landed on
  a relative path, which is this release.

### Documentation

- **[docs/signatures.md](docs/signatures.md) — the reasoning behind the
  above**, and the part that is not code: why the obvious `evaluatePolicy`
  version fails, the identity-proofing ladder, the evidence package,
  Optic ID on Vision Pro and the cross-device hybrid path for headsets that
  expose no platform authenticator, and per-product bindings for care
  handoffs, BAA execution, key release, and likeness releases. Recommends
  **ESIGN/UETA** grade with 21 CFR Part 11 as a configuration change rather
  than a rewrite — HIPAA does not require Part 11, and JIM's terms already
  state the product is not a medical device. Ends with what the scheme does
  *not* prove, including the absence of a trusted display: WebAuthn cannot
  attest to what appeared on the screen, and the mitigation is signing on a
  second device rather than a claim that it can.

## [0.1.5] — 2026-07-25

### Added

- **Published deployments** — `QRME_PUBLIC_URL` makes `GET /pair` advertise
  the deployment's public address (QR included) instead of a LAN address, so
  the phone flow works hosted or local from one code path. `QRME_SIGNUP_KEY`
  gates profile creation behind an `x-signup-key` header so a published
  instance stays the operator's rather than open registration; unset leaves
  LAN use exactly as it was, and talking to a profile stays public either way.
- **Deployable as one container** — a two-stage `Dockerfile` builds the studio
  and installs the API into a single image, so a hosted instance serves UI and
  API from one origin exactly as the phone flow does. Runs as a non-root user,
  keeps the database on a `/data` volume, honours `$PORT`, and reports health
  at `/health`. [docs/hosting.md](docs/hosting.md) covers the operator side:
  the two postures (local vs published), why TLS isn't optional, what hosting
  profiles for other people commits you to, and — stated plainly — what the
  deployment does *not* give you (no multi-tenancy, rate limiting, or backups).
- **The Cloud Model Gateway server** (`cloudgw/`, `python -m cloudgw`) — the
  other end of a contract that until now only had clients and fakes. Serves
  `POST /v1/generate`, `GET /v1/model`, and the contribution intake with
  revocation by anonymous ref. One operator-configured model (stub without a
  key, and it says so in `/v1/model` and `/health` rather than passing itself
  off as a hosted tier); bearer token per contributing deployment so the
  intake records *which* one contributed; fail-closed off-machine when no
  tokens are set. Contributions seal into PDI as an ordinary tenant — and
  with no vault configured they are **refused**, never written somewhere
  unencrypted, while inference keeps working. The intake screens for
  identifying fields at any depth, product-shaped ids, and email addresses,
  and answers 422 naming the field instead of sanitizing: a quiet strip would
  hide the client bug that leaked it.
- **Beacons land on a page, not on JSON** — a beacon's QR used to point at
  `/summon?ref=…`, so a stranger who scanned a sticker got a wall of braces.
  `GET /b/{beacon_id}` is the page that should have been there: one
  self-contained document (inline CSS, no scripts, no font fetches — it opens
  in a camera app's in-app browser, on cellular, from a cold start), the
  portrait rising into view, and one way in. The AI mark is rendered **on the
  portrait** rather than in the chrome, because a stranger who screenshots it
  should carry the disclosure with the image — someone in the studio knows
  they are looking at a synthetic profile; someone who scanned a sticker in a
  bathroom does not. A picked-up beacon says so plainly instead of erroring,
  and a rated profile shows an age wall carrying no name and no face.
- **Shared-room beacons** — a beacon placed with `mode: "room"` mints a room,
  and everyone who scans that code lands in the same conversation rather than
  each in a private thread: a class, a workshop, a meeting, an AA table. The
  page says so before anyone types, since "others may be here" is not
  something to discover afterwards. `docs/beacons.md` covers placement, and
  pairs starters with the places their codes make sense.
- **See who the sticker is without leaving the camera** — point the QRME iOS
  app at a beacon and the profile appears *on the sticker*, in the live
  viewfinder. Vision reads the code, `GET /b/{beacon_id}/card` answers a
  compact payload, and the portrait is drawn on the quadrilateral Vision
  reported so it tracks the sticker as the phone moves. The AI mark comes from
  the same payload as the face and is drawn in the same view, so the two
  cannot come apart. A rated beacon's card carries `age_wall` **alone** — no
  name, no portrait — because an overlay renders whatever it is handed, so the
  withholding happens at the source. Note the boundary honestly: a *stock*
  camera app can only open a URL, which is the whole of the API surface a QR
  exposes to a third party; drawing over a viewfinder requires owning it.
- **The native apps are compiled in CI** (`.github/workflows/native.yml`) —
  iOS via XcodeGen + `xcodebuild` on macOS, Android via `gradle
  assembleDebug`, Windows via Visual Studio's MSBuild (not `dotnet build` —
  the Windows App SDK's PRI packaging task ships with VS and is absent from
  the standalone .NET SDK at every version). Until now the Swift, Kotlin and
  C# had never been through a compiler here at all: they were checked by
  reading and by brace/XML well-formedness, which catches a typo and nothing
  else. It found five real defects on its first runs. All three steps
  re-surface the actual compiler diagnostics on failure, since Gradle prints
  Kotlin errors above its `FAILURE` block and MSBuild scrolls them past the
  per-project noise — a red run used to report an exit code and nothing more.
  Compile only — signing and packaging stay in the release workflow — and it
  runs only when `native/` changes, since macOS runner minutes are not free.
- **Profile portraits** — `GET /profiles/{id}/avatar` returns the asset, the
  profile's AI watermark, and the likeness record as one shape, so 2-D, 3-D,
  VR and AR surfaces composite the badge rather than deciding whether to; a
  profile with no portrait reports `placeholder` instead of an unbadged image.
  An invented likeness reports no rights holder; a real person's face reports
  the recorded grant, its attestor, and that it is revocable. Art direction
  for the whole starter collection ships in `qrme/avatars.py` and is served
  generation-ready at `GET /avatars/briefs`, with each brief carrying its own
  constraints (invented person, no trademarked costume) so they survive being
  pasted elsewhere. The starter briefs double as each profile's `appearance`,
  so the face and the voice describe the same character — and the three
  mental-health profiles are marked `sombre` and played straight.
- **A rated starter** — `@vivienne_sable` seeds the 18+ tier so it isn't an
  empty shelf either. Fictional by necessity: adult mode is never available
  for a profile of another real person, and a starter ships everywhere. Every
  discovery surface age-walls it exactly as before — it is absent from public
  browse entirely.

## [0.1.4] — 2026-07-24

### Added

- **`python -m qrme` launcher** — bare invocation prints the menu of
  every way to run QRME, one command each, so users choose their device:
  `phone` (builds the studio if missing — npm install included on first
  run — prints the pairing URL with a scannable QR drawn straight into
  the terminal, serves on the local network; flags `--port`, `--rebuild`,
  `--no-build`, `--print-only`), `desktop` (the Electron app on this PC,
  or a pointer to the packaged installers when npm is absent), and
  `serve` (the headless API alone, `--host`/`--port`). Same backend,
  data, and token checks in every form.

## [0.1.3] — 2026-07-24

### Added

- **Run it on your phone** — the API serves the built studio at `/app`, so a
  phone on the same Wi-Fi opens QRME with nothing to configure (one origin
  for UI and API, so no CORS and no "which host?" step). `GET /pair`
  resolves this machine's local-network address and returns the URL to open
  — with `GET /pair/qr.svg` as a scannable QR and a pairing card in the
  Control Center. Installable as a PWA (manifest, icon, standalone display,
  app-shell service worker that never caches API traffic), with a phone
  layout: the sidebar becomes a bottom tab bar, 16px inputs so iOS doesn't
  zoom, and safe-area insets for the notch and home indicator.

## [0.1.2] — 2026-07-24

### Added

- **Watermarking on every AI render** — all AI-generated work, textual or
  visual, is stamped with a verifiable credential and a visible mark:
  chat turns (including proactive check-ins and farewells), posts, room
  turns, game and robot lines, creative works, proofreads, perception
  guidance, and task outputs. Owners **design their profile's watermark**
  (mark + label, `PUT /profiles/{id}/watermark`, editors in all three
  native apps); the design rides on every render, always displayed, and
  the AI designation is invariant — it cannot be designed away. The
  native apps show the mark on chat bubbles and post cards.
- **Terms of Service** (docs/terms.md, served at `GET /terms`) — assumption
  of risk and release, no-professional-advice and emergency disclaimers,
  warranty disclaimer, liability cap, indemnification, creator
  responsibilities, 18+ terms, and simulated-commerce notice. Profile
  creation records the accepted version + timestamp (clickwrap with a
  server-side receipt); an explicit refusal is refused (403); all three
  apps display the agreement at the create screen.

- **Synthetic-media watermarking** — public posts and non-text chat
  modalities are stamped at creation with a verifiable credential
  (producer, SHA-256, issue time, disclosure); public verification via
  `GET /watermarks/{id}` and `POST /watermarks/verify` catches altered or
  substituted media.
- **macOS notarization wiring** — hardened runtime + entitlements +
  `notarize` in the electron-builder config, so adding the Apple secrets
  produces a fully notarized, Gatekeeper-clean build; docs/releasing.md
  now walks through obtaining the macOS and Windows certificates.

## [0.1.1] — 2026-07-24

### Added

- **First-run onboarding screens** — provider login (Apple / Google / email),
  identity & age verification, access permissions, Avatar Studio, immersive
  AR/VR chat, live video, and an "all set" summary, in iOS and Android chrome.
- **Native iOS / Android / Windows apps at full parity** — Chat, Community
  (stranger matchmaking incl. the verified-18+ rated tier, multiparty rooms),
  Connect (social platforms + connected apps), Robots, Knowledge Excursions,
  Reach (summon @handle + QR beacons, marketplace, licensing, **earnings**),
  Settings (model picker, objections, **steering hub**, **relationship**,
  feedback), and Gaming — every backend surface reachable from every client.
- **LLM provider choice** per profile (Claude / OpenAI / Grok / Perplexity /
  Gemini, offline stub fallback) and **safe knowledge excursions** (study a
  topic without leaking private data).
- **Robotic embodiment** — bind catalog robots as physical bodies, per-kind
  command allowlists, robot task packs; **watch remote** — agents, profile,
  and robots on the wrist with green/orange/red lights and remote actions.
- **Steering** (not piloting) — throttle/behavior/intimacy dials that shape
  how a profile comes across, unified in a hub with age + appearance; rides
  on every surface and embodiment.
- **Marketplace growth** — starter collection (30 industries + wellbeing trio),
  knowledge packs, robot task packs, federated pack registries, creator
  ledger with payouts; **rated placement** (18+ venues, age wall at the
  source) with commerce gating, per-venue analytics, **placement earnings**,
  and **PDI-sealed placement custody**.
- **Third-party objection & revocation flow** (audit + memorial/succession),
  per-profile **language & provenance**, translate-anything, gateway language
  choice; **smart-glasses connectors** and **agent-operated gaming
  companions**; in-app **"Help us improve" feedback**; **suite smoke** — one
  command proves the whole tandem stack.
- **Chrome localization** — the apps' own tab/nav labels and common actions in
  all 10 supported languages — plus pull-to-refresh and refresh actions.
- `GET /health` — service liveness with tandem flags (the front-ends
  previously probed `/openapi.json`).

### Fixed

- CI collected zero tests (`tests/` was not a package and a fragile
  `find_spec` guard crashed collection); the suite now runs identically in CI
  and locally.
- Two text-overflow issues on the onboarding screens.

## [0.1.0] — 2026-07-21

First public release. QRME is the AI synthetic-profile platform of the
three-product suite (with [jim-mini](https://github.com/davidsbianchi1984/jim-mini)
and [pdi](https://github.com/davidsbianchi1984/pdi)).

### Added

- **Profiles & relationships** — create self / third-party (consent-gated) /
  fictional profiles with age & identity verification; relationship-aware
  behavior (`PUT /profiles/{id}/relationships/{interactor}`) and
  engagement-based style adaptation that never moves identity or boundaries.
- **Memory & moderation** — per-(profile, interactor) memory; every reply
  passes moderation, with an optional owner approval queue.
- **Lifecycle** — aging, succession (`/succeed`), memorial state
  (`/memorial`), graceful sunset (`/sunset`), and a full objection / takedown /
  appeal flow (`/objections` + `resolve` / `withdraw` / `attest`).
- **Summoning** — `@handle`, `#tag`, and QR beacons (`/summon`, `/beacons`,
  `/profiles/{id}/handle`).
- **Marketplace & licensing** — listings, ownership transfer, training-data
  licensing, and derivable specialist agents.
- **Assistant & perception** — compose / proofread / triage helpers,
  embodiments, workflows, and proactive outreach with user-set quiet hours.
- **Cloud model** — optional greater-model gateway with automatic local
  fallback and opt-in, individually revocable contributions.
- **PDI tandem** — seal source material and fine-tune artifacts in the
  encrypted vault; erasure purges the vaulted keys.
- **Data ownership** — full export and complete erasure at any time; bearer
  capability tokens stored only as SHA-256 hashes.
- **Suite gateway** (`suite/gateway.py`) — one origin fronting all three
  products, unified sign-on, and a stateless cross-cutting control plane:
  suite-wide erase (with receipt), export, centralized vault-sealed consent,
  and usage metering.
- **Apps** — a runnable React + Vite + Electron desktop console and mobile
  screen designs; a suite launcher; CI that smoke-builds the front-ends and a
  per-OS installer release workflow.

[Unreleased]: https://github.com/davidsbianchi1984/qrme/compare/app-v0.16.0...HEAD
[0.19.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.19.1
[0.19.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.19.0
[0.18.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.18.0
[0.17.0]: https://github.com/davidsbianchi1984/qrme/commit/c0c2544
[0.16.0]: https://github.com/davidsbianchi1984/qrme/commit/ed3d9c8
[0.15.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.15.0
[0.14.5]: https://github.com/davidsbianchi1984/qrme/commit/7928b5a77c95617970acb5cc656038d2973c4fd7
[0.14.4]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.14.4
[0.14.3]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.14.3
[0.14.2]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.14.2
[0.14.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.14.1
[0.14.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.14.0
[0.13.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.13.1
[0.13.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.13.0
[0.12.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.12.0
[0.11.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.11.1
[0.11.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.11.0
[0.10.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.10.0
[0.9.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.9.1
[0.9.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.9.0
[0.8.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.8.0
[0.7.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.7.0
[0.6.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.6.1
[0.6.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.6.0
[0.5.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.5.0
[0.4.8]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.8
[0.4.7]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.7
[0.4.6]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.6
[0.4.5]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.5
[0.4.4]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.4
[0.4.3]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.3
[0.4.2]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.2
[0.4.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.1
[0.4.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.0
[0.3.3]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.3.3
[0.3.2]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.3.2
[0.3.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.3.1
[0.3.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.3.0
[0.2.2]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.2.2
[0.2.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.2.1
[0.2.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.2.0
[0.1.9]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.9
[0.1.8]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.8
[0.1.7]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.7
[0.1.6]: https://github.com/davidsbianchi1984/qrme/commit/db6d7c9
[0.1.5]: https://github.com/davidsbianchi1984/qrme/commit/13338e6
[0.1.4]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.4
[0.1.3]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.3
[0.1.2]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.2
[0.1.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.1
[0.1.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.0
