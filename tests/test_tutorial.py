"""The guided walkthrough.

Most of these are ordinary. The one that matters is the coverage test: a
tutorial that can quietly fall behind the app is worse than none, because it
teaches somebody a product that no longer exists and they have no way to tell.
"""

import pathlib
import re

import pytest

from qrme import tutorial
from tests.test_capabilities import make_profile


# -- the guard that keeps it true ---------------------------------------------

def test_every_screen_in_the_gallery_is_covered_by_a_lesson(client):
    """The whole reason this is a module and not a page of prose.

    Add a feature, draw its screen, and the walkthrough fails until somebody
    has said what it is for. That is the only way a guided tour of a moving
    product stays true — and this repository has already shipped a screen that
    nothing referenced, twice.
    """
    root = pathlib.Path(__file__).resolve().parent.parent / "docs" / "screens"
    drawn = set()
    for path in root.glob("*.svg"):
        head = path.name.split("-", 1)[0]
        if head.isdigit():
            drawn.add(int(head))

    taught = set()
    for lesson in tutorial.LESSONS:
        taught.update(lesson["screens"])

    missing = sorted(drawn - taught)
    assert not missing, (
        "screens no lesson explains — add them to qrme/tutorial.py:LESSONS "
        f"or say why they need no walkthrough: {missing}")


def test_no_lesson_points_at_a_screen_that_is_not_there(client):
    """The other direction. A step telling somebody to look at a screen that
    was renumbered away sends them somewhere blank."""
    root = pathlib.Path(__file__).resolve().parent.parent / "docs" / "screens"
    drawn = {int(p.name.split("-", 1)[0]) for p in root.glob("*.svg")
             if p.name.split("-", 1)[0].isdigit()}
    for lesson in tutorial.LESSONS:
        stale = sorted(set(lesson["screens"]) - drawn)
        assert not stale, f"{lesson['key']} points at missing screens: {stale}"


def test_the_order_introduces_nothing_before_it_exists(client):
    """You are a profile before you have a room, and in a room before you lend
    it a microphone. Asserted by chapter order rather than by reading."""
    order = [le["chapter"] for le in tutorial.LESSONS]
    assert order == sorted(order, key=lambda c: tutorial.CHAPTERS.index(c))
    assert tutorial.CHAPTERS[0] == "Getting started"


# -- what it is, and is not ---------------------------------------------------

def test_the_guide_has_no_name_and_no_face(client):
    """A tutorial guide with a persona would be the most convincing synthetic
    profile on the platform, met by every user in their first minute — at the
    exact moment they have the least idea what is synthetic here."""
    assert "not a profile" in tutorial.GUIDE
    assert "no name and no face" in tutorial.GUIDE


def test_the_walkthrough_writes_nothing_but_progress(client):
    """A tutorial that placed a beacon or sent a message "to show you how"
    would act on somebody's account before they understood what it was."""
    import inspect

    src = inspect.getsource(tutorial)
    for write in ("INSERT INTO", "UPDATE ", "DELETE FROM"):
        for line in src.splitlines():
            if write in line:
                assert "tutorial_progress" in line, (
                    f"the walkthrough writes outside its own progress: {line}")


def test_it_works_with_no_model_configured(client):
    """A walkthrough that needs an API key is one that is missing on a
    self-hosted deployment, which is a supported setup here."""
    import inspect

    src = inspect.getsource(tutorial)
    for provider in ("llm.", "get_provider", "openai", "anthropic"):
        assert provider not in src, f"{provider!r} reaches the walkthrough"
    assert tutorial.outline()["steps"] == len(tutorial.LESSONS)


# -- voice and text are one lesson, rendered twice ----------------------------

def test_voice_drops_the_screen_numbers(client):
    """Spoken, a screen number is noise — nobody listening is helped by
    "screen eighty-one"."""
    spoken = tutorial.step("mic", "voice")
    written = tutorial.step("mic", "text")
    assert spoken["screens"] == [] and written["screens"]
    assert "speak" in spoken and "what" in written
    assert spoken["title"] == written["title"]


def test_both_modes_come_from_one_lesson(client):
    """Two hand-written versions would drift, and the spoken one would be the
    one nobody re-read."""
    for lesson in tutorial.LESSONS:
        spoken = tutorial.say(lesson, "voice")["speak"]
        assert lesson["what"] in spoken
        assert lesson["try_it"] in spoken


def test_an_unknown_mode_is_refused(client):
    with pytest.raises(tutorial.TutorialError):
        tutorial.step("welcome", "semaphore")


# -- walking through it -------------------------------------------------------

