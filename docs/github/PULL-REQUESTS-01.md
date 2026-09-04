# qrme — pull requests

Every pull request opened against <https://github.com/davidsbianchi1984/qrme>, newest first, with the body as written. The body is the argument for the change; git keeps the diff but not the argument.

**351 pull requests, 348 merged.**

This is one part of a page GitHub is too long to render whole — see [PULL-REQUESTS.md](PULL-REQUESTS.md) for the rest.

**#351 to #241.**

## #351 — The face says what it is and what it does

- merged · opened 2026-09-04 · merged 2026-09-04
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/351>

> Screen 199 was the last one the camera could not reach. Reaching it turned up a defect underneath rather than a gap in the harness, and photographing the surface showed four more things wrong with it.
>
> ## The ear that could hear and said it could not
>
> The wave lives inside the talk overlay, which opens from the composer's microphone. Headless Chromium ships with no capture device, so the surface photographed as *"No microphone the browser can reach"* — true about the host and false about the product. Given Chromium's fake device it photographed the same way, because the recogniser fails there with `audio-capture`, and `audio-capture` was a dead end in all four of this console's ears.
>
> It should not have been. It is the recogniser reporting that **it** could not get audio, which is not the same fact as the browser being unable to. A handheld that hands its microphone to a call, and a desktop whose recogniser loses the device while `getUserMedia` still opens it, both landed on a sentence about a missing microphone over a microphone that was there.
>
> It joins `network`, `not-allowed` and `service-not-allowed` on the road to the recorded ear, in the chat overlay, the room, the orb and dictation — and stays self-correcting: where the device really is gone, the recording fails at `getUserMedia` and says so.
>
> ```
> asked     can the camera open the page
> mattered  can it open the page in the state it is for
> ```
>
> The camera gets that fake device in a browser of its own, because the device carries the fake device's **name** — Voice and Settings both list what audio is playing through, and both came back reading "Fake Default Audio Output". A device invented for one screen must not sign its name across the others.
>
> ## What the photograph then showed
>
> **The picture said the name twice.** `watermark.line` is `AI · <name>` and `.talk-name` prints the same name two lines below it — wrapped onto two lines in a 110-pixel frame, covering the chin to do it. The picture carries the designation; the name is said once.
>
> **The mark was cropped in half, and there were three of them.** The talk face, the room seat and the full-screen stage each had their own — a band across the bottom of a circle, a 7px tint, a grey pill — so one fact about one kind of profile looked like three different facts. All wear one `.ai-pill` now: dark, hairline, above everything the picture can do to it, and hung off the corner where a round frame used to eat it.
>
> The card's mark moved back onto the picture too, with the field report that moved it off **answered rather than overruled**: `text-size-adjust: none` refuses the phone font-boosting that once inflated it into the face, and what growth remains goes outward from a corner instead of across it.
>
> **The four panels beside the face could not be told apart.** Their tabs carried each panel's full title into a 60-pixel column, where the browser cut all four to their first eight characters — `Who the… / What th… / What yo… / How the…`, four labels sharing a first word. The tab gets a word — **Who, Memory, Us, Manner** — in ten languages; the sentence stays as the tooltip and as what a screen reader announces.
>
> **A name is not an introduction.** `industry` said which field somebody works in and nothing said which job, so a wall of thirty-four faces gave a reader nothing to choose on.
>
> ## The job, beside the field
>
> Profiles carry a `job_title` next to `industry`:
>
> - settable by their owner, like the field is
> - filled for the thirty-four starters out of the personas already written
> - taken from the seat's own title when a company hires somebody — so a hire reads *"Bookkeeper, Bianchi & Sons Bakery"* rather than a title with no house on it, and the founder reads *"Founder, QRME"* rather than leaving a reader asking founder of what
>
> `job_title` and not `position`: the friends list already puts a `position` on the wire and it is an ordinal. One name, one type.
>
> One `Trade` component draws both lines on the talk surface, the pool card, the circle card and the friends row. The room's seat has carried its own line since it was built.
>
> ## The guard that was worth stopping on
>
> The name search grew `industry` and `job_title`. The row-shape guard asks *did the row grow a key, or a fact* — so it was widened with the reasoning written into it rather than deleted. Neither is a new fact: `GET /profiles/{id}` is public and hands out both, and the browse pool beside the search already showed them. Without them the search was the one public list of people that showed a name and refused to say whose it was.
>
> ## Also
>
> The camera's own profile was seeded with an `interaction_scope` the product itself never writes, so `GET /profiles/{id}` answered 500 for the one profile every capture is taken as.
>
> ## Checks
>
> - **5726 passed, 3 skipped** — full suite
> - Camera: every screen reached, no failures; 62 captures changed and 199 is a photograph
> - Numbering audited across the three products — **211, 45 and 20**, unbroken from 1, every file shown somewhere, all three stated counts already true, nothing to close
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #350 — QRME Studios 3.0.5 — the voice door: the phone line JIM rings emergency contacts on

- merged · opened 2026-09-03 · merged 2026-09-03
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/350>

> ## What this is
>
> JIM-mini 3.0.8 rings its reach-out cascade through a phone line. The line's other half lives here, in the compose stack, the same shape as the camera and the ears.
>
> ## Changes
>
> - **`docker/voice/`** (new): a stateless sidecar that holds the phone house's credential, answers JIM's `GET /health`, `GET /standing` and `POST /calls` under the one shared secret, turns the house's webhooks into JIM's own call-id doors, and composes no prose of its own — every spoken sentence rides JIM's line envelope. Five houses behind one interface (`houses/`: Twilio, SignalWire, Telnyx, Plivo, Vonage), each verifying its own webhook signature and the per-call signature before a word is spoken, each mapping its terminal words onto JIM's six.
> - **`docker/beta-compose.yml`**: the `voice` service; JIM's `JIM_VOICE_URL` (compose literal), `JIM_VOICE_SECRET`, `JIM_TELEPHONY_PROVIDER`, and `JIM_LLM_TIMEOUT` with its load-bearing default.
> - **`docker/beta.Caddyfile`**: only the house-facing paths under `/voice` on jim-mini.com are published, named path by path so JIM's own spoken-voice doors keep their prefix.
> - **`docs/beta-deploy.md`**: the `.env` template rows for the line, what wiring one means in plain words, the two curls and the runbook that prove it.
> - **Release train**: 3.0.5 across every field and the three store manifests, CHANGELOG section, README row.
>
> ## Tests
>
> `tests/test_the_voice_door_speaks_to_the_phone_house.py` (153 tests): the JIM-facing doors and their bearer, the emergency refusal, the Twilio create-call shape, every house's signature verifier against vectors, the line machine end to end against a JIM stub, and restart amnesia. Full suite: 5691 passed.
>
> ## Pinned, not changed
>
> The 911 send stays held shut in JIM's source whatever is set here: the line rings people, never dispatchers, and refuses an emergency number at three locks.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #349 — The three roads out, and the video one renders every reply by itself

- merged · opened 2026-08-30 · merged 2026-08-30
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/349>

> Eight commits. The starter faces became photographs, two of them gained 3-D models, the import shelf opened on Avatar SDK, the avatars learned to breathe — and then a presence grew a third road out: the reply, rendered as video.
>
> ## The roads
>
> A presence takes one of three roads, and each surface falls down the list when the one above it is not there. A still photo. A speaking avatar. Or video.
>
> | | What fills the frame | Speed | What it costs |
> |---|---|---|---|
> | 1 · Profile photo | The still, carrying the AI mark in its own pixels | Instant | Nothing |
> | 2 · Avatar | The 3-D head, breathing, mouth on the voice | Live, every frame | Nothing, once the model exists |
> | 3 · Video generation | The reply rendered as footage | Minutes | Ten to fifteen cents a second |
>
> ## Nobody presses play
>
> On the video road every approved reply is rendered as it arrives. The turn starts the job and moves on — a render is minutes and a reply is not — so what the chat response carries is a row, and the screen polls it. The words stay readable the whole time the footage is being made.
>
> Three things make that safe to switch on.
>
> **The road is stored, not held on the screen that picks it.** It was component state, which was fine while the only thing it did was choose which block Identity drew. But `auto_render` runs on a turn nobody is looking at a console for, and a choice living in a component is one `/profiles/{id}/chat` cannot see.
>
> **A daily ceiling in seconds sits directly above the picker**, not on a settings page found after the bill. It counts renders already *started*, so two quick replies cannot both slip under a limit neither had spent.
>
> **A reply past the ceiling arrives as text saying so.** An owner who set a limit and then stopped seeing video is owed the reason — "you reached the limit you set" is a different sentence from "it broke". A failed render never fails the turn either: the reply already happened and the person is reading it.
>
> ## Length is derived, never dialled
>
> `filming.length_for` works out how long the passage takes to say and renders for exactly that. A dial would make the video fit the setting instead of the content — two sentences padded to thirty seconds, or a paragraph hurried into five. The console shows the number it arrived at and never offers to change it. Past the ceiling it says so rather than trimming: a video that quietly drops its last sentence is worse than one that was never made, because nobody watching it can tell.
>
> ## The direction stands
>
> "It's too dark, let's have this on the beach" is not a note about one video; it is where this profile lives from now on. `filming.amend` rewrites the standing direction from what the owner said rather than appending, so twenty corrections stay one readable paragraph instead of a transcript of complaints that contradict each other. Both the windowed and full-screen surfaces read and write the same row, so progress sticks by construction, and an append-only log keeps what was asked as well as where it ended up.
>
> ## A render outlives the page that started it
>
> `GET /video/latest/{profile_id}` is what a conversation asks on opening. The bubble tells somebody the render "keeps going without this page open, and appears here when you come back" — and nothing made that true: the scene arrived on the response and lived in component state, so closing the tab lost a job still being paid for.
>
> ## No vendor is load-bearing
>
> Seven services are named and none is depended on. Sora is absent on purpose: OpenAI deprecated it on 26 April 2026 and shuts the API down on 24 September. Ready Player Me closed on 31 January 2026 and is why `avatarforge.py` exists at all. Two shutdowns in fifteen months in the two markets this platform would most like to buy from, so a shelf that sends somebody to a service with a published end date is worse than a shelf one row shorter.
>
> ## Two corrections the full run found, both older than this change
>
> **Offline mode reached starting a render and not polling one.** The gate sat in `filming.render`, one level above the socket, so an offline host refused to *begin* a video and would happily go on asking the service whether one had finished. A poll carries a job id rather than somebody's words, but it still opens a connection to a machine that is by definition not this one, and "nothing leaves the host" has to be true of every way out or it is not a property of the code. Moved into `_ask`, the module's only way out.
>
> **Five refusals passed on `str(exc)`.** `str()` on a `Templated` returns a plain `str`, so a refusal built from a template arrived at the handler having forgotten how it was built — English, silently, indistinguishable from a sentence nobody has translated. All five use `i18n.raised` now.
>
> ## What is recorded rather than built
>
> Ten video routes are recorded as doorless on the iOS, Android and Windows shells. A shell that can *start* a render it cannot show, cap or cancel is the exact failure `unused_native_bindings.txt` exists to catch — the road is not one route but a picker, a ceiling, a prose direction, a poller that survives backgrounding, and a player. The ten come off together when a shell grows the last two.
>
> ## The screens
>
> Screen 209 is a photograph, not a drawing. Rather than filing `SceneFilm` under a Chat screen that does not show it, `tools/shoot_screens.py` seeds the road and the row the way the product writes them and photographs the real component polling the real route.
>
> The README also gains real output: two scenes this platform rendered, and an exchange shown as four compositions — the same two turns in a window and on a phone, with the green ring following whoever the turn belongs to.
>
> ## Checks
>
> - Full suite green over the final tree: **5270 passed, 3 skipped**
> - Console typechecks and builds
> - Doorless route backlog back to empty; surface census, gallery grid, tutorial coverage, ten-language string guards, refusal and field-label guards all green
> - 62 tests in `tests/test_the_video_door_is_open.py`, 9 in `tests/test_a_shipped_face_has_three_dimensions.py`
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #348 — The capability register: nine faculties, on one page, beside their permissions

- merged · opened 2026-08-30 · merged 2026-08-30
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/348>

> ## What this adds
>
> Nine faculties can be given to a profile. Every one of them already had a door
> — `console_doorless.txt` has stood at zero for many rounds — and not one of
> them had a place that named the set. Channel 3 lived inside Live Now, Channel 2
> inside a room, the look permit as a checkbox on Hands. Somebody wanting to
> answer *what can a profile actually do* had to already know where to look,
> which meant the only people who could answer it were the people who built it.
>
> ```
> asked     can each capability be reached
> mattered  can the whole set be read at once
> ```
>
> **Capabilities** (screen 208) carries four columns for each of the nine:
>
> | column | what it is |
> |---|---|
> | what it is | the function, in a sentence, in the reader's language |
> | where it stands | read live from the same route the owning screen reads |
> | what it rests on | the permission that had to exist first, named rather than implied |
> | where it is withdrawn | the screen that owns it, one press away |
>
> The third column is the reason the screen exists as code rather than as a
> document: a register that could disagree with the product would be a brochure.
> Nothing on it grants, opens, commands or revokes — it reads, and it routes.
> `README.md` carries the same four columns as a table, for a reader who never
> opens the app.
>
> A capability this console could not ask about renders as unread, never as off.
> The two are different facts and the register refuses to let them look the same.
>
> ## On the naming
>
> The nine are named for what they do, not for the body part they resemble.
> *Eyes* claims a faculty, where *a live view through the holder's own camera,
> opened by the holder, minuted, and disclosed to everybody present* states a
> behaviour that can be checked against the code and found true or false.
>
> ## Why these nine are not JIM-mini's nine
>
> The sibling product gained a register of the same shape in the same round, and
> it is deliberately not the same rows. This product lends a profile an ear and
> an eye *into a place* — Channel 2 and Channel 3, disclosed to the other people
> present — where JIM-mini attaches them to a monitor on one person. Copying the
> sibling's wording would have produced a register that described the wrong
> product accurately.
>
> The two rows that *are* verbatim siblings are screen observation and interface
> operation, because `hands.py` is itself a verbatim sibling: the motor that
> performs those moves is one program serving either stack.
>
> ## Registries and guards
>
> Three guards caught this mid-build and each was right:
>
> - `test_nav_labels_are_localised` — three Japanese strings still carried the
>   English word *body*; translated rather than quoted
> - `formal_register.txt` — a German sentence opened with third-person *Sie* and
>   pushed the informal-register count past its ceiling. Rewritten so the sentence
>   does not begin with it, rather than filed as an eleventh exception
> - `test_dock` — the new lesson had no phrasing in `help.DIRECTIONS`, so the
>   helper dock could not direct anybody to it
>
> Also updated: `tests/ui_screens.txt` (screen 208, status line recounted),
> `productmap.DOORS`, `tutorial.LESSONS`, and the gallery.
>
> ## Testing
>
> Full suite green over the final tree: **5189 passed, 3 skipped, 0 failed.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #347 — A body is a surface, and the cut is 2.7.0

- merged · opened 2026-08-29 · merged 2026-08-29
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/347>

> **asked** can a profile work a body the way it works a screen
> **mattered** which of the screen's bounds mean nothing on something that can move in a room
>
> `qrme/robotics.py` has carried a catalogue of bodies for several releases — platforms, kinds, a per-kind command allowlist, and a refusal to bind anything only *announced*. None of it was ever attached to a grant, a reach, a ledger or a refusal. The hands built all four for screens, and wiring the two together is a short afternoon and the wrong one to have.
>
> Four of the screen's bounds do not transfer, and the difference is that a mis-click is undone with a keystroke and an arm in the wrong place is not:
>
> | the screen's bound | on a body |
> |---|---|
> | `places` names software | has to name where the body may **be** — "anywhere in the house" is the `"*"` of the physical world |
> | a step budget | bounds how many things happen, and says nothing about how hard any one of them is |
> | the stop is a corner of the screen | a person standing beside a robot is not holding its mouse, and a button on a web page is not a stop |
> | `land` takes the far end's word | a body reporting that it moved because it *sent* a move is the request restated, not evidence |
>
> So `body` is a surface, watching through one is allowed — seeing and saying what is there carries none of the four — and `acting` is refused with all four named out loud. A person told "not supported" learns nothing; a person told what is missing can decide whether to supply it.
>
> Nothing here transmits anything to a physical machine, and that is the point: building the transmit path first and the envelope afterwards is how the envelope ends up shaped by whatever was easy to transmit.
>
> ## The number
>
> All three READMEs promise that one version names one tested combination of all three products, and three hands rounds cut here and nowhere else quietly ended that: 2.6.0 here, 2.3.1 in jim-mini and in the vault. Nothing failed, because nothing compares the three. So this is 2.7.0 and so are the other two, rather than each taking its own next number.
>
> ## Checks
>
> Full local suite over the final tree: **5163 passed, 3 skipped**. Five new tests in `tests/test_a_body_is_not_a_screen.py`.
>
> One failure in the first run was `test_the_console_typechecks`, caused by `three` missing from this container's `node_modules` rather than by any change here; after `npm install` it passes.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #346 — Carry the voice waiver to the three native shells

- merged · opened 2026-08-27 · merged 2026-08-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/346>

> ## What this carries
>
> The console has held the spoken-voice release/reclaim pair since the release ledger shipped; the three shell backlogs recorded the pair as a rights decision that ships first where its language lives. This round carries it over, as those rows promised:
>
> - **iOS, Android, Windows voice screens** each gain one toggle beside the binding — "Let everybody here use this voice" / "Take the voice back" — reading which way it faces from the binding's own `released` flag, in the console's ten languages.
> - **Three shell backlogs** (`tests/*_doorless.txt`) shrink by the pair of rows that promised it.
> - **Windows client** gains the `Delete(path, token)` request helper two earlier doors already called — the calls existed, the helper never did.
>
> Also under `[Unreleased]`: the open door (inverted connections) round from the prior push on this branch.
>
> ## Gates
>
> Full suite: 4911 passed, 2 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #345 — Every profile knows the application it lives in, and the conversation can leave it

- merged · opened 2026-08-24 · merged 2026-08-24
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/345>

> Six commits, covering both of this console's conversations — the agent and synthetic profiles — on the web, Android and iOS.
>
> ## The strip stopped knowing whose conversation it carries
>
>     asked     can the strip carry this conversation
>     mattered  does the strip have to know what kind it is
>
> The walk-along strip was written for one caller and held that caller's wire. Then the agent asked for the same button and answers through the authoring turn. `Walking` now carries `take(message)` and the screen that started the walk — the only thing that understands its own wire — hands that over.
>
> ## Every profile knows the application it lives in
>
> A synthetic profile knew everything about the person it represents and nothing about the place it stands in. Asked where to change what it is allowed to do, a mechanic answered like a mechanic who had never seen the app. The agent had the same gap: told its eleven tools and nothing else, it shrugged at a screen sitting in the navigation bar.
>
> `qrme/productmap.py` is this console door by door — all sixty-eight — joined to `tests/ui_screens.txt` so a screen added without a row fails the suite in the round that adds it.
>
> It goes into `persona.build_system_prompt` rather than into the routes, **so a profile created a second from now stands in the same building without anybody remembering**. A turn carries the consent doors always, the doors the message is about capped at six, and the names of everything else. The agent gets the same block under a sentence separating it from the roster: the roster is what it may *do*, the map is what the application *has*, and it cannot open these.
>
> Two things the block says about itself, in the prompt because that is the only place the model reads: naming a door is not permission to open one, and a mechanic who can point at the Permissions tab is still a mechanic.
>
> ## The conversation leaves the application
>
> **Web** — this PR originally said it couldn't. `away.ts` is right that a hidden page has its *recogniser* ended; it is not right about `getUserMedia`, where an open capture keeps recording while the window is minimised and the browser shows its own recording indicator. So the strip records where it can and posts the bytes to a new general ear, `POST /interactors/{id}/heard` — the room's door of the same name without a room around it, gated on the person's own token, because transcription costs the deployment something and a stranger's id is not a way to spend it. Being put away closes the recogniser and not the recorder, because the browser closes one and not the other.
>
> **Android** — a foreground service, declared `microphone` and not exported, with a notification that cannot be swiped away and whose first action ends the conversation. It carries the profile's **AI designation**: a notification glanced at from inside another app is the moment somebody has the least context and the last place to leave *is this a person* to a guess. The service learned the agent's wire too — told which kind it carries rather than handed a callback, with the agent's thread living in the service and going when it does. A row that cannot be taken back is spoken rather than done: a yes said into a phone in somebody's pocket is not the press that row asks for.
>
> **iOS** — `UIBackgroundModes: audio` and both usage strings, with the microphone one rewritten to describe the walking case rather than only voice enrollment.
>
> **Pressing walk lands on the front page**, so the app is navigable from there and one swipe from being left behind.
>
> **None of the native code has been compiled** — no Swift toolchain, and the proxy refuses `dl.google.com` so there is no Android SDK. The guards read the declarations, which is where the absence of an indicator would live.
>
> ## The walk says who answered it
>
> `generated_by` is who actually wrote a turn rather than who a profile is set to — the field exists because an owner whose key expired read stub-written text labelled with the model they had chosen. The console shows an amber banner; the strip had none, and the phone has no screen at all. Both now say *answered from what's stored here*. The agent's walk says nothing, deliberately: the authoring turn reports no provenance, and a `false` would be a claim nothing checked.
>
> ## A real defect, caught by the suite rather than by me
>
> `said` as a new parameter of `build_system_prompt` was **shadowed by a local list of the same name** inside it, so every room turn handed a list of seat descriptions to a selector expecting a sentence. The local is `seats` now. It surfaced as `'list' object has no attribute 'lower'` three frames down, so `selected` checks its own contract and says where the mistake actually is.
>
> Worth naming plainly: my earlier "green" claims for this repo came from **selective** runs, and the room tests were in none of the selections. A selection is not a suite. The result below is a full run.
>
> ## Testing
>
> Guards across four files, sabotage-tested throughout. Four sabotages slipped and were all the same shape — asserting a name appears rather than that the code uses it:
>
> - `test_every_synthetic_profile_carries_it` asserted the Desk tab's *name*, and every door's name is in the index on every turn;
> - the profile walk's guard asserted the bare word `degraded_from`, which the comment above it also contains;
> - the 503 check found the number in the docstring describing it;
> - and the iOS background mode passed by absence, because this repo's shell guard had no iOS checks at all.
>
> All fixed and re-sabotaged.

## #344 — Informal register, the chat ear, and two refusal guards that were measuring the wrong thing

- merged · opened 2026-08-24 · merged 2026-08-24
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/344>

> Four pieces, all in `[Unreleased]`.
>
> ## 1. The chat ear closed after one sentence
>
> Opening the talk overlay and pressing *speak* listened for about a second and dropped back to *tap to talk*. `SpeechRecognition.continuous` defaults to **false** — the engine stops itself the moment it decides one utterance has ended — and nothing reopened it.
>
> ```
> asked     did the microphone open
> mattered  is it still open when the person is still talking
> ```
>
> The ear now runs continuous with interim results, accumulates finalised phrases instead of replacing the box on every event, and reopens itself in `onend` while the listener is still wanted — Chrome ends a session on its own silence timeout even with `continuous` set, so the reopen is what actually keeps it listening. Button became a toggle; unmount closes the recognizer. The talk overlay also gained the composer's share menu (pictures, video, camera, documents), and the avatar box under the composer is gone.
>
> ## 2. German finishes the informal register
>
> **380 rows** across `app/src/l10n.ts` and the three native `L10n` tables, converted fragment by fragment so a partly-formal string could not be mangled by a global substitution.
>
> ```
> asked     is the string translated
> mattered  who does it think it is talking to
> ```
>
> What stays counted is third-person `Sie`/`Ihr`, not formal address — `Sie hängt am Brett` is the question, `Sie ist passwortgeschützt` is the briefcase — each named in `tests/formal_register.txt`. Floor 18 console, 4 Android/iOS, 6 Windows.
>
> Also: `chat.talk.stop` and `chat.talk.again` were read through `tr(cond ? "a" : "b", lang)`. The guard that finds translated keys nobody uses reported both, and it was right about what it could see — a static reader cannot follow a key assembled at runtime. One `tr(` per branch now.
>
> ## 3. A wiring precondition is not a refusal
>
> The refusal collector derives which exception classes to follow from the handlers that stringify them — correctly picking up `ValueError` — then swept **every** raise of that class, constructors included.
>
> ```
> asked     is this sentence raised through a class a route stringifies
> mattered  can a person reach the place it is raised
> ```
>
> `CloudModelClient needs base_url or a client` fires in an `__init__` from environment variables while the app is wired: no object, no request, no reader. Two rows here, seven across the trio. Checked three ways — forward, backward, and that the exempted set matches what the ledger names exactly.
>
> **The ratchet also had 82 rows of slack**: ceiling 164 against 82 recorded rows, never brought down as rows were struck. It would have let the whole backlog be written again without a word.
>
> ## 4. A floor at a thirty-seventh of what it measures
>
> `assert len(i18n._REFUSALS) >= 9` against a table of **335** — the worst of the three. Registered as a Ratchet so the comparison happens, and struck from the unregistered-floor backlog (85 → 84).
>
> ## Verification
>
> Full suite green over this tree: **4465 passed, 3 skipped**. Placeholder parity checked in both directions. Both new guards sabotage-tested.

## #343 — The interrupted turn says how far it got, and a picture comes back down

- merged · opened 2026-08-23 · merged 2026-08-23
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/343>

