# qrme — release notes

Every release published to <https://github.com/davidsbianchi1984/qrme/releases>, newest first. GitHub keeps these in its own database, not in the repository; this page is the copy that travels with a clone.

**282 releases.**

This is one part of a page GitHub is too long to render whole — see [RELEASE-NOTES.md](RELEASE-NOTES.md) for the rest.

**app-v0.53.1 to app-v0.1.1.**

## app-v0.53.1 — QRME app-v0.53.1

- Published: 2026-08-07
- Commit: `175b6e357c4f0546d77a0cf879b159b89dda8ef2`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.53.1>

> ### Nothing reaches the other platform, and now something checks
>
> `qrme/embeds.py` opens by naming the two things a video post could quietly
> stop doing: *"that nothing is copied, and that nothing is requested from the
> other platform until a viewer asks for it."* The first had real tests. The
> second had a field that is `None` and **a sentence promising a request will
> not happen**:
>
>     assert post["video"]["thumbnail"] is None
>     assert "until you press play" in entry["video"]["note"]
>
> Neither would notice a request happening. Add an oEmbed lookup for a real
> title tomorrow, keep `thumbnail` at `None`, leave the note alone, and every
> test in that file stays green while the module's central claim stops being
> true.
>
> So the network is unplugged and everything a viewer does is done: post a
> video, render the wall, read the post, load the public feed. **Nothing
> reached out** — the promise held, it simply had nothing checking it.
>
> Two things the guard's own injection pass found, in the guard:
>
> * the fixture **records as well as raises**. A thumbnail fetch written the way
>   somebody would actually write it — `try: urlopen(...) except Exception:
>   pass` — eats the raise, and a raise-only guard would have stayed green with
>   the request already made. The recorded list is what failed the test;
> * the source-level backstop was looking for `import urlopen`, which nobody
>   would ever write. `urlopen` is a function; the module is `urllib.request`.
>   The check now catches both `import X` and `from X import`.
>
> One more assertion in the same file keeps this from being satisfied by a
> feature that has stopped working: a card that renders nothing also makes no
> requests.
>
> Cut together with JIM-mini and PDI at **app-v0.53.1**.

## app-v0.53.0 — QRME app-v0.53.0

