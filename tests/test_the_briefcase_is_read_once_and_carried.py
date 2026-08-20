"""What you hand a profile, read once and kept.

The link-in-a-turn reader worked and evaporated: the page reached that turn's
prompt and nothing else, so discussing the page meant pasting it again and
paying for it again. These tests hold the two halves that fixed it — that the
material survives the turn, and that what survives is the digest rather than
the document.

    asked     can the profile read what you hand it
    mattered  can it still remember it on the next turn
"""

from __future__ import annotations

import io
import zipfile

import pytest

from qrme import briefcase


# --------------------------------------------------------------------------- #
# Reading the bytes
# --------------------------------------------------------------------------- #

def test_plain_text_is_read():
    kind, text, was_read = briefcase.read_file(b"Patent one covers the "
                                               b"beacon.", "notes.txt")
    assert (kind, was_read) == ("document", True)
    assert "beacon" in text


def test_a_photograph_is_imported_and_not_claimed_as_read():
    """A one-pixel PNG. This deployment has no eyes; the item still lands,
    and ``read`` says plainly that nobody looked at it."""
    png = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
           b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
           + b"\x00" * 20)
    kind, text, was_read = briefcase.read_file(png, "me.png")
    assert (kind, text, was_read) == ("photo", "", False)


def test_a_docx_gives_up_its_words():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr(
            "word/document.xml",
            "<w:document><w:body><w:p><w:r><w:t>Claim 1: a synthetic "
            "profile</w:t></w:r></w:p></w:body></w:document>")
    kind, text, was_read = briefcase.read_file(buf.getvalue(), "filing.docx")
    assert (kind, was_read) == ("document", True)
    assert "synthetic profile" in text


def test_an_unknown_archive_is_listed_not_invented():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("a.bin", b"\x00\x01")
        archive.writestr("b.bin", b"\x02\x03")
    _, text, was_read = briefcase.read_file(buf.getvalue(), "bundle.zip")
    assert was_read and "2 file(s)" in text and "a.bin" in text


def test_a_pdf_with_no_text_layer_is_not_read():
    """A scan is pixels. Reporting it as read would put a profile in front of
    a document it cannot see, which is the failure this flag exists for."""
    _, text, was_read = briefcase.read_file(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
                                            + b"\x00" * 200, "scan.pdf")
    assert (text, was_read) == ("", False)


# --------------------------------------------------------------------------- #
# The distillation — the whole credit argument
# --------------------------------------------------------------------------- #

class _CountingProvider:
    """Records every call, so a test can prove how many times a document was
    actually sent anywhere."""

    def __init__(self, reply: str = "A briefing about two patents."):
        self.calls: list[str] = []
        self.reply = reply

    def generate(self, system: str, messages: list[dict]) -> str:
        self.calls.append(messages[-1]["content"])
        return self.reply


def test_a_short_text_is_its_own_digest():
    assert briefcase.distill("Short enough.", "t", _CountingProvider()) == \
        "Short enough."


def test_a_long_text_is_distilled_once_and_the_digest_is_small():
    provider = _CountingProvider()
    long_text = "The beacon patent. " * 400
    digest = briefcase.distill(long_text, "Patents", provider)
    assert len(provider.calls) == 1
    assert len(digest) <= briefcase.MAX_DIGEST < len(long_text)


def test_a_provider_that_errors_falls_back_to_the_head_of_the_text():
    class Broken:
        def generate(self, system, messages):
            raise RuntimeError("no key")

    digest = briefcase.distill("x" * 5000, "t", Broken())
    assert digest.endswith("…") and len(digest) <= briefcase.MAX_DIGEST + 1


def test_the_stub_never_becomes_a_digest():
    """The stub explains itself rather than performing a character. Stored as
    a reading it would put a sentence about our software into the prompt under
    somebody's document title, and report its length as theirs."""
    from qrme import llm

    body = "The beacon patent. " * 400
    digest = briefcase.distill(body, "Patents", llm.StubProvider())
    assert digest == body[:briefcase.MAX_DIGEST].rstrip() + "…"


def test_a_provider_that_degrades_to_the_fallback_is_not_believed():
    """`FallbackProvider` swallows the failure and answers with the stub. The
    caller sees a perfectly ordinary string; only `answered_by` says who
    wrote it."""
    from qrme import llm

    class Broken:
        def generate(self, system, messages):
            raise RuntimeError("expired key")

    provider = llm.FallbackProvider("anthropic", Broken(), llm.StubProvider())
    body = "The beacon patent. " * 400
    assert briefcase.distill(body, "Patents", provider) == \
        body[:briefcase.MAX_DIGEST].rstrip() + "…"


