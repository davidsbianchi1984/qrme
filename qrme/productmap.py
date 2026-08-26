"""What this console is, told to the things that talk for it.

A synthetic profile is somebody's stand-in inside an application, and until
now it knew everything about the person it represents and nothing about the
place it lives. Asked *where do I change what you're allowed to do*, a
mechanic profile answered like a mechanic who had never seen the app — which
is exactly right for the character and exactly wrong for the moment.

    asked     can this profile do it
    mattered  can the console, and where is it

The same gap opened wider the day a conversation could be carried around the
app: somebody walking from Chat to Settings with a profile in their pocket is
asking it to help with the screen they just opened.

Every surface the census in `tests/ui_screens.txt` knows about has a row
here, and a test holds the two together in both directions. A screen added
without a row fails the suite — which is the point, because the failure this
answers is a capability shipping and nothing that speaks for the product ever
hearing about it.

## Why it is selected rather than sent

Sixty-eight doors is a manual, and a prompt full of manual stops noticing the
person in front of it — a real risk here, where the prompt already carries a
persona, a relationship, a language directive and whatever the vault
remembers. So a turn carries three things:

  * the **core** — the doors that are load-bearing on any turn, which here
    means the consent ones: what the agent may do, what has been delegated,
    who is allowed to know, contesting a profile that depicts you, and the
    way to reach a person;
  * the **relevant** — the doors whose own words appear in what the person
    just said, most-matched first, capped;
  * the **index** — the names of everything else, and nothing about them.

The index is the part that makes the shrug impossible. A profile that can see
`Permissions tab` in a list says *there is a screen for that* instead of *I
do not know*, and that sentence is the whole of what this file buys.

## What a row is not

It is not permission, and it is emphatically not a persona. Nothing here lets
a profile change anything — the delegation policy decides that — and nothing
here tells it to stop being who it is. A mechanic who can point at the
Permissions tab is still a mechanic.
"""

from __future__ import annotations

import re
from typing import NamedTuple


class Door(NamedTuple):
    """One surface of the console, as something that talks can describe it."""

    #: The component, exactly as `tests/ui_screens.txt` names it. The join
    #: key — a row for a surface that no longer exists, or a surface with no
    #: row, is what the guard beside this file fails on.
    surface: str
    #: What the person taps, in the words the console itself renders.
    place: str
    #: What it is for, in one line.
    what: str
    #: The person's own words for it — what somebody would *say*, not what
    #: the code calls it.
    cues: tuple[str, ...]
    #: On every turn regardless of the message. Reserved for the doors whose
    #: absence is a consent failure rather than an inconvenience.
    always: bool = False


