# QRME v0.1.4 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.4` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.1.4** — run it your way: one command prints every way to run
QRME and you pick the device — your phone (scan a QR straight off the
terminal), this PC, a packaged installer, or the headless API. One of
three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Highlights

- **Run it your way — `python -m qrme`** — the launcher menu prints every
  way to run QRME, one command each, so you pick per device: `phone` (the
  QR flow below), `desktop` (the Electron app on this PC), the packaged
  installer (no toolchain needed), or `serve` (the headless API alone).
  `python -m qrme phone` does the whole phone setup in one command —
  builds the studio if missing, prints the pairing URL **with a QR code
  drawn straight into the terminal**, and serves on your local network.
- **Run it on your phone** — the API serves the built studio at `/app`
  (one origin for UI and API — nothing to configure on the phone);
  `GET /pair` returns the URL on your local network with a scannable QR,
  and the studio installs to the home screen as a standalone app with a
  thumb-reachable bottom tab bar. Local network only, by design.
- **Watermarking on every AI render** — all AI-generated work, textual or
  visual, is stamped at creation with a verifiable synthetic-media
  credential: chat turns (including proactive check-ins and farewells),
  public posts, room turns, game and robot comms lines, creative works,
  proofreads, perception guidance, task outputs, and voice/image/video
  modalities. Anyone holding a piece of content can verify it —
  `GET /watermarks/{id}` resolves the credential and
  `POST /watermarks/verify` catches altered or substituted content.
- **Owner-designed watermarks, displayed at all times** — each profile's
  mark + label (`PUT /profiles/{id}/watermark`, design editors in all
  three native apps) rides on every render; the AI designation is
  invariant and cannot be designed away. Chat bubbles and post cards in
  iOS, Android, and Windows show the mark.
- **Terms of Service** — docs/terms.md served versioned at `GET /terms`:
  assumption of risk and release, no-professional-advice and emergency
  disclaimers, warranty disclaimer, liability cap, indemnification,
  creator responsibilities, 18+ terms, and the simulated-commerce notice.
  Profile creation is clickwrap with a server-side receipt (version +
  timestamp recorded); refusal is refused (403); all three apps display
  the agreement at the create screen.
- **Signed, notarized builds wired** — hardened runtime + entitlements +
  notarization in the electron-builder config: adding the Apple/Windows
  signing secrets produces Gatekeeper-clean, SmartScreen-friendly
  installers. docs/releasing.md walks through obtaining the certificates.

### Verification

Backend suite green (QRME 270 tests); live-server smoke flows pass; the
front-ends build clean; static native checks (XAML/SVG parse, brace
balance, brush audit) are clean across iOS/Android/Windows sources.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.1.4` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.