# --------------------------------------------------------------------------- #
# Whose material it is
# --------------------------------------------------------------------------- #

def _import_text(client, profile_id, interactor_id, body: bytes,
                 filename="notes.txt", **params):
    return client.post(
        f"/profiles/{profile_id}/briefcase/file",
        params={"interactor_id": interactor_id, "filename": filename,
                **params},
        content=body)


def test_an_imported_document_comes_back_on_the_list(
        client, profile_id, interactor_id):
    made = _import_text(client, profile_id, interactor_id,
                        b"US 2025/0246290 A1 covers the guardian.")
    assert made.status_code == 201, made.text
    listed = client.get(f"/profiles/{profile_id}/briefcase",
                        params={"interactor_id": interactor_id})
    assert listed.status_code == 200
    items = listed.json()["items"]
    assert [i["id"] for i in items] == [made.json()["id"]]
    assert items[0]["read"] is True


def test_the_briefcase_belongs_to_the_pair_and_not_to_the_profile(
        client, profile_id, interactor_id):
    """The next visitor does not inherit the last one's papers."""
    _import_text(client, profile_id, interactor_id, b"My medical history.")
    other = client.post("/interactors",
                        json={"display_name": "Rae",
                              "birthdate": "1990-02-02"}).json()["id"]
    listed = client.get(f"/profiles/{profile_id}/briefcase",
                        params={"interactor_id": other})
    assert listed.json()["items"] == []


def test_the_full_text_is_readable_on_its_own_door(
        client, profile_id, interactor_id):
    made = _import_text(client, profile_id, interactor_id,
                        b"The exact wording of claim 1.")
    got = client.get(f"/profiles/{profile_id}/briefcase/{made.json()['id']}",
                     params={"interactor_id": interactor_id})
    assert got.status_code == 200
    assert "claim 1" in got.json()["text"]


def test_taking_it_back_removes_it(client, profile_id, interactor_id):
    made = _import_text(client, profile_id, interactor_id, b"Take this back.")
    item_id = made.json()["id"]
    gone = client.delete(f"/profiles/{profile_id}/briefcase/{item_id}",
                         params={"interactor_id": interactor_id})
    assert gone.status_code == 204
    again = client.delete(f"/profiles/{profile_id}/briefcase/{item_id}",
                          params={"interactor_id": interactor_id})
    assert again.status_code == 404


def test_a_departed_profile_takes_nothing_new(
        client, profile_id, interactor_id):
    """Importing is not a passive store — the distillation runs the profile's
    own provider. A memorial is frozen and must not be reading on somebody's
    behalf."""
    from qrme import db

    conn = db.connect()
    conn.execute("UPDATE profiles SET status='departed' WHERE id=?",
                 (profile_id,))
    conn.commit()
    handed = _import_text(client, profile_id, interactor_id, b"read this")
    assert handed.status_code == 410, handed.text
    linked = client.post(f"/profiles/{profile_id}/briefcase/link",
                         json={"interactor_id": interactor_id,
                               "url": "https://example.test/x"})
    assert linked.status_code == 410


def test_a_memorial_still_hands_back_what_you_gave_it(
        client, profile_id, interactor_id):
    """The other half. Reading the briefcase and emptying it stay open in
    every status, for the same reason a departed profile's memory remains
    viewable — what you handed over is yours, and a memorial must not be a
    place your documents are stuck in."""
    from qrme import db

    made = _import_text(client, profile_id, interactor_id, b"my filing")
    item_id = made.json()["id"]
    conn = db.connect()
    conn.execute("UPDATE profiles SET status='departed' WHERE id=?",
                 (profile_id,))
    conn.commit()
    listed = client.get(f"/profiles/{profile_id}/briefcase",
                        params={"interactor_id": interactor_id})
    assert listed.status_code == 200 and len(listed.json()["items"]) == 1
    read = client.get(f"/profiles/{profile_id}/briefcase/{item_id}",
                      params={"interactor_id": interactor_id})
    assert read.status_code == 200 and "filing" in read.json()["text"]
    gone = client.delete(f"/profiles/{profile_id}/briefcase/{item_id}",
                         params={"interactor_id": interactor_id})
    assert gone.status_code == 204


def test_an_empty_upload_is_refused(client, profile_id, interactor_id):
    assert _import_text(client, profile_id, interactor_id,
                        b"").status_code == 422


def test_a_link_that_is_not_a_link_is_refused(
        client, profile_id, interactor_id):
    made = client.post(f"/profiles/{profile_id}/briefcase/link",
                       json={"interactor_id": interactor_id,
                             "url": "ftp://files.example"})
    assert made.status_code == 422