- Published: 2026-08-07
- Commit: `febbcab1b9bcb07f37f9b70e3c3e6eda1620761d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.53.0>

> ### Cut together at one version
>
> The three products are cut at one version, so this release exists here to keep
> that true. **No code changes in this repo this round.**
>
> The round's work is JIM-mini auditing its own promises, and the finding is one
> this repo should read twice: a block of refusals on the wire, guarded by tests
> that read the refusals back out of the dict that hardcodes them. The behaviour
> turned out to be correct — but nothing had been checking, and one sentence was
> wider than the truth.
>
> Both halves matter here. This repo ships posture and provenance blocks of the
> same shape on the feed, the wall and the marketplace, and the lesson transfers
> whole: **a claim about an absence has to be falsified from outside the claim**,
> by taking the action and looking at what changed. And **saying only what you
> refuse is how a true sentence misleads** — the reason this repo's own answers
> name what they keep rather than only what they do not.
>
> Cut together with JIM-mini and PDI at **app-v0.53.0**.

## app-v0.52.0 — QRME app-v0.52.0

- Published: 2026-08-07
- Commit: `d28916caac68aa711301213ccd8222a0232efeb2`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.52.0>

> ### Cut together at one version
>
> The three products are cut at one version, so this release exists here to keep
> that true. **No code changes in this repo this round.**
>
> The round's work is JIM-mini's, and it is a defect this repo knows by heart: a
> promise stated on the wire with nothing enforcing it. Its surface picker had
> reported `reads_health_aloud` since it shipped, and every reader was a screen
> rendering the word next to a button — the same shape as a binding that is not a
> door, or a refusal that names a field no form has. The decision now happens
> before anything is synthesised.
>
> The reason it belongs in this repo's story: **the enforcement point is the one
> that holds the thing**. QRME settled the same argument for the feed, where
> `plays` is decided by who holds the file rather than recomputed by four
> clients. A guardian deciding what a room may hear, and a platform deciding what
> a card may play, are the same rule about where a promise is kept.
>
> Cut together with JIM-mini and PDI at **app-v0.52.0**.

## app-v0.51.0 — QRME app-v0.51.0

- Published: 2026-08-07
- Commit: `b7eeaffee5db1c14e918188d3bbdc985ba9b7839`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.51.0>

> ### How many people it is talking to, offered rather than asked for
>
> A synthetic profile talks to many people at once by construction. The harm was
> never the multiplicity — it is the **discovery**: finding out, late, that the
> number was available the whole time and nobody offered it. That gap is
> entirely the product's doing, and closing it costs a count and a sentence.
>
> `GET /profiles/{profile_id}/attention` is **public and needs no token** —
> distinct people this week and altogether, plus one plain line. Making somebody
> get an account first would be the same withholding with a form in front of it,
> so it lives on the accountless screen beside the objection form and the mark
> check, on the console and all three phones.
>
> Three refusals ride as **fields rather than prose**, so a screen renders them
> next to the number instead of composing a reassuring sentence of its own: no
> ranking, no favourite, no names. The last is greppable rather than promised —
> a test reads the SQL and fails any statement that selects a column instead of
> counting rows. A viewer may ask *am I one of them* about their own id, and
> only their own.
>
> *"You're my favourite"* is the obvious product move and it is a lie the
> software cannot make true. It also hands somebody something to lose, so the
> day the count goes up they lose it. Nothing here models jealousy and nothing
> invites it: a product that manufactures the feeling in order to resolve it has
> manufactured the feeling.
>
> The round's other work is JIM-mini's — a bearing dial, an ambient company
> beat, and an isolation signal whose beat points back at this platform's rooms,
> desks and people.
>
> Cut together with JIM-mini and PDI at **app-v0.51.0**.

## app-v0.50.0 — QRME app-v0.50.0

- Published: 2026-08-06
- Commit: `6b556ac1560f046e94b22686ede9528925e0efdb`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.50.0>

> ## Cut together at one version
>
> No code changes in this repo this round. The work is JIM-mini's: its coach gains a **presence** — the half that speaks first rather than waiting to be asked, and deliberate about which parts of a companion are worth having and which are the failure mode.
>
> One thing there is this platform's business, because this platform is what it reaches into. `GET /presence/{user_id}/reach` hands somebody QRME's live rooms, staffed desks and synthetic profiles as **offers** — nothing joined, no bell rung on anybody's behalf, and no health context crossing over: the offer names an area, never a condition. The same posture the community door and the feed already keep, applied to a surface whose whole purpose is suggesting people — which is exactly where it would have been easiest to loosen.
>
> Cut together with JIM-mini and PDI at app-v0.50.0.

## app-v0.49.0 — QRME app-v0.49.0

- Published: 2026-08-06
- Commit: `c987416bc6778ff56348540fdc87df00e58ab050`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.49.0>

> ## The stream — one card at a time, and who is allowed to play
>
> One public feed a person swipes: a video that loops, a swipe, the next one — and mixed into it the two things this product has that a video app does not. A **live room you can walk into**, and a **desk with a real person behind it**, with the shop behind the desk browsable without leaving the stream. `GET /feed` and `GET /feed/{id}`, both readable without an account.
>
> **The line it had to not cross.** `post_videos` has carried the same comment since long before this surface existed: *the link and the id, never the file and never a thumbnail*. So `plays` is decided by **who holds the file** — footage this deployment holds loops; everything else stays a facade until somebody presses it, and makes no request before that. Asserted on the wire, where all four clients read it, rather than in any one of them.
>
> **Every fourth card is a place with a person in it.** A room and a desk both carry a plain sentence *before* the button, because both reach a human being.
>
> **Nothing is in the stream by default** — approved wall posts, open desks, and rooms attached to a desk that chose to be found. A rated desk is absent rather than blurred, and a shared link to one answers 404, because a 403 announces that the thing exists.
>
> Screens **189 Feed**, **190 What Plays**, **191 Rooms & Desks**, with a walkthrough lesson.
>
> **On all four clients.** A first draft recorded the two routes as doorless on the phones; the per-shell records are pinned empty by a test, so the door got built instead. iOS, Android and Windows read the same routes and render the same `plays`, with the console's own fourteen `feed.*` rows copied into the three native tables. What the phones do not have yet is the gesture — Previous and Next are buttons, which is also the version somebody who cannot drag can use.
>
> Cut together with JIM-mini and PDI at app-v0.49.0.
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.48.3...app-v0.49.0

## app-v0.48.3 — QRME app-v0.48.3

- Published: 2026-08-06
- Commit: `03727250a893421d4332590af2c234f673cf0336`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.48.3>

> ### Cut together at one version
>
> The three products are cut at one version, so this release exists here to keep
> that true. **No code changes in this repo this round.**
>
> The round's work is PDI's: its desktop console, which had no localization table
> at all until 0.48.2, takes its next two screens — **Custody** and
> **Continuity**, chosen ahead of larger ones because they are decisions rather
> than descriptions. 229 English strings to 177.
>
> Two things there are worth carrying across. The split record that repo wrote at
> 0.48.2 predicted it would *"become a real record the moment a screen exists on
> both sides"*, and it did within one round — one disagreement, caught and
> reconciled the day the table grew. And four more guards went blind the way
> 0.48.2 said they would: a check that greps a screen for a sentence stops seeing
> it the moment the sentence moves into a table. Both are worth expecting here,
> where every screen is already localized and every such guard was written
> against English that has since moved.
>
> Cut together with JIM-mini and PDI at app-v0.48.3.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.48.2...app-v0.48.3

## app-v0.48.2 — QRME app-v0.48.2

- Published: 2026-08-06
- Commit: `a2dd791af7930522b483f9aa0500f0f6ce865e70`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.48.2>

> ### The third axis, and how small it turned out to be
>
> 0.48.0 compared keys inside one table. 0.48.1 compared the console's table with
> each shell's. Both rounds ended by naming the same gap: rows they could not
> reconcile because **the three shells disagreed with each other**, leaving no
> native wording for the console to adopt. Nothing had ever compared the shells.
>
> Measured for the first time, the axis holds almost nothing:
>
> | | same key, 2+ shells | disagreeing | same English, all three | with no shared wording |
> |---|---|---|---|---|
> | QRME | 1056 | **1** | 972 | **1** |
> | JIM-mini | 261 | 0 | 204 | **3** |
> | PDI | 51 | 0 | 47 | 0 |
>
> Four rows across three products, and `action.sign_out` in Portuguese was
> QRME's: the phones said *Sair*, the Windows shell *Terminar sessão*. *Sair* is
> *leave*; ending a session in pt-PT is *terminar sessão*, so the odd shell out
> was the correct one and the other two moved to it.
>
> Saying that plainly is the point. Two rounds pointed here as the next large
> thing and it is not large, and a guard built expecting otherwise would have
> been built to find far more than exists.
>
> ### A correction to 0.48.1's record
>
> `console_native_split.txt` recorded two rows as third-axis cases. **Only one
> was.** `nc.t.stranger`'s two keys are Android-only and agree with each other,
> so a native wording had been available the whole time — the row was a plain
> console disagreement misfiled as a harder one. It is reconciled rather than
> recorded, and the record says so. QRME's console split went 26 → 24 rows,
> JIM-mini's 6 → 3.
>
> ### Added
>
> - `tests/test_the_three_shells_say_the_same_thing.py` — per product, the keys
>   two shells share and disagree on, and the English strings all three hold with
>   no wording in common, matched exactly against `tests/native_shell_split.txt`.
>   Where two shells agree the third is the drift and follows them; where all
>   three differ there is no majority, the row is a judgement, and it is
>   recorded. Ported to JIM-mini and PDI in the same round.
>
> Cut together with JIM-mini and PDI at app-v0.48.2.

## app-v0.48.1 — QRME app-v0.48.1

- Published: 2026-08-06
- Commit: `28473ca51ec7637c9719018b47167422101b7b37`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.48.1>

> ### Two tables, one product, and nothing compared them
>
> 0.48.0 compared keys *inside* one table. This round asks the same question one
> level out. The desktop console has its own table — `app/src/l10n.ts`, 1,882
> rows — and the three shells have theirs.
>
> **223 English strings live in both the console table and the iOS table, and
> 102 of them had no translation the two tables agreed on.** Android 104,
> Windows 103. Fifty keys are literally the same key in both tables, and two of
> those disagreed: `corner.send` in Arabic, and `plc.venues` in French —
> *Espaces* on the desktop, *Lieux* on the phone.
>
>     asked     does each table say the same thing twice the same way
>     mattered  do the tables say the same thing as each other
>
> ### The register
>
> The largest systematic cause is not vocabulary. It is who the product thinks
> it is talking to.
>
> | German | Sie / Ihnen / Ihre | du / dein / dich |
> |---|---|---|
> | console | **204** | 32 |
> | phone | 7 | **60** |
>
> The desktop addresses a German reader formally, the phone informally — *Wo Sie
> stehen* against *Wo du stehst*, *Ihre Signatur-Berechtigungen* against *Deine
> Signaturberechtigungen*. In a language with a T–V distinction that is a claim
> about the relationship, and this product made both at once. Spanish is milder
> and mostly settled (20 *usted* rows against 47 *tú* in the console).
>
> Every row reconciled this round moved onto the phones' wording, and so onto
> *du* and *tú*. **The whole-table sweep is recorded, not done**: German T–V is
> not a pronoun substitution, and the rule against machine-mangling text a person
> relies on applies to 204 rows as much as to fourteen.
>
> ### What 0.48.0 did to this number
>
> Widened it. Reconciling the Desk and the Counter picked *Theke* for the Desk so
> German would stop naming two tab-bar entries *Schalter*. The console still said
> *Schalter*, and nothing compared the two tables — a fix in one opening a gap
> with the other, which is this arc's shape committed once more inside its own
> fix.
>
> ### The measurement was nearly the bug again, twice
>
> JIM-mini's console writes some rows escaped — `"\u7834\u68c4\u3059\u308b"`,
> which in TypeScript **is** 破棄する. The first version of this check compared
> source bytes, so nine of that repo's thirty-four "disagreements" were one
> string spelled two ways. Decoding came first; the count fell from 34 to 25
> before a line was fixed.
>
> Then the guard-on-the-guard for the decoder was written with its escapes
> *already decoded* — it asserted `_decode("破") == "破"`, which is true of any
> function that returns its argument, and it passed with the decoder switched
> off. The injection pass caught it. It is now built from an explicit backslash.
>
> ### What was reconciled
>
> The voiceprint surface (`vce.*` against `nvoi.*`) — including *A previous
> voiceprint was retired when consent was withdrawn*, which differed in eight of
> nine languages, and *voiceprint* itself, *huella vocal* on the desktop against
> *huella de voz* on the phone. The desk surface. The chrome verbs 0.48.0 had
> already settled inside the native tables and the console had never been told
> about. QRME's count went **102 → 8** on iOS, 104 → 9, 103 → 9.
>
> ### Added
>
> - `tests/test_the_desktop_and_the_phone_say_different_things.py` — per shell,
>   the English strings both tables hold with no wording they agree on, matched
>   exactly against `tests/console_native_split.txt`, with a ceiling, floors and
>   probes under both parses, and a decoder whose own test is built from a
>   literal backslash. Ported to JIM-mini and PDI in the same round.
>
> ### Changed
>
> - 123 console rows moved onto the native wording across 381 language cells.
> - `action.save` in Portuguese moves the other way, to *Guardar*: *Salvar* is
>   pt-BR and every other Portuguese row in these products is pt-PT.
>
> Cut together with JIM-mini and PDI at app-v0.48.1.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.48.0...app-v0.48.1

## app-v0.48.0 — QRME app-v0.48.0

- Published: 2026-08-06
- Commit: `01f7a4aa1775354596287e27a6b644331577ce74`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.48.0>

> ### The same sentence, translated twice, and the two copies had drifted
>
> 0.47.9 corrected what `native_dead_keys.txt` meant: 263 of its 335 rows are not
> waste but cross-shell asymmetry. This round asked what those 263 actually are,
> and **sixty of them are a sentence the shell already says under a different
> key**.
>
> `nc.find` is dead on the iPhone and on Android. The Windows shell uses it for
> the Community screen's join button. The iPhone has that same button and calls
> it `nc.match.find`:
>
> | | Windows (`nc.find`) | iPhone (`nc.match.find`) |
> |---|---|---|
> | es | Buscar una coincidencia | Buscar a alguien |
> | fr | Trouver une mise en relation | Trouver un binôme |
> | de | Eine Verbindung suchen | Gegenüber finden |
>
> An English reader sees one product. A Spanish reader sees a different button on
> the phone than on the desktop, for the same press.
>
> Counted across the whole table rather than only the dead rows: **54 English
> strings under two or more keys on iOS, 55 on Android, 60 on Windows** — about
> 215 redundant rows, 2,150 translations maintained twice. *Send* exists under
> five keys. And in **43 of the 54** iOS sets the copies had already drifted.
>
>     asked     is every string on the screen translated
>     mattered  does the product say the same thing twice the same way
>
> ### A duplicate is a question, not a defect
>
> Three things produce one English string under two keys, and only the last is a
> bug. The new record, `tests/native_split_wordings.txt`, says so at the top:
>
> 1. **English hides the gender.** `ava.show`, `cam.show`, `lend.show`,
>    `org.show`, `work.show` all read *Show it*; Spanish must pick *Mostrarlo* or
>    *Mostrarla* by what *it* is. Five rows is the right number of rows.
> 2. **One English word is two words.** `counter.trade` is a trade as in a craft
>    — *Oficio*, *Métier*, *Gewerk*, 手艺. `tab.trade` is trade as in commerce —
>    *Comercio*, *Négoce*, 交易. The translations are right; the English is wrong.
> 3. **The same thing said two ways for no reason.** *Refresh* was *ताज़ा करें*
>    on two screens and *रीफ़्रेश* on a third. Nobody decided this.
>
> The third kind is reconciled: **34 sets, 351 language cells across the three
> tables.** The first two are recorded by name — 42 rows, every one of them a
> question about the English rather than a translation mistake.
>
> ### Two tabs with the same name
>
> `tab.counter` and `tab.desk` are separate entries in the same tab bar. In
> Spanish both read *Mostrador*; in French both *Comptoir*; in Portuguese both
> *Balcão*. Three languages in which this product's own tab bar named two
> destinations identically. The Manage screen's mirror had it right —
> `nmg.t.counter` is *Ventanilla* / *Guichet* / *Guichê* — which is how it
> surfaced: by asking why the two copies disagreed.
>
> ### A file that does not compile
>
> `people.say` and `party.say` both read *Say something*, and their Italian
> differed. One of them was `"it": "Di\u0027 qualcosa"` — a literal `\u0027` in
> a **Swift** string, where the escape is `\u{0027}` and the unbraced form is not
> an escape sequence at all. `L10n.swift` does not compile. No Swift toolchain
> runs in this repo's CI, so nothing had said so; the Android and Windows tables
> carry the row correctly. The guard now refuses `\uXXXX` in the Swift table.
>
> ### Where some of the duplicates came from
>
> Under my own hand. 0.47.6 wired 91 Android sites Compose had hidden, and did it
> by inserting `nmg.t.desk`, `nmg.t.gaming` and `nmg.t.sign` beside `tab.desk`,
> `tab.gaming` and `nsig.sign`, which already held those words. 0.47.7 hit a key
> collision and renamed around it rather than reconciling the two rows. The rule
> that would have stopped both, now written down: before inserting a row, look
> for the sentence.
>
> ### Added
>
> - `tests/test_the_same_sentence_translated_twice.py` — per shell, the English
>   strings carried by two or more keys whose ten translations disagree, matched
>   exactly against `tests/native_split_wordings.txt` in both directions, with a
>   ceiling on the total and a check that the Swift table holds no unbraced
>   unicode escape. Ported to JIM-mini and PDI in the same round.
>
> ### Changed
>
> - 34 duplicate sets reconciled across the iOS, Android and Windows tables —
>   *Send*, *Refresh*, *Leave*, *Sign*, *Topic*, *Rating*, *Display name*, the
>   Manage screen's tab strip and the Desk/Counter vocabulary among them.
> - The Counter tab is now *Ventanilla* / *Guichet* / *Guichê*, distinct from the
>   Desk tab in every language.
>
> Cut together with JIM-mini and PDI at app-v0.48.0.

## app-v0.47.9 — QRME app-v0.47.9

- Published: 2026-08-06
- Commit: `046ac8df8e741e8f8cfbc5ee4dc04be2db7266b2`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.9>

> ### The number was mislabelled, and it was hiding a consent screen
>
> `native_dead_keys.txt` has led with the word **backlog** for three releases,
> implying the work was deletion. **263 of its 335 rows are asked for by a
> different shell.** They are not rows nobody uses; they are rows *this* shell
> does not use and a sibling does — and every one is the same question: this
> screen exists on all three shells, so why does one of them say less?
>
>     asked     is this row used anywhere
>     mattered  does this shell say what its siblings say
>
> Only 72 rows are asked for by no shell at all. Those are the deletion
> candidates; the rest are a to-do list about screens, and the file now says so.
>
> ### What the mislabelling was hiding
>
> The **voiceprint consent block**. Every shell shows a heading — *what this
> permission holds* — and beneath it three sentences: the watermark, the
> attestation, the withdrawal. Android and the desktop took all three from the
> table. The iPhone had them **hardcoded in English**, in an array handed to a
> `ForEach` — which is not the start of a `Text(`, and so was read by nothing.
> The screen showed a translated promise and then said, in one language only,
> the three things the promise consists of.
>
> It also prepended `"· "` to each line. Android's copy of the same block carries
> a note saying the bullet belongs *in* the row so an RTL reader gets it on the
> correct side. That note had been there since it was written.
>
> ### The fifth shape
>
> `_ARRAY` is the Swift twin of the `listOf` shape 0.47.6 found in Kotlin: an
> array literal handed to a loop. Ported to all three repos, where it turned up
> **nothing else** — this screen was the only instance across nine shells, which
> is why it survived four rounds of widening.
>
> Phrases only, the rule `_TERNARY` set: an array of API values is as common as
> an array of sentences.
>
> ### Also
>
> * `ns.pr.short` — *Counts of what failed. Never what you typed.* — was held by
>   the iPhone and said by both siblings. Now said here too.
> * Seven rows deleted for the honest reason: the desktop has no beacon-scanner
>   page, and `nsig.domain.android` / `nsig.ceremony.win` each explain one
>   platform's own constraint to shells that cannot hit it.
>
> ### Named rather than counted
>
> **The iPhone's beacon scanner has no camera-permission state.** Android shows
> *Camera access is needed to read a beacon* and *Nothing is recorded — frames
> are read and discarded*; iOS guards on `AVCaptureDevice.default(for: .video)`
> and, when permission is refused, renders nothing at all. That is a missing
> screen state rather than a missing string, so it is recorded in the file rather
> than half-built here — and the second sentence is a privacy promise the Android
> reader is given and the iPhone reader is not.
>
> Cut together with JIM-mini and PDI at app-v0.47.9.

## app-v0.47.8 — QRME app-v0.47.8

- Published: 2026-08-06
- Commit: `a3c32daf03bdb381a6d5cad7441ba7cfe52eb43d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.8>

> ### No changes in this repo
>
> The three products are cut at one version, so this release exists here to keep that true. The round's work is PDI's Transfers screen — the sealed transfer, the intake, and the two out-of-band instructions that sit under a token shown once and name the only way the file can be retrieved.
>
> The rules it applied were written here: the picker keeping its raw values as identity (0.47.4), the strip resolving keys out of a `listOf` (0.47.6), and the desktop's labels moving out of XAML into a `Localize()` (0.47.7).
>
> Cut together with JIM-mini and PDI at app-v0.47.8.

## app-v0.47.7 — QRME app-v0.47.7

- Published: 2026-08-06
- Commit: `b578decb3e55bce26bde678428c60f016420a4ea`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.7>

> ### The other two syntaxes
>
> 0.47.6 derived the Kotlin rule from the shell and left the other two as
> hard-coded lists: `_SWIFT` at eight constructs, `_XAML` at four attributes.
> Both had the same blind spot, and finding it was a matter of asking the same
> question one more time.
>
> **iOS** wraps its labels the way Compose does — `row`, `field`, `stat` — so the
> derivation now covers Swift too, reading the *last* identifier before the colon
> because Swift's parameter list carries an argument label in front of the name.
>
> **Windows** is the bigger half. `_XAML` reads attributes, and half of this
> shell's labels are not written in XAML at all: the settled idiom here is
> `x:Name` on the element and `Foo.Text = L10n.T("key")` in a `Localize()` the
> constructor calls. A label that was never localized therefore sits in the
> code-behind as an **assignment**, which `Text="` cannot match.
>
>     asked     is this an attribute on an element
>     mattered  does this end up as the words on an element
>
> **91 call sites across nine shells** — 16 on the iPhones, 33 on the desktops,
> in three products. Here that is the Overview card's *Kind / Status / ID*, the
> Reach page's five status verdicts, the Settings page's steering and feedback
> lines, the objection form's refusal, and both places the signing ceremony says
> *Follow the Windows Hello prompt.*
>
> Phrases only, and for the reason `_TERNARY` already gave: this shell sets
> `Box.Text = "advance"` and `Box.Text = "bottom_right"` as **default values** in
> input boxes — API tokens a person edits, not prose a person reads. A rule that
> raises a ratcheted count under-counts on purpose; the raw 28 on this shell is
> 12 once that filter runs, and the 12 are the sentences.
>
> *So far: {list}* is one row with a slot rather than a translated half joined
> to a list, which is the rule the alarm rows have followed since they were
> written.
>
> Records back to their floors: **iOS 2, Android 2, Windows 3.** Dead rows 350 to
> 347.
>
> Cut together with JIM-mini and PDI at app-v0.47.7.

## app-v0.47.6 — QRME app-v0.47.6

- Published: 2026-08-06
- Commit: `2ccb437b4a7382734c9b2c3668e99b5922f67486`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.6>

> ### Every button on the Android shell was English, and both guards said otherwise
>
> Compose has no `Button(text)`. A button on these shells is a `Box` with a `Text` inside it, written once as a private composable and called from everywhere by name — `SmallAction("Send")`, `BrandButton("Bind")`, `labeledField("Desk id", id, "dsk_…")`. The untranslated-screens rule's Kotlin pattern list was `Text(` and nothing else, so it read none of them, and this shell's record has been sitting at **2** with 80 English strings on it.
>
>     asked     does the string start a `Text(`
>     mattered  does the string end up inside one
>
> The rule now derives its constructs from the shell rather than naming one: a function with a `String` parameter whose body renders that parameter through `Text(` is, by construction, something that puts a string in front of a person, and the argument at that parameter's **position** is the string it puts there. Not `[A-Z]\w*` — `labeledField` and `cardRow` break the capitalization convention Compose composables usually follow — and not argument zero, because `labeledField` renders both its label and the grey prompt inside the box, which is where these screens keep their examples.
>
> ### The prune this round was going to make, withdrawn
>
> 0.47.5 recorded **540 rows** translated into ten languages that nothing asks for, and said in the record file itself that the way to work them off is by reading each one, because some are rows a screen *should* be asking for. This round read them, grouped them, and assembled a prune of 366 — rows for screens another shell has and this one does not. That prune ran, and was then withdrawn.
>
> **59 of the 154 rows it deleted from the Android table were strings still hardcoded on that shell.** `nmg.t.general` through `nmg.t.deals` — the sixteen labels of the Manage tab strip — were among them, sitting one line away from a `listOf("General", "Summon", "Market", …)` that put them on screen in English. 14 of 133 on Windows were the same. The two guards shared one blind spot, so the screens read as asking for nothing and the rows read as asked for by nobody, and the second reading is what the delete was built on.
>
>     asked     is this row asked for
>     mattered  is this row asked for *by a call this guard can read*
>
> So the number came down by wiring instead. **91 call sites** now go through `L10n`, **33 rows** were added for the ones no table held, and the four segmented tab strips resolve keys instead of naming their screens in English. **540 to 350**, and no row deleted.
>
> The rule this round earned, written into the record file: *a row that looks dead is evidence about the guard before it is evidence about the row.*
>
> Cut together with JIM-mini and PDI at app-v0.47.6.

## app-v0.47.5 — QRME app-v0.47.5

- Published: 2026-08-06
- Commit: `483a9ee6de56105a4c1cb02d34c8b1bd7cd7918f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.5>

> ### Three screens titled with their own key names
>
> JIM-mini has had a guard since 0.44.x that asks whether every key a shell
> *asks for* is a key that shell *holds* — because `L10n.t` returns the key when
> there is no row, so a screen with a missing row renders its own source code
> where a heading belongs. It stayed in that one product for several releases
> while this repo carried the same three tables and the same risk.
>
> Ported here this round, and it found the defect it exists for on the first
> run. `tab.compose`, `tab.posts` and `tab.robots` are **screen headings** on
> Android, and the Android table held none of them. Those three screens have
> been titled `tab.compose`, `tab.posts` and `tab.robots`, in every language
> including English. The rows were lifted from the iOS table.
>
>     asked     does the screen call the localizer
>     mattered  does the localizer have anything to say
>
> ### Keys built at runtime, again
>
> Four call sites asked for `"counter.presence." + p` and `"corner.switch." +
> feature`. A key assembled at runtime is a key no guard can see being asked
> for, so all five rows read as *nothing asks for this* — the direction that
> invites somebody to delete a row a screen is using. Each branch resolves on
> its own line now, the same fix this arc has applied twice already.
>
> ### The other direction, recorded
>
> **540 rows** across the three shells are translated into ten languages and
> asked for by nothing. That is not one defect; it is the residue of thirty
> rounds in which rows were added ahead of the screens that would use them, or
> left behind when a screen was rewritten. It is recorded and ratcheted rather
> than deleted in one pass, because some of those rows are ones a screen
> *should* be asking for and is not — and a bulk delete would bury them.
>
> Cut together with JIM-mini and PDI at app-v0.47.5.

## app-v0.47.4 — QRME app-v0.47.4

- Published: 2026-08-06
- Commit: `8a52e31f57cb78bd76789d2b6e1579fe9d0ca69a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.4>

> ### Version alignment
>
> No QRME code changed this round. The work was JIM-mini's Overview — the first
> screen a person sees after signing in — and the three tab strips whose English
> lived in a `case` clause of an `enum Tab: String`, which is the shape this
> repo found in its own pickers at 0.46.8 and JIM found in ConnectView at
> 0.47.2. 229 → 150 across its three shells.
>
> Cut together with JIM-mini and PDI at app-v0.47.4.

## app-v0.47.3 — QRME app-v0.47.3

- Published: 2026-08-06
- Commit: `af8a1b347f252929feb2e730f7e5f7e2ef8162c3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.3>

> ### The literal one statement away from the call
>
> `clientpaths.py` is byte-identical in all three repos by design, so the new
> guard-on-guard it gained this round runs here too — and found two calls this
> shell's Android client makes that the route audit could not see:
>
>     val path = if (industry.isNullOrBlank()) "/packs"
>     else "/packs?industry=" + enc(industry)
>     val arr = JSONArray(request(path))
>
> The audit reads a call's arguments and cannot follow a variable, so both
> spellings of the path read as no call at all. Fixed at the call site rather
> than by teaching the extractor to chase assignments — a path spelled where it
> is sent is easier for a person to read too. `/marketplace/listings` was the
> same shape.
>
> This repo's doorless records have been at zero since 0.44.2, so nothing was
> inflated here; what was blind was the *refusal* check, which cannot notice a
> client asking for a route under the wrong verb if it cannot see the call.
>
> Two path literals stay recorded as deliberate non-calls: `DeskViewUrl` and the
> signing-ceremony URL both return an address for something else to open.
>
> Cut together with JIM-mini and PDI at app-v0.47.3.

## app-v0.47.2 — QRME app-v0.47.2

- Published: 2026-08-06
- Commit: `078b70278f522a7bf5bce0d14d5eea692db75f1b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.2>

> ### The fix I found here and did not carry
>
> At 0.46.9 this repo found that the Windows shell's **Sign out** sits in
> `NavigationView.PaneFooter` while the loop localizing the nav walks
> `Nav.MenuItems`, and fixed it. JIM-mini has the same file, the same loop and
> the same footer, and nobody checked. It has been saying *Sign out* in every
> language since.
>
>     asked     is the bug fixed
>     mattered  is the bug fixed in the other two products
>
> No QRME code changed this round. The finding is JIM's to fix and it is fixed
> there, along with Family and Connect on all three of its shells — 386 → 229.
>
> Cut together with JIM-mini and PDI at app-v0.47.2.

## app-v0.47.1 — QRME app-v0.47.1

- Published: 2026-08-06
- Commit: `896bd368420e38e44ebfb44d4f32171964438b8a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.1>

> ### The blind spot was in all three products
>
> 0.47.0 found that this repo's native-shell measurement could not see a string
> chosen by a ternary. The other two products' guards are this one, copied — so
> the blind spot was in all three by construction, and the widening is ported
> to both this round along with the two tests that hold it in place.
>
> JIM was understating by **40**, PDI by **12**.
>
> No QRME code changed. What the correction found in JIM is in that repo's
> changelog and is worth reading: the fourteen rows that carve out its alarm
> surface localize what the alarm says once it is going, and not **Tap for
> emergency** — because the count they were chosen from could not see it.
>
> Cut together with JIM-mini and PDI at app-v0.47.1.

## app-v0.47.0 — QRME app-v0.47.0

- Published: 2026-08-06
- Commit: `cfecf63fcf12ac6be59d8cf8791fac12a68d5aad`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.47.0>

> ### The ternary hid the sentence
>
> `Text(cond ? "Verifies" : "Does not verify")` was invisible to the
> measurement. Every pattern in the extractor looked for a literal at the
> **start** of an argument list, and a string chosen by a condition is not
> there.
>
>     asked     is this literal the first thing in a Text(…)
>     mattered  does a person read it
>
> What that hid, in rounds that recorded these screens as finished:
>
> * the signing screen telling somebody whether their credential **verifies**,
>   and whether it is **device-bound — cannot sync** or **syncable — exists on
>   your other devices**;
> * the voice screen's gate — *Enough of your voice is on record — mint the
>   voiceprint* — localized in 0.46.7, which left this behind;
> * the desk's **Ring the bell**, **● LIVE** and **SAMPLE VIEW**;
> * the scanner's **Point at a QRME code**.
>
> On all three shells, in each case.
>
> The record said 68. The truth was **125**.
>
> The widening counts phrases and not lone tokens, deliberately: `cond ? "on" :
> "off"` is as often an API value as a word, and the conservative direction for
> a rule that *raises* a ratcheted number is to under-count. Two new tests hold
> both halves of that — one fails if the rule stops matching, one fails if it
> starts matching tokens.
>
> ### The floor
>
> **125 → 7**, and the seven contain no English at all: `dsk_…`, `sig_…` and
> `prf_…` are identifier prefixes shown as placeholders, `%.0fs` is a duration
> format, and two are the extractor's own truncation of an interpolated format
> string. They stay in the count rather than being special-cased out — a rule
> that excuses strings is a rule that can be taught to excuse the wrong ones.
>
> iOS 80 → 2, Android 43 → 2, Windows 89 → 3.
>
> ### Four wordings settled
>
> The gaming blurb — Windows alone said **agent-operated**, the fact a reader
> most needs about the thing in the lobby beside them. The minor-in-lobby
> toggle, worded two ways. The robot-pack badge, **🤖 ROBOT** against **🤖 ROBOT
> TASKS**. The industry filter, with and without its example. The longer
> wording wins in each case, because in each case it says one more true thing.
>
> Cut together with JIM-mini and PDI at app-v0.47.0.

## app-v0.46.9 — QRME app-v0.46.9

- Published: 2026-08-06
- Commit: `5c14164f89b7118ada0913f16240f01fb87c0056`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.9>

> ### The button that ends the session
>
> Windows' Sign out sits in `NavigationView.PaneFooter`. `LocalizeNav()` walks
> `Nav.MenuItems`. It never reached it, so the control that ends a session read
> **Sign out** in every language the shell offers.
>
> The row it needed, `action.sign_out`, has been in the iOS and Android tables
> since they were written. Android was using it. iOS had it and hardcoded the
> English next to it anyway. Windows did not have the row at all — the appender
> this round added it to one table out of three, which is how the gap showed up
> in the arithmetic before it showed up in a screenshot.
>
> One control, three states of done. All three ask the table now.
>
> ### The nav's English defaults are gone
>
> Every `NavigationViewItem` carried `Content="Overview"`, `Content="Chat"` and
> so on — dead markup, overwritten at construction. Not harmless: `L10n.T`
> returns the key when a key is missing, and a plausible English default hides
> that. A missing `tab.study` would have rendered "Study" and looked correct.
> Four items already carried no `Content` for exactly this reason. Now none do.
>
> ### Six screens, three shells, one pass
>
> Overview, Compose, Posts, Connect, Robots and Study — taken together rather
> than one shell at a time, because one-shell-at-a-time is what produces the
> split wordings this arc keeps finding.
>
> **212 → 68.** iOS 80 → 34, Android 43 → 12, Windows 89 → 22.
>
> ### Two more pickers rendering their own enum
>
> `ConnectView.Tab` and `StudioView.Tab` on iOS had raw values that were both
> the API-side section names and the words a reader sees — the same shape as
> `ManageView.Tab` last release, and the relationship dropdown three before
> that. Neither was visible to the ratchet, because the English lives in the
> enum rather than in a `Text(…)`.
>
> ### One picker, two wordings
>
> The chat role picker says *Advisor — weigh it and recommend* and *Operator —
> just do it* on the console and on Windows; on iOS and Android it said
> *Advisor* and *Operator* and left the reader to guess. This is the control
> that decides whether a synthetic profile recommends something or goes and
> does it. The explaining wording wins, taken verbatim from the console table.
>
> Cut together with JIM-mini and PDI at app-v0.46.9.

## app-v0.46.8 — QRME app-v0.46.8

- Published: 2026-08-06
- Commit: `a142c51050d86aa83394201327345a3db59d5828`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.8>

> ### The crisis number that only works in one country
>
> The wellbeing card on the marketplace — the one introducing Dr. Lena
> Whitcomb, Dr. Marcus Adeyemi and Dr. Priya Nair — ended with *"In crisis,
> call or text 988."* That is the US Suicide & Crisis Lifeline. It reaches
> nothing from Spain, Japan, India or Egypt, and this round put that sentence
> into ten languages, which is what made it obvious: a translated instruction
> to dial a number that does not answer is worse than an untranslated one.
>
> It now says **contact your local crisis line or emergency services**. The
> sibling product settled this same question rounds ago and its wording was
> already there to copy.
>
> Two files still carry the number in starter-pack content served from the
> backend — `qrme/packs.py` and `qrme/seed.py`. That is a different surface,
> localized server-side, and it gets its own round.
>
> ### The same surface has three names
>
> `ManageView` on iOS, `ReachPage` on Windows, six loose panels in `Screens.kt`
> on Android. One console — the owner's reach: their @handle, their placed QR
> beacons, their marketplace listing, their knowledge packs, the license their
> expertise is offered under, and what it has earned.
>
> Its **own sub-tabs were English on every shell**. Summon, Market, Packs,
> License, Earn — the tab bar behind the tab bar. That is the finding this
> whole arc opened with, one level down.
>
> The iOS tab enum was the cause: its raw values were both the API-side section
> names *and* the words a person read. Splitting them is the same fix as the
> relationship dropdown four releases ago and the kind picker three ago.
>
> **368 → 212.** iOS 133 → 80, Android 96 → 43, Windows 139 → 89.
>
> ### One paragraph, two lengths
>
> Windows told a reader three things about knowledge packs that the phones did
> not: that a reply's provenance names the pack it drew on, that a robot task
> pack teaches a physical body new commandable tasks and is capability-checked
> at install, and that free packs download while priced ones are bought. Three
> facts, missing from two shells out of three.
>
> The longer wording wins and all three shells carry it now.
>
> ### A shell that would not have compiled
>
> Three sections of the iOS console ended up with two `@EnvironmentObject`
> declarations of the same property — the bulk pass added one to sections that
> already had it under `private`. Two stored properties with one name do not
> compile. Caught before the guards ran, by reading the file.
>
> Cut together with JIM-mini and PDI at app-v0.46.8.

## app-v0.46.7 — QRME app-v0.46.7

- Published: 2026-08-06
- Commit: `f098c86498a3aeddd42417345e98cb2bd14136a3`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.7>

> ## Two cards, done on two shells out of three
>
> `WhoWroteThisCard` and `ObjectToAProfileCard` — the pair a person contesting a profile reaches — were localized on iOS and Windows last release and left in English on Android.
>
> Not a scope decision: **every key they needed already existed**, so the fix cost zero new rows. The cause is where the code sits. Android's cards live five thousand lines from the screen that calls them, so working *the Settings screen* never touched them — and the changelog two releases ago says **all three shells or none** in as many words.
>
> ## Signatures and Voice, on all three
>
> **470 → 368.**
>
> | shell | before | after |
> |---|---|---|
> | iOS | 171 | 133 |
> | Android | 128 | 96 |
> | Windows | 171 | 139 |
>
> Sixty rows, written once and generated into Swift, Kotlin and C#.
>
> ## One promise, two wordings
>
> The voice consent copy said *the recording stays on this device* on the phones and *stays on this machine* on the desktop — the same assurance about where a recording of somebody's voice lives, stated twice. **One row now**, and the third round running that this shape has turned up.
>
> Windows also had the attestation itself — *I attest this is accurate and complete* — as the literal default text of the box a person is agreeing with. It is looked up now, so the sentence somebody signs is in the language they read.
>
> ## A check that was wrong about names
>
> The English-leak check flagged `Digital Asset Links`, `webauthn.dll`, `Edge`, `Windows Hello` and `WebAuthn` as untranslated English sitting inside the Japanese and Chinese rows. They are product and specification names and stay English in every language. The check exists to catch a sentence somebody forgot to translate, not a name that has no translation.
>
> Cut together with JIM-mini and PDI at app-v0.46.7.

## app-v0.46.6 — QRME app-v0.46.6

- Published: 2026-08-05
- Commit: `051d15c3c870944a60548b8c0f64a27ef99a978e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.6>

> ### The rest of Settings, and Community
>
> Last release took the first screen and the governance half of Settings on all
> three shells. This one finishes Settings — steering, the relationship, the
> feedback card, and the consent notice for failure reporting — and does
> Community, the two screens where somebody meets a stranger or opens a room.
>
> **590 → 470.** iOS 217 → 171, Android 158 → 128, Windows 215 → 171.
>
> Seventy-five rows: sixty-eight written once and generated into Swift, Kotlin
> and C#, and seven — the relationship types — **ported verbatim from the
> console's own `rel.t.*`** rather than worded a second time.
>
> ### Three pickers still rendering enum members as words
>
> `t.Replace('_', ' ')` and `$0.replacingOccurrences(…).capitalized` turned
> `romantic_partner` into *"Romantic Partner"* on the relationship picker of all
> three shells. That is not a label anybody wrote; it is the API's member with
> its underscore taken out. All three now look the word up, and all three read
> the value back by index, so the visible text is free to be a translation.
>
> The same shape was fixed on the console's dropdown at 0.46.2 and on the phones'
> kind picker at 0.46.5. This is the third client and the third round of it.
>
> ### Two tallies that counted in English
>
> The feedback card's *"So far: 3 idea · 1 bug"* built its own sentence by
> joining the API's category names, inside a card that is otherwise translated.
> Both the prefix and the categories are looked up now.
>
> ### One sentence, three wordings
>
> The consent notice for failure reporting said *"the day it happened"* on iOS,
> *"the day"* on Android, and *"the day"* with a different closing sentence on
> Windows — three versions of the paragraph that asks a person to agree to
> something. It is one row now. Consent is asked in the reader's language, and
> the same words, or it is not really asked.
>
> Cut together with JIM-mini and PDI at app-v0.46.6.

## app-v0.46.5 — QRME app-v0.46.5

- Published: 2026-08-05
- Commit: `6117a84a2059b41caf54277a9712edd66c0f875c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.5>

> ### The first screen, on all three phones
>
> Twenty-one releases took the console's untranslated record to its floor. The
> phones were never measured until the round that wrote
> `native_screens_untranslated.txt`, which counted 703 English strings behind
> QRME's three translated tab bars and recorded them honestly rather than
> pretending.
>
> This round takes the **first screen and the settings screen** on all three:
> **703 → 590**, sixty rows in ten languages, written once and generated into
> Swift, Kotlin and C# rather than typed three times.
>
> ### The screen with no language to read
>
> `WelcomeView` renders before a profile exists, so `state.language` is `"en"`
> for every reader on Earth — and the language picker in the middle of that
> screen is where the profile's language gets chosen in the first place.
>
> `L10n.deviceLanguage` was written one release earlier for the accountless
> screen, whose reader is in exactly this position. All three shells now read
> the device here. What that changes most is the sentence above the button:
> **a person cannot agree to terms they cannot read.**
>
> ### The Android shell did not compile
>
> `ProblemReportingCard()` sat between two arguments of a `Text(…)` call in
> `Screens.kt`. Kotlin does not accept that. The parentheses balance, so
> nothing counting brackets would have noticed, and there is no Kotlin compiler
> in this suite — it was found by reading the file while localizing it, which
> is not a method.
>
> The call moves to where the iOS shell has always had it, and the shape gets a
> check: two arguments with nothing between them. A `{` reopens statement
> context, so `vm.call({ … oauthState = st … })` is ordinary code — the first
> draft called both of those a defect and was fixed before it was kept.
>
> ### Two pickers that posted their own labels
>
> The kind picker rendered the API's members as words (`other_person` →
> *"Other Person"*), and on Windows `OnStart` read that visible text back as
> the value to post — so translating the label would have posted the Spanish
> word as the kind. The members move into `_kinds`; only what somebody reads is
> looked up. This is the same defect the console's relationship dropdown had at
> 0.46.2.
>
> ### Every row, not every row of one prefix
>
> The shells' ten-language check has only ever looked at `pub.*` — the rows the
> accountless round ported, because that was the set that existed. It now
> checks every row of all three tables, plus that no translation loses or
> invents a `{slot}`.
>
> Its first draft read a line at a time and called fourteen complete rows
> incomplete: the tab labels were wrapped across three lines when they were
> written. A check that reports missing translations that are right there would
> have had somebody delete and retype them.
>
> Cut together with JIM-mini and PDI at app-v0.46.5.

## app-v0.46.4 — QRME app-v0.46.4

- Published: 2026-08-05
- Commit: `c32393985ad7e7d540de0fa9772bd2308ade13b9`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.4>

> ### The refusal names a field, and the form did not name it at all
>
> `_FIELD_LABELS` puts the label a person can see into the 422 that names a
> field. The record of what is *not* mapped explains its own fallback: an
> identifier a reader can match to the form beats a word invented for them.
> That paragraph was doing two jobs. *Nobody labels it* was the reason not to
> invent a word, and it had quietly become the reason not to look.
>
> **Signature id** is QRME's one. The release box on Referrals had a
> placeholder and no name, so a 422 saying `signature_id` had nothing on the
> screen to match. The label is now `ref.sign.sid`, in ten languages, ported
> from the placeholder's own opening words; the field is mapped from the same
> wording, so the sentence and the box agree by construction.
>
> The record: 124 → 123. PDI's went 91 → 51 the same way — forty of its rows
> had a control and no label — and JIM's 100 → 99.
>
> Cut together with JIM-mini and PDI at app-v0.46.4.

## app-v0.46.3 — QRME app-v0.46.3

- Published: 2026-08-05
- Commit: `11e6900e016935cfb6380313b371bad9ff880d50`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.3>

> ### The console record reaches its floor
>
> **25 → 1.** Twenty-one releases, about 1500 keys, forty-six screens. The
> last three:
>
> **What Would They Do** — the horizon list held its three English phrases
> in a `const`; it holds keys. The confidence note was four fragments
> around three numbers and is one sentence, because the count does not
> lead the clause in Japanese.
>
> **Memory Vault 🔒** — including both `confirm()` dialogs. A confirmation
> somebody cannot read is not a confirmation, and *this cannot be undone*
> is the sentence that most needs to arrive in the reader's language.
>
> **Friends** — the founder tag, the suggestion list, and the note that
> distinguishes *removed* from *there was nothing to remove*.
>
> 38 keys.
>
> ### What the file says now
>
> `console_untranslated.txt` opened by describing a console that hands a
> Spanish reader 1576 English strings the moment they click past a
> translated sidebar. That was true when it was written and has not been
> true for some time, so the header was rewritten: what it was for, what
> it is for now, and both corrections that mattered — the 117 punctuation
> rows struck in 0.30.10, and the one row that stays.
>
> **The floor is one, not zero.** `AI ·` on TheMark is quoted rather than
> written, and translating a quotation of what the server hardcodes would
> describe a designation nobody is shown. A floor of zero would have been
> a nicer number and a less honest one.
>
> ### A format that had never met the number one
>
> Every ratchet's first line must read `# status: floor|backlog — N rows`,
> enforced across all of them by
> `test_every_ratchet_says_what_it_is_before_it_says_anything_else`. The
> pattern demanded the plural unconditionally, so landing on exactly one
> row forced a choice between *1 rows* at the top of a file about stating
> a count honestly, and a format that had simply never met the case.
>
> The pattern now requires the *right* form — `row` for one, `rows`
> otherwise — which is stricter than requiring one form of the word, not
> looser. It immediately found `refusals_untranslated.txt`, which has been
> sitting at one row and saying *1 rows*.

## app-v0.46.2 — QRME app-v0.46.2

- Published: 2026-08-05
- Commit: `0422dfcbeff4305c0e53b6dc77cf70943538e77a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.2>

> ### The front page, the price list, and who is in a life
>
> The console-untranslated record falls **69 → 25**. Four screens this
> round rather than three, because they are small and the tail is short.
>
> **Home** — the four stat tiles held their label and their caption as
> English strings in a `const`. They hold keys now.
>
> **Plans** — the price list, the two custody paragraphs, and the sentence
> somebody reads after cancelling: *a lapsed plan is not a reason to
> delete anybody's work.* The storage posture was three fragments around
> two values and is one sentence; the clause naming who can read your work
> does not sit last in Japanese.
>
> **Relationships** — and a real bug found while translating it. The
> `<option>` elements carried no `value`, so **the visible text was the
> value posted to the API**. Translating the label alone would have sent
> *amistad* as a relationship type and *cálido* as a tone. The enum moved
> to `value` and only the word somebody reads is looked up. Worth saying
> plainly: this was not a localization defect, it was a latent one that
> localization walked into.
>
> **Discover** — the marketplace, the starter collection, and the two
> badges that say whether a face is a photograph or not.
>
> 76 keys.
>
> ### The dead-key guard, widened again — the same lesson, third time
>
> Last release taught it that a key can live in a table: `{ id: "chat",
> key: "rms.ch.chat" }`. This release it called four *more* live keys
> dead, because Home's tiles carry two of them — `{ key: …, subKey: … }` —
> and the check matched the literal word `key:`.
>
>     asked     is the field called `key`
>     mattered  is the field named for holding a key
>
> It matches the suffix now, so `subKey`, `labelKey` and `titleKey` are
> all the convention they look like. That is twice in two releases that
> this check has been wrong in the same direction, and both times its
> advice — *wire them, or delete them* — pointed at working code.

## app-v0.46.1 — QRME app-v0.46.1

- Published: 2026-08-05
- Commit: `473dbaa7646ff61cdcb42baf8f6d91abc52564ec`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.1>

> ### The room, the conversation, and the door to both
>
> The console-untranslated record falls **116 → 69**.
>
> **Rooms** — the channel list held its five English labels in a `const`
> beside the ids. It holds keys now, so the badge and the dropdown read the
> same row and a sixth channel cannot arrive half-named.
>
> **Chat with —** the role picker, the where-you-are fields, and the four
> notes a reply can carry about itself: a specialist handoff, a moderation
> hold, which role the profile chose, or that it adapted to where you said
> you were.
>
> **Inside a room** — the paragraph explaining that lending your microphone
> is a disclosure rather than a setting, translated whole.
>
> 64 keys across three screens.
>
> ### Two guards, one of them for a mistake I keep almost making
>
> `test_no_key_is_translated_into_ten_languages_and_used_nowhere` called
> five live keys dead. They are held in a table — `{ id: "chat", key:
> "rms.ch.chat" }` — and looked up as `tr(c.key, lang)`, so there is no
> literal after `tr(` anywhere and all five render. That is the same shape
> as the `nav.` template the check already excuses, arriving by a second
> road, and its advice — *wire them, or delete them* — would have had
> somebody delete five working translations. A `key:` field now counts as
> a lookup written down early, and the comment says why.
>
> `test_no_translation_is_carrying_an_english_word` is new. Every check
> before it asks whether a row *exists* and whether it has its ten
> languages; none can tell a finished Japanese sentence from one with
> `travels` still sitting in the middle. Two rows were drafted that way
> while writing this release — one `someone`, one `travels` — and both
> were caught by re-reading, which works right up until it doesn't.
>
>     asked     is the row translated
>     mattered  is the row translated all the way through
>
> The rule is narrow so it can be trusted: `ja` and `zh` only, a lowercase
> Latin word of four letters or more, present in the row's own English,
> standing bare rather than inside 「」, and only in rows whose English is
> prose rather than a list of values — `advance / assist / cancel` is
> three names, not a sentence, and demanding they be bracketed would make
> a placeholder worse in service of a rule about sentences. It passed on
> the whole table first run; verified by putting `travels` back.

## app-v0.46.0 — QRME app-v0.46.0

- Published: 2026-08-05
- Commit: `6d7ad6e59a4102776c937e002bba0c41bd7f1e4f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.46.0>

> ### The wall, the guide, and the blend
>
> The console-untranslated record falls **180 → 116**, and every one of the
> sixty-four rows went — no keeps this round.
>
> **Wall** — the For You feed. `Links from {platforms} render right here`
> was three fragments around a value and is now one sentence; the emoji
> labels keep their glyph and translate the word beside it, because `💬`
> is a picture and *comments* is not. The moderation refusal, the
> withdrawal, and the two words a card falls back to when it has no name —
> *You* and *someone* — were string literals nobody would have found by
> reading the screen for English.
>
> **Show me around** — the walkthrough's own copy, including the paragraph
> about why written answers keep working when a provider is down. The
> step's screen list has singular and plural rows, and `no screen` is its
> own row rather than an English default sitting inside a ternary.
>
> **Blend a Profile** — the sentence explaining what blending *is* bolds
> its main clause in the middle of itself, so it is one row with that
> clause as a hole. Splitting at the `<b>` would have handed a translator
> *"Blending"* and *" whose persona mixes"*, which is not a sentence in
> any of the ten. The four form refusals — sign in, pick two, name it,
> your birthdate — are translated too; they are the only text most people
> will see on this screen before it works.
>
> 85 keys across three screens, ten languages each, exact-sync held in
> both directions.

## app-v0.45.9 — QRME app-v0.45.9

- Published: 2026-08-05
- Commit: `9c5bf9934820a1850e22c1a4853fb5c91f6cbb89`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.9>

> ### The thing named, what leaves, and the mark it carries
>
> The console-untranslated record falls **254 → 180**.
>
> **One thing, named** — six reads with six different answers to who may
> ask, and the paragraph explaining each is now a whole sentence rather
> than the words either side of an interpolated value. The campaign line
> was `{raised} of {goal} from {donors} donor(s) · {status}`: five
> fragments, and neither Japanese nor Chinese puts "of" between the two
> numbers.
>
> **What leaves, and on what terms** — the licence paragraph bolds the
> word *consult* in the middle of itself, so the sentence is one row with
> that word as a hole; it is an adjective in English and a prepositional
> phrase in most of the other nine, and it does not sit in the same
> place. The revoke result keeps its three separate outcomes — nothing
> ever left, deleted at the gateway, marked here but the gateway was
> unreachable — because a tick for all three would be the wrong
> reassurance in any language.
>
> **The mark, and what is said about it** — the objection copy, the held
> queue, and the sentence that an owner cannot resolve an objection
> against their own profile.
>
> 99 keys across three screens, ten languages each.
>
> **One row of the seventy-five stays, on purpose.** `AI ·` in TheMark is
> quoted rather than written: the sentence beside it says the line comes
> back with those two characters in front of whatever you type, and the
> server hardcodes them into `design.line`. Translating the quotation to
> `IA ·` would put a word on the screen that the product never produces —
> the paragraph would be describing a designation nobody is shown. It is
> quoted the way `409` and `#tag` are quoted, and `console_untranslated.txt`
> now says so above the row rather than leaving the next reader to
> rediscover it.
>
> Two pinned prose checks were rewired as their sentences moved, and one
> of them tightened while it moved: `test_the_screen_labels_the_preview_by_
> whether_it_is_opted_in` matched a sentence in the screen, which after
> this round would have matched nothing useful — it now asks the screen
> for both lookups and the table for both English headings.

## app-v0.45.8 — QRME app-v0.45.8

- Published: 2026-08-05
- Commit: `391686342088182922125f5121102a3f77448f89`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.8>

> ### The money, the loan, and the firm
>
> The console-untranslated record falls **338 → 254**.
>
> **Where the money goes** — a campaign card said `$40.00 of $200.00 · 3
> donors` as four English fragments stitched by JSX, and a raised-of-goal
> line does not read in that order in Japanese or Chinese. It is one
> sentence in the table now, with the amounts as named holes, and the
> donor count is its own row because most of the ten languages inflect it.
> The designation copy is translated whole: *a campaign cannot exist until
> you say where its money goes.*
>
> **Lent skills** — the screen's four claims about what a grant is were
> string literals chosen inside a ternary, which is the shape that renders
> correctly and reads as English forever. All four are translated: that
> nothing is transferred, that the skill is used and never copied, that
> either party can end it alone, and that every use is written down where
> the borrower can read it too.
>
> **The ecosystem** — departments, roles, the demo org, the joint plan and
> the sealed tags. `item(s) pulled` and `· agent:` were fragments around a
> value and are now whole rows.
>
> 98 keys across three screens, ten languages each, exact-sync held in
> both directions.
>
> ### The table had 1519 rows and one of them was checked
>
> `test_no_tab_is_missing_a_language` reads `nav.*` and nothing else. That
> was the whole table when it was written — `l10n.ts` opens by calling
> itself "chrome localization for the desktop console" and for a long time
> that was true. Forty-six screens have moved into it since, one release
> at a time, and none of those rows had a completeness check.
>
> The gap is quiet in the way that matters. A key with no row at all
> renders its own identifier — `org.title` in the heading — and somebody
> reports it. A key missing *one* language falls back to English, which
> looks deliberate: a Hindi reader sees an English heading on a Hindi page
> with no way to tell an untranslated string from a forgotten one.
>
>     asked     is the sidebar translated everywhere
>     mattered  is the table translated everywhere
>
> `test_no_row_of_the_table_is_missing_a_language` now audits all 1519
> rows. It passed on the first run — every row was already complete — so
> this latches work already done rather than opening a backlog. Verified
> by deleting Hindi from one row and watching it name the row and the
> language.

## app-v0.45.7 — QRME app-v0.45.7

- Published: 2026-08-05
- Commit: `c8f4265e7b0634e0ad3e0bf369b6c8922ecddefb`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.7>

> ### The ledger, the name, and the stranger
>
> The console-untranslated record falls **425 → 338**.
>
> **Who is following, and what they pay** — the sentence that keeps a
> count of presses from reading as elapsed time now exists in both the
> singular and the plural row, in all ten languages: *each one because
> somebody pressed a button.*
>
> **In its own words** — the language a persona writes in is not a display
> setting, and the screen still says so. Claiming a handle replaces
> whatever the profile had, and the old one stops resolving; that
> paragraph is translated whole rather than broken around its bolded verb.
> This screen already bound `lang` to the *profile's* chosen language, so
> the console's own language is bound separately as `uiLang` — the two are
> different questions and now have different names.
>
> **Arriving, and strangers** — the `@handle` and `#tag` examples went
> into the table too. They are format examples, but the word after the
> sigil is readable text, and a Spanish reader is better served by
> `@usuario` than by `@handle`.
>
> 95 keys plus three placeholders, all ten languages, exact-sync held in
> both directions.
>
> The pinned check that a period is a press was tightened while it moved:
> it now requires the sentence **twice**, because the singular and plural
> rows are separate strings and the plural is the one somebody reads on a
> second press.

## app-v0.45.6 — QRME app-v0.45.6

- Published: 2026-08-05
- Commit: `46d52944bccbe32ca32b4e5438add9a381c4d366`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.6>

> ### The lobby, the screen in the corridor, and a voice
>
> The console-untranslated record falls **516 → 425**.
>
> **Who is in the game with you** — forty-seven `lby.*` keys. The long
> sentence about what a synthetic member is told carries the argument
> this product exists for: a lobby that reads as friends when it is one
> player and several generated voices is exactly the impression to
> prevent. It now reads that way in ten languages.
>
> **Where this is seen** — the front page a stranger lands on, the page
> you build yourself, and the screens it hangs on. The distinction the
> screen turns on is translated with it: only you can see the list of
> physical places, but what any one screen is *showing* is public,
> because a fixture in a corridor displays to whoever walks past.
>
> **Voice** — thirty-one of the seventy-three `prs.*`/`vce.*` keys are
> the voice half, and they include all three of the sentences that always
> hold: the watermark, the attestation that is not a checkbox, and the
> withdrawal that deletes the samples and stays on record.
>
> 120 keys, all ten languages, exact-sync held in both directions.
>
> The dead-key check passed on the first run this round — the message
> added at 0.45.5 did the work it was written for.

## app-v0.45.5 — QRME app-v0.45.5

- Published: 2026-08-05
- Commit: `5af50edf24d3e559cd5d72eef05042e377b7d8b8`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.5>

> ### The objection, the camera, and the market
>
> The console-untranslated record falls **616 → 516**.
>
> **Contesting a profile** — forty-three `con.*` keys. The screen a
> person reaches when a profile here represents them, and the two
> shortcuts that skip review entirely because a standing party's rights
> outweigh preserving the profile. The status values themselves stay in
> the API's vocabulary, untranslated on the wire, because `Contest.tsx`
> compares against the literal `"open"` — a guard already stands on that
> and it still does.
>
> **What is live here** — thirty-five `liv.*` keys. A camera, a
> microphone, a face worn over a camera, and the sentence underneath all
> three: whatever you put between yourself and the people around you,
> they are told.
>
> **Marketplace** — thirty-nine `mkt.*` keys, including the one about
> your own search scope: *yours alone, behind your own token — it does
> not tell a seller where you are.*
>
> 117 keys, all ten languages, exact-sync held in both directions.
>
> ### The guard that would not say what to do
>
> Keys written as `tr(cond ? "a" : "b", lang)` render perfectly and are
> invisible to the dead-key check, because neither key is a literal after
> `tr(`. That shape has stranded keys in **three consecutive releases** —
> twelve, then two, then four. The check caught all of them; its message
> said *"wire them, or delete them"*, which is wrong advice, since the
> keys were already wired.
>
>     asked     is this key looked up
>     mattered  does the failure tell you what to do about it
>
> The check now looks for its own blind spot: when a dead key is one
> selected inside a `tr(` call, it says so and prints the fix.

## app-v0.45.4 — QRME app-v0.45.4

- Published: 2026-08-05
- Commit: `e340e11e19aee529f3001c9200abb7356a4cf72d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.4>

> ### Two directions, one picture
>
> The console-untranslated record falls **724 → 616**.
>
> **Watch together** — a posted video, a shared position, and whoever
> you bring, including your own profiles. Fifty-two `wp.*` keys. The
> sentence worth having in ten languages is the one about the seek
> buttons: *this moves a number, it does not press play on anybody's
> device*. Bringing a profile in speaks in its voice, so it needs that
> profile's own owner token — also translated, because it is the
> difference between a refusal that makes sense and one that does not.
>
> **Delegation and work** — fifty-six `dlg.*` keys, both halves: what
> your own profile may do unattended, and you asking somebody else's to
> do something inside the limits its owner published. Including the two
> sentences the screen is careful about — that delegated work is for
> somebody already in a conversation, and that which sources the other
> owner scoped is not yours to know.
>
> **Where people find you** — thirty-one `bcn.*` keys. Two kinds of QR
> code that look identical and go opposite ways, and the count that
> cannot be previewed: opening a scan page *is* a scan, on every surface,
> because the server cannot tell an owner checking their own sticker from
> a stranger who found it.
>
> 139 keys, all ten languages, exact-sync held in both directions.
>
> The pinned check that the beacon screen names both directions was
> rewritten. Once the two words moved into the table, matching them in
> the screen succeeded off the key names — `bcn.away`, `bcn.here` — a
> check that could no longer fail for the right reason. It now asks the
> screen for the lookups and the table for the words.

## app-v0.45.3 — QRME app-v0.45.3

- Published: 2026-08-05
- Commit: `8b0c035d13a836fbf4c703cf09d14efcd001c507`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.3>

> ### Three more, and the wrist among them
>
> The console-untranslated record falls **848 → 724**.
>
> **Beginning, and passing on** — how a profile starts, what it is
> taught, who holds it after, and the one press from a wrist. Fifty-three
> `pas.*` keys. The load-bearing sentence is the one about succession:
> the single route in this product an owner token cannot open, because
> the signal it answers is that the owner has died or cannot act. It now
> reads that way in ten languages, with the bolded clause interpolated
> rather than the sentence broken around it. The four genesis questions
> took their example answers into the table as well — *warm, but needs
> quiet evenings* is what a form like that is actually read from, and
> leaving it English would have left the question English.
>
> **Signing** — forty-four `sgn.*` keys, including the sentences the
> screen refuses to soften: a check that did not run is drawn as not run
> and never as a tick, and a package handed to you is checked without
> this platform vouching for it.
>
> **Where it is marketed** — forty-one `plc.*` keys. The venue note
> itself is still rendered verbatim from the payload and never
> retyped; what is translated is everything the console says around it.
>
> One hundred and thirty-eight keys, all ten languages, exact-sync held
> in both directions.

## app-v0.45.2 — QRME app-v0.45.2

- Published: 2026-08-05
- Commit: `2972c2a1f13403612f546123d08eb5385f5e99af`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.2>

> ### The three biggest screens left
>
> The console-untranslated record falls **978 → 848**, and the three
> screens that come off it are the three largest on the backlog.
>
> **Exchanges** — the document two people sign before work changes
> hands. The manifest, the fingerprint it is signed against, and the rule
> the whole screen is arranged around: change one line and both
> signatures are cleared, visibly, in front of you. Forty-nine `exc.*`
> keys, and they include the sentences the screen *says back* after an
> act — *Signed — this manifest, and nothing it becomes later*, *The
> manifest changed, so both signatures were cleared* — which a Spanish
> reader was getting in English on the one screen where the wording is
> the product.
>
> **Reaching out, and what stops it** — four refusals that are four
> different facts, and the one of them that is not the owner's to lift.
> Forty-three `rch.*` keys, including the whole gates paragraph, which
> now interpolates its four bolded terms rather than being broken into
> five English fragments around them.
>
> **Visiting, and being found** — the visitor's side of a desk and the
> sticker a profile is left on. Fifty-seven `vis.*` keys.
>
> One hundred and forty-nine keys, all ten languages, exact-sync held in
> both directions and the dead-key guard green.

## app-v0.45.1 — QRME app-v0.45.1

- Published: 2026-08-05
- Commit: `fe2ec392b3bd3fe70c881bde1ce5add08c74f8f0`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.1>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No QRME code changed — JIM ran its
> console-untranslated record to zero, and every screen of that console
> now speaks all ten languages. QRME's own record stands at 978 and the
> work continues there.

## app-v0.45.0 — QRME app-v0.45.0

- Published: 2026-08-05
- Commit: `69c6a4c42c766c3dedbfef297bfe82602f698e66`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.45.0>

> ### Under a thousand
>
> Two screens, and the console-untranslated record crosses back into
> three figures for the first time: **1072 → 978**.
>
> The **Workshop** — the source material a profile is built from with
> the custody line drawn in plain sight, the dials that shape manner and
> never permissions, the CV, the specialists it hands work to, the forms
> it speaks through, the local fine-tune, and the public signature a
> stranger can check without an account — becomes forty-five `wsh.*`
> keys from forty-eight strings.
>
> **Bodies** — the market of robots checked against what the makers were
> actually saying, the binding, the task packs fitted to a particular
> machine rather than to the profile, the connectors, the command
> allowlist, what each skill will *not* do, and the owner-only log of
> everything a body in somebody's home has been told — becomes
> thirty-seven `rbt.*` keys from forty-six strings.
>
> All ten languages, exact-sync held in both directions.

## app-v0.44.9 — QRME app-v0.44.9

- Published: 2026-08-05
- Commit: `4df9f06f34508544a6c06d6b76657735f57a304d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.9>

> ### Who this profile is, in every language
>
> The Identity screen — the roster of your own profiles with the one
> badge shown as a thing that sits somewhere and can move, the
> verification claim and who checked it, anonymity with the withheld and
> the *not* withheld list at the same weight, the bubble, the rename,
> the export, the memorial, and the two different endings — is localized
> end to end: forty-nine strings become forty-seven `idn.*` keys in all
> ten languages. The sentences that carry the feature's honesty stay
> whole: that only you can see the roster because it is the link between
> your personas, that a withheld attestor would point back to a name
> this profile does not publish, and that deleting is erasure rather
> than retirement. The console-untranslated record falls **1121 →
> 1072**, exact-sync held in both directions.

## app-v0.44.8 — QRME app-v0.44.8

- Published: 2026-08-05
- Commit: `a1b85081d1b90c5fa312eb097fba091912fb4df1`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.8>

> ### The tail of the audit speaks
>
> The Remainder screen — the six small features that each had a couple
> of routes and no door, kept honestly on one screen: app feedback, mod
> registries, connected apps, excursions, the steering hub, playing
> alongside somebody, the id inspector, the portrait, and the two halves
> of a social connection — is localized end to end: fifty-one strings
> become forty-nine `rem.*` keys in all ten languages. The paragraph
> that explains why the outward publish runs the strict filter and
> stamps a credential moved into the table with the rest, and the test
> that pinned it follows it there. The console-untranslated record falls
> **1172 → 1121**, exact-sync held in both directions.

## app-v0.44.7 — QRME app-v0.44.7

- Published: 2026-08-05
- Commit: `61de37b292b1bbb1d7eef36d4a955866d54970d7`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.7>

> ### The handover speaks
>
> The Referrals screen — finding somebody qualified, the summary read
> before anything is signed, the signature that covers those exact
> bytes, the one-time link, the signing credentials with what each can
> actually sign, the certificate, and the clinician's own side of the
> door — is localized end to end: fifty-three strings become forty-nine
> `ref.*` keys in all ten languages. The sentences that carry the
> feature's honesty — that a profile is not a clinician, that nothing
> has gone anywhere yet, that the challenge is the hash of the words on
> screen, that a second open fails on purpose — are whole paragraphs in
> every language rather than fragments. The console-untranslated record
> falls **1225 → 1172**, exact-sync held in both directions.

## app-v0.44.6 — QRME app-v0.44.6

- Published: 2026-08-05
- Commit: `ee4b93844b6073f50a2693d5829be1ad2a32b303`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.6>

> ### The counter in the street speaks
>
> The Desk screen — the staffed counter itself: opening one with its
> attestation, the bell, the guests, the stream overlay, the beacons a
> stranger scans in the street and the card a scanner is shown — is
> localized end to end: fifty-six strings become forty-seven `desk.*`
> keys in all ten languages, joining the `desk.mine.*` and
> `desk.counter.*` keys the connection bracket already had. The
> console-untranslated record falls **1281 → 1225**, exact-sync held in
> both directions.

## app-v0.44.5 — QRME app-v0.44.5

- Published: 2026-08-05
- Commit: `582a3a502a22a943e5a19c3c31e4832c35dfc3df`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.5>

> ### The counter speaks
>
> The Selling screen — the seller's side of the counter: the offer, the
> licence holders, the earnings statement with its per-currency honesty,
> the payouts, the shop window and the place a listing names — is
> localized end to end: fifty-six strings become forty-seven `sell.*`
> keys in all ten languages. The mixed-currency caution and the claimant
> rule are whole sentences with named holes rather than fragments. The
> console-untranslated record falls **1337 → 1281**, exact-sync held in
> both directions.

## app-v0.44.4 — QRME app-v0.44.4

- Published: 2026-08-05
- Commit: `b6169fa75839a292453ab39128a9f70e150fcb39`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.4>

> ### The Control Center speaks
>
> The Settings screen — the console's Control Center, and the largest
> block left on the untranslated record — is localized end to end:
> sixty-six strings become forty-four `set.*` keys in all ten languages.
> The heavily interpolated paragraphs (the backend address, the model
> API key, the mail setup, the watermark recovery verdict, the honest
> warnings about which model actually answers) are whole sentences with
> named holes rather than fragments. The console-untranslated record
> falls **1403 → 1337**, exact-sync held in both directions.

## app-v0.44.3 — QRME app-v0.44.3

- Published: 2026-08-05
- Commit: `fea6f6eaaab37ed3d7d036702140fce399fc46a5`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.3>

> ### The backlogs shrink from both ends
>
> A ratchet round, worked the way the ratchets ask to be worked. The
> Assist screen — the largest single block on the gated console's
> untranslated record — is localized end to end: fifty-six strings
> become fifty-three `asst.*` keys in all ten languages, whole sentences
> with named holes rather than fragments, and the screen follows the
> profile's language the way the chrome does. The console-untranslated
> record falls **1459 → 1403**, exact-sync in both directions.
>
> The field-label evidence pass walked all 131 residue rows against
> every client form. Seven are now typed into forms this cut shipped —
> `beneficiary` and `designees` on the till, `comfort`, `humor`,
> `social_style`, `what_matters` and `sources` on the genesis and
> composite interviews — and each gains its ten-language label; the
> residue falls **131 → 124**. The rest stay on the identifier fallback
> with the evidence recorded: control-owned flags and client-filled ids,
> not things a person mistypes.

## app-v0.44.2 — QRME app-v0.44.2

- Published: 2026-08-05
- Commit: `b9865770e6016e59fa5a171200f28f7fa0a4f1e4`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.2>

> ### The last doors
>
> The per-shell doorless records run to **zero**: with this cut every
> route in the table has a door on iOS, Android and Windows. What was
> left was the deepest machinery — the interview a profile is born from
> (genesis and the hybrid blend, its constituents recorded in the open),
> the knowledge packs, the owner's simulations and offline fine-tuning,
> the cloud-contribution ledger that shows what would leave before it
> leaves, the profile's reach into a person's day (proactive check-ins,
> quiet hours, feedback, referrals), the license a stranger buys against
> an offer, and the senses (perceive, the microphone-lending vocabulary,
> the overlay catalogue, the experience list that refuses `years` by
> name).
>
> Twenty-seven routes gain their remaining doors — 21 on all three
> shells, plus the per-shell stragglers (health, the marketplace and
> pack listings, the signature policy and credential retirement, the
> desk stream join). **71 rows struck; the records fall to
> ios 0 / android 0 / windows 0**, and the emptiness itself is now a
> test: `test_no_route_in_the_table_lacks_a_door_anywhere`. Forty-two
> interface strings arrive in all ten languages on all three shells,
> and a live overload collision in the Android client
> (`beaconCard`) was found and renamed on the way.

## app-v0.44.1 — QRME app-v0.44.1

- Published: 2026-08-05
- Commit: `312bdce0511ef644284105389cb93699442c6552`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.1>

> ### The sticker, the queue and the stamp
>
> Six more blocks off the per-shell doorless record — the beacon a
> stranger scans on the street (with the desk sticker, the social
> presence beacon, and pairing the console onto a phone), the moderation
> queue the owner works, the reviews readers trust, the watermark that
> proves provenance, the media that rides the wall, and the wearables on
> the wrist. What they share is the street: every one is where the
> product meets somebody who did not open the app on purpose.
>
> Twenty-four routes gain doors on iOS, Android and Windows — **71 rows
> struck**; the records fall to ios 21 / android 26 / windows 24, under
> a guard that renders the rules rather than inventing them: the overlay
> never draws the face without the disclosure; only the owner moderates
> and a resolved message stays resolved; you can change what you said
> and take it back, with the row surviving for the trail; a review
> requires having actually talked to it; a real credential on altered
> content says both things; the caps are published before an upload
> fails and authentic media is never AI-marked; a room-facing microphone
> is refused with the reason. Thirty-four interface strings arrive in
> all ten languages on all three shells.

## app-v0.44.0 — QRME app-v0.44.0

- Published: 2026-08-05
- Commit: `e3dac88f2e08e0e9a7e5d1216a1e3fc1048dd3e1`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.44.0>

> ### The keys, the till and the lifeline
>
> Three more blocks off the per-shell doorless record — the account
> (signup, sign-in, the emailed code, the password reset, the OAuth
> doors), the money (the price list, subscriptions, orders, proceeds and
> campaigns) and the app's own status and help. Every one is the frame
> around the product rather than the product: the key that gets you in,
> the till that takes your money, and the line you pull when neither
> works. Until this cut a phone could hold a profile in its hand and
> still have to borrow a desktop to make an account, read a price, or
> ask what a light means.
>
> Twenty-four routes gain doors on iOS, Android and Windows — **72 rows
> struck**; the records fall to ios 45 / android 49 / windows 48, under
> a guard that renders the rules rather than inventing them: the address
> is proven before sign-in works; no button is an address oracle; a
> reset kills every old session; the price list is public and generated
> from the same table the gate reads; nothing bills on a timer; a donor
> gives to the names on the proceeds list and a campaign cannot open
> until those names exist; help writes nothing and is public on purpose.
> Forty interface strings arrive in all ten languages on all three
> shells.

## app-v0.43.9 — QRME app-v0.43.9

- Published: 2026-08-05
- Commit: `f6039821d93f86082f175647303f5bc52c1a6dab`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.9>

> ### The face it shows the world
>
> Nine more blocks off the per-shell doorless record — the portrait, the
> emblem and the badge, the page and its themes, the front, the surfaces,
> the blend, the bodies, the dials and the wrist — and what they share is
> that every one is how a profile *looks* to somebody deciding whether to
> trust it. That decision happens on a phone held at a bus stop, not at a
> desk, and until this cut the phone could not check a single one of the
> claims the desktop could.
>
> Twenty-four routes gain doors on iOS, Android and Windows — **72 rows
> struck**; the records fall to ios 69, android 73, windows 72, under a
> guard that renders the rules rather than inventing them: the portrait
> travels with its AI badge and whose likeness it is; the public badge
> withholds the attestor while a profile is anonymous; the page is the
> owner's to write and anyone's to read, its themes a closed set; the
> blend answers 404 on a non-hybrid rather than pretending; the same
> personality is checkable across every body while the list of bodies
> stays the owner's; the dials are 0–100 integers and intimacy never
> rises on a non-rated persona; and the wrist reuses the full apps'
> paths — same auth, same allowlists — so a tap from a watch can do
> nothing a phone could not. Forty-three interface strings arrive in
> all ten languages on all three shells, and three more request fields
> (`asset`, `emblem`, `surfaces`) now refuse with the label on the form.

## app-v0.43.8 — QRME app-v0.43.8

- Published: 2026-08-05
- Commit: `6f23e635fa173b30a42bb9fd94a672b2633849a3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.8>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No QRME code changed — JIM's watch bridge
> gained the device picker (Apple Watch, Wear OS, Fitbit, Garmin), the
> Fitbit-aware seed, and Bluetooth pairing for speakers, glasses, AR/VR
> headsets and spatial displays. QRME's profiles and shells are untouched.

## app-v0.43.7 — QRME app-v0.43.7

- Published: 2026-08-05
- Commit: `896a811886bd65c18ab8278304ed806531fe1860`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.7>

> ### The record, the veil and the exit
>
> Seven more blocks off the per-shell doorless record — the memory
> list, the record between the profile and one person, source material,
> the profile's own ledger, anonymity, verification, and the ways a
> profile ends — and what they share is that every one is a promise the
> product makes in its own marketing: you own it, you can read it, you
> can erase it, and you can leave. A promise that can only be exercised
> at a desktop is a promise with office hours. The phones now keep it.
>
> Twenty-five routes gain doors on iOS, Android and Windows — **75 rows
> struck**; the records fall to ios 93, android 97, windows 96, under a
> hundred for the first time — each rendering its backend's rules: the
> memory list exists for choosing what to erase, and erase sits next to
> read; the pair reads the pair's record (thread, engagement, clinical
> notes, adaptation) and nobody else — an injection that unguarded the
> raw conversation read walked past the first version of this round's
> guard, which now pins the stranger's 403 on all four reads and on the
> erase; the veil's limits are half the payload, with what anonymity
> does NOT withhold rendered first; the badge is a fact, not a word —
> level and attestor travel with it, one badge per person, and the
> roster of your other profiles answers only to your own token;
> departing, memorializing and deleting are three different ends with
> three different buttons, and succession is reviewer-verified because
> the owner token is exactly the thing that may be unavailable. A
> second injection dropped one language from one row on one shell and
> the full-list rule caught it. 40 shared strings per shell, in ten
> languages.
>
> The field-label residue falls 135 → 134: `verification_ref` is typed
> into the succession form on all three shells, so its refusal now
> names the label on the form; `anonymous`, a flag the veil's switch
> owns, stays on the identifier fallback the record's doctrine
> prescribes.

## app-v0.43.6 — QRME app-v0.43.6

- Published: 2026-08-05
- Commit: `b12e535c39932db8b3375c34ce4ec30fd811dbc8`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.6>

> ### The workshop in the pocket
>
> Six more blocks off the per-shell doorless record — workflows, the
> delegation envelope, the assistant's verbs, autonomous tasks under a
> revocable grant, rated placements, and domain specialists — and what
> they share is that every one is work the profile does when the owner
> is not watching. That is exactly the work an owner checks from the
> device in their pocket: what ran, where it paused, who was allowed to
> start it, and how to pull the plug.
>
> Twenty-eight routes gain doors on iOS, Android and Windows — **84
> rows struck**; the records fall to ios 118, android 122, windows 121
> — each rendering its backend's rules: a workflow pauses where the
> world has to answer, and advance and resume are different buttons
> because they are different acts; delegation is off until the owner
> declares it, the offer answers a bare GET and never names the grant,
> and delegating `research` without a grant is refused while the owner
> is looking (an injection that unguarded the workflow list went red
> before it shipped, as did one that quietly dropped a shell's
> specialist door); a task's grant can die mid-run and the refusal says
> so; a rated placement takes an adult-mode profile only and every ref
> resolves through the age wall; the specialists are the owner's to
> attach. 50 shared strings per shell, in ten languages.
>
> The field-label residue falls 140 → 135: `interactor_id`, `phases`,
> `items`, `text` and `specialist_profile_id` are all typed into this
> round's forms on three shells, so their refusals now name the labels
> on the forms; `grant_token`, minted by a button and never typed,
> stays on the identifier fallback the record's doctrine prescribes.

## app-v0.43.5 — QRME app-v0.43.5

- Published: 2026-08-05
- Commit: `f6c59904e250d3fc4e4e344fc87b52f33c1ec7a8`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.5>

> ### The seal, the mail and the screen
>
> Seven more blocks off the per-shell doorless record — signatures, the
> mail server, the room's ear, the wall screen, the plan, the handoff
> and the campaign — and what they share is an audience that is not the
> owner at the console: the person *accepting* a signature, the admin
> proving mail can actually leave the box, whoever walks into a room or
> past a wall panel, the account holder reading what their plan reaches,
> the provider on the far end of a handoff, and a donor arriving from a
> beacon scan with no account at all. Every one of those people is
> holding a phone, and until this cut the phone had no door.
>
> Twenty-five routes gain doors on iOS, Android and Windows — **74 rows
> struck**; the records fall to ios 146, android 150, windows 149 — each
> rendering its backend's rules: a verification asks nothing of this
> deployment (an empty package gets a verdict whose notes name the
> missing field, not an error); the mail read is public and the write is
> the deployment's, with the password never coming back out; the
> microphone disclosure is readable exactly where the microphone is — in
> the room, and an injection that widened it to anyone holding the room
> id went red before it shipped; what a wall screen shows is public on
> purpose and only its owner changes it; a lapsed plan keeps its
> profiles; a handoff exists only by consent, opens only by its token
> and dies revoked; a donation needs no token and closing the campaign
> needs the owner. 47 shared strings per shell, in ten languages — and a
> second injection that dropped one language from one row on one shell
> was caught by the full-list rule.
>
> On Windows the ceremony page's address is now taken off the same GET
> the web view will issue, so the door and the address cannot drift —
> and the last unstruck signatures row fell with it.
>
> The field-label residue falls 141 → 140: `faces` is typed into the
> wall-screen form on all three shells, so its refusal now names the
> label on the form; `interactor_id`, filled from the session rather
> than typed, stays on the identifier fallback the record's doctrine
> prescribes.

## app-v0.43.4 — QRME app-v0.43.4

- Published: 2026-08-05
- Commit: `fc2978f8c5441ffe226f3f8797fe93d76ceeb677`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.4>

> ### The body, the case and the lobby
>
> Five more blocks of the per-shell doorless record, and the shape of
> what was missing differs by block: the robot body's owner could not
> audit from a phone what the body had been told to do; the referral
> flow existed end to end with no phone on either side of it; the person
> who raised an objection could read their case on the console and not
> on the device in their pocket; a lobby's honest roster — what every
> callsign *is* — was unreadable exactly where people game; and the
> dock, whose whole job is pointing at where features live, could not
> itself be found.
>
>     asked     does the audit trail exist
>     mattered  can its owner read it from the device they carry
>
> Twenty-five routes gain doors on iOS, Android and Windows in one cut
> — **75 rows struck**; the records fall to ios 171, android 175,
> windows 173 — each rendering its backend's rules: the command log
> answers to the owner alone and intimacy is never a body dial (an
> injection that let it through went red before it shipped); a referral
> opens exactly once; the objection's reviewer verb refuses the owner by
> role; the roster names each member's kind; and every dock face carries
> a way out of the read-only pane. 45 shared strings per shell, in ten
> languages.
>
> The field-label residue honestly stays at 141: every candidate this
> round's forms touch — `signature_id`, `corner`, `state`, `face`,
> `outcome`, `robot_id` — is an enum member or a context-filled id,
> exactly what the record's own doctrine keeps on the identifier
> fallback.

## app-v0.43.3 — QRME app-v0.43.3

- Published: 2026-08-05
- Commit: `c682aeec5d620cb84b4d4c40462547bd317145d0`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.3>

> ### The place, the camera, the organization and the tour
>
> Four more blocks of the per-shell doorless record. The phone could
> stand in a room and not know whose corner it was, who had lent a
> microphone into it, or who was wearing what over their face — the
> disclosures the console has rendered since the live-place round, each
> addressed to everyone present precisely because a disclosure only its
> subject can see is not a disclosure. The camera existed with published
> refusals no phone could read. The owner's organization could
> coordinate and the phone could not found one. The guided tour could
> not be opened from the device most likely to be in a new user's hand.
>
>     asked     is the disclosure served
>     mattered  can the person standing in the place read it
>
> Twenty-seven routes gain doors on iOS, Android and Windows in one cut
> — **81 rows struck**; the records fall to ios 196, android 200,
> windows 198 — with the rules kept rather than invented: the camera
> opens with its refusals shown verbatim; only the holder opens a
> session and either party alone closes it; the organization answers
> only to its owner's account; the tour is anybody's. 44 shared strings
> per shell, in ten languages.
>
> ### The evidence rule, applied twice
>
> `minutes` and `lesson` leave the field-label residue (143 → 141): the
> camera's minutes box and the tour's step box now ask a person for
> them. `minutes` arrives as JIM's existing row, ported rather than
> written twice. `learner_id`, `interactor_id` and `holder_id` stay —
> context-filled ids, the honest fallback.

## app-v0.43.2 — QRME app-v0.43.2

- Published: 2026-08-04
- Commit: `16fcb338b187cc45e836db272babef8a4cb0becc`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.2>

> ### The crowd, the couch and the loan
>
> Back to the standing backlogs. Three blocks of the per-shell doorless
> record, read together: the phone could be liked and could not like
> anybody (nine audience routes), could be invited to a watch party the
> console started and could not start, seek, or speak in one (ten), and
> could neither lend a skill nor borrow one (ten).
>
>     asked     is the surface built
>     mattered  can somebody holding a phone stand in the crowd
>
> Twenty-nine routes gain doors on iOS, Android and Windows in one cut —
> **84 rows struck**; the records fall to ios 223, android 227,
> windows 225 — and the rules each block renders are the backend's, not
> the shell's: the numbers under the buttons come from one call; seek
> moves a number and presses play on nobody's device; a synthetic party
> guest carries the sentence that it has not seen the footage; a grant's
> terms are the vocabulary's own sentences, verbatim; and a gift is a
> gift — refused without a verified adult, irreversible by design.
> 45 shared strings per shell, in ten languages.
>
> ### The evidence rule, applied once
>
> `position_s` leaves the field-label residue (144 → 143): the party's
> seek box now asks a person for it on all three shells, which is the
> one direction the record moves. `host_id`, `lender_id` and `actor_id`
> stay — a context-filled id is not something a person types, and the
> identifier remains the honest fallback.
>
> ### A guard that sampled
>
> The ten-language check first spot-checked eight keys, and an injection
> walked straight past it: a row outside the sample lost a language and
> the test stayed green. The key list is now read off the iOS table and
> required, complete, on all three shells.

## app-v0.43.1 — QRME app-v0.43.1

- Published: 2026-08-04
- Commit: `20643ea7183b2451f26baa1019491d953e829cfd`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.1>

> ### The platform tells you what happened
>
> Every 0.42.x round built a way for one person to act on another — a
> message sent, a comment left under a post, a friendship extended, an
> exchange signed, a place on a stream granted — and every one shared a
> silence: the thing happened, and the person it happened to found out
> only by going to look.
>
>     asked     can the platform do this to a person
>     mattered  does the person ever hear about it
>
> `GET /profiles/{id}/inbox` is the window and `POST …/inbox/seen` is the
> one verb it takes. Five deeds note themselves at the deed, not at the
> router, so every path tells or none does. Three rules, each guarded:
>
> * **The inbox names the deed, never the words.** A row carries a kind,
>   an actor and a reference; the message itself stays behind the owner's
>   door where it already lives. The kinds are a closed set — a kind
>   invented in passing would render as its raw identifier in ten
>   languages at once.
> * **Your own deeds never land in your own inbox.** Telling somebody
>   what they just did is noise wearing the coat of news.
> * **A blocked comment produces no event, and a declined guest hears
>   nothing.** Announcing a thing the recipient can never see would be
>   the filter advertising its own catch; a decline delivers nothing a
>   person can act on.
>
> All four clients gain the door in the same cut — the console's Friends
> screen and each shell's People screen carry the card and the seen
> button, with the deed sentences in ten languages per shell.

## app-v0.43.0 — QRME app-v0.43.0

- Published: 2026-08-04
- Commit: `5490572e72b80a7a0e3aace5ea86c0eef8e1f775`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.43.0>

> ### The phone could be listed and could not do business
>
> Three blocks of the per-shell doorless record, read together, said one
> thing. The caller's side of a desk shipped long ago — ring the bell,
> join the stream, open a session — and no shell could ever *staff* one:
> open a desk, set its presence, decide who comes through, print the QR
> sticker that is its front door. The market screen could put a card up
> and could not search, price, place, sell or buy. Exchanges — two
> parties, one manifest, the platform's whole apparatus for agreeing to
> work — existed on no shell at all.
>
>     asked     can a phone be found on the platform
>     mattered  can a phone do business on it
>
> Forty-six routes, and a row for each in every one of the three records.
> iOS, Android and Windows each gain **Counter**, **Trade** and **Deals**,
> and each renders three rules the backend already decided rather than
> forming a fourth opinion: presence is the closed set the refusal names
> (`attended`, `away`, `closed`); both parties sign the same manifest and
> any change clears both signatures, each item accepted separately; and a
> desk is a real person, so opening one asks for the attestor and the
> basis rather than letting the refusal do it.
>
> **139 rows struck** — the largest bite taken out of this backlog since
> it was opened. The records fall to ios 251, android 255, windows 253;
> iOS's extra row comes off below, a door that was standing open all
> along.
>
> ### Two doors the guard could not see
>
> `clientpaths.IOS` knew one call shape: a path handed to `request(...)`.
> A route that answers **bytes** — the QR sticker, the still of a desk —
> is not fetched that way: the shell builds a URL and an image view does
> the GET. Two live doors read as absent.
>
> The third time this lesson has come round; Android's `URL(` form is in
> the file for it, and PDI's ported verb assumption was the second.
>
>     asked     does the shell call the transport helper for this route
>     mattered  does the shell fetch this route at all
>
> The new rule then failed the same way its predecessors did, and the
> suite caught it before it shipped: declared `verb="GET"` on the claim
> that a URL built this way is a URL to *read*, it reported a phantom
> `GET /marketplace/listings/{id}` — the older `removeListing` builds its
> URL the same way and sets `httpMethod = "DELETE"` two lines down. So
> the verb is read, exactly as Kotlin's `requestMethod` is — and reading
> it found a fourth door nothing knew about: `unlistLicense`, the same
> idiom, on the ios doorless record since the licensing round. The same
> correction lands in JIM and PDI, where it takes one false row off each
> of their ios records too: doors that had been standing open the whole
> time.
>
> ### A delete that worked reported a failure
>
> Driving the new bindings turned up the reason to drive them: several
> routes answer **204 No Content**, and all three shells decoded the body
> unconditionally. Zero bytes threw, so every successful delete put an
> error on the screen. An empty success now decodes as an empty object in
> each shell — and still throws for a response that genuinely needed
> content.

## app-v0.42.9 — QRME app-v0.42.9

- Published: 2026-08-04
- Commit: `a9be53149bd2f10bc820c02961de9d370678a67f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.9>

> ### The people around a profile reach the phones
>
> The community round built the friends list, the wall and comments, and
> every round since has treated them as done. The per-shell door audit
> said otherwise: nine routes with a door in the console and none on iOS,
> Android or Windows — twenty-seven rows sitting in the doorless records
> the whole time.
>
>     asked     does the platform have a social surface
>     mattered  can somebody holding a phone reach it
>
> A person on a phone was *on* the wall — their profile had one, others
> could read it — and could not post to it, could not see who the platform
> suggested they know, and could not take back a comment.
>
> Each shell gains a **People** screen carrying all nine, and each renders
> three rules the backend already decided rather than inventing a fourth
> opinion. **A pinned row gets no remove control** — the founder's two
> profiles refuse deletion with 409, and the list marks them `pinned`
> precisely so a client can leave the button off. **A blocked post or
> comment comes back to its author** — the write answers 201 with a
> status, because the words *were* recorded. **A suggestion carries the
> reason it was made**, including what the ranking never touches: source
> material, memories, anything vaulted.
>
> Fifteen strings per shell in ten languages, so the screens-untranslated
> ratchet does not move. The per-shell doorless records fall to ios 299,
> android 301, windows 299.

## app-v0.42.8 — QRME app-v0.42.8

- Published: 2026-08-04
- Commit: `5d9e19de800bb4f340285e7125024c4f3777634b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.8>

> ### The record said nobody asks; the forms had started asking
>
> `tests/field_labels_unmapped.txt` holds the request-model fields whose
> identifier *is* the label, on its own stated rule: "map one when a form
> starts asking a person for it." Nobody had re-read the record against
> the forms since it was written — and eighteen releases of new screens
> had quietly broken its premise for 107 of its 251 rows.
>
>     asked     is every field labelled or recorded
>     mattered  is the recorded reason still true
>
> The audit is mechanical and evidence-bound: a field counts as *asked
> for* only when a console input is literally bound to it. Those 107 —
> the Corner page's whole document, the desk, shop, exchange and signing
> forms, the settings screen's connection fields — now carry hand-written
> labels in all ten languages, worded identically to JIM's table where
> the products share a name. The 144 rows that remain are what the record
> always claimed to hold: enum members a control sets, ids a client fills
> from the resource it is looking at, and flags a switch owns.
>
> ### The lights say unreachable rather than vanish
>
> A field report in the same cut: the agent-lights pop-up — bottom-left,
> minimizable — gone. Driving the console in a browser showed it alive
> over a healthy backend; the disappearance lives on one path.
> `WatchLights` caught fetch errors with "keep the last face; a blip must
> not blank it" — and when the *first* fetch fails there is no last face,
> so the widget renders nothing, forever. A stored base address pointing
> at a backend too old to carry `/profiles/{id}/watch` turns that blip
> into a permanent absence that reads as the feature being removed.
>
> Unreachable is now a state the widget shows, not one it hides in: with
> a session present and no face, the minimized dot renders unlit gray,
> titled in the reader's language, and pressing it retries. The guard
> checks the dot is *reachable*, not merely present — the first draft
> checked presence, and an injected early `return null` sailed past it.

## app-v0.42.7 — QRME app-v0.42.7

- Published: 2026-08-04
- Commit: `e86d9e2ba0e289619378d59fb5c8ecf2b510ccdd`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.7>

> ### The person decides who reaches them
>
> The platform's people could befriend each other, meet at desks, buy from
> shops — and could not send each other a message, could not turn any of it
> off, and had no page of their own to point at.
>
>     asked     can profiles talk and present themselves
>     mattered  can the people behind them — on their own terms
>
> `qrme/social.py`, three surfaces sharing one idea. **Feature switches**:
> a named set per profile, default on, and everything downstream refuses
> *by naming the switch*, so "why can't I message them" always has an
> answer that is theirs. **Direct messages**: friends only — the
> friendship graph is the consent record the platform already keeps, and
> consent that only one person can end is not consent, so both directions
> must stand; one thread per pair; unfriending closes the door without
> deleting what was said. **The homepage sandbox**: a page like the old
> MySpace — headline, about, theme, links, top friends — validated so hard
> there is structurally nowhere to put a script: hex colors only, http(s)
> links only, plain text only, top friends from actual friends. A rejected
> edit changes nothing; the switch hides the page from everyone but its
> owner.
>
> Six routes, doored on all four clients: the console's **Your corner**
> screen (188) with the switches beside the other settings, and Corner
> panels on iOS, Android and Windows rendering their shells' own L10n
> tables in ten languages.

## app-v0.42.6 — QRME app-v0.42.6

- Published: 2026-08-04
- Commit: `efc89d7cde1825ba403b3d70c304805fc00b5de4`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.6>

> ### Version alignment
>
> The three products are cut together, so one number names one combination
> of all three. No QRME code changed — JIM gained booking and scheduling
> with reminders on its proactive ladder and opt-in email to the user's own
> verified address, and a JIM user can now book one of QRME's shop services as one act — the order and the appointment together.

## app-v0.42.5 — QRME app-v0.42.5

- Published: 2026-08-04
- Commit: `9de6ad267a6903ad3e77584bd50b2640fd96f17c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.5>

> ### A shop is not a desk
>
> The desk shipped as a geek squad for any industry — sessions, consent,
> connections, lent programs. What the platform still had nowhere to put was
> the ordinary case: a business or a person who simply sells things, and the
> nearest shelf would have hung "buy a candle" on the connection apparatus.
>
>     asked     can a specialist serve a caller at a counter
>     mattered  can a business or a person sell goods and services at all
>
> `qrme/shops.py` is the storefront on five rules: one shop per profile (a
> second open is an edit); an offering states kind, price in its own
> currency, and availability; the buyer is an *interactor* — the identity
> JIM's tandem already maintains; money is simulated with real accounting —
> fulfilment credits the creator ledger as `shop_sale`, and only fulfilment
> does; and both sides can let go, the buyer while `placed`, the seller by
> declining. Eight routes, and every one shipped with a door on all four
> clients in the same cut: the console (screen **187**, lesson included) and
> the iOS, Android and Windows shells — whose doorless records had one slot
> of headroom, which made "build the doors" the only honest option. A full
> shopping day writes nothing into any desk table, and a test proves it.

## app-v0.42.4 — QRME app-v0.42.4

- Published: 2026-08-04
- Commit: `39e646151a7a6ebb46594900a857c6fffbe9b636`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.4>

> ### Version alignment
>
> The three products are cut together, so one number names one combination
> of all three. No QRME code changed — JIM's money guardian gained its
> native doors on iOS, Android and Windows in this round, and the finance desks QRME lists beside a money warning are now reachable from the phone that shows the warning.

## app-v0.42.3 — QRME app-v0.42.3

- Published: 2026-08-04
- Commit: `c42064aa27d23d389880f48475f07852d6273819`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.3>

> ### The last thirteen unaudited screens
>
> `ui_screens.txt` carried two components as `unaudited` since the file was
> seeded — the softer word, and it was covering: neither `Discover` nor
> `Wall` had ever been drawn. Both shipped in the community round and were
> iterated on for thirty versions with nothing in the gallery, which means
> `undrawn=0` was false for exactly that long.
>
>     asked     is every component accounted for in the manifest
>     mattered  does every component have a drawing
>
> Screens **185 Discover** (the starter collection, tag search, befriending
> from the card) and **186 Wall** (the For You feed and its facade contract —
> nothing loads from another platform until the viewer presses play) close
> the column. Both ceilings now read zero and the slack test keeps them
> there: from here a surface either has a drawing or fails the suite.

## app-v0.42.2 — QRME app-v0.42.2

- Published: 2026-08-04
- Commit: `2b32051fe32c0f984e32332a7f2b3d577ab2b3d3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.2>

> ### Version alignment
>
> The three products are cut together, so one number names one combination
> of all three. QRME's part in this round is one door: `GET /desks` now
> serves JIM's money warnings, which list real finance desks — people with
> trades and locations — beside the tandem specialist as places a warning
> can send somebody.

## app-v0.42.1 — QRME app-v0.42.1

- Published: 2026-08-04
- Commit: `8fcf8c9b99cfeb7748b15acdfdf52e1f2cde6040`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.1>

> ### The starters can answer for their own trade
>
> ### The finding
>
> The Starter Collection's grounding stopped at one Field Pack per industry —
> three items, installed in 0.3.1 so a physician persona would stop answering
> from tone alone. That fixed the cold start and no more: ask Dr. Osei what
> she actually knows, what she can do for you, or who she works with, and the
> honest answer was three pamphlets. The persona budget renders `sources[:8]`,
> so five of her eight seats were empty.
>
>     asked     does the starter have source material
>     mattered  can the starter answer for its own trade
>
> ### What shipped
>
> `qrme/dossiers.py`: one dossier for every starter — the thirty-three and
> Vivienne Sable, by name, so a missing entry is a failing test rather than a
> quiet gap. Each installs:
>
>   * **What I know** — the trade in depth, in the starter's own voice;
>   * **Skills and services** — what they can actually do for somebody,
>     including across a desk session, with lent programs and skills;
>   * **Colleagues in the collection** — who they refer to and why, composed
>     from the same list that installs the *real friendships*, so the sentence
>     the persona says and the API's friends list cannot disagree;
>   * skill chips widened from three marketplace tags to eight or more.
>
> Installed by seed and by the startup repair — the dossiers arrive on the
> first launch after the upgrade, blank-aware per part so an owner's edits are
> never overwritten, and idempotent so a second seed press stacks nothing.
>
> Vivienne's dossier keeps the rated tier's hard lines in its own text:
> fictional by necessity, everything behind the age wall, referrals to the
> collection's ordinary professionals.
>
> ### The dossier nearly starved the pack
>
> The first draft installed the dossier and left `_ground`'s blank-only check
> alone — so on the repair path the dossier arrived first, the pack's check
> saw "not blank", and every un-grounded deployment would have received the
> dossier *instead of* its Field Pack, forever. The 0.3.1 grounding tests
> caught it: `grounded` came back 0 where 34 belonged. The pack's blank check
> now excludes the dossier's three titles — the deployment's own writing is
> not an owner's decision.
>
> ### Checks
>
> `tests/test_the_starters_know_their_trade.py`, 77 tests: the roster and the
> dossiers are the same set in both directions, every dossier clears
> substance floors, colleagues resolve and nobody refers to themselves,
> every named colleague is an actual friendship, the six sources fit the
> eight-seat prompt budget, and a distinctive phrase plus a colleague's name
> reach the rendered prompt.
>
> Two injections. The second earned its keep against this file's own first
> draft: removing the friendship install left `friends >= 2` green, because
> the two founder profiles alone satisfy a floor of two.
>
>     asked     does the starter have two friends
>     mattered  are the named colleagues among them
>
> The check now asks for the colleagues by id.

## app-v0.42.0 — QRME app-v0.42.0

- Published: 2026-08-04
- Commit: `327fffcce73daf84b766cd1e740f8cd541053d50`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.42.0>

> ### The desk can finally do the job
>
> ### The finding
>
> Everything on a desk let a person *reach* it — the card, the bell, the
> stream, the printed code on the shop door. Nothing let the desk do the work
> those doors exist for. A repair counter's whole trade is "hand me the
> thing": the staffer takes the caller's screen, their machine, a program, and
> works on it — Geek Squad, for whatever trade the desk is in. QRME had the
> counter and no way to pass anything across it.
>
>     asked     can a person reach the desk
>     mattered  can the desk then do the work
>
> ### What shipped
>
> Desk service sessions and connections, with the counter's physics kept:
>
>   * The desk's token opens a **session** with one named caller (optionally
>     citing the bell that started it — and only its own desk's bell).
>   * Inside a session the desk **offers** a connection — `screen_share`,
>     `remote_control`, `app_access`, `file_drop` — naming the target and, for
>     remote control, a written scope the caller is shown. Every offer carries
>     what agreeing to it *means*, in words, from one server-side table.
>   * An offer grants nothing. The **caller's accept** is what mints the link
>     token, and it is returned to the caller alone — it is their machine the
>     link opens, so the secret is theirs to hand to their own tooling. The
>     desk's view of the same session never carries it.
>   * Either side ends a link or closes the session; closing ends every live
>     link. Ending **NULLs the token in the row** — an ended connection has no
>     secret left to present, structurally, not by a flag someone checks.
>   * On a rated desk the accept sits behind the same verified-adult gate as
>     the card, the view, the bell and joining.
>
> Eight routes, all doored in the console the same round: the staffer's
> sessions live on the Desk screen beside the bell; the caller's side —
> offers, the yes/no, the live token, the end — sits on the visitor half.
>
>
> ### And the skill, not just the link
>
> "Program access such as Cursor, and skills" is the counter's whole trade,
> and half of it already existed: `sharing.py` has always been able to lend a
> skill two-party — offer, accept, a use log, either side closes — and a desk
> was already a surface it could ride. Two pieces were missing and are in:
>
>   * **`app` is a lendable kind** — "a connected program they can drive."
>     The program stays the lender's, driven through their own connector; the
>     borrower gets uses, one at a time, each written down.
>   * **A counter session is a surface** (`desk_session`), and closing the
>     session calls `sharing.close_surface` the way exchanges and watch
>     parties already do — so "use Cursor for this repair" dies with the
>     repair. Driven by removing the call and watching the lent program still
>     answer after the counter closed.
>
> ### The ratchets earned their keep
>
> The first full-suite run at this version failed four of this repository's own
> guards — the field-label map, the refusal table, the console-language
> snapshot and the per-shell doorless records — because a feature round adds
> fields, refusals, strings and routes, and every one of those surfaces is
> ratcheted. Each was settled the way the ratchets demand rather than by
> loosening them: the new fields and refusals are translated in ten languages,
> the Desk screen's new strings went through the console's own `t()` table
> instead of onto the backlog, and the eight new routes got real doors on all
> three native shells — models, client functions and screen calls — because the
> shell records had no headroom to record them as debt.
>
> ### Checks
>
> `tests/test_the_desk_can_finally_do_the_job.py`, fourteen tests. Driven
> three ways before it was believed: making `end` keep the token in the row
> fails the row-level check ("NULLed is the contract"); handing the desk's
> view the token fails the caller-alone check; letting any desk's ring seed a
> session fails the queue-laundering check.

## app-v0.41.0 — QRME app-v0.41.0

- Published: 2026-08-02
- Commit: `dc8a715dd2582bcd005ca3d1126d1030b92eeca0`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.41.0>

> ### The workflow round-trips and nothing walked the whole arc
>
> ### The finding
>
> `qrme/workflows.py` opens by naming three properties a delegated, multi-phase
> goal has to keep:
>
>   * memory is carried forward between phases,
>   * every phase is generated through the profile's persona,
>   * and `confirm` pauses for a human before the work goes out.
>
> Each had unit coverage on its own side of the wire. QRME tested `advance`.
> JIM tested `handoff.start` against a stub. What nothing did was walk the arc
> end to end: `suite/smoke.py` — the one check that boots all three products
> together — seeded them, wired the tandems, drove a single exchange, proved its
> custody through the vault, and stopped. `start_workflow`, `advance` and
> `specialist_tasks` were never called across the boundary at all.
>
>     asked     does the workflow round-trip
>     mattered  does anything walk the whole arc
>
> ### What driving it found
>
> Two behaviours nothing had met end to end, both now recorded as steps rather
> than discovered as surprises:
>
>   * **Delegated work is Pro-gated.** The first `POST /users/{id}/specialist-tasks`
>     came back `402` naming `synthetic_agents`. The exchange the smoke check
>     already drove needs only the vault, which Basic has — so the run had never
>     touched that gate. The refusal is now asserted before the upgrade, because
>     "this is the tier that buys it" is the answer somebody deciding whether to
>     pay actually needs.
>   * **Delegation is off until the specialist's owner opts in**, and `research`
>     is refused unless a grant scopes what it may read. The run now proves the
>     default the way it proves the tier gate — by asking first and being told
>     no — then takes the owner's part: mints an owner token, creates the grant,
>     and `PUT`s the delegation policy.
>
> The arc then walks `research → draft → send` and stops at `confirm`, with
> `awaiting` naming what it is waiting for. Three phases carried forward, and a
> pause instead of an ending.
>
> ### Checks
>
> `tests/test_suite_smoke.py` grew from three assertions on one run to eight
> named checks over a module-scoped run: the tier gate is named, the owner had
> to opt in, memory crossed more than one phase, `confirm` paused rather than
> completed, and JIM's surviving row still names the profile that did the work.
>
> Driven three ways before it was believed:
>
>   * make `confirm` complete instead of pause — and note what that looks like
>     from the outside: **four** phases done rather than three. A check that
>     counted phases would have read the regression as a *fuller* pass. Only the
>     check that asks whether it paused fails.
>   * stop carrying memory between phases — the arc dies naming the phase list
>     it did not build.
>   * open the delegation gate — which took **two** edits, not one. Flipping
>     `delegation.offer`, the advertised answer to "do you accept work", got
>     nothing started: `delegation.start` re-checks the policy itself. The
>     advertisement is not the gate, and the second check is the one that holds.
>
> ### Also
>
> The failure the smoke fixture reports is now the step that died and how far the
> run got, rather than a truncated dump of the whole report with `...` where the
> answer was.

## app-v0.40.9 — QRME app-v0.40.9

- Published: 2026-08-02
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.40.9>

> ### The README said v0.18.0
>
> ### The finding
>
> The first bold line of every README in all three products read:
>
>     **Current release: v0.18.0**
>
> and the line directly beneath it said the three are *"versioned and cut
> together, so one number names one combination of all three"* — a convention the
> banner had stopped following at 0.18.0 and kept advertising for twenty-two
> releases.
>
> The release-history table underneath stopped at **0.30.6**. Seventeen shipped
> releases — 0.25.0 through 0.29.0, 0.30.7 to 0.30.9, and the whole 0.40.x line —
> were in `CHANGELOG.md` and absent from the page anybody actually reads. The
> changelog was right the entire time; the summary of it in front of the door was
> behind.
>
>     asked     is the release written down
>     mattered  does the front page say what shipped
>
> Reported from the README beside the video, which is the one place this was
> always going to be noticed and the one place no test was looking.
>
> ### Changed
>
> - The banner names `pyproject.toml`'s version; the table carries every release
>   from 0.25.0 on, backfilled from each product's own changelog.
> - `test_the_readme_says_what_shipped.py` — five tests, the same file in all
>   three: the banner matches the version, every release has a row, the newest
>   row is this release, no row names a release that was never cut, and a guard
>   on the scan itself.
>
> Two injections, both reproducing the reported defect exactly: the banner set
> back to v0.18.0, and the table truncated at 0.30.6 again.
>
> ### Five of the seven unaudited screens
>
> `ui_screens.txt` carried seven components whose drawings had never been
> confirmed one by one. Five resolve, and they resolve by reading the
> *component's own heading* rather than its name — which is exactly why they sat
> unresolved: `Campaigns` draws "Where the Money Goes", `Org` draws "The
> Ecosystem", `Simulate` draws "What Would They Do". Not one of those three
> shares a word with the component that renders it.
>
> `Discover` and `Wall` stay unaudited, and they are now the two worth looking
> at rather than five that were merely unlabelled: no screen in the gallery
> carries either heading, under that name or another. They may be genuinely
> undrawn — in which case `undrawn=0` has been false for as long as `unaudited`
> has been covering for it, and `unaudited` is the softer of the two words.
>
>     asked     is every component accounted for in this file
>     mattered  does every component have a drawing
>
> The ceiling moves 7 → 2.

## app-v0.40.7 — QRME app-v0.40.7

- Published: 2026-08-02
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.40.7>

> ### The record that outlived the code
>
> ### The finding
>
> `public_untranslated.txt` opened with a paragraph explaining that
> `Onboarding.tsx` — the screen every person in the world meets first — carried
> forty-odd English strings, that translating them was "its own round", and that
> a half-translated sign-up form would be worse than an English one. All of that
> was true when it was written.
>
> `The screen everybody meets first` translated them. `The pre-session backlog
> reaches its floor` took the count to four and appended its correction *below*
> the stale paragraph, which nobody struck:
>
>     What is left is not prose. A product name, a punctuation mark, an
>     example address and an example code — strings that are the same in
>     every language. This is the floor, not a backlog.
>
> So the file held two statements about itself with the false one first. Read
> top-down — which is how anybody reads a file — it advertised a cleared backlog,
> and the correction was twenty lines further on. This round was planned off that
> paragraph before the extractor was run and the work turned out to be two
> releases old.
>
>     asked     is the record complete
>     mattered  does the record still describe the code
>
> The numbers were right the whole time. The prose around them had outlived the
> thing it described, and a record only works if a reader can trust the first
> thing it says.
>
> ### Every ratchet now leads with what it is
>
> `# status: floor|backlog — N rows`, on the first line, with the count checked
> against the rows beneath it. `floor` means the remainder is permanent and is
> not work; `backlog` means somebody still owes it. The two cannot be told apart
> from the numbers — `console_untranslated` sits exactly at its ceiling with
> 1,459 strings still to translate, and `public_untranslated` sits exactly at its
> ceiling and is finished — which is why the file has to say which it is, in a
> line that cannot drift from its own contents.
>
> A third check was written and struck before it shipped: *a file calling itself
> a floor must sit exactly at its ceiling*. It fired on `native_untranslated.txt`,
> which the last release took from three rows to none — a floor of zero under a
> ceiling of three, and the best kind there is. `floor` is a claim about what the
> remaining rows **are**, not how many, and a check that pretended otherwise
> would have been one more guard answering the question next to the one that
> matters.
>
> ### The reasons move next to the rows
>
> `unused_native_bindings.txt` recorded two bindings whose justification lived in
> the guard's module docstring — true, careful, and one file away from the list
> it explained. A record whose justification is somewhere else reads, at the
> place somebody actually looks, as an unexplained backlog: the shape this audit
> found seven times in `0.40.5`. Every row now carries its reason on the row, and
> a new check refuses one that does not.
>
> ### Changed
>
> - `tests/test_a_record_that_outlived_the_code.py` — three tests, and the same
>   file lands in all three products.
> - `public_untranslated.txt` rewritten so the current state leads and the
>   history is kept below it, labelled as history.
> - `unused_native_bindings.txt`: one row per binding, reason after an em dash;
>   `_recorded()` reads the name and `test_every_recorded_binding_says_why_it_is_recorded`
>   refuses a bare row.
> - Status lines on all five ratchets here.
>
> Three injections: the stale paragraph put back above the status line, a status
> count drifted from its rows, and a reason stripped back off a binding — each
> caught by a different check.

## app-v0.40.6 — QRME app-v0.40.6

- Published: 2026-08-02
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.40.6>

> ### The stranger's language, finished
>
> Two rounds ago every shell learned to work out what language its reader speaks
> without a profile — `Locale.preferredLanguages`, the system locale list,
> `CurrentUICulture` — and the round stopped there, on purpose: twenty-odd
> sentences on each of three screens was its own round, and half-porting them
> would have been the per-client mistake in miniature. The remainder went into
> `native_untranslated.txt`, which only shrinks.
>
> This is that round. The accountless screen — the one a person reaches when they
> have found a synthetic profile of themselves, or are holding a screenshot and
> want to know whether a person wrote it — now speaks ten languages on iOS,
> Android and Windows.
>
> ### Ported, not translated again
>
> The console has carried these sixty-four `pub.*` rows in ten languages since
> the browser's half was done. The shells took those rows rather than
> commissioning a second wording of the same sentence: two wordings is two things
> to keep in step, and the drift shows up first in the language nobody here
> reads. Four keys are new, and all four name UI only a shell has — a sheet's
> dismiss button, two client-side validation lines, and a placeholder.
>
> The counts fell with it: **iOS 280 → 260, Android 195 → 181, Windows 279 →
> 262.** Windows fell furthest per screen because every one of its sentences was
> a XAML attribute, which is written once at parse time and cannot be re-read
> when the language changes; localizing them meant moving them to the code-behind
> first.
>
> ### The ratchet was checking the record, not the screens
>
> `native_untranslated.txt` held the line at three entries and only shrank — and
> could have been driven to zero by deleting three lines, with all three screens
> still in English.
>
>     asked     is the backlog written down and shrinking
>     mattered  did anything get translated
>
> `test_no_accountless_screen_has_english_of_its_own` now reads the screens. It
> borrows the sibling guard's extraction patterns rather than writing its own,
> because two definitions of "an English string on a screen" is two numbers that
> can disagree, and the disagreement would live in whichever one nobody reads.
>
> ### Changed
>
> - 33 `pub.*` rows in ten languages added to each shell's `L10n` table, plus a
>   `fill` helper: the console's rows carry `{id}`, `{now}` and `{matched}`, and
>   building those sentences by concatenation instead is how a translation ends
>   up in English word order in nine languages.
> - `prior_status` added to `ObjectionOpened` on all three shells and
>   `examined_windows` to Android's and Windows' `WatermarkRecovery` — both
>   returned by the API since those routes shipped, neither modelled, and the
>   console's sentences name them.
> - Every one of the three screens resolves its language once, at the top, so no
>   call site can quietly fall back to the profile's setting.
> - Six new tests. Four injections: an English sentence back on one shell, a
>   language taken from the profile, a string put back into XAML, and a row cut
>   to three languages — each caught by a different check.
>
> One literal is declared rather than translated: `prf_…`, the prefix of every
> profile id, which is `prf_…` in all ten languages.

## app-v0.40.5 — QRME app-v0.40.5

- Published: 2026-08-02
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.40.5>

> ### The door they closed was the owner's
>
> Deletion in this product retires the owner's token. It retires nothing anybody
> else holds, and every audit that walked up to a terminated profile through an
> owner-gated route was told 401 and went away satisfied.
>
> `POST /profiles/{id}/license/acquire` is authorised by the **buyer's**
> interactor token, which termination never touches. Driven end to end against a
> profile whose subject objected and whose objection was upheld:
>
>     POST /objections/{id}/resolve   200  {"status": "upheld",
>                                           "profile_status": "terminated"}
>     POST .../license/acquire        201  the licence sells, the fee credits
>     POST .../license/{g}/derive     201  a new profile, seeded from the
>                                          erased persona, owned by the buyer,
>                                          with its own owner token
>
>     asked     can the owner still act on a terminated profile
>     mattered  can anyone still act on it
>
> The same hole one status over: a profile **restricted pending review** — the
> one whose subject is arguing in that moment that it should not exist — could be
> bought and cloned throughout the review. `succeed_profile` already refuses to
> hand a contested identity to a new owner, and `has_open_objection` sits in the
> same module for that check. Succession hands over the profile; derivation hands
> over a *copy* of it, permanently, to a stranger, and never asked.
>
> ### The count
>
> Seven tables carry a `profile_id` beside a revocation flag or a live token — a
> capability somebody else holds over this profile. **Termination touched none of
> them.** Not the licence, not the skill grant, not the handoff package, not the
> paired wrist, not the voice consent, not the contribution log. `_terminate`
> walked fourteen tables and its docstring is about *reachability*; on
> reachability it was right, and capabilities were a list nobody had written.
>
> ### Changed
>
> - `licensing.set_license`, `acquire_license` and `derive_agent` now call
>   `common.require_may_publish` — 410 for a departed or terminated profile, 403
>   for one under objection review. The gate at `derive` is the one that catches
>   a licence bought while the source was active and cashed in during the review.
> - `governance._terminate` revokes every capability a third party holds:
>   `license_grants`, `grants`, `handoffs`, `contribution_log`, `voice_consents`
>   and `wearables`, and takes the standing licence offer down with them.
> - `tests/test_termination_revokes_more_than_the_owners_token.py` — eleven
>   tests. The generalisation reads the schema rather than a list in the file, so
>   a capability table added next release is in scope by construction; the one
>   exemption (`referrals`) carries its reason, because an unexplained exemption
>   is what seven ungated tables looked like.
>
> A profile already derived under a licence bought while its source was active is
> left alone: it is its buyer's profile, with its own owner and its own
> provenance line, and tearing it down is a different decision from this one.

## app-v0.40.3 — QRME app-v0.40.3

- Published: 2026-08-02
- Commit: `8fa323150792e149a17699dacc863da2d8e6f7cd`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.40.3>

> ### The provenance named the model that was asked, not the one that answered
>
> `content_provenance` is this product's central claim, and its own docstring
> says so: *the verifiable basis of a piece of persona-generated content: which
> model produced it ... so nothing the platform emits is a black box.*
>
> It read the profile's **stored preference**:
>
> ```python
> "generated_by": llm.resolve_choice(llm.get_choice(profile["id"])),
> ```
>
> Meanwhile both network wrappers degrade rather than fail.
> `llm.FallbackProvider` catches any exception from the primary and returns the
> local stub's text, logging a warning. `cloud.CloudProvider` did the same and
> did not even log.
>
> So an owner sets their profile to Anthropic and brings their own API key. The
> key expires. The next post is written by the stub on their own machine, stamped
> `generated_by: "anthropic"`, watermarked, and published — and the only trace is
> a log line addressed to nobody.
>
>     asked     which model was this profile set to
>     mattered  which model actually wrote this
>
> **Degrading is still the behaviour.** A model outage should not take the
> product down, and that decision has not changed. What changed is what the
> platform then *says* about the result.
>
> ### The rule was already written down, in the other product
>
> JIM-mini's `FallbackProvider` has carried it in its docstring for releases:
>
> > The degrade is recorded on the instance (`answered_by`, `failure`) so a
> > caller can tell the user the truth about who actually answered — **a log line
> > the user will never read is not disclosure.**
>
> The product that had the rule was the health app. The product that needed it
> was the one whose premise is that generated content carries a trustworthy
> account of where it came from.
>
> ### What was built
>
> * A request-scoped record of who actually generated — the same idiom this
>   module already uses for the caller's API key, chosen because every call site
>   is `provider_for_profile(id).generate(…)`, built and discarded inline with
>   nothing left to interrogate.
> * Both wrappers record on **success and failure**. Recording only the degrade
>   leaves a stale one describing a later answer that was perfectly good.
> * `generated_by` now reports the truth, with `degraded_from` beside it —
>   without that second field a record that suddenly says "local fallback" reads
>   as somebody changing a setting rather than a credential going dead.
> * The console shows it, in amber, on the chat surface. A record nobody can see
>   is the same defect one layer up.
>
> ### The caller's own key never rides along
>
> The reason for a degrade is now shown to the person and written to the log, and
> it comes from an exception this codebase did not raise. Some HTTP clients put
> the whole request — headers included — into the string form of their errors,
> and on this path the interesting header is the caller's API key. `llm.scrub`
> removes it before the reason is recorded or logged.
>
> ### The generalisation
>
> A structural check requires that **every** `generate` answering a provider
> failure with somebody else's text records who answered. Two such wrappers exist
> today; the defect was that one of them was silent, so a check naming the known
> classes would have passed while a third went on lying.
>
> Its first draft read only dotted calls and reported the wrapper that had just
> been fixed — `cloud.py` calls `llm.note_answered_by(...)`, `llm.py` calls its
> own `note_answered_by(...)` unqualified.
>
>     asked     does the handler call llm.note_answered_by
>     mattered  does the handler record who answered

## app-v0.40.2 — QRME app-v0.40.2

- Published: 2026-08-02
- Commit: `2139d5addeb8ec9f6df2bc9978dfe7bac62543a2`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.40.2>

> ### The refusals, finished
>
> 0.24.0 translated the eleven refusals any route can raise and **wrote the rest
> down**. 142 sentences sat in `tests/refusals_untranslated.txt` from that day to this — the sentences
> this product says when it says no, still English on an account that had chosen
> otherwise.
>
> An owner who set Portuguese got a Portuguese sidebar, Portuguese answers from
> the model, and English the moment they were told no.
>
>
>     asked     is the refusal translated
>     mattered  is every refusal translated
>
> All 141 are now in `_REFUSALS`, in the nine languages beside English. The
> record is a decision rather than a backlog for the first time: one sentence, the `QRME_ADMIN_TOKEN` misconfiguration its own header
> already argued should stay English, because the person who can act on it is
> an operator and the fix is the name of an environment variable.
>
> ### What deliberately stays an identifier
>
> Field names, header names, enum values and environment variables are not
> translated and are not meant to read as words — `base_age, robot_id, QRME_PDI_URL, approve/reject`. They are the API's own
> names, the same string in every language, and declining them into a sentence is
> the half-in-one-language failure the table exists to refuse.
>
> ### The check that could not have caught a lie
>
> `test_every_translated_refusal_has_every_language` asks whether each row has
> all nine keys. A row whose nine values are the English sentence pasted nine
> times satisfies it exactly — and the table would then claim the refusal is
> handled while every reader still got English.
>
>     asked     does every refusal have every language
>     mattered  does every language say something other than the English
>
> That gap was harmless while eleven rows were added by hand and reviewed one at
> a time. It stops being harmless the moment 141 are added in one release, so
> `test_no_refusal_is_translated_into_english` was added first and injected
> against: an English value in one slot of one row fails it by name.

## app-v0.40.1 — QRME app-v0.40.1

- Published: 2026-08-02
- Commit: `f9fed8875b17631747e70a84744ec980044ba25f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.40.1>

> ### The objector could end a profile and could not read their own case
>
> `GET /objections/{id}/audit` is owner- or reviewer-gated, and its docstring
> gives the reason in its own words: *it can quote the objector's reason*. That
> gate is right about the free text and wrong about who it locks out. **The
> objector wrote that reason.**
>
> And they were not a bystander to the case. `POST /objections/{id}/withdraw`
> and `/revoke` are both public, and both **terminate the profile and erase its
> content**. The one party on this surface with no account — a contested person,
> sometimes a bereaved estate — could pull the lever and could not read the
> record of having pulled it.
>
>     asked     could the audit trail leak the objector's reason
>     mattered  who is the audit trail for
>
> **A second view, not a wider one.** `GET /objections/{id}/timeline` is public
> and localized and carries event, actor, time, sealed — and no `detail` at all.
> Not the objector's reason, not the reviewer's note, not the owner's. The shape
> of what happened is theirs; nobody's prose is. The `/audit` gate is untouched
> and `test_audit_is_owner_or_reviewer_gated` still passes.
>
> ### The two routes that end a profile did not speak the visitor's language
>
> Of the four public routes on this surface, the two that merely open or read an
> objection negotiated `Accept-Language`. The two that terminate a synthetic
> profile of a real person answered `{"id": …, "status": "withdrawn",
> "profile_status": "terminated"}` — three enum values and no sentence, in any
> language. Both now carry a translated `note` and a pointer to the timeline.
>
> `test_the_stranger_has_a_language_too.py` did not catch this and is not wrong:
> it checks that the public *strings* are translated, and a route that produces
> no sentence has no string to find.
>
>     asked     are the public strings translated
>     mattered  does every public route accept the visitor's language
>
> ### The language no client was sending
>
> The half of the same defect that lives on the other side of the wire. The
> routes above choose their language from `Accept-Language`. **No native shell
> was sending that header** — not this product's, and not either sibling's. The
> browser sends it unasked, which is exactly why the console looked correct and
> the three clients a contested person is most likely to be holding were the ones
> still answering in English.
>
>     asked     can the shell say it in the reader's language
>     mattered  does the reader's language ever reach the server
>
> One line in each shell's request helper, sourced from the device resolver the
> 0.30.x rounds had already built and nothing had used.
>
> ### Doors
>
> The timeline reaches the browser console, iOS, Android and Windows — event ·
> actor · time, sealed where the vault holds the row, in ten languages.
>
> ### Two guards corrected after they passed something they should not have
>
> * **Windows' localizer had one signature and now has two.** `L10n.T(key)`
>   reads `AppState.Current.Language`, which is the profile's setting — the wrong
>   answer on the one screen whose reader has no profile, reachable by writing
>   nothing at all. A `T(key, lang)` overload was added, and the arity guard,
>   which read the *first* declaration it found, failed six correct call sites.
>   It reads every declaration now.
>
>       asked     does every call match the signature
>       mattered  does every call match a signature that exists
>
> * **The new header guard used `any` where it needed `all`.** PDI's iOS client
>   builds requests in two places — the shared helper and the intake submit its
>   accountless recipient uses. Hardcoding `"en"` on one of them passed, because
>   the other was still right. The union hid a surface inside the guard written
>   to stop exactly that.

## app-v0.40.0 — QRME app-v0.40.0

- Published: 2026-08-02
- Commit: `e84b3302f2468604d54a2a8224bc3cc0de35921a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.40.0>

> > Staged as 0.30.10 and cut as **0.40.0**. The work below is unchanged; only
> > the number moved, from a patch on the 0.30 line to a minor of its own.
>
> ### A rule reversed, and said so rather than changed quietly
>
> `test_the_nav_is_translated_and_nothing_behind_it_is.py` records how many
> English strings sit behind this console's forty-six translated sidebar labels.
> It kept punctuation, under a rule written into the file in its own words:
>
> > Whitespace-bearing strings are kept: `" · "` is a separator somebody reads.
>
> That was a deliberate decision and it conflated two different things. A
> separator is **rendered**; it is not **unreadable to a non-English speaker**.
> There is no Portuguese for `·`, and none for `⚠`, `%`, `.` or `—` either.
>
>     asked     is this string rendered to somebody
>     mattered  is this string one a non-English reader cannot read
>
> **117 of the rows in `console_untranslated.txt` were punctuation** — so the
> count this file exists to state honestly was overstated by that much. The
> ceiling is corrected from 1576 to **1459**.
>
> The sibling product hit the identical thing one release earlier, in the shells,
> where the extractor counted `"\(dim): \(n)%"` as English prose; 0.30.9
> corrected that and this is the same correction one surface over. Twice now the
> question has been *did the extractor find a string* when what mattered was
> *did it find a word*.
>
> ### Nothing else changed here
>
> The round's work is the sibling product's: a QRME specialist could be reached
> from its monitoring path and not from its coach, so the person who typed a
> question got a weaker answer than the person whose watch noticed something.
> That fix is JIM-side. This repo carries the correction above and the version.

## app-v0.30.9 — QRME app-v0.30.9

- Published: 2026-08-02
- Commit: `934c69336579c4deae683fccec0f566a5dd0fb7e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.9>

> ### Two corrections carried in from the sibling's round
>
> **A type-compatible argument swap, guarded.** JIM's Android client declares its
> shared helper `request(path, method, body, token)`, and three calls in that
> shell — plus one in PDI's — passed the verb first. Both arguments are `String`,
> so nothing complained; the request went to `base + "GET"` with the method set
> to a path. Two of them shipped in 0.30.7.
>
>     asked     does the call have the right number of arguments
>     mattered  does it have them in the right order
>
> There is no Kotlin toolchain in this build environment, which is the whole
> reason it sat there — the same reason forty one-argument `L10n.t` calls sat in
> that shell before 0.30.7. `test_a_screen_nothing_opens.py` now reads the
> helper's own declared signature and refuses an HTTP verb in the path slot.
> This repo's Android client is clean; the guard is here because the surfaces
> are the same three shells written the same way.
>
> ### Last release's untranslated counts were overstated
>
> 0.30.8 measured how much of each native shell is English behind a translated
> tab bar. The extractor counted **any string literal containing a letter**,
> which counted format fragments like `"\(dim): \(n)%"` — whose only letters are
> variable names nobody reads — as English prose. Roughly seventy-five of them
> across the nine shells.
>
>     asked     does this literal contain letters
>     mattered  does this literal contain words a reader reads
>
> The ratchet caught it the honest way: by firing on a card in the sibling
> product that had just been fully localized. A measurement that reports a
> regression where an improvement happened is worse than no measurement.
>
> Corrected figures for this product, now in `native_screens_untranslated.txt`:
>
> | shell | was recorded | actually |
> |---|---|---|
> | iOS | 289 | **280** |
> | Android | 205 | **195** |
> | Windows | 326 | **279** |
>
> The percentages in 0.30.8's table were computed the same wrong way and are
> restated here: QRME 2.4% / 3.9% / 0.7%. The shape of the finding does not
> change — these are still the worst three of the nine, and this product's
> Windows shell still answers in the reader's language exactly twice.

## app-v0.30.8 — QRME app-v0.30.8

- Published: 2026-08-02
- Commit: `2323abc9023dc87848f76ef2ce1f9de5240049a0`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.8>

> ### The console guard, asked of the phones
>
> `test_the_nav_is_translated_and_nothing_behind_it_is.py` has been in this repo
> since the console rounds. It found forty-six translated sidebar labels in front
> of 1577 English screens, and said why that is worse than shipping no
> translations at all:
>
> > A uniformly English console tells a Spanish reader the truth on the first
> > screen they see. This one puts *Mercado*, *Amigos* and *Ajustes* in the
> > sidebar — the app apparently answering in their language — and then hands
> > them English the moment they click.
>
> It checks `app/src`. This product also ships three native shells, all three
> with a translated tab bar, and nobody had ever counted what is behind them.
>
> | product | iOS | Android | Windows |
> |---|---|---|---|
> | **QRME** | **2.4%** | **3.8%** | **0.6%** |
> | JIM-mini | 13.0% | 14.2% | 9.7% |
> | PDI | 8.9% | 10.2% | 3.5% |
>
>     asked     is the console's nav-vs-behind gap measured
>     mattered  is the phones' too
>
> These are the worst three of the nine. Last release recorded that this
> product's Windows shell answers in the reader's language exactly twice — the
> nav loop and one button — and left it standing rather than fixing it under
> cover of a round about something else. This is that round: 289 iOS, 205
> Android and 326 Windows strings, measured and ratcheted in
> `native_screens_untranslated.txt`.
>
> The ratchet runs both ways. The count may not rise, and the record may not sit
> more than twenty above the real number — a ceiling nobody is near is a ceiling
> somebody can drift back up into without it ever firing.
>
> ### Nothing is carved out here yet, and the record says which surface should be
>
> The sibling product took its **alarm surface** off these numbers this release —
> fourteen strings on all three of its shells, by name rather than by count,
> chosen because that is where English is a hazard rather than a discourtesy.
>
> This repo has no equivalent subset yet. The record names the candidate rather
> than leaving the absence implicit: the **objection and audit** screens, where
> somebody contests what a synthetic profile said about them. Those are
> decisions, not descriptions, which is the same test the sibling applied.
>
> ### Every slot is now checked to survive its translation
>
> A row whose English says `{name} was contacted` and whose German forgot the
> hole renders a sentence with the person's name missing from the middle of it.
> Nothing else would notice: the string is present, the language is right, and
> the sentence is wrong.
>
> Where a shell's table holds no slotted row — which is all three here today —
> the check **skips loudly** rather than passing on an empty set. A check over
> nothing is the failure mode this whole audit is named after, and a skip says so
> in the run output where a green dot would not.

## app-v0.30.7 — QRME app-v0.30.7

- Published: 2026-08-02
- Commit: `ed5bd6e644ebd9077e107ada39648eb90d4e495a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.7>

> ### A guard ported before this repo needed it
>
> `test_a_screen_nothing_opens.py` holds every screen a shell declares to being
> reachable from somewhere in that shell, and every call to that shell's
> localizer to the number of arguments the localizer actually declares.
>
> The finding is the sibling product's: the synthetic-self screen shipped into
> three shells with its wording in ten languages, unreachable in all three, and
> on two of them written against a signature it did not have. A guard already
> existed to check those strings were present. They were.
>
>     asked     does the screen have its wording
>     mattered  does anything open the screen
>
> This repo's twenty iOS views, sixteen Android screens and seventeen Windows
> pages are all reachable, and every localizer call matches its shell's
> signature. That is why the port happens now rather than after something here
> breaks — the last four rounds each turned up a guard covering one surface of
> four, and the surfaces are the same three shells written the same way.
>
> **Two false positives were fixed before the guard was kept.** The first
> version required a screen to be constructed as `Name()` with no arguments, and
> called `DeskView`, `SignatureView` and `VoiceView` unreachable — all three are
> opened from `ManageView` with arguments. The second matched Kotlin composables
> against a corpus containing their own `fun Name(` declaration, which makes
> every screen its own caller.
>
>     asked     is the name written anywhere
>     mattered  is it written somewhere other than where it is defined
>
> Comments are stripped before any of it. Twice already in this audit a check has
> been satisfied by prose describing the thing it was looking for.
>
> ### One thing the port found here, recorded rather than fixed
>
> This product's Windows shell makes exactly **two** calls to its localizer — the
> nav loop and one button — where its iOS shell makes seven and its Android shell
> eight. It renders nearly all of its chrome from XAML literals, so a German user
> gets a German nav pane and English everything else.
>
> That is a real gap and it is not what this release is about. It is written down
> on `test_the_call_extraction_finds_something`, whose floor is set at two for
> that reason: raising the floor to a comfortable number would have hidden it
> inside the guard meant to notice things like it.

## app-v0.30.6 — QRME app-v0.30.6

- Published: 2026-08-02
- Commit: `d28343ae7563723bebc09fff267f62e1ac744aae`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.6>

> ### The plan gate speaks the reader's language
>
> `refusals_untranslated.txt` carried this as an exception for four releases, in
> its own words: a template whose slots were English prose, where translating the
> frame alone would produce *"a sentence half in each language, at the one moment
> in this product that stands between somebody and a decision to pay"*.
>
>     asked     can the frame be translated
>     mattered  can the slots be
>
> They can. The capability descriptions and the billing period are a **closed set
> this product authors**, so they are `i18n.Term`s with translations rather than
> strangers — and `Term` is now exempt from the whitespace rule for exactly that
> reason. The rule catches prose *nobody wrote a translation for*; an unmapped
> `Term` still keeps the whole sentence English, so the exemption is paid for
> rather than a hole.
>
> The **plan titles** stay as they are. `Basic` and `Pro` are what the product is
> called on the pricing page, in the console's tabs and on a receipt, and
> somebody comparing a refusal against a price list needs the same word in both
> places.
>
> `Opening` capitalises **after** translation, never before: the vocabulary holds
> one form of each phrase and each language raises its own first letter from it.
> `str.capitalize()` was wrong here — it lower-cases the rest, which would have
> flattened German's nouns.
>
> ### The console had the same defect one layer out
>
> The card under the message repeated, in English, what the message says: the
> plan you are on, the plan you need, the price, the period, and that billing is
> simulated. It was written when `message` was English too, so the repetition
> cost nothing — and the moment the sentence started arriving translated, it
> became the only English left on that card.
>
>     asked     is the refusal translated
>     mattered  is what surrounds it
>
> The duplicate is gone. The price and the simulated-billing disclosure are
> adjacent **inside** the message — the invariant that card was built to keep —
> now in ten languages rather than one, and the driven test asserts the pairing
> inside the sentence rather than in the markup.
>
> Seven injections, each caught by the right test. The seventh needed a new test
> first: everything asserted the plan gate by calling `localize_detail` directly,
> and every one of those passed while the handler's dict branch was dropping the
> template on the floor.
>
>     asked     does the module translate this shape
>     mattered  does the request path reach the code that does
>
> That test then failed for a second, correct reason — it sent `Accept-Language`
> with an owner token, and the credential decides the language here.

## app-v0.30.5 — QRME app-v0.30.5

- Published: 2026-08-01
- Commit: `82f109f217c097a62f3d5bc9c84414bf3dbf6e5a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.5>

> ### The plan gate said HTTP 402
>
> 0.30.4 left the plan gate open as the one refusal deliberately not translated,
> because its message interpolates prose. Going back to translate it turned up
> something else first: on three of the four client families it was not arriving
> at all.
>
> `detail` has three shapes in this product — a **string** for most refusals, a
> **dict** for the plan gate, a **list** for a 422. 0.30.3 gave the list a
> top-level `message` and taught every client to read it. The plan gate's
> `message` stayed nested inside its dict.
>
>     asked     does the sentence ride beside the structure
>     mattered  does every structured refusal put it in the same place
>
> The three native shells look for a top-level `message`, then for a string
> `detail`. A dict is neither, so the one refusal in this product that stands
> between somebody and a decision to pay rendered as the bare status code: no
> price, no plan name, no reason.
>
> | Client | Before | After |
> |---|---|---|
> | iOS | `HTTP 402` | the sentence, with price and plan |
> | Android | `HTTP 402` | the sentence, with price and plan |
> | Windows | `HTTP 402` | the sentence, with price and plan |
> | Console | correct | unchanged |
>
> **One of those was a regression from 0.30.3.** Android had been coercing the
> dict through `toString()` and showing its raw JSON — ugly, but it contained the
> price. Teaching it to read the top-level key first is what dropped it to the
> status code. iOS and Windows had always been broken.
>
> **The fix is not a third special case.** Every refusal now carries a top-level
> `message` holding the sentence a person reads, whichever shape `detail` is, so
> a client never has to know the shape and a structured refusal added later
> cannot repeat this. `detail` is untouched: the console still reads the dict to
> draw the upgrade card with its price and button. `sentence_of` returns nothing
> when there is nothing readable rather than inventing a sentence — a bare status
> is more honest than one this codebase made up, and would be indistinguishable
> from a real one.
>
> Five injections, each caught by the right test — but the fifth needed the test
> rewritten first. It compared the lifted sentence with the nested one on the
> plan gate, whose message is deliberately untranslated, so both sides were the
> same English string whichever order the handler used, and an injection that
> lifted before localizing passed.
>
>     asked     do the two copies agree
>     mattered  is the lifted one the translated one
>
> It now drives a message that is actually in the translation table, where the
> wrong order produces a visible difference.
>
> Still open, and unchanged by this: *translating* the plan gate. Its message
> interpolates a capability description and a plan title, which are English
> prose, and 0.30.4's mechanism refuses prose slots by design.

## app-v0.30.4 — QRME app-v0.30.4

- Published: 2026-08-01
- Commit: `141d5876e97a635d32f55a42dbb6a2c46f57c4a6`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.4>

> ### A refusal whose English is not a constant
>
> `refusals_untranslated.txt` has carried the same paragraph for three releases:
> f-string refusals, named as uncovered and deliberately not counted in the
> backlog, because
>
>     f"language must be one of {', '.join(SUPPORTED)}"
>
> cannot be looked up by its English source — at the moment it is raised there is
> no English source, only a result.
>
>     asked     is the refusal a constant we can translate
>     mattered  is every part of it something we can translate
>
> `i18n.Templated` is a `str` whose value is the finished English sentence,
> carrying the template and its slots so `localize_detail` can refill the frame
> in the reader's language. Nothing that already treats a detail as text changed
> — the default English path, JSON encoding, and every driven test asserting on a
> refusal message all work exactly as before.
>
> **The slot is the whole design.** A translated frame around an English slot is
> *worse* than an English sentence: it reads as a bug, in front of somebody who
> is already being told no. That is precisely why this record refuses to ship a
> translated plan gate, and doing it here by accident would have been the same
> mistake with a mechanism to spread it. So whitespace means prose, and a slot
> that fails the test keeps the whole refusal English — the state it was already
> in, now chosen rather than stumbled into.
>
> The known limit is stated rather than hidden: a **single** English word has no
> whitespace either, and is indistinguishable from an identifier.
>
> QRME interpolates closed sets — an objection's `open | upheld | dismissed` —
> so it carries a `Term` marker and a translated vocabulary, resolved at *render*
> rather than at raise, because the reader's language is not known where the
> refusal is raised. An unmapped word keeps the refusal English too, which makes
> coverage structural instead of a list somebody has to remember to update.
>
> **18 of 49 sites converted**; the record now names the reason per site rather
> than "f-string". Seven of the remaining 31 carry prose this product does not
> author — a mail server's exception, a moderation verdict, a hardware
> availability string — and no mechanism changes that.
>
> **Two of my own checks asked the wrong question and were caught by their own
> subjects.** The slot pattern was first written as a character allowlist, which
> quietly meant ASCII: Devanagari writes its vowels as combining marks, which are
> not `\w`, so every Hindi word in the vocabulary failed a rule written to catch
> English sentences. And the vocabulary check asked whether each translation was
> a single token, failing on `वापस ली गई` and `تم التسليم` — correct translations
> that happen to be two words.
>
>     asked     is this translation a single token
>     mattered  is this translation not still English
>
> Six injections, each caught by the right test — including the `Templated`
> branch placed below the plain-string branch, which would have looked up the
> finished sentence, found nothing, and returned English indistinguishably from a
> sentence nobody has translated yet.

## app-v0.30.3 — QRME app-v0.30.3

- Published: 2026-08-01
- Commit: `3870358223674f85a478c389d816907fad23efff`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.3>

> ### The refusal that arrived as a list
>
> 0.30.1 put the 422 into the reader's language — the refusal a mistyped form
> produces, and the one a person meets most often. Nothing looked at what a
> client does with the result.
>
> `detail` on a 422 is a *list* of pydantic rows, and every client family
> rendered it by a path written for a string. The console called
> `JSON.stringify` on it, so the note under a form read
> `[{"type":"missing","loc":["body","display_name"],"msg":"Field required"}]`.
> Android's `JSONObject.optString` coerces a `JSONArray` through `toString()`,
> producing the same. iOS asked for `as? String`, got `nil`, and fell back to
> `HTTP 422`; Windows called `GetString()` on an array, which throws, was
> caught, and did the same.
>
>     asked     is the refusal translated
>     mattered  is the refusal a sentence
>
> The `msg` translated last release was correct, arrived, and was read by
> nobody: it sat inside a JSON blob or was discarded for a status code. Two of
> the four families showed the person **less** than before their language was
> ever considered.
>
> **The fix.** `i18n.validation_message` composes one sentence from the rows, in
> the reader's language, and rides beside `detail` rather than replacing it —
> `detail` is the FastAPI contract, what a machine reading this API has a right
> to, and what the driven tests read. Every client decode now reads the sentence
> first. The field name stays the API's own (`display_name`), joined with an em
> dash rather than declined into the sentence, so nothing comes out half in one
> language and half in another. Mapping those names to the labels a form
> actually shows needs a per-client table that does not exist, and is recorded as
> the remaining gap rather than guessed at.
>
> **The guard took three attempts, and the first two are why the third is worth
> having.** Asking whether a client's source mentions `message` passed on all
> four clients while all four were broken — it is a field on a model, a
> parameter name on an exception class, and a word in the comment directly above
> the bug. Anchoring on the throw and asking whether the surrounding lines read
> it caught the three shells and still passed on a broken console, because the
> fallback chain has always read the sentence key as an *alternative to*
> `detail`.
>
>     asked     does the decode mention the sentence
>     mattered  does the decode pass the sentence on
>
> Seven injections, each caught by the right test with the right message.
>
> **The shape that walked past a fix it already had.** QRME's console met this
> exact problem in an earlier round and solved it — for the plan gate, whose
> refusal is an *object* carrying its own `message`. A list is an object with no
> `message`, so the 422 fell through to the `JSON.stringify` written for the
> unhandled case.
>
>     asked     does a structured refusal reach the reader as a sentence
>     mattered  does every structured refusal
>
> `test_gates_answer_in_a_shape_a_screen_can_use` pinned the exact two-argument
> spelling of that call and fired when a third argument was added to carry the
> sentence. Loosened to a prefix match, which is what it meant — the structure
> still rides out unflattened — and re-injected to confirm it still catches the
> regression it was written for.

## app-v0.30.2 — QRME app-v0.30.2

- Published: 2026-08-01
- Commit: `dc6c868a6d0896a9b6ebc059d6dc2cae726535ce`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.2>

> ### The synthetic self enters the tandem contract
>
> `docs/tandem.md` gains the boundary before the code that obeys it, and this
> release carries the amendment that names the one exception to it. The
> implementation is JIM-mini's; the contract is shared, byte-identical in all
> three repositories, and it is QRME's `self` profile the whole section is about.
>
> Everything the contract described linked JIM to *somebody else's* profile, and
> the JIM user reached QRME as an **interactor** — a stranger. `ProfileKind` is
> `self | other_person | fictional | hybrid` and a `self` profile speaks *as* the
> person; JIM had no column, module or route that knew it existed, and QRME held
> nothing pointing back.
>
>     asked     does JIM reference synthetic profiles
>     mattered  does JIM reference this person's own
>
> An owner token, not an interactor token. The link refused unless QRME reports
> `kind == "self"` — a `fictional` profile briefed with somebody's medication
> schedule is a different product with the same code. JIM → QRME is an enumerated
> allowlist, consented per category, empty by default, with the composer building
> the brief *from* the allowlist rather than filtering a payload down to it.
>
> **The amendment.** Journal entries, check-in notes and transcripts never cross
> under any consent. The one category made of the person's own words is
> **medication**, and it is named in the contract rather than hidden in an
> implementation: `meds.py` invites their wording, so names are free text by
> design, and *"the pill for my HIV"* is a diagnosis typed into a field asking
> for a drug. Consenting to that category is consenting to a self-profile that
> can be asked about those strings by anyone it talks to — which is why the
> preview shows the strings and not a count of them.
>
> The brief arrives through QRME's own owner-gated
> `POST /profiles/{id}/sources`, so it lands where the persona is grounded and is
> sealed into PDI when a vault is configured.

## app-v0.30.1 — QRME app-v0.30.1

- Published: 2026-08-01
- Commit: `8a87b5d55a814730bc5014131242a142d36ab2b3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.1>

> ### The refusal that handed the body back
>
> The round in 0.30.0 put every refusal this product *writes* into the reader's
> language, through one handler no raise site opts into. It missed every refusal
> this product *returns*.
>
>     asked     is every refusal this product writes translated
>     mattered  is every refusal this product returns
>
> `RequestValidationError` is not an `HTTPException`. FastAPI raises it before
> routing finishes and renders it with its own handler, so a 422 — the refusal a
> person meets most often, because it is what a mistyped form produces — went out
> past a handler written to catch everything.
>
> **The larger half is what it carried.** Pydantic's error rows hold an `input`
> key with the value that failed, and for a missing field that value is the
> entire submitted body. Driven against the siblings: JIM returned a journal
> entry about chest pain, PDI a record value in plaintext on the one path in an
> encrypted vault that never touches the encryption layer.
>
> Every other part of this ecosystem's error design refuses to carry content.
> `errors.ts` and the nine `Problems` modules record a method, a redacted path
> and a status, and have no parameter a message could arrive through. `cloudgw`
> refuses a report whole if it finds prose in it rather than sanitising it. The
> one place content left the process was the framework's default renderer,
> because nobody had looked at it as ours.
>
>     asked     does this product record anything private
>     mattered  does this product return anything private
>
> **What this is not:** disclosure between people. A 422 goes back to whoever
> sent the request, so what came back was the sender's own body, and no stored
> record was exposed. **What it is:** content on an error path, travelling
> through whatever sits between the app and the person — a proxy's access log, a
> HAR export on a support ticket. A posture with one documented exception is a
> preference.
>
> `type`, `loc` and `msg` are returned; `input` and `ctx` are not, built as an
> allowlist so the response cannot grow a leak by somebody else's release.
> `value_error` and `assertion_error` messages are replaced outright: a validator
> that quotes the value it rejected is the same leak wearing a different key.
>
> On `extra_forbidden` the key is echoed only when it is *shaped* like a field
> name. The first version replaced it always, and
> `test_a_write_that_answers_200_did_something` failed by name — two routes there
> used to accept `dials` for `values` and `years` for `period`, discard them and
> answer 200, and a round was spent making them strict so the caller is told
> which key was wrong.
>
>     asked     can a key carry content
>     mattered  does this key look like content
>
> The guard does not check for the `input` key — that would test the name of the
> leak rather than the leak. It posts a canary at every body-taking route from
> `all_routes` and fails if it appears anywhere in the response; before the fix
> it named **124 routes**. A second check asserts how many of those reached
> validation at all, because a sweep of two hundred routes that all 404 first is
> a spotless report about nothing.
>
>
> ### The synthetic self enters the tandem contract
>
> `docs/tandem.md` gains the boundary before the code that will obey it.
>
> Everything the contract described linked JIM to *somebody else's* profile, and
> the JIM user reached QRME as an **interactor** — a stranger. `ProfileKind` is
> `self | other_person | fictional | hybrid` and a `self` profile speaks *as* the
> person; JIM had no column, module or route that knew it existed, and QRME held
> nothing pointing back.
>
>     asked     does JIM reference synthetic profiles
>     mattered  does JIM reference this person's own
>
> An owner token, not an interactor token. The link refused unless QRME reports
> `kind == "self"`. JIM → QRME is an enumerated allowlist, consented per
> category, empty by default, with the composer building the brief *from* the
> allowlist rather than filtering a payload down to it — and no free text from
> the user crossing at all. Byte-identical in all three repositories.

## app-v0.30.0 — QRME app-v0.30.0

- Published: 2026-08-01
- Commit: `bbbcedcea10248630b7f73d373408372437277f6`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.30.0>

> ### Forty-six translated labels, forty-six English screens
>
> QRME's sidebar answers in the reader's language: forty-six `nav.*` keys, ten
> languages each, built by ``t(`nav.${n.id}`, lang)``. Behind those forty-six
> labels are forty-six screens, and every string on all of them is English —
> **1576 of them**, now recorded in `tests/console_untranslated.txt` and
> ratcheted.
>
>     asked     is the chrome localized
>     mattered  is anything behind the chrome localized
>
> `l10n.ts` declares its own scope in its first line — "chrome localization for
> the desktop console" — and three rounds of language audit read that sentence as
> a boundary rather than as the thing to question. Each widened correctly inside
> it: `Public.tsx`, then `Onboarding.tsx`, then the native shells. Each ended
> green.
>
> This is worse than a console with no translations at all, which is why it is
> recorded separately rather than folded in. A uniformly English console tells a
> Spanish reader the truth on the first screen. This one puts *Mercado*, *Amigos*
> and *Ajustes* in the sidebar and hands them English the moment they click —
> and the backend already answers in the profile's language, so the model replies
> in Portuguese inside a frame that cannot.
>
> The structural half is `test_the_two_records_partition_the_console`. Both
> language records now derive their screen sets from `screens/` and must together
> cover it exactly: none in both, none in neither. A screen added to this console
> lands in a count whether or not anybody remembers these files exist.
>
>
> ### The persona speaks it everywhere; the platform spoke English
>
> `qrme/i18n.py` opens with "the persona speaks it everywhere", and it does — the
> directive rides on the system prompt, so every generation site inherits it. The
> product's own sentences were another matter. An owner who set Portuguese got a
> Portuguese sidebar, Portuguese answers from the model, and English on all 153
> of its refusals.
>
> `common.refusals_in` was added in 0.24.0 for the four accountless routes, and
> its docstring wrote down why the owner routes were left out:
>
> > `profile_or_404` and its siblings are shared with every owner route and say
> > "profile not found" in English, which is right there — the owner picked that
> > language
>
> The owner did not pick that language. They picked one, it is in
> `language_prefs`, and English is what they get when they picked English. The
> justification for the scope **was** the defect.
>
>     asked     did the caller state a language
>     mattered  did the profile
>
> One exception handler on the app, for the reason the membership gate is one
> dependency: a sentence cannot be added to the product and forgotten at a raise
> site, because no raise site opts in. `refusals_in` is gone — two paths
> translating one sentence are free to drift.
>
> Two ways this could have been wrong and still passed, both now driven.
> **Whose language:** reading the `profile_id` in the path answers a stranger in
> the language of the person they are asking *about*; reading `Accept-Language`
> takes `en-US` from a console owner's browser whatever they set in the app. The
> credential names the reader. **Which stored value:** `effective_language`
> returns English whenever the mode is `on_demand` — a statement about the
> persona's voice, not about what the owner reads.
>
> Eleven sentences translated into all nine; **142** recorded in
> `tests/refusals_untranslated.txt` and ratcheted, with the 49 f-string refusals
> and the plan gate named in the header as classes the file does not cover.

## app-v0.29.0 — QRME app-v0.29.0

- Published: 2026-08-01
- Commit: `d0d96e2b02174890b4fddd687f6860ba144b778e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.29.0>

> ### The deploy that lived in a chat log
>
> `docs/cloudgw-deploy.md` — the gateway from a bare host to installers that
> actually report, with the two build-time variables that are the point of the
> exercise.
>
> It says in its first line what has and has not been proven. The routes, the
> refusals, the token scopes and the fail-closed defaults were all driven
> against a running instance; **the image build was not**, because the sandbox
> it was verified in has no Docker daemon. A runbook that does not distinguish
> those two is a runbook that will be trusted in the wrong place.
>
> It also states what the box does not buy: counters cannot reproduce a bug, and
> they cannot reach installers already in the field, because the address is
> compiled in.
>
>
> ### A translated string nobody reads
>
> Two keys shipped in 0.27.0 were in the table and wired to nothing — caught by
> hand last release. `test_no_key_is_translated_into_ten_languages_and_used_
> nowhere` now catches the class, here and in JIM, where eight more turned up.
>
>     asked     is every key in the table complete
>     mattered  does every key in the table reach a screen
>
> Every completeness check in both repositories asks whether a key *has* its ten
> languages. None asked whether anything looks it up, so a translated string can
> sit beside the English it was supposed to replace with nothing to say which
> one a reader gets.
>
> The first version of the check read literal keys only and reported all
> fifty-three `nav.*` keys as dead. Every one is live — `App.tsx` builds them,
> `` t(`nav.${n.id}`, lang) `` — so a guard against dead translations would have
> had somebody delete the working ones. It now understands a built key's literal
> head.
>
>
> ### The pre-session backlog reaches its floor
>
> 37 → 20 → **4**, and the four are a product name, a full stop, an example
> address and an example verification code — strings that are the same in every
> language. `public_untranslated.txt` now says so in its header: this is a
> floor, not a backlog.
>
> Two keys added last release were in the table and wired to nothing — the
> tagline and the password-mismatch warning. They had been translated into ten
> languages and no screen looked them up, so the strings stayed English while
> the table said otherwise. The round that localized the form localized most of
> the form and stopped, which is the same shape as the round two releases ago
> that localized the door and stopped at the sign on it.
>
> Fourteen more keys and the wiring for all of them, including the two dead
> ones. Four strings were missed on the first pass because JSX had wrapped them
> across source lines — a substitution matching a single line finds nothing and
> reports success.

## app-v0.28.0 — QRME app-v0.28.0

- Published: 2026-08-01
- Commit: `a2879b4916445bcef5c749afc7de66b018676690`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.28.0>

> Aligned with JIM-mini 0.28.0. The three products carry one version, so a
> release that only moves in one of them still moves in all three.
>
> Nothing in this product's own code changed this cut. JIM's console gained the
> localization layer whose absence was measured last release, and two of its
> guards broke on the way — both asking whether a sentence was in a screen's
> *file* when what mattered was whether the screen *says* it. Neither surface
> exists here in that form.

## app-v0.25.0 — QRME app-v0.25.0

- Published: 2026-08-01
- Commit: `05b8e81b7b120110a6e6cffa9938dc353f24855f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.25.0>

> Two outstanding console tasks — Google/Apple credentials and the Windows Hello
> field test — written down field by field. Writing them down found a defect in
> each.
>
> ### A relying party id is a domain, and `127.0.0.1` is not one
>
> `docs/signatures.md` is careful that the ceremony must run on the relying
> party's own origin, and every client obeys it: the Windows shell embeds a
> WebView2 pointed at `/signatures/ceremony`, the console opens the same page.
> Both fetch it from `http://127.0.0.1:8000` — the default base address — and
> `QRME_RP_ID` defaults to `qrme.app`.
>
> Neither can host a ceremony. `rp.id` must be a **domain**, so an IP-address
> origin has none it could use; and `qrme.app` is not a suffix of a loopback
> host either. The Register and Sign buttons had never worked from a default
> install and could not, and the browser's refusal arrives inside an embedded
> WebView as a DOMException that reads like a declined credential rather than a
> wrong address.
>
>     asked     does the ceremony run on the relying party's own origin
>     mattered  can that origin be a relying party at all
>
> Both clients now rewrite a loopback IP to `localhost` — a domain, the same
> backend, a secure context without a certificate — and the ceremony route
> refuses a pairing that cannot work with a **page** naming the variable to
> change, because a JSON error inside a WebView is a blank panel.
>
> ### The Apple client secret expires and nothing says so
>
> `QRME_APPLE_CLIENT_SECRET` is not a string you copy once. It is an ES256 JWT
> minted from a `.p8`, capped by Apple at six months, with no renewal notice
> and no degraded mode — on the day it lapses every token exchange answers
> `invalid_client`. `providers()` reports the door open the entire time,
> because it asks whether the variable is *set*.
>
> `scripts/mint_apple_secret.py` mints it and reads its expiry without needing
> the key, exiting non-zero inside the last thirty days so a health check can
> act. Two things it gets right that are easy to get wrong: JWS wants a raw
> 64-byte `r || s` signature where `cryptography` returns DER, and a lifetime
> past Apple's ceiling is refused at minting rather than at the exchange. The
> test verifies the signature with the public key instead of measuring it.
>
> ### Added
>
> - `docs/sign-in.md` — every field of the Google Web-application client and
>   the Apple Services ID, with the return addresses, the scopes that keep it
>   out of verification review, and why a Desktop-app client cannot be used.
> - `docs/windows-hello-field-test.md` — the checklist, including what the test
>   cannot prove: Windows verifies rather than signs, the ceremony runs through
>   Edge's WebAuthn, and `basic` is the only tier a self-asserted credential
>   reaches.
> - `scripts/mint_apple_secret.py`, with `mint` and `check`.
> - `*.p8` in `.gitignore`, and a test that fails if one lands in the tree
>   anyway.

## app-v0.21.0 — QRME app-v0.21.0

- Published: 2026-08-01
- Commit: `7a186500619f560b137640b331bfe22924c53b85`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.21.0>

> **QRME v0.21.0 — four doors, and three defects behind them.**
>
> Four rounds run back to back. Each one built a console door for a backend
> feature that had none. In three of the four, building the door found a defect
> in the thing it was a door to — and in every one of those, the argument
> against the defect was **already written down somewhere else in the same
> repository**.
>
> ## A room id was the only thing a room asked for
>
> `Rooms` could open a room and not enter it. Building the way in — **screen
> 175** — found two defects worth more than the screen.
>
> - **Anybody could speak as anybody.** `POST /rooms/{id}/messages` read the
>   speaker from `sender_id` *in the request body* and checked only that the id
>   named a participant, never that the caller *was* that person. A stranger's
>   token plus a named participant's id gave a `201`, a message stored under her
>   name, and every profile in the room answering as though she had spoken.
> - **The transcript asked for nothing at all** — not a wrong token, no token.
>   And neither did `advance`, so a stranger could run somebody else's room
>   forward indefinitely against their model key.
>
> A room id is not a secret; it rides in beacons and on printed QR stickers,
> which is the point of them. That sentence was already written **two routes
> away**, on `GET /rooms/{id}/mic`, guarding the narrower fact of who is wearing
> a live microphone. All three now go through the same membership check.
>
> `sender_id` stays on the request model and is ignored — three shipped native
> clients send it, and a 422 on upgrade is a worse answer than not believing it.
>
> ## The body market, and what you bolt onto a body
>
> Choosing a body is shopping, and the catalogue listed nine models. It now
> lists **36 from 25 makers** across humanoids, home robots, quadrupeds and
> announced platforms, with a review date the suite refuses to let go stale.
>
> Announced bodies are listed **on purpose** — an owner shopping should see what
> is coming — and binding one is refused with a `409` that says so, rather than
> a `404` that would lie about a machine its maker has publicly shown.
>
> Alongside it, the **connections bracket**: task packs and connectors. Each
> installed pack becomes a commandable verb for exactly one body, capability
> checked at install and audited like every built-in command. A vacuum is still
> never taught `fetch`.
>
> ## A policy you could publish and nobody could take up
>
> `Delegate` built the owner's half of delegation — mint a grant, choose which
> phases run unattended, start and advance and cancel. But delegation exists for
> the person on the **other** end of a conversation, and that half had four
> bindings and no screen calling any of them. The policy was publishable and
> unusable from the console that published it.
>
> Driven end to end, **every rule was already right**: the offer is public and
> lists phases only, never the grant id, because which source items the owner
> scoped is the owner's business; `research` is refused without a grant, and the
> refusal names what it protects rather than the rule it enforces; starting one
> requires an existing conversation; and reading one is `403` to an outsider,
> `401` to nobody at all, and `200` to the delegate *and* the owner, who are
> entitled to it for different reasons.
>
> The first round in a while with no defect in it, recorded plainly as such. The
> failure it *did* find is exactly the one the door audit exists to name: a
> feature finished and unreachable.
>
> ## A missing field was reported as a broken signature
>
> Seven signature routes had no console door: enrol a credential, revoke one,
> read the policy, mint an envelope, sign it, and check a package handed over
> from outside. `Referrals` had already written the gap down as a sentence —
> *“None enrolled. The ceremony can enrol one.”* — under a heading with no
> button behind it. The ceremony page existed and posts the raw assertion back
> to its host; nothing in the console was listening, so the message went
> nowhere.
>
> Building the listener found the defect, in the one place this feature cannot
> afford one.
>
> `verify_package` runs eight checks in order. **Any** exception anywhere in that
> sequence ran `checks["signature"] = False` and appended `str(exc)`. So a
> package missing `display_text` — trimmed in transit, or a summary forwarded in
> place of the package — came back saying **the signature is invalid**, when the
> ECDSA verification several lines earlier had passed. That is the strongest and
> most damaging thing this endpoint can say, it was false, and the reason offered
> was `'display_text'`: a Python `KeyError` repr sitting beside two notes written
> as full sentences. A counterparty reading it would conclude they had been
> handed a forgery.
>
> The argument was already in the same feature. The router says of its own
> refusals: *the message is the reason, because a signature that is turned away
> without one is impossible to fix from the outside.* A counterparty is exactly
> the outside.
>
> Two rules now hold. A check that already **passed** is never retroactively
> failed by a later one breaking — only the check that actually broke is
> reported broken. And a check that never **ran** is not a pass: all eight are
> named, `valid` is false whenever any is absent, and the notes say which and
> why in sentences. The screen draws unrun as unrun, because a fixed backend
> behind a screen that drew absent as a tick would put the same lie back on the
> glass.
>
> ## Where the numbers landed
>
> | | before | after |
> |---|---|---|
> | Console-doorless routes | 64 | 40 |
> | `api.ts` bindings nothing calls | 25 | 12 |
> | Screen-manifest `unaudited` seeds | 8 | 7 |
>
> New screens **174–178**. Full suite: **1926 passing**.
>
> ---
>
> Installers for macOS, Windows and Linux are attached below once the release
> build finishes.
>
>
> ## What's Changed
> * The installer could not report, and nothing said so by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/247
> * Ask each client the door question separately, and build the seller's side by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/248
> * Resolve a seller to their account, not to their profile by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/249
> * Cut 0.20.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/250
> * Four door-audit rounds: rooms, bodies, delegation, signing by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/251
> * Cut 0.21.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/252
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.20.0...app-v0.21.0

## app-v0.20.0 — QRME app-v0.20.0

- Published: 2026-08-01
- Commit: `2bf7bb6c540e60d04c1897de5f0277c2a8c7a170`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.20.0>

> **QRME v0.20.0 — the doorless backlog reached zero.**
>
> It began at **116** routes the backend served that no client could reach. This
> release closes the last **42**, each with a door in the console, carried by six
> new screens (**168–173**).
>
> A route with no door is the quieter of the two integration failures. A client
> asking for a route that does not exist produces a 404 somebody eventually
> reports. A route no client asks for produces nothing at all: the code is
> present, its tests pass, the changelog says it shipped, and the capability is
> simply unreachable.
>
> ## What the exercise actually produced
>
> Not doors — **defects**. Almost none were visible to the typecheck.
>
> **Three routes took no token at all.**
>
> - `POST /packs` let anybody publish to the marketplace, name any string as the
>   publisher, and name *any account* as the one sales accrue to.
> - `POST /profiles/{id}/interactions/{id}/feedback` let anybody rate in somebody
>   else's name — and since an `up` rating is the trigger for cloud contribution,
>   an unauthenticated caller could push a stranger's conversation out of the
>   deployment.
> - `GET /profiles/{id}/engagement/{id}` exposed how often a named person talks
>   to a profile, across how many sessions, and whether they liked it.
>
> In each case the argument against it was **already written down elsewhere in
> this repository** — `commerce.beneficiary_of` on gifts, the beacon list on
> physical places. Three routes had quietly gone the other way.
>
> **A licence was sold to somebody who could not use it.** A licence permitting
> derivatives went to a buyer under 18: `201`, `can_derive: true`, fee credited
> to the seller at sale time — then a `403` on the only thing the licence exists
> for. The adult check now runs at acquire, where the money moves.
>
> **A link resolved against the wrong origin.** Desk beacons returned a relative
> `scan_url` while the profile beacons next door returned an absolute one, so the
> console's scan link resolved against the console's own origin — dead in every
> packaged build.
>
> **An honesty note was served to nobody.** A desk's view frame, and the sentence
> it carries — *this deployment has no camera on this desk, so the frame is not
> live and is not claimed to be* — was never rendered anywhere in the console.
>
> ## The audit could not see two kinds of request
>
> An `<img src>` is a fetch. An `<a href>` is a fetch. Neither passes through the
> API client, and the extractor could see neither — so two routes sat on the
> backlog while the placements screen had been rendering both since it was
> written.
>
> Worse, **the exemption list had absorbed three of them**, each marked "rendered
> in an `<img src>`, not fetched by the API client" — an exemption made out of a
> blind spot, which is the shape that stops anybody asking. One of the three had
> no door at all. The list now holds to one rule: **exempt a path because nothing
> should ever call it, never because the audit cannot see the call.**
>
> ## Recorded rather than corrected
>
> Five findings are pinned as observed behaviour instead of changed, because each
> is a decision to make deliberately rather than while building a screen:
>
> - a **gift** reads its beneficiary from the subject; a **subscription** takes
>   one from the request body;
> - the contribution **preview is computed whether or not you are opted in**, so
>   the console changes the heading rather than the content;
> - the quiet-hours window is half-open, so **9-to-9 covers nothing** — changing
>   the arithmetic would silently redefine every window already stored;
> - three deletes give three different answers to *there was nothing there*;
> - `deleted_at_gateway` is true *vacuously* when nothing ever left.
>
> ## The guard, now that the backlog is empty
>
> A new assertion says so directly, separate from the record comparison so the
> message is plain when it goes: *the number is no longer zero*. Its
> guard-on-guard moved too — asserting the snapshot was non-empty no longer means
> anything, so the liveness check now sits on the console's extracted call sites.
>
> Seven new test files, 154 tests, 23 injection-verified. **Suite: 1807 passing.**

## app-v0.24.0 — QRME app-v0.24.0

- Published: 2026-08-01
- Commit: `46db32b685f26f2b99e98cb7806334a8278b05f1`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.24.0>

> Nine rounds, one question: **when a stranger does reach the thing built for
> them, can they read what it says?**
>
> The last release opened the doors — the objector, the person asking whether
> what they were sent is genuine, the person checking they met the same profile
> twice. This one is what is written on the other side of them, and every
> finding is the same shape a layer further in: a surface localized while the
> sentence it answers with was not.
>
> ## The screen was in ten languages and the answers were in one
>
> `qrme/i18n.py` takes a `profile_id`. The accountless screen's reader has
> none, so that module could not have answered them even if something had
> asked. A visitor in Osaka got a Japanese page, pasted in a piece of text,
> pressed a Japanese button, and was told in English:
>
> > no stamped work shares any wording with this text
>
> which is the answer to the only question they came with. The restriction
> notice after opening an objection, the consistency guarantee, the
> synthetic-media disclosure, the recovery method and every refusal were the
> same.
>
> Thirteen sentences in ten languages, hand-translated rather than
> machine-translated, in a table separate from the per-profile machinery above
> it. Four public routes read `Accept-Language`; `refusals_in` translates what
> they raise, narrowly, so an owner's refusal is untouched.
>
> **The state words are deliberately not translated.** The first version of
> this translated `status` too, and driving it caught the cost: `Contest.tsx`
> branches on `status === "open"` to show the card a subject or an estate uses
> to end a case immediately. A Japanese browser would have made that control
> vanish from a signed-in screen. What a person reads is translated; what a
> client compares is not.
>
> ## Twenty-five strings on the public screen, five in the ledger
>
> The backlog file listed five sentence fragments and called them the hard
> remainder. They were what a regex over TSX happened to be able to see:
> `>([^<>{}]+)<` excludes braces, so every sentence wrapping an interpolated
> value was skipped whole, and the five reported were their brace-free scraps.
> TypeScript generics look like tags to that pattern, which is why it had grown
> a rule dropping lines with `=`, `;` or `=>` — and that rule then swallowed
> the mark pane's entire explanatory paragraph.
>
> `app/scripts/jsx-text.mjs` asks TypeScript's own parser for `JsxText` nodes
> instead. Twelve new keys in ten languages, and `fill()` so a sentence with
> named holes stays one translatable unit rather than three fragments no
> translator can reorder.
>
> ## The pre-session surface is two screens
>
> That guard measured `Public.tsx` alone and reported the pre-session surface
> clean. `App.tsx` renders two things before a profile exists, and the other is
> the one everybody meets first. `Onboarding.tsx` carries thirty-seven English
> strings while already calling `visitorLang()` three times — on the links
> pointing at the accountless screen. The round that localized the door
> localized the sign to the door and stopped.
>
> Recorded and ratcheted rather than half-translated: a partly-translated
> sign-up form reads as broken software at the moment somebody is deciding
> whether to trust it with their email address.
>
> ## Three phones with no way to ask
>
> Every native shell's `language` is read from the profile's stored setting, so
> the one screen whose reader has no profile is the one screen where that value
> is guaranteed to be the default. `WithoutAnAccountView.swift` contains no
> `L10n.` calls beside a table with ten languages in it — and there was nothing
> to pass it.
>
> iOS, Android and Windows now resolve a device language from
> `Locale.preferredLanguages`, the system locale list and `CurrentUICulture`,
> region dropped, English as a fallback rather than a guess. The screens'
> strings are recorded, all three shells or none.
>
> ## One header, three products
>
> QRME, JIM-mini and PDI each grew a `negotiate()` in a different round.
> Compared side by side for the first time, two rows disagreed — `ar;q=0` and
> `de;q=abc`. `q=0` means *not acceptable*, so a browser sending `ar;q=0` is
> refusing Arabic. A conformance table now lives byte-identically in all three
> repositories.
>
> ## Also
>
> - `test_the_promise_and_the_door_are_on_the_same_surface` could no longer see
>   a claim made through a lookup key. Injecting a localized no-account claim
>   into a gated screen passed against the shipped guard; both it and its
>   positive control now resolve text through `l10n.ts`.
>
> **2097 tests passing.**

## app-v0.23.0 — QRME app-v0.23.0

- Published: 2026-08-01
- Commit: `0d7a119861b0e6bd26ece54a44b647c30cabbfb7`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.23.0>

> **QRME v0.22.0 — the audit reaches zero, and finds five more defects on the way.**
>
> Five rounds. Each built a console door for a backend feature that had none,
> and in **every one of them** building the door found a defect in the thing it
> was a door to. In every one of those, the argument against the defect was
> already written down somewhere else in the same repository — usually a few
> lines away, occasionally in the docstring directly above.
>
> | | at the start of this release | now |
> |---|---|---|
> | Console-doorless routes | 64 | **0** |
> | `api.ts` bindings nothing calls | 25 | **0** |
>
> Both record files are now **empty rather than short**, and the tests that read
> them assert emptiness.
>
> ## The only post that actually leaves was the one going out unmarked
>
> `POST /social/{cid}/publish` writes a profile's words to a platform QRME does
> not run. It is the single route in this product where synthetic media
> genuinely **leaves the building** — and it stored that post with
> `watermark_id` NULL, while `compose_post`, the in-app equivalent, stamped a
> credential every time.
>
> `compose_post` even says why, in a sentence that describes the *other* route
> more exactly than the one it is written above: *a public post is synthetic
> media leaving the platform: it carries a verifiable synthetic-media credential
> from the moment it exists.* So the only posts going out unmarked were the ones
> actually going out.
>
> The same function ran the profile's own `maturity` as its moderation filter,
> where `compose_post` forces `strict` with the note *public posts face the
> widest audience: always the strict filter*. A profile set to `open` was held to
> the loosest rule on the way to an audience QRME cannot see, and the strictest
> one when posting where it can.
>
> ## Anybody could take away the name a profile answers to
>
> `PUT /profiles/{id}/handle` took **no credential of any kind**. The damage is
> not that a stranger could give a profile a second name — claiming a handle
> deletes the existing one first, because that is how *changing* your handle
> works. So anybody could take `@rosa` away from Rosa: every printed reference,
> shared link and beacon naming her went dead at once, and the name she now
> answered to was picked by whoever did it.
>
> The three beacon routes **immediately below this one in the same file** were
> given exactly this check in an earlier pass, and `place_beacon` states the
> reason in words that fit here without changing a syllable.
>
> ## A post the filter refused was published by the route that lists what was published
>
> `compose_post` stores a held post `pending` and returns `content: None` **to
> the owner who just asked for it**. Fourteen lines further down, `list_posts`
> returned every column of every row, whatever its status, to anybody, with no
> token. The hold was enforced against the author and against nobody else — and
> `flag_reason` went with it, naming the rule the text broke.
>
> ## An id was read as a credential, in the feature built on consent
>
> `/connections` had no authentication at all. Speak as anybody, read anybody's
> conversation, and end one with no id and no token.
>
> ## A guest joining a stream minted the room before the 401
>
> The anonymous path created the desk's room and *then* refused the caller.
>
> ## Two guards that could only pass while the problem existed
>
> `test_the_union_is_still_wider_than_the_console` asserted the union backlog was
> *strictly* smaller than the console's, reasoning that if the two ever agreed
> the likelier cause was a broken native extractor than a console that had caught
> up. Sound while catching up was hypothetical. It now asserts the invariant that
> survives — the union can never exceed the console's, since the console is one of
> its own surfaces — and the liveness check it was doubling for moved to
> `test_each_native_shell_is_still_being_read`, which counts call sites per shell
> and would actually notice.
>
> ## Also in this release
>
> **Six new console screens** (178–183): signing a document, the visitor's side
> of a desk, meeting a stranger, the mark on a post, what a profile says and in
> which language, and the remainder — the last eighteen routes, wired as one
> lookup control rather than nine buttons nobody would find.
>
> The iOS, Android and Windows shells carry the same credentials the console
> now does, on connections and on claiming a handle.
>
> **Suite: 2027 passing.**
>
> ---
>
> Cut in step with [JIM-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [PDI](https://github.com/davidsbianchi1984/pdi), both also at v0.22.0, both of
> which reached zero on the same audit in this release.

## app-v0.22.0 — QRME app-v0.22.0

- Published: 2026-07-31
- Commit: `9bd67e3f3734f576e8982c5c34aaea81363e587f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.22.0>

> **QRME v0.22.0 — the audit reaches zero, and finds five more defects on the way.**
>
> Five rounds. Each built a console door for a backend feature that had none,
> and in **every one of them** building the door found a defect in the thing it
> was a door to. In every one of those, the argument against the defect was
> already written down somewhere else in the same repository — usually a few
> lines away, occasionally in the docstring directly above.
>
> | | at the start of this release | now |
> |---|---|---|
> | Console-doorless routes | 64 | **0** |
> | `api.ts` bindings nothing calls | 25 | **0** |
>
> Both record files are now **empty rather than short**, and the tests that read
> them assert emptiness.
>
> ## The only post that actually leaves was the one going out unmarked
>
> `POST /social/{cid}/publish` writes a profile's words to a platform QRME does
> not run. It is the single route in this product where synthetic media
> genuinely **leaves the building** — and it stored that post with
> `watermark_id` NULL, while `compose_post`, the in-app equivalent, stamped a
> credential every time.
>
> `compose_post` even says why, in a sentence that describes the *other* route
> more exactly than the one it is written above: *a public post is synthetic
> media leaving the platform: it carries a verifiable synthetic-media credential
> from the moment it exists.* So the only posts going out unmarked were the ones
> actually going out.
>
> The same function ran the profile's own `maturity` as its moderation filter,
> where `compose_post` forces `strict` with the note *public posts face the
> widest audience: always the strict filter*. A profile set to `open` was held to
> the loosest rule on the way to an audience QRME cannot see, and the strictest
> one when posting where it can.
>
> ## Anybody could take away the name a profile answers to
>
> `PUT /profiles/{id}/handle` took **no credential of any kind**. The damage is
> not that a stranger could give a profile a second name — claiming a handle
> deletes the existing one first, because that is how *changing* your handle
> works. So anybody could take `@rosa` away from Rosa: every printed reference,
> shared link and beacon naming her went dead at once, and the name she now
> answered to was picked by whoever did it.
>
> The three beacon routes **immediately below this one in the same file** were
> given exactly this check in an earlier pass, and `place_beacon` states the
> reason in words that fit here without changing a syllable.
>
> ## A post the filter refused was published by the route that lists what was published
>
> `compose_post` stores a held post `pending` and returns `content: None` **to
> the owner who just asked for it**. Fourteen lines further down, `list_posts`
> returned every column of every row, whatever its status, to anybody, with no
> token. The hold was enforced against the author and against nobody else — and
> `flag_reason` went with it, naming the rule the text broke.
>
> ## An id was read as a credential, in the feature built on consent
>
> `/connections` had no authentication at all. Speak as anybody, read anybody's
> conversation, and end one with no id and no token.
>
> ## A guest joining a stream minted the room before the 401
>
> The anonymous path created the desk's room and *then* refused the caller.
>
> ## Two guards that could only pass while the problem existed
>
> `test_the_union_is_still_wider_than_the_console` asserted the union backlog was
> *strictly* smaller than the console's, reasoning that if the two ever agreed
> the likelier cause was a broken native extractor than a console that had caught
> up. Sound while catching up was hypothetical. It now asserts the invariant that
> survives — the union can never exceed the console's, since the console is one of
> its own surfaces — and the liveness check it was doubling for moved to
> `test_each_native_shell_is_still_being_read`, which counts call sites per shell
> and would actually notice.
>
> ## Also in this release
>
> **Six new console screens** (178–183): signing a document, the visitor's side
> of a desk, meeting a stranger, the mark on a post, what a profile says and in
> which language, and the remainder — the last eighteen routes, wired as one
> lookup control rather than nine buttons nobody would find.
>
> The iOS, Android and Windows shells carry the same credentials the console
> now does, on connections and on claiming a handle.
>
> **Suite: 2027 passing.**
>
> ---
>
> Cut in step with [JIM-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [PDI](https://github.com/davidsbianchi1984/pdi), both also at v0.22.0, both of
> which reached zero on the same audit in this release.
>
>
> ## What's Changed
> * Four door-audit rounds: rooms, bodies, delegation, signing by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/251
> * Cut 0.21.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/252
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.20.1...app-v0.22.0

## app-v0.20.1 — QRME app-v0.20.1

- Published: 2026-07-31
- Commit: `b3dc8d043b2c35b438fdee52d946cb998a83a40d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.20.1>

> **QRME v0.20.1 — the guard was measuring the wrong thing, and the money knew.**
>
> Two rounds, and the second was found by the first.
>
> ## The union hid a surface
>
> 0.20.0 reported a doorless backlog of **zero**. It was true of the wrong
> question. `clientpaths.doorless` unions the console with the iOS, Android and
> Windows shells, so a route only the phone calls counts as doored — and the
> number went to zero while a desktop owner could not reach **64 routes**. The
> guard was answering *some client can reach this*, which was true, in place of
> *this client can reach this*, which was not.
>
> That is the shape of every defect this audit has produced: a checker answering
> a question slightly to the left of the one that matters, and passing.
>
> **Two new guards, in all three repositories:**
>
> - `test_the_console_is_a_client_too.py` — the console's own backlog, checked in
>   both directions and ratcheted so it cannot grow past where it started. The
>   union guard stays; a route no client anywhere calls is still worse. A
>   phone-only capability is a legitimate design choice, which is what the
>   snapshot is for: deferring one takes a deliberate edit and shows in a diff.
> - `test_a_binding_is_not_a_door.py` — a function in `api.ts` that no screen
>   calls is not a door, and `doorless` counted it as one. The docstring on
>   `doorless` had said this was *"a discipline rather than something the test
>   can enforce"*. It is enforceable in about twenty lines, and found **25
>   bindings nothing calls**. *The test cannot check this* is a claim worth
>   testing.
>
> ## Screen 174 — "What you are owed"
>
> Nine of the sixty-four were the whole seller's side of the product. An owner
> could be bought from and could not post a licence offer, see who held one,
> revoke it, read a penny of what it earned, or ask to be paid — all present on
> the phone's Earn tab, all absent from the desk.
>
> Building the screen found three defects.
>
> **A statement added two currencies together.** ¥100 and $100 came back as
> `accrued: 200`, labelled with whichever sale was newest, and all three native
> shells render that figure with a currency symbol in front of it. Nothing was
> wrong with the entries; each carried its own currency the whole time. The
> arithmetic over them was wrong, in the one place where a wrong number looks
> exactly like a right one. Totals are per currency now (`by_currency`,
> `currencies`, and a `mixed` flag on the headline), the settlement currency is
> chosen deterministically rather than by recency, and a payout settles **one**
> currency and reports what is `remaining`. A single-currency account reads
> exactly as it did.
>
> **Anyone could delete anyone's listing.** `DELETE /marketplace/listings/{id}`
> asked for no credential, while `DELETE …/offer` — which destroys strictly less
> — answered the same stranger *"not your offer"*. Driven against a running
> backend: a stranger removed a listing that had a recorded seller, an open offer
> and a paid order against it. The offer and the orders survived orphaned and the
> title was free for somebody else to put up. A listing is now claimed by whoever
> staked something on it — the creator recorded in `listing_claims`, the seller
> on its offer, or the owner of the profile it advertises. Creating one still
> needs no token, and a listing with no claimant at all is still anybody's to
> clear away, which is the honest reading of an endpoint that needs none.
>
> **A sale credited to a key nothing reads.** This one came out of paying down
> the first of the 25 unused bindings. `PUT /marketplace/listings/{id}/offer`
> recorded the seller as the token's subject — and an **owner token's subject is
> a profile, not an account**, while `GET /profiles/{id}/earnings` resolves the
> profile to its `owner_id` before querying the ledger. So a seller who priced a
> listing while signed in as their profile's owner got `200` on the offer, `201`
> on the purchase with a real `ledger_entry` and the sentence *the sale is
> recorded on the seller's statement* — and an empty statement. The money was
> written under a key nothing queries, and every response along the way said it
> had gone through.
>
> It survived because nobody could do it: `api.setOffer` existed and no screen
> called it, and the phone prices listings as an *interactor*, whose subject id
> already is the account. `commerce.beneficiary_of` has resolved a profile to its
> owner for gifts since gifts existed — the same rule, never applied to the other
> half of the money. `_earner()` is that rule on the other half, across pricing,
> withdrawing and `GET /marketplace/sales`.
>
> ## Also
>
> - **`clientpaths.py` was not byte-identical across the three repositories**,
>   though it says it is. JIM-mini and PDI never received the `fetch`,
>   `window.open`, `<img src>` and `<a href>` call forms from 0.20.0, so their
>   backlogs counted doors that already existed. Restored; JIM's dropped 73 → 69.
> - **The pairing QR is built from a literal** in JIM-mini and PDI rather than
>   from a path arriving in a response body — a real door no static check could
>   see, which had got itself exempted as *not a client call*. That is an
>   exemption made out of a blind spot, and the last one of those turned out to
>   have no door at all.
>
> ## Where the numbers stand
>
> | | QRME | JIM-mini | PDI |
> |---|---|---|---|
> | union backlog | 0 | 69 | 58 |
> | console backlog | 55 | 109 | 84 |
> | unused bindings | 21 | 4 | 3 |
>
> The console backlogs are new, ratcheted, and now visible. That is the point of
> them.
>
>
> ## What's Changed
> * A marketplace somebody can use, and a guard that stopped inventing work by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/231
> * Record what breaks on the phone and the desktop shell too by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/232
> * Doors for the three two-party surfaces, and four tabs that showed their own key by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/233
> * An identity door, and two refusals that never reached the caller by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/234
> * Doors for how a profile presents itself, everywhere it is seen by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/235
> * Doors for what is live in a place, and one rule under three features by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/236
> * Reviewer development mode meant everybody, not localhost by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/237
> * A door for contesting a profile that depicts you by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/238
> * A door for the guide, a refusal with its structure kept, and the plan it names by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/239
> * Bodies, and where a rated profile is marketed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/240
> * A write that answers 200 did something by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/241
> * Two questions a mark answers by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/242
> * A signature over the bytes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/243
> * It observes and talks by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/244
> * The doorless backlog reaches zero (42 → 0) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/245
> * Cut 0.20.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/246
> * The installer could not report, and nothing said so by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/247
> * Ask each client the door question separately, and build the seller's side by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/248
> * Resolve a seller to their account, not to their profile by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/249
> * Cut 0.20.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/250
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.19.1...app-v0.20.1

## app-v0.19.1 — QRME app-v0.19.1

- Published: 2026-07-30
- Commit: `c899ceacb7025d04799309b4846161b124fb6c3a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.19.1>

> **QRME v0.19.1** — a feature can no longer ship with nothing drawn.
>
> The gallery tests all check screens against the README: a reference with no
> file, a file with no reference, a gap in the numbering. Every one of them
> starts from the screens. **None asked the opposite question — does this surface
> have a screen at all?** So a feature could ship undrawn, untaught and
> unreachable from the in-app helper, and the suite stayed green.
>
> That had happened three times, most recently to 0.19.0's own error-reporting
> card and its first-run notice, which went out undrawn while the release notes
> described them at length. It is the same shape of flaw found twice before here:
> a guard that only walks the relation in the direction where the answers already
> exist.
>
> `ui_screens.txt` is the missing direction. Every console surface carries a
> screen number, `undrawn`, or `unaudited`, so a surface nobody has classified
> fails in the round that introduces it. The mapping is declared rather than
> guessed — matching component names to screen titles resolved only a fraction of
> them, because titles are written for the person using the app and component
> names for the person editing it.
>
> Both backlogs are ratcheted against a ceiling each repository declares for
> itself, and a ceiling left high after the backlog falls fails too: a ratchet
> that stops ratcheting re-opens the ground it gained. Five failures were injected
> to prove it bites, including the one that matters — silencing the check by
> writing `undrawn` fails the ratchet.
>
> **And the two surfaces it caught are drawn.** Screens **150 What Went Wrong** and **151 Before Anything Is Sent** join the gallery, each
> with a lesson and with phrasings that reach it in the words somebody actually
> types when something has broken: "it failed", "something broke", "stop
> sending", "opt out". The card draws an operation and a status and nothing else,
> because that is all the log holds.
>
> **No application behaviour changes in this release** — screens, gallery,
> lessons, helper phrasings, and the guard that will keep them honest.
>
>
> ## What's Changed
> * Fail when a surface ships with no drawing, then draw the two that did by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/229
> * Cut 0.19.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/230
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.19.0...app-v0.19.1

## app-v0.19.0 — QRME app-v0.19.0

- Published: 2026-07-30
- Commit: `024f7755349481253652cd1afb53c0325b70e30b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.19.0>

> **QRME v0.19.0** — the app can tell you what broke, without telling you
> anything about anybody.
>
> Every failed request in the console is now recorded and, where a build has
> somewhere to send, reported. What gets kept is the *operation* and the
> status code: `POST /profiles/{id}/chat → 500` identifies a bug, where
> `POST /profiles/prf_0de08e794ed0/chat` identifies a person. Only the first
> is written down, and the redaction happens before the row is stored, so
> there is no moment at which the buffer holds something that would later
> have to be scrubbed.
>
> The obvious version of this would have quietly undone what every other
> screen promises. These backends put user input straight into their error
> messages — *no device called 'Pixel Buds' on this account*, *unknown site
> 'knee'*. Good messages for the person reading them, and the wrong thing to
> keep. So the message is shown to you, who own it, and is **never written
> to the log**.
>
> **Nothing goes before you have been asked.** Sending is opt-out, which
> only means something if the opting-out can happen before the first report
> rather than being discovered afterwards in a panel nobody opened. A
> first-run notice holds everything until it is answered — and it shows the
> actual payload rather than describing it, from the same function that
> sends it, so it cannot go stale while still reading honestly. The switch
> on the Control card is that same answer, changeable whenever.
>
> Counts are sent as **deltas**: each row remembers how much of itself has
> been reported, so reopening the app twenty times does not turn one broken
> screen into twenty. A failed send moves nothing, and the next launch
> retries.
>
> **The gateway refuses rather than redacts.** `cloudgw` gains
> `POST /v1/problems`, which accepts exactly five top-level keys and five
> per problem and rejects anything else — an unknown field, a `platform`
> string long enough to hide a sentence, a `day` carrying a time of day, a
> path with an unredacted id still in it. It could redact that path itself;
> doing so would let a build whose redaction had broken keep working while
> nobody learned that every report from those users had been arriving with a
> profile id in it.
>
> What survives is less than what arrives. Reports are not stored as
> reports — they fold into counters keyed by product, version, platform,
> operation and status. Locale is validated and then dropped, and nothing
> records that a particular install sent anything, or when beyond the day.
>
> **Off by default, by absence rather than by flag.** The collector address
> is compiled in at build time and unset, so an installer built without one
> has nowhere to send and no code path that could acquire one. There is no
> address for a later mistake to switch on.
>
> **Fixed** — four bugs found by running the thing rather than reasoning
> about it. The gateway had no CORS at all, so every browser preflight would
> have been refused and every report would have failed silently. Its
> validators were anchored with `$`, which in Python also matches before a
> trailing newline, so `Win32\n` passed a check whose error message promised
> newlines were not allowed. A counter file that was valid JSON of the wrong
> shape was adopted wholesale and took the read endpoint down with it. And
> the test guarding the payload shape ran only in this repository — the one
> where a leak would have mattered least.
>
>
> ## What's Changed
> * Guard every client path against the route table, in four languages by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/221
> * Check the verb, not just the address by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/222
> * Menus that keep their promises, and the routes with no door at all by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/223
> * A profile that can act for you, and a way to say how far by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/224
> * A desk you can actually staff by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/225
> * Record what fails, without recording anything private by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/226
> * Send the error reports, and refuse anything that is not one by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/227
> * Cut 0.19.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/228
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.18.0...app-v0.19.0

## app-v0.18.0 — QRME app-v0.18.0

- Published: 2026-07-30
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.18.0>

> **QRME v0.18.0** — the shells catch up, and so do the drawings.
>
> The two features that had gained console doors but no native ones now
> have them. **Who wrote this?** reaches Manage on iOS, Android and
> Windows — paste a passage and it names the profile that produced it, from
> the text alone, showing matched passages out of stored rather than a bare
> yes, and naming nobody at all below the 0.25 threshold. **The role
> picker** reaches the chat composer on all three, defaulting to "read my
> prompt" and reporting back which role applied *and whether it was
> declared or inferred*, so an inference is never handed back as an
> instruction.
>
> That completes something two earlier rounds each claimed and neither
> finished: every feature with a door in the web console now has one in the
> native shells.
>
> **And the drawings caught up.** Voice cloning, the recoverable watermark
> and the role all shipped with no screen, no lesson, and no way for the
> in-app helper to point at them — for two whole versions. Three screens
> join the gallery (**147 Your Own Voice**, **148 Who Wrote This?**, **149
> How Should They Work?**), each with a lesson in its proper chapter, each
> reachable by asking the helper in the words somebody would actually type:
> "clone my voice", "who wrote this", "just do it".
>
> **Fixed** — `SmallAction` on Android took no `enabled` parameter, so a
> busy or empty action looked live and merely ignored taps. It takes one
> now, and the label dims with it.
>
>
> ## What's Changed
> * Field round: portraits self-heal, phone layout, and the Wall reaches the console by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/208
> * Uploads on the wall — pictures, video, files — pasted links play, and two new front doors by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/209
> * Two more doors on the model menu, and the role rides the turn by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/210
> * Cut 0.16.0, and cite the publication number by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/211
> * Voice cloning, in the order FIG. 800 draws it by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/212
> * The watermark learns to survive being edited by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/213
> * The closing passage is not a release note by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/214
> * Three features come out from behind the API by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/215
> * Voice enrollment reaches the device that has the microphone by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/216
> * Cut 0.17.0, and fix a 404 under every like, comment and share by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/217
> * The last two console-only features reach the native shells by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/218
> * Draw, teach and make findable what 0.16.0 and 0.17.0 shipped by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/219
> * Cut 0.18.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/220
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.15.0...app-v0.18.0

## app-v0.15.0 — QRME app-v0.15.0

- Published: 2026-07-29
- Commit: `b835f783c6957a6494cb8c09184644caa73ca949`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.15.0>

> **QRME v0.15.0** — the temperament dials, the field's list verbatim.
>
> Steering gains a fourth dial group: mood, outlook, maturity,
> agreeableness, confidence, curiosity — each 0–100, defaulting to
> silence, rendered into the persona prompt exactly like the existing
> dials and picked up by every surface that reads the dial catalog.
> Together with language, the aging lifecycle, and the freeform persona,
> the video's "modify your profile's characteristics" list is covered
> dial for dial. Cut alongside JIM-mini's guided wellness round.
>
> ### Verification
>
> Full suite green.
>
> ### Install
>
> If you have 0.7.0 or later, this arrives on its own — one restart when
> prompted.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Cut 0.14.5 — cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/205
> * The temperament dials — the field's list, verbatim by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/206
> * Cut 0.15.0 — the temperament dials by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/207
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.14.4...app-v0.15.0

## app-v0.14.4 — QRME app-v0.14.4

- Published: 2026-07-29
- Commit: `3d7879229339db1a92d5227376d6d40c3e2481d2`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.14.4>

> **QRME v0.14.4** — the console names a version mismatch, and the field feedback lands.
>
> A stale backend from an older install used to mean silent "Not Found"
> on every newer screen; the console now compares its own version with
> the backend's on launch and says so in a banner, with a one-click
> repoint. Discovery cards carry the portrait and say which kind of
> face it is (AI badge on generated portraits; real-photo only on an
> authentic photograph). Room kinds read plainly. Blend explains itself
> — a brand-new openly-hybrid profile, not a follow. The Memory Vault
> gains Erase all, the two Settings credentials explain each other, and
> the chat Send button clears the help bubble.
>
> ### Verification
>
> Full suite green.
>
> ### Install
>
> If you have 0.7.0 or later, this arrives on its own — one restart when
> prompted.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The console names a version mismatch by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/202
> * Field feedback: faces on the cards, plain labels, erase all by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/203
> * Cut 0.14.4 — the console names a version mismatch by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/204
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.14.3...app-v0.14.4

## app-v0.14.3 — QRME app-v0.14.3

- Published: 2026-07-29
- Commit: `a8b62d59ce1cdb0e27fc91e7443fc41a8ab07c1f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.14.3>

> **QRME v0.14.3** — the lights are always on.
>
> The studio gains a round, watch-face-sized window pinned to every
> screen: the wrist's exact glanceable payload — green working, amber
> needs a hand, red stopped, with counts and the approvals line —
> polling the watch route with the owner token, ring colored by the
> worst light. A minimize control folds it to a dot in that colour when
> it is in the way, and the choice sticks. And the Matthew 7:24–25
> passage now closes every README in the repo, byte-identical, enforced
> by a binding test.
>
> ### Verification
>
> Full suite green.
>
> ### Install
>
> If you have 0.7.0 or later, this arrives on its own — one restart when
> prompted.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Cut 0.9.0 — no functional change; cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/177
> * Cut 0.9.1 — no functional change; cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/178
> * A real offline model — 0.10.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/179
> * The console catches up with its backend — 0.11.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/180
> * Cut 0.11.1 — no functional change; cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/181
> * The specification, mined: hybrid profiles, real-time simulation, environmental adaptation by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/182
> * The console shows the mined features: Blend, What If, and where you are by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/183
> * Cut 0.12.0 — the specification, mined by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/184
> * Both stones turned: crowdfunding with routed proceeds + the operational ecosystem by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/185
> * The console chrome follows the profile's language by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/186
> * Cut 0.13.0 — the ecosystem round by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/187
> * Demo org: one press, a staffed organization by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/188
> * Docs round: the tandem contract + invention disclosure catch up by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/189
> * Hardening: caps and idempotency on the new surface by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/190
> * Cut 0.13.1 — demo, docs and hardening by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/191
> * The front page and the wrist learn the new doors by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/192
> * Cut 0.14.0 — the front page and the wrist by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/193
> * The suite wires its own tandem, and one call builds the ecosystem by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/194
> * Cut 0.14.1 — the suite wires its own tandem by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/195
> * The vault posture survives suite mode by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/196
> * Docs: suite mode enters the tandem contract by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/197
> * The launcher shows the joints by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/198
> * Cut 0.14.2 — the vault posture survives suite mode by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/199
> * The lights are always on + every README ends on the rock by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/200
> * Cut 0.14.3 — the lights are always on by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/201
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.8.0...app-v0.14.3

## app-v0.8.0 — QRME v0.8.0

- Published: 2026-07-29
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.8.0>

> **QRME v0.8.0** — the continuity round, cut together with the siblings.
> No new routes here: QRME's part of the story was already built —
> reviewer-gated ownership succession (a profile passes to its named
> successor when its owner cannot authorize the handoff themselves) and the
> memorial sunset (a profile with no successor freezes rather than
> orphans).
>
> ### What joined up
>
> One attested absence now carries through all three products: JIM-mini's
> new **vigil** (the alarm that fires when a person's signals stop) produces
> an event id that serves as the succession `verification_ref` here, and as
> the activation reference for PDI's new **bequests** (vault scopes that
> unlock to a named person only at attestation).
>
> ### Verification
>
> 1188 tests green, unchanged in behaviour.
>
> ### Install
>
> If you have 0.7.0, this arrives on its own — one restart when prompted.
> Otherwise, download the installer for your OS from the assets below.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The app keeps itself current — 0.7.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/175
> * Continuity joined up — 0.8.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/176
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.6.1...app-v0.8.0

## app-v0.6.1 — QRME v0.6.1

- Published: 2026-07-29
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.6.1>

> **QRME v0.6.1** — a small honesty fix in Settings, cut together with the
> siblings at this version.
>
> ### Model honesty in Settings
>
> **Settings → Which model answers** now says plainly — in amber — when
> replies would come from the built-in offline helper (no working key on the
> deployment), or when the provider you picked has no key and another will
> answer. The silent case was the bad one: *Automatic* quietly resolving to
> the stub under a screen full of provider logos.
>
> ### What changed in the siblings
>
> JIM-mini's Apple Watch bridge: an iPhone Shortcuts automation drips Health
> readings at a per-user tokened URL (deposit-only — the reply never carries
> guidance), and uploading the Health app's export.zip seeds the baseline
> from months of history in one step — no events written, drift bands armed
> the same day.
>
> ### Verification
>
> 1188 tests green, unchanged in behaviour — which is the point.
>
> ### Install
>
> Download the installer for your OS from the assets below and double-click.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Pick your model by its own logo — 0.5.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/169
> * Cut 0.6.0 — no functional change; cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/170
> * Model honesty in Settings — 0.6.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/171
> * Record the inventions with dates by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/172
> * Restore the owner's LICENSE exactly as he wrote it by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/173
> * Screen 141: the model picker the gallery didn't show yet by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/174
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.4.8...app-v0.6.1

## app-v0.4.8 — QRME v0.4.8

- Published: 2026-07-29
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.8>

> **QRME v0.4.8** — the round where the app can actually send email. One
> of three interoperating products, all three cut together at this version.
>
> ### Mail is configuration, and now it is in the app
>
> An app cannot send email by itself; it has to hand the message to a mail
> server. Until now the only way to name one was an environment variable —
> so a desktop install never could, and a verification email was never going
> to arrive no matter how many times it was requested.
>
> **Settings → Email delivery** now takes a mail server, username, app
> password, from address and link address. It says plainly which source is in
> force (environment beats the settings screen beats nothing), and it
> **sends a real test message on demand** — reporting exactly what the mail
> server said rather than claiming success. The password is stored on the
> machine it was typed on and is never returned by the API.
>
> Configure one and local signup becomes genuine email verification again,
> with the clickable link as the headline and the 6-digit code as fallback.
> Leave it empty and the app says so, and lets you in — because an
> unprovable inbox is not a gate, it is a locked door in an empty house.
>
> ### Verification
>
> 1188 tests green, including that the password never comes back out, that
> the environment outranks the settings row, that a failed send reports the
> server's own words, and that configuring mail flips signup from local
> activation to a real emailed link.
>
> ### Install
>
> Download the installer for your OS from the assets below and double-click.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * An upgraded app no longer adopts an older install's leftover backend — cut 0.4.7 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/167
> * Email delivery is configurable from the app itself — cut 0.4.8 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/168
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.4.6...app-v0.4.8

## app-v0.4.6 — QRME v0.4.6

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.6>

> **QRME v0.4.6** — the round where verification matched the deployment.
> One of three interoperating products, all three cut together at this
> version.
>
> ### Signup that fits where it runs
>
> A desktop install has no mail service, so no email can ever arrive — yet
> 0.4.4's code screen sat waiting for one. Now:
>
> - **Desktop (no mail transport): signup goes straight in.** The machine
>   owner is trusted on a single-user local install — there is no inbox to
>   prove and nothing to prove it to. Create account → you're in.
> - **Hosted (SMTP configured): a real email with a clickable verify link**,
>   the shape every mainstream flow uses, with the 6-digit code as fallback.
>   Click the link in your mail and **the app continues on its own** — it
>   holds your email and password, so it signs in the moment the address is
>   proven.
>
> ### Also fixed
>
> - A signup that crashed mid-flight (0.4.3) no longer strands the retry: a
>   pending account routes straight to verification with a fresh code; an
>   already-verified address routes to sign-in.
> - The packaged app can open its own backend log from the verification
>   screen (Electron bridge) — relevant on deployments without mail.
>
> ### Verification
>
> 1178 tests green. The frozen binaries were rebuilt and the full first
> run driven against them — signup straight into a session, personal routes,
> sign-in, a profile created under the account, a chat.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.6` tag) and double-click —
> create your account and you are in.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * A stranded pending account is finished on a no-mail machine — cut 0.4.6 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/166
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.4.5...app-v0.4.6

## app-v0.4.5 — QRME v0.4.5

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.5>

> **QRME v0.4.5** — the round where verification matched the deployment.
> One of three interoperating products, all three cut together at this
> version.
>
> ### Signup that fits where it runs
>
> A desktop install has no mail service, so no email can ever arrive — yet
> 0.4.4's code screen sat waiting for one. Now:
>
> - **Desktop (no mail transport): signup goes straight in.** The machine
>   owner is trusted on a single-user local install — there is no inbox to
>   prove and nothing to prove it to. Create account → you're in.
> - **Hosted (SMTP configured): a real email with a clickable verify link**,
>   the shape every mainstream flow uses, with the 6-digit code as fallback.
>   Click the link in your mail and **the app continues on its own** — it
>   holds your email and password, so it signs in the moment the address is
>   proven.
>
> ### Also fixed
>
> - A signup that crashed mid-flight (0.4.3) no longer strands the retry: a
>   pending account routes straight to verification with a fresh code; an
>   already-verified address routes to sign-in.
> - The packaged app can open its own backend log from the verification
>   screen (Electron bridge) — relevant on deployments without mail.
>
> ### Verification
>
> 1178 tests green. The frozen binaries were rebuilt and the full first
> run driven against them — signup straight into a session, personal routes,
> sign-in, a profile created under the account, a chat.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.5` tag) and double-click —
> create your account and you are in.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Verification matches the deployment: direct on desktop, link-first by mail — and the 0.4.5 cut by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/165
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.4.4...app-v0.4.5

## app-v0.4.4 — QRME v0.4.4

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.4>

> **QRME v0.4.4** — the round where the Windows signup 500 died. One of
> three interoperating products, all three cut together at this version.
>
>
> ### The fix
>
> With no mail server configured, the verification code prints to the server
> console — in a banner drawn with box characters that the frozen Windows
> backend's cp1252 console encoding cannot represent. The print raised
> mid-request, so **every signup answered "Internal Server Error"** on the
> one platform the console transport serves most — found by a real first-run
> report within the hour of 0.4.3 shipping. The banner is ASCII now, the
> frozen entry point reconfigures stdout/stderr to replace rather than raise,
> and a test encodes the console delivery to cp1252 forever
> (mutation-checked). The console also stops hiding one error behind another:
> a non-JSON body ("Internal Server Error") now surfaces as the server's own
> words, not a JSON-parse exception.
>
> ### Verification
>
> 1175 tests green.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.4` tag) and double-click.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Fix the Windows signup 500, and cut 0.4.4 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/163
> * Release gate: the frozen backend must perform the real first run, per OS by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/164
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.4.3...app-v0.4.4

## app-v0.4.3 — QRME v0.4.3

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.3>

> **QRME v0.4.3** — the release where the app got a front door, and the
> installer got legs. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
> this version.
>
> ### Accounts — the address is proven before sign-in works
>
> Email + password, in the shape every mainstream flow has taught people, built
> as our own screens: create-account and sign-in tabs, show/hide password
> toggles, the password typed twice with a live match check, the requirement
> stated up front, and **Forgot password**. Behind it, the security spine:
>
> - `POST /signup` creates an account that **cannot sign in yet** — a 6-digit
>   code goes to the address (SMTP when configured, printed to the server
>   terminal otherwise) and only `POST /verify-email` proves the inbox and
>   mints the first token.
> - The account is what *owns*: its id is the `owner_id` profiles are created
>   under and the `account_id` memberships bill to. Every profile keeps its
>   own owner capability token exactly as before.
> - Password reset by the same emailed-code proof — and a reset **revokes
>   every account session**, so whoever prompted it, only the inbox holder
>   stays signed in.
> - Unknown-address and wrong-password answer identically, and neither resend
>   nor reset-request reveals who has an account.
> - Passwords PBKDF2 with per-account salts; codes hashed at rest, single-use,
>   15-minute expiry.
>
> ### Bring your own model key
>
> Paste your credential (Anthropic, OpenAI, xAI, Gemini) in the Control
> Center: it stays on your device, rides only your requests as
> `x-llm-api-key`, and the server **never stores or logs it** — a test dumps
> the whole database and asserts the key is not in it. A key makes your
> explicit provider choice usable with no deployment credentials at all, and
> on auto it defaults to Claude rather than the stub. The deployment's env
> key remains the fallback: an operator lending theirs out.
>
> ### The installer runs itself
>
> The whole Python backend ships **frozen inside the installer** (PyInstaller,
> per-OS) and the app spawns it at launch when nothing answers `/health` —
> double-click-and-done: no Python install, no terminal, data under the app's
> own user-data directory, the backend dying with the window. A backend you
> already run is left alone.
>
> ### Verification
>
> 1174 tests green. The frozen binary was built and booted on Linux; the
> account rules — code single-use, purpose-bound, reset revoking sessions,
> no address oracles, nothing stored in the clear — are each a test.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.3` tag) and double-click —
> this is the first release where that is the whole instruction. Or run
> `python -m qrme` and pick your device.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The desktop installers were labelled 0.3.3 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/159
> * Online model default, and the desktop first-run fixed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/160
> * Accounts, bring-your-own model key, the self-running installer — and the 0.4.3 cut by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/161
> * mac: declare the frozen backend in x64ArchFiles by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/162
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.4.1...app-v0.4.3

## app-v0.4.1 — QRME v0.4.1

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.1>

> **QRME v0.4.1** — the release where free got honest, and the claims got
> checked. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
> this version.
>
> ### A free plan, with nothing private about it
>
> Free reaches everything Basic reaches — your profiles, your own agent —
> so **$20 buys privacy, not features**. The difference is where your work
> lives and who holds it:
>
> | | | |
> | --- | --- | --- |
> | **Free** | platform custody | QRME holds it, you have access. Ordinary HTTPS, our database, in the clear, no vault at any point |
> | **Basic / Pro** | your custody | sealed in PDI before it lands, under a key you can hold, with a tamper-evident chain over every access |
>
> The disclosure is a **field on every surface that names a plan**, not a line
> in a Terms of Service. And the vault gate now asks about the *plan* rather
> than the deployment — it used to ask the other question, so a free account on
> a PDI-backed deployment had its work sealed into a vault it was not paying
> for and could not hold a key to. Guarded by counting vault writes, not by
> reading call sites.
>
> ### What the open store will not hold
>
> The test for the list is *whose exposure is it*: **source material about
> somebody else**, **anything behind the age gate**, and — found on the way
> through — **a clinician's written opinion about a real person**, which was
> heading for the open store because the referral flow writes through a path
> the third-party rule never saw. Refused before any clinician is contacted.
> A downgrade never unseals anything; an upgrade cannot un-expose what was
> already open.
>
> ### Channel 3 — sharing your camera
>
> Point your camera at the thing — a knocking engine, a boiler, a document —
> so somebody else can see it. The subject sets the rules: a thing, place or
> document can be watched by anyone; **a body only ever by a person, never a
> synthetic profile**. Two taps to open, one to close, hard time cap, and a
> disclosure on every surface.
>
> ### The claims got checked
>
> The README's "N tests" arithmetic is now verified against the files (two
> counts were stale), no user-facing copy may hardcode a refusal count that
> disagrees with the list (four did), and a refusal test must be reached by a
> request that would otherwise succeed — a mutation check caught one of this
> release's own tests passing for the wrong reason.
>
> ### Verification
>
> 1153 tests green. Screens 136–140 new, the tier and signup screens redrawn
> for the free plan, and every guard above mutation-checked.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.1` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Channel 3, a free plan under platform custody, and the guards that check the claims by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/157
> * Cut 0.4.1 — the round where free got honest, and the claims got checked by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/158
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.4.0...app-v0.4.1

## app-v0.4.0 — QRME app-v0.4.0

- Published: 2026-07-27
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.4.0>

> **QRME v0.3.3** — the release where an agent working on its own stopped being
> something you had to go and check. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### One question, answered everywhere
>
> An agent off doing work raises one question, and it is not *what phase is it
> in*. It is **does this need me right now?** Three colours answer it:
>
> | | | |
> | --- | --- | --- |
> | 🟢 **green** | working · done | in progress, or finished. Nothing wanted from you |
> | 🟡 **amber** | needs you | it has stopped and is waiting on a person |
> | 🔴 **red** | stopped | it hit an error or was cancelled, and will not continue |
>
> The word rides with the colour, because green alone cannot separate an agent
> that is still going from one that has finished — and those call for opposite
> reactions.
>
> ### Derived, never stored
>
> There is no `light` column and nothing sets one. It is computed in the single
> function every workflow read passes through, so a row cannot be persisted with
> a light that disagrees with its own status. A second field naming the same fact
> is a second field that can disagree with the first, and the one a screen reads
> would be the one nobody remembers to update. A test asserts the column does not
> exist.
>
> An unrecognised status **raises rather than defaulting**. A default would paint
> an unknown state green, and green is the colour that means *ignore me* — the
> one failure this must not have.
>
> ### Three surfaces, doing three different jobs
>
> **The watch** shows three lights and three counts and **no agent names**.
> Naming them was the first cut and was wrong: a name is something you read, and
> reading is the thing a glance cannot do. Which agent went amber is a question
> for the app, where there is room to answer it.
>
> **Screen 82** folds every agent into one tappable group per light. Somebody
> opening it *because* amber appeared should not have to scan a flat list for the
> one that changed.
>
> **The overlay** rides over an ordinary screen, and over **every** desktop view.
> This is the piece that makes the rest useful: an agent that reports only on its
> own screen is one you have to remember to go and check, and amber and red are
> exactly the states nobody thinks to look for. Desktop users have no wrist to
> glance at, which is why it is on every view rather than one.
>
> It is shaped like the watch face rather than as a bar across the screen — a
> small translucent box in the bottom-right, three stacked rows, each its own tap
> target. A bar reads as chrome and cuts the content in half; a corner box reads
> as something floating above the work, which is what it is.
>
> ### The README leads with the screens now
>
> Everything you can look at is above everything you have to read, and the
> run / config material is gathered under one **Reference** heading at the bottom
> — so a command spotted in a screenshot has one place to go and look it up.
> Those tables are set smaller, because they are for looking things up in rather
> than reading through.
>
> ### Also in this release
>
> - A group subtitle that ran under the chevron is fixed, and the builder now
>   length-guards them — the bug was visible in a render and invisible in the
>   source, which is how it survived being written.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.
>
> ### Verification
>
> 633 tests green (9 new). 212 routes. Both starter generators idempotent under
> `--check`.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.3.3` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Agent status light: watch, app, and an overlay that follows you by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/154
> * Release 0.3.3, and a README that leads with the screens by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/155
> * v0.4.0 — the social layer, channel 2, who you are allowed to be, and a price by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/156
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.3.2...app-v0.4.0

## app-v0.3.2 — app-v0.3.2

- Published: 2026-07-27
- Commit: `632ba1756697ccc57ddd3f60c0b2b655e4a96b26`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.3.2>

> **QRME v0.3.2** — the release where the starter collection stopped looking like
> a directory. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### The starter gallery shows each profile's own front page
>
> It used to be a portrait with a name and an industry captioned under it. That is
> a directory listing, not a profile — screen 80 gives a starter an avatar bubble,
> a role, **the rating people who talked to it left**, skill chips, Memory /
> Relationships / Engagement, a career, a review, and a **Talk to** button. The
> page was showing two of those.
>
> It was also **five columns wide** — roughly 590px of content on a phone that
> offers 390 — so on mobile the fourth column was sliced mid-word and the fifth
> never appeared. Every starter past the third was unreachable to anybody reading
> on a phone, which is most people. Two columns of whole cards fit, checked by
> rendering the real markup at 390px rather than by arithmetic.
>
> Generated from `qrme/seed.py`, not hand-written: the old gallery was a second
> copy of the starter list maintained by hand and could drift from it silently.
> Adding a starter without a role line is now a build error rather than a blank
> cell, and both tools have a `--check` mode.
>
> Careers and reviews are written, like the personas themselves — these are
> invented experts, so a CV is characterisation of the kind the bio already is,
> and each is drawn from that starter's own bio so the two cannot contradict each
> other. The rating and the three tiles are the app's own sample values, identical
> on every card: a freshly seeded starter has zero of each, so 34 cards reading
> *4.0 · 37 reviews* is self-evidently a template, and the README says so.
>
> ### Fixed
>
> **The rated starter was the only profile with no source material at all.** 0.3.1
> grounded every starter in its industry's Field Pack and left Vivienne Sable out,
> under a rule that ran two things together: the age wall governs *who may talk to
> her*, and was never a reason for her to know less about her own subject.
>
> The **Cabaret & Burlesque Field Pack** is theatre history and stagecraft — the
> Ziegfeld era, the Parisian revues, and why a tease is a rhythm problem. Free and
> unrated like the other 33, so it reaches her through the existing path with no
> change to `_ground()`. Seeding now reports `grounded: 34`, where it reported 33.
>
> Deliberately **not** the same thing as the $6.99 age-gated *After Dark Companion
> Pack*, which is conversational craft sold to owners of any adult-mode persona
> and never auto-installed. A test pins both so they cannot be merged by accident.
>
> **A test was asserting the gap into place.**
> `test_starter_packs_cover_every_industry` compared the pack list against
> `STARTERS` and not `STARTERS + RATED`, so the check that existed to catch a
> missing pack would have gone on passing forever with her ungrounded.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.
>
> ### Verification
>
> 624 tests green (2 new). 211 routes. Both generators idempotent under `--check`.
> All 34 cards clear their content by exactly 16px, checked across every file
> rather than eyeballed on one.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.3.2` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Show each starter as the card the app gives it by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/151
> * Starter cards: the whole of screen 80, career and reviews included by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/152
> * Release prep v0.3.2 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/153
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.3.1...app-v0.3.2

## app-v0.3.1 — QRME app-v0.3.1

- Published: 2026-07-26
- Commit: `00ff8490c549414e7b4f27f2e4ba408514aaefcd`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.3.1>

> **QRME v0.3.1** — the release where the starter profiles stopped answering from
> tone alone. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Highlights
>
> **Starters arrive knowing something.** `qrme/packs.py` has always described its
> starter packs as *"one free Field Pack per industry, **matching the Starter
> Collection**"*. The pairing was never wired. All 34 starters shipped with **zero
> source material** while 37 packs sat in the marketplace — Dr. Sana Iqbal had an
> environment persona and no environmental knowledge, Diego Fuentes a construction
> persona and no construction material. Every one of them answered from tone alone,
> which is a convincing impression of expertise and not the thing itself.
>
> Seeding now installs each starter's own industry pack, and it is part of the
> **repair** path — deployments seeded before this catch up by re-running seed
> rather than by hand across 34 profiles.
>
> Deliberately narrow, and each limit is a way of not overwriting somebody's
> decision:
>
> - **Only the starter's own industry.** Not "everything relevant" —
>   `build_system_prompt` renders `sources[:8]`, so a profile that hoards material
>   crowds out its own knowledge. One pack is three items, which leaves the budget
>   room to grow.
> - **Only onto a profile with nothing.** An owner who added their own material, or
>   removed the pack on purpose, is not topped up on the next seed.
> - **Free packs only, and no ledger credit.** A deployment grounding its own
>   starters is not a purchase; a priced pack stays a decision for whoever owns the
>   profile.
> - **The rated starter is left alone.** There is no adult-industry Field Pack, and
>   substituting one would be putting words in the profile the age wall exists to
>   contain.
>
> ### Changed
>
> **The README says which version you are looking at.** The title said `(v1)` and
> the only feature section mapped the original PRD scope, so thirteen releases of
> work were described nowhere a visitor would find them. There is now a release
> table, newest first, and the PRD map keeps its place while saying what it
> actually is — a conformance map, not a history. The same section went into all
> three repositories.
>
> ### Fixed
>
> **The README's avatar bubbles had no visible glow.** The bubble shipped in 0.3.0
> got the rounded clip right and then blurred the halo across most of the margin,
> which spread the light so thin it vanished against a dark page — a glow that
> existed in the source and nowhere a reader would see it. Narrowed the blur and
> raised the strength so the gallery matches the Profile Home screen it is meant to
> mirror. Checked by rendering against the app's own background, which is the only
> way this is checkable at all.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.
>
> ### Verification
>
> 622 tests green. 211 routes. The grounding limits are mutation-checked — a
> priced pack being auto-installed, and a profile with existing material being
> topped up, each fail the test that forbids it.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.3.1` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Ground each starter in its own industry pack; fix the bubble glow by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/147
> * Say what version this is, and what each release actually added by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/148
> * Release prep v0.4.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/149
> * Renumber this release 0.3.1, not 0.4.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/150
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.3.0...app-v0.3.1

## app-v0.3.0 — app-v0.3.0

- Published: 2026-07-26
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.3.0>

> **QRME v0.3.0** — the release where the tandem reaches a person. A synthetic
> specialist could answer a question; now it can be handed a multi-step task, and
> the person talking to it can be put in front of a real clinician with the
> release **signed for rather than ticked**. One of three interoperating products
> (with [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Highlights
>
> - **A specialist can be handed a task, not just a turn.** `qrme/workflows.py`
>   has always run `research → draft → review → send → confirm` in character,
>   carrying memory forward and surviving across sessions. Every route reaching it
>   was owner-only, which blocked the case the tandem needs: JIM's Guardian
>   handing work to a specialist it is already talking to.
>
>   Relaxing those routes would have been the wrong fix. **A workflow is not a
>   chat turn** — it runs several phases unattended and its `research` phase reads
>   the profile's vaulted source material, where a missing grant means scope
>   `["*"]`, *all of it*. So delegation is off until an owner turns it on, and
>   **delegating `research` without a grant is refused at write time**, where the
>   owner is present to read the error rather than at 3am inside somebody else's
>   workflow. An owner's own workflow has no `delegated_workflows` row, and that
>   absence is what keeps the two surfaces from ever merging.
>
> - **A referral to a real clinician, authorised by a signature.**
>   `POST /handoffs` could already package a session for a real provider — and it
>   released on `consent: true`, **a boolean the client sets**. Meanwhile
>   `qrme/webauthn.py` opens by describing itself as *"the layer that turns 'the
>   app says the user agreed' into something a third party can check"*, sitting
>   one import away from the single endpoint that ships somebody's health
>   conversation outside the product.
>
>   A referral signs at the **`high` tier**: document proofing on a device-bound
>   credential — the platform authenticator (Face ID / Touch ID / Optic ID) rather
>   than a passkey that roams. The challenge **is** the hash of the exact package,
>   and release re-hashes the stored bytes rather than trusting the hash recorded
>   beside them. Bound to one referral, so an assertion raised elsewhere is not a
>   skeleton key. The link **opens once**, and a second attempt says so rather
>   than quietly working.
>
> - **The clinician writes back, and the profile is caught up.** Opening the link
>   mints a reply token at that same moment — open once, reply once. The note is
>   sealed in the PDI vault under `qrme/{profile}/clinical/…`, the same treatment
>   source material gets.
>
>   It is deliberately **not** a `source_items` row, and that is the decision the
>   rest hangs on: source material is what a profile recalls *as its own*, and it
>   is what a workflow's `research` phase reads. Instead the note arrives in its
>   own prompt block naming the clinician — *these are that clinician's words, not
>   yours* — so the person does not have to retell their situation, and the
>   profile does not acquire a clinical opinion it can improvise from.
>
> - **Matching filters on expertise and only ranks on geography.** A cardiologist
>   two streets away is not a substitute for a psychiatrist. No match returns
>   nothing rather than a near miss: a confident wrong referral is somebody
>   phoning a clinic that cannot help them.
>
> ### Fixed
>
> - **The starter gallery on GitHub rendered 34 black boxes.** The portraits were
>   loading fine — they are square RGB with a near-black backdrop, and the README
>   embeds them raw, while the app draws its rounded avatar bubble at render time.
>   GitHub's markdown sanitiser strips the `style` attribute that would round
>   them, so on a surface QRME does not control the bubble has to be **in the
>   pixels**. `tools/bubble_portraits.py` bakes it, on transparency so the gallery
>   sits on whatever theme the reader has.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.
>
> ### Verification
>
> 589 tests green (40 new this release). 209 routes. Nine safety properties are
> mutation-checked — each fails the test that forbids it: delegating research
> without a grant, a delegated caller widening its envelope, an owner's workflow
> appearing on the delegated routes, a signature raised elsewhere releasing a
> referral, trusting the stored hash instead of re-hashing, a referral link
> opening twice, dropping the clinician attribution directive, a clinician
> writing back repeatedly, and one patient's note reaching another's conversation.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.3.0` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Owner-authorized workflow delegation by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/143
> * Medical referral: signed for, not consented to — and the clinician writes back by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/145
> * Bake the avatar bubble into the README portraits by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/144
> * Release prep v0.3.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/146
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.2.2...app-v0.3.0

## app-v0.2.2 — app-v0.2.2

- Published: 2026-07-26
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.2.2>

> **QRME v0.2.2** — a documentation release. **No code changed**: no new routes,
> no schema, no behaviour. Everything here corrects something that was
> *described* wrongly, which on this round turned out to be the thing costing
> real time. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Fixed
>
> - **`POST /marketplace/seed` advertised the opposite of what it does.** Its
>   docstring — the text served in the OpenAPI docs, which is where somebody
>   deciding whether a call is safe to make actually reads — still said
>   *"Idempotent — already-seeded profiles are skipped"*. v0.2.1 made that only
>   half true: the endpoint now also **repairs**, filling a missing portrait or
>   appearance on a starter that already exists.
>
>   The stale sentence pointed away from the fix. Anyone looking at three
>   starters rendering as bare initials would read that line and conclude the one
>   call that repairs them could not possibly help, because skipping is precisely
>   what they do not want. The claim was wrong in **four** places — the endpoint,
>   `qrme/seed.py`'s module and `seed()` docstrings, and the README's Starter
>   Collection row — and all four now say idempotent *and* repairing, blank-only,
>   reporting `repaired` alongside `created` and `skipped`.
>
>   **To repair a live deployment, this is still the one call:**
>   `POST /marketplace/seed`.
>
> - **Three releases of changelog links were missing.** `[0.1.9]`, `[0.2.0]` and
>   `[0.2.1]` had headings but no link definitions, so three shipped versions
>   rendered as literal `[0.2.1]` bracket text rather than linking anywhere, and
>   `[Unreleased]` still compared against `app-v0.1.8` — presenting a
>   three-release diff as though it were an empty one.
>
> - **The release checklist is why that kept happening**, and is the entry that
>   matters most here. `docs/releasing.md` step 1 said to move the `Unreleased`
>   items under the new heading and date it, and stopped — it never mentioned the
>   link definition at the bottom of the file. The step was skipped three
>   releases running by someone following the instructions correctly, and nothing
>   complains when you miss it: the heading renders fine, and the damage appears
>   hundreds of lines from where the edit was made.
>
>   Step 2 was wrong in the same direction. It named `pyproject.toml` and
>   `app/package.json` when the version string lives in **five** places — the two
>   it omitted being the `FastAPI(...)` call in `qrme/api.py` and the second root
>   entry in `app/package-lock.json`, both of which had to be rediscovered each
>   round. Both steps now say what they meant, in all three repositories.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.
>
> ### Verification
>
> 549 tests green — **the same 549, passing the same way**, which is the point of
> a release that claims no functional change. 197 routes, also unchanged. Version
> strings moved in exactly five places: `pyproject.toml`, the FastAPI app,
> `app/package.json`, and the two root entries in its lockfile (dependency
> versions untouched). Every version heading in the changelog was checked against
> its link definition — 12 for 12.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.2.2` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Correct the seed endpoint's idempotency description by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/140
> * Fix the release checklist that lost three sets of changelog links by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/141
> * Release prep v0.2.2 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/142
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.2.1...app-v0.2.2

## app-v0.2.1 — app-v0.2.1

- Published: 2026-07-26
- Commit: `61435e69b3be8b6bff4eb37c127b58f75e3ef44b`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.2.1>

> **QRME v0.2.1** — the release where a profile stops being a face and a sentence,
> and every screen gets something that can answer a question without pretending to
> be a person. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Highlights
>
> - **A profile has a front page.** Skills, experience, reviews, rating, and how
>   many people have actually talked to it — in **one call**, because the caller
>   is a scan page on cellular and five round trips is how a page arrives in
>   pieces.
>
> - **A review comes from somebody who was actually there.** It checks the
>   `engagement` row for a real interaction, and `UNIQUE (profile_id, author_id)`
>   makes a second review from one account impossible **in the schema** rather
>   than in a check somebody could forget — reviews are edited, never stacked.
>   Without both, a rating is worth exactly the number of accounts somebody can
>   make. The average always reports its own `count`: one five-star review and
>   two hundred are different facts.
>
> - **Experience about a real person is a credential.** On a `fictional` profile
>   invented history is the point and the AI mark says so. On one depicting
>   somebody real, *"twenty years at Accra General"* is a claim asserted on their
>   behalf, so it is refused without the same rights basis the persona needed.
>
> - **A help box on every screen.** Every screen here can be somebody's first — a
>   beacon scan lands a stranger on a profile page — and until now the only thing
>   that could answer a question was a synthetic profile, which is the one thing
>   that should never be answering questions *about the product*.
>
>   It is structurally **not a profile**: no name, no face, no memory. On a
>   product whose subject is synthetic people who can be mistaken for real ones, a
>   help assistant with a portrait would be a thirty-fifth character rather than
>   the thing that explains the other thirty-four. *Are you real*, *pretend you
>   are*, *what do you think of me* are caught **before any model sees them** and
>   handed back to the profile on the page. It writes nothing, and it works with
>   no model at all — the written answers are the answer, not an apology.
>
> - **The screens show real faces instead of a hologram.** Profile Home, Avatar
>   Studio and Live Video drew a purple orb with a generic person glyph where the
>   face belongs. All 34 starter portraits were already in the repo and exactly
>   one screen used them.
>
>   **A rounded box rather than a circle, and not only for taste**:
>   `tools/mark_portraits.py` burns the AI mark into the pixels at the top-right,
>   so a circular clip cuts off the corner the disclosure lives in. Those screens
>   name the character and their profession; "AI assistant" stays where it
>   belongs, in chrome that genuinely cannot know who is loaded.
>
> - **Screen 80** is the front page a visitor sees, as opposed to screen 5, which
>   is the owner's view of their own profile.
>
> ### Fixed
>
> - **Re-seeding repairs a starter that predates its portrait.** The seed is
>   idempotent by @handle, and idempotent meant *do nothing* — so a deployment
>   created before the portraits shipped was stuck showing **initials** on
>   profiles whose faces ship inside the package, and running the seed again, the
>   obvious repair, did nothing at all. It backfills blanks now and reports
>   `repaired` next to `created` and `skipped`. **To fix a live deployment:**
>   `POST /marketplace/seed`.
>
> - **The chat screen's online dot** sat at a fixed x that assumed a three-letter
>   name, so a longer one ran straight through it. Found by rendering the screen
>   rather than by reading the diff.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.
>
> ### Verification
>
> 549 tests green (26 new this release). 197 routes. 169 SVGs parse, and all 160
> rendered screens carry the help affordance. Both front-ends build clean.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.2.1` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The assistant has no name any more by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/137
> * Real faces on the screens, and a front page behind them by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/138
> * Release prep v0.2.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/139
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.2.0...app-v0.2.1

## app-v0.2.0 — app-v0.2.0

- Published: 2026-07-25
- Commit: `c4c7669976131609cecf6d50b3d0157bcf096b84`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.2.0>

> **QRME v0.2.0** — the minor bump, and honestly: **there are no functional
> changes to QRME in this release.** The three products version as one, and this
> round's work was next door. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
> this version.
>
> ### Why 0.2.0 rather than 0.1.10
>
> The 0.1.x line ran from a profile you could talk to, to a suite where all three
> products put printed codes on physical things and answer a stranger's phone
> with a page rather than JSON — desk beacons, care beacons, custody beacons, an
> agent at a facility gate that can speak but cannot decide, a marketplace you
> can search in words, and an escalation path in each product that reaches an
> actual human. That is a different product from 0.1.0, and 0.1.10 would have
> undersold it.
>
> ### What changed here
>
> - **Only one workflow writes the release body now.** `desktop-release.yml`
>   published `RELEASE_NOTES.md` **verbatim** — *"Ready-to-paste body for the
>   GitHub Release…"* preamble and all — while `sync-release-notes.yml` published
>   the same file with that preamble stripped. Both fired on the same tag push;
>   the sync finished in six seconds and the installer build finished two to four
>   minutes later and overwrote it. The build always won, so every release since
>   the sync workflow existed shipped the preamble until somebody re-ran the sync
>   by hand. The build no longer sets a body at all, and the sync now waits for
>   it rather than racing it.
>
> ### What changed in the siblings
>
> - **PDI** — a per-tenant on-call roster. `PDI_GATE_ONCALL` was one name for the
>   whole deployment, which in a multi-tenant vault routed every customer's
>   courier to the same person.
> - **JIM-mini** — nothing of its own this round.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent: spend
> totals, cooling-off, parental controls, a real identity check behind "verified
> adult", chargebacks, payout compliance. If you wire a real processor to these
> endpoints, that list is the work remaining.
>
> ### Verification
>
> 523 tests green — the same 523, passing the same way, which is the point of a
> release that claims no functional change here. 192 routes. Both front-ends
> build clean, and iOS, Android and Windows all compile in CI.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.2.0` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Only one workflow writes the release body now by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/135
> * Release prep v0.2.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/136
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.9...app-v0.2.0

## app-v0.1.9 — app-v0.1.9

- Published: 2026-07-25
- Commit: `c3f5ebf6096b0bc80edab5faf75dc922ff85ba53`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.9>

> **QRME v0.1.9** — a documentation release for this repository, and a real one
> for its siblings. The shared architecture doc had quietly stopped describing the
> architecture, and the three copies of it had stopped agreeing with each other.
> One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Highlights
>
> - **The tandem doc was missing an arrow.** For most of this project's life the
>   topology fit in one sentence: every arrow points *into* PDI, because PDI is
>   the bottom layer and a vault whose availability depends on a model provider is
>   a worse vault. PDI's gate agent broke that on purpose — it asks a QRME profile
>   for the words it speaks to somebody standing at a facility door — and the
>   document, its diagram and its section headings all still described the world
>   before that. [docs/tandem.md](docs/tandem.md) now has a `pdi ✕ qrme` section:
>   the flow, the fallbacks, and why the model is the voice and not the decider.
>
> - **Two of the three copies were describing a past release.** JIM's and PDI's
>   still listed the suite gateway's erase, export, consent and metering as
>   `[planned]` when `suite/gateway.py` had shipped them, and the docker-compose
>   end-to-end harness as planned when it runs in CI. A reader in either repo was
>   told cross-app deletion did not exist. The three copies are byte-identical
>   again, and the test counts it cited (*QRME 59, JIM 49, PDI 20*) are now the
>   real ones.
>
> - **The beacon family is written down as a family.** Three products now put a
>   printed code on a physical thing and answer three different questions with it
>   — a profile, a person somebody watches over, custody of data. The shared rules
>   were true in three places and recorded in none: a scan is a page and not JSON;
>   a dead code and a code that never existed render identically; the page renders
>   only what the server handed it, so it cannot disclose what the card withheld.
>
> - **The diagram is generated.** `tools/build_assets.py` writes
>   `docs/diagrams/tandem-flow.svg` from a block that is identical in all three
>   repositories, so one picture cannot become three that disagree. It replaces a
>   hand-drawn SVG that was cream-and-serif while every other asset in every repo
>   is night-indigo — and that showed two arrows, because it was drawn when there
>   were two.
>
> ### What changed in the siblings
>
> This release's functional work landed next door, closing the two gaps both
> escalating beacons had been carrying:
>
> - **PDI** — a gate hand-off now reaches a person. It used to record the on-call
>   contact's name and tell nobody, so somebody could stand at a door at 2am
>   waiting for someone who did not know they were there.
> - **JIM-mini** — `JIM_SITE_ROSTER` became a rota that knows who is on *now*,
>   and an escalation now actually sends something. A flat list pages the day
>   person at 2am, which is the feature failing in the hour it was built for.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent: spend
> totals, cooling-off, parental controls, a real identity check behind "verified
> adult", chargebacks, payout compliance. If you wire a real processor to these
> endpoints, that list is the work remaining.
>
> ### Verification
>
> 523 tests green. 192 routes. Both front-ends build clean, and iOS, Android and
> Windows all compile in CI.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.1.9` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * sync-release-notes: read the tag's notes, and stop duplicating What's Changed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/130
> * Generate the README cover instead of hand-building it by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/131
> * Marketplace search: words, place, and a hand with the words by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/132
> * The tandem doc describes the architecture that exists, and v0.1.9 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/133
> * tandem.md: JIM's test count by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/134
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.8...app-v0.1.9

## app-v0.1.8 — app-v0.1.8

- Published: 2026-07-25
- Commit: `1ffcfc704407c91daaa5bd741ca89a686a0b83d6`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.8>

> **QRME v0.1.8** — the release where a live desk stops being something you watch
> and becomes somewhere you can be. You can ask to come up on the stream, and the
> room's reactions render on the picture rather than beside it. One of three
> interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Highlights
>
> - **Two ways into a live room, and they are not the same act.** Watching and
>   commenting is something a viewer does; appearing *on* the stream is something
>   the host lets them do. `mode: audience` joins immediately; `mode: guest`
>   **only asks**, returning a pending request rather than a room — a join that
>   behaved as though the request had been granted would be the worst possible
>   default.
>
> - **Coming up has the gates the act deserves.** It needs an account, because the
>   host is deciding about a person rather than an anonymous request, and on a
>   rated desk a **verified adult**, because a guest there is someone *going live*
>   on an 18+ stream rather than merely watching one. One hand up at a time, a
>   decision made once, an owner-only queue — and a guest can always step back
>   down without asking, since needing permission to *stop* being on camera would
>   be the wrong way round.
>
> - **The reactions are on the picture.** `GET /desks/{id}/overlay` defines the
>   layer once — comments, likes, shares, gifts, who is up — so every client draws
>   the same one. They belong over the video because that is where the viewer is
>   already looking, and on a stream whose premise is an empty chair with a bell,
>   the reactions *are* the room. Transparent plates so the room stays visible
>   through them; the text on top is not faded, because chat you have to squint at
>   is chat nobody reads.
>
> - **The screens show what they had been describing.** Eight new mobile screens
>   and three desktop views cover live desks, desk beacons, the audience layer,
>   commerce and signatures — none of which had a screen at all. Three carry the
>   **real camera frames**, embedded rather than linked, because an SVG rendered
>   through an `<img>` tag cannot fetch external files. The signs in them are the
>   feature: *ring bell for service, away from the desk*.
>
> - **All 34 starter portraits are visible.** In the README, in
>   [docs/avatars.md](docs/avatars.md) beneath the briefs that specify them, and
>   as a grid on the Starter Collection screen — which used to say "seeded with
>   faces" and draw icon chips. No gallery carries a badge of its own: the AI mark
>   is burned into each portrait's own pixels, so it survives a screenshot, a
>   hotlink or a crop and travels into every page that shows one.
>
> ### Also fixed
>
> `[0.1.5]` and `[0.1.6]` in the changelog linked to release tags that were never
> pushed, so both were 404s. They now point at their release-prep commits.
> Deliberately *not* fixed by backfilling those tags — that would fire the
> installer build and publish two superseded releases dated after v0.1.7, at the
> top of the page people download from.
>
> ### Money here is still simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body. [docs/commerce.md](docs/commerce.md) lists what is absent: spend
> totals, cooling-off, parental controls, a real identity check behind "verified
> adult", chargebacks, payout compliance. If you wire a real processor to these
> endpoints, that list is the work remaining.
>
> ### Verification
>
> 500 tests green (14 new this release). 187 routes. 172 SVGs parse. Both
> front-ends build clean, and iOS, Android and Windows all compile in CI.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.1.8` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Point the untagged versions at commits, not missing releases by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/124
> * Screens for the capabilities 0.1.6 and 0.1.7 added by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/125
> * Show the starter collection in the README by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/126
> * Put the real camera frames into the live-stream screens by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/127
> * Show the faces on the Starter Collection screen by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/128
> * Release prep v0.1.8: version bumps, changelog cut, release notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/129
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.7...app-v0.1.8

## app-v0.1.7 — QRME app-v0.1.7

- Published: 2026-07-25
- Commit: `59fb9513b6aab1c7eec3a3f7d335c73c5b35ebdc`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.7>

> **QRME v0.1.7** — the release where a profile stops being only something you
> talk to. You can now like it, comment on it, share it, subscribe to it, gift
> the person behind it, and buy what they are selling — and a live desk can be
> left on a door as a printed code, the way a synthetic profile already could.
> One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
> this version.
>
> ### Highlights
>
> - **A live desk can be left behind as a printed code.** A profile beacon and a
>   desk beacon are the same gesture aimed at opposite things: scanning the first
>   reveals somebody who does not exist and the page marks the portrait *AI*;
>   scanning the second reveals somebody who does. So the badge is inverted and
>   deliberately unlike the AI mark at a glance — **Live person — not AI**, green
>   and top-right against the mark's neutral bottom-left — because absence of the
>   AI mark is not a disclosure on its own. The sticker goes on the shop door
>   *because* nobody is behind it, so the scan page carries a working bell.
>
> - **Like, comment, share, subscribe.** On a profile, a live desk, a room
>   message or a marketplace listing. A **like is a fact, not a counter** —
>   stored per person, so liking twice is still one like and no account can
>   manufacture popularity in a loop. A **comment** goes through the same
>   moderation pipeline as a chat turn, at the target's maturity setting; a
>   blocked one is kept and shown to its author with the reason, and to nobody
>   else. A **share** needs no account, because the person who scanned a sticker
>   is the one most likely to pass it on — the age gate lives at the destination,
>   not on the sharer.
>
> - **Subscriptions, free and paid.** A free `follow`, and a `paid` tier that
>   credits the creator's ledger each period alongside pack sales and licence
>   fees. Paid confirms the price explicitly, because a recurring charge nobody
>   meant to start *keeps* costing them. **Nothing bills on a timer** — periods
>   are charged by an explicit renew, so a deployment left running accrues
>   nothing unseen.
>
> - **The marketplace is transactable at last.** `listings` had no price and no
>   purchase endpoint, so a product could be listed and bought by nobody. Now a
>   listing is a shop window and an **offer** is what makes it a shop: price and
>   seller live in a row only a token-holder can write, and the seller comes from
>   that token rather than a request body. A listing nobody offered cannot be
>   bought — not by a check that could be forgotten, but because there is nowhere
>   for a price to be.
>
> - **Gifts, with rules purchases do not carry.** A gift sends money to a person
>   and receives nothing, which is the shape livestream tipping keeps turning
>   into a way of taking money from people who should not be spending it. So the
>   giver must be a **verified adult** whoever they are gifting, a single gift is
>   **capped**, a rated desk runs its own 18+ gate on top, and the recipient is
>   read from the subject rather than named by the giver.
>
> - **Windows signs, through the browser engine rather than interop.** The
>   blocker was `webauthn.dll` — hundreds of lines of version-sensitive struct
>   marshalling a compile cannot check. Edge already talks to Windows Hello, so
>   the desktop app hosts a **WebView2** on a new `GET /signatures/ceremony`
>   page served from the deployment's own origin. The page never sees a token.
>
> - **The three products now cut as one release.** Same number, same pass, even
>   when a repository has nothing of its own to ship — documented in
>   [docs/releasing.md](docs/releasing.md) in all three.
>
> ### Money here is simulated
>
> Subscriptions, gifts and purchases write **real rows** on the creator's
> statement and settle through the same payout sweep as pack sales and licence
> fees — but **no real funds move**, and every money-bearing response says so in
> its own body rather than leaving it to a policy page.
>
> [docs/commerce.md](docs/commerce.md) states what is *absent*: running spend
> totals, cooling-off, parental controls, a real identity check behind "verified
> adult", chargebacks, and payout compliance. If you wire a real payment
> processor to these endpoints, that list is the work remaining — not a set of
> nice-to-haves.
>
> ### Verification
>
> 486 tests green (48 new this release). Both front-ends build clean. iOS,
> Android and Windows all compile in CI.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.1.7` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * sync-release-notes: publish the release body from RELEASE_NOTES.md by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/103
> * Published deployments: pairing knows its public URL, optional signup key by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/104
> * Deployable as one container: Dockerfile builds the studio, docs/hosting.md by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/105
> * Profile portraits: art direction, the badge, and whose face it is by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/106
> * The Cloud Model Gateway server — the other end of a documented contract by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/107
> * Compile the native apps in CI by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/108
> * Beacons: a page instead of JSON, and shared rooms by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/110
> * Make the Android and Windows build failures readable too by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/109
> * See who the sticker is without leaving the camera by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/112
> * Release prep v0.1.5 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/114
> * Signatures that survive being disputed, and the Android camera overlay by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/115
> * The apps sign, the mark is in the pixels, and the portraits are cut on the right lines by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/116
> * Release prep v0.1.6, and three gaps the audit found first by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/117
> * Windows signs, through the browser engine rather than interop by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/118
> * README: repair the intro, standardize the patent line by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/119
> * Leave a live desk behind as a printed code by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/120
> * The audience layer: like, comment, share, subscribe by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/121
> * Gifts, and buying things on the marketplace by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/122
> * Release prep v0.1.7: version bumps, changelog cut, release notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/123
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.4...app-v0.1.7

## app-v0.1.4 — QRME v0.1.4

- Published: 2026-07-24
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.4>

> **QRME v0.1.4** — run it your way: one command prints every way to run
> QRME and you pick the device — your phone (scan a QR straight off the
> terminal), this PC, a packaged installer, or the headless API. One of
> three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### Highlights
>
> - **Run it your way — `python -m qrme`** — the launcher menu prints every
>   way to run QRME, one command each, so you pick per device: `phone` (the
>   QR flow below), `desktop` (the Electron app on this PC), the packaged
>   installer (no toolchain needed), or `serve` (the headless API alone).
>   `python -m qrme phone` does the whole phone setup in one command —
>   builds the studio if missing, prints the pairing URL **with a QR code
>   drawn straight into the terminal**, and serves on your local network.
> - **Run it on your phone** — the API serves the built studio at `/app`
>   (one origin for UI and API — nothing to configure on the phone);
>   `GET /pair` returns the URL on your local network with a scannable QR,
>   and the studio installs to the home screen as a standalone app with a
>   thumb-reachable bottom tab bar. Local network only, by design.
> - **Watermarking on every AI render** — all AI-generated work, textual or
>   visual, is stamped at creation with a verifiable synthetic-media
>   credential: chat turns (including proactive check-ins and farewells),
>   public posts, room turns, game and robot comms lines, creative works,
>   proofreads, perception guidance, task outputs, and voice/image/video
>   modalities. Anyone holding a piece of content can verify it —
>   `GET /watermarks/{id}` resolves the credential and
>   `POST /watermarks/verify` catches altered or substituted content.
> - **Owner-designed watermarks, displayed at all times** — each profile's
>   mark + label (`PUT /profiles/{id}/watermark`, design editors in all
>   three native apps) rides on every render; the AI designation is
>   invariant and cannot be designed away. Chat bubbles and post cards in
>   iOS, Android, and Windows show the mark.
> - **Terms of Service** — docs/terms.md served versioned at `GET /terms`:
>   assumption of risk and release, no-professional-advice and emergency
>   disclaimers, warranty disclaimer, liability cap, indemnification,
>   creator responsibilities, 18+ terms, and the simulated-commerce notice.
>   Profile creation is clickwrap with a server-side receipt (version +
>   timestamp recorded); refusal is refused (403); all three apps display
>   the agreement at the create screen.
> - **Signed, notarized builds wired** — hardened runtime + entitlements +
>   notarization in the electron-builder config: adding the Apple/Windows
>   signing secrets produces Gatekeeper-clean, SmartScreen-friendly
>   installers. docs/releasing.md walks through obtaining the certificates.
>
> ### Verification
>
> Backend suite green (QRME 270 tests); live-server smoke flows pass; the
> front-ends build clean; static native checks (XAML/SVG parse, brace
> balance, brush audit) are clean across iOS/Android/Windows sources.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.1.4` tag), run `python -m qrme`
> and pick your device, or open it on your phone — see the README.

## app-v0.1.3 — QRME v0.1.3

- Published: 2026-07-24
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.3>

> **QRME v0.1.3** — the trust release: everything the platform generates is
> watermarked and verifiable, users accept real terms with a receipt, and
> signed/notarized builds are wired. One of three interoperating products
> (with [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### Highlights
>
> - **Run it on your phone** — the API serves the built studio at `/app`
>   (one origin for UI and API — nothing to configure on the phone);
>   `GET /pair` returns the URL on your local network with a scannable QR,
>   and the studio installs to the home screen as a standalone app with a
>   thumb-reachable bottom tab bar. Local network only, by design.
> - **Watermarking on every AI render** — all AI-generated work, textual or
>   visual, is stamped at creation with a verifiable synthetic-media
>   credential: chat turns (including proactive check-ins and farewells),
>   public posts, room turns, game and robot comms lines, creative works,
>   proofreads, perception guidance, task outputs, and voice/image/video
>   modalities. Anyone holding a piece of content can verify it —
>   `GET /watermarks/{id}` resolves the credential and
>   `POST /watermarks/verify` catches altered or substituted content.
> - **Owner-designed watermarks, displayed at all times** — each profile's
>   mark + label (`PUT /profiles/{id}/watermark`, design editors in all
>   three native apps) rides on every render; the AI designation is
>   invariant and cannot be designed away. Chat bubbles and post cards in
>   iOS, Android, and Windows show the mark.
> - **Terms of Service** — docs/terms.md served versioned at `GET /terms`:
>   assumption of risk and release, no-professional-advice and emergency
>   disclaimers, warranty disclaimer, liability cap, indemnification,
>   creator responsibilities, 18+ terms, and the simulated-commerce notice.
>   Profile creation is clickwrap with a server-side receipt (version +
>   timestamp recorded); refusal is refused (403); all three apps display
>   the agreement at the create screen.
> - **Signed, notarized builds wired** — hardened runtime + entitlements +
>   notarization in the electron-builder config: adding the Apple/Windows
>   signing secrets produces Gatekeeper-clean, SmartScreen-friendly
>   installers. docs/releasing.md walks through obtaining the certificates.
>
> ### Verification
>
> Backend suite green (QRME 266 tests); live-server smoke flows pass; the
> front-ends build clean; static native checks (XAML/SVG parse, brace
> balance, brush audit) are clean across iOS/Android/Windows sources.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.1.3` tag), run from source, or
> open it on your phone — see the README's "Run it on your phone".
>
>
> ## What's Changed
> * Run QRME from your phone: served studio, pairing, installable PWA by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/99
> * Release prep v0.1.3: version bumps, changelog cut, release notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/100
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.2...app-v0.1.3

## app-v0.1.2 — QRME v0.1.2

- Published: 2026-07-24
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.2>

> **QRME v0.1.2** — the trust release: everything the platform generates is
> watermarked and verifiable, users accept real terms with a receipt, and
> signed/notarized builds are wired. One of three interoperating products
> (with [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### Highlights
>
> - **Watermarking on every AI render** — all AI-generated work, textual or
>   visual, is stamped at creation with a verifiable synthetic-media
>   credential: chat turns (including proactive check-ins and farewells),
>   public posts, room turns, game and robot comms lines, creative works,
>   proofreads, perception guidance, task outputs, and voice/image/video
>   modalities. Anyone holding a piece of content can verify it —
>   `GET /watermarks/{id}` resolves the credential and
>   `POST /watermarks/verify` catches altered or substituted content.
> - **Owner-designed watermarks, displayed at all times** — each profile's
>   mark + label (`PUT /profiles/{id}/watermark`, design editors in all
>   three native apps) rides on every render; the AI designation is
>   invariant and cannot be designed away. Chat bubbles and post cards in
>   iOS, Android, and Windows show the mark.
> - **Terms of Service** — docs/terms.md served versioned at `GET /terms`:
>   assumption of risk and release, no-professional-advice and emergency
>   disclaimers, warranty disclaimer, liability cap, indemnification,
>   creator responsibilities, 18+ terms, and the simulated-commerce notice.
>   Profile creation is clickwrap with a server-side receipt (version +
>   timestamp recorded); refusal is refused (403); all three apps display
>   the agreement at the create screen.
> - **Signed, notarized builds wired** — hardened runtime + entitlements +
>   notarization in the electron-builder config: adding the Apple/Windows
>   signing secrets produces Gatekeeper-clean, SmartScreen-friendly
>   installers. docs/releasing.md walks through obtaining the certificates.
>
> ### Verification
>
> Backend suite green (QRME 259 tests); live-server smoke flows pass; the
> front-ends build clean; static native checks (XAML/SVG parse, brace
> balance, brush audit) are clean across iOS/Android/Windows sources.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.1.2` tag), or run from source —
> see the README's Quick Start.
>
>
> ## What's Changed
> * Synthetic-media watermarking + macOS notarization wiring by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/95
> * Terms of Service: served, accepted by clickwrap, recorded with a receipt by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/96
> * Watermark every AI render, with owner-designed marks that always display by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/97
> * Release prep v0.1.2: version bumps, changelog cut, release notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/98
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.1...app-v0.1.2

## app-v0.1.1 — app-v0.1.1

- Published: 2026-07-24
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.1>

> **QRME v0.1.1** — the platform grows a body, a marketplace economy, and native
> apps at full parity. One of three interoperating products (with
> [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
> [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### Highlights
>
> - **Native apps at full parity** — iOS (SwiftUI), Android (Jetpack Compose),
>   and Windows (WinUI 3) now reach every backend surface: chat, community
>   (stranger matchmaking including the verified-18+ rated tier, multiparty
>   rooms), social & app connectors, robots, knowledge excursions, reach
>   (@handle + QR beacons, marketplace, licensing, earnings), settings
>   (model picker, objections, steering, relationship, feedback), and gaming.
> - **Steering, not piloting** — throttle/behavior/intimacy dials shape how a
>   profile comes across (tone, pace, manner), unified in a hub with its age
>   and appearance. The profile still acts on its own within its embodiments.
> - **Embodiments** — catalog robots as physical bodies with per-kind command
>   allowlists and installable task packs; smart-glasses connectors; and
>   agent-operated gaming companions for consoles and online play. The **watch
>   remote** puts agents, the profile, and robots on the wrist — green /
>   orange / red lights and one-tap remote actions.
> - **A working creator economy** — starter collection (30 industries + the
>   wellbeing trio), knowledge packs, robot task packs, federated pack
>   registries, and a creator ledger: pack sales, license fees, and verified
>   venue-placement views in one statement with payouts. Rated (18+) placement
>   keeps the age wall at the source, gates commerce, and seals its event
>   trail into PDI for provable custody.
> - **Rights & reach** — the complete third-party objection / revocation flow;
>   per-profile language + content provenance with translate-anything; and
>   first-run onboarding from provider login to a built profile.
> - **In-app feedback** — a "Help us improve" section on every client.
> - **Chrome localization** — the apps' own tab/nav labels in all 10 supported
>   languages, plus pull-to-refresh across the main screens.
> - **Ops** — `GET /health` with tandem flags, a repaired CI (the suite now
>   collects identically in CI and locally), and `python -m suite.smoke`
>   proving the whole three-product tandem stack in one command.
>
> ### Verification
>
> 553 backend tests green across the suite (QRME 251); live-server smoke flows
> pass on all three products; all four front-ends (app + launcher here, siblings'
> apps) build clean; the cross-product suite smoke passes end to end.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.1.1` tag), or run from source —
> see the README's Quick Start.
>
>
> ## What's Changed
> * README: fix a paste artifact (environmenlets → environment lets) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/47
> * Add first-run, login & immersive screens (login, verify, avatar, AR/VR, live video) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/48
> * Fix two text-overflow issues on the onboarding screens by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/49
> * Record post-0.1.0 onboarding screens in the changelog by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/50
> * Social connections: collect to build profiles, publish/run via QR beacons by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/51
> * Support all 16 connection platforms from the suite set by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/52
> * Connected-apps catalog: Apple, Google, Microsoft & Canva connectors by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/53
> * App connectors: connect a catalog app and use it (collect · act · produce) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/54
> * Safe knowledge excursions: study a topic without leaking private data by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/55
> * Add Knowledge Excursions screen (50) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/56
> * Add simple Files & Photos device-connector screen (51) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/57
> * Add per-assistant screens: Apple Intelligence, Google Gemini, Microsoft Copilot by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/58
> * Add native iOS/Android/Windows apps for QRME by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/59
> * Let profiles pick their LLM provider (Claude/OpenAI/Grok/Perplexity/Gemini) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/60
> * Complete third-party objection & revocation flow (audit + memorial/succession) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/61
> * Robotic embodiment: bind catalog robots to a profile as physical bodies by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/62
> * Native apps: add Robots and Settings (model picker + objections) screens by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/63
> * Native apps: add the Chat screen (the core interaction loop) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/64
> * Native apps: add Knowledge Excursions and consolidate the Studio tab by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/65
> * Native apps: add Connect (social platforms + connected apps), grouped with Robots by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/66
> * Native apps: add Community (stranger matchmaking + multiparty rooms) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/67
> * Native apps: add Reach (summon @handle + QR beacons, marketplace, licensing) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/68
> * Per-profile language + content provenance by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/69
> * Language at the create-profile gateway, translate-anything tool, and modes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/70
> * Starter collection: one synthetic profile per industry, seeded on the marketplace by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/71
> * Starter collection: mental-health trio for the JIM tandem hookup by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/72
> * Native marketplace browse: surface the wellbeing starters by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/73
> * Knowledge packs: downloadable expertise clusters on the marketplace by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/74
> * Robot task packs: marketplace modules for the bodies profiles embody by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/75
> * Docs: screens and module map for packs, robot mods, and embodiment by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/76
> * Pack registries: Robotmods.net and LLMmods.com on the marketplace by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/77
> * Rated placement: market 18+ profiles at adult venues, walled at the source by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/78
> * Rated commerce: the age wall covers buying, not just viewing by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/79
> * Placement analytics: what each adult venue earns by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/80
> * Creator ledger: one statement for everything a creator earns by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/81
> * Watch remote: agents, profile, and robots on the wrist by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/82
> * Pilot controls: live throttles and behavior sliders by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/83
> * Suite smoke: one command proves the whole tandem stack by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/84
> * Smart-glasses connectors + agent-operated gaming companions by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/85
> * Dials: drop the "pilot" framing, keep the throttle/behavior/intimacy dials by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/86
> * Steering: the owner shapes tone/pace/manner — not piloting by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/87
> * Steering hub: unify the dials with age and appearance by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/88
> * Help us improve: in-app feedback anyone can send by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/89
> * Placement earnings + PDI-sealed placement custody by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/90
> * Native round: steering hub, earnings, relationship, rated stranger tier by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/91
> * Chrome localization + polish across the native apps by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/92
> * Fix CI: make the test suite collectable outside `python -m pytest` by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/93
> * Release prep v0.1.1: /health, version bumps, changelog & notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/94
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.0...app-v0.1.1

