# Commerce — gifts, and buying things on the marketplace

The [audience layer](audience.md) was about attention. This is about money, and
the two need different care: an over-counted like is embarrassing, a
mis-credited payment is a dispute.

## Money here is simulated

Nothing in this repository moves real funds. What it *does* do is write real
rows on the creator's statement — alongside pack sales, licence fees and venue
placements — settling through the same payout sweep. The accounting is honest
even though the payment is not real.

Every response that involves money says so **in its own body** rather than
leaving it to this page, because implying a payment processor that does not
exist is the kind of claim that gets believed.

## A listing is a shop window; an offer is what makes it a shop

`POST /marketplace/listings` needs no token and never has. Anyone can create a
listing naming any `provider_name` they like. That was harmless while listings
were discovery-only, and stops being harmless the moment a price can be
attached to one.

So the price and the seller live in a separate `listing_offers` row that only a
token-holder can create, and **the seller comes from that token, never from a
request body**. A listing with no offer cannot be bought — not because of a
check somebody could forget, but because there is nowhere for a price to be.

```
PUT    /marketplace/listings/{id}/offer      price it            (token = seller)
GET    /marketplace/listings/{id}/offer      the price — public
DELETE /marketplace/listings/{id}/offer      stop selling        (seller only)
POST   /marketplace/listings/{id}/purchase   buy it              (token = buyer)
GET    /orders                               what you bought     (token)
GET    /marketplace/sales                    what you sold       (token)
```

Buying requires `accept_price` to match, the same explicit step priced packs
use. The price is read from the offer rather than from the request, so agreeing
to a number means agreeing to *the* number rather than merely stating one.

Other things the purchase path refuses, each for a stated reason:

| refused | why |
|---|---|
| buying your own listing | credits you with your own money *and* inflates the listing's sales count |
| a withdrawn or sold-out offer | the shop is shut; the window can stay up |
| a rated listing, unverified viewer | the same gate that hides it from an unverified browse |

Withdrawing an offer keeps the listing as a shop window and keeps past orders
as receipts. An order copies the listing's **title at purchase time** — a
receipt that changes when the seller edits the listing is not a receipt.

## A gift is not a small purchase

A purchase exchanges money for a thing. A gift sends money to a person and
receives nothing — and that asymmetry is exactly the shape that livestream
tipping has repeatedly turned into a mechanism for taking money from people who
should not be spending it.

So gifts carry rules purchases do not:

- **The giver must be a verified adult**, whoever they are gifting. Not because
  the recipient is sensitive, but because the giver is. An account with no
  birthdate on it is refused: an unverified age is not evidence of an adult.
- **A single gift is capped** at `commerce.GIFT_MAX` (500). A cap does not make
  gifting safe; it removes the single worst outcome — one tap emptying an
  account — while the rest of the problem stays honestly out of scope.
- **Gifting a rated desk runs the adult gate as well.** The giver being an
  adult and the surface being 18+ answer different questions, and neither
  substitutes for the other.
- **The beneficiary is read from the subject, never from the giver.** A
  body-supplied beneficiary would let anyone route a gift meant for a performer
  into their own balance.

```
POST /{profiles|desks}/{id}/gift    send value        (verified adult)
GET  /{profiles|desks}/{id}/gifts   the tip jar, and the per-gift cap
```

A gift response states `refundable: false` at the point of giving rather than
in a policy page. Nothing is delivered in return, so there is nothing to fail
to deliver and nothing to return.

### What this is not

These rules are proportionate, **not sufficient**. A production deployment
handling real money needs things this module does not have and does not pretend
to have:

- running spend totals per giver, and cooling-off after a burst;
- parental controls, and a real identity check behind "verified adult" rather
  than a birthdate the account supplied;
- chargeback and dispute handling;
- tax and payout compliance for the people receiving the money.

That list is here rather than absent because a half-built safety feature that
looks whole is worse than an obviously missing one. If you wire a real payment
processor to these endpoints, treat the above as the work remaining, not as
nice-to-haves.

## Where the money shows up

Everything lands on the existing creator statement
(`GET /profiles/{id}/earnings`) with its own `kind`:

| kind | from |
|---|---|
| `listing_sale` | a marketplace purchase |
| `gift` | a gift on a profile or desk |
| `subscription` | a paid subscription period ([audience](audience.md)) |
| `pack_sale`, `license_fee`, `placement` | already existed |

All of them accrue and settle through the same `POST …/earnings/payout` sweep,
so a creator has one statement rather than one per feature.
