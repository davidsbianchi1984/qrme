"""The help assistant that sits on every screen.

Every screen in QRME can be the first one somebody sees — a beacon scan lands a
stranger on a profile page, a shared link drops them into a room — and until
now the only thing on any of those screens that could answer a question was a
synthetic profile, which is the one thing that should never be answering
questions *about the product*.

So this is deliberately, structurally **not a profile**:

* **No name and no face.** QRME's whole subject is synthetic people who can be
  mistaken for real ones. A help assistant with a name and a portrait would be
  a thirty-fifth character, indistinguishable from the thirty-four the AI mark
  exists to disclose. This one is furniture, and says so.
* **It never speaks as anybody.** :data:`REFUSALS` catches the questions that
  ask it to — *what do you think of me*, *are you real*, *pretend you are* —
  and it hands them back to the profile the user is actually talking to, which
  is the thing that has a persona, a relationship and a moderation pipeline.
* **It answers about the product and does nothing else.** No endpoint here
  writes anything: it cannot place a beacon, change a setting, or send a
  message. The same boundary as `marketplace.assist` (which suggests searches
  and never runs one) and PDI's gate agent (which speaks a decision it did not
  make). A model can change the words on this surface and nothing else.

**It works with no model at all.** :data:`TOPICS` is written prose, matched by
keyword, and it is the answer rather than a fallback that apologises. A help
system that stops helping when a provider is down is a help system that is
absent on precisely the day everything else is confusing too — and a
self-hosted deployment with no API key configured is a supported, ordinary
setup here, not a degraded one.
"""

from __future__ import annotations

from . import llm

DISCLOSURE = ("Automated help for using QRME. This is not one of the synthetic "
              "profiles — it has no persona and no memory of you.")

# What it will not do, and where it sends you instead. Checked before anything
# else, because these are precisely the questions a help box on a page full of
# synthetic people invites.
REFUSALS = {
    "identity": (
        ("are you real", "are you human", "are you a person", "are you ai",
         "who are you really"),
        "I'm the help box — automated, no persona, no memory of you. The "
        "profile on this page is a synthetic profile, and its own page says "
        "so.",
    ),
    "roleplay": (
        ("pretend", "act as", "roleplay", "role play", "speak as", "be my"),
        "I only explain how QRME works. If you want to talk to somebody, the "
        "profile on this page is the one with a persona — I'd only be a worse "
        "copy of it.",
    ),
    "about_you": (
        ("what do you think of me", "how am i doing", "do you like me",
         "remember me", "do you remember"),
        "I don't know anything about you — no memory, no profile, nothing "
        "kept between questions. The profile you're talking to keeps its own "
        "memory, and you can read and delete it from the Memory Vault.",
    ),
}

