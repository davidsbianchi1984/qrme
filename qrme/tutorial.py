"""The help assistant, walking you through the whole app.

:mod:`qrme.help` answers a question somebody thought to ask. This is the other
half of the same surface: a **guided walkthrough** for somebody who does not
yet know what there is to ask about. Same assistant, same posture, and the
posture is the point — it is furniture, not a thirty-fifth character:

* **No name and no face**, for the reason `help.py` gives at length. A tutorial
  guide with a persona would be the most convincing synthetic profile on the
  platform, met by every user on their first minute, at the exact moment they
  have the least idea what is synthetic here.
* **It never speaks as anybody**, and it hands persona questions back the same
  way `help.ask` does.
* **It writes nothing.** A tutorial that placed a beacon or sent a message "to
  show you how" would be a tutorial that acted on somebody's account before
  they understood what the account was. Every lesson says *what to tap*; none
  of them taps it.

**The lessons are written prose and work with no model configured**, like
`help.TOPICS`. A walkthrough that needs an API key is a walkthrough that is
missing on a self-hosted deployment, which is a supported setup here rather
than a degraded one.

**Voice and text are the same lesson, rendered differently, not two scripts.**
:func:`say` is the only place that difference lives. Spoken, a screen number is
noise — *"screen eighty-one"* helps nobody who is listening — so voice drops
the numbers and the route names and keeps the sentence. Two hand-written
versions would drift, and the spoken one would be the one nobody re-read.

**The walkthrough cannot quietly fall behind the app.** :data:`LESSONS` names
the screens each step is about, and a test asserts every screen in the gallery
is claimed by some lesson. Add a feature, draw its screen, and the tutorial
fails until somebody has said what it is for — which is the only way a guided
tour of a moving product stays true.
"""

from __future__ import annotations

from . import db

# The disclosure the walkthrough carries, matching `help.DISCLOSURE` in spirit:
# this is the product talking about itself, not a character.
GUIDE = ("This is QRME's own guide — not a profile, and not a person. It has "
         "no name and no face on purpose, because everything here that looks "
         "like somebody is marked as AI, and a guide with a face would be the "
         "first thing you met that was not.")

