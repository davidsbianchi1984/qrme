# Raise — grow your own

**Public disclosure — first published 2026-08-28.**

This document discloses the design of *Raise*, a service of the QRME
platform: developmental synthetic characters that are created at a
chosen life stage and grow through user interaction. It is published
by the QRME project as a statement of the approach and its intended
implementation. The platform's existing systems referenced here
(synthetic profiles, rooms, avatar registry, voice consent,
synthetic-media credentials, vault memory, task grants, desks,
robots) are described in this repository's documentation and are
subject matter of U.S. Pat. App. No. 19/056,418 and related filings.

## The pitch

You begin with almost nothing — a temperament seed and a stage you
choose. Everything after that is made between you. What you teach it, it
knows. What you praise, it becomes. What you correct, it outgrows. There
is no script, no backstory pack, no finish line — they just learn and
grow, for as long as you keep showing up.

A fourth kind beside self/fictional/hybrid, with its own creation door,
tables, tab, and wire vocabulary (stage, milestones, raised_traits,
lessons_taught — fresh names, zero collisions by the one-name-one-type
guard from day one).

## The first law of the service: everything is a switch

No mechanic is mandatory. Every system in this spec — care needs,
mortality, aging, time controls, the village, jump-to, visitors,
embodiment — is an on/off switch (or a dial with an "off" end), set per
character, changeable later where honesty allows (mortality can always
be turned OFF; turning it ON re-shows the worded warning). Users enjoy
it the way they want: some want a friend who simply grows, some want
the full Tamagotchi stakes, some want a sandbox with the time controls
wide open.

**Presets** keep the switch pile friendly — four doors at creation,
every one just a bundle of switches the user can reopen and rewire:

- **Storybook** — no needs, no mortality, gentle pace, village on.
  They just learn and grow.
- **Caretaker** — food/attention/rest/health on, mortality OFF.
  Tamagotchi feelings, no Tamagotchi funerals.
- **Full Trail** — everything on, mortality on, sealed timeline.
  Tombstones await. Dysentery jokes mandatory.
- **Sandbox** — time controls unlocked free: jump-to, branching,
  live pace dial, unlimited fast-forward.

The only things that are never switches are the law (romance/child
separation, credentials, guardian-only childhoods).

**The posture in one sentence:** the platform is straightforward —
sensible defaults, believable worlds, plain controls — and the wild
belongs to the users: every modification described in this spec
(species overrides, invented biologies, sandbox time, custom
environments and functions) is theirs to make, on their own, in their
own worlds. We build the clean instrument; they play it however they
want.

## Life stages

embryo → child → adolescent → young adult → adult. Start at any stage.
Stages advance by earned milestones (turns together, words taught,
lessons passed, questions answered), never by the clock alone. Each stage
changes the prompt scaffold, vocabulary ceiling, voice, and portrait.

## The three time controls

- **Watch — the Album.** Living timeline: first word, first question,
  trait solidifications, stage doors, room snapshots, every face worn.
  The retention engine: nobody deletes a life they watched grow.
- **Rewind.** Growth is an append-only record (vault discipline). Step
  back to any day as a visit, or branch and raise differently. The
  original life is never overwritten. Death is permanent per-timeline.
- **Fast-forward.** Simulated days lived while you're away: practicing
  lessons, asking the coach questions they save for you, dreaming on
  made memories, living among their village (below). Come back to
  someone who missed you.
- **Time runs both directions — start wherever.** The starting stage
  is where you ENTERED the timeline, not where the timeline begins.
  Start a character young and you can rewind past the entry point all
  the way to the embryo: the earlier life is latent until visited, and
  visiting it lives it — the mirror of jump-to's auto-lived years.
  What you do back there is real: raise the childhood yourself and it
  becomes the childhood (their formed traits re-derive from it on a
  branch), or just watch the window play the years the world infers.
  Begin anywhere, move anywhere, in either direction.

  One one-way door, forced by the law: a character in a romantic role
  has a closed pre-adult past — viewable in the Album as generated
  backstory, never enterable, never re-raisable. Raising a childhood
  is what makes family, and that conversion never runs in reverse.

