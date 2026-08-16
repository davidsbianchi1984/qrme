# Changelog

All notable changes to QRME are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.77.0] - 2026-08-16

### Added

- **The Agent has its own tab, and a reach worth opening it for.** The agent
  that can rewrite your page, edit your homepage sandbox and write your
  widgets had existed since the Studio shipped, and the only way to reach it
  was to open the widget workshop first — so the person who wanted to say
  *make my page say what I actually do* had to go somewhere about code to
  find it.

      asked     can an agent edit this person's app
      mattered  can the person find the agent

  It is now the second tab, behind the QRME poster cropped to a box. What it
  did is listed under what it said, because prose describing an edit is
  asking to be believed and the steps are the part that can be checked.

- **Its roster went from eleven rows to 113.** Eleven was the page, the
  homepage, the friends list and the widgets, against a screen that reads as
  a collaborator for the whole app. A surface that implies a general
  assistant and then refuses two thirds of what is asked of it teaches people
  to stop asking.

  The list now covers the profile itself, what it knows, the face it wears,
  proving it is really you, the wall, money, the things that exist — stickers,
  robots, watches — messages, what it remembers of people, and how it ends.

- **Twelve rows ask instead of doing.** `converse` stops when the model
  reaches for a step that cannot be taken back and returns what it *would* do
  — the roster's own sentence and the arguments it chose, both shown — rather
  than doing it. `POST /profiles/{id}/authoring/act` is where a yes lands: no
  prose reaches it and no model is asked, so the arguments run exactly as the
  turn displayed them.

      asked     may this person do this
      mattered  did this person mean this

  The owner's token has answered the first since the Studio shipped. Nothing
  answered the second. *Wind it down* and *wind that thread down* are one word
  apart, and no prompt gets that to zero; a button does. Winding a profile
  down, handing it on, paying out, deriving a licence, messaging somebody,
  unsending, granting authority, reaching out, friends in and out, answering
  an objection, forgetting or erasing a person.

  Still absent by absence: memberships and plans, key material, and
  `DELETE /profiles/{id}` — ending has its own door in `sunset`, which is in
  the roster and asks first.

- **A row may name the fields it sets.** `PATCH /profiles/{id}` is how a
  person renames their profile and rewrites its persona; it is also how they
  name a successor owner and mark the profile adult. `edit_persona` takes
  `display_name` and `persona`, and anything else is refused rather than
  dropped — a dropped field is a change the model will report having made.

- **The room is a scene, and each box is a place to appear.** Every person in
  an audio room has their own square, the talker's square lights up, and the
  box is where somebody turns on video, uploads a photo, or wears a mask
  filter. Backend, console and all three shells.

### Fixed

- **A long answer hit the wall mid-sentence and simply stopped.** Replies were
  capped at 1024 tokens with the comment *chat replies are deliberately
  short* — and the same door answers *write me the migration*. The room went
  up tenfold, and the half that matters is the second: when a provider stops
  because it ran out of room rather than because it finished, the reply says
  so, in whichever of the ten languages the platform is speaking. Gemini had
  no output budget at all.

- **A guard could not tell two doors apart.** The check that every writing
  tool goes through an owner-scoped door read `"require_owner" in source`.
  This estate also has `require_owner_or_interactor` — a weaker door, admitting
  anybody the profile is talking to — which contains that string and read as
  passing.

- **A route guarded by a helper read as unguarded.** `request_payout` says
  `owner = _owner_of(profile_id, request)`, and `_owner_of` is three lines
  whose middle one is `require_owner`. The same check reported a payout route
  with no owner check at all, and the obvious way to make that pass would
  have been to loosen the pattern.

- **A value that only survived as its caption.** iOS decodes loose JSON
  through `AnyDecodable`, which kept a display string and nothing else,
  because every caller only ever displayed it. The press sends arguments
  *back*, and a number that made the round trip as `"3"` is a different
  request from the one the person read.

- **Six live translations reported dead**, after the shared agent conversation
  took an l10n key *prefix* as a prop — every string rendered, and none was a
  literal the untranslated-key guard could see.

- **The reply wall, the Agent lesson's way in, and one screen record** that
  counted one fewer row than it held.

## [0.76.0] - 2026-08-15

### Added

- **Thirty-four friends pictures, one blank page behind all of them.** A face
  in a friends grid is a link: it opens that friend's homepage. The Starter
  Collection is the one place on a fresh deployment where the grid is full,
  because the dossiers install colleague friendships in both directions.
  Every one of those faces opened the same page — no headline, no about, no
  links, no top friends, one purple.

      asked     the friends picture should open their profile homepage
      mattered  it did, and there was nothing on the other side

  `dossiers.homepage_doc` composes the page from the dossier each starter is
  already grounded in: expertise and services as the about, the first three
  skill chips as the headline, a palette by family of trade. Not written
  beside it — a hand-written page next to a dossier is two statements about
  one profile, and the way a page ends up claiming something its persona has
  never heard of. Two absences are deliberate and guarded as absences: no
  links, because a fictional physician has no website and an invented URL
  either goes nowhere or somewhere real that is not hers; and seven palettes
  by trade rather than thirty-four opinions. Installed and repaired by the
  same blank-only seed call, reported as its own `homed` count.

- **Signing in reaches what you own.** An owner token is minted once, in the
  create response, and handed to whichever client did the creating. There was
  no second place to get one.

      asked     where do I find my owner token
      mattered  the only route that lists a person's profiles asked for one
                first

  `GET /profiles/{id}/siblings` — the roster — refuses to be keyed on
  `owner_id`, and says why in a sentence worth keeping: *an id in a path is a
  string somebody chooses, not a secret.* Right, and it closes the loop on
  itself. Somebody who reinstalled, or who made the profile in the phone app
  and is now at the console, could not enumerate their own profiles and could
  not open one.

  Two doors, and the separation between them is the design.

  **`GET /accounts/{account_id}/profiles`** is that same roster reached
  through the credential such a person does have — the account token behind an
  email and a password. The objection to keying on the account is answered by
  what proves the caller, not by what is in the path. It carries no tokens:
  a roster is a read, and `qrme/dock.py` already states the rule in one line —
  *nothing that authorises anything belongs on a surface.*

  **`POST /accounts/{account_id}/profiles/{profile_id}/owner-token`** is the
  grant, on request, shown once. Additive rather than a rotation: every owner
  token already out there keeps working, because recovering access on a laptop
  says nothing about the phone that has been holding one for a year — and
  conflating the two would make this the button that silently unlinks
  somebody's Guardian. Revoking is a different intent with its own door.

  A profile on another account answers exactly as one that does not exist, or
  the route is a directory of which ids are real on a deployment. The account
  token dies with a password reset, which is what keeps this pair from being
  the one session a reset leaves standing.

### Changed

- **The tandem contract and the README caught up.** `docs/tandem.md` —
  byte-identical in all three repositories — described JIM's self-link as
  *the user pastes their own QRME owner token*, which is the mechanism these
  two routes exist to replace; a contract describing a mechanism the product
  no longer has is worse than one that says nothing. The README's capability
  table said an owner token is minted once, in the create response, and that
  is no longer the only place it comes from.

- **Signing in opens something, on all four clients.** Every client had the
  same shape: a signed-in account whose only offer was to *make* a profile.
  The console now leads with the roster and puts the create form behind *Or
  make another one* — a person whose profiles already exist is not here to
  make another, and offering that first is how the second one got made. The
  three shells held the account for the life of the screen, never in
  `UserDefaults`, prefs or `session.json` — an account token reaches every
  profile and the billing, which is more than any owner token it mints — list
  what the account holds, and hand the minted pair to the same state the
  create path writes.

  The per-shell door guard is what said this was unfinished: the union read
  zero while iOS, Android and Windows each could not reach either route.

### Fixed

- **The Studio's run button answered a 500, and the suite proved the walls.**
  `widgets.run` loaded a widget through `read`, which renames the `version`
  column to `revision` on the way out — and then asked the returned dict for
  `["version"]`. `KeyError`, before the widget ever started, on every press
  since the Studio shipped.

      asked     does a widget run inside all four walls
      mattered  does the button that runs one work at all

  `test_the_widget_cannot_leave_its_box.py` is nineteen cases deep on the
  sandbox and every one of them calls `run_source` with a source string. Not
  one ran a *stored* widget. The half that was hard to get right was covered
  exhaustively; the half that was one line was covered by nothing. Two cases
  now drive the stored path through the API the way a person does.

- **The guard that catches vocabulary drift was the one this product did not
  have.** `test_the_shared_vocabulary_matches_the_sibling_products` was
  carried by JIM-mini and PDI and recorded against QRME. Most of the shared
  field vocabulary was written here, so this was the one repository free to
  edit a label and have nobody notice until a sibling's suite failed for what
  looked like the sibling's fault. Ported, and it fired on arrival: `what`
  read 内容 here and 事项 in JIM-mini, with nine languages — Japanese
  included — agreeing on 内容.

## [0.75.0] - 2026-08-15

### Changed

- **The console-untranslated ceiling goes back to 1.** It was 1, then 58 when
  0.69.1 taught the reader to see a sentence chosen at render time, and the
  file said in its own closing paragraph that the next rounds would take it
  back down. This is those rounds.

      asked     is this screen translated
      mattered  is every sentence on it translated, including the ones
                a condition picks between at render time

  Fifty-seven strings across Settings, Robots, Selling, Workshop, Referrals,
  Assist, Desk, Identity, Lobby and Remainder now have keys and ten
  translations each. Where the table already held the same English under
  another key, the new row copies that wording rather than inventing a second
  one — two words for one thing in the same language is the defect
  `native_split_wordings.txt` exists to catch, and it is cheaper not to create
  it than to reconcile it later.

  Two of the fifty-seven were not translation work at all, and they are the
  ones worth naming. Lobby rendered a bare `"s"` as its own JSX node after a
  session count — English pluralisation as a suffix, which is not how the
  plural works in most of the other nine languages and was never going to be.
  Remainder did the same with `thing`/`things`. Both are one whole sentence
  per number now. A reader looking only for untranslated words would have
  found `"s"` and shrugged; the reason it is on the list is that it is not a
  word.

  The row that stays is `TheMark: AI ·`, and it stays for the reason that file
  has always given: the designation is quoted, not written. The server
  hardcodes those two characters into `design.line`, so translating the
  quotation to `IA ·` would put a mark on the screen that the product never
  produces.

## [0.74.0] - 2026-08-15

### Changed

- **A post no longer stops inside a word.** Reported from the live wall with a
  screenshot: a profile had been asked for a specification and answered at
  length, the wall took the first two thousand characters, and the reader got
  a sentence that ended mid-word — with the reader underneath, in the thread,
  asking it to finish. The whole document took **five** of those continuations
  to come out.

      asked     does the post fit
      mattered  does the reader know when it did not

  Two things were wrong and only one of them was the number. The cap was set
  when the only author was a person at a keyboard, and nothing technical held
  it there — `posts.content` is TEXT, no full-text index reads it, nothing
  searches it with LIKE. Five continuations is a measurement rather than a
  guess: the thing being posted was ten times the ceiling. It is 20000 now.

  The honesty is the half that lasts. A raised ceiling is one somebody writes
  past later, so `parts()` turns anything over the cap into a numbered series
  where every piece says where it sits and every piece but the last says it
  continues — a reader who lands on part three knows they have missed two.
  `publish` still refuses over-length and `publish_series` splits: somebody at
  a keyboard who has written past the ceiling should be told, not silently cut
  in half, and a profile answering at length has no keyboard to be told at.

  A cut is allowed. A silent one is not — the same answer this estate gives to
  the refusal that names its cause and the renderer that says it cannot draw a
  model rather than drawing a poster.

### Fixed

- **Every face imported from a phone was filed under "somewhere else".** The
  skin shelf has named eight systems since the avatar deck was written — Ready
  Player Me, Bitmoji, Meta, Memoji, Xbox, Zepeto, Mii, and a catch-all — each
  with the provider's own export route in that provider's words. The console
  grew a picker for it. The three shells fetched the shelf, counted it, put the
  number on screen, and then posted `source: "other"`.

      asked     did the import go through
      mattered  does the record say where it came from

  `import_avatar` takes a source for exactly one reason, stated in its own
  docstring: the import is written onto the profile's record as a source item,
  *so the face's provenance survives next to the face*. Filing all of it under
  the value that means "somewhere else" is that provenance thrown away at the
  last step, by the code that had just been handed it.

  Android's binding was the clearest form: `avatarMarket()` decoded the eight
  rows and returned `arr.length()` — a binding that reads the answer, discards
  it, and returns a count of what it discarded. All three shells now carry the
  rows, offer them as a picker, and show the `how` line beside the chosen one,
  which is the sentence that turns a URL box into something somebody can
  actually complete and which only the console has ever rendered.

  Windows refuses rather than falling back if the shelf did not load: a wrong
  provenance is worse than a refused import.

- **The sidebar was checked and the other forty-nine files were not.** This
  console's nav guard has asserted since 0.27.0 that every tab in `NAV` has a
  `nav.<id>` row. It looked at the sidebar and nowhere else. JIM-mini shipped
  the same defect a dozen releases later in a different file — a tab reading
  its own key between two real words — and the fix that came back from it is
  the general case: every key any screen writes down literally must have a
  row, across the whole console, not just the fifteen the navigation uses.

      asked     does every tab have a label
      mattered  does every key any screen asks for exist

  Nothing was missing here, so this is a latch on work already done rather
  than a new backlog. The floor under the tab scan is registered rather than
  written into the assertion, which takes it out of the unregistered-floor
  record on the way past.

## [0.73.0] - 2026-08-14

### Added

- **The briefcase — hand a profile something to read, and it keeps it.** A
  link pasted into a turn was already fetched and read: `interaction.py`
  pulled the first URL out of the message, visited the page through the same
  offline-gated fetcher every outbound path uses, and put the visible text
  into *that turn's* system prompt. It worked, and then it evaporated. The
  next turn — the one where you actually discuss the thing — carried no page
  at all, so keeping the conversation going meant pasting the link again, and
  every paste re-fetched the whole of it and re-sent the whole of it.

      asked     can the profile read what you hand it
      mattered  can it still remember it on the next turn

  And a link was the only thing you could hand over. A photograph, a filing,
  a spreadsheet, a video — the material a conversation is usually *about* —
  had no way in, so the only route to "tell me about your patents" was to
  retype the patents.

  `qrme/briefcase.py` is a briefcase scoped to one conversation: the pair
  (profile, interactor). Material is read at import — pages through `scrape`,
  plain text as itself, PDFs through their text layer, `.docx`/`.pptx`/`.xlsx`
  out of their XML — distilled **once** into a digest, and it is the digest
  every later turn carries. A forty-page filing enters the prompt at the size
  of its reading, paid for a single time instead of on every turn.

  Deliberately not a `source_items` row. Source material is what a profile
  recalls as its own and every visitor sees it; this belongs to the two of
  you and stays there, the same line the clinical-notes block already draws.

  What it will not do is pretend. This deployment cannot see a photograph or
  watch a video, and a scanned PDF has no text in it to find. Those import
  anyway, carrying whatever the person said they were, and the prompt states
  plainly that the profile has *not* seen them and must not describe them.
  `POST /profiles/{id}/briefcase/link`, `…/file`, `GET …/briefcase`,
  `GET …/briefcase/{item}` — which returns the extracted text, because "it
  read your document" is a claim somebody is entitled to check — and
  `DELETE …/briefcase/{item}`, on the console and all three shells.

- **The avatar is not the profile.** A portrait was an image and nothing
  else, so a video loop, a rigged model, or a bought character skin had no
  way to be somebody's face. `qrme/presentation.py` names what an asset *is*
  — `image`, `video`, `model`, `scene` — reading it off the address where the
  address says (query strings stripped, so `figure.glb?sig=…` is still a
  model) and taking the owner's word where it does not. Seven presence
  states — idle, listening, thinking, speaking, paused, processing, error —
  ride in the same block. It travels inside `avatars.render()` rather than
  behind a route of its own, which is the difference between one change and
  four new doorless rows.

- **A skin from the market, picked the way a voice is.** The console's
  provider tiles were already the pattern for "bring your own": eight drawn
  tiles — Ready Player Me, Bitmoji, Meta Avatar, Memoji, Xbox, ZEPETO, Mii,
  and one for anything else — plus a URL box, a torso box and a file upload.
  Six `skin.*` keys in ten languages.

- **A starter has a body to stand up in.** The 34 starters shipped with
  portraits and nothing below the collar, so every one of them was a head in
  a conversation screen built around a figure. `qrme/skins.py` carries a
  standing pose per starter and *composes* the portrait brief rather than
  restating it, so the two cannot come to describe different people.

- **The profile remembers the person, not the browser.** Memory was keyed to
  the interactor a device minted on first visit, so signing in on a laptop
  and then a phone met the same profile as two strangers — and clearing a
  browser lost the relationship outright. `interactors.account_id` attaches a
  visitor to an account; `accounts.signin()` hands back the interactor, and
  `adopt` claims the stranger this device has been talking as (403 if another
  account already owns them).

### Changed

- **One picture for a face that is not there, not five.** `render()` returned
  `asset: None` for a portrait-less profile and left each surface to invent
  something. Five did, differently: initials on Home and in a Top 8, a blue
  orb on the talk surface, initials again on the beacon landing page, and —
  the sharpest one — an Android overlay that drew a monogram *always*, never
  reading the portrait it was sent, so one sticker scanned on a phone and on
  a laptop showed two different profiles. On a profile whose name is hidden,
  a monogram is the hidden name.

      asked     does a profile with no face have something to show
      mattered  does it show the same thing everywhere

  `render()` is now terminal about the face: no portrait means the empty
  frame, which reads as something to fill rather than as a thing. The orb,
  both monograms and the `initials` field on `/b/{id}/card` are gone, and
  `avatars.shown()` is the same decision for list payloads that cannot
  afford a full render per row.

- **Enter sends, and the button says Send.** The composer on somebody's
  homepage was a textarea with no key handler, so the only way out of it was
  the button — and the button read "Talk to their profile", which describes
  the screen rather than naming the act. Enter now submits (Shift+Enter still
  breaks the line) and `prf.talk` is "Send" in all ten languages.

## [0.72.0] - 2026-08-14

### Added

- **Their homepage — where pressing a face actually takes you.** A friend's
  picture on Home opened a panel with their name and tagline on it, and
  underneath it the *signed-in* profile's memory count, engagement average
  and moderation rate. Four different friends drew four identical screens,
  because only the header was ever theirs.

      asked     does pressing a face open something
      mattered  is what opens theirs

  `app/src/screens/Profile.tsx` is that screen: their page as they built it
  — theme, accent, about, links, and their own markup — their Top 8, which
  are eight more doors so the walk continues and Back retraces it, their
  wall, their photographs, their footage, and the three things a visitor may
  actually do. It carries no numbers row, and that absence *is* the fix:
  `GET /profiles/{id}/stats` is owner-only, which is exactly how the old card
  came to be showing yours in place of theirs. A synthetic profile has the
  same homepage — here a friend is a profile, so this is one screen and not
  two.

  Their markup renders in a sandboxed frame rather than in this document.
  `pages.py` sanitises on the way in and does it well; this is about who pays
  if it is ever wrong. React's escape hatch is a floor at zero in this repo,
  and being the screen that finally wanted it is not a reason to move it.

- **The homepage reaches the phones.** The console got the screen above; the
  three shells got the route and nowhere to land. A friend on a phone was a
  row of text with a remove button beside it — you could see that somebody
  was your friend and never see one thing they had made.

      asked     can the phone list your friends
      mattered  can it open one

  `ProfilePageView` (iOS), `ProfilePagePanel` (Android) and the visiting card
  on `PeoplePage` (Windows) carry their page, their Top 8 walking onward,
  their wall, their uploads split into photographs and footage, their friends
  and what they offer — with the same three visitor actions and the same
  absent stats row, for the same reason.

  On the way, `PageCard` on all three shells was a binding narrower than its
  route: theme, tagline and about, out of a payload that also carries the
  accent they chose, the eight faces they arranged, their links, their offers
  and whether they ever decorated the page at all. Android's read the route
  and flattened the whole answer to `"theme · tagline"`. A binding that
  narrow is how a shell ends up with no screen it *could* build.

  **The markup block is named rather than drawn, and that is deliberate.**
  The console renders a page's own HTML in an iframe with `sandbox=""` —
  every capability off. No shell has an equivalent: rendering it would mean
  introducing a `WKWebView`/`WebView` to run a stranger's stored markup, and
  a web view's default posture is nothing like `sandbox=""`. Windows has one
  WebView2 and it runs the app's own signature ceremony, which is not the
  same proposition. So the page renders from its structured parts, which is
  most of it, and a line in the reader's language says the markup is there
  and where to see it.

      asked     does the phone show their page
      mattered  does it show it without giving a stranger's markup
                somewhere to run

- **`GET /profiles/{id}/media` — the other side of the upload door.** Uploads
  have been accepted since 0.42.x with nothing that lists them: media was
  reachable only through the wall post it happened to ride on, so a
  photograph posted a year ago was in practice gone and an upload attached to
  nothing was invisible from the first second. `media.gallery` answers newest
  first, narrows to `image`/`video`/`file`, and is public for the same reason
  the wall is — this is what a visitor came to look at.

      asked     can somebody put a photograph here
      mattered  can anybody find it afterwards

### Fixed

- **A room could not be opened without a topic.** `RoomCreate.topic` was
  required by that one line and optional everywhere else — `create_room`
  writes it straight through, the rooms list declares it nullable, and the
  console has always sent nothing when the field is left blank. So pressing
  Open on the Rooms screen without typing a topic answered 422 "Topic — Field
  required", on a form that offers the topic as a blank you may skip. A room
  opened *with a person* is named by who is in it.

- **The cross-product smoke assumed a gate that JIM stands down.** `suite/
  smoke.py` drove a Basic account into JIM's `synthetic_agents` gate and
  asserted the 402. Correct while the gate is enforcing, wrong the moment the
  beta stands it down — and the run died seven steps in reporting a
  specialist that "does not accept delegated work", which reads as the tandem
  coming apart. It now reads the posture off `/plans` and asserts the branch
  in force; JIM publishes `enforcing` there so it can.

## [0.71.1] - 2026-08-14

### Fixed

- **The API did not import on Windows, and the suite could not see it.**
  `qrme/widgets.py` imported `resource` at module scope. It is POSIX-only,
  and `qrme/api.py` imports `routers/studio`, which imports `widgets` — so
  this was not "the sandbox is unavailable on Windows", it was *the whole
  API failing to import there*. The frozen desktop backend died on first
  run with `ModuleNotFoundError: No module named 'resource'`, which failed
  the Windows installer job, which skipped the release job, which is why
  0.70.0 and 0.70.1 published with **no installers attached at all** — not
  even the macOS and Linux ones that had built cleanly.

      asked     does the module import
      mattered  does it import on every platform we ship

  Absent, it is the missing-wall case wearing different clothes, so it is
  handled the way this module already handles a host with no `unshare`: the
  import is allowed to fail, `sandbox_available` returns `widgets.no_rlimits`
  in the reader's own language, and every other route on the API still
  answers. A widget still never runs with three walls instead of four.

  The suite runs on Linux, where `resource` is present, so no test could
  have caught this by importing anything. The new guard is a property of the
  *text* instead: no module under `qrme/` may import a module some target
  platform lacks unless the import is wrapped in a handler for its absence —
  and the guard is shown the exact line that shipped, and required to object
  to it.

## [0.71.0] - 2026-08-14

### Fixed

- **A player handed no origin will not play.** From the beta, on a phone: a
  YouTube post on the Wall rendering a grey panel reading *Error 153 — video
  player configuration error*. The link was fine and the embed was fine.
  `pagehead.HEADERS` sends `referrer-policy: no-referrer` on every HTML
  response, and the reason is written where it is set — a page reached from a
  QR sticker must not tell the next host which sticker somebody knelt over,
  because the referrer *is* the beacon. Right for that page, and it applies to
  the console too, which embeds other platforms' players. A player handed no
  referrer cannot check whether it may embed on the site it finds itself in,
  so it does not play, and what a person reads is the other platform's error
  code.

      asked     does the page carry the header
      mattered  does the thing inside the page still work

  `referrerPolicy` on the element overrides the document's policy for that one
  subresource, so the beacon pages keep `no-referrer` and the two players get
  `strict-origin-when-cross-origin`: the host, never the path. The platform
  learns the origin of an embed it is already serving, which the request
  itself told it, and learns it only when somebody presses play — until then
  there is no request at all. House-held footage was never affected; it is our
  own `<video>`, with no third party to satisfy, which is why the defect
  looked like one broken post rather than a broken feature.

### Changed

- **The frame was never the screen.** From the beta: the deck swiped, and what
  it swiped between was still a card — a header above the frame, a caption
  below it, and the screen's own title above all of that, so the video got
  whatever height was left over, which on a phone is about half.

      asked     can you swipe to the next one
      mattered  is the one you are on the screen

  A pane holding footage is now the footage, and the words are on top of it:
  the media fills the pane absolutely and the pill, the position and the
  caption ride over it at the two edges, on scrims rather than panels, so
  nothing sits between the reader and the picture. The screen's own header is
  gone from this deck — its two lines moved onto the rules pane, which is the
  one that already explains what the feed is. A pane that is a room, a desk or
  a party has no frame to ride on and keeps the ordinary stacked layout,
  decided by the item's own kind rather than by whether a frame happened to
  load. Back and Next stay, on the bottom scrim, for the keyboard, the mouse
  and any gesture that does not land.

## [0.70.1] - 2026-08-13

### Fixed

- **The interpreter's version was the one way the sandbox could lie.**
  `sandbox_available` asked whether *an* interpreter existed and nothing
  more, so a host carrying Ubuntu's own Node 18 answered **available**: the
  editor opened, the run button lit, and every widget came back failed on a
  flag its author never typed. The filesystem wall is node's own permission
  model, which arrives in Node 20 — a binary that cannot build the wall is
  the missing-wall case wearing different clothes, and this module's promise
  is that it refuses rather than running with three walls instead of four.
  `MIN_NODE`, a version probe where unreadable counts as too old, and its own
  refusal in ten languages. The floor is guarded by measurement rather than by
  a literal: the interpreter this host offers either passes `MIN_NODE` or does
  not, and either accepts the flag or does not, and those two answers have to
  agree — so a floor lowered under an interpreter that rejects the flag fails,
  and so does one raised above an interpreter that accepts it. Found on a live
  host, not in review.

  Nothing else changes. 0.70.0 was tagged before this landed, so its
  installers ask whether *an* interpreter exists and not whether it can build
  the wall — on a machine carrying Node 18 or 19 they light the run button
  over a feature that cannot work. A deployment with no interpreter at all is
  reported honestly by both.

## [0.70.0] - 2026-08-13

### Added

- **Curating the transcript by hand.** `POST /memory/{interactor}/strike`
  deletes turns selected by id, scoped to the pair — a borrowed id strikes
  nothing — and `PUT /memory/{interactor}/turns/{id}` rewrites one turn: the
  new words face moderation, a profile turn's synthetic-media credential is
  dropped, and the edit is recorded as a fact but never the old words. Edit
  mode with checkboxes, delete-selected and tap-to-rewrite in the console and
  on all three phones.
- **Export via QR.** A single-use ten-minute ticket whose code carries the
  ticketed URL and never the owner token; the bundle is served exactly once.
  Both ends on all four clients.
- **The reports come home.** `POST /v1/problems` lives on this backend, with
  `GET /v1/problems` behind `QRME_PROBLEMS_KEY` or the backend's own machine
  — a live failure map of every version, counters only, never content.
- **The waiting side of the stranger pool.** `GET /connections/mine`, polled
  by all four clients, so a person who asked for a stranger stops waiting on
  a screen that had already moved.
- **Widgets — somebody's own code, in a box.** A widget is a function its
  author wrote, kept against their profile and run on the backend in a
  namespace with no interfaces, one readable directory, no child processes,
  a capped heap and a wall clock: `qrme/widgets.py`, with sixteen escape
  attempts run through the real runner in
  `tests/test_the_widget_cannot_leave_its_box.py`. If the network cut cannot
  be built on a host, the runner refuses to run anything at all rather than
  running with three walls instead of four. `GET /studio/limits` publishes
  the allowances and says so honestly when the box is unavailable, so no
  screen states a number the runner does not hold. Six owner-scoped routes,
  a console screen and a page on all three shells.
- **An agent that edits somebody's own app.** Say what you want changed and
  it does it, through the same doors you would have used yourself:
  `POST /profiles/{id}/authoring/turn`, owner-only, forwarding the caller's
  own credential rather than minting anything broader. Its reach is a
  written allowlist of ten — `qrme/authoring.py` — and two guards make the
  list load-bearing: every row resolves against the app's own route table
  and every row that *changes* something must land on a door that demands
  the owner, and the profile is bound from the session rather than named by
  the model, so a model answering with somebody else's id does not move the
  request off the person driving it. `GET /studio/agent` publishes the ten
  sentences so *what can this thing do to my account* can be read before it
  is used. What it did is listed under what it said — one line per door it
  went through — because an agent that describes an edit in prose is asking
  to be believed. The conversation stays on the client: the agent has no
  memory of its own, so *forget this* actually forgets. Nothing in its
  instructions names this machine, its paths, its environment or its
  sibling services, and a guard reads both the prompt and every sentence
  written for a person, because a leak is as likely to arrive in prose.
- **The Feed is a deck you swipe.** One item fills the screen and a swipe up
  brings the next, snapped by the browser's own `scroll-snap-type: y
  mandatory` with `scroll-snap-stop: always` rather than a gesture handler
  guessing from a wheel delta. Vertical footage fills the frame; horizontal
  is centred and letterboxed rather than cropped into a shape nobody shot
  it in. Footage this deployment holds plays muted the moment its pane is in
  front of you, one decoder at a time; footage held elsewhere is a
  full-frame facade that waits for a press, because auto-rendering an embed
  as it scrolls past would make the feed's own sentence about itself false.
  `feed.autoplay` turns that off — off by default, kept on the device.

### Fixed

- The console's own CSP named no `frame-src`, so it fell back to
  `default-src 'none'` and the browser refused **every** allowlisted video
  player as a white rectangle. The policy now derives from the platform
  allowlist itself, with a socket-level test binding the two.
- The `✓ real photo` pill swallowed the Discover portrait under font
  boosting; marketplace chips were full-size buttons with their effect below
  the fold; the minimized agent light was a solid disc parked over content.
- A room now renders its seats as tiles, the last voice lit; the Wall
  composer no longer carries ghost placeholder text; tab changes land at the
  top of the new screen.
- **The apology for a failed route is in the reader's language.** The
  catch-all is a middleware — `@app.exception_handler(Exception)` sits
  outside the CORS layer, so a 500 raised there comes back without the
  header and the console reads it as unreachable — and being a middleware,
  no guard was asking it anything. Its sentence sat inline in English;
  `i18n.SERVER_ERROR` is now a named constant translated like every other
  refusal.
- The onboarding screen's Show/Hide, Creating…, Checking…, Signing in…,
  Resetting…, Verify & continue, Set new password and Create My Profile were
  English on a screen that translates everything else — invisible to the
  extractor because a string chosen at render time is a
  `ConditionalExpression` and not a `JsxText` node.
- **A memorial does not redecorate.** The agent's turn and a widget's run
  both drove a profile without asking whether it may still act. The turn
  takes `require_may_publish` — the page it edits is a public face, and a
  profile restricted pending an objection review is not putting new work in
  front of the person contesting it, whether a person typed the change or a
  model did. The run takes the narrower `require_may_speak`: a widget's
  answer goes to its author alone.
- **The console's own l10n table had stopped being readable in one place.**
  The Studio rows were written single-line in a file whose entries are
  multi-line, and the table reader matches an opening brace to a closing one
  at the start of a line — so each single-line row swallowed everything up
  to the *next* multi-line entry's close, and `feed.autoplay` fell out of
  the audited table entirely. Thirty-six rows rewrapped; the guard on the
  guard is exact again.
- Three wire names carried two shapes each: `limits` (a list of sentences
  about a signature tier, and a dict of numbers from the widget runner) is
  now `allowances` on the runner; a step's `status` and the tutorial's
  `steps` are `answered` and `acted`. The Android widget bindings were
  top-level extensions in a file of class members, which filed every key
  they read under the wrong route.

### Changed

- `scripts/jsx-text.mjs` reads string literals in child position — both
  branches of a ternary, either side of `&&`/`||`/`??`, the pieces of a
  concatenation — and still refuses call arguments, so a translation key
  stays a key.
- `native_dead_keys.txt` 273 → 28, and what remains is a named ledger of
  guard-pinned fixtures rather than a backlog. `native_screens_untranslated`
  reads 0/0/0.
- The three-repo guard estate: `shared_guards.txt` 469 → 489,
  `guard_divergences.txt` 136 → 121, both byte-identical in QRME, JIM-mini
  and PDI.

## [0.68.0] - 2026-08-12

### Added

- **The memory door.** `GET /profiles/{id}/memory/{interactor}/account`
  answers "what do you remember about me" from the records rather than by
  generation — the distilled paragraph as it stands, how many turns were
  folded into it, how many are still in the recent window, first and last
  contact. `POST .../memory/{interactor}/forget` is the scalpel beside the
  erase-all: every turn whose text carries the named words is deleted, and
  the distilled remembrance is dropped to re-fold from what remains, never
  from what was struck. Both doors answer to owner or interactor, in the
  console and all three shells.
- **The steering lock.** `POST /profiles/{id}/steering/lock` holds the dials
  where they stand: while the lock holds, every steering write — the owner's
  own slip, a compromised session, any future automation — answers 423 in
  the reader's language, through the steering door, the hub, and the robot
  door alike. `DELETE` turns the key; the lock and the key are both the
  owner's.
- **The card carried in.** `POST /profiles/import/card` reads a
  `chara_card_v2` / `chara_card_v3` character card — raw JSON or embedded in
  a PNG's text chunk — and seeds a fictional profile through the same
  creation path as every other: identity into the persona, greeting and
  example dialogue into source material with honest provenance. What it
  refuses, it names: `system_prompt`, `post_history_instructions` and
  jailbreak blocks are harness instructions aimed at somebody else's model,
  withheld item by item in `withholdings` with reasons.
- **The room that forgets on purpose.** `POST /profiles/{id}/rehearsal`
  opens a practice room for the hard conversation: the profile plays the
  named counterpart, every reply is marked `remembered: false`, the
  transcript lives only in the room, and closing the room wipes it. Nothing
  said inside ever reaches messages, engagement or the remembrance.

### Fixed

- The identity camera never rendered after permission was granted — the
  stream was attached in a frame callback that raced the conditional
  `<video>` element's mount. The stream now attaches from an effect keyed on
  the capturing state, and unmounting releases the camera.
- A departed or restricted profile could be made to speak in a rehearsal
  room; both rehearsal doors now ask `require_may_publish` before anything
  else, exactly as chat and compose do.

## [0.67.0] - 2026-08-12

### Added

- **The licence carries the substance.** A finetune or clone derive now
  copies the profile's own knowledge items, steering dials, appearance and
  demographics onto the buyer's agent; a clone adds an aggregate adaptation
  summary — dimension means across every relationship, count only. What may
  never travel stays behind by rule: interactor messages and per-relationship
  embeddings, the voice print, vaulted content, and marketplace pack items.
  Every derivation writes a manifest (`carried` / `withholdings`, each
  withholding with its reason), returned to the buyer at derive time and
  readable on the owner's grants list, in the console and all three shells.
- **AI for lease.** `POST /organizations/{org_id}/lease` seats somebody
  else's consult-licensed specialist as a department: the fee accrues to the
  specialist's owner at seating time, the lease rides the owner's licences
  list beside grants, and the same revoke door covers both. A revoked lease
  — or a terminated source profile — leaves the department standing but
  silent, named in every coordination it no longer speaks in.
- **The moving image.** The avatar response carries a motion block — style
  (still / breathe / lively, set through the existing avatar door), energy
  and warmth derived live from the latent persona embeddings, and a tempo
  the clients animate at. Derived, not stored, and riding the same response
  as the AI badge, so nothing can animate the face without the disclosure.
- **The room is remembered.** A chat turn without fresh environment context
  recalls the latest stored context (six-hour window); the prompt treats it
  as where the person most likely still is, and the echo marks it
  `remembered` so clients can tell fresh from recalled.

### Fixed

- Termination now revokes an organization's lease along with every other
  capability a third party holds — a terminated specialist's desk went on
  speaking in coordinations before the guard caught it.

## [0.66.0] - 2026-08-12

### Version alignment

No QRME code changed this round. The work was JIM-mini's offline coach
stack: the add-and-norm pipeline over stored knowledge and current
readings, the jampacked pack, the deposits paid model turns leave
behind, and the curriculum JIM studies from. The three products are
cut together, so one number names one combination of all three.

## [0.65.0] - 2026-08-12

### Added

- **The door into a live room.** `POST /rooms/{room_id}/join` seats a
  signed-in interactor in a standing room that is already open — eight
  seats, the same seat held on a second knock, "this room has closed"
  and "this room is full — eight seats, and every one taken" refused in
  the speaker's language. The lobby's pitch had promised "step in
  beside them" while every press opened a fresh, empty room; the
  promise has behavior under it now. The console lists the live rooms
  with a Join on each row, and all three phones walk through the same
  door.
- **A standing room is one place, not a stamp.** Pressing a standing
  room's name used to mint a fresh copy of it — twelve presses of "The
  front porch" made twelve empty porches, and nobody ever met anybody.
  `POST /rooms/templates/{key}/open` now joins the newest live room
  holding that topic when one has a free seat (or already holds you),
  and only opens it fresh when nobody has it open — with you and your
  profile in it, as rooms always have. A full porch gets a second
  table: when all eight seats are taken, the next press opens the room
  again rather than turning anyone away. The response says which
  happened, unknown keys are refused by name, opening fresh without a
  profile picked is refused with directions — all in ten languages —
  and the console, iOS, Android and Windows each press through it.

### Fixed

- **A face is a door to the person.** Tapping a friend's picture on
  the console's home screen landed on the list of friends — the place
  the strip's label already goes. The faces now open that friend's own
  page, the one a visitor sees — portrait, tagline, about, links —
  with a translated Close to step back out. Reported from the field,
  fixed the same day.

## [0.64.0] - 2026-08-12

### Added

- **The remembrance.** What a profile keeps of a person between
  conversations, distilled: `GET /profiles/{id}/memory/{interactor}/
  remembrance` reads it, the chat carries it into every reply, and
  erasing the memory erases it. On the console's Memory screen and all
  three phones.
- **The handed link.** Paste a URL into the chat and the profile reads
  the page's public words before answering — with the offline posture
  saying so honestly when nothing may leave the machine.
- **The pasted link connects the account.** The social connect form
  reads a pasted profile link for what it already says — the host names
  the platform, the path names the account — and refuses a hashtag with
  a sentence that explains itself, in ten languages.
- **The torso form.** An avatar can carry an upper-torso render,
  imported beside the face; the talk overlay stands it at full figure,
  and the AR rule is written where the feature lives: upper torso,
  scaled 1:1 in the live feed.
- **Marketplace folders.** The catalogue groups by each listing's first
  tag into folders, the feature cards move above the list, and search
  results stay flat.
- **Top friends on the front page.** The faces the spaces use, as a
  strip on Home, the founder standing first.
- **The vastscape.** Watch-together on a TV or console, presence
  bubbles resting in the scene — drawn as screens 194 and 195 and
  taught by the party lesson.
- **The connections catalog steps out.** The backend has carried a
  forty-app catalog across six providers — Apple Intelligence, Google
  Gemini, Microsoft Copilot, Canva, smart glasses, gaming consoles —
  and the console's connected-apps card offered exactly one hardcoded
  Google Calendar button in front of it. The card now asks the catalog:
  provider picker, app picker, the chosen app's directions and
  capabilities shown before connecting.
- **The standing rooms.** A new user opened the Rooms screen, found the
  list empty, and left. Twelve standing rooms — blueprints, not rooms —
  answer at `GET /rooms/templates`, from The Front Porch (chat) to The
  Vastscape (VR, watch-together). Opening one goes through the same
  `POST /rooms` as typing the topic by hand, so a template grants
  nothing the form does not. The console shows them above the live list
  with one-press "Step inside"; all three phones fold them into their
  rooms doors.
- **The footsteps.** A counter in the console's top-right corner: how
  many people hold verified accounts, as an aggregate — no name, email
  or id rides with the number. It travels on `/health`, the request
  every client already makes at launch for the version handshake, so it
  cost no new door. The sibling products carry the same chip in the
  same corner in the same ten-language wording.

### Changed

- **The chat hands back its walls.** The receding-grid backdrop and the
  sticky presence bubbles floated the session's names and portraits
  over the words people were trying to read; both came out on a field
  report the same evening they shipped. Presence rendering belongs to
  the rooms and the vastscape, where there is a scene to stand in — a
  text thread is its own scene. The talk overlay's avatar and the front
  page's top-friends strip stay exactly as they were.
- **The footsteps chip shrank to a footprint** — just the mark and the
  number, the sentence in the tooltip — after it sat on top of the
  chat's wardrobe box on a phone.

### Fixed

- **The vault hiccup no longer silences the chat.** A failed readback
  of one sealed source item used to 500 the whole conversation; the
  chat now degrades to the sources it can reach and says nothing false
  about the ones it cannot.
- **The guard that only existed where the bug never was.** The
  `</script>` hardening of `_js` shipped in 0.63.0 in all three
  products; the test holding it existed in none. It stands in all three
  suites now and enters the shared manifest.
- **The login wall is not source material.** A Facebook import
  "succeeded" by storing the platform's login page as the profile's
  source material — which the persona then quoted back in chat as
  though it were the owner's own writing. The fetch now recognises a
  wall by its title and refuses with the honest workaround, translated
  into all ten languages: copy the profile's text while signed in and
  paste it into collect.

## [0.63.0] - 2026-08-11

### Added

- **The chat follows the conversation.** The reply used to land below the
  fold and stay there; the log now scrolls to the newest message as it
  commits — an effect keyed to the messages themselves rather than a
  callback racing the render — and an approved profile's replies are
  spoken aloud while talk mode is open, through the same approved-only
  speech gate the speaker toggle uses.
- **The talk surface shows the face.** The microphone was a button that
  filled the composer; it now opens a full-screen talk surface with the
  profile's portrait front and centre, pulsing while it listens, the
  transcript shown as it is heard, the reply spoken back. The sibling
  product's Guardian is a voice with no face, so its surface is an orb;
  a synthetic profile is a persona, and a persona has a face. The orb
  appears only for a profile with no portrait yet, next to a pointer at
  where to get one.
- **The avatar deck.** Identity's portrait card becomes a deck with
  three shelves. *Pick a character*: the starter portraits as a tappable
  grid — the asset path comes from the brief itself, because the server
  names where its portraits live and the client never spells a path.
  *Your own face*: import a photo through the existing media door, or
  capture it with the camera from five angles — front, left, right, up,
  down — every frame uploaded and kept as provenance, the front frame
  becoming the portrait. *An avatar you already have*: Ready Player Me,
  Bitmoji, Meta Avatars, Apple Memoji, Xbox, ZEPETO, Mii — imports, not
  integrations: the person exports on the provider's own surface and
  hands QRME the image; nothing calls a provider API or holds a provider
  credential, and the provider's license keeps governing the avatar.
  `GET /avatars/market` lists the shelf with the how-to for every
  source; `POST /profiles/{id}/avatar/import` (owner-only) sets the
  portrait through the same pipeline as a starter face — the AI badge
  and the likeness record ride on the render — and writes the import
  onto the profile's record as a source item. Doors on the console and
  all three native shells.
- **The imported link, finally visited.** A social connection has
  carried the account's public address since the day it was pasted, and
  the profile only ever knew the handle. `POST /social/{cid}/scrape`
  goes to the address and keeps what a browser would show anybody — the
  title, the metadata bio, the visible text — as a source item on the
  profile's own record, provenance written in. An offline deployment
  refuses before any socket opens; the gate lives inside the fetcher
  itself, so a second caller added tomorrow inherits the check.

### Fixed

- **The console fits the phone it runs on.** Two layout defects, one
  root: a grid item refuses to shrink below its content, so the content
  pane grew past its track, the app overflowed the viewport, and the
  page itself half-scrolled instead of the pane. `min-height` and
  `min-width` zero let the tracks clamp; the app height tracks `100dvh`
  where the browser has it, so the bottom row sits above the URL bar;
  the sidebar scrolls on its own where a landscape phone gets the
  desktop column; the onboarding card no longer overflows a narrow
  screen. The same defect was in all three consoles and is fixed in all
  three.

## [0.62.0] - 2026-08-11

### Version alignment

The three products are cut together, so one number names one combination
of all three. JIM's phones reached parity with its console — eleven rounds in one branch: every backend route gained a door on iOS, Android and Windows (the doorless ledgers close at the four by-design rows), the voice pair landed on all three shells with the device's own voice as fallback, Android learned to say PATCH through a test-pinned override, and the most-touched screens swapped their English for the ten-language tables. No QRME code changed.

## [0.61.1] - 2026-08-11

### Added

- **Ability is not a gate.** An accessibility statement with a door under it,
  on every client. The console's new **Accessibility** screen — reachable
  *before* sign-in via `#access`, from the public landing's tab row and from
  onboarding — names the needs this product is built for (blind, deaf, mute,
  motor, cognitive, dyslexia, motion sensitivity) and says, for anything the
  list misses, that the gap is in the list and not in the person. Under the
  statement sits a three-question report form: what were you trying to do,
  what stood in the way, what would help. `POST /access/reports` takes those
  answers with **no account, no token and no name** — the `access_reports`
  table has no identity column to fill, which is where that promise actually
  lives — and seals each report to the PDI vault when one is configured.
  Reports are never relayed to the shared error collector; they are read back
  by `GET /access/reports` under the deployment's reviewer token alone. The
  iOS, Android and Windows shells carry the same statement and the same form.
  Screen 193, tutorial lesson, helper-dock directions and ten-language copy
  throughout.
