"""The upload hears.

`read_file` told a handed-over video "this deployment holds the bytes
and cannot turn them into words" — true when it was written, untrue
since the stack grew ears. The video branch now asks the ears' bytes
door (`scrape.transcribe_bytes`), and the item carries the words said
in the recording; without ears the old posture stands unchanged — held,
said so, never invented.

    asked     what does this recording say
    mattered  the words said in it — heard at home, or honestly "held"

A voice memo rides the same branch: an .m4a opens with the same `ftyp`
box an .mp4 does and sniffs as video. And these are ears, not eyes —
the picture in the frames stays undescribed either way, exactly as a
photograph does.
"""

from __future__ import annotations

from qrme import briefcase, scrape

_MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 48


def _never_bytes(data, on_behalf_of=None):
    raise AssertionError("the ears must not run for this upload")


def test_a_video_upload_reads_as_the_words_said(monkeypatch):
    monkeypatch.setattr(
        scrape, "transcribe_bytes",
        lambda data, on_behalf_of=None: {"text": "The vault held through the restore drill.",
                      "duration_seconds": 9.0, "language": "en"})
    kind, text, was_read = briefcase.read_file(_MP4, "briefing.mp4")
    assert (kind, was_read) == ("video", True)
    assert "restore drill" in text


def test_without_ears_the_video_keeps_the_honest_posture(monkeypatch):
    monkeypatch.setattr(scrape, "transcribe_bytes", lambda data, on_behalf_of=None: None)
    kind, text, was_read = briefcase.read_file(_MP4, "briefing.mp4")
    assert (kind, text, was_read) == ("video", "", False)


def test_a_photograph_never_reaches_the_ears(monkeypatch):
    """Ears, not eyes: the image branch answers before any transcriber,
    and a photo stays imported-not-read."""
    monkeypatch.setattr(scrape, "transcribe_bytes", _never_bytes)
    png = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
           b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
           + b"\x00" * 20)
    kind, text, was_read = briefcase.read_file(png, "me.png")
    assert (kind, text, was_read) == ("photo", "", False)


def test_missing_ears_answer_none_before_anything_moves(monkeypatch):
    monkeypatch.delenv("QRME_EARS_URL", raising=False)
    assert scrape.transcribe_bytes(_MP4) is None
    assert scrape.transcribe_bytes(b"") is None


def test_a_heard_upload_lands_read_on_the_pairs_list(client, profile_id,
                                                     interactor_id,
                                                     monkeypatch):
    """The route-level account: the item arrives on the pair's list with
    the words and `read: true` — the same shape a document takes."""
    monkeypatch.setattr(
        scrape, "transcribe_bytes",
        lambda data, on_behalf_of=None: {"text": "Two lookouts standing, one letter waiting.",
                      "duration_seconds": 5.5, "language": "en"})
    made = client.post(
        f"/profiles/{profile_id}/briefcase/file",
        params={"interactor_id": interactor_id, "filename": "memo.m4a"},
        content=_MP4)
    assert made.status_code == 201, made.text
    listed = client.get(f"/profiles/{profile_id}/briefcase",
                        params={"interactor_id": interactor_id}).json()
    item = listed["items"][0]
    assert item["read"] is True and item["kind"] == "video"
