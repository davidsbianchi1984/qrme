"""The adapter that was named in a docstring and never built.

    asked     video is selected but seedance is not rendering video
    mattered  QRME_FILM_URL had nothing on the box to point at

`filming.py` speaks one submit-and-poll shape and says plainly that it
is "one adapter away from any vendor whose own API differs". The adapter
was the missing half: `docker/ears` and `docker/forge` each ship one,
and the video road never got hers, so every render went nowhere however
the picker was set.

These exercise `docker/film/server.py` directly with the network stubbed
— the translation is the whole of what it does, and the translation is
what breaks when a vendor renames a field.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest
from fastapi import HTTPException

FILM = pathlib.Path(__file__).resolve().parent.parent / "docker" / "film" \
    / "server.py"


@pytest.fixture()
def film(monkeypatch):
    spec = importlib.util.spec_from_file_location("film_server", FILM)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("FAL_KEY", "test-key")
    module._JOBS.clear()
    return module


def test_every_provider_the_product_offers_has_a_model(film):
    """The shelf and the adapter cannot disagree.

    A name in `filming.PROVIDERS` with no row here is a tile somebody can
    press that refuses — which is the defect this whole round is about,
    one layer down.
    """
    from qrme import filming
    for name in filming.PROVIDERS:
        if name == "none":
            continue
        assert name in film.MODELS, f"{name} is offered and cannot be sent"


def test_a_model_id_can_be_corrected_without_a_rebuild(film, monkeypatch):
    """Hosted model ids are somebody else's strings and they rename them."""
    assert film.model_for("veo") == film.MODELS["veo"]
    monkeypatch.setenv("FILM_MODEL_VEO", "fal-ai/veo9")
    assert film.model_for("veo") == "fal-ai/veo9"


def test_a_provider_with_no_model_says_what_to_set(film):
    with pytest.raises(HTTPException) as raised:
        film.model_for("bolex")
    assert "FILM_MODEL_BOLEX" in raised.value.detail


def test_no_credential_refuses_in_words(film, monkeypatch):
    monkeypatch.delenv("FAL_KEY", raising=False)
    with pytest.raises(HTTPException) as raised:
        film.key()
    assert raised.value.status_code == 503
    assert "FAL_KEY" in raised.value.detail


def test_health_never_hands_back_the_key(film):
    got = film.health()
    assert got["keyed"] is True
    assert "test-key" not in repr(got)


def test_a_started_render_answers_a_job_to_follow(film, monkeypatch):
    sent = {}

    def fake(url, body=None):
        sent["url"], sent["body"] = url, body
        return {"request_id": "req-1"}

    monkeypatch.setattr(film, "_call", fake)
    got = film.submit(film.Scene(provider="seedance", prompt="a quiet room",
                                 seconds=6, shape="portrait"))
    assert got == {"id": "req-1"}
    assert film.MODELS["seedance"] in sent["url"]
    assert sent["body"]["duration"] == 6
    assert sent["body"]["aspect_ratio"] == "9:16"


def test_a_render_that_finishes_at_once_skips_the_polling(film, monkeypatch):
    monkeypatch.setattr(film, "_call",
                        lambda url, body=None: {"video": {"url": "u.mp4"}})
    assert film.submit(film.Scene(prompt="x")) == {"video_url": "u.mp4"}


@pytest.mark.parametrize("payload,expected", [
    ({"video": {"url": "a.mp4"}}, "a.mp4"),
    ({"video": "b.mp4"}, "b.mp4"),
    ({"video_url": "c.mp4"}, "c.mp4"),
    ({"videos": [{"url": "d.mp4"}]}, "d.mp4"),
    ({"videos": ["e.mp4"]}, "e.mp4"),
    ({"nothing": 1}, None),
])
def test_the_finished_file_is_found_wherever_the_model_put_it(
        film, payload, expected):
    """Vendors disagree about this between models on ONE host."""
    assert film._video_in(payload) == expected


def test_an_answer_with_no_render_and_no_job_is_refused(film, monkeypatch):
    monkeypatch.setattr(film, "_call", lambda url, body=None: {"ok": True})
    with pytest.raises(HTTPException) as raised:
        film.submit(film.Scene(prompt="x"))
    assert raised.value.status_code == 502


def test_a_pending_render_reads_as_pending(film, monkeypatch):
    film._JOBS["j"] = ("fal-ai/veo3", film.time.time())
    monkeypatch.setattr(film, "_call",
                        lambda url, body=None: {"status": "IN_PROGRESS"})
    assert film.follow("j") == {"status": "pending"}


def test_a_finished_render_hands_back_the_file(film, monkeypatch):
    film._JOBS["j"] = ("fal-ai/veo3", film.time.time())

    def fake(url, body=None):
        return ({"status": "COMPLETED"} if url.endswith("/status")
                else {"video": {"url": "done.mp4"}})

    monkeypatch.setattr(film, "_call", fake)
    assert film.follow("j") == {"status": "done", "video_url": "done.mp4"}
    assert "j" not in film._JOBS


def test_a_job_this_process_lost_is_failed_rather_than_missing(film):
    """A restart loses the pairing, and `filming.follow` reads a status.

    404 would have the product treat a dead render as a transport fault
    and keep asking; `failed` ends it and says why in one sentence.
    """
    got = film.follow("gone")
    assert got["status"] == "failed"
    assert "restart" in got["detail"]


def test_the_shapes_the_product_offers_all_resolve(film):
    from qrme import filming
    for shape in filming.SHAPES:
        assert shape in film.RATIOS