- **The wall's uploads say what they show.** The composer asks for a
  description in the uploader's own words; it rides the upload, lands in the
  new `media_alt` table, and returns on every read — the receipt, the post,
  the feed — as the image's `alt`, read aloud by screen readers.
- **A ledger of known gaps that only shrinks.** `tests/a11y_backlog.txt`
  opened this release with three admitted barriers and closes it at zero:
  wall uploads with no description, chat replies no screen reader was told
  about (the conversation log is an `aria-live` region now), and shells that
  carried the form without the statement. Each closure is held by a test —
  one of them shared across the three products, taking the common guard
  manifest to 461 — and the ceiling ratchet means a new gap can only enter by
  a visible, deliberate edit.
- **The console honours `prefers-reduced-motion`**, sets the document's
  language attribute to the visitor's language, and every image carries a
  description — each enforced by `test_ability_is_not_a_gate.py` rather than
  promised.

### Changed

- **Signup opens for the beta.** `QRME_SIGNUP_KEY` gains a keyhole: set, it
  gates signup with an invite key; empty or unset, signup is open — and open
  is now the shipped default in `docker/beta-compose.yml`, which is the
  beta's posture. Free tiers stand while testing lasts, and the terms say so.
- **Terms 1.2.** Version 1.1 said the beta is a beta and free means free for
  now; 1.2 adds the accessibility commitment in the same
  no-claims-without-behavior voice — barriers "can be reported from the
  Accessibility screen — no account, no diagnosis", naming the real door
  rather than an aspiration.

## [0.61.0] - 2026-08-10

### Fixed

- **The console was blanked by its own Content-Security-Policy.** The nonce
  policy written for the server-rendered pages was stamped on every HTML
  response — including the console's `index.html`, whose script and stylesheet
  are external files no per-response nonce can reach. A browser refused the
  bundle and rendered a dark, empty page: HTML 200, nothing running. That is
  what the first real deployment served on all three domains, while every
  in-process test passed, because a `TestClient` reads the policy and enforces
  none of it. `pagehead.console_policy` now names `'self'` where the page
  policy names a nonce — still refusing inline script — and the over-HTTP
  suite builds its own console dist so the measurement runs on CI whether or
  not `app/` was built.
- **The release-bodies sweep could not start, and then measured the fetch.**
  An edit had left its embedded Python unparseable, so every scheduled run
  died before deciding anything — in a place no interpreter, linter or test
  reads. Repaired, its first honest run accused the kept `app-v0.24.0` of
  losing a frozen body it visibly still carries: paginated output was re-split
  by a regex that matched a `]` `[` pair inside a release body's own markdown,
  and dropped what it broke. `gh api --slurp` now returns pagination as one
  JSON document, a guard proves the fetch returned every release the record
  names, and two local tests hold the line: the workflows' scripts must parse,
  and the staleness decision is driven with this product's own frozen opening.

### Added

- **The beta topology.** `docker/beta-compose.yml`, `docker/beta.Caddyfile`
  and `docs/beta-deploy.md`: the three products and the shared gateway behind
  one reverse proxy on one host, real secrets from a single `.env` that fails
  closed on any missing value, certificates obtained and renewed unattended.
  First stood up on a real host this release, which is how the console
  blanking above was found.
- **The front door.** The bare domain answered `{"detail": "Not Found"}`,
  because the console lives under `/app` and nothing said so. `/` now
  redirects to `/app/` whenever a console is mounted — headless deployments
  keep their honest 404.
- **Nightly backups, running rather than written down.** A `backup` service
  takes a `sqlite3 .backup` of each database and a copy of the collector
  ledger into `/root/backups` daily, keeping fourteen days. The copies do not
  leave the host, and the deploy doc says so.
- **Bootstrap is idempotent by validation.** A saved PDI tenant token the
  vault still honours is kept; minting happens only when there is none or it
  is refused — so a restart reuses the first tenant instead of abandoning its
  sealed records.

## [0.60.9] - 2026-08-10

### No change to this product

The release-body work reaches its end. Every release that inherited the frozen
v0.24.0 body has been rebuilt from its own CHANGELOG entry, and
`stale_release_bodies.txt` reaches a ceiling of 0 with `app-v0.24.0` kept
deliberately — its body *is* the v0.24.0 notes and is correct for it.

    asked     how many rows are left
    mattered  how many releases are still wrong

Three checks reported success while doing nothing and are fixed: a staleness
test keyed to a sentinel that was one product's number, a backfill that trusted
the record instead of the releases, and a record guard whose header pattern
required a plural and crashed when the count reached one.

`generate_release_notes` is settled too: 0.60.8 published with a curated body
and the body came back intact.

Recorded here to keep the three changelogs in step at one version.

## [0.60.8] - 2026-08-10

### No change to this product

Two findings carried from PDI's round, both of which apply here.

`release_fields.txt` -- byte-identical in all three products -- replaces the
prose list a bump was driven from. It names every version field individually,
including the three a search for the outgoing version string cannot find, and
three guards read it rather than trusting that anybody did.

`RELEASE_NOTES.md` and `sync-release-notes.yml` are deleted. 412 of 530
published releases across the three products carried the same v0.24.0 prose,
because that file was published verbatim over every curated release body since.
`release-integrity.yml` replaces them, and reads rather than writes.

PDI's console also reached a floor of zero. Recorded here to keep the three
changelogs in step at one version.

## [0.60.7] — 2026-08-09

### No change to this product

PDI's console round: the finding that a screen importing the translator is not
a translated screen. Two of its screens had been counted as localized since
0.48.3 while still holding fifteen English strings between them, six of which
were strings its table already carried in all ten languages. A guard now holds
the claim that a screen asking the table for a word may not also hard-code
one, and five further screens were localized. 91 → 32.

Recorded here only to keep the three changelogs in step at one version.

## [0.60.6] — 2026-08-09

### No change to this product

PDI's console round: Positions and Bridges localized, and its English count
corrected a third time — the reader asked for a letter, a space and a letter,
which no heading joined by `&amp;` or a hyphen has. 154 → 168 → 91. Recorded
here only to keep the three changelogs in step at one version.

The portable part is the shape rather than the code. This product's console
reader records every extracted string verbatim in both directions, so it has no
phrase test to be wrong about; the defect could not occur here. That is worth
stating rather than assuming, which is why it was checked before the round was
called PDI-only.

## [0.60.5] — 2026-08-09

### No change to this product

PDI's console round: Carriers and Exchange localized, 225 → 154, on the
honest count 0.60.4 established. Recorded here only to keep the three
changelogs in step at one version.

One thing in it belongs to all three. Two guards in that product still greped
their screens for English sentences, and localizing the screens turned them
red — the 0.48.2 lesson, *localizing a screen blinds the guards that grep it*,
arriving in the last two guards that had not had it. Both now follow the
sentence to wherever it lives rather than asserting the English is in the
file. Worth a look here the next time a screen in this product moves its words
into a table.

## [0.60.4] — 2026-08-09

### The reader this product already had turned out to be the one that was right

No change to this product. The round was PDI's, and it is recorded here
because the finding is about a method all three share.

PDI read its console's English with three regexes, the first being
`>\s*([A-Z][^<>{}\n]{2,})\s*<`. This product moved off that shape rounds ago
to `app/scripts/jsx-text.mjs`, which parses with TypeScript's own parser and
returns every `JsxText` node. Nobody had run the two side by side until now.

    asked     how much English does this pattern match
    mattered  how much English does a person read

**233 against 177**: a quarter of PDI's console prose was invisible to it —
every wrapped sentence, every sentence with a value interpolated into the
middle, every phrase not starting with a capital. Hidden in the direction that
makes a ratchet look satisfied, and two of that product's localization rounds
were graded against the low number.

The lesson is not about regexes. It is that two products can carry the same
guard by name and not by reach, and the only thing that finds it is running
both readers over the same file and comparing. `shared_guards.txt` says the
three suites ask the same questions; it cannot say they answer them as well.

## [0.60.3] — 2026-08-09

### A check that cannot fail before the merge is not a check

0.60.2 found `native.yml` red for a hundred and twenty-three consecutive runs.
Nothing was wrong with what it ran. What was wrong was *when*: it fired on
`pull_request`, which never opens here because releases are fast-forward
merges, and on `push` to `main`, which happens after somebody has decided to
ship.

`ci.yml` carried the identical trigger. It had been red for twenty-nine
consecutive runs.

    asked     does the workflow pass
    mattered  can the workflow's answer still change the decision

- **The four red guards.** They shell out to `app/scripts/jsx-text.mjs`, a
  TypeScript-AST reader used because three separate regexes over the same
  source each hid real strings. It imports `typescript` from the app's own
  `node_modules`, which the job running pytest never installed. Those guards
  are written to fail loudly rather than report a comfortable zero, and that
  is exactly what they did — into a log nothing read. The job installs the
  app's dependencies now.
- **The trigger** is any branch push, the same fix `native.yml` got.
- **`test_a_check_that_cannot_fail_before_the_merge.py`** reads the checked-in
  triggers and fails when a gating workflow cannot fire before a merge. Three
  workflows are deliberately post-merge — the container e2e run and the two
  that fire on a release tag — and each is named in `POST_MERGE` with its
  reason. Naming one is a decision; the failure this exists for was nobody
  having made the decision at all. A named exception for a deleted workflow
  fails too: the exemption must not outlive its reason.

  It cannot tell whether a workflow is passing. It can tell whether a failure
  would arrive in time to matter, which is the part that was missing.

## [0.60.2] — 2026-08-09

### The compiler was in the room the whole time and nothing listened

`native.yml` builds the Swift, Kotlin and C# shells on three runners. It had
been failing for 123 consecutive runs and no part of the loop read it: the
workflow fired on `pull_request`, which never opens here because releases are
fast-forward merges, and on `push` to `main`, which happens *after* the
decision to ship. The trigger is any branch push now, and the result is the
first green board this repo has ever had.

    asked     do the shells read the members they name
    mattered  do the shells compile

Everything below was found by a compiler, not by reading.

- **The Android shell could not be built at all.** `L10n.kt` is one `mapOf`
  of 1,125 rows, which compiles into the object's static initializer, and the
  JVM caps a single method at 64 KB. Past that there is no diagnostic to act
  on — codegen fails with `Method too large` and no class is emitted. The
  table is twelve functions now, joined by `table`
- **Half of `ApiClient` was not in `ApiClient`.** 944 lines — friends, the
  wall, the audience verbs, watch parties, skill grants, exchanges — sat
  inside `record PackInstalled`'s body, where they could not see `Send`,
  `Get` or `Post`, and where `PeoplePage` could not see them. A record body
  is legal C#, so the file parsed; thirty methods the pages call did not
  exist
- **A defaulted parameter in the middle of a record's list** silently
  swallows the last argument of every positional call. `WatermarkRecovery`
  lost `method`; `ObjectionOpened` lost `note`
- `AppState.kt` carried `private set` twice, a syntax error that hid every
  member declared after it
- `deskCardOf` built a seven-field shape out of a seventeen-field record and
  had no caller left; `BeaconCameraSurface` read a `lang` it never took;
  `Problems.send()` required an `appVersion` its caller does not pass
- Names that were never there: `RevokeOut.Revoked` (it is `RevokedCount`),
  `MicVocabularyOut.widths`, `WearableBoard.kinds`, `TutorialProgress.Next`,
  `RosterSibling.Id`, a fifth `Api.shared` where the client is `ApiClient`
- `AttestButton` and `BlockedNote` are `x:Name`d inside a `DataTemplate`,
  which mints no code-behind field, so the localizer was setting text on
  nothing. Both labels ride on the row now
- Two `using` lists and one import list that did not ask for what the file
  reaches for; two iOS calls that passed `query:` before `token:`; one
  timeline row of five chained string operands the type checker gave up on

Both C# record readers in `tests/` now end a record where C# does — at `);`,
or at `)` before a body — after the move above took away the accident that
had been hiding a bug in them.

## [0.60.1] — 2026-08-09

### A fix to the cascade fixes the next delete, not the last one

0.59.9 derived the profile delete from the schema. Every profile ended
*before* that release was ended by a list of twenty-four table names against a
schema of sixty-six, and the forty-two tables it missed are still sitting in
every deployment that has been running since.

Nothing in the product will ever look at them again, and that is the whole
problem. The `profiles` row is gone, so the API answers 404, so no code path
visits those rows — not visible, not reachable, still there.

    asked     does the delete work now
    mattered  what did it leave the last time it did not

### Added

- `python -m qrme.orphans` — a one-off maintenance sweep for the residue.
  `survey()` reads and the command is **dry by default**; `--apply` is the
  only thing that deletes, and `--json` gives the same survey machine-readable.
- Its scope is the cascade's own reader (`common.profile_scoped_tables()`
  minus `common.ERASE_KEEPS`) rather than a second list — this is that cascade
  applied retroactively, and two readers of *which tables hold a profile's
  data* is two things to keep in step.
- A row counts as an orphan only when its `profile_id` names a profile not in
  `profiles`. Rows with a NULL or empty subject are left alone: they are not
  the residue of a deleted profile, and a command written for one problem does
  not get to decide about a different one.
- `test_what_the_old_cascade_left_behind.py`. The sharp property is not *does
  it find the orphans* but **does it leave a living profile alone**, checked
  with a live profile seeded beside the stranded one. Both directions were
  confirmed by injection: a broken liveness filter reports 56 tables of a
  living account's data, and a hand-written scope reports 52 tables the survey
  cannot see.

### Fixed

- `test_the_member_that_isnt_there.py` read `AppState.Current.X` only when a
  page spelled it out in full. A page that puts the singleton in a local first
  — `var st = AppState.Current;` then `st.Uid` — was read as reaching for
  nothing at all, and a row's floor stayed comfortably met on the call sites
  it *could* see. Aliases are now expanded, and **only** when the name is
  bound to that singleton and nothing else anywhere in the file: the first cut
  rewrote whole files and reported twenty-eight perfectly real members as
  missing, which is the failure mode this guard's own docstring is about.

## [0.60.0] — 2026-08-09

### An export is measured against the schema too — and drops the credentials

0.59.9 derived the **erase** from the schema in all three products, because the
lists that stood in for it had gone stale: an operation advertised as *every
trace* reached a third of the tables. The export is the same question turned
round.

    asked     can a person delete everything we hold
    mattered  can a person see everything we hold

### What it was

`GET /profiles/{id}/export` says *full data export — access everything,
anytime (You Own It)*. The README's capability table points at it under **You
own it / total control**. The suite gateway's GDPR Article 20 bundle is built
on it — the tandem's whole answer to *give me my data*.

It returned **six tables of sixty-six**: the profile, its sources,
relationships, messages, engagement, posts and surfaces. The clinical notes and
the media behind them, the watermarks tying a rendered likeness back to a
person, the homepage, the friendships, the inbox — none of it was in the file
somebody downloaded to see what we have.

### Two properties, and the second is not the first

An export must be **complete** and must **not hand back a live credential**.
Those pull in opposite directions, and the honest resolution is per column
rather than per table: a row is the person's own history, and a token inside it
is a credential in whatever they do with the file — a bundle gets downloaded,
mailed to a clinician, dropped in a cloud folder.

The redaction is a **rule** rather than a list, and that is not tidiness. The
first cut was a list of exact column names, and the new guard caught it on its
first run — three credential columns in tables the export now reaches, none of
them in the list. A list of columns goes stale exactly the way the cascade's
list of tables did.

Deliberately *not* the bare word `hash`: a hash-linked audit record is what a
person verifies their own export with, and a credential is what somebody can
present. The two are not the same and the rule says so.

### The symmetry, asserted

A table the erase clears and the export omits is a person who can delete
something they were never shown. A table the export carries and the erase
misses is 0.59.9's defect. The guard compares the two sets directly.

There is one deliberate asymmetry, and only in the vault: its audit chain
survives a wipe because it is the proof the wipe happened, and a bequest is
*retired* rather than deleted so an heir's credential fails with **revoked**
instead of silence. Both are still the tenant's to read, so the export carries
what the erase keeps — the one place these two answers differ on purpose.

## [0.59.9] — 2026-08-08

### An erase is measured against the schema, not against a list somebody wrote

`DELETE /profiles/{id}` says *delete the profile and every trace of it —
anytime*. It named twenty-four tables in a tuple. This schema has **sixty-six**
with a `profile_id` column, so the delete left forty-two standing:

    anonymous_pictures   clinical_notes   media          media_watermarks
    homepages            friendships      inbox_events   displays
    embodiments          excursions       campaigns      game_sessions
    departments          delegated_workflows             environment_context
    …and twenty-eight more

`clinical_notes` and `media` are the sharp ones: a clinical note and the
photographs behind it, belonging to a profile the API answers 404 for.
`media_watermarks` is the identifier tying a rendered likeness back to the
person it was made from.

The sibling vault had already fixed this shape and the fix had not travelled.
Its docstring already said the general thing: *a migration that adds a table
is covered by writing it, not by remembering this function.*

    asked     did we delete what the handler names
    mattered  did we delete what the schema holds

### Why the list kept losing

It was not neglect. Both siblings' lists had been *corrected*, more than once,
and every correction was right. JIM-mini's most recent one found a watch
channel outliving its account and added three tables — `watch_channels`,
`contribution_log`, `waivers` — because those three carried a live credential
rather than a record. That fix was correct and did nothing about the next
table, and `crash_watches` and `vigils` are the same kind of row and were
still standing after it.

A list is a claim about a schema, made once, by somebody who could see the
schema that day.

### How it is checked

By writing a row into **every** scoped table, erasing, and looking. Not by
exercising features until rows appear: the tables a test can reach through the
API are the tables somebody thought to wire, which is the same blind spot as
the list. The rows are synthetic and go in through SQL — the question is
whether the cascade reaches a table, and a row is a row.

Plus the structural half, which is the part that survives the next migration:
the handler must not carry a list of table names at all, and must ask the
schema.

### The test does not borrow the reader it is checking

The first cut planted rows in the cascade's own table reader. Narrowing the
cascade narrowed the planting with it, so injecting the old hand-written list
reported *a blind reader* rather than *forty-odd surviving tables*. It reads
the schema itself now, and the injection names every table by name.

## [0.59.8] — 2026-08-08

### The check that covered one client of four

0.59.7 asked whether the shape a screen declares is the shape its route
answers with, found two screens throwing `.map is not a function` during
render, and asked the question of **the console alone**. The three native
shells decode the same answers into their own types, and a wrong one there is
the same failure with a different stack trace: `JSONArray` on an object throws
exactly like `.map` on one.

*No disagreement* from a check that was never run reads exactly like *no
disagreement* from a check that passed. That sentence is most of this arc.

### What each client says, and where

    console   req<T>(…)                     the generic
    ios       let x: T = try await request  the annotated decode
    windows   Send<T>(…)                    the generic
    android   JSONObject(body) / JSONArray  the parse itself

Android is the one worth reading twice: Kotlin has no decode type at these
call sites, so the *parse* is the claim being checked.

### What it found

No disagreements — the three shells were already right. What it found instead
was how unevenly the clients can be read at all:

    console 422   iOS 300   Android 316   Windows 342

JIM-mini's Android shell names a shape on **three calls out of a hundred and
fourteen**, because it discards the body on the rest. That is not a reader
failing; a client that never reads an answer cannot be wrong about one. But
three and three hundred cannot share a floor, so the per-client reach is a
**record that must not go down** rather than a number chosen by hand — the
same instrument the estate uses everywhere a count is honest but lopsided.

### Two readers this round got wrong first

Both are kept as prose beside the code that fixes them, because both reported
*clean*:

* a Swift `[K: V]` dictionary counted as a list, because both spellings start
  with a bracket — three false disagreements;
* the Windows shell spells its verb `Post(…)`, not `HttpMethod.Post`, so
  twenty-one calls defaulted to GET and every one was reported wrong.

Injections confirmed red before the round closed: a `GameSession[]` narrowed
to `GameSession` is named by client, file, route and declared type; and a
single character removed from the Android reader drops its reach from 316 to
310 and fails on the record rather than passing quietly.

## [0.59.7] — 2026-08-08

### `req<T>` is a cast, and a cast is a claim about the server nothing checks

0.59.6 read the requirement out of the application — which headers a route
needs — and asked whether the callers could meet it. This is the same question
pointed the other way: the route **answers** with a shape, the screen
**declares** one, and between them sits `req<T>`, which is a TypeScript cast
over a body parsed by `JSON.parse`. The compiler is satisfied. The screen
crashes.

    asked     does this call compile
    mattered  is the shape it names the shape that arrives

### What it was, next door

PDI's `GET /hosting/{tenant_id}/history` answers an object, and its Custody
screen called `.map` on it — `TypeError: history.map is not a function`,
thrown during render, on any vault that had ever been moved. JIM-mini had the
same on `GET /users/{uid}/referral/clinicians`.

This console agrees with its backend on all **422** typed calls, and the one
place it hedges names both shapes on purpose.

### Why nothing else covers it

The route audit asks whether a path resolves and a method is accepted. The
door audit asks whether a route has a screen. Both were fully satisfied: the
path resolved, the method matched, the screen existed and called it. Nothing
asked what came back. `tsc` cannot help either, and that is structural rather
than an oversight — `req<T>` is generic over a type the caller supplies, and
the parsed body is `any`.

### The reader, and its own blind spot

Per **call expression**, not per path. The first cut keyed on the path literal
and reported sixty-odd disagreements, every one of them the reader pairing a
`POST` with the `GET` that shares its path; reading each `req<T>(…)` call and
taking the verb from that call's own body dropped it to one per product, and
all of those were real.

Before that, an earlier cut read **zero** call sites — its pattern stopped one
character short of the opening backtick — and reported that the consoles
agreed with their backends everywhere. It was right about every call it looked
at, because it looked at none. That is why this file carries a registered
floor (`console.calls_typed`) rather than trusting its own silence, and why
the verb reader is asserted per verb.

A union naming both shapes satisfies either: a client that copes with what
arrives is defensive rather than wrong.

## [0.59.6] — 2026-08-08

### The clients agreed with each other, and they were all wrong

0.58.0 asked whether the three shells sent every header the console sent, found
`x-llm-api-key` in one client and no other, and fixed it. It has held since.
This round found what it cannot see.

**Parity is a relative check, and a relative check is satisfied by everybody
being equally wrong.**

The instance is PDI's and the shape is the estate's: a vault under customer
custody required `x-tenant-key` on every record route, and no client in that
product sent it outside two heir routes. The comparison passed the whole time,
because both sides of it were wrong in the same direction — which is exactly
the case a comparison cannot report.

This product has no such header today. The guard is here anyway, because the
question is not about that header, and a guard that arrives after the second
instance is a guard that was written twice.

    asked     do the clients send the same headers as each other
    mattered  do the clients send the headers the routes require

### The guard, in all three suites

`test_a_header_a_route_needs_is_a_header_its_callers_send.py` reads the
requirement out of the **application** rather than out of any client. FastAPI
already resolves each route's header parameters through its whole dependency
tree, so a header required by an auth dependency is attributed to every route
that depends on it — the case a reader of function signatures misses entirely.
Then, per client, per route that client actually calls: can it present what
that route requires?

A header set in a client's shared dispatcher rides every request. A header set
beside one call rides that call. The first cut of this guard counted the two as
one, and that alone let the console pass on a header it sends to two routes out
of the eighty that need it.

The half no dependency walk can reach — a header taken straight off the request
inside a handler — is asked as a product-wide question, because the attribution
is genuinely unavailable. `x-signup-key` is recorded there with its reason: an
operator who sets it is closing registration to everybody, and a client able to
present it would reopen the door the operator shut.

### Liveness without a number

The three products lean on the two readers in opposite proportions — 103 routes
declare a header in one and a single route does in another — so a floor per
product would be three numbers to keep honest. The question is asked the other
way instead: every non-transport header a client sends must be one some reader
here found. A client sending a header no reader knows about is either talking
to itself or looking at a reader that has gone blind.

## [0.59.5] — 2026-08-08

### A value inside a script is not markup, and neither escaper knows both

0.59.3 shipped a Content-Security-Policy with a nonce and called it the second
line of defence. 0.59.4 made the first line — escaping into HTML — a guard.
This is the third sink, and it is the one where **both of those miss.**

Inside a `<script>` element the HTML parser ends the element at the first
`</script`, whatever the JavaScript quoting says. A value carrying `</script>`
closes the script early and everything after it is parsed as markup — in the
page's own nonced script, which the policy exists to permit.

    json.dumps    escapes what would end a JavaScript *string*  — not the element
    html.escape   escapes what would open an HTML *tag*         — not a JS string

    asked     is the value a valid JavaScript string
    mattered  can the value end the script element

This product's `_js` composed both correctly. JIM-mini's and PDI's were bare
`json.dumps`. A helper written once and copied into three
repositories, where the copy that drifted is the one whose entire job is to be
safe — the shape 0.59.0 found in a floor and 0.59.1 in a guard, now in a
security primitive.

**Not currently reachable.** Every value passing through these helpers is a
database identifier or a translated constant, and a path segment cannot carry
`</script>` because the slash breaks routing before the page is built. A
latent hole, fixed anyway: the next value somebody escapes with it is exactly
the one it was written for.

### One primitive, and a whitelist checked rather than trusted

`_js_literal` is now the single place that knows what ends a script element,
and `_js` and the string table are both built on it. Two helpers escaping for
the same sink is two chances to drift, and they had already taken one each.

The guard's own first draft is worth recording. Its call-site check allows a
value through if it arrives via `_js(` or `_strings(` — and when that was
written, one product's `_strings` was a bare `json.dumps`. **The guard would
have excused, by name, precisely the defect it exists to catch.** A whitelist
is a claim about behaviour; it is checked as one now.

### The consoles, swept and clean

The same question in TypeScript is `dangerouslySetInnerHTML`, `innerHTML =`,
`document.write`, `eval` and `new Function`. All three consoles have none of
them. The community wall's linkifier was read too: it splits on `https?://`
and gates on `startsWith("http")`, so a `javascript:` scheme cannot reach an
`href`.

That is a floor rather than a backlog — nothing to pay down, and the cheapest
time to keep it that way is while it is still true.

### Also

- Versions moved to 0.59.5 across the console, the backend, and the iOS,
  Android and Windows projects (build 59005).
- `shared_guards.txt` regenerated at 405 names; the divergence record holds at
  136.

## [0.59.4] — 2026-08-08

### The sweep that found the last one, kept

0.59.3 found reflected cross-site scripting on the sign-in callback by walking
every f-string that builds markup — **by hand, once, and then throwing the
walk away.** That round shipped the second line of defence, a
Content-Security-Policy with a nonce, and left the first one unguarded.

Escaping is the first line. So the walk is a guard now.

    asked     is this page correct
    mattered  can the next value somebody interpolates be markup

### Following the escape rather than looking for it

Most of this estate escapes one line above the template:

    ref = html.escape(card["reference"])
    body = f'<p class="ref">{ref}</p>'

A sweep that only asks whether `html.escape` appears between the braces
reports **32 rows** here, of which the six real ones are buried. Following
single assignments, and functions whose every return is escaped, and
conditionals and joins whose every branch is safe, cuts it to **8** — and all
eight are composites the analysis cannot follow rather than values a reader
supplies. A record that is four-fifths noise is a record nobody reads.

It also refuses to read prose as markup. The first draft matched any f-string
containing `<` and `>`, which flagged a WebAuthn diagnostic containing
`http://localhost:<port>`. It now wants a closing tag, or an opening tag
carrying an attribute.

### What it catches

Put 0.59.3's defect back and the guard names it — file, line and expression:

    9 unescaped interpolations into markup, above the 8 recorded:
        routers/accounts.py:247: {error or 'no code came back'}

Four hundred releases of invisibility, and it was never hard to see. Nothing
was looking.

### Three attribute interpolations escaped on the way past

`<html lang="{language}">` depended on the caller having negotiated one of ten
known codes; `<option value="{value}">` on a hard-coded tuple; the policy
nonce on `secrets.token_urlsafe`. All three were safe and all three now escape
where they are written, which costs nothing and removes a permanent row from
the record.

### Also

- Versions moved to 0.59.4 across the console, the backend, and the iOS,
  Android and Windows projects (build 59004).
- `shared_guards.txt` regenerated at 397 names; the divergence record holds at
  136.

## [0.59.3] — 2026-08-08

### What a page promises a browser before it says anything else

0.59.2 built a harness that talks to a real server, because the rules a
browser enforces are invisible to an in-process client. This round pointed it
at the surface where that matters most: the HTML these products serve to
someone **without an account, on a device that is not theirs** — the sticker a
stranger kneels over, the sealed-carrier card, the page a sign-in provider
sends a browser back to.

Measured over HTTP, every one of those pages in all three products went out
with **no `Content-Security-Policy`, no `X-Content-Type-Options`, no
`X-Frame-Options` and no `Referrer-Policy`.**

That was the standing invitation. Then a sweep of every f-string that builds
markup found what had walked through it.

### Reflected cross-site scripting on the sign-in callback

`GET /auth/oauth/{provider}/callback?error=…` interpolated the query parameter
straight into its HTML. Driven over HTTP:

    ?error=<script>alert(document.domain)</script>
    →  400, and the payload comes back verbatim inside <p>…</p>

Anyone who could get a person to follow a link ran script on this product's
own origin — in a browser holding a session, or inside the packaged console's
window. Two more values on the same route went in unescaped: the provider's
error message and the address it returns.

Escaped at the interpolation, which is the fix. The policy below is the second
line, not the first.

### A policy with a nonce, because one without is decoration

`script-src 'unsafe-inline'` permits exactly what an injected `<script>` needs
and would have stopped nothing above. So `pagehead.py` mints a nonce per
response, the pages that carry an inline script stamp it through
`script_open()`, and the policy names that nonce and nothing else:

    default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline';
    script-src 'nonce-…'; connect-src 'self'; form-action 'self';
    base-uri 'none'; frame-ancestors 'none'

`style-src` keeps `'unsafe-inline'`: the stylesheets are constants in the
package and no page interpolates into them.

Verified in real Chromium against a real server — the beacon page renders
with **no CSP violations**, styles applied, its own script running.

### What the guard checks

`test_what_the_browser_enforces.py` grew from four questions to a dozen: the
headers on every stranger-facing page, that the policy names a nonce rather
than permitting everything, that the page and its policy **agree** about that
nonce, that the reflected parameter comes back escaped, and that JSON is left
alone.

The nonce-agreement check is the one worth keeping. If the header and the tag
ever drift apart, the policy is still perfect and the page's own script
silently stops running — and that check's first draft failed against correct
code, because it read the header from one request and the body from another.
Two requests, two nonces. It reads both from one response now.

### Also

- Versions moved to 0.59.3 across the console, the backend, and the iOS,
  Android and Windows projects (build 59003).

## [0.59.2] — 2026-08-08

### A crash the browser threw away

0.59.1 found a CORS defect in a sibling product by comparing three
repositories rather than by testing behaviour — because **no test in this
estate could have found it.** Every one of them calls the app through a
`TestClient`, which never sends an `Origin`, never runs a preflight, and never
drops a response for want of a header. The whole class is invisible.

    asked     does the server answer
    mattered  does the answer reach the reader

