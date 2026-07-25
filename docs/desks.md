# Live desks: a real person, and the mark that must not be on them

Everything else in QRME is a synthetic profile, and every render of one carries
the AI mark. A desk is the opposite case — an actual human offering a service —
and the important part of the design is what it refuses to do.

## The mark is off, and that is not a relaxation

**A desk never carries the AI watermark.** Stamping "AI" on a real person is
not a cautious default. It is a false statement about them: it tells a visitor
that the human they are waiting for does not exist. A mark is a claim, and a
claim has to be true in both directions or it is worth nothing in either.

`tests/test_desks.py` checks both halves in the same file, on purpose:

| | AI mark |
|---|---|
| Synthetic profile | always, and it cannot be designed away |
| Live desk | never, anywhere on the card or the view |

An unmarked synthetic face is the failure everyone expects. Marking a real
human is the one nobody checks for, which is exactly why it is pinned next to
its opposite.

## Absence is not the disclosure

An unmarked card could equally be an AI whose badge got dropped, so a desk
makes the claim positively — *Live person — not AI* — and shows who vouched for
it, on what basis, and when.

That claim is **recorded, not proven**. QRME stores an attestation; it does not
independently verify a human, and saying otherwise would make this badge as
hollow as an unmarked AI card. The card carries that sentence next to the claim
rather than in a policy document.

A desk cannot be opened without an attestor and a basis. A "not AI" badge that
nobody stands behind is worse than no badge, because it would be believed.

**Signing raises it.** An attestation bound with
`binding_kind="desk_human_attestation"` at the `high` tier
([docs/signatures.md](signatures.md)) turns "we wrote down who said so" into a
signature a counterparty can verify without trusting this deployment. The card
reports `attestation.signed` and the signature id when one exists.

## What a visitor looks at

Not a portrait. We have no photograph of the person and do not go looking for
one; a desk shows a **camera view of the desk itself**. An empty chair with a
sign on it says everything a visitor needs to know, and it depicts nobody.

`GET /desks/{id}/view.webp` serves that view. When a desk has no camera
configured, a sample frame stands in and the card reports `feed.live: false` —
presenting a still frame as a live feed would be the same class of lie as
marking a human as AI, so the clients label it **SAMPLE VIEW** rather than
**● LIVE**.

## The bell

The sign taped to the chair says to ring the bell. A visitor looking at that
chair through a screen cannot reach it, so the button is on the screen they are
already looking at — in the iOS, Android and Windows apps.

`POST /desks/{id}/bell` takes no token. The person standing in front of an
empty chair is exactly the person who has no account, and demanding one at that
moment would be demanding it at the worst possible moment.

It is rate limited, because a bell anyone can ring from anywhere is a doorbell
prank waiting to happen:

* an identified caller waits **5 minutes** between rings;
* an anonymous caller — a stranger from a beacon, with no identity to limit
  against — is capped **per desk**, at 30 seconds.

A closed desk has no bell at all, and says so rather than accepting a ring
nobody will hear. An *attended* desk still accepts one: they are here, but
looking elsewhere, and that is a reason to ring rather than a reason not to.