> Two changes on top of the 1.5.0 work already on this branch.
>
> ## A profile answering an interruption knows where it was cut off
>
> Cutting a profile off mid-paragraph leaves the person holding a PREFIX of what it said. Until now the reply they got next was built from a transcript that showed the whole turn as though they had sat through it, so the profile either carried on from a point they never reached or answered as if its unheard sentences had landed.
>
>     asked     did the person interrupt
>     mattered  how much had they heard when they did
>
> The client knows the answer precisely because the voice is played sentence by sentence: an interruption lands on a known boundary, and `Speaking.heard()` reports exactly what reached the room. That rode nowhere until now.
>
> - It rides on the interrupted turn itself — `room_messages.heard` — rather than beside it. It is a fact about that turn, every profile in the room reads the same transcript, and it survives a reload.
> - The write is guarded twice, by `sender_kind='profile'` and by `room_id`: a person's own message is not something they interrupted, and a client holding one room's token must not reach into another's transcript.
> - `_worded` renders it as a stated fact, in the same shape an attachment is, naming the part that reached the room so the reply can pick up from there. A turn heard through its last sentence is reported as finished rather than as a loss — apologising for a gap that is not there is its own failure, and it has its own test.
>
> Optional on the wire and ignorable. A client that never sends it — the three native shells, anything older — is describing a room where nothing was interrupted.
>
> ## Whatever you put up in a room, you can take back down again
>
> The chip labelled "Just my name" was taken out on request earlier in this round. It was a display toggle on a strip that was cropping, and the behaviour it offered survived: the camera control sets `showing` to voice and lands in the same place. Nothing looked broken.
>
> It was also the only caller of `DELETE /rooms/{room_id}/face` — the one route that takes an uploaded room picture or background back **off the server**. Changing what is displayed leaves the file exactly where it is; `roomface.clear` is what removes it. So the removal quietly took away the way down from a background somebody regrets, in a product where the thing on screen is a photograph of a person.
>
>     asked     is the picture on screen
>     mattered  can the person who put it there get it off the server
>
> The binding guard caught the orphan, which is what it is for. Recording it would have kept the route counted as doored while the erasure door stayed shut — exactly the false door that file's own header warns about. The taking-down half is back, narrowed rather than restored: offered only when `media_url` or `background_url` says there is something up to take down, which the display toggle never checked. It reloads afterwards, because a seat still showing a picture that is already deleted is a control that looks like it failed. `ins.face.hereoff` in all ten languages.
>
> ## Testing
>
> - `tests/test_the_profile_knows_it_was_cut_off.py` — 6 tests, including one that takes a real turn with a stubbed provider and inspects the transcript that actually went out. A fact recorded and never handed to the model is a fact that changes nothing.
> - `tests/test_a_picture_you_put_up_comes_back_down.py` — 3 tests. A guard that counts callers is satisfied by any caller, including a wrong one, so these read the claim instead: that a control reaches the binding that sends DELETE, that it is conditioned on there being a file, and that the room is re-read.
> - Both files negative-tested claim by claim. Door, route, language and release guards green; `tsc` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #342 — 1.4.0 — four things that worked and could not be seen to work

- merged · opened 2026-08-22 · merged 2026-08-23
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/342>

> Draft while the full suite runs over this tree. Nothing merges until it is green.
>
> One thread through all four findings: **the work was done and the answer was dropped.** A failure that is both total and unreported survives, and the unreported half is what lets it.
>
> ## A PDF comes back as words, or it comes back as nothing
>
> Reported three times, the third with the transcript attached — the profile in the room saying the filings *"came through as garbage on my end — scanned PDFs, no text layer, so what I'm seeing is byte soup rather than claims."*
>
> It was reporting honestly. Against a real, ordinary, text-bearing PDF the shipped reader produced **1,818 characters of mojibake and declared it read**. The same file now reads as 4,295 characters of English.
>
> ```
> asked     did any text come out of the PDF
> mattered  is it text
> ```
>
> Three faults, and the third is why the first two survived being reported three times:
>
> - **Only zlib streams were decoded.** A stream in ASCII85 — which is what the real file used — raised `zlib.error`, and the handler appended it **still encoded**. The scanner then matched parentheses inside compressed bytes. That is where the byte soup came from.
> - **Hex strings were not matched at all.** `_PDF_STR` knew `(...)` and not `<...>`, so every generator that prefers hex produced an empty read.
> - **`len(text) >= 40` stood in for *is this text*.** Forty characters is a length, and garbage is long. So this module's own header promise — that a PDF carrying only scanned pixels has no text in it to find — was the one case never reached. Unreadable bytes never came back empty; they came back as a paragraph.
>
> `_reads_like_language` is the gate that was missing, and it is what makes the rest safe to be best-effort. Everything upstream guesses; guessing is fine as long as failures come back as failures.
>
> Measured, not assumed: six filter arrangements built from what real generators emit — **two read before this, six now**. Nine gate cases: Japanese, Arabic, German compounds and number-heavy filing text pass as writing; the verbatim byte soup, base64 and a hex dump do not. The guards were run against the shipped reader and four of six arrangements fail it. No new dependencies — the container has no poppler and no OCR and this needs neither.
>
> ## The add-friend button says what happened
>
> *"I tried to bring in another synthetic profile in my friends list by using the add friend button and it's not working."*
>
> The server was never the problem — driven end to end, the row lands and reads back, and a second press correctly answers `added: false, reason: "already a friend"`. Every fault was in the console:
>
> - `Profile.tsx` guarded with a bare `return`. No request, no error, no note. `Discover.tsx`'s identical guard has always named the reason.
> - `Friends.tsx` asserted the owner token with `!` instead of checking it, then rendered the refusal at the **bottom** of a screen carrying the search results, the browse pool, the list and the suggestions. An answer below the fold is an answer nobody reads.
> - `addFriend` was `req<unknown>` with all three call sites dropping the reply.
>
> `FriendRemoval` has carried the same warning in a comment all along. It was never carried across to the add.
>
> ## The room shows you who you know
>
> *"My friends list should appear and be able to choose from the friends list to add other friends and profiles to the chat."*
>
> The invite has worked since it was built. The only way to name the guest was to type `prf_3735f90003ba`. Complete and unusable — which does not look like a bug from the inside: every part works, the tests pass, and the only person who finds out is the one holding the phone.
>
> Walked end to end: rows from the friends door → invite 201 → accept 201 → profile seated. **Not covered, said here rather than left to be found:** inviting another *person* by name. The wire takes profiles only; people join rooms through the lobby.
>
> ## A slept tab does not go quietly deaf
>
> No `visibilitychange` handler existed anywhere. The agent's orb and the room's standing ear both relit on `onend` into a page that could not run a recogniser — the room's own comment named the case ("a tab blur") and treated it as ordinary. Both ask before restarting now, at both doors, and both surfaces say *this tab is in the background* in all ten languages.
>
> ## Testing
>
> 52 new guards across the four. Every defect was planted back and confirmed caught — which is how one of them got fixed: it searched the body for `.added` and passed against a screen that had dropped the verdict entirely, because the l10n key it printed regardless is called `dsc.added`. A guard that matches the string it is meant to catch you printing is not a guard.
>
> `tsc --noEmit` clean. Full suite still running; results to follow before this leaves draft.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #341 — Release prep 0.99.0

- merged · opened 2026-08-22 · merged 2026-08-22
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/341>

> ## What this is
>
> Release prep for **0.99.0**.
>
>     asked     do the thirteen fields say the same release
>     mattered  a version is a promise every surface makes at once
>
> The trio versions together — one number names one tested combination of JIM-mini, QRME and PDI — so all thirteen version fields move at once: `pyproject.toml`, `app/package.json` and its lockfile, the Android `versionCode`/`versionName`, the iOS `MARKETING_VERSION`/`CURRENT_PROJECT_VERSION`, the three fields in `QrmeStudio.csproj`, and the `FastAPI(version=…)` the running service reports.
>
> ## What landed in this release
>
> **A voice room is a voice room.** A room opened for audio arrives speaking, with no type bar to contradict it and the microphone as the way in; leaving any screen ends its voices, the transcript keeps itself current, and the talking light follows the voice actually being heard.
>
> ## Paperwork
>
> - `CHANGELOG.md` — the `[Unreleased]` heading is dated `[0.99.0] - 2026-08-21`, and the compare link closes over the tag rather than trailing `HEAD`.
> - `README.md` — the current-release line and one new row in the history table.
>
> ## Tests
>
> Full suite green over this tree: **4071 passed, 3 skipped** (24m48s). Run solo — JIM's and QRME's suites both bind ports and cannot share a machine with each other.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #340 — A voice room is a voice room

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/340>

> ## What
>
> Field report, holding a `voice` room up against what it drew: "this is supposed to be audio chat only — we need to get rid of the type bar and the transparent chat text and go back to hearing the voices."
>
> The channel was chosen on the way in and then ignored. Every room wore the same chat furniture, and hearing was an opt-in press — so the one room whose whole pitch is sound arrived silent with a keyboard in front of it.
>
>     asked     what kind of room is this
>     mattered  the room's own answer, or the same furniture everywhere
>
> - **It arrives speaking.** Going in is itself the press the autoplay rules want (exactly what the 🔊 toggle was standing in for), so nothing else has to be tapped. The toggle stays as the way to *silence* a voice room; a chat room's remembered choice is untouched.
> - **No type bar, no transparent lines.** The strip is replaced by one control that listens, plus a line naming who is speaking.
> - **The mic sends.** Dictation's "the send stays a decision" bargain belongs to a room people type in; here speaking is the medium, so what the recogniser hears goes straight into the room. One microphone — starting to talk stops dictation, and leaving or switching rooms lets go of it.
> - **What stays:** the transcript keeps its card (reading stays deliberate rather than pasted over a room you came to listen to), sharing and "let them talk" are untouched, and a browser with no recogniser (iOS Safari) gets the typed pill back with a line saying why.
>
> ## Tests
>
> - `tests/test_the_room_speaks_for_itself.py` gains five: the channel decides the furniture (both flat scene and stage), the room turns its own ear on, talking reaches the room and stops dictation, the no-recogniser fallback, and the talk control letting go with the room.
> - Full suite: **4071 passed, 3 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #339 — Release prep 0.98.0

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/339>

> ## What
>
> Version bump 0.97.0 → 0.98.0 across every surface that states it: `pyproject.toml`, `qrme/api.py` (FastAPI title), `app/package.json` + lockfile, Android `build.gradle.kts` (versionCode 98000), iOS `project.yml`, Windows `QrmeStudio.csproj`. The CHANGELOG's `[Unreleased]` is dated `[0.98.0] - 2026-08-21` with the compare link closed over the tag, and the README's release table gains the 0.98.0 row.
>
>     asked     do the thirteen fields say the same release
>     mattered  a version is a promise every surface makes at once
>
> ## Tests
>
> Full suite over the release tree: **4066 passed, 3 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #338 — Leaving the screen ends the voices

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/338>

> ## What
>
> The twin product found this defect first, on its conversation screens; the same one lived here in three rooms.
>
>     asked     what happens to a playing voice when its screen goes away
>     mattered  a voice with no screen is a speaker nobody can stop
>
> - **Agent orb** — no unmount teardown at all: the relight-after-reply contract kept re-opening the recogniser under a screen that no longer exists, and the dictation recogniser was never owned by `stopVoice`. The teardown now runs `stopVoice()` and stops the dictation by hand.
> - **Room ear** — the queue kept reading the OLD room's turns after a switch, because its only handle was a local inside the loop. It now carries a run counter and a live handle: switching rooms — or leaving, which runs the same cleanup — bumps the run, stops the playing turn, and stops the dictation. The per-turn 🔊 rides the same handle.
> - **Chat overlay** — the reply, and the device-voice fallback behind it, both played on after navigation. The screen now holds the `Speaking` handle and stops it (and cancels the synthesiser) on the way out.
>
> ## Tests
>
> - `tests/test_leaving_the_room_ends_the_voices.py` — pins the orb teardown (stopVoice + dictation), the ear's run counter and room-change cleanup, and the chat overlay's stop + synthesiser cancel.
> - Full suite: **4066 passed, 3 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #337 — The room keeps itself current, and the light follows the voice

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/337>

> ## What
>
> Two fixes to the room screen, one commit.
>
> **The room keeps itself current.** The transcript refreshed only on mount or after the viewer's own action — another person's turn, a profile's reply to somebody else, a shared picture: none of it arrived until you did something. The room now polls its transcript every four seconds while open. That also fixes the loneliest wait in the product: your own turn appears while the profiles are still writing their replies, because the server stores it before it starts generating — before this, the send sat invisible until every profile had finished. The room's ear reads new turns as they land. A failing poll stays quiet (an error banner repainted every four seconds is a nag; the next action's own error handling still says what is wrong).
>
> **The talking light follows the voice.** The green square matched the transcript's *last line* — with the ear reading a backlog of turns aloud one by one, three queued turns light the wrong square until the reading catches up. The square now lights the turn actually being heard (the ear's queue and the per-turn 🔊 both mark whose turn is playing), with the transcript's last line as the fallback when no voice plays. Identity matching (kind + id, never display name) stands.
>
>     asked     does the room move on its own, and whose square is lit
>     mattered  a room you have to poke to hear is not a room, and the
>               light belongs on the voice being heard
>
> ## Tests
>
> - `test_the_room_speaks_for_itself.py` gains `test_the_room_keeps_itself_current` (poll present, quiet on failure) and `test_the_light_follows_the_voice` (voicing wins, set before play, cleared on every exit path).
> - Full suite: **4063 passed, 3 skipped** (a solo re-run after one environmental failure in the port-binding browser-enforcement module while the PDI suite ran in parallel — passes clean alone).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #336 — The answer begins before it ends

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/336>

> ## What
>
> Every screen that speaks a profile's bound voice now speaks **piece by piece**: the reply is cut at sentence ends (`app/src/pieces.ts` — the same splitter the twin product ships), the first sentence is synthesised alone (small, so it comes back fast), and every later piece is fetched while the one before it plays (`app/src/spoken.ts`, `speakInPieces`).
>
>     asked     when does the answer start being heard
>     mattered  does the wait grow with the length of the answer
>
> - **Agent orb** — the `playing` ref becomes a `Speaking` handle, so closing the orb stops the whole reply (not just the playing piece before the next one starts).
> - **Chat talk overlay** — the talking face lights when the first word is heard, not when the whole reply is rendered.
> - **Room** — the auto-hear queue and the per-turn 🔊 both go through the pipeline; one-voice-at-a-time and the silent-backlog rule stand.
> - `Voice.tsx` keeps its direct call: its one utterance is the fixed one-sentence binding test.
> - Failure contract: the first piece is awaited before the handle exists, so a caller with no binding/engine still takes its device-voice fallback with the whole text; a later piece failing drops the remainder quietly (the text stands on screen). A withheld autoplay still ends quietly — that guard moved with the code it pins.
> - Side effect that is really the point: each piece is far below any engine's synthesis ceiling, so a long reply no longer falls out of the bound voice into the browser's robot just for being long.
> - **Docs**: §8d of `docs/beta-deploy.md` now proves the local model with the vault's own `local_model_standing` posture read (landed in PDI this round) instead of leaving the proof to a conversation.
>
> ## Tests
>
> - `tests/test_the_answer_begins_before_it_ends.py` — 8 new tests: the splitter is transpiled and executed through node (first sentence rides alone, decimals and titles don't split, thirty sentences don't become thirty requests, nothing lost); pipeline pins (prefetch, first-piece gate, no screen calls the synthesis door directly, orb close stops the handle, the runbook names the standing door).
> - Full suite: **4061 passed, 3 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #335 — The room speaks for itself, and listens

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/335>

> ## What this is
>
> Field report over the room screen (Inside.tsx): the per-turn 🔊 was liked, and sent back anyway — the room should be hearable without pressing each turn, the composer should take speech and not only typing, and a button that is only a send "could be a lot smaller".
>
> - **Hear the room**: a toggle (one press — the gesture autoplay rules want); after it, every profile turn that *arrives* speaks in its bound voice. One voice at a time, backlog deliberately silent, withheld autoplay ends quietly (per-turn 🔊 stays on every line), choice remembered per browser.
> - **Dictation mic**: speech types into the box where the browser ships a recogniser — absent, not disabled, on iOS Safari — and never sends on its own; the send stays a decision in a room with other people in it.
> - **Compact send**: the "Say it" button shrank to a glyph, kept its accessible name, and Enter sends too.
>
> ## How it holds
>
> `tests/test_the_room_speaks_for_itself.py` — 8 pins: remembered choice (on *and* off), silent backlog, the queue's lock, quiet autoplay refusal, surviving per-turn button, dictation-types-never-sends, the dead-control rule, and the send's accessible name.
>
> ## Diff shape
>
> `app/src/screens/Inside.tsx` (toggle + queue + dictation + composer), `app/src/l10n.ts` (3 keys ×10 languages), one new test file, CHANGELOG.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #334 — The starters sound like themselves

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/334>

> ## What this is
>
> The reviewer's call, after listening to the starter pack: the women in the collection take a woman's voice from the engine's own premade list, the men a man's — and never the voice the sibling guardian product speaks with.
>
> The audit found the pack almost there already, with one systematic exception: **River**, the engine's androgynous premade, sat on two men and a woman. Recast:
>
> - Pete Kowalski (career civil servant) → **Bill**
> - Harold Jenkins (insurance adjuster) → **George**
> - Nadia Petrova (security analyst) → **Alice**
>
> ## How it holds
>
> - `tests/test_the_starters_sound_like_themselves.py`: every starter whose brief states a gender is pinned to a matching voice from a vetted premade table; the guardian's default voice (Daniel) appears nowhere in the pack; briefs that state no gender are deliberately unpinned rather than guessed at.
> - Decks seeded before the recast are repaired at startup — but only where the binding still equals, byte for byte, what the seed itself wrote (`_RECAST` in `qrme/seed.py`). An owner who rebound a voice keeps it, whatever it is.
>
> ## Diff shape
>
> `qrme/seed.py` (3 voice rows + `_RECAST` + recast branch in `_voice`), one new test file, CHANGELOG.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #333 — Section 8: the vault's real voice — a local model on the box

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/333>

> The long-promised §8, unblocked by writing it as a decision table instead of waiting on the box's numbers: measure `free -h`, take the row you can afford while the stack runs — the estate's own 4 GB VPS takes the smallest row (`llama3.2:1b`), and a bigger box someday changes the answer without changing the page.
>
> - **The runbook** (`docs/beta-deploy.md` §8): measure → pick from the table → one Ollama daemon on the stack's network (`docker run … --network docker_default`, weights in a named volume, no published port — the same standing the ears and eyes have; PDI's offline gate resolves the service name to a private address even under `PDI_OFFLINE`) → pull the row's model → four `.env` lines → recreate `pdi` and `qrme`. Ends the way it starts: measure again under load, with the removal lines one paste away so the honest stub can resume.
> - **Compose** forwards all four dials (`PDI_OLLAMA_URL`, `PDI_RESIDENT_MODEL`, `QRME_OLLAMA_URL`, `QRME_OLLAMA_MODEL`) and §2's `.env` template documents them — the documented-variable guard holds both directions.
> - **`qrme/llm.py`** reads its two through `or` rather than `get()` defaults: compose forwards blanks on a box whose operator left them empty, and an empty string standing in for a default is how a dial connected to nothing becomes a broken door.
>
> ```
> asked     can the box afford a voice
> mattered  a runbook that starts with a measurement instead of an instruction
>           never asks a 4 GB box to act like a 32 GB one
> ```
>
> ## Verification
>
> Full QRME suite over the final tree: **4023 passed, 4 skipped** in 17:13 — the documented-variable guard green over the four new dials.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #332 — Release prep 0.97.0

- merged · opened 2026-08-21 · merged 2026-08-21
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/332>

> 0.97.0 across the trio. This repo's half: everyone here is the default — the browse pool with its honest head count on the console and all three native shells, Go private as the reversible door out of the pool and the name search; a voice id binds to the account that brought it; the agent orb and the pair chat answer in the bound voice with the device's as honest fallback; and the orb stops lying — it relights over silence, says "Speaking" while the reply plays, and bows out after two quiet minutes.
>
> The thirteen release fields move to 0.97.0, the CHANGELOG's `[Unreleased]` becomes the dated `[0.97.0]` section with its compare link closed over the tag, and the README banner and release table say the same.
>
> ## Verification
>
> Full QRME suite over the final release tree: **4023 passed, 4 skipped** in 16:51.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #331 — Everyone here is the default, and the bound voice reaches the conversation

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/331>

> QRME's slice of a multi-repo batch round, two commits over one verified tree.
>
> ## Everyone here is the default (`4f09844`)
>
> The field asked for it in head-count terms: every profile made on the deployment goes on the browse list, real people and synthetic ones side by side. Listing is the default; privacy is the door out.
>
> - `GET /people/browse` — public like `/people`, made of the same already-public rows, with the honest `head_count` and a per-kind breakdown (`kind_counts`). Anonymous profiles never appear; only active profiles greet strangers.
> - `PUT /profiles/{id}/listing` — the owner's **Go private** switch, taking a profile out of the pool *and* the name search, reversibly, per profile. The `unlisted` column rides the additive migration, so an existing deployment wakes up with everybody listed — the spec's default.
> - The pool stands on every surface: the console's Friends screen (count line, kind chips, add buttons, this profile's own switch) and real doors on all three native shells — SwiftUI, Compose, and XAML each browse, show the standing, and flip the switch, with the ten l10n rows in each shell's own table.
>
> Five guards fired on the way in and every one earned its keep: the field-label registry demanded a labelled `listed`; the two-party sweep demanded `/people/browse` declare itself a public read; the doorless ratchet refused a recorded backlog and demanded real native doors; the unused-binding ratchet then demanded screens actually call them; and the wire-name guard caught `kinds` colliding with the overlays' `kinds` (it ships as `kind_counts`). The duplicate-translation guard even caught "you" translated two ways.
>
> ```
> asked     who is here
> mattered  a deployment whose people cannot see each other is a hallway of closed doors
> ```
>
> ## The bound voice reaches the conversation (`04e2a62`)
>
> A profile whose owner had made and bound a real voice still answered the agent's orb and the chat screen in the browser's robot. Both now speak through the bound voice first — the deployment's engine, the watermark riding in the header — with the device's voice standing in when there's no binding, no engine key, or the reply outruns the ceiling. The orb's relight contract carries over either mouth, closing the orb stops the audio mid-sentence, and the chat face's "speaking" state learns the second mouth.
>
> ## Verification
>
> Full QRME suite over the final tree: **4023 passed, 4 skipped** in 16:33 — including the new `test_everyone_here_is_the_default.py` (6 tests). `npx tsc --noEmit` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #330 — The voice binds to the account that brought it, and the orb tells the truth

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/330>

> Two halves, one screen apart — a self-picked round closing a flagged gap and a mic-truth bug.
>
> ## The voice claim (`qrme/spoken.py`)
>
> `GET /profiles/{id}/voice` is a public read on purpose — a voice a stranger can hear is a voice a stranger should be able to check the provenance of. That put every voice id one screen away from every other tester, on a deployment whose ElevenLabs key is shared: anyone who learned an id could bind it and speak with somebody else's cloned voice (the warning was given the day the key went deployment-wide).
>
> The first account to bind an id now holds it: the same owner may share it across their own profiles, another account is refused with the reason and told to make its own voice on the provider's surface, and unbinding everywhere releases the claim. The claim is the bindings themselves (a join against `profiles.owner_id`), not a second ledger — nothing to migrate, nothing to drift.
>
> ```
> asked     whose voice is a bound voice
> mattered  a claimable clone of a real throat is impersonation with extra steps
> ```
>
> ## The honest orb (`app/src/screens/Agent.tsx`)
>
> A silent stretch ends the browser's recogniser on its own, and the orb kept saying "listening" over a dead microphone. It relights now — unless a turn is mid-flight (the reply's own end relights), the person closed the orb, or nothing has been heard for two minutes, in which case the conversation bows out quietly (`CONVERSATION_IDLE_MS = 120_000`, the same number JIM's rooms settled on). The idle clock restarts when a spoken reply finishes so a long answer never eats into the two minutes, a failed turn relights the mic instead of stranding the orb, and while the reply is being spoken the orb says "Speaking — it listens again after" in ten languages.
>
> ## Verification
>
> Full QRME suite over the final tree: **4015 passed, 4 skipped** in 17:20 — including the new `test_the_voice_binds_to_the_account_that_brought_it.py` (4 tests: cross-account refusal, same-account sharing, release-on-unbind, distinct ids untouched). `npx tsc --noEmit` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #329 — Release prep 0.96.0

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/329>

> 0.96.0 across the trio. This repo's half: the picture goes up like the camera (full-bleed with the same double-tap/hold reveal machinery), the assist screen's wearables card takes the settings-page shape (My devices / Other devices, hairline rows, ⓘ details), and `MAX_REPLY_TOKENS` comes back to five times the original room after the field called the ten-times wait on spoken turns.
>
> The thirteen release fields move to 0.96.0, the CHANGELOG's `[Unreleased]` becomes the dated `[0.96.0]` section with its compare link closed over the tag, and the README banner and release table say the same.
>
> ## Verification
>
> Full QRME suite over the final release tree: **4011 passed, 4 skipped** in 18:14.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #328 — The spoken turn, the picture up, and the device page

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/328>

> Three field reports from one beta session, landed as three commits over one verified tree.
>
> ## The reply ceiling comes back to five (`b447bd6`)
>
> `MAX_REPLY_TOKENS` went 1024 → 5120 → 10240 across earlier rounds; the field called the last move back. On spoken turns the person waits through the whole synthesis before hearing anything, and ten times the original room made that wait noticeable. Back to `1024 * 5`, with the comment carrying both moves and the pin test renamed to `test_the_budget_is_five_times_what_it_was` so the history stays in the tree.
>
>     asked     how long is the answer
>     mattered  a spoken reply is waited on end-to-end — the ceiling is a latency dial
>
> ## The picture goes up like the camera (`c3cccd3`)
>
> "Put a picture up" rendered as a small portrait while the camera went full-bleed. The photo now joins the camera's machinery in `Inside.tsx`: full-bleed in the tile (`.rs-photo.rs-fullbleed` sharing the camera's CSS), the same double-tap/hold reveal to reach the controls on your own tile, and the swap paths (different photo, back to camera, profile picture, just the name) all reachable from the revealed controls. Other seats see photos full-bleed too; the reveal machinery stays yours alone.
>
>     asked     can a picture stand where the camera stood
>     mattered  two ways of showing a face should not have two different rooms
>
> ## Connecting a device reads like the phone's own Bluetooth page (`01175f2`)
>
> A field report held the assist screen's wearables card next to the phone's Bluetooth settings. It is the settings shape now: **My devices** as a rounded, hairline-separated list — name, Connected/Not connected on the right, ⓘ opening the detail (kind, transport, faces, Unpair) — and **Other devices** underneath holding the scan and the manual add. Five new l10n rows in all ten languages.
>
>     asked     can a person find their device
>     mattered  a screen shaped like the one in their pocket needs no manual
>
> ## Verification
>
> Full suite over the final tree (all three changes together): **4011 passed, 4 skipped** in 18:11. The ceiling change tripped the old `test_the_budget_is_ten_times_what_it_was` pin mid-flight — the pin moved with the decision and keeps both moves in its docstring.
>
> JIM's half of the device-page report lands separately in jim-mini.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #327 — The eyes open on the beta host

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/327>