DOORS: tuple[Door, ...] = (
    # -- where people are --------------------------------------------------
    Door("Home", "Home tab",
         "the front page — press a face and land on that person's homepage",
         ("home tab", "front page", "faces", "start screen")),
    Door("Profile", "a profile's own page",
         "whoever's page you are looking at, theirs or your own",
         ("their page", "profile page", "someone's page", "homepage")),
    Door("Public", "the console without an account",
         "what somebody who has not signed up can see and do",
         ("without an account", "not signed in", "guest", "logged out")),
    Door("Onboarding", "the way back in",
         "signing in, and recovering a profile you already have",
         ("sign in", "log in", "recover", "forgot", "get back in",
          "create an account")),
    Door("Discover", "Discover tab",
         "finding profiles and places you have not met",
         ("discover", "find someone", "search for people", "browse people")),
    Door("Feed", "Feed tab",
         "one card at a time, swipe for the next — what is public, playing "
         "and open right now",
         ("feed", "swipe", "what's playing", "what's on")),
    Door("Wall", "Wall tab",
         "the wall — posts and video on a profile",
         ("wall", "post", "my posts", "video wall")),
    Door("Corner", "My Space tab",
         "your public page and your messages; what you edit here is exactly "
         "what a visitor sees",
         ("my space", "my page", "my corner", "what visitors see")),
    Door("Friends", "Friends tab",
         "friends, and the inbox",
         ("friend", "inbox", "message someone", "contacts")),
    Door("Audience", "Audience tab",
         "who follows a profile, and what they pay",
         ("follow", "audience", "subscriber", "who follows")),
    Door("Named", "Lookup tab",
         "one named thing, and who may ask about it",
         ("lookup", "look up a name", "named thing")),

    # -- talking -----------------------------------------------------------
    Door("Chat", "Chat tab",
         "talking with a synthetic profile — typed, dictated, or out loud",
         ("chat", "talk to", "conversation", "speak to", "message it")),
    Door("Briefcase", "the briefcase on the chat composer",
         "the documents a conversation carries",
         ("briefcase", "attach a document", "send a file", "paperwork")),
    Door("TalkRail", "the owner's rail above a chat",
         "the owner-only panels of a conversation",
         ("owner panel", "chat rail", "owner tools")),
    Door("Waveform", "the wave on the composer",
         "the voice level while somebody is speaking",
         ("waveform", "voice level", "the wave")),
    Door("Stranger", "Guest Access tab",
         "arriving, and talking to a stranger",
         ("stranger", "guest access", "someone new", "first visit")),
    Door("Referrals", "Referrals tab",
         "handing a conversation to somebody qualified",
         ("referral", "hand it to", "qualified", "professional help",
          "refer me")),
    Door("Lobby", "Gaming tab",
         "who is in the game with you, and handing a conversation on",
         ("game", "gaming", "lobby", "play together")),
    Door("Rooms", "Rooms tab",
         "shared places — flat, AR and VR rooms",
         ("room", "meet in", "shared space", "vr", "ar")),
    Door("Inside", "the Room screen",
         "inside a room — the camera, the microphone, and what is shared "
         "between the people in it",
         ("inside a room", "share my screen", "share a file",
          "in the room")),
    Door("Live", "Live Now tab",
         "what is live in a shared place — a camera being shared, a "
         "microphone lent",
         ("live", "going live", "broadcast", "streaming now")),
    Door("WatchParty", "Watch Party tab",
         "watching a posted video together, with synthetic profiles in the "
         "room",
         ("watch party", "watch together", "watch it with me",
          "watch this", "watch a video", "video with you")),
    Door("Solitude", "My Attention tab",
         "who may reach you, and when",
         ("do not disturb", "my attention", "leave me alone", "quiet hours",
          "who can reach me")),

    # -- what a profile is -------------------------------------------------
    Door("Identity", "Identity tab",
         "who this profile is, who is allowed to know, and how it ends",
         ("identity", "who am i", "who knows", "anonymous", "who i am"),
         always=True),
    Door("Presence", "Presence tab",
         "how this profile presents itself, everywhere it is seen",
         ("presence", "how i look", "appearance", "avatar", "portrait")),
    Door("SkinPicker", "the avatar deck on Identity",
         "choosing what a profile wears",
         ("avatar", "avatar deck", "change my picture", "pick a face",
          "skin")),
    Door("SkinTiles", "the avatar tiles",
         "the faces there are to choose from",
         ("avatar tiles", "which faces", "face options")),
    Door("InWords", "Language & Name tab",
         "the words a profile uses, and the name it answers to",
         ("language", "my name", "what to call", "rename",
          "speak spanish")),
    Door("Voice", "Voice tab",
         "the voiceprint — permission, the recording, and the voice a "
         "profile speaks in",
         ("voice", "voiceprint", "how it sounds", "clone my voice",
          "record my voice")),
    Door("TheMark", "Watermark tab",
         "the mark this profile's work carries, and what it has published",
         ("watermark", "the mark", "ai label", "signature on my work")),
    Door("Workshop", "Profile Builder tab",
         "what a profile is made of, and how the owner shapes it",
         ("profile builder", "build a profile", "make a profile", "workshop",
          "shape it")),
    Door("Blend", "Blend tab",
         "blending two profiles into a hybrid that never claims to be "
         "either one",
         ("blend", "hybrid", "mix two", "combine profiles")),
    Door("Simulate", "What If tab",
         "what would they do — rehearsing a situation with a profile",
         ("what if", "simulate", "rehearse", "what would they do",
          "practice")),
    Door("Passing", "Beginning and passing on",
         "how a profile starts, what it is taught, who holds it after, and "
         "the one press from a wrist",
         ("passing on", "who gets it", "after i die", "inherit", "legacy",
          "memorial")),
    Door("Relationships", "Relationships tab",
         "how a profile stands with each person it knows",
         ("relationship", "how we know each other", "who is close")),
    Door("Memory", "Memory Vault tab",
         "what a pair remembers, sealed — shown, and something you can "
         "curate",
         ("memory", "remember", "forget that", "what do you remember",
          "vault")),

    # -- what it may do ----------------------------------------------------
    Door("Agent", "Agent tab",
         "the collaborator with its own front door — it changes your page, "
         "your sandbox and your widgets through your own doors",
         ("agent", "the collaborator", "change my page", "edit my page",
          "build me")),
    Door("Allowed", "Permissions tab",
         "what the agent may do, one row at a time",
         ("permission", "allowed", "what can it do", "let it", "consent",
          "turn that off"),
         always=True),
    Door("Delegate", "Delegation tab",
         "delegation and work — what a profile may do on your behalf",
         ("delegate", "on my behalf", "act for me", "authority"),
         always=True),
    Door("Assist", "Tasks tab",
         "the profile working for its owner, and what it leaves behind",
         ("task", "do it for me", "work for me", "assign")),
    Door("Robots", "Robots & Devices tab",
         "a body to speak through",
         ("robot", "device", "speak through", "hardware")),
    Door("Plugins", "Plug-ins tab",
         "the plug-in storefront, and what each row can reach",
         ("plug-in", "plugin", "integration", "connect an app")),
    Door("Studio", "Widgets tab",
         "tools you write for your own profile — a function in a box with "
         "no network",
         ("widget", "my own tool", "studio", "little program", "script")),
    Door("Remainder", "More Tools tab",
         "the last of the tools, in one place",
         ("more tools", "the rest", "what else is there")),

    # -- money and terms ---------------------------------------------------
    Door("Market", "Marketplace tab",
         "browsing, searching, placing, pricing and buying",
         ("marketplace", "buy", "sell", "listing", "price", "for sale")),
    Door("Shops", "Shops tab",
         "goods and services from businesses and people — not a desk, no "
         "sessions",
         ("shop", "store", "goods", "services", "order something")),
    Door("Desk", "Desk tab",
         "sessions — booking time with a profile, and holding one open",
         ("desk", "book a session", "appointment", "book time",
          "consultation")),
    Door("Visiting", "Visits tab",
         "the other side of a desk, and leaving a profile somewhere",
         ("visit", "drop in", "leave it somewhere")),
    Door("Signing", "Signing tab",
         "signing, from the console",
         ("sign", "signature", "signing")),
    Door("Exchanges", "Exchanges tab",
         "the agreement two people sign before work changes hands",
         ("exchange", "agreement", "contract", "terms of work")),
    Door("Grants", "Skill Lending tab",
         "lending a skill inside a place two people already share",
         ("lend a skill", "skill lending", "borrow a skill", "grant")),
    Door("Selling", "Earnings tab",
         "the other side of the counter",
         # "can I get my money out" reached nothing while "payout" sat in
         # the row — the words a table is written in are rarely the words
         # somebody uses when they want the thing.
         ("earnings", "payout", "what i earned", "revenue", "get paid",
          "money out", "cash out", "withdraw", "my money")),
    Door("Placements", "Ad Placements tab",
         "where a rated profile is marketed",
         ("placement", "advertis", "marketed", "promote")),
    Door("Campaigns", "Campaigns tab",
         "where the money goes",
         ("campaign", "where the money goes", "spend", "budget")),
    Door("Reaching", "Outreach tab",
         "one person, and what reaching out to them costs",
         ("outreach", "reach out", "cold message", "contact someone new")),
    Door("Plans", "Plans & Billing tab",
         "the price list, and this account's membership",
         ("plan", "billing", "subscription", "upgrade", "how much",
          "membership")),
    Door("Leaving", "Exports & Licensing tab",
         "what leaves this deployment, and on what terms",
         ("export", "licensing", "take it with me", "download my",
          "what leaves")),
    Door("Org", "Org tab",
         "the ecosystem — an organisation of profiles, and who leads it",
         ("organisation", "organization", "org", "team of profiles",
          "ecosystem")),
    Door("Beacons", "Beacons tab",
         "connections to the world — a code on a wall, and a code on a "
         "platform",
         ("beacon", "qr code", "code on a wall", "link my account")),

    # -- the doors that answer for the product -----------------------------
    Door("Contest", "Disputes tab",
         "contesting a profile that depicts you, and holding what one says",
         ("dispute", "contest", "that's not me", "depicts me", "take it "
          "down", "complain about a profile"),
         always=True),
    Door("Matters", "Support tab",
         "somebody's matter, from saying it to seeing what happened to it",
         ("support", "help me with", "raise it", "my matter", "complaint"),
         always=True),
    Door("Settings", "Settings tab",
         "the control centre — what this deployment can reach, and the keys",
         ("setting", "control centre", "control center", "api key",
          "configuration")),
    Door("ProviderTiles", "the model tiles on Settings",
         "which model answers",
         ("which model", "provider", "openai", "anthropic", "model")),
    Door("Access", "Accessibility tab",
         "ability is not a gate — what the product does about each need, "
         "and all of it works without an account",
         ("accessibility", "screen reader", "blind", "deaf", "caption",
          "large text", "dyslexia", "one hand", "read it to me",
          "can't see", "cannot see", "hard to hear", "too small")),
    Door("Guide", "Tour tab",
         "the walkthrough, and what the help box can answer",
         ("tour", "walkthrough", "show me around", "how does this work",
          "guide me")),
    Door("Problems", "the report-a-problem screen",
         "what went wrong, and exactly what leaves this device",
         ("report a problem", "bug", "broke", "crash", "not working",
          "broken")),
    Door("ProblemNotice", "the first-run notice before anything is sent",
         "what a problem report contains, said once before the first one "
         "goes",
         ("what gets sent", "before i report", "leaves this device")),
    Door("Refusal", "the refusal card, wherever one happens",
         "a refusal rendered as what it is, with the reason and the way on",
         ("refused", "why was that blocked", "it said no", "denied")),
)

