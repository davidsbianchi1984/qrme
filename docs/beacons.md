# Beacons — leaving a profile somewhere

A beacon is a synthetic profile left in a physical place. Print the QR, stick
it where the people who need that profile already are, and anyone who scans
it lands on the profile's page.

    POST /profiles/{id}/beacons   place one
    GET  /b/{beacon_id}           where the printed QR points
    DELETE /beacons/{beacon_id}   pick it back up

`scan_url` is the one to print or share. `summon_url` is the JSON surface for
clients that want data rather than a page.

## What a scan actually does — three different answers

Whether the portrait can appear *in the camera*, without going anywhere,
depends entirely on which camera is looking.

| Scanned with | What happens | Status |
|---|---|---|
| The stock camera app | A URL chip. Tap it and `/b/{id}` reveals the portrait. | shipped |
| **The QRME app** | **The portrait is drawn on the sticker in the live viewfinder.** No tap, no page. | shipped (iOS) |
| The stock camera, via an iOS App Clip | An App Clip Card — portrait, name, action — over the camera, before going anywhere | needs your Apple account |

**The stock camera cannot be made to render anything.** Reading a QR and
offering its URL is the entirety of what it exposes; there is no API for a
third party to draw into that viewfinder. Anyone claiming otherwise is
describing one of the other two rows.

### In the QRME app

`BeaconScannerView` owns the viewfinder, so it can draw on it. Vision reads
the code, `GET /b/{id}/card` returns the little that an overlay needs, and
the portrait is composited onto the quadrilateral Vision reported — tracking
the sticker as the phone moves. Tapping opens the full page; not tapping
still showed you who it is, which was the point.

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
