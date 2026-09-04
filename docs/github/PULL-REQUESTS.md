# qrme — pull requests

Every pull request opened against <https://github.com/davidsbianchi1984/qrme>, newest first, with the body as written. The body is the argument for the change; git keeps the diff but not the argument.

**351 pull requests, 348 merged.**

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

## #240 — Bodies, and where a rated profile is marketed

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/240>

> The two blocks left from the placements/robots backlog. Eleven routes, doorless backlog **100 → 89**. Screens **162** and **163**.
>
> Both were built by driving the running server, and both had a trap that a route signature hides.
>
> ## 163 — Bodies
>
> The native shells already drove the catalogue, the binding and a command button, so the three routes describing what a body has *become* had no caller anywhere. Three list-shaped things here have almost the same name and mean different things:
>
> | | is |
> |---|---|
> | `robot.commands` | what this model of body accepts at all — the buttons |
> | `GET /robots/{id}/commands` | the audit log of what it was told to do |
> | `GET /robots/{id}/skills` | task modules from a pack, which **extend** the first list |
>
> A screen built from the route names puts the log where the buttons belong, and it typechecks.
>
> **The steering write takes `values`, not `dials`.** `SteeringSet` is `{values: dict}` with a default of `{}`, so a body keyed anything else is accepted, ignored, and answered `200` with the dials unchanged — no error, no log line, nothing to notice. `dials` is the obvious guess because that is what the *read* calls the catalogue. Found by writing and reading back; both halves are guarded now.
>
> Each installed skill's `procedure` renders verbatim, because every one of them names what the body will *not* do — *reminders only: never dispense*, *companionship, not care, and never a substitute for human contact* — and that limit is the sentence somebody pointing a robot at a relative needs to read. `behavior_profile` is drawn beside the dials: pace becomes motion eagerness, autonomy becomes initiative, assertiveness becomes firmness. It is the difference between a slider and an explanation.
>
> Steering is Pro-gated, so the 402 lands as the upsell card added last round.
>
> ## 162 — Where it is marketed
>
> An adult-mode profile advertised at an adult venue — a creator platform, a directory — as a link or a printable code. Only defensible because of the sentence every venue carries, rendered verbatim and never paraphrased:
>
> > every summon of a rated profile resolves through QRME's 18+ age wall, regardless of where the QR or handle was found
>
> The wall does not travel. Shortening that to "18+" drops the load-bearing half, so a test asserts the clause is still on every venue and that the console renders `v.note` rather than keeping a second copy.
>
> Three things only the running server showed:
>
> - **`scan_url` and `summon_url` are not interchangeable.** One is where a phone camera lands and what the code encodes; the other is the JSON surface for clients. Publishing the wrong one hands somebody a page of JSON, so the screen labels both;
> - **`funnel.chat_rate` is null, not zero**, until something has got through the wall. `(null).toFixed()` is `"0"` in JavaScript rather than an error, so an unchecked screen publishes a conversion rate nobody measured. It reads *"nothing has got through yet, so there is no conversion to quote"*;
> - **taking a placement down deactivates the beacon rather than deleting it** — a code already printed at a venue stops resolving instead of being reissued to point somewhere new. That is the safety property, and the screen says it as it happens.
>
> The list and create shapes differ on both surfaces, so the screens derive what they show rather than assuming the richer response came back. The placement list's link is labelled **"open here"** on purpose: the published address uses the configured public host and this one uses whatever API the console is pointed at — same route, different host, and quietly calling this one "the link" would hand somebody the wrong address to print.
>
> ## Run, not just built
>
> Both screens driven in Chromium against a live backend: a body bound, commanded (`tidy` → queued, and in the log a second later) and steered; a placement made, its QR fetched from the API and rendered at 296×296, the funnel read with the null rate reported as an absence. Every tab including the two new ones verified clickable at 1200px and 800px — the sidebar reservation added last round still holds with two more entries in it.
>
> ## New tests
>
> `test_bodies_and_placements_have_doors.py` — 35 tests. The steering write reads back; a dial clamps rather than refusing; intimacy is never a body dial; the dials become a behaviour profile; the three lists stay three different things; a disallowed command is refused *by name* (which is why the screen can show buttons); unbinding says unbound rather than deleted; every venue still carries the clause; only an adult-mode profile is placed; both urls exist and differ; the list shape stays different from the create; the rate is absent rather than zero; walled + verified sums to scans; a takedown 410s the printed code; and the console half of each.
>
> Four injection-verified against the exact defect each describes: gutting `set_dials`, sending `{dials:…}`, dropping the null check, and softening the venue clause.
>
> **Suite: 1495 passed.**
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #239 — A door for the guide, a refusal with its structure kept, and the plan it names

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/239>

> Three commits, each one found by building the door to the one before it. Doorless backlog **116 → 100**.
>
> ## `4677a10` — A door for the guide itself
>
> Twelve routes: the walkthrough (×7), the help topic index, and the helper dock (×4). The least comfortable set to have found — the product has a written walkthrough that works with no model configured, names the screens each step is about, and is held to the gallery by a test, and there was no way for anybody to take it. Screen **160**, `Guide.tsx`.
>
> Building it produced its own mistake immediately: the lesson introducing the walkthrough said it was "thirty-eight written steps", which was true when the sentence was typed and false one line later. `test_lessons_do_not_count_themselves.py` guards the shape rather than correcting the number — a count in prose is a fact about a collection embedded in a member of it, so the act of adding a member falsifies it. The live number is `total` on `GET /tutorial/progress/{id}`.
>
> ## `ad11fa3` — Keep the structure of a refusal that was built to have one
>
> Several gates answer with an **object** rather than a sentence:
>
> ```
> {"reason": "plan", "capability": "builders", "needs": "pro", "have": "free",
>  "price_usd": 130, "period": "month", "message": "…",
>  "billing": "simulated — no real funds move"}
> ```
>
> Somebody built that on purpose — it is strictly more work than returning a string and the only reason to do it is so a screen can draw a real answer. `req()` then did `JSON.stringify(detail)` and threw the result as the error message, so every screen that catches an error and shows `.message` showed the raw object. Nothing failed: the request was right, the refusal was right, and it was destroyed on delivery.
>
> `RequestError` carries `status` and the untouched `detail`, `planGate()` reads the structure back out, and `Refusal.tsx` decides how to draw it. The price and *simulated — no real funds move* render on the same line, because a screen quoting $130 a month without them would make a claim this product avoids everywhere else.
>
> ## `564457e` — The plan a refusal names
>
> Drawing the refusal properly found the next thing: there was **no plans surface**. `GET /plans` and the three `/memberships` routes had no caller either, so the console could refuse you for not having Pro and had no way to sell you Pro. That is worse than a flat no — an offer naming a plan in a product with no way to join one advertises something that appears not to exist.
>
> `Plans.tsx` is that door (screens **130**, **131** — already drawn, never claimed by a component), and `onPlans` is threaded from the shell into every screen that can be refused.
>
> Fixing the transport was also only half of it. Every screen threw the same structure away one layer up — `setError((e as Error).message)`, in all of them. They now hold the error and hand it to `Refusal`, which keeps each screen's existing look for an ordinary failure and draws a gate as a card with a button. A test fails on the flattening pattern reappearing anywhere under `app/src`.
>
> Driven against a running backend first. Two things only the live server showed:
>
> - **`period` is null on the unpaid tiers**, not `"month"` at zero — a screen printing "$0 a month" would be inventing a subscription;
> - **`visitor` and `free` are different plans that both cost nothing.** One is somebody with no account reading a public page; the other is an account whose work sits in the platform's database in the clear. A picker written from the price alone collapses them into one $0 row and hides the entire argument.
>
> Then clicked, in a real browser, which found one more. The always-on agent-lights widget is fixed to the bottom-left corner **on top of the sidebar**, and the column had grown long enough that its last three tabs were underneath it — Playwright reported the click landing on the lights. That is the same fault the phone layout was fixed for in an earlier round, when the widget covered Home and Chat and the tabs were reported as broken screens; the desktop half had simply not grown into it yet. The sidebar reserves the widget's footprint, and the test asserts the arithmetic rather than the number so the next tab is safe.
>
> Verified end to end against a live backend: a free account pressing **Buy** on a listing gets a real 402, the card renders as `PRO — marketplace` with the sentence, the price and the billing note, and **See the plans** lands on the Plans screen.
>
> ## New tests
>
> | File | Tests | What it guards |
> |---|---|---|
> | `test_lessons_do_not_count_themselves.py` | 42 | no lesson (or README, `help.py`, `api.ts`, or any `.tsx`) states how many lessons there are |
> | `test_gates_answer_in_a_shape_a_screen_can_use.py` | 12 | the gate still answers with the object, and `req()` does not stringify it again |
> | `test_the_refusal_has_somewhere_to_send_you.py` | 21 | the four plan routes have a caller, `visitor`/`free` stay apart, capabilities stay keyed the way the gate refuses, the shell threads `onPlans`, no screen flattens the error, the sidebar reserves the widget |
>
> All injection-verified — each guard was confirmed to fail against the defect it describes.
>
> **Suite: 1458 passed.**
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #238 — A door for contesting a profile that depicts you

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/238>

> Nine routes with no caller, including the takedown path for a product whose whole subject is synthetic people who can be mistaken for real ones. Somebody who found a profile of themselves had no way, from here, to say so. The doorless backlog falls **125 → 116**.
>
> ## Two properties, side by side, because either alone would be unfair
>
> **Opening an objection restricts the profile immediately** — public surfaces off, no new interactors — *before* anybody reviews it. Waiting out a review while the thing you are contesting goes on meeting people is not a protection.
>
> **`prior_status` sits right beside it**, because that restriction is only defensible if it is reversible: a dismissal puts the profile back to exactly what it was, active or a departed memorial.
>
> ## Objecting needs no account, and the screen says so
>
> The route is public on purpose. A person who has just found a profile of themselves should not have to join the platform hosting it in order to object to it. What they give instead is a proof reference pointing at an identity check held elsewhere — not a login, which is precisely what lets them object without one. Left unsaid, most people would assume they had to sign up first.
>
> ## The audit panel states `vault_backed` in words
>
> *Tamper-evident* is a claim that depends on a PDI vault being configured. Where none is, the timeline is still the timeline and nothing is hash-chained — showing the events without that caveat would overstate what the deployment actually has.
>
> ## The two shortcuts, with their asymmetry named
>
> The subject may **withdraw consent**; an estate may **revoke authorization**. Both skip review entirely and terminate the profile at once, even mid-review, because a standing party's rights outweigh preserving it. Each applies to one rights basis only, and the refusal on the wrong basis names the profile's actual one.
>
> ## Checks
>
> - 1383 passed — full suite
> - 15 response shapes verified field-by-field against a running server, including the behavioural claims the screen makes: that opening really does restrict at once and record the prior status, that dismissal really does restore it, that uphold terminates, and that a shortcut used on the wrong rights basis names the profile's actual basis in its refusal
> - `npm run build` and `tsc --noEmit` clean
>
> Follows `8fa5989`, which fixed the fail-open on the reviewer gate these routes sit behind — kept as a separate commit so it is reviewable on its own.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #237 — Reviewer development mode meant everybody, not localhost

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/237>

> `auth.require_reviewer` guards the two most destructive operations in the product:
>
> - `POST /objections/{id}/resolve` — upholding **terminates a profile and erases its content**
> - `POST /profiles/{id}/succeed` — **hands a profile to a different owner**
> - (and `GET /objections/{id}/audit`, which quotes the objector's stated reason)
>
> Both sit outside profile ownership on purpose — an owner must not adjudicate an objection against their own profile — so the gate is a deployment secret, `QRME_ADMIN_TOKEN`.
>
> **With that variable unset the function returned unconditionally, for any caller from any address.** On a deployment where nobody set it, an anonymous caller on the internet could erase any profile and take ownership of any profile.
>
> ## Why this is worth more than the four lines it took to fix
>
> **The docstring was the bug.** It said:
>
> > Unset = development mode (open, for local use only), matching PDI's admin convention
>
> Nothing enforced the local part. And it did not match that convention — `cloudgw._caller` has had the localhost check the whole time:
>
> ```python
> if not configured:
>     host = request.client.host if request.client else ""
>     if host in _LOCAL_CALLERS:
>         return "local-dev"
>     raise HTTPException(503, ...)
> ```
>
> The code did what it claimed in every respect except the one that mattered, which means reading it carefully is exactly how somebody would have concluded it was fine.
>
> **It failed open on the deployment least able to notice.** An operator who configured the token was never affected. An operator who had not — a first deploy, a staging box that got a public address, anybody following a quickstart — was the one exposed.
>
> ## The fix
>
> Fails closed the way the gateway already did: a local caller keeps the development path, a remote one gets a **503 naming the variable to set**, so the refusal is actionable rather than merely closed.
>
> ## Tests
>
> `test_reviewer_dev_mode_is_local_only.py`, 10 tests, verified by reverting the fix and watching 4 fail. They cover both halves plus two cases that are easy to lose:
>
> - **a configured token still gates by the token** — the address must not have quietly become the check, so a local caller with the wrong token is still 403 and a remote caller with the right one is allowed;
> - **the owner-fallback path still works.** `_require_owner_or_reviewer` is written as `except HTTPException: … require_owner(...)`, so making the reviewer check raise in a new case changes which branch a real request takes. An owner reading their own case must still get through.
>
> ## Checks
>
> - 1383 passed — full suite (up 10)
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #236 — Doors for what is live in a place, and one rule under three features

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/236>

> Twenty routes with no caller: a camera being shared, a microphone lent to the profiles in a room, a face drawn over a camera. Three features that look separate and are one, because the same rule holds all of them — **whatever you put between yourself and the people around you, they are told.** The doorless backlog falls **145 → 125**.
>
> ## Three things rendered verbatim
>
> Each is an argument the backend already made carefully, and a paraphrase would be a worse version of it.
>
> **The `never` list on a live session.** A viewer cannot zoom, focus or switch lens; cannot take a photograph or start a recording from their side; cannot reach any other camera on the device or network; gets no coordinates; cannot begin a session without the holder starting it in the moment; and there is no state where it is running and not visible on the holder's own screen.
>
> **The refusal when a profile is asked to watch a person's body** — a paragraph about accountability rather than a rule name, and the most important sentence in the feature:
>
> > A profile watching a body in real time would be making judgements about it with no examination, no accountability and nobody to answer for being wrong — and unlike a still, there is no moment somebody chose to send.
>
> The screen shows it *before* the button, not after the attempt.
>
> **`why_it_is_yours` on the bystander note.** The platform declines to promise anything about who walked into shot, because it cannot see the room. A reassurance about something it cannot observe would be worth nothing, and saying so is the honest version.
>
> ## A bug this found in my own screen
>
> The camera and the microphone accept **different sets of surfaces**:
>
> | | surfaces |
> |---|---|
> | camera | `connection, desk, exchange, room` |
> | microphone | `connection, desk, party` |
>
> A watch party takes a lent microphone and refuses a shared camera; a room takes a camera and lends microphones through its own route. The first version of this screen had one picker built from the microphone's vocabulary, so sharing a camera into a party would have 422'd every time.
>
> Invisible to the typecheck — they are strings on both sides — and caught only by driving it. There are two pickers now, and the verification asserts the two sets *differ* rather than quietly using whichever happens to work.
>
> ## Checks
>
> - 1373 passed — full suite
> - 30 response shapes verified field-by-field against a running server, including that the overlay disclosure really does contain "a real person is underneath", that `liveCameras` returns a bare array rather than a wrapper, and that a profile watching a person is refused with the whole paragraph
> - `npm run build` and `tsc --noEmit` clean
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #235 — Doors for how a profile presents itself, everywhere it is seen

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/235>

> Twelve routes with no caller, across three audiences that are not the same audience: the page somebody builds, the front page a stranger lands on from a scan, and the fixed screens the profile is shown on. The doorless backlog falls **157 → 145**.
>
> ## `/pages/themes` was written for a door that never got built
>
> It publishes the allowed HTML tags and CSS properties, with this comment beside them:
>
> > Published so an editor can grey out what it knows will be stripped, rather than letting somebody write it and lose it.
>
> Nothing was reading them. So the editor now lists the surviving tags **before** you write, and shows `html_removed` after a save — because the save succeeds either way. Without that, a `<script>` disappears and the page quietly does less than its author wrote, with no indication it ever contained anything else.
>
> Same reasoning for `about_blocked`: the owner's view carries moderation's reason so the text can be fixed rather than silently dropped.
>
> ## The display asymmetry, made visible
>
> What a given screen is **showing** is public — a fixture in a corridor displays to whoever walks past and cannot keep a secret from them. The list of an owner's screens is **not**, because that is a list of physical places. Two routes that look alike and are not, so the screen says which is which instead of rendering both as ordinary rows.
>
> The `never` list is rendered verbatim — what a fixed screen may never show, each entry with its reason. A wall panel is read by people who did not choose to look at it, and those sentences are that argument already made once, carefully. The backend refuses a forbidden face with the reason rather than the rule, for the same reason, and the screen passes it straight through.
>
> ## Scope changed mid-round, deliberately
>
> Placements were in the original cut. Reading `qrme/routers/summon.py` showed `/profiles/{id}/placements` is the **adult-venue marketing** surface — age wall, custody chain — not general placement. It does not belong in a screen about themes and wall panels, so it comes out and gets its own round rather than being a third of this one.
>
> ## Checks
>
> - 1373 passed — full suite
> - 21 response shapes verified field-by-field against a running server, including that a forbidden face is refused **with its reason**, that `html_removed` actually names the stripped tag, and that removing a display leaves the record at `live: false` rather than erasing it
> - `npm run build` and `tsc --noEmit` clean
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #234 — An identity door, and two refusals that never reached the caller

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/234>

> Twenty routes with no caller, covering who a profile is and how it ends — including `DELETE /profiles/{id}`, so the console could make a profile and never remove one. The doorless backlog falls **177 → 157**.
>
> ## The screen (`156`)
>
> Arranged around the rule the feature turns on: **at most one of your profiles may be verified, because the badge says you are a particular real person, and said of two at once it is either false of one or a claim that you are two people.**
>
> So the roster comes first, and the badge is drawn as a thing that *sits on one profile and moves* rather than a checkbox each profile has and most fail. An invented person reads as **unverifiable** rather than as an empty box — those are different answers, and only one of them means somebody has not got round to it.
>
> The anonymity card puts `not_withheld` beside `withheld` at the same size. Anonymity here is a promise about what the platform publishes, not a promise that nobody can recognise your writing, and a screen showing only the first half would be selling the second.
>
> Both endings sit together because the difference is what happens to the people who knew the profile. Retiring leaves that readable; deleting returns a count per kind of record — twenty-five of them — which the screen itemises rather than summarising. *Deleted* is a claim; the numbers are evidence.
>
> ## Two backend bugs, found by building the door against it
>
> **A 500 with an empty body.** `POST /profiles/{id}/verification` caught `identity.IdentityError` and not `verification.VerificationError`. The two come from adjacent modules and only one was in the `except`, so an unknown proofing level — or a level above `self_asserted` with nobody named as having checked — raised straight through.
>
> The part worth recording: the exception it dropped carried the exact sentence the caller needed, naming all four valid levels. The work of explaining had been done and was then discarded by the wrong handler, which is worse than never writing it, because everything upstream looks careful.
>
> **An undiscoverable enum.** `GET /identity/vocabulary` is the route whose whole job is publishing the closed sets a client must offer. It described every rule about verification — who may hold the badge, that it moves, that an invented person is unverifiable — and omitted the four words a claim has to be made in. There was no way to build a level picker from the API; you had to read `qrme/verification.py`.
>
> Both are pinned by `test_verification_refusals_reach_the_caller.py` (8 tests), verified by reverting each fix and watching three fail. One test asserts the set the vocabulary *advertises* is the set the claim endpoint *accepts* — otherwise the fix is the original bug with a step added. Another asserts the 409 for the one-badge rule survived: a malformed claim is the caller's mistake, the one-badge rule is the product refusing something well-formed, and only the second tells you what to do instead.
>
> ## Two routes deliberately keep no door
>
> They stay in the backlog rather than getting buttons that lie:
>
> - `POST /profiles/{id}/succeed` needs a **reviewer** token by design — succession runs when the owner cannot authorise anything, so a button on the owner's own screen would 403 every press;
> - `POST /profiles/genesis` is a second creation path (a profile born from a short interview, which names itself). It belongs beside the first one in onboarding, not on a screen about a profile that already exists.
>
> ## Checks
>
> - 1373 passed — full suite (up 8)
> - 28 response shapes verified field-by-field against a running server, including the case that matters most: a profile both **verified and anonymous**, where `/badge` drops the attestor and returns `attestor_withheld` — "checked by Dr Okafor of St Mary's" would narrow an anonymous author to a city and a workplace
> - `npm run build` and `tsc --noEmit` clean
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #233 — Doors for the three two-party surfaces, and four tabs that showed their own key

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/233>

> Twenty-eight routes had no caller: the agreed exchange, the lent skill and the watch party. All three modules were complete and unreachable from the console. The doorless backlog falls **205 → 177**.
>
> ## Each screen is built around its feature's rule
>
> The mechanics are obvious and the constraint is not, so the constraint is what the screen has to carry.
>
> **Exchanges** (`153`) re-renders the whole agreement from every reply rather than patching what is on screen, so an edit that clears both signatures is something you *watch happen*. A screen that optimistically appended a row would show a signed agreement the server had already un-signed — precisely the failure the fingerprint rule exists to prevent. The `runs_warning` sits next to the signing button rather than in the manifest, because the moment to read it is before agreeing.
>
> **Lent skills** (`154`) never disables the close button by side. Two people open a grant, either one alone closes it, and the moment withdrawal matters is exactly the moment the person benefiting would not agree to it. The use log goes to both parties: a record only one side can read is not a record.
>
> **Watch together** (`155`) renders the profile's prompt instruction verbatim, in a panel of its own. A person whose profile is sitting in a room discussing a film can read what it was actually told about not having seen the video, instead of trusting that it was told anything.
>
> ## The types were checked against a running backend
>
> Written from the route signatures first, then driven against a live server — which is the only reason two of them are right:
>
> - `signatures[]` carries **`matches_current`**, the server's own computed answer to whether a signature still applies. Not the `fingerprint` field written down here from the signature alone, which does not exist on the wire — and which the screen was going to approximate by comparing truncated hashes by hand. (It is `true` in every reachable state today: the manifest can only be edited from `draft`, and `reopen` deletes the signatures on the way. So it is the backend checking its own invariant rather than assuming it, and the type says that rather than implying a live signal.)
> - `POST /exchanges/{id}/items` returns the **whole exchange**, not the item — so the new item's id comes out of the returned manifest.
> - `POST /watch-parties/{id}/members` likewise returns the whole party.
> - `channel` has **two different shapes** depending on `open`, so `ExchangeChannel` is a union rather than one type with optionals.
> - `POST /watch-parties/{id}/end` returns a summary of what it shut down and nothing party-shaped.
>
> A typecheck proves the code agrees with what was written down. It cannot prove what was written down is true. 34 shapes verified field by field on a live server.
>
> ## Four tabs have been rendering their own identifiers
>
> `t()` ends `|| key`, so a tab with no entry puts `nav.market`, `nav.delegate`, `nav.desk` and `nav.voice` in the sidebar — in every language including English. `NAV` carried the correct English `label` one line above the icon, and nothing read it: two sources of truth with the unused one looking authoritative.
>
> It also failed in the direction that hides. A blank label looks broken and gets reported; `nav.market` looks like a name somebody chose, and nobody files a bug about a tab that has a name.
>
> `test_nav_labels_are_localised` now fails on all three ways it can recur — a tab with no entry, an entry missing a language, and the unused `NAV.label` disagreeing with the l10n row. Verified by injection.
>
> ## Also
>
> - Three tutorial lessons, three gallery rows, three `ui_screens.txt` entries, helper-dock keyword routing for all three, and a console-door paragraph in each of the three README sections.
> - `*.db` never covered SQLite's `-shm`/`-wal` sidecars, so running the backend once left untracked noise in everybody's `git status`.
>
> ## Checks
>
> - 1365 passed — full suite (up 6: the new nav guard)
> - 34 response shapes verified against a running backend, exercising both parties, both refusal paths, and the void-on-edit rule
> - `npm run build` clean; `tsc --noEmit` clean
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #232 — Record what breaks on the phone and the desktop shell too

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/232>

> The console has recorded failures content-free since 0.19.0 — the operation and the status, never the message, never the path as it was actually called. The three native shells recorded nothing at all, so every failure a user hit on iOS, Android or Windows was invisible.
>
> ## The rule, in three more languages
>
> | | |
> |---|---|
> | `native/ios/Sources/Problems.swift` | `UserDefaults`, `Codable` rows |
> | `native/android/…/Problems.kt` | `SharedPreferences`, JSON rows |
> | `native/windows/Problems.cs` | `%LOCALAPPDATA%/QRME`, `System.Text.Json` |
>
> Each takes `method`, `path`, `status` and has no parameter a detail string could arrive through. The signature is the safeguard, and it matters here specifically: the backends put user input straight into their error messages — a device name, a body site, a language code. Good messages for the person reading them and the wrong thing to keep, so they are shown and never written down. Redaction happens on the way *in*, so the stored buffer never holds a value that would later have to be scrubbed.
>
> `POST /profiles/{id}/chat → 500` identifies a bug; `POST /profiles/prf_0de08e794ed0/chat` identifies a person. Only the first survives.
>
> ## Why the tests are structural
>
> One rule with four implementations drifts, and it drifts silently — a redaction narrowed on Android leaks nothing on the desktop, so nothing an ordinary test run would notice. There is no test runner for these sources here; the native workflow compiles them and stops. So `test_native_shells_record_nothing_private.py` reads them the way the TypeScript guard reads `errors.ts`: signature arity, stored fields, the four redaction patterns at full width, the FNV-1a constants, and both failure kinds at the call sites — including the request that never reached a server, which is the case an implementation forgets because it is an exception rather than a status.
>
> The suffix bound is checked by name because it has already gone wrong once: requiring six hex characters let `cap_9f2`, `req_77aa` and `usr_1` through when the console's version was written. A shell that quietly restored that bound would leak on that platform alone.
>
> What the file cannot check is behaviour: that Swift's FNV-1a and Kotlin's produce the same digits is asserted by neither, only that both are FNV-1a with the same constants. Stated in the file rather than hidden.
>
> ## The defect writing that guard exposed
>
> `Problems.attach` existed and was called nowhere. The Android shell would have recorded nothing and said nothing about it, because the recorder refuses to crash over a diagnostic — a missing attach has no symptom at all. Every structural check above passed while the feature was simply off on that platform.
>
> Worth naming as a class rather than a typo: those checks ask whether each piece is *correct*, and correctness of every piece is not the same as the feature being *on*. iOS and Windows have no equivalent step — `UserDefaults` and `%APPDATA%` are reachable from anywhere — which is exactly why the third platform's extra wire went unnoticed. `MainActivity.onCreate` now attaches, and `test_the_android_recorder_is_switched_on` fails if that line ever leaves.
>
> ## Scope
>
> These record only. Sending stays the console's job and happens only where a collector was compiled in, so native-shell failures do not reach the gateway aggregate. `native/README.md` says so rather than leaving it to be assumed.
>
> Also carries the previously-pushed gateway container deploy-path commit, which had no PR of its own: `cloudgw/Dockerfile`, the `0.2.0` contract version, and the boot banner that names what an operator has left unset.
>
> ## Checks
>
> - 1359 passed — full suite
> - 19 passed — the new guard, with the attach line removed by injection to confirm it fails
> - 51 passed — route and native path guards, since the recorder reads paths the resolver also reads
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #231 — A marketplace somebody can use, and a guard that stopped inventing work

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/231>

> Thirteen routes — the whole commercial surface, including all of the money path — existed in the backend with no caller. You could not search, place a listing in a town, put a price on one, or buy one, and a seller could not see what they had sold.
>
> **doorless: 218 → 205.** The entire `/marketplace/*` block is closed.
>
> ## The guard was aiming me at work that was already done
>
> I set out to build this door and TypeScript refused a duplicate binding: `api.marketplace()` already existed and Discover had been calling it since it was written. But `GET /marketplace` was on the doorless backlog.
>
> The cause is in `clientpaths.py`. A template literal may nest another inside an interpolation:
>
> ```ts
> `/marketplace${tag ? `?tag=${enc(tag)}` : ""}`
> ```
>
> The backtick alternative was `` [^`]* ``, which stops at the **inner** opening backtick. The captured literal became `` /marketplace${tag ? ``, the query cut landed on the literal `?` inside it, and the call normalised to a path no route matches.
>
> **This is a different failure from every earlier one in that file.** The truncating extractor, the verb read off a neighbouring call, the route table read flat instead of recursed — all made the guard too *lenient*, and those get found by the bug they let through. This one made it **invent work**, which fails more quietly: an invention is found only when somebody goes to do it and discovers it done.
>
> One route out of 218 here and none in jim-mini or pdi, so the guard was substantially right. The distinction is now written into the file, because the quiet direction is the one worth naming.
>
> Interpolations are matched by counting braces, and the optional-query marker recognises a backtick as well as a quote — the same idiom is usually written with a nested template.
>
> ## Every shape probed, not read
>
> Two would have been wrong from the route signatures alone:
>
> - the offer takes **`price`**, not `price_cents`
> - `settings/{id}` wants an **interactor** id, not a profile's
>
> The whole path was driven end to end against a running server:
>
> ```
> PUT  offer      -> seller_id is the caller; pricing is what establishes the seller
> POST purchase   -> 422 "this is your own listing — buying it would credit you
>                         with your own money and inflate your sales count"
> POST purchase   -> 201 ord_… paid, ledger led_… (as a second party)
> POST purchase   -> 422 "this costs 45.00 GBP; send accept_price=45.00 to confirm"
> GET  sales      -> the seller's statement, one order
> ```
>
> Those refusals turned out to be the best copy on the screen.
>
> ## Two sentences quoted, not paraphrased
>
> The backend states in its own reply that ranking is *"deterministic — title, tags, provider, blurb, in that order. No model reorders this."* and that the money is simulated. The screen renders both verbatim: a marketplace that quietly ranked by something else would be a different product, and money that looks real and is not is the worst thing here to be vague about.
>
> `marketAssist` is shown as suggestions for the search box only — the reply says `applied: false`, and the caption says so too.
>
> ## The surface guard earned itself
>
> The moment `Market.tsx` appeared, last round's guard failed the suite unprompted and would not pass until screen **152 Marketplace** was drawn, given a gallery row and a lesson, and made reachable by the words somebody actually types — "find a plumber", "for sale", "hire". That is the fourth docs catch-up round not happening.
>
> The screen builder also refused a card title that ran off the card, and the dock test refused the lesson until a phrasing reached it.
>
> ## Notes
>
> - No backend changes.
> - Console typechecks and builds; full suite running at time of writing.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #230 — Cut 0.19.1

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/230>

> 0.19.0 shipped its own error-reporting card and first-run notice **with no screen, no lesson and nothing for the in-app helper to point at** — while its release notes described the feature at length. The guard that now prevents that (qrme#229) and the two drawings it asked for landed on `main` after the tag, so they need a version to ship in.
>
> Companion PRs in jim-mini and pdi.
>
> ## The five strings
>
> | File | |
> |---|---|
> | `pyproject.toml` | what pip follows |
> | `qrme/api.py` | `FastAPI(version=…)`, what the release tag follows |
> | `app/package.json` | what the installer filenames and the auto-updater follow |
> | `app/package-lock.json` | **twice** — the lockfile header and the `""` entry under `"packages"` |
>
> `test_docs_gallery.py` asserts all five agree; it passes. Console builds with `0.19.1` in the bundle.
>
> ## What ships in it
>
> **No application behaviour changes.** Screens 150 and 151, their gallery rows, a lesson, helper phrasings — and the guard that fails when a surface ships with none of them.
>
> The guard is the substance. Every gallery test checks screens against the README and none asked whether a surface has a screen at all, so three features had already shipped undrawn and needed a dedicated catch-up round each. `ui_screens.txt` closes that direction: a surface nobody has classified fails in the round that introduces it, and silencing it by writing `undrawn` fails the ratchet.
>
> ## Notes
>
> - Suite green at time of writing; full run in flight.
> - Tag creation stays yours — links follow when this merges.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #229 — Fail when a surface ships with no drawing, then draw the two that did

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/229>

> Companion PRs [jim#176](https://github.com/davidsbianchi1984/jim-mini/pull/176) and [pdi#137](https://github.com/davidsbianchi1984/pdi/pull/137). Two commits: the guard, then the drawings it asks for.
>
> ## The guard
>
> `test_docs_gallery.py` checks screens against the README in both directions — a reference with no file, a file with no reference, a gap in the numbering, a filename a URL cannot carry. Every one of them starts from the screens. **None asks the opposite question: does this surface have a screen at all?**
>
> So a feature can ship with nothing drawn, nothing taught, and nothing for the helper to point at, and the suite stays green. That is not hypothetical — it has happened three times. Voice cloning, the recoverable watermark and the chat role picker each went two versions undrawn and needed a dedicated catch-up round (#100). Then the error-reporting card and its first-run notice shipped in 0.19.0 exactly the same way, while the release notes described the feature at length.
>
> It is the same shape of flaw this suite has found twice elsewhere: **a guard that only walks the relation in the direction where the answers already exist.** The doorless audit was a route with no client door. The redaction check read `doorless_routes.txt`, which shrinks as doors are built, and would have gone vacuous the day it emptied.
>
> `ui_screens.txt` is the missing direction. Every surface under `app/src/screens/` and every top-level surface component carries a screen number, `undrawn`, or `unaudited`.
>
> **Why the mapping is declared rather than inferred.** Matching component names against screen titles resolved only **ten of twenty-four**, because titles are written for the person using the app ("How Should They Work?") and component names for the person editing it ("Delegate"). Guessing the rest would have produced a mapping that looked complete and was not — the exact failure mode this round exists to close. `unaudited` is the honest seed for components that predate the file, and it is not a status a new component may use.
>
> **Both backlogs are ratcheted against a ceiling each repo declares for itself.** This test is byte-identical across three repositories with different backlogs, so one hardcoded number would be the largest of the three and leave the other two slack to grow into. A ceiling left high after the backlog falls fails too: a ratchet that stops ratcheting re-opens the ground it gained.
>
> Verified by injection, five ways — the second is the one that gives the first its teeth:
>
> ```
> unclassified surface                          -> fails
> silenced by writing `undrawn`                 -> fails (the ratchet)
> mapping points at a screen that doesn't exist -> fails
> typo'd status ("undrwan")                     -> fails
> component deleted, entry left behind          -> fails
> raising the ceiling deliberately              -> passes, and shows in the diff
> ```
>
> That last one is deliberate. Raising the ceiling is one line saying plainly that the backlog grew, which is a conversation worth having rather than one a test should win on its own.
>
> ## The drawings
>
> Screens **150 What Went Wrong** and **151 Before Anything Is Sent**, with gallery rows, a lesson, and `DIRECTIONS` phrasings for the words somebody actually types when something has broken — "it failed", "something broke", "stop sending", "opt out".
>
> The card draws an operation and a status and nothing else, because that is all the log holds. Drawing a message there would depict a product that does not exist.
>
> Both surfaces move off `undrawn`, and the ceiling drops to zero with them.
>
> ## Two existing guards earned their keep
>
> The screen builder **refused a card title that ran off the card** (`'Sent when the app opens' needs 187px, has 155px`), and the dock test **refused the lesson until a phrasing reached it** (`no phrasing reaches 'problems'`). Neither is new. They are the directions this repo was already checking — which is precisely what made the missing direction worth building rather than assuming.
>
> ## Notes
>
> - No backend behaviour changes: screens, gallery, lesson, helper phrasings and the new guard.
> - Suite green: **1340 passed**, up from 1334 — exactly the six new tests, nothing else moved.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #228 — Cut 0.19.0

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/228>

> 0.18.0 is already released, so the error-capture and send work merged in qrme#226 and qrme#227 had nowhere to ship. Cut with the siblings so the suite carries one version. Companion PRs [jim#175](https://github.com/davidsbianchi1984/jim-mini/pull/175) and [pdi#136](https://github.com/davidsbianchi1984/pdi/pull/136).
>
> ## The five strings
>
> They move together, as the releasing checklist says and as each of them has drifted at least once before — pyproject sat at 0.4.0 through the 0.4.1 cut, the lockfile roots at 0.3.3 through two:
>
> | File | |
> |---|---|
> | `pyproject.toml` | what pip follows |
> | `qrme/api.py` | `FastAPI(version=…)`, what the release tag follows |
> | `app/package.json` | what the installer filenames and the auto-updater follow |
> | `app/package-lock.json` | **twice** — npm writes the root version in the lockfile header *and* in the `""` entry under `"packages"` |
>
> `test_docs_gallery.py` asserts all five agree; it passes. Console builds with `0.19.0` in the bundle.
>
> ## What ships in it
>
> The console records every failed request and, where a build has a collector address, reports it once at launch — the operation and the status code, never the message and never the path as it was actually called. `cloudgw` gains `POST`/`GET /v1/problems` to receive them, refusing anything that is not exactly an error report rather than sanitizing it.
>
> Nothing sends before a first-run notice has been answered, and that notice renders the real payload rather than describing it.
>
> ## Two things found while cutting
>
> **`app-v0.16.0` and `app-v0.17.0` were never tagged.** Only `app-v0.15.0` and `app-v0.18.0` exist on the remote. Two versions were cut in the repo — strings bumped, changelog written, release notes staged — and then never released. The existing `[0.16.0]:` link reference points at a tag that does not exist, so it is already a dead link.
>
> This adds references for `[0.19.0]` (anticipating the tag, as the convention has always done) and `[0.18.0]` (that tag is real, and the reference was simply missing). `[0.17.0]` is deliberately left without one rather than writing a third link to nothing.
>
> **`cloudgw` stays at `0.1.0`.** It gained an endpoint pair this round and its version is what `/health` reports — but it is the gateway's own version rather than part of the product release train, and it has sat at 0.1.0 through every cut. Flagged rather than changed, since that is a convention question. Note the version-consistency test reads `qrme/api.py` specifically, so the sidecar's number cannot be confused for the product's.
>
> ## Notes
>
> - No functional changes in this commit — versions, changelog and release notes only.
> - Full suite running at time of writing; the five-string check and the console build are already green.
> - Tag creation stays yours — nothing here pushes `app-v0.19.0`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #227 — Send the error reports, and refuse anything that is not one

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/227>

> The consoles have recorded content-free failures since qrme#226. This is the other half — they now **send** them, once at launch, alongside the update check, and `cloudgw` grows somewhere to send them to. Companion PRs [jim#174](https://github.com/davidsbianchi1984/jim-mini/pull/174) and [pdi#135](https://github.com/davidsbianchi1984/pdi/pull/135); `errors.ts`, `Problems.tsx`, `ProblemNotice.tsx` and the console test are byte-identical across the three repos.
>
> ## Nothing goes before the person has been asked
>
> Sending is opt-**out**, which only means something if the opting-out can happen *before* the first report rather than being discovered afterwards in a settings panel nobody opened. A switch nobody knows about is not a choice.
>
> So `sendProblems` refuses until a first-run notice has been answered. That notice **renders the actual payload** rather than describing it, from the same function that posts it — prose saying "we only send error codes" would be a claim you have to trust; showing the object means the notice cannot go stale while still reading honestly. Both answers are offered, and it appears only where a build has a collector at all, because interrupting somebody to explain a thing that cannot happen is how people learn these notices are noise.
>
> Driven end to end against a live gateway:
>
> ```
> first launch, notice unanswered   -> awaiting-notice   (nothing sent)
> person clicks "No thanks"         -> turned-off        (nothing sent, ever)
> fresh install, before answering   -> awaiting-notice
>               after "That's fine" -> sent
> ```
>
> The aggregate then held exactly one row — from the install that agreed. The one that declined contributed nothing.
>
> After that first answer it is opt-out as normal: automatic, with the same switch on the Settings card, changeable whenever.
>
> ## Off by absence, not by flag
>
> The collector address is compiled in at build time and unset by default:
>
> ```bash
> PROBLEM_COLLECTOR=https://gw.example.com PROBLEM_TOKEN=… npm run build
> ```
>
> Unset, and the installer has nowhere to send and no code path that could acquire one — a stronger default than a boolean, because there is no address for a later mistake to switch on. The send swallows every failure; a diagnostic that can delay a launch has stopped being worth having.
>
> Sent from the renderer rather than the Electron main process, because that is where the buffer lives — a diagnostic needing an IPC channel of its own has more ways to go wrong than the bugs it finds. It lands beside the update check anyway: `setupAutoUpdate()` runs the moment the window is created.
>
> ## Counts are deltas
>
> Each row remembers how much of itself has been reported, so reopening the app twenty times does not turn one broken screen into twenty. Nothing is deleted after a send — the row is the user's own history. A failed send moves the watermark not at all, and the next launch retries:
>
> ```
> send to a dead collector -> failed,  watermark sent=0 of 1
> retry once it is up      -> sent,    watermark sent=1 of 1
> ```
>
> ## The intake refuses rather than redacts
>
> `cloudgw/problems.py` accepts exactly five top-level keys and five per problem and **422s on anything else** — an unknown field, a `platform` string long enough to hide a sentence, a `day` carrying a time of day, a path with an unredacted id still in it:
>
> ```
> problems[0].op contains 'usr_8752921df161', which looks like an identifier
> rather than a route name. The console redacts these before storing them, so
> this build's redaction is not working. Refused rather than redacted here,
> because redacting here would hide that from the only people who can fix it.
> ```
>
> It could redact that path itself; the pattern is right there. Doing so would let a build whose redaction had broken keep working, with the only signal a server-side counter nobody reads. Refusing is also cheaper here than for contributions next door: a rejected error report costs one lost diagnostic, where a rejected contribution costs somebody their donated work.
>
> ## What survives is less than what arrives
>
> Reports are not stored as reports. They fold into counters keyed by product, version, platform, operation and status:
>
> ```
>   7  jim-mini  GET /users/{id}/captures -> 404
>   3  qrme      POST /profiles/{id}/chat -> 500
>   1  qrme      GET /users/{id}/captures/{id}/image -> 404
> ```
>
> Locale is validated and then **dropped** — every extra dimension narrows a row towards a single install, and platform plus version is what triage actually needs. Nothing records that a particular install sent anything, or when beyond the day. That is also why these counters sit in a plain file while contributions are sealed in PDI: contributions are people's own words; these have no owner to protect, and encrypting them would look careful and mean nothing.
>
> Reading the aggregate needs a narrower permission than writing to it (`CLOUDGW_PROBLEM_READERS`, unset = the local developer only). The posting token ships inside every installer and is public the moment somebody unzips one; a wrong write costs a wrong counter, while reading is a live map of what fails on every build.
>
> ## Four bugs found by checking rather than reasoning
>
> **A gap in the guard itself.** Injecting a `detail` field into the outgoing report was caught — but only by the test comparing the wire shape against the gateway, which runs only in *this* repo. In JIM and PDI, where a leak would cost the most, it would have passed. The five field names are now pinned locally too.
>
> **Every validator was wrong about its own rule.** All the intake's patterns were anchored with `$`, which in Python matches before a trailing newline as well as at end of string — so `Win32\n` and `GET /health\n` were accepted by a validator whose own error message said newlines were not allowed. All now end `\Z`, with a test, because the next person will reach for `$` too.
>
> **No CORS at all** — the one that would have made the rest pointless. The sender posts JSON with an `authorization` header, making it a non-simple request: the browser preflights with `OPTIONS` and refuses the real call unless that is answered. Every preflight would have 405'd, every report would have failed, and because the sender swallows failures the feature would have been dead in the field with nothing to show for it. Found by asking what an Electron renderer's origin actually *is*: `null`, since it loads from `file://` — which is also why no origin allowlist could have been written. Verified by deleting the middleware and watching the preflight test fail.
>
> **A 500 on the read, found by being careless rather than clever.** While driving the client, a scratch file of unrelated JSON got reused as the counter path. The aggregate loaded it — it parsed, after all — and `GET /v1/problems` then died sorting values that had no `count`. Unparseable JSON had been handled from the start; *parseable* JSON of the wrong shape had not, and that is the likelier accident: a half-written file that closes its braces, an older format, a path pointed at something already there. Rows are validated individually on load now, so a bad one is dropped and good ones beside it survive. A test written from imagination would have reached for `"{ this is not json"` again and stayed green.
>
> ## Tests
>
> Twenty-nine on the intake, nineteen on the console module. The notice gate was verified by injection twice — once by removing it, once by moving it to *after* the fetch, which would have looked like a check while being none. Beyond that: counts add across reports, the worst thing sorts first, counters survive a restart, a partly-corrupt counter file keeps its valid rows, the posting token cannot read, and an unconfigured reader list means nobody but the developer.
>
> ## Notes
>
> - No product-backend changes. No new routes on the QRME app, so the doorless backlog is unaffected.
> - All three consoles typecheck and build. Suites: PDI 299 passed / 1 skipped, JIM 745 / 1.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #226 — Record what fails, without recording anything private

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/226>

> Error collection across all three consoles, built so it cannot carry user data. Companion PRs in jim-mini and pdi; `errors.ts`, `Problems.tsx` and the test are byte-identical across the three repos.
>
> ## The obvious version would have broken the promise
>
> Every failed request already passes through one function, so catching them is ~30 lines. The hard part is what a failure may say about itself. These backends put user input straight into their error messages:
>
> ```
> no device called 'Pixel Buds' on this account
> unknown site 'knee'; one of scalp, face, eye, mouth…
> unknown language 'xx'
> ```
>
> Good messages for the person reading them, bad things to keep. In JIM they can be health content. So the message is shown to the user, who owns it, and **is never written to the log**. Same reasoning for the path: `/profiles/prf_0de08e794ed0/chat` identifies a person; `POST /profiles/{id}/chat` identifies a bug.
>
> | Recorded | Never recorded |
> |---|---|
> | operation (`POST /profiles/{id}/chat`) | the error message |
> | status (0 = never reached a server) | ids, tokens, key prefixes |
> | count, date (day only) | request or response bodies |
> | app version, platform, language | timestamps finer than a day |
>
> Redaction happens **on the way in**, so there is no moment at which the buffer holds something that would have to be scrubbed later.
>
> ## Nothing transmits
>
> Local, capped at 50, with a Settings card showing the exact payload — the same object the copy button produces, from one function, so the preview cannot drift from what is copied. The backend ships inside the installer, so for a desktop user there is no server on the other end; a copy and a paste is the honest path, not a limitation to apologise for.
>
> ## Two mistakes caught by testing, not by reasoning
>
> **The redaction under-redacted.** Requiring six hex characters let `cap_9f2`, `req_77aa` and `usr_1` through — three of the first eight real paths. Widened, then validated against **239 real route segments** across the three products to confirm it does not eat route names in the other direction.
>
> **The test checking that had the same shape of flaw.** It read segments from `doorless_routes.txt`, which shrinks every time a door is built — so it would have weakened as the backlog cleared and gone **vacuous the day it emptied**. A test that gets less thorough as the project improves is worse than no test, because nothing announces the moment it stopped meaning anything. It now reads the live route table. Discovering that app by name then picked QRME's `cloudgw` sidecar (10 segments instead of 400); only the floor caught it, so the choice became "the package with the most routes".
>
> ## Twelve tests hold the shape
>
> - `recordProblem` has no parameter a message could arrive through
> - the stored record has no field one could sit in
> - the report's keys are pinned
> - `api.ts` never hands the recorder anything but a status
> - short ids are redacted as well as long ones
> - no real route name is eaten
>
> **Verified by injection**, not assertion: a `detail` parameter added to the recorder, and the redaction narrowed back to six-hex ids. Both caught.
>
> ## Notes
>
> - No backend changes. No new routes, so the doorless backlog is unaffected.
> - All three consoles typecheck and build; suites green (PDI 293 at time of writing).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #225 — A desk you can actually staff

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/225>

> The desk is the one surface in QRME whose promise is a **person** — a real tradesperson, attested by somebody, reachable now. None of it was reachable from a client: you could not open a desk, say whether anybody was behind it, answer the bell, or let a visitor come up.
>
> The new **Desk** screen covers the counter end to end — opening one with the attestation it rests on, presence, rings, guests, the stream overlay, and beacons.
>
> ## Four things stated the backend's way, not the console's guess
>
> **A desk is not a profile.** The API answers `desk_id` and `desk_token`, so the token lives in the screen rather than the shared session — signing in as an owner does not make you the counter, and conflating them would let one person's session speak for a desk they do not staff.
>
> **Away and closed are different promises.** One says come back, the other says the counter is shut. The desk gets to make either, so both are buttons.
>
> **The attestation is shown to its own keeper**, `burned` included. A withdrawn claim is not something to find out about from a visitor.
>
> **Picking up a beacon retires it** — the sticker on the wall stops working. That is the point of picking it up, so the button says so.
>
> ## Probing caught what habit would have got wrong
>
> The desk answers `desk_id` and `desk_token`, **not** `id` and `owner_token`. My first probe used the familiar names and every follow-up call 404'd. Had I written the bindings from habit instead of from a live response, sixteen calls would have compiled, shipped, and failed against a real desk.
>
> ## `view.webp` and the beacon QR are excluded, not doored
>
> Both render in an `<img src>` rather than being fetched by the API client — the same category as the pair and medical-ID codes already in `NOT_A_CLIENT_CALL`. Counting them as doorless would have meant building a door that cannot exist.
>
> ## Coverage
>
> **Eighteen routes off the doorless list, 236 → 218** (16 real doors + the 2 image exclusions).
>
> ## Notes
>
> - `clientpaths.py` stays byte-identical across the three repos; companion commits land the same exclusion in jim-mini and pdi, and both repos' guards were re-run to confirm nothing shifted.
> - Console typechecks and builds; full suite running at time of writing.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #224 — A profile that can act for you, and a way to say how far

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/224>

> QRME's first pass at the doorless backlog — the largest of the three at 252.
>
> The whole authorisation chain existed in the backend with **no caller anywhere**: mint a revocable grant, authorise which phases may run unattended, start a workflow, advance it, answer it when it stops, cancel it. Shipping the acting half without the governing half is the wrong half to ship, and it is the half that shipped.
>
> ## The screen is ordered the way the decision is
>
> 1. **Grants first** — a phase reads the profile's own material *through* one, and it can be withdrawn mid-run. The work stops seeing what the grant covered from that moment, not at the end.
> 2. **The policy second** — it is a choice about scope, not about work.
> 3. **The runs last** — they are what the first two make possible.
>
> ## Three things are the server's judgement rendered, not the console's invention
>
> **The delegable phases come from the server.** `GET /profiles/{id}/delegation` returns them; the client does not retype the list.
>
> **`research` cannot be delegated without a grant.** The backend refuses it outright:
>
> > delegating `research` requires a grant: without one the phase reads every source item on the profile
>
> So the console sends the grant it holds, and lets that refusal reach anyone who has not minted one **with its message intact** — rather than pre-empting it with a guess that would drift from the real rule.
>
> **A stopped run shows what it is waiting for.** `awaiting` is the entire point of the pause: the profile stopped because it needs a person, and it says what for. Answering resumes it in place.
>
> ## Coverage
>
> | Family | Routes |
> |---|---|
> | grants (mint, revoke) | 2 |
> | delegation (get, set) | 2 |
> | workflows (create, list, get, advance, resume, cancel) | 6 |
> | delegated workflows (start, get, advance, resume) | 4 |
> | tasks (run, list) | 2 |
>
> **Sixteen routes off the doorless list, 252 → 236.** Bindings and screen landed together, per the rule in `clientpaths.doorless()`.
>
> ## Notes
>
> - Console typechecks and builds clean; full suite running at time of writing.
> - Every response shape was read off a live response rather than inferred from the handler.
> - Delegated workflows are kept separate from the owner's own on purpose: those are the runs somebody *other* than the owner started, under the policy the owner set.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #223 — Menus that keep their promises, and the routes with no door at all

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/223>

> **This PR now carries two rounds.** The second was pushed onto the same branch while the first was still in CI, so they merge together.
>
> ---
>
> # 1. Every option the backend offers, it now has to accept
>
> A catalog endpoint is a menu. The console and the three shells render it directly, so whatever it lists is what a user can pick. If the endpoint that *consumes* the choice refuses one of those values, the user meets an error for doing exactly what they were offered.
>
> Eight checks now send the request rather than read source: languages in both delivery modes, the same languages as translation targets, the steering dials the server describes, the providers on the model menu, the robots, the connectors, the pack registries. **All accepted — no field bug.** Verified by making `/languages` offer Arabic while the writer refused it, and watching both language tests fail.
>
> Two judgement calls, stated in the tests: a **409 is not counted as a refusal** (the server understood the value and objected to *state*), and an **empty catalog fails rather than passes**.
>
> One approach was tried and deliberately not shipped: matching client literals to backend vocabularies by field name. `role="dialog"` is ARIA, `target="_blank"` is an anchor, `platform="xbox"` is a gaming platform, and `kind` means five different things in five modules. Nearly every hit was false, and a guard that cries wolf is worse than none.
>
> ---
>
> # 2. Which routes have no door?
>
> The inverse question. The guards ask whether every call reaches a route; this asks whether every route is reachable from a door a user can open — the quieter failure by far. A call to a missing route 404s and gets reported. **A route nobody calls produces nothing at all.**
>
> ## 252 of QRME's 409 routes are in that position
>
> Spot-checked, not assumed: the console reads `/profiles/{id}/friends` and renders the list, while `DELETE /profiles/{id}/friends/{fid}` is called by nothing. **You can gain a friend and never remove one.** `/displays`, `/comments`, `/agent/lights` and 250 others are in the same position.
>
> Recorded in `tests/doorless_routes.txt` as a ratchet: it **cannot grow** (a new doorless route fails), and it **must shrink deliberately** (building a door also fails, asking for the line to be struck).
>
> ## A correction, and the test that forced it
>
> The first version of this audit reported **zero** and passed. That was wrong in the most dangerous way — vacuously. `app.routes` is not the flat list it appears to be: FastAPI wraps each `include_router` in an `_IncludedRouter` carrying no `path` or `methods` of its own, so walking the top level saw **8 routes out of 409**. `all_routes()` now recurses.
>
> Route *matching* was never affected — the wrapper implements `matches` and delegates — so the guards from #221 and #222 stand. Only enumeration was broken.
>
> `test_the_audit_is_actually_looking_at_something` caught it, by asserting the route table is not implausibly small. **It was written in the same round it went on to falsify**, which is the argument for writing them.
>
> ## Not started: building the doors
>
> 426 route+method pairs across the three products is many rounds of work, and which families come first is a product decision rather than a mechanical one.
>
> ## Notes
>
> - Local suite (round 104): **1284 passed**. Round 105's is running.
> - `tests/clientpaths.py` stays byte-identical with jim-mini's and pdi's copies.
> - Tests and docs only — no runtime behaviour changes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #222 — Check the verb, not just the address

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/222>

> The route guard added in #221 accepted a **partial** router match — path right, method ignored. That passes a client sending `POST` where only `GET` is mounted, which answers **405**; from the user's side that is the same dead button as the 404 the guard exists to prevent. It now requires a full match.
>
> ## Reading the verb means reading four dialects
>
> None of it is guessable, so `CallForm` records where each language keeps it:
>
> | Surface | How the verb is written |
> |---|---|
> | console (TS) | labelled — `{ method: "POST" }` |
> | iOS (Swift) | labelled — `method: "PUT"` |
> | Android (Kotlin) | positional, right after the path |
> | Windows (C#) | the helper's own name — `Post(...)`, or `HttpMethod.Get` |
>
> ## Scoping to the enclosing call corrected the boundary both ways
>
> My first attempt scanned forward from a path literal and reported three "mismatches" that were all artefacts — a neighbouring call's `method:` leaked in whenever that neighbour wrote its path in double quotes. Parsing the call with balanced parens removed the guesswork and exposed two real facts:
>
> - **Double-quoted paths were skipped entirely.** In #221 I wrote a comment justifying that as safe. It happened to be true, but I had asserted it rather than checked it, and it left roughly a third of the console's call sites outside a guard that claimed to cover the console. **42 paths became 74 verb-and-path pairs.**
> - **`"/app"` stopped counting as a request.** It appears in `defaultBase()`, asking whether `window.location.pathname` starts with it — a question about where the page is served, not a call. Only something that knows what encloses a literal can tell those apart.
>
> ## Coverage
>
> | Surface | pairs checked | refused |
> |---|---|---|
> | console | 74 | 0 |
> | iOS | 89 | 0 |
> | Android | 87 | 0 |
> | Windows | 90 | 0 |
>
> **No field bug came out of this** — all 340 pairs are accepted. Saying so plainly: the value here is the guard, not a catch.
>
> ## Verified by injection, not assertion
>
> - console `POST` → `PUT` on `/interactors` → `PUT /interactors … accepted here: POST`
> - iOS call stripped of its `method:` label so it fell back to GET → `[ios] GET /profiles … accepted here: POST`
>
> Both restored to a zero diff afterward.
>
> ## A new class of guard
>
> Each language's verb reader gets its own liveness test. They are separate code and they fail quietly: if one stops matching, every call from that surface silently becomes a GET — and since most routes *do* serve a GET, the suite would stay green while checking almost nothing. A surface reaching dozens of routes and reporting a single verb is now an assertion failure.
>
> ## Notes
>
> - `tests/clientpaths.py` stays byte-identical with jim-mini's and pdi's copies (`acf4c50…`).
> - `native/README.md` updated where it described the check as path-only, keeping both stated limits: routing-level matching cannot see refusals that happen *after* dispatch, and a path assembled at runtime is invisible to any static scan.
> - Tests and docs only — no runtime behaviour changes, so nothing here needs a version cut of its own.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #221 — Guard every client path against the route table, in four languages

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/221>

> 0.17.0 fixed a 404 under every like, comment and share on the community wall, and added a test so it could not come back. **The test had a hole, and six client surfaces had no test at all.**
>
> ## The hole in the guard
>
> `test_console_routes_exist.py` cut each path at its first interpolation whenever a query followed. That is correct for `?tag=${tag}` — the path ends before the `?` anyway — and wrong for this:
>
> ```ts
> `/profiles/${profileId}/media?filename=${encodeURIComponent(file.name)}`
> ```
>
> which was being checked as bare **`/profiles`**.
>
> A prefix that *resolves* is worse than one that does not. The check passes, reports success, and the tail it exists to verify is never looked at. Two of QRME's console paths were being skipped this way — the adult feed and the **media upload added in 0.16.0**.
>
> The fix is an ordering change: fill interpolations in *before* cutting the query, with the optional-parameter idiom (`${adult ? "?adult=true" : ""}`) recognised as the one interpolation that really *is* a query, marked by a quoted `?` inside its braces.
>
> ## The gap: three shells, no guard
>
> `native.yml` proves the shells compile. A path is a string in all three languages, so this compiles perfectly, ships, and 404s in the field:
>
> ```swift
> "/post/\(id)/like"      // the Wall bug, verbatim
> ```
>
> Around **220 path literals** across iOS, Android and Windows had never once been compared with the route table.
>
> | Surface | Paths | Interpolation | Previously checked |
> |---|---|---|---|
> | console | 42 | `${x}` | partially — 2 were being skipped |
> | iOS | 74 | `\(x)` | ❌ |
> | Android | 72 | `$x` / `${x}` | ❌ |
> | Windows | 74 | `{x}` | ❌ |
>
> The singular of every `_KIND_BY_PATH` value is now banned in the native sources too, so a fix made on the web cannot be quietly undone on a phone. `test_the_shells_and_the_console_agree_on_the_wall` states that directly: 0.17.0's fix was five lines in one TypeScript file, and nothing stopped the same five paths being written the old way in Swift, Kotlin or C#.
>
> ## Two tests guard the guard
>
> **`test_each_shell_is_actually_being_scanned`** — fails if a language's pattern stops matching. A scan that silently finds nothing reads exactly like a scan that finds nothing wrong, and it would turn this whole file into a test that always passes.
>
> **`test_an_interpolated_query_does_not_truncate_the_path`** — pins the truncation bug against the two live paths that were being skipped, asserting they now reach the guard *and* resolve.
>
> ## Shared extraction
>
> `tests/clientpaths.py` holds the language table and the normaliser, used by both guards and **byte-identical in all three repos** (md5 `38e1a310…`). The repo root is located by walking up to `pyproject.toml` rather than counted in `.parent`s — this file sits at `tests/` here and `{pkg}/tests/` in the siblings, and that was the only thing that would otherwise differ.
>
> ## Result
>
> **No new field bug came out of this.** Every path all four surfaces build resolves. I'd rather say that plainly than dress up a clean audit — the value here is the guard, not a catch.
>
> Each check was verified by injecting the bug it claims to catch:
>
> | Injected | Into | Result |
> |---|---|---|
> | `"/post/\(postId)/like"` | iOS | both Wall guards fired, naming the platform |
> | `"/modles"` | Windows | `[windows] /modles (native/windows/ApiClient.cs, from '/modles')` |
>
> Every tree was restored to zero diff afterward.
>
> ## Also
>
> `native/README.md` gains a **"Do the paths resolve?"** section beside its existing "Do they compile?" claim, and states both limits rather than overselling: routing-level matching cannot see a refusal that happens *after* dispatch — which is exactly why the singular segments are banned by name — and a path assembled from pieces at runtime is invisible to any static scan.
>
> ## Tests
>
> Local suite running at time of push; the four route-guard files pass (`9 passed`) and CI runs the identical `test` job. Test count goes 1269 → 1274.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #220 — Cut 0.18.0

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/220>

> 0.18.0 across all five version strings — `pyproject.toml`, `qrme/api.py`'s `FastAPI(version=)`, `app/package.json`, and the two *root* entries of `app/package-lock.json`. Plus the changelog heading over the accumulated `[Unreleased]` content, the README history row and current-release line, and a fresh `RELEASE_NOTES.md`.
>
> The lockfile split is root-only by construction, and it earned that this time: `node_modules/react-refresh` is genuinely at version `0.17.0`, and it was correctly left alone.
>
> ## What it carries
>
> **Native parity, completed.** Provenance lookup ("Who wrote this?") and the advisor/collaborator/operator role picker reach iOS, Android and Windows. Every feature with a door in the web console now has one in the native shells — a thing two earlier rounds each named in their scope and neither finished.
>
> **The drawings caught up.** Voice cloning, the recoverable watermark and the role had all shipped with no screen, no lesson and no way for the in-app helper to point at them, for two whole versions. Screens **147 Your Own Voice**, **148 Who Wrote This?** and **149 How Should They Work?** join the gallery, each with a lesson in its proper chapter and a phrase the helper answers to.
>
> **Fixed** — `SmallAction` on Android took no `enabled` parameter, so a busy or empty action looked live and merely ignored taps.
>
> ## Verification
>
> - 1269 tests passed on this content before the cut; console builds clean (`✓ built in 1.34s`).
> - All five version strings verified per repo, and no stale root `0.17.0` anywhere.
> - Scripture confirmed still the README's closing section and deliberately not itemized as a changelog item.
>
> Cut together with [jim#167](https://github.com/davidsbianchi1984/jim-mini/pull/167) and [pdi#127](https://github.com/davidsbianchi1984/pdi/pull/127) so the suite carries one version.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #219 — Draw, teach and make findable what 0.16.0 and 0.17.0 shipped

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/219>

> Voice cloning, the recoverable watermark and the role picker each had code, a console door and (as of #218) a native door — and **no screen, no lesson, and no way for the in-app helper to point at them.** The convention here has been screen SVG + gallery row + lesson + help destination per feature; it had quietly stopped being followed for two whole versions.
>
> | # | Screen | Lesson chapter | Ask the helper |
> |---|---|---|---|
> | 147 | Your Own Voice | You are in control | "clone my voice", "sound like me" |
> | 148 | Who Wrote This? | You are in control | "who wrote this", "was this ai" |
> | 149 | How Should They Work? | Working | "just do it", "give me advice" |
>
> The help destinations are read by both the assistant *and* the dock's routing table from the same place, so one addition covers both surfaces.
>
> ## Two of this repo's own guards earned their keep
>
> **The screen builder refuses text that would overflow its box.** It caught eight strings before anything rendered — `'This is my own voice' needs 151px, has 119px` and so on. I shortened each rather than widening a card, because the guard is right about the layout.
>
> **The tutorial test requires lessons stay grouped by chapter in `CHAPTERS` order.** Appending the three at the end broke it (`At index 8 diff: 'Out in the world' != 'You are in control'`), so each lesson went into its chapter's own block instead. That constraint exists so the walkthrough never introduces a thing before the thing it depends on.
>
> I'd have shipped both defects without them.
>
> ## Verification
>
> - `test_docs_gallery`, `test_dock`, `test_tutorial`, `test_help`, `test_readme_scripture`: **71 passed.** The gallery test is a three-way check — every SVG referenced exists, every SVG is referenced, and the numeric sequence is unbroken.
> - Screen builder is deterministic: re-running before my change regenerated all 292 existing screens byte-identical, so the diff here is only the new work.
> - Helper routing verified live: `'clone my voice' -> [147]`, `'who wrote this' -> [148]`, `'just do it' -> [149]`.
> - Full suite running; CI is the gate.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #218 — The last two console-only features reach the native shells

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/218>

> Voice enrollment went native in 0.17.0; the other two features that had gained console doors did not. So iOS, Android and Windows could neither ask *who wrote this* nor choose how the profile should work a turn.
>
> | Feature | Route | Where it landed |
> |---|---|---|
> | **Who wrote this?** | `POST /watermarks/recover` | iOS `SettingsView`, Android Settings, Windows `SettingsPage` |
> | **Role picker** (spec clauses 2/12) | `role` on `POST /profiles/{id}/chat` | the chat composer on all three |
>
> Each client also gains the `RoleContext` / `WatermarkRecovery` wire models, and `chat()` takes an optional `role`.
>
> ## Two deliberate details
>
> **Recovery never answers with a bare yes.** The card shows matched passages out of stored, plus the similarity, and below the 0.25 threshold it names **nobody** — it reports the closest overlap and the threshold instead. Ordinary phrases travel between unrelated texts, and a coincidence must not read as an accusation. The failure branch shows the backend's own `reason` rather than a flat "no".
>
> **The role picker defaults to inference, and says so.** "Read my prompt" is index 0 / the empty value, which is what the backend does on its own. The reply then reports which role applied **and whether it was declared or inferred**, so an inference is never presented back as an instruction.
>
> ## Parity, finally
>
> With this, every feature with a door in the web console has one in the native shells:
>
> | | Voice | Watermark recovery | Role picker |
> |---|---|---|---|
> | iOS / Android / Windows | ✅ | ✅ | ✅ |
>
> That parity was named in the scope of two earlier native rounds and finished by neither. I verified it by grep this time rather than asserting it.
>
> ## Verification
>
> - Console builds clean (`✓ built in 1.55s`) — untouched here, checked for regressions.
> - No Swift/Kotlin/.NET toolchain in this environment, so **the iOS / Android / Windows jobs on this PR are the real check.** XAML well-formedness verified locally.
> - Caught by review before pushing: `WatermarkRecovery` needed an explicit import in Kotlin (a `mutableStateOf<T?>` type reference, unlike `WatermarkDesign` which is only ever inferred); `System.Linq` and `Microsoft.UI.Xaml.Media` were missing in the two Windows code-behinds; and one of my own edits silently no-oped against a non-existent anchor, which I only found by grepping for the result instead of trusting the script's "ok".
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #217 — Cut 0.17.0, and fix a 404 under every like, comment and share

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/217>

> ## The bug
>
> **Every like, comment and share on the community wall returned 404, and always had.**
>
> The audience routes dispatch on a leading `{kind}` and map the *plural* path segment to a singular kind (`posts` → `post`). `app/src/api.ts` was asking for the singular, so `/post/{id}/like`, `/post/{id}/comments` and `/post/{id}/share` reached the generic route and were then refused by the kind lookup. Liking a post, unliking it, reading its comments, writing one, sharing it — none of it worked in any release that shipped the buttons.
>
> Proven, not inferred:
>
> ```
> POST /post/pst_…/like       -> 404      POST /posts/pst_…/like       -> 201
> GET  /post/pst_…/comments   -> 404      GET  /posts/pst_…/comments   -> 200
> POST /post/pst_…/share      -> 404      POST /posts/pst_…/share      -> 201
> ```
>
> ## Why nothing caught it, and what now does
>
> Neither half was wrong on its own — the backend tests exercised the plural and passed, and the console compiled because a template literal is only a string. So the fix ships with `tests/test_console_routes_exist.py`, which checks the two halves *against each other*:
>
> - every path `api.ts` builds must resolve against the app's real route table;
> - no singular form of any mapped segment may appear in `api.ts` (covers all nine `{kind}` routes — like, comments, share, subscribe, subscribers, audience, gift, gifts — not just the three that were broken);
> - the singular's 404 and the plural's 200 are both observed against a live request, so the rule is not merely a spelling convention.
>
> One limit is recorded in the test rather than left to be rediscovered: **a route-table comparison would not have caught this.** `/post/x/like` matches `/{kind}/{target_id}/like` perfectly well at the routing layer, because the refusal happens after dispatch. I verified the new test fails on the old code before keeping it.
>
> ## The cut
>
> 0.17.0 across all five version strings — `pyproject.toml`, `qrme/api.py`'s `FastAPI(version=)`, `app/package.json`, and the two *root* entries of `app/package-lock.json` (root only; no dependency at the same version was touched). Plus the changelog heading over the accumulated `[Unreleased]` content, the README history row and current-release line, and a fresh `RELEASE_NOTES.md`.
>
> It carries: voice enrollment on the three native shells, the three features that gained console doors, the recoverable watermark, the Windows nav-label fix, and the Wall fix above.
>
> Also restores `The choice sticks.` to the 0.14.3 entry — a sentence describing real behaviour (the minimize state persists) that was removed while clearing the Matthew 7 paragraph out of the release notes, though it was never part of that passage.
>
> ## Verification
>
> - `test_readme_scripture`, `test_console_routes_exist`: 5 passed. Full suite ran clean before the changelog edit; CI is the gate.
> - Console builds clean.
> - Scripture confirmed still the README's closing section, and deliberately not itemized as a changelog item.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #216 — Voice enrollment reaches the device that has the microphone

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/216>

> The Voice screen shipped in the web console — which is the one surface where the owner cannot actually record anything, so it asks them to *type* how many seconds of speech they gathered. iOS, Android and Windows each gain a **Voice** screen walking the same FIG. 800 order (permission → collection → the characteristics → the print), but recording the sample and measuring it.
>
> ## What changed
>
> | Shell | Screen | Recorder |
> |---|---|---|
> | iOS | `native/ios/Sources/Views/VoiceView.swift`, reached from a new **Voice** segment in Manage | `AVAudioRecorder` + `NSMicrophoneUsageDescription` |
> | Android | `native/android/…/ui/VoiceScreen.kt`, new **Voice** tab in `ManageScreen` | `MediaRecorder` + `RECORD_AUDIO` |
> | Windows | `native/windows/Views/VoicePage.xaml`, new sidebar item | `MediaCapture` + system privacy setting |
>
> Each shell also gains the six voiceprint bindings in its API client (`voiceprint`, `grantVoiceConsent`, `addVoiceSample`, `buildVoiceprint`, `speakInVoice`, `revokeVoiceprint`) and the matching wire models.
>
> ## The privacy property is structural, not a promise
>
> The recording is written to the app's own container — `temporaryDirectory` on iOS, `cacheDir` on Android, `LocalApplicationData\QrmeStudio\voice` on Windows — and only the *measurement* crosses the wire, with `reference` naming the file. That is what the backend's `reference` field is for. No audio is uploaded, so no voice corpus can accumulate server-side; it is a consequence of where the bytes are written rather than a policy about them.
>
> ## Turn counting says which method it used
>
> iOS and Android read the platform's level meter (`averagePower(forChannel:)`, `maxAmplitude`) and count rising edges out of silence, so a turn is a stretch of speech. Windows does not meter its input, so it reports **one turn per recording** rather than deriving a count from the duration. A coarse number the app can stand behind beats a plausible one it cannot — the same reason `analyze()` reports counts instead of a quality score.
>
> ## Fixed
>
> The Windows navigation pane displayed the literal strings `tab.desk` and `tab.signatures`. Chrome localization falls back to the key when a key is missing, and those two were never added when the screens were. All three (with `tab.voice`) are now in `L10n.cs` in every supported language.
>
> ## Verification
>
> - Web console builds clean (`✓ built in 1.66s`).
> - `test_readme_scripture`, `test_docs_gallery`, `test_voiceprint`, `test_watermark_recovery`: 24 passed locally; full suite plus CI is the gate.
> - No Swift/Kotlin/.NET toolchain exists in the authoring environment, so these three files were reviewed rather than built locally — but `native.yml` compiles all three on their own runners, so the **iOS / Android / Windows jobs on this PR are the real check**.
> - Three problems were caught by review before pushing: `ApplicationData.Current` throws in an unpackaged WinUI app (switched to the same `LocalApplicationData` root `AppState` already uses), `MediaRecorder(null)` does not satisfy the API-31 constructor's non-null `Context`, and a `.map` chained off an optional inside an optional-chained Swift expression was replaced with explicit steps.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #215 — Three features come out from behind the API

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/215>

> An audit round for what had been skipped, and it found the failure this project keeps relearning: **a door nobody can open reads in the field as the feature not existing.** Voice cloning, the recoverable watermark and the advisor/collaborator/operator role all shipped as routes with no way to reach them from the app.
>
> ## Voice tab
>
> Walks FIG. 800's order rather than offering one "clone me" button, because the permission is the first box in the drawing for a reason:
>
> 1. **Permission** — with the own-voice attestation stated as what it is, and Withdraw on the same card.
> 2. **Enrollment** — add samples by source, and the readiness numbers are shown (`3 samples · 45s`, "still wants 75s more"), so a thin enrollment *looks* thin instead of hiding behind a progress bar.
> 3. **The voice** — mint the print only when it is earned, then speak, with the basis and the spoken disclosure printed under the result.
>
> ## Role picker on the composer
>
> Advisor / collaborator / operator, with **"Let it read my prompt"** as the default — which is the honest default, since that is exactly what the backend does when no role is sent. The reply's note now reports which role applied and whether it was `declared` or `inferred`.
>
> ## "Who wrote this?" in Control
>
> Paste any text; it names the profile that produced it, from the text alone, and reports `N of M passages match`, the similarity, and whether the writing is verbatim or has been altered since. When nothing matches it says so with the reason, rather than shrugging.
>
> ## Notes
>
> - No backend changes. `ChatReply` gains `role_context` and the chat request gains `role` in the typed client; everything else is new screens and bindings.
> - Console and launcher builds green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #214 — The closing passage is not a release note

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/214>

> Founder's direction: the Matthew 7:24–25 passage **stays at the end of every README** — that standing rule is unchanged and still test-enforced — but it does not belong in the list of what an update contains. It's how the documentation closes, not a feature that shipped.
>
> ## What changed
>
> - Removed the 0.14.3 changelog paragraph that announced it.
> - Removed it from the 0.14.3 README release-history row.
>
> ## What did not change
>
> - The passage itself, byte-identical at the very end of every README.
> - `tests/test_readme_scripture.py`, which enforces that every `README*.md` closes with the root's block — still passing, so a newly added README still can't forget it.
>
> Docs-binding tests green: 13 passed. The same change is in jim-mini and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #213 — The watermark learns to survive being edited

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/213>

> Built from the field drawing: message *m* + sequence *S^N* + security key *K^D* → watermark *W* → embed → **Attack** → extract *W'* → reconstruct *m'*.
>
> ## The gap
>
> `POST /watermarks/verify` could only confirm that a piece of content matched a credential id **you already held**. One changed character made it fail, and it never said who wrote the text. The drawing asks for the other direction — recover the mark *from the content*, after the content has been attacked.
>
> ## What's new
>
> `POST /watermarks/recover` takes text with **no credential id** and answers *whose work is this?* — and keeps answering after the text has been rewritten.
>
> Every stamped text now also deposits an inverted index of **keyed five-word windows**: the normalized text cut into overlapping windows, each HMAC-SHA256'd with the deployment's watermark key (`QRME_WATERMARK_KEY`). Recovery hashes a candidate the same way and asks which stamp shares the most windows, scoring by overlap.
>
> The reply states its evidence instead of asserting a verdict:
>
> ```
> {"recovered": true, "profile_id": "prf_…", "verbatim": false,
>  "similarity": 0.62, "matched_windows": 31, "stored_windows": 44,
>  "examined_windows": 47, "state": "altered but traceable", …}
> ```
>
> It's arithmetic, not a learned detector, so the score can be checked by hand.
>
> ## Three deliberate restraints
>
> - **A coincidence is not an accusation.** Below a 0.25 similarity it names nobody — ordinary phrases travel between unrelated texts. A test feeds it a shared sentence about afternoon light and confirms it refuses.
> - **The key is what makes it a watermark rather than a fingerprint.** Without it nobody can compute matching windows, so a credential can't be forged or transplanted onto text QRME never wrote. A test swaps `QRME_WATERMARK_KEY` and watches recovery go silent.
> - **A provenance store must not become a corpus.** The stored rows are keyed hashes, so the index can't be read back as the writing it came from. A test asserts none of the passage's own words appear in the table.
>
> ## Notes
>
> - New table `watermark_shingles` with an index on `shingle` — a real inverted-index lookup rather than a scan over every stamp, and a new table (not new columns) so existing databases pick it up through `CREATE TABLE IF NOT EXISTS` with no migration.
> - `QRME_WATERMARK_KEY` unset derives a stable key from the database path so a local install still recovers its own marks. The docstring says plainly that this is a working default, not a secret.
> - Route registered before the `/watermarks/{watermark_id}` catch-all; `tests/test_routing.py` passes.
>
> ## Tests
>
> `tests/test_watermark_recovery.py` (8): verbatim recovery at similarity 1.0; an edited passage still traceable and honestly marked as altered; unrelated text recovers nobody; a shared phrase refused below threshold; the key swap silencing recovery; two profiles told apart; the route answering with no id; and the index proven non-reversible.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #212 — Voice cloning, in the order FIG. 800 draws it

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/212>

> From the field drawing: FIG. 800 is a **permission gate first and a recorder second** — 802 asks for permission to collect and use call information, 804 initializes collection, 806/808 collect from an active call, 810 analyzes it to determine the characteristics of the communication, 812 records the voice for cloning. That ordering *is* the design, so `qrme/voiceprint.py` makes it load-bearing rather than decorative.
>
> ## The flow, box by box
>
> | Step | Endpoint | What it does |
> |---|---|---|
> | 802 | `PUT /profiles/{id}/voiceprint/consent` | The permission, before anything is collected. `own_voice` is an **attestation** — QRME refuses to learn a voice on somebody else's behalf. Consent is scoped to named sources (`call` / `voice_note` / `direct`). |
> | 806–808 | `POST /profiles/{id}/voiceprint/samples` | A gathered sample. **Metadata only** — seconds, turns, transcript size, and a `reference` naming where the audio itself lives — so a voice corpus never accumulates inside the profile database. 403 with the reason when consent doesn't cover that source. |
> | 810 | (returned by every collect, and `GET …/voiceprint`) | The characteristics as arithmetic anyone can check: samples, seconds, mean turn length, mean chars per turn, sources. No opaque score. |
> | 812 | `POST /profiles/{id}/voiceprint` | Mints the print — refused until the enrollment is real (≥3 samples, ≥120s), so a thin enrollment is *called* thin instead of labelled ready. |
> | — | `POST /profiles/{id}/voiceprint/speak` | Speaks in the enrolled voice, always with the watermark credential **and** a spoken disclosure. |
> | — | `DELETE /profiles/{id}/voiceprint` | Withdrawal: samples deleted, print retired, the withdrawal itself left on record. |
>
> ## The three rules it inherits from the rest of the codebase
>
> - **Your own voice.** QRME's premise is a profile built from your own likeness; a voiceprint is that promise in another medium. Enrollment is owner-only and requires the attestation. There is no path here for a stranger, a celebrity, or a recording of someone who never agreed.
> - **The mark is not optional.** Synthesized speech leaves stamped (`qrme/watermark.py`) and carrying "this voice is synthesized … not a recording of them speaking these words." A cloned voice that doesn't say it is one is the thing this codebase exists to refuse.
> - **Revocable, and it means it.** Withdrawing deletes the samples and retires the print; the tombstone stays, which is the opposite of pretending nothing happened.
>
> ## Tests
>
> `tests/test_voiceprint.py` (9): the gate bites before collection; a non-own-voice attestation is refused; consent is scoped per source; the analysis is counted not scored; a full enrollment mints a print; speech always carries mark + disclosure; no print means no speech; withdrawal deletes samples and silences the print; and the constants are asserted directly.
>
> Full suite green: **1255 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #211 — Cut 0.16.0, and cite the publication number

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/211>

> The 0.16.0 release cut, carrying everything merged since 0.15.0.
>
> ## Publication number
>
> Application 19/056,418 (526.P002) **published as US 2025/0265659 A1 on August 21, 2025** — from the USPTO PDF in the field. A published application is citable public record, so the number now rides beside the application in the README's patent line.
>
> ## Version cut — 0.15.0 → 0.16.0
>
> Five version strings (`pyproject.toml`, `qrme/api.py`, `app/package.json`, both root entries of `app/package-lock.json`), the `[0.16.0]` heading over the changelog content the feature PRs wrote, the README release line + history row, and `RELEASE_NOTES.md`.
>
> **In this release:** wall uploads (photos, videos, files — kind decided by the bytes, caps published, never the AI mark) and pasted video links rendering as players on the nothing-loads-until-play facade; **Sign in with Google / Apple**, live only where configured; **DeepSeek** and **your own algorithm** on the model menu, the latter dark until its URL is set; the **advisor / collaborator / operator** role context (spec clauses 2 and 12) declared on a turn or read from the prompt itself; startup portrait self-repair; and the phone-layout fixes.
>
> ## Verification
>
> Full suite green (1246 at the last full run); version/changelog/README binding tests green (13); console and launcher builds green.
>
> ## Tag and release
>
> The tag is yours to push — `app-v0.16.0`. `RELEASE_NOTES.md` is the ready-to-paste body.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #210 — Two more doors on the model menu, and the role rides the turn

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/210>

> The provider round plus the P002 clause audit, QRME side.
>
> ## What's here
>
> **DeepSeek + your own algorithm** — from the field ask: "give the users the option to plug in my algorithm … or DeepSeek or any others on the market … assign their logos to make the clickable attachments to where they can pick and choose."
> - **DeepSeek** joins the provider registry as a first-class entry (`QRME_DEEPSEEK_API_KEY` or `DEEPSEEK_API_KEY`; model override via `QRME_DEEPSEEK_MODEL`, default `deepseek-chat`).
> - **Your own algorithm** — a `custom` provider pointing at any endpoint speaking the OpenAI dialect: `QRME_CUSTOM_LLM_URL` + `QRME_CUSTOM_LLM_KEY`, optional `QRME_CUSTOM_LLM_MODEL`/`QRME_CUSTOM_LLM_LABEL`. Built as configuration so the day the founder's algorithm exists, no release is needed.
> - The custom tile **stays dark until its URL is set** (`needs_base` gate) — a key alone points at nothing. Console logo tiles for both.
>
> **Advisor, collaborator, operator (spec clauses 2/12)** — the clause-by-clause audit of the pasted P002 clauses found every embodiment already in code (simulation, environmental adaptation, watermarks, anonymity, memory, engagement, moderation, adult-consent, GPT providers) except role-specific contexts. Now real: a chat turn can declare `role: "advisor" | "collaborator" | "operator"`, or leave it unset and the profile reads the prompt itself (`qrme/roles.py` — transparent keyword inference, silent on a tie, never a hidden model call). The reply's `role_context` names the role and how it arrived (`declared`/`inferred`); frames shape *how* the profile works this turn, never *who* it is — persona, relationship, memory and moderation apply unchanged.
>
> ## Tests
>
> - `tests/test_models.py`: both new provider doors on `GET /models`; custom unconfigured until its URL lands.
> - `tests/test_roles.py` (6): declared role echoes, autonomous inference, plain turns stay plain, unknown role 422, transparent keyword unit test, declared-beats-inferred.
> - Full suite green locally (1240 at last full run + the 6 new); console `npm run build` green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #209 — Uploads on the wall — pictures, video, files — pasted links play, and two new front doors

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/209>

> The picks from the open list (items 1 & 4) plus the composer requests, all of them.
>
> **Pictures, video, a note, files on every post.** The note is the post text; uploads carry the rest: kind decided from the file's bytes — images (JPEG/PNG/GIF/WebP), video (MP4/WebM), and **Files**: PDF by magic, the zip-family office formats (PK magic — the extension survives only from a whitelist, anything fancier becomes `.zip`), and plain text (`txt/csv/md`; a text file claiming `.html` serves as `.txt`, where markup is just characters — nothing a browser executes is ever served). Caps published at `GET /media/limits` (8 MB image / 60 MB video / 20 MB file); the uploader's filename rides as a display name only. Never the AI mark: authentic media stays authentic. Ownership checked before the post row is written.
>
> **A link dropped in the text renders the video, not just the text.** With no explicit video field, the first whitelisted URL in the body becomes the post's video — same facade contract, nothing loads from the platform until the viewer presses play. Unknown platforms' links stay text, now clickable.
>
> **Sign in with Google / Apple** (`qrme/oauth.py`): configuration decides whether the buttons are live; grey doors carry their exact setup note; the provider's word verifies the inbox; the parked session is claimable exactly once; passwordless accounts fail closed on typed passwords. Console buttons + browser flow + poll-claim.
>
> **Item 4 (Windows Hello signing)** needed no code: the WebView2 ceremony from an earlier round already talks to Windows Hello through Edge — awaiting a field test on a real machine.
>
> Tests: `test_wall_media.py` (5 — including the `.exe`→`.zip` and `<script>`→`.txt` refusals and the pasted-link auto-render), `test_oauth_signin.py` (3), wall suite green. Console upload flow verified live in a browser.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #208 — Field round: portraits self-heal, phone layout, and the Wall reaches the console

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/208>

> Field round, from live testing reports plus the transcript/photo re-audit. Everything below reproduced and verified against a running backend (screenshots in session).
>
> **Starter portraits missing over their names.** A deployment seeded before the portraits shipped has 34 starters with blank `avatar` columns, and the repair lived behind the Discover seed button nobody knows is a repair:
> - `seed.repair()` — blank-only portrait repair, run automatically at API startup. Heals starters **and the founder's two profiles**, which `_seed_one_founder`'s early return used to skip (0/36 faces → restart → 36/36, the photograph restored from the photo tree, never stamped with the AI mark). Never creates a profile.
>
> **"It wouldn't let me type in a topic for the room."** Reproduced at phone size: twelve tab labels forced the app to ~576px wide, so every form overflowed sideways and the Kind dropdown crowded the Topic box; the agent-lights circle and help fab sat on top of the bottom tab bar. The tab bar now scrolls, forms stack one column, corner widgets ride above the tabs, and Rooms-create without a profile names the requirement.
>
> **The Wall reaches the console.** The community layer (For You feed with stated reasons, posts, likes, comments, shares, shared-video links) has lived in the backend since the community round — the desktop console never got the door, which read in the field as the features not existing. New Wall tab: composer with optional video link (platform whitelist shown up front), video cards honoring the facade contract (nothing loads from the other platform until the viewer presses play), like/comment/share, and a Your-wall section so a solo owner doesn't post into apparent silence. Verified live with a YouTube link.
>
> Also: the `[0.14.5]` CHANGELOG link points at the cut commit instead of a tag that never shipped.
>
> Tests: startup-repair pair in `test_seed_backfill.py`; full suite 1230 green; console build green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #207 — Cut 0.15.0 — the temperament dials

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/207>

> Release cut for **0.15.0**, in train with jim-mini and pdi. QRME's content this round is the temperament dial group (mood, outlook, maturity, agreeableness, confidence, curiosity) merged in #206.
>
> - CHANGELOG heading over the existing [Unreleased] story, RELEASE_NOTES.md, README current-release line and table row, five version strings.
> - Tag `app-v0.15.0` on the squash commit; release body stays empty for sync-release-notes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #206 — The temperament dials — the field's list, verbatim

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/206>

> The transcript-mining round, QRME half. The vision video promises control over "mood, outlook, maturity, agreeableness, confidence, curiosity" — steering now has that list **verbatim**, as a fourth dial group:
>
> - **`temperament`** joins system / behavior / intimacy in `qrme/steering.py`: six dials, 0–100, default 50 = silence, each with honest low/high poles ("subdued and quiet-toned" ↔ "bright and upbeat"; "tentative, hedges" ↔ "self-assured, decisive"; …).
> - The render layer is generic, so the group flows into `GET /steering` catalogs, the persona-prompt directive, and any surface that reads the dial spec — no other code changed.
> - Test pins the group's membership and its prompt rendering (near-default dials stay silent).
>
> On the video's remaining "characteristics" list: language (the language setting), age/maturity (the aging lifecycle + the new maturity dial), and culture/background live in the freeform persona by design — the deliberate home for identity a table shouldn't flatten.
>
> Full steering suite green (7); console build green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #205 — Cut 0.14.5 — cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/205>

> Release cut for **0.14.5**, in train with jim-mini and pdi. No functional change in QRME this round — the content is JIM's (the fall path, the native crash watch, the docs web).
>
> - CHANGELOG rider + heading, RELEASE_NOTES.md, README current-release line and table row, five version strings.
> - Tag `app-v0.14.5` on the squash commit; release body stays empty for sync-release-notes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #204 — Cut 0.14.4 — the console names a version mismatch

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/204>

> Release cut for **0.14.4**, in train with jim-mini and pdi at the same version.
>
> - CHANGELOG: 0.14.4 heading over the Unreleased content (version-mismatch banner; discovery-card faces with AI/real-photo badges; plain room labels; Blend explained; Erase all; the settings that say which secret is which; the send button clearing the fab), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.4
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, qrme/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.4` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #203 — Field feedback: faces on the cards, plain labels, erase all

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/203>

> Live-testing feedback, applied:
>
> - **Discovery cards get faces, with provenance**: `/marketplace` now returns `avatar` + `avatar_kind` per card (via `avatars.render()`, so anonymous profiles keep their silhouette and no hidden face can leak). The console draws the portrait — or initials — with an **AI** badge on generated portraits and **✓ real photo** only on an authentic photograph under `/photos`. New test: `tests/test_marketplace_cards.py`.
> - **Friends**: the "the founder stands first, on every list" subtitle is removed (the pinning itself is untouched).
> - **Rooms**: kind labels read plainly — **Text**, **Voice chat only**, **Video**, **AR**, **VR** (video was already there; nothing missing).
> - **Blend explains itself**: a new lead card says what blending *is* — it creates a brand-new openly-hybrid profile in the shares you choose; it is **not** following or friending, and the sources are untouched.
> - **Memory Vault**: **Erase all** beside the per-conversation erase, with one confirmation naming the count.
>
> (The "won't let me add anybody" / "interactor and profile" reports trace to the stale-backend issue the version guard now catches — the current console already shows real names and working add/erase.)
>
> `npm run build` green; full binding subset green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #202 — The console names a version mismatch

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/202>

> Field report from live testing of JIM-mini: a fresh console over a stale backend answers **"Not Found"** on every newer screen while looking otherwise alive. The Electron shell already refuses to adopt a version-mismatched backend on its own port — but a **stored base address** (e.g. the LAN address saved for the phone bridge, which deliberately wins over the desktop URL) can still steer the console to an old process holding that address.
>
> The console now performs the version handshake itself, in all three products (sibling PRs in jim-mini and pdi):
>
> - `vite.config.ts` injects `__APP_VERSION__` from package.json → `CONSOLE_VERSION` in api.ts.
> - **`VersionGuard.tsx`** fetches `/health` on launch and compares versions. On mismatch: a fixed red banner on every screen — *"Two versions of QRME are answering. This app is v0.14.3, but the backend at &lt;base&gt; is v0.8.0…"* — with a one-click **"Use this app's own backend"** (clears the stored base and reloads) when the desktop shell's own backend is available, or plain instructions to end the leftover backend process otherwise. Dismissible; wraps onboarding too, since a mismatched backend at sign-up is the same trap one screen earlier.
> - A backend so old it predates the `/health` version field reads as "(older than 0.5)" instead of passing silently.
>
> `npm run build` (tsc + vite) green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #201 — Cut 0.14.3 — the lights are always on

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/201>

> Release cut for **0.14.3**, in train with jim-mini and pdi at the same version.
>
> - CHANGELOG: 0.14.3 heading over the Unreleased content (the watch-sized minimizable lights window in the studio; the scripture closing every README, test-enforced), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.3
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, qrme/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.3` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #200 — The lights are always on + every README ends on the rock

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/200>

> Two requests in one branch:
>
> **1. The watch-sized lights window — on screen at all times, minimizable.**
> - **`app/src/WatchLights.tsx`** — a round, 176px watch-face-sized window pinned bottom-left (Help owns bottom-right), mounted in the App shell outside the tab switch so every screen has it. It shows the wrist's exact payload — 🟢 working, 🟡 needs a hand, 🔴 stopped, plus the profile chip and the approvals line — polling `GET /profiles/{id}/watch` every 15s with the owner token. The bezel ring takes the worst light's colour.
> - **Minimize** — the `–` control folds it to a 46px dot in the worst light's colour; clicking the dot restores it. The choice persists (`localStorage`), and a fetch blip keeps the last face instead of blanking.
> - README's "Where you actually see it" table gains the studio-widget row.
>
> **2. The scripture closes every README, from here on.**
> - The Matthew 7:24–25 passage (with the ark prose) that closes the root README now closes **every** README in the repo — `app/`, `launcher/`, `docker/`, `assets/design/`, and the four `native/` READMEs — byte-identical, at the very end.
> - `tests/test_readme_scripture.py` enforces the standing rule: every tracked README must end with the root README's passage block, so the next README added cannot forget it. Sibling PRs (jim-mini#145, pdi#117) apply the same rule.
>
> CHANGELOG entries for both. `npm run build` green; binding tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #199 — Cut 0.14.2 — the vault posture survives suite mode

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/199>

> Release cut for **0.14.2**, in train with jim-mini and pdi at the same version.
>
> - CHANGELOG: 0.14.2 heading over the Unreleased content (gateway wires QRME's PDI tandem; `POST /suite/operations`; launcher joints; tandem-contract docs; smoke repair), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.2
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, qrme/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.2` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #198 — The launcher shows the joints

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/198>

> The suite launcher's dashboard catches up with the gateway's new surface:
>
> - **Joint lights** — the two tandems the gateway wires in-process (care-team tandem, vault sealing), read from `/suite/health`'s `tandems`. Amber means that joint runs degraded (no care team / no sealing), not that a product is down.
> - **Build my ecosystem** — one press calls `POST /suite/ecosystem`: demo org seeded in QRME, JIM's care team linked to its first desk; shows the org, its desks, and the link state. Idempotent, so pressing again finds the same one.
> - **Operations** — the owner-scoped list from `POST /suite/operations`: your coordinations as the vault recorded them, with a refresh and an empty-state pointer to JIM's Care Team tab.
>
> Launcher README documents the new dashboard section; CHANGELOG entry added. `npm run build` (tsc + vite) green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #197 — Docs: suite mode enters the tandem contract

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/197>

> `docs/tandem.md` (kept byte-identical across qrme, jim-mini and pdi) gains a **"Suite mode — the gateway wires the tandems itself"** section under *qrme / jim-mini ✕ pdi*:
>
> - how the gateway wires both joints at startup (JIM's `QRMEClient` bridge; the `suite:qrme-vault` tenant injected as QRME's own `PDIClient`),
> - why the tenant token is a deployment credential and when the self-mint is refused (`PDI_ADMIN_TOKEN`),
> - what `GET /suite/health` `tandems` means (degraded, not down),
> - how `POST /suite/operations` re-draws PDI's per-tenant isolation **by owner** when every suite identity's seals share the one tenant.
>
> Plus a CHANGELOG entry. Sibling PRs carry the identical file to jim-mini and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #196 — The vault posture survives suite mode

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/196>

> In suite mode the mounted QRME ran with `app.state.pdi = None`, so coordinations quietly stopped sealing the moment the three products shared one origin — the vault posture was a casualty of the deployment shape.
>
> - **The gateway wires QRME's PDI tandem**: finds (or mints once, by name) a dedicated vault tenant `suite:qrme-vault` and injects QRME's own `PDIClient` over the in-process bridge. A deployment that already configured `QRME_PDI_URL` keeps its wiring; a PDI running with `PDI_ADMIN_TOKEN` refuses the mint and the operator configures the token explicitly, as they would standalone.
> - **`GET /suite/health` reports both tandems** (`jim_qrme`, `qrme_pdi`) — false means that joint runs degraded, not that it's down.
> - **`POST /suite/operations`** — the provenance view: the caller's coordinations as the vault recorded them, authenticated with their own QRME owner token and scoped by owner, because in suite mode every identity's seals share the one tenant. The vault token never leaves the process; another identity sees none of it; a forged token gets 403.
> - **Fixes `python -m suite.smoke`**, failing locally since the vault gate moved from deployment to plan: its user enrolled as a visitor, whose writes rightly stay out of the vault. The smoke now subscribes its user to a private plan before asserting the exchange sealed. (CI's qrme-only checkout skips the smoke, which is how it slipped.)
>
> Tests: `test_suite_mode_keeps_the_vault_posture` (sealing + provenance scoping + forged-token refusal), `test_the_vault_tenant_is_minted_once` (restart reuses the tenant), and the repaired smoke — 11/11 locally; suite tests skip in CI as before.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #195 — Cut 0.14.1 — the suite wires its own tandem

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/195>

> Release cut for **0.14.1**, in train with jim-mini and pdi at the same version.
>
> - CHANGELOG: 0.14.1 section under Unreleased (the suite gateway wires its own in-process tandem; `POST /suite/ecosystem` one-call bootstrap), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.1
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, qrme/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.1` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #194 — The suite wires its own tandem, and one call builds the ecosystem

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/194>

> Two seams the suite gateway was missing:
>
> - **The tandem wires itself.** In suite mode all three products share one process, but the mounted JIM had no QRME client — the care team couldn't work at all through the gateway. Now the gateway bridges JIM's `QRMEClient` to the mounted QRME app over an in-process ASGI transport: care team and specialist handoffs work with no second server and no `JIM_QRME_URL`. Skipped gracefully when either side is missing — a partial suite still comes up.
> - **`POST /suite/ecosystem`** — one call after `/suite/session`: hand back the tokens it returned (the gateway stays stateless, storing no credential) and get a working ecosystem — the demo org seeded in QRME (idempotent) and JIM's care team linked to its first desk.
>
> **Verification**: the new gateway test drives session → ecosystem → a manual coordination *through the gateway*, asserting the joint plan lands back in JIM — 8/8 suite tests green in the full-suite dev setup. CI's qrme-only checkout skips the suite tests by design (`pytestmark` skip), so the local run is the verification; the rest of CI is unaffected.
>
> Also fixed en route: this environment's sibling installs pointed at stale scratch snapshots; they now point at the live worktrees.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #193 — Cut 0.14.0 — the front page and the wrist

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/193>

> The 0.14.0 release-train cut for QRME: Home's "New in this release" card and the two new wrist faces (Proceeds, Coordination — counts only, drawn as watch faces 10-11) from #192. Cut mechanics per docs/releasing.md; siblings cut alongside.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #192 — The front page and the wrist learn the new doors

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/192>

> Two commits, one theme — the ecosystem round's features become findable and glanceable:
>
> - **Home** gains a "New in this release" card pointing at Blend, What If, Campaigns and Org. The doors existed; the front page never said so — and a door the front page doesn't name is a door testers never find.
> - **The wrist/pane** gains two faces with the same test as the four before them (a count-shaped answer to "is anything waiting on me", never the thing itself): **proceeds** — how your open campaigns are doing, never a donor's name — and **coordination** — whether the departments finished a joint plan, never the plan. Both route to their drawn screens (145, 146).
>
> Dock/agent-light suites: 43 passed; console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #191 — Cut 0.13.1 — demo, docs and hardening

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/191>

> The 0.13.1 release-train cut for QRME, bundling what landed after 0.13.0: the one-press demo org (#188), the docs round (#189), and the hardening caps (#190). Cut mechanics per docs/releasing.md; siblings cut alongside at the same number.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #190 — Hardening: caps and idempotency on the new surface

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/190>

> Three guards the ecosystem round's routes deserve, each with a test:
>
> - **An organization holds at most twelve departments.** A coordination is one model call per desk plus the composition pass — the department count is the request's cost multiplier, and the cap is what keeps one press from becoming a bill.
> - **The tokenless donate door gets a per-campaign daily count** (1000/day). Donations are deliberately tokenless — generosity isn't gated behind signup — which makes them the platform's one anonymous write; the count is far above any real campaign's daily traffic and low enough that the door can never become a ledger-spam hose.
> - **The demo-org button is idempotent.** Pressing it twice returns the same team instead of minting a second set of agents and grants.
>
> `tests/test_organizations.py` + `tests/test_campaigns.py`: 17 passed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #189 — Docs round: the tandem contract + invention disclosure catch up

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/189>

> Two documents catch up with the ecosystem round, in one docs PR (siblings in jim-mini and pdi):
>
> **docs/tandem.md** — byte-identical in all three repositories (md5 `cef566d1…`):
> - **qrme ✕ jim-mini** gains "The care team is an organization": the user's own owner token (QRME's org routes stay owner-only, JIM never sneaks around that), the *stacking* trigger (drift + adherence below 75%, not severity), summaries crossing but never raw readings, once a day, calm path only.
> - **qrme / jim-mini ✕ pdi** gains the `qrme/coordination/{id}` key space and the operations journal — a view, never a side door.
>
> **docs/invention-disclosure.md** — five new dated sections for counsel: weighted hybrid personas with a public composition; predictive simulation with evidence-earned confidence; environmental context beside biometric context; proceeds designations with token-lifecycle succession; departmental agent coordination over revocable scopes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #188 — Demo org: one press, a staffed organization

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/188>

> First PR of the next train: testers should meet the ecosystem working, not as an empty form.
>
> - `POST /organizations/demo` builds a complete team on the caller's own account: two enterprise agents (Workshop, Finance) each born with a small knowledge source and an all-scope **revocable grant**, desked into "The Demo Workshop", ready to coordinate — and ready to demonstrate revocation (revoke a grant, watch that desk's pulls stop).
> - Ownership stays honest: nothing touches the starter collection — those profiles belong to the platform, and a department may only be staffed by a profile its org's owner holds. The demo mints its agents *for* the caller and returns their owner tokens once, like profile creation does.
> - Console: the Org tab offers **"Found a demo org"** when no organization exists yet.
> - Test: the demo org is born ready — both desks scoped, a coordination runs immediately, and both agents actually pull their notes (`items_read >= 1`).
>
> Org suite: 9 passed; routing guard green; console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #187 — Cut 0.13.0 — the ecosystem round

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/187>

> The 0.13.0 release-train cut for QRME. This round: crowdfunding with proceeds routed where the user said (#185), the operational ecosystem (#185), and the console chrome following the profile's language (#186) — proved end-to-end against live JIM and PDI processes (care team coordinated from JIM, plan journaled in PDI, donation split exactly on the ledger).
>
> Cut mechanics per docs/releasing.md: CHANGELOG section + link definitions, RELEASE_NOTES for the `app-v0.13.0` tag, README release line + table row, five version strings (lockfile roots only — a dependency pinned at 0.12.0 stays untouched).
>
> JIM-mini and PDI cut alongside at the same number.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #186 — The console chrome follows the profile's language

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/186>

> The 0.5.x localization round covered the native reference apps (`native/ios/Sources/L10n.swift` and siblings); the Electron console — the app actually in testers' hands — still spoke English whatever the profile spoke.
>
> - `app/src/l10n.ts` carries the same chrome table as the native L10n files: all 12 nav labels plus sign-out, in the 10 backend-supported languages (en/es/fr/de/pt/it/ja/zh/hi/ar), falling back to English per key so a missing translation shows words, never a blank.
> - `App.tsx` reads `GET /profiles/{id}/language` the moment a profile is active and relabels the sidebar and sign-out; pick Español in a profile and the console frame follows.
> - Content localization was always server-side — this closes the console's frame around it, including the five tabs added this session (Blend, What If, Campaigns, Org).
>
> Console `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #185 — Both stones turned: crowdfunding with routed proceeds + the operational ecosystem

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/185>

> The round sweeps the two remaining unbuilt capabilities from the three founding documents — one from the QRME patent spec, one from the PDI proposal.
>
> ## 1 · Crowdfunding with proceeds routed where the user said (spec [0020], example two)
>
> > "supply crowdfunding for any loved ones, left behind or organizations for donations, wherever the proceeds might go up to the user"
>
> - `PUT /profiles/{id}/proceeds` designates loved ones and organizations with shares that must sum to exactly 100. Sunset changes nothing (the living owner keeps the pen); verified owner death (`/succeed`) revokes the old token and hands it to the chosen successor — "leave it in good hands," enforced by the token lifecycle.
> - `POST /profiles/{id}/campaigns` is **refused until a designation exists** and never opens on a rated profile — tips to a performer stay behind the age-gated gift.
> - `POST /campaigns/{id}/donate` is tokenless and capped like a gift; each donation splits at the door onto the ledger (computed in cents so shares re-add exactly); a designee with a platform account is paid on their own creator statement. The public card always shows the names — a donor gives to people, not to the platform.
> - Screen **145 · Where the Money Goes**, `proceeds` lesson, helper directions, **Campaigns** console tab.
>
> ## 2 · The operational ecosystem (PDI proposal)
>
> > "role-specific AI agents … collaborate across departments, pulling relevant data, offering smart suggestions, and coordinating efforts"
>
> - `POST /organizations` + `/departments` staff each department with one of your own profiles as its role agent — a stranger's profile is refused, and so is a rated one.
> - Department reads are scoped by the same **revocable grant** machinery as claim-25 tasks: revoke and the pulls stop instantly, the org stands (proved by test).
> - `POST /organizations/{id}/coordinate` takes one goal across every department: each agent contributes from its own scoped material in its own persona, the initiating agent composes the joint plan — watermarked synthetic, owner-only, never distributed — and with the PDI tandem configured the record is **sealed into the vault**.
> - Screen **146 · The Ecosystem**, `ecosystem` lesson, helper directions, **Org** console tab.
>
> ## Verification
>
> - `tests/test_campaigns.py` (11) + `tests/test_organizations.py` (5) + all binding suites (tutorial/dock/help/gallery/routing): **87 passed**.
> - Console `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #184 — Cut 0.12.0 — the specification, mined

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/184>

> The 0.12.0 release-train cut for QRME — this round's feature repo. The filed patent specification (App. 19/056,418, SYNTHETIC USER PROFILE MANAGEMENT) was read end to end and everything it describes that the apps did not yet do was built in, backend (#182) and console (#183):
>
> - **Hybrid profiles** — blended from several people, shares and borrowed aspects, honest about being a blend; Blend tab, screen 142.
> - **Real-time simulation** — the represented person's likely decision and workflow, confidence earned from evidence; What If tab, screen 143.
> - **Environmental adaptation** — replies that fit where the person actually is; 📍 toggle in Chat, screen 144.
>
> Cut mechanics per docs/releasing.md:
> - CHANGELOG 0.12.0 section + link definitions repointed
> - RELEASE_NOTES.md refreshed for the `app-v0.12.0` tag
> - README current-release line and release-table row
> - Version bumped in all five places (pyproject, `qrme/api.py`, package.json, both lockfile root entries)
>
> JIM-mini and PDI cut alongside at the same number (pdi#106 and the jim-mini cut PR), both "no functional change".
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #183 — The console shows the mined features: Blend, What If, and where you are

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/183>

> The console round for #182's three spec-mined capabilities. They existed only as API routes; now every layer that binds a feature to the product carries them — the same pipeline every feature goes through (screen → lesson → directions → gallery → console).
>
> ## Screens 142–144
> - **142 · Blend a Profile** — the hybrid's shares and borrowed aspects, the honesty rule, and the two refusals (rated never blends; strangers need a listing).
> - **143 · What Would They Do** — decision, workflow, confidence *earned* from evidence, marked as AI and private.
> - **144 · Where You Are** — location/conditions/time riding beside the claim-23 biometrics, woven in and never recited back.
>
> Drawn for both platforms (288 SVGs regenerated); the builder's width audit shaped every card title.
>
> ## Walkthrough & helper
> - New lessons `blend` ("Getting started") and `predict` ("Working"); the `talk` lesson now teaches telling the profile where you are and claims screen 144.
> - `help.DIRECTIONS` phrases for each — "both grandparents", "what would they do", "knows where i am" — so the helper can point at all three.
> - README gallery rows for 142–144.
>
> ## Console (`app/`)
> - **Blend tab** — pick ≥2 candidates (your own profile + marketplace, exactly the sources the backend accepts), set shares and a borrowed aspect each, see the live percentage, blend, view the recorded composition, and adopt the hybrid as the active profile.
> - **What If tab** — owner-only simulation runner: scenario + horizon, the prediction with its disclaimer, and the confidence shown *with* the source-items/remembered-turns basis it was earned from; past runs listed.
> - **Chat** — a 📍 toggle opens where/conditions/doing fields that ride as `environment` on the message; an adapted reply is labeled "adapted to where you are". Off until opened, empty until filled — nothing is inferred or collected.
>
> ## Verification
> - `tests/test_tutorial.py`, `test_dock.py`, `test_help.py`, `test_docs_gallery.py`, `test_spec_mined.py`: **82 passed** — every screen claimed by a lesson, every lesson reachable by the helper, gallery in sequence.
> - Console: `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #182 — The specification, mined: hybrid profiles, real-time simulation, environmental adaptation

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/182>

> A full read of the filed specification of App. 19/056,418 (SYNTHETIC USER PROFILE MANAGEMENT, docket 526.P002) turned up three capabilities the spec describes that the code did not yet have. Each is implemented here from the spec's own words, with tests in `tests/test_spec_mined.py` and a README section ("The specification, mined") citing the passages.
>
> ## Hybrid profiles — spec [0038]
>
> > "a combination of aspects or characteristics of several people, such as a combination of several past presidents or business leaders, a combination of trusted relatives such as grandparents who are gone"
>
> - `POST /profiles/composite` blends ≥2 source profiles into one `kind=hybrid` profile (`qrme/composite.py`): per-constituent normalized weights and an optional borrowed *aspect* ("their patience", "their storytelling"), recorded in `composite_sources`.
> - `GET /profiles/{id}/composition` publishes the blend to anyone — the same open stance as `/transparency`.
> - Sources must be the caller's own or marketplace-listed. **Departed profiles may be blended on purpose** (grandparents who are gone is the spec's own example); rated profiles never; `kind=hybrid` cannot be typed free-hand on `POST /profiles`.
> - The persona prompt carries the blend honestly: a hybrid says who it is a composite of and never claims to be any single constituent.
>
> ## Real-time simulation / predictive modeling — clauses 1 & 5
>
> > "real-time simulations of the first person's actions, workflows, and decision-making processes for predictive modeling and operational insights" · retained memory "utilized for predictive modeling"
>
> - `POST /profiles/{id}/simulate` (owner-only, `qrme/simulation.py`) predicts the decision, concrete workflow, and in-character rationale for a scenario over `immediate` / `short_term` / `long_term`, optionally conditioned on one relationship's memory and latent embedding.
> - `confidence` is **earned from evidence volume** (source items, remembered turns, embedding present) — never from how sure the model sounds. A profile with no material scores 0.2 however fluent its answer; conditioning on real memory raises it, and the test proves the ordering.
> - The narrative is watermarked synthetic, stored with its basis, and never distributed — which is also why there is no moderation step: moderation gates what leaves toward an audience, and a simulation has none.
>
> ## Environmental adaptation — clause 1
>
> > "dynamically adapt to environmental data, such as location, conditions, and user behavior, enabling contextual relevance"
>
> - `ChatRequest.environment` ({location, conditions, local_time, activity}) rides beside the claim-23 biometrics: stored in `environment_context`, rendered into the system prompt so the reply fits where the person actually is, and echoed back on `ChatResponse.environment`.
>
> ## Verification
>
> - `tests/test_spec_mined.py`: 11 new tests — blend + normalization, public composition, stranger/rated-source refusals, free-hand `kind=hybrid` refusal, hybrid chat, confidence honesty and ordering, owner-only simulation, environment storage/echo.
> - Full suite: **1205 passed** locally.
> - Live boot drive: profile → composite → simulate end-to-end against the stub provider.
>
> Console screens for the three features are left for a console round, matching how the claims 21–26 features landed (backend first, screens in 0.11.0).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #181 — Cut 0.11.1 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/181>

> In PDI, the desktop app finally carries its own vault. **1194 tests green**, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #180 — The console catches up with its backend — 0.11.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/180>

> Field-tested and found wanting: the backend has had friends (founder pinned first), a marketplace, a 33-profile starter collection, rooms across five channels, and live desks for many releases — and the console showed none of it.
>
> ## Three new screens
>
> - **Discover** — marketplace cards, tag search, one press to install the **33-profile starter collection** (idempotent server-side); every card is a real profile with an *Add friend* button.
> - **Friends** — the list with **David Bianchi and his synthetic profile pinned at positions one and two** (enforced by `qrme/friends.py` since the friends round — finally visible), plus suggestions.
> - **Rooms** — open and list rooms across **2D text / 2D audio / 2D video / AR / VR** (AR/VR carry an honest badge: step inside from a headset or phone; the desktop shows the room), plus **live desks** with presence and the 18+ badge where it applies. Backed by new `GET /rooms` and `GET /desks` list routes — the per-id routes existed; the doors didn't.
>
> ## The memory vault names names
>
> `GET /profiles/{id}/memories` (owner-only): one row per remembered conversation — *Dana with June Bianchi · 12 turns · last Tuesday* — never "profile" and "interactor". View any conversation; **erase exactly the one you choose**.
>
> ## Chat's fallback stopped performing a character
>
> "[stub reply in a warm tone to: hi]" was a stage direction leaking into the play. The fallback now quotes what it heard plainly, says no model answered, and names both doors out (a provider key, or Ollama). The quoted echo stays on purpose — moderation must see user-influenced text ride into the reply, end to end (the maturity-gate test depends on it and still passes).
>
> Cut **0.11.0** with the siblings.
>
> ## Verification
>
> **1194 tests green** (6 new): the vault lists conversations by real names, owner-only; erasing one conversation leaves the others; rooms list with their channels (voice/ar/vr) and participant counts; desks list with presence; the fallback carries no stage directions and names ollama.com. Console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #179 — A real offline model — 0.10.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/179>

> Same round as JIM-mini: **Ollama as a first-class Local provider**. Install it, `ollama pull deepseek-r1:1.5b`, and QRME finds the daemon on its own — the tile lights up configured, no key, nothing leaves the machine. Automatic prefers a running local model over the stub when no cloud key exists; offline mode uses it too. `QRME_OLLAMA_MODEL` / `QRME_OLLAMA_URL` override.
>
> Cut **0.10.0** with the siblings. **1188 tests green.** Console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #178 — Cut 0.9.1 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/178>

> In JIM-mini, the watch panel became honest about reachability. **1188 tests green**, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #177 — Cut 0.9.0 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/177>

> The three products are cut as one release. In JIM-mini, the medicine cabinet arrived: medications in the user's own words, a day board with humane grace, an as-needed ceiling that refuses to log past itself, and a coach that notices a missed critical dose without ever alarming.
>
> **1188 tests green**, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #176 — Continuity joined up — 0.8.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/176>

> No new routes: QRME's part of the continuity story was already built — reviewer-gated ownership succession (`POST /profiles/{id}/succession`) and the memorial sunset. What this round adds is the **join**, now documented: a JIM-mini vigil event id serves as the succession `verification_ref`, and the same reference activates PDI's new bequests — one attested absence carries through all three products.
>
> Disclosure entry added to `docs/invention-disclosure.md`. Cut **0.8.0** with the siblings.
>
> ## Verification
>
> **1188 tests green**, unchanged in behaviour. Console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #175 — The app keeps itself current — 0.7.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/175>

> Same round as the siblings: on launch the desktop shell asks GitHub Releases whether a newer version exists (`electron-updater`). Windows/Linux download in the background and offer one restart (`killBackend()` first, so the new version starts its own backend); macOS is told and taken to the download page. Every failure path silent by design.
>
> Also pays a debt the screens round left: the tutorial guard requires every drawn screen to carry a lesson, and **141 (the model picker) had none — the suite was red on `main`**. Lesson added under *You are in control*, plus helper directions ("which model", "swap the model", the provider names) so the dock can point at it.
>
> ## Verification
>
> **1188 tests green.** Console build clean; `main.cjs` syntax-checked; `electron-updater` packaged as a runtime dependency; `build.publish` set to this repo.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #174 — Screen 141: the model picker the gallery didn't show yet

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/174>

> One new screen in `docs/screens/build.py`, generated for **iOS and Android** and added to the README gallery:
>
> - **141 · Which Model Answers** — Claude speaking for the profile, five providers one tap away, the on-device key, and the amber honesty notice when a reply would come from the offline helper.
>
> (Authored first as `num=100`, which collided with *Video Full Screen* — the builder's stale-file sweep caught the strays; the number moved to 141, the next free slot. No duplicate numbers remain.)
>
> Every `docs/**.svg` referenced by the README verified present on disk.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #173 — Restore the owner's LICENSE exactly as he wrote it

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/173>

> PR #172 squash-merged a stale snapshot that still carried the license rewrite, so the rewrite reached main against the owner's explicit instruction. This restores the LICENSE byte-identical to his last deliberate license commit (`9ed125b` — "Update permission clause in LICENSE file"), along with the MIT metadata lines in `pyproject.toml` and `app/package.json` that accompanied it.
>
> The invention disclosure (`docs/invention-disclosure.md`) stays.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #172 — Record the inventions with dates

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/172>

> `docs/invention-disclosure.md` — QRME's distinctive mechanisms with dates and code anchors: the owner-governed synthetic profile with watermarked outputs, the single-chokepoint membership gate, request-scoped bring-your-own-credential inference, vault-sealed tandem custody, desk beacons, microphone lending. Written to be handed to a patent attorney, and standing as a public, git-timestamped priority-of-invention record.
>
> **The LICENSE is untouched — it stays exactly as the owner wrote it.**
>
> Not legal advice, and no substitute for counsel. No version cut: nothing behavioral changed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #171 — Model honesty in Settings — 0.6.1

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/171>

> The silent case was the bad one: *Automatic* quietly resolving to the built-in offline stub under a screen full of provider logos.
>
> **Settings → Which model answers** now shows an amber notice when replies would come from the built-in helper (no working key on the deployment), and when a picked provider has no key so another will answer. New `.degraded` style, distinct from `.error`: nothing failed to deliver — it degraded.
>
> (In JIM-mini, the same round also stopped the coach performing distress it never detected — see its PR.)
>
> Cut **0.6.1** with the siblings.
>
> ## Verification
>
> **1188 tests green.** Console `npm run build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #170 — Cut 0.6.0 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/170>

> The three products are cut as one release, so the version moves here even though QRME gained no route, no schema and no behaviour.
>
> In JIM-mini: the Apple Watch found its way in — a Shortcuts automation drips Health readings at a per-user tokened URL, and the Health app's export seeds the baseline from months of history in one upload.
>
> ## Verification
>
> **1188 tests green**, unchanged in behaviour — which is the point.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #169 — Pick your model by its own logo — 0.5.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/169>

> The model picker was a dropdown of provider strings, which is a poor way to answer "who is speaking for my profile right now."
>
> **Settings → Model** now shows a tile per provider — Claude, ChatGPT, Grok, Perplexity, Gemini — each with its own glyph, drawn here rather than copied, plus *Auto* for "whichever is configured." A provider with no credential says so on its tile instead of failing later.
>
> The choice rides the provider layer that already carried the bring-your-own-key header, so a request with `x-llm-api-key` still runs on the caller's credential and still never persists or logs it.
>
> ## Release
>
> Cut **0.5.0** with the siblings: CHANGELOG, README, RELEASE_NOTES, and all five version strings.
>
> ## Verification
>
> **1188 tests green**, including that the selected provider survives a restart, that choosing a provider with no credential reports that plainly instead of silently answering from another one, and that the request-scoped key still outranks the stored one. Console `npm run build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #168 — Email delivery is configurable from the app itself — cut 0.4.8

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/168>

> Mirror of jim-mini's round. An app hands mail to a mail server; until now the only way to name one was an environment variable, so a desktop install could never send a verification email at all.
>
> **Settings → Email delivery** (`mail_settings`, `GET/PUT/DELETE /settings/mail`, `POST /settings/mail/test`) now takes a mail server, username, app password, from address and link address. It reports which of three sources is in force — environment > settings screen > none — and **sends a real test message on demand**, surfacing exactly what the mail server said rather than claiming success. The password goes up and never comes back down.
>
> 1188 tests green. 0.4.8 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #167 — An upgraded app no longer adopts an older install's leftover backend — cut 0.4.7

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/167>

> Mirror of jim-mini's fix, from the root cause behind three "fixed" signups that weren't: the shell adopted whatever backend answered its port, and on Windows quitting killed the frozen backend's *launcher* while leaving the real Python process alive — so a zombie from an early install could hold 8000 across every upgrade and serve its old API to each new console.
>
> - `/health` reports the backend's **version**.
> - The shell adopts a running backend **only when that version is its own**; otherwise it takes a free port, starts its own there, and passes that exact address to the window (a stored loopback address never overrides it).
> - Quitting kills the backend's **whole process tree** (`taskkill /T` on Windows).
> - The release gate now asserts the frozen backend reports the version being packaged.
>
> 1180 tests green. 0.4.7 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #166 — A stranded pending account is finished on a no-mail machine — cut 0.4.6

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/166>

> Databases from older builds hold half-made accounts (0.4.3 crashed mid-signup) that nothing can ever verify where no mail can be sent — and they were resurrecting the email screen on desktop installs. Retrying signup on a no-mail deployment now finishes the pending account on the spot, under the newly-typed password. A **verified** account is never overwritten this way, on any deployment; SMTP deployments still require the emailed proof. Guard test covers both sides. 1179 tests green. 0.4.6 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #165 — Verification matches the deployment: direct on desktop, link-first by mail — and the 0.4.5 cut

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/165>

> Mirror of jim-mini's round, from the same 0.4.4 field report: the code screen waited for an email that can never arrive — a desktop install has no mail service.
>
> - **Desktop (no mail transport): signup activates directly.** The machine owner is trusted on a single-user local install; there is no inbox to prove. Create account → into profile creation.
> - **Hosted (SMTP): the email now leads with a clickable verify link** (`GET /verify-email/click`, human-facing result page), 6-digit code as fallback; the app polls sign-in with the credentials it already holds and continues on its own after the click.
> - A pending account left by a crashed signup routes straight to verification with a fresh code instead of stranding the retry; already-verified routes to sign-in.
> - The packaged app can open its own backend log (Electron bridge button).
> - Smoke gate updated: the frozen binary must now sign up **straight into an account session** on each OS, then create a profile and chat.
>
> 1178 tests green; frozen binary rebuilt and smoke-passed locally; consoles typecheck and build. 0.4.5 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #164 — Release gate: the frozen backend must perform the real first run, per OS

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/164>

> No installer ships a first run that was not performed. Before electron-builder touches anything, the exact PyInstaller binary that will be packaged runs the whole flow **on the runner's real OS** — signup, the code read from the console log the way Electron pipes it, verify, a profile under the account, a chat, sign-in — with `PYTHONIOENCODING=cp1252:strict` so the Windows console-encoding class of failure is exercised on every platform, Linux included.
>
> 0.4.3 shipped a Windows-only signup 500 this step would have refused to package. "It worked on Linux" stops being a release argument here.
>
> Verified locally against fresh frozen binaries, twice in a row each (the double-run caught and fixed a leftover-process bug in the gate itself: PyInstaller one-file spawns a child the parent's kill doesn't reach — per-run ports + process-group kill now).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #163 — Fix the Windows signup 500, and cut 0.4.4

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/163>

> Reported from a real 0.4.3 Windows install within the hour of shipping: signup answered `Unexpected token 'I', "Internal S"… is not valid JSON`.
>
> Two stacked bugs:
>
> - **The backend 500'd**: with no mail server configured, the verification code prints to the server console — in a banner drawn with `═` box characters that the frozen Windows backend's cp1252 stdout cannot encode. The print raised mid-request. ASCII banner now; `packaging/backend_entry.py` reconfigures stdout/stderr to replace rather than raise; a test encodes the console delivery to cp1252 forever (mutation-checked: restoring one box character fails it).
> - **The console hid the real error**: `req()` assumed every body is JSON, so the person saw a JSON.parse exception instead of "Internal Server Error". Non-JSON bodies now surface as the server's own words.
>
> Plus the 0.4.4 release prep (changelog, notes, README table, five version strings under the guard). 1175 tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #162 — mac: declare the frozen backend in x64ArchFiles

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/162>

> The `app-v0.4.3` build failed on macOS only: the universal build merges the x64 and arm64 app bundles, and `@electron/universal` refuses any file identical in both that is not declared — which the PyInstaller backend binary is, being one file for both architectures. One config line: `mac.x64ArchFiles: "Contents/Resources/backend/*"`.
>
> Windows and Linux built fine; the release job skipped (and no installers attached) only because the matrix had this one failure. After merging, move the `app-v0.4.3` tag to the fix commit and the workflow will attach the full installer set.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #161 — Accounts, bring-your-own model key, the self-running installer — and the 0.4.3 cut

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/161>

> Four commits: the QRME half of the packaging round, the account layer mirroring jim-mini's, a gitignore fix, and the 0.4.3 release prep.
>
> ### Accounts: email + password, the address verified before sign-in works
>
> The account is what *owns* — its id is the `owner_id` profiles are created under and the `account_id` memberships bill to — while every profile keeps its own owner capability token exactly as before. `POST /signup` creates an account that **cannot sign in yet**: a 6-digit code goes to the address (SMTP when `QRME_SMTP_HOST` is configured, printed to the server terminal otherwise) and only `POST /verify-email` proves the inbox and mints the first account token. `POST /signin` refuses unverified addresses and answers unknown-address and wrong-password identically; `POST /password/reset/request` + `POST /password/reset` change a forgotten password by the same emailed-code proof and **revoke every account session**. Passwords PBKDF2 with per-account salts; codes hashed at rest, single-use, 15-minute expiry, purpose-bound. The console onboarding is now two stages — the account gate (tabs, show/hide toggles, re-enter password checked live, Forgot password) and then profile creation under the signed-in account.
>
> ### Bring-your-own model key
>
> `x-llm-api-key` rides any request into a request-scoped context variable the provider layer reads — that request's generations run on the caller's credential, **never persisted, never logged** (a test dumps the whole database and asserts the key isn't in it). An explicit provider choice plus a caller key counts as configured; a key on auto defaults to Claude rather than the stub; the deployment's env key remains the fallback. The Control Center stores the key device-side only.
>
> ### The installer runs itself
>
> `packaging/backend_entry.py` freezes the whole backend with PyInstaller; the release workflow builds it per-OS and ships it via `extraResources`; Electron probes `/health`, spawns the bundled backend when nothing answers, and kills it on quit. Verified on Linux: the frozen binary boots and answers.
>
> ### Cut 0.4.3
>
> Changelog, release notes, README release table, all five version strings moved together under the five-way guard.
>
> **Verification:** 1174 tests green (16 new). `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #160 — Online model default, and the desktop first-run fixed

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/160>

> Three commits, all from running the product for real today.
>
> ### Default the Anthropic provider to claude-opus-5
>
> The default model string in `qrme/llm.py` (and the two README rows quoting it) still named the previous Opus generation. `QRME_MODEL` still overrides; every other provider default untouched.
>
> Verified live: with `QRME_LLM=anthropic` the server dials the real Anthropic API on every chat (request IDs minted by api.anthropic.com), `GET /models` reports `claude-opus-5`, and the per-profile switchboard (`PUT /profiles/{id}/model`) stores and honors provider choices.
>
> ### Desktop onboarding first-run (same defects reported against JIM Guardian's Windows build)
>
> - The age-verification field shipped pre-filled with a sample birthdate; it now starts empty and Create My Profile waits for a real one. (The name field was already deliberately empty here — JIM's screen broke that rule; fixed on its side in jim-mini#111.)
> - A network-level fetch failure surfaced as "Failed to fetch"; it now names the backend URL it could not reach and how to start one.
>
> ### serve: default CORS open on loopback, so the console's own advice works
>
> Same dead-end as JIM Guardian's: the packaged console calls the API cross-origin, and `python -m qrme serve` never set `QRME_CORS_ORIGINS`, so every request died as "Failed to fetch" against a backend that was running fine. A loopback serve now defaults CORS open — the posture the in-app hint has always instructed — announced on stdout, with `--no-cors` to keep it closed, and never when binding beyond loopback or when an explicit allowlist is set. Owner and interactor endpoints still require their bearer tokens. Four tests. The console's error message now names `python -m qrme serve` (bare `python -m qrme` only prints the launcher menu).
>
> Verified: `tsc --noEmit && vite build` clean. 1158 backend tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #159 — The desktop installers were labelled 0.3.3

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-viewfinder` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/159>

> Found while verifying the app-v0.4.1 release you just published: the attached installers are named `QRME-0.3.3-universal.dmg`, `QRME.Setup.0.3.3.exe`, etc.
>
> `app/package.json` carries its own version and no cut ever bumped it — the 0.4.0 and 0.4.1 releases both attached installers stamped 0.3.3. They were **built from the right tag and contain current code**; only the label is stale. The part that actually bites is the auto-updater, which compares package versions and will tell an installed app there is nothing newer.
>
> Same disease as the stale test counts and the stale refusal counts this round already fixed: a duplicated number with nothing to fail when the other copy moves.
>
> - `app/package.json` → `0.4.1`
> - A guard test asserting it always matches the API version, mutation-checked
> - The launcher's `package.json` is deliberately untouched — it versions on its own cadence and its assets are not stamped with the release number
>
> The already-published 0.4.1 installers keep working; the next tag builds correctly named ones. No re-tag needed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #158 — Cut 0.4.1 — the round where free got honest, and the claims got checked

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-viewfinder` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/158>

> Release housekeeping only — no code beyond the version string. 1153 tests unchanged.
>
> - CHANGELOG: `[Unreleased]` → `[0.4.1] — 2026-07-28`
> - `qrme/api.py` version `0.4.0` → `0.4.1`
> - README: header to v0.4.1, a 0.4.1 row in the release-history table
> - `RELEASE_NOTES.md` rewritten as the ready-to-paste body for the `app-v0.4.1` release
>
> Two leftovers from the previous cut, fixed while passing: the CHANGELOG's `[Unreleased]` compare link still pointed at `app-v0.3.3` and no `[0.4.0]` link ref was ever added; and `RELEASE_NOTES.md` was still the 0.3.3 body.
>
> After merging: create the `app-v0.4.1` tag on the merge commit and paste `RELEASE_NOTES.md` as the release body — tags and releases are proxy-blocked for this session, so those two steps are yours.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #157 — Channel 3, a free plan under platform custody, and the guards that check the claims

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-viewfinder` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/157>

> Four rounds on one branch, because they interlock. 1153 tests pass.
>
> ## Channel 3 — sharing your camera
>
> `qrme/viewfinder.py`, 7 routes, 28 tests, screens **136** and **137**. Point your camera at the thing — a knocking engine, a boiler, a document — so somebody else can see it, like screen-share but for the room. The subject sets the rules: a thing, place or document can be watched by anyone; **a body only ever by a person, never a synthetic profile**. Two taps to open, one to close, hard time cap, disclosure on every surface, and `NEVER` (camera control, capture trigger, background start, silent run) asserted rather than intended.
>
> ## A free plan, with nothing private about it
>
> `qrme/storage.py`, 38 tests, screens **138–140**. Two postures: **open cloud** (Free — the platform's own database, in the clear) and **vault** (Basic and Pro — sealed in PDI under a key you can hold). Free and Basic reach identical capabilities — `includes("free") == includes("basic")`, asserted — so **$20 buys privacy, not features**. The disclosure is a field on every surface that states a plan, and the open posture names its readers instead of gesturing at them.
>
> Refused rather than quietly exposed, on the test *whose exposure is it*: source material about somebody else, anything behind the age gate, and **a clinician's written opinion about a real person** — which was heading for the open store because the referral flow writes through `referral.reply` rather than `add_source`, so the third-party rule never saw it. Refused at `/referrals/prepare`, before any clinician is contacted.
>
> ## Platform custody, and the vault gate that asked the wrong question
>
> The free plan is the hosted-assistant arrangement: **QRME holds the work and the person has access to it**, over ordinary HTTPS, never through a vault. Named as **custody, not ownership** — a product decides who holds and operates a record; it does not get to decide away statutory rights over personal data.
>
> The bug underneath: every seal point read `if pdi is not None` — whether the *deployment* has a vault, not whether the *account* pays for one — so a free account on a PDI-backed deployment had its work sealed into a vault it could not hold a key to. `storage.vault_for(plan, pdi)` is now the one place the question is asked, guarded by **counting vault writes**, not reading call sites. Reads, deletions and signing keep the real vault deliberately: a plan-gated vault on a read strands a downgraded account's history; on a delete it fakes erasure; on `_seal` it silently stops writing the custody chain, since signers are often interactors with no membership.
>
> ## The guards that check the claims
>
> - A hard line is never answered with a price: a rated profile of a real person is 403 at any amount, ordered before the 402 posture check.
> - No user-facing copy may hardcode a refusal count that disagrees with `len(SENSITIVE)` — this drift shipped (four places said "two" after the list grew to three), and screen 140 didn't draw the third refusal at all.
> - The README's own arithmetic is now tested: every "`module.py`, N tests" claim is verified against the files, after two were found stale.
> - A refusal test must be reached by a request that would otherwise succeed — a mutation check caught one of this PR's own tests passing with the guard removed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #156 — v0.4.0 — the social layer, channel 2, who you are allowed to be, and a price

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-friends` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/156>

> **Cuts v0.4.0.** Fifty-four commits. Eighteen new modules, 1,086 tests, 352 endpoints, 135 phone screens, 9 watch faces, 14 desktop views.
>
> The original title said the founder *"can be removed"* and the body said `DELETE` works on him like anybody else. That was true of the first commit and stopped being true two commits later, when the pin was made unremovable. Since this squashes onto main, that description would have become the record — so it is rewritten here rather than left to be the thing somebody reads in a year. The same applies to the last line of the previous version, which said channel 2 remained held. It is now green-lit and included.
>
> ## Who you stand with
>
> `friends.py` — profile ↔ profile, deliberately **not** the existing `relationships` table, which records how a profile treats an *interactor*. A test pins them apart, because a bug that read one as the other would look exactly like working code.
>
> Directed, not mutual: `befriend` writes one row, because a friends list is a claim its owner makes and a mutual edge would let somebody else edit yours. `mutual` is reported per entry so a surface shows the difference rather than inventing it.
>
> **Two founder rows, pinned first and unremovable.** `unfriend` refuses them by name — enforced in the one function every removal path goes through, not at each call site. Position is computed from `origin`, never stored, so it cannot drift out of step with what the row says.
>
> `verification.py` gives the pair its meaning: a **photograph** with a gold VERIFIED mark burned bottom-right, and an **AI rendering** with the AI badge. *This picture is authentic* and *this profile is synthetic* are two different claims, so they live in two directories — `/photos` is never AI-marked, `/portraits` always is.
>
> ## Anonymous, several, and exactly one verified
>
> `identity.py` — 8 routes, 21 tests, screens 118 and 119. Three things a person is allowed to be, and the module is the tension between them: you may be anonymous, you may hold as many profiles as you like, and **at most one may be verified**.
>
> The badge is not a quality score. It is the sentence *this is that particular real person* — said of two profiles at once it is either false of one of them, or a claim that one human being is two authenticated people, which is precisely the primitive verification exists to deny everybody else. So it **moves rather than multiplies**: one at a time, not one forever, because a rule somebody could only satisfy by deleting a profile is a rule they would answer by lying. `checked_at` is deliberately not re-stamped — a document seen in 2019 is not a document seen today because the badge changed seats.
>
> A `fictional` profile is **unverifiable rather than unverified** and never consumes the slot; getting that backwards would let an invented character lock a real person out of their own badge.
>
> **Writing the rule found the defect underneath it.** `anonymous` was honoured by the four surfaces that *render* a profile — front-page card, landing page, prompt, watermark — and by the route that returns one, not at all. `GET /profiles/{id}` is public and handed over `display_name` in full, so the shortest way past anonymity was to ask for the profile.
>
> `owner_id` was the worse half, because it does not undo one profile's anonymity — **it undoes all of them at once**. Two anonymous profiles sharing an account are the same person, and anybody could read that field off both and match them, then read it off the named profile beside them and put a name to the pair. Both withheld from everyone but the owner now, on every profile, along with `successor_owner`.
>
> An anonymous profile's badge withholds **who checked**: "verified by Dr Okafor of St Mary's" narrows an anonymous author to a city and a workplace. What survives is the part worth having, and the reason an anonymous profile would want one — *a real person stands behind this, and somebody checked* — which is the difference between a pseudonym and a bot.
>
> And the rule immediately caught **the seed verifying both founder profiles**. They are the same man, so the platform was asserting he was two verified people, on the deployment that ships as the worked example.
>
> ## Channel 2 — lending the room's profiles your microphone
>
> Green-lit, so screen 81 comes off hold. In a voice room your microphone is carrying your voice to the other people; the profiles are reading text and have no ear. This lends them the watch on your wrist.
>
> **The disclosure is the design, so the disclosure is the screen** — it shows the other participants *by name* seeing the grant. Restoring it from the shelved branch, the text-width guard added since rejected three of its five card strings, which had run off the phone unnoticed where the screen was first drawn.
>
> **The disclosure route was the real find.** Its docstring said "readable by anyone in the room"; the code checked nothing, so "in the room" meant "knows the id" — and a room id rides in beacons and on printed QR stickers, which is what they are for. Anyone who scanned a sticker could read who was wearing a live microphone, on what, and since when. That is a privacy feature inverted. A signed-in stranger is now refused as firmly as an anonymous one.
>
> **Pairing and lending were two vocabularies for one collar clip.** The registry says `lapel_mic`; this module and `jim/mic.py` say `lapel`. Nothing joined them, so you could pair a lapel mic and be told it was an unknown microphone type — from a registry whose own comment says it exists for this feature. Translated rather than renamed, because renaming either side breaks something real.
>
> Plus `GET /microphones/vocabulary`, open, with the refusals published **by name and reason** — a client that knew only the allowed list would grey out a conference puck as though the feature were unfinished, when its absence is the whole argument.
>
> ## The page you make yourself
>
> `markup.py` is a real HTML allowlist — because the version of this that took raw markup is why the Samy worm took MySpace offline in 2005. Script, frames, forms, `on*` handlers and `javascript:`/`data:` URLs are gone, content and all. Sanitised on the way **in**, so exactly one moment of unsafe markup exists rather than one per renderer.
>
> `pages.py` carries themes, a Top 8, the profile's own marketplace listings read live rather than copied, up to twelve links under the same URL rule, and the For You feed inline.
>
> ## The wall, and the feed
>
> `wall.py`. The ranking uses **public actions only** — never memories, source material or anything vaulted, and a test parses the ranking's own SQL to hold that. Every entry says *why* it is in front of you. Popularity is capped so one loud stranger cannot outrank every friend.
>
> `embeds.py` posts video from five platforms. Nothing is copied — the platform, the id, and the title **you** typed. **No request reaches YouTube until somebody presses play.** The URL is rebuilt from the id, so a tracking parameter or `youtube.com.evil.tld` cannot ride along.
>
> `revisions.py` lets people edit and retract what they said, and the correction is what the next turn reasons from.
>
> ## Rooms, and everything full screen
>
> `watchparty.py` — synthetic profiles in the room, and the honest part: **a profile has not seen the video and cannot.** Its context reports `transcript_available: false` and *tells* the profile it has not watched. Starving a model of context and hoping is not a safeguard. The room shares a position, not a player.
>
> Seven surfaces get three full-screen states each — plain, held, sideways. A long press dims to 78% and returns the help button, which is otherwise gone from live surfaces because a floating `?` on a video is a permanent smudge sitting where the share button goes.
>
> ## Work, agreed before it moves
>
> `exchange.py`. What crosses in each direction item by item, what is included at the end and **what is not**. Both sign, and only then does anything move. **Any change voids both signatures** — stored against a hash of the agreement, not its id. Items that *run* are flagged. It grants **no device access**, and that limit is in the code.
>
> `sharing.py` lends a skill inside a room, desk, party, connection or exchange. **Two to open a grant, one to close it** — symmetric consent to start makes it a loan; asymmetric consent to end stops it being a trap.
>
> `wearables.py` pairs watches, bands, earbuds, lapel and clip-on mics at sign-up. **Room-facing microphones are refused at the door** — a smart speaker hears whoever walks in, and they did not pair it, were not asked, and may have a right not to be recorded.
>
> ## What the audit found
>
> All operations exercised with schema-derived bodies: **no 500s**. Algorithms probed at their edges — entity-encoded `javascript:`, a null byte in a scheme, `https://www.youtube.com@evil.tld` — all refused.
>
> What it did find was cost. One 25-item feed ran **584 SQL statements**, because it hydrated every candidate before ranking. Three N+1s: feed 584→6, friends list 41→3, and the feed's tag lookup from one-per-friend to one.
>
> ## Defects fixed on the way
>
> - **Three routers had no authorization at all.** An anonymous stranger could forge both signatures on somebody else's exchange, open its channel, and accept delivery of an executable on their behalf. Fixed with `require_self`/`require_one_of`, and a sweep test asserts no two-party route can be added without a way to identify its caller.
> - **Text ran off the side of the phone** on eight screens. `textwidth.py` is a *measured* advance-width table (`Companion` and `lllllllll` are both nine characters and one is nearly twice as wide), and `audit.py` measures every `<text>` in every file.
> - **`Ring the bell` was drawn below the tab bar** on Live Desks — the button that screen exists for, painted over by an opaque bar.
> - **A failed build corrupted its own output**: `open(..., "w")` truncates before the generator runs, so a raise left a zero-byte SVG. Fixed in all four builders.
> - **Stale SVGs were never pruned** — renumbering left six files still rendering a product that no longer existed.
> - **`/{surface}/{surface_id}/…` was about to ship**, and a two-variable prefix matches any three-segment path. `tests/test_routing.py` asserts it for every route, mutation-checked against a planted shadow.
> - **Nothing tied the README gallery to the screens on disk** — and this round produced the third instance of that class: inserting screen 81 into a full three-wide row pushed **82** off the page. Every file existed and every link resolved, so both existence checks would have passed while the gallery read 79, 80, 81, 83. The numeric run is now asserted too.
> - **`docs/tandem.md` was 92 lines short in PDI** — a file meant to be byte-identical in three repos was identical in two.
>
> ## Everything you present as, on every device
>
> `overlays.py`, `identity.py`, `gamelobby.py`, `displays.py` — wear a character
> over your camera, change what is behind you, hold several profiles with at most
> one badge, sit beside a game without ever being in it, and put a profile on a
> wall panel.
>
> **A live person under a mask is still marked as real.** The first cut refused
> overlays on a live desk, conflating *this face is unmodified* with *a real
> person is here*. Those are different claims and only the second is what the
> badge says: viewers arrived at a named account on purpose, and the name is at
> the top left of every live surface. So the desk keeps `NOT AI · REAL PERSON`
> whatever is worn over it — burned in, tied to the account, and the same mark
> whether the face is bare or covered. A user with facial dysmorphia gets to use
> the product without giving up the badge that says somebody is there.
>
> **A generated background says so and a real face does not have to.** Your own
> photo needs no mark; an AI-made room carries one, because a synthetic
> *background* is synthetic media even when the person is not.
>
> **No synthetic member ever occupies a player slot** — not as a second
> controller, not over Bluetooth, not on a console of its own, and not through a
> capture card, which is the workaround people actually propose: watching the
> screen in order to play *is* playing. Twelve refusals by name, on their own
> screen, because a rule nobody can see is a rule somebody will test.
>
> **Anonymous is a property of the profile, not a label on four surfaces.**
> `Anonymous NNNNNNNN`, fixed and unchangeable, with the account withheld so two
> of somebody's profiles cannot be matched to each other.
>
> ## Three-way coverage, and the audit that forced it
>
> Channel 2 got a watch face because an audit before tagging found the feature was
> phone-only — odd, since **the watch is the device being lent**. Run against
> everything else this round, the same audit found the same hole five more times.
>
> Watch faces **06 Identity, 07 On Camera, 08 Lobby, 09 Screens** are one question
> in five shapes: *what am I currently presenting as?* None of them can change
> anything; face 05 stays the single exception, because a permission you cannot
> revoke from the device running it is not really yours. Desktop views **12–14**
> are the ones a wide window earns — 13 folds overlays, backgrounds and displays
> into one view, because at a desk they are one question rather than three
> modules.
>
> The face↔permission binding test was tightened while it was open: it reads an
> explicit `face="..."` key out of the builder instead of inferring the face from
> a title. The alternative was loosening a regex that could not match "On Camera",
> which would have let a face drawn under any unmatched name pass silently.
>
> ## A guide, a pane, and directions
>
> `tutorial.py` — seventeen steps, seven chapters, in an order that introduces
> nothing before it exists. **The guide has no name and no face**, structurally: a
> tutorial guide with a persona would be the most convincing synthetic profile on
> this platform, met by every user in their first minute, at the exact moment they
> have the least idea what is synthetic here. It never taps anything for you, it
> works with no model configured, and **it cannot quietly fall behind the app** —
> each lesson names its screens and a test binds the set to the gallery in both
> directions.
>
> **Voice and text are one lesson rendered twice.** The assistant delivers it:
> *"show me around"* is not a question with an answer, so the help box starts the
> tour inline rather than handing back a paragraph about tours.
>
> `dock.py` — the watch faces in a pane that tucks into the bottom corner, for the
> people who own neither a watch nor a wall panel. It casts the *same* faces,
> bound by test to `wearables.FACES`. **It shows and it routes; it never acts** —
> the exact inversion of the watch's one exception, because nothing here is the
> device and a control floating over live video is a mis-tap on somebody's
> broadcast. **It is inside every screenshot**, so no message bodies, no memory,
> no agent names, no viewer names, and on a surface being broadcast it opens
> tucked with the preference returned alongside rather than overwritten.
>
> On the desktop it **replaced** something rather than joining it: that corner
> already held a pinned agent-lights panel with no way to close it — three
> quarters of this feature, missing a lid.
>
> And *"where do I change my background"* now gets directions instead of a
> description. `help.DIRECTIONS` is keyed by tutorial lesson, a test asserts every
> lesson is reachable, and the answer names the screen plus the dock face when
> there is one — read from `dock.ROUTES`, so the assistant and the corner cannot
> disagree about where a feature lives.
>
> ## Two more defects of the same kind
>
> - **A screen title's punctuation reached its filename.** "Where Is It?" produced
>   `129-where-is-it?.svg`, where the `?` starts a query string and the README's
>   `<img src>` draws a broken icon. A comma had done it once already. Both came
>   from the slug being written out by hand in **two places that disagreed** — the
>   sweep that deletes stale files and the write that creates them — so the
>   builder now has one `slug()`, and a test asserts no screen file is named
>   something a URL cannot carry.
> - **The desktop avatar was painted over the header pill on every view**, sitting
>   at a hard-coded 96px while `status_dot` sizes itself from its label. It read
>   as a rendering glitch on all eleven views, which is how long it survived: the
>   header is the part of a mockup nobody looks at twice.
>
> ## Membership: Basic $20/month, Pro $130/month
>
> `qrme/tiers.py`, 4 routes, 26 tests, screens 130–135.
>
> | | | |
> | --- | --- | --- |
> | **Visitor** | free | read any public page — a scanned beacon needs no account |
> | **Basic** | $20/month | make your own profiles and your own agent |
> | **Pro** | $130/month | everything that leaves your account: marketplace, connectors, skills, downloads, connections, and every modifier and builder |
>
> **Visitor is a real state, not an oversight.** The whole reach story is a
> stranger scanning a printed code and landing somewhere useful. A wall asking
> them to subscribe before they could read the page would break the feature the
> beacons exist for.
>
> **Enforcement is one table and one chokepoint.** `tiers.gate` is installed once
> as an application-wide dependency, so **no route opts in** and none can be
> forgotten at the eleventh endpoint. The alternative was a `require_plan(...)`
> call at the top of every paid handler — the exact shape this repository has
> been bitten by twice: a docstring claiming a check the code did not make.
>
> **That table is asserted against the served routes, and the first version
> failed.** It named `/steering`, `/governance` and `/licensing` as prefixes.
> None is a route here — steering lives at `/profiles/{id}/steering` — so all
> three were **paywalls in front of a wall**: they read as protection, protected
> nothing, and would have survived indefinitely, because nothing fails when a
> pattern matches no traffic. Patterns now, not prefixes, because most paid
> capabilities hang off a profile and a prefix table cannot say that without
> gating the whole `/profiles` tree.
>
> **Browsing stays open, and that is a decision.** A Basic member may look at the
> marketplace and may not transact on it. A paywall that hides the shop from the
> person you are trying to sell to argues against itself, and the catalogue is
> public to strangers anyway.
>
> **The refusal is structured, because 402 is already spoken here.**
> `POST /packs/{id}/install` answers 402 for *this pack costs money, confirm the
> price*. Both are genuinely payment-required, so the status is right for both —
> but a client must show *upgrade* for one and *confirm* for the other, and
> telling them apart by matching on prose breaks the first time somebody rewords
> a message.
>
> **A membership belongs to the account, not the profile** — per-profile would
> mean paying twice to hold two profiles, which is exactly what `identity.py`
> exists to let people do for free. Creating a profile enrols a new account on
> Basic; an existing member keeps their plan. **Cancelling keeps the profiles.**
> Money is simulated throughout, and a test asserts nothing reaches a processor.
>
> ### Signing up carries the plan
>
> Screens 132–135. The tier work landed the price list and the gate; what it did
> not do was put the choice anywhere in the journey somebody walks. First run was
> 41 → 42 → 43 → 44 → 47 with no plan step in it.
>
> **132 Pick a Plan** is in-flow and deliberately not the same screen as 130 —
> its third card lets you decline and keep looking. **133 Payment** is drawn
> rather than skipped, because a signup flow has one and pretending otherwise
> makes these mockups a worse guide than the product — but it carries the
> simulation pill and a card saying no processor is called, since a convincing
> checkout is the one place here somebody could reasonably be misled about money.
> **134 You're on Basic** names what is *not* included, which is the honest half
> of an upsell. **135 This Needs Pro** renders the structured 402.
>
> Walked end to end against the running app rather than assumed: a visitor reads
> the price list, creating a profile enrols on Basic with six capabilities
> locked, the marketplace returns `{reason: plan, needs: pro, price_usd: 130}`
> with billing disclosed, upgrading opens the same call, and browsing was never
> gated at any point.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code)_

## #155 — Release 0.3.3, and a README that leads with the screens

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-0.3.3` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/155>

> Cuts **0.3.3** across the suite, and reorders the README so the screens come first.
>
> ## The README
>
> The page opened with roughly 650 lines of prose and put the screen galleries near the bottom, which is backwards: the screens are the part you can understand at a glance, and the prose is the part you read only if the screens raised a question.
>
> New shape:
>
> 1. **Title and intro** — unchanged
> 2. **The screens** — desktop and mobile galleries, then the portraits and starter collection
> 3. **What it does** — the capability sections
> 4. **Reference** — Architecture, Run, Run it on your phone, Configuration, Test, Example flow, all under one heading at the bottom
>
> The point of the Reference block is that it has an address. If you see a command in one of the screenshots and don't know what it does, it is in one place at the end rather than scattered through the middle.
>
> Those tables are **set smaller**, because they are for looking things up in rather than reading through. Two implementation notes, since neither is obvious:
>
> - GitHub's markdown sanitiser **strips `style`**, so `<sub>` is the only size control actually available. This repo already used it for the gallery captions, so it is known to render.
> - Markdown is **not processed inside an HTML block**, so the converted cells emit their own `<code>`, `<b>` and `<a>` rather than leaving backticks and brackets to show up literally.
>
> ## Release contents
>
> The agent status light — the mapping in `qrme/agentlight.py`, screens 82 and 83, the desktop overlay on every view, and the README section explaining it. Full detail in [CHANGELOG.md](CHANGELOG.md).
>
> Version bumped in all five places (`pyproject.toml`, the `FastAPI(...)` call, `app/package.json`, and both root entries in `app/package-lock.json` — dependency pins left alone), the `[0.3.3]` link definition added, and `[Unreleased]` repointed.
>
> ## What is deliberately not in this release
>
> The held work stays under `[Unreleased]` and is named nowhere in the changelog entry or the release notes. I also checked what GitHub will auto-generate for *What's Changed*: the only PR merged since `app-v0.3.2` is #154, whose title is about the agent light. That is the surface that leaked once before, so it is checked rather than assumed.
>
> ## Verification
>
> - 633 tests pass; both starter generators idempotent under `--check`.
> - The restructure was verified by diffing the prose line-by-line against the previous README: **nothing lost**, the only differences being the version bump and the new Reference intro. The word count *drops*, which is just table pipe characters disappearing into HTML.
> - Every generated table was checked for a uniform column count, and rendered in a browser to confirm it reads as smaller without losing its code spans or links. That check caught a real bug: cells containing an escaped `\|` were being split as if it were a column separator, which invented a column and shifted the rest of the row. Fixed and re-verified.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #154 — Agent status light: watch, app, and an overlay that follows you

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-agent-light` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/154>

> One question, answered everywhere: **does this agent need me right now?**
>
> ## The mapping
>
> `qrme/agentlight.py` is the only place the meaning lives. Five workflow statuses collapse to three colours, and each colour carries a word — a colour alone cannot separate an agent that is still going from one that has finished, and those call for opposite reactions.
>
> | status | light | word |
> | --- | --- | --- |
> | `running` | green | working |
> | `completed` | green | done |
> | `awaiting_input` | amber | needs you |
> | `failed` | red | stopped |
> | `cancelled` | red | stopped |
>
> Two properties are structural rather than conventional:
>
> - **Derived, never stored.** The light is attached in `_hydrate()`, the one function every workflow read passes through, so a row cannot be persisted with a light that disagrees with its status. A test asserts no `light` column exists.
> - **Unknown statuses raise.** A new status added later without a light fails loudly instead of quietly defaulting to green — the one wrong answer that would matter.
>
> `GET /agent/lights` returns the legend, built from the mapping rather than restated alongside it. Routes 211 → 212.
>
> ## The three surfaces
>
> They do three different jobs, and that is the point.
>
> - **Watch — face 36 (in JIM).** Three lights, three counts, **no agent names**. Naming them was the first cut and was wrong: a name is something you read, and reading is the thing a glance cannot do. Which agent went amber is a question for the app, where there is room to answer it.
> - **App — screen 82.** The same three lights, each a tappable group. Somebody opening this *because* amber appeared should not have to scan a flat list for the one that changed.
> - **Overlay — screen 83, and every desktop view.** A pinned strip with the counts and a way in. An agent that reports only on its own screen is one you have to remember to check, and amber and red are exactly the states nobody thinks to go looking for. On desktop it rides on every view, because those users have no wrist to glance at.
>
> Screen 81 is left free for the held work.
>
> ## Also
>
> - Screen 65's pills read `WORKING` / `NEEDS YOU` / `STOPPED` instead of naming colours.
> - `agent_groups()` length-guards its subtitles. Two of the three ran under the chevron — visible in a render, invisible in the source — so the next one fails the build instead of arriving as a screenshot weeks later.
>
> ## Verification
>
> 633 tests pass. 9 new ones cover the mapping: every written status has a light, unknown statuses raise, only amber sets `needs_you`, exactly three colours exist, no stored column, and the light follows the status through the API and the listing. The guard was mutation-checked — a 31-character subtitle fails.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #153 — Release prep v0.3.2

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-v032` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/153>

> Cuts **v0.3.2** — the starter-card work and the rated starter's grounding.
>
> Neither had a changelog entry. They went to `main` across #151 and #152 and were
> described only in commit messages, which is not where anybody looks.
>
> ## What this release contains
>
> - **The starter gallery shows each profile's own front page.** Screen 80, not a
>   captioned thumbnail: bubble, role, the rating people left, skill chips, Memory
>   / Relationships / Engagement, a career, a review, a Talk-to button. Two columns
>   instead of five, so a phone stops slicing the fourth column mid-word.
> - **Fixed: the rated starter had no source material at all.** The Cabaret &
>   Burlesque Field Pack grounds her in theatre history and stagecraft. Seeding
>   reports `grounded: 34` where it reported 33.
> - **Fixed: a test was asserting that gap into place** —
>   `test_starter_packs_cover_every_industry` compared against `STARTERS` and not
>   `STARTERS + RATED`.
>
> ## What stays under `[Unreleased]`
>
> Channel 2, same as 0.3.1. Its code is on `main`; it is not part of a described
> release.
>
> ## Release mechanics
>
> Version moved in all five places, with the lockfile's two root entries verified
> as exactly two changed lines. Changelog sectioned, link definition added,
> `[Unreleased]` repointed at `app-v0.3.2`. README's current-release line and
> table row updated.
>
> **Tag this commit, not the tip of `main`.**
>
> ## Verification
>
> 624 tests green, 211 routes. No microphone content anywhere in the diff.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #152 — Starter cards: the whole of screen 80, career and reviews included

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-starter-cards-v2` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/152>

> Rebuilds the starter gallery cards from **screen 80** — the profile front page a
> visitor actually lands on — instead of screen 5, and carries it all the way
> through rather than stopping at the rating.
>
> ## Each card now has
>
> - avatar bubble with the AI mark burned in
> - name and role
> - **star rating and review count**
> - skill chips
> - **Memory · Relationships · Engagement**
> - **EXPERIENCE** — two posts, employer and dates
> - **REVIEWS** — a name, stars and a line
> - **Talk to …**, with the honorific where the name carries one
>
> ## What is real and what is written
>
> **Real, read out of `qrme/seed.py`:** name, role, portrait, industry, skills.
>
> **Written:** the careers and the reviews. These are invented experts — the first
> line of that README section says so — and a CV is characterisation of exactly
> the kind the bio already is. Each is drawn from that starter's own bio so the
> two cannot contradict each other.
>
> **Sample values, identical on all 34:** rating, reviews count, memory,
> relationships, engagement. A freshly seeded starter has zero of each, checked
> against a real seed rather than assumed. Thirty-four cards all reading *4.0 · 37
> reviews* is self-evidently a template rather than a measurement, and the README
> says so directly under the gallery.
>
> ## Layout
>
> Card height is derived from content — role lines, chip rows and quote lines —
> not a constant plus a nudge. One collision fixed: the experience boxes leave 6px
> and the `REVIEWS` label's cap-height takes 8, so it was sitting inside the box
> above it.
>
> ## Verification
>
> 622 tests green. Both generators idempotent under `--check`. All 34 cards clear
> their content by exactly 16px, checked programmatically across every file rather
> than eyeballed on one. Gallery measures 358px inside a 390px phone viewport with
> no overflow and no broken images.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #151 — Show each starter as the card the app gives it

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-starter-cards` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/151>

> The starter gallery was a portrait with a name and an industry captioned under
> it. That is a directory listing, not a profile — the app's own **Profile Home**
> (screen 5) gives a starter an avatar bubble, a role, stat tiles and a Chat
> button. Three published versions failed to fix this because each time the
> portrait was adjusted and never the thing around it.
>
> ## Two defects
>
> **It was five columns wide.** Five 118px thumbnails is ~590px of content and a
> phone offers ~390, so on GitHub mobile the fourth column was sliced mid-word and
> the fifth never appeared. Every starter past the third was unreachable to anyone
> reading on a phone.
>
> **Each cell showed two lines of caption**, where the product shows a card.
>
> ## What this does
>
> Each cell is now the Profile Home card itself, generated per starter into
> `docs/portraits/cards/`. Two columns of whole cards fit a phone — verified by
> rendering the real markup at 390px, not by arithmetic.
>
> **The tiles carry facts, not the mock's numbers.** Screen 5 reads *Memory 247 ·
> Relationships 12 · Engagement 92%*. That is fine for one illustrative mock and
> would be a fabrication repeated 34 times here, because nobody has talked to
> these profiles yet. Each card reports the size of the Field Pack grounding it
> and how many skills it is tagged with — both true. The rated starter has no pack
> (there is no adult-industry Field Pack, deliberately) and its card says `None`
> rather than a zero that would read as a failure.
>
> ## Generated, not hand-written
>
> Two tools, both reading `qrme/seed.py` directly, because the old gallery was a
> second hand-maintained copy of the starter list and could drift from it silently:
>
> | | |
> | --- | --- |
> | `tools/starter_cards.py` | renders the 34 cards; fails loudly on a starter with no role line rather than emitting a blank one |
> | `tools/starter_gallery.py` | rewrites the README between markers; `--check` exits 1 on drift |
>
> Roles are curated rather than regex-extracted from the bios — almost right,
> thirty-four times, is worse than a list somebody read once. They use the app's
> own lower-case phrasing (*"retired fee-only financial planner"*).
>
> ## Verification
>
> 622 tests green. Both generators are idempotent (`--check` clean immediately
> after running). All 34 card references resolve, every row has exactly 2 cells,
> and no `portraits/bubbles` reference remains inside the gallery.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #150 — Renumber this release 0.3.1, not 0.4.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-renumber-031` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/150>

> The jump was wrong. 0.2.2 went to 0.3.0 and this round went to 0.4.0, which
> walks through the numbers far faster than the work warrants. **The convention
> from here is to stay in the 0.3.x line and only reach 0.4.0 after 0.3.9.**
>
> ## Why this costs nothing
>
> **No `app-v0.4.0` tag was ever pushed**, in any of the three repositories.
> 0.4.0 existed only as strings in files on `main` — nothing was built, no GitHub
> Release was published, and no installer carries the number. This is a text
> change, not a retraction.
>
> ## What moved
>
> - The five version places: `pyproject.toml`, the `FastAPI(...)` call,
>   `app/package.json`, and the two root entries in `app/package-lock.json`
>   (verified as exactly two changed lines; `@malept/flatpak-bundler` and
>   `asynckit` genuinely are at 0.4.0 and are left alone)
> - `CHANGELOG.md` — the section heading and both link definitions
> - `RELEASE_NOTES.md` — title, body, and the tag it tells you to push
> - `README.md` — the current-release line, plus a row for this release in the
>   table
>
> ## Verification
>
> 622 tests green, 211 routes. No microphone content in the diff.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #149 — Release prep v0.4.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-v040-release` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/149>

> Cuts **v0.4.0** — the starter grounding, the bubble-glow fix, and this round's
> README work.
>
> ## What this release contains
>
> - **Starters arrive knowing something.** All 34 shipped with zero source material
>   while 37 packs sat in the marketplace. Seeding now installs each starter's own
>   industry pack, as part of the repair path so existing deployments catch up by
>   re-running rather than by hand across 34 profiles.
> - **The README says which version you are looking at**, with a release table.
> - **Fixed:** the avatar bubbles had no visible glow — the halo was blurred across
>   most of the margin, so it existed in the source and nowhere a reader would see
>   it.
>
> ## What stays under `[Unreleased]`
>
> The room-microphone entry. Its code is on `main`, but it is not part of a
> described release and these notes must not claim otherwise. `main` being ahead
> of the last tag is the normal state, and recording it that way is more honest
> than either announcing work that is being held or quietly dropping it from a
> section that claims to be complete.
>
> ## Release mechanics
>
> Version moved in all five places: `pyproject.toml`, the `FastAPI(...)` call,
> `app/package.json`, and the **two root entries** in `app/package-lock.json` —
> verified as exactly two changed lines, dependency pins untouched. Changelog
> sectioned, link definition added, `[Unreleased]` repointed at `app-v0.4.0`.
>
> **Do not tag until this is merged**, and tag this commit rather than the tip of
> `main`.
>
> ## Verification
>
> 622 tests green, 211 routes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #148 — Say what version this is, and what each release actually added

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-readme-release-summary` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/148>

> The title said `(v1)` and the only feature section mapped the original PRD
> scope, so a reader could not tell which release they were looking at or what had
> happened since the first one. Thirteen releases of work were described nowhere a
> visitor would find them — the changelog has it all, but the changelog is not
> where somebody lands.
>
> ## What changed
>
> - Title drops `(v1)`; a line at the top names the current release (**v0.3.0**)
>   and the two products cut alongside it.
> - New **What's in the current release** table — thirteen releases, newest first,
>   saying what each one actually added.
> - The old **What's in v1** section keeps its name and position but now says what
>   it is: the PRD conformance map. It answers a different question — which
>   numbered requirement is implemented — not what shipped when.
> - The simulated-money notice moves up with it. Someone deciding whether to trust
>   the marketplace tables should not have to reach `docs/commerce.md` to learn no
>   real funds move.
>
> ## Scope
>
> README only, one file. The table stops at v0.3.0, which is the current release.
>
> ## Verification
>
> Every relative link in the file resolves, and the new table is well-formed
> (13 rows, 2 columns throughout).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #147 — Ground each starter in its own industry pack; fix the bubble glow

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-starter-grounding` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/147>

> ## The specialists knew nothing
>
> `qrme/packs.py` has always described its starter packs as *"one free Field Pack per industry, **matching the Starter Collection**"*. **The pairing was never wired.**
>
> All 34 starters shipped with **zero source material** while 37 packs sat in the marketplace. Dr. Sana Iqbal had an environment persona and no environmental knowledge. Diego Fuentes had a construction persona and no construction material. Every one of them answered from tone alone.
>
> Seeding now installs each starter's own industry pack, and it's part of the **repair** path — so deployments seeded before this catch up by re-running, rather than by hand across 34 profiles.
>
> ## Deliberately narrow
>
> Each limit is a way of not overwriting somebody else's decision:
>
> | Rule | Why |
> | --- | --- |
> | **Only the starter's own industry** | `build_system_prompt` renders `sources[:8]`. A profile that hoards material crowds out its own knowledge — one pack is three items, leaving room to grow |
> | **Only onto a profile with nothing** | An owner who added their own material, or removed the pack on purpose, isn't topped up on the next seed. The same blank-only rule the portrait backfill follows |
> | **Free packs only, no ledger credit** | A deployment grounding its own starters isn't a purchase. A priced pack stays a decision for whoever owns the profile |
> | **The rated starter is left alone** | There's no adult-industry Field Pack, and substituting one would put words in the profile the age wall exists to contain |
>
> Verified end to end: Marcus Bell gets the Personal Finance Field Pack, Dr. Sana Iqbal the Climate & Sustainability Field Pack, and both reach the system prompt.
>
> ## Also: the bubble glow was invisible
>
> The avatar bubble shipped in 0.3.0 got the rounded clip right and then blurred the halo across most of the margin — spreading the light so thin it vanished against a dark page. A glow that existed in the source and nowhere a reader would ever see it.
>
> Narrowed the blur and raised the strength so the README gallery matches the Profile Home screen it's meant to mirror. Checked by rendering against the app's own background in both light and dark, which is the only way this is checkable at all.
>
> ## Verification
>
> - **601 tests**, 12 new. Existing 589 unchanged. 209 routes.
> - **Mutation-checked**: installing over existing material, ignoring the industry match, and auto-installing a priced pack each fail the test that forbids them.
> - Worth noting on the third — **it initially survived**. Every seeded Field Pack is free, so removing the price guard changed nothing observable and the guard was real but unexercised. I added a test that prices one before re-running the mutant.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #146 — Release prep v0.3.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-release-v0.3.0` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/146>

> Cuts **v0.3.0** across all three products. A minor bump rather than a patch — this round added real surface.
>
> ## What's in it
>
> **The round where the tandem reaches a person.** A synthetic specialist could answer a question; now it can be handed a multi-step task, and the person talking to it can be put in front of a real clinician with the release **signed for rather than ticked**.
>
> - **Owner-authorized workflow delegation** (#143) — the workflow routes stay owner-only because a workflow reads vaulted source material unattended and a missing grant means scope `["*"]`. Delegation is a separate surface, off until an owner enables it, and delegating `research` without a grant is refused at write time.
> - **A medical referral, signed for** (#145) — a verified WebAuthn assertion at the `high` tier over the hash of the exact package, bound to that one referral, opening once. Replaces a `consent: true` boolean that was authorising a health conversation leaving the product.
> - **The clinician writes back** (#145) — sealed in the PDI vault, attributed in its own prompt block rather than filed as source material, so the patient doesn't retell everything and the profile doesn't acquire a clinical opinion it can improvise from.
> - **The README gallery renders avatar bubbles** (#144) instead of 34 black boxes.
>
> ## Release mechanics
>
> Version bumped in **all five places** per the checklist:
>
> | | |
> | --- | --- |
> | `pyproject.toml` | ✅ |
> | `FastAPI(...)` in `qrme/api.py` | ✅ |
> | `app/package.json` | ✅ |
> | `app/package-lock.json` top-level | ✅ |
> | `app/package-lock.json` → `packages` → `""` | ✅ |
>
> Dependency versions untouched. `[0.3.0]` link definition added and `[Unreleased]` repointed to `app-v0.3.0` — the step this checklist exists to stop anyone missing.
>
> ## Verification
>
> - **589 tests green**, 40 new this release. **209 routes** (was 197 at 0.2.2). `create_app().version` reads `0.3.0`.
> - All **14** changelog headings checked against their link definitions — 14 for 14.
> - Siblings run in the same pass: jim-mini **346**, pdi **192**.
> - **Nine safety properties are mutation-checked** across this release — each fails the test that forbids it: delegating research without a grant; a delegated caller widening its envelope; an owner's workflow appearing on the delegated routes; a signature raised elsewhere releasing a referral; trusting the stored hash instead of re-hashing; a referral link opening twice; dropping the clinician attribution directive; a clinician writing back repeatedly; one patient's note reaching another's conversation.
>
> ## After merge
>
> The `app-v0.3.0` tag has to be pushed by you — the git proxy here refuses `refs/tags/*`. Body can be left empty or generated; `sync-release-notes.yml` lays `RELEASE_NOTES.md` over the top once the build finishes either way. Watch the case: `app-v0.3.0` lowercase.
>
> Companion PRs: jim-mini `claude/jim-release-v0.3.0`, pdi `claude/pdi-release-v0.3.0`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #145 — Medical referral: signed for, not consented to — and the clinician writes back

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-medical-referral` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/145>

> Reaching a **real clinician** from an AI specialist session, making the release provable, and bringing the answer back so the patient doesn't have to retell it.
>
> ## The thing that was wrong
>
> `POST /handoffs` could already package a session for a real provider. It releases on **`consent: true` — a boolean the client sets.**
>
> Meanwhile `qrme/webauthn.py` opens by describing itself as *"the layer that turns 'the app says the user agreed' into something a third party can check."* The entire signing stack — enrolment, proofing levels, device-bound credentials, envelope challenges, verified evidence packages — has been sitting **one import away** from the single endpoint that ships somebody's health conversation outside the product. A checkbox was authorising it.
>
> ## Going out: signed for
>
> **Signs at the `high` tier.** Document proofing on a device-bound credential — the platform authenticator (Face ID / Touch ID / Optic ID) rather than a passkey that roams. An account without one is *told so*, never quietly dropped to a weaker tier: that would be the checkbox again wearing a signature's name.
>
> **The signature is over the package.** The envelope's challenge *is* the hash of the exact bytes, and `release()` **re-hashes the stored package** at release time.
>
> > Worth flagging: my first draft compared `pkg["document_sha256"]` to the `document_sha256` **column** — two values written in the same breath, which agree no matter what happens to the row afterwards. It proved nothing, and the docstring claiming otherwise was false. The test written for that property caught it. The guarantee exists only because the check now reads the real bytes; the column is kept as a record and the schema says it isn't the check.
>
> **Bound to one referral** (`binding_kind="referral"` — a valid assertion raised elsewhere is not a skeleton key), and **one-time**: the link opens once, and a second attempt says so rather than quietly working, because a replayed link is something the patient should be able to discover.
>
> ## Coming back: caught up, not diagnosed
>
> Opening the link mints a **reply token** at that same moment, so the summary link stays burnt while exactly **one** note can return. Open once, reply once — a channel that needed the summary link kept alive would have traded the handover against the guarantee the patient signed for.
>
> The note is **sealed in the PDI vault** under `qrme/{profile}/clinical/…`: the same treatment source material gets, content in the vault and only a key reference held locally.
>
> **It is deliberately not a `source_items` row**, and that is the decision the rest hangs on. Source material is what a profile recalls *as its own*, and it is what `workflows._scoped_items` feeds to a `research` phase — a clinical opinion filed there could be recited as the profile's own knowledge, or drafted from into a letter. A test asserts it reaches neither.
>
> Instead it arrives in its own prompt block naming the clinician:
>
> > *These are that clinician's words, not yours.* Attribute them by name. You are not a clinician and must never present this as your own assessment, extend it into advice they did not give, or answer a new medical question by reasoning from it — for anything it does not cover, say so and point back to them.
>
> Notes are scoped to **(profile, interactor)**. Another interactor talking to the same profile sees nothing, in the prompt or through the API.
>
> ## Matching
>
> Expertise **filters**, geography only **ranks** — a cardiologist two streets away is not a substitute for a psychiatrist. No match returns nothing rather than a near miss: a confident wrong referral is somebody phoning a clinic that cannot help them. The package names the specialist `synthetic: true` inside itself, since a clinician reading a transcript should never have to work out which voice was a person.
>
> ## Verification
>
> - **573 tests**, 24 new. Existing 549 unchanged. **204 routes** (was 197).
> - **Mutation-checked**, six properties — each fails the test that forbids it: dropping the referral binding; trusting the stored hash; letting the link open twice; dropping the attribution directive; letting the clinician write repeatedly; widening the note query past the interactor.
> - The signing path runs end to end against a real ES256 authenticator double, and the vault path against a PDI double.
>
> Independent of #143 and #144. Companion: jim-mini #97.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #144 — Bake the avatar bubble into the README portraits

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-readme-avatar-bubbles` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/144>

> The starter gallery on GitHub renders **34 hard-edged black boxes** where the app shows rounded avatar bubbles.
>
> ## What was actually wrong
>
> The portraits were loading fine. They're square 512×512 **RGB with no alpha** — corner pixel `(7,7,18)`, a near-black backdrop — and the README embeds them raw.
>
> Inside the product a portrait is never shown that way: `face()` in `docs/screens/build.py` puts it in a rounded box over a soft brand glow with a hairline border, **at render time**. The README can't do that, and the obvious fix doesn't survive — GitHub's markdown sanitiser strips the `style` attribute. On a surface QRME doesn't control, the bubble is in the pixels or it doesn't happen.
>
> That's the same reasoning as `tools/mark_portraits.py`, and the same shape: run once offline, commit the result.
>
> ## Two decisions worth stating
>
> **Derived, never in place.** `tools/bubble_portraits.py` writes to `docs/portraits/bubbles/` and leaves the originals alone. `qrme/assets/portraits/` is what the API serves at `/portraits/{handle}.webp` and what the screens read — and the screens draw their *own* bubble, so baking one into the source would nest a bubble inside a bubble on every app screen.
>
> **Alpha, not a background colour.** The corners and glow margin are transparent, so the gallery sits on whatever theme the reader has. A baked-in dark backdrop would be the black box again by another route, and a grey slab in light mode. Rendered and checked in both.
>
> The rounded clip, glow and border are matched to `face()`'s values so the README and the app agree.
>
> ## On the AI mark
>
> `face()`'s docstring says its radius "stays well inside" the burned-in mark. Strictly that's not true — at radius 0.28 the mark pill's outer corner *is* trimmed. I checked by rendering rather than by reading: **the ✦ AI glyph and text stay fully legible**, because the pill has its own rounded corner and what gets clipped is mostly empty fill. The disclosure survives, which is what matters. Flagging it because the wording overstates the margin.
>
> ## Verification
>
> - **565 tests**, 2 new. Existing 563 unchanged.
> - A portrait with no bubble fails; a bubble that lost its alpha fails. That failure is invisible in the repo and sits on the project's front page, so it shouldn't depend on someone noticing.
> - Gallery rendered at GitHub's own page widths in **both light and dark** before shipping.
> - 34 files, 1.6 MB total (~47 KB each).
>
> Independent of #143 — that branch carries the delegation work and doesn't touch these files.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #143 — Owner-authorized workflow delegation

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/143>

> Lets somebody **other than the owner** start a workflow — how JIM's Guardian hands work to a specialist rather than sending a chat turn.
>
> ## Why not just relax the workflow routes
>
> `qrme/workflows.py` already runs `research → draft → review → send → confirm` in character, carrying memory forward and surviving across sessions. Every route reaching it is `require_owner`. The obvious fix — let an interactor call those routes — is the wrong one.
>
> **A workflow is not a chat turn.** `POST /chat` composes one reply and moderates it. A workflow runs several phases unattended, and its `research` phase reads the profile's **vaulted source material** — where `workflows._scoped_items` treats a missing grant as scope `["*"]`, meaning *all of it*.
>
> A chat turn anyone may start is a considered decision. An unattended multi-phase read over everything the owner ever vaulted, startable by anyone who can reach the endpoint, is not that decision at a larger size — it's a different one.
>
> ## The envelope
>
> Delegation is **off until an owner turns it on**, and turning it on means saying what may be delegated.
>
> | Rule | |
> | --- | --- |
> | No policy → 403 | Absent row, not an empty default. The capability appears only when somebody deliberately asks for it |
> | **A grant is mandatory once `research` is delegable** | Refused at write time (422), where the owner is present to read the error — not at 3am inside somebody else's workflow. This is the one that keeps `["*"]` unreachable down this path |
> | A caller may only ask for a subset | Nobody widens their own envelope |
> | Omitting the plan gets the *owner's* set | Never `DEFAULT_PLAN`, which is every phase there is |
> | Caller must already be in conversation | Checked against `messages`, not `relationships` — those are owner-set, and requiring one would gate every handoff behind an owner action per caller |
>
> `send` **is** delegable, deliberately: the phase produces the finished deliverable, and there is no code path from a workflow phase to an outbound message.
>
> ## The two surfaces never merge
>
> An owner's own workflow has no `delegated_workflows` row, and that absence is the whole guard — it 404s on the delegated routes however the caller authenticates. Only the interactor who started one may read or advance it; the owner can see it, but through the delegated route, not by the two sets of routes converging.
>
> ## New surface
>
> 5 routes (197 → **202**), two new tables (`delegation_policies`, `delegated_workflows` — new tables, not new columns, per the schema convention).
>
> ## Verification
>
> - **563 tests**, 14 new. Existing 549 unchanged.
> - **Mutation-checked** — each of these fails the test that forbids it:
>   - dropping the grant requirement for `research`
>   - letting an omitted plan fall through to `workflows.DEFAULT_PLAN`
>   - exposing an owner's own workflow on the delegated routes
>
> Companion PRs: jim-mini `claude/jim-contribution-preview-and-task-handoff` (the caller), pdi `claude/pdi-tandem-doc-delegated-workflows` (shared doc only).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #142 — Release prep v0.2.2

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/142>

> Cuts **v0.2.2** across all three products. A documentation release — **no code changed**: no new routes, no schema, no behaviour.
>
> ## What's in it
>
> Everything corrects something that was *described* wrongly, which this round turned out to be the thing costing real time.
>
> - **`POST /marketplace/seed` advertised the opposite of what it does.** It still said *"Idempotent — already-seeded profiles are skipped"* after v0.2.1 taught it to **repair** too. That text is served in the OpenAPI docs, so it pointed away from the one call that fixes a deployment showing bare initials instead of portraits. Corrected in four places — the endpoint, `qrme/seed.py`'s module and `seed()` docstrings, and the README's Starter Collection row. (Shipped in #140.)
>
> - **Three releases of changelog link definitions were missing**, and **the release checklist was why**. `docs/releasing.md` step 1 never mentioned them, so the step was skipped by someone following the instructions correctly; step 2 named two version locations when there are five. (Shipped in #141.)
>
> ## Release mechanics
>
> Version bumped in **exactly five places**, per the checklist this round fixed:
>
> | Location | |
> | --- | --- |
> | `pyproject.toml` | ✅ |
> | `FastAPI(...)` in `qrme/api.py` | ✅ |
> | `app/package.json` | ✅ |
> | `app/package-lock.json` top-level `"version"` | ✅ |
> | `app/package-lock.json` → `packages` → `""` | ✅ |
>
> Dependency versions in the lockfile untouched.
>
> ## Verification
>
> - **549 tests green** — the same 549, passing the same way, which is the point of a release claiming no functional change.
> - **197 routes**, also unchanged. `create_app().version` reads `0.2.2`.
> - All **13** changelog headings checked against their link definitions — 13 for 13, including the new `[0.2.2]`. `[Unreleased]` repointed to `app-v0.2.2`.
> - Siblings run in the same pass: jim-mini **312**, pdi **192**, both unchanged.
>
> ## After merge
>
> The `app-v0.2.2` tag has to be pushed by you — the git proxy here refuses `refs/tags/*` writes. Leave the release body empty when you create it; `sync-release-notes.yml` lays `RELEASE_NOTES.md` over the top once the build finishes.
>
> Companion PRs: jim-mini `claude/jim-release-v0.2.2`, pdi `claude/pdi-release-v0.2.2`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #141 — Fix the release checklist that lost three sets of changelog links

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/141>

> Documentation only. No behaviour change — 549 tests pass unchanged.
>
> Follow-up to #140, which repaired the changelog link definitions without touching the reason they went missing.
>
> ## Why three releases in a row lost the same thing
>
> `docs/releasing.md` step 1 said to move the `Unreleased` items under the new heading and date it, and stopped there. It never mentioned the link definition at the bottom of the file — so the step was skipped by somebody following the instructions correctly, three times.
>
> Nothing complains when you miss it. The heading renders fine without a definition, and the damage shows up hundreds of lines away from where the edit was made: a shipped version rendering as literal `[0.2.1]` bracket text, and an `[Unreleased]` link quietly diffing against a tag three releases old.
>
> Step 1 now shows the two lines to add, and says plainly that this is the step that gets missed.
>
> ## Step 2 was wrong in the same direction
>
> It named `pyproject.toml` and `app/package.json`. The version string actually lives in **five** places:
>
> | | |
> | --- | --- |
> | `pyproject.toml` | named already |
> | `app/package.json` | named already |
> | the `FastAPI(...)` call in `qrme/api.py` | **omitted** |
> | `app/package-lock.json` top-level `"version"` | **omitted** |
> | `app/package-lock.json` → `packages` → `""` → `"version"` | **omitted** |
>
> Those three had to be rediscovered every round. The step now names all five and warns off the dependency pins in the lockfile, which look identical to the two that matter.
>
> ## Across the three repos
>
> The same correction goes to jim-mini and pdi, whose link definitions had drifted identically — all three stopped at `0.1.8`. Companion PRs:
>
> - jim-mini — `claude/jim-changelog-release-links`
> - pdi — `claude/pdi-changelog-release-links`
>
> ## Verification
>
> `QRME_STUDIO_DIR=/nonexistent python3 -m pytest -q` → **549 passed**. The sibling suites were run in the same pass: jim-mini **312**, pdi **192**, both unchanged.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #140 — Correct the seed endpoint's idempotency description

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/140>

> Documentation only. No behaviour change — 549 tests pass unchanged.
>
> ## The problem
>
> `POST /marketplace/seed` still advertised itself as *"Idempotent — already-seeded profiles are skipped"*. Since v0.2.1 that is only half the story: the endpoint also **repairs**, filling a missing portrait or appearance on a starter that already exists.
>
> The stale sentence was load-bearing in the wrong direction. It is the text served in the OpenAPI docs — which is where somebody deciding whether a call is safe to make actually reads — so a person staring at three starters rendering as bare initials would read that line and conclude the one call that fixes them cannot possibly help. Skipping is precisely what they do not want.
>
> ## What changed
>
> The claim was wrong in **four** places, not the one I first spotted:
>
> | Where | Why it matters |
> | --- | --- |
> | `qrme/routers/community.py` — the endpoint docstring | Served in the OpenAPI docs; the one most people read |
> | `qrme/seed.py` — module docstring | What you get from `help(qrme.seed)` and the source |
> | `qrme/seed.py` — `seed()`'s docstring | Did not mention the `repaired` count it now returns |
> | `README.md` — Starter Collection row | The description a new deployment reads first |
>
> All four now say idempotent **and** repairing, note that the repair is blank-only (anything an owner set is left alone), and mention `repaired` alongside `created` and `skipped` in the response.
>
> ## Also fixed
>
> The changelog's link definitions stopped at `0.1.8`. `[0.1.9]`, `[0.2.0]` and `[0.2.1]` had headings but no link definition, so three shipped versions rendered as literal `[0.2.1]` bracket text rather than links to their releases — and `[Unreleased]` still compared against `app-v0.1.8`, presenting a three-release diff as if it were an empty one.
>
> ## Verification
>
> - `QRME_STUDIO_DIR=/nonexistent python3 -m pytest -q` → **549 passed**, the same 549.
> - Rendered the OpenAPI description directly from `create_app().openapi()` to confirm the new text reaches the docs page intact.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #139 — Release prep v0.2.1

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-v0.2.1` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/139>

> Version strings in the five places, changelog cut, release notes rewritten. All three products cut together at this version.
>
> ## What this release carries
>
> - **A profile front page** — skills, experience, reviews, rating, in one call. A review requires a real interaction on record and `UNIQUE (profile_id, author_id)` makes a second one from an account impossible in the schema; experience about a real person needs the same rights basis the persona did.
> - **A help box on every screen**, structurally not a synthetic profile — no name, no face, no memory, and it refuses to be one before any model sees the question.
> - **Real portraits** where Profile Home, Avatar Studio and Live Video drew a generic orb, in rounded boxes so the AI mark burned into the top-right corner survives.
> - **Screen 80**, the front page a visitor sees as opposed to the owner's view.
> - **The seed repair** that puts a face back on a starter created before the portraits shipped — the fix for the `MB` / `OM` / `DS` initials.
>
> ## Verification
>
> **549 tests green. 197 routes. 169 SVGs parse**, and all 160 rendered screens carry the help affordance. Both front-ends build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #138 — Real faces on the screens, and a front page behind them

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-portrait-backfill` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/138>

> Three things, all the same complaint: the profiles showed a hologram, and there was nothing behind the face to show anyway.
>
> ## 1. The initials were a bug, not a rendering problem
>
> `MB` / `OM` / `DS` are Marcus Bell, Otis Marsh and Dr. Sana Iqbal — all three ship with real portrait files. Those profiles were created **before** the portraits existed, and nothing could put them back: the seed is idempotent by @handle, and idempotent meant `continue`. So the obvious repair — re-run the seed — was exactly the thing that couldn't work.
>
> It backfills now, **blank-only**, so it's a repair and not a reset. On a live deployment: `POST /marketplace/seed`.
>
> ```
> first run :  created 34, skipped  0, repaired 0
> second run:  created  0, skipped 34, repaired 3   ← the three from the report
> ```
>
> ## 2. The screens drew a hologram where a face belongs
>
> Profile Home, Avatar Studio and Live Video drew `orb()` — a purple sphere with a generic person glyph. **The pixels were already in the repo**: all 34 starter portraits ride in `frames.PORTRAITS`, and exactly one screen used them.
>
> **A rounded box rather than a circle, and not only for taste.** `tools/mark_portraits.py` burns the AI mark into the pixels at the **top-right** — so a circular clip of a square portrait cuts off the corner the disclosure lives in. The radius stays well inside it, so the mark survives into every screen showing a face, which is the whole reason it was burned in rather than composited. Verified by rendering and looking at it.
>
> Those screens now name the character and their profession — *Marcus Bell · retired fee-only financial planner* — both sourced from `seed.py` so the face and the name cannot drift apart. "AI assistant" stays where it belongs: the chrome that genuinely cannot know who is loaded.
>
> ## 3. A profile now has a front page
>
> `qrme/frontpage.py` — skills, experience, reviews, rating, and how many people have actually talked to it, in **one call**, because the caller is a scan page on cellular and five round trips is how a page arrives in pieces.
>
> | | |
> |---|---|
> | `GET /profiles/{id}/front` | the whole page |
> | `PUT /profiles/{id}/experience` | owner-only, replaced wholesale |
> | `GET`/`POST /profiles/{id}/reviews` | one per person, edited not stacked |
>
> **A review comes from somebody who was actually there.** It checks the `engagement` row for a real interaction, and `UNIQUE (profile_id, author_id)` makes a second review from one account impossible *in the schema* rather than in a check somebody could forget. Without both, a rating is worth exactly the number of accounts somebody can make. The average always reports its own `count` — one five-star review and two hundred are different facts.
>
> **Experience about a real person is a credential.** On a `fictional` profile invented history is the point and the AI mark says so. On one depicting somebody real, *"twenty years at Accra General"* is a claim asserted on their behalf, so it's refused without the same rights basis the persona needed.
>
> **Nothing on the page outranks the mark.** A five-star average is a well-liked synthetic profile and nothing more. Reviews are moderated on the way in; a blocked one is kept, shown to its author with the reason, invisible to everyone else, and excluded from the average.
>
> The headline is **derived from the persona** rather than stored — a separate field is a second copy that starts agreeing with it and stops.
>
> ## Verification
>
> **538 tests green (15 new). 195 routes. 167 SVGs parse.** Mutation-checked four ways: restoring the seed's bare `continue`, dropping the "was actually there" check, and dropping the rights-basis check each fail the test that forbids them.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #137 — The assistant has no name any more

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-unname-the-assistant` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/137>

> "Ava" was a sample profile name that had quietly become the product's mascot:
>
> | where | said |
> |---|---|
> | studio nav | *Chat with Ava* |
> | chat bubble CSS | `.bubble.ava` |
> | screen gallery | *People in Ava's life*, *Ava wants to reply*, *Talked with Ava* |
> | desktop frames | *Ava · Online*, *Ava · AI Version Me* |
> | demo handle | `@ava.bianchi` |
> | onboarding | `useState("Ava")` |
>
> None of that is true of the product. **A QRME profile is named by whoever creates it**, so hardcoding one name in the chrome told every user their assistant was somebody else's.
>
> The chat screen was already right — it reads `session.profile.display_name`. The name only ever lived in the parts that *could not* know it.
>
> ## Now
>
> Everything that cannot know the name says **AI assistant**, and the message role is `assistant` rather than `ava` — which is what it always was.
>
> **Onboarding no longer pre-fills the name.** A default sitting in the box is the one most people never change, which is exactly how a sample name becomes a mascot. It's empty now, with *"Name your assistant"* as placeholder text.
>
> Screen 6 is `06-chat.svg` rather than `06-chat-with-ava.svg`, and the README gallery follows.
>
> ## Found by rendering, not by reading the diff
>
> The chat screen's online dot sat at a **fixed x that assumed a three-letter name** — so "AI assistant" ran straight through it. The dot and its label are measured off the label now, so a longer name cannot overwrite the status.
>
> Four strings also read badly once the name came out (*"Talked with it"*, *"People in its life"*), and were reworded rather than left as mechanical substitutions.
>
> ## Also
>
> Test fixtures that typed `"Ava"` as a `display_name` are `"Test Profile"` now. The name was perfectly fine as user input — but leaving it made the grep lie.
>
> ## Verification
>
> **523 tests green. 167 SVGs parse. The studio builds clean.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #136 — Release prep v0.2.0

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-v0.2.0` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/136>

> **No functional changes to QRME in this release.** The round was next door, where PDI grew a per-tenant on-call roster. The three products version as one, so this repo cuts the same number in the same pass — `docs/releasing.md` says an empty round says so plainly rather than padding.
>
> ## Why 0.2.0 rather than 0.1.10
>
> The 0.1.x line ran from a profile you could talk to, to a suite where all three products put printed codes on physical things and answer a stranger's phone with a **page rather than JSON** — desk beacons, care beacons, custody beacons, an agent at a facility gate that can speak but cannot decide, a marketplace searchable in words, and an escalation path in each product that reaches an actual human.
>
> That is a different product from 0.1.0. 0.1.10 would have undersold it.
>
> ## What is in here
>
> Version strings in the five places, changelog cut, release notes rewritten — plus the workflow race fix that merged earlier today, which is the only functional change this repo carries into 0.2.0.
>
> ## Verification
>
> **523 tests green** — the same 523, passing the same way, which is rather the point of a release claiming no functional change here. 192 routes. Both front-ends build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #135 — Only one workflow writes the release body now

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-release-body-race` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/135>

> Two of them did.
>
> `desktop-release.yml` published the release with `body_path: RELEASE_NOTES.md` — the file **verbatim**, *"Ready-to-paste body for the GitHub Release…"* preamble and all — while `sync-release-notes.yml` published the same file with that preamble stripped. Both fired on the same tag push.
>
> ```
> 20:50:09  both workflows start
> 20:50:15  sync-release-notes  → correct body   ✓
> 20:52:43  desktop-release     → raw file       ✗ overwrites it
> ```
>
> The build always won. Every release since the sync workflow existed has shipped the maintainer preamble at the top of its notes until somebody re-ran the sync by hand — v0.1.9 included, in all three repos.
>
> The de-duplication logic already sitting in the sync workflow — *"several releases carry it twice from a body that was pasted over one that already had it"* — turns out to be scar tissue from this. It was treating the symptom of a race nobody had spotted as a race.
>
> ## Fixed at both ends
>
> **The build stops writing a body.** It attaches installers and lets GitHub generate the changelog. That alone removes the second writer.
>
> **The sync stops racing.** It now triggers on `workflow_run` when the build **completes**, rather than on the tag push, so the curated notes are the last write by construction rather than by luck:
>
> ```yaml
> workflow_run:
>   workflows: ["Desktop release"]
>   types: [completed]
> ```
>
> The tag comes from `workflow_run.head_branch`, and the job is guarded so the manual artifact-only builds — which publish no release — don't trigger a pointless sync.
>
> `types: [completed]` rather than success-only is deliberate: a build that fails *after* creating the release is exactly when a wrong body is least likely to be noticed.
>
> ## Also
>
> [docs/releasing.md](docs/releasing.md) now says to leave the release body empty when tagging, records which workflow owns it, and names the other trap in the same area — tag names are case-sensitive to `tags: ["app-v*"]`, so `App-v0.1.9` silently triggers nothing at all.
>
> ## Verification
>
> Both workflow files parse as YAML, and the `workflows:` name is checked against each repo's actual `name:` — they differ per repo (`Desktop release` / `Guardian release` / `Console release`), which is the kind of thing that would have failed silently.
>
> **523 tests green.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #134 — tandem.md: JIM's test count

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-tandem-counts` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/134>

> One line. `docs/tandem.md` cites each repo's suite size, and JIM's moved from 293 to 297 in [jim-mini#88](https://github.com/davidsbianchi1984/jim-mini/pull/88) — a guard against an unreadable `JIM_SITE_ROTA` taking down its escalation path.
>
> Keeping the three copies byte-identical is the property this file is supposed to have, and letting it drift by one number is how the counts got to *"QRME 59, JIM 49, PDI 20"* in the first place.
>
> No functional change. **523 tests green.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #133 — The tandem doc describes the architecture that exists, and v0.1.9

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/133>

> `docs/tandem.md` is the document every README points a new reader at, and it had drifted in three ways at once.
>
> ## It was missing an arrow
>
> For most of this project's life the topology fit in one sentence: **every arrow points into PDI**, because PDI is the bottom layer and a vault whose availability depends on a model provider is a worse vault.
>
> PDI's gate agent broke that on purpose — it asks a QRME profile for the words it speaks to somebody standing at a facility door. The document, the ASCII diagram and the section headings all still described the world before it. `pdi/qrme_client.py`'s own docstring cites *"every arrow in docs/tandem.md points into PDI"* while being the thing that made it false.
>
> There is a `pdi ✕ qrme` section now: the flow, the fallbacks, and why the model is the voice and not the decider.
>
> ## Two of the three copies were a release behind
>
> JIM's and PDI's still listed the suite gateway's erase, export, consent and metering as `[planned]` when `suite/gateway.py` had shipped them, and the docker-compose e2e harness as planned when it runs in CI. A reader in either repo was told cross-app deletion did not exist.
>
> The three copies are byte-identical again.
>
> ## The numbers were wrong
>
> *"QRME 59, JIM 49, PDI 20 tests"* — against suites of **523, 293 and 177**.
>
> ## New sections
>
> - **The beacon family.** Three products now put a printed code on a physical thing and answer three different questions with it. The shared rules were true in three places and written down in none: a scan is a page and not JSON; a dead code and a code that never existed render identically; the page renders only what the server handed it, so it cannot disclose what the card withheld.
> - **Reaching a human** — the one thing the suite genuinely cannot supply for itself, and the subject of this round's work in the siblings.
>
> ## The diagram is generated
>
> `tools/build_assets.py` writes `docs/diagrams/tandem-flow.svg` from a block identical in all three repos, so one picture cannot become three that disagree. It replaces a hand-drawn SVG that was cream-and-serif while every other asset in every repo is night-indigo — and that showed two arrows, because it was drawn when there were two.
>
> Rendered in a browser and checked for collisions rather than trusted to parse.
>
> ## Also
>
> The Starter Collection row said *33 fictional profiles* while the README, the avatars doc and the generated cover said 34. Both were right — `@vivienne_sable` seeds the rated tier from `RATED` rather than `STARTERS` — and reading them together still looked like a contradiction. Named.
>
> ## Release prep v0.1.9
>
> Version strings in the five places (`pyproject.toml`, the FastAPI app, `app/package.json`, the two root entries in its lockfile), changelog cut, release notes rewritten. All three products cut together at this version, per `docs/releasing.md`.
>
> ## Verification
>
> **523 tests green. 192 routes.** All three `docs/tandem.md` and `docs/diagrams/tandem-flow.svg` verified byte-identical across the three repositories.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #132 — Marketplace search: words, place, and a hand with the words

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-marketplace-search` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/132>

> ## Why
>
> Browsing meant knowing the vocabulary — exact `kind`, exact `tag`, exact `area`. Fine if you already know the tag is `legal`; useless if what you have is *"someone who can help me read a lease."*
>
> `qrme/marketplace.py` adds free-text search, a place, saved settings, and an assistant that helps somebody name what they want. 8 routes, 23 tests, [docs/marketplace.md](https://github.com/davidsbianchi1984/qrme/blob/claude/qrme-marketplace-search/docs/marketplace.md).
>
> ## Place is not `area`
>
> `listings.area` was **already taken** and means a *subject* area — healthcare, finance, legal. So geography went into its own table. Folding them together would have made *"near me"* quietly mean *"in healthcare"* — which looks like an empty marketplace and is very hard to see.
>
> **Nothing is sniffed.** No IP geolocation, no GPS, no address parsing. A seller types where they serve; a searcher types where they are. Location a user did not enter is location they did not agree to share.
>
> Localities are **names, not points** — there is no distance maths. That's a real limitation (no "within 10 miles") and also the reason there is nothing to leak. `GET /marketplace/localities` lists what actually exists, so a searcher picks rather than typing a spelling nothing matches and concluding the place is empty.
>
> ## A rated listing can never carry a place
>
> `set_place` **refuses** one — so no row is written, so no place filter can match it, even for a verified adult.
>
> That's [desks.md](https://github.com/davidsbianchi1984/qrme/blob/main/docs/desks.md)'s line — *where a performer physically is has nothing to do with browsing them, and a place filter is a way of asking* — made **structural** rather than a check the next filter to be added could forget. The refusal is loud, because an operator who thinks they've set a location needs to know they haven't.
>
> ## Ranking is deterministic, and says why
>
> Field-weighted (title 6, tags 4, provider 3, blurb 2, area 1), prefix-matched so *nutrition* finds *nutritionist*. Every result carries `score` and `matched_on`; `hidden_by_place` is reported rather than swallowed.
>
> Two callers passing the same arguments get the same order — which is what makes *"why am I seeing this?"* answerable without trusting anybody.
>
> ## The assistant writes the box and stops
>
> `POST /marketplace/assist` turns *"I don't know what to search for"* into two or three candidate searches. It returns **suggestions and never results**, and there is deliberately **no code path from it into `search()`**.
>
> Same boundary as PDI's gate agent: a model can change what is in your search box and nothing else. It cannot filter, reorder, or decide what you're shown — so everyone gets the same explainable ranking. A marketplace where a model silently re-ranks is one where nobody, including the operator, can say why you saw what you saw.
>
> Falls back to keywords from the need itself when no provider is reachable, so nobody is stuck behind an outage.
>
> ## Two bugs worth naming
>
> **Caught by a test, not by reading:** `search_with_prefs` used `setdefault` to apply saved settings — but the route passes *every* query parameter, so an unset one arrives as an explicit `None` and the key already exists. Saved settings were never being applied at all.
>
> **Caught by rendering and looking:** `build.py`'s `button()` fell through to `ghost` for any kind it didn't recognise, so a screen's primary action silently lost its fill. Valid SVG either way, which is exactly why only the generator can catch it — it now raises on an unknown kind.
>
> ## Changes
>
> | | |
> |---|---|
> | `qrme/marketplace.py` | new |
> | `qrme/db.py` | `listing_places`, `marketplace_prefs` |
> | `qrme/routers/community.py`, `qrme/models.py` | 8 routes + schemas |
> | `tests/test_marketplace_search.py` | 23 tests |
> | `docs/screens/` | screens 77–79, + the `button()` guard |
> | `docs/marketplace.md`, `README.md`, `CHANGELOG.md` | |
>
> ## Verification
>
> **523 tests green** (was 500). 192 API paths. 195 SVGs parse; every README image reference resolves. All three new screens rendered to PNG and inspected on both platforms.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #131 — Generate the README cover instead of hand-building it

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-generated-cover` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/131>

> ## Why
>
> The cover at the top of the README was a hand-built one-off, and it had aged the way hand-built one-offs do. It was drawn **before** live desks, desk beacons, the audience layer, the marketplace, gifts and the burned-in AI mark existed — so it was still advertising the 0.1.0 product four releases later.
>
> It was also off-palette: **amber on navy**, while every screen in `docs/screens/` is night-indigo with neon purple. The cover and the screenshots beneath it did not look like the same product.
>
> ## What changed
>
> `tools/build_assets.py` generates it, from the same palette constants the screens use — for the same reason those are generated: *a picture of the product that cannot be regenerated is a picture that will be wrong soon, and nobody will notice.* Dependency-free, stdlib only, like the screen builders.
>
> The new cover **names what shipped** rather than implying it — 34 starter profiles, live desks, desk beacons, the audience layer, the marketplace, gifts — and the AI mark rides on the portrait in the illustration too, because that is the whole point of burning it into the pixels.
>
> ## Verified by looking, not by parsing
>
> Two composition defects the "it parses" check would never have caught:
>
> 1. the dotted orbit ring ran straight through the tagline, and the right third was empty
> 2. the relationship connectors came out as a flat fan of straight lines
>
> Both fixed and re-rendered.
>
> ## The sixteen files I did *not* touch
>
> `assets/design/01-*` through `16-*` are unchanged and deliberately so — **no README or doc references any of them**, so they are an orphaned illustration library rather than something going stale in public. Worth stating out loud so the gap reads as a decision rather than an oversight. Say the word if you'd like them folded into the generator too.
>
> ## Verification
>
> 189 SVGs parse; every README image reference resolves on disk. No application code touched, so the suite is unaffected (500 tests, unchanged).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #130 — sync-release-notes: read the tag's notes, and stop duplicating What's Changed

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/130>

> ## Why
>
> Ported from [pdi#63](https://github.com/davidsbianchi1984/pdi/pull/63), where two defects in this workflow surfaced while repairing a release body that a stray paste had overwritten. The file was **byte-identical across all three repos**, so both defects are here too.
>
> ## The defects
>
> **1. It read the wrong file.** `actions/checkout@v4` had no `ref`, so it checked out the default branch — where `RELEASE_NOTES.md` always holds the *newest* version's notes. Syncing a tag push was correct by accident (the tag is the tip). Repairing anything older was actively wrong: it would publish the current version's notes onto an old release — the same failure this workflow exists to prevent, arriving by a different route. It now checks out the tag it is syncing.
>
> **2. It discarded the PR list.** `gh release edit --notes-file` replaces the whole body, so every sync silently dropped the auto-generated *What's Changed* section. It's now read off the release first and re-appended — and **de-duplicated on the way past**, since `app-v0.1.3` here carries that block twice, from a body pasted over one that already had it.
>
> ## State of this repo's releases
>
> Checked while investigating: **qrme's `app-v0.1.8` body is correct.** The stray paste took QRME's v0.1.8 notes and put them on *PDI's* `app-v0.1.4` — nothing here was overwritten. The only defect found in this repo is the duplicated *What's Changed* on `app-v0.1.3`.
>
> ## Note on the preamble
>
> The workflow already stripped the *"Ready-to-paste body for the GitHub Release… Kept in sync with CHANGELOG.md"* line — a maintainer instruction that reads oddly to somebody who came for an installer. It survives on releases only because they were pasted by hand rather than synced. Any release this runs against loses it.
>
> ## Verification
>
> No application code touched — workflow only, so the suite is unaffected (500 tests, unchanged). The rebuild logic was tested against the real tags in the PDI PR before being ported here.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #129 — Release prep v0.1.8: version bumps, changelog cut, release notes

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-release-v0.1.8` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/129>

> **Unlike 0.1.7, this is a real feature release** rather than a coordinated number. Since the v0.1.7 tag this repo gained:
>
> | | |
> |---|---|
> | code | **458 insertions** across `qrme/` and `tests/` |
> | API routes | **182 → 187** |
> | schema | new `desk_guests` table |
>
> Someone running 0.1.7 cannot come up on a stream. That's a feature release.
>
> ## The gap I closed first
>
> **`[Unreleased]` was empty**, and it shouldn't have been. The live-room round landed *after* 0.1.7 was cut and never got a changelog entry. Cutting 0.1.8 straight away would have published release notes that didn't mention the only thing in the release. So this writes the entry, then cuts it.
>
> ## What's in the diff
>
> - **Versions to 0.1.8** — `pyproject.toml`, the FastAPI app, `app/` and `launcher/` `package.json`, and the two root entries in each lockfile. Dependency versions untouched; the lockfile edits are pinned to lines 3 and 9 by assertion.
> - **CHANGELOG** gains `[0.1.8] — 2026-07-25`: the two join modes and their gates, the overlay endpoint, eight new mobile screens and three desktop views, the real camera frames, the starter portraits made visible, and the changelog-anchor repair.
> - **RELEASE_NOTES.md** rewritten for v0.1.8.
>
> The notes keep the simulated-money limits at the same volume as the features, as the last two releases did — a note listing gifting and purchase without listing the *absent* spend controls reads as a payments product.
>
> ## Verification
>
> 500 tests green. 187 routes. FastAPI reports `0.1.8`, and no `0.1.7` string survives in any version site.
>
> ## After merge
>
> The `app-v0.1.8` tag goes on **this** commit. That matters more this time than last: `main` had already drifted five commits past the 0.1.7 tag point before this release was cut.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #128 — Show the faces on the Starter Collection screen

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-portrait-grid` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/128>

> You asked whether I'd put the holographic avatars into the screens. **The answer was no**, and you were right to check.
>
> The portraits went into the README and `docs/avatars.md` galleries, and the live landing page has rendered them since 0.1.6 — but **no screen ever showed one**. Screen 74 said *"seeded with faces"* and then drew icon chips, which is the one thing a screen about portraits must not do.
>
> ## What changed
>
> All 34 now appear as a five-column grid, in `seed.py`'s own order, embedded as base64 — same technique as the desk frames and for the same reason: an SVG rendered through an `<img>` tag can't fetch external files, so a relative path renders as an empty box. 114px square, ~4 KB each, 126 KB for the set.
>
> **The grid carries no badge of its own**, and doesn't need one. Every portrait has the AI mark burned into its own pixels by `tools/mark_portraits.py`, and it stays legible at thumbnail size — which is exactly the property that made burning it in worth doing rather than drawing it at render time. You can see the badge on all 34 in the grid.
>
> Seven rows of faces leave about 95px above the tab bar, so the screen went from five cards and a button to one card and none. The grid *is* the screen.
>
> ## One detail in the encoder
>
> It reads the roster from `seed.py` rather than listing the directory. So the grid is the collection in its own order — and a portrait added without a starter, or a starter added without a portrait, **fails the build** instead of producing a silently short grid.
>
> ## On your screenshot
>
> `landing_starters.png` isn't generated by anything in the repo — it's a stale preview from before the portraits shipped. I seeded a fresh deployment and confirmed the landing page emits ``'&lt;img src="/portraits/marcus_bell.webp"&gt;'``, not "MB". The initials path in `landing.py` still exists, but only fires for a profile with no portrait at all.
>
> ## Verification
>
> 34 starters, 34 grid entries, same order, **34 distinct images** (checked by digest, so a copy-paste repeat would have shown up). 172 SVGs parse, 500 tests green, and I rendered the screen and looked at it.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #127 — Put the real camera frames into the live-stream screens

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-desk-frames` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/127>

> The desk screens described a camera view and showed nothing. The photos were already in the repo — `desk_view.webp` (the office, *RING BELL FOR SERVICE — AWAY FROM THE DESK*) and `stage_view.webp` (*BE BACK SOON OR RING BELL*) — and those signs are the whole feature. They're the situation the bell was built for, and what a visitor is actually looking at while they wait.
>
> ## Embedded, not linked
>
> An SVG rendered through an `<img>` tag — which is how GitHub shows one in a README — **cannot fetch external files**, so a relative path to the `.webp` would have rendered as an empty box.
>
> So the pixels ride inside the SVG as a base64 JPEG. The encoding lives in `docs/screens/frames.py`, generated once by `tools/encode_desk_frames.py`, which keeps `build.py`'s property of importing nothing outside the standard library — nobody needs Pillow to regenerate the galleries.
>
> | screen | frame | tag |
> |---|---|---|
> | 69 Live Desks | desk | `SAMPLE VIEW` — matches the API's `live: false` when no camera is configured |
> | 75 Live Room | desk | `LIVE` · "Bev is away — ring the bell" |
> | 76 Rated Stream *(new)* | stage | `LIVE` · same bell, behind the adult gate, location withheld |
> | desktop 07 | desk | in the live-room panel |
>
> **None carry an AI watermark.** These are photographs of real rooms belonging to real people; marking one would be a false statement about both the room and the person about to walk back into it.
>
> ## Two defects I only found by rasterising the output
>
> Both would have shipped if I'd stopped at "the SVG parses":
>
> **Text overflowed the cards.** `card_block` does no clipping — a long subtitle just runs off the edge. Mine reached 58 characters where the pre-existing screens top out at 46. I measured the real budget from the layout constants (`CW` is 252; a title beside a `HUMAN` pill gets ~139px) and cut every string to fit: **17 chars beside a pill, 24 without, 42 for the photo caption.**
>
> **The bell emoji rendered as tofu** wherever no emoji font is installed. Removed — the icon chip beside it already said the same thing.
>
> ## Verification
>
> 172 SVGs parse. 76 mobile screens and 9 desktop views on disk, the same in the README, every reference resolves. 486 tests green. I rendered 69, 75, 76 and desktop 07 to PNG and looked at them.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #126 — Show the starter collection in the README

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-starter-gallery` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/126>

> You're right — the README already said *"All 34 starters ship **with** their portrait"* and then showed none of them. Screen 74 depicts the collection as a UI mockup, which is a different thing from seeing the faces.
>
> ## What changed
>
> All 34 now appear as a gallery — 33 invented experts, one per industry, plus Vivienne Sable, the one rated profile — placed directly under the sentence that claims they exist.
>
> 7 rows of 5, each cell showing the portrait, the name, and the industry.
>
> ## Why this is safe to publish
>
> Worth stating rather than assuming. **The AI mark is burned into each portrait's own pixels** by `tools/mark_portraits.py` — it isn't drawn by a client at render time. So it survives a screenshot, a hotlink, or a crop, and these images carry their disclosure into the README itself.
>
> That's exactly the property the marking pass was built for. A gallery of *unmarked* synthetic faces on a public page would have been precisely the failure that feature exists to prevent. Verified with `--check`: 34 portraits match the manifest.
>
> I also **looked at the rated profile's portrait** rather than trusting the label before putting it on a public page. It's a dressing-room scene, fully clothed, nothing explicit, and the caption labels it `adult · 18+`.
>
> ## Verification
>
> - 34 handles map to 34 files, no orphans in either direction
> - Every image reference in the README resolves
> - 486 tests green
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #125 — Screens for the capabilities 0.1.6 and 0.1.7 added

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-screens-v0.1.7` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/125>

> ## What I found first
>
> Nothing was stale. Every screen on disk was already in the README gallery, every referenced image resolved, and `build.py` regenerated all 136 existing files **byte-identical**.
>
> The gap was coverage: **five capabilities shipped across 0.1.6 and 0.1.7 with no screen at all.** `17-summon-beacons` covers *profile* beacons — the opposite case from a desk beacon — so it was doing no work for the new feature.
>
> ## Five new screens, 69–73
>
> Both platforms, in the existing declarative card idiom:
>
> | # | screen | what it shows |
> |---|---|---|
> | 69 | Live Desks | the empty chair, the attestation, the bell |
> | 70 | Desk Beacons | the sticker on the shop door, the 30s anonymous cooldown, the age wall a tokenless scan always hits |
> | 71 | Audience | likes as facts not counters, moderated comments, shares gated at the destination, both subscription tiers |
> | 72 | Gifts & Purchases | the shop-window/offer distinction, and a `SIMULATED` pill |
> | 73 | Signatures | the document shown *before* the prompt |
>
> ## The one I checked rather than assumed
>
> **Screens 69 and 70 carry no AI mark**, deliberately — a desk is an actual person, so the badge makes the positive claim (*Live person — not AI*) instead of the disclosure every synthetic profile carries.
>
> I verified that against the rendered SVG rather than trusting the template: the only occurrences of "AI" in `69-live-desks.svg` are the two lines that *deny* it. Getting that wrong in the artwork would contradict the invariant the API enforces.
>
> Screen 72 gets the same treatment for money — the `SIMULATED` pill means the screen says what the API says, rather than implying a payment processor that doesn't exist.
>
> ## JIM-mini and PDI need nothing
>
> Checked both rather than assuming. Each regenerates byte-identical, every README reference resolves (jim's apparent 59th reference is an Android variant that exists), and neither had a functional change this round. Adding screens there would be inventing coverage for features that didn't move.
>
> ## Verification
>
> 146 SVGs parse as XML, 0 malformed. 73 screens on disk, 73 referenced in the README, no dangling references in either direction. 486 tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #124 — Point the untagged versions at commits, not missing releases

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-changelog-anchors` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/124>

> v0.1.5 and v0.1.6 were released — changelog, notes, version bumps — but their `app-v*` tags were never pushed, so no GitHub Release exists for either and the CHANGELOG entries linked to two 404s.
>
> ## The fix
>
> Those two entries now point at their **release-prep commits** (`13338e6`, `db6d7c9`). The link then means "here is what that version was", which is what someone following it actually wants, and it resolves.
>
> `[0.1.4]` and below keep their release-tag links, because those releases are real. `[0.1.7]` keeps its tag link, because that tag is about to be pushed.
>
> ## Why not just backfill the tags
>
> I considered it and decided against it. Pushing `app-v0.1.5` and `app-v0.1.6` now would fire `desktop-release.yml`, build installers on real macOS/Windows/Linux runners, and publish two Releases **dated after v0.1.7** — putting superseded installers at the top of the page people download from. That's a worse outcome than the dead links were.
>
> `docs/releasing.md` records that reasoning, because an unexplained gap in a tag sequence is exactly the sort of thing someone finds later and "fixes" without knowing why it was left.
>
> ## Scope
>
> Docs only — no code, no version change, no new release.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #123 — Release prep v0.1.7: version bumps, changelog cut, release notes

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-release-v0.1.7` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/123>

> The first release cut under the rule written down last round: **the three products ship as one**, same number, same pass. QRME carries this round's substance; JIM-mini ([#78](https://github.com/davidsbianchi1984/jim-mini/pull/78)) and PDI ([#59](https://github.com/davidsbianchi1984/pdi/pull/59)) cut alongside with documentation-only changes and say so plainly.
>
> v0.1.6 was about telling the truth in both directions. This one is about a profile being more than something you talk to: you can like it, comment on it, share it, subscribe to it, gift the person behind it, and buy what they're selling — and a live desk can be left on a door as a printed code, the way a synthetic profile already could.
>
> ## What's in the diff
>
> - **Versions to 0.1.7** — `pyproject.toml`, the FastAPI app, `app/` and `launcher/` `package.json`, and the two root entries in each lockfile. Dependency versions untouched: the lockfile edits are pinned to lines 3 and 9 by an assertion, not a blind replace.
> - **CHANGELOG** cuts `[0.1.7] — 2026-07-25` from Unreleased, with the anchors.
> - **RELEASE_NOTES.md** rewritten for v0.1.7.
>
> ## Two things I want to flag
>
> **The release notes keep the money limits at the same volume as the features.** A note that lists gifting and marketplace purchase without listing the *absent* spend controls — no running totals, no cooling-off, no parental controls, no real identity check behind "verified adult", no chargebacks, no payout compliance — is the kind that gets read as a payments product. It isn't one, and the notes say so.
>
> **This also fixes a section boundary I got wrong last round.** The `### Changed` heading for the release-convention entry was inserted mid-list, which left the Windows-signing and `portrait_marked` entries — both genuinely *additions* — sitting under Changed. The heading now sits after them, so `### Added` holds all five feature entries.
>
> ## Verification
>
> 486 tests green. FastAPI reports `0.1.7`, and no `0.1.6` string survives in any version site. JIM-mini (240) and PDI (134) both verified unchanged, which is the point of a release claiming to change nothing functional in those two.
>
> ## After merge
>
> The `app-v0.1.7` tag goes on **this** commit, not on whatever `main` reaches later — per the convention, work landing after a changelog is sectioned belongs to `[Unreleased]`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #122 — Gifts, and buying things on the marketplace

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-commerce` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/122>

> Round 2 of the audience work, based cleanly on `main` now that #121 has landed. It opens by fixing what round 1 turned up: **`listings` had no price and no purchase endpoint at all** — a product could be listed and bought by nobody. Packs and licences had priced purchase; listings never got it.
>
> ## A listing is a shop window; an offer is what makes it a shop
>
> `POST /marketplace/listings` needs no token and never has, so anyone can create a listing naming any `provider_name` they like. Harmless while listings were discovery-only — and *not* harmless the moment a price can attach to one.
>
> So price and seller live in a separate `listing_offers` row that only a token-holder can write, and **the seller comes from that token, never from a request body**. A listing with no offer cannot be bought — not because of a check somebody could forget, but because there is nowhere for a price to be. The safety property is structural.
>
> This also avoids a second schema trap: `_SCHEMA` is applied with `CREATE TABLE IF NOT EXISTS`, so new columns on the existing `listings` table would only ever appear on a fresh database. Same reasoning as the `desk_beacons` table last round.
>
> | refused | why |
> |---|---|
> | unpriced listing | "a shop window, not a shop" — no seller to pay |
> | buying your own listing | credits you with your own money *and* inflates the sales count |
> | withdrawn / sold out | the shop is shut; the window can stay up |
> | rated listing, unverified viewer | same gate that hides it from an unverified browse |
>
> Buying confirms `accept_price` **against the offer**, so agreeing to a number means agreeing to *the* number rather than merely stating one. An order copies the title it was bought under — a receipt that changes when the seller edits the listing is not a receipt. Withdrawing keeps both the shop window and past receipts.
>
> ## A gift is not a small purchase
>
> A purchase exchanges money for a thing. A gift sends money to a person and receives nothing — and that asymmetry is exactly the shape livestream tipping keeps turning into a way of taking money from people who should not be spending it. So gifts carry rules purchases don't:
>
> - **The giver must be a verified adult**, whoever they're gifting. An account with no birthdate is refused: an unverified age is not evidence of an adult.
> - **A single gift is capped** (`GIFT_MAX`, 500).
> - **A rated desk runs the 18+ gate on top.** The giver being an adult and the surface being rated answer different questions; neither substitutes.
> - **The beneficiary is read from the subject**, never named by the giver — a body-supplied one would let anyone route a performer's gift into their own balance. There's a test that passes `beneficiary: "attacker"` in the body and asserts it lands nowhere.
>
> Each gift states `refundable: false` at the point of giving rather than in a policy page. Nothing is delivered, so there is nothing to return.
>
> ## Money is still simulated
>
> Real rows on the creator's statement under `listing_sale` and `gift`, settling through the same payout sweep as pack sales and licence fees — no real funds moved. Every money-bearing response says so **in its own body** rather than relying on a page nobody opens.
>
> ## What this is not
>
> `docs/commerce.md` lists it plainly: running spend totals, cooling-off after a burst, parental controls, a real identity check behind "verified adult", chargeback handling, and payout/tax compliance are **all absent**.
>
> That list is written down rather than omitted because a half-built safety feature that looks whole is worse than an obviously missing one — and because anyone wiring a real payment processor to these endpoints needs to know what's left to do.
>
> ## Verification
>
> 486 tests green, 22 new. Confirmed against the ledger directly that a sale credits the seller and a gift credits the person behind the desk, rather than assuming the `credit()` calls landed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #121 — The audience layer: like, comment, share, subscribe

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-audience` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/121>

> Round 1 of two. Everything a viewer does *other* than talk — chat and rooms already carried the conversation; this is the quieter half. Gifting and marketplace purchase are round 2.
>
> > Originally stacked on #120; rebased onto `main` after that merged, so this is now a single commit containing only the audience layer.
>
> ## Four verbs, four targets
>
> | | profile | desk | message | listing |
> |---|---|---|---|---|
> | like / comment / share | ✓ | ✓ | ✓ | ✓ |
> | subscribe | ✓ | ✓ | — | — |
>
> A message and a listing can't be subscribed to — subscribing means *tell me when there is more from them*, and neither produces more. Targets are a `(kind, id)` pair rather than a column per thing; four near-identical tables would have drifted apart within a round.
>
> ## Three properties carry the design
>
> **A like is a fact, not a counter.** `reactions` is UNIQUE on `(target, actor)`, so liking twice is idempotent and reports `was_already_liked` rather than erroring. An integer column would let one account manufacture popularity by calling an endpoint in a loop — which makes *every* number on the platform meaningless, not just that one. It's also why a like needs a token: a like from nobody in particular is a number anyone can produce.
>
> **A comment is authored text, so it's filtered like authored text.** Same moderation pipeline as a chat turn, at **the target's** maturity setting rather than the commenter's, since it lands under someone else's name. A blocked comment is kept, returned to its author with the reason, and shown to nobody else — `201`, not `422`, because the comment *was* accepted and recorded; what happened to it is in `status`. Dropping it silently teaches the author nothing and they repost; showing it to everyone teaches them the filter doesn't work.
>
> **Sharing is gated at the far end, not at the sharer.** No token needed, including for a rated target, because the link lands the recipient on the age wall regardless of who sent it. Refusing the sharer would be gate theatre. Shares record the actor when there is one — "shared 40 times" and "shared 40 times by one account" are different facts.
>
> ## Subscriptions
>
> Two tiers on one row: free `follow`, and `paid` which credits the creator's ledger each period alongside pack sales and licence fees.
>
> - **`accept_price` must match** — the same explicit consent priced packs use, for a sharper reason: a recurring charge a viewer didn't mean to start *keeps* costing them.
> - **Nothing bills on a timer.** First period charged on subscribe, later ones by an explicit `POST /subscriptions/{id}/renew`. A deployment left running accrues nothing unseen.
> - **Cancelling keeps the row**, so a lapsed subscriber stays distinguishable from someone who was never there. Re-subscribing reuses it.
> - **Money is simulated**, as everywhere else here — and each subscription says so in its own `billing` field rather than leaving it to a policy page. It still writes a real row on the creator's statement (`kind: subscription`) and settles through the existing payout sweep.
>
> ## The rated gate
>
> Every verb runs the deployment's **existing** verified-adult check rather than a second implementation — the weaker of two gates is always the one that gets used. The test asserts across all five surfaces in one loop, because a gate remembered on four of five is exactly the kind that ships.
>
> ## Two naming calls
>
> - `GET …/audience`, **not** `engagement` — that word already means the per-relationship EMA score that conditions the persona prompt. Two different numbers under one word get read as one.
> - Path segments are the plural resource names the rest of the API uses (`/profiles/…`), mapped to singular kinds internally, so these routes read like the ones they sit beside. The router registers **last** so every concrete route gets first refusal on a match.
>
> ## Verification
>
> 464 tests green, 26 new — re-run after the rebase, not just before it. Confirmed the paid subscription actually lands on the creator's statement rather than assuming it, and that no generic route shadows an existing one (176 routes, full suite green).
>
> ## Found along the way
>
> `listings` has **no `price` and no purchase endpoint at all** — you can list a product on the marketplace today and nobody can buy it. Packs and licences have priced purchase; listings never got it. That's the first thing round 2 fixes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #120 — Leave a live desk behind as a printed code

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-desk-beacons` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/120>

> A profile can be left somewhere physical as a QR sticker. A desk could not — the odd gap, since the sticker on the shop door is arguably the more natural of the two: it is there precisely *because* nobody is behind the desk right now, which is the exact situation the bell was built for.
>
> ## The two are the same gesture aimed at opposite things
>
> That difference is the whole feature. Scanning a profile beacon reveals somebody who does not exist, and the page marks the portrait **AI**. Scanning a desk beacon reveals somebody who does, and the page must not say otherwise.
>
> | | profile beacon | desk beacon |
> |---|---|---|
> | what is revealed | somebody who does not exist | somebody who does |
> | the badge | **AI** — neutral, bottom-left | **Live person — not AI** — green, top-right |
> | the way in | a conversation, or a shared room | the bell, and the live stream |
> | a rated one, scanned | age wall | age wall |
>
> The badge placement is deliberate: the two must not be confusable at the glance a scanner actually gives them. Absence of the AI mark is **not** a disclosure on its own — an unmarked card could be a synthetic profile whose badge got dropped — so the claim is positive, and it carries who vouched for it, on the page rather than in a policy document elsewhere.
>
> ## Two things follow from the scanner being a stranger
>
> Neither is a gap to close later:
>
> - **Their ring is anonymous**, so it takes the 30-second per-desk cooldown rather than the 5-minute per-caller one. A printed code is reachable by anyone walking past; that is the entire threat model.
> - **A rated desk always shows them the age wall.** There is no token on a sticker scan that could clear it, which is the right answer rather than a limitation. The wall withholds the name and, above all, the location — whereabouts on an adult listing is a safety matter, and a sticker is by definition somewhere physical.
>
> Placing a beacon is **owner-only**. Anyone who could print a code for a desk they do not hold could put a stranger's name and whereabouts on a sticker and put it anywhere.
>
> ## Two implementation choices worth flagging
>
> **Its own `desk_beacons` table, not a nullable `desk_id` on `beacons`.** That column is `NOT NULL` on every database already out there, and the schema is applied with `CREATE TABLE IF NOT EXISTS` — so widening an existing table would only ever take effect on a fresh one. Additive works everywhere.
>
> **The bell posts to a relative URL.** It is the one script on the scan page. An absolute public base would ring a bell on a different host when the code is scanned over a LAN, where the origin that actually served the page is an IP rather than the configured hostname.
>
> ## Also: the release convention, written down
>
> `docs/releasing.md` here and in both sibling repos now records that the three products cut as one release — same number, same pass, even when a repository has nothing of its own to ship, in which case its entry says so in those words rather than being padded. It also writes down the trap that follows, because it already nearly bit: tag the release-prep commit rather than the tip of `main`, since QRME's v0.1.6 tag point sits two commits behind its `main` for exactly this reason.
>
> ## Verification
>
> 438 tests green, 11 new. The JavaScript syntax guard is one I checked can actually fail: mutating the bell script made it go red, restoring it made it green — a guard that cannot fail is worse than none. Also verified `node --check -` genuinely rejects bad input from stdin rather than passing vacuously.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #119 — README: repair the intro, standardize the patent line

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/readme-patent-polish` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/119>

> The first paragraph of the README had two sentences fused into one. It read:
>
> > …all within the same secure, private network **environment lets a user create, customize, and interact with** AI-driven synthetic profiles…
>
> The patent blurb and the description of what QRME actually is had been pasted together, so the first thing anyone reads on the repo is a sentence that doesn't parse.
>
> ## What changed
>
> Three changes, all confined to the opening. `README.md` is the only file touched: **+10 / −4**.
>
> - **The patent notice becomes a blockquote** above the description, with the application number written the way a patent number is normally written rather than as a shouted run-on. Same information, same claim.
> - **The description starts as its own sentence again.**
> - **The agent-management copy moves into a "Roadmap" paragraph.** It keeps its content, but it describes what the platform will do when those capabilities are activated — not what it does today. Leaving it inside the opening sentence is what fused the two in the first place.
>
> No claim is added, removed, or weakened. This is the same information, punctuated.
>
> ## Provenance, and the part I dropped
>
> This was written on a branch dated 22 July that never had a PR opened for it — it surfaced during a cleanup of stale local branches, as the one branch that couldn't be confirmed merged. It was rebased onto current main; the conflict was in exactly the paragraph it rewrites.
>
> Its **`## Download` section was dropped rather than rebased.** It hardcoded `0.1.0` installer filenames (`QRME-0.1.0-universal.dmg` and friends), which are three releases stale, and stated flatly that installers are unsigned — which per-OS signing has since made conditional on whether signing secrets are configured. A download section naming the wrong files is worse than no download section, and the Releases page is already linked from the docs.
>
> ## Verification
>
> 427 tests green. No test reads `README.md`. Checked for leftover conflict markers (none) and for links pointing at the removed `#download` anchor (none — the remaining "download" mentions are prose about knowledge-pack downloads).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #118 — Windows signs, through the browser engine rather than interop

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-windows-signing` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/118>

> The two loose ends from the audit.
>
> ---
>
> # 1. Windows can sign
>
> I said `webauthn.dll` interop was the blocker and that I wouldn't ship it untested. That was the right call about *the interop* and the wrong call about *the feature* — there's another route to Windows Hello with no marshalling in it at all.
>
> **Edge already implements WebAuthn and already talks to Windows Hello.** So the desktop app hosts a **WebView2** pointed at a new `GET /signatures/ceremony`, the page calls `navigator.credentials`, and the assertion comes back over the WebView2 message channel. The part most likely to be wrong is Edge's job, not mine.
>
> Two properties of that page are load-bearing rather than incidental:
>
> - **Served from the relying party's own origin.** WebAuthn refuses a mismatched `rpId`, and an opaque origin — a `data:` URL, a local file — has none to match. That's *why* it's a server route and not a string embedded in the C#.
> - **It never sees a token.** The page returns the raw assertion to its host; the host makes the authenticated call. A bearer token in a query string ends up in logs and browser history.
>
> It renders the document before the prompt for the same reason the native screens do: the system prompt can never say what is being signed.
>
> ## What I could actually verify here
>
> - The page escapes its input (`<script>` in the display text comes back inert).
> - It carries no token.
> - It refuses an unknown mode or a missing challenge (422 both).
> - **Its JavaScript parses under `node --check`** — the `%`-formatting around the JS modulo operator was the obvious way to break this silently, so I checked rather than assumed.
>
> **The C# has not been compiled here.** The Windows CI job on this PR is its first compile.
>
> One fragile thing I wrote and then removed: I was parsing the enrolment challenge back out of the navigated URL. It's stored in a field now — re-deriving it from a query string is a decode bug waiting to happen.
>
> ---
>
> # 2. `asset_marked` has a consumer
>
> It rode on the avatar response and nothing read it. The camera overlays are the surface that most needs it: a shipped starter's portrait carries the AI mark **in its own pixels**, an owner-attached asset is somebody else's file that cannot be vouched for, and a surface QRME doesn't control has to be able to tell those apart.
>
> `GET /b/{id}/card` now reports `portrait_marked`. QRME's own overlays still draw their badge either way — theirs carries the profile's *designed* label and is real text rather than pixels, so it's additive, not redundant.
>
> The exact-shape assertion on the card caught the new field, which is the test doing its job rather than getting in the way.
>
> ---
>
> ## Verification
>
> `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **427 passed** (3 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #117 — Release prep v0.1.6, and three gaps the audit found first

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-release-v0.1.6` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/117>

> v0.1.5 led on the beacon. This one leads on **telling the truth in both directions**: a synthetic profile now carries the AI mark in its own pixels, and a live desk carries none at all.
>
> Before cutting it I went looking for things that shipped *looking* finished and could not work. Three, all real.
>
> ---
>
> ## 1. The signing flow in both mobile apps could never succeed
>
> iOS and Android each enrol a passkey at `self_asserted` — all their screens can do — then immediately requested the `standard` tier, which needs `federated` proofing or better. Every attempt died at the server:
>
> ```
> enrol:            201  can_sign: ['basic']
> request standard: 422  "this account has no credential enrolled to the 'standard' tier"
> ```
>
> **My tests missed it because every one of them enrols at `document` level**, so none walked the sequence the clients actually perform. There are now tests that do. Both apps default to `basic` and say plainly that the higher tiers need an identity check a passkey alone doesn't provide.
>
> ## 2. A credential's proofing level could never change
>
> `docs/signatures.md` said *"the user re-proofs and the new level applies from that moment forward"*. Nothing implemented it, so every credential was stuck at whatever it enrolled with, permanently — which is what made #1 unrecoverable rather than merely wrong.
>
> `POST /signatures/credentials/{id}/proofing` records a fresh check. **Going forward only:** a signature already made copied its level into the evidence at signing time, so raising the credential today cannot quietly upgrade what it signed yesterday. There's a test pinning exactly that.
>
> ## 3. A desk's camera could never be turned on
>
> `feed.live` was read from a column no endpoint could write, so the live branch was unreachable and every desk was a sample view for ever. `PUT /desks/{id}/camera` sets it — desk token only, because a camera on a person is not something a platform switches on for them.
>
> ---
>
> ## Also
>
> - Removed `desks.listing()`, defined and never called.
> - Gave desks and signatures the README sections they never got.
> - Fixed a `set_portrait` docstring still talking about a "placeholder" after the feature became a camera view.
>
> ## The release itself
>
> - Versions to `0.1.6`: `pyproject.toml`, the FastAPI app, the suite gateway, `app/` and `launcher/` `package.json`, plus the two root entries in each lockfile.
> - `CHANGELOG.md` cuts `[0.1.6] — 2026-07-25` with the link anchors.
> - `RELEASE_NOTES.md` rewritten.
>
> ## One thing you should decide
>
> **JIM-mini and PDI have empty `[Unreleased]` sections.** Everything since v0.1.5 is QRME-only, so bumping them to 0.1.6 would be a version with nothing in it. I've left them alone here rather than inventing content for a changelog — say the word if you want them bumped for suite alignment and I'll do it with a release note that says exactly that and nothing more.
>
> ## Verification
>
> `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **425 passed** (7 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #116 — The apps sign, the mark is in the pixels, and the portraits are cut on the right lines

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-signature-clients` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/116>

> Four things: native clients for the signature endpoints, the AI mark burned into the portraits, the mug that wasn't supposed to say anything, and a re-slice of the portrait sheet.
>
> ---
>
> # 1. The AI mark is in the pixels now
>
> The disclosure already rode *alongside* a portrait — `GET /profiles/{id}/avatar` returns it, and the beacon page and both camera overlays composite it. That covers every surface QRME controls and **none of the ones it does not**.
>
> Shipping the collection as static files at `/portraits/{handle}.webp` is what made that concrete, and that was my change in #115. An ordinary file URL can be hotlinked, embedded in someone else's page, scraped, saved or screenshotted — and a composited badge survives none of those. The result is a synthetic face circulating with nothing saying so, which is the one outcome the watermark exists to prevent.
>
> So the mark goes into the bytes:
>
> - **Top-right**, because every composited badge in the product is bottom-left (`landing.py`, `BeaconScannerView`, `BeaconScanner.kt`). They never collide, and they aren't duplicates: the burned mark is the invariant "AI" designation on the pixels, the composited one carries the profile's *designed* label as selectable, accessible text.
> - **Burned offline** by `tools/mark_portraits.py`, not at request time — that would put an imaging library in the runtime dependencies and redraw a constant on every fetch.
> - **Pinned by a SHA-256 manifest** the test suite checks. A portrait swapped for an unmarked one fails CI instead of shipping quietly. The check needs no imaging library, so it runs in CI as-is.
> - `asset_marked` on the avatar response says which case an asset is in. QRME's surfaces composite either way; the field is for surfaces it *doesn't* control — a VR nameplate, an AR overlay, an embed, a marketplace card. An owner-attached asset always reports `false`, because nothing here can vouch for someone else's file.
>
> ---
>
> # 2. The signing clients
>
> | Platform | Enrol | Sign | Read & verify |
> | --- | --- | --- | --- |
> | iOS / visionOS | ✅ `ASAuthorizationPlatformPublicKeyCredentialProvider` | ✅ Face ID / Touch ID / Optic ID | ✅ |
> | Android | ✅ Credential Manager | ✅ platform authenticator | ✅ |
> | Windows | — | — | ✅ |
>
> iOS and Android use the platform's own passkey UI, so the private key stays in the Secure Enclave or StrongBox and the app never touches it. Both render the document **immediately before the prompt** and send that exact text to the server — the §5 mitigation, since the prompt itself can never say what is being signed.
>
> Both need a **verified domain** first (associated domains on iOS, Digital Asset Links on Android), which a LAN dev server cannot have. The screens say so rather than failing with a system error nobody can read.
>
> **Windows reads and verifies but does not sign, deliberately.** Reaching Windows Hello means `webauthn.dll` struct marshalling that a compile cannot meaningfully check and I cannot run here. A button that looks like it signs and might not is worse than no button. The desktop app gets the half needing no authenticator: enrolled credentials, an evidence package re-verified on fetch, and a paste box for checking a package a counterparty handed over.
>
> **Two C# collisions caught while writing it:** `SignaturePolicy()` and `SigningCredentials()` as members shadow the records of the same name, so the return types stop resolving (CS0118). Members renamed, wire types kept.
>
> ---
>
> # 3. The mug
>
> `bev_lindqvist` had the word **"nothing"** lettered onto her mug — a literal reading of the brief's "a mug that says nothing at all", and the only baked-in text in the collection that wasn't deliberate. Painted out, with the mug's shading interpolated across the patch per column rather than flattened.
>
> # 4. The slice was on the wrong lines
>
> The sheet was cut on a nominal 192px grid, but subjects overrun their cells, so several tiles carried a sliver of the neighbour — Otis's arm in Bev's frame, his guitar headstock in Lena's. Re-sliced on the **quietest column near each seam**, which is where the real gutter is; most seams have literally zero content, and the two that don't are exactly the ones that looked wrong.
>
> `dr_priya_nair` is re-cropped too — her source is a wide landscape scene, so a full-width cut padded her down to a thumbnail inside her own tile.
>
> ---
>
> ## Verification
>
> - `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **390 passed**.
> - **The Swift, Kotlin and C# have not been compiled here** — the native CI jobs on this PR are their first compile. I'll report what they say rather than route around them.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #115 — Signatures that survive being disputed, and the Android camera overlay

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-signature-spec` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/115>

> Two things: the WebAuthn/passkey signature scheme (spec **and** implementation), and the Android in-camera beacon overlay via CameraX + ML Kit.
>
> ---
>
> # 1. Signatures
>
> `docs/signatures.md` is the reasoning; `qrme/webauthn.py`, `qrme/signatures.py` and `qrme/routers/signatures.py` are the implementation.
>
> ## The core of it
>
> The instinct was right — a real Face ID *is* the gesture. What changes is what comes back from it.
>
> ```swift
> LAContext().evaluatePolicy(...) { ok, _ in
>     if ok { api.post("/handoff/sign", ["signed": true]) }   // ← the whole problem
> }
> ```
>
> That returns a **boolean, to the app**. A patched client sends `{"signed": true}` and the server cannot tell. In a dispute the record says "our software says he agreed," which is the claim under dispute. Face ID isn't the weak part — the weak part is that `evaluatePolicy` leaves behind no artifact anyone else can check.
>
> ## The challenge is the document
>
> ```
> challenge = SHA-256(canonical({v, envelope, doc_sha256, display_sha256,
>                                meaning, signer, tier, issued_at, expires_at, rp}))
> ```
>
> The authenticator signs over that, so the assertion binds a verified gesture to **one record and nothing else**. `test_altering_the_document_after_signing_breaks_verification` is the whole feature in one test.
>
> Also enforced: `userVerification: "required"` (a presence tap is refused), one envelope signs once, an assertion made for document A is refused for document B, and a `webauthn.create` ceremony can't be laundered into a signature.
>
> ## Verification is real
>
> `cryptography` becomes a runtime dependency. That's the honest call: a module that parsed assertions without verifying them would produce records that only *look* like evidence. CBOR is the small subset WebAuthn actually uses — written here, refusing anything outside it — rather than another dependency.
>
> The 30 tests build a fake authenticator on a **genuine P-256 key**: real authenticator data, real client data, a real ECDSA signature. Nothing is stubbed on the verification path, because a mocked signature check would prove only that the mock returns `True`.
>
> ## Policy that's enforced, not documented
>
> - A `self_asserted` credential is **refused at `/signatures/request`** for the high tier.
> - Syncable credentials report `be`/`bs` and are barred from the top tier — a key present on every device in a cloud account is a weaker claim of exclusive possession.
> - The evidence **copies the public key**, so revoking a passkey never retroactively unmakes what it signed.
> - `POST /signatures/verify` checks a package with no token and no lookup: a counterparty shouldn't have to trust this deployment.
> - Every package ships its own limits attached, including that WebAuthn has no trusted display.
>
> ## One correction to the spec, found by writing the tests
>
> §7 said Vision Pro "works today, unchanged" because Optic ID is a platform authenticator — then required *every* headset onto the second device. Both can't be true.
>
> Optic ID's prompt is composited by the system, exactly the position an iPhone is in with Face ID, and we don't send iPhones to a second device. The document is app-rendered either way, so requiring hybrid on visionOS is a real usability cost buying nothing. **The hybrid requirement now falls on headsets with no platform authenticator** (Quest, Android XR, anything unrecognised) — which needed the phone anyway. Spec and code corrected together.
>
> ## ESIGN/UETA, not Part 11
>
> HIPAA does **not** require Part 11 — that confusion is common and expensive — and JIM's terms already state the product is not a medical device, so there's no FDA-regulated record for it to attach to. The certificate endpoint (a Part 11 requirement) ships anyway, because it's also what makes a signature legible to a person.
>
> ---
>
> # 2. The Android camera overlay
>
> `native/android/app/.../ui/BeaconScanner.kt` — CameraX owns the viewfinder, ML Kit reads the code, same behaviour as the iOS scanner.
>
> **The one genuinely different thing is coordinates.** ML Kit reports in the analysis image's own space — rotated relative to the view, usually a different resolution — so the box is mapped through the preview's `FILL_CENTER` transform before anything is drawn. Skip it and the portrait lands where the sticker is not: it looks like a tracking bug and is really a coordinate-space bug. (iOS has the mirror-image problem: Vision's origin is bottom-left, SwiftUI's is top-left.)
>
> The barcode model is **bundled** rather than downloaded on demand, so a first scan works without Play Services fetching anything. `SmallAction` in `Screens.kt` is file-private, so the scanner carries its own button rather than widening another file's API to reach it.
>
> ---
>
> ## Verification
>
> - `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **380 passed** (30 new).
> - **The Kotlin has not been compiled here** — the native CI job on this PR is its first compile.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #114 — Release prep v0.1.5

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-release-v0.1.5` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/114>

> v0.1.4 led on choice — one command, every way to run QRME. This one leads on **the beacon**: leave a profile somewhere physical, and a stranger with a phone meets it.
>
> _(Reopened from #113 — its branch was pruned while it was in flight, which auto-closed it. Identical commit.)_
>
> ## What changed
>
> - Versions to `0.1.5` everywhere: `pyproject.toml`, the FastAPI app, the suite gateway, `app/` and `launcher/` `package.json`, plus the two root entries in each lockfile. Dependency versions untouched — the lockfile edits anchor on position, not on a bare version string.
> - `CHANGELOG.md` cuts `[0.1.5] — 2026-07-25` from Unreleased, with the compare/tag link anchors.
> - `RELEASE_NOTES.md` rewritten for v0.1.5.
>
> ## Three entries the beacon round never wrote down
>
> The landing page (#110) and the camera overlay (#112) shipped without changelog entries. Added: the page instead of JSON, shared-room beacons, and the in-camera overlay.
>
> ## One correction
>
> The native-CI entry still said Windows builds with `dotnet build`. That was true when it was written and stopped being true when the WinUI3 PRI packaging task turned out to ship only with Visual Studio's MSBuild — the changelog would have shipped describing a workflow that doesn't exist. It now also records that all three steps re-surface compiler diagnostics on failure.
>
> ## On how the camera feature is described
>
> The notes state the boundary rather than leaving it to the docs: a **stock** camera app can only open a URL, and drawing over a viewfinder means owning the viewfinder. Someone reading "the profile appears on the sticker" should not come away thinking it happens in Apple's camera app.
>
> ## Verification
>
> `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **350 passed** locally. CI ran this exact commit on #113 before the prune closed it: **342 passed, 8 skipped**, having installed `qrme-0.1.5` — so the bump is confirmed to be the version under test.
>
> This PR touches no code, so the native jobs won't run on it — they were green on #112, including the overlay's first compile.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #113 — Release prep v0.1.5

- closed · opened 2026-07-25
- `claude/qrme-release-v0.1.5` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/113>

> v0.1.4 led on choice — one command, every way to run QRME. This one leads on **the beacon**: leave a profile somewhere physical, and a stranger with a phone meets it.
>
> ## What changed
>
> - Versions to `0.1.5` everywhere: `pyproject.toml`, the FastAPI app, the suite gateway, `app/` and `launcher/` `package.json`, plus the two root entries in each lockfile. Dependency versions untouched — the lockfile edits anchor on position, not on a bare version string.
> - `CHANGELOG.md` cuts `[0.1.5] — 2026-07-25` from Unreleased, with the compare/tag link anchors.
> - `RELEASE_NOTES.md` rewritten for v0.1.5.
>
> ## Three entries the beacon round never wrote down
>
> The landing page (#110) and the camera overlay (#112) shipped without changelog entries. Added: the page instead of JSON, shared-room beacons, and the in-camera overlay.
>
> ## One correction
>
> The native-CI entry still said Windows builds with `dotnet build`. That was true when it was written and stopped being true when the WinUI3 PRI packaging task turned out to ship only with Visual Studio's MSBuild — the changelog would have shipped describing a workflow that doesn't exist. It now also records that all three steps re-surface compiler diagnostics on failure.
>
> ## On how the camera feature is described
>
> The notes state the boundary rather than leaving it to the docs: a **stock** camera app can only open a URL, and drawing over a viewfinder means owning the viewfinder. Someone reading "the profile appears on the sticker" should not come away thinking it happens in Apple's camera app.
>
> ## Verification
>
> `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **350 passed**.
>
> This PR touches no code, so the native jobs won't run on it — they were green on #112, including the overlay's first compile.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #112 — See who the sticker is without leaving the camera

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-camera-overlay` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/112>

> Point the phone at a beacon sticker and the profile appears **on the sticker**, in the live camera feed. No tap, no page, no navigation.
>
> _(Reopened from #111 — that PR's branch was pruned while it was in flight, which auto-closed it. Same commit, rebased onto main after #109.)_
>
> ## Three cameras, three different answers
>
> Worth stating up front, because only one of these is ours to build:
>
> | Camera | What it can do | Status |
> | --- | --- | --- |
> | Stock camera app (iOS/Android) | Open a URL. That is the entire API surface a QR code exposes to a third party — there is no hook to draw into someone else's viewfinder. | The landing page from #110 is the best possible version of this, and it is still a page. |
> | **The QRME app** | Owns the viewfinder, so it can draw on it. | **This PR.** |
> | App Clip Card | A card over Apple's own camera with no app installed. | Documented in `docs/beacons.md`; configuring it needs the account holder's Apple Developer account, so it is not code that can land here. |
>
> ## `GET /b/{beacon_id}/card`
>
> The payload an overlay needs and nothing more: `profile_id`, `display_name`, `watermark`, `portrait`, `initials`, `label`, `shared_room`, `open_url`, `age_wall`. It counts a scan the same way the HTML page does.
>
> A rated beacon returns `{"age_wall": true, "rated": true, "note": …}` and **nothing else** — no name, no portrait. The overlay renders whatever comes back, so the withholding has to happen at the source rather than be trusted to the client.
>
> `summon_url` and `scan_url` are unchanged.
>
> ## `BeaconScannerView`
>
> - `AVCaptureSession` + `VNDetectBarcodesRequest` restricted to `.qr`.
> - Vision reports a normalised box with the origin at the bottom-left; SwiftUI draws from the top-left. The conversion is why the portrait sits **on** the sticker and tracks it as the phone moves, rather than parking in a corner of the screen.
> - Resolution is guarded by beacon id plus an in-flight flag. The camera delivers ~30 frames a second and every one of them sees the same sticker; without the guard the overlay would re-request continuously and count a scan each time.
> - Payloads that are not `<base>/b/bcn_…` are ignored — somebody's Wi-Fi QR is left alone.
> - Reachable from Manage → Summon → "Scan a beacon".
>
> The AI mark is drawn from the same payload as the face, in the same view, always. An overlay that could show the portrait without the disclosure would be the worst version of this feature: a synthetic person appearing in the real world with nothing saying so.
>
> `NSCameraUsageDescription` is added to the iOS target — iOS terminates the app on first capture without it.
>
> ## Verification
>
> - 350 passed (`QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q`), including 7 new tests for the card endpoint: shape, scan counting, shared-room flag, missing beacon, and that a rated beacon leaks neither name nor portrait.
> - **The Swift was never compiled locally** — there is no Xcode in this environment. The native CI job added in #108 was its first compile, on #111, and the iOS job came back green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #111 — See who the sticker is without leaving the camera

- closed · opened 2026-07-25
- `claude/qrme-camera-overlay` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/111>

> Point the phone at a beacon sticker and the profile appears **on the sticker**, in the live camera feed. No tap, no page, no navigation.
>
> ## Three cameras, three different answers
>
> Worth stating up front, because only one of these is ours to build:
>
> | Camera | What it can do | Status |
> | --- | --- | --- |
> | Stock camera app (iOS/Android) | Open a URL. That is the entire API surface a QR code exposes to a third party — there is no hook to draw into someone else's viewfinder. | The landing page from #110 is the best possible version of this, and it is still a page. |
> | **The QRME app** | Owns the viewfinder, so it can draw on it. | **This PR.** |
> | App Clip Card | A card over Apple's own camera with no app installed. | Documented in `docs/beacons.md`; configuring it needs the account holder's Apple Developer account, so it is not code that can land here. |
>
> ## `GET /b/{beacon_id}/card`
>
> The payload an overlay needs and nothing more: `profile_id`, `display_name`, `watermark`, `portrait`, `initials`, `label`, `shared_room`, `open_url`, `age_wall`. It counts a scan the same way the HTML page does.
>
> A rated beacon returns `{"age_wall": true, "rated": true, "note": …}` and **nothing else** — no name, no portrait. The overlay renders whatever comes back, so the withholding has to happen at the source rather than be trusted to the client.
>
> `summon_url` and `scan_url` are unchanged.
>
> ## `BeaconScannerView`
>
> - `AVCaptureSession` + `VNDetectBarcodesRequest` restricted to `.qr`.
> - Vision reports a normalised box with the origin at the bottom-left; SwiftUI draws from the top-left. The conversion is why the portrait sits **on** the sticker and tracks it as the phone moves, rather than parking in a corner of the screen.
> - Resolution is guarded by beacon id plus an in-flight flag. The camera delivers ~30 frames a second and every one of them sees the same sticker; without the guard the overlay would re-request continuously and count a scan each time.
> - Payloads that are not `<base>/b/bcn_…` are ignored — somebody's Wi-Fi QR is left alone.
> - Reachable from Manage → Summon → "Scan a beacon".
>
> The AI mark is drawn from the same payload as the face, in the same view, always. An overlay that could show the portrait without the disclosure would be the worst version of this feature: a synthetic person appearing in the real world with nothing saying so.
>
> `NSCameraUsageDescription` is added to the iOS target — iOS terminates the app on first capture without it.
>
> ## Verification
>
> - 350 passed (`QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q`), including 7 new tests for the card endpoint: shape, scan counting, shared-room flag, missing beacon, and that a rated beacon leaks neither name nor portrait.
> - **The Swift has not been compiled locally** — there is no Xcode in this environment. The native CI job added in #108 is its first compile, and it runs on this PR because `native/**` changed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #110 — Beacons: a page instead of JSON, and shared rooms

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-beacon-landing` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/110>

> ## Why
>
> A beacon is a profile left somewhere physical. Its printed QR pointed at `/summon?ref=…`, which answers **JSON** — so anyone scanning that sticker got a wall of braces. `GET /b/{beacon_id}` is the page that should have been there.
>
> ## On "it generates right there"
>
> The reveal is a CSS animation, because **a stock camera app scanning a QR can only open a URL**. It can't composite anything over the viewfinder. Anchoring a portrait to the sticker in 3D needs WebXR (partial on iOS Safari, and it prompts for camera permission — a hard sell for a stranger) or the native apps via a deep link. `docs/beacons.md` says so rather than implying otherwise.
>
> ## One conversation, or many
>
> `mode` decides what a scan opens:
>
> - **`chat`** (default) — a private conversation each. Unchanged.
> - **`room`** — one shared room, minted at placement with the profile already in it. Everyone scanning the same sticker joins the same conversation: a class, a workshop, a meeting, a Q&A after a set. Open until the beacon is picked up.
>
> The page says *"you may not be the only one here"* — someone who scanned a sticker has no way of knowing, and walking into a room isn't the same as opening a chat.
>
> **Rated placements stay one-to-one.** A shared room behind an 18+ QR at a public venue raises moderation questions nobody should acquire by accident, so it isn't reachable from that path.
>
> ## Placement is the actual idea
>
> `docs/beacons.md` pairs the starter industries with where they earn their keep — musician in the green room, nutritionist in the produce aisle, financial planner in a bank lobby, sponsor at the back table of a meeting, legal at a courthouse corridor. Nothing in the code ties an industry to a place; it's guidance.
>
> It also flags that a code in a clinic waiting room or at a recovery meeting will be scanned by people in a bad hour, so don't place a beacon somewhere its profile isn't equipped for.
>
> ## What a stranger is told
>
> - **The AI mark rides on the portrait**, not the chrome — a screenshot carries the disclosure too.
> - **Rated → age wall**, which is the ordinary path for a public sticker since a stranger has no token. The wall says the check happens at QRME, not at whoever placed the code.
> - **Picked-up beacons and departed profiles** get a sentence, not a stack trace.
>
> ## Two bugs found while building it
>
> - **`watermark.design()` ignored the anonymity flag.** An anonymous profile's real name was riding on every render it produced — chat turns, posts, portraits. The name is withheld on summon cards and marketplace listings; the watermark was the one surface giving it away. Fixed at that layer, so all surfaces are covered.
> - **"Talk to Dr."** — the call to action took the first word of the display name. Now skips honorifics, falling back to the whole name rather than to something wrong.
>
> ## Verification
>
> `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **343 passed** (22 new).
>
> Rendered every state in headless Chromium at phone size and looked at them. The initial preview used an unrelated photo as a stand-in and looked absurd — the shipped default for a profile with no portrait is initials, which is what the seeded starters actually get.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #109 — Make the Android and Windows build failures readable too

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-native-logs` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/109>

> ## Why
>
> The iOS step got this treatment when its first red run reported nothing but `exit code 65` and diagnosing it cost a full log dump. The other two jobs have the same problem — it went unnoticed here only because they happened to pass:
>
> - **Gradle** prints Kotlin diagnostics well above its `FAILURE` block, so the tail shows `compileDebugKotlin FAILED` and nothing about why.
> - **MSBuild** scrolls its errors past the per-project noise, leaving a bare exit code.
>
> Porting the gate to JIM-mini turned that from theory into a cost: its first run failed on **both** platforms, and each diagnosis needed the log pulled and paged through by hand.
>
> ## What changed
>
> Both steps `tee` their output and, on failure, re-surface the diagnostics in a collapsed group — `e:` lines for Kotlin, `error CSxxxx` for MSBuild. Same builds, legible results.
>
> Windows also gets `shell: bash` so the `pipefail`/`tee` idiom works identically across all three jobs.
>
> ## Verification
>
> The workflow triggers on changes to itself, so all three native jobs run on this PR — and since QRME's native code already compiles, a green run here is the real check: it proves the `tee`/`pipefail` wrapper doesn't break a **passing** build, which is the one way this change could do harm.
>
> The failure path is being exercised in parallel on the JIM-mini and PDI branches, where the same edit is pushed and those jobs are actually red.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #108 — Compile the native apps in CI

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-native-ci` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/108>

> ## Why
>
> The Swift, Kotlin and C# in `native/` **has never been through a compiler in this repository.** It was checked by reading it, and by balance/well-formedness checks on braces and XML — which catch a typo and nothing else. A missing symbol, a type error, a SwiftUI signature that moved, an unresolved dependency: all of it would ship, and be discovered by the first person who opened Xcode.
>
> ## Three toolchains, three runners
>
> | Job | Runner | What it does |
> |---|---|---|
> | **iOS** | `macos-latest` | `brew install xcodegen` → `xcodegen generate` → `xcodebuild` against the simulator SDK, signing disabled |
> | **Android** | `ubuntu-latest` | JDK 17 (matching `jvmTarget`) → Gradle 8.9 → `gradle assembleDebug` |
> | **Windows** | `windows-latest` | .NET 8 → `dotnet build -c Release -p:Platform=x64 -r win-x64` |
>
> Three details worth knowing:
>
> - **There is no `.xcodeproj` in git** — `project.yml` is the source of truth and XcodeGen generates the project, which keeps a merge-hostile generated file out of the repo. So CI proves the *spec* is valid too, not just the Swift.
> - **There is no `gradlew` or wrapper jar** (a checked-in binary nobody reviews), so `setup-gradle` provisions the version `gradle-wrapper.properties` already pins — CI and a developer's machine build with one Gradle.
> - **Windows needs a runtime identifier.** The csproj is unpackaged and `WindowsAppSDKSelfContained`, so the App SDK is copied in rather than resolved from a framework package.
>
> Compile only — signing and packaging stay in `desktop-release.yml` and need certificates this workflow deliberately doesn't have. It runs on changes under `native/` and on demand, not on every PR, since macOS runner minutes aren't free.
>
> ## Caveat, stated plainly
>
> **This workflow has not been executed anywhere.** There's no macOS, Windows or Android toolchain in the environment it was written in, so nothing here is verified beyond the YAML parsing. **Its first run is this pull request.**
>
> If it comes back red, that is most likely a real finding about code that has never been compiled — not a flaw in the workflow to route around. I'll read the failure and fix whichever end is actually wrong.
>
> ## Scope
>
> QRME only, on purpose. JIM-mini and PDI have the same `native/` structure and the same gap, but replicating a workflow to three repos before it has ever run once is how you get three broken workflows. Once this one is green I'll port it.
>
> ## Verification
>
> `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **297 passed** (unchanged; this adds no Python).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #107 — The Cloud Model Gateway server — the other end of a documented contract

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-cloud-gateway` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/107>

> ## Why
>
> `docs/cloud-model.md` has described this gateway for a while, and all three products could already talk to one — route inference to a greater hosted model, fall back locally when it's unreachable, contribute rated exchanges. What didn't exist was anything to talk to. The clients were tested against fakes, and the doc said the gateway *"is not part of these repositories."* Now it is (`cloudgw/`, `python -m cloudgw`).
>
> ## Deliberately small
>
> Consent, anonymization and fallback stay client-side, where they belong — the deployment holding the data is the only one that can decide what leaves it. The server authenticates callers, serves one operator-configured model, and takes contributions into PDI **as an ordinary tenant**, with no privileges the contract doesn't give every tenant.
>
> ## What it adds that a client can't
>
> **A last line of defence on the intake.** A gateway accumulates a corpus from deployments it doesn't control, running versions it didn't ship. One client bug and there are real names in the training data — found much later, if at all.
>
> So contributions are screened again here: identifying fields at any depth, product-shaped ids, email addresses. A leak is **refused with a 422 naming the field**, not sanitized. Sanitizing quietly would hide the client bug that produced it; refusing tells that deployment's operator their build is leaking while it can still be fixed. `cloudgw/screening.py` is importable on its own, so it can be run over a corpus that already exists.
>
> **Two more refusals:**
>
> - **No vault configured → contributions refused**, not written somewhere unencrypted and unauditable. Never storing beats storing badly. Inference, which needs no vault, keeps working.
> - **No `CLOUDGW_TOKENS` → localhost only.** Same posture as PDI's admin surface: an open gateway on a routable address is somebody else's model bill and an unattributable corpus.
>
> Without an API key it serves a deterministic stub and **says so** in `/v1/model`, `/health`, and at boot. A gateway quietly passing a stub off as a hosted tier is worse than one that refuses to start.
>
> ## Verified against real services, not only fakes
>
> Booted a real PDI and a real gateway, then drove QRME's own `CloudModelClient` through both:
>
> - Contribution sealed on disk — confirmed no plaintext in the `ciphertext` column.
> - `GET /audit/verify` → `intact: true`.
> - Wrong gateway token → `CloudProvider` falls back to the local provider.
> - Identity leak (`profile_id`) → refused.
> - `revoke_contributions` → record deleted, audit chain still intact (the deletion is itself audited).
>
> **That run found two bugs the unit tests could not:**
>
> 1. PDI's `ContributionIn` takes `payload` as an **object**; the store was sending a JSON string. A stub vault accepts either happily; a real PDI answers 422. The fake now asserts the type.
> 2. `python -m cloudgw` had a **syntax error** — nothing imported `__main__`, so it shipped green. There's now a test for it, because the banner it prints is how an operator learns they're serving a stub or collecting into a vault that isn't there.
>
> ## Verification
>
> `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **321 passed** (24 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #106 — Profile portraits: art direction, the badge, and whose face it is

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-avatars` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/106>

> ## Why
>
> A profile without a face is a row in a table. This adds the visual half of a synthetic identity — and puts the two things that can go wrong with one beyond any individual surface's ability to get them wrong.
>
> **No images are generated here.** This is the specification and the plumbing; assets attach afterwards through `PUT /profiles/{id}/avatar`.
>
> ## The badge is attached at the source
>
> `GET /profiles/{id}/avatar` never returns a bare asset — it returns the asset, the profile's AI watermark, and the likeness record together:
>
> ```json
> {
>   "asset": "avatars/marcus_bell.png",
>   "watermark": { "line": "✦ AI · Marcus Bell", "always_displayed": true },
>   "likeness": { "real_person": false, "note": "invented likeness — no rights holder" },
>   "placeholder": false
> }
> ```
>
> A portrait is the most-looked-at render QRME produces, and *"the client forgot"* is exactly how an unmarked synthetic face reaches a viewer. Attaching the badge at the source means the chat header, the marketplace card, the VR nameplate and the AR overlay all receive the disclosure from one shape. A profile with no portrait yet reports `placeholder`, so surfaces fall back to initials rather than showing an unbadged stock image.
>
> ## Whose face it is, is a rights question — so the API answers it
>
> An invented likeness reports no rights holder. A real person's face reports the recorded grant, who attested it, and that it can be withdrawn — because permission given in conversation is not a record, and the profile row is the thing the objection/takedown lifecycle can actually act on.
>
> Two rules this depends on were already enforced; the tests now assert them, since the portrait work rests on them holding:
>
> - `POST /profiles` → **422** for `kind="other_person"` with no consent basis and attestor.
> - `POST /profiles` → **403** for `adult_mode` on another real person. `rated.py` states it as a hard line, and a funny costume idea doesn't get to reopen it.
>
> ## The art direction ships as data
>
> Every starter has a brief written to be handed straight to an illustrator or a generator, published at `GET /avatars/briefs`. Each brief carries **its own constraints** — invented person, no trademarked costume, no logos — so they survive being pasted into a tool somewhere else. That's what keeps `seed.py`'s promise true of the picture and not just the persona.
>
> The briefs double as each profile's `appearance`, which rides on the prompt, so the face and the voice describe the same character.
>
> They lean funny on purpose — a stock headshot reads as a corporate mascot, while a financial planner in far too much gold reads as *a character, and everyone knows it*, which is the honest note for a synthetic profile to open on:
>
> | Profile | Portrait |
> |---|---|
> | Marcus Bell (finance) | Gold chains to the sternum, gold grills, pinky rings — holding a pocket calculator like a trophy. |
> | Wren Okafor (arts) | A brush in the teeth and one in each hand, cadmium yellow across one cheek that clearly happened hours ago. |
> | Harold Jenkins (insurance) | An umbrella held open indoors, because you never know. Expression entirely sincere. |
> | Bev Lindqvist (HR) | A mug that says nothing at all, and the expression of someone who has heard it and is not going to react. |
>
> **Three are deliberately not funny.** The mental-health trio JIM-mini's Guardian escalates to get calm rooms and no gags, marked `sombre` so a bulk generation run can't cheerful them up. A joke portrait on the profile someone reaches in a bad hour is a joke at their expense.
>
> ## A rated starter
>
> `@vivienne_sable` seeds the 18+ tier so it isn't an empty shelf either. Fictional by necessity rather than preference: adult mode is never available for a profile of another real person, and a starter ships to every deployment. The brief stays Old-Hollywood backstage glamour — gated in the product, tasteful in the source, since this repository is public.
>
> The existing age wall covers it unchanged: it is **absent from public browse entirely**, which the seed tests now assert rather than assume.
>
> ## Verification
>
> `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **291 passed** (15 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #105 — Deployable as one container: Dockerfile builds the studio, docs/hosting.md

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-deploy` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/105>

> ## Why
>
> Publishing an instance should keep the property that makes the phone flow work: the studio and the API on **one origin**, nothing to configure on the device. The existing `Dockerfile` shipped the API only, so hosting meant standing the UI up separately and reintroducing the "which host is the backend?" question that `/pair` exists to eliminate.
>
> ## What changed
>
> **`Dockerfile` — two stages.** `node:20-slim` builds `app/dist`; `python:3.12-slim` installs the package and takes only the built studio across, so the Node toolchain never ships in the runtime image.
>
> - Runs as a non-root service user (uid 10001).
> - `QRME_DB` defaults under the declared `/data` volume — a restart must not be a data-loss event.
> - Honours `$PORT` for platforms that assign one; `HEALTHCHECK` on `/health`.
> - Drops `COPY suite/`: nothing the service or the harness runs imports it.
>
> **One real bug, found by reading rather than building.** `console_dir()` resolves `app/dist` relative to the *package*, and after `pip install` the package lives in site-packages — nowhere near the dist the image copies to `/srv`. The studio would have been found only by accident, when the working directory happened to shadow the installed copy. Fixed by setting `QRME_CONSOLE_DIR=/srv/app/dist` explicitly.
>
> **`tests/test_container.py`** pins that agreement so it can't drift back: the env var must equal the COPY destination, the DB path must sit under the volume, `USER` must precede `CMD`, and the bind must be `0.0.0.0` with `$PORT` honoured. Static checks, deliberately — see the caveat below.
>
> **`docker/docker-compose.yml`** — the suite e2e harness builds this same image, and its one-shot `bootstrap` writes to a `shared` volume that Docker creates root-owned (no `/shared` exists in the image to inherit ownership from). It now runs as root there rather than the production image carrying a `/shared` it has no use for; the env files it leaves are world-readable for `qrme` and `jim`.
>
> **`docs/hosting.md`** — the operator's side:
>
> - The two postures side by side (local vs published) and which variables each requires.
> - Why TLS is not optional when owner and interactor tokens travel in headers.
> - What hosting other people's profiles commits you to — the ToS review, that encryption at rest belongs to PDI and QRME's own database is not encrypted, and that erasure has to be tested on your deployment before it's promised.
> - A **"What this does not give you"** section, stated plainly: no multi-tenancy, no rate limiting, no backups.
>
> Also notes that shared cPanel-style hosting is a poor fit — this is a long-running ASGI process, not a request-per-script runtime.
>
> ## Caveat, stated up front
>
> **The image was not built or run here.** The Docker CLI is present in this environment but there is no daemon, so every check on it is static. Build it once before trusting it.
>
> ## Verification
>
> - `QRME_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **281 passed** (5 new).
> - `docker/docker-compose.yml` and `.github/workflows/e2e.yml` parse.
> - Confirmed by inspection that `docker/bootstrap.py` and `docker/e2e.py` import only the stdlib, so removing `COPY suite/` cannot break the harness.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #104 — Published deployments: pairing knows its public URL, optional signup key

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-hosting` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/104>

> ## Why
>
> The phone flow assumed a laptop on Wi-Fi. Troubleshooting alongside colleagues means the same deployment also has to be reachable from the internet — a different posture. Both now work from one code path (matching pdi#51).
>
> ## What
>
> | Variable | Effect |
> |---|---|
> | `QRME_PUBLIC_URL` | `GET /pair` advertises the deployment's own address, **QR included**, instead of a LAN address the phone can't see from outside. Unset → LAN behaviour exactly as before. |
> | `QRME_SIGNUP_KEY` | Profile creation requires the key as an `x-signup-key` header, so a published instance stays the operator's and their colleagues' rather than open registration. Unset → open, the right default when reaching the API already means being in the house. |
>
> Talking to a profile stays public either way — the key gates **creating an account here**, not using one.
>
> One design note worth flagging: the gate rides as a **route dependency**, not a call inside the handler. It belongs to the HTTP surface, so in-process callers (seeding the starter collection) aren't affected. The starter-profile tests caught this immediately when it was written the other way — `qrme/seed.py` calls `create_profile()` directly, and a required `request` parameter broke six tests. The dependency form is both correct and less invasive.
>
> ## Testing
>
> `tests/test_hosting.py` (6): hosted pairing advertises the public URL; unhosted falls back to LAN; trailing-slash normalisation; the signup key refuses missing *and* wrong keys and accepts the right one; unset leaves local use open; and the gate does **not** touch chat with an existing profile.
>
> Full suite: **276 passed**.
>
> ## Follow-up
>
> Same treatment for JIM (`JIM_PUBLIC_URL` + `JIM_SIGNUP_KEY` on enroll) next, then Dockerfile + `docs/hosting.md` for self-host vs. outsourced.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #103 — sync-release-notes: publish the release body from RELEASE_NOTES.md

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-sync-release-notes` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/103>

> ## Why
>
> Release bodies have been pasted by hand, and v0.1.4 hit both failure modes: copying from a rendered page silently strips the markdown, and a manual "delete the old half" edit truncated a line mid-sentence. `RELEASE_NOTES.md` is already the source of truth (it literally says "kept in sync with CHANGELOG.md"), so there's no reason a human should be moving that text through a clipboard.
>
> ## What
>
> `.github/workflows/sync-release-notes.yml` sets a published release's body from `RELEASE_NOTES.md`:
>
> - **`workflow_dispatch`** with a `tag` input — fixes an existing release from the Actions tab.
> - **`push` on `app-v*` tags** — every future release gets its body automatically, right after the tag goes up.
>
> It strips the file's internal "ready-to-paste" preamble so the published body starts at the headline, then `gh release edit --notes-file` does the rest. Uses the repo's own `GITHUB_TOKEN` (`contents: write`) — no new secrets.
>
> ## Testing
>
> - YAML parses.
> - The extraction step verified against the real `RELEASE_NOTES.md`: yields 3298 chars, starts at `**QRME v0.1.4** — run it your way…`, contains no "Ready-to-paste" preamble, ends at `see the README.`
> - After merge I'll dispatch it against `app-v0.1.4` to repair the current body, which is the immediate fix.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #102 — Release prep v0.1.4: version bumps, changelog cut, release notes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-release-v014` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/102>

> ## What
>
> Release mechanics for **v0.1.4** — the launcher round rolls in, and the headline moves with it. v0.1.2/v0.1.3 led on trust (watermarking, terms, signed builds); this one leads on **choice**:
>
> > **QRME v0.1.4** — run it your way: one command prints every way to run QRME and you pick the device — your phone (scan a QR straight off the terminal), this PC, a packaged installer, or the headless API.
>
> - Versions to **0.1.4** everywhere: `pyproject.toml`, FastAPI app, suite gateway, `app/` and `launcher/` package.json + lockfile root entries (dependency versions untouched — the lockfile edits anchor on the package name).
> - CHANGELOG cuts **[0.1.4] — 2026-07-24** from Unreleased with its link anchor.
> - `RELEASE_NOTES.md` rewritten for v0.1.4: new headline, launcher and one-command phone setup leading the highlights.
>
> After merge, creating the `app-v0.1.4` tag fires the `desktop-release` workflow and builds the installers.
>
> ## Testing
>
> - Full suite: **270 passed** (run headless, the CI condition).
> - `app/` and `launcher/` front-ends build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #101 — python -m qrme: launcher menu — phone, desktop, installer, or headless, one command each

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-phone-cmd` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/101>

> ## What
>
> Same launcher as jim-mini#69 — users choose how and where to run QRME, one command each:
>
> ```bash
> python -m qrme           # the launcher menu: choose your device
> ```
>
> | Choice | Command | What happens |
> |---|---|---|
> | **On your phone** | `python -m qrme phone` | builds the studio if missing (first-run `npm install` included), prints the pairing URL **with a QR drawn straight into the terminal**, serves on the local network |
> | **On this PC** | `python -m qrme desktop` | the Electron desktop app; without npm it points at the packaged installers |
> | **Packaged installer** | releases/latest | `.dmg`/`.exe`/`.AppImage` — no toolchain needed |
> | **Headless API** | `python -m qrme serve` | backend alone, localhost by default (`--host`/`--port`) |
>
> Every option runs the same backend with the same data and token checks. `phone` flags: `--port`, `--rebuild`, `--no-build`, `--print-only`. Serving uses the `"qrme.api:app"` import string so the studio mount happens *after* the build step.
>
> ## Testing
>
> - 4 new tests: built path prints URL + terminal QR; headless path prints build guidance and no QR; the bare menu lists all four ways; `desktop` without npm points at the installers.
> - Full suite: **270 passed** (run headless, the CI condition).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #100 — Release prep v0.1.3: version bumps, changelog cut, release notes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-release-v013` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/100>

> ## What
>
> Release mechanics for **v0.1.3** — the phone round rolls in: studio served at `/app`, `GET /pair` with the scannable QR, and the installable PWA. The release-notes headline stays exactly as it was in v0.1.2 (the trust release); the phone feature leads the highlights.
>
> - Versions to **0.1.3** everywhere: `pyproject.toml`, FastAPI app, suite gateway, `app/` and `launcher/` package.json + lockfile root entries (dependency versions untouched).
> - CHANGELOG cuts **[0.1.3] — 2026-07-24** from Unreleased and repairs the release link anchors.
> - `RELEASE_NOTES.md` updated as the ready-to-paste v0.1.3 GitHub Release body.
>
> After merge, creating the `app-v0.1.3` tag fires the `desktop-release` workflow and builds the installers.
>
> ## Testing
>
> - Full suite: **266 passed**.
> - `app/` and `launcher/` front-ends build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #99 — Run QRME from your phone: served studio, pairing, installable PWA

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-mobile` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/99>

> ## What
>
> Same mobile treatment as jim-mini#67 — operate the QRME studio from a phone with nothing to install and nothing to configure.
>
> **The API serves the studio.** The built studio mounts at `/app`, so the UI and the API share one origin — the phone loads the page and calls the address it came from. No CORS setup, no "which host is the backend?" step. Mounted last so it can never shadow an API route, and skipped entirely when `app/` hasn't been built (the API stays headless as before).
>
> **`GET /pair` finds the machine.** It resolves this machine's local-network address from the routing table and returns the URL to open, plus `GET /pair/qr.svg` as a scannable QR — both surfaced in a pairing card on the Control Center screen. Loopback is treated as a failure, not a fallback (on a phone `127.0.0.1` means the phone), and every blocker — unbuilt studio, unreachable address — is reported at once rather than one per round trip.
>
> **Installable as a PWA** — manifest, icon, standalone display, and a service worker that caches the **app shell only**, never API traffic: a stale chat reply or moderation state shown as current is worse than an error.
>
> **Phone layout** — the sidebar becomes a thumb-reachable bottom tab bar, inputs sit at 16px so iOS doesn't zoom on focus, and the layout respects the notch and home indicator. Also fixes the app title ("QRME" → "QRME Studio") and gives the tab a real icon.
>
> ```bash
> npm --prefix app run build           # build the studio once
> uvicorn qrme.api:app --host 0.0.0.0  # listen on the network
> curl localhost:8000/pair             # what to open on the phone
> ```
>
> The address is local-network only — profiles and their memories stay on your own network, and every personal endpoint still requires the owner or interactor bearer token.
>
> ## Testing
>
> - `tests/test_mobile.py` (7): pairing returns a reachable address (never loopback) and a QR encoding it; the loopback case is reported honestly with the fix; both blockers report together; the studio mounts at `/app` when built without shadowing the API; the API stays headless when it isn't; the shipped PWA declares itself installable and its worker leaves API traffic alone.
> - Full suite: **266 passed**, run with and without a built studio (the condition that caught the JIM bug).
> - **Live-server check against the LAN address**: `/app/`, manifest, service worker, icon, and QR all serve; profile creation, interactor chat (watermark line riding on the reply), and pairing all work from that origin.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #98 — Release prep v0.1.2: version bumps, changelog cut, release notes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-release-v012` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/98>

> ## What
>
> Release mechanics for **v0.1.2 — the trust release**: universal watermarking with owner-designed marks, Terms of Service with clickwrap receipts, and signed/notarized build wiring all roll into this version.
>
> - Versions to **0.1.2** everywhere: `pyproject.toml`, FastAPI app, suite gateway, `app/` and `launcher/` package.json + lockfile root entries.
> - CHANGELOG cuts **[0.1.2] — 2026-07-24** from Unreleased (watermarking on every AI render, Terms of Service, synthetic-media credentials, macOS notarization wiring).
> - `RELEASE_NOTES.md` rewritten as the ready-to-paste v0.1.2 GitHub Release body.
>
> After merge, creating the `app-v0.1.2` tag fires the `desktop-release` workflow and builds the installers.
>
> ## Testing
>
> - Full suite: **259 passed**.
> - `python -m suite.smoke`: all 8 tandem flows `ok: true` end to end.
> - `app/` and `launcher/` front-ends build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #97 — Watermark every AI render, with owner-designed marks that always display

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-watermark-design` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/97>

> ## What
>
> Two things, both platform-wide:
>
> **1. Watermarking now runs on ALL AI-generated content — textual and visual.**
> Previously only public posts and non-text chat modalities were stamped. Now every AI render carries the verifiable synthetic-media credential:
>
> - chat replies (including proactive check-ins and sunset farewells) — stored on the message row and returned with every history render
> - community room turns
> - gaming comms lines and robot spoken lines
> - creative works (music/poem/note/lyric), proofread output, perception guidance
> - autonomous task outputs
> - posts and voice/image/video modalities (as before)
>
> Stored renders keep their `watermark_id` (new columns on `messages`, `room_messages`, `creative_works`, `tasks`), list/history endpoints return the credential with the content, and public verification is unchanged: `GET /watermarks/{id}` resolves the credential, `POST /watermarks/verify` catches altered or substituted content.
>
> **2. Custom (user-designed) watermarks, displayed at all times.**
> Every credential now carries a `display` block — the profile's watermark (mark + label) rendered as a line every surface shows alongside the content. Owners design their own via `PUT /profiles/{id}/watermark` (design read is public, since every surface must render it), with one invariant: **the AI designation cannot be designed away** — a label without "AI" is rendered with it. Default is `✦ AI · <profile name>`.
>
> **Native apps (iOS / Android / Windows):** the watermark line renders on every AI chat bubble and post card, and Settings gains a "Watermark" design editor (mark + label, live preview of the rendered line, reset to default).
>
> ## Testing
>
> - 3 new tests in `tests/test_watermark.py`: every text reply is stamped and history renders the mark (interactor turns are never watermarked); custom designs always declare AI (`🌹 AI · Dana's Garden`), design read is public, changing it requires the owner, clearing resets to default; creative works and proofreads are stamped.
> - Full suite: **259 passed**.
> - Static native checks: all XAML/SVG parse, brace/paren balance on Swift/Kotlin/C#, all `Qrme*` brushes referenced in Views are defined in App.xaml.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #96 — Terms of Service: served, accepted by clickwrap, recorded with a receipt

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-terms` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/96>

> Liability protection from the get-go.
>
> ## The agreement ([docs/terms.md](../blob/claude/qrme-terms/docs/terms.md))
>
> - Profiles are **AI-generated synthetic content** — never professional (medical/legal/financial) advice; 911/988 emergency language up front
> - **Assumption of risk and release (waiver)** covering AI personas, other users, and connected devices — except gross negligence / willful misconduct
> - **Creator responsibilities** — third-party rights basis, age/identity honesty, published content; the objection/takedown flow is contractually binding
> - **18+ terms**, as-is **warranty disclaimer**, **liability cap** (12-month fees or $100), **indemnification**, simulated-commerce notice, governing-law placeholder for counsel
>
> ## The mechanics
>
> - `GET /terms` serves the versioned agreement (version, key points, document) so every client can display it
> - Profile creation **records the accepted version + timestamp** on the profile — clickwrap with a server-side receipt — and refuses an explicit refusal (403)
> - All three native apps show the agreement on the create screen and send an explicit acceptance
>
> ## Tests
>
> `tests/test_terms.py` (2): terms served versioned with the emergency and synthetic-content points; acceptance recorded with a timestamped receipt and refusal refused.
>
> **256 tests pass**; native static checks clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #95 — Synthetic-media watermarking + macOS notarization wiring

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-watermark-signing` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/95>

> Two of the three long-deferred items land here (the BAA lands in the PDI/JIM PRs).
>
> ## Synthetic-media watermarking
>
> Generated content that leaves the platform carries a **verifiable synthetic-media credential** (`qrme/watermark.py`): every public post and every non-text chat modality (voice/image/video) is stamped at creation — watermark id, producing profile, SHA-256 of the content, issue time, and a plain-language disclosure. Verification is **public by design**: `GET /watermarks/{id}` resolves a credential with no token, and `POST /watermarks/verify` (id + content) additionally reports whether the presented content still matches the issued hash — altered or substituted media is called out, and content that merely *claims* a watermark fails the lookup. Posts keep their credential reference; pending/blocked replies are never stamped.
>
> ## macOS notarization wiring
>
> The electron-builder mac config gains `hardenedRuntime`, Gatekeeper entitlements (`app/build/entitlements.mac.plist`), and `notarize: true` — so the moment the Apple secrets exist, the release workflow produces a fully notarized, Gatekeeper-clean build. **Previously signing would run but notarization silently never happened.** `docs/releasing.md` now walks through obtaining both certificates (Apple Developer ID `.p12` + Windows OV/EV `.pfx`) and which secret each value lands in. Unsigned builds still succeed exactly as before.
>
> ## Tests
>
> `tests/test_watermark.py` (3): posts carry a resolvable credential and tampered content is caught; non-text chat modalities are stamped while plain text is not; unknown watermarks 404.
>
> **254 tests pass**; the desktop app builds clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #94 — Release prep v0.1.1: /health, version bumps, changelog & notes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-release-0.1.1` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/94>

> Everything between the `app-v0.1.0` tag (54 commits back) and now rolls into **v0.1.1**. This PR is the release mechanics:
>
> - **`GET /health`** — service liveness with tandem flags (`pdi`/`cloud`/`offline`), sibling-style; the desktop app's probe switches to it from the old `/openapi.json` workaround. +1 test (**251**).
> - **Versions to 0.1.1 everywhere** — pyproject, FastAPI app, suite gateway, `app/` and `launcher/` package.json + lockfiles.
> - **CHANGELOG** gains the full `[0.1.1]` section — native parity, steering, embodiments, marketplace economy, rated stack, rights & language, feedback, chrome l10n, CI fix — and **RELEASE_NOTES.md** is rewritten as the ready-to-paste v0.1.1 GitHub Release body.
>
> ## Verified for release
>
> 251 tests green · live-server smoke flows pass · app + launcher build clean · `python -m suite.smoke` passes end to end.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #93 — Fix CI: make the test suite collectable outside `python -m pytest`

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-ci-fix` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/93>

> Found during the full-history audit: **every CI run of the `test` job has been failing at collection** with `ModuleNotFoundError: No module named 'tests'` — while local runs passed. Two causes, both fixed:
>
> - `tests/` was not a package, so the `from tests.…` imports the suite uses only resolve when the repo root is on `sys.path` (which `python -m pytest` does and CI's bare `pytest -q` does not). `tests/__init__.py` makes the imports resolve either way, and the workflow switches to `python -m pytest -q` to match local runs.
> - `test_suite_gateway`'s skip-guard called `find_spec("jim.api")`, which **raises** `ModuleNotFoundError` when the parent package `jim` isn't installed at all — crashing collection in a qrme-only checkout instead of skipping. The guard now treats a missing parent as "not installed" (`test_suite_smoke`'s `importorskip` was already safe).
>
> JIM-mini and PDI CI are green (their test dirs were already packages); only QRME was affected. 250 tests pass locally; this PR's own CI run is the proof.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #92 — Chrome localization + polish across the native apps

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-l10n-polish` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/92>

> The apps' own frame now follows the profile's language, and the main screens refresh properly — items 3 & 4 of the backlog sweep, QRME slice.
>
> ## Localization
>
> A chrome string table (`L10n`) on each platform covers tab/nav names, the Settings title, and the most common actions in all 10 backend-supported languages (en/es/fr/de/pt/it/ja/zh/hi/ar), falling back to English per key. The chosen profile language — loaded at Settings and remembered in AppState / SharedPreferences / session.json — drives it, so picking Español relabels the iOS tab bar, the Android bottom nav, the Windows nav pane (re-applied on every pane selection so a change lands immediately), and the localized buttons. Content localization was always server-side; this closes the frame around it.
>
> ## Polish
>
> - iOS: pull-to-refresh on Overview / Posts / Settings (`.refreshable`)
> - Android: Compose `PullToRefreshBox` on Overview; sign-out button localized
> - Windows: Refresh action on Overview
>
> ## Verification
>
> No backend changes; **250 tests still pass**; native XML parse, brace balance, and brush audit clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #91 — Native round: steering hub, earnings, relationship, rated stranger tier

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-native-round` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/91>

> Four owner surfaces that existed only in the backend land on all three native clients (SwiftUI, Jetpack Compose, WinUI 3) — items 7, 8, and 10 of the backlog sweep.
>
> ## Steering (Settings)
>
> The full hub: grouped dial sliders (system/behavior; **intimacy appears only for adult-mode profiles** since the spec gates it), appearance description, base age + ages-over-time toggle, effective-age readback. One Apply call rides `PUT /profiles/{id}/steering/hub`. Steering, not piloting — the copy says so.
>
> ## Earnings (Manage/Reach → "Earn")
>
> The creator statement — accrued / paid / lifetime, per-kind breakdown, ledger entries with memos, and the Request-payout sweep (disabled at zero balance).
>
> ## Your relationship (Settings)
>
> The owner sets how the profile relates to their own interactor identity — type, nickname, tone — via `PUT /profiles/{id}/relationships/{interactor_id}`; mints the identity lazily if Chat hasn't yet.
>
> ## Rated stranger tier (Community)
>
> The tier picker replaces the "this app doesn't do age verification" cop-out. Choosing **Rated 18+** asks for a birthdate once, mints a fresh interactor identity carrying it (the server-side age wall does the checking), and remembers the identity as verified **only after the rated queue actually admits it** — a minor's birthdate still 403s and nothing is remembered. AppState persists the verified flag on every platform.
>
> Windows also gains a shared `Get(path, token)` request helper.
>
> ## Verification
>
> No backend changes; **250 tests still pass**; native XML parse, brace balance, and brush audit clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #90 — Placement earnings + PDI-sealed placement custody

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-earnings-custody` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/90>

> Two gaps in the rated-placement stack close (items 1 & 2 of the backlog sweep): venue placements now feed the creator ledger, and the placement trail is provable.
>
> ## Earnings
>
> A **verified** view arriving through a venue-placement beacon credits the creator's ledger at transaction time — kind `placement`, ref = placement id, `PLACEMENT_VIEW_RATE` per view, memo names the venue. Simulated ad/affiliate revenue, real accounting, landing in the same owner statement (`GET /profiles/{id}/earnings`) as pack sales and license fees. Walled resolutions and direct @handle summons earn nothing; free is never a money event.
>
> ## Custody
>
> When a PDI vault is configured, every rated-resolution event is **sealed into the vault** as it's recorded (`qrme/{profile}/rated/events/{id}` — kind, beacon, venue/placement attribution, timestamp). Owner-only `GET /profiles/{id}/placements/custody` lists the sealed records plus whether PDI's tamper-evident audit chain verifies intact (`PDIClient` gains `audit_verify`). Same custody standard as tandem exchanges; 409 without a vault; the local analytics row always stands even if sealing fails.
>
> ## Tests
>
> `tests/test_placement_earnings_custody.py` (4): verified venue views credit the ledger while walled/direct don't; events seal with placement attribution and custody reads back chain-intact; custody requires a vault and the owner.
>
> **250 tests pass.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #89 — Help us improve: in-app feedback anyone can send

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-feedback` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/89>

> A **"Help us improve"** section now lives in Settings on every client — send an idea, an improvement, a bug, or praise, with an optional 1–5 rating.
>
> Feedback is **private**: a submitter sees only their own submissions plus the public tally by category (how many ideas, bugs, …), so the "you're heard" loop shows without exposing anyone's words. Open to anyone — an authenticated caller's role/subject is recorded so they can find their submissions again; otherwise it's anonymous.
>
> ## Changes
>
> - `feedback` table (`id, submitter, category, message, rating, status, created_at`) + `FeedbackSubmit` model
> - `POST /feedback` validates category, non-empty message, 1–5 rating (422s); `GET /feedback` returns `{mine, tally, total, categories}` — `mine` only for the authenticated submitter, `tally` aggregate over all
> - Native UI, all in Settings, wired to submit + load: iOS `FeedbackCard`, Android `FeedbackPanel`, Windows "Help us improve" card
>
> ## Tests
>
> `tests/test_feedback.py` (4): anyone can submit and it tallies; bad category/rating/message refused; an authenticated submitter sees only their own; two users don't see each other's words.
>
> **246 tests pass.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #88 — Steering hub: unify the dials with age and appearance

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-steering-hub` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/88>

> ## Summary
>
> One owner surface for everything that shapes **how a profile comes across** — the tone/pace/manner dials, its **age**, and its **appearance** — in a single hub. The dedicated features that already own those (Avatar Studio, Aging, personality) still stand alone and stay where they're needed; the hub **composes** them, it doesn't replace them.
>
> - **Appearance** — profiles gain an `appearance` column: a look/presentation description that rides on the persona system prompt across every surface and embodiment (chat, rooms, robot speech). `build_system_prompt` appends it, robust to either a dict or a sqlite `Row` profile.
> - **`GET /profiles/{id}/steering/hub`** — returns the dials (spec + values), the age block (`base_age`, `aging_enabled`, `effective_age`), and appearance (`description` + `demographics`).
> - **`PUT /profiles/{id}/steering/hub`** — sets any subset: `values` go through the same clamps/gates (intimacy stays 18+-only), `age` fills the gap the existing `PATCH /profiles` left (setting `base_age` post-creation), and `appearance` is new. Negative age → 422; owner-only.
> - The standalone `/steering` dials endpoints are unchanged and still work — the hub reads/writes the same storage.
> - **Screen 66 · Steering** now shows the hub (dials + appearance + age); README steering row documents it.
>
> ## Tests
>
> `tests/test_steering_hub.py` (6): the hub gathers all three sections; setting every section with each one riding the persona prompt (dials directive, appearance line, age line); partial update leaving the rest untouched; the intimacy gate holding on a non-adult profile; bad-age 422 + owner-only; and the standalone dials endpoint still working alongside the hub.
>
> **242 passed** (236 existing + 6 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #87 — Steering: the owner shapes tone/pace/manner — not piloting

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-steering` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/87>

> ## Summary
>
> Renames the feature to **steering** — the vocabulary you asked for. Steering is the owner shaping *how a profile / agent / robot comes across* (tone, voice, pace, manner). It shapes presentation; it does **not** remote-operate the entity — the entity still acts on its own within its embodiments. That's the line: **steering, not piloting**. All the controls are kept exactly as they are; only the framing and naming move.
>
> Pure rename + reword, **no behavior change**:
>
> - **Files** — `qrme/dials.py` → `qrme/steering.py`; `qrme/routers/dials.py` → `qrme/routers/steering.py`; `tests/test_dials.py` → `tests/test_steering.py` (git renames).
> - **API** — `/profiles|robots/{id}/dials` → `/steering`; `DialsSet` → `SteeringSet`; route fns `get_/set_profile_steering`, `get_/set_robot_steering`.
> - **Schema** — table `dial_settings` → `steering_settings`.
> - **Prompt** — directive head *"How you're currently dialed in…"* → *"Your current steering — how you're set to come across…"*.
> - **Watch** — throttle read-out points at `PUT /profiles/{id}/steering`.
> - **Screen** — 66 · Dials → **66 · Steering** (old SVGs removed, regenerated); README feature row + gallery cell.
>
> The individual sliders are still called **dials** (a steering control is a dial): system (`pace`/`autonomy`/`verbosity`), behavior (`warmth`/`formality`/`humor`/`assertiveness`), and the **18+-only `intimacy`** dial — all unchanged, still age-gated and boundary-bound, shaping style/pace/behavior only.
>
> ## Tests
>
> `tests/test_steering.py` (6, renamed): neutral defaults staying silent, sliders shaping the prompt with clamping, the 18+-only intimacy dial, robot dials → behavior profile, the live watch throttle, and owner-only access.
>
> **236 passed.** The only remaining "piloting" strings are the deliberate *"steering, not piloting"* contrasts that explain the distinction.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #86 — Dials: drop the "pilot" framing, keep the throttle/behavior/intimacy dials

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-dials-rename` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/86>

> ## Summary
>
> Same functionality, reframed. The throttle, behavior, and intimacy dials stay exactly as they are — but they're no longer "piloting." They're a profile's / robot's **disposition** (how it's tuned, part of who it is), not an owner remote-controlling it. The entity acts on its own within its embodiments; the dials describe its temperament.
>
> This is a pure rename + reword — **no behavior change**:
>
> - **Files** — `qrme/pilot.py` → `qrme/dials.py`; `qrme/routers/pilot.py` → `qrme/routers/dials.py`; `tests/test_pilot_controls.py` → `tests/test_dials.py` (all tracked as git renames).
> - **API** — `/profiles/{id}/pilot` → `/profiles/{id}/dials` and `/robots/{id}/pilot` → `/robots/{id}/dials`; `PilotSet` → `DialsSet`; route fns `get_/set_profile_dials`, `get_/set_robot_dials`.
> - **Schema** — table `pilot_controls` → `dial_settings`.
> - **Prompt** — the persona directive head reworded from *"Pilot settings from your owner — adjust…"* to *"How you're currently dialed in — let this shape…"* (disposition, not a remote control).
> - **Watch** — the throttle read-out now points at `PUT /profiles/{id}/dials`.
> - **Screen** — 66 · Pilot Controls → **66 · Dials** (old SVGs removed, regenerated); README feature row + gallery cell reworded off "pilot."
>
> The dials themselves are untouched: system (`pace`/`autonomy`/`verbosity`), behavior (`warmth`/`formality`/`humor`/`assertiveness`), and the **18+-only `intimacy`** dial — all still age-gated, boundary-bound, and shaping style/pace/behavior only, never identity, boundaries, age-gating, or the command allowlist.
>
> ## Tests
>
> `tests/test_dials.py` (6, renamed): neutral defaults staying silent, sliders shaping the prompt with clamping, the 18+-only intimacy dial, robot dials → behavior profile, the live watch throttle, and owner-only access.
>
> **236 passed.** The only remaining "pilot" strings in the tree are "Microsoft Copilot" and the aerospace "former test pilot" persona — both unrelated.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #85 — Smart-glasses connectors + agent-operated gaming companions

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-glasses-gaming` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/85>

> ## Summary
>
> Two device-and-play features, both built on QRME's existing connector and persona machinery.
>
> ### Smart glasses — capture the POV, render to the lens
> The connector catalog gains a **`glasses`** provider: **Ray-Ban Meta**, **Meta Ray-Ban Display**, **Google (Android XR)**, **XREAL Air**. `collect` pulls the wearer's point of view (camera, audio, context) in as source material; `produce` renders back to the lens — a HUD caption/overlay, live-translation, or navigation the persona speaks/draws. Because it reuses the existing connect / collect / invoke app-connector flow, the native **Apps** picker (which is catalog-driven) already lists them — no new native code needed.
>
> ### Gaming companions — a profile plays alongside real players
> - The catalog also gains a **`gaming`** provider (PlayStation · Xbox · Switch · Steam · PC) for capturing play and producing highlights.
> - **`qrme/routers/gaming.py`** — `POST /profiles/{id}/gaming/sessions` brings a profile into a game as a **companion**, **teammate**, or **practice partner**; `POST /gaming/sessions/{sid}/callout` generates its next in-character comms line (callout · coordination · banter) through the persona and runs it through moderation — team comms is a public surface, so **a minor in the lobby forces strict**; plus list + end.
> - **Fair play is a system rule, not a toggle** — the `FAIR_PLAY` directive is baked into every callout prompt: the companion plays within the game's rules and never claims, offers, or uses cheats/exploits/automation. The pilot dials shape *how* it talks, never whether it plays fair.
> - **Native** — a Gaming surface in all three apps (iOS `ManageView` tab, Android Manage `TabRow`, Windows nav page): start a session, feed it the situation, see the moderated line (or the held reason), end.
>
> **Screens/docs** — gallery screens **67 · Smart Glasses** and **68 · Gaming Companion** (136 SVGs regenerate clean); README connector rows + gallery cells.
>
> ## Tests
>
> `tests/test_glasses_gaming.py` (7): glasses in the catalog with capture+render directions; connect → collect → invoke through a glasses connector; gaming platforms present; a companion starting and calling out in character with chat-grade provenance; the minor-in-lobby strict path; ended-session 409; and owner-only gating. The existing catalog-count test is updated to 6 providers.
>
> **236 passed** (228 existing + 8 new, minus the merged catalog assertions); native XAML/SVG parse, brace balance, and brush audit clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #84 — Suite smoke: one command proves the whole tandem stack

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-suite-smoke` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/84>

> ## Summary
>
> `python -m suite.smoke` — the parked cross-product health check, delivered. It boots **QRME, JIM-mini, and PDI in-process** (TestClient, no ports, no network), seeds everything, wires the tandems, and drives one live end-to-end exchange:
>
> 1. **PDI** comes up: starter vault seeded, JIM issued its tenancy.
> 2. **QRME** seeded: 33 starter profiles, 38 packs, both federated registries synced.
> 3. **JIM** boots in tandem with both siblings (`/health`: `tandem: true, pdi: true`), seeds its specialists, and links all **5 tandem pairs** by @handle.
> 4. A user's financial-stress detection routes to the QRME starter specialist **@marcus_bell** ("Marcus Bell — retired fee-only financial planner"), and the exchange is **sealed in the PDI vault**.
> 5. The sealed exchange's provenance is read back through JIM's custody window: origin *JIM Guardian*, **hash chain intact**.
>
> Prints a JSON report of every step; exit 0 = the suite is green. A missing sibling package is reported (not crashed on), matching the suite gateway's optional-import behavior, and `tests/test_suite_smoke.py` runs the same check under pytest — skipping cleanly when the siblings aren't installed.
>
> Verified live in this environment: all 7 steps green against the real current mains of all three products.
>
> ## Tests
>
> **229 passed** (228 existing + the smoke test).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #83 — Pilot controls: live throttles and behavior sliders

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-pilot-controls` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/83>

> ## Summary
>
> Owners can **pilot** what they run — agents, synthetic profiles, and robots — with 0–100 dials (50 = as written) that shape style, pace, and manner, never identity or safety:
>
> - **system** — `pace` (the throttle: unhurried ⟷ eager), `autonomy` (checks first ⟷ acts alone), `verbosity`;
> - **behavior** — `warmth`, `formality`, `humor`, `assertiveness`;
> - **intimacy** — an **18+-only** dial, present and effective *only* on an adult-mode profile (hard-clamped to 0 everywhere else) and, even at full, raising flirtation/affection **within the persona's stated boundaries and the strict moderation every public surface runs** — never explicit content on demand.
>
> The dials ride on the persona system prompt (`pilot.directive()`), so chat, compose, rooms, and robot speech all inherit them; near-default dials say nothing. A robot reads `pace`/`autonomy`/`assertiveness` as a motion **behavior profile** (advisory for the vendor bridge — it never widens the command allowlist). `GET`/`PUT /profiles/{id}/pilot` and `/robots/{id}/pilot` are owner-only, and the watch face carries the live pace+autonomy throttle read-out.
>
> The dials never override boundaries, age-gating, or the command allowlist — they are style/pace/behavior only.
>
> **Screens/docs** — gallery screen **66 · Pilot Controls** (132 SVGs regenerate clean) + README feature row.
>
> ## Tests
>
> `tests/test_pilot_controls.py` (6): neutral defaults staying silent in the prompt, sliders shaping the prompt with range clamping, the 18+-only intimacy dial (absent + clamped off on a non-adult profile; present + effective within boundaries on an adult-mode one), robot dials mapping to a behavior profile independent of the profile's, the live watch throttle, and owner-only access.
>
> **228 passed** (222 existing + 6 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #82 — Watch remote: agents, profile, and robots on the wrist

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-watch-remote` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/82>

> ## Summary
>
> The watch becomes an **extension and remote** for everything the owner runs — agents, the synthetic profile, and robot bodies.
>
> **The glanceable face** — owner-only `GET /profiles/{id}/watch`:
> - every agent (workflow) with a status light — **green = working**, **orange = needing assistance** (paused, awaiting input), **red = stopped** (failed/cancelled), *done* when finished — plus its current phase and what a paused one is waiting for;
> - the profile chip: orange when replies are held for owner approval, red when the profile is restricted;
> - each robot with its light (active / docked / offline), the wrist's **quick-command ring** (come here · patrol · dock · stop, filtered by the body's allowlist) and its learned task-pack verbs;
> - a working / needing-assistance / stopped summary, and `haptic: alert` whenever anything is orange or red — the wrist taps the owner.
>
> **The remote** — `POST /profiles/{id}/watch/act` runs one action from the wrist: advance / **assist** (with the asked-for input) / cancel an agent, approve / reject a held reply, or command a robot. Every action reuses the exact routes the full apps use (`workflows.advance/resume/cancel`, moderation approve/reject, `command_robot`) — same auth, same allowlists, same moderation. **The wrist adds no new powers, only reach.**
>
> **Screens/docs** — gallery screen **65 · Watch Remote** (130 SVGs regenerate clean) + README feature row.
>
> ## Tests
>
> `tests/test_watch_remote.py` (4): the full light lifecycle (green → orange with haptic on the confirm pause → 422 assist without input → assist → done; cancel → red with stopped count), the robot quick ring with status flips and learned-task execution (unknown verbs still refused from the wrist), the pending-approval orange chip clearing on approve, and owner-only access.
>
> **222 passed** (218 existing + 4 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #81 — Creator ledger: one statement for everything a creator earns

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-creator-ledger` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/81>

> ## Summary
>
> Every priced sale on the marketplace now writes a ledger entry **at transaction time**, attributed to the earning creator's `owner_id` — so a creator's statement is a record, not a reconstruction:
>
> - **Pack sales** (knowledge, robot task, and rated packs alike) credit the pack's new `publisher_owner_id`: starter packs accrue to `qrme-starter`, **federated registry sales accrue to the registry key** — Robotmods.net / LLMmods.com partner earnings live in the same ledger — and published packs accrue to whoever the publisher names.
> - **License fees** credit the source profile's owner at acquisition, with a memo carrying the license kind and persona.
> - **Free downloads are never money events** — `credit()` refuses zero amounts.
>
> **API** (`qrme/ledger.py` + `qrme/routers/earnings.py`, owner-only):
> - `GET /profiles/{id}/earnings` — every entry newest-first, plus accrued / paid / lifetime totals and a per-kind breakdown.
> - `POST /profiles/{id}/earnings/payout` — sweeps the accrued balance into a payout (simulated transfer, real accounting), stamping every entry with the payout id; **409 on an empty balance** — a payout of nothing is not a payout.
>
> **Screens/docs** — gallery screen **64 · Creator Payouts** (128 SVGs regenerate clean) + README feature row.
>
> ## Tests
>
> `tests/test_creator_ledger.py` (6): pack-sale accrual with the free-download non-event, license-fee accrual with memo, the payout sweep (totals move accrued→paid, entries stamped, empty-balance 409), rated commerce landing in the same ledger, registry sales accruing to `llmmods`, and owner-only access.
>
> **218 passed** (212 existing + 6 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #80 — Placement analytics: what each adult venue earns

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-placement-analytics` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/80>

> ## Summary
>
> Per-venue performance for rated placements (#78), owner-only and privacy-preserving:
>
> - **Event trail** (`rated_events`) — every resolution of a rated profile on a discovery surface is logged as *walled* or *verified_view*, attributed to its beacon (NULL = a direct @handle summon). Only the outcome and the beacon are stored — **never the viewer** — and ordinary (non-rated) profiles leave no trail at all.
> - **`GET /profiles/{id}/placements/analytics`** (owner-only) — per-venue scan counts split walled vs. verified with a **daily trend**, direct-ref resolutions as their own row, and the profile **funnel**: resolutions → verified views → unique chatters, with `verified_rate` and `chat_rate` — so a creator sees which venue actually converts, not just which one gets scanned.
> - **Screens/docs** — gallery screen **63 · Placement Analytics** (126 SVGs regenerate clean) + README feature row.
>
> ## Tests
>
> `tests/test_placement_analytics.py` (4): the full funnel with rates (2 anonymous walls + 1 verified scan + 1 direct wall + 1 chat → `verified_rate 0.25`, `chat_rate 1.0`), per-venue splits across OnlyFans/Fansly placements, owner-only access plus the empty unmarketed shape, and the no-trail guarantee for non-rated profiles.
>
> **212 passed** (208 existing + 4 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #79 — Rated commerce: the age wall covers buying, not just viewing

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-rated-commerce` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/79>

> ## Summary
>
> Extends the 18+ wall from discovery (#78) to **transactions**:
>
> - **Rated packs** — packs gain a `rated` flag. Rated packs are omitted from the `/packs` catalog and 403-walled at detail unless the caller is age-verified: a verified-18+ interactor, **or the owner of an adult-mode profile** (`rated.buyer_is_adult` — adult-mode ownership proved 18+ at creation). A rated pack installs **only onto adult-mode profiles**, with the usual explicit `accept_price` consent on top.
> - **Rated licensing** — a rated profile's license *offer* is itself age-gated (the shop window, not just the sale), and acquiring the license requires a verified-18+ buyer — a minor's interactor token is refused with a clear reason.
> - **Starter rated pack** — *After Dark Companion Pack* ($6.99): consent-forward conversational craft for adult-mode personas ("a 'no' or a pause is a full answer"; boundaries stated out loud) — never explicit content, and deliberately **never listed on the open marketplace**: the age-gated `/packs` catalog is its only door.
>
> ## Tests
>
> `tests/test_rated_commerce.py` (6): catalog invisibility for anonymous / minor / non-adult-owner callers vs. visibility for verified adults and adult-mode owners; detail walling; no open-marketplace listing; install refusal on regular profiles plus the full 402 → purchase onto an adult-mode profile; license-offer gating; acquisition gating; and the consent-forward content guarantee. Seed totals updated in the existing pack tests.
>
> **208 passed** (202 existing + 6 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #78 — Rated placement: market 18+ profiles at adult venues, walled at the source

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-rated-placement` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/78>

> ## Summary
>
> Adult-mode profiles — already creatable only by a **verified-adult owner** and chat-gated to **verified-adult interactors** — can now be *marketed* where adult audiences actually are, without the age gate ever leaving QRME's hands.
>
> - **Venues** (`qrme/rated.py`) — a structural catalog (same pattern as the connected-apps and pack-registry catalogs) of venues willing to host rated profiles or their beacons: OnlyFans and Fansly (`profile` + `beacon` hosting) and x-rated site directories (`beacon`). `GET /venues`.
> - **Placements** — `POST /profiles/{id}/placements` (owner-only, adult-mode required) mints a printable/embeddable **QR beacon** for the venue and returns the **@handle / #tag** refs to publish there; `GET` lists placements with live scan counts; `DELETE` withdraws — the beacon stops summoning (410).
> - **The wall travels with the profile, not the venue.** Every discovery surface now resolves rated profiles through the age wall: `@handle` and beacon scans answer with a wall card (existence acknowledged, no name, no chat path); `#tag` browse and marketplace listings **omit** rated profiles entirely (a list is not a direct ref); only a viewer presenting an interactor token with a **verified 18+ birthdate** gets the real card, labeled `rated: true`. Minors with tokens hit the same wall as anonymous viewers.
> - **Hard line at creation** — adult mode is *never* available for a profile of another real person (`kind: other_person` → 403); only `self` (the verified adult owner themself) or `fictional` personas.
> - **Native apps unchanged by design** — they carry no rated surfaces, since there is no in-app 18+ identity verification; the README documents this explicitly.
>
> **Screens/docs** — new gallery screen **62 · Rated Placement** (124 SVGs regenerate clean) + README feature row.
>
> ## Tests
>
> `tests/test_rated_placement.py` (8): the other-real-person refusal, the venue catalog, placement minting with QR + wall-resolved scan counting, the adult-mode requirement, the wall on every ref for anonymous **and minor** viewers vs. the full card for verified adults, tag-browse and marketplace omission, and placement withdrawal killing the beacon.
>
> **202 passed** (194 existing + 8 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #77 — Pack registries: Robotmods.net and LLMmods.com on the marketplace

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-pack-registries` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/77>

> ## Summary
>
> Two federated mod storefronts now publish into the marketplace alongside the local starter collection (represented structurally — the same pattern as the connected-apps catalog; a live deployment would fetch each registry's feed):
>
> - **Robotmods.net** — task mods for robot bodies: *Pet Care Mod* (free; never free-feed, report rather than improvise, stop on animal stress) and *Workshop Assistant Mod* ($4.99; power tools are never touched, never hold the workpiece under a running tool).
> - **LLMmods.com** — knowledge mods for LLM personas: *Negotiation Mod* (free) and *Public Speaking Mod* ($3.49).
>
> **Federation mechanics** (`qrme/pack_sources.py`): `GET /packs/registries` lists both sources with sync state; `POST /packs/registries/{key}/sync` imports a registry's catalog idempotently as ordinary knowledge packs with `origin`/`origin_url` on the label and a marketplace listing under the registry tag. Once synced, nothing is special-cased: same buy/download flow (priced mods keep the 402 → `accept_price` consent), same capability checks for robot mods, same provenance counting, same uninstall/revocation.
>
> **Native (all three apps)** — the Packs surface gains a **Pack sources** card listing both storefronts with taglines, per-registry sync state (`n/m packs synced`), and one-tap Sync; every federated pack card shows "from robotmods.net" / "from llmmods.com".
>
> **Screens/docs** — new gallery screen **61 · Pack Registries** (both phone platforms, 122 SVGs regenerate clean); README feature row; `native/README.md` endpoint map updated.
>
> ## Tests
>
> `tests/test_pack_registries.py`: registry listing with sync state, idempotent import with origin/marketplace tagging + unknown-registry 404, Pet Care Mod installing and commanding on a NEO with its procedure audited, the priced Workshop/Public Speaking consent flows, Negotiation Mod grounding chat provenance (`by_kind.pack: 3`), and the workshop safety lines.
>
> **194 passed** (189 existing + 5 new); XAML/brace/brush statics clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #76 — Docs: screens and module map for packs, robot mods, and embodiment

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-screens-docs` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/76>

> ## Summary
>
> The README's screen gallery and architecture notes had fallen behind the code — knowledge packs (#74), robot task packs (#75), the embodied-agent flow, and the native Packs surfaces all existed with no documentation trail. This PR closes the gap:
>
> **New screens** (`docs/screens/`, hand-built SVG, both phone platforms — 120 total regenerate clean):
> - **57 · Knowledge Packs** — the download/buy shop: free Field Packs vs. priced packs with explicit accept, install grows the source material, provenance counts `grounded_in.by_kind: pack`.
> - **58 · Robot Task Packs** — task mods for the body a profile embodies: capability-checked install (a vacuum is never sold manipulation), allowlist extended not opened, every task audited with its procedure.
> - **59 · Embodied Agent** — same identity in the body, learned modules in the `say` prompt, `GET /robots/{id}/skills`, instantly revocable.
> - **60 · Publish a Pack** — creators bundle knowledge items or task modules, free or priced, listed under `#pack`.
>
> **README** — gallery section for 57–60; the Architecture section gains a marketplace-expertise module map (`qrme/packs.py`, `qrme/routers/packs.py`, `qrme/seed.py`, `qrme/robotics.py`, `qrme/routers/robots.py`) and a pointer to the native clients.
>
> **native/README.md** — the screen-by-screen endpoint map now covers the Packs shop (knowledge + robot task install/revoke flows), language & translate settings, and the wellbeing quick-browse chips.
>
> ## Verification
>
> All 120 SVGs parse as XML; **189 tests pass** (docs-only change).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #75 — Robot task packs: marketplace modules for the bodies profiles embody

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-robot-packs` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/75>

> ## Summary
>
> Knowledge packs (#74) gain an **audience**: `profile` packs ground the persona (unchanged), and new **`robot` packs carry task modules for the body a profile embodies** — the AI agent's robot learns purchasable skills from the marketplace. Each module is a new commandable verb with the capabilities it requires and the procedure the embodied agent follows.
>
> The safety model is the existing one, extended rather than opened:
> - **Capability-checked install** — a robot pack installs onto a specific bound robot (`robot_id`) and every module's `requires` list is checked against the robotics catalog: a vacuum is never sold a manipulation task, and a task may never shadow a built-in command.
> - **Allowlist semantics preserved** — installed tasks extend exactly that robot's command allowlist; unknown verbs are still refused, and every execution lands in the `robot_commands` audit trail with the pack's procedure in the result.
> - **Revocable** — `DELETE /robots/{id}/packs/{pack_id}` removes the tasks immediately; `GET /robots/{id}/skills` lists what a body has learned; the embodied persona's `say` prompt knows its body's learned modules.
>
> **Starter robot packs** (seeded with the rest): *Household Tasks*, *Care Assistance* (reminders never dispense medication, escort is never physical support), and *Sentry Patrol* (report, never intervene) free; *Culinary Assistant* priced (never knives or hot cookware) exercising the buy flow.
>
> **Backend**: `audience` on `knowledge_packs`, `task`/`requires` on `pack_items`, new `robot_skills` table, per-robot `pack_installs` rows; install branches by audience with strict cross-audience validation; `command_robot` consults installed skills.
>
> **Native**: all three Packs screens show a 🤖 ROBOT badge, install onto the profile's bound body (with a clear bind-a-robot-first error), and revoke through the robot route.
>
> ## Tests
>
> `tests/test_robot_packs.py`: task teaching end-to-end (refused before install, queued with procedure after, audited, unknown verbs still refused), capability protection (household pack refused on a vacuum, sentry pack fits), priced-pack 402→consent flow, strict audience routing, uninstall revocation with reinstall, and the care pack's safety lines. Existing pack tests updated for the larger seed.
>
> **189 passed** (183 existing + 6 new); native XAML/brace/brush statics clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #74 — Knowledge packs: downloadable expertise clusters on the marketplace

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-knowledge-packs` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/74>

> ## Summary
>
> A **knowledge pack** is a downloadable cluster of curated expertise for one industry, bought (or downloaded free) on the marketplace and installed onto a profile to make it professionally smarter. The mechanism is real, not cosmetic: installing copies the pack's items into the profile's **source material** (vaulted in PDI when configured), so the persona's system-prompt knowledge base genuinely grows — and every reply's provenance counts the `pack` grounding honestly. Uninstalling shrinks it back and clears the vaulted copies.
>
> **Backend**
> - `qrme/packs.py` — `STARTER_PACKS`: a free *Field Pack* for **all 33 starter industries** (3+ curated practitioner items each; the wellbeing packs keep the 988 care line, cybersecurity stays defensive-only). Idempotent `seed()` (`python -m qrme.packs` / `POST /packs/seed`) that also lists each pack on the marketplace under the `pack` tag.
> - `qrme/routers/packs.py` — `GET /packs` catalog (+industry filter) and `GET /packs/{id}` detail showing item **titles only** (the shop window; contents are the product), `POST /packs` to publish free or priced packs, `POST /packs/{id}/install` (owner-gated; a priced pack without explicit `accept_price` → **402**, payment simulated like licensing), `GET /profiles/{id}/packs`, and `DELETE` uninstall.
> - Schema: `knowledge_packs` / `pack_items` / `pack_installs`; `source_items` gains `pack_id` so uninstall removes exactly what a pack added.
>
> **Native (all three apps)**
> - **iOS** — new *Packs* tab in Manage (`PacksView.swift`): browse with industry filter, FREE/price badge, Download / Buy button (the priced tap is the `accept_price` consent), installed state, Remove.
> - **Android** — `PacksPanel` behind the same *Packs* tab in the Reach screen.
> - **Windows** — a *Packs* pivot on `ReachPage` with the same flow; `App.xaml` gains the **missing `QrmeRedBrush`** (already referenced by three existing pages) plus `QrmeT3Brush`/`QrmeAmberBrush`.
>
> ## Tests
>
> `tests/test_knowledge_packs.py`: full industry coverage, seed + marketplace listing + idempotency, free install growing the knowledge base end-to-end (source items, system prompt carries pack content, chat provenance `by_kind.pack`), priced-pack 402→purchase flow with recorded `price_paid`, uninstall shrinking back, wellbeing care-line guarantees, and owner gating.
>
> **183 passed** (176 existing + 7 new). Native statics clean — including a new audit that every `StaticResource` brush referenced by a view is defined.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #73 — Native marketplace browse: surface the wellbeing starters

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-native-trio` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/73>

> ## Summary
>
> The mental-health trio (#72) landed on the marketplace, but the native apps only offered a blank free-text tag filter to find them. All three clients now show a **Wellbeing & quick browse** card in the Market section:
>
> - **One-tap tag chips** — `#mental-health`, `#mood`, `#relationships` first, then popular areas (`#healthcare`, `#finance`, `#fitness`, `#food`). Tapping a chip fills the filter and reloads the listings, so the trio (and the rest of the starter collection) is one tap away instead of requiring users to guess tag names.
> - **An honest supportive-care note** — the wellbeing starters offer education and support, never a substitute for professional care; in crisis, call or text 988.
>
> Per platform: iOS gets a horizontal chip row with selected-state styling in `ManageView`'s Market section; Android mirrors it in `MarketPanel` via a `horizontalScroll` row over a shared `QUICK_TAGS` constant; Windows populates a chip `ItemsControl` on `ReachPage` from `QuickBrowseTags`, each chip filling `FilterTagBox` and reloading.
>
> ## Verification
>
> Static only (no native toolchains in this environment): all `.xaml` parse as XML; brace/paren balance clean across `.swift`/`.kt`/`.cs`. Backend untouched — **176 tests pass**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #72 — Starter collection: mental-health trio for the JIM tandem hookup

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-mental-health-starters` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/72>

> ## Summary
>
> Three new starter personas (30 → 33) carrying the same named experts JIM-mini's Guardian registers as starter specialists, so its tandem hookup can route the mental-health conditions through live synthetic personas:
>
> - **`@dr_lena_whitcomb`** (mental_health) — clinical psychologist, anxiety & panic. Evidence-based steadying techniques (paced breathing, grounding, gentle exposure) framed as education and support, never diagnosis; points to a licensed clinician or 988 when distress runs deep.
> - **`@dr_marcus_adeyemi`** (psychiatry) — psychiatrist, mood disorders. Plain that he cannot prescribe or diagnose here; treats any mention of self-harm as the moment to reach 988 or local emergency services.
> - **`@dr_priya_nair`** (counseling) — family & couples therapist. Communication tools and perspective, not verdicts on who is right; recommends a licensed couples therapist for patterns deeper than a conversation.
>
> All three are `companion_coach` purpose, run the same moderation and provenance pipeline as every profile, and are summonable by `@handle` — the stable cross-product name the JIM hookup resolves. A follow-up JIM PR extends `TANDEM_HANDLES` to these three.
>
> ## Tests
>
> `test_mental_health_trio_is_summonable_for_the_jim_tandem`: each handle summons to the right profile with chat reachable, and the `mental-health` tag browse surfaces the trio. Existing starter tests (uniqueness, idempotency, marketplace population) cover the additions dynamically.
>
> **176 passed** (175 existing + 1 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #71 — Starter collection: one synthetic profile per industry, seeded on the marketplace

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-starter-profiles` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/71>

> Solves the marketplace cold start: a fresh QRME deployment now seeds **30 curated synthetic experts — one per industry** — so users have profiles to immerse with before anyone publishes their own.
>
> ## The collection
>
> One crafted persona per industry: healthcare (Dr. Amara Osei), finance (Marcus Bell), technology (Priya Raman), education, legal, agriculture, manufacturing, construction, real estate, energy, transportation & logistics, retail, hospitality, media, arts & design, sports & fitness, culinary, environment & climate, government & civic, nonprofit, science, telecom, insurance, automotive, aerospace, fashion & beauty, marketing, cybersecurity (defensive-only by persona), HR, and music. Each persona is written to be genuinely useful to talk to, with in-character guardrails where the domain needs them (the physician distinguishes education from medical advice, the attorney says when to hire a real lawyer, the financial planner teaches concepts, never picks).
>
> ## How they're wired in
>
> - **Both marketplace surfaces**: the generalized `listings` (browse + tag filter, visible in the native Market screens) *and* the profile `marketplace` table that powers `#tag` summoning — so `#healthcare` summons Dr. Osei and `@chef_henri_laurent` resolves directly.
> - **Claimed `@handle`** per starter for direct summoning.
> - **Full immersion path already works**: chat requires only an interactor identity, so visitors converse with starters through the same moderation pipeline and get the same provenance block (model, persona grounding, disclaimer) as with any user profile.
> - All starters are `fictional` kind (no real-person rights involved), owned by `qrme-starter`.
>
> ## Seeding
>
> `POST /marketplace/seed` or `python -m qrme.seed` — **idempotent** (a starter whose handle is already claimed is skipped), so it's safe to run at every deploy.
>
> ## Verification
>
> - 5 new tests: industry/handle uniqueness with ≥30 coverage, marketplace population + tag browse, idempotency (no duplicate listings), @handle and #tag summoning, and an end-to-end visitor chat with provenance.
> - Full suite: **175 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #70 — Language at the create-profile gateway, translate-anything tool, and modes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-translate-gateway` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/70>

> QRME's version of the setup-gateway + translate round:
>
> ## 1. Language at the setup gateway
>
> `POST /profiles` accepts a `language`, applied before the profile's very first reply — a persona created as Spanish-speaking speaks Spanish from turn one. All three native create-profile screens gain the picker.
>
> ## 2. Translate anything (`POST /profiles/{id}/translate`, owner-gated)
>
> Anything the owner runs across — an interactor's message, a room turn, a marketplace listing — translates into the profile's language (or an explicit `to` target) using **the profile's own model**; the offline stub returns `engine: "stub"` with an honest note instead of a fake translation. A Translate tool joins the language card in every client's Settings.
>
> ## 3. Delivery mode
>
> The language preference now carries a `mode`: **`pre`** (default — the persona speaks the language natively everywhere via the system-prompt directive) or **`on_demand`** (the persona keeps its original voice; the owner translates selectively). The persona prompt and the provenance `language` metadata both honor it; a "Speak it natively" toggle rides on every client's language card.
>
> ## Verification
>
> - 4 new tests: gateway creation with language, unknown-language rejection, mode round-trip on the persona prompt, and translate-tool stub honesty + auth/target validation.
> - Full suite: **170 passed**. XAML parses clean; brace/paren balance passes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #69 — Per-profile language + content provenance

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-language-provenance` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/69>

> Ports JIM's language + provenance guarantees to QRME, mapped to what QRME actually produces: persona-generated content.
>
> ## Language (`/languages`, `GET/PUT /profiles/{id}/language`)
>
> A profile speaks its owner-set language **everywhere it appears**. The directive rides on `persona.build_system_prompt` — the single point every generation surface flows through — so chat replies, composed posts, room turns, and robot speech all generate natively in-language with no per-endpoint plumbing. Ten languages; owner-only setting, stored like the model preference; picker added to the Settings screen on all three native clients.
>
> ## Provenance (on every chat reply and composed post)
>
> QRME's content is a character speaking, so its provenance is the **derivation trail of the persona**, not medical citations:
>
> - `generated_by` — the exact model that produced the text.
> - `grounded_in` — the profile's core identity plus a count of the consented source items (by kind) that fed the generation.
> - `licensed_from` — lineage when the profile is a licensed derivative, so derived agents are always traceable to their source.
> - `moderation` — the maturity level and verdict the content passed through before delivery.
> - A disclaimer that this is a synthetic persona speaking, not a verified factual source.
>
> All three native clients render the trail under chat replies (a compact ⓘ line) and composed posts (full footer with lineage and disclaimer).
>
> ## Verification
>
> - 4 new tests: language catalog/choice/validation, the directive riding on the persona prompt, chat provenance shape, and compose grounding counts.
> - Full suite: **166 passed**. XAML parses clean; brace/paren balance passes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #68 — Native apps: add Reach (summon @handle + QR beacons, marketplace, licensing)

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-native-reach` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/68>

> Lands the last owner-facing routers — `summon.py`, the marketplace half of `community.py`, and `licensing.py` — in all three native clients, completing owner-facing parity for QRME.
>
> ## What's included
>
> - **Summon** — claim the profile's unique `@handle` (`PUT /profiles/{id}/handle`), place QR beacons ("leave the profile behind" somewhere physical) with scan counts and pick-up (`/profiles/{id}/beacons`, `DELETE /beacons/{bid}`), and a try-a-summon box that resolves `@handle` / `#tag` / beacon references through `GET /summon` and renders the public discovery card(s).
> - **Market** — list the profile on the marketplace (title, blurb, tags — which also makes it `#tag`-summonable), browse with a tag filter, and remove your own listing (`/marketplace/listings`).
> - **License** — offer the profile's expertise as consult / finetune / clone with price and terms (`PUT /profiles/{id}/license`), see who holds grants with any derived-agent provenance (`GET /profiles/{id}/licenses`), revoke a grant (`DELETE /licenses/{gid}`), or unlist. **Buyer-side acquire/derive is deliberately excluded**: it requires a verified (18+) interactor identity that the apps' anonymous interactor doesn't carry — the UI explains this, matching how the stranger rated tier was handled.
>
> ## Per platform
>
> - **iOS (SwiftUI)**: the Settings tab becomes a segmented **Manage** tab (General / Summon / Market / License) via the new `ManageView`, reusing `SettingsView` for General; new models (`HandleClaim`, `Beacon`, `SummonResult`, `Listing`, `LicenseOffer`, `LicenseGrant`, …) and thirteen endpoints on `ApiClient`.
> - **Android (Compose)**: `ManageScreen` with a four-tab `TabRow` wrapping the existing `SettingsScreen` plus `SummonPanel` / `MarketPanel` / `LicensePanel`; matching models and methods; bottom-bar label Settings → Manage.
> - **Windows (WinUI 3)**: new `ReachPage` (Summon / Market / License Pivot) and a Reach sidebar item; the flat Settings page stays as-is.
> - READMEs updated: the apps now cover the full owner-facing router surface, with the remaining exclusions (rated tier, buyer acquire/derive, provider directory/handoffs) documented as deliberate.
>
> ## Verification
>
> - All XAML parses clean (`xml.dom.minidom`).
> - Brace/paren balance checks pass on the new Swift/Kotlin/C#.
> - Backend untouched: 162 pytest tests pass.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #67 — Native apps: add Community (stranger matchmaking + multiparty rooms)

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/qrme-native-community` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/67>

> Widens the Chat surface on all three native clients to cover the community routers — anonymous stranger connections (`qrme/routers/connections.py`) and multiparty rooms (`qrme/routers/community.py`).
>
> ## What's included
>
> - **Stranger** — anonymous, consent-first friendly matchmaking: join the queue with an optional alias (`POST /connections/join`), converse once matched (send + refresh via the interactor-scoped messages endpoints), see your own blocked messages flagged ("blocked — only you can see this"), and end the connection from either side. The **rated tier is deliberately not offered** — it requires 18+ age verification, which the apps' lazily-minted interactor identity doesn't carry; the UI says so.
> - **Rooms** — a group chat with you and your profile (`POST /rooms` with user + profile participants): sending a message triggers each profile participant's moderated turn, and a "Let them talk" button drives the unprompted `POST /rooms/{id}/advance` turn. Blocked profile turns render as "· blocked by moderation ·".
> - **iOS (SwiftUI)**: new `ChatHubView` (Profile / Stranger / Rooms segmented, reusing the existing `ChatView`) in `CommunityView.swift`; `ApiClient` gains `ConnJoin`/`ConnMsg`/`RoomCreated`/`RoomMsg` models, the eight community endpoints, and query-string support in the shared `request` helper (needed for the interactor-scoped GETs).
> - **Android (Compose)**: `ChatHubScreen` with a Profile / Stranger / Rooms `TabRow` plus `StrangerPanel`/`RoomsPanel`; a `withInteractor` helper mints and remembers the same interactor identity Chat uses; matching `ApiClient` methods.
> - **Windows (WinUI 3)**: new `CommunityPage` (Stranger / Rooms Pivot) and a Community sidebar item next to Chat; matching records and calls, including show/hide of the join vs. conversation cards.
> - READMEs updated; remaining backend-only surfaces are now marketplace listings, licensing, and summon handles/beacons.
>
> ## Verification
>
> - All XAML parses clean (`xml.dom.minidom`).
> - Brace/paren balance checks pass on the new Swift/Kotlin/C#.
> - Backend untouched: 162 pytest tests pass.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #66 — Native apps: add Connect (social platforms + connected apps), grouped with Robots

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-native-connect` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/66>

> Adds the **Connect** surface to all three native clients — social-platform connections and the connected-apps catalog — grouped with the existing Robots screen so the phone nav bars stay at five destinations. This completes the connector-screen parity round across the suite.
>
> ## What's included
>
> - **iOS (SwiftUI)**: new `ConnectView` with a Social / Apps / Robots segmented switch (Robots reuses the existing `RobotsView`). Social offers the 16-platform picker, optional handle, connect-to-collect / connect-to-publish, per-connection collect-sample / publish-update / disconnect, and the collected/published tallies. Apps lists the catalog with Connect, then Collect and a one-tap capability Invoke per connector. `ApiClient` gains `SocialConn`, `CatalogApp`/`CatalogProvider`/`AppsCatalog`, `AppConn`, `InvokeResult` and the ten Connect endpoints.
> - **Android (Compose)**: `ConnectScreen` with a Social / Apps / Robots `TabRow` (platform filter chips, handle field, the same collect/publish/disconnect and catalog connect/collect/invoke actions); matching models and methods on `ApiClient`; bottom bar item renamed Robots → Connect.
> - **Windows (WinUI 3)**: new `ConnectPage` Pivot (Social / Apps) plus a Connect sidebar item; the flat Robots item stays since the `NavigationView` sidebar scales. Matching records and calls on `ApiClient`, including revoke-aware row visibility.
> - READMEs updated; the "not yet wired" note now reflects that connectors are covered and only relationships / community / licensing / summons remain backend-only.
>
> ## Verification
>
> - All XAML parses clean (`xml.dom.minidom`).
> - Brace/paren balance checks pass on the new Swift/Kotlin/C#.
> - Backend untouched: 162 pytest tests pass.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #65 — Native apps: add Knowledge Excursions and consolidate the Studio tab

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-native-excursions` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/65>

> ## Summary
> Adds the last major missing QRME surface to the native apps — **Knowledge Excursions** — and fixes tab creep with a **Studio** grouping.
>
> - **Study screen** (iOS/Android/Windows): start an excursion (`POST /profiles/{id}/excursions` with topic + question); each prior excursion shows the **privacy facts** — how many private terms were redacted from the outbound brief and a `left host` / `stayed local` badge — plus the findings, with a **Fold into knowledge** action (`POST /excursions/{cid}/learn`) and a ✓ once folded.
> - **Nav consolidation** (iOS/Android): Compose, Posts, and Study now live behind one segmented **Studio** tab, bringing the bottom bar back to five destinations (Overview · Chat · Studio · Robots · Settings). Windows keeps separate sidebar items (NavigationView scales) and gains Study.
>
> ## Verification
> Static: all XAML/XML well-formed, braces/parens balanced. Backend untouched — `pytest` **162 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #64 — Native apps: add the Chat screen (the core interaction loop)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-native-chat` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/64>

> ## Summary
> The one product loop the native scaffolds were still missing: **talking with the profile**. New Chat destination on iOS/Android/Windows, placed right after Overview.
>
> - The device owner's interactor identity is minted lazily on first send (`POST /interactors`) and **persisted**, so the same relationship continues across launches; sign-out clears it.
> - `POST /profiles/{id}/chat` renders the in-character reply; replies held by moderation show as **"⏳ Held for review"** with the flag reason instead of silently vanishing.
> - Chat bubbles align mine-right / profile-left in the shared palette; input row pinned at the bottom.
>
> ## Verification
> Static: all XAML/XML well-formed, braces/parens balanced. Backend untouched — `pytest` **162 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #63 — Native apps: add Robots and Settings (model picker + objections) screens

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-native-screens` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/63>

> ## Summary
> Brings the iOS/Android/Windows native scaffolds up to date with the new backend surfaces from the recent workstreams. Two new destinations on every platform (tab bar / NavigationView now 5 entries):
>
> - **Robots** — bind a catalog robot (`GET /robotics/catalog`, `POST /profiles/{id}/robots`), list bound bodies with live status, and send allowlisted commands (`say` with a topic, `clean`, `patrol`, `dock`) via `POST /robots/{rid}/command`. The `say` result (generated in character and moderated server-side) renders inline; command buttons appear only when the body's allowlist includes them.
> - **Settings** — the LLM provider picker (`GET /models` with configured flags, `GET/PUT /profiles/{id}/model`, effective resolution shown) and the governance view: objections against the profile with the owner's **Re-attest my rights basis** action.
>
> ## Verification
> Static (no native toolchain on Linux): all XAML/XML well-formed, braces/parens balanced across every `.swift`/`.kt`/`.cs`. Backend untouched — `pytest` **162 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #62 — Robotic embodiment: bind catalog robots to a profile as physical bodies

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-robotics` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/62>

> ## Summary
> A shared **robotics catalog** (`qrme/robotics.py`) covering **Isaac 1** (Weave), **NEO** (1X), **UWorld U1 Lite/Pro/Ultra** (UBTech), **Memo** (Sunday), and Roborock **Saros 20 / Saros 20 Sonic / Qrevo Curv 2 Flow** — each with kind, capabilities, and whether it can run an onboard LLM. In QRME a bound robot is an **embodiment**: the same persona in a physical body.
>
> ## Endpoints
> - `GET /robotics/catalog` — the registry, grouped by maker, with per-kind command allowlists
> - `POST /profiles/{id}/robots` — owner-only bind; creates a normal `embodiments` row so identity-consistency and chat routing treat the body like any other embodiment. For LLM-capable platforms the binding records which `qrme.llm` provider rides onboard (defaults to the profile's own model preference — ties into the provider-picker work)
> - `POST /robots/{rid}/command` — validated against the per-kind allowlist (a vacuum cannot `fetch`); `say` generates the line **in character** through the robot's provider and strictly moderates it before it is ever spoken
> - `GET /robots/{rid}/commands` — the audit log of every order; list/unbind round out the surface
>
> ## Verification
> 9 new tests (catalog, embodiment creation, LLM rules, allowlist, moderated speech, owner gating, unbind); **full suite 162 passed**. Screen 56 (Robotics) rendered and verified.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #61 — Complete third-party objection & revocation flow (audit + memorial/succession)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-objection-revocation` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/61>

> ## Summary
> Completes the third-party objection & revocation flow on top of the existing lifecycle, adding the pieces it was missing: a **PDI-sealed audit trail**, an **estate/authority revocation** path, correct **memorial** interaction, and a **succession** guard.
>
> ## What's new
> - **PDI-sealed audit trail** — every transition (`opened·reattested·upheld·dismissed·withdrawn·revoked·terminated`) lands in a new `objection_events` table and, when a PDI vault is configured, is sealed into it under `qrme/governance/{profile}/{objection}/{event}`. PDI hash-chains every write, so the sealed copy is independently tamper-evident. `GET /objections/{id}/audit` returns the owner/reviewer-gated timeline. Sealing never blocks the action (records locally + flags `sealed:false` if the vault is down).
> - **Estate/authority revocation** — `POST /objections/{id}/revoke` forces immediate termination for `subject_consent` (subject) and `estate_authorization` (estate). `public_figure_commentary` has no consent to revoke → review only. `/withdraw` stays as the subject alias.
> - **Memorial interaction** — a departed memorial can now be contested: opening an objection suspends it (`prior_status` remembered), **dismissal restores the memorial**, uphold/withdraw/revoke tears it down. Termination clears any named successor.
> - **Succession guard** — `succeed_profile` returns 409 while an objection is open.
>
> ## State machine
> Full diagram + before/after screen flow in [`docs/governance-objections.md`](docs/governance-objections.md); mobile mock is screen **55 — Objection & Revocation** (contested-state detail with the vault-sealed timeline and per-party actions).
>
> ## Verification
> 10 new tests (audit trail, PDI sealing via fake vault, estate revoke, memorial contest+restore, succession block); **full suite 153 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #60 — Let profiles pick their LLM provider (Claude/OpenAI/Grok/Perplexity/Gemini)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-llm-providers` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/60>

> ## Summary
> Owners are no longer locked to Claude. `qrme.llm` becomes a provider **registry** with OpenAI-compatible (OpenAI, xAI Grok, Perplexity) and Gemini adapters alongside the existing Anthropic provider and deterministic stub. Each profile chooses which model powers it.
>
> ## Endpoints
> - `GET /models` — every provider + whether it's configured in this deployment + the platform default
> - `GET /profiles/{id}/model` — the profile's stored `provider` and the `effective` provider it resolves to
> - `PUT /profiles/{id}/model` — owner-only; body `{provider}` ∈ `auto|anthropic|openai|grok|perplexity|gemini|stub`
>
> Choice is stored in a new `model_prefs` table; `chat`/`compose`/`proactive` route through `llm.provider_for_profile`; the choice is surfaced in `GET /profiles/{id}/transparency`.
>
> ## Design guarantees
> - **Deterministic stub is the floor** — any network provider that errors (bad key, outage, missing SDK) degrades to the stub and logs it; generation never hard-fails.
> - **Offline is absolute** — `QRME_OFFLINE` bypasses every network provider regardless of choice.
> - **Explicit choice wins** — a chosen provider is used directly (not wrapped by the cloud gateway); `auto` preserves the prior default + optional greater-model gateway behavior.
> - stdlib `urllib` only (matches `qrme.cloud`/`qrme.pdi_client`), **no new dependencies**.
>
> ## Verification
> 7 new tests; **full suite 143 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #59 — Add native iOS/Android/Windows apps for QRME

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-native` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/59>

> ## Summary
> Scaffolds three idiomatic **native** clients for QRME under a new `native/` directory, mirroring the JIM-mini native structure so all products feel like one system. Each is a separate native codebase wired to the real QRME backend — no shared web view, no backend changes.
>
> | Platform | Stack | Folder |
> |---|---|---|
> | iOS | Swift + SwiftUI (XcodeGen) | `native/ios/` |
> | Android | Kotlin + Jetpack Compose (Gradle) | `native/android/` |
> | Windows | C# + WinUI 3 (Windows App SDK) | `native/windows/` |
>
> ## Screens & wire contracts
> - **Create Profile** → `POST /profiles` (`{owner_id, kind, display_name, persona, demographics, verification.birthdate}`) → persists returned `owner_token`
> - **Overview** → `GET /profiles/{id}` (public card: kind, status, id) + Sign out
> - **Compose** → `POST /profiles/{id}/compose` (`{topic}`) → renders the generated post
> - **Posts** → `GET /profiles/{id}/posts` → the profile's feed
>
> Host defaults: `127.0.0.1:8000` (iOS/Windows), `10.0.2.2:8000` (Android emulator); base URL overridable.
>
> ## Verification
> No native toolchain on CI (Linux), so static checks only: all XAML/XML well-formed, `project.yml` valid YAML, braces/parens balanced across every `.swift`/`.kt`/`.cs`, Android `namespace`/`applicationId` and manifest consistent. `python3 -m pytest -q` → **136 passed** (backend untouched).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #58 — Add per-assistant screens: Apple Intelligence, Google Gemini, Microsoft Copilot

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-assistant-screens` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/58>

> ## Summary
> Adds three dedicated per-assistant drill-down screens (52 Apple Intelligence, 53 Google Gemini, 54 Microsoft Copilot) to the mobile screen gallery. Each screen lists the on-device apps the assistant reaches (collect) and its headline capabilities (act / produce).
>
> ## Changes
> - `docs/screens/build.py`: new portable `assistant` hero (no `icon()` calls), parameterized by `provider` (apple/google/microsoft) — colored identity dot + label + "N apps" pill, wrapping app chips, and four capability cards. Three new `SCREENS` entries (52–54).
> - Six new SVGs (iOS + Android): `52-apple-intelligence`, `53-google-gemini`, `54-microsoft-copilot`.
> - `README.md`: gallery cells for the three screens.
>
> ## Verification
> - `python3 docs/screens/build.py` runs clean (108 screens).
> - Rendered all three to PNG and eyeballed: 13-chip Apple screen wraps across 4 rows with no overflow; all capability cards clear the tab bar.
> - `python3 -m pytest -q` → 136 passed (backend untouched).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #57 — Add simple Files & Photos device-connector screen (51)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-files-photos` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/57>

> A plain connector surface — connect **Files/Folders and Photos** on **iOS, Android, and Windows** — alongside the fuller Connected Apps catalog (both kept). "Only the folders & albums you pick — nothing else is read." Screen **51 · Files & Photos** (iOS + Android), README updated. Generator-only; rendered and verified no clipping.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #56 — Add Knowledge Excursions screen (50)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/qrme-excursions-screen` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/56>

> Adds the missing screen for the safe-knowledge-excursions feature (`qrme/research.py`): a topic being studied with a **SANITIZED** brief showing `[private]` redactions, a "nothing left the host · local model" indicator, and findings folded in as a knowledge source. Screen **50 · Knowledge Excursions** (iOS + Android), README gallery updated.
>
> Generator-only change (no backend touched); rendered and verified no clipping; full suite **136 green**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #55 — Safe knowledge excursions: study a topic without leaking private data

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/qrme-knowledge-excursions` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/55>

> ## Summary
>
> When a profile's model meets an unfamiliar topic — needs to study, gather tools, or get more familiar to help with a request — it can go fetch **general knowledge without carrying the owner's private data out**, then bring it back for the **local model** to use with the private context that never left.
>
> Two guarantees:
>
> 1. **The outbound brief is sanitized.** The profile's own name, the people it talks to (relationship interactors), its handle, and any caller-marked private terms are redacted. `brief` is exactly what could leave, and it's stored so the excursion is auditable.
> 2. **Nothing private leaves the host.** Offline (`QRME_OFFLINE=1`) the gather runs on the local deterministic provider — no network. Even with a cloud model attached, only the sanitized brief is sent; `left_host` reports whether anything actually left.
>
> Findings come back as general knowledge and fold into the profile as a learned `knowledge` source (`POST /excursions/{id}/learn`).
>
> ## Endpoints (`qrme/routers/research.py`)
>
> | Method | Path | Purpose |
> |--------|------|---------|
> | POST | `/profiles/{id}/excursions` | study a topic (sanitize → gather) |
> | GET | `/profiles/{id}/excursions` | list |
> | GET | `/excursions/{cid}` | detail + audit (`brief`, `redactions`, `left_host`) |
> | POST | `/excursions/{cid}/learn` | fold findings in as a knowledge source |
>
> ## Tests
>
> 5 new tests — brief carries no private terms, findings carry none, nothing leaves by default, offline gathers locally, learn folds in. **Full suite 136 passing.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #54 — App connectors: connect a catalog app and use it (collect · act · produce)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/qrme-app-connectors` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/54>

> ## Summary
>
> Makes the connected-apps **catalog usable**, not just browsable. A profile connects to a catalog app (Apple Photos, Google Calendar, Microsoft 365, Canva, …), granting a subset of that app's capabilities, and its agents then use it in the direction the app supports.
>
> ## Endpoints (`qrme/routers/apps.py`)
>
> | Method | Path | Purpose |
> |--------|------|---------|
> | POST | `/profiles/{id}/apps` | connect a catalog app (grants a capability subset) |
> | GET | `/profiles/{id}/apps` | list connected apps |
> | DELETE | `/apps/{cid}` | revoke |
> | POST | `/apps/{cid}/collect` | pull context in as `linked_account` source material (builds the profile; sealed in PDI when configured) |
> | POST | `/apps/{cid}/invoke` | run a granted capability (`act` / `produce`) |
>
> Validated against `catalog.BY_KEY`: an unknown app is **404**, an ungranted capability or unsupported direction is **422/409**, all owner-gated.
>
> ## Tests
>
> 6 new tests. **Full suite 131 passing.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #53 — Connected-apps catalog: Apple, Google, Microsoft & Canva connectors

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/qrme-connector-catalog` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/53>

> ## Summary
>
> Beyond the 16 social platforms, a profile and its agents can connect to the **AI-integrated apps** on a person's devices — the same surfaces Apple Intelligence, Google Gemini, Microsoft Copilot and Canva expose. Adds a connector **catalog** capturing them.
>
> Each entry declares its **provider**, **app**, **capabilities** (the AI features), and **directions**:
> - `collect` — pull context in (build the profile / inform the agent)
> - `act` — drive the app agentically (create an event, run a shortcut, auto-browse)
> - `produce` — generate output (images, movies, designs)
>
> ### Coverage
> - **Apple Intelligence** — Photos, Calendar, Mail, Messages, Files, Notes, Reminders, Safari, Shortcuts, Passwords, Wallet, Phone/FaceTime, System (Writing Tools · Siri · Visual Intelligence · Genmoji)
> - **Google Gemini** — Photos, Calendar, Gmail, Keep/Tasks, Maps, Chrome, YouTube, Play Store, Gboard, Files, agentic Live/AppFunctions
> - **Microsoft Copilot** — Photos, File Explorer, Notepad, Paint, Snipping Tool, Settings, Microsoft 365, Copilot (Vision · Recall · Click-to-Do)
> - **Canva Magic Studio** — Magic Design/Media/Write/Edit/Switch/Layers, background remover, translate
>
> ## Endpoint & screen
>
> - `GET /connectors/catalog` returns the catalog grouped by provider.
> - New **Screen 49 · Connected Apps** (iOS + Android).
>
> ## Tests
>
> 3 new tests (endpoint shape, every entry well-formed, key apps present). **Full suite 125 passing.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #52 — Support all 16 connection platforms from the suite set

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/qrme-all-platforms` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/52>

> Expands the social-platform set from 8 to the full **16** the suite connects to. Adds **WhatsApp, Meta, Mastodon, Twitch, Snapchat, Roblox, Pinterest, Discord** alongside Instagram, X, TikTok, Facebook, LinkedIn, YouTube, Reddit, Threads — each with a presence-URL template for its QR beacon. The Social Connections screen now shows the full platform palette.
>
> Test covers connecting all 16 and the new beacons' presence URLs. Full suite **122 passing**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #51 — Social connections: collect to build profiles, publish/run via QR beacons

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/qrme-social-connections` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/51>

> ## Summary
>
> A social-platform **connection** layer for QRME. Each connection links a profile to a platform (Instagram, X, TikTok, Facebook, LinkedIn, YouTube, Reddit, Threads) in one of two directions:
>
> - **collect** — pulls the account's content *in* as source material that **builds the profile**. Each item lands in `source_items` as a `social_post` (sealed in the PDI vault when configured), exactly like any other training source.
> - **publish** — posts / runs the profile *on* the platform. Posts pass the same moderation pipeline as chat, a `social:<name>` surface is registered, and a **QR beacon** (`segno`) reaches the profile's presence there.
>
> Collect and publish are **separate connections**, so a read-only import can never also post. Everything is owner-gated.
>
> ## Endpoints (`qrme/routers/social.py`)
>
> | Method | Path | Purpose |
> |--------|------|---------|
> | POST | `/profiles/{id}/social` | connect a platform (collect or publish) |
> | GET | `/profiles/{id}/social` | list connections |
> | DELETE | `/social/{cid}` | revoke |
> | POST | `/social/{cid}/collect` | ingest items → profile source material |
> | POST | `/social/{cid}/publish` | moderated post to the platform |
> | GET | `/social/{cid}/beacon` | presence URL + QR path |
> | GET | `/social/{cid}/qr.svg` | the printable QR beacon |
>
> ## Also
>
> - `social_connections` table, `SocialConnect` / `SocialCollect` / `SocialPublish` models.
> - **Screen 48 · Social Connections** (collect vs publish, with a live QR beacon), iOS + Android.
>
> ## Tests
>
> 7 new tests (collect→sources, moderated publish, beacon/QR, direction guards, revoke, surface lifecycle). **Full suite: 121 passing** (was 114).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #50 — Record post-0.1.0 onboarding screens in the changelog

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/qrme-changelog-unreleased` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/50>

> ## Summary
>
> The provider-login and first-run onboarding screens added since **v0.1.0** (Log In, Verify Identity, Enable Access, Avatar Studio, Immersive Chat, Live Video, All Set) weren't reflected in the changelog. This records them under `## [Unreleased]` — plus the two text-overflow fixes — so the next release notes stay honest.
>
> Docs-only. No code changes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #49 — Fix two text-overflow issues on the onboarding screens

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/qrme-onboarding-polish` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/49>

> ## Summary
>
> Found during a full gap sweep of all three repos — two text-overflow bugs on QRME's onboarding screens:
>
> - **Verify Identity** — the *"Age 18+ confirmed"* row title collided with the `VERIFIED` badge. Shortened to *"Age 18+"* (the badge already conveys "confirmed").
> - **Immersive Chat** — the *"Ava stands in your space, life-size"* subtitle clipped the card's right edge. Trimmed to *"Ava stands in your space"*.
>
> Regenerated for both **iOS** and **Android** and re-rendered to confirm the fixes.
>
> ## Sweep result
>
> Everything else checked out clean: all three screen generators reproduce their committed SVGs with zero drift, README ↔ screen link integrity is intact (mobile, desktop, watch — no broken refs, no orphans), and backend suites pass (QRME 114, JIM 101, PDI 38).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #48 — Add first-run, login & immersive screens (login, verify, avatar, AR/VR, live video)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/qrme-immersive-onboarding-screens` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/48>

> ## Summary
>
> Fills the screen gaps you flagged — provider login, guided first-run setup, and the immersive surfaces (avatar / AR / VR / live video). Seven new screens, each in **iOS and Android** chrome:
>
> | # | Screen | What |
> |---|---|---|
> | 41 | **Log In** | Continue with **Apple / Google / Email** — real brand marks |
> | 42 | **Verify Identity** | one-time age 18+ + Face ID liveness + optional government ID |
> | 43 | **Enable Access** | notifications, camera & mic, health, contacts toggles |
> | 44 | **Avatar Studio** | a **2D portrait** and a **3D avatar** for chat / video / AR / VR |
> | 45 | **Immersive Chat** | life-size avatar in **AR / VR**, spatial audio, passthrough/full-VR |
> | 46 | **Live Video** | face-to-face **video call** with the AI avatar, on-device encrypted stream |
> | 47 | **All Set** | guided-setup completion |
>
> ## Details
>
> - Extends `docs/screens/build.py` with the Apple/Google/envelope brand marks and seven new hero renderers, all in the existing visual language.
> - Regenerates the gallery: **94 screens (47 × 2 platforms)**. No existing screen (01–40) changed.
> - README app-screens gallery updated with two new sections. Purely additive — the intro/patent text is untouched.
> - Each new SVG visually verified (rendered to PNG and reviewed).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #47 — README: fix a paste artifact (environmenlets → environment lets)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/fix-paste-artifacts` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/47>

> Repairs a single merged word in the intro (`environmenlets` → `environment lets`). All wording, patent text, dates, and dockets are left exactly as authored — one-character-level fix only.
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #46 — Per-platform code signing (macOS vs Windows certs independent)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/per-os-signing` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/46>

> ## Summary
>
> The signed build fed the **same** `CSC_LINK` to every OS, so adding only a macOS certificate would make the **Windows** job try to sign with the Apple `.p12` and fail the whole release. Make signing **per-platform and opt-in**:
>
> - **macOS** signs when `CSC_LINK` (Apple Developer ID `.p12`) is present.
> - **Windows** signs when `WIN_CSC_LINK` (Authenticode `.pfx`) is present.
> - **Linux/AppImage** never signs.
>
> Each platform's build step sees only its own certificate, so one platform's cert can't break another's build, and an absent cert simply yields an unsigned build (current behavior). Docs updated with the per-platform secret names.
>
> No change to the unsigned path — I'll dispatch a dry-run after merge to confirm all three OSes still build unsigned.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #45 — Build a universal (Intel + Apple Silicon) macOS dmg

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/universal-mac` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/45>

> ## Summary
>
> The macOS build produced an **arm64-only** dmg, leaving Intel Macs uncovered. Switch the `mac` target to a single **universal** binary that runs natively on both Intel and Apple Silicon.
>
> ```json
> "mac": { "target": [{ "target": "dmg", "arch": "universal" }], ... }
> ```
>
> Next tagged release will produce `…-universal.dmg` in place of the arm64-only one. I'll verify with a dispatch dry-run before it goes out.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #44 — e2e: fix PDI_MASTER_KEY default (must decode to 32 bytes)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/e2e-fix-masterkey` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/44>

> ## Summary
>
> With the orchestration hardened, the e2e run failed **fast with container logs** and pinpointed the real bug:
>
> ```
> pdi-1 | ValueError: PDI_MASTER_KEY must be base64 of 32 bytes
> ```
>
> The harness's default base64 key decoded to **30 bytes** (`for-test-only-32-bytes-key!!!!`), so PDI aborted on startup, the vault never became healthy, and the whole stack couldn't come up. Replaced it with a base64 value that decodes to exactly **32 bytes**.
>
> This is the last blocker — the e2e flow itself was already verified locally against booted services. Merging re-runs the workflow on `main`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #43 — e2e: robust compose orchestration (fix hang)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/e2e-compose-fix` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/43>

> ## Summary
>
> The first real full-stack e2e run (after removing the token requirement) **hung** for 25+ min and had to be cancelled. Root cause: `docker compose up --abort-on-container-exit --exit-code-from e2e` deadlocks with the one-shot `bootstrap` container — bootstrap exits 0, and the abort/exit-code handling stalls waiting on the `e2e` container, which never comes up cleanly. (The e2e *logic* was verified locally with plain processes; the container orchestration couldn't be, because base-image pulls are blocked in the dev sandbox — so this surfaced on the first real runner execution.)
>
> Fix — the standard "stack + test-runner" pattern:
>
> - **`up -d --build pdi qrme jim`** brings up the long-running services, running `bootstrap` to completion first (it's qrme's dependency) and honoring the `service_healthy` / `service_completed_successfully` conditions during startup.
> - **`run --rm --build e2e`** runs the flow as a one-shot, blocking on e2e's own `depends_on` (jim healthy) and exiting with the flow's status.
> - **`timeout-minutes: 20`** so a stuck stack fails fast instead of hanging the runner, and **`compose logs` on failure** for diagnosis.
>
> Merging triggers the workflow on `main`, so it self-verifies (and can no longer hang).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #42 — e2e: drop SUITE_REPO_TOKEN — sibling repos are public

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/e2e-no-secret` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/42>

> ## Summary
>
> The full-stack e2e workflow checks out `jim-mini` and `pdi` next to `qrme`. All three repos are **public**, so `actions/checkout` clones them with the built-in `GITHUB_TOKEN` — no personal-access-token secret is needed.
>
> Removes the `token: ${{ secrets.SUITE_REPO_TOKEN }}` inputs from the sibling checkouts and updates the docs. Now the workflow runs on `main` with **zero manual secret setup**.
>
> (If the repos are ever made private, re-add a `token:` with cross-repo read access.)
>
> Merging this to `main` triggers the workflow via `push`, so it'll self-verify.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #41 — Fix desktop-release packaging (electron-builder)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/fix-desktop-packaging` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/41>

> ## Summary
>
> A `workflow_dispatch` dry run of `desktop-release.yml` (run [29889807907](https://github.com/davidsbianchi1984/qrme/actions/runs/29889807907)) surfaced two real, release-blocking bugs — caught before any tag went out:
>
> 1. **Empty `CSC_LINK` broke the build.** The step always passed `CSC_LINK: ${{ secrets.CSC_LINK }}`, which is an **empty string** when the secret is unset; electron-builder treats `""` as a cert *path* and fails (`... /app not a file`, `WIN_CSC_LINK is not correct`). Fixed by splitting into a **signed** build (only when a cert secret is present) and an explicitly **unsigned** build (`CSC_IDENTITY_AUTO_DISCOVERY=false`). Secrets can't be used in `if:`, so availability is resolved into a step output first.
> 2. **Missing package metadata crashed update-info generation.** electron-builder couldn't detect the repository, so `computeChannelNames` threw `Cannot read properties of null (reading 'channel')`. Fixed by adding `author` + `repository` to `package.json` and setting `build.publish: null` to disable auto-update metadata.
>
> Result: installers package **unsigned by default**, and **signed** when the signing secrets are configured. Renderer build unchanged.
>
> ## Testing
>
> Renderer `npm run build` green locally; YAML + package.json validated. I'll re-run the dispatch dry run after merge to confirm the full electron-builder packaging is green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #40 — Use RELEASE_NOTES.md as the GitHub Release body

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/release-notes-body` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/40>

> ## Summary
>
> The desktop-release job used `generate_release_notes: true` only, so the curated `RELEASE_NOTES.md` wasn't used. Point the release at it (`body_path: RELEASE_NOTES.md`, with a checkout so the file is present); the auto-generated changelog is still appended.
>
> No behavior change until an `app-v*` tag is pushed. Prep for cutting v0.1.0.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #39 — Full-stack e2e harness, release notes & ops docs

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-e2e-release-ops` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/39>

> ## Summary
>
> Closes the remaining open items before v0.1.0.
>
> ### Full-stack e2e harness (`docker/`)
> Boots **PDI + QRME + JIM-mini as three separate containers** on one network and runs an end-to-end flow over the real HTTP seams — the booted-services counterpart to the in-process tandem tests.
>
> - `bootstrap.py` mints the PDI tenant tokens the two AI apps need to seal records.
> - `e2e.py` drives: PDI seal→read→audit-verify → a QRME specialist profile that chats → JIM enroll→monitor→**delegate-to-QRME-over-HTTP** → suite erasure. Its exit code is the CI verdict.
> - `Dockerfile` + `.dockerignore` for the backend image.
> - `.github/workflows/e2e.yml` runs it on `main` / on demand (needs a `SUITE_REPO_TOKEN` secret to pull the sibling repos; per-PR checks stay the fast `pytest` + app smoke build).
>
> **Verified locally**: booted the three as real uvicorn services with the exact compose wiring and ran `e2e.py` green, including the real JIM→QRME delegation (QRME's reply flows back through JIM's guidance). The container *build* itself is proxy-blocked from pulling base images in the sandbox, so it runs on CI runners — `docker compose config` validates.
>
> ### Release ops
> - `RELEASE_NOTES.md` — ready-to-paste v0.1.0 GitHub Release body.
> - `docs/releasing.md` — tag→build→sign→release flow and the optional signing secrets (`CSC_LINK`, `CSC_KEY_PASSWORD`, `APPLE_*`).
> - `docs/media-provenance.md` — records watermarking as a deliberate v1 non-goal (v1 profiles are text-only) with a concrete C2PA design for when generated media lands.
>
> ## Testing
>
> Adds infra/docs only; `pytest` (114) and the front-end smoke build are unchanged. Compose config validated; e2e flow verified against locally-booted services.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #38 — Release polish: CHANGELOG, CONTRIBUTING, suite docs, project URLs

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-release-polish` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/38>

> ## Summary
>
> Release scaffolding for v0.1.0 (docs only, no behavior change):
>
> - **CHANGELOG.md** — Keep a Changelog format, v0.1.0 feature summary.
> - **CONTRIBUTING.md** — dev setup, test/build expectations, decoupling + data-promise guidance, PR flow.
> - **README** — new "The suite — one origin, one login" section documenting `suite/gateway.py`: the mounted one-origin layout plus the cross-cutting control plane (`/suite/session`, `/suite/erase`, `/suite/export`, `/suite/consent`, `/suite/usage`), which wasn't surfaced in the README before.
> - **pyproject** — add `Homepage` and `Changelog` project URLs.
>
> ## Testing
>
> Docs/metadata only; `pytest` (114) and the front-end smoke build are unchanged. TOML validated.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #37 — Suite control plane: cross-app erase, export, consent, usage metering

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-suite-controlplane` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/37>

> ## Summary
>
> Closes the genuine **cross-cutting / tandem** gaps from the backlog. Per-product features (objections, succession, memorial, sunset, summon, quiet-hours, cloud-revoke in QRME; escalation, sensitivity, habits, goals, journal, provider handoff, `DELETE /data` in JIM; key rotation, audit schema, soft/wipe delete, snapshot in PDI) are already implemented — the real gaps were the suite-level concerns that span all three apps.
>
> One identity spans three products, so its cross-cutting concerns must too. This extends the suite gateway (`suite/gateway.py`) with a **stateless control plane** that fans out over the per-product tokens the caller already holds — the gateway stores no credential of its own.
>
> ## New endpoints
>
> | Endpoint | Closes | What |
> | --- | --- | --- |
> | `POST /suite/erase` | Deletion propagation across tandem; automatic cross-app deletion | Right to be forgotten, suite-wide — deletes the QRME profile, erases the JIM user, drops every sealed PDI record; returns a **per-product receipt** (`complete` true only when all acknowledge). Each product erases with its own authority; PDI via the tenant write token (no admin key). |
> | `POST /suite/export` | GDPR data portability / audit exports | One `suite-export/v1` bundle with the identity's data from every product (QRME export, JIM report, PDI snapshot). |
> | `PUT /suite/consent` + `POST /suite/consent/read` | Centralized consent management spanning all three | One authoritative consent doc **sealed in the identity's PDI vault** (encrypted + on the tamper-evident audit chain) and **enforced, not just logged** — withdrawing `cloud_contribution` also revokes it in QRME. |
> | `POST /suite/usage` | Suite subscription / billing metering hooks | Aggregates a counter per product into one `suite-usage/v1` meter for a downstream biller (rating/charging out of v1). |
>
> ## Docs
>
> `docs/tandem.md` markers updated from `[planned]` to `[implemented]` for data-deletion propagation, unified consent, GDPR erasure/portability, and billing metering hooks.
>
> ## Testing
>
> - 4 new end-to-end tandem tests wiring the **real** three apps in-process: erase propagation (profile really gone, vault emptied), export bundles every product, consent sealed + read-back + enforced in QRME, usage meters span the suite.
> - `pytest -q` — **114 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #36 — Make httpx a runtime dependency (suite gateway needs it)

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-httpx-dep` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/36>

> ## Summary
>
> `suite/gateway.py` imports `httpx` at runtime — it uses `httpx.ASGITransport` to call the mounted QRME / JIM / PDI apps in-process for the unified `/suite/session` sign-on. But `httpx` was declared only under the `dev` optional-dependencies extra, so a plain `pip install qrme` (without `[dev]`) could import the gateway and fail at runtime with `ModuleNotFoundError`.
>
> This promotes `httpx` to a main dependency. It stays listed under `dev` too (the test client uses it).
>
> ## Testing
>
> - One-line dependency change; existing CI (`pytest -q` + app smoke build) covers it.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #35 — Suite gateway (one origin + unified login) + launcher + CI app smoke

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-suite` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/35>

> ## What this adds
>
> Makes the three products **run together as one product**.
>
> ### `suite/gateway.py` — one backend origin
> - Mounts **qrme at `/qrme`, jim at `/jim`, pdi at `/pdi`** (they stay independent apps; the gateway is a thin router). Any product that isn't importable is skipped.
> - `GET /suite/health` — which products are mounted and live.
> - `POST /suite/session` — **unified sign-on**: one `{display_name, birthdate}` provisions a QRME profile, a JIM user, and a PDI tenant in a single in-process call and returns all tokens.
> - Run: `SUITE_CORS_ORIGINS='*' uvicorn suite.gateway:app`
>
> ### `launcher/` — the suite launcher
> Runnable React + Vite + Electron app: sign in once, see each product's live status, open its console.
>
> ### CI smoke-test
> `ci.yml` grows an **`apps`** job that builds `app/` and `launcher/` on every PR — proving the front-ends still type-check and build.
>
> ## Verified
> `tests/test_suite_gateway.py` covers one-origin routing + unified sign-on end to end (skips cleanly if jim/pdi aren't installed). **110 tests pass.** Driven live: gateway mounts all three; launcher signs in as one identity provisioned across all three. `httpx` promoted to a runtime dependency.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #34 — CI: build &amp; sign the desktop installers on per-OS runners

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-desktop-dist` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/34>

> ## What this adds
>
> `.github/workflows/desktop-release.yml` — a GitHub Actions **matrix** that builds the `app/` installers on **real macOS, Windows, and Linux runners**:
>
> - macOS → **.dmg**, Windows → **.exe** (NSIS), Linux → **.AppImage**
> - Push a tag `app-v0.1.0` → builds all three and **attaches them to a GitHub Release**; or run the workflow manually to get them as downloadable Actions artifacts.
> - **Code signing is optional** and driven entirely by repository secrets (`CSC_LINK` / `CSC_KEY_PASSWORD`, plus Apple notarization creds) — **never committed**. With no secrets the build still succeeds, just unsigned.
>
> ## Why CI (and not "here")
>
> A `.dmg`/`.exe` can't be cross-built or code-signed from Linux — they need their own OS and signing certs. So the correct pipeline is per-OS runners, which is exactly what this workflow uses. (The sandbox also can't fetch the Electron/electron-builder toolchain — those downloads aren't on the allowlisted registries — so local packaging isn't possible in this environment either.)
>
> `app/README.md` documents the release + signing flow.
>
> ## To produce binaries
> 1. Merge this.
> 2. (Optional) add signing secrets under **Settings → Secrets and variables → Actions**.
> 3. Push a tag: `git tag app-v0.1.0 && git push --tags` → the Release appears with all three installers.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #33 — Add a runnable QRME desktop app (React + Vite + Electron)

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-desktop-app` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/33>

> ## What this adds
>
> A **real, runnable front-end** wired to the QRME API — not a mockup. React + TypeScript + Vite, wrapped in **Electron** so it packages to an installable desktop binary.
>
> ### `app/` — the client
> - **`api.ts`** — typed QRME API client (configurable base URL).
> - **screens**:
>   - Onboarding → `POST /profiles`, `POST /interactors`, `PUT …/relationships/…`
>   - Home → `GET /profiles/{id}`, `GET …/stats`
>   - Chat → `POST …/chat` (surfaces moderation status + specialist-handoff state)
>   - Relationships → `GET …/transparency` + add
>   - Memory Vault → `GET`/`DELETE …/memory/{interactor}`
>   - Control Center → `GET /offline/status`, base-URL config, sign out
> - **`electron/`** — main + preload (the desktop wrapper).
> - README with run instructions.
>
> ### Backend
> - `create_app()` gains **optional CORS** (`QRME_CORS_ORIGINS`, off by default) so a packaged app can call the API cross-origin.
>
> ## How to run
> ```bash
> QRME_CORS_ORIGINS=* uvicorn qrme.api:app        # backend (stub provider = offline)
> cd app && npm install
> npm run dev            # web  → http://localhost:5173
> npm run electron:dev   # desktop window
> npm run dist           # installable binary → release/  (.dmg / .exe / .AppImage)
> ```
>
> ## Verification
> Driven end to end against a live backend with headless Chromium: create profile → Home stats render → **real chat round-trips** (see screenshots below). `tsc --noEmit && vite build` is clean; **all 107 backend tests pass**. Build artifacts (`node_modules/`, `dist/`, `release/`) are gitignored.
>
> > Note: I verified the web/renderer build and live API wiring in-sandbox; producing the final signed per-OS installer (`npm run dist`) needs the target OS toolchain and is left to run on your machine.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #32 — Add session-lifecycle screens; verify the app runs end to end

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/32>

> ## What this does
>
> Completes the mockup journey — **download → sign in → running → ending a session** — and confirms the backend runs start to finish.
>
> - **Two new mobile screens** (both platforms): **Sign In** (returning-user unlock — Face ID / vault passphrase) and **End Session** (a session summary + Sign Out, "your vault is sealed"). Generated in iOS and Android chrome — 40 screens × 2 platforms.
> - README grows a **Session lifecycle** gallery group.
> - **Verified the app runs end to end:** `pytest` passes (107 tests) and the FastAPI app boots and serves requests (`POST /profiles` → 201).
>
> ## Notes
>
> - Additive — one generator + README + new SVGs; no backend code touched.
> - Branch reset off latest `main`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #31 — Add iOS/Android and macOS/Windows platform chrome variants

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/31>

> ## What this adds
>
> Every screen now ships in **each platform's native OS chrome**, from the same generators — no content duplicated, only the window/status frame changes.
>
> - **Mobile** (`docs/screens/build.py`):
>   - **iOS** — Dynamic Island notch, iOS status icons, home indicator → `docs/screens/`
>   - **Android** — punch-hole camera, Android status icons, three-button gesture nav → `docs/screens/android/`
>   - 38 screens × 2 platforms.
> - **Desktop** (`docs/desktop/build.py`):
>   - **macOS** — traffic-light buttons, rounded window → `docs/desktop/`
>   - **Windows** — caption min/max/close buttons, squarer window → `docs/desktop/windows/`
>   - 6 views × 2 platforms.
>
> A shared `PLATFORM` / `PLATFORM_D` switch drives the chrome; running each generator emits both platforms. The README grows a **Platforms** comparison band.
>
> ## Notes
>
> - Pure additive — docs/assets + README; no app code touched.
> - Branch reset off latest `main` (prior PRs #28–#30 merged).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #30 — Add the QRME desktop app — wide, multi-panel workspace

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/30>

> ## What this adds
>
> A **desktop** form of QRME alongside the mobile app — one world, three products, in QRME's neon-purple identity.
>
> - **`docs/desktop/build.py`** — generates 6 self-contained desktop-window SVGs (1280×820) with a sidebar nav, top bar, and a workspace of panels. It **reuses the mobile generator's icon + colour library** so both galleries stay one system; tints use `rgba()` for renderer-agnostic output. Regenerate with `python3 docs/desktop/build.py`.
> - **The views:**
>
> | # | View | Content |
> |---|---|---|
> | 01 | Home | Live tiles, conversations-over-time chart, Ava profile, recent-activity feed, relationships |
> | 02 | Conversation | Chat surface + the AI-context "why this response" panel |
> | 03 | Relationships | Relationship table + per-person detail |
> | 04 | Memory Vault | Item table (stories/voice/photos/…) + vault storage |
> | 05 | Marketplace & Licensing | Discovery cards + your offers and earnings |
> | 06 | Control Center | Privacy toggles, permissions, embodiments & surfaces |
>
> - **`README.md`** — the "App screens" section now presents both the **desktop app** and the **mobile app**.
>
> ## Notes
>
> - Pure additive — docs/assets + README only; no code paths touched.
> - Branch reset off latest `main` (prior gallery PRs #28/#29 are merged).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #29 — Add 7 more app screens: moderation, posting & the persona engine

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/29>

> ## What this adds
>
> Fills the remaining capability gaps in the app-screen gallery so **every documented QRME feature has a screen** (31 → 38). Same generator, same design language, same `rgba()` renderer-safe tints.
>
> | # | Screen | Capability |
> |---|---|---|
> | 32 | Moderation | Owner approval queue; every reply checked before it's seen (PRD 6.5) |
> | 33 | Posts | Compose & post in the profile's voice, through the moderation pipeline |
> | 34 | Adult Mode | Age-gated at both ends; minors always strict (PRD 6.7) |
> | 35 | Aging & Lifecycle | Effective age evolves; successor owner or memorial (PRD 6.6) |
> | 36 | Multi-Modal | Text / voice / image / video output; voice preserved from sources |
> | 37 | Persona Embedding | Latent per-relationship state conditioning attention (Claims 21–23) |
> | 38 | Surfaces | Cross-platform presence: chat, feed, web, AR/VR, wearable |
>
> ## Notes
>
> - Pure additive — 7 new SVGs, generator + README gallery updated (fourth theme group).
> - Branch was reset off latest `main` (the prior gallery PR #28 is already merged), so this PR shows only the 7 new screens.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #28 — Add the QRME app-screen gallery: a screen for every capability

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/28>

> ## What this adds
>
> A hand-built SVG mockup of the **whole QRME product — one screen per capability**, in the app's design language: Deep Indigo · Neon Purple · Warm Amber · Soft Silver, SF-style system type, liquid-glass cards. Every screen is a self-contained SVG (no fonts, images, or scripts), so it renders identically in a browser, the README, and any converter.
>
> ## Contents
>
> - **`docs/screens/build.py`** — generates 31 screens from a shared vector icon set, palette, and device frame. Tints use `rgba()` so they're renderer-agnostic (8-digit hex alpha renders opaque in some converters). Regenerate with `python3 docs/screens/build.py`.
> - **Screens 01–15** mirror the product mockup: Welcome, Create Profile, Build Your Profile, Personality, Profile Home, Chat, Memory Vault, Relationships, Add Relationship, Profile Health, Marketplace, Licensing Center, Embodiments, Control Center, Design Language.
> - **Screens 16–31** cover the rest of the surface: Genesis, Summon & Beacons, Proactive, Transparency, Connections, Rooms, Providers, Cloud Model, Offline Mode, Objection & Lifecycle, Memorial, AI Assistant, Specialists (biometric handoff), Tasks & Grants, Fine-Tune, and the data promise.
> - **`README.md`** grows an **App screens** gallery grouping all 31 by theme.
>
> ## Notes
>
> - Pure additive change — no code paths touched, only docs/assets and a README section.
> - Every screen maps to a real QRME capability documented elsewhere in the README (endpoints, claims 21–26, lifecycle states, the PDI/JIM-mini tandem).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #27 — Docs: lifecycle & tandem diagrams, data promise, security section update

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/27>

> ## Summary
>
> Final cleanup items 3–5 (QRME's share) — no code changes.
>
> - `docs/diagrams/lifecycle.svg` — the profile state machine (active → restricted → terminated / dismissed-back, active → departed/memorial, succession loop) with consent notes on each edge; linked from `lifecycle-and-consent.md`.
> - `docs/diagrams/tandem-flow.svg` — the three-product data flow (JIM ↔ QRME guidance + continuity, both → PDI sealed storage, optional cloud gateway with the offline-mode note); linked from `tandem.md`.
> - README **"Your data promise"** — the no-raw-data-leaves-your-vault guarantee in user language, grounded in shipped mechanics (vault, preview/revoke, offline mode, erasure).
> - `tandem.md` security section updated to reality: capability-token auth in all three apps (hashed at rest, reviewer role, constant-time admin compares), the user-visible access log, and HIPAA's access-log item moved from planned to implemented.
>
> ## Testing
>
> Docs only; `QRME_LLM=stub python3 -m pytest tests -q` → **107 passed** (unchanged). Both SVGs validate as XML.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #26 — Ownership succession and the public memorial view

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/26>

> ## Summary
>
> Medium item (successor/legacy handling) — completes the `[planned]` succession spec and gives a departed profile a real memorial the outside world (and JIM) can reference.
>
> - `POST /profiles/{id}/succeed` (reviewer-gated via `QRME_ADMIN_TOKEN`, since the original owner may be unable to authorize; carries an out-of-band `verification_ref`):
>   - With a named `successor_owner`, ownership **transfers** — the old owner tokens are revoked and a fresh owner token is minted for the successor (shown once).
>   - With no successor, the profile **sunsets to memorial** — farewells sent, frozen rather than orphaned. 409 when already departed/terminated.
> - `GET /profiles/{id}/memorial` (public) — the departed profile's memorial: name (respecting anonymity), `@handle`, purpose, active beacon anchors, relationships touched — **never persona internals**; 409 while not departed.
>
> ## Testing
>
> New `tests/test_memorial.py` (3): succession transfers control (old token 401s, successor's works, card shows the new owner); no-successor succession becomes a memorial with farewells delivered and re-succession 409ing; the public memorial view (anchors, handle, no persona leak). `QRME_LLM=stub python3 -m pytest tests -q` → **107 passed**.
>
> ## Docs
>
> `docs/design/lifecycle-and-consent.md` succession section flipped to `[implemented]`; README documents both endpoints.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #25 — Cloud-contribution transparency: preview, verbatim log, true revoke

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/25>

> ## Summary
>
> Medium item — the contribution loop was opt-in and anonymized, but the owner couldn't see exactly what leaves or claw anything back. Now they can.
>
> - `contribution_log` table — every contribution is logged locally, **verbatim**, under a random opaque `ref` sent with the payload. The gateway never sees profile ids — only the local log maps a ref back — so items stay anonymous at the gateway yet remain individually deletable.
> - `GET /profiles/{id}/cloud-contribution` (owner) — `opted_in`, the policy, a **dry-run preview of exactly what the next contribution would contain** (nothing is sent), and the full history with revocation state.
> - `POST /profiles/{id}/cloud-contribution/revoke` (owner) — turns the flag off **and** asks the gateway to delete every previously contributed item by ref (`CloudModelClient.revoke_contributions` → `POST /v1/contributions/revoke`).
> - `anonymized_exchange` moved to `common.py` so feedback and the preview share one implementation; `contribution_log` purged on profile delete; the fake gateway implements the revoke endpoint.
>
> ## Testing
>
> New `tests/test_contribution_flow.py` (4): the preview is fully anonymized (no ids anywhere, persona name replaced) and nothing leaves on a dry run; the local log matches the gateway payload byte-for-byte; revoke stops future contributions and empties the gateway; opted-out empty state. `QRME_LLM=stub python3 -m pytest tests -q` → **104 passed**.
>
> ## Docs
>
> README cloud section documents the preview/log/revoke flow.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #24 — Keep personality consistent across embodiments

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/24>

> ## Summary
>
> Medium item — a profile keeps one identity as it moves between forms (speaker, hologram, robot, …).
>
> - `persona.identity_signature()` — a stable fingerprint (name, core persona, purpose, maturity) independent of embodiment/modality; the same value across voice, text, and a hologram proves it's the same personality.
> - `build_system_prompt()` affirms identity/memory/voice are constant across every form; only the form of expression changes.
> - `ChatResponse` gains `persona_signature` (invariant) and `embodiment` (the form a turn came through).
> - `GET /profiles/{id}/embodiment-consistency` (public) exposes the signature + the embodiments/surfaces the profile is live on.
>
> ## Testing
>
> New `tests/test_embodiment_consistency.py` (3). `QRME_LLM=stub python3 -m pytest tests -q` → **100 passed**.
>
> ## Docs
>
> README embodiments row documents the guarantee.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #23 — Training-data licensing and derivable specialist agents

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/23>

> ## Summary
>
> Backlog High #5 — owners license a profile's expertise; buyers acquire a license and can **derive their own specialist agent** from it, with provenance.
>
> - `qrme/routers/licensing.py` + `license_offers`/`license_grants` tables:
>   - `PUT`/`GET`/`DELETE /profiles/{id}/license` — offer terms (`consult`|`finetune`|`clone`, price, `allow_derivatives`); `GET` public.
>   - `POST /profiles/{id}/license/acquire` (buyer, interactor-token gated) → revocable `lic_` token.
>   - `POST /profiles/{id}/license/{grant}/derive` — derive a buyer-owned specialist agent seeded from the source persona; requires `allow_derivatives` + valid grant + verified-adult buyer; records `licensed_from`, returns the child's `owner_token`. `consult` forbids derivation; deriving twice 409s.
>   - `GET /profiles/{id}/licenses` (owner); `DELETE /licenses/{grant}` revokes.
> - `licensed_from` on `profiles` + `ProfileOut`; license tables purged on owner delete.
>
> ## Testing
>
> New `tests/test_licensing.py` (6). `QRME_LLM=stub python3 -m pytest tests -q` → **97 passed**.
>
> ## Docs
>
> README gains a training-data-licensing section.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #22 — Offline-first mode: fully on-host, no external transmission

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/22>

> ## Summary
>
> Backlog High #3 — a hard offline mode so QRME provably runs fully on-host.
>
> - `qrme/offline.py` + `QRME_OFFLINE=1`: `llm.get_provider` returns the local deterministic provider only (Anthropic SDK + cloud gateway bypassed even if configured); `create_app` never attaches the cloud client (even an injected one), so cloud contribution is inert; `GET /offline/status` reports `external_transmission_possible: false` and the data-locality guarantees.
> - Local fine-tuning already recomputes embeddings on-host; its result now reports `computed: locally` and `offline_mode`.
>
> ## Testing
>
> New `tests/test_offline.py` (5). `QRME_LLM=stub python3 -m pytest tests -q` → **91 passed**.
>
> ## Docs
>
> README config table gains `QRME_OFFLINE`; claim-26 row notes the guarantee.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #21 — Proactive-outreach anti-spam: rate cap, quiet hours, reply-suppression

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/21>

> ## Summary
>
> Implements the `[planned]` proactive limits from `docs/design/lifecycle-and-consent.md` so an unprompted-outreach profile can never spam someone.
>
> - `qrme/common.proactive_gate` + `proactive_state` table (per profile+interactor):
>   - **Rate cap** — at most one unprompted outreach per `proactive_min_interval_hours` (new `profiles` column, default 24, owner-configurable via `PATCH /profiles`).
>   - **Quiet hours** — the recipient's UTC-hour window (wraps midnight) via `PUT /interactors/{id}/quiet-hours` (interactor-token gated); new `quiet_start`/`quiet_end` columns on `interactors`.
>   - **Reply-suppression** — after an outreach, no further outreach until the recipient replies at least once; a chat message clears the flag.
> - `POST /profiles/{id}/proactive/{interactor}` runs the gate and returns **429** when blocked, records the outreach on success. State purged on delete/clear-memory.
>
> ## Testing
>
> New `tests/test_proactive_limits.py` (5): the rate cap; the reply-then-resume path (rate cap isolated at 0h); rate-cap expiry after the interval; quiet-hours suppression + allowance; and quiet-hours requiring the interactor's own token (403 otherwise). `QRME_LLM=stub python3 -m pytest tests -q` → **86 passed**.
>
> ## Docs
>
> README proactive-companionship row + `docs/design/lifecycle-and-consent.md` flipped the limits to `[implemented]`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #20 — Objection/takedown flow and restricted/terminated lifecycle states

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/20>

> ## Summary
>
> Implements the `[planned]` objection lifecycle from `docs/design/lifecycle-and-consent.md`: a real person (or their estate) can contest a profile that represents them.
>
> - `qrme/routers/governance.py` + `objections` table:
>   - `POST /objections` (public, proof-of-identity ref) opens a case and moves the profile to **restricted**.
>   - **Restricted** effects: hidden from `GET /marketplace`, un-chattable via summon, and closed to new interactors in chat (an existing relationship may continue). `departed`/`terminated` already block chat.
>   - `POST /profiles/{id}/objections/{obj}/attest` (owner) re-attests the basis.
>   - `POST /objections/{obj}/resolve` (reviewer — `QRME_ADMIN_TOKEN`, constant-time compare, so an owner can't adjudicate their own case): `uphold` **terminates** (content erased, tombstone left, owner token revoked), `dismiss` returns to **active**.
>   - `POST /objections/{obj}/withdraw` (subject) forces termination for a `subject_consent` profile; refused for other bases.
> - `ProfileOut` now reports `status`; new `restricted`/`terminated` states join `active`/`departed`. Objections purged on owner delete.
>
> ## Testing
>
> New `tests/test_objections.py` (7): open→restrict, new-interactor block with discovery hidden, dismiss→active, uphold→terminated (chat 410), subject withdrawal, withdrawal refused for non-subject-consent, and no objecting to a terminated profile. `QRME_LLM=stub python3 -m pytest tests -q` → **81 passed**.
>
> ## Docs
>
> README gains an objection/lifecycle section; `docs/design/lifecycle-and-consent.md` flipped the flow and both states to `[implemented]`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #19 — Resumable multi-step workflows with memory carry-over

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/19>

> ## Summary
>
> Backlog item #2 (autonomous multi-step task execution with memory carry-over). `tasks.py` runs a single-shot `grant → read → compose → moderate`. This adds **workflows**: a named plan of phases the profile works through one at a time.
>
> - `qrme/workflows.py` — a plan of phases (`research`, `draft`, `review`, `send`, `confirm`). `advance()` runs the next phase; each phase's output is **carried forward as working memory** into the next, so the profile builds on its own prior work, and every phase runs through the **persona prompt** so it stays in character.
> - The `confirm` phase **pauses** (`awaiting_input`); `resume()` supplies the awaited external confirmation — possibly **in a later session** — so a workflow survives across sessions.
> - Vault reads run under the **same revocable grant** as single-shot tasks; revoking it mid-run fails the next read-bearing phase. Only phase *outputs* are kept as memory; raw vaulted content is used in-memory only.
> - Endpoints (owner-gated): `POST /profiles/{id}/workflows`, `GET` (list/one), `…/{wf}/advance`, `…/{wf}/resume`, `…/{wf}/cancel`. New `workflows` table, purged on profile deletion.
>
> ## Testing
>
> New `tests/test_workflows.py` (5): the full `research → draft → review → send → confirm` run with accumulating working memory; the pause/resume-across-session path; grant revocation mid-run; unknown-phase rejection (422); cancel. `QRME_LLM=stub python3 -m pytest tests -q` → **74 passed**.
>
> ## Docs
>
> README claim-25 row extended to describe the workflow phases, carry-over, pause/resume, and mid-run grant revocation.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #18 — Sustain the biometric specialist handoff across a conversation

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/18>

> ## Summary
>
> Backlog item #1 (real-time biometric-triggered agent switching *inside* a single conversation). Previously a domain specialist spoke only on the exact turn that carried biometrics, then the next turn snapped back to the primary profile — a single-message detour, not a real hand-to-hand.
>
> Now the handoff is **sustained**: once monitoring routes a conversation to a specialist, it stays there across turns — including turns with no biometrics — until a fresh reading shows recovery, then hands control back.
>
> - New `active_handoffs` table (per profile+interactor); `common.py` helpers `get/set/clear_active_handoff` and `biometrics_recovered()` (the return signal: no concerning domain **and** stress < 0.4).
> - `chat()` reworked into a small state machine — a new/changed domain **engages** or **re-routes** the specialist; an active handoff without recovery is **sustained**; a recovery reading **returns** control. `ChatResponse.handoff.state` reports `engaged | sustained | returned`.
> - Per `(profile, interactor)`; torn down on memory-clear and on profile deletion (whether the profile was the primary or the specialist).
>
> ## Testing
>
> - Extended `test_specialist_switch_on_biometrics` through the full `engaged → sustained → returned` lifecycle (including a no-biometrics sustain turn and a calm-turn return-to-profile).
> - New `tests/test_handoff.py`: domain re-routing mid-conversation, per-interactor isolation, and teardown on memory wipe.
> - `QRME_LLM=stub python3 -m pytest tests -q` → **69 passed**.
>
> ## Docs
>
> README claim-24 row now describes the sustained handoff and the `state` field.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #17 — Capability-token authentication for owner control

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/17>

> ## Summary
>
> Closes the biggest hole in QRME's API: identity was **self-asserted**. Any caller who knew a `profile_id` could edit, export, delete, read another owner's sources/memory, or moderate their queue, and `owner_id` was a spoofable body field.
>
> This introduces **bearer capability tokens**:
>
> - `qrme/auth.py` — issue/verify tokens; only the SHA-256 hash is persisted (`api_tokens`), so a DB leak yields no usable credential. Two roles: **owner** (per profile) and **interactor** (per interactor).
> - `POST /profiles` and `POST /profiles/genesis` mint and return `owner_token` **once**; `POST /interactors` returns an interactor `token`.
> - **Owner-only endpoints** now require the profile's owner token — edit, sources, surfaces, embodiments, marketplace, stats, export, delete, sunset, moderation queue + approve/reject, specialists, grants/tasks, fine-tune, embeddings, compose, and the assistant/perception endpoints. Missing/invalid → **401**; valid token for the wrong resource → **403**.
> - Per-conversation **memory** is reachable by the profile owner *or* that interactor.
> - Deleting a profile **revokes** its owner token.
> - **Public by design (no token):** chat, profile card, marketplace browse, summon — talking to a synthetic profile stays as open as scanning a QR code.
> - `owner_id` becomes a grouping/display attribute, no longer a security boundary.
>
> The tandem path is unaffected: JIM→QRME uses the public chat/interactor endpoints.
>
> ## Testing
>
> - New `tests/test_auth.py` (7 tests): 401/403/200 gating, public-surface openness, delete-revokes-token, and owner-or-interactor memory access.
> - Test helpers updated to carry the owner token; multi-owner tests switch explicitly.
> - `QRME_LLM=stub python3 -m pytest tests -q` → **66 passed**.
>
> ## Docs
>
> README gains an **Authentication & access control** section documenting the token model.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #16 — Remove film-inspired framing from companion/assistant features

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/16>

> ## Summary
>
> Removes all external film-inspired framing from the companion and assistant/perception features, presenting them purely as product mechanics.
>
> Changes:
> - `qrme/companion.py` — docstring reframed to "an ambient-companion model, translated into product mechanics with an explicit consent boundary on each."
> - `qrme/routers/assistant.py` — module docstring reframed; removed scene-specific asides; the music brief now describes an original musical piece (melody/tempo/feeling) rather than a scene-specific instrument.
> - `README.md` — Companion-features intro and the triage table cell reframed with no external references.
> - `tests/test_assistant.py` / `tests/test_companion.py` — test docstrings reworded and the sample display name changed to a neutral value.
>
> No behavioral change: endpoints, scoring, moderation, and persistence are untouched.
>
> ## Testing
>
> `QRME_LLM=stub python3 -m pytest tests -q` → **59 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #15 — Spec: profile lifecycle, consent &amp; rights + cross-cutting tandem design

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/15>

> ## Summary
>
> Detailed design specs answering the "not yet spec'd out in detail" gaps, grounded in the current code and marking **[implemented]** vs **[planned]** throughout.
>
> **`docs/design/lifecycle-and-consent.md`** (QRME):
> - Third-party profile consent/rights bases (subject_consent / estate_authorization / public_figure_commentary) and the objection → restricted → re-attest → terminate/reinstate takedown flow, with revocable consent
> - Ownership succession (`successor_owner`) on owner death/incapacity, and auto-memorial when none is named
> - Full lifecycle state machine — active / restricted / departed (memorial) / terminated — with the memorial-vs-termination decision
> - Adult-content rules **between** synthetic profiles, and the hard floor that estate/public-figure third-party profiles can never be placed in adult scenarios
> - Marketplace commerce flow (price/purchase/ownership-transfer/ratings/disputes), summoning collision/transfer/expiration, proactive anti-spam limits
>
> **`docs/tandem.md`** (synced to all three repos): unified identity/account-linking, user-controlled data-deletion propagation, cross-product billing, the exact JIM→QRME and app→PDI data flows with fallback/offline handling, unified consent center, GDPR/HIPAA compliance story, and the tandem testing strategy.
>
> Companion specs shipped to the other repos: jim-mini `docs/guardian-internals.md` (baselines, detection ruleset, prediction, escalation decision tree, sensitivity tuning, noise handling) and pdi `docs/operations.md` (key rotation/KMS, audit schema, tenant deletion, DR, scaling, billing hooks) — plus a real code gap closed in pdi: **tenant soft-delete / wipe / restore** (`DELETE /tenants/{id}?mode=`, `POST /tenants/{id}/restore`).
>
> ## Testing
>
> Docs-only in QRME; 59 tests still green. PDI tenant-deletion shipped with 2 new tests (20 total).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #14 — Assistant &amp; perception: triage, proofread, real-time perception, creative composition

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/14>

> ## Summary
>
> Imports the assistant, perceptual, and creative roles Samantha plays in *Her*, as original QRME features (new `qrme/routers/assistant.py`), each passing the profile's moderation:
>
> - **Triage / curation** — `POST /profiles/{id}/assist/triage`: sort a large pile of items and keep the best N by a transparent, auditable relevance score (the "keep the 86 best emails" scene)
> - **Proofread** — `POST /profiles/{id}/assist/proofread`: an improved version in the user's voice, plus concrete edit suggestions
> - **Perceive & guide** — `POST /profiles/{id}/perceive`: "see" a real-time scene (objects, people, gestures, place) through a camera and give hands-free, step-by-step guidance toward a goal (the carnival-navigation scene), or just share the moment; perceptions are logged
> - **Compose creative works** — `POST /profiles/{id}/assist/compose` + `GET …/assist/works`: an original music/poem/note/lyric capturing a shared moment (the piano-piece scenes), kept as an artifact
>
> Erasure covers the new `creative_works` and `perceptions` tables.
>
> Separately, the critical PDI security fix shipped to pdi `main`: admin endpoints (tenant/deployment/token issuance, which mint vault credentials) now require `PDI_ADMIN_TOKEN` when configured.
>
> ## Testing
>
> 6 new tests (59 total, all passing): triage picks the two strong items out of 22, proofread detection, carnival perception with recognized-entity counts + goal guidance, moment-sharing perception, creative composition + artifact listing, and purge-on-delete.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #13 — Summoning (@/#/QR beacons) + community layer: rooms, listings, providers, consented handoffs

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/13>

> ## Summary
>
> **Summoning** (`qrme/routers/summon.py`) — leaving behind and summoning profiles:
> - `PUT /profiles/{id}/handle` claims a unique, normalized `@handle`; `GET /summon?ref=` resolves `@handle`, `#tag` (marketplace tags), or a beacon token — always public discovery cards, never persona internals
> - `POST /profiles/{id}/beacons` *leaves a profile behind* at a physical place; `GET /beacons/{id}/qr.svg` renders a real printable QR code (new pure-Python `segno` dependency) encoding the summon URL; scans are counted; `DELETE` picks the beacon back up; a departed profile's beacon resolves as a memorial
>
> **Community layer** (`qrme/routers/community.py`):
> - **Rooms** — multiparty conversations over `chat`/`voice`/`video`/`ar`/`vr` with any mix of real users and synthetic profiles: user↔user, profile↔profile (`POST /rooms/{id}/advance`), or combinations. Every profile turn is moderated; a room with a minor present always runs the strict filter, and blocked input produces no profile turns
> - **Marketplace listings** — `POST/GET /marketplace/listings`: users and businesses share and market synthetic profiles, content, business expertise, or services, browsable by kind, tag, and area
> - **Providers & consented handoffs** — a directory of real local businesses per area (healthcare, medical, mental health, finance, relationships, career); `POST /handoffs` packages the AI specialist's session summary for a provider **only with explicit consent** (403 otherwise), seals it in the PDI vault when configured, releases it solely through a revocable token, and revocation purges the sealed package
>
> ## Testing
>
> 10 new tests (54 total, all passing): self-naming/QR/beacon lifecycle including memorial resolution, mixed rooms, profile-profile advance, video/AR/VR channel descriptors, minor-strict rooms, listing filters, and the full handoff consent → seal → redeem → revoke → purge cycle.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #12 — Replace profile-to-profile dialogue with user-to-user connections

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/12>

> ## Summary
>
> Course-correction on the companion set: the chat-room inspiration was users meeting *other users*, not AIs conversing with each other. This removes the AI–AI `converse` feature and replaces it with **Connections** (`qrme/routers/connections.py`):
>
> - `POST /connections/join` — anonymous matchmaking by alias in a `friendly` tier, or a `rated` tier where **both** parties must be age-verified 18+ to even enter the queue
> - Per-tier moderation: rated pairs (verified consenting adults) run the `open` filter; friendly runs `balanced`, with a minor recipient always held to `strict` — blocked messages are stored for the sender's record but never delivered
> - Anonymity by design: participants see aliases only, never display names or ids; non-participants get 403 on the thread
> - `POST /connections/{id}/end` — either side ends it anytime; messaging afterwards returns 410
>
> Removed: `POST /profiles/{id}/converse`, `companion.converse`, the `dialogues` table, and its test. Genesis, proactive outreach, transparency, embodiments, and sunset are unchanged.
>
> ## Testing
>
> 4 new tests (44 total, all passing): friendly match + alias anonymity + outsider 403, rated-tier age gating (minor and unverified rejected) with open moderation between verified adults, minor shielding in the friendly tier, and end-of-connection semantics.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #11 — Companion features: genesis interview, proactive outreach, transparency, AI–AI dialogue, embodiments, graceful departure

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/11>

> ## Summary
>
> Companion mechanics inspired by the ambient-OS ideal of Spike Jonze's *Her*, rebuilt with explicit consent boundaries (new `qrme/companion.py`):
>
> - **Genesis interview** — `POST /profiles/genesis`: a profile born from four personal questions (social style, humor, what matters, comfort); omit `display_name` and it deterministically chooses its own name from the answers
> - **Proactive companionship** — `POST /profiles/{id}/proactive/{interactor}`: the profile reaches out first — 403 unless the owner set `interaction_scope: proactive`; the outreach is moderated and lands in shared memory
> - **Honesty about multiplicity** — `GET /profiles/{id}/transparency`, plus a chat-prompt rule: the profile truthfully acknowledges its other ongoing relationships whenever asked
> - **Profile-to-profile dialogue** — `POST /profiles/{id}/converse`: two synthetic profiles exchange moderated turns; flagged turns are dropped, never stored
> - **Embodiments (even robots)** — `POST/GET /profiles/{id}/embodiments`: speaker, earpiece, hologram, robot, humanoid; chat accepts an embodiment as its surface
> - **Graceful departure** — `POST /profiles/{id}/sunset`: a farewell composed for every relationship, profile becomes `departed`, memory/export preserved, archive sealed in PDI, chat returns `410` instead of a silent 404
>
> Matching jim-mini work pushed to its `main`: `POST /companion/{user_id}` — the ambient guardian check-in that reaches out first, grounded in mood, goals, and personality.
>
> ## Testing
>
> 6 new tests (41 total, all passing): self-naming determinism, proactive consent gating, transparency counts, four-turn dialogues, robot embodiment routing, and full sunset lifecycle including PDI archival and double-sunset conflict.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #10 — Cloud Model Gateway, router refactor, and quick wins

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/10>

> ## Summary
>
> **Cloud model** (new `qrme/cloud.py`, shared contract in `docs/cloud-model.md`):
> - `CloudModelClient` + `CloudProvider`: chat, compose, and autonomous tasks route to a Cloud Model Gateway's hosted tier — a greater model (e.g. `claude-fable-5`) than the local default — with automatic fallback to the local provider whenever the gateway is unreachable. Configure with `QRME_CLOUD_URL` + `QRME_CLOUD_TOKEN` or an injected client.
> - **Contribution loop**: per-profile `cloud_contribution` opt-in. Only positively-rated exchanges are contributed, anonymized (profile/interactor ids stripped, display name replaced with `PERSONA`); down-votes and non-consenting profiles never contribute. `GET /cloud/status` reports the tier. Contributions land in PDI's encrypted, audited intake.
>
> **Refactor (quick win)**: the 800-line `api.py` split into routers — `routers/profiles.py`, `routers/interaction.py`, `routers/intelligence.py` — with shared helpers in `qrme/common.py`; `create_app` now only wires state and routers.
>
> **Other quick wins**: GitHub Actions CI (pytest on push/PR), SQLite WAL mode, pytest `filterwarnings` for the TestClient deprecation.
>
> Matching cloud work pushed to jim-mini (greater-model guidance + anonymized outcome contributions) and pdi (sealed, audited contribution intake).
>
> ## Testing
>
> 4 new tests (35 total, all passing): greater-model routing, gateway-down fallback, anonymization + consent gating (including proof no ids/names leave), and no-gateway status.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #9 — Design system + repo polish: asset docs, gallery, accessibility, licensing, packaging

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/9>

> ## Summary
>
> **Design system (`assets/design/`)**
> - New `README.md`: palette tokens (indigo/silver/amber + per-product accents), design philosophy, file conventions, and crisp-PNG export guidance at 512/1024/2048/4096 px (rsvg-convert, Inkscape, headless-Chrome recipes, GitHub social-preview note)
> - `gallery.html` rebuilt: responsive auto-fit grid, dark theme, palette swatch row, per-asset descriptions with open-SVG links, lazy-loaded images, and an export-tip callout
> - All 17 SVGs upgraded structurally: `role="img"`, `aria-labelledby`, id'd `<title>`, and new `<desc>` elements; conventions (per-file id prefixes, viewBox+size, system fonts) documented
>
> **Repo standardization**
> - MIT `LICENSE` (© 2026 David Bianchi) and a comprehensive Python `.gitignore`
> - `pyproject.toml`: readme, license, authors, keywords, classifiers, and URLs metadata
> - `README.md`: new Configuration env-var table, Related projects section (three-repo suite), and License section
> - `docs/tandem.md`: the three-project tandem architecture doc now lives in this repo too (matching jim-mini and pdi)
>
> Matching polish (LICENSE, .gitignore, pyproject, README sections, SVG accessibility) pushed to jim-mini and pdi.
>
> ## Testing
>
> 31 tests passing; all SVGs and TOML validated.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #8 — Implement claims 21–26 and the AI Profile Marketplace

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/8>

> ## Summary
>
> **Claims 21–26** (`qrme/adaptation.py`, `qrme/tasks.py`):
>
> - **21** — per-(profile, interactor) latent persona embedding: a named vector (engagement, warmth, depth, positivity, stress, continuity), EMA-updated and versioned after every interaction for cross-session state; `GET /profiles/{id}/embedding/{interactor}`
> - **22** — the embedding renders as attention weighting in the system prompt, so engagement conditions where the model attends
> - **23** — `ChatRequest.biometrics`: real-time monitoring data (typically from JIM-mini) stored per interaction, feeding the stress dimension and a monitored-situation prompt note
> - **24** — domain specialists (`PUT /profiles/{id}/specialists`); biometric signals route replies to the matching specialist profile, reported via `ChatResponse.handoff`
> - **25** — revocable grants + autonomous multi-step tasks (grant-check → scoped vault read → compose → moderation) logging summaries only, never raw vault data; `DELETE /grants/{id}` revokes instantly
> - **26** — `POST /profiles/{id}/finetune`: offline local adaptation over stored history, artifact sealed in the PDI vault when configured, `external_transmission: false`; erasure purges adaptation artifacts
>
> **AI Profile Marketplace** (architecture-poster extra): `POST/DELETE /profiles/{id}/marketplace`, `GET /marketplace?tag=` — public discovery cards only, anonymous profiles stay anonymous.
>
> ## Testing
>
> 8 new tests (31 total, all passing), including revocation, vault sealing/purging, and specialist-switch scenarios.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #7 — Design assets for the new capabilities: purpose modes, profile health, sources &amp; vault

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/7>

> ## Summary
>
> Three new illustrations in the established indigo/silver/amber style, covering the capabilities added in #6:
>
> - **`14-purpose-modes.svg`** — the six purpose modes as cards (legacy & memorial, family, creator persona, social & fan, companion & coaching, enterprise agent), each with its API value
> - **`15-profile-health.svg`** — the `GET /profiles/{id}/stats` dashboard (engagement trend, sessions, memory entries, moderation pass rate, relationship graph), the strict/balanced/open maturity dial, and the multi-modal output row
> - **`16-sources-vault.svg`** — source material flowing into the profile, natural recall, content sealed in the PDI vault (key reference only), and the edit/export/delete owner controls
>
> `gallery.html` updated to showcase all three. All SVGs are hand-built and validate as well-formed XML; tests unaffected (23 passing).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #6 — Add product-sheet capabilities: purposes, source material, maturity filters, multi-modal, surfaces, compose, stats, owner control, PDI vault

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/6>

> ## Summary
>
> Implements everything from the four product infographics that QRME didn't yet have:
>
> - **Profile purposes** — `legacy_memorial`, `family`, `creator_persona`, `social_fan`, `companion_coach`, `enterprise_agent`; each conditions the persona prompt (brand-safe creator, wholesome family, knowledge-base enterprise agent, …)
> - **Source material** ("AI builds & trains the profile") — `POST/GET /profiles/{id}/sources` for photos, conversations, social posts, writings, voice notes, life events, knowledge entries, and linked accounts; recent items are recalled naturally in every prompt
> - **Age & maturity filters** — per-profile `strict`/`balanced`/`open` dial; minors are always strict, and strict filters flagged content even for verified adults
> - **Multi-modal output** — `modality` on chat (`text`/`voice`/`image`/`video`) returns a render descriptor; voice reports whether it's preserved from voice-note sources (synthesis out of scope for v1)
> - **Cross-platform presence** — `PUT/GET /profiles/{id}/surfaces` (chat, feed, web, AR/VR, wearable, `social:<name>`) with chat-side surface validation
> - **Posting at scale** — `POST /profiles/{id}/compose` drafts a post in the profile's voice through the same moderation pipeline; public posts always face the strict filter
> - **Profile health, at a glance** — `GET /profiles/{id}/stats`: sessions, memory entries, moderation pass rate, relationship-graph size, engagement average, sources, posts, surfaces
> - **You own it / total control** — `PATCH /profiles/{id}` (edit anytime), `GET /profiles/{id}/export` (full export), `DELETE /profiles/{id}` (erases everything, including vaulted records)
> - **Encrypted at rest** — PDI tandem via `qrme/pdi_client.py` (`QRME_PDI_URL` + `QRME_PDI_TOKEN`): source-material content sealed in PDI's AES-256-GCM vault, only key references kept locally, resolved on read and purged on delete
>
> ## Testing
>
> 11 new tests in `tests/test_capabilities.py` (23 total, all passing), including a FakePDI at the client boundary verifying content is sealed, resolved on read, and purged on delete.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #5 — Rebuild design asset suite at higher quality; add repo cover

- merged · opened 2026-07-18 · merged 2026-07-18
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/5>

> ## Summary
>
> - Redraws all twelve feature illustrations (`assets/design/01–12`) and the Guardian tandem piece (`13`) with substantially higher craft: layered background gradients, glow/blur lighting (`feGaussianBlur` / `feDropShadow`), vignettes, finer detail (constellations, particles, rim lights), and tighter typography — same subjects, same indigo/silver/amber system.
> - Adds a new 1280×640 repo cover (`assets/design/00-cover.svg`, GitHub social-preview ratio) — central avatar dissolving into data, relationship threads graded warm-dense (family) to cool-sparse (stranger), memory-timeline arc — and embeds it at the top of the README.
> - Redesigns `gallery.html` to showcase the full 14-piece set with hover cards.
>
> All assets remain hand-built SVG (no external fonts, images, or scripts) and validate as well-formed XML.
>
> Matching artwork was pushed directly to `jim-mini` (cover + rebuilt tandem illustration) and `pdi` (cover + new architecture and encryption-flow diagrams).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #4 — Design assets: condensed prompt suite + JIM-mini/Guardian illustration

- merged · opened 2026-07-17 · merged 2026-07-17
- `claude/qrme-design-assets` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/4>

> ## Summary
>
> Design-only changes, split out from the Guardian code PR (#3):
>
> - **`docs/design/image-prompts.md`** — updated to the condensed 12-prompt suite (the canonical prompt reference) and added prompt **13** for the JIM-mini / Guardian tandem layer.
> - **`assets/design/13-guardian-tandem.svg`** — new vector concept asset showing the Guardian closed loop: wearable biometric signals → Guardian shield-with-pulse detection → triggering the matching QRME specialist synthetic-profile avatar → moderated guidance out, with a distinct critical-path escalation to an emergency contact and a return loop noting the episode is remembered. Same indigo/silver/amber design system as the existing twelve assets.
> - **`assets/design/gallery.html`** — includes asset 13.
>
> No code, tests, or API surface touched — purely documentation and static SVG assets.
>
> ## Test plan
>
> - All 13 SVGs validate as well-formed XML.
> - `docs/design/image-prompts.md` links line up with the files in `assets/design/`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #3 — Three standalone products (QRME · JIM-mini · PDI) that interoperate in tandem over HTTP

- closed · opened 2026-07-17
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/3>

> **Closed** — superseded by splitting JIM-mini and PDI into their own separate repositories.
>
> This PR bundled the `jim/` and `pdi/` code into the QRME repo, but the plan changed to three separate repos:
> - **QRME** — this repo (stays pure synthetic-profile platform; `main` already is).
> - **JIM-mini / Guardian** — moving to its own `jim-mini` repo.
> - **Private Data Infrastructure** — moving to its own `pdi` repo.
>
> The self-contained project bundles were delivered separately. QRME's `main` is unchanged and pure. PR #4 (design assets) is unaffected.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #2 — QRME v1: AI synthetic profile platform per PRD (#1)

- merged · opened 2026-07-17 · merged 2026-07-17
- `main` → `claude/qrme-synthetic-profiles-a4t8y9`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/2>

> QRME v1: AI synthetic profile platform per PRD

## #1 — QRME v1: AI synthetic profile platform per PRD

- merged · opened 2026-07-17 · merged 2026-07-17
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/1>

> ## Summary
>
> Bootstraps the QRME platform (PRD Draft v0.1) as a FastAPI + SQLite backend implementing the v1 feature set:
>
> - **Profile creation & onboarding (PRD 6.1)** — age/identity verification with a parent/guardian consent flow for minor owners, a required consent/rights record when a profile represents another real person, demographics, imported source list, and an anonymity toggle.
> - **Relationship-aware modification (6.2)** — per-(profile, interactor) relationship config (type, nickname, tone, restricted topics) conditioned into the persona system prompt.
> - **Engagement-based learning (6.3)** — an auditable exponential-moving-average score from message length, return visits, and explicit up/down feedback; it adapts reply style and depth only, never core identity or boundaries.
> - **Persistent memory (6.4)** — prior turns per interactor feed the chat context; owners/users can view and clear history.
> - **Content moderation (6.5)** — every profile-generated reply passes a rule-based pipeline (deny patterns, age-appropriateness for minors, relationship boundary topics) before it's visible; `manual` mode holds all replies in an owner approval queue, and held content is hidden from interactors.
> - **Aging & lifecycle (6.6)** — profiles can age (effective age evolves from `base_age` over time) and carry a `successor_owner` for legacy succession.
> - **Adult content mode (6.7)** — gated at both ends: an adult verified owner to enable it, a verified 18+ interactor to chat.
> - **In-app chat surface (6.8, v1)** — `POST /profiles/{id}/chat`.
>
> The LLM layer uses the official Anthropic SDK (`claude-opus-4-8`, adaptive thinking). Without credentials — or with `QRME_LLM=stub` — a deterministic stub provider keeps the whole platform and its tests runnable offline.
>
> ## Test plan
>
> - `pytest` — 13 tests covering the consent/verification gates, relationship-aware replies, memory persistence and clearing, engagement scoring and feedback, adult-mode gating, and the moderation queue (hold → approve/reject). All pass.
> - Live smoke test with `uvicorn`: created a consent-gated legacy profile, set a grandchild relationship, chatted (reply used the configured nickname and tone and passed moderation), and verified memory persisted.
>
> ## Notes
>
> - The repo was empty; `main` was created with an initial empty commit as the PR base. Consider setting `main` as the repository default branch.
> - Out of scope per PRD non-goals: biometric switching, robotic embodiment, watermarking, marketplace. Social posting integrations are represented only as a `sources` list in v1.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

