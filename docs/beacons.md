# Beacons — leaving a profile somewhere

A beacon is a synthetic profile left in a physical place. Print the QR, stick
it where the people who need that profile already are, and anyone who scans
it lands on the profile's page.

    POST /profiles/{id}/beacons   place one
    GET  /b/{beacon_id}           where the printed QR points
    DELETE /beacons/{beacon_id}   pick it back up

`scan_url` is the one to print or share. `summon_url` is the JSON surface for
clients that want data rather than a page.

> **A live desk can be left behind the same way**, with the badge inverted —
> *Live person — not AI* instead of the AI mark, because there is an actual
> person behind that door. Different table, different routes (`/d/{id}`), same
> gesture. See [desks.md](desks.md#leaving-the-desk-behind--beacons).

## What a scan actually does — three different answers

Whether the portrait can appear *in the camera*, without going anywhere,
depends entirely on which camera is looking.

| Scanned with | What happens | Status |
|---|---|---|
| The stock camera app | A URL chip. Tap it and `/b/{id}` reveals the portrait. | shipped |
| **The QRME app** | **The portrait is drawn on the sticker in the live viewfinder.** No tap, no page. | shipped (iOS + Android) |
| The stock camera, via an iOS App Clip | An App Clip Card — portrait, name, action — over the camera, before going anywhere | needs your Apple account |

**The stock camera cannot be made to render anything.** Reading a QR and
offering its URL is the entirety of what it exposes; there is no API for a
third party to draw into that viewfinder. Anyone claiming otherwise is
describing one of the other two rows.

### In the QRME app

The app owns the viewfinder, so it can draw on it. `GET /b/{id}/card`
returns the little an overlay needs, and the portrait is composited onto the
code's reported bounds — tracking the sticker as the phone moves. Tapping
opens the full page; not tapping still showed you who it is, which was the
point.

Two implementations, one behaviour:

* **iOS** — `BeaconScannerView`, AVFoundation + Vision. Vision reports a
  normalised box with the origin at the bottom-left; SwiftUI draws from the
  top-left, so the box is converted before anything is placed.
* **Android** — `BeaconScanner.kt`, CameraX + ML Kit. ML Kit reports in the
  analysis image's own coordinate space, which is rotated relative to the
  view and usually a different resolution, so the box is mapped through the
  preview's `FILL_CENTER` transform. Skip either conversion and the portrait
  lands somewhere the sticker is not — the failure looks like a tracking bug
  and is really a coordinate-space bug.

Both guard resolution by beacon id plus an in-flight flag: the camera
delivers around thirty frames a second and every one of them sees the same
sticker, so without the guard the overlay would re-request continuously and
count a scan each time.

The card carries the AI mark in the same payload as the portrait, so an
overlay cannot draw the face without also having been handed the disclosure.
A rated beacon's card contains **neither the name nor the portrait** — only
`age_wall: true` — so the overlay can render the wall without ever holding
anything to leak.

### The stock camera, without the app: App Clips

An **App Clip Card** is the one way a portrait appears over a stock camera
with nothing installed: iOS shows a card with a header image, title and
subtitle when it recognises a URL registered to your App Clip. It is real,
shipping Apple technology and it is the closest thing to the idea.

It needs things this repository cannot provide: an Apple Developer account,
an App Clip target, and an `apple-app-site-association` file served from the
deployment's domain. The header image would be the profile's portrait, so it
also needs the portrait to be a stable public URL. Worth doing; not
something code alone finishes.

WebXR is the remaining option and the weakest: partial support on iOS Safari,
and it prompts for camera access — a hard sell for a stranger who just
pointed a phone at a sticker.

## Placement is the whole idea

The starter collection covers an industry each, and the point of a beacon is
that a profile is most useful exactly where its subject already comes up:

| Profile | Left at |
|---|---|
| `@otis_marsh` (music) | the venue's green room, a rehearsal space |
| a music instructor | the counter of a music shop |
| `@dr_sana_iqbal` / a nutritionist | the produce aisle, by the scales |
| `@marcus_bell` (finance) | a bank lobby, a teller window |
| `@coach_dana_reyes` (fitness) | the gym floor, beside the rack |
| a parenthood coach | a family-planning clinic waiting room |
| a recovery sponsor | the back table at a meeting |
| `@jonathan_ashe` (legal) | a bail bondsman's window, a courthouse corridor |

Any profile can be placed anywhere; nothing in the code ties an industry to a
location. The table is a suggestion about where a profile earns its keep.

### Two placements, end to end

The table above is a list. These are the two that show what the feature
actually has to survive, because in both of them the person scanning is a
stranger standing somewhere the creator is not.

#### The songwriter at the concert hall

Otis has a set on Friday. He prints a sticker and puts it on the merch table
and inside the stairwell to the balcony, where people queue.

```bash
curl -X POST $QRME/profiles/$OTIS/beacons \
  -d '{"label":"merch table, Friday","mode":"room","topic":"after the set"}'
```

`mode: room` is the whole choice here. A **chat** beacon gives every scanner
their own private conversation, which for a Q&A after a set is forty people
each asking the same question into forty separate rooms. A **room** beacon
mints one shared room with the profile already in it, so everyone who scans
the same sticker is in the same conversation — they can see each other's
questions, and the answers land once.

The room page says *"you may not be the only one here"* before anybody types.
A stranger who scanned a sticker on a wall has no way of knowing which of the
two they walked into, and a shared room is a different thing to enter than a
private chat.

What the scanner gets, without an account and without knowing what QRME is:
the portrait with **the AI mark burned into the pixels**, so a screenshot of
it still carries the disclosure; the profile's page; and the room. When Otis
peels the sticker off on Saturday, the beacon reports itself picked up rather
than 404ing — stickers outlive the things behind them, and a code someone
scans next month should say so in a sentence instead of looking broken.

#### The 18+ creator, and a sticker in a bathroom stall

The interesting case, because it is the one where the ordinary path and the
dangerous path are the same path. A creator with a rated (18+) profile puts a
QR sticker on the inside of a stall door in a men's room. It will be scanned
by strangers, some of them not adults, and neither the creator nor QRME is
standing there to check.

The design answer is that **the sticker cannot carry anything to leak.**

- **The beacon card contains neither the name nor the portrait.** For a rated
  placement the payload is `age_wall: true` and nothing else — so the camera
  overlay can draw the wall having never held a face, a handle, or a blurb.
  There is no rated content on the sticker for a wrong scan to reveal, because
  the sticker was never given any.
- **The age wall is the ordinary path, not the failure path.** A stranger who
  scanned a sticker has no token, so the age check can *never* pass on a first
  scan. That is not an edge case to handle — it is what every public rated
  beacon does every time, and the wall is built as the normal first screen
  rather than as an error.
- **The wall says the check happens at QRME**, not at whoever put the sticker
  up. A stranger has no reason to trust a code on a door, and telling them
  where verification actually occurs is the difference between a gate and a
  phishing page shaped like one.
- **Rated placements stay one-to-one.** `mode: room` is refused for them. A
  shared room behind an adult QR at a public venue is a different product with
  different moderation questions, and not something anybody should acquire by
  accident because a flag defaulted.

The creator gets what they came for — a code that turns a wall into a way to
find them — and the only thing a wrong scanner reaches is a wall that names
nobody.

Both of these are also why `docs/beacons.md` keeps saying *stranger* rather
than *user*. Everything on the far side of a printed code is somebody with no
account, no context, and no reason to have read anything.

**Placing a beacon for someone else's benefit carries obligations.** A code
in a clinic waiting room or at a recovery meeting will be scanned by people
in a bad hour. The mental-health profiles keep crisis escalation local and
their portraits are deliberately unfunny; do not place a beacon somewhere its
profile is not actually equipped for.

## One conversation, or many

`mode` decides what a scan opens:

- **`chat`** (default) — each person who scans gets their own private
  conversation with the profile. What every beacon did before.
- **`room`** — one shared room, minted when the beacon is placed with the
  profile already in it. Everyone who scans the same sticker joins the same
  conversation, so they are talking to the profile *together*: a class, a
  workshop, a meeting, a Q&A after a set. It stays open until the beacon is
  picked up.

```bash
curl -X POST $QRME/profiles/$PID/beacons \
  -d '{"label":"Tuesday 7pm, church basement","mode":"room",
       "topic":"open share"}'
```

The room page says so plainly — *"you may not be the only one here"* — because
someone who scanned a sticker has no way of knowing otherwise, and a shared
room is a different thing to walk into than a private chat.

Rated (18+) placements stay one-to-one. A shared room behind an adult QR at a
public venue is a different product with different moderation questions, and
is not something to acquire by accident.

## What a stranger is told

Whoever scans has no account and may not know what QRME is, so the page
carries the things they could not otherwise know:

- **The AI mark rides on the portrait itself**, not the page chrome, so a
  screenshot carries the disclosure too. Someone in the studio knows they are
  looking at a synthetic profile; someone who scanned a sticker in a bathroom
  does not.
- **Rated profiles show the age wall.** This is the ordinary path for a
  public sticker rather than an edge case: a stranger has no token, so the
  age check can never pass. The wall also says the check happens at QRME, not
  at whoever placed the code.
- **Picked-up beacons and departed profiles say so** in a sentence. Stickers
  outlive the things behind them.
