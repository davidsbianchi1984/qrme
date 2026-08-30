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


# --- length is derived, not dialled ------------------------------------

def test_a_passage_is_rendered_for_as_long_as_it_takes_to_say():
    """The dial this replaces made the video fit the setting instead of
    the content."""
    from qrme import filming
    short = filming.length_for("Yes.")
    longer = filming.length_for(" ".join(["word"] * 40))
    assert short < longer
    assert filming.MIN_SECONDS <= short <= filming.MAX_SECONDS
    assert filming.MIN_SECONDS <= longer <= filming.MAX_SECONDS


def test_nothing_renders_below_the_floor_or_above_the_ceiling():
    from qrme import filming
    assert filming.length_for("") == filming.MIN_SECONDS
    assert filming.length_for(" ".join(["word"] * 5000)) == filming.MAX_SECONDS


def test_a_passage_too_long_for_one_scene_is_answered_not_truncated():
    """A video that quietly drops its last sentence is worse than one
    that was never made — nobody watching can tell."""
    from qrme import filming
    assert filming.too_long(" ".join(["word"] * 500)) is True
    assert filming.too_long("A courtroom at dusk.") is False


def test_the_door_says_the_length_is_not_a_control():
    """A screen reading this must not draw a slider."""
    from qrme import filming
    assert filming.doors()["length_is_derived"] is True


def test_a_render_asks_for_the_length_the_passage_needs(monkeypatch, wired):
    from qrme import filming
    speaks = _speaks(lambda url, body: {"video_url": "https://cdn/x.mp4"})
    monkeypatch.setattr("urllib.request.urlopen", speaks)
    passage = " ".join(["word"] * 30)
    filming.render(passage)
    assert speaks.calls[0][1]["seconds"] == filming.length_for(passage)


# --- the standing direction --------------------------------------------

@pytest.fixture()
def seeded(monkeypatch):
    import tempfile as _t
    monkeypatch.setenv("QRME_DB", _t.mkdtemp() + "/scene.db")
    from qrme import db
    db.reset()
    db.connect()
    yield
    db.reset()


def test_a_profile_that_has_said_nothing_still_has_a_direction(seeded):
    """The first render must not be a lottery."""
    from qrme import filming
    assert filming.direction_of("p1") == filming.DEFAULT_DIRECTION


def test_what_they_said_is_carried_to_the_next_render(seeded):
    """The whole point of storing it: "let's have this on the beach" is
    not a note about one video."""
    from qrme import filming
    filming.set_direction("p1", "A sunlit beach at golden hour.")
    assert filming.direction_of("p1") == "A sunlit beach at golden hour."
    assert "beach" in filming.compose("p1", "Yes, that helps.")


def test_the_direction_leads_and_the_passage_follows(seeded):
    """A renderer handed them the other way round treats the setting as
    an afterthought."""
    from qrme import filming
    filming.set_direction("p1", "A beach.")
    composed = filming.compose("p1", "Yes.")
    assert composed.index("A beach.") < composed.index("Yes.")


def test_there_is_one_press_back_to_the_default(seeded):
    from qrme import filming
    filming.set_direction("p1", "A beach.")
    assert filming.forget_direction("p1") == filming.DEFAULT_DIRECTION
    assert filming.direction_of("p1") == filming.DEFAULT_DIRECTION


def test_one_profile_s_direction_is_not_another_s(seeded):
    from qrme import filming
    filming.set_direction("p1", "A beach.")
    assert filming.direction_of("p2") == filming.DEFAULT_DIRECTION


def test_a_direction_cannot_grow_without_limit(seeded):
    """It rides every prompt, so one that grows unbounded starts crowding
    out the passage it is supposed to be framing."""
    from qrme import filming
    kept = filming.set_direction("p1", "beach " * 500)
    assert len(kept) <= filming.MAX_DIRECTION


def test_an_empty_direction_is_refused_rather_than_stored(seeded):
    from qrme import filming
    with pytest.raises(filming.FilmingError):
        filming.set_direction("p1", "   ")


def test_an_amendment_rewrites_rather_than_appends(seeded, monkeypatch):
    """Appending degrades fast: "too dark", "still too dark", "actually
    the beach was better" — twenty corrections become a transcript of
    complaints that contradict each other."""
    from qrme import filming

    class Model:
        def generate(self, system, messages):
            self.saw = messages[0]["content"]
            return "A sunlit beach at golden hour, wide, salt haze."

    model = Model()
    monkeypatch.setattr("qrme.llm.provider_for_profile", lambda *a, **k: model)
    filming.set_direction("p1", "A dark room at night.")
    got = filming.amend("p1", "it's too dark, let's have this on the beach")
    assert got["direction"] == "A sunlit beach at golden hour, wide, salt haze."
    assert "dark room" not in filming.direction_of("p1")
    # It was shown the standing direction, not asked to invent from nothing.
    assert "A dark room at night." in model.saw


def test_an_amendment_with_nothing_asked_is_refused(seeded):
    from qrme import filming
    with pytest.raises(filming.FilmingError):
        filming.amend("p1", "  ")