#: How many message-matched doors a turn may carry beyond the core. Six —
#: the prompt this joins already carries a persona, a relationship, a
#: language directive and whatever the vault remembers, and the person in
#: front of it has to survive all of that.
LIMIT = 6

_HEAD = ("this application's own doors, and where each lives — when somebody "
         "asks for something that belongs to one, point at it by name "
         "instead of saying you cannot:")
_FOOT = ("answer questions about this application from these lines rather "
         "than from what assistants generally can or cannot do. Naming a "
         "door is not permission to act: what may actually be changed is "
         "decided by the delegation policy, not by this list. Stay in "
         "character while you do it — knowing where a screen is does not "
         "make you a help desk.")
_INDEX = ("the rest of this application, by name only — if one of these is "
          "what they are after, say so and name it rather than declining: ")


#: The endings a single-word cue may wear. Written out rather than stemmed
#: because a stemmer would need a dependency and would still be guessing:
#: this is the closed set of things English does to the handful of verbs and
#: nouns anybody uses to ask for a screen. It exists because a table matched
#: on the exact word only fires for people who happen to speak the way it was
#: typed — `follower` missed "who is following me", `medication` missed
#: "my medications", and each one landed the person in the index instead of
#: on the screen that was sitting in the navigation bar.
_ENDINGS = r"(?:e?s|ing|ed|er|ers)?"


