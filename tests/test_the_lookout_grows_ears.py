"""The lookout grows ears.

The vault's `fetch.listen` (PDI 0.94) seals the words said in a
recording. This round points the lookout twin at it: planting a URL
that *is* a recording — the media file itself, not a page containing a
player — stands a listening appointment instead of a rendering one,
under the same capture key and change-memory, so everything downstream
(the read-back, the changed_at, the chat prompt, the letter) reads a
transcript exactly the way it reads a page.

    asked     can a profile keep an ear on a recording
    mattered  the same lookout, hearing where hearing is what the URL is

Honesty carries over unchanged: a deployment without ears fails the
cycle in words, and the lookout's `trouble` line — fed by the vault's
runs ledger — says why. There is no silent stand-in for hearing.
"""

from __future__ import annotations

from qrme import db, letter, lookout

from tests.test_the_profile_keeps_itself_current import (StandingVault,
                                                         _allow_study,
                                                         _plant)


def test_a_recording_url_plants_a_listening_appointment(client, profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    out = _plant(client, profile_id, url="https://cdn.example/briefing.mp4")
    task = vault.standing[out["task_id"]]
    assert task["plan_steps"] == [
        {"tool": "fetch.listen",
         "args": {"url": "https://cdn.example/briefing.mp4"}}]


def test_the_suffix_is_read_from_the_path_not_the_query(client, profile_id):
    """`?session=a.html` after an .mp3 is still a recording; an .html
    page that merely mentions media in its query is still a page."""
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    heard = _plant(client, profile_id,
                   url="https://cdn.example/town-hall.mp3?session=a.html")
    assert (vault.standing[heard["task_id"]]["plan_steps"][0]["tool"]
            == "fetch.listen")
    seen = _plant(client, profile_id,
                  url="https://example.com/schedule.html?video=talk.mp4")
    assert (vault.standing[seen["task_id"]]["plan_steps"][0]["tool"]
            == "fetch.render")


def test_a_page_still_gets_the_eyes(client, profile_id):
    """A page containing a player is a page — the eyes render it; only a
    URL that is itself the media file gets the ears."""
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    out = _plant(client, profile_id, url="https://example.com/live-talks")
    assert (vault.standing[out["task_id"]]["plan_steps"][0]["tool"]
            == "fetch.render")


def test_the_letter_calls_a_recording_what_it_is(client, profile_id,
                                                 monkeypatch):
    """A transcript's change is new words said, not a page edited — the
    letter's watching line says "watched recording", and an ordinary
    page keeps "watched page"."""
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    _plant(client, profile_id, url="https://cdn.example/briefing.mp4")
    now = db.utcnow()
    monkeypatch.setattr(lookout, "_capture", lambda pdi, tid: {
        "text": "Doors hold.", "transcribed": True,
        "changed_at": now, "fetched_at": now})
    lines = letter._watching_lines(
        profile_id, "2000-01-01T00:00:00+00:00", vault,
        "2999-01-01T00:00:00+00:00", live=False)
    assert lines == [f"watched recording https://cdn.example/briefing.mp4"
                     f" changed on {now[:10]}"]

    monkeypatch.setattr(lookout, "_capture", lambda pdi, tid: {
        "text": "A page.", "changed_at": now, "fetched_at": now})
    lines = letter._watching_lines(
        profile_id, "2000-01-01T00:00:00+00:00", vault,
        "2999-01-01T00:00:00+00:00", live=False)
    assert lines[0].startswith("watched page ")
