# Changelog

All notable changes to QRME are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Fixed

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

[Unreleased]: https://github.com/davidsbianchi1984/qrme/compare/app-v0.3.3...HEAD
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
