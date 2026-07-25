# QRME v0.1.8 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.8` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.1.8** — the release where a live desk stops being something you watch
and becomes somewhere you can be. You can ask to come up on the stream, and the
room's reactions render on the picture rather than beside it. One of three
interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Highlights

- **Two ways into a live room, and they are not the same act.** Watching and
  commenting is something a viewer does; appearing *on* the stream is something
  the host lets them do. `mode: audience` joins immediately; `mode: guest`
  **only asks**, returning a pending request rather than a room — a join that
  behaved as though the request had been granted would be the worst possible
  default.

- **Coming up has the gates the act deserves.** It needs an account, because the
  host is deciding about a person rather than an anonymous request, and on a
  rated desk a **verified adult**, because a guest there is someone *going live*
  on an 18+ stream rather than merely watching one. One hand up at a time, a
  decision made once, an owner-only queue — and a guest can always step back
  down without asking, since needing permission to *stop* being on camera would
  be the wrong way round.

- **The reactions are on the picture.** `GET /desks/{id}/overlay` defines the
  layer once — comments, likes, shares, gifts, who is up — so every client draws
  the same one. They belong over the video because that is where the viewer is
  already looking, and on a stream whose premise is an empty chair with a bell,
  the reactions *are* the room. Transparent plates so the room stays visible
  through them; the text on top is not faded, because chat you have to squint at
  is chat nobody reads.

- **The screens show what they had been describing.** Eight new mobile screens
  and three desktop views cover live desks, desk beacons, the audience layer,
  commerce and signatures — none of which had a screen at all. Three carry the
  **real camera frames**, embedded rather than linked, because an SVG rendered
  through an `<img>` tag cannot fetch external files. The signs in them are the
  feature: *ring bell for service, away from the desk*.

- **All 34 starter portraits are visible.** In the README, in
  [docs/avatars.md](docs/avatars.md) beneath the briefs that specify them, and
  as a grid on the Starter Collection screen — which used to say "seeded with
  faces" and draw icon chips. No gallery carries a badge of its own: the AI mark
  is burned into each portrait's own pixels, so it survives a screenshot, a
  hotlink or a crop and travels into every page that shows one.

### Also fixed

`[0.1.5]` and `[0.1.6]` in the changelog linked to release tags that were never
pushed, so both were 404s. They now point at their release-prep commits.
Deliberately *not* fixed by backfilling those tags — that would fire the
installer build and publish two superseded releases dated after v0.1.7, at the
top of the page people download from.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent: spend
totals, cooling-off, parental controls, a real identity check behind "verified
adult", chargebacks, payout compliance. If you wire a real processor to these
endpoints, that list is the work remaining.

### Verification

500 tests green (14 new this release). 187 routes. 172 SVGs parse. Both
front-ends build clean, and iOS, Android and Windows all compile in CI.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.1.8` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
