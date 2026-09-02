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

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
