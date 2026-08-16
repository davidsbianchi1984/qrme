"""The Studio: a person's own widgets, and the box they run in.

Every route here is the owner's. Not "the owner's by convention" — the
scope is checked at the door with `require_owner` and again in
:mod:`qrme.widgets`, where a widget id belonging to another profile is *not
found* rather than acted upon. Two checks for one question is deliberate:
the door is what a client meets, and the query is what actually decides,
and a feature whose isolation lives only at the door is one refactor away
from not having any.

The run route is the one that matters. It hands somebody's own code to a
subprocess with no network, one directory, no child processes and finite
time — see `qrme/widgets.py` for how each of those is held, and
`tests/test_the_widget_cannot_leave_its_box.py` for the escape attempts
that prove they are.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import authoring, i18n, llm, offline, widgets
from ..common import (profile_or_404, require_may_publish,
                      require_may_speak, require_owner)

router = APIRouter()


class WidgetWrite(BaseModel):
    name: str = Field(..., max_length=80,
                      description="What this widget is called, to its author.")
    source: str = Field(..., description=(
        "JavaScript. Export a function, or an object with run(): it is "
        "called with the inputs you send and whatever it returns is the "
        "answer."))


class WidgetRun(BaseModel):
    inputs: dict | None = Field(
        None, description="Handed to the widget as its argument.")


def _refuse(exc: widgets.WidgetError) -> HTTPException:
    """A widget's refusals are keys, not sentences — the reader gets theirs
    from the table like every other refusal in this product."""
    return HTTPException(422, i18n.STUDIO_REFUSALS[str(exc)])


@router.get("/studio/limits")
def studio_limits() -> dict:
    """What a widget may spend, and whether the box can be built here at all.

    Served rather than duplicated in the console, so a screen cannot promise
    a limit the runner does not hold. `available` false is the honest state
    on a host without user namespaces: the editor still opens, and the run
    button says why it will not press.
    """
    ready, why = widgets.sandbox_available()
    # `allowances` rather than `limits`: on this wire `limits` already means a
    # list of sentences about what a signature tier permits, and a name that
    # carries two shapes is the one thing a reader cannot check
    # (tests/test_one_name_one_type_on_the_wire.py).
    return {"allowances": widgets.LIMITS, "available": ready,
            "unavailable_because": why or None}


class AgentTurn(BaseModel):
    said: str = Field(..., max_length=8000,
                      description="What you would like changed.")
    history: list[dict] = Field(
        default_factory=list, description=(
            "The conversation so far, as `{role, content}` — the console "
            "keeps it, because the agent does not."))


@router.get("/studio/agent")
def studio_agent() -> dict:
    """What the agent may touch, and whether it can be driven here.

    Published so a person can read the whole list before they let it near
    anything. The sentences are `qrme/authoring.py`'s and every one of them
    resolves to a route a guard checks.
    """
    return {"can_touch": authoring.what_it_can_touch(),
            "tools": list(authoring.tool_names()),
            "available": bool(llm.available())}


@router.post("/profiles/{profile_id}/authoring/turn")
def authoring_turn(profile_id: str, body: AgentTurn, request: Request) -> dict:
    """One turn of the agent that edits somebody's own app.

    The caller's own credential is what the agent then acts with — forwarded,
    not exchanged for something broader — so this door is the whole of its
    authority, and `require_owner` here is the whole of the check.

    The profile's own model choice answers: somebody who brought their own
    key is driving their own key, and the house key is the fallback it always
    was.
    """
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    # The page this agent edits is the profile's public face, so the gate is
    # the publishing one. A departed profile is a memorial — nobody
    # redecorates a memorial — and a profile restricted pending an objection
    # review is not putting new work in front of the person contesting it,
    # whether a person typed the change or a model did.
    require_may_publish(profile)
    provider = llm.provider_for_profile(profile_id,
                                        cloud=request.app.state.cloud)
    try:
        turn = authoring.converse(
            body.said, body.history, app=request.app, profile_id=profile_id,
            authorization=request.headers.get("authorization"),
            provider=provider)
    except authoring.AgentError as exc:
        raise _agent_refusal(exc) from None
    except offline.LeftTheHost:
        # Offline mode is its own answer everywhere else in this product, and
        # dressing it as a quiet model would be the one sentence that reads
        # like the switch is not working.
        raise
    except Exception as exc:                       # noqa: BLE001
        # The provider's own message is written for an operator and would
        # arrive here as a sentence in one language, on a screen that has
        # ten.
        raise _agent_refusal(
            authoring.AgentError("agent.model_silent")) from exc
    # The keys travel as keys with the sentence beside them, so a screen can
    # show the sentence and a client that knows better can show its own.
    for step in turn["acted"]:
        if step.get("refused"):
            step["said"] = i18n.STUDIO_REFUSALS.get(step["refused"],
                                                    step["refused"])
    turn["said"] = (i18n.STUDIO_REFUSALS[turn["stopped"]]
                    if turn["stopped"] else None)
    return turn


class AgentAct(BaseModel):
    tool: str = Field(..., max_length=40,
                      description="The tool the agent proposed.")
    arguments: dict = Field(default_factory=dict, description=(
        "The arguments it proposed, handed back unchanged."))


@router.post("/profiles/{profile_id}/authoring/act")
def authoring_act(profile_id: str, body: AgentAct, request: Request) -> dict:
    """Do the thing the agent asked about. The press, not the sentence.

    Most of the roster runs inside a turn, because most of it is a mistake a
    person can undo — a tagline goes back, a widget keeps its versions, a post
    comes down. The rows marked `confirm` cannot be undone: a sunset, a
    message somebody else has now read, a payout, a grant of authority handed
    to a third party. Those stop mid-turn and come back as a proposal.

        asked     may this person do this
        mattered  did this person mean this

    The token answers the first question and has answered it since the Studio
    shipped. This route is the second one. It takes no prose and asks no
    model — the arguments arrive exactly as the turn showed them, which is
    what makes the sentence on the screen the thing being agreed to rather
    than a summary of it.
    """
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    require_may_publish(profile)
    if not authoring.is_a_tool(body.tool):
        raise _agent_refusal(authoring.AgentError("agent.unknown_tool"))
    # A row that runs inside a turn has no business arriving here: it would
    # mean a client had learned to drive the roster directly, which is a
    # second, unguarded copy of `converse`.
    if not authoring.needs_a_press(body.tool):
        raise _agent_refusal(authoring.AgentError("agent.not_asked"))
    try:
        did = authoring.call(
            body.tool, body.arguments, app=request.app, profile_id=profile_id,
            authorization=request.headers.get("authorization"))
    except authoring.AgentError as exc:
        raise _agent_refusal(exc) from None
    return {"tool": did["tool"], "answered": did["status"],
            "says": authoring.what_it_would_do(body.tool)}


def _agent_refusal(exc: authoring.AgentError) -> HTTPException:
    return HTTPException(422, i18n.STUDIO_REFUSALS[str(exc)])


@router.get("/profiles/{profile_id}/widgets")
def list_widgets(profile_id: str, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return {"widgets": widgets.listing(profile_id)}


@router.post("/profiles/{profile_id}/widgets")
def create_widget(profile_id: str, body: WidgetWrite,
                  request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return widgets.save(profile_id, body.name, body.source)
    except widgets.WidgetError as exc:
        raise _refuse(exc) from None


@router.get("/profiles/{profile_id}/widgets/{widget_id}")
def read_widget(profile_id: str, widget_id: str, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return widgets.read(profile_id, widget_id)
    except widgets.WidgetError as exc:
        raise _refuse(exc) from None


@router.put("/profiles/{profile_id}/widgets/{widget_id}")
def update_widget(profile_id: str, widget_id: str, body: WidgetWrite,
                  request: Request) -> dict:
    """A new version rather than an overwrite: `version` climbs, so somebody
    reading a run's answer can tell which of their own drafts produced it."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return widgets.save(profile_id, body.name, body.source, widget_id)
    except widgets.WidgetError as exc:
        raise _refuse(exc) from None


@router.delete("/profiles/{profile_id}/widgets/{widget_id}")
def delete_widget(profile_id: str, widget_id: str, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return widgets.remove(profile_id, widget_id)
    except widgets.WidgetError as exc:
        raise _refuse(exc) from None


@router.post("/profiles/{profile_id}/widgets/{widget_id}/run")
def run_widget(profile_id: str, widget_id: str, body: WidgetRun,
               request: Request) -> dict:
    """Run it, and answer with what happened either way.

    A widget that throws, times out, is killed by a limit, or cannot run
    because the box is unavailable all come back **200** with a `status` the
    screen renders — none of them is a refusal of the request. The request
    was fine; the code was not, and telling those apart is the difference
    between an editor and a wall.
    """
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    # The narrower gate: a widget's answer goes to its author and nobody
    # else, so a contested profile may still run its own code — but a
    # terminated one does nothing at all, and a memorial does not compute.
    require_may_speak(profile)
    try:
        answer = widgets.run(profile_id, widget_id, body.inputs)
    except widgets.WidgetError as exc:
        raise _refuse(exc) from None
    if answer.get("detail"):
        answer["said"] = i18n.STUDIO_REFUSALS.get(answer["detail"],
                                                  answer["detail"])
    return answer