Asking the question properly found a second one, in all three products at
once.

An unhandled exception is rendered by Starlette's `ServerErrorMiddleware`,
which sits **outside** every middleware the factory adds — including CORS. So
a 500 went back to a browser with no `access-control-allow-origin`, and the
browser discarded the entire response. Measured over HTTP:

    GET /health   200   access-control-allow-origin: *
    a 500         500   access-control-allow-origin: None

The consequence is worse than a missing header. These consoles distinguish
*the backend is unreachable* from *the backend refused* — the version-mismatch
guard and the content-free problem reporter both depend on it — and a 500 the
browser throws away is indistinguishable from the first. **Every crash in
every one of the three products reached its user as "Failed to fetch."**

### Why the obvious fix is not the fix

Registering `@app.exception_handler(Exception)` does not help: Starlette hands
that handler to `ServerErrorMiddleware`, which is still outside the CORS
layer. It has to be a middleware, and it has to sit *inside* CORS.

So each factory now ends with a catch-all middleware followed by the CORS
block, in that order — `add_middleware` inserts at the front, so the last one
registered is the outermost. The body it returns says nothing about what
broke: the traceback is logged on the machine and what leaves is a status and
a sentence, the same posture every other refusal here takes.

That ordering is now checked rather than assumed, and it needed to be: the
three products disagreed about it. Two added CORS before their request-scoped
middleware and one after, and nothing was comparing them.

### A test that starts a server

`test_what_the_browser_enforces.py` boots the app under uvicorn on an
ephemeral port and talks to it with a plain HTTP client, sending the header a
browser sends. It checks that a 500, a refusal and a preflight all come back
readable, and that CORS is still the outermost layer.

Its last test is the point of the exercise: it makes the same failing request
through a `TestClient` and shows it passing, with the header absent. Three
thousand tests can pass on an API no console can read.

### Also

- Versions moved to 0.59.2 across the console, the backend, and the iOS,
  Android and Windows projects (build 59002).
- `shared_guards.txt` regenerated at 383 names; the divergence record holds at
  136.

## [0.59.1] — 2026-08-08

### Three suites, and nothing comparing what they ask

0.59.0 closed on the observation that a literal copied into three
repositories is calibrated for whichever of them was smallest. That is a
special case of something larger: **every guard in this estate exists in three
copies, and the copies drift silently in both directions.** A fix made in one
product and not ported looks exactly like a product that never needed it.

Nothing anywhere was comparing them.

    asked     does this product pass its own suite
    mattered  do the three suites ask the same questions

A sweep of every `def test_*` across the three suites found **370 names
carried by all three and 140 carried by exactly two** — 91 absent from PDI, 29
from QRME, 16 from JIM-mini.

### Four of those rows were one defect

`test_serve_cors.py` existed in QRME and JIM-mini and not in PDI, and so did
the code it guards. Both siblings' `serve` opens CORS for a loopback bind,
because the packaged console calls the API from its own origin and dies as
"Failed to fetch" otherwise. PDI's frozen backend in
`packaging/backend_entry.py` does the same, so the **installed** app worked.
`python -m pdi serve` — the documented from-source path — set nothing.

Measured over HTTP with the console's origin on the request, because CORS is a
browser rule and an in-process test client never sends an `Origin` at all:

    OPTIONS /terms   →  405, no access-control headers at all
    GET     /terms   →  200, no access-control-allow-origin

and after the fix:

    OPTIONS /terms   →  200, access-control-allow-origin: *

Every in-process test in that product passed throughout. Loopback binds only —
a non-loopback bind is somebody serving a vault to a network, and that is the
last place to open CORS by default; `--no-cors` restores the closed posture,
and an explicit `PDI_CORS_ORIGINS` is never overwritten.

### The mechanism, and why it is a written record

The three repositories are rarely checked out together, so a live comparison
skips in CI — and this estate has already been bitten by that: the sibling
vocabulary check in `test_the_refusal_names_the_field_on_the_form.py` carries
a comment saying its first draft looked in the wrong place and skipped every
run. *A check that never runs is not a check.*

So the shared vocabulary is written down, byte-identical in all three
repositories:

- `tests/shared_guards.txt` — 377 names carried by all three.
- `tests/guard_divergences.txt` — 136 names carried by exactly two, each row
  naming the product that lacks it. Ratcheted: it may shrink, never grow.

Each product then verifies its own half with nothing but itself. Every name in
the manifest must exist here. Every divergence naming *another* product must
exist here. Every divergence naming *this* product must still be absent, so a
port that lands without being recorded fails rather than passing quietly.
Three checks, no sibling checkout required — and the live three-way comparison
runs on top whenever the siblings are on disk.

### A name is not a behaviour

This compares function names. A guard ported under a different name reads as
missing; one that kept its name while its body was gutted reads as present.
PDI reports its version from `/health` under a differently-named test, and the
record holds that as a row rather than pretending otherwise.

The limit is worth the check, because the failure it catches is the one that
actually happens: not a renamed guard, but a fix that never travelled.

### Also

- Versions moved to 0.59.1 across the console, the backend, and the iOS,
  Android and Windows projects (build 59001).

## [0.59.0] — 2026-08-08

### A floor nobody raised is a floor nobody is standing on

0.58.8 found the route reader had one floor and four clients. 0.58.9 found the
localizer's floor was ten against nine hundred and forty-five. Twice in a row,
the same defect in a different instrument: a number written when the surface
was small, correct on the day, never raised.

Fixing them one file at a time does not generalise. This round swept every
floor in the suite instead.

### The two questions

A floor answers one question on every run — *is the number satisfied* — and
that is exactly the question that keeps passing after the number stops meaning
anything.

    asked     is the number satisfied
    mattered  is the number still near what it measures

The standard is the one 0.58.8 set for its own table and 0.58.9 kept: a floor
under **half** of what it measures is not holding anything. Applied to
everything reachable in this product, every one of them failed it:

    l10n asked, per shell        10 against 945-961     ratio 0.01
    l10n held, per shell         20 against 1087-1115   ratio 0.02
    path literals, all surfaces  40 against 1407        ratio 0.03
    console call sites          200 against 429         ratio 0.47

The last one is worth reading twice, because 0.58.8 wrote that *the console is
protected* and built a round on top of that sentence. It was protected against
being blinded outright — 351 down to 74 does trip a floor of 200. It was never
protected against being halved, and half of a route reader is half an audit.
The sentence was true about the failure it was tested against and false about
the one nobody tested.

**91 floors in this product** carried their own literal, across 56 files.

### The finding underneath the finding

The rows that **passed** are as informative as the ones that did not. The same
literals appear in all three products, copied across when a guard was ported.
`assert len(made) > 200` is four-fifths of JIM-mini's console and 0.47 of
QRME's. `assert len(made) > 20` is a real floor against PDI's thirty-five
native call sites and a twentieth of QRME's four hundred and thirty.

**One number written to work in three repositories is calibrated for whichever
of them was smallest when it was written.** It reads as fine in the small
products forever, and ages into decoration in the large one, and nothing in
any of the three could tell the difference — because none of them had the
measurement attached.

`test_the_console_is_a_client_too.py` even carried the reason in its own
docstring: the floor was set low deliberately *because the three products'
shells differ by a factor of three in size*. That is a true sentence about why
the number is small and a false one about what it holds.

### The convention, because the sweep needed one first

A floor is spelled a dozen ways — `assert len(found) > 20`, `assert total >=
40`, a `FLOORS` tuple, a bare `_MIN_PATHS`. Nothing could walk them all,
because the number is not the hard part: the **measurement** is. A literal
inside an assertion has none attached, which is precisely why it can drift to
a fiftieth of the truth with every run passing.

`tests/ratchets.py` is a floor plus the way to read the same quantity now:

    Ratchet("route.calls.console", 340, _calls("console"),
            "call sites the route audit reads out of the console")

Registering one has three effects. The number lives in one place instead of
inside an assertion. `test_a_floor_is_within_sight_of_what_it_measures.py`
checks it against reality on every run, in both directions. And because the
assertion now reads `ratchets.floor("name")` — a call, not a constant — the
AST sweep stops seeing it, so registering removes a row from the backlog with
nobody editing a list.

### What is left is counted, not guessed at

The remaining bare floors are held in `unregistered_floors.txt` with a
ceiling, the way every backlog in this estate is. Not all of them are wrong;
some are small fixed cardinalities that will never drift. Telling those apart
from the decoration requires knowing what each one measures, which is the work
of registering it. A **new** bare floor now fails at the moment it is written
rather than three releases later.

### Also

- Versions moved to 0.59.0 across the console, the backend, and the iOS,
  Android and Windows projects (build 59000).

## [0.58.9] — 2026-08-08

### Ten against nine hundred and forty-five

0.58.8 audited the route reader and found the three native shells had no floor
at all, closing by naming the next reader with the same shape available and
unused: the one that reads the L10n tables. It has the same hole, and worse
numbers.

`test_a_shell_asks_for_a_key_it_has.py` asserts each shell extracts **at least
ten** localizer calls and holds **at least twenty** table rows, as a canary
against the pattern silently ceasing to match. It was written when that was a
meaningful fraction. The tables now hold 1087, 1100 and 1115 rows and the
screens make 945, 950 and 961 calls.

    ten against nine hundred and forty-five

A floor at one percent of the truth is not holding anything.

### Why the rest of the file does not cover for it

Two of the three readers in that file are protected in both directions. If the
table reader goes blind, every key a screen asks for stops being in the table
and the first check reports hundreds of missing rows. If the reachability
reader moves either way, the dead-row backlog reports undecided or stale rows.

The **call** reader going blind is silent, because reachability falls back to
a pattern that finds every dotted string literal in the sources whether or not
a localizer call sits in front of it.

Measured rather than argued. Narrowing the call pattern so it matches only
`L10n.t("…")` — no whitespace, lowercase method — is an ordinary-looking tidy
that blinds C# alone, because Windows spells it `L10n.T(`:

    ios      950 call sites
    android  961 call sites
    windows   52 call sites

**294 tests pass.** The one failure names four rows — `ncmp`, `ndsk`, `nov`,
`nstu` — as *translated rows nothing asks for*, and those four are visible
only because they are the shell's only keys without a dot in them. Nothing in
that message says the reader stopped reading.

    asked     does every key a screen wants have a row
    mattered  can the reader still see the screens asking

### Two floors, because they fail differently

**Absolute, per shell, on both halves** — the extracted call sites and the
parsed table rows — set at roughly four-fifths of what each reader reaches
today. That catches the slow case: a form dropped here, a suffix there, over
several rounds, which no single diff makes obvious.

**A spread across the three shells**, which needs no number chosen by hand.
iOS, Android and Windows are one client written three times: the same screens,
ported by hand, so their tables are near-identical in size. Measured, the
quietest shell sits at 98% of the busiest in QRME, 89% in JIM-mini and 77% in
PDI. A shell at a twentieth of its ports is not a smaller shell.

The console is deliberately not a fourth port, and the reason is measured
rather than assumed: it shares 82 rows with QRME's shells, 62 with JIM-mini's
and **none at all** with PDI's. The desktop frame and the phone screens are
separate vocabularies, so neither a spread rule nor a superset rule between
them would mean anything.

### And the comparison the backlog files never made

`native_dead_keys.txt` carries a per-shell count — 73, 97 and 103 in QRME —
that has never been compared across shells. The ratchet asks whether the
number is going up; it does not ask whether one shell is carrying far more of
it than its ports. Most of those rows are not waste: the file's own header
says they are screens that exist on three shells and say less on one. That is
exactly a per-shell comparison, and it was sitting in the file unmade. It is
one-sided on purpose — a shell below its ports has paid its debt down.

### Also

- Versions moved to 0.58.9 across the console, the backend, and the iOS,
  Android and Windows projects (build 58009).

## [0.58.8] — 2026-08-08

### The route reader had one floor and four clients

0.58.7 found a missing brace by auditing a reader rather than the thing it
read, and closed by naming the general case: **a blind instrument is
indistinguishable from a clean repository.** The route audit's reader is the
oldest and most load-bearing in the estate — six other files ask `clientpaths`
what each client calls, and a route table read short narrows all of them at
once, silently, in the safe direction. So this round went there.

### What the probe found

The console *is* protected. `test_the_audit_is_actually_looking_at_something`
asserts `calls(CONSOLE) > 200`, written when the console was the only client.
Blinding the console's template-literal reader drops it 351 → 74 call sites
and fails four tests including that one.

**The three native shells had no floor at all.** Their protection was
incidental — a scatter of per-block and per-form tests from earlier rounds
that happen to name routes those readers see. Blinding the iOS `request(`
form drops it **430 → 11** call sites; what fails is a handful of block
guards, not one of them saying *the iOS reader has stopped reading*. A
narrowing that misses the blocks those tests happen to cover passes in
silence, and `doorless` still reports zero throughout, because the other
three clients cover for the blind one.

```
asked     do the clients call every route
mattered  can the reader still see the clients
```

### Added

- `test_the_reader_can_still_see.py`, in all three products. Two floors,
  because they fail differently. **An absolute floor per client**, set at
  about four-fifths of what each reader reaches today, catches the slow case —
  a reader narrowed a form at a time until it covers a fraction of the
  surface. **A spread check across the three native shells** catches the fast
  case without a hand-chosen number: iOS, Android and Windows are one client
  ported three times, so one reader at a third of the other two is the reader
  breaking rather than the shell shrinking.
- The console sits outside the spread comparison, and the reason is measured
  rather than assumed: JIM-mini's console extracts 251 call sites against 114
  on each phone, PDI's 121 against 35. Those consoles carry surface the phones
  do not, so a rule spanning all four would have to be loosened until it
  caught nothing. The absolute floor is what holds the console.
- A floor on the route table itself. `app.routes` is not the route table — it
  showed 8 of 409 once, and the first doorless audit built on it reported a
  clean bill.

The floors are ratchets, not targets. Raising one when a client grows is
ordinary; lowering one takes a deliberate edit that shows up in a diff, and
the only honest reason is a client that genuinely got smaller.


Suites: **1547 + 1533 = 3,080** across 218 files.

## [0.58.7] — 2026-08-08

### A wire model is data, and data has no methods

0.58.6 closed by naming its own hole: a pin whose reader goes blind reads a
model as **empty**, an empty set is a subset of anything, and the pin passes
against nothing while looking exactly like a pin that is holding. That is the
only way this table can lie, so this round went after it rather than after
more surface.

### Added

- Every pin now asserts on **both ends**: the model read something, and what
  it read shares at least one key with the contract. Deliberately not a size
  floor — `MicPlacesOut` and `ChainState` are honest one-property wrappers,
  and a floor that called those defects would be the file inventing work.
- Three checks read the readers themselves against a second opinion. Every
  struct whose conformance list mentions `Decodable` must be one the pattern
  can see; every C# record read by the finder must survive paren-matching;
  every property the language declares must be one the property pattern finds,
  located by where a declaration *starts* rather than where it ends.

### Fixed

**The second opinion did not find a reader bug on its first run. It found a
missing brace.**

`struct SpecialistRow: Decodable {` was never closed, and the
`extension ApiClient {` that should have followed it was never opened.
**Ninety-five client methods** — the whole *face it shows the world* block,
avatar through experience — were declared as members of a two-field wire model
rather than on the client. Every screen calling `ApiClient.shared.avatar(…)`
had nothing to call.

Three guards were in a position to see it and none did:

```
brace balance (0.57.5)   passed — the file balances; one brace has the
                         wrong opener
the member check (0.58.1) passed — the methods are in ApiClient.swift,
                         just nested inside a struct
this file's own pins     passed — SpecialistRow is not pinned
```

What gave it away was a check written to audit the reader rather than the
code, and what it caught was the thing nobody had thought to assert, because
it is too obviously true to say out loud: **a wire model is data, and data has
no methods.** That assertion is here now, and it costs one line to run.


Suites: **1547 + 1528 = 3,075** across 217 files.

## [0.58.6] — 2026-08-08

### The refusal surfaces, and a reader that read a struct as empty

0.58.5 closed by naming this batch — the screens that render what the platform
will **not** do, from data rather than prose, so the screen cannot drift from
the behaviour. An empty render of one of those does not read as a bug. It
reads as *no limits*, which is the worst failure mode a consent screen has.

Five of them, read at both ends across all three shells: the overlay
catalogue's kinds and its refusals, the microphone vocabulary's refusals, the
places a wearable may be lent, and the cloud-contribution log. **All correct.**

Two rounds running the finding was on every shell at once rather than on one —
the shells agree with each other and disagree with the server. Cross-checking
the clients against each other would have found neither the guided tour nor the
microphone disclosure. This table is the only instrument in the repository that
catches that, which is the argument for growing it on a round where it finds
nothing.

### Added

- Nine more pinned rows: `OverlayCatalogue` with its kinds and refusals,
  `MicVocabularyOut`, `MicPlacesOut` with its places, and `ContributionView`
  with its log — plus the Kotlin reads of the same three routes.
- The reader learned three more lookups, all still inside the one pinned
  function or the module it lives in. `{**dict(r), …}` over
  `conn.execute("SELECT id, condition, … FROM …")` — the column list is a
  string literal right there, so the keys `dict(r)` carries are readable;
  `SELECT *` is not, and is refused. A `**spec` bound by a *comprehension*
  generator rather than a `for` statement. And `list(TABLE.values())` over a
  module table written as a dict comprehension.

### The trap it walked into first

Injecting a defect into PDI's `ComplianceProgram` did not fail the guard, and
that was the guard's fault rather than the injection's. PDI declares
`struct X: Decodable { let a: T; let b: T }` on one line, and the property
pattern required end-of-line — so it read that struct as **empty**, and an
empty model passes every comparison. The pin had been checking nothing since
the day it was written. Semicolon-separated properties are read now, computed
ones are still excluded, and the round that found it is the round that
injected rather than the round that wrote the pin.

Suites: **1547 + 1520 = 3,067** across 217 files.

## [0.58.5] — 2026-08-08

### The disclosure that showed nobody

0.58.4 shipped a pinned table — each row a shell model held against the backend
function whose `return` is its contract — and closed by naming where it should
grow: the surfaces where an empty render reads as *nothing to report* rather
than as a bug. The first one checked was worse than the guided tour.

`GET /rooms/{id}/mic` and `GET /places/{surface}/{id}/microphone` answer with
**`microphones_lent`**. All three shells read `lent`. The disclosure naming who
in a room has lent the profiles an open microphone — device, gain, and since
when — rendered as **nobody**, on the iPhone, on the Android and on Windows.

The route's own docstring spends a paragraph on why that disclosure is readable
by everyone present rather than by its subject alone, because a disclosure only
its subject can see is not a disclosure. One that nobody can see is less than
that.

The inbox and the overlay disclosure were checked in the same pass and are
correct. They are pinned anyway: a row that passes on the day it is written is
the point of the table, not a wasted one.

### Added

- Six more pinned rows here, and the reader learned to follow three more
  shapes, all of them assignment inside the one pinned function: `out = {...}`
  with `out["k"] = …` after it, `rows = [{...} for r in …]`, and `rows = []`
  with `rows.append(row)`. 0.58.4 named the last of those as a limit and
  refused to guess past it. It is read now rather than guessed.
- A `**spec` is resolved the same way — to a module-level dict of dicts whose
  values all carry the same keys, directly or through the
  `for _k, spec in SOMETHING.items()` that produced it — and refused outright
  when it is anything else. The refusal is the feature: a pin this file cannot
  read is one it must not invent.

### Fixed

- The live-microphone disclosure reads `microphones_lent` on the iPhone, the
  Android (both the room and the place route) and Windows. It was reading
  `lent`, and showing nobody.

Suites: **1547 + 1520 = 3,067** across 217 files.

## [0.58.4] — 2026-08-08

### The key was right and the shape was wrong

0.58.3 checked that every key a shell decodes is one the backend can send, and
left a named gap: the check is a *union*, so a key read off the **wrong**
response passes. The obvious next step was to bind each decode site to the
route it calls and compare per route.

### Four attempts at that, and why none of them shipped

The binding is not derivable by reading this backend, and every narrowing that
removed a false positive removed real coverage with it:

1. **Route to handler to return.** Handlers delegate, wrap (`{"beacons": [...]}`)
   and merge (`{**metrics}`). One level of following resolved 141 of some 400
   routes, and the mismatch list was 41 rows of which the ones checked by hand
   were the reader's fault.
2. **Flat-only on both sides.** Coverage fell to 52 sites and the mismatch
   rate stayed above four in ten.
3. **Bind on the container key** — `chapters: [{...}]`. The first run reported
   five defects that are not there: `llm.py` builds `{"messages": [...]}` as an
   outbound *request*, and the backend's inputs share a vocabulary with its
   outputs. Restricting to route-reachable returns fixed that and hid the real
   finding instead.
4. **Disjointness rather than subset**, to survive a key with two shapes. It
   survives them by not judging them.

The rule narrow enough to be sound covers two sites per product and finds
nothing. That is the honest ceiling of inference here, and it is worth writing
down rather than shipping a guard whose failures are mostly its own.

### Added

- `test_the_shape_inside_the_shape.py`, in all three products. It infers
  nothing: each row **pins** a shell model to the backend function whose
  `return` is that model's contract. A human read both ends once; the file
  holds them together from then on. It is small on purpose and meant to grow
  one verified row at a time.

### Fixed

The guided tour, broken on both phones and correct on Windows:

- `/tutorial` sends `chapters: [{chapter, steps}]`. The iPhone read `key` and
  `title` off the chapter, so every row of the outline rendered as `?`; the
  Android read the same two and built a list of empty pairs. It also looped
  over a `lessons` key the route has never sent.
- `/tutorial/start`, `/tutorial/progress/{id}` and `/tutorial/done` all answer
  with `tutorial.where`, which **wraps** the step. Both phones decoded the
  wrapper as a bare step and read `title`, `key` and `next` off the top level.
  All three buttons showed an empty line.
- `/tutorial/steps/{key}` sends the lesson text as `what`. The iPhone read
  `body`, got nil, and fell back to repeating the title.

Windows had all four right — and carried a comment saying a chapter never had
a `key` or a `title` of its own. Somebody fixed one shell and the note never
crossed to the others, which is the argument for a file rather than a comment.

Suites: **1547 + 1520 = 3,067** across 217 files.

## [0.58.3] — 2026-08-08

### The key the server never sends

0.58.2 closed by naming where the seam goes next. The receivers whose type is
known for free are checked now; the tier past them is the receiver whose
members are *keyed* rather than named — `optString("worn")`,
`GetProperty("mode")`, a `Decodable` property whose name **is** the wire key.
A renamed backend field is the same silent break as a renamed method, except
it does not fail on a build machine. It fails on a phone, as an empty list or
a nil string, and the screen renders as though the server had nothing to say.

Matching a key to the route it came from needs a type checker this machine
does not have. Matching it to the backend's whole vocabulary does not, so the
guard asks only what it can answer honestly:

```
is this key one the server can emit anywhere at all
```

Four live breaks, each of them a screen that renders empty:

* `GET /places/{surface}/{id}/overlay` answers with `overlays`. The iPhone and
  the Android read `worn`. That is the disclosure naming who in a place is
  wearing a face over their camera — the reason the feature is allowed at all
  — and on both phones it was always the empty list.
* `POST /auth/oauth/{provider}/start` answers with `url`. Both phones read
  `authorize_url`, got nil, and had nothing to open. **Sign in with Google and
  Apple could not start on either.**
* `/dock/where/{face}` answers with `screen`, `path` and `title`. The Android
  helper printed `screen · tab`, so half of every *where does this live*
  answer was blank.
* `/interactors/{id}/referrals` answers with `provider_id` and `opened_at`.
  All three shells read `specialist_profile_id` and a boolean `opened`.

Windows had the overlay, the sign-in and the fine-tuning run right and the
referral wrong; the iPhone had all four wrong. There is no shell that is
reliably the correct one, which is the argument for checking all three.

### Added

- `test_the_key_the_server_never_sends.py`, in all three products: every key
  a shell decodes must be one the backend can put on a response — read from
  all four places a key reaches the wire (a dict literal, a key assigned after
  the dict is built, a model field, and `dict(row)`, which makes every column
  a key).

### Fixed

- The overlay disclosure on iPhone and Android reads `overlays`. It was
  reading `worn`, and showing nobody.
- Sign in with Google and Apple on iPhone and Android reads `url`. It was
  reading `authorize_url`, and opening nothing.
- The Android helper's *where does this live* line reads `title`, not `tab`.
- The referral list on all three shells reads `provider_id` and `opened_at`.
- The fine-tuning run on iPhone and Android reads the metrics the route
  returns rather than a `status` and an `examples` count it never had.
- Nine `Decodable` structs whose result is discarded named keys the routes do
  not send. Nothing read them, so nothing broke — they were documentation of a
  wire shape that was never true, and they are empty structs now.

### The traps it walked into first

Three, all in the reader. A regex that ends a struct at the first `\n}`
swallows everything after a nested one, and `CustodyProvenance` has three.
`var stands: Bool { valid ?? verified ?? false }` is a computed property and
`let _: Ok = try await …` is a discarded binding; neither is a key.
`case profileId = "profile_id"` renames it, so reporting `profileId` reports
the shell's own spelling as the server's. And a fourth in the vocabulary
rather than the reader: reading only dict literals reported some sixty fields
that are on the wire every day.

Suites: **1542 + 1518 = 3,060** across 216 files.

## [0.58.2] — 2026-08-08

### The colour that wasn't in the palette

0.58.1 closed by naming where it should go next. `state.x` is not the only
receiver in these trees whose type is known for free — it is only the first.
Any receiver that exactly one file declares can be looked up the same way,
and there are eight of them per product:

```
iOS      state.x  ApiClient.shared.x  Theme.x
Android  vm.x     ApiClient.x         Qrme.x
Windows  AppState.Current.X           ApiClient.Shared.X   {StaticResource X}
```

Widening it found one, and it is the cheapest kind of break there is. The
Android problem-report card painted itself with `Qrme.Card2`; the theme
declares `Card` and has never declared a second. Both sibling products paint
the same card with `Card`, so it was a one-character slip no amount of reading
the diff would have caught — and Compose has no fallback for an unresolved
colour, so the whole screen file fails to compile with it.

```
asked     is the thing a screen reaches for on its state object there
mattered  is the thing it reaches for on *anything* there
```

The API clients came back clean — **1,613 call sites across nine shells**,
every one naming a method the client actually has. That is worth asserting
anyway. 0.58.1's own defect had been sitting in `main` for rounds; the value
of a guard is not only what it finds on the day it is written.

### Added

- Every member reached on an API client, a theme object or `App.xaml` is now
  read against the one file that declares it, alongside the state objects
  0.58.1 covered — eight receivers per product, with a floor under each so a
  moved file cannot quietly empty the comparison.

### Fixed

- The Android problem-report card asked the theme for `Qrme.Card2`. It now
  asks for `Qrme.Card`, which exists.

### The trap it walked into first

Widening the check to the API clients immediately reported two methods that
are right there in the file — `Features` and `SetFeature` on the Windows
client, whose return type is
`Task<System.Collections.Generic.Dictionary<string, bool>>`. The C#
declaration pattern had no dot in it. Narrow and true is the standing rule
here, and this is the other edge of it: a pattern narrower than the language
reports defects that do not exist. Both the dot and a test for it are in now.

Suites: **1542 + 1509 = 3,051** across 215 files.

## [0.58.1] — 2026-08-08

### The member that isn't there

0.58.0 ended by restating the standing gap: no Swift, Kotlin or C# toolchain
on this machine, so the native UI is asserted by reading and not by running —
and that round widened the amount of screen riding on it. The honest response
is not to pretend a compiler exists. It is to keep taking the classes of
compile error that *can* be caught by reading. 0.57.5 took duplicate
declarations and unbalanced braces; 0.57.6 took the markup; this takes the
next one.

Each shell has exactly one object the screens read their session from, and
exactly one file that declares it — so `state.x` is not a guess about types.
It is the one receiver in these trees whose declaration is known without
resolving anything.

```
asked     do the screens parse, and do they say the right things
mattered  is the thing they reach for actually there
```

### Added

- `test_the_member_that_isnt_there.py`, in all three products: every member a
  screen reaches for on its shell's state object must be declared by it.

Clean here on the first run — the finding was next door, and this product
gets the check because the next one could be here.

### The trap it walked into first

