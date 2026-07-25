# QRME v0.2.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.2.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.2.0** — the minor bump, and honestly: **there are no functional
changes to QRME in this release.** The three products version as one, and this
round's work was next door. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version.

### Why 0.2.0 rather than 0.1.10

The 0.1.x line ran from a profile you could talk to, to a suite where all three
products put printed codes on physical things and answer a stranger's phone
with a page rather than JSON — desk beacons, care beacons, custody beacons, an
agent at a facility gate that can speak but cannot decide, a marketplace you
can search in words, and an escalation path in each product that reaches an
actual human. That is a different product from 0.1.0, and 0.1.10 would have
undersold it.

### What changed here

- **Only one workflow writes the release body now.** `desktop-release.yml`
  published `RELEASE_NOTES.md` **verbatim** — *"Ready-to-paste body for the
  GitHub Release…"* preamble and all — while `sync-release-notes.yml` published
  the same file with that preamble stripped. Both fired on the same tag push;
  the sync finished in six seconds and the installer build finished two to four
  minutes later and overwrote it. The build always won, so every release since
  the sync workflow existed shipped the preamble until somebody re-ran the sync
  by hand. The build no longer sets a body at all, and the sync now waits for
  it rather than racing it.

### What changed in the siblings

- **PDI** — a per-tenant on-call roster. `PDI_GATE_ONCALL` was one name for the
  whole deployment, which in a multi-tenant vault routed every customer's
  courier to the same person.
- **JIM-mini** — nothing of its own this round.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent: spend
totals, cooling-off, parental controls, a real identity check behind "verified
adult", chargebacks, payout compliance. If you wire a real processor to these
endpoints, that list is the work remaining.

### Verification

523 tests green — the same 523, passing the same way, which is the point of a
release that claims no functional change here. 192 routes. Both front-ends
build clean, and iOS, Android and Windows all compile in CI.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.2.0` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
