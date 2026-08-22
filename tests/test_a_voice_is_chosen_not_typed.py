"""A voice is chosen, not typed.

Binding a profile's voice was `PUT /profiles/{id}/voice` with an opaque
`voice_id` — "the owner points the profile at a voice made on the
provider's own surface". True to how the provider works, and not something
a person building a profile can do: it asks them to already know a
twenty-character identifier, so the voices actually available to them were
invisible.

    asked     can a profile be pointed at a voice
    mattered  can its owner see which voices there are

`GET /voices` is the list that makes the binding door usable, and the
console shows it as a picker with the typed field kept beside it — the
picker is a convenience over the id, never a replacement for it, because a
voice made a minute ago on the dashboard should still be bindable before
any cache catches up.

## The two rules, and why neither is a filter

**Gender is a hint.** A profile here can be a device, a drawing, an
invention or an idea — `qrme/seed.py` already carries a rule for a brief
that states no gender — so a voice whose labels say nothing keeps an empty
string and stays as bindable as any other. Nothing filters on it.

**Cloned is a label.** The provider marks a voice cloned when somebody
enrolled a real person's. Whether that restricts who may bind it was asked
directly and answered: every voice on this deployment's account is shared,
so the flag is shown for the same reason the AI mark is shown — a person
choosing a real person's voice should be able to see that is what it is —
and it gates nobody.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from qrme import spoken

REPO = Path(__file__).resolve().parents[1]
API_TS = (REPO / "app/src/api.ts").read_text(encoding="utf-8")
VOICE_TSX = (REPO / "app/src/screens/Voice.tsx").read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def _no_cache():
    spoken._library_cache.clear()
    yield
    spoken._library_cache.clear()


# -- the list exists ---------------------------------------------------------

def test_the_door_answers_a_list(client):
    r = client.get("/voices")
    assert r.status_code == 200, r.text
    voices = r.json()["voices"]
    assert voices, "the picker would have nothing to show"
    for v in voices:
        assert set(v) >= {"id", "name", "gender", "note", "cloned"}


def test_it_asks_the_account_rather_than_reciting(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_real")
    asked = {}

    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self):
            return json.dumps({"voices": [
                {"voice_id": "v1", "name": "David Bianchi",
                 "category": "cloned", "labels": {"gender": "male"}}]}).encode()

    def _open(req, timeout=0):
        asked["url"] = req.full_url
        return _Resp()

    monkeypatch.setattr(spoken.urllib.request, "urlopen", _open)
    got = spoken.library()
    assert asked["url"].endswith("/v1/voices")
    assert [v["name"] for v in got] == ["David Bianchi"]
    assert got[0]["cloned"] is True


# -- neither rule is a filter ------------------------------------------------

def test_a_voice_with_no_gender_is_still_a_voice():
    row = spoken._as_voice({"voice_id": "v", "labels": {"gender": "neutral"}})
    assert row["gender"] == ""
    assert row["id"] == "v", "the row was dropped for having no gender"


def test_nothing_filters_the_list_by_gender():
    """A device, a drawing, an idea. The picker sorts and suggests; it does
    not decide who may choose what."""
    picker = VOICE_TSX[VOICE_TSX.index("{library.length > 0 && ("):]
    picker = picker[:picker.index("</select>")]
    for banned in (".filter(", "=== \"male\"", "=== \"female\""):
        assert banned not in picker, (
            f"the picker narrows the list with {banned} — gender is a hint, "
            "not a gate")


def test_a_clone_is_labelled_and_not_gated():
    """Asked and answered: every voice on this account is shared."""
    picker = VOICE_TSX[VOICE_TSX.index("{library.length > 0 && ("):]
    picker = picker[:picker.index("</select>")]
    assert "voice.spoken.isclone" in picker, (
        "a cloned voice is offered without saying it is one")
    assert "disabled" not in picker, (
        "a row in the picker is unselectable — clones are shared here")


# -- and it falls back rather than emptying ----------------------------------

def test_no_key_keeps_a_list_to_choose_from(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    assert spoken.library() == spoken.FALLBACK_VOICES


def test_a_provider_having_an_afternoon_does_not_empty_the_picker(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_real")

    def _boom(req, timeout=0):
        raise OSError("down")

    monkeypatch.setattr(spoken.urllib.request, "urlopen", _boom)
    assert spoken.library() == spoken.FALLBACK_VOICES


def test_offline_never_reaches_the_provider(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_real")
    monkeypatch.setenv("QRME_OFFLINE", "1")

    def _boom(req, timeout=0):
        raise AssertionError("offline mode opened a socket for the picker")

    monkeypatch.setattr(spoken.urllib.request, "urlopen", _boom)
    assert spoken.library() == spoken.FALLBACK_VOICES


def test_the_answer_is_cached(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_real")
    calls = {"n": 0}

    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b'{"voices": [{"voice_id": "v", "name": "One"}]}'

    def _open(req, timeout=0):
        calls["n"] += 1
        return _Resp()

    monkeypatch.setattr(spoken.urllib.request, "urlopen", _open)
    spoken.library(); spoken.library()
    assert calls["n"] == 1


# -- the typed field stays ---------------------------------------------------

def test_the_id_can_still_be_typed():
    """A voice made a minute ago on the dashboard should be bindable before
    any cache catches up. The picker is a convenience over the id, never a
    replacement for it."""
    assert 'placeholder={tr("voice.spoken.id.ph", lang)}' in VOICE_TSX, (
        "the typed id field is gone, so a voice the list has not caught up "
        "with cannot be bound at all")


def test_the_console_has_a_door_for_the_list():
    assert 'req<{ voices:' in API_TS and '"/voices"' in API_TS
