# Beacons — leaving a profile somewhere

A beacon is a synthetic profile left in a physical place. Print the QR, stick
it where the people who need that profile already are, and anyone who scans
it lands on the profile's page.

    POST /profiles/{id}/beacons   place one
    GET  /b/{beacon_id}           where the printed QR points
    DELETE /beacons/{beacon_id}   pick it back up

`scan_url` is the one to print or share. `summon_url` is the JSON surface for
clients that want data rather than a page.

## What a scan actually does

A phone's camera app can only **open a URL** — it cannot draw anything over
the viewfinder. So "aim at the sticker and the profile appears" is a landing
page that reveals the portrait the moment it paints. That is what most
"it generated right there" experiences are.

True augmented reality — the portrait anchored to the sticker in 3D as you
move the phone — needs either WebXR (support on iOS Safari is partial and
requires an explicit camera permission prompt, which is a hard sell for a
stranger scanning a sticker) or the native apps, which can take a deep link
and composite properly. The native route is the realistic one; it is not
built yet.

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
