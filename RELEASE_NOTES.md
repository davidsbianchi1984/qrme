# QRME v0.4.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.4.1** — the release where free got honest, and the claims got
checked. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version.

### A free plan, with nothing private about it

Free reaches everything Basic reaches — your profiles, your own agent —
so **$20 buys privacy, not features**. The difference is where your work
lives and who holds it:

| | | |
| --- | --- | --- |
| **Free** | platform custody | QRME holds it, you have access. Ordinary HTTPS, our database, in the clear, no vault at any point |
| **Basic / Pro** | your custody | sealed in PDI before it lands, under a key you can hold, with a tamper-evident chain over every access |

The disclosure is a **field on every surface that names a plan**, not a line
in a Terms of Service. And the vault gate now asks about the *plan* rather
than the deployment — it used to ask the other question, so a free account on
a PDI-backed deployment had its work sealed into a vault it was not paying
for and could not hold a key to. Guarded by counting vault writes, not by
reading call sites.

### What the open store will not hold

The test for the list is *whose exposure is it*: **source material about
somebody else**, **anything behind the age gate**, and — found on the way
through — **a clinician's written opinion about a real person**, which was
heading for the open store because the referral flow writes through a path
the third-party rule never saw. Refused before any clinician is contacted.
A downgrade never unseals anything; an upgrade cannot un-expose what was
already open.

### Channel 3 — sharing your camera

Point your camera at the thing — a knocking engine, a boiler, a document —
so somebody else can see it. The subject sets the rules: a thing, place or
document can be watched by anyone; **a body only ever by a person, never a
synthetic profile**. Two taps to open, one to close, hard time cap, and a
disclosure on every surface.

### The claims got checked

The README's "N tests" arithmetic is now verified against the files (two
counts were stale), no user-facing copy may hardcode a refusal count that
disagrees with the list (four did), and a refusal test must be reached by a
request that would otherwise succeed — a mutation check caught one of this
release's own tests passing for the wrong reason.

### Verification

1153 tests green. Screens 136–140 new, the tier and signup screens redrawn
for the free plan, and every guard above mutation-checked.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.4.1` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
