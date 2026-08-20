"""The briefcase hears.

A read-once link that *is* a recording used to fall to the plain fetch,
which decodes compressed media as mojibake and marks it read — a worse
account than saying nothing. The link goes to the stack's ears now
(`scrape.fetch_transcribed`), and what the interactor's item carries is
the words said in the recording.

    asked     what does this link say
    mattered  the words said in it — and "held, not read" when there
              are no ears, never junk marked read

Without ears there is no stand-in: unlike a page, where the shell the
server sends is still the page's own text, the bytes of a recording are
not its words. The item takes the same posture an uploaded video does —
held, said so — and the suffix list that decides what counts as a
recording lives in one place, shared with the lookout.
"""

from __future__ import annotations

import inspect

from qrme import briefcase, lookout, scrape


def _never(url, on_behalf_of=None):
    raise AssertionError(f"this fetcher must not run for {url}")


def test_a_recording_link_reads_as_the_words_said(monkeypatch):
    monkeypatch.setattr(
        scrape, "fetch_transcribed",
        lambda url, on_behalf_of=None: {
            "text": "The vault held through the restore drill.",
            "duration_seconds": 12.4, "language": "en"})
    monkeypatch.setattr(scrape, "fetch", _never)
    monkeypatch.setattr(scrape, "fetch_rendered", _never)
    text, was_read, title = briefcase.read_link(
        "https://cdn.example/briefing.mp4", "prf_x")
    assert was_read is True
    assert "restore drill" in text
    assert title is None


def test_without_ears_a_recording_is_held_not_read(monkeypatch):
    """The point of the round: no junk marked read. The plain fetch must
    not even run — decoded video bytes are not a reading."""
    monkeypatch.setattr(scrape, "fetch_transcribed",
                        lambda url, on_behalf_of=None: None)
    monkeypatch.setattr(scrape, "fetch", _never)
    monkeypatch.setattr(scrape, "fetch_rendered", _never)
    text, was_read, title = briefcase.read_link(
        "https://cdn.example/briefing.mp4", "prf_x")
    assert (text, was_read, title) == ("", False, None)


def test_a_page_link_still_reads_through_the_eyes(monkeypatch):
    monkeypatch.setattr(
        scrape, "fetch_rendered",
        lambda url, on_behalf_of=None: {"title": "JIM Guardian",
                                        "text": "Live monitoring · calm"})
    monkeypatch.setattr(scrape, "fetch_transcribed", _never)
    monkeypatch.setattr(scrape, "fetch", _never)
    text, was_read, title = briefcase.read_link(
        "https://jim-mini.example/app/", "prf_x")
    assert was_read is True and title == "JIM Guardian"
    assert "Live monitoring" in text


def test_missing_ears_answer_none_before_anything_leaves(monkeypatch):
    """No QRME_EARS_URL: fetch_transcribed answers None without opening a
    socket — the caller decides what honesty looks like."""
    monkeypatch.delenv("QRME_EARS_URL", raising=False)
    assert scrape.fetch_transcribed("https://cdn.example/a.mp4") is None


def test_the_two_doors_share_one_suffix_list():
    """A suffix taught to the briefcase is taught to the lookout — the
    list lives in scrape and the lookout delegates."""
    assert "scrape.is_recording" in inspect.getsource(lookout._is_recording)
    for url in ("https://cdn.example/a.mp3?session=b.html",
                "https://cdn.example/a.MP4"):
        assert scrape.is_recording(url) is True
        assert lookout._is_recording(url) is True
    assert scrape.is_recording("https://example.com/talks.html?v=a.mp4") \
        is False
