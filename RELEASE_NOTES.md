# QRME v0.1.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.1.0** — the first public release of the AI synthetic-profile platform,
one of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

QRME lets you create, customize, and interact with AI-driven synthetic profiles
— of yourself, of another person (with consent/rights handling), or a fictional
persona — that adapt to *who* they're talking to and *how engaged* that person
is, while keeping identity and boundaries fixed.

### Highlights

- **Profiles & relationships** — self / third-party (consent-gated) / fictional
  profiles; relationship-aware behavior and engagement-based style adaptation
  that never moves identity or boundaries.
- **Memory & moderation** — per-relationship memory; every reply moderated, with
  an optional owner approval queue.
- **Full lifecycle** — aging, succession, memorial state, graceful sunset, and a
  complete objection / takedown / appeal flow.
- **Summoning** — `@handle`, `#tag`, and QR beacons.
- **Marketplace & licensing** — listings, ownership transfer, training-data
  licensing, derivable specialist agents.
- **Cloud model** — optional greater-model gateway with local fallback and
  opt-in, revocable contributions.
- **You own it** — full export and complete erasure any time; tokens stored only
  as SHA-256 hashes.
- **Suite** — one origin fronting all three products, unified sign-on, and a
  cross-cutting control plane (suite-wide erase, export, consent, usage).
- **Apps** — runnable desktop console + suite launcher; this release attaches
  per-OS installers built and (optionally) signed in CI.

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
the backend from source — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
