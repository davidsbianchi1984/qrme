"""A profile writes something down, and it arrives as a document.

Field report, three questions in one breath: *"I'm asking him to prepare me
a document. How was he supposed to send it, and how am I supposed to receive
it, and how does it render on the screen?"*

    asked     can a profile write something
    mattered  can it hand it over

It always could write. What it could not do was hand anything over — a
profile emits text into a bubble, so a report arrived as a wall of chat that
was gone up the scroll on the next turn. The reading half of this pipe has
existed since 1.0.0: hand a room a PDF and the profiles there discuss it.
This is the same pipe pointed the other way.

## The rule this is the mirror of

`media.py` says a person's own photograph is **never** AI-marked, because
stamping an authentic picture is a false statement in the direction the mark
exists to prevent. A document a profile composed is the opposite case — it
is synthetic outright — and it is marked at the moment it is made. The
`ai_marked` field has existed since media existed and was the literal
`False` in every path, because nothing in the product generated a file.
"""

from __future__ import annotations

import pytest

from qrme import composing, db, llm

from .test_the_profile_remembers_by_meaning import _chat


class Composing:
    """A provider that fences a document, as the guidance asks."""

    def __init__(self, title="Quarterly summary", body="# Q3\n\nRevenue up.",
                 said="Here is the summary you asked for."):
        self.title, self.body, self.said = title, body, said
        self.prompts: list[str] = []

    def generate(self, system, messages):
        self.prompts.append(system)
        fence = f"```document: {self.title}\n{self.body}\n```"
        return f"{self.said}\n\n{fence}" if self.said else fence


@pytest.fixture()
def speaks(monkeypatch):
    """Swap the profile's provider for one that fences a document.

    Patched at `llm.provider_for_profile` — the factory every generation
    site resolves through — rather than at an app attribute, which is what
    the rest of this suite does and the only thing the chat path reads.
    """
    def _use(provider):
        monkeypatch.setattr(llm, "provider_for_profile",
                            lambda *a, **k: provider)
        return provider
    return _use


# -- the split ---------------------------------------------------------------

def test_the_document_leaves_the_conversation_and_becomes_a_file():
    """The fence comes out of what is read.

    Leaving it in would put the whole document in the bubble *and* in the
    file — the exact failure this exists to fix, with an attachment added.
    """
    spoken, doc = composing.split(
        "Here you go.\n\n```document: Notes\n# Heading\n\nBody.\n```")
    assert spoken == "Here you go."
    assert doc == {"title": "Notes", "body": "# Heading\n\nBody."}


def test_an_ordinary_reply_is_left_alone():
    for plain in ("just talking",
                  "here is code:\n```python\nprint(1)\n```",
                  "```\nbare fence\n```"):
        assert composing.split(plain) == (plain, None), (
            "a fence that is not a document fence was taken as one — a "
            "profile quoting code hands over a file")


def test_an_empty_fence_is_a_stumble_not_a_document():
    """The fence still comes out: a person should never read one."""
    spoken, doc = composing.split("Here.\n\n```document: Nothing\n\n```")
    assert doc is None
    assert "```" not in spoken


def test_a_filename_survives_a_hostile_title():
    for title, want in [
        ("Quarterly summary", "Quarterly summary.md"),
        ("../../etc/passwd", "etcpasswd.md"),
        ("", "document.md"),
        ("...", "document.md"),
    ]:
        got = composing.filename(title)
        assert got == want, f"{title!r} -> {got!r}"
        assert "/" not in got and "\\" not in got


# -- the whole way through ---------------------------------------------------

def test_a_composed_document_arrives_as_a_marked_file(client, profile_id,
                                                      interactor_id, speaks):
    made = speaks(Composing())
    out = _chat(client, profile_id, interactor_id, "prepare me a summary")

    turn = out["profile_message"]
    assert turn["content"] == "Here is the summary you asked for.", (
        "the document was left in the chat bubble as well as being filed")
    doc = turn["document"]
    assert doc is not None, "the profile composed and nothing was handed over"
    assert doc["kind"] == "file"
    assert doc["name"] == "Quarterly summary.md"
    assert doc["ai_marked"] is True, (
        "a document a profile composed is synthetic media and must say so")

    row = db.connect().execute(
        "SELECT ai_marked FROM media WHERE id=?", (doc["id"],)).fetchone()
    assert row["ai_marked"] == 1
    assert made.prompts, "the provider was never asked"


def test_the_profile_is_told_it_may(client, profile_id, interactor_id,
                                    speaks):
    """A capability nobody is told about is a capability nobody uses."""
    made = speaks(Composing())
    _chat(client, profile_id, interactor_id, "hello")
    assert "```document:" in made.prompts[0], (
        "the prompt never mentions the fence, so a profile has no way to "
        "know it can hand anything over")


def test_a_document_with_no_words_around_it_still_gets_a_sentence(
        client, profile_id, interactor_id, speaks):
    """Handing somebody a page without a word is stranger than this product
    should be on its own."""
    speaks(Composing(said=""))
    out = _chat(client, profile_id, interactor_id, "prepare me a summary")
    turn = out["profile_message"]
    assert turn["content"], "the turn was handed over with nothing said"
    assert "```" not in turn["content"]
    assert turn["document"] is not None


def test_an_upload_is_not_marked(client, profile_id):
    """The other half of the rule, and the reason the default is False."""
    from qrme import media as media_mod
    saved = media_mod.save(profile_id, b"GIF89a" + b"\x00" * 32,
                           name="me.gif")
    assert saved["ai_marked"] is False
    row = db.connect().execute(
        "SELECT ai_marked FROM media WHERE id=?", (saved["id"],)).fetchone()
    assert row["ai_marked"] == 0, (
        "a person's own upload was stamped as synthetic — a false "
        "statement in the direction the mark exists to prevent")


def test_the_turn_carries_the_card_and_not_the_body(client, profile_id,
                                                    interactor_id, speaks):
    """A transcript is polled. A document in every poll is the document
    sent again, on every poll, forever."""
    body = "# Long\n\n" + ("filler paragraph. " * 500)
    speaks(Composing(body=body))
    out = _chat(client, profile_id, interactor_id, "write it up")
    turn = out["profile_message"]
    assert body not in str(turn), "the whole document rode the turn"
    assert turn["document"]["url"]