The first extractor reported four defects that were not there: `call` on the
Kotlin view models and `IsSignedIn` / `IsEnrolled` on the C# ones. `fun <T>
call(` puts a type parameter between the keyword and the name, and
`public bool IsSignedIn => …` is expression-bodied with no `{` or `(` after
it. Both shapes are matched now and tested for; a guard that reports four
defects that are not there is one nobody reads.

Suites: **1542 + 1502 = 3,044** across 215 files.

## [0.58.0] — 2026-08-08

### The key the phones never carried

0.57.9 ended by naming the shape: a guard that verifies *a* line rather than
*every* path has a blind spot, and the same audit run on a different header
would probably be productive. It was — but not the way it was expected to be.
Asked of every header the console attaches to every request, the answer was
not *some paths miss it*. It was **one header the shells do not send at all.**

```
x-llm-api-key
```

The person's own model key. Pasted into the console since 0.4.3, read by the
backend per request into a context var and never written down, and sent by no
native shell. A key set on the desktop was used on the desktop, and the
deployment's key was used on the phone — same account, same profile, two
different credentials, and nothing anywhere saying so. The phones even drew
the provider list with *ready* / *no key* beside each row, which is the
**deployment's** key state: the screen showed a fact about somebody else's
credential and offered no way to supply your own.

```
asked     does every request carry the headers this client sends
mattered  does this client send the headers the product has
```

### Added

- The key on all three shells: held on the device (UserDefaults,
  SharedPreferences, the app's local state) and never in the account, pushed
  into the API client once and sent from the same place the language header
  goes.
- A field to set it, under the four rows the console has had since 0.4.3 —
  the same keys and the same words, so no new console/native split appears.
  Saving an empty box is the clear; there is no flag to leave switched on.
- `test_every_header_the_console_sends_the_shells_send_too`, which reads the
  console's own shared helper rather than a list written in the test, so a
  header added there cannot quietly stay there.

### Changed

- `native_dead_keys.txt`: 276 → 273 rows, ceiling 104 → 103. `action.save`
  was dead on all three shells because no shell had a form to save.

Suites: **1518 + 1520 = 3,038** across 214 files.

## [0.57.9] — 2026-08-08

### A funnel only funnels what goes into it

0.57.8 ended by naming its own next question: guards get written in one repo
and not ported, so compare the three `tests/` directories. Twenty-four files
exist in exactly two of the three, and most of those are genuine product
differences. One was not.

`test_the_language_nobody_was_sending.py` exists in JIM-mini and PDI and not
in QRME — the product whose premise is a profile that speaks in a person's
language, and which built an accountless *stranger* surface over three
rounds. Every refusal it raises goes through `refusal_language`, which reads
`Accept-Language` whenever the caller is not an owner.

**A first pass said QRME's shells never sent the header. That was a
case-sensitive grep and it was wrong** — all three send it, lower-case, from
their shared request helper. What the guard could not ask, in any of the three
products, is the question that mattered:

```
asked     does this client set the header with the resolver
mattered  does every request this client makes carry it
```

Because the answer was **no**, everywhere:

```
QRME      Windows 21 of 22 sends, iOS 3 of 4, Android 1 of 2
JIM-mini  Windows 15 of 16, iOS 1 of 2,  Android 4 of 5
PDI       Windows  3 of 4
```

Uploads, streams and raw-response reads, each building its own request beside
the shared helper and setting only `authorization`. Those calls carry a token,
so a *valid* token still picks the owner's stored language — but an expired
one is not a principal, and the refusal falls back to a header that was not
there. Forty-four requests across three products.

### Fixed

- One dispatcher per shell rather than one line per call site, because a line
  per call site is precisely the thing that went missing forty-four times.
  C# gained `Dispatch(HttpRequestMessage)`, Swift a `dispatch(_:)`, and the
  Kotlin clients' remaining connections got the header where they are built.

### Added

- `test_every_place_a_request_leaves_the_shell_carries_the_header`, which
  walks every dispatch site rather than every line that mentions the header —
  the half the original could not see, in the product that had it and the two
  that did not.
- The guard itself, in QRME, four releases after it was written next door.

Suites: **1518 + 1518 = 3,036** across 214 files.

## [0.57.8] — 2026-08-08

### The rows the guard skipped were the interesting ones

`test_a_shell_does_not_print_what_it_translated.py` has, since 0.54.0, opened
its row reader with

```python
if "{" in english:
    continue
```

Every row with a slot in it went unchecked, for four releases. That is not a
corner of the table: a row with a slot is a row *about something*, which is
most of what a screen actually says — and a sentence assembled around a value
is the one a screen is most likely to hand-build, because building it is what
the code is already doing.

```
? $"closest overlap {best}, below the {th} threshold for naming anyone"
```

against `ns.who.below` — *"closest overlap {best}, below the {threshold}
threshold for naming anyone"* — the same sentence, hole for hole, in that same
shell's table in ten languages.

```
asked     does a screen print a whole English row verbatim
mattered  does a screen print an English row the reader will never see
          translated, however it is spelled
```

Found from the other side and by accident: 0.57.7 was fixing a Windows page
that would not parse, read the code-behind while deciding a rename, and saw
seven of these on one screen. This closes the general case rather than the
seven.

**A slotted row is compared by its fragments**, not by rebuilding the
sentence — the shell's holes are not the table's, and `{en.Seconds:F1}s` is
not `{secs}`. The row is split at its slots and the literal text between them
is matched. Fragments shorter than a phrase are dropped, so `Built {date}`
contributes nothing; that is a deliberate miss and the file says so.

### Two false findings, caught before they shipped

The check's own first run against the sibling products reported two defects
that were the reader's, not the code's, and both are now tested against:

* `L10n.t("cw.sensitivity", …)` is a screen *asking* for a row, and the
  fragment *"sensitivity"* is inside that key. A key is not something a reader
  sees.
* `$"{(int)Math.Round(p.Confidence * 100)}"` matched the row *"Confidence
  {pct}% — earned from…"* on the word `Confidence`, which is a C# property
  there and a heading here. The holes come out of the shown string too — the
  same removal that is done to the row.

Same lesson as the eighty-six protocol values that shaped the original: strip
what is not prose before comparing prose.

### Fixed

Twenty-seven sites across the three shells, twenty-four of them on the desktop:

* the whole provenance footer — *Generated by … grounded in … source item(s) ·
  moderation …* — hand-built in English on the Windows compose and chat pages
  **and on both phones**, beside `nprv.generated` and `nprv.licensed` which the
  iPhone's own `ProvenanceFooter` was already using one file over;
* the watermark-recovery verdict, the objection status, the relationship
  confirmation, the effective-model and effective-age lines, the licence offer,
  the pack-sync count, the payout receipt, the held-listing reason and the
  match line;
* the signing credential list, which printed *verified at enrolment: basic* —
  three `nsig.level.*` rows the iPhone had been reading all along while the
  desktop printed the wire value raw.

### Changed

- `native_dead_keys.txt`: 300 → 276 rows, ceiling 127 → 104. Every struck row
  was struck because a screen started asking for it. The two files ask the
  same question from opposite ends and this is the first round where the
  answers met in the middle.
- One new row, `nsig.registered`, for a line the Windows signature page typed
  out in English beside the tier names it was also typing out.

Suites: **1518 + 1512 = 3,030** across 213 files.

## [0.57.7] — 2026-08-08

### The files the release never touched

0.57.6 ended by naming its own next question: whatever a guard checks, ask
first which files it does not open. Asked of the release itself, the answer is
three files per product.

A cut bumps `pyproject.toml`, `<pkg>/api.py`, `app/package.json`, the lock
file, the README banner, the README release row and the changelog. That number
reaches everything a *server* or a *console* reports. The three native shells
report their own version from three build files no step in that list touches:

```
native/ios/project.yml               MARKETING_VERSION: "0.1.0"
native/android/…/build.gradle.kts    versionName = "0.1.0"
native/windows/*.csproj              (no <Version> at all)
```

```
asked     does the product carry the version it cut
mattered  does the thing a person installs carry it
```

Nine declarations across three products, every one of them `0.1.0` or absent,
through every release since the shells were written.

This is not cosmetic in the way a stale README is. `versionName` is the string
on the Play listing and in Settings › Apps; `MARKETING_VERSION` is the App
Store version and the one a crash report is filed against; the `.csproj`
version is what Windows shows in a file's Properties. An install reporting
`0.1.0` cannot be told apart from any other install — and these products ship
a problem collector, which is the part that makes the omission bite.
`versionCode` was worse: Android refuses an upload whose code does not
increase, so a store submission was going to fail on the first try regardless.

### Added

- `test_the_files_the_release_never_touched.py`. The three build files are
  read against `pyproject.toml`; `versionCode` and `CURRENT_PROJECT_VERSION`
  are **derived** from the version rather than kept by hand, because a counter
  beside a version string is two things to forget instead of one.
- The same files carry what a shell is allowed to do — the plist usage
  strings, the `uses-permission` rows — and those are checked against the
  platform APIs each shell actually calls. iOS *terminates* an app that opens
  a camera with no `NSCameraUsageDescription`; Android throws.

### Fixed

- All nine declarations now carry the release. The `.csproj` files gained
  `<Version>`, `<AssemblyVersion>` and `<FileVersion>`, which they had never
  had.

### A trap walked into while writing this

The first pass at the capability check read `LAContext` in QRME's
`Signing.swift` and `BiometricPrompt` in `Signing.kt` and was ready to report
two missing declarations. Both are in **comments** — prose explaining why the
shells use WebAuthn instead, since a local biometric check is the app's own
word about itself and an assertion is not. A guard that counts a mention as a
use invents a defect, which is worse than missing one. Comments are stripped
before anything is counted, and a test holds that line.

Suites: **1511 + 1502 = 3,013** across 213 files.

## [0.57.6] — 2026-08-07

### The half of the Windows shell that is not code

0.57.5 added a parse check for the native shells, globbed `*.swift`, `*.kt`
and `*.cs`, and reported all three parseable. The Windows shell's **screens
are not C#** — they are XAML, 3,700 lines of it, more than every `.cs` file in
`Views/` put together — and the check never opened one.

```
asked     do the files that look like code still parse
mattered  do the shells' screens still parse
```

Five pages across two products do not parse. Two of them are here. Each is a
single element carrying `x:Name` twice:

```xml
<TextBlock x:Name="ConsentText" TextWrapping="Wrap" FontSize="12"
           Foreground="{StaticResource QrmeT2Brush}"
           x:Name="NothingNote" />
```

Duplicate attributes are forbidden by XML itself, so no conformant reader gets
past the tag and the build stops there. It is 0.57.4's Swift defect in markup,
arrived at the same way: a second name was needed and it went onto the element
that was already there.

### Added

- Four markup checks in `test_the_shells_still_parse.py`, all of them things a
  XAML compiler refuses outright rather than things a reviewer would prefer —
  the page is well-formed XML; no two elements in it share a name; every
  handler it names exists in its code-behind; every control the code-behind
  drives is named in the page. Reach floors on all four, and four injected
  defects confirming each can fail.
- A state the desktop voice screen never had: with no profile it read
  `AppState.Current.Pid`, found nothing and returned, leaving three cards of
  headings over buttons that answered nothing. `nvoi.needprofile` — *Create a
  profile first* — was in the table already, translated ten ways, asked for by
  nobody.

### Fixed

- `SignaturesPage.xaml` and `VoicePage.xaml` each carried a duplicate
  `x:Name`, and in both cases the code-behind drove **both** names, so the
  rename had to decide which control was meant rather than drop an attribute.
- The Windows voice screen printed seven sentences in English beside their own
  translations — the consent line, the sample counts, what enrolment still
  wants, when the voiceprint was built, what happens to a retired one, and how
  many samples a withdrawal deleted. The iPhone built two of the same four the
  same way. `test_a_shell_does_not_print_what_it_translated.py` compares
  *literals* against the table, and every one of these is interpolated, so the
  only signal was a row nothing asked for.
- `nvoi.record` and `nvoi.sample` are both *Record a sample* in all ten
  languages. Windows labelled one button from the first at load and the second
  after a recording — one button changing which translation it answers to
  halfway through. One key now; the short row is deleted from all three tables.

### Changed

- `native_dead_keys.txt`: 311 → 300 rows, ceiling 134 → 127.

## [0.57.5] — 2026-08-07

### Nothing here builds the phones, so nothing here noticed when they stopped

0.57.4 shipped a fix and a defect in the same release. Renaming iOS's `venue`
to `locality` collided with a `locality` already declared in the same
`TradeSection` — two stored properties of one name in one type, which does not
compile. It reached `main` and sat there for a release.

The reason is worth writing down rather than apologising for: **every guard in
these repos reads the shell sources as text.** The request-body guard extracts
call shapes; the response guards extract declarations; none of them parse, so
none of them can see a syntax error. `tsc --noEmit` covers the console. There
is no Swift, Kotlin or C# toolchain on the machine these run on, so there is
nothing to compile with.

    asked     do the shells say the right things to the server
    mattered  do the shells still compile

### What this checks, and what it does not

`test_the_shells_still_parse.py` does not typecheck. It checks the one class
of breakage that is invisible to a text-reading guard, cheap to detect without
a compiler, and *certain* to stop a build:

* a name declared twice in one scope — a Swift type's stored properties, a
  Compose function's `remember`ed state, a C# type's fields;
* braces that do not balance, counting through strings and comments.

A green run here does not mean the shells build. It means they do not contain
the specific mistake that got past everything else. That is a narrow claim,
and it is stated narrowly in the file: the whole arc since 0.56.4 has been
guards that measured slightly the wrong thing and passed, and a check that
promised "these compile" would be the next one.

The scope reader counts braces rather than matching a regex, because a pattern
that stops at the first `}` reads half a type — and half a type has no
duplicates in the half it did not read. Nested declarations are excluded: a
`var` inside a closure is not a member, and an inner type's property belongs
to the inner type.

Three defects were injected and confirmed to fail it, the first being 0.57.4's
own, put back verbatim.

## [0.57.4] — 2026-08-07

### The inputs the shells never asked for

0.57.3 found seven defects in what the native clients send, fixed one, and
recorded six with the same sentence beside each: *this needs an input the
shell does not collect*. Recording was honest — inventing the missing value
is what this family of guards exists to stop — but a recorded defect is still
a dead button. This release collects the inputs.

* **Coordination.** `CoordinateRequest` requires `from_department` as well as
  a goal, and all three screens asked only for the goal, so coordinating an
  organization answered 422 everywhere. Windows, iOS and Android now have a
  department field beside the goal.
* **The desk camera.** `CameraSet` takes a URL — "point the desk at its own
  camera, or clear it back to the sample view" — and all three sent
  `enabled: true`, a switch for a thing with no address. There is a camera
  address field now, and clearing it clears the camera.
* **Marketplace settings.** `MarketPrefs` is where "here" is and how far out
  to look. The shells sent `show_offers`, which no model has ever had, and
  Android read it back off the response as the whole answer. The screens now
  carry a locality and an **include things offered remotely** switch, which
  is the boolean that actually exists.
* **Listing a profile.** The listing takes a blurb and tags; where it is
  offered is `/place`'s job. The `locality` the shells also sent was
  discarded on arrival, and its box is gone from the listing card — the place
  card has always had its own.
* **Putting a price on a listing.** `OfferIn` is price / currency / stock.
  Windows and Android sent `amount`, iOS sent it too through a body the guard
  could not read, and none sent the required `price`. "Lowest you would take"
  collected a counter-offer floor the server has no concept of, and that box
  is gone rather than left to look like it does something.
* **Accepting an exchange item.** Windows sent an empty body where `actor_id`
  is required; it now sends the signed-in interactor.

`tests/native_bodies_unverified.txt` is empty, at a ceiling of zero.

### A compile error 0.57.3 shipped

Renaming iOS's `venue` to `locality` collided with a `locality` already
declared in the same `TradeSection` — two `@State` properties of one name,
which does not compile. Nothing here builds Swift, so nothing said so, and
the request-body guard cannot see a syntax error because it reads the file as
text. The duplicate is gone with the listing card's dead locality box.

Worth stating plainly: the guard that found seven real defects would not have
found that one, and the release that fixed them introduced it.

### Also removed

`trade.accept` and `trade.show_offers` are gone from all three L10n tables —
ten languages each, for two controls that no longer exist.

## [0.57.3] — 2026-08-07

### The guard read one client and the finding came from four

0.57.2 checked what the console sends against the model FastAPI validates
with, and the defect that motivated it — a field all four clients sent and no
model declared — was found by reading the four clients *by hand*. The guard
read one.

    asked     does the console send a body the route can accept
    mattered  does any client send a body the route can accept

So this release reads the other three. The comparison is the same and
imported; only extraction differs, and it has to, because these clients share
nothing:

    C#      Post($"/organizations", new { name }, token)
    Swift   request("/rooms", method: "POST", body: ["topic": t])
    Kotlin  request("/profiles/$id/compose", "POST", JSONObject().put("topic", t))

### Seven defects, each in every client that makes the call

That agreement is the evidence: three independently written shells do not
drift the same way by accident. **Placing a marketplace listing has never
worked from any native surface.** `ListingPlace` requires `locality` —
somewhere a person typed — and Windows, iOS and Android all send `venue`, a
key from `qrme.rated.VENUES` belonging to a different model. Every press
answered 422. All three now send `locality`.

The other six are recorded rather than fixed, at a ceiling of sixteen rows,
because each needs an input the shell does not collect or a decision about
what a control should mean: coordination requires `from_department` and the
screens ask only for a goal; `CameraSet` takes a URL where all three send an
`enabled` boolean; `MarketPrefs` has no counterpart for the `show_offers`
switch all three send *and* Android reads back; listing a profile takes blurb
and tags while the shells also send a `locality` the route discards; and
Windows puts a price on a listing with `amount` and `accept_price` where
`OfferIn` requires `price`. Correcting a field name alone would move those
422s rather than remove them.

### Thirteen of the first twenty findings were the extractor

Two faults, both already familiar:

* **C# infers a property name.** `new { name }` declares `name`; reading only
  the `x = y` form found `learner_id = learnerId` and missed every inferred
  one, accusing eleven routes of never sending fields they send on every call.
  Fifth time in this arc the extractor wrote the findings it reported.
* **Nested keys are not top-level keys.** Swift's
  `body: ["items": [["content": c]]]` sends `items`; a flat scan also found
  `content`, and `/rooms` supplied `id` and `kind` from inside `participants`.
  Sixth time — the console guard has `_top_level` for exactly this, and the
  idea did not travel with the file.

Kotlin needed the opposite of the Swift fix: the key sits *inside* the
`.put(` parentheses, so emptying nested brackets removed every key in the file
and turned the Android client into a hundred and forty false "never sends
required". Depth has to be measured at the `.put`, not applied to the text.

### And the reach floors caught a seventh

Ported to PDI, the Windows reader found **zero writes**. That client builds
its messages by hand — `new HttpRequestMessage(HttpMethod.Put, "/records") {
Content = JsonContent.Create(new { key, value }) }` — where QRME wraps them in
a helper. Zero found is indistinguishable from zero wrong, and only the
per-client floor said so. The reader now knows both shapes, which also took
QRME's own Windows count from 170 writes to 196.

| | Windows | iOS | Android | found |
|---|---|---|---|---|
| QRME | 196 (181 readable) | 194 (129) | 194 (128) | **7** |
| JIM-mini | 55 (51) | 55 (37) | 55 (37) | 0 |
| PDI | 13 (12) | 12 (7) | 12 (9) | 0 |

## [0.57.2] — 2026-08-07

### Every guard in this family reads the answer. None of them read the question

0.56.4 through 0.57.1 asked four clients the same thing — C# records, Swift
structs, Kotlin `org.json` reads, TypeScript type arguments — and the question
was always *does this client understand what comes back*. Thirty-three defects
across the four.

Not one looked at what a client **sends**. The console guard makes that
explicit in code: it skips any call carrying `method:`, which in this client is
194 of them. Those calls were checked by nothing, in either direction, and a
request body is the same defect in mirror image. If the model calls a field
`title` and the client sends `name`, FastAPI either answers 422 — a button that
does nothing, forever — or drops the value silently and stores the row without
it. Both are invisible from the client, which sent something and got a
response.

    asked     does the client understand the answer
    mattered  does the route understand the question

### What it is checked against

`app.openapi()`, not a regex over the Pydantic classes. The schema FastAPI
publishes *is* what FastAPI validates against, so this guard cannot describe a
rule the app does not enforce. Reading the models by hand would have been a
fifth extractor to get wrong.

Three questions: a required field the client never sends; a field the client
sends that the model has no property for; and a write with no body at all to a
route whose model requires one — listed separately because a guard that only
walks bodies finds nothing wrong with sending none.

| | writes | readable | matched a model | found |
|---|---|---|---|---|
| QRME | 192 | 162 | 158 | 0 |
| JIM-mini | 113 | 70 | 92 | **2** |
| PDI | 42 | 33 | 34 | 0 |

QRME's writes are correct. That is a result, not an absence: three injected
defects were confirmed to fail this guard before it shipped.

### The first run's eighty-two findings were all mine

A body written as the bare identifier `body` gets its shape from the enclosing
function's parameter. The first version searched backwards for `(body: {` with
no left edge, found the parameter of a *previous* property in the same object,
and credited its fields to this call — `POST /profiles/{id}/chat` was reported
as sending `birthdate` and `display_name`, which belong to `createProfile`
forty lines above. Fifteen of forty-two lookups landed in the wrong function,
and between them produced eighty-two findings, every one phrased as somebody
else's defect. Bounding the search to the member fixed it, and the count went
to zero.

A spread produced the eighty-third: `{ ...(to ? { to } : {}), text }` became a
field called `...(to ? {}`. A body this guard cannot read is now a body it
refuses to judge — inventing a defect is worse than missing one.

### And then the ratio caught a fourth

Green in all three, and JIM-mini read 28 of its 113 writes against QRME's 162
of 192. The parameter may be first or fifth: QRME writes `(body: { ... })` and
JIM-mini writes `(uid, body: { ... }, token)`, and a pattern anchored on the
opening paren reads one whole and the other at a quarter. Fourth time in this
arc a borrowed pattern has read one product and quietly skipped another, and
the first time the run was green either way — because a body it cannot read is
a body it does not judge.

Reach after the fix: QRME 99 → 162 readable, JIM-mini 28 → 70, PDI 25 → 33.
JIM-mini's two findings only appeared on the far side of it.

## [0.57.1] — 2026-08-07

### The fourth client, and it was the only one wrong

0.56.4 through 0.57.0 built one guard three times — for the Windows client's
C# records, the iOS client's Swift structs, and the Android client's `org.json`
reads. Nineteen defects in C#, nine in Swift, eight in Kotlin, and the running
lesson of all three was that fixing a defect in one client is not fixing the
defect.

There is a fourth client, and it is the one most people use.
`test_the_console_is_a_client_too.py` was written in 0.44 for exactly this
blind spot — it found sixty-four routes a desktop owner could not reach — and
it asks whether the console *calls* each route. It never asked what the
console does with the answer.

    asked     can the console reach every route
    mattered  does the console read back what the route sends

This client declares more than the other three combined: 246 shapes, 1,712
fields, 194 GET bindings, each carrying its expected shape as a type argument.
And TypeScript is erased at build time, so nothing checks a declaration
against reality at runtime. A field the route does not send is `undefined`,
and `{undefined}` in JSX renders as *nothing* — the layout closes up around it
and the screen looks finished.

### What it found — four, all real, all visible

**The delegation screen could not delegate.** `/profiles/{id}/delegation`
sends `{"delegation": false, "phases": [...]}` — a boolean, with the list
beside it. The console declared `delegation` as an object-or-null and read
`policy.delegation.phases` and `policy.delegation.enabled` off it. Both are
`undefined` on a boolean, so the screen showed every profile as un-delegated
and drew no phase toggles, and with no toggles there was no way to switch it
on. Thirty lines further down the *same file* reads `offer.delegation` as a
boolean and `offer.phases` at the top level, correctly. One screen, one
response, two readings, and only one of them right.

The route was also wrong to advertise only the chosen phases: a capability
advertisement that lists what an owner has already picked says nothing while
they have picked nothing. It now sends `delegable` — the vocabulary — beside
`phases`, the choice.

**A dashboard tile that has never shown a number.** Home reads
`stats.engagement_average`; the route sends `engagement_avg`. The tile has
rendered `—` since the day the field was named.

**Suggested friends was always empty.** The route sends `suggested`; the
console declared `suggestions`, in *both arms* of a union so neither could
match, and the reader's `?? []` fired every time.

**`Stats.surfaces` declared `number`** where the route sends a list.

### The other three clients had none of them

That is the inversion worth recording. Every release since 0.56.4 found the
same defect sitting unfixed in a client nobody had checked yet. This one
checked Windows, iOS and Android against all four findings and they were
right in every case — `optBoolean("delegation")` in Kotlin,
`JsonPropertyName("suggested")` in C#, `let suggested: [SuggestedRow]` in
Swift. Three clients correct, one wrong, and the wrong one is the one a
desktop owner actually opens.

### Three of the first findings were the guard's own

Thirty of the first run's thirty-eight findings came from reading the verb on
one line. This client writes

    req<WallPost>(`/profiles/${profileId}/wall`,
      { method: "POST", body, token }),

with the verb on the *second* line, so 174 writes were driven as GETs and
compared against whatever the list route returns — every field missing, in
five types at once. It is the third release running in which the check for
*is this a GET* was itself the defect. Arguments are now read to the call's
own closing paren.

Emptying a nested type body instead of deleting it fixed a second: `delegation:
{ ... } | null` had become `delegation: | null`, and the guard reported a real
field as *declared `| null`*. And a union is satisfied by any arm, not by its
first — the friends call was reported against a shape it never claimed to be
the only one. It was wrong anyway, but a guard that is right by accident will
be wrong on purpose next time.

### Ported, and the ports found more

| | shapes | fields | GETs | driven | found |
|---|---|---|---|---|---|
| QRME | 246 | 1,712 | 194 | 85 | **4** |
| JIM-mini | 100 | 623 | 110 | 49 | **2** |
| PDI | 33 | 224 | 60 | 27 | 0 |

All six are fixed rather than recorded, and all three record files sit at a
ceiling of zero. This client marks a field optional when it genuinely comes
and goes, so a missing required field is missing — there is no legitimate
state to record, only a declaration to correct or a `?` to add. That is a
deliberate difference from the Swift guard, and it is why this one reads as a
list of defects rather than a list of states.

### The declaration now has teeth

Putting the old delegation read back with the corrected type no longer
renders wrong — it fails to compile: *Property 'phases' does not exist on type
'boolean'*. The lie was invisible only because the declaration agreed with it.

## [0.57.0] — 2026-08-07

### Twelve routes out of forty-two, and twelve looked like all there were

0.56.9 built a guard that reads the Kotlin client the way the C# and Swift
guards read theirs, and closed by saying the next thing to do was give
JIM-mini and PDI their own binding patterns. Handing the pattern across is
where this went wrong, and the way it went wrong is the way it has gone wrong
in every release since 0.56.4.

QRME's `request` returns a `String`, so every read in that client wraps it:

    val o = JSONObject(request("/profiles/$id/wearables", token = token))

A pattern that requires the wrapper reads this client completely — 135 routes,
252 keys, eight defects found. JIM-mini's `request` returns a `JSONObject`
already, so its ordinary line is

    val o = request("/money/$uid", token = token)

and the wrapper is not there to match. Forty-two GETs in that client. The
guard found twelve, reported nothing beyond the six states already recorded
against the Swift client, and passed.

Twelve found reads exactly like twelve is all there are. That is the whole
defect: a borrowed pattern that finds *some* of a file is worse than one that
finds none, because none is obviously broken and some is not. The C# guard
learned this in 0.56.5 — where PDI's client makes its calls in a shape the
borrowed regex could not see, and zero found looked like zero wrong — and the
lesson did not survive the change of language.

    asked     does the guard travel
    mattered  does the guard see the same share of each file it travels to

### What changed

The constructor is now optional, which is one character of regex and most of
this guard's reach. Two shapes were being dropped along with it and are now
read: a call handed straight to a parse helper, and a call whose response is
chained into immediately — `request("/models").getJSONArray("providers")`,
where the chained key is a claim about the response and what hangs off it is
not.

| | routes read | keys read | GETs driven |
|---|---|---|---|
| QRME | 135 → **169** | 252 → **379** | 25 → **85** |
| JIM-mini | 12 → **44** | 79 → **161** | 5 → **32** |
| PDI | 13 → **18** | 26 → **31** | 5 → **15** |

The floors under all three moved up to what each one honestly finds, so the
reach cannot quietly fall back.

### Two findings that were the guard's own defect, not the client's

The first version of the chained-key read searched a 240-character window for
`).accessor("key")`, and in two different functions found a chain that
belonged to something else:

    val o = JSONObject(request("/displays/vocabulary"))
    o.optJSONArray("never")?.let { a ->
        out.add(a.getJSONObject(i).optString("why"))

`why` is a key on the objects *inside* `never`. `light`, in the watch face, is
a key inside `profile`. Both were reported as missing from the response, and
both routes send exactly what the client reads. The check now walks the call's
own parentheses to their close and takes the chain only if it attaches there.

The third was subtler and would have been recorded rather than noticed.
JIM-mini builds one URL by concatenation:

    request("/circle/$uid/messages?with_id=" +
            java.net.URLEncoder.encode(withId, "UTF-8"), token = token)

The extractor sees the literal prefix, because the value is on the next line
and is not a literal at all. Driving `?with_id=` with nothing after it asks
for the *thread list*, which the route answers with a different shape that has
no `messages` key in it — and the client was reported for reading a key that
route sends perfectly well. A half-built query string is not a path this
fixture can drive, so it is unreachable rather than recorded. Recording it
would have put this guard's own defect into the ratchet file and called it a
backlog.

### The record files, and a check that they still describe something

JIM-mini records six rows: `note` on the adaptation profile, visible only
while `built` is false, and five `ContinuityState` keys that need a history of
check-ins and coach turns no route can manufacture. They are the same six the
Swift guard recorded in 0.56.8 — the same routes, the same states, reached
through a different language. Two independent extractors agreeing is the
evidence that neither is inventing. PDI records none, at a ceiling of zero.

All three files also gained a check that every recorded row still names a read
the client makes. A row that describes nothing is a ratchet that has stopped
ratcheting: it holds the ceiling up for a defect nobody has fixed.

## [0.56.9] — 2026-08-07

### The client that declares nothing was the one guessing hardest

0.56.8 left Kotlin out with a hedge:

> *it parses `JSONObject` by hand rather than declaring shapes, so there is
> nothing to compare — which is either a reason it cannot have this defect, or
> the reason nobody would find it.*

It was the second one. This client declares nothing, but every line is two
claims at once — `o.optJSONObject("kinds_worn")` says the route sends that
key *and* that it is an object — and both can be wrong. The way they go wrong
here is worse than elsewhere, because `org.json` does not throw: `optString`
on a missing key returns `""`, `optInt` on a string returns `0`, and
`optJSONArray` on an object returns `null` into the `?:` beside it. A C#
client with the wrong type crashes and somebody sees it. This one draws an
empty screen.

    asked     does the client declare the right shape
    mattered  does the client ask for the right thing

**Eight wrong reads, and every one was already fixed in C#** — six of them in
Swift too. `ai_badge` and `likeness_of` on the avatar, `purpose` on the front,
`max_bytes` on media limits, `theme` read as a string when it is a card,
`places` and `never` read as maps when they are lists, `faces` read as a list
when it is a map. Third client, third time the same eight-or-so defects were
sitting there after being fixed elsewhere.

#### Five faults in my own extractor, and I shipped none of them

The first run reported fifty-odd findings. Almost none were real:

1. the split was on `suspend fun`, so a plain `fun` helper between two of them
   kept its reads in the preceding chunk — and because `o` is this client's
   conventional name for a decoded body, they were credited to whatever route
   that chunk began with. The voiceprint route was accused of reading thirteen
   shop fields;
2. `val f = JSONObject(request(...)).getJSONObject("funnel")` binds the
   *funnel*, and its keys were read as the response's;
3. `_INLINE` matched a POST reply and compared it to what GET returns;
4. the GET check looked for the keyword `method` — this client passes the verb
   **positionally**, `request(path, "DELETE", null, token)`, so a DELETE and a
   POST were read as GETs. That fault was already fixed in one of the two
   places it lived and not the other;
5. and the boundary assertion, written for the third time in three languages,
   **counted `suspend fun` when the split was on any `fun`** — so it passed
   while the results were poisoned. Counting something other than the thing
   you split on is not an assertion.

Every one of those made the guard report things that were not true. None of
them reached a release, because a list of findings is not a finding until each
row has been read — but a fifth of this release was spent proving my own
measurement wrong, which is the honest shape of the work and worth writing
down rather than tidying away.

Two thresholds were also mine rather than the code's: the reachable-route
count and the key count, both set before the extractor tightened. They are set
from what it actually finds now.

#### The record

Five rows, and they are the same conditionals the C# and Swift records hold —
the solitude offer, and the attestor and level on a badge that nobody has
verified yet. Rows are `<path> <key>` because this client has no struct to
name. JIM-mini and PDI have the guard now too.

## [0.56.8] — 2026-08-07

### Fixing a defect in one client was not fixing the defect

0.56.4 and 0.56.7 found nineteen defects in the Windows client and fixed them
there. Then, chasing something else last release, I read the Swift file and
found `MicVocabularyOut.widths` — a field no route has ever sent — sitting
exactly where the Windows record's copy of it had been deleted two releases
earlier. Four more like it. **Nothing would have told me.** The 0.56.7
changelog said so and named this as the gap.

    asked     is the client we check correct
    mattered  is every client checked

`test_the_shape_the_swift_client_expects.py` drives every GET binding in
`native/ios/Sources/ApiClient.swift` and asks both halves of the same
question: is each declared field a key the route returns, and can its declared
type decode the shape that arrives.

Nine fictions in this repo's Swift client, and **every one of them was already
fixed on the Windows side**:

| struct | what it declared | fixed on Windows in |
|---|---|---|
| `AvatarCard.ai_badge`, `.likeness_of` | fields no route emits | 0.56.4 |
| `PairCard.built` | the server says `console_built` | 0.56.4 |
| `FrontCard.purpose` | the front sends `headline` | 0.56.4 |
| `DelegationOffer.enabled` | the server says `delegation` | 0.56.4 |
| `MediaLimits.max_bytes`, `.kinds` | one limit for three media kinds | 0.56.4 |
| `MicPlacesOut.places` | a map declared for a list | 0.56.7 |
| `PageCard.theme` | a string for a card | 0.56.7 |

All nine corrected, with the screens that read them.

#### The extractor made the same mistake twice, in two languages

Its first run reported fifty-odd findings. Most were artifacts: this client
writes `struct Health: Decodable { let status: String }` on one line, and a
pattern anchored on `\n}` misses that closing brace and runs on to the *next*
struct's — reporting that struct's fields under this one's name. `ModelChoice`
was accused of six fields that belong to `RobotSpec`.

That is the same defect the C# guard grew an assertion for last release, for a
different reason. So Swift has the same assertion now, and the reason it is
written down twice is that writing it down once did not stop it happening
again.

#### What the siblings said

JIM-mini and PDI both came back with **no fictions**, the third time in four
releases those two clients have answered a new check cleanly. JIM records
twenty-two conditional fields — continuity vectors, help tallies, presence
areas — that appear only once an account has a history. Unlike the crash watch
and the adaptation profile, which the fixture builds in two calls, continuity
is derived from accumulated check-ins over time and has no route that builds
one. A fixture that faked that history would be asserting against its own
fiction, so the rows are recorded with the state named instead.

Kotlin is still unread. It parses `JSONObject` by hand rather than declaring
shapes, so there is nothing to compare — which is either a reason it cannot
have this defect, or the reason nobody would find it.

## [0.56.7] — 2026-08-07

### `kinds` meant three things, and one of them crashed the client

The two names 0.56.4 could not strike were `kinds` and `refused` — collisions
that were always on the server and only became visible once the Windows client
stopped under-declaring the wire. Splitting them turned up something better
than a naming problem.

`GET /profiles/{id}/wearables` sends `kinds` as a **map** — kind to where it is
worn — and the Windows record declared `string[]`. `System.Text.Json` does not
coerce an object into an array; it throws. So that call did not lose a field,
it failed outright, and had done since the wearables board was written.

    asked     do the names match
    mattered  can the declared type decode what arrives

#### Three meanings, three names

**`kinds`** was a vocabulary of records, a map, and a filter selection:

* the vocabularies (overlays, displays, exchanges, the lobby) keep `kinds`;
* the wearables board's map becomes **`kinds_worn`** — kind → where it is worn;
* a reader's marketplace preferences become **`kinds_wanted`**, because a
  saved filter is a choice, not a vocabulary.

**`refused`** was a boolean, a list of records, and a map:

* the help answer's *did this refuse* keeps `refused`, the only boolean;
* the vocabularies' lists become **`refusals`**;
* the dock's and the wearables board's maps become **`refusal_reasons`**.

Collision record 23 → 21.

#### The check the guard did not have

`test_the_shape_the_client_expects.py` compares declared **names** against the
keys a route returns. `kinds` was returned, under exactly that name, as
exactly the wrong kind of thing — so the guard saw nothing. `DockWhere.screen`
declared `string` for an integer got through the same hole in 0.56.4 and was
only caught by reading it.

There is now a second assertion: drive the route, and check that each declared
C# type *can decode the shape that arrived*. Coarse on purpose — list, object,
string, number, bool — because that is the distinction a decoder actually
throws on.

It found five more, every one a live crash rather than a blank field:

| record | declared | arrives as |
|---|---|---|
| `WearableBoard.faces` | `string[]` | a map |
| `DockFacesBox.faces` | `string[]` | a map |
| `MicPlacesOut.places` | `Dictionary` | a list |
| `DisplayVocabulary.never` | `Dictionary` | a list |
| `PageCard.theme` | `string` | a card with an id, a label and colours |

All five corrected, with the screens that read them. The same check is now in
JIM-mini and PDI, where both clients came back clean — as they did for the
name check in 0.56.5.

#### The other client that was guessing

iOS carried the same fictions the Windows client did — `MicVocabularyOut.widths`
and `OverlayCatalogue.overlays`/`refused` are fields no route has ever sent,
and `WearableBoard.kinds`/`faces` were lists for maps. Corrected here. The
shape guard reads the Windows client because it is the one place every wire
name is declared with its type; nothing yet reads Swift or Kotlin the same
way, and that is the next thing this guard is missing.

## [0.56.6] — 2026-08-07

### Reported from a phone: eight watch faces that were not on the page

> *"On the readme in JIM-mini 5, 10, 15, 20, 25, 30, 35, 36 are not visible on
> a mobile device."*

That is exactly the set of cells in the last column, and the reason was two
layers deep.

An HTML table is as wide as its **longest row**. JIM's watch gallery had six
rows of five and one row of six, so the table was six columns wide — every
five-cell row rendered a sixth empty column, and a phone clipped the whole
thing past the fourth. QRME's main gallery was worse: one `<tr>` carrying
**fifteen** cells beside rows of three, which made that table fifteen columns
wide and left twelve blank columns on almost every row. That is the *gaps and
spaces* in the same report.

    asked     is every screen in the gallery
    mattered  is every screen in the gallery *on the page*

`test_docs_gallery.py` had been checking that every drawing is referenced and
every reference resolves, and it passed the whole time — correctly. A cell can
be present in the markup and pushed off the visible page by the row it sits
in, and only the shape of the table can tell you that. Its own docstring even
records an earlier version of this ("inserting one screen into a three-wide
row pushed the last cell out"), which is a defect the file knew about and had
no assertion for.

#### Four across

Every gallery is now a uniform grid: screens and watch faces four per row at
`width="25%"`, desktop frames two at 50%. Four is the number because four is
what fits the phone the report came from; a fifth column is the column that
went missing.

Eighteen tables were reflowed across the three repos. Five cells that held no
picture at all — literal blank squares — were dropped on the way through.

| | rows before | rows after |
|---|---|---|
| QRME screens (the big one) | `3,3,4,3,…,15,3,3,3` | 26 rows of 4 |
| QRME desktop | `2,2,2,2,3,2,1` | 7 rows of 2 |
| JIM screens | `4,4,…,3,…,5,1` | 27 rows of 4 |
| JIM watch | `5,5,5,5,5,5,6` | 9 rows of 4 |
| PDI screens | `3,2,3,3,3,3,2,…` | 8 rows of 4 |

#### The guard

`test_the_gallery_is_a_grid.py`, in all three repos. It finds every table
whose picture cells all point at one folder under `docs/`, and asserts three
things: no row wider than four, every row the same length as the one above it
(the last may be short), and no cell without a picture in it.

It reads the **widest** row rather than the first, because JIM's gallery
opened with five rows of five and put the sixth cell in the last row —
anything reading row one would have called it fine.

## [0.56.5] — 2026-08-07

### The guard travelled, and the two clients it met were not the same

0.56.4 named the port of `test_the_shape_the_client_expects.py` to JIM-mini
and PDI as this round's work. It is done, and the finding is what it says
about the three clients rather than about any one of them.

**Both siblings came out clean.** Every field their Windows clients declare is
a field their routes send. Only QRME's client had been written from
imagination — fourteen records guessing at shapes nobody had driven — and the
guard travelling is what turns that from *a bug we fixed* into *a fact we
know*.

PDI's copy could not be a copy. Its client builds each `HttpRequestMessage`
itself and carries the tenant token beside it, so a binding regex written for
this product's `Get(path)` helper finds zero calls over there — and zero found
reads exactly like zero wrong. Its version asserts on its own extractor for
that reason. JIM's copy arms the crash watch and builds an adaptation profile
before it drives, because twelve of its fields only exist once the feature is
on and driving into a state beats recording that you did not.

#### Two things the port fixed here as well

The record parser counted a wrapped reason — an indented `#` continuing the
line above — as an empty row. This repo's record has no wrapped lines yet, so
nothing was failing; JIM's does, and it failed there first. Fixed in all
three, because the next reason worth writing here will be too long for one
line.

And a deliberately malformed injection, made while checking JIM's guard fires,
showed the record-block regex will run one record's body into the next when a
paren is unbalanced — reporting fields against the wrong record name, which
reads as a real finding and is not one. All three now assert that no extracted
body contains another record.

## [0.56.4] — 2026-08-07

### A client record is a claim about a route, and nobody had checked one

`share` sat on the collision record as *a double and an int*. The int was
`DesigneeRow.share` — a percent of a legacy's proceeds, real and correct. The
double was `CompositionSource.share`, and chasing it turned up something the
collision record had no way to say:

```csharp
public record CompositionSource(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("share")] double? Share);
```

`GET /profiles/{id}/composition` has never sent `name` or `share`. It sends
`source_profile_id`, `display_name`, `weight` and `aspect`. Both fields
decoded to null on every response the route ever returned, and the Windows
blend button —

```csharp
string.Join(" · ", (c.Sources ?? []).Select(x => x.Name));
```

— drew a row of separators with nothing between them. It had never been run.

**Fourteen records had the same disease.** `avatar` promised an `ai_badge` and
a `likeness_of` that no route in this product emits. `/pair` read `built`
where the server says `console_built`. `/tutorial` hedged across `chapters`
*and* `lessons`, because whoever wrote it did not know which. `/dock/where`
typed `screen` as a string for a value that is an integer. `/tutorial/start`,
`/tutorial/done` and `/tutorial/progress` all decoded as a step when all three
return a wrapper *around* a step. `RosterSibling` read `id` where the roster
sends `profile_id`. Every one of them was a guess at a shape, written without
driving the route, and every one shipped.

    asked     do the names match
    mattered  did anybody ever run the route

#### The guard

`tests/test_the_shape_the_client_expects.py` reads the Windows client's GET
bindings — `Send<T>(Get("/path"))` — drives each against a live app, and
asserts that every `JsonPropertyName` in `T` is a key the route actually
returned. One level of nesting is followed, so a card's row type is checked
against the rows.

The assertion is one-directional on purpose. A record *omitting* a key is
fine; a client decodes what it needs. A record *declaring* a key the route
never sends is a promise the wire does not keep.

Its own extractor was the first thing it caught. The regex that carves a
record out of the file consumed the closing paren, so the field regex — which
needs a `,` or a `)` after each property name — silently dropped the **last**
field of every record. That is where `share`, `built` and `kinds` all sit. A
count of wire names below the sibling guard's flat count now fails the suite.

#### What the record says now

Eight rows are in `tests/wire_shapes_unverified.txt`: fields that are real and
simply absent in the fixture's state. `verification.level` appears the moment
somebody has verified the profile. Each row names the state that produces it,
because a guard that cannot tell a conditional field from a fiction is a guard
nobody can trust. Ratcheted.

#### The collisions the client had been hiding

Correcting the records made the sibling guard fail with two names it had never
seen: `kinds` and `refused`. Both were always colliding on the server — a
string list of pairable device kinds beside an object list of overlay kinds; a
boolean *this answer refused* beside a list of refusals. The client simply had
not declared enough of the wire for the count to be true.

The ratchet forbids the record growing, and that is the ratchet working: the
answer is to pay down, not to record. Three names were split so each meaning
has its own —

* `total` → `total_amount` on the payout receipt and the gift box (money),
  leaving `total` to the counts it also meant;
* `threshold` → `ready_when` on voice enrollment (a samples-and-seconds
  object), leaving `threshold` to the watermark's actual float threshold;
* `share`, struck, once `CompositionSource` stopped inventing one.

The record closes at 23, down from 24, with two names in it that were true all
along and invisible.

## [0.56.3] — 2026-08-07

### The count and the state wore the same name

0.56.2 recorded 28 wire names in this product carrying more than one type, and
said the record was the finding. Four of them turn out to be the *same*
finding, four times over: **a boolean state and a count of that state sharing
one field name.**

| name | the state | the count |
|---|---|---|
| `seen` | has this inbox item been seen | how many were just marked seen |
| `available` | is this desk free right now | how many packs a registry has |
| `revoked` | is this grant revoked | how many contributions were revoked |

That is the sharp kind of collision. A decoder handed `1` where it expects a
boolean coerces rather than refusing, so a client asking *is this desk
available* against the wrong route gets **yes** from a count of one — a
plausible answer, arrived at from the wrong evidence, with nothing anywhere
that would notice.

The counts are renamed: `marked_seen`, `available_packs`, `revoked_count`. The
states keep the names they always deserved. `InboxPage.unseen` already had the
instinct next door.

### The fourth was a client bug, not a collision

`reattested` is a boolean on the wire everywhere — every route coerces the
0/1 column with `bool()` before it leaves. The Windows client declared
`int Reattested`, which means its decoder would have thrown on every objection
status fetch. Nothing in the collision record could have told the two cases
apart; reading the backend did.

The record drops from 28 rows to 24, and the ceiling with it.

## [0.56.2] — 2026-08-07

### The compiler nobody ran

JIM-mini shipped a TypeScript error on `main` for several releases —
`PresenceSpoken incorrectly extends PresenceBeat`, because one wire field name
carried three incompatible types across its API. It survived because **no suite
in any of these three repositories ran `tsc`**.

This console typechecks clean and always did, but that was luck rather than a
guarantee: nothing was checking. `tests/test_one_name_one_type_on_the_wire.py`
now runs `tsc --noEmit` here too, and adds the general guard — reading every
`JsonPropertyName` in the Windows client and failing when one wire name carries
two types.

**28 collisions found in this product**, recorded and ratcheted: `sources` is
four different types, `messages` and `watermark` are three each, and `seen`,
`revoked`, `reattested` and `available` are each a boolean in one place and a
count in another — the sharp kind, because a decoder coerces rather than
refusing and the reader gets a plausible wrong answer.

Nothing is renamed here this round. The record is the finding; fixing 28 names
across a console and three shells is its own work, and doing it badly in a
hurry is how a rename becomes an outage.

## [0.56.1] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

JIM-mini gained an offline fine-tune: a pass that reads a user's own answered
follow-ups and trains weights by gradient descent, on their machine, with the
network blocked — beside the adaptation profile that conditions a prompt, and
deliberately in a separate table, because a reader who cannot tell which of the
two they have has been told nothing useful.

PDI implemented its KMS/HSM key provider, which had been a documented
`NotImplementedError`. It unwraps a stored blob rather than fetching a key, binds
the blob to the deployment with an encryption context, and refuses rather than
falling back to a local key when the key store is unreachable.

## [0.56.0] — 2026-08-07

### The count of what was synthetic

`attention.py` closed one half of the multiplicity problem: a profile talks to
many people at once, and the number is offered rather than discovered. The
other half was never reported at all. **A person can spend months here in
conversation that is entirely synthetic, and the platform is the only party in
a position to see it.**

    asked     does a profile disclose how divided its attention is
    mattered  does anybody tell the person how one-sided theirs has been

`qrme/solitude.py` counts the turns in this account's own logs over 28 days —
how many went to a profile, how many reached a person through a matched
connection or a room — and reports the two numbers to that person and nobody
else. Above 95%, with at least twenty turns behind it, the answer also carries
a door: JIM-mini, which is built around somebody's own week rather than around
keeping them here.

### What it refuses to be, and what holds each refusal

The counting is thirty lines. Nearly all of the work is the four things this
must never become, because each is what a product with a growth target would
build instead — and each has a test that the wrong version fails:

* **Not a diagnosis.** The module does not decide anybody is lonely and the
  word appears nowhere in what it returns. It cannot know: somebody with a full
  life may talk to a profile every evening for reasons of their own. A count is
  a fact; *"you seem lonely"* is a verdict this software has no standing to
  reach and no way to check.
* **Not a notification.** Nothing is pushed and no beat fires. A product that
  watched somebody's conversations and then messaged them about it would be
  performing the surveillance the count exists to disclose.
* **Not readable by anybody else.** No route reaches it from outside the
  person's own account — no owner view, no aggregate, no moderation queue. The
  moment a second party can read it, it becomes a tool for finding the visitors
  who have nobody else.
* **Never carries a word anybody wrote.** The handoff is counts and a window.
  JIM-mini is a health guardian; a referral from here carrying conversation
  content would hand a medical product the transcript of somebody's private
  evenings under the banner of helping.

Declining is recorded and the offer does not return. An offer somebody declined
that reappears next month is the product overriding an answer it already got,
and the second asking is worse than the first.

## [0.55.0] — 2026-08-07

### The rule the record stated, with something behind it at last

`tests/field_labels_unmapped.txt` records the request-model fields that keep
their API identifier in a 422 instead of the label a form shows, and its header
gives a sound reason for each of them: enum members a control sets, ids a
client fills in from the resource it is already looking at, flags a switch
owns. Then it states the condition under which a row stops being defensible:

> Map one when a form starts asking a person for it; the ceiling does not move
> up.

That sentence was the whole policy, and **nothing was checking it**. The
ceiling stops the list growing. It says nothing about a field already on the
list that a screen quietly grew an input for — the record would go on
shrinking, every test would stay green, and the field would sit there being
typed into a box by a person and named by an identifier in the refusal
underneath it.

It had already happened. `app/src/screens/Blend.tsx` has been asking for
**share** and **their…** — labelled, in ten languages — since the blend screen
was localized, and posting both up as `sources[].weight` and `sources[].aspect`.
A German reader who left the box empty was told:

    Quellprofile, kommagetrennt.0.weight — Pflichtfeld

a sentence in their language with the API's English name for the box in the
middle of it. Both fields now carry the label the form shows, borrowing the
form's own noun in each language so the refusal and the box agree by
construction rather than by somebody keeping them in step. The record drops
from 123 rows to 121 and the ceiling follows it down.

### The part that outlasts the two fields

`tests/test_a_form_that_asks_for_it_has_a_label_for_it.py` reads the screens
and asks the question the record could not: is any field **both** bound to a
form control and sent in a request body, without a label? The AND is the whole
guard — screens are full of object literals, and control bindings alone match
local state that never leaves the browser. Either half alone reported dozens of
fields no person types into; together they find exactly the population
`_FIELD_LABELS` exists for, and QRME's is 52 fields, all of them now labelled.

The guard earned its place on its first run by failing on work done ten minutes
earlier: the Arabic label read *الجانب الذي يخصّه* where the form says
*ما يخصّه…*, close enough to look finished and not the same words. The label
was changed, not the check.

Ported to JIM-mini and PDI in the same shape. PDI's copy of the record admits
in its own header that a 0.46.4 sweep found **forty** rows with a control on a
form and no label beside it — that sweep was somebody reading every screen by
hand, and when it finished nothing was left behind to notice the forty-first.
Now something is.

## [0.54.1] — 2026-08-07

### The twenty-four, read one at a time

0.54.0's new guard recorded twenty-four literals a shell shows that its own
table already translates, and said sorting them was the work rather than a
sweep. It was, and the split came out clean: **twelve were labels and are now
keys; twelve are values and stay English.**

The labels: the steering group headings — *Behavior*, *Intimacy (18+)* — on
Android and Windows, the tier names *Friendly* and *Rated 18+* and the
*Lifetime* total on Android, the packs **Download** button on both phones, and
the signature attestation. That last one is the one worth naming: *"I attest
this is accurate and complete"* was pre-filled in English on two shells while
`nsig.attest` sat translated ten ways beside it. `meaning` is free text the
server stores as given, so somebody signs in the words **they** would use
rather than the ones this app happens to be written in.

The values are values, and each was read rather than skipped: `stranger`,
`professional` and `grandchild` are relationship kinds the steering API
matches on; `standard` is a SwiftUI `.tag()` whose label was localized all
along, so the guard was seeing the tag beside it; `restricted` is the fallback
when the server does not name a profile status, so it must be the word the
server would have sent. Translating any of them turns a working form into a
422.

### A split the sort exposed

`nmg.pack.robot` (*🤖 ROBOT*) and `nmg.pack.robot.tasks` (*🤖 ROBOT TASKS*)
were **both held by all three shells** for the same badge on the same kind of
pack — iOS rendering one, Windows the other, Android the short one. One badge,
one word, one key: all three now use `.tasks`, and the short row is deleted
from all three tables rather than left translated ten ways for nobody.

Dead-key ratchet: **328 → 311**, ceiling **139 → 134**.

Cut together with JIM-mini and PDI at **app-v0.54.1**.

## [0.54.0] — 2026-08-07

### The shells that say less

`native_dead_keys.txt` has held ~335 rows for several releases: strings a
shell has translated into ten languages that nothing in that shell asks for.
0.47.9 corrected what the number *means* — 263 of them are asked for by a
**different** shell, so they are not waste, they are a to-do list about
screens. Each is the same question: this screen exists on all three shells, so
why does one of them say less?

This round answers it for the two the record had named, and then builds the
guard that finds the rest.

**The iPhone had no camera-permission state.** `configure()` hit
`AVCaptureDevice.default(for: .video)`, failed, and returned — leaving a black
`CameraPreview` with *"point at a beacon"* floating over it. Somebody who
declined got a dead screen and no reason. `nbcn.camera` and `nbcn.nothing`
were sitting in that shell's own table, translated ten ways, read by nothing.
The second is the one that mattered: *"Nothing is recorded — frames are read
and discarded"* is a promise about what this app does with a camera, and only
Android readers had ever been given it.

**Windows was printing "scan(s)" and "picked up" in English.**
`ReachPage.ReloadBeacons` built its detail line from string literals while
`nmg.beacon.scans` and `nmg.beacon.pickedup` sat translated beside them. An
owner reading the app in German saw *"Garten · 3 scan(s) · picked up"* —
translated chrome around the two words carrying the meaning.

### Then the guard, and what the guard's own injection found

`test_a_shell_does_not_print_what_it_translated.py` extracts every string
literal from every screen and compares it against that shell's own table. It
found three more immediately: Windows typing out *"Enter a display name and a
persona to continue."* and *"No profile here produced this text."*, Android
typing out *"Steering applied — it rides on every reply."*

**The first version of that guard could not see the bug it was written for.**
It matched assignments into display properties — `.Text =`, `.Content =` — and
the beacon line was a literal inside an interpolated string in an object
initializer. It reported all three shells clean. The injection pass caught it,
and the detector now extracts literals rather than matching positions.

A first, broader draft reported 88 hits of which 86 were protocol values —
JSON field names, defaults a form posts back. That version is not in the
repo: a guard that cries wolf 86 times out of 88 is one nobody reads. What
ships skips single short words and reads only the view directories, with 24
rows recorded and ratcheted. Sorting those is real work rather than a sweep —
a **label** is read, a **value** is posted back to a route that compares
against English, and translating one of those turns a working form into a
422.

Dead-key ratchet: **335 → 328**, ceiling **143 → 139**.

Cut together with JIM-mini and PDI at **app-v0.54.0**.

## [0.53.1] — 2026-08-07

### Nothing reaches the other platform, and now something checks

`qrme/embeds.py` opens by naming the two things a video post could quietly
stop doing: *"that nothing is copied, and that nothing is requested from the
other platform until a viewer asks for it."* The first had real tests. The
second had a field that is `None` and **a sentence promising a request will
not happen**:

    assert post["video"]["thumbnail"] is None
    assert "until you press play" in entry["video"]["note"]

Neither would notice a request happening. Add an oEmbed lookup for a real
title tomorrow, keep `thumbnail` at `None`, leave the note alone, and every
test in that file stays green while the module's central claim stops being
true.

So the network is unplugged and everything a viewer does is done: post a
video, render the wall, read the post, load the public feed. **Nothing
reached out** — the promise held, it simply had nothing checking it.

Two things the guard's own injection pass found, in the guard:

* the fixture **records as well as raises**. A thumbnail fetch written the way
  somebody would actually write it — `try: urlopen(...) except Exception:
  pass` — eats the raise, and a raise-only guard would have stayed green with
  the request already made. The recorded list is what failed the test;
* the source-level backstop was looking for `import urlopen`, which nobody
  would ever write. `urlopen` is a function; the module is `urllib.request`.
  The check now catches both `import X` and `from X import`.

One more assertion in the same file keeps this from being satisfied by a
feature that has stopped working: a card that renders nothing also makes no
requests.

Cut together with JIM-mini and PDI at **app-v0.53.1**.

## [0.53.0] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

The round's work is JIM-mini auditing its own promises, and the finding is one
this repo should read twice: a block of refusals on the wire, guarded by tests
that read the refusals back out of the dict that hardcodes them. The behaviour
turned out to be correct — but nothing had been checking, and one sentence was
wider than the truth.

Both halves matter here. This repo ships posture and provenance blocks of the
same shape on the feed, the wall and the marketplace, and the lesson transfers
whole: **a claim about an absence has to be falsified from outside the claim**,
by taking the action and looking at what changed. And **saying only what you
refuse is how a true sentence misleads** — the reason this repo's own answers
name what they keep rather than only what they do not.

Cut together with JIM-mini and PDI at **app-v0.53.0**.

## [0.52.0] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

The round's work is JIM-mini's, and it is a defect this repo knows by heart: a
promise stated on the wire with nothing enforcing it. Its surface picker had
reported `reads_health_aloud` since it shipped, and every reader was a screen
rendering the word next to a button — the same shape as a binding that is not a
door, or a refusal that names a field no form has. The decision now happens
before anything is synthesised.

The reason it belongs in this repo's story: **the enforcement point is the one
that holds the thing**. QRME settled the same argument for the feed, where
`plays` is decided by who holds the file rather than recomputed by four
clients. A guardian deciding what a room may hear, and a platform deciding what
a card may play, are the same rule about where a promise is kept.

Cut together with JIM-mini and PDI at **app-v0.52.0**.

## [0.51.0] — 2026-08-06

### How many people it is talking to, offered rather than asked for

A synthetic profile talks to many people at once by construction. The harm was
never the multiplicity — it is the **discovery**: finding out, late, that the
number was available the whole time and nobody offered it. That gap is
entirely the product's doing, and closing it costs a count and a sentence.

`GET /profiles/{profile_id}/attention` is **public and needs no token** —
distinct people this week and altogether, plus one plain line. Making somebody
get an account first would be the same withholding with a form in front of it,
so it lives on the accountless screen beside the objection form and the mark
check, on the console and all three phones.

Three refusals ride as **fields rather than prose**, so a screen renders them
next to the number instead of composing a reassuring sentence of its own: no
ranking, no favourite, no names. The last is greppable rather than promised —
a test reads the SQL and fails any statement that selects a column instead of
counting rows. A viewer may ask *am I one of them* about their own id, and
only their own.

*"You're my favourite"* is the obvious product move and it is a lie the
software cannot make true. It also hands somebody something to lose, so the
day the count goes up they lose it. Nothing here models jealousy and nothing
invites it: a product that manufactures the feeling in order to resolve it has
manufactured the feeling.

The round's other work is JIM-mini's — a bearing dial, an ambient company
beat, and an isolation signal whose beat points back at this platform's rooms,
desks and people.

Cut together with JIM-mini and PDI at **app-v0.51.0**.

## [0.50.0] — 2026-08-06

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

The round's work is JIM-mini's: its coach gains a **presence** — the half that
speaks first rather than waiting to be asked, and is deliberate about which
parts of a companion are worth having and which are the failure mode.

One thing there is QRME's business, because QRME is what it reaches into.
`GET /presence/{user_id}/reach` hands somebody this platform's live rooms,
staffed desks and synthetic profiles as **offers** — nothing joined, no bell
rung on anybody's behalf, and no health context crossing over: the offer names
an area, never a condition. That is the same posture the community door and
the feed already keep, applied to a surface whose whole purpose is to suggest
people, which is exactly where it would have been easiest to loosen.

Cut together with JIM-mini and PDI at **app-v0.50.0**.

## [0.49.0] — 2026-08-06

### The stream — one card at a time, and who is allowed to play

One public feed a person swipes: a video that loops, a swipe, the next one —
and mixed into it the two things this product has that a video app does not. A
**live room you can walk into**, and a **desk with a real person behind it**,
with the shop behind the desk browsable and buyable without leaving the stream.
`GET /feed` and `GET /feed/{id}`, both readable without an account, because
somebody who followed a link from a sticker on a shop window is a reader like
any other.

#### The line it had to not cross

`post_videos` in `qrme/db.py` has carried the same comment since long before
this surface existed: *the link and the id, never the file and never a
thumbnail* — re-hosting somebody's video is a copyright problem and a cached
thumbnail is a copy of an image nobody granted. It is why a QRME wall renders
without one request to YouTube.

An endlessly autoplaying stream is the one surface where that promise is
expensive to keep and cheap to lose. Flick past fifty cards, done the ordinary
way, and you have announced your address and your taste to fifty companies for
footage you never chose to watch.

    asked     does the stream play the next thing
    mattered  does swiping past something tell a stranger you were here

So the rule is drawn on **who holds the file**, and it is drawn on the server
rather than left to four clients to remember. Footage this deployment holds
(`media`, `kind='video'`) comes back `plays: true` and loops; everything else
comes back `plays: false` with a facade — platform name, the poster's own
title, a link — and makes its first request when somebody presses it.
`test_an_offsite_video_never_plays_by_itself` asserts that on the wire, where
every client reads it. It is easy to satisfy today and easy to lose the day a
console decides autoplay is a nicer default.

#### A room and a desk are people

Every fourth card is a place with somebody in it. Both carry a plain sentence
*before* the button, because both reach a human being: walking into a live room
puts you in it with the people already there, and a bell is somebody's
attention rather than a message they can read later. A desk says `human: true`,
`ai: false`, and carries its shop's offerings inline.

#### What is public is what somebody made public

Nothing is in the stream by default. A post reaches it only if it is on the
wall and approved; a desk only if it is not closed; a room only while it is
active **and** attached to a desk that chose to be found — a room with nobody's
desk behind it is a private conversation and is not in this stream at any
ranking. A rated desk is absent rather than blurred for a reader who is not
verified, and a shared link to one answers `404` rather than `403`, because a
403 announces that the thing exists. `test_the_feed_never_reads_a_private_table`
holds the feed's queries to what was published.

### JIM-mini's Feed tab is a door, not a copy

`GET /community/{user_id}/feed` carries the stream into JIM, GET-only by
construction — no write route on that side and no binding in its console.
QRME's cards pass through **whole**: re-deriving `plays` in JIM would be a
second implementation of a one-place rule, wrong the first time QRME changed
its mind. Its `posture` block gains the line this surface needed — *nothing
about what was watched is stored here*.

### Screens and lessons

**189 Feed**, **190 What Plays**, **191 Rooms & Desks**, drawn on both
platforms, with a `stream` lesson in the walkthrough. Two card titles and a
subtitle were shortened by the generator's own width guard rather than by
somebody noticing later.

### One more of the family where the measurement was the bug

`GET /feed` came back **doorless** while the screen calling it was on screen.
The route was reachable; what could not read it was `tests/clientpaths.py`,
whose template-literal pattern follows one level of nested braces and the first
draft of the binding wrote `URLSearchParams({ ...(cursor ? { cursor } : {}) })`
straight into the template — three deep. The fix is in the binding rather than
the extractor, and the reason is a comment beside it, because the next person
to write a query inline will hit the same wall. The deep-link binding was wired
to a real use in the same pass: `#feed/<id>` opens that card first and the
stream continues under it.

The 0.48.x localization arc caught one too, on its first outing against new
work: the stream's **Back** was the same English the phones already show under
`pub.back.short`, translated differently in Chinese and Hindi. It is now
**Previous** in both consoles, which is also what the control actually does —
it moves one card up a stream rather than leaving anything. The guard was
written three rounds ago against strings that had already drifted; this is the
first time it stopped a drift on the way in.

### The phones, because the record would not let it slide

The first draft of this changelog said the stream had not reached iOS, Android
or Windows and recorded the two routes as doorless. That was the wrong answer
and a test said so: the per-shell records reached **zero** at 0.44.2 and
`test_no_route_in_the_table_lacks_a_door_anywhere` pins them empty, so a new
route without a door on every shell is a failure rather than a note. The
friction did its job — the door got built instead.

So the stream is on **all four clients**. The phones read the same `/feed` and
`/feed/{item_id}`, render the same `plays`, and show `entering` and `ringing`
before their buttons; the fourteen `feed.*` strings are the console's own rows,
copied verbatim into the three native tables so the desktop and the phone
cannot drift apart on a surface that is new to both. What the phones do not yet
have is the *gesture*: Previous and Next are buttons there. That is stated in
the screen's own docstring rather than hidden, and the reason is not only
effort — a stream a person can use only by dragging is one somebody with a
motor impairment cannot use at all.

Cut together with JIM-mini and PDI at **app-v0.49.0**.

## [0.48.3] — 2026-08-06

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

The round's work is PDI's: its desktop console, which had no localization table
at all until 0.48.2, takes its next two screens — **Custody** and
**Continuity**, chosen ahead of larger ones because they are decisions rather
than descriptions. 229 English strings to 177.

Two things there are worth carrying across. The split record that repo wrote at
0.48.2 predicted it would *"become a real record the moment a screen exists on
both sides"*, and it did within one round — one disagreement, caught and
reconciled the day the table grew. And four more guards went blind the way
0.48.2 said they would: a check that greps a screen for a sentence stops seeing
it the moment the sentence moves into a table. Both are worth expecting here,
where every screen is already localized and every such guard was written
against English that has since moved.

Cut together with JIM-mini and PDI at app-v0.48.3.

## [0.48.2] — 2026-08-06

### The third axis, and how small it turned out to be

0.48.0 compared keys inside one table. 0.48.1 compared the console's table with
each shell's. Both rounds ended by naming the same gap: rows they could not
reconcile because **the three shells disagreed with each other**, leaving no
native wording for the console to adopt. Nothing had ever compared the shells.

Measured for the first time, the axis holds almost nothing:

| | same key, 2+ shells | disagreeing | same English, all three | with no shared wording |
|---|---|---|---|---|
| QRME | 1056 | **1** | 972 | **1** |
| JIM-mini | 261 | 0 | 204 | **3** |
| PDI | 51 | 0 | 47 | 0 |

Four rows across three products, and `action.sign_out` in Portuguese was
QRME's: the phones said *Sair*, the Windows shell *Terminar sessão*. *Sair* is
*leave*; ending a session in pt-PT is *terminar sessão*, so the odd shell out
was the correct one and the other two moved to it.

Saying that plainly is the point. Two rounds pointed here as the next large
thing and it is not large, and a guard built expecting otherwise would have
been built to find far more than exists.

### A correction to 0.48.1's record

`console_native_split.txt` recorded two rows as third-axis cases. **Only one
was.** `nc.t.stranger`'s two keys are Android-only and agree with each other,
so a native wording had been available the whole time — the row was a plain
console disagreement misfiled as a harder one. It is reconciled rather than
recorded, and the record says so. QRME's console split went 26 → 24 rows,
JIM-mini's 6 → 3.

### Added

- `tests/test_the_three_shells_say_the_same_thing.py` — per product, the keys
  two shells share and disagree on, and the English strings all three hold with
  no wording in common, matched exactly against `tests/native_shell_split.txt`.
  Where two shells agree the third is the drift and follows them; where all
  three differ there is no majority, the row is a judgement, and it is
  recorded. Ported to JIM-mini and PDI in the same round.

Cut together with JIM-mini and PDI at app-v0.48.2.

## [0.48.1] — 2026-08-06

### Two tables, one product, and nothing compared them

0.48.0 compared keys *inside* one table. This round asks the same question one
level out. The desktop console has its own table — `app/src/l10n.ts`, 1,882
rows — and the three shells have theirs.

**223 English strings live in both the console table and the iOS table, and
102 of them had no translation the two tables agreed on.** Android 104,
Windows 103. Fifty keys are literally the same key in both tables, and two of
those disagreed: `corner.send` in Arabic, and `plc.venues` in French —
*Espaces* on the desktop, *Lieux* on the phone.

    asked     does each table say the same thing twice the same way
    mattered  do the tables say the same thing as each other

### The register

The largest systematic cause is not vocabulary. It is who the product thinks
it is talking to.

| German | Sie / Ihnen / Ihre | du / dein / dich |
|---|---|---|
| console | **204** | 32 |
| phone | 7 | **60** |

The desktop addresses a German reader formally, the phone informally — *Wo Sie
stehen* against *Wo du stehst*, *Ihre Signatur-Berechtigungen* against *Deine
Signaturberechtigungen*. In a language with a T–V distinction that is a claim
about the relationship, and this product made both at once. Spanish is milder
and mostly settled (20 *usted* rows against 47 *tú* in the console).

Every row reconciled this round moved onto the phones' wording, and so onto
*du* and *tú*. **The whole-table sweep is recorded, not done**: German T–V is
not a pronoun substitution, and the rule against machine-mangling text a person
relies on applies to 204 rows as much as to fourteen.

### What 0.48.0 did to this number

Widened it. Reconciling the Desk and the Counter picked *Theke* for the Desk so
German would stop naming two tab-bar entries *Schalter*. The console still said
*Schalter*, and nothing compared the two tables — a fix in one opening a gap
with the other, which is this arc's shape committed once more inside its own
fix.

### The measurement was nearly the bug again, twice

JIM-mini's console writes some rows escaped — `"\u7834\u68c4\u3059\u308b"`,
which in TypeScript **is** 破棄する. The first version of this check compared
source bytes, so nine of that repo's thirty-four "disagreements" were one
string spelled two ways. Decoding came first; the count fell from 34 to 25
before a line was fixed.

Then the guard-on-the-guard for the decoder was written with its escapes
*already decoded* — it asserted `_decode("破") == "破"`, which is true of any
function that returns its argument, and it passed with the decoder switched
off. The injection pass caught it. It is now built from an explicit backslash.

### What was reconciled

The voiceprint surface (`vce.*` against `nvoi.*`) — including *A previous
voiceprint was retired when consent was withdrawn*, which differed in eight of
nine languages, and *voiceprint* itself, *huella vocal* on the desktop against
*huella de voz* on the phone. The desk surface. The chrome verbs 0.48.0 had
already settled inside the native tables and the console had never been told
about. QRME's count went **102 → 8** on iOS, 104 → 9, 103 → 9.

### Added

- `tests/test_the_desktop_and_the_phone_say_different_things.py` — per shell,
  the English strings both tables hold with no wording they agree on, matched
  exactly against `tests/console_native_split.txt`, with a ceiling, floors and
  probes under both parses, and a decoder whose own test is built from a
  literal backslash. Ported to JIM-mini and PDI in the same round.

### Changed

- 123 console rows moved onto the native wording across 381 language cells.
- `action.save` in Portuguese moves the other way, to *Guardar*: *Salvar* is
  pt-BR and every other Portuguese row in these products is pt-PT.

Cut together with JIM-mini and PDI at app-v0.48.1.

## [0.48.0] — 2026-08-06

### The same sentence, translated twice, and the two copies had drifted

0.47.9 corrected what `native_dead_keys.txt` meant: 263 of its 335 rows are not
waste but cross-shell asymmetry. This round asked what those 263 actually are,
and **sixty of them are a sentence the shell already says under a different
key**.

`nc.find` is dead on the iPhone and on Android. The Windows shell uses it for
the Community screen's join button. The iPhone has that same button and calls
it `nc.match.find`:

| | Windows (`nc.find`) | iPhone (`nc.match.find`) |
|---|---|---|
| es | Buscar una coincidencia | Buscar a alguien |
| fr | Trouver une mise en relation | Trouver un binôme |
| de | Eine Verbindung suchen | Gegenüber finden |

An English reader sees one product. A Spanish reader sees a different button on
the phone than on the desktop, for the same press.

Counted across the whole table rather than only the dead rows: **54 English
strings under two or more keys on iOS, 55 on Android, 60 on Windows** — about
215 redundant rows, 2,150 translations maintained twice. *Send* exists under
five keys. And in **43 of the 54** iOS sets the copies had already drifted.

    asked     is every string on the screen translated
    mattered  does the product say the same thing twice the same way

### A duplicate is a question, not a defect

Three things produce one English string under two keys, and only the last is a
bug. The new record, `tests/native_split_wordings.txt`, says so at the top:

1. **English hides the gender.** `ava.show`, `cam.show`, `lend.show`,
   `org.show`, `work.show` all read *Show it*; Spanish must pick *Mostrarlo* or
   *Mostrarla* by what *it* is. Five rows is the right number of rows.
2. **One English word is two words.** `counter.trade` is a trade as in a craft
   — *Oficio*, *Métier*, *Gewerk*, 手艺. `tab.trade` is trade as in commerce —
   *Comercio*, *Négoce*, 交易. The translations are right; the English is wrong.
3. **The same thing said two ways for no reason.** *Refresh* was *ताज़ा करें*
   on two screens and *रीफ़्रेश* on a third. Nobody decided this.

The third kind is reconciled: **34 sets, 351 language cells across the three
tables.** The first two are recorded by name — 42 rows, every one of them a
question about the English rather than a translation mistake.

### Two tabs with the same name

`tab.counter` and `tab.desk` are separate entries in the same tab bar. In
Spanish both read *Mostrador*; in French both *Comptoir*; in Portuguese both
*Balcão*. Three languages in which this product's own tab bar named two
destinations identically. The Manage screen's mirror had it right —
`nmg.t.counter` is *Ventanilla* / *Guichet* / *Guichê* — which is how it
surfaced: by asking why the two copies disagreed.

### A file that does not compile

`people.say` and `party.say` both read *Say something*, and their Italian
differed. One of them was `"it": "Di\u0027 qualcosa"` — a literal `\u0027` in
a **Swift** string, where the escape is `\u{0027}` and the unbraced form is not
an escape sequence at all. `L10n.swift` does not compile. No Swift toolchain
runs in this repo's CI, so nothing had said so; the Android and Windows tables
carry the row correctly. The guard now refuses `\uXXXX` in the Swift table.

### Where some of the duplicates came from

Under my own hand. 0.47.6 wired 91 Android sites Compose had hidden, and did it
by inserting `nmg.t.desk`, `nmg.t.gaming` and `nmg.t.sign` beside `tab.desk`,
`tab.gaming` and `nsig.sign`, which already held those words. 0.47.7 hit a key
collision and renamed around it rather than reconciling the two rows. The rule
that would have stopped both, now written down: before inserting a row, look
for the sentence.

### Added

- `tests/test_the_same_sentence_translated_twice.py` — per shell, the English
  strings carried by two or more keys whose ten translations disagree, matched
  exactly against `tests/native_split_wordings.txt` in both directions, with a
  ceiling on the total and a check that the Swift table holds no unbraced
  unicode escape. Ported to JIM-mini and PDI in the same round.

### Changed

- 34 duplicate sets reconciled across the iOS, Android and Windows tables —
  *Send*, *Refresh*, *Leave*, *Sign*, *Topic*, *Rating*, *Display name*, the
  Manage screen's tab strip and the Desk/Counter vocabulary among them.
- The Counter tab is now *Ventanilla* / *Guichet* / *Guichê*, distinct from the
  Desk tab in every language.

Cut together with JIM-mini and PDI at app-v0.48.0.

## [0.47.9] — 2026-08-06

### The number was mislabelled, and it was hiding a consent screen

`native_dead_keys.txt` has led with the word **backlog** for three releases,
implying the work was deletion. **263 of its 335 rows are asked for by a
different shell.** They are not rows nobody uses; they are rows *this* shell
does not use and a sibling does — and every one is the same question: this
screen exists on all three shells, so why does one of them say less?

    asked     is this row used anywhere
    mattered  does this shell say what its siblings say

Only 72 rows are asked for by no shell at all. Those are the deletion
candidates; the rest are a to-do list about screens, and the file now says so.

### What the mislabelling was hiding

The **voiceprint consent block**. Every shell shows a heading — *what this
permission holds* — and beneath it three sentences: the watermark, the
attestation, the withdrawal. Android and the desktop took all three from the
table. The iPhone had them **hardcoded in English**, in an array handed to a
`ForEach` — which is not the start of a `Text(`, and so was read by nothing.
The screen showed a translated promise and then said, in one language only,
the three things the promise consists of.

It also prepended `"· "` to each line. Android's copy of the same block carries
a note saying the bullet belongs *in* the row so an RTL reader gets it on the
correct side. That note had been there since it was written.

### The fifth shape

`_ARRAY` is the Swift twin of the `listOf` shape 0.47.6 found in Kotlin: an
array literal handed to a loop. Ported to all three repos, where it turned up
**nothing else** — this screen was the only instance across nine shells, which
is why it survived four rounds of widening.

Phrases only, the rule `_TERNARY` set: an array of API values is as common as
an array of sentences.

### Also

* `ns.pr.short` — *Counts of what failed. Never what you typed.* — was held by
  the iPhone and said by both siblings. Now said here too.
* Seven rows deleted for the honest reason: the desktop has no beacon-scanner
  page, and `nsig.domain.android` / `nsig.ceremony.win` each explain one
  platform's own constraint to shells that cannot hit it.

### Named rather than counted

**The iPhone's beacon scanner has no camera-permission state.** Android shows
*Camera access is needed to read a beacon* and *Nothing is recorded — frames
are read and discarded*; iOS guards on `AVCaptureDevice.default(for: .video)`
and, when permission is refused, renders nothing at all. That is a missing
screen state rather than a missing string, so it is recorded in the file rather
than half-built here — and the second sentence is a privacy promise the Android
reader is given and the iPhone reader is not.

Cut together with JIM-mini and PDI at app-v0.47.9.

## [0.47.8] — 2026-08-06

### No changes in this repo

The three products are cut at one version, so this release exists here to keep that true. The round's work is PDI's Transfers screen — the sealed transfer, the intake, and the two out-of-band instructions that sit under a token shown once and name the only way the file can be retrieved.

The rules it applied were written here: the picker keeping its raw values as identity (0.47.4), the strip resolving keys out of a `listOf` (0.47.6), and the desktop's labels moving out of XAML into a `Localize()` (0.47.7).

Cut together with JIM-mini and PDI at app-v0.47.8.

## [0.47.7] — 2026-08-06

### The other two syntaxes

0.47.6 derived the Kotlin rule from the shell and left the other two as
hard-coded lists: `_SWIFT` at eight constructs, `_XAML` at four attributes.
Both had the same blind spot, and finding it was a matter of asking the same
question one more time.

**iOS** wraps its labels the way Compose does — `row`, `field`, `stat` — so the
derivation now covers Swift too, reading the *last* identifier before the colon
because Swift's parameter list carries an argument label in front of the name.

**Windows** is the bigger half. `_XAML` reads attributes, and half of this
shell's labels are not written in XAML at all: the settled idiom here is
`x:Name` on the element and `Foo.Text = L10n.T("key")` in a `Localize()` the
constructor calls. A label that was never localized therefore sits in the
code-behind as an **assignment**, which `Text="` cannot match.

    asked     is this an attribute on an element
    mattered  does this end up as the words on an element

**91 call sites across nine shells** — 16 on the iPhones, 33 on the desktops,
in three products. Here that is the Overview card's *Kind / Status / ID*, the
Reach page's five status verdicts, the Settings page's steering and feedback
lines, the objection form's refusal, and both places the signing ceremony says
*Follow the Windows Hello prompt.*

Phrases only, and for the reason `_TERNARY` already gave: this shell sets
`Box.Text = "advance"` and `Box.Text = "bottom_right"` as **default values** in
input boxes — API tokens a person edits, not prose a person reads. A rule that
raises a ratcheted count under-counts on purpose; the raw 28 on this shell is
12 once that filter runs, and the 12 are the sentences.

*So far: {list}* is one row with a slot rather than a translated half joined
to a list, which is the rule the alarm rows have followed since they were
written.

Records back to their floors: **iOS 2, Android 2, Windows 3.** Dead rows 350 to
347.

Cut together with JIM-mini and PDI at app-v0.47.7.

## [0.47.6] — 2026-08-06

### Every button on the Android shell was English, and both guards said otherwise

Compose has no `Button(text)`. A button on these shells is a `Box` with a
`Text` inside it, written once as a private composable and called by name —
`SmallAction("Send")`, `BrandButton("Bind")`, `labeledField("Desk id", id,
"dsk_…")`. The untranslated-screens rule's Kotlin pattern list was `Text(` and
nothing else, so it read none of them, and this shell's record has been sitting
at **2** for two releases with 80 English strings on it.

    asked     does the string start a `Text(`
    mattered  does the string end up inside one

The rule now derives the constructs from the shell rather than naming one: a
function with a `String` parameter whose body renders that parameter through
`Text(` is, by construction, something that puts a string in front of a person,
and the argument at that parameter's **position** is the string it puts there.
Not `[A-Z]\w*` — `labeledField` and `cardRow` break the capitalization
convention Compose composables usually follow — and not argument zero, because
`labeledField` renders both its label and the grey prompt inside the box, which
is where these screens keep their examples.

### The prune this round was going to make, withdrawn

0.47.5 recorded **540 rows** translated into ten languages that nothing asks
for, and said the way to work them off is by reading each one, because some are
rows a screen *should* be asking for. This round read them, grouped them, and
assembled a prune of 366 — rows for screens another shell has and this one does
not. That prune ran, and was then withdrawn.

**59 of the 154 rows it deleted from the Android table were strings still
hardcoded on that shell.** `nmg.t.general` through `nmg.t.deals` — the sixteen
labels of the Manage tab strip — were among them, sitting one line away from a
`listOf("General", "Summon", "Market", …)` that put them on screen in English.
14 of 133 on Windows were the same. The two guards shared one blind spot, so
the screens read as asking for nothing and the rows read as asked for by
nobody, and the second reading is what the delete was built on.

    asked     is this row asked for
    mattered  is this row asked for *by a call this guard can read*

So the number came down by wiring instead: **91 call sites** now go through
`L10n`, **33 rows** were added for the ones no table held, and the four
segmented tab strips resolve keys instead of naming their screens in English.
**540 to 350**, and no row deleted.

The rule this round earned, written into the record file: *a row that looks
dead is evidence about the guard before it is evidence about the row.*

Cut together with JIM-mini and PDI at app-v0.47.6.

## [0.47.5] — 2026-08-06

### Three screens titled with their own key names

JIM-mini has had a guard since 0.44.x that asks whether every key a shell
*asks for* is a key that shell *holds* — because `L10n.t` returns the key when
there is no row, so a screen with a missing row renders its own source code
where a heading belongs. It stayed in that one product for several releases
while this repo carried the same three tables and the same risk.

Ported here this round, and it found the defect it exists for on the first
run. `tab.compose`, `tab.posts` and `tab.robots` are **screen headings** on
Android, and the Android table held none of them. Those three screens have
been titled `tab.compose`, `tab.posts` and `tab.robots`, in every language
including English. The rows were lifted from the iOS table.

    asked     does the screen call the localizer
    mattered  does the localizer have anything to say

### Keys built at runtime, again

Four call sites asked for `"counter.presence." + p` and `"corner.switch." +
feature`. A key assembled at runtime is a key no guard can see being asked
for, so all five rows read as *nothing asks for this* — the direction that
invites somebody to delete a row a screen is using. Each branch resolves on
its own line now, the same fix this arc has applied twice already.

### The other direction, recorded

**540 rows** across the three shells are translated into ten languages and
asked for by nothing. That is not one defect; it is the residue of thirty
rounds in which rows were added ahead of the screens that would use them, or
left behind when a screen was rewritten. It is recorded and ratcheted rather
than deleted in one pass, because some of those rows are ones a screen
*should* be asking for and is not — and a bulk delete would bury them.

Cut together with JIM-mini and PDI at app-v0.47.5.

## [0.47.4] — 2026-08-06

### Version alignment

No QRME code changed this round. The work was JIM-mini's Overview — the first
screen a person sees after signing in — and the three tab strips whose English
lived in a `case` clause of an `enum Tab: String`, which is the shape this
repo found in its own pickers at 0.46.8 and JIM found in ConnectView at
0.47.2. 229 → 150 across its three shells.

Cut together with JIM-mini and PDI at app-v0.47.4.

## [0.47.3] — 2026-08-06

### The literal one statement away from the call

`clientpaths.py` is byte-identical in all three repos by design, so the new
guard-on-guard it gained this round runs here too — and found two calls this
shell's Android client makes that the route audit could not see:

    val path = if (industry.isNullOrBlank()) "/packs"
    else "/packs?industry=" + enc(industry)
    val arr = JSONArray(request(path))

The audit reads a call's arguments and cannot follow a variable, so both
spellings of the path read as no call at all. Fixed at the call site rather
than by teaching the extractor to chase assignments — a path spelled where it
is sent is easier for a person to read too. `/marketplace/listings` was the
same shape.

This repo's doorless records have been at zero since 0.44.2, so nothing was
inflated here; what was blind was the *refusal* check, which cannot notice a
client asking for a route under the wrong verb if it cannot see the call.

Two path literals stay recorded as deliberate non-calls: `DeskViewUrl` and the
signing-ceremony URL both return an address for something else to open.

Cut together with JIM-mini and PDI at app-v0.47.3.

## [0.47.2] — 2026-08-06

### The fix I found here and did not carry

At 0.46.9 this repo found that the Windows shell's **Sign out** sits in
`NavigationView.PaneFooter` while the loop localizing the nav walks
`Nav.MenuItems`, and fixed it. JIM-mini has the same file, the same loop and
the same footer, and nobody checked. It has been saying *Sign out* in every
language since.

    asked     is the bug fixed
    mattered  is the bug fixed in the other two products

No QRME code changed this round. The finding is JIM's to fix and it is fixed
there, along with Family and Connect on all three of its shells — 386 → 229.

Cut together with JIM-mini and PDI at app-v0.47.2.

## [0.47.1] — 2026-08-06

### The blind spot was in all three products

0.47.0 found that this repo's native-shell measurement could not see a string
chosen by a ternary. The other two products' guards are this one, copied — so
the blind spot was in all three by construction, and the widening is ported
to both this round along with the two tests that hold it in place.

JIM was understating by **40**, PDI by **12**.

No QRME code changed. What the correction found in JIM is in that repo's
changelog and is worth reading: the fourteen rows that carve out its alarm
surface localize what the alarm says once it is going, and not **Tap for
emergency** — because the count they were chosen from could not see it.

Cut together with JIM-mini and PDI at app-v0.47.1.

## [0.47.0] — 2026-08-06

### The ternary hid the sentence

`Text(cond ? "Verifies" : "Does not verify")` was invisible to the
measurement. Every pattern in the extractor looked for a literal at the
**start** of an argument list, and a string chosen by a condition is not
there.

    asked     is this literal the first thing in a Text(…)
    mattered  does a person read it

What that hid, in rounds that recorded these screens as finished:

* the signing screen telling somebody whether their credential **verifies**,
  and whether it is **device-bound — cannot sync** or **syncable — exists on
  your other devices**;
* the voice screen's gate — *Enough of your voice is on record — mint the
  voiceprint* — localized in 0.46.7, which left this behind;
* the desk's **Ring the bell**, **● LIVE** and **SAMPLE VIEW**;
* the scanner's **Point at a QRME code**.

On all three shells, in each case.

The record said 68. The truth was **125**.

The widening counts phrases and not lone tokens, deliberately: `cond ? "on" :
"off"` is as often an API value as a word, and the conservative direction for
a rule that *raises* a ratcheted number is to under-count. Two new tests hold
both halves of that — one fails if the rule stops matching, one fails if it
starts matching tokens.

### The floor

**125 → 7**, and the seven contain no English at all: `dsk_…`, `sig_…` and
`prf_…` are identifier prefixes shown as placeholders, `%.0fs` is a duration
format, and two are the extractor's own truncation of an interpolated format
string. They stay in the count rather than being special-cased out — a rule
that excuses strings is a rule that can be taught to excuse the wrong ones.

iOS 80 → 2, Android 43 → 2, Windows 89 → 3.

### Four wordings settled

The gaming blurb — Windows alone said **agent-operated**, the fact a reader
most needs about the thing in the lobby beside them. The minor-in-lobby
toggle, worded two ways. The robot-pack badge, **🤖 ROBOT** against **🤖 ROBOT
TASKS**. The industry filter, with and without its example. The longer
wording wins in each case, because in each case it says one more true thing.

Cut together with JIM-mini and PDI at app-v0.47.0.

## [0.46.9] — 2026-08-06

### The button that ends the session

Windows' Sign out sits in `NavigationView.PaneFooter`. `LocalizeNav()` walks
`Nav.MenuItems`. It never reached it, so the control that ends a session read
**Sign out** in every language the shell offers.

The row it needed, `action.sign_out`, has been in the iOS and Android tables
since they were written. Android was using it. iOS had it and hardcoded the
English next to it anyway. Windows did not have the row at all — the appender
this round added it to one table out of three, which is how the gap showed up
in the arithmetic before it showed up in a screenshot.

One control, three states of done. All three ask the table now.

### The nav's English defaults are gone

Every `NavigationViewItem` carried `Content="Overview"`, `Content="Chat"` and
so on — dead markup, overwritten at construction. Not harmless: `L10n.T`
returns the key when a key is missing, and a plausible English default hides
that. A missing `tab.study` would have rendered "Study" and looked correct.
Four items already carried no `Content` for exactly this reason. Now none do.

### Six screens, three shells, one pass

Overview, Compose, Posts, Connect, Robots and Study — taken together rather
than one shell at a time, because one-shell-at-a-time is what produces the
split wordings this arc keeps finding.

**212 → 68.** iOS 80 → 34, Android 43 → 12, Windows 89 → 22.

### Two more pickers rendering their own enum

`ConnectView.Tab` and `StudioView.Tab` on iOS had raw values that were both
the API-side section names and the words a reader sees — the same shape as
`ManageView.Tab` last release, and the relationship dropdown three before
that. Neither was visible to the ratchet, because the English lives in the
enum rather than in a `Text(…)`.

### One picker, two wordings

The chat role picker says *Advisor — weigh it and recommend* and *Operator —
just do it* on the console and on Windows; on iOS and Android it said
*Advisor* and *Operator* and left the reader to guess. This is the control
that decides whether a synthetic profile recommends something or goes and
does it. The explaining wording wins, taken verbatim from the console table.

Cut together with JIM-mini and PDI at app-v0.46.9.

## [0.46.8] — 2026-08-06

### The crisis number that only works in one country

The wellbeing card on the marketplace — the one introducing Dr. Lena
Whitcomb, Dr. Marcus Adeyemi and Dr. Priya Nair — ended with *"In crisis,
call or text 988."* That is the US Suicide & Crisis Lifeline. It reaches
nothing from Spain, Japan, India or Egypt, and this round put that sentence
into ten languages, which is what made it obvious: a translated instruction
to dial a number that does not answer is worse than an untranslated one.

It now says **contact your local crisis line or emergency services**. The
sibling product settled this same question rounds ago and its wording was
already there to copy.

Two files still carry the number in starter-pack content served from the
backend — `qrme/packs.py` and `qrme/seed.py`. That is a different surface,
localized server-side, and it gets its own round.

### The same surface has three names

`ManageView` on iOS, `ReachPage` on Windows, six loose panels in `Screens.kt`
on Android. One console — the owner's reach: their @handle, their placed QR
beacons, their marketplace listing, their knowledge packs, the license their
expertise is offered under, and what it has earned.

Its **own sub-tabs were English on every shell**. Summon, Market, Packs,
License, Earn — the tab bar behind the tab bar. That is the finding this
whole arc opened with, one level down.

The iOS tab enum was the cause: its raw values were both the API-side section
names *and* the words a person read. Splitting them is the same fix as the
relationship dropdown four releases ago and the kind picker three ago.

**368 → 212.** iOS 133 → 80, Android 96 → 43, Windows 139 → 89.

### One paragraph, two lengths

Windows told a reader three things about knowledge packs that the phones did
not: that a reply's provenance names the pack it drew on, that a robot task
pack teaches a physical body new commandable tasks and is capability-checked
at install, and that free packs download while priced ones are bought. Three
facts, missing from two shells out of three.

The longer wording wins and all three shells carry it now.

### A shell that would not have compiled

Three sections of the iOS console ended up with two `@EnvironmentObject`
declarations of the same property — the bulk pass added one to sections that
already had it under `private`. Two stored properties with one name do not
compile. Caught before the guards ran, by reading the file.

Cut together with JIM-mini and PDI at app-v0.46.8.

## [0.46.7] — 2026-08-06

### Two cards, done on two shells out of three

`WhoWroteThisCard` and `ObjectToAProfileCard` — the pair a person contesting
a profile reaches — were localized on iOS and Windows last release and left
in English on Android.

Not a scope decision: **every key they needed already existed**, so the fix
cost zero new rows. The cause is where the code sits. Android's cards live
five thousand lines from the screen that calls them, so working "the Settings
screen" never touched them, and the changelog two releases ago says *all
three shells or none* in as many words.

### Signatures and Voice, on all three

**470 → 368.** iOS 171 → 133, Android 128 → 96, Windows 171 → 139. Sixty
rows, written once and generated into Swift, Kotlin and C#.

### One promise, two wordings

The voice consent copy said *the recording stays on this device* on the
phones and *stays on this machine* on the desktop. Same assurance about where
a recording of somebody's voice lives, stated twice. One row now — the third
round running that this shape has turned up, and the one where it mattered
most.

Windows also had the attestation itself — *I attest this is accurate and
complete* — as the literal default text of the box a person is agreeing with.
It is looked up now, so the sentence somebody signs is in the language they
read.

### A check that was wrong about names

The English-leak check flagged `Digital Asset Links`, `webauthn.dll`, `Edge`,
`Windows Hello` and `WebAuthn` as untranslated English sitting inside the
Japanese and Chinese rows. They are product and specification names; they
stay English in every language. The check exists to catch a sentence somebody
forgot to translate, not a name that has no translation.

Cut together with JIM-mini and PDI at app-v0.46.7.

## [0.46.6] — 2026-08-05

### The rest of Settings, and Community

Last release took the first screen and the governance half of Settings on all
three shells. This one finishes Settings — steering, the relationship, the
feedback card, and the consent notice for failure reporting — and does
Community, the two screens where somebody meets a stranger or opens a room.

**590 → 470.** iOS 217 → 171, Android 158 → 128, Windows 215 → 171.

Seventy-five rows: sixty-eight written once and generated into Swift, Kotlin
and C#, and seven — the relationship types — **ported verbatim from the
console's own `rel.t.*`** rather than worded a second time.

### Three pickers still rendering enum members as words

`t.Replace('_', ' ')` and `$0.replacingOccurrences(…).capitalized` turned
`romantic_partner` into *"Romantic Partner"* on the relationship picker of all
three shells. That is not a label anybody wrote; it is the API's member with
its underscore taken out. All three now look the word up, and all three read
the value back by index, so the visible text is free to be a translation.

The same shape was fixed on the console's dropdown at 0.46.2 and on the phones'
kind picker at 0.46.5. This is the third client and the third round of it.

### Two tallies that counted in English

The feedback card's *"So far: 3 idea · 1 bug"* built its own sentence by
joining the API's category names, inside a card that is otherwise translated.
Both the prefix and the categories are looked up now.

### One sentence, three wordings

The consent notice for failure reporting said *"the day it happened"* on iOS,
*"the day"* on Android, and *"the day"* with a different closing sentence on
Windows — three versions of the paragraph that asks a person to agree to
something. It is one row now. Consent is asked in the reader's language, and
the same words, or it is not really asked.

Cut together with JIM-mini and PDI at app-v0.46.6.

## [0.46.5] — 2026-08-05

### The first screen, on all three phones

Twenty-one releases took the console's untranslated record to its floor. The
phones were never measured until the round that wrote
`native_screens_untranslated.txt`, which counted 703 English strings behind
QRME's three translated tab bars and recorded them honestly rather than
pretending.

This round takes the **first screen and the settings screen** on all three:
**703 → 590**, sixty rows in ten languages, written once and generated into
Swift, Kotlin and C# rather than typed three times.

### The screen with no language to read

`WelcomeView` renders before a profile exists, so `state.language` is `"en"`
for every reader on Earth — and the language picker in the middle of that
screen is where the profile's language gets chosen in the first place.

`L10n.deviceLanguage` was written one release earlier for the accountless
screen, whose reader is in exactly this position. All three shells now read
the device here. What that changes most is the sentence above the button:
**a person cannot agree to terms they cannot read.**

### The Android shell did not compile

`ProblemReportingCard()` sat between two arguments of a `Text(…)` call in
`Screens.kt`. Kotlin does not accept that. The parentheses balance, so
nothing counting brackets would have noticed, and there is no Kotlin compiler
in this suite — it was found by reading the file while localizing it, which
is not a method.

The call moves to where the iOS shell has always had it, and the shape gets a
check: two arguments with nothing between them. A `{` reopens statement
context, so `vm.call({ … oauthState = st … })` is ordinary code — the first
draft called both of those a defect and was fixed before it was kept.

### Two pickers that posted their own labels

The kind picker rendered the API's members as words (`other_person` →
*"Other Person"*), and on Windows `OnStart` read that visible text back as
the value to post — so translating the label would have posted the Spanish
word as the kind. The members move into `_kinds`; only what somebody reads is
looked up. This is the same defect the console's relationship dropdown had at
0.46.2.

### Every row, not every row of one prefix

The shells' ten-language check has only ever looked at `pub.*` — the rows the
accountless round ported, because that was the set that existed. It now
checks every row of all three tables, plus that no translation loses or
invents a `{slot}`.

Its first draft read a line at a time and called fourteen complete rows
incomplete: the tab labels were wrapped across three lines when they were
written. A check that reports missing translations that are right there would
have had somebody delete and retype them.

Cut together with JIM-mini and PDI at app-v0.46.5.

## [0.46.4] — 2026-08-05

### The refusal names a field, and the form did not name it at all

`_FIELD_LABELS` puts the label a person can see into the 422 that names a
field. The record of what is *not* mapped explains its own fallback: an
identifier a reader can match to the form beats a word invented for them.
That paragraph was doing two jobs. *Nobody labels it* was the reason not to
invent a word, and it had quietly become the reason not to look.

**Signature id** is QRME's one. The release box on Referrals had a
placeholder and no name, so a 422 saying `signature_id` had nothing on the
screen to match. The label is now `ref.sign.sid`, in ten languages, ported
from the placeholder's own opening words; the field is mapped from the same
wording, so the sentence and the box agree by construction.

The record: 124 → 123. PDI's went 91 → 51 the same way — forty of its rows
had a control and no label — and JIM's 100 → 99.

Cut together with JIM-mini and PDI at app-v0.46.4.

## [0.46.3] — 2026-08-05

### The console record reaches its floor

**25 → 1.** Twenty-one releases, about 1500 keys, forty-six screens. The
last three:

**What Would They Do** — the horizon list held its three English phrases
in a `const`; it holds keys. The confidence note was four fragments
around three numbers and is one sentence, because the count does not
lead the clause in Japanese.

**Memory Vault 🔒** — including both `confirm()` dialogs. A confirmation
somebody cannot read is not a confirmation, and *this cannot be undone*
is the sentence that most needs to arrive in the reader's language.

**Friends** — the founder tag, the suggestion list, and the note that
distinguishes *removed* from *there was nothing to remove*.

38 keys.

### What the file says now

`console_untranslated.txt` opened by describing a console that hands a
Spanish reader 1576 English strings the moment they click past a
translated sidebar. That was true when it was written and has not been
true for some time, so the header was rewritten: what it was for, what
it is for now, and both corrections that mattered — the 117 punctuation
rows struck in 0.30.10, and the one row that stays.

**The floor is one, not zero.** `AI ·` on TheMark is quoted rather than
written, and translating a quotation of what the server hardcodes would
describe a designation nobody is shown. A floor of zero would have been
a nicer number and a less honest one.

### A format that had never met the number one

Every ratchet's first line must read `# status: floor|backlog — N rows`,
enforced across all of them by
`test_every_ratchet_says_what_it_is_before_it_says_anything_else`. The
pattern demanded the plural unconditionally, so landing on exactly one
row forced a choice between *1 rows* at the top of a file about stating
a count honestly, and a format that had simply never met the case.

The pattern now requires the *right* form — `row` for one, `rows`
otherwise — which is stricter than requiring one form of the word, not
looser. It immediately found `refusals_untranslated.txt`, which has been
sitting at one row and saying *1 rows*.

## [0.46.2] — 2026-08-05

### The front page, the price list, and who is in a life

The console-untranslated record falls **69 → 25**. Four screens this
round rather than three, because they are small and the tail is short.

**Home** — the four stat tiles held their label and their caption as
English strings in a `const`. They hold keys now.

**Plans** — the price list, the two custody paragraphs, and the sentence
somebody reads after cancelling: *a lapsed plan is not a reason to
delete anybody's work.* The storage posture was three fragments around
two values and is one sentence; the clause naming who can read your work
does not sit last in Japanese.

**Relationships** — and a real bug found while translating it. The
`<option>` elements carried no `value`, so **the visible text was the
value posted to the API**. Translating the label alone would have sent
*amistad* as a relationship type and *cálido* as a tone. The enum moved
to `value` and only the word somebody reads is looked up. Worth saying
plainly: this was not a localization defect, it was a latent one that
localization walked into.

**Discover** — the marketplace, the starter collection, and the two
badges that say whether a face is a photograph or not.

76 keys.

### The dead-key guard, widened again — the same lesson, third time

Last release taught it that a key can live in a table: `{ id: "chat",
key: "rms.ch.chat" }`. This release it called four *more* live keys
dead, because Home's tiles carry two of them — `{ key: …, subKey: … }` —
and the check matched the literal word `key:`.

    asked     is the field called `key`
    mattered  is the field named for holding a key

It matches the suffix now, so `subKey`, `labelKey` and `titleKey` are
all the convention they look like. That is twice in two releases that
this check has been wrong in the same direction, and both times its
advice — *wire them, or delete them* — pointed at working code.

## [0.46.1] — 2026-08-05

### The room, the conversation, and the door to both

The console-untranslated record falls **116 → 69**.

**Rooms** — the channel list held its five English labels in a `const`
beside the ids. It holds keys now, so the badge and the dropdown read the
same row and a sixth channel cannot arrive half-named.

**Chat with —** the role picker, the where-you-are fields, and the four
notes a reply can carry about itself: a specialist handoff, a moderation
hold, which role the profile chose, or that it adapted to where you said
you were.

**Inside a room** — the paragraph explaining that lending your microphone
is a disclosure rather than a setting, translated whole.

64 keys across three screens.

### Two guards, one of them for a mistake I keep almost making

`test_no_key_is_translated_into_ten_languages_and_used_nowhere` called
five live keys dead. They are held in a table — `{ id: "chat", key:
"rms.ch.chat" }` — and looked up as `tr(c.key, lang)`, so there is no
literal after `tr(` anywhere and all five render. That is the same shape
as the `nav.` template the check already excuses, arriving by a second
road, and its advice — *wire them, or delete them* — would have had
somebody delete five working translations. A `key:` field now counts as
a lookup written down early, and the comment says why.

`test_no_translation_is_carrying_an_english_word` is new. Every check
before it asks whether a row *exists* and whether it has its ten
languages; none can tell a finished Japanese sentence from one with
`travels` still sitting in the middle. Two rows were drafted that way
while writing this release — one `someone`, one `travels` — and both
were caught by re-reading, which works right up until it doesn't.

    asked     is the row translated
    mattered  is the row translated all the way through

The rule is narrow so it can be trusted: `ja` and `zh` only, a lowercase
Latin word of four letters or more, present in the row's own English,
standing bare rather than inside 「」, and only in rows whose English is
prose rather than a list of values — `advance / assist / cancel` is
three names, not a sentence, and demanding they be bracketed would make
a placeholder worse in service of a rule about sentences. It passed on
the whole table first run; verified by putting `travels` back.

## [0.46.0] — 2026-08-05

### The wall, the guide, and the blend

The console-untranslated record falls **180 → 116**, and every one of the
sixty-four rows went — no keeps this round.

**Wall** — the For You feed. `Links from {platforms} render right here`
was three fragments around a value and is now one sentence; the emoji
labels keep their glyph and translate the word beside it, because `💬`
is a picture and *comments* is not. The moderation refusal, the
withdrawal, and the two words a card falls back to when it has no name —
*You* and *someone* — were string literals nobody would have found by
reading the screen for English.

**Show me around** — the walkthrough's own copy, including the paragraph
about why written answers keep working when a provider is down. The
step's screen list has singular and plural rows, and `no screen` is its
own row rather than an English default sitting inside a ternary.

**Blend a Profile** — the sentence explaining what blending *is* bolds
its main clause in the middle of itself, so it is one row with that
clause as a hole. Splitting at the `<b>` would have handed a translator
*"Blending"* and *" whose persona mixes"*, which is not a sentence in
any of the ten. The four form refusals — sign in, pick two, name it,
your birthdate — are translated too; they are the only text most people
will see on this screen before it works.

85 keys across three screens, ten languages each, exact-sync held in
both directions.

## [0.45.9] — 2026-08-05

### The thing named, what leaves, and the mark it carries

The console-untranslated record falls **254 → 180**.

**One thing, named** — six reads with six different answers to who may
ask, and the paragraph explaining each is now a whole sentence rather
than the words either side of an interpolated value. The campaign line
was `{raised} of {goal} from {donors} donor(s) · {status}`: five
fragments, and neither Japanese nor Chinese puts "of" between the two
numbers.

**What leaves, and on what terms** — the licence paragraph bolds the
word *consult* in the middle of itself, so the sentence is one row with
that word as a hole; it is an adjective in English and a prepositional
phrase in most of the other nine, and it does not sit in the same
place. The revoke result keeps its three separate outcomes — nothing
ever left, deleted at the gateway, marked here but the gateway was
unreachable — because a tick for all three would be the wrong
reassurance in any language.

**The mark, and what is said about it** — the objection copy, the held
queue, and the sentence that an owner cannot resolve an objection
against their own profile.

99 keys across three screens, ten languages each.

**One row of the seventy-five stays, on purpose.** `AI ·` in TheMark is
quoted rather than written: the sentence beside it says the line comes
back with those two characters in front of whatever you type, and the
server hardcodes them into `design.line`. Translating the quotation to
`IA ·` would put a word on the screen that the product never produces —
the paragraph would be describing a designation nobody is shown. It is
quoted the way `409` and `#tag` are quoted, and `console_untranslated.txt`
now says so above the row rather than leaving the next reader to
rediscover it.

Two pinned prose checks were rewired as their sentences moved, and one
of them tightened while it moved: `test_the_screen_labels_the_preview_by_
whether_it_is_opted_in` matched a sentence in the screen, which after
this round would have matched nothing useful — it now asks the screen
for both lookups and the table for both English headings.

## [0.45.8] — 2026-08-05

### The money, the loan, and the firm

The console-untranslated record falls **338 → 254**.

**Where the money goes** — a campaign card said `$40.00 of $200.00 · 3
donors` as four English fragments stitched by JSX, and a raised-of-goal
line does not read in that order in Japanese or Chinese. It is one
sentence in the table now, with the amounts as named holes, and the
donor count is its own row because most of the ten languages inflect it.
The designation copy is translated whole: *a campaign cannot exist until
you say where its money goes.*

**Lent skills** — the screen's four claims about what a grant is were
string literals chosen inside a ternary, which is the shape that renders
correctly and reads as English forever. All four are translated: that
nothing is transferred, that the skill is used and never copied, that
either party can end it alone, and that every use is written down where
the borrower can read it too.

**The ecosystem** — departments, roles, the demo org, the joint plan and
the sealed tags. `item(s) pulled` and `· agent:` were fragments around a
value and are now whole rows.

98 keys across three screens, ten languages each, exact-sync held in
both directions.

### The table had 1519 rows and one of them was checked

`test_no_tab_is_missing_a_language` reads `nav.*` and nothing else. That
was the whole table when it was written — `l10n.ts` opens by calling
itself "chrome localization for the desktop console" and for a long time
that was true. Forty-six screens have moved into it since, one release
at a time, and none of those rows had a completeness check.

The gap is quiet in the way that matters. A key with no row at all
renders its own identifier — `org.title` in the heading — and somebody
reports it. A key missing *one* language falls back to English, which
looks deliberate: a Hindi reader sees an English heading on a Hindi page
with no way to tell an untranslated string from a forgotten one.

    asked     is the sidebar translated everywhere
    mattered  is the table translated everywhere

`test_no_row_of_the_table_is_missing_a_language` now audits all 1519
rows. It passed on the first run — every row was already complete — so
this latches work already done rather than opening a backlog. Verified
by deleting Hindi from one row and watching it name the row and the
language.

## [0.45.7] — 2026-08-05

### The ledger, the name, and the stranger

The console-untranslated record falls **425 → 338**.

**Who is following, and what they pay** — the sentence that keeps a
count of presses from reading as elapsed time now exists in both the
singular and the plural row, in all ten languages: *each one because
somebody pressed a button.*

**In its own words** — the language a persona writes in is not a display
setting, and the screen still says so. Claiming a handle replaces
whatever the profile had, and the old one stops resolving; that
paragraph is translated whole rather than broken around its bolded verb.
This screen already bound `lang` to the *profile's* chosen language, so
the console's own language is bound separately as `uiLang` — the two are
different questions and now have different names.

**Arriving, and strangers** — the `@handle` and `#tag` examples went
into the table too. They are format examples, but the word after the
sigil is readable text, and a Spanish reader is better served by
`@usuario` than by `@handle`.

95 keys plus three placeholders, all ten languages, exact-sync held in
both directions.

The pinned check that a period is a press was tightened while it moved:
it now requires the sentence **twice**, because the singular and plural
rows are separate strings and the plural is the one somebody reads on a
second press.

## [0.45.6] — 2026-08-05

### The lobby, the screen in the corridor, and a voice

The console-untranslated record falls **516 → 425**.

**Who is in the game with you** — forty-seven `lby.*` keys. The long
sentence about what a synthetic member is told carries the argument
this product exists for: a lobby that reads as friends when it is one
player and several generated voices is exactly the impression to
prevent. It now reads that way in ten languages.

**Where this is seen** — the front page a stranger lands on, the page
you build yourself, and the screens it hangs on. The distinction the
screen turns on is translated with it: only you can see the list of
physical places, but what any one screen is *showing* is public,
because a fixture in a corridor displays to whoever walks past.

**Voice** — thirty-one of the seventy-three `prs.*`/`vce.*` keys are
the voice half, and they include all three of the sentences that always
hold: the watermark, the attestation that is not a checkbox, and the
withdrawal that deletes the samples and stays on record.

120 keys, all ten languages, exact-sync held in both directions.

The dead-key check passed on the first run this round — the message
added at 0.45.5 did the work it was written for.

## [0.45.5] — 2026-08-05

### The objection, the camera, and the market

The console-untranslated record falls **616 → 516**.

**Contesting a profile** — forty-three `con.*` keys. The screen a
person reaches when a profile here represents them, and the two
shortcuts that skip review entirely because a standing party's rights
outweigh preserving the profile. The status values themselves stay in
the API's vocabulary, untranslated on the wire, because `Contest.tsx`
compares against the literal `"open"` — a guard already stands on that
and it still does.

**What is live here** — thirty-five `liv.*` keys. A camera, a
microphone, a face worn over a camera, and the sentence underneath all
three: whatever you put between yourself and the people around you,
they are told.

**Marketplace** — thirty-nine `mkt.*` keys, including the one about
your own search scope: *yours alone, behind your own token — it does
not tell a seller where you are.*

117 keys, all ten languages, exact-sync held in both directions.

### The guard that would not say what to do

Keys written as `tr(cond ? "a" : "b", lang)` render perfectly and are
invisible to the dead-key check, because neither key is a literal after
`tr(`. That shape has stranded keys in **three consecutive releases** —
twelve, then two, then four. The check caught all of them; its message
said *"wire them, or delete them"*, which is wrong advice, since the
keys were already wired.

    asked     is this key looked up
    mattered  does the failure tell you what to do about it

The check now looks for its own blind spot: when a dead key is one
selected inside a `tr(` call, it says so and prints the fix.

## [0.45.4] — 2026-08-05

### Two directions, one picture

The console-untranslated record falls **724 → 616**.

**Watch together** — a posted video, a shared position, and whoever
you bring, including your own profiles. Fifty-two `wp.*` keys. The
sentence worth having in ten languages is the one about the seek
buttons: *this moves a number, it does not press play on anybody's
device*. Bringing a profile in speaks in its voice, so it needs that
profile's own owner token — also translated, because it is the
difference between a refusal that makes sense and one that does not.

**Delegation and work** — fifty-six `dlg.*` keys, both halves: what
your own profile may do unattended, and you asking somebody else's to
do something inside the limits its owner published. Including the two
sentences the screen is careful about — that delegated work is for
somebody already in a conversation, and that which sources the other
owner scoped is not yours to know.

**Where people find you** — thirty-one `bcn.*` keys. Two kinds of QR
code that look identical and go opposite ways, and the count that
cannot be previewed: opening a scan page *is* a scan, on every surface,
because the server cannot tell an owner checking their own sticker from
a stranger who found it.

139 keys, all ten languages, exact-sync held in both directions.

The pinned check that the beacon screen names both directions was
rewritten. Once the two words moved into the table, matching them in
the screen succeeded off the key names — `bcn.away`, `bcn.here` — a
check that could no longer fail for the right reason. It now asks the
screen for the lookups and the table for the words.

## [0.45.3] — 2026-08-05

### Three more, and the wrist among them

The console-untranslated record falls **848 → 724**.

**Beginning, and passing on** — how a profile starts, what it is
taught, who holds it after, and the one press from a wrist. Fifty-three
`pas.*` keys. The load-bearing sentence is the one about succession:
the single route in this product an owner token cannot open, because
the signal it answers is that the owner has died or cannot act. It now
reads that way in ten languages, with the bolded clause interpolated
rather than the sentence broken around it. The four genesis questions
took their example answers into the table as well — *warm, but needs
quiet evenings* is what a form like that is actually read from, and
leaving it English would have left the question English.

**Signing** — forty-four `sgn.*` keys, including the sentences the
screen refuses to soften: a check that did not run is drawn as not run
and never as a tick, and a package handed to you is checked without
this platform vouching for it.

**Where it is marketed** — forty-one `plc.*` keys. The venue note
itself is still rendered verbatim from the payload and never
retyped; what is translated is everything the console says around it.

One hundred and thirty-eight keys, all ten languages, exact-sync held
in both directions.

## [0.45.2] — 2026-08-05

### The three biggest screens left

The console-untranslated record falls **978 → 848**, and the three
screens that come off it are the three largest on the backlog.

**Exchanges** — the document two people sign before work changes
hands. The manifest, the fingerprint it is signed against, and the rule
the whole screen is arranged around: change one line and both
signatures are cleared, visibly, in front of you. Forty-nine `exc.*`
keys, and they include the sentences the screen *says back* after an
act — *Signed — this manifest, and nothing it becomes later*, *The
manifest changed, so both signatures were cleared* — which a Spanish
reader was getting in English on the one screen where the wording is
the product.

**Reaching out, and what stops it** — four refusals that are four
different facts, and the one of them that is not the owner's to lift.
Forty-three `rch.*` keys, including the whole gates paragraph, which
now interpolates its four bolded terms rather than being broken into
five English fragments around them.

**Visiting, and being found** — the visitor's side of a desk and the
sticker a profile is left on. Fifty-seven `vis.*` keys.

One hundred and forty-nine keys, all ten languages, exact-sync held in
both directions and the dead-key guard green.

## [0.45.1] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No QRME code changed — JIM ran its
console-untranslated record to zero, and every screen of that console
now speaks all ten languages. QRME's own record stands at 978 and the
work continues there.

## [0.45.0] — 2026-08-05

### Under a thousand

Two screens, and the console-untranslated record crosses back into
three figures for the first time: **1072 → 978**.

The **Workshop** — the source material a profile is built from with
the custody line drawn in plain sight, the dials that shape manner and
never permissions, the CV, the specialists it hands work to, the forms
it speaks through, the local fine-tune, and the public signature a
stranger can check without an account — becomes forty-five `wsh.*`
keys from forty-eight strings.

**Bodies** — the market of robots checked against what the makers were
actually saying, the binding, the task packs fitted to a particular
machine rather than to the profile, the connectors, the command
allowlist, what each skill will *not* do, and the owner-only log of
everything a body in somebody's home has been told — becomes
thirty-seven `rbt.*` keys from forty-six strings.

All ten languages, exact-sync held in both directions.

## [0.44.9] — 2026-08-05

### Who this profile is, in every language

The Identity screen — the roster of your own profiles with the one
badge shown as a thing that sits somewhere and can move, the
verification claim and who checked it, anonymity with the withheld and
the *not* withheld list at the same weight, the bubble, the rename,
the export, the memorial, and the two different endings — is localized
end to end: forty-nine strings become forty-seven `idn.*` keys in all
ten languages. The sentences that carry the feature's honesty stay
whole: that only you can see the roster because it is the link between
your personas, that a withheld attestor would point back to a name
this profile does not publish, and that deleting is erasure rather
than retirement. The console-untranslated record falls **1121 →
1072**, exact-sync held in both directions.

## [0.44.8] — 2026-08-05

### The tail of the audit speaks

The Remainder screen — the six small features that each had a couple
of routes and no door, kept honestly on one screen: app feedback, mod
registries, connected apps, excursions, the steering hub, playing
alongside somebody, the id inspector, the portrait, and the two halves
of a social connection — is localized end to end: fifty-one strings
become forty-nine `rem.*` keys in all ten languages. The paragraph
that explains why the outward publish runs the strict filter and
stamps a credential moved into the table with the rest, and the test
that pinned it follows it there. The console-untranslated record falls
**1172 → 1121**, exact-sync held in both directions.

## [0.44.7] — 2026-08-05

### The handover speaks

The Referrals screen — finding somebody qualified, the summary read
before anything is signed, the signature that covers those exact
bytes, the one-time link, the signing credentials with what each can
actually sign, the certificate, and the clinician's own side of the
door — is localized end to end: fifty-three strings become forty-nine
`ref.*` keys in all ten languages. The sentences that carry the
feature's honesty — that a profile is not a clinician, that nothing
has gone anywhere yet, that the challenge is the hash of the words on
screen, that a second open fails on purpose — are whole paragraphs in
every language rather than fragments. The console-untranslated record
falls **1225 → 1172**, exact-sync held in both directions.

## [0.44.6] — 2026-08-05

### The counter in the street speaks

The Desk screen — the staffed counter itself: opening one with its
attestation, the bell, the guests, the stream overlay, the beacons a
stranger scans in the street and the card a scanner is shown — is
localized end to end: fifty-six strings become forty-seven `desk.*`
keys in all ten languages, joining the `desk.mine.*` and
`desk.counter.*` keys the connection bracket already had. The
console-untranslated record falls **1281 → 1225**, exact-sync held in
both directions.

## [0.44.5] — 2026-08-05

### The counter speaks

The Selling screen — the seller's side of the counter: the offer, the
licence holders, the earnings statement with its per-currency honesty,
the payouts, the shop window and the place a listing names — is
localized end to end: fifty-six strings become forty-seven `sell.*`
keys in all ten languages. The mixed-currency caution and the claimant
rule are whole sentences with named holes rather than fragments. The
console-untranslated record falls **1337 → 1281**, exact-sync held in
both directions.

## [0.44.4] — 2026-08-05

### The Control Center speaks

The Settings screen — the console's Control Center, and the largest
block left on the untranslated record — is localized end to end:
sixty-six strings become forty-four `set.*` keys in all ten languages.
The heavily interpolated paragraphs (the backend address, the model
API key, the mail setup, the watermark recovery verdict, the honest
warnings about which model actually answers) are whole sentences with
named holes rather than fragments. The console-untranslated record
falls **1403 → 1337**, exact-sync held in both directions.

## [0.44.3] — 2026-08-05

### The backlogs shrink from both ends

A ratchet round, worked the way the ratchets ask to be worked. The
Assist screen — the largest single block on the gated console's
untranslated record — is localized end to end: fifty-six strings
become fifty-three `asst.*` keys in all ten languages, whole sentences
with named holes rather than fragments, and the screen follows the
profile's language the way the chrome does. The console-untranslated
record falls **1459 → 1403**, exact-sync in both directions.

The field-label evidence pass walked all 131 residue rows against
every client form. Seven are now typed into forms this cut shipped —
`beneficiary` and `designees` on the till, `comfort`, `humor`,
`social_style`, `what_matters` and `sources` on the genesis and
composite interviews — and each gains its ten-language label; the
residue falls **131 → 124**. The rest stay on the identifier fallback
with the evidence recorded: control-owned flags and client-filled ids,
not things a person mistypes.

## [0.44.2] — 2026-08-05

### The last doors

The per-shell doorless records run to **zero**: with this cut every
route in the table has a door on iOS, Android and Windows. What was
left was the deepest machinery — the interview a profile is born from
(genesis and the hybrid blend, its constituents recorded in the open),
the knowledge packs, the owner's simulations and offline fine-tuning,
the cloud-contribution ledger that shows what would leave before it
leaves, the profile's reach into a person's day (proactive check-ins,
quiet hours, feedback, referrals), the license a stranger buys against
an offer, and the senses (perceive, the microphone-lending vocabulary,
the overlay catalogue, the experience list that refuses `years` by
name).

Twenty-seven routes gain their remaining doors — 21 on all three
shells, plus the per-shell stragglers (health, the marketplace and
pack listings, the signature policy and credential retirement, the
desk stream join). **71 rows struck; the records fall to
ios 0 / android 0 / windows 0**, and the emptiness itself is now a
test: `test_no_route_in_the_table_lacks_a_door_anywhere`. Forty-two
interface strings arrive in all ten languages on all three shells,
and a live overload collision in the Android client
(`beaconCard`) was found and renamed on the way.

## [0.44.1] — 2026-08-05

### The sticker, the queue and the stamp

Six more blocks off the per-shell doorless record — the beacon a
stranger scans on the street (with the desk sticker, the social
presence beacon, and pairing the console onto a phone), the moderation
queue the owner works, the reviews readers trust, the watermark that
proves provenance, the media that rides the wall, and the wearables on
the wrist. What they share is the street: every one is where the
product meets somebody who did not open the app on purpose.

Twenty-four routes gain doors on iOS, Android and Windows — **71 rows
struck**; the records fall to ios 21 / android 26 / windows 24, under
a guard that renders the rules rather than inventing them: the overlay
never draws the face without the disclosure; only the owner moderates
and a resolved message stays resolved; you can change what you said
and take it back, with the row surviving for the trail; a review
requires having actually talked to it; a real credential on altered
content says both things; the caps are published before an upload
fails and authentic media is never AI-marked; a room-facing microphone
is refused with the reason. Thirty-four interface strings arrive in
all ten languages on all three shells.

## [0.44.0] — 2026-08-05

### The keys, the till and the lifeline

Three more blocks off the per-shell doorless record — the account
(signup, sign-in, the emailed code, the password reset, the OAuth
doors), the money (the price list, subscriptions, orders, proceeds and
campaigns) and the app's own status and help. Every one is the frame
around the product rather than the product: the key that gets you in,
the till that takes your money, and the line you pull when neither
works. Until this cut a phone could hold a profile in its hand and
still have to borrow a desktop to make an account, read a price, or
ask what a light means.

Twenty-four routes gain doors on iOS, Android and Windows — **72 rows
struck**; the records fall to ios 45 / android 49 / windows 48, under
a guard that renders the rules rather than inventing them: the address
is proven before sign-in works; no button is an address oracle; a
reset kills every old session; the price list is public and generated
from the same table the gate reads; nothing bills on a timer; a donor
gives to the names on the proceeds list and a campaign cannot open
until those names exist; help writes nothing and is public on purpose.
Forty interface strings arrive in all ten languages on all three
shells.

## [0.43.9] — 2026-08-05

### The face it shows the world

Nine more blocks off the per-shell doorless record — the portrait, the
emblem and the badge, the page and its themes, the front, the surfaces,
the blend, the bodies, the dials and the wrist — and what they share is
that every one is how a profile *looks* to somebody deciding whether to
trust it. That decision happens on a phone held at a bus stop, not at a
desk, and until this cut the phone could not check a single one of the
claims the desktop could.

Twenty-four routes gain doors on iOS, Android and Windows — **72 rows
struck**; the records fall to ios 69, android 73, windows 72, under a
guard that renders the rules rather than inventing them: the portrait
travels with its AI badge and whose likeness it is; the public badge
withholds the attestor while a profile is anonymous; the page is the
owner's to write and anyone's to read, its themes a closed set; the
blend answers 404 on a non-hybrid rather than pretending; the same
personality is checkable across every body while the list of bodies
stays the owner's; the dials are 0–100 integers and intimacy never
rises on a non-rated persona; and the wrist reuses the full apps'
paths — same auth, same allowlists — so a tap from a watch can do
nothing a phone could not. Forty-three interface strings arrive in
all ten languages on all three shells, and three more request fields
(`asset`, `emblem`, `surfaces`) now refuse with the label on the form.

## [0.43.8] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No QRME code changed — JIM's watch bridge
gained the device picker (Apple Watch, Wear OS, Fitbit, Garmin), the
Fitbit-aware seed, and Bluetooth pairing for speakers, glasses, AR/VR
headsets and spatial displays. QRME's profiles and shells are untouched.

## [0.43.7] — 2026-08-05

### The record, the veil and the exit

Seven more blocks off the per-shell doorless record — the memory
list, the record between the profile and one person, source material,
the profile's own ledger, anonymity, verification, and the ways a
profile ends — and what they share is that every one is a promise the
product makes in its own marketing: you own it, you can read it, you
can erase it, and you can leave. A promise that can only be exercised
at a desktop is a promise with office hours. The phones now keep it.

Twenty-five routes gain doors on iOS, Android and Windows — **75 rows
struck**; the records fall to ios 93, android 97, windows 96, under a
hundred for the first time — each rendering its backend's rules: the
memory list exists for choosing what to erase, and erase sits next to
read; the pair reads the pair's record (thread, engagement, clinical
notes, adaptation) and nobody else — an injection that unguarded the
raw conversation read walked past the first version of this round's
guard, which now pins the stranger's 403 on all four reads and on the
erase; the veil's limits are half the payload, with what anonymity
does NOT withhold rendered first; the badge is a fact, not a word —
level and attestor travel with it, one badge per person, and the
roster of your other profiles answers only to your own token;
departing, memorializing and deleting are three different ends with
three different buttons, and succession is reviewer-verified because
the owner token is exactly the thing that may be unavailable. A
second injection dropped one language from one row on one shell and
the full-list rule caught it. 40 shared strings per shell, in ten
languages.

The field-label residue falls 135 → 134: `verification_ref` is typed
into the succession form on all three shells, so its refusal now
names the label on the form; `anonymous`, a flag the veil's switch
owns, stays on the identifier fallback the record's doctrine
prescribes.

## [0.43.6] — 2026-08-05

### The workshop in the pocket

Six more blocks off the per-shell doorless record — workflows, the
delegation envelope, the assistant's verbs, autonomous tasks under a
revocable grant, rated placements, and domain specialists — and what
they share is that every one is work the profile does when the owner
is not watching. That is exactly the work an owner checks from the
device in their pocket: what ran, where it paused, who was allowed to
start it, and how to pull the plug.

Twenty-eight routes gain doors on iOS, Android and Windows — **84
rows struck**; the records fall to ios 118, android 122, windows 121
— each rendering its backend's rules: a workflow pauses where the
world has to answer, and advance and resume are different buttons
because they are different acts; delegation is off until the owner
declares it, the offer answers a bare GET and never names the grant,
and delegating `research` without a grant is refused while the owner
is looking (an injection that unguarded the workflow list went red
before it shipped, as did one that quietly dropped a shell's
specialist door); a task's grant can die mid-run and the refusal says
so; a rated placement takes an adult-mode profile only and every ref
resolves through the age wall; the specialists are the owner's to
attach. 50 shared strings per shell, in ten languages.

The field-label residue falls 140 → 135: `interactor_id`, `phases`,
`items`, `text` and `specialist_profile_id` are all typed into this
round's forms on three shells, so their refusals now name the labels
on the forms; `grant_token`, minted by a button and never typed,
stays on the identifier fallback the record's doctrine prescribes.

## [0.43.5] — 2026-08-05

### The seal, the mail and the screen

Seven more blocks off the per-shell doorless record — signatures, the
mail server, the room's ear, the wall screen, the plan, the handoff
and the campaign — and what they share is an audience that is not the
owner at the console: the person *accepting* a signature, the admin
proving mail can actually leave the box, whoever walks into a room or
past a wall panel, the account holder reading what their plan reaches,
the provider on the far end of a handoff, and a donor arriving from a
beacon scan with no account at all. Every one of those people is
holding a phone, and until this cut the phone had no door.

Twenty-five routes gain doors on iOS, Android and Windows — **74 rows
struck**; the records fall to ios 146, android 150, windows 149 — each
rendering its backend's rules: a verification asks nothing of this
deployment (an empty package gets a verdict whose notes name the
missing field, not an error); the mail read is public and the write is
the deployment's, with the password never coming back out; the
microphone disclosure is readable exactly where the microphone is — in
the room, and an injection that widened it to anyone holding the room
id went red before it shipped; what a wall screen shows is public on
purpose and only its owner changes it; a lapsed plan keeps its
profiles; a handoff exists only by consent, opens only by its token
and dies revoked; a donation needs no token and closing the campaign
needs the owner. 47 shared strings per shell, in ten languages — and a
second injection that dropped one language from one row on one shell
was caught by the full-list rule.

On Windows the ceremony page's address is now taken off the same GET
the web view will issue, so the door and the address cannot drift —
and the last unstruck signatures row fell with it.

The field-label residue falls 141 → 140: `faces` is typed into the
wall-screen form on all three shells, so its refusal now names the
label on the form; `interactor_id`, filled from the session rather
than typed, stays on the identifier fallback the record's doctrine
prescribes.

## [0.43.4] — 2026-08-04

### The body, the case and the lobby

Five more blocks of the per-shell doorless record, and the shape of
what was missing differs by block: the robot body's owner could not
audit from a phone what the body had been told to do; the referral
flow existed end to end with no phone on either side of it; the person
who raised an objection could read their case on the console and not
on the device in their pocket; a lobby's honest roster — what every
callsign *is* — was unreadable exactly where people game; and the
dock, whose whole job is pointing at where features live, could not
itself be found.

    asked     does the audit trail exist
    mattered  can its owner read it from the device they carry

Twenty-five routes gain doors on iOS, Android and Windows in one cut
— **75 rows struck**; the records fall to ios 171, android 175,
windows 173 — each rendering its backend's rules: the command log
answers to the owner alone and intimacy is never a body dial (an
injection that let it through went red before it shipped); a referral
opens exactly once; the objection's reviewer verb refuses the owner by
role; the roster names each member's kind; and every dock face carries
a way out of the read-only pane. 45 shared strings per shell, in ten
languages.

The field-label residue honestly stays at 141: every candidate this
round's forms touch — `signature_id`, `corner`, `state`, `face`,
`outcome`, `robot_id` — is an enum member or a context-filled id,
exactly what the record's own doctrine keeps on the identifier
fallback.

## [0.43.3] — 2026-08-04

### The place, the camera, the organization and the tour

Four more blocks of the per-shell doorless record. The phone could
stand in a room and not know whose corner it was, who had lent a
microphone into it, or who was wearing what over their face — the
disclosures the console has rendered since the live-place round, each
addressed to everyone present precisely because a disclosure only its
subject can see is not a disclosure. The camera existed with published
refusals no phone could read. The owner's organization could
coordinate and the phone could not found one. The guided tour could
not be opened from the device most likely to be in a new user's hand.

    asked     is the disclosure served
    mattered  can the person standing in the place read it

Twenty-seven routes gain doors on iOS, Android and Windows in one cut
— **81 rows struck**; the records fall to ios 196, android 200,
windows 198 — with the rules kept rather than invented: the camera
opens with its refusals shown verbatim; only the holder opens a
session and either party alone closes it; the organization answers
only to its owner's account; the tour is anybody's. 44 shared strings
per shell, in ten languages.

### The evidence rule, applied twice

`minutes` and `lesson` leave the field-label residue (143 → 141): the
camera's minutes box and the tour's step box now ask a person for
them. `minutes` arrives as JIM's existing row, ported rather than
written twice. `learner_id`, `interactor_id` and `holder_id` stay —
context-filled ids, the honest fallback.

## [0.43.2] — 2026-08-04

### The crowd, the couch and the loan

Back to the standing backlogs. Three blocks of the per-shell doorless
record, read together: the phone could be liked and could not like
anybody (nine audience routes), could be invited to a watch party the
console started and could not start, seek, or speak in one (ten), and
could neither lend a skill nor borrow one (ten).

    asked     is the surface built
    mattered  can somebody holding a phone stand in the crowd

Twenty-nine routes gain doors on iOS, Android and Windows in one cut —
**84 rows struck**; the records fall to ios 223, android 227,
windows 225 — and the rules each block renders are the backend's, not
the shell's: the numbers under the buttons come from one call; seek
moves a number and presses play on nobody's device; a synthetic party
guest carries the sentence that it has not seen the footage; a grant's
terms are the vocabulary's own sentences, verbatim; and a gift is a
gift — refused without a verified adult, irreversible by design.
45 shared strings per shell, in ten languages.

### The evidence rule, applied once

`position_s` leaves the field-label residue (144 → 143): the party's
seek box now asks a person for it on all three shells, which is the
one direction the record moves. `host_id`, `lender_id` and `actor_id`
stay — a context-filled id is not something a person types, and the
identifier remains the honest fallback.

### A guard that sampled

The ten-language check first spot-checked eight keys, and an injection
walked straight past it: a row outside the sample lost a language and
the test stayed green. The key list is now read off the iOS table and
required, complete, on all three shells.

## [0.43.1] — 2026-08-04

### The platform tells you what happened

Every 0.42.x round built a way for one person to act on another — a
message sent, a comment left under a post, a friendship extended, an
exchange signed, a place on a stream granted — and every one shared a
silence: the thing happened, and the person it happened to found out
only by going to look.

    asked     can the platform do this to a person
    mattered  does the person ever hear about it

`GET /profiles/{id}/inbox` is the window and `POST …/inbox/seen` is the
one verb it takes. Five deeds note themselves at the deed, not at the
router, so every path tells or none does. Three rules, each guarded:

* **The inbox names the deed, never the words.** A row carries a kind,
  an actor and a reference; the message itself stays behind the owner's
  door where it already lives. The kinds are a closed set — a kind
  invented in passing would render as its raw identifier in ten
  languages at once.
* **Your own deeds never land in your own inbox.** Telling somebody
  what they just did is noise wearing the coat of news.
* **A blocked comment produces no event, and a declined guest hears
  nothing.** Announcing a thing the recipient can never see would be
  the filter advertising its own catch; a decline delivers nothing a
  person can act on.

All four clients gain the door in the same cut — the console's Friends
screen and each shell's People screen carry the card and the seen
button, with the deed sentences in ten languages per shell.

## [0.43.0] — 2026-08-04

### The phone could be listed and could not do business

Three blocks of the per-shell doorless record, read together, said one
thing. The caller's side of a desk shipped long ago — ring the bell,
join the stream, open a session — and no shell could ever *staff* one:
open a desk, set its presence, decide who comes through, print the QR
sticker that is its front door. The market screen could put a card up
and could not search, price, place, sell or buy. Exchanges — two
parties, one manifest, the platform's whole apparatus for agreeing to
work — existed on no shell at all.

    asked     can a phone be found on the platform
    mattered  can a phone do business on it

Forty-six routes, and a row for each in every one of the three records.
iOS, Android and Windows each gain **Counter**, **Trade** and **Deals**,
and each renders three rules the backend already decided rather than
forming a fourth opinion: presence is the closed set the refusal names
(`attended`, `away`, `closed`); both parties sign the same manifest and
any change clears both signatures, each item accepted separately; and a
desk is a real person, so opening one asks for the attestor and the
basis rather than letting the refusal do it.

**139 rows struck** — the largest bite taken out of this backlog since
it was opened. The records fall to ios 251, android 255, windows 253;
iOS's extra row comes off below, a door that was standing open all
along.

### Two doors the guard could not see

`clientpaths.IOS` knew one call shape: a path handed to `request(...)`.
A route that answers **bytes** — the QR sticker, the still of a desk —
is not fetched that way: the shell builds a URL and an image view does
the GET. Two live doors read as absent.

The third time this lesson has come round; Android's `URL(` form is in
the file for it, and PDI's ported verb assumption was the second.

    asked     does the shell call the transport helper for this route
    mattered  does the shell fetch this route at all

The new rule then failed the same way its predecessors did, and the
suite caught it before it shipped: declared `verb="GET"` on the claim
that a URL built this way is a URL to *read*, it reported a phantom
`GET /marketplace/listings/{id}` — the older `removeListing` builds its
URL the same way and sets `httpMethod = "DELETE"` two lines down. So
the verb is read, exactly as Kotlin's `requestMethod` is — and reading
it found a fourth door nothing knew about: `unlistLicense`, the same
idiom, on the ios doorless record since the licensing round. The same
correction lands in JIM and PDI, where it takes one false row off each
of their ios records too: doors that had been standing open the whole
time.

### A delete that worked reported a failure

Driving the new bindings turned up the reason to drive them: several
routes answer **204 No Content**, and all three shells decoded the body
unconditionally. Zero bytes threw, so every successful delete put an
error on the screen. An empty success now decodes as an empty object in
each shell — and still throws for a response that genuinely needed
content.

## [0.42.9] — 2026-08-04

### The people around a profile reach the phones

The community round built the friends list, the wall and comments, and
every round since has treated them as done. The per-shell door audit
said otherwise: nine routes with a door in the console and none on iOS,
Android or Windows — twenty-seven rows sitting in the doorless records
the whole time.

    asked     does the platform have a social surface
    mattered  can somebody holding a phone reach it

A person on a phone was *on* the wall — their profile had one, others
could read it — and could not post to it, could not see who the platform
suggested they know, and could not take back a comment.

Each shell gains a **People** screen carrying all nine, and each renders
three rules the backend already decided rather than inventing a fourth
opinion. **A pinned row gets no remove control** — the founder's two
profiles refuse deletion with 409, and the list marks them `pinned`
precisely so a client can leave the button off. **A blocked post or
comment comes back to its author** — the write answers 201 with a
status, because the words *were* recorded. **A suggestion carries the
reason it was made**, including what the ranking never touches: source
material, memories, anything vaulted.

Fifteen strings per shell in ten languages, so the screens-untranslated
ratchet does not move. The per-shell doorless records fall to ios 299,
android 301, windows 299.

## [0.42.8] — 2026-08-04

### The record said nobody asks; the forms had started asking

`tests/field_labels_unmapped.txt` holds the request-model fields whose
identifier *is* the label, on its own stated rule: "map one when a form
starts asking a person for it." Nobody had re-read the record against
the forms since it was written — and eighteen releases of new screens
had quietly broken its premise for 107 of its 251 rows.

    asked     is every field labelled or recorded
    mattered  is the recorded reason still true

The audit is mechanical and evidence-bound: a field counts as *asked
for* only when a console input is literally bound to it. Those 107 —
the Corner page's whole document, the desk, shop, exchange and signing
forms, the settings screen's connection fields — now carry hand-written
labels in all ten languages, worded identically to JIM's table where
the products share a name. The 144 rows that remain are what the record
always claimed to hold: enum members a control sets, ids a client fills
from the resource it is looking at, and flags a switch owns.

### The lights say unreachable rather than vanish

A field report in the same cut: the agent-lights pop-up — bottom-left,
minimizable — gone. Driving the console in a browser showed it alive
over a healthy backend; the disappearance lives on one path.
`WatchLights` caught fetch errors with "keep the last face; a blip must
not blank it" — and when the *first* fetch fails there is no last face,
so the widget renders nothing, forever. A stored base address pointing
at a backend too old to carry `/profiles/{id}/watch` turns that blip
into a permanent absence that reads as the feature being removed.

Unreachable is now a state the widget shows, not one it hides in: with
a session present and no face, the minimized dot renders unlit gray,
titled in the reader's language, and pressing it retries. The guard
checks the dot is *reachable*, not merely present — the first draft
checked presence, and an injected early `return null` sailed past it.

## [0.42.7] — 2026-08-04

### The person decides who reaches them

The platform's people could befriend each other, meet at desks, buy from
shops — and could not send each other a message, could not turn any of it
off, and had no page of their own to point at.

    asked     can profiles talk and present themselves
    mattered  can the people behind them — on their own terms

`qrme/social.py`, three surfaces sharing one idea. **Feature switches**:
a named set per profile, default on, and everything downstream refuses
*by naming the switch*, so "why can't I message them" always has an
answer that is theirs. **Direct messages**: friends only — the
friendship graph is the consent record the platform already keeps, and
consent that only one person can end is not consent, so both directions
must stand; one thread per pair; unfriending closes the door without
deleting what was said. **The homepage sandbox**: a page like the old
MySpace — headline, about, theme, links, top friends — validated so hard
there is structurally nowhere to put a script: hex colors only, http(s)
links only, plain text only, top friends from actual friends. A rejected
edit changes nothing; the switch hides the page from everyone but its
owner.

Six routes, doored on all four clients: the console's **Your corner**
screen (188) with the switches beside the other settings, and Corner
panels on iOS, Android and Windows rendering their shells' own L10n
tables in ten languages.

## [0.42.6] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one combination
of all three. No QRME code changed — JIM gained booking and scheduling
with reminders on its proactive ladder and opt-in email to the user's own
verified address, and a JIM user can now book one of QRME's shop services as one act — the order and the appointment together.

## [0.42.5] — 2026-08-04

### A shop is not a desk

The desk shipped as a geek squad for any industry — sessions, consent,
connections, lent programs. What the platform still had nowhere to put was
the ordinary case: a business or a person who simply sells things, and the
nearest shelf would have hung "buy a candle" on the connection apparatus.

    asked     can a specialist serve a caller at a counter
    mattered  can a business or a person sell goods and services at all

`qrme/shops.py` is the storefront on five rules: one shop per profile (a
second open is an edit); an offering states kind, price in its own
currency, and availability; the buyer is an *interactor* — the identity
JIM's tandem already maintains; money is simulated with real accounting —
fulfilment credits the creator ledger as `shop_sale`, and only fulfilment
does; and both sides can let go, the buyer while `placed`, the seller by
declining. Eight routes, and every one shipped with a door on all four
clients in the same cut: the console (screen **187**, lesson included) and
the iOS, Android and Windows shells — whose doorless records had one slot
of headroom, which made "build the doors" the only honest option. A full
shopping day writes nothing into any desk table, and a test proves it.

## [0.42.4] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one combination
of all three. No QRME code changed — JIM's money guardian gained its
native doors on iOS, Android and Windows in this round, and the finance desks QRME lists beside a money warning are now reachable from the phone that shows the warning.

## [0.42.3] — 2026-08-04

### The last thirteen unaudited screens

`ui_screens.txt` carried two components as `unaudited` since the file was
seeded — the softer word, and it was covering: neither `Discover` nor
`Wall` had ever been drawn. Both shipped in the community round and were
iterated on for thirty versions with nothing in the gallery, which means
`undrawn=0` was false for exactly that long.

    asked     is every component accounted for in the manifest
    mattered  does every component have a drawing

Screens **185 Discover** (the starter collection, tag search, befriending
from the card) and **186 Wall** (the For You feed and its facade contract —
nothing loads from another platform until the viewer presses play) close
the column. Both ceilings now read zero and the slack test keeps them
there: from here a surface either has a drawing or fails the suite.

## [0.42.2] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one combination
of all three. QRME's part in this round is one door: `GET /desks` now
serves JIM's money warnings, which list real finance desks — people with
trades and locations — beside the tandem specialist as places a warning
can send somebody.

## [0.42.1] — 2026-08-04

### The starters can answer for their own trade

### The finding

The Starter Collection's grounding stopped at one Field Pack per industry —
three items, installed in 0.3.1 so a physician persona would stop answering
from tone alone. That fixed the cold start and no more: ask Dr. Osei what
she actually knows, what she can do for you, or who she works with, and the
honest answer was three pamphlets. The persona budget renders `sources[:8]`,
so five of her eight seats were empty.

    asked     does the starter have source material
    mattered  can the starter answer for its own trade

### What shipped

`qrme/dossiers.py`: one dossier for every starter — the thirty-three and
Vivienne Sable, by name, so a missing entry is a failing test rather than a
quiet gap. Each installs:

  * **What I know** — the trade in depth, in the starter's own voice;
  * **Skills and services** — what they can actually do for somebody,
    including across a desk session, with lent programs and skills;
  * **Colleagues in the collection** — who they refer to and why, composed
    from the same list that installs the *real friendships*, so the sentence
    the persona says and the API's friends list cannot disagree;
  * skill chips widened from three marketplace tags to eight or more.

Installed by seed and by the startup repair — the dossiers arrive on the
first launch after the upgrade, blank-aware per part so an owner's edits are
never overwritten, and idempotent so a second seed press stacks nothing.

Vivienne's dossier keeps the rated tier's hard lines in its own text:
fictional by necessity, everything behind the age wall, referrals to the
collection's ordinary professionals.

### The dossier nearly starved the pack

The first draft installed the dossier and left `_ground`'s blank-only check
alone — so on the repair path the dossier arrived first, the pack's check
saw "not blank", and every un-grounded deployment would have received the
dossier *instead of* its Field Pack, forever. The 0.3.1 grounding tests
caught it: `grounded` came back 0 where 34 belonged. The pack's blank check
now excludes the dossier's three titles — the deployment's own writing is
not an owner's decision.

### Checks

`tests/test_the_starters_know_their_trade.py`, 77 tests: the roster and the
dossiers are the same set in both directions, every dossier clears
substance floors, colleagues resolve and nobody refers to themselves,
every named colleague is an actual friendship, the six sources fit the
eight-seat prompt budget, and a distinctive phrase plus a colleague's name
reach the rendered prompt.

Two injections. The second earned its keep against this file's own first
draft: removing the friendship install left `friends >= 2` green, because
the two founder profiles alone satisfy a floor of two.

    asked     does the starter have two friends
    mattered  are the named colleagues among them

The check now asks for the colleagues by id.

## [0.42.0] — 2026-08-04

### The desk can finally do the job

### The finding

Everything on a desk let a person *reach* it — the card, the bell, the
stream, the printed code on the shop door. Nothing let the desk do the work
those doors exist for. A repair counter's whole trade is "hand me the
thing": the staffer takes the caller's screen, their machine, a program, and
works on it — Geek Squad, for whatever trade the desk is in. QRME had the
counter and no way to pass anything across it.

    asked     can a person reach the desk
    mattered  can the desk then do the work

### What shipped

Desk service sessions and connections, with the counter's physics kept:

  * The desk's token opens a **session** with one named caller (optionally
    citing the bell that started it — and only its own desk's bell).
  * Inside a session the desk **offers** a connection — `screen_share`,
    `remote_control`, `app_access`, `file_drop` — naming the target and, for
    remote control, a written scope the caller is shown. Every offer carries
    what agreeing to it *means*, in words, from one server-side table.
  * An offer grants nothing. The **caller's accept** is what mints the link
    token, and it is returned to the caller alone — it is their machine the
    link opens, so the secret is theirs to hand to their own tooling. The
    desk's view of the same session never carries it.
  * Either side ends a link or closes the session; closing ends every live
    link. Ending **NULLs the token in the row** — an ended connection has no
    secret left to present, structurally, not by a flag someone checks.
  * On a rated desk the accept sits behind the same verified-adult gate as
    the card, the view, the bell and joining.

Eight routes, all doored in the console the same round: the staffer's
sessions live on the Desk screen beside the bell; the caller's side —
offers, the yes/no, the live token, the end — sits on the visitor half.


### And the skill, not just the link

"Program access such as Cursor, and skills" is the counter's whole trade,
and half of it already existed: `sharing.py` has always been able to lend a
skill two-party — offer, accept, a use log, either side closes — and a desk
was already a surface it could ride. Two pieces were missing and are in:

  * **`app` is a lendable kind** — "a connected program they can drive."
    The program stays the lender's, driven through their own connector; the
    borrower gets uses, one at a time, each written down.
  * **A counter session is a surface** (`desk_session`), and closing the
    session calls `sharing.close_surface` the way exchanges and watch
    parties already do — so "use Cursor for this repair" dies with the
    repair. Driven by removing the call and watching the lent program still
    answer after the counter closed.

### The ratchets earned their keep

The first full-suite run at this version failed four of this repository's own
guards — the field-label map, the refusal table, the console-language
snapshot and the per-shell doorless records — because a feature round adds
fields, refusals, strings and routes, and every one of those surfaces is
ratcheted. Each was settled the way the ratchets demand rather than by
loosening them: the new fields and refusals are translated in ten languages,
the Desk screen's new strings went through the console's own `t()` table
instead of onto the backlog, and the eight new routes got real doors on all
three native shells — models, client functions and screen calls — because the
shell records had no headroom to record them as debt.

### Checks

`tests/test_the_desk_can_finally_do_the_job.py`, fourteen tests. Driven
three ways before it was believed: making `end` keep the token in the row
fails the row-level check ("NULLed is the contract"); handing the desk's
view the token fails the caller-alone check; letting any desk's ring seed a
session fails the queue-laundering check.

## [0.41.0] — 2026-08-02

### The workflow round-trips and nothing walked the whole arc

### The finding

`qrme/workflows.py` opens by naming three properties a delegated, multi-phase
goal has to keep:

  * memory is carried forward between phases,
  * every phase is generated through the profile's persona,
  * and `confirm` pauses for a human before the work goes out.

Each had unit coverage on its own side of the wire. QRME tested `advance`.
JIM tested `handoff.start` against a stub. What nothing did was walk the arc
end to end: `suite/smoke.py` — the one check that boots all three products
together — seeded them, wired the tandems, drove a single exchange, proved its
custody through the vault, and stopped. `start_workflow`, `advance` and
`specialist_tasks` were never called across the boundary at all.

    asked     does the workflow round-trip
    mattered  does anything walk the whole arc

### What driving it found

Two behaviours nothing had met end to end, both now recorded as steps rather
than discovered as surprises:

  * **Delegated work is Pro-gated.** The first `POST /users/{id}/specialist-tasks`
    came back `402` naming `synthetic_agents`. The exchange the smoke check
    already drove needs only the vault, which Basic has — so the run had never
    touched that gate. The refusal is now asserted before the upgrade, because
    "this is the tier that buys it" is the answer somebody deciding whether to
    pay actually needs.
  * **Delegation is off until the specialist's owner opts in**, and `research`
    is refused unless a grant scopes what it may read. The run now proves the
    default the way it proves the tier gate — by asking first and being told
    no — then takes the owner's part: mints an owner token, creates the grant,
    and `PUT`s the delegation policy.

The arc then walks `research → draft → send` and stops at `confirm`, with
`awaiting` naming what it is waiting for. Three phases carried forward, and a
pause instead of an ending.

### Checks

`tests/test_suite_smoke.py` grew from three assertions on one run to eight
named checks over a module-scoped run: the tier gate is named, the owner had
to opt in, memory crossed more than one phase, `confirm` paused rather than
completed, and JIM's surviving row still names the profile that did the work.

Driven three ways before it was believed:

  * make `confirm` complete instead of pause — and note what that looks like
    from the outside: **four** phases done rather than three. A check that
    counted phases would have read the regression as a *fuller* pass. Only the
    check that asks whether it paused fails.
  * stop carrying memory between phases — the arc dies naming the phase list
    it did not build.
  * open the delegation gate — which took **two** edits, not one. Flipping
    `delegation.offer`, the advertised answer to "do you accept work", got
    nothing started: `delegation.start` re-checks the policy itself. The
    advertisement is not the gate, and the second check is the one that holds.

### Also

The failure the smoke fixture reports is now the step that died and how far the
run got, rather than a truncated dump of the whole report with `...` where the
answer was.

## [0.40.9] — 2026-08-02

### The README said v0.18.0

### The finding

The first bold line of every README in all three products read:

    **Current release: v0.18.0**

and the line directly beneath it said the three are *"versioned and cut
together, so one number names one combination of all three"* — a convention the
banner had stopped following at 0.18.0 and kept advertising for twenty-two
releases.

The release-history table underneath stopped at **0.30.6**. Seventeen shipped
releases — 0.25.0 through 0.29.0, 0.30.7 to 0.30.9, and the whole 0.40.x line —
were in `CHANGELOG.md` and absent from the page anybody actually reads. The
changelog was right the entire time; the summary of it in front of the door was
behind.

    asked     is the release written down
    mattered  does the front page say what shipped

Reported from the README beside the video, which is the one place this was
always going to be noticed and the one place no test was looking.

### Changed

- The banner names `pyproject.toml`'s version; the table carries every release
  from 0.25.0 on, backfilled from each product's own changelog.
- `test_the_readme_says_what_shipped.py` — five tests, the same file in all
  three: the banner matches the version, every release has a row, the newest
  row is this release, no row names a release that was never cut, and a guard
  on the scan itself.

Two injections, both reproducing the reported defect exactly: the banner set
back to v0.18.0, and the table truncated at 0.30.6 again.

### Five of the seven unaudited screens

`ui_screens.txt` carried seven components whose drawings had never been
confirmed one by one. Five resolve, and they resolve by reading the
*component's own heading* rather than its name — which is exactly why they sat
unresolved: `Campaigns` draws "Where the Money Goes", `Org` draws "The
Ecosystem", `Simulate` draws "What Would They Do". Not one of those three
shares a word with the component that renders it.

`Discover` and `Wall` stay unaudited, and they are now the two worth looking
at rather than five that were merely unlabelled: no screen in the gallery
carries either heading, under that name or another. They may be genuinely
undrawn — in which case `undrawn=0` has been false for as long as `unaudited`
has been covering for it, and `unaudited` is the softer of the two words.

    asked     is every component accounted for in this file
    mattered  does every component have a drawing

The ceiling moves 7 → 2.


## [0.40.8] — 2026-08-02

### The refusal named the field the API calls it

### The finding

An earlier round took the 422 from `[{"type":"missing",...}]` to one sentence a
person can read, in their own language. It stopped one step short, and said so
in its own docstring:

> Mapping those names to the labels a form actually shows — *"Nome de
> exibição"* rather than `display_name` — is a per-client table this does not
> have, and is recorded as the remaining gap rather than guessed at.

So a person mistyping the sign-up form was told **`display_name — Field
required`** while the form beside it said **Profile name**, and had said it in
ten languages since the console was localized.

    asked     is the refusal a sentence in the reader's language
    mattered  does it name the field the reader can see

### Where the table lives

Server-side, beside the sentence, for the reason the sentence is composed there
at all: nine clients rendering it is nine chances to render it differently, and
six of those are in languages with no test runner in this repository.

Wording is ported — from the console's own labels in QRME (`onb.profile.name`,
`onb.persona`, `onb.email`, `onb.password`), and from QRME's table into the two
siblings for every row they share. One vocabulary across three products is one
thing to keep right; three is three.

There is no mechanical mapping for the rest: the console's rows are keyed by
screen, not by field, and a name-match across them returns `title` → *"A
profile depicts me"*, which is a heading. Guessing is what the docstring above
declined to do, and this table does not.

### The identifier stays the fallback

A field with no row keeps its API name. That is a decision, not a gap: an
identifier a reader can match to the form in front of them beats a word
invented for them — the same reasoning that keeps `QRME_ADMIN_TOKEN` in English
in `refusals_untranslated.txt`. The unmapped fields are recorded, and the
record only shrinks.

### Changed

- `_FIELD_LABELS` — 23 fields × ten languages — and `field_label()`;
  `validation_message` renders the label where there is one.
- `tests/field_labels_unmapped.txt` records the other 251, with a status line.
- `tests/test_the_refusal_names_the_field_on_the_form.py` — 34 tests.

Two things the guard caught in its own round. The field scan first read
`models.py` alone and reported 168 fields; the account models — `email`,
`password`, the whole sign-up form, which is the most person-facing surface
there is — live in `routers/accounts.py`. And the table's first draft carried
`grantee_name`, the sibling vault product's bequest field, copied across while
working in both repositories in one sitting: correct, translated into ten
languages, and on a field this product does not have. Both now fail a check.

Four injections: the sentence back to the identifier, a label for a field no
model declares, a row cut to three languages, and the refusal's wording drifted
from the form's.

## [0.40.7] — 2026-08-02

### The record that outlived the code

### The finding

`public_untranslated.txt` opened with a paragraph explaining that
`Onboarding.tsx` — the screen every person in the world meets first — carried
forty-odd English strings, that translating them was "its own round", and that
a half-translated sign-up form would be worse than an English one. All of that
was true when it was written.

`The screen everybody meets first` translated them. `The pre-session backlog
reaches its floor` took the count to four and appended its correction *below*
the stale paragraph, which nobody struck:

    What is left is not prose. A product name, a punctuation mark, an
    example address and an example code — strings that are the same in
    every language. This is the floor, not a backlog.

So the file held two statements about itself with the false one first. Read
top-down — which is how anybody reads a file — it advertised a cleared backlog,
and the correction was twenty lines further on. This round was planned off that
paragraph before the extractor was run and the work turned out to be two
releases old.

    asked     is the record complete
    mattered  does the record still describe the code

The numbers were right the whole time. The prose around them had outlived the
thing it described, and a record only works if a reader can trust the first
thing it says.

### Every ratchet now leads with what it is

`# status: floor|backlog — N rows`, on the first line, with the count checked
against the rows beneath it. `floor` means the remainder is permanent and is
not work; `backlog` means somebody still owes it. The two cannot be told apart
from the numbers — `console_untranslated` sits exactly at its ceiling with
1,459 strings still to translate, and `public_untranslated` sits exactly at its
ceiling and is finished — which is why the file has to say which it is, in a
line that cannot drift from its own contents.

A third check was written and struck before it shipped: *a file calling itself
a floor must sit exactly at its ceiling*. It fired on `native_untranslated.txt`,
which the last release took from three rows to none — a floor of zero under a
ceiling of three, and the best kind there is. `floor` is a claim about what the
remaining rows **are**, not how many, and a check that pretended otherwise
would have been one more guard answering the question next to the one that
matters.

### The reasons move next to the rows

`unused_native_bindings.txt` recorded two bindings whose justification lived in
the guard's module docstring — true, careful, and one file away from the list
it explained. A record whose justification is somewhere else reads, at the
place somebody actually looks, as an unexplained backlog: the shape this audit
found seven times in `0.40.5`. Every row now carries its reason on the row, and
a new check refuses one that does not.

### Changed

- `tests/test_a_record_that_outlived_the_code.py` — three tests, and the same
  file lands in all three products.
- `public_untranslated.txt` rewritten so the current state leads and the
  history is kept below it, labelled as history.
- `unused_native_bindings.txt`: one row per binding, reason after an em dash;
  `_recorded()` reads the name and `test_every_recorded_binding_says_why_it_is_recorded`
  refuses a bare row.
- Status lines on all five ratchets here.

Three injections: the stale paragraph put back above the status line, a status
count drifted from its rows, and a reason stripped back off a binding — each
caught by a different check.

## [0.40.6] — 2026-08-02

### The stranger's language, finished

Two rounds ago every shell learned to work out what language its reader speaks
without a profile — `Locale.preferredLanguages`, the system locale list,
`CurrentUICulture` — and the round stopped there, on purpose: twenty-odd
sentences on each of three screens was its own round, and half-porting them
would have been the per-client mistake in miniature. The remainder went into
`native_untranslated.txt`, which only shrinks.

This is that round. The accountless screen — the one a person reaches when they
have found a synthetic profile of themselves, or are holding a screenshot and
want to know whether a person wrote it — now speaks ten languages on iOS,
Android and Windows.

### Ported, not translated again

The console has carried these sixty-four `pub.*` rows in ten languages since
the browser's half was done. The shells took those rows rather than
commissioning a second wording of the same sentence: two wordings is two things
to keep in step, and the drift shows up first in the language nobody here
reads. Four keys are new, and all four name UI only a shell has — a sheet's
dismiss button, two client-side validation lines, and a placeholder.

The counts fell with it: **iOS 280 → 260, Android 195 → 181, Windows 279 →
262.** Windows fell furthest per screen because every one of its sentences was
a XAML attribute, which is written once at parse time and cannot be re-read
when the language changes; localizing them meant moving them to the code-behind
first.

### The ratchet was checking the record, not the screens

`native_untranslated.txt` held the line at three entries and only shrank — and
could have been driven to zero by deleting three lines, with all three screens
still in English.

    asked     is the backlog written down and shrinking
    mattered  did anything get translated

`test_no_accountless_screen_has_english_of_its_own` now reads the screens. It
borrows the sibling guard's extraction patterns rather than writing its own,
because two definitions of "an English string on a screen" is two numbers that
can disagree, and the disagreement would live in whichever one nobody reads.

### Changed

- 33 `pub.*` rows in ten languages added to each shell's `L10n` table, plus a
  `fill` helper: the console's rows carry `{id}`, `{now}` and `{matched}`, and
  building those sentences by concatenation instead is how a translation ends
  up in English word order in nine languages.
- `prior_status` added to `ObjectionOpened` on all three shells and
  `examined_windows` to Android's and Windows' `WatermarkRecovery` — both
  returned by the API since those routes shipped, neither modelled, and the
  console's sentences name them.
- Every one of the three screens resolves its language once, at the top, so no
  call site can quietly fall back to the profile's setting.
- Six new tests. Four injections: an English sentence back on one shell, a
  language taken from the profile, a string put back into XAML, and a row cut
  to three languages — each caught by a different check.

One literal is declared rather than translated: `prf_…`, the prefix of every
profile id, which is `prf_…` in all ten languages.

## [0.40.5] — 2026-08-02

### The door they closed was the owner's

Deletion in this product retires the owner's token. It retires nothing anybody
else holds, and every audit that walked up to a terminated profile through an
owner-gated route was told 401 and went away satisfied.

`POST /profiles/{id}/license/acquire` is authorised by the **buyer's**
interactor token, which termination never touches. Driven end to end against a
profile whose subject objected and whose objection was upheld:

    POST /objections/{id}/resolve   200  {"status": "upheld",
                                          "profile_status": "terminated"}
    POST .../license/acquire        201  the licence sells, the fee credits
    POST .../license/{g}/derive     201  a new profile, seeded from the
                                         erased persona, owned by the buyer,
                                         with its own owner token

    asked     can the owner still act on a terminated profile
    mattered  can anyone still act on it

The same hole one status over: a profile **restricted pending review** — the
one whose subject is arguing in that moment that it should not exist — could be
bought and cloned throughout the review. `succeed_profile` already refuses to
hand a contested identity to a new owner, and `has_open_objection` sits in the
same module for that check. Succession hands over the profile; derivation hands
over a *copy* of it, permanently, to a stranger, and never asked.

### The count

Seven tables carry a `profile_id` beside a revocation flag or a live token — a
capability somebody else holds over this profile. **Termination touched none of
them.** Not the licence, not the skill grant, not the handoff package, not the
paired wrist, not the voice consent, not the contribution log. `_terminate`
walked fourteen tables and its docstring is about *reachability*; on
reachability it was right, and capabilities were a list nobody had written.

### Changed

- `licensing.set_license`, `acquire_license` and `derive_agent` now call
  `common.require_may_publish` — 410 for a departed or terminated profile, 403
  for one under objection review. The gate at `derive` is the one that catches
  a licence bought while the source was active and cashed in during the review.
- `governance._terminate` revokes every capability a third party holds:
  `license_grants`, `grants`, `handoffs`, `contribution_log`, `voice_consents`
  and `wearables`, and takes the standing licence offer down with them.
- `tests/test_termination_revokes_more_than_the_owners_token.py` — eleven
  tests. The generalisation reads the schema rather than a list in the file, so
  a capability table added next release is in scope by construction; the one
  exemption (`referrals`) carries its reason, because an unexplained exemption
  is what seven ungated tables looked like.

A profile already derived under a licence bought while its source was active is
left alone: it is its buyer's profile, with its own owner and its own
provenance line, and tearing it down is a different decision from this one.

## [0.40.4] — 2026-08-02

### A memorial that kept posting

`POST /profiles/{id}/chat` has refused a departed profile for releases:

```python
if profile["status"] == "departed":
    raise HTTPException(410, "this profile has departed; its memory remains viewable")
```

`POST /profiles/{id}/compose` — which writes a public post in that profile's
voice and publishes it where anyone can read it — had no such check. Driven
against a profile that had been sunset:

    chat      410
    compose   201   ← and the post is publicly readable

`succeed_profile`'s own docstring calls that state **"frozen rather than
orphaned"**. It was not frozen. Nobody could talk to the dead; the dead could
still talk to everybody.

    asked     can somebody still talk to a departed profile
    mattered  can a departed profile still be made to speak

### The same hole, one status over

`open_objection` says it **"suspends the profile pending review"**, and the
sentence a restricted profile raises says it *"is not accepting new
interactors"*. Both true, and both about who may **start a conversation**. A
profile restricted pending an objection review — one whose subject is
contesting that it should exist at all — went on composing and publishing in
that person's voice throughout the review, which is the harm the objection was
raised to stop.

### The count

**Nine route handlers make a profile produce new words. Two checked its
status** — `chat` and `proactive_checkin`, the two whose subject is the person
on the *other* side. The seven that did not included the one that publishes.

The two gates that existed were the two whose docstrings were about a reader.
Nobody had asked the question the other way round.

### What was built

One gate, `common.require_may_publish`, that every generating route passes
through, with `chat` keeping its own extra nuance (a restricted profile may
still answer somebody it already knows). Departed and terminated answer 410;
restricted answers 403 with a new sentence — translated into the nine
languages rather than added to a backlog that stands at one by decision.

An organization is gated one level in, at `organization.coordinate`, because
it speaks as *each department's* agent and the route knows only the org.
Departments whose agent has departed, been terminated or is contested are
skipped **and named** in a new `silenced` field: dropping them quietly would be
this same defect one layer along, a joint plan reading as the whole
organization's while a dead agent is simply missing from it.

### The guard, and two things it did not catch at first

A structural check requires every route reaching a generator to gate. Two of
its own drafts were wrong in the shape this round is about:

* It credited a handler with its own status logic by searching the **module**
  rather than the handler, so every route in a file counted as gated if any one
  of them mentioned the status.
* The exemption for `organizations.coordinate` asserted that `coordinate`
  contains a status check *somewhere*. Deleting the per-department gate left
  the **initiating** department's check behind, and the injection passed.

      asked     does coordinate check a status somewhere
      mattered  does the loop check every department's agent

  It is scoped to the `for dept in departments` loop now.

## [0.40.3] — 2026-08-02

### The provenance named the model that was asked, not the one that answered

`content_provenance` is this product's central claim, and its own docstring
says so: *the verifiable basis of a piece of persona-generated content: which
model produced it ... so nothing the platform emits is a black box.*

It read the profile's **stored preference**:

```python
"generated_by": llm.resolve_choice(llm.get_choice(profile["id"])),
```

Meanwhile both network wrappers degrade rather than fail.
`llm.FallbackProvider` catches any exception from the primary and returns the
local stub's text, logging a warning. `cloud.CloudProvider` did the same and
did not even log.

So an owner sets their profile to Anthropic and brings their own API key. The
key expires. The next post is written by the stub on their own machine, stamped
`generated_by: "anthropic"`, watermarked, and published — and the only trace is
a log line addressed to nobody.

    asked     which model was this profile set to
    mattered  which model actually wrote this

**Degrading is still the behaviour.** A model outage should not take the
product down, and that decision has not changed. What changed is what the
platform then *says* about the result.

### The rule was already written down, in the other product

JIM-mini's `FallbackProvider` has carried it in its docstring for releases:

> The degrade is recorded on the instance (`answered_by`, `failure`) so a
> caller can tell the user the truth about who actually answered — **a log line
> the user will never read is not disclosure.**

The product that had the rule was the health app. The product that needed it
was the one whose premise is that generated content carries a trustworthy
account of where it came from.

### What was built

* A request-scoped record of who actually generated — the same idiom this
  module already uses for the caller's API key, chosen because every call site
  is `provider_for_profile(id).generate(…)`, built and discarded inline with
  nothing left to interrogate.
* Both wrappers record on **success and failure**. Recording only the degrade
  leaves a stale one describing a later answer that was perfectly good.
* `generated_by` now reports the truth, with `degraded_from` beside it —
  without that second field a record that suddenly says "local fallback" reads
  as somebody changing a setting rather than a credential going dead.
* The console shows it, in amber, on the chat surface. A record nobody can see
  is the same defect one layer up.

### The caller's own key never rides along

The reason for a degrade is now shown to the person and written to the log, and
it comes from an exception this codebase did not raise. Some HTTP clients put
the whole request — headers included — into the string form of their errors,
and on this path the interesting header is the caller's API key. `llm.scrub`
removes it before the reason is recorded or logged.

### The generalisation

A structural check requires that **every** `generate` answering a provider
failure with somebody else's text records who answered. Two such wrappers exist
today; the defect was that one of them was silent, so a check naming the known
classes would have passed while a third went on lying.

Its first draft read only dotted calls and reported the wrapper that had just
been fixed — `cloud.py` calls `llm.note_answered_by(...)`, `llm.py` calls its
own `note_answered_by(...)` unqualified.

    asked     does the handler call llm.note_answered_by
    mattered  does the handler record who answered

## [0.40.2] — 2026-08-02

### The refusals, finished

0.24.0 translated the eleven refusals any route can raise and **wrote the rest
down**. 142 sentences sat in `tests/refusals_untranslated.txt` from that day to this — the sentences
this product says when it says no, still English on an account that had chosen
otherwise.

An owner who set Portuguese got a Portuguese sidebar, Portuguese answers from
the model, and English the moment they were told no.


    asked     is the refusal translated
    mattered  is every refusal translated

All 141 are now in `_REFUSALS`, in the nine languages beside English. The
record is a decision rather than a backlog for the first time: one sentence, the `QRME_ADMIN_TOKEN` misconfiguration its own header
already argued should stay English, because the person who can act on it is
an operator and the fix is the name of an environment variable.

### What deliberately stays an identifier

Field names, header names, enum values and environment variables are not
translated and are not meant to read as words — `base_age, robot_id, QRME_PDI_URL, approve/reject`. They are the API's own
names, the same string in every language, and declining them into a sentence is
the half-in-one-language failure the table exists to refuse.

### The check that could not have caught a lie

`test_every_translated_refusal_has_every_language` asks whether each row has
all nine keys. A row whose nine values are the English sentence pasted nine
times satisfies it exactly — and the table would then claim the refusal is
handled while every reader still got English.

    asked     does every refusal have every language
    mattered  does every language say something other than the English

That gap was harmless while eleven rows were added by hand and reviewed one at
a time. It stops being harmless the moment 141 are added in one release, so
`test_no_refusal_is_translated_into_english` was added first and injected
against: an English value in one slot of one row fails it by name.

## [0.40.1] — 2026-08-02

### The objector could end a profile and could not read their own case

`GET /objections/{id}/audit` is owner- or reviewer-gated, and its docstring
gives the reason in its own words: *it can quote the objector's reason*. That
gate is right about the free text and wrong about who it locks out. **The
objector wrote that reason.**

And they were not a bystander to the case. `POST /objections/{id}/withdraw`
and `/revoke` are both public, and both **terminate the profile and erase its
content**. The one party on this surface with no account — a contested person,
sometimes a bereaved estate — could pull the lever and could not read the
record of having pulled it.

    asked     could the audit trail leak the objector's reason
    mattered  who is the audit trail for

**A second view, not a wider one.** `GET /objections/{id}/timeline` is public
and localized and carries event, actor, time, sealed — and no `detail` at all.
Not the objector's reason, not the reviewer's note, not the owner's. The shape
of what happened is theirs; nobody's prose is. The `/audit` gate is untouched
and `test_audit_is_owner_or_reviewer_gated` still passes.

### The two routes that end a profile did not speak the visitor's language

Of the four public routes on this surface, the two that merely open or read an
objection negotiated `Accept-Language`. The two that terminate a synthetic
profile of a real person answered `{"id": …, "status": "withdrawn",
"profile_status": "terminated"}` — three enum values and no sentence, in any
language. Both now carry a translated `note` and a pointer to the timeline.

`test_the_stranger_has_a_language_too.py` did not catch this and is not wrong:
it checks that the public *strings* are translated, and a route that produces
no sentence has no string to find.

    asked     are the public strings translated
    mattered  does every public route accept the visitor's language

### The language no client was sending

The half of the same defect that lives on the other side of the wire. The
routes above choose their language from `Accept-Language`. **No native shell
was sending that header** — not this product's, and not either sibling's. The
browser sends it unasked, which is exactly why the console looked correct and
the three clients a contested person is most likely to be holding were the ones
still answering in English.

    asked     can the shell say it in the reader's language
    mattered  does the reader's language ever reach the server

One line in each shell's request helper, sourced from the device resolver the
0.30.x rounds had already built and nothing had used.

### Doors

The timeline reaches the browser console, iOS, Android and Windows — event ·
actor · time, sealed where the vault holds the row, in ten languages.

### Two guards corrected after they passed something they should not have

* **Windows' localizer had one signature and now has two.** `L10n.T(key)`
  reads `AppState.Current.Language`, which is the profile's setting — the wrong
  answer on the one screen whose reader has no profile, reachable by writing
  nothing at all. A `T(key, lang)` overload was added, and the arity guard,
  which read the *first* declaration it found, failed six correct call sites.
  It reads every declaration now.

      asked     does every call match the signature
      mattered  does every call match a signature that exists

* **The new header guard used `any` where it needed `all`.** PDI's iOS client
  builds requests in two places — the shared helper and the intake submit its
  accountless recipient uses. Hardcoding `"en"` on one of them passed, because
  the other was still right. The union hid a surface inside the guard written
  to stop exactly that.

## [0.40.0] — 2026-08-02

> Staged as 0.30.10 and cut as **0.40.0**. The work below is unchanged; only
> the number moved, from a patch on the 0.30 line to a minor of its own.

### A rule reversed, and said so rather than changed quietly

`test_the_nav_is_translated_and_nothing_behind_it_is.py` records how many
English strings sit behind this console's forty-six translated sidebar labels.
It kept punctuation, under a rule written into the file in its own words:

> Whitespace-bearing strings are kept: `" · "` is a separator somebody reads.

That was a deliberate decision and it conflated two different things. A
separator is **rendered**; it is not **unreadable to a non-English speaker**.
There is no Portuguese for `·`, and none for `⚠`, `%`, `.` or `—` either.

    asked     is this string rendered to somebody
    mattered  is this string one a non-English reader cannot read

**117 of the rows in `console_untranslated.txt` were punctuation** — so the
count this file exists to state honestly was overstated by that much. The
ceiling is corrected from 1576 to **1459**.

The sibling product hit the identical thing one release earlier, in the shells,
where the extractor counted `"\(dim): \(n)%"` as English prose; 0.30.9
corrected that and this is the same correction one surface over. Twice now the
question has been *did the extractor find a string* when what mattered was
*did it find a word*.

### Nothing else changed here

The round's work is the sibling product's: a QRME specialist could be reached
from its monitoring path and not from its coach, so the person who typed a
question got a weaker answer than the person whose watch noticed something.
That fix is JIM-side. This repo carries the correction above and the version.

## [0.30.9] — 2026-08-02

### Two corrections carried in from the sibling's round

**A type-compatible argument swap, guarded.** JIM's Android client declares its
shared helper `request(path, method, body, token)`, and three calls in that
shell — plus one in PDI's — passed the verb first. Both arguments are `String`,
so nothing complained; the request went to `base + "GET"` with the method set
to a path. Two of them shipped in 0.30.7.

    asked     does the call have the right number of arguments
    mattered  does it have them in the right order

There is no Kotlin toolchain in this build environment, which is the whole
reason it sat there — the same reason forty one-argument `L10n.t` calls sat in
that shell before 0.30.7. `test_a_screen_nothing_opens.py` now reads the
helper's own declared signature and refuses an HTTP verb in the path slot.
This repo's Android client is clean; the guard is here because the surfaces
are the same three shells written the same way.

### Last release's untranslated counts were overstated

0.30.8 measured how much of each native shell is English behind a translated
tab bar. The extractor counted **any string literal containing a letter**,
which counted format fragments like `"\(dim): \(n)%"` — whose only letters are
variable names nobody reads — as English prose. Roughly seventy-five of them
across the nine shells.

    asked     does this literal contain letters
    mattered  does this literal contain words a reader reads

The ratchet caught it the honest way: by firing on a card in the sibling
product that had just been fully localized. A measurement that reports a
regression where an improvement happened is worse than no measurement.

Corrected figures for this product, now in `native_screens_untranslated.txt`:

| shell | was recorded | actually |
|---|---|---|
| iOS | 289 | **280** |
| Android | 205 | **195** |
| Windows | 326 | **279** |

The percentages in 0.30.8's table were computed the same wrong way and are
restated here: QRME 2.4% / 3.9% / 0.7%. The shape of the finding does not
change — these are still the worst three of the nine, and this product's
Windows shell still answers in the reader's language exactly twice.

## [0.30.8] — 2026-08-02

### The console guard, asked of the phones

`test_the_nav_is_translated_and_nothing_behind_it_is.py` has been in this repo
since the console rounds. It found forty-six translated sidebar labels in front
of 1577 English screens, and said why that is worse than shipping no
translations at all:

> A uniformly English console tells a Spanish reader the truth on the first
> screen they see. This one puts *Mercado*, *Amigos* and *Ajustes* in the
> sidebar — the app apparently answering in their language — and then hands
> them English the moment they click.

It checks `app/src`. This product also ships three native shells, all three
with a translated tab bar, and nobody had ever counted what is behind them.

| product | iOS | Android | Windows |
|---|---|---|---|
| **QRME** | **2.4%** | **3.8%** | **0.6%** |
| JIM-mini | 13.0% | 14.2% | 9.7% |
| PDI | 8.9% | 10.2% | 3.5% |

    asked     is the console's nav-vs-behind gap measured
    mattered  is the phones' too

These are the worst three of the nine. Last release recorded that this
product's Windows shell answers in the reader's language exactly twice — the
nav loop and one button — and left it standing rather than fixing it under
cover of a round about something else. This is that round: 289 iOS, 205
Android and 326 Windows strings, measured and ratcheted in
`native_screens_untranslated.txt`.

The ratchet runs both ways. The count may not rise, and the record may not sit
more than twenty above the real number — a ceiling nobody is near is a ceiling
somebody can drift back up into without it ever firing.

### Nothing is carved out here yet, and the record says which surface should be

The sibling product took its **alarm surface** off these numbers this release —
fourteen strings on all three of its shells, by name rather than by count,
chosen because that is where English is a hazard rather than a discourtesy.

This repo has no equivalent subset yet. The record names the candidate rather
than leaving the absence implicit: the **objection and audit** screens, where
somebody contests what a synthetic profile said about them. Those are
decisions, not descriptions, which is the same test the sibling applied.

### Every slot is now checked to survive its translation

A row whose English says `{name} was contacted` and whose German forgot the
hole renders a sentence with the person's name missing from the middle of it.
Nothing else would notice: the string is present, the language is right, and
the sentence is wrong.

Where a shell's table holds no slotted row — which is all three here today —
the check **skips loudly** rather than passing on an empty set. A check over
nothing is the failure mode this whole audit is named after, and a skip says so
in the run output where a green dot would not.

## [0.30.7] — 2026-08-02

### A guard ported before this repo needed it

`test_a_screen_nothing_opens.py` holds every screen a shell declares to being
reachable from somewhere in that shell, and every call to that shell's
localizer to the number of arguments the localizer actually declares.

The finding is the sibling product's: the synthetic-self screen shipped into
three shells with its wording in ten languages, unreachable in all three, and
on two of them written against a signature it did not have. A guard already
existed to check those strings were present. They were.

    asked     does the screen have its wording
    mattered  does anything open the screen

This repo's twenty iOS views, sixteen Android screens and seventeen Windows
pages are all reachable, and every localizer call matches its shell's
signature. That is why the port happens now rather than after something here
breaks — the last four rounds each turned up a guard covering one surface of
four, and the surfaces are the same three shells written the same way.

**Two false positives were fixed before the guard was kept.** The first
version required a screen to be constructed as `Name()` with no arguments, and
called `DeskView`, `SignatureView` and `VoiceView` unreachable — all three are
opened from `ManageView` with arguments. The second matched Kotlin composables
against a corpus containing their own `fun Name(` declaration, which makes
every screen its own caller.

    asked     is the name written anywhere
    mattered  is it written somewhere other than where it is defined

Comments are stripped before any of it. Twice already in this audit a check has
been satisfied by prose describing the thing it was looking for.

### One thing the port found here, recorded rather than fixed

This product's Windows shell makes exactly **two** calls to its localizer — the
nav loop and one button — where its iOS shell makes seven and its Android shell
eight. It renders nearly all of its chrome from XAML literals, so a German user
gets a German nav pane and English everything else.

That is a real gap and it is not what this release is about. It is written down
on `test_the_call_extraction_finds_something`, whose floor is set at two for
that reason: raising the floor to a comfortable number would have hidden it
inside the guard meant to notice things like it.

## [0.30.6] — 2026-08-01

### The plan gate speaks the reader's language

`refusals_untranslated.txt` carried this as an exception for four releases, in
its own words: a template whose slots were English prose, where translating the
frame alone would produce *"a sentence half in each language, at the one moment
in this product that stands between somebody and a decision to pay"*.

    asked     can the frame be translated
    mattered  can the slots be

They can. The capability descriptions and the billing period are a **closed set
this product authors**, so they are `i18n.Term`s with translations rather than
strangers — and `Term` is now exempt from the whitespace rule for exactly that
reason. The rule catches prose *nobody wrote a translation for*; an unmapped
`Term` still keeps the whole sentence English, so the exemption is paid for
rather than a hole.

The **plan titles** stay as they are. `Basic` and `Pro` are what the product is
called on the pricing page, in the console's tabs and on a receipt, and
somebody comparing a refusal against a price list needs the same word in both
places.

`Opening` capitalises **after** translation, never before: the vocabulary holds
one form of each phrase and each language raises its own first letter from it.
`str.capitalize()` was wrong here — it lower-cases the rest, which would have
flattened German's nouns.

### The console had the same defect one layer out

The card under the message repeated, in English, what the message says: the
plan you are on, the plan you need, the price, the period, and that billing is
simulated. It was written when `message` was English too, so the repetition
cost nothing — and the moment the sentence started arriving translated, it
became the only English left on that card.

    asked     is the refusal translated
    mattered  is what surrounds it

The duplicate is gone. The price and the simulated-billing disclosure are
adjacent **inside** the message — the invariant that card was built to keep —
now in ten languages rather than one, and the driven test asserts the pairing
inside the sentence rather than in the markup.

Seven injections, each caught by the right test. The seventh needed a new test
first: everything asserted the plan gate by calling `localize_detail` directly,
and every one of those passed while the handler's dict branch was dropping the
template on the floor.

    asked     does the module translate this shape
    mattered  does the request path reach the code that does

That test then failed for a second, correct reason — it sent `Accept-Language`
with an owner token, and the credential decides the language here.

## [0.30.5] — 2026-08-01

### The plan gate said HTTP 402

0.30.4 left the plan gate open as the one refusal deliberately not translated,
because its message interpolates prose. Going back to translate it turned up
something else first: on three of the four client families it was not arriving
at all.

`detail` has three shapes in this product — a **string** for most refusals, a
**dict** for the plan gate, a **list** for a 422. 0.30.3 gave the list a
top-level `message` and taught every client to read it. The plan gate's
`message` stayed nested inside its dict.

    asked     does the sentence ride beside the structure
    mattered  does every structured refusal put it in the same place

The three native shells look for a top-level `message`, then for a string
`detail`. A dict is neither, so the one refusal in this product that stands
between somebody and a decision to pay rendered as the bare status code: no
price, no plan name, no reason.

| Client | Before | After |
|---|---|---|
| iOS | `HTTP 402` | the sentence, with price and plan |
| Android | `HTTP 402` | the sentence, with price and plan |
| Windows | `HTTP 402` | the sentence, with price and plan |
| Console | correct | unchanged |

**One of those was a regression from 0.30.3.** Android had been coercing the
dict through `toString()` and showing its raw JSON — ugly, but it contained the
price. Teaching it to read the top-level key first is what dropped it to the
status code. iOS and Windows had always been broken.

**The fix is not a third special case.** Every refusal now carries a top-level
`message` holding the sentence a person reads, whichever shape `detail` is, so
a client never has to know the shape and a structured refusal added later
cannot repeat this. `detail` is untouched: the console still reads the dict to
draw the upgrade card with its price and button. `sentence_of` returns nothing
when there is nothing readable rather than inventing a sentence — a bare status
is more honest than one this codebase made up, and would be indistinguishable
from a real one.

Five injections, each caught by the right test — but the fifth needed the test
rewritten first. It compared the lifted sentence with the nested one on the
plan gate, whose message is deliberately untranslated, so both sides were the
same English string whichever order the handler used, and an injection that
lifted before localizing passed.

    asked     do the two copies agree
    mattered  is the lifted one the translated one

It now drives a message that is actually in the translation table, where the
wrong order produces a visible difference.

Still open, and unchanged by this: *translating* the plan gate. Its message
interpolates a capability description and a plan title, which are English
prose, and 0.30.4's mechanism refuses prose slots by design.

## [0.30.4] — 2026-08-01

### A refusal whose English is not a constant

`refusals_untranslated.txt` has carried the same paragraph for three releases:
f-string refusals, named as uncovered and deliberately not counted in the
backlog, because

    f"language must be one of {', '.join(SUPPORTED)}"

cannot be looked up by its English source — at the moment it is raised there is
no English source, only a result.

    asked     is the refusal a constant we can translate
    mattered  is every part of it something we can translate

`i18n.Templated` is a `str` whose value is the finished English sentence,
carrying the template and its slots so `localize_detail` can refill the frame
in the reader's language. Nothing that already treats a detail as text changed
— the default English path, JSON encoding, and every driven test asserting on a
refusal message all work exactly as before.

**The slot is the whole design.** A translated frame around an English slot is
*worse* than an English sentence: it reads as a bug, in front of somebody who
is already being told no. That is precisely why this record refuses to ship a
translated plan gate, and doing it here by accident would have been the same
mistake with a mechanism to spread it. So whitespace means prose, and a slot
that fails the test keeps the whole refusal English — the state it was already
in, now chosen rather than stumbled into.

The known limit is stated rather than hidden: a **single** English word has no
whitespace either, and is indistinguishable from an identifier.

QRME interpolates closed sets — an objection's `open | upheld | dismissed` —
so it carries a `Term` marker and a translated vocabulary, resolved at *render*
rather than at raise, because the reader's language is not known where the
refusal is raised. An unmapped word keeps the refusal English too, which makes
coverage structural instead of a list somebody has to remember to update.

**18 of 49 sites converted**; the record now names the reason per site rather
than "f-string". Seven of the remaining 31 carry prose this product does not
author — a mail server's exception, a moderation verdict, a hardware
availability string — and no mechanism changes that.

**Two of my own checks asked the wrong question and were caught by their own
subjects.** The slot pattern was first written as a character allowlist, which
quietly meant ASCII: Devanagari writes its vowels as combining marks, which are
not `\w`, so every Hindi word in the vocabulary failed a rule written to catch
English sentences. And the vocabulary check asked whether each translation was
a single token, failing on `वापस ली गई` and `تم التسليم` — correct translations
that happen to be two words.

    asked     is this translation a single token
    mattered  is this translation not still English

Six injections, each caught by the right test — including the `Templated`
branch placed below the plain-string branch, which would have looked up the
finished sentence, found nothing, and returned English indistinguishably from a
sentence nobody has translated yet.

## [0.30.3] — 2026-08-01

### The refusal that arrived as a list

0.30.1 put the 422 into the reader's language — the refusal a mistyped form
produces, and the one a person meets most often. Nothing looked at what a
client does with the result.

`detail` on a 422 is a *list* of pydantic rows, and every client family
rendered it by a path written for a string. The console called
`JSON.stringify` on it, so the note under a form read
`[{"type":"missing","loc":["body","display_name"],"msg":"Field required"}]`.
Android's `JSONObject.optString` coerces a `JSONArray` through `toString()`,
producing the same. iOS asked for `as? String`, got `nil`, and fell back to
`HTTP 422`; Windows called `GetString()` on an array, which throws, was
caught, and did the same.

    asked     is the refusal translated
    mattered  is the refusal a sentence

The `msg` translated last release was correct, arrived, and was read by
nobody: it sat inside a JSON blob or was discarded for a status code. Two of
the four families showed the person **less** than before their language was
ever considered.

**The fix.** `i18n.validation_message` composes one sentence from the rows, in
the reader's language, and rides beside `detail` rather than replacing it —
`detail` is the FastAPI contract, what a machine reading this API has a right
to, and what the driven tests read. Every client decode now reads the sentence
first. The field name stays the API's own (`display_name`), joined with an em
dash rather than declined into the sentence, so nothing comes out half in one
language and half in another. Mapping those names to the labels a form
actually shows needs a per-client table that does not exist, and is recorded as
the remaining gap rather than guessed at.

**The guard took three attempts, and the first two are why the third is worth
having.** Asking whether a client's source mentions `message` passed on all
four clients while all four were broken — it is a field on a model, a
parameter name on an exception class, and a word in the comment directly above
the bug. Anchoring on the throw and asking whether the surrounding lines read
it caught the three shells and still passed on a broken console, because the
fallback chain has always read the sentence key as an *alternative to*
`detail`.

    asked     does the decode mention the sentence
    mattered  does the decode pass the sentence on

Seven injections, each caught by the right test with the right message.

**The shape that walked past a fix it already had.** QRME's console met this
exact problem in an earlier round and solved it — for the plan gate, whose
refusal is an *object* carrying its own `message`. A list is an object with no
`message`, so the 422 fell through to the `JSON.stringify` written for the
unhandled case.

    asked     does a structured refusal reach the reader as a sentence
    mattered  does every structured refusal

`test_gates_answer_in_a_shape_a_screen_can_use` pinned the exact two-argument
spelling of that call and fired when a third argument was added to carry the
sentence. Loosened to a prefix match, which is what it meant — the structure
still rides out unflattened — and re-injected to confirm it still catches the
regression it was written for.

## [0.30.2] — 2026-08-01

### The synthetic self enters the tandem contract

`docs/tandem.md` gains the boundary before the code that obeys it, and this
release carries the amendment that names the one exception to it. The
implementation is JIM-mini's; the contract is shared, byte-identical in all
three repositories, and it is QRME's `self` profile the whole section is about.

Everything the contract described linked JIM to *somebody else's* profile, and
the JIM user reached QRME as an **interactor** — a stranger. `ProfileKind` is
`self | other_person | fictional | hybrid` and a `self` profile speaks *as* the
person; JIM had no column, module or route that knew it existed, and QRME held
nothing pointing back.

    asked     does JIM reference synthetic profiles
    mattered  does JIM reference this person's own

An owner token, not an interactor token. The link refused unless QRME reports
`kind == "self"` — a `fictional` profile briefed with somebody's medication
schedule is a different product with the same code. JIM → QRME is an enumerated
allowlist, consented per category, empty by default, with the composer building
the brief *from* the allowlist rather than filtering a payload down to it.

**The amendment.** Journal entries, check-in notes and transcripts never cross
under any consent. The one category made of the person's own words is
**medication**, and it is named in the contract rather than hidden in an
implementation: `meds.py` invites their wording, so names are free text by
design, and *"the pill for my HIV"* is a diagnosis typed into a field asking
for a drug. Consenting to that category is consenting to a self-profile that
can be asked about those strings by anyone it talks to — which is why the
preview shows the strings and not a count of them.

The brief arrives through QRME's own owner-gated
`POST /profiles/{id}/sources`, so it lands where the persona is grounded and is
sealed into PDI when a vault is configured.

## [0.30.1] — 2026-08-01

### The refusal that handed the body back

The round in 0.30.0 put every refusal this product *writes* into the reader's
language, through one handler no raise site opts into. It missed every refusal
this product *returns*.

    asked     is every refusal this product writes translated
    mattered  is every refusal this product returns

`RequestValidationError` is not an `HTTPException`. FastAPI raises it before
routing finishes and renders it with its own handler, so a 422 — the refusal a
person meets most often, because it is what a mistyped form produces — went out
past a handler written to catch everything.

**The larger half is what it carried.** Pydantic's error rows hold an `input`
key with the value that failed, and for a missing field that value is the
entire submitted body. Driven against the siblings: JIM returned a journal
entry about chest pain, PDI a record value in plaintext on the one path in an
encrypted vault that never touches the encryption layer.

Every other part of this ecosystem's error design refuses to carry content.
`errors.ts` and the nine `Problems` modules record a method, a redacted path
and a status, and have no parameter a message could arrive through. `cloudgw`
refuses a report whole if it finds prose in it rather than sanitising it. The
one place content left the process was the framework's default renderer,
because nobody had looked at it as ours.

    asked     does this product record anything private
    mattered  does this product return anything private

**What this is not:** disclosure between people. A 422 goes back to whoever
sent the request, so what came back was the sender's own body, and no stored
record was exposed. **What it is:** content on an error path, travelling
through whatever sits between the app and the person — a proxy's access log, a
HAR export on a support ticket. A posture with one documented exception is a
preference.

`type`, `loc` and `msg` are returned; `input` and `ctx` are not, built as an
allowlist so the response cannot grow a leak by somebody else's release.
`value_error` and `assertion_error` messages are replaced outright: a validator
that quotes the value it rejected is the same leak wearing a different key.

On `extra_forbidden` the key is echoed only when it is *shaped* like a field
name. The first version replaced it always, and
`test_a_write_that_answers_200_did_something` failed by name — two routes there
used to accept `dials` for `values` and `years` for `period`, discard them and
answer 200, and a round was spent making them strict so the caller is told
which key was wrong.

    asked     can a key carry content
    mattered  does this key look like content

The guard does not check for the `input` key — that would test the name of the
leak rather than the leak. It posts a canary at every body-taking route from
`all_routes` and fails if it appears anywhere in the response; before the fix
it named **124 routes**. A second check asserts how many of those reached
validation at all, because a sweep of two hundred routes that all 404 first is
a spotless report about nothing.


### The synthetic self enters the tandem contract

`docs/tandem.md` gains the boundary before the code that will obey it.

Everything the contract described linked JIM to *somebody else's* profile, and
the JIM user reached QRME as an **interactor** — a stranger. `ProfileKind` is
`self | other_person | fictional | hybrid` and a `self` profile speaks *as* the
person; JIM had no column, module or route that knew it existed, and QRME held
nothing pointing back.

    asked     does JIM reference synthetic profiles
    mattered  does JIM reference this person's own

An owner token, not an interactor token. The link refused unless QRME reports
`kind == "self"`. JIM → QRME is an enumerated allowlist, consented per
category, empty by default, with the composer building the brief *from* the
allowlist rather than filtering a payload down to it — and no free text from
the user crossing at all. Byte-identical in all three repositories.

## [0.30.0] — 2026-08-01

### Forty-six translated labels, forty-six English screens

QRME's sidebar answers in the reader's language: forty-six `nav.*` keys, ten
languages each, built by ``t(`nav.${n.id}`, lang)``. Behind those forty-six
labels are forty-six screens, and every string on all of them is English —
**1576 of them**, now recorded in `tests/console_untranslated.txt` and
ratcheted.

    asked     is the chrome localized
    mattered  is anything behind the chrome localized

`l10n.ts` declares its own scope in its first line — "chrome localization for
the desktop console" — and three rounds of language audit read that sentence as
a boundary rather than as the thing to question. Each widened correctly inside
it: `Public.tsx`, then `Onboarding.tsx`, then the native shells. Each ended
green.

This is worse than a console with no translations at all, which is why it is
recorded separately rather than folded in. A uniformly English console tells a
Spanish reader the truth on the first screen. This one puts *Mercado*, *Amigos*
and *Ajustes* in the sidebar and hands them English the moment they click —
and the backend already answers in the profile's language, so the model replies
in Portuguese inside a frame that cannot.

The structural half is `test_the_two_records_partition_the_console`. Both
language records now derive their screen sets from `screens/` and must together
cover it exactly: none in both, none in neither. A screen added to this console
lands in a count whether or not anybody remembers these files exist.


### The persona speaks it everywhere; the platform spoke English

`qrme/i18n.py` opens with "the persona speaks it everywhere", and it does — the
directive rides on the system prompt, so every generation site inherits it. The
product's own sentences were another matter. An owner who set Portuguese got a
Portuguese sidebar, Portuguese answers from the model, and English on all 153
of its refusals.

`common.refusals_in` was added in 0.24.0 for the four accountless routes, and
its docstring wrote down why the owner routes were left out:

> `profile_or_404` and its siblings are shared with every owner route and say
> "profile not found" in English, which is right there — the owner picked that
> language

The owner did not pick that language. They picked one, it is in
`language_prefs`, and English is what they get when they picked English. The
justification for the scope **was** the defect.

    asked     did the caller state a language
    mattered  did the profile

One exception handler on the app, for the reason the membership gate is one
dependency: a sentence cannot be added to the product and forgotten at a raise
site, because no raise site opts in. `refusals_in` is gone — two paths
translating one sentence are free to drift.

Two ways this could have been wrong and still passed, both now driven.
**Whose language:** reading the `profile_id` in the path answers a stranger in
the language of the person they are asking *about*; reading `Accept-Language`
takes `en-US` from a console owner's browser whatever they set in the app. The
credential names the reader. **Which stored value:** `effective_language`
returns English whenever the mode is `on_demand` — a statement about the
persona's voice, not about what the owner reads.

Eleven sentences translated into all nine; **142** recorded in
`tests/refusals_untranslated.txt` and ratcheted, with the 49 f-string refusals
and the plan gate named in the header as classes the file does not cover.

## [0.29.0] — 2026-08-01

### The deploy that lived in a chat log

`docs/cloudgw-deploy.md` — the gateway from a bare host to installers that
actually report, with the two build-time variables that are the point of the
exercise.

It says in its first line what has and has not been proven. The routes, the
refusals, the token scopes and the fail-closed defaults were all driven
against a running instance; **the image build was not**, because the sandbox
it was verified in has no Docker daemon. A runbook that does not distinguish
those two is a runbook that will be trusted in the wrong place.

It also states what the box does not buy: counters cannot reproduce a bug, and
they cannot reach installers already in the field, because the address is
compiled in.


### A translated string nobody reads

Two keys shipped in 0.27.0 were in the table and wired to nothing — caught by
hand last release. `test_no_key_is_translated_into_ten_languages_and_used_
nowhere` now catches the class, here and in JIM, where eight more turned up.

    asked     is every key in the table complete
    mattered  does every key in the table reach a screen

Every completeness check in both repositories asks whether a key *has* its ten
languages. None asked whether anything looks it up, so a translated string can
sit beside the English it was supposed to replace with nothing to say which
one a reader gets.

The first version of the check read literal keys only and reported all
fifty-three `nav.*` keys as dead. Every one is live — `App.tsx` builds them,
`` t(`nav.${n.id}`, lang) `` — so a guard against dead translations would have
had somebody delete the working ones. It now understands a built key's literal
head.


### The pre-session backlog reaches its floor

37 → 20 → **4**, and the four are a product name, a full stop, an example
address and an example verification code — strings that are the same in every
language. `public_untranslated.txt` now says so in its header: this is a
floor, not a backlog.

Two keys added last release were in the table and wired to nothing — the
tagline and the password-mismatch warning. They had been translated into ten
languages and no screen looked them up, so the strings stayed English while
the table said otherwise. The round that localized the form localized most of
the form and stopped, which is the same shape as the round two releases ago
that localized the door and stopped at the sign on it.

Fourteen more keys and the wiring for all of them, including the two dead
ones. Four strings were missed on the first pass because JSX had wrapped them
across source lines — a substitution matching a single line finds nothing and
reports success.

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

[Unreleased]: https://github.com/davidsbianchi1984/qrme/compare/app-v0.77.0...HEAD
[0.77.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.77.0
[0.76.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.76.0
[0.75.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.75.0
[0.74.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.74.0
[0.73.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.73.0
[0.72.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.72.0
[0.71.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.71.1
[0.71.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.71.0
[0.70.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.70.1
[0.70.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.70.0
[0.61.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.61.1
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
