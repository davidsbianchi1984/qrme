# QRME v0.4.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.4.0** — the release where the starter profiles stopped answering from
tone alone. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Highlights

**Starters arrive knowing something.** `qrme/packs.py` has always described its
starter packs as *"one free Field Pack per industry, **matching the Starter
Collection**"*. The pairing was never wired. All 34 starters shipped with **zero
source material** while 37 packs sat in the marketplace — Dr. Sana Iqbal had an
environment persona and no environmental knowledge, Diego Fuentes a construction
persona and no construction material. Every one of them answered from tone alone,
which is a convincing impression of expertise and not the thing itself.

Seeding now installs each starter's own industry pack, and it is part of the
**repair** path — deployments seeded before this catch up by re-running seed
rather than by hand across 34 profiles.

Deliberately narrow, and each limit is a way of not overwriting somebody's
decision:

- **Only the starter's own industry.** Not "everything relevant" —
  `build_system_prompt` renders `sources[:8]`, so a profile that hoards material
  crowds out its own knowledge. One pack is three items, which leaves the budget
  room to grow.
- **Only onto a profile with nothing.** An owner who added their own material, or
  removed the pack on purpose, is not topped up on the next seed.
- **Free packs only, and no ledger credit.** A deployment grounding its own
  starters is not a purchase; a priced pack stays a decision for whoever owns the
  profile.
- **The rated starter is left alone.** There is no adult-industry Field Pack, and
  substituting one would be putting words in the profile the age wall exists to
  contain.

### Changed

**The README says which version you are looking at.** The title said `(v1)` and
the only feature section mapped the original PRD scope, so thirteen releases of
work were described nowhere a visitor would find them. There is now a release
table, newest first, and the PRD map keeps its place while saying what it
actually is — a conformance map, not a history. The same section went into all
three repositories.

### Fixed

**The README's avatar bubbles had no visible glow.** The bubble shipped in 0.3.0
got the rounded clip right and then blurred the halo across most of the margin,
which spread the light so thin it vanished against a dark page — a glow that
existed in the source and nowhere a reader would see it. Narrowed the blur and
raised the strength so the gallery matches the Profile Home screen it is meant to
mirror. Checked by rendering against the app's own background, which is the only
way this is checkable at all.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.

### Verification

622 tests green. 211 routes. The grounding limits are mutation-checked — a
priced pack being auto-installed, and a profile with existing material being
topped up, each fail the test that forbids it.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.4.0` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