# Written answers to the questions people actually arrive with. Grounded in
# what the product does rather than generated, so this surface is correct
# whether or not a model is reachable.
TOPICS: dict[str, tuple[tuple[str, ...], str]] = {
    "what_is_this": (
        ("what is qrme", "what is this", "what does this do", "explain qrme"),
        "QRME makes AI synthetic profiles: characters with a persona, a "
        "memory, and a relationship to each person who talks to them. Every "
        "one is marked as AI — the mark is burned into the portrait's own "
        "pixels, so it survives a screenshot or a crop.",
    ),
    "is_it_a_real_person": (
        ("is this a real person", "is this person real", "are they real",
         "synthetic", "is it ai"),
        "No. Everything with the AI mark is a synthetic profile — an invented "
        "character. A **live desk** is the opposite case: it belongs to a real "
        "person who is simply not at it right now, and carries a green "
        "'Live person — not AI' badge instead.",
    ),
    "beacons": (
        ("beacon", "qr", "qr code", "scanned", "scan", "sticker",
         "why am i here", "why am i on this page", "how did i get here"),
        "You scanned a beacon — a printed code somebody placed on purpose. It "
        "resolves to a profile's page. Scanning does nothing on its own: "
        "nobody is notified and nothing is recorded about you until you act.",
    ),
    "memory": (
        ("memory", "remember", "forget", "delete", "erase", "vault",
         "privacy", "what it knows"),
        "Each profile keeps memory per person, so what it remembers of you is "
        "yours and separate from everyone else's. The Memory Vault lists it, "
        "and you can delete any of it. Deleting a profile purges its vault "
        "records too.",
    ),
    "reviews": (
        ("review", "reviews", "rating", "ratings", "stars",
         "leave a review"),
        "A profile's front page carries a rating from people who have actually "
        "talked to it — a review needs a real interaction on record, and it's "
        "one per person, edited rather than stacked. The average always shows "
        "how many reviews it's an average of.",
    ),
    "relationships": (
        ("relationship", "why did it say", "why does it talk",
         "tone", "different"),
        "A profile answers differently depending on who's asking. The "
        "relationship you have with it — family, friend, stranger — "
        "conditions its tone and what it will discuss.",
    ),
    "desks": (
        ("desk", "live desk", "ring the bell", "nobody there"),
        "A live desk belongs to a real person who stepped away. Ringing the "
        "bell asks them to come back — it doesn't reach an AI, and the badge "
        "says 'Live person — not AI' for exactly that reason.",
    ),
    "adult": (
        ("18+", "adult", "rated", "age gate", "age-walled", "nsfw"),
        "Rated profiles are age-walled: they resolve to a gate rather than a "
        "page unless you're a verified adult, on every surface — handle, tag, "
        "beacon scan and marketplace alike.",
    ),
    "money": (
        ("pay", "price", "cost", "subscribe", "gift", "buy", "money"),
        "Commerce here is **simulated**: purchases, gifts and subscriptions "
        "write real rows on a creator's statement but no real funds move, and "
        "every money-bearing response says so in its own body.",
    ),
    "make_one": (
        ("create", "make a profile", "how do i start", "my own"),
        "Create a profile, give it a persona, and it's yours: you hold the "
        "owner token, you set what it may discuss, and you can export or "
        "delete everything it holds.",
    ),
}


# Asking for the tour, in the words people use. Kept beside TOPICS rather than
# inside it because the reply is not a paragraph — it is the first step of a
# walkthrough, and a topic that returned prose about tours would be the most
# annoying possible answer to "show me around".
_WALKTHROUGH: dict[str, tuple[tuple[str, ...], str]] = {
    "walk_me_through": (
        ("show me around", "walk me through", "give me a tour", "tutorial",
         "guide me", "how do i use this", "where do i start", "getting started",
         "teach me", "walkthrough", "show me how"),
        "",
    ),
}


