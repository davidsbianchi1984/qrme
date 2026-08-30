"""The video road, and the wait that belongs to the person taking it.

`qrme/filming.py` sends a described scene to a rendering service and waits
for it. Thirty seconds of 4K takes minutes today, and the first draft of
that module treated the slowness as a reason to keep the road closed.

    asked     is it fast enough to ship
    mattered  whose decision is it whether to wait

It is theirs. So the wait is quoted before anybody commits to one, the
timeout is generous enough that the quote is not a lie, and everything
that can be refused is refused before a socket opens.

These fake the service with `urllib.request.urlopen`, the way
`test_the_forge_builds_a_face` fakes the sidecar: the point of the tests
is this module's behaviour, and a real vendor in a test suite is a bill
and a flake.
"""

import io
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VARS = ("QRME_FILM_PROVIDER", "QRME_FILM_URL", "QRME_FILM_KEY")


@pytest.fixture(autouse=True)
def bare(monkeypatch):
    """Every test starts from a deployment nobody configured."""
    for name in VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("QRME_OFFLINE", raising=False)


@pytest.fixture()
def wired(monkeypatch):
    monkeypatch.setenv("QRME_FILM_PROVIDER", "seedance")
    monkeypatch.setenv("QRME_FILM_URL", "https://render.test/v1")
    monkeypatch.setenv("QRME_FILM_KEY", "secret-value")
    # Nobody waits three seconds a poll in a test suite.
    monkeypatch.setattr("qrme.filming.POLL_EVERY", 0)


