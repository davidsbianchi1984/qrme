# QRME v0.1.2 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.2` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.1.2** — the trust release: everything the platform generates is
watermarked and verifiable, users accept real terms with a receipt, and
signed/notarized builds are wired. One of three interoperating products
(with [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Highlights

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

Backend suite green (QRME 259 tests); live-server smoke flows pass; the
front-ends build clean; static native checks (XAML/SVG parse, brace
balance, brush audit) are clean across iOS/Android/Windows sources.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.1.2` tag), or run from source —
see the README's Quick Start.