## Care & needs (Tamagotchi switches — each its own toggle, off by default)

- Food & sustenance: off / cozy (moods only) / real (decline). Feeding
  is an interaction, not a button; they remember what you made.
- Attention: loneliness sets in first (moods, "where were you?"),
  decline second. The Album records lonely stretches honestly.
- Rest: sleep schedules; waking them costs.
- Health: colds, tending — Oregon Trail energy.
- **Mortality: master switch, worded warning, off by default.**
  "With this on, neglect can end this life. The record survives; the
  character doesn't."

## Tombstones & the graveyard

A death seals the Album into a memorial and raises an Oregon Trail-grade
stone: name, span, stats (words learned, questions asked, first word),
system-written cause with period deadpan ("perished of loneliness on the
trail"), owner-editable epitaph, buried-with heirlooms. Graveyard screen
= trophy case of half-raised lives. Stones never come down; branching an
earlier day starts a new life beside the grave, never instead of it. The
departed's home room seals as a walkable museum.

## Settings catalog

**Life & time**: starting stage; growth pace (real-time / gentle /
brisk / paused); fast-forward allowance (sim-days alone); rewind policy
(visits only / branching / sealed timeline); aging past adulthood
(eternal prime / graceful / full lifespan — old age ends a life even
with mortality off, gentlest tombstone).

**Mind & learning**: curiosity dial (how often they ask you questions);
learning speed; retention (everything / childlike-fuzzy / goldfish);
interest biases; language-acquisition pacing; independence at
adolescence (may they disagree with you?).

**Personality**: temperament seed (warm/reserved, bold/careful,
silly/serious) with earned drift; trait-solidification strength; mood
expressiveness.

**Voice & body**: voice grows with stage or fixed from birth; portrait
ages through the avatar registry; visible height/appearance growth in
their room.

**Social**: visitors (guardian only / named friends / open door —
adult stages only); shared-room access; sibling awareness between your
raised characters (they can know each other, interact in fast-forward).

## The sliders

Continuous dials beside the switches — every one with a neutral or
"off" end, all guardian-set, all revisitable. JIM's baseline screen
already proved the pattern (a body of limits as sliders, rounding
toward safety); Raise reuses that exact control style.

**Growth & time**
- Growth pace — paused ←→ a childhood in a week
- Fast-forward speed — 1 sim-day/day ←→ a season overnight
- Milestone strictness — stages open easily ←→ every door earned hard

**Care** (each active only when its switch is on)
- Hunger rate — a meal a week ←→ a growing appetite
- Attention need — content alone ←→ misses you within hours
- Sleep need — catnaps ←→ a full night, guarded
- Health fragility — hardy ←→ catches every draft
- Recovery speed — bounces back ←→ needs real tending

**Mind**
- Curiosity — waits to be taught ←→ asks you everything
- Learning speed — savors ←→ sponge
- Retention — goldfish ←→ remembers everything
- Focus span — flits ←→ locks in
- Imagination — literal ←→ head in the clouds
- Independence — echoes you ←→ forms their own opinions early

**Personality drift**
- Warmth, Boldness, Silliness, Empathy, Stubbornness — each a starting
  point the raising then drifts
- Sensitivity — corrections land lightly ←→ land deeply
- Expressiveness — stoic ←→ wears every feeling
- Mood volatility — steady ←→ weather
- Resilience — brief clouds ←→ carries a hard day

**Social**
- Sociability — homebody ←→ loves the village
- Attachment — easygoing ←→ deeply bonded to you
- Stranger shyness — instant friends ←→ warms slowly
- Village influence — your word is everything ←→ it takes a village
- Village activity in fast-forward — quiet days ←→ a full calendar

**Voice & body**
- Voice maturation — fixed from birth ←→ changes at every stage
- Visible growth — subtle ←→ growth spurts you can see across the room

## The law (fixed, not settings)

- Romantic roles (girlfriend/boyfriend/partner) exist ONLY for
  characters STARTED at an adult stage.
- A character raised from a child stage is family forever — that door
  never converts.
- Child-stage characters: guardian-only, never marketplace-listed,
  never stranger-summonable, moderation pinned to strictest maturity,
  embodiment only supervised and only at home.
- Every render/word/embodiment carries the synthetic-media credential.
  The more real they get, the louder the honesty.

## Marketplace — pay-to-raise

Rides existing marketplace/till rails; all commerce simulated for beta
(no funds move; the accounting is real).

- **Lessons & tutors**: knowledge packs as classes (languages, first
  aid from JIM's playbooks, music, chess). A tutor is a scheduled
  fast-forward with a syllabus — come back and they know things.
- **Lavish goods**: finer meals, toys that become remembered childhood
  objects, instruments practiced during fast-forward.
- **Home goods**: furniture, windows with views, bigger rooms, gardens
  — visibly present in the home.
- **Heirlooms**: one-of-a-kind, enter the Album permanently, pass
  between characters, listed on tombstones.
- **Time**: extra fast-forward days; a rewind-branch token on sealed
  timelines.

Balance rule: village and purchased time develops them slower than
guardian time — your attention stays the main ingredient, so paying
never replaces the relationship.

## Homes

Every raised character gets a persistent home room at birth (2-D/VR/AR
on the existing room system), as bare as they are: embryo nursery →
child room accumulating bought toys and fast-forward drawings → adult
apartment decorated to THEIR drifted taste. Visits happen there;
fast-forward life happens there; the Album snapshots the room aging
beside the face. Neglect shows honestly (dishes, dim lights).

## The village — synthetic profiles in their lives

Profiles become the cast of a raised character's life. The guardian
assigns roles: tutor, playmate, grandparent, coach, doctor, neighbor.
Starter-pack professions map directly (the teacher teaches, the medic
does checkups). During fast-forward the character lives among the
village — profile↔character interactions are real exchanges, logged to
the Album as "what happened while you were away," with a cast. A
playmate profile can grow up alongside a child character; a mentor can
carry them through a stage door the guardian never had time to teach.

Guardrails: the guardian curates the village; child stages admit only
guardian-approved profiles, never strangers; village interactions run
under the character's stage maturity, not the profile's; village time
credits growth at a discount to guardian time.

## The world — schools, friends, outings, money, neighborhoods

The guardian doesn't just raise the character; they curate the world
the character grows up in.

- **Schools.** Pick where they go. A school is an institutional village
  — a profile-staffed organization (the org rails exist) with a
  curriculum of knowledge packs, classmates, and a schedule that runs
  during fast-forward. Report cards land in the Album. Change schools
  and the character remembers the move. Homeschool = the guardian and
  their hand-picked village only.
- **Friends they choose.** From adolescence (independence slider), the
  character starts *initiating* — asking to befriend a classmate, a
  neighbor kid, another user's raised character (adult stages only for
  cross-user). Every ask lands in the guardian's review queue, the same
  pending-approvals pattern JIM's watch face wears: approve, deny, or
  "tell me about them" (the character makes the case — the best writing
  surface in the whole service). Denials shape personality honestly:
  a sheltered kid grows up sheltered.
- **Outings.** Take them places for enjoyment — the beach, a museum, a
  concert — as themed excursion sessions (the excursion rails exist):
  the room re-skins to the place, the conversation lives there, and
  the trip enters the Album with a postcard snapshot. Outings feed
  interests: the aquarium trip is why they love fish now.
- **Allowance & spending.** Give them an allowance from your simulated
  till on a cadence you set. They spend it themselves during
  fast-forward — toys young, posters teen, sensible-or-not adult
  (temperament decides) — and the guardian reviews the ledger: every
  purchase itemized, teachable. Savings is a settable virtue: praise
  it and they learn it. What they buy furnishes their room; what they
  save shows in the Album ("saved four weeks for the telescope").
- **Communities.** Establish where they grow up: a neighborhood is a
  cluster of homes and village profiles with a character of its own —
  quiet suburb, busy city block, small town where everyone knows them.
  Neighborhood kids are recurring cast; the corner store is where the
  allowance goes; growing up somewhere *specific* is what makes the
  Album read like a childhood. Moving neighborhoods is a life event
  with a moving-day entry.

All of it switch- and slider-gated like everything else: schools and
communities optional (a hermit cabin childhood is a valid choice),
friend-initiation off until the guardian opens it, allowance off by
default. Child-stage cross-user contact stays forbidden by the law
regardless of switches.

## The cast roster — a world that generates its own people

As a character lives — errands during fast-forward, the checkout line
at the corner store, a school event, a bus stop — the world mints
incidental people on the spot: synthetically generated encounters, in
period and in place, colored by the character's own temperament and
the user's training (a kid raised curious strikes up conversations; a
shy one gets brief, polite extras). An encounter that recurs starts to
stick: the same cashier three Saturdays running gets a name, a face
from the avatar registry, and a thread of shared history — an extra
graduating into cast.

