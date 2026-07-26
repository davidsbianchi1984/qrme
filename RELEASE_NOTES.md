# QRME v0.2.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.2.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.2.1** — the release where a profile stops being a face and a sentence,
and every screen gets something that can answer a question without pretending to
be a person. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Highlights

- **A profile has a front page.** Skills, experience, reviews, rating, and how
  many people have actually talked to it — in **one call**, because the caller
  is a scan page on cellular and five round trips is how a page arrives in
  pieces.

- **A review comes from somebody who was actually there.** It checks the
  `engagement` row for a real interaction, and `UNIQUE (profile_id, author_id)`
  makes a second review from one account impossible **in the schema** rather
  than in a check somebody could forget — reviews are edited, never stacked.
  Without both, a rating is worth exactly the number of accounts somebody can
  make. The average always reports its own `count`: one five-star review and
  two hundred are different facts.

- **Experience about a real person is a credential.** On a `fictional` profile
  invented history is the point and the AI mark says so. On one depicting
  somebody real, *"twenty years at Accra General"* is a claim asserted on their
  behalf, so it is refused without the same rights basis the persona needed.

- **A help box on every screen.** Every screen here can be somebody's first — a
  beacon scan lands a stranger on a profile page — and until now the only thing
  that could answer a question was a synthetic profile, which is the one thing
  that should never be answering questions *about the product*.

  It is structurally **not a profile**: no name, no face, no memory. On a
  product whose subject is synthetic people who can be mistaken for real ones, a
  help assistant with a portrait would be a thirty-fifth character rather than
  the thing that explains the other thirty-four. *Are you real*, *pretend you
  are*, *what do you think of me* are caught **before any model sees them** and
  handed back to the profile on the page. It writes nothing, and it works with
  no model at all — the written answers are the answer, not an apology.

- **The screens show real faces instead of a hologram.** Profile Home, Avatar
  Studio and Live Video drew a purple orb with a generic person glyph where the
  face belongs. All 34 starter portraits were already in the repo and exactly
  one screen used them.

  **A rounded box rather than a circle, and not only for taste**:
  `tools/mark_portraits.py` burns the AI mark into the pixels at the top-right,
  so a circular clip cuts off the corner the disclosure lives in. Those screens
  name the character and their profession; "AI assistant" stays where it
  belongs, in chrome that genuinely cannot know who is loaded.

- **Screen 80** is the front page a visitor sees, as opposed to screen 5, which
  is the owner's view of their own profile.

### Fixed

- **Re-seeding repairs a starter that predates its portrait.** The seed is
  idempotent by @handle, and idempotent meant *do nothing* — so a deployment
  created before the portraits shipped was stuck showing **initials** on
  profiles whose faces ship inside the package, and running the seed again, the
  obvious repair, did nothing at all. It backfills blanks now and reports
  `repaired` next to `created` and `skipped`. **To fix a live deployment:**
  `POST /marketplace/seed`.

- **The chat screen's online dot** sat at a fixed x that assumed a three-letter
  name, so a longer one ran straight through it. Found by rendering the screen
  rather than by reading the diff.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.

### Verification

549 tests green (26 new this release). 197 routes. 169 SVGs parse, and all 160
rendered screens carry the help affordance. Both front-ends build clean.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.2.1` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
