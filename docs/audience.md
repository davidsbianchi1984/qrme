# The audience layer — like, comment, share, subscribe

Everything a viewer does *other* than talk. Chat and rooms already carried the
conversation; this carries the quieter half — the reactions that decide whether
anyone comes back, and the subscription that says they intend to.

Four verbs across four kinds of target:

| | profile | desk | message | listing |
|---|---|---|---|---|
| like | ✓ | ✓ | ✓ | ✓ |
| comment | ✓ | ✓ | ✓ | ✓ |
| share | ✓ | ✓ | ✓ | ✓ |
| subscribe | ✓ | ✓ | — | — |

A message and a listing cannot be subscribed to: subscribing means *tell me
when there is more from them*, and neither produces more.

Targets are a `(kind, id)` pair rather than a column per thing. A like on a
synthetic profile, a live desk, a room message and a marketplace listing is the
same fact about the same person, and four near-identical tables would have
drifted apart within a round.

## A like is a fact, not a counter

`reactions` is UNIQUE on `(target, actor)`. Liking twice is idempotent and
returns `was_already_liked: true` rather than an error, so a client can render
the button's state without a second request.

This is the whole design. A plain integer column would let one account
manufacture popularity by calling an endpoint in a loop — which makes every
number on the platform meaningless, not just that one. The cost is that a like
requires a token; that is not a side effect, it is the point. A like from
nobody in particular is a number anyone can produce.

## A comment is authored text, so it is filtered like authored text

Comments go through the same [moderation](../qrme/moderation.py) pipeline as a
chat turn, at **the target's** maturity setting rather than the commenter's —
a comment lands under someone else's name, and the profile owner is who a
visitor will hold responsible for what appears there. A minor commenting is
held to the strict filter whatever the target is set to, exactly as in chat.

A blocked comment is **kept**, returned to its author with the reason, and
shown to nobody else — the same shape `connections.py` already uses. The
endpoint answers `201`, not `422`: the comment *was* accepted and recorded, and
what happened to it is in `status`.

Both halves matter. Dropping it silently teaches the author nothing and they
post it again; showing it to everyone teaches them the filter does not work.
Blocked comments are not counted in the totals.

## Sharing is gated at the far end, not at the sharer

Anyone can share, including a caller with no token — someone who scanned a
sticker is exactly the person most likely to pass it on, and has no account.

Sharing a **rated** target is allowed for the same reason: the link they would
send lands the recipient on the age wall regardless of who sent it. Refusing
the sharer would be gate theatre, and the gate that actually holds is the one
at the destination, which cannot be routed around.

Shares are recorded rather than merely counted, with the actor when there is
one. *Shared 40 times* and *shared 40 times by one account* are different
facts, and only one of them is worth anything.

## Subscriptions: two tiers on one row

- **`follow`** — free. Means "tell me when they are live, or when they post".
- **`paid`** — recurring, and credits the creator's ledger each period.

A paid tier requires `accept_price` to match the price being charged, the same
explicit-consent step priced packs already use. It is here for a sharper
reason: a subscription is recurring, so a viewer who did not mean to start one
**keeps** paying for it — strictly worse than a single purchase they did not
mean to make.

**Nothing bills on a timer.** The first period is charged on subscribe; later
periods are charged by an explicit `POST /subscriptions/{id}/renew`. A
deployment left running does not accrue charges nobody authorised and nobody
saw.

Cancelling sets `status` and keeps the row, so a lapsed subscriber stays
distinguishable from someone who was never there. Re-subscribing reactivates
the same row rather than creating a second one, so one person has one history.

### Money here is simulated

Exactly as it is for packs, licences and venue placements. A paid subscription
writes a **real row** on the creator's statement with `kind: subscription` and
settles through the same payout sweep as everything else — but nothing in this
repository moves real funds. Every subscription response says so in its
`billing` field rather than leaving it to a policy page, because implying a
payment processor that does not exist is the kind of claim that gets believed.

## Rated targets stay rated, on every verb

Liking, commenting on, subscribing to, or reading the counts of an 18+ desk all
run the deployment's **existing** verified-adult check. This layer does not
implement a second one — a weaker second gate is always the one that gets used.

The test for this asserts across all five surfaces in one loop rather than one
endpoint at a time, because a gate that was remembered on four of five is
exactly the kind that ships.

## Endpoints

The path segment is the plural resource name the rest of the API already uses;
`audience.py` works in singular kinds and maps between them, so these routes
read like the ones they sit beside instead of like a separate API.

```
POST   /{profiles|desks|messages|listings}/{id}/like        (token)
DELETE /{...}/{id}/like                                     (token)

POST   /{...}/{id}/comments      moderated; 201 even when blocked   (token)
GET    /{...}/{id}/comments      approved + your own blocked ones
DELETE /comments/{id}            withdraw your own                  (token)

POST   /{...}/{id}/share         no token needed; returns the link

POST   /{profiles|desks}/{id}/subscribe     follow, or paid+accept_price (token)
DELETE /{profiles|desks}/{id}/subscribe     cancel                       (token)
POST   /subscriptions/{id}/renew            charge the next period       (token)
GET    /subscriptions                       what you subscribe to        (token)
GET    /{profiles|desks}/{id}/subscribers   who subscribes to this

GET    /{...}/{id}/audience      likes, comments, shares, subscribers,
                                 and your own state in one call
```

`GET …/audience` is deliberately **not** called `engagement`: this codebase
already uses that word for the per-relationship EMA score that conditions the
persona prompt ([adaptation.py](../qrme/adaptation.py)). Two different numbers
under one word would have been read as one number by whoever came next.

## Not built yet

**Gifting and marketplace purchase** are the commerce half of this and are a
separate round. Note that `listings` currently has no `price` and no purchase
endpoint at all — you can list a product on the marketplace today and nobody
can buy it. Packs and licences have priced purchase; listings never got it.
