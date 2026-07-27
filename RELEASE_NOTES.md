# QRME v0.3.3 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.3.3` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.3.3** — the release where an agent working on its own stopped being
something you had to go and check. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### One question, answered everywhere

An agent off doing work raises one question, and it is not *what phase is it
in*. It is **does this need me right now?** Three colours answer it:

| | | |
| --- | --- | --- |
| 🟢 **green** | working · done | in progress, or finished. Nothing wanted from you |
| 🟡 **amber** | needs you | it has stopped and is waiting on a person |
| 🔴 **red** | stopped | it hit an error or was cancelled, and will not continue |

The word rides with the colour, because green alone cannot separate an agent
that is still going from one that has finished — and those call for opposite
reactions.

### Derived, never stored

There is no `light` column and nothing sets one. It is computed in the single
function every workflow read passes through, so a row cannot be persisted with
a light that disagrees with its own status. A second field naming the same fact
is a second field that can disagree with the first, and the one a screen reads
would be the one nobody remembers to update. A test asserts the column does not
exist.

An unrecognised status **raises rather than defaulting**. A default would paint
an unknown state green, and green is the colour that means *ignore me* — the
one failure this must not have.

### Three surfaces, doing three different jobs

**The watch** shows three lights and three counts and **no agent names**.
Naming them was the first cut and was wrong: a name is something you read, and
reading is the thing a glance cannot do. Which agent went amber is a question
for the app, where there is room to answer it.

**Screen 82** folds every agent into one tappable group per light. Somebody
opening it *because* amber appeared should not have to scan a flat list for the
one that changed.

**The overlay** rides over an ordinary screen, and over **every** desktop view.
This is the piece that makes the rest useful: an agent that reports only on its
own screen is one you have to remember to go and check, and amber and red are
exactly the states nobody thinks to look for. Desktop users have no wrist to
glance at, which is why it is on every view rather than one.

It is shaped like the watch face rather than as a bar across the screen — a
small translucent box in the bottom-right, three stacked rows, each its own tap
target. A bar reads as chrome and cuts the content in half; a corner box reads
as something floating above the work, which is what it is.

### The README leads with the screens now

Everything you can look at is above everything you have to read, and the
run / config material is gathered under one **Reference** heading at the bottom
— so a command spotted in a screenshot has one place to go and look it up.
Those tables are set smaller, because they are for looking things up in rather
than reading through.

### Also in this release

- A group subtitle that ran under the chevron is fixed, and the builder now
  length-guards them — the bug was visible in a render and invisible in the
  source, which is how it survived being written.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.

### Verification

633 tests green (9 new). 212 routes. Both starter generators idempotent under
`--check`.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.3.3` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