# --------------------------------------------------------------------------- #
# What the prompt carries
# --------------------------------------------------------------------------- #

def test_the_block_carries_the_digest_and_not_the_document(
        client, profile_id, interactor_id):
    long_text = ("The beacon patent describes a QR sticker. " * 300).encode()
    _import_text(client, profile_id, interactor_id, long_text,
                 filename="patents.txt")
    block = briefcase.block(profile_id, interactor_id)
    assert block is not None
    assert len(block) < len(long_text) / 4


def test_an_unread_item_is_carried_as_unread(
        client, profile_id, interactor_id):
    png = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
           b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
           + b"\x00" * 20)
    _import_text(client, profile_id, interactor_id, png, filename="lab.png",
                 note="my lab results")
    block = briefcase.block(profile_id, interactor_id)
    assert "could not open" in block
    assert "my lab results" in block
    assert "Do not describe or summarise" in block


def test_an_empty_briefcase_adds_nothing_to_the_prompt(
        client, profile_id, interactor_id):
    assert briefcase.block(profile_id, interactor_id) is None


def test_a_conversation_will_not_carry_material_without_bound(
        client, profile_id, interactor_id):
    for _ in range(briefcase.MAX_ITEMS):
        assert _import_text(client, profile_id, interactor_id,
                            b"one more").status_code == 201
    over = _import_text(client, profile_id, interactor_id, b"one too many")
    assert over.status_code == 422
    assert str(briefcase.MAX_ITEMS) in over.json()["detail"]


def test_an_imported_link_is_not_also_fetched_inline_on_the_same_turn(
        client, profile_id, interactor_id, monkeypatch):
    """Pasting the link you just imported must not pay for the page twice."""
    url = "https://example.test/patents"
    monkeypatch.setattr(briefcase, "read_link",
                        lambda u, on_behalf_of=None:
                            ("A page about two patents.", True, "Patents"))
    made = client.post(f"/profiles/{profile_id}/briefcase/link",
                       json={"interactor_id": interactor_id, "url": url})
    assert made.status_code == 201, made.text
    assert briefcase.holds_link(profile_id, interactor_id,
                                f"have a look at {url} again")
    assert not briefcase.holds_link(profile_id, interactor_id,
                                    "https://example.test/other")


def test_the_profile_answers_with_the_material_still_in_hand(
        client, profile_id, interactor_id):
    """The turn after the import — the one that used to have nothing."""
    _import_text(client, profile_id, interactor_id,
                 b"Patent US 2025/0246290 A1 covers the guardian loop.",
                 filename="patents.txt")
    said = client.post(f"/profiles/{profile_id}/chat",
                       json={"interactor_id": interactor_id,
                             "message": "tell me about my patents"})
    assert said.status_code == 200, said.text
    # The stub does not perform a character, so the observable claim is the
    # prompt itself: the block is there for the turn that follows the import.
    assert "0246290" in briefcase.block(profile_id, interactor_id)


def test_a_link_is_read_with_the_deployments_eyes(
        client, profile_id, interactor_id, monkeypatch):
    """With a renderer deployed, the read-once reading is the rendered page
    — what a person meets — not the shell the server sends. This is the
    'read once — 12 characters' failure, closed: the demonstration was a
    console whose whole surface hid behind scripts a plain fetch never ran."""
    from qrme import scrape
    monkeypatch.setattr(
        scrape, "fetch_rendered",
        lambda url, on_behalf_of=None: {
            "title": "JIM Guardian",
            "text": "Live monitoring · baseline 66 · all calm · 3 lookouts"})

    def never(url, on_behalf_of=None):
        raise AssertionError("the plain fetch must not run when eyes read")
    monkeypatch.setattr(scrape, "fetch", never)
    text, was_read, title = briefcase.read_link(
        "https://jim-mini.example/app/", "prf_x")
    assert was_read is True and title == "JIM Guardian"
    assert "Live monitoring" in text and len(text) > 12


def test_without_eyes_the_plain_reading_stands_in(
        client, profile_id, interactor_id, monkeypatch):
    """No renderer on this deployment: fetch_rendered answers None and the
    plain fetch carries what it can — the old behavior, kept honestly."""
    from qrme import scrape
    monkeypatch.setattr(scrape, "fetch_rendered",
                        lambda url, on_behalf_of=None: None)
    monkeypatch.setattr(
        scrape, "fetch",
        lambda url, on_behalf_of=None:
            "<html><head><title>JIM Guardian</title></head><body></body></html>")
    text, was_read, title = briefcase.read_link(
        "https://jim-mini.example/app/", "prf_x")
    assert title == "JIM Guardian"
