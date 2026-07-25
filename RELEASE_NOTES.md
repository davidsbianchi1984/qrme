# QRME v0.1.5 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.5` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.1.5** — leave a profile somewhere. A QR sticker on a wall, a
card on a table: someone points a phone at it and meets a synthetic
profile, right there. This release makes that scan land somewhere worth
landing, lets a code open into a room several people share, and — in the
iOS app — draws the profile **on the sticker itself**, in the live camera.
One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Highlights

- **Beacons land on a page, not on JSON.** A beacon's QR used to point at
  `/summon?ref=…`, so a stranger who scanned a sticker got a wall of braces.
  `GET /b/{beacon_id}` is the page that should have been there: one
  self-contained document — inline CSS, no scripts, no font fetches, because
  it opens in a camera app's in-app browser, on cellular, from a cold start —
  with the portrait rising into view and exactly one way in.
- **The AI mark is on the portrait, not in the chrome.** Someone in the studio
  knows they are looking at a synthetic profile. Someone who scanned a sticker
  in a bathroom stall does not, and if they screenshot it the disclosure has
  to travel with the image. A picked-up beacon says so plainly rather than
  erroring, and a rated profile shows an age wall that carries no name and no
  face.
- **Shared-room beacons.** Placed with `mode: "room"`, one code puts everyone
  who scans it into the *same* conversation rather than each into a private
  thread — a class, a workshop, a shop demo, a meeting. The page says "others
  may be here" before anyone types, because that is not something to discover
  afterwards.
- **See who it is without leaving the camera.** Point the QRME iOS app at a
  beacon and the profile appears *on the sticker*, in the live viewfinder:
  Vision reads the code, `GET /b/{beacon_id}/card` answers, and the portrait is
  drawn on the quadrilateral Vision reported so it tracks the sticker as the
  phone moves. The AI mark comes from the same payload as the face and is drawn
  in the same view, so the two cannot come apart. A rated beacon's card carries
  `age_wall` **alone** — no name, no portrait — since an overlay renders
  whatever it is handed.
  - Worth being exact about the boundary: a **stock** camera app can only open
    a URL. That is the entire API surface a QR code exposes to a third party,
    and no app can change it. Drawing over a viewfinder means owning the
    viewfinder. `docs/beacons.md` lays out all three tiers, including the App
    Clip Card path, which needs an Apple Developer account to configure.
- **`docs/beacons.md` — where to put them.** Placement paired with starters: a
  music instructor's card at the shop counter, a nutritionist in the produce
  aisle, a fitness coach at the gym, a sponsor at a meeting, a finance guide at
  the bank. Any profile, any industry, any user's choice.
- **The native apps are compiled in CI.** Until this release the Swift, Kotlin
  and C# in `native/` had never been through a compiler at all — they were
  checked by reading and by brace/XML well-formedness, which catches a typo and
  nothing else. iOS via XcodeGen + `xcodebuild`, Android via `gradle
  assembleDebug`, Windows via Visual Studio's **MSBuild** (not `dotnet build`:
  the Windows App SDK's PRI packaging task ships with VS and is absent from the
  standalone .NET SDK at every version). It found five real defects on its
  first runs, and all three steps now re-surface the actual compiler
  diagnostics on failure instead of a bare exit code.
- **The Cloud Model Gateway server** (`cloudgw/`, `python -m cloudgw`) — the
  other end of a contract that until now had only clients and fakes. One
  operator-configured model, which says so in `/v1/model` and `/health` rather
  than passing a stub off as a hosted tier; a bearer token per contributing
  deployment; fail-closed off-machine. Contributions seal into PDI as an
  ordinary tenant, and with no vault configured they are **refused** rather
  than written somewhere unencrypted — while inference keeps working. The
  intake screens for identifying fields at any depth and answers 422 naming the
  field instead of quietly stripping it, because a quiet strip hides the client
  bug that leaked it.
- **Deployable as one container, and published deployments.** A two-stage
  `Dockerfile` builds the studio and installs the API into one image, serving
  UI and API from one origin. `QRME_PUBLIC_URL` makes `GET /pair` advertise the
  public address so the phone flow works hosted or local from one code path,
  and `QRME_SIGNUP_KEY` keeps a published instance the operator's rather than
  open registration — talking to a profile stays public either way.
  [docs/hosting.md](docs/hosting.md) states what the deployment does *not* give
  you: no multi-tenancy, no rate limiting, no backups.
- **Profile portraits and the starter collection.** `GET /profiles/{id}/avatar`
  returns asset, AI watermark and likeness record as one shape, so 2-D, 3-D, VR
  and AR surfaces composite the badge rather than deciding whether to. An
  invented likeness reports no rights holder; a real person's face reports the
  recorded grant, its attestor, and that it is revocable.

### Verification

350 tests green. Both front-ends build clean. The native compile gate is green
on all three platforms — including the camera overlay's first ever compile,
which landed green.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.1.5` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
