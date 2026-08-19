# QRME — AI Synthetic Profile Platform

**Current release: v0.87.0** ([changelog](CHANGELOG.md)) — one of three products
([jim-mini](https://github.com/davidsbianchi1984/jim-mini),
[pdi](https://github.com/davidsbianchi1984/pdi)) versioned and cut together, so
one number names one combination of all three.


> **Patent pending** — *Synthetic User Profile Management System*
> (U.S. Patent Application No. 19/056,418, Attorney Docket 526.P002;
> **published as US 2025/0265659 A1 on August 21, 2025**).

QRME lets a user create, customize, and interact with AI-driven synthetic
profiles — versions of themselves, another person (with consent/rights
handling), or a fictional persona. Profiles adapt to *who* they're talking to
(relationship-aware behavior) and *how engaged* that person is, while keeping
their core identity and boundaries fixed. See [docs/PRD.md](docs/PRD.md).

**Roadmap — AI agent management.** When activated, the platform can deploy
intelligent, role-specific AI agents that assist users, automate tasks, manage
workflows, and enhance operational decision-making — running more efficiently
and taking over mundane or outdated tasks and roles — all within the same
secure, private network environment.

QRME is one of three products versioned and released together — see the
banner above. The sister products:
[JIM-mini](https://github.com/davidsbianchi1984/jim-mini) (health guardian)
and [PDI](https://github.com/davidsbianchi1984/pdi) (private data vault).

## Ability is not a gate

If how a person's body or mind works stands between them and this product,
that is a defect in the product — not in them. This is stated upfront, before
features, because it shapes them: we build for blind and low-vision people,
deaf and hard-of-hearing people, mute and nonspeaking people, people with
limited mobility or amputation or tremor, autistic and cognitively different
people, people with dyslexia, people sensitive to motion — and for every need
not on that list, which is a gap in the list, not in the person.

What is true today, enforced by the suite rather than promised: every
function works by text alone and voice is always optional; every image in
the console carries a description (`test_ability_is_not_a_gate.py` fails on
one that does not); no step is timed; the console honours
`prefers-reduced-motion`; and the known gaps live in
[`tests/a11y_backlog.txt`](tests/a11y_backlog.txt), a ledger that only
shrinks. Anything that stands in your way can be reported from the
**Accessibility** screen — reachable *before* sign-in (`#access`), in ten
languages, with three questions and no diagnosis: what were you trying to
do, what stood in the way, what would help. Reports stay on the deployment
that received them (sealed to the PDI vault when one is configured, never
relayed to the shared error collector), are read with the deployment's
reviewer token, and become rows in that only-shrinks ledger. That is the
whole loop: your words become tracked work.



## What it does

| Capability | Description |
|---|---|
| **Synthetic profiles** | Create and interact with AI-driven profiles — yourself, another person with consent and rights handling, or a fictional persona — each conditioned on who it is talking to and how long they have known each other. |
| **Community** | Walls, feeds, friends, rooms (voice, camera, watch parties, games), gifts, and a marketplace of knowledge and task packs. |
| **The Studio and its agent** | A personal agent that edits your own page, writes widgets, posts, and searches the web — acting only through published tools, each behind the same doors a person uses. |
| **Voice and likeness** | Voiceprint enrollment under attestation, spoken voices bound from the provider's surface, avatars and masks — every generated utterance watermarked and every AI face marked as one. |
| **Governance** | Objections, takedowns, lifecycle states, signatures that survive dispute, tamper-evident provenance, and translated refusals in ten languages. |
| **Privacy** | Room pixels never cross clients; disclosures are recorded, not footage. `QRME_OFFLINE=1` keeps everything on the host, enforced at every socket. |
| **Tandem** | Runs beside JIM-mini and on top of the PDI vault, one version number across the three. |

## Watch faces, and the wearables that show them


QRME had a watch *API* and no way to say **which watch**. `POST
/profiles/{id}/wearables` pairs one over Bluetooth — a watch, band, ring,
earbuds or glasses — and says which faces it may show.

<table>
<tr>
<td align="center" width="25%"><a href="docs/watch/01-agents.svg"><img src="docs/watch/01-agents.svg" width="150" alt="Agents"></a><br><sub><b>01</b> · Agents</sub></td>
<td align="center" width="25%"><a href="docs/watch/02-activity.svg"><img src="docs/watch/02-activity.svg" width="150" alt="Activity"></a><br><sub><b>02</b> · Activity</sub></td>
<td align="center" width="25%"><a href="docs/watch/03-profile.svg"><img src="docs/watch/03-profile.svg" width="150" alt="Profile"></a><br><sub><b>03</b> · Profile</sub></td>
<td align="center" width="25%"><a href="docs/watch/04-control.svg"><img src="docs/watch/04-control.svg" width="150" alt="Control"></a><br><sub><b>04</b> · Control</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/watch/05-microphone.svg"><img src="docs/watch/05-microphone.svg" width="150" alt="Microphone"></a><br><sub><b>05</b> · Microphone</sub></td>
<td align="center" width="25%"><a href="docs/watch/06-identity.svg"><img src="docs/watch/06-identity.svg" width="150" alt="Identity"></a><br><sub><b>06</b> · Identity</sub></td>
<td align="center" width="25%"><a href="docs/watch/07-on-camera.svg"><img src="docs/watch/07-on-camera.svg" width="150" alt="On Camera"></a><br><sub><b>07</b> · On Camera</sub></td>
<td align="center" width="25%"><a href="docs/watch/08-lobby.svg"><img src="docs/watch/08-lobby.svg" width="150" alt="Lobby"></a><br><sub><b>08</b> · Lobby</sub></td>
</tr>
<tr>
<td align="center" width="25%"><a href="docs/watch/09-screens.svg"><img src="docs/watch/09-screens.svg" width="150" alt="Screens"></a><br><sub><b>09</b> · Screens</sub></td>
<td align="center" width="25%"><a href="docs/watch/10-proceeds.svg"><img src="docs/watch/10-proceeds.svg" width="150" alt="Proceeds"></a><br><sub><b>10</b> · Proceeds</sub></td>
<td align="center" width="25%"><a href="docs/watch/11-coordination.svg"><img src="docs/watch/11-coordination.svg" width="150" alt="Coordination"></a><br><sub><b>11</b> · Coordination</sub></td>
</tr>
</table>

**Paired at sign-up, not found in a settings page.** The agent lights and the
watch faces are worth having on day one, so the device step is part of joining.

| may be paired | |
| --- | --- |
| watch · band · ring | on the wrist, on the finger |
| earbuds · headset | in or over the ears |
| **lapel mic · clip-on mic** | clipped to the collar or clothing |
| glasses · pendant | worn on the face or at the neck |

| refused | why |
| --- | --- |
| smart speaker · conference puck · room array · tabletop mic · desk mic | each **hears whoever walks in** — and that person did not pair it, was not asked, and may have a right not to be recorded |

**The microphone kinds pair but do not listen.** Nothing in this module opens a
channel; a paired device is a registration and a set of allowed faces. A test
asserts no capture path exists here — no record, stream, listen or sample.

They are in the catalogue because the registry is what
channel 2 (lending a room your microphone) needs, and
a device somebody already paired for their watch face should not have to be
paired twice. That feature has now landed, and lending still happens *there*
rather than here — pairing says which devices you own, lending says what one of
them may do in one room, and keeping them apart is what lets a grant end with
the room without unpairing the watch.

**Room-facing microphones are refused at the door**, not allowed and then
restricted. A restriction is a setting somebody can change; a refusal is a fact
about the product. A platform cannot collect a waiver from a person who is
merely present, so until that is settled the whole device class stays out. The
refusals are published with their reasons so a client greys them out rather
than offering one and returning a 422.

**A wearable is not an embodiment.** `embodiments` records where a *profile*
lives — a speaker, a hologram, a robot body. This is hardware belonging to the
**owner**, reaching their own account. Folding them together would mean pairing
a watch could put somebody's synthetic persona on their wrist, which is a
different feature with a different consent question. A test asserts pairing
writes no embodiment.

**Pairing and permission only.** No sensor stream, no capture, nothing about a
microphone — a paired device here is a screen and a set of buttons. A test
asserts the pairing model does not so much as mention audio.

**Faces are a permission, not a free field.** A closed set, so a face added
later cannot arrive on every wrist by default — and a test holds the drawn
faces and the permission list in step, because a face you can enable and never
see is a permission granting nothing.

**Unpairing revokes rather than deletes.** The row survives, so a device sent
away cannot return by re-presenting the same name, and the owner can still see
what was ever paired — which is the question people actually ask after losing a
watch.

**Faces 06–09 all answer the same kind of question**: *what am I currently
presenting as, without looking at a phone.* Which profile you are posting as
and whether it is anonymous — the one mistake here that cannot be taken back,
and exactly the thing somebody assumes rather than checks when the answer is
two taps into a phone. What your camera is showing, which is the one thing your
own screen cannot show you, because the phone is in front of the lens and you
are behind it. Who is in the game with you, as counts. And which fixed screens
are live with you on them, because a fixture is the surface you can forget is
on — you walked away from it.

**05 Microphone is the one face that can end something**, and that is
deliberate rather than an exception to *"the wrist adds reach, not powers"*. A
lent microphone **is** this watch. Making somebody find a phone to stop their
own device listening would be the one permission on the platform you cannot
revoke from the thing it runs on, and *"yours to end, alone and at any moment"*
would be false.

**02 Activity is the community layer on a wrist, as counts.** Not the content:
a feed is a reading surface, and reading is the thing a glance cannot do. Same
reasoning that kept agent names off face 01.


The full desktop, mobile and portrait galleries live in
[docs/gallery.md](docs/gallery.md).

## Release history

<details>
<summary><b>What each release added, newest first</b> — the short version of
how it got here; full detail in <a href="CHANGELOG.md">CHANGELOG.md</a>.</summary>

| Release | What landed |
|---|---|
| **0.87.0** | **Profiles remember by meaning, and the pair holds the eraser** — `qrme/recollection.py` seals each thing a person tells a profile into the tandem and embeds it under the same key through PDI's resident index (a hash, never the text), so the reply that matters finds the moment it is *about*, however long ago — with the prefix carrying the profile *and* the interactor, because what Alice told it must never surface for Bob. The pair's sealed shelf lists every moment the vault remembers with a per-moment forget, and every transcript door keeps the promise the shelf makes: strike, forget-by-words, rewrite and erase-all all reach the vault — `sealed_forgotten` says what actually let go, an edit re-seals the words as they now stand, and profile erasure takes seals, ledger rows and vectors together. Plan-gated at every seal point, honest at every failure, on the console and all three shells |
| **0.86.0** | **The AR and VR rooms become places to stand in** — the room screen reads the channel the join answer has always carried, and the two immersive kinds offer a stage: AR anchors every seat over the device's own passthrough at positions the seat index decides, with the honest note that nothing of your surroundings is streamed or stored and a refused camera downgrading to a plain backdrop that says so; VR renders a floor grid under a turntable of seats, each card counter-rotated to face you from wherever a drag leaves the room turned. Both keep the scene's rules — chosen photos, AI-marked portraits, the talking light — and the last thing said rides the stage. Entered by a press, left by one, in ten languages |
| **0.85.0** | **The beta round, worked end to end** — nine merged rounds from one evening of the owner's field reports. The room camera goes full-bleed, flips, and draws masks on the wearer's own preview, with every AI seat wearing its portrait; profiles speak with voices bound from the engine's own surface (`qrme/spoken.py`), all 34 starters and both founder profiles bound at seed; the agent screen lands where its owner corrected it — the mic records into the box, a drawn waveform opens the orb, and **Create picture or video / Search the Internet / Write or edit** each function, the search through a new keyless door that also reached all three phones. The feed plays what the wall played, Discover cards open their profiles, friends wear faces with a small red ✕ and a `GET /people` finder, the blend fits a phone, rooms open by kind (VR/AR/2-D) from a decorated homepage with the roster on every card. The fifty-six-door menu becomes six professional groups behind a top-left drawer, two dozen tabs renamed in ten languages with seventeen screen interiors matched to them; Live Now leads with what is live; the chat composer's tools fold behind a +; and `available` finally means somebody real answers, with What If wearing its no-model banner |
| **0.84.0** | **The step that was impossible to perform** — 0.83.0 moved `exit` to the first line of each check block on the deploy page, reasoning that it was the same repair as the `ssh` at the top of the deploy block. The next deploy proved the reasoning wrong in one paste. The two are not symmetric: `ssh host` followed by more lines works, because ssh takes the rest as standard input and runs it on the far side; `exit` followed by more lines does not — the shell tears down and the remainder goes into a session that is already closing. It echoes, and it is gone. A deploy that had gone perfectly, three checks that never ran, and no error to say so. The first version made the step easy to skip; the second made it **impossible to perform**, which is worse, because a skipped step at least leaves a prompt you can still type into. Getting to your own machine is a new window, and that is prose because it is not a command — the guard is inverted to match, a check block must now contain no change of machine at all where it previously required one. Its companion was too loose to catch anything on the first pass: it accepted a bare *new window*, which the paragraphs explaining why it is a new window also contain, so deleting the instruction left it green. That is the second guard on this page in two days to match its own surrounding prose — a guard that can be satisfied by the explanation of a rule is not checking the rule |
| **0.83.0** | **The page somebody pastes, one step further down** — 0.82.0 put `ssh` inside the block you copy, because a fenced block of its own is a block you skip. The next deploy found the identical defect one step down, twice in the same paste: `exit` was a sentence *between* the deploy and the version checks with a paragraph under them explaining why it mattered, so the checks ran on the host — the one place they prove nothing, since they answer from inside the network they exist to test from outside — and the Windows block, correct in every character, sat where the next step goes, so it got run too, in a shell with no `curl.exe`. `exit` is the first line of each check block now, the two blocks are marked as a choice rather than laid out as a sequence, and each carries all three products because a block somebody runs on its own has to check all three on its own. One of the three new guards was itself written too loosely on the first pass — it accepted the word *either*, which § 7 already contains four paragraphs up, so it passed on a page carrying no marker at all: a guard whose word can arrive by accident reports on the prose rather than on the shape |
| **0.82.0** | **The page somebody pastes, and the sentence that forgot how it was built** — `docs/beta-deploy.md` § 7 warned that `/srv/qrme` is on the host and then put `ssh root@your-host` in a fenced block of its own above the deploy, and a block of its own is a block you skip: what gets pasted is the thing that looks like the procedure. It was pasted into PowerShell on a handheld and failed twice — no such path, and no `docker` — then failed a third time on check lines carrying `; echo`, which in PowerShell is `Write-Output` and at the end of a pipeline with nothing feeding it stops and prompts for input. Both are one failure: a correction written *about* a command instead of *as* one. The `ssh` is the first line of the block now, the PowerShell form is written out as its own block, and a guard holds the shape — the page may be rewritten, and its commands have to stay runnable by the reader they are addressed to. Beside it, the guard for the defect 0.81.0 fixed at the one site that was known: `test_a_built_sentence_is_not_laundered_through_str` reads which of this product's own exceptions carry a built sentence and fails any route that catches one and passes on `str(exc)`. It found a second site immediately — the excursion route, written in the same round as the fix, laundering the privilege refusal exactly the same way |
| **0.81.0** | **A roster of what the agent may do, and nobody says yes by arriving** — the product grew powers faster than it grew a place to see them: studying the open web, asking strangers, briefing a real professional, running a job over vaulted material, reaching emergency services. The only way to learn what one could do was to meet a power mid-conversation. Every row is on one list now, saying what the agent would be allowed to do, **what it keeps** — the half these lists omit, because summarising a meeting and summarising a meeting *and keeping the recording* are different agreements — and whether it reaches somebody who never chose it. That last one is a field rather than a paragraph so a guard can read it: nothing that reaches other people is ever on by default, and the one row that is on carries the written reason why. The check sits at each power's own last hop rather than in the route above it, the refusal names the thing instead of the identifier and arrives translated, and visitors read the same list — what an agent may do on somebody's behalf is not a secret kept from the person it would be done to. Alongside it, the dialer's sealed-call sentence had been reaching every reader in English: `str()` on a built sentence forgets how it was built |
| **0.80.0** | **The agent asks people, and somebody is counting the visits** — an excursion asks a model and gets back what was already written down. An **inquiry** asks people: the question goes on an open board anybody can answer with no account and no name, and an answer the owner accepts folds into the profile as a knowledge source, so the offline model ends up knowing something it could not have looked up while the person who knew it never learns whose question it was. The sanitiser cannot be told not to — a guard fails any boolean parameter and any branch inside it — and the board carries the scrubbed line and nothing else, not even the redaction count, because two questions with the same unusual count are a thread to pull. Beside it, the case a scrubber never covered: offline mode answered *did anything leave*, and nothing answered *who has watched us leave, and how often*. Every outbound connection is now witnessed at the one function every socket already passes through — **host only, never the path**, because in a profile fetch that tail is the subject's own handle — and standing a host down refuses at the socket, so it binds every fetcher rather than the screen that listed it |
| **0.79.0** | **The shop, the lock, and the button nobody ever had** — the connector catalogue was forty-two rows of device AI, reachable only through a dropdown labelled *provider* inside another screen. It is a hundred and three rows across nine families now — the inbox, the drive, the tracker, the payment processor, the open web, and the social pages a profile reads without ever posting to — with a storefront on the console and all three phones. Each row says what it needs before it can reach anything, and that lock is a posture: `invoke` used to answer *performed* for every connector on the board having reached nothing at all, and now refuses an unsigned-in one by name. Two guard findings came with it — the door guard skipped every path starting `/app`, meaning the console bundle, and `/apps` starts with it, which hid that **uninstalling a connector had no door on any client** |
| **0.78.0** | **A front door, not a poster** — the Agent tab shipped as an illustration at full width above a card you had to scroll past to type into. It is a composer now: one pill with `+` inside on the left and the microphone, the room and send on the right, five attachment entries that each open a screen that exists, a rail of nineteen destinations scrolling sideways, and three openings for somebody who has the screen and not the sentence. The mark is the tab's and only the tab's. Alongside it, the deploy page learned to say which machine you are supposed to be standing on |
| **0.77.0** | **The Agent, opened up** — the agent that rewrites your page and writes your widgets got its own tab, second in the row, and a roster that went from eleven rows to 113: the profile itself, what it knows, the face it wears, the wall, money, the stickers and robots and watches, messages, what it remembers of people, and how it ends. Twelve of those cannot be taken back, so they stop and ask — the sentence the roster promised, the arguments it chose, and a button. Alongside it the room became a scene, every box a place to turn on video or wear a mask, and a reply that ran out of room now says so instead of stopping mid-sentence |
| **0.76.0** | **The Studio's run button answered a 500, and the suite proved the walls** — nineteen sandbox cases called `run_source` with a source string and not one ran a *stored* widget, so `widgets.run` asked a row-mapper's output for the column name it renames on the way out and raised `KeyError` before the code started. Every press, since the Studio shipped. Alongside it, thirty-four starter homepages: a face in a friends grid is a link, the Starter Collection is the one place a fresh deployment has a full grid, and every face opened the same blank purple page — now composed from each starter's own dossier, with no invented links and a palette per family of trade |
| **0.75.0** | **A bare "s" is not a word, and that is why it was on the list** — the console-untranslated ceiling was 1, went to 58 when the reader learned to see a sentence chosen at render time, and is 1 again: fifty-seven strings across ten screens now carry a key and ten translations. Two of them were never translation work. Lobby rendered a bare `"s"` as its own node after a session count — English pluralisation as a suffix, which is not how the plural works in most of the other nine languages — and Remainder did the same with `thing`/`things`; both are one whole sentence per number now. The row that stays is `AI ·`, quoted rather than written, because the server hardcodes those two characters and a translated `IA ·` would be a mark the product never produces |
| **0.74.0** | **A post that stops inside a word, and a face filed under "somewhere else"** — a profile asked for a specification answered at length, the wall took the first two thousand characters, and the reader got a sentence ending mid-word, then asked it to finish five times. The cap is 20000 now, and past it `parts()` makes a numbered series where every piece says where it sits and every piece but the last says it continues: a cut is allowed, a silent one is not. Also: the skin shelf has named eight avatar systems for releases while the importer filed every face from a phone under "somewhere else", and the sidebar was the only one of fifty console files anything checked |
| **0.73.0** | **The briefcase, the avatar that is not the profile, and one face for a face that is not there** — a link pasted into a turn was fetched, read, and then evaporated: the next turn carried no page, so discussing a document meant pasting it again and paying its full length again, and a photograph, a filing or a video had no way in at all. `qrme/briefcase.py` reads what you hand over **once**, distils it to a digest, and it is the digest every later turn carries — scoped to the pair, so the next visitor inherits none of it. A portrait can now be a video, a rigged model or a bought character skin rather than only an image, picked from a market shelf the way a voice is, with a standing figure for each of the 34 starters. Memory follows the account instead of the browser, so a laptop and a phone are no longer two strangers. And a profile with no portrait had **five** different faces across the surfaces — initials twice on the console, a blue orb, initials on the beacon page, and an Android overlay that drew a monogram *always* and never read the portrait it was sent; there is one frame now. Also fixed: `CREATE TABLE IF NOT EXISTS` is not a migration — an indexed new column meant `connect()` raised on every database that already existed |
| **0.72.0** | **Their homepage, and the phones that can now open one** — pressing a face opened a card showing the *signed-in* profile's numbers under somebody else's name; the new screen carries their page, their Top 8 walking onward, their wall and their uploads, and no stats row at all, because `/stats` is owner-only and that is how the old card came to be wrong. `GET /profiles/{id}/media` gives the upload door its other side. iOS, Android and Windows get the same screen — their `PageCard` bindings were three fields out of a payload carrying eight, which is why no shell had one before |
| **0.71.1** | **The API did not import on Windows** — `widgets.py` imported `resource`, which is POSIX-only, at the top of the file, and `api.py` reaches it through `routers/studio`, so this was not an unavailable sandbox but the whole API failing to import: the frozen desktop backend died on first run, the Windows installer job failed, the release job was skipped, and 0.70.0 and 0.70.1 published with no installers attached at all — not even the macOS and Linux ones that had built. The import is now allowed to fail and the runner says so in the reader's own language; the guard is a property of the text, because a suite that only runs on Linux can never import its way to this |
| **0.71.0** | **The player learned the origin, and the deck became the screen** — a YouTube post on the Wall rendered the platform's own *Error 153* because `referrer-policy: no-referrer` is right for a page reached from a QR sticker and wrong for the players the console embeds, so the beacon pages keep it and the two players get the host and never the path; and a pane holding footage is now the footage, with the pill, the position and the caption riding over it on scrims rather than a header above the frame and a caption below it taking half a phone |
| **0.70.1** | **The sandbox could lie about itself** — the widget runner asked whether *an* interpreter existed and never whether it was new enough, so a host carrying Node 18 reported ready and then failed every run on a flag its author never typed; the floor is Node 20, where the filesystem wall arrives, and it is guarded by measurement rather than by a literal — the interpreter this host offers either passes the floor or does not, and either accepts the flag or does not, and those two answers have to agree |
| **0.70.0** | **Your own code in a box, an agent that writes it, and a Feed you swipe** — a widget runs on the backend with no network, one directory, no child processes and finite time, and the runner refuses outright rather than running with three walls instead of four; an agent edits your page, your homepage and your widgets through the same doors you would have used, reaching no further than a written list of ten that a guard resolves against the route table, with the profile bound from your session rather than named by the model and every door it went through listed under what it said; the Feed became a deck where one item fills the screen and a swipe brings the next, with anything held on somebody else's platform still waiting for a press. Also: turns are selected and struck or rewritten in place with the edit recorded but never the old words; an export QR carries a single-use ten-minute ticket and never the owner token; the console's own CSP stopped blanking every video player; the failure reports come home to this backend; and the extractor now reads a ternary's branches, which found nine English buttons on the screen a stranger meets |
| **0.68.0** | **The memory door, the steering lock, the card carried in, and the room that forgets on purpose** — a persona tells you what it actually holds about you and forgets one named thing without erasing the friendship; the owner locks the dials against everyone including their own slip; a chara_card_v2/v3 card (JSON or PNG) seeds a profile with its harness instructions withheld by name; and a rehearsal room plays the hard conversation without a word of it entering the relationship's memory |
| **0.67.0** | **The licence carries the substance** — a finetune or clone derive hands the buyer the profile's knowledge, dials and (on a clone) an aggregate adaptation summary, under a manifest of what crossed and what stayed; organizations lease a stranger's licensed specialist as a revocable department; the portrait moves at a tempo its own history sets; and a persona remembers the room between turns |
| **0.66.0** | **Cut in step** — no QRME code changed; JIM-mini's coach became an offline add-and-norm stack over stored knowledge and current readings, with a jampacked pack, deposits from paid model turns, and a curriculum JIM studies on one press |
| **0.65.0** | **A standing room is one place, not a stamp** — the standing rooms stop minting copies: `POST /rooms/templates/{key}/open` joins the newest live room with a free seat and only opens fresh when nobody has it open, a full porch gets a second table, and `POST /rooms/{room_id}/join` gives the lobby's “step in beside them” pitch real behavior — eight seats, refusals in ten languages, all four clients through both doors; and a friend's face on the home screen now opens that friend's page, not the list it sat in |
| **0.64.0** | **The catalog steps out, the rooms stand ready, the footsteps show** — the connected-apps card asks the forty-app catalog instead of offering one hardcoded button; twelve standing rooms answer at `GET /rooms/templates`, one press from real on the console and all three phones; a footsteps counter rides `/health` into every console's corner (and shrank to a footprint the same evening, on a field report); the chat handed back its walls — presence rendering belongs to the rooms and the vastscape, a text thread is its own scene; and the social scrape refuses a login wall in ten languages instead of storing the platform's words as the person's |
| **0.63.0** | **The talk surface shows the face, and the face has a deck** — the microphone opens a full listening screen with the profile's portrait front and centre, pulsing while it listens, the reply spoken back (the orb only for a profile with no portrait yet); Identity's portrait card becomes a deck — characters, your own photos, a five-angle capture, and the avatar systems people already live in as imports with provenance on the record (`GET /avatars/market`, `POST /profiles/{id}/avatar/import`); the chat scrolls to the newest reply as it commits; `POST /social/{cid}/scrape` keeps what a public page shows anybody as a source item; and the console fits the phone it runs on — grid tracks clamp, `100dvh`, the sidebar scrolls on its own |
| **0.62.0** | **Cut in step** — JIM's phones reached parity with its console — eleven rounds in one branch: every backend route gained a door on iOS, Android and Windows (the doorless ledgers close at the four by-design rows), the voice pair landed on all three shells with the device's own voice as fallback, Android learned to say PATCH through a test-pinned override, and the most-touched screens swapped their English for the ten-language tables. No QRME code changed. |
| **0.61.1** | **Ability is not a gate** — an accessibility statement with a door under it: the Accessibility screen reachable before sign-in (`#access`), three questions with no account, no token and no name (the table has no identity column to fill), sealed to the PDI vault and read only under the reviewer token. Signup opens for the beta behind a keyhole that stays. The known-gaps ledger opened at three rows and closes at zero — wall uploads describe what they show, the chat log tells the screen reader, the shells carry the per-need statement — every closure held by a test, and Terms 1.2 says only what is true |
| **0.61.0** | **The beta stands up** — three products behind one proxy on one host, and the first real run found what no in-process test could: every console blanked by its own Content-Security-Policy. A policy of its own for `/app`, the bare domain now lands on the console, backups become a nightly job instead of instructions, bootstrap keeps its tenants across restarts, and the release-bodies sweep survives its first honest run — twice repaired, then proven against the live releases |
| **0.60.9** | **No change to this product** — the release-body work ends: every inherited body rebuilt from its own CHANGELOG entry, the record at a ceiling of 0 with one release kept deliberately, and three checks that reported success while doing nothing fixed. Carried here to keep the three at one version |
| **0.60.8** | **No change to this product** -- carried from PDI's round: a release checklist naming every version field, byte-identical in all three, and the deletion of `RELEASE_NOTES.md` after 412 of 530 releases proved to carry one frozen v0.24.0 body. A reader replaces the writer. Carried here to keep the three at one version |
| **0.60.7** | **No change to this product** — PDI's console round: a screen that imports the translator is not a translated screen. Two of its screens sat on the finished side of the ledger for twelve releases holding fifteen English strings; a guard now names that state on the round it happens. 91 → 32. Carried here to keep the three at one version |
| **0.60.6** | **No change to this product** — PDI's console round (Positions and Bridges, 154 → 168 → 91). Carried here to keep the three at one version. Its reader asked for a letter-space-letter and so could not see `Role &amp; industry`; this product's console reader records strings verbatim rather than counting phrases, so it has no such test to be wrong about — checked, not assumed |
| **0.60.5** | **No change to this product** — PDI's console round (225 → 154). Carried here to keep the three at one version. Its one portable lesson: two guards that greped their screens for English went red when the screens were localized, and now follow the key to the table instead |
| **0.60.4** | **The reader this product already had turned out to be the one that was right** — no change here. PDI's console was read by the regex shape this product abandoned rounds ago, and it was missing a quarter of the English. Two suites can carry the same guard by name and not by reach |
| **0.60.3** | **A check that cannot fail before the merge is not a check** — `ci.yml` carried the same blind trigger `native.yml` did, and had been red for 29 runs on four guards that shell out to the JSX-text extractor: the job running pytest installed no node dependencies, so they failed on the runner and passed everywhere else. Trigger fixed, dependencies installed, and a guard that reads the triggers themselves |
| **0.60.2** | **The compiler was in the room the whole time and nothing listened** — `native.yml` had been red for 123 runs on a trigger the release loop never reached. Fixed, and the shells then named real defects: an Android L10n table too large to compile at all, 944 lines of `ApiClient` living inside a record's body, two records whose mid-list default swallowed the last positional argument, and a dozen members that were never there |
| **0.60.1** | **A fix to the cascade fixes the next delete, not the last one** — every profile ended before 0.59.9 was ended by a list of 24 table names against a schema of 66, and the 42 tables it missed are still sitting in every deployment running since. `python -m qrme.orphans` is the reach-back: dry by default, `--apply` to clear, scope taken from the cascade's own reader. Its sharp property is not *does it find the orphans* but **does it leave a living profile alone** |
| **0.60.0** | **An export is measured against the schema too** — `GET /profiles/{id}/export` says *access everything, anytime (You Own It)*, the README's capability table points at it, and the suite gateway's GDPR Article 20 bundle is built on it. It returned **6 tables of 66**. Now derived from the schema like the erase cascade, with live credentials dropped **per column by rule** — the first cut was a list of column names and the new guard caught three it missed on its first run |
| **0.59.9** | **An erase is measured against the schema, not a list somebody wrote** — `DELETE /profiles/{id}` says *the profile and every trace of it*. It named 24 tables; the schema has **66** with a `profile_id` column, so 42 survived — `clinical_notes`, `media` and `media_watermarks`, `anonymous_pictures`, `homepages`, `friendships`, `inbox_events`. The cascade is derived from the schema now, and a guard plants a row in every scoped table, deletes, and looks |
| **0.59.8** | **The check that covered one client of four** — 0.59.7 asked whether the shape a screen declares is the shape its route answers with, and asked it of the console alone. The three shells decode the same answers into their own types, and a wrong one there throws the same way. Extended to all four clients (console 422 · iOS 300 · Android 316 · Windows 342); no disagreements, and the reach is now a record that cannot go down, because a reader that stops matching reports agreement |
| **0.59.7** | **`req<T>` is a cast, and a cast is a claim nothing checks** — a route answers with a shape and a screen declares one, and between them sits a TypeScript generic the compiler cannot verify against anything: the body arrives through `JSON.parse`, which is `any`. Next door two screens declared an array where the route answers an object and threw `.map is not a function` during render. This console agrees on all 422 typed calls; the guard is here so it stays that way |
| **0.59.6** | **The clients agreed with each other and were all wrong** — parity between clients is a relative check, and a relative check is satisfied by everybody being equally wrong. Next door a vault under customer custody required `x-tenant-key` on every record route and no client sent it, so pressing *hold our own key* locked all four clients out — including out of the button that undoes it. The new guard reads the requirement out of the **application's** dependency tree, then asks each client only about the routes it actually calls |
| **0.59.5** | **The third sink, where both the escaping and the policy miss** — inside a `<script>` the HTML parser ends the element at the first `</script`, whatever the JavaScript quoting says, so a value can close the page's own nonced script and everything after it is markup. This product's `_js` composed both escapers correctly; the siblings' were bare `json.dumps`. All three now share one primitive, and every value entering a script is checked to pass through it. The consoles were swept too and are clean — no `dangerouslySetInnerHTML`, `innerHTML`, `eval` — now a floor |
| **0.59.4** | **The sweep that found the last one, kept** — 0.59.3 found reflected XSS by walking every f-string that builds markup, by hand, once, and throwing the walk away. It is now a guard with a ratcheted record: **8 rows**, all pre-escaped composites the analysis cannot follow. It follows escaping through single assignments and helper returns (32 rows → 8 without it) and refuses to read `http://localhost:<port>` as a page. Put 0.59.3's defect back and it names the file, the line and the expression |
| **0.59.3** | **Reflected cross-site scripting on the sign-in callback** — `?error=<script>…` came back as live markup on a page served from this origin, and every HTML page a stranger reaches carried no `Content-Security-Policy`, no `nosniff`, no frame or referrer policy. Escaped at the interpolation, and `pagehead.py` now stamps a per-response nonce the policy names, so an injected tag has none and does not run. Verified in real Chromium: no CSP violations, the page still works |
| **0.59.2** | **A crash the browser threw away** — an unhandled 500 is rendered by Starlette *outside* every middleware the app adds, including CORS, so it went back with no `access-control-allow-origin` and the browser discarded it whole. Every crash reached its user as "Failed to fetch", indistinguishable from a backend that is not running. No in-process test could see it: a `TestClient` sends no `Origin` and applies no browser rule. Fixed with a catch-all inside the CORS layer, and guarded by a file that boots a real server |
| **0.59.1** | **Three suites, and nothing comparing what they ask** — every guard here exists in three copies and the copies drift silently. A sweep of test-function names found 370 carried by all three and 140 by exactly two. Four of those were one defect in PDI. The shared vocabulary and the divergences are now written down, byte-identical in all three repos, so each product checks its own half with no sibling checkout — plus the live three-way comparison when they are on disk |
| **0.59.0** | **A floor nobody raised** — two rounds found the same defect in two instruments, so this one swept every floor in the suite. 91 of them carried their own literal with no way to measure what they held, and every reachable one was decoration: l10n 10 against 945–961, path literals 40 against 1407, console call sites 200 against 429. `ratchets.py` is the convention — a floor plus the way to read the same quantity now — and the rest are held in a backlog that only shrinks |
| **0.58.9** | **Ten against nine hundred and forty-five** — the L10n guard's floor has not moved since it was written: ten localizer calls, twenty table rows, against tables that now hold 1087–1115 rows and screens that make 945–961 calls. Narrowing the call pattern to `L10n.t("…")` blinds C# alone — Windows 945 → 52 — and 294 tests pass while the one failure names four rows as a backlog complaint. Per-shell floors on both halves, plus a spread across the three ports that needs no hand-chosen number |
| **0.58.8** | **The route reader had one floor and four clients** — the console's extractor has been floored since it was the only client; the three shells had nothing. Blinding the iOS `request(` form drops it 430 → 11 call sites while `doorless` still reports zero, because the other clients cover for the blind one. Two floors now: an absolute one per client, and a spread across the three shells that needs no hand-chosen number |
| **0.58.7** | **A wire model is data, and data has no methods** — every pin now asserts on both ends and three checks audit the readers themselves. The first run of that audit found a missing brace, not a reader bug: `SpecialistRow` was never closed and the `extension ApiClient` after it never opened, so ninety-five client methods were declared on a two-field wire model. Brace balance passed, the member check passed, the pins passed |
| **0.58.6** | **The refusal surfaces** — the screens that render what the platform will *not* do, checked at both ends on all three shells: overlay kinds and refusals, the microphone vocabulary, the places a wearable may be lent, the contribution log. All correct, all pinned. The trap was the guard's own: PDI declares one-line structs, the property pattern required end-of-line, and a pin had been checking an empty model since the day it was written |
| **0.58.5** | **The disclosure that showed nobody** — the mic routes answer with `microphones_lent` and all three shells read `lent`, so the list of who in a room has lent the profiles an open microphone rendered as nobody on every client. Six more pinned rows, and the reader now follows a list built by appending — the limit 0.58.4 named and refused to guess past |
| **0.58.4** | **The key was right and the shape was wrong** — binding a decode site to its route is not derivable by reading this backend; four attempts are recorded and none shipped. What shipped instead pins a shell model to the function whose `return` is its contract, and the pinning found the guided tour blank on both phones: the outline read `key`/`title` off `{chapter, steps}`, and three buttons decoded `tutorial.where` as the step it wraps |
| **0.58.3** | **The key the server never sends** — a `Decodable` property name *is* the wire key, and a wrong one fails on a phone rather than on a build machine. Four live breaks: the overlay disclosure showing nobody on both phones, Sign in with Google and Apple unable to start on either, the helper's *where does this live* line half blank on Android, and the referral list reading a boolean where a timestamp is |
| **0.58.2** | **The colour that wasn't in the palette** — 0.58.1 checked the one receiver whose type is known for free; this checks all eight. The Android problem-report card painted itself with `Qrme.Card2` on a theme that declares `Card` and never a second, which Compose does not compile. The API clients came back clean across 1,613 call sites, and are asserted anyway |
| **0.58.1** | **The member that isn't there** — with no Swift, Kotlin or C# compiler here, the native UI is checked by reading; this takes the next class of compile error that reading can catch. Each shell has one object the screens read their session from and one file declaring it, so a member it does not declare is not a style question. Clean in this product; the sibling shells had thirty-nine call sites that do not compile |
| **0.58.0** | **The key the phones never carried** — auditing every header the console attaches to every request turned up one the shells do not send at all: `x-llm-api-key`, the person's own model key, pasted into the console since 0.4.3 and read by the backend per request. A key set on the desktop ran the desktop; the phone quietly ran the deployment's — same account, two credentials, nothing saying so. All three shells now hold one, offer a field for it under the console's own words, and send it |
| **0.57.9** | **A funnel only funnels what goes into it** — comparing the three test directories turned up a guard that existed in the other two products and not in this one, the product whose whole premise is speaking in a person's language. Porting it exposed what it could not ask: **21 of 22 Windows sends, 3 of 4 on iOS and 1 of 2 on Android built their own request beside the shared helper** and carried no `Accept-Language`, so every refusal they drew from an expired token arrived in English. One dispatcher per shell, and a check that walks dispatch sites rather than header lines |
| **0.57.8** | **The rows the guard skipped were the interesting ones** — the untranslated-literal check opened with `if "{" in english: continue`, so every row with a slot in it went unchecked for four releases. Those are most of what a screen says, and the sentence built around a value is the one a screen hand-builds. Twenty-seven sites: the whole provenance footer in English on the desktop and both phones, the watermark verdict, the objection status, the licence offer, the signing credential list. Slotted rows are compared by their fragments now; `native_dead_keys` 300 → 276 |
| **0.57.7** | **The files the release never touched** — fifty-five cuts bumped `pyproject.toml`, `api.py`, `package.json`, the README banner and the changelog, and not one of them touched the three files the phones report their own version from. `MARKETING_VERSION` and `versionName` said `0.1.0`; the `.csproj` declared no version at all, so every Windows build since the shell was written reported `1.0.0`. A `versionCode` of `1` would have had the first Play upload refused outright. The same files carry what each shell is allowed to do, so those are checked here too |
| **0.57.6** | **The half of the Windows shell that is not code** — 0.57.5 globbed `*.swift`, `*.kt` and `*.cs`, called that three shells and reported them parseable. The Windows shell's screens are XAML, and it never opened one. Two pages here carried `x:Name` twice on a single element, which no XML reader gets past; three more in JIM-mini. Four markup checks — well-formedness, one name per element, handlers that exist, controls the page declares — and the voice screen, read while fixing it, was printing seven sentences in English that its own table translates ten ways |
| **0.57.5** | **Nothing here builds the phones, so nothing here noticed when they stopped** — 0.57.4 shipped a Swift compile error because every guard reads these sources as text and none of them parse. A duplicate-declaration and brace-balance check for Swift, Kotlin and C#, narrow by design: it does not promise the shells build, only that they lack the mistake that got past everything else |
| **0.57.4** | **The inputs the shells never asked for** — 0.57.3 recorded six native-write defects as *needing an input the shell does not collect*; this collects them. A department beside the goal, a camera address, a locality and an include-remote switch, `price` where the shells said `amount`, and the signed-in actor on an accept. Six dead buttons across three shells, and the record is empty. Also fixes a Swift compile error 0.57.3 introduced |
| **0.57.3** | **The guard read one client and the finding came from four** — request bodies checked across the Windows, iOS and Android shells. Seven defects, each present in every client that makes the call, including a marketplace listing placement that has never worked on any native surface. Thirteen of the first twenty findings were the extractor's own, and a seventh defect surfaced only because PDI's Windows reader hit zero |
| **0.57.2** | **Every guard reads the answer; none read the question** — nothing had ever checked a *request* body against the model FastAPI validates with. QRME's 192 writes are correct; the guard's own first run produced 82 findings that were all its own defect, and a fifth was caught only by comparing how much of each client it reached |
| **0.57.1** | **The fourth client, and it was the only one wrong** — the console declares more than the three native clients combined and nothing had ever checked it. Four defects, all visible: the delegation screen could not delegate, a dashboard tile had never shown a number, suggested friends was always empty, and a list was declared a count. Windows, iOS and Android were right about all four |
| **0.57.0** | **Twelve routes out of forty-two, and twelve looked like all there were** — the Kotlin guard travelled to JIM-mini and PDI by requiring a `JSONObject(` wrapper those clients do not use, so it read a quarter of one file and passed. Constructor made optional, parse-helper and chained reads added: QRME 135→169 routes, JIM 12→44, PDI 13→18. Three of the new findings were the guard's own defects, caught before shipping |
| **0.56.9** | **The client that declares nothing was guessing hardest** — Kotlin has no structs to check, so nobody had; every `optString("k")` is a claim about a name *and* a type, and `org.json` never throws when either is wrong. Eight wrong reads, all already fixed in C#. Five faults in my own extractor found and fixed before any of them shipped |
| **0.56.8** | **Fixing a defect in one client was not fixing the defect** — the shape guard now reads Swift too, and found nine fictions in the iOS client that had all been fixed on the Windows side releases earlier. Its own extractor made the same swallow-the-next-struct mistake the C# one did, in a different language |
| **0.56.7** | **`kinds` meant three things, and one of them crashed the client** — `/wearables` sends it as a map where the record declared `string[]`, so that call threw rather than losing a field. `kinds`/`refused` split into six honest names (record 23 → 21), and the shape guard now checks that a declared type can decode what arrives — which found five more live crashes |
| **0.56.6** | **Eight watch faces that were not on the page** — reported from a phone. An HTML table is as wide as its longest row, so one `<tr>` with fifteen cells beside rows of three left twelve blank columns everywhere and clipped the rest off a phone. Every gallery is a uniform grid now — four across for screens and watch faces, two for desktop frames — with a guard that reads the widest row, not the first |
| **0.56.5** | **The guard travelled** — 0.56.4's shape guard ported to JIM-mini and PDI, and both siblings came out clean: only this client had been written from imagination. PDI's copy needed its own binding regex, because a pattern borrowed from here finds zero calls there and zero found reads like zero wrong |
| **0.56.4** | **A client record is a claim about a route** — `share`'s unexplained side turned out to be a Windows record declaring `name` and `share` on a route that has only ever sent `display_name` and `weight`; the button wired to it drew separators with nothing between them. Fourteen records were the same guess. New guard drives every GET binding and checks the claim. Collisions 24 → 23 |
| **0.56.3** | **The count and the state wore the same name** — `seen`, `available` and `revoked` were each a boolean *and* a tally of that boolean, and a decoder handed `1` where it wants `true` coerces rather than refusing. Counts renamed; a fourth row turned out to be a Windows decoder bug rather than a collision. Record 28 → 24 |
| **0.56.2** | **The compiler nobody ran** — `tsc` is in the suite in all three repos now, along with a guard that fails when one wire name carries two types. 28 collisions found here and recorded: `sources` is four types, `messages` and `watermark` three each |
| **0.56.1** | Cut together at one version; JIM-mini trains a real offline model from its own follow-up record, and PDI's HSM key path stopped being a seam |
| **0.56.0** | **The count of what was synthetic** — `attention.py` tells you how divided a profile's attention is; nothing told *you* how one-sided yours had been. Counts from your own logs, readable by you alone, with a door to JIM-mini above the line — and four tests holding it to a count rather than a diagnosis, a notification, a signal somebody else can read, or a transcript with a referral stapled to it |
| **0.55.0** | **The rule the record stated** — the field-label backlog's own header said *map one when a form starts asking a person for it*, and nothing was checking it; the blend screen had been asking for **share** and **their…** in ten languages while the refusal underneath said `weight` and `aspect`. Plus the guard that reads the screens, which failed first on an Arabic label written ten minutes earlier |
| **0.54.1** | **The twenty-four, read one at a time** — twelve were labels and are keys now, including a signature attestation pre-filled in English while its translation sat beside it; twelve are values a route matches on and stay English. Plus one badge that had two words across shells |
| **0.54.0** | **The shells that say less** — the iPhone had no camera-permission state, so a declined viewfinder showed a black screen instead of *nothing is recorded*; Windows printed "scan(s)" and "picked up" in English beside their own translations. Plus the guard that finds the rest — whose first version could not see the bug it was written for |
| **0.53.1** | **Nothing reaches the other platform** — the network is unplugged and a video is posted, the wall rendered and the feed loaded. The promise held; a `None` field and a sentence were all that had been guarding it |
| **0.53.0** | Cut together at one version; the round's work audits promises this repo ships in the same shape — a claim about an absence has to be falsified from outside the claim, and saying only what you refuse is how a true sentence misleads |
| **0.52.0** | Cut together at one version; the round's work is JIM-mini enforcing a promise that had been a caption — the same argument this repo settled for the feed, where the enforcement point is whoever holds the thing |
| **0.51.0** | **How many people it is talking to** — public, no token, on the accountless screen and all three phones: distinct people this week and altogether, with no ranking, no favourite and no names, greppable rather than promised |
| **0.50.0** | Cut together at one version; the round's work is JIM-mini's presence — and its door onto this platform hands over rooms, desks and profiles as offers, with no bell rung on anybody's behalf |
| **0.49.0** | **The stream** — one public card at a time: footage this deployment holds loops, anything on somebody else's platform stays a card until pressed, and every fourth card is a live room or a desk with a person behind it. JIM-mini's Feed tab is a GET-only door onto the same stream |
| **0.48.3** | Cut together at one version; the round's work is PDI's console — Custody and Continuity, 229 → 177 |
| **0.48.2** | The third axis measured at last — the three shells against each other — and it held **one** row here: *Sign out* was *Sair* on the phones and *Terminar sessão* on the desktop shell. A 0.48.1 record entry corrected: one of its two "shells disagree" rows was not one |
| **0.48.1** | **Two tables, one product** — 223 English strings live in both the console table and the iPhone's and 102 had no wording the two agreed on; the desktop says *Sie* (204 rows) where the phone says *du* (60); the voiceprint, desk and chrome surfaces reconciled, 102 → 8 |
| **0.48.0** | **The same sentence, translated twice** — 54 English strings under 2+ keys on iOS and 43 of them already drifted; 34 sets reconciled, 42 recorded as questions about the English; two tab-bar entries that read alike in three languages; and a `\u0027` that stops `L10n.swift` compiling |
| **0.47.9** | **The number was mislabelled, and it was hiding a consent screen** — 263 of the 335 "dead" rows are asked for by a different shell, so they are screens saying less rather than waste; the voiceprint consent block's three sentences were hardcoded English on the iPhone, in an array a loop reads |
| **0.47.8** | Cut together with the other two at one version; the round's work is PDI's Transfers screen |
| **0.47.7** | **The other two syntaxes** — 0.47.6 derived the label rule for Kotlin and left Swift at eight hard-coded constructs and XAML at four attributes; the Windows code-behind sets half its labels by assignment, which `Text="` cannot match, so 91 call sites across nine shells were invisible |
| **0.47.6** | **Every button on the Android shell was English** — Compose has no `Button(text)`, so the untranslated rule's `Text(` pattern read none of them; the rule now derives label-bearing functions and their argument positions from the shell, 91 call sites wired, and this round's 366-row prune withdrawn because 59 of its deletions were rows the shell should ask for (540 → 350) |
| **0.47.5** | **Three screens titled with their own key names** — the dead-key guard ported from JIM-mini found `tab.compose`, `tab.posts` and `tab.robots` missing from the Android table, so those headings rendered the key; plus 540 dead rows recorded and ratcheted |
| **0.47.4** | Version alignment — the round's work was JIM's Overview and the tab strips whose English lived in an enum's `case` clause (229 → 150) |
| **0.47.3** | A guard on the route audit itself — every path literal must sit inside a call shape it knows, or be recorded as not a request; found two Android calls here written one statement away from the call site |
| **0.47.2** | The PaneFooter sign-out bug found and fixed here at 0.46.9 was never carried to the sibling — it is now, along with JIM's Family and Connect screens (386 → 229) |
| **0.47.1** | The ternary blind spot was in all three products — widening ported to JIM and PDI, which were understating by 40 and 12 |
| **0.47.0** | **The ternary hid the sentence, and then the floor** — a string chosen by a condition was invisible to the native-shell measurement, hiding the signing screen's *"Verifies"*, the voice-enrolment gate and the desk's *"Ring the bell"* on all three shells; the count corrected 68 → 125 and then run to 7, none of which is English |
| **0.46.9** | **Six screens on three shells, and the button that ends the session** — Overview, Compose, Posts, Connect, Robots and Study localized everywhere (212 → 68); Windows' Sign out sat in the pane footer where the nav localizer never walked, so it read *"Sign out"* in all ten languages while the row it needed sat unused in two other tables |
| **0.46.8** | **The reach console, and a crisis number that only works in one country** — Manage/Reach localized on iOS, Android and Windows including its own sub-tabs (368 → 212); the wellbeing card's *"call or text 988"* replaced with local crisis line or emergency services, in all ten languages |
| **0.46.7** | **Signatures and Voice, and a gap on one shell** — both screens localized on iOS, Android and Windows (470 → 368); two cards localized on two shells last release and missed on Android are finished, at the cost of no new rows at all |
| **0.46.6** | **The rest of Settings, and Community** — steering, relationship, feedback and the failure-report consent notice, plus the stranger and room screens, on all three shells (590 → 470); three relationship pickers stop rendering `romantic_partner` as a word |
| **0.46.5** | **The first screen, on all three phones** — Welcome and Settings localized on iOS, Android and Windows (703 → 590); the first-run screen reads the device's language because no profile exists yet to hold one; the Android shell did not compile and now does |
| **0.46.4** | **The refusal names a field the form never named** — the signature box on Referrals had a placeholder and no label; the label is added, ported into the field table, and the record drops 124 → 123 (PDI's 91 → 51) |
| **0.46.3** | **The console record reaches its floor** — Simulate, Memory and Friends localized; console-untranslated 25 → 1 after twenty-one releases, the last row kept on purpose because `AI ·` is quoted rather than written |
| **0.46.2** | **The front page, the price list, and who is in a life** — Home, Plans, Relationships and Discover localized (console-untranslated 69 → 25); the relationship dropdowns were posting their visible label to the API, and now post the enum |
| **0.46.1** | **The room, the conversation, and the door to both** — Rooms, Chat and Inside localized (console-untranslated 116 → 69); the dead-key guard learns that a key can live in a table, and a new check catches an English word left inside a Japanese or Chinese sentence |
| **0.46.0** | **The wall, the guide, and the blend** — Wall, Guide and Blend localized; console-untranslated 180 → 116, with no rows kept back |
| **0.45.9** | **The thing named, what leaves, and the mark it carries** — Named, Leaving and TheMark localized (console-untranslated 254 → 180); one row kept on purpose, because `AI ·` is quoted rather than written |
| **0.45.8** | **The money, the loan, and the firm** — Campaigns, Grants and Org fully localized (console-untranslated 338 → 254); the table's ten-language check widened from the sidebar to all 1519 rows |
| **0.45.7** | **The ledger, the name, and the stranger** — Audience, InWords and Stranger fully localized; console-untranslated 425 → 338 |
| **0.45.6** | **The lobby, the screen in the corridor, and a voice** — Lobby, Presence and Voice fully localized; console-untranslated 516 → 425 |
| **0.45.5** | **The objection, the camera, and the market** — Contest, Live and Market fully localized; console-untranslated 616 → 516; the dead-key guard learns to name its own blind spot |
| **0.45.4** | **Two directions, one picture** — WatchParty, Delegate and Beacons fully localized; console-untranslated 724 → 616 |
| **0.45.3** | **Three more, and the wrist among them** — Passing, Signing and Placements fully localized; console-untranslated 848 → 724 |
| **0.45.2** | **The three biggest screens left** — Exchanges, Reaching and Visiting fully localized; console-untranslated 978 → 848 |
| **0.45.1** | Version alignment with JIM's console-to-zero round |
| **0.45.0** | **Under a thousand** — the Workshop and Bodies screens fully localized; the console-untranslated record crosses into three figures (1072 → 978) |
| **0.44.9** | **Who this profile is, in every language** — the Identity screen fully localized (console-untranslated 1121 → 1072) |
| **0.44.8** | **The tail of the audit speaks** — the Remainder screen fully localized (console-untranslated 1172 → 1121) |
| **0.44.7** | **The handover speaks** — the Referrals screen fully localized (console-untranslated 1225 → 1172) |
| **0.44.6** | **The counter in the street speaks** — the Desk screen fully localized (console-untranslated 1281 → 1225) |
| **0.44.5** | **The counter speaks** — the Selling screen fully localized (console-untranslated 1337 → 1281) |
| **0.44.4** | **The Control Center speaks** — the Settings screen fully localized (console-untranslated 1403 → 1337) |
| **0.44.3** | **The backlogs shrink from both ends** — the Assist screen fully localized (console-untranslated 1459 → 1403) and the field-label evidence pass maps seven newly-typed fields (residue 131 → 124) |
| **0.44.2** | **The last doors** — genesis and hybrids, packs, simulations and fine-tuning, the contribution ledger, proactive reach and quiet hours, licensing, and the senses reach all three shells; **the doorless records run to zero** (ios 0 / android 0 / windows 0) |
| **0.44.1** | **The sticker, the queue and the stamp** — beacons/QR and pairing, the moderation queue with message edit/retract, reviews, watermark resolution and tamper-check, media upload and wearables reach all three shells; **71 doorless rows struck**, records fall to ios 21 / android 26 / windows 24 |
| **0.44.0** | **The keys, the till and the lifeline** — accounts (signup, sign-in, verification, reset, OAuth), money (plans, subscriptions, orders, proceeds, campaigns) and status+help reach all three shells; **72 doorless rows struck**, records fall to ios 45 / android 49 / windows 48 |
| **0.43.9** | **The face it shows the world** — the portrait, the emblem and badge, the page and themes, the front, the surfaces, the blend, the bodies, the dials and the wrist reach all three shells; **72 doorless rows struck**, records fall to ios 69 / android 73 / windows 72 |
| **0.43.8** | Version alignment with JIM's watch-picker round (device picker, Fitbit seed, Bluetooth pairing) |
| **0.43.7** | **The record, the veil and the exit** — the memory list, the pair's record, source material, the ledger (transparency/export/stats/feed), anonymity, verification and the three ways a profile ends reach all three shells; **75 doorless rows struck**, records fall to ios 93 / android 97 / windows 96 |
| **0.43.6** | **The workshop in the pocket** — workflows and their pauses, the delegation envelope, the assistant's verbs, tasks under a revocable grant, rated placements and specialists reach all three shells; **84 doorless rows struck**, records fall to ios 118 / android 122 / windows 121 |
| **0.43.5** | **The seal, the mail and the screen** — signatures and verification, mail settings, rooms and the microphone disclosure, wall screens, memberships, consented handoffs and campaigns reach all three shells; **74 doorless rows struck**, records fall to ios 146 / android 150 / windows 149 |
| **0.43.4** | **The body, the case and the lobby** — robot audit trails and dials, the medical referral flow, objections, the game lobby's honest roster and the helper dock reach all three shells; **75 doorless rows struck**, records fall to ios 171 / android 175 / windows 173 |
| **0.43.3** | **The place, the camera, the organization and the tour** — whose-corner, microphone and overlay disclosures, the camera with its refusals, organizations and the guided tour reach all three shells; **81 doorless rows struck**, records fall to ios 196 / android 200 / windows 198 |
| **0.43.2** | **The crowd, the couch and the loan** — the audience verbs (like, share, subscribe, gift), the watch party and skill grants reach all three shells; **84 doorless rows struck**, records fall to ios 223 / android 227 / windows 225 |
| **0.43.1** | **The platform tells you what happened** — an inbox of deeds done to you (message, comment, friendship, signature, a place on a stream), named but never quoted, on the console and all three shells |
| **0.43.0** | **The phone could be listed and could not do business** — 46 routes for staffing a desk, trading in the market and signing an exchange reached iOS, Android and Windows; **139 doorless rows struck**. Plus two guard-invisible image doors and a 204 that made every successful delete report failure |
| **0.42.9** | **The people around a profile reach the phones** — friends, suggestions, the wall and comments gained People screens on iOS, Android and Windows; 27 rows struck from the per-shell doorless records, with the pinned/blocked/ranked-on rules rendered rather than re-decided |
| **0.42.8** | **The record said nobody asks; the forms had started asking** — 107 of 251 recorded "no form asks for this" fields turned out to be bound to real console inputs; all now carry ten-language labels, leaving 144 rows that match the record's own rule; the agent-lights widget now shows an unlit retry dot when the backend is unreachable instead of silently vanishing |
| **0.42.7** | **The person decides who reaches them** — friends-only messages with per-profile feature switches that refuse by name, and a MySpace-style homepage sandbox (hex colors, http(s) links, plain text, actual friends) on all four clients |
| **0.42.6** | **Version alignment** — JIM gained booking/scheduling with bottom-rung reminders and self-only email; a shop service can now be booked as one act, order and appointment together |
| **0.42.5** | **A shop is not a desk** — standalone storefronts: one shop per profile, offerings with price/currency/availability, buyers are interactors, fulfilment (and only fulfilment) credits the ledger, both sides can let go. Eight routes with doors on all four clients in the same cut (console screen 187 + iOS/Android/Windows), and a test that a shopping day writes nothing into any desk table |
| **0.42.4** | **Version alignment** — JIM's money guardian gained its native doors; the finance desks QRME serves beside a warning are now reachable from the phones that show it |
| **0.42.3** | **The last thirteen unaudited screens** — across the three repos, thirteen components had sat `unaudited` since the manifests were seeded; the audit confirmed eight of them had never been drawn at all. QRME's two were both in that eight: screens **185 Discover** and **186 Wall** are the drawings, both `unaudited` ceilings fell to zero, and `undrawn=0` is finally true rather than covered for |
| **0.42.2** | **Version alignment** — JIM gained its money guardian; QRME's `GET /desks` now serves its warnings, listing real finance desks beside the tandem specialist |
| **0.42.1** | **The starters can answer for their own trade** — one Field Pack left five of eight prompt seats empty on every starter. `dossiers.py` now gives all 34 — Vivienne Sable included — what-I-know, skills-and-services and colleagues source items, 8+ skill chips, and a colleague graph installed as real friendships, composed from the same list as the prose so chat and the API give one answer. 77 tests, both directions |
| **0.42.0** | **The desk can finally do the job** — every desk surface let a person reach the counter and none let the desk do the work it exists for. Service sessions and connections shipped: the desk offers (screen, machine, program, files), only the caller's accept mints the link token — returned to them alone — and either side ends it, the token dying in the row. Rated desks gate the accept behind the same adult wall as every other surface . A desk can also lend a *skill* — `app` joins the lendable kinds (a connected program like Cursor, driven through the lender's own connector, every use logged), and a counter session is a grant surface that takes its skills with it when it closes |
| **0.41.0** | **The workflow round-trips and nothing walked the whole arc** — `workflows.py` names three properties a delegated multi-phase goal has to keep, each unit-tested on its own side of the wire; the one check that boots all three products drove a single exchange and stopped, never calling `start_workflow`, `advance` or `specialist_tasks` across the boundary. Driving it surfaced the Pro gate and the owner's opt-in as steps rather than surprises, and the arc now walks research → draft → send and pauses at `confirm` |
| **0.40.9** | **The README said v0.18.0** — the first bold line of every README named a release twenty-two cuts old, on the line directly above one promising the three products are versioned and cut together; the history table underneath stopped at 0.30.6, leaving seventeen shipped releases in the changelog and off the page anybody reads. Both are now checked against `pyproject.toml` and the changelog, and five of seven unaudited screens are resolved by reading each component's heading rather than its name |
| **0.40.8** | **The refusal named the field the API calls it** — An earlier round took the 422 from `[{"type":"missing",...}]` to one sentence a person can read, in their own language. |
| **0.40.7** | **The record that outlived the code** — `public_untranslated.txt` opened with a paragraph explaining that `Onboarding.tsx` — the screen every person in the world meets first — carried forty-odd English strings, that translating them was "its own round", and that a half-translated sign-up form would be worse than an English one. |
| **0.40.6** | **The stranger's language, finished** — Two rounds ago every shell learned to work out what language its reader speaks without a profile — `Locale.preferredLanguages`, the system locale list, `CurrentUICulture` — and the round stopped there, on purpose: twenty-odd sentences on ea |
| **0.40.5** | **The door they closed was the owner's** — Deletion in this product retires the owner's token. |
| **0.40.4** | **A memorial that kept posting** — `POST /profiles/{id}/chat` has refused a departed profile for releases: `POST /profiles/{id}/compose` — which writes a public post in that profile's voice and publishes it where anyone can read it — had no such check. |
| **0.40.3** | **The provenance named the model that was asked, not the one that answered** — `content_provenance` is this product's central claim, and its own docstring says so: *the verifiable basis of a piece of persona-generated content: which model produced it ... |
| **0.40.2** | **The refusals, finished** — 0.24.0 translated the eleven refusals any route can raise and **wrote the rest down**. |
| **0.40.1** | **The objector could end a profile and could not read their own case** — `GET /objections/{id}/audit` is owner- or reviewer-gated, and its docstring gives the reason in its own words: *it can quote the objector's reason*. |
| **0.40.0** | **A rule reversed, and said so rather than changed quietly** — `test_the_nav_is_translated_and_nothing_behind_it_is.py` records how many English strings sit behind this console's forty-six translated sidebar labels. |
| **0.30.9** | **Two corrections carried in from the sibling's round** — **A type-compatible argument swap, guarded.** JIM's Android client declares its shared helper `request(path, method, body, token)`, and three calls in that shell — plus one in PDI's — passed the verb first. |
| **0.30.8** | **The console guard, asked of the phones** — `test_the_nav_is_translated_and_nothing_behind_it_is.py` has been in this repo since the console rounds. |
| **0.30.7** | **A guard ported before this repo needed it** — `test_a_screen_nothing_opens.py` holds every screen a shell declares to being reachable from somewhere in that shell, and every call to that shell's localizer to the number of arguments the localizer actually declares. |
| **0.29.0** | **The deploy that lived in a chat log** — `docs/cloudgw-deploy.md` — the gateway from a bare host to installers that actually report, with the two build-time variables that are the point of the exercise. |
| **0.28.0** | **0.28.0** — Aligned with JIM-mini 0.28.0. The three products carry one version, so a release that only moves in one of them still moves in all three. |
| **0.27.0** | **The screen everybody meets first** — `public_untranslated.txt` recorded thirty-seven English strings on the pre-session surface, thirty-six of them on `Onboarding.tsx` — the screen every single person meets before any account exists anywhere. |
| **0.26.0** | **Three copies of one guard, three different blind spots** — `clientpaths.py` says of itself, in its own docstring, that it is *byte- identical in qrme, jim-mini and pdi*. |
| **0.25.0** | **A relying party id is a domain, and `127.0.0.1` is not one** — Two outstanding console tasks — Google/Apple credentials and the Windows Hello field test — written down field by field. |
| **0.30.6** | **The plan gate speaks the reader's language** — the one refusal the record refused to half-do for four releases, because translating its frame around English prose slots would have produced a sentence half in each language at the moment somebody decides whether to pay. The capability descriptions and the billing period are a closed set this product authors, so they translate; the plan titles deliberately do not, because `Pro` is what the product is called on the receipt. The console had the same defect one layer out — an English card repeating, in English, what the message had just started saying in Portuguese |
| **0.30.5** | **The plan gate said HTTP 402** — `detail` is a string for most refusals, a dict for the plan gate and a list for a 422, and only the list had been given a top-level `message`. The three shells look for that key and then for a string `detail`; a dict is neither, so the one refusal standing between somebody and a decision to pay rendered as a bare status code — no price, no plan name. Android's was a regression from the previous release. Every refusal now carries the sentence in one place whatever shape the structure has, and the structure still rides along for the console's upgrade card |
| **0.30.4** | **A refusal whose English is not a constant** — 49 f-string refusals had been named as uncovered for three releases, because a sentence built by interpolation has no English source to key on at the moment it is raised. `i18n.Templated` carries the template and its slots beside the finished English text; 18 converted. The slot is the whole design: whitespace means prose, and a prose slot keeps the entire refusal English rather than producing a sentence half in each language. Two of my own checks asked the wrong question — a character allowlist that quietly meant ASCII and rejected every Hindi word, and a token test that failed on correct two-word translations |
| **0.30.3** | **The refusal that arrived as a list** — a 422's `detail` is pydantic's rows, not a string, and all four client families rendered it by a path written for one: two printed the raw JSON under the form, two threw it away for `HTTP 422`. The sentence translated last release was correct, arrived, and was read by nobody. The console had already solved this shape for the plan gate's *object* refusal, and a list walked straight past that fix. The server composes the sentence now; the guard took three attempts, and the first two passed on code that was fully broken |
| **0.30.2** | **The synthetic self enters the tandem contract** — QRME has always had `kind: "self"`, a profile that speaks *as* a person, and the sibling guardian had no column, module or route that knew it existed. The boundary is now written down before the code that obeys it, byte-identical in three repositories: an owner token, `kind == "self"` or refused, an enumerated allowlist empty by default, and medication named as the one category made of the person's own words — because a drug name they typed can be a diagnosis |
| **0.30.1** | **The refusal that handed the body back** — a 422 is the refusal a person meets most often and it went out past the handler that localizes everything else, carrying pydantic's `input` key: on a missing field, the entire submitted body handed straight back, in a product whose whole error design exists so that content never travels. Closed in all three, with a canary posted at every body-taking route rather than a check for the key's name — it named 124 of them before the fix |
| **0.30.0** | **Forty-six translated labels, forty-six English screens** — the console's sidebar answers in ten languages and every one of the forty-six screens behind it is English, 1576 strings of it, now measured and ratcheted; the two language records must together cover `screens/` exactly, so a new screen cannot land outside a count. And the persona spoke the owner's language everywhere while the platform refused them in English on all 153 of its refusals — with the reason written into a docstring, that *the owner picked that language*, when the owner had picked Portuguese and it was in the database the whole time |
| **0.24.0** | **The doors opened; the answers were still in English** — the accountless screen was in ten languages and every sentence the server contributed to it was in one, including the answer to the only question a visitor came with. The public routes now read the header. The guard that watched that screen could see five of its twenty-five English strings, because a regex over TSX skips any sentence wrapping a value; TypeScript's own parser reads them now. It also measured one of the two screens a person meets before signing up. Three native shells gained a way to ask what language their reader speaks |
| **0.23.0** | **The doors nobody could open** — the objector, the person asking whether what they were sent is genuine, and the person checking they met the same profile twice all had public routes and no way in. A *Without an account* surface on all four clients, before the sign-in gate, with `#object` deep links so a takedown notice can point at the form. The visitor's language now comes from their browser rather than a profile they do not have. iOS can revoke a signing credential it enrolled |
| **0.22.0** | **The only post that actually leaves was the one going out unmarked** — `publish` stored a profile's words on a platform QRME does not run with no credential and the profile's own filter, where the in-app path stamped every post and forced the strict one. Both now match. The door audit reaches zero, a handle could be taken from the profile answering to it, a post the filter refused was served by the route listing what was published, and an id was being read as a credential in the one feature built on consent |
| **0.21.0** | **Four door-audit rounds, and three defects behind the doors they built** — a missing field reported as a broken signature, a licensing policy you could publish and nobody could take up, a room that asked for nothing but its own id, the body market and what bolts onto a body, and native shells that learned to send a credential |
| **0.20.1** | **A sale credited to a key nothing reads** — the marketplace statement reads by account id and the sale was written against a profile id, found by the round that built a guard naming every `api.ts` binding no screen calls. And the union hid a surface: *some* client reaching a route was being counted as *this* client reaching it |
| **0.20.0** | **The doorless backlog reaches zero** — 116 routes the backend served that no client could reach, closed. The audit could not see two kinds of request until this release, so part of that number was never really there; what was left is recorded rather than quietly corrected |
| **0.19.1** | **The error card gets a face** — 0.19.0 shipped its own reporting card and first-run notice with no screen, no lesson and nothing for the helper to point at, while the release notes described the feature at length. Drawn, taught, findable, and a guard that fails the next time a surface ships with none of them |
| **0.19.0** | **It can tell you it broke without telling anybody what you said** — content-free error capture in all three consoles and on every native shell, sent to a collector that never receives a word of your content |
| **0.18.0** | **Parity, and the drawings to prove it** — voice, provenance lookup and the role picker reach iOS/Android/Windows, and every one of them is finally drawn, taught and findable |
| **0.17.0** | **Voice reaches the microphone, and the Wall's buttons work again** — voice enrollment on iOS/Android/Windows, three features given doors, the recoverable watermark, and a 404 fixed under every like, comment and share |
| **0.16.0** | **Your own pixels, two new front doors, two new model doors** — wall uploads and pasted-link players, Google/Apple sign-in, DeepSeek and your own algorithm, and the role rides the turn |
| **0.15.0** | **The temperament dials** — mood, outlook, maturity, agreeableness, confidence, curiosity join the steering catalog |
| **0.14.5** | **Cut with the siblings** — JIM's fall path, native crash watch, and docs web |
| **0.14.4** | **The console names a version mismatch** — plus faces on the discovery cards (AI / real-photo badges), plain room labels, Blend explained, Erase all, and the settings that say which secret is which |
| **0.14.3** | **The lights are always on** — a watch-sized, minimizable agent-lights window in the studio |
| **0.14.2** | **The vault posture survives suite mode** — the gateway wires QRME's PDI tandem (`suite:qrme-vault`), owner-scoped operations provenance (`POST /suite/operations`), and the launcher shows the joints |
| **0.14.1** | **The suite wires its own tandem** — in-process tandem bridging and the one-call ecosystem bootstrap (`POST /suite/ecosystem`) |
| **0.14.0** | **The front page and the wrist** — Home names the new doors; watch faces 10-11 glance proceeds and coordination, counts only |
| **0.13.1** | **Demo, docs and hardening** — the one-press demo org, the tandem contract and disclosures caught up, and caps on the new surface |
| **0.13.0** | **The ecosystem round** — crowdfunding with proceeds routed by the user (screen 145, Campaigns tab), organizations whose department agents coordinate on one goal (screen 146, Org tab), and a console chrome that follows the profile's language |
| **0.12.0** | **The specification, mined** — hybrid profiles blended from several people, real-time simulation with confidence earned from evidence, and replies that adapt to where you are; Blend and What If tabs plus the 📍 toggle in Chat |
| **0.11.1** | **Cut with the siblings** — no functional change; PDI's desktop app finally carries its own vault |
| **0.11.0** | **The console catches up with its backend** — Discover (marketplace + one-press starter collection), Friends (founder pinned first, visibly), Rooms (2D/AR/VR + live desks), a memory vault that names names and erases one conversation at a time, and a chat fallback that stopped performing a character |
| **0.10.0** | **A real offline model** — install Ollama, pull deepseek-r1:1.5b, and QRME finds it on its own: a Local tile, no key, nothing leaves the machine |
| **0.9.1** | **Cut with the siblings** — no functional change |
| **0.9.0** | **Cut with the siblings** — no functional change; in JIM-mini the medicine cabinet arrived |
| **0.8.0** | **Continuity, joined up** — cut with the siblings: JIM-mini's silence vigil and PDI's bequests now attest QRME's existing succession/memorial flow with one shared reference |
| **0.7.0** | **The last version anyone fetches by hand** — the desktop app checks GitHub Releases on launch; Windows/Linux download the update and offer one restart, macOS is shown the download |
| **0.6.1** | **Model honesty in Settings** — an amber notice when replies would come from the built-in offline helper (or a keyless pick), instead of silence under a screen of logos |
| **0.6.0** | **Cut with the siblings** — no functional change; in JIM-mini the Apple Watch found its way in (Shortcuts drip + Health-export baseline seed) |
| **0.5.0** | **The round where the model switchboard got a face.** Claude, ChatGPT, Grok, Perplexity, Gemini and the offline stub as tiles you click in the Control Center, each saying whether it is configured here — the per-profile choice has been in the API since 0.4.3 and nowhere in the app |
| **0.4.8** | **The round where the app can actually send email.** Point it at a mail server from Settings — host, username, app password, link address — see which source is in force, and send a real test message that reports what the server said. Configuring one turns local signup back into genuine email verification, clickable link and all; without one, the app says so plainly instead of waiting on a letter it cannot post |
| **0.4.7** | **The round where an upgrade actually replaced the old app.** A leftover backend from an earlier install held the port and served its old API to every new console — so three upgrades in a row met the first version's signup. `/health` reports the version, the shell adopts a backend only when it is its own (else it takes a free port and tells the window), and quitting kills the whole process tree |
| **0.4.6** | **The round where old data stopped resurrecting the email screen.** A pending half-account from an older build is finished on the spot when signup retries on a no-mail deployment — under the newly-typed password, verified accounts never overwritten, SMTP deployments unchanged |
| **0.4.5** | **The round where verification matched the deployment.** A desktop install has no mail service, so signup activates directly — no screen waiting for an email that cannot come; a deployment with SMTP enforces the real proof, its email now leads with a clickable verify link (code as fallback), and the app continues on its own after the click. A crashed signup no longer strands the retry, and the packaged app can open its own backend log |
| **0.4.4** | **The round where the Windows signup 500 died.** The emailed-code banner used characters the frozen Windows backend's console encoding cannot print, so every signup crashed mid-request; ASCII banner, replace-don't-raise stdout, a cp1252 guard test, and console errors that show the server's words instead of a JSON-parse exception |
| **0.4.3** | **The round where the app got a front door and a key of your own.** Email + password accounts with the address proven by a 6-digit emailed code before sign-in works — the account owns the profiles, resets revoke every session, and neither login nor reset can be used to fish for who has an account. Bring-your-own model key: paste your credential in the Control Center and your requests run on it, never stored server-side, with the deployment's key as the lent fallback. And the installer finally runs itself: the whole Python backend ships frozen inside it and the app spawns it at launch — double-click-and-done |
| **0.4.2** | **The round where the installer you download actually gets you running.** A first-run bug report from a real Windows install drove all of it: the desktop installers stop being labelled 0.3.3 (and a widened guard now holds all five version strings together — pyproject had sat at 0.4.0 and the lockfile roots at 0.3.3, each a number nothing failed on), `python -m qrme serve` now answers the packaged console by default instead of dying cross-origin as *"Failed to fetch"*, the console's errors name the URL and the command instead of the raw fetch error, the age field stops pre-filling a birthdate, and the Anthropic provider defaults to `claude-opus-5` |
| **0.4.1** | **The round where free got honest, and the claims got checked.** A free plan that reaches everything Basic reaches — $20 buys privacy, not features — stored under **platform custody**: QRME holds it, you have access, no vault at any point, and every surface that names a plan says so. The vault gate now asks about the *plan* rather than the deployment (a free account's work was being sealed into a vault it could not hold a key to), a clinician's note about a real person joined the refusals, and channel 3 points your camera at a thing so somebody else can see it — never at a person for a synthetic profile. Plus the guards that keep the README's own arithmetic true |
| **0.4.0** | **The round where it got a price, and a guide that walks you to what you paid for.** Membership — Basic $20/month to make your own things, Pro $130/month for everything that leaves your account — enforced at **one chokepoint** rather than a check per route, on a table asserted against the served routes (the first version named three prefixes that were not routes at all: paywalls in front of a wall). A **pane in the corner** carrying the watch faces for people who own no watch, which shows and routes and never acts. And an assistant that answers *where is it* with a screen instead of a paragraph |
| **0.3.3** | **The round where an agent working on its own stopped being something you had to go and check.** One question — *does this need me right now?* — answered by three colours, on the wrist, in the app, and in a corner box that rides over whatever screen you are on |
| **0.3.2** | **The round where the starter collection stopped looking like a directory.** Each of the 34 is shown as the profile card the app actually gives it — rating, skills, memory/relationships/engagement, a career, a review, a Talk-to button — two columns wide so a phone stops clipping it. Plus the one starter that had no source material at all: the rated profile is grounded now, in theatre history rather than nothing |
| **0.3.1** | **The round where the starter profiles stopped answering from tone alone.** All 34 shipped with zero source material while the packs matching them sat unused in the marketplace; seeding now grounds each one in its own industry pack, as part of the **repair** path so deployments seeded earlier catch up by re-running. Plus this README, and a fix to the avatar bubbles' glow |
| **0.3.0** | **The round where the tandem reaches a person.** Owner-authorized **workflow delegation** — a specialist can be handed a multi-step task rather than a single chat turn, off until an owner enables it and refused outright if `research` is delegated without a source grant. A **medical referral signed for rather than consented to**: the release is authorised by a verified WebAuthn assertion on a device-bound credential (Face ID / Touch ID / Optic ID), the challenge *is* the hash of the exact package, and the link opens **once**. The clinician then **writes back once**, and the note reaches the profile attributed to them by name rather than absorbed as the profile's own knowledge |
| **0.2.2** | A documentation release — no code changed in any of the three products. Corrections to things that described themselves inaccurately, plus the release checklist that explains why those kept happening |
| **0.2.1** | A profile has a **front page** — screen 80, what a visitor actually lands on from a beacon scan. A help box on every screen. Real faces instead of the hologram placeholder throughout the screens |
| **0.2.0**–**0.1.9** | Marketplace search by words, by place, and by an assistant that only ever *suggests* — you run the search, and nothing reorders your results. Generated architecture diagram and README cover |
| **0.1.8** | Two ways into a live room, and they are deliberately not the same act. The live-desk video overlay. The starter collection visible rather than described |
| **0.1.7** | Gifts and marketplace purchases. The audience layer — like, comment, share, subscribe. A live desk left behind as a **printed QR code**. The point at which the three products began being cut as one release |
| **0.1.6** | The starter collection got faces, with the **AI mark burned into every shipped portrait**. Live desks. The native apps sign, and signatures survive being disputed |
| **0.1.5** | Published deployments, one-container deploy, the Cloud Model Gateway, and beacons that land on a page rather than on JSON. Native apps compiled in CI |
| **0.1.4**–**0.1.2** | `python -m qrme` launcher, running it on your phone, synthetic-media watermarking on every AI render, Terms of Service, macOS notarization |
| **0.1.1** | Native iOS / Android / Windows apps at full parity. First-run onboarding. LLM provider choice, robotic embodiment, steering, and the third-party objection & revocation flow |
| **0.1.0** | First public release — profiles & relationships, memory & moderation, lifecycle, summoning, marketplace & licensing, assistant & perception, cloud model |

**Money here is still simulated.** Subscriptions, gifts and purchases write real
rows on the creator's statement and settle through the same payout sweep as pack
sales and licence fees — but **no real funds move**, and every money-bearing
response says so in its own body. [docs/commerce.md](docs/commerce.md) lists
what is absent.

</details>

## Reference

Everything below is lookup material — how to run it, what to configure, what
the endpoints are. It is at the bottom on purpose: if you see a command in one
of the screens in [docs/gallery.md](docs/gallery.md) and want to know what it
does, this is where to find it.

### Architecture

- **API**: FastAPI (`qrme/api.py`), app factory `create_app()`.
- **Storage**: SQLite (`qrme/db.py`), path via `QRME_DB` (default `qrme.db`).
- **Persona conditioning**: `qrme/persona.py` builds the system prompt from
  profile identity + relationship + engagement + aging.
- **LLM**: official Anthropic SDK (`qrme/llm.py`); the default model is
  set by `QRME_MODEL`, with adaptive thinking. Without credentials (or with `QRME_LLM=stub`) a
  deterministic stub provider is used, so everything runs offline.
  **Bring your own key:** send `x-llm-api-key` on any request (the console's
  Control Center stores it device-side) and that request's generations run
  on your credential — never persisted, never logged; the deployment's env
  key (an operator lending theirs out) answers requests that bring none.
- **Marketplace expertise**: `qrme/packs.py` (knowledge packs + robot task
  packs, starter content, seeding) with routes in `qrme/routers/packs.py`;
  `qrme/seed.py` (starter profile collection); `qrme/robotics.py` (robot
  catalog, per-kind command allowlists) with routes in
  `qrme/routers/robots.py`.
- **Native clients**: three idiomatic codebases under [`native/`](native/)
  (SwiftUI, Jetpack Compose, WinUI 3) exercising the real API — see
  [native/README.md](native/README.md) for the screen-by-screen endpoint
  map.

### Run

```bash
pip install -e .[dev]
uvicorn qrme.api:app --reload
```

Set `ANTHROPIC_API_KEY` (or log in with `ant auth login`) for real model
replies; otherwise the stub provider answers. Override the model with
`QRME_MODEL`.

### Run it on your phone

The studio is a web app, so a phone on the same Wi-Fi runs it straight from
this backend — no app store, no second server, nothing to configure on the
phone.

```bash
python -m qrme          # the launcher menu: choose your device
python -m qrme phone    # straight to the phone flow
```

Bare `python -m qrme` prints the launcher menu — every way to run QRME,
one command each, so you pick per device: **phone** (this section),
**desktop** (`python -m qrme desktop`, the Electron app on this PC),
**packaged installer** (`.dmg`/`.exe`/`.AppImage` from the releases page —
no toolchain needed), or **headless API** (`python -m qrme serve`). Same
backend, same data, same token checks in every form.

The packaged installer is **double-click-and-done**: it ships the whole
Python backend as a frozen binary (`packaging/backend_entry.py`, built by
PyInstaller in the release workflow) and the app spawns it at launch when no
backend is already answering — no Python install, no terminal, data under
the app's own user-data directory, and the spawned backend dies with the
window. A backend you already run yourself is left alone.

`python -m qrme phone` builds the studio if it's missing (first run installs the
npm dependencies too), prints the phone URL **with a QR code right in the
terminal**, and starts the API on the network — scan, Add to Home Screen,
done. Flags: `--port`, `--rebuild`, `--no-build`, `--print-only`.

### Maintenance: rows the old profile delete left behind

Before 0.59.9 the profile delete ran off a list of twenty-four table names
against a schema of sixty-six. Every profile ended on a build older than that
release left forty-two tables standing — `clinical_notes` and the `media`
behind them, `media_watermarks`, `anonymous_pictures`, `homepages`,
`friendships`, `inbox_events` — and nothing in the running product will ever
look at them again, because the `profiles` row is gone and the API answers
404. Fixing the cascade fixed the next delete. It did not reach back.

```bash
python -m qrme.orphans            # count them, change nothing
python -m qrme.orphans --json     # the same survey, machine-readable
python -m qrme.orphans --apply    # clear them
```

**Dry by default.** The command a person runs to find out how bad it is is not
the command that changes it. A row counts as an orphan only when its
`profile_id` names a profile that is not in `profiles`; rows with a NULL or
empty subject are left alone. The scope is the delete cascade's own reader,
so this is that cascade applied retroactively rather than a second list to
keep in step.

A deployment first installed on 0.59.9 or later has nothing to sweep, and the
command says so in a sentence.


The manual equivalent, if you prefer the steps separately:

```bash
npm --prefix app install && npm --prefix app run build   # build the studio once
uvicorn qrme.api:app --host 0.0.0.0                      # listen on the network
curl localhost:8000/pair                                 # what to open on the phone
```

`GET /pair` answers with the studio's URL on your local network (and
`GET /pair/qr.svg` is the same URL as a QR code — the Control Center screen
shows both, so you can scan it off the laptop). Open that URL on the phone,
then **Add to Home Screen**: it installs as a standalone app with its own
icon, runs full-screen, and keeps working through a brief drop in
connectivity.

Why it needs no setup: the API serves the studio at `/app`, so the UI and
the API share one origin — the studio simply calls the address it was loaded
from. The phone layout follows: the sidebar becomes a thumb-reachable bottom
tab bar, inputs stay at 16px so iOS doesn't zoom, and the layout respects
the notch and home indicator.

#### Published deployments

The same code serves a laptop on Wi-Fi and an instance you host for yourself
and your colleagues to reach from anywhere:

<table>
<tr><th align="left"><sub>Variable</sub></th><th align="left"><sub>Effect</sub></th></tr>
<tr><td valign="top"><sub><code>QRME_PUBLIC_URL</code></sub></td><td valign="top"><sub><code>GET /pair</code> advertises this address (QR included) instead of a LAN one, so the phone flow works over the internet. Serve it over HTTPS — tokens travel in headers.</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_SIGNUP_KEY</code></sub></td><td valign="top"><sub>Profile creation requires this key as the <code>x-signup-key</code> header, so a published instance stays yours rather than open registration. Unset = open, the right default on a LAN.</sub></td></tr>
</table>

Talking to a profile stays public either way; the key gates creating an
account on your deployment, not using one.

The `Dockerfile` packages the studio and the API into one image so a hosted
instance serves both from the same origin, exactly like the phone flow does:

```bash
docker build -t qrme .
docker run -p 8000:8000 -v qrme-data:/data \
  -e QRME_PUBLIC_URL=https://qrme.example.com \
  -e QRME_SIGNUP_KEY="$(openssl rand -base64 24)" qrme
```

[docs/hosting.md](docs/hosting.md) covers the rest — TLS, what mounting
`/data` protects, and what running profiles for other people commits you to.

Without `QRME_PUBLIC_URL`, the address is local-network only and deliberately
not reachable from the internet — your profiles and their memories stay on
your own network.
Everything still requires the owner or interactor bearer token; a phone on
the LAN is exactly as authorized as a laptop on the LAN. If `/pair` reports
`reachable: false`, it could only find loopback (which on a phone means the
phone itself): set `QRME_LAN_HOST` to this machine's address and restart.

### Configuration

<table>
<tr><th align="left"><sub>Variable</sub></th><th align="left"><sub>Default</sub></th><th align="left"><sub>Purpose</sub></th></tr>
<tr><td valign="top"><sub><code>QRME_DB</code></sub></td><td valign="top"><sub><code>qrme.db</code></sub></td><td valign="top"><sub>SQLite database path</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_LLM</code></sub></td><td valign="top"><sub>auto</sub></td><td valign="top"><sub><code>stub</code> forces the offline deterministic provider; <code>anthropic</code> forces the SDK</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_OFFLINE</code></sub></td><td valign="top"><sub>off</sub></td><td valign="top"><sub><code>1</code>/<code>true</code> runs <b>fully offline</b>: local inference only (Anthropic SDK and cloud gateway bypassed even if configured), cloud never attached, embeddings/fine-tuning recomputed on-host. <code>GET /offline/status</code> reports the posture</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_MODEL</code></sub></td><td valign="top"><sub><code>claude-opus-5</code></sub></td><td valign="top"><sub>Model used for profile replies</sub></td></tr>
<tr><td valign="top"><sub><code>ANTHROPIC_API_KEY</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Enables real model replies</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_PDI_URL</code> / <code>QRME_PDI_TOKEN</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>PDI tandem: seal source material in the encrypted vault</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_CLOUD_URL</code> / <code>QRME_CLOUD_TOKEN</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Cloud Model Gateway: greater-model inference with local fallback + opt-in contribution (<a href="docs/cloud-model.md">docs/cloud-model.md</a>; standing one up: <a href="docs/cloudgw-deploy.md">docs/cloudgw-deploy.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_RP_ID</code></sub></td><td valign="top"><sub><code>qrme.app</code></sub></td><td valign="top"><sub>The WebAuthn relying party — <b>the deployment's own domain</b>. Passkeys are bound to it, so leaving the default on a real deployment makes every signature fail as "made for a different site". A relying party id must be a <b>domain</b>: on a loopback install set <code>localhost</code>, never an IP (<a href="docs/signatures.md">docs/signatures.md</a>, <a href="docs/windows-hello-field-test.md">docs/windows-hello-field-test.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_RP_ORIGINS</code></sub></td><td valign="top"><sub>any</sub></td><td valign="top"><sub>Comma-separated allowlist of origins a signing ceremony may come from. Unset accepts any origin the relying party matches</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_GOOGLE_CLIENT_ID</code> / <code>QRME_GOOGLE_CLIENT_SECRET</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Sign in with Google. Unset greys the button and shows why (<a href="docs/sign-in.md">docs/sign-in.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_APPLE_CLIENT_ID</code> / <code>QRME_APPLE_CLIENT_SECRET</code></sub></td><td valign="top"><sub>—</sub></td><td valign="top"><sub>Sign in with Apple. The secret is a <b>JWT you sign yourself and it expires within six months</b> — mint and check it with <code>scripts/mint_apple_secret.py</code> (<a href="docs/sign-in.md">docs/sign-in.md</a>)</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_CONSOLE_DIR</code></sub></td><td valign="top"><sub><code>app/dist</code></sub></td><td valign="top"><sub>Where the built studio is served from. Set it explicitly in a container — it resolves relative to the installed package otherwise, which is not where the build lands</sub></td></tr>
<tr><td valign="top"><sub><code>QRME_CORS_ORIGINS</code></sub></td><td valign="top"><sub>off</sub></td><td valign="top"><sub>Comma-separated allowlist for a front-end on another origin; <code>*</code> for any. Off is right when the studio and API share an origin</sub></td></tr>
</table>

### Test

```bash
pytest
```

### Example flow

```bash
# 1. Create a profile (owner is age-verified)
curl -s localhost:8000/profiles -H 'content-type: application/json' -d '{
  "owner_id": "owner-1", "kind": "self", "display_name": "Dana",
  "persona": "A retired teacher who loves gardening and dry humor.",
  "verification": {"birthdate": "1984-06-01"}}'

# 2. Register an interactor and set the relationship
curl -s localhost:8000/interactors -d '{"display_name": "Sam", "birthdate": "2000-01-15"}' -H 'content-type: application/json'
curl -s -X PUT localhost:8000/profiles/$PROFILE/relationships/$INTERACTOR \
  -H 'content-type: application/json' \
  -d '{"relationship_type": "grandchild", "nickname": "kiddo", "tone": "playful", "boundaries": ["finances"]}'

# 3. Chat — reply is persona-, relationship-, and engagement-conditioned,
#    and moderated before it is shown
curl -s localhost:8000/profiles/$PROFILE/chat -H 'content-type: application/json' \
  -d '{"interactor_id": "'$INTERACTOR'", "message": "Tell me about your garden!"}'
```

## License

Copyright © 2026 David Bianchi. Use requires prior written permission —
see [LICENSE](LICENSE).

---

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