def _row(d: Door) -> str:
    return f"- {d.what}: {d.place}"


def _hits(d: Door, said: str) -> int:
    n = 0
    for cue in d.cues:
        # Whole words, plural allowed. A cue list written in the singular
        # and matched in the singular is a table that only works when people
        # happen to speak the way it was typed — the sibling product's
        # `medication` missed "where are my medications", and phrases missed
        # anything reworded at all.
        pattern = (r"\b" + re.escape(cue) + _ENDINGS + r"\b") \
            if " " not in cue else re.escape(cue)
        if re.search(pattern, said):
            n += 1
    return n


def core() -> str:
    """The doors that ride every turn, message or no message.

    The consent ones. Getting *what may this thing do on my behalf* wrong is
    a harm rather than a disappointment, and so is a person who cannot find
    the way to contest a profile that depicts them or to reach somebody.
    """
    rows = [_row(d) for d in DOORS if d.always]
    return "\n".join([_HEAD, *rows, _FOOT])


def selected(message: str, limit: int = LIMIT) -> list[Door]:
    """The doors this message is about, most-matched first.

    Ties keep the table's order, so the answer does not reshuffle between
    two turns that said the same thing.
    """
    # The contract, checked where it is broken rather than three frames
    # down. A caller once handed this a list — a local variable in the
    # prompt builder shadowed the parameter — and the failure surfaced as
    # `'list' object has no attribute 'lower'` inside the selector, which
    # says nothing about where the mistake was.
    if message is not None and not isinstance(message, str):
        raise TypeError(
            f"the message selecting doors must be text, not "
            f"{type(message).__name__} — something upstream is passing the "
            "wrong thing, and the door selection is only where it shows")
    said = (message or "").lower()
    if not said:
        return []
    scored = []
    for i, d in enumerate(DOORS):
        if d.always:
            continue
        n = _hits(d, said)
        if n:
            scored.append((-n, i, d))
    scored.sort()
    return [d for _, _, d in scored[:limit]]


