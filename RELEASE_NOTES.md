# QRME v0.3.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.3.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.3.0** — the release where the tandem reaches a person. A synthetic
specialist could answer a question; now it can be handed a multi-step task, and
the person talking to it can be put in front of a real clinician with the
release **signed for rather than ticked**. One of three interoperating products
(with [jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Highlights

- **A specialist can be handed a task, not just a turn.** `qrme/workflows.py`
  has always run `research → draft → review → send → confirm` in character,
  carrying memory forward and surviving across sessions. Every route reaching it
  was owner-only, which blocked the case the tandem needs: JIM's Guardian
  handing work to a specialist it is already talking to.

  Relaxing those routes would have been the wrong fix. **A workflow is not a
  chat turn** — it runs several phases unattended and its `research` phase reads
  the profile's vaulted source material, where a missing grant means scope
  `["*"]`, *all of it*. So delegation is off until an owner turns it on, and
  **delegating `research` without a grant is refused at write time**, where the
  owner is present to read the error rather than at 3am inside somebody else's
  workflow. An owner's own workflow has no `delegated_workflows` row, and that
  absence is what keeps the two surfaces from ever merging.

- **A referral to a real clinician, authorised by a signature.**
  `POST /handoffs` could already package a session for a real provider — and it
  released on `consent: true`, **a boolean the client sets**. Meanwhile
  `qrme/webauthn.py` opens by describing itself as *"the layer that turns 'the
  app says the user agreed' into something a third party can check"*, sitting
  one import away from the single endpoint that ships somebody's health
  conversation outside the product.

  A referral signs at the **`high` tier**: document proofing on a device-bound
  credential — the platform authenticator (Face ID / Touch ID / Optic ID) rather
  than a passkey that roams. The challenge **is** the hash of the exact package,
  and release re-hashes the stored bytes rather than trusting the hash recorded
  beside them. Bound to one referral, so an assertion raised elsewhere is not a
  skeleton key. The link **opens once**, and a second attempt says so rather
  than quietly working.

- **The clinician writes back, and the profile is caught up.** Opening the link
  mints a reply token at that same moment — open once, reply once. The note is
  sealed in the PDI vault under `qrme/{profile}/clinical/…`, the same treatment
  source material gets.

  It is deliberately **not** a `source_items` row, and that is the decision the
  rest hangs on: source material is what a profile recalls *as its own*, and it
  is what a workflow's `research` phase reads. Instead the note arrives in its
  own prompt block naming the clinician — *these are that clinician's words, not
  yours* — so the person does not have to retell their situation, and the
  profile does not acquire a clinical opinion it can improvise from.

- **Matching filters on expertise and only ranks on geography.** A cardiologist
  two streets away is not a substitute for a psychiatrist. No match returns
  nothing rather than a near miss: a confident wrong referral is somebody
  phoning a clinic that cannot help them.

### Fixed

- **The starter gallery on GitHub rendered 34 black boxes.** The portraits were
  loading fine — they are square RGB with a near-black backdrop, and the README
  embeds them raw, while the app draws its rounded avatar bubble at render time.
  GitHub's markdown sanitiser strips the `style` attribute that would round
  them, so on a surface QRME does not control the bubble has to be **in the
  pixels**. `tools/bubble_portraits.py` bakes it, on transparency so the gallery
  sits on whatever theme the reader has.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.

### Verification

589 tests green (40 new this release). 209 routes. Nine safety properties are
mutation-checked — each fails the test that forbids it: delegating research
without a grant, a delegated caller widening its envelope, an owner's workflow
appearing on the delegated routes, a signature raised elsewhere releasing a
referral, trusting the stored hash instead of re-hashing, a referral link
opening twice, dropping the clinician attribution directive, a clinician
writing back repeatedly, and one patient's note reaching another's conversation.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.3.0` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
