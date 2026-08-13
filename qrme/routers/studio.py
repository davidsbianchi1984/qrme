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

from .. import i18n, widgets
from ..common import profile_or_404, require_owner

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
    return {"limits": widgets.LIMITS, "available": ready,
            "unavailable_because": why or None}


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
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        answer = widgets.run(profile_id, widget_id, body.inputs)
    except widgets.WidgetError as exc:
        raise _refuse(exc) from None
    if answer.get("detail"):
        answer["said"] = i18n.STUDIO_REFUSALS.get(answer["detail"],
                                                  answer["detail"])
    return answer
