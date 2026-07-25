# Marketplace search — words, place, and a hand with the words

Browsing used to mean knowing the vocabulary. `GET /marketplace/listings`
filtered by exact `kind`, exact `tag` and exact `area`, which is fine if you
already know the tag is `legal` and useless if what you have is *"someone who
can help me read a lease."*

    GET  /marketplace/search        words + place + the existing filters
    GET  /marketplace/localities    every place a listing actually claims
    PUT  /marketplace/listings/{id}/place     where it is offered
    GET  /marketplace/settings/{interactor}   where "here" is, and how far
    PUT  /marketplace/settings/{interactor}
    POST /marketplace/assist        candidate searches — never results

## Place is not `area`

`listings.area` was already taken, and it means a **subject** area:
`healthcare`, `finance`, `relationships`, `legal`. Geography went into its own
table rather than that column, because folding them together would make
*"near me"* quietly mean *"in healthcare"* — a bug that would look like an
empty marketplace and be very hard to see.

So a listing's place lives in `listing_places`, and it is deliberately coarse:

- **Nothing is sniffed.** No IP geolocation, no GPS, no address parsing. A
  seller types where they serve; a searcher types where they are. Location a
  user did not enter is location they did not agree to share, and a marketplace
  that guesses it has made that decision for them.
- **A locality is a name, not a point.** `"Oakland, CA"` — not coordinates and
  not a radius. There is no distance maths here at all, which is a limitation
  and also the reason there is nothing to leak.
- **`remote` reaches past the locality.** A listing served from anywhere still
  answers a local search, because "must I be near you?" is the actual question
  and for a lot of expertise the answer is no.

`GET /marketplace/localities` exists so a searcher picks from what is really
there. A free-text place box on its own produces a spelling nothing matches,
and an empty result that reads as "this marketplace has nothing".

## A rated listing can never carry a place

`set_place` refuses one. Not filtered later — **refused**, so no row is ever
written, so there is nothing for a place filter to match.

This is [desks.md](desks.md)'s line, moved to the marketplace: where a
performer physically is has nothing to do with browsing them, and a place
filter is a way of asking. Making it structural rather than a check means the
next person to add a filter cannot forget it — there is simply no data.

The refusal is loud rather than silent because an operator who thinks they
have set a location needs to know they have not.

## Ranking is deterministic, and says why

Scores are field-weighted — title 6, tags 4, provider 3, blurb 2, area 1 —
with prefix matching so *nutrition* finds *nutritionist*, and a short stop
list so *"someone who can help me"* does not out-rank the actual subject.

Two callers passing the same arguments get the same order. Every result
carries its `score` and the `matched_on` fields, so *"why am I seeing this?"*
has an answer that does not require trusting anybody.

`hidden_by_place` is reported rather than swallowed: a search that filtered
nine listings out on location should say so, or it looks like the marketplace
is empty.

## Settings are defaults, not a cage

An interactor saves where "here" is, how far out to look, and the kinds and
tags they keep choosing. Those become the defaults for their searches — and
**anything passed explicitly wins**, so a saved locality never traps somebody
who has just typed a different one.

Saving `scope: locality` without a locality is refused. Silently returning
nothing would be indistinguishable from an empty marketplace.

A saved list of several kinds or tags does *not* narrow: this filter takes one
value, and picking one of somebody's several on their behalf is a worse answer
than leaving it open.

## The assistant writes the box, and stops

`POST /marketplace/assist` takes *"I don't know what to search for"* and hands
back two or three candidate searches. It returns **suggestions and never
results**, and there is deliberately no code path from it into `search()`.

That boundary is the whole design, and it is the same one
[PDI's gate agent](https://github.com/davidsbianchi1984/pdi/blob/main/docs/beacons.md)
draws: a model can change what is in your search box, and nothing else. It
cannot filter, cannot reorder, and cannot decide what you are shown — so the
results you get are the same deterministic ranking everybody gets, and the
operator can still explain them.

A marketplace where a model silently re-ranks what you see is one where nobody
— including the person running it — can say why you saw what you saw.

If no model is reachable the suggestions fall back to keywords pulled from the
need itself. The box is never empty, and nobody is stuck behind a provider
outage.

## What this does not give you

- **No distance.** "Within 10 miles" is not expressible; localities match by
  name. Adding radius means storing coordinates, which is the thing this
  design is avoiding.
- **No inferred location.** Not from an IP, not from a device, not from a
  previous purchase. If a user has not typed it, the marketplace does not
  know it.
- **No personalised ranking.** Settings filter; they do not reorder. Two
  people searching the same words in the same place see the same list, which
  is what makes the ranking explainable.
- **No synonyms or spelling correction.** Prefix matching covers
  *nutrition/nutritionist*; it does not cover *attorney/lawyer*. That wants a
  vocabulary, and a wrong one silently buries listings.