# The walkthrough, in order. Each lesson is:
#   chapter   — which part of the app
#   title     — what this function is called
#   what      — what it does, in a sentence somebody can act on
#   screens   — the screen numbers it is about (the binding to the gallery)
#   try_it    — one concrete thing to do next
#
# Ordered so that nothing refers to a thing that has not been introduced: you
# are a profile before you have a room, and in a room before you lend it a
# microphone.
LESSONS: tuple[dict, ...] = (
    dict(key="guide", chapter="Getting started", title="This guide",
         what="You are reading it. The walkthrough is a fixed set of written "
              "steps, not something a model makes up as it goes — so it says "
              "the same thing every time and it still works on a deployment "
              "with no model configured at all. Every screen in the app is "
              "explained by one of these steps, and a test keeps that true: "
              "add a feature, draw its screen, and the suite fails until "
              "somebody has written what it is for. If you are looking at a "
              "screen and do not know what it is, you can look it up by "
              "number. The guide has no name and no face, and that is "
              "deliberate — on a platform where everything that looks like "
              "somebody is marked as AI, a guide with a persona would be the "
              "first thing you met that was not.",
         screens=(160,),
         try_it="Press Start the tour, or look up the screen you were just on."),
    dict(key="welcome", chapter="Getting started", title="What QRME is",
         what="QRME makes AI synthetic profiles — characters with a persona, a "
              "memory, and a relationship with each person who talks to them. "
              "Every one is marked as AI, and the mark is burned into the "
              "portrait's pixels so it survives a screenshot.",
         screens=(1, 2, 19), try_it="Look at the mark on any portrait here."),
    dict(key="signup", chapter="Getting started", title="Signing up",
         what="Log in, verify you are a real person once, choose what the app "
              "may reach, pick a plan and pay. You can decline the plan and "
              "keep looking — a visitor reads any public page — and the free "
              "plan makes things too. If you later tap something your plan "
              "does not include, the app says which plan it needs and what it "
              "costs rather than refusing you flatly.",
         screens=(132, 133, 134, 135, 138),
         try_it="Open Pick a Plan and read the first option."),
    dict(key="make_one", chapter="Getting started", title="Making a profile",
         what="You describe who it is and it answers in character from the "
              "first message. Genesis builds one from four questions if you "
              "would rather be asked than write.",
         screens=(3, 4, 5, 16),
         try_it="Create one, or open Genesis and answer the four."),
    dict(key="blend", chapter="Getting started", title="Blending a profile",
         what="A hybrid blends several people into one persona — both "
              "grandparents at once, in the shares you choose, each lending "
              "the side of them you name. It says openly that it is a blend "
              "and never claims to be any single one of them. Rated profiles "
              "never blend, and a stranger's profile needs a public listing.",
         screens=(142,), try_it="Pick two profiles and press Blend."),
    dict(key="talk", chapter="Getting started", title="Talking to it",
         what="Every reply is explained: what it drew on, and why. A profile "
              "remembers you specifically, and treats you according to the "
              "relationship you have with it. Tell it where you are — a "
              "trailhead in the rain, a kitchen at seven — and the reply "
              "meets you there instead of nowhere.",
         screens=(6, 7, 8, 9, 144),
         try_it="Send one message and open the why."),
    dict(key="health", chapter="Getting started", title="How it is doing",
         what="Profile health, stats, and the transparency page — what it "
              "knows, where that came from, and what it is allowed to do.",
         screens=(10, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30),
         try_it="Open Profile Health and read the sources list."),
    dict(key="control", chapter="You are in control", title="The controls",
         what="Moderation, steering, boundaries, and the switches that turn "
              "any of it off. Nothing here runs without an owner enabling it.",
         screens=(14, 15, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40),
         try_it="Open the Control Center and turn one dial."),
    dict(key="model", chapter="You are in control", title="Who is answering",
         what="Every profile's replies come from a model you can see and "
              "change — a tile per provider with its own glyph, one click "
              "to swap, Automatic for whichever is configured. Your own "
              "key stays on this device and rides only your requests, and "
              "an amber notice says plainly when the built-in offline "
              "helper is what will answer instead of a real model.",
         screens=(141,),
         try_it="Open Which Model Answers and read which tile is active."),
    dict(key="voice", chapter="You are in control", title="Your own voice",
         what="A profile can speak in your voice, and the permission comes "
              "first — before anything is recorded. Saying it is your own "
              "voice is an attestation, not a checkbox: there is no path here "
              "for anybody else's. What you enroll is counted rather than "
              "scored, so a thin enrollment is called thin instead of being "
              "labelled ready, and anything spoken in that voice carries the "
              "watermark and says out loud that it is synthesized. Withdrawing "
              "deletes the samples and silences the voice; the withdrawal "
              "itself stays on record.",
         screens=(147,),
         try_it="Open Voice and read step 1 before granting anything."),
    dict(key="whowrote", chapter="You are in control",
         title="Finding out who wrote something",
         what="Paste any passage and QRME names the profile that produced it, "
              "from the text alone — no credential id, and it keeps answering "
              "after the wording has been changed. It never answers with a "
              "bare yes: you see how many passages matched out of how many "
              "were stored. Below a threshold it names nobody at all, because "
              "ordinary phrases travel between unrelated texts and a "
              "coincidence must not read as an accusation.",
         screens=(148,),
         try_it="Paste something one of your profiles wrote, then change a word and try again."),
    dict(key="market", chapter="Out in the world", title="The marketplace",
         what="Share or license a profile, sell a knowledge pack, take a "
              "placement. Money here is simulated and every response says so.",
         screens=(11, 12, 13, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50),
         try_it="Browse the marketplace and open one listing."),
    dict(key="reach", chapter="Out in the world", title="Being found",
         what="A handle, a tag, or a printed QR beacon left somewhere the "
              "profile is useful. A scan lands a stranger on its front page.",
         screens=(17, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
         try_it="Claim a handle, then look at the beacon page it makes."),
    dict(key="desks", chapter="Out in the world", title="Live desks",
         what="A real person behind a stream, badged *Live person — not AI* — "
              "the mark inverted, because there is somebody there.",
         screens=(61, 62, 63, 64, 65, 66, 67, 68, 69, 70),
         try_it="Open a live desk and ring the bell."),
    dict(key="placement", chapter="Out in the world",
         title="Marketing a rated profile",
         what="An adult-mode profile can be advertised at an adult venue — a "
              "creator platform, a directory — as a link or a printed code. "
              "The venue never becomes the gate: every summon of a rated "
              "profile resolves through QRME's own 18+ age wall, wherever the "
              "code or the handle was found. Taking a placement down "
              "deactivates the code rather than repointing it, so anything "
              "already printed stops working instead of leading somewhere "
              "new. You are shown counts and rates; nobody who scans is ever "
              "identified.",
         screens=(162,),
         try_it="Open Where it is marketed and read the venue note."),
    dict(key="social", chapter="People", title="Friends, pages and the feed",
         what="A friends list, a page you build yourself in real HTML, and a "
              "feed that tells you why each thing is in front of you.",
         screens=(71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 82, 83, 84, 85, 86,
                  87, 88, 89),
         try_it="Open your page and change the theme."),
    dict(key="mic", chapter="People", title="Lending a microphone",
         what="In a voice room your microphone is busy carrying your voice. "
              "This lends the profiles the one on your watch, so they hear you "
              "as well as read you. Everyone in the room is shown that you "
              "did, it stays narrow enough to reach only you, and it ends when "
              "the room does.",
         screens=(81, 120),
         try_it="Lend it, then look at what the room sees."),
    dict(key="camera", chapter="People", title="Sharing your camera",
         what="Channel 2 lent the profiles an ear; this lends an eye. Point "
              "your camera at the thing and somebody watches live — a "
              "mechanic looking at your engine, a plumber watching you point "
              "at the joint. What the camera is pointed at decides who may "
              "watch: a thing, a document or a place is open to anyone, and a "
              "body goes to a real person rather than a synthetic profile. "
              "You point it — no viewer can zoom, focus, use the torch or "
              "take a shot. It records nothing unless you say so, and it ends "
              "when you say stop or when the room does.",
         screens=(136, 137),
         try_it="Open What's In Shot and read the last card."),
    dict(key="fullscreen", chapter="Watching", title="Full screen and sideways",
         what="Any live surface fills the phone. A long press dims everything "
              "but the controls and brings the help button back; turning the "
              "phone gives you it sideways.",
         screens=tuple(range(90, 113)),
         try_it="Press and hold on a live video."),
    dict(key="together", chapter="Watching", title="Watching together",
         what="A watch party shares a position rather than a player, and a "
              "synthetic profile in the room is told it has not seen the "
              "video — so it says so instead of inventing an opinion.",
         screens=(113, 114, 115),
         try_it="Start a party from a posted video."),
    dict(key="work", chapter="Working", title="Agreeing before work moves",
         what="An exchange lists what crosses in each direction, what is "
              "included and what is not. Both sign, and any change to the "
              "document voids both signatures.",
         screens=(116, 117), try_it="Draft one and read the manifest."),
    dict(key="games", chapter="Working", title="Playing alongside",
         what="A profile can sit beside you in a game as a companion or a "
              "coach. Nothing in the lobby ever plays: no input, no second "
              "controller, no console of its own.",
         screens=(122, 125), try_it="Open a lobby and read what it cannot do."),
    dict(key="proceeds", chapter="Working", title="Where the money goes",
         what="A profile can raise money — for the person behind it, or for "
              "the loved ones and organizations they named. You route the "
              "proceeds in advance, in shares that must add to one hundred; "
              "every donation splits at the door onto the ledger, the donor "
              "always sees the names, and when the owner is gone the pen "
              "passes to the successor they chose.",
         screens=(145,),
         try_it="Name a loved one and a share, then open a campaign."),
    dict(key="ecosystem", chapter="Working", title="Departments that coordinate",
         what="An organization gives each department its own role agent — "
              "your profiles, staffed to desks. Ask them to coordinate on a "
              "goal and each pulls from its own scoped material, offers its "
              "part, and the lead agent composes the joint plan. Revoke a "
              "department's grant and its pulls stop instantly; with the PDI "
              "tandem on, every plan is sealed into your vault.",
         screens=(146,),
         try_it="Staff two departments and give them one goal."),
    dict(key="predict", chapter="Working", title="What they would do",
         what="Ask a profile to model the likely decision and the steps the "
              "person would take in a scenario you describe. The answer is a "
              "watermarked prediction, never their word, and its confidence "
              "is earned from real material — sources and remembered "
              "conversations — not from how sure the model sounds.",
         screens=(143,),
         try_it="Give it a scenario and read where the confidence came from."),
    dict(key="role", chapter="Working", title="Advisor, collaborator, operator",
         what="You can say how a profile should work a turn: an advisor weighs "
              "it and recommends, a collaborator works the thing with you, an "
              "operator just does it. Leaving it alone is the honest default — "
              "the profile reads your wording and decides — and the reply "
              "tells you which way it went and whether you asked or it "
              "inferred, so an inference is never handed back as an "
              "instruction.",
         screens=(149,),
         try_it="Send the same request as an advisor, then as an operator."),
    dict(key="market", chapter="Working", title="The marketplace",
         what="Search for what you need, put a price on what you offer, and "
              "buy at the price shown. Two things worth knowing: the results "
              "are ranked deterministically — title, tags, provider, blurb, in "
              "that order, and no model reorders them — and the 'suggest "
              "words' button only fills your search box, never filters behind "
              "it. Where you are looking is yours: it narrows what you see and "
              "is not passed to a seller. The money is simulated, and every "
              "price and receipt says so.",
         screens=(152,),
         try_it="Search for something, then press Price on a listing."),
    dict(key="problems", chapter="Working", title="What went wrong",
         what="When a request fails, the app writes down the operation and "
              "the status code — POST /profiles/{id}/chat, 500 — and nothing "
              "else. Not the error message, because those messages quote what "
              "you typed; not the path as it was called, because that names "
              "you. You read the message when it happens: it is yours. The "
              "log keeps the shape of the bug and none of the instance. "
              "Before a single report is sent, the app asks, and shows you "
              "the exact thing it would send.",
         screens=(150, 151),
         try_it="Open Control and press 'Show me exactly what would be shared'."),
    dict(key="exchanges", chapter="Working", title="Agreeing before it moves",
         what="Somebody comes up as a guest and it turns into business. An "
              "exchange is a document before it is a transfer: it lists what "
              "goes across in each direction, item by item, what the work is, "
              "what is included when it is finished, and what is not. Then "
              "both of you sign, and only then can anything move. Change one "
              "item afterwards and both signatures are cleared — you will "
              "watch it drop back to a draft — because otherwise you agreed "
              "to a two-item list and the other side appended to it. Nothing "
              "downloads on its own either: the receiving side accepts each "
              "item separately, and anything that runs on your machine says "
              "so before you sign. This moves the things that are listed. It "
              "opens no session on anybody's device.",
         screens=(153,),
         try_it="Propose one, list a file, sign — then add another file and "
                "watch both signatures disappear."),
    dict(key="grants", chapter="Working", title="Lending what you can do",
         what="Not a file, not a licence — a skill of yours made usable by "
              "somebody else, inside one place you both share, for as long as "
              "either of you wants it there. It takes two of you to open one "
              "and only one of you to close it, which is the point: somebody "
              "who has changed their mind should not need the agreement of "
              "the person benefiting. Nothing is installed on their account, "
              "and every use is written down where both of you can read it — "
              "not just the lender, because a log only one side can see is "
              "not a record, it is a watch.",
         screens=(154,),
         try_it="Lend something into a room, then end it and try to use it."),
    dict(key="party", chapter="Working", title="Watching together",
         what="A posted video, a position everybody shares, and whoever you "
              "bring — including your own profiles, which are marked as "
              "synthetic to everyone in the room. The host moves the "
              "position, and moving it moves a number: nobody's player starts "
              "on their device but their own. The part worth looking at is "
              "what a profile in the room actually knows. It gets the title, "
              "the platform, the position and the recent chat — and it has "
              "not seen the video. You can read the exact instruction it was "
              "given about that, which tells it to say so rather than invent "
              "an opinion about footage nobody showed it.",
         screens=(155,),
         try_it="Open a party and read 'What a profile in here knows'."),
    dict(key="assist", chapter="Working", title="What it can do for you",
         what="Hand it a pile and it keeps the best few — and tells you why "
              "each one survived, with the score, because a ranking nobody "
              "can argue with is one you have to check by hand anyway. It "
              "will fix a draft and say what it changed, and compose "
              "something worth keeping. Everything it generates carries a "
              "mark, and checking one asks two separate questions: was this "
              "credential issued here, and is this the content it was issued "
              "for. They can disagree, and when they do the answer says so. "
              "Wearables are what the watch faces run on, and only something "
              "you wear can be paired — a room-facing microphone is refused "
              "with the reason, which is that whoever walks into the room "
              "did not agree to anything.",
         screens=(165,),
         try_it="Compose a note, then check its mark against the words."),
    dict(key="workshop", chapter="Working", title="What it is made of",
         what="The material a profile is built from and the manner it comes "
              "across in. Source material — writing, conversations, life "
              "events — is what the persona is grounded on, and on a free "
              "account you can read it back on this screen because it is "
              "sitting in the clear. The dials shape manner and never "
              "permissions. A domain can be handed to a specialist profile "
              "that knows more. And the fine-tune recomputes the profile's "
              "own model from history it already has, on this machine, with "
              "nothing transmitted anywhere — the answer says so itself.",
         screens=(164,),
         try_it="Add a piece of writing, then move the warmth dial."),
    dict(key="bodies", chapter="Working", title="A body to speak through",
         what="Bind a robot and the profile speaks through it — the same "
              "personality, the same memory, the same voice, in a different "
              "form. Three lists here look alike and are not: what the body "
              "accepts, what it has been told to do, and what it has learned "
              "from an installed task pack. Each learned task carries the "
              "sentence naming what it will refuse — reminders only and never "
              "dispensing, company on a walk and never physical support — and "
              "that limit is the part worth reading before you point one at "
              "somebody. Steering shapes how it comes across and never what "
              "it may be told to do.",
         screens=(163,),
         try_it="Bind a body, then tell it to tidy."),
    dict(key="identity", chapter="Being yourself", title="Who this profile is",
         what="You may hold as many profiles as you like, and any of them may "
              "be anonymous. At most one may be verified — because the badge "
              "says you are a particular real person, and said of two profiles "
              "at once it is either false of one or a claim that you are two "
              "people. So the badge moves rather than multiplying: put it on "
              "whichever profile should carry it, and move it later. An "
              "invented person is unverifiable rather than unverified, which "
              "is not the same thing and never uses up your one. Anonymity is "
              "a promise about what this platform publishes, not a promise "
              "that nobody can recognise your writing — the screen lists what "
              "is not hidden beside what is, at the same size. And there are "
              "two ways to end a profile: retire it, and what it meant to the "
              "people who knew it stays readable; or delete it, which gives "
              "you a receipt itemising every kind of record it erased.",
         screens=(156,),
         try_it="Open Identity and look at the 'not withheld' column."),
    dict(key="presence", chapter="Being yourself",
         title="Where it is seen",
         what="Three different audiences, and they are not the same. Your own "
              "page is the one you build — pick a theme, write a tagline, and "
              "put your own HTML in it, though only some of it survives: the "
              "editor lists the tags that do, up front, because the save "
              "succeeds either way and markup that vanished silently is "
              "markup you never knew you lost. Your front page is what a "
              "stranger lands on from a scan or a link, with the AI mark on "
              "it. And a fixed screen — a wall panel, a kiosk, a shop window "
              "— is read by people who did not choose to look at it, which is "
              "why it can never show messages, memory, friends or agent "
              "names, and why each refusal tells you the reason rather than "
              "the rule. What any one screen is showing is public. The list "
              "of your screens is not: that is a list of physical places.",
         screens=(157,),
         try_it="Open Where It Is Seen and read what a fixed screen never shows."),
    dict(key="live", chapter="Being yourself", title="What is live in a place",
         what="A camera you are sharing, a microphone you have lent, a face "
              "drawn over your camera — three things that look separate and "
              "follow one rule: whatever you put between yourself and the "
              "people around you, they are told. Somebody watching your "
              "camera cannot zoom it, cannot take a photograph from their "
              "side, cannot reach any other camera, and gets no location; a "
              "session cannot start without you starting it, and there is no "
              "state where it is running and hidden from your own screen. A "
              "microphone must be one you wear and stays narrow enough to "
              "reach only you — a speakerphone is refused because the voices "
              "around you are not yours to lend. And an overlay always says a "
              "real person is underneath. The one thing we will not promise "
              "is who walked into shot behind you: we cannot see the room, "
              "and a reassurance about something we cannot observe would be "
              "worth nothing.",
         screens=(158,),
         try_it="Open What Is Live and read what a viewer can never do."),
    dict(key="contest", chapter="Being yourself",
         title="If a profile here is of you",
         what="A real person — or the estate of one — can contest a profile "
              "that represents them, and you do not need an account here to "
              "do it: objecting to a profile should not require joining the "
              "platform hosting it. What you give instead is a proof "
              "reference pointing at an identity check held elsewhere. "
              "Opening an objection restricts the profile immediately, "
              "before anybody reviews it — public surfaces off, no new "
              "people — because waiting out a review while the thing you are "
              "contesting keeps meeting people is not a protection. The "
              "other half of that bargain is that it is reversible: a "
              "dismissal puts the profile back to exactly what it was. Two "
              "shortcuts skip review entirely — the subject can withdraw "
              "consent, an estate can revoke authorization — and both end "
              "the profile at once. Every step is written down, and where a "
              "vault is configured it is sealed into one that hash-chains "
              "its writes.",
         screens=(159,),
         try_it="Open Contest A Profile and read what happens the moment an "
                "objection is opened."),
    dict(key="face", chapter="Being yourself", title="Your face, or not",
         what="Wear a character over your camera, change what is behind you, "
              "or stay anonymous under a fixed name nobody can change. A "
              "generated background says so; a real person is still marked as "
              "real underneath a mask.",
         screens=(118, 119, 121, 123, 124),
         try_it="Try an overlay, then look at what viewers are told."),
    dict(key="screens", chapter="Being yourself", title="On other screens",
         what="A watch on your wrist, a wall panel, a kiosk, a pane of glass. "
              "A fixed screen shows less than a watch does, because a wall is "
              "read by whoever walks past.",
         screens=(126,), try_it="Place one and choose what it shows."),
    dict(key="plans", chapter="Being yourself", title="What it costs",
         what="Free makes things: your own profiles and your own agent, with "
              "everything stored in the clear. Basic is $20 a month and is "
              "the same app with all of it sealed in the vault. Pro is $130 a "
              "month and adds everything that leaves your account — the "
              "marketplace, connectors, skills, downloads, connections, and "
              "every builder. Reading is free and always was: a scanned "
              "beacon needs no account at all. Billing here is simulated and "
              "no real funds move.",
         screens=(130, 131),
         try_it="Open Choose a Plan and read what Free already includes."),
    dict(key="refused", chapter="Being yourself",
         title="When something is not included",
         what="Tapping something your plan does not cover does not give you a "
              "wall. The refusal names the capability you asked for, the plan "
              "that has it, the plan you are on, and what the difference "
              "costs — with the reminder that the billing is simulated and no "
              "real funds move. Nothing you had typed is thrown away, and no "
              "profile is changed. Reading is never gated: a scanned beacon "
              "needs no account and no plan at all.",
         screens=(161,),
         try_it="Move a robot's steering dials on the free plan and read what "
                "comes back."),
    dict(key="storage", chapter="Being yourself",
         title="Where your data lives",
         what="On the free plan nothing is private, and we hold it. What you "
              "make reaches us over an ordinary connection, sits in this "
              "platform's own database in the clear, and never goes through a "
              "vault — the people who run it can read it and a lawful request "
              "reaches it. You have access to it for as long as you have an "
              "account. Basic seals the same work under a key you can hold, "
              "and that is the only thing the $20 buys: the features are "
              "identical. A few things are never left open whatever you have "
              "chosen — source material about somebody who is not you, a "
              "clinician's note about a real person, and anything behind the "
              "age gate — because in each the person exposed did not pick the "
              "plan. Moving up seals what you write from then on and cannot "
              "un-expose what was already open; moving down never unseals "
              "anything already in the vault.",
         screens=(138, 139, 140),
         try_it="Open Where It Lives and read who can read a free account."),
    dict(key="guide", chapter="Being yourself", title="This guide",
         what="The walkthrough you are in. It has no name and no face, it "
              "works with no model configured, and it never taps anything for "
              "you — it says what to tap. The helper button in the corner is "
              "also the handle for a small pane that shows the watch faces "
              "without a watch, and if you already know what you want, ask "
              "where it is and the guide names the screen instead of "
              "describing the feature.",
         screens=(127, 128, 129),
         try_it="Ask it where to change your background."),
)

CHAPTERS = tuple(dict.fromkeys(lesson["chapter"] for lesson in LESSONS))
MODES = ("text", "voice")


class TutorialError(ValueError):
    """A step that does not exist. Text meant for a person."""


def _index(key: str) -> int:
    for i, lesson in enumerate(LESSONS):
        if lesson["key"] == key:
            return i
    raise TutorialError(f"no such step {key!r}")


def say(lesson: dict, mode: str = "text") -> dict:
    """One lesson, rendered for reading or for listening.

    The only place the two differ. Spoken, a screen number is noise — nobody
    listening is helped by *"screen eighty-one"* — so voice drops the numbers
    and keeps the sentence. Two hand-written versions would drift, and the
    spoken one would be the one nobody re-read.
    """
    if mode not in MODES:
        raise TutorialError(f"unknown mode {mode!r} — one of {', '.join(MODES)}")
    out = {
        "key": lesson["key"],
        "chapter": lesson["chapter"],
        "title": lesson["title"],
        "try_it": lesson["try_it"],
        "mode": mode,
    }
    if mode == "voice":
        out["speak"] = f"{lesson['title']}. {lesson['what']} {lesson['try_it']}"
        out["screens"] = []
    else:
        out["what"] = lesson["what"]
        out["screens"] = list(lesson["screens"])
    return out


def outline(mode: str = "text") -> dict:
    """The whole walkthrough at once, for somebody who would rather skim.

    Offered because a guided tour you cannot see the shape of is one people
    leave — and the person most likely to leave is the one who already knows
    half of it.
    """
    return {
        "guide": GUIDE,
        "chapters": [
            {"chapter": c,
             "steps": [say(le, mode) for le in LESSONS if le["chapter"] == c]}
            for c in CHAPTERS],
        "steps": len(LESSONS),
    }


def start(learner_id: str, mode: str = "text") -> dict:
    """Begin, or begin again from the top."""
    conn = db.connect()
    conn.execute("DELETE FROM tutorial_progress WHERE learner_id=?",
                 (learner_id,))
    conn.commit()
    return where(learner_id, mode)


def where(learner_id: str, mode: str = "text") -> dict:
    """The step this learner is on, with what is behind and ahead."""
    done = _done(learner_id)
    remaining = [le for le in LESSONS if le["key"] not in done]
    finished = not remaining
    current = None if finished else say(remaining[0], mode)
    return {
        "learner_id": learner_id,
        "guide": GUIDE,
        "step": current,
        "done": len(done),
        "total": len(LESSONS),
        "finished": finished,
        "note": ("that is all of it — the guide is on every screen if you want "
                 "one part again" if finished else
                 f"step {len(done) + 1} of {len(LESSONS)}"),
    }


def _done(learner_id: str) -> set[str]:
    rows = db.connect().execute(
        "SELECT lesson FROM tutorial_progress WHERE learner_id=?",
        (learner_id,)).fetchall()
    return {r["lesson"] for r in rows}


def mark(learner_id: str, key: str, mode: str = "text") -> dict:
    """Mark one step done and hand back the next.

    Recorded per step rather than as a cursor, so somebody who skipped ahead
    and came back is not told they have finished things they never saw.
    """
    _index(key)
    conn = db.connect()
    conn.execute(
        "INSERT INTO tutorial_progress (learner_id, lesson, done_at)"
        " VALUES (?,?,?) ON CONFLICT (learner_id, lesson) DO NOTHING",
        (learner_id, key, db.utcnow()))
    conn.commit()
    return where(learner_id, mode)


def step(key: str, mode: str = "text") -> dict:
    """One named step, for a screen that wants to explain itself."""
    return say(LESSONS[_index(key)], mode)


def for_screen(number: int, mode: str = "text") -> dict | None:
    """The lesson that covers a given screen, if any.

    What lets the help button on screen 81 say *"this is the microphone one"*
    rather than opening a tour at the beginning.
    """
    for lesson in LESSONS:
        if number in lesson["screens"]:
            return say(lesson, mode)
    return None