# "Where is the thing that does X." The question the help box gets more than
# any other and answered worst, because a paragraph *describing* a feature to
# somebody who is asking where it lives is a correct answer to a question they
# did not ask.
#
# Keyed by tutorial lesson, so the directions cannot name a screen the
# walkthrough does not cover — `tutorial.LESSONS` already binds each lesson to
# its screens, and a test binds every lesson to an entry here. Add a feature,
# draw its screen, write its lesson, and the assistant can point at it or the
# suite fails.
#
# The phrases are what people type, not what the feature is called. Somebody
# looking for overlays types *change my face*; nobody types *overlays*.
DIRECTIONS: dict[str, tuple[str, ...]] = {
    "make_one": ("make a profile", "new profile", "create a profile",
                 "add a profile", "genesis"),
    "blend": ("blend", "hybrid", "combine profiles", "mix profiles",
              "both grandparents", "composite", "merge two profiles"),
    "predict": ("what would they do", "what would he do", "what would she do",
                "simulate", "simulation", "predict", "forecast",
                "run a scenario"),
    "proceeds": ("crowdfunding", "crowdfund", "donate", "donation",
                 "raise money", "fundraiser", "where the money goes",
                 "proceeds", "leave it to my family"),
    "ecosystem": ("organization", "departments", "department", "my company",
                  "coordinate", "team of agents", "agents work together",
                  "operational ecosystem"),
    "talk": ("send a message", "chat with", "talk to it", "message it",
             "where i am", "knows where i am", "my location", "environment",
             "the weather here"),
    "health": ("profile health", "how is it doing", "stats", "transparency",
               "what it knows", "sources"),
    "control": ("control center", "moderation", "boundaries", "steering",
                "turn it off", "settings", "switches"),
    "model": ("which model", "model picker", "swap the model", "claude",
              "chatgpt", "grok", "perplexity", "gemini", "api key",
              "change the ai"),
    "market": ("marketplace", "sell", "license", "listing", "knowledge pack",
               "buy a profile"),
    "reach": ("handle", "claim a name", "beacon", "qr code", "sticker",
              "get found", "share a link"),
    "desks": ("live desk", "ring the bell", "go live", "start a stream"),
    "social": ("friends", "my page", "the feed", "the wall", "post something"),
    "mic": ("lend my microphone", "microphone", "let it hear me", "channel 2",
            "mic"),
    "fullscreen": ("full screen", "fullscreen", "landscape", "sideways",
                   "rotate"),
    "together": ("watch party", "watch together", "watch with"),
    "work": ("exchange", "agreement", "sign something", "contract"),
    "games": ("game", "games", "play", "lobby", "co-op", "multiplayer"),
    "face": ("change my face", "face overlay", "mask", "disguise", "costume",
             "change my background", "background", "backdrop", "blur",
             "be anonymous", "anonymous", "hide my name"),
    "camera": ("share my camera", "show them", "channel 3", "live camera",
               "point my camera", "let them see", "show you the problem"),
    "screens": ("wall panel", "kiosk", "fixed screen", "put it on a screen",
                "second screen", "the corner", "the pane", "the dock",
                "little box", "mini window"),
    "guide": ("the guide", "the helper", "help button", "this assistant"),
    "welcome": ("the ai mark", "the mark", "the badge", "watermark"),
    "signup": ("sign up", "signup", "get started", "make an account",
               "join", "register", "pay", "payment", "card", "checkout"),
    "plans": ("price", "pricing", "cost", "how much", "plan", "plans",
              "subscription", "subscribe", "upgrade", "basic", "pro",
              "billing", "what do i get"),
    "workshop": ("source material", "sources", "what it knows",
                 "train it", "fine-tune", "finetune", "specialists",
                 "hand off a domain", "experience", "cv", "dials",
                 "steering", "how it comes across", "made of"),
    "bodies": ("robot", "robots", "a body", "humanoid", "android",
               "my robot", "bind a robot", "embodiment", "speak through",
               "task pack", "robot skills"),
    "placement": ("adult venue", "onlyfans", "fansly", "rated placement",
                  "place my profile", "market my profile", "18+ venue",
                  "adult marketing", "where is it advertised"),
    # Kept off `plans`, which answers "what does it cost". Somebody typing
    # these has already been stopped by something and wants to know what the
    # stop means — a different question with its own screen.
    "refused": ("why can't i", "why cant i", "not included", "not available",
                "locked", "refused", "greyed out", "grayed out",
                "needs pro", "needs basic", "not on my plan"),
    # "free" moved off `plans` and onto this lesson. Somebody typing it is
    # almost never asking what a tier costs — they are asking what the free
    # one gives up, and that question has its own screens.
    "storage": ("free", "is my data private", "private", "privacy",
                "encrypted", "encryption", "the vault", "vault",
                "who can read", "where is my data", "in the clear"),
    "voice": ("my voice", "clone my voice", "voice clone", "voiceprint",
              "sound like me", "speak in my voice", "enroll my voice",
              "record my voice", "voice"),
    # Kept off `welcome`, which explains what the AI mark *is*. Somebody
    # typing these wants the other direction — a passage in hand and no idea
    # whose it is — and that has its own screen.
    "whowrote": ("who wrote this", "who made this", "did you write this",
                 "whose work is this", "check this text", "was this ai",
                 "is this mine", "prove i wrote it", "trace this"),
    "role": ("advisor", "collaborator", "operator", "how should it work",
             "just do it", "give me advice", "work with me", "role"),
    # The words somebody uses when something has just broken, plus the ones
    # they use when they have noticed the reporting and want it to stop.
    "market": ("marketplace", "buy", "sell", "shop", "price", "for sale",
               "find a plumber", "hire", "listing", "search for someone"),
    "problems": ("what went wrong", "error", "errors", "it failed",
                 "something broke", "bug", "report a bug", "crash",
                 "stop sending", "stop reporting", "opt out", "diagnostics"),
    # People arrive at an exchange from the money side ("contract", "invoice")
    # or the file side ("send me the files"), and the point of the feature is
    # that those are the same screen. Both sets of words go here.
    # Two very different arrivals at one screen: somebody wanting the blue
    # tick, and somebody wanting out. Both belong here.
    # People arrive here from three directions — decorating a page, putting
    # a profile on a physical screen, and asking what a wall can show.
    "presence": ("my page", "customise", "customize", "theme", "layout",
                 "html", "tagline", "front page", "what people see",
                 "wall panel", "kiosk", "screen", "display", "shop window",
                 "put it on a screen", "surfaces"),
    # Somebody worried about being watched, and somebody trying to share a
    # camera, arrive with very different words at the same screen.
    "live": ("camera", "share my camera", "show them", "video call",
             "is anyone watching", "recording", "who can see", "bystander",
             "microphone", "lend my mic", "they can hear", "mute",
             "mask", "overlay", "hide my face", "filter"),
    # The words somebody uses when they have just found a profile of
    # themselves, and the words an owner uses about their own held messages.
    "contest": ("that is me", "this is me", "profile of me", "impersonating",
                "take it down", "takedown", "remove this profile", "object",
                "objection", "i did not agree", "without my permission",
                "my late", "estate", "withdraw consent", "revoke",
                "moderation queue", "approve", "waiting for approval"),
    # "Where is the tour" is a different question from "show me around",
    # which _WALKTHROUGH already answers by starting one. These are the words
    # for the screen that lists it, and for the dock's own settings.
    "guide": ("the guide", "the tour", "lessons", "what am i looking at",
              "what is this screen", "explain this screen", "help topics",
              "what can you answer", "the dock", "the pane", "the bubble",
              "move the dock", "hide the dock", "corner"),
    "identity": ("verify", "verified", "badge", "blue tick", "prove it is me",
                 "anonymous", "hide my name", "who checked", "my profiles",
                 "rename", "delete my profile", "delete this profile",
                 "close my account", "export", "retire", "sunset", "memorial",
                 "avatar", "emblem", "picture", "portrait"),
    "exchanges": ("exchange", "agreement", "contract", "sign", "signature",
                  "send me the files", "hand over", "deliverables",
                  "what is included", "scope", "invoice", "manifest"),
    "grants": ("lend", "borrow", "lent", "share a skill", "let them use",
               "grant", "loan", "use my", "revoke", "stop letting them"),
    "party": ("watch together", "watch party", "watch with", "same video",
              "sync video", "viewing party", "watch a video together"),
}


