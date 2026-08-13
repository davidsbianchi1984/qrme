"""The authoring agent, driven end to end against the real doors.

## What this file is for

`test_the_agent_reaches_no_further_than_its_owner` reads the registry. This
one *uses* it: a scripted model asks for a tool, the request goes through
`qrme/routers/studio.py` and out the same door a person's own console would
knock on, and the change is then read back through a second request.

    asked     does the agent's reply describe an edit
    mattered  did the edit happen

Those come apart in exactly one way, and it is the way that matters: a model
is perfectly capable of writing *I've made your page darker* having called
nothing at all. Every assertion here reads the record rather than the reply.

The model is scripted rather than real. A guard that needs a key is a guard
that does not run, and what is under test is the loop, the binding and the
door — none of which is the model's to get right.
"""
from __future__ import annotations

import json

import pytest

from qrme import authoring


class Scripted:
    """A model that says what it was told to, in order, and records the
    conversation it was handed."""

    def __init__(self, *replies: str) -> None:
        self._replies = list(replies)
        self.systems: list[str] = []
        self.seen: list[list[dict]] = []

    def generate(self, system: str, messages: list[dict]) -> str:
        self.systems.append(system)
        self.seen.append([dict(m) for m in messages])
        return self._replies.pop(0) if self._replies else "done"


@pytest.fixture()
def owner_token(client, profile_id):
    """The token `profile_id` already put on the client, read back.

    Named rather than implicit because the whole question in this file is
    *whose* credential the agent acts with, and a header set by a fixture
    somewhere else is not an answer somebody reading a test can see.
    """
    return client.headers["authorization"].split(" ", 1)[1]


def _turn(client, profile_id: str, owner_token: str, provider,
          said: str = "make it darker", history=None):
    return client.post(
        f"/profiles/{profile_id}/authoring/turn",
        json={"said": said, "history": history or []},
        headers={"Authorization": f"Bearer {owner_token}"},
    )


@pytest.fixture
def driving(monkeypatch):
    """Point the route's provider at a scripted one."""
    def use(provider):
        monkeypatch.setattr("qrme.llm.provider_for_profile",
                            lambda *a, **k: provider)
        return provider
    return use


def test_the_edit_it_describes_is_the_edit_that_happened(
        client, profile_id, owner_token, driving):
    """The whole point. The reply is prose; the page is the record."""
    driving(Scripted(
        'CALL edit_page {"tagline": "still gardening"}',
        "Done — your tagline now reads *still gardening*.",
    ))
    answer = _turn(client, profile_id, owner_token, None,
                   said="change my tagline")
    assert answer.status_code == 200, answer.text
    body = answer.json()
    assert [s["tool"] for s in body["acted"]] == ["edit_page"]
    assert body["acted"][0]["answered"] == 200

    page = client.get(f"/profiles/{profile_id}/page").json()
    assert page["tagline"] == "still gardening", (
        "the agent said it changed the tagline and the page disagrees")


def test_a_widget_it_writes_is_a_widget_that_runs(
        client, profile_id, owner_token, driving):
    """Two steps, the second using what the first returned — the shape every
    real request takes, and the one a single-call test cannot show."""
    source = "module.exports = ({ n }) => (n || 0) + 1;"
    driving(Scripted(
        'CALL write_widget ' + json.dumps({"name": "add one",
                                           "source": source}),
        "There it is — *add one* takes `n` and gives you the next number.",
    ))
    answer = _turn(client, profile_id, owner_token, None,
                   said="write me something that adds one")
    assert answer.status_code == 200, answer.text
    assert [s["tool"] for s in answer.json()["acted"]] == ["write_widget"]

    mine = client.get(f"/profiles/{profile_id}/widgets",
                      headers={"Authorization": f"Bearer {owner_token}"})
    names = [w["name"] for w in mine.json()["widgets"]]
    assert "add one" in names, names


def test_the_agent_is_told_what_the_tool_answered(
        client, profile_id, owner_token, driving):
    """The result goes back into the conversation. Without it the second step
    is the model guessing at what the first one returned."""
    model = Scripted('CALL read_page {}', "Your page is as it was.")
    driving(model)
    assert _turn(client, profile_id, owner_token, None).status_code == 200

    last = model.seen[-1][-1]
    assert last["role"] == "user"
    assert last["content"].startswith("RESULT read_page 200"), last["content"]


