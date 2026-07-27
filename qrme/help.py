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