def where_is(question: str) -> dict | None:
    """Directions to the screen that does a thing, rather than a description.

    The other half of the walkthrough. `show me around` starts at the
    beginning; this answers *I know what I want, where is it* — which is the
    same question the dock's routing table answers for the pane, read from the
    same place so the assistant and the pane cannot disagree.
    """
    from . import dock, tutorial

    key = None
    hits = 0
    q = (question or "").lower().strip()
    if not q:
        return None
    import re

    for lesson_key, phrases in DIRECTIONS.items():
        n = sum(1 for p in phrases
                if re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", q))
        if n > hits:
            key, hits = lesson_key, n
    if key is None:
        return None

    lesson = tutorial.LESSONS[tutorial._index(key)]
    screens = list(lesson["screens"])

    # If the same thing is also a face on the pane in the corner, say so — that
    # is the whole reason the dock is discoverable at all. Somebody who never
    # taps the helper button will never find out it opens onto anything.
    in_dock = None
    for face_name, route in dock.ROUTES.items():
        if route["screen"] in screens:
            in_dock = dock.route(face_name)
            break

    say = f"{lesson['title']}: {lesson['try_it']}"
    if in_dock:
        say += (f" It is also a face on the pane in the corner — tap the help "
                f"button and choose {in_dock['title']}.")
    return {"lesson": key, "title": lesson["title"], "screens": screens,
            "say": say, "dock": in_dock, "walkthrough_step": f"/tutorial/steps/{key}"}


def _model_is_real() -> bool:
    """Whether a *real* provider is configured, as opposed to the offline stub.

    The stub exists so the platform and its tests run with no credentials, and
    it answers everything with deterministic filler. That is right for a
    persona — a character saying something bland is still in character — and
    wrong here, where the written answer in :data:`TOPICS` is simply better
    than "[stub reply in a warm tone]". A deployment with no API key gets the
    prose, which is the whole reason the prose is written out.
    """
    try:
        return llm.resolve_choice(None) != "stub"
    except Exception:
        return False


def _match(question: str, table) -> str | None:
    """Best-matching answer, on whole words.

    Not a substring test: "age" is inside "page" and "message", so
    *"why am I on this page"* matched the age-gate topic and confidently
    explained the 18+ wall to somebody asking why they were looking at a QR
    code. Short keys make substring matching actively wrong rather than merely
    imprecise, so keys match at word boundaries.
    """
    import re

    q = question.lower().strip()
    best, score = None, 0
    for keys, answer in table.values():
        hits = sum(1 for k in keys
                   if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", q))
        if hits > score:
            best, score = answer, hits
    return best


def topics() -> list[str]:
    """What it can answer about, so a UI can offer them rather than leaving
    somebody guessing at a blank box."""
    return sorted(TOPICS)


def _grounding() -> str:
    return "\n".join(f"- {answer}" for _keys, answer in TOPICS.values())


def ask(question: str, provider=None, mode: str = "text") -> dict:
    """Answer a question about using QRME. Never writes anything.

    Returns ``source`` so a caller can tell a written answer from a generated
    one, and ``ai`` so a surface can mark it — a generated sentence on a page
    full of disclosed synthetic profiles should not be the one unlabelled
    thing on it.
    """
    question = (question or "").strip()
    if not question:
        return {"answer": "Ask me anything about using QRME.",
                "source": "written", "ai": False, "refused": False,
                "disclosure": DISCLOSURE, "topics": topics()}

    # Before anything else, and before any model sees it: the questions that
    # ask this surface to be somebody.
    refusal = _match(question, REFUSALS)
    if refusal:
        return {"answer": refusal, "source": "written", "ai": False,
                "refused": True, "disclosure": DISCLOSURE, "topics": topics()}

    # "Show me around" is not a question with an answer — it is a request for
    # the walkthrough. Matched here rather than left as a topic, because the
    # help box is where somebody asks it and being handed a paragraph about
    # tours instead of a tour is the wrong reply.
    #
    # The assistant delivers it either way: `mode="voice"` renders the same
    # lesson for listening, so somebody driving or unable to read the screen
    # gets the tour rather than a link to it.
    if _match(question, _WALKTHROUGH) is not None:
        from . import tutorial
        first = tutorial.LESSONS[0]
        step = tutorial.say(first, mode)
        return {
            "answer": step.get("speak") or f"{step['title']}. {step['what']}",
            "source": "written", "ai": False, "refused": False,
            "disclosure": DISCLOSURE, "topics": topics(),
            "walkthrough": {"started": True, "step": step,
                            "steps": len(tutorial.LESSONS),
                            "next": "/tutorial/done"},
        }

    # "Where do I change my background." Matched before TOPICS and before any
    # model, because both would answer it with a description of backgrounds —
    # a correct paragraph about a thing, handed to somebody who was asking
    # where it lives. Directions are cheap and the model cannot know the screen
    # numbers.
    directions = where_is(question)
    if directions is not None:
        return {"answer": directions["say"], "source": "written", "ai": False,
                "refused": False, "disclosure": DISCLOSURE, "topics": topics(),
                "directions": directions}

    written = _match(question, TOPICS)

    if provider is None and _model_is_real():
        try:
            provider = llm.get_provider()
        except Exception:
            provider = None

    if provider is not None:
        try:
            reply = provider.generate(
                "You are the help box for QRME, a platform for AI synthetic "
                "profiles. Answer only about how QRME works, in at most three "
                "plain sentences. You are not a character and have no persona, "
                "name or memory; if asked to be one, say so and point at the "
                "profile on the page. Never invent a feature. Use only these "
                "facts:\n" + _grounding(),
                [{"role": "user", "content": question}])
            if reply and reply.strip():
                return {"answer": reply.strip(), "source": "model", "ai": True,
                        "refused": False, "disclosure": DISCLOSURE,
                        "topics": topics()}
        except Exception:
            pass          # a provider outage is not a reason to stop helping

    return {
        "answer": written or (
            "I can only help with using QRME — profiles, beacons, memory, "
            "desks, reviews and the age gate. Ask about one of those, or the "
            "profile on this page can answer for itself."),
        "source": "written", "ai": False, "refused": False,
        "disclosure": DISCLOSURE, "topics": topics(),
    }
