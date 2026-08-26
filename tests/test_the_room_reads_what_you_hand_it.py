"""The room reads what you hand it.

Field report, and the profile said it itself, in a room where a PDF had
just landed:

    "I can see them land, but I can't read them from where I'm standing —
     I don't get to open attachments and pretend I've examined them."

Which was honest, and was the bug. `_worded` turned an attachment into
"[shared a file: Response 1.pdf]" and stopped there, so a profile in a
room with a document could name it and nothing else. Ask it to comment
and the only truthful answer was that it could not.

    asked     did the file arrive
    mattered  can the profiles in here read it

## Nothing new was invented

`briefcase.read_file` has read PDFs, the zip-family office documents,
plain text and — with ears deployed — recordings, since the one-to-one
conversation grew a briefcase. The room simply did not call it. This is
that call, plus the two consequences of making it: the reading rides into
the prompt, and the transcript says on the attachment itself whether
there was one.

## Whose reading it is

Deliberately **not** a briefcase row. A briefcase belongs to one pair and
the next visitor does not inherit it. This belongs to the room, where
everybody present is already looking at the file — which is a different
boundary, and the looser of the two only because the file was handed to
the room in the first place.

## The failure that must stay honest

A photograph, a scanned filing, a recording on a stack with no ears: held
and unreadable. The label says so in the prompt, and the transcript says
so on screen. Filling that hole with a guess is the one outcome worse
than the bug being fixed — a profile confidently summarising a document
nobody read is exactly the failure this estate exists to refuse.
"""

from __future__ import annotations

from pathlib import Path

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)

SRC = (Path(__file__).resolve().parents[1]
       / "qrme/routers/community.py").read_text(encoding="utf-8")

# A minimal honest PNG — pixels, and nothing a reader can turn into words.
PNG = (b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR"
       + b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
       + b"\x1f\x15\xc4\x89" + b"\x00" * 16)

NOTES = (
    "Quarterly response, prepared for the board.\n\n"
    "Revenue held flat against a falling market. The three open matters "
    "named in the last filing are each resolved or scheduled. Nothing in "
    "this document changes the guidance issued in March.\n"
).encode("utf-8")


def _room(client):
    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={
        "topic": "the filing", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": dana["id"]}]}).json()
    return user, room


def test_a_document_is_read_on_the_way_in(client):
    user, room = _room(client)
    mine = as_interactor(user)
    r = client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}"
        "&filename=response-1.txt",
        headers=mine, content=NOTES)
    assert r.status_code == 201, r.text
    assert r.json()["shared"]["media"]["read"] is True, (
        "a plain-text document landed unread")


def test_the_reading_is_kept_not_rederived(client):
    """Paid for once, the briefcase's own economy. The digest is on the
    row, so every later turn carries it without re-reading the file."""
    user, room = _room(client)
    client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}"
        "&filename=response-1.txt",
        headers=as_interactor(user), content=NOTES)
    from qrme import db

    row = db.connect().execute(
        "SELECT media_text, media_digest FROM room_messages"
        " WHERE room_id=? AND media_id IS NOT NULL", (room["id"],)).fetchone()
    assert row["media_text"], "the words were read and thrown away"
    assert row["media_digest"], "no reading was kept for the later turns"


def test_a_photograph_is_held_and_said_to_be_unread(client):
    """The honest half. Pixels are not words, and a profile told they are
    would describe a picture nobody looked at."""
    user, room = _room(client)
    r = client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}&filename=sunset.png",
        headers=as_interactor(user), content=PNG)
    assert r.status_code == 201, r.text
    assert r.json()["shared"]["media"]["read"] is False


def test_the_transcript_says_whether_it_was_read(client):
    """On the attachment, before the question is put — the person sharing
    should not have to ask a profile to find out."""
    user, room = _room(client)
    mine = as_interactor(user)
    client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}&filename=a.png",
        headers=mine, content=PNG)
    client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}&filename=b.txt",
        headers=mine, content=NOTES)
    seen = client.get(f"/rooms/{room['id']}/messages", headers=mine).json()
    marks = [m["media"]["read"] for m in seen if m["media"]]
    assert marks == [False, True]


def test_the_reading_reaches_the_prompt():
    """The whole point. A digest on a row that never enters the system
    prompt is a profile that still cannot discuss your document."""
    turns = SRC[SRC.index("def _profile_turns"):]
    turns = turns[:turns.index("\n@router")]
    assert "media_digest" in turns, (
        "the history query does not fetch the reading")
    assert "it reads:" in turns, (
        "the reading is never handed to the model")


def test_an_unreadable_file_is_labelled_unread_in_the_prompt():
    """Absence stated, never filled. This is the line between a profile
    that says it cannot see inside your scan and one that invents what is
    in it."""
    turns = SRC[SRC.index("def _profile_turns"):]
    turns = turns[:turns.index("\n@router")]
    assert "you have not read it" in turns


def test_the_room_reading_is_not_a_briefcase_row():
    """A briefcase belongs to one pair; the person next in line does not
    inherit your medical records. A room share is to the room."""
    fn = SRC[SRC.index("def _read_share"):]
    fn = fn[:fn.index("\ndef ")]
    assert "briefcase.add(" not in fn, (
        "a room share is being filed into one visitor's private briefcase")


