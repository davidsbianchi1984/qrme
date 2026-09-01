# The stores room

Everything the three storefronts need, kept where the release train can
reach it. The app itself does not change here — a store build is the same
console, the same backend, the same rails; what lives in this directory
is the packaging that puts it on a shelf.

| Counter | What ships | What it wraps |
| --- | --- | --- |
| [`meta-horizon/`](meta-horizon/) | A packaged PWA for Quest headsets | The live console at sntheticprofiles.com, same as the browser road |
| [`steam/`](steam/) | A thin desktop launcher | `native/windows/QrmeStudio`, published self-contained |
| [`viveport/`](viveport/) | The same launcher on HTC's shelf | The same publish output as Steam |

[`listing.md`](listing.md) is the copy all three counters share — one
description, one set of screenshots, one honest content-rating sheet —
so the product does not describe itself three different ways.

## What is deliberately not in this repo

App IDs, developer credentials, signing keys and upload tokens. Each
counter's README names the environment variables its build script reads;
the scripts refuse loudly when they are unset rather than shipping
something half-signed. Filling them is the owner's step, on the owner's
machine, after the developer accounts clear — the same doctrine as every
other secret in this deployment: entered where they are used, never
pasted into the record.

## The version rides the train

Every manifest in this room carries the app version, and
`tests/test_the_stores_carry_the_same_version.py` holds it equal to
`app/package.json` — a release cannot go out with a stale shelf. Bumping
the version means bumping it here too; the guard is the reminder.