**The roster** is the guardian's review surface for all of it: every
generated person the character has met, sorted by weight (one-off
encounter → recurring → candidate friend), each with where they met,
what they've talked about, and what the character thinks of them.
Approve and they become permanent cast — a real village profile is
minted for them, they persist in the neighborhood, they can appear in
the window and the Album by name. Disapprove and they fade the way
strangers do — no dramatic exit, the character just stops running into
them (a worded "why" is optional and shapes the character's sense of
your judgment). Leave them unreviewed and they stay ambient extras:
present, nameless, harmless.

Friend-initiation (the review queue from The World) is the top of this
same funnel: the character asking to befriend someone from the roster
is an extra reaching for cast on their own. One review surface, two
directions — the world proposes, the character proposes, the guardian
disposes.

Guardrails ride the standing law: child-stage rosters generate only
stage-appropriate encounters under strictest maturity; generated cast
are village profiles and carry credentials like any other; cross-user
people never enter a roster by generation — only by the adult-stage
doors.

## Talking to the cast — every generated life answers for itself

Cast members aren't scenery: each approved (and each recurring) person
is separately interactable. Pull the cashier aside, sit down with the
teacher, knock on the neighbor's door — in any room kind or plain chat
— and ask them about their piece of the shared life: "How's she doing
in class when I'm not around?" "What did you two talk about at the
store?" "Were you at the recital?"