def test_reading_never_costs_the_share(client):
    """The attachment is the deliverable; the reading is a bonus on top of
    it. A reader that throws must not take the file down with it."""
    fn = SRC[SRC.index("def _read_share"):]
    fn = fn[:fn.index("\ndef ")]
    assert fn.count("except Exception") >= 2, (
        "a failure to read would refuse a file that saved cleanly")


def test_the_profile_is_actually_handed_the_words(client, monkeypatch):
    """The claim, proven rather than pinned: take a real turn in a room
    where a document landed, and read what went to the model."""
    from qrme.routers import community

    seen: list = []

    class Provider:
        def generate(self, system, turns):
            seen.append(turns)
            return "Noted."

    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: Provider())
    user, room = _room(client)
    mine = as_interactor(user)
    client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}"
        "&filename=response-1.txt&caption=have a look",
        headers=mine, content=NOTES)
    r = client.post(f"/rooms/{room['id']}/advance", headers=mine)
    assert r.status_code in (200, 201), r.text
    assert seen, "no profile turn was taken"
    handed = " ".join(t["content"] for t in seen[-1])
    assert "response-1.txt" in handed
    assert "it reads:" in handed, (
        "the profile was told a file arrived and not what is in it")


# ---------------------------------------------------------------------------
# The handed link — the other thing a person hands a room.
#
# Field report, from a room, said by the profile itself: "Fifth link, same
# wall — I can't open any of them from this seat." The pair conversation has
# read handed links since the briefcase round; the room never made the call.
# Same discipline as the file above: read once at post time, kept on the row,
# said honestly when it could not be read.

PAGE = ("<html><head><title>The QRME estate</title>"
        '<meta name="description" content="Three products in lockstep.">'
        "</head><body>The estate ships QRME, JIM-mini and PDI together, "
        "and the beta is live.</body></html>")


def test_a_link_handed_to_the_room_is_read(client, monkeypatch):
    from qrme import scrape

    monkeypatch.setattr(scrape, "fetch", lambda url, on_behalf_of=None: PAGE)
    user, room = _room(client)
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"message": "Have a look at https://example.com/qrme",
                          "sender_id": user})
    assert r.status_code == 201, r.text
    from qrme import db

    row = db.connect().execute(
        "SELECT media_id, media_text, media_digest FROM room_messages"
        " WHERE room_id=? AND sender_kind='user'", (room["id"],)).fetchone()
    assert row["media_id"] is None, "a link is not an attachment"
    assert row["media_digest"], "the page was read and no reading was kept"


def test_the_link_reading_reaches_the_prompt(client, monkeypatch):
    """The whole point — the reading in the turn the model actually gets."""
    from qrme import scrape
    from qrme.routers import community

    monkeypatch.setattr(scrape, "fetch", lambda url, on_behalf_of=None: PAGE)
    seen: list = []

    class Provider:
        def generate(self, system, turns):
            seen.append(turns)
            return "Read it."

    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: Provider())
    user, room = _room(client)
    client.post(f"/rooms/{room['id']}/messages", headers=as_interactor(user),
                json={"message": "Thoughts on https://example.com/qrme ?",
                      "sender_id": user})
    assert seen, "no profile turn was taken"
    handed = " ".join(t["content"] for t in seen[-1])
    assert "the page was read — it says:" in handed, (
        "the profile was handed a link and not the page")


def test_an_unreached_link_is_said_to_be_unread(client, monkeypatch):
    """The honest half, again. A fetch that fails must reach the prompt as
    an absence, or the profile invents the page."""
    from qrme import scrape
    from qrme.routers import community

    def refuse(url, on_behalf_of=None):
        raise OSError("no route")

    monkeypatch.setattr(scrape, "fetch", refuse)
    seen: list = []

    class Provider:
        def generate(self, system, turns):
            seen.append(turns)
            return "I could not open it."

    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: Provider())
    user, room = _room(client)
    client.post(f"/rooms/{room['id']}/messages", headers=as_interactor(user),
                json={"message": "See https://example.com/gone",
                      "sender_id": user})
    assert seen, "no profile turn was taken"
    handed = " ".join(t["content"] for t in seen[-1])
    assert "could not be reached" in handed
    assert "never guess" in handed


def test_an_offline_deployment_does_not_fetch(client, monkeypatch):
    """The same switch every outbound path honours. A vault that promises
    nothing leaves this machine cannot open a socket because somebody
    pasted a URL into a room."""
    from qrme import offline, scrape

    def trip(url, on_behalf_of=None):
        raise AssertionError("an offline deployment opened a socket")

    monkeypatch.setattr(offline, "enabled", lambda: True)
    monkeypatch.setattr(scrape, "fetch", trip)
    user, room = _room(client)
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"message": "See https://example.com/qrme",
                          "sender_id": user})
    assert r.status_code == 201, r.text
    from qrme import db

    row = db.connect().execute(
        "SELECT media_why FROM room_messages WHERE room_id=?"
        " AND sender_kind='user'", (room["id"],)).fetchone()
    assert row["media_why"] == "offline"


def test_reading_never_costs_the_message():
    """The message is the deliverable; the reading is a bonus on top of
    it — the same sentence _read_share earned, owed here too."""
    fn = SRC[SRC.index("def _read_link"):]
    fn = fn[:fn.index("\ndef ")]
    assert "except Exception" in fn, (
        "a failure to read would refuse a message that said something")
    assert "offline.enabled()" in fn, (
        "the room's link fetch does not honour the offline switch")
