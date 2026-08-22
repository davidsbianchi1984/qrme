"""A profile writes something down, and it arrives as a document.

Field report, and three questions in one breath: *"I'm asking him to prepare
me a document. How was he supposed to send it, and how am I supposed to
receive it, and how does it render on the screen? I need to tackle these for
when these profiles are capable of drafting and composing and sharing."*

    asked     can a profile write something
    mattered  can it hand it over

It always could write. What it could not do was *hand anything over*: a
profile emits text into a bubble and nothing else. Ask one for a report and
you got the report as a wall of chat — unsaveable, unopenable, gone up the
scroll on the next turn. The reading half of this pipe has existed since
1.0.0 (`briefcase.py`: hand a room a PDF and the profiles there discuss it).
This is the same pipe pointed the other way.

## Why a marker in the text rather than a tool call

The provider contract is `generate(system, messages) -> str`. One string
back, no tool-calling loop, and every bound provider in this product
implements exactly that — including the offline stub and the vault's
resident. Adding a tool channel would mean changing all of them, and
changing them for a feature whose entire payload is *text the model already
knows how to write*.

So the document rides the channel that exists. The profile is told it may
fence a composition; the fence is taken out of what the person reads and
becomes the file. A model that never uses the fence has lost nothing, and a
deployment whose provider is a stub still works.

## What is marked, and why this is the case the rule was waiting for

`media.py` states that a person's own photograph is **never** AI-marked,
because stamping an authentic picture is a false statement in the direction
the mark exists to prevent. The mirror of that rule is this: a document a
profile composed is synthetic media outright, and it is marked so at the
moment it is made. `ai_marked` has been a field in this API since media
existed and has been the constant `False` in every path, because until now
nothing in the product generated a file. It is a fact now.
"""

from __future__ import annotations

import re

#: The fence. Deliberately not a bare ``` block: a profile writing about
#: code, or quoting a file, produces those constantly and none of them are
#: a document being handed over. The opening line names the document, which
#: is also how it gets a filename somebody can find later.
_FENCE = re.compile(
    r"```document:[ \t]*(?P<title>[^\n]*)\n(?P<body>.*?)(?:\n```|\Z)",
    re.S)

#: A composition longer than this is a file that wants to be a book. The cap
#: is generous and exists so one runaway generation cannot fill a disk.
MAX_BODY = 200_000

#: What a document is called when the profile fenced one and named it
#: nothing. Not "untitled": the person asked for something, and the name of
#: the thing they asked for is the one fact the fence was supposed to carry.
FALLBACK_TITLE = "Document"


def split(reply: str) -> tuple[str, dict | None]:
    """Separate what the person reads from what they receive.

    Returns `(spoken, document)`. `document` is None when the profile wrote
    no fence, which is every ordinary turn.

    The fence comes out of the spoken text rather than being left in it.
    Leaving it would put the whole document in the chat bubble *and* in the
    file — which is the failure this exists to fix, with an attachment
    added to it.
    """
    if not reply:
        return reply, None
    found = _FENCE.search(reply)
    if not found:
        return reply, None
    body = found.group("body").strip()
    if not body:
        # A fence with nothing in it is a model stumble, not a document.
        # The fence still comes out — a person should never read one.
        return (reply[:found.start()] + reply[found.end():]).strip(), None
    title = (found.group("title") or "").strip()[:120] or FALLBACK_TITLE
    spoken = (reply[:found.start()] + reply[found.end():]).strip()
    return spoken, {"title": title, "body": body[:MAX_BODY]}


def filename(title: str) -> str:
    """A filename from a title, safe on every filesystem.

    The stored file is named by its media id regardless (see `media.save`);
    this is the name a person sees on the card and gets when they save it,
    so it is worth being the title they asked for rather than an id.
    """
    stem = re.sub(r"[^\w \-.]", "", title).strip().strip(".").strip()
    # Leading dots go with the trailing ones. `../../etc/passwd` loses its
    # slashes to the character class above and would otherwise arrive as
    # `....etcpasswd` — not a traversal any more, but a hidden file on unix
    # and a name nobody typed.
    stem = re.sub(r"\.{2,}", ".", stem).strip(".").strip() or "document"
    return f"{stem[:100]}.md"


#: What the profile is told, once, in the system prompt. Written as a
#: permission rather than an instruction: a profile that narrates its own
#: formatting rules at somebody is worse company than one that just talks.
GUIDANCE = (
    "If you are asked to prepare, draft, write up or put together something "
    "that is a document rather than a remark — a summary, a plan, a letter, "
    "a report, notes — you may hand it over as a file instead of pasting it "
    "into the conversation. Fence it like this:\n"
    "```document: A short title\n"
    "...the whole document, in Markdown...\n"
    "```\n"
    "Say a sentence outside the fence about what you have made, the way a "
    "person handing somebody a page would. Everything inside the fence "
    "becomes the file and is not shown in the conversation, so do not "
    "repeat it outside. Use this only when a document is genuinely what was "
    "wanted; ordinary answers stay ordinary answers."
)