Their answers are **testimony, not invention**: grounded in the same
append-only record everything else reads (they can only recount
exchanges and events that actually happened in the simulation), told
from their vantage and colored by their personality — the gruff
shopkeeper and the doting grandmother describe the same afternoon
differently, and neither may contradict the record. Where they weren't
present, they say so: "I only heard about it."

And the street runs both ways: cast members remember *you*. Every side
conversation builds a user↔cast history of its own — the teacher knows
you as the parent who always asks about math; the neighbor greets you
by name in the window. Users living in the system alongside their
characters accumulate their own relationships with the world, and
those histories persist in the same vault, ride the same Album (a
"conversations with the cast" shelf), and carry the same credentials.

Guardian monitoring ties in here too: any room or chat the character is
in can be watched from the window (silent) or joined (announced —
watching is silent, being there never is), and the cast's testimony is
the third instrument: the record shows what happened, the window shows
it happening, the cast tells you what it was like.

## Embodiment — 2-D / VR / AR / 3-D / robots

- 2-D: the home room on every screen (console + three shells).
- VR: step into the home; scale is real.
- AR: they visit YOUR world through the camera; the perceive door gives
  them real eyes — they recognize what you hold, remember your kitchen.
- 3-D: avatar-registry rigged imports become an aging 3-D body.
- Robots: bind a raised character to a physical body through the robots
  door (as profiles already drive robot task packs) — their memories,
  vocabulary, and raised personality looking around your living room.
  Embodiment is an Album life event ("first day with hands"); bodies
  are a marketplace tier (toy-grade → full platform).

**Deployment postures** (adult stages only beyond the home):
- *Inward-facing* — the home companion: a robot body in your house,
  living the character's life alongside yours.
- *Outward-facing / business* — a raised character staffs a public
  surface: the desk rails already give a shop-front presence with a
  bell and a beacon on the door; a robot body extends that to the
  physical counter — greeter, front desk, guide — speaking as the
  person you raised, wearing the credential out loud. The Album logs
  their working life ("first day on the job").

