# QRME v0.1.9 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.9` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.1.9** — a documentation release for this repository, and a real one
for its siblings. The shared architecture doc had quietly stopped describing the
architecture, and the three copies of it had stopped agreeing with each other.
One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Highlights

- **The tandem doc was missing an arrow.** For most of this project's life the
  topology fit in one sentence: every arrow points *into* PDI, because PDI is
  the bottom layer and a vault whose availability depends on a model provider is
  a worse vault. PDI's gate agent broke that on purpose — it asks a QRME profile
  for the words it speaks to somebody standing at a facility door — and the
  document, its diagram and its section headings all still described the world
  before that. [docs/tandem.md](docs/tandem.md) now has a `pdi ✕ qrme` section:
  the flow, the fallbacks, and why the model is the voice and not the decider.

- **Two of the three copies were describing a past release.** JIM's and PDI's
  still listed the suite gateway's erase, export, consent and metering as
  `[planned]` when `suite/gateway.py` had shipped them, and the docker-compose
  end-to-end harness as planned when it runs in CI. A reader in either repo was
  told cross-app deletion did not exist. The three copies are byte-identical
  again, and the test counts it cited (*QRME 59, JIM 49, PDI 20*) are now the
  real ones.

- **The beacon family is written down as a family.** Three products now put a
  printed code on a physical thing and answer three different questions with it
  — a profile, a person somebody watches over, custody of data. The shared rules
  were true in three places and recorded in none: a scan is a page and not JSON;
  a dead code and a code that never existed render identically; the page renders
  only what the server handed it, so it cannot disclose what the card withheld.

- **The diagram is generated.** `tools/build_assets.py` writes
  `docs/diagrams/tandem-flow.svg` from a block that is identical in all three
  repositories, so one picture cannot become three that disagree. It replaces a
  hand-drawn SVG that was cream-and-serif while every other asset in every repo
  is night-indigo — and that showed two arrows, because it was drawn when there
  were two.

### What changed in the siblings

This release's functional work landed next door, closing the two gaps both
escalating beacons had been carrying:

- **PDI** — a gate hand-off now reaches a person. It used to record the on-call
  contact's name and tell nobody, so somebody could stand at a door at 2am
  waiting for someone who did not know they were there.
- **JIM-mini** — `JIM_SITE_ROSTER` became a rota that knows who is on *now*,
  and an escalation now actually sends something. A flat list pages the day
  person at 2am, which is the feature failing in the hour it was built for.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent: spend
totals, cooling-off, parental controls, a real identity check behind "verified
adult", chargebacks, payout compliance. If you wire a real processor to these
endpoints, that list is the work remaining.

### Verification

523 tests green. 192 routes. Both front-ends build clean, and iOS, Android and
Windows all compile in CI.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.1.9` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