> asked     is the sidecar up
>     mattered  did anything ever actually render on the host
>
> Field find, from the deploy itself: the renderer container had crash-looped since its first deploy — `ModuleNotFoundError: No module named 'playwright'` — and `pip show playwright` inside the freshly built image answered "not found". The Playwright base image bakes the *browsers*, but the module was not importable by the python uvicorn runs under, so every capture on the host has been riding the honest plain-fetch fallback (`rendered: false`, with the reason in the seal) since 0.93.
>
> Changes:
> - `docker/renderer/Dockerfile`: `playwright==1.47.0` installed explicitly, pinned to the image's own baked browsers — verified live on the beta host, where this exact line took the container from `Restarting` to `Up` with `Uvicorn running` in the log
> - `docs/beta-deploy.md` §6b/§6c: the after-deploy checks pair `ps` with a three-line log tail — `ps` proves a container restarts politely; the log proves it booted, which is exactly how this hid for two releases
> - `CHANGELOG.md`: the entry is folded into 0.95.0's Fixed section, since no 0.95.0 tag has been fired yet and the tag should build with working eyes
>
> Full QRME suite green over this tree: 4011 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #326 — Release prep 0.95.0

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/326>

> asked     do the thirteen fields say the same release
>     mattered  a version is a promise every surface makes at once
>
> 0.95.0 for QRME: the ears arc reaching every briefcase door — a read-once link that is a recording comes back as the words said in it, an uploaded video or memo is heard through the ears' bytes door, and true audio files land as a `recording` of their own instead of an "unrecognized file" refusal. The thirteen version fields moved together via the release manifest; the changelog is dated with the compare link closed over the tag; the README's banner and table carry the release.
>
> Full QRME suite green over this tree: 4011 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #325 — The voice memo lands

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/325>

> asked     can a person hand the profile a voice memo
>     mattered  the words said in it, landing — never "unrecognized file"
>
> A true audio file — MP3, WAV, Ogg, FLAC — handed to the briefcase was refused at the door with "unrecognized file", the deferred half of the upload round. It is a briefcase kind of its own now, `recording`: sniffed by its magic bytes before the media reader can refuse it, heard through the ears' bytes door, and honestly *held* on a stack without ears — landing either way beats a 422.
>
> The wall's media store is deliberately unchanged: it serves images and video a profile wears; a recording handed to a pair belongs to the conversation, read here and never stored as a file. RIFF stays two things — WAVE is a recording, WEBP a photograph — and `.m4a` is absent from the audio magics on purpose: it opens with the same `ftyp` box an `.mp4` does and the video branch already hears it.
>
> Changes:
> - `qrme/briefcase.py`: `_AUDIO_MAGIC` + `_sounds_like_audio`, the `recording` branch in `read_file`, `KINDS` and the prompt-block label
> - `qrme/routers/briefcase.py`: the door's docstring names the voice memo
> - `tests/test_the_upload_hears.py`: four more tests — heard memo, held-not-refused without ears, RIFF disambiguation, route-level kind
>
> Full QRME suite green over this tree: 4011 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #324 — The upload hears

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/324>

> asked     what does this recording say
>     mattered  the words said in it — heard at home, or honestly "held"
>
> A video handed to the briefcase was still told "this deployment holds the bytes and cannot turn them into words" — true when it was written, untrue since the stack grew ears. The ears gain a bytes door (`POST /transcribe-file`: same 200MB cap, same temp-directory custody, nothing fetched so the SSRF inward gate has no business on it; the transcription core is now shared between both doors), and `read_file`'s video branch asks it through `scrape.transcribe_bytes`: the item lands carrying the words said in the recording, `read: true`, the same shape a document takes. A voice memo rides the same branch — an `.m4a` opens with the same `ftyp` box an `.mp4` does. Without ears the old posture stands unchanged, and these are ears, not eyes: the picture in the frames stays undescribed either way.
>
> Worth recording: the estate's own egress guard (`test_nothing_leaves_the_host`) failed the first full run because the new socket skipped the offline gate on the grounds that the sidecar is stack plumbing — the exact deployment-assumption drift `offline.allow`'s docstring warns about. The socket is now gated on the sidecar's own address (stack-internal passes even offline, the Ollama rule) and the visit is witnessed against the profile the upload belongs to, with `on_behalf_of` threaded through `read_file` from the route.
>
> Changes:
> - `docker/ears/server.py`: `/transcribe-file` + shared `_words_from`
> - `qrme/scrape.py`: `transcribe_bytes(data, on_behalf_of)` — gated, attributed, None for every missing-ears case
> - `qrme/briefcase.py` + `qrme/routers/briefcase.py`: the video branch hears; docstrings tell the new truth
> - `docs/beta-deploy.md` §6c: the bytes door documented
> - `tests/test_the_upload_hears.py`: five tests, unit and route-level
>
> Full QRME suite green over this tree: 4007 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #323 — The briefcase hears

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/323>

> asked     what does this link say
>     mattered  the words said in it — or "held", never junk marked read
>
> A read-once link that *is* a recording used to fall to the plain fetch, which decodes compressed media as mojibake and marks it read — a worse account than saying nothing. The link goes to the stack's ears now (`scrape.fetch_transcribed`, named by `QRME_EARS_URL` in the compose file), and the interactor's item carries the words said in the recording.
>
> Without ears there is no stand-in: unlike a page, where the shell the server sends is still the page's own text, the bytes of a recording are not its words. The item is *held, not read* — the same posture an uploaded video takes — and the plain fetch does not even run for a media link.
>
> Changes:
> - `qrme/scrape.py`: `is_recording` (the canonical media-suffix list) and `fetch_transcribed` (None for every kind of missing ears, offline gate on the target)
> - `qrme/briefcase.py`: `read_link` routes recordings to the ears, refuses honestly without them
> - `qrme/lookout.py`: `_is_recording` delegates to the shared list — a suffix taught to one door is taught to both
> - `docker/beta-compose.yml`: the qrme service's env block gains `QRME_EARS_URL`
> - `tests/test_the_briefcase_hears.py`: five tests, including that the plain fetch never runs for a media link and that both doors share one suffix list
>
> Full QRME suite green over this tree: 4002 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #322 — The lookout grows ears, and the release cuts

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/322>

> Three commits over one suite-verified tree.
>
> **The lookout grows ears** (`caa4087`)
>
>     asked     can a profile keep an ear on a recording
>     mattered  the same lookout, hearing where hearing is what the URL is
>
> Planting a lookout on a URL that *is* a recording — the media file itself (.mp3, .mp4 and kin, judged by the path, never the query) — stands a `fetch.listen` appointment on the vault's ears. Same capture key, same change-memory; the letter says "watched recording" because new words said are not a page edited. A deployment without ears fails the cycle in words and the `trouble` line carries the reason.
>
> **The study's author on screen** (`31561b1`)
>
>     asked     does the person see who answered
>     mattered  a provenance only the API can see is disclosure to nobody
>
> The trips list and the single-study view wear `answered_by` beside `left_host` and the redaction count — ten languages, absent on rows that predate the record.
>
> **Release prep 0.94.0** (`1a9e016`)
>
> The thirteen version fields moved together via the release manifest; the changelog is dated with the compare link closed over the tag; the README's banner and table carry the release.
>
> Full QRME suite green over this tree: 3997 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #321 — The stack grows ears

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/321>

> asked     what was said in this recording
>     mattered  the words, made at home — never the bytes shipped out
>
> A transcription sidecar joins the deploy stack (`docker/ears`): a local speech-to-text model in its own container, one door — `POST /transcribe {url}` answers the words said in a recording, audio or video, ffmpeg making one shape of either. The vault's new `fetch.listen` (pdi PR #189) asks here, named by `PDI_EARS_URL` in the compose file — topology, not a secret, like the eyes.
>
> The words are made on the deployment's own hardware — a recording fetched on someone's behalf never leaves the facility to become text — and the sidecar keeps no copy: transcribed in a temp directory, deleted with it. The same outward-only boundary as the renderer (private, loopback, link-local and stack-internal addresses refused, single-label names included), a 200MB cap, and the model weights baked in at image build so a running stack never reaches out for them (first `docker compose build` downloads the whisper `base` model once, ~150MB).
>
> Changes:
> - `docker/ears/Dockerfile` + `docker/ears/server.py` (new)
> - `docker/beta-compose.yml`: `ears` service; the pdi service's env block gains `PDI_EARS_URL`
> - `docs/beta-deploy.md`: §6c "The ears" beside the eyes, including the honest difference — no fallback, because the bytes of a recording are not its words
>
> Full QRME suite green over this tree: 3993 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #320 — The study says who answered

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/320>

> asked     which model was this study sent to
>     mattered  which model actually wrote these findings
>
> The excursion row was the audit trail for what could have left — the sanitized brief, the redaction count, `left_host` — but not for who wrote what came back: a study whose model degraded to the stub, or whose vault turned out to be an older tandem without the voice door, was recorded exactly like one the chosen model answered.
>
> Every excursion now records `answered_by` — the model's registry name, `vault` for the resident, `local fallback` for a degrade, `stub` for the local provider asked directly — read from the same request-scoped record the content provenance stamp trusts (`llm.answered_by`), cleared before the gather so an earlier degrade on the request cannot describe this study, and put back the way it was found.
>
> Changes:
> - `qrme/db.py`: `excursions.answered_by TEXT` (base schema + migration; rows that predate the column stay `null` rather than being guessed at)
> - `qrme/research.py`: `gather_inside` notes its own two outcomes — the resident's answer is `vault`, the fall to the local provider is `local fallback (degraded from vault)`, never dressed in the vault's name; `excursion` records the answer and carries it into the `qrme_studies` ledger row in the vault's tables; module docstring documents the provenance fingerprint
> - `qrme/routers/research.py`: the excursion endpoints carry the field
> - `tests/test_the_study_says_who_answered.py`: six tests — stub named as itself, a model's name on its study, a degrade not dressed as the model, the vault named vault, an older tandem not dressed as the vault, and an earlier note not describing this study
>
> Full QRME suite green over this tree: 3993 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #319 — The letter is not the looser door

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/319>