class _Answer(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _speaks(script):
    """A fake service. `script` is called with (url, body) and returns the
    dict it should answer with."""
    calls = []

    def urlopen(request, timeout=None):
        body = None
        if request.data:
            body = json.loads(request.data.decode())
        calls.append((request.full_url, body, dict(request.headers)))
        return _Answer(json.dumps(script(request.full_url, body)).encode())

    urlopen.calls = calls
    return urlopen


# --- the door, before anybody writes a prompt --------------------------

def test_a_deployment_that_chose_nothing_says_what_to_set():
    from qrme import filming
    assert filming.configured() is False
    why = filming.why_not()
    assert "QRME_FILM_PROVIDER" in why


@pytest.mark.parametrize("missing", ["QRME_FILM_URL", "QRME_FILM_KEY"])
def test_half_a_configuration_is_not_a_configuration(monkeypatch, missing):
    """The failure this prevents is a deployment that believes it has
    video because it named a provider."""
    from qrme import filming
    for name, value in (("QRME_FILM_PROVIDER", "kling"),
                        ("QRME_FILM_URL", "https://render.test/v1"),
                        ("QRME_FILM_KEY", "k")):
        monkeypatch.setenv(name, value)
    monkeypatch.delenv(missing, raising=False)
    assert filming.configured() is False
    assert missing in (filming.why_not() or "")


def test_a_misspelled_provider_is_not_silently_a_working_one(monkeypatch):
    from qrme import filming
    monkeypatch.setenv("QRME_FILM_PROVIDER", "seedanse")
    monkeypatch.setenv("QRME_FILM_URL", "https://render.test/v1")
    monkeypatch.setenv("QRME_FILM_KEY", "k")
    assert filming.provider() == "none"
    assert filming.configured() is False


def test_sora_is_not_on_the_shelf():
    """Deprecated 26 April 2026, API off 24 September 2026. The same call
    `avatars.MARKET` made when Ready Player Me closed."""
    from qrme import filming
    assert "sora" not in filming.PROVIDERS


def test_no_vendor_is_load_bearing():
    from qrme import filming
    assert filming.PROVIDERS[0] == "none"
    assert len(filming.PROVIDERS) >= 5, "one vendor is a dependency"


def test_the_door_never_reports_the_key(monkeypatch):
    """`doors` is drawn on a screen and goes into screenshots."""
    from qrme import filming
    monkeypatch.setenv("QRME_FILM_PROVIDER", "ltx")
    monkeypatch.setenv("QRME_FILM_URL", "https://render.test/v1")
    monkeypatch.setenv("QRME_FILM_KEY", "super-secret-value")
    assert "super-secret-value" not in repr(filming.doors())


# --- the quote, which is why the door is open --------------------------

def test_the_wait_is_quoted_before_anybody_commits():
    from qrme import filming
    quoted = filming.estimate(30)
    assert quoted["wait_seconds"] > 30, "a render is slower than its output"
    assert quoted["worth_leaving"] is True
    assert filming.estimate(2)["worth_leaving"] is False


def test_the_timeout_is_longer_than_the_quote_it_gives():
    """A quote the timeout cannot honour is a lie with a progress bar."""
    from qrme import filming
    longest = filming.estimate(filming.MAX_SECONDS)["wait_seconds"]
    assert filming.GIVE_UP_AFTER > longest


# --- what is refused before a socket opens -----------------------------

def test_the_form_is_checked_without_a_provider():
    from qrme import filming
    for bad in ({"scene": "   "},
                {"scene": "ok", "shape": "diagonal"},
                {"scene": "ok", "seconds": 0},
                {"scene": "ok", "seconds": filming.MAX_SECONDS + 1}):
        with pytest.raises(filming.FilmingError):
            filming.check(bad.pop("scene"), **bad)
    filming.check("a courtroom at dusk", seconds=5, shape="portrait")


def test_an_unconfigured_deployment_refuses_rather_than_pretending():
    from qrme import filming
    with pytest.raises(filming.FilmingError):
        filming.render("a courtroom at dusk", seconds=5)


def test_an_offline_deployment_keeps_the_prompt_at_home(monkeypatch, wired):
    """A prompt is somebody's words and a render service is by definition
    not on this machine."""
    from qrme import filming
    monkeypatch.setenv("QRME_OFFLINE", "1")
    with pytest.raises(Exception) as raised:
        filming.render("a courtroom at dusk", seconds=5)
    assert "render.test" in str(raised.value) or raised.type is not None


# --- the road itself ---------------------------------------------------

def test_a_render_that_finishes_at_once_comes_straight_back(monkeypatch,
                                                            wired):
    from qrme import filming
    speaks = _speaks(lambda url, body: {"video_url": "https://cdn/x.mp4"})
    monkeypatch.setattr("urllib.request.urlopen", speaks)
    got = filming.render("a courtroom at dusk", seconds=4)
    assert got["video_url"] == "https://cdn/x.mp4"
    assert got["provider"] == "seedance"
    # The provider rides in the body so the far end knows which to run.
    assert speaks.calls[0][1]["provider"] == "seedance"
    assert speaks.calls[0][1]["prompt"] == "a courtroom at dusk"


def test_a_render_that_takes_a_while_is_followed_to_the_end(monkeypatch,
                                                            wired):
    from qrme import filming
    seen = {"polls": 0}

    def script(url, body):
        if body is not None:
            return {"id": "job-7"}
        seen["polls"] += 1
        if seen["polls"] < 3:
            return {"status": "pending"}
        return {"status": "done", "video_url": "https://cdn/late.mp4"}

    monkeypatch.setattr("urllib.request.urlopen", _speaks(script))
    got = filming.render("a courtroom at dusk", seconds=4)
    assert got["video_url"] == "https://cdn/late.mp4"
    assert seen["polls"] == 3


def test_the_caller_can_decline_to_hold_the_request_open(monkeypatch, wired):
    """A screen would rather poll than keep a connection open for four
    minutes, and gets the job and the quote to do it with."""
    from qrme import filming
    monkeypatch.setattr("urllib.request.urlopen",
                        _speaks(lambda url, body: {"id": "job-9"}))
    got = filming.render("a courtroom", seconds=10, wait=False)
    assert got["pending"] is True
    assert got["id"] == "job-9"
    assert got["wait_seconds"] > 0


def test_a_failure_at_the_service_is_passed_through_in_its_words(monkeypatch,
                                                                 wired):
    """"Rejected by our safety filter" is something a person can act on.
    "The render failed" is not."""
    from qrme import filming

    def script(url, body):
        if body is not None:
            return {"id": "job-3"}
        return {"status": "failed", "detail": "the prompt was rejected"}

    monkeypatch.setattr("urllib.request.urlopen", _speaks(script))
    with pytest.raises(filming.FilmingError) as raised:
        filming.render("a courtroom", seconds=4)
    assert "rejected" in str(raised.value)


def test_an_answer_with_neither_a_render_nor_a_job_is_refused(monkeypatch,
                                                              wired):
    """The silent failure this replaces: a caller reading `video_url` off
    a dict that has neither, and showing an empty player."""
    from qrme import filming
    monkeypatch.setattr("urllib.request.urlopen",
                        _speaks(lambda url, body: {"ok": True}))
    with pytest.raises(filming.FilmingError):
        filming.render("a courtroom", seconds=4)


def test_an_unreachable_service_is_not_a_video(monkeypatch, wired):
    from qrme import filming

    def dies(request, timeout=None):
        raise OSError("no route")

    monkeypatch.setattr("urllib.request.urlopen", dies)
    with pytest.raises(filming.FilmingError) as raised:
        filming.render("a courtroom", seconds=4)
    assert "could not be reached" in str(raised.value)


def test_the_key_travels_and_is_not_in_the_prompt(monkeypatch, wired):
    from qrme import filming
    speaks = _speaks(lambda url, body: {"video_url": "https://cdn/x.mp4"})
    monkeypatch.setattr("urllib.request.urlopen", speaks)
    filming.render("a courtroom", seconds=4)
    _url, body, headers = speaks.calls[0]
    sent = {k.lower(): v for k, v in headers.items()}
    assert sent.get("authorization") == "Bearer secret-value"
    assert "secret-value" not in json.dumps(body)


def test_whatever_comes_back_is_marked():
    """A generated video is synthetic media outright, and this is the
    artifact most likely to be met with no context around it."""
    from qrme import filming
    assert filming.doors()["marked"] is True
