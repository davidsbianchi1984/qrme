# Changelog

All notable changes to QRME are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

[Unreleased]: https://github.com/davidsbianchi1984/qrme/compare/app-v0.1.0...HEAD
[0.1.0]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.1.0