> asked     does the letter keep the excursions' promise
>     mattered  one loose door undoes every careful one
>
> Raised by the outside reviewer: the study path sanitizes what leaves the host and writes down that it left — and the weekly letter, naming the people the pair talked with, the watched pages, the week's counts, reached the same network models with neither.
>
> Now the letter keeps the promise. A voice that would leave the host receives the *sanitized* digest — with the week's own names passed to the sanitize pass the way the inquiry path passes its extras — and each letter stores and discloses `left_host` and the redaction count. The owner's letter keeps every word: sanitizing is about what leaves, never about what they may read of their own week. The vault's voice still reads the full digest — the facility's own wire is not leaving, exactly as the excursions already ruled (`llm.is_network` publishes the registry's honest `network` column; the caller decides what counts as leaving).
>
> JIM's letter makes the same move in its own repo, same round. Suite green over the final tree: 3980 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #318 — Every documented variable reaches its container

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/318>

> asked     does the page's .env template match the compose file
>     mattered  a documented dial that reaches no container is a lie with good documentation
>
> `PDI_RESIDENT_PULSE` was the scar: the deploy page told the operator to set it, and the compose file never forwarded it — compose passes only what a service's environment block names. `PDI_OLLAMA_URL` was the second instance, and a second instance is when a lesson becomes a guard.
>
> The guard checks both directions over the deploy page's `.env` template and the compose file: every documented variable must be forwarded by some service's environment block, and every `${VAR:?}` the compose file refuses to start without must be documented. It reads the YAML compose actually parses rather than the raw text — its own first draft flagged `CLOUDGW_CONSOLES_TOKEN`, which lives in a deliberately commented-out "one edit away" block, and a door deliberately not built yet is not a requirement.
>
> Suite green over the final tree: 3976 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #317 — Complete context rides the briefcase and the lookouts

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/317>

> asked     did the profile read what it was handed
>     mattered  a complete scrape that reads shells scrapes nothing
>
> The owner handed his profile three consoles and the briefcase said "read once — 12 characters, carried as 12" about each: the shell the server sends, distilled faithfully into nothing. The eyes exist now (0.92's renderer sidecar and the vault's `fetch.render`); this round makes everything that reads a page on someone's behalf actually use them.
>
> - **The briefcase's read-once links take the rendered reading first**: `scrape.fetch_rendered` asks the stack's renderer through the same offline gate the plain fetch stands behind — the target is what leaves — and `read_link` carries what a person would meet. A deployment without eyes answers None and the plain fetch stands in; the character count on the item's state line is the honest witness to which reading it was.
> - **The lookout twin plants `fetch.render` standing plans**: watching a page, not a shell. On a vault without a renderer the tool itself falls back and the seal says so; on a vault too old to know the tool, the plant fails in the vault's own words through the same door every lookout failure uses.
> - `QRME_RENDERER_URL` is named in the qrme service's own compose block — third time the forwards-only-what-a-block-names lesson has earned its keep here.
>
> JIM's lookouts made the same move in their own repo, same round. Suite green over the final tree: 3974 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #316 — The stack grows eyes

- merged · opened 2026-08-20 · merged 2026-08-20
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/316>

> asked     what does the page say
>     mattered  what a person would see, not what the server sent first
>
> A rendering sidecar joins the beta stack (`docker/renderer`): a real browser in its own container, one door, `POST /render {url}` answering a page's text as a person meets it. The vault's new `fetch.render` tool asks here, so a lookout pointed at a JavaScript console stops reading as a title and a dozen characters.
>
> Two boundaries, enforced inside the sidecar rather than assumed: **the eyes look outward only** — private, loopback, link-local and stack-internal addresses are refused for the target and for every subresource a page tries to load, via route interception, so a page on the open web cannot use these eyes to peer at the stack behind them — and **every render starts a fresh browser**, slower on purpose, so no cookies or storage bleed between one tenant's lookout and another's.
>
> `PDI_RENDERER_URL` is named in the compose file's own environment block — topology, not a secret, and named in the block because compose forwards only what a service's block names; that lesson already has its scar in this changelog. The deploy page grows §6b: what the eyes are, the boundaries, the honest fallback a deployment without them keeps, and the one-line check after a deploy. Compose validated; suite green over the final tree: 3972 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #315 — A backup you haven't restored from is a belief

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/315>

> asked     does the backup restore, and is the escrowed key real
>     mattered  every other failure costs a round; this one is an ending
>
> Raised by the outside reviewer as the only failure on the list with no second attempt, and moved ahead of everything on that argument. Three changes, one section:
>
> - **The freshness marker.** The compose backup loop now writes `/backups/.last-ok` after every successful pass, and §6 says to check the marker, not the folder — a loop that died silently keeps the shape of a backup while holding yesterday's.
> - **§6a, the restore drill.** The newest dump booted in a scratch container with the master key and admin token pasted from the password manager — never the box's `.env`, because the fire that burns the disk burns the `.env` with it. The audit chain walked end to end through a drill tenant, and a record sealed *before today* read back, because a fresh seal round-tripping proves nothing: only old data can vouch for a key.
> - **Cadence written down.** Quarterly, and after any key rotation — the two moments a stale escrow copy is born — with drill dates logged beside the key itself.
>
> The section was field-tested live while it was written, and its lines exist because the first run broke without them: paste-safe single-line commands (a clipboard that wraps long lines shattered a backslash-continued `docker run` into five fragments), `-u 0:0` on the scratch container (the image's unprivileged user cannot write a root-owned bind mount, and WAL-on-connect turns that into `server_error` on every door but `/health`), a sleep before the health check, and secrets verified by sha256 fingerprint before anything boots — hands produced eight different keys in eight attempts, and fingerprints settled every argument without a key touching the screen.
>
> The first run also cashed the drill's whole argument: it caught the password manager holding a wrong master key while the `.env` still held the right one, and the section now closes that loop with a paste-back fingerprint check. Suite green over the final tree: 3972 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #314 — The changelog says what the fixes were

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/314>

> The pulse-passthrough fix (#312) and the models-path fix (#313) landed with commits and pull requests and no CHANGELOG entries — the exact fold-it-away this estate's changelog discipline exists to prevent, caught from outside by a reader of the repos.
>
>     asked     are the deploy-day fixes written as what they were
>     mattered  awkward entries are what earn a changelog its credibility
>
> Both now stand under Unreleased as what they were: a gap between the docs and the compose file, and a runbook check aimed at a door that did not exist.
>
> Docs-only; full suite green: 3972 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #313 — The models check asks a door that exists

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/313>

> The "which model actually answers" check in `docs/beta-deploy.md` said `/api/models`; the Caddyfile proxies each domain 1:1 with no `/api` prefix, so the deployment answers `404 Not Found` to the exact command the page hands the operator — mid-deploy, wearing the costume of a broken stack.
>
>     asked     does the runbook's check hit a real route
>     mattered  a 404 mid-deploy reads as a broken box, not a wrong path
>
> Found the way every drift on this page has been found: by somebody standing on the box, pasting the line — during today's 0.91.0 deploy. The route is `/models`; the page now says so. Docs-only; the paste-ready guard passes; full suite green: 3972 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #312 — The pulse reaches the container

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/312>

> `PDI_RESIDENT_PULSE=60` in `/srv/qrme/.env` was the documented deploy step for the vault's heartbeat — and `docker/beta-compose.yml` never forwarded it: compose passes only what a service's `environment:` block names, so the standing tasks would have stood still on a box whose operator had done everything the instructions said. The same shape as the stub that reads as a broken feature: the deployment failing to say a variable never reached the process.
>
>     asked     does the heartbeat variable reach the process
>     mattered  an env line compose never forwards is a note to nobody
>
> The `pdi` service now passes `PDI_RESIDENT_PULSE` through with an empty default — empty means no in-process pulse, the pre-0.88 posture, so existing deploys are untouched — and the §2 `.env` template carries the line with its meaning, set to the beta's documented 60.
>
> Full suite green over this tree: 3972 passed, 4 skipped; the deploy-page paste-ready guard passes and the compose file parses.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #311 — Release prep 0.91.0

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/311>

> Thirteen version fields moved by the release script (driven by `tests/release_fields.txt`), plus the README banner, a 0.91.0 release-table row, and the CHANGELOG section dated with refreshed compare links.
>
>     asked     which files does a release touch
>     mattered  which fields does a release touch
>
> 0.90.0 → 0.91.0, build code 90000 → 91000. The cut carries the excursion honoring the voice choice (#308), the weekly letter (#309), and the letter's completed account of the asking (#310).
>
> Full suite green over this exact tree: 3972 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #310 — The letter accounts for the asking

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/310>

> The weekly letter counted messages, sealed moments, studies and the watching — and said nothing about the open board: the questions this profile put in front of strangers, and the answers they left. Twinned with davidsbianchi1984/jim-mini#241.
>
>     asked     who did the profile ask this week, and did anyone answer
>     mattered  work done on your behalf belongs in your account of it
>
> The digest now carries both — "N questions asked on the open board", "N answers came back" (blocked answers excluded) — in the same plain-sentence shape as every other line. The half of the studying that is done by people, and as much a part of the week as the pages.
>
> One new test; full suite green over the final tree: 3972 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #309 — The week in the pair's words

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/309>

> JIM's letter told a person what their own numbers meant; this is the twin turned toward custody. An owner runs a synthetic profile that talks to people, seals moments, studies topics and watches pages — and the only way to know what kind of week it had was to open four screens. The letter is the account rendered owed.
>
>     asked     what kind of week did the profile have
>     mattered  an account rendered only on request is an account withheld
>
> `POST /profiles/{id}/letter` composes the week from what it actually held: the messages exchanged and with whom, the moments sealed in the vault, the studies taken with their latest topics, and what the watching noticed — a changed page inside the window, a watch whose latest round failed. Each line is a fact from a table; none of them is a judgement.
>
> - The profile's **own provider** turns the digest into warm prose without adding a single fact the digest doesn't carry — the voice that speaks all week is the voice that reports on it, so the vault choice is honored here too.
> - `described_by` says plainly whether a model or the digest wrote the body: the stub, or a recorded degrade, keeps the digest as the letter rather than dressing it up.
> - An empty week writes no letter, refused translated.
> - A shelf keeps past letters newest first, each carrying the digest the words were made from. Doors on the console and all three shells.
>
> Four new tests; full suite green over the final tree: 3971 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #308 — The excursion honors the voice choice

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/308>

> An owner who picked "The vault's local model" made a choice about where this profile's words are made. The chat path honored it; the study path did not — `research.excursion` resolved the app-level cloud and shipped the sanitized brief out with `left_host: true`, exactly as if no choice existed.
>
>     asked     does the study speak with the chosen voice
>     mattered  a choice honored in one room and not the next is decor
>
> A profile whose provider is the vault now studies *inside*: `gather_inside` hands the brief to the resident (the same voice door the conversation uses), the findings are made on the facility's own hardware, the cloud sees nothing — the test spies on it — and `left_host` honestly says false. An older tandem without the voice door falls to the local deterministic provider, because the honest fallback for "never send it out" is a worse answer made at home, not a better one made by quietly shipping it anyway.
>
> Profiles on other providers study exactly as before, and the excursion row's contract is unchanged: the brief is still exactly what could have left, beside the count of what was taken out. No new routes; no wire changes. Twinned with the JIM half.
>
> Three new tests; full suite green over the final tree: 3967 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #307 — Release prep 0.90.0

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/307>

> Thirteen version fields moved by the release script (driven by `tests/release_fields.txt`), plus the README banner, a 0.90.0 release-table row, and the CHANGELOG section dated with refreshed compare links.
>
>     asked     which files does a release touch
>     mattered  which fields does a release touch
>
> 0.89.0 → 0.90.0, build code 89000 → 90000. The cut carries the watching answering to its owner: the lookout list and capture read-back saying when each page last actually changed (#305), and a failing lookout carrying its why in red (#306).
>
> Full suite green over this exact tree: 3964 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #306 — The lookout says why it fails

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/306>

> A lookout row could already say `failed`; the why lived buried in the vault's runs ledger (davidsbianchi1984/pdi#184), a console away from the owner whose watching broke. Twinned with davidsbianchi1984/jim-mini#237.
>
>     asked     why did the watching stop working
>     mattered  a failed status without a why is a shrug
>
> The PDI client gains `resident_runs` (None on an older PDI — deliberately not the same answer as "no rounds yet"), and the lookout list reads the latest round: when that round failed, its note rides the row as `trouble`, worn in red on all four clients.
>
> - Only the latest round speaks — a lookout that failed yesterday and ran clean this morning is not in trouble, so no stale alarm outlives its recovery.
> - An older vault without the ledger, or an unreached one, leaves the field null the same way `status` already goes null: absence stays absence, and a lookout in trouble never makes the list itself fail.
> - The note is the server's own sentence, shown as-is like every status and error on these rows.
>
> Three new tests; full suite green over the final tree: 3964 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #305 — The lookout says when the page changed

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/305>

> PDI 0.89's fetch fingerprints its captures (davidsbianchi1984/pdi#183); this round carries that knowledge to the owner. Twinned with davidsbianchi1984/jim-mini#236.
>
>     asked     when did the page change
>     mattered  a fetch date answers when we looked, not when it moved
>
> The lookout list and the capture read-back gain `changed_at` — when the watched page last actually changed across the vault's re-seals, not merely when it was last read — surfaced translated on all four clients ("Changed {when}", ten languages), and the profile's prompt block wears it too ("captured …, last changed …"), so a persona can say how fresh the menu it is quoting really is.
>
> Honesty carries through: a capture from before fingerprints answers nothing rather than inventing a date, an unreadable tandem leaves the field null the same way `status` already goes null, and absence never becomes a guess anywhere on the path from seal to screen.
>
> Two new tests; full suite green over the final tree: 3961 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #304 — Release prep 0.89.0

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/304>

> Thirteen version fields moved by the release script (driven by `tests/release_fields.txt`), plus the README banner, a 0.89.0 release-table row, and the CHANGELOG section dated with refreshed compare links.
>
>     asked     which files does a release touch
>     mattered  which fields does a release touch
>
> 0.88.0 → 0.89.0, build code 88000 → 89000. The cut carries the profile answering grounded in the vault (#302) and the lookout twin (#303): retrieval and generation both inside the facility with `grounded_in_vault` disclosed, and watched pages riding the chat prompt as dated captures the vault re-seals on its own appointments.
>
> Full suite green over this exact tree: 3959 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #303 — The profile keeps itself current: the lookout twin

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/303>

> JIM's lookout (davidsbianchi1984/jim-mini#231), with the payoff turned toward conversation: an owner plants "keep an eye on this page" as one standing appointment in the vault (davidsbianchi1984/pdi#177's tasks, davidsbianchi1984/pdi#178's schedule) whose single `fetch.url` step re-seals the current capture every cycle — and the profile *answers from* it. The latest captures ride the chat prompt wearing their URL and `fetched_at` date, capped at a digest's length, so a persona whose restaurant menu changed this morning speaks this morning's menu. The resident does the watching from inside the facility; QRME never does, and what leaves QRME is the URL once, at planting.
>
>     asked     can a profile stay current on a page
>     mattered  who does the watching, and where the page lives
>
> The rules, inherited from the JIM round and the study errands:
>
> - **Consent before the web.** Planting requires the profile's standing `study_the_web` privilege — the same consent the excursions ask for.
> - **Writes are plan-gated; reads and deletes keep the real vault.** The list, the capture read-back, the prompt block and the drop take `app.state.pdi`.
> - **The ledger lets go only after the vault did.** A drop cancels the standing task, unseals the capture, then deletes the local row; erasure walks the same path for every lookout the profile has, reported as `lookouts_cancelled`.
> - **Honesty at every edge.** No vault, an older tandem, an unreached tandem: each answers in words — and the prompt block contributes nothing rather than failing, because a turn that lands without the pages beats a turn refused for them.
>
> Doors on all four clients (console watched-pages card, iOS, Android, Windows). `no such lookout` joins `_REFUSALS` translated; `every_hours` joins `_FIELD_LABELS`; the drop wears the repo's existing stop-watching wording. 11 new tests; full suite green over the final tree: 3959 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #302 — The profile answers grounded in the vault

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/302>

> With the `vault` provider chosen, the resident ranks the pair's own seals against the last thing said and answers *from* them — retrieval and generation both inside the facility, through PDI's ask door (pdi#181) with the pair prefix as the wall inside the shared tenant, so what Alice told a profile still never grounds its reply to Bob. Twin of jim-mini#233.
>
>     asked     does the profile remember
>     mattered  where the remembering happens, and who is told
>
> - Client-side recall steps aside when the vault grounds: the resident reads the same seals, and the same seals said twice is not more memory.
> - `grounded_in_vault` in the provenance says whether the grounding actually happened — an older PDI without the ask door still speaks through the voice door, ungrounded and disclosed.
> - The prefix rides a request-scoped contextvar set by the chat route, the one layer that knows which pair is talking; the persona and conversation travel in the ask door's `system` slot, so grounding never costs the profile its voice.
>
> Three new tests. Full suite: **3947 passed, 4 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #301 — Release prep 0.88.0

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/301>

> Thirteen version fields driven by `tests/release_fields.txt`, plus the README banner, a release-table row, and the dated CHANGELOG section.
>
> 0.87.0 → 0.88.0, build code 87000 → 88000. The cut carries the vault voice (a profile generating on the facility's own hardware, falling honestly to the product's own stub when the vault has no model) and recall keeping the real vault across a billing change. On the console and all three shells.
>
> Full suite over the release tree: **3944 passed, 4 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #300 — Recall keeps the real vault

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/300>

> The last read still behind the plan gate (twin of jim-mini#230). The chat route passed the write-gated `memory_vault` to `recollection.chat_block` — so a member who moved to Free had a shelf that showed the pair's sealed moments and a reply that had stopped finding them.
>
>     asked     is the seal plan-gated
>     mattered  is the recall
>
> Recall now reads the real vault while the seal keeps the plan gate — the same writes-only split every other memory door already holds after the curation rounds. A free account's new turns are honestly not sealed at all, and the new test proves both halves at once: the spy sees the real vault reach `chat_block`, and the embed count stands still.
>
> Full suite: **3944 passed, 4 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #299 — The voice inside the vault

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/299>

> A `vault` provider joins the model registry: an owner picks "The vault's local model (PDI resident)" on the existing model screen and the profile's words are generated through PDI's new `/resident/infer` door (pdi#176), on the facility's own inference server. The prompt travels the one authenticated channel every seal uses and goes no further, and PDI's audit line carries its length, never its words.
>
>     asked     can a profile speak from inside the building
>     mattered  does the prompt ever leave it
>
> Honest at every edge: a vault with no local model raises rather than speaking the resident's operational stub sentence in a persona's voice — the turn falls to this product's own stub with the reason in the log; an older tandem without the door does the same; and with no tandem attached the choice simply is not configured, so a stored preference can never wedge generation.
>
> The provider reads the *live* client the app holds — `pdi_client.active()` bound to app state at creation — not a startup snapshot. No new routes: the choice rides the existing `/models` and `PUT /profiles/{id}/model` doors, and the label flows to every client from the server registry.
>
> Five new tests in `tests/test_the_voice_inside_the_vault.py`. Full suite: **3943 passed, 4 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #298 — Release prep 0.87.0

- merged · opened 2026-08-19 · merged 2026-08-19
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/298>

> Thirteen version fields driven by `tests/release_fields.txt`, plus the README banner, a release-table row, and the dated CHANGELOG section — with the stale `[Unreleased]` compare link brought current.
>
> 0.86.0 → 0.87.0, build code 86000 → 87000. The cut carries the profiles' memory by meaning: each interactor turn sealed into the tandem and embedded under the same key, recalled pair-scoped so what Alice said never surfaces for Bob; the pair's sealed shelf with a per-moment forget; and every transcript door — strike, forget by words, rewrite, erase-all — reaching the vault, so nothing struck stays findable. On the console and all three shells.
>
> Full suite over the release tree: **3938 passed, 4 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #297 — Transcript curation reaches the vault — no door forgets halfway

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/297>

> The shelf round (#296) proved a sealed memory can be taken back by hand. This closes the other half of the doctrine: the doors that curate the *transcript* — strike by checkbox, forget by words, rewrite in place, erase the whole memory — deleted the local turns and left the sealed recollection of those turns in the vault, **still findable**. Somebody who struck "custody hearing" from the record could have it surface in the profile's next reply, recalled by meaning from a seal no door had touched.
>
>     asked     did the turn leave the transcript
>     mattered  did the moment stop being findable
>
> ## What changed
>
> - **Strike and forget-by-words** unmake each struck turn's sealed memory — vector, seal, ledger row — and answer `sealed_forgotten` with what the vault actually let go of. Only refs the ledger holds are counted: profile turns are never sealed and count nothing, and a down tandem counts zero rather than failing the strike, because the strike is local truth and must land regardless.
> - **Rewrite** forgets the old seal through the real vault and re-seals the new words through the plan-gated one, answering `memory_resealed`. The order matters both ways: writes are plan-gated where deletes are not, so a member who moved to Free can still take the old seal away — and the rewrite is then simply not sealed, because old words that stayed findable would betray the edit.
> - **Erase-all for a pair** sweeps the pair's vectors, seals and ledger rows in one trip (`recollection.forget_pair`), each row going only after its seal did. When the tandem is down the local clearing still lands and the unswept rows stay on the shelf — readable and individually forgettable later — rather than being orphaned.
>
> No new routes, so no new doors: the typed clients (console, iOS, Android, Windows) carry the two new answer fields, and the count surfaces where each idiom already prints counts.
>
> ## Tests
>
> Eight new in `tests/test_striking_reaches_the_vault.py`: a struck turn stops being findable while its sibling still is; striking a profile turn forgets no seal; the strike survives a down tandem; forget-by-words takes the seal; an edit re-seals the new words; a plan-less edit ends the memory; erase-all sweeps the pair and only the pair; a down tandem leaves the shelf standing. Full suite: **3938 passed, 4 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #296 — The sealed shelf, shown and curatable — the interactor's own door

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/296>

> JIM's shelf round (jim-mini #226) put the coach's remembered moments in front of the person they are about; this is QRME's twin, one wall stricter, because the moments here belong to a pair.
>
>     asked     does the profile remember through the vault
>     mattered  can the person see what it remembers, and take one back
>
> ## The shelf
>
> `GET /profiles/{id}/memory/{interactor_id}/recollections` lists every moment the vault remembers of this conversation — refs from the `recollections` ledger (the same rows erasure walks), lines read back from the tandem — behind the pair's own `require_owner_or_interactor` door, so the answer is exactly what recall can surface, not a claim about it. A tandem that cannot be reached answers `readable: false` with the refs still listed: "I hold a moment I cannot show you right now" and "I hold nothing" are different answers.
>
> ## The forget door
>
> `DELETE …/recollections/{ref}` takes one moment back the whole way — the vector, the seal and the ledger row together, so it stops being findable rather than merely unreadable — while the chat turn it was sealed from stays in the transcript: forgetting the sealed memory is not striking the conversation, which keeps its own doors. The ref is scoped to the pair's ledger before the vault is asked anything, so a borrowed ref from someone else's conversation forgets nothing; and the ledger row lets go only after the vault did — a forget that only forgot the bookkeeping would strand the vector.
>
> Both doors read the **real** vault, not the plan-gated one: `storage.vault_for` gates writes only, and somebody who moved to Free still has a history they must be able to read back and let go of.
>
> ## Clients
>
> Doors on all four — the talk rail lists the shelf under the scalpel with a per-moment forget button; the three shells speak the pocket's id-driven idiom, the ref riding the turn-id field because the ref of a sealed moment is the turn it was sealed from. Five l10n rows per surface in all ten languages, byte-identical across the four tables; the new 404 joins `i18n._REFUSALS` translated rather than the ratcheted backlog. Wire names were checked against the Windows client's declarations: `held` is already a bool on this wire, so the shelf carries no count — the list is its own count.
>
> ## Tests
>
> Nine new in `tests/test_the_pair_reads_its_own_shelf.py`: the shelf lists what the vault holds; Bob's shelf never lists what Alice said; a stranger's token opens nothing; a down tandem says unreadable rather than empty; forgetting unmakes vector + seal + ledger while the transcript survives; a borrowed ref forgets nothing; a down tandem on forget is said, not hidden. Full suite: **3930 passed, 4 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #295 — Profile erasure takes the memory vectors too

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/295>

> The recollection round wrote the ledger row erasure reads, so the sealed lines died with the profile — but their embedding vectors survived in the resident's index, still ranking.
>
> Erasure now takes every vector under the profile's memory prefix in one resident call (`recollection.forget_profile`, PDI's new prefix forget) and reports the count in its answer — `memory_vectors: null` when the tandem was unreached, said rather than guessed. The sealed texts and the `recollections` ledger rows are taken by the sweep itself, as before; the vectors are the half only the resident can do. Held by a live test that chats, erases the profile, and checks the index is empty.
>
> Suite: 3921 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #294 — The profile remembers by meaning, through the vault

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/294>

> `remembrance` distills forward, in order — a timeline. `qrme/recollection.py` adds the other axis: each thing a person says to a profile is sealed AES-256-GCM into the tandem and embedded under the same key through PDI 0.86.0's resident index (which stores a hash of the text, never the text), so the reply that matters finds the moment that is *about* it — the sister from Lisbon mentioned once in March surfaces when the cooking question comes in October. Recalled lines ride the prompt beside the distillate, as memory the profile may draw on, never an instruction.
>
> The JIM round's three rules hold, plus one stricter:
> - **Memory never breaks the doing** — a chat turn lands even when the tandem is down.
> - **No vault, no memory, no pretending** — plan-gated through `storage.vault_for`; an older PDI without the resident reports "the vault has no memory index" while the words stay sealed.
> - **One pair's memories** — the recall prefix carries the profile *and the interactor*: what Alice told a profile never surfaces in its reply to Bob.
>
> Erasure knows every key from the first one cut: each seal writes a `recollections` ledger row, and the profile-erasure sweep reads its `pdi_key` column — the JIM round's mid-flight lesson applied here before it could recur.
>
> And each research excursion tabulates its ledger row — topic, redactions, whether anything left the host, never the findings — into a `qrme_studies` dataset through the resident's plan door, queryable in the PDI console.
>
> Suite: 3920 passed, 4 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #293 — Release prep 0.86.0

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/293>

> Thirteen manifest-driven version fields (0.85.0 → 0.86.0, build code 85000 → 86000), the CHANGELOG section dated 2026-08-18, the README banner and a release-table row. The cut carries the AR and VR rooms become places to stand in: the AR passthrough stage with deterministic seat anchors, the VR turntable under a drag, and the last thing said riding the stage.
>
> Suite: 3910 passed, 4 skipped over the final tree.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #292 — The AR and VR rooms become places to stand in

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/292>

> The homepage has sold rooms in three presentations since the channels shipped — 2-D, AR, VR — and the room screen rendered all five channels as the same flat grid: the channel was a badge on the way in and nothing inside.
>
> The join answer has always carried the channel; `Inside` reads it now, and the two immersive channels offer a **stage**:
>
> - **AR** — the device's own world-facing camera as passthrough, with every seat anchored over it at a position the seat index decides, so the same room shows everyone the same arrangement. The honest note rides the stage: the passthrough is drawn only for you, nothing of your surroundings is streamed or stored — and a refused camera downgrades to a plain backdrop and says so.
> - **VR** — a scene rendered on this device: a floor grid under a turntable of seats spaced evenly around a circle, each card counter-rotated to face the viewer from wherever a drag leaves the room turned.
>
> Both stages keep the scene's rules — chosen photos, profile portraits with their AI mark, the talking light — and the last thing said rides the stage, so stepping in is not stepping out of the conversation. Entered by a press, left by one, in ten languages.
>
> Suite: 3909 passed, 4 skipped (one environment-flaky widget-sandbox network test verified passing in isolation and on the clean tree; the wall it guards held in the flaky run — status `killed`, nothing reached).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #291 — Release prep 0.85.0

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/291>

> ## What this does
>
> The 0.85.0 cut for QRME, in step with JIM-mini and PDI: all thirteen version fields from `tests/release_fields.txt` (0.84.0 → 0.85.0, build code 84000 → 85000; `cloudgw/api.py` keeps its own 0.2.0, the exclusion the manifest names), the README banner and a release-table row, and the CHANGELOG sectioned to `[0.85.0] - 2026-08-18` with its compare links.
>
> The cut carries the beta round worked end to end across nine merged rounds: the room's full-bleed camera, flip, masks and seat portraits; the spoken voices with every starter and both founder profiles bound at seed; the agent screen as its owner corrected it, with the keyless web search on all four clients; the field-reported fixes from the feed to the blend; the grouped menu and its renames inside and out; Live Now leading with what is live; the chat composer's + ; and `available` finally meaning somebody real answers.
>
> Full local suite: **3910 passed, 4 skipped** over this tree.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #290 — Available means somebody real answers

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/290>

> ## What this round does
>
> - **The no-model state is finally visible.** `llm.available()` is the provider *catalog* — nine rows, configured or not — so `bool(llm.available())` on the studio-agent door could never be false: the beta ran the stub while every screen was told a model was there, which is how "unable to view the simulation" reached the owner as a mystery instead of as a configuration line. `available` now reads the resolved default (`llm.default_name() != "stub"`), so the no-model sentences the screens have carried all along actually fire. Two tests hold it in both directions.
> - **What If wears the state on its face** — when the deployment resolves to the stub, a banner names the missing provider key and who adds it, instead of the stub's apology arriving three sentences into a prediction card. Ten languages.
> - **Two cryptic screen leads** — Lookup's ("Six reads, six different answers…") and Outreach's ("Four different refusals…") — replaced with plain sentences that say what the doors do.
>
> Full local suite over this tree: **3910 passed, 4 skipped**.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #289 — The words inside match the doors outside

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/289>

> ## What this round does
>
> The menu round renamed the tabs; this one walks through the doors:
>
> - **Seventeen screen headers** drop their riddle names for the menu's own professional words — My Space, My Attention, Profile Builder, Tasks, Language & Name, More Tools, Lookup, Live Now, Exports & Licensing, Outreach, Earnings, Permissions, Guest Access, Watermark, Visits, Ad Placements, Tour — in all ten languages, reusing the translations the menu round already carried so console and shells keep agreeing.
> - **The Identity "bubble" card is "Profile picture" now, and it shows the picture** — an 84px circle of the actual avatar (dashed empty circle when unset) in place of an asset path in a code span. The `idn.bubble.showing` row and its usage went together.
> - **The camera-share viewer field offers real profiles** — your own and your friends', by display name — instead of a box waiting for a raw id; the free-text field remains for the person case, which has no listable ids.
> - **The fixed-screen registry gains three kinds** the owner asked after by name: `cast_sink` (AirPlay/Cast), `bluetooth_device`, and `attached_device` (USB/HDMI), all private-side; the picker renders them from the served vocabulary with no console change needed.
>
> Full local suite over this tree: **3908 passed, 4 skipped**.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #288 — The beta round: the room, the agent, the doors, and the menu

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/288>

> ## What this round does
>
> One evening of field reports from the deployed beta, worked end to end across two commits.
>
> ### The room and the voice
> - Room camera goes full-bleed with hidden controls (double-tap / long-press reveals), the lens flips, masks draw on the wearer's own preview, and AI seats wear their profiles' portraits with the mark.
> - `qrme/spoken.py`: a profile binds to a voice made on the engine's own surface; synthesis runs server-side, watermarked, `ELEVENLABS_API_KEY` living only in the host's environment. The socket consults offline mode like every other way out of the host.
>
> ### The agent screen, as corrected
> - The mic **records into the box** (a visible red take, stopped by hand, sending nothing); a drawn waveform button opens the orb voice mode.
> - The three openers do what they say: **Create picture or video** (picker → upload → the send button publishes to the wall with your caption), **Search the Internet** (a new keyless door, `GET /profiles/{id}/search`, DuckDuckGo instant answers — works on a deployment with no model configured), **Write or edit** (the agent's own writing tools).
>
> ### The reported fixes
> - Feed videos resolve hosted footage against the API base (they played only on the wall before).
> - Discover cards open the profile they show.
> - Friends rows wear faces, removal is a small red ✕, and `GET /people` lets beta testers find each other by name or handle — anonymous profiles never match, only active profiles greet strangers.
> - The blend form fits a phone; marketplace chips stay chips under the mobile button floor.
>
> ### Parity
> iOS, Android and Windows each gained the spoken-voice binding (with playback through AVAudioPlayer / MediaPlayer / Windows MediaPlayer), the web search, and the people finder — the per-shell doorless records stay at zero.
>
> ### The menu
> Six named groups behind a grouped sidebar; a top-left drawer on the phone replaces the fifty-six-door bottom bar; two dozen tabs renamed to professional labels in all ten languages. The bottom-bar-coverage guard was rewritten to hold the drawer design by stacking order.
>
> ### The front page
> The README is a professional overview; the full galleries moved to `docs/gallery.md` and the long-form capability sections to `docs/capabilities.md`, with every README guard updated to hold the same promises across the new pages. `docs/beta-deploy.md` gained a "which model actually answers" check for the What If report.
>
> Full local suite over this tree: **3904 passed, 4 skipped**.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #287 — The agent's remit, which was prose in a docstring

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/287>

> The field ask, in its own words: *I wanted to assist users, especially within the app and outside the app, in regards to their issues with their app, synthetic profiles or platform.*
>
> ```
> asked     can somebody get their issue looked at
> mattered  can they find out afterwards what happened to it
> ```
>
> `qrme/privileges.py` opens by saying what this agent is for — not a life-wide companion, that is JIM's shape, but a thing that exists to **get a person's matter resolved**. Every power in that roster is justified by that sentence, and there was nowhere for a matter to live. Three modules answered neighbouring questions and none of them this one: `help` says how the product works and writes nothing, `feedback` takes ideas into a box nobody replies to, `problems` counts what broke, content-free, never knowing whose failure it was.
>
> ## The help box answers first, and settles nothing
>
> Most of what arrives at a support door is a question with a written answer, so a matter opens by putting the person's own words to `help.ask` — the same ladder `jim.noticed` walks next door, free and local first.
>
> The first draft let a recognised question open the matter **already settled**, and the first sentence run through it was *"my card was charged twice on tuesday"*, which came back settled, by help, on the strength of a keyword. That matching is right for what it was built for: an approximately right paragraph costs a reader nothing. The same guess disposing of a billing complaint costs them the complaint, silently, because a settled matter is in nobody's queue.
>
> So a matter with an answer waiting on it stands at `answered` — *here is something, is that it* — and only a person moves anything to `settled`. That holds for a model's sentence too, and the model is why the line has to exist at all.
>
> ## It is raisable by somebody who cannot sign in
>
> *Within the app and outside the app* includes the account somebody has been locked out of, and an issue tracker that requires an account is closed to exactly the people whose issue is the account. A matter may be raised with no principal, and what comes back is a **claim** — one string, shown once, stored as a hash the way `escalation` keeps the waiver's. Nothing else opens an anonymous matter: not being the operator, not knowing the id, not guessing. They are unreachable as a group rather than filtered out of one, so there is no caller a listing could return them to.
>
> ## Nothing here exercises a power
>
> A matter can *name* that one of the roster's powers was used on it and it cannot use one — a support record that could also spend somebody's grants would be a second door onto every power in that roster. No row was added to the roster: the remit did not need a new power, it needed somewhere for the powers there to be pointed.
>
> The guard reads the module's own imports with `ast`. Its first version asked whether the source contained `"from . import research"`, and stayed green when `research` was added to the grouped import this module already had — a guard that only catches the defect written the way its author imagined is a guard for its author.
>
> ## Two more things running it found
>
> - **The queue's default was `open`,** and came back empty on a database holding two matters nobody had answered, because both had gone to `answered` on help's say-so. A support queue reporting *nothing to do* while people wait is worse than no queue; the default is everything unsettled.
> - **The raiser had no way to say *that was not the answer*** except wait for somebody here to notice. They can, it goes back to `open`, and the step stays on the record — a matter answered wrongly once is a different thing from one nobody ever answered.
>
> `help.ask` gained `recognised` for this: `source` could not answer *did this box actually know the question*, because the fallback is as `written` as a real answer is.
>
> ## What the suite found
>
> Five wire names carried two types each, and the guard named all five:
>
> | name | collided with | now |
> |---|---|---|
> | `concerns` | a matter's subject vs the list of subjects | `concern` |
> | `mine` | `feedback`'s list | `my_matters` |
> | `step` / `steps` | the tutorial's | `did` / `trail` |
> | `waiting` | a count elsewhere | `unsettled` |
>
> Plus an interpolated `L10n` key on iOS — invisible to the guard counting English literals behind a translated tab bar, and then read as a key of its own by the guard checking every key a shell asks for, so the four standings are written out one literal at a time; `Pick it up` already carried different translations under `trade.unplace`; two iOS members that do not exist; a console binding nothing called; a screen with no lesson; and `help.DIRECTIONS` with no phrasing reaching the new one, which matters because the help box is the surface most likely to meet somebody who needs this door.
>
> ## Testing
>
> - Full local suite over the final tree: **3850 passed, 4 skipped** (22:01) — +27 against 0.84.0's 3823.
> - New: `tests/test_somebody_says_something_is_wrong.py` (19). The power guard and the shape guard were each watched to fail on the exact defect before being kept; the power one three different ways it could be written.
> - Console typechecks clean; all four shells parse, all four have doors on the eight routes, and each sends `x-matter-claim` where the route requires it.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #286 — Four commands on the deploy page that had never been typed

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/286>

> The 0.84.0 stack came up, all three names answered `0.84.0`, and then the page's own line from § 3 stopped with ten errors naming ten missing variables:
>
> ```
> docker compose -f docker/beta-compose.yml ps
> ```
>
> ```
> asked     does the page have the commands
> mattered  do they run in the directory the page put you in
> ```
>
> ## Nothing was wrong with the stack
>
> Compose interpolates the whole file before it does anything at all, so a read-only subcommand needs the values exactly as much as the one that builds. And it cannot find them on its own: `.env` is at `/srv/qrme/.env`, while compose looks for one beside the compose file it was handed — `docker/` — which is a different directory. `--env-file .env` was on the two `up` lines and on none of the other four.
>
> § 2 makes every variable `${VAR:?}` deliberately, and that is what turns the omission into ten lines rather than a stack started quietly degraded. It is also what makes the failure easy to misread: on `up` it is plainly the guard doing its job; on `ps`, against containers already running and answering, it looks exactly like a broken deploy.
>
> ## They were wrong because nobody had run them
>
> The deploy line is the one anybody types. `ps`, `logs`, `logs caddy` and the restart sit around it and had been read rather than used — the same shape as everything else this page keeps finding in itself: correct prose around a command nobody had performed in the room it is addressed to.
>
> The restart in § 4 was the other half — `docker compose ... restart caddy`, in prose, with the ellipsis standing exactly where the missing flag goes. This page has shipped a described command twice before (*add `.exe` to each*, and *then `exit`*) and both were followed exactly and still failed. It is written out now, in a block, and § 4 says why in one sentence.
>
> § 6 was checked and is clean: it runs `ls -la /root/backups`, not compose.
>
> ## Two guards, both checked by putting the defect back
>
> - every line driving `beta-compose.yml` carries `--env-file`
> - no command inside a fenced block is written with a hole in it
>
> They read the whole page rather than § 7, because which section a command sits in has no bearing on whether it runs. Stripping the flag off § 3's `ps` fails the first; re-eliding the restart fails the second. The prose stays free to name the abbreviation it is warning against — a guard that could not tell those apart would stop the page explaining itself.
>
> ## Testing
>
> - Full local suite over the final tree: **3825 passed, 4 skipped** (22:05). The +2 against 0.84.0's 3823 are the two new guards.
> - `test_the_deploy_page_is_paste_ready.py` goes from 9 to 11, and each new one was watched to fail on the exact defect before being kept.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #285 — Release prep 0.84.0

- merged · opened 2026-08-18 · merged 2026-08-18
- `claude/new-session-ftgm38` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/285>

> Thirteen version fields, driven by `tests/release_fields.txt` rather than a prose checklist, plus the README banner, a release-table row, and the CHANGELOG entry.
>
> ```
> asked     which files does a release touch
> mattered  which fields does a release touch
> ```
>
> `0.83.0 -> 0.84.0`, build code `83000 -> 84000`.
>
> ## The one field a release never touches
>
> `cloudgw/api.py` keeps its own `0.2.0`. That is the exclusion the manifest names in its own words — the cloud model gateway is a separate deployable carrying a separate contract, and `*/api.py` would otherwise match it. A prose checklist of *files to edit* has no way to say *and not this one*.
>
> ## What the cut carries
>
> `[Unreleased]` held one fix, now cut into `## [0.84.0]`: the deploy page's check blocks, where 0.83.0's repair made the step **impossible to perform** rather than merely easy to skip. `ssh host` followed by more lines works because ssh takes the rest as standard input; `exit` followed by more lines does not — the shell tears down and the remainder echoes into a session that is already closing. Getting back to your own machine is a new window, and the guard is inverted to match.
>
> ## Testing
>
> - Full local suite over the final tree: **3823 passed, 4 skipped** (22:48).
> - The release guards in `test_the_files_the_release_never_touched.py` and `test_the_readme_says_what_shipped.py` pass (21).
> - Two environment gaps had to be closed before the suite could report on this diff at all, neither of them a defect in it: the system `cryptography` panicked at collection in 38 files for want of `_cffi_backend`, and `app/node_modules` was absent, so the JSX-text extractor could not run. `npm install` brought only this bump's own two lines into the lockfile — no dependency drift.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_012RuEkwtajFcHEhMxUNPWMN)_

## #284 — A room you could open, walk into, and ask nobody into

- merged · opened 2026-08-15 · merged 2026-08-16
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/284>

> Rooms had a route to open one, a route to step into a live one, a microphone, messages and an advance. None of it got a *particular* person into a *particular* room. The only ways were to name them in the create body — which needs their id before the room exists — or to send them the room id by some means this product does not provide.
>
> ```
> asked     can I open a room
> mattered  can I ask somebody into it
> ```
>
> ## The invite is the inbox event
>
> There is no invites table. `kind` is `room_invite` and `ref` is the room, so the row the person reads and the row `accept` checks are the same row. Two records of one fact is how a withdrawn invite stays acceptable, and how an accepted one still shows as pending.
>
> ## Both halves, or neither
>
> An invite with no acceptance is a notification, and `join` seats *interactors* — so an invited profile could read that it had been asked and have no route to say yes. The accept is authorized as the **guest**: a host who could seat somebody from their own screen would make "invite" a word for something that is not one.
>
> ## Also fixed
>
> The inbox join reached only the `profiles` table, so a person who invited you arrived as a bare id. It now falls back to `interactors`, and the test asserts the name rather than the shape.
>
> ## Doors
>
> A friend picker and an Ask button on each live room, and the accept on the invite row in the guest's own inbox — the only place it can be pressed. Eight l10n rows in ten languages.
>
> ## Tests
>
> `tests/test_a_room_you_cannot_ask_anybody_into.py` — 11 cases: the round trip, who may ask (in-room only, either participant kind, 401 unidentified), who may accept (guest only, and not without an invite), what a second press does (idempotent both ways), and the room's own state (closed 409, departed profile 410, already-in-room 409).
>
> The full local suite has not yet been run over this tree.
>
> ---
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #283 — The briefcase: read once, and still there on the next turn

- merged · opened 2026-08-14 · merged 2026-08-14
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/283>

> A link pasted into a turn was already fetched and read — `interaction.py` pulled the first URL out of the message, visited the page through the same offline-gated fetcher every outbound path uses, and put the visible text into *that turn's* system prompt. It worked, and then it evaporated: the next turn, the one where you actually discuss the thing, carried no page at all. Keeping the conversation going meant pasting the link again, and every paste re-fetched the whole of it and re-sent the whole of it.
>
> ```
> asked     can the profile read what you hand it
> mattered  can it still remember it on the next turn
> ```
>
> And a link was the only thing you could hand over. A photograph, a filing, a spreadsheet, a video — the material a conversation is usually *about* — had no way in.
>
> ## What this adds
>
> `qrme/briefcase.py` reads what is handed over at import, distils it **once** into a digest capped at 700 characters, and it is the digest every later turn carries. A forty-page filing enters the prompt at the size of its reading, paid for a single time instead of on every turn. `chars` beside `digest_chars` on every row is that claim made checkable.
>
> Keyed on the pair `(profile, interactor)`, not on the profile. A `source_items` row is what a profile recalls as its own and every visitor sees it; this belongs to the two people in the conversation and stays there — the line `persona.build_system_prompt` already draws around a clinician's notes, for the same reason.
>
> Extraction: pages through `scrape`, plain text as itself, PDFs through their text layer (Flate-decoded content streams), `.docx`/`.pptx`/`.xlsx` out of their XML, and an unknown archive as a listing rather than an invention.
>
> | route | for |
> | --- | --- |
> | `POST /profiles/{id}/briefcase/link` | a page, read through the offline gate |
> | `POST /profiles/{id}/briefcase/file` | raw bytes; the kind is read from the bytes, never the name |
> | `GET /profiles/{id}/briefcase` | what this conversation is carrying |
> | `GET /profiles/{id}/briefcase/{item}` | the text that was actually extracted |
> | `DELETE /profiles/{id}/briefcase/{item}` | stop carrying it, from the next turn on |
>
> Doors on the console, iOS, Android and Windows — the odd-client-out guard is green.
>
> ## What it refuses to pretend
>
> This deployment has no eyes, and a scanned PDF has no text layer to find. A photograph, a video and a scan import anyway, carrying whatever the person said they were, with `was_read` 0 and a second prompt block that states the profile has **not** opened them and must not describe or summarise anything in the list. A profile inventing the contents of a picture it was handed is worse than one asking what is in it.
>
> ## Three things the guards found, fixed rather than recorded
>
> - **The stub would have become a digest.** It no longer performs a character — it explains itself — so storing its reply would have put a sentence about this software into the prompt under somebody's document title, and reported its length as theirs. `distill` checks before the call and after it, since `FallbackProvider` degrades silently and only `answered_by` says who wrote the text.
> - **`prf.bc.remove` said "Take it back"**, which three other keys already carry with different translations behind them. Reworded to "Stop carrying it".
> - **The l10n generator ate `prf.theirs`** on Android and Windows: its first pattern consumed a trailing newline it never put back, joining two rows onto one line, and the dedupe pass then read the joined line as one row and deleted it whole. Restored. A regex is not a parser.
>
> ## Also
>
> Enter sends on somebody's homepage (Shift+Enter still breaks the line), and the button that read "Talk to their profile" — a description of the screen rather than a name for the act — says **Send**, in all ten languages.
>
> ## Tests
>
> `tests/test_the_briefcase_is_read_once_and_carried.py` — 22 cases covering extraction per kind, the unread flag, pair scoping, the caps, and that the block carries the digest rather than the document. Full local suite result reported separately before any merge.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #282 — Their homepage: where pressing a face actually takes you

- merged · opened 2026-08-14 · merged 2026-08-14
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/282>

> From the beta, four screenshots of Top Friends. Pressing a friend's picture opened a panel with their name and their tagline in it, and underneath that the *signed-in* profile's memory count, engagement average, moderation pass rate, persona and chat button. Only the header was ever theirs, which is why all four looked the same.
>
>     asked     does pressing a face open something
>     mattered  is what opens theirs
>
> ## The screen
>
> `app/src/screens/Profile.tsx` is what a face now opens. Their page as they built it — theme, accent, about, links — their Top 8, which are eight more doors so the walk continues and Back retraces it rather than dropping you where it started, their wall, their photographs, their footage, and the three things a visitor may actually do.
>
> Every read on it is a route that was already public: this is what a visitor came to look at. A synthetic profile has the same homepage — here a friend *is* a profile, so this is one screen and not two.
>
> **No stats row, and the absence is the fix.** `GET /profiles/{id}/stats` is `require_owner`: somebody else's memory count is not readable and should not be. That gate is exactly how the old card came to be showing yours in place of theirs — it had nothing of theirs to draw, so it drew what it could reach.
>
> **Their markup renders in a frame with `sandbox` empty**, not in this document. `pages.py` sanitises on the way in and does it well; this is about who pays if that is ever wrong. React's escape hatch is a floor at zero in this repo precisely so that decision has to be made rather than reached for, and being the screen that finally wanted it is not a reason to move the floor.
>
> ## The upload door had nothing on the other side of it
>
> Photos and Videos would have been two buttons with no query behind them. Uploads have been accepted since 0.42.x and could be found only through the wall post they happened to ride on, so a photograph posted a year ago was in practice gone, and one attached to nothing was invisible from the first second.
>
>     asked     can somebody put a photograph here
>     mattered  can anybody find it afterwards
>
> `media.gallery` and `GET /profiles/{profile_id}/media`: newest first, narrowing to image, video or file, public like the wall it appears on.
>
> ## Two things driving found
>
> **A room could not be opened without a topic.** `RoomCreate.topic` was required by that one line and optional by every reader around it — `create_room` writes it straight through, the rooms list declares it nullable, and the console has always sent nothing when the field is left blank. Pressing Open on the Rooms screen without typing a topic answered 422 "Topic — Field required", on a form that offers the topic as a blank you may skip.
>
> **Messaging is mutual.** `_are_friends` requires both edges on purpose — "consent that only one person can end is not consent" — so a Message button on a stranger's page always fails, and one drawn the moment *you* add *them* still fails, which is worse because it looks like it should have worked. The screen reads both lists and shows the one control that is true: add them, wait for them, or write.
>
> ## Also
>
> `suite/smoke.py` asserted a plan gate that JIM stands down for the beta. It read the 402 as fixed and died seven steps in reporting a specialist that "does not accept delegated work" — which reads as the tandem coming apart rather than as a flag having moved. It now reads the posture off `/plans` and asserts the branch in force.
>
> ## Checks
>
> - Nine new tests over the gallery and the topic-less room.
> - Every read and every action driven end to end over HTTP as a visitor with no token, including all three friendship states and both refusals.
> - Console typechecks and builds.
> - Screen drawn at 197; README says what it is.
> - Full local suite running over this tree — result will be reported before merge.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #281 — The Studio: a box for somebody's own code, an agent that writes it, and the Feed as a deck you swipe

- merged · opened 2026-08-13 · merged 2026-08-13
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/281>

> Three slices from one conversation: a place for people to write their own code without reaching anybody else's, an agent that writes it for them, and a Feed that behaves like a feed.
>
> ## `eea0950` — the box a person's own code runs in
>
> A widget is a function somebody wrote, stored against their profile, run on demand against their own data. This commit is only the box, because everything else in the round rests on it holding.
>
> **Why not a shell.** The obvious way to give somebody coding access is a shell. This deployment cannot offer one, and the reason is not caution in general — it is what sits on the machine. The same host holds JIM-mini's clinical captures and money-guardian statement files, PDI's tenant vaults, and every profile's remembrance of every conversation. A shell handed to whoever signs up reads all of it, through a door the tenant-isolation guards were written to make impossible.
>
>     asked     can a person run their own code here
>     mattered  can a person run their own code without reaching anybody else's
>
> **Four walls, each a mechanism rather than a policy:**
>
> | attempt | held by |
> |---|---|
> | `fetch("https://example.com")` | `unshare -rn` — a namespace with no interfaces |
> | `readFileSync("/etc/passwd")` | node's permission model, one directory admitted |
> | the database, by name and by path | same |
> | `child_process.execSync("id")` | same — the escape that would void the rest |
> | reading `process.env` | an environment holding nothing this process knows |
> | `for(;;){}` | `RLIMIT_CPU` |
> | a held-open timer | wall-clock kill |
> | allocate forever | V8's own heap cap |
> | return 2 MB | byte cap on what may be rendered back |
>
> Interpreters are resolved to absolute paths in the parent and exec'd by path, so the child cannot be steered into a different binary by a search order it can read.
>
> **The refusal that matters.** If the network cut cannot be built — an unusual kernel, a container without user namespaces — the runner refuses to run anything at all rather than running with three walls instead of four. A sandbox that quietly degrades still looks like a working feature, and nobody learns otherwise until the day it matters.
>
> **Two failures this already had**, both kept in the file because they are the interesting kind:
>
> - `RLIMIT_AS` at 256MB killed node before it ran a line. V8 *reserves* gigabytes of address space at startup and touches almost none of it, so a cap sized like a memory budget is not a small budget — it is a refusal to start, arriving as `killed` on every widget including the ones that add two numbers. The heap is capped by `--max-old-space-size` now, which fails inside the child as an error its author can read.
> - A widget holding a timer open hits the wall clock; a widget returning a promise that never resolves holds nothing open, so node exits in forty milliseconds with no answer. Reading the second as a timeout teaches the runner to wait five seconds for a child that has already gone; reading it as success hands the console an empty value as though something were returned. One is a clock, the other is somebody's forgotten `resolve`, and the reader is told which.
>
> `test_the_widget_cannot_leave_its_box.py` — sixteen escape attempts written the way somebody would actually write them, each run through the real runner. Nothing asserts on the runner's own configuration: a guard that reads the sandbox's settings and agrees with them proves only that the file is self-consistent.
>
> ## `1f947b0` `de2916f` — the agent that edits somebody's own app
>
> An owner's token can call anything the owner can call. That is a true statement about authority and a terrible one about design, because the owner can also end their profile, and nobody typing *make my page darker* means *and be free to end me if you misread it*.
>
> So the reach is a list — `qrme/authoring.TOOLS`, ten rows, each naming the door it goes through and carrying a sentence written for the person deciding whether to allow it. Two guards make the list load-bearing rather than decorative:
>
> - every row resolves against the app's own route table, and every row that **changes** something must land on a door that demands the owner;
> - the profile is bound from the session by `call` and is never the model's to name — so a model answering `{"profile_id": "<somebody else>"}`, because it was asked to or because it read those words in a page it had just been handed, does not move the request off the person driving it.
>
> Reads are exempt from the first guard on purpose, and the second is why that is safe: `GET .../page` is what a visitor sees and has no owner to demand.
>
> **The executor makes the request rather than calling the module behind the route.** The door is where `require_owner` lives, where the plan is checked, where a contested profile goes quiet and where the refusal is translated, and an agent that reached past all of that would be a second, weaker copy of the product. The caller's own credential is forwarded rather than exchanged for something broader, so the agent's reach is exactly the reach of whoever is driving it — and expires with theirs.
>
> **What it is never told is the host**: not its name, its paths, its environment or its sibling services. Every person who signs up drives one of these, on a machine that also holds other people's clinical captures and vaults. A guard reads the prompt *and* every sentence written for a person, because a leak is as likely to arrive in prose.
>
> `test_the_agent_does_what_it_says_it_did.py` drives the whole loop against the real doors with a scripted model, because the one way a reply and a record come apart is the way that matters: a model is perfectly capable of writing *I've made your page darker* having called nothing at all. Every assertion reads the record.
>
> On the screen, what it did is listed under what it said — one line per door it went through, refusals included. `GET /studio/agent` publishes the ten sentences so *what can this thing do to my account* has an answer somebody can finish reading before pressing anything. The conversation is the client's to keep: the agent has no memory of its own, no table, nothing to leak — which is both cheaper and the design where *forget this* is a button that actually forgets.
>
> Four clients, ten languages each. Three wire-name collisions the phone guards caught on the way through, all mine, all renamed rather than recorded: `limits` (already a list of sentences about a signature tier) became `allowances`; a step's `status` (an int, against `status` the string everywhere else) became `answered`; `steps` (against the tutorial's `TutorialStep[]`) became `acted`.
>
> ## `ec830d1` — a deck you swipe, not a card with a Next button
>
> From the beta, on a phone: opening the Feed showed a card with a Play button, Previous and Next, and a video filling part of it.
>
> The Feed is now a deck. One item fills the screen, a swipe up brings the next, and the snapping is the browser's own — `scroll-snap-type: y mandatory` with `scroll-snap-stop: always` — rather than a gesture handler guessing at intent from a wheel delta. Vertical footage fills the frame; horizontal is centred with `object-fit: contain`, which letterboxes rather than cropping somebody's video into a shape they did not shoot it in.
>
> **What plays by itself, and what waits.** Footage this deployment holds plays the moment its pane is in front of you, muted, and only that pane gets a decoder. Footage held elsewhere does not: the feed prints a sentence about itself — *"It stays a card until you press play, so scrolling past it tells them nothing"* — and auto-rendering an embed as it scrolls into view makes that sentence false. So an elsewhere item is a **full-frame** facade with one centred play: the same size and the same swipe as everything else, and it waits.
>
>     asked     does the feed feel like a feed
>     mattered  does scrolling past something tell anybody
>
> **The switch**: `feed.autoplay`, off by default, its own line saying what turning it on costs, in ten languages. Kept on the device rather than on the profile — this is a fact about what this browser fetches, not about who somebody is.
>
> ## `840b77d` `cd6c1d6` — what the gate found
>
> Six defects, surfaced by the suite rather than by review, and all of them mine:
>
> - **A memorial that redecorates.** `authoring_turn` and `run_widget` drove a profile without asking whether it may still act. The turn takes `require_may_publish` — the page this agent edits is a public face, and a profile restricted pending an objection review is not putting new work in front of the person contesting it, whether a person typed the change or a model did. The run takes the narrower `require_may_speak`: a widget's answer goes to its author alone, so a contested profile may still run its own code; a terminated one does nothing.
> - **A parser that stopped seeing.** The whole `studio.*` block in `l10n.ts` was written single-line in a file whose entries are multi-line, and the console's table reader matches `"key": {` … `^  },`. Each single-line entry therefore swallowed everything up to the *next* multi-line entry's closing brace, and `feed.autoplay` fell out of the table it was supposed to be audited in — the Feed's own switch had been invisible since the deck landed. Thirty-six rows rewrapped; `declared == set(table)` is exact again.
> - **Android's widget bindings** were top-level extensions in a file of 463 class members, which put every key they read under `/studio/limits`. **Windows** reached for `state.Api` and `state.ProfileId`, which are `ApiClient.Shared` and `state.Pid`. The Compose screen asked the theme for a colour it does not have.
> - **`said` and `history`** — the two fields the agent's form asks for — name themselves on a refusal in ten languages instead of arriving as identifiers.
> - **Screen 196.** The undrawn ceiling is zero, so Widgets is drawn: the box first, because *write your own code here* only means something once somebody knows what the code cannot reach; the agent second, with its steps under its prose for the same reason. A README gallery row, a *Your own tools* lesson at the end of *Being yourself* (a new chapter would have broken the ordering invariant rather than teaching anything), the helper's plain phrasings, and the row count in `ui_screens.txt` corrected from 57 to 58.
>
> ## Tests
>
> **Full local suite green over `cd6c1d6`: 3421 passed, 2 skipped** (up from 3396 at the sandbox slice). Console typecheck clean.
>
> ## Not done here
>
> The merge and the version cut are David's call, and the tag is his step. Nothing on the live sites changes until the VPS deploy.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #280 — Five phone sessions' field reports: curation, QR export, room scene, stranger roulette, plain words, and error reports that come home

- merged · opened 2026-08-13 · merged 2026-08-13
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/280>

> Twenty-seven commits from five phone sessions on the beta — every one answering something you hit, asked for, or that the session exposed — plus the guide catching up, the untranslated count reaching zero, the dead-keys backlog run from 273 to a 28-row ledger, and a field report on a sibling product that changed how every screen in this repo is read.
>
> ## `cd370c5` — three field reports from one phone session
> The green `✓ real photo` pill was swallowing the Discover portrait (font-boosting inflated it; it now sits under the photo and boosting is pinned off). Marketplace chips were full-size buttons with their effect below the fold. The minimized agent light is a small translucent dot instead of a green disc parked over content.
>
> ## `c6811fe` — the console&#39;s own policy was blanking every video player
> &#34;It seemed to attach the video but it&#39;s not playing&#34;: the console&#39;s CSP named no `frame-src`, so it fell back to `default-src &#39;none&#39;` and the browser refused **every** allowlisted player as a white rectangle — live host only, invisible to every test. `frame-src` now derives from the platform allowlist itself, with a socket-level test binding the two.
>
> ## `4097c76` — the checkboxes and the pen: curating the transcript by hand
> `POST /memory/{interactor}/strike` deletes turns selected by id (scoped to the pair); `PUT /memory/{interactor}/turns/{id}` rewrites one turn — new words face moderation, a profile turn&#39;s synthetic-media credential is dropped, the edit is recorded as a fact but never the old words. Console gets Edit mode/checkboxes/delete-selected/tap-to-rewrite; all three shells get the same doors.
>
> ## `6de4dcf` — the room is a scene, and the wall&#39;s boxes are blank
> Inside-a-room renders the seats as tiles above the transcript, person/profile marked apart, the last voice wearing the lit border. The Wall composer&#39;s ghost placeholder text is gone.
>
> ## `24eff36` — the second phone session: six reports, six answers
> Tab changes land at the top of the new screen; Blend candidates show blurb + tags and gain search; What-If past runs open on tap; &#34;Show the prompt&#34; shows it inline; and **Export via QR**: a single-use ten-minute ticket, the QR carrying the ticketed URL and *never the owner token*, the bundle served exactly once.
>
> ## `fe23610` — three more phone sessions: the roulette, the plain words, and the reports come home
> The stranger pool stopped stranding the waiting side; `POST /v1/problems` lives on this backend with `GET /v1/problems` behind `QRME_PROBLEMS_KEY`; fields that asked for pickers got them; words reworded ×10 languages; Control Center says true things plainly; Home stopped lying by staleness; connectors offer &#34;All of the above&#34; as a list, not a wildcard; the exchange lifecycle is driven end-to-end in one test.
>
> ## `7ef0ef3` + `1b3e5b8` — what the full gate found in its own guards
> The member-guard&#39;s Kotlin reader learned nested classes are members; Windows&#39; dead `prob.server` row wired; three floor records re-pointed.
>
> ## `49d4fa6` — the guide catches up with the evening
> The curation lesson, the problems retrieval half, the stranger-roulette and identity-handoff sentences enter the tutorial and help index.
>
> ## `6b7cb00` — the untranslated count reaches zero: 2/2/3 → 0/0/0
>
> ## `d851b57` → `7a2fb04` — the dead-keys grind: 273 → 28, and the 28 are a ledger
>
> - **Real English over dead translations, family by family**: iOS packs&#39; Sync/Synced/FREE/Buy were English ternary tokens invisible to the tabs guard; **Android&#39;s chat role chips were hardcoded English pairs over four translated rows**; Android&#39;s relationship chips showed raw slugs while holding all seven translated; Windows said &#34;engine:&#34; over a translated `ns.tr.engine`.
> - **Sentences one shell never said**: the desktop&#39;s signing page gains the hashed-into-the-challenge privacy sentence both phones show; its attest button answers instead of reloading silently; its Reach page tells a profile-less user to create one instead of throwing; Android&#39;s problem-report card gains &#34;counts of what failed, never what you typed&#34;.
> - **One mis-wiring**: the desktop&#39;s desk note box had &#34;need a key cut&#34; as its placeholder — a different sentence in the wrong slot, unwired and deleted.
> - **What stays (28 rows) is a ledger, not a backlog**: fixture rows the parse probe and block guards are built on, read at full strength on every shell.
>
> ## `15d0c28` → `7b574f3` — the guard-divergences backlog, 136 → 121
>
> The record of guards two of the three products carry and the third does not, byte-identical in all three repositories. Twelve rows resolved by porting the *questions* rather than the names; then PDI gained the README-arithmetic guard (which found a hosting claim of 16 against 25 real tests) and the custody guard — which found that the vault, of all three products, never said that holding data is not owning it, nor that a data subject&#39;s statutory rights survive the arrangement. `shared_guards.txt` 469 → **489**.
>
> **The apology for a failed route (`6887ef7`).** Porting `test_every_handler_returns_through_the_one_place` into this suite — a guard PDI and JIM-mini have carried since they grew one `i18n.refuse`, and this product never had because it answers refusals a shape of its own — exposed what none of the three suites was asking.
>
> Every exception handler here answers in the reader&#39;s language. The catch-all does not, and could not be caught by that guard, because the catch-all is not a handler: `@app.exception_handler(Exception)` goes to `ServerErrorMiddleware`, outside the CORS layer, so the 500 comes back without the header and the console reads it as *unreachable* rather than *refused*. It has to be a middleware — and being a middleware, nothing was asking it anything. Its sentence sat inline in English in **all three products**:
>
>     "Something went wrong on our side. Nothing you sent was recorded."
>
>     asked     does every exception handler answer in the reader's language
>     mattered  does every failure answer in the reader's language
>
> The one answer every route can give is the one a person meets when the product is already failing them, and it was the only one that came back in a language they might not read. `i18n.SERVER_ERROR` is a named constant with its row in `_REFUSALS` in nine languages, and the middleware reads the reader&#39;s language the way the handlers do. `test_every_failure_answers_in_the_readers_language` asks the catch-all directly in all three suites, matching a middleware whose `except` names `Exception` or is bare — proven failing against the sentence it replaced.
>
> ## `3ec04d5` + `9a21b8b` — nine English buttons the widened reader found on the stranger&#39;s screen
>
> A field report on PDI — **&#34;It seems to be blocking the PDI menus&#34;** — began with a status pill sitting on a phone&#39;s tab bar and ended in this estate&#39;s text extractor.
>
> `{busy ? "Creating…" : tr("onb.create", visitorLang())}` is a `ConditionalExpression`, not a `JsxText` node. Half of that line was translated and half was English, and the reader behind every count in this repo saw neither.
>
>     asked     what text does this file place between its tags
>     mattered  what words does this screen put on the glass
>
> `scripts/jsx-text.mjs` now reads string literals in child position — both branches of a ternary, either side of `&&`/`||`/`??`, the pieces of a concatenation — skipping any literal with no letter in it, and still refusing call arguments so a translation key stays a key.
>
> What it found first was the screen a stranger meets: Show/Hide on the password field and its aria-label, Creating…, Checking…, Signing in…, Resetting…, Verify &amp; continue, Set new password, Create My Profile — rows entering the table in ten languages, every site selecting the *result* rather than the key. `9a21b8b` is what the full gate then said about them: three carried English the shells already hold under other keys, with the two tables disagreeing in some language. Reconciled onto the phones&#39; wording; the third was a collision of senses — the password toggle&#39;s bare *Show* met `trade.show` (*Ver*, *查看*, &#34;view a trade&#34;) — so the toggle now reads the password-specific rows it already had for its aria-label.
>
> ## `2f8ab09` — the stylesheet is read here too
>
> The guard that came out of that field report — nothing fixed to the bottom of the viewport may cover the tab bar, and a minimized light must actually be small — now runs in this console. The behaviour was already right, after your own report about the agent lights and the help bubble. What was missing was the question.
>
>     asked     was this fixed once, on the screen somebody reported
>     mattered  does anything stop it happening again, here
>
> Porting it repaired the reader: this stylesheet opens the mobile media query more than once, deliberately, so the corner widgets win the cascade from the bottom of the file — and a reader that took the first block would have measured a rule a later block overrides.
>
> ## Tests
> **Full suite green over the final tree: 3380 passed, 2 skipped** (gate over `7b574f3`; the second skip is the debt-ratio guard standing down as designed). `native_screens_untranslated.txt` 0/0/0; `native_dead_keys.txt` 273 → 28; `guard_divergences.txt` at 121 with `shared_guards.txt` at 489.
>
> Schema: new tables only (`message_edits`, `export_tickets`, `problem_reports`).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #279 — Watch parties take the link you paste, go public on the live surfaces, and reach the phones

- merged · opened 2026-08-12 · merged 2026-08-13
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/279>

> Six commits, three field reports answered, fully gated (3343 passed over the final tree) and driven live end-to-end against a running server.
>
> ## What's in the stack
>
> **`8899b6d` — docs: the guide catches up with 0.67.0 and 0.68.0**
> The in-app guide learns the features that shipped around it: help topics and lesson prose for account memory and named forgetting, the steering lock, character-card import, and conversation rehearsal. README rows to match.
>
> **`fe9a140` — the watch party takes the link you paste** (field report: "I just tried to start a watch party with a YouTube link — this feature doesn't work")
> `POST /watch-parties` now accepts `video_url` — a pasted link goes through the same `embeds.parse` platform allowlist a wall post's video faces, and the video hangs off the party's own id in `post_videos`, so no fabricated post ever surfaces on a wall. A URL pasted into the `post_id` field is met too. The unknown-id refusal now names what's actually wrong and suggests pasting the link. Console sends `video_url` when the field is a URL.
>
> **`dc82dde` — a party the host chose to be found** ("make it public, posting on the public wall/feed/room/desk" + "IDs should be for just jumping into specific rooms or private rooms")
> Parties are private by default. `POST /watch-parties/{id}/listing` (host-only, title required, strict moderation on the title) opens the browse door: a card on `GET /watch-parties/public` (tokenless) and on the feed's first page — counts and the video facade only, never member names. The id stays the private jump-in door either way; publishing never weakens the members door. Announce-on-wall lets the host post the party to a wall by hand.
>
> **`75de586` — two guards meet the browse door**
> The two-party auth sweep learns the deliberately public route (`OPEN` allowlist with rationale), and the iOS English-behind-tabs ratchet is satisfied by precomputing a card label instead of interpolating.
>
> **`f1dfd61` — joining from the feed lands you in the room**
> Console feed renders the party card and its Join button joins then opens the party screen; the announce row on the party screen posts to a wall.
>
> **`bf73a9b` — party cards reach the phones**
> iOS, Android and Windows shells all decode feed kind `"party"` (title, platform, people count, joining note) and join from the card; the party screens gain the public browse list and publish/unpublish buttons. Chrome strings ×10 languages, byte-matched across the three shells' tables.
>
> ## Proven against a running server
> Drove the whole loop over HTTP on a scratch DB: paste-URL start (YouTube allowlisted, `public: false` by default), publish refused without a title (the exact refusal shipped), publish with title, tokenless `GET /watch-parties/public` returns the counts-only card with a join door, a second profile joins from the card, and the feed's first page carries `kind: "party"` with `counts.party: 1`.
>
> ## Tests
> Full suite green over the final tree: **3343 passed, 1 skipped**. Thirteen new watch-party tests (URL start, allowlist refusal, no fabricated post, profile blindness unchanged, publish/unpublish, host-only, title gates, delist on end, feed ride) plus the auth-sweep allowlist entry.

## #278 — Cut 0.68.0 — the shortlist ships

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/278>

> Release cut: thirteen version fields to 0.68.0, README banner + table row, and the CHANGELOG entry covering the research program — the memory door, the steering lock, character-card import, rehearsal rooms that forget on purpose, plus the identity-camera fix and the memorial/rehearsal gate.
>
> Full suite gate running; merge follows on green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #277 — R47+R48: character-card import + rehearsal mode

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/277>

> The last two rounds of the research program.
>
> **R47 — character-card import.** `qrme/cardimport.py` reads chara_card_v2/v3 cards as raw JSON or embedded in a PNG's `chara`/`ccv3` text chunk (pure chunk-walking, no image library) and maps what a card honestly is — name, described identity, greeting, example dialogue — onto QRME's profile shape via `POST /profiles/import/card`, through the same creation path as every other profile. The card's texts land as source material with honest provenance. What it refuses, it names: `system_prompt`, `post_history_instructions` and jailbreak blocks are harness instructions, not identity — withheld item by item in `withholdings`, the license manifest's honest shape.
>
> **R48 — rehearsal mode.** `POST /profiles/{id}/rehearsal` opens a room whose transcript lives only in the room, only until it closes; `/say` plays the counterpart in the named scenario and marks every reply `remembered: false`; `DELETE` wipes row and transcript together. Nothing said inside ever reaches messages, engagement or the remembrance — proven by test.
>
> Doors on all four clients for both rounds (console, iOS, Android, Windows), `nw.card` / `cht.rh` rows ×10 languages, `cht.rh.open` aligned to `party.start`'s existing wording, three rehearsal refusals translated.
>
> Full suite gate running; merge follows on green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #276 — R46: steering lock — the personality nobody can move

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/276>

> R46 from the research shortlist: the steadiest fear about personas is drift — a personality that moves under your hands or somebody else's. The lock answers it literally.
>
> - **`steering.lock` / `unlock` / `lock_of`** + `steering_locks` table: while a lock row stands, `set_dials` refuses outright — the owner's own slip, a compromised session, and any future automation all hit the same wall. The refusal speaks all ten languages and rides status 423.
> - **`POST /profiles/{id}/steering/lock`** (optional reason, owner-only) + `DELETE` to unlock. The lock shows at both read doors (steering + hub), and every write path that reaches `set_dials` — steering PUT, hub PUT, robot steering PUT — answers 423 while it holds.
> - Doors on all four clients (console Workshop card with sliders disabling, iOS SteeringPanel, Android hub panel, Windows SettingsPage) with lock rows ×10 languages, wording byte-matched across tables.
> - Tests in `test_the_personality_nobody_can_move.py`.
>
> Full suite gate running; merge follows on green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #275 — R45: the memory door — what it remembers, and forget that one thing

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/275>

> R45 from the research shortlist: the most consistent trust ask — see what a persona holds about you, and correct it surgically instead of burning the whole friendship with erase-all.
>
> - **`GET /profiles/{id}/memory/{interactor}/account`**: "what do you remember about me", answered from the records rather than by generation — the distilled paragraph as it stands, how many turns were folded into it, how many are still in the recent window, first/last contact.
> - **`POST /profiles/{id}/memory/{interactor}/forget {about}`**: the scalpel — every turn whose text carries the words is deleted, and the distilled remembrance is dropped so it re-folds from what remains, never from what was struck. Empty words 422; unremembered words 404.
> - Both doors answer to owner or interactor, like the transcript and remembrance views beside them.
> - Doors on all four clients (console Memory screen, iOS RecordView, Android MemBlock, Windows PeoplePage) with `mem.account` / `mem.forget` rows ×10 languages, wording byte-matched.
> - Tests in `test_the_memory_door.py`.
>
> Full suite gate running; merge follows on green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #274 — Fix identity camera never rendering after permission grant

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/274>

> Field-reported beta bug: the facial-capture flow (forward / left / right / down / up) asked for camera permission and then rendered nothing.
>
> **Cause**: the stream was attached to the `<video>` element inside a `requestAnimationFrame` callback that raced React's commit of the conditionally-rendered element — when the frame fired before the element existed, the stream was never attached and the preview stayed black.
>
> **Fix** (`app/src/screens/Identity.tsx`):
> - Hold the `MediaStream` in a ref and attach it from a `useEffect` keyed on the capturing state, with an explicit `play()`.
> - Unmount cleanup stops all tracks so the camera light goes off when leaving the screen.
> - `stopCapture` clears `srcObject` and releases tracks explicitly.
>
> `tsc` green; full server suite gate running before merge.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #273 — 0.67.0: cut in step

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/273>

> The thirteen fields the release checklist names, the README banner and table row, and the CHANGELOG entry. This round the substance was QRME's: licences that carry the profile's knowledge and dials under a manifest, organizations leasing licensed specialists, the portrait that moves with its history, and the persona that remembers the room. The three products are cut together, so one number names one combination of all three. Merges on green suite.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #272 — The licence carries the substance — four patent rounds (R33–R36)

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/272>

> Four rounds from the patent-portfolio gap analysis, plus the guard-fix round the full suite demanded. Re-gate in progress; merges only on green.
>
> **The licence carries the substance (R33).** A finetune or clone derive now hands the buyer the profile's substance — its own knowledge items, steering dials, appearance and demographics; a clone adds an aggregate adaptation summary (dimension means across every relationship, count only). What may never travel stays behind by rule: interactor messages and per-relationship embeddings, the voice print, vaulted content, and marketplace pack items. Every derivation writes a manifest — `carried` / `withholdings`, each withholding with its reason — in the same transaction, returned to the buyer and readable on the owner's grants list. Console and all three native shells show it.
>
> **AI for lease (R34).** `POST /organizations/{org_id}/lease` seats somebody else's consult-licensed specialist as a department: the fee accrues to the specialist's owner at seating time, the lease rides the owner's licences list beside grants, and the same revoke door covers both. A revoked lease — or a terminated source profile — leaves the department standing but silent, named in every coordination it no longer speaks in. Doors in all four clients.
>
> **The moving image (R35).** The avatar response carries a motion block — style (still / breathe / lively via the existing PUT avatar door), energy and warmth derived live from the latent persona embeddings, a tempo the clients animate at. Derived, not stored, and riding the same response as the AI badge and likeness record, so nothing can animate the face without holding the disclosure.
>
> **The room is remembered (R36).** Environment context was stored and rendered into the prompt but never read back. Now a turn without fresh environment recalls the latest stored context (six-hour window), the prompt treats it as likelihood rather than certainty, and the echo marks it `remembered`.
>
> **Nine guards answered (fix round).** The full-suite gate flagged nine things and was right about all of them — including a real defect: termination now revokes an organization's lease along with every other third-party capability.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #271 — 0.65.0: the rooms keep their word, and the three cut together

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/271>

> Two commits: Round 30, then the 0.65.0 cut.
>
> **A standing room is one place, not a stamp.** Pressing a standing room's name used to mint a fresh copy of it — twelve presses of "The front porch" made twelve empty porches. `POST /rooms/templates/{key}/open` now joins the newest live room holding that topic when one has a free seat (or already holds you), and only opens it fresh when nobody has it open — with you and your profile in it. A full porch gets a second table: when all eight seats are taken, the next press opens the room again. The response says which happened, unknown keys and profile-less fresh opens are refused in ten languages, and the console, iOS, Android and Windows each press through the door.
>
> **A face is a door to the person.** Tapping a friend's picture on the console's home screen landed on the list of friends; it now opens that friend's own page as a visitor sees it — portrait, tagline, about, links — with a translated Close. Reported from the field, fixed the same day.
>
> **The cut.** The thirteen fields the release checklist names, the README banner and table row, and the CHANGELOG entry — the same cut in jim-mini and pdi, so the three products stand at one version.
>
> Full QRME suite green over the final tree: 3303 passed, 1 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #270 — The door into a live room

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/270>

> The audit that opened this round found the sentence before the field did: the standing rooms shipped saying "press one and you are inside with your profile, and anyone else can join" — and participants were frozen at creation. No join route existed. The live list showed rooms with their heads counted and no way in. A claim without behavior, one evening old and already tagged in 0.64.0.
>
> This is the behavior:
>
> - `qrme/routers/community.py` — `POST /rooms/{room_id}/join`: the token names the joiner (a room id rides on beacons and printed stickers, so knowing it cannot stand in for being a person); joining twice is being there once; the table seats eight, the same number the create form holds, because a limit that differs by door is two limits
> - `qrme/i18n.py` — the closed-room and full-room refusals in ten languages
> - Console — the live list's rows grow a Step-inside button that joins and lands you on the Inside screen with the room open (`Rooms.tsx` → `App.tsx` → `Inside.tsx` threading)
> - iOS / Android / Windows — `joinRoom` bindings with real call sites in each shell's rooms section, `room.join` rows carrying the same translations `party.join` already had
> - `tests/test_community.py` — a stranger joins and speaks; no token, no entry; double-join idempotent; the ninth joiner is turned away while an existing participant re-joins freely
>
> Suite: 3301 passed, 1 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #269 — 0.64.0: the tour comes home, and the three cut together

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/269>

> Two things in one commit, because the owner asked for them in one breath: the corrections, then the cut.
>
> **The tour returns to the front page.** The gallery split moved every picture to docs/gallery.md and kept a curated handful; the owner read the result and wanted the README the way it was. It is: the full illustrated tour stands in the README again, docs/gallery.md is gone, and the gallery guards read the front page alone, exactly as they did before the move. The split never reached a release, so it owes the changelog nothing. Individual pictures come out later, by hand, one named at a time.
>
> **The 0.64.0 cut.** The thirteen fields the release checklist names, the README banner and table row, and the CHANGELOG entry — the same cut in all three repositories. QRME's changelog tells the whole story since 0.63.0, eight rounds of it: the remembrance, the handed link, the pasted link, the torso form, marketplace folders, top friends, the vastscape, the connections catalog picker, the standing rooms, the footsteps, the chat handing back its walls, the vault-hiccup fix, the escape-guard test, and the login-wall refusal.
>
> Suite: 3299 passed, 1 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #268 — The login wall is not source material

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/268>

> The field report, verbatim from the chat that surfaced it: the persona answered a question about its owner's Facebook with "what came through was basically the login page." The import had "succeeded" — by storing the platform's login wall as the profile's source material, because a wall page has a title and text and the fetch asked no further questions.
>
> The fetch now recognises a wall and refuses honestly:
>
> - `qrme/scrape.py` — `wall(page)`: the check reads the page's **title**, where a wall announces itself ("Log into Facebook", "Sign Up | LinkedIn"), so a profile whose bio merely mentions signing in is never refused over its own words
> - `qrme/routers/social.py` — the scrape door refuses a wall with 422 and the honest workaround: copy the profile's text while signed in and paste it into collect
> - `qrme/i18n.py` — the refusal in all ten languages
> - `tests/test_the_link_that_was_never_visited.py` — a Facebook wall page is a refusal, nothing lands in the sources, and the not-a-wall counter-case holds
>
> A wall's words are the platform's, not the person's, and material that feeds a profile's training must never be them.
>
> Suite: 3299 passed, 1 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #267 — The chip shrinks to a footprint, and the chat hands back its walls

- merged · opened 2026-08-12 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/267>

> Two field reports from the same phone, minutes apart.
>
> **The chip was three times too big.** It sat on top of the chat's wardrobe box. It is now just the mark and the number — `👣 2` — at a third the size, tucked tighter into the corner, with the full sentence moved into the hover tooltip so both wordings still stand in all ten languages. The same shrink ships in the sibling consoles (jim-mini#202, pdi#162).
>
> **The chat hands back its walls.** The receding-grid backdrop and the sticky presence bubbles floated the session's names and portraits over the words people were trying to read, and the imported portrait rendered badly at bubble size. Both are out: the chat is a plain message thread again. Presence rendering belongs to the rooms and the vastscape, where there is a scene to stand in — a text thread is its own scene. Untouched on purpose: the full-screen talk overlay's avatar/torso, and the front page's top-friends strip (which keeps the bubble styles alive). The one l10n key the bubbles alone asked for (`chat.you`) leaves the tables with them, keeping the dead-key ledger at zero.
>
> - `app/src/screens/Chat.tsx` — presence block and `chat-space` class removed; avatar still loads on mount for the talk overlay
> - `app/src/styles.css` — grid backdrop, sticky presence row, `youfill`, and the torso-in-chat rule removed; shared bubble styles kept for Home
> - `app/src/Footsteps.tsx` + `styles.css` — the chip shrink
> - `app/src/l10n.ts` — `chat.you` deleted in all ten languages
>
> Suite: 3298 passed, 1 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #266 — The catalog steps out, the rooms stand ready, the footsteps show

- merged · opened 2026-08-11 · merged 2026-08-12
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/266>

> Three field reports, one round.
>
> **The connections catalog.** "Google Calendar is the only app that shows up" — and the backend has carried a forty-app catalog across six providers (Apple Intelligence, Google Gemini, Microsoft Copilot, Canva, smart glasses, gaming consoles) all along. The console's connected-apps card offered exactly one hardcoded button in front of it. The card now asks the catalog: provider picker, app picker, the chosen app's directions and capabilities shown before connecting. Google Calendar has company because the company was always there and the door was not.
>
> **The standing rooms.** A new user opened the Rooms screen, found the list empty, and left. Twelve standing rooms — blueprints, not rooms — now answer at `GET /rooms/templates`, from The Front Porch (chat) to The Vastscape (VR, watch-together). Opening one goes through the same `POST /rooms` as typing the topic by hand, so a template grants nothing the form does not. The console shows them above the live list with one-press "Step inside"; iOS, Android and Windows fold them into their rooms doors (binding + tap-to-fill, per the binding-is-not-a-door guard).
>
> **The footsteps.** "Is there a way to know how many people have accounts?" A counter now stands in the top-right corner: verified accounts, as an aggregate — no name, email or id rides with the number. It travels on `/health`, the request every client already makes at launch for the version handshake, so it cost no new door. The JIM-mini and PDI consoles carry the same chip in the same corner in the same ten-language wording (jim-mini#201, pdi#161).
>
> Also in the diff: the Footsteps chip classified as fixed chrome in `test_every_surface_is_drawn.py` (like the version guard), and one iOS untranslated-ratchet catch — a nested quote inside a string interpolation read as English prose; the fix is the house pattern the next file over already used.
>
> Suite: 3298 passed, 1 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #265 — Round 20: the link handed mid-conversation + the remembrance past the window

- merged · opened 2026-08-11 · merged 2026-08-11
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/265>

> The other half of the Round 18 field report ("looking things up, remembering more"), plus today's report from the field: *"I'm not seeing where to import a data screen profile with a link."*
>
> **The pasted link names its own platform.** The social import door asked for a transcription — pick a platform from a dropdown, retype the handle out of the link you're holding. The handle field now takes the link itself: the host names the platform, the path names the account, and what the link says wins over the dropdown. Unrecognized sites are refused with the fix in the sentence (both refusals in the ten-language table); a platform front door with no account is told apart from a profile page. The console placeholder says "the handle — or paste the profile's link", and a pasted link pre-selects *collect*.
>
> **The link handed mid-conversation.** A URL pasted into the chat box is read on the spot through the same offline-gated fetcher every outbound path uses, and the page rides into that turn's prompt. The honest lines are load-bearing: offline, the prompt says the link was not visited and must never be guessed at; a failed fetch is admitted in the same words. A message with no link fetches nothing.
>
> **The remembrance past the window.** Chat context was the last 30 approved turns and the 31st-oldest vanished. Aged-out turns are now folded — by the profile's own provider — into one running paragraph per (profile, interactor) that rides every prompt. Each fold reads only what newly aged out; a distillation failure never breaks the reply. Readable at `GET /profiles/{id}/memory/{interactor}/remembrance` (owner or the person it is of) — a card on the console's Memory screen, and the memory-show action on all three shells now leads with what was kept. The DELETE that erases a conversation erases the remembrance in the same breath.
>
> Suite: 3289 passed, 1 skipped (15 new tests). The floor-ratchet guard caught two bare numeric floors in the new tests on the way; both now derive from the setup they measure.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #264 — Round 19: the talk surface shows the face, the face has a deck + 0.63.0 cut

- merged · opened 2026-08-11 · merged 2026-08-11
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/264>

> Two commits: Round 19, then the 0.63.0 cut.
>
> **The talk surface shows the face.** The microphone no longer fills the composer — it opens a full-screen talk surface with the profile's portrait front and centre, pulsing while it listens, the transcript shown as it's heard, the reply spoken back through the approved-only speech gate. The orb appears only for a profile with no portrait yet, next to a pointer at where to get one. (The Guardian is a voice with no face, so its surface is an orb; a persona has a face.)
>
> **The avatar deck.** Identity's portrait card becomes a deck with three shelves:
> - *Pick a character* — the starter portraits as a tappable grid; the asset path comes from the brief itself (the server names where its portraits live, the client never spells a path).
> - *Your own face* — import a photo through the existing media door, or capture from five angles (front/left/right/up/down); every frame is uploaded and kept as provenance, the front frame becomes the portrait.
> - *An avatar you already have* — Ready Player Me, Bitmoji, Meta Avatars, Apple Memoji, Xbox, ZEPETO, Mii — as imports, not integrations: the person exports on the provider's own surface and hands QRME the image; nothing calls a provider API or holds a provider credential.
>
> Two routes carry it: `GET /avatars/market` (the shelf, with the how-to for every source) and `POST /profiles/{id}/avatar/import` (owner-only; portrait set through the same pipeline as a starter face — AI badge and likeness record ride on the render — and the import written onto the profile's record as a source item). Unknown source → 422 with the pointer to the market list. Doors on the console and all three native shells, with `ava.market`/`ava.import`/`ava.url.ph` rows carrying the console's translations verbatim.
>
> **The console fits the phone it runs on.** Both field-reported layout defects trace to grid items refusing to shrink below their content: the tracks clamp now (`min-height`/`min-width: 0`), the app height follows `100dvh`, the sidebar scrolls on its own in the landscape-phone case, and the onboarding card no longer overflows a narrow screen.
>
> **0.63.0: cut together at one version.** All thirteen version fields the release checklist names, plus the changelog entry and README story row. One new field label (`extra` — the capture's extra frames) entered the ten-language table when the field-label guard asked for it.
>
> Suite: 3274 passed, 1 skipped over the full tree (Round 19 + cut).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #263 — Round 18: the chat follows the conversation, gains a voice, and visits the link it imports

- merged · opened 2026-08-11 · merged 2026-08-11
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/263>

> Three field reports from the beta, in one round.
>
> ## The chat scrolled the wrong way
> Talking to a profile on a phone, the reply landed below the fold and stayed there until you dragged it up. The scroll ran from a `finally` block inside `requestAnimationFrame`, which can fire before React commits the new bubble — it measured the height from before the reply existed. Moved to an effect keyed on the message list and the thinking state, so it runs after the commit and scrolls to the bubble it is scrolling to. The conversation now stays pinned to its newest line, including while the profile is still thinking.
>
> ## The chat had no voice
> The voice pair has been on the native shells since 0.62.0, but the console chat — the surface the beta actually runs — could neither speak nor listen. Two buttons on the composer now: one reads each **approved** reply aloud in the reader's language through the device's own speech engine, one fills the box from the microphone. Both feature-detected: the mic button does not render where the browser has no SpeechRecognition, and the speak toggle no-ops where there is no synthesizer. A held or moderated message is never read out as if the profile had said it.
>
> ## The imported link was never visited
> A `collect` connection has known the account it points at since the day it was made — platform and handle is a public URL — and the collect door only ever stored what the owner pasted. The door named *pull the account's content in* was in truth *retype it in*. `POST /social/{cid}/scrape` (`qrme/scrape.py`) goes to the address and takes what a browser would show anybody: the title, the bio line in the page's metadata, the visible text, capped. It lands as an ordinary `social_post` source item — sealed into the PDI vault when one is configured — with the URL and fetch time written into the words, so the provenance travels with the material. A button on the connection, on the console **and all three native shells**, offered only where a collect connection has a handle to visit.
>
> What it refuses, each with the reason in the sentence: an offline deployment does not open the socket (`offline.allow` is called at the fetch site, so a second caller inherits the gate rather than remembering it); a connection with no handle has no address; a page with nothing readable is a 502, not an empty source. Only public pages, as anyone on earth would see them. The two new refusals are translated into all ten languages.
>
> The same door lands on JIM (guidance context) and PDI (an encrypted vault record) in this round; the three refusal guards it carries now pass in all three suites, so they leave the divergence backlog and join `shared_guards.txt`, byte-identical across the three repositories.
>
> ## Verification
> Full local suite green before push: **3268 passed, 1 skipped**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #262 — 0.62.0: cut together at one version

- merged · opened 2026-08-11 · merged 2026-08-11
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/262>

> Version alignment: the three products are cut together, so one number names one combination of all three. No QRME code changed — JIM's phones reached parity with their console this round (every backend route with a door on iOS, Android and Windows, the voice pair with the device's own voice as the fallback, PATCH through a test-pinned override, the most-touched screens speaking the reader's language). The thirteen version fields the release checklist names all move in step, plus the changelog entry and the README story row.
>
> Suite: 3262 passed, 1 skipped locally before push.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #261 — 0.61.1: cut together at one version

- merged · opened 2026-08-11 · merged 2026-08-11
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/261>

> Release prep for the joint cut: QRME's part of app-v0.61.1.
>
> - The nine version fields the release checklist names, bumped 0.61.0 → 0.61.1 (build codes 61000 → 61001) — `pyproject.toml`, `qrme/api.py`, `app/package.json`, both root entries of the lockfile, `project.yml` (marketing + project version), `build.gradle.kts` (name + code), `QrmeStudio.csproj` (Version / AssemblyVersion / FileVersion)
> - CHANGELOG `[0.61.1]` entry covering the accessibility statement + accountless report door, wall-upload descriptions, the aria-live chat log, the emptied known-gaps ledger, the open-signup keyhole and Terms 1.2, with the link definition the releasing doc asks for
> - README banner → v0.61.1 and a new story-table row
>
> Tagging (`app-v0.61.1` on this commit) is the maintainer's step, per docs/releasing.md.
>
> Suite: 3262 passed, 1 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #260 — The backlog the statement promised, run to zero

- merged · opened 2026-08-11 · merged 2026-08-11
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/260>

> The accessibility round ended by admitting three barriers into `tests/a11y_backlog.txt`. This round closes all three and lowers the ceiling to zero.
>
> ## The upload asks what it shows
>
> Wall media uploads never asked for a description, so every picture reached other people with an empty alt. The composer now asks ("Describe what it shows", ten languages), the words ride the upload as an `alt` query parameter, land in a new `media_alt` side table (a side table because this schema has no migrations), and come back on every read — the upload receipt, the post, the feed hydration — as the image's `alt`.
>
> ## The chat tells the screen reader
>
> Chat replies appeared silently. The conversation log is a `role="log"` `aria-live="polite"` region now, so a screen reader hears the answer arrive instead of sitting in silence.
>
> ## The shells carry the statement
>
> iOS, Android and Windows carried the report form and its lead, but not the per-need statement the console makes. The nine `ns.acc.needs.*` keys now ride in all three native L10n tables — the console's own translations, script-copied, not re-translated — and all three access views name every need before asking their three questions.
>
> ## Guards
>
> - `test_the_wall_upload_asks_and_the_picture_answers` — behavior end to end, plus the composer source
> - `test_the_chat_tells_the_screen_reader` (repo-local)
> - `test_the_shells_carry_the_statement` (shared — the three-way manifest moves to 461 rows, byte-identical across qrme, jim-mini and pdi)
> - `a11y_backlog.txt`: 3 rows → 0 rows, ceiling 3 → 0; the img-alt guard's docstring now states the true reason an empty alt passes (the form asks; blank is the uploader's decision)
>
> Suite: 3262 passed, 1 skipped.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #259 — Ability is not a gate: the accessibility statement, behavior, guards and report door

- merged · opened 2026-08-11 · merged 2026-08-11
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/259>

> The statement, the behavior behind it, the guards, and the door — because a commitment with no door is a sentence.
>
> **The statement, upfront.** The README carries an "Ability is not a gate" section before features; the console carries a new Access screen (**193**), in ten languages, reachable *before sign-in* via `#access` and linked under the sign-in form — the person it exists for may be the person the signup shut out. It names who is expected here: blind and low-vision, deaf and hard-of-hearing, mute and nonspeaking, motor/amputation/tremor, autistic and cognitively different, dyslexic, motion-sensitive — and says a missing need is a gap in the list, not in the person.
>
> **The behavior.** `POST /access/reports`: three questions and no diagnosis (what were you trying to do, what stood in the way, what would help), no token, into a table with **no submitter column** — sealed to the PDI vault when configured, never relayed to the shared problems collector. `GET /access/reports`: reviewer-token only. Doors in the console and all three native shells, localized in ten languages. `document.documentElement.lang` now follows the real page language, and the stylesheet honours `prefers-reduced-motion`.
>
> **The guards.** `test_ability_is_not_a_gate.py`: a report needs no account and keeps no name; reading is the steward's alone; every console image says what it shows; and `tests/a11y_backlog.txt` — the tracked work the statement promises — only shrinks. Four new rows in `shared_guards.txt` (456 → 460), traveling to all three products.
>
> **The paperwork.** Terms 1.2 names the real door where 1.1 could only promise a help surface; the three questions enter the field-label catalog; the tutorial teaches the screen; the helper dock can point at it.
>
> Suite: 3259 passed, 1 skipped locally before push. Same round lands in jim-mini and pdi.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #258 — The door defaults open: signup keys become optional in the beta compose file

- merged · opened 2026-08-10 · merged 2026-08-10
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/258>

> The beta compose file was written when the posture was a locked door: `QRME_SIGNUP_KEY` and `JIM_SIGNUP_KEY` were `${VAR:?}`, so the stack refused to start without real keys, and the first `.env` got keys it never chose. Now that the consoles honestly ask for an invite key whenever `/health` says the deployment is gated, that inherited lock would greet every beta tester with a field the operator never meant to show.
>
> **Empty now means open.** The signup keys default to empty in the compose file — the one deliberate exception to the everything-is-required rule — and `docs/beta-deploy.md` says so where it lists which secrets to generate: blank while the beta runs open, filled in when account creation should need an invitation.
>
> Operator's step after merge: blank the two lines in `/srv/qrme/.env` (`QRME_SIGNUP_KEY=` / `JIM_SIGNUP_KEY=`), pull, relaunch. `/health` then reports `"signup_key": false` and the signup screens stop asking.
>
> Suite: 3248 passed, 1 skipped locally before push.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #257 — The gate gets a keyhole, plans go free, and the terms say beta

- merged · opened 2026-08-10 · merged 2026-08-10
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/257>

> ## What
>
> Three things, each disclosed where a person meets it:
>
> - **The gate gets a keyhole.** `QRME_SIGNUP_KEY` closed account creation and no client could answer it — the live beta returned every signup a 403 nobody could act on. `/health` now reports whether the gate is set (never the key); the console and all three native shells store an invite key and send it as `x-signup-key`; the signup screens ask for one exactly when the deployment is gated, in ten languages. The `unsendable_headers.txt` row that called this gap deliberate is struck with the reversal written in place; `shared_guards.txt` grows 455 → 456 (byte-identical across the three repos).
> - **Free during the beta.** Both paid plans drop to $0 while the beta runs; tiers keep their names and gates, and every price surface says "free during the beta, $20/$130 a month when it ends." Price tests guard the new agreement, dated.
> - **Terms 1.1.** Beta status (testing only, data may be lost or reset, no fees during the beta, none begin without notice and renewed agreement) and the accessibility commitment (worded strictly to what is true today: text-alone covers everything, voice always optional, gaps become tracked work).
>
> Suites: QRME 3248 passed / 1 skipped, JIM 1754 / 3, PDI 1097 / 5. Sibling PRs in jim-mini and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #256 — 0.61.0: the beta stands up

- merged · opened 2026-08-10 · merged 2026-08-10
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/256>

> ## What
>
> The 0.60.10 cut. Version fields bumped in every site — `pyproject.toml`, `qrme/api.py`, `app/package.json` + lock, Android `versionCode`/`versionName`, iOS `MARKETING_VERSION`/`CURRENT_PROJECT_VERSION`, Windows `Version`/`AssemblyVersion`/`FileVersion` — plus the CHANGELOG entry and README banner/history row.
>
> What this release carries (all previously merged to main):
> - the console-blanking CSP fix and its over-HTTP guard
> - the bare-domain → `/app/` front door
> - the beta topology (`beta-compose.yml`, `beta.Caddyfile`, `docs/beta-deploy.md`), first stood up on a real host
> - nightly database backups as a running service
> - bootstrap idempotent by validation
> - the release-bodies sweep repaired twice (parse, fetch) and guarded
>
> Suites: QRME 3247 passed / 1 skipped, JIM-mini 1753 / 3, PDI 1096 / 5. Sibling cut PRs in jim-mini and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #255 — The sweep measured the fetch, not the releases

- merged · opened 2026-08-10 · merged 2026-08-10
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/255>

> ## What
>
> The repaired sweep's first honest run failed claiming the kept release `app-v0.24.0` no longer carries the frozen body. The release was fine — the **fetch** had lost it: paginated `gh api` output was re-split into pages by a regex matching any `]` `[` pair, including one inside a release body's own markdown, and broken chunks were dropped silently.
>
> - `gh api --paginate --slurp` now returns pagination as one valid JSON document; the regex chunking is gone.
> - A completeness guard proves the fetch returned every release the record names (rows and `# kept:`) before anything is compared — a lost release is reported as a fetch failure, never as a repair that didn't happen.
> - Driven end-to-end against a stub `gh`: the honest verdict on the real record, and the guard firing when the kept release goes missing.
>
> Sibling PRs in the other two repositories carry the identical change.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #254 — The checker that could not start, and the copies that finally run

- merged · opened 2026-08-10 · merged 2026-08-10
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/254>

> ## What
>
> - **Repairs the release-bodies sweep**: an earlier edit left the workflow's embedded Python unparseable (a misplaced `problems = []` and a dropped `if gone:`), so every scheduled run died on an IndentationError before checking anything. The block is restored to its intended shape.
> - **Adds the guard that was missing**: `test_the_workflow_scripts_still_parse` extracts the Python heredocs from both release workflows and parses them (verified to fail against the broken version), and `test_the_frozen_opening_decides_staleness_for_this_product` drives the staleness decision with this product's own `# frozen-opens:` header, using the `prose()` function taken from the sweep's own script — a stale body is caught, a fresh one passes, and a body merely quoting the phrase passes (the defect the startswith decision replaced).
> - **Bootstrap is idempotent by validation**: a saved PDI tenant token that PDI still honours is kept; minting happens only when there is none or it is refused. A restart now reuses the first tenant instead of abandoning its sealed records. Driven live against a local PDI: mint on first run, keep on restart, re-mint on a dishonoured token.
> - **Backups become a running job**: a `backup` sidecar in `beta-compose.yml` takes a nightly `sqlite3 .backup` of all three databases plus the collector ledger into `/root/backups`, keeping fourteen days. `docs/beta-deploy.md` § 6 updated from instructions to verification, with the stated limit that copies do not leave the host.
> - `shared_guards.txt`: 453 → 455, byte-identical across the three repositories.
>
> Sibling PRs: davidsbianchi1984/jim-mini and davidsbianchi1984/pdi carry the same sweep repair and guards.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #253 — The console the policy blanked

- merged · opened 2026-08-10 · merged 2026-08-10
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/253>

> ## What happened
>
> The first real deploy of the beta topology came up healthy — containers, certificates, all of it — and all three consoles rendered as blank dark pages. The nonce Content-Security-Policy meant for the server-rendered pages was stamped on the console's HTML too, and the console's bundle is an external same-origin script no nonce can reach, so the browser refused it. HTML 200, nothing running. No in-process test saw it: a `TestClient` reads the policy and enforces none of it.
>
> ## The fix
>
> - **`pagehead.console_policy()`** — `'self'` where the page policy names a nonce, still no inline script; `blob:` for previews and synthesised audio, `worker-src` for the service worker, `manifest-src` for the home screen.
> - **The middleware picks the policy by path** — `/app` gets the console policy; every other page keeps the nonce policy unchanged.
> - **`GET /` redirects to `/app/`** when a console is built. Measured live, the bare domain answered `{"detail": "Not Found"}`, and a tester types the domain, not the mount point. Recorded in `NOT_A_CLIENT_CALL`: no client constructs the address it is already standing on.
>
> ## Test-enforced
>
> `test_what_the_browser_enforces.py` now measures the console's headers over real HTTP, against a console dist the fixture lays down itself so CI asks the question without a front-end build. Three new guards enter `shared_guards.txt` (450 → 453), byte-identical across the three repositories. Guard on the guard: the stranger pages are asserted to keep their nonce policy, so the console's wider policy cannot leak.
>
> Full suite: 3,245 passed, 1 skipped.
>
> Sibling PRs carry the same fix in jim-mini and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #252 — Cut 0.21.0

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/252>

> Five version strings (`pyproject.toml`, `qrme/api.py`, `app/package.json`, and
> both root entries of `app/package-lock.json`), the changelog promoted from
> Unreleased, and `RELEASE_NOTES.md` rewritten for the tag body.
>
> Covers the four door-audit rounds merged in #251: rooms, the body market,
> delegation, and signing. Three of the four found a defect behind the door —
> a room transcript readable with no token at all, a delegation policy nobody
> could take up, and `verify_package` reporting a valid signature as broken
> because a later field was missing.
>
> | | before | after |
> |---|---|---|
> | Console-doorless routes | 64 | 40 |
> | `api.ts` bindings nothing calls | 25 | 12 |
> | Screen-manifest `unaudited` seeds | 8 | 7 |
>
> Full suite after the cut: **1926 passed**.
>
> Tag is the user's step — pushing `app-v0.21.0` fires the desktop release build
> and lays `RELEASE_NOTES.md` over the release body.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #251 — Four door-audit rounds: rooms, bodies, delegation, signing

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/251>

> Four rounds run back to back. Each one built a console door for a backend
> feature that had none, and in three of the four, building the door found a
> defect in the thing it was a door to — with the argument against the defect
> already written down elsewhere in the same repository.
>
> ## Round 1 — a room id was the only thing a room asked for
>
> `Rooms` could open one and not enter it. Screen 175 is the way in, and it
> found two defects worth more than the screen:
>
> - **Anybody could speak as anybody.** `POST /rooms/{id}/messages` read the
>   speaker from `sender_id` *in the body* and checked only that it named a
>   participant, never that the caller *was* that person.
> - **The transcript asked for nothing at all** — not a wrong token, no token —
>   and neither did `advance`.
>
> A room id is not a secret; it rides on printed stickers. That sentence was
> already written two routes away, on `GET /rooms/{id}/mic`. All three now go
> through `_require_in_room`. `sender_id` stays on the model and is ignored:
> three shipped native clients send it, and a 422 on upgrade is a worse answer
> than not believing it.
>
> ## Round 2 — the body market, and the connections bracket
>
> The catalogue listed nine robot models; it now lists 36 from 25 makers across
> humanoids, home robots, quadrupeds and announced platforms, with a review
> date the suite refuses to let go stale. Announced bodies are listed on purpose
> and refuse to bind with a 409 that says why, rather than a 404 that would lie
> about a machine its maker has publicly shown. Plus the connections bracket:
> task packs and connectors, each installed pack becoming a commandable verb for
> exactly one body, capability-checked and audited like every built-in command.
>
> ## Round 3 — a policy you could publish and nobody could take up
>
> `Delegate` had the owner's half only. Delegation exists for the person on the
> *other* end of a conversation, and that half had four bindings and no screen.
>
> Driven end to end, **every rule was already right** — the offer lists phases
> and never the grant id, `research` is refused without a grant, starting one
> requires an existing conversation, and reading it is 403 to an outsider, 401
> to nobody, 200 to the delegate and the owner both. First round in a while with
> no defect in it, recorded as such. The failure it *did* find is the one the
> door audit exists to name: a feature finished and unreachable.
>
> `api.health` was deleted rather than doored — same route as `healthInfo`, threw
> the body away, returned a boolean. Not every unused binding wants a screen.
>
> ## Round 4 — a missing field was reported as a broken signature
>
> Seven signature routes had no console door. `Referrals` had written the gap
> down as a sentence — *"None enrolled. The ceremony can enrol one."* — under a
> heading with no button. The ceremony page existed and posts the assertion back
> by `postMessage`; nothing was listening.
>
> Building the listener found the defect, in the one place this feature cannot
> afford one. `verify_package` runs eight checks in order, and *any* exception
> anywhere in that sequence ran `checks["signature"] = False`. So a package
> missing `display_text` came back saying **the signature is invalid**, when the
> ECDSA verification several lines earlier had passed — the most damaging thing
> this endpoint can say, and untrue — with the reason given as `'display_text'`,
> a `KeyError` repr beside two notes written as full sentences. A counterparty
> reading that would conclude they held a forgery.
>
> The argument was already in the same feature: the router says of its own
> refusals that *the message is the reason, because a signature that is turned
> away without one is impossible to fix from the outside.* A counterparty is
> exactly the outside.
>
> Two rules now hold: a check that already passed is never retroactively failed
> by a later one breaking, and a check that never *ran* is not a pass.
>
> ## Counts
>
> | | before | after |
> |---|---|---|
> | Console-doorless routes | 64 | 40 |
> | `api.ts` bindings nothing calls | 25 | 12 |
> | Screen-manifest `unaudited` seeds | 8 | 7 |
>
> New screens 174–178. Full suite: **1926 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #250 — Cut 0.20.1

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/250>

> Five version strings — `pyproject.toml`, the FastAPI app, `app/package.json` and **both** root entries of `app/package-lock.json` — plus the dated changelog heading and rewritten release notes. QRME, JIM-mini and PDI move on one number, as they have since 0.1.6.
>
> ## What 0.20.1 carries
>
> The changelog's `[0.20.1]` section holds **two rounds** under their own subheadings, because they shipped together and the second was found by the first.
>
> **The union hid a surface.** 0.20.0 reported a doorless backlog of zero. It was true of the wrong question: `clientpaths.doorless` unions the console with the three native shells, so a route only the phone calls counts as doored — and the console alone could not reach **64 routes**. Two new guards, in all three repositories: `test_the_console_is_a_client_too.py` and `test_a_binding_is_not_a_door.py`, the latter enforcing something the `doorless` docstring had declared unenforceable and finding **25 bindings nothing calls**.
>
> Screen **174, "What you are owed"** — the seller's side, which the console did not have. Building it exposed three defects: a statement that added ¥100 and $100 into 200; a `DELETE /marketplace/listings/{id}` that asked for no credential while its narrower neighbour said *"not your offer"*; and a sale credited to a profile id while the statement reads by account id.
>
> **A sale credited to a key nothing reads.** Paying down the first orphaned binding found it. The offer recorded the token's subject, and an owner token's subject is a profile, not an account. `200` on the offer, `201` on the purchase with a real ledger entry and the words *the sale is recorded on the seller's statement* — and an empty statement. `commerce.beneficiary_of` had resolved a profile to its owner for gifts since gifts existed; `_earner()` is that rule on the other half of the money.
>
> ## Companion PRs
>
> - [jim-mini#183](https://github.com/davidsbianchi1984/jim-mini/pull/183) — 786 passed
> - [pdi#144](https://github.com/davidsbianchi1984/pdi/pull/144) — 340 passed
>
> ## Verification
>
> All five version strings verified programmatically against the changelog and release-notes headings; console builds; version-related tests pass and no test hardcodes the old number. **The full suite was still running when this was pushed** — CI is the authority, and I'll report the local result.
>
> Tagging remains a manual step.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #249 — Resolve a seller to their account, not to their profile

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/249>

> Paying down the first of the 25 unused `api.ts` bindings — the ones [#248](https://github.com/davidsbianchi1984/qrme/pull/248)'s new guard found — turned up a money defect.
>
> ## A sale credited to a key nothing reads
>
> `PUT /marketplace/listings/{id}/offer` recorded the seller as `auth.principal(request)["subject_id"]`, and **an owner token's subject is a profile, not an account**. `GET /profiles/{id}/earnings` resolves the profile to its `owner_id` before reading the ledger.
>
> Driven against a running backend:
>
> | step | result |
> |---|---|
> | price the listing with an owner token | `200`, `seller_id: prf_45cd…` |
> | buyer purchases | `201`, real `ledger_entry`, *"the sale is recorded on the seller's statement"* |
> | seller reads their statement | **empty** |
>
> The money was written. It was written under a key nothing queries, and every response along the way said it had gone through.
>
> ### Why it survived
>
> Nobody could do it. `api.setOffer` existed in `api.ts` and no screen called it — precisely the gap the previous round's guard was written to find, and this is what came out of closing the first one. On the phone the Market tab prices listings as an *interactor*, whose subject id already **is** the account, so the one surface that could reach the route took the path that happens to work.
>
> `commerce.beneficiary_of` has resolved a profile to its `owner_id` for gifts since gifts existed — same file, same reason. The rule was written down and applied to one half of the money.
>
> ## Fixed
>
> - **`_earner()`** resolves an owner token to its account on every seller-side route: pricing, withdrawing, and `GET /marketplace/sales`. Moving what is stored had to move what is compared, or a seller locks themselves out of their own offer — pinned by its own test.
> - **`api.placeListing` / `api.unplaceListing` took no token.** Harmless only while nothing called them; those routes gained claimant gating in #248, so a tokenless call would now be a 401.
>
> ## Added
>
> "What you are owed" gains **a price on it** and **where it is offered** — `setOffer`, `withdrawOffer`, `placeListing`, `unplaceListing`. Unused bindings **25 → 21**.
>
> ## Verification
>
> Injection-tested: reverting `_earner` to `_actor` fails five tests. 119 directly-affected tests pass, console typechecks and builds, docs/tutorial/gallery/scripture guards pass. **The full suite was still running when this was pushed** — CI is the authority on it, and I'll report what the local run says.
>
> The room-microphone feature (`lendMicInRoom`, `micsInRoom`, `takeBackMicInRoom`, `roomMessages`) is the next block: I drove it live, the routes are correct and well-guarded, and there is no door to any of them.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #248 — Ask each client the door question separately, and build the seller's side

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/248>

> The doorless backlog reached zero in 0.20.0 measuring the wrong thing. `clientpaths.doorless` unions the console with the iOS, Android and Windows shells, so a route only the phone calls counts as doored — the number went to zero while a desktop owner could not reach **64 routes**. The guard was answering *some client can reach this*, which was true, in place of *this client can reach this*, which was not.
>
> That is the same shape as every other defect this audit has produced: a checker answering a question slightly to the left of the one that matters, and passing.
>
> ## Two guards
>
> - **`test_the_console_is_a_client_too.py`** — the console's own backlog in `console_doorless.txt`, checked in both directions and ratcheted so it cannot grow past 64. The union guard stays; a route no client anywhere calls is still worse. A phone-only capability is a legitimate design choice, which is what the snapshot is for: deferring one takes a deliberate edit and shows up in a diff.
> - **`test_a_binding_is_not_a_door.py`** — the same mistake one level down. A function in `api.ts` that no screen calls is not a door, and `doorless` counts it as one. Its docstring called this *"a discipline rather than something the test can enforce"*; it turned out to be enforceable in about twenty lines, and found **25 bindings nothing calls**. *The test cannot check this* is a claim worth testing.
>
> ## Screen 174 — "What you are owed"
>
> Nine of the sixty-four were the whole seller's side of the product. An owner could be bought from and could not post a licence offer, see who held one, revoke it, read a penny of what it earned, or ask to be paid — all present on the phone's Earn tab, all absent from the desk. Building the screen found two defects.
>
> ### A statement added two currencies together
>
> ¥100 and $100 came back as `accrued: 200`, labelled with whichever sale was newest, and all three native shells render that figure with a currency symbol in front of it. Nothing was wrong with the entries — each carried its own currency the whole time — only the arithmetic over them, in the one place where a wrong number looks exactly like a right one.
>
> Totals are now per currency (`by_currency`, `currencies`, and a `mixed` flag on the headline); the settlement currency is chosen deterministically rather than by recency; a payout settles **one** currency and reports what is `remaining`. A single-currency account reads exactly as it did.
>
> ### Anyone could delete anyone's listing
>
> `DELETE /marketplace/listings/{id}` asked for no credential at all, while `DELETE /marketplace/listings/{id}/offer` — which destroys strictly less — answered the same stranger *"not your offer"*. Driven live against a running backend: a stranger removed a listing that had a recorded seller, an open offer and a paid order against it. The offer and the orders survived orphaned, and the title was free for somebody else to put up.
>
> A listing is now claimed by whoever staked something on it — the creator recorded in `listing_claims`, the seller on its offer, or the owner of the profile it advertises. Creating one still needs no token (that is the design, and the seller is established when a price is attached), and a listing with no claimant at all is still anybody's to clear away, which is the honest reading of an endpoint that needs none. The place routes are gated the same way: moving somebody else's listing to another city is a quieter version of taking it down.
>
> ## Also
>
> `clientpaths.py` says it is byte-identical across the three repositories and was not — JIM and PDI never received the `fetch`, `window.open`, `<img src>` and `<a href>` call forms from the previous round. Restored, and the companion PRs are [jim-mini#182](https://github.com/davidsbianchi1984/jim-mini/pull/182) and [pdi#143](https://github.com/davidsbianchi1984/pdi/pull/143).
>
> ## Verification
>
> Every fix was injection-tested: the guard was deliberately broken and the test confirmed red before being restored. One assertion **missed** on first attempt — `"statement.totals.mixed" in src` was satisfied by a second, unrelated line further down the file — and is now pinned to the actual conditional and re-verified.
>
> Console typechecks and builds. Docs, tutorial, gallery, surface and door guards pass; the full suite was still running locally when this was pushed, so CI is the authority on it.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #247 — The installer could not report, and nothing said so

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/247>

> Found while going to write the setup instructions for `PROBLEM_COLLECTOR`. **The instruction would not have worked.**
>
> ## The chain, and where it broke
>
> | link | state |
> |---|---|
> | `errors.ts` reads `__PROBLEM_COLLECTOR__` | ✅ |
> | `vite.config.ts` defines it from `process.env.PROBLEM_COLLECTOR` | ✅ |
> | `docs/cloud-model.md` says to rebuild with it set | ✅ |
> | **`desktop-release.yml` passes it to the build** | ❌ |
>
> Three packaging steps — macOS signed, Windows signed, unsigned — each carefully threading its *signing certificate* through `env:`, and not one of them mentioning the collector.
>
> So **every installer this workflow has ever produced compiled an empty address**, whatever secrets were configured, and launch-time error reporting was inert in every shipped desktop build. Nothing failed. The define existed. The documentation was correct about what to set. The step that runs the build dropped it on the floor, and the only way to notice was to install a build and watch nothing arrive.
>
> There is an irony in the source worth recording: `errors.ts` already anticipates the *neighbouring* mistake — it refuses to invent a product name because *"a repo whose vite.config.ts forgot the define would otherwise file its reports under whichever product this fallback named"*. The define was not forgotten. The environment feeding it was.
>
> ## The guard
>
> `test_the_installer_can_actually_report.py` checks the **chain**, not any one link: the source reads the define, the bundler supplies it from the environment, and *every* step running the packaging command passes it in.
>
> Two details that make it hold:
>
> - **Build steps are found by what they run** (`npm run dist`), not by what they are called. The name is the part most likely to change.
> - **A guard-on-guard** fails if that finder ever returns fewer than three, so renaming the packaging command cannot make this file quietly vacuous — the exact failure mode it exists to catch, one level up.
>
> `every` rather than `some` matters: the workflow branches three ways on signing and a build comes from exactly one branch per platform, so a variable threaded through two of three still ships one silent platform.
>
> **Four injections verified:** unwiring one step of three (the defect that shipped), hardcoding the token instead of reading a secret, renaming the packaging command to make the finder vacuous, and vite ceasing to read the environment.
>
> ## Behaviour that did not change
>
> **An unset secret still builds.** It arrives as an empty string — exactly the state the source already reads as *no collector* — so a fork with nothing configured keeps producing installers that report nothing rather than failing its release. "Off by default" survives the wiring.
>
> ## What this changes on your side
>
> Set `PROBLEM_COLLECTOR` and `PROBLEM_TOKEN` as repository **secrets**, then re-run the desktop release. Setting them before this fix would have done nothing.
>
> `docs/cloud-model.md` says plainly what was wrong and that the secrets are the mechanism — byte-identical across the three repositories, verified by md5.
>
> Same gap, same fix, same guard in [jim-mini](https://github.com/davidsbianchi1984/jim-mini/pull/181) and [pdi](https://github.com/davidsbianchi1984/pdi/pull/142).
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #246 — Cut 0.20.0

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/246>

> All three repositories move together, as they always do — one number across QRME, JIM-mini and PDI, so a console and a backend that disagree about their version are disagreeing about something real.
>
> Five strings: `pyproject.toml`, the `FastAPI(version=)` in `qrme/api.py`, `app/package.json`, and **both** root entries of `app/package-lock.json`. The lockfile is edited textually to preserve npm's formatting and then re-parsed to confirm both roots moved — a third occurrence slipping in is exactly what a blind string replace would carry silently.
>
> ## What 0.20.0 contains
>
> **The doorless backlog reached zero.** It began at **116** routes the backend served that no client could reach; this release closes the last **42**, across six new screens (**168–173**).
>
> What the campaign produced was not doors but **defects**, and almost none were visible to the typecheck:
>
> - **Three routes took no token at all.** A pack could be published under any publisher name crediting *any* account; a rating could be cast in somebody else's name — and since an `up` rating triggers cloud contribution, that let an unauthenticated caller push a stranger's conversation out of the deployment; and a named person's engagement record was readable by anybody holding two ids. In each case **the argument against it was already written down elsewhere in this repository**, and three routes had quietly gone the other way.
> - **A licence sold to a buyer too young to use it**, with the fee taken at sale time and the refusal arriving at delivery.
> - **A scan link that resolved against the console's own origin** — dead in every packaged build.
> - **A desk's honesty note rendered nowhere at all.**
>
> **The audit could not see two kinds of request.** An `<img src>` is a fetch; an `<a href>` is a fetch. Neither passes through the API client, and the extractor saw neither — so two routes sat on the backlog while a screen had been rendering both since it was written. Worse, the exemption list had absorbed three of them, and one of those had no door at all. The list now holds to one rule: **exempt a path because nothing should ever call it, never because the audit cannot see the call.**
>
> **Five findings are recorded rather than corrected**, because each is a decision to make deliberately rather than while building a screen: the gift/subscription beneficiary asymmetry, the contribution preview that survives opting out, the half-open quiet-hours window where 9-to-9 covers nothing, three deletes that disagree about *there was nothing there*, and `deleted_at_gateway` being true vacuously.
>
> ## The guard, now that the backlog is empty
>
> A new assertion says so directly, separate from the record comparison so the message is plain when it goes: *the number is no longer zero*. Its guard-on-guard moved too — asserting the snapshot was non-empty no longer means anything, so the liveness check now sits on the console's extracted call sites.
>
> ---
>
> `CHANGELOG.md` and `RELEASE_NOTES.md` updated. The scripture stays last in the README and appears in neither.
>
> The tag is not created here — that stays yours.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #245 — The doorless backlog reaches zero (42 → 0)

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/245>

> Six rounds, **42 routes**, screens **168–173**. The doorless backlog began at 116 and is now **empty**.
>
> What the exercise actually produced was not doors. It was defects — and almost none of them were visible to the typecheck.
>
> ---
>
> ## The defects, first
>
> | | what was wrong |
> |---|---|
> | `POST /packs` | **took no token at all.** Anybody could publish to the marketplace, name any string as the `publisher`, and name **any account** as the one sales accrue to |
> | `POST .../feedback` | **took no token.** A rating in somebody else's name — and an `up` rating is the trigger for contributing that exchange to the cloud, so an unauthenticated caller could push a stranger's conversation out of the deployment |
> | `GET .../engagement/{id}` | **took no token.** How often a named person talks to a profile, across how many sessions, and whether they liked it |
> | licence `acquire` | sold a clone licence to a **fourteen-year-old** — 201, `can_derive: true`, fee credited at sale time — then 403 on the only thing the licence is for |
> | desk `scan_url` | **relative** while its twin was absolute, so the console's scan link resolved against the console's own origin: dead in every packaged build |
> | `/desks/{id}/view.webp` | **never rendered anywhere.** Its honesty note — *a sample view; not live and not claimed to be* — was served to nobody |
> | the route audit | blind to `<img src>` and `<a href>` — the two requests with no function call in them |
> | the exemption list | had absorbed three of those as "not a client call", which is how the missing `<img>` above stayed hidden |
>
> The three unauthenticated routes share a shape: the argument against each was **already written down elsewhere in the same repository**. `commerce.beneficiary_of` says *a body-supplied beneficiary would let anyone direct a gift meant for a performer into their own balance*; the beacon list is owner-gated because *that is a list of physical places associated with a person*. Three routes were quietly making the opposite call.
>
> ---
>
> ## The rounds
>
> ### 168 · A period is a press — the audience
> Nothing renews on a timer; a period is charged when somebody presses renew, so `periods` counts deliberate acts and the screen says so rather than letting it read as elapsed time. `accept_price` must equal `price` exactly — a flag would let a client agree to a figure it never showed anybody. One asymmetry **recorded rather than corrected**: a gift reads its beneficiary from the subject, a subscription takes one from the body.
>
> ### 169 · A code on a wall — beacons
> Two codes that look identical and go opposite ways: a placed beacon brings a stranger *here*, a platform beacon sends them *away*. **Looking at a code is free; opening it is not** — every scan surface increments, because the server cannot tell an owner checking their own sticker from a stranger. A `?preview=1` would fix the inconvenience and ruin the number. Fixed the origin-relative `scan_url`, taught the extractor about markup requests, and emptied the exemption list of everything it was hiding.
>
> ### 170 · Four refusals, and two of them are yours — reaching out
> Four gates on unprompted outreach, in four different sentences because they are four different facts — and only two are the owner's to lift. **Quiet hours are not.** Sending them with an owner token is a 403, and that refusal is the feature: a window your correspondent can move is not a boundary. Also: the window is half-open, so 9-to-9 covers *nothing*; recorded and warned about rather than corrected, since changing the arithmetic would redefine every window already stored.
>
> ### 171 · Two kinds of leaving — contribution and licensing
> The contribution preview is a **dry run**, computed whether or not you are opted in — so the heading changes with `opted_in` and the content does not, because rendering it either way tells an opted-out owner their next conversation is on its way out. `deleted_at_gateway` is true *vacuously* when nothing ever left, so the console reads the count beside it.
>
> ### 172 · One thing, named
> Six reads, six answers to who may ask. **The campaign is the inversion**: the most public read in the product, and that is what makes it honest — it carries `proceeds_to`, so somebody about to give money sees who receives it on the same card. In the same spirit a campaign cannot exist before the designation does.
>
> ### 173 · Beginning, and passing on
> **An owner token cannot be the gate on succession**, because the signal it answers is that the owner cannot act. A reviewer holds it. With nobody named, the profile sunsets to memorial — *frozen rather than orphaned*.
>
> ### Taking it back (no new screen)
> Four deletes went onto the screens that already own the things they undo. Building them side by side surfaced a disagreement none of the routes knows it is in: deleting a missing comment is a 404, unlisting an unlisted profile is a 404, and unfriending a stranger is a **200 with `removed: false`**. Recorded rather than unified — but asserted together, so a future round that does unify them changes that test on purpose.
>
> ---
>
> ## The backlog, and its guard
>
> `doorless_routes.txt` is empty. `test_every_route_has_a_door.py` gains an assertion saying so directly, separate from the record comparison so the message is plain when it goes: *the number is no longer zero*, rather than *strike this line*.
>
> Its guard-on-guard changed with it. Asserting the snapshot was non-empty no longer means anything, so the liveness check moved to where the meaning lives — **the console must still be producing call sites** (>200). If the extractor broke entirely every route would read as doorless, loudly; if it were quietly narrowed to a handful of forms, that count is what would notice.
>
> The exemption list now holds to one rule: **exempt a path because nothing should ever call it, never because the audit cannot see the call.** Four entries survive — a terms page, an emailed verification link, a medical-ID QR, and the OAuth callbacks, whose address is built by the API and handed to the provider (a `redirect_uri` a client could choose is one an attacker could choose).
>
> ---
>
> ## Tests
>
> Six new files, **154 tests**, **23 injection-verified**. Two of the injections missed on the first attempt and both are recorded in the code: one guard searched the whole file for a word that also appears in the screen's own docstring, so it would have been green whether or not anybody looking at the screen was ever told. That is the fourth time this session the same blind spot appeared, so the fix is now a shared `_markup` / `_prose` helper rather than a habit.
>
> **Suite: 1807 passed** (from 1626 at the start of these rounds).
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #244 — It observes and talks

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/244>

> The gaming lobby and the handoff. **Eight routes, backlog 50 → 42.** Screen **167**.
>
> ## The line
>
> The lobby's entire design is one sentence it publishes about itself — *everything in this lobby observes and talks; nothing in it plays* — and the `never` list spells that out twelve ways. The obvious entries (`input`, `aim`, `macro`) are the dull ones. The four worth reading close routes somebody would otherwise argue for:
>
> - **its own hardware** — *a second machine does not turn a bot into a player; it just moves where the bot is running*
> - **a second controller** — *the same bot with a shorter cable, and a controller nobody is holding is not a player's*
> - **a Bluetooth pad** paired to a console as an input device
> - **a capture card** feeding it the picture
>
> The console renders all twelve verbatim. "No cheating" is not the same statement, and shortening an argument to a slogan is how the argument gets lost — so a test asserts each of those four is still refused *by name*, with its reasoning attached.
>
> ## The uncomfortable card
>
> `GET .../lobby/context` is what a synthetic member is **told** about its own position, and the instruction says openly that some of the others are synthetic too. A model that believes every callsign is a person addresses them as people, and a lobby that reads as five friends when it is one player and four generated voices is exactly the impression this product exists to prevent. The screen shows it to the owner, because that is the only way to check it.
>
> The roster says which members are synthetic **per member** rather than as a count in a corner — everyone in a match is owed that.
>
> ## Two ways to hand a conversation on
>
> The handoff turns out to be the lighter sibling of the referral built in the previous round, and the pair is worth seeing together:
>
> | | referral | handoff |
> |---|---|---|
> | authorised by | a device signature over the bytes | explicit consent |
> | lifetime | one open, ever | until revoked |
> | on revoke | — | the package is **purged**, not hidden |
>
> Neither substitutes for the other, and a product offering only the heavier one would push people to skip it. Consent is a field on the request, so an unchecked box is refused by the server rather than only by a disabled button.
>
> ## Three names near enough to swap
>
> The vocabulary says `kind`; the read and the write both say `member_kind`. The wrong one is a 422 for a missing field, and there is a test for it. A person seats **only themselves** — *an id in a request body is a claim*, checked against the token — and somebody else's profile is refused with a pointer to the lent-skill routes that already ask both sides, rather than half-answering a two-party question.
>
> Building the screen also caught a binding I had written and never called: `leaveLobby` had no button. The parametrised call-site test found it before merge.
>
> ## Tests
>
> `test_it_observes_and_talks.py` — 28 tests. Three injection-verified.
>
> Also made a docstring raw in `clientpaths.py`, which was warning on an escape sequence in prose that quotes a regex.
>
> **Suite: 1626 passed.**
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #243 — A signature over the bytes

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/243>

> Handing a conversation to a clinician. **Twelve routes, backlog 62 → 50.** Screen **166**.
>
> A profile is not a clinician, and the package it assembles says so before it says anything else. Every part of this is built to be awkward in the places where the easy version would be wrong.
>
> - **Prepare releases nothing.** You read exactly what would go, and the challenge it raises **is the hash of those bytes** — so signing it signs this summary rather than a checkbox, and a summary edited afterwards cannot ride the old signature. `display_sha256` covers the words that were on the screen, not just the document: a signature over a document nobody saw is a signature over nothing.
> - **The link works once**, and a second attempt says *when* the first happened rather than quietly working. A replayed link is something the patient should be able to discover.
> - **The clinician writes back one time**, and their words stay theirs — recorded, attributed, and never recited by the profile as its own knowledge.
>
> ## Three pairs, each one wrong variable from a bug that looks like success
>
> | | |
> |---|---|
> | the **referral token** | opens it |
> | the **reply token** | answers it — and does not exist until it has been opened |
> | `envelope_id` | is what gets signed |
> | `signature_id` | is what release checks |
> | **proofing level** | how the identity was checked |
> | `can_sign` | what that actually permits — and a referral is `high` |
>
> The screen shows `can_sign` rather than the tier table, because that is the fact somebody needs when the button is greyed out. `POST /signatures/credentials/{row}/proofing` is how a credential moves up, and the visible consequence is that list growing from `["basic"]` to `["basic","standard","high"]`.
>
> Matching is expertise-first by design — *a cardiologist two streets away is not a substitute for a psychiatrist* — so area filters and location only ranks, and no match is an empty list rather than a near-miss.
>
> ## The route audit's second blind spot
>
> The WebAuthn ceremony is a **page the browser navigates to**. It has to be: WebAuthn refuses a mismatched `rpId` and an opaque origin has none to match, which is why it is a route rather than a string inside the desktop app. So no client "requests" it, and every client that opens it counted as doorless — Windows already had it and still showed on the list.
>
> `clientpaths.py` now recognises `window.open` as the GET it is. One wrinkle worth writing down: the URL must be built as ``getBase() + `/signatures/ceremony…` `` rather than a template opening with an interpolation, or the extractor cannot resolve the literal and the door goes on counting as missing while working perfectly.
>
> ## Driven end to end
>
> In-process against the fake authenticator that already exists for the signature suite — reused rather than rebuilt, since a second copy would drift: enrol, re-proof to `document`, prepare, sign, release, open, reply, read the note back, print the certificate.
>
> ## Tests
>
> `test_a_signature_over_the_bytes.py` — 32 tests: prepare hands out no link; the package names the specialist as synthetic first; the challenge covers what was shown; a self-asserted credential is refused and a document check opens the tier; the link 410s on the second open with the time of the first; the reply token is not the opening token (both directions); the clinician's words stay attributed; a clinical note is readable only by the pair; expertise filters and geography ranks; no match is empty; the certificate keeps the words that were shown; the ceremony refuses without a challenge and carries no token.
>
> Three injection-verified.
>
> **Suite: 1597 passed.**
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #242 — Two questions a mark answers

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/242>

> The profile working for its owner, and what it leaves behind. **Fifteen routes, backlog 77 → 62.** Screen **165**.
>
> Triage, proofreading, composing something to keep, the wearables the watch faces run on, the reviews from people who actually talked to it, correcting your own turn, and the check on any mark.
>
> ## The mark answers two questions, and they can disagree
>
> | field | asks |
> |---|---|
> | `valid` | was this credential issued by this deployment |
> | `content_match` | is this the content it was issued for |
>
> A genuine credential over altered content comes back **`valid: true, content_match: false`**, with a sentence saying so. A screen reporting `valid` alone would call something genuine at the exact moment the server said it had been changed — the one failure a provenance check must not have, because it is worse than having no check at all. The screen asks both, always, and draws the mismatch loudest. `GET /watermarks/{id}` correctly omits `content_match` entirely: it never saw any content, and a field defaulting to true would be a claim it cannot make.
>
> ## Two arguments rendered verbatim
>
> **A room-facing microphone is refused with a paragraph, not a shrug:** a smart speaker *hears whoever walks into the room, and they did not pair it, were not asked, and may have a right not to be recorded*. "Unsupported device" would be the console throwing away somebody's reasoning. The refusals are published on the *read* too, so the screen can say why a device is absent from the picker rather than letting somebody find out by failing.
>
> **Triage returns the reason each item survived**, with its score. `_score` in `assistant.py` is arithmetic anybody can read, deliberately. A pile sorted by a number nobody can see is a pile somebody has to re-check by hand, which is the work triage was supposed to do.
>
> `answers_stale_text` is drawn as well — a reply written before the message above it was edited says so, rather than the conversation quietly rewriting itself.
>
> ## Two smaller finds
>
> - **`include_revoked` was never bound.** `wearables.py` promises *unpairing is a revocation, not a delete — the row stays with `revoked_at`*, and without that parameter the console could never show it. A kept promise nobody can see may as well not have been kept. There is a checkbox now.
> - **The route audit could not see `fetch`.** `req()` serialises JSON, so a raw-bytes upload has to call `fetch` directly — and `POST /profiles/{id}/media` had a working door while still counting as doorless. `clientpaths.py` now recognises both call forms, which closes a blind spot the audit had for any call made outside the JSON helper.
>
> ## A guard I had to write twice
>
> The first version of the stale-answer check searched the whole file for `answers_stale_text` — which also appears in the docstring and the type, so it passed after the markup stopped reading it. Same vacuous shape as last round's dial test, caught this time by injection before merge rather than by a broken build. It checks the render site now.
>
> ## Tests
>
> `test_two_questions_a_mark_answers.py` — 35 tests: valid and content_match disagree correctly; the bare record makes no claim about content; an unknown mark says it was not issued here; triage quotes its scores; proofreading returns the change and a mark; a composed work is kept and marked; the room-mic refusal keeps its reasoning and is published before anybody tries; unpairing keeps the row and `include_revoked` is the only way to see it; a wearable is addressed by name and not id; a review needs somebody who actually talked; the empty rating carries a sentence rather than a phantom zero; an edit marks the reply that answered the old wording; retracting needs a body saying who.
>
> Four injection-verified.
>
> **Suite: 1564 passed.**
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #241 — A write that answers 200 did something

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/241>

> The owner's workshop — source material, the dials, a CV, the specialists a profile hands work to, the bodies it speaks through, and the local fine-tune that folds it all back in. **Twelve routes, backlog 89 → 77.** Screen **164**.
>
> Not one of them had a caller. The profile could be created and talked to, and everything that made it *this* profile rather than a default one was unreachable.
>
> ## The defect, twice
>
> Two of these writes were **silently permissive**, and it is the same shape both times — a Pydantic model where every field has a default, so a body it does not understand is accepted, discarded, and answered `200`:
>
> | route | takes | the guess |
> |---|---|---|
> | `PUT .../steering` | `values` | `dials` — what the *read* calls its catalogue |
> | `PUT .../experience` | `period` | `years` — what anybody writing a CV form reaches for |
>
> Neither produced an error. The row saved with no dates, the dials did not move, and both requests looked exactly like successes: same status, same shape, plausible body. Nothing in the response distinguished *I applied your change* from *I ignored it*, so a client that fired and moved on would never find out.
>
> Both models are strict now, so a wrong key gets a 422 naming the field. But **the strictness is the fix, not the guard.** The guard has to be the thing that would have caught it in the first place, which is writing and reading back — that is what the new test file does, and its name is the rule.
>
> ## The part worth reading twice
>
> Making the models strict broke a test that had been green for years.
>
> `test_the_menu_matches_the_kitchen` has a case named *every dial the server describes can be set*, whose docstring says "a dial described but not settable is a slider that throws when moved". It sent `{"dials": {name: 50}}` and passed on every dial — **while setting none of them.** The server accepted the body and ignored it, so every dial "worked".
>
> The guard was green for exactly the same reason the bug was invisible. It no longer trusts the status: it moves each dial off its current value and asks the server what it holds. Injection-verified against a `set_dials` that does nothing — which the old version could not catch.
>
> ## And a third, in my own screen
>
> The picker for what a profile speaks through offered `screen`, `wearable` and `vehicle`. The enum is `speaker, earpiece, hologram, robot, humanoid, other`. Each wrong option sat in the dropdown looking exactly like a right one and would have 422'd on submit — a wrong option is indistinguishable from a right one until somebody presses it. Caught by a runtime test, then guarded properly: a test reads the `Literal` off `EmbodimentAdd` and checks the console's option list against it.
>
> ## Rendered, not summarised
>
> - **A source's content**, when it is there — because *there* means readable, by this platform, by whoever operates it, and by a lawful request. A tick saying "stored" would hide which side of the custody line the account is on. The screen says `Stored in the clear on this deployment — that is what you are looking at`;
> - **the fine-tune's answer**, which is mostly claims about what did *not* happen (`external_transmission: false`, `computed: "locally (embeddings recomputed on-host…)"`). Those are the reason the feature reads the way it does, so they come from the response rather than from the console's own authority;
> - **the identity signature.** `GET .../embodiment-consistency` needs no account, deliberately — somebody who met the profile through a speaker can check it against the one they met in a room. A test asserts the binding stays token-free, because adding one would work and would quietly make a public verification surface private to the one person who does not need it.
>
> ## Run
>
> Driven against a running backend first, then in Chromium: a source added and shown in the clear, a CV line that kept its dates, an embodiment bound from the real enum, a fine-tune reporting nothing transmitted, a dial moved and read back at 80, and guidance from a scene arriving with its watermark line. Form-clearing after submit was added when the drive showed the source form keeping its contents.
>
> ## Tests
>
> `test_a_write_that_answers_200_did_something.py` — 32 tests: both writes read back; both refuse the key they used to drop; the robot route is covered by the same shared model; source material agrees with itself about vaulting from both ends; the source kind enum is closed; the plural specialist route takes one pair; the fine-tune keeps reporting what did not happen; the consistency check needs no account; an embodiment says whether it can answer for itself; guidance carries its mark; and every option in the picker is a kind the server takes.
>
> Six injection-verified, including the corrected menu test against the exact silent no-op it was blind to.
>
> **Suite: 1528 passed.**
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

