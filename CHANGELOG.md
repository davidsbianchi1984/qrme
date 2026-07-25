# Changelog

All notable changes to QRME are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

[Unreleased]: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.6...HEAD
[0.1.6]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.6
[0.1.5]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.5
[0.1.4]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.4
[0.1.3]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.3
[0.1.2]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.2
[0.1.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.1
[0.1.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.0
