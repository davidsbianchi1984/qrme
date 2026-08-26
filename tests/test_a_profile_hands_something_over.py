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


# -- the shape that was asked for --------------------------------------------
#
# "Let's let the synthetic profiles generate PDFs." The fence title is the
# one channel the profile already has, so the shape rides there: a title
# ending .pdf arrives as a real PDF from the built-in writer; .txt as plain
# text; everything else stays Markdown, the shape every language fits.

def test_a_pdf_when_a_pdf_was_asked_for():
    data, name = composing.render(
        {"title": "Audit plan.pdf", "body": "One page.\nTwo lines."})
    assert name == "Audit plan.pdf"
    assert data.startswith(b"%PDF-"), "the .pdf that arrived is not a PDF"


def test_the_estate_can_read_its_own_hand():
    """The writer proven by the reader that has parsed PDFs since 1.0.0 —
    if briefcase cannot read the page we wrote, nobody's viewer is likely
    to either."""
    from qrme import briefcase

    body = ("The plan\n\n" + "\n".join(
        f"Step {i}: measure, publish, repeat." for i in range(1, 60)))
    data, name = composing.render({"title": "Plan.pdf", "body": body})
    kind, text, read = briefcase.read_file(data, name, None)
    assert read, "our own reader could not read our own PDF"
    assert "Step 1:" in text
    assert "Step 59:" in text, "the second page was written and lost"


def test_a_script_helvetica_cannot_carry_arrives_as_markdown():
    """The honest limit, honestly taken: standard Type-1 Helvetica stops
    at Latin-1, and a page of substitution marks is worse than the right
    words in the wrong costume."""
    data, name = composing.render(
        {"title": "计划.pdf", "body": "三个产品一起前进。"})
    assert name.endswith(".md"), "a PDF was promised for a script it cannot hold"
    assert "三个产品" in data.decode("utf-8"), "the words did not survive"


def test_plain_text_when_plain_text_was_asked_for():
    data, name = composing.render({"title": "notes.TXT", "body": "plain"})
    assert name == "notes.txt"
    assert data == b"plain"


def test_the_profile_is_told_about_the_shapes():
    assert ".pdf" in composing.GUIDANCE, (
        "a shape nobody is told about is a shape nobody asks for")


# -- the same hand, in a room ------------------------------------------------
#
# The guidance has ridden every room prompt since the composing round —
# build_system_prompt appends it unconditionally — but the room never made
# the split. A profile that took the offer had its whole fence land raw in
# the transcript: the document as a wall of chat, with the markers showing.

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: E402,F401
                                     make_profile)


def _doc_room(client, monkeypatch, provider):
    from qrme.routers import community
    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: provider)
    user = make_interactor(client, "Theo", "1990-01-01")
    made = make_profile(client)
    room = client.post("/rooms", json={
        "topic": "the audit", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": made["id"]}]}).json()
    return user, room


def test_a_room_turn_hands_the_document_over(client, monkeypatch):
    user, room = _doc_room(client, monkeypatch, Composing())
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"message": "prepare me a summary",
                          "sender_id": user})
    assert r.status_code == 201, r.text
    turn = r.json()["replies"][0]
    assert "```" not in (turn["content"] or ""), (
        "the fence landed raw in the room transcript")
    assert turn["media"], "the profile composed and the room got no file"
    assert turn["media"]["name"] == "Quarterly summary.md"
    assert turn["media"]["read"] is True, (
        "the other profiles in this room cannot read the handed document")


def test_the_room_document_is_marked(client, monkeypatch):
    user, room = _doc_room(client, monkeypatch, Composing())
    client.post(f"/rooms/{room['id']}/messages", headers=as_interactor(user),
                json={"message": "write it up", "sender_id": user})
    row = db.connect().execute(
        "SELECT media_id FROM room_messages WHERE room_id=?"
        " AND sender_kind='profile' AND media_id IS NOT NULL",
        (room["id"],)).fetchone()
    assert row, "no document row landed"
    marked = db.connect().execute(
        "SELECT ai_marked FROM media WHERE id=?",
        (row["media_id"],)).fetchone()
    assert marked["ai_marked"] == 1, (
        "a document a profile composed is synthetic media and must say so")


def test_a_wordless_room_handover_still_gets_a_sentence(client, monkeypatch):
    user, room = _doc_room(client, monkeypatch, Composing(said=""))
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"message": "prepare me a summary",
                          "sender_id": user})
    turn = r.json()["replies"][0]
    assert turn["content"], "the page was handed over without a word"
    assert "```" not in turn["content"]
    assert turn["media"]


# -- the stuttered fence -----------------------------------------------------
#
# Field transcript, from a room: the model lost the thread mid-document and
# started the fence again, twice — one turn, three overlapping drafts, each
# a longer prefix of the page it was trying to write. First-match filing
# handed over the most truncated attempt and left the retries raw.

def test_a_stuttered_fence_hands_over_the_furthest_attempt():
    reply = ("Here's the page — hand it straight to them.\n\n"
             "```document: Staleness Contract\n"
             "# Contract\n\n## Part 1\nTimestamp at the source.\n"
             "```document: Staleness Contract\n"
             "# Contract\n\n## Part 1\nTimestamp at the source.\n"
             "## Part 2\nDeclare a freshness window.\n"
             "```document: Staleness Contract\n"
             "# Contract\n\n## Part 1\nTimestamp at the source.\n"
             "## Part 2\nDeclare a freshness window.\n"
             "## Part 3\nSeparate the two silences.\n")
    spoken, doc = composing.split(reply)
    assert spoken == "Here's the page — hand it straight to them."
    assert "```" not in spoken, "a retry landed raw in the bubble"
    assert doc is not None
    assert "Part 3" in doc["body"], (
        "a shorter attempt was filed while the finished draft existed")


def test_prose_after_a_closed_fence_survives():
    spoken, doc = composing.split(
        "Before.\n\n```document: Notes\nBody.\n```\nAfter.")
    assert spoken == "Before.\n\nAfter."
    assert doc == {"title": "Notes", "body": "Body."}


def test_talking_about_the_fence_is_not_using_it():
    """The opener is anchored to the start of a line — a profile telling
    somebody how the fence works mid-sentence is describing it."""
    reply = "You'd write ```document: Title on its own line to hand one over."
    assert composing.split(reply) == (reply, None)