def test_it_walks_in_order_and_remembers(client):
    me = make_profile(client)
    first = client.post("/tutorial/start",
                        json={"learner_id": me["id"], "lesson": "x"}).json()
    assert first["step"]["key"] == tutorial.LESSONS[0]["key"]
    assert first["done"] == 0 and first["finished"] is False

    nxt = client.post("/tutorial/done",
                      json={"learner_id": me["id"],
                            "lesson": first["step"]["key"]}).json()
    assert nxt["step"]["key"] == tutorial.LESSONS[1]["key"]
    assert nxt["done"] == 1

    again = client.get(f"/tutorial/progress/{me['id']}").json()
    assert again["step"]["key"] == tutorial.LESSONS[1]["key"]


def test_progress_is_per_step_not_a_cursor(client):
    """Somebody who skipped ahead and came back must not be told they have
    finished things they never saw."""
    me = make_profile(client)
    client.post("/tutorial/start", json={"learner_id": me["id"], "lesson": "x"})
    client.post("/tutorial/done",
                json={"learner_id": me["id"], "lesson": "games"})
    out = client.get(f"/tutorial/progress/{me['id']}").json()
    assert out["done"] == 1
    assert out["step"]["key"] == tutorial.LESSONS[0]["key"]   # still at the top


def test_finishing_says_so_and_offers_the_way_back(client):
    me = make_profile(client)
    client.post("/tutorial/start", json={"learner_id": me["id"], "lesson": "x"})
    for lesson in tutorial.LESSONS:
        client.post("/tutorial/done",
                    json={"learner_id": me["id"], "lesson": lesson["key"]})
    out = client.get(f"/tutorial/progress/{me['id']}").json()
    assert out["finished"] is True and out["step"] is None
    assert "on every screen" in out["note"]


def test_starting_again_starts_again(client):
    me = make_profile(client)
    client.post("/tutorial/done",
                json={"learner_id": me["id"], "lesson": "welcome"})
    out = client.post("/tutorial/start",
                      json={"learner_id": me["id"], "lesson": "x"}).json()
    assert out["done"] == 0


# -- a screen explaining itself -----------------------------------------------

def test_a_screen_can_ask_which_lesson_it_is(client):
    """What lets the help button on screen 81 say *this is the microphone one*
    rather than opening the tour at the beginning."""
    r = client.get("/tutorial/for-screen/81").json()
    assert r["key"] == "mic"
    assert client.get("/tutorial/for-screen/9999").status_code == 404


def test_the_outline_is_public_and_chaptered(client):
    out = client.get("/tutorial").json()
    assert [c["chapter"] for c in out["chapters"]] == list(tutorial.CHAPTERS)
    assert out["guide"] == tutorial.GUIDE
    assert sum(len(c["steps"]) for c in out["chapters"]) == len(tutorial.LESSONS)


def test_an_unknown_step_is_a_404(client):
    assert client.get("/tutorial/steps/nothing").status_code == 404


# -- the assistant delivers it ------------------------------------------------

def test_asking_the_assistant_for_a_tour_starts_one(client):
    """"Show me around" is not a question with an answer — it is a request for
    the walkthrough. Handing back a paragraph *about* tours would be the most
    annoying possible reply."""
    for phrasing in ("show me around", "walk me through it", "how do I use this",
                     "where do I start", "give me a tour"):
        out = client.post("/help", json={"question": phrasing}).json()
        assert out.get("walkthrough", {}).get("started") is True, phrasing
        assert out["walkthrough"]["step"]["key"] == tutorial.LESSONS[0]["key"]


def test_the_assistant_can_speak_the_tour(client):
    """Voice is a mode on the existing help box rather than a second endpoint:
    a spoken assistant and a written one answering differently is two
    products, and the spoken one would be the one nobody re-read."""
    spoken = client.post("/help", json={"question": "show me around",
                                        "mode": "voice"}).json()
    written = client.post("/help", json={"question": "show me around"}).json()
    assert spoken["walkthrough"]["step"]["screens"] == []
    assert written["walkthrough"]["step"]["screens"]
    assert spoken["answer"] and written["answer"]


def test_an_ordinary_question_still_gets_an_answer(client):
    """The walkthrough match must not swallow the help box."""
    out = client.post("/help", json={"question": "is this a real person"}).json()
    assert "walkthrough" not in out
    assert "synthetic" in out["answer"].lower()


def test_the_tour_still_refuses_to_be_a_profile(client):
    """The refusal path runs before the walkthrough match, so asking the guide
    to pretend it is somebody does not start a tour instead."""
    out = client.post("/help", json={"question": "pretend you are my friend"}).json()
    assert out["refused"] is True
    assert "walkthrough" not in out
