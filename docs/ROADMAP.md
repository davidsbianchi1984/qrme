# Roadmap

Where QRME goes from 2.8.0, and what 3.0.0 has to mean before it is
allowed to be called 3.0.0.

This document reserves a band, not a schedule. Nine version numbers are
set aside; what lands in each one is decided when it is built, because a
roadmap that names 2.9.4 eighteen months early is a promise to a number
rather than to a person.

---

## The shape

| Band | What it is for |
| --- | --- |
| **2.9.0 – 2.9.9** | The avenues, one at a time. Each release takes one road that half-works and makes it work all the way to the far end. |
| **3.0.0** | Every avenue functions properly inside the apps. Not new roads — the ones already drawn, all of them, working. |

3.0.0 is a celebration release and it is the only kind of celebration
that survives being looked at: nothing new, everything true.

---

## The avenues

An avenue is a road a person can already see in the product. Chat is an
avenue. Voice is an avenue. Avatar, video, AR, VR, wearables, and the
connections that let a profile act are avenues. Some of them run the
whole way. Some of them stop at a door with a screen behind it and
nothing on the other side of the screen.

The 2.9.x band closes those gaps. Each release takes an avenue end to
end, and the bar is not "there is a screen for it" — the bar is that a
person who has never read this repository can start at the front door and
arrive at the far end without hitting a wall.

### Chat, voice, avatar, video

Furthest along. The room now draws in three formats per viewer — audio,
avatar, video — and the format is the viewer's own: two people in one
room can sit in different formats and neither moves the other's. The
video road renders every approved turn under a daily ceiling the owner
set. What is left here is polish and census, not architecture.

### AR and VR

The one David named explicitly, and the reason 3.0.0 exists as a marker.

>     asked     is there an AR screen
>     mattered  does a headset put you in the room

Today the room has an AR mode and a VR mode, and both are drawn in the
browser — the seats over the device's own passthrough for AR, around a
turntable the drag turns for VR. That is a rehearsal of the thing, not
the thing. Nothing of yours and no room of anybody else's crosses the
wire for it, which is the right property to have built first and the
reason the rehearsal is worth keeping.

What 3.0.0 requires:

- **Connection points to the known American models.** The registry
  already carries four glasses (`rayban_meta`, `meta_display`,
  `google_androidxr`, `xreal_air`) and five gaming platforms
  (`playstation`, `xbox`, `nintendo`, `steam`, `pc`). The list has to
  grow to the American headset and glasses makers a person would
  actually name, and each entry has to be a *connection*, not a logo.
- **However they connect.** Steam, Meta, OpenXR, SteamVR, visionOS,
  Android XR — the road into a device is the device's road, and the
  product does not get to prefer one because it was easier.
- **It ports into the console and renders there.** The end of this
  avenue is not a browser page that says AR. It is the room rendering
  inside the console or the supporting platform, in that platform's own
  environment.
- **The same figures.** AvatarSDK figures — the ones the forge already
  produces — stood inside the existing overlays. Not a second avatar
  pipeline for headsets. A vendor is a slot, never the foundation, and a
  second pipeline is a second foundation.
- **A box for what the camera sees.** On top of the overlay, a window
  showing what the device is actually viewing. In AR that is the
  passthrough; the person needs to see the room *and* the world, and a
  compositor that only gives them one of the two has answered a
  different question.

### Wearables

The watch is its own avenue and it has the same three parts.

- **A list of American makers to pick from**, on the screen, by name.
- **An actual connection to that watch**, established and verifiable —
  not a picker that stores a string.
- **The screens render on the wrist.** Every screen built for JIM-mini
  and for QRME, drawn on watches and wearables, at watch size. The
  console already has 36 working watch faces; that is the paint, and
  this is the plumbing under it.

### Connections and skills, used out loud

A synthetic profile added to a friends list, with connections made and
skills granted, should accept a spoken or typed command *in the room* —
"make that video shorter", "change the background", "put on the jacket"
— and carry it out through the connections it already holds.

The capability is largely built. What is being added is one connection
*into the room and the chat* for video rendering; the rest are made
behind the scenes already. What is missing is the demonstration: the
avenues shown, as screens, in the README files, so that a reader can see
each road being driven rather than being told it exists.

### Connections from the visitor's side

David's design, recorded here because it is not built and should not be
described as if it were.

Today, connections are strictly owner-only. `connect_app` calls
`require_owner`, which takes a strict owner token — no lease, no dock, no
interactor. A visitor cannot connect anything to a profile they do not
own, and there is no adopt route for profiles.

What is wanted: when a user creates a public-facing agent, a *visitor*
should be able to modify the connection side of that synthetic profile —
and those modifications live on the visitor's side. The owner's profile
does not change. Two people can meet the same public agent and have it
reach two different sets of connections, each person's own.

The problem to solve before this can be built, stated plainly: a
connection is a credential. A visitor-side connection means the visitor's
credential, held against somebody else's profile, used in a session the
owner did not authorise and may not see. The data model has to make it
impossible for a visitor's connection to become the owner's, impossible
for the owner to read the visitor's credential, and obvious on both
screens which of the two a given connection is. Until that is designed,
this stays a paragraph and not a route.

---

## An open question: the counts

The product has been described as having "30 some odd connections and all
108 skills". The registry says something else, and the registry is what
ships:

| | Counted from the code |
| --- | --- |
| Connectors in `catalog.CONNECTORS` | **103** |
| Providers | **9** — apple 13, canva 1, gaming 5, glasses 4, google 11, microsoft 8, scrape 16, search 4, work 41 |
| Distinct capabilities across those connectors | **180** |
| Tiered capabilities in `tiers.CAPABILITIES` | **8** |
| Doors in `productmap.DOORS` | **76** |
| Hands in `hands.KEYS` | **22** |

There is no 30 and no 108 anywhere in the data. The gap is worth
resolving before any screen is built that prints a number, because a
screen that claims 108 skills over a registry holding 180 capabilities is
wrong twice — it undercounts, and it teaches the reader to distrust the
next number too. Either the counts David has in mind are a different
grouping that should be named and computed, or the phrasing changes.

Whichever way it resolves, screens print counts *derived from the
registry*, never typed in.

---

## Standing rules for the band

- **Full local suite green over the final tree before any merge.** Not
  over the tree as it was when the feature was written.
- **Every route has a door.** `tests/doorless_routes.txt` stays empty. A
  route with no client screen fails the guard, and an avenue that ends at
  an endpoint nobody can reach is not an avenue.
- **Refusals speak ten languages.** Both backlog files stay at zero with
  a ceiling of zero.
- **A vendor is a slot, never the foundation.** Ready Player Me shut on
  31 January 2026 and the replacements quoted $800/month; the forge runs
  locally because of it. Every new device, headset, or model provider
  added in this band goes in as a slot behind the same seam.
- **Deprecated providers are absent, not disabled.** Sora 2 was
  deprecated on 26 April 2026 and its API shuts on 24 September 2026; it
  is not in `filming.PROVIDERS` and does not get added back.

---

## 3.0.0

Every avenue functions properly inside the apps.

The test is a person, not a checklist: someone who has never seen this
code opens the app, picks any road on the map — chat, voice, avatar,
video, AR, VR, the watch, a profile acting through its own connections —
and drives it to the end without finding a wall. When that is true for
all of them, it is 3.0.0, and we sit down.
