# QRME v0.20.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.20.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.20.0 — the doorless backlog reached zero.**

It began at **116** routes the backend served that no client could reach. This
release closes the last **42**, each with a door in the console, carried by six
new screens (**168–173**).

A route with no door is the quieter of the two integration failures. A client
asking for a route that does not exist produces a 404 somebody eventually
reports. A route no client asks for produces nothing at all: the code is
present, its tests pass, the changelog says it shipped, and the capability is
simply unreachable.

## What the exercise actually produced

Not doors — **defects**. Almost none were visible to the typecheck.

**Three routes took no token at all.**

- `POST /packs` let anybody publish to the marketplace, name any string as the
  publisher, and name *any account* as the one sales accrue to.
- `POST /profiles/{id}/interactions/{id}/feedback` let anybody rate in somebody
  else's name — and since an `up` rating is the trigger for cloud contribution,
  an unauthenticated caller could push a stranger's conversation out of the
  deployment.
- `GET /profiles/{id}/engagement/{id}` exposed how often a named person talks
  to a profile, across how many sessions, and whether they liked it.

In each case the argument against it was **already written down elsewhere in
this repository** — `commerce.beneficiary_of` on gifts, the beacon list on
physical places. Three routes had quietly gone the other way.

**A licence was sold to somebody who could not use it.** A licence permitting
derivatives went to a buyer under 18: `201`, `can_derive: true`, fee credited
to the seller at sale time — then a `403` on the only thing the licence exists
for. The adult check now runs at acquire, where the money moves.

**A link resolved against the wrong origin.** Desk beacons returned a relative
`scan_url` while the profile beacons next door returned an absolute one, so the
console's scan link resolved against the console's own origin — dead in every
packaged build.

**An honesty note was served to nobody.** A desk's view frame, and the sentence
it carries — *this deployment has no camera on this desk, so the frame is not
live and is not claimed to be* — was never rendered anywhere in the console.

## The audit could not see two kinds of request

An `<img src>` is a fetch. An `<a href>` is a fetch. Neither passes through the
API client, and the extractor could see neither — so two routes sat on the
backlog while the placements screen had been rendering both since it was
written.

Worse, **the exemption list had absorbed three of them**, each marked "rendered
in an `<img src>`, not fetched by the API client" — an exemption made out of a
blind spot, which is the shape that stops anybody asking. One of the three had
no door at all. The list now holds to one rule: **exempt a path because nothing
should ever call it, never because the audit cannot see the call.**

## Recorded rather than corrected

Five findings are pinned as observed behaviour instead of changed, because each
is a decision to make deliberately rather than while building a screen:

- a **gift** reads its beneficiary from the subject; a **subscription** takes
  one from the request body;
- the contribution **preview is computed whether or not you are opted in**, so
  the console changes the heading rather than the content;
- the quiet-hours window is half-open, so **9-to-9 covers nothing** — changing
  the arithmetic would silently redefine every window already stored;
- three deletes give three different answers to *there was nothing there*;
- `deleted_at_gateway` is true *vacuously* when nothing ever left.

## The guard, now that the backlog is empty

A new assertion says so directly, separate from the record comparison so the
message is plain when it goes: *the number is no longer zero*. Its
guard-on-guard moved too — asserting the snapshot was non-empty no longer means
anything, so the liveness check now sits on the console's extracted call sites.

Seven new test files, 154 tests, 23 injection-verified. **Suite: 1807 passing.**