The owner sees who rang while they were away (`GET /desks/{id}/rings`, their
token only — who called on a tradesperson is theirs, not a visitor's to browse)
and clears each one as they answer it.

## 18+ streams

An adult stream is **not a separate tier**. It is the same live desk behind the
same verified-adult gate every other 18+ surface already uses —
`rated.viewer_is_adult`, reused rather than re-implemented, because a second
gate is a second thing to get wrong and the weaker one always wins.

What changes when `rated` is set:

* **The card becomes an age wall** for anyone unverified: existence
  acknowledged, and nothing else. No name, no trade, no view, and above all
  **no location** — where a performer physically is has nothing to do with
  watching them, and it stays withheld even past the wall.
* **The view, the bell, and joining all require the same token.** The bell is
  public on an ordinary desk, because the visitor at an empty chair is exactly
  the person without an account. Handing anyone a way to buzz an adult
  performer from anywhere is a different thing, so it is gated.
* **Only they can open it.** The repo's existing hard line is that adult mode
  is never available for a profile of *another* real person. A stream is a real
  person by definition, so the same line lands here as: the attestor must be
  the owner, attesting for themselves. A third party opening an 18+ stream in
  someone else's name is the exact shape this refusal exists to prevent.
* **Still no AI mark**, on the wall or past it. There is a person on the other
  end, and that is true whether or not you are old enough to see them.

## Joining

`POST /desks/{id}/join` returns the room whoever is watching shares — a room
rather than a call per viewer, because that is what a stream is. It is minted
on first arrival, so a desk nobody has visited carries none.

## Leaving the desk behind — beacons

A profile can be left somewhere physical as a printed QR code
([beacons.md](beacons.md)). A desk can too, and it is arguably the more
natural of the two: the sticker goes on the shop door *because* nobody is
behind it right now, which is the exact situation the bell was built for.

The two are the same gesture aimed at opposite things, and the differences are
the whole feature:

| | profile beacon | desk beacon |
|---|---|---|
| what is revealed | somebody who does not exist | somebody who does |
| the badge | **AI** — on the portrait, so a screenshot carries it | **Live person — not AI** — green, top-right, worded as a claim |
| the way in | a conversation, or a shared room | the bell, and the live stream |
| a rated one, scanned | age wall | age wall |

The badge placement is deliberate: green and top-right against the AI mark's
neutral bottom-left, so the two cannot be confused at the glance a scanner
actually gives them. Absence of the AI mark would not be a disclosure on its
own — an unmarked card could be a synthetic profile whose badge got dropped —
so the desk states the claim positively and names who vouched for it, right
there on the page.

Two things follow from the scanner being a stranger with no account, and
neither is a limitation to work around:

- **Their ring is anonymous**, so it takes the per-desk cooldown (30s) rather
  than the per-caller one (5min). A printed code is reachable by anyone walking
  past, which is the entire threat model.
- **A rated desk always shows them the age wall.** There is no token on a
  sticker scan, so there is nothing that could clear it. The wall withholds the
  name and, above all, the location: whereabouts on an adult listing is a
  safety matter, and a sticker is by definition somewhere physical.

The scan page is one self-contained document for the same reasons the profile
one is — a camera app's in-app browser, on cellular, from cold. The bell is the
single script on it, and it posts to a **relative** URL: an absolute public
base would ring a bell on a different host when the code is scanned over a LAN.

## Endpoints

```
POST   /desks                        open a desk (attestation required)
GET    /desks/{id}                   the card: who, presence, human claim, bell
GET    /desks/{id}/view.webp         the camera view — no watermark, no-store
PUT    /desks/{id}/presence          attended | away | closed   (desk token)
PUT    /desks/{id}/portrait          the owner's own photo, or clear it (token)
PUT    /desks/{id}/camera            point it at a real camera        (token)
POST   /desks/{id}/bell              ring it — public, rate limited
GET    /desks/{id}/rings             who rang                   (desk token)
POST   /desks/{id}/rings/{ring}/ack  mark one answered          (desk token)
POST   /desks/{id}/join              join the live stream

POST   /desks/{id}/beacons           print the desk onto something (desk token)
GET    /desks/{id}/beacons           every code, with its scan count  (token)
DELETE /desk-beacons/{id}            peel the sticker off             (token)
GET    /desk-beacons/{id}/qr.svg     the printable code — public
GET    /d/{id}                       what a phone opens on a scan
GET    /d/{id}/card                  the same scan, as JSON for the apps
```

Placing a beacon is owner-only. Anyone who could print a code for a desk they
do not hold could put a stranger's name and whereabouts on a sticker and put it
anywhere — worse than the feature is worth.

For a rated desk every public surface above also requires an interactor token
whose verified birthdate shows 18 or older:

```
GET    /desks/{id}                   → age wall without one
GET    /desks/{id}/view.webp         → 403 without one
POST   /desks/{id}/bell              → 403 without one
POST   /desks/{id}/join              → 403 without one
```
