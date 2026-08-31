"""The service that renders a profile is a choice somebody can make.

    asked     which video generation company will be used
    mattered  does pressing the name change what gets sent

The picker on the Identity screen drew all seven providers, lit the one
the deployment's environment named, and handed every click to
``onPick={() => undefined}``. Nothing was stored and nothing was sent, so
choosing Seedance and choosing nothing were the same act with different
pixels. Field report: "Video is selected but seadance is not rendering
video."

The endpoint and the credential stay deployment-wide on purpose. This
module speaks one submit-and-poll protocol and the model name rides in
the body, so an owner picking a company spends no new secret and reaches
nothing the operator has not already pointed at.
"""

from __future__ import annotations

import pytest

from qrme import db, filming


@pytest.fixture()
def profile_id(tmp_path, monkeypatch):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "pick.db"))
    db.reset()
    db.connect()
    yield "prof_video_pick"
    db.reset()


def test_a_profile_with_no_choice_renders_on_the_deployments(profile_id,
                                                             monkeypatch):
    monkeypatch.setenv("QRME_FILM_PROVIDER", "veo")
    got = filming.road_of(profile_id)
    assert got["provider"] == "veo"
    assert got["provider_set"] is False


def test_the_choice_is_stored_and_reported(profile_id, monkeypatch):
    monkeypatch.setenv("QRME_FILM_PROVIDER", "veo")
    filming.set_road(profile_id, "video", 120, film_provider="seedance")
    got = filming.road_of(profile_id)
    assert got["provider"] == "seedance"
    assert got["provider_set"] is True
    # And it outlives the deployment changing its own mind.
    monkeypatch.setenv("QRME_FILM_PROVIDER", "kling")
    assert filming.road_of(profile_id)["provider"] == "seedance"


def test_the_road_alone_leaves_the_company_alone(profile_id, monkeypatch):
    """Sending the road says nothing about the service.

    The two live in one row and one route, so a screen that only meant to
    change the road would otherwise clear a choice nobody touched.
    """
    monkeypatch.setenv("QRME_FILM_PROVIDER", "veo")
    filming.set_road(profile_id, "video", 120, film_provider="seedance")
    filming.set_road(profile_id, "photo")
    got = filming.road_of(profile_id)
    assert got["road"] == "photo"
    assert got["provider"] == "seedance"


def test_none_hands_the_choice_back(profile_id, monkeypatch):
    monkeypatch.setenv("QRME_FILM_PROVIDER", "veo")
    filming.set_road(profile_id, "video", 120, film_provider="seedance")
    filming.set_road(profile_id, "video", 120, film_provider="none")
    got = filming.road_of(profile_id)
    assert got["provider"] == "veo"
    assert got["provider_set"] is False


def test_a_company_this_platform_does_not_speak_is_refused(profile_id):
    with pytest.raises(filming.FilmingError):
        filming.set_road(profile_id, "video", 120, film_provider="sora")


def test_sora_is_not_on_the_shelf():
    """Deprecated 26 April 2026, API down 24 September 2026. A shelf that
    sends somebody to a service with a published end date is worse than a
    shelf one row shorter."""
    assert "sora" not in filming.PROVIDERS


def test_the_chosen_company_is_what_gets_sent(profile_id, monkeypatch):
    """The body carries the profile's company, not the box's.

    This is the assertion the defect would have failed: `render` read
    `provider()` — the environment — in five places, so an owner's choice
    could be stored and still never leave the building.
    """
    monkeypatch.setenv("QRME_FILM_PROVIDER", "veo")
    monkeypatch.setenv("QRME_FILM_URL", "https://film.example")
    monkeypatch.setenv("QRME_FILM_KEY", "k")
    filming.set_road(profile_id, "video", 600, film_provider="seedance")

    sent = {}

    def fake_ask(url, body=None, *, on_behalf_of=None):
        if body:
            sent.update(body)
        return {"video_url": "https://film.example/out.mp4"}

    monkeypatch.setattr(filming, "_ask", fake_ask)
    out = filming.render("a quiet room", seconds=5, directed_for=profile_id)
    assert sent["provider"] == "seedance"
    assert out["provider"] == "seedance"
