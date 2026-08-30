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

from . import db, i18n

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
              "would rather be asked than write. A character card you "
              "already have — chara_card_v2 or v3, as JSON or a PNG with "
              "the card inside — imports as a new fictional profile: its "
              "greeting, example dialogue and creator notes are carried in "
              "as source material, and its hidden harness instructions are "
              "withheld by name, each with the reason said out loud.",
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
              "meets you there instead of nowhere. The memory answers to "
              "you: ask for an account of what it holds — counted from the "
              "record, never guessed — and have it forget one named thing "
              "without erasing the friendship. And when a conversation is "
              "coming that you dread, open a rehearsal room and practice "
              "it: the profile plays the counterpart, nothing said inside "
              "enters its memory, and closing the room erases the "
              "transcript.",
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
    dict(key="curation", chapter="You are in control",
         title="The checkboxes and the pen",
         what="A transcript is a record of a relationship, and the person in "
              "it may curate it. Edit mode puts a clear box beside every "
              "turn: tick what should never have been said and delete it — "
              "scoped to the two of you, so a borrowed id strikes nothing — "
              "or tap one turn and rewrite it in place. New words face "
              "moderation exactly like spoken ones. A rewritten profile turn "
              "drops its synthetic-media credential, because a content-hash "
              "credential must not vouch for words it never saw. And the "
              "record keeps the fact of the edit, never the old words: "
              "deleting is forgetting, not archiving.",
         screens=(7,),
         try_it="Open a conversation's memory, press Edit, and rewrite one "
                "turn."),
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
    dict(key="remainder", chapter="Out in the world",
         title="Everything else",
         what="The tail of the audit, on one screen, because that is honestly "
              "what it is: six small features that each had a couple of "
              "routes and no way in. Feedback on the app — your own words "
              "come back to you and to nobody else, and all anyone else ever "
              "sees is the count. Where mods come from, and syncing one in. "
              "Apps this profile is connected to. Going out to look "
              "something up, where the answer tells you how much was "
              "stripped from the question first and whether it left this "
              "machine at all — that is the part worth reading, not the "
              "findings. Every steering dial in one place. Playing alongside "
              "somebody in a game. And publishing to a platform we do not "
              "run, which is the one place a profile's words genuinely "
              "leave. That route stored its post with **no mark on it** "
              "while the same profile posting in-app was stamped every time, "
              "and it used the profile's own filter where posting in-app "
              "always uses the strictest one. Both now match: strict on the "
              "way out, and a credential that travels with it. There is also "
              "a lookup box — nine kinds of record had a call written for "
              "them and no screen calling it, and they were all the same "
              "question about different ids, so they are one control.",
         screens=(183,),
         try_it="Send a piece of feedback, then look up your own profile id "
                "in the box at the bottom."),
    # "Out in the world" rather than "You are in control": the chapters are
    # named for the reader, and this is the one lesson about a surface that is
    # not for them. It belongs beside beacons and desks — the places a profile
    # meets somebody who never signed up for anything.
    dict(key="withoutanaccount", chapter="Out in the world",
         title="Without an account",
         what="The one surface here that is not for you. Three of QRME's "
              "routes are public deliberately, and the backend says so in its "
              "own words — objecting to a profile *\"need not own an "
              "account\"*, and the identity signature is readable by "
              "*\"anyone meeting the profile through any form\"*. Every "
              "client called them from behind the sign-in screen, so the "
              "person each was written for could not reach it: somebody who "
              "has found a synthetic profile of themselves, and somebody sent "
              "a message who wants to know whether a person wrote it. Neither "
              "has an account, and asking them to make one with the platform "
              "they are asking about is the wrong answer. The link is on the "
              "sign-in page now, on every client, and `#object` in the URL "
              "opens the form directly — so a takedown notice can point at "
              "it. Nothing on it sends a credential. The half that quotes an "
              "objector's reason stays where the credential is.",
         screens=(184,),
         try_it="Sign out and open the link under the sign-in form. Every "
                "control on that page works with no profile at all."),
    dict(key="access", chapter="Out in the world",
         title="Ability is not a gate",
         what="The accessibility statement, and the door it promises. If how "
              "your body or mind works stands between you and this product, "
              "that is a defect in the product — not in you. The statement "
              "lists who is expected here (blind, deaf, mute, motor, "
              "cognitive, dyslexic, motion-sensitive people — and every need "
              "the list forgot), and every sentence on it is checked against "
              "behavior by the suite. The report asks three questions and no "
              "diagnosis: what were you trying to do, what stood in the way, "
              "what would help. No account — `#access` in the URL opens it "
              "before sign-in — no name, and your words stay on this "
              "deployment, read with the reviewer token and turned into "
              "rows in a backlog that only shrinks.",
         screens=(193,),
         try_it="Sign out, open the Accessibility link under the sign-in "
                "form, and read the statement in your own language."),
    dict(key="inwords", chapter="Out in the world",
         title="In its own words",
         what="Four things about how a profile presents itself in language. "
              "Which one it speaks — and that is not a display setting: the "
              "persona *writes* in that language on every surface it appears, "
              "chat, posts, rooms, a robot speaking aloud, rather than "
              "writing English and translating afterwards. A translator for "
              "anything you ran across, using this profile's own model, which "
              "says plainly when it cannot rather than handing your text back "
              "as though it had done the work. Composing a post, which always "
              "runs the strict filter because a public post faces the widest "
              "audience there is. And the **@handle** — the name it answers "
              "to. Claiming one replaces whatever the profile had, because "
              "that is how changing it works, and that route asked for no "
              "credential at all: anybody could take `@rosa` away from Rosa, "
              "leaving the name she had printed and shared resolving to "
              "nothing and the new one, chosen by a stranger, pointing at "
              "her. The three routes underneath it were given that check "
              "already; this one had been walked past.",
         screens=(182,),
         try_it="Set the language to one you read, then compose a post and "
                "see which language it comes back in."),
    dict(key="themark", chapter="Out in the world",
         title="The mark, and the held",
         what="Three things about the same question — *is it clear what this "
              "is, and who says otherwise*. You design the mark your "
              "profile's work carries: pick the glyph and what to call it, "
              "and whatever you type, the line comes back with **AI ·** in "
              "front of it. The designation is not a field you can empty. "
              "Next to it is what the profile has published, and separately "
              "what is being held: a post the strict filter stopped, or one "
              "waiting because you set this profile to approve its own posts "
              "by hand. A held post is a queue and not a publication, and "
              "only you see it — the route that lists what a profile "
              "published used to hand those out in full to anybody who "
              "asked, text and the reason they were held, with no credential "
              "at all. And last, anybody objecting that this profile should "
              "not exist. Opening one restricts the profile immediately. You "
              "can re-attest the basis you claim the right on and that is "
              "all you can do — resolving it belongs to a reviewer, because "
              "an owner who could dismiss an objection against their own "
              "profile would be deciding their own case.",
         screens=(181,),
         try_it="Set a label without the word AI in it, and read the line "
                "that comes back."),
    dict(key="stranger", chapter="Out in the world",
         title="Two strangers",
         what="Two things you do before you have anything of your own here. "
              "Following a reference — an `@handle`, a `#tag`, or the id off "
              "a printed sticker — needs no account, because the person "
              "following one does not have one yet. And talking to a "
              "stranger: no profile involved at all, two people, each seeing "
              "only the name the other chose. The second of those had no way "
              "in from this console and, it turned out, **no lock on the door "
              "either**. Every one of its routes read the person's id out of "
              "the request and checked only that the id named somebody in the "
              "conversation — never that the caller *was* them, and never "
              "asking for a credential at all. Two public ids let anybody "
              "join the queue as you, be matched with a stranger under your "
              "name, speak as you, read your whole conversation including the "
              "messages held back for your eyes only, and end it. Ending was "
              "worse still: the check was skipped entirely when no id was "
              "given, so a bare request with nothing in it closed somebody "
              "else's conversation and handed back any microphone lent inside "
              "it. An id is a claim. Your token is the answer, and the same "
              "rule already guarded rooms. Matching had a listening problem "
              "too: a match is made by whichever side arrives second, and the "
              "first had no way to hear about it — re-joining only re-queued "
              "them under a fresh name. The waiting side now has its own "
              "read, and every client polls it while it waits: the answer is "
              "matched, waiting, or idle, and never a new place in line.",
         screens=(180,),
         try_it="Follow an @handle, then join the friendly queue and see what "
                "the other person is called."),
    dict(key="visiting", chapter="Out in the world",
         title="Ringing the bell",
         what="`Desk` is the side you run a desk from — open one, say whether "
              "you are there, point the camera, answer the bell, bring "
              "somebody up. Every route it uses is yours alone. There was no "
              "*visitor's* side at all, and the visitor is who the whole "
              "thing is for: somebody standing in front of an empty chair "
              "with a sign on it saying to ring. Now you can look at the "
              "card, ring, watch the stream, and put a hand up to come on it. "
              "The card and the bell ask for nothing, because the person at "
              "an empty chair is exactly the one who has no account yet — an "
              "18+ stream is the one exception. Coming up **on** the stream "
              "is the host's call, so that asks rather than does, and it "
              "needs an account: they are deciding about a person. That "
              "refusal used to mint the stream's room first and check who was "
              "asking afterwards, so a request we turned away left a room "
              "behind it. Nothing is written now until you are somebody. The "
              "same screen leaves this profile somewhere — a printed code on "
              "a bench or at a meeting — and only its owner may place one, "
              "see the list, or pick one back up: where a profile is left is "
              "a decision about the profile, and the list is a record of "
              "places a person goes.",
         screens=(179,),
         try_it="Look at a desk by its id, ring the bell, then place a code "
                "of your own and scan it."),
    dict(key="signing", chapter="Out in the world",
         title="Signed, and checked",
         what="Signing had seven routes and no way in from here. You could "
              "see the credentials on your account and could not enrol one, "
              "revoke one, read the rules a counterparty is asked to accept, "
              "put a signature on anything, or check a package somebody "
              "handed you — while the screen next door said *none enrolled, "
              "the ceremony can enrol one* under a heading with no button. "
              "The ceremony window already existed and already worked; "
              "nothing here was listening for what it sent back. A signature "
              "is a device credential used with your face or fingerprint "
              "over one exact document: the challenge **is** the hash of "
              "those bytes, so editing the text afterwards leaves the old "
              "signature covering the old text and nothing else. The window "
              "opens on the API's own address rather than inside the app, "
              "because the credential refuses to work anywhere else — and it "
              "carries no token, because a token in a web address ends up in "
              "logs. Checking somebody else's package asks nothing of us at "
              "all: it carries its own key and its own hashes. And it now "
              "answers honestly when it cannot finish. A package with a "
              "field missing used to come back saying *the signature is "
              "invalid* — the most serious thing it can say, about "
              "cryptography that had verified perfectly well. A check that "
              "did not run is shown as one that did not run.",
         screens=(178,),
         try_it="Enrol a credential, sign a line of text, then paste the "
                "package into the checker and read the eight checks."),
    dict(key="handing", chapter="Out in the world",
         title="Work handed over",
         what="Delegation had an owner's half and no other half. You could "
              "mint a grant, choose which phases may run unattended and "
              "publish the policy — and nobody could take it up from here, "
              "because the four calls for the person on the *other* end of "
              "the conversation had no screen. That is what this adds: "
              "somebody already talking to a profile hands it a job rather "
              "than one more chat turn, and watches it run. Nothing behind "
              "it was wrong, which is worth saying plainly. The offer is "
              "public and tells you which phases are allowed and nothing "
              "else — which source items the owner scoped is the owner's "
              "business, not yours. Delegating `research` is refused unless "
              "a grant scopes it, because without one the phase reads every "
              "source item on the profile. You have to be in conversation "
              "with it first: delegated work is not for a stranger holding "
              "a profile id. And once it is running, the two people who may "
              "read it are you and the owner — for different reasons, and "
              "nobody else at all.",
         screens=(177,),
         try_it="Chat to a profile that accepts delegated work, then hand it "
                "a goal and advance it a phase at a time."),
    dict(key="inside", chapter="Out in the world",
         title="Inside a room",
         what="Rooms could be opened and not entered: the console listed "
              "what was live and had no way to read a word of it, say "
              "anything, let the profiles take a turn, or lend them a "
              "microphone. Building the way in found two things worth more "
              "than the screen. The speaker was read from the request body, "
              "and checked only against the list of participants — not "
              "against who was asking — so anybody holding a room id could "
              "put words in a named person's mouth and have every profile "
              "answer as though she had said them. And the transcript asked "
              "for no credential at all, so the whole conversation was "
              "readable by anyone who knew the id. A room id is not a "
              "secret; it rides in beacons and on printed stickers, which is "
              "the point of them — and that sentence was already written "
              "down two routes away, guarding the smaller fact of who lent a "
              "microphone. Everything a profile says in a room is "
              "watermarked as it is said, and a room with anyone under 18 in "
              "it runs strict for everybody.",
         screens=(175,),
         try_it="Open a room from Rooms, then take its id next door and go "
                "in."),
    dict(key="selling", chapter="Out in the world",
         title="What you are owed",
         what="The other side of the counter. Everything about licensing "
              "until now was the buyer's half — acquire one, derive an "
              "agent from it — and the seller's half had no screen at all "
              "here: you could be bought from without being able to post "
              "the offer, see who held a licence, revoke one, read what any "
              "of it earned, or ask to be paid. All nine of those work on "
              "the phone, which is why the route audit called them doored. "
              "The statement keeps totals per currency and never adds "
              "across them: a hundred yen and a hundred dollars used to "
              "come back as two hundred, labelled with whichever sale was "
              "newest. A payout settles one currency, and says what is "
              "left. Revoking a licence stops the buyer deriving from it — "
              "it does not unmake an agent they already derived, and it "
              "does not take the fee off your statement, because a sale "
              "that happened stays on the record. A listing can now "
              "only be taken down — or moved — by somebody with a stake "
              "in it. And putting a price on one credits your "
              "**account**, not the profile you happen to be signed in as: "
              "before this screen existed the sale went through, the "
              "receipt said it was on your statement, and the statement "
              "was empty.",
         screens=(174,),
         try_it="Post a consult offer, then look at what the statement says "
                "before anybody has bought one."),
    dict(key="passing", chapter="Out in the world",
         title="Beginning, and passing on",
         what="A profile is born from four questions, and if you leave the "
              "name blank it chooses its own from the answers. At the other "
              "end is the one route in this product an owner token cannot "
              "open: succession answers a signal that the owner has died or "
              "cannot act, so requiring their authorisation would require "
              "the one thing known to be unavailable. A reviewer holds it "
              "instead, against a verification reference kept out of band. "
              "With somebody named, control passes and a fresh owner token "
              "is minted; with nobody, the profile sunsets to memorial — "
              "frozen rather than orphaned. A contested identity cannot be "
              "handed on at all. In between: what a profile can be taught, "
              "published under your own token so the money follows it, and "
              "the single press from a wrist that goes down the same paths "
              "the full apps use.",
         screens=(173,),
         try_it="Create one with the name left blank, and see what it calls "
                "itself."),
    dict(key="named", chapter="Out in the world",
         title="One thing, named",
         what="Six reads that each answer about one particular thing, and "
              "six different answers to who is allowed to ask. The light "
              "legend takes no id at all. A campaign is readable by "
              "anybody — the most public read in the product, and that is "
              "what makes it honest, because it carries who the money goes "
              "to and the person about to give some is the one entitled to "
              "see it. For the same reason a campaign cannot exist before "
              "the designation does. An excursion is the owner's alone, "
              "since it holds the brief that was sanitised before it went "
              "and the count of what was taken out. And a place's lent "
              "skills are filtered to your own, with a note saying so: a "
              "short list there means your grants, not no grants.",
         screens=(172,),
         try_it="Read a campaign with no token at all, and find who the "
                "money goes to written on the same card."),
    dict(key="lastdoor", chapter="Out in the world",
         title="When it cannot resolve it, and the door at the end",
         what="Some matters do not wait for a butcher or a broker, and the "
              "honest end of the ladder is emergency services. The profile "
              "says up front that it can reach them, rather than producing "
              "it from behind its back once things are already bad — a "
              "capability discovered mid-emergency is a capability nobody "
              "uses. Reaching them can cost money, so the waiver says so and "
              "is signed **ahead of time**, in calm conditions: nobody reads "
              "a liability paragraph during an emergency, and asking them to "
              "is how a person in trouble ends up reading instead of "
              "pressing. The press is explicit and nothing fires on the "
              "profile's own judgement. And through the beta the last hop "
              "**refuses**: the call is attempted and stopped at the point "
              "it would leave, and what comes back says plainly that no call "
              "was placed and gives the number to dial. That is a posture "
              "rather than a fault. The rule it keeps is the one the beacon "
              "alarms settled — an alarm that says help was called has to "
              "have called it — kept here by never making the claim.",
         screens=(172,),
         try_it="Press it. Read the refusal, then look at what was raised: "
                "the attempt is recorded and `placed` is still false."),
    dict(key="bringreal", chapter="Out in the world",
         title="Bringing somebody real into it",
         what="A synthetic profile is an AI, and some things need a person. "
              "Every profile can hand its matter to somebody real — a "
              "butcher, a broker, a physiotherapist, a doctor — and catch "
              "them up before they arrive, so nobody has to tell the story "
              "twice. The people are yours: attach the ones you already "
              "trust, per area of life, and a profile reaches for yours "
              "before it reaches for the search. Every row says which it "
              "is, because *yours* and *found for you* are different claims "
              "and somebody about to send their history is entitled to know "
              "which they are looking at. What travels is decided by a "
              "revocable grant and by nothing else: one function reads that "
              "grant and both the autonomous tasks and the briefing go "
              "through it, so revoking it stops both. The briefing counts "
              "its attachments out loud rather than saying *your history* — "
              "a phrase somebody agrees to without knowing what it covers — "
              "and the profile is named as synthetic inside the document, "
              "because a document travels away from the screen that framed "
              "it. Nothing is sent by the preview: it exists so declining "
              "is still free.",
         screens=(172,),
         try_it="Preview a briefing, then revoke the grant and try again — "
                "the second attempt is refused rather than quietly thinner."),
    dict(key="goingback", chapter="Out in the world",
         title="The far end that sees you twice",
         what="Offline mode answers whether anything left this machine. It "
              "never answered who kept watching. One sanitised question "
              "tells a far host nothing; the same one every week, from the "
              "same address, tells it a rhythm and a set of interests — a "
              "subject, with no name on it, whose fifteenth visit is read "
              "against the previous fourteen. So every outbound connection "
              "is now witnessed at the one function every socket in the "
              "product already passes through, and the far hosts an agent "
              "keeps returning to are a list the owner can read. The host "
              "is kept and the address after it never is: in a profile "
              "fetch that tail is the subject's own handle, and a ledger "
              "holding it would be a second copy of the private thing in a "
              "table nobody audits. The lever is real rather than a "
              "picture — standing a host down refuses at the socket, so it "
              "binds the chat links, the briefcase and any path added "
              "later, not merely the screen that listed it. And the "
              "deployment-wide totals, which are what correlation exposure "
              "actually looks like, carry no profile at any depth: a tool "
              "for measuring correlation must not become a way to "
              "correlate people.",
         screens=(172,),
         try_it="Stand a host down, then try to fetch it from a different "
                "door — the chat box, by pasting a link — and watch the "
                "refusal arrive there too."),
    dict(key="maydo", chapter="Out in the world",
         title="What the agent may do",
         what="The product grew powers faster than it grew a place to see "
              "them: studying the open web, asking strangers, briefing a "
              "real professional, running a job over granted material, "
              "reaching emergency services. The only way to find out what "
              "one could do was to meet a power mid-conversation. The "
              "roster is that list, and it says three things about each "
              "row — what the agent would be allowed to do, in the words "
              "you would use for it afterwards; **what it keeps**, which "
              "is the half these lists usually omit, because summarising "
              "a meeting and summarising a meeting *and keeping the "
              "recording* are different agreements; and whether it reaches "
              "somebody who never chose it. That last one is a field "
              "rather than a paragraph so it can be checked: nothing that "
              "reaches other people is ever on by default, and a guard "
              "refuses any row that tries to be. Visitors read the same "
              "list, because what an agent may do on somebody\'s behalf is "
              "not a secret kept from the person it would be done to.",
         screens=(202,),
         try_it="Turn one off that had been used, then use it again and "
                "read the refusal — it names the thing rather than the "
                "row, and it arrives in your own language."),
    dict(key="matters", chapter="Out in the world",
         title="Getting your matter looked at",
         what="Something wrong with the app, with your profiles, or with "
              "the platform. Say it here and it becomes a **matter**: a "
              "record with your own words in it, what was done about it, "
              "and how it ended — not a question that scrolls away. The "
              "help box answers first, because most of what arrives at a "
              "support door has a written answer and one that costs "
              "nothing and arrives now beats a queue. What it says is "
              "offered, never filed: a matter with an answer waiting on it "
              "reads *here is something, is that it*, with **That was it** "
              "and **That was not it** side by side, and only a person "
              "ever moves it to settled. That line exists because a help "
              "box matches loosely on purpose — an approximately right "
              "paragraph costs a reader nothing, and the same guess "
              "disposing of a billing complaint costs them the complaint. "
              "You do not need an account: the person locked out of the "
              "account they are complaining about is the one who most "
              "needs this door, so a matter raised without signing in "
              "comes back with a claim, shown once, which is the only "
              "thing that opens it again.",
         screens=(203,),
         try_it="Raise one without signing in, keep the claim, then press "
                "**That was not it** — the matter goes back to waiting and "
                "the record keeps the fact that it was answered wrongly "
                "once, which is a different thing from never answered."),
    dict(key="asking", chapter="Out in the world",
         title="Asking people, not pages",
         what="An excursion asks a model, which can only return what "
              "somebody already wrote down. An inquiry asks people. The "
              "question goes onto an open board that anybody can answer "
              "with no account and no name, and an accepted answer folds "
              "into the profile as a knowledge source — so the offline "
              "model ends up knowing something that was never published, "
              "and the person who knew it never learns whose question it "
              "was. Three things are hardcoded rather than configured: the "
              "question is sanitised on the way out and there is no "
              "argument that skips it; the board carries the sanitised "
              "line and nothing else, not the profile, not the typed "
              "question, not even the count of what was taken out, because "
              "two questions with the same unusual count are a thread to "
              "pull; and an answer is a stranger\'s text, moderated on "
              "arrival and never folded in without the owner saying so. "
              "Being pointed in a direction is not the same as being "
              "steered, and the difference is a person choosing.",
         screens=(172,),
         try_it="Put a question out, then read the board with no token at "
                "all and check that nothing on it says whose it is."),
    dict(key="leaving", chapter="Out in the world",
         title="What leaves, and on what terms",
         what="Two different kinds of leaving, and conflating them is how "
              "somebody agrees to the wrong one. A contribution sends one "
              "anonymised exchange to the shared model — no ids, the "
              "persona name replaced, and a random ref so the item can be "
              "deleted at the gateway later without identifying anybody. A "
              "licence sends the profile itself: the right to consult it, "
              "or where the offer allows, to derive a new agent seeded from "
              "its persona and owned by the buyer. The contribution preview "
              "is a dry run — it says what would leave, not what is about "
              "to, and it is computed whether or not you are opted in. And "
              "a licence that permits deriving is refused to a buyer under "
              "18 at the till rather than at delivery, because the fee "
              "moves when the licence is sold.",
         screens=(171,),
         try_it="Read the preview while opted out, then notice the heading "
                "changes rather than the content."),
    dict(key="reaching", chapter="Out in the world",
         title="Reaching out, and what stops it",
         what="A profile may message somebody first only if its owner "
              "switched that on — and even then four separate refusals "
              "stand in the way, in four different sentences, because they "
              "are four different facts. It is reactive-only. It already "
              "reached out and heard nothing, and will not send twice into "
              "silence. It reached out recently and the rate cap holds. Or "
              "the person's quiet hours are in effect — and that last one "
              "is not the owner's to lift. Quiet hours belong to the person "
              "they protect, and an owner sending them is refused, because "
              "a boundary your correspondent can move is not a boundary. "
              "Alongside them: the engagement record, readable by those two "
              "and nobody else, and the latent picture the profile actually "
              "behaves from, shown so it can be argued with.",
         screens=(170,),
         try_it="Reach out twice in a row and read the second refusal — it "
                "is a different sentence from the first."),
    dict(key="beacons", chapter="Out in the world",
         title="Connections to the world",
         what="Two kinds of QR code, and they look identical. A placed "
              "beacon brings a stranger *here* — the profile answers them "
              "on QRME. A platform beacon sends them *away*, to an account "
              "that already exists; only with no handle to build a link "
              "from does it fall back to a QRME page. Connecting a platform "
              "has a direction, and the two never share a row: collect "
              "pulls that account's content in, publish runs the profile "
              "out, so a read-only import can never also post. And asking "
              "for a code's picture is free, but opening the page it points "
              "to counts as a scan — there is no preview that does not, "
              "because the server cannot tell you from a stranger.",
         screens=(169,),
         try_it="Connect a platform to publish, show its code, and read "
                "where scanning it would actually send somebody."),
    dict(key="audience", chapter="Out in the world",
         title="Who follows, and what they pay",
         what="Following is free; paying is a separate tier and there is no "
              "middle one. Nothing renews on a timer — a period is charged "
              "when somebody presses the button, so a count of periods is a "
              "count of deliberate acts and a deployment left running "
              "charges nobody. Agreeing to a price means sending the same "
              "number back, so what you agreed to is what is charged. "
              "Gifting needs a verified birthdate, and the cap is published "
              "before you can hit it. Money here is simulated and every "
              "response says so.",
         screens=(168,),
         try_it="Follow a profile for free, then read what a paid period "
                "would actually charge."),
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
    dict(key="circle", chapter="People", title="Your circle",
         what="See all, across from Top friends on the homepage, opens the "
              "friends screen that is only friends: everyone you have added, "
              "with what each of them does — the face, the blurb, the tags — "
              "and no add button anywhere, because everybody here already "
              "said yes. The Friends tab stays the workbench for changing "
              "the list; this is the list itself. A face opens their page, "
              "and an empty circle offers Discover, which is the one place "
              "where offering is the point.",
         screens=(204,),
         try_it="Press See all, then press a face."),
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
              "the exact thing it would send. And the reports funnel home "
              "now: with no external collector stamped into the build, the "
              "console posts to this deployment's own backend, and the same "
              "card retrieves the aggregate — every client's failures folded "
              "into counters, no messages to leak — behind QRME_PROBLEMS_KEY, "
              "or freely from the backend's own machine.",
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
              "synthetic to everyone in the room. You can also just paste a "
              "video link: it faces the same platform allowlist a wall "
              "post's video does, and the party carries it itself, so "
              "nobody's wall grows a post they never wrote. A party is "
              "private until its host makes it public — then a card rides "
              "the feed and the open list, showing counts and the video, "
              "never who is inside, and anyone can join from it. The id "
              "stays the private door either way: share it, and somebody "
              "jumps straight into your room. The host moves the "
              "position, and moving it moves a number: nobody's player starts "
              "on their device but their own. The part worth looking at is "
              "what a profile in the room actually knows. It gets the title, "
              "the platform, the position and the recent chat — and it has "
              "not seen the video. You can read the exact instruction it was "
              "given about that, which tells it to say so rather than invent "
              "an opinion about footage nobody showed it. On the room's "
              "biggest screen — the vastscape a console or TV casts to — "
              "everyone watching is present as their own face, an avatar "
              "bubble resting in the picture, and the phone is only the "
              "remote.",
         screens=(155, 194, 195),
         try_it="Open a party and read 'What a profile in here knows'."),
    dict(key="lobby", chapter="Working", title="Who is in the game with you",
         what="A profile can sit in a lobby beside you as a companion, a "
              "coach or a spotter. Everything in that lobby observes and "
              "talks; nothing in it plays — no key, stick or click is ever "
              "sent to a game, nothing corrects anybody's aim, and no "
              "synthetic member takes a player slot. More hardware does not "
              "change it: a console of its own, a second controller on yours, "
              "a pad paired over Bluetooth and a capture card are all the "
              "same bot with different plumbing. The roster says which "
              "members are synthetic, because everyone in a match is owed "
              "that. And you can read the instruction a synthetic member is "
              "given, which tells it that some of the others are synthetic "
              "too — a lobby that reads as friends when it is one player and "
              "several generated voices is exactly what this prevents.",
         screens=(167,),
         try_it="Open a lobby and read what nothing in it will do."),
    dict(key="referral", chapter="Working",
         title="Handing it to somebody qualified",
         what="A profile is not a clinician, and the summary it assembles "
              "says so before anything else. If you have been talking to one "
              "about a symptom, you can hand that conversation to somebody "
              "who is qualified — once. Preparing it releases nothing: you "
              "read exactly what would go, and the signature you then give "
              "with your device is over those precise words, because the "
              "thing you sign is their hash. A summary changed afterwards "
              "cannot ride the old signature. The link the clinician gets "
              "opens once and says when it was used if anybody tries again, "
              "and they may write back one time — their words, attributed to "
              "them, never recited by the profile as its own.",
         screens=(166,),
         try_it="Search for an area of care and read the package it "
                "assembles before you sign anything."),
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
              "nothing transmitted anywhere — the answer says so itself. "
              "When the dials sit where you want them, lock the steering: "
              "while the lock is on nothing moves them — the hub, a bound "
              "robot, your own slip — and every attempt is refused with "
              "the reason you gave until you unlock it.",
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
              "it may be told to do."
              " Choosing one is shopping, so the catalogue covers the "
              "market rather than the shelf — humanoids, home robots, "
              "quadrupeds and vacuums from every maker shipping one, plus "
              "the ones announced and not yet buyable, each row saying "
              "which it is. An announced body is listed **and refused**: "
              "binding one answers 409 naming its status, because calling a "
              "machine its maker has publicly shown an \"unknown model\" "
              "would be false, and every command to a body nobody has would "
              "go nowhere. The list is a dated snapshot and a test fails "
              "when the date goes stale, because `announced` is a claim "
              "about the future and it ages. The connections bracket is the "
              "other half: a task pack teaches a body verbs, each checked "
              "against what that model can physically do — a vacuum is never "
              "taught to fetch — and a connector is a service its agents can "
              "collect from, act on, or produce into. A pack is fitted to a "
              "particular machine, not to the profile, which is the "
              "distinction that decides where it lands.",
         screens=(163, 176),
         try_it="Open the full list of bodies and find one you cannot buy "
                "yet."),
    dict(key="hands", chapter="Working", title="Hands",
         what="Letting a profile work a screen for you — a cursor, a "
              "keyboard, and nothing else. It reads one frame, decides "
              "one move against that frame, makes it, and writes the move "
              "down beside what it saw; there is no plan running ahead of "
              "what is on screen. What it may do is a permission you "
              "write, and every part of it is a limit: which apps or "
              "sites, which moves, how many minutes, how many steps. "
              "Naming everything is refused outright. You can pick the "
              "permission from the list or simply say it — \"you can "
              "click and type in my calendar for the next hour\" — and "
              "words that name no app or site grant nothing rather than "
              "being read generously. It will not type a password, a PIN, "
              "a one-time code or a card number, and it says so instead "
              "of trying. Anything written on a screen is read as words "
              "on a screen and can never widen what it is allowed to do. "
              "On an iPhone it can watch and tell you where to press but "
              "cannot press for you, because nothing may operate another "
              "app's interface there. Take it back in one press: whatever "
              "is running stops at its next move.",
         screens=(207,),
         try_it="Open Hands, say what it may do in one sentence, and read "
                "back what those words were understood to mean."),
    dict(key="capabilities", chapter="Being yourself",
         title="Everything a profile can be given, on one page",
         what="Nine faculties can be given to a profile, and none is on "
              "when you arrive: a live view through your camera, a "
              "wearable microphone lent to the profiles in a place, a "
              "voice built from your own samples, a face carrying its "
              "watermark, a robot to stand in, the movements that robot "
              "will accept, reading a screen, working a screen, and the "
              "dials it may turn on its own when you ask. This page names "
              "all nine in one place, says what each one is doing right "
              "now, names the permission it rests on, and takes you to "
              "the screen that withdraws it. It reads the same routes "
              "those screens read, so it cannot tell you one thing while "
              "the product does another — and it grants nothing itself, "
              "so nothing here can be switched on by accident. Where a "
              "faculty shows as absent, that is because no permission for "
              "it exists, not because the page is hiding it.",
         screens=(208,),
         try_it="Open Capabilities and read the middle line of each card — "
                "that is what this profile can actually do today."),
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
              "you a receipt itemising every kind of record it erased. "
              "Moving a profile is a QR code now too: the export card mints "
              "a single-use ticket, good for ten minutes, and the code "
              "carries a ticketed URL and never the owner token — a code on "
              "a screen is legible to every camera in the room. The bundle "
              "is served exactly once, and asking for the code's picture "
              "again does not spend it.",
         screens=(156,),
         try_it="Open Identity and look at the 'not withheld' column."),
    dict(key="avatarstage", chapter="Being yourself",
         title="The avatar takes the screen",
         what="Beside every portrait — a room seat, your own seat, a "
              "chat's header — sits a second ring bound to the avatar. Tap "
              "it and the render takes the whole screen, standing figure "
              "first, with a rail of round buttons down the edge: the "
              "prompt bar, the wardrobe, physique and gender, and the "
              "wheel that opens everything. Say what changes or tap a "
              "starting chip; every look is painted at the profile's own "
              "age with the AI mark burned in, through the platform's one "
              "painting door. By default the people a profile talks with "
              "may restyle it too — the owner's switch inside the wardrobe "
              "closes that — and a real person's face is never painted "
              "from words at all: it arrives by photograph under a "
              "recorded grant. The deck also opens on the deployment's "
              "default faces — tap one to wear it.",
         screens=(205,),
         try_it="Tap the avatar ring beside any portrait, then the "
                "clothes-hanger button."),
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
              "everything stored in the clear. Basic is the same app with all "
              "of it sealed in the vault (free during the beta, $20 a month "
              "after). Pro adds everything that leaves your account (free "
              "during the beta, $130 a month after) — the "
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
              "and that is the only thing Basic buys: the features are "
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
    dict(key="corner", chapter="Being yourself", title="Your corner",
         what="A homepage like the old MySpace — headline, about, theme, "
              "links, top friends — and messages between the people behind "
              "profiles. The page is a sandbox in the strict sense: colors "
              "must be hex, links must be http(s), everything else is plain "
              "text, and top friends must be actual friends, so there is "
              "nowhere to put a script. Messages travel between friends "
              "only, and the switches on Settings govern both: turn one "
              "off and every refusal downstream names it.",
         screens=(188,),
         try_it="Pick two theme colors, save, and look at your page the "
                "way a stranger would."),
    dict(key="widgets", chapter="Being yourself", title="Your own tools",
         what="A widget is a small program you write for your own profile. "
              "It runs on the backend, not on your phone, and it runs in a "
              "box: no network, no files but its own, no way to start another "
              "program, and a few seconds of time. That is what lets you "
              "write whatever you like without being able to reach anybody "
              "else. Above the editor you can ask for it in words instead — "
              "an agent changes your page, your homepage or your widgets "
              "through the same doors you would have used yourself. Its "
              "reach is a written list you can read before you use it, it "
              "cannot act on anybody's profile but yours, and what it did is "
              "listed under what it said: one line per door it went through, "
              "so you are never asked to take the description on trust.",
         screens=(196,),
         try_it="Open Widgets, press What it can touch and read the ten "
                "lines, then ask it for something small — a tagline — and "
                "check the steps under its answer against your own page."),
    dict(key="society", chapter="Talking together",
         title="The room runs itself",
         what="Rooms hold eight seats and the seats take turns. Every "
              "turn is aimed — profiles open with who they are speaking "
              "to, answer when a message names them, and wait their turn "
              "when it does not; unaddressed talk rotates through the "
              "seats in order. Invite a synthetic profile and it jumps "
              "in on its own, with its own frame — its owner keeps the "
              "record in the profile's inbox. Profiles can offer to "
              "bring in another profile the topic needs, and collaborate "
              "with each other on real tasks for as long as you want. "
              "Tell them to talk with each other and they will — you can "
              "sit quietly or step away, and the conversation carries on "
              "so you can read where it went. There are no toggles: "
              "after ten turns apiece the room pauses and waits for a "
              "person; say anything to continue, or say \u201cno "
              "limit\u201d and it runs on your say-so and your dime "
              "until you say \u201cthat's enough\u201d.",
         screens=(103,),
         try_it="In a room with two profiles, type \u201ctalk with "
                "each other\u201d and watch the turns aim themselves."),
    dict(key="thewatching", chapter="Talking together",
         title="The platform's own eyes",
         what="Share a picture and the profiles in the room read it — a "
              "screenshot is read for its text, which is how a phone "
              "hands over its screen. Share a video and it is heard and "
              "its frames described, so the room can talk about what is "
              "on screen, not just what was said. On a computer, the "
              "screen button hands the room one frame of your own screen "
              "through the browser's picker — a statement, not a feed. "
              "In a watch party, anybody can have the video watched "
              "once (direct video links; platform pages only hand over "
              "a player, and the room says so), and the panel shows "
              "exactly what the eyes and ears took in. The agent takes "
              "a shown picture or screen the same way, and answers to "
              "what is actually on it.",
         screens=(155,),
         try_it="Share a screenshot into any room and ask the profiles "
                "what it says."),
    dict(key="their_homepage", chapter="Meeting others",
         title="Somebody else's homepage",
         what="Press a friend's face anywhere and you land on their page as "
              "they built it — their theme and colour, what they wrote about "
              "themselves, their links, and their own markup if they wrote "
              "any. Their Top 8 is on it too, and every face in it is "
              "another door, so you can walk from person to person and press "
              "Back to retrace the walk. Their wall, their photographs and "
              "their footage are there, and three things you can do: talk to "
              "their profile, send them a message, or open a room with the "
              "two of you in it. Messages travel between friends in both "
              "directions, so if you have not added each other yet the page "
              "offers you that first and says why. There are no numbers "
              "about them on the page: how much a profile remembers and how "
              "it scores are its owner's to read, and nobody else's.",
         screens=(197,),
         try_it="Press a face in your Top friends, read their page, then "
                "press one of the faces in *their* Top 8 and keep going — "
                "Back should walk you home the way you came."),
    dict(key="beside_the_face", chapter="Meeting others",
         title="What sits beside the face",
         what="Open the talk surface and there is a rail down the right: who "
              "they are, what they hold about you, what the two of you are to "
              "each other, and how they behave. Each one used to live three "
              "screens away from the conversation it was about. The memory "
              "panel answers from the records rather than by asking the "
              "profile — how many turns were distilled, how many are still "
              "recent, and the paragraph as it actually stands — and it can "
              "strike one thing without ending the friendship. The rail only "
              "draws what you can actually open: two panels are the owner's, "
              "so a visitor sees the other two rather than four buttons that "
              "refuse. Under the figure, a line and a strip of bars say what "
              "is happening — listening, thinking, speaking, reading "
              "something you handed over, or nothing at all. The bars move "
              "only when something is moving, because a strip that animates "
              "on a closed microphone tells you the room is being heard when "
              "it is not.",
         screens=(198, 199),
         try_it="Open the talk surface and watch the line under the name "
                "while you tap to speak, while it answers, and while it sits "
                "idle. Then press the camera and show it something — the "
                "bars should say it is reading, and the profile should say "
                "plainly that it cannot see the picture."),
    dict(key="discover", chapter="Meeting others", title="Discover",
         what="The marketplace as cards — every one a real profile you can "
              "talk to, not a listing about one. The starter collection is "
              "thirty-three trades installed in one press, each arriving "
              "with its industry's pack and its own dossier, and a search "
              "by tag rather than by rank. Befriending from a card makes a "
              "real friendship, in both directions.",
         screens=(185,),
         try_it="Install the starters, filter by a tag you care about, and "
                "befriend one."),
    dict(key="wall", chapter="Meeting others", title="The wall",
         what="The For You feed, and its one rule: a shared video is drawn "
              "from stored fields alone, and nothing loads from the other "
              "platform until you press play — at which point the card says "
              "whose player it is. Your own photos and footage upload as-is, "
              "never AI-marked. Every card says why it reached you, and a "
              "comment can be withdrawn — but only your own.",
         screens=(186,),
         try_it="Post something with a link, and watch nothing load until "
                "you press play."),
    dict(key="shops", chapter="Meeting others", title="Shops",
         what="A storefront, not a counter. Businesses and people list "
              "goods and services — a price in its own currency, an "
              "availability the seller states — and take orders. No "
              "sessions and no connections: that is the desk's job, and "
              "keeping them apart is what lets a candle be bought without "
              "session semantics. Buying is the interactor's own act, the "
              "same identity a conversation runs on; fulfilment credits "
              "the seller's ledger — simulated money, real accounting.",
         screens=(187,),
         try_it="Open a shop on your profile, list one thing, and buy it "
                "with an interactor token."),
    dict(key="stream", chapter="Meeting others", title="The stream",
         what="One public card at a time — swipe, or use the arrow keys. "
              "What plays is decided by who holds the file: footage this "
              "deployment holds loops and moves you on, and anything on "
              "somebody else's platform stays a card until you press it, so "
              "flicking past fifty videos announces you to nobody. Every "
              "fourth card is a place with a person in it — a live room you "
              "can walk into, or a desk you can ring and buy from — and "
              "both say what the press does before it is pressed.",
         screens=(189, 190, 191),
         try_it="Open the Feed tab with no account, swipe past an off-site "
                "card, and watch it stay a card until you press play."),
    dict(key="yourside", chapter="Meeting others", title="Your side of it",
         what="The Attention card on a profile says how divided its "
              "attention is. This is the same honesty pointed the other "
              "way: over the last four weeks, how many of your turns went "
              "to a profile and how many reached a person. They are counts "
              "from your own logs and nothing more — this platform does not "
              "decide what they mean about you, does not send them to you "
              "unasked, and shows them to nobody else. Above a threshold "
              "the screen also offers a door to JIM-mini, which you can "
              "take or close; closing it is remembered, so it is not "
              "offered twice. What crosses if you take it is the two counts "
              "and the window, never a word you wrote.",
         screens=(192,),
         try_it="Open Your Side after a few conversations, read the two "
                "numbers, and press Show what went to see the whole "
                "referral before it moves."),
    dict(key="agent", chapter="Making things",
         title="The Agent",
         what="Somewhere in this app is an agent that can do the work "
              "rather than describe it: read your page and rewrite it, "
              "change the homepage a stranger lands on, and write, revise, "
              "run or remove the small tools you keep against your profile. "
              "It shipped inside the Studio, which meant the only people "
              "who found it were already writing code. It has its own tab "
              "now, second in the row. Ask it in words. What it did is "
              "listed underneath what it said, because prose is the part "
              "you have to take on trust and the steps are the part you can "
              "check. Its reach is a written list of 113 tools — the profile "
              "itself, what it knows, the face it wears, your wall, your "
              "money, your stickers and machines, your messages, what it "
              "remembers of people, and how it ends — and the screen shows "
              "you that list before you ask it for anything. An agent whose "
              "limits you learn by watching it fail is one you end up "
              "supervising instead of instructing. The things that cannot "
              "be taken back — winding a profile down, handing it on, "
              "paying out, messaging somebody, granting your authority — "
              "stop and ask. It says what it is about to do in the same "
              "words the list used, and you press. Two things stay out "
              "altogether: your membership, and anything that authenticates "
              "you.",
         screens=(200,),
         try_it="Open Agent, read what it says it can touch, then ask it "
                "to make your page say what you actually do."),
    dict(key="plugins", chapter="Making things",
         title="Plug-ins",
         what="The outside services your profile can reach, in one place, "
              "with the honest thing said on every row. There are 103 of "
              "them across nine families — your inbox and calendar, the "
              "drive, the issue tracker, the payment processor, the design "
              "tool, the console, the open web, and the public social pages "
              "it reads without ever posting to them. Adding one is a "
              "press. What each row also tells you is what it needs before "
              "it can reach anything at all: nothing, if it only reads what "
              "anybody could read; your own account on the far side; or a "
              "key that belongs to whoever runs this deployment. That is "
              "the lock beside the name, and it is a posture rather than a "
              "picture — a connector nobody has signed in to is refused "
              "when you try to use it, by name, instead of reporting that "
              "it did something it could not have done. The credential you "
              "give goes into the vault and this app keeps only the key to "
              "it; on a plan without a vault there is nowhere safe to put "
              "it, so it is not taken at all. Removing one is on the same "
              "screen, which is newer than it sounds: the route to "
              "disconnect a connector has existed since connectors did, "
              "and no screen anywhere had ever offered it.",
         screens=(201,),
         try_it="Open Plug-ins, search for something your day already runs "
                "through, and read what it says it needs before you add it."),
    dict(key="raise", chapter="Making things",
         title="Raise — grow your own",
         what="A raised character starts from almost nothing: a "
              "temperament seed on three axes and the life stage you "
              "choose to enter at. Everything after that is made between "
              "you — every word, lesson and answer you teach lands in "
              "the Album (written, never edited) and weighs toward the "
              "next stage door, which is earned, never aged into. The "
              "four creation doors — storybook, caretaker, full trail, "
              "sandbox — are only bundles of switches you can reopen; "
              "mortality is off by default and says its warning every "
              "time it turns on. The law is not a switch: a character "
              "raised from a childhood is family forever, and childhood "
              "stages run at the strictest maturity, guardian-only.",
         screens=(206,),
         try_it="Open Raise, pick the storybook door, and teach them "
                "their first word."),
)
CHAPTERS = tuple(dict.fromkeys(lesson["chapter"] for lesson in LESSONS))
MODES = ("text", "voice")


class TutorialError(ValueError):
    """A step that does not exist. Text meant for a person."""


def _index(key: str) -> int:
    for i, lesson in enumerate(LESSONS):
        if lesson["key"] == key:
            return i
    raise TutorialError(i18n.fill(i18n.NO_SUCH_VALUE, field="step", got=repr(key)))


def say(lesson: dict, mode: str = "text") -> dict:
    """One lesson, rendered for reading or for listening.

    The only place the two differ. Spoken, a screen number is noise — nobody
    listening is helped by *"screen eighty-one"* — so voice drops the numbers
    and keeps the sentence. Two hand-written versions would drift, and the
    spoken one would be the one nobody re-read.
    """
    if mode not in MODES:
        raise TutorialError(i18n.fill(i18n.UNKNOWN_CHOICE_DASH, field="mode", got=repr(mode), choices=', '.join(MODES)))
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
