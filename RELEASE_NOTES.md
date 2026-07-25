# QRME v0.1.7 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.7` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.1.7** — the release where a profile stops being only something you
talk to. You can now like it, comment on it, share it, subscribe to it, gift
the person behind it, and buy what they are selling — and a live desk can be
left on a door as a printed code, the way a synthetic profile already could.
One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version.

### Highlights

- **A live desk can be left behind as a printed code.** A profile beacon and a
  desk beacon are the same gesture aimed at opposite things: scanning the first
  reveals somebody who does not exist and the page marks the portrait *AI*;
  scanning the second reveals somebody who does. So the badge is inverted and
  deliberately unlike the AI mark at a glance — **Live person — not AI**, green
  and top-right against the mark's neutral bottom-left — because absence of the
  AI mark is not a disclosure on its own. The sticker goes on the shop door
  *because* nobody is behind it, so the scan page carries a working bell.

- **Like, comment, share, subscribe.** On a profile, a live desk, a room
  message or a marketplace listing. A **like is a fact, not a counter** —
  stored per person, so liking twice is still one like and no account can
  manufacture popularity in a loop. A **comment** goes through the same
  moderation pipeline as a chat turn, at the target's maturity setting; a
  blocked one is kept and shown to its author with the reason, and to nobody
  else. A **share** needs no account, because the person who scanned a sticker
  is the one most likely to pass it on — the age gate lives at the destination,
  not on the sharer.

- **Subscriptions, free and paid.** A free `follow`, and a `paid` tier that
  credits the creator's ledger each period alongside pack sales and licence
  fees. Paid confirms the price explicitly, because a recurring charge nobody
  meant to start *keeps* costing them. **Nothing bills on a timer** — periods
  are charged by an explicit renew, so a deployment left running accrues
  nothing unseen.

- **The marketplace is transactable at last.** `listings` had no price and no
  purchase endpoint, so a product could be listed and bought by nobody. Now a
  listing is a shop window and an **offer** is what makes it a shop: price and
  seller live in a row only a token-holder can write, and the seller comes from
  that token rather than a request body. A listing nobody offered cannot be
  bought — not by a check that could be forgotten, but because there is nowhere
  for a price to be.

- **Gifts, with rules purchases do not carry.** A gift sends money to a person
  and receives nothing, which is the shape livestream tipping keeps turning
  into a way of taking money from people who should not be spending it. So the
  giver must be a **verified adult** whoever they are gifting, a single gift is
  **capped**, a rated desk runs its own 18+ gate on top, and the recipient is
  read from the subject rather than named by the giver.

- **Windows signs, through the browser engine rather than interop.** The
  blocker was `webauthn.dll` — hundreds of lines of version-sensitive struct
  marshalling a compile cannot check. Edge already talks to Windows Hello, so
  the desktop app hosts a **WebView2** on a new `GET /signatures/ceremony`
  page served from the deployment's own origin. The page never sees a token.

- **The three products now cut as one release.** Same number, same pass, even
  when a repository has nothing of its own to ship — documented in
  [docs/releasing.md](docs/releasing.md) in all three.

### Money here is simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body rather than leaving it to a policy page.

[docs/commerce.md](docs/commerce.md) states what is *absent*: running spend
totals, cooling-off, parental controls, a real identity check behind "verified
adult", chargebacks, and payout compliance. If you wire a real payment
processor to these endpoints, that list is the work remaining — not a set of
nice-to-haves.

### Verification

486 tests green (48 new this release). Both front-ends build clean. iOS,
Android and Windows all compile in CI.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.1.7` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
