# QRME v0.20.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.20.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.20.1 — the guard was measuring the wrong thing, and the money knew.**

Two rounds, and the second was found by the first.

## The union hid a surface

0.20.0 reported a doorless backlog of **zero**. It was true of the wrong
question. `clientpaths.doorless` unions the console with the iOS, Android and
Windows shells, so a route only the phone calls counts as doored — and the
number went to zero while a desktop owner could not reach **64 routes**. The
guard was answering *some client can reach this*, which was true, in place of
*this client can reach this*, which was not.

That is the shape of every defect this audit has produced: a checker answering
a question slightly to the left of the one that matters, and passing.

**Two new guards, in all three repositories:**

- `test_the_console_is_a_client_too.py` — the console's own backlog, checked in
  both directions and ratcheted so it cannot grow past where it started. The
  union guard stays; a route no client anywhere calls is still worse. A
  phone-only capability is a legitimate design choice, which is what the
  snapshot is for: deferring one takes a deliberate edit and shows in a diff.
- `test_a_binding_is_not_a_door.py` — a function in `api.ts` that no screen
  calls is not a door, and `doorless` counted it as one. The docstring on
  `doorless` had said this was *"a discipline rather than something the test
  can enforce"*. It is enforceable in about twenty lines, and found **25
  bindings nothing calls**. *The test cannot check this* is a claim worth
  testing.

## Screen 174 — "What you are owed"

Nine of the sixty-four were the whole seller's side of the product. An owner
could be bought from and could not post a licence offer, see who held one,
revoke it, read a penny of what it earned, or ask to be paid — all present on
the phone's Earn tab, all absent from the desk.

Building the screen found three defects.

**A statement added two currencies together.** ¥100 and $100 came back as
`accrued: 200`, labelled with whichever sale was newest, and all three native
shells render that figure with a currency symbol in front of it. Nothing was
wrong with the entries; each carried its own currency the whole time. The
arithmetic over them was wrong, in the one place where a wrong number looks
exactly like a right one. Totals are per currency now (`by_currency`,
`currencies`, and a `mixed` flag on the headline), the settlement currency is
chosen deterministically rather than by recency, and a payout settles **one**
currency and reports what is `remaining`. A single-currency account reads
exactly as it did.

**Anyone could delete anyone's listing.** `DELETE /marketplace/listings/{id}`
asked for no credential, while `DELETE …/offer` — which destroys strictly less
— answered the same stranger *"not your offer"*. Driven against a running
backend: a stranger removed a listing that had a recorded seller, an open offer
and a paid order against it. The offer and the orders survived orphaned and the
title was free for somebody else to put up. A listing is now claimed by whoever
staked something on it — the creator recorded in `listing_claims`, the seller
on its offer, or the owner of the profile it advertises. Creating one still
needs no token, and a listing with no claimant at all is still anybody's to
clear away, which is the honest reading of an endpoint that needs none.

**A sale credited to a key nothing reads.** This one came out of paying down
the first of the 25 unused bindings. `PUT /marketplace/listings/{id}/offer`
recorded the seller as the token's subject — and an **owner token's subject is
a profile, not an account**, while `GET /profiles/{id}/earnings` resolves the
profile to its `owner_id` before querying the ledger. So a seller who priced a
listing while signed in as their profile's owner got `200` on the offer, `201`
on the purchase with a real `ledger_entry` and the sentence *the sale is
recorded on the seller's statement* — and an empty statement. The money was
written under a key nothing queries, and every response along the way said it
had gone through.

It survived because nobody could do it: `api.setOffer` existed and no screen
called it, and the phone prices listings as an *interactor*, whose subject id
already is the account. `commerce.beneficiary_of` has resolved a profile to its
owner for gifts since gifts existed — the same rule, never applied to the other
half of the money. `_earner()` is that rule on the other half, across pricing,
withdrawing and `GET /marketplace/sales`.

## Also

- **`clientpaths.py` was not byte-identical across the three repositories**,
  though it says it is. JIM-mini and PDI never received the `fetch`,
  `window.open`, `<img src>` and `<a href>` call forms from 0.20.0, so their
  backlogs counted doors that already existed. Restored; JIM's dropped 73 → 69.
- **The pairing QR is built from a literal** in JIM-mini and PDI rather than
  from a path arriving in a response body — a real door no static check could
  see, which had got itself exempted as *not a client call*. That is an
  exemption made out of a blind spot, and the last one of those turned out to
  have no door at all.

## Where the numbers stand

| | QRME | JIM-mini | PDI |
|---|---|---|---|
| union backlog | 0 | 69 | 58 |
| console backlog | 55 | 109 | 84 |
| unused bindings | 21 | 4 | 3 |

The console backlogs are new, ratcheted, and now visible. That is the point of
them.
