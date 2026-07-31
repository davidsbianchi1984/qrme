# QRME v0.21.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.21.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.21.0 — four doors, and three defects behind them.**

Four rounds run back to back. Each one built a console door for a backend
feature that had none. In three of the four, building the door found a defect
in the thing it was a door to — and in every one of those, the argument
against the defect was **already written down somewhere else in the same
repository**.

## A room id was the only thing a room asked for

`Rooms` could open a room and not enter it. Building the way in — **screen
175** — found two defects worth more than the screen.

- **Anybody could speak as anybody.** `POST /rooms/{id}/messages` read the
  speaker from `sender_id` *in the request body* and checked only that the id
  named a participant, never that the caller *was* that person. A stranger's
  token plus a named participant's id gave a `201`, a message stored under her
  name, and every profile in the room answering as though she had spoken.
- **The transcript asked for nothing at all** — not a wrong token, no token.
  And neither did `advance`, so a stranger could run somebody else's room
  forward indefinitely against their model key.

A room id is not a secret; it rides in beacons and on printed QR stickers,
which is the point of them. That sentence was already written **two routes
away**, on `GET /rooms/{id}/mic`, guarding the narrower fact of who is wearing
a live microphone. All three now go through the same membership check.

`sender_id` stays on the request model and is ignored — three shipped native
clients send it, and a 422 on upgrade is a worse answer than not believing it.

## The body market, and what you bolt onto a body

Choosing a body is shopping, and the catalogue listed nine models. It now
lists **36 from 25 makers** across humanoids, home robots, quadrupeds and
announced platforms, with a review date the suite refuses to let go stale.

Announced bodies are listed **on purpose** — an owner shopping should see what
is coming — and binding one is refused with a `409` that says so, rather than
a `404` that would lie about a machine its maker has publicly shown.

Alongside it, the **connections bracket**: task packs and connectors. Each
installed pack becomes a commandable verb for exactly one body, capability
checked at install and audited like every built-in command. A vacuum is still
never taught `fetch`.

## A policy you could publish and nobody could take up

`Delegate` built the owner's half of delegation — mint a grant, choose which
phases run unattended, start and advance and cancel. But delegation exists for
the person on the **other** end of a conversation, and that half had four
bindings and no screen calling any of them. The policy was publishable and
unusable from the console that published it.

Driven end to end, **every rule was already right**: the offer is public and
lists phases only, never the grant id, because which source items the owner
scoped is the owner's business; `research` is refused without a grant, and the
refusal names what it protects rather than the rule it enforces; starting one
requires an existing conversation; and reading one is `403` to an outsider,
`401` to nobody at all, and `200` to the delegate *and* the owner, who are
entitled to it for different reasons.

The first round in a while with no defect in it, recorded plainly as such. The
failure it *did* find is exactly the one the door audit exists to name: a
feature finished and unreachable.

## A missing field was reported as a broken signature

Seven signature routes had no console door: enrol a credential, revoke one,
read the policy, mint an envelope, sign it, and check a package handed over
from outside. `Referrals` had already written the gap down as a sentence —
*“None enrolled. The ceremony can enrol one.”* — under a heading with no
button behind it. The ceremony page existed and posts the raw assertion back
to its host; nothing in the console was listening, so the message went
nowhere.

Building the listener found the defect, in the one place this feature cannot
afford one.

`verify_package` runs eight checks in order. **Any** exception anywhere in that
sequence ran `checks["signature"] = False` and appended `str(exc)`. So a
package missing `display_text` — trimmed in transit, or a summary forwarded in
place of the package — came back saying **the signature is invalid**, when the
ECDSA verification several lines earlier had passed. That is the strongest and
most damaging thing this endpoint can say, it was false, and the reason offered
was `'display_text'`: a Python `KeyError` repr sitting beside two notes written
as full sentences. A counterparty reading it would conclude they had been
handed a forgery.

The argument was already in the same feature. The router says of its own
refusals: *the message is the reason, because a signature that is turned away
without one is impossible to fix from the outside.* A counterparty is exactly
the outside.

Two rules now hold. A check that already **passed** is never retroactively
failed by a later one breaking — only the check that actually broke is
reported broken. And a check that never **ran** is not a pass: all eight are
named, `valid` is false whenever any is absent, and the notes say which and
why in sentences. The screen draws unrun as unrun, because a fixed backend
behind a screen that drew absent as a tick would put the same lie back on the
glass.

## Where the numbers landed

| | before | after |
|---|---|---|
| Console-doorless routes | 64 | 40 |
| `api.ts` bindings nothing calls | 25 | 12 |
| Screen-manifest `unaudited` seeds | 8 | 7 |

New screens **174–178**. Full suite: **1926 passing**.

---

Installers for macOS, Windows and Linux are attached below once the release
build finishes.