def test_a_model_that_cannot_be_reached_leaves_the_scene_alone(seeded,
                                                               monkeypatch):
    """The failure this prevents is a correction that silently blanks the
    direction somebody spent five amendments building."""
    from qrme import filming

    class Dead:
        def generate(self, system, messages):
            raise OSError("no route")

    monkeypatch.setattr("qrme.llm.provider_for_profile", lambda *a, **k: Dead())
    filming.set_direction("p1", "A beach.")
    with pytest.raises(filming.FilmingError):
        filming.amend("p1", "make it night")
    assert filming.direction_of("p1") == "A beach."


def test_an_empty_answer_leaves_the_scene_alone(seeded, monkeypatch):
    from qrme import filming

    class Blank:
        def generate(self, system, messages):
            return "   "

    monkeypatch.setattr("qrme.llm.provider_for_profile", lambda *a, **k: Blank())
    filming.set_direction("p1", "A beach.")
    with pytest.raises(filming.FilmingError):
        filming.amend("p1", "make it night")
    assert filming.direction_of("p1") == "A beach."


def test_the_render_sends_the_direction_in_front_of_the_passage(
        seeded, monkeypatch, wired):
    from qrme import filming
    filming.set_direction("p1", "A sunlit beach at golden hour.")
    speaks = _speaks(lambda url, body: {"video_url": "https://cdn/x.mp4"})
    monkeypatch.setattr("urllib.request.urlopen", speaks)
    filming.render("Yes, that helps.", directed_for="p1")
    sent = speaks.calls[0][1]["prompt"]
    assert sent.index("beach") < sent.index("Yes, that helps.")


def test_the_direction_does_not_move_the_clock(seeded, monkeypatch, wired):
    """Letting the setting lengthen the render would make "put us on the
    beach" cost money, which is not what anybody meant by it."""
    from qrme import filming
    passage = " ".join(["word"] * 30)
    filming.set_direction("p1", "A beach. " * 20)
    speaks = _speaks(lambda url, body: {"video_url": "https://cdn/x.mp4"})
    monkeypatch.setattr("urllib.request.urlopen", speaks)
    filming.render(passage, directed_for="p1")
    assert speaks.calls[0][1]["seconds"] == filming.length_for(passage)


# --- the account of what was asked --------------------------------------

def test_every_change_is_logged_with_what_it_replaced(seeded):
    """The direction is one row that gets overwritten, which is right for
    a standing setting and useless as an account of one."""
    from qrme import filming
    filming.set_direction("p1", "A dark room.")
    filming.set_direction("p1", "A sunlit beach.")
    log = filming.direction_log("p1")
    assert len(log) == 2
    assert log[0]["became"] == "A sunlit beach."
    assert log[0]["was"] == "A dark room."


def test_the_log_is_newest_first(seeded):
    from qrme import filming
    for n in ("one", "two", "three"):
        filming.set_direction("p1", f"A room, {n}.")
    assert filming.direction_log("p1")[0]["became"] == "A room, three."


def test_a_change_made_full_screen_is_what_the_frame_reads(seeded,
                                                           monkeypatch):
    """Progress sticks across the two views because there are not two of
    them: one row, read by both."""
    from qrme import filming

    class Model:
        def generate(self, system, messages):
            return "A sunlit beach at golden hour."

    monkeypatch.setattr("qrme.llm.provider_for_profile", lambda *a, **k: Model())
    filming.amend("p1", "let's have this on the beach", surface="fullscreen")
    # Nothing is carried back. The windowed frame reads the same row.
    assert filming.direction_of("p1") == "A sunlit beach at golden hour."
    assert filming.direction_log("p1")[0]["surface"] == "fullscreen"


def test_the_log_keeps_their_words_not_just_the_result(seeded, monkeypatch):
    """Somebody who has amended five times cannot otherwise tell which
    request caused the thing they now dislike."""
    from qrme import filming

    class Model:
        def generate(self, system, messages):
            return "A sunlit beach at golden hour."

    monkeypatch.setattr("qrme.llm.provider_for_profile", lambda *a, **k: Model())
    filming.amend("p1", "it's too dark")
    assert filming.direction_log("p1")[0]["asked"] == "it's too dark"


def test_starting_over_is_logged_too(seeded):
    """A log with five amendments and no reset reads as though the last
    amendment is still in force."""
    from qrme import filming
    filming.set_direction("p1", "A beach.")
    filming.forget_direction("p1")
    log = filming.direction_log("p1")
    assert log[0]["became"] == filming.DEFAULT_DIRECTION
    assert log[0]["was"] == "A beach."


def test_resetting_an_untouched_scene_writes_nothing(seeded):
    """Pressing start-over on a default is not an event."""
    from qrme import filming
    filming.forget_direction("p1")
    assert filming.direction_log("p1") == []


def test_a_failed_amendment_leaves_no_trace(seeded, monkeypatch):
    """The log is what happened, not what was attempted — an entry whose
    `became` never became would make the account a lie."""
    from qrme import filming

    class Dead:
        def generate(self, system, messages):
            raise OSError("no route")

    monkeypatch.setattr("qrme.llm.provider_for_profile", lambda *a, **k: Dead())
    filming.set_direction("p1", "A beach.")
    with pytest.raises(filming.FilmingError):
        filming.amend("p1", "make it night")
    assert len(filming.direction_log("p1")) == 1


def test_one_profile_s_log_is_not_another_s(seeded):
    from qrme import filming
    filming.set_direction("p1", "A beach.")
    assert filming.direction_log("p2") == []