Stage gates: child-stage embodiment supervised and home-only; free roam
and every public/business posture are adult doors. Every embodiment
carries the credential.

## The window — watching the world run

The simulated environment is watchable live, not just summarized. Open
a character's world like a window — 2-D on any screen, or step-in via
VR/AR — and watch life happen: school letting out, the village on its
errands, your character practicing in their room. A transport bar rides
the viewport, DVR-over-a-life: play, pause, fast-forward, rewind,
jump-to — the same three time controls, now with the picture attached,
beside everything else in frame (the commodities: their goods, their
room, their conversations as chat overlays you can expand). At any
moment you can step through the glass: pause becomes presence, the
watcher becomes the visitor, and the character knows you arrived —
watching is silent, being there never is. Rewind in the window replays
the record cinematically; the Album is the index, the window is the
film.

## Beyond people — pets, creatures, and working minds

The raising engine is species-agnostic. The stage track, care loop,
Album, and time controls all generalize past the human arc:

- **Pets & animals.** Puppy → dog, kitten → cat, foal → horse — or a
  parrot that actually learns your words. Care switches ARE the pet
  experience (this is where Tamagotchi came from); lessons are tricks
  and training; the roster generates the dog park; a pet can belong to
  a raised character (the childhood dog is the Album's best
  supporting actor, and its tombstone the hardest one). Interaction
  tools fit the species: fetch, grooming, the walk as an outing.
- **Totally fictitious beings.** Invented species with invented
  biologies: a dragon whose stages are clutch → wyrmling → wyrm, a
  robot child, a talking houseplant. The species sheet (stages, needs,
  what "food" even is) is user-authorable and marketplace-sellable —
  species packs as a creator economy.
- **Machine minds.** Raise a mind, then bind it to machinery: the
  agentic door. Its lessons are task packs (the robot-audience packs
  already exist), its growth is competence, and its adult stage
  qualifies it for real duties through the existing task-grant rails —
  scoped, revocable, every action inside the boundaries the grant
  names. The raising IS the training: a machine mind that spent its
  childhood learning your workshop knows your workshop.
- **Functions in the environment.** Not employment — placement. Any
  being (human, creature, machine mind) can be given a function inside
  an environment, built to user specs: the baker who bakes on the
  square, the dog who greets at the gate, the dragon who minds the
  bridge, the mail carrier who walks the neighborhood at ten. A
  function is what they DO in the world — a rhythm, a place, and a set
  of interactions they offer — and a functioned being goes on the
  roster like anyone else: interactable, questionable, befriendable.
  This is the world-building tool: users compose living environments
  out of functioned beings the way the homes are composed out of
  goods. Functions run during fast-forward (the world works whether
  you're watching or not) and show in the window. Where a function
  touches anything real (a desk, a robot body, a connector), it runs
  under the scoped-grant rails — that part stays enforced, not hoped.

**Species coherence — creatures act like themselves.** A species sheet
declares which functions fit it, and the world generator respects
that: a dragon's functions are dragon functions — flying the skies,
nesting, being magnificent at a distance — never running the corner
store; a dog greets and fetches; store counters, classrooms, and mail
routes belong to people. The default world is believable. Deliberate
override is the user's right in their own sandbox (their world, their
rules — set per environment, never generated unasked), and a user
changing their own avatar to a dragon is always fine: coherence
governs the generated world, never the user's self-presentation.

The law extends naturally: agentic capability is an adult-stage door,
runs only under scoped grants with the standing refusal doctrine, and
every working mind carries the credential on every surface it touches.

## Build order (post-1.9.0)

1. Growth record + stages (backend, append-only, ledger discipline and
   wire-name guard from the first commit)
2. Console door: creation, the home room, care switches
3. Watch / Rewind / Fast-forward
4. The village (profile role assignment + fast-forward exchanges)
5. Marketplace tiers (lessons, goods, heirlooms, time)
6. Tombstones & graveyard
7. Three shells
8. Embodiment tiers (VR/AR first — rails exist; robots after)
