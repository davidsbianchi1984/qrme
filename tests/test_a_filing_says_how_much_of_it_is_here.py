"""A document that was cut says so.

    asked     did the document read
    mattered  how much of it did

The cap is real and wanted — a briefcase is not an archive, and the module's
whole economy rests on a long filing being paid for once and carried as a
digest thereafter. What it was not was visible.

`_clean` tidied and cut on the same line, so every reader had already thrown
the number away before anybody could ask for it. A 70,000-character patent
application became 20,000 characters, the item said **read**, and the count
shown beside it was the KEPT length rather than the document's. Nothing
anywhere said that two thirds had gone.

That is the *held, not read* problem wearing better clothes. The profile is
not refusing — it is answering, confidently, about claim 14 from material it
never saw, because nothing told it the document stopped. And a person reading
"read once — 20,000 characters" has no way to know their filing was three
times that.

So the cut moved to where its cost can be written down beside it, and both
doors say it: the pair's briefcase and a room share, which are the same
reader and were the same silence.
"""

from __future__ import annotations

import re

import pytest

from qrme.briefcase import MAX_TEXT, add, block, capped

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)

#: Long enough that the cap bites, DERIVED from the cap rather than written
#: as a number: a constant that has to be edited every time the ceiling moves
#: is a test that silently stops exercising the thing it is named for. This
#: one is always half again longer than whatever the cap is.
_SENTENCE = "Claim 1. A method of regulating thermal transfer. "
FILING = _SENTENCE * (int(MAX_TEXT * 1.5 // len(_SENTENCE)) + 1)
SHORT = "A one-page note about the sealed enclosure and its two conduits."


def test_the_cap_still_caps():
    """The first thing to prove, because the rest is about reporting a cut
    that has to actually happen."""
    assert len(FILING) > MAX_TEXT
    assert len(capped(FILING)) == MAX_TEXT
    assert capped(SHORT) == SHORT


def test_tidying_no_longer_cuts():
    """The two were one line, and that is why the number was unavailable:
    every reader in this module ends in `_clean`, so the length was gone
    before any caller could record it."""
    from qrme.briefcase import _clean

    # Compared against the TIDIED length, not the raw one: stripping a
    # trailing space is tidying and always was. The claim is that nothing is
    # cut, not that nothing is touched.
    assert len(_clean(FILING)) == len(FILING.strip()), (
        "_clean is cutting again, so the document's own length is thrown "
        "away before anything can report it"
    )


def test_an_item_carries_the_documents_own_length(client):
    item = add("p1", "i1", kind="document", title="US 2025 0265659 A1",
               text=FILING, read=True)
    assert item["chars"] == MAX_TEXT
    assert item["full_chars"] == len(FILING.strip())


def test_a_whole_document_reports_no_loss(client):
    """`full_chars` is a truncation notice. On an item that fits, it would be
    a notice about nothing — shown on every short document forever."""
    item = add("p1", "i1", kind="document", title="Short note",
               text=SHORT, read=True)
    assert item["chars"] == len(SHORT)
    assert item["full_chars"] is None


def test_the_profile_is_told_it_holds_a_part(client):
    """Read at the prompt, because a column nothing shows the model is a
    fact that changes nothing — the same lesson the interrupted turn taught
    two rounds ago."""
    add("p1", "i1", kind="document", title="US 2025 0265659 A1",
        text=FILING, read=True)
    said = block("p1", "i1") or ""
    assert "only the first" in said
    assert f"{MAX_TEXT:,}" in said
    assert f"{len(FILING.strip()):,}" in said
    assert "must not answer as though you had" in said, (
        "the prompt says the document was cut and not what to do about it, "
        "which leaves the model free to answer as if it had the whole"
    )


def test_a_document_that_fits_says_nothing_about_being_cut(client):
    add("p1", "i1", kind="document", title="Short note", text=SHORT,
        read=True)
    assert "only the first" not in (block("p1", "i1") or "")


# -- and the room, which is the same reader and was the same silence -------

def test_a_room_share_says_how_much_of_it_is_here(client, monkeypatch):
    from qrme.routers import community

    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": user},
        {"kind": "profile", "id": dana["id"]}]}).json()["id"]

    posted = client.post(
        f"/rooms/{room}/share?interactor_id={user}"
        "&filename=US 2025 0265659 A1.txt&caption=have a look",
        headers=as_interactor(user), content=FILING.encode())
    assert posted.status_code in (200, 201), posted.text

    seen: list = []

    class Provider:
        def generate(self, system, turns):
            seen.append(turns)
            return "Noted."

    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: Provider())
    advanced = client.post(f"/rooms/{room}/advance",
                           headers=as_interactor(user))
    assert advanced.status_code in (200, 201), advanced.text
    assert seen, "no profile turn was taken"
    handed = " ".join(t["content"] for t in seen[-1])
    assert "only the first" in handed, (
        "a filing shared into a room is cut with nothing saying so — the "
        "briefcase gained the notice and the room did not"
    )
    assert f"{len(FILING.strip()):,}" in handed


