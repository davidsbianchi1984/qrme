# QRME v0.3.2 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.3.2` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.3.2** — the release where the starter collection stopped looking like
a directory. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### The starter gallery shows each profile's own front page

It used to be a portrait with a name and an industry captioned under it. That is
a directory listing, not a profile — screen 80 gives a starter an avatar bubble,
a role, **the rating people who talked to it left**, skill chips, Memory /
Relationships / Engagement, a career, a review, and a **Talk to** button. The
page was showing two of those.

It was also **five columns wide** — roughly 590px of content on a phone that
offers 390 — so on mobile the fourth column was sliced mid-word and the fifth
never appeared. Every starter past the third was unreachable to anybody reading
on a phone, which is most people. Two columns of whole cards fit, checked by
rendering the real markup at 390px rather than by arithmetic.

Generated from `qrme/seed.py`, not hand-written: the old gallery was a second
copy of the starter list maintained by hand and could drift from it silently.
Adding a starter without a role line is now a build error rather than a blank
cell, and both tools have a `--check` mode.

Careers and reviews are written, like the personas themselves — these are
invented experts, so a CV is characterisation of the kind the bio already is,
and each is drawn from that starter's own bio so the two cannot contradict each
other. The rating and the three tiles are the app's own sample values, identical
on every card: a freshly seeded starter has zero of each, so 34 cards reading
*4.0 · 37 reviews* is self-evidently a template, and the README says so.

### Fixed

**The rated starter was the only profile with no source material at all.** 0.3.1
grounded every starter in its industry's Field Pack and left Vivienne Sable out,
under a rule that ran two things together: the age wall governs *who may talk to
her*, and was never a reason for her to know less about her own subject.

The **Cabaret & Burlesque Field Pack** is theatre history and stagecraft — the
Ziegfeld era, the Parisian revues, and why a tease is a rhythm problem. Free and
unrated like the other 33, so it reaches her through the existing path with no
change to `_ground()`. Seeding now reports `grounded: 34`, where it reported 33.

Deliberately **not** the same thing as the $6.99 age-gated *After Dark Companion
Pack*, which is conversational craft sold to owners of any adult-mode persona
and never auto-installed. A test pins both so they cannot be merged by accident.

**A test was asserting the gap into place.**
`test_starter_packs_cover_every_industry` compared the pack list against
`STARTERS` and not `STARTERS + RATED`, so the check that existed to catch a
missing pack would have gone on passing forever with her ungrounded.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.

### Verification

624 tests green (2 new). 211 routes. Both generators idempotent under `--check`.
All 34 cards clear their content by exactly 16px, checked across every file
rather than eyeballed on one.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.3.2` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