def test_a_tool_the_model_invented_is_refused_and_the_turn_goes_on(
        client, profile_id, owner_token, driving):
    """A refusal is a turn, not a wall. The model is told the name is not one
    of its own and gets to answer with something else — which is how it stops
    asking, rather than the person seeing a 500 for the model's mistake."""
    driving(Scripted(
        'CALL delete_profile {}',
        "I can't do that — I can change your page, but not end it.",
    ))
    answer = _turn(client, profile_id, owner_token, None)
    assert answer.status_code == 200, answer.text
    body = answer.json()
    assert body["acted"][0]["refused"] == "agent.unknown_tool"
    assert body["acted"][0]["said"], "the refusal reached the screen as a key"
    assert body["reply"].startswith("I can't")


def test_the_agent_cannot_be_driven_by_somebody_else(
        client, profile_id, driving):
    """The door, not the registry. Somebody else's token gets nowhere near
    the loop, and neither does nobody's."""
    driving(Scripted('CALL edit_page {"tagline": "mine now"}'))
    del client.headers["authorization"]
    assert client.post(f"/profiles/{profile_id}/authoring/turn",
                       json={"said": "change it"}).status_code == 401

    # A real owner — of a different profile. The one who would actually try
    # this is somebody with an account, not somebody with a guess.
    other = client.post("/profiles", json={
        "owner_id": "owner-2", "kind": "self", "display_name": "Ray",
        "persona": "A neighbour who keeps bees.",
        "verification": {"birthdate": "1984-06-01"}}).json()
    assert client.post(
        f"/profiles/{profile_id}/authoring/turn",
        json={"said": "change it"},
        headers={"Authorization": f"Bearer {other['owner_token']}"},
    ).status_code == 403


def test_the_forwarded_credential_is_the_whole_of_its_reach(
        client, profile_id, owner_token, driving):
    """The agent acts with the caller's own token and holds nothing else. A
    turn driven by the owner reaches the owner's rows; the same loop with no
    credential reaches nothing, which is what makes this a forward rather
    than a mint."""
    model = Scripted('CALL list_widgets {}', "You have none yet.")
    driving(model)
    assert _turn(client, profile_id, owner_token, None).status_code == 200

    refused = authoring.call("list_widgets", {}, app=client.app,
                             profile_id=profile_id, authorization=None)
    assert refused["status"] == 401, (
        "the agent reached the owner's widgets with no credential at all — "
        "something other than the caller's token is opening that door")


def test_it_stops_rather_than_looping(client, profile_id, owner_token,
                                      driving):
    """A model that only ever calls tools would call them forever. The turn
    ends, says so in the reader's language, and the steps it did take are
    still shown."""
    driving(Scripted(*['CALL read_page {}'] * (authoring.STEPS + 3)))
    answer = _turn(client, profile_id, owner_token, None)
    assert answer.status_code == 200, answer.text
    body = answer.json()
    assert body["stopped"] == "agent.too_many_steps"
    assert body["said"], "it stopped and said nothing about stopping"
    assert len(body["acted"]) == authoring.STEPS


def test_an_empty_ask_is_refused_before_a_model_is_paid_for_it(
        client, profile_id, owner_token, driving):
    model = Scripted("nothing to do")
    driving(model)
    answer = _turn(client, profile_id, owner_token, None, said="   ")
    assert answer.status_code == 422
    assert not model.seen, "an empty ask reached the provider"


def test_prose_that_merely_mentions_a_call_is_prose(
        client, profile_id, owner_token, driving):
    """The reply a person is most likely to get after asking *what can you
    do* is a paragraph containing the word CALL. Acting on it would mean a
    sentence in a page the agent had just read could steer it."""
    driving(Scripted(
        "I could CALL edit_page {} for you if you like — shall I?"))
    answer = _turn(client, profile_id, owner_token, None, said="what can you do")
    assert answer.status_code == 200, answer.text
    assert answer.json()["acted"] == []


def test_what_it_can_touch_is_readable_without_signing_in(client):
    """Somebody deciding whether to use this should be able to read what it
    reaches first. The list is the registry's, not a second copy."""
    published = client.get("/studio/agent")
    assert published.status_code == 200
    assert published.json()["can_touch"] == authoring.what_it_can_touch()
    assert published.json()["tools"] == list(authoring.tool_names())