def test_a_short_share_says_nothing_about_being_cut(client, monkeypatch):
    from qrme.routers import community

    user = make_interactor(client, "Sam", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": user},
        {"kind": "profile", "id": dana["id"]}]}).json()["id"]
    client.post(
        f"/rooms/{room}/share?interactor_id={user}&filename=note.txt",
        headers=as_interactor(user), content=SHORT.encode())

    seen: list = []

    class Provider:
        def generate(self, system, turns):
            seen.append(turns)
            return "Noted."

    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: Provider())
    client.post(f"/rooms/{room}/advance", headers=as_interactor(user))
    handed = " ".join(t["content"] for t in seen[-1]) if seen else ""
    assert "only the first" not in handed


def test_the_room_does_not_keep_a_whole_filing_in_a_transcript_row(client):
    """`_clean` no longer cuts, so a share that stored the reader's output
    raw would put seventy thousand characters in a message row. The cap
    moved; it did not go away."""
    from qrme.routers.community import _read_share

    words, digest, why, whole = _read_share(FILING.encode(), "filing.txt",
                                            None)
    assert len(words) == MAX_TEXT
    assert whole == len(FILING.strip())
    assert not why


# -- and on both screens, where the person who uploaded it is looking ------
#
# The profile being told is half of it. A person reading "read once — 20,000
# characters" beside a filing three times that length has been handed the
# kept length wearing the document's name, and nothing on screen distinguishes
# the two. Both surfaces say it now: the briefcase panel and the room's
# attachment line.

from pathlib import Path  # noqa: E402

CONSOLE = Path(__file__).resolve().parents[1] / "app" / "src"
BRIEFCASE_TSX = (CONSOLE / "Briefcase.tsx").read_text(encoding="utf-8")
INSIDE_TSX = (CONSOLE / "screens" / "Inside.tsx").read_text(encoding="utf-8")
L10N = (CONSOLE / "l10n.ts").read_text(encoding="utf-8")


def _looked_up(source: str) -> set[str]:
    return set(re.findall(r'tr\("([a-z.]+\.part(?:\.why)?)"', source))


def test_both_screens_say_it_when_a_document_was_cut():
    """One surface saying it is the failure this round has now caught four
    times: a fix that reaches one of two paths looks exactly like a fix."""
    assert "prf.bc.part" in _looked_up(BRIEFCASE_TSX), (
        "the briefcase panel still prints the kept length as the document's"
    )
    assert "ins.file.part" in _looked_up(INSIDE_TSX), (
        "the room's attachment line still prints the kept length as the "
        "document's"
    )
    for key in ("prf.bc.part", "prf.bc.part.why", "ins.file.part"):
        assert f'"{key}"' in L10N, key


def test_a_whole_document_still_reads_as_whole_on_both():
    """The old wording has to survive, or every short note acquires a
    truncation notice about nothing."""
    for source, key in ((BRIEFCASE_TSX, "prf.bc.read"),
                        (INSIDE_TSX, "ins.file.read")):
        assert f'tr("{key}", lang)' in source, key


def test_the_kept_length_comes_from_the_server():
    """The cap is a server constant. A console that hard-coded it would
    print a stale number the day it moves, and the number is the whole
    content of the sentence."""
    assert "m.media.chars" in INSIDE_TSX, (
        "the room derives the kept length instead of reading it"
    )
    from qrme.routers.community import _media_brief

    assert "kept" in _media_brief.__code__.co_varnames


def test_the_room_puts_both_numbers_on_the_wire(client):
    from tests.test_capabilities import as_interactor  # noqa: F811

    user = make_interactor(client, "Ada", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": user},
        {"kind": "profile", "id": dana["id"]}]}).json()["id"]
    posted = client.post(
        f"/rooms/{room}/share?interactor_id={user}&filename=filing.txt",
        headers=as_interactor(user), content=FILING.encode())
    media = posted.json()["shared"]["media"]
    assert media["chars"] == MAX_TEXT
    assert media["full_chars"] == len(FILING.strip())

    # And on a reload, not only in the reply to the share.
    seen = client.get(f"/rooms/{room}/messages",
                      headers=as_interactor(user)).json()
    last = [m["media"] for m in seen if m.get("media")][-1]
    assert last["chars"] == MAX_TEXT and last["full_chars"] == len(FILING.strip())