def index(exclude: set[str] | None = None) -> str:
    """Everything else, by name only.

    Names and nothing more: a door somebody can name is a door somebody can
    be walked to on the next turn, and that is the difference between
    routing and declining.
    """
    skip = exclude or set()
    names = [d.place for d in DOORS if d.surface not in skip and not d.always]
    return _INDEX + "; ".join(names)


#: The screens a client can say a person is standing on, by key. A closed
#: vocabulary rather than free text: the client names a screen it knows it
#: is, and an unknown key says nothing rather than guessing. Grown beside
#: DOORS, so the sentence uses the same names the doors do.
STANDING: dict[str, str] = {
    "chat": "the Chat screen",
    "talk": "the Chat screen's talk face — the full-screen voice view",
    "room": "a room (the Inside screen)",
    "agent": "the Agent screen",
}


def lines(message: str = "", limit: int = LIMIT,
          standing: str | None = None) -> list[str]:
    """The whole block for one turn: core, then relevant, then the index.

    `standing` is which screen the person is looking at while they ask,
    when the client said. The field report that earned it: asked where to
    attach a file, a profile described the Chat composer's briefcase — to
    somebody standing in a room, whose file door is the paperclip by the
    Type box. Every door it named existed; none of them were where the
    person was. Directions start from where somebody stands or they are
    trivia.
    """
    picked = selected(message, limit)
    out = [core()]
    place = STANDING.get(standing or "")
    if place:
        out.insert(0, (
            f"They are standing on {place} RIGHT NOW. Give directions from "
            "where they stand: a control on that screen is pointed to as it "
            "appears there, and a control on any other screen is said to be "
            "on that other screen, by name — directions for a screen they "
            "are not on send somebody hunting for a briefcase that is not "
            "there."))
    if picked:
        out.append("also relevant to what they just said:\n"
                   + "\n".join(_row(d) for d in picked))
    out.append(index({d.surface for d in picked}))
    return out


def block(message: str = "", standing: str | None = None) -> str:
    """One string, for a prompt that is assembled by joining parts."""
    return "\n".join(lines(message, standing=standing))
