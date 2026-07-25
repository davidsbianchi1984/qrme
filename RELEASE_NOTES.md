# QRME v0.1.6 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.6` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.1.6** — the release about telling the truth in both directions. A
synthetic profile now carries the AI mark in its own pixels, so it survives
being screenshotted or hotlinked; and a **live desk** — an actual person
behind a counter — carries no mark at all, because stamping "AI" on a real
human is a false statement about them. One of three interoperating products
(with [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Highlights

- **Live desks, and a bell you can reach.** A real person offering a service,
  behind the same surfaces as a synthetic profile and with the one difference
  that matters: **a desk never carries the AI watermark.** Absence alone would
  be ambiguous — an unmarked card could be an AI whose badge got dropped — so
  the claim is positive (*Live person — not AI*) with the attestor, the basis,
  and the word **recorded** rather than *proven* shipped beside it. A desk
  cannot be opened without saying who vouches.
- **What a visitor looks at is the desk, not a portrait.** We have no
  photograph of the person and do not go looking for one; the surface is a
  camera view of their own counter. An empty chair with a sign on it says
  everything, and it depicts nobody. Without a camera configured the card
  reports `live: false` and the apps say **SAMPLE VIEW** — a still frame
  presented as live would be the same class of lie.
- **The sign says ring the bell, so the button is on the screen.** iOS,
  Android and Windows all carry it. No token: the person in front of an empty
  chair is exactly the one without an account. Rate limited, because a bell
  anyone can ring from anywhere is a doorbell prank waiting to happen.
- **18+ streams** are the same desk behind the deployment's *existing*
  verified-adult gate — not a new tier and not a second, weaker check.
  Unverified callers get an age wall carrying existence and nothing else; the
  location stays withheld even past it. Only the performer can open one,
  because the standing rule that adult mode is never available for a profile of
  another real person lands here as *the attestor must be the owner, attesting
  for themselves*.
- **Signatures that survive being disputed.** The same Face ID gesture through
  WebAuthn/passkeys, returning an assertion signed in the Secure Enclave over a
  challenge that **is** the document hash. Change one byte and it stops
  verifying. iOS/visionOS and Android drive the ceremony; Windows reads and
  verifies but does not sign, because reaching Windows Hello means interop a
  compile cannot meaningfully check and a button that looks like it signs and
  does not is worse than no button. ESIGN/UETA grade, with 21 CFR Part 11 as a
  configuration change — HIPAA does not require Part 11, and that confusion is
  expensive.
- **The AI mark is in the pixels.** All 34 starter portraits carry it burned
  in, top-right, where every composited badge sits bottom-left so the two never
  collide. `/portraits/{handle}.webp` is an ordinary file URL — hotlink it,
  embed it, screenshot it, and a composited badge survives none of that. Pinned
  by a SHA-256 manifest the test suite checks, so an unmarked replacement fails
  CI rather than shipping quietly.
- **Beacons you can read without leaving the camera.** Point the iOS or Android
  app at a sticker and the profile is drawn *on the code* in the live
  viewfinder. A stock camera app can only open a URL — that is the whole API
  surface a QR exposes to a third party — so the landing page from v0.1.5
  remains the best possible version of that, and this is the one that doesn't
  need it.

### Fixed

Three things a pre-release audit turned up, all of them features that looked
finished and could not work:

- **The signing flow in both mobile apps could never succeed.** They enrol at
  `self_asserted` and then asked for the `standard` tier, which needs better
  proofing. Every attempt died at the server. The tests missed it because they
  all enrol at `document` level, so none walked the sequence the clients
  actually perform.
- **A credential's proofing level could never change**, despite the spec
  promising exactly that. `POST /signatures/credentials/{id}/proofing` records
  a fresh check — going forward only, never rewriting what was already signed.
- **A desk's camera could never be turned on.** `feed.live` read a column no
  endpoint could write, so the live branch was unreachable.

### Verification

425 tests green. Both front-ends build clean. iOS, Android and Windows all
compile in CI.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.1.6` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
